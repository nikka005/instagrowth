from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from models import InstagramAccount, InstagramAccountCreate, InstagramAccountUpdate
from database import get_database
from dependencies import get_current_user, get_user_with_team_access, check_account_limit, check_ai_usage, increment_ai_usage
from services import estimate_instagram_metrics, generate_posting_recommendations

router = APIRouter(prefix="/accounts", tags=["Instagram Accounts"])

@router.post("", response_model=InstagramAccount)
async def create_account(data: InstagramAccountCreate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_account_limit(user, db)
    
    metrics = await estimate_instagram_metrics(data.username, data.niche)
    
    account_id = f"acc_{uuid.uuid4().hex[:12]}"
    account_doc = {
        "account_id": account_id,
        "user_id": user.user_id,
        "team_id": user.team_id,
        "username": data.username,
        "niche": data.niche,
        "notes": data.notes,
        "client_name": data.client_name,
        "client_email": data.client_email,
        "follower_count": metrics.get("estimated_followers"),
        "engagement_rate": metrics.get("estimated_engagement_rate"),
        "estimated_reach": metrics.get("estimated_reach"),
        "posting_frequency": metrics.get("posting_frequency"),
        "best_posting_time": metrics.get("best_posting_time"),
        "last_audit_date": None,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.instagram_accounts.insert_one(account_doc)
    return InstagramAccount(**account_doc)

@router.get("", response_model=List[InstagramAccount])
async def get_accounts(request: Request):
    db = get_database()
    user, team_ids = await get_user_with_team_access(request, db)
    
    query = {"$or": [{"user_id": user.user_id}]}
    if team_ids:
        query["$or"].append({"team_id": {"$in": team_ids}})
    
    accounts = await db.instagram_accounts.find(query, {"_id": 0}).to_list(100)
    return [InstagramAccount(**acc) for acc in accounts]

@router.get("/{account_id}", response_model=InstagramAccount)
async def get_account(account_id: str, request: Request):
    db = get_database()
    user, team_ids = await get_user_with_team_access(request, db)
    
    query = {"account_id": account_id, "$or": [{"user_id": user.user_id}]}
    if team_ids:
        query["$or"].append({"team_id": {"$in": team_ids}})
    
    account = await db.instagram_accounts.find_one(query, {"_id": 0})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return InstagramAccount(**account)

@router.put("/{account_id}", response_model=InstagramAccount)
async def update_account(account_id: str, data: InstagramAccountUpdate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.instagram_accounts.update_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = await db.instagram_accounts.find_one({"account_id": account_id}, {"_id": 0})
    return InstagramAccount(**account)

@router.delete("/{account_id}")
async def delete_account(account_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.instagram_accounts.delete_one({"account_id": account_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}

@router.post("/{account_id}/refresh-metrics")
async def refresh_account_metrics(account_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    await check_ai_usage(user, db, feature="audit")
    metrics = await estimate_instagram_metrics(account["username"], account["niche"])
    
    await db.instagram_accounts.update_one(
        {"account_id": account_id},
        {"$set": {
            "follower_count": metrics.get("estimated_followers"),
            "engagement_rate": metrics.get("estimated_engagement_rate"),
            "estimated_reach": metrics.get("estimated_reach"),
            "posting_frequency": metrics.get("posting_frequency"),
            "best_posting_time": metrics.get("best_posting_time")
        }}
    )
    await increment_ai_usage(user.user_id, db, feature="audit")
    return metrics

@router.get("/{account_id}/posting-recommendations")
async def get_posting_recommendations(account_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    await check_ai_usage(user, db, feature="posting_recommendations")
    
    current_metrics = {
        "estimated_followers": account.get("follower_count"),
        "estimated_engagement_rate": account.get("engagement_rate")
    }
    recommendations = await generate_posting_recommendations(
        account["username"], account["niche"], current_metrics
    )
    await increment_ai_usage(user.user_id, db, feature="posting_recommendations")
    return recommendations
