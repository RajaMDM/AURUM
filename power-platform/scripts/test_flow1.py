"""
test_flow1.py — Verify Phase 4 Flow 1 (auto-approve high-confidence match) is working.

Flips Sarah Chen CRM record's aurum_processing_status from 4 (SURVIVED) to 3 (MATCHED)
to satisfy Flow 1's trigger filter (confidence >= 0.85 AND status = 3 = MATCHED).
Waits 90s for the cloud flow to fire (Dataverse triggers have polling latency).
Re-reads the staging record + the linked canonical and reports what changed.

Flow 1 expected actions:
  1. Pre-condition: aurum_canonical_customer is not null (Sarah's is — links to canonical)
  2. Update staging — set aurum_processing_status = 4 (SURVIVED)
  3. Update canonical — set aurum_last_refined_date = utcNow()

Pass criteria:
  - Sarah's processing_status flips back to 4 (proves Flow action 2 ran)
  - Canonical's aurum_last_refined_date advances (proves Flow action 3 ran)

Read-only besides the one PATCH on Sarah CRM. PATCH is repeatable — Flow 1
just keeps flipping her back to 4.

Usage:
    source ~/.zprofile && source .venv/bin/activate
    python scripts/test_flow1.py
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from auth import get_token  # noqa: E402
from load_sample_data import get_dataverse_url  # noqa: E402

WAIT_SECS = 90
SARAH_CRM_SOURCE_ID = "CRM-01077"


def main() -> int:
    token = get_token()
    base = get_dataverse_url().rstrip("/") + "/api/data/v9.2/"
    h_get = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    }
    h_patch = {**h_get, "Content-Type": "application/json", "If-Match": "*"}

    # --- 1. Find Sarah Chen CRM ---
    sarah_select = (
        "$select=aurum_crm_customerid,aurum_first_name_raw,aurum_last_name_raw,"
        "aurum_processing_status,aurum_match_confidence,aurum_match_method,"
        "_aurum_canonical_customer_value,modifiedon"
    )
    sarah_filter = (
        f"$filter=aurum_first_name_raw eq 'Sarah' and aurum_last_name_raw eq 'Chen' "
        f"and aurum_crm_source_id eq '{SARAH_CRM_SOURCE_ID}'"
    )
    sarah_url = base + f"aurum_crm_customers?{sarah_filter}&{sarah_select}"

    r = requests.get(sarah_url, headers=h_get, timeout=30)
    r.raise_for_status()
    recs = r.json().get("value", [])
    if len(recs) != 1:
        print(f"FATAL: expected 1 Sarah Chen CRM record, got {len(recs)}", file=sys.stderr)
        return 2

    s = recs[0]
    sid = s["aurum_crm_customerid"]
    canonical_lookup = s.get("_aurum_canonical_customer_value")

    # Read current canonical for baseline
    canonical_url = (
        base
        + f"aurum_customers({canonical_lookup})"
        + "?$select=aurum_full_name,aurum_last_refined_date,modifiedon"
    )
    r = requests.get(canonical_url, headers=h_get, timeout=30)
    r.raise_for_status()
    c_before = r.json()

    print("=" * 72)
    print("BEFORE TEST")
    print("=" * 72)
    print(f"Sarah CRM record found:")
    print(f"  GUID:                         {sid}")
    print(f"  Name:                         {s['aurum_first_name_raw']} {s['aurum_last_name_raw']}")
    print(f"  processing_status:            {s['aurum_processing_status']} (expected 4 = SURVIVED)")
    print(f"  match_confidence:             {s['aurum_match_confidence']}")
    print(f"  match_method:                 {s['aurum_match_method']}")
    print(f"  staging modifiedon:           {s['modifiedon']}")
    print(f"  canonical link GUID:          {canonical_lookup}")
    print(f"Canonical record:")
    print(f"  full_name:                    {c_before.get('aurum_full_name')}")
    print(f"  last_refined_date (BEFORE):   {c_before.get('aurum_last_refined_date')}")
    print(f"  canonical modifiedon:         {c_before.get('modifiedon')}")

    if s["aurum_processing_status"] != 4:
        print(f"\nWARNING: Sarah's processing_status is {s['aurum_processing_status']}, "
              f"expected 4. The test still proceeds — just noting the deviation from "
              f"Phase 2 sample-data baseline.")

    # --- 2. PATCH status to 3 (MATCHED) ---
    print()
    print("=" * 72)
    print("PATCH — flip processing_status from current value to 3 (MATCHED)")
    print("=" * 72)
    patch_url = base + f"aurum_crm_customers({sid})"
    patch_time = datetime.now(timezone.utc)
    print(f"PATCH UTC time:               {patch_time.isoformat()}")
    r = requests.patch(
        patch_url, headers=h_patch, json={"aurum_processing_status": 3}, timeout=30
    )
    r.raise_for_status()
    print(f"PATCH HTTP:                   {r.status_code} {r.reason}")

    # Re-read immediately
    r = requests.get(sarah_url, headers=h_get, timeout=30)
    r.raise_for_status()
    s_post = r.json()["value"][0]
    print(f"Immediately after PATCH:")
    print(f"  processing_status:            {s_post['aurum_processing_status']} (expected 3 = MATCHED)")
    print(f"  match_confidence:             {s_post['aurum_match_confidence']} (untouched)")
    print(f"  staging modifiedon:           {s_post['modifiedon']}")

    # --- 3. Wait ---
    print()
    print("=" * 72)
    print(f"WAITING {WAIT_SECS}s for Flow 1 to fire (Dataverse trigger latency)")
    print("=" * 72)
    for elapsed in range(0, WAIT_SECS, 30):
        time.sleep(min(30, WAIT_SECS - elapsed))
        print(f"  ...{elapsed + min(30, WAIT_SECS - elapsed)}s elapsed")

    # --- 4. Re-read both records ---
    r = requests.get(sarah_url, headers=h_get, timeout=30)
    r.raise_for_status()
    s_final = r.json()["value"][0]
    r = requests.get(canonical_url, headers=h_get, timeout=30)
    r.raise_for_status()
    c_after = r.json()

    print()
    print("=" * 72)
    print(f"AFTER {WAIT_SECS}s WAIT")
    print("=" * 72)
    print(f"Sarah CRM:")
    print(f"  processing_status:            {s_final['aurum_processing_status']} "
          f"(expected 4 = SURVIVED if Flow 1 worked)")
    print(f"  match_confidence:             {s_final['aurum_match_confidence']}")
    print(f"  staging modifiedon:           {s_final['modifiedon']}")
    print(f"Canonical:")
    print(f"  last_refined_date (AFTER):    {c_after.get('aurum_last_refined_date')}")
    print(f"  canonical modifiedon:         {c_after.get('modifiedon')}")

    # --- 5. Diagnose ---
    status_back_to_4 = s_final["aurum_processing_status"] == 4
    staging_modified_after_patch = s_final["modifiedon"] != s_post["modifiedon"]
    canonical_lrd_advanced = (
        c_after.get("aurum_last_refined_date") != c_before.get("aurum_last_refined_date")
    )
    canonical_modified_after = c_after.get("modifiedon") != c_before.get("modifiedon")

    print()
    print("=" * 72)
    print("TEST RESULT")
    print("=" * 72)
    if status_back_to_4 and canonical_lrd_advanced:
        print("✓ FLOW 1 WORKED")
        print("  - Staging processing_status flipped back to 4 (Flow action 2 ran)")
        print("  - Canonical last_refined_date advanced (Flow action 3 ran)")
        print("  - Both Flow 1 update actions executed successfully")
    elif status_back_to_4 and not canonical_lrd_advanced:
        print("⚠ PARTIAL SUCCESS — staging updated, canonical NOT updated")
        print("  - Flow action 2 ran (staging back to 4)")
        print("  - Flow action 3 may have failed or been skipped")
        print("  - Possible cause: lookup-resolution issue on aurum_canonical_customer in step 3")
    elif not status_back_to_4 and not staging_modified_after_patch:
        print("✗ FLOW DID NOT FIRE")
        print("  - Staging modifiedon unchanged since PATCH")
        print("  - Possible causes:")
        print("    a) Trigger 'Select columns' doesn't include aurum_processing_status")
        print("       → re-edit trigger, add it (or leave blank to fire on any column change)")
        print("    b) Trigger 'Scope' set to 'User' instead of 'Organization'")
        print("       → check trigger config, set to Organization")
        print("    c) Flow turned OFF or paused (user said it's ON, but worth re-confirming)")
        print("    d) Trigger filter expression has a typo — e.g., 'eq 3' interpreted as string '3'")
    elif not status_back_to_4 and staging_modified_after_patch:
        print("✗ FLOW FIRED BUT FAILED")
        print("  - Staging modifiedon advanced (something modified after PATCH)")
        print("  - But processing_status is not back to 4")
        print("  - Possible causes:")
        print("    a) Condition step (canonical-customer-not-null) evaluated false unexpectedly")
        print("    b) Update-staging action failed at runtime — check flow run history")
        print("    c) Flow loop-protection killed the run")
        print(f"  - Final status value seen: {s_final['aurum_processing_status']}")

    # --- 6. Workflow state check (best-effort) ---
    print()
    print("=" * 72)
    print("WORKFLOW REGISTRATION (best-effort, Dataverse Web API only)")
    print("=" * 72)
    print("Note: detailed per-run history (input/output, error msg, duration) lives in")
    print("Power Automate API (api.flow.microsoft.com), not Dataverse Web API. For")
    print("per-run forensics: make.powerautomate.com → My flows → <flow> → Run history.")
    print()
    try:
        wf_url = (
            base
            + "workflows?"
            + "$filter=(contains(name,'AURUM') or contains(name,'Auto-Approve'))"
            + "&$select=name,category,statecode,statuscode,workflowid,modifiedon"
            + "&$top=20"
        )
        r = requests.get(wf_url, headers=h_get, timeout=30)
        r.raise_for_status()
        flows = r.json().get("value", [])
        print(f"Workflows matching 'AURUM' or 'Auto-Approve': {len(flows)}")
        for f in flows:
            state_label = {0: "Draft", 1: "Activated"}.get(f.get("statecode"), f.get("statecode"))
            cat_label = {0: "Workflow", 1: "Dialog", 2: "Business Rule",
                         3: "Action", 4: "Business Process Flow",
                         5: "Modern Flow"}.get(f.get("category"), f.get("category"))
            print(f"  - {f.get('name')!r}")
            print(f"      category={cat_label}, statecode={state_label}, "
                  f"modifiedon={f.get('modifiedon')}")
    except Exception as e:
        print(f"Workflow registry query failed (non-fatal): {e}")

    return 0 if status_back_to_4 else 1


if __name__ == "__main__":
    raise SystemExit(main())
