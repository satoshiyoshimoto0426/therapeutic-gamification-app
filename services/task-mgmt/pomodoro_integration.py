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
    """Pomodoro?"""
    session_id: str
    uid: str
    task_id: str
    planned_duration: int = 25  # ?
    actual_duration: Optional[int] = None
    status: PomodoroSessionStatus = PomodoroSessionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    break_type: Optional[BreakType] = None
    break_duration: int = 5  # ?
    break_started_at: Optional[datetime] = None
    break_completed_at: Optional[datetime] = None
    focus_music_enabled: bool = False
    interruption_count: int = 0
    notes: str = ""


class WorkSession(BaseModel):
    """?60?"""
    uid: str
    start_time: datetime
    total_duration: int = 0  # ?
    pomodoro_sessions: List[str] = []  # session_ids
    break_suggestions_count: int = 0
    break_refusal_count: int = 0
    is_active: bool = True


class ADHDSupportMetrics(BaseModel):
    """ADHD支援"""
    uid: str
    total_pomodoro_sessions: int = 0
    successful_sessions: int = 0
    break_compliance_rate: float = 0.0
    average_focus_duration: float = 0.0
    usage_frequency_score: float = 0.0  # 0.0-1.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PomodoroIntegrationService:
    """Pomodoro?"""
    
    def __init__(self):
        # ?Firestoreを
        self.pomodoro_sessions: Dict[str, PomodoroSession] = {}
        self.work_sessions: Dict[str, WorkSession] = {}  # uid -> WorkSession
        self.adhd_metrics: Dict[str, ADHDSupportMetrics] = {}  # uid -> metrics
        
        # 設定
        self.WORK_SESSION_THRESHOLD = 60  # ?
        self.MANDATORY_BREAK_DURATION = 15  # ?
        self.SHORT_BREAK_DURATION = 5  # ?
        self.LONG_BREAK_DURATION = 15  # ?
        
    def generate_session_id(self, uid: str) -> str:
        """?IDを"""
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
        Pomodoro?
        
        Args:
            uid: ユーザーID
            task_id: タスクID
            duration: ?
            focus_music_enabled: ?
            
        Returns:
            PomodoroSession: ?
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
            
            # ?
            await self._update_work_session(uid, session_id)
            
            # 自動
            asyncio.create_task(self._auto_complete_session(session_id, duration))
            
            logger.info(f"Pomodoro session started: {session_id} for user {uid}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start Pomodoro session: {str(e)}")
            raise
    
    async def complete_pomodoro_session(
        self,
        session_id: str,
        actual_duration: Optional[int] = None,
        notes: str = ""
    ) -> PomodoroSession:
        """
        Pomodoro?
        
        Args:
            session_id: ?ID
            actual_duration: 実装
            notes: メイン
            
        Returns:
            PomodoroSession: ?
        """
        try:
            if session_id not in self.pomodoro_sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.pomodoro_sessions[session_id]
            
            if session.status != PomodoroSessionStatus.ACTIVE:
                raise ValueError(f"Session is not active: {session.status}")
            
            session.status = PomodoroSessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            session.actual_duration = actual_duration or session.planned_duration
            session.notes = notes
            
            # ADHD支援
            await self._update_adhd_metrics(session.uid, session)
            
            # ?
            break_suggestion = await self._suggest_break(session.uid, session)
            
            logger.info(f"Pomodoro session completed: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to complete Pomodoro session: {str(e)}")
            raise
    
    async def start_break(
        self,
        session_id: str,
        break_type: BreakType = BreakType.SHORT
    ) -> PomodoroSession:
        """
        ?
        
        Args:
            session_id: ?ID
            break_type: ?
            
        Returns:
            PomodoroSession: ?
        """
        try:
            if session_id not in self.pomodoro_sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.pomodoro_sessions[session_id]
            session.status = PomodoroSessionStatus.BREAK
            session.break_type = break_type
            session.break_started_at = datetime.utcnow()
            
            # ?
            break_durations = {
                BreakType.SHORT: self.SHORT_BREAK_DURATION,
                BreakType.LONG: self.LONG_BREAK_DURATION,
                BreakType.MANDATORY: self.MANDATORY_BREAK_DURATION
            }
            session.break_duration = break_durations.get(break_type, self.SHORT_BREAK_DURATION)
            
            # 自動
            asyncio.create_task(self._auto_complete_break(session_id, session.break_duration))
            
            logger.info(f"Break started for session: {session_id}, type: {break_type}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start break: {str(e)}")
            raise
    
    async def complete_break(self, session_id: str) -> PomodoroSession:
        """
        ?
        
        Args:
            session_id: ?ID
            
        Returns:
            PomodoroSession: ?
        """
        try:
            if session_id not in self.pomodoro_sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.pomodoro_sessions[session_id]
            
            if session.status != PomodoroSessionStatus.BREAK:
                raise ValueError(f"Session is not in break: {session.status}")
            
            session.break_completed_at = datetime.utcnow()
            session.status = PomodoroSessionStatus.COMPLETED
            
            logger.info(f"Break completed for session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to complete break: {str(e)}")
            raise
    
    async def cancel_session(self, session_id: str, reason: str = "") -> PomodoroSession:
        """
        ?
        
        Args:
            session_id: ?ID
            reason: ?
            
        Returns:
            PomodoroSession: ?
        """
        try:
            if session_id not in self.pomodoro_sessions:
                raise ValueError(f"Session not found: {session_id}")
            
            session = self.pomodoro_sessions[session_id]
            session.status = PomodoroSessionStatus.CANCELLED
            session.notes = f"Cancelled: {reason}" if reason else "Cancelled"
            
            logger.info(f"Session cancelled: {session_id}, reason: {reason}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to cancel session: {str(e)}")
            raise
    
    def calculate_adhd_assist_multiplier(self, uid: str) -> float:
        """
        ADHD支援
        
        Args:
            uid: ユーザーID
            
        Returns:
            float: ADHD支援1.0-1.3?
        """
        try:
            if uid not in self.adhd_metrics:
                return 1.0
            
            metrics = self.adhd_metrics[uid]
            
            # 基本
            base_multiplier = 1.0
            
            # 使用0.0-1.0 -> 1.0-1.2?
            frequency_bonus = metrics.usage_frequency_score * 0.2
            
            # 成0.0-1.0 -> 0.0-0.1?
            success_rate = (
                metrics.successful_sessions / metrics.total_pomodoro_sessions
                if metrics.total_pomodoro_sessions > 0 else 0.0
            )
            success_bonus = success_rate * 0.1
            
            # ?0.0-1.0 -> 0.0-0.1?
            compliance_bonus = metrics.break_compliance_rate * 0.1
            
            final_multiplier = base_multiplier + frequency_bonus + success_bonus + compliance_bonus
            
            # 1.0-1.3の
            return min(1.3, max(1.0, final_multiplier))
            
        except Exception as e:
            logger.error(f"Failed to calculate ADHD assist multiplier: {str(e)}")
            return 1.0
    
    async def check_continuous_work_time(self, uid: str) -> Dict[str, any]:
        """
        ?60?
        
        Args:
            uid: ユーザーID
            
        Returns:
            Dict: ?
        """
        try:
            if uid not in self.work_sessions:
                return {
                    "continuous_minutes": 0,
                    "needs_break": False,
                    "break_suggestion": None
                }
            
            work_session = self.work_sessions[uid]
            
            if not work_session.is_active:
                return {
                    "continuous_minutes": 0,
                    "needs_break": False,
                    "break_suggestion": None
                }
            
            # ?
            current_time = datetime.utcnow()
            continuous_minutes = int((current_time - work_session.start_time).total_seconds() / 60)
            
            # 60?
            if continuous_minutes >= self.WORK_SESSION_THRESHOLD:
                break_suggestion = await self._generate_break_suggestion(uid, work_session)
                
                return {
                    "continuous_minutes": continuous_minutes,
                    "needs_break": True,
                    "break_suggestion": break_suggestion,
                    "refusal_count": work_session.break_refusal_count
                }
            
            return {
                "continuous_minutes": continuous_minutes,
                "needs_break": False,
                "break_suggestion": None
            }
            
        except Exception as e:
            logger.error(f"Failed to check continuous work time: {str(e)}")
            return {
                "continuous_minutes": 0,
                "needs_break": False,
                "break_suggestion": None,
                "error": str(e)
            }
    
    async def handle_break_refusal(self, uid: str) -> Dict[str, any]:
        """
        ?3.2: 2?
        
        Args:
            uid: ユーザーID
            
        Returns:
            Dict: ?
        """
        try:
            if uid not in self.work_sessions:
                return {"error": "No active work session"}
            
            work_session = self.work_sessions[uid]
            work_session.break_refusal_count += 1
            
            if work_session.break_refusal_count >= 2:
                # ?
                mother_concern_message = self._generate_mother_concern_narrative(uid)
                
                return {
                    "refusal_count": work_session.break_refusal_count,
                    "show_mother_concern": True,
                    "narrative": mother_concern_message,
                    "mandatory_break_required": True
                }
            
            return {
                "refusal_count": work_session.break_refusal_count,
                "show_mother_concern": False,
                "narrative": None,
                "mandatory_break_required": False
            }
            
        except Exception as e:
            logger.error(f"Failed to handle break refusal: {str(e)}")
            return {"error": str(e)}
    
    async def get_user_pomodoro_statistics(self, uid: str, days: int = 30) -> Dict[str, any]:
        """
        ユーザーPomodoro?
        
        Args:
            uid: ユーザーID
            days: ?
            
        Returns:
            Dict: Pomodoro?
        """
        try:
            # ?
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            user_sessions = [
                session for session in self.pomodoro_sessions.values()
                if session.uid == uid and session.started_at and session.started_at >= cutoff_date
            ]
            
            total_sessions = len(user_sessions)
            completed_sessions = len([s for s in user_sessions if s.status == PomodoroSessionStatus.COMPLETED])
            cancelled_sessions = len([s for s in user_sessions if s.status == PomodoroSessionStatus.CANCELLED])
            
            # ?
            completed_durations = [
                s.actual_duration or s.planned_duration 
                for s in user_sessions 
                if s.status == PomodoroSessionStatus.COMPLETED
            ]
            avg_focus_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
            
            # ADHD支援
            adhd_metrics = self.adhd_metrics.get(uid, ADHDSupportMetrics(uid=uid))
            
            return {
                "period_days": days,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "cancelled_sessions": cancelled_sessions,
                "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
                "average_focus_duration": avg_focus_duration,
                "adhd_assist_multiplier": self.calculate_adhd_assist_multiplier(uid),
                "usage_frequency_score": adhd_metrics.usage_frequency_score,
                "break_compliance_rate": adhd_metrics.break_compliance_rate,
                "total_focus_time": sum(completed_durations)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pomodoro statistics: {str(e)}")
            return {"error": str(e)}
    
    # プレビュー
    
    async def _auto_complete_session(self, session_id: str, duration_minutes: int):
        """?"""
        try:
            await asyncio.sleep(duration_minutes * 60)  # ?
            
            if session_id in self.pomodoro_sessions:
                session = self.pomodoro_sessions[session_id]
                if session.status == PomodoroSessionStatus.ACTIVE:
                    await self.complete_pomodoro_session(session_id)
                    
        except Exception as e:
            logger.error(f"Auto-complete session failed: {str(e)}")
    
    async def _auto_complete_break(self, session_id: str, duration_minutes: int):
        """?"""
        try:
            await asyncio.sleep(duration_minutes * 60)  # ?
            
            if session_id in self.pomodoro_sessions:
                session = self.pomodoro_sessions[session_id]
                if session.status == PomodoroSessionStatus.BREAK:
                    await self.complete_break(session_id)
                    
        except Exception as e:
            logger.error(f"Auto-complete break failed: {str(e)}")
    
    async def _update_work_session(self, uid: str, session_id: str):
        """?"""
        try:
            current_time = datetime.utcnow()
            
            if uid not in self.work_sessions:
                # ?
                self.work_sessions[uid] = WorkSession(
                    uid=uid,
                    start_time=current_time,
                    pomodoro_sessions=[session_id]
                )
            else:
                work_session = self.work_sessions[uid]
                
                # ?30?
                if work_session.pomodoro_sessions:
                    last_session_id = work_session.pomodoro_sessions[-1]
                    if last_session_id in self.pomodoro_sessions:
                        last_session = self.pomodoro_sessions[last_session_id]
                        if last_session.completed_at:
                            time_gap = current_time - last_session.completed_at
                            if time_gap.total_seconds() > 1800:  # 30?
                                # ?
                                self.work_sessions[uid] = WorkSession(
                                    uid=uid,
                                    start_time=current_time,
                                    pomodoro_sessions=[session_id]
                                )
                                return
                
                # ?
                work_session.pomodoro_sessions.append(session_id)
                
        except Exception as e:
            logger.error(f"Failed to update work session: {str(e)}")
    
    async def _update_adhd_metrics(self, uid: str, session: PomodoroSession):
        """ADHD支援"""
        try:
            if uid not in self.adhd_metrics:
                self.adhd_metrics[uid] = ADHDSupportMetrics(uid=uid)
            
            metrics = self.adhd_metrics[uid]
            metrics.total_pomodoro_sessions += 1
            
            if session.status == PomodoroSessionStatus.COMPLETED:
                metrics.successful_sessions += 1
            
            # 使用30?
            days_since_start = max(1, (datetime.utcnow() - metrics.last_updated).days)
            daily_usage = metrics.total_pomodoro_sessions / days_since_start
            metrics.usage_frequency_score = min(1.0, daily_usage / 5.0)  # 1?5?
            
            # ?
            if metrics.successful_sessions > 0:
                # ?
                current_duration = session.actual_duration or session.planned_duration
                metrics.average_focus_duration = (
                    (metrics.average_focus_duration * (metrics.successful_sessions - 1) + current_duration) /
                    metrics.successful_sessions
                )
            
            metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update ADHD metrics: {str(e)}")
    
    async def _suggest_break(self, uid: str, session: PomodoroSession) -> Optional[Dict[str, any]]:
        """?"""
        try:
            # ?
            work_check = await self.check_continuous_work_time(uid)
            
            if work_check.get("needs_break", False):
                return {
                    "type": "mandatory",
                    "message": "60?",
                    "duration": self.MANDATORY_BREAK_DURATION,
                    "continuous_minutes": work_check.get("continuous_minutes", 0)
                }
            
            # ?
            return {
                "type": "normal",
                "message": "お",
                "duration": self.SHORT_BREAK_DURATION,
                "continuous_minutes": work_check.get("continuous_minutes", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to suggest break: {str(e)}")
            return None
    
    async def _generate_break_suggestion(self, uid: str, work_session: WorkSession) -> Dict[str, any]:
        """?"""
        try:
            continuous_minutes = int((datetime.utcnow() - work_session.start_time).total_seconds() / 60)
            
            if work_session.break_refusal_count >= 2:
                return {
                    "type": "mother_concern",
                    "title": "お",
                    "message": self._generate_mother_concern_narrative(uid),
                    "duration": self.MANDATORY_BREAK_DURATION,
                    "is_mandatory": True
                }
            elif work_session.break_refusal_count == 1:
                return {
                    "type": "gentle_reminder",
                    "title": "?",
                    "message": f"も{continuous_minutes}?",
                    "duration": self.LONG_BREAK_DURATION,
                    "is_mandatory": False
                }
            else:
                return {
                    "type": "first_suggestion",
                    "title": "?",
                    "message": f"{continuous_minutes}?",
                    "duration": self.SHORT_BREAK_DURATION,
                    "is_mandatory": False
                }
                
        except Exception as e:
            logger.error(f"Failed to generate break suggestion: {str(e)}")
            return {
                "type": "error",
                "message": "?",
                "duration": self.SHORT_BREAK_DURATION,
                "is_mandatory": False
            }
    
    def _generate_mother_concern_narrative(self, uid: str) -> str:
        """?"""
        narratives = [
            "あ",
            "お",
            "お"
        ]
        
        import random
        return random.choice(narratives)


# ?
pomodoro_service = PomodoroIntegrationService()