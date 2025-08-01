"""
Guardian Portal Service - ?

SAML/Magic Link?PDFレベル
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import json
from pathlib import Path
import asyncio
import logging
import uuid

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

# 基本
def validate_email(email: str) -> bool:
    """メイン"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_uid(uid: str) -> bool:
    """UID検証"""
    return isinstance(uid, str) and len(uid) > 0

app = FastAPI(title="Guardian Portal Service", version="1.0.0")
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Guardian?
class GuardianAuth:
    def __init__(self):
        self.secret_key = "guardian_secret_key_2024"
        self.magic_links = {}  # 実装Redisを
        self.saml_config = {
            "entity_id": "therapeutic-app-guardian",
            "sso_url": "https://guardian.therapeutic-app.com/sso",
            "certificate": "guardian_saml_cert"
        }
    
    def generate_magic_link(self, email: str, guardian_id: str) -> str:
        """Magic Link?"""
        if not validate_email(email):
            raise ValueError("無")
        
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(minutes=15)
        
        self.magic_links[token] = {
            "email": email,
            "guardian_id": guardian_id,
            "expires_at": expiry,
            "used": False
        }
        
        return f"https://guardian.therapeutic-app.com/auth/magic?token={token}"
    
    def verify_magic_link(self, token: str) -> Dict[str, Any]:
        """Magic Link検証"""
        if token not in self.magic_links:
            raise HTTPException(status_code=401, detail="無")
        
        link_data = self.magic_links[token]
        
        if link_data["used"]:
            raise HTTPException(status_code=401, detail="?")
        
        if datetime.utcnow() > link_data["expires_at"]:
            raise HTTPException(status_code=401, detail="?")
        
        # ?
        self.magic_links[token]["used"] = True
        
        return {
            "guardian_id": link_data["guardian_id"],
            "email": link_data["email"]
        }
    
    def create_guardian_jwt(self, guardian_id: str, permissions: List[str]) -> str:
        """Guardian?JWT?"""
        payload = {
            "guardian_id": guardian_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=8),
            "iat": datetime.utcnow(),
            "type": "guardian"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_guardian_jwt(self, token: str) -> Dict[str, Any]:
        """Guardian JWT?"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload.get("type") != "guardian":
                raise HTTPException(status_code=401, detail="無")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="?")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="無")

# Guardian?
class GuardianRBAC:
    def __init__(self):
        self.permissions = {
            "view-only": ["view_reports", "view_progress"],
            "task-edit": ["view_reports", "view_progress", "edit_tasks", "assign_tasks"],
            "chat-send": ["view_reports", "view_progress", "edit_tasks", "assign_tasks", "send_messages", "emergency_contact"]
        }
    
    def get_guardian_permissions(self, guardian_id: str) -> List[str]:
        """Guardian?Firestoreか"""
        # デフォルト
        guardian_permissions = {
            "guardian_001": "chat-send",
            "guardian_002": "task-edit",
            "guardian_003": "view-only"
        }
        
        permission_level = guardian_permissions.get(guardian_id, "view-only")
        return self.permissions.get(permission_level, self.permissions["view-only"])
    
    def check_permission(self, guardian_id: str, required_permission: str) -> bool:
        """?"""
        guardian_permissions = self.get_guardian_permissions(guardian_id)
        return required_permission in guardian_permissions

# デフォルト
class GuardianProfile(BaseModel):
    guardian_id: str
    name: str
    email: str
    relationship: str  # "parent", "counselor", "support_worker"
    managed_users: List[str]
    permission_level: str
    created_at: datetime
    last_login: Optional[datetime] = None

class WeeklyReport(BaseModel):
    user_id: str
    guardian_id: str
    week_start: datetime
    week_end: datetime
    total_tasks_completed: int
    total_xp_earned: int
    mood_average: float
    crystal_progress: Dict[str, int]
    story_chapters_completed: int
    adherence_rate: float
    recommendations: List[str]

class MagicLinkRequest(BaseModel):
    email: str
    guardian_id: str

class SAMLResponse(BaseModel):
    saml_response: str
    relay_state: Optional[str] = None

# Guardian?
guardian_auth = GuardianAuth()
guardian_rbac = GuardianRBAC()

# レベル
from report_generator import report_service

# ?
from care_points_system import (
    care_points_system, 
    CorporatePurchaseRequest,
    CarePointTransferRequest,
    ADHDDocumentVerificationRequest,
    ADHDDiscountRequest
)

# ?
async def get_current_guardian(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """?Guardian?"""
    token = credentials.credentials
    return guardian_auth.verify_guardian_jwt(token)

# APIエラー

@app.post("/auth/magic-link")
async def request_magic_link(request: MagicLinkRequest):
    """Magic Link?"""
    try:
        magic_link = guardian_auth.generate_magic_link(
            request.email, 
            request.guardian_id
        )
        
        # 実装
        logger.info(f"Magic link generated for {request.email}: {magic_link}")
        
        return {
            "success": True,
            "message": "Magic Linkを",
            "magic_link": magic_link  # デフォルト
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/magic")
async def verify_magic_link(token: str):
    """Magic Link検証JWT発"""
    try:
        link_data = guardian_auth.verify_magic_link(token)
        permissions = guardian_rbac.get_guardian_permissions(link_data["guardian_id"])
        
        jwt_token = guardian_auth.create_guardian_jwt(
            link_data["guardian_id"],
            permissions
        )
        
        return {
            "success": True,
            "access_token": jwt_token,
            "token_type": "bearer",
            "guardian_id": link_data["guardian_id"],
            "permissions": permissions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="?")

@app.post("/auth/saml")
async def saml_login(saml_response: SAMLResponse):
    """SAML?"""
    # 実装SAMLレベル
    # こ
    
    try:
        # SAML検証
        guardian_id = "guardian_saml_001"  # SAMLか
        permissions = guardian_rbac.get_guardian_permissions(guardian_id)
        
        jwt_token = guardian_auth.create_guardian_jwt(guardian_id, permissions)
        
        return {
            "success": True,
            "access_token": jwt_token,
            "token_type": "bearer",
            "guardian_id": guardian_id,
            "permissions": permissions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="SAML?")

@app.get("/dashboard")
async def get_dashboard(guardian: Dict[str, Any] = Depends(get_current_guardian)):
    """Guardian?"""
    guardian_id = guardian["guardian_id"]
    
    # ?
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="レベル")
    
    # 管理
    managed_users = [
        {
            "user_id": "user_001",
            "name": "?",
            "current_level": 15,
            "total_xp": 2500,
            "last_activity": "2024-01-20T10:30:00Z",
            "mood_trend": "improving",
            "task_completion_rate": 0.85
        }
    ]
    
    return {
        "guardian_id": guardian_id,
        "permissions": guardian["permissions"],
        "managed_users": managed_users,
        "dashboard_summary": {
            "total_users": len(managed_users),
            "active_users_today": 1,
            "average_completion_rate": 0.85,
            "alerts": []
        }
    }

@app.get("/reports/weekly/{user_id}")
async def generate_weekly_report(
    user_id: str,
    week_start: str,  # YYYY-MM-DD format
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?PDFレベル"""
    guardian_id = guardian["guardian_id"]
    
    # ?
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="レベル")
    
    try:
        # ?
        week_start_date = datetime.strptime(week_start, "%Y-%m-%d")
        
        # PDFレベル
        pdf_content = await report_service.generate_weekly_report(
            user_id, guardian_id, week_start_date
        )
        
        # ?
        filename = f"weekly_report_{user_id}_{week_start}.pdf"
        
        return {
            "success": True,
            "report_url": f"/reports/download/{filename}",
            "generated_at": datetime.utcnow().isoformat(),
            "file_size": len(pdf_content)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="無")
    except Exception as e:
        logger.error(f"レベル: {e}")
        raise HTTPException(status_code=500, detail="レベル")

