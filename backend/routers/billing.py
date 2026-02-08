from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import os

from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing"])

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

PLANS = {
    "starter": {"name": "Starter", "price": 19, "accounts": 1, "ai_usage": 10, "team": False},
    "pro": {"name": "Pro", "price": 49, "accounts": 5, "ai_usage": 100, "team": False},
    "agency": {"name": "Agency", "price": 149, "accounts": 25, "ai_usage": 500, "team": True},
    "enterprise": {"name": "Enterprise", "price": 299, "accounts": 100, "ai_usage": 2000, "team": True}
}

@router.get("/plans")
async def get_plans():
    return [{"id": k, **v} for k, v in PLANS.items()]

@router.post("/create-checkout-session")
async def create_checkout_session(plan_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PLANS[plan_id]
    
    if not STRIPE_API_KEY or STRIPE_API_KEY == "sk_test_emergent":
        return {
            "url": f"https://growth-saas-app.preview.emergentagent.com/billing?mock=true&plan={plan_id}",
            "mock": True,
            "message": "Stripe not configured. This is a mock checkout."
        }
    
    try:
        from emergentintegrations.payments.stripe import create_checkout
        
        origin = request.headers.get("origin", "https://growth-saas-app.preview.emergentagent.com")
        
        checkout_result = await create_checkout(
            api_key=STRIPE_API_KEY,
            product_name=f"InstaGrowth OS - {plan['name']} Plan",
            unit_amount=plan["price"] * 100,
            currency="usd",
            mode="subscription",
            success_url=f"{origin}/billing?success=true&plan={plan_id}",
            cancel_url=f"{origin}/billing?canceled=true"
        )
        return {"url": checkout_result.get("url"), "session_id": checkout_result.get("session_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@router.get("/subscription")
async def get_subscription(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    subscription = await db.subscriptions.find_one(
        {"user_id": user.user_id, "status": "active"}, {"_id": 0}
    )
    
    return {
        "plan": user.role,
        "account_limit": user.account_limit,
        "ai_usage_limit": user.ai_usage_limit,
        "ai_usage_current": user.ai_usage_current,
        "subscription": subscription
    }

@router.post("/upgrade")
async def upgrade_plan(plan_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PLANS[plan_id]
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {
            "role": plan_id,
            "account_limit": plan["accounts"],
            "ai_usage_limit": plan["ai_usage"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": f"Upgraded to {plan['name']} plan", "plan": plan}
