from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import uuid
import jwt
import httpx

from models import UserCreate, UserLogin, User, UserResponse, PasswordResetRequest, PasswordResetConfirm
from utils import hash_password, verify_password, create_token, create_verification_token, JWT_SECRET
from services import send_email
from database import get_database
from dependencies import create_notification
from routers.admin_websocket import notify_new_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(data: UserCreate, request: Request):
    db = get_database()
    existing = await db.users.find_one({"email": data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    verification_token = create_verification_token()
    
    # Check for referral code
    referral_code = request.query_params.get("ref")
    
    user_doc = {
        "user_id": user_id,
        "email": data.email,
        "name": data.name,
        "password_hash": hash_password(data.password),
        "picture": None,
        "role": "starter",
        "plan_id": None,
        "account_limit": 1,
        "ai_usage_limit": 10,
        "ai_usage_current": 0,
        "email_verified": False,
        "verification_token": verification_token,
        "team_id": None,
        "extra_accounts": 0,
        "referred_by": referral_code,
        "onboarding_completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    await db.users.insert_one(user_doc)
    
    origin = request.headers.get("origin", "https://email-send-fail.preview.emergentagent.com")
    verify_url = f"{origin}/verify-email?token={verification_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Welcome to InstaGrowth OS!</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p>Hi {data.name},</p>
            <p>Please verify your email address:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Verify Email</a>
            </div>
        </div>
    </div>
    """
    await send_email(data.email, "Verify your InstaGrowth OS account", email_html)
    await create_notification(user_id, "system", "Welcome to InstaGrowth OS!", "Start by adding your first Instagram account.", "/accounts", db)
    
    # Process referral if code provided
    if referral_code:
        try:
            from routers.referrals import process_referral_signup
            await process_referral_signup(user_id, data.email, referral_code)
        except Exception as e:
            pass  # Don't fail registration if referral processing fails
    
    # Send welcome automation email
    try:
        from routers.email_automation import send_automated_email
        await send_automated_email("welcome", data.email, {
            "name": data.name,
            "dashboard_url": f"{origin}/dashboard"
        })
    except Exception:
        pass  # Don't fail registration if welcome email fails
    
    # Notify admins of new user registration
    try:
        await notify_new_user({"user_id": user_id, "email": data.email, "name": data.name, "role": "starter"})
    except Exception:
        pass  # Don't fail registration if notification fails
    
    token = create_token(user_id, data.email)
    return {"token": token, "user": UserResponse(**user_doc)}

@router.post("/verify-email")
async def verify_email(token: str):
    db = get_database()
    user_doc = await db.users.find_one({"verification_token": token}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    await db.users.update_one(
        {"verification_token": token},
        {"$set": {"email_verified": True, "verification_token": None, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, request: Request):
    db = get_database()
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        return {"message": "If this email exists, a password reset link will be sent"}
    
    reset_token = create_verification_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_resets.insert_one({
        "token": reset_token,
        "user_id": user_doc["user_id"],
        "email": data.email,
        "expires_at": expires_at.isoformat(),
        "used": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    origin = request.headers.get("origin", "https://email-send-fail.preview.emergentagent.com")
    reset_url = f"{origin}/reset-password?token={reset_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Reset Your Password</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p>Hi {user_doc['name']},</p>
            <p>Click below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Reset Password</a>
            </div>
            <p style="font-size: 14px; color: #666;">This link expires in 1 hour.</p>
        </div>
    </div>
    """
    await send_email(data.email, "Reset your InstaGrowth OS password", email_html)
    return {"message": "If this email exists, a password reset link will be sent"}

@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm):
    db = get_database()
    reset_doc = await db.password_resets.find_one({"token": data.token, "used": False}, {"_id": 0})
    if not reset_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = datetime.fromisoformat(reset_doc["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    await db.users.update_one(
        {"user_id": reset_doc["user_id"]},
        {"$set": {"password_hash": hash_password(data.new_password), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    await db.password_resets.update_one({"token": data.token}, {"$set": {"used": True}})
    return {"message": "Password reset successfully"}

@router.post("/login")
async def login(data: UserLogin, totp_code: str = None, response: Response = None):
    db = get_database()
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if 2FA is enabled
    if user_doc.get("is_2fa_enabled"):
        if not totp_code:
            return {"requires_2fa": True, "message": "2FA code required", "user_id": user_doc["user_id"]}
        
        # Verify 2FA code
        import pyotp
        totp = pyotp.TOTP(user_doc["totp_secret"])
        if not totp.verify(totp_code):
            # Check backup codes
            if totp_code not in user_doc.get("backup_codes", []):
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
            # Remove used backup code
            await db.users.update_one(
                {"user_id": user_doc["user_id"]},
                {"$pull": {"backup_codes": totp_code}}
            )
    
    token = create_token(user_doc["user_id"], data.email)
    
    response.set_cookie(
        key="session_token", value=token, httponly=True, secure=True,
        samesite="none", max_age=7 * 24 * 60 * 60, path="/"
    )
    return {"token": token, "user": UserResponse(**user_doc)}

@router.post("/session")
async def create_session(request: Request, response: Response):
    db = get_database()
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        auth_data = resp.json()
    
    user_doc = await db.users.find_one({"email": auth_data["email"]}, {"_id": 0})
    
    if not user_doc:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id, "email": auth_data["email"], "name": auth_data["name"],
            "picture": auth_data.get("picture"), "password_hash": None, "role": "starter",
            "plan_id": None, "account_limit": 1, "ai_usage_limit": 10, "ai_usage_current": 0,
            "email_verified": True, "team_id": None, "extra_accounts": 0,
            "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": None
        }
        await db.users.insert_one(user_doc)
        await create_notification(user_id, "system", "Welcome!", "Start by adding your Instagram account.", "/accounts", db)
    else:
        if auth_data.get("picture") != user_doc.get("picture"):
            await db.users.update_one(
                {"user_id": user_doc["user_id"]},
                {"$set": {"picture": auth_data.get("picture"), "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            user_doc["picture"] = auth_data.get("picture")
    
    session_token = auth_data["session_token"]
    await db.user_sessions.insert_one({
        "user_id": user_doc["user_id"], "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    response.set_cookie(
        key="session_token", value=session_token, httponly=True, secure=True,
        samesite="none", max_age=7 * 24 * 60 * 60, path="/"
    )
    return {"user": UserResponse(**user_doc)}

@router.get("/me", response_model=UserResponse)
async def get_me(request: Request):
    from dependencies import get_current_user
    db = get_database()
    user = await get_current_user(request, db)
    return UserResponse(**user.model_dump())

@router.post("/logout")
async def logout(request: Request, response: Response):
    db = get_database()
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}

@router.post("/complete-onboarding")
async def complete_onboarding(goal: str = None, request: Request = None):
    """Mark user onboarding as completed"""
    from dependencies import get_current_user
    db = get_database()
    user = await get_current_user(request, db)
    
    update_data = {
        "onboarding_completed": True,
        "onboarding_goal": goal,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": update_data}
    )
    
    return {"message": "Onboarding completed", "goal": goal}


# ==================== DATA DELETION ====================

from pydantic import BaseModel

class DataDeletionRequest(BaseModel):
    email: str

@router.post("/data-deletion-request")
async def request_data_deletion(data: DataDeletionRequest):
    """Request deletion of all user data"""
    db = get_database()
    deletion_id = f"DEL-{uuid.uuid4().hex[:12].upper()}"
    
    # Create deletion request record
    deletion_doc = {
        "deletion_id": deletion_id,
        "email": data.email,
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "scheduled_deletion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    await db.data_deletion_requests.insert_one(deletion_doc)
    
    # Send confirmation email
    try:
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); padding: 30px; border-radius: 12px; text-align: center;">
                <h1 style="color: white; margin: 0;">Data Deletion Request</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
                <p>We received a request to delete all data associated with this email address from InstaGrowth OS.</p>
                <div style="background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Confirmation ID:</p>
                    <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #333;">{deletion_id}</p>
                </div>
                <p>Your data will be permanently deleted within 30 days.</p>
                <p style="font-size: 14px; color: #666;">If you did not request this, please contact support immediately.</p>
            </div>
        </div>
        """
        from services import send_email
        await send_email(data.email, "Data Deletion Request Confirmed", email_html)
    except:
        pass  # Don't fail if email fails
    
    return {"deletion_id": deletion_id, "message": "Data deletion request submitted"}

@router.post("/data-deletion-callback")
async def instagram_data_deletion_callback(request: Request):
    """Meta/Instagram Data Deletion Callback URL"""
    import hmac
    import hashlib
    import base64
    import json
    
    db = get_database()
    
    # Get the signed request from Meta
    body = await request.body()
    form_data = dict(item.split("=") for item in body.decode().split("&"))
    signed_request = form_data.get("signed_request", "")
    
    if not signed_request:
        raise HTTPException(status_code=400, detail="Missing signed_request")
    
    # Parse signed request
    try:
        encoded_sig, payload = signed_request.split(".", 1)
        # Decode payload
        payload_data = json.loads(base64.urlsafe_b64decode(payload + "=="))
        user_id = payload_data.get("user_id")
    except:
        raise HTTPException(status_code=400, detail="Invalid signed_request")
    
    # Create deletion record
    deletion_id = f"META-{uuid.uuid4().hex[:12].upper()}"
    
    deletion_doc = {
        "deletion_id": deletion_id,
        "meta_user_id": user_id,
        "source": "meta_callback",
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "scheduled_deletion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    await db.data_deletion_requests.insert_one(deletion_doc)
    
    # Remove Instagram tokens for this user
    await db.instagram_accounts.update_many(
        {"instagram_id": str(user_id)},
        {"$set": {"access_token": None, "connection_status": "disconnected"}}
    )
    
    # Return response as required by Meta
    origin = request.headers.get("origin", "https://email-send-fail.preview.emergentagent.com")
    return {
        "url": f"{origin}/data-deletion?id={deletion_id}",
        "confirmation_code": deletion_id
    }