@app.get("/reports/download/{filename}")
async def download_report(
    filename: str,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """レベル"""
    guardian_id = guardian["guardian_id"]
    
    # ?
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="レベル")
    
    try:
        # ?IDと
        parts = filename.replace('.pdf', '').split('_')
        if len(parts) >= 4:
            user_id = parts[2]
            week_start = parts[3]
            week_start_date = datetime.strptime(week_start, "%Y-%m-%d")
            
            # PDFコア
            pdf_content = await report_service.generate_weekly_report(
                user_id, guardian_id, week_start_date
            )
            
            # 一般
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file.flush()
                
                return FileResponse(
                    tmp_file.name,
                    media_type='application/pdf',
                    filename=filename
                )
        else:
            raise HTTPException(status_code=400, detail="無")
            
    except Exception as e:
        logger.error(f"レベル: {e}")
        raise HTTPException(status_code=500, detail="レベル")

@app.get("/users/{user_id}/progress")
async def get_user_progress(
    user_id: str,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """ユーザー"""
    guardian_id = guardian["guardian_id"]
    
    # ?
    if not guardian_rbac.check_permission(guardian_id, "view_progress"):
        raise HTTPException(status_code=403, detail="?")
    
    # ユーザー
    progress_data = {
        "user_id": user_id,
        "current_level": 15,
        "total_xp": 2500,
        "crystal_progress": {
            "Self-Discipline": 75,
            "Empathy": 45,
            "Resilience": 60,
            "Curiosity": 80,
            "Communication": 35,
            "Creativity": 55,
            "Courage": 25,
            "Wisdom": 70
        },
        "recent_tasks": [
            {
                "task_id": "task_001",
                "description": "?",
                "completed_at": "2024-01-20T07:30:00Z",
                "xp_earned": 25,
                "mood_at_completion": 4
            },
            {
                "task_id": "task_002", 
                "description": "プレビュー",
                "completed_at": "2024-01-20T14:00:00Z",
                "xp_earned": 50,
                "mood_at_completion": 3
            }
        ],
        "mood_history": [
            {"date": "2024-01-20", "mood": 3.8},
            {"date": "2024-01-19", "mood": 3.5},
            {"date": "2024-01-18", "mood": 4.0}
        ],
        "story_progress": {
            "current_chapter": "?4?: ?",
            "yu_level": 15,
            "player_level": 14,
            "chapters_completed": 3
        }
    }
    
    return progress_data

# ?

@app.post("/care-points/corporate/purchase")
async def corporate_purchase_care_points(
    request: CorporatePurchaseRequest,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?"""
    guardian_id = guardian["guardian_id"]
    
    # ?IDとguardian_idの
    if not guardian_rbac.check_permission(guardian_id, "edit_tasks"):
        raise HTTPException(status_code=403, detail="?")
    
    try:
        # ?
        discount_rate = care_points_system.calculate_corporate_discount(request.amount)
        
        # Stripe?
        payment_intent = care_points_system.create_stripe_payment_intent(
            request.amount, 
            request.corporate_id,
            discount_rate
        )
        
        return {
            "success": True,
            "payment_intent": payment_intent,
            "discount_rate": discount_rate,
            "original_amount": request.amount,
            "discounted_amount": payment_intent["amount"],
            "points_to_receive": payment_intent["amount"] * care_points_system.point_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Corporate purchase initiation failed: {e}")
        raise HTTPException(status_code=500, detail="?")

@app.post("/care-points/corporate/confirm")
async def confirm_corporate_purchase(
    payment_intent_id: str,
    corporate_id: str,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "edit_tasks"):
        raise HTTPException(status_code=403, detail="?")
    
    try:
        # 実装Stripeか
        # こ
        amount = 10000  # 実装Stripeか
        
        purchase = care_points_system.process_corporate_purchase(
            corporate_id, 
            amount, 
            payment_intent_id
        )
        
        return {
            "success": True,
            "purchase": {
                "corporate_id": purchase.corporate_id,
                "points_purchased": purchase.points_purchased,
                "amount_paid": purchase.purchase_amount,
                "discount_applied": purchase.discount_applied,
                "created_at": purchase.created_at.isoformat()
            },
            "new_balance": care_points_system.get_care_point_balance(corporate_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Corporate purchase confirmation failed: {e}")
        raise HTTPException(status_code=500, detail="?")

@app.post("/care-points/transfer")
async def transfer_care_points(
    request: CarePointTransferRequest,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "edit_tasks"):
        raise HTTPException(status_code=403, detail="?")
    
    try:
        metadata = {
            "transferred_by": guardian_id,
            "message": request.message
        } if request.message else {"transferred_by": guardian_id}
        
        transaction = care_points_system.transfer_care_points(
            request.from_corporate_id,
            request.to_user_id,
            request.points,
            metadata
        )
        
        return {
            "success": True,
            "transaction": {
                "transaction_id": transaction.transaction_id,
                "from_entity": transaction.from_entity,
                "to_user": transaction.to_user,
                "points": transaction.points,
                "created_at": transaction.created_at.isoformat()
            },
            "corporate_balance": care_points_system.get_care_point_balance(request.from_corporate_id),
            "user_balance": care_points_system.get_care_point_balance(request.to_user_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Care points transfer failed: {e}")
        raise HTTPException(status_code=500, detail="?")

@app.get("/care-points/balance/{entity_id}")
async def get_care_point_balance(
    entity_id: str,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="?")
    
    balance = care_points_system.get_care_point_balance(entity_id)
    
    return {
        "entity_id": entity_id,
        "balance": balance,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/care-points/transactions/{entity_id}")
async def get_transaction_history(
    entity_id: str,
    limit: int = 50,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="?")
    
    transactions = care_points_system.get_transaction_history(entity_id, limit)
    
    return {
        "entity_id": entity_id,
        "transactions": [
            {
                "transaction_id": t.transaction_id,
                "from_entity": t.from_entity,
                "to_user": t.to_user,
                "points": t.points,
                "transaction_type": t.transaction_type,
                "created_at": t.created_at.isoformat(),
                "metadata": t.metadata
            }
            for t in transactions
        ],
        "total_count": len(transactions)
    }

@app.post("/care-points/adhd/verify-document")
async def verify_adhd_document(
    request: ADHDDocumentVerificationRequest,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """ADHD?"""
    guardian_id = guardian["guardian_id"]
    
    # ?
    if not guardian_rbac.check_permission(guardian_id, "chat-send"):
        raise HTTPException(status_code=403, detail="?")
    
    try:
        document_id = f"adhd_doc_{uuid.uuid4().hex[:12]}"
        
        document = care_points_system.verify_adhd_medical_document(
            document_id,
            request.user_id,
            request.document_type,
            request.verifier_id
        )
        
        return {
            "success": True,
            "document": {
                "document_id": document.document_id,
                "user_id": document.user_id,
                "document_type": document.document_type,
                "verified": document.verified,
                "verified_at": document.verified_at.isoformat() if document.verified_at else None,
                "verified_by": document.verified_by,
                "expiry_date": document.expiry_date.isoformat() if document.expiry_date else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ADHD document verification failed: {e}")
        raise HTTPException(status_code=500, detail="ADHD?")

@app.post("/care-points/adhd/apply-discount")
async def apply_adhd_discount(
    request: ADHDDiscountRequest,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """ADHD?50%?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "edit_tasks"):
        raise HTTPException(status_code=403, detail="?")
    
    try:
        discount_info = care_points_system.apply_adhd_discount(
            request.user_id,
            request.original_amount
        )
        
        # Stripe?
        coupon = care_points_system.create_stripe_coupon_for_adhd(request.user_id)
        
        return {
            "success": True,
            "discount_info": discount_info,
            "stripe_coupon": coupon,
            "message": "ADHD?50%?"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ADHD discount application failed: {e}")
        raise HTTPException(status_code=500, detail="ADHD?")

@app.get("/care-points/adhd/eligibility/{user_id}")
async def check_adhd_discount_eligibility(
    user_id: str,
    guardian: Dict[str, Any] = Depends(get_current_guardian)
):
    """ADHD?"""
    guardian_id = guardian["guardian_id"]
    
    if not guardian_rbac.check_permission(guardian_id, "view_reports"):
        raise HTTPException(status_code=403, detail="?")
    
    eligible = care_points_system.check_adhd_discount_eligibility(user_id)
    
    return {
        "user_id": user_id,
        "eligible": eligible,
        "discount_rate": 0.5 if eligible else 0.0,
        "message": "ADHD?" if eligible else "ADHD?"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)