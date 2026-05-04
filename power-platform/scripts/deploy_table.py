"""
deploy_table.py — YAML→Web API deployer for AURUM-PP staging tables (02-05).

Reads one AURUM-PP table YAML (e.g. dataverse/schemas/02_aurum_crm_customer_staging.yaml),
applies the conventions from project_aurum_pp_table_conventions.md (memory) verbatim,
posts entity + columns + option sets + (optional) lookup to the Dataverse Web API,
then runs a verification read-back that reports column count, choice value
verification, schema-name casing audit, and any deviations from conventions.

Stops on the first failure. Aborts before any POST if the table already exists,
the entity is on the off-limits list, or the lookup target (aurum_customer) is
missing from the env.

Usage:
    # dry-run — print planned payloads to stdout, write nothing, no auth, no env vars needed
    python scripts/deploy_table.py dataverse/schemas/02_aurum_crm_customer_staging.yaml --dry-run

    # real deploy — writes to the env named by AURUM_PP_DATAVERSE_URL
    python scripts/deploy_table.py dataverse/schemas/02_aurum_crm_customer_staging.yaml

Required environment variables (set in ~/.zprofile) for non-dry-run:
    AURUM_PP_DATAVERSE_URL          e.g. https://<env-host>.crm.dynamics.com/
    AURUM_PP_SOLUTION_UNIQUE_NAME   the unique name (NOT display name) of the
                                    target solution. Discover via:
                                      GET /api/data/v9.2/solutions
                                          ?$select=uniquename
                                          &$filter=friendlyname eq 'AURUM Master Data Management'

Auth uses scripts/auth.py — silent token from cache, falls back to device-code
only if cache expired.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auth import get_token  # noqa: E402

# ---------------------------------------------------------------------------
# Required env vars
# ---------------------------------------------------------------------------

ENV_DATAVERSE_URL = "AURUM_PP_DATAVERSE_URL"
ENV_SOLUTION_NAME = "AURUM_PP_SOLUTION_UNIQUE_NAME"

# ---------------------------------------------------------------------------
# CONVENTIONS — single source of truth, mirrors project_aurum_pp_table_conventions.md.
# When the conventions doc changes, change this block and only this block.
# Audit this dict against the memory file before any deployment.
# ---------------------------------------------------------------------------

CONVENTIONS: dict[str, Any] = {
    # Per-column flags applied to every attribute on every AURUM-PP table.
    "per_column": {
        "IsSecured": False,
        "IsAuditEnabled": {"Value": True},
        "IsValidForAdvancedFind": {"Value": True},
    },
    # Per-table flags applied to every staging/profile table (NOT to aurum_customer
    # which is OFF LIMITS — that table was deployed manually with HasNotes=true,
    # an asymmetry the conventions doc explicitly preserves).
    # HasNotes/HasActivities are immutable post-create — must be set on entity POST.
    "per_table": {
        "IsAuditEnabled": {"Value": True},
        "IsDuplicateDetectionEnabled": {"Value": True},
        "ChangeTrackingEnabled": True,
        "IsQuickCreateEnabled": True,
        "IsRetentionEnabled": False,
        "IsMailMergeEnabled": {"Value": False},
        "IsConnectionsEnabled": {"Value": True},
        # PRIMITIVE BOOL at EntityMetadata level (NOT BooleanManagedProperty).
        # Asymmetric vs the per_column counterpart which IS nested. See
        # feedback_verify_dataverse_state_via_webapi.md for the shape table.
        "IsValidForAdvancedFind": True,
        "HasNotes": False,
        "HasActivities": False,
        "EntityColor": "#29588C",
    },
    # Cascade for the aurum_canonical_customer → aurum_customer lookup on staging
    # tables. Referential = staging records survive if canonical is deleted
    # (REFINE re-resolves the link).
    "lookup_cascade": {
        "Assign": "NoCascade",
        "Delete": "RemoveLink",
        "Merge": "NoCascade",
        "Reparent": "NoCascade",
        "Share": "NoCascade",
        "Unshare": "NoCascade",
    },
    # Choice defaults for staging tables. Looked up by column schema_name —
    # works across 02/03/04 because they share these column names. Assay (05)
    # has no entries here, so its option columns get DefaultFormValue=-1
    # (Dataverse's "no default" sentinel) by virtue of the field being omitted.
    "staging_choice_defaults": {
        "aurum_match_method": 5,        # Unmatched (5 in CRM/ECOMM, also 5 in LOYALTY's 6-option list)
        "aurum_processing_status": 1,   # Loaded
    },
    "lookup_target_entity": "aurum_customer",
    "off_limits_entities": {"aurum_customer"},
}

# Per-table A1 overrides: when YAML's stated primary_name_attribute is a
# CalculatedField (which Dataverse rejects as PrimaryNameAttribute on entity
# create), promote a regular column to PrimaryName and add the calc field in a
# second pass after regular columns exist.
PRIMARY_NAME_OVERRIDES: dict[str, dict[str, Any]] = {
    "aurum_crm_customer": {
        # last_name has higher search cardinality than first_name across most
        # populations — better default search behavior in lookup pickers.
        "promoted_primary": "aurum_last_name_raw",
        "calc_field_name": "aurum_full_name_display",
        "calc_formula": 'CONCAT(aurum_first_name_raw, " ", aurum_last_name_raw)',
    },
}

# en-US — all AURUM-PP labels.
LANG_CODE = 1033

log = logging.getLogger("aurum_pp.deploy_table")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------


def get_required_env(name: str, hint: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(
            f"{name} environment variable not set.\n"
            f"  Hint: {hint}\n"
            f"  Add to ~/.zprofile:  export {name}=<value>\n"
            f"  Then:  source ~/.zprofile"
        )
    return val


def get_dataverse_url() -> str:
    url = get_required_env(
        ENV_DATAVERSE_URL,
        "Set to your Dataverse environment URL, e.g. https://<env-host>.crm.dynamics.com/",
    )
    return url if url.endswith("/") else url + "/"


def get_solution_name() -> str:
    return get_required_env(
        ENV_SOLUTION_NAME,
        "Set to the unique name of the target solution. Discover via:\n"
        "    GET /api/data/v9.2/solutions?$select=uniquename"
        "&$filter=friendlyname eq 'AURUM Master Data Management'",
    )


# ---------------------------------------------------------------------------
# Web API client — bearer auth, OData headers, MSCRM.SolutionUniqueName on writes
# ---------------------------------------------------------------------------


class WebAPI:
    """Thin wrapper. Raises RuntimeError on any non-2xx with body excerpt."""

    def __init__(self, base_url: str, token: str, solution_name: str) -> None:
        self.base = base_url + "api/data/v9.2/"
        self.token = token
        self.solution_name = solution_name

    def _headers(self, *, write: bool) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        if write:
            h["Content-Type"] = "application/json"
            # Tells Dataverse which solution the new metadata belongs to so the
            # components ship together when this solution is exported (Phase 5).
            # Without this header, components land in the default solution and
            # cannot be packaged.
            h["MSCRM.SolutionUniqueName"] = self.solution_name
        return h

    def get(self, path: str) -> dict[str, Any]:
        url = self.base + path.lstrip("/")
        log.debug("GET %s", url)
        resp = requests.get(url, headers=self._headers(write=False), timeout=30)
        if not resp.ok:
            raise RuntimeError(
                f"GET {path} failed: HTTP {resp.status_code} {resp.reason}\n"
                f"  body: {resp.text[:500]}"
            )
        return resp.json()

    def get_or_none(self, path: str) -> dict[str, Any] | None:
        """GET that returns None on 404. Used for existence checks."""
        url = self.base + path.lstrip("/")
        resp = requests.get(url, headers=self._headers(write=False), timeout=30)
        if resp.status_code == 404:
            return None
        if not resp.ok:
            raise RuntimeError(
                f"GET {path} failed: HTTP {resp.status_code} {resp.reason}\n"
                f"  body: {resp.text[:500]}"
            )
        return resp.json()

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a write. Returns body merged with `_entity_id_url` from the
        OData-EntityId response header (Dataverse's canonical way of returning
        the new MetadataId on metadata creates, often with empty body)."""
        url = self.base + path.lstrip("/")
        log.debug("POST %s", url)
        resp = requests.post(
            url, headers=self._headers(write=True), json=payload, timeout=60,
        )
        if not resp.ok:
            raise RuntimeError(
                f"POST {path} failed: HTTP {resp.status_code} {resp.reason}\n"
                f"  body: {resp.text[:1000]}"
            )
        entity_id_url = resp.headers.get("OData-EntityId", "")
        body: dict[str, Any] = {}
        if resp.text:
            try:
                body = resp.json()
            except json.JSONDecodeError:
                body = {}
        if entity_id_url:
            body["_entity_id_url"] = entity_id_url
            log.info("    → MetadataId URL: %s", entity_id_url)
        return body


