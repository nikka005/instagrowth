from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from models import ABTest, ABTestCreate
from database import get_database
from dependencies import get_current_user

router = APIRouter(prefix="/ab-tests", tags=["A/B Testing"])

@router.post("", response_model=ABTest)
async def create_ab_test(data: ABTestCreate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    account = await db.instagram_accounts.find_one(
        {"account_id": data.account_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    test_id = f"test_{uuid.uuid4().hex[:12]}"
    test_doc = {
        "test_id": test_id, "account_id": data.account_id, "user_id": user.user_id,
        "content_type": data.content_type, "variant_a": data.variant_a, "variant_b": data.variant_b,
        "votes_a": 0, "votes_b": 0, "winner": None, "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ab_tests.insert_one(test_doc)
    return ABTest(**test_doc)

@router.get("")
async def get_ab_tests(account_id: Optional[str] = None, status: Optional[str] = None, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if account_id:
        query["account_id"] = account_id
    if status:
        query["status"] = status
    
    tests = await db.ab_tests.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return tests

@router.get("/{test_id}")
async def get_ab_test(test_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    test = await db.ab_tests.find_one({"test_id": test_id, "user_id": user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    return test

@router.post("/{test_id}/vote")
async def vote_ab_test(test_id: str, variant: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    test = await db.ab_tests.find_one({"test_id": test_id, "user_id": user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    if test["status"] != "active":
        raise HTTPException(status_code=400, detail="Test is no longer active")
    
    if variant not in ["a", "b"]:
        raise HTTPException(status_code=400, detail="Invalid variant. Use 'a' or 'b'")
    
    update_field = "votes_a" if variant == "a" else "votes_b"
    await db.ab_tests.update_one({"test_id": test_id}, {"$inc": {update_field: 1}})
    
    updated_test = await db.ab_tests.find_one({"test_id": test_id}, {"_id": 0})
    return {"votes_a": updated_test["votes_a"], "votes_b": updated_test["votes_b"]}

@router.post("/{test_id}/complete")
async def complete_ab_test(test_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    test = await db.ab_tests.find_one({"test_id": test_id, "user_id": user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    winner = "a" if test["votes_a"] > test["votes_b"] else ("b" if test["votes_b"] > test["votes_a"] else "tie")
    
    await db.ab_tests.update_one(
        {"test_id": test_id},
        {"$set": {"status": "completed", "winner": winner}}
    )
    return {"winner": winner, "votes_a": test["votes_a"], "votes_b": test["votes_b"]}
