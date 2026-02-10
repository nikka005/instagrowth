from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json
import httpx
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from models import GrowthPlan, GrowthPlanRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_LONG

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/growth-plans", tags=["Growth Planner"])

INSTAGRAM_GRAPH_URL = "https://graph.instagram.com"

async def fetch_account_metrics(access_token: str):
    """Fetch real account metrics for growth planning"""
    try:
        async with httpx.AsyncClient() as client:
            # Get profile
            profile_resp = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me",
                params={
                    "fields": "id,username,followers_count,follows_count,media_count",
                    "access_token": access_token
                },
                timeout=10
            )
            
            # Get recent media
            media_resp = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me/media",
                params={
                    "fields": "id,media_type,like_count,comments_count,timestamp",
                    "limit": 20,
                    "access_token": access_token
                },
                timeout=10
            )
            
            profile = profile_resp.json() if profile_resp.status_code == 200 else {}
            media = media_resp.json().get("data", []) if media_resp.status_code == 200 else []
            
            # Calculate metrics
            total_likes = sum(m.get("like_count", 0) for m in media)
            total_comments = sum(m.get("comments_count", 0) for m in media)
            avg_engagement = (total_likes + total_comments) / len(media) if media else 0
            followers = profile.get("followers_count", 0)
            engagement_rate = (avg_engagement / followers * 100) if followers else 0
            
            # Analyze content types
            content_types = {}
            for m in media:
                t = m.get("media_type", "IMAGE")
                content_types[t] = content_types.get(t, 0) + 1
            
            return {
                "followers": followers,
                "following": profile.get("follows_count", 0),
                "media_count": profile.get("media_count", 0),
                "avg_likes": total_likes / len(media) if media else 0,
                "avg_comments": total_comments / len(media) if media else 0,
                "engagement_rate": round(engagement_rate, 2),
                "content_mix": content_types,
                "posts_analyzed": len(media)
            }
    except Exception as e:
        logger.warning(f"Could not fetch account metrics: {e}")
    return {}

@router.post("", response_model=GrowthPlan)
async def create_growth_plan(data: GrowthPlanRequest, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_ai_usage(user, db, feature="growth_plan")
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    niche = data.niche or account.get("niche", "general")
    
    # Fetch real metrics if available
    real_metrics = {}
    if account.get("access_token"):
        logger.info(f"Fetching real metrics for growth plan @{account['username']}")
        real_metrics = await fetch_account_metrics(account["access_token"])
    
    # Build data-driven prompt
    metrics_context = ""
    if real_metrics:
        metrics_context = f"""
REAL ACCOUNT METRICS:
- Current Followers: {real_metrics.get('followers', 0):,}
- Following: {real_metrics.get('following', 0):,}
- Total Posts: {real_metrics.get('media_count', 0)}
- Average Likes/Post: {real_metrics.get('avg_likes', 0):.0f}
- Average Comments/Post: {real_metrics.get('avg_comments', 0):.0f}
- Engagement Rate: {real_metrics.get('engagement_rate', 0)}%
- Content Mix: {real_metrics.get('content_mix', {})}

Create a plan that addresses these specific metrics and helps improve engagement."""
    
    system_message = f"""Create an actionable, data-driven daily growth plan based on REAL account data.
Return JSON with 'daily_tasks' array.
Each task must have: day (int), title (string), description (string), type (post/engage/analyze/learn), priority (high/medium/low)
Make tasks SPECIFIC to the account's current performance.
{metrics_context}"""
    
    prompt = f"""Create a personalized {data.duration}-day Instagram growth plan for @{account['username']}:
- Niche: {niche}
- Current Followers: {account.get('follower_count', real_metrics.get('followers', 'Unknown'))}
- Engagement Rate: {account.get('engagement_rate', real_metrics.get('engagement_rate', 'Unknown'))}%
{metrics_context}

Focus on realistic, achievable goals based on their current metrics."""
    
    try:
        ai_response = await generate_ai_content(prompt, system_message, timeout_seconds=AI_TIMEOUT_LONG)
        cleaned = ai_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        plan_data = json.loads(cleaned.strip())
        daily_tasks = plan_data.get("daily_tasks", [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Growth plan generation error: {e}")
        # Generate fallback with real data context
        daily_tasks = []
        for day in range(1, data.duration + 1):
            task_types = ["post", "engage", "analyze", "learn"]
            task_type = task_types[(day - 1) % 4]
            
            # Customize based on real metrics
            if real_metrics.get('engagement_rate', 0) < 2:
                priority = "high" if task_type == "engage" else "medium"
            else:
                priority = "high" if day <= 7 else "medium"
            
            daily_tasks.append({
                "day": day,
                "title": f"Day {day}: {task_type.capitalize()} Focus",
                "description": f"Focus on {task_type} activities to improve your {real_metrics.get('engagement_rate', 3)}% engagement",
                "type": task_type,
                "priority": priority
            })
    
    await increment_ai_usage(user.user_id, db, feature="growth_plan")
    
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    plan_doc = {
        "plan_id": plan_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "duration": data.duration,
        "daily_tasks": daily_tasks,
        "based_on_real_data": bool(real_metrics),
        "metrics_at_creation": real_metrics if real_metrics else None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.growth_plans.insert_one(plan_doc)
    return GrowthPlan(**plan_doc)

@router.get("", response_model=List[GrowthPlan])
async def get_growth_plans(account_id: Optional[str] = None, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    plans = await db.growth_plans.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [GrowthPlan(**p) for p in plans]

@router.get("/{plan_id}", response_model=GrowthPlan)
async def get_growth_plan(plan_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    plan = await db.growth_plans.find_one({"plan_id": plan_id, "user_id": user.user_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Growth plan not found")
    return GrowthPlan(**plan)

@router.get("/{plan_id}/pdf")
async def get_growth_plan_pdf(plan_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    plan = await db.growth_plans.find_one({"plan_id": plan_id, "user_id": user.user_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Growth plan not found")
    
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    team = None
    if user.team_id:
        team = await db.teams.find_one({"team_id": user.team_id}, {"_id": 0})
    
    brand_color = team.get("brand_color", "#6366F1") if team else "#6366F1"
    company_name = team.get("name", "InstaGrowth OS") if team else "InstaGrowth OS"
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFillColor(HexColor(brand_color))
    p.rect(0, height - 100, width, 100, fill=True)
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 55, f"{company_name} - Growth Plan")
    
    y = height - 140
    p.setFillColor(HexColor("#000000"))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"{plan['duration']}-Day Growth Plan")
    y -= 30
    
    p.setFont("Helvetica", 11)
    for task in plan.get('daily_tasks', [])[:15]:
        p.drawString(50, y, f"Day {task['day']}: {task['title'][:60]}")
        y -= 16
        if y < 50:
            p.showPage()
            y = height - 50
    
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#666666"))
    p.drawString(50, 30, f"Generated by {company_name} | {datetime.now().strftime('%Y-%m-%d')}")
    
    p.save()
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=growth_plan_{plan_id}.pdf"}
    )
