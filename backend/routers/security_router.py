"""
Security API Router - Rate limiting, IP blocking, session management
"""
from fastapi import APIRouter, HTTPException, Request

from database import get_database
from dependencies import get_current_user
from routers.admin_panel_auth import verify_admin_token
from security import (
    get_blocked_ips, block_ip, unblock_ip,
    get_suspicious_users, flag_suspicious_user, unflag_suspicious_user,
    is_ip_blocked, check_login_rate_limit
)
from datetime import datetime, timezone

router = APIRouter(prefix="/security", tags=["Security"])

# ==================== USER SESSION ENDPOINTS ====================

@router.get("/sessions")
async def get_user_sessions(request: Request):
    """Get user's active sessions"""
    db = get_database()
    user = await get_current_user(request, db)
    
    sessions = await db.user_sessions.find(
        {"user_id": user.user_id, "is_active": True},
        {"_id": 0, "session_token": 0}
    ).to_list(10)
    
    return {"sessions": sessions}

@router.post("/sessions/logout-all")
async def logout_all_sessions(request: Request):
    """Logout from all sessions except current"""
    db = get_database()
    user = await get_current_user(request, db)
    
    # Get current session token from cookie
    current_token = request.cookies.get("session_token")
    
    await db.user_sessions.update_many(
        {"user_id": user.user_id, "session_token": {"$ne": current_token}},
        {"$set": {"is_active": False, "logged_out_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Logged out from all other sessions"}

@router.delete("/sessions/{session_id}")
async def logout_session(session_id: str, request: Request):
    """Logout from a specific session"""
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.user_sessions.update_one(
        {"session_id": session_id, "user_id": user.user_id},
        {"$set": {"is_active": False, "logged_out_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session logged out"}

# ==================== ADMIN SECURITY ENDPOINTS ====================

@router.get("/admin/blocked-ips")
async def get_blocked_ips_list(request: Request):
    """Get list of blocked IPs (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Get from in-memory
    memory_blocked = get_blocked_ips()
    
    # Get from database (permanent blocks)
    db_blocked = await db.blocked_ips.find({}, {"_id": 0}).to_list(100)
    
    return {
        "temporary_blocks": memory_blocked,
        "permanent_blocks": db_blocked
    }

@router.post("/admin/block-ip")
async def admin_block_ip(
    ip: str,
    reason: str = None,
    permanent: bool = False,
    request: Request = None
):
    """Block an IP address (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    if permanent:
        await db.blocked_ips.update_one(
            {"ip": ip},
            {"$set": {
                "ip": ip,
                "reason": reason,
                "blocked_by": admin["admin_id"],
                "blocked_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
    else:
        block_ip(ip)
    
    return {"message": f"IP {ip} blocked"}

@router.delete("/admin/unblock-ip/{ip}")
async def admin_unblock_ip(ip: str, request: Request):
    """Unblock an IP address (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Remove from memory
    unblock_ip(ip)
    
    # Remove from database
    await db.blocked_ips.delete_one({"ip": ip})
    
    return {"message": f"IP {ip} unblocked"}

@router.get("/admin/suspicious-users")
async def get_suspicious_users_list(request: Request):
    """Get list of flagged suspicious users (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    # Get from memory
    flagged_ids = get_suspicious_users()
    
    # Get user details
    users = []
    for user_id in flagged_ids:
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
        if user:
            users.append(user)
    
    # Also get from database
    db_flagged = await db.suspicious_users.find({}, {"_id": 0}).to_list(100)
    
    return {
        "flagged_users": users,
        "database_flags": db_flagged
    }

@router.post("/admin/flag-user")
async def admin_flag_user(
    user_id: str,
    reason: str,
    request: Request = None
):
    """Flag a user as suspicious (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    flag_suspicious_user(user_id)
    
    await db.suspicious_users.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "reason": reason,
            "flagged_by": admin["admin_id"],
            "flagged_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"message": "User flagged"}

@router.delete("/admin/unflag-user/{user_id}")
async def admin_unflag_user(user_id: str, request: Request):
    """Remove suspicious flag from user (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    unflag_suspicious_user(user_id)
    await db.suspicious_users.delete_one({"user_id": user_id})
    
    return {"message": "User unflagged"}

@router.post("/admin/force-logout")
async def admin_force_logout(user_id: str, request: Request = None):
    """Force logout a user from all sessions (admin)"""
    db = get_database()
    admin = await verify_admin_token(request)
    
    result = await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {
            "is_active": False,
            "logged_out_at": datetime.now(timezone.utc).isoformat(),
            "forced_by": admin["admin_id"]
        }}
    )
    
    # Also update user document
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"force_logout": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": f"User force logged out from {result.modified_count} sessions"}
