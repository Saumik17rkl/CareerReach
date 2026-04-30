from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Contact
from app.services.excel_parser import parse_excel
from sqlalchemy import or_

router = APIRouter()


# ---------------------------
# EMAIL VALIDATION
# ---------------------------
def is_valid_email(email):
    if not email:
        return False

    if not isinstance(email, str):
        return False

    email = email.strip()
    return "@" in email and "." in email


# ---------------------------
# PHONE CLEANING
# ---------------------------
def clean_phone(phone):
    if not phone:
        return None

    # Handle pandas NaN or float numbers
    if isinstance(phone, float):
        if str(phone) == "nan":
            return None
        phone = str(int(phone))

    if isinstance(phone, str):
        phone = phone.strip()

        # Remove spaces / dashes
        phone = phone.replace(" ", "").replace("-", "")

        return phone if phone.isdigit() else None

    return None


# ---------------------------
# UPLOAD ENDPOINT
# ---------------------------
@router.post("/upload-excel")
async def upload_excel(file: UploadFile, db: Session = Depends(get_db)):

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files allowed")

    data = parse_excel(file.file)

    inserted = 0
    skipped_invalid_email = 0

    for sheet, records in data.items():
        for item in records:

            # ---------------------------
            # CLEAN EMAIL
            # ---------------------------
            if not is_valid_email(item.get("email")):
                item["email"] = None
                skipped_invalid_email += 1

            # ---------------------------
            # CLEAN PHONES
            # ---------------------------
            item["mobile"] = clean_phone(item.get("mobile"))
            item["landline"] = clean_phone(item.get("landline"))

            # ---------------------------
            # DEDUP CHECK (UPDATED)
            # ---------------------------
            exists = db.query(Contact).filter(
                or_(
                    Contact.email == item.get("email"),
                    Contact.mobile == item.get("mobile"),
                    Contact.landline == item.get("landline")
                )
            ).first()

            if not exists:
                db.add(Contact(**item))
                inserted += 1

    db.commit()

    return {
        "inserted": inserted,
        "skipped_invalid_email": skipped_invalid_email,
        "sheets": list(data.keys())
    }