"""
GDPR準拠

こ
- ?
- デフォルト
- ?
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import json
import hashlib
import uuid


class DataCategory(Enum):
    """?"""
    BASIC_PROFILE = "basic_profile"          # 基本
    THERAPEUTIC_DATA = "therapeutic_data"    # 治療
    BEHAVIORAL_DATA = "behavioral_data"      # ?
    BIOMETRIC_DATA = "biometric_data"        # ?
    LOCATION_DATA = "location_data"          # ?
    COMMUNICATION_DATA = "communication_data" # コア


class ProcessingPurpose(Enum):
    """デフォルト"""
    THERAPEUTIC_SUPPORT = "therapeutic_support"
    GAME_PROGRESSION = "game_progression"
    PERSONALIZATION = "personalization"
    ANALYTICS = "analytics"
    SAFETY_MONITORING = "safety_monitoring"
    RESEARCH = "research"


class ConsentStatus(Enum):
    """?"""
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class DataClassification:
    """?"""
    category: DataCategory
    sensitivity_level: int  # 1-5 (5が)
    retention_period: timedelta
    processing_purposes: List[ProcessingPurpose]
    legal_basis: str
    anonymizable: bool = True
    
    
@dataclass
class ConsentRecord:
    """?"""
    consent_id: str
    user_id: str
    data_category: DataCategory
    processing_purpose: ProcessingPurpose
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    consent_text: str = ""
    version: str = "1.0"


class PrivacyProtectionSystem:
    """プレビュー"""
    
    def __init__(self):
        self.data_classifications = self._initialize_data_classifications()
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.anonymization_keys: Dict[str, str] = {}
        
    def _initialize_data_classifications(self) -> Dict[DataCategory, DataClassification]:
        """デフォルト"""
        return {
            DataCategory.BASIC_PROFILE: DataClassification(
                category=DataCategory.BASIC_PROFILE,
                sensitivity_level=2,
                retention_period=timedelta(days=2555),  # 7?
                processing_purposes=[ProcessingPurpose.THERAPEUTIC_SUPPORT, ProcessingPurpose.GAME_PROGRESSION],
                legal_basis="?",
                anonymizable=True
            ),
            DataCategory.THERAPEUTIC_DATA: DataClassification(
                category=DataCategory.THERAPEUTIC_DATA,
                sensitivity_level=5,
                retention_period=timedelta(days=3650),  # 10?
                processing_purposes=[ProcessingPurpose.THERAPEUTIC_SUPPORT, ProcessingPurpose.SAFETY_MONITORING],
                legal_basis="?",
                anonymizable=False  # 治療
            ),
            DataCategory.BEHAVIORAL_DATA: DataClassification(
                category=DataCategory.BEHAVIORAL_DATA,
                sensitivity_level=3,
                retention_period=timedelta(days=1095),  # 3?
                processing_purposes=[ProcessingPurpose.PERSONALIZATION, ProcessingPurpose.ANALYTICS],
                legal_basis="?",
                anonymizable=True
            ),
            DataCategory.BIOMETRIC_DATA: DataClassification(
                category=DataCategory.BIOMETRIC_DATA,
                sensitivity_level=5,
                retention_period=timedelta(days=365),   # 1?
                processing_purposes=[ProcessingPurpose.SAFETY_MONITORING],
                legal_basis="?",
                anonymizable=False
            ),
            DataCategory.LOCATION_DATA: DataClassification(
                category=DataCategory.LOCATION_DATA,
                sensitivity_level=4,
                retention_period=timedelta(days=90),    # 3?
                processing_purposes=[ProcessingPurpose.SAFETY_MONITORING],
                legal_basis="?",
                anonymizable=True
            ),
            DataCategory.COMMUNICATION_DATA: DataClassification(
                category=DataCategory.COMMUNICATION_DATA,
                sensitivity_level=3,
                retention_period=timedelta(days=1095),  # 3?
                processing_purposes=[ProcessingPurpose.THERAPEUTIC_SUPPORT, ProcessingPurpose.PERSONALIZATION],
                legal_basis="?",
                anonymizable=True
            )
        }
    
    def classify_data(self, data_type: str) -> Optional[DataClassification]:
        """デフォルト"""
        data_mapping = {
            "user_profile": DataCategory.BASIC_PROFILE,
            "mood_log": DataCategory.THERAPEUTIC_DATA,
            "task_completion": DataCategory.BEHAVIORAL_DATA,
            "heart_rate": DataCategory.BIOMETRIC_DATA,
            "location": DataCategory.LOCATION_DATA,
            "chat_message": DataCategory.COMMUNICATION_DATA,
            "story_choice": DataCategory.BEHAVIORAL_DATA,
            "xp_progress": DataCategory.BEHAVIORAL_DATA,
            "mandala_data": DataCategory.THERAPEUTIC_DATA
        }
        
        category = data_mapping.get(data_type)
        if category:
            return self.data_classifications[category]
        return None
    
    def request_consent(self, user_id: str, data_category: DataCategory, 
                       processing_purpose: ProcessingPurpose) -> str:
        """?"""
        consent_id = str(uuid.uuid4())
        classification = self.data_classifications[data_category]
        
        # ?
        if classification.legal_basis == "?":
            consent_text = self._generate_consent_text(data_category, processing_purpose)
            
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                data_category=data_category,
                processing_purpose=processing_purpose,
                status=ConsentStatus.PENDING,
                consent_text=consent_text,
                expires_at=datetime.now() + timedelta(days=365)  # 1?
            )
            
            self.consent_records[consent_id] = consent_record
            return consent_id
        else:
            # ?
            return self._auto_grant_consent(user_id, data_category, processing_purpose)
    
    def grant_consent(self, consent_id: str) -> bool:
        """?"""
        if consent_id not in self.consent_records:
            return False
        
        consent = self.consent_records[consent_id]
        consent.status = ConsentStatus.GRANTED
        consent.granted_at = datetime.now()
        
        return True
    
    def withdraw_consent(self, user_id: str, data_category: DataCategory, 
                        processing_purpose: ProcessingPurpose) -> bool:
        """?"""
        for consent in self.consent_records.values():
            if (consent.user_id == user_id and 
                consent.data_category == data_category and 
                consent.processing_purpose == processing_purpose and
                consent.status == ConsentStatus.GRANTED):
                
                consent.status = ConsentStatus.WITHDRAWN
                consent.withdrawn_at = datetime.now()
                return True
        
        return False
    
    def check_consent(self, user_id: str, data_category: DataCategory, 
                     processing_purpose: ProcessingPurpose) -> bool:
        """?"""
        classification = self.data_classifications[data_category]
        
        # ?
        if classification.legal_basis != "?":
            return True
        
        # ?
        for consent in self.consent_records.values():
            if (consent.user_id == user_id and 
                consent.data_category == data_category and 
                consent.processing_purpose == processing_purpose and
                consent.status == ConsentStatus.GRANTED and
                (consent.expires_at is None or consent.expires_at > datetime.now())):
                return True
        
        return False
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """ユーザー"""
        return [consent for consent in self.consent_records.values() 
                if consent.user_id == user_id]
    
    def anonymize_data(self, data: Dict, data_category: DataCategory) -> Dict:
        """デフォルト"""
        classification = self.data_classifications[data_category]
        
        if not classification.anonymizable:
            raise ValueError(f"デフォルト {data_category.value} は")
        
        anonymized_data = data.copy()
        
        # ?
        if 'user_id' in anonymized_data:
            anonymized_data['user_id'] = self._get_anonymous_id(anonymized_data['user_id'])
        
        # ?
        sensitive_fields = ['name', 'email', 'phone', 'address', 'ip_address']
        for field in sensitive_fields:
            if field in anonymized_data:
                if field in ['name', 'email']:
                    del anonymized_data[field]
                else:
                    anonymized_data[field] = self._hash_field(anonymized_data[field])
        
        return anonymized_data
    
    def apply_data_minimization(self, data: Dict, processing_purpose: ProcessingPurpose) -> Dict:
        """デフォルト"""
        # ?
        purpose_fields = {
            ProcessingPurpose.THERAPEUTIC_SUPPORT: [
                'user_id', 'mood_score', 'task_completion', 'story_progress', 'timestamp'
            ],
            ProcessingPurpose.GAME_PROGRESSION: [
                'user_id', 'xp', 'level', 'crystal_progress', 'timestamp'
            ],
            ProcessingPurpose.PERSONALIZATION: [
                'user_id', 'preferences', 'behavior_patterns', 'timestamp'
            ],
            ProcessingPurpose.ANALYTICS: [
                'anonymous_id', 'usage_metrics', 'performance_data', 'timestamp'
            ],
            ProcessingPurpose.SAFETY_MONITORING: [
                'user_id', 'risk_indicators', 'intervention_triggers', 'timestamp'
            ]
        }
        
        required_fields = purpose_fields.get(processing_purpose, list(data.keys()))
        return {k: v for k, v in data.items() if k in required_fields}
    
    def check_retention_policy(self, data_timestamp: datetime, 
                              data_category: DataCategory) -> bool:
        """?"""
        classification = self.data_classifications[data_category]
        expiry_date = data_timestamp + classification.retention_period
        return datetime.now() < expiry_date
    
    def _generate_consent_text(self, data_category: DataCategory, 
                              processing_purpose: ProcessingPurpose) -> str:
        """?"""
        category_names = {
            DataCategory.BASIC_PROFILE: "基本",
            DataCategory.THERAPEUTIC_DATA: "治療",
            DataCategory.BEHAVIORAL_DATA: "?",
            DataCategory.BIOMETRIC_DATA: "?",
            DataCategory.LOCATION_DATA: "?",
            DataCategory.COMMUNICATION_DATA: "コア"
        }
        
        purpose_names = {
            ProcessingPurpose.THERAPEUTIC_SUPPORT: "治療",
            ProcessingPurpose.GAME_PROGRESSION: "ゲーム",
            ProcessingPurpose.PERSONALIZATION: "?",
            ProcessingPurpose.ANALYTICS: "?",
            ProcessingPurpose.SAFETY_MONITORING: "安全",
            ProcessingPurpose.RESEARCH: "?"
        }
        
        return f"""
        {category_names[data_category]}を{purpose_names[processing_purpose]}の
        
        ?{category_names[data_category]}
        ?{purpose_names[processing_purpose]}
        ?{self.data_classifications[data_category].retention_period.days}?
        
        こ
        """
    
    def _auto_grant_consent(self, user_id: str, data_category: DataCategory, 
                           processing_purpose: ProcessingPurpose) -> str:
        """自動"""
        consent_id = str(uuid.uuid4())
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            data_category=data_category,
            processing_purpose=processing_purpose,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(),
            consent_text="?"
        )
        
        self.consent_records[consent_id] = consent_record
        return consent_id
    
    def _get_anonymous_id(self, user_id: str) -> str:
        """?IDの"""
        if user_id not in self.anonymization_keys:
            # 一般IDを
            self.anonymization_keys[user_id] = hashlib.sha256(
                f"{user_id}_{uuid.uuid4()}".encode()
            ).hexdigest()[:16]
        
        return self.anonymization_keys[user_id]
    
    def _hash_field(self, value: str) -> str:
        """?"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]


