from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from models import GrowthPlan, GrowthPlanRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_LONG

router = APIRouter(prefix="/growth-plans", tags=["Growth Planner"])

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
    
    system_message = """Create actionable daily growth plan. Return JSON with 'daily_tasks' array.
    Each task: day (int), title (string), description (string), type (post/engage/analyze/learn), priority (high/medium/low)."""
    
    prompt = f"Create {data.duration}-day Instagram growth plan for {niche} niche."
    
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
    except Exception:
        daily_tasks = []
        for day in range(1, data.duration + 1):
            task_type = ["post", "engage", "analyze", "learn"][day % 4]
            daily_tasks.append({
                "day": day, "title": f"Day {day}: {task_type.capitalize()} Focus",
                "description": f"Focus on {task_type} activities",
                "type": task_type, "priority": "high" if day <= 7 else "medium"
            })
    
    await increment_ai_usage(user.user_id, db)
    
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    plan_doc = {
        "plan_id": plan_id, "account_id": data.account_id, "user_id": user.user_id,
        "duration": data.duration, "daily_tasks": daily_tasks,
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
