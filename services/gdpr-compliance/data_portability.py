"""
GDPR?20?

?
- ?
- ?JSON?CSV?XML?
- ?
- デフォルト
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, BinaryIO, Union
from datetime import datetime, timedelta
import json
import csv
import xml.etree.ElementTree as ET
import zipfile
import io
import hashlib
import uuid


class ExportFormat(Enum):
    """エラー"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"
    PARQUET = "parquet"


class DataPortabilityScope(Enum):
    """デフォルト"""
    ALL_DATA = "all_data"
    PROFILE_ONLY = "profile_only"
    THERAPEUTIC_DATA = "therapeutic_data"
    USER_GENERATED = "user_generated"
    PREFERENCES = "preferences"
    CUSTOM = "custom"


@dataclass
class PortabilityRequest:
    """?"""
    request_id: str
    user_id: str
    scope: DataPortabilityScope
    format: ExportFormat
    custom_categories: List[str] = field(default_factory=list)
    include_metadata: bool = True
    compress_output: bool = True
    direct_transfer: Optional[str] = None  # ?
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    processed: bool = False
    download_count: int = 0
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None


@dataclass
class DataSchema:
    """デフォルト"""
    category: str
    fields: Dict[str, str]  # field_name -> data_type
    relationships: List[str] = field(default_factory=list)
    portable: bool = True
    format_specific_rules: Dict[str, Dict] = field(default_factory=dict)


