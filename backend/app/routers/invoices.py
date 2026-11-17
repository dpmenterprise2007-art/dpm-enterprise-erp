from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.security import get_current_user
from app.models import Customer, Invoice, InvoiceLine, InvoiceSequence, Item
from app.schemas import InvoiceCreate, InvoiceRead

router = APIRouter(prefix="/api/v1", tags=["Sales Invoices"], dependencies=[Depends(get_current_user)])
CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def financial_year(value: datetime) -> str:
    year = value.year if value.month >= 4 else value.year - 1
    return f"{year % 100:02d}-{(year + 1) % 100:02d}"


@router.post("/invoices", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    customer = db.get(Customer, payload.customer_id)
    if not customer or not customer.is_active:
        raise HTTPException(status_code=404, detail="Active customer not found")
    if customer.state_code and customer.state_code != payload.place_of_supply:
        raise HTTPException(status_code=422, detail="Place of supply does not match the customer's registered state. Verify the transaction before invoicing.")

    subtotal = ZERO
    discount_total = ZERO
    taxable_total = ZERO
    cgst_total = ZERO
    sgst_total = ZERO
    igst_total = ZERO
    prepared_lines = []

    for line in payload.lines:
        if line.item_id:
            item = db.get(Item, line.item_id)
            if not item or not item.is_active:
                raise HTTPException(status_code=404, detail=f"Active item not found: {line.item_id}")
        gross = money(line.quantity * line.rate)
        discount = money(line.discount_amount)
        if discount > gross:
            raise HTTPException(status_code=422, detail=f"Discount exceeds line value for {line.description}")
        taxable = money(gross - discount)
        tax = money(taxable * line.gst_rate / Decimal("100"))
        cgst = ZERO
        sgst = ZERO
        igst = ZERO
        if payload.company_state_code == payload.place_of_supply:
            cgst = money(tax / Decimal("2"))
            sgst = money(tax - cgst)
        else:
            igst = tax
        line_total = money(taxable + cgst + sgst + igst)

        subtotal += gross
        discount_total += discount
        taxable_total += taxable
        cgst_total += cgst
        sgst_total += sgst
        igst_total += igst
        prepared_lines.append({
            "item_id": line.item_id,
            "description": line.description,
            "hsn_sac": line.hsn_sac,
            "unit": line.unit,
            "quantity": line.quantity,
            "rate": line.rate,
            "discount_amount": discount,
            "taxable_value": taxable,
            "gst_rate": line.gst_rate,
            "cgst_amount": cgst,
            "sgst_amount": sgst,
            "igst_amount": igst,
            "line_total": line_total,
        })

    subtotal = money(subtotal)
    discount_total = money(discount_total)
    taxable_total = money(taxable_total)
    cgst_total = money(cgst_total)
    sgst_total = money(sgst_total)
    igst_total = money(igst_total)
    grand_total = money(taxable_total + cgst_total + sgst_total + igst_total)
    fy = financial_year(payload.invoice_date)

    invoice = Invoice(
        status="draft",
        invoice_date=payload.invoice_date,
        financial_year=fy,
        customer_id=customer.id,
        customer_name=customer.legal_name or customer.display_name,
        customer_gstin=customer.gstin,
        customer_address=customer.billing_address,
        place_of_supply=payload.place_of_supply,
        company_state_code=payload.company_state_code,
        subtotal=subtotal,
        discount_total=discount_total,
        taxable_total=taxable_total,
        cgst_total=cgst_total,
        sgst_total=sgst_total,
        igst_total=igst_total,
        grand_total=grand_total,
        notes=payload.notes,
        lines=[InvoiceLine(**line) for line in prepared_lines],
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices", response_model=list[InvoiceRead])
def list_invoices(db: Session = Depends(get_db)):
    query = select(Invoice).options(selectinload(Invoice.lines)).order_by(Invoice.created_at.desc()).limit(200)
    return db.scalars(query).all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    query = select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice_id)
    invoice = db.scalar(query)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/issue", response_model=InvoiceRead)
def issue_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    invoice = db.scalar(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice_id).with_for_update())
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status == "issued":
        return invoice
    if invoice.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft invoices can be issued")

    sequence_stmt = insert(InvoiceSequence).values(financial_year=invoice.financial_year, last_number=1)
    sequence_stmt = sequence_stmt.on_conflict_do_update(
        index_elements=[InvoiceSequence.financial_year],
        set_={"last_number": InvoiceSequence.last_number + 1},
    ).returning(InvoiceSequence.last_number)
    next_number = db.scalar(sequence_stmt)
    invoice.invoice_number = f"DPM/{invoice.financial_year}/{next_number:04d}"
    invoice.status = "issued"
    invoice.posted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: UUID, db: Session = Depends(get_db)):
    invoice = db.scalar(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice_id))
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status != "issued":
        raise HTTPException(status_code=409, detail="Issue the invoice before generating its tax invoice PDF")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("DPM ENTERPRISE PRIVATE LIMITED", styles["Title"]),
        Paragraph("TAX INVOICE", styles["Heading2"]),
        Paragraph(f"Invoice: {invoice.invoice_number} &nbsp;&nbsp; Date: {invoice.invoice_date:%d-%m-%Y}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"<b>Bill To:</b> {invoice.customer_name}", styles["Normal"]),
        Paragraph(f"GSTIN: {invoice.customer_gstin or 'Not provided'}", styles["Normal"]),
        Paragraph(f"Address: {invoice.customer_address or 'Not provided'}", styles["Normal"]),
        Paragraph(f"Place of Supply: {invoice.place_of_supply}", styles["Normal"]),
        Spacer(1, 14),
    ]
    rows = [["Description", "HSN/SAC", "Qty", "Rate", "Taxable", "GST %", "Line Total"]]
    for line in invoice.lines:
        rows.append([
            line.description, line.hsn_sac or "-", str(line.quantity), f"{line.rate:.2f}",
            f"{line.taxable_value:.2f}", f"{line.gst_rate:.2f}", f"{line.line_total:.2f}",
        ])
    table = Table(rows, repeatRows=1, colWidths=[150, 48, 35, 55, 60, 42, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B3153")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DCE2EA")),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.extend([table, Spacer(1, 14)])
    totals = [
        ["Taxable Value", f"INR {invoice.taxable_total:.2f}"],
        ["CGST", f"INR {invoice.cgst_total:.2f}"],
        ["SGST", f"INR {invoice.sgst_total:.2f}"],
        ["IGST", f"INR {invoice.igst_total:.2f}"],
        ["Grand Total", f"INR {invoice.grand_total:.2f}"],
    ]
    total_table = Table(totals, colWidths=[390, 130], hAlign="RIGHT")
    total_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.HexColor("#1B3153")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(total_table)
    if invoice.notes:
        story.extend([Spacer(1, 12), Paragraph(f"Notes: {invoice.notes}", styles["Normal"])])
    story.extend([Spacer(1, 24), Paragraph("This is a system-generated invoice. Verify tax treatment and statutory particulars before use.", styles["Italic"])])
    doc.build(story)
    buffer.seek(0)
    filename = f"{invoice.invoice_number.replace('/', '-')}.pdf"
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{filename}"'})
