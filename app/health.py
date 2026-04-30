from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine
from sqlalchemy import text
import os

router = APIRouter()

@router.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "ReachBridge API",
        "version": "1.0.0"
    }

@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies database connection"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "database": "connected",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@router.get("/health/live")
def liveness_check():
    """Liveness check - basic service availability"""
    return {
        "status": "alive",
        "timestamp": str(datetime.utcnow())
    }
