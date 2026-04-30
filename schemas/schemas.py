from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactBase(BaseModel):
    company_name: str
    hr_name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    role: Optional[str]
    location: Optional[str]


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True


class SubmissionCreate(ContactBase):
    pass


class ApplicationCreate(BaseModel):
    user_name: str
    company_name: str
    hr_name: str
    email: Optional[EmailStr]
    phone: Optional[str]