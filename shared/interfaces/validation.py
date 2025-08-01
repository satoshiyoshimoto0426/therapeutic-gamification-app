"""
Validation Interface

バリデーション機能のインターフェース定義
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from .core_types import TaskType, TaskStatus, CrystalAttribute


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class ValidationResult(BaseModel):
    """バリデーション結果"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    field_errors: Dict[str, List[str]] = {}
    
    def add_error(self, message: str, field: str = None):
        """エラー追加"""
        self.is_valid = False
        self.errors.append(message)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message: str):
        """警告追加"""
        self.warnings.append(message)


class BaseValidator:
    """基本バリデーター"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> ValidationResult:
        """必須チェック"""
        result = ValidationResult(is_valid=True)
        
        if value is None or (isinstance(value, str) and not value.strip()):
            result.add_error(f"{field_name}は必須です", field_name)
        
        return result
    
    @staticmethod
    def validate_string_length(
        value: str, 
        field_name: str, 
        min_length: int = None, 
        max_length: int = None
    ) -> ValidationResult:
        """文字列長チェック"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, str):
            result.add_error(f"{field_name}は文字列である必要があります", field_name)
            return result
        
        length = len(value.strip())
        
        if min_length is not None and length < min_length:
            result.add_error(f"{field_name}は{min_length}文字以上である必要があります", field_name)
        
        if max_length is not None and length > max_length:
            result.add_error(f"{field_name}は{max_length}文字以下である必要があります", field_name)
        
        return result
    
    @staticmethod
    def validate_numeric_range(
        value: Union[int, float], 
        field_name: str, 
        min_value: Union[int, float] = None, 
        max_value: Union[int, float] = None
    ) -> ValidationResult:
        """数値範囲チェック"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, (int, float)):
            result.add_error(f"{field_name}は数値である必要があります", field_name)
            return result
        
        if min_value is not None and value < min_value:
            result.add_error(f"{field_name}は{min_value}以上である必要があります", field_name)
        
        if max_value is not None and value > max_value:
            result.add_error(f"{field_name}は{max_value}以下である必要があります", field_name)
        
        return result
    
    @staticmethod
    def validate_email(email: str, field_name: str = "email") -> ValidationResult:
        """メールアドレスチェック"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(email, str):
            result.add_error(f"{field_name}は文字列である必要があります", field_name)
            return result
        
        email = email.strip()
        
        # 簡単なメールアドレス形式チェック
        if "@" not in email or "." not in email.split("@")[-1]:
            result.add_error(f"{field_name}の形式が正しくありません", field_name)
        
        return result
    
    @staticmethod
    def validate_date_range(
        date_value: Union[datetime, date], 
        field_name: str,
        min_date: Union[datetime, date] = None,
        max_date: Union[datetime, date] = None
    ) -> ValidationResult:
        """日付範囲チェック"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(date_value, (datetime, date)):
            result.add_error(f"{field_name}は日付である必要があります", field_name)
            return result
        
        if min_date is not None and date_value < min_date:
            result.add_error(f"{field_name}は{min_date}以降である必要があります", field_name)
        
        if max_date is not None and date_value > max_date:
            result.add_error(f"{field_name}は{max_date}以前である必要があります", field_name)
        
        return result


class TaskValidator(BaseValidator):
    """タスクバリデーター"""
    
    @classmethod
    def validate_task_creation(cls, task_data: Dict[str, Any]) -> ValidationResult:
        """タスク作成バリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 必須フィールドチェック
        required_fields = ["title", "task_type", "difficulty"]
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                result.add_error(f"{field}は必須です", field)
        
        # タイトルチェック
        if "title" in task_data:
            title_result = cls.validate_string_length(
                task_data["title"], "title", min_length=1, max_length=100
            )
            if not title_result.is_valid:
                result.errors.extend(title_result.errors)
                result.field_errors.update(title_result.field_errors)
        
        # 説明チェック
        if "description" in task_data and task_data["description"]:
            desc_result = cls.validate_string_length(
                task_data["description"], "description", max_length=500
            )
            if not desc_result.is_valid:
                result.errors.extend(desc_result.errors)
                result.field_errors.update(desc_result.field_errors)
        
        # 難易度チェック
        if "difficulty" in task_data:
            diff_result = cls.validate_numeric_range(
                task_data["difficulty"], "difficulty", min_value=1, max_value=5
            )
            if not diff_result.is_valid:
                result.errors.extend(diff_result.errors)
                result.field_errors.update(diff_result.field_errors)
        
        # 推定時間チェック
        if "estimated_duration" in task_data:
            duration_result = cls.validate_numeric_range(
                task_data["estimated_duration"], "estimated_duration", 
                min_value=5, max_value=480
            )
            if not duration_result.is_valid:
                result.errors.extend(duration_result.errors)
                result.field_errors.update(duration_result.field_errors)
        
        # タスクタイプチェック
        if "task_type" in task_data:
            try:
                TaskType(task_data["task_type"])
            except ValueError:
                result.add_error("無効なタスクタイプです", "task_type")
        
        # 期限チェック
        if "due_date" in task_data and task_data["due_date"]:
            try:
                due_date = datetime.fromisoformat(task_data["due_date"].replace('Z', '+00:00'))
                date_result = cls.validate_date_range(
                    due_date, "due_date", min_date=datetime.utcnow()
                )
                if not date_result.is_valid:
                    result.errors.extend(date_result.errors)
                    result.field_errors.update(date_result.field_errors)
            except (ValueError, AttributeError):
                result.add_error("無効な日付形式です", "due_date")
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_task_completion(cls, completion_data: Dict[str, Any]) -> ValidationResult:
        """タスク完了バリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 気分スコアチェック
        if "mood_score" not in completion_data:
            result.add_error("mood_scoreは必須です", "mood_score")
        else:
            mood_result = cls.validate_numeric_range(
                completion_data["mood_score"], "mood_score", min_value=1, max_value=5
            )
            if not mood_result.is_valid:
                result.errors.extend(mood_result.errors)
                result.field_errors.update(mood_result.field_errors)
        
        # 実際の時間チェック
        if "actual_duration" in completion_data and completion_data["actual_duration"]:
            duration_result = cls.validate_numeric_range(
                completion_data["actual_duration"], "actual_duration", 
                min_value=1, max_value=1440
            )
            if not duration_result.is_valid:
                result.errors.extend(duration_result.errors)
                result.field_errors.update(duration_result.field_errors)
        
        # ノートチェック
        if "notes" in completion_data and completion_data["notes"]:
            notes_result = cls.validate_string_length(
                completion_data["notes"], "notes", max_length=1000
            )
            if not notes_result.is_valid:
                result.errors.extend(notes_result.errors)
                result.field_errors.update(notes_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result


class MoodValidator(BaseValidator):
    """気分バリデーター"""
    
    @classmethod
    def validate_mood_log(cls, mood_data: Dict[str, Any]) -> ValidationResult:
        """気分ログバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 気分スコアチェック
        if "mood_score" not in mood_data:
            result.add_error("mood_scoreは必須です", "mood_score")
        else:
            mood_result = cls.validate_numeric_range(
                mood_data["mood_score"], "mood_score", min_value=1, max_value=5
            )
            if not mood_result.is_valid:
                result.errors.extend(mood_result.errors)
                result.field_errors.update(mood_result.field_errors)
        
        # ノートチェック
        if "notes" in mood_data and mood_data["notes"]:
            notes_result = cls.validate_string_length(
                mood_data["notes"], "notes", max_length=500
            )
            if not notes_result.is_valid:
                result.errors.extend(notes_result.errors)
                result.field_errors.update(notes_result.field_errors)
        
        # コンテキストタグチェック
        if "context_tags" in mood_data:
            if not isinstance(mood_data["context_tags"], list):
                result.add_error("context_tagsはリストである必要があります", "context_tags")
            elif len(mood_data["context_tags"]) > 10:
                result.add_error("context_tagsは10個以下である必要があります", "context_tags")
        
        result.is_valid = len(result.errors) == 0
        return result


