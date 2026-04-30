from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import AccessLog

LIMIT = 10

def check_limit(db: Session, ip: str):
    last_24h = datetime.utcnow() - timedelta(hours=24)

    count = db.query(AccessLog).filter(
        AccessLog.user_ip == ip,
        AccessLog.timestamp >= last_24h
    ).count()

    return count < LIMIT