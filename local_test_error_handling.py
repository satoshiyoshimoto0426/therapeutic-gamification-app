"""
ローカルテスト環境のエラーハンドリングシステム

このモジュールは、ローカルテスト環境で発生する様々なエラーを
適切に分類し、ユーザーに分かりやすいメッセージと復旧ヒントを提供します。
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorCategory(Enum):
    """エラーカテゴリの列挙"""
    ENVIRONMENT = "environment"
    DEPENDENCY = "dependency"
    SERVICE = "service"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    PERMISSION = "permission"
    RESOURCE = "resource"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """エラーの重要度"""
    CRITICAL = "critical"  # システムが動作不能
    ERROR = "error"        # 機能が動作しない
    WARNING = "warning"    # 機能は動作するが問題がある
    INFO = "info"          # 情報提供のみ


class LocalTestError(Exception):
    """ローカルテスト環境エラーの基底クラス"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Args:
            message: エラーメッセージ
            category: エラーカテゴリ
            severity: エラーの重要度
            recovery_hint: 復旧方法のヒント
            details: 追加の詳細情報
            cause: 原因となった例外
        """
        self.message = message
        self.category = category
        self.severity = severity
        self.recovery_hint = recovery_hint
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)
    
    def get_formatted_message(self) -> str:
        """フォーマットされたエラーメッセージを取得"""
        lines = []
        
        # 重要度アイコン
        severity_icons = {
            ErrorSeverity.CRITICAL: "🔴",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.INFO: "ℹ️"
        }
        icon = severity_icons.get(self.severity, "❌")
        
        # メインメッセージ
        lines.append(f"{icon} [{self.category.value.upper()}] {self.message}")
        
        # 詳細情報
        if self.details:
            lines.append("\n詳細:")
            for key, value in self.details.items():
                lines.append(f"  • {key}: {value}")
        
        # 復旧ヒント
        if self.recovery_hint:
            lines.append(f"\n💡 解決方法: {self.recovery_hint}")
        
        # 原因
        if self.cause:
            lines.append(f"\n原因: {str(self.cause)}")
        
        return "\n".join(lines)


class EnvironmentError(LocalTestError):
    """環境関連のエラー"""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.ENVIRONMENT,
            severity=ErrorSeverity.CRITICAL,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class DependencyError(LocalTestError):
    """依存関係のエラー"""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.DEPENDENCY,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class ServiceError(LocalTestError):
    """サービス起動・管理のエラー"""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = details or {}
        if service_name:
            details["service"] = service_name
        
        super().__init__(
            message=message,
            category=ErrorCategory.SERVICE,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class DatabaseError(LocalTestError):
    """データベース関連のエラー"""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class ConfigurationError(LocalTestError):
    """設定ファイル関連のエラー"""
    
    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = details or {}
        if config_file:
            details["config_file"] = config_file
        
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class NetworkError(LocalTestError):
    """ネットワーク関連のエラー"""
    
    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.WARNING,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class PermissionError(LocalTestError):
    """権限関連のエラー"""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = details or {}
        if resource:
            details["resource"] = resource
        
        super().__init__(
            message=message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class ResourceError(LocalTestError):
    """リソース不足のエラー"""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = details or {}
        if resource_type:
            details["resource_type"] = resource_type
        
        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.WARNING,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class ValidationError(LocalTestError):
    """バリデーションエラー"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        recovery_hint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR,
            recovery_hint=recovery_hint,
            details=details,
            cause=cause
        )


