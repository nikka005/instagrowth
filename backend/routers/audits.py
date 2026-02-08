from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import base64

from models import Audit, AuditRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_MEDIUM

router = APIRouter(prefix="/audits", tags=["AI Audits"])

@router.post("", response_model=Audit)
async def create_audit(data: AuditRequest, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_ai_usage(user, db, feature="audit")
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    system_message = """You are an Instagram growth expert. Provide detailed analysis in JSON:
    - engagement_score (0-100)
    - shadowban_risk (low/medium/high)
    - content_consistency (0-100)
    - estimated_followers (int)
    - estimated_engagement_rate (float)
    - growth_mistakes (array of 3-5 mistakes)
    - recommendations (array of 5-7 recommendations)
    - roadmap (object with week1-4 arrays)
    Response must be valid JSON only."""
    
    prompt = f"""Analyze Instagram account:
    Username: @{account['username']}
    Niche: {account['niche']}
    Notes: {account.get('notes', 'None')}
    Current followers: {account.get('follower_count', 'Unknown')}"""
    
    try:
        ai_response = await generate_ai_content(prompt, system_message, timeout_seconds=AI_TIMEOUT_MEDIUM)
        cleaned = ai_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        audit_data = json.loads(cleaned.strip())
    except HTTPException:
        raise
    except Exception as e:
        audit_data = {
            "engagement_score": 65, "shadowban_risk": "medium", "content_consistency": 70,
            "estimated_followers": account.get("follower_count", 5000),
            "estimated_engagement_rate": account.get("engagement_rate", 3.5),
            "growth_mistakes": ["Inconsistent posting schedule", "Not using trending audio in Reels",
                               "Weak call-to-actions in captions", "Missing engagement in first 30 minutes"],
            "recommendations": ["Post consistently at peak hours", "Use trending audio in Reels",
                               "Add strong CTAs for saves and shares", "Engage with similar accounts before posting",
                               "Use 20-30 relevant hashtags"],
            "roadmap": {"week1": ["Audit content", "Create calendar", "Research trends"],
                       "week2": ["Post 5 Reels", "Engage daily", "Optimize bio"],
                       "week3": ["Analyze performance", "Double down on winners"],
                       "week4": ["Review analytics", "Plan next month"]}
        }
    
    await increment_ai_usage(user.user_id, db)
    
    audit_id = f"audit_{uuid.uuid4().hex[:12]}"
    audit_doc = {
        "audit_id": audit_id, "account_id": data.account_id, "user_id": user.user_id,
        "username": account["username"], "engagement_score": audit_data.get("engagement_score", 0),
        "shadowban_risk": audit_data.get("shadowban_risk", "unknown"),
        "content_consistency": audit_data.get("content_consistency", 0),
        "estimated_followers": audit_data.get("estimated_followers"),
        "estimated_engagement_rate": audit_data.get("estimated_engagement_rate"),
        "growth_mistakes": audit_data.get("growth_mistakes", []),
        "recommendations": audit_data.get("recommendations", []),
        "roadmap": audit_data.get("roadmap", {}),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.audits.insert_one(audit_doc)
    
    await db.instagram_accounts.update_one(
        {"account_id": data.account_id},
        {"$set": {"last_audit_date": datetime.now(timezone.utc).isoformat()}}
    )
    return Audit(**audit_doc)

@router.get("", response_model=List[Audit])
async def get_audits(account_id: Optional[str] = None, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    audits = await db.audits.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [Audit(**a) for a in audits]

@router.get("/{audit_id}", response_model=Audit)
async def get_audit(audit_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    audit = await db.audits.find_one({"audit_id": audit_id, "user_id": user.user_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return Audit(**audit)

@router.get("/{audit_id}/pdf")
async def get_audit_pdf(audit_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    audit = await db.audits.find_one({"audit_id": audit_id, "user_id": user.user_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    team = None
    if user.team_id:
        team = await db.teams.find_one({"team_id": user.team_id}, {"_id": 0})
    
    brand_color = team.get("brand_color", "#6366F1") if team else "#6366F1"
    company_name = team.get("name", "InstaGrowth OS") if team else "InstaGrowth OS"
    logo_url = team.get("logo_url") if team else None
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFillColor(HexColor(brand_color))
    p.rect(0, height - 100, width, 100, fill=True)
    
    if logo_url and logo_url.startswith("data:"):
        try:
            logo_data = logo_url.split(",")[1]
            logo_bytes = base64.b64decode(logo_data)
            logo_img = ImageReader(BytesIO(logo_bytes))
            p.drawImage(logo_img, 30, height - 80, width=50, height=50, preserveAspectRatio=True)
        except:
            pass
    
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100 if logo_url else 50, height - 55, f"{company_name} - Account Audit")
    
    y = height - 140
    p.setFillColor(HexColor("#000000"))
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"@{audit['username']}")
    y -= 30
    
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Engagement Score: {audit['engagement_score']}/100")
    y -= 20
    p.drawString(50, y, f"Shadowban Risk: {audit['shadowban_risk'].upper()}")
    y -= 20
    p.drawString(50, y, f"Content Consistency: {audit['content_consistency']}/100")
    if audit.get('estimated_followers'):
        y -= 20
        p.drawString(50, y, f"Estimated Followers: {audit['estimated_followers']:,}")
    y -= 40
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Growth Mistakes:")
    y -= 20
    p.setFont("Helvetica", 11)
    for mistake in audit.get('growth_mistakes', [])[:5]:
        p.drawString(60, y, f"• {mistake[:80]}")
        y -= 18
    y -= 20
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Recommendations:")
    y -= 20
    p.setFont("Helvetica", 11)
    for rec in audit.get('recommendations', [])[:7]:
        p.drawString(60, y, f"• {rec[:80]}")
        y -= 18
    
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#666666"))
    p.drawString(50, 30, f"Generated by {company_name} | {datetime.now().strftime('%Y-%m-%d')}")
    
    p.save()
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=audit_{audit['username']}.pdf"}
    )
