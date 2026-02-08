from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from database import get_database
from routers.admin_panel_auth import verify_admin_token, check_permission, log_admin_action, get_client_ip

router = APIRouter(prefix="/admin-panel", tags=["Admin Panel - Dashboard & Analytics"])

# ==================== DASHBOARD STATS ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request):
    """Get admin dashboard overview stats"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Basic counts
    total_users = await db.users.count_documents({})
    active_subscriptions = await db.subscriptions.count_documents({"status": "active"})
    total_accounts = await db.instagram_accounts.count_documents({})
    total_audits = await db.audits.count_documents({})
    total_content = await db.content_items.count_documents({})
    
    # Today's stats
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    new_users_today = await db.users.count_documents({"created_at": {"$gte": today_start}})
    audits_today = await db.audits.count_documents({"created_at": {"$gte": today_start}})
    
    # AI usage
    ai_requests_today = await db.users.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$ai_usage_current"}}}
    ]).to_list(1)
    total_ai_requests = ai_requests_today[0]["total"] if ai_requests_today else 0
    
    # Plan distribution
    plan_distribution = {}
    for plan in ["starter", "pro", "agency", "enterprise"]:
        plan_distribution[plan] = await db.users.count_documents({"role": plan})
    
    return {
        "total_users": total_users,
        "active_subscriptions": active_subscriptions,
        "total_accounts": total_accounts,
        "total_audits": total_audits,
        "total_content": total_content,
        "new_users_today": new_users_today,
        "audits_today": audits_today,
        "ai_requests_today": total_ai_requests,
        "plan_distribution": plan_distribution
    }

@router.get("/dashboard/charts/revenue")
async def get_revenue_chart(days: int = 30, request: Request = None):
    """Get revenue data for chart"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "revenue")
    
    # Get transactions for last N days
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    transactions = await db.payment_transactions.find(
        {"created_at": {"$gte": start_date}, "status": "completed"},
        {"_id": 0, "amount": 1, "created_at": 1}
    ).to_list(10000)
    
    # Group by date
    revenue_by_date = {}
    for tx in transactions:
        date = tx["created_at"][:10]
        revenue_by_date[date] = revenue_by_date.get(date, 0) + tx.get("amount", 0)
    
    # Fill in missing dates
    chart_data = []
    current = datetime.now(timezone.utc) - timedelta(days=days)
    for _ in range(days):
        date_str = current.strftime("%Y-%m-%d")
        chart_data.append({
            "date": date_str,
            "revenue": revenue_by_date.get(date_str, 0)
        })
        current += timedelta(days=1)
    
    return {"chart_data": chart_data}

@router.get("/dashboard/charts/users")
async def get_users_chart(days: int = 30, request: Request = None):
    """Get new users data for chart"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    users = await db.users.find(
        {"created_at": {"$gte": start_date}},
        {"_id": 0, "created_at": 1}
    ).to_list(10000)
    
    # Group by date
    users_by_date = {}
    for user in users:
        date = user["created_at"][:10]
        users_by_date[date] = users_by_date.get(date, 0) + 1
    
    chart_data = []
    current = datetime.now(timezone.utc) - timedelta(days=days)
    for _ in range(days):
        date_str = current.strftime("%Y-%m-%d")
        chart_data.append({
            "date": date_str,
            "users": users_by_date.get(date_str, 0)
        })
        current += timedelta(days=1)
    
    return {"chart_data": chart_data}

@router.get("/dashboard/charts/ai-usage")
async def get_ai_usage_chart(days: int = 30, request: Request = None):
    """Get AI usage trend for chart"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Get AI usage logs
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    content = await db.content_items.find(
        {"created_at": {"$gte": start_date}},
        {"_id": 0, "created_at": 1}
    ).to_list(10000)
    
    audits = await db.audits.find(
        {"created_at": {"$gte": start_date}},
        {"_id": 0, "created_at": 1}
    ).to_list(10000)
    
    # Combine and group by date
    usage_by_date = {}
    for item in content + audits:
        date = item["created_at"][:10]
        usage_by_date[date] = usage_by_date.get(date, 0) + 1
    
    chart_data = []
    current = datetime.now(timezone.utc) - timedelta(days=days)
    for _ in range(days):
        date_str = current.strftime("%Y-%m-%d")
        chart_data.append({
            "date": date_str,
            "requests": usage_by_date.get(date_str, 0)
        })
        current += timedelta(days=1)
    
    return {"chart_data": chart_data}

# ==================== REVENUE ANALYTICS ====================

