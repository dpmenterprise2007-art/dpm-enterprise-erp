# Security and Data Handling

This repository is public. Commit source code and synthetic test fixtures only.

Never commit .env files, API credentials, GST portal credentials, customer/vendor/employee personal records, bank statements, real invoices, contracts, tender documents, production database dumps or backup archives.

Before production:
- Strong password hashing and session revocation.
- Role-based access control and least privilege.
- HTTPS for remote access.
- Secrets supplied through protected environment variables or a secret manager.
- Encrypted backups with separated access.
- Audit logs for financial and administrative actions.
- Dependency and vulnerability scanning.
- Restore testing and incident response procedures.
