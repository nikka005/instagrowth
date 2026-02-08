from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List

from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def get_notifications(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    notifications = await db.notifications.find(
        {"user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    return notifications

@router.get("/unread-count")
async def get_unread_count(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    count = await db.notifications.count_documents({"user_id": user.user_id, "read": False})
    return {"count": count}

@router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": user.user_id},
        {"$set": {"read": True}}
    )
    return {"message": "Notification marked as read"}

@router.put("/read-all")
async def mark_all_read(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    await db.notifications.update_many(
        {"user_id": user.user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}
