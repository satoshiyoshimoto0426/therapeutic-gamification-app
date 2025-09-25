"""
自動デプロイメント設定管理

デプロイメントに必要な設定とコンフィギュレーションを管理します。
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path


class Environment(Enum):
    """デプロイメント環境"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStrategy(Enum):
    """デプロイメント戦略"""
    BLUE_GREEN = "blue_green"
    ROLLING_UPDATE = "rolling_update"
    CANARY = "canary"


class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class CloudConfig:
    """Google Cloud設定"""
    project_id: str
    region: str = "asia-northeast1"
    service_name: str = "therapeutic-gamification-app"
    
    # Cloud Run設定
    memory: str = "2Gi"
    cpu: str = "2"
    min_instances: int = 1
    max_instances: int = 100
    timeout: int = 300
    concurrency: int = 100
    
    # 必要なAPI
    required_apis: List[str] = field(default_factory=lambda: [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "containerregistry.googleapis.com",
        "artifactregistry.googleapis.com",
        "firestore.googleapis.com",
        "iam.googleapis.com",
        "secretmanager.googleapis.com",
        "logging.googleapis.com",
        "monitoring.googleapis.com"
    ])


@dataclass
class HealthCheckConfig:
    """ヘルスチェック設定"""
    endpoints: List[str] = field(default_factory=lambda: ["/health", "/api/health"])
    timeout_seconds: int = 30
    retry_attempts: int = 3
    success_threshold: float = 0.95
    performance_threshold_ms: int = 2000
    check_interval_seconds: int = 10


@dataclass
class NotificationConfig:
    """通知設定"""
    slack_webhook_url: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    enable_github_status: bool = True
    enable_dashboard_updates: bool = True


@dataclass
class SecurityConfig:
    """セキュリティ設定"""
    enable_security_scan: bool = True
    enable_vulnerability_check: bool = True
    enable_dependency_check: bool = True
    min_test_coverage: float = 0.8
    security_scan_timeout: int = 300


@dataclass
class DeploymentConfig:
    """デプロイメント設定"""
    environment: Environment
    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    cloud_config: CloudConfig = None
    health_check_config: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    notification_config: NotificationConfig = field(default_factory=NotificationConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    
    # デプロイメント固有設定
    traffic_split_percentage: int = 10
    rollback_on_failure: bool = True
    auto_cleanup_old_revisions: bool = True
    max_revisions_to_keep: int = 3
    
    # ログ設定
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.cloud_config is None:
            # 環境変数から設定を読み込み
            project_id = os.getenv("GCP_PROJECT_ID", "therapeutic-gamification-app-prod")
            self.cloud_config = CloudConfig(project_id=project_id)
        
        # 環境別設定の調整
        if self.environment == Environment.PRODUCTION:
            self.cloud_config.min_instances = 5
            self.cloud_config.max_instances = 1000
            self.security_config.min_test_coverage = 0.9
        elif self.environment == Environment.STAGING:
            self.cloud_config.min_instances = 1
            self.cloud_config.max_instances = 10
        else:  # DEVELOPMENT
            self.cloud_config.min_instances = 0
            self.cloud_config.max_instances = 5
            self.security_config.enable_security_scan = False


class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config_cache: Dict[str, DeploymentConfig] = {}
    
    def get_config(self, environment: Environment) -> DeploymentConfig:
        """環境別設定を取得"""
        env_name = environment.value
        
        if env_name not in self._config_cache:
            self._config_cache[env_name] = self._load_config(environment)
        
        return self._config_cache[env_name]
    
    def _load_config(self, environment: Environment) -> DeploymentConfig:
        """設定を読み込み"""
        # 基本設定を作成
        config = DeploymentConfig(environment=environment)
        
        # 設定ファイルが存在する場合は読み込み
        if self.config_file and Path(self.config_file).exists():
            # TODO: YAML/JSON設定ファイルの読み込み実装
            pass
        
        # 環境変数からの設定上書き
        self._apply_env_overrides(config)
        
        return config
    
    def _apply_env_overrides(self, config: DeploymentConfig):
        """環境変数による設定上書き"""
        # Cloud設定
        if os.getenv("GCP_PROJECT_ID"):
            config.cloud_config.project_id = os.getenv("GCP_PROJECT_ID")
        
        if os.getenv("GCP_REGION"):
            config.cloud_config.region = os.getenv("GCP_REGION")
        
        if os.getenv("SERVICE_NAME"):
            config.cloud_config.service_name = os.getenv("SERVICE_NAME")
        
        # 通知設定
        if os.getenv("SLACK_WEBHOOK_URL"):
            config.notification_config.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # セキュリティ設定
        if os.getenv("MIN_TEST_COVERAGE"):
            try:
                config.security_config.min_test_coverage = float(os.getenv("MIN_TEST_COVERAGE"))
            except ValueError:
                pass
        
        # ログレベル
        if os.getenv("LOG_LEVEL"):
            try:
                config.log_level = LogLevel(os.getenv("LOG_LEVEL"))
            except ValueError:
                pass
    
    def validate_config(self, config: DeploymentConfig) -> List[str]:
        """設定の妥当性チェック"""
        errors = []
        
        # 必須設定のチェック
        if not config.cloud_config.project_id:
            errors.append("GCP_PROJECT_IDが設定されていません")
        
        if not config.cloud_config.service_name:
            errors.append("サービス名が設定されていません")
        
        # 数値範囲のチェック
        if config.security_config.min_test_coverage < 0 or config.security_config.min_test_coverage > 1:
            errors.append("テストカバレッジの最小値は0.0-1.0の範囲で設定してください")
        
        if config.cloud_config.min_instances < 0:
            errors.append("最小インスタンス数は0以上で設定してください")
        
        if config.cloud_config.max_instances <= config.cloud_config.min_instances:
            errors.append("最大インスタンス数は最小インスタンス数より大きく設定してください")
        
        return errors


# デフォルト設定インスタンス
default_config_manager = ConfigManager()