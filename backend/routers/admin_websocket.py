"""
Admin WebSocket for Real-Time Updates

Provides real-time notifications to admin panel for:
- New user registrations
- Subscription changes
- AI usage alerts
- System events
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin WebSocket"])

class AdminConnectionManager:
    """Manages WebSocket connections for admin panel"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.admin_roles: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, admin_id: str, role: str):
        await websocket.accept()
        if admin_id not in self.active_connections:
            self.active_connections[admin_id] = []
        self.active_connections[admin_id].append(websocket)
        self.admin_roles[admin_id] = role
        logger.info(f"Admin WebSocket connected: {admin_id} ({role})")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Admin WebSocket connected"
        })
    
    def disconnect(self, websocket: WebSocket, admin_id: str):
        if admin_id in self.active_connections:
            if websocket in self.active_connections[admin_id]:
                self.active_connections[admin_id].remove(websocket)
            if not self.active_connections[admin_id]:
                del self.active_connections[admin_id]
                if admin_id in self.admin_roles:
                    del self.admin_roles[admin_id]
        logger.info(f"Admin WebSocket disconnected: {admin_id}")
    
    async def send_to_admin(self, admin_id: str, message: dict):
        """Send message to specific admin"""
        if admin_id in self.active_connections:
            for connection in self.active_connections[admin_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to admin {admin_id}: {e}")
    
    async def broadcast_to_role(self, role: str, message: dict):
        """Broadcast message to all admins with specific role"""
        for admin_id, admin_role in self.admin_roles.items():
            if admin_role == role or admin_role == "super_admin":
                await self.send_to_admin(admin_id, message)
    
    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected admins"""
        for admin_id in list(self.active_connections.keys()):
            await self.send_to_admin(admin_id, message)
    
    def get_connected_admins(self) -> List[dict]:
        """Get list of connected admins"""
        return [
            {"admin_id": aid, "role": self.admin_roles.get(aid, "unknown")}
            for aid in self.active_connections.keys()
        ]

admin_manager = AdminConnectionManager()

# Event types for admin notifications
class AdminEventType:
    NEW_USER = "new_user"
    USER_UPGRADED = "user_upgraded"
    USER_DOWNGRADED = "user_downgraded"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    NEW_PAYMENT = "new_payment"
    AI_LIMIT_WARNING = "ai_limit_warning"
    SYSTEM_ALERT = "system_alert"
    NEW_AUDIT = "new_audit"
    NEW_ACCOUNT = "new_account"
    ADMIN_LOGIN = "admin_login"
    ADMIN_ACTION = "admin_action"

@router.websocket("/admin-ws/{admin_id}")
async def admin_websocket_endpoint(websocket: WebSocket, admin_id: str, role: str = "support"):
    """WebSocket endpoint for admin real-time updates"""
    await admin_manager.connect(websocket, admin_id, role)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": message.get("timestamp")})
            
            elif message.get("type") == "subscribe":
                channel = message.get("channel")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel,
                    "message": f"Subscribed to {channel}"
                })
            
            elif message.get("type") == "get_online_admins":
                admins = admin_manager.get_connected_admins()
                await websocket.send_json({
                    "type": "online_admins",
                    "admins": admins,
                    "count": len(admins)
                })
    
    except WebSocketDisconnect:
        admin_manager.disconnect(websocket, admin_id)
    except Exception as e:
        logger.error(f"Admin WebSocket error: {e}")
        admin_manager.disconnect(websocket, admin_id)

# ==================== Event Broadcasting Functions ====================

async def notify_new_user(user_data: dict):
    """Notify admins of new user registration"""
    await admin_manager.broadcast_all({
        "type": AdminEventType.NEW_USER,
        "title": "New User Registration",
        "message": f"New user registered: {user_data.get('email')}",
        "data": {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "plan": user_data.get("role", "starter")
        },
        "priority": "normal"
    })

async def notify_subscription_change(user_id: str, old_plan: str, new_plan: str, action: str):
    """Notify admins of subscription changes"""
    event_type = AdminEventType.USER_UPGRADED if action == "upgrade" else AdminEventType.USER_DOWNGRADED
    
    await admin_manager.broadcast_to_role("finance", {
        "type": event_type,
        "title": f"User {action.capitalize()}d",
        "message": f"User changed from {old_plan} to {new_plan}",
        "data": {
            "user_id": user_id,
            "old_plan": old_plan,
            "new_plan": new_plan,
            "action": action
        },
        "priority": "high"
    })

async def notify_payment(payment_data: dict):
    """Notify admins of new payment"""
    await admin_manager.broadcast_to_role("finance", {
        "type": AdminEventType.NEW_PAYMENT,
        "title": "New Payment Received",
        "message": f"Payment of ${payment_data.get('amount')} received",
        "data": payment_data,
        "priority": "normal"
    })

async def notify_ai_limit_warning(user_id: str, usage: int, limit: int):
    """Notify admins when user approaches AI limit"""
    percentage = (usage / limit) * 100
    if percentage >= 90:
        await admin_manager.broadcast_all({
            "type": AdminEventType.AI_LIMIT_WARNING,
            "title": "AI Usage Warning",
            "message": f"User {user_id} at {percentage:.0f}% AI usage",
            "data": {
                "user_id": user_id,
                "usage": usage,
                "limit": limit,
                "percentage": percentage
            },
            "priority": "high" if percentage >= 95 else "normal"
        })

async def notify_system_alert(title: str, message: str, severity: str = "info"):
    """Send system-wide alert to all admins"""
    await admin_manager.broadcast_all({
        "type": AdminEventType.SYSTEM_ALERT,
        "title": title,
        "message": message,
        "severity": severity,
        "priority": "high" if severity in ["error", "critical"] else "normal"
    })

async def notify_admin_action(admin_email: str, action: str, target: str, details: dict = None):
    """Notify other admins of admin actions"""
    await admin_manager.broadcast_all({
        "type": AdminEventType.ADMIN_ACTION,
        "title": "Admin Action",
        "message": f"{admin_email} performed {action} on {target}",
        "data": {
            "admin": admin_email,
            "action": action,
            "target": target,
            "details": details or {}
        },
        "priority": "low"
    })

# Export functions for use in other modules
def get_admin_manager():
    return admin_manager
