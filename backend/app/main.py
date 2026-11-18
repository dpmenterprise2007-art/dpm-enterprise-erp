from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.invoices import router as invoices_router
from app.routers.masters import router as masters_router
from app.ui import router as ui_router

app = FastAPI(title=settings.app_name, version="1.0.0", description="Local-first DPM Enterprise ERP")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["GET","POST","PUT","PATCH","DELETE"], allow_headers=["Authorization","Content-Type"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ui_router)
app.include_router(auth_router)
app.include_router(masters_router)
app.include_router(invoices_router)

@app.get("/health", tags=["System"])
def health() -> dict[str,str]:
    return {"status":"ok","application":"DPM ENTERPRISE ERP"}
