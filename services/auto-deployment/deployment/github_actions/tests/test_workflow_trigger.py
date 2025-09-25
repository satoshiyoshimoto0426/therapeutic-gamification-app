"""
Workflow Trigger テスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from ..workflow_trigger import (
    WorkflowTrigger, TriggerRequest, TriggerResult, TriggerType
)
from ..github_client import GitHubClient, WorkflowRun
try:
    from ....config import DeploymentConfig, Environment, DeploymentStrategy
    from ....exceptions import DeploymentError
except ImportError:
    from enum import Enum
    from dataclasses import dataclass
    
    class Environment(Enum):
        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
    
    class DeploymentStrategy(Enum):
        BLUE_GREEN = "blue_green"
        ROLLING_UPDATE = "rolling_update"
    
    @dataclass
    class DeploymentConfig:
        environment: Environment
        strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    
    class DeploymentError(Exception):
        pass


class TestWorkflowTrigger:
    """WorkflowTrigger テストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.config = DeploymentConfig(
            environment=Environment.STAGING,
            strategy=DeploymentStrategy.BLUE_GREEN
        )
        
        self.mock_github_client = Mock(spec=GitHubClient)
        self.trigger = WorkflowTrigger(self.config, self.mock_github_client)
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.trigger.config == self.config
        assert self.trigger.github_client == self.mock_github_client
        assert "ci-cd-pipeline.yml" in self.trigger.workflow_configs
        assert "deploy-only.yml" in self.trigger.workflow_configs
        assert "rollback.yml" in self.trigger.workflow_configs
    
    def test_trigger_deployment_success(self):
        """デプロイメントトリガー成功テスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=123,
            name="CI/CD Pipeline",
            status="queued",
            conclusion=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/123",
            head_sha="abc123",
            head_branch="main",
            workflow_id=456,
            run_number=1
        )
        
        self.mock_github_client.trigger_workflow.return_value = 123
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # テスト実行
        request = TriggerRequest(
            workflow_id="ci-cd-pipeline.yml",
            ref="main",
            environment=Environment.STAGING,
            inputs={"environment": "staging"}
        )
        
        result = self.trigger.trigger_deployment(request)
        
        # 検証
        assert result.run_id == 123
        assert result.workflow_name == "CI/CD Pipeline"
        assert result.status == "queued"
        assert result.html_url == "https://github.com/test/test/actions/runs/123"
        
        self.mock_github_client.trigger_workflow.assert_called_once()
        self.mock_github_client.get_workflow_run.assert_called_once_with(123)
    
    def test_trigger_deployment_with_wait(self):
        """完了待ちありのデプロイメントトリガーテスト"""
        # モック設定
        mock_run_initial = WorkflowRun(
            id=123,
            name="CI/CD Pipeline",
            status="queued",
            conclusion=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/123",
            head_sha="abc123",
            head_branch="main",
            workflow_id=456,
            run_number=1
        )
        
        mock_run_completed = WorkflowRun(
            id=123,
            name="CI/CD Pipeline",
            status="completed",
            conclusion="success",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/123",
            head_sha="abc123",
            head_branch="main",
            workflow_id=456,
            run_number=1
        )
        
        self.mock_github_client.trigger_workflow.return_value = 123
        self.mock_github_client.get_workflow_run.side_effect = [
            mock_run_initial,  # 初回取得
            mock_run_completed  # 完了待ち中の取得
        ]
        
        # テスト実行
        request = TriggerRequest(
            workflow_id="ci-cd-pipeline.yml",
            wait_for_completion=True,
            timeout_minutes=1
        )
        
        with patch('time.sleep'):  # sleepをモック化
            result = self.trigger.trigger_deployment(request)
        
        # 検証
        assert result.conclusion == "success"
        assert result.completed_at is not None
    
    def test_trigger_deployment_invalid_workflow(self):
        """無効なワークフローIDでのトリガーテスト"""
        request = TriggerRequest(workflow_id="invalid.yml")
        
        with pytest.raises(DeploymentError, match="未知のワークフローID"):
            self.trigger.trigger_deployment(request)
    
    def test_trigger_ci_cd_pipeline(self):
        """CI/CDパイプライントリガーテスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=123,
            name="CI/CD Pipeline",
            status="queued",
            conclusion=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/123",
            head_sha="abc123",
            head_branch="main",
            workflow_id=456,
            run_number=1
        )
        
        self.mock_github_client.trigger_workflow.return_value = 123
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # テスト実行
        result = self.trigger.trigger_ci_cd_pipeline(
            environment=Environment.STAGING,
            ref="develop",
            skip_tests=True,
            force_deploy=False
        )
        
        # 検証
        assert result.run_id == 123
        
        # trigger_workflowの呼び出し引数を確認
        call_args = self.mock_github_client.trigger_workflow.call_args
        assert call_args[1]["workflow_id"] == "ci-cd-pipeline.yml"
        assert call_args[1]["ref"] == "develop"
        assert call_args[1]["inputs"]["environment"] == "staging"
        assert call_args[1]["inputs"]["skip_tests"] == "true"
        assert call_args[1]["inputs"]["force_deploy"] == "false"
    
    def test_trigger_deploy_only(self):
        """デプロイのみトリガーテスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=124,
            name="Deploy Only",
            status="queued",
            conclusion=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/124",
            head_sha="abc123",
            head_branch="main",
            workflow_id=457,
            run_number=1
        )
        
        self.mock_github_client.trigger_workflow.return_value = 124
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # テスト実行
        result = self.trigger.trigger_deploy_only(
            environment=Environment.PRODUCTION,
            image_tag="v1.2.3",
            skip_health_check=True
        )
        
        # 検証
        assert result.run_id == 124
        
        # trigger_workflowの呼び出し引数を確認
        call_args = self.mock_github_client.trigger_workflow.call_args
        assert call_args[1]["workflow_id"] == "deploy-only.yml"
        assert call_args[1]["inputs"]["environment"] == "production"
        assert call_args[1]["inputs"]["image_tag"] == "v1.2.3"
        assert call_args[1]["inputs"]["skip_health_check"] == "true"
    
    def test_trigger_rollback(self):
        """ロールバックトリガーテスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=125,
            name="Rollback",
            status="completed",
            conclusion="success",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/125",
            head_sha="abc123",
            head_branch="main",
            workflow_id=458,
            run_number=1
        )
        
        self.mock_github_client.trigger_workflow.return_value = 125
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # テスト実行
        with patch('time.sleep'):  # sleepをモック化
            result = self.trigger.trigger_rollback(
                environment=Environment.PRODUCTION,
                target_revision="rev-20231201-123456",
                reason="Critical bug fix"
            )
        
        # 検証
        assert result.run_id == 125
        assert result.conclusion == "success"
        
        # trigger_workflowの呼び出し引数を確認
        call_args = self.mock_github_client.trigger_workflow.call_args
        assert call_args[1]["workflow_id"] == "rollback.yml"
        assert call_args[1]["inputs"]["environment"] == "production"
        assert call_args[1]["inputs"]["target_revision"] == "rev-20231201-123456"
        assert call_args[1]["inputs"]["reason"] == "Critical bug fix"
    
    def test_get_available_workflows(self):
        """利用可能なワークフロー一覧取得テスト"""
        workflows = self.trigger.get_available_workflows()
        
        assert len(workflows) == 3
        
        # CI/CDパイプライン
        ci_cd = next(w for w in workflows if w["id"] == "ci-cd-pipeline.yml")
        assert ci_cd["name"] == "CI/CD Pipeline"
        assert ci_cd["supports_manual_trigger"] is True
        assert "environment" in ci_cd["optional_inputs"]
        
        # デプロイのみ
        deploy_only = next(w for w in workflows if w["id"] == "deploy-only.yml")
        assert deploy_only["name"] == "Deploy Only"
        assert "environment" in deploy_only["required_inputs"]
        
        # ロールバック
        rollback = next(w for w in workflows if w["id"] == "rollback.yml")
        assert rollback["name"] == "Rollback"
        assert "target_revision" in rollback["required_inputs"]
    
    def test_validate_connection(self):
        """接続検証テスト"""
        self.mock_github_client.validate_connection.return_value = True
        
        result = self.trigger.validate_connection()
        
        assert result is True
        self.mock_github_client.validate_connection.assert_called_once()
    
    def test_validate_connection_failure(self):
        """接続検証失敗テスト"""
        self.mock_github_client.validate_connection.side_effect = Exception("Connection failed")
        
        result = self.trigger.validate_connection()
        
        assert result is False