class DataMinimizationEngine:
    """デフォルト"""
    
    def __init__(self, privacy_system: PrivacyProtectionSystem):
        self.privacy_system = privacy_system
    
    def minimize_for_storage(self, data: Dict, data_type: str, 
                           processing_purpose: ProcessingPurpose) -> Dict:
        """?"""
        classification = self.privacy_system.classify_data(data_type)
        if not classification:
            return data
        
        # デフォルト
        minimized_data = self.privacy_system.apply_data_minimization(data, processing_purpose)
        
        # ?
        if (classification.anonymizable and 
            processing_purpose in [ProcessingPurpose.ANALYTICS, ProcessingPurpose.RESEARCH]):
            minimized_data = self.privacy_system.anonymize_data(
                minimized_data, classification.category
            )
        
        return minimized_data
    
    def clean_expired_data(self, data_records: List[Dict]) -> List[Dict]:
        """?"""
        valid_records = []
        
        for record in data_records:
            data_type = record.get('data_type', 'unknown')
            timestamp = record.get('timestamp', datetime.now())
            
            classification = self.privacy_system.classify_data(data_type)
            if classification and self.privacy_system.check_retention_policy(timestamp, classification.category):
                valid_records.append(record)
        
        return valid_records


class ConsentManagementInterface:
    """?"""
    
    def __init__(self, privacy_system: PrivacyProtectionSystem):
        self.privacy_system = privacy_system
    
    def get_consent_dashboard(self, user_id: str) -> Dict:
        """ユーザー"""
        consents = self.privacy_system.get_user_consents(user_id)
        
        dashboard_data = {
            "user_id": user_id,
            "total_consents": len(consents),
            "active_consents": len([c for c in consents if c.status == ConsentStatus.GRANTED]),
            "consent_details": []
        }
        
        for consent in consents:
            dashboard_data["consent_details"].append({
                "consent_id": consent.consent_id,
                "data_category": consent.data_category.value,
                "processing_purpose": consent.processing_purpose.value,
                "status": consent.status.value,
                "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                "can_withdraw": consent.status == ConsentStatus.GRANTED
            })
        
        return dashboard_data
    
    def bulk_consent_request(self, user_id: str, 
                           consent_requests: List[Dict]) -> Dict[str, str]:
        """一般"""
        consent_ids = {}
        
        for request in consent_requests:
            data_category = DataCategory(request['data_category'])
            processing_purpose = ProcessingPurpose(request['processing_purpose'])
            
            consent_id = self.privacy_system.request_consent(
                user_id, data_category, processing_purpose
            )
            
            consent_ids[f"{data_category.value}_{processing_purpose.value}"] = consent_id
        
        return consent_ids
    
    def opt_out_all(self, user_id: str) -> bool:
        """?"""
        consents = self.privacy_system.get_user_consents(user_id)
        success_count = 0
        
        for consent in consents:
            if consent.status == ConsentStatus.GRANTED:
                if self.privacy_system.withdraw_consent(
                    user_id, consent.data_category, consent.processing_purpose
                ):
                    success_count += 1
        
        return success_count > 0