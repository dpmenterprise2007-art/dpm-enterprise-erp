import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("gstin", name="uq_customers_gstin"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(180))
    gstin: Mapped[str | None] = mapped_column(String(15), index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(254))
    billing_address: Mapped[str | None] = mapped_column(Text)
    shipping_address: Mapped[str | None] = mapped_column(Text)
    state_code: Mapped[str | None] = mapped_column(String(2))
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (UniqueConstraint("gstin", name="uq_vendors_gstin"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(180))
    gstin: Mapped[str | None] = mapped_column(String(15), index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(254))
    address: Mapped[str | None] = mapped_column(Text)
    state_code: Mapped[str | None] = mapped_column(String(2))
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False, default="product")
    hsn_sac: Mapped[str | None] = mapped_column(String(8))
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="NOS")
    sale_rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    purchase_rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class InvoiceSequence(Base):
    __tablename__ = "invoice_sequences"

    financial_year: Mapped[str] = mapped_column(String(7), primary_key=True)
    last_number: Mapped[int] = mapped_column(nullable=False, default=0)


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("invoice_number", name="uq_invoices_invoice_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    financial_year: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(180), nullable=False)
    customer_gstin: Mapped[str | None] = mapped_column(String(15))
    customer_address: Mapped[str | None] = mapped_column(Text)
    place_of_supply: Mapped[str] = mapped_column(String(2), nullable=False)
    company_state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    taxable_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cgst_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    sgst_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    igst_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    hsn_sac: Mapped[str | None] = mapped_column(String(8))
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="NOS")
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    taxable_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    invoice: Mapped["Invoice"] = relationship(back_populates="lines")
