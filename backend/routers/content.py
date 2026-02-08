from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json

from models import ContentItem, ContentRequest
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_ai_content, AI_TIMEOUT_MEDIUM

router = APIRouter(prefix="/content", tags=["Content Engine"])

@router.post("/generate", response_model=ContentItem)
async def generate_content(data: ContentRequest, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_ai_usage(user, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    niche = data.niche or account.get("niche", "general")
    topic = data.topic or "trending topics"
    
    prompts = {
        "reels": f"Generate 5 viral Reel ideas for {niche} about {topic}. Include title, concept, hook, audio suggestion. Return JSON array.",
        "hooks": f"Generate 7 scroll-stopping hooks for {niche} about {topic}. Return JSON array of strings.",
        "captions": f"Generate 5 engaging captions for {niche} about {topic}. Include emojis, CTAs. Return JSON array of strings.",
        "hashtags": f"Generate 30 hashtags for {niche} about {topic}. Mix competition levels. Return JSON array of strings."
    }
    
    system_message = "You are an Instagram content strategist. Return ONLY valid JSON array."
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
    except Exception:
        fallback = {
            "reels": ["Day in the life", "Behind the scenes", "Tutorial", "Transformation", "Trending dance"],
            "hooks": ["Wait until you see...", "POV: You discovered...", "This changed everything", "Stop scrolling if...", "Secret nobody tells..."],
            "captions": ["Ready to level up?", "Save this!", "Comment YES!", "Tag someone", "Double tap"],
            "hashtags": ["#instagramgrowth", "#contentcreator", "#reels", "#viral", "#growthhacks"]
        }
        content_list = fallback.get(data.content_type, fallback["captions"])
    
    await increment_ai_usage(user.user_id, db)
    
    content_id = f"content_{uuid.uuid4().hex[:12]}"
    content_doc = {
        "content_id": content_id, "account_id": data.account_id, "user_id": user.user_id,
        "content_type": data.content_type, "content": content_list, "is_favorite": False,
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
