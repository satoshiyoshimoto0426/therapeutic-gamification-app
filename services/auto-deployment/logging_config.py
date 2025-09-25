"""
自動デプロイメントログ設定

構造化ログとリアルタイム監視のためのログ設定を提供します。
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
try:
    from .config import LogLevel, DeploymentConfig
except ImportError:
    from config import LogLevel, DeploymentConfig


class StructuredFormatter(logging.Formatter):
    """構造化ログフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを構造化JSON形式でフォーマット"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 例外情報がある場合は追加
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # カスタム属性を追加
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "module", "lineno", "funcName", "created",
                          "msecs", "relativeCreated", "thread", "threadName",
                          "processName", "process", "getMessage", "exc_info",
                          "exc_text", "stack_info"]:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class DeploymentLoggerAdapter(logging.LoggerAdapter):
    """デプロイメント専用ログアダプター"""
    
    def __init__(self, logger: logging.Logger, deployment_id: str):
        super().__init__(logger, {"deployment_id": deployment_id})
        self.deployment_id = deployment_id
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """ログメッセージを処理してデプロイメントIDを追加"""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
    
    def log_step(self, step: str, status: str, details: Optional[Dict[str, Any]] = None):
        """デプロイメントステップをログ出力"""
        extra = {
            "step": step,
            "status": status,
            "deployment_id": self.deployment_id
        }
        
        if details:
            extra.update(details)
        
        self.info(f"デプロイメントステップ: {step} - {status}", extra=extra)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """エラーをログ出力"""
        extra = {
            "error_type": error.__class__.__name__,
            "deployment_id": self.deployment_id
        }
        
        if context:
            extra.update(context)
        
        self.error(f"デプロイメントエラー: {str(error)}", extra=extra, exc_info=True)
    
    def log_metric(self, metric_name: str, value: float, unit: str = ""):
        """メトリクスをログ出力"""
        extra = {
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "deployment_id": self.deployment_id
        }
        
        self.info(f"メトリクス: {metric_name} = {value} {unit}", extra=extra)


class LogManager:
    """ログ管理クラス"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """ログ設定を初期化"""
        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(self._get_log_level())
        
        # 既存のハンドラーをクリア
        root_logger.handlers.clear()
        
        # コンソールハンドラーの設定
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(console_handler)
        
        # ファイルハンドラーの設定（指定されている場合）
        if self.config.log_file:
            self._setup_file_handler(root_logger)
        
        # 外部ログハンドラーの設定
        self._setup_external_handlers(root_logger)
    
    def _get_log_level(self) -> int:
        """ログレベルを取得"""
        level_mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        return level_mapping.get(self.config.log_level, logging.INFO)
    
    def _setup_file_handler(self, logger: logging.Logger):
        """ファイルハンドラーを設定"""
        log_file = Path(self.config.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ローテーションファイルハンドラー
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    
    def _setup_external_handlers(self, logger: logging.Logger):
        """外部ログハンドラーを設定"""
        # Google Cloud Loggingハンドラー（本番環境）
        if self.config.environment.value == "production":
            try:
                from google.cloud import logging as gcp_logging
                client = gcp_logging.Client()
                gcp_handler = client.get_default_handler()
                gcp_handler.setFormatter(StructuredFormatter())
                logger.addHandler(gcp_handler)
            except ImportError:
                # Google Cloud Loggingライブラリが利用できない場合はスキップ
                pass
    
    def get_logger(self, name: str) -> logging.Logger:
        """名前付きロガーを取得"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(f"auto_deployment.{name}")
        return self._loggers[name]
    
    def get_deployment_logger(self, deployment_id: str) -> DeploymentLoggerAdapter:
        """デプロイメント専用ロガーを取得"""
        base_logger = self.get_logger("deployment")
        return DeploymentLoggerAdapter(base_logger, deployment_id)
    
    def log_deployment_start(self, deployment_id: str, config: Dict[str, Any]):
        """デプロイメント開始をログ出力"""
        logger = self.get_deployment_logger(deployment_id)
        logger.log_step(
            "deployment_start",
            "started",
            {
                "environment": config.get("environment"),
                "strategy": config.get("strategy"),
                "service_name": config.get("service_name")
            }
        )
    
    def log_deployment_complete(self, deployment_id: str, duration_seconds: float, success: bool):
        """デプロイメント完了をログ出力"""
        logger = self.get_deployment_logger(deployment_id)
        status = "success" if success else "failed"
        logger.log_step(
            "deployment_complete",
            status,
            {"duration_seconds": duration_seconds}
        )
        logger.log_metric("deployment_duration", duration_seconds, "seconds")
    
    def create_audit_log(self, action: str, user: str, details: Dict[str, Any]):
        """監査ログを作成"""
        audit_logger = self.get_logger("audit")
        audit_logger.info(
            f"監査ログ: {action}",
            extra={
                "audit_action": action,
                "user": user,
                "timestamp": datetime.utcnow().isoformat(),
                **details
            }
        )


# グローバルログマネージャー（設定後に初期化）
_log_manager: Optional[LogManager] = None


def initialize_logging(config: DeploymentConfig) -> LogManager:
    """ログシステムを初期化"""
    global _log_manager
    _log_manager = LogManager(config)
    return _log_manager


def get_logger(name: str) -> logging.Logger:
    """ロガーを取得（初期化済みの場合）"""
    if _log_manager is None:
        # フォールバック: 基本的なロガーを返す
        return logging.getLogger(f"auto_deployment.{name}")
    return _log_manager.get_logger(name)


def get_deployment_logger(deployment_id: str) -> DeploymentLoggerAdapter:
    """デプロイメントロガーを取得"""
    if _log_manager is None:
        # フォールバック: 基本的なアダプターを返す
        base_logger = logging.getLogger("auto_deployment.deployment")
        return DeploymentLoggerAdapter(base_logger, deployment_id)
    return _log_manager.get_deployment_logger(deployment_id)