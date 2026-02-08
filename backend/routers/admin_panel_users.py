from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid
from io import StringIO
import csv

from database import get_database
from routers.admin_panel_auth import verify_admin_token, check_permission, log_admin_action, get_client_ip
from utils import hash_password

router = APIRouter(prefix="/admin-panel", tags=["Admin Panel - Users"])

# ==================== USER MANAGEMENT ====================

@router.get("/users")
async def get_all_users(
    skip: int = 0, 
    limit: int = 50, 
    search: str = None,
    plan: str = None,
    status: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    request: Request = None
):
    """Get all users with filters"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    query = {}
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}}
        ]
    if plan:
        query["role"] = plan
    if status:
        query["status"] = status
    
    sort_dir = -1 if sort_order == "desc" else 1
    
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort(sort_by, sort_dir).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents(query)
    
    # Enrich with account counts
    for user in users:
        user["accounts_count"] = await db.instagram_accounts.count_documents({"user_id": user["user_id"]})
        user["audits_count"] = await db.audits.count_documents({"user_id": user["user_id"]})
    
    return {"users": users, "total": total, "skip": skip, "limit": limit}

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, request: Request):
    """Get detailed user info"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get related data
    accounts = await db.instagram_accounts.find({"user_id": user_id}, {"_id": 0}).to_list(100)
    audits = await db.audits.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    subscription = await db.subscriptions.find_one({"user_id": user_id, "status": "active"}, {"_id": 0})
    
    # AI usage history
    ai_usage = {
        "current_month": user.get("ai_usage_current", 0),
        "limit": user.get("ai_usage_limit", 10)
    }
    
    return {
        "user": user,
        "accounts": accounts,
        "recent_audits": audits,
        "subscription": subscription,
        "ai_usage": ai_usage
    }

@router.put("/users/{user_id}/plan")
async def change_user_plan(user_id: str, plan: str, request: Request):
    """Change user's plan"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    PLAN_LIMITS = {
        "starter": {"accounts": 1, "ai_usage": 10},
        "pro": {"accounts": 5, "ai_usage": 100},
        "agency": {"accounts": 25, "ai_usage": 500},
        "enterprise": {"accounts": 100, "ai_usage": 2000},
        "admin": {"accounts": 999, "ai_usage": 9999}
    }
    
    if plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_plan = user.get("role", "starter")
    limits = PLAN_LIMITS[plan]
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {
            "role": plan,
            "account_limit": limits["accounts"],
            "ai_usage_limit": limits["ai_usage"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_admin_action(admin, "change_plan", "user", user_id, {"old_plan": old_plan, "new_plan": plan}, get_client_ip(request))
    
    return {"message": f"User plan changed to {plan}"}

@router.put("/users/{user_id}/status")
async def update_user_status(user_id: str, status: str, request: Request):
    """Block/Unblock user"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    if status not in ["active", "blocked", "suspended"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, f"user_{status}", "user", user_id, {}, get_client_ip(request))
    
    return {"message": f"User status updated to {status}"}

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: str, new_password: str, request: Request):
    """Reset user's password"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"password_hash": hash_password(new_password), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, "reset_password", "user", user_id, {}, get_client_ip(request))
    
    return {"message": "Password reset successfully"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    """Delete user and all related data"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete all related data
    await db.users.delete_one({"user_id": user_id})
    await db.instagram_accounts.delete_many({"user_id": user_id})
    await db.audits.delete_many({"user_id": user_id})
    await db.content_items.delete_many({"user_id": user_id})
    await db.growth_plans.delete_many({"user_id": user_id})
    await db.notifications.delete_many({"user_id": user_id})
    await db.dm_templates.delete_many({"user_id": user_id})
    await db.subscriptions.delete_many({"user_id": user_id})
    
    await log_admin_action(admin, "delete_user", "user", user_id, {"email": user.get("email")}, get_client_ip(request))
    
    return {"message": "User deleted successfully"}

@router.get("/users/export/csv")
async def export_users_csv(request: Request):
    """Export users to CSV"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "users")
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(10000)
    
    output = StringIO()
    fields = ["user_id", "name", "email", "role", "account_limit", "ai_usage_current", "ai_usage_limit", "email_verified", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(users)
    
    await log_admin_action(admin, "export_users", "users", None, {"count": len(users)}, get_client_ip(request))
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )
