from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, UploadFile, File
from fastapi.responses import StreamingResponse
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
from io import BytesIO, StringIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import base64
import asyncio
import resend
import secrets
from collections import defaultdict
import time

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

# Rate limiting storage
rate_limit_storage = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10  # max AI requests per minute

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
    extra_accounts: int = 0
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
    extra_accounts: int = 0

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
    role: str = "viewer"

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
    role: str
    status: str = "pending"
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
    client_name: Optional[str] = None
    client_email: Optional[str] = None

class InstagramAccountUpdate(BaseModel):
    username: Optional[str] = None
    niche: Optional[str] = None
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None

class InstagramAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    account_id: str
    user_id: str
    team_id: Optional[str] = None
    username: str
    niche: str
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
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
    is_favorite: bool = False
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

# DM Template Models
class DMTemplateCreate(BaseModel):
    name: str
    category: str  # welcome, sales, support, follow_up, lead_qualify
    message: str
    variables: Optional[List[str]] = None

class DMTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    template_id: str
    user_id: str
    name: str
    category: str
    message: str
    variables: List[str] = []
    use_count: int = 0
    created_at: datetime

# DM Reply Bot Models
class DMReplySettings(BaseModel):
    account_id: str
    enabled: bool = False
    welcome_template_id: Optional[str] = None
    lead_qualify_enabled: bool = False
    lead_questions: Optional[List[str]] = None
    auto_reply_delay_min: int = 30  # seconds
    auto_reply_delay_max: int = 120
    working_hours_start: int = 9  # 9 AM
    working_hours_end: int = 21  # 9 PM

class DMConversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    conversation_id: str
    account_id: str
    user_id: str
    contact_username: str
    is_lead: bool = False
    lead_score: int = 0
    messages: List[Dict[str, Any]] = []
    status: str = "active"  # active, qualified, not_qualified, converted
    created_at: datetime
    updated_at: Optional[datetime] = None

# Competitor Analysis Models
class CompetitorAnalysisRequest(BaseModel):
    account_id: str
    competitor_usernames: List[str]

class CompetitorAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    analysis_id: str
    account_id: str
    user_id: str
    competitors: List[Dict[str, Any]]
    insights: List[str]
    opportunities: List[str]
    created_at: datetime

# A/B Test Models
class ABTestCreate(BaseModel):
    account_id: str
    content_type: str  # hooks, captions
    variant_a: str
    variant_b: str

class ABTest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    test_id: str
    account_id: str
    user_id: str
    content_type: str
    variant_a: str
    variant_b: str
    votes_a: int = 0
    votes_b: int = 0
    winner: Optional[str] = None
    status: str = "active"  # active, completed
    created_at: datetime

# One-Time Product Models
class OneTimeProduct(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    type: str  # recovery_report, content_pack, audit_pdf

class ProductPurchase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    purchase_id: str
    user_id: str
    product_id: str
    amount: float
    status: str
    data: Optional[Dict[str, Any]] = None
    created_at: datetime

# Notification Models
class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str
    user_id: str
    type: str  # team_invite, plan_upgrade, ai_limit, system
    title: str
    message: str
    read: bool = False
    action_url: Optional[str] = None
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

def check_rate_limit(user_id: str) -> bool:
    """Check if user has exceeded rate limit for AI requests"""
    current_time = time.time()
    user_requests = rate_limit_storage[user_id]
    
    # Remove old requests outside the window
    rate_limit_storage[user_id] = [t for t in user_requests if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limit_storage[user_id]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    rate_limit_storage[user_id].append(current_time)
    return True

async def send_email(to_email: str, subject: str, html_content: str):
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

async def create_notification(user_id: str, type: str, title: str, message: str, action_url: Optional[str] = None):
    """Create a notification for a user"""
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
    user = await get_current_user(request)
    team_ids = [user.team_id] if user.team_id else []
    
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0, "team_id": 1}
    ).to_list(100)
    team_ids.extend([m["team_id"] for m in member_teams])
    
    return user, list(set(team_ids))

async def check_account_limit(user: User):
    count = await db.instagram_accounts.count_documents({"user_id": user.user_id})
    total_limit = user.account_limit + user.extra_accounts
    if count >= total_limit:
        raise HTTPException(status_code=403, detail=f"Account limit reached ({total_limit}). Upgrade your plan or purchase extra accounts.")

