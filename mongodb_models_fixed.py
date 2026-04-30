from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr

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
        try:
            from mongodb_fixed import get_mongodb
            self.db = get_mongodb()
            if self.db:
                self.contacts = self.db["contacts"]
                self.access_logs = self.db["access_logs"]
            else:
                raise Exception("MongoDB not available")
        except Exception as e:
            print(f"MongoDB initialization failed: {e}")
            self.db = None
            self.contacts = None
            self.access_logs = None
    
    def is_available(self):
        """Check if MongoDB is available"""
        return self.db is not None and self.contacts is not None
    
    def create_contact(self, contact_data: Dict[str, Any]) -> str:
        """Create a new contact"""
        if not self.is_available():
            raise Exception("MongoDB not available")
        
        contact_data["created_at"] = datetime.utcnow()
        contact_data["updated_at"] = datetime.utcnow()
        result = self.contacts.insert_one(contact_data)
        return str(result.inserted_id)
    
    def get_contact_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID"""
        if not self.is_available():
            return None
        
        try:
            # Try with ObjectId
            from bson import ObjectId
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
            print(f"Error getting contact: {e}")
            return None
    
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts"""
        if not self.is_available():
            return []
        
        try:
            contacts = list(self.contacts.find({}))
            for contact in contacts:
                contact["id"] = str(contact["_id"])
                del contact["_id"]
            return contacts
        except Exception as e:
            print(f"Error getting all contacts: {e}")
            return []
    
    def get_contacts_by_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Get contacts by sheet name"""
        if not self.is_available():
            return []
        
        try:
            contacts = list(self.contacts.find({"source_sheet": sheet_name}))
            for contact in contacts:
                contact["id"] = str(contact["_id"])
                del contact["_id"]
            return contacts
        except Exception as e:
            print(f"Error getting contacts by sheet: {e}")
            return []
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search contacts by company name or HR name"""
        if not self.is_available():
            return []
        
        try:
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
        except Exception as e:
            print(f"Error searching contacts: {e}")
            return []
    
    def get_all_sheets(self) -> List[str]:
        """Get all unique sheet names"""
        if not self.is_available():
            return []
        
        try:
            sheets = self.contacts.distinct("source_sheet")
            return sheets
        except Exception as e:
            print(f"Error getting sheets: {e}")
            return []
    
    def delete_contacts_by_sheet(self, sheet_name: str) -> int:
        """Delete all contacts from a specific sheet"""
        if not self.is_available():
            return 0
        
        try:
            result = self.contacts.delete_many({"source_sheet": sheet_name})
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting contacts by sheet: {e}")
            return 0
    
    def check_duplicate(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for duplicate contact"""
        if not self.is_available():
            return None
        
        try:
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
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return None
    
    def create_access_log(self, log_data: Dict[str, Any]) -> str:
        """Create access log"""
        if not self.is_available():
            return ""
        
        try:
            log_data["accessed_at"] = datetime.utcnow()
            result = self.access_logs.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating access log: {e}")
            return ""
    
    def get_access_logs_by_ip(self, ip: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get access logs by IP address"""
        if not self.is_available():
            return []
        
        try:
            logs = list(self.access_logs.find({"user_ip": ip}).sort("accessed_at", -1).limit(limit))
            for log in logs:
                log["id"] = str(log["_id"])
                del log["_id"]
            return logs
        except Exception as e:
            print(f"Error getting access logs: {e}")
            return []
