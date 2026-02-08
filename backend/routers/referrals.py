"""
Referral/Affiliate System Router
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from database import get_database
from dependencies import get_current_user
from routers.admin_panel_auth import verify_admin_token
from credits import add_extra_credits

router = APIRouter(prefix="/referrals", tags=["Referrals"])

# Referral rewards configuration
REFERRAL_CONFIG = {
    "referrer_reward_credits": 50,  # Credits for the person who referred
    "referee_reward_credits": 25,   # Credits for the new user who signed up
    "commission_percentage": 20,    # Percentage commission on first payment
    "min_payout_amount": 50,        # Minimum amount for payout
}

# ==================== USER ENDPOINTS ====================

@router.get("/code")
async def get_or_create_referral_code(request: Request):
    """Get or create user's referral code"""
    db = get_database()
    user = await get_current_user(request, db)
    
    # Check if user already has a referral code
    referral = await db.referral_codes.find_one({"user_id": user.user_id}, {"_id": 0})
    
    if not referral:
        # Create new referral code
        code = f"REF-{user.user_id[-6:].upper()}-{uuid.uuid4().hex[:4].upper()}"
        referral = {
            "user_id": user.user_id,
            "code": code,
            "clicks": 0,
            "signups": 0,
            "conversions": 0,
            "total_earnings": 0,
            "pending_earnings": 0,
            "paid_out": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.referral_codes.insert_one(referral)
        referral.pop("_id", None)
    
    return {
        "code": referral["code"],
        "stats": {
            "clicks": referral["clicks"],
            "signups": referral["signups"],
            "conversions": referral["conversions"],
            "total_earnings": referral["total_earnings"],
            "pending_earnings": referral["pending_earnings"],
            "paid_out": referral["paid_out"]
        },
        "rewards": REFERRAL_CONFIG
    }

@router.get("/stats")
async def get_referral_stats(request: Request):
    """Get detailed referral statistics"""
    db = get_database()
    user = await get_current_user(request, db)
    
    referral = await db.referral_codes.find_one({"user_id": user.user_id}, {"_id": 0})
    if not referral:
        return {"message": "No referral code yet", "stats": None}
    
    # Get recent referrals
    recent_referrals = await db.referrals.find(
        {"referrer_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return {
        "code": referral["code"],
        "overview": {
            "clicks": referral["clicks"],
            "signups": referral["signups"],
            "conversions": referral["conversions"],
            "conversion_rate": round((referral["conversions"] / max(referral["signups"], 1)) * 100, 1)
        },
        "earnings": {
            "total": referral["total_earnings"],
            "pending": referral["pending_earnings"],
            "paid_out": referral["paid_out"],
            "available_for_payout": max(0, referral["pending_earnings"] - REFERRAL_CONFIG["min_payout_amount"])
        },
        "recent_referrals": recent_referrals,
        "rewards": REFERRAL_CONFIG
    }

@router.post("/track-click")
async def track_referral_click(code: str):
    """Track a referral link click"""
    db = get_database()
    
    result = await db.referral_codes.update_one(
        {"code": code, "is_active": True},
        {"$inc": {"clicks": 1}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    return {"tracked": True}

@router.post("/request-payout")
async def request_payout(request: Request):
    """Request payout of pending earnings"""
    db = get_database()
    user = await get_current_user(request, db)
    
    referral = await db.referral_codes.find_one({"user_id": user.user_id})
    if not referral:
        raise HTTPException(status_code=404, detail="No referral account found")
    
    if referral["pending_earnings"] < REFERRAL_CONFIG["min_payout_amount"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum payout is ${REFERRAL_CONFIG['min_payout_amount']}"
        )
    
    payout_id = f"PAYOUT-{uuid.uuid4().hex[:12].upper()}"
    payout_amount = referral["pending_earnings"]
    
    # Create payout request
    payout = {
        "payout_id": payout_id,
        "user_id": user.user_id,
        "amount": payout_amount,
        "status": "pending",
        "payment_method": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.referral_payouts.insert_one(payout)
    
    # Update referral stats
    await db.referral_codes.update_one(
        {"user_id": user.user_id},
        {
            "$set": {"pending_earnings": 0},
            "$inc": {"paid_out": payout_amount}
        }
    )
    
    return {
        "payout_id": payout_id,
        "amount": payout_amount,
        "message": "Payout request submitted. You'll receive payment within 5-7 business days."
    }

# ==================== INTERNAL FUNCTIONS ====================

async def process_referral_signup(referee_id: str, referee_email: str, referral_code: str):
    """Process a successful referral signup"""
    db = get_database()
    
    # Find the referrer
    referrer_doc = await db.referral_codes.find_one({"code": referral_code, "is_active": True})
    if not referrer_doc:
        return None
    
    referrer_id = referrer_doc["user_id"]
    
    # Create referral record
    referral = {
        "referral_id": f"REF-{uuid.uuid4().hex[:12]}",
        "referrer_id": referrer_id,
        "referee_id": referee_id,
        "referee_email": referee_email,
        "referral_code": referral_code,
        "status": "signed_up",
        "referrer_reward_given": False,
        "referee_reward_given": False,
        "commission_earned": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.referrals.insert_one(referral)
    
    # Update referral code stats
    await db.referral_codes.update_one(
        {"code": referral_code},
        {"$inc": {"signups": 1}}
    )
    
    # Give credits to referee (new user)
    await add_extra_credits(
        referee_id, 
        REFERRAL_CONFIG["referee_reward_credits"],
        "Referral bonus - Welcome gift"
    )
    await db.referrals.update_one(
        {"referral_id": referral["referral_id"]},
        {"$set": {"referee_reward_given": True}}
    )
    
    # Give credits to referrer
    await add_extra_credits(
        referrer_id, 
        REFERRAL_CONFIG["referrer_reward_credits"],
        f"Referral bonus - {referee_email}"
    )
    await db.referrals.update_one(
        {"referral_id": referral["referral_id"]},
        {"$set": {"referrer_reward_given": True}}
    )
    
    return referral

async def process_referral_conversion(referee_id: str, payment_amount: float):
    """Process when a referred user makes their first payment"""
    db = get_database()
    
    # Find the referral
    referral = await db.referrals.find_one(
        {"referee_id": referee_id, "status": "signed_up"}
    )
    
    if not referral:
        return None
    
    # Calculate commission
    commission = payment_amount * (REFERRAL_CONFIG["commission_percentage"] / 100)
    
    # Update referral
    await db.referrals.update_one(
        {"referral_id": referral["referral_id"]},
        {"$set": {
            "status": "converted",
            "commission_earned": commission,
            "converted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update referrer's earnings
    await db.referral_codes.update_one(
        {"user_id": referral["referrer_id"]},
        {
            "$inc": {
                "conversions": 1,
                "total_earnings": commission,
                "pending_earnings": commission
            }
        }
    )
    
    return {"commission": commission, "referrer_id": referral["referrer_id"]}

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/overview")
async def admin_referral_overview(request: Request):
    """Get referral system overview (admin)"""
    db = get_database()
    await verify_admin_token(request)
    
    total_referrals = await db.referrals.count_documents({})
    converted_referrals = await db.referrals.count_documents({"status": "converted"})
    
    # Sum total earnings
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total_earnings"}}}
    ]
    earnings_result = await db.referral_codes.aggregate(pipeline).to_list(1)
    total_earnings = earnings_result[0]["total"] if earnings_result else 0
    
    # Pending payouts
    pending_payouts = await db.referral_payouts.count_documents({"status": "pending"})
    
    # Top referrers
    top_referrers = await db.referral_codes.find(
        {},
        {"_id": 0}
    ).sort("total_earnings", -1).limit(10).to_list(10)
    
    return {
        "total_referrals": total_referrals,
        "converted": converted_referrals,
        "conversion_rate": round((converted_referrals / max(total_referrals, 1)) * 100, 1),
        "total_earnings_paid": total_earnings,
        "pending_payouts": pending_payouts,
        "top_referrers": top_referrers,
        "config": REFERRAL_CONFIG
    }

@router.get("/admin/payouts")
async def admin_get_payouts(status: str = None, request: Request = None):
    """Get all payout requests (admin)"""
    db = get_database()
    await verify_admin_token(request)
    
    query = {}
    if status:
        query["status"] = status
    
    payouts = await db.referral_payouts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    return {"payouts": payouts}

@router.put("/admin/payouts/{payout_id}")
async def admin_process_payout(
    payout_id: str,
    status: str,
    notes: str = None,
    request: Request = None
):
    """Process a payout request (admin)"""
    db = get_database()
    await verify_admin_token(request)
    
    if status not in ["approved", "paid", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    update_data = {
        "status": status,
        "processed_at": datetime.now(timezone.utc).isoformat()
    }
    if notes:
        update_data["notes"] = notes
    
    result = await db.referral_payouts.update_one(
        {"payout_id": payout_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    return {"message": f"Payout {status}"}
