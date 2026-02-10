from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

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
    onboarding_completed: bool = False
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
    onboarding_completed: bool = False

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
    niche: str = "Other"
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    # OAuth fields
    instagram_user_id: Optional[str] = None
    instagram_id: Optional[str] = None
    access_token: Optional[str] = None
    token_expires_at: Optional[float] = None
    connection_status: Optional[str] = None  # "connected" or None
    connected_at: Optional[str] = None
    # Profile data
    profile_picture: Optional[str] = None
    account_type: Optional[str] = None
    # Metrics
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    estimated_reach: Optional[int] = None
    posting_frequency: Optional[str] = None
    best_posting_time: Optional[str] = None
    last_audit_date: Optional[datetime] = None
    last_refreshed: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None

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
    category: str
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
    auto_reply_delay_min: int = 30
    auto_reply_delay_max: int = 120
    working_hours_start: int = 9
    working_hours_end: int = 21

class DMConversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    conversation_id: str
    account_id: str
    user_id: str
    contact_username: str
    is_lead: bool = False
    lead_score: int = 0
    messages: List[Dict[str, Any]] = []
    status: str = "active"
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
    content_type: str
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
    status: str = "active"
    created_at: datetime

# One-Time Product Models
class OneTimeProduct(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    type: str

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
    type: str
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
