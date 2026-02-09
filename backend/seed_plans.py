"""
Seed default subscription plans for InstaGrowth OS
Run this script once to create the default plans
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid

async def seed_plans():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME', 'instagrowth_db')]
    
    # Check if plans already exist
    existing = await db.plans.count_documents({})
    if existing > 0:
        print(f"Plans already exist ({existing} plans). Skipping seed.")
        return
    
    default_plans = [
        {
            "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
            "name": "Starter",
            "description": "Perfect for individual creators getting started",
            "price": 19,
            "billing_cycle": "monthly",
            "features": [
                "1 Instagram Account",
                "10 AI Audits/month",
                "50 AI Credits/month",
                "Basic Content Generation",
                "Email Support"
            ],
            "limits": {
                "accounts": 1,
                "audits_per_month": 10,
                "ai_credits": 50
            },
            "is_popular": False,
            "is_active": True,
            "sort_order": 1,
            "stripe_price_id": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
            "name": "Pro",
            "description": "For growing creators and small agencies",
            "price": 49,
            "billing_cycle": "monthly",
            "features": [
                "5 Instagram Accounts",
                "50 AI Audits/month",
                "200 AI Credits/month",
                "Advanced Content Generation",
                "Growth Planner",
                "Priority Email Support"
            ],
            "limits": {
                "accounts": 5,
                "audits_per_month": 50,
                "ai_credits": 200
            },
            "is_popular": True,
            "is_active": True,
            "sort_order": 2,
            "stripe_price_id": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
            "name": "Agency",
            "description": "For agencies managing multiple clients",
            "price": 149,
            "billing_cycle": "monthly",
            "features": [
                "20 Instagram Accounts",
                "Unlimited AI Audits",
                "1000 AI Credits/month",
                "White-label Reports",
                "Team Collaboration",
                "API Access",
                "Priority Support"
            ],
            "limits": {
                "accounts": 20,
                "audits_per_month": -1,
                "ai_credits": 1000
            },
            "is_popular": False,
            "is_active": True,
            "sort_order": 3,
            "stripe_price_id": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
            "name": "Enterprise",
            "description": "Custom solutions for large organizations",
            "price": 299,
            "billing_cycle": "monthly",
            "features": [
                "Unlimited Instagram Accounts",
                "Unlimited AI Audits",
                "Unlimited AI Credits",
                "Full White-label Solution",
                "Custom Integrations",
                "Dedicated Account Manager",
                "24/7 Phone Support",
                "SLA Guarantee"
            ],
            "limits": {
                "accounts": -1,
                "audits_per_month": -1,
                "ai_credits": -1
            },
            "is_popular": False,
            "is_active": True,
            "sort_order": 4,
            "stripe_price_id": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    result = await db.plans.insert_many(default_plans)
    print(f"Successfully created {len(result.inserted_ids)} default plans!")
    
    # Also create a free trial plan
    free_plan = {
        "plan_id": f"plan_{uuid.uuid4().hex[:12]}",
        "name": "Free Trial",
        "description": "7-day free trial to explore all features",
        "price": 0,
        "billing_cycle": "trial",
        "trial_days": 7,
        "features": [
            "1 Instagram Account",
            "5 AI Audits",
            "20 AI Credits",
            "Basic Content Generation"
        ],
        "limits": {
            "accounts": 1,
            "audits_per_month": 5,
            "ai_credits": 20
        },
        "is_popular": False,
        "is_active": True,
        "sort_order": 0,
        "stripe_price_id": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.plans.insert_one(free_plan)
    print("Created Free Trial plan!")

if __name__ == "__main__":
    asyncio.run(seed_plans())
