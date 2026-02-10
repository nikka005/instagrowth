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
import httpx
import logging

from models import Audit, AuditRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_MEDIUM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audits", tags=["AI Audits"])

INSTAGRAM_GRAPH_URL = "https://graph.instagram.com"

async def fetch_instagram_media(access_token: str, limit: int = 25):
    """Fetch recent media/posts from Instagram API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me/media",
                params={
                    "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                    "limit": limit,
                    "access_token": access_token
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.warning(f"Failed to fetch media: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        logger.error(f"Error fetching Instagram media: {e}")
        return []

def analyze_posts_data(posts: list, follower_count: int):
    """Analyze real post data to calculate engagement metrics"""
    if not posts:
        return {
            "total_posts": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "engagement_rate": 0,
            "post_types": {},
            "posting_frequency": "Unknown",
            "best_performing_post": None,
            "worst_performing_post": None,
            "captions_analysis": []
        }
    
    total_likes = 0
    total_comments = 0
    post_types = {"IMAGE": 0, "VIDEO": 0, "CAROUSEL_ALBUM": 0}
    posts_with_engagement = []
    captions = []
    
    for post in posts:
        likes = post.get("like_count", 0)
        comments = post.get("comments_count", 0)
        total_likes += likes
        total_comments += comments
        
        media_type = post.get("media_type", "IMAGE")
        post_types[media_type] = post_types.get(media_type, 0) + 1
        
        engagement = likes + comments
        posts_with_engagement.append({
            "id": post.get("id"),
            "caption": post.get("caption", "")[:100],
            "likes": likes,
            "comments": comments,
            "engagement": engagement,
            "type": media_type,
            "timestamp": post.get("timestamp")
        })
        
        if post.get("caption"):
            captions.append(post.get("caption", "")[:200])
    
    avg_likes = total_likes / len(posts) if posts else 0
    avg_comments = total_comments / len(posts) if posts else 0
    
    # Calculate engagement rate
    engagement_rate = 0
    if follower_count and follower_count > 0:
        engagement_rate = ((avg_likes + avg_comments) / follower_count) * 100
    
    # Sort by engagement
    posts_with_engagement.sort(key=lambda x: x["engagement"], reverse=True)
    
    return {
        "total_posts_analyzed": len(posts),
        "total_likes": total_likes,
        "total_comments": total_comments,
        "avg_likes": round(avg_likes, 1),
        "avg_comments": round(avg_comments, 1),
        "engagement_rate": round(engagement_rate, 2),
        "post_types": post_types,
        "best_performing_post": posts_with_engagement[0] if posts_with_engagement else None,
        "worst_performing_post": posts_with_engagement[-1] if posts_with_engagement else None,
        "recent_captions": captions[:5]
    }

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
    
    # Fetch real Instagram data if access token available
    posts_data = []
    posts_analysis = {}
    
    if account.get("access_token"):
        logger.info(f"Fetching real Instagram data for @{account['username']}")
        posts_data = await fetch_instagram_media(account["access_token"], limit=25)
        posts_analysis = analyze_posts_data(posts_data, account.get("follower_count", 0))
        logger.info(f"Analyzed {posts_analysis.get('total_posts_analyzed', 0)} posts")
    
    system_message = """You are an Instagram growth expert analyzing REAL account data. 
    Provide detailed analysis based on the actual metrics provided.
    Response must be valid JSON with:
    - engagement_score (0-100, based on real engagement rate)
    - shadowban_risk (low/medium/high, based on engagement patterns)
    - content_consistency (0-100, based on posting patterns)
    - growth_mistakes (array of 3-5 specific mistakes based on the data)
    - recommendations (array of 5-7 actionable recommendations)
    - roadmap (object with week1-4 arrays of specific tasks)
    - content_analysis (brief analysis of their caption style)
    Response must be valid JSON only, no markdown."""
    
    # Build detailed prompt with real data
    prompt = f"""Analyze this Instagram account with REAL data:

ACCOUNT INFO:
- Username: @{account['username']}
- Niche: {account.get('niche', 'Not specified')}
- Followers: {account.get('follower_count', 'Unknown')}
- Following: {account.get('following_count', 'Unknown')}
- Total Posts: {account.get('media_count', 'Unknown')}
- Account Type: {account.get('account_type', 'Unknown')}

