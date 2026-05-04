"""
UNEARTH Domain Profiler
Runs completeness, consistency, and format checks across a domain dataset.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import pandas as pd
import re


@dataclass
class DQIssue:
    row_index: int
    field: str
    rule: str
    value: Any
    severity: str = "WARNING"


@dataclass
class ProfileResult:
    domain: str
    row_count: int
    issues: list[DQIssue] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def quality_score(self) -> float:
        if self.row_count == 0:
            return 0.0
        clean_rows = self.row_count - len({i.row_index for i in self.issues})
        return round(clean_rows / self.row_count * 100, 1)

    def summary(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "rows": self.row_count,
            "issues": self.issue_count,
            "quality_score_pct": self.quality_score,
            "by_rule": self._by_rule(),
        }

    def _by_rule(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in self.issues:
            counts[issue.rule] = counts.get(issue.rule, 0) + 1
        return counts


class CustomerProfiler:
    """DQ rules specific to the Customer domain."""

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)
    PHONE_RE = re.compile(r"^[\+\d\-\(\)\s]{7,20}$")

    def profile(self, path: str) -> ProfileResult:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        result = ProfileResult(domain="customer", row_count=len(df))

        for i, row in df.iterrows():
            # Completeness
            for req in ["first_name", "last_name"]:
                if req in df.columns and row.get(req, "").strip() == "":
                    result.issues.append(DQIssue(i, req, "MISSING_REQUIRED", "", "ERROR"))

            # Email format
            email = row.get("email", "").strip()
            if email and not self.EMAIL_RE.match(email):
                result.issues.append(DQIssue(i, "email", "INVALID_EMAIL_FORMAT", email))

            # Phone format
            phone = row.get("phone", "").strip()
            if phone and not self.PHONE_RE.match(phone):
                result.issues.append(DQIssue(i, "phone", "INVALID_PHONE_FORMAT", phone))

            # Case consistency check
            fname = row.get("first_name", "")
            if fname and fname == fname.upper() and len(fname) > 2:
                result.issues.append(DQIssue(i, "first_name", "ALL_CAPS", fname, "WARNING"))

        return result


def _read_csv(path: str) -> pd.DataFrame:
    """Shared CSV reader — string typing, no NA coercion."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


class ProductProfiler:
    """DQ rules specific to the Product domain.

    Expected columns: sku, name, brand, category, uom, barcode.
    Tolerates missing columns — rules only fire when the field exists.
    """

    BARCODE_RE = re.compile(r"^\d{8}$|^\d{12}$|^\d{13}$|^\d{14}$")  # EAN-8/UPC-A/EAN-13/GTIN-14
    SKU_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{2,}$")
    KNOWN_UOMS = {"EA", "PC", "PCS", "KG", "G", "L", "ML", "M", "CM", "BOX", "PACK", "CASE", "DOZ"}

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="product", row_count=len(df))

        for i, row in df.iterrows():
            sku = row.get("sku", "").strip()
            name = row.get("name", "").strip()
            brand = row.get("brand", "").strip()
            uom = row.get("uom", "").strip()
            barcode = row.get("barcode", "").strip()

            if "sku" in df.columns and not sku:
                result.issues.append(DQIssue(i, "sku", "MISSING_REQUIRED", "", "ERROR"))
            elif sku and not self.SKU_RE.match(sku):
                result.issues.append(DQIssue(i, "sku", "INVALID_SKU_FORMAT", sku, "WARNING"))

            if "name" in df.columns and not name:
                result.issues.append(DQIssue(i, "name", "MISSING_REQUIRED", "", "ERROR"))
            elif name and name == name.upper() and len(name) > 3:
                result.issues.append(DQIssue(i, "name", "ALL_CAPS", name, "WARNING"))

            if barcode and not self.BARCODE_RE.match(barcode):
                result.issues.append(DQIssue(i, "barcode", "INVALID_BARCODE_FORMAT", barcode, "WARNING"))

            if uom and uom.upper() not in self.KNOWN_UOMS:
                result.issues.append(DQIssue(i, "uom", "UNKNOWN_UOM", uom, "WARNING"))

            if brand and brand == brand.upper() and len(brand) > 3:
                result.issues.append(DQIssue(i, "brand", "ALL_CAPS", brand, "WARNING"))

        return result


