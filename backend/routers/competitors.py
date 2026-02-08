from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List
import uuid

from models import CompetitorAnalysis, CompetitorAnalysisRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import analyze_competitor

router = APIRouter(prefix="/competitors", tags=["Competitor Analysis"])

@router.post("/analyze", response_model=CompetitorAnalysis)
async def create_competitor_analysis(data: CompetitorAnalysisRequest, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_ai_usage(user, db, feature="competitor_analysis")
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    competitors = []
    for username in data.competitor_usernames[:5]:
        analysis = await analyze_competitor(username, account["niche"])
        competitors.append({"username": username, **analysis})
    
    insights = [
        f"Top competitor has {max(c.get('estimated_followers', 0) for c in competitors):,} followers",
        f"Average engagement rate: {sum(c.get('estimated_engagement_rate', 0) for c in competitors) / len(competitors):.1f}%",
        "Most competitors focus on Reels content"
    ]
    
    opportunities = [
        "Focus on underserved content types",
        "Post during competitor off-hours",
        "Create content addressing competitor weaknesses"
    ]
    
    await increment_ai_usage(user.user_id, db, feature="competitor_analysis")
    
    analysis_id = f"analysis_{uuid.uuid4().hex[:12]}"
    analysis_doc = {
        "analysis_id": analysis_id, "account_id": data.account_id, "user_id": user.user_id,
        "competitors": competitors, "insights": insights, "opportunities": opportunities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.competitor_analyses.insert_one(analysis_doc)
    return CompetitorAnalysis(**analysis_doc)

@router.get("")
async def get_competitor_analyses(account_id: str = None, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    analyses = await db.competitor_analyses.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return analyses

@router.get("/{analysis_id}")
async def get_competitor_analysis(analysis_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    analysis = await db.competitor_analyses.find_one(
        {"analysis_id": analysis_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
