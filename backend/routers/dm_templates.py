from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import re

from models import DMTemplate, DMTemplateCreate
from database import get_database
from dependencies import get_current_user, check_ai_usage, increment_ai_usage
from services import generate_dm_reply

router = APIRouter(prefix="/dm-templates", tags=["DM Templates"])

@router.post("", response_model=DMTemplate)
async def create_dm_template(data: DMTemplateCreate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    template_id = f"template_{uuid.uuid4().hex[:12]}"
    variables = re.findall(r'\{\{(\w+)\}\}', data.message)
    
    template_doc = {
        "template_id": template_id, "user_id": user.user_id, "name": data.name,
        "category": data.category, "message": data.message,
        "variables": variables or data.variables or [], "use_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.dm_templates.insert_one(template_doc)
    return DMTemplate(**template_doc)

@router.get("")
async def get_dm_templates(category: Optional[str] = None, request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    query = {"user_id": user.user_id}
    if category:
        query["category"] = category
    
    templates = await db.dm_templates.find(query, {"_id": 0}).to_list(100)
    return templates

@router.put("/{template_id}")
async def update_dm_template(template_id: str, data: DMTemplateCreate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    variables = re.findall(r'\{\{(\w+)\}\}', data.message)
    
    result = await db.dm_templates.update_one(
        {"template_id": template_id, "user_id": user.user_id},
        {"$set": {"name": data.name, "category": data.category, "message": data.message,
                 "variables": variables or data.variables or []}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated"}

@router.delete("/{template_id}")
async def delete_dm_template(template_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    result = await db.dm_templates.delete_one({"template_id": template_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}

@router.post("/{template_id}/generate-reply")
async def generate_dm_reply_from_template(template_id: str, message: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    await check_ai_usage(user, db, feature="dm_reply")
    
    template = await db.dm_templates.find_one({"template_id": template_id, "user_id": user.user_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    context = f"Template category: {template['category']}. Base message style: {template['message'][:100]}"
    reply = await generate_dm_reply(message, context, "friendly")
    
    await db.dm_templates.update_one({"template_id": template_id}, {"$inc": {"use_count": 1}})
    await increment_ai_usage(user.user_id, db, feature="dm_reply")
    
    return {"reply": reply}