class VendorProfiler:
    """DQ rules specific to the Vendor domain.

    Expected columns: legal_name, trading_name, tax_id, country, parent_vendor_id, source_id.
    Tax ID format varies by jurisdiction; AURUM treats it as alphanumeric 5-20 chars.
    """

    TAX_ID_RE = re.compile(r"^[A-Za-z0-9\-]{5,20}$")
    COUNTRY_RE = re.compile(r"^[A-Za-z\s]{2,40}$")

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="vendor", row_count=len(df))

        for i, row in df.iterrows():
            legal = row.get("legal_name", "").strip()
            trading = row.get("trading_name", "").strip()
            tax_id = row.get("tax_id", "").strip()
            country = row.get("country", "").strip()
            parent = row.get("parent_vendor_id", "").strip()
            source_id = row.get("source_id", "").strip()

            if "legal_name" in df.columns and not legal:
                result.issues.append(DQIssue(i, "legal_name", "MISSING_REQUIRED", "", "ERROR"))

            if tax_id and not self.TAX_ID_RE.match(tax_id):
                result.issues.append(DQIssue(i, "tax_id", "INVALID_TAX_ID_FORMAT", tax_id, "WARNING"))

            if "country" in df.columns and not country:
                result.issues.append(DQIssue(i, "country", "MISSING_COUNTRY", "", "WARNING"))
            elif country and not self.COUNTRY_RE.match(country):
                result.issues.append(DQIssue(i, "country", "INVALID_COUNTRY_FORMAT", country, "WARNING"))

            if legal and trading and legal.lower() == trading.lower():
                result.issues.append(DQIssue(i, "trading_name", "LEGAL_TRADING_IDENTICAL", trading, "WARNING"))

            if parent and source_id and parent == source_id:
                result.issues.append(DQIssue(i, "parent_vendor_id", "SELF_PARENT", parent, "ERROR"))

        return result


class AssetProfiler:
    """DQ rules specific to the Asset domain.

    Expected columns: asset_tag, description, category, lifecycle_state, location_id, assigned_to.
    Asset records that are neither located nor assigned are operationally orphaned.
    """

    TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-\s]{2,}$")
    KNOWN_LIFECYCLES = {
        "active", "in_use", "in use", "available", "stored",
        "maintenance", "under maintenance", "repair",
        "retired", "disposed", "decommissioned", "lost"
    }

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="asset", row_count=len(df))

        for i, row in df.iterrows():
            tag = row.get("asset_tag", "").strip()
            desc = row.get("description", "").strip()
            lifecycle = row.get("lifecycle_state", "").strip()
            location_id = row.get("location_id", "").strip()
            assigned = row.get("assigned_to", "").strip()

            if "asset_tag" in df.columns and not tag:
                result.issues.append(DQIssue(i, "asset_tag", "MISSING_REQUIRED", "", "ERROR"))
            elif tag and not self.TAG_RE.match(tag):
                result.issues.append(DQIssue(i, "asset_tag", "INVALID_TAG_FORMAT", tag, "WARNING"))

            if "description" in df.columns and not desc:
                result.issues.append(DQIssue(i, "description", "MISSING_REQUIRED", "", "ERROR"))

            if lifecycle and lifecycle.lower() not in self.KNOWN_LIFECYCLES:
                result.issues.append(DQIssue(i, "lifecycle_state", "INVALID_LIFECYCLE_STATE", lifecycle, "WARNING"))

            if "location_id" in df.columns and "assigned_to" in df.columns and not location_id and not assigned:
                result.issues.append(DQIssue(i, "location_id", "ORPHAN_ASSET", "", "WARNING"))

        return result


class LocationProfiler:
    """DQ rules specific to the Location domain.

    Expected columns: location_code, name, type, city, country, parent_id,
    latitude, longitude.
    Latitude must be in [-90, 90]; longitude in [-180, 180].
    The (0, 0) coordinate is flagged as a likely placeholder (Null Island).
    """

    CODE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-\s]{2,}$")

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="location", row_count=len(df))

        for i, row in df.iterrows():
            code = row.get("location_code", "").strip()
            name = row.get("name", "").strip()
            country = row.get("country", "").strip()
            parent = row.get("parent_id", "").strip()
            lat_raw = row.get("latitude", "").strip()
            lon_raw = row.get("longitude", "").strip()

            if "location_code" in df.columns and not code:
                result.issues.append(DQIssue(i, "location_code", "MISSING_REQUIRED", "", "ERROR"))
            elif code and not self.CODE_RE.match(code):
                result.issues.append(DQIssue(i, "location_code", "INVALID_CODE_FORMAT", code, "WARNING"))

            if "name" in df.columns and not name:
                result.issues.append(DQIssue(i, "name", "MISSING_REQUIRED", "", "ERROR"))

            if "country" in df.columns and not country:
                result.issues.append(DQIssue(i, "country", "MISSING_COUNTRY", "", "WARNING"))

            lat = self._safe_float(lat_raw)
            lon = self._safe_float(lon_raw)
            if lat_raw and lat is None:
                result.issues.append(DQIssue(i, "latitude", "INVALID_LATITUDE_FORMAT", lat_raw, "ERROR"))
            elif lat is not None and not -90 <= lat <= 90:
                result.issues.append(DQIssue(i, "latitude", "LATITUDE_OUT_OF_RANGE", lat_raw, "ERROR"))

            if lon_raw and lon is None:
                result.issues.append(DQIssue(i, "longitude", "INVALID_LONGITUDE_FORMAT", lon_raw, "ERROR"))
            elif lon is not None and not -180 <= lon <= 180:
                result.issues.append(DQIssue(i, "longitude", "LONGITUDE_OUT_OF_RANGE", lon_raw, "ERROR"))

            if lat is not None and lon is not None and lat == 0 and lon == 0:
                result.issues.append(DQIssue(i, "latitude", "NULL_ISLAND_PLACEHOLDER", "0,0", "WARNING"))

            if parent and code and parent == code:
                result.issues.append(DQIssue(i, "parent_id", "SELF_PARENT", parent, "ERROR"))

        return result

    @staticmethod
    def _safe_float(value: str) -> float | None:
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None


