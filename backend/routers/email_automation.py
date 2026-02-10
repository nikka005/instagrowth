"""
Email Automation System - Automated emails for user lifecycle
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from datetime import datetime, timezone, timedelta
import uuid
import asyncio

from database import get_database
from services import send_email
from routers.admin_panel_auth import verify_admin_token

router = APIRouter(prefix="/email-automation", tags=["Email Automation"])

# Email Templates - Configurable
EMAIL_TEMPLATES = {
    "welcome": {
        "name": "Welcome Email",
        "subject": "Welcome to InstaGrowth OS! 🚀",
        "enabled": True,
        "trigger": "user_registration",
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
        "name": "Subscription Activated",
        "subject": "Your {plan} Plan is Now Active! 🎉",
        "enabled": True,
        "trigger": "subscription_created",
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
    "renewal_reminder_7day": {
        "name": "7-Day Renewal Reminder",
        "subject": "⏰ Your Subscription Renews in 7 Days",
        "enabled": True,
        "trigger": "scheduled",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Renewal Reminder</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your subscription renews in 7 days</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Just a friendly reminder that your <strong>{plan}</strong> subscription will automatically renew on <strong>{renewal_date}</strong>.</p>
                
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <p style="margin: 0;"><strong>Plan:</strong> {plan}</p>
                    <p style="margin: 8px 0 0 0;"><strong>Amount:</strong> ${amount}/month</p>
                    <p style="margin: 8px 0 0 0;"><strong>Renewal Date:</strong> {renewal_date}</p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">No action needed if you want to continue enjoying all features!</p>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: rgba(255,255,255,0.1); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid rgba(255,255,255,0.2);">Manage Subscription</a>
                </div>
            </div>
        </div>
        """
    },
    "renewal_reminder_3day": {
        "name": "3-Day Renewal Reminder",
        "subject": "⚡ Your Subscription Renews in 3 Days",
        "enabled": True,
        "trigger": "scheduled",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Renewal in 3 Days</h1>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Your <strong>{plan}</strong> subscription renews in <strong>3 days</strong> on {renewal_date}.</p>
                
                <div style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <p style="margin: 0;"><strong>Amount:</strong> ${amount}</p>
                    <p style="margin: 8px 0 0 0;"><strong>Payment Method:</strong> Card ending in •••• {last_four}</p>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Manage Billing</a>
                </div>
            </div>
        </div>
        """
    },
    "credits_low": {
        "name": "Low Credits Alert",
        "subject": "⚠️ Your AI Credits Are Running Low ({remaining} left)",
        "enabled": True,
        "trigger": "credit_threshold",
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
                    <li>Refer friends and earn bonus credits!</li>
                </ul>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{billing_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Upgrade Plan</a>
                </div>
            </div>
        </div>
        """
    },
    "subscription_cancelled": {
        "name": "Subscription Cancelled",
        "subject": "We're Sorry to See You Go 😢",
        "enabled": True,
        "trigger": "subscription_cancelled",
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
    "weekly_digest": {
        "name": "Weekly Digest",
        "subject": "📊 Your Weekly Instagram Growth Report",
        "enabled": True,
        "trigger": "scheduled_weekly",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Weekly Growth Report</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{week_range}</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Here's your Instagram growth summary for this week:</p>
                
                <table style="width: 100%; margin: 24px 0; border-spacing: 8px;">
                    <tr>
                        <td style="background: rgba(99, 102, 241, 0.1); border-radius: 12px; padding: 20px; text-align: center; width: 50%;">
                            <p style="margin: 0; font-size: 28px; font-weight: bold; color: #a5b4fc;">{audits_run}</p>
                            <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Audits Run</p>
                        </td>
                        <td style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 20px; text-align: center; width: 50%;">
                            <p style="margin: 0; font-size: 28px; font-weight: bold; color: #6ee7b7;">{content_created}</p>
                            <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Content Created</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background: rgba(245, 158, 11, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                            <p style="margin: 0; font-size: 28px; font-weight: bold; color: #fcd34d;">{credits_used}</p>
                            <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Credits Used</p>
                        </td>
                        <td style="background: rgba(236, 72, 153, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                            <p style="margin: 0; font-size: 28px; font-weight: bold; color: #f9a8d4;">{credits_remaining}</p>
                            <p style="margin: 4px 0 0 0; font-size: 14px; color: #94a3b8;">Credits Left</p>
                        </td>
                    </tr>
                </table>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">View Full Dashboard</a>
                </div>
            </div>
        </div>
        """
    },
    "inactivity_reminder": {
        "name": "Inactivity Reminder",
        "subject": "We Miss You! 👋 Your AI Credits Are Waiting",
        "enabled": True,
        "trigger": "scheduled",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">We Miss You!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your AI credits are waiting to be used</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">We noticed you haven't used InstaGrowth OS in a while. You still have <strong>{credits_remaining} AI credits</strong> ready to use!</p>
                
                <div style="background: rgba(139, 92, 246, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0;">
                    <h3 style="margin: 0 0 16px 0; color: #c4b5fd;">Quick Ideas to Get Started:</h3>
                    <ul style="margin: 0; padding-left: 20px; line-height: 2;">
                        <li>Run a fresh audit on your accounts</li>
                        <li>Generate engaging content ideas</li>
                        <li>Create a new growth plan</li>
                        <li>Analyze your competitors</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{dashboard_url}" style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">Return to Dashboard</a>
                </div>
            </div>
        </div>
        """
    },
    "referral_reward": {
        "name": "Referral Reward",
        "subject": "🎉 You Earned {credits} Bonus Credits!",
        "enabled": True,
        "trigger": "referral_signup",
        "template": """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: white; border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">Referral Reward!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">+{credits} bonus credits added</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Great news! Someone signed up using your referral link. We've added <strong>{credits} bonus credits</strong> to your account!</p>
                
                <div style="background: rgba(16, 185, 129, 0.1); border-radius: 12px; padding: 24px; margin: 24px 0; text-align: center;">
                    <p style="margin: 0; font-size: 48px; font-weight: bold; color: #6ee7b7;">+{credits}</p>
                    <p style="margin: 8px 0 0 0; color: #94a3b8;">Bonus Credits Added</p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">Keep sharing your referral link to earn more credits! Remember:</p>
                <ul style="line-height: 2;">
                    <li>50 credits for each friend who signs up</li>
                    <li>20% commission when they subscribe</li>
                </ul>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{referrals_url}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">View Referral Dashboard</a>
                </div>
            </div>
        </div>
        """
    }
}

FRONTEND_URL = "https://email-send-fail.preview.emergentagent.com"

async def send_automated_email(email_type: str, recipient_email: str, data: dict):
    """Send an automated email based on template type"""
    if email_type not in EMAIL_TEMPLATES:
        raise ValueError(f"Unknown email type: {email_type}")
    
    template_config = EMAIL_TEMPLATES[email_type]
    
    # Check if template is enabled
    if not template_config.get("enabled", True):
        return False
    
    # Check if user has opted out (from database)
    db = get_database()
    prefs = await db.email_preferences.find_one({"email": recipient_email})
    if prefs and not prefs.get(email_type, True):
        return False
    
    subject = template_config["subject"].format(**data)
    html = template_config["template"].format(**data)
    
    try:
        result = await send_email(recipient_email, subject, html)
        
        # Check if email was actually sent
        if result.get("status") == "success":
            await db.email_logs.insert_one({
                "email_id": f"EMAIL-{uuid.uuid4().hex[:12]}",
                "type": email_type,
                "recipient": recipient_email,
                "subject": subject,
                "status": "sent",
                "resend_id": result.get("email_id"),
                "sent_at": datetime.now(timezone.utc).isoformat()
            })
            return True
        elif result.get("status") == "skipped":
            await db.email_logs.insert_one({
                "email_id": f"EMAIL-{uuid.uuid4().hex[:12]}",
                "type": email_type,
                "recipient": recipient_email,
                "subject": subject,
                "status": "skipped",
                "error": result.get("message"),
                "attempted_at": datetime.now(timezone.utc).isoformat()
            })
            return False
        else:
            # Status is "error"
            await db.email_logs.insert_one({
                "email_id": f"EMAIL-{uuid.uuid4().hex[:12]}",
                "type": email_type,
                "recipient": recipient_email,
                "subject": subject,
                "status": "failed",
                "error": result.get("message"),
                "attempted_at": datetime.now(timezone.utc).isoformat()
            })
            return False
    except Exception as e:
        # Log failure
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


# ==================== TRIGGER FUNCTIONS ====================

async def trigger_welcome_email(user_id: str, name: str, email: str):
    """Trigger welcome email for new user"""
    await send_automated_email("welcome", email, {
        "name": name,
        "dashboard_url": f"{FRONTEND_URL}/dashboard"
    })

async def trigger_subscription_email(user_id: str, plan: str, account_limit: int, ai_credits: int, next_billing_date: str):
    """Trigger subscription activated email"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
    if user:
        await send_automated_email("subscription_activated", user["email"], {
            "name": user.get("name", "there"),
            "plan": plan,
            "account_limit": str(account_limit),
            "ai_credits": str(ai_credits),
            "next_billing_date": next_billing_date,
            "dashboard_url": f"{FRONTEND_URL}/dashboard"
        })

async def trigger_cancellation_email(user_id: str, end_date: str):
    """Trigger subscription cancelled email"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
    if user:
        await send_automated_email("subscription_cancelled", user["email"], {
            "name": user.get("name", "there"),
            "end_date": end_date,
            "billing_url": f"{FRONTEND_URL}/billing"
        })

async def trigger_low_credits_email(user_id: str, remaining: int, total: int, reset_date: str):
    """Trigger low credits alert email"""
    db = get_database()
    
    # Check if we already sent this alert recently (within 24 hours)
    recent = await db.email_logs.find_one({
        "type": "credits_low",
        "recipient_user_id": user_id,
        "sent_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}
    })
    if recent:
        return False
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
    if user:
        await send_automated_email("credits_low", user["email"], {
            "name": user.get("name", "there"),
            "remaining": str(remaining),
            "used": str(total - remaining),
            "total": str(total),
            "reset_date": reset_date,
            "billing_url": f"{FRONTEND_URL}/billing"
        })
        
        # Mark that we sent this alert
        await db.email_logs.update_one(
            {"type": "credits_low", "recipient_user_id": user_id},
            {"$set": {"last_alert": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

async def trigger_referral_reward_email(user_id: str, credits: int):
    """Trigger referral reward notification email"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
    if user:
        await send_automated_email("referral_reward", user["email"], {
            "name": user.get("name", "there"),
            "credits": str(credits),
            "referrals_url": f"{FRONTEND_URL}/referrals"
        })


# ==================== SCHEDULED TASKS ====================

async def run_renewal_reminders():
    """Check for upcoming renewals and send reminder emails"""
    db = get_database()
    now = datetime.now(timezone.utc)
    
    results = {"7_day": 0, "3_day": 0}
    
    # 7-day reminders
    seven_days = now + timedelta(days=7)
    subs_7day = await db.subscriptions.find({
        "status": "active",
        "renewal_reminder_7d_sent": {"$ne": True},
        "current_period_end": {
            "$gte": (seven_days - timedelta(hours=12)).isoformat(),
            "$lte": (seven_days + timedelta(hours=12)).isoformat()
        }
    }).to_list(100)
    
    for sub in subs_7day:
        user = await db.users.find_one({"user_id": sub["user_id"]}, {"_id": 0})
        if user:
            success = await send_automated_email("renewal_reminder_7day", user["email"], {
                "name": user.get("name", "there"),
                "plan": sub.get("plan_name", "Pro"),
                "amount": str(sub.get("amount", 49)),
                "renewal_date": sub.get("current_period_end", "soon")[:10],
                "billing_url": f"{FRONTEND_URL}/billing"
            })
            if success:
                await db.subscriptions.update_one(
                    {"subscription_id": sub["subscription_id"]},
                    {"$set": {"renewal_reminder_7d_sent": True}}
                )
                results["7_day"] += 1
    
    # 3-day reminders
    three_days = now + timedelta(days=3)
    subs_3day = await db.subscriptions.find({
        "status": "active",
        "renewal_reminder_3d_sent": {"$ne": True},
        "current_period_end": {
            "$gte": (three_days - timedelta(hours=12)).isoformat(),
            "$lte": (three_days + timedelta(hours=12)).isoformat()
        }
    }).to_list(100)
    
    for sub in subs_3day:
        user = await db.users.find_one({"user_id": sub["user_id"]}, {"_id": 0})
        if user:
            success = await send_automated_email("renewal_reminder_3day", user["email"], {
                "name": user.get("name", "there"),
                "plan": sub.get("plan_name", "Pro"),
                "amount": str(sub.get("amount", 49)),
                "renewal_date": sub.get("current_period_end", "soon")[:10],
                "last_four": "4242",
                "billing_url": f"{FRONTEND_URL}/billing"
            })
            if success:
                await db.subscriptions.update_one(
                    {"subscription_id": sub["subscription_id"]},
                    {"$set": {"renewal_reminder_3d_sent": True}}
                )
                results["3_day"] += 1
    
    return results

async def run_low_credits_check():
    """Check for users with low credits and send alerts"""
    db = get_database()
    
    # Find users with less than 20% credits remaining
    credits_list = await db.ai_credits.find({}).to_list(1000)
    
    sent_count = 0
    for credits in credits_list:
        if credits["total_credits"] > 0:
            percentage = (credits["remaining_credits"] / credits["total_credits"]) * 100
            if percentage < 20 and credits["remaining_credits"] > 0:
                # Calculate reset date (1st of next month)
                now = datetime.now(timezone.utc)
                if now.month == 12:
                    reset_date = f"January 1, {now.year + 1}"
                else:
                    reset_date = f"{['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][now.month]} 1, {now.year}"
                
                await trigger_low_credits_email(
                    credits["user_id"],
                    credits["remaining_credits"],
                    credits["total_credits"],
                    reset_date
                )
                sent_count += 1
    
    return {"sent": sent_count}

async def run_inactivity_check():
    """Check for inactive users and send re-engagement emails"""
    db = get_database()
    
    # Find users who haven't logged in for 7+ days
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    
    inactive_users = await db.users.find({
        "last_login": {"$lt": seven_days_ago},
        "inactivity_email_sent": {"$ne": True}
    }).to_list(100)
    
    sent_count = 0
    for user in inactive_users:
        # Get their credits
        credits = await db.ai_credits.find_one({"user_id": user["user_id"]})
        credits_remaining = credits["remaining_credits"] if credits else 0
        
        success = await send_automated_email("inactivity_reminder", user["email"], {
            "name": user.get("name", "there"),
            "credits_remaining": str(credits_remaining),
            "dashboard_url": f"{FRONTEND_URL}/dashboard"
        })
        
        if success:
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"inactivity_email_sent": True}}
            )
            sent_count += 1
    
    return {"sent": sent_count}

async def run_weekly_digest():
    """Send weekly digest emails to active users"""
    db = get_database()
    
    # Get date range
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=7)).strftime("%b %d")
    week_end = now.strftime("%b %d, %Y")
    week_range = f"{week_start} - {week_end}"
    
    # Find users who opted in to weekly digests
    users = await db.users.find({
        "weekly_digest_enabled": {"$ne": False}
    }).to_list(1000)
    
    sent_count = 0
    for user in users:
        # Get user's stats for the week
        user_id = user["user_id"]
        week_ago = (now - timedelta(days=7)).isoformat()
        
        audits_count = await db.audits.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        })
        
        content_count = await db.content_items.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        })
        
        credits = await db.ai_credits.find_one({"user_id": user_id})
        credits_used = credits.get("used_credits", 0) if credits else 0
        credits_remaining = credits.get("remaining_credits", 0) if credits else 0
        
        success = await send_automated_email("weekly_digest", user["email"], {
            "name": user.get("name", "there"),
            "week_range": week_range,
            "audits_run": str(audits_count),
            "content_created": str(content_count),
            "credits_used": str(credits_used),
            "credits_remaining": str(credits_remaining),
            "dashboard_url": f"{FRONTEND_URL}/dashboard"
        })
        
        if success:
            sent_count += 1
    
    return {"sent": sent_count}


# ==================== API ENDPOINTS ====================

@router.post("/run-scheduled-tasks")
async def run_all_scheduled_tasks(request: Request = None):
    """Run all scheduled email tasks (call this from cron job)"""
    results = {
        "renewals": await run_renewal_reminders(),
        "low_credits": await run_low_credits_check(),
        "inactivity": await run_inactivity_check()
    }
    return results

@router.post("/run-weekly-digest")
async def trigger_weekly_digest(request: Request = None):
    """Run weekly digest emails (call this on Sundays)"""
    return await run_weekly_digest()

@router.get("/templates")
async def get_email_templates(request: Request = None):
    """Get all available email templates"""
    templates = []
    for key, config in EMAIL_TEMPLATES.items():
        templates.append({
            "id": key,
            "name": config["name"],
            "subject": config["subject"],
            "enabled": config.get("enabled", True),
            "trigger": config.get("trigger", "manual")
        })
    return {"templates": templates}

@router.get("/templates/{template_id}")
async def get_email_template(template_id: str, request: Request = None):
    """Get a specific email template"""
    if template_id not in EMAIL_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = EMAIL_TEMPLATES[template_id]
    return {
        "id": template_id,
        "name": template["name"],
        "subject": template["subject"],
        "enabled": template.get("enabled", True),
        "trigger": template.get("trigger", "manual"),
        "template_html": template["template"]
    }

@router.put("/templates/{template_id}/toggle")
async def toggle_email_template(template_id: str, enabled: bool, request: Request = None):
    """Enable or disable an email template"""
    await verify_admin_token(request)
    
    if template_id not in EMAIL_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    EMAIL_TEMPLATES[template_id]["enabled"] = enabled
    
    # Also persist to database
    db = get_database()
    await db.email_template_settings.update_one(
        {"template_id": template_id},
        {"$set": {"enabled": enabled, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"template_id": template_id, "enabled": enabled}

@router.post("/send-test")
async def send_test_email(template_id: str, recipient: str, request: Request = None):
    """Send a test email (admin only)"""
    await verify_admin_token(request)
    
    if template_id not in EMAIL_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Use placeholder data
    test_data = {
        "name": "Test User",
        "dashboard_url": f"{FRONTEND_URL}/dashboard",
        "billing_url": f"{FRONTEND_URL}/billing",
        "referrals_url": f"{FRONTEND_URL}/referrals",
        "plan": "Pro",
        "account_limit": "5",
        "ai_credits": "100",
        "next_billing_date": "March 1, 2025",
        "renewal_date": "March 1, 2025",
        "amount": "49",
        "last_four": "4242",
        "end_date": "March 1, 2025",
        "remaining": "5",
        "used": "95",
        "total": "100",
        "reset_date": "March 1, 2025",
        "credits": "50",
        "credits_remaining": "50",
        "week_range": "Feb 1 - Feb 8, 2025",
        "audits_run": "3",
        "content_created": "12",
        "credits_used": "45"
    }
    
    success = await send_automated_email(template_id, recipient, test_data)
    return {"success": success, "template_id": template_id, "recipient": recipient}

@router.get("/logs")
async def get_email_logs(
    limit: int = 50, 
    email_type: str = None, 
    status: str = None,
    request: Request = None
):
    """Get email sending logs (admin only)"""
    await verify_admin_token(request)
    
    db = get_database()
    query = {}
    if email_type:
        query["type"] = email_type
    if status:
        query["status"] = status
    
    logs = await db.email_logs.find(query, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    
    # Get stats
    total_sent = await db.email_logs.count_documents({"status": "sent"})
    total_failed = await db.email_logs.count_documents({"status": "failed"})
    
    return {
        "logs": logs,
        "stats": {
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": round((total_sent / max(total_sent + total_failed, 1)) * 100, 1)
        }
    }

@router.get("/stats")
async def get_email_stats(request: Request = None):
    """Get email automation statistics"""
    await verify_admin_token(request)
    
    db = get_database()
    
    # Get stats by type
    pipeline = [
        {"$group": {
            "_id": "$type",
            "total": {"$sum": 1},
            "sent": {"$sum": {"$cond": [{"$eq": ["$status", "sent"]}, 1, 0]}},
            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
        }}
    ]
    
    by_type = await db.email_logs.aggregate(pipeline).to_list(20)
    
    # Get recent activity (last 7 days)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_sent = await db.email_logs.count_documents({
        "status": "sent",
        "sent_at": {"$gte": seven_days_ago}
    })
    
    return {
        "by_type": by_type,
        "recent_7_days": recent_sent,
        "templates_count": len(EMAIL_TEMPLATES)
    }

