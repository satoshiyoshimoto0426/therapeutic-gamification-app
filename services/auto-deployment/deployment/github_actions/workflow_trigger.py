"""
GitHub Actions ワークフロートリガーシステム

ワークフローの実行をトリガーし、パラメータを渡す機能を提供します。
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .github_client import GitHubClient, WorkflowRun
from .parameter_manager import ParameterManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

try:
    from services.auto_deployment.config import DeploymentConfig, Environment
    from services.auto_deployment.exceptions import DeploymentError, GitHubAPIError
    from services.auto_deployment.logging_config import get_logger
except ImportError:
    # フォールバック用のクラス
    from enum import Enum
    from dataclasses import dataclass
    
    class Environment(Enum):
        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
    
    @dataclass
    class DeploymentConfig:
        environment: Environment
    
    class DeploymentError(Exception):
        pass
    
    class GitHubAPIError(Exception):
        pass
    
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class TriggerType(Enum):
    """トリガータイプ"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"


@dataclass
class TriggerRequest:
    """トリガーリクエスト"""
    workflow_id: str
    ref: str = "main"
    environment: Environment = Environment.PRODUCTION
    trigger_type: TriggerType = TriggerType.MANUAL
    inputs: Optional[Dict[str, Any]] = None
    wait_for_completion: bool = False
    timeout_minutes: int = 30


@dataclass
class TriggerResult:
    """トリガー結果"""
    run_id: int
    workflow_name: str
    status: str
    html_url: str
    triggered_at: str
    completed_at: Optional[str] = None
    conclusion: Optional[str] = None
    error_message: Optional[str] = None


