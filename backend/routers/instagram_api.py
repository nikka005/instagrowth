"""
Instagram Graph API Integration

This module provides real Instagram API integration using Meta's Graph API.
Requires:
- Meta Developer App with Instagram Basic Display or Instagram Graph API
- Valid access tokens from user OAuth flow

Note: Instagram API requires Meta Business verification for production use.
"""
from fastapi import APIRouter, HTTPException, Request, Query
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import httpx
import os
import logging

from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/instagram-api", tags=["Instagram API"])

logger = logging.getLogger(__name__)

# Instagram API Configuration
INSTAGRAM_APP_ID = os.environ.get('INSTAGRAM_APP_ID', '')
INSTAGRAM_APP_SECRET = os.environ.get('INSTAGRAM_APP_SECRET', '')
INSTAGRAM_REDIRECT_URI = os.environ.get('INSTAGRAM_REDIRECT_URI', 'https://growth-admin-staging.preview.emergentagent.com/auth/instagram/callback')

# Meta Graph API Base URLs
INSTAGRAM_BASIC_DISPLAY_API = "https://graph.instagram.com"
INSTAGRAM_GRAPH_API = "https://graph.facebook.com/v18.0"

class InstagramAPIClient:
    """Instagram API Client for fetching real data"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = INSTAGRAM_BASIC_DISPLAY_API
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get the authenticated user's profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me",
                params={
                    "fields": "id,username,account_type,media_count",
                    "access_token": self.access_token
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch Instagram profile")
            return response.json()
    
    async def get_user_media(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get user's recent media"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me/media",
                params={
                    "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                    "limit": limit,
                    "access_token": self.access_token
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch media")
            data = response.json()
            return data.get("data", [])
    
    async def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Get insights for a specific media (requires Instagram Business/Creator account)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{media_id}/insights",
                params={
                    "metric": "engagement,impressions,reach,saved",
                    "access_token": self.access_token
                }
            )
            if response.status_code != 200:
                return {}  # Insights may not be available for all account types
            return response.json()
    
    async def get_account_insights(self, period: str = "day") -> Dict[str, Any]:
        """Get account insights (requires Instagram Business/Creator account)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me/insights",
                params={
                    "metric": "impressions,reach,follower_count,profile_views",
                    "period": period,
                    "access_token": self.access_token
                }
            )
            if response.status_code != 200:
                return {}
            return response.json()

# ==================== OAuth Flow ====================

@router.get("/auth/url")
async def get_instagram_auth_url(request: Request):
    """Generate Instagram OAuth URL"""
    if not INSTAGRAM_APP_ID:
        raise HTTPException(status_code=500, detail="Instagram API not configured. Set INSTAGRAM_APP_ID in environment.")
    
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_APP_ID}"
        f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
        f"&scope=user_profile,user_media"
        f"&response_type=code"
    )
    return {"auth_url": auth_url}

@router.get("/auth/callback")
async def instagram_oauth_callback(code: str, request: Request):
    """Handle Instagram OAuth callback"""
    db = get_database()
    user = await get_current_user(request, db)
    
    if not INSTAGRAM_APP_ID or not INSTAGRAM_APP_SECRET:
        raise HTTPException(status_code=500, detail="Instagram API not configured")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": INSTAGRAM_APP_ID,
                "client_secret": INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": INSTAGRAM_REDIRECT_URI,
                "code": code
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = response.json()
    
    # Get long-lived token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{INSTAGRAM_GRAPH_API}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": INSTAGRAM_APP_SECRET,
                "access_token": token_data["access_token"]
            }
        )
        
        if response.status_code == 200:
            long_lived_data = response.json()
            access_token = long_lived_data.get("access_token", token_data["access_token"])
            expires_in = long_lived_data.get("expires_in", 3600)
        else:
            access_token = token_data["access_token"]
            expires_in = 3600
    
    # Get user profile
    ig_client = InstagramAPIClient(access_token)
    profile = await ig_client.get_user_profile()
    
    # Store connection
    connection_doc = {
        "connection_id": f"ig_conn_{profile['id']}",
        "user_id": user.user_id,
        "instagram_user_id": profile["id"],
        "username": profile.get("username"),
        "account_type": profile.get("account_type"),
        "access_token": access_token,
        "token_expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(),
        "connected_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    await db.instagram_connections.update_one(
        {"user_id": user.user_id, "instagram_user_id": profile["id"]},
        {"$set": connection_doc},
        upsert=True
    )
    
    return {
        "message": "Instagram connected successfully",
        "username": profile.get("username"),
        "account_type": profile.get("account_type")
    }

# ==================== Data Endpoints ====================

