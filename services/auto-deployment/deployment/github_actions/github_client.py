"""
GitHub API クライアント

GitHub APIとの通信を管理するクライアントクラス
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

try:
    from services.auto_deployment.exceptions import GitHubAPIError, AuthenticationError
    from services.auto_deployment.logging_config import get_logger
except ImportError:
    # フォールバック用の例外クラス
    class GitHubAPIError(Exception):
        pass
    
    class AuthenticationError(Exception):
        pass
    
    # フォールバック用のロガー
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


@dataclass
class WorkflowRun:
    """ワークフロー実行情報"""
    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped
    created_at: datetime
    updated_at: datetime
    html_url: str
    head_sha: str
    head_branch: str
    workflow_id: int
    run_number: int


@dataclass
class WorkflowJob:
    """ワークフロージョブ情報"""
    id: int
    name: str
    status: str
    conclusion: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    html_url: str
    steps: List[Dict[str, Any]]


class GitHubClient:
    """GitHub API クライアント"""
    
    def __init__(self, token: Optional[str] = None, repo_owner: Optional[str] = None, 
                 repo_name: Optional[str] = None):
        """
        初期化
        
        Args:
            token: GitHub Personal Access Token
            repo_owner: リポジトリオーナー
            repo_name: リポジトリ名
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = repo_owner or os.getenv("GITHUB_REPO_OWNER", "your-org")
        self.repo_name = repo_name or os.getenv("GITHUB_REPO_NAME", "therapeutic-gamification-app")
        
        if not self.token:
            raise AuthenticationError("GitHub tokenが設定されていません")
        
        self.base_url = "https://api.github.com"
        self.repo_url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}"
        
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "auto-deployment-system/1.0"
        })
        
        # リトライ設定
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"GitHub client initialized for {self.repo_owner}/{self.repo_name}")
    
    def trigger_workflow(self, workflow_id: str, ref: str = "main", 
                        inputs: Optional[Dict[str, Any]] = None) -> int:
        """
        ワークフローをトリガー
        
        Args:
            workflow_id: ワークフローID（ファイル名またはID）
            ref: ブランチ、タグ、またはSHA
            inputs: ワークフローへの入力パラメータ
            
        Returns:
            トリガーされたワークフロー実行ID
        """
        url = f"{self.repo_url}/actions/workflows/{workflow_id}/dispatches"
        
        payload = {
            "ref": ref,
            "inputs": inputs or {}
        }
        
        logger.info(f"Triggering workflow {workflow_id} on {ref} with inputs: {inputs}")
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            # GitHub APIはワークフロートリガー時に実行IDを直接返さないため、
            # 最新の実行を取得して推定する
            time.sleep(2)  # APIの遅延を考慮
            runs = self.list_workflow_runs(workflow_id, limit=1)
            
            if runs:
                run_id = runs[0].id
                logger.info(f"Workflow triggered successfully. Run ID: {run_id}")
                return run_id
            else:
                raise GitHubAPIError("ワークフロー実行IDを取得できませんでした")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to trigger workflow: {e}")
            raise GitHubAPIError(f"ワークフローのトリガーに失敗しました: {e}")
    
    def get_workflow_run(self, run_id: int) -> WorkflowRun:
        """
        ワークフロー実行情報を取得
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            ワークフロー実行情報
        """
        url = f"{self.repo_url}/actions/runs/{run_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            return WorkflowRun(
                id=data["id"],
                name=data["name"],
                status=data["status"],
                conclusion=data["conclusion"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                html_url=data["html_url"],
                head_sha=data["head_sha"],
                head_branch=data["head_branch"],
                workflow_id=data["workflow_id"],
                run_number=data["run_number"]
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workflow run {run_id}: {e}")
            raise GitHubAPIError(f"ワークフロー実行情報の取得に失敗しました: {e}")
    
    def list_workflow_runs(self, workflow_id: str, status: Optional[str] = None,
                          branch: Optional[str] = None, limit: int = 30) -> List[WorkflowRun]:
        """
        ワークフロー実行一覧を取得
        
        Args:
            workflow_id: ワークフローID
            status: フィルタするステータス
            branch: フィルタするブランチ
            limit: 取得件数制限
            
        Returns:
            ワークフロー実行一覧
        """
        url = f"{self.repo_url}/actions/workflows/{workflow_id}/runs"
        
        params = {"per_page": min(limit, 100)}
        if status:
            params["status"] = status
        if branch:
            params["branch"] = branch
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            runs = []
            for run_data in data["workflow_runs"][:limit]:
                runs.append(WorkflowRun(
                    id=run_data["id"],
                    name=run_data["name"],
                    status=run_data["status"],
                    conclusion=run_data["conclusion"],
                    created_at=datetime.fromisoformat(run_data["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(run_data["updated_at"].replace("Z", "+00:00")),
                    html_url=run_data["html_url"],
                    head_sha=run_data["head_sha"],
                    head_branch=run_data["head_branch"],
                    workflow_id=run_data["workflow_id"],
                    run_number=run_data["run_number"]
                ))
            
            return runs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list workflow runs: {e}")
            raise GitHubAPIError(f"ワークフロー実行一覧の取得に失敗しました: {e}")
    
    def get_workflow_jobs(self, run_id: int) -> List[WorkflowJob]:
        """
        ワークフロージョブ一覧を取得
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            ワークフロージョブ一覧
        """
        url = f"{self.repo_url}/actions/runs/{run_id}/jobs"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job_data in data["jobs"]:
                started_at = None
                completed_at = None
                
                if job_data["started_at"]:
                    started_at = datetime.fromisoformat(job_data["started_at"].replace("Z", "+00:00"))
                if job_data["completed_at"]:
                    completed_at = datetime.fromisoformat(job_data["completed_at"].replace("Z", "+00:00"))
                
                jobs.append(WorkflowJob(
                    id=job_data["id"],
                    name=job_data["name"],
                    status=job_data["status"],
                    conclusion=job_data["conclusion"],
                    started_at=started_at,
                    completed_at=completed_at,
                    html_url=job_data["html_url"],
                    steps=job_data["steps"]
                ))
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workflow jobs for run {run_id}: {e}")
            raise GitHubAPIError(f"ワークフロージョブ情報の取得に失敗しました: {e}")
    
    def cancel_workflow_run(self, run_id: int) -> bool:
        """
        ワークフロー実行をキャンセル
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            キャンセル成功フラグ
        """
        url = f"{self.repo_url}/actions/runs/{run_id}/cancel"
        
        try:
            response = self.session.post(url)
            response.raise_for_status()
            
            logger.info(f"Workflow run {run_id} cancelled successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to cancel workflow run {run_id}: {e}")
            raise GitHubAPIError(f"ワークフロー実行のキャンセルに失敗しました: {e}")
    
    def get_workflow_logs(self, run_id: int) -> bytes:
        """
        ワークフローログを取得
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            ログデータ（ZIP形式）
        """
        url = f"{self.repo_url}/actions/runs/{run_id}/logs"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info(f"Retrieved logs for workflow run {run_id}")
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workflow logs for run {run_id}: {e}")
            raise GitHubAPIError(f"ワークフローログの取得に失敗しました: {e}")
    
    def create_deployment_status(self, deployment_id: int, state: str, 
                               target_url: Optional[str] = None,
                               description: Optional[str] = None) -> bool:
        """
        デプロイメントステータスを作成
        
        Args:
            deployment_id: デプロイメントID
            state: ステータス（pending, success, error, failure）
            target_url: ターゲットURL
            description: 説明
            
        Returns:
            作成成功フラグ
        """
        url = f"{self.repo_url}/deployments/{deployment_id}/statuses"
        
        payload = {"state": state}
        if target_url:
            payload["target_url"] = target_url
        if description:
            payload["description"] = description
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Deployment status created: {state}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create deployment status: {e}")
            raise GitHubAPIError(f"デプロイメントステータスの作成に失敗しました: {e}")
    
    def validate_connection(self) -> bool:
        """
        GitHub API接続を検証
        
        Returns:
            接続成功フラグ
        """
        url = f"{self.repo_url}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info("GitHub API connection validated successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API connection validation failed: {e}")
            return False