class WorkflowTrigger:
    """ワークフロートリガー"""
    
    def __init__(self, config: DeploymentConfig, github_client: Optional[GitHubClient] = None):
        """
        初期化
        
        Args:
            config: デプロイメント設定
            github_client: GitHubクライアント（省略時は自動作成）
        """
        self.config = config
        self.github_client = github_client or GitHubClient()
        self.parameter_manager = ParameterManager(config)
        
        # ワークフロー設定
        self.workflow_configs = {
            "ci-cd-pipeline.yml": {
                "name": "CI/CD Pipeline",
                "description": "メインのCI/CDパイプライン",
                "supports_manual_trigger": True,
                "required_inputs": [],
                "optional_inputs": ["environment", "skip_tests", "force_deploy"]
            },
            "deploy-only.yml": {
                "name": "Deploy Only",
                "description": "デプロイのみ実行",
                "supports_manual_trigger": True,
                "required_inputs": ["environment"],
                "optional_inputs": ["image_tag", "skip_health_check"]
            },
            "rollback.yml": {
                "name": "Rollback",
                "description": "ロールバック実行",
                "supports_manual_trigger": True,
                "required_inputs": ["environment", "target_revision"],
                "optional_inputs": ["reason"]
            }
        }
        
        logger.info("WorkflowTrigger initialized")
    
    def trigger_deployment(self, request: TriggerRequest) -> TriggerResult:
        """
        デプロイメントワークフローをトリガー
        
        Args:
            request: トリガーリクエスト
            
        Returns:
            トリガー結果
        """
        logger.info(f"Triggering deployment workflow: {request.workflow_id}")
        
        try:
            # パラメータの準備
            workflow_inputs = self._prepare_workflow_inputs(request)
            
            # ワークフローの検証
            self._validate_workflow_request(request, workflow_inputs)
            
            # ワークフローをトリガー
            run_id = self.github_client.trigger_workflow(
                workflow_id=request.workflow_id,
                ref=request.ref,
                inputs=workflow_inputs
            )
            
            # 実行情報を取得
            workflow_run = self.github_client.get_workflow_run(run_id)
            
            result = TriggerResult(
                run_id=run_id,
                workflow_name=workflow_run.name,
                status=workflow_run.status,
                html_url=workflow_run.html_url,
                triggered_at=workflow_run.created_at.isoformat()
            )
            
            # 完了まで待機する場合
            if request.wait_for_completion:
                result = self._wait_for_completion(result, request.timeout_minutes)
            
            logger.info(f"Workflow triggered successfully. Run ID: {run_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to trigger workflow: {e}")
            raise DeploymentError(f"ワークフローのトリガーに失敗しました: {e}")
    
    def trigger_ci_cd_pipeline(self, environment: Environment, 
                              ref: str = "main", 
                              skip_tests: bool = False,
                              force_deploy: bool = False) -> TriggerResult:
        """
        CI/CDパイプラインをトリガー
        
        Args:
            environment: デプロイメント環境
            ref: ブランチ、タグ、またはSHA
            skip_tests: テストスキップフラグ
            force_deploy: 強制デプロイフラグ
            
        Returns:
            トリガー結果
        """
        request = TriggerRequest(
            workflow_id="ci-cd-pipeline.yml",
            ref=ref,
            environment=environment,
            trigger_type=TriggerType.AUTOMATIC,
            inputs={
                "environment": environment.value,
                "skip_tests": str(skip_tests).lower(),
                "force_deploy": str(force_deploy).lower()
            }
        )
        
        return self.trigger_deployment(request)
    
    def trigger_deploy_only(self, environment: Environment,
                           image_tag: Optional[str] = None,
                           skip_health_check: bool = False) -> TriggerResult:
        """
        デプロイのみワークフローをトリガー
        
        Args:
            environment: デプロイメント環境
            image_tag: デプロイするイメージタグ
            skip_health_check: ヘルスチェックスキップフラグ
            
        Returns:
            トリガー結果
        """
        inputs = {
            "environment": environment.value,
            "skip_health_check": str(skip_health_check).lower()
        }
        
        if image_tag:
            inputs["image_tag"] = image_tag
        
        request = TriggerRequest(
            workflow_id="deploy-only.yml",
            environment=environment,
            trigger_type=TriggerType.MANUAL,
            inputs=inputs
        )
        
        return self.trigger_deployment(request)
    
    def trigger_rollback(self, environment: Environment,
                        target_revision: str,
                        reason: Optional[str] = None) -> TriggerResult:
        """
        ロールバックワークフローをトリガー
        
        Args:
            environment: デプロイメント環境
            target_revision: ロールバック先のリビジョン
            reason: ロールバック理由
            
        Returns:
            トリガー結果
        """
        inputs = {
            "environment": environment.value,
            "target_revision": target_revision
        }
        
        if reason:
            inputs["reason"] = reason
        
        request = TriggerRequest(
            workflow_id="rollback.yml",
            environment=environment,
            trigger_type=TriggerType.MANUAL,
            inputs=inputs,
            wait_for_completion=True,
            timeout_minutes=15
        )
        
        return self.trigger_deployment(request)
    
    def _prepare_workflow_inputs(self, request: TriggerRequest) -> Dict[str, str]:
        """
        ワークフロー入力パラメータを準備
        
        Args:
            request: トリガーリクエスト
            
        Returns:
            ワークフロー入力パラメータ
        """
        # 基本パラメータ
        inputs = self.parameter_manager.get_workflow_parameters(
            request.environment,
            request.trigger_type
        )
        
        # リクエスト固有のパラメータを追加
        if request.inputs:
            inputs.update(request.inputs)
        
        # 全ての値を文字列に変換（GitHub Actions要件）
        return {k: str(v) for k, v in inputs.items()}
    
    def _validate_workflow_request(self, request: TriggerRequest, 
                                  inputs: Dict[str, str]) -> None:
        """
        ワークフローリクエストを検証
        
        Args:
            request: トリガーリクエスト
            inputs: ワークフロー入力パラメータ
        """
        # ワークフロー設定の確認
        if request.workflow_id not in self.workflow_configs:
            raise DeploymentError(f"未知のワークフローID: {request.workflow_id}")
        
        workflow_config = self.workflow_configs[request.workflow_id]
        
        # 手動トリガーサポートの確認
        if (request.trigger_type == TriggerType.MANUAL and 
            not workflow_config.get("supports_manual_trigger", False)):
            raise DeploymentError(f"ワークフロー {request.workflow_id} は手動トリガーをサポートしていません")
        
        # 必須パラメータの確認
        required_inputs = workflow_config.get("required_inputs", [])
        for required_input in required_inputs:
            if required_input not in inputs:
                raise DeploymentError(f"必須パラメータが不足しています: {required_input}")
        
        # 環境固有の検証
        if request.environment == Environment.PRODUCTION:
            # 本番環境への追加検証
            if request.trigger_type == TriggerType.AUTOMATIC and not inputs.get("force_deploy"):
                # 自動デプロイの場合は追加チェック
                pass
    
    def _wait_for_completion(self, result: TriggerResult, 
                           timeout_minutes: int) -> TriggerResult:
        """
        ワークフロー完了まで待機
        
        Args:
            result: トリガー結果
            timeout_minutes: タイムアウト時間（分）
            
        Returns:
            更新されたトリガー結果
        """
        logger.info(f"Waiting for workflow completion (timeout: {timeout_minutes} minutes)")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                workflow_run = self.github_client.get_workflow_run(result.run_id)
                
                result.status = workflow_run.status
                
                if workflow_run.status == "completed":
                    result.conclusion = workflow_run.conclusion
                    result.completed_at = workflow_run.updated_at.isoformat()
                    
                    if workflow_run.conclusion == "success":
                        logger.info(f"Workflow completed successfully: {result.run_id}")
                    else:
                        logger.warning(f"Workflow completed with conclusion: {workflow_run.conclusion}")
                    
                    break
                
                # 進行中の場合は待機
                time.sleep(30)  # 30秒間隔でチェック
                
            except Exception as e:
                logger.error(f"Error while waiting for workflow completion: {e}")
                result.error_message = str(e)
                break
        else:
            # タイムアウト
            logger.warning(f"Workflow wait timeout after {timeout_minutes} minutes")
            result.error_message = f"タイムアウト（{timeout_minutes}分）"
        
        return result
    
    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """
        利用可能なワークフロー一覧を取得
        
        Returns:
            ワークフロー一覧
        """
        workflows = []
        
        for workflow_id, config in self.workflow_configs.items():
            workflows.append({
                "id": workflow_id,
                "name": config["name"],
                "description": config["description"],
                "supports_manual_trigger": config.get("supports_manual_trigger", False),
                "required_inputs": config.get("required_inputs", []),
                "optional_inputs": config.get("optional_inputs", [])
            })
        
        return workflows
    
    def validate_connection(self) -> bool:
        """
        GitHub接続を検証
        
        Returns:
            接続成功フラグ
        """
        try:
            return self.github_client.validate_connection()
        except Exception as e:
            logger.error(f"GitHub connection validation failed: {e}")
            return False