import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")


class CustomerInput(BaseModel):
    display_name: str = Field(min_length=1, max_length=180)
    legal_name: str | None = Field(default=None, max_length=180)
    gstin: str | None = Field(default=None, min_length=15, max_length=15)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    state_code: str | None = Field(default=None, pattern=r"^[0-9]{2}$")
    opening_balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        value = value.upper()
        if not GSTIN_PATTERN.fullmatch(value):
            raise ValueError("Invalid GSTIN format")
        return value


class CustomerRead(CustomerInput):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorInput(BaseModel):
    display_name: str = Field(min_length=1, max_length=180)
    legal_name: str | None = Field(default=None, max_length=180)
    gstin: str | None = Field(default=None, min_length=15, max_length=15)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    state_code: str | None = Field(default=None, pattern=r"^[0-9]{2}$")
    opening_balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        value = value.upper()
        if not GSTIN_PATTERN.fullmatch(value):
            raise ValueError("Invalid GSTIN format")
        return value


class VendorRead(VendorInput):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ItemInput(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    item_type: Literal["product", "service"] = "product"
    hsn_sac: str | None = Field(default=None, max_length=8)
    unit: str = Field(default="NOS", max_length=20)
    sale_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    purchase_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    gst_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)


class ItemRead(ItemInput):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
