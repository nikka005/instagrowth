"""
AI Credit System - Track and manage user AI credits
"""
from datetime import datetime, timezone, timedelta
from database import get_database

# Credit costs per feature
CREDIT_COSTS = {
    "audit": 10,
    "caption": 1,
    "hashtags": 1,
    "content_ideas": 2,
    "hooks": 1,
    "growth_plan": 15,
    "competitor_analysis": 5,
    "dm_reply": 1,
    "posting_recommendations": 3,
    "ab_test": 2
}

# Plan credit allocations (monthly)
PLAN_CREDITS = {
    "free": 5,
    "starter": 10,
    "pro": 100,
    "agency": 500,
    "enterprise": 2000
}

async def get_user_credits(user_id: str) -> dict:
    """Get user's credit information"""
    db = get_database()
    
    credits = await db.ai_credits.find_one({"user_id": user_id}, {"_id": 0})
    
    if not credits:
        # Get user's plan to determine allocation
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "plan": 1})
        plan = user.get("plan", "starter") if user else "starter"
        total = PLAN_CREDITS.get(plan, 10)
        
        # Create initial credits
        credits = {
            "user_id": user_id,
            "total_credits": total,
            "used_credits": 0,
            "remaining_credits": total,
            "reset_date": get_next_reset_date().isoformat(),
            "extra_credits": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.ai_credits.insert_one(credits)
        credits.pop("_id", None)
    
    return credits

def get_next_reset_date() -> datetime:
    """Get the next monthly reset date (1st of next month)"""
    now = datetime.now(timezone.utc)
    if now.month == 12:
        return datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    return datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

async def check_and_reset_credits(user_id: str) -> dict:
    """Check if credits need reset and reset if necessary"""
    db = get_database()
    credits = await get_user_credits(user_id)
    
    reset_date = datetime.fromisoformat(credits["reset_date"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    
    if now >= reset_date:
        # Get user's plan
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "plan": 1})
        plan = user.get("plan", "starter") if user else "starter"
        total = PLAN_CREDITS.get(plan, 10)
        
        # Reset credits
        await db.ai_credits.update_one(
            {"user_id": user_id},
            {"$set": {
                "total_credits": total,
                "used_credits": 0,
                "remaining_credits": total + credits.get("extra_credits", 0),
                "reset_date": get_next_reset_date().isoformat(),
                "last_reset": now.isoformat()
            }}
        )
        credits = await get_user_credits(user_id)
    
    return credits

async def use_credits(user_id: str, feature: str, amount: int = None) -> tuple[bool, dict]:
    """
    Use credits for a feature. Returns (success, credits_info)
    """
    db = get_database()
    
    # Check and reset if needed
    credits = await check_and_reset_credits(user_id)
    
    # Get cost
    cost = amount if amount else CREDIT_COSTS.get(feature, 1)
    
    # Check if enough credits
    if credits["remaining_credits"] < cost:
        return False, {
            "error": "Insufficient credits",
            "required": cost,
            "remaining": credits["remaining_credits"],
            "feature": feature
        }
    
    # Deduct credits
    await db.ai_credits.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "used_credits": cost,
                "remaining_credits": -cost
            },
            "$push": {
                "usage_history": {
                    "feature": feature,
                    "cost": cost,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    
    # Get updated credits
    updated_credits = await get_user_credits(user_id)
    
    # Check if low credits alert needed (below 20%)
    if updated_credits["total_credits"] > 0:
        percentage = (updated_credits["remaining_credits"] / updated_credits["total_credits"]) * 100
        if percentage < 20 and updated_credits["remaining_credits"] > 0:
            try:
                from routers.email_automation import trigger_low_credits_email
                reset_date = updated_credits.get("reset_date", "1st of next month")
                await trigger_low_credits_email(
                    user_id,
                    updated_credits["remaining_credits"],
                    updated_credits["total_credits"],
                    reset_date[:10] if isinstance(reset_date, str) else str(reset_date)
                )
            except Exception:
                pass  # Don't fail if email fails
    
    return True, updated_credits

async def add_extra_credits(user_id: str, amount: int, reason: str = "purchase") -> dict:
    """Add extra credits to user account"""
    db = get_database()
    
    await db.ai_credits.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "extra_credits": amount,
                "remaining_credits": amount
            },
            "$push": {
                "credit_additions": {
                    "amount": amount,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return await get_user_credits(user_id)

async def update_plan_credits(user_id: str, new_plan: str):
    """Update credits when user changes plan"""
    db = get_database()
    
    new_total = PLAN_CREDITS.get(new_plan, 10)
    credits = await get_user_credits(user_id)
    
    # Calculate new remaining (keep used, update total)
    new_remaining = max(0, new_total - credits["used_credits"]) + credits.get("extra_credits", 0)
    
    await db.ai_credits.update_one(
        {"user_id": user_id},
        {"$set": {
            "total_credits": new_total,
            "remaining_credits": new_remaining,
            "plan_updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await get_user_credits(user_id)

def get_credit_costs() -> dict:
    """Get all credit costs for frontend display"""
    return CREDIT_COSTS

def get_plan_credits() -> dict:
    """Get plan credit allocations"""
    return PLAN_CREDITS
