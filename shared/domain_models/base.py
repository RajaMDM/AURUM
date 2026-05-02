"""
Base domain model for all AURUM records.
Every domain entity inherits from BaseRecord.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


class DomainType(str, Enum):
    CUSTOMER = "customer"
    PRODUCT = "product"
    VENDOR = "vendor"
    ASSET = "asset"
    LOCATION = "location"
    EMPLOYEE = "employee"
    COUNTERPARTY = "counterparty"


class RecordSource(BaseModel):
    system_id: str
    system_name: str
    record_id: str
    loaded_at: datetime = Field(default_factory=datetime.utcnow)
    raw_attributes: dict[str, Any] = Field(default_factory=dict)


class BaseRecord(BaseModel):
    """Universal base for all AURUM domain records."""
    aurum_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: DomainType
    sources: list[RecordSource] = Field(default_factory=list)
    is_golden: bool = False
    trust_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    attributes: dict[str, Any] = Field(default_factory=dict)

    def add_source(self, source: RecordSource) -> None:
        self.sources.append(source)
        self.updated_at = datetime.utcnow()

    def mark_golden(self, trust_score: float) -> None:
        self.is_golden = True
        self.trust_score = trust_score
        self.updated_at = datetime.utcnow()


class CustomerRecord(BaseRecord):
    domain: DomainType = DomainType.CUSTOMER
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    date_of_birth: Optional[str] = None


class ProductRecord(BaseRecord):
    domain: DomainType = DomainType.PRODUCT
    sku: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    uom: Optional[str] = None
    barcode: Optional[str] = None


class VendorRecord(BaseRecord):
    domain: DomainType = DomainType.VENDOR
    legal_name: Optional[str] = None
    trading_name: Optional[str] = None
    tax_id: Optional[str] = None
    country: Optional[str] = None
    parent_vendor_id: Optional[str] = None


class AssetRecord(BaseRecord):
    domain: DomainType = DomainType.ASSET
    asset_tag: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    lifecycle_state: Optional[str] = None
    location_id: Optional[str] = None
    assigned_to: Optional[str] = None


class LocationRecord(BaseRecord):
    domain: DomainType = DomainType.LOCATION
    location_code: Optional[str] = None
    name: Optional[str] = None
    location_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    parent_location_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
