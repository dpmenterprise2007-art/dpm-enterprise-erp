from datetime import datetime, timezone
from decimal import Decimal
from html import escape
from typing import Annotated
from uuid import UUID
import jwt
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from app.config import settings
from app.db import get_db
from app.models import Customer, Invoice, Item, User, Vendor
from app.routers.invoices import create_invoice, issue_invoice, invoice_pdf
from app.schemas import InvoiceCreate, InvoiceLineInput
from app.security import hash_password, verify_password, create_access_token

router=APIRouter(include_in_schema=False)
NAV='<a href="/">Overview</a><a href="/customers">Customers</a><a href="/suppliers">Suppliers</a><a href="/invoices">Invoices</a><a href="/invoices/new">New invoice</a><a href="/users">Users</a>'
CSS='/static/app.css'

def shell(title,body,user=None):
    account=f'<span>{escape(user.full_name)} · {escape(user.role)}</span><a href="/logout">Sign out</a>' if user else ''
    nav=f'<aside>{NAV}</aside>' if user else ''
    return HTMLResponse(f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · DPM ERP</title><link rel="stylesheet" href="{CSS}"></head><body><header><a class="brand" href="/">DPM <b>ENTERPRISE ERP</b></a><div class="account">{account}</div></header><div class="layout">{nav}<main><small>DPM ENTERPRISE PRIVATE LIMITED</small><h1>{escape(title)}</h1>{body}</main></div></body></html>')

def auth(request,db):
    try:
        data=jwt.decode(request.cookies.get("dpm_session",""),settings.jwt_secret_key,algorithms=[settings.jwt_algorithm])
        user=db.get(User,data.get("sub"))
    except (jwt.PyJWTError,ValueError,TypeError):
        user=None
    if not user or not user.is_active: raise HTTPException(303,headers={"Location":"/login"})
    return user

def inp(label,name,typ="text",required=False):
    return f'<label>{escape(label)}<input name="{name}" type="{typ}" {"required" if required else ""}></label>'

def table(headers,rows):
    return '<table><tr>'+''.join(f'<th>{h}</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join(f'<td>{v}</td>' for v in row)+'</tr>' for row in rows)+'</table>'

@router.get("/login",response_class=HTMLResponse)
def login_page(db:Session=Depends(get_db)):
    if (db.scalar(select(func.count()).select_from(User)) or 0)==0: return RedirectResponse("/setup",303)
    form='<form class="card narrow" method="post"><h2>Sign in</h2>'+inp("Email","email","email",True)+inp("Password","password","password",True)+'<button>Sign in</button></form>'
    return shell("Sign in",form)

@router.post("/login")
def login(email:Annotated[str,Form()],password:Annotated[str,Form()],db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==email.strip().lower()))
    if not user or not user.is_active or not verify_password(password,user.password_hash):
        return shell("Sign in",'<form class="card narrow" method="post"><p class="error">Email or password incorrect.</p>'+inp("Email","email","email",True)+inp("Password","password","password",True)+'<button>Sign in</button></form>')
    r=RedirectResponse("/",303);r.set_cookie("dpm_session",create_access_token(user),httponly=True,samesite="lax",secure=False,max_age=settings.access_token_expire_minutes*60);return r

@router.get("/logout")
def logout():
    r=RedirectResponse("/login",303);r.delete_cookie("dpm_session");return r

@router.get("/",response_class=HTMLResponse)
def dashboard(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db)
    names=["Customers","Suppliers","Invoices","Items"];models=[Customer,Vendor,Invoice,Item]
    cards=''.join(f'<div class="stat"><small>{n}</small><strong>{db.scalar(select(func.count()).select_from(m)) or 0}</strong></div>' for n,m in zip(names,models))
    return shell("Business overview",f'<section class="stats">{cards}</section><section class="card"><h2>Quick actions</h2><a class="button" href="/customers">Customers</a> <a class="button" href="/suppliers">Suppliers</a> <a class="button" href="/invoices/new">Create invoice</a></section><p class="muted">Local SQLite · Python runtime</p>',u)

@router.get("/customers",response_class=HTMLResponse)
def customers(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db);items=db.scalars(select(Customer).order_by(Customer.display_name)).all()
    rows=[(escape(x.display_name),escape(x.gstin or "-"),escape(x.phone or "-"),escape(x.state_code or "-")) for x in items]
    form='<form class="card" method="post"><h2>Add customer</h2>'+inp("Display name","display_name","text",True)+inp("Legal name","legal_name")+inp("GSTIN","gstin")+inp("Phone","phone")+inp("Email","email","email")+inp("Billing address","billing_address")+inp("State code","state_code")+'<button>Save customer</button></form>'
    return shell("Customer master",form+table(["Customer","GSTIN","Phone","State"],rows),u)

@router.post("/customers")
def add_customer(request:Request,display_name:Annotated[str,Form()],legal_name:Annotated[str,Form()]="",gstin:Annotated[str,Form()]="",phone:Annotated[str,Form()]="",email:Annotated[str,Form()]="",billing_address:Annotated[str,Form()]="",state_code:Annotated[str,Form()]="",db:Session=Depends(get_db)):
    auth(request,db);db.add(Customer(display_name=display_name.strip(),legal_name=legal_name or None,gstin=gstin.upper() or None,phone=phone or None,email=email or None,billing_address=billing_address or None,state_code=state_code or None))
    try: db.commit()
    except Exception: db.rollback()
    return RedirectResponse("/customers",303)

@router.get("/suppliers",response_class=HTMLResponse)
def suppliers(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db);items=db.scalars(select(Vendor).order_by(Vendor.display_name)).all()
    rows=[(escape(x.display_name),escape(x.gstin or "-"),escape(x.phone or "-"),escape(x.state_code or "-")) for x in items]
    form='<form class="card" method="post"><h2>Add supplier</h2>'+inp("Display name","display_name","text",True)+inp("Legal name","legal_name")+inp("GSTIN","gstin")+inp("Phone","phone")+inp("Email","email","email")+inp("Address","address")+inp("State code","state_code")+'<button>Save supplier</button></form>'
    return shell("Supplier master",form+table(["Supplier","GSTIN","Phone","State"],rows),u)

@router.post("/suppliers")
def add_supplier(request:Request,display_name:Annotated[str,Form()],legal_name:Annotated[str,Form()]="",gstin:Annotated[str,Form()]="",phone:Annotated[str,Form()]="",email:Annotated[str,Form()]="",address:Annotated[str,Form()]="",state_code:Annotated[str,Form()]="",db:Session=Depends(get_db)):
    auth(request,db);db.add(Vendor(display_name=display_name.strip(),legal_name=legal_name or None,gstin=gstin.upper() or None,phone=phone or None,email=email or None,address=address or None,state_code=state_code or None))
    try: db.commit()
    except Exception: db.rollback()
    return RedirectResponse("/suppliers",303)

@router.get("/invoices",response_class=HTMLResponse)
def invoices(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db);items=db.scalars(select(Invoice).order_by(Invoice.created_at.desc()).limit(200)).all()
    rows=[(escape(x.invoice_number or "Draft"),escape(x.customer_name),x.invoice_date.strftime("%d-%m-%Y"),escape(x.status),f"₹{x.grand_total:,.2f}") for x in items]
    return shell("Sales invoices",'<a class="button" href="/invoices/new">Create invoice</a>'+table(["Number","Customer","Date","Status","Total"],rows),u)

@router.get("/invoices/new",response_class=HTMLResponse)
def invoice_form(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db);cs=db.scalars(select(Customer).where(Customer.is_active.is_(True))).all();its=db.scalars(select(Item).where(Item.is_active.is_(True))).all()
    co=''.join(f'<option value="{x.id}">{escape(x.display_name)}</option>' for x in cs)
    io=''.join(f'<option value="{x.id}">{escape(x.name)}</option>' for x in its)
    body=f'<form class="card" method="post"><h2>Invoice details</h2><label>Customer<select name="customer_id" required><option value="">Select</option>{co}</select></label>'+inp("Invoice date","invoice_date","date",True)+inp("Place of supply state code","place_of_supply","text",True)+inp("Company GST state code","company_state_code","text",True)+f'<label>Item master (optional)<select name="item_id"><option value="">Manual</option>{io}</select></label>'+inp("Description","description","text",True)+inp("HSN/SAC","hsn_sac")+inp("Unit","unit")+inp("Quantity","quantity","number",True)+inp("Rate ₹","rate","number",True)+'<label>GST rate<select name="gst_rate"><option>0</option><option>5</option><option>12</option><option selected>18</option><option>28</option></select></label>'+inp("Notes","notes")+'<button>Create draft invoice</button></form>'
    return shell("Create tax invoice",body,u)

@router.post("/invoices/new")
def invoice_save(request:Request,customer_id:Annotated[str,Form()],invoice_date:Annotated[str,Form()],place_of_supply:Annotated[str,Form()],company_state_code:Annotated[str,Form()],description:Annotated[str,Form()],quantity:Annotated[Decimal,Form()],rate:Annotated[Decimal,Form()],item_id:Annotated[str,Form()]="",hsn_sac:Annotated[str,Form()]="",unit:Annotated[str,Form()] ="NOS",gst_rate:Annotated[Decimal,Form()]=Decimal("18"),notes:Annotated[str,Form()] ="",db:Session=Depends(get_db)):
    auth(request,db)
    payload=InvoiceCreate(customer_id=UUID(customer_id),invoice_date=datetime.fromisoformat(invoice_date).replace(tzinfo=timezone.utc),place_of_supply=place_of_supply,company_state_code=company_state_code,notes=notes or None,lines=[InvoiceLineInput(item_id=UUID(item_id) if item_id else None,description=description,hsn_sac=hsn_sac or None,unit=unit or "NOS",quantity=quantity,rate=rate,gst_rate=gst_rate)])
    inv=create_invoice(payload,db);return RedirectResponse(f"/invoices/{inv.id}",303)

@router.get("/invoices/{invoice_id}",response_class=HTMLResponse)
def invoice_detail(invoice_id:UUID,request:Request,db:Session=Depends(get_db)):
    u=auth(request,db);x=db.scalar(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id==invoice_id))
    if not x: raise HTTPException(404,"Invoice not found")
    lines=[(escape(y.description),str(y.quantity),f"₹{y.rate:,.2f}",f"₹{y.taxable_value:,.2f}",f"₹{y.line_total:,.2f}") for y in x.lines]
    action=f'<form method="post" action="/invoices/{x.id}/issue"><button>Issue invoice</button></form>' if x.status=="draft" else f'<a class="button" href="/invoices/{x.id}/pdf" target="_blank">Open PDF</a>'
    return shell("Invoice detail",f'<section class="card"><p>{escape(x.status)} · {escape(x.invoice_number or "Draft")}</p><p>Customer: {escape(x.customer_name)}</p>{table(["Description","Qty","Rate","Taxable","Total"],lines)}<h2>Grand total ₹{x.grand_total:,.2f}</h2>{action}</section>',u)

