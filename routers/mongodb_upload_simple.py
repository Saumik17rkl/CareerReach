from fastapi import APIRouter, UploadFile, HTTPException
from services.excel_parser import parse_excel
from routers.mongodb_contacts_simple import get_contact_ops

router = APIRouter()

def is_valid_email(email):
    if not email:
        return False
    if not isinstance(email, str):
        return False
    email = email.strip()
    return "@" in email and "." in email

def clean_phone(phone):
    if not phone:
        return None
    if isinstance(phone, float):
        if str(phone) == "nan":
            return None
        phone = str(int(phone))
    if isinstance(phone, str):
        phone = phone.strip()
        phone = phone.replace(" ", "").replace("-", "")
        return phone if phone.isdigit() else None
    return None

def generate_sheet_name(ops, base_sheet):
    existing_sheets = ops.get_all_sheets()
    if not existing_sheets:
        return base_sheet
    
    base_pattern = f"{base_sheet}_"
    similar_sheets = [s for s in existing_sheets if s.startswith(base_pattern)]
    
    if not similar_sheets:
        if base_sheet in existing_sheets:
            return f"{base_sheet}_1"
        else:
            return base_sheet
    
    max_num = 0
    for sheet in similar_sheets:
        try:
            num = int(sheet.split('_')[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass
    
    return f"{base_sheet}_{max_num + 1}"

@router.post("/upload-excel")
async def upload_excel(file: UploadFile):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files allowed")
    
    ops = get_contact_ops()
    
    try:
        data = parse_excel(file.file)
        
        inserted = 0
        skipped_invalid_email = 0
        skipped_duplicates = 0
        new_sheet_names = []
        
        for sheet, records in data.items():
            new_sheet_name = generate_sheet_name(ops, sheet)
            new_sheet_names.append(new_sheet_name)
            
            for item in records:
                item["source_sheet"] = new_sheet_name
                
                if not is_valid_email(item.get("email")):
                    item["email"] = None
                    skipped_invalid_email += 1
                
                item["mobile"] = clean_phone(item.get("mobile"))
                item["landline"] = clean_phone(item.get("landline"))
                
                duplicate = ops.check_duplicate(item)
                if duplicate:
                    skipped_duplicates += 1
                    continue
                
                ops.create_contact(item)
                inserted += 1
        
        return {
            "inserted": inserted,
            "skipped_invalid_email": skipped_invalid_email,
            "skipped_duplicates": skipped_duplicates,
            "original_sheets": list(data.keys()),
            "new_sheets": new_sheet_names
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Excel file: {str(e)}")