class UserValidator(BaseValidator):
    """ユーザーバリデーター"""
    
    @classmethod
    def validate_user_registration(cls, user_data: Dict[str, Any]) -> ValidationResult:
        """ユーザー登録バリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 必須フィールドチェック
        required_fields = ["email", "display_name"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                result.add_error(f"{field}は必須です", field)
        
        # メールアドレスチェック
        if "email" in user_data:
            email_result = cls.validate_email(user_data["email"])
            if not email_result.is_valid:
                result.errors.extend(email_result.errors)
                result.field_errors.update(email_result.field_errors)
        
        # 表示名チェック
        if "display_name" in user_data:
            name_result = cls.validate_string_length(
                user_data["display_name"], "display_name", 
                min_length=1, max_length=50
            )
            if not name_result.is_valid:
                result.errors.extend(name_result.errors)
                result.field_errors.update(name_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result


class APIValidator:
    """API バリデーター"""
    
    @staticmethod
    def validate_pagination_params(
        page: int = 1, 
        page_size: int = 20
    ) -> ValidationResult:
        """ページネーションパラメータバリデーション"""
        result = ValidationResult(is_valid=True)
        
        if page < 1:
            result.add_error("pageは1以上である必要があります", "page")
        
        if page_size < 1 or page_size > 100:
            result.add_error("page_sizeは1以上100以下である必要があります", "page_size")
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @staticmethod
    def validate_date_range_params(
        start_date: str = None, 
        end_date: str = None
    ) -> ValidationResult:
        """日付範囲パラメータバリデーション"""
        result = ValidationResult(is_valid=True)
        
        parsed_start = None
        parsed_end = None
        
        if start_date:
            try:
                parsed_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                result.add_error("start_dateの形式が正しくありません", "start_date")
        
        if end_date:
            try:
                parsed_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                result.add_error("end_dateの形式が正しくありません", "end_date")
        
        if parsed_start and parsed_end and parsed_start > parsed_end:
            result.add_error("start_dateはend_dateより前である必要があります")
        
        result.is_valid = len(result.errors) == 0
        return result