async def check_ai_usage(user: User):
    if user.ai_usage_current >= user.ai_usage_limit:
        raise HTTPException(status_code=403, detail=f"AI usage limit reached ({user.ai_usage_limit}). Upgrade your plan.")
    
    if not check_rate_limit(user.user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before making more AI requests.")

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
    system_message = """You are an Instagram analytics expert. Based on the username and niche, 
    provide realistic estimates for Instagram account metrics. Return JSON with:
    - estimated_followers (int)
    - estimated_engagement_rate (float, 1-10%)
    - estimated_reach (int)
    - posting_frequency (string)
    - best_posting_time (string with timezone)
    - growth_potential (string: low/medium/high)
    Be realistic based on typical performance in the niche."""
    
    prompt = f"Estimate Instagram metrics for @{username} in the {niche} niche."
    
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
            "best_posting_time": "9 AM - 12 PM EST",
            "growth_potential": "medium"
        }

async def generate_posting_recommendations(username: str, niche: str, current_metrics: Dict) -> Dict[str, Any]:
    """Generate AI-based posting time recommendations"""
    system_message = """You are an Instagram growth strategist. Analyze the account and provide 
    optimal posting time recommendations. Return JSON with:
    - best_times (array of {day: string, times: array of strings})
    - frequency (string, e.g., "5-7 posts per week")
    - content_mix (object with percentages for reels, posts, stories)
    - peak_engagement_windows (array of time ranges)
    - avoid_times (array of times to avoid posting)
    - reasoning (string explaining the recommendations)"""
    
    prompt = f"""Provide posting recommendations for:
    Username: @{username}
    Niche: {niche}
    Current followers: {current_metrics.get('estimated_followers', 'Unknown')}
    Current engagement: {current_metrics.get('estimated_engagement_rate', 'Unknown')}%"""
    
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
        logger.error(f"Posting recommendations error: {e}")
        return {
            "best_times": [
                {"day": "Monday", "times": ["9:00 AM", "12:00 PM", "6:00 PM"]},
                {"day": "Wednesday", "times": ["9:00 AM", "12:00 PM", "7:00 PM"]},
                {"day": "Friday", "times": ["10:00 AM", "2:00 PM", "8:00 PM"]}
            ],
            "frequency": "5-7 posts per week",
            "content_mix": {"reels": 60, "posts": 25, "stories": 15},
            "peak_engagement_windows": ["9-11 AM", "7-9 PM"],
            "avoid_times": ["2-5 AM", "During major events"],
            "reasoning": "Based on typical engagement patterns in your niche"
        }

async def generate_dm_reply(message: str, context: str, tone: str = "friendly") -> str:
    """Generate AI-powered DM reply"""
    system_message = f"""You are an Instagram account manager. Generate a {tone}, professional 
    DM reply. Keep it natural, avoid sounding robotic. Include appropriate emojis.
    Context: {context}
    Return ONLY the reply message, nothing else."""
    
    prompt = f"Generate a reply to this DM: \"{message}\""
    
    try:
        response = await generate_ai_content(prompt, system_message)
        return response.strip()
    except Exception as e:
        logger.error(f"DM reply generation error: {e}")
        return "Thanks for reaching out! I'll get back to you soon. 😊"

