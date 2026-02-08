"""
Admin Support Ticket Management
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from database import get_database
from routers.admin_panel_auth import verify_admin_token
from services import send_email

router = APIRouter(prefix="/admin-panel/tickets", tags=["Admin Tickets"])

@router.get("")
async def get_all_tickets(
    status: str = None,
    priority: str = None,
    category: str = None,
    search: str = None,
    limit: int = 50,
    skip: int = 0,
    request: Request = None
):
    """Get all support tickets"""
    db = get_database()
    await verify_admin_token(request)
    
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"subject": {"$regex": search, "$options": "i"}},
            {"user_email": {"$regex": search, "$options": "i"}},
            {"ticket_id": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.support_tickets.count_documents(query)
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Get counts by status
    open_count = await db.support_tickets.count_documents({"status": "open"})
    pending_count = await db.support_tickets.count_documents({"status": "pending"})
    closed_count = await db.support_tickets.count_documents({"status": "closed"})
    
    return {
        "tickets": tickets,
        "total": total,
        "counts": {
            "open": open_count,
            "pending": pending_count,
            "closed": closed_count
        }
    }

@router.get("/stats")
async def get_ticket_stats(request: Request = None):
    """Get support ticket statistics"""
    db = get_database()
    await verify_admin_token(request)
    
    total = await db.support_tickets.count_documents({})
    open_tickets = await db.support_tickets.count_documents({"status": "open"})
    pending_tickets = await db.support_tickets.count_documents({"status": "pending"})
    closed_tickets = await db.support_tickets.count_documents({"status": "closed"})
    
    # Priority counts
    urgent = await db.support_tickets.count_documents({"priority": "urgent", "status": {"$ne": "closed"}})
    high = await db.support_tickets.count_documents({"priority": "high", "status": {"$ne": "closed"}})
    
    # Category breakdown
    pipeline = [
        {"$match": {"status": {"$ne": "closed"}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    category_counts = await db.support_tickets.aggregate(pipeline).to_list(20)
    
    return {
        "total": total,
        "open": open_tickets,
        "pending": pending_tickets,
        "closed": closed_tickets,
        "urgent": urgent,
        "high_priority": high,
        "by_category": {item["_id"]: item["count"] for item in category_counts}
    }

@router.get("/{ticket_id}")
async def get_ticket_admin(ticket_id: str, request: Request = None):
    """Get a specific ticket (admin)"""
    db = get_database()
    await verify_admin_token(request)
    
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id}, {"_id": 0})
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

@router.post("/{ticket_id}/reply")
async def admin_reply_to_ticket(
    ticket_id: str,
    message: str,
    request: Request = None
):
    """Admin reply to a ticket"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    ticket = await db.support_tickets.find_one({"ticket_id": ticket_id})
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    new_message = {
        "message_id": f"MSG-{admin['admin_id'][:8]}",
        "sender_type": "admin",
        "sender_id": admin["admin_id"],
        "sender_name": admin["name"],
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
                "status": "pending",
                "assigned_to": admin["admin_id"]
            }
        }
    )
    
    # Send email notification to user
    try:
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">New Reply to Your Ticket</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
                <p>Hi {ticket['user_name']},</p>
                <p>Our support team has replied to your ticket:</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #6366f1;">
                    <p style="margin: 0; font-style: italic;">"{message[:200]}{'...' if len(message) > 200 else ''}"</p>
                </div>
                <p style="margin: 0;"><strong>Ticket ID:</strong> {ticket_id}</p>
                <p style="margin: 10px 0;"><strong>Subject:</strong> {ticket['subject']}</p>
                <p style="font-size: 14px; color: #666; margin-top: 20px;">Log in to your dashboard to view the full conversation and reply.</p>
            </div>
        </div>
        """
        await send_email(ticket["user_email"], f"Re: {ticket['subject']} [{ticket_id}]", email_html)
    except:
        pass
    
    return {"message": "Reply added", "message_id": new_message["message_id"]}

@router.put("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    status: str,
    request: Request = None
):
    """Update ticket status"""
    db = get_database()
    await verify_admin_token(request)
    
    if status not in ["open", "pending", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    update_data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if status == "closed":
        update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": f"Ticket status updated to {status}"}

@router.put("/{ticket_id}/priority")
async def update_ticket_priority(
    ticket_id: str,
    priority: str,
    request: Request = None
):
    """Update ticket priority"""
    db = get_database()
    await verify_admin_token(request)
    
    if priority not in ["low", "normal", "high", "urgent"]:
        raise HTTPException(status_code=400, detail="Invalid priority")
    
    result = await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {"$set": {
            "priority": priority,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": f"Ticket priority updated to {priority}"}

@router.put("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    admin_id: str = None,
    request: Request = None
):
    """Assign ticket to an admin"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    assign_to = admin_id if admin_id else admin["admin_id"]
    
    result = await db.support_tickets.update_one(
        {"ticket_id": ticket_id},
        {"$set": {
            "assigned_to": assign_to,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket assigned"}

@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id: str, request: Request = None):
    """Delete a ticket (super admin only)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    result = await db.support_tickets.delete_one({"ticket_id": ticket_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket deleted"}
