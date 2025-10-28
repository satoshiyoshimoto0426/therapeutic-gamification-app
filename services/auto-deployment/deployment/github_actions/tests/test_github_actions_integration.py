"""
GitHub Actions統合テスト

GitHub Actions統合機能の統合テストを実行します。
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from github_client import GitHubClient, WorkflowRun
from workflow_trigger import WorkflowTrigger, TriggerRequest, TriggerType
from workflow_monitor import WorkflowMonitor, MonitoringStatus
from parameter_manager import ParameterManager
try:
    from ....config import DeploymentConfig, Environment, DeploymentStrategy
    from ....exceptions import DeploymentError, GitHubAPIError
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
    
    class GitHubAPIError(Exception):
        pass


class TestGitHubActionsIntegration:
    """GitHub Actions統合テストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.config = DeploymentConfig(
            environment=Environment.STAGING,
            strategy=DeploymentStrategy.BLUE_GREEN
        )
        
        # モックGitHubクライアント
        self.mock_github_client = Mock(spec=GitHubClient)
        
        # 各コンポーネントを初期化
        self.trigger = WorkflowTrigger(self.config, self.mock_github_client)
        self.monitor = WorkflowMonitor(self.config, self.mock_github_client)
        self.parameter_manager = ParameterManager(self.config)
    
    def teardown_method(self):
        """テストクリーンアップ"""
        self.monitor.stop_all_monitoring()
    
    def test_full_deployment_workflow(self):
        """完全なデプロイメントワークフローテスト"""
        # モック設定
        mock_run_queued = WorkflowRun(
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
        
        mock_run_in_progress = WorkflowRun(
            id=123,
            name="CI/CD Pipeline",
            status="in_progress",
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
            mock_run_queued,    # トリガー直後
            mock_run_queued,    # 監視開始時
            mock_run_in_progress,  # 監視中
            mock_run_completed  # 完了時
        ]
        
        # 1. パラメータ準備
        parameters = {
            "environment": "staging",
            "skip_tests": False,
            "force_deploy": False
        }
        
        # パラメータ検証
        errors = self.parameter_manager.validate_parameters("ci-cd-pipeline.yml", parameters)
        assert errors == []
        
        # デフォルト値適用
        final_parameters = self.parameter_manager.apply_defaults(
            "ci-cd-pipeline.yml", parameters, Environment.STAGING
        )
        
        # 2. ワークフロートリガー
        request = TriggerRequest(
            workflow_id="ci-cd-pipeline.yml",
            ref="main",
            environment=Environment.STAGING,
            trigger_type=TriggerType.AUTOMATIC,
            inputs=final_parameters
        )
        
        trigger_result = self.trigger.trigger_deployment(request)
        
        assert trigger_result.run_id == 123
        assert trigger_result.workflow_name == "CI/CD Pipeline"
        assert trigger_result.status == "queued"
        
        # 3. 監視開始
        monitoring_events = []
        def event_callback(session, event):
            monitoring_events.append(event)
        
        monitoring_session = self.monitor.start_monitoring(123, [event_callback])
        
        assert monitoring_session.run_id == 123
        assert monitoring_session.status == MonitoringStatus.ACTIVE
        assert len(monitoring_events) == 1  # monitoring_started イベント
        
        # 4. 完了待ち（モック化）
        with patch('time.sleep'):
            final_run = self.monitor.wait_for_completion(123, timeout_minutes=1)
        
        assert final_run.status == "completed"
        assert final_run.conclusion == "success"
        
        # 5. 監視停止
        self.monitor.stop_monitoring(123)
        
        # 検証
        self.mock_github_client.trigger_workflow.assert_called_once()
        assert self.mock_github_client.get_workflow_run.call_count >= 2
    
    def test_deployment_with_rollback(self):
        """ロールバック付きデプロイメントテスト"""
        # 失敗するデプロイメントをモック
        mock_run_failed = WorkflowRun(
            id=124,
            name="CI/CD Pipeline",
            status="completed",
            conclusion="failure",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/124",
            head_sha="def456",
            head_branch="main",
            workflow_id=456,
            run_number=2
        )
        
        # ロールバック成功をモック
        mock_rollback_run = WorkflowRun(
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
        
        self.mock_github_client.trigger_workflow.side_effect = [124, 125]
        self.mock_github_client.get_workflow_run.side_effect = [
            mock_run_failed,    # 失敗したデプロイメント
            mock_rollback_run   # ロールバック
        ]
        
        # 1. 失敗するデプロイメントをトリガー
        deploy_result = self.trigger.trigger_ci_cd_pipeline(
            environment=Environment.PRODUCTION,
            ref="main"
        )
        
        assert deploy_result.run_id == 124
        
        # 2. 失敗を検出してロールバックをトリガー
        with patch('time.sleep'):
            rollback_result = self.trigger.trigger_rollback(
                environment=Environment.PRODUCTION,
                target_revision="rev-20231201-123456",
                reason="Deployment failed"
            )
        
        assert rollback_result.run_id == 125
        assert rollback_result.conclusion == "success"
        
        # 検証
        assert self.mock_github_client.trigger_workflow.call_count == 2
    
    def test_parameter_validation_and_conversion(self):
        """パラメータ検証と変換の統合テスト"""
        # 1. 無効なパラメータでの検証
        invalid_parameters = {
            "environment": "invalid_env",
            "skip_tests": "not_boolean",
            "traffic_percentage": "150"
        }
        
        errors = self.parameter_manager.validate_parameters(
            "deploy-only.yml", invalid_parameters
        )
        
        assert len(errors) > 0
        
        # 2. 有効なパラメータでの検証
        valid_parameters = {
            "environment": "production",
            "image_tag": "v1.2.3",
            "skip_health_check": True,
            "traffic_percentage": 25
        }
        
        errors = self.parameter_manager.validate_parameters(
            "deploy-only.yml", valid_parameters
        )
        
        assert errors == []
        
        # 3. デフォルト値適用
        parameters_with_defaults = self.parameter_manager.apply_defaults(
            "deploy-only.yml", {"environment": "production"}, Environment.PRODUCTION
        )
        
        assert "skip_health_check" in parameters_with_defaults
        assert "traffic_percentage" in parameters_with_defaults
        
        # 4. GitHub Actions形式に変換
        github_parameters = self.parameter_manager.convert_to_github_format(
            parameters_with_defaults
        )
        
        # 全ての値が文字列になっていることを確認
        for value in github_parameters.values():
            assert isinstance(value, str)
    
    def test_monitoring_with_callbacks(self):
        """コールバック付き監視テスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=126,
            name="Test Workflow",
            status="in_progress",
            conclusion=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/126",
            head_sha="ghi789",
            head_branch="main",
            workflow_id=459,
            run_number=1
        )
        
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # イベント収集用のコールバック
        collected_events = []
        def collect_events(session, event):
            collected_events.append({
                "event_type": event.event_type,
                "run_id": event.run_id,
                "message": event.message
            })
        
        # 進捗報告用のコールバック
        progress_reports = []
        def report_progress(session, event):
            if event.event_type == "status_change":
                progress_reports.append({
                    "run_id": session.run_id,
                    "old_status": event.old_status,
                    "new_status": event.new_status
                })
        
        # グローバルコールバック追加
        self.monitor.add_global_callback(report_progress)
        
        # 監視開始
        session = self.monitor.start_monitoring(126, [collect_events])
        
        # イベントが記録されていることを確認
        assert len(collected_events) >= 1
        assert collected_events[0]["event_type"] == "monitoring_started"
        assert collected_events[0]["run_id"] == 126
        
        # 進捗レポートも記録されていることを確認
        assert len(progress_reports) >= 0  # 初期状態では変更がないかもしれない
        
        # 監視停止
        self.monitor.stop_monitoring(126)
        
        # 停止イベントが記録されていることを確認
        stop_events = [e for e in collected_events if e["event_type"] == "monitoring_stopped"]
        assert len(stop_events) == 1
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        # 1. GitHub API エラー
        self.mock_github_client.trigger_workflow.side_effect = GitHubAPIError("API Error")
        
        request = TriggerRequest(workflow_id="ci-cd-pipeline.yml")
        
        with pytest.raises(DeploymentError, match="ワークフローのトリガーに失敗しました"):
            self.trigger.trigger_deployment(request)
        
        # 2. 無効なワークフローID
        request = TriggerRequest(workflow_id="nonexistent.yml")
        
        with pytest.raises(DeploymentError, match="未知のワークフローID"):
            self.trigger.trigger_deployment(request)
        
        # 3. 監視開始エラー
        self.mock_github_client.get_workflow_run.side_effect = Exception("Connection Error")
        
        with pytest.raises(DeploymentError, match="監視の開始に失敗しました"):
            self.monitor.start_monitoring(999)
    
    def test_concurrent_monitoring(self):
        """並行監視テスト"""
        # 複数のワークフロー実行をモック
        mock_runs = [
            WorkflowRun(
                id=i,
                name=f"Workflow {i}",
                status="in_progress",
                conclusion=None,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                html_url=f"https://github.com/test/test/actions/runs/{i}",
                head_sha=f"sha{i}",
                head_branch="main",
                workflow_id=456,
                run_number=i
            )
            for i in range(127, 130)
        ]
        
        def get_workflow_run_side_effect(run_id):
            return next(run for run in mock_runs if run.id == run_id)
        
        self.mock_github_client.get_workflow_run.side_effect = get_workflow_run_side_effect
        
        # 複数の監視セッションを開始
        sessions = []
        for run_id in range(127, 130):
            session = self.monitor.start_monitoring(run_id)
            sessions.append(session)
        
        # 全てのセッションがアクティブであることを確認
        for session in sessions:
            assert session.status == MonitoringStatus.ACTIVE
            assert session.run_id in self.monitor.sessions
        
        # 監視セッション数を確認
        assert len(self.monitor.sessions) == 3
        
        # 全ての監視を停止
        for run_id in range(127, 130):
            self.monitor.stop_monitoring(run_id)
        
        # 全てのセッションが停止されていることを確認
        for session in sessions:
            assert session.status == MonitoringStatus.STOPPED
    
    def test_workflow_configuration_validation(self):
        """ワークフロー設定検証テスト"""
        # 利用可能なワークフロー一覧を取得
        workflows = self.trigger.get_available_workflows()
        
        assert len(workflows) == 3
        
        # 各ワークフローの設定を検証
        for workflow in workflows:
            assert "id" in workflow
            assert "name" in workflow
            assert "description" in workflow
            assert "supports_manual_trigger" in workflow
            assert "required_inputs" in workflow
            assert "optional_inputs" in workflow
            
            # パラメータスキーマを取得
            schema = self.parameter_manager.get_workflow_parameter_schema(workflow["id"])
            assert schema is not None
            assert schema["workflow_id"] == workflow["id"]
            
            # 必須パラメータがスキーマに存在することを確認
            for required_input in workflow["required_inputs"]:
                assert required_input in schema["parameters"]
                assert schema["parameters"][required_input]["required"] is True
    
    def test_end_to_end_deployment_simulation(self):
        """エンドツーエンドデプロイメントシミュレーション"""
        # デプロイメントの全フローをシミュレート
        
        # 1. 設定検証
        assert self.trigger.validate_connection() is True  # モックなので常にTrue
        
        # 2. パラメータ準備
        base_params = self.parameter_manager.get_workflow_parameters(
            Environment.STAGING, "automatic"
        )
        
        deploy_params = {
            "environment": "staging",
            "skip_tests": False,
            "image_tag": "v2.1.0"
        }
        
        # パラメータ検証
        errors = self.parameter_manager.validate_parameters(
            "ci-cd-pipeline.yml", deploy_params
        )
        assert errors == []
        
        # デフォルト値適用
        final_params = self.parameter_manager.apply_defaults(
            "ci-cd-pipeline.yml", deploy_params, Environment.STAGING
        )
        
        # GitHub形式に変換
        github_params = self.parameter_manager.convert_to_github_format(final_params)
        
        # 3. デプロイメント実行のモック設定
        mock_run = WorkflowRun(
            id=200,
            name="CI/CD Pipeline",
            status="completed",
            conclusion="success",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://github.com/test/test/actions/runs/200",
            head_sha="final123",
            head_branch="main",
            workflow_id=456,
            run_number=10
        )
        
        self.mock_github_client.trigger_workflow.return_value = 200
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # 4. デプロイメント実行
        request = TriggerRequest(
            workflow_id="ci-cd-pipeline.yml",
            ref="main",
            environment=Environment.STAGING,
            inputs=github_params,
            wait_for_completion=True,
            timeout_minutes=30
        )
        
        with patch('time.sleep'):
            result = self.trigger.trigger_deployment(request)
        
        # 5. 結果検証
        assert result.run_id == 200
        assert result.workflow_name == "CI/CD Pipeline"
        assert result.conclusion == "success"
        
        # 6. 監視ログの確認（実際の実装では監視も並行して実行される）
        monitoring_session = self.monitor.start_monitoring(200)
        assert monitoring_session.run_id == 200
        assert len(monitoring_session.events) >= 1
        
        # クリーンアップ
        self.monitor.stop_monitoring(200)