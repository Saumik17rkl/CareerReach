from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from mongodb import get_mongodb

class MongoContact(BaseModel):
    id: Optional[str] = None
    company_name: str
    hr_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    landline: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    source_sheet: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class MongoAccessLog(BaseModel):
    id: Optional[str] = None
    user_ip: str
    user_agent: str
    contact_id: str
    accessed_at: datetime = datetime.utcnow()

class MongoContactOperations:
    def __init__(self):
        self.db = get_mongodb()
        self.contacts = self.db["contacts"]
        self.access_logs = self.db["access_logs"]
    
    def create_contact(self, contact_data: Dict[str, Any]) -> str:
        """Create a new contact"""
        contact_data["created_at"] = datetime.utcnow()
        contact_data["updated_at"] = datetime.utcnow()
        result = self.contacts.insert_one(contact_data)
        return str(result.inserted_id)
    
    def get_contact_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID"""
        try:
            # Try with ObjectId first
            from pymongo import ObjectId
            try:
                contact = self.contacts.find_one({"_id": ObjectId(contact_id)})
                if contact:
                    contact["id"] = str(contact["_id"])
                    del contact["_id"]
                return contact
            except:
                # Try with string ID
                contact = self.contacts.find_one({"_id": contact_id})
                if contact:
                    contact["id"] = str(contact["_id"])
                    del contact["_id"]
                return contact
        except Exception as e:
            return None
    
    def get_all_contacts(self) -> list:
        """Get all contacts"""
        contacts = list(self.contacts.find({}))
        for contact in contacts:
            contact["id"] = str(contact["_id"])
            del contact["_id"]
        return contacts
    
    def get_contacts_by_sheet(self, sheet_name: str) -> list:
        """Get contacts by sheet name"""
        contacts = list(self.contacts.find({"source_sheet": sheet_name}))
        for contact in contacts:
            contact["id"] = str(contact["_id"])
            del contact["_id"]
        return contacts
    
    def search_contacts(self, query: str) -> list:
        """Search contacts by company name or HR name"""
        search_filter = {
            "$or": [
                {"company_name": {"$regex": query, "$options": "i"}},
                {"hr_name": {"$regex": query, "$options": "i"}}
            ]
        }
        contacts = list(self.contacts.find(search_filter))
        for contact in contacts:
            contact["id"] = str(contact["_id"])
            del contact["_id"]
        return contacts
    
    def get_all_sheets(self) -> list:
        """Get all unique sheet names"""
        sheets = self.contacts.distinct("source_sheet")
        return sheets
    
    def delete_contacts_by_sheet(self, sheet_name: str) -> int:
        """Delete all contacts from a specific sheet"""
        result = self.contacts.delete_many({"source_sheet": sheet_name})
        return result.deleted_count
    
    def check_duplicate(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for duplicate contact"""
        filters = []
        
        if contact_data.get("email"):
            filters.append({"email": contact_data["email"]})
        
        if contact_data.get("mobile"):
            filters.append({"mobile": contact_data["mobile"]})
        
        if contact_data.get("landline"):
            filters.append({"landline": contact_data["landline"]})
        
        if filters:
            duplicate = self.contacts.find_one({"$or": filters})
            if duplicate:
                duplicate["id"] = str(duplicate["_id"])
                del duplicate["_id"]
                return duplicate
        
        return None
    
    def create_access_log(self, log_data: Dict[str, Any]) -> str:
        """Create access log"""
        log_data["accessed_at"] = datetime.utcnow()
        result = self.access_logs.insert_one(log_data)
        return str(result.inserted_id)
    
    def get_access_logs_by_ip(self, ip: str, limit: int = 10) -> list:
        """Get access logs by IP address"""
        logs = list(self.access_logs.find({"user_ip": ip}).sort("accessed_at", -1).limit(limit))
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
