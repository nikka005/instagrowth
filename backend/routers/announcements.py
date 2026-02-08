"""
In-App Announcements System
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from database import get_database
from dependencies import get_current_user
from routers.admin_panel_auth import verify_admin_token

router = APIRouter(prefix="/announcements", tags=["Announcements"])

# ==================== USER ENDPOINTS ====================

@router.get("")
async def get_active_announcements(request: Request = None):
    """Get active announcements for users"""
    db = get_database()
    
    now = datetime.now(timezone.utc).isoformat()
    
    announcements = await db.announcements.find({
        "status": "active",
        "start_date": {"$lte": now},
        "$or": [
            {"end_date": None},
            {"end_date": {"$gte": now}}
        ]
    }, {"_id": 0}).sort("created_at", -1).to_list(10)
    
    return {"announcements": announcements}

@router.post("/{announcement_id}/dismiss")
async def dismiss_announcement(announcement_id: str, request: Request = None):
    """Dismiss an announcement for the user"""
    db = get_database()
    user = await get_current_user(request, db)
    
    await db.user_dismissed_announcements.update_one(
        {"user_id": user.user_id, "announcement_id": announcement_id},
        {"$set": {
            "dismissed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"message": "Announcement dismissed"}

@router.get("/unread")
async def get_unread_announcements(request: Request = None):
    """Get unread announcements for a user"""
    db = get_database()
    user = await get_current_user(request, db)
    
    # Get dismissed announcement IDs
    dismissed = await db.user_dismissed_announcements.find(
        {"user_id": user.user_id},
        {"announcement_id": 1}
    ).to_list(100)
    dismissed_ids = [d["announcement_id"] for d in dismissed]
    
    now = datetime.now(timezone.utc).isoformat()
    
    announcements = await db.announcements.find({
        "status": "active",
        "announcement_id": {"$nin": dismissed_ids},
        "start_date": {"$lte": now},
        "$or": [
            {"end_date": None},
            {"end_date": {"$gte": now}}
        ]
    }, {"_id": 0}).sort("created_at", -1).to_list(10)
    
    return {"announcements": announcements, "count": len(announcements)}

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/all")
async def get_all_announcements_admin(request: Request = None):
    """Get all announcements (admin)"""
    db = get_database()
    await verify_admin_token(request)
    
    announcements = await db.announcements.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"announcements": announcements}

@router.post("/admin/create")
async def create_announcement(
    title: str,
    message: str,
    type: str = "info",
    target: str = "all",
    start_date: str = None,
    end_date: str = None,
    link_url: str = None,
    link_text: str = None,
    request: Request = None
):
    """Create a new announcement"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    announcement_id = f"ANN-{uuid.uuid4().hex[:8].upper()}"
    
    announcement = {
        "announcement_id": announcement_id,
        "title": title,
        "message": message,
        "type": type,  # info, warning, success, update, maintenance
        "target": target,  # all, free, paid, starter, pro, agency, enterprise
        "status": "active",
        "start_date": start_date or datetime.now(timezone.utc).isoformat(),
        "end_date": end_date,
        "link_url": link_url,
        "link_text": link_text,
        "created_by": admin["admin_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.announcements.insert_one(announcement)
    del announcement["_id"]
    
    return announcement

@router.put("/admin/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    title: str = None,
    message: str = None,
    type: str = None,
    status: str = None,
    end_date: str = None,
    request: Request = None
):
    """Update an announcement"""
    db = get_database()
    await verify_admin_token(request)
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if title:
        update_data["title"] = title
    if message:
        update_data["message"] = message
    if type:
        update_data["type"] = type
    if status:
        update_data["status"] = status
    if end_date:
        update_data["end_date"] = end_date
    
    result = await db.announcements.update_one(
        {"announcement_id": announcement_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"message": "Announcement updated"}

@router.delete("/admin/{announcement_id}")
async def delete_announcement(announcement_id: str, request: Request = None):
    """Delete an announcement"""
    db = get_database()
    await verify_admin_token(request)
    
    result = await db.announcements.delete_one({"announcement_id": announcement_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"message": "Announcement deleted"}
