# DPM ENTERPRISE ERP
Local-first ERP for DPM ENTERPRISE PRIVATE LIMITED.

## Stack
Python + FastAPI + server-rendered HTML + local CSS + SQLite. No Node.js, Next.js, Docker or PostgreSQL required.

## Windows quick start
1. Install Python 3.11 or newer and enable Add Python to PATH.
2. Double-click START_DPM_ERP.bat.
3. First run creates .venv, installs Python packages, creates backend/.env and backend/dpm_erp.db, then opens the browser.
4. Later starts reuse installed packages and the local database. Stop with Ctrl+C.

Internet is needed for the first Python dependency installation only.

## First administrator
After starting the app, open a second Command Prompt in the repository folder:
```bat
cd backend
..\.venv\Scripts\python.exe -m scripts.create_admin --email admin@example.com --name "DPM Admin"
```
Choose a strong password (12+ characters), then sign in at http://127.0.0.1:8000/login.

## Current modules
Dashboard, customer master, supplier master, invoice draft/issue/PDF, admin user management and existing JSON API at /api/v1.

## Data
SQLite file: backend/dpm_erp.db. Stop the app before copying it for backup. Keep backend/.env private.

## Release status
Local development build, not a production accounting release. Validate GST registration, place of supply, tax rates, invoice numbering, security and backup/restore before live use. Full double-entry accounting, purchase, inventory, BOQ, project costing and advanced reports remain future work.
