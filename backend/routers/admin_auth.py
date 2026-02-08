from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
import uuid
import jwt
import os

from database import get_database
from utils import verify_password, JWT_SECRET

router = APIRouter(prefix="/admin-auth", tags=["Admin Authentication"])

class AdminLogin(BaseModel):
    email: EmailStr
    password: str
    admin_code: str  # Additional security code for admin login

# Admin secret code - in production, this should be in environment variables
ADMIN_SECRET_CODE = os.environ.get('ADMIN_SECRET_CODE', 'INSTAGROWTH_ADMIN_2024')

def create_admin_token(user_id: str, email: str, expires_hours: int = 8) -> str:
    """Create a shorter-lived token for admin sessions"""
    payload = {
        "user_id": user_id,
        "email": email,
        "is_admin": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@router.post("/login")
async def admin_login(data: AdminLogin, response: Response):
    """Separate admin login with additional security code"""
    db = get_database()
    
    # Verify admin secret code first
    if data.admin_code != ADMIN_SECRET_CODE:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Find user
    user_doc = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Verify password
    if not verify_password(data.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Check if user is admin
    if user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    # Create admin-specific token with shorter expiry
    token = create_admin_token(user_doc["user_id"], data.email)
    
    # Log admin login
    await db.admin_logins.insert_one({
        "user_id": user_doc["user_id"],
        "email": data.email,
        "ip_address": None,  # Can be extracted from request headers
        "login_at": datetime.now(timezone.utc).isoformat()
    })
    
    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=8 * 60 * 60,  # 8 hours
        path="/"
    )
    
    return {
        "token": token,
        "admin": {
            "user_id": user_doc["user_id"],
            "email": user_doc["email"],
            "name": user_doc["name"],
            "role": user_doc["role"]
        },
        "expires_in": "8 hours"
    }

@router.get("/verify")
async def verify_admin_session(request: Request):
    """Verify if current session is a valid admin session"""
    db = get_database()
    
    admin_token = request.cookies.get("admin_session")
    if not admin_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            admin_token = auth_header[7:]
    
    if not admin_token:
        raise HTTPException(status_code=401, detail="Admin session not found")
    
    try:
        payload = jwt.decode(admin_token, JWT_SECRET, algorithms=["HS256"])
        
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Not an admin session")
        
        user_doc = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
        if not user_doc or user_doc.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access revoked")
        
        return {
            "valid": True,
            "admin": {
                "user_id": user_doc["user_id"],
                "email": user_doc["email"],
                "name": user_doc["name"]
            }
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Admin session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid admin session")

@router.post("/logout")
async def admin_logout(request: Request, response: Response):
    """Logout from admin session"""
    db = get_database()
    
    admin_token = request.cookies.get("admin_session")
    if admin_token:
        try:
            payload = jwt.decode(admin_token, JWT_SECRET, algorithms=["HS256"])
            await db.admin_logins.update_one(
                {"user_id": payload["user_id"]},
                {"$set": {"logout_at": datetime.now(timezone.utc).isoformat()}},
                upsert=False
            )
        except:
            pass
    
    response.delete_cookie(key="admin_session", path="/")
    return {"message": "Admin logged out successfully"}

@router.get("/login-history")
async def get_admin_login_history(request: Request):
    """Get admin login history (admin only)"""
    db = get_database()
    
    # Verify admin session first
    admin_token = request.cookies.get("admin_session")
    if not admin_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            admin_token = auth_header[7:]
    
    if not admin_token:
        raise HTTPException(status_code=401, detail="Admin session required")
    
    try:
        payload = jwt.decode(admin_token, JWT_SECRET, algorithms=["HS256"])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
    except:
        raise HTTPException(status_code=401, detail="Invalid admin session")
    
    history = await db.admin_logins.find(
        {}, {"_id": 0}
    ).sort("login_at", -1).limit(50).to_list(50)
    
    return {"login_history": history}
