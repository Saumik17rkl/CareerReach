from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from routers.mongodb_contacts_simple import get_contact_ops

router = APIRouter()

class SubmissionCreate(BaseModel):
    company_name: str
    hr_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None

@router.post("/submit-contact")
async def submit_contact(submission: SubmissionCreate):
    ops = get_contact_ops()
    
    try:
        contact_data = {
            "company_name": submission.company_name,
            "hr_name": submission.hr_name,
            "email": submission.email,
            "mobile": submission.phone,
            "landline": None,
            "role": submission.role,
            "location": submission.location,
            "source_sheet": "Manual_Entry"
        }
        
        duplicate = ops.check_duplicate(contact_data)
        if duplicate:
            raise HTTPException(status_code=400, detail="Contact already exists")
        
        contact_id = ops.create_contact(contact_data)
        
        return {
            "message": "Contact submitted successfully",
            "contact_id": contact_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact: {str(e)}")
