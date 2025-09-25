"""
デプロイメントオーケストレータ

自動デプロイメントの中央制御システム。
全てのデプロイメント処理を統括し、各コンポーネントを協調させます。
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from .config import DeploymentConfig, Environment, DeploymentStrategy, default_config_manager
    from .exceptions import (
        DeploymentError, PreDeploymentError, DeploymentExecutionError,
        ErrorSeverity, ErrorCategory, ErrorAction, ErrorResponse
    )
    from .logging_config import initialize_logging, get_deployment_logger, DeploymentLoggerAdapter
except ImportError:
    # テスト環境での絶対インポート
    from config import DeploymentConfig, Environment, DeploymentStrategy, default_config_manager
    from exceptions import (
        DeploymentError, PreDeploymentError, DeploymentExecutionError,
        ErrorSeverity, ErrorCategory, ErrorAction, ErrorResponse
    )
    try:
        from logging_config import initialize_logging, get_deployment_logger, DeploymentLoggerAdapter
    except ImportError:
        # ログ設定が利用できない場合のフォールバック
        initialize_logging = None
        get_deployment_logger = None
        DeploymentLoggerAdapter = None


class DeploymentStatus(Enum):
    """デプロイメントステータス"""
    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class DeploymentPhase(Enum):
    """デプロイメントフェーズ"""
    PRE_VALIDATION = "pre_validation"
    ENVIRONMENT_SETUP = "environment_setup"
    BUILD_AND_DEPLOY = "build_and_deploy"
    HEALTH_CHECK = "health_check"
    TRAFFIC_MIGRATION = "traffic_migration"
    POST_DEPLOYMENT = "post_deployment"
    CLEANUP = "cleanup"


@dataclass
class DeploymentStep:
    """デプロイメントステップ"""
    name: str
    phase: DeploymentPhase
    function: Callable
    required: bool = True
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DeploymentResult:
    """デプロイメント結果"""
    deployment_id: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    environment: Environment = None
    service_url: Optional[str] = None
    revision_name: Optional[str] = None
    error: Optional[DeploymentError] = None
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """デプロイメント時間を秒で返す"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_success(self) -> bool:
        """デプロイメントが成功したかどうか"""
        return self.status == DeploymentStatus.COMPLETED
    
    def to_dict(self) -> Dict[str, Any]:
        """結果を辞書形式で返す"""
        return {
            "deployment_id": self.deployment_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "environment": self.environment.value if self.environment else None,
            "service_url": self.service_url,
            "revision_name": self.revision_name,
            "duration_seconds": self.duration_seconds,
            "error": self.error.to_dict() if self.error else None,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "metrics": self.metrics
        }


