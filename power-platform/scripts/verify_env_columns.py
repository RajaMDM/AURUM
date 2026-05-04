"""
verify_env_columns.py — Quirk 10 systematic verification across all 5 AURUM-PP tables.

Reads the deployed env metadata via Dataverse Web API for each of the 5 tables
(aurum_customer, aurum_crm_customer, aurum_ecomm_customer, aurum_loyalty_customer,
aurum_assay_profile), builds the load_sample_data.py Plan locally to harvest every
column key the script writes per entity_logical, then computes the drift in both
directions:

  ghost columns   — script writes them but env lacks them (Quirk 10 anti-pattern,
                    will cause HTTP 400 on insert; must be dropped or deployed)
  missing columns — env has aurum_* attributes the script never populates
                    (informational; not a defect, but useful for completeness review)

Writes docs/env_column_manifest_<DATE>.md as the verification artifact. Future
scripts touching env data should diff their payload key sets against this manifest
before any POST.

Usage:
    python scripts/verify_env_columns.py

No writes to env. Read-only metadata + local plan introspection.
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any

import requests

# Make scripts/ importable so we can pull in load_sample_data and auth.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from auth import get_token  # noqa: E402
from load_sample_data import (  # noqa: E402
    CALC_FIELDS_TO_SKIP,
    DEFAULT_ENTITY_SETS,
    build_plan,
    get_dataverse_url,
)

log = logging.getLogger("aurum_pp.verify_env_columns")

ODATA_BIND_SUFFIX = "@odata.bind"

# OOTB system attributes we filter out of the "missing" report — they're never
# populated by load_sample_data and never should be (Dataverse manages them).
SYSTEM_ATTRIBUTE_PREFIXES: tuple[str, ...] = (
    "createdby", "createdon", "createdonbehalfby",
    "modifiedby", "modifiedon", "modifiedonbehalfby",
    "owningbusinessunit", "owningteam", "owninguser",
    "ownerid", "statecode", "statuscode",
    "versionnumber", "importsequencenumber",
    "overriddencreatedon", "timezoneruleversionnumber",
    "utcconversiontimezonecode",
    # Auto-companion lookup-id columns (e.g., aurum_canonicalcustomerid that
    # pairs with aurum_canonical_customer)
)


def collect_script_columns(plan: Any) -> dict[str, set[str]]:
    """Walk a built Plan and return: entity_logical -> set of column keys written.

    Normalizes @odata.bind keys back to their underlying lookup attribute names
    (e.g., 'aurum_canonical_customer@odata.bind' -> 'aurum_canonical_customer')
    so they diff correctly against env metadata.
    """
    by_entity: dict[str, set[str]] = {k: set() for k in DEFAULT_ENTITY_SETS}

    def harvest(entity_logical: str, payload: dict[str, Any]) -> None:
        for k in payload:
            key = k[: -len(ODATA_BIND_SUFFIX)] if k.endswith(ODATA_BIND_SUFFIX) else k
            by_entity[entity_logical].add(key)

    # Demo-story records
    for story in plan.demo_stories:
        for rec in story.records:
            harvest(rec.entity_logical, rec.payload)
        # Note: load_sample_data.py adds 'aurum_canonical_customer@odata.bind'
        # at insert time (not in DemoRecord.payload). Add it explicitly so the
        # ghost-check covers what's actually POSTed.
        for rec in story.records:
            if rec.entity_logical != "aurum_customer" and rec.links_to_canonical_role:
                by_entity[rec.entity_logical].add("aurum_canonical_customer")

    # Filler records
    for c in plan.filler_canonicals:
        harvest("aurum_customer", c["payload"])
    for entity_logical, recs in [
        ("aurum_crm_customer", plan.filler_crm),
        ("aurum_ecomm_customer", plan.filler_ecomm),
        ("aurum_loyalty_customer", plan.filler_loyalty),
    ]:
        for rec in recs:
            harvest(entity_logical, rec["payload"])
            if rec.get("_links_canonical_index") is not None:
                by_entity[entity_logical].add("aurum_canonical_customer")

    # Assay records (assay_records is a list of payload dicts, not wrapped)
    for r in plan.assay_records:
        harvest("aurum_assay_profile", r)

    return by_entity


def fetch_env_attributes(
    base_url: str, token: str, entity_logical: str
) -> list[dict[str, Any]]:
    """GET /api/data/v9.2/EntityDefinitions(LogicalName='<table>')/Attributes
    Returns list of {LogicalName, AttributeType, IsCustomAttribute} dicts."""
    url = (
        base_url.rstrip("/")
        + "/api/data/v9.2/"
        + f"EntityDefinitions(LogicalName='{entity_logical}')"
        + "/Attributes?$select=LogicalName,AttributeType,IsCustomAttribute"
    )
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        },
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(
            f"GET Attributes for {entity_logical} failed: HTTP {resp.status_code} "
            f"{resp.reason}\n  body: {resp.text[:500]}"
        )
    return resp.json().get("value", [])


def is_system_column(name: str) -> bool:
    """OOTB system attribute we don't expect the script to populate."""
    if name in SYSTEM_ATTRIBUTE_PREFIXES:
        return True
    # Auto-companion id columns Dataverse silently creates for primary-name and
    # lookup attributes (e.g., aurum_customerid pairs with aurum_customer's PK).
    if name.endswith("id") and name.startswith("aurum_"):
        # Only flag as system if there's an obvious sibling — but we can't know
        # that here without more env data. Be conservative: include in missing
        # list and let the human review.
        return False
    return False


