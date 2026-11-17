from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.masters import router as masters_router
from app.routers.invoices import router as invoices_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Billing, accounting and interior-project management API for DPM ENTERPRISE PRIVATE LIMITED.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(masters_router)
app.include_router(invoices_router)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "application": "DPM ENTERPRISE ERP"}


@app.get("/api/v1", tags=["System"])
def api_root() -> dict[str, str]:
    return {"name": "DPM ENTERPRISE ERP", "version": "1.0.0", "stage": "invoice-engine"}