class DeploymentOrchestrator:
    """デプロイメントオーケストレータ"""
    
    def __init__(self, config: Optional[DeploymentConfig] = None):
        self.config = config
        self.logger: Optional[DeploymentLoggerAdapter] = None
        self.deployment_steps: List[DeploymentStep] = []
        self.current_deployment: Optional[DeploymentResult] = None
        self._step_registry: Dict[str, DeploymentStep] = {}
        
        # コンポーネントの初期化（後で実装）
        self.validator = None
        self.environment_manager = None
        self.deployment_engine = None
        self.health_monitor = None
        self.notification_system = None
        self.rollback_manager = None
        
        self._initialize_default_steps()
    
    def _initialize_default_steps(self):
        """デフォルトのデプロイメントステップを初期化"""
        default_steps = [
            DeploymentStep(
                name="validate_prerequisites",
                phase=DeploymentPhase.PRE_VALIDATION,
                function=self._validate_prerequisites,
                timeout_seconds=120
            ),
            DeploymentStep(
                name="setup_environment",
                phase=DeploymentPhase.ENVIRONMENT_SETUP,
                function=self._setup_environment,
                dependencies=["validate_prerequisites"],
                timeout_seconds=300
            ),
            DeploymentStep(
                name="build_and_deploy",
                phase=DeploymentPhase.BUILD_AND_DEPLOY,
                function=self._build_and_deploy,
                dependencies=["setup_environment"],
                timeout_seconds=900
            ),
            DeploymentStep(
                name="health_check",
                phase=DeploymentPhase.HEALTH_CHECK,
                function=self._perform_health_check,
                dependencies=["build_and_deploy"],
                timeout_seconds=180
            ),
            DeploymentStep(
                name="migrate_traffic",
                phase=DeploymentPhase.TRAFFIC_MIGRATION,
                function=self._migrate_traffic,
                dependencies=["health_check"],
                timeout_seconds=600
            ),
            DeploymentStep(
                name="post_deployment_monitoring",
                phase=DeploymentPhase.POST_DEPLOYMENT,
                function=self._post_deployment_monitoring,
                dependencies=["migrate_traffic"],
                timeout_seconds=300
            ),
            DeploymentStep(
                name="cleanup",
                phase=DeploymentPhase.CLEANUP,
                function=self._cleanup,
                dependencies=["post_deployment_monitoring"],
                required=False,
                timeout_seconds=120
            )
        ]
        
        for step in default_steps:
            self.register_step(step)
    
    def register_step(self, step: DeploymentStep):
        """デプロイメントステップを登録"""
        self._step_registry[step.name] = step
        if step not in self.deployment_steps:
            self.deployment_steps.append(step)
    
    async def deploy(
        self,
        environment: Environment,
        options: Optional[Dict[str, Any]] = None
    ) -> DeploymentResult:
        """メインデプロイメント処理"""
        deployment_id = str(uuid.uuid4())
        
        # 設定の取得と初期化
        if self.config is None:
            self.config = default_config_manager.get_config(environment)
        
        # ログシステムの初期化
        log_manager = initialize_logging(self.config)
        self.logger = log_manager.get_deployment_logger(deployment_id)
        
        # デプロイメント結果の初期化
        self.current_deployment = DeploymentResult(
            deployment_id=deployment_id,
            status=DeploymentStatus.PENDING,
            start_time=datetime.utcnow(),
            environment=environment
        )
        
        self.logger.log_step("deployment_init", "started", {
            "deployment_id": deployment_id,
            "environment": environment.value,
            "options": options or {}
        })
        
        try:
            # デプロイメント実行
            await self._execute_deployment_pipeline()
            
            # 成功時の処理
            self.current_deployment.status = DeploymentStatus.COMPLETED
            self.current_deployment.end_time = datetime.utcnow()
            
            self.logger.log_step("deployment_complete", "success", {
                "duration_seconds": self.current_deployment.duration_seconds
            })
            
            return self.current_deployment
            
        except DeploymentError as e:
            # デプロイメントエラーの処理
            await self._handle_deployment_error(e)
            return self.current_deployment
            
        except Exception as e:
            # 予期しないエラーの処理
            deployment_error = DeploymentExecutionError(
                f"予期しないエラーが発生しました: {str(e)}",
                severity=ErrorSeverity.CRITICAL
            )
            await self._handle_deployment_error(deployment_error)
            return self.current_deployment
    
    async def _execute_deployment_pipeline(self):
        """デプロイメントパイプラインを実行"""
        self.current_deployment.status = DeploymentStatus.VALIDATING
        
        # 依存関係の解決
        ordered_steps = self._resolve_dependencies()
        
        for step in ordered_steps:
            await self._execute_step(step)
    
    def _resolve_dependencies(self) -> List[DeploymentStep]:
        """ステップの依存関係を解決して実行順序を決定"""
        # 簡単なトポロジカルソート実装
        resolved = []
        remaining = self.deployment_steps.copy()
        
        while remaining:
            # 依存関係が満たされているステップを探す
            ready_steps = [
                step for step in remaining
                if all(dep in [s.name for s in resolved] for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # 循環依存関係がある場合
                raise PreDeploymentError(
                    "ステップの循環依存関係が検出されました",
                    severity=ErrorSeverity.CRITICAL
                )
            
            # 最初の準備完了ステップを追加
            step = ready_steps[0]
            resolved.append(step)
            remaining.remove(step)
        
        return resolved
    
    async def _execute_step(self, step: DeploymentStep):
        """個別ステップを実行"""
        self.logger.log_step(step.name, "started")
        
        try:
            # タイムアウト付きでステップを実行
            await asyncio.wait_for(
                step.function(),
                timeout=step.timeout_seconds
            )
            
            self.current_deployment.steps_completed.append(step.name)
            self.logger.log_step(step.name, "completed")
            
        except asyncio.TimeoutError:
            error_msg = f"ステップ '{step.name}' がタイムアウトしました ({step.timeout_seconds}秒)"
            self._handle_step_failure(step, error_msg)
            
        except Exception as e:
            error_msg = f"ステップ '{step.name}' でエラーが発生しました: {str(e)}"
            self._handle_step_failure(step, error_msg)
    
    def _handle_step_failure(self, step: DeploymentStep, error_msg: str):
        """ステップ失敗時の処理"""
        self.current_deployment.steps_failed.append(step.name)
        self.logger.log_step(step.name, "failed", {"error": error_msg})
        
        if step.required:
            raise DeploymentExecutionError(
                error_msg,
                severity=ErrorSeverity.HIGH,
                context={"step_name": step.name}
            )
        else:
            # 必須でないステップの場合は警告として続行
            self.logger.log_step(step.name, "skipped", {"reason": "non_required_step_failed"})
    
    async def _handle_deployment_error(self, error: DeploymentError):
        """デプロイメントエラーの処理"""
        self.current_deployment.status = DeploymentStatus.FAILED
        self.current_deployment.end_time = datetime.utcnow()
        self.current_deployment.error = error
        
        self.logger.log_error(error, {
            "deployment_id": self.current_deployment.deployment_id,
            "failed_steps": self.current_deployment.steps_failed
        })
        
        # 自動ロールバックの判定
        if (self.config.rollback_on_failure and 
            error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]):
            await self._initiate_rollback()
    
    async def _initiate_rollback(self):
        """ロールバックを開始"""
        self.current_deployment.status = DeploymentStatus.ROLLING_BACK
        self.logger.log_step("rollback", "started")
        
        try:
            # ロールバック処理（後で実装）
            if self.rollback_manager:
                await self.rollback_manager.execute_rollback()
            
            self.current_deployment.status = DeploymentStatus.ROLLED_BACK
            self.logger.log_step("rollback", "completed")
            
        except Exception as e:
            self.logger.log_error(e, {"context": "rollback_failed"})
            # ロールバック失敗は最も深刻な状況
    
    # デフォルトステップの実装（プレースホルダー）
    async def _validate_prerequisites(self):
        """前提条件の検証"""
        self.logger.info("前提条件を検証中...")
        # TODO: 実際の検証ロジックを実装
        await asyncio.sleep(1)  # 模擬処理時間
    
    async def _setup_environment(self):
        """環境セットアップ"""
        self.logger.info("環境をセットアップ中...")
        # TODO: 実際の環境セットアップロジックを実装
        await asyncio.sleep(2)  # 模擬処理時間
    
    async def _build_and_deploy(self):
        """ビルドとデプロイ"""
        self.logger.info("ビルドとデプロイを実行中...")
        self.current_deployment.status = DeploymentStatus.DEPLOYING
        # TODO: 実際のビルド・デプロイロジックを実装
        await asyncio.sleep(5)  # 模擬処理時間
    
    async def _perform_health_check(self):
        """ヘルスチェック実行"""
        self.logger.info("ヘルスチェックを実行中...")
        self.current_deployment.status = DeploymentStatus.TESTING
        # TODO: 実際のヘルスチェックロジックを実装
        await asyncio.sleep(2)  # 模擬処理時間
    
    async def _migrate_traffic(self):
        """トラフィック移行"""
        self.logger.info("トラフィックを移行中...")
        # TODO: 実際のトラフィック移行ロジックを実装
        await asyncio.sleep(3)  # 模擬処理時間
    
    async def _post_deployment_monitoring(self):
        """デプロイ後監視"""
        self.logger.info("デプロイ後監視を開始...")
        # TODO: 実際の監視ロジックを実装
        await asyncio.sleep(2)  # 模擬処理時間
    
    async def _cleanup(self):
        """クリーンアップ"""
        self.logger.info("クリーンアップを実行中...")
        # TODO: 実際のクリーンアップロジックを実装
        await asyncio.sleep(1)  # 模擬処理時間
    
    def get_deployment_status(self) -> Optional[Dict[str, Any]]:
        """現在のデプロイメント状況を取得"""
        if self.current_deployment:
            return self.current_deployment.to_dict()
        return None
    
    async def cancel_deployment(self) -> bool:
        """デプロイメントをキャンセル"""
        if self.current_deployment and self.current_deployment.status in [
            DeploymentStatus.PENDING, DeploymentStatus.VALIDATING, DeploymentStatus.DEPLOYING
        ]:
            self.logger.log_step("deployment_cancel", "requested")
            # TODO: キャンセル処理の実装
            return True
        return False