from fastapi import APIRouter, Depends, Request, HTTPException, Query
from typing import Dict, Any, List
from models.mongodb_models import MongoContactOperations
from mongodb import get_mongodb
import json

router = APIRouter(prefix="/contacts")

def get_contact_ops():
    return MongoContactOperations()

# ---------------------------
# GET CONTACTS (ALL / FILTERED)
# ---------------------------
@router.get("/")
def get_contacts(
    request: Request,
    sheet: str = Query(None),
    search: str = Query(None),
    ops: MongoContactOperations = Depends(get_contact_ops)
):
    try:
        if sheet:
            # Get contacts for specific sheet
            contacts = ops.get_contacts_by_sheet(sheet)
            result = {}
            for contact in contacts:
                cleaned_contact = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
                if cleaned_contact:
                    result[contact["id"]] = cleaned_contact
            return {"sheet": sheet, "data": result}
        elif search:
            # Search contacts
            contacts = ops.search_contacts(search)
            result = {}
            for contact in contacts:
                cleaned_contact = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
                if cleaned_contact:
                    result[contact["id"]] = cleaned_contact
            return {"data": result}
        else:
            # Get all contacts grouped by sheet
            all_contacts = ops.get_all_contacts()
            grouped = {}
            for contact in all_contacts:
                sheet_name = contact.get("source_sheet", "Unknown")
                if sheet_name not in grouped:
                    grouped[sheet_name] = {}
                
                cleaned_contact = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
                if cleaned_contact:
                    grouped[sheet_name][contact["id"]] = cleaned_contact
            
            return {"data": grouped}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contacts: {str(e)}")

# ---------------------------
# GET SHEET NAMES
# ---------------------------
@router.get("/sheets")
def get_sheets(ops: MongoContactOperations = Depends(get_contact_ops)):
    try:
        sheets = ops.get_all_sheets()
        return sheets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sheets: {str(e)}")

# ---------------------------
# GET FULL CONTACT (LIMITED)
# ---------------------------
@router.get("/{contact_id}")
def get_contact(contact_id: str, request: Request, ops: MongoContactOperations = Depends(get_contact_ops)):
    try:
        contact = ops.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Log access
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        ops.create_access_log({
            "user_ip": ip,
            "user_agent": user_agent,
            "contact_id": contact_id
        })
        
        # Clean response
        cleaned_contact = {k: v for k, v in contact.items() if v not in [None, "", "Invalid Email"]}
        return cleaned_contact
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contact: {str(e)}")

# ---------------------------
# DELETE SHEET
# ---------------------------
@router.delete("/sheets/{sheet_name}")
def delete_sheet(sheet_name: str, ops: MongoContactOperations = Depends(get_contact_ops)):
    try:
        # Check if sheet exists
        contacts = ops.get_contacts_by_sheet(sheet_name)
        if not contacts:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        # Delete all contacts from the sheet
        deleted_count = ops.delete_contacts_by_sheet(sheet_name)
        
        return {
            "message": f"Sheet '{sheet_name}' deleted successfully",
            "deleted_contacts": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting sheet: {str(e)}")
