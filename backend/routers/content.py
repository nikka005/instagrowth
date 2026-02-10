from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json
import httpx
import logging

from models import ContentItem, ContentRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_MEDIUM

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content", tags=["Content Engine"])

INSTAGRAM_GRAPH_URL = "https://graph.instagram.com"

async def fetch_account_posts(access_token: str, limit: int = 10):
    """Fetch recent posts for content context"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me/media",
                params={
                    "fields": "id,caption,media_type,like_count,comments_count",
                    "limit": limit,
                    "access_token": access_token
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("data", [])
    except Exception as e:
        logger.warning(f"Could not fetch posts for context: {e}")
    return []

def analyze_content_style(posts: list):
    """Analyze existing content style from real posts"""
    if not posts:
        return {}
    
    captions = [p.get("caption", "") for p in posts if p.get("caption")]
    content_types = {}
    for p in posts:
        t = p.get("media_type", "IMAGE")
        content_types[t] = content_types.get(t, 0) + 1
    
    avg_caption_length = sum(len(c) for c in captions) / len(captions) if captions else 0
    uses_emojis = any("😀" in c or "🔥" in c or "❤" in c or "✨" in c for c in captions)
    uses_hashtags = any("#" in c for c in captions)
    
    return {
        "avg_caption_length": int(avg_caption_length),
        "uses_emojis": uses_emojis,
        "uses_hashtags": uses_hashtags,
        "content_mix": content_types,
        "sample_captions": captions[:3]
    }

@router.post("/generate", response_model=ContentItem)
async def generate_content(data: ContentRequest, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    # Map content types to credit features
    feature_map = {
        "reels": "content_ideas",
        "hooks": "hooks",
        "captions": "caption",
        "hashtags": "hashtags"
    }
    feature = feature_map.get(data.content_type, "content_ideas")
    
    await check_ai_usage(user, db, feature=feature)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    niche = data.niche or account.get("niche", "general")
    topic = data.topic or "trending topics"
    
    # Fetch real posts for context if available
    content_style = {}
    if account.get("access_token"):
        logger.info(f"Fetching real posts for content context @{account['username']}")
        posts = await fetch_account_posts(account["access_token"], limit=10)
        content_style = analyze_content_style(posts)
    
    # Build context-aware prompt
    style_context = ""
    if content_style:
        style_context = f"""
REAL ACCOUNT ANALYSIS:
- Average caption length: {content_style.get('avg_caption_length', 0)} characters
- Uses emojis: {'Yes' if content_style.get('uses_emojis') else 'No'}
- Uses hashtags: {'Yes' if content_style.get('uses_hashtags') else 'No'}
- Content mix: {content_style.get('content_mix', {})}
- Sample captions from their posts: {content_style.get('sample_captions', [])}

Match this style in generated content."""
    
    account_context = f"""
ACCOUNT INFO:
- Username: @{account['username']}
- Niche: {niche}
- Followers: {account.get('follower_count', 'Unknown')}
- Engagement Rate: {account.get('engagement_rate', 'Unknown')}%
{style_context}"""
    
    prompts = {
        "reels": f"""Generate 5 viral Reel ideas for {niche} about {topic}.
{account_context}
Include title, concept, hook, audio suggestion tailored to their audience size and style.
Return JSON array.""",
        "hooks": f"""Generate 7 scroll-stopping hooks for {niche} about {topic}.
{account_context}
Make them match the account's voice and engagement level.
Return JSON array of strings.""",
        "captions": f"""Generate 5 engaging captions for {niche} about {topic}.
{account_context}
Match their caption style, emoji usage, and include CTAs.
Return JSON array of strings.""",
        "hashtags": f"""Generate 30 hashtags for {niche} about {topic}.
{account_context}
Mix competition levels appropriate for {account.get('follower_count', 5000)} followers.
Return JSON array of strings."""
    }
    
    system_message = "You are an Instagram content strategist analyzing REAL account data. Return ONLY valid JSON array. Match the account's proven style."
    prompt = prompts.get(data.content_type, prompts["captions"])
    
    try:
        ai_response = await generate_ai_content(prompt, system_message, timeout_seconds=AI_TIMEOUT_MEDIUM)
        cleaned = ai_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        content_list = json.loads(cleaned.strip())
        if isinstance(content_list[0], dict):
            content_list = [str(item) for item in content_list]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        fallback = {
            "reels": ["Day in the life", "Behind the scenes", "Tutorial", "Transformation", "Trending dance"],
            "hooks": ["Wait until you see...", "POV: You discovered...", "This changed everything", "Stop scrolling if...", "Secret nobody tells..."],
            "captions": ["Ready to level up?", "Save this!", "Comment YES!", "Tag someone", "Double tap"],
            "hashtags": ["#instagramgrowth", "#contentcreator", "#reels", "#viral", "#growthhacks"]
        }
        content_list = fallback.get(data.content_type, fallback["captions"])
    
    await increment_ai_usage(user.user_id, db, feature=feature)
    
    content_id = f"content_{uuid.uuid4().hex[:12]}"
    content_doc = {
        "content_id": content_id, "account_id": data.account_id, "user_id": user.user_id,
        "content_type": data.content_type, "content": content_list, "is_favorite": False,
        "based_on_real_data": bool(content_style),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.content_items.insert_one(content_doc)
    return ContentItem(**content_doc)

@router.get("", response_model=List[ContentItem])
async def get_content(account_id: Optional[str] = None, content_type: Optional[str] = None, 
                      favorites_only: bool = False, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    if content_type:
        query["content_type"] = content_type
    if favorites_only:
        query["is_favorite"] = True
    
    items = await db.content_items.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [ContentItem(**item) for item in items]

@router.put("/{content_id}/favorite")
async def toggle_favorite(content_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    content = await db.content_items.find_one({"content_id": content_id, "user_id": user.user_id}, {"_id": 0})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    new_status = not content.get("is_favorite", False)
    await db.content_items.update_one({"content_id": content_id}, {"$set": {"is_favorite": new_status}})
    return {"is_favorite": new_status}
