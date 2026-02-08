from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
import httpx
import uuid
import os

from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/instagram", tags=["Instagram API"])

# Meta API endpoints
META_AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
META_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
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
    
    # Get the frontend URL for redirect
    frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "").replace("/api", "")
    if not frontend_url:
        frontend_url = request.headers.get("origin", "http://localhost:3000")
    
    redirect_uri = f"{frontend_url}/api/instagram/callback"
    
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
    
    # Instagram Basic Display API scopes
    scopes = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"
    
    auth_url = (
        f"{META_AUTH_URL}?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scopes}&"
        f"response_type=code&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def instagram_callback(code: str = None, state: str = None, error: str = None, error_description: str = None):
    """Handle Instagram OAuth callback"""
    db = get_database()
    
    # Get frontend URL for redirects
    frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000").replace("/api", "")
    
    if error:
        return RedirectResponse(f"{frontend_url}/accounts?error={error_description or error}")
    
    if not code or not state:
        return RedirectResponse(f"{frontend_url}/accounts?error=Missing authorization code")
    
    # Verify state
    oauth_state = await db.oauth_states.find_one({"state": state})
    if not oauth_state:
        return RedirectResponse(f"{frontend_url}/accounts?error=Invalid state")
    
    user_id = oauth_state["user_id"]
    await db.oauth_states.delete_one({"state": state})
    
    app_id, app_secret = await get_meta_credentials()
    redirect_uri = f"{frontend_url}/api/instagram/callback"
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.get(
                META_TOKEN_URL,
                params={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "redirect_uri": redirect_uri,
                    "code": code
                }
            )
            
            if token_response.status_code != 200:
                error_data = token_response.json()
                error_msg = error_data.get("error", {}).get("message", "Failed to get access token")
                return RedirectResponse(f"{frontend_url}/accounts?error={error_msg}")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get long-lived token
            long_token_response = await client.get(
                f"{META_GRAPH_URL}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "fb_exchange_token": access_token
                }
            )
            
            if long_token_response.status_code == 200:
                long_token_data = long_token_response.json()
                access_token = long_token_data.get("access_token", access_token)
            
            # Get user's Facebook pages
            pages_response = await client.get(
                f"{META_GRAPH_URL}/me/accounts",
                params={"access_token": access_token}
            )
            
            if pages_response.status_code != 200:
                return RedirectResponse(f"{frontend_url}/accounts?error=Failed to get Facebook pages")
            
            pages_data = pages_response.json()
            pages = pages_data.get("data", [])
            
            if not pages:
                return RedirectResponse(f"{frontend_url}/accounts?error=No Facebook pages found. Please connect a page to your Instagram account.")
            
            # For each page, try to get the connected Instagram account
            connected_accounts = []
            for page in pages:
                page_id = page["id"]
                page_token = page["access_token"]
                
                ig_response = await client.get(
                    f"{META_GRAPH_URL}/{page_id}",
                    params={
                        "fields": "instagram_business_account",
                        "access_token": page_token
                    }
                )
                
                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    ig_account = ig_data.get("instagram_business_account")
                    
                    if ig_account:
                        ig_id = ig_account["id"]
                        
                        # Get Instagram account details
                        ig_details_response = await client.get(
                            f"{META_GRAPH_URL}/{ig_id}",
                            params={
                                "fields": "username,name,profile_picture_url,followers_count,follows_count,media_count,biography",
                                "access_token": page_token
                            }
                        )
                        
                        if ig_details_response.status_code == 200:
                            ig_details = ig_details_response.json()
                            connected_accounts.append({
                                "ig_id": ig_id,
                                "page_id": page_id,
                                "page_token": page_token,
                                "username": ig_details.get("username"),
                                "name": ig_details.get("name"),
                                "profile_picture": ig_details.get("profile_picture_url"),
                                "followers_count": ig_details.get("followers_count"),
                                "follows_count": ig_details.get("follows_count"),
                                "media_count": ig_details.get("media_count"),
                                "biography": ig_details.get("biography")
                            })
            
            if not connected_accounts:
                return RedirectResponse(f"{frontend_url}/accounts?error=No Instagram Business accounts found. Make sure your Instagram is connected to a Facebook Page.")
            
            # Save connected accounts to database
            for ig_account in connected_accounts:
                account_id = f"acc_{uuid.uuid4().hex[:12]}"
                
                # Check if account already exists
                existing = await db.instagram_accounts.find_one({
                    "user_id": user_id,
                    "instagram_id": ig_account["ig_id"]
                })
                
                if existing:
                    # Update existing account
                    await db.instagram_accounts.update_one(
                        {"account_id": existing["account_id"]},
                        {"$set": {
                            "access_token": ig_account["page_token"],
                            "follower_count": ig_account["followers_count"],
                            "following_count": ig_account["follows_count"],
                            "media_count": ig_account["media_count"],
                            "profile_picture": ig_account["profile_picture"],
                            "biography": ig_account["biography"],
                            "connected_at": datetime.now(timezone.utc).isoformat(),
                            "connection_status": "connected"
                        }}
                    )
                else:
                    # Create new account
                    account_doc = {
                        "account_id": account_id,
                        "user_id": user_id,
                        "instagram_id": ig_account["ig_id"],
                        "page_id": ig_account["page_id"],
                        "username": ig_account["username"],
                        "name": ig_account["name"],
                        "niche": "Other",
                        "notes": ig_account.get("biography", ""),
                        "profile_picture": ig_account["profile_picture"],
                        "follower_count": ig_account["followers_count"],
                        "following_count": ig_account["follows_count"],
                        "media_count": ig_account["media_count"],
                        "access_token": ig_account["page_token"],
                        "connection_status": "connected",
                        "connected_at": datetime.now(timezone.utc).isoformat(),
                        "last_audit_date": None,
                        "status": "active",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    await db.instagram_accounts.insert_one(account_doc)
            
            return RedirectResponse(f"{frontend_url}/accounts?success=true&connected={len(connected_accounts)}")
            
    except Exception as e:
        return RedirectResponse(f"{frontend_url}/accounts?error={str(e)}")

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
    
    if not account.get("access_token") or not account.get("instagram_id"):
        raise HTTPException(status_code=400, detail="Account not connected via Instagram API")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{META_GRAPH_URL}/{account['instagram_id']}",
                params={
                    "fields": "username,name,profile_picture_url,followers_count,follows_count,media_count,biography",
                    "access_token": account["access_token"]
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Failed to refresh data")
                raise HTTPException(status_code=400, detail=error_msg)
            
            data = response.json()
            
            await db.instagram_accounts.update_one(
                {"account_id": account_id},
                {"$set": {
                    "username": data.get("username", account["username"]),
                    "name": data.get("name"),
                    "profile_picture": data.get("profile_picture_url"),
                    "follower_count": data.get("followers_count"),
                    "following_count": data.get("follows_count"),
                    "media_count": data.get("media_count"),
                    "biography": data.get("biography"),
                    "last_refreshed": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "message": "Account refreshed",
                "followers": data.get("followers_count"),
                "following": data.get("follows_count"),
                "media_count": data.get("media_count")
            }
            
    except httpx.HTTPError as e:
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
