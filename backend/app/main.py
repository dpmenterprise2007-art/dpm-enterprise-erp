from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.config import settings
from app.db import Base, SessionLocal, engine
from app import models  # noqa: F401 - register SQLAlchemy models
from app.models import User
from app.security import hash_password
from app.routers.auth import router as auth_router
from app.routers.invoices import router as invoices_router
from app.routers.masters import router as masters_router
from app.routers.leads import router as leads_router
from app.ui import router as ui_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preview bootstrap. Production requires persistent managed DB, migrations,
    # secure secret rotation, and tested backups before business data is entered.
    Base.metadata.create_all(bind=engine)

    # Provision the first administrator from private Render environment variables.
    # Never overwrite an existing account or reset an existing administrator.
    if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
        with SessionLocal() as db:
            existing = db.scalar(select(User).where(User.email == settings.bootstrap_admin_email.lower()))
            if existing is None and (db.query(User).count() == 0):
                db.add(User(
                    full_name=settings.bootstrap_admin_name,
                    email=settings.bootstrap_admin_email.strip().lower(),
                    password_hash=hash_password(settings.bootstrap_admin_password),
                    role="admin",
                    is_active=True,
                ))
                db.commit()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.2",
    description="DPM ENTERPRISE ERP preview",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ui_router)
app.include_router(auth_router)
app.include_router(masters_router)
app.include_router(leads_router)
app.include_router(invoices_router)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "application": "DPM ENTERPRISE ERP"}
