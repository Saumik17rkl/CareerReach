from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Submission
from app.schemas.schemas import SubmissionCreate

router = APIRouter()

@router.post("/submit-contact")
def submit_contact(data: SubmissionCreate, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host

    entry = Submission(**data.dict(), submitted_by_ip=ip)
    db.add(entry)
    db.commit()

    return {"message": "Submitted"}