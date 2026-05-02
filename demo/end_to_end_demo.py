"""
AURUM End-to-End Pipeline Demo
Runs the full ASSAY → UNEARTH → REFINE → UNFURL → MARK arc
on synthetic customer data.

Usage:
    python shared/sample_data/generate_all.py   # generate dirty data first
    python demo/end_to_end_demo.py
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from shared.sample_data.generate_all import (
    generate_customers, generate_products, generate_assets, generate_locations, OUTPUT_DIR
)
from assay.schema_inspector.inspector import SchemaInspector
from unearth.profiler.domain_profiler import CustomerProfiler
from refine.matching.matcher import find_candidates
from refine.golden_record.survivorship import build_golden_record
from unfurl.publish.publisher import GoldenRecordPublisher
from mark.lineage.tracker import LineageTracker

import pandas as pd


def separator(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def main() -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  AURUM — End-to-End Pipeline Demo                       ║")
    print("║  Raw data in. Hallmarked golden records out.             ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ── STAGE 01: ASSAY ──────────────────────────────────────────────
    separator("STAGE 01: ASSAY — Inspect the raw ore")
    generate_customers(n=50)
    customer_path = OUTPUT_DIR / "customers_dirty.csv"

    inspector = SchemaInspector(source_name="CRM_EXPORT")
    schema = inspector.inspect(customer_path)
    print(f"  Source:         {schema['source']}")
    print(f"  Rows:           {schema['row_count']}")
    print(f"  Fields:         {schema['field_count']}")
    print(f"  High-null:      {schema['high_null_fields']}")
    assert schema["row_count"] == 50, "ASSAY: row count mismatch"
    assert schema["field_count"] > 0, "ASSAY: no fields found"
    print("  ✅ ASSAY passed")

    # ── STAGE 02: UNEARTH ────────────────────────────────────────────
    separator("STAGE 02: UNEARTH — Surface what's buried")
    profiler = CustomerProfiler()
    profile = profiler.profile(str(customer_path))
    summary = profile.summary()
    print(f"  Rows profiled:  {summary['rows']}")
    print(f"  DQ issues:      {summary['issues']}")
    print(f"  Quality score:  {summary['quality_score_pct']}%")
    print(f"  Issues by rule: {summary['by_rule']}")
    assert summary["rows"] == 50, "UNEARTH: row count mismatch"
    print("  ✅ UNEARTH passed")

    # ── STAGE 03: REFINE ─────────────────────────────────────────────
    separator("STAGE 03: REFINE — Fuse many into one golden record")
    df = pd.read_csv(customer_path, dtype=str, keep_default_na=False)
    candidates = find_candidates(df, sample_size=20)
    matches = [c for c in candidates if c.is_match]
    print(f"  Candidates:     {len(candidates)}")
    print(f"  Matches (≥0.75):{len(matches)}")
    if matches:
        top = matches[0]
        print(f"  Top match:      {top.record_a_id} ↔ {top.record_b_id}  score={top.composite_score}")

    # Build a golden record from a small cluster
    cluster = df.head(4).to_dict("records")
    golden = build_golden_record(cluster)
    print(f"  Golden record:  {golden['first_name']} {golden['last_name']}")
    print(f"  Trust score:    {golden['trust_score']}")
    print(f"  Sources merged: {golden['source_systems']}")
    assert golden["is_golden"] is True, "REFINE: golden flag not set"
    assert golden["trust_score"] > 0, "REFINE: trust score is zero"
    print("  ✅ REFINE passed")

    # ── STAGE 04: UNFURL ─────────────────────────────────────────────
    separator("STAGE 04: UNFURL — Issue to the world")
    publisher = GoldenRecordPublisher({
        "ERP":   "https://erp.internal/api/mdm/customer",
        "CRM":   "https://crm.internal/api/mdm/customer",
        "ECOMM": "https://ecomm.internal/api/mdm/customer",
    })
    result = publisher.publish(golden, domain="customer")
    print(f"  Published to:   {result['published_to']}")
    assert len(result["published_to"]) == 3, "UNFURL: consumer count mismatch"
    print("  ✅ UNFURL passed")

    # ── STAGE 05: MARK ───────────────────────────────────────────────
    separator("STAGE 05: MARK — Stamp provenance and lineage")
    tracker = LineageTracker()
    record_id = "AURUM-CUST-00001"
    tracker.record(record_id, "ASSAY_COMPLETE",   {"source": "CRM_EXPORT", "rows": 50})
    tracker.record(record_id, "UNEARTH_COMPLETE", {"issues": summary["issues"], "quality_score": summary["quality_score_pct"]})
    tracker.record(record_id, "REFINE_COMPLETE",  {"cluster_size": golden["cluster_size"], "trust_score": golden["trust_score"]})
    tracker.record(record_id, "UNFURL_COMPLETE",  {"consumers": result["published_to"]})
    tracker.record(record_id, "MARK_STAMPED",     {"is_golden": True})

    history = tracker.history(record_id)
    print(f"  Lineage events: {len(history)}")
    for event in history:
        print(f"    [{event['action']}] @ {event['timestamp'][:19]}")
    assert len(history) == 5, "MARK: lineage event count mismatch"
    print("  ✅ MARK passed")

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  ALL STAGES PASSED — Golden record hallmarked.           ║")
    print("╚══════════════════════════════════════════════════════════╝\n")


if __name__ == "__main__":
    main()