@router.get("/profile/{account_id}")
async def get_real_instagram_profile(account_id: str, request: Request):
    """Get real Instagram profile data"""
    db = get_database()
    user = await get_current_user(request, db)
    
    # Get account with connection
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check for Instagram connection
    connection = await db.instagram_connections.find_one(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    
    if not connection:
        return {
            "source": "ai_estimated",
            "message": "No Instagram API connection. Using AI-estimated data.",
            "profile": {
                "username": account.get("username"),
                "follower_count": account.get("follower_count"),
                "engagement_rate": account.get("engagement_rate"),
                "estimated": True
            }
        }
    
    # Check token expiry
    token_expires = datetime.fromisoformat(connection["token_expires_at"].replace('Z', '+00:00'))
    if token_expires < datetime.now(timezone.utc):
        return {
            "source": "ai_estimated",
            "message": "Instagram token expired. Please reconnect.",
            "profile": {
                "username": account.get("username"),
                "follower_count": account.get("follower_count"),
                "engagement_rate": account.get("engagement_rate"),
                "estimated": True
            }
        }
    
    # Fetch real data
    try:
        ig_client = InstagramAPIClient(connection["access_token"])
        profile = await ig_client.get_user_profile()
        media = await ig_client.get_user_media(limit=10)
        
        # Calculate engagement rate from recent posts
        if media:
            total_engagement = sum((m.get("like_count", 0) + m.get("comments_count", 0)) for m in media)
            avg_engagement = total_engagement / len(media)
            engagement_rate = (avg_engagement / profile.get("media_count", 1)) * 100 if profile.get("media_count") else 0
        else:
            engagement_rate = 0
        
        # Update stored account with real data
        await db.instagram_accounts.update_one(
            {"account_id": account_id},
            {"$set": {
                "follower_count": profile.get("followers_count"),
                "media_count": profile.get("media_count"),
                "engagement_rate": round(engagement_rate, 2),
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "data_source": "instagram_api"
            }}
        )
        
        return {
            "source": "instagram_api",
            "profile": {
                "username": profile.get("username"),
                "account_type": profile.get("account_type"),
                "media_count": profile.get("media_count"),
                "follower_count": profile.get("followers_count"),
                "engagement_rate": round(engagement_rate, 2),
                "estimated": False
            },
            "recent_media": media[:5]
        }
    except Exception as e:
        logger.error(f"Instagram API error: {e}")
        return {
            "source": "ai_estimated",
            "message": f"Instagram API error: {str(e)}",
            "profile": {
                "username": account.get("username"),
                "follower_count": account.get("follower_count"),
                "engagement_rate": account.get("engagement_rate"),
                "estimated": True
            }
        }

@router.get("/media/{account_id}")
async def get_instagram_media(account_id: str, limit: int = 25, request: Request = None):
    """Get Instagram media for an account"""
    db = get_database()
    user = await get_current_user(request, db)
    
    connection = await db.instagram_connections.find_one(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    
    if not connection:
        raise HTTPException(status_code=400, detail="No Instagram connection. Please connect your account first.")
    
    try:
        ig_client = InstagramAPIClient(connection["access_token"])
        media = await ig_client.get_user_media(limit=limit)
        return {"media": media, "count": len(media)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch media: {str(e)}")

@router.get("/insights/{account_id}")
async def get_instagram_insights(account_id: str, request: Request):
    """Get Instagram account insights (Business/Creator accounts only)"""
    db = get_database()
    user = await get_current_user(request, db)
    
    connection = await db.instagram_connections.find_one(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    
    if not connection:
        raise HTTPException(status_code=400, detail="No Instagram connection")
    
    try:
        ig_client = InstagramAPIClient(connection["access_token"])
        insights = await ig_client.get_account_insights()
        
        if not insights:
            return {
                "message": "Insights not available. Requires Instagram Business or Creator account.",
                "available": False
            }
        
        return {"insights": insights, "available": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")

@router.post("/sync/{account_id}")
async def sync_instagram_data(account_id: str, request: Request):
    """Force sync Instagram data from API"""
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    connection = await db.instagram_connections.find_one(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    
    if not connection:
        return {"synced": False, "message": "No Instagram API connection"}
    
    try:
        ig_client = InstagramAPIClient(connection["access_token"])
        profile = await ig_client.get_user_profile()
        media = await ig_client.get_user_media(limit=25)
        
        # Calculate metrics
        if media:
            total_likes = sum(m.get("like_count", 0) for m in media)
            total_comments = sum(m.get("comments_count", 0) for m in media)
            avg_engagement = (total_likes + total_comments) / len(media)
            engagement_rate = (avg_engagement / max(profile.get("followers_count", 1), 1)) * 100
        else:
            engagement_rate = 0
        
        # Update account
        await db.instagram_accounts.update_one(
            {"account_id": account_id},
            {"$set": {
                "follower_count": profile.get("followers_count"),
                "media_count": profile.get("media_count"),
                "engagement_rate": round(engagement_rate, 2),
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "data_source": "instagram_api"
            }}
        )
        
        return {
            "synced": True,
            "data": {
                "followers": profile.get("followers_count"),
                "media_count": profile.get("media_count"),
                "engagement_rate": round(engagement_rate, 2)
            }
        }
    except Exception as e:
        return {"synced": False, "message": str(e)}

@router.get("/connections")
async def get_instagram_connections(request: Request):
    """Get all Instagram connections for the user"""
    db = get_database()
    user = await get_current_user(request, db)
    
    connections = await db.instagram_connections.find(
        {"user_id": user.user_id},
        {"_id": 0, "access_token": 0}
    ).to_list(100)
    
    return {"connections": connections}

@router.delete("/connections/{connection_id}")
async def disconnect_instagram(connection_id: str, request: Request):
    """Disconnect Instagram account"""
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.instagram_connections.delete_one(
        {"connection_id": connection_id, "user_id": user.user_id}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return {"message": "Instagram disconnected"}