# ---------------------------------------------------------------------------
# Localized label + RequiredLevel helpers
# ---------------------------------------------------------------------------


def label(text: str) -> dict[str, Any]:
    return {"LocalizedLabels": [{"Label": text, "LanguageCode": LANG_CODE}]}


def required_level(req: bool) -> dict[str, str]:
    return {"Value": "ApplicationRequired" if req else "None"}


# ---------------------------------------------------------------------------
# Per-type attribute payload builders
# ---------------------------------------------------------------------------


def _common_attr(col: dict[str, Any], odata_type: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "@odata.type": f"Microsoft.Dynamics.CRM.{odata_type}",
        "SchemaName": col["schema_name"],
        "LogicalName": col["schema_name"],
        "DisplayName": label(col["display_name"]),
        "RequiredLevel": required_level(col.get("required", False)),
    }
    if "description" in col:
        payload["Description"] = label(col["description"])
    payload.update(CONVENTIONS["per_column"])
    return payload


def build_string_attr(col: dict[str, Any]) -> dict[str, Any]:
    p = _common_attr(col, "StringAttributeMetadata")
    p["MaxLength"] = col.get("max_length", 100)
    p["FormatName"] = {"Value": "Email" if col.get("format") == "Email" else "Text"}
    return p


def build_integer_attr(col: dict[str, Any]) -> dict[str, Any]:
    p = _common_attr(col, "IntegerAttributeMetadata")
    if "min_value" in col:
        p["MinValue"] = col["min_value"]
    if "max_value" in col:
        p["MaxValue"] = col["max_value"]
    return p


