"""
AURUM FastAPI Runtime
HTTP surface for the pipeline. Mounts the same modules the demo, CLI, and
MCP server use, so behaviour is identical across runtimes.

Run locally:

    uvicorn runtimes.api.main:app --reload --port 8000

OpenAPI docs:    http://localhost:8000/docs
ReDoc:           http://localhost:8000/redoc

Endpoints accept CSV uploads via multipart form data. Server-side file
paths are NOT accepted by default — that would invite path traversal on
any deployment that exposes this beyond localhost.
"""
from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

# Make repo root importable when invoked via uvicorn.
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assay.schema_inspector.inspector import SchemaInspector  # noqa: E402
from unearth.anomaly import AnomalyDetector  # noqa: E402
from unearth.profiler.domain_profiler import (  # noqa: E402
    AssetProfiler,
    CounterpartyProfiler,
    CustomerProfiler,
    EmployeeProfiler,
    LocationProfiler,
    ProductProfiler,
    VendorProfiler,
)

logger = logging.getLogger(__name__)

VERSION = "0.1.3"

PROFILERS = {
    "customer":     CustomerProfiler,
    "product":      ProductProfiler,
    "vendor":       VendorProfiler,
    "asset":        AssetProfiler,
    "location":     LocationProfiler,
    "employee":     EmployeeProfiler,
    "counterparty": CounterpartyProfiler,
}

app = FastAPI(
    title="AURUM",
    version=VERSION,
    description=(
        "Master Data Management reference pipeline — HTTP surface.\n\n"
        "Endpoints accept CSV uploads via multipart form. Use `/docs` for "
        "interactive OpenAPI exploration."
    ),
)


@app.get("/", tags=["meta"])
def root() -> dict[str, Any]:
    """Landing endpoint — pipeline metadata and links."""
    return {
        "name": "AURUM",
        "version": VERSION,
        "tagline": "Raw data in. Hallmarked golden records out.",
        "stages": ["ASSAY", "UNEARTH", "REFINE", "UNFURL", "MARK"],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "version": VERSION}


@app.get("/domains", tags=["meta"])
def domains() -> dict[str, list[str]]:
    """List the 7 AURUM domains and which have a profiler ready."""
    return {"domains": sorted(PROFILERS.keys())}


@app.post("/assay", tags=["assay"])
async def assay_endpoint(
    file: UploadFile = File(..., description="CSV file to inspect"),
    source_name: str = Query("api_source", description="Logical source-system name."),
) -> dict[str, Any]:
    """ASSAY — inspect a CSV: types, nulls, cardinality, samples."""
    path = await _save_upload(file)
    try:
        inspector = SchemaInspector(source_name=source_name)
        return inspector.inspect(path)
    finally:
        path.unlink(missing_ok=True)


@app.post("/unearth/{domain}", tags=["unearth"])
async def unearth_endpoint(
    domain: str,
    file: UploadFile = File(..., description="Domain CSV to profile"),
) -> dict[str, Any]:
    """UNEARTH — run the DQ profiler for the given domain."""
    domain = domain.lower()
    profiler_cls = PROFILERS.get(domain)
    if profiler_cls is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown domain '{domain}'. Valid: {sorted(PROFILERS.keys())}",
        )

    path = await _save_upload(file)
    try:
        result = profiler_cls().profile(str(path))
        summary = result.summary()
        return {
            **summary,
            "issues": [
                {
                    "row": i.row_index,
                    "field": i.field,
                    "rule": i.rule,
                    "value": i.value,
                    "severity": i.severity,
                }
                for i in result.issues
            ],
        }
    finally:
        path.unlink(missing_ok=True)


@app.post("/anomaly", tags=["unearth"])
async def anomaly_endpoint(
    file: UploadFile = File(..., description="CSV to scan for anomalies"),
    domain: str = Query("generic", description="Cosmetic label for the result."),
    contamination: float = Query(0.1, ge=0.001, le=0.5, description="Expected fraction of anomalous rows."),
) -> dict[str, Any]:
    """UNEARTH — Isolation Forest anomaly detection on an arbitrary CSV."""
    path = await _save_upload(file)
    try:
        detector = AnomalyDetector(contamination=contamination)
        result = detector.detect(str(path), domain=domain)
        return {
            **result.summary(),
            "flagged_rows": [f.to_dict() for f in result.flagged],
        }
    finally:
        path.unlink(missing_ok=True)


async def _save_upload(file: UploadFile) -> Path:
    """Persist an UploadFile to a tempfile so pandas can read it."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv uploads are accepted.")

    suffix = Path(file.filename).suffix or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        tmp.write(content)
        tmp.flush()
    finally:
        tmp.close()
    return Path(tmp.name)