class DataPortabilityEngine:
    """デフォルト"""
    
    def __init__(self):
        self.portability_requests: Dict[str, PortabilityRequest] = {}
        self.data_schemas = self._initialize_data_schemas()
        self.export_handlers = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.CSV: self._export_csv,
            ExportFormat.XML: self._export_xml,
            ExportFormat.YAML: self._export_yaml
        }
    
    def _initialize_data_schemas(self) -> Dict[str, DataSchema]:
        """デフォルト"""
        return {
            "user_profile": DataSchema(
                category="user_profile",
                fields={
                    "user_id": "string",
                    "username": "string",
                    "email": "string",
                    "birth_date": "date",
                    "created_at": "datetime",
                    "last_login": "datetime"
                },
                portable=True
            ),
            "therapeutic_data": DataSchema(
                category="therapeutic_data",
                fields={
                    "session_id": "string",
                    "mood_score": "integer",
                    "anxiety_level": "integer",
                    "task_completion_rate": "float",
                    "session_duration": "integer",
                    "notes": "text",
                    "timestamp": "datetime"
                },
                portable=True,
                format_specific_rules={
                    "csv": {"flatten_nested": True},
                    "xml": {"use_attributes": False}
                }
            ),
            "game_progress": DataSchema(
                category="game_progress",
                fields={
                    "level": "integer",
                    "xp": "integer",
                    "crystal_progress": "json",
                    "completed_tasks": "json",
                    "achievements": "json",
                    "last_updated": "datetime"
                },
                portable=True
            ),
            "preferences": DataSchema(
                category="preferences",
                fields={
                    "language": "string",
                    "timezone": "string",
                    "notification_settings": "json",
                    "privacy_settings": "json",
                    "accessibility_settings": "json"
                },
                portable=True
            ),
            "user_generated_content": DataSchema(
                category="user_generated_content",
                fields={
                    "content_id": "string",
                    "content_type": "string",
                    "title": "string",
                    "body": "text",
                    "tags": "json",
                    "created_at": "datetime",
                    "modified_at": "datetime"
                },
                portable=True
            ),
            "interaction_history": DataSchema(
                category="interaction_history",
                fields={
                    "interaction_id": "string",
                    "interaction_type": "string",
                    "timestamp": "datetime",
                    "context": "json",
                    "response": "json"
                },
                portable=True,
                format_specific_rules={
                    "csv": {"max_rows_per_file": 10000}
                }
            )
        }
    
    def create_portability_request(self, user_id: str, scope: DataPortabilityScope,
                                 format: ExportFormat, custom_categories: List[str] = None,
                                 include_metadata: bool = True, compress_output: bool = True,
                                 direct_transfer: str = None) -> str:
        """?"""
        request_id = str(uuid.uuid4())
        
        request = PortabilityRequest(
            request_id=request_id,
            user_id=user_id,
            scope=scope,
            format=format,
            custom_categories=custom_categories or [],
            include_metadata=include_metadata,
            compress_output=compress_output,
            direct_transfer=direct_transfer
        )
        
        self.portability_requests[request_id] = request
        return request_id
    
    def process_portability_request(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.portability_requests:
            return {"error": "Request not found"}
        
        request = self.portability_requests[request_id]
        
        if request.processed:
            return {"error": "Request already processed"}
        
        try:
            # デフォルト
            data_to_export = self._collect_portable_data(request.user_id, request.scope, request.custom_categories)
            
            # メイン
            if request.include_metadata:
                data_to_export = self._add_metadata(data_to_export, request)
            
            # ?
            export_handler = self.export_handlers.get(request.format)
            if not export_handler:
                return {"error": f"Unsupported format: {request.format.value}"}
            
            exported_data = export_handler(data_to_export, request.user_id)
            
            # ?
            if request.compress_output:
                exported_data = self._compress_data(exported_data, request.format)
            
            # ?
            file_path = self._save_export_file(request_id, exported_data)
            file_size = len(exported_data) if isinstance(exported_data, (str, bytes)) else 0
            checksum = self._calculate_checksum(exported_data)
            
            # ?
            request.processed = True
            request.file_path = file_path
            request.file_size = file_size
            request.checksum = checksum
            
            # ?
            transfer_result = None
            if request.direct_transfer:
                transfer_result = self._perform_direct_transfer(request, exported_data)
            
            return {
                "success": True,
                "request_id": request_id,
                "file_path": file_path,
                "file_size": file_size,
                "checksum": checksum,
                "format": request.format.value,
                "expires_at": request.expires_at.isoformat(),
                "direct_transfer": transfer_result
            }
        
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}
    
    def download_export(self, request_id: str, user_id: str) -> Optional[bytes]:
        """エラー"""
        if request_id not in self.portability_requests:
            return None
        
        request = self.portability_requests[request_id]
        
        if request.user_id != user_id:
            return None
        
        if not request.processed or not request.file_path:
            return None
        
        if datetime.now() > request.expires_at:
            return None
        
        # ?
        request.download_count += 1
        
        # ?
        try:
            with open(request.file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def get_portability_status(self, request_id: str) -> Dict:
        """?"""
        if request_id not in self.portability_requests:
            return {"error": "Request not found"}
        
        request = self.portability_requests[request_id]
        
        return {
            "request_id": request_id,
            "user_id": request.user_id,
            "scope": request.scope.value,
            "format": request.format.value,
            "processed": request.processed,
            "created_at": request.created_at.isoformat(),
            "expires_at": request.expires_at.isoformat(),
            "file_size": request.file_size,
            "download_count": request.download_count,
            "checksum": request.checksum,
            "days_until_expiry": (request.expires_at - datetime.now()).days
        }
    
    def validate_data_integrity(self, request_id: str, provided_checksum: str) -> bool:
        """デフォルト"""
        if request_id not in self.portability_requests:
            return False
        
        request = self.portability_requests[request_id]
        return request.checksum == provided_checksum
    
    def get_supported_formats(self) -> Dict[str, Dict]:
        """?"""
        return {
            "json": {
                "name": "JSON",
                "description": "JavaScript Object Notation",
                "mime_type": "application/json",
                "extension": ".json",
                "structured": True,
                "human_readable": True
            },
            "csv": {
                "name": "CSV",
                "description": "Comma-Separated Values",
                "mime_type": "text/csv",
                "extension": ".csv",
                "structured": True,
                "human_readable": True
            },
            "xml": {
                "name": "XML",
                "description": "eXtensible Markup Language",
                "mime_type": "application/xml",
                "extension": ".xml",
                "structured": True,
                "human_readable": True
            },
            "yaml": {
                "name": "YAML",
                "description": "YAML Ain't Markup Language",
                "mime_type": "application/x-yaml",
                "extension": ".yaml",
                "structured": True,
                "human_readable": True
            }
        }
    
    def _collect_portable_data(self, user_id: str, scope: DataPortabilityScope, 
                             custom_categories: List[str]) -> Dict:
        """?"""
        data = {}
        
        if scope == DataPortabilityScope.ALL_DATA:
            categories = list(self.data_schemas.keys())
        elif scope == DataPortabilityScope.PROFILE_ONLY:
            categories = ["user_profile", "preferences"]
        elif scope == DataPortabilityScope.THERAPEUTIC_DATA:
            categories = ["therapeutic_data", "game_progress"]
        elif scope == DataPortabilityScope.USER_GENERATED:
            categories = ["user_generated_content", "interaction_history"]
        elif scope == DataPortabilityScope.PREFERENCES:
            categories = ["preferences"]
        elif scope == DataPortabilityScope.CUSTOM:
            categories = custom_categories
        else:
            categories = []
        
        for category in categories:
            if category in self.data_schemas and self.data_schemas[category].portable:
                data[category] = self._get_category_data(user_id, category)
        
        return data
    
    def _get_category_data(self, user_id: str, category: str) -> List[Dict]:
        """カスタム"""
        # 実装
        # こ
        sample_data = {
            "user_profile": [
                {
                    "user_id": user_id,
                    "username": "sample_user",
                    "email": "user@example.com",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "therapeutic_data": [
                {
                    "session_id": "session_001",
                    "mood_score": 4,
                    "anxiety_level": 2,
                    "task_completion_rate": 0.8,
                    "timestamp": "2024-01-01T10:00:00Z"
                }
            ],
            "game_progress": [
                {
                    "level": 15,
                    "xp": 2500,
                    "crystal_progress": {"self_discipline": 80, "empathy": 60},
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            ]
        }
        
        return sample_data.get(category, [])
    
    def _add_metadata(self, data: Dict, request: PortabilityRequest) -> Dict:
        """メイン"""
        metadata = {
            "export_info": {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "export_date": datetime.now().isoformat(),
                "scope": request.scope.value,
                "format": request.format.value,
                "data_categories": list(data.keys()),
                "total_records": sum(len(records) if isinstance(records, list) else 1 
                                   for records in data.values())
            },
            "schema_info": {
                category: {
                    "fields": self.data_schemas[category].fields,
                    "relationships": self.data_schemas[category].relationships
                }
                for category in data.keys()
                if category in self.data_schemas
            },
            "legal_info": {
                "data_controller": "治療",
                "legal_basis": "GDPR?20?",
                "retention_notice": "こ30?",
                "contact": "privacy@therapeutic-app.com"
            }
        }
        
        return {
            "_metadata": metadata,
            "data": data
        }
    
    def _export_json(self, data: Dict, user_id: str) -> str:
        """JSON?"""
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    
    def _export_csv(self, data: Dict, user_id: str) -> bytes:
        """CSV?"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for category, records in data.items():
                if category.startswith('_'):  # メイン
                    continue
                
                if not isinstance(records, list):
                    records = [records]
                
                csv_buffer = io.StringIO()
                
                if records:
                    # ヘルパー
                    fieldnames = list(records[0].keys())
                    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # デフォルト
                    for record in records:
                        # JSON ?
                        processed_record = {}
                        for key, value in record.items():
                            if isinstance(value, (dict, list)):
                                processed_record[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                processed_record[key] = value
                        writer.writerow(processed_record)
                
                zip_file.writestr(f"{category}.csv", csv_buffer.getvalue().encode('utf-8'))
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def _export_xml(self, data: Dict, user_id: str) -> str:
        """XML?"""
        root = ET.Element("personal_data_export")
        root.set("user_id", user_id)
        root.set("export_date", datetime.now().isoformat())
        
        for category, records in data.items():
            if category.startswith('_'):  # メイン
                continue
            
            category_element = ET.SubElement(root, category)
            
            if not isinstance(records, list):
                records = [records]
            
            for record in records:
                record_element = ET.SubElement(category_element, "record")
                
                for key, value in record.items():
                    field_element = ET.SubElement(record_element, key)
                    if isinstance(value, (dict, list)):
                        field_element.text = json.dumps(value, ensure_ascii=False)
                    else:
                        field_element.text = str(value)
        
        # メイン
        if "_metadata" in data:
            metadata_element = ET.SubElement(root, "metadata")
            self._add_dict_to_xml(metadata_element, data["_metadata"])
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _export_yaml(self, data: Dict, user_id: str) -> str:
        """YAML?"""
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # yaml?JSONで
            return self._export_json(data, user_id)
    
    def _add_dict_to_xml(self, parent: ET.Element, data: Dict):
        """?XML?"""
        for key, value in data.items():
            element = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self._add_dict_to_xml(element, value)
            elif isinstance(value, list):
                for item in value:
                    item_element = ET.SubElement(element, "item")
                    if isinstance(item, dict):
                        self._add_dict_to_xml(item_element, item)
                    else:
                        item_element.text = str(item)
            else:
                element.text = str(value)
    
    def _compress_data(self, data: Union[str, bytes], format: ExportFormat) -> bytes:
        """デフォルト"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            filename = f"personal_data_export.{format.value}"
            zip_file.writestr(filename, data)
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def _save_export_file(self, request_id: str, data: Union[str, bytes]) -> str:
        """エラー"""
        # 実装
        file_path = f"/tmp/export_{request_id}.zip"
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        with open(file_path, 'wb') as f:
            f.write(data)
        
        return file_path
    
    def _calculate_checksum(self, data: Union[str, bytes]) -> str:
        """?"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    def _perform_direct_transfer(self, request: PortabilityRequest, data: Union[str, bytes]) -> Dict:
        """?"""
        # 実装APIを
        return {
            "success": False,
            "message": "Direct transfer not implemented",
            "destination": request.direct_transfer
        }


class DataPortabilityValidator:
    """デフォルト"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict:
        """検証"""
        return {
            "completeness": {
                "required_categories": ["user_profile"],
                "optional_categories": ["therapeutic_data", "preferences"]
            },
            "format_compliance": {
                "json": {"valid_json": True, "encoding": "utf-8"},
                "csv": {"valid_csv": True, "delimiter": ",", "encoding": "utf-8"},
                "xml": {"valid_xml": True, "encoding": "utf-8"}
            },
            "data_integrity": {
                "no_corruption": True,
                "consistent_ids": True,
                "valid_timestamps": True
            }
        }
    
    def validate_export(self, request_id: str, exported_data: Union[str, bytes]) -> Dict:
        """エラー"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0.0,
            "format_compliance": True,
            "data_integrity": True
        }
        
        try:
            # ?
            format_result = self._validate_format(exported_data)
            validation_result["format_compliance"] = format_result["valid"]
            if not format_result["valid"]:
                validation_result["errors"].extend(format_result["errors"])
            
            # ?
            completeness_result = self._validate_completeness(exported_data)
            validation_result["completeness_score"] = completeness_result["score"]
            if completeness_result["warnings"]:
                validation_result["warnings"].extend(completeness_result["warnings"])
            
            # デフォルト
            integrity_result = self._validate_data_integrity(exported_data)
            validation_result["data_integrity"] = integrity_result["valid"]
            if not integrity_result["valid"]:
                validation_result["errors"].extend(integrity_result["errors"])
            
            validation_result["valid"] = (
                validation_result["format_compliance"] and
                validation_result["data_integrity"] and
                validation_result["completeness_score"] >= 0.8
            )
        
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _validate_format(self, data: Union[str, bytes]) -> Dict:
        """?"""
        # ?
        return {"valid": True, "errors": []}
    
    def _validate_completeness(self, data: Union[str, bytes]) -> Dict:
        """?"""
        # ?
        return {"score": 1.0, "warnings": []}
    
    def _validate_data_integrity(self, data: Union[str, bytes]) -> Dict:
        """デフォルト"""
        # ?
        return {"valid": True, "errors": []}