class ErrorHandler:
    """エラーハンドリングのユーティリティクラス"""
    
    @staticmethod
    def handle_error(error: Exception, context: Optional[str] = None) -> LocalTestError:
        """
        一般的な例外をLocalTestErrorに変換
        
        Args:
            error: 発生した例外
            context: エラーが発生したコンテキスト
            
        Returns:
            LocalTestError: 変換されたエラー
        """
        if isinstance(error, LocalTestError):
            return error
        
        # 既知のエラーパターンに基づいて変換
        error_str = str(error).lower()
        
        # 環境エラー
        if "python" in error_str or "node" in error_str or "npm" in error_str:
            return EnvironmentError(
                message=f"環境エラーが発生しました: {str(error)}",
                recovery_hint="Python/Node.jsが正しくインストールされているか確認してください",
                cause=error
            )
        
        # 依存関係エラー
        if "module" in error_str or "package" in error_str or "import" in error_str:
            return DependencyError(
                message=f"依存関係のエラーが発生しました: {str(error)}",
                recovery_hint="pip install -r requirements.txt または npm install を実行してください",
                cause=error
            )
        
        # ポート関連エラー
        if "port" in error_str or "address already in use" in error_str:
            return ServiceError(
                message=f"ポートが既に使用されています: {str(error)}",
                recovery_hint="他のプロセスを停止するか、別のポートを使用してください",
                cause=error
            )
        
        # 権限エラー
        if "permission" in error_str or "access denied" in error_str:
            return PermissionError(
                message=f"権限エラーが発生しました: {str(error)}",
                recovery_hint="管理者権限で実行するか、ファイル/ディレクトリの権限を確認してください",
                cause=error
            )
        
        # ファイル/ディレクトリエラー
        if "no such file" in error_str or "not found" in error_str:
            return ConfigurationError(
                message=f"ファイルまたはディレクトリが見つかりません: {str(error)}",
                recovery_hint="パスが正しいか、ファイルが存在するか確認してください",
                cause=error
            )
        
        # デフォルト
        return LocalTestError(
            message=f"予期しないエラーが発生しました: {str(error)}",
            recovery_hint="エラーログを確認し、必要に応じてサポートに連絡してください",
            details={"context": context} if context else None,
            cause=error
        )
    
    @staticmethod
    def get_recovery_hints(category: ErrorCategory) -> List[str]:
        """
        エラーカテゴリに基づく一般的な復旧ヒントを取得
        
        Args:
            category: エラーカテゴリ
            
        Returns:
            復旧ヒントのリスト
        """
        hints = {
            ErrorCategory.ENVIRONMENT: [
                "Python 3.9以上がインストールされているか確認",
                "Node.js 16以上がインストールされているか確認",
                "環境変数PATHが正しく設定されているか確認"
            ],
            ErrorCategory.DEPENDENCY: [
                "pip install -r requirements.txt を実行",
                "npm install を実行",
                "仮想環境が有効化されているか確認"
            ],
            ErrorCategory.SERVICE: [
                "ポートが他のプロセスで使用されていないか確認",
                "サービスのログを確認",
                "設定ファイルが正しいか確認"
            ],
            ErrorCategory.DATABASE: [
                "モックデータベースが初期化されているか確認",
                "データファイルが存在するか確認",
                "データ形式が正しいか確認"
            ],
            ErrorCategory.CONFIGURATION: [
                "設定ファイルが存在するか確認",
                "設定ファイルの形式が正しいか確認",
                ".env.localファイルを確認"
            ],
            ErrorCategory.NETWORK: [
                "インターネット接続を確認",
                "ファイアウォール設定を確認",
                "プロキシ設定を確認"
            ],
            ErrorCategory.PERMISSION: [
                "管理者権限で実行",
                "ファイル/ディレクトリの権限を確認",
                "所有者を確認"
            ],
            ErrorCategory.RESOURCE: [
                "ディスク容量を確認",
                "メモリ使用量を確認",
                "不要なプロセスを停止"
            ],
            ErrorCategory.VALIDATION: [
                "入力値を確認",
                "データ形式を確認",
                "必須フィールドが入力されているか確認"
            ]
        }
        
        return hints.get(category, ["エラーログを確認してください"])
    
    @staticmethod
    def print_error(error: LocalTestError) -> None:
        """エラーを整形して出力"""
        print("\n" + "=" * 70)
        print(error.get_formatted_message())
        print("=" * 70 + "\n")


# 便利な関数
def create_environment_error(message: str, **kwargs) -> EnvironmentError:
    """環境エラーを作成"""
    return EnvironmentError(message=message, **kwargs)


def create_dependency_error(message: str, **kwargs) -> DependencyError:
    """依存関係エラーを作成"""
    return DependencyError(message=message, **kwargs)


def create_service_error(message: str, service_name: Optional[str] = None, **kwargs) -> ServiceError:
    """サービスエラーを作成"""
    return ServiceError(message=message, service_name=service_name, **kwargs)


def create_database_error(message: str, **kwargs) -> DatabaseError:
    """データベースエラーを作成"""
    return DatabaseError(message=message, **kwargs)


def create_configuration_error(message: str, config_file: Optional[str] = None, **kwargs) -> ConfigurationError:
    """設定エラーを作成"""
    return ConfigurationError(message=message, config_file=config_file, **kwargs)
