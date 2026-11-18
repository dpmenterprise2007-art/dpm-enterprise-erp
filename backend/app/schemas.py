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


class InvoiceLineInput(BaseModel):
    item_id: uuid.UUID | None = None
    description: str = Field(min_length=1, max_length=240)
    hsn_sac: str | None = Field(default=None, max_length=8)
    unit: str = Field(default="NOS", max_length=20)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)
    rate: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=18, decimal_places=2)
    gst_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, max_digits=5, decimal_places=2)


class InvoiceCreate(BaseModel):
    customer_id: uuid.UUID
    invoice_date: datetime
    place_of_supply: str = Field(pattern=r"^[0-9]{2}$")
    company_state_code: str = Field(pattern=r"^[0-9]{2}$")
    notes: str | None = None
    lines: list[InvoiceLineInput] = Field(min_length=1, max_length=100)


class InvoiceLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    item_id: uuid.UUID | None
    description: str
    hsn_sac: str | None
    unit: str
    quantity: Decimal
    rate: Decimal
    discount_amount: Decimal
    taxable_value: Decimal
    gst_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    line_total: Decimal


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    invoice_number: str | None
    status: str
    invoice_date: datetime
    financial_year: str
    customer_id: uuid.UUID
    customer_name: str
    customer_gstin: str | None
    customer_address: str | None
    place_of_supply: str
    company_state_code: str
    subtotal: Decimal
    discount_total: Decimal
    taxable_total: Decimal
    cgst_total: Decimal
    sgst_total: Decimal
    igst_total: Decimal
    grand_total: Decimal
    notes: str | None
    created_at: datetime
    posted_at: datetime | None
    lines: list[InvoiceLineRead]


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=12, max_length=256)
    role: Literal["admin", "staff"] = "staff"


class LeadCreate(BaseModel):
    contact_name: str = Field(min_length=1, max_length=160)
    company_name: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    source: str = Field(default="manual", min_length=1, max_length=60)
    requirement: str | None = None
    estimated_value: Decimal = Field(default=Decimal("0.00"), ge=0)
    follow_up_at: datetime | None = None


class LeadUpdate(BaseModel):
    contact_name: str | None = Field(default=None, min_length=1, max_length=160)
    company_name: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    source: str | None = Field(default=None, min_length=1, max_length=60)
    requirement: str | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0)
    status: Literal["new", "contacted", "qualified", "proposal", "won", "lost"] | None = None
    follow_up_at: datetime | None = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    contact_name: str
    company_name: str | None
    phone: str | None
    email: EmailStr | None
    source: str
    requirement: str | None
    estimated_value: Decimal
    status: str
    follow_up_at: datetime | None
    score: int
    created_at: datetime
    updated_at: datetime
