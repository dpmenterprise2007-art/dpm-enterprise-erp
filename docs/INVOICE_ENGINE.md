# GST Invoice Engine – Development Scope

## Endpoints
- POST /api/v1/invoices – create a draft invoice.
- GET /api/v1/invoices – list recent invoices.
- GET /api/v1/invoices/{invoice_id} – retrieve invoice and line snapshots.
- POST /api/v1/invoices/{invoice_id}/issue – assign the financial-year sequence and issue the invoice.
- GET /api/v1/invoices/{invoice_id}/pdf – generate a PDF for an issued invoice.

## Current calculations
- Decimal arithmetic and paise rounding.
- Line-level discount.
- Taxable value per line.
- Intra-state split into CGST and SGST.
- Inter-state IGST.
- Financial-year numbering in DPM/YY-YY/NNNN format.
- Invoice line values are stored as document snapshots.

## Important limitations
- This is an early development implementation, not a legally approved tax invoice product.
- The company GST registration profile and state code must be configured from verified company records; the current draft endpoint receives the company state code in the request.
- Place-of-supply, HSN/SAC, rate applicability, exemptions, reverse charge, exports, SEZ, e-commerce TCS/TDS, cess, rounding and statutory particulars need broader rule coverage and professional validation.
- Issuing an invoice currently assigns a number and changes its status; it does not yet create accounting journal entries or payment allocations.
- Authentication, permissions, audit trails, cancellation/reversal controls and production-grade document numbering review are still pending.
- PDF is a basic generated layout; official DPM logo, registered address, GSTIN, bank details, terms, signature and statutory declarations must be configured before production.
