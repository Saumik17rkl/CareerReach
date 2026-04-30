from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    hr_name = Column(String)
    email = Column(String, nullable=True, index=True)
    mobile = Column(String, nullable=True, index=True)
    landline = Column(String, nullable=True, index=True)
    role = Column(String)
    location = Column(String)
    source_sheet = Column(String)


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True)
    user_ip = Column(String)
    user_agent = Column(String)
    contact_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    hr_name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=True)
    location = Column(String, nullable=True)
    submitted_by_ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    company_name = Column(String)
    hr_name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)