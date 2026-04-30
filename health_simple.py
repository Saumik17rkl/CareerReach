from datetime import datetime
from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "CareerReach API",
        "version": "2.0.0"
    }

@router.get("/health/ready")
def readiness_check():
    """Readiness check - verifies service is ready"""
    return {
        "status": "ready",
        "database": "in-memory",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/health/live")
def liveness_check():
    """Liveness check - basic service availability"""
    return {
        "status": "alive",
        "timestamp": str(datetime.utcnow())
    }
