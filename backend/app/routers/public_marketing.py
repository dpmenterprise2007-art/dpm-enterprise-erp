from collections import defaultdict, deque
from html import escape
from time import monotonic
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
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


@router.get("/site", response_class=HTMLResponse, include_in_schema=False)
def public_site():
    base = settings.public_base_url.rstrip("/")
    return HTMLResponse(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DPM Enterprise | Interior Design & Custom Furniture</title>
<meta name="description" content="Residential, corporate and commercial interior design, turnkey fit-outs, modular kitchens and custom furniture by DPM Enterprise.">
<link rel="canonical" href="{escape(base)}/site"><meta name="robots" content="index,follow">
<style>
:root{{--bg:#0b1220;--panel:#121d31;--gold:#d7b477;--text:#f5f2eb;--muted:#b8c1cf}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 Arial,sans-serif}}
header,main,footer{{max-width:1120px;margin:auto;padding:24px}}header{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #29364b}}
.brand{{font-weight:800;letter-spacing:1px}}.brand span{{color:var(--gold)}}a{{color:var(--gold)}}.hero{{padding:70px 24px 48px}}.eyebrow{{color:var(--gold);letter-spacing:2px;text-transform:uppercase;font-size:12px}}
h1{{font-size:clamp(38px,7vw,68px);line-height:1.05;max-width:800px;margin:12px 0}}h2{{font-size:30px}}.muted{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}
.card{{background:var(--panel);border:1px solid #29364b;border-radius:16px;padding:22px}}.cta{{display:inline-block;background:var(--gold);color:#161616;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:700}}
form{{display:grid;gap:12px}}input,textarea{{width:100%;padding:13px;border:1px solid #43516a;border-radius:8px;background:#0b1424;color:white;font:inherit}}button{{border:0;cursor:pointer}}.note{{font-size:13px;color:var(--muted)}}#result{{min-height:24px;color:var(--gold)}}footer{{border-top:1px solid #29364b;margin-top:40px;color:var(--muted)}}
</style></head><body>
<header><div class="brand">DPM <span>ENTERPRISE</span></div><a href="#enquiry">Request a consultation</a></header>
<main><section class="hero"><div class="eyebrow">Interior design · Turnkey execution · Custom furniture</div>
<h1>Spaces designed around the way you live and work.</h1>
<p class="muted">DPM Enterprise delivers residential and commercial interiors, corporate office fit-outs, showrooms, hospitality spaces, clinics, modular kitchens and made-to-measure furniture.</p>
<a class="cta" href="#enquiry">Discuss your project</a></section>
<section><h2>Our services</h2><div class="grid">
<div class="card"><h3>Residential interiors</h3><p class="muted">Apartments, bungalows, complete home interiors, wardrobes and kitchens.</p></div>
<div class="card"><h3>Corporate & commercial</h3><p class="muted">Office fit-outs, retail showrooms, restaurants, hotels and clinics.</p></div>
<div class="card"><h3>Custom furniture</h3><p class="muted">Made-to-measure furniture, counters, storage and specialist joinery.</p></div>
<div class="card"><h3>Turnkey execution</h3><p class="muted">Coordinated design, material planning, manufacturing and site execution.</p></div>
</div></section>
<section id="enquiry" class="card" style="margin-top:32px"><h2>Tell us about your project</h2>
<p class="muted">Share your requirement. Our team can contact you to discuss scope, location and next steps.</p>
<form id="lead"><input name="contact_name" placeholder="Your name" minlength="2" maxlength="160" required>
<input name="company_name" placeholder="Company name (optional)" maxlength="180">
<input name="phone" placeholder="Phone number" minlength="8" maxlength="20" required>
<input name="email" type="email" placeholder="Email (optional)">
<input name="city" placeholder="Project city (optional)" maxlength="100">
<textarea name="requirement" placeholder="Project type, approximate area and requirement" minlength="10" maxlength="5000" required></textarea>
<input name="website" aria-hidden="true" tabindex="-1" autocomplete="off" style="position:absolute;left:-10000px">
<button class="cta" type="submit">Submit enquiry</button><div id="result" role="status"></div></form>
<p class="note">Site visits are chargeable at ₹5,000 + 18% GST (₹5,900), subject to confirmation and scheduling.</p></section>
<section style="margin-top:32px"><h2>Contact DPM Enterprise</h2><p>Phone: <a href="tel:02269719769">022 69719769</a> · <a href="tel:9930998063">9930998063</a></p><p class="muted">DPM ENTERPRISE PRIVATE LIMITED · Virar, Maharashtra, India</p></section></main>
<footer>© DPM ENTERPRISE PRIVATE LIMITED</footer>
<script>
document.getElementById('lead').addEventListener('submit',async e=>{{e.preventDefault();const f=e.currentTarget;const data=Object.fromEntries(new FormData(f).entries());const out=document.getElementById('result');out.textContent='Submitting…';try{{const r=await fetch('/api/v1/public/enquiries',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}});const j=await r.json();if(!r.ok)throw new Error(j.detail||'Unable to submit');out.textContent='Thank you. Your enquiry reference is '+j.reference+'.';f.reset()}}catch(err){{out.textContent=err.message}}}});
</script></body></html>""")


@router.post("/api/v1/public/enquiries", status_code=status.HTTP_202_ACCEPTED)
def public_enquiry(payload: PublicEnquiry, request: Request, db: Session = Depends(get_db)):
    _rate_limit(request)
    if payload.website.strip():
        return {"accepted": True, "reference": str(uuid4())[:8].upper()}
    lead = Lead(
        contact_name=payload.contact_name.strip(),
        company_name=payload.company_name.strip() if payload.company_name else None,
        phone=payload.phone.strip(),
        email=str(payload.email) if payload.email else None,
        source="public_website",
        requirement=(payload.requirement.strip() + (f" | Location: {payload.city.strip()}" if payload.city else "")),
        status="new", estimated_value=0,
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
        "User-agent: *\nAllow: /site\nDisallow: /api/\nDisallow: /login\nDisallow: /users\n"
        f"Sitemap: {base}/sitemap.xml\n",
        media_type="text/plain",
    )


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    base = settings.public_base_url.rstrip("/")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f'<url><loc>{escape(base + "/site")}</loc></url></urlset>')
    return Response(content=xml, media_type="application/xml")


@router.get("/api/v1/public/marketing/status")
def marketing_status():
    return {
        "public_site": "ready",
        "public_enquiry_api": "ready",
        "robots_txt": "ready",
        "sitemap_xml": "ready",
        "social_publishing": "not_connected",
        "seo_canonical_domain": settings.public_base_url,
        "note": "Social publishing requires authorized platform credentials and permissions.",
    }
