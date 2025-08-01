"""
?
?
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
import uuid
import hashlib
import logging
import json
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class PlaytestUserStatus(Enum):
    """?"""
    INVITED = "invited"           # ?
    ONBOARDING = "onboarding"     # ?
    ACTIVE = "active"             # アプリ
    INACTIVE = "inactive"         # ?7?
    COMPLETED = "completed"       # ?
    DROPPED = "dropped"           # ?
    SUSPENDED = "suspended"       # 一般

class ConsentType(Enum):
    """?"""
    DATA_COLLECTION = "data_collection"
    ANALYTICS = "analytics"
    FEEDBACK_COLLECTION = "feedback_collection"
    RESEARCH_PARTICIPATION = "research_participation"
    COMMUNICATION = "communication"

class TestUserDemographics(BaseModel):
    """?"""
    age_range: Optional[str] = Field(None, description="?20-25?")
    gender: Optional[str] = Field(None, description="?")
    occupation: Optional[str] = Field(None, description="?")
    education_level: Optional[str] = Field(None, description="?")
    tech_proficiency: Optional[str] = Field(None, description="?low/medium/high?")
    mental_health_experience: Optional[str] = Field(None, description="メイン")
    gaming_experience: Optional[str] = Field(None, description="ゲーム")
    smartphone_usage: Optional[str] = Field(None, description="ストーリー")
    preferred_language: Optional[str] = Field("ja", description="?")
    timezone: Optional[str] = Field("Asia/Tokyo", description="タスク")

class TestUserConsent(BaseModel):
    """ユーザー"""
    consent_type: ConsentType
    granted: bool
    granted_at: datetime
    version: str = Field("1.0", description="?")
    ip_address_hash: Optional[str] = Field(None, description="IPアプリ")

class TestUserActivity(BaseModel):
    """ユーザー"""
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    session_count: int = 0
    total_session_duration: float = 0.0  # ?
    feature_usage: Dict[str, int] = Field(default_factory=dict)
    task_completion_count: int = 0
    story_progression: int = 0
    feedback_submitted: int = 0

class TestUser(BaseModel):
    """?"""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email_hash: str = Field(..., description="?")
    status: PlaytestUserStatus = PlaytestUserStatus.INVITED
    registration_date: datetime = Field(default_factory=datetime.now)
    demographics: TestUserDemographics = Field(default_factory=TestUserDemographics)
    consents: List[TestUserConsent] = Field(default_factory=list)
    activity: TestUserActivity = Field(default_factory=TestUserActivity)
    ab_test_assignments: Dict[str, str] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)
    created_by: str = Field("system", description="?")
    updated_at: datetime = Field(default_factory=datetime.now)

class PlaytestUserManager:
    """?"""
    
    def __init__(self, max_users: int = 50):
        self.users: Dict[str, TestUser] = {}
        self.email_to_user_id: Dict[str, str] = {}
        self.max_users = max_users
        self.invitation_codes: Dict[str, str] = {}  # code -> user_id
        
        # プレビュー
        self.privacy_config = {
            "email_salt": "therapeutic_gaming_alpha_2024",
            "data_retention_days": 90,
            "anonymization_enabled": True,
            "consent_required": True,
            "minimum_age": 18
        }
    
    def generate_email_hash(self, email: str) -> str:
        """メイン"""
        salt = self.privacy_config["email_salt"]
        combined = f"{email.lower()}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def generate_invitation_code(self) -> str:
        """?"""
        return str(uuid.uuid4())[:8].upper()
    
    async def register_user(self, email: str, demographics: Optional[Dict[str, Any]] = None,
                           invitation_code: Optional[str] = None) -> TestUser:
        """?"""
        
        # ?
        if len(self.users) >= self.max_users:
            raise ValueError(f"?{self.max_users}?")
        
        # メイン
        email_hash = self.generate_email_hash(email)
        if email_hash in self.email_to_user_id:
            raise ValueError("こ")
        
        # ?
        if invitation_code:
            if invitation_code not in self.invitation_codes:
                raise ValueError("無")
            if self.invitation_codes[invitation_code]:
                raise ValueError("こ")
        
        # ユーザー
        user = TestUser(
            email_hash=email_hash,
            demographics=TestUserDemographics(**(demographics or {}))
        )
        
        # 基本
        required_consents = [
            ConsentType.DATA_COLLECTION,
            ConsentType.RESEARCH_PARTICIPATION
        ]
        
        for consent_type in required_consents:
            consent = TestUserConsent(
                consent_type=consent_type,
                granted=True,
                granted_at=datetime.now()
            )
            user.consents.append(consent)
        
        # ?
        self.users[user.user_id] = user
        self.email_to_user_id[email_hash] = user.user_id
        
        # ?
        if invitation_code:
            self.invitation_codes[invitation_code] = user.user_id
        
        logger.info(f"Test user registered: {user.user_id}")
        return user
    
    async def update_user_status(self, user_id: str, new_status: PlaytestUserStatus,
                                reason: Optional[str] = None) -> TestUser:
        """ユーザー"""
        if user_id not in self.users:
            raise ValueError("ユーザー")
        
        user = self.users[user_id]
        old_status = user.status
        user.status = new_status
        user.updated_at = datetime.now()
        
        if reason:
            user.notes.append(f"{datetime.now().isoformat()}: Status changed from {old_status.value} to {new_status.value} - {reason}")
        
        logger.info(f"User {user_id} status updated: {old_status.value} -> {new_status.value}")
        return user
    
    async def update_user_activity(self, user_id: str, activity_data: Dict[str, Any]) -> TestUser:
        """ユーザー"""
        if user_id not in self.users:
            raise ValueError("ユーザー")
        
        user = self.users[user_id]
        activity = user.activity
        
        # ?
        if "last_login" in activity_data:
            activity.last_login = datetime.fromisoformat(activity_data["last_login"])
        
        if "last_active" in activity_data:
            activity.last_active = datetime.fromisoformat(activity_data["last_active"])
        
        if "session_duration" in activity_data:
            activity.session_count += 1
            activity.total_session_duration += activity_data["session_duration"]
        
        if "feature_used" in activity_data:
            feature = activity_data["feature_used"]
            activity.feature_usage[feature] = activity.feature_usage.get(feature, 0) + 1
        
        if "task_completed" in activity_data:
            activity.task_completion_count += activity_data["task_completed"]
        
        if "story_progress" in activity_data:
            activity.story_progression = max(activity.story_progression, activity_data["story_progress"])
        
        if "feedback_submitted" in activity_data:
            activity.feedback_submitted += 1
        
        # ストーリー
        await self._auto_update_status(user)
        
        user.updated_at = datetime.now()
        return user
    
    async def _auto_update_status(self, user: TestUser):
        """ストーリー"""
        now = datetime.now()
        
        # INVITEDかACTIVE?
        if user.status == PlaytestUserStatus.INVITED and user.activity.last_active:
            user.status = PlaytestUserStatus.ACTIVE
            user.notes.append(f"{now.isoformat()}: Auto-updated to ACTIVE (first activity)")
        
        # ?7?
        if user.activity.last_active:
            days_inactive = (now - user.activity.last_active).days
            if days_inactive >= 7 and user.status == PlaytestUserStatus.ACTIVE:
                user.status = PlaytestUserStatus.INACTIVE
                user.notes.append(f"{now.isoformat()}: Auto-updated to INACTIVE (7 days inactive)")
        
        # ?
        completion_criteria = {
            "min_sessions": 10,
            "min_tasks": 20,
            "min_story_progress": 50,
            "min_feedback": 3
        }
        
        if (user.activity.session_count >= completion_criteria["min_sessions"] and
            user.activity.task_completion_count >= completion_criteria["min_tasks"] and
            user.activity.story_progression >= completion_criteria["min_story_progress"] and
            user.activity.feedback_submitted >= completion_criteria["min_feedback"] and
            user.status == PlaytestUserStatus.ACTIVE):
            
            user.status = PlaytestUserStatus.COMPLETED
            user.notes.append(f"{now.isoformat()}: Auto-updated to COMPLETED (criteria met)")
    
    async def add_consent(self, user_id: str, consent_type: ConsentType,
                         granted: bool, ip_address: Optional[str] = None) -> TestUser:
        """?"""
        if user_id not in self.users:
            raise ValueError("ユーザー")
        
        user = self.users[user_id]
        
        # IPアプリ
        ip_hash = None
        if ip_address:
            ip_hash = hashlib.sha256(f"{ip_address}{self.privacy_config['email_salt']}".encode()).hexdigest()[:16]
        
        consent = TestUserConsent(
            consent_type=consent_type,
            granted=granted,
            granted_at=datetime.now(),
            ip_address_hash=ip_hash
        )
        
        # ?
        existing_consent = None
        for i, existing in enumerate(user.consents):
            if existing.consent_type == consent_type:
                existing_consent = i
                break
        
        if existing_consent is not None:
            user.consents[existing_consent] = consent
        else:
            user.consents.append(consent)
        
        user.updated_at = datetime.now()
        logger.info(f"Consent updated for user {user_id}: {consent_type.value} = {granted}")
        return user
    
    async def assign_ab_test(self, user_id: str, test_id: str, variant: str) -> TestUser:
        """A/B?"""
        if user_id not in self.users:
            raise ValueError("ユーザー")
        
        user = self.users[user_id]
        user.ab_test_assignments[test_id] = variant
        user.updated_at = datetime.now()
        
        logger.info(f"A/B test assigned for user {user_id}: {test_id} = {variant}")
        return user
    
    def get_user(self, user_id: str) -> Optional[TestUser]:
        """ユーザー"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[TestUser]:
        """メイン"""
        email_hash = self.generate_email_hash(email)
        user_id = self.email_to_user_id.get(email_hash)
        return self.users.get(user_id) if user_id else None
    
    def list_users(self, status: Optional[PlaytestUserStatus] = None,
                  limit: Optional[int] = None) -> List[TestUser]:
        """ユーザー"""
        users = list(self.users.values())
        
        if status:
            users = [u for u in users if u.status == status]
        
        # ?
        users.sort(key=lambda u: u.registration_date, reverse=True)
        
        if limit:
            users = users[:limit]
        
        return users
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """ユーザー"""
        total_users = len(self.users)
        
        # ストーリー
        status_counts = Counter(user.status for user in self.users.values())
        
        # ?
        age_ranges = Counter(user.demographics.age_range for user in self.users.values() if user.demographics.age_range)
        tech_proficiency = Counter(user.demographics.tech_proficiency for user in self.users.values() if user.demographics.tech_proficiency)
        
        # ?
        active_users = [u for u in self.users.values() if u.status == PlaytestUserStatus.ACTIVE]
        avg_sessions = sum(u.activity.session_count for u in active_users) / len(active_users) if active_users else 0
        avg_session_duration = sum(u.activity.total_session_duration for u in active_users) / len(active_users) if active_users else 0
        
        # ?
        completion_rate = status_counts[PlaytestUserStatus.COMPLETED] / total_users if total_users > 0 else 0
        
        # ?
        dropout_rate = status_counts[PlaytestUserStatus.DROPPED] / total_users if total_users > 0 else 0
        
        return {
            "total_users": total_users,
            "max_users": self.max_users,
            "capacity_utilization": total_users / self.max_users,
            "status_distribution": dict(status_counts),
            "demographics": {
                "age_ranges": dict(age_ranges),
                "tech_proficiency": dict(tech_proficiency)
            },
            "activity_metrics": {
                "average_sessions_per_user": round(avg_sessions, 2),
                "average_session_duration_minutes": round(avg_session_duration, 2),
                "completion_rate": round(completion_rate, 3),
                "dropout_rate": round(dropout_rate, 3)
            },
            "consent_compliance": self._calculate_consent_compliance()
        }
    
    def _calculate_consent_compliance(self) -> Dict[str, float]:
        """?"""
        consent_stats = {}
        
        for consent_type in ConsentType:
            granted_count = 0
            total_count = 0
            
            for user in self.users.values():
                user_consent = None
                for consent in user.consents:
                    if consent.consent_type == consent_type:
                        user_consent = consent
                        break
                
                if user_consent:
                    total_count += 1
                    if user_consent.granted:
                        granted_count += 1
            
            consent_stats[consent_type.value] = granted_count / total_count if total_count > 0 else 0.0
        
        return consent_stats
    
    async def cleanup_inactive_users(self, days_threshold: int = 30) -> int:
        """?"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        cleanup_count = 0
        
        users_to_cleanup = []
        for user in self.users.values():
            if (user.status == PlaytestUserStatus.INACTIVE and
                user.activity.last_active and
                user.activity.last_active < cutoff_date):
                users_to_cleanup.append(user.user_id)
        
        for user_id in users_to_cleanup:
            await self.update_user_status(user_id, PlaytestUserStatus.DROPPED, 
                                        f"Auto-cleanup after {days_threshold} days inactive")
            cleanup_count += 1
        
        logger.info(f"Cleaned up {cleanup_count} inactive users")
        return cleanup_count
    
    def export_user_data(self, user_id: str, include_sensitive: bool = False) -> Dict[str, Any]:
        """ユーザーGDPR?"""
        if user_id not in self.users:
            raise ValueError("ユーザー")
        
        user = self.users[user_id]
        
        export_data = {
            "user_id": user.user_id,
            "registration_date": user.registration_date.isoformat(),
            "status": user.status.value,
            "demographics": user.demographics.dict(exclude_none=True),
            "activity_summary": {
                "session_count": user.activity.session_count,
                "total_session_duration_minutes": user.activity.total_session_duration,
                "task_completion_count": user.activity.task_completion_count,
                "story_progression": user.activity.story_progression,
                "feedback_submitted": user.activity.feedback_submitted
            },
            "consents": [
                {
                    "type": consent.consent_type.value,
                    "granted": consent.granted,
                    "granted_at": consent.granted_at.isoformat(),
                    "version": consent.version
                }
                for consent in user.consents
            ],
            "ab_test_assignments": user.ab_test_assignments
        }
        
        if include_sensitive:
            export_data["email_hash"] = user.email_hash
            export_data["notes"] = user.notes
        
        return export_data
    
    async def delete_user_data(self, user_id: str) -> bool:
        """ユーザーGDPR?"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # メイン
        if user.email_hash in self.email_to_user_id:
            del self.email_to_user_id[user.email_hash]
        
        # ユーザー
        del self.users[user_id]
        
        logger.info(f"User data deleted: {user_id}")
        return True