from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# Admin Models
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "support"  # super_admin, support, finance

class AdminLogin(BaseModel):
    email: EmailStr
    password: str
    admin_code: str
    totp_code: Optional[str] = None  # 2FA code

class AdminResponse(BaseModel):
    admin_id: str
    name: str
    email: str
    role: str
    is_2fa_enabled: bool = False
    created_at: str

class Admin2FASetup(BaseModel):
    admin_id: str
    secret: str
    qr_code: str
    backup_codes: List[str]

# Plan Models
class PlanCreate(BaseModel):
    name: str
    price: float
    billing_cycle: str = "monthly"  # monthly, yearly
    account_limit: int
    ai_limit: int
    team_limit: int = 0
    white_label: bool = False
    features: List[str] = []

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    billing_cycle: Optional[str] = None
    account_limit: Optional[int] = None
    ai_limit: Optional[int] = None
    team_limit: Optional[int] = None
    white_label: Optional[bool] = None
    status: Optional[str] = None
    features: Optional[List[str]] = None

class Plan(BaseModel):
    plan_id: str
    name: str
    price: float
    billing_cycle: str
    account_limit: int
    ai_limit: int
    team_limit: int
    white_label: bool
    features: List[str]
    status: str = "active"
    created_at: str

# System Settings
class SystemSettings(BaseModel):
    platform_name: str = "InstaGrowth OS"
    support_email: str = "support@instagrowth.com"
    default_ai_model: str = "gpt-5.2"
    openai_api_key: Optional[str] = None
    stripe_api_key: Optional[str] = None
    resend_api_key: Optional[str] = None
    meta_api_key: Optional[str] = None

# IP Whitelist
class IPWhitelistEntry(BaseModel):
    ip_address: str
    description: str = ""
    added_by: str
    added_at: str

# Admin Log
class AdminLog(BaseModel):
    log_id: str
    admin_id: str
    admin_email: str
    action: str
    target_type: str  # user, plan, subscription, system
    target_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: str
    created_at: str

# Revenue Stats
class RevenueStats(BaseModel):
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    churn_rate: float
    arpu: float  # Average Revenue Per User
    total_revenue: float
    revenue_by_plan: Dict[str, float]

# AI Usage Stats
class AIUsageStats(BaseModel):
    total_requests_today: int
    total_requests_month: int
    estimated_cost: float
    usage_by_feature: Dict[str, int]
    top_users: List[Dict[str, Any]]
