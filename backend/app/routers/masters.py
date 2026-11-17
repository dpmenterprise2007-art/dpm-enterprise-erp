from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer, Item, Vendor
from app.schemas import CustomerInput, CustomerRead, ItemInput, ItemRead, VendorInput, VendorRead

router = APIRouter(prefix="/api/v1", tags=["Master Data"])


def commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A record with the same unique GSTIN already exists.") from exc


@router.post("/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerInput, db: Session = Depends(get_db)):
    record = Customer(**payload.model_dump())
    db.add(record)
    commit_or_conflict(db)
    db.refresh(record)
    return record


@router.get("/customers", response_model=list[CustomerRead])
def list_customers(
    search: str | None = Query(default=None, max_length=180),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    query = select(Customer)
    if active_only:
        query = query.where(Customer.is_active.is_(True))
    if search:
        query = query.where(Customer.display_name.ilike(f"%{search}%"))
    return db.scalars(query.order_by(Customer.display_name).limit(200)).all()


@router.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    record = db.get(Customer, customer_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")
    return record


@router.patch("/customers/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: UUID, payload: CustomerInput, db: Session = Depends(get_db)):
    record = db.get(Customer, customer_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    commit_or_conflict(db)
    db.refresh(record)
    return record


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_customer(customer_id: UUID, db: Session = Depends(get_db)):
    record = db.get(Customer, customer_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")
    record.is_active = False
    db.commit()


@router.post("/vendors", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorInput, db: Session = Depends(get_db)):
    record = Vendor(**payload.model_dump())
    db.add(record)
    commit_or_conflict(db)
    db.refresh(record)
    return record


@router.get("/vendors", response_model=list[VendorRead])
def list_vendors(search: str | None = Query(default=None, max_length=180), db: Session = Depends(get_db)):
    query = select(Vendor).where(Vendor.is_active.is_(True))
    if search:
        query = query.where(Vendor.display_name.ilike(f"%{search}%"))
    return db.scalars(query.order_by(Vendor.display_name).limit(200)).all()


@router.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemInput, db: Session = Depends(get_db)):
    record = Item(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/items", response_model=list[ItemRead])
def list_items(search: str | None = Query(default=None, max_length=180), db: Session = Depends(get_db)):
    query = select(Item).where(Item.is_active.is_(True))
    if search:
        query = query.where(Item.name.ilike(f"%{search}%"))
    return db.scalars(query.order_by(Item.name).limit(500)).all()
