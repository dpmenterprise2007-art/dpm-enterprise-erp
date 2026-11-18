from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadRead, LeadUpdate
from app.security import get_current_user

router = APIRouter(prefix="/api/v1", tags=["CRM Leads"], dependencies=[Depends(get_current_user)])

def calculate_lead_score(lead: Lead) -> int:
    """Deterministic, explainable baseline score; not represented as an AI prediction."""
    score = 10
    if lead.phone:
        score += 15
    if lead.email:
        score += 10
    if lead.company_name:
        score += 10
    if lead.requirement:
        score += 15
    if lead.estimated_value >= 1_000_000:
        score += 25
    elif lead.estimated_value >= 250_000:
        score += 15
    elif lead.estimated_value > 0:
        score += 5
    if lead.follow_up_at:
        score += 5
    return min(score, 100)

@router.post("/leads", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**payload.model_dump(), status="new")
    lead.score = calculate_lead_score(lead)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/leads", response_model=list[LeadRead])
def list_leads(
    search: str | None = Query(default=None, max_length=180),
    lead_status: str | None = Query(default=None, alias="status", max_length=24),
    db: Session = Depends(get_db),
):
    query = select(Lead)
    if search:
        term = f"%{search}%"
        query = query.where((Lead.contact_name.ilike(term)) | (Lead.company_name.ilike(term)) | (Lead.phone.ilike(term)) | (Lead.email.ilike(term)))
    if lead_status:
        query = query.where(Lead.status == lead_status)
    return db.scalars(query.order_by(Lead.created_at.desc()).limit(500)).all()

@router.get("/leads/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/leads/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: UUID, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    lead.score = calculate_lead_score(lead)
    db.commit()
    db.refresh(lead)
    return lead
