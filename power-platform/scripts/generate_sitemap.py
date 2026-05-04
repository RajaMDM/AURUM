"""
generate_sitemap.py — Phase 3 prep — generate AURUM Steward Workbench sitemap artifacts.

Produces three artifacts from a single in-script SITEMAP definition (single
source of truth, same pattern as load_sample_data.py's lineage doc generator):

  1. dataverse/sitemap/aurum_steward_workbench_sitemap.xml
     Technically-valid SiteMap XML per Microsoft's documented schema. Can be
     pasted into the classic site map designer's XML view (Switch to classic
     in modern app designer → Sitemap → ⋯ → XML view). Reference artifact.

  2. docs/phase3_sitemap_walkthrough.md
     PRIMARY DELIVERABLE — step-by-step manual maker UI walkthrough for the
     modern app designer at execution time. Tabular: parent → child name →
     icon → target type → target reference, plus per-step time estimates.

  3. docs/phase3_views_specification.md
     System view definitions per table — view name, plain-English filter,
     sort order, columns, FetchXML snippet. NOT importable (views are
     created in maker UI per-table); this is the spec you work through.

Why no solution-package generation: building a customizations.xml + solution.xml
+ .zip that imports cleanly requires referencing views and dashboards that
don't exist in env yet (Phase 3 hasn't created them). The failure modes (publisher
prefix mismatch, missing component references, schema-version drift) are hard to
test locally before import. The walkthrough doc is the safer Phase 3 path.
Solution-package generation becomes feasible at Phase 5+ when all referenced
components exist and we can round-trip an export to seed the template.

References (cited in module docstring per project rule):
  - SiteMap schema (XSD reference):
    https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/customize-dev/sitemap-schema
  - SiteMap entity:
    https://learn.microsoft.com/power-apps/developer/data-platform/reference/entities/sitemap
  - Modern app designer:
    https://learn.microsoft.com/power-apps/maker/model-driven-apps/create-edit-app
  - Distribute via solution (the path we deferred):
    https://learn.microsoft.com/power-apps/maker/model-driven-apps/distribute-model-driven-app

Usage:
    python scripts/generate_sitemap.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET

log = logging.getLogger("aurum_pp.generate_sitemap")

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP_OUT = REPO_ROOT / "dataverse" / "sitemap" / "aurum_steward_workbench_sitemap.xml"
WALKTHROUGH_OUT = REPO_ROOT / "docs" / "phase3_sitemap_walkthrough.md"
VIEWS_OUT = REPO_ROOT / "docs" / "phase3_views_specification.md"
FORMS_OUT = REPO_ROOT / "docs" / "phase3_forms_specification.md"


# ---------------------------------------------------------------------------
# Sitemap data definition (single source of truth)
# ---------------------------------------------------------------------------

@dataclass
class SubArea:
    id: str
    title_plain: str            # always-safe ASCII title
    title_with_icon: str        # title with emoji prefix (best-effort)
    sub_type: str               # "Entity" | "Dashboard" | "URL"
    entity: str | None = None   # logical name when sub_type == "Entity"
    note: str = ""              # walkthrough commentary (e.g. cross-table caveat)


@dataclass
class Group:
    id: str
    title_plain: str
    title_with_icon: str
    aurum_stage: str            # ASSAY | UNEARTH | REFINE | UNFURL | (Dashboards has no stage)
    description: str
    subareas: list[SubArea] = field(default_factory=list)


@dataclass
class Sitemap:
    app_name: str
    area_id: str
    area_title: str
    groups: list[Group]


SITEMAP = Sitemap(
    app_name="AURUM Steward Workbench",
    area_id="Area_AurumWorkbench",
    area_title="AURUM Steward Workbench",
    groups=[
        Group(
            id="Group_ASSAY",
            title_plain="ASSAY (Profiling)",
            title_with_icon="📥 ASSAY (Profiling)",
            aurum_stage="ASSAY",
            description="Data quality findings + column-level profiling statistics. Surfaces nulls, format anomalies, and sample values per source field.",
            subareas=[
                SubArea(
                    id="SubArea_Assay_Findings",
                    title_plain="Data Quality Findings",
                    title_with_icon="Data Quality Findings",
                    sub_type="Entity",
                    entity="aurum_assay_profile",
                    note="Default view: 'Active Profile Findings' (create per views_specification.md, then mark as default in entity's Public Views).",
                ),
            ],
        ),
        Group(
            id="Group_UNEARTH",
            title_plain="UNEARTH (Staging)",
            title_with_icon="🔍 UNEARTH (Staging)",
            aurum_stage="UNEARTH",
            description="Raw staging records as-ingested per source system. Pre-normalization, pre-matching.",
            subareas=[
                SubArea(
                    id="SubArea_Unearth_CRM",
                    title_plain="CRM Records",
                    title_with_icon="CRM Records",
                    sub_type="Entity",
                    entity="aurum_crm_customer",
                ),
                SubArea(
                    id="SubArea_Unearth_ECOMM",
                    title_plain="E-commerce Records",
                    title_with_icon="E-commerce Records",
                    sub_type="Entity",
                    entity="aurum_ecomm_customer",
                ),
                SubArea(
                    id="SubArea_Unearth_LOYALTY",
                    title_plain="Loyalty Records",
                    title_with_icon="Loyalty Records",
                    sub_type="Entity",
                    entity="aurum_loyalty_customer",
                ),
            ],
        ),
        Group(
            id="Group_REFINE",
            title_plain="REFINE (Matching)",
            title_with_icon="⚖️ REFINE (Matching)",
            aurum_stage="REFINE",
            description="Match outcomes — borderline, auto-approved, unmatched. Cross-table virtual views are NOT a native model-driven app concept (acknowledged Phase 7 hero-page work); each subarea points to one staging table by default.",
            subareas=[
                SubArea(
                    id="SubArea_Refine_PendingReview",
                    title_plain="Pending Steward Review",
                    title_with_icon="Pending Steward Review",
                    sub_type="Entity",
                    entity="aurum_crm_customer",
                    note="Cross-table limitation — points to CRM by default. Create 'Pending Steward Review' view on all 3 staging tables (filter: aurum_processing_status = 4 / STEWARD_REVIEW). Steward navigates between sources via left-nav after selecting this entry. Phase 7 hero-page work will replace this with a unified canvas-app page.",
                ),
                SubArea(
                    id="SubArea_Refine_AutoApproved",
                    title_plain="Auto-Approved Matches",
                    title_with_icon="Auto-Approved Matches",
                    sub_type="Entity",
                    entity="aurum_crm_customer",
                    note="Cross-table limitation — same as above. View filter: aurum_processing_status = 5 / SURVIVED AND aurum_match_method ∈ {EXACT, FUZZY_HIGH}.",
                ),
                SubArea(
                    id="SubArea_Refine_Unmatched",
                    title_plain="Unmatched Records",
                    title_with_icon="Unmatched Records",
                    sub_type="Entity",
                    entity="aurum_crm_customer",
                    note="Cross-table limitation — same as above. View filter: aurum_match_method = 5 / UNMATCHED OR aurum_canonical_customer = null.",
                ),
            ],
        ),
        Group(
            id="Group_UNFURL",
            title_plain="UNFURL (Canonical)",
            title_with_icon="🌟 UNFURL (Canonical)",
            aurum_stage="UNFURL",
            description="Canonical / golden customer records — the survivorship-resolved single view. Surfaces trust score, completeness, source provenance.",
            subareas=[
                SubArea(
                    id="SubArea_Unfurl_Customer",
                    title_plain="Customer Master",
                    title_with_icon="Customer Master",
                    sub_type="Entity",
                    entity="aurum_customer",
                    note="Default view: 'Active Golden Records' (filter: aurum_is_golden = true; create per views_specification.md, mark as default in entity's Public Views).",
                ),
            ],
        ),
        Group(
            id="Group_Dashboards",
            title_plain="Dashboards",
            title_with_icon="📊 Dashboards",
            aurum_stage="(none)",
            description="Operational dashboard surfaces. MARK stage intentionally absent — no lineage table exists yet (Power Automate audit trail comes Phase 4). Adding an empty MARK node now would look broken.",
            subareas=[
                SubArea(
                    id="SubArea_Dashboard_Operations",
                    title_plain="AURUM-PP Operations Dashboard",
                    title_with_icon="AURUM-PP Operations Dashboard",
                    sub_type="Dashboard",
                    note="Dashboard does not exist yet at sitemap-build time. Two options at execution: (a) create a placeholder system dashboard first then bind this SubArea to it, OR (b) skip this SubArea until Phase 6's dashboard work and add it then. Option (b) recommended — empty dashboards look worse than a missing nav entry.",
                ),
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Views specification (per-entity system views to create in maker UI)
# ---------------------------------------------------------------------------

@dataclass
class ViewSpec:
    entity: str
    view_name: str
    purpose: str
    filter_plain_english: str
    fetch_xml_filter: str
    sort_order: str
    columns: list[str]
    is_default_recommendation: bool = False


# Picklist value source-of-truth: load_sample_data.py classes
#   AssaySeverity (lines 213-216): OK=1, WARNING=2, CRITICAL=3
#   ProcessingStatus (lines 166-172): LOADED=1, PROFILED=2, MATCHED=3, SURVIVED=4, STEWARD_REVIEW=5, REJECTED=6
#   MatchMethod (lines 157-163): EXACT=1, FUZZY_HIGH=2, FUZZY_BORDERLINE=3, STEWARD_APPROVED=4, UNMATCHED=5, SINGLE_SOURCE_PROMOTION=6
# Verify against source before changing — see feedback_spec_enum_source_of_truth.md memory.

VIEWS = [
    ViewSpec(
        entity="aurum_assay_profile",
        view_name="Active Profile Findings",
        purpose="ASSAY group default — surface critical+warning data-quality findings only, hide OK rows.",
        filter_plain_english="aurum_severity in (Warning=2, Critical=3) — exclude OK-severity (=1) rows from the default view.",
        fetch_xml_filter="<filter type='and'><condition attribute='aurum_severity' operator='in'><value>2</value><value>3</value></condition></filter>",
        sort_order="aurum_severity DESC (Critical=3 first, Warning=2 second), then aurum_null_pct DESC",
        columns=["aurum_field_name", "aurum_source_table", "aurum_severity", "aurum_null_pct", "aurum_format_anomaly_pct", "aurum_run_timestamp"],
        is_default_recommendation=True,
    ),
    ViewSpec(
        entity="aurum_customer",
        view_name="Active Golden Records",
        purpose="UNFURL group default — show only golden (survivorship-approved) canonicals.",
        filter_plain_english="aurum_is_golden = true",
        fetch_xml_filter="<filter type='and'><condition attribute='aurum_is_golden' operator='eq' value='1'/></filter>",
        sort_order="aurum_trust_score DESC, then aurum_full_name ASC",
        columns=["aurum_full_name", "aurum_email_primary", "aurum_phone_primary", "aurum_city", "aurum_country", "aurum_trust_score", "aurum_source_systems", "aurum_last_refined_date"],
        is_default_recommendation=True,
    ),
    ViewSpec(
        entity="aurum_crm_customer",
        view_name="Pending Steward Review",
        purpose="REFINE group — borderline matches needing human judgment. Same view name on ECOMM/LOYALTY (build 3x — see REFINE replication notes).",
        filter_plain_english="aurum_processing_status = 5 (STEWARD_REVIEW)",
        fetch_xml_filter="<filter type='and'><condition attribute='aurum_processing_status' operator='eq' value='5'/></filter>",
        sort_order="aurum_match_confidence DESC (highest-confidence borderlines first)",
        columns=["aurum_first_name_raw", "aurum_last_name_raw", "aurum_email_raw", "aurum_phone_raw", "aurum_match_confidence", "aurum_match_method", "aurum_loaded_date"],
    ),
    ViewSpec(
        entity="aurum_crm_customer",
        view_name="Auto-Approved Matches",
        purpose="REFINE group — high-confidence auto-survived records. Same view name on ECOMM/LOYALTY (build 3x — see REFINE replication notes).",
        filter_plain_english="aurum_processing_status = 4 (SURVIVED) AND aurum_match_method in (EXACT=1, FUZZY_HIGH=2)",
        fetch_xml_filter="<filter type='and'><condition attribute='aurum_processing_status' operator='eq' value='4'/><condition attribute='aurum_match_method' operator='in'><value>1</value><value>2</value></condition></filter>",
        sort_order="aurum_loaded_date DESC",
        columns=["aurum_first_name_raw", "aurum_last_name_raw", "aurum_email_raw", "aurum_match_confidence", "aurum_match_method", "aurum_canonical_customer", "aurum_loaded_date"],
    ),
    ViewSpec(
        entity="aurum_crm_customer",
        view_name="Unmatched Records",
        purpose="REFINE group — prospects/orphans, no canonical link. Same view name on ECOMM/LOYALTY (build 3x — see REFINE replication notes; LOYALTY also surfaces SINGLE_SOURCE_PROMOTION=6 records via the OR-null clause, which is intended).",
        filter_plain_english="aurum_match_method = 5 (UNMATCHED) OR aurum_canonical_customer is null",
        fetch_xml_filter="<filter type='or'><condition attribute='aurum_match_method' operator='eq' value='5'/><condition attribute='aurum_canonical_customer' operator='null'/></filter>",
        sort_order="aurum_loaded_date DESC",
        columns=["aurum_first_name_raw", "aurum_last_name_raw", "aurum_email_raw", "aurum_phone_raw", "aurum_match_method", "aurum_loaded_date"],
    ),
]


# REFINE views replicate to ECOMM (1:1 column mapping — schemas align) and to
# LOYALTY (column substitutions required — LOYALTY uses _parsed suffix because
# it ingests "LAST, FIRST"-format legacy names; design decision documented in
# project_aurum_pp_design_decisions.md memory).
REFINE_REPLICATION_NOTES = {
    "aurum_ecomm_customer": {
        "summary": "1:1 column mapping with CRM. All columns in CRM REFINE views exist with identical names on ECOMM. Use save-as-and-modify in maker UI's view editor: change Entity to aurum_ecomm_customer, no column substitutions needed.",
        "substitutions": {},
    },
    "aurum_loyalty_customer": {
        "summary": "Schema differs — LOYALTY uses _parsed suffix on name fields (ingests 'LAST, FIRST' legacy format). Substitute the columns below when copying CRM REFINE views to LOYALTY. Optionally ADD aurum_full_name_legacy as an extra column for steward visibility into the original legacy string.",
        "substitutions": {
            "aurum_first_name_raw": "aurum_first_name_parsed",
            "aurum_last_name_raw": "aurum_last_name_parsed",
        },
    },
}


# ---------------------------------------------------------------------------
# Forms specification (per-entity main-form layouts)
# ---------------------------------------------------------------------------

@dataclass
class FormField:
    column: str                 # actual env logical name (verified against env_column_manifest)
    note: str = ""              # optional field-level commentary


@dataclass
class FormRow:
    columns: int                # 1, 2, or 3 — fields rendered side-by-side
    fields: list[FormField]
    label: str = ""             # optional row label (e.g., "Name parts" for the 3-col first/middle/last row)


@dataclass
class FormTab:
    name: str
    purpose: str                # one-line tab description shown to maker
    rows: list[FormRow]


@dataclass
class FormSpec:
    entity: str
    purpose: str                # one-line form description
    tabs: list[FormTab]


# Spec → env name reconciliation. The user's verbal spec used informal names
# (e.g., aurum_email, aurum_trust_completeness). These are mapped to actual env
# logical names below and the divergences are surfaced in the rendered doc's
# "Spec-to-env name reconciliation" section.
SPEC_TO_ENV_NAME_MAP = {
    "aurum_email": "aurum_email_primary",
    "aurum_phone": "aurum_phone_primary",
    "aurum_trust_completeness": "aurum_completeness_score",
    "aurum_trust_diversity": "aurum_diversity_score",
    "aurum_address_line_1_raw": "aurum_address_line1_raw",  # underscore typo in user spec
    "aurum_anomaly_pct": "(no env column — see ASSAY form note)",
    "aurum_length_min": "aurum_min_length",
    "aurum_length_max": "aurum_max_length",
}


FORMS = [
    FormSpec(
        entity="aurum_customer",
        purpose="Canonical / golden customer record. UNFURL-stage primary form. 4 tabs separating identity, address, trust scoring, and lineage.",
        tabs=[
            FormTab(name="Identity", purpose="Who this person is — primary identifiers, name parts, contact, household link.", rows=[
                FormRow(columns=1, label="Display name", fields=[FormField(column="aurum_full_name", note="Top of form, prominent. Survivorship-resolved display name.")]),
                FormRow(columns=3, label="Name parts", fields=[
                    FormField(column="aurum_first_name"),
                    FormField(column="aurum_middle_name", note="Decision B — SHOWN on canonical form even when empty. Empty values accepted (most demo records have no middle name)."),
                    FormField(column="aurum_last_name"),
                ]),
                FormRow(columns=2, label="Primary contact", fields=[
                    FormField(column="aurum_email_primary", note="User-spec name 'aurum_email' → env logical name 'aurum_email_primary'."),
                    FormField(column="aurum_phone_primary", note="User-spec name 'aurum_phone' → env logical name 'aurum_phone_primary'."),
                ]),
                FormRow(columns=1, fields=[FormField(column="aurum_household_head", note="Self-referential lookup to another aurum_customer. Phase 4+ household-grouping concept; can be left null in Phase 3.")]),
            ]),
            FormTab(name="Address", purpose="Survivorship-resolved primary address.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_address_line1")]),
                FormRow(columns=2, fields=[FormField(column="aurum_city"), FormField(column="aurum_postal_code")]),
                FormRow(columns=1, fields=[FormField(column="aurum_country")]),
            ]),
            FormTab(name="Trust Score", purpose="Survivorship trust signals + golden-record toggle. Read-mostly fields populated by REFINE.", rows=[
                FormRow(columns=3, label="Score components", fields=[
                    FormField(column="aurum_completeness_score", note="User-spec 'aurum_trust_completeness' → env 'aurum_completeness_score'."),
                    FormField(column="aurum_diversity_score", note="User-spec 'aurum_trust_diversity' → env 'aurum_diversity_score'."),
                    FormField(column="aurum_trust_score", note="Composite: 0.6 × completeness + 0.4 × diversity."),
                ]),
                FormRow(columns=1, fields=[FormField(column="aurum_is_golden", note="Prominent toggle. Drives the 'Active Golden Records' default view's filter.")]),
            ]),
            FormTab(name="Lineage", purpose="Provenance + steward review state. Surfaces which sources contributed and when records were last touched.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_source_systems", note="Pipe-separated list, e.g., 'CRM|ECOMM|LOYALTY'.")]),
                FormRow(columns=2, fields=[FormField(column="aurum_first_seen_date"), FormField(column="aurum_last_refined_date")]),
                FormRow(columns=1, fields=[FormField(column="aurum_steward_review_status", note="Picklist: AUTO_APPROVED=1, PENDING=2, APPROVED=3, REJECTED=4, MERGED=5.")]),
            ]),
        ],
    ),
    FormSpec(
        entity="aurum_crm_customer",
        purpose="CRM staging record — UNEARTH stage. 3 tabs: raw source data, CRM-specific business attributes, match/review outcome.",
        tabs=[
            FormTab(name="Source Data (Raw)", purpose="As-ingested fields from CRM source system. Pre-normalization.", rows=[
                FormRow(columns=2, fields=[FormField(column="aurum_first_name_raw"), FormField(column="aurum_last_name_raw")]),
                FormRow(columns=2, fields=[FormField(column="aurum_email_raw"), FormField(column="aurum_phone_raw")]),
                FormRow(columns=3, fields=[FormField(column="aurum_address_line1_raw"), FormField(column="aurum_city_raw"), FormField(column="aurum_country_raw")]),
            ]),
            FormTab(name="CRM-Specific", purpose="Business attributes only meaningful in CRM context (segment, LTV, acquisition, last touch).", rows=[
                FormRow(columns=2, fields=[FormField(column="aurum_crm_source_id"), FormField(column="aurum_crm_segment")]),
                FormRow(columns=2, fields=[FormField(column="aurum_crm_lifetime_value"), FormField(column="aurum_crm_acquisition_channel")]),
                FormRow(columns=1, fields=[FormField(column="aurum_crm_last_interaction_date")]),
            ]),
            FormTab(name="Match & Review", purpose="REFINE-stage outputs — link to canonical, match scoring, processing state.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_canonical_customer", note="Hero field — Lookup to aurum_customer. Null = unmatched/orphan.")]),
                FormRow(columns=2, fields=[FormField(column="aurum_match_method"), FormField(column="aurum_match_confidence")]),
                FormRow(columns=1, fields=[FormField(column="aurum_processing_status", note="Prominent. Picklist: LOADED=1, PROFILED=2, MATCHED=3, SURVIVED=4, STEWARD_REVIEW=5, REJECTED=6.")]),
                FormRow(columns=1, fields=[FormField(column="aurum_loaded_date")]),
            ]),
        ],
    ),
    FormSpec(
        entity="aurum_ecomm_customer",
        purpose="E-commerce staging record — UNEARTH stage. Mirrors CRM's 3-tab structure with ECOMM-specific business attributes (orders, spend, shipping).",
        tabs=[
            FormTab(name="Source Data (Raw)", purpose="As-ingested fields from ECOMM platform. Note: shipping address is on this entity (vs CRM's billing-style address).", rows=[
                FormRow(columns=2, fields=[FormField(column="aurum_first_name_raw"), FormField(column="aurum_last_name_raw")]),
                FormRow(columns=2, fields=[FormField(column="aurum_email_raw", note="ECOMM primary name (Quirk 8)."), FormField(column="aurum_phone_raw")]),
                FormRow(columns=1, fields=[FormField(column="aurum_default_shipping_line1")]),
                FormRow(columns=3, fields=[FormField(column="aurum_default_shipping_city"), FormField(column="aurum_default_shipping_postal"), FormField(column="aurum_default_shipping_country")]),
            ]),
            FormTab(name="ECOMM-Specific", purpose="Order behavior — totals, spend, first/last order dates.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_ecomm_source_id")]),
                FormRow(columns=2, fields=[FormField(column="aurum_ecomm_total_orders"), FormField(column="aurum_ecomm_total_spend")]),
                FormRow(columns=2, fields=[FormField(column="aurum_ecomm_first_order_date"), FormField(column="aurum_ecomm_last_order_date")]),
            ]),
            FormTab(name="Match & Review", purpose="Identical structure to CRM Match & Review tab.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_canonical_customer", note="Hero field.")]),
                FormRow(columns=2, fields=[FormField(column="aurum_match_method"), FormField(column="aurum_match_confidence")]),
                FormRow(columns=1, fields=[FormField(column="aurum_processing_status", note="Prominent. Same picklist values as CRM.")]),
                FormRow(columns=1, fields=[FormField(column="aurum_loaded_date")]),
            ]),
        ],
    ),
    FormSpec(
        entity="aurum_loyalty_customer",
        purpose="Loyalty staging record — UNEARTH stage. 3 tabs: legacy + parsed names, loyalty-program attributes, match/review.",
        tabs=[
            FormTab(name="Source Data (Raw)", purpose="LOYALTY ingests 'LAST, FIRST' legacy format → parsed into _parsed name fields. Show legacy + parsed side-by-side so steward sees the parser's output.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_full_name_legacy", note="Original 'LAST, FIRST' string from legacy loyalty system.")]),
                FormRow(columns=3, label="Parsed name parts", fields=[
                    FormField(column="aurum_first_name_parsed"),
                    FormField(column="aurum_middle_name_parsed"),
                    FormField(column="aurum_last_name_parsed"),
                ]),
                FormRow(columns=2, fields=[FormField(column="aurum_email_raw"), FormField(column="aurum_phone_raw")]),
                FormRow(columns=3, fields=[FormField(column="aurum_address_line1_raw"), FormField(column="aurum_city_raw"), FormField(column="aurum_country_raw")]),
            ]),
            FormTab(name="LOYALTY-Specific", purpose="Loyalty program attributes — member number, tier, points, tenure.", rows=[
                FormRow(columns=2, fields=[FormField(column="aurum_loyalty_member_number", note="LOYALTY primary name."), FormField(column="aurum_loyalty_tier")]),
                FormRow(columns=2, fields=[FormField(column="aurum_loyalty_points_balance"), FormField(column="aurum_loyalty_member_since")]),
                FormRow(columns=1, fields=[FormField(column="aurum_birth_year")]),
                FormRow(columns=1, fields=[FormField(column="aurum_household_head_member_number", note="Future-feature column — household grouping by member number. Phase 4+ scope.")]),
            ]),
            FormTab(name="Match & Review", purpose="Same structure as CRM/ECOMM. Reminder: LOYALTY's MatchMethod includes a unique value SINGLE_SOURCE_PROMOTION=6 not present in CRM/ECOMM.", rows=[
                FormRow(columns=1, fields=[FormField(column="aurum_canonical_customer", note="Hero field. Often null on LOYALTY due to single-source-promotion records.")]),
                FormRow(columns=2, fields=[FormField(column="aurum_match_method", note="Includes SINGLE_SOURCE_PROMOTION=6 in addition to the standard 5 values."), FormField(column="aurum_match_confidence")]),
                FormRow(columns=1, fields=[FormField(column="aurum_processing_status", note="Prominent.")]),
                FormRow(columns=1, fields=[FormField(column="aurum_loaded_date")]),
            ]),
        ],
    ),
    FormSpec(
        entity="aurum_assay_profile",
        purpose="Data-quality finding — ASSAY stage. Single-tab compact layout for steward triage.",
        tabs=[
            FormTab(name="Profile Finding", purpose="What field, in what source, with what severity. Plus the supporting statistics + sample values.", rows=[
                FormRow(columns=2, label="Field identification", fields=[FormField(column="aurum_field_name", note="Prominent."), FormField(column="aurum_source_table", note="Prominent. Picklist: CRM_STAGING=1, ECOMM_STAGING=2, LOYALTY_STAGING=3, CUSTOMER_GOLDEN=4.")]),
                FormRow(columns=1, fields=[FormField(column="aurum_severity", note="Prominent. Picklist: OK=1, WARNING=2, CRITICAL=3.")]),
                FormRow(columns=2, fields=[FormField(column="aurum_inferred_type"), FormField(column="aurum_distinct_values")]),
                FormRow(columns=2, label="Quality percentages — env has only 2 of the 3 the spec listed", fields=[
                    FormField(column="aurum_null_pct"),
                    FormField(column="aurum_format_anomaly_pct", note="User-spec listed 3 percent fields (null_pct, anomaly_pct, format_anomaly_pct) but env only has 2 (aurum_null_pct, aurum_format_anomaly_pct). The spec's 'aurum_anomaly_pct' has no env column — likely user typo conflating with format_anomaly_pct. Rendering 2-column. Resolve at form-build time: confirm 2 is correct, OR deploy a separate aurum_anomaly_pct column first."),
                ]),
                FormRow(columns=2, fields=[FormField(column="aurum_min_length", note="User-spec 'aurum_length_min' → env 'aurum_min_length'."), FormField(column="aurum_max_length", note="User-spec 'aurum_length_max' → env 'aurum_max_length'.")]),
                FormRow(columns=3, label="Sample values", fields=[FormField(column="aurum_sample_value_1"), FormField(column="aurum_sample_value_2"), FormField(column="aurum_sample_value_3")]),
                FormRow(columns=2, label="Run metadata (small, bottom)", fields=[FormField(column="aurum_run_id"), FormField(column="aurum_run_timestamp")]),
            ]),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def render_sitemap_xml(sm: Sitemap) -> str:
    """Render technically-valid SiteMap XML per Microsoft's schema.
    Reference: https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/customize-dev/sitemap-schema
    """
    root = ET.Element("SiteMap")
    area = ET.SubElement(root, "Area", {
        "Id": sm.area_id,
        "ShowGroups": "true",
        "Title": sm.area_title,
    })
    for grp in sm.groups:
        group_el = ET.SubElement(area, "Group", {
            "Id": grp.id,
            "Title": grp.title_with_icon,
        })
        for sa in grp.subareas:
            attrs = {"Id": sa.id, "Title": sa.title_with_icon}
            if sa.sub_type == "Entity" and sa.entity:
                attrs["Entity"] = sa.entity
            ET.SubElement(group_el, "SubArea", attrs)
    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def render_walkthrough(sm: Sitemap) -> str:
    """Render the manual-maker-UI walkthrough doc (PRIMARY deliverable)."""
    L: list[str] = []
    L.append("# Phase 3 — Sitemap walkthrough (AURUM Steward Workbench)")
    L.append("")
    L.append("**Auto-generated by `scripts/generate_sitemap.py`. Do NOT hand-edit — edit the SITEMAP definition in the script and re-run.**")
    L.append("")
    L.append("Step-by-step build of the AURUM Steward Workbench model-driven app sitemap, manually in the Power Apps maker UI's modern app designer. Total estimated time: **20–25 minutes** (1 area + 5 groups + 9 subareas + emoji-render verification).")
    L.append("")
    L.append("## Pre-flight (before opening maker UI)")
    L.append("")
    L.append("1. Confirm the 5 tables exist in env via `python scripts/verify_env_columns.py` (re-runs in ~3 sec, sanity-check). Manifest in `docs/env_column_manifest_<DATE>.md`.")
    L.append("2. The 5 system views referenced from sitemap subareas (Pending Steward Review × 3, Active Profile Findings, Active Golden Records) do NOT need to exist before sitemap build — entity-type SubAreas land on the entity's *current default view*, then steward picks from view dropdown. Views are built per `phase3_views_specification.md` either before or after sitemap (independent work).")
    L.append("3. Have your Dataverse env open: maker.powerapps.com → AURUM-PP-Dev environment → Solutions → AURUM Master Data Management.")
    L.append("")
    L.append("## Step 1 — Create the model-driven app shell (3 min)")
    L.append("")
    L.append("1. Solutions → AURUM Master Data Management → **+ New** → **App** → **Model-driven app**.")
    L.append(f"2. Name: **{sm.app_name}**. Description: \"AURUM 5-stage pipeline UI — ASSAY profiling, UNEARTH staging, REFINE matching, UNFURL canonical, plus dashboards. MARK stage absent until Phase 4.\"")
    L.append("3. Click **Create**. Modern app designer opens.")
    L.append("")
    L.append("📸 **Screenshot to capture:** the empty modern app designer with the app name in the title bar.")
    L.append("")
    L.append("## Step 2 — Build the sitemap (15 min)")
    L.append("")
    L.append(f"In the modern app designer, the left **Pages** pane is your sitemap. The user's design has 1 area (\"{sm.area_title}\") containing 5 groups, totaling 9 subareas. Build them in the order below.")
    L.append("")
    L.append("> **Emoji-rendering check** — the modern app designer accepts emoji in titles, but rendering varies by browser/OS at runtime. After completing the sitemap, **Play** the app and verify emoji render correctly. If they don't, edit each Group title back to its plain-text version per the `Plain-text fallback` column.")
    L.append("")
    L.append("### Build order")
    L.append("")
    L.append("| # | Parent | Action | Title (with icon) | Plain-text fallback | Type | Target | Time |")
    L.append("|---:|---|---|---|---|---|---|---:|")
    step = 1
    L.append(f"| {step} | (root) | Add Area | `{sm.area_title}` | `{sm.area_title}` | Area | (n/a) | 1 min |")
    step += 1
    for grp in sm.groups:
        L.append(f"| {step} | `{sm.area_title}` | Add Group | `{grp.title_with_icon}` | `{grp.title_plain}` | Group | (n/a) | 1 min |")
        step += 1
        for sa in grp.subareas:
            target = f"Entity: `{sa.entity}`" if sa.sub_type == "Entity" else (f"Dashboard: (TBD)" if sa.sub_type == "Dashboard" else "URL: (TBD)")
            L.append(f"| {step} | `{grp.title_with_icon}` | Add SubArea | `{sa.title_with_icon}` | `{sa.title_plain}` | {sa.sub_type} | {target} | 1 min |")
            step += 1
    L.append("")
    L.append("### Per-group context (use this when prompting the maker designer for descriptions)")
    L.append("")
    for grp in sm.groups:
        L.append(f"#### {grp.title_with_icon}")
        L.append("")
        L.append(f"- **AURUM stage:** {grp.aurum_stage}")
        L.append(f"- **Description:** {grp.description}")
        L.append("")
        for sa in grp.subareas:
            L.append(f"  - **{sa.title_with_icon}** — {sa.sub_type}" + (f" (`{sa.entity}`)" if sa.entity else ""))
            if sa.note:
                L.append(f"    - *Note:* {sa.note}")
        L.append("")
    L.append("## Step 3 — Save and Play (2 min)")
    L.append("")
    L.append("1. Click **Save** (top-right). Wait for save confirmation.")
    L.append("2. Click **Play**. App opens in a new tab.")
    L.append("3. Verify all 5 groups render in left nav, all 9 subareas are clickable, navigation between groups works.")
    L.append("4. **Emoji-rendering check** — confirm `📥 🔍 ⚖️ 🌟 📊` render correctly. If broken/missing/garbled, return to designer, edit each Group title back to its plain-text fallback.")
    L.append("")
    L.append("📸 **Screenshot to capture:** the live app's left navigation pane showing all 5 stage groups (with whichever icon style ended up rendering).")
    L.append("")
    L.append("## Step 4 — Publish (1 min)")
    L.append("")
    L.append("1. Back in app designer, click **Publish**. Wait for confirmation.")
    L.append("2. Share the app: top-right **Share** → assign **System Customizer** + your user. Phase 4 will add proper steward security roles.")
    L.append("")
    L.append("## Known limitations (acknowledge upfront)")
    L.append("")
    L.append("1. **Cross-table views** — REFINE's three subareas (Pending Steward Review, Auto-Approved Matches, Unmatched Records) each point to ONE table (`aurum_crm_customer` by default). Steward navigates between CRM/ECOMM/LOYALTY via left-nav after selecting the REFINE entry. NOT IDEAL but acceptable for Phase 3. Phase 7 hero-page work replaces this with a unified canvas-app page.")
    L.append("2. **MARK stage absent** — no lineage table exists; MARK shows up as Power Automate audit trail in Phase 4. Adding an empty MARK node now would look broken.")
    L.append("3. **Operations Dashboard subarea is a placeholder** — recommend skipping until Phase 6 builds the dashboard. An empty dashboard looks worse than a missing nav entry.")
    L.append("")
    L.append(f"## Reference artifact: `dataverse/sitemap/aurum_steward_workbench_sitemap.xml`")
    L.append("")
    L.append("Technically-valid SiteMap XML generated alongside this walkthrough. NOT directly importable in modern maker UI (no standalone-XML import path exists), but usable in the classic site map designer's XML view (modern designer → ⋯ → Switch to classic → Sitemap → ⋯ → XML view → paste). Kept as a structured reference + future-import-path artifact (when we generate solution `.zip` packages in Phase 5+).")
    L.append("")
    return "\n".join(L) + "\n"


def render_views_spec() -> str:
    """Render the per-view system-view specification doc."""
    L: list[str] = []
    L.append("# Phase 3 — System views specification (per table)")
    L.append("")
    L.append("**Auto-generated by `scripts/generate_sitemap.py`. Do NOT hand-edit — edit VIEWS in the script and re-run.**")
    L.append("")
    L.append("System view definitions referenced from the sitemap subareas in `phase3_sitemap_walkthrough.md`. Views are NOT importable as a unit in modern maker UI (each view is created in the table's Views section); this doc is the spec you work through per-table.")
    L.append("")
    L.append("**REFINE-stage caveat:** the three REFINE views (Pending Steward Review, Auto-Approved Matches, Unmatched Records) are listed once below using `aurum_crm_customer` columns, but **must be created on all 3 staging tables** (CRM + ECOMM + LOYALTY). The sitemap's REFINE subareas point to CRM by default (see walkthrough's known-limitations section).")
    L.append("")
    L.append("**Picklist value source-of-truth (verified against `load_sample_data.py` enum classes 2026-05-03):**")
    L.append("- `aurum_severity`: OK=1, WARNING=2, CRITICAL=3")
    L.append("- `aurum_processing_status`: LOADED=1, PROFILED=2, MATCHED=3, **SURVIVED=4**, **STEWARD_REVIEW=5**, REJECTED=6")
    L.append("- `aurum_match_method`: EXACT=1, FUZZY_HIGH=2, FUZZY_BORDERLINE=3, STEWARD_APPROVED=4, UNMATCHED=5, SINGLE_SOURCE_PROMOTION=6 (LOYALTY only)")
    L.append("")
    by_entity: dict[str, list[ViewSpec]] = {}
    for v in VIEWS:
        by_entity.setdefault(v.entity, []).append(v)
    for entity, vs in by_entity.items():
        L.append(f"## `{entity}`")
        L.append("")
        for v in vs:
            tag = " — **set as DEFAULT view**" if v.is_default_recommendation else ""
            L.append(f"### `{v.view_name}`{tag}")
            L.append("")
            L.append(f"**Purpose:** {v.purpose}")
            L.append("")
            L.append(f"**Filter (plain English):** {v.filter_plain_english}")
            L.append("")
            L.append("**FetchXML filter snippet:**")
            L.append("")
            L.append("```xml")
            L.append(v.fetch_xml_filter)
            L.append("```")
            L.append("")
            L.append(f"**Sort order:** {v.sort_order}")
            L.append("")
            L.append("**Columns to display (in order):**")
            for c in v.columns:
                L.append(f"- `{c}`")
            L.append("")
    L.append("## REFINE replication notes (CRM → ECOMM, CRM → LOYALTY)")
    L.append("")
    L.append("The 3 REFINE views above are spec'd against `aurum_crm_customer`. Build them on CRM first, then replicate to ECOMM and LOYALTY using maker UI's save-as flow. Per-target replication notes:")
    L.append("")
    for target_entity, info in REFINE_REPLICATION_NOTES.items():
        L.append(f"### `{target_entity}`")
        L.append("")
        L.append(info["summary"])
        L.append("")
        if info["substitutions"]:
            L.append("**Column substitutions:**")
            L.append("")
            L.append("| CRM column (in spec) | Substitute with on this entity |")
            L.append("|---|---|")
            for src, dst in info["substitutions"].items():
                L.append(f"| `{src}` | `{dst}` |")
            L.append("")
    L.append("## Estimated time")
    L.append("")
    L.append(f"- {len(VIEWS)} unique view definitions × ~3 min each in maker UI Views editor = **~{len(VIEWS) * 3} min**")
    L.append("- REFINE views (3 unique) × replicate to ECOMM (1:1, no substitution) + LOYALTY (with substitution) = +6 views × ~3 min = **+18 min**")
    L.append("- **Total: ~33 minutes** for full views buildout.")
    L.append("")
    return "\n".join(L) + "\n"


def render_forms_spec() -> str:
    """Render the per-entity main-form layout specification doc."""
    L: list[str] = []
    L.append("# Phase 3 — Forms specification (per table)")
    L.append("")
    L.append("**Auto-generated by `scripts/generate_sitemap.py`. Do NOT hand-edit — edit FORMS in the script and re-run.**")
    L.append("")
    L.append("Main-form layouts for the 5 AURUM-PP tables, structured as tabs → rows (1/2/3-column) → fields. Use these as the spec when configuring each entity's Main form in the maker UI form designer.")
    L.append("")
    L.append("**All column names verified against env (per `docs/env_column_manifest_2026-05-03.md`).** Where the user's verbal pre-Phase-3 spec used informal names, the divergence is reconciled below.")
    L.append("")
    L.append("## Spec-to-env name reconciliation")
    L.append("")
    L.append("The pre-Phase-3 verbal spec used informal column names. Mapping to actual env logical names:")
    L.append("")
    L.append("| User-spec name | Actual env logical name | Notes |")
    L.append("|---|---|---|")
    for spec_name, env_name in SPEC_TO_ENV_NAME_MAP.items():
        note = ""
        if "no env column" in env_name:
            note = "⚠️ flagged in form section below"
        elif "address_line_1" in spec_name:
            note = "underscore typo in verbal spec"
        L.append(f"| `{spec_name}` | `{env_name}` | {note} |")
    L.append("")
    L.append("## Picklist value source-of-truth")
    L.append("")
    L.append("Verified against `load_sample_data.py` enum classes 2026-05-03 — same values used in `phase3_views_specification.md`:")
    L.append("- `aurum_severity`: OK=1, WARNING=2, CRITICAL=3")
    L.append("- `aurum_processing_status`: LOADED=1, PROFILED=2, MATCHED=3, SURVIVED=4, STEWARD_REVIEW=5, REJECTED=6")
    L.append("- `aurum_match_method`: EXACT=1, FUZZY_HIGH=2, FUZZY_BORDERLINE=3, STEWARD_APPROVED=4, UNMATCHED=5, SINGLE_SOURCE_PROMOTION=6 (LOYALTY only)")
    L.append("- `aurum_crm_segment`: BASIC=1, STANDARD=2, PREMIUM=3, VIP=4")
    L.append("- `aurum_loyalty_tier`: BRONZE=1, SILVER=2, GOLD=3, PLATINUM=4")
    L.append("- `aurum_steward_review_status`: AUTO_APPROVED=1, PENDING=2, APPROVED=3, REJECTED=4, MERGED=5")
    L.append("- `aurum_source_table`: CRM_STAGING=1, ECOMM_STAGING=2, LOYALTY_STAGING=3, CUSTOMER_GOLDEN=4")
    L.append("- `aurum_inferred_type`: TEXT=1, EMAIL=2, PHONE=3, DATE=4, NUMERIC=5, EMPTY=6")
    L.append("")
    for fs in FORMS:
        L.append(f"## `{fs.entity}` — Main form")
        L.append("")
        L.append(f"**Purpose:** {fs.purpose}")
        L.append("")
        L.append(f"**Tab count:** {len(fs.tabs)}")
        L.append("")
        for tab in fs.tabs:
            L.append(f"### Tab: `{tab.name}`")
            L.append("")
            L.append(f"_{tab.purpose}_")
            L.append("")
            L.append("| Row | Layout | Field(s) | Field-level notes |")
            L.append("|---:|---|---|---|")
            for i, row in enumerate(tab.rows, start=1):
                col_label = f"{row.columns}-col"
                if row.label:
                    col_label = f"{row.columns}-col ({row.label})"
                fields_md = " · ".join(f"`{f.column}`" for f in row.fields)
                notes = "; ".join(f.note for f in row.fields if f.note)
                L.append(f"| {i} | {col_label} | {fields_md} | {notes} |")
            L.append("")
    L.append("## Estimated time")
    L.append("")
    L.append(f"- 5 main forms × average ~6 min per form (tab creation, field placement, save+publish) = **~30 minutes**")
    L.append("- Add ~5 min for the canonical (aurum_customer) 4-tab form vs the simpler ASSAY 1-tab form. Realistic total: **~30–35 minutes** for full forms buildout.")
    L.append("")
    L.append("## Build order recommendation")
    L.append("")
    L.append("1. **`aurum_assay_profile`** first (1 tab, simplest, validates the row/column workflow in the form designer)")
    L.append("2. **`aurum_crm_customer`** (3 tabs, template for ECOMM and LOYALTY)")
    L.append("3. **`aurum_ecomm_customer`** (clone CRM's Match & Review tab via copy-paste in form designer if available, otherwise rebuild)")
    L.append("4. **`aurum_loyalty_customer`** (clone CRM's Match & Review tab; Source Data tab is meaningfully different — uses _parsed name fields)")
    L.append("5. **`aurum_customer`** last (4 tabs, most complex; benefits from form-designer muscle memory built on the others)")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    SITEMAP_OUT.write_text(render_sitemap_xml(SITEMAP), encoding="utf-8")
    log.info("SiteMap XML written: %s", SITEMAP_OUT.relative_to(REPO_ROOT))

    WALKTHROUGH_OUT.write_text(render_walkthrough(SITEMAP), encoding="utf-8")
    log.info("Walkthrough doc written: %s", WALKTHROUGH_OUT.relative_to(REPO_ROOT))

    VIEWS_OUT.write_text(render_views_spec(), encoding="utf-8")
    log.info("Views spec written: %s", VIEWS_OUT.relative_to(REPO_ROOT))

    FORMS_OUT.write_text(render_forms_spec(), encoding="utf-8")
    log.info("Forms spec written: %s", FORMS_OUT.relative_to(REPO_ROOT))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
