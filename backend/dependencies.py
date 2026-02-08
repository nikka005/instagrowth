from fastapi import HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
import os

JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')

async def get_current_user(request: Request, db):
    """Extract and validate user from request"""
    from models import User
    
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(session_token, JWT_SECRET, algorithms=["HS256"])
        user_doc = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user_doc)
    except jwt.ExpiredSignatureError:
        pass
    except jwt.InvalidTokenError:
        pass
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)

async def get_user_with_team_access(request: Request, db) -> tuple:
    """Get user and their accessible team IDs"""
    user = await get_current_user(request, db)
    team_ids = [user.team_id] if user.team_id else []
    
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0, "team_id": 1}
    ).to_list(100)
    team_ids.extend([m["team_id"] for m in member_teams])
    
    return user, list(set(team_ids))

async def check_account_limit(user, db):
    """Check if user has reached account limit"""
    count = await db.instagram_accounts.count_documents({"user_id": user.user_id})
    total_limit = user.account_limit + user.extra_accounts
    if count >= total_limit:
        raise HTTPException(status_code=403, detail=f"Account limit reached ({total_limit}). Upgrade your plan or purchase extra accounts.")

async def check_ai_usage(user, db):
    """Check if user has AI usage available"""
    from utils import check_rate_limit
    
    if user.ai_usage_current >= user.ai_usage_limit:
        raise HTTPException(status_code=403, detail=f"AI usage limit reached ({user.ai_usage_limit}). Upgrade your plan.")
    
    if not check_rate_limit(user.user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before making more AI requests.")

async def increment_ai_usage(user_id: str, db):
    """Increment user's AI usage counter"""
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"ai_usage_current": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

async def create_notification(user_id: str, type: str, title: str, message: str, action_url: Optional[str], db):
    """Create a notification for a user"""
    import uuid
    notification_doc = {
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "type": type,
        "title": title,
        "message": message,
        "read": False,
        "action_url": action_url,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification_doc)
    return notification_doc
