"""
Pomodoro統合とADHD支援機能

Pomodoro統合とADHD支援機能（60分連続作業時の自動休憩提案）
Requirements: 3.2, 5.3
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import asyncio
import logging

logger = logging.getLogger(__name__)


class PomodoroSessionStatus(str, Enum):
    """Pomodoroセッション状態"""
    PENDING = "pending"      # 待機中
    ACTIVE = "active"        # 実行中
    BREAK = "break"          # 休憩中
    COMPLETED = "completed"  # 完了
    CANCELLED = "cancelled"  # キャンセル


class BreakType(str, Enum):
    """休憩タイプ"""
    SHORT = "short"          # 短い休憩（5分）
    LONG = "long"            # 長い休憩（15分）
    MANDATORY = "mandatory"  # 強制休憩（60分連続作業後）


class PomodoroSession(BaseModel):
    """Pomodoroセッション"""
    session_id: str
    uid: str
    task_id: str
    planned_duration: int = 25  # 予定時間（分）
    actual_duration: Optional[int] = None
    status: PomodoroSessionStatus = PomodoroSessionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    break_type: Optional[BreakType] = None
    break_duration: int = 5  # 休憩時間（分）
    break_started_at: Optional[datetime] = None
    break_completed_at: Optional[datetime] = None
    focus_music_enabled: bool = False
    interruption_count: int = 0
    notes: str = ""


class WorkSession(BaseModel):
    """作業セッション（60分連続作業チェック用）"""
    uid: str
    start_time: datetime
    total_duration: int = 0  # 総作業時間（分）
    pomodoro_sessions: List[str] = []  # session_ids
    break_suggestions_count: int = 0
    break_refusal_count: int = 0
    is_active: bool = True


class ADHDSupportMetrics(BaseModel):
    """ADHD支援メトリクス"""
    uid: str
    total_pomodoro_sessions: int = 0
    successful_sessions: int = 0
    break_compliance_rate: float = 0.0
    average_focus_duration: float = 0.0
    usage_frequency_score: float = 0.0  # 0.0-1.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PomodoroIntegrationService:
    """Pomodoro統合サービス"""
    
    def __init__(self):
        # 実際の実装ではFirestoreを使用
        self.pomodoro_sessions: Dict[str, PomodoroSession] = {}
        self.work_sessions: Dict[str, WorkSession] = {}  # uid -> WorkSession
        self.adhd_metrics: Dict[str, ADHDSupportMetrics] = {}  # uid -> metrics
        
        # 設定値
        self.WORK_SESSION_THRESHOLD = 60  # 連続作業時間閾値（分）
        self.MANDATORY_BREAK_DURATION = 15  # 強制休憩時間（分）
        self.SHORT_BREAK_DURATION = 5  # 短い休憩時間（分）
        self.LONG_BREAK_DURATION = 15  # 長い休憩時間（分）
        
    def generate_session_id(self, uid: str) -> str:
        """セッションIDを生成"""
        import uuid
        return f"pomodoro_{uid}_{uuid.uuid4().hex[:8]}"
    
    async def start_pomodoro_session(
        self,
        uid: str,
        task_id: str,
        duration: int = 25,
        focus_music_enabled: bool = False
    ) -> PomodoroSession:
        """
        Pomodoroセッション開始
        
        Args:
            uid: ユーザーID
            task_id: タスクID
            duration: セッション時間（分）
            focus_music_enabled: 集中音楽有効
            
        Returns:
            PomodoroSession: 開始されたセッション
        """
        try:
            session_id = self.generate_session_id(uid)
            
            session = PomodoroSession(
                session_id=session_id,
                uid=uid,
                task_id=task_id,
                planned_duration=duration,
                status=PomodoroSessionStatus.ACTIVE,
                started_at=datetime.utcnow(),
                focus_music_enabled=focus_music_enabled
            )
            
            self.pomodoro_sessions[session_id] = session
            
            # 作業セッション更新
            await self._update_work_session(uid, session_id)
            
            # 自動完了タスク
            asyncio.create_task(self._auto_complete_session(session_id, duration))
            
            logger.info(f"Pomodoro session started: {session_id} for user {uid}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start Pomodoro session: {str(e)}")
            raise
    
    def calculate_adhd_assist_multiplier(self, uid: str) -> float:
        """
        ADHD支援係数計算
        
        Args:
            uid: ユーザーID
            
        Returns:
            float: ADHD支援係数（1.0-1.3の範囲）
        """
        try:
            if uid not in self.adhd_metrics:
                return 1.0
            
            metrics = self.adhd_metrics[uid]
            
            # 基本係数
            base_multiplier = 1.0
            
            # 使用頻度ボーナス（0.0-1.0 -> 1.0-1.2の範囲）
            frequency_bonus = metrics.usage_frequency_score * 0.2
            
            # 成功率ボーナス（0.0-1.0 -> 0.0-0.1の範囲）
            success_rate = (
                metrics.successful_sessions / metrics.total_pomodoro_sessions
                if metrics.total_pomodoro_sessions > 0 else 0.0
            )
            success_bonus = success_rate * 0.1
            
            # 休憩遵守率ボーナス（0.0-1.0 -> 0.0-0.1の範囲）
            compliance_bonus = metrics.break_compliance_rate * 0.1
            
            final_multiplier = base_multiplier + frequency_bonus + success_bonus + compliance_bonus
            
            # 1.0-1.3の範囲に制限
            return min(1.3, max(1.0, final_multiplier))
            
        except Exception as e:
            logger.error(f"Failed to calculate ADHD assist multiplier: {str(e)}")
            return 1.0
    
    async def get_user_pomodoro_statistics(self, uid: str, days: int = 30) -> Dict[str, any]:
        """
        ユーザーのPomodoro統計取得
        
        Args:
            uid: ユーザーID
            days: 統計期間（日）
            
        Returns:
            Dict: Pomodoro統計情報
        """
        try:
            # 期間フィルタ
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            user_sessions = [
                session for session in self.pomodoro_sessions.values()
                if session.uid == uid and session.started_at and session.started_at >= cutoff_date
            ]
            
            total_sessions = len(user_sessions)
            completed_sessions = len([s for s in user_sessions if s.status == PomodoroSessionStatus.COMPLETED])
            
            # ADHD支援メトリクス
            adhd_metrics = self.adhd_metrics.get(uid, ADHDSupportMetrics(uid=uid))
            
            return {
                "period_days": days,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
                "adhd_assist_multiplier": self.calculate_adhd_assist_multiplier(uid),
                "usage_frequency_score": adhd_metrics.usage_frequency_score,
                "break_compliance_rate": adhd_metrics.break_compliance_rate
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pomodoro statistics: {str(e)}")
            return {"error": str(e)}
    
    # プライベートメソッド
    
    async def _update_work_session(self, uid: str, session_id: str):
        """作業セッション更新"""
        try:
            current_time = datetime.utcnow()
            
            if uid not in self.work_sessions:
                # 新規作業セッション
                self.work_sessions[uid] = WorkSession(
                    uid=uid,
                    start_time=current_time,
                    pomodoro_sessions=[session_id]
                )
            else:
                work_session = self.work_sessions[uid]
                work_session.pomodoro_sessions.append(session_id)
                
        except Exception as e:
            logger.error(f"Failed to update work session: {str(e)}")
    
    async def _auto_complete_session(self, session_id: str, duration_minutes: int):
        """自動セッション完了"""
        try:
            await asyncio.sleep(duration_minutes * 60)  # 分を秒に変換
            
            if session_id in self.pomodoro_sessions:
                session = self.pomodoro_sessions[session_id]
                if session.status == PomodoroSessionStatus.ACTIVE:
                    session.status = PomodoroSessionStatus.COMPLETED
                    session.completed_at = datetime.utcnow()
                    session.actual_duration = duration_minutes
                    
        except Exception as e:
            logger.error(f"Auto-complete session failed: {str(e)}")


# グローバルサービスインスタンス
pomodoro_service = PomodoroIntegrationService()