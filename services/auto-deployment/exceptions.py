"""
自動デプロイメント例外クラス

デプロイメント処理で発生する各種例外を定義します。
"""

from enum import Enum
from typing import List, Optional, Dict, Any


class ErrorSeverity(Enum):
    """エラーの重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """エラーカテゴリ"""
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post_deployment"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    CONFIGURATION = "configuration"


class ErrorAction(Enum):
    """エラー発生時のアクション"""
    RETRY = "retry"
    ROLLBACK_INITIATED = "rollback_initiated"
    MANUAL_INTERVENTION = "manual_intervention"
    ABORT_DEPLOYMENT = "abort_deployment"
    CONTINUE_WITH_WARNING = "continue_with_warning"


class DeploymentError(Exception):
    """デプロイメント基底例外クラス"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_steps: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.recovery_steps = recovery_steps or []
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で返す"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recovery_steps": self.recovery_steps,
            "context": self.context
        }


class PreDeploymentError(DeploymentError):
    """デプロイ前チェックエラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PRE_DEPLOYMENT,
            **kwargs
        )


class ConfigurationError(DeploymentError):
    """設定エラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class SecurityError(DeploymentError):
    """セキュリティエラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class InfrastructureError(DeploymentError):
    """インフラストラクチャエラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.INFRASTRUCTURE,
            **kwargs
        )


class DeploymentExecutionError(DeploymentError):
    """デプロイメント実行エラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DEPLOYMENT,
            **kwargs
        )


class HealthCheckError(DeploymentError):
    """ヘルスチェックエラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.POST_DEPLOYMENT,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class RollbackError(DeploymentError):
    """ロールバックエラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.POST_DEPLOYMENT,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class ValidationError(PreDeploymentError):
    """バリデーションエラー"""
    
    def __init__(self, message: str, validation_failures: List[str], **kwargs):
        super().__init__(message, **kwargs)
        self.validation_failures = validation_failures
        self.context["validation_failures"] = validation_failures


class AuthenticationError(InfrastructureError):
    """認証エラー"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            recovery_steps=[
                "認証情報を確認してください",
                "gcloud auth login を実行してください",
                "サービスアカウントキーを確認してください"
            ],
            **kwargs
        )


class APIError(InfrastructureError):
    """API関連エラー"""
    
    def __init__(self, message: str, api_name: str, **kwargs):
        super().__init__(
            message,
            recovery_steps=[
                f"{api_name} APIが有効化されているか確認してください",
                "必要な権限が付与されているか確認してください",
                "APIクォータを確認してください"
            ],
            **kwargs
        )
        self.api_name = api_name
        self.context["api_name"] = api_name


class TimeoutError(DeploymentError):
    """タイムアウトエラー"""
    
    def __init__(self, message: str, timeout_seconds: int, **kwargs):
        super().__init__(
            message,
            recovery_steps=[
                "タイムアウト値を増やして再試行してください",
                "ネットワーク接続を確認してください",
                "リソースの可用性を確認してください"
            ],
            **kwargs
        )
        self.timeout_seconds = timeout_seconds
        self.context["timeout_seconds"] = timeout_seconds


class ResourceNotFoundError(InfrastructureError):
    """リソース未発見エラー"""
    
    def __init__(self, message: str, resource_type: str, resource_name: str, **kwargs):
        super().__init__(
            message,
            recovery_steps=[
                f"{resource_type}が存在するか確認してください",
                "リソース名のスペルを確認してください",
                "適切なプロジェクトが選択されているか確認してください"
            ],
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.context.update({
            "resource_type": resource_type,
            "resource_name": resource_name
        })


class CloudResourceError(InfrastructureError):
    """Cloud resource management error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            recovery_steps=[
                "Check Google Cloud project configuration",
                "Verify API enablement and permissions",
                "Check resource quotas and limits",
                "Verify network connectivity"
            ],
            **kwargs
        )


class EnvironmentError(DeploymentError):
    """Environment detection and setup error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            recovery_steps=[
                "Check environment configuration",
                "Verify environment variables are set correctly",
                "Review environment detection settings",
                "Check project and region settings"
            ],
            **kwargs
        )


class NetworkError(InfrastructureError):
    """Network-related error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            recovery_steps=[
                "Check network connectivity",
                "Verify DNS resolution",
                "Check firewall rules",
                "Retry the operation"
            ],
            **kwargs
        )


class ErrorResponse:
    """エラーレスポンス"""
    
    def __init__(
        self,
        action: ErrorAction,
        message: str,
        recovery_steps: List[str],
        retry_after_seconds: Optional[int] = None
    ):
        self.action = action
        self.message = message
        self.recovery_steps = recovery_steps
        self.retry_after_seconds = retry_after_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """レスポンス情報を辞書形式で返す"""
        result = {
            "action": self.action.value,
            "message": self.message,
            "recovery_steps": self.recovery_steps
        }
        
        if self.retry_after_seconds is not None:
            result["retry_after_seconds"] = self.retry_after_seconds
        
        return result
