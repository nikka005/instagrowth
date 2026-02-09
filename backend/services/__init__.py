import os
import logging
import asyncio
import uuid
import resend
from typing import Dict, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@instagrowth.app')

# AI Timeout configuration
AI_TIMEOUT_SHORT = 30   # For simple operations (metrics, DM replies)
AI_TIMEOUT_MEDIUM = 60  # For standard operations (content, audits)
AI_TIMEOUT_LONG = 120   # For complex operations (growth plans)

async def get_resend_api_key():
    """Get Resend API key from env or database settings"""
    global RESEND_API_KEY
    if RESEND_API_KEY and RESEND_API_KEY != "re_placeholder_key":
        return RESEND_API_KEY
    
    # Try to get from database
    try:
        from database import get_database
        db = get_database()
        settings = await db.system_settings.find_one({"setting_id": "global"}, {"_id": 0})
        if settings and settings.get("resend_api_key"):
            return settings.get("resend_api_key")
    except Exception as e:
        logger.warning(f"Could not get Resend API key from database: {e}")
    
    return RESEND_API_KEY

async def send_email(to_email: str, subject: str, html_content: str):
    api_key = await get_resend_api_key()
    
    if not api_key or api_key == "re_placeholder_key":
        logger.warning(f"Email not sent (no API key configured): {subject} to {to_email}")
        return {"status": "skipped", "message": "Email service not configured. Set RESEND_API_KEY in System Settings"}
    
    resend.api_key = api_key
    
    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {"status": "success", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {"status": "error", "message": str(e)}

async def generate_ai_content(prompt: str, system_message: str, timeout_seconds: int = AI_TIMEOUT_MEDIUM) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"instagrowth_{uuid.uuid4().hex[:8]}",
        system_message=system_message
    ).with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=prompt)
    
    try:
        response = await asyncio.wait_for(
            chat.send_message(user_message),
            timeout=timeout_seconds
        )
        return response
    except asyncio.TimeoutError:
        logger.error(f"AI generation timed out after {timeout_seconds}s")
        raise HTTPException(
            status_code=504, 
            detail=f"AI generation timed out. Please try again or simplify your request."
        )

async def estimate_instagram_metrics(username: str, niche: str) -> Dict[str, Any]:
    system_message = """You are an Instagram analytics expert. Based on the username and niche, 
    provide realistic estimates for Instagram account metrics. Return JSON with:
    - estimated_followers (int)
    - estimated_engagement_rate (float, 1-10%)
    - estimated_reach (int)
    - posting_frequency (string)
    - best_posting_time (string with timezone)
    - growth_potential (string: low/medium/high)
    Be realistic based on typical performance in the niche."""
    
    prompt = f"Estimate Instagram metrics for @{username} in the {niche} niche."
    
    try:
        response = await generate_ai_content(prompt, system_message, timeout_seconds=30)
        import json
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"AI metrics estimation error: {e}")
        return {
            "estimated_followers": 5000,
            "estimated_engagement_rate": 3.5,
            "estimated_reach": 2000,
            "posting_frequency": "3x per week",
            "best_posting_time": "9 AM - 12 PM EST",
            "growth_potential": "medium"
        }

async def generate_posting_recommendations(username: str, niche: str, current_metrics: Dict) -> Dict[str, Any]:
    system_message = """You are an Instagram growth strategist. Analyze the account and provide 
    optimal posting time recommendations. Return JSON with:
    - best_times (array of {day: string, times: array of strings})
    - frequency (string, e.g., "5-7 posts per week")
    - content_mix (object with percentages for reels, posts, stories)
    - peak_engagement_windows (array of time ranges)
    - avoid_times (array of times to avoid posting)
    - reasoning (string explaining the recommendations)"""
    
    prompt = f"""Provide posting recommendations for:
    Username: @{username}
    Niche: {niche}
    Current followers: {current_metrics.get('estimated_followers', 'Unknown')}
    Current engagement: {current_metrics.get('estimated_engagement_rate', 'Unknown')}%"""
    
    try:
        response = await generate_ai_content(prompt, system_message, timeout_seconds=45)
        import json
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"Posting recommendations error: {e}")
        return {
            "best_times": [
                {"day": "Monday", "times": ["9:00 AM", "12:00 PM", "6:00 PM"]},
                {"day": "Wednesday", "times": ["9:00 AM", "12:00 PM", "7:00 PM"]},
                {"day": "Friday", "times": ["10:00 AM", "2:00 PM", "8:00 PM"]}
            ],
            "frequency": "5-7 posts per week",
            "content_mix": {"reels": 60, "posts": 25, "stories": 15},
            "peak_engagement_windows": ["9-11 AM", "7-9 PM"],
            "avoid_times": ["2-5 AM", "During major events"],
            "reasoning": "Based on typical engagement patterns in your niche"
        }

async def generate_dm_reply(message: str, context: str, tone: str = "friendly") -> str:
    system_message = f"""You are an Instagram account manager. Generate a {tone}, professional 
    DM reply. Keep it natural, avoid sounding robotic. Include appropriate emojis.
    Context: {context}
    Return ONLY the reply message, nothing else."""
    
    prompt = f"Generate a reply to this DM: \"{message}\""
    
    try:
        response = await generate_ai_content(prompt, system_message, timeout_seconds=30)
        return response.strip()
    except Exception as e:
        logger.error(f"DM reply generation error: {e}")
        return "Thanks for reaching out! I'll get back to you soon."

async def analyze_competitor(competitor_username: str, niche: str) -> Dict[str, Any]:
    system_message = """You are an Instagram competitive analyst. Analyze the competitor and provide insights.
    Return JSON with:
    - estimated_followers (int)
    - estimated_engagement_rate (float)
    - content_strategy (string)
    - posting_frequency (string)
    - strengths (array of strings)
    - weaknesses (array of strings)
    - content_types (object with percentages)
    - hashtag_strategy (string)
    - audience_demographics (string)"""
    
    prompt = f"Analyze Instagram competitor @{competitor_username} in the {niche} niche."
    
    try:
        response = await generate_ai_content(prompt, system_message, timeout_seconds=45)
        import json
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        logger.error(f"Competitor analysis error: {e}")
        return {
            "estimated_followers": 10000,
            "estimated_engagement_rate": 4.0,
            "content_strategy": "Consistent posting with trending content",
            "posting_frequency": "Daily",
            "strengths": ["Strong visual brand", "Engaging captions"],
            "weaknesses": ["Limited story engagement", "Inconsistent reels"],
            "content_types": {"reels": 50, "posts": 30, "stories": 20},
            "hashtag_strategy": "Mix of branded and trending hashtags",
            "audience_demographics": "18-34 year olds interested in " + niche
        }
