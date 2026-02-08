"""
AI Credits API Router
"""
from fastapi import APIRouter, HTTPException, Request

from database import get_database
from dependencies import get_current_user
from credits import (
    get_user_credits, use_credits, add_extra_credits, 
    check_and_reset_credits, get_credit_costs, get_plan_credits
)

router = APIRouter(prefix="/credits", tags=["Credits"])

@router.get("")
async def get_credits(request: Request):
    """Get user's credit information"""
    db = get_database()
    user = await get_current_user(request, db)
    
    credits = await check_and_reset_credits(user.user_id)
    return credits

@router.get("/costs")
async def get_feature_costs():
    """Get credit costs for all features"""
    return {
        "costs": get_credit_costs(),
        "plan_allocations": get_plan_credits()
    }

@router.post("/use")
async def use_feature_credits(
    feature: str,
    amount: int = None,
    request: Request = None
):
    """Use credits for a feature"""
    db = get_database()
    user = await get_current_user(request, db)
    
    success, result = await use_credits(user.user_id, feature, amount)
    
    if not success:
        raise HTTPException(status_code=402, detail=result)
    
    return result

@router.get("/history")
async def get_credit_history(limit: int = 50, request: Request = None):
    """Get user's credit usage history"""
    db = get_database()
    user = await get_current_user(request, db)
    
    credits = await db.ai_credits.find_one(
        {"user_id": user.user_id},
        {"_id": 0, "usage_history": {"$slice": -limit}}
    )
    
    return {
        "history": credits.get("usage_history", []) if credits else []
    }
