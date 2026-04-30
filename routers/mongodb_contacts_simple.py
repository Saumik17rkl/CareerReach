from fastapi import APIRouter, Depends, Request, HTTPException, Query
from typing import Dict, Any, List

router = APIRouter(prefix="/contacts")

# Simple in-memory fallback for testing
class SimpleContactOps:
    def __init__(self):
        self.contacts = {}
        self.next_id = 1
    
    def is_available(self):
        return True
    
    def get_all_sheets(self):
        sheets = set()
        for contact in self.contacts.values():
            if "source_sheet" in contact:
                sheets.add(contact["source_sheet"])
        return list(sheets)
    
    def get_contacts_by_sheet(self, sheet_name):
        return [contact for contact in self.contacts.values() if contact.get("source_sheet") == sheet_name]
    
    def create_contact(self, contact_data):
        contact_id = str(self.next_id)
        contact_data["id"] = contact_id
        self.contacts[contact_id] = contact_data
        self.next_id += 1
        return contact_id
    
    def check_duplicate(self, contact_data):
        for contact in self.contacts.values():
            if (contact_data.get("email") and contact.get("email") == contact_data["email"]) or \
               (contact_data.get("mobile") and contact.get("mobile") == contact_data["mobile"]):
                return contact
        return None


# Keep a single in-memory store for the whole process so data persists across requests
_OPS_SINGLETON = SimpleContactOps()

def get_contact_ops():
    return _OPS_SINGLETON

@router.get("/")
def get_contacts(sheet: str = Query(None), search: str = Query(None), ops: SimpleContactOps = Depends(get_contact_ops)):
    if sheet:
        contacts = ops.get_contacts_by_sheet(sheet)
        result = {}
        for contact in contacts:
            cleaned = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
            if cleaned:
                result[contact["id"]] = cleaned
        return {"sheet": sheet, "data": result}
    else:
        # Return all contacts grouped by sheet
        grouped = {}
        for contact in ops.contacts.values():
            sheet = contact.get("source_sheet", "Unknown")
            if sheet not in grouped:
                grouped[sheet] = {}
            cleaned = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
            if cleaned:
                grouped[sheet][contact["id"]] = cleaned
        return {"data": grouped}

@router.get("/sheets")
def get_sheets(ops: SimpleContactOps = Depends(get_contact_ops)):
    return ops.get_all_sheets()

@router.get("/{contact_id}")
def get_contact(contact_id: str, request: Request, ops: SimpleContactOps = Depends(get_contact_ops)):
    contact = ops.contacts.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    cleaned = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
    return cleaned

@router.delete("/sheets/{sheet_name}")
def delete_sheet(sheet_name: str, ops: SimpleContactOps = Depends(get_contact_ops)):
    contacts_to_delete = [contact_id for contact_id, contact in ops.contacts.items() 
                        if contact.get("source_sheet") == sheet_name]
    
    if not contacts_to_delete:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    for contact_id in contacts_to_delete:
        del ops.contacts[contact_id]
    
    return {
        "message": f"Sheet '{sheet_name}' deleted successfully",
        "deleted_contacts": len(contacts_to_delete)
    }
