import bcrypt
import jwt
import secrets
import time
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Optional
import os

logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')

# Rate limiting storage
rate_limit_storage = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 10

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
    current_time = time.time()
    user_requests = rate_limit_storage[user_id]
    rate_limit_storage[user_id] = [t for t in user_requests if current_time - t < RATE_LIMIT_WINDOW]
    if len(rate_limit_storage[user_id]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    rate_limit_storage[user_id].append(current_time)
    return True
