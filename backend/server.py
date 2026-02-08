from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import httpx
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import base64
import asyncio
import resend
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment variables
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@instagrowth.app')

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Create the main app
app = FastAPI(title="InstaGrowth OS API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "starter"
    plan_id: Optional[str] = None
    account_limit: int = 1
    ai_usage_limit: int = 10
    ai_usage_current: int = 0
    email_verified: bool = False
    team_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str
    plan_id: Optional[str] = None
    account_limit: int
    ai_usage_limit: int
    ai_usage_current: int
    email_verified: bool = False
    team_id: Optional[str] = None

# Password Reset Models
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Team Models
class TeamCreate(BaseModel):
    name: str

class TeamInvite(BaseModel):
    email: EmailStr
    role: str = "viewer"  # viewer, editor, admin

class TeamMemberUpdate(BaseModel):
    role: str

class Team(BaseModel):
    model_config = ConfigDict(extra="ignore")
    team_id: str
    owner_id: str
    name: str
    logo_url: Optional[str] = None
    brand_color: str = "#6366F1"
    created_at: datetime

class TeamMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    member_id: str
    team_id: str
    user_id: str
    email: str
    name: str
    role: str  # owner, admin, editor, viewer
    status: str = "pending"  # pending, active
    invited_at: datetime
    joined_at: Optional[datetime] = None

# White-label Settings
class WhiteLabelSettings(BaseModel):
    logo_url: Optional[str] = None
    brand_color: str = "#6366F1"
    company_name: Optional[str] = None

# Instagram Account Models
class InstagramAccountCreate(BaseModel):
    username: str
    niche: str
    notes: Optional[str] = None

class InstagramAccountUpdate(BaseModel):
    username: Optional[str] = None
    niche: Optional[str] = None
    notes: Optional[str] = None

class InstagramAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    account_id: str
    user_id: str
    team_id: Optional[str] = None
    username: str
    niche: str
    notes: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    estimated_reach: Optional[int] = None
    posting_frequency: Optional[str] = None
    best_posting_time: Optional[str] = None
    last_audit_date: Optional[datetime] = None
    status: str = "active"
    created_at: datetime

# Audit Models
class AuditRequest(BaseModel):
    account_id: str

class Audit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    audit_id: str
    account_id: str
    user_id: str
    username: str
    engagement_score: int
    shadowban_risk: str
    content_consistency: int
    estimated_followers: Optional[int] = None
    estimated_engagement_rate: Optional[float] = None
    growth_mistakes: List[str]
    recommendations: List[str]
    roadmap: Dict[str, Any]
    created_at: datetime

# Content Models
class ContentRequest(BaseModel):
    account_id: str
    content_type: str
    niche: Optional[str] = None
    topic: Optional[str] = None

class ContentItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    content_id: str
    account_id: str
    user_id: str
    content_type: str
    content: List[str]
    created_at: datetime

# Growth Plan Models
class GrowthPlanRequest(BaseModel):
    account_id: str
    duration: int
    niche: Optional[str] = None

class GrowthPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    plan_id: str
    account_id: str
    user_id: str
    duration: int
    daily_tasks: List[Dict[str, Any]]
    created_at: datetime

# Payment Models
class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    transaction_id: str
    user_id: str
    session_id: str
    plan_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str, expires_days: int = 7) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def create_verification_token() -> str:
    return secrets.token_urlsafe(32)

async def send_email(to_email: str, subject: str, html_content: str):
    """Send email using Resend"""
    if not RESEND_API_KEY or RESEND_API_KEY == "re_placeholder_key":
        logger.warning(f"Email not sent (no API key): {subject} to {to_email}")
        return {"status": "skipped", "message": "Email service not configured"}
    
    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {"status": "success", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {"status": "error", "message": str(e)}

async def get_current_user(request: Request) -> User:
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

async def get_user_with_team_access(request: Request) -> tuple:
    """Get user and check team access for shared accounts"""
    user = await get_current_user(request)
    team_ids = [user.team_id] if user.team_id else []
    
    # Get teams where user is a member
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0, "team_id": 1}
    ).to_list(100)
    team_ids.extend([m["team_id"] for m in member_teams])
    
    return user, list(set(team_ids))

async def check_account_limit(user: User):
    count = await db.instagram_accounts.count_documents({"user_id": user.user_id})
    if count >= user.account_limit:
        raise HTTPException(status_code=403, detail=f"Account limit reached ({user.account_limit}). Upgrade your plan.")

async def check_ai_usage(user: User):
    if user.ai_usage_current >= user.ai_usage_limit:
        raise HTTPException(status_code=403, detail=f"AI usage limit reached ({user.ai_usage_limit}). Upgrade your plan.")

