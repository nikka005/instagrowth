"""
InstaGrowth OS - Main Server Application
Version: 2.0.0

Modular FastAPI application with separate routers for each feature domain.
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from io import StringIO
import csv
from datetime import datetime, timezone

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routers
from routers import (
    auth, accounts, audits, content, growth, 
    teams, dm_templates, competitors, ab_testing,
    notifications, billing, admin, admin_auth, websocket
)
from database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(
    title="InstaGrowth OS API",
    description="AI-powered Instagram Growth & Management Platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(audits.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(growth.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(dm_templates.router, prefix="/api")
app.include_router(competitors.router, prefix="/api")
app.include_router(ab_testing.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(admin_auth.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")

# Root endpoint
@app.get("/api/")
async def root():
    return {
        "message": "InstaGrowth OS API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "healthy"
    }

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Plans endpoint (for billing page)
@app.get("/api/plans")
async def get_plans():
    return [
        {"id": "starter", "name": "Starter", "price": 19, "accounts": 1, "ai_usage": 10, "team": False},
        {"id": "pro", "name": "Pro", "price": 49, "accounts": 5, "ai_usage": 100, "team": False},
        {"id": "agency", "name": "Agency", "price": 149, "accounts": 25, "ai_usage": 500, "team": True},
        {"id": "enterprise", "name": "Enterprise", "price": 299, "accounts": 100, "ai_usage": 2000, "team": True}
    ]

# Dashboard stats endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(request: Request):
    from dependencies import get_current_user
    db = get_database()
    user = await get_current_user(request, db)
    
    accounts = await db.instagram_accounts.count_documents({"user_id": user.user_id})
    audits = await db.audits.count_documents({"user_id": user.user_id})
    content_items = await db.content_items.count_documents({"user_id": user.user_id})
    growth_plans = await db.growth_plans.count_documents({"user_id": user.user_id})
    
    recent_audits = await db.audits.find(
        {"user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "accounts_count": accounts,
        "account_limit": user.account_limit,
        "audits_count": audits,
        "content_items_count": content_items,
        "growth_plans_count": growth_plans,
        "ai_usage_current": user.ai_usage_current,
        "ai_usage_limit": user.ai_usage_limit,
        "recent_audits": recent_audits
    }

# CSV Export endpoint
@app.get("/api/export/csv")
async def export_data_csv(data_type: str, request: Request):
    from dependencies import get_current_user
    db = get_database()
    user = await get_current_user(request, db)
    
    if data_type == "accounts":
        data = await db.instagram_accounts.find({"user_id": user.user_id}, {"_id": 0}).to_list(1000)
        fields = ["username", "niche", "follower_count", "engagement_rate", "status", "created_at"]
    elif data_type == "audits":
        data = await db.audits.find({"user_id": user.user_id}, {"_id": 0}).to_list(1000)
        fields = ["username", "engagement_score", "shadowban_risk", "content_consistency", "created_at"]
    elif data_type == "content":
        data = await db.content_items.find({"user_id": user.user_id}, {"_id": 0}).to_list(1000)
        fields = ["content_type", "content", "is_favorite", "created_at"]
    else:
        return {"error": "Invalid data type. Use: accounts, audits, or content"}
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for item in data:
        if "content" in item and isinstance(item["content"], list):
            item["content"] = "; ".join(str(c) for c in item["content"])
        writer.writerow(item)
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={data_type}_export.csv"}
    )

# One-time products
ONE_TIME_PRODUCTS = [
    {"product_id": "recovery_report", "name": "Account Recovery Report", "description": "In-depth analysis of shadowbanned account", "price": 49.99, "type": "recovery_report"},
    {"product_id": "content_pack_30", "name": "30-Day Content Pack", "description": "30 days of ready-to-post content", "price": 29.99, "type": "content_pack"},
    {"product_id": "competitor_deep_dive", "name": "Competitor Deep Dive", "description": "Detailed analysis of 5 competitors", "price": 39.99, "type": "competitor_analysis"}
]

@app.get("/api/products")
async def get_products():
    return ONE_TIME_PRODUCTS

@app.post("/api/products/{product_id}/purchase")
async def purchase_product(product_id: str, request: Request):
    from dependencies import get_current_user
    import uuid
    db = get_database()
    user = await get_current_user(request, db)
    
    product = next((p for p in ONE_TIME_PRODUCTS if p["product_id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    
    purchase_id = f"purchase_{uuid.uuid4().hex[:12]}"
    purchase_doc = {
        "purchase_id": purchase_id,
        "user_id": user.user_id,
        "product_id": product_id,
        "amount": product["price"],
        "status": "pending",
        "data": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.one_time_purchases.insert_one(purchase_doc)
    
    return {
        "purchase_id": purchase_id,
        "product": product,
        "message": "Purchase initiated. Complete payment to access.",
        "mock": True
    }

# Extra accounts upsell
@app.post("/api/upsell/extra-accounts")
async def purchase_extra_accounts(count: int, request: Request):
    from dependencies import get_current_user
    db = get_database()
    user = await get_current_user(request, db)
    
    price_per_account = 5
    total_price = count * price_per_account
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$inc": {"extra_accounts": count}}
    )
    
    return {
        "message": f"Added {count} extra account slots",
        "total_price": total_price,
        "new_total": user.account_limit + user.extra_accounts + count,
        "mock": True
    }

# Stripe webhook (placeholder)
@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    logger.info("Received Stripe webhook")
    return {"received": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