@router.post("/invoices/{invoice_id}/issue")
def invoice_issue(invoice_id:UUID,request:Request,db:Session=Depends(get_db)):
    auth(request,db);issue_invoice(invoice_id,db);return RedirectResponse(f"/invoices/{invoice_id}",303)

@router.get("/users",response_class=HTMLResponse)
def users(request:Request,db:Session=Depends(get_db)):
    u=auth(request,db)
    if u.role!="admin": raise HTTPException(403,"Admin only")
    items=db.scalars(select(User).order_by(User.full_name)).all()
    rows=[(escape(x.full_name),escape(x.email),escape(x.role)) for x in items]
    form='<form class="card" method="post"><h2>Create user</h2>'+inp("Full name","full_name","text",True)+inp("Email","email","email",True)+inp("Password (12+ chars)","password","password",True)+'<label>Role<select name="role"><option>staff</option><option>admin</option></select></label><button>Create user</button></form>'
    return shell("User access",form+table(["Name","Email","Role"],rows),u)

@router.post("/users")
def user_add(request:Request,full_name:Annotated[str,Form()],email:Annotated[str,Form()],password:Annotated[str,Form()],role:Annotated[str,Form()] ="staff",db:Session=Depends(get_db)):
    u=auth(request,db)
    if u.role!="admin": raise HTTPException(403,"Admin only")
    if len(password)<12: raise HTTPException(422,"Password must be at least 12 characters")
    db.add(User(full_name=full_name.strip(),email=email.strip().lower(),password_hash=hash_password(password),role=role if role in {"admin","staff"} else "staff"));db.commit()
    return RedirectResponse("/users",303)

