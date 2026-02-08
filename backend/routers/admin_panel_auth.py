from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid
import jwt
import pyotp
import qrcode
import base64
from io import BytesIO
import os
import secrets

from database import get_database
from utils import hash_password, verify_password, JWT_SECRET

router = APIRouter(prefix="/admin-panel", tags=["Admin Panel"])

ADMIN_SECRET_CODE = os.environ.get('ADMIN_SECRET_CODE', 'INSTAGROWTH_ADMIN_2024')
ADMIN_IP_WHITELIST_ENABLED = os.environ.get('ADMIN_IP_WHITELIST_ENABLED', 'false').lower() == 'true'

# Role permissions
ROLE_PERMISSIONS = {
    "super_admin": ["*"],
    "support": ["users", "accounts", "logs"],
    "finance": ["subscriptions", "revenue", "plans"]
}

def create_admin_token(admin_id: str, email: str, role: str, expires_hours: int = 8) -> str:
    payload = {
        "admin_id": admin_id,
        "email": email,
        "role": role,
        "is_admin_panel": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def verify_admin_token(request: Request):
    db = get_database()
    
    admin_token = request.cookies.get("admin_panel_token")
    if not admin_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            admin_token = auth_header[7:]
    
    if not admin_token:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    try:
        payload = jwt.decode(admin_token, JWT_SECRET, algorithms=["HS256"])
        if not payload.get("is_admin_panel"):
            raise HTTPException(status_code=403, detail="Invalid admin token")
        
        admin = await db.admins.find_one({"admin_id": payload["admin_id"]}, {"_id": 0})
        if not admin or admin.get("status") != "active":
            raise HTTPException(status_code=403, detail="Admin account disabled")
        
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Admin session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid admin token")

async def check_permission(admin: dict, resource: str):
    role = admin.get("role", "support")
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    if "*" not in permissions and resource not in permissions:
        raise HTTPException(status_code=403, detail=f"No permission to access {resource}")

async def log_admin_action(admin: dict, action: str, target_type: str, target_id: str = None, details: dict = None, ip: str = None):
    db = get_database()
    log_doc = {
        "log_id": f"log_{uuid.uuid4().hex[:12]}",
        "admin_id": admin["admin_id"],
        "admin_email": admin["email"],
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details or {},
        "ip_address": ip or "unknown",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.admin_logs.insert_one(log_doc)

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# ==================== ADMIN AUTH ====================

@router.post("/auth/register")
async def register_admin(name: str, email: str, password: str, role: str, request: Request):
    """Register new admin (Super Admin only)"""
    db = get_database()
    admin = await verify_admin_token(request)
    await check_permission(admin, "*")
    
    existing = await db.admins.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Admin email already exists")
    
    if role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    admin_id = f"admin_{uuid.uuid4().hex[:12]}"
    admin_doc = {
        "admin_id": admin_id,
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "status": "active",
        "is_2fa_enabled": False,
        "totp_secret": None,
        "backup_codes": [],
        "allowed_ips": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.admins.insert_one(admin_doc)
    
    await log_admin_action(admin, "create_admin", "admin", admin_id, {"new_admin_email": email}, get_client_ip(request))
    
    return {"admin_id": admin_id, "message": "Admin created successfully"}

@router.post("/auth/login")
async def admin_panel_login(email: str, password: str, admin_code: str, totp_code: str = None, request: Request = None, response: Response = None):
    """Admin panel login with optional 2FA"""
    db = get_database()
    
    # Verify admin code
    if admin_code != ADMIN_SECRET_CODE:
        await db.admin_logs.insert_one({
            "log_id": f"log_{uuid.uuid4().hex[:12]}",
            "admin_id": None,
            "admin_email": email,
            "action": "failed_login",
            "target_type": "auth",
            "details": {"reason": "invalid_admin_code"},
            "ip_address": get_client_ip(request),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Find admin
    admin = await db.admins.find_one({"email": email}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Verify password
    if not verify_password(password, admin.get("password_hash", "")):
        await log_admin_action({"admin_id": admin["admin_id"], "email": email}, "failed_login", "auth", None, {"reason": "wrong_password"}, get_client_ip(request))
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Check if admin is active
    if admin.get("status") != "active":
        raise HTTPException(status_code=403, detail="Admin account is disabled")
    
    # Check IP whitelist
    client_ip = get_client_ip(request)
    if admin.get("allowed_ips") and len(admin["allowed_ips"]) > 0:
        if client_ip not in admin["allowed_ips"]:
            raise HTTPException(status_code=403, detail="Access denied from this IP address")
    
    # Verify 2FA if enabled
    if admin.get("is_2fa_enabled"):
        if not totp_code:
            return {"requires_2fa": True, "message": "2FA code required"}
        
        totp = pyotp.TOTP(admin["totp_secret"])
        if not totp.verify(totp_code):
            # Check backup codes
            if totp_code in admin.get("backup_codes", []):
                # Remove used backup code
                await db.admins.update_one(
                    {"admin_id": admin["admin_id"]},
                    {"$pull": {"backup_codes": totp_code}}
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Create token
    token = create_admin_token(admin["admin_id"], email, admin["role"])
    
    # Log successful login
    await log_admin_action(admin, "login", "auth", None, {"ip": client_ip}, client_ip)
    
    response.set_cookie(
        key="admin_panel_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=8 * 60 * 60,
        path="/"
    )
    
    return {
        "token": token,
        "admin": {
            "admin_id": admin["admin_id"],
            "name": admin["name"],
            "email": admin["email"],
            "role": admin["role"],
            "is_2fa_enabled": admin.get("is_2fa_enabled", False)
        }
    }

@router.post("/auth/setup-2fa")
async def setup_2fa(request: Request):
    """Setup 2FA for admin"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # Generate QR code
    provisioning_uri = totp.provisioning_uri(admin["email"], issuer_name="InstaGrowth OS Admin")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    # Store temporarily (not enabled yet)
    await db.admins.update_one(
        {"admin_id": admin["admin_id"]},
        {"$set": {"pending_2fa_secret": secret, "pending_backup_codes": backup_codes}}
    )
    
    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "backup_codes": backup_codes
    }

@router.post("/auth/verify-2fa")
async def verify_and_enable_2fa(totp_code: str, request: Request):
    """Verify and enable 2FA"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    admin_doc = await db.admins.find_one({"admin_id": admin["admin_id"]}, {"_id": 0})
    secret = admin_doc.get("pending_2fa_secret")
    
    if not secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    totp = pyotp.TOTP(secret)
    if not totp.verify(totp_code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Enable 2FA
    await db.admins.update_one(
        {"admin_id": admin["admin_id"]},
        {
            "$set": {
                "is_2fa_enabled": True,
                "totp_secret": secret,
                "backup_codes": admin_doc.get("pending_backup_codes", [])
            },
            "$unset": {"pending_2fa_secret": "", "pending_backup_codes": ""}
        }
    )
    
    await log_admin_action(admin, "enable_2fa", "security", admin["admin_id"], {}, get_client_ip(request))
    
    return {"message": "2FA enabled successfully"}

@router.post("/auth/disable-2fa")
async def disable_2fa(password: str, request: Request):
    """Disable 2FA"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    admin_doc = await db.admins.find_one({"admin_id": admin["admin_id"]}, {"_id": 0})
    if not verify_password(password, admin_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    await db.admins.update_one(
        {"admin_id": admin["admin_id"]},
        {"$set": {"is_2fa_enabled": False, "totp_secret": None, "backup_codes": []}}
    )
    
    await log_admin_action(admin, "disable_2fa", "security", admin["admin_id"], {}, get_client_ip(request))
    
    return {"message": "2FA disabled"}

@router.post("/auth/logout")
async def admin_panel_logout(request: Request, response: Response):
    """Logout from admin panel"""
    try:
        admin = await verify_admin_token(request)
        await log_admin_action(admin, "logout", "auth", None, {}, get_client_ip(request))
    except:
        pass
    
    response.delete_cookie(key="admin_panel_token", path="/")
    return {"message": "Logged out"}

@router.get("/auth/me")
async def get_current_admin(request: Request):
    """Get current admin info"""
    admin = await verify_admin_token(request)
    return {
        "admin_id": admin["admin_id"],
        "name": admin["name"],
        "email": admin["email"],
        "role": admin["role"],
        "is_2fa_enabled": admin.get("is_2fa_enabled", False),
        "permissions": ROLE_PERMISSIONS.get(admin["role"], [])
    }

# ==================== IP WHITELIST ====================

@router.get("/security/ip-whitelist")
async def get_ip_whitelist(request: Request):
    """Get admin's IP whitelist"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    admin_doc = await db.admins.find_one({"admin_id": admin["admin_id"]}, {"_id": 0})
    return {"allowed_ips": admin_doc.get("allowed_ips", []), "current_ip": get_client_ip(request)}

@router.post("/security/ip-whitelist")
async def add_ip_to_whitelist(ip_address: str, description: str = "", request: Request = None):
    """Add IP to whitelist"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    entry = {
        "ip": ip_address,
        "description": description,
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.admins.update_one(
        {"admin_id": admin["admin_id"]},
        {"$push": {"allowed_ips": entry}}
    )
    
    await log_admin_action(admin, "add_ip_whitelist", "security", None, {"ip": ip_address}, get_client_ip(request))
    
    return {"message": "IP added to whitelist"}

@router.delete("/security/ip-whitelist/{ip_address}")
async def remove_ip_from_whitelist(ip_address: str, request: Request):
    """Remove IP from whitelist"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    await db.admins.update_one(
        {"admin_id": admin["admin_id"]},
        {"$pull": {"allowed_ips": {"ip": ip_address}}}
    )
    
    await log_admin_action(admin, "remove_ip_whitelist", "security", None, {"ip": ip_address}, get_client_ip(request))
    
    return {"message": "IP removed from whitelist"}
