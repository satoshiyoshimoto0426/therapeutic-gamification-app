"""
GDPR準拠

?
- ?
- ?
- ?
- ?
- ?
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import json
import uuid


class ConsentType(Enum):
    """?"""
    EXPLICIT = "explicit"        # ?
    IMPLIED = "implied"          # ?
    LEGITIMATE_INTEREST = "legitimate_interest"  # ?
    VITAL_INTEREST = "vital_interest"           # ?
    PUBLIC_TASK = "public_task"                 # ?
    CONTRACT = "contract"                       # ?


class ConsentScope(Enum):
    """?"""
    THERAPEUTIC_SUPPORT = "therapeutic_support"
    PERSONALIZATION = "personalization"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    RESEARCH = "research"
    THIRD_PARTY_SHARING = "third_party_sharing"


class AgeGroup(Enum):
    """?"""
    CHILD = "child"          # 13?
    MINOR = "minor"          # 13-17?
    ADULT = "adult"          # 18?


@dataclass
class ConsentRequest:
    """?"""
    request_id: str
    user_id: str
    scope: ConsentScope
    consent_type: ConsentType
    purpose_description: str
    data_categories: List[str]
    retention_period: timedelta
    third_parties: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    parent_consent_required: bool = False


@dataclass
class ConsentResponse:
    """?"""
    response_id: str
    request_id: str
    user_id: str
    granted: bool
    granted_at: datetime
    ip_address: str
    user_agent: str
    consent_method: str  # "web_form", "mobile_app", "email", etc.
    parent_consent_id: Optional[str] = None
    withdrawal_deadline: Optional[datetime] = None


@dataclass
class ConsentWithdrawal:
    """?"""
    withdrawal_id: str
    response_id: str
    user_id: str
    withdrawn_at: datetime
    reason: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""


class ConsentManagementSystem:
    """?"""
    
    def __init__(self):
        self.consent_requests: Dict[str, ConsentRequest] = {}
        self.consent_responses: Dict[str, ConsentResponse] = {}
        self.consent_withdrawals: Dict[str, ConsentWithdrawal] = {}
        self.user_age_verification: Dict[str, AgeGroup] = {}
        self.parent_child_relationships: Dict[str, str] = {}  # child_id -> parent_id
    
    def verify_user_age(self, user_id: str, birth_date: datetime) -> AgeGroup:
        """ユーザー"""
        age = (datetime.now() - birth_date).days // 365
        
        if age < 13:
            age_group = AgeGroup.CHILD
        elif age < 18:
            age_group = AgeGroup.MINOR
        else:
            age_group = AgeGroup.ADULT
        
        self.user_age_verification[user_id] = age_group
        return age_group
    
    def register_parent_child_relationship(self, parent_id: str, child_id: str) -> bool:
        """?"""
        # ?
        parent_age = self.user_age_verification.get(parent_id)
        if parent_age != AgeGroup.ADULT:
            return False
        
        self.parent_child_relationships[child_id] = parent_id
        return True
    
    def create_consent_request(self, user_id: str, scope: ConsentScope,
                             purpose_description: str, data_categories: List[str],
                             retention_period: timedelta,
                             third_parties: List[str] = None) -> str:
        """?"""
        request_id = str(uuid.uuid4())
        
        # ?
        user_age = self.user_age_verification.get(user_id, AgeGroup.ADULT)
        parent_consent_required = user_age in [AgeGroup.CHILD, AgeGroup.MINOR]
        
        # ?
        consent_type = self._determine_consent_type(scope, data_categories)
        
        request = ConsentRequest(
            request_id=request_id,
            user_id=user_id,
            scope=scope,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_categories=data_categories,
            retention_period=retention_period,
            third_parties=third_parties or [],
            parent_consent_required=parent_consent_required
        )
        
        # ?1?
        if consent_type == ConsentType.EXPLICIT:
            request.expires_at = datetime.now() + timedelta(days=365)
        
        self.consent_requests[request_id] = request
        return request_id
    
    def grant_consent(self, request_id: str, user_id: str, ip_address: str,
                     user_agent: str, consent_method: str = "web_form") -> Optional[str]:
        """?"""
        if request_id not in self.consent_requests:
            return None
        
        request = self.consent_requests[request_id]
        if request.user_id != user_id:
            return None
        
        # ?
        if request.parent_consent_required:
            parent_id = self.parent_child_relationships.get(user_id)
            if not parent_id:
                return None  # ?
        
        response_id = str(uuid.uuid4())
        
        response = ConsentResponse(
            response_id=response_id,
            request_id=request_id,
            user_id=user_id,
            granted=True,
            granted_at=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_method=consent_method
        )
        
        # ?14?
        response.withdrawal_deadline = datetime.now() + timedelta(days=14)
        
        self.consent_responses[response_id] = response
        return response_id
    
    def grant_parent_consent(self, request_id: str, parent_id: str, child_id: str,
                           ip_address: str, user_agent: str) -> Optional[str]:
        """?"""
        if request_id not in self.consent_requests:
            return None
        
        request = self.consent_requests[request_id]
        if request.user_id != child_id:
            return None
        
        # ?
        registered_parent = self.parent_child_relationships.get(child_id)
        if registered_parent != parent_id:
            return None
        
        response_id = str(uuid.uuid4())
        
        response = ConsentResponse(
            response_id=response_id,
            request_id=request_id,
            user_id=child_id,
            granted=True,
            granted_at=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_method="parent_consent",
            parent_consent_id=parent_id
        )
        
        self.consent_responses[response_id] = response
        return response_id
    
    def withdraw_consent(self, response_id: str, user_id: str, reason: str = None,
                        ip_address: str = "", user_agent: str = "") -> bool:
        """?"""
        if response_id not in self.consent_responses:
            return False
        
        response = self.consent_responses[response_id]
        if response.user_id != user_id:
            return False
        
        # ?
        for withdrawal in self.consent_withdrawals.values():
            if withdrawal.response_id == response_id:
                return False  # ?
        
        withdrawal_id = str(uuid.uuid4())
        
        withdrawal = ConsentWithdrawal(
            withdrawal_id=withdrawal_id,
            response_id=response_id,
            user_id=user_id,
            withdrawn_at=datetime.now(),
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.consent_withdrawals[withdrawal_id] = withdrawal
        return True
    
    def check_consent_status(self, user_id: str, scope: ConsentScope) -> Dict:
        """?"""
        user_consents = []
        
        # ユーザー
        for response in self.consent_responses.values():
            if response.user_id == user_id:
                request = self.consent_requests.get(response.request_id)
                if request and request.scope == scope:
                    
                    # ?
                    is_withdrawn = any(
                        w.response_id == response.response_id 
                        for w in self.consent_withdrawals.values()
                    )
                    
                    # ?
                    is_expired = (request.expires_at and 
                                datetime.now() > request.expires_at)
                    
                    user_consents.append({
                        "response_id": response.response_id,
                        "granted": response.granted,
                        "granted_at": response.granted_at.isoformat(),
                        "is_withdrawn": is_withdrawn,
                        "is_expired": is_expired,
                        "is_valid": response.granted and not is_withdrawn and not is_expired
                    })
        
        # ?
        valid_consents = [c for c in user_consents if c["is_valid"]]
        
        return {
            "user_id": user_id,
            "scope": scope.value,
            "has_valid_consent": len(valid_consents) > 0,
            "consent_history": user_consents,
            "latest_consent": valid_consents[-1] if valid_consents else None
        }
    
    def get_user_consent_dashboard(self, user_id: str) -> Dict:
        """ユーザー"""
        dashboard = {
            "user_id": user_id,
            "age_group": self.user_age_verification.get(user_id, AgeGroup.ADULT).value,
            "consents_by_scope": {},
            "total_consents": 0,
            "active_consents": 0,
            "withdrawn_consents": 0
        }
        
        # ?
        for scope in ConsentScope:
            consent_status = self.check_consent_status(user_id, scope)
            dashboard["consents_by_scope"][scope.value] = consent_status
            
            if consent_status["consent_history"]:
                dashboard["total_consents"] += len(consent_status["consent_history"])
                
                if consent_status["has_valid_consent"]:
                    dashboard["active_consents"] += 1
                
                withdrawn_count = sum(1 for c in consent_status["consent_history"] 
                                    if c["is_withdrawn"])
                dashboard["withdrawn_consents"] += withdrawn_count
        
        return dashboard
    
    def generate_consent_form(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.consent_requests:
            return {}
        
        request = self.consent_requests[request_id]
        
        form = {
            "request_id": request_id,
            "title": f"{request.scope.value}に",
            "purpose": request.purpose_description,
            "data_categories": request.data_categories,
            "retention_period": f"{request.retention_period.days}?",
            "third_parties": request.third_parties,
            "consent_type": request.consent_type.value,
            "parent_consent_required": request.parent_consent_required,
            "expires_at": request.expires_at.isoformat() if request.expires_at else None,
            "legal_text": self._generate_legal_text(request),
            "withdrawal_info": "こ"
        }
        
        return form
    
    def bulk_consent_check(self, user_id: str, scopes: List[ConsentScope]) -> Dict[str, bool]:
        """?"""
        results = {}
        
        for scope in scopes:
            consent_status = self.check_consent_status(user_id, scope)
            results[scope.value] = consent_status["has_valid_consent"]
        
        return results
    
    def get_consent_analytics(self) -> Dict:
        """?"""
        total_requests = len(self.consent_requests)
        total_responses = len(self.consent_responses)
        total_withdrawals = len(self.consent_withdrawals)
        
        # ストーリー
        scope_stats = {}
        for scope in ConsentScope:
            scope_requests = [r for r in self.consent_requests.values() if r.scope == scope]
            scope_stats[scope.value] = {
                "requests": len(scope_requests),
                "granted": sum(1 for r in scope_requests 
                             if any(resp.request_id == r.request_id and resp.granted 
                                   for resp in self.consent_responses.values())),
                "withdrawal_rate": 0  # 計算
            }
        
        return {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "total_withdrawals": total_withdrawals,
            "consent_rate": total_responses / total_requests if total_requests > 0 else 0,
            "withdrawal_rate": total_withdrawals / total_responses if total_responses > 0 else 0,
            "scope_statistics": scope_stats
        }
    
    def _determine_consent_type(self, scope: ConsentScope, data_categories: List[str]) -> ConsentType:
        """ストーリー"""
        # ?
        sensitive_categories = ["therapeutic_data", "biometric_data", "location_data"]
        if any(cat in sensitive_categories for cat in data_categories):
            return ConsentType.EXPLICIT
        
        # ?
        if scope in [ConsentScope.MARKETING, ConsentScope.RESEARCH, ConsentScope.THIRD_PARTY_SHARING]:
            return ConsentType.EXPLICIT
        
        # 治療
        if scope == ConsentScope.THERAPEUTIC_SUPPORT:
            return ConsentType.LEGITIMATE_INTEREST
        
        return ConsentType.EXPLICIT
    
    def _generate_legal_text(self, request: ConsentRequest) -> str:
        """?"""
        base_text = f"""
        ?{request.purpose_description}の
        あ
        
        ?{', '.join(request.data_categories)}
        ?{request.retention_period.days}?
        """
        
        if request.third_parties:
            base_text += f"\n?{', '.join(request.third_parties)}"
        
        base_text += """
        
        こ
        ま
        
        ?
        """
        
        if request.parent_consent_required:
            base_text += "\n\n?"
        
        return base_text


class ConsentOptOutManager:
    """?"""
    
    def __init__(self, consent_system: ConsentManagementSystem):
        self.consent_system = consent_system
        self.opt_out_requests: Dict[str, Dict] = {}
    
    def create_opt_out_request(self, user_id: str, scopes: List[ConsentScope] = None) -> str:
        """?"""
        request_id = str(uuid.uuid4())
        
        # ?
        if scopes is None:
            scopes = list(ConsentScope)
        
        opt_out_request = {
            "request_id": request_id,
            "user_id": user_id,
            "scopes": [scope.value for scope in scopes],
            "created_at": datetime.now().isoformat(),
            "processed": False,
            "processing_results": {}
        }
        
        self.opt_out_requests[request_id] = opt_out_request
        return request_id
    
    def process_opt_out_request(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.opt_out_requests:
            return {"success": False, "error": "Request not found"}
        
        opt_out_request = self.opt_out_requests[request_id]
        user_id = opt_out_request["user_id"]
        results = {}
        
        # ?
        for scope_value in opt_out_request["scopes"]:
            scope = ConsentScope(scope_value)
            consent_status = self.consent_system.check_consent_status(user_id, scope)
            
            if consent_status["has_valid_consent"]:
                latest_consent = consent_status["latest_consent"]
                if latest_consent:
                    success = self.consent_system.withdraw_consent(
                        latest_consent["response_id"], 
                        user_id, 
                        "User opt-out request"
                    )
                    results[scope_value] = {"withdrawn": success}
                else:
                    results[scope_value] = {"withdrawn": False, "reason": "No active consent"}
            else:
                results[scope_value] = {"withdrawn": False, "reason": "No valid consent found"}
        
        opt_out_request["processed"] = True
        opt_out_request["processing_results"] = results
        opt_out_request["processed_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "request_id": request_id,
            "results": results
        }
    
    def get_opt_out_status(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.opt_out_requests:
            return {"found": False}
        
        return {
            "found": True,
            "request": self.opt_out_requests[request_id]
        }