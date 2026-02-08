from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
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
import base64

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
    role: str = "starter"  # starter, pro, agency, enterprise, admin
    plan_id: Optional[str] = None
    account_limit: int = 1
    ai_usage_limit: int = 10
    ai_usage_current: int = 0
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
    username: str
    niche: str
    notes: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
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
    growth_mistakes: List[str]
    recommendations: List[str]
    roadmap: Dict[str, Any]
    created_at: datetime

# Content Models
class ContentRequest(BaseModel):
    account_id: str
    content_type: str  # reels, hooks, captions, hashtags
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
    duration: int  # 7, 14, or 30 days
    niche: Optional[str] = None

class GrowthPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    plan_id: str
    account_id: str
    user_id: str
    duration: int
    daily_tasks: List[Dict[str, Any]]
    created_at: datetime

# Subscription Models
class SubscriptionPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    plan_id: str
    name: str
    price: float
    account_limit: int
    ai_usage_limit: int
    features: List[str]
    is_active: bool = True

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

def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def get_current_user(request: Request) -> User:
    # Check cookie first
    session_token = request.cookies.get("session_token")
    
    # Fall back to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if it's a JWT token (email/password auth)
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
    
    # Check session-based auth (Google OAuth)
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
    """Generate content using OpenAI GPT-5.2 via emergentintegrations"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"instagrowth_{uuid.uuid4().hex[:8]}",
        system_message=system_message
    ).with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=prompt)
    response = await chat.send_message(user_message)
    return response

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(data: UserCreate):
    existing = await db.users.find_one({"email": data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
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
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, data.email)
    return {"token": token, "user": UserResponse(**user_doc)}

@api_router.post("/auth/login")
async def login(data: UserLogin, response: Response):
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user_doc["user_id"], data.email)
    
    # Set cookie for session
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
    """Handle Google OAuth session creation"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get user data from Emergent auth
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        auth_data = resp.json()
    
    # Check if user exists
    user_doc = await db.users.find_one({"email": auth_data["email"]}, {"_id": 0})
    
    if not user_doc:
        # Create new user
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
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
        await db.users.insert_one(user_doc)
    else:
        user_id = user_doc["user_id"]
        # Update picture if changed
        if auth_data.get("picture") != user_doc.get("picture"):
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {"picture": auth_data.get("picture"), "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            user_doc["picture"] = auth_data.get("picture")
    
    # Store session
    session_token = auth_data["session_token"]
    session_doc = {
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
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

# ==================== INSTAGRAM ACCOUNTS ROUTES ====================

@api_router.post("/accounts", response_model=InstagramAccount)
async def create_account(data: InstagramAccountCreate, user: User = Depends(get_current_user)):
    await check_account_limit(user)
    
    account_id = f"acc_{uuid.uuid4().hex[:12]}"
    account_doc = {
        "account_id": account_id,
        "user_id": user.user_id,
        "username": data.username,
        "niche": data.niche,
        "notes": data.notes,
        "follower_count": None,
        "engagement_rate": None,
        "last_audit_date": None,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.instagram_accounts.insert_one(account_doc)
    return InstagramAccount(**account_doc)

@api_router.get("/accounts", response_model=List[InstagramAccount])
async def get_accounts(user: User = Depends(get_current_user)):
    accounts = await db.instagram_accounts.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)
    return [InstagramAccount(**acc) for acc in accounts]

@api_router.get("/accounts/{account_id}", response_model=InstagramAccount)
async def get_account(account_id: str, user: User = Depends(get_current_user)):
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id, "user_id": user.user_id},
        {"_id": 0}
    )
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
    
    account = await db.instagram_accounts.find_one(
        {"account_id": account_id},
        {"_id": 0}
    )
    return InstagramAccount(**account)

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str, user: User = Depends(get_current_user)):
    result = await db.instagram_accounts.delete_one(
        {"account_id": account_id, "user_id": user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}

# ==================== AI AUDIT ROUTES ====================

@api_router.post("/audits", response_model=Audit)
async def create_audit(data: AuditRequest, user: User = Depends(get_current_user)):
    await check_ai_usage(user)
    
    # Get account
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Generate audit using AI
    system_message = """You are an Instagram growth expert analyzing accounts. 
    Provide detailed, actionable analysis in JSON format with these exact keys:
    - engagement_score (0-100)
    - shadowban_risk (low/medium/high)
    - content_consistency (0-100)
    - growth_mistakes (array of 3-5 specific mistakes)
    - recommendations (array of 5-7 actionable recommendations)
    - roadmap (object with week1, week2, week3, week4 arrays of daily tasks)
    Be specific and professional. Response must be valid JSON only."""
    
    prompt = f"""Analyze this Instagram account:
    Username: @{account['username']}
    Niche: {account['niche']}
    Notes: {account.get('notes', 'No additional notes')}
    
    Generate a comprehensive audit with engagement score, shadowban risk assessment, 
    content consistency rating, common growth mistakes, and a 30-day recovery roadmap."""
    
    try:
        ai_response = await generate_ai_content(prompt, system_message)
        # Parse JSON from response
        import json
        # Clean response - remove markdown code blocks if present
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
        # Fallback mock data
        audit_data = {
            "engagement_score": 65,
            "shadowban_risk": "medium",
            "content_consistency": 70,
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
        "growth_mistakes": audit_data.get("growth_mistakes", []),
        "recommendations": audit_data.get("recommendations", []),
        "roadmap": audit_data.get("roadmap", {}),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.audits.insert_one(audit_doc)
    
    # Update account last audit date
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
    
    # Check plan for PDF export
    if user.role == "starter":
        raise HTTPException(status_code=403, detail="PDF export requires Pro plan or higher")
    
    # Generate PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFillColor(HexColor("#6366F1"))
    p.rect(0, height - 100, width, 100, fill=True)
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 60, "InstaGrowth OS - Account Audit Report")
    
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
    p.drawString(50, 30, f"Generated by InstaGrowth OS | {datetime.now().strftime('%Y-%m-%d')}")
    
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
    
    # Get account for niche context
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
        # Clean response
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
        # Fallback content
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
        # Generate fallback tasks
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
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFillColor(HexColor("#6366F1"))
    p.rect(0, height - 100, width, 100, fill=True)
    p.setFillColor(HexColor("#FFFFFF"))
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 60, f"{plan['duration']}-Day Growth Plan")
    
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
    p.drawString(50, 30, f"Generated by InstaGrowth OS | {datetime.now().strftime('%Y-%m-%d')}")
    
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
        plans.append({
            "plan_id": plan_id,
            **plan
        })
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
    
    # Create pending transaction
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
    
    # Update transaction
    if status.payment_status == "paid":
        txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        if txn and txn.get("status") != "completed":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Update user plan
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
    total_revenue = await db.payment_transactions.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_audits": total_audits,
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
    
    # Get recent audits for chart
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
    return {"message": "InstaGrowth OS API", "version": "1.0.0"}

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
