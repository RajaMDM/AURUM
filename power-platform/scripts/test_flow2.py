"""
test_flow2.py — Verify Phase 4 Flow 2 (Steward Review for borderline matches) is working.

Flips Mohammed Al-Rashid's CRM staging record from aurum_processing_status = 5
(STEWARD_REVIEW) to 3 (MATCHED) to satisfy Flow 2's trigger filter
(0.55 <= confidence < 0.65 AND status = 3 = MATCHED). Mohammed sits at
composite=0.60 — exactly in the borderline band. After 90s wait, status should
flip back to 5 (STEWARD_REVIEW), proving Flow 2 caught the change.

Flow 2 expected actions:
  1. Update staging — set aurum_processing_status = 5 (STEWARD_REVIEW)

Pass criteria:
  - Mohammed's processing_status flips back to 5 within ~90s

Notes:
  - Mohammed CRM is the ONLY borderline-band demo record (per audit:
    composite=0.60, in 0.55–0.65 range). He's the unique test subject.
  - Read-only besides the one PATCH on Mohammed CRM. PATCH is repeatable —
    Flow 2 just keeps flipping him back to 5.

Usage:
    source ~/.zprofile && source .venv/bin/activate
    python scripts/test_flow2.py
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
MOHAMMED_CRM_SOURCE_ID = "CRM-00219"


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

    # --- 1. Find Mohammed CRM ---
    select = (
        "$select=aurum_crm_customerid,aurum_first_name_raw,aurum_last_name_raw,"
        "aurum_processing_status,aurum_match_confidence,aurum_match_method,"
        "_aurum_canonical_customer_value,modifiedon"
    )
    flt = f"$filter=aurum_crm_source_id eq '{MOHAMMED_CRM_SOURCE_ID}'"
    list_url = base + f"aurum_crm_customers?{flt}&{select}"

    r = requests.get(list_url, headers=h_get, timeout=30)
    r.raise_for_status()
    recs = r.json().get("value", [])
    if len(recs) != 1:
        print(f"FATAL: expected 1 Mohammed CRM record (source_id={MOHAMMED_CRM_SOURCE_ID}), "
              f"got {len(recs)}", file=sys.stderr)
        return 2

    m = recs[0]
    mid = m["aurum_crm_customerid"]

    print("=" * 72)
    print("BEFORE TEST")
    print("=" * 72)
    print(f"Mohammed CRM record found:")
    print(f"  GUID:                         {mid}")
    print(f"  Name (raw):                   {m['aurum_first_name_raw']} {m['aurum_last_name_raw']}")
    print(f"  processing_status:            {m['aurum_processing_status']} (expected 5 = STEWARD_REVIEW)")
    print(f"  match_confidence:             {m['aurum_match_confidence']} (expected ~0.60, in Flow 2's band)")
    print(f"  match_method:                 {m['aurum_match_method']} (expected 3 = FUZZY_BORDERLINE)")
    print(f"  canonical link GUID:          {m.get('_aurum_canonical_customer_value')} (expected null — Mohammed is unlinked)")
    print(f"  staging modifiedon:           {m['modifiedon']}")

    if m["aurum_processing_status"] != 5:
        print(f"\nNOTE: Mohammed's processing_status is {m['aurum_processing_status']}, "
              f"not 5. Test still proceeds — but flow result interpretation may differ.")

    confidence = m["aurum_match_confidence"]
    if not (0.55 <= confidence < 0.65):
        print(f"\nWARNING: Mohammed's match_confidence is {confidence}, OUTSIDE Flow 2's "
              f"0.55–0.65 band. Flow 2 trigger filter will NOT match this record. "
              f"Test will fail to demonstrate Flow 2.")
        return 3

    # --- 2. PATCH status to 3 (MATCHED) ---
    print()
    print("=" * 72)
    print("PATCH — flip processing_status to 3 (MATCHED)")
    print("=" * 72)
    patch_url = base + f"aurum_crm_customers({mid})"
    patch_time = datetime.now(timezone.utc)
    print(f"PATCH UTC time:               {patch_time.isoformat()}")
    r = requests.patch(
        patch_url, headers=h_patch, json={"aurum_processing_status": 3}, timeout=30
    )
    r.raise_for_status()
    print(f"PATCH HTTP:                   {r.status_code} {r.reason}")

    # Re-read immediately
    r = requests.get(list_url, headers=h_get, timeout=30)
    r.raise_for_status()
    m_post = r.json()["value"][0]
    print(f"Immediately after PATCH:")
    print(f"  processing_status:            {m_post['aurum_processing_status']} (expected 3 = MATCHED)")
    print(f"  match_confidence:             {m_post['aurum_match_confidence']} (untouched)")
    print(f"  staging modifiedon:           {m_post['modifiedon']}")

    # --- 3. Wait ---
    print()
    print("=" * 72)
    print(f"WAITING {WAIT_SECS}s for Flow 2 to fire")
    print("=" * 72)
    for elapsed in range(0, WAIT_SECS, 30):
        time.sleep(min(30, WAIT_SECS - elapsed))
        print(f"  ...{elapsed + min(30, WAIT_SECS - elapsed)}s elapsed")

    # --- 4. Re-read ---
    r = requests.get(list_url, headers=h_get, timeout=30)
    r.raise_for_status()
    m_final = r.json()["value"][0]

    print()
    print("=" * 72)
    print(f"AFTER {WAIT_SECS}s WAIT")
    print("=" * 72)
    print(f"Mohammed CRM:")
    print(f"  processing_status:            {m_final['aurum_processing_status']} "
          f"(expected 5 = STEWARD_REVIEW if Flow 2 worked)")
    print(f"  match_confidence:             {m_final['aurum_match_confidence']}")
    print(f"  staging modifiedon:           {m_final['modifiedon']}")

    # --- 5. Diagnose ---
    status_back_to_5 = m_final["aurum_processing_status"] == 5
    staging_modified_after_patch = m_final["modifiedon"] != m_post["modifiedon"]
    elapsed_label = ""
    try:
        # Compute approximate elapsed seconds between PATCH and final modifiedon
        from datetime import datetime as _dt
        final_dt = _dt.fromisoformat(m_final["modifiedon"].replace("Z", "+00:00"))
        elapsed = (final_dt - patch_time).total_seconds()
        elapsed_label = f" (~{elapsed:.0f}s after PATCH)"
    except Exception:
        pass

    print()
    print("=" * 72)
    print("TEST RESULT")
    print("=" * 72)
    if status_back_to_5:
        print(f"✓ FLOW 2 WORKED")
        print(f"  - Status flipped back to 5 (STEWARD_REVIEW){elapsed_label}")
        print(f"  - Mohammed's borderline-band record correctly routed to steward review")
    elif not staging_modified_after_patch:
        print(f"✗ FLOW DID NOT FIRE")
        print(f"  - Staging modifiedon unchanged since PATCH")
        print(f"  - Possible causes (same diagnostic ladder as Flow 1):")
        print(f"    a) Trigger 'Select columns' doesn't include aurum_processing_status")
        print(f"    b) Trigger 'Scope' set to 'User' instead of 'Organization'")
        print(f"    c) Flow turned OFF or not yet saved/activated")
        print(f"    d) Trigger filter syntax issue — check OData expression in trigger config")
    elif staging_modified_after_patch and not status_back_to_5:
        print(f"✗ FLOW FIRED BUT FAILED")
        print(f"  - Staging modifiedon advanced (something modified after PATCH)")
        print(f"  - But processing_status is not 5")
        print(f"  - Final status value seen: {m_final['aurum_processing_status']}")
        print(f"  - Likely: filter condition evaluated false (verify upper bound 'lt 0.65',")
        print(f"    or condition action assigned wrong value)")

    # --- 6. Workflow registration check ---
    print()
    print("=" * 72)
    print("WORKFLOW REGISTRATION (best-effort)")
    print("=" * 72)
    try:
        wf_url = (
            base
            + "workflows?"
            + "$filter=(contains(name,'AURUM') or contains(name,'Steward'))"
            + "&$select=name,category,statecode,statuscode,workflowid,modifiedon"
            + "&$top=20"
        )
        r = requests.get(wf_url, headers=h_get, timeout=30)
        r.raise_for_status()
        flows = r.json().get("value", [])
        print(f"Workflows matching 'AURUM' or 'Steward': {len(flows)}")
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

    return 0 if status_back_to_5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
