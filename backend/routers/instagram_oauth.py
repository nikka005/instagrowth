from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
import httpx
import uuid
import os
import logging

from database import get_database
from dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/instagram", tags=["Instagram API"])

# Instagram Business Login API endpoints
INSTAGRAM_AUTH_URL = "https://www.instagram.com/oauth/authorize"
INSTAGRAM_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
INSTAGRAM_GRAPH_URL = "https://graph.instagram.com"
# Meta Graph API for business accounts
META_GRAPH_URL = "https://graph.facebook.com/v18.0"

async def get_meta_credentials():
    """Get Meta API credentials from system settings or environment"""
    db = get_database()
    settings = await db.system_settings.find_one({"setting_id": "global"}, {"_id": 0})
    
    app_id = settings.get("meta_app_id") if settings else None
    app_secret = settings.get("meta_app_secret") if settings else None
    
    if not app_id:
        app_id = os.environ.get("META_APP_ID")
    if not app_secret:
        app_secret = os.environ.get("META_APP_SECRET")
    
    return app_id, app_secret

@router.get("/auth/url")
async def get_instagram_auth_url(request: Request):
    """Generate Instagram OAuth URL for user to connect their account"""
    db = get_database()
    user = await get_current_user(request, db)
    
    app_id, app_secret = await get_meta_credentials()
    
    if not app_id or not app_secret:
        raise HTTPException(
            status_code=400, 
            detail="Instagram API not configured. Please contact admin to set up Meta API credentials."
        )
    
    # Get the site URL for redirect - prioritize SITE_URL, fallback to request origin
    site_url = os.environ.get("SITE_URL")
    if not site_url:
        # Try to get from request origin header
        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")
        if origin and "instagrowth.io" in origin:
            site_url = origin
        elif referer and "instagrowth.io" in referer:
            site_url = referer.split("/")[0] + "//" + referer.split("/")[2]
        else:
            site_url = "https://instagrowth.io"
    
    # Ensure no trailing slash
    site_url = site_url.rstrip("/")
    redirect_uri = f"{site_url}/api/instagram/callback"
    
    # Store state for security
    state = f"{user.user_id}_{uuid.uuid4().hex[:8]}"
    await db.oauth_states.update_one(
        {"state": state},
        {"$set": {
            "user_id": user.user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "type": "instagram"
        }},
        upsert=True
    )
    
    # Instagram Business Login scopes
    scopes = "instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish"
    
    auth_url = (
        f"{INSTAGRAM_AUTH_URL}?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scopes}&"
        f"response_type=code&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def instagram_callback(request: Request, code: str = None, state: str = None, error: str = None, error_description: str = None):
    """Handle Instagram OAuth callback"""
    db = get_database()
    
    # Get site URL for redirects - hardcode for production
    site_url = os.environ.get("SITE_URL", "https://instagrowth.io")
    if not site_url or "localhost" in site_url:
        site_url = "https://instagrowth.io"
    
    if error:
        return RedirectResponse(f"{site_url}/accounts?error={error_description or error}")
    
    if not code or not state:
        return RedirectResponse(f"{site_url}/accounts?error=Missing authorization code")
    
    # Verify state
    oauth_state = await db.oauth_states.find_one({"state": state})
    if not oauth_state:
        return RedirectResponse(f"{site_url}/accounts?error=Invalid state")
    
    user_id = oauth_state["user_id"]
    await db.oauth_states.delete_one({"state": state})
    
    app_id, app_secret = await get_meta_credentials()
    redirect_uri = f"{site_url}/api/instagram/callback"
    
    try:
        # Exchange code for access token using Instagram API
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                INSTAGRAM_TOKEN_URL,
                data={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": code
                }
            )
            
            if token_response.status_code != 200:
                error_data = token_response.json()
                error_msg = error_data.get("error_message", "Failed to get access token")
                return RedirectResponse(f"{site_url}/accounts?error={error_msg}")
            
            token_data = token_response.json()
            short_lived_token = token_data.get("access_token")
            instagram_user_id = token_data.get("user_id")
            
            # Exchange for long-lived token
            long_token_response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/access_token",
                params={
                    "grant_type": "ig_exchange_token",
                    "client_secret": app_secret,
                    "access_token": short_lived_token
                }
            )
            
            if long_token_response.status_code == 200:
                long_token_data = long_token_response.json()
                access_token = long_token_data.get("access_token", short_lived_token)
                expires_in = long_token_data.get("expires_in", 5184000)  # 60 days default
            else:
                access_token = short_lived_token
                expires_in = 3600
            
            # Get Instagram user profile with extended fields
            profile_response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me",
                params={
                    "fields": "id,username,account_type,media_count,profile_picture_url,followers_count,follows_count,biography,name",
                    "access_token": access_token
                }
            )
            
            if profile_response.status_code != 200:
                return RedirectResponse(f"{site_url}/accounts?error=Failed to get Instagram profile")
            
            profile_data = profile_response.json()
            logger.info(f"Profile data received: {profile_data}")
            
            # Save the connected account to instagram_accounts collection
            account_id = f"ig_{uuid.uuid4().hex[:12]}"
            username = profile_data.get("username", "")
            
            account_doc = {
                "account_id": account_id,
                "user_id": user_id,
                "team_id": None,
                "instagram_user_id": str(instagram_user_id),
                "instagram_id": str(instagram_user_id),  # For Graph API calls
                "username": username,
                "niche": "Other",  # Default niche, user can update later
                "notes": f"Connected via Instagram API on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                "account_type": profile_data.get("account_type"),
                "follower_count": profile_data.get("followers_count"),
                "following_count": profile_data.get("follows_count"),
                "media_count": profile_data.get("media_count"),
                "biography": profile_data.get("biography"),
                "name": profile_data.get("name"),
                "engagement_rate": None,
                "estimated_reach": None,
                "posting_frequency": None,
                "best_posting_time": None,
                "profile_picture": profile_data.get("profile_picture_url"),
                "access_token": access_token,
                "token_expires_at": datetime.now(timezone.utc).timestamp() + expires_in,
                "connection_status": "connected",
                "last_audit_date": None,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "connected_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Check if account already exists in instagram_accounts collection
            existing = await db.instagram_accounts.find_one({
                "user_id": user_id,
                "instagram_user_id": str(instagram_user_id)
            })
            
            if existing:
                # Update existing account with new token
                logger.info(f"Updating existing Instagram account for user {user_id}: @{username}")
                await db.instagram_accounts.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "access_token": access_token,
                        "token_expires_at": account_doc["token_expires_at"],
                        "media_count": profile_data.get("media_count"),
                        "connection_status": "connected",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                logger.info(f"Successfully updated account @{username}")
            else:
                # Insert new account
                logger.info(f"Creating new Instagram account for user {user_id}: @{username}")
                await db.instagram_accounts.insert_one(account_doc)
                logger.info(f"Successfully created account @{username} with id {account_id}")
            
            return RedirectResponse(f"{site_url}/accounts?success=true&connected=1")
            
    except Exception as e:
        return RedirectResponse(f"{site_url}/accounts?error={str(e)}")

@router.post("/{account_id}/refresh")
async def refresh_instagram_data(account_id: str, request: Request):
    """Refresh Instagram account data from API"""
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not account.get("access_token"):
        raise HTTPException(status_code=400, detail="Account not connected via Instagram API")
    
    access_token = account["access_token"]
    instagram_id = account.get("instagram_id") or account.get("instagram_user_id")
    
    try:
        async with httpx.AsyncClient() as client:
            # First try Instagram Graph API for basic profile
            response = await client.get(
                f"{INSTAGRAM_GRAPH_URL}/me",
                params={
                    "fields": "id,username,account_type,media_count,profile_picture_url,followers_count,follows_count,biography,name",
                    "access_token": access_token
                },
                timeout=15
            )
            
            update_data = {
                "last_refreshed": datetime.now(timezone.utc).isoformat()
            }
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Instagram API response: {data}")
                
                update_data.update({
                    "username": data.get("username", account.get("username")),
                    "media_count": data.get("media_count"),
                    "account_type": data.get("account_type"),
                    "profile_picture": data.get("profile_picture_url"),
                    "follower_count": data.get("followers_count"),
                    "following_count": data.get("follows_count"),
                    "biography": data.get("biography"),
                    "name": data.get("name")
                })
            else:
                # Try with Facebook Graph API for business accounts
                logger.info(f"Basic API failed, trying business account endpoint")
                
                if instagram_id:
                    biz_response = await client.get(
                        f"{META_GRAPH_URL}/{instagram_id}",
                        params={
                            "fields": "id,username,name,profile_picture_url,followers_count,follows_count,media_count,biography",
                            "access_token": access_token
                        },
                        timeout=15
                    )
                    
                    if biz_response.status_code == 200:
                        data = biz_response.json()
                        logger.info(f"Business API response: {data}")
                        
                        update_data.update({
                            "username": data.get("username", account.get("username")),
                            "media_count": data.get("media_count"),
                            "profile_picture": data.get("profile_picture_url"),
                            "follower_count": data.get("followers_count"),
                            "following_count": data.get("follows_count"),
                            "biography": data.get("biography"),
                            "name": data.get("name")
                        })
                    else:
                        error_data = biz_response.json()
                        logger.warning(f"Business API error: {error_data}")
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            await db.instagram_accounts.update_one(
                {"account_id": account_id},
                {"$set": update_data}
            )
            
            return {
                "message": "Account refreshed",
                "data": update_data
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error refreshing account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Instagram API: {str(e)}")

@router.get("/{account_id}/insights")
async def get_instagram_insights(account_id: str, request: Request):
    """Get Instagram account insights"""
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not account.get("access_token") or not account.get("instagram_id"):
        raise HTTPException(status_code=400, detail="Account not connected via Instagram API")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{META_GRAPH_URL}/{account['instagram_id']}/insights",
                params={
                    "metric": "impressions,reach,profile_views,follower_count",
                    "period": "day",
                    "access_token": account["access_token"]
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Failed to get insights")
                raise HTTPException(status_code=400, detail=error_msg)
            
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Instagram API: {str(e)}")

@router.get("/{account_id}/media")
async def get_instagram_media(account_id: str, limit: int = 25, request: Request = None):
    """Get recent media from Instagram account"""
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not account.get("access_token") or not account.get("instagram_id"):
        raise HTTPException(status_code=400, detail="Account not connected via Instagram API")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{META_GRAPH_URL}/{account['instagram_id']}/media",
                params={
                    "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                    "limit": limit,
                    "access_token": account["access_token"]
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Failed to get media")
                raise HTTPException(status_code=400, detail=error_msg)
            
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Instagram API: {str(e)}")

@router.delete("/{account_id}/disconnect")
async def disconnect_instagram(account_id: str, request: Request):
    """Disconnect Instagram account (remove API access)"""
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.instagram_accounts.update_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"$set": {
            "access_token": None,
            "connection_status": "disconnected",
            "disconnected_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Instagram account disconnected"}
