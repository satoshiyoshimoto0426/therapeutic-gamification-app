"""
GDPR?12-22?

実装
- ?13-14?: ?
- ?15?: アプリ
- ?16?: ?
- ?17?: ?
- ?18?: ?
- ?19?: ?
- ?20?: デフォルト
- ?21?: ?
- ?22?: 自動
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import uuid
import zipfile
import io
import csv


class DataSubjectRight(Enum):
    """デフォルト"""
    ACCESS = "access"                    # アプリ15?
    RECTIFICATION = "rectification"      # ?16?
    ERASURE = "erasure"                 # ?17?
    RESTRICTION = "restriction"          # ?18?
    PORTABILITY = "portability"         # デフォルト20?
    OBJECTION = "objection"             # ?21?
    AUTOMATED_DECISION = "automated_decision"  # 自動22?


class RequestStatus(Enum):
    """?"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PARTIALLY_COMPLETED = "partially_completed"


class RejectionReason(Enum):
    """?"""
    IDENTITY_NOT_VERIFIED = "identity_not_verified"
    EXCESSIVE_REQUESTS = "excessive_requests"
    LEGAL_OBLIGATION = "legal_obligation"
    PUBLIC_INTEREST = "public_interest"
    LEGITIMATE_INTERESTS = "legitimate_interests"
    FREEDOM_OF_EXPRESSION = "freedom_of_expression"


@dataclass
class DataSubjectRequest:
    """デフォルト"""
    request_id: str
    user_id: str
    right_type: DataSubjectRight
    status: RequestStatus
    submitted_at: datetime
    description: str = ""
    supporting_documents: List[str] = field(default_factory=list)
    identity_verified: bool = False
    response_deadline: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    completed_at: Optional[datetime] = None
    rejection_reason: Optional[RejectionReason] = None
    rejection_details: str = ""
    processing_notes: List[str] = field(default_factory=list)


