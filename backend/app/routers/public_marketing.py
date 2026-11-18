from collections import defaultdict, deque
from datetime import datetime, timezone
from html import escape
from time import monotonic
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Lead

router = APIRouter(tags=["Public Website & Marketing"])
_hits: dict[str, deque[float]] = defaultdict(deque)
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 8


class PublicEnquiry(BaseModel):
    contact_name: str = Field(min_length=2, max_length=160)
    company_name: str | None = Field(default=None, max_length=180)
    phone: str = Field(min_length=8, max_length=20)
    email: EmailStr | None = None
    requirement: str = Field(min_length=10, max_length=5000)
    city: str | None = Field(default=None, max_length=100)
    # Must remain empty. This hidden field is a basic bot trap.
    website: str = Field(default="", max_length=200)


def _rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = monotonic()
    bucket = _hits[ip]
    while bucket and now - bucket[0] > _WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many enquiries. Please try again later.")
    bucket.append(now)


@router.post("/api/v1/public/enquiries", status_code=status.HTTP_202_ACCEPTED)
def public_enquiry(payload: PublicEnquiry, request: Request, db: Session = Depends(get_db)):
    """Public website lead capture. No ERP login required; never exposes CRM records."""
    _rate_limit(request)
    if payload.website.strip():
        # Return the same generic response as accepted submissions to avoid bot feedback.
        return {"accepted": True, "reference": str(uuid4())[:8].upper()}
    lead = Lead(
        contact_name=payload.contact_name.strip(),
        company_name=payload.company_name.strip() if payload.company_name else None,
        phone=payload.phone.strip(),
        email=str(payload.email) if payload.email else None,
        source="public_website",
        requirement=(payload.requirement.strip() + (f" | Location: {payload.city.strip()}" if payload.city else "")),
        status="new",
        estimated_value=0,
        score=40 + (10 if payload.email else 0) + (10 if payload.company_name else 0),
    )
    db.add(lead)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Enquiry could not be saved. Please retry.")
    return {"accepted": True, "reference": str(lead.id)[:8].upper()}


@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots_txt():
    base = settings.public_base_url.rstrip("/")
    return PlainTextResponse(
        "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /login\nDisallow: /users\n"
        f"Sitemap: {base}/sitemap.xml\n",
        media_type="text/plain",
    )


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    base = settings.public_base_url.rstrip("/")
    # Only public marketing pages are listed; private ERP pages and APIs are excluded.
    paths = ["/", "/services", "/interior-design", "/modular-kitchen", "/custom-furniture", "/contact"]
    urls = "".join(
        f"<url><loc>{escape(base + path)}</loc></url>" for path in paths
    )
    xml = '<?xml version="1.0" encoding="UTF-8"?>' + (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/api/v1/public/marketing/status")
def marketing_status():
    """Reports implemented public capabilities without implying social accounts are connected."""
    return {
        "public_enquiry_api": "ready",
        "robots_txt": "ready",
        "sitemap_xml": "ready",
        "social_publishing": "not_connected",
        "seo_canonical_domain": settings.public_base_url,
        "note": "Social publishing requires authorized platform credentials and permissions.",
    }
