from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from database import get_database
from routers.admin_panel_auth import verify_admin_token, check_permission, log_admin_action, get_client_ip

router = APIRouter(prefix="/admin-panel", tags=["Admin Panel - Subscriptions & Plans"])

# ==================== SUBSCRIPTION MANAGEMENT ====================

@router.get("/subscriptions")
async def get_all_subscriptions(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    plan: str = None,
    request: Request = None
):
    """Get all subscriptions"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "subscriptions")
    
    query = {}
    if status:
        query["status"] = status
    if plan:
        query["plan_id"] = plan
    
    subscriptions = await db.subscriptions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.subscriptions.count_documents(query)
    
    # Enrich with user info
    for sub in subscriptions:
        user = await db.users.find_one({"user_id": sub.get("user_id")}, {"_id": 0, "name": 1, "email": 1})
        sub["user"] = user
    
    return {"subscriptions": subscriptions, "total": total}

@router.put("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str, request: Request):
    """Cancel subscription"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "subscriptions")
    
    sub = await db.subscriptions.find_one({"subscription_id": subscription_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Update user plan to starter
    await db.users.update_one(
        {"user_id": sub["user_id"]},
        {"$set": {"role": "starter", "account_limit": 1, "ai_usage_limit": 10}}
    )
    
    await log_admin_action(admin, "cancel_subscription", "subscription", subscription_id, {"user_id": sub["user_id"]}, get_client_ip(request))
    
    return {"message": "Subscription cancelled"}

@router.put("/subscriptions/{subscription_id}/plan")
async def change_subscription_plan(subscription_id: str, new_plan: str, request: Request):
    """Change subscription plan"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "subscriptions")
    
    sub = await db.subscriptions.find_one({"subscription_id": subscription_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    plan = await db.plans.find_one({"plan_id": new_plan}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    old_plan = sub.get("plan_id")
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {"$set": {"plan_id": new_plan, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Update user limits
    await db.users.update_one(
        {"user_id": sub["user_id"]},
        {"$set": {
            "role": new_plan,
            "account_limit": plan.get("account_limit", 1),
            "ai_usage_limit": plan.get("ai_limit", 10)
        }}
    )
    
    await log_admin_action(admin, "change_subscription_plan", "subscription", subscription_id, {"old_plan": old_plan, "new_plan": new_plan}, get_client_ip(request))
    
    return {"message": f"Subscription plan changed to {new_plan}"}

# ==================== PLAN MANAGEMENT ====================

@router.get("/plans")
async def get_all_plans(request: Request):
    """Get all plans"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "plans")
    
    plans = await db.plans.find({}, {"_id": 0}).sort("price", 1).to_list(100)
    
    # Add subscriber count
    for plan in plans:
        plan["subscribers"] = await db.users.count_documents({"role": plan["plan_id"]})
    
    return {"plans": plans}

@router.post("/plans")
async def create_plan(
    name: str,
    price: float,
    billing_cycle: str,
    account_limit: int,
    ai_limit: int,
    team_limit: int = 0,
    white_label: bool = False,
    features: str = "",
    request: Request = None
):
    """Create new plan"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "plans")
    
    plan_id = name.lower().replace(" ", "_")
    
    existing = await db.plans.find_one({"plan_id": plan_id})
    if existing:
        raise HTTPException(status_code=400, detail="Plan already exists")
    
    features_list = [f.strip() for f in features.split(",") if f.strip()] if features else []
    
    plan_doc = {
        "plan_id": plan_id,
        "name": name,
        "price": price,
        "billing_cycle": billing_cycle,
        "account_limit": account_limit,
        "ai_limit": ai_limit,
        "team_limit": team_limit,
        "white_label": white_label,
        "features": features_list,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.plans.insert_one(plan_doc)
    
    await log_admin_action(admin, "create_plan", "plan", plan_id, {"name": name, "price": price}, get_client_ip(request))
    
    return {"plan_id": plan_id, "message": "Plan created successfully"}

@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: str,
    name: str = None,
    price: float = None,
    billing_cycle: str = None,
    account_limit: int = None,
    ai_limit: int = None,
    team_limit: int = None,
    white_label: bool = None,
    status: str = None,
    features: str = None,
    request: Request = None
):
    """Update plan"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "plans")
    
    plan = await db.plans.find_one({"plan_id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if price is not None:
        update_data["price"] = price
    if billing_cycle is not None:
        update_data["billing_cycle"] = billing_cycle
    if account_limit is not None:
        update_data["account_limit"] = account_limit
    if ai_limit is not None:
        update_data["ai_limit"] = ai_limit
    if team_limit is not None:
        update_data["team_limit"] = team_limit
    if white_label is not None:
        update_data["white_label"] = white_label
    if status is not None:
        update_data["status"] = status
    if features is not None:
        update_data["features"] = [f.strip() for f in features.split(",") if f.strip()]
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.plans.update_one({"plan_id": plan_id}, {"$set": update_data})
    
    await log_admin_action(admin, "update_plan", "plan", plan_id, update_data, get_client_ip(request))
    
    return {"message": "Plan updated successfully"}

@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, request: Request):
    """Delete/disable plan"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "plans")
    
    # Check if any users are on this plan
    users_on_plan = await db.users.count_documents({"role": plan_id})
    if users_on_plan > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete plan with {users_on_plan} active subscribers")
    
    await db.plans.update_one({"plan_id": plan_id}, {"$set": {"status": "disabled"}})
    
    await log_admin_action(admin, "disable_plan", "plan", plan_id, {}, get_client_ip(request))
    
    return {"message": "Plan disabled"}
