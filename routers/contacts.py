from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Contact, AccessLog
from app.services.utils import get_client_info
from app.services.limiter import check_limit

router = APIRouter(prefix="/contacts")


# ---------------------------
# CLEAN RESPONSE (REMOVE NULLS)
# ---------------------------
def clean_dict(data: dict):
    return {
        k: v for k, v in data.items()
        if v not in [None, "", "Invalid Email"]
    }


# ---------------------------
# GET CONTACTS (ALL / FILTERED)
# ---------------------------
@router.get("/")
def get_contacts(
    request: Request,
    sheet: str = Query(None),
    db: Session = Depends(get_db)
):
    ip, ua = get_client_info(request)

    # ---------------------------
    # FILTER BY SHEET
    # ---------------------------
    if sheet:
        all_sheets = db.query(Contact.source_sheet).distinct().all()
        sheet_names = [s[0] for s in all_sheets]

        # numeric → map to actual sheet name
        if sheet.isdigit():
            idx = int(sheet) - 1
            if idx < 0 or idx >= len(sheet_names):
                raise HTTPException(status_code=400, detail="Invalid sheet index")
            sheet = sheet_names[idx]

        contacts = db.query(Contact).filter(
            Contact.source_sheet == sheet
        ).all()

        result = {}

        for c in contacts:
            cleaned = clean_dict({
                "company_name": c.company_name,
                "hr_name": c.hr_name,
                "email": c.email,
                "mobile": c.mobile,
                "landline": c.landline,
                "role": c.role,
                "location": c.location
            })

            if cleaned:
                result[c.id] = cleaned

        return {
            "sheet": sheet,
            "data": result
        }

    # ---------------------------
    # ALL SHEETS
    # ---------------------------
    contacts = db.query(Contact).all()

    grouped = {}

    for c in contacts:
        sheet_name = c.source_sheet

        if sheet_name not in grouped:
            grouped[sheet_name] = {}

        cleaned = clean_dict({
            "company_name": c.company_name,
            "hr_name": c.hr_name,
            "email": c.email,
            "mobile": c.mobile,
            "landline": c.landline,
            "role": c.role,
            "location": c.location
        })

        if not cleaned:
            continue

        grouped[sheet_name][c.id] = cleaned

    return {"data": grouped}


# ---------------------------
# GET SHEET NAMES
# ---------------------------
@router.get("/sheets")
def get_sheets(db: Session = Depends(get_db)):
    sheets = db.query(Contact.source_sheet).distinct().all()
    return [s[0] for s in sheets]


# ---------------------------
# GET FULL CONTACT (LIMITED)
# ---------------------------
@router.get("/{contact_id}")
def get_contact(contact_id: int, request: Request, db: Session = Depends(get_db)):
    ip, ua = get_client_info(request)

    if not check_limit(db, ip):
        raise HTTPException(status_code=429, detail="Limit exceeded")

    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    log = AccessLog(user_ip=ip, user_agent=ua, contact_id=contact_id)
    db.add(log)
    db.commit()

    return clean_dict({
        "id": contact.id,
        "company_name": contact.company_name,
        "hr_name": contact.hr_name,
        "email": contact.email,
        "mobile": contact.mobile,
        "landline": contact.landline,
        "role": contact.role,
        "location": contact.location,
        "source_sheet": contact.source_sheet
    })


# ---------------------------
# DELETE SHEET
# ---------------------------
@router.delete("/sheets/{sheet_name}")
def delete_sheet(sheet_name: str, db: Session = Depends(get_db)):
    # Check if sheet exists
    sheet_contacts = db.query(Contact).filter(Contact.source_sheet == sheet_name).all()
    
    if not sheet_contacts:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    # Delete all contacts from the sheet
    deleted_count = db.query(Contact).filter(Contact.source_sheet == sheet_name).count()
    db.query(Contact).filter(Contact.source_sheet == sheet_name).delete()
    db.commit()
    
    return {
        "message": f"Sheet '{sheet_name}' deleted successfully",
        "deleted_contacts": deleted_count
    }