# Authentication and Local Setup

## 1. Configure environment
Copy `.env.example` to `.env`. Set a unique, randomly generated JWT_SECRET_KEY (at least 32 random bytes) and a strong database password. Do not commit `.env`.

## 2. Start PostgreSQL
From the repository root:
```bash
docker compose up -d db
```

## 3. Install and migrate backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

## 4. Create the first administrator
Run from the backend directory:
```bash
python scripts/create_admin.py --email admin@example.com --name "DPM Administrator"
```
The script prompts for the password; use at least 12 characters. Do not put passwords in shell history.

## 5. Run services
Backend:
```bash
uvicorn app.main:app --reload
```
Frontend, in another terminal:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000/login.

## Current access model
- Login returns a short-lived JWT bearer token.
- Customer, supplier, item and invoice APIs require authentication.
- User roles currently include `admin` and `staff`; fine-grained permission matrices and refresh-token/session revocation are future hardening work.
- The frontend currently stores the bearer token in browser localStorage for this development build. Before production, move to secure HttpOnly cookies or an equivalent hardened session design, add CSRF controls as appropriate, rate limiting, lockout policy, audit logs, and HTTPS.

## Important
Do not enter live customer or company financial records until deployment security, database backups, access controls and statutory invoice rules have been reviewed and tested.