class TestTriggerRequest:
    """TriggerRequest テストクラス"""
    
    def test_trigger_request_creation(self):
        """TriggerRequest作成テスト"""
        request = TriggerRequest(
            workflow_id="test.yml",
            ref="develop",
            environment=Environment.STAGING,
            trigger_type=TriggerType.MANUAL,
            inputs={"key": "value"},
            wait_for_completion=True,
            timeout_minutes=45
        )
        
        assert request.workflow_id == "test.yml"
        assert request.ref == "develop"
        assert request.environment == Environment.STAGING
        assert request.trigger_type == TriggerType.MANUAL
        assert request.inputs == {"key": "value"}
        assert request.wait_for_completion is True
        assert request.timeout_minutes == 45
    
    def test_trigger_request_defaults(self):
        """TriggerRequestデフォルト値テスト"""
        request = TriggerRequest(workflow_id="test.yml")
        
        assert request.ref == "main"
        assert request.environment == Environment.PRODUCTION
        assert request.trigger_type == TriggerType.MANUAL
        assert request.inputs is None
        assert request.wait_for_completion is False
        assert request.timeout_minutes == 30


class TestTriggerResult:
    """TriggerResult テストクラス"""
    
    def test_trigger_result_creation(self):
        """TriggerResult作成テスト"""
        result = TriggerResult(
            run_id=123,
            workflow_name="Test Workflow",
            status="completed",
            html_url="https://github.com/test/test/actions/runs/123",
            triggered_at="2023-01-01T00:00:00Z",
            completed_at="2023-01-01T01:00:00Z",
            conclusion="success",
            error_message=None
        )
        
        assert result.run_id == 123
        assert result.workflow_name == "Test Workflow"
        assert result.status == "completed"
        assert result.html_url == "https://github.com/test/test/actions/runs/123"
        assert result.triggered_at == "2023-01-01T00:00:00Z"
        assert result.completed_at == "2023-01-01T01:00:00Z"
        assert result.conclusion == "success"
        assert result.error_message is None


class TestTriggerType:
    """TriggerType テストクラス"""
    
    def test_trigger_type_values(self):
        """TriggerType値テスト"""
        assert TriggerType.MANUAL.value == "manual"
        assert TriggerType.AUTOMATIC.value == "automatic"
        assert TriggerType.SCHEDULED.value == "scheduled"
        assert TriggerType.WEBHOOK.value == "webhook"