@dataclass
class DataProcessingRecord:
    """デフォルト"""
    record_id: str
    user_id: str
    data_category: str
    processing_purpose: str
    legal_basis: str
    data_source: str
    retention_period: timedelta
    third_party_recipients: List[str] = field(default_factory=list)
    automated_decision_making: bool = False
    profiling: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class DataSubjectRightsEngine:
    """デフォルト"""
    
    def __init__(self):
        self.requests: Dict[str, DataSubjectRequest] = {}
        self.processing_records: Dict[str, List[DataProcessingRecord]] = {}
        self.user_data_inventory: Dict[str, Dict] = {}
        self.automated_decisions: Dict[str, List[Dict]] = {}
    
    def submit_rights_request(self, user_id: str, right_type: DataSubjectRight,
                            description: str = "", supporting_documents: List[str] = None) -> str:
        """?"""
        request_id = str(uuid.uuid4())
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            right_type=right_type,
            status=RequestStatus.SUBMITTED,
            submitted_at=datetime.now(),
            description=description,
            supporting_documents=supporting_documents or []
        )
        
        self.requests[request_id] = request
        
        # 自動
        if self._can_auto_process(right_type):
            self._start_auto_processing(request_id)
        
        return request_id
    
    def verify_identity(self, request_id: str, verification_data: Dict) -> bool:
        """?"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        
        # ?
        required_fields = ["email", "birth_date", "verification_code"]
        if all(field in verification_data for field in required_fields):
            request.identity_verified = True
            request.processing_notes.append(f"?: {datetime.now().isoformat()}")
            
            if request.status == RequestStatus.SUBMITTED:
                request.status = RequestStatus.UNDER_REVIEW
            
            return True
        
        return False
    
    def process_access_request(self, request_id: str) -> Dict:
        """アプリ15?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        if request.right_type != DataSubjectRight.ACCESS:
            return {"error": "Invalid request type"}
        
        if not request.identity_verified:
            return {"error": "Identity not verified"}
        
        user_id = request.user_id
        
        # ユーザー
        access_data = {
            "request_id": request_id,
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "personal_data": self._collect_personal_data(user_id),
            "processing_activities": self._get_processing_activities(user_id),
            "data_sources": self._get_data_sources(user_id),
            "recipients": self._get_data_recipients(user_id),
            "retention_periods": self._get_retention_periods(user_id),
            "rights_information": self._get_rights_information(),
            "automated_decisions": self._get_automated_decisions(user_id)
        }
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_notes.append("アプリ")
        
        return access_data
    
    def process_rectification_request(self, request_id: str, corrections: Dict) -> Dict:
        """?16?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        if request.right_type != DataSubjectRight.RECTIFICATION:
            return {"error": "Invalid request type"}
        
        if not request.identity_verified:
            return {"error": "Identity not verified"}
        
        user_id = request.user_id
        results = {
            "request_id": request_id,
            "corrections_applied": [],
            "corrections_rejected": [],
            "third_party_notifications": []
        }
        
        # ?
        for field, new_value in corrections.items():
            if self._can_rectify_field(user_id, field):
                old_value = self._get_current_value(user_id, field)
                self._update_field(user_id, field, new_value)
                
                results["corrections_applied"].append({
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "updated_at": datetime.now().isoformat()
                })
                
                # ?
                recipients = self._get_field_recipients(user_id, field)
                for recipient in recipients:
                    self._notify_third_party_correction(recipient, user_id, field, new_value)
                    results["third_party_notifications"].append(recipient)
            
            else:
                results["corrections_rejected"].append({
                    "field": field,
                    "reason": "Field cannot be modified or does not exist"
                })
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_notes.append("?")
        
        return results
    
    def process_erasure_request(self, request_id: str) -> Dict:
        """?17?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        if request.right_type != DataSubjectRight.ERASURE:
            return {"error": "Invalid request type"}
        
        if not request.identity_verified:
            return {"error": "Identity not verified"}
        
        user_id = request.user_id
        
        # ?
        erasure_assessment = self._assess_erasure_eligibility(user_id)
        
        results = {
            "request_id": request_id,
            "data_erased": [],
            "data_retained": [],
            "third_party_notifications": [],
            "assessment": erasure_assessment
        }
        
        # ?
        for data_category, can_erase in erasure_assessment["categories"].items():
            if can_erase["eligible"]:
                self._erase_data_category(user_id, data_category)
                results["data_erased"].append({
                    "category": data_category,
                    "erased_at": datetime.now().isoformat()
                })
                
                # ?
                recipients = self._get_category_recipients(user_id, data_category)
                for recipient in recipients:
                    self._notify_third_party_erasure(recipient, user_id, data_category)
                    results["third_party_notifications"].append(recipient)
            
            else:
                results["data_retained"].append({
                    "category": data_category,
                    "reason": can_erase["reason"]
                })
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_notes.append("?")
        
        return results
    
    def process_portability_request(self, request_id: str, format_type: str = "json") -> Dict:
        """デフォルト20?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        if request.right_type != DataSubjectRight.PORTABILITY:
            return {"error": "Invalid request type"}
        
        if not request.identity_verified:
            return {"error": "Identity not verified"}
        
        user_id = request.user_id
        
        # ?
        portable_data = self._collect_portable_data(user_id)
        
        # ?
        if format_type == "json":
            export_data = self._export_as_json(portable_data)
        elif format_type == "csv":
            export_data = self._export_as_csv(portable_data)
        elif format_type == "xml":
            export_data = self._export_as_xml(portable_data)
        else:
            export_data = self._export_as_json(portable_data)  # デフォルト
        
        results = {
            "request_id": request_id,
            "user_id": user_id,
            "export_format": format_type,
            "data_categories": list(portable_data.keys()),
            "export_data": export_data,
            "generated_at": datetime.now().isoformat(),
            "download_expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_notes.append("デフォルト")
        
        return results
    
    def process_restriction_request(self, request_id: str, restriction_scope: List[str]) -> Dict:
        """?18?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        if request.right_type != DataSubjectRight.RESTRICTION:
            return {"error": "Invalid request type"}
        
        if not request.identity_verified:
            return {"error": "Identity not verified"}
        
        user_id = request.user_id
        results = {
            "request_id": request_id,
            "restrictions_applied": [],
            "restrictions_rejected": []
        }
        
        for scope in restriction_scope:
            if self._can_restrict_processing(user_id, scope):
                self._apply_processing_restriction(user_id, scope)
                results["restrictions_applied"].append({
                    "scope": scope,
                    "restricted_at": datetime.now().isoformat()
                })
            else:
                results["restrictions_rejected"].append({
                    "scope": scope,
                    "reason": "Cannot restrict processing for this scope"
                })
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_notes.append("?")
        
        return results
    
    def get_processing_transparency_info(self, user_id: str) -> Dict:
        """?13-14?"""
        return {
            "user_id": user_id,
            "controller_info": {
                "name": "治療",
                "contact": "privacy@therapeutic-app.com",
                "dpo_contact": "dpo@therapeutic-app.com"
            },
            "processing_purposes": self._get_processing_purposes(user_id),
            "legal_bases": self._get_legal_bases(user_id),
            "data_categories": self._get_data_categories(user_id),
            "recipients": self._get_data_recipients(user_id),
            "retention_periods": self._get_retention_periods(user_id),
            "international_transfers": self._get_international_transfers(user_id),
            "automated_decision_making": self._get_automated_decision_info(user_id),
            "data_subject_rights": self._get_available_rights(),
            "complaint_authority": {
                "name": "?",
                "website": "https://www.ppc.go.jp/",
                "contact": "complaint@ppc.go.jp"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_request_status(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.requests:
            return {"error": "Request not found"}
        
        request = self.requests[request_id]
        
        return {
            "request_id": request_id,
            "status": request.status.value,
            "submitted_at": request.submitted_at.isoformat(),
            "response_deadline": request.response_deadline.isoformat(),
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "identity_verified": request.identity_verified,
            "processing_notes": request.processing_notes,
            "days_remaining": (request.response_deadline - datetime.now()).days
        }
    
    def get_user_rights_dashboard(self, user_id: str) -> Dict:
        """ユーザー"""
        user_requests = [req for req in self.requests.values() if req.user_id == user_id]
        
        dashboard = {
            "user_id": user_id,
            "available_rights": [right.value for right in DataSubjectRight],
            "request_history": [],
            "pending_requests": 0,
            "completed_requests": 0,
            "transparency_info": self.get_processing_transparency_info(user_id)
        }
        
        for request in user_requests:
            dashboard["request_history"].append({
                "request_id": request.request_id,
                "right_type": request.right_type.value,
                "status": request.status.value,
                "submitted_at": request.submitted_at.isoformat(),
                "completed_at": request.completed_at.isoformat() if request.completed_at else None
            })
            
            if request.status in [RequestStatus.SUBMITTED, RequestStatus.UNDER_REVIEW, RequestStatus.IN_PROGRESS]:
                dashboard["pending_requests"] += 1
            elif request.status == RequestStatus.COMPLETED:
                dashboard["completed_requests"] += 1
        
        return dashboard
    
    # プレビュー
    def _can_auto_process(self, right_type: DataSubjectRight) -> bool:
        """自動"""
        auto_processable = [DataSubjectRight.ACCESS, DataSubjectRight.PORTABILITY]
        return right_type in auto_processable
    
    def _start_auto_processing(self, request_id: str):
        """自動"""
        request = self.requests[request_id]
        request.status = RequestStatus.IN_PROGRESS
        request.processing_notes.append("自動")
    
    def _collect_personal_data(self, user_id: str) -> Dict:
        """?"""
        return self.user_data_inventory.get(user_id, {})
    
    def _get_processing_activities(self, user_id: str) -> List[Dict]:
        """?"""
        records = self.processing_records.get(user_id, [])
        return [
            {
                "purpose": record.processing_purpose,
                "legal_basis": record.legal_basis,
                "data_category": record.data_category,
                "retention_period": record.retention_period.days
            }
            for record in records
        ]
    
    def _get_data_sources(self, user_id: str) -> List[str]:
        """デフォルト"""
        records = self.processing_records.get(user_id, [])
        return list(set(record.data_source for record in records))
    
    def _get_data_recipients(self, user_id: str) -> List[str]:
        """デフォルト"""
        records = self.processing_records.get(user_id, [])
        recipients = []
        for record in records:
            recipients.extend(record.third_party_recipients)
        return list(set(recipients))
    
    def _get_retention_periods(self, user_id: str) -> Dict[str, int]:
        """?"""
        records = self.processing_records.get(user_id, [])
        return {
            record.data_category: record.retention_period.days
            for record in records
        }
    
    def _get_automated_decisions(self, user_id: str) -> List[Dict]:
        """自動"""
        return self.automated_decisions.get(user_id, [])
    
    def _get_rights_information(self) -> Dict:
        """?"""
        return {
            "access": "あ",
            "rectification": "?",
            "erasure": "?",
            "restriction": "?",
            "portability": "?",
            "objection": "?"
        }
    
    def _assess_erasure_eligibility(self, user_id: str) -> Dict:
        """?"""
        # ?
        return {
            "overall_eligible": True,
            "categories": {
                "profile_data": {"eligible": True, "reason": ""},
                "therapeutic_data": {"eligible": False, "reason": "?"},
                "behavioral_data": {"eligible": True, "reason": ""},
                "communication_data": {"eligible": True, "reason": ""}
            }
        }
    
    def _collect_portable_data(self, user_id: str) -> Dict:
        """?"""
        # ユーザー
        all_data = self.user_data_inventory.get(user_id, {})
        portable_categories = ["profile_data", "preferences", "user_generated_content"]
        
        return {
            category: data for category, data in all_data.items()
            if category in portable_categories
        }
    
    def _export_as_json(self, data: Dict) -> str:
        """JSON?"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _export_as_csv(self, data: Dict) -> str:
        """CSV?"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘルパー
        writer.writerow(["Category", "Field", "Value"])
        
        # デフォルト
        for category, fields in data.items():
            if isinstance(fields, dict):
                for field, value in fields.items():
                    writer.writerow([category, field, str(value)])
            else:
                writer.writerow([category, "", str(fields)])
        
        return output.getvalue()
    
    def _export_as_xml(self, data: Dict) -> str:
        """XML?"""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<personal_data>']
        
        for category, fields in data.items():
            xml_lines.append(f'  <{category}>')
            if isinstance(fields, dict):
                for field, value in fields.items():
                    xml_lines.append(f'    <{field}>{value}</{field}>')
            else:
                xml_lines.append(f'    <value>{fields}</value>')
            xml_lines.append(f'  </{category}>')
        
        xml_lines.append('</personal_data>')
        return '\n'.join(xml_lines)
    
    def _get_processing_purposes(self, user_id: str) -> List[str]:
        """?"""
        records = self.processing_records.get(user_id, [])
        return list(set(record.processing_purpose for record in records))
    
    def _get_legal_bases(self, user_id: str) -> List[str]:
        """?"""
        records = self.processing_records.get(user_id, [])
        return list(set(record.legal_basis for record in records))
    
    def _get_data_categories(self, user_id: str) -> List[str]:
        """デフォルト"""
        records = self.processing_records.get(user_id, [])
        return list(set(record.data_category for record in records))
    
    def _get_international_transfers(self, user_id: str) -> List[Dict]:
        """?"""
        # ?
        return []
    
    def _get_automated_decision_info(self, user_id: str) -> Dict:
        """自動"""
        decisions = self.automated_decisions.get(user_id, [])
        return {
            "exists": len(decisions) > 0,
            "decisions": decisions,
            "opt_out_available": True
        }
    
    def _get_available_rights(self) -> List[str]:
        """?"""
        return [right.value for right in DataSubjectRight]
    
    # デフォルト
    def _can_rectify_field(self, user_id: str, field: str) -> bool:
        """?"""
        return True  # ?
    
    def _get_current_value(self, user_id: str, field: str) -> Any:
        """?"""
        return "current_value"  # ?
    
    def _update_field(self, user_id: str, field: str, new_value: Any):
        """?"""
        pass  # ?
    
    def _get_field_recipients(self, user_id: str, field: str) -> List[str]:
        """?"""
        return []  # ?
    
    def _notify_third_party_correction(self, recipient: str, user_id: str, field: str, new_value: Any):
        """?"""
        pass  # ?
    
    def _erase_data_category(self, user_id: str, category: str):
        """デフォルト"""
        pass  # ?
    
    def _get_category_recipients(self, user_id: str, category: str) -> List[str]:
        """カスタム"""
        return []  # ?
    
    def _notify_third_party_erasure(self, recipient: str, user_id: str, category: str):
        """?"""
        pass  # ?
    
    def _can_restrict_processing(self, user_id: str, scope: str) -> bool:
        """?"""
        return True  # ?
    
    def _apply_processing_restriction(self, user_id: str, scope: str):
        """?"""
        pass  # ?


class DataTransparencyEngine:
    """デフォルト"""
    
    def __init__(self):
        self.processing_notices: Dict[str, Dict] = {}
        self.privacy_policies: Dict[str, Dict] = {}
    
    def generate_processing_notice(self, user_id: str, processing_context: str) -> Dict:
        """?13-14?"""
        notice_id = str(uuid.uuid4())
        
        notice = {
            "notice_id": notice_id,
            "user_id": user_id,
            "processing_context": processing_context,
            "controller_identity": "治療",
            "controller_contact": "privacy@therapeutic-app.com",
            "dpo_contact": "dpo@therapeutic-app.com",
            "processing_purposes": self._get_context_purposes(processing_context),
            "legal_basis": self._get_context_legal_basis(processing_context),
            "legitimate_interests": self._get_legitimate_interests(processing_context),
            "data_categories": self._get_context_data_categories(processing_context),
            "recipients": self._get_context_recipients(processing_context),
            "international_transfers": self._get_context_transfers(processing_context),
            "retention_period": self._get_context_retention(processing_context),
            "data_subject_rights": self._get_applicable_rights(processing_context),
            "withdrawal_info": self._get_withdrawal_info(processing_context),
            "automated_decision_making": self._get_context_automation(processing_context),
            "data_source": self._get_data_source_info(processing_context),
            "generated_at": datetime.now().isoformat()
        }
        
        self.processing_notices[notice_id] = notice
        return notice
    
    def update_privacy_policy(self, version: str, changes: Dict) -> str:
        """プレビュー"""
        policy_id = str(uuid.uuid4())
        
        policy = {
            "policy_id": policy_id,
            "version": version,
            "effective_date": datetime.now().isoformat(),
            "changes": changes,
            "full_policy": self._generate_full_policy(),
            "notification_sent": False
        }
        
        self.privacy_policies[policy_id] = policy
        return policy_id
    
    def _get_context_purposes(self, context: str) -> List[str]:
        """コア"""
        purposes_map = {
            "registration": ["アプリ", "?"],
            "therapeutic": ["治療", "?"],
            "analytics": ["?", "使用"],
            "marketing": ["?", "?"]
        }
        return purposes_map.get(context, ["一般"])
    
    def _get_context_legal_basis(self, context: str) -> str:
        """コア"""
        basis_map = {
            "registration": "?",
            "therapeutic": "?",
            "analytics": "?",
            "marketing": "?"
        }
        return basis_map.get(context, "?")
    
    def _get_legitimate_interests(self, context: str) -> Optional[str]:
        """?"""
        if context == "therapeutic":
            return "ユーザー"
        return None
    
    def _get_context_data_categories(self, context: str) -> List[str]:
        """コア"""
        categories_map = {
            "registration": ["基本", "?"],
            "therapeutic": ["治療", "?"],
            "analytics": ["使用", "?"],
            "marketing": ["?", "?"]
        }
        return categories_map.get(context, ["一般"])
    
    def _get_context_recipients(self, context: str) -> List[str]:
        """コア"""
        recipients_map = {
            "therapeutic": ["治療", "?"],
            "analytics": ["?"],
            "marketing": ["?"]
        }
        return recipients_map.get(context, [])
    
    def _get_context_transfers(self, context: str) -> List[Dict]:
        """コア"""
        # ?
        return []
    
    def _get_context_retention(self, context: str) -> str:
        """コア"""
        retention_map = {
            "registration": "アプリ",
            "therapeutic": "7?",
            "analytics": "3?",
            "marketing": "?"
        }
        return retention_map.get(context, "?")
    
    def _get_applicable_rights(self, context: str) -> List[str]:
        """?"""
        return [right.value for right in DataSubjectRight]
    
    def _get_withdrawal_info(self, context: str) -> Optional[str]:
        """?"""
        if self._get_context_legal_basis(context) == "?":
            return "こ"
        return None
    
    def _get_context_automation(self, context: str) -> Dict:
        """コア"""
        automation_map = {
            "therapeutic": {
                "exists": True,
                "description": "AIに",
                "logic": "?",
                "significance": "治療",
                "opt_out_available": True
            }
        }
        return automation_map.get(context, {"exists": False})
    
    def _get_data_source_info(self, context: str) -> str:
        """デフォルト"""
        source_map = {
            "registration": "ユーザー",
            "therapeutic": "アプリ",
            "analytics": "システム"
        }
        return source_map.get(context, "?")
    
    def _generate_full_policy(self) -> Dict:
        """?"""
        return {
            "controller_info": "治療",
            "processing_purposes": ["治療", "?", "安全"],
            "legal_bases": ["?", "?", "?"],
            "data_categories": ["基本", "治療", "?"],
            "retention_periods": "?",
            "data_subject_rights": "アプリ",
            "contact_info": "privacy@therapeutic-app.com",
            "last_updated": datetime.now().isoformat()
        }