"""
Task System Interface

タスク管理システムのインターフェース定義
Requirements: 5.1, 5.5
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from .core_types import TaskType, TaskStatus, CrystalAttribute


class TaskDifficulty(int, Enum):
    """タスク難易度"""
    VERY_EASY = 1    # とても簡単
    EASY = 2         # 簡単
    MEDIUM = 3       # 普通
    HARD = 4         # 難しい
    VERY_HARD = 5    # とても難しい


class TaskPriority(str, Enum):
    """タスク優先度"""
    LOW = "low"         # 低
    MEDIUM = "medium"   # 中
    HIGH = "high"       # 高
    URGENT = "urgent"   # 緊急


class ADHDSupportLevel(str, Enum):
    """ADHD支援レベル"""
    NONE = "none"           # なし
    BASIC = "basic"         # 基本
    MODERATE = "moderate"   # 中程度
    INTENSIVE = "intensive" # 集中的


class XPCalculationResult(BaseModel):
    """XP計算結果"""
    base_xp: int
    mood_coefficient: float
    adhd_assist_multiplier: float
    time_efficiency_bonus: float = 0.0
    priority_bonus: float = 0.0
    final_xp: int
    breakdown: Dict[str, Any] = {}


class Task(BaseModel):
    """タスクエンティティ"""
    task_id: str
    uid: str
    task_type: TaskType
    title: str
    description: str = ""
    difficulty: TaskDifficulty
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: int = 30  # 分
    actual_duration: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    base_xp: int = 0
    xp_earned: int = 0
    mood_at_completion: Optional[int] = None
    adhd_support_level: ADHDSupportLevel = ADHDSupportLevel.NONE
    pomodoro_sessions_planned: int = 1
    pomodoro_sessions_completed: int = 0
    break_reminders_enabled: bool = True
    focus_music_enabled: bool = False
    linked_story_edge: Optional[str] = None
    habit_tag: Optional[str] = None
    mandala_cell_id: Optional[str] = None
    primary_crystal_attribute: Optional[CrystalAttribute] = None
    secondary_crystal_attributes: List[CrystalAttribute] = []
    tags: List[str] = []
    notes: str = ""
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.base_xp == 0:
            self.base_xp = self._calculate_base_xp()
    
    def _calculate_base_xp(self) -> int:
        """基本XP計算"""
        base_values = {
            TaskDifficulty.VERY_EASY: 5,
            TaskDifficulty.EASY: 10,
            TaskDifficulty.MEDIUM: 15,
            TaskDifficulty.HARD: 25,
            TaskDifficulty.VERY_HARD: 40
        }
        return base_values.get(self.difficulty, 15)
    
    def start_task(self):
        """タスク開始"""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
    
    def complete_task(
        self, 
        mood_score: int, 
        actual_duration: Optional[int] = None,
        notes: str = "",
        adhd_assist_multiplier: float = 1.0
    ) -> int:
        """タスク完了"""
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError("Task is not in progress")
        
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.mood_at_completion = mood_score
        self.actual_duration = actual_duration
        self.notes = notes
        
        # XP計算
        mood_coefficient = 0.8 + (mood_score - 1) * 0.1  # 0.8-1.2
        self.xp_earned = int(self.base_xp * mood_coefficient * adhd_assist_multiplier)
        
        return self.xp_earned
    
    def is_overdue(self) -> bool:
        """期限切れチェック"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != TaskStatus.COMPLETED
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """残り時間取得"""
        if not self.due_date:
            return None
        remaining = self.due_date - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def get_crystal_growth_events(self) -> List[Tuple[CrystalAttribute, str]]:
        """クリスタル成長イベント取得"""
        events = []
        if self.primary_crystal_attribute:
            events.append((self.primary_crystal_attribute, "task_completion"))
        for attr in self.secondary_crystal_attributes:
            events.append((attr, "task_completion"))
        return events


