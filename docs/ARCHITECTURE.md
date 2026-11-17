# DPM ERP Architecture

Single-company internal ERP for DPM ENTERPRISE PRIVATE LIMITED. No multi-tenant SaaS.

## Application layers
1. Next.js + TypeScript web client.
2. Tauri Windows shell (planned), reusing the web client.
3. FastAPI application services and REST API.
4. PostgreSQL relational database.
5. File storage for generated invoices and attachments.
6. Encrypted backup and tested restore workflow.

## Bounded contexts
Identity/access control; company configuration and financial periods; customers/vendors; item and tax catalog; sales; procurement; accounting; banking; inventory; interior projects and BOQ; furniture manufacturing; GST reporting; HR/payroll; audit and backup.

## Critical invariants
- Use Decimal/NUMERIC for money, never binary floating point.
- A posted journal must balance and be immutable.
- Posting must be atomic in a database transaction.
- Document numbering must be unique and concurrency-safe.
- Correct posted documents through reversal/credit/debit-note workflows.
- Preserve tax snapshots on posted documents.
- Every privileged financial action must be attributable to a user.

## Deployment
Use one authoritative PostgreSQL database. Remote access must use secure authenticated connectivity. Cloud storage receives encrypted backups; it is not a second independently writable database.