async def analyze_competitor(competitor_username: str, niche: str) -> Dict[str, Any]:
    """AI-based competitor analysis"""
    system_message = """You are an Instagram competitive analyst. Analyze the competitor and provide insights.
    Return JSON with:
    - estimated_followers (int)
    - estimated_engagement_rate (float)
    - content_strategy (string)
    - posting_frequency (string)
    - strengths (array of strings)
    - weaknesses (array of strings)
    - content_types (object with percentages)
    - hashtag_strategy (string)
    - audience_demographics (string)"""
    
    prompt = f"Analyze Instagram competitor @{competitor_username} in the {niche} niche."
    
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
        logger.error(f"Competitor analysis error: {e}")
        return {
            "estimated_followers": 10000,
            "estimated_engagement_rate": 4.0,
            "content_strategy": "Consistent posting with trending content",
            "posting_frequency": "Daily",
            "strengths": ["Strong visual brand", "Engaging captions"],
            "weaknesses": ["Limited story engagement", "Inconsistent reels"],
            "content_types": {"reels": 50, "posts": 30, "stories": 20},
            "hashtag_strategy": "Mix of branded and trending hashtags",
            "audience_demographics": "18-34 year olds interested in " + niche
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
        "extra_accounts": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    await db.users.insert_one(user_doc)
    
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
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
    
    # Create welcome notification
    await create_notification(
        user_id, "system", "Welcome to InstaGrowth OS!",
        "Start by adding your first Instagram account.", "/accounts"
    )
    
    token = create_token(user_id, data.email)
    return {"token": token, "user": UserResponse(**user_doc)}

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
            <p>Hi {user.name},</p>
            <p>Click below to verify your email:</p>
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

@api_router.post("/auth/reset-password")
async def reset_password(data: PasswordResetConfirm):
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
            "email_verified": True,
            "team_id": None,
            "extra_accounts": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
        await db.users.insert_one(user_doc)
        await create_notification(user_id, "system", "Welcome!", "Start by adding your Instagram account.", "/accounts")
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

# ==================== NOTIFICATION ROUTES ====================

@api_router.get("/notifications")
async def get_notifications(user: User = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    return notifications

@api_router.get("/notifications/unread-count")
async def get_unread_count(user: User = Depends(get_current_user)):
    count = await db.notifications.count_documents({"user_id": user.user_id, "read": False})
    return {"count": count}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user: User = Depends(get_current_user)):
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": user.user_id},
        {"$set": {"read": True}}
    )
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/read-all")
async def mark_all_read(user: User = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": user.user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}

# ==================== TEAM MANAGEMENT ROUTES ====================

@api_router.post("/teams")
async def create_team(data: TeamCreate, user: User = Depends(get_current_user)):
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
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"team_id": team_id, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return Team(**team_doc)

@api_router.get("/teams")
async def get_user_teams(user: User = Depends(get_current_user)):
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0}
    ).to_list(100)
    
    team_ids = [m["team_id"] for m in member_teams]
    teams = await db.teams.find({"team_id": {"$in": team_ids}}, {"_id": 0}).to_list(100)
    
    return teams