def build_decimal_attr(col: dict[str, Any]) -> dict[str, Any]:
    p = _common_attr(col, "DecimalAttributeMetadata")
    p["Precision"] = col.get("precision", 2)
    # YAML uses both `min`/`max` and `min_value`/`max_value` across schemas.
    if "min" in col or "min_value" in col:
        p["MinValue"] = col.get("min", col.get("min_value"))
    if "max" in col or "max_value" in col:
        p["MaxValue"] = col.get("max", col.get("max_value"))
    return p


def build_currency_attr(col: dict[str, Any]) -> dict[str, Any]:
    p = _common_attr(col, "MoneyAttributeMetadata")
    p["Precision"] = 2
    p["PrecisionSource"] = 2
    return p


def build_datetime_attr(col: dict[str, Any], *, date_only: bool) -> dict[str, Any]:
    p = _common_attr(col, "DateTimeAttributeMetadata")
    p["Format"] = "DateOnly" if date_only else "DateAndTime"
    p["DateTimeBehavior"] = {"Value": "UserLocal"}
    return p


def build_picklist_attr(
    col: dict[str, Any], *, default_value: int | None,
) -> dict[str, Any]:
    """OptionSet with explicit small-int values from YAML.

    Dataverse default is to assign 100000001+; we MUST pass explicit Value on
    each option to anchor at 1..N as the conventions require. Local option set
    (IsGlobal=False) — owned by this attribute, not a tenant-wide choice.
    """
    p = _common_attr(col, "PicklistAttributeMetadata")
    options = [
        {"Value": opt["value"], "Label": label(opt["label"])}
        for opt in col["options"]
    ]
    p["OptionSet"] = {
        "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
        "OptionSetType": "Picklist",
        "IsGlobal": False,
        "Options": options,
    }
    if default_value is not None:
        p["DefaultFormValue"] = default_value
    return p


