from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import Optional

from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def get_all_users(skip: int = 0, limit: int = 50, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents({})
    
    return {"users": users, "total": total, "skip": skip, "limit": limit}

@router.get("/stats")
async def get_admin_stats(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = await db.users.count_documents({})
    total_accounts = await db.instagram_accounts.count_documents({})
    total_audits = await db.audits.count_documents({})
    total_content = await db.content_items.count_documents({})
    total_teams = await db.teams.count_documents({})
    
    plan_distribution = {}
    for plan in ["starter", "pro", "agency", "enterprise"]:
        plan_distribution[plan] = await db.users.count_documents({"role": plan})
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_audits": total_audits,
        "total_content": total_content,
        "total_teams": total_teams,
        "plan_distribution": plan_distribution
    }

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, request: Request):
    db = get_database()
    admin = await get_current_user(request, db)
    
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if role not in ["starter", "pro", "agency", "enterprise", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    PLAN_LIMITS = {
        "starter": {"accounts": 1, "ai_usage": 10},
        "pro": {"accounts": 5, "ai_usage": 100},
        "agency": {"accounts": 25, "ai_usage": 500},
        "enterprise": {"accounts": 100, "ai_usage": 2000},
        "admin": {"accounts": 999, "ai_usage": 9999}
    }
    
    limits = PLAN_LIMITS[role]
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {
            "role": role,
            "account_limit": limits["accounts"],
            "ai_usage_limit": limits["ai_usage"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User role updated to {role}"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    db = get_database()
    admin = await get_current_user(request, db)
    
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    await db.users.delete_one({"user_id": user_id})
    await db.instagram_accounts.delete_many({"user_id": user_id})
    await db.audits.delete_many({"user_id": user_id})
    await db.content_items.delete_many({"user_id": user_id})
    await db.growth_plans.delete_many({"user_id": user_id})
    await db.notifications.delete_many({"user_id": user_id})
    
    return {"message": "User and related data deleted"}
