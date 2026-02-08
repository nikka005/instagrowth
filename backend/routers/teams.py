from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from datetime import datetime, timezone
from typing import List
import uuid
import base64

from models import Team, TeamCreate, TeamInvite, TeamMemberUpdate, WhiteLabelSettings
from database import get_database
from dependencies import get_current_user, create_notification
from services import send_email
from utils import create_verification_token

router = APIRouter(prefix="/teams", tags=["Team Management"])

@router.post("")
async def create_team(data: TeamCreate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    if user.role not in ["agency", "enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Team management requires Agency plan or higher")
    
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    team_doc = {
        "team_id": team_id, "owner_id": user.user_id, "name": data.name,
        "logo_url": None, "brand_color": "#6366F1",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.insert_one(team_doc)
    
    member_doc = {
        "member_id": f"member_{uuid.uuid4().hex[:12]}", "team_id": team_id,
        "user_id": user.user_id, "email": user.email, "name": user.name,
        "role": "owner", "status": "active",
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.team_members.insert_one(member_doc)
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"team_id": team_id, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return Team(**team_doc)

@router.get("")
async def get_user_teams(request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    member_teams = await db.team_members.find(
        {"user_id": user.user_id, "status": "active"}, {"_id": 0}
    ).to_list(100)
    
    team_ids = [m["team_id"] for m in member_teams]
    teams = await db.teams.find({"team_id": {"$in": team_ids}}, {"_id": 0}).to_list(100)
    return teams

@router.get("/{team_id}")
async def get_team(team_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "status": "active"}, {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/{team_id}/invite")
async def invite_team_member(team_id: str, data: TeamInvite, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can invite members")
    
    existing = await db.team_members.find_one({"team_id": team_id, "email": data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="User already invited to this team")
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    invite_token = create_verification_token()
    
    member_doc = {
        "member_id": f"member_{uuid.uuid4().hex[:12]}", "team_id": team_id,
        "user_id": None, "email": data.email, "name": "", "role": data.role,
        "status": "pending", "invite_token": invite_token,
        "invited_at": datetime.now(timezone.utc).isoformat(), "joined_at": None
    }
    await db.team_members.insert_one(member_doc)
    
    invitee = await db.users.find_one({"email": data.email}, {"_id": 0})
    if invitee:
        await create_notification(
            invitee["user_id"], "team_invite",
            f"Team Invitation from {team['name']}",
            f"{user.name} invited you to join their team as {data.role}.",
            f"/accept-invite?token={invite_token}", db
        )
    
    origin = request.headers.get("origin", "https://server-restore-2.preview.emergentagent.com")
    invite_url = f"{origin}/accept-invite?token={invite_token}"
    
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); padding: 30px; border-radius: 12px; text-align: center;">
            <h1 style="color: white; margin: 0;">Team Invitation</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
            <p>You've been invited to join <strong>{team['name']}</strong> on InstaGrowth OS!</p>
            <p>Invited by: {user.name}</p>
            <p>Your role: {data.role.capitalize()}</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{invite_url}" style="background: #6366F1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold;">Accept Invitation</a>
            </div>
        </div>
    </div>
    """
    await send_email(data.email, f"You're invited to join {team['name']} on InstaGrowth OS", email_html)
    return {"message": "Invitation sent", "member_id": member_doc["member_id"]}

@router.post("/accept-invite")
async def accept_invite(token: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    invite = await db.team_members.find_one({"invite_token": token, "status": "pending"}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    if invite["email"] != user.email:
        raise HTTPException(status_code=403, detail="This invitation was sent to a different email")
    
    await db.team_members.update_one(
        {"invite_token": token},
        {"$set": {"user_id": user.user_id, "name": user.name, "status": "active",
                 "invite_token": None, "joined_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if not user.team_id:
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$set": {"team_id": invite["team_id"], "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    return {"message": "Invitation accepted", "team_id": invite["team_id"]}

@router.get("/{team_id}/members")
async def get_team_members(team_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "status": "active"}, {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    return members

@router.put("/{team_id}/members/{member_id}")
async def update_team_member(team_id: str, member_id: str, data: TeamMemberUpdate, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can update members")
    
    target_member = await db.team_members.find_one({"member_id": member_id}, {"_id": 0})
    if target_member and target_member["role"] == "owner":
        raise HTTPException(status_code=400, detail="Cannot change owner's role")
    
    await db.team_members.update_one(
        {"member_id": member_id, "team_id": team_id}, {"$set": {"role": data.role}}
    )
    return {"message": "Member updated"}

@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(team_id: str, member_id: str, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    current_member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": {"$in": ["owner", "admin"]}, "status": "active"},
        {"_id": 0}
    )
    if not current_member:
        raise HTTPException(status_code=403, detail="Only team owners and admins can remove members")
    
    target_member = await db.team_members.find_one({"member_id": member_id}, {"_id": 0})
    if target_member and target_member["role"] == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    await db.team_members.delete_one({"member_id": member_id, "team_id": team_id})
    return {"message": "Member removed"}

@router.put("/{team_id}/settings")
async def update_team_settings(team_id: str, data: WhiteLabelSettings, request: Request):
    db = get_database()
    user = await get_current_user(request, db)
    
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": "owner", "status": "active"}, {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owner can update settings")
    
    update_data = {}
    if data.logo_url is not None:
        update_data["logo_url"] = data.logo_url
    if data.brand_color:
        update_data["brand_color"] = data.brand_color
    if data.company_name:
        update_data["name"] = data.company_name
    
    if update_data:
        await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    return team

@router.post("/{team_id}/logo")
async def upload_team_logo(team_id: str, file: UploadFile = File(...), request: Request = None):
    db = get_database()
    user = await get_current_user(request, db)
    
    member = await db.team_members.find_one(
        {"team_id": team_id, "user_id": user.user_id, "role": "owner", "status": "active"}, {"_id": 0}
    )
    if not member:
        raise HTTPException(status_code=403, detail="Only team owner can upload logo")
    
    contents = await file.read()
    logo_b64 = base64.b64encode(contents).decode()
    logo_url = f"data:{file.content_type};base64,{logo_b64}"
    
    await db.teams.update_one({"team_id": team_id}, {"$set": {"logo_url": logo_url}})
    return {"logo_url": logo_url}
