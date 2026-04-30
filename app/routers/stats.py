from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Contact, Submission, Application

router = APIRouter()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "contacts": db.query(Contact).count(),
        "submissions": db.query(Submission).count(),
        "applications": db.query(Application).count(),
    }