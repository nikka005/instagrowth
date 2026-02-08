"""
Security middleware for rate limiting, IP blocking, and abuse protection
"""
from fastapi import Request, HTTPException
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import asyncio
import time

# In-memory rate limiters (use Redis in production for distributed systems)
login_attempts = defaultdict(list)  # IP -> [timestamps]
ai_requests = defaultdict(list)  # user_id -> [timestamps]
blocked_ips = set()
suspicious_users = set()

# Configuration
LOGIN_RATE_LIMIT = 5  # attempts per window
LOGIN_WINDOW = 300  # 5 minutes
AI_RATE_LIMIT = 30  # requests per minute
AI_WINDOW = 60  # 1 minute
BLOCK_DURATION = 3600  # 1 hour

def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def check_login_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded login rate limit"""
    if ip in blocked_ips:
        return False
    
    now = time.time()
    # Clean old attempts
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < LOGIN_WINDOW]
    
    if len(login_attempts[ip]) >= LOGIN_RATE_LIMIT:
        blocked_ips.add(ip)
        # Auto-unblock after duration (in production, use scheduled task)
        asyncio.create_task(auto_unblock_ip(ip))
        return False
    
    login_attempts[ip].append(now)
    return True

async def auto_unblock_ip(ip: str):
    """Auto unblock IP after duration"""
    await asyncio.sleep(BLOCK_DURATION)
    blocked_ips.discard(ip)

def check_ai_rate_limit(user_id: str) -> tuple[bool, int]:
    """Check if user has exceeded AI rate limit. Returns (allowed, remaining)"""
    now = time.time()
    # Clean old requests
    ai_requests[user_id] = [t for t in ai_requests[user_id] if now - t < AI_WINDOW]
    
    remaining = AI_RATE_LIMIT - len(ai_requests[user_id])
    
    if remaining <= 0:
        return False, 0
    
    ai_requests[user_id].append(now)
    return True, remaining - 1

def is_ip_blocked(ip: str) -> bool:
    """Check if IP is blocked"""
    return ip in blocked_ips

def block_ip(ip: str, duration: int = BLOCK_DURATION):
    """Manually block an IP"""
    blocked_ips.add(ip)
    if duration > 0:
        asyncio.create_task(auto_unblock_ip(ip))

def unblock_ip(ip: str):
    """Manually unblock an IP"""
    blocked_ips.discard(ip)

def flag_suspicious_user(user_id: str):
    """Flag a user as suspicious"""
    suspicious_users.add(user_id)

def unflag_suspicious_user(user_id: str):
    """Remove suspicious flag from user"""
    suspicious_users.discard(user_id)

def is_user_suspicious(user_id: str) -> bool:
    """Check if user is flagged as suspicious"""
    return user_id in suspicious_users

def get_blocked_ips() -> list:
    """Get list of blocked IPs"""
    return list(blocked_ips)

def get_suspicious_users() -> list:
    """Get list of suspicious users"""
    return list(suspicious_users)

def clear_login_attempts(ip: str):
    """Clear login attempts for IP (on successful login)"""
    login_attempts.pop(ip, None)
