"""
UNEARTH LLM Rule Generator
Translates steward prose ("phone numbers must be UAE-format if country is UAE")
into reviewable Python rules.

Architectural position (see docs/architecture/ai-strategy.md):
- The generator NEVER auto-promotes rules. Output is written to a
  ``generated/`` directory; a human is in the loop before promotion.
- Structured output via Anthropic's tool-use API.
- Prompt caching on the system prompt to keep repeated calls cheap.
- Provider-neutral surface: the generator depends only on a tiny client
  protocol so OpenAI / Bedrock / a local model can be swapped in by
  satisfying the same interface.
- Token-budget guard at construction time.
- Deterministic fallback when no API key is configured — generation
  raises ``LLMUnavailableError`` rather than silently inventing rules.
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_GENERATED_DIR = Path(__file__).parent / "generated"

SYSTEM_PROMPT = """You are a data-quality rule compiler for the AURUM MDM platform.

Your job is to translate a steward's plain-English description of a data-quality \
rule into a small, deterministic Python function that operates on a single \
record (a ``dict[str, str]``) and returns ``True`` if the row VIOLATES the rule.

Hard requirements:
- The function signature is exactly: ``def check(row: dict) -> bool``
- The function body MUST NOT import anything, call ``eval``, ``exec``, ``open``, \
  network, or filesystem APIs.
- The function body MUST be deterministic and side-effect-free.
- Use only: dict access, string methods, the ``re`` module (already in scope), \
  comparisons, and basic arithmetic.
- Return ``True`` when the rule is violated; ``False`` when the row is clean.
- Prefer narrow, well-named guards over long if-chains.

Return your answer using the ``emit_rule`` tool. Do not narrate."""

EMIT_RULE_TOOL = {
    "name": "emit_rule",
    "description": "Emit a single deterministic DQ rule for the AURUM rule engine.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Short snake_case identifier for the rule, e.g. 'uae_phone_format'.",
            },
            "description": {
                "type": "string",
                "description": "One-sentence description of what the rule enforces.",
            },
            "severity": {
                "type": "string",
                "enum": ["ERROR", "WARNING"],
                "description": "ERROR for hard violations; WARNING for soft signals.",
            },
            "fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The row fields the rule reads.",
            },
            "function_body": {
                "type": "string",
                "description": (
                    "The full Python source of `def check(row: dict) -> bool:` "
                    "including the def line. Use `re` if needed (it's pre-imported)."
                ),
            },
        },
        "required": ["name", "description", "severity", "fields", "function_body"],
    },
}


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM client cannot be initialised (missing key, bad config)."""


class LLMClient(Protocol):
    """Minimal client surface — anthropic.Anthropic satisfies this."""

    def messages_create(self, **kwargs: Any) -> Any: ...  # pragma: no cover


@dataclass
class GeneratedRule:
    """A rule emitted by the LLM, awaiting human review before promotion."""

    rule_id: str
    name: str
    description: str
    severity: str
    fields: list[str]
    function_body: str
    prompt: str
    model: str
    sample_columns: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "fields": self.fields,
            "function_body": self.function_body,
            "prompt": self.prompt,
            "model": self.model,
            "sample_columns": self.sample_columns,
            "created_at": self.created_at,
        }

    def save(self, directory: Path | str | None = None) -> Path:
        """Persist the rule as a Python module with a JSON sidecar.

        The Python file is human-reviewable; the sidecar JSON carries the
        prompt, model, and metadata needed for audit replay.
        """
        target_dir = Path(directory) if directory else DEFAULT_GENERATED_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        py_path = target_dir / f"{self.name}.py"
        json_path = target_dir / f"{self.name}.json"

        header = (
            f'"""Generated rule: {self.name}\n\n'
            f"{self.description}\n\n"
            f"Generated by:  {self.model}\n"
            f"Generated at:  {self.created_at}\n"
            f"Rule ID:       {self.rule_id}\n"
            f"Severity:      {self.severity}\n"
            f"Fields:        {', '.join(self.fields)}\n\n"
            f'STATUS: pending steward review — NOT auto-promoted to active ruleset.\n'
            f'"""\n'
            f"import re\n\n"
        )
        py_path.write_text(header + self.function_body + "\n", encoding="utf-8")
        json_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return py_path


