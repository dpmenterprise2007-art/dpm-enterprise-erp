from fastapi import FastAPI

app = FastAPI(
    title="DPM ENTERPRISE ERP API",
    version="1.0.0",
    description="Billing, accounting and interior-project management API for DPM ENTERPRISE PRIVATE LIMITED.",
)


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "application": "DPM ENTERPRISE ERP"}


@app.get("/api/v1", tags=["System"])
def api_root() -> dict[str, str]:
    return {"name": "DPM ENTERPRISE ERP", "version": "1.0.0", "stage": "foundation"}