class EmployeeProfiler:
    """DQ rules specific to the Employee domain.

    Expected columns: employee_id, first_name, last_name, email, manager_id,
    department, hire_date, status.
    A self-referential manager (manager_id == employee_id) is a hierarchy cycle.
    """

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)
    DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    KNOWN_STATUSES = {"active", "on leave", "leave", "terminated", "retired", "suspended"}

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="employee", row_count=len(df))

        for i, row in df.iterrows():
            emp_id = row.get("employee_id", "").strip()
            fname = row.get("first_name", "").strip()
            lname = row.get("last_name", "").strip()
            email = row.get("email", "").strip()
            manager = row.get("manager_id", "").strip()
            hire_date = row.get("hire_date", "").strip()
            status = row.get("status", "").strip()

            for field_name, value in [("employee_id", emp_id), ("first_name", fname), ("last_name", lname)]:
                if field_name in df.columns and not value:
                    result.issues.append(DQIssue(i, field_name, "MISSING_REQUIRED", "", "ERROR"))

            if email and not self.EMAIL_RE.match(email):
                result.issues.append(DQIssue(i, "email", "INVALID_EMAIL_FORMAT", email, "WARNING"))

            if manager and emp_id and manager == emp_id:
                result.issues.append(DQIssue(i, "manager_id", "SELF_MANAGER", manager, "ERROR"))

            if hire_date and not self.DATE_RE.match(hire_date):
                result.issues.append(DQIssue(i, "hire_date", "INVALID_DATE_FORMAT", hire_date, "WARNING"))

            if status and status.lower() not in self.KNOWN_STATUSES:
                result.issues.append(DQIssue(i, "status", "INVALID_STATUS", status, "WARNING"))

        return result


class CounterpartyProfiler:
    """DQ rules specific to the Counterparty domain.

    Expected columns: counterparty_id, legal_name, lei, is_customer, is_vendor,
    country, jurisdiction.
    LEI (Legal Entity Identifier) is 20 alphanumeric chars per ISO 17442.
    A counterparty with neither customer nor vendor role is incomplete.
    """

    LEI_RE = re.compile(r"^[A-Z0-9]{20}$")
    BOOL_TRUTHY = {"true", "1", "yes", "y", "t"}
    BOOL_FALSY = {"false", "0", "no", "n", "f", ""}

    def profile(self, path: str) -> ProfileResult:
        df = _read_csv(path)
        result = ProfileResult(domain="counterparty", row_count=len(df))

        for i, row in df.iterrows():
            cp_id = row.get("counterparty_id", "").strip()
            legal = row.get("legal_name", "").strip()
            lei = row.get("lei", "").strip()
            is_customer = row.get("is_customer", "").strip().lower()
            is_vendor = row.get("is_vendor", "").strip().lower()
            country = row.get("country", "").strip()
            jurisdiction = row.get("jurisdiction", "").strip()

            if "counterparty_id" in df.columns and not cp_id:
                result.issues.append(DQIssue(i, "counterparty_id", "MISSING_REQUIRED", "", "ERROR"))

            if "legal_name" in df.columns and not legal:
                result.issues.append(DQIssue(i, "legal_name", "MISSING_REQUIRED", "", "ERROR"))

            if lei and not self.LEI_RE.match(lei):
                result.issues.append(DQIssue(i, "lei", "INVALID_LEI_FORMAT", lei, "WARNING"))

            if "is_customer" in df.columns and "is_vendor" in df.columns:
                cust_truthy = is_customer in self.BOOL_TRUTHY
                vend_truthy = is_vendor in self.BOOL_TRUTHY
                if not cust_truthy and not vend_truthy:
                    result.issues.append(DQIssue(i, "is_customer", "ROLE_UNFLAGGED", "", "WARNING"))

            if "country" in df.columns and not country:
                result.issues.append(DQIssue(i, "country", "MISSING_COUNTRY", "", "WARNING"))

            if "jurisdiction" in df.columns and not jurisdiction:
                result.issues.append(DQIssue(i, "jurisdiction", "MISSING_JURISDICTION", "", "WARNING"))

        return result
