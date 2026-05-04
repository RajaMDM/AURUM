"""
Integration tests for the AURUM FastAPI runtime.

Uses Starlette's TestClient (synchronous, no real network) to exercise
each endpoint with sample CSVs constructed inline.
"""
from __future__ import annotations
import io

import pytest
from fastapi.testclient import TestClient

from runtimes.api.main import app

client = TestClient(app)


CUSTOMER_CSV = (
    "first_name,last_name,email,phone\n"
    "John,Smith,john@acme.com,+971501234567\n"
    "Jane,Doe,not-an-email,+971502345678\n"
    "JIM,Doe,jim@acme.com,abc\n"  # ALL_CAPS + bad phone
)

PRODUCT_CSV = (
    "sku,name,brand,category,uom,barcode\n"
    "SKU-0001,Headphones,Acme Corp,Electronics,EA,6912345678901\n"
    "SKU-0002,Headphones,Acme Corp,Electronics,WIDGET,69123\n"  # bad uom + bad barcode
)


def _csv_payload(name: str, csv: str) -> dict:
    return {"file": (name, io.BytesIO(csv.encode("utf-8")), "text/csv")}


# ── meta endpoints ────────────────────────────────────────────────────
def test_root_returns_metadata():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "AURUM"
    assert body["stages"] == ["ASSAY", "UNEARTH", "REFINE", "UNFURL", "MARK"]


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_domains_lists_seven():
    r = client.get("/domains")
    assert r.status_code == 200
    assert set(r.json()["domains"]) == {
        "customer", "product", "vendor", "asset",
        "location", "employee", "counterparty",
    }


# ── assay ─────────────────────────────────────────────────────────────
def test_assay_endpoint_returns_schema():
    r = client.post(
        "/assay",
        files=_csv_payload("customers.csv", CUSTOMER_CSV),
        params={"source_name": "TEST_SRC"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "TEST_SRC"
    assert body["row_count"] == 3
    field_names = [f["field"] for f in body["fields"]]
    assert "first_name" in field_names
    assert "email" in field_names


def test_assay_rejects_non_csv():
    r = client.post(
        "/assay",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 400
    assert "csv" in r.json()["detail"].lower()


def test_assay_rejects_empty_file():
    r = client.post(
        "/assay",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
    )
    assert r.status_code == 400


# ── unearth ───────────────────────────────────────────────────────────
def test_unearth_customer_runs_profiler():
    r = client.post("/unearth/customer", files=_csv_payload("customers.csv", CUSTOMER_CSV))
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "customer"
    assert body["rows"] == 3
    rules = {issue["rule"] for issue in body["issues"]}
    assert "INVALID_EMAIL_FORMAT" in rules
    assert "INVALID_PHONE_FORMAT" in rules
    assert "ALL_CAPS" in rules


def test_unearth_product_runs_profiler():
    r = client.post("/unearth/product", files=_csv_payload("products.csv", PRODUCT_CSV))
    assert r.status_code == 200
    body = r.json()
    rules = {issue["rule"] for issue in body["issues"]}
    assert "UNKNOWN_UOM" in rules


def test_unearth_unknown_domain_returns_404():
    r = client.post("/unearth/martian", files=_csv_payload("x.csv", CUSTOMER_CSV))
    assert r.status_code == 404
    assert "Unknown domain" in r.json()["detail"]


def test_unearth_domain_is_case_insensitive():
    r = client.post("/unearth/CUSTOMER", files=_csv_payload("c.csv", CUSTOMER_CSV))
    assert r.status_code == 200
    assert r.json()["domain"] == "customer"


# ── anomaly ───────────────────────────────────────────────────────────
def test_anomaly_endpoint_returns_summary():
    rows = ["first_name,last_name,email"]
    for i in range(15):
        rows.append(f"John{i},Smith{i},john{i}@acme.com")
    rows.append(",,")  # outlier
    csv = "\n".join(rows) + "\n"

    r = client.post(
        "/anomaly",
        files=_csv_payload("customers.csv", csv),
        params={"domain": "customer", "contamination": 0.1},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "customer"
    assert body["rows"] == 16
    assert body["flagged"] >= 1                 # count from summary
    assert isinstance(body["flagged_rows"], list)
    assert len(body["flagged_rows"]) == body["flagged"]


def test_anomaly_contamination_bounds_enforced():
    r = client.post(
        "/anomaly",
        files=_csv_payload("c.csv", CUSTOMER_CSV),
        params={"contamination": 0.9},  # above 0.5 ceiling
    )
    assert r.status_code == 422  # FastAPI validation error


# ── OpenAPI surface ───────────────────────────────────────────────────
def test_openapi_schema_includes_all_routes():
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"].keys())
    assert "/" in paths
    assert "/health" in paths
    assert "/domains" in paths
    assert "/assay" in paths
    assert "/anomaly" in paths
    assert "/unearth/{domain}" in paths
