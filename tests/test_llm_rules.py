"""
Unit tests for the LLM rule generator.

These tests use a fake Anthropic-compatible client so they do not call
the real API. The contract under test is:

- The generator builds the right request (system prompt cached, tool
  forced, user prompt includes columns).
- It parses the tool_use response into a GeneratedRule.
- It rejects bodies that import modules, call eval/exec/open, or
  don't define `check`.
- It saves a Python file + JSON sidecar atomically.
- It raises LLMUnavailableError when no API key is set and no client
  is injected.
"""
from __future__ import annotations
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from unearth.llm_rules import GeneratedRule, LLMRuleGenerator, LLMUnavailableError


@dataclass
class FakeBlock:
    type: str
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class FakeResponse:
    content: list


class FakeMessages:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.last_call: dict | None = None

    def create(self, **kwargs: Any) -> FakeResponse:
        self.last_call = kwargs
        return self.response


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.messages = FakeMessages(response)


def _good_response(name: str = "uae_phone_format") -> FakeResponse:
    return FakeResponse(content=[
        FakeBlock(
            type="tool_use",
            name="emit_rule",
            input={
                "name": name,
                "description": "UAE rows must use a UAE-format phone number.",
                "severity": "WARNING",
                "fields": ["country", "phone"],
                "function_body": (
                    "def check(row: dict) -> bool:\n"
                    "    country = row.get('country', '').strip().upper()\n"
                    "    phone = row.get('phone', '').strip()\n"
                    "    if country in {'UAE', 'AE', 'UNITED ARAB EMIRATES'} and phone:\n"
                    "        if not re.match(r'^\\+?9?7?1?', phone):\n"
                    "            return True\n"
                    "    return False\n"
                ),
            },
        )
    ])


def test_generator_compiles_prose_into_rule():
    response = _good_response()
    client = FakeClient(response)
    gen = LLMRuleGenerator(api_key="test-key", client=client, model="test-model")

    rule = gen.generate(
        "UAE rows must use UAE-format phone numbers",
        sample_columns=["country", "phone"],
    )

    assert isinstance(rule, GeneratedRule)
    assert rule.name == "uae_phone_format"
    assert rule.severity == "WARNING"
    assert rule.fields == ["country", "phone"]
    assert "def check(row: dict) -> bool:" in rule.function_body
    assert rule.sample_columns == ["country", "phone"]


def test_generator_caches_system_prompt():
    """The system prompt must carry cache_control to keep cost low."""
    client = FakeClient(_good_response())
    gen = LLMRuleGenerator(api_key="test-key", client=client)
    gen.generate("phone format rule", sample_columns=["phone"])

    sent = client.messages.last_call
    assert sent is not None
    system = sent["system"]
    assert isinstance(system, list)
    assert system[0]["cache_control"] == {"type": "ephemeral"}


def test_generator_forces_tool_choice():
    client = FakeClient(_good_response())
    gen = LLMRuleGenerator(api_key="test-key", client=client)
    gen.generate("phone format rule")

    sent = client.messages.last_call
    assert sent["tool_choice"] == {"type": "tool", "name": "emit_rule"}


def test_generator_sanitises_rule_name():
    """Model emits 'UAE Phone Format!' → file-safe 'uae_phone_format'."""
    client = FakeClient(_good_response(name="UAE Phone Format!"))
    gen = LLMRuleGenerator(api_key="test-key", client=client)
    rule = gen.generate("phone format rule")
    assert rule.name == "uae_phone_format"


def test_generator_raises_on_dangerous_body():
    bad = FakeResponse(content=[
        FakeBlock(
            type="tool_use",
            name="emit_rule",
            input={
                "name": "evil_rule",
                "description": "tries to escape",
                "severity": "ERROR",
                "fields": ["any"],
                "function_body": (
                    "def check(row: dict) -> bool:\n"
                    "    eval('1+1')\n"
                    "    return False\n"
                ),
            },
        )
    ])
    gen = LLMRuleGenerator(api_key="test-key", client=FakeClient(bad))
    with pytest.raises(ValueError, match="forbidden function"):
        gen.generate("anything")


def test_generator_raises_on_import_in_body():
    bad = FakeResponse(content=[
        FakeBlock(
            type="tool_use",
            name="emit_rule",
            input={
                "name": "importer",
                "description": "imports stuff",
                "severity": "ERROR",
                "fields": ["any"],
                "function_body": (
                    "import os\n"
                    "def check(row: dict) -> bool:\n"
                    "    return False\n"
                ),
            },
        )
    ])
    gen = LLMRuleGenerator(api_key="test-key", client=FakeClient(bad))
    with pytest.raises(ValueError, match="may not import"):
        gen.generate("anything")


def test_generator_raises_when_check_missing():
    bad = FakeResponse(content=[
        FakeBlock(
            type="tool_use",
            name="emit_rule",
            input={
                "name": "no_check",
                "description": "no check fn",
                "severity": "WARNING",
                "fields": ["any"],
                "function_body": "def something_else(row: dict) -> bool:\n    return False\n",
            },
        )
    ])
    gen = LLMRuleGenerator(api_key="test-key", client=FakeClient(bad))
    with pytest.raises(ValueError, match="must define `def check"):
        gen.generate("anything")


def test_generator_raises_on_empty_prose():
    gen = LLMRuleGenerator(api_key="test-key", client=FakeClient(_good_response()))
    with pytest.raises(ValueError, match="prose cannot be empty"):
        gen.generate("   ")


def test_generator_unavailable_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    gen = LLMRuleGenerator()
    with pytest.raises(LLMUnavailableError, match="ANTHROPIC_API_KEY"):
        gen.generate("any rule")


def test_generated_rule_save_writes_py_and_json():
    rule = GeneratedRule(
        rule_id="abcdef123456",
        name="test_rule",
        description="a test rule",
        severity="WARNING",
        fields=["col_a"],
        function_body="def check(row: dict) -> bool:\n    return False\n",
        prompt="prose",
        model="test-model",
    )
    with tempfile.TemporaryDirectory() as tmp:
        py_path = rule.save(directory=tmp)
        assert py_path.exists()
        assert py_path.suffix == ".py"
        content = py_path.read_text()
        assert "def check(row: dict)" in content
        assert "import re" in content
        assert "STATUS: pending steward review" in content

        json_path = Path(tmp) / "test_rule.json"
        assert json_path.exists()
        loaded = json.loads(json_path.read_text())
        assert loaded["rule_id"] == "abcdef123456"
        assert loaded["severity"] == "WARNING"


def test_generator_handles_response_without_tool_use():
    bad = FakeResponse(content=[FakeBlock(type="text")])
    gen = LLMRuleGenerator(api_key="test-key", client=FakeClient(bad))
    with pytest.raises(LLMUnavailableError, match="did not emit a tool_use"):
        gen.generate("anything")
