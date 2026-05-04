"""
Unit tests for the 7 AURUM domain profilers.

Each test writes a tiny dirty-CSV fixture to a tempfile, runs the profiler,
and asserts on the rule codes that should fire (or not fire).
"""
from __future__ import annotations
import tempfile
from pathlib import Path

import pytest

from unearth.profiler.domain_profiler import (
    AssetProfiler,
    CounterpartyProfiler,
    CustomerProfiler,
    EmployeeProfiler,
    LocationProfiler,
    ProductProfiler,
    ProfileResult,
    VendorProfiler,
)


def _write_csv(rows: list[str]) -> str:
    """Write rows (header + data lines) to a tempfile and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    tmp.write("\n".join(rows) + "\n")
    tmp.close()
    return tmp.name


def _rules(result: ProfileResult) -> set[str]:
    return {issue.rule for issue in result.issues}


# ── CUSTOMER ─────────────────────────────────────────────────────────────
def test_customer_profiler_flags_missing_required_and_format():
    path = _write_csv([
        "first_name,last_name,email,phone",
        ",Smith,john@example.com,+971501234567",      # missing first_name
        "John,,john@example.com,+971501234567",       # missing last_name
        "John,Smith,not-an-email,+971501234567",      # bad email
        "John,Smith,john@example.com,abc",            # bad phone
        "JOHN,Smith,john@example.com,+971501234567",  # ALL_CAPS first_name
    ])
    result = CustomerProfiler().profile(path)
    assert result.row_count == 5
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "INVALID_EMAIL_FORMAT" in rules
    assert "INVALID_PHONE_FORMAT" in rules
    assert "ALL_CAPS" in rules
    Path(path).unlink()


# ── PRODUCT ──────────────────────────────────────────────────────────────
def test_product_profiler_catches_bad_barcode_and_uom():
    path = _write_csv([
        "sku,name,brand,category,uom,barcode",
        ",Headphones,Acme,Electronics,EA,6912345678901",         # missing sku
        "SKU-0001,,Acme,Electronics,EA,6912345678901",            # missing name
        "SKU-0002,Headphones,Acme,Electronics,WIDGET,69123",       # bad uom + bad barcode
        "SKU-0003,WIRELESS HEADPHONES,Acme,Electronics,EA,6912345678901",  # ALL_CAPS name
        "SKU-0004,Headphones,Acme,Electronics,KG,6912345678901",   # clean
    ])
    result = ProductProfiler().profile(path)
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "UNKNOWN_UOM" in rules
    assert "INVALID_BARCODE_FORMAT" in rules
    assert "ALL_CAPS" in rules
    Path(path).unlink()


def test_product_profiler_accepts_clean_data():
    path = _write_csv([
        "sku,name,brand,category,uom,barcode",
        "SKU-0001,Headphones,Acme Corp,Electronics,EA,6912345678901",
    ])
    result = ProductProfiler().profile(path)
    assert result.issue_count == 0
    assert result.quality_score == 100.0
    Path(path).unlink()


# ── VENDOR ───────────────────────────────────────────────────────────────
def test_vendor_profiler_flags_self_parent_and_identical_names():
    path = _write_csv([
        "source_id,legal_name,trading_name,tax_id,country,parent_vendor_id",
        "V-1,,Trading Co,TX-12345,UAE,",                   # missing legal_name
        "V-2,Acme Holdings,Acme Holdings,TX-12345,UAE,",   # legal == trading
        "V-3,Acme,Acme Trading,!!!,UAE,",                  # bad tax_id
        "V-4,Acme,Acme Trading,TX-12345,,",                # missing country
        "V-5,Acme,Acme Trading,TX-12345,UAE,V-5",          # self-parent
    ])
    result = VendorProfiler().profile(path)
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "LEGAL_TRADING_IDENTICAL" in rules
    assert "INVALID_TAX_ID_FORMAT" in rules
    assert "MISSING_COUNTRY" in rules
    assert "SELF_PARENT" in rules
    Path(path).unlink()


# ── ASSET ────────────────────────────────────────────────────────────────
def test_asset_profiler_flags_orphan_and_unknown_lifecycle():
    path = _write_csv([
        "asset_tag,description,category,lifecycle_state,location_id,assigned_to",
        ",Laptop,IT,Active,LOC-001,emp-1",                # missing tag
        "AST-0001,,IT,Active,LOC-001,emp-1",               # missing description
        "AST-0002,Laptop,IT,FUNKY,LOC-001,emp-1",          # bad lifecycle
        "AST-0003,Laptop,IT,Active,,",                     # orphan
    ])
    result = AssetProfiler().profile(path)
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "INVALID_LIFECYCLE_STATE" in rules
    assert "ORPHAN_ASSET" in rules
    Path(path).unlink()


# ── LOCATION ─────────────────────────────────────────────────────────────
def test_location_profiler_flags_bad_coordinates_and_null_island():
    path = _write_csv([
        "location_code,name,type,city,country,parent_id,latitude,longitude",
        "LOC-001,Mall Store,Store,Dubai,UAE,,25.2,55.3",         # clean
        "LOC-002,Mall Store,Store,Dubai,UAE,,200,55.3",          # latitude out of range
        "LOC-003,Mall Store,Store,Dubai,UAE,,25.2,500",          # longitude out of range
        "LOC-004,Mall Store,Store,Dubai,UAE,,abc,55.3",          # non-numeric latitude
        "LOC-005,Mall Store,Store,Dubai,UAE,,0,0",               # null island
        "LOC-006,Mall Store,Store,Dubai,UAE,LOC-006,25.2,55.3",  # self-parent
    ])
    result = LocationProfiler().profile(path)
    rules = _rules(result)
    assert "LATITUDE_OUT_OF_RANGE" in rules
    assert "LONGITUDE_OUT_OF_RANGE" in rules
    assert "INVALID_LATITUDE_FORMAT" in rules
    assert "NULL_ISLAND_PLACEHOLDER" in rules
    assert "SELF_PARENT" in rules
    Path(path).unlink()


# ── EMPLOYEE ─────────────────────────────────────────────────────────────
def test_employee_profiler_flags_self_manager_and_bad_email():
    path = _write_csv([
        "employee_id,first_name,last_name,email,manager_id,hire_date,status",
        "E-1,John,Smith,john@acme.com,E-2,2020-01-15,Active",        # clean
        ",John,Smith,john@acme.com,E-2,2020-01-15,Active",            # missing employee_id
        "E-3,John,Smith,not-an-email,E-2,2020-01-15,Active",          # bad email
        "E-4,John,Smith,john@acme.com,E-4,2020-01-15,Active",         # self manager
        "E-5,John,Smith,john@acme.com,E-2,01/15/2020,Active",         # bad date
        "E-6,John,Smith,john@acme.com,E-2,2020-01-15,Time Traveling", # unknown status
    ])
    result = EmployeeProfiler().profile(path)
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "INVALID_EMAIL_FORMAT" in rules
    assert "SELF_MANAGER" in rules
    assert "INVALID_DATE_FORMAT" in rules
    assert "INVALID_STATUS" in rules
    Path(path).unlink()


# ── COUNTERPARTY ─────────────────────────────────────────────────────────
def test_counterparty_profiler_flags_lei_and_role():
    path = _write_csv([
        "counterparty_id,legal_name,lei,is_customer,is_vendor,country,jurisdiction",
        "CP-1,Acme,529900T8BM49AURSDO55,true,false,UAE,DIFC",     # clean
        ",Acme,529900T8BM49AURSDO55,true,false,UAE,DIFC",          # missing id
        "CP-2,,529900T8BM49AURSDO55,true,false,UAE,DIFC",          # missing legal_name
        "CP-3,Acme,SHORT-LEI,true,false,UAE,DIFC",                 # bad LEI
        "CP-4,Acme,529900T8BM49AURSDO55,false,false,UAE,DIFC",     # role unflagged
        "CP-5,Acme,529900T8BM49AURSDO55,true,false,,DIFC",         # missing country
        "CP-6,Acme,529900T8BM49AURSDO55,true,false,UAE,",          # missing jurisdiction
    ])
    result = CounterpartyProfiler().profile(path)
    rules = _rules(result)
    assert "MISSING_REQUIRED" in rules
    assert "INVALID_LEI_FORMAT" in rules
    assert "ROLE_UNFLAGGED" in rules
    assert "MISSING_COUNTRY" in rules
    assert "MISSING_JURISDICTION" in rules
    Path(path).unlink()


# ── PROFILE RESULT SHAPE ─────────────────────────────────────────────────
def test_profile_result_summary_shape():
    path = _write_csv([
        "first_name,last_name,email,phone",
        "John,Smith,john@example.com,+971501234567",  # one clean row
    ])
    result = CustomerProfiler().profile(path)
    summary = result.summary()
    assert summary["domain"] == "customer"
    assert summary["rows"] == 1
    assert summary["issues"] == 0
    assert summary["quality_score_pct"] == 100.0
    assert summary["by_rule"] == {}
    Path(path).unlink()


@pytest.mark.parametrize("profiler_cls,domain", [
    (CustomerProfiler, "customer"),
    (ProductProfiler, "product"),
    (VendorProfiler, "vendor"),
    (AssetProfiler, "asset"),
    (LocationProfiler, "location"),
    (EmployeeProfiler, "employee"),
    (CounterpartyProfiler, "counterparty"),
])
def test_profiler_handles_empty_file(profiler_cls, domain):
    """Profiler tolerates a header-only CSV without crashing."""
    path = _write_csv(["col_a,col_b"])
    result = profiler_cls().profile(path)
    assert result.domain == domain
    assert result.row_count == 0
    assert result.quality_score == 0.0  # documented behaviour for zero rows
    Path(path).unlink()