REAL ENGAGEMENT METRICS (from last {posts_analysis.get('total_posts_analyzed', 0)} posts):
- Average Likes per Post: {posts_analysis.get('avg_likes', 'N/A')}
- Average Comments per Post: {posts_analysis.get('avg_comments', 'N/A')}
- Calculated Engagement Rate: {posts_analysis.get('engagement_rate', 'N/A')}%
- Total Likes (recent posts): {posts_analysis.get('total_likes', 'N/A')}
- Total Comments (recent posts): {posts_analysis.get('total_comments', 'N/A')}

CONTENT MIX:
- Images: {posts_analysis.get('post_types', {}).get('IMAGE', 0)}
- Videos/Reels: {posts_analysis.get('post_types', {}).get('VIDEO', 0)}
- Carousels: {posts_analysis.get('post_types', {}).get('CAROUSEL_ALBUM', 0)}

BEST PERFORMING POST:
{json.dumps(posts_analysis.get('best_performing_post', {}), indent=2) if posts_analysis.get('best_performing_post') else 'N/A'}

SAMPLE CAPTIONS:
{chr(10).join(['- ' + c[:100] for c in posts_analysis.get('recent_captions', [])[:3]]) if posts_analysis.get('recent_captions') else 'No captions available'}

Based on this REAL data, provide specific, actionable analysis."""
    
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
        
        # Use real engagement rate if available
        if posts_analysis.get('engagement_rate'):
            audit_data['real_engagement_rate'] = posts_analysis.get('engagement_rate')
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI parsing error: {e}")
        # Fallback with real data if available
        real_engagement = posts_analysis.get('engagement_rate', 3.5)
        engagement_score = min(100, int(real_engagement * 15)) if real_engagement else 65
        
        audit_data = {
            "engagement_score": engagement_score,
            "shadowban_risk": "low" if real_engagement > 3 else "medium" if real_engagement > 1 else "high",
            "content_consistency": 70,
            "real_engagement_rate": real_engagement,
            "growth_mistakes": [
                f"Average {posts_analysis.get('avg_comments', 0):.0f} comments per post - need more engagement",
                "Content mix could be improved" if posts_analysis.get('post_types', {}).get('VIDEO', 0) < 3 else "Good video content",
                "Inconsistent posting schedule",
                "Captions may need stronger CTAs"
            ],
            "recommendations": [
                f"Your engagement rate is {real_engagement:.2f}% - {'good' if real_engagement > 3 else 'needs improvement'}",
                f"Post more Reels - you have {posts_analysis.get('post_types', {}).get('VIDEO', 0)} videos",
                "Engage with followers in first 30 minutes of posting",
                "Use trending audio in Reels",
                f"Your best post got {posts_analysis.get('best_performing_post', {}).get('likes', 0)} likes - analyze what worked"
            ],
            "roadmap": {
                "week1": ["Audit top performing content", "Create content calendar", "Research trending audio"],
                "week2": ["Post 5 Reels", "Engage daily for 30 min", "Optimize bio"],
                "week3": ["Analyze performance", "Double down on what works"],
                "week4": ["Review analytics", "Plan next month strategy"]
            }
        }
    
    await increment_ai_usage(user.user_id, db, feature="audit")
    
    audit_id = f"audit_{uuid.uuid4().hex[:12]}"
    audit_doc = {
        "audit_id": audit_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "username": account["username"],
        "engagement_score": audit_data.get("engagement_score", 0),
        "shadowban_risk": audit_data.get("shadowban_risk", "unknown"),
        "content_consistency": audit_data.get("content_consistency", 0),
        "estimated_followers": account.get("follower_count"),
        "estimated_engagement_rate": audit_data.get("real_engagement_rate", posts_analysis.get("engagement_rate")),
        "growth_mistakes": audit_data.get("growth_mistakes", []),
        "recommendations": audit_data.get("recommendations", []),
        "roadmap": audit_data.get("roadmap", {}),
        "posts_analyzed": posts_analysis.get("total_posts_analyzed", 0),
        "avg_likes": posts_analysis.get("avg_likes"),
        "avg_comments": posts_analysis.get("avg_comments"),
        "content_analysis": audit_data.get("content_analysis"),
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
