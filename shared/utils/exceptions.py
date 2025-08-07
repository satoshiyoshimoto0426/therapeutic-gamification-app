"""
Custom exceptions for the therapeutic gamification app
Standardized error handling across all microservices
"""

from typing import Optional, Dict, Any

class TherapeuticGameError(Exception):
    """Base exception for therapeutic gamification app"""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(TherapeuticGameError):
    """Validation error for input data"""
    
    def __init__(self, message: str, field: Optional[str] = None, invalid_value: Any = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.invalid_value = invalid_value

class BusinessLogicError(TherapeuticGameError):
    """Business logic error"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
        self.operation = operation


class DatabaseError(TherapeuticGameError):
    """Database operation error"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


class NotFoundError(TherapeuticGameError):
    """Generic not found error"""

    def __init__(self, entity: str, entity_id: Optional[str] = None):
        details = {"entity": entity}
        if entity_id is not None:
            details["id"] = entity_id
            message = f"{entity} not found: {entity_id}"
        else:
            message = f"{entity} not found"
        super().__init__(message, "NOT_FOUND", details=details)

class AuthenticationError(TherapeuticGameError):
    """Authentication related errors"""
    
    def __init__(self, message: str = "?"):
        super().__init__(message, "AUTH_ERROR")

class AuthorizationError(TherapeuticGameError):
    """Authorization related errors"""
    
    def __init__(self, message: str = "こ"):
        super().__init__(message, "AUTHORIZATION_ERROR")

class UserNotFoundError(TherapeuticGameError):
    """User not found error"""
    
    def __init__(self, user_id: str):
        message = f"ユーザー: {user_id}"
        super().__init__(message, "USER_NOT_FOUND")
        self.user_id = user_id

class TaskNotFoundError(TherapeuticGameError):
    """Task not found error"""
    
    def __init__(self, task_id: str):
        message = f"タスク: {task_id}"
        super().__init__(message, "TASK_NOT_FOUND")
        self.task_id = task_id

class DailyTaskLimitExceededError(TherapeuticGameError):
    """Daily task limit exceeded error (ADHD consideration)"""
    
    def __init__(self, current_count: int, limit: int = 16):
        message = f"1?: {current_count}/{limit}"
        super().__init__(message, "DAILY_TASK_LIMIT_EXCEEDED")
        self.current_count = current_count
        self.limit = limit

class XPCalculationError(TherapeuticGameError):
    """XP calculation error"""
    
    def __init__(self, message: str = "XP計算"):
        super().__init__(message, "XP_CALCULATION_ERROR")

class StoryGenerationError(TherapeuticGameError):
    """AI story generation error"""
    
    def __init__(self, message: str = "ストーリー"):
        super().__init__(message, "STORY_GENERATION_ERROR")

class TherapeuticSafetyError(TherapeuticGameError):
    """Therapeutic safety violation error"""
    
    def __init__(self, message: str = "治療", confidence: float = 0.0):
        super().__init__(message, "THERAPEUTIC_SAFETY_ERROR")
        self.confidence = confidence

class MandalaGridError(TherapeuticGameError):
    """Mandala grid operation error"""
    
    def __init__(self, message: str, x: Optional[int] = None, y: Optional[int] = None):
        super().__init__(message, "MANDALA_GRID_ERROR")
        self.coordinates = (x, y) if x is not None and y is not None else None

class InsufficientCoinsError(TherapeuticGameError):
    """Insufficient coins for purchase error"""
    
    def __init__(self, required: int, available: int):
        message = f"コア: {required}, ?: {available}"
        super().__init__(message, "INSUFFICIENT_COINS")
        self.required = required
        self.available = available

class ItemNotFoundError(TherapeuticGameError):
    """Item not found error"""
    
    def __init__(self, item_id: str):
        message = f"アプリ: {item_id}"
        super().__init__(message, "ITEM_NOT_FOUND")
        self.item_id = item_id

class InvalidEquipmentSlotError(TherapeuticGameError):
    """Invalid equipment slot error"""
    
    def __init__(self, slot: str):
        message = f"無: {slot}"
        super().__init__(message, "INVALID_EQUIPMENT_SLOT")
        self.slot = slot

class JobClassNotUnlockedError(TherapeuticGameError):
    """Job class not unlocked error"""
    
    def __init__(self, job_class: str):
        message = f"?: {job_class}"
        super().__init__(message, "JOB_CLASS_NOT_UNLOCKED")
        self.job_class = job_class

class BattleNotActiveError(TherapeuticGameError):
    """Battle not active error"""
    
    def __init__(self, message: str = "アプリ"):
        super().__init__(message, "BATTLE_NOT_ACTIVE")

class ReflectionAlreadyCompletedError(TherapeuticGameError):
    """Reflection already completed today error"""
    
    def __init__(self, message: str = "?"):
        super().__init__(message, "REFLECTION_ALREADY_COMPLETED")

class DatabaseConnectionError(TherapeuticGameError):
    """Database connection error"""
    
    def __init__(self, message: str = "デフォルト"):
        super().__init__(message, "DATABASE_CONNECTION_ERROR")

class ExternalAPIError(TherapeuticGameError):
    """External API error"""
    
    def __init__(self, service: str, message: str = "?APIで"):
        super().__init__(f"{service}: {message}", "EXTERNAL_API_ERROR")
        self.service = service

class RateLimitExceededError(TherapeuticGameError):
    """Rate limit exceeded error"""
    
    def __init__(self, limit: int, window: str = "?"):
        message = f"レベル: {limit}?/{window}"
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.limit = limit
        self.window = window

class ConfigurationError(TherapeuticGameError):
    """Configuration error"""
    
    def __init__(self, setting: str, message: str = "設定"):
        super().__init__(f"{setting}: {message}", "CONFIGURATION_ERROR")
        self.setting = setting

# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    BusinessLogicError: 400,
    AuthenticationError: 401,
    AuthorizationError: 403,
    UserNotFoundError: 404,
    TaskNotFoundError: 404,
    ItemNotFoundError: 404,
    NotFoundError: 404,
    DailyTaskLimitExceededError: 429,
    RateLimitExceededError: 429,
    DatabaseConnectionError: 503,
    DatabaseError: 500,
    ExternalAPIError: 502,
    TherapeuticGameError: 500,  # Default for base exception
}

def get_http_status_code(exception: Exception) -> int:
    """Get appropriate HTTP status code for exception"""
    return EXCEPTION_STATUS_MAP.get(type(exception), 500)