def build_relationship_lookup(
    *,
    relationship_schema: str,
    referenced_entity: str,
    referencing_entity: str,
    lookup_col: dict[str, Any],
) -> dict[str, Any]:
    """OneToMany relationship payload. Creates the lookup column on the
    referencing (many) side as a side-effect. Cascade per CONVENTIONS."""
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
        "SchemaName": relationship_schema,
        "ReferencedEntity": referenced_entity,
        "ReferencingEntity": referencing_entity,
        "Lookup": {
            "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
            "SchemaName": lookup_col["schema_name"],
            "LogicalName": lookup_col["schema_name"],
            "DisplayName": label(lookup_col["display_name"]),
            "Description": label(lookup_col.get("description", "")),
            "RequiredLevel": {"Value": "None"},
            **CONVENTIONS["per_column"],
        },
        "CascadeConfiguration": CONVENTIONS["lookup_cascade"],
    }


# ---------------------------------------------------------------------------
# YAML column type predicates + dispatch
# ---------------------------------------------------------------------------


def is_primary_key(col: dict[str, Any]) -> bool:
    return col.get("is_primary_key", False)


def is_lookup(col: dict[str, Any]) -> bool:
    return col.get("type") == "Lookup"


def is_calculated(col: dict[str, Any]) -> bool:
    return col.get("type") == "CalculatedField"


def is_optionset(col: dict[str, Any]) -> bool:
    return col.get("type") == "OptionSet"


def build_simple_attr(col: dict[str, Any], default_value: int | None = None) -> dict[str, Any]:
    """Dispatch a non-PK, non-lookup, non-calc column."""
    t = col["type"]
    if t == "SingleLineOfText":
        return build_string_attr(col)
    if t == "WholeNumber":
        return build_integer_attr(col)
    if t == "Decimal":
        return build_decimal_attr(col)
    if t == "Currency":
        return build_currency_attr(col)
    if t == "DateOnly":
        return build_datetime_attr(col, date_only=True)
    if t == "DateAndTime":
        return build_datetime_attr(col, date_only=False)
    if t == "OptionSet":
        return build_picklist_attr(col, default_value=default_value)
    raise RuntimeError(
        f"Unsupported YAML type: {t!r} on column {col.get('schema_name')!r}"
    )


# ---------------------------------------------------------------------------
# Entity payload — PrimaryNameAttribute baked in (Dataverse requirement)
# ---------------------------------------------------------------------------


def build_entity_payload(
    yaml_data: dict[str, Any], *, primary_attr_name: str,
) -> dict[str, Any]:
    e = yaml_data["entity"]
    primary_col = next(
        c for c in yaml_data["columns"] if c["schema_name"] == primary_attr_name
    )
    primary_payload = build_string_attr(primary_col)
    # Dataverse CreateEntity requires IsPrimaryName=true on exactly one
    # attribute in Attributes[]. The error "Required field 'PrimaryAttribute'
    # is missing" really means this flag isn't set anywhere. AttributeType +
    # AttributeTypeName mirror what aurum_customer's primary carries on
    # read-back — defensive alongside @odata.type.
    primary_payload["IsPrimaryName"] = True
    primary_payload["AttributeType"] = "String"
    primary_payload["AttributeTypeName"] = {"Value": "StringType"}
    payload: dict[str, Any] = {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": e["schema_name"],
        "LogicalName": e["schema_name"],
        "DisplayName": label(e["display_name"]),
        "DisplayCollectionName": label(e["display_collection_name"]),
        "Description": label(e.get("description", "")),
        "OwnershipType": e.get("ownership_type", "UserOwned"),
        "PrimaryNameAttribute": primary_attr_name,
        "Attributes": [primary_payload],
    }
    payload.update(CONVENTIONS["per_table"])
    return payload