@router.get("/revenue/stats")
async def get_revenue_stats(request: Request):
    """Get revenue statistics"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "revenue")
    
    # Calculate MRR
    active_subs = await db.subscriptions.find({"status": "active"}, {"_id": 0}).to_list(10000)
    
    PLAN_PRICES = {
        "starter": 19,
        "pro": 49,
        "agency": 149,
        "enterprise": 299
    }
    
    mrr = sum(PLAN_PRICES.get(sub.get("plan_id", "starter"), 0) for sub in active_subs)
    arr = mrr * 12
    
    # Total users for churn calculation
    total_users = await db.users.count_documents({})
    cancelled_last_month = await db.subscriptions.count_documents({
        "status": "cancelled",
        "cancelled_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}
    })
    churn_rate = (cancelled_last_month / total_users * 100) if total_users > 0 else 0
    
    # ARPU
    arpu = mrr / total_users if total_users > 0 else 0
    
    # Revenue by plan
    revenue_by_plan = {}
    for plan, price in PLAN_PRICES.items():
        count = await db.users.count_documents({"role": plan})
        revenue_by_plan[plan] = count * price
    
    # Total revenue
    total_transactions = await db.payment_transactions.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_revenue = total_transactions[0]["total"] if total_transactions else 0
    
    return {
        "mrr": mrr,
        "arr": arr,
        "churn_rate": round(churn_rate, 2),
        "arpu": round(arpu, 2),
        "total_revenue": total_revenue,
        "revenue_by_plan": revenue_by_plan,
        "active_subscriptions": len(active_subs)
    }

# ==================== AI USAGE ANALYTICS ====================

@router.get("/ai-usage/stats")
async def get_ai_usage_stats(request: Request):
    """Get AI usage statistics"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Total usage
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1, "email": 1, "ai_usage_current": 1, "ai_usage_limit": 1, "role": 1}).to_list(10000)
    
    total_usage = sum(u.get("ai_usage_current", 0) for u in users)
    
    # Today's usage (from content and audits)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    content_today = await db.content_items.count_documents({"created_at": {"$gte": today_start}})
    audits_today = await db.audits.count_documents({"created_at": {"$gte": today_start}})
    growth_plans_today = await db.growth_plans.count_documents({"created_at": {"$gte": today_start}})
    
    requests_today = content_today + audits_today + growth_plans_today
    
    # This month
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    content_month = await db.content_items.count_documents({"created_at": {"$gte": month_start}})
    audits_month = await db.audits.count_documents({"created_at": {"$gte": month_start}})
    growth_plans_month = await db.growth_plans.count_documents({"created_at": {"$gte": month_start}})
    
    requests_month = content_month + audits_month + growth_plans_month
    
    # Estimated cost (assuming $0.01 per request)
    COST_PER_REQUEST = 0.01
    estimated_cost = requests_month * COST_PER_REQUEST
    
    # Usage by feature
    usage_by_feature = {
        "content_generation": content_month,
        "audits": audits_month,
        "growth_plans": growth_plans_month
    }
    
    # Top users
    top_users = sorted(users, key=lambda x: x.get("ai_usage_current", 0), reverse=True)[:10]
    
    return {
        "total_requests_today": requests_today,
        "total_requests_month": requests_month,
        "estimated_cost_month": round(estimated_cost, 2),
        "usage_by_feature": usage_by_feature,
        "top_users": [
            {"user_id": u["user_id"], "name": u.get("name", ""), "email": u.get("email", ""), "usage": u.get("ai_usage_current", 0), "limit": u.get("ai_usage_limit", 0), "plan": u.get("role", "starter")}
            for u in top_users
        ]
    }

# ==================== INSTAGRAM ACCOUNTS ====================