class TaskXPCalculator:
    """タスクXP計算機"""
    
    @staticmethod
    def get_xp_preview(
        task_type: TaskType,
        difficulty: TaskDifficulty,
        mood_score: int,
        adhd_support_level: ADHDSupportLevel
    ) -> int:
        """XPプレビュー計算"""
        base_values = {
            TaskDifficulty.VERY_EASY: 5,
            TaskDifficulty.EASY: 10,
            TaskDifficulty.MEDIUM: 15,
            TaskDifficulty.HARD: 25,
            TaskDifficulty.VERY_HARD: 40
        }
        
        base_xp = base_values.get(difficulty, 15)
        mood_coefficient = 0.8 + (mood_score - 1) * 0.1
        
        adhd_multipliers = {
            ADHDSupportLevel.NONE: 1.0,
            ADHDSupportLevel.BASIC: 1.1,
            ADHDSupportLevel.MODERATE: 1.2,
            ADHDSupportLevel.INTENSIVE: 1.3
        }
        adhd_multiplier = adhd_multipliers.get(adhd_support_level, 1.0)
        
        return int(base_xp * mood_coefficient * adhd_multiplier)
    
    @staticmethod
    def calculate_detailed_xp(
        task: Task,
        mood_score: int,
        actual_duration: Optional[int] = None,
        adhd_assist_multiplier: float = 1.0
    ) -> XPCalculationResult:
        """詳細XP計算"""
        base_xp = task.base_xp
        mood_coefficient = 0.8 + (mood_score - 1) * 0.1
        
        # 時間効率ボーナス
        time_efficiency_bonus = 0.0
        if actual_duration and task.estimated_duration:
            if actual_duration <= task.estimated_duration:
                efficiency = task.estimated_duration / actual_duration
                time_efficiency_bonus = min(0.2, (efficiency - 1) * 0.1)
        
        # 優先度ボーナス
        priority_bonuses = {
            TaskPriority.LOW: 0.0,
            TaskPriority.MEDIUM: 0.05,
            TaskPriority.HIGH: 0.1,
            TaskPriority.URGENT: 0.15
        }
        priority_bonus = priority_bonuses.get(task.priority, 0.0)
        
        # 最終XP計算
        multiplier = mood_coefficient * adhd_assist_multiplier * (1 + time_efficiency_bonus + priority_bonus)
        final_xp = int(base_xp * multiplier)
        
        return XPCalculationResult(
            base_xp=base_xp,
            mood_coefficient=mood_coefficient,
            adhd_assist_multiplier=adhd_assist_multiplier,
            time_efficiency_bonus=time_efficiency_bonus,
            priority_bonus=priority_bonus,
            final_xp=final_xp,
            breakdown={
                "base": base_xp,
                "mood_adjustment": base_xp * (mood_coefficient - 1),
                "adhd_bonus": base_xp * mood_coefficient * (adhd_assist_multiplier - 1),
                "time_bonus": base_xp * mood_coefficient * adhd_assist_multiplier * time_efficiency_bonus,
                "priority_bonus": base_xp * mood_coefficient * adhd_assist_multiplier * priority_bonus
            }
        )


class TaskTypeRecommender:
    """タスクタイプ推奨システム"""
    
    @staticmethod
    def recommend_crystal_attributes(task_type: TaskType) -> List[CrystalAttribute]:
        """タスクタイプに基づくクリスタル属性推奨"""
        recommendations = {
            TaskType.ROUTINE: [CrystalAttribute.SELF_DISCIPLINE, CrystalAttribute.RESILIENCE],
            TaskType.ONE_SHOT: [CrystalAttribute.COURAGE, CrystalAttribute.CURIOSITY],
            TaskType.SKILL_UP: [CrystalAttribute.WISDOM, CrystalAttribute.CREATIVITY],
            TaskType.SOCIAL: [CrystalAttribute.EMPATHY, CrystalAttribute.COMMUNICATION]
        }
        return recommendations.get(task_type, [CrystalAttribute.SELF_DISCIPLINE])
    
    @staticmethod
    def recommend_difficulty(
        user_experience_level: int,
        task_complexity: str,
        user_confidence: int
    ) -> TaskDifficulty:
        """難易度推奨"""
        # 簡単な推奨ロジック
        if task_complexity == "simple" and user_confidence >= 4:
            return TaskDifficulty.EASY
        elif task_complexity == "complex" or user_confidence <= 2:
            return TaskDifficulty.HARD
        else:
            return TaskDifficulty.MEDIUM