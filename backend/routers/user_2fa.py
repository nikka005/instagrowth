"""
Two-Factor Authentication (2FA) for Regular Users

Provides TOTP-based 2FA with:
- Setup with QR code
- Backup codes
- Enable/disable functionality
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import Optional
import pyotp
import qrcode
import base64
from io import BytesIO
import secrets

from database import get_database
from dependencies import get_current_user
from utils import verify_password

router = APIRouter(prefix="/auth/2fa", tags=["User 2FA"])

@router.get("/status")
async def get_2fa_status(request: Request):
    """Get current 2FA status for user"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    return {
        "is_enabled": user_doc.get("is_2fa_enabled", False),
        "has_backup_codes": len(user_doc.get("backup_codes", [])) > 0
    }

@router.post("/setup")
async def setup_2fa(request: Request):
    """Initialize 2FA setup - generates secret and QR code"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    if user_doc.get("is_2fa_enabled"):
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # Generate QR code
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="InstaGrowth OS"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    # Store pending setup
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {
            "pending_2fa_secret": secret,
            "pending_backup_codes": backup_codes
        }}
    )
    
    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "backup_codes": backup_codes,
        "manual_entry_key": secret
    }

@router.post("/verify")
async def verify_and_enable_2fa(code: str, request: Request):
    """Verify TOTP code and enable 2FA"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    secret = user_doc.get("pending_2fa_secret")
    if not secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated. Call /setup first.")
    
    # Verify the code
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Enable 2FA
    await db.users.update_one(
        {"user_id": user.user_id},
        {
            "$set": {
                "is_2fa_enabled": True,
                "totp_secret": secret,
                "backup_codes": user_doc.get("pending_backup_codes", []),
                "2fa_enabled_at": datetime.now(timezone.utc).isoformat()
            },
            "$unset": {
                "pending_2fa_secret": "",
                "pending_backup_codes": ""
            }
        }
    )
    
    return {
        "message": "2FA enabled successfully",
        "backup_codes_count": len(user_doc.get("pending_backup_codes", []))
    }

@router.post("/disable")
async def disable_2fa(password: str, code: str, request: Request):
    """Disable 2FA (requires password and current 2FA code)"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    if not user_doc.get("is_2fa_enabled"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")
    
    # Verify password
    if not verify_password(password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Verify 2FA code
    totp = pyotp.TOTP(user_doc["totp_secret"])
    if not totp.verify(code):
        # Check backup codes
        if code not in user_doc.get("backup_codes", []):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Disable 2FA
    await db.users.update_one(
        {"user_id": user.user_id},
        {
            "$set": {
                "is_2fa_enabled": False,
                "2fa_disabled_at": datetime.now(timezone.utc).isoformat()
            },
            "$unset": {
                "totp_secret": "",
                "backup_codes": ""
            }
        }
    )
    
    return {"message": "2FA disabled successfully"}

@router.post("/verify-code")
async def verify_2fa_code(code: str, user_id: str):
    """Verify 2FA code during login (called from login endpoint)"""
    db = get_database()
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user_doc.get("is_2fa_enabled"):
        return {"valid": True, "message": "2FA not enabled"}
    
    # Verify TOTP
    totp = pyotp.TOTP(user_doc["totp_secret"])
    if totp.verify(code):
        return {"valid": True}
    
    # Check backup codes
    backup_codes = user_doc.get("backup_codes", [])
    if code in backup_codes:
        # Remove used backup code
        await db.users.update_one(
            {"user_id": user_id},
            {"$pull": {"backup_codes": code}}
        )
        return {"valid": True, "backup_code_used": True}
    
    return {"valid": False}

@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(password: str, code: str, request: Request):
    """Regenerate backup codes (requires password and 2FA code)"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    if not user_doc.get("is_2fa_enabled"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")
    
    # Verify password
    if not verify_password(password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Verify 2FA code
    totp = pyotp.TOTP(user_doc["totp_secret"])
    if not totp.verify(code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Generate new backup codes
    new_backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"backup_codes": new_backup_codes}}
    )
    
    return {
        "message": "Backup codes regenerated",
        "backup_codes": new_backup_codes
    }

@router.get("/backup-codes")
async def get_backup_codes_count(request: Request):
    """Get remaining backup codes count"""
    db = get_database()
    user = await get_current_user(request, db)
    
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    
    return {
        "remaining_codes": len(user_doc.get("backup_codes", [])),
        "is_2fa_enabled": user_doc.get("is_2fa_enabled", False)
    }
