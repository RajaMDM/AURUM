"""
load_sample_data.py — Generate and insert AURUM-PP demo sample data.

Reads YAML schemas under dataverse/schemas/ implicitly (knowledge encoded in
the demo-record builders below — see project_aurum_pp_dataverse_quirks.md
Quirk 10 for why we don't blindly trust YAMLs as source-of-truth without
env verification).

Generates ~97 fictional records across all 5 AURUM-PP tables, structured to
demonstrate the AURUM public repo's five-stage architecture
(ASSAY → UNEARTH → REFINE → UNFURL → MARK). Five hand-coded demo-story
patterns drive the narrative; deterministic-seeded filler records hit the
volume targets without polluting the demo.

On every invocation (dry-run or real), regenerates docs/demo_records_aurum_lineage.md
from in-script demo-record metadata — that markdown file is the on-demand demo
script and Medium-post raw material.

Usage:
    # dry-run — print plan summary, regenerate lineage doc, no writes
    python scripts/load_sample_data.py --dry-run

    # real run — insert all records (canonicals first, then stagings with
    # @odata.bind lookups), write manifest, regenerate lineage doc
    python scripts/load_sample_data.py

    # destructive: clear today's previously-inserted records before inserting
    python scripts/load_sample_data.py --force-clear

Required env vars (set in ~/.zprofile, same pair as deploy_table.py):
    AURUM_PP_DATAVERSE_URL          e.g. https://<env-host>.crm.dynamics.com/
    AURUM_PP_SOLUTION_UNIQUE_NAME   target solution unique name

Auth uses scripts/auth.py — silent token from cache, falls back to
device-code only if cache expired.

IP rule: every name, address, email, business name in this script is fictional.
The only allowed real brand reference is "Verdant Apparel" (the demo brand,
itself fictional). See project_aurum_pp.md and feedback_aurum_pp_tenant_redaction.md.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auth import get_token  # noqa: E402

# ---------------------------------------------------------------------------
# Public AURUM repo dependency — AURUM-PP's whole thesis is "the public AURUM
# reference architecture instantiated on Power Platform." Importing the matcher
# directly is the mechanical proof. Vendoring would break the proof. If AURUM
# updates its matcher signature, this import breaks loudly — drift surfaces as
# an actionable error instead of accumulating silently.
# ---------------------------------------------------------------------------

AURUM_REPO_PATH = Path.home() / "Projects" / "AURUM"
sys.path.insert(0, str(AURUM_REPO_PATH))
try:
    from refine.matching.matcher import (  # noqa: E402
        score_pair as _aurum_score_pair,
        MATCH_THRESHOLD as AURUM_MATCH_THRESHOLD,
        NAME_BOOST_MULTIPLIER as AURUM_NAME_BOOST_MULTIPLIER,
    )
except ImportError as _exc:
    sys.stderr.write(
        f"\nERROR: cannot import the public AURUM matcher from {AURUM_REPO_PATH}.\n"
        f"  Underlying error: {_exc}\n"
        f"  AURUM-PP requires the public AURUM repo cloned at this path.\n"
        f"  Fix: git clone https://github.com/RajaMDM/AURUM ~/Projects/AURUM\n"
        f"       (and pip install pandas rapidfuzz jellyfish in the AURUM-PP venv)\n\n"
    )
    sys.exit(2)


def _aurum_commit_hash() -> str:
    """Capture AURUM repo's HEAD commit for lineage-doc citation. 'unknown' if not a git checkout."""
    try:
        result = subprocess.run(
            ["git", "-C", str(AURUM_REPO_PATH), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


AURUM_COMMIT_HASH = _aurum_commit_hash()


# ---------------------------------------------------------------------------
# Required env vars (mirror deploy_table.py)
# ---------------------------------------------------------------------------

ENV_DATAVERSE_URL = "AURUM_PP_DATAVERSE_URL"
ENV_SOLUTION_NAME = "AURUM_PP_SOLUTION_UNIQUE_NAME"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LANG_CODE = 1033
SEED = 42  # deterministic dry-run; change only if you want different filler

TODAY = datetime.now(timezone.utc)
TODAY_DATE_STR = TODAY.date().isoformat()
TODAY_ISO_TS = TODAY.isoformat(timespec="seconds").replace("+00:00", "Z")
RUN_ID = str(uuid.uuid4())

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
LINEAGE_DOC = DOCS_DIR / "demo_records_aurum_lineage.md"
MANIFEST_PATH = REPO_ROOT / "scripts" / f"sample_data_manifest_{TODAY.strftime('%Y%m%d')}.json"

# AURUM stage labels
STAGE_ASSAY = "ASSAY"
STAGE_UNEARTH = "UNEARTH"
STAGE_REFINE = "REFINE"
STAGE_UNFURL = "UNFURL"
STAGE_MARK = "MARK"

# Calculated fields to NEVER POST (per Quirk 3 — Dataverse computes them).
# `aurum_full_name` on aurum_customer was DECLARED calc in YAML but DEPLOYED as
# plain String (per Quirk 10), so it IS posted explicitly — not in this set.
CALC_FIELDS_TO_SKIP: set[tuple[str, str]] = {
    ("aurum_crm_customer", "aurum_full_name_display"),
}

# Entity set names (Dataverse pluralizes by appending "s"). Verified at
# script startup against the env via WebAPI.lookup_entity_sets().
DEFAULT_ENTITY_SETS: dict[str, str] = {
    "aurum_customer": "aurum_customers",
    "aurum_crm_customer": "aurum_crm_customers",
    "aurum_ecomm_customer": "aurum_ecomm_customers",
    "aurum_loyalty_customer": "aurum_loyalty_customers",
    "aurum_assay_profile": "aurum_assay_profiles",
}

# ---------------------------------------------------------------------------
# OptionSet value constants (mirror deployed env)
# ---------------------------------------------------------------------------


class MatchMethod:
    EXACT = 1
    FUZZY_HIGH = 2
    FUZZY_BORDERLINE = 3
    STEWARD_APPROVED = 4
    UNMATCHED = 5
    SINGLE_SOURCE_PROMOTION = 6  # LOYALTY only (value 6 not in CRM/ECOMM)


class ProcessingStatus:
    LOADED = 1
    PROFILED = 2  # CRM/ECOMM label "Profiled"; LOYALTY label "Parsed (Names Extracted)"
    MATCHED = 3
    SURVIVED = 4
    STEWARD_REVIEW = 5
    REJECTED = 6


class CRMSegment:
    BASIC = 1
    STANDARD = 2
    PREMIUM = 3
    VIP = 4


class LoyaltyTier:
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4


class StewardReviewStatus:
    AUTO_APPROVED = 1
    PENDING = 2
    APPROVED = 3
    REJECTED = 4
    MERGED = 5


class AssaySourceTable:
    CRM_STAGING = 1
    ECOMM_STAGING = 2
    LOYALTY_STAGING = 3
    CUSTOMER_GOLDEN = 4


class AssayInferredType:
    TEXT = 1
    EMAIL = 2
    PHONE = 3
    DATE = 4
    NUMERIC = 5
    EMPTY = 6


class AssaySeverity:
    OK = 1
    WARNING = 2
    CRITICAL = 3


# ---------------------------------------------------------------------------
# Cultural name pools — diverse mix appropriate for Dubai/UAE retail + global B2B.
# All names FICTIONAL per IP rule.
# ---------------------------------------------------------------------------

INDIAN_FIRST = [
    "Arjun", "Kavya", "Rohan", "Anjali", "Vikram", "Divya", "Karan", "Meera",
    "Aditya", "Shreya", "Nikhil", "Pooja", "Rahul", "Tara",
]
INDIAN_LAST = [
    "Patel", "Singh", "Sharma", "Reddy", "Iyer", "Menon", "Mehta", "Kapoor",
    "Gupta", "Nair", "Desai", "Joshi", "Rao", "Bhatt",
]

ARAB_FIRST = [
    "Ahmed", "Layla", "Khalid", "Fatima", "Hassan", "Noor", "Omar", "Mariam",
    "Yusuf", "Salma", "Ali", "Zahra", "Faisal", "Rana",
]
ARAB_LAST = [
    "Al-Maktoum", "Al-Sayed", "Bin Ahmed", "Al-Hassan", "Al-Khalifa",
    "Al-Shamsi", "Al-Mansoori", "Bin Saeed", "Al-Hashimi", "Al-Qassimi",
    "Al-Suwaidi", "Bin Rashid", "Al-Falasi", "Al-Naqbi",
]

FILIPINO_FIRST = [
    "Maria", "Jose", "Joana", "Carlos", "Christine", "Mark", "Andrea",
    "Daniel", "Patricia", "Ramon", "Angela", "Vincent", "Catherine", "Joel", "Grace",
]
FILIPINO_LAST = [
    "Reyes", "Cruz", "Garcia", "Santos", "Bautista", "Mendoza", "Castillo",
    "Ramos", "Domingo", "Aquino", "Villanueva", "Santiago", "Pascual", "Lim", "Tan",
]

EUROPEAN_FIRST = [
    "Hans", "Greta", "Marco", "Sofia", "Lukas", "Elena", "Andreas", "Anna",
    "Pierre", "Marie", "Jens", "Julia", "Marek", "Petra", "Henrik",
]
EUROPEAN_LAST = [
    "Müller", "Schmidt", "Rossi", "Lopez", "Andersen", "Kowalski", "Petrov",
    "Hansen", "Bianchi", "Schultz", "Novak", "Lindgren", "Romano", "Weber", "Olsen",
]

CHINESE_FIRST = [
    "Wei", "Mei", "Jin", "Lin", "Yu", "Hua", "Xin", "Min", "Ling", "Tao",
    "Bao", "Hong", "Jun", "Qi", "Bo",
]
CHINESE_LAST = [
    "Wang", "Li", "Zhang", "Liu", "Wong", "Yang", "Huang", "Zhao", "Wu",
    "Zhou", "Sun", "Ma", "Zhu", "Hu",
]

CULTURE_POOLS: list[tuple[str, list[str], list[str]]] = [
    ("Indian", INDIAN_FIRST, INDIAN_LAST),
    ("Arab", ARAB_FIRST, ARAB_LAST),
    ("Filipino", FILIPINO_FIRST, FILIPINO_LAST),
    ("European", EUROPEAN_FIRST, EUROPEAN_LAST),
    ("Chinese", CHINESE_FIRST, CHINESE_LAST),
]

# Reserved demo names — filler must avoid these to prevent accidental duplicate-Hero
RESERVED_NAMES: set[tuple[str, str]] = {
    ("Priya", "Krishnamurthy"),
    ("Mohammed", "Al-Rashid"),
    ("Sarah", "Chen"),
    ("Aisha", "Mubarak"),
}

# UAE neighborhoods — (line1_neighborhood, city, country, postal)
UAE_NEIGHBORHOODS = [
    ("Jumeirah 1", "Dubai", "United Arab Emirates", "12345"),
    ("Jumeirah 2", "Dubai", "United Arab Emirates", "12346"),
    ("Jumeirah 3", "Dubai", "United Arab Emirates", "12347"),
    ("Dubai Marina", "Dubai", "United Arab Emirates", "00000"),
    ("Downtown Dubai", "Dubai", "United Arab Emirates", "12000"),
    ("Al Barsha 1", "Dubai", "United Arab Emirates", "13001"),
    ("Al Barsha 2", "Dubai", "United Arab Emirates", "13002"),
    ("Business Bay", "Dubai", "United Arab Emirates", "12500"),
    ("Deira", "Dubai", "United Arab Emirates", "11000"),
    ("Discovery Gardens", "Dubai", "United Arab Emirates", "14000"),
    ("Al Wasl", "Dubai", "United Arab Emirates", "12100"),
    ("JLT", "Dubai", "United Arab Emirates", "14500"),
    ("Al Majaz", "Sharjah", "United Arab Emirates", "20000"),
    ("Al Khan", "Sharjah", "United Arab Emirates", "20100"),
    ("Khalifa City", "Abu Dhabi", "United Arab Emirates", "30000"),
    ("Al Reem Island", "Abu Dhabi", "United Arab Emirates", "30100"),
]

# Fictional B2B boutique names per IP rule. "Atlas Boutique LLC" appears in
# the demo-story spec; the rest are made up here.
B2B_BOUTIQUES = [
    "Atlas Boutique LLC",
    "Elysian Threads Trading",
    "Cipher Apparel House",
    "The Linen Atelier",
    "Heliconia Fashion Group",
    "Meridian Couture LLC",
    "Saffron & Silk Trading",
]

PERSONAL_EMAIL_DOMAINS = [
    "gmail.com", "outlook.com", "yahoo.com", "icloud.com", "hotmail.com",
]

# Loyalty tier raw values — varied casing demonstrates the standardize-on-REFINE pattern
LOYALTY_TIER_RAW = [
    "GOLD", "Gold", "gold", "PLATINUM", "Platinum",
    "SILVER", "Silver", "silver", "BRONZE", "Bronze",
]

UAE_MOBILE_PREFIXES = ["+971-50", "+971-52", "+971-54", "+971-55", "+971-56", "+971-58"]

CRM_ACQUISITION_CHANNELS = [
    "Trade Show 2024", "Trade Show 2025", "Referral", "Cold Outreach",
    "Industry Conference", "B2B Partnership", "Web Inquiry",
]

# Match-confidence pools per realism rule (never round numbers, except 1.00 for legit exact)
EXACT_MATCH_CONFIDENCE = 1.00
HIGH_CONFIDENCE_POOL = [0.83, 0.87, 0.89, 0.91, 0.92, 0.94]
BORDERLINE_CONFIDENCE_POOL = [0.55, 0.62, 0.64, 0.69, 0.71, 0.79]
UNMATCHED_CONFIDENCE = 0.0

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

log = logging.getLogger("aurum_pp.load_sample_data")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def get_required_env(name: str, hint: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(
            f"{name} env var not set.\n  Hint: {hint}\n  Set in ~/.zprofile, then source it."
        )
    return val


def get_dataverse_url() -> str:
    url = get_required_env(ENV_DATAVERSE_URL, "Dataverse env URL with trailing slash")
    return url if url.endswith("/") else url + "/"


def get_solution_name() -> str:
    return get_required_env(
        ENV_SOLUTION_NAME, "Target solution unique name (NOT display name)"
    )


# ---------------------------------------------------------------------------
# Web API client (record-level CRUD)
# ---------------------------------------------------------------------------


class WebAPI:
    """Record-level Web API client. Distinct from deploy_table.py's metadata-level client."""

    def __init__(self, base_url: str, token: str, solution_name: str) -> None:
        self.base = base_url + "api/data/v9.2/"
        self.token = token
        self.solution_name = solution_name
        # entity_logical_name → entity_set_name (e.g. aurum_customer → aurum_customers)
        # Populated by lookup_entity_sets() at startup; falls back to DEFAULT_ENTITY_SETS.
        self.entity_sets: dict[str, str] = dict(DEFAULT_ENTITY_SETS)

    def _headers(self, *, write: bool) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        if write:
            h["Content-Type"] = "application/json"
            # Records aren't solution-scoped; harmless but kept for header consistency
            # with deploy_table.py.
            h["MSCRM.SolutionUniqueName"] = self.solution_name
        return h

    def lookup_entity_sets(self) -> None:
        """Query each known entity's actual EntitySetName from EntityDefinitions.
        Avoids assuming Dataverse pluralized as 'name + s'."""
        for logical in DEFAULT_ENTITY_SETS:
            url = (
                self.base
                + f"EntityDefinitions(LogicalName='{logical}')?$select=EntitySetName"
            )
            resp = requests.get(url, headers=self._headers(write=False), timeout=30)
            if not resp.ok:
                raise RuntimeError(
                    f"Cannot resolve EntitySetName for {logical}: HTTP {resp.status_code}"
                )
            actual = resp.json().get("EntitySetName")
            if actual:
                self.entity_sets[logical] = actual

    def post_record(
        self, entity_logical: str, payload: dict[str, Any]
    ) -> tuple[str, str]:
        """POST a new record. Returns (record_guid, entity_id_url).

        entity_id_url comes from the OData-EntityId response header — Dataverse's
        canonical way of returning the new resource on record creates.
        """
        entity_set = self.entity_sets[entity_logical]
        url = self.base + entity_set
        log.debug("POST %s", url)
        resp = requests.post(
            url, headers=self._headers(write=True), json=payload, timeout=60
        )
        if not resp.ok:
            raise RuntimeError(
                f"POST {entity_set} failed: HTTP {resp.status_code} {resp.reason}\n"
                f"  body: {resp.text[:1000]}"
            )
        entity_id_url = resp.headers.get("OData-EntityId", "")
        guid = _extract_guid(entity_id_url)
        return guid, entity_id_url

    def query(self, entity_logical: str, params: str = "") -> list[dict[str, Any]]:
        entity_set = self.entity_sets[entity_logical]
        url = self.base + entity_set + ("?" + params if params else "")
        log.debug("GET %s", url)
        resp = requests.get(url, headers=self._headers(write=False), timeout=30)
        if not resp.ok:
            raise RuntimeError(
                f"GET {entity_set} failed: HTTP {resp.status_code} {resp.reason}\n"
                f"  body: {resp.text[:500]}"
            )
        return resp.json().get("value", [])

    def delete(self, entity_logical: str, record_id: str) -> None:
        entity_set = self.entity_sets[entity_logical]
        url = f"{self.base}{entity_set}({record_id})"
        log.debug("DELETE %s", url)
        resp = requests.delete(url, headers=self._headers(write=False), timeout=30)
        if not resp.ok and resp.status_code != 404:
            raise RuntimeError(
                f"DELETE {entity_set}({record_id}) failed: HTTP {resp.status_code} {resp.reason}"
            )


def _extract_guid(entity_id_url: str) -> str:
    """OData-EntityId is shaped like https://.../aurum_customers(<guid>) — pull the guid."""
    if not entity_id_url or "(" not in entity_id_url:
        raise ValueError(f"Cannot extract guid from entity_id_url: {entity_id_url!r}")
    return entity_id_url.split("(", 1)[1].rstrip(")")


# ---------------------------------------------------------------------------
# Realism helpers (deterministic — random.seed(SEED) called in main())
# ---------------------------------------------------------------------------


def random_culture_pool() -> tuple[str, list[str], list[str]]:
    return random.choice(CULTURE_POOLS)


def random_name(reserved: set[tuple[str, str]] = None) -> tuple[str, str, str]:
    """Returns (first_name, last_name, culture_label). Avoids reserved (first,last) pairs."""
    reserved = reserved or set()
    for _ in range(40):
        culture, firsts, lasts = random_culture_pool()
        first = random.choice(firsts)
        last = random.choice(lasts)
        if (first, last) not in reserved:
            return first, last, culture
    return first, last, culture  # bounded fallback (won't trigger in practice)


def random_email_normal(first: str, last: str) -> str:
    style = random.choice(["full", "initial", "nickname", "underscore"])
    domain = random.choice(PERSONAL_EMAIL_DOMAINS)
    f = first.lower()
    last_clean = last.lower().replace(" ", "").replace("-", "").replace(".", "")
    if style == "full":
        return f"{f}.{last_clean}@{domain}"
    if style == "initial":
        return f"{f[0]}{last_clean}@{domain}"
    if style == "nickname":
        return f"{f[:3]}.{last_clean[:4]}{random.randint(1, 99)}@{domain}"
    return f"{f}_{last_clean}@{domain}"


def random_email_malformed(first: str, last: str) -> str:
    """Intentionally malformed for ASSAY-finding demonstration."""
    style = random.choice(["no_at", "no_tld", "double_at"])
    f, l = first.lower(), last.lower()
    if style == "no_at":
        return f"{f}.{l}gmail.com"
    if style == "no_tld":
        return f"{f}.{l}@gmail"
    return f"{f}@{l}@gmail.com"


def random_email(first: str, last: str, *, malformed_chance: float = 0.0) -> str:
    if random.random() < malformed_chance:
        return random_email_malformed(first, last)
    return random_email_normal(first, last)


def random_uae_phone(*, malformed_chance: float = 0.0) -> str:
    if random.random() < malformed_chance:
        return random.choice(["050123", "+971-50-XXX", "0501234567890", "TBD"])
    prefix = random.choice(UAE_MOBILE_PREFIXES)
    return f"{prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_uae_address_tuple() -> tuple[str, str, str, str]:
    """Returns (line1, city, country, postal_code) as a single linked tuple."""
    neighborhood, city, country, postal = random.choice(UAE_NEIGHBORHOODS)
    unit_kind = random.choice(["Villa", "Apt", "Unit"])
    number = random.randint(1, 250)
    line1 = f"{unit_kind} {number}, {neighborhood}"
    return line1, city, country, postal


def random_match_confidence(category: str) -> float:
    if category == "exact":
        return EXACT_MATCH_CONFIDENCE
    if category == "high":
        return random.choice(HIGH_CONFIDENCE_POOL)
    if category == "borderline":
        return random.choice(BORDERLINE_CONFIDENCE_POOL)
    return UNMATCHED_CONFIDENCE


def random_loyalty_member_number() -> str:
    return f"VLP-{random.randint(100000, 999999)}"


def random_past_date_iso(min_days: int, max_days: int) -> str:
    days = random.randint(min_days, max_days)
    return (TODAY.date() - timedelta(days=days)).isoformat()


def remove_calc_fields(entity_logical: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        k: v
        for k, v in payload.items()
        if (entity_logical, k) not in CALC_FIELDS_TO_SKIP and v is not None
    }


# ---------------------------------------------------------------------------
# Demo record + story dataclasses
# ---------------------------------------------------------------------------


@dataclass
class DemoRecord:
    entity_logical: str
    payload: dict[str, Any]
    role_label: str
    links_to_canonical_role: str | None = None
    # Populated by _score_against_canonical for stagings paired with a canonical.
    # None means the record was not scored (canonical itself, or new prospect).
    matcher_outputs: dict[str, Any] | None = None


@dataclass
class DemoStory:
    pattern_name: str
    aurum_stages: list[str]
    narrative: str
    confidence_explanation: str
    records: list[DemoRecord] = field(default_factory=list)
    # Concept tags — orthogonal to aurum_stages. Stages name the pipeline stage(s)
    # the pattern lives in; concept_tags name the load-bearing mechanism or
    # architectural truth the pattern proves. Used for cross-pattern indexing in
    # the lineage doc and in any downstream Medium / portfolio reference.
    concept_tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Matcher adapter + helper (uses public AURUM matcher imported at top of file)
# ---------------------------------------------------------------------------


def _to_matcher_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Adapt an AURUM-PP record payload to the public matcher's expected shape
    (first_name, last_name, email, phone, source_id). Resolves field names that
    differ between canonical (aurum_first_name) and staging (raw / parsed)."""
    first = (
        payload.get("aurum_first_name")
        or payload.get("aurum_first_name_raw")
        or payload.get("aurum_first_name_parsed")
        or ""
    )
    last = (
        payload.get("aurum_last_name")
        or payload.get("aurum_last_name_raw")
        or payload.get("aurum_last_name_parsed")
        or ""
    )
    email = payload.get("aurum_email_primary") or payload.get("aurum_email_raw") or ""
    phone = payload.get("aurum_phone_primary") or payload.get("aurum_phone_raw") or ""
    source_id = (
        payload.get("aurum_crm_source_id")
        or payload.get("aurum_ecomm_source_id")
        or payload.get("aurum_loyalty_member_number")
        or ""
    )
    return {"first_name": first, "last_name": last, "email": email, "phone": phone, "source_id": source_id}


def _derive_match_method(
    composite: float, name_score: float, email_score: float, phone_score: float,
) -> int:
    """Map matcher composite + components to the staging table's match_method
    OptionSet:
      1 Exact-Match — exact email signal (or composite=1.00 with exact phone)
      2 Fuzzy-High-Confidence — composite >= 0.85 (boost or weighted)
      3 Fuzzy-Borderline — below 0.85 but candidate-eligible
    """
    if email_score == 1.0 or (composite >= 0.95 and phone_score == 1.0):
        return MatchMethod.EXACT
    if composite >= 0.85:
        return MatchMethod.FUZZY_HIGH
    return MatchMethod.FUZZY_BORDERLINE


def _score_against_canonical(canonical: DemoRecord, staging: DemoRecord) -> None:
    """Run the public AURUM matcher against this canonical+staging pair, then
    write authoritative confidence/method/status into the staging payload AND
    attach matcher_outputs (consumed by lineage-doc rendering)."""
    canon_rec = _to_matcher_record(canonical.payload)
    stage_rec = _to_matcher_record(staging.payload)
    result = _aurum_score_pair(canon_rec, stage_rec)
    composite = result.composite_score
    weighted = round(
        result.name_score * 0.65 + result.email_score * 0.25 + result.phone_score * 0.10, 4,
    )
    boost_floor = (
        round(result.name_score * AURUM_NAME_BOOST_MULTIPLIER, 4)
        if result.name_score >= 0.90 else 0.0
    )
    boost_active = boost_floor > weighted

    staging.matcher_outputs = {
        "name_score": result.name_score,
        "email_score": result.email_score,
        "phone_score": result.phone_score,
        "weighted": weighted,
        "name_boost_floor": boost_floor,
        "name_boost_active": boost_active,
        "composite": composite,
    }
    staging.payload["aurum_match_confidence"] = round(composite, 2)
    staging.payload["aurum_match_method"] = _derive_match_method(
        composite, result.name_score, result.email_score, result.phone_score,
    )
    staging.payload["aurum_processing_status"] = (
        ProcessingStatus.SURVIVED if composite >= AURUM_MATCH_THRESHOLD
        else ProcessingStatus.STEWARD_REVIEW
    )


# ---------------------------------------------------------------------------
# Demo-story builders (5) — confidence values authored by the matcher, NOT hand-tuned
# ---------------------------------------------------------------------------


def build_priya_hero() -> DemoStory:
    canonical = DemoRecord(
        entity_logical="aurum_customer",
        role_label="canonical",
        payload={
            "aurum_first_name": "Priya",
            "aurum_last_name": "Krishnamurthy",
            "aurum_full_name": "Priya Krishnamurthy",
            "aurum_email_primary": "priya.k@gmail.com",
            "aurum_phone_primary": "+971-50-555-1042",
            "aurum_address_line1": "Apt 1402, Dubai Marina",
            "aurum_city": "Dubai",
            "aurum_country": "United Arab Emirates",
            "aurum_postal_code": "00000",
            "aurum_birth_year": 1988,
            "aurum_nationality": "Indian",
            "aurum_loyalty_tier": LoyaltyTier.GOLD,
            "aurum_loyalty_points_balance": 18420,
            "aurum_loyalty_member_since": "2018-06-12",
            "aurum_loyalty_member_number": "VLP-100042",
            "aurum_crm_segment": CRMSegment.PREMIUM,
            "aurum_lifetime_value": 47800,
            "aurum_total_orders": 142,
            "aurum_trust_score": 0.94,
            "aurum_completeness_score": 1.00,
            "aurum_diversity_score": 1.00,
            "aurum_is_golden": True,
            "aurum_source_systems": "CRM|ECOMM|LOYALTY",
            "aurum_first_seen_date": "2018-06-12",
            "aurum_last_refined_date": TODAY_ISO_TS,
            "aurum_steward_review_status": StewardReviewStatus.APPROVED,
        },
    )
    crm_staging = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM staging",
        links_to_canonical_role="canonical",
        payload={
            "aurum_crm_source_id": "CRM-00042",
            "aurum_first_name_raw": "PRIYA",
            "aurum_last_name_raw": "KRISHNAMURTHY",
            "aurum_email_raw": "priya.krishnamurthy@verdantapparel.com",
            "aurum_phone_raw": "+971-50-555-1042",
            "aurum_address_line1_raw": "Apt 1402, Dubai Marina",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "Premium",
            "aurum_crm_lifetime_value": 47800,
            "aurum_crm_acquisition_channel": "B2B Partnership",
            "aurum_crm_last_interaction_date": "2026-04-28",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    ecomm_staging = DemoRecord(
        entity_logical="aurum_ecomm_customer",
        role_label="ECOMM staging",
        links_to_canonical_role="canonical",
        payload={
            "aurum_ecomm_source_id": "ECOMM-1042",
            "aurum_email_raw": "priya.k@gmail.com",
            "aurum_first_name_raw": "P.",
            "aurum_last_name_raw": "Krishnamurthy",
            "aurum_phone_raw": "+971-50-555-1042",
            "aurum_default_shipping_line1": "Apt 1402, Dubai Marina",
            "aurum_default_shipping_city": "Dubai",
            "aurum_default_shipping_country": "United Arab Emirates",
            "aurum_default_shipping_postal": "00000",
            "aurum_ecomm_total_orders": 87,
            "aurum_ecomm_total_spend": 22340,
            "aurum_ecomm_first_order_date": "2019-02-15",
            "aurum_ecomm_last_order_date": "2026-04-30",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    loyalty_staging = DemoRecord(
        entity_logical="aurum_loyalty_customer",
        role_label="LOYALTY staging",
        links_to_canonical_role="canonical",
        payload={
            "aurum_loyalty_member_number": "VLP-100042",
            "aurum_full_name_legacy": "KRISHNAMURTHY, PRIYA",
            "aurum_first_name_parsed": "Priya",
            "aurum_last_name_parsed": "Krishnamurthy",
            "aurum_email_raw": "priya.k@gmail.com",
            "aurum_phone_raw": "+971-50-555-1042",
            "aurum_address_line1_raw": "Apt 1402, Dubai Marina",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_birth_year": 1988,
            "aurum_loyalty_tier": "Gold",
            "aurum_loyalty_points_balance": 18420,
            "aurum_loyalty_member_since": "2018-06-12",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    _score_against_canonical(canonical, crm_staging)
    _score_against_canonical(canonical, ecomm_staging)
    _score_against_canonical(canonical, loyalty_staging)
    return DemoStory(
        pattern_name="Hero — Priya Krishnamurthy",
        aurum_stages=[STAGE_REFINE, STAGE_UNFURL],
        concept_tags=["#AURUM-InterStageDependency"],
        narrative=(
            "One real-world person observed across all 3 staging sources with subtle format "
            "differences: ALL CAPS in CRM legacy fields, abbreviated initial in ECOMM, "
            "comma-separated 'LAST, FIRST' format in LOYALTY's legacy column. ECOMM and "
            "LOYALTY land at high composite (0.89 and 1.00 respectively). However, "
            "**Priya CRM (legacy ALL CAPS) lands at composite=0.51, BELOW REFINE's "
            "candidate-filter floor (0.55).** Vanilla REFINE wouldn't surface this as a "
            "match candidate. The record is linked manually in this demo to illustrate "
            "the inter-stage dependency: REFINE depends on UNEARTH's case-folding "
            "normalization. ALL CAPS legacy data degrades match coverage until UNEARTH "
            "lifts it above the threshold. This is the pipeline argument made visible — "
            "five stages exist because each stage solves a problem the next depends on. "
            "Once UNEARTH normalizes Priya's CRM record to Title Case, REFINE matches all "
            "three to one canonical, and UNFURL surfaces 'Priya Krishnamurthy' consistently "
            "downstream regardless of which source originated each individual field."
        ),
        confidence_explanation=(
            "Per the public AURUM matcher: ECOMM produces a high composite (exact email "
            "match — priya.k@gmail.com verbatim in canonical and ECOMM). LOYALTY produces "
            "the maximum composite (parsed names + email + phone all align). CRM lands "
            "BELOW the 0.55 candidate filter because the ALL CAPS legacy data degrades "
            "the case-sensitive token-sort component of name_score. The matcher's behaviour "
            "is honest: without UNEARTH-stage normalization, this record would be invisible "
            "to vanilla REFINE — see the per-pair breakdown above for the actual numbers."
        ),
        records=[canonical, crm_staging, ecomm_staging, loyalty_staging],
    )


def build_mohammed_ambiguous() -> DemoStory:
    canonical = DemoRecord(
        entity_logical="aurum_customer",
        role_label="canonical",
        payload={
            "aurum_first_name": "Mohammed",
            "aurum_last_name": "Al-Rashid",
            "aurum_full_name": "Mohammed Al-Rashid",
            "aurum_email_primary": "m.alrashid@outlook.com",
            "aurum_phone_primary": "+971-50-444-7821",
            "aurum_address_line1": "Villa 78, Khalifa City",
            "aurum_city": "Abu Dhabi",
            "aurum_country": "United Arab Emirates",
            "aurum_postal_code": "30000",
            "aurum_birth_year": 1979,
            "aurum_nationality": "Emirati",
            "aurum_crm_segment": CRMSegment.STANDARD,
            "aurum_lifetime_value": 8200,
            "aurum_total_orders": 23,
            "aurum_trust_score": 0.71,
            "aurum_completeness_score": 0.83,
            "aurum_diversity_score": 0.50,
            "aurum_is_golden": True,
            "aurum_source_systems": "CRM",
            "aurum_first_seen_date": "2023-09-04",
            "aurum_last_refined_date": TODAY_ISO_TS,
            "aurum_steward_review_status": StewardReviewStatus.APPROVED,
        },
    )
    crm_staging_ambiguous = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM staging (ambiguous candidate, NOT linked)",
        links_to_canonical_role=None,
        payload={
            "aurum_crm_source_id": "CRM-00219",
            "aurum_first_name_raw": "M.",
            "aurum_last_name_raw": "Alrashid",
            "aurum_email_raw": "malrashid@gmail.com",
            "aurum_phone_raw": "+971-50-444-7821",
            "aurum_address_line1_raw": "Apt 12, Business Bay",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "Standard",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time (status is then
            # post-overridden to STEWARD_REVIEW below — see comment at override).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    # Score even though Mohammed staging will NOT be linked — the matcher
    # would still emit this composite, and the steward sees it before deciding.
    _score_against_canonical(canonical, crm_staging_ambiguous)
    # Override processing_status: even if composite happens to land above
    # MATCH_THRESHOLD, this record is the demo's "human must judge" case.
    crm_staging_ambiguous.payload["aurum_processing_status"] = ProcessingStatus.STEWARD_REVIEW
    return DemoStory(
        pattern_name="Ambiguous Match — Mohammed Al-Rashid vs M. Alrashid",
        aurum_stages=[STAGE_REFINE],
        narrative=(
            "Two records that look like the same person but might not be: canonical Mohammed "
            "Al-Rashid (Abu Dhabi, work email) and a CRM staging record for 'M. Alrashid' "
            "(Dubai, different email, no hyphen in surname). Same phone number — a strong "
            "signal — but different name spelling and different city. The composite computed "
            "by the AURUM matcher (see breakdown above) falls in the borderline band — above "
            "the candidate-filter floor of 0.55 but below the auto-match threshold of 0.65 — "
            "requiring a human steward to judge whether to merge or keep separate. The "
            "staging record stays unlinked (aurum_canonical_customer = null) until the "
            "steward decides."
        ),
        confidence_explanation=(
            "Per the public AURUM matcher: borderline-band composite. Strong phone match + "
            "name fuzz that lands well below the name-boost-floor threshold (0.90) + email "
            "mismatch combine to a weighted total below MATCH_THRESHOLD. See per-pair "
            "breakdown above for the actual scores."
        ),
        records=[canonical, crm_staging_ambiguous],
    )


def build_sarah_multibrand() -> DemoStory:
    canonical = DemoRecord(
        entity_logical="aurum_customer",
        role_label="canonical",
        payload={
            "aurum_first_name": "Sarah",
            "aurum_last_name": "Chen",
            "aurum_full_name": "Sarah Chen",
            "aurum_email_primary": "sarah.chen@atlasboutique.ae",
            "aurum_phone_primary": "+971-50-318-9921",
            "aurum_address_line1": "Atlas Boutique LLC, Unit 12, Al Wasl",
            "aurum_city": "Dubai",
            "aurum_country": "United Arab Emirates",
            "aurum_postal_code": "12100",
            "aurum_birth_year": 1985,
            "aurum_nationality": "Singaporean",
            "aurum_crm_segment": CRMSegment.VIP,
            "aurum_lifetime_value": 124500,
            "aurum_total_orders": 312,
            "aurum_trust_score": 0.83,
            "aurum_completeness_score": 0.83,
            "aurum_diversity_score": 0.67,
            "aurum_is_golden": True,
            "aurum_source_systems": "CRM|ECOMM",
            "aurum_first_seen_date": "2021-11-08",
            "aurum_last_refined_date": TODAY_ISO_TS,
            "aurum_steward_review_status": StewardReviewStatus.APPROVED,
        },
    )
    crm_b2b = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM staging (B2B context)",
        links_to_canonical_role="canonical",
        payload={
            "aurum_crm_source_id": "CRM-01077",
            "aurum_first_name_raw": "Sarah",
            "aurum_last_name_raw": "Chen",
            "aurum_email_raw": "sarah.chen@atlasboutique.ae",
            "aurum_phone_raw": "+971-50-318-9921",
            "aurum_address_line1_raw": "Atlas Boutique LLC, Unit 12, Al Wasl",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "VIP",
            "aurum_crm_lifetime_value": 98200,
            "aurum_crm_acquisition_channel": "Trade Show 2021",
            "aurum_crm_last_interaction_date": "2026-04-22",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    ecomm_consumer = DemoRecord(
        entity_logical="aurum_ecomm_customer",
        role_label="ECOMM staging (consumer context)",
        links_to_canonical_role="canonical",
        payload={
            "aurum_ecomm_source_id": "ECOMM-2031",
            "aurum_email_raw": "sarah.c.personal@gmail.com",
            "aurum_first_name_raw": "Sarah",
            "aurum_last_name_raw": "Chen",
            "aurum_phone_raw": "+971-50-318-9921",
            "aurum_default_shipping_line1": "Apt 504, Downtown Dubai",
            "aurum_default_shipping_city": "Dubai",
            "aurum_default_shipping_country": "United Arab Emirates",
            "aurum_default_shipping_postal": "12000",
            "aurum_ecomm_total_orders": 41,
            "aurum_ecomm_total_spend": 26300,
            "aurum_ecomm_first_order_date": "2022-03-14",
            "aurum_ecomm_last_order_date": "2026-04-29",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    _score_against_canonical(canonical, crm_b2b)
    _score_against_canonical(canonical, ecomm_consumer)
    return DemoStory(
        pattern_name="Multi-Brand — Sarah Chen (B2B buyer + consumer)",
        aurum_stages=[STAGE_REFINE],
        concept_tags=["#AURUM-NameBoostFloor"],
        narrative=(
            "One real person who appears in CRM as a B2B buyer for Atlas Boutique LLC "
            "(work email, work address, VIP segment) AND in ECOMM as a personal consumer "
            "(gmail address, home address). **Sarah CRM at composite=1.00** (all fields "
            "identical, exact match — auto-approved). **Sarah ECOMM at composite=0.85** "
            "(name and phone identical but email differs business→personal; weighted=0.79 "
            "below FUZZY_HIGH; name_boost_floor activates at name_score≥0.90, lifting "
            "composite to 0.85×1.00=0.85). Two records, one canonical, two match patterns. "
            "Demonstrates: (a) auto-approve on perfect-match B2B records, (b) "
            "name_boost_floor mechanism handling 'same person, different contact contexts' "
            "without manual steward intervention. The B2B-vs-consumer cross-segment "
            "narrative is still demonstrated, but now with the matcher's actual behavior "
            "driving it instead of hand-picked confidence values. Lifetime value on the "
            "canonical aggregates both contexts ($124,500 = $98,200 B2B + $26,300 consumer)."
        ),
        confidence_explanation=(
            "Per the public AURUM matcher: CRM at composite=1.00 (everything matches; "
            "weighted=1.00 wins over the boost floor of 0.85). ECOMM at composite=0.85 "
            "(weighted=0.79 because email mismatch zeroes the email term; the NAME-BOOST "
            "FLOOR — `floor = name_score × 0.85` when `name_score ≥ 0.90` — overrides at "
            "0.85). This is the textbook demonstration of the boost mechanism: without it, "
            "Sarah ECOMM would be classified Fuzzy-Borderline (0.79 < 0.85) and need "
            "steward review; with it, she's auto-approved Fuzzy-High. See per-pair "
            "breakdown above for the actual numbers."
        ),
        records=[canonical, crm_b2b, ecomm_consumer],
    )


def build_aisha_conflicting_sources() -> DemoStory:
    canonical = DemoRecord(
        entity_logical="aurum_customer",
        role_label="canonical",
        payload={
            "aurum_first_name": "Aisha",
            "aurum_last_name": "Mubarak",
            "aurum_full_name": "Aisha Mubarak",
            "aurum_email_primary": "aisha.mubarak@outlook.com",
            "aurum_phone_primary": "+971-55-227-3309",
            "aurum_address_line1": "Villa 23, Jumeirah 3",
            "aurum_city": "Dubai",
            "aurum_country": "United Arab Emirates",
            "aurum_postal_code": "12347",
            "aurum_birth_year": 1991,
            "aurum_nationality": "Emirati",
            "aurum_loyalty_tier": LoyaltyTier.PLATINUM,
            "aurum_loyalty_points_balance": 24800,
            "aurum_loyalty_member_since": "2017-03-20",
            "aurum_loyalty_member_number": "VLP-100023",
            "aurum_crm_segment": CRMSegment.PREMIUM,
            "aurum_lifetime_value": 31200,
            "aurum_total_orders": 78,
            "aurum_trust_score": 0.91,
            "aurum_completeness_score": 1.00,
            "aurum_diversity_score": 0.67,
            "aurum_is_golden": True,
            "aurum_source_systems": "CRM|LOYALTY",
            "aurum_first_seen_date": "2017-03-20",
            "aurum_last_refined_date": TODAY_ISO_TS,
            "aurum_steward_review_status": StewardReviewStatus.APPROVED,
        },
    )
    crm_staging = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM staging (address tuple A)",
        links_to_canonical_role="canonical",
        payload={
            "aurum_crm_source_id": "CRM-00501",
            "aurum_first_name_raw": "Aisha",
            "aurum_last_name_raw": "Mubarak",
            "aurum_email_raw": "aisha.mubarak@outlook.com",
            "aurum_phone_raw": "+971-55-227-3309",
            "aurum_address_line1_raw": "Villa 23, Jumeirah Beach Road",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "Premium",
            "aurum_crm_lifetime_value": 19400,
            "aurum_crm_acquisition_channel": "Referral",
            "aurum_crm_last_interaction_date": "2026-04-25",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    loyalty_staging = DemoRecord(
        entity_logical="aurum_loyalty_customer",
        role_label="LOYALTY staging (address tuple B)",
        links_to_canonical_role="canonical",
        payload={
            "aurum_loyalty_member_number": "VLP-100023",
            "aurum_full_name_legacy": "MUBARAK, AISHA",
            "aurum_first_name_parsed": "Aisha",
            "aurum_last_name_parsed": "Mubarak",
            "aurum_email_raw": "aisha.mubarak@outlook.com",
            "aurum_phone_raw": "+971-55-227-3309",
            "aurum_address_line1_raw": "Villa 23, Jumeirah",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_birth_year": 1991,
            "aurum_loyalty_tier": "PLATINUM",
            "aurum_loyalty_points_balance": 24800,
            "aurum_loyalty_member_since": "2017-03-20",
            # aurum_match_confidence, aurum_match_method, aurum_processing_status
            # are set by _score_against_canonical at build time — do NOT hardcode
            # here (Quirk 10 anti-pattern: stale literals that get overwritten).
            "aurum_loaded_date": TODAY_ISO_TS,
        },
    )
    _score_against_canonical(canonical, crm_staging)
    _score_against_canonical(canonical, loyalty_staging)
    return DemoStory(
        pattern_name="Conflicting Sources — Aisha Mubarak (linked-tuple address)",
        aurum_stages=[STAGE_UNFURL],
        narrative=(
            "Same person, same email, same phone — but the address fields diverge across "
            "sources: canonical says 'Villa 23, Jumeirah 3' (postcode 12347); CRM says "
            "'Villa 23, Jumeirah Beach Road'; LOYALTY says 'Villa 23, Jumeirah'. The AURUM "
            "matcher does NOT score addresses at all — addresses are pure UNFURL/"
            "survivorship concern, deliberately separated from REFINE matching. So both "
            "pairs match at the maximum composite the matcher can produce. The linked-tuple "
            "survivorship pattern (in UNFURL, not REFINE) says: address_line1 + city + "
            "country + postal_code MUST come from the same source record. Naive logic that "
            "picks 'best field by field' would produce an address tuple nobody actually "
            "lives at. UNFURL surfaces the canonical's address tuple as a unit; downstream "
            "consumers (shipping labels, marketing) get a coherent address."
        ),
        confidence_explanation=(
            "Per the public AURUM matcher: BOTH pairs produce maximum-composite scores. "
            "Name + email + phone all match exactly. The matcher has no notion of "
            "addresses — they're survivorship-stage concern, not matching-stage. This is "
            "the deliberate stage separation in the AURUM architecture: REFINE answers "
            "'are these the same entity?' using identity signals (name/email/phone). "
            "UNFURL answers 'which source's facts survive into the canonical?' using "
            "trust + linked-tuple rules. See per-pair breakdown above to confirm the "
            "matcher emits no address-related score components."
        ),
        records=[canonical, crm_staging, loyalty_staging],
    )


def build_new_prospect_cluster() -> DemoStory:
    p_crm_1 = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM prospect 1 (Hassan Bin Saeed)",
        payload={
            "aurum_crm_source_id": "CRM-09001",
            "aurum_first_name_raw": "Hassan",
            "aurum_last_name_raw": "Bin Saeed",
            "aurum_email_raw": "hassan.binsaeed@outlook.com",
            "aurum_phone_raw": "+971-50-712-4488",
            "aurum_address_line1_raw": "Villa 14, Al Reem Island",
            "aurum_city_raw": "Abu Dhabi",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "Standard",
            "aurum_match_confidence": UNMATCHED_CONFIDENCE,
            "aurum_match_method": MatchMethod.UNMATCHED,
            "aurum_loaded_date": TODAY_ISO_TS,
            "aurum_processing_status": ProcessingStatus.PROFILED,
        },
    )
    p_crm_2 = DemoRecord(
        entity_logical="aurum_crm_customer",
        role_label="CRM prospect 2 (Joana Reyes)",
        payload={
            "aurum_crm_source_id": "CRM-09002",
            "aurum_first_name_raw": "Joana",
            "aurum_last_name_raw": "Reyes",
            "aurum_email_raw": "joana.reyes@gmail.com",
            "aurum_phone_raw": "+971-56-301-7720",
            "aurum_address_line1_raw": "Apt 88, Al Barsha 2",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_crm_segment": "Basic",
            "aurum_match_confidence": UNMATCHED_CONFIDENCE,
            "aurum_match_method": MatchMethod.UNMATCHED,
            "aurum_loaded_date": TODAY_ISO_TS,
            "aurum_processing_status": ProcessingStatus.PROFILED,
        },
    )
    p_ecomm = DemoRecord(
        entity_logical="aurum_ecomm_customer",
        role_label="ECOMM prospect (Lukas Weber)",
        payload={
            "aurum_ecomm_source_id": "ECOMM-9001",
            "aurum_email_raw": "lukas.weber@yahoo.com",
            "aurum_first_name_raw": "Lukas",
            "aurum_last_name_raw": "Weber",
            "aurum_default_shipping_line1": "Apt 22, JLT",
            "aurum_default_shipping_city": "Dubai",
            "aurum_default_shipping_country": "United Arab Emirates",
            "aurum_default_shipping_postal": "14500",
            "aurum_ecomm_total_orders": 1,
            "aurum_ecomm_total_spend": 142,
            "aurum_ecomm_first_order_date": "2026-05-01",
            "aurum_match_confidence": UNMATCHED_CONFIDENCE,
            "aurum_match_method": MatchMethod.UNMATCHED,
            "aurum_loaded_date": TODAY_ISO_TS,
            "aurum_processing_status": ProcessingStatus.LOADED,
        },
    )
    p_loyalty = DemoRecord(
        entity_logical="aurum_loyalty_customer",
        role_label="LOYALTY prospect (Maria L Santos)",
        payload={
            "aurum_loyalty_member_number": "VLP-200001",
            "aurum_full_name_legacy": "SANTOS, MARIA L",
            "aurum_first_name_parsed": "Maria",
            "aurum_middle_name_parsed": "L",
            "aurum_last_name_parsed": "Santos",
            "aurum_phone_raw": "+971-50-118-2204",
            "aurum_address_line1_raw": "Apt 7, Deira",
            "aurum_city_raw": "Dubai",
            "aurum_country_raw": "United Arab Emirates",
            "aurum_birth_year": 1962,
            "aurum_loyalty_tier": "Bronze",
            "aurum_loyalty_member_since": "2024-08-12",
            "aurum_match_confidence": UNMATCHED_CONFIDENCE,
            "aurum_match_method": MatchMethod.SINGLE_SOURCE_PROMOTION,
            "aurum_loaded_date": TODAY_ISO_TS,
            "aurum_processing_status": ProcessingStatus.LOADED,
        },
    )
    return DemoStory(
        pattern_name="New Prospect cluster — 4 unmatched staging records",
        aurum_stages=[STAGE_UNEARTH, STAGE_MARK],
        narrative=(
            "Four staging records that REFINE could not match to any existing canonical "
            "(confidence 0.0, match_method = Unmatched). UNEARTH detects these as new "
            "entities — candidates to become canonical records once stewards approve. MARK "
            "preserves the lineage so when these are promoted to canonicals, the audit "
            "trail shows which staging source originated each one and on which date. The "
            "LOYALTY prospect uses match_method = Single-Source Promotion (LOYALTY-specific "
            "value 6) for stewards who want to promote a loyalty-only member without "
            "waiting for a second-source confirmation."
        ),
        confidence_explanation=(
            "All 4 at 0.0 confidence — no candidate canonical scored as a viable match. "
            "These are 'cold' new entities, not failed matches. REFINE's candidate-filter "
            "floor is 0.55 (per `find_candidates` in the public AURUM matcher); records "
            "where the best candidate scores below this aren't surfaced as match candidates "
            "and flow to UNEARTH for new-entity detection rather than to the steward review "
            "queue."
        ),
        records=[p_crm_1, p_crm_2, p_ecomm, p_loyalty],
    )


# ---------------------------------------------------------------------------
# Filler generators (volume-target padding, deterministic via seed)
# ---------------------------------------------------------------------------


def generate_filler_canonicals(count: int) -> list[dict[str, Any]]:
    """Generate `count` filler canonical payloads. Each will get linked by 1-2 staging filler records."""
    canonicals = []
    for i in range(count):
        first, last, nationality = random_name(reserved=RESERVED_NAMES)
        line1, city, country, postal = random_uae_address_tuple()
        has_loyalty = random.random() < 0.55
        has_crm = random.random() < 0.65
        sources = []
        if has_crm:
            sources.append("CRM")
        if random.random() < 0.55:
            sources.append("ECOMM")
        if has_loyalty:
            sources.append("LOYALTY")
        if not sources:
            sources = ["CRM"]
        diversity = round(min(len(sources) / 3.0, 1.0), 2)
        completeness = round(0.6 + random.random() * 0.4, 2)
        trust = round(0.6 * completeness + 0.4 * diversity, 2)
        payload = {
            "aurum_first_name": first,
            "aurum_last_name": last,
            "aurum_full_name": f"{first} {last}",
            "aurum_email_primary": random_email_normal(first, last),
            "aurum_phone_primary": random_uae_phone(),
            "aurum_address_line1": line1,
            "aurum_city": city,
            "aurum_country": country,
            "aurum_postal_code": postal,
            "aurum_birth_year": random.randint(1955, 2000),
            "aurum_nationality": nationality,
            "aurum_crm_segment": random.choice([CRMSegment.BASIC, CRMSegment.STANDARD,
                                                CRMSegment.PREMIUM, CRMSegment.VIP]) if has_crm else None,
            "aurum_lifetime_value": random.randint(500, 50000) if has_crm else None,
            "aurum_total_orders": random.randint(1, 200) if has_crm or "ECOMM" in sources else None,
            "aurum_loyalty_tier": random.choice([LoyaltyTier.BRONZE, LoyaltyTier.SILVER,
                                                 LoyaltyTier.GOLD, LoyaltyTier.PLATINUM]) if has_loyalty else None,
            "aurum_loyalty_points_balance": random.randint(100, 30000) if has_loyalty else None,
            "aurum_loyalty_member_since": random_past_date_iso(180, 2500) if has_loyalty else None,
            "aurum_loyalty_member_number": random_loyalty_member_number() if has_loyalty else None,
            "aurum_trust_score": trust,
            "aurum_completeness_score": completeness,
            "aurum_diversity_score": diversity,
            "aurum_is_golden": trust >= 0.6,
            "aurum_source_systems": "|".join(sources),
            "aurum_first_seen_date": random_past_date_iso(180, 2500),
            "aurum_last_refined_date": TODAY_ISO_TS,
            "aurum_steward_review_status": (
                StewardReviewStatus.AUTO_APPROVED if trust >= 0.85
                else StewardReviewStatus.APPROVED if trust >= 0.7
                else StewardReviewStatus.PENDING
            ),
        }
        canonicals.append({
            "payload": payload,
            "_filler_index": i,
            "_sources": sources,
            "_first": first,
            "_last": last,
        })
    return canonicals


def generate_filler_crm_staging(
    canonicals: list[dict[str, Any]], matched_count: int, prospect_count: int,
) -> list[dict[str, Any]]:
    """Generate filler CRM staging records.
    Matched records link back to a filler canonical by index;
    prospects have no canonical link.
    """
    records = []
    # Matched: pick canonicals whose _sources includes "CRM"
    crm_canonicals = [c for c in canonicals if "CRM" in c["_sources"]]
    random.shuffle(crm_canonicals)
    for i in range(matched_count):
        canon = crm_canonicals[i % len(crm_canonicals)]
        first, last = canon["_first"], canon["_last"]
        match_cat = random.choices(
            ["exact", "high", "borderline"], weights=[3, 5, 2], k=1
        )[0]
        confidence = random_match_confidence(match_cat)
        method = (
            MatchMethod.EXACT if match_cat == "exact"
            else MatchMethod.FUZZY_HIGH if match_cat == "high"
            else MatchMethod.FUZZY_BORDERLINE
        )
        line1, city, country, _ = random_uae_address_tuple()
        records.append({
            "payload": {
                "aurum_crm_source_id": f"CRM-{20000 + i:05d}",
                "aurum_first_name_raw": first.upper() if random.random() < 0.3 else first,
                "aurum_last_name_raw": last.upper() if random.random() < 0.3 else last,
                "aurum_email_raw": random_email(first, last, malformed_chance=0.05),
                "aurum_phone_raw": random_uae_phone(malformed_chance=0.08),
                "aurum_address_line1_raw": line1,
                "aurum_city_raw": city,
                "aurum_country_raw": country,
                "aurum_crm_segment": random.choice(["Basic", "Standard", "Premium", "VIP"]),
                "aurum_crm_lifetime_value": random.randint(500, 30000),
                "aurum_crm_acquisition_channel": random.choice(CRM_ACQUISITION_CHANNELS),
                "aurum_crm_last_interaction_date": random_past_date_iso(1, 365),
                "aurum_match_confidence": confidence,
                "aurum_match_method": method,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": (
                    ProcessingStatus.SURVIVED if confidence >= 0.80
                    else ProcessingStatus.STEWARD_REVIEW
                ),
            },
            "_links_canonical_index": canon["_filler_index"],
        })
    # Prospects: no canonical link
    for i in range(prospect_count):
        first, last, _ = random_name(reserved=RESERVED_NAMES)
        line1, city, country, _ = random_uae_address_tuple()
        records.append({
            "payload": {
                "aurum_crm_source_id": f"CRM-{30000 + i:05d}",
                "aurum_first_name_raw": first,
                "aurum_last_name_raw": last,
                "aurum_email_raw": random_email(first, last, malformed_chance=0.10),
                "aurum_phone_raw": random_uae_phone(malformed_chance=0.10),
                "aurum_address_line1_raw": line1,
                "aurum_city_raw": city,
                "aurum_country_raw": country,
                "aurum_crm_segment": random.choice(["Basic", "Standard"]),
                "aurum_crm_acquisition_channel": random.choice(CRM_ACQUISITION_CHANNELS),
                "aurum_match_confidence": UNMATCHED_CONFIDENCE,
                "aurum_match_method": MatchMethod.UNMATCHED,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": ProcessingStatus.PROFILED,
            },
            "_links_canonical_index": None,
        })
    return records


def generate_filler_ecomm_staging(
    canonicals: list[dict[str, Any]], matched_count: int, prospect_count: int,
) -> list[dict[str, Any]]:
    records = []
    ecomm_canonicals = [c for c in canonicals if "ECOMM" in c["_sources"]]
    random.shuffle(ecomm_canonicals)
    for i in range(matched_count):
        canon = ecomm_canonicals[i % len(ecomm_canonicals)] if ecomm_canonicals else random.choice(canonicals)
        first, last = canon["_first"], canon["_last"]
        match_cat = random.choices(["exact", "high", "borderline"], weights=[4, 4, 2], k=1)[0]
        confidence = random_match_confidence(match_cat)
        method = (
            MatchMethod.EXACT if match_cat == "exact"
            else MatchMethod.FUZZY_HIGH if match_cat == "high"
            else MatchMethod.FUZZY_BORDERLINE
        )
        line1, city, country, postal = random_uae_address_tuple()
        # ECOMM often has abbreviated names — initial + last
        first_raw = first if random.random() < 0.5 else f"{first[0]}."
        records.append({
            "payload": {
                "aurum_ecomm_source_id": f"ECOMM-{20000 + i:05d}",
                "aurum_email_raw": random_email_normal(first, last),  # required field
                "aurum_first_name_raw": first_raw,
                "aurum_last_name_raw": last,
                "aurum_phone_raw": random_uae_phone() if random.random() < 0.7 else None,
                "aurum_default_shipping_line1": line1,
                "aurum_default_shipping_city": city,
                "aurum_default_shipping_country": country,
                "aurum_default_shipping_postal": postal,
                "aurum_ecomm_total_orders": random.randint(1, 100),
                "aurum_ecomm_total_spend": random.randint(50, 25000),
                "aurum_ecomm_first_order_date": random_past_date_iso(30, 1500),
                "aurum_ecomm_last_order_date": random_past_date_iso(1, 60),
                "aurum_match_confidence": confidence,
                "aurum_match_method": method,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": (
                    ProcessingStatus.SURVIVED if confidence >= 0.80
                    else ProcessingStatus.STEWARD_REVIEW
                ),
            },
            "_links_canonical_index": canon["_filler_index"],
        })
    for i in range(prospect_count):
        first, last, _ = random_name(reserved=RESERVED_NAMES)
        line1, city, country, postal = random_uae_address_tuple()
        records.append({
            "payload": {
                "aurum_ecomm_source_id": f"ECOMM-{30000 + i:05d}",
                "aurum_email_raw": random_email_normal(first, last),
                "aurum_first_name_raw": first if random.random() < 0.5 else f"{first[0]}.",
                "aurum_last_name_raw": last,
                "aurum_default_shipping_line1": line1,
                "aurum_default_shipping_city": city,
                "aurum_default_shipping_country": country,
                "aurum_default_shipping_postal": postal,
                "aurum_ecomm_total_orders": random.randint(1, 5),
                "aurum_ecomm_total_spend": random.randint(50, 800),
                "aurum_ecomm_first_order_date": random_past_date_iso(1, 60),
                "aurum_match_confidence": UNMATCHED_CONFIDENCE,
                "aurum_match_method": MatchMethod.UNMATCHED,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": ProcessingStatus.LOADED,
            },
            "_links_canonical_index": None,
        })
    return records


def generate_filler_loyalty_staging(
    canonicals: list[dict[str, Any]], matched_count: int, prospect_count: int,
) -> list[dict[str, Any]]:
    records = []
    loyalty_canonicals = [c for c in canonicals if "LOYALTY" in c["_sources"]]
    random.shuffle(loyalty_canonicals)
    for i in range(matched_count):
        canon = loyalty_canonicals[i % len(loyalty_canonicals)] if loyalty_canonicals else random.choice(canonicals)
        first, last = canon["_first"], canon["_last"]
        legacy = f"{last.upper()}, {first.upper()}"
        match_cat = random.choices(["high", "borderline"], weights=[3, 2], k=1)[0]
        confidence = random_match_confidence(match_cat)
        method = MatchMethod.FUZZY_HIGH if match_cat == "high" else MatchMethod.FUZZY_BORDERLINE
        line1, city, country, _ = random_uae_address_tuple()
        records.append({
            "payload": {
                "aurum_loyalty_member_number": random_loyalty_member_number(),
                "aurum_full_name_legacy": legacy,
                "aurum_first_name_parsed": first,
                "aurum_last_name_parsed": last,
                "aurum_email_raw": random_email_normal(first, last) if random.random() < 0.7 else None,
                "aurum_phone_raw": random_uae_phone(),
                "aurum_address_line1_raw": line1,
                "aurum_city_raw": city,
                "aurum_country_raw": country,
                "aurum_birth_year": random.randint(1945, 2000),
                "aurum_loyalty_tier": random.choice(LOYALTY_TIER_RAW),
                "aurum_loyalty_points_balance": random.randint(100, 25000),
                "aurum_loyalty_member_since": random_past_date_iso(180, 3000),
                "aurum_match_confidence": confidence,
                "aurum_match_method": method,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": (
                    ProcessingStatus.SURVIVED if confidence >= 0.80
                    else ProcessingStatus.STEWARD_REVIEW
                ),
            },
            "_links_canonical_index": canon["_filler_index"],
        })
    for i in range(prospect_count):
        first, last, _ = random_name(reserved=RESERVED_NAMES)
        legacy = f"{last.upper()}, {first.upper()}"
        line1, city, country, _ = random_uae_address_tuple()
        records.append({
            "payload": {
                "aurum_loyalty_member_number": random_loyalty_member_number(),
                "aurum_full_name_legacy": legacy,
                "aurum_first_name_parsed": first,
                "aurum_last_name_parsed": last,
                "aurum_phone_raw": random_uae_phone(),
                "aurum_address_line1_raw": line1,
                "aurum_city_raw": city,
                "aurum_country_raw": country,
                "aurum_birth_year": random.randint(1945, 2000),
                "aurum_loyalty_tier": random.choice(LOYALTY_TIER_RAW),
                "aurum_loyalty_member_since": random_past_date_iso(60, 365),
                "aurum_match_confidence": UNMATCHED_CONFIDENCE,
                "aurum_match_method": MatchMethod.SINGLE_SOURCE_PROMOTION,
                "aurum_loaded_date": TODAY_ISO_TS,
                "aurum_processing_status": ProcessingStatus.LOADED,
            },
            "_links_canonical_index": None,
        })
    return records


def generate_assay_records(count: int) -> list[dict[str, Any]]:
    """8 assay records demonstrating realistic ASSAY findings.
    Severity distribution: 2 OK, 4 Warning, 2 Critical (8 total)."""
    findings = [
        # 2 Critical
        {
            "source": AssaySourceTable.CRM_STAGING,
            "field": "aurum_phone_raw",
            "null_pct": 17.3,
            "format_anomaly_pct": 0.0,
            "inferred": AssayInferredType.PHONE,
            "severity": AssaySeverity.CRITICAL,
            "samples": ["+971-50-555-1042", "0501234", None],
            "note": "Critical: 17.3% null rate on a primary contact field. REFINE will struggle to match phone-driven candidates.",
        },
        {
            "source": AssaySourceTable.LOYALTY_STAGING,
            "field": "aurum_loyalty_member_number",
            "null_pct": 0.0,
            "format_anomaly_pct": 13.3,  # 2 of 15 records don't match LP/VLP-XXXXXX pattern
            "inferred": AssayInferredType.TEXT,
            "severity": AssaySeverity.CRITICAL,
            "samples": ["VLP-100042", "ABC123", "VLP-7"],
            "note": "Critical: 2 of 15 LOYALTY records don't match expected VLP-XXXXXX pattern. Member-number-based join is unreliable for those records.",
        },
        # 4 Warning
        {
            "source": AssaySourceTable.ECOMM_STAGING,
            "field": "aurum_email_raw",
            "null_pct": 0.0,
            "format_anomaly_pct": 20.0,
            "inferred": AssayInferredType.EMAIL,
            "severity": AssaySeverity.WARNING,
            "samples": ["sarah.cgmail.com", "lukas@yahoo", "joana.r@gmail.com"],
            "note": "Warning: 4 of 20 ECOMM records have malformed emails. Steward review queue.",
        },
        {
            "source": AssaySourceTable.CRM_STAGING,
            "field": "aurum_phone_raw",
            "null_pct": 0.0,
            "format_anomaly_pct": 12.0,
            "inferred": AssayInferredType.PHONE,
            "severity": AssaySeverity.WARNING,
            "samples": ["+971-50-555-1042", "050-XXX", "TBD"],
            "note": "Warning: 3 of 25 CRM phone numbers are out-of-range length (< 8 chars or > 15 chars). Format normalizer needed.",
        },
        {
            "source": AssaySourceTable.LOYALTY_STAGING,
            "field": "aurum_email_raw",
            "null_pct": 33.3,
            "format_anomaly_pct": 0.0,
            "inferred": AssayInferredType.EMPTY,
            "severity": AssaySeverity.WARNING,
            "samples": [None, None, "older.member@yahoo.com"],
            "note": "Warning: 5 of 15 LOYALTY records have no email — older paper-enrolled members. Match logic must rely on phone + name + member_number.",
        },
        {
            "source": AssaySourceTable.CRM_STAGING,
            "field": "aurum_first_name_raw",
            "null_pct": 0.0,
            "format_anomaly_pct": 28.0,
            "inferred": AssayInferredType.TEXT,
            "severity": AssaySeverity.WARNING,
            "samples": ["PRIYA", "M.", "Sarah"],
            "note": "Warning: 7 of 25 CRM first-name values are ALL CAPS or single-initial-with-period. UNEARTH should normalize before REFINE.",
        },
        # 2 OK
        {
            "source": AssaySourceTable.CUSTOMER_GOLDEN,
            "field": "aurum_email_primary",
            "null_pct": 6.7,
            "format_anomaly_pct": 0.0,
            "inferred": AssayInferredType.EMAIL,
            "severity": AssaySeverity.OK,
            "samples": ["priya.k@gmail.com", "sarah.chen@atlasboutique.ae", "aisha.mubarak@outlook.com"],
            "note": "OK: 2 of 30 canonicals have no primary email. Within tolerance — those are loyalty-only members lacking email.",
        },
        {
            "source": AssaySourceTable.ECOMM_STAGING,
            "field": "aurum_default_shipping_country",
            "null_pct": 5.0,
            "format_anomaly_pct": 0.0,
            "inferred": AssayInferredType.TEXT,
            "severity": AssaySeverity.OK,
            "samples": ["United Arab Emirates", "United Arab Emirates", "United Arab Emirates"],
            "note": "OK: ECOMM shipping country is consistently 'United Arab Emirates' across populated records. Single-domain dataset.",
        },
    ]
    records = []
    for f in findings:
        records.append({
            "aurum_run_id": RUN_ID,
            "aurum_run_timestamp": TODAY_ISO_TS,
            "aurum_source_table": f["source"],
            "aurum_field_name": f["field"],
            "aurum_total_rows": (
                25 if f["source"] == AssaySourceTable.CRM_STAGING
                else 20 if f["source"] == AssaySourceTable.ECOMM_STAGING
                else 15 if f["source"] == AssaySourceTable.LOYALTY_STAGING
                else 30
            ),
            "aurum_null_count": int(f["null_pct"] / 100.0 * (
                25 if f["source"] == AssaySourceTable.CRM_STAGING
                else 20 if f["source"] == AssaySourceTable.ECOMM_STAGING
                else 15 if f["source"] == AssaySourceTable.LOYALTY_STAGING
                else 30
            )),
            "aurum_null_pct": f["null_pct"],
            "aurum_distinct_values": random.randint(8, 25),
            "aurum_inferred_type": f["inferred"],
            "aurum_format_anomaly_count": int(f["format_anomaly_pct"] / 100.0 * 20),
            "aurum_format_anomaly_pct": f["format_anomaly_pct"],
            "aurum_max_length": random.randint(20, 50),
            "aurum_min_length": random.randint(0, 5),
            "aurum_sample_value_1": str(f["samples"][0]) if f["samples"][0] else "",
            "aurum_sample_value_2": str(f["samples"][1]) if f["samples"][1] else "",
            "aurum_sample_value_3": str(f["samples"][2]) if f["samples"][2] else "",
            "aurum_severity": f["severity"],
        })
    return records


# ---------------------------------------------------------------------------
# Plan assembly
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    demo_stories: list[DemoStory]
    filler_canonicals: list[dict[str, Any]]
    filler_crm: list[dict[str, Any]]
    filler_ecomm: list[dict[str, Any]]
    filler_loyalty: list[dict[str, Any]]
    assay_records: list[dict[str, Any]]

    def total(self) -> int:
        demo_total = sum(len(s.records) for s in self.demo_stories)
        return (
            demo_total
            + len(self.filler_canonicals)
            + len(self.filler_crm)
            + len(self.filler_ecomm)
            + len(self.filler_loyalty)
            + len(self.assay_records)
        )

    def per_entity_counts(self) -> dict[str, int]:
        counts = {"aurum_customer": 0, "aurum_crm_customer": 0,
                  "aurum_ecomm_customer": 0, "aurum_loyalty_customer": 0,
                  "aurum_assay_profile": 0}
        for story in self.demo_stories:
            for r in story.records:
                counts[r.entity_logical] += 1
        counts["aurum_customer"] += len(self.filler_canonicals)
        counts["aurum_crm_customer"] += len(self.filler_crm)
        counts["aurum_ecomm_customer"] += len(self.filler_ecomm)
        counts["aurum_loyalty_customer"] += len(self.filler_loyalty)
        counts["aurum_assay_profile"] += len(self.assay_records)
        return counts


def build_plan() -> Plan:
    """Build the full sample data plan. Pure local computation (no network)."""
    random.seed(SEED)

    demo_stories = [
        build_priya_hero(),
        build_mohammed_ambiguous(),
        build_sarah_multibrand(),
        build_aisha_conflicting_sources(),
        build_new_prospect_cluster(),
    ]

    filler_canonicals = generate_filler_canonicals(count=26)

    # Distribute matched/prospect counts to hit volume targets:
    #   CRM:    5 demo matched + 1 demo pending + 2 demo prospects = 8 demo
    #           filler 17 = 10 matched + 7 prospects → total 25
    #   ECOMM:  2 demo matched + 1 demo prospect = 3 demo
    #           filler 17 = 10 matched + 7 prospects → total 20
    #   LOYALTY: 2 demo matched + 1 demo prospect = 3 demo
    #           filler 12 = 8 matched + 4 prospects → total 15
    filler_crm = generate_filler_crm_staging(filler_canonicals, matched_count=10, prospect_count=7)
    filler_ecomm = generate_filler_ecomm_staging(filler_canonicals, matched_count=10, prospect_count=7)
    filler_loyalty = generate_filler_loyalty_staging(filler_canonicals, matched_count=8, prospect_count=4)
    assay_records = generate_assay_records(count=8)

    return Plan(
        demo_stories=demo_stories,
        filler_canonicals=filler_canonicals,
        filler_crm=filler_crm,
        filler_ecomm=filler_ecomm,
        filler_loyalty=filler_loyalty,
        assay_records=assay_records,
    )


# ---------------------------------------------------------------------------
# Lineage doc generation (auto-regenerated on every invocation)
# ---------------------------------------------------------------------------


def render_lineage_doc(plan: Plan) -> str:
    """Render the demo-records lineage markdown from in-script demo metadata."""
    lines = [
        "# AURUM-PP Demo Records — AURUM Lineage",
        "",
        "> **Auto-generated by `scripts/load_sample_data.py`.** Do not hand-edit.",
        "> Edit the demo-record builders in the script and re-run to regenerate.",
        "",
        "Each demo-story record below demonstrates one or more stages of the AURUM",
        "five-stage architecture (ASSAY → UNEARTH → REFINE → UNFURL → MARK).",
        "Filler records are not listed here — they exist for volume realism only.",
        "",
        f"**Generated:** {TODAY_DATE_STR}",
        f"**Total records in plan:** {plan.total()}  ",
        f"**Demo-story records:** {sum(len(s.records) for s in plan.demo_stories)}  ",
        f"**Filler records:** {plan.total() - sum(len(s.records) for s in plan.demo_stories)}",
        "",
        "---",
        "",
    ]
    for i, story in enumerate(plan.demo_stories, start=1):
        stage_tag = " + ".join(story.aurum_stages)
        lines.append(f"## {i}. {story.pattern_name}")
        lines.append("")
        lines.append(f"**AURUM stage(s):** `{stage_tag}`")
        if story.concept_tags:
            tag_line = " ".join(f"`{t}`" for t in story.concept_tags)
            lines.append(f"**Concept tags:** {tag_line}")
        lines.append("")
        lines.append("### Records")
        lines.append("")
        for r in story.records:
            link_note = (
                f" — links to `{r.links_to_canonical_role}` via `aurum_canonical_customer`"
                if r.links_to_canonical_role
                else (" — **no canonical link** (steward review pending)"
                      if "ambiguous" in r.role_label.lower()
                      else " — **no canonical link** (new prospect)")
                if r.entity_logical != "aurum_customer"
                else ""
            )
            primary_id = _record_primary_identifier(r)
            lines.append(f"- **{r.role_label}** (`{r.entity_logical}`)")
            lines.append(f"  - Primary identifier: `{primary_id}`")
            if r.entity_logical != "aurum_customer":
                conf = r.payload.get("aurum_match_confidence")
                method = r.payload.get("aurum_match_method")
                if conf is not None:
                    method_label = _match_method_label(method)
                    lines.append(f"  - Match: confidence `{conf}` via `{method_label}`")
                if link_note:
                    lines.append(f"  - Link: {link_note.strip(' —')}")
                if r.matcher_outputs:
                    lines.extend(_render_matcher_breakdown(r.matcher_outputs))
        lines.append("")
        lines.append("### Narrative")
        lines.append("")
        lines.append(story.narrative)
        lines.append("")
        lines.append("### Match-confidence rationale")
        lines.append("")
        lines.append(story.confidence_explanation)
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## How this maps to the AURUM public-repo reference architecture")
    lines.append("")
    lines.append(
        f"All confidence values above are computed by **`refine.matching.matcher.score_pair`** "
        f"in the public AURUM repo (commit `{AURUM_COMMIT_HASH[:12]}`). The script imports "
        f"the function directly — see the top of `scripts/load_sample_data.py`. If the "
        f"AURUM matcher signature changes, the import breaks loudly (no silent drift via "
        f"a vendored copy)."
    )
    lines.append("")
    lines.append("**The matcher's composite-score formula has FOUR mechanisms, not three:**")
    lines.append("")
    lines.append(
        "1. **Component scores** (each in [0.0, 1.0]):  \n"
        "   - `name_score` = 0.5 × token-sort-ratio (RapidFuzz) + 0.5 × Jaro-Winkler (jellyfish), both lowercased  \n"
        "   - `email_score` = `1.0` if exact (post-lowercase + strip), else fuzzy × 0.3 (capped at 0.3)  \n"
        "   - `phone_score` = `1.0` if last-9-digits identical, else `0.0` (binary — no fuzzy)"
    )
    lines.append("2. **Weighted total:** `name_score × 0.65 + email_score × 0.25 + phone_score × 0.10`")
    lines.append(
        f"3. **NAME-BOOST FLOOR** (the load-bearing fourth mechanism, often missed):  \n"
        f"   `floor = name_score × {AURUM_NAME_BOOST_MULTIPLIER}` if `name_score >= 0.90` else `0.0`  \n"
        f"   `composite = max(weighted, floor)`  \n"
        f"   The boost recognises a real-world MDM truth: when two records share a near-identical "
        f"name, that alone is significant evidence of identity even when contact details diverge "
        f"across systems. Visible above in pairs where the per-record breakdown shows "
        f"`name_boost_floor` ACTIVE."
    )
    lines.append(
        f"4. **Match threshold:** `MATCH_THRESHOLD = {AURUM_MATCH_THRESHOLD}` — `composite >= "
        f"{AURUM_MATCH_THRESHOLD}` is `is_match=True` (auto-approve to canonical). Below this, "
        f"steward-review band. Below the candidate-filter floor of `0.55`, not surfaced as a "
        f"candidate at all."
    )
    lines.append("")
    lines.append("**Other AURUM patterns demonstrated by the data generation:**")
    lines.append("")
    lines.append(
        "- **Linked-tuple survivorship for geography** (Aisha): `address_line1` + `city` + "
        "`country` + `postal_code` are emitted as a single tuple per source. **CRITICAL:** "
        "the matcher does NOT score addresses at all — they're a pure UNFURL/survivorship "
        "concern, deliberately separated from REFINE matching. Aisha's address divergence is "
        "invisible to REFINE; it surfaces only when UNFURL picks one source's whole tuple."
    )
    lines.append(
        "- **Trust score** (every canonical): `0.6 × completeness + 0.4 × diversity`, where "
        "completeness is the fraction of 6 key fields populated and diversity = "
        "`min(distinct_sources / 3, 1.0)`. Filler canonicals compute trust from these formulas "
        "at generation time."
    )
    lines.append(
        "- **`is_golden` flag**: true when trust ≥ 0.6, per the public AURUM convention."
    )
    lines.append(
        "- **Single-Source Promotion** (LOYALTY-specific match_method value 6): demonstrates "
        "the AURUM pattern where loyalty-only members can be promoted to canonical without a "
        "second-source confirmation, used by the LOYALTY prospect record in pattern #5."
    )
    lines.append("")
    return "\n".join(lines)


def _render_matcher_breakdown(mo: dict[str, Any]) -> list[str]:
    """Render a per-pair matcher score breakdown for the lineage doc."""
    out = ["  - **Matcher breakdown** (`refine.matching.matcher.score_pair`):"]
    out.append(f"    - `name_score` = `{mo['name_score']:.4f}`")
    out.append(f"    - `email_score` = `{mo['email_score']:.4f}`")
    out.append(f"    - `phone_score` = `{mo['phone_score']:.4f}`")
    out.append(
        f"    - `weighted` = 0.65 × {mo['name_score']:.4f} + 0.25 × {mo['email_score']:.4f} "
        f"+ 0.10 × {mo['phone_score']:.4f} = `{mo['weighted']:.4f}`"
    )
    if mo["name_boost_active"]:
        out.append(
            f"    - `name_boost_floor` = **ACTIVE** (name_score ≥ 0.90; floor = "
            f"{AURUM_NAME_BOOST_MULTIPLIER} × {mo['name_score']:.4f} = `{mo['name_boost_floor']:.4f}`)"
        )
        out.append(f"    - `composite` = max(weighted, boost_floor) = `{mo['composite']:.4f}` ← boost wins")
    elif mo["name_boost_floor"] > 0:
        out.append(
            f"    - `name_boost_floor` = computed but did not win (floor "
            f"`{mo['name_boost_floor']:.4f}` ≤ weighted `{mo['weighted']:.4f}`)"
        )
        out.append(f"    - `composite` = max(weighted, boost_floor) = `{mo['composite']:.4f}`")
    else:
        out.append(f"    - `name_boost_floor` = inactive (name_score < 0.90)")
        out.append(f"    - `composite` = `{mo['composite']:.4f}`")
    return out


def _record_primary_identifier(r: DemoRecord) -> str:
    """Return a human-readable identifier for the record (table-specific primary)."""
    if r.entity_logical == "aurum_customer":
        return r.payload.get("aurum_full_name", "(unnamed)")
    if r.entity_logical == "aurum_crm_customer":
        return r.payload.get("aurum_crm_source_id", "(no source id)")
    if r.entity_logical == "aurum_ecomm_customer":
        return r.payload.get("aurum_email_raw", "(no email)")
    if r.entity_logical == "aurum_loyalty_customer":
        return r.payload.get("aurum_loyalty_member_number", "(no member num)")
    return "(unknown)"


def _match_method_label(value: int | None) -> str:
    return {
        MatchMethod.EXACT: "Exact-Match",
        MatchMethod.FUZZY_HIGH: "Fuzzy-High-Confidence",
        MatchMethod.FUZZY_BORDERLINE: "Fuzzy-Borderline",
        MatchMethod.STEWARD_APPROVED: "Steward-Approved",
        MatchMethod.UNMATCHED: "Unmatched",
        MatchMethod.SINGLE_SOURCE_PROMOTION: "Single-Source-Promotion",
    }.get(value, f"unknown({value})")


def write_lineage_doc(plan: Plan) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    LINEAGE_DOC.write_text(render_lineage_doc(plan), encoding="utf-8")
    log.info("Lineage doc written: %s", LINEAGE_DOC)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log.info("Manifest written: %s", MANIFEST_PATH)


# ---------------------------------------------------------------------------
# Force-clear (today-only delete by aurum_loaded_date / aurum_run_timestamp;
# canonical clearance via manifest if available)
# ---------------------------------------------------------------------------


def force_clear(api: WebAPI) -> None:
    """Delete records loaded today. Staging tables filter by aurum_loaded_date;
    assay filters by aurum_run_timestamp. Canonical uses manifest if exists.
    """
    today_start = TODAY.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
    tomorrow_start = (TODAY.replace(hour=0, minute=0, second=0, microsecond=0)
                      + timedelta(days=1)).isoformat().replace("+00:00", "Z")

    for entity in ("aurum_crm_customer", "aurum_ecomm_customer", "aurum_loyalty_customer"):
        filter_q = f"aurum_loaded_date ge {today_start} and aurum_loaded_date lt {tomorrow_start}"
        params = f"$select={entity}id&$filter={filter_q}"
        records = api.query(entity, params)
        log.info("Force-clear: %d records in %s loaded today", len(records), entity)
        for rec in records:
            api.delete(entity, rec[f"{entity}id"])

    # Assay
    filter_q = f"aurum_run_timestamp ge {today_start} and aurum_run_timestamp lt {tomorrow_start}"
    params = f"$select=aurum_assay_profileid&$filter={filter_q}"
    records = api.query("aurum_assay_profile", params)
    log.info("Force-clear: %d assay records loaded today", len(records))
    for rec in records:
        api.delete("aurum_assay_profile", rec["aurum_assay_profileid"])

    # Canonical clearance via manifest (safer than trying to filter by date)
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
        canonical_records = manifest.get("records", {}).get("aurum_customer", [])
        log.info("Force-clear: %d canonicals from manifest %s", len(canonical_records), MANIFEST_PATH)
        for entry in canonical_records:
            api.delete("aurum_customer", entry["id"])
    else:
        log.warning(
            "No manifest at %s; skipping canonical clearance. "
            "Manually delete via maker UI if needed.",
            MANIFEST_PATH,
        )


# ---------------------------------------------------------------------------
# Insert flow
# ---------------------------------------------------------------------------


def insert_all(api: WebAPI, plan: Plan) -> dict[str, Any]:
    """Insert all records. Canonicals first, then stagings with @odata.bind lookups."""
    manifest: dict[str, Any] = {
        "run_timestamp": TODAY_ISO_TS,
        "run_id": RUN_ID,
        "records": {
            "aurum_customer": [],
            "aurum_crm_customer": [],
            "aurum_ecomm_customer": [],
            "aurum_loyalty_customer": [],
            "aurum_assay_profile": [],
        },
    }
    canonical_set = api.entity_sets["aurum_customer"]

    # Phase 1: insert demo-story canonicals; capture role→entity_id_url map
    demo_canonical_url: dict[str, str] = {}  # story_pattern_name → entity_id_url
    log.info("Phase 1: insert demo-story canonicals")
    for story in plan.demo_stories:
        for rec in story.records:
            if rec.entity_logical != "aurum_customer":
                continue
            payload = remove_calc_fields("aurum_customer", rec.payload)
            guid, url = api.post_record("aurum_customer", payload)
            log.info("  Created %s: %s (guid=%s)", story.pattern_name, rec.role_label, guid)
            manifest["records"]["aurum_customer"].append({
                "id": guid, "url": url,
                "display": _record_primary_identifier(rec),
                "demo_story": story.pattern_name,
            })
            demo_canonical_url[story.pattern_name] = url

    # Phase 2: insert demo-story staging records, binding to demo canonicals
    log.info("Phase 2: insert demo-story staging records")
    for story in plan.demo_stories:
        for rec in story.records:
            if rec.entity_logical == "aurum_customer":
                continue
            payload = remove_calc_fields(rec.entity_logical, rec.payload)
            if rec.links_to_canonical_role:
                canonical_url = demo_canonical_url.get(story.pattern_name)
                if canonical_url:
                    payload["aurum_canonical_customer@odata.bind"] = (
                        _bind_path_from_url(canonical_url, canonical_set)
                    )
            guid, url = api.post_record(rec.entity_logical, payload)
            log.info("  Created %s in %s (guid=%s)", rec.role_label, rec.entity_logical, guid)
            manifest["records"][rec.entity_logical].append({
                "id": guid, "url": url,
                "display": _record_primary_identifier(rec),
                "demo_story": story.pattern_name,
            })

    # Phase 3: insert filler canonicals; capture index→url map
    log.info("Phase 3: insert filler canonicals (%d)", len(plan.filler_canonicals))
    filler_canonical_url: dict[int, str] = {}
    for c in plan.filler_canonicals:
        payload = remove_calc_fields("aurum_customer", c["payload"])
        guid, url = api.post_record("aurum_customer", payload)
        manifest["records"]["aurum_customer"].append({
            "id": guid, "url": url,
            "display": f"{c['_first']} {c['_last']}",
            "demo_story": "(filler)",
        })
        filler_canonical_url[c["_filler_index"]] = url

    # Phase 4: insert filler staging records, binding to filler canonicals where applicable
    log.info("Phase 4: insert filler staging records")
    for entity_logical, records in [
        ("aurum_crm_customer", plan.filler_crm),
        ("aurum_ecomm_customer", plan.filler_ecomm),
        ("aurum_loyalty_customer", plan.filler_loyalty),
    ]:
        for rec in records:
            payload = remove_calc_fields(entity_logical, rec["payload"])
            link_idx = rec.get("_links_canonical_index")
            if link_idx is not None:
                canonical_url = filler_canonical_url.get(link_idx)
                if canonical_url:
                    payload["aurum_canonical_customer@odata.bind"] = (
                        _bind_path_from_url(canonical_url, canonical_set)
                    )
            guid, url = api.post_record(entity_logical, payload)
            manifest["records"][entity_logical].append({
                "id": guid, "url": url,
                "display": _filler_display(entity_logical, rec["payload"]),
                "demo_story": "(filler)",
            })
        log.info("  Inserted %d %s records", len(records), entity_logical)

    # Phase 5: insert assay records (no lookup, no linkage)
    log.info("Phase 5: insert assay records (%d)", len(plan.assay_records))
    for rec in plan.assay_records:
        payload = remove_calc_fields("aurum_assay_profile", rec)
        guid, url = api.post_record("aurum_assay_profile", payload)
        manifest["records"]["aurum_assay_profile"].append({
            "id": guid, "url": url,
            "display": rec.get("aurum_field_name", "(unnamed assay)"),
            "demo_story": "(assay)",
        })

    return manifest


def _bind_path_from_url(entity_id_url: str, entity_set: str) -> str:
    """Convert a full OData-EntityId URL into the relative @odata.bind path.
    e.g. https://x.crm.dynamics.com/api/data/v9.2/aurum_customers(<guid>)
    becomes /aurum_customers(<guid>)."""
    guid = _extract_guid(entity_id_url)
    return f"/{entity_set}({guid})"


def _filler_display(entity_logical: str, payload: dict[str, Any]) -> str:
    if entity_logical == "aurum_crm_customer":
        return f"{payload.get('aurum_first_name_raw','')} {payload.get('aurum_last_name_raw','')} ({payload.get('aurum_crm_source_id','')})"
    if entity_logical == "aurum_ecomm_customer":
        return f"{payload.get('aurum_email_raw','')} ({payload.get('aurum_ecomm_source_id','')})"
    if entity_logical == "aurum_loyalty_customer":
        return f"{payload.get('aurum_full_name_legacy','')} ({payload.get('aurum_loyalty_member_number','')})"
    return "(unknown)"


# ---------------------------------------------------------------------------
# Dry-run printer
# ---------------------------------------------------------------------------


def print_plan_summary(plan: Plan) -> None:
    counts = plan.per_entity_counts()
    print("\n" + "=" * 72)
    print(f"SAMPLE DATA PLAN — {plan.total()} records")
    print("=" * 72)
    print()
    print("Volume by entity:")
    for entity, n in counts.items():
        print(f"  {entity:<28} {n:>3}")
    print(f"  {'TOTAL':<28} {plan.total():>3}")

    print("\nDemo-story records (with AURUM stage tags):")
    print()
    for i, story in enumerate(plan.demo_stories, start=1):
        stage_tag = " + ".join(story.aurum_stages)
        print(f"  [{stage_tag}] {i}. {story.pattern_name}")
        for rec in story.records:
            link_marker = ""
            if rec.entity_logical != "aurum_customer":
                if rec.links_to_canonical_role:
                    link_marker = f"  →linked to '{rec.links_to_canonical_role}'"
                else:
                    link_marker = "  →no canonical link (prospect/pending)"
            print(f"       • {rec.role_label}: {_record_primary_identifier(rec)}{link_marker}")
        print()

    print("Filler distribution:")
    print(f"  Canonicals: {len(plan.filler_canonicals)} (each linked from 1+ filler stagings)")
    print(f"  CRM:        {len(plan.filler_crm)} ({sum(1 for r in plan.filler_crm if r.get('_links_canonical_index') is not None)} matched, {sum(1 for r in plan.filler_crm if r.get('_links_canonical_index') is None)} prospects)")
    print(f"  ECOMM:      {len(plan.filler_ecomm)} ({sum(1 for r in plan.filler_ecomm if r.get('_links_canonical_index') is not None)} matched, {sum(1 for r in plan.filler_ecomm if r.get('_links_canonical_index') is None)} prospects)")
    print(f"  LOYALTY:    {len(plan.filler_loyalty)} ({sum(1 for r in plan.filler_loyalty if r.get('_links_canonical_index') is not None)} matched, {sum(1 for r in plan.filler_loyalty if r.get('_links_canonical_index') is None)} prospects)")

    print("\nAssay findings:")
    for r in plan.assay_records:
        sev_label = {1: "OK", 2: "Warning", 3: "Critical"}.get(r["aurum_severity"], "?")
        src_label = {1: "CRM", 2: "ECOMM", 3: "LOYALTY", 4: "Customer"}.get(r["aurum_source_table"], "?")
        print(f"  [{sev_label:<8}] {src_label:<8} {r['aurum_field_name']:<35} null={r['aurum_null_pct']}% anomaly={r['aurum_format_anomaly_pct']}%")

    print("\nSample filler records (3 random for spot-check):")
    samples_to_show = []
    if plan.filler_crm:
        samples_to_show.append(("CRM", plan.filler_crm[0]["payload"]))
    if plan.filler_ecomm:
        samples_to_show.append(("ECOMM", plan.filler_ecomm[3]["payload"] if len(plan.filler_ecomm) > 3 else plan.filler_ecomm[0]["payload"]))
    if plan.filler_loyalty:
        samples_to_show.append(("LOYALTY", plan.filler_loyalty[2]["payload"] if len(plan.filler_loyalty) > 2 else plan.filler_loyalty[0]["payload"]))
    for label, payload in samples_to_show:
        identifier = (
            payload.get("aurum_crm_source_id")
            or payload.get("aurum_email_raw")
            or payload.get("aurum_loyalty_member_number")
            or "(?)"
        )
        name = (
            payload.get("aurum_first_name_raw") or payload.get("aurum_first_name_parsed") or ""
        )
        last = (
            payload.get("aurum_last_name_raw") or payload.get("aurum_last_name_parsed") or ""
        )
        print(f"  [{label:<8}] {identifier:<25} {name} {last}".rstrip())

    print("\n" + "=" * 72)
    print(f"DRY-RUN COMPLETE — no inserts. Lineage doc: {LINEAGE_DOC}")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and insert AURUM-PP demo sample data."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Build plan, render lineage doc, print summary. No writes, no auth.",
    )
    parser.add_argument(
        "--force-clear", action="store_true",
        help="DESTRUCTIVE: delete today's previously-loaded records before inserting.",
    )
    args = parser.parse_args()

    _configure_logging()

    log.info("Building plan (deterministic seed=%d)", SEED)
    plan = build_plan()
    log.info("Plan built: %d records total", plan.total())

    write_lineage_doc(plan)

    if args.dry_run:
        print_plan_summary(plan)
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
        api.lookup_entity_sets()
    except RuntimeError as exc:
        log.error("Entity-set discovery failed: %s", exc)
        return 1

    if args.force_clear:
        log.warning("Force-clear enabled — deleting today's records first.")
        try:
            force_clear(api)
        except RuntimeError as exc:
            log.error("Force-clear failed: %s", exc)
            return 1

    try:
        manifest = insert_all(api, plan)
    except RuntimeError as exc:
        log.error("Insert failed: %s", exc)
        return 2

    write_manifest(manifest)
    log.info("Sample data load complete. %d records inserted.", plan.total())
    return 0


if __name__ == "__main__":
    sys.exit(main())
