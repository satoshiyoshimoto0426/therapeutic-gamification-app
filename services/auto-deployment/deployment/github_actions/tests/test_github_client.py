"""
GitHub Client テスト
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import requests

from github_client import GitHubClient, WorkflowRun, WorkflowJob
try:
    from ....exceptions import GitHubAPIError, AuthenticationError
except ImportError:
    class GitHubAPIError(Exception):
        pass
    
    class AuthenticationError(Exception):
        pass


class TestGitHubClient:
    """GitHubClient テストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.mock_token = "test_token"
        self.mock_repo_owner = "test_owner"
        self.mock_repo_name = "test_repo"
        
        with patch.dict('os.environ', {
            'GITHUB_TOKEN': self.mock_token,
            'GITHUB_REPO_OWNER': self.mock_repo_owner,
            'GITHUB_REPO_NAME': self.mock_repo_name
        }):
            self.client = GitHubClient()
    
    def test_initialization_with_token(self):
        """トークンありの初期化テスト"""
        assert self.client.token == self.mock_token
        assert self.client.repo_owner == self.mock_repo_owner
        assert self.client.repo_name == self.mock_repo_name
        assert self.client.base_url == "https://api.github.com"
        assert "Authorization" in self.client.session.headers
    
    def test_initialization_without_token(self):
        """トークンなしの初期化テスト"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(AuthenticationError):
                GitHubClient()
    
    @patch('requests.Session.post')
    @patch('time.sleep')
    def test_trigger_workflow_success(self, mock_sleep, mock_post):
        """ワークフロートリガー成功テスト"""
        # モックレスポンス設定
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # list_workflow_runsのモック
        mock_run = WorkflowRun(
            id=123,
            name="Test Workflow",
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
        
        with patch.object(self.client, 'list_workflow_runs', return_value=[mock_run]):
            run_id = self.client.trigger_workflow("test.yml", "main", {"key": "value"})
        
        assert run_id == 123
        mock_post.assert_called_once()
        mock_sleep.assert_called_once_with(2)
    
    @patch('requests.Session.post')
    def test_trigger_workflow_api_error(self, mock_post):
        """ワークフロートリガーAPIエラーテスト"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_post.return_value = mock_response
        
        with pytest.raises(GitHubAPIError):
            self.client.trigger_workflow("test.yml")
    
    @patch('requests.Session.get')
    def test_get_workflow_run_success(self, mock_get):
        """ワークフロー実行情報取得成功テスト"""
        mock_data = {
            "id": 123,
            "name": "Test Workflow",
            "status": "completed",
            "conclusion": "success",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T01:00:00Z",
            "html_url": "https://github.com/test/test/actions/runs/123",
            "head_sha": "abc123",
            "head_branch": "main",
            "workflow_id": 456,
            "run_number": 1
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        workflow_run = self.client.get_workflow_run(123)
        
        assert workflow_run.id == 123
        assert workflow_run.name == "Test Workflow"
        assert workflow_run.status == "completed"
        assert workflow_run.conclusion == "success"
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_workflow_run_not_found(self, mock_get):
        """ワークフロー実行情報取得失敗テスト"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(GitHubAPIError):
            self.client.get_workflow_run(999)
    
    @patch('requests.Session.get')
    def test_list_workflow_runs_success(self, mock_get):
        """ワークフロー実行一覧取得成功テスト"""
        mock_data = {
            "workflow_runs": [
                {
                    "id": 123,
                    "name": "Test Workflow 1",
                    "status": "completed",
                    "conclusion": "success",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T01:00:00Z",
                    "html_url": "https://github.com/test/test/actions/runs/123",
                    "head_sha": "abc123",
                    "head_branch": "main",
                    "workflow_id": 456,
                    "run_number": 1
                },
                {
                    "id": 124,
                    "name": "Test Workflow 2",
                    "status": "in_progress",
                    "conclusion": None,
                    "created_at": "2023-01-01T02:00:00Z",
                    "updated_at": "2023-01-01T02:30:00Z",
                    "html_url": "https://github.com/test/test/actions/runs/124",
                    "head_sha": "def456",
                    "head_branch": "develop",
                    "workflow_id": 456,
                    "run_number": 2
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        runs = self.client.list_workflow_runs("test.yml")
        
        assert len(runs) == 2
        assert runs[0].id == 123
        assert runs[0].status == "completed"
        assert runs[1].id == 124
        assert runs[1].status == "in_progress"
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_workflow_jobs_success(self, mock_get):
        """ワークフロージョブ取得成功テスト"""
        mock_data = {
            "jobs": [
                {
                    "id": 789,
                    "name": "test-job",
                    "status": "completed",
                    "conclusion": "success",
                    "started_at": "2023-01-01T00:00:00Z",
                    "completed_at": "2023-01-01T00:30:00Z",
                    "html_url": "https://github.com/test/test/actions/runs/123/jobs/789",
                    "steps": [
                        {
                            "name": "Checkout",
                            "status": "completed",
                            "conclusion": "success",
                            "number": 1
                        }
                    ]
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        jobs = self.client.get_workflow_jobs(123)
        
        assert len(jobs) == 1
        assert jobs[0].id == 789
        assert jobs[0].name == "test-job"
        assert jobs[0].status == "completed"
        assert len(jobs[0].steps) == 1
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_cancel_workflow_run_success(self, mock_post):
        """ワークフロー実行キャンセル成功テスト"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.cancel_workflow_run(123)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_workflow_logs_success(self, mock_get):
        """ワークフローログ取得成功テスト"""
        mock_content = b"test log content"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = mock_content
        mock_get.return_value = mock_response
        
        logs = self.client.get_workflow_logs(123)
        
        assert logs == mock_content
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_create_deployment_status_success(self, mock_post):
        """デプロイメントステータス作成成功テスト"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.create_deployment_status(
            123, "success", "https://example.com", "Deployment successful"
        )
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.Session.get')
    def test_validate_connection_success(self, mock_get):
        """接続検証成功テスト"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.validate_connection()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_validate_connection_failure(self, mock_get):
        """接続検証失敗テスト"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized")
        mock_get.return_value = mock_response
        
        result = self.client.validate_connection()
        
        assert result is False
        mock_get.assert_called_once()


class TestWorkflowRun:
    """WorkflowRun テストクラス"""
    
    def test_workflow_run_creation(self):
        """WorkflowRun作成テスト"""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        run = WorkflowRun(
            id=123,
            name="Test Workflow",
            status="completed",
            conclusion="success",
            created_at=created_at,
            updated_at=updated_at,
            html_url="https://github.com/test/test/actions/runs/123",
            head_sha="abc123",
            head_branch="main",
            workflow_id=456,
            run_number=1
        )
        
        assert run.id == 123
        assert run.name == "Test Workflow"
        assert run.status == "completed"
        assert run.conclusion == "success"
        assert run.created_at == created_at
        assert run.updated_at == updated_at


class TestWorkflowJob:
    """WorkflowJob テストクラス"""
    
    def test_workflow_job_creation(self):
        """WorkflowJob作成テスト"""
        started_at = datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)
        
        job = WorkflowJob(
            id=789,
            name="test-job",
            status="completed",
            conclusion="success",
            started_at=started_at,
            completed_at=completed_at,
            html_url="https://github.com/test/test/actions/runs/123/jobs/789",
            steps=[{"name": "Checkout", "status": "completed"}]
        )
        
        assert job.id == 789
        assert job.name == "test-job"
        assert job.status == "completed"
        assert job.conclusion == "success"
        assert job.started_at == started_at
        assert job.completed_at == completed_at
        assert len(job.steps) == 1