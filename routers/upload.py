from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Contact
from app.services.excel_parser import parse_excel
from sqlalchemy import or_, and_

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
# PROGRESSIVE SHEET NAMING
# ---------------------------
def generate_sheet_name(db: Session, base_sheet: str):
    """Generate progressive sheet names: Sheet1, Sheet2, Sheet1_1, Sheet2_1, etc."""
    
    # Get existing sheets
    existing_sheets = db.query(Contact.source_sheet).distinct().all()
    existing_sheet_names = [s[0] for s in existing_sheets]
    
    # If this is the first upload, use the base sheet name
    if not existing_sheet_names:
        return base_sheet
    
    # Count existing sheets with this base name
    base_pattern = f"{base_sheet}_"
    similar_sheets = [s for s in existing_sheet_names if s.startswith(base_pattern)]
    
    if not similar_sheets:
        # Check if base sheet exists
        if base_sheet in existing_sheet_names:
            return f"{base_sheet}_1"
        else:
            return base_sheet
    
    # Find the highest number
    max_num = 0
    for sheet in similar_sheets:
        try:
            num = int(sheet.split('_')[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass
    
    return f"{base_sheet}_{max_num + 1}"


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
    new_sheet_names = []

    for sheet, records in data.items():
        # Generate progressive sheet name
        new_sheet_name = generate_sheet_name(db, sheet)
        new_sheet_names.append(new_sheet_name)
        
        for item in records:
            # Add the new sheet name
            item["source_sheet"] = new_sheet_name

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
            # SMART DEDUP CHECK
            # ---------------------------
            filters = []
            
            # Only check non-null fields for deduplication
            if item.get("email"):
                filters.append(Contact.email == item["email"])
            
            if item.get("mobile"):
                filters.append(Contact.mobile == item["mobile"])
            
            if item.get("landline"):
                filters.append(Contact.landline == item["landline"])
            
            exists = None
            if filters:
                exists = db.query(Contact).filter(or_(*filters)).first()
            else:
                # Fallback: check by company + HR name if no contact info
                if item.get("company_name") and item.get("hr_name"):
                    exists = db.query(Contact).filter(
                        and_(
                            Contact.company_name == item["company_name"],
                            Contact.hr_name == item["hr_name"]
                        )
                    ).first()

            if not exists:
                db.add(Contact(**item))
                inserted += 1

    db.commit()

    return {
        "inserted": inserted,
        "skipped_invalid_email": skipped_invalid_email,
        "original_sheets": list(data.keys()),
        "new_sheets": new_sheet_names
    }