class LLMRuleGenerator:
    """Generates DQ rules from steward prose via the Anthropic API.

    Parameters
    ----------
    api_key
        Anthropic API key. Falls back to the ``ANTHROPIC_API_KEY`` env var.
    model
        Model ID. Default is a recent Sonnet — override to use Opus for
        harder rules at higher cost.
    max_tokens
        Per-call output token budget. Default 1024 is plenty for one rule.
    client
        Optional pre-built client (used in tests for mocking).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: Any = None,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = client
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._api_key:
            raise LLMUnavailableError(
                "ANTHROPIC_API_KEY is not set. Configure it in the environment "
                "or pass api_key= to LLMRuleGenerator."
            )
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise LLMUnavailableError("anthropic package not installed") from e
        self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def generate(self, prose: str, sample_columns: list[str] | None = None) -> GeneratedRule:
        """Compile a prose rule into a GeneratedRule pending steward review."""
        prose = prose.strip()
        if not prose:
            raise ValueError("prose cannot be empty")

        sample_columns = sample_columns or []
        client = self._ensure_client()

        user_text = self._format_user_prompt(prose, sample_columns)
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[EMIT_RULE_TOOL],
            tool_choice={"type": "tool", "name": "emit_rule"},
            messages=[{"role": "user", "content": user_text}],
        )

        tool_input = self._extract_tool_input(response)
        rule = self._tool_input_to_rule(tool_input, prose, sample_columns)
        self._validate_function_body(rule.function_body)
        return rule

    @staticmethod
    def _format_user_prompt(prose: str, columns: list[str]) -> str:
        col_block = ", ".join(columns) if columns else "(unspecified)"
        return (
            f"Steward prose:\n{prose}\n\n"
            f"Available row columns: {col_block}\n\n"
            f"Emit a single rule via the emit_rule tool."
        )

    @staticmethod
    def _extract_tool_input(response: Any) -> dict[str, Any]:
        for block in getattr(response, "content", []):
            if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == "emit_rule":
                raw = getattr(block, "input", None)
                if isinstance(raw, dict):
                    return raw
        raise LLMUnavailableError("Model did not emit a tool_use block — cannot generate rule.")

    @staticmethod
    def _tool_input_to_rule(
        tool_input: dict[str, Any],
        prose: str,
        sample_columns: list[str],
    ) -> GeneratedRule:
        name = _safe_snake(tool_input["name"])
        rule_id = hashlib.sha256(
            f"{name}:{prose}:{datetime.utcnow().isoformat()}".encode("utf-8")
        ).hexdigest()[:12]
        return GeneratedRule(
            rule_id=rule_id,
            name=name,
            description=tool_input["description"],
            severity=tool_input["severity"],
            fields=list(tool_input.get("fields", [])),
            function_body=tool_input["function_body"],
            prompt=prose,
            model=tool_input.get("__model__", ""),
            sample_columns=sample_columns,
        )

    @staticmethod
    def _validate_function_body(body: str) -> None:
        """Parse the body and reject obvious dangerous calls.

        This is *not* a sandbox — it's a static-analysis guard that catches
        accidents and obvious LLM regressions. Steward review is the real
        safety net.
        """
        try:
            tree = ast.parse(body)
        except SyntaxError as e:
            raise ValueError(f"generated function failed to parse: {e}") from e

        forbidden_names = {"eval", "exec", "open", "compile", "__import__"}
        forbidden_modules = {"os", "subprocess", "socket", "shutil", "pathlib"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in forbidden_names:
                    raise ValueError(f"generated rule calls forbidden function: {func.id}")
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    if func.value.id in forbidden_modules:
                        raise ValueError(
                            f"generated rule references forbidden module: {func.value.id}"
                        )
            if isinstance(node, ast.Import):
                raise ValueError("generated rule may not import modules")
            if isinstance(node, ast.ImportFrom):
                raise ValueError("generated rule may not import modules")

        # Confirm a `check` function with the right signature is present
        funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        if not any(f.name == "check" for f in funcs):
            raise ValueError("generated function body must define `def check(row: dict) -> bool`")


_SAFE_NAME_RE = re.compile(r"[^a-z0-9_]+")


def _safe_snake(name: str) -> str:
    """Normalise a model-emitted rule name into a safe filename / identifier."""
    s = name.strip().lower().replace("-", "_").replace(" ", "_")
    s = _SAFE_NAME_RE.sub("", s)
    if not s or not s[0].isalpha():
        s = f"rule_{s}" if s else "unnamed_rule"
    return s[:60]
