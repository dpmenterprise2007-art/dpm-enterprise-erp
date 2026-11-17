# Database migrations

From the backend directory, after configuring the local DATABASE_URL:

```bash
alembic upgrade head
```

To create a future migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe change"
```

Review every generated migration before applying it. Do not use destructive migrations against live company data without a verified backup and approval.