@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf_ui(invoice_id: UUID, request: Request, db: Session = Depends(get_db)):
    auth(request, db)
    return invoice_pdf(invoice_id, db)

@router.get("/setup", response_class=HTMLResponse)
def first_admin_setup(db: Session = Depends(get_db)):
    if (db.scalar(select(func.count()).select_from(User)) or 0)>0:
        return RedirectResponse("/login",303)
    form='<form class="card narrow" method="post"><h2>First-time administrator setup</h2><p class="muted">Create the first DPM ERP administrator account.</p>'+inp("Full name","full_name","text",True)+inp("Email","email","email",True)+inp("Password (minimum 12 characters)","password","password",True)+'<button>Create administrator</button></form>'
    return shell("Initial setup",form)

@router.post("/setup")
def first_admin_create(full_name: Annotated[str,Form()], email: Annotated[str,Form()], password: Annotated[str,Form()], db: Session = Depends(get_db)):
    if (db.scalar(select(func.count()).select_from(User)) or 0)>0:
        return RedirectResponse("/login",303)
    if len(password)<12:
        raise HTTPException(422,"Password must be at least 12 characters")
    db.add(User(full_name=full_name.strip(),email=email.strip().lower(),password_hash=hash_password(password),role="admin"))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409,"Could not create administrator; check whether this email already exists")
    return RedirectResponse("/login",303)