def render_manifest(
    by_entity_script: dict[str, set[str]],
    by_entity_env: dict[str, dict[str, dict[str, Any]]],
    today: str,
) -> str:
    """Render the full env-column-manifest markdown doc.

    Renders header → summary table (computed up front) → per-table sections.
    Avoids the prior bug where summary was line-inserted mid-document.
    """
    # Compute summary first so the table can be rendered in its proper place.
    summary: list[tuple[str, int, int, int]] = []  # (table, env_aurum, ghosts, missing_aurum)
    for entity_logical in DEFAULT_ENTITY_SETS:
        env_attrs = by_entity_env.get(entity_logical, {})
        env_names = set(env_attrs.keys())
        script_names = by_entity_script.get(entity_logical, set())
        ghosts = sorted(script_names - env_names)
        missing_aurum = sorted(
            n for n in (env_names - script_names)
            if n.startswith("aurum_") and not is_system_column(n)
        )
        env_aurum_count = sum(1 for n in env_names if n.startswith("aurum_"))
        summary.append((entity_logical, env_aurum_count, len(ghosts), len(missing_aurum)))

    lines: list[str] = []
    lines.append(f"# AURUM-PP env column manifest — {today}")
    lines.append("")
    lines.append(
        "Generated by `scripts/verify_env_columns.py`. Captures the actual deployed "
        "column list per table (queried via Dataverse Web API EntityDefinitions/"
        "Attributes) vs the columns `scripts/load_sample_data.py` writes, with "
        "drift in both directions surfaced explicitly."
    )
    lines.append("")
    lines.append(
        "**Quirk 10 verification artifact.** Future scripts touching env data should "
        "diff their payload key sets against this manifest before any POST. Memory: "
        "`project_aurum_pp_dataverse_quirks.md` Quirk 10."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Table | env aurum_ cols | ghost cols | env-only aurum_ cols |")
    lines.append("|---|---:|---:|---:|")
    for tbl, env_n, ghost_n, missing_n in summary:
        lines.append(f"| `{tbl}` | {env_n} | {ghost_n} | {missing_n} |")
    lines.append("")

    for entity_logical in DEFAULT_ENTITY_SETS:
        env_attrs = by_entity_env.get(entity_logical, {})
        env_names = set(env_attrs.keys())
        script_names = by_entity_script.get(entity_logical, set())

        ghosts = sorted(script_names - env_names)
        missing_aurum = sorted(
            n for n in (env_names - script_names)
            if n.startswith("aurum_") and not is_system_column(n)
        )

        env_aurum_count = sum(1 for n in env_names if n.startswith("aurum_"))

        lines.append(f"## `{entity_logical}`")
        lines.append("")
        lines.append(
            f"- Env (deployed) custom-aurum_ columns: **{env_aurum_count}** "
            f"(plus OOTB system attributes, omitted)"
        )
        lines.append(f"- Script writes: **{len(script_names)}** distinct keys")
        lines.append(f"- Ghost columns (script writes, env lacks): **{len(ghosts)}**")
        lines.append(
            f"- Missing-from-script (env has, script doesn't populate): "
            f"**{len(missing_aurum)}** aurum_ columns"
        )
        lines.append("")

        # Ghosts — the actionable section
        lines.append("### Ghost columns (script→env drift, MUST FIX)")
        lines.append("")
        if not ghosts:
            lines.append("_None — script payloads align with env._")
        else:
            for g in ghosts:
                lines.append(f"- `{g}`")
        lines.append("")

        # Missing — informational
        lines.append("### aurum_ columns deployed in env but never written by script")
        lines.append("")
        if not missing_aurum:
            lines.append(
                "_None — script populates every deployed aurum_ column "
                "(or correctly omits via remove_calc_fields)._"
            )
        else:
            lines.append(
                "_Informational. May indicate: (a) calc/derived fields populated "
                "post-insert by Dataverse, (b) staging-only fields not relevant to "
                "demo, (c) genuine coverage gap to consider._"
            )
            lines.append("")
            for m in missing_aurum:
                attr_type = env_attrs[m].get("AttributeType", "?")
                lines.append(f"- `{m}` ({attr_type})")
        lines.append("")

        # Full env column list (collapsible-friendly)
        lines.append(f"<details><summary>Full env column list ({len(env_names)} attributes)</summary>")
        lines.append("")
        for n in sorted(env_names):
            attr_type = env_attrs[n].get("AttributeType", "?")
            is_custom = env_attrs[n].get("IsCustomAttribute", False)
            tag = "custom" if is_custom else "system"
            lines.append(f"- `{n}` ({attr_type}, {tag})")
        lines.append("")
        lines.append("</details>")
        lines.append("")

        # Full script keys list
        lines.append(f"<details><summary>Full script-written key list ({len(script_names)} keys)</summary>")
        lines.append("")
        for n in sorted(script_names):
            in_env = "✓" if n in env_names else "✗ GHOST"
            lines.append(f"- `{n}` [{in_env}]")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    log.info("Building plan locally to harvest script column keys")
    plan = build_plan()
    by_entity_script = collect_script_columns(plan)
    for ent, keys in by_entity_script.items():
        log.info("  %s: %d distinct keys written by script", ent, len(keys))

    log.info("Acquiring Dataverse token")
    token = get_token()
    base_url = get_dataverse_url()

    log.info("Querying env metadata for 5 tables")
    by_entity_env: dict[str, dict[str, dict[str, Any]]] = {}
    for entity_logical in DEFAULT_ENTITY_SETS:
        attrs = fetch_env_attributes(base_url, token, entity_logical)
        by_entity_env[entity_logical] = {a["LogicalName"]: a for a in attrs}
        log.info("  %s: %d attributes in env", entity_logical, len(attrs))

    today = date.today().isoformat()
    manifest = render_manifest(by_entity_script, by_entity_env, today)

    out_path = SCRIPTS_DIR.parent / "docs" / f"env_column_manifest_{today}.md"
    # write_text overwrites by default — re-runnable on every env change without
    # accumulating stale appended content. Manifest is a snapshot, not a log.
    out_path.write_text(manifest, encoding="utf-8")
    log.info("Manifest written (overwrites prior): %s", out_path)

    # Print stdout summary for human triage
    print()
    print("=" * 72)
    print(f"DRIFT SUMMARY — {today}")
    print("=" * 72)
    total_ghosts = 0
    for entity_logical in DEFAULT_ENTITY_SETS:
        env_names = set(by_entity_env[entity_logical].keys())
        script_names = by_entity_script[entity_logical]
        ghosts = sorted(script_names - env_names)
        total_ghosts += len(ghosts)
        print(f"\n{entity_logical}: {len(ghosts)} ghost column(s)")
        for g in ghosts:
            print(f"  ✗ GHOST: {g}")
        if not ghosts:
            print("  ✓ no ghosts")
    print()
    print(f"TOTAL GHOSTS across 5 tables: {total_ghosts}")
    print(f"Full manifest: {out_path.relative_to(SCRIPTS_DIR.parent)}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
