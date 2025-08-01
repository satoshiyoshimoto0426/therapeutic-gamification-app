"""
タスク
Task system validation utilities
Requirements: 5.1, 5.2
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .task_system import Task, TaskDifficulty, TaskPriority, ADHDSupportLevel
from .core_types import TaskType, TaskStatus


class TaskValidator:
    """タスク"""
    
    # バリデーション
    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_NOTES_LENGTH = 1000
    MAX_TAGS_COUNT = 10
    MAX_TAG_LENGTH = 50
    MIN_ESTIMATED_DURATION = 5    # ?5?
    MAX_ESTIMATED_DURATION = 480  # ?8?
    
    @staticmethod
    def validate_task_creation(task_data: Dict) -> Tuple[bool, List[str]]:
        """タスク"""
        errors = []
        
        # ?
        required_fields = ['task_id', 'uid', 'task_type', 'title', 'difficulty']
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                errors.append(f"? '{field}' が")
        
        # タスク
        title = task_data.get('title', '')
        if len(title) > TaskValidator.MAX_TITLE_LENGTH:
            errors.append(f"タスク{TaskValidator.MAX_TITLE_LENGTH}文字")
        
        # ?
        description = task_data.get('description', '')
        if len(description) > TaskValidator.MAX_DESCRIPTION_LENGTH:
            errors.append(f"?{TaskValidator.MAX_DESCRIPTION_LENGTH}文字")
        
        # ?
        estimated_duration = task_data.get('estimated_duration', 30)
        if not (TaskValidator.MIN_ESTIMATED_DURATION <= estimated_duration <= TaskValidator.MAX_ESTIMATED_DURATION):
            errors.append(f"?{TaskValidator.MIN_ESTIMATED_DURATION}?{TaskValidator.MAX_ESTIMATED_DURATION}?")
        
        # タスク
        tags = task_data.get('tags', [])
        if len(tags) > TaskValidator.MAX_TAGS_COUNT:
            errors.append(f"タスク{TaskValidator.MAX_TAGS_COUNT}?")
        
        for tag in tags:
            if len(tag) > TaskValidator.MAX_TAG_LENGTH:
                errors.append(f"タスク{TaskValidator.MAX_TAG_LENGTH}文字")
        
        # ?
        due_date = task_data.get('due_date')
        if due_date and due_date <= datetime.utcnow():
            errors.append("?")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_task_completion(task: Task, mood_score: int) -> Tuple[bool, List[str]]:
        """タスク"""
        errors = []
        
        # タスク
        if task.status != TaskStatus.IN_PROGRESS:
            errors.append("?")
        
        # 気分
        if not (1 <= mood_score <= 5):
            errors.append("気分1か5の")
        
        # 実装
        if task.actual_duration and task.actual_duration < 1:
            errors.append("実装1?")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_xp_calculation_inputs(
        difficulty: int,
        mood_coefficient: float,
        adhd_assist: float
    ) -> Tuple[bool, List[str]]:
        """XP計算"""
        errors = []
        
        # ?
        if not (1 <= difficulty <= 5):
            errors.append("?1か5の")
        
        # 気分
        if not (0.5 <= mood_coefficient <= 2.0):
            errors.append("気分0.5か2.0の")
        
        # ADHD支援
        if not (0.5 <= adhd_assist <= 2.0):
            errors.append("ADHD支援0.5か2.0の")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_task_state_transition(
        current_status: TaskStatus,
        new_status: TaskStatus
    ) -> Tuple[bool, str]:
        """タスク"""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.OVERDUE],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.OVERDUE],
            TaskStatus.OVERDUE: [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS],
            TaskStatus.COMPLETED: []  # ?
        }
        
        allowed_transitions = valid_transitions.get(current_status, [])
        
        if new_status in allowed_transitions:
            return True, ""
        else:
            return False, f"?{current_status.value}か{new_status.value}に"
    
    @staticmethod
    def validate_adhd_support_settings(
        support_level: ADHDSupportLevel,
        pomodoro_sessions: int,
        estimated_duration: int
    ) -> Tuple[bool, List[str]]:
        """ADHD支援"""
        errors = []
        
        # Pomodoro?
        if pomodoro_sessions < 1:
            errors.append("Pomodoro?1?")
        
        max_sessions = estimated_duration // 25  # 25?
        if pomodoro_sessions > max_sessions + 2:  # ?
            errors.append(f"?({estimated_duration}?)にPomodoro?")
        
        # 支援
        if support_level == ADHDSupportLevel.NONE and pomodoro_sessions > 1:
            errors.append("支援Pomodoro?1つ")
        
        return len(errors) == 0, errors


class TaskBusinessRules:
    """タスク"""
    
    @staticmethod
    def can_user_create_task(
        user_id: str,
        daily_task_count: int,
        daily_limit: int = 16
    ) -> Tuple[bool, str]:
        """ユーザー"""
        if daily_task_count >= daily_limit:
            return False, f"1?({daily_limit}?)に"
        
        return True, ""
    
    @staticmethod
    def calculate_recommended_break_time(
        estimated_duration: int,
        adhd_support_level: ADHDSupportLevel
    ) -> int:
        """?"""
        base_break_time = 5  # 基本5?
        
        # ?
        if estimated_duration > 60:
            base_break_time += (estimated_duration - 60) // 30 * 2
        
        # ADHD支援
        support_multipliers = {
            ADHDSupportLevel.NONE: 1.0,
            ADHDSupportLevel.BASIC: 1.2,
            ADHDSupportLevel.MODERATE: 1.5,
            ADHDSupportLevel.INTENSIVE: 2.0
        }
        
        multiplier = support_multipliers.get(adhd_support_level, 1.0)
        return int(base_break_time * multiplier)
    
    @staticmethod
    def should_suggest_task_split(
        estimated_duration: int,
        difficulty: TaskDifficulty,
        adhd_support_level: ADHDSupportLevel
    ) -> Tuple[bool, str]:
        """タスク"""
        # ADHD支援
        if adhd_support_level in [ADHDSupportLevel.MODERATE, ADHDSupportLevel.INTENSIVE]:
            if estimated_duration > 45:
                return True, "?45?"
        
        # ?
        if difficulty in [TaskDifficulty.HARD, TaskDifficulty.VERY_HARD]:
            if estimated_duration > 90:
                return True, "?90?"
        
        return False, ""
    
    @staticmethod
    def calculate_urgency_score(
        due_date: Optional[datetime],
        priority: TaskPriority,
        difficulty: TaskDifficulty
    ) -> float:
        """?0.0-1.0?"""
        if not due_date:
            return 0.0
        
        # ?
        time_remaining = due_date - datetime.utcnow()
        hours_remaining = time_remaining.total_seconds() / 3600
        
        if hours_remaining <= 0:
            time_urgency = 1.0
        elif hours_remaining <= 2:
            time_urgency = 0.9
        elif hours_remaining <= 24:
            time_urgency = 0.7
        elif hours_remaining <= 72:
            time_urgency = 0.5
        else:
            time_urgency = 0.2
        
        # ?
        priority_weights = {
            TaskPriority.LOW: 0.5,
            TaskPriority.MEDIUM: 0.7,
            TaskPriority.HIGH: 0.9,
            TaskPriority.URGENT: 1.0
        }
        
        priority_weight = priority_weights.get(priority, 0.7)
        
        # ?
        difficulty_weights = {
            TaskDifficulty.VERY_EASY: 0.8,
            TaskDifficulty.EASY: 0.9,
            TaskDifficulty.MEDIUM: 1.0,
            TaskDifficulty.HARD: 1.1,
            TaskDifficulty.VERY_HARD: 1.2
        }
        
        difficulty_weight = difficulty_weights.get(difficulty, 1.0)
        
        # ?
        urgency_score = time_urgency * priority_weight * difficulty_weight
        return min(1.0, urgency_score)


class TaskMetrics:
    """タスク"""
    
    @staticmethod
    def calculate_completion_rate(
        completed_tasks: int,
        total_tasks: int
    ) -> float:
        """?"""
        if total_tasks == 0:
            return 0.0
        return completed_tasks / total_tasks
    
    @staticmethod
    def calculate_average_xp_per_task(
        total_xp: int,
        completed_tasks: int
    ) -> float:
        """タスクXPを"""
        if completed_tasks == 0:
            return 0.0
        return total_xp / completed_tasks
    
    @staticmethod
    def calculate_time_estimation_accuracy(
        estimated_durations: List[int],
        actual_durations: List[int]
    ) -> float:
        """?"""
        if not estimated_durations or not actual_durations:
            return 0.0
        
        if len(estimated_durations) != len(actual_durations):
            return 0.0
        
        accuracy_scores = []
        for estimated, actual in zip(estimated_durations, actual_durations):
            if estimated == 0 or actual == 0:
                continue
            
            # ? = 1 - |? - 実装| / max(?, 実装)
            accuracy = 1 - abs(estimated - actual) / max(estimated, actual)
            accuracy_scores.append(max(0, accuracy))
        
        return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
    
    @staticmethod
    def calculate_productivity_trend(
        daily_xp_history: List[Tuple[datetime, int]],
        days: int = 7
    ) -> str:
        """?"""
        if len(daily_xp_history) < 2:
            return "insufficient_data"
        
        # ?
        recent_data = daily_xp_history[-days:] if len(daily_xp_history) >= days else daily_xp_history
        
        if len(recent_data) < 2:
            return "insufficient_data"
        
        # ?
        x_values = list(range(len(recent_data)))
        y_values = [xp for _, xp in recent_data]
        
        n = len(recent_data)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # ?
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 5:
            return "improving"
        elif slope < -5:
            return "declining"
        else:
            return "stable"