@router.get("/instagram-accounts")
async def get_all_instagram_accounts(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    search: str = None,
    request: Request = None
):
    """Get all Instagram accounts"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "accounts")
    
    query = {}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"niche": {"$regex": search, "$options": "i"}}
        ]
    
    accounts = await db.instagram_accounts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.instagram_accounts.count_documents(query)
    
    # Enrich with owner info
    for acc in accounts:
        user = await db.users.find_one({"user_id": acc.get("user_id")}, {"_id": 0, "name": 1, "email": 1})
        acc["owner"] = user
    
    return {"accounts": accounts, "total": total}

@router.post("/instagram-accounts/{account_id}/disconnect")
async def disconnect_account(account_id: str, request: Request):
    """Disconnect Instagram account"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "accounts")
    
    await db.instagram_accounts.update_one(
        {"account_id": account_id},
        {"$set": {"status": "disconnected", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, "disconnect_account", "instagram_account", account_id, {}, get_client_ip(request))
    
    return {"message": "Account disconnected"}

@router.post("/instagram-accounts/{account_id}/flag")
async def flag_account(account_id: str, reason: str, request: Request):
    """Flag account for suspicious activity"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "accounts")
    
    await db.instagram_accounts.update_one(
        {"account_id": account_id},
        {"$set": {"flagged": True, "flag_reason": reason, "flagged_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, "flag_account", "instagram_account", account_id, {"reason": reason}, get_client_ip(request))
    
    return {"message": "Account flagged"}

# ==================== LOGS ====================

@router.get("/logs")
async def get_admin_logs(
    skip: int = 0,
    limit: int = 100,
    action: str = None,
    admin_id: str = None,
    target_type: str = None,
    start_date: str = None,
    end_date: str = None,
    request: Request = None
):
    """Get admin activity logs"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "logs")
    
    query = {}
    if action:
        query["action"] = action
    if admin_id:
        query["admin_id"] = admin_id
    if target_type:
        query["target_type"] = target_type
    if start_date:
        query["created_at"] = {"$gte": start_date}
    if end_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = end_date
        else:
            query["created_at"] = {"$lte": end_date}
    
    logs = await db.admin_logs.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.admin_logs.count_documents(query)
    
    return {"logs": logs, "total": total}

# ==================== SYSTEM SETTINGS ====================

@router.get("/settings")
async def get_system_settings(request: Request):
    """Get system settings"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    settings = await db.system_settings.find_one({"setting_id": "global"}, {"_id": 0})
    
    if not settings:
        settings = {
            "setting_id": "global",
            "platform_name": "InstaGrowth OS",
            "support_email": "support@instagrowth.com",
            "default_ai_model": "gpt-5.2"
        }
    
    # Mask sensitive keys
    if settings.get("openai_api_key"):
        settings["openai_api_key"] = "***" + settings["openai_api_key"][-4:]
    if settings.get("stripe_api_key"):
        settings["stripe_api_key"] = "***" + settings["stripe_api_key"][-4:]
    if settings.get("resend_api_key"):
        settings["resend_api_key"] = "***" + settings["resend_api_key"][-4:]
    
    return settings

@router.put("/settings")
async def update_system_settings(
    platform_name: str = None,
    support_email: str = None,
    default_ai_model: str = None,
    openai_api_key: str = None,
    stripe_api_key: str = None,
    resend_api_key: str = None,
    meta_api_key: str = None,
    request: Request = None
):
    """Update system settings"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    update_data = {}
    if platform_name:
        update_data["platform_name"] = platform_name
    if support_email:
        update_data["support_email"] = support_email
    if default_ai_model:
        update_data["default_ai_model"] = default_ai_model
    if openai_api_key and not openai_api_key.startswith("***"):
        update_data["openai_api_key"] = openai_api_key
    if stripe_api_key and not stripe_api_key.startswith("***"):
        update_data["stripe_api_key"] = stripe_api_key
    if resend_api_key and not resend_api_key.startswith("***"):
        update_data["resend_api_key"] = resend_api_key
    if meta_api_key and not meta_api_key.startswith("***"):
        update_data["meta_api_key"] = meta_api_key
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.system_settings.update_one(
            {"setting_id": "global"},
            {"$set": update_data},
            upsert=True
        )
    
    await log_admin_action(admin, "update_settings", "system", None, {"fields_updated": list(update_data.keys())}, get_client_ip(request))
    
    return {"message": "Settings updated"}

# ==================== TEAM MANAGEMENT (INTERNAL ADMINS) ====================

@router.get("/team")
async def get_admin_team(request: Request):
    """Get all admin team members"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    admins = await db.admins.find({}, {"_id": 0, "password_hash": 0, "totp_secret": 0, "backup_codes": 0}).to_list(100)
    
    return {"admins": admins}

@router.put("/team/{admin_id}/role")
async def update_admin_role(admin_id: str, role: str, request: Request):
    """Update admin role"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    if admin["admin_id"] == admin_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    
    if role not in ["super_admin", "support", "finance"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    await db.admins.update_one(
        {"admin_id": admin_id},
        {"$set": {"role": role, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, "update_admin_role", "admin", admin_id, {"new_role": role}, get_client_ip(request))
    
    return {"message": "Admin role updated"}

@router.put("/team/{admin_id}/status")
async def update_admin_status(admin_id: str, status: str, request: Request):
    """Enable/disable admin"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    if admin["admin_id"] == admin_id:
        raise HTTPException(status_code=400, detail="Cannot disable yourself")
    
    if status not in ["active", "disabled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    await db.admins.update_one(
        {"admin_id": admin_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_admin_action(admin, f"admin_{status}", "admin", admin_id, {}, get_client_ip(request))
    
    return {"message": f"Admin {status}"}
