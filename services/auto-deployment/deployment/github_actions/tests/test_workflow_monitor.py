"""
Workflow Monitor テスト
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from workflow_monitor import (
    WorkflowMonitor, MonitoringSession, MonitoringEvent, MonitoringStatus
)
from github_client import GitHubClient, WorkflowRun, WorkflowJob
try:
    from ....config import DeploymentConfig, Environment
    from ....exceptions import DeploymentError
except ImportError:
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


class TestWorkflowMonitor:
    """WorkflowMonitor テストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.config = DeploymentConfig(environment=Environment.STAGING)
        self.mock_github_client = Mock(spec=GitHubClient)
        self.monitor = WorkflowMonitor(self.config, self.mock_github_client)
    
    def teardown_method(self):
        """テストクリーンアップ"""
        self.monitor.stop_all_monitoring()
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.monitor.config == self.config
        assert self.monitor.github_client == self.mock_github_client
        assert self.monitor.sessions == {}
        assert self.monitor.monitoring_active is False
        assert self.monitor.monitoring_interval == 30
    
    def test_start_monitoring_success(self):
        """監視開始成功テスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=123,
            name="Test Workflow",
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
        
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # コールバック関数
        callback_called = []
        def test_callback(session, event):
            callback_called.append((session, event))
        
        # テスト実行
        session = self.monitor.start_monitoring(123, [test_callback])
        
        # 検証
        assert session.run_id == 123
        assert session.workflow_name == "Test Workflow"
        assert session.status == MonitoringStatus.ACTIVE
        assert len(session.events) == 1
        assert session.events[0].event_type == "monitoring_started"
        assert 123 in self.monitor.sessions
        assert len(callback_called) == 1
        
        self.mock_github_client.get_workflow_run.assert_called_once_with(123)
    
    def test_start_monitoring_failure(self):
        """監視開始失敗テスト"""
        self.mock_github_client.get_workflow_run.side_effect = Exception("API Error")
        
        with pytest.raises(DeploymentError, match="監視の開始に失敗しました"):
            self.monitor.start_monitoring(123)
    
    def test_stop_monitoring(self):
        """監視停止テスト"""
        # 監視セッションを作成
        session = MonitoringSession(
            run_id=123,
            workflow_name="Test Workflow",
            started_at=datetime.now()
        )
        self.monitor.sessions[123] = session
        
        # コールバック関数
        callback_called = []
        def test_callback(session, event):
            callback_called.append((session, event))
        
        session.callbacks.append(test_callback)
        
        # テスト実行
        result = self.monitor.stop_monitoring(123)
        
        # 検証
        assert result is True
        assert session.status == MonitoringStatus.STOPPED
        assert len(session.events) == 1
        assert session.events[0].event_type == "monitoring_stopped"
        assert len(callback_called) == 1
    
    def test_stop_monitoring_not_found(self):
        """存在しない監視セッションの停止テスト"""
        result = self.monitor.stop_monitoring(999)
        assert result is False
    
    def test_get_monitoring_status(self):
        """監視ステータス取得テスト"""
        # 監視セッションを作成
        session = MonitoringSession(
            run_id=123,
            workflow_name="Test Workflow",
            started_at=datetime.now()
        )
        self.monitor.sessions[123] = session
        
        # テスト実行
        result = self.monitor.get_monitoring_status(123)
        
        # 検証
        assert result == session
        
        # 存在しないセッション
        result = self.monitor.get_monitoring_status(999)
        assert result is None
    
    def test_get_workflow_progress(self):
        """ワークフロー進捗取得テスト"""
        # モック設定
        mock_run = WorkflowRun(
            id=123,
            name="Test Workflow",
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
        
        mock_jobs = [
            WorkflowJob(
                id=789,
                name="test-job-1",
                status="completed",
                conclusion="success",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                html_url="https://github.com/test/test/actions/runs/123/jobs/789",
                steps=[
                    {"name": "Checkout", "status": "completed", "conclusion": "success", "number": 1},
                    {"name": "Test", "status": "completed", "conclusion": "success", "number": 2}
                ]
            ),
            WorkflowJob(
                id=790,
                name="test-job-2",
                status="in_progress",
                conclusion=None,
                started_at=datetime.now(timezone.utc),
                completed_at=None,
                html_url="https://github.com/test/test/actions/runs/123/jobs/790",
                steps=[
                    {"name": "Setup", "status": "completed", "conclusion": "success", "number": 1},
                    {"name": "Deploy", "status": "in_progress", "conclusion": None, "number": 2}
                ]
            )
        ]
        
        self.mock_github_client.get_workflow_run.return_value = mock_run
        self.mock_github_client.get_workflow_jobs.return_value = mock_jobs
        
        # テスト実行
        progress = self.monitor.get_workflow_progress(123)
        
        # 検証
        assert progress["run_id"] == 123
        assert progress["workflow_name"] == "Test Workflow"
        assert progress["status"] == "in_progress"
        assert progress["progress"]["jobs"]["total"] == 2
        assert progress["progress"]["jobs"]["completed"] == 1
        assert progress["progress"]["jobs"]["percentage"] == 50.0
        assert progress["progress"]["steps"]["total"] == 4
        assert progress["progress"]["steps"]["completed"] == 3
        assert progress["progress"]["steps"]["percentage"] == 75.0
        assert len(progress["jobs"]) == 2
    
    def test_wait_for_completion_success(self):
        """完了待ち成功テスト"""
        # モック設定
        mock_run_in_progress = WorkflowRun(
            id=123,
            name="Test Workflow",
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
            name="Test Workflow",
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
        
        self.mock_github_client.get_workflow_run.side_effect = [
            mock_run_in_progress,
            mock_run_completed
        ]
        
        # 進捗コールバック
        progress_calls = []
        def progress_callback(progress):
            progress_calls.append(progress)
        
        # テスト実行
        with patch('time.sleep'):  # sleepをモック化
            with patch.object(self.monitor, 'get_workflow_progress', return_value={"status": "in_progress"}):
                result = self.monitor.wait_for_completion(123, 1, progress_callback)
        
        # 検証
        assert result.status == "completed"
        assert result.conclusion == "success"
        assert len(progress_calls) >= 1
    
    def test_wait_for_completion_timeout(self):
        """完了待ちタイムアウトテスト"""
        # モック設定（常に進行中を返す）
        mock_run = WorkflowRun(
            id=123,
            name="Test Workflow",
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
        
        self.mock_github_client.get_workflow_run.return_value = mock_run
        
        # テスト実行（短いタイムアウト）
        with patch('time.time', side_effect=[0, 0, 70]):  # 70秒経過をシミュレート
            with patch('time.sleep'):
                with pytest.raises(DeploymentError, match="ワークフロー完了の待機がタイムアウトしました"):
                    self.monitor.wait_for_completion(123, 1)  # 1分でタイムアウト
    
    def test_add_remove_global_callback(self):
        """グローバルコールバック追加・削除テスト"""
        def test_callback(session, event):
            pass
        
        # 追加テスト
        self.monitor.add_global_callback(test_callback)
        assert test_callback in self.monitor.global_callbacks
        
        # 削除テスト
        result = self.monitor.remove_global_callback(test_callback)
        assert result is True
        assert test_callback not in self.monitor.global_callbacks
        
        # 存在しないコールバックの削除
        result = self.monitor.remove_global_callback(test_callback)
        assert result is False
    
    def test_cleanup_old_sessions(self):
        """古いセッションクリーンアップテスト"""
        # 古いセッションを作成
        old_session = MonitoringSession(
            run_id=123,
            workflow_name="Old Workflow",
            started_at=datetime.now() - timedelta(hours=25),  # 25時間前
            status=MonitoringStatus.STOPPED
        )
        
        # 新しいセッションを作成
        new_session = MonitoringSession(
            run_id=124,
            workflow_name="New Workflow",
            started_at=datetime.now(),
            status=MonitoringStatus.ACTIVE
        )
        
        self.monitor.sessions[123] = old_session
        self.monitor.sessions[124] = new_session
        
        # テスト実行
        from datetime import timedelta
        cleaned_count = self.monitor.cleanup_old_sessions(24)
        
        # 検証
        assert cleaned_count == 1
        assert 123 not in self.monitor.sessions
        assert 124 in self.monitor.sessions


class TestMonitoringSession:
    """MonitoringSession テストクラス"""
    
    def test_monitoring_session_creation(self):
        """MonitoringSession作成テスト"""
        started_at = datetime.now()
        
        session = MonitoringSession(
            run_id=123,
            workflow_name="Test Workflow",
            started_at=started_at,
            status=MonitoringStatus.ACTIVE
        )
        
        assert session.run_id == 123
        assert session.workflow_name == "Test Workflow"
        assert session.started_at == started_at
        assert session.status == MonitoringStatus.ACTIVE
        assert session.events == []
        assert session.last_check is None
        assert session.error_count == 0
        assert session.callbacks == []


class TestMonitoringEvent:
    """MonitoringEvent テストクラス"""
    
    def test_monitoring_event_creation(self):
        """MonitoringEvent作成テスト"""
        timestamp = datetime.now()
        
        event = MonitoringEvent(
            timestamp=timestamp,
            run_id=123,
            event_type="status_change",
            old_status="queued",
            new_status="in_progress",
            job_name="test-job",
            step_name="test-step",
            message="Status changed",
            metadata={"key": "value"}
        )
        
        assert event.timestamp == timestamp
        assert event.run_id == 123
        assert event.event_type == "status_change"
        assert event.old_status == "queued"
        assert event.new_status == "in_progress"
        assert event.job_name == "test-job"
        assert event.step_name == "test-step"
        assert event.message == "Status changed"
        assert event.metadata == {"key": "value"}


class TestMonitoringStatus:
    """MonitoringStatus テストクラス"""
    
    def test_monitoring_status_values(self):
        """MonitoringStatus値テスト"""
        assert MonitoringStatus.ACTIVE.value == "active"
        assert MonitoringStatus.PAUSED.value == "paused"
        assert MonitoringStatus.STOPPED.value == "stopped"
        assert MonitoringStatus.ERROR.value == "error"