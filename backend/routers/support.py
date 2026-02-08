"""
Support Ticket System Router
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from database import get_database
from dependencies import get_current_user
from services import send_email

router = APIRouter(prefix="/support", tags=["Support"])

# ==================== USER ENDPOINTS ====================

@router.post("/tickets")
async def create_ticket(
    subject: str,
    message: str,
    category: str = "general",
    priority: str = "normal",
    request: Request = None
):
    """Create a new support ticket"""
    db = get_database()
    user = await get_current_user(request, db)
    
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    ticket = {
        "ticket_id": ticket_id,
        "user_id": user.user_id,
        "user_email": user.email,
        "user_name": user.name,
        "subject": subject,
        "category": category,  # general, billing, technical, feature, bug
        "priority": priority,  # low, normal, high, urgent
        "status": "open",
        "messages": [{
            "message_id": f"MSG-{uuid.uuid4().hex[:8]}",
            "sender_type": "user",
            "sender_id": user.user_id,
            "sender_name": user.name,
            "message": message,
            "attachments": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
        "assigned_to": None
    }
    
    await db.support_tickets.insert_one(ticket)
    
    # Send confirmation email
    try:
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Support Ticket Created</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
                <p>Hi {user.name},</p>
                <p>We've received your support request and our team will get back to you soon.</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Ticket ID:</strong> {ticket_id}</p>
                    <p style="margin: 10px 0 0 0;"><strong>Subject:</strong> {subject}</p>
                    <p style="margin: 10px 0 0 0;"><strong>Category:</strong> {category}</p>
                </div>
                <p style="font-size: 14px; color: #666;">You can view your ticket status in your dashboard.</p>
            </div>
        </div>
        """
        await send_email(user.email, f"Support Ticket #{ticket_id} Created", email_html)
    except:
        pass
    
    del ticket["_id"]
    return ticket

@router.get("/tickets")
async def get_user_tickets(
    status: str = None,
    request: Request = None
):
    """Get user's support tickets"""
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if status:
        query["status"] = status
    
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"tickets": tickets}

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, request: Request = None):
    """Get a specific ticket"""
    db = get_database()
    user = await get_current_user(request, db)
    
    ticket = await db.support_tickets.find_one(
        {"ticket_id": ticket_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

@router.post("/tickets/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: str,
    message: str,
    request: Request = None
):
    """Add a reply to a ticket"""
    db = get_database()
    user = await get_current_user(request, db)
    
    ticket = await db.support_tickets.find_one(
        {"ticket_id": ticket_id, "user_id": user.user_id}
    )
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket["status"] == "closed":
        raise HTTPException(status_code=400, detail="Cannot reply to closed ticket")
    
    new_message = {
        "message_id": f"MSG-{uuid.uuid4().hex[:8]}",
        "sender_type": "user",
        "sender_id": user.user_id,
        "sender_name": user.name,
        "message": message,
        "attachments": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {
            "$push": {"messages": new_message},
            "$set": {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "open" if ticket["status"] == "pending" else ticket["status"]
            }
        }
    )
    
    return {"message": "Reply added", "message_id": new_message["message_id"]}

@router.post("/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: str, request: Request = None):
    """Close a ticket"""
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.support_tickets.update_one(
        {"ticket_id": ticket_id, "user_id": user.user_id},
        {"$set": {
            "status": "closed",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket closed"}