# ---------------------------------------------------------------------------
# Plan building — pure local computation, no network
# ---------------------------------------------------------------------------


def determine_primary_name(yaml_data: dict[str, Any]) -> str:
    """Resolve the actual PrimaryNameAttribute. If the YAML's stated value is a
    calculated field, look up the override; otherwise pass through."""
    e = yaml_data["entity"]
    stated = e["primary_name_attribute"]
    stated_col = next(
        (c for c in yaml_data["columns"] if c["schema_name"] == stated), None
    )
    if stated_col and is_calculated(stated_col):
        override = PRIMARY_NAME_OVERRIDES.get(e["schema_name"])
        if not override:
            raise RuntimeError(
                f"Entity {e['schema_name']} has calculated PrimaryNameAttribute "
                f"{stated!r} but no PRIMARY_NAME_OVERRIDES entry. Add one before "
                f"retrying."
            )
        return override["promoted_primary"]
    return stated


def build_plan(yaml_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the ordered list of operations.

    Order:
      1. Create entity (with promoted PrimaryName attribute baked in)
      2. Create each non-PK, non-lookup, non-calc, non-primary column
      3. Create lookup (if any) via OneToMany relationship
      4. Create calc field (if override exists) — last because formula references real cols
    """
    e = yaml_data["entity"]
    entity_name = e["schema_name"]
    primary_name = determine_primary_name(yaml_data)
    plan: list[dict[str, Any]] = []

    # 1. Entity
    entity_payload = build_entity_payload(yaml_data, primary_attr_name=primary_name)
    plan.append({
        "description": f"Create entity {entity_name} (PrimaryName={primary_name})",
        "method": "POST",
        "path": "EntityDefinitions",
        "payload": entity_payload,
    })

    # 2. Regular columns
    staging_defaults = CONVENTIONS["staging_choice_defaults"]
    for col in yaml_data["columns"]:
        if is_primary_key(col):
            continue  # Auto-created; verified post-hoc by name match
        if col["schema_name"] == primary_name:
            continue  # Already inline in entity payload
        if is_lookup(col):
            continue  # Handled in step 3
        if is_calculated(col):
            continue  # Handled in step 4

        default_value = (
            staging_defaults.get(col["schema_name"]) if is_optionset(col) else None
        )
        attr_payload = build_simple_attr(col, default_value=default_value)
        plan.append({
            "description": f"Create column {col['schema_name']} (type={col['type']})",
            "method": "POST",
            "path": f"EntityDefinitions(LogicalName='{entity_name}')/Attributes",
            "payload": attr_payload,
        })

    # 3. Lookup column(s) via relationship
    for col in yaml_data["columns"]:
        if not is_lookup(col):
            continue
        target = col["target_entity"]
        relationship_schema = f"{target}_{entity_name}_{col['schema_name']}"
        rel_payload = build_relationship_lookup(
            relationship_schema=relationship_schema,
            referenced_entity=target,
            referencing_entity=entity_name,
            lookup_col=col,
        )
        plan.append({
            "description": (
                f"Create lookup {col['schema_name']} → {target} "
                f"(relationship={relationship_schema}, Referential cascade)"
            ),
            "method": "POST",
            "path": "RelationshipDefinitions",
            "payload": rel_payload,
        })

    # 4. Calculated field — DEFERRED to manual maker UI creation.
    # Dataverse's Web API requires FormulaDefinition as compiled XAML
    # (workflow activity definition), not the simple-text expression syntax.
    # XAML synthesis is non-trivial for one column on one table. See
    # project_aurum_pp_dataverse_quirks.md (Quirk 3) — trigger to revisit
    # is when 3+ tables need calc fields.
    override = PRIMARY_NAME_OVERRIDES.get(entity_name)
    if override:
        log.info(
            "Calc field %s deferred to manual maker UI creation. "
            "See project_aurum_pp_dataverse_quirks.md.",
            override["calc_field_name"],
        )
        log.info(
            "  Intended formula for the maker UI step: %s",
            override["calc_formula"],
        )

    return plan


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------


def pre_flight(api: WebAPI, yaml_data: dict[str, Any]) -> None:
    """Run all pre-flight checks. Raises RuntimeError on any failure."""
    e = yaml_data["entity"]
    entity_name = e["schema_name"]

    if entity_name in CONVENTIONS["off_limits_entities"]:
        raise RuntimeError(
            f"Entity {entity_name} is in OFF_LIMITS_ENTITIES — refusing to deploy. "
            f"This table was deployed manually and is protected from automation."
        )

    existing = api.get_or_none(
        f"EntityDefinitions(LogicalName='{entity_name}')?$select=LogicalName"
    )
    if existing is not None:
        raise RuntimeError(
            f"Table {entity_name} already exists in env. Aborting (no detect-and-resume). "
            f"Manual cleanup required before re-run — delete via maker.powerapps.com or "
            f"a solution-cleanup flow, then retry."
        )

    lookups = [c for c in yaml_data["columns"] if is_lookup(c)]
    for col in lookups:
        target = col["target_entity"]
        target_meta = api.get_or_none(
            f"EntityDefinitions(LogicalName='{target}')?$select=LogicalName"
        )
        if target_meta is None:
            raise RuntimeError(
                f"Lookup target {target!r} not found in env (required by column "
                f"{col['schema_name']!r}). Was table 01 (aurum_customer) deployed? "
                f"Aborting before any writes."
            )

    log.info("Pre-flight: entity does not yet exist; lookup targets present; OK to proceed.")


# ---------------------------------------------------------------------------
# Plan execution — stop on first failure
# ---------------------------------------------------------------------------


def execute_plan(api: WebAPI, plan: list[dict[str, Any]]) -> None:
    for i, op in enumerate(plan, start=1):
        log.info("[%d/%d] %s", i, len(plan), op["description"])
        try:
            result = api.post(op["path"], op["payload"])
        except RuntimeError as exc:
            raise RuntimeError(
                f"Step {i}/{len(plan)} failed: {op['description']}\n"
                f"  POST {op['path']}\n"
                f"  Error: {exc}\n"
                f"Stopping. Steps 1..{i - 1} succeeded; step {i} did not. "
                f"Inspect partial state in env before retrying."
            ) from exc
        op["result"] = result


# ---------------------------------------------------------------------------
# Verification — read-back via Web API + structured report
# ---------------------------------------------------------------------------


def _calc_field_names() -> set[str]:
    """All schema_names that are deployed as calc fields. Verification
    skips per-column flag check on these (IsAuditEnabled deliberately False)."""
    return {ov["calc_field_name"] for ov in PRIMARY_NAME_OVERRIDES.values()}


def verify_table(api: WebAPI, yaml_data: dict[str, Any]) -> dict[str, Any]:
    e = yaml_data["entity"]
    entity_name = e["schema_name"]

    entity_meta = api.get(
        f"EntityDefinitions(LogicalName='{entity_name}')"
    )
    attrs = api.get(
        f"EntityDefinitions(LogicalName='{entity_name}')/Attributes"
        "?$select=LogicalName,SchemaName,AttributeType,"
        "IsAuditEnabled,IsSecured,IsValidForAdvancedFind"
    )["value"]

    # User-defined attributes only — strip system columns (createdon, modifiedon, etc.)
    aurum_attrs = [a for a in attrs if a["LogicalName"].startswith("aurum_")]

    expected_cols = [c["schema_name"] for c in yaml_data["columns"]]
    actual_aurum_names = {a["LogicalName"] for a in aurum_attrs}
    missing = [c for c in expected_cols if c not in actual_aurum_names]
    extra = [a for a in actual_aurum_names if a not in expected_cols]

    bad_casing = [
        n for n in actual_aurum_names if n != n.lower() or " " in n
    ]

    # Choice read-back — verify each option's Value matches YAML and none auto-assigned
    choice_report = []
    for col in yaml_data["columns"]:
        if not is_optionset(col):
            continue
        picklist = api.get(
            f"EntityDefinitions(LogicalName='{entity_name}')"
            f"/Attributes(LogicalName='{col['schema_name']}')"
            "/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$expand=OptionSet"
        )
        actual_values = sorted(o["Value"] for o in picklist["OptionSet"]["Options"])
        expected_values = sorted(o["value"] for o in col["options"])
        bad = [v for v in actual_values if v >= 100000000]
        choice_report.append({
            "column": col["schema_name"],
            "expected_values": expected_values,
            "actual_values": actual_values,
            "match": expected_values == actual_values,
            "auto_assigned_above_100M": bad,
        })

    # Per-table flag deviations
    table_deviations = []
    for k, expected in CONVENTIONS["per_table"].items():
        actual = entity_meta.get(k)
        if isinstance(expected, dict) and "Value" in expected:
            actual_val = actual.get("Value") if isinstance(actual, dict) else actual
            if actual_val != expected["Value"]:
                table_deviations.append(
                    {"flag": k, "expected": expected["Value"], "actual": actual_val}
                )
        else:
            if actual != expected:
                table_deviations.append({"flag": k, "expected": expected, "actual": actual})

    # Per-column flag deviations (skipping calc fields — known exception)
    calc_names = _calc_field_names()
    col_deviations = []
    for a in aurum_attrs:
        if a["LogicalName"] in calc_names:
            continue
        for k, expected in CONVENTIONS["per_column"].items():
            actual = a.get(k)
            if isinstance(expected, dict) and "Value" in expected:
                actual_val = actual.get("Value") if isinstance(actual, dict) else actual
                if actual_val != expected["Value"]:
                    col_deviations.append({
                        "column": a["LogicalName"], "flag": k,
                        "expected": expected["Value"], "actual": actual_val,
                    })
            else:
                if actual != expected:
                    col_deviations.append({
                        "column": a["LogicalName"], "flag": k,
                        "expected": expected, "actual": actual,
                    })

    return {
        "entity": entity_name,
        "column_counts": {
            "expected": len(expected_cols),
            "actual_aurum_columns": len(actual_aurum_names),
            "missing": missing,
            "extra": extra,
        },
        "casing_audit": {
            "bad_casing": bad_casing,
            "all_clean": not bad_casing,
        },
        "choices": choice_report,
        "table_flag_deviations": table_deviations,
        "column_flag_deviations": col_deviations,
        "all_columns": sorted(actual_aurum_names),
    }


def print_report(report: dict[str, Any]) -> bool:
    clean = True
    print("\n" + "=" * 72)
    print(f"VERIFICATION REPORT — {report['entity']}")
    print("=" * 72)

    print("\n[1] Column count")
    cc = report["column_counts"]
    print(f"    expected: {cc['expected']}")
    print(f"    actual (aurum_): {cc['actual_aurum_columns']}")
    if cc["missing"]:
        clean = False
        print(f"    MISSING: {cc['missing']}")
    if cc["extra"]:
        clean = False
        print(f"    EXTRA (in env, not in YAML): {cc['extra']}")
    if not cc["missing"] and not cc["extra"]:
        print("    [OK] all columns present")

    print("\n[2] Schema-name casing")
    if report["casing_audit"]["all_clean"]:
        print("    [OK] all snake_case, no spaces")
    else:
        clean = False
        print(f"    BAD CASING: {report['casing_audit']['bad_casing']}")

    print("\n[3] Choice values read-back")
    if not report["choices"]:
        print("    (no choice columns)")
    for c in report["choices"]:
        ok = c["match"] and not c["auto_assigned_above_100M"]
        if not ok:
            clean = False
        marker = "[OK]" if ok else "[!! ]"
        print(f"    {marker} {c['column']}: expected {c['expected_values']}, actual {c['actual_values']}")
        if c["auto_assigned_above_100M"]:
            print(f"        AUTO-ASSIGNED VALUES >= 100000000: {c['auto_assigned_above_100M']}")

    print("\n[4] Per-table flag deviations")
    if not report["table_flag_deviations"]:
        print("    [OK] no deviations from CONVENTIONS.per_table")
    else:
        clean = False
        for d in report["table_flag_deviations"]:
            print(f"    [!!] {d['flag']}: expected {d['expected']!r}, actual {d['actual']!r}")

    print("\n[5] Per-column flag deviations")
    if not report["column_flag_deviations"]:
        print("    [OK] no deviations from CONVENTIONS.per_column")
    else:
        clean = False
        for d in report["column_flag_deviations"]:
            print(f"    [!!] {d['column']}.{d['flag']}: expected {d['expected']!r}, actual {d['actual']!r}")

    print("\n[6] Full schema-name listing")
    for n in report["all_columns"]:
        print(f"    {n}")

    print("\n" + ("VERIFICATION CLEAN" if clean else "VERIFICATION HAS DEVIATIONS"))
    print("=" * 72)
    return clean


# ---------------------------------------------------------------------------
# Dry-run printer
# ---------------------------------------------------------------------------


def print_plan(plan: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 72)
    print(f"DRY-RUN: planned operations ({len(plan)} total)")
    print("=" * 72)
    for i, op in enumerate(plan, start=1):
        print(f"\n--- Step {i}/{len(plan)} ---")
        print(f"Description: {op['description']}")
        print(f"{op['method']} {op['path']}")
        print("Payload:")
        print(json.dumps(op["payload"], indent=2, ensure_ascii=False))
    print("\n" + "=" * 72)
    print("DRY-RUN COMPLETE — no writes were made, no auth was performed,")
    print("no env vars were resolved. Pure offline payload inspection.")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy one AURUM-PP table from YAML to Dataverse.",
    )
    parser.add_argument("yaml_path", help="Path to the YAML schema for one table.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned API payloads to stdout and exit. No writes, no auth, no env vars.",
    )
    args = parser.parse_args()

    _configure_logging()

    yaml_path = Path(args.yaml_path).expanduser().resolve()
    if not yaml_path.exists():
        log.error("YAML not found: %s", yaml_path)
        return 1

    log.info("Loading YAML: %s", yaml_path)
    with yaml_path.open(encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    # Build the plan WITHOUT touching the network — pure local computation.
    try:
        plan = build_plan(yaml_data)
    except RuntimeError as exc:
        log.error("Plan-build failed: %s", exc)
        return 1

    if args.dry_run:
        print_plan(plan)
        return 0

    try:
        base_url = get_dataverse_url()
        solution_name = get_solution_name()
    except RuntimeError as exc:
        log.error("%s", exc)
        return 1

    try:
        token = get_token()
    except RuntimeError as exc:
        log.error("Auth failed: %s", exc)
        return 1

    api = WebAPI(base_url=base_url, token=token, solution_name=solution_name)

    try:
        pre_flight(api, yaml_data)
    except RuntimeError as exc:
        log.error("Pre-flight failed: %s", exc)
        return 1

    try:
        execute_plan(api, plan)
    except RuntimeError as exc:
        log.error("Execution stopped: %s", exc)
        return 2

    log.info("All %d planned operations succeeded. Running verification.", len(plan))
    try:
        report = verify_table(api, yaml_data)
    except RuntimeError as exc:
        log.error("Verification failed: %s", exc)
        return 3

    clean = print_report(report)
    return 0 if clean else 4


if __name__ == "__main__":
    sys.exit(main())