@api_router.get("/teams/{team_id}")
async def get_team(team_id: str, user: User = Depends(get_current_user)):
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
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can invite members")
    
    existing = await db.team_members.find_one({"team_id": team_id, "email": data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="User already invited to this team")
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    
    invite_token = create_verification_token()
    member_doc = {
        "member_id": f"member_{uuid.uuid4().hex[:12]}",
        "team_id": team_id,
        "user_id": None,
        "email": data.email,
        "name": "",
        "role": data.role,
        "status": "pending",
        "invite_token": invite_token,
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "joined_at": None
    }
    await db.team_members.insert_one(member_doc)
    
    # Create notification for invitee if they exist
    invitee = await db.users.find_one({"email": data.email}, {"_id": 0})
    if invitee:
        await create_notification(
            invitee["user_id"], "team_invite",
            f"Team Invitation from {team['name']}",
            f"{user.name} invited you to join their team as {data.role}.",
            f"/accept-invite?token={invite_token}"
        )
    
    origin = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    invite_url = f"{origin}/accept-invite?token={invite_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Team Invitation</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p>You've been invited to join <strong>{team['name']}</strong> on InstaGrowth OS!</p>
            <p>Invited by: {user.name}</p>
            <p>Your role: {data.role.capitalize()}</p>
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
    invite = await db.team_members.find_one({"invite_token": token, "status": "pending"}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    if invite["email"] != user.email:
        raise HTTPException(status_code=403, detail="This invitation was sent to a different email")
    
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
    
    if not user.team_id:
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"team_id": invite["team_id"], "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    return {"message": "Invitation accepted", "team_id": invite["team_id"]}

@api_router.get("/teams/{team_id}/members")
async def get_team_members(team_id: str, user: User = Depends(get_current_user)):
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
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can update members")
    
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
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can remove members")
    
    target_member = await db.team_members.find_one({"member_id": member_id}, {"_id": 0})
    if target_member and target_member["role"] == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    await db.team_members.delete_one({"member_id": member_id, "team_id": team_id})
    
    return {"message": "Member removed"}

@api_router.put("/teams/{team_id}/settings")
async def update_team_settings(team_id: str, data: WhiteLabelSettings, user: User = Depends(get_current_user)):
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
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": "owner", "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owner can upload logo")
    
    contents = await file.read()
    logo_b64 = base64.b64encode(contents).decode()
    logo_url = f"data:{file.content_type};base64,{logo_b64}"
    
    await db.teams.update_one({"team_id": team_id}, {"$set": {"logo_url": logo_url}})
    
    return {"logo_url": logo_url}

# ==================== INSTAGRAM ACCOUNTS ROUTES ====================

@api_router.post("/accounts", response_model=InstagramAccount)
async def create_account(data: InstagramAccountCreate, user: User = Depends(get_current_user)):
    await check_account_limit(user)
    
    metrics = await estimate_instagram_metrics(data.username, data.niche)
    
    account_id = f"acc_{uuid.uuid4().hex[:12]}"
    account_doc = {
        "account_id": account_id,
        "user_id": user.user_id,
        "team_id": user.team_id,
        "username": data.username,
        "niche": data.niche,
        "notes": data.notes,
        "client_name": data.client_name,
        "client_email": data.client_email,
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
    result = await db.instagram_accounts.delete_one({"account_id": account_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}

@api_router.post("/accounts/{account_id}/refresh-metrics")
async def refresh_account_metrics(account_id: str, user: User = Depends(get_current_user)):
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

@api_router.get("/accounts/{account_id}/posting-recommendations")
async def get_posting_recommendations(account_id: str, user: User = Depends(get_current_user)):
    """Get AI-powered posting time recommendations"""
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    await check_ai_usage(user)
    
    current_metrics = {
        "estimated_followers": account.get("follower_count"),
        "estimated_engagement_rate": account.get("engagement_rate")
    }
    
    recommendations = await generate_posting_recommendations(
        account["username"], account["niche"], current_metrics
    )
    
    await increment_ai_usage(user.user_id)
    
    return recommendations

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
                "Post consistently at peak hours",
                "Use trending audio in Reels",
                "Add strong CTAs for saves and shares",
                "Engage with similar accounts before posting",
                "Use 20-30 relevant hashtags"
            ],
            "roadmap": {
                "week1": ["Audit content", "Create calendar", "Research trends"],
                "week2": ["Post 5 Reels", "Engage daily", "Optimize bio"],
                "week3": ["Analyze performance", "Double down on winners"],
                "week4": ["Review analytics", "Plan next month"]
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
    audit = await db.audits.find_one({"audit_id": audit_id, "user_id": user.user_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return Audit(**audit)

@api_router.get("/audits/{audit_id}/pdf")
async def get_audit_pdf(audit_id: str, user: User = Depends(get_current_user)):
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
        "reels": f"Generate 5 viral Reel ideas for {niche} about {topic}. Include title, concept, hook, audio suggestion. Return JSON array.",
        "hooks": f"Generate 7 scroll-stopping hooks for {niche} about {topic}. Return JSON array of strings.",
        "captions": f"Generate 5 engaging captions for {niche} about {topic}. Include emojis, CTAs. Return JSON array of strings.",
        "hashtags": f"Generate 30 hashtags for {niche} about {topic}. Mix competition levels. Return JSON array of strings."
    }
    
    system_message = "You are an Instagram content strategist. Return ONLY valid JSON array."
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
            "reels": ["Day in the life", "Behind the scenes", "Tutorial", "Transformation", "Trending dance"],
            "hooks": ["Wait until you see...", "POV: You discovered...", "This changed everything", "Stop scrolling if...", "Secret nobody tells..."],
            "captions": ["Ready to level up? 🚀", "Save this! 📌", "Comment YES! 💬", "Tag someone 👇", "Double tap ❤️"],
            "hashtags": ["#instagramgrowth", "#contentcreator", "#reels", "#viral", "#growthhacks"]
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
        "is_favorite": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.content_items.insert_one(content_doc)
    
    return ContentItem(**content_doc)

@api_router.get("/content", response_model=List[ContentItem])
async def get_content(account_id: Optional[str] = None, content_type: Optional[str] = None, favorites_only: bool = False, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    if content_type:
        query["content_type"] = content_type
    if favorites_only:
        query["is_favorite"] = True
    
    items = await db.content_items.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [ContentItem(**item) for item in items]

@api_router.put("/content/{content_id}/favorite")
async def toggle_favorite(content_id: str, user: User = Depends(get_current_user)):
    """Toggle favorite status of content"""
    content = await db.content_items.find_one({"content_id": content_id, "user_id": user.user_id}, {"_id": 0})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    new_status = not content.get("is_favorite", False)
    await db.content_items.update_one(
        {"content_id": content_id},
        {"$set": {"is_favorite": new_status}}
    )
    
    return {"is_favorite": new_status}

# ==================== DM TEMPLATE ROUTES ====================

@api_router.post("/dm-templates", response_model=DMTemplate)
async def create_dm_template(data: DMTemplateCreate, user: User = Depends(get_current_user)):
    template_id = f"template_{uuid.uuid4().hex[:12]}"
    
    # Extract variables from message (e.g., {{name}}, {{product}})
    import re
    variables = re.findall(r'\{\{(\w+)\}\}', data.message)
    
    template_doc = {
        "template_id": template_id,
        "user_id": user.user_id,
        "name": data.name,
        "category": data.category,
        "message": data.message,
        "variables": variables or data.variables or [],
        "use_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.dm_templates.insert_one(template_doc)
    return DMTemplate(**template_doc)

@api_router.get("/dm-templates")
async def get_dm_templates(category: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if category:
        query["category"] = category
    
    templates = await db.dm_templates.find(query, {"_id": 0}).to_list(100)
    return templates

@api_router.put("/dm-templates/{template_id}")
async def update_dm_template(template_id: str, data: DMTemplateCreate, user: User = Depends(get_current_user)):
    import re
    variables = re.findall(r'\{\{(\w+)\}\}', data.message)
    
    result = await db.dm_templates.update_one(
        {"template_id": template_id, "user_id": user.user_id},
        {"$set": {
            "name": data.name,
            "category": data.category,
            "message": data.message,
            "variables": variables or data.variables or []
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template updated"}

@api_router.delete("/dm-templates/{template_id}")
async def delete_dm_template(template_id: str, user: User = Depends(get_current_user)):
    result = await db.dm_templates.delete_one({"template_id": template_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}

@api_router.post("/dm-templates/{template_id}/generate-reply")
async def generate_dm_reply_from_template(template_id: str, message: str, user: User = Depends(get_current_user)):
    """Generate AI-powered DM reply based on template"""
    await check_ai_usage(user)
    
    template = await db.dm_templates.find_one({"template_id": template_id, "user_id": user.user_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    context = f"Template category: {template['category']}. Base message style: {template['message'][:100]}"
    reply = await generate_dm_reply(message, context)
    
    # Increment template use count
    await db.dm_templates.update_one(
        {"template_id": template_id},
        {"$inc": {"use_count": 1}}
    )
    
    await increment_ai_usage(user.user_id)
    
    return {"reply": reply}

# ==================== COMPETITOR ANALYSIS ROUTES ====================

@api_router.post("/competitor-analysis")
async def create_competitor_analysis(data: CompetitorAnalysisRequest, user: User = Depends(get_current_user)):
    """Analyze competitors for an account"""
    await check_ai_usage(user)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Analyze each competitor
    competitors_data = []
    for username in data.competitor_usernames[:5]:  # Limit to 5 competitors
        analysis = await analyze_competitor(username, account["niche"])
        analysis["username"] = username
        competitors_data.append(analysis)
    
    # Generate overall insights
    system_message = """Based on competitor analysis, provide strategic insights. Return JSON:
    - insights (array of 5 key observations)
    - opportunities (array of 3-5 growth opportunities)"""
    
    prompt = f"Summarize insights from these competitors: {competitors_data}"
    
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
        summary = json.loads(cleaned.strip())
    except:
        summary = {
            "insights": ["Competitors post consistently", "Reels perform best", "Engagement is key"],
            "opportunities": ["Underserved content topics", "Better hashtag strategy", "More story engagement"]
        }
    
    await increment_ai_usage(user.user_id)
    
    analysis_id = f"comp_{uuid.uuid4().hex[:12]}"
    analysis_doc = {
        "analysis_id": analysis_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "competitors": competitors_data,
        "insights": summary.get("insights", []),
        "opportunities": summary.get("opportunities", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.competitor_analyses.insert_one(analysis_doc)
    
    return CompetitorAnalysis(**analysis_doc)

@api_router.get("/competitor-analysis")
async def get_competitor_analyses(account_id: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    
    analyses = await db.competitor_analyses.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return analyses

# ==================== A/B TEST ROUTES ====================

@api_router.post("/ab-tests")
async def create_ab_test(data: ABTestCreate, user: User = Depends(get_current_user)):
    """Create an A/B test for content"""
    test_id = f"test_{uuid.uuid4().hex[:12]}"
    test_doc = {
        "test_id": test_id,
        "account_id": data.account_id,
        "user_id": user.user_id,
        "content_type": data.content_type,
        "variant_a": data.variant_a,
        "variant_b": data.variant_b,
        "votes_a": 0,
        "votes_b": 0,
        "winner": None,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ab_tests.insert_one(test_doc)
    return ABTest(**test_doc)

@api_router.get("/ab-tests")
async def get_ab_tests(account_id: Optional[str] = None, status: Optional[str] = None, user: User = Depends(get_current_user)):
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    if status:
        query["status"] = status
    
    tests = await db.ab_tests.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return tests

@api_router.post("/ab-tests/{test_id}/vote")
async def vote_ab_test(test_id: str, variant: str, user: User = Depends(get_current_user)):
    """Vote for a variant in A/B test"""
    if variant not in ["a", "b"]:
        raise HTTPException(status_code=400, detail="Invalid variant. Use 'a' or 'b'")
    
    test = await db.ab_tests.find_one({"test_id": test_id, "user_id": user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test["status"] != "active":
        raise HTTPException(status_code=400, detail="Test is no longer active")
    
    field = f"votes_{variant}"
    await db.ab_tests.update_one(
        {"test_id": test_id},
        {"$inc": {field: 1}}
    )
    
    # Check if we should determine winner (e.g., after 10 total votes)
    updated = await db.ab_tests.find_one({"test_id": test_id}, {"_id": 0})
    total_votes = updated["votes_a"] + updated["votes_b"]
    
    if total_votes >= 10:
        winner = "a" if updated["votes_a"] > updated["votes_b"] else "b" if updated["votes_b"] > updated["votes_a"] else "tie"
        await db.ab_tests.update_one(
            {"test_id": test_id},
            {"$set": {"status": "completed", "winner": winner}}
        )
    
    return {"message": "Vote recorded", "votes_a": updated["votes_a"], "votes_b": updated["votes_b"]}

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
    
    system_message = """Create actionable daily growth plan. Return JSON with 'daily_tasks' array.
    Each task: day (int), title (string), description (string), type (post/engage/analyze/learn), priority (high/medium/low)."""
    
    prompt = f"Create {data.duration}-day Instagram growth plan for {niche} niche."
    
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
                "description": f"Focus on {task_type} activities",
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
    plan = await db.growth_plans.find_one({"plan_id": plan_id, "user_id": user.user_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return GrowthPlan(**plan)

@api_router.get("/growth-plans/{plan_id}/pdf")
async def get_growth_plan_pdf(plan_id: str, user: User = Depends(get_current_user)):
    plan = await db.growth_plans.find_one({"plan_id": plan_id, "user_id": user.user_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    team = None
    if user.team_id:
        team = await db.teams.find_one({"team_id": user.team_id}, {"_id": 0})
    
    brand_color = team.get("brand_color", "#6366F1") if team else "#6366F1"
    company_name = team.get("name", "InstaGrowth OS") if team else "InstaGrowth OS"
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFillColor(HexColor(brand_color))
    p.rect(0, height - 100, width, 100, fill=True)
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 55, f"{plan['duration']}-Day Growth Plan")
    
    y = height - 140
    p.setFillColor(HexColor("#000000"))
    
    for task in plan.get("daily_tasks", [])[:20]:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"Day {task.get('day')}: {task.get('title', '')[:50]}")
        y -= 15
        p.setFont("Helvetica", 10)
        p.drawString(60, y, task.get('description', '')[:80])
        y -= 22
        
        if y < 50:
            p.showPage()
            y = height - 50
    
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#666666"))
    p.drawString(50, 30, f"Generated by {company_name}")
    
    p.save()
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=growth_plan_{plan_id}.pdf"}
    )

# ==================== ONE-TIME PRODUCTS ROUTES ====================

ONE_TIME_PRODUCTS = {
    "recovery_report": {
        "product_id": "recovery_report",
        "name": "Instagram Recovery Report",
        "description": "Detailed analysis and recovery roadmap for struggling accounts",
        "price": 9.0,
        "type": "recovery_report"
    },
    "content_pack": {
        "product_id": "content_pack",
        "name": "30-Day Viral Content Pack",
        "description": "30 days of ready-to-post content ideas, hooks, and captions",
        "price": 19.0,
        "type": "content_pack"
    },
    "audit_pdf": {
        "product_id": "audit_pdf",
        "name": "Premium Account Audit PDF",
        "description": "Comprehensive audit report with detailed recommendations",
        "price": 15.0,
        "type": "audit_pdf"
    },
    "extra_account": {
        "product_id": "extra_account",
        "name": "Extra Instagram Account Slot",
        "description": "Add one more Instagram account to your plan",
        "price": 5.0,
        "type": "extra_account"
    }
}

@api_router.get("/products")
async def get_products():
    return list(ONE_TIME_PRODUCTS.values())

@api_router.post("/products/{product_id}/purchase")
async def purchase_product(product_id: str, request: Request, user: User = Depends(get_current_user)):
    if product_id not in ONE_TIME_PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = ONE_TIME_PRODUCTS[product_id]
    
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    host_url = str(request.base_url).rstrip("/")
    origin_url = request.headers.get("origin", "https://instagrowth-os.preview.emergentagent.com")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")
    
    checkout_request = CheckoutSessionRequest(
        amount=product["price"],
        currency="usd",
        success_url=f"{origin_url}/billing?product_session={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin_url}/billing",
        metadata={
            "user_id": user.user_id,
            "product_id": product_id,
            "product_type": product["type"]
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    purchase_doc = {
        "purchase_id": f"purch_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "product_id": product_id,
        "session_id": session.session_id,
        "amount": product["price"],
        "status": "pending",
        "data": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.product_purchases.insert_one(purchase_doc)
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/products/purchase-status/{session_id}")
async def get_product_purchase_status(session_id: str, user: User = Depends(get_current_user)):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    status = await stripe_checkout.get_checkout_status(session_id)
    
    if status.payment_status == "paid":
        purchase = await db.product_purchases.find_one({"session_id": session_id}, {"_id": 0})
        if purchase and purchase.get("status") != "completed":
            # Process the purchase
            product_id = purchase["product_id"]
            
            if product_id == "extra_account":
                # Add extra account slot
                await db.users.update_one(
                    {"user_id": user.user_id},
                    {"$inc": {"extra_accounts": 1}}
                )
            
            await db.product_purchases.update_one(
                {"session_id": session_id},
                {"$set": {"status": "completed"}}
            )
            
            await create_notification(
                user.user_id, "system",
                "Purchase Complete!",
                f"Your purchase of {ONE_TIME_PRODUCTS[product_id]['name']} is complete.",
                "/billing"
            )
    
    return {"status": status.status, "payment_status": status.payment_status}

@api_router.get("/products/purchases")
async def get_user_purchases(user: User = Depends(get_current_user)):
    purchases = await db.product_purchases.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return purchases

# ==================== EXPORT ROUTES ====================

@api_router.get("/export/accounts")
async def export_accounts_csv(user: User = Depends(get_current_user)):
    """Export accounts to CSV"""
    accounts = await db.instagram_accounts.find({"user_id": user.user_id}, {"_id": 0}).to_list(100)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Username", "Niche", "Followers", "Engagement Rate", "Reach", "Notes", "Client Name", "Created At"])
    
    for acc in accounts:
        writer.writerow([
            acc.get("username", ""),
            acc.get("niche", ""),
            acc.get("follower_count", ""),
            acc.get("engagement_rate", ""),
            acc.get("estimated_reach", ""),
            acc.get("notes", ""),
            acc.get("client_name", ""),
            acc.get("created_at", "")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=accounts.csv"}
    )

@api_router.get("/export/audits")
async def export_audits_csv(user: User = Depends(get_current_user)):
    """Export audits to CSV"""
    audits = await db.audits.find({"user_id": user.user_id}, {"_id": 0}).to_list(100)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Username", "Engagement Score", "Shadowban Risk", "Content Consistency", "Followers", "Created At"])
    
    for audit in audits:
        writer.writerow([
            audit.get("username", ""),
            audit.get("engagement_score", ""),
            audit.get("shadowban_risk", ""),
            audit.get("content_consistency", ""),
            audit.get("estimated_followers", ""),
            audit.get("created_at", "")
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audits.csv"}
    )

@api_router.get("/export/content")
async def export_content_csv(user: User = Depends(get_current_user)):
    """Export content to CSV"""
    content = await db.content_items.find({"user_id": user.user_id}, {"_id": 0}).to_list(500)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Content Type", "Content", "Is Favorite", "Created At"])
    
    for item in content:
        for c in item.get("content", []):
            writer.writerow([
                item.get("content_type", ""),
                c,
                item.get("is_favorite", False),
                item.get("created_at", "")
            ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=content.csv"}
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
    return [{"plan_id": k, **v} for k, v in SUBSCRIPTION_PLANS.items()]

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
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")
    
    checkout_request = CheckoutSessionRequest(
        amount=plan["price"],
        currency="usd",
        success_url=f"{origin_url}/billing?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin_url}/billing",
        metadata={"user_id": user.user_id, "plan_id": plan_id}
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "session_id": session.session_id,
        "plan_id": plan_id,
        "amount": plan["price"],
        "currency": "usd",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
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
                
                await create_notification(
                    user.user_id, "plan_upgrade",
                    f"Upgraded to {plan['name']}!",
                    f"Your account now has {plan['account_limit']} accounts and {plan['ai_usage_limit']} AI generations.",
                    "/dashboard"
                )
    
    return {"status": status.status, "payment_status": status.payment_status, "amount_total": status.amount_total}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    host_url = str(request.base_url).rstrip("/")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            
            # Check for subscription payment
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
                        {"user_id": txn["user_id"]},
                        {"$set": {
                            "role": plan_id,
                            "plan_id": plan_id,
                            "account_limit": plan["account_limit"],
                            "ai_usage_limit": plan["ai_usage_limit"],
                            "ai_usage_current": 0
                        }}
                    )
            
            # Check for product purchase
            purchase = await db.product_purchases.find_one({"session_id": session_id}, {"_id": 0})
            if purchase and purchase.get("status") != "completed":
                if purchase["product_id"] == "extra_account":
                    await db.users.update_one(
                        {"user_id": purchase["user_id"]},
                        {"$inc": {"extra_accounts": 1}}
                    )
                
                await db.product_purchases.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "completed"}}
                )
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

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
    
    product_revenue = await db.product_purchases.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_audits": total_audits,
        "total_teams": total_teams,
        "subscription_revenue": total_revenue[0]["total"] if total_revenue else 0,
        "product_revenue": product_revenue[0]["total"] if product_revenue else 0,
        "total_revenue": (total_revenue[0]["total"] if total_revenue else 0) + (product_revenue[0]["total"] if product_revenue else 0),
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
    favorites = await db.content_items.count_documents({"user_id": user.user_id, "is_favorite": True})
    
    recent_audits = await db.audits.find(
        {"user_id": user.user_id},
        {"_id": 0, "engagement_score": 1, "content_consistency": 1, "created_at": 1, "username": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    unread_notifications = await db.notifications.count_documents({"user_id": user.user_id, "read": False})
    
    return {
        "accounts_count": accounts,
        "audits_count": audits,
        "content_items_count": content_items,
        "growth_plans_count": growth_plans,
        "favorites_count": favorites,
        "ai_usage": {"current": user.ai_usage_current, "limit": user.ai_usage_limit},
        "account_usage": {"current": accounts, "limit": user.account_limit + user.extra_accounts},
        "recent_audits": recent_audits,
        "unread_notifications": unread_notifications
    }

# ==================== ROOT ROUTE ====================

@api_router.get("/")
async def root():
    return {"message": "InstaGrowth OS API", "version": "2.0.0"}

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
