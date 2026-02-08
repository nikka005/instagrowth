"""
Email Automation System - Automated emails for user lifecycle
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
import uuid

from database import get_database
from services import send_email

router = APIRouter(prefix="/email-automation", tags=["Email Automation"])

# Email Templates
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to InstaGrowth OS! 🚀",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Welcome to InstaGrowth OS!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Instagram growth journey starts now</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Thank you for joining InstaGrowth OS! We're excited to help you grow your Instagram presence with AI-powered tools.</p>
                
                <div style="background: rgba(99, 102, 241, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <h3 style="margin: 0 0 16px 0; color: #a5b4fc;">🎯 Quick Start Guide</h3>
                    <ol style="margin: 0; padding-left: 20px; line-height: 2;">
                        <li>Connect your Instagram account</li>
                        <li>Generate your first AI audit</li>
                        <li>Create content with AI suggestions</li>
                        <li>Build your personalized growth plan</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Go to Dashboard</a>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8;">Need help? Reply to this email or visit our support center.</p>
            </div>
            <div style="background: rgba(0,0,0,0.2); padding: 24px; text-align: center;">
                <p style="margin: 0; font-size: 12px; color: #64748b;">© 2025 InstaGrowth OS. All rights reserved.</p>
            </div>
        </div>
        """
    },
    "subscription_activated": {
        "subject": "Your {plan} Plan is Now Active! 🎉",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Subscription Activated!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">You're now on the {plan} plan</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Great news! Your {plan} subscription is now active. Here's what you now have access to:</p>
                
                <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <h3 style="margin: 0 0 16px 0; color: #6ee7b7;">✨ Your Plan Includes</h3>
                    <ul style="margin: 0; padding-left: 20px; line-height: 2;">
                        <li>{account_limit} Instagram accounts</li>
                        <li>{ai_credits} AI credits per month</li>
                        <li>{team_limit} team members</li>
                        <li>All premium features</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Start Using Your Plan</a>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8;">Your next billing date: {next_billing_date}</p>
            </div>
        </div>
        """
    },
    "renewal_reminder": {
        "subject": "Your Subscription Renews in {days} Days",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Renewal Reminder</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your subscription renews soon</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Just a friendly reminder that your <strong>{plan}</strong> subscription will automatically renew in <strong>{days} days</strong>.</p>
                
                <div style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <p style="margin: 0;"><strong>Amount:</strong> ${amount}/month</p>
                    <p style="margin: 8px 0 0 0;"><strong>Renewal Date:</strong> {renewal_date}</p>
                    <p style="margin: 8px 0 0 0;"><strong>Payment Method:</strong> •••• {last_four}</p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">No action needed if you want to continue. To make changes:</p>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: rgba(255,255,255,0.1); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid rgba(255,255,255,0.2);">Manage Subscription</a>
                </div>
            </div>
        </div>
        """
    },
    "credits_low": {
        "subject": "⚠️ Your AI Credits Are Running Low",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Credits Running Low</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Only {remaining} credits remaining</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">You're running low on AI credits. You have <strong>{remaining} credits</strong> remaining out of your monthly {total} credits.</p>
                
                <div style="background: rgba(239, 68, 68, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <p style="margin: 0;"><strong>Credits Used:</strong> {used}/{total}</p>
                    <p style="margin: 8px 0 0 0;"><strong>Reset Date:</strong> {reset_date}</p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">Options to get more credits:</p>
                <ul style="line-height: 2;">
                    <li>Wait for monthly reset on {reset_date}</li>
                    <li>Upgrade to a higher plan for more credits</li>
                    <li>Purchase additional credit packs</li>
                </ul>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Upgrade Plan</a>
                </div>
            </div>
        </div>
        """
    },
    "subscription_cancelled": {
        "subject": "We're Sorry to See You Go 😢",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #64748b 0%, #475569 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Subscription Cancelled</h1>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Your InstaGrowth OS subscription has been cancelled. You'll continue to have access until <strong>{end_date}</strong>.</p>
                
                <div style="background: rgba(100, 116, 139, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <h3 style="margin: 0 0 16px 0; color: #94a3b8;">Before you go, remember you can:</h3>
                    <ul style="margin: 0; padding-left: 20px; line-height: 2;">
                        <li>Export your data and reports</li>
                        <li>Download any generated content</li>
                        <li>Save your growth plans</li>
                    </ul>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">Changed your mind? You can reactivate anytime:</p>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Reactivate Subscription</a>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8;">We'd love to know why you cancelled. Reply to this email with your feedback.</p>
            </div>
        </div>
        """
    },
    "weekly_report": {
        "subject": "📊 Your Weekly Instagram Growth Report",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Weekly Growth Report</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{week_range}</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Here's your Instagram growth summary for this week:</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 24px 0;">
                    <div style="background: rgba(99, 102, 241, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #a5b4fc;">{follower_change}</p>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Follower Change</p>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #6ee7b7;">{ai_used}</p>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">AI Features Used</p>
                    </div>
                    <div style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #fcd34d;">{content_created}</p>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Content Created</p>
                    </div>
                    <div style="background: rgba(236, 72, 153, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #f9a8d4;">{audits_run}</p>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Audits Run</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">View Full Dashboard</a>
                </div>
            </div>
        </div>
        """
    }
}

async def send_automated_email(email_type: str, recipient_email: str, data: dict):
    """Send an automated email based on template type"""
    if email_type not in EMAIL_TEMPLATES:
        raise ValueError(f"Unknown email type: {email_type}")
    
    template = EMAIL_TEMPLATES[email_type]
    subject = template["subject"].format(**data)
    html = template["template"].format(**data)
    
    try:
        await send_email(recipient_email, subject, html)
        
        # Log the email
        db = get_database()
        await db.email_logs.insert_one({
            "email_id": f"EMAIL-{uuid.uuid4().hex[:12]}",
            "type": email_type,
            "recipient": recipient_email,
            "subject": subject,
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat()
        })
        
        return True
    except Exception as e:
        # Log failure
        db = get_database()
        await db.email_logs.insert_one({
            "email_id": f"EMAIL-{uuid.uuid4().hex[:12]}",
            "type": email_type,
            "recipient": recipient_email,
            "subject": subject,
            "status": "failed",
            "error": str(e),
            "attempted_at": datetime.now(timezone.utc).isoformat()
        })
        return False

# API Endpoints for triggering emails

@router.post("/send-welcome")
async def trigger_welcome_email(user_id: str, request: Request = None):
    """Send welcome email to a user"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    frontend_url = "https://insta-automation-8.preview.emergentagent.com"
    
    success = await send_automated_email("welcome", user["email"], {
        "name": user.get("name", "there"),
        "dashboard_url": f"{frontend_url}/dashboard"
    })
    
    return {"success": success}

@router.post("/check-renewals")
async def check_and_send_renewal_reminders(request: Request = None):
    """Check for upcoming renewals and send reminder emails"""
    db = get_database()
    
    # Find subscriptions expiring in 3 days
    three_days = datetime.now(timezone.utc) + timedelta(days=3)
    
    subscriptions = await db.subscriptions.find({
        "status": "active",
        "current_period_end": {"$lte": three_days.isoformat()}
    }).to_list(100)
    
    sent_count = 0
    for sub in subscriptions:
        user = await db.users.find_one({"user_id": sub["user_id"]}, {"_id": 0})
        if user:
            success = await send_automated_email("renewal_reminder", user["email"], {
                "name": user.get("name", "there"),
                "plan": sub.get("plan", "Pro"),
                "days": "3",
                "amount": "49",
                "renewal_date": sub.get("current_period_end", "soon"),
                "last_four": "4242",
                "billing_url": "https://insta-automation-8.preview.emergentagent.com/billing"
            })
            if success:
                sent_count += 1
    
    return {"sent": sent_count}

@router.post("/check-low-credits")
async def check_and_send_low_credit_alerts(request: Request = None):
    """Check for users with low credits and send alerts"""
    db = get_database()
    
    # Find users with less than 20% credits remaining
    credits_list = await db.ai_credits.find({}).to_list(1000)
    
    sent_count = 0
    for credits in credits_list:
        if credits["total_credits"] > 0:
            percentage = (credits["remaining_credits"] / credits["total_credits"]) * 100
            if percentage < 20:
                user = await db.users.find_one({"user_id": credits["user_id"]}, {"_id": 0})
                if user:
                    success = await send_automated_email("credits_low", user["email"], {
                        "name": user.get("name", "there"),
                        "remaining": credits["remaining_credits"],
                        "used": credits["used_credits"],
                        "total": credits["total_credits"],
                        "reset_date": credits.get("reset_date", "1st of next month"),
                        "billing_url": "https://insta-automation-8.preview.emergentagent.com/billing"
                    })
                    if success:
                        sent_count += 1
    
    return {"sent": sent_count}

@router.get("/templates")
async def get_email_templates():
    """Get all available email templates"""
    return {
        "templates": list(EMAIL_TEMPLATES.keys())
    }

@router.get("/logs")
async def get_email_logs(limit: int = 50, email_type: str = None, request: Request = None):
    """Get email sending logs"""
    db = get_database()
    
    query = {}
    if email_type:
        query["type"] = email_type
    
    logs = await db.email_logs.find(query, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    return {"logs": logs}