async def increment_ai_usage(user_id: str):
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"ai_usage_current": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

# ==================== AI FUNCTIONS ====================

async def generate_ai_content(prompt: str, system_message: str) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"instagrowth_{uuid.uuid4().hex[:8]}",
        system_message=system_message
    ).with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=prompt)
    response = await chat.send_message(user_message)
    return response

async def estimate_instagram_metrics(username: str, niche: str) -> Dict[str, Any]:
    """Use AI to estimate Instagram metrics based on username and niche"""
    system_message = """You are an Instagram analytics expert. Based on the username and niche, 
    provide realistic estimates for Instagram account metrics. Return JSON with:
    - estimated_followers (int, based on typical accounts in this niche)
    - estimated_engagement_rate (float, 1-10%)
    - estimated_reach (int, typical reach per post)
    - posting_frequency (string, e.g., "daily", "3x per week")
    - best_posting_time (string, e.g., "9 AM - 12 PM EST")
    - growth_potential (string: low/medium/high)
    Be realistic and base estimates on typical performance in the niche."""
    
    prompt = f"""Estimate Instagram metrics for:
    Username: @{username}
    Niche: {niche}
    
    Provide realistic estimates based on typical accounts in this niche."""
    
    try:
        response = await generate_ai_content(prompt, system_message)
        import json
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"AI metrics estimation error: {e}")
        return {
            "estimated_followers": 5000,
            "estimated_engagement_rate": 3.5,
            "estimated_reach": 2000,
            "posting_frequency": "3x per week",
            "best_posting_time": "9 AM - 12 PM",
            "growth_potential": "medium"
        }

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(data: UserCreate, request: Request):
    existing = await db.users.find_one({"email": data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    verification_token = create_verification_token()
    
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
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    await db.users.insert_one(user_doc)
    
    # Send verification email
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    verify_url = f"{origin}/verify-email?token={verification_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Welcome to InstaGrowth OS!</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; color: #333;">Hi {data.name},</p>
            <p style="font-size: 16px; color: #333;">Please verify your email address to get started:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Verify Email</a>
            </div>
            <p style="font-size: 14px; color: #666;">Or copy this link: {verify_url}</p>
            <p style="font-size: 14px; color: #666;">This link expires in 24 hours.</p>
        </div>
    </div>
    """
    await send_email(data.email, "Verify your InstaGrowth OS account", email_html)
    
    token = create_token(user_id, data.email)
    return {"token": token, "user": UserResponse(**user_doc), "message": "Please check your email to verify your account"}

@api_router.post("/auth/verify-email")
async def verify_email(token: str):
    user_doc = await db.users.find_one({"verification_token": token}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    await db.users.update_one(
        {"verification_token": token},
        {"$set": {"email_verified": True, "verification_token": None, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Email verified successfully"}

@api_router.post("/auth/resend-verification")
async def resend_verification(request: Request, user: User = Depends(get_current_user)):
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    verification_token = create_verification_token()
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"verification_token": verification_token}}
    )
    
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    verify_url = f"{origin}/verify-email?token={verification_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Verify Your Email</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; color: #333;">Hi {user.name},</p>
            <p style="font-size: 16px; color: #333;">Click below to verify your email:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Verify Email</a>
            </div>
        </div>
    </div>
    """
    await send_email(user.email, "Verify your InstaGrowth OS account", email_html)
    
    return {"message": "Verification email sent"}

@api_router.post("/auth/forgot-password")
async def forgot_password(data: PasswordResetRequest, request: Request):
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        # Don't reveal if email exists
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
    
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    reset_url = f"{origin}/reset-password?token={reset_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Reset Your Password</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; color: #333;">Hi {user_doc['name']},</p>
            <p style="font-size: 16px; color: #333;">You requested a password reset. Click below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Reset Password</a>
            </div>
            <p style="font-size: 14px; color: #666;">This link expires in 1 hour.</p>
            <p style="font-size: 14px; color: #666;">If you didn't request this, please ignore this email.</p>
        </div>
    </div>
    """
    await send_email(data.email, "Reset your InstaGrowth OS password", email_html)
    
    return {"message": "If this email exists, a password reset link will be sent"}

@api_router.post("/auth/reset-password")
async def reset_password(data: PasswordResetConfirm):
    reset_doc = await db.password_resets.find_one(
        {"token": data.token, "used": False},
        {"_id": 0}
    )
    if not reset_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = datetime.fromisoformat(reset_doc["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    await db.users.update_one(
        {"user_id": reset_doc["user_id"]},
        {"$set": {"password_hash": hash_password(data.new_password), "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Mark token as used
    await db.password_resets.update_one(
        {"token": data.token},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password reset successfully"}

@api_router.post("/auth/login")
async def login(data: UserLogin, response: Response):
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user_doc["user_id"], data.email)
    
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {"token": token, "user": UserResponse(**user_doc)}

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
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
            "user_id": user_id,
            "email": auth_data["email"],
            "name": auth_data["name"],
            "picture": auth_data.get("picture"),
            "password_hash": None,
            "role": "starter",
            "plan_id": None,
            "account_limit": 1,
            "ai_usage_limit": 10,
            "ai_usage_current": 0,
            "email_verified": True,  # Google OAuth emails are verified
            "team_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
        await db.users.insert_one(user_doc)
    else:
        user_id = user_doc["user_id"]
        if auth_data.get("picture") != user_doc.get("picture"):
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"picture": auth_data.get("picture"), "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            user_doc["picture"] = auth_data.get("picture")
    
    session_token = auth_data["session_token"]
    session_doc = {
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {"user": UserResponse(**user_doc)}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(**user.model_dump())

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}

# ==================== TEAM MANAGEMENT ROUTES ====================

@api_router.post("/teams")
async def create_team(data: TeamCreate, user: User = Depends(get_current_user)):
    # Only agency and enterprise can create teams
    if user.role not in ["agency", "enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Team management requires Agency plan or higher")
    
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    team_doc = {
        "team_id": team_id,
        "owner_id": user.user_id,
        "name": data.name,
        "logo_url": None,
        "brand_color": "#6366F1",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.insert_one(team_doc)
    
    # Add owner as team member
    member_doc = {
        "member_id": f"member_{uuid.uuid4().hex[:12]}",
        "team_id": team_id,
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "role": "owner",
        "status": "active",
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.team_members.insert_one(member_doc)
    
    # Update user's team_id
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"team_id": team_id, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return Team(**team_doc)

@api_router.get("/teams")
async def get_user_teams(user: User = Depends(get_current_user)):
    # Get teams where user is owner or member
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    ).to_list(100)
    
    team_ids = [m["team_id"] for m in member_teams]
    teams = await db.teams.find({"team_id": {"$in": team_ids}}, {"_id": 0}).to_list(100)
    
    return teams

@api_router.get("/teams/{team_id}")
async def get_team(team_id: str, user: User = Depends(get_current_user)):
    # Check user has access
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team

@api_router.post("/teams/{team_id}/invite")
async def invite_team_member(team_id: str, data: TeamInvite, request: Request, user: User = Depends(get_current_user)):
    # Check user is owner or admin
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can invite members")
    
    # Check if already invited
    existing = await db.team_members.find_one(
        {"team_id": team_id, "email": data.email},
        {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already invited to this team")
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    
    invite_token = create_verification_token()
    member_doc = {
        "member_id": f"member_{uuid.uuid4().hex[:12]}",
        "team_id": team_id,
        "user_id": None,  # Will be set when user accepts
        "email": data.email,
        "name": "",
        "role": data.role,
        "status": "pending",
        "invite_token": invite_token,
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "joined_at": None
    }
    await db.team_members.insert_one(member_doc)
    
    # Send invitation email
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    invite_url = f"{origin}/accept-invite?token={invite_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Team Invitation</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; color: #333;">You've been invited to join <strong>{team['name']}</strong> on InstaGrowth OS!</p>
            <p style="font-size: 16px; color: #333;">Invited by: {user.name}</p>
            <p style="font-size: 16px; color: #333;">Your role: {data.role.capitalize()}</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{invite_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Accept Invitation</a>
            </div>
        </div>
    </div>
    """
    await send_email(data.email, f"You're invited to join {team['name']} on InstaGrowth OS", email_html)
    
    return {"message": "Invitation sent", "member_id": member_doc["member_id"]}

@api_router.post("/teams/accept-invite")
async def accept_invite(token: str, user: User = Depends(get_current_user)):
    invite = await db.team_members.find_one(
        {"invite_token": token, "status": "pending"},
        {"_id": 0}
    )
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    if invite["email"] != user.email:
        raise HTTPException(status_code=403, detail="This invitation was sent to a different email")
    
    # Update member
    await db.team_members.update_one(
        {"invite_token": token},
        {"$set": {
            "user_id": user.user_id,
            "name": user.name,
            "status": "active",
            "invite_token": None,
            "joined_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update user's team_id if not set
    if not user.team_id:
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"team_id": invite["team_id"], "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    return {"message": "Invitation accepted", "team_id": invite["team_id"]}

@api_router.get("/teams/{team_id}/members")
async def get_team_members(team_id: str, user: User = Depends(get_current_user)):
    # Check user has access
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    return members

@api_router.put("/teams/{team_id}/members/{member_id}")
async def update_team_member(team_id: str, member_id: str, data: TeamMemberUpdate, user: User = Depends(get_current_user)):
    # Check user is owner or admin
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can update members")
    
    # Can't change owner role
    target_member = await db.team_members.find_one({"member_id": member_id}, {"_id": 0})
    if target_member and target_member["role"] == "owner":
        raise HTTPException(status_code=400, detail="Cannot change owner's role")
    
    await db.team_members.update_one(
        {"member_id": member_id, "team_id": team_id},
        {"$set": {"role": data.role}}
    )
    
    return {"message": "Member updated"}

@api_router.delete("/teams/{team_id}/members/{member_id}")
async def remove_team_member(team_id: str, member_id: str, user: User = Depends(get_current_user)):
    # Check user is owner or admin
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can remove members")
    
    # Can't remove owner
    target_member = await db.team_members.find_one({"member_id": member_id}, {"_id": 0})
    if target_member and target_member["role"] == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    await db.team_members.delete_one({"member_id": member_id, "team_id": team_id})
    
    return {"message": "Member removed"}

@api_router.put("/teams/{team_id}/settings")
async def update_team_settings(team_id: str, data: WhiteLabelSettings, user: User = Depends(get_current_user)):
    # Check user is owner
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": "owner", "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owner can update settings")
    
    update_data = {}
    if data.logo_url is not None:
        update_data["logo_url"] = data.logo_url
    if data.brand_color:
        update_data["brand_color"] = data.brand_color
    if data.company_name:
        update_data["name"] = data.company_name
    
    if update_data:
        await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    return team

@api_router.post("/teams/{team_id}/logo")
async def upload_team_logo(team_id: str, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    # Check user is owner
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": "owner", "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owner can upload logo")
    
    # Read and encode logo as base64
    contents = await file.read()
    logo_b64 = base64.b64encode(contents).decode()
    logo_url = f"data:{file.content_type};base64,{logo_b64}"
    
    await db.teams.update_one({"team_id": team_id}, {"$set": {"logo_url": logo_url}})
    
    return {"logo_url": logo_url}

# ==================== INSTAGRAM ACCOUNTS ROUTES ====================

@api_router.post("/accounts", response_model=InstagramAccount)
async def create_account(data: InstagramAccountCreate, user: User = Depends(get_current_user)):
    await check_account_limit(user)
    
    # Get AI-estimated metrics
    metrics = await estimate_instagram_metrics(data.username, data.niche)
    
    account_id = f"acc_{uuid.uuid4().hex[:12]}"
    account_doc = {
        "account_id": account_id,
        "user_id": user.user_id,
        "team_id": user.team_id,
        "username": data.username,
        "niche": data.niche,
        "notes": data.notes,
        "follower_count": metrics.get("estimated_followers"),
        "engagement_rate": metrics.get("estimated_engagement_rate"),
        "estimated_reach": metrics.get("estimated_reach"),
        "posting_frequency": metrics.get("posting_frequency"),
        "best_posting_time": metrics.get("best_posting_time"),
        "last_audit_date": None,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.instagram_accounts.insert_one(account_doc)
    return InstagramAccount(**account_doc)

@api_router.get("/accounts", response_model=List[InstagramAccount])
async def get_accounts(request: Request):
    user, team_ids = await get_user_with_team_access(request)
    
    # Get user's own accounts and team accounts
    query = {"$or": [{"user_id": user.user_id}]}
    if team_ids:
        query["$or"].append({"team_id": {"$in": team_ids}})
    
    accounts = await db.instagram_accounts.find(query, {"_id": 0}).to_list(100)
    return [InstagramAccount(**acc) for acc in accounts]

@api_router.get("/accounts/{account_id}", response_model=InstagramAccount)
async def get_account(account_id: str, request: Request):
    user, team_ids = await get_user_with_team_access(request)
    
    query = {"account_id": account_id, "$or": [{"user_id": user.user_id}]}
    if team_ids:
        query["$or"].append({"team_id": {"$in": team_ids}})
    
    account = await db.instagram_accounts.find_one(query, {"_id": 0})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return InstagramAccount(**account)

@api_router.put("/accounts/{account_id}", response_model=InstagramAccount)
async def update_account(account_id: str, data: InstagramAccountUpdate, user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.instagram_accounts.update_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = await db.instagram_accounts.find_one({"account_id": account_id}, {"_id": 0})
    return InstagramAccount(**account)

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str, user: User = Depends(get_current_user)):
    result = await db.instagram_accounts.delete_one(
        {"account_id": account_id, "user_id": user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}

@api_router.post("/accounts/{account_id}/refresh-metrics")
async def refresh_account_metrics(account_id: str, user: User = Depends(get_current_user)):
    """Refresh AI-estimated metrics for an account"""
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    await check_ai_usage(user)
    
    metrics = await estimate_instagram_metrics(account["username"], account["niche"])
    
    await db.instagram_accounts.update_one(
        {"account_id": account_id},
        {"$set": {
            "follower_count": metrics.get("estimated_followers"),
            "engagement_rate": metrics.get("estimated_engagement_rate"),
            "estimated_reach": metrics.get("estimated_reach"),
            "posting_frequency": metrics.get("posting_frequency"),
            "best_posting_time": metrics.get("best_posting_time")
        }}
    )
    
    await increment_ai_usage(user.user_id)
    
    return metrics

# ==================== AI AUDIT ROUTES ====================

@api_router.post("/audits", response_model=Audit)
async def create_audit(data: AuditRequest, user: User = Depends(get_current_user)):
    await check_ai_usage(user)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    system_message = """You are an Instagram growth expert analyzing accounts. 
    Provide detailed, actionable analysis in JSON format with these exact keys:
    - engagement_score (0-100)
    - shadowban_risk (low/medium/high)
    - content_consistency (0-100)
    - estimated_followers (int)
    - estimated_engagement_rate (float, percentage)
    - growth_mistakes (array of 3-5 specific mistakes)
    - recommendations (array of 5-7 actionable recommendations)
    - roadmap (object with week1, week2, week3, week4 arrays of daily tasks)
    Be specific and professional. Response must be valid JSON only."""
    
    prompt = f"""Analyze this Instagram account:
    Username: @{account['username']}
    Niche: {account['niche']}
    Notes: {account.get('notes', 'No additional notes')}
    Current estimated followers: {account.get('follower_count', 'Unknown')}
    
    Generate a comprehensive audit with engagement score, shadowban risk assessment, 
    content consistency rating, common growth mistakes, and a 30-day recovery roadmap."""
    
    try:
        ai_response = await generate_ai_content(prompt, system_message)
        import json
        cleaned = ai_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        audit_data = json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"AI Error: {e}")
        audit_data = {
            "engagement_score": 65,
            "shadowban_risk": "medium",
            "content_consistency": 70,
            "estimated_followers": account.get("follower_count", 5000),
            "estimated_engagement_rate": account.get("engagement_rate", 3.5),
            "growth_mistakes": [
                "Inconsistent posting schedule",
                "Not using trending audio in Reels",
                "Weak call-to-actions in captions",
                "Missing engagement in first 30 minutes"
            ],
            "recommendations": [
                "Post consistently at peak hours (9AM, 12PM, 6PM)",
                "Use trending audio in first 3 seconds of Reels",
                "Add strong CTAs asking for saves and shares",
                "Engage with similar accounts 30 min before posting",
                "Use 20-30 relevant hashtags per post"
            ],
            "roadmap": {
                "week1": ["Audit existing content", "Create content calendar", "Research trending audio"],
                "week2": ["Post 5 Reels", "Engage 30min daily", "Optimize bio"],
                "week3": ["Analyze best performing content", "Double down on winners", "Test new formats"],
                "week4": ["Review analytics", "Refine strategy", "Plan next month"]
            }
        }
    
    await increment_ai_usage(user.user_id)
    
    audit_id = f"audit_{uuid.uuid4().hex[:12]}"
    audit_doc = {
        "audit_id": audit_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "username": account["username"],
        "engagement_score": audit_data.get("engagement_score", 0),
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

@api_router.get("/audits", response_model=List[Audit])
async def get_audits(account_id: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    audits = await db.audits.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [Audit(**a) for a in audits]

@api_router.get("/audits/{audit_id}", response_model=Audit)
async def get_audit(audit_id: str, user: User = Depends(get_current_user)):
    audit = await db.audits.find_one(
        {"audit_id": audit_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return Audit(**audit)

@api_router.get("/audits/{audit_id}/pdf")
async def get_audit_pdf(audit_id: str, user: User = Depends(get_current_user)):
    audit = await db.audits.find_one(
        {"audit_id": audit_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    # Get white-label settings if user has a team
    team = None
    if user.team_id:
        team = await db.teams.find_one({"team_id": user.team_id}, {"_id": 0})
    
    brand_color = team.get("brand_color", "#6366F1") if team else "#6366F1"
    company_name = team.get("name", "InstaGrowth OS") if team else "InstaGrowth OS"
    logo_url = team.get("logo_url") if team else None
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header with brand color
    p.setFillColor(HexColor(brand_color))
    p.rect(0, height - 100, width, 100, fill=True)
    
    # Logo if available
    if logo_url and logo_url.startswith("data:"):
        try:
            logo_data = logo_url.split(",")[1]
            logo_bytes = base64.b64decode(logo_data)
            logo_img = ImageReader(BytesIO(logo_bytes))
            p.drawImage(logo_img, 30, height - 80, width=50, height=50, preserveAspectRatio=True)
        except Exception as e:
            logger.warning(f"Failed to load logo: {e}")
    
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100 if logo_url else 50, height - 55, f"{company_name} - Account Audit Report")
    
    # Account info
    y = height - 140
    p.setFillColor(HexColor("#000000"))
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"@{audit['username']}")
    y -= 30
    
    # Scores
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Engagement Score: {audit['engagement_score']}/100")
    y -= 20
    p.drawString(50, y, f"Shadowban Risk: {audit['shadowban_risk'].upper()}")
    y -= 20
    p.drawString(50, y, f"Content Consistency: {audit['content_consistency']}/100")
    if audit.get('estimated_followers'):
        y -= 20
        p.drawString(50, y, f"Estimated Followers: {audit['estimated_followers']:,}")
    if audit.get('estimated_engagement_rate'):
        y -= 20
        p.drawString(50, y, f"Estimated Engagement Rate: {audit['estimated_engagement_rate']:.1f}%")
    y -= 40
    
    # Mistakes
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Growth Mistakes:")
    y -= 20
    p.setFont("Helvetica", 11)
    for mistake in audit.get('growth_mistakes', [])[:5]:
        p.drawString(60, y, f"• {mistake[:80]}")
        y -= 18
    y -= 20
    
    # Recommendations
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Recommendations:")
    y -= 20
    p.setFont("Helvetica", 11)
    for rec in audit.get('recommendations', [])[:7]:
        p.drawString(60, y, f"• {rec[:80]}")
        y -= 18
    
    # Footer
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#666666"))
    p.drawString(50, 30, f"Generated by {company_name} | {datetime.now().strftime('%Y-%m-%d')}")
    
    p.save()
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=audit_{audit['username']}_{audit_id}.pdf"}
    )

# ==================== CONTENT ENGINE ROUTES ====================

@api_router.post("/content/generate", response_model=ContentItem)
async def generate_content(data: ContentRequest, user: User = Depends(get_current_user)):
    await check_ai_usage(user)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    niche = data.niche or account.get("niche", "general")
    topic = data.topic or "trending topics"
    
    prompts = {
        "reels": f"Generate 5 viral Instagram Reel ideas for the {niche} niche about {topic}. Each idea should have: title, concept, hook, and trending audio suggestion. Return as JSON array.",
        "hooks": f"Generate 7 scroll-stopping hooks (first 3 seconds scripts) for Instagram Reels in the {niche} niche about {topic}. These should grab attention immediately. Return as JSON array of strings.",
        "captions": f"Generate 5 engaging Instagram captions for the {niche} niche about {topic}. Include emojis, call-to-actions, and encourage saves/shares. Return as JSON array of strings.",
        "hashtags": f"Generate 30 relevant Instagram hashtags for the {niche} niche about {topic}. Mix of high, medium, and low competition. Return as JSON array of strings."
    }
    
    system_message = """You are an Instagram content strategist. Generate viral, engaging content.
    Return ONLY a valid JSON array of items. No explanations, just the JSON array."""
    
    prompt = prompts.get(data.content_type, prompts["captions"])
    
    try:
        ai_response = await generate_ai_content(prompt, system_message)
        import json
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
    except Exception as e:
        logger.error(f"AI Content Error: {e}")
        fallback = {
            "reels": ["Day in the life Reel", "Behind the scenes", "Tutorial style", "Before/After transformation", "Trending audio dance"],
            "hooks": ["Wait until you see this...", "POV: You just discovered...", "This changed everything for me", "Stop scrolling if you...", "The secret nobody tells you about..."],
            "captions": ["Ready to level up? Here's how... 🚀", "Save this for later! 📌", "Comment YES if you agree! 💬", "Tag someone who needs to see this 👇", "Double tap if this resonates ❤️"],
            "hashtags": ["#instagramgrowth", "#contentcreator", "#reelsinstagram", "#viralreels", "#growthhacks", "#socialmedia", "#instagramtips"]
        }
        content_list = fallback.get(data.content_type, fallback["captions"])
    
    await increment_ai_usage(user.user_id)
    
    content_id = f"content_{uuid.uuid4().hex[:12]}"
    content_doc = {
        "content_id": content_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "content_type": data.content_type,
        "content": content_list,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.content_items.insert_one(content_doc)
    
    return ContentItem(**content_doc)

@api_router.get("/content", response_model=List[ContentItem])
async def get_content(account_id: Optional[str] = None, content_type: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    if content_type:
        query["content_type"] = content_type
    
    items = await db.content_items.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [ContentItem(**item) for item in items]

# ==================== GROWTH PLANNER ROUTES ====================

@api_router.post("/growth-plans", response_model=GrowthPlan)
async def create_growth_plan(data: GrowthPlanRequest, user: User = Depends(get_current_user)):
    await check_ai_usage(user)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    niche = data.niche or account.get("niche", "general")
    
    system_message = """You are an Instagram growth strategist. Create actionable daily plans.
    Return a JSON object with 'daily_tasks' array. Each task has: day (1-30), title, description, type (post/engage/analyze/learn), and priority (high/medium/low).
    Focus on consistency, engagement, and content quality."""
    
    prompt = f"""Create a {data.duration}-day Instagram growth plan for the {niche} niche.
    Include daily tasks for:
    - Content creation and posting
    - Engagement activities
    - Analytics review
    - Strategy refinement
    
    Make it actionable and specific to the {niche} niche."""
    
    try:
        ai_response = await generate_ai_content(prompt, system_message)
        import json
        cleaned = ai_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        plan_data = json.loads(cleaned.strip())
        daily_tasks = plan_data.get("daily_tasks", [])
    except Exception as e:
        logger.error(f"AI Plan Error: {e}")
        daily_tasks = []
        for day in range(1, data.duration + 1):
            task_type = ["post", "engage", "analyze", "learn"][day % 4]
            daily_tasks.append({
                "day": day,
                "title": f"Day {day}: {task_type.capitalize()} Focus",
                "description": f"Focus on {task_type} activities for your {niche} account",
                "type": task_type,
                "priority": "high" if day <= 7 else "medium"
            })
    
    await increment_ai_usage(user.user_id)
    
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    plan_doc = {
        "plan_id": plan_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "duration": data.duration,
        "daily_tasks": daily_tasks,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.growth_plans.insert_one(plan_doc)
    
    return GrowthPlan(**plan_doc)

@api_router.get("/growth-plans", response_model=List[GrowthPlan])
async def get_growth_plans(account_id: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    plans = await db.growth_plans.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [GrowthPlan(**p) for p in plans]

@api_router.get("/growth-plans/{plan_id}", response_model=GrowthPlan)
async def get_growth_plan(plan_id: str, user: User = Depends(get_current_user)):
    plan = await db.growth_plans.find_one(
        {"plan_id": plan_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return GrowthPlan(**plan)

@api_router.get("/growth-plans/{plan_id}/pdf")
async def get_growth_plan_pdf(plan_id: str, user: User = Depends(get_current_user)):
    plan = await db.growth_plans.find_one(
        {"plan_id": plan_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    # Get white-label settings
    team = None
    if user.team_id:
        team = await db.teams.find_one({"team_id": user.team_id}, {"_id": 0})
    
    brand_color = team.get("brand_color", "#6366F1") if team else "#6366F1"
    company_name = team.get("name", "InstaGrowth OS") if team else "InstaGrowth OS"
    logo_url = team.get("logo_url") if team else None
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
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
    p.drawString(100 if logo_url else 50, height - 55, f"{plan['duration']}-Day Growth Plan")
    
    y = height - 140
    p.setFillColor(HexColor("#000000"))
    
    for task in plan.get("daily_tasks", [])[:15]:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"Day {task.get('day', '?')}: {task.get('title', 'Task')[:50]}")
        y -= 15
        p.setFont("Helvetica", 10)
        desc = task.get('description', '')[:100]
        p.drawString(60, y, desc)
        y -= 25
        
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

# ==================== SUBSCRIPTION & PAYMENT ROUTES ====================

SUBSCRIPTION_PLANS = {
    "starter": {"name": "Starter", "price": 19.0, "account_limit": 1, "ai_usage_limit": 10, "features": ["1 Instagram account", "Limited AI usage", "Basic audit reports"]},
    "pro": {"name": "Pro", "price": 49.0, "account_limit": 5, "ai_usage_limit": 100, "features": ["5 Instagram accounts", "Full AI access", "PDF exports", "Growth planner"]},
    "agency": {"name": "Agency", "price": 149.0, "account_limit": 25, "ai_usage_limit": 500, "features": ["25 Instagram accounts", "White-label PDFs", "Team access", "Priority support"]},
    "enterprise": {"name": "Enterprise", "price": 299.0, "account_limit": 100, "ai_usage_limit": 2000, "features": ["100 Instagram accounts", "API access", "Custom branding", "Dedicated support"]}
}

@api_router.get("/plans")
async def get_plans():
    plans = []
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        plans.append({"plan_id": plan_id, **plan})
    return plans

@api_router.post("/checkout/session")
async def create_checkout_session(request: Request, user: User = Depends(get_current_user)):
    data = await request.json()
    plan_id = data.get("plan_id")
    origin_url = data.get("origin_url")
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/billing?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/billing"
    
    checkout_request = CheckoutSessionRequest(
        amount=plan["price"],
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user.user_id,
            "plan_id": plan_id,
            "plan_name": plan["name"]
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    transaction_doc = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "session_id": session.session_id,
        "plan_id": plan_id,
        "amount": plan["price"],
        "currency": "usd",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    await db.payment_transactions.insert_one(transaction_doc)
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, user: User = Depends(get_current_user)):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    status = await stripe_checkout.get_checkout_status(session_id)
    
    if status.payment_status == "paid":
        txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        if txn and txn.get("status") != "completed":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            plan_id = txn.get("plan_id")
            if plan_id in SUBSCRIPTION_PLANS:
                plan = SUBSCRIPTION_PLANS[plan_id]
                await db.users.update_one(
                    {"user_id": user.user_id},
                    {"$set": {
                        "role": plan_id,
                        "plan_id": plan_id,
                        "account_limit": plan["account_limit"],
                        "ai_usage_limit": plan["ai_usage_limit"],
                        "ai_usage_current": 0,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
            
            if txn and txn.get("status") != "completed":
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                user_id = txn.get("user_id")
                plan_id = txn.get("plan_id")
                
                if plan_id in SUBSCRIPTION_PLANS:
                    plan = SUBSCRIPTION_PLANS[plan_id]
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "role": plan_id,
                            "plan_id": plan_id,
                            "account_limit": plan["account_limit"],
                            "ai_usage_limit": plan["ai_usage_limit"],
                            "ai_usage_current": 0,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# ==================== ADMIN ROUTES ====================

async def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@api_router.get("/admin/users")
async def admin_get_users(admin: User = Depends(require_admin)):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users

@api_router.get("/admin/stats")
async def admin_get_stats(admin: User = Depends(require_admin)):
    total_users = await db.users.count_documents({})
    total_accounts = await db.instagram_accounts.count_documents({})
    total_audits = await db.audits.count_documents({})
    total_teams = await db.teams.count_documents({})
    total_revenue = await db.payment_transactions.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_audits": total_audits,
        "total_teams": total_teams,
        "total_revenue": total_revenue[0]["total"] if total_revenue else 0,
        "users_by_plan": await db.users.aggregate([
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]).to_list(10)
    }

@api_router.put("/admin/users/{user_id}/role")
async def admin_update_user_role(user_id: str, role: str, admin: User = Depends(require_admin)):
    if role not in ["starter", "pro", "agency", "enterprise", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    plan = SUBSCRIPTION_PLANS.get(role, {"account_limit": 1, "ai_usage_limit": 10})
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {
            "role": role,
            "plan_id": role if role != "admin" else None,
            "account_limit": plan.get("account_limit", 1),
            "ai_usage_limit": plan.get("ai_usage_limit", 10),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User role updated"}

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: User = Depends(get_current_user)):
    accounts = await db.instagram_accounts.count_documents({"user_id": user.user_id})
    audits = await db.audits.count_documents({"user_id": user.user_id})
    content_items = await db.content_items.count_documents({"user_id": user.user_id})
    growth_plans = await db.growth_plans.count_documents({"user_id": user.user_id})
    
    recent_audits = await db.audits.find(
        {"user_id": user.user_id},
        {"_id": 0, "engagement_score": 1, "content_consistency": 1, "created_at": 1, "username": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "accounts_count": accounts,
        "audits_count": audits,
        "content_items_count": content_items,
        "growth_plans_count": growth_plans,
        "ai_usage": {"current": user.ai_usage_current, "limit": user.ai_usage_limit},
        "account_usage": {"current": accounts, "limit": user.account_limit},
        "recent_audits": recent_audits
    }

# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "InstaGrowth OS API", "version": "1.1.0"}

# Include the router
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
