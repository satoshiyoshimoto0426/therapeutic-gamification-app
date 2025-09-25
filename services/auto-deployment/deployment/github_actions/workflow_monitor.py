"""
GitHub Actions ワークフロー監視システム

ワークフローの実行状況を監視し、リアルタイムでステータスを追跡します。
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .github_client import GitHubClient, WorkflowRun, WorkflowJob
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

try:
    from services.auto_deployment.config import DeploymentConfig
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


class MonitoringStatus(Enum):
    """監視ステータス"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MonitoringEvent:
    """監視イベント"""
    timestamp: datetime
    run_id: int
    event_type: str  # status_change, job_completed, step_failed, etc.
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    job_name: Optional[str] = None
    step_name: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringSession:
    """監視セッション"""
    run_id: int
    workflow_name: str
    started_at: datetime
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    events: List[MonitoringEvent] = field(default_factory=list)
    last_check: Optional[datetime] = None
    error_count: int = 0
    callbacks: List[Callable] = field(default_factory=list)


class WorkflowMonitor:
    """ワークフロー監視"""
    
    def __init__(self, config: DeploymentConfig, github_client: Optional[GitHubClient] = None):
        """
        初期化
        
        Args:
            config: デプロイメント設定
            github_client: GitHubクライアント（省略時は自動作成）
        """
        self.config = config
        self.github_client = github_client or GitHubClient()
        
        # 監視セッション管理
        self.sessions: Dict[int, MonitoringSession] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.monitoring_interval = 30  # 30秒間隔
        
        # イベントコールバック
        self.global_callbacks: List[Callable] = []
        
        logger.info("WorkflowMonitor initialized")
    
    def start_monitoring(self, run_id: int, 
                        callbacks: Optional[List[Callable]] = None) -> MonitoringSession:
        """
        ワークフロー監視を開始
        
        Args:
            run_id: ワークフロー実行ID
            callbacks: イベントコールバック関数のリスト
            
        Returns:
            監視セッション
        """
        logger.info(f"Starting monitoring for workflow run: {run_id}")
        
        try:
            # ワークフロー情報を取得
            workflow_run = self.github_client.get_workflow_run(run_id)
            
            # 監視セッションを作成
            session = MonitoringSession(
                run_id=run_id,
                workflow_name=workflow_run.name,
                started_at=datetime.now(),
                callbacks=callbacks or []
            )
            
            self.sessions[run_id] = session
            
            # 監視スレッドを開始（まだ開始していない場合）
            if not self.monitoring_active:
                self._start_monitoring_thread()
            
            # 初期イベントを記録
            initial_event = MonitoringEvent(
                timestamp=datetime.now(),
                run_id=run_id,
                event_type="monitoring_started",
                new_status=workflow_run.status,
                message=f"Monitoring started for {workflow_run.name}"
            )
            
            session.events.append(initial_event)
            self._trigger_callbacks(session, initial_event)
            
            logger.info(f"Monitoring started for run {run_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start monitoring for run {run_id}: {e}")
            raise DeploymentError(f"監視の開始に失敗しました: {e}")
    
    def stop_monitoring(self, run_id: int) -> bool:
        """
        ワークフロー監視を停止
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            停止成功フラグ
        """
        if run_id not in self.sessions:
            logger.warning(f"No monitoring session found for run {run_id}")
            return False
        
        session = self.sessions[run_id]
        session.status = MonitoringStatus.STOPPED
        
        # 停止イベントを記録
        stop_event = MonitoringEvent(
            timestamp=datetime.now(),
            run_id=run_id,
            event_type="monitoring_stopped",
            message="Monitoring stopped by user request"
        )
        
        session.events.append(stop_event)
        self._trigger_callbacks(session, stop_event)
        
        logger.info(f"Monitoring stopped for run {run_id}")
        return True
    
    def get_monitoring_status(self, run_id: int) -> Optional[MonitoringSession]:
        """
        監視ステータスを取得
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            監視セッション（存在しない場合はNone）
        """
        return self.sessions.get(run_id)
    
    def get_workflow_progress(self, run_id: int) -> Dict[str, Any]:
        """
        ワークフロー進捗情報を取得
        
        Args:
            run_id: ワークフロー実行ID
            
        Returns:
            進捗情報
        """
        try:
            workflow_run = self.github_client.get_workflow_run(run_id)
            jobs = self.github_client.get_workflow_jobs(run_id)
            
            # ジョブ進捗を計算
            total_jobs = len(jobs)
            completed_jobs = sum(1 for job in jobs if job.status == "completed")
            
            # ステップ進捗を計算
            total_steps = sum(len(job.steps) for job in jobs)
            completed_steps = sum(
                sum(1 for step in job.steps if step.get("conclusion") in ["success", "failure", "skipped"])
                for job in jobs
            )
            
            progress = {
                "run_id": run_id,
                "workflow_name": workflow_run.name,
                "status": workflow_run.status,
                "conclusion": workflow_run.conclusion,
                "created_at": workflow_run.created_at.isoformat(),
                "updated_at": workflow_run.updated_at.isoformat(),
                "html_url": workflow_run.html_url,
                "progress": {
                    "jobs": {
                        "total": total_jobs,
                        "completed": completed_jobs,
                        "percentage": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
                    },
                    "steps": {
                        "total": total_steps,
                        "completed": completed_steps,
                        "percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
                    }
                },
                "jobs": []
            }
            
            # ジョブ詳細を追加
            for job in jobs:
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "conclusion": job.conclusion,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "html_url": job.html_url,
                    "steps": []
                }
                
                # ステップ詳細を追加
                for step in job.steps:
                    step_info = {
                        "name": step.get("name"),
                        "status": step.get("status"),
                        "conclusion": step.get("conclusion"),
                        "number": step.get("number"),
                        "started_at": step.get("started_at"),
                        "completed_at": step.get("completed_at")
                    }
                    job_info["steps"].append(step_info)
                
                progress["jobs"].append(job_info)
            
            return progress
            
        except Exception as e:
            logger.error(f"Failed to get workflow progress for run {run_id}: {e}")
            raise DeploymentError(f"ワークフロー進捗の取得に失敗しました: {e}")
    
    def wait_for_completion(self, run_id: int, timeout_minutes: int = 30,
                          progress_callback: Optional[Callable] = None) -> WorkflowRun:
        """
        ワークフロー完了まで待機
        
        Args:
            run_id: ワークフロー実行ID
            timeout_minutes: タイムアウト時間（分）
            progress_callback: 進捗コールバック関数
            
        Returns:
            完了したワークフロー実行情報
        """
        logger.info(f"Waiting for workflow completion: {run_id} (timeout: {timeout_minutes}m)")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_status = None
        
        while time.time() - start_time < timeout_seconds:
            try:
                workflow_run = self.github_client.get_workflow_run(run_id)
                
                # ステータス変更を検出
                if workflow_run.status != last_status:
                    logger.info(f"Workflow status changed: {last_status} -> {workflow_run.status}")
                    last_status = workflow_run.status
                    
                    # 進捗コールバックを呼び出し
                    if progress_callback:
                        try:
                            progress = self.get_workflow_progress(run_id)
                            progress_callback(progress)
                        except Exception as e:
                            logger.warning(f"Progress callback failed: {e}")
                
                # 完了チェック
                if workflow_run.status == "completed":
                    logger.info(f"Workflow completed with conclusion: {workflow_run.conclusion}")
                    return workflow_run
                
                # 待機
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error while waiting for workflow completion: {e}")
                time.sleep(60)  # エラー時は長めに待機
        
        # タイムアウト
        logger.warning(f"Workflow wait timeout after {timeout_minutes} minutes")
        raise DeploymentError(f"ワークフロー完了の待機がタイムアウトしました（{timeout_minutes}分）")
    
    def add_global_callback(self, callback: Callable) -> None:
        """
        グローバルイベントコールバックを追加
        
        Args:
            callback: コールバック関数
        """
        self.global_callbacks.append(callback)
        logger.info("Global callback added")
    
    def remove_global_callback(self, callback: Callable) -> bool:
        """
        グローバルイベントコールバックを削除
        
        Args:
            callback: コールバック関数
            
        Returns:
            削除成功フラグ
        """
        if callback in self.global_callbacks:
            self.global_callbacks.remove(callback)
            logger.info("Global callback removed")
            return True
        return False
    
    def _start_monitoring_thread(self) -> None:
        """監視スレッドを開始"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Monitoring thread started")
    
    def _monitoring_loop(self) -> None:
        """監視ループ"""
        logger.info("Monitoring loop started")
        
        while self.monitoring_active:
            try:
                # アクティブなセッションを監視
                active_sessions = [
                    session for session in self.sessions.values()
                    if session.status == MonitoringStatus.ACTIVE
                ]
                
                if not active_sessions:
                    time.sleep(self.monitoring_interval)
                    continue
                
                for session in active_sessions:
                    try:
                        self._check_workflow_status(session)
                    except Exception as e:
                        logger.error(f"Error checking workflow {session.run_id}: {e}")
                        session.error_count += 1
                        
                        # エラーが多い場合は監視を一時停止
                        if session.error_count >= 5:
                            session.status = MonitoringStatus.ERROR
                            error_event = MonitoringEvent(
                                timestamp=datetime.now(),
                                run_id=session.run_id,
                                event_type="monitoring_error",
                                message=f"Too many errors, monitoring paused: {e}"
                            )
                            session.events.append(error_event)
                            self._trigger_callbacks(session, error_event)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # エラー時は長めに待機
        
        logger.info("Monitoring loop stopped")
    
    def _check_workflow_status(self, session: MonitoringSession) -> None:
        """ワークフローステータスをチェック"""
        workflow_run = self.github_client.get_workflow_run(session.run_id)
        session.last_check = datetime.now()
        
        # 最新イベントのステータスと比較
        last_event = session.events[-1] if session.events else None
        current_status = workflow_run.status
        
        # ステータス変更を検出
        if not last_event or last_event.new_status != current_status:
            status_event = MonitoringEvent(
                timestamp=datetime.now(),
                run_id=session.run_id,
                event_type="status_change",
                old_status=last_event.new_status if last_event else None,
                new_status=current_status,
                message=f"Status changed to {current_status}"
            )
            
            session.events.append(status_event)
            self._trigger_callbacks(session, status_event)
        
        # 完了チェック
        if workflow_run.status == "completed":
            completion_event = MonitoringEvent(
                timestamp=datetime.now(),
                run_id=session.run_id,
                event_type="workflow_completed",
                new_status=workflow_run.status,
                message=f"Workflow completed with conclusion: {workflow_run.conclusion}",
                metadata={"conclusion": workflow_run.conclusion}
            )
            
            session.events.append(completion_event)
            session.status = MonitoringStatus.STOPPED
            self._trigger_callbacks(session, completion_event)
        
        # ジョブレベルの監視
        self._check_job_status(session)
    
    def _check_job_status(self, session: MonitoringSession) -> None:
        """ジョブステータスをチェック"""
        try:
            jobs = self.github_client.get_workflow_jobs(session.run_id)
            
            for job in jobs:
                # ジョブ完了イベント
                if job.status == "completed" and job.conclusion:
                    # 既に記録済みかチェック
                    job_completed_events = [
                        e for e in session.events
                        if e.event_type == "job_completed" and e.job_name == job.name
                    ]
                    
                    if not job_completed_events:
                        job_event = MonitoringEvent(
                            timestamp=datetime.now(),
                            run_id=session.run_id,
                            event_type="job_completed",
                            job_name=job.name,
                            new_status=job.conclusion,
                            message=f"Job '{job.name}' completed with conclusion: {job.conclusion}",
                            metadata={
                                "job_id": job.id,
                                "conclusion": job.conclusion,
                                "html_url": job.html_url
                            }
                        )
                        
                        session.events.append(job_event)
                        self._trigger_callbacks(session, job_event)
                
                # 失敗したステップの検出
                for step in job.steps:
                    if step.get("conclusion") == "failure":
                        step_failed_events = [
                            e for e in session.events
                            if (e.event_type == "step_failed" and 
                                e.job_name == job.name and 
                                e.step_name == step.get("name"))
                        ]
                        
                        if not step_failed_events:
                            step_event = MonitoringEvent(
                                timestamp=datetime.now(),
                                run_id=session.run_id,
                                event_type="step_failed",
                                job_name=job.name,
                                step_name=step.get("name"),
                                message=f"Step '{step.get('name')}' failed in job '{job.name}'",
                                metadata={
                                    "step_number": step.get("number"),
                                    "step_conclusion": step.get("conclusion")
                                }
                            )
                            
                            session.events.append(step_event)
                            self._trigger_callbacks(session, step_event)
        
        except Exception as e:
            logger.warning(f"Failed to check job status: {e}")
    
    def _trigger_callbacks(self, session: MonitoringSession, event: MonitoringEvent) -> None:
        """イベントコールバックを実行"""
        # セッション固有のコールバック
        for callback in session.callbacks:
            try:
                callback(session, event)
            except Exception as e:
                logger.error(f"Session callback failed: {e}")
        
        # グローバルコールバック
        for callback in self.global_callbacks:
            try:
                callback(session, event)
            except Exception as e:
                logger.error(f"Global callback failed: {e}")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        古い監視セッションをクリーンアップ
        
        Args:
            max_age_hours: 保持時間（時間）
            
        Returns:
            削除されたセッション数
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_sessions = [
            run_id for run_id, session in self.sessions.items()
            if session.started_at < cutoff_time and session.status == MonitoringStatus.STOPPED
        ]
        
        for run_id in old_sessions:
            del self.sessions[run_id]
        
        logger.info(f"Cleaned up {len(old_sessions)} old monitoring sessions")
        return len(old_sessions)
    
    def stop_all_monitoring(self) -> None:
        """全ての監視を停止"""
        self.monitoring_active = False
        
        for session in self.sessions.values():
            if session.status == MonitoringStatus.ACTIVE:
                session.status = MonitoringStatus.STOPPED
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        logger.info("All monitoring stopped")