"""
タスクXP計算
Task system and XP calculation comprehensive tests
Requirements: 5.1, 5.2
"""

import pytest
from datetime import datetime, timedelta
from shared.interfaces.task_system import (
    Task, TaskDifficulty, TaskPriority, ADHDSupportLevel,
    TaskXPCalculator, XPCalculationResult, TaskTypeRecommender
)
from shared.interfaces.task_validation import TaskValidator, TaskBusinessRules, TaskMetrics
from shared.interfaces.core_types import TaskType, TaskStatus, CrystalAttribute


class TestTaskSystem:
    """タスク"""
    
    def test_task_creation(self):
        """基本"""
        task = Task(
            task_id="test_task_001",
            uid="test_user",
            task_type=TaskType.ONE_SHOT,
            title="?",
            description="こ",
            difficulty=TaskDifficulty.MEDIUM
        )
        
        assert task.task_id == "test_task_001"
        assert task.uid == "test_user"
        assert task.task_type == TaskType.ONE_SHOT
        assert task.title == "?"
        assert task.difficulty == TaskDifficulty.MEDIUM
        assert task.status == TaskStatus.PENDING
        assert task.base_xp > 0  # 自動
        print(f"? Task created with base XP: {task.base_xp}")
    
    def test_base_xp_calculation(self):
        """基本XPの"""
        # ?
        difficulties_and_expected_xp = [
            (TaskDifficulty.VERY_EASY, 5),
            (TaskDifficulty.EASY, 10),
            (TaskDifficulty.MEDIUM, 15),
            (TaskDifficulty.HARD, 25),
            (TaskDifficulty.VERY_HARD, 40)
        ]
        
        for difficulty, expected_base in difficulties_and_expected_xp:
            task = Task(
                task_id=f"test_{difficulty}",
                uid="test_user",
                task_type=TaskType.ONE_SHOT,
                title="Test Task",
                difficulty=difficulty
            )
            assert task.base_xp == expected_base
            print(f"? {difficulty.name}: {task.base_xp} XP")
    
    def test_task_lifecycle(self):
        """タスク"""
        task = Task(
            task_id="lifecycle_test",
            uid="test_user",
            task_type=TaskType.ONE_SHOT,
            title="?",
            difficulty=TaskDifficulty.MEDIUM
        )
        
        # ?
        assert task.status == TaskStatus.PENDING
        assert task.started_at is None
        assert task.completed_at is None
        print("? Initial state: PENDING")
        
        # タスク
        task.start_task()
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        print("? Task started: IN_PROGRESS")
        
        # タスク
        xp_earned = task.complete_task(mood_score=4, actual_duration=25)
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.mood_at_completion == 4
        assert task.actual_duration == 25
        assert xp_earned > 0
        assert task.xp_earned == xp_earned
        print(f"? Task completed: {xp_earned} XP earned")
    
    def test_xp_calculation_with_mood(self):
        """気分XP計算"""
        mood_tests = [
            (1, 0.8),  # ? -> 0.8?
            (3, 1.0),  # ? -> 1.0?
            (5, 1.2)   # ? -> 1.2?
        ]
        
        for mood_score, expected_coefficient in mood_tests:
            task = Task(
                task_id=f"mood_test_{mood_score}",
                uid="test_user",
                task_type=TaskType.ONE_SHOT,
                title="気分",
                difficulty=TaskDifficulty.MEDIUM  # base_xp = 15
            )
            task.start_task()
            
            xp_earned = task.complete_task(mood_score=mood_score)
            expected_xp = int(15 * expected_coefficient)  # base_xp * mood_coefficient
            assert xp_earned == expected_xp
            print(f"? Mood {mood_score}: {xp_earned} XP (coefficient: {expected_coefficient})")


class TestTaskXPCalculator:
    """TaskXPCalculator?"""
    
    def test_detailed_xp_calculation(self):
        """?XP計算"""
        task = Task(
            task_id="detailed_xp_test",
            uid="test_user",
            task_type=TaskType.ONE_SHOT,
            title="?XP計算",
            difficulty=TaskDifficulty.MEDIUM,
            priority=TaskPriority.HIGH,
            adhd_support_level=ADHDSupportLevel.BASIC,
            estimated_duration=30
        )
        
        result = TaskXPCalculator.calculate_detailed_xp(
            task=task,
            mood_score=4,
            actual_duration=25
        )
        
        assert isinstance(result, XPCalculationResult)
        assert result.base_xp == task.base_xp
        assert result.mood_coefficient == 1.1  # mood_score 4 -> 1.1
        assert result.adhd_assist_multiplier == 1.1  # BASIC level
        assert result.time_efficiency_bonus > 1.0  # ?
        assert result.priority_bonus == 1.1  # HIGH priority
        assert result.final_xp > result.base_xp
        assert "base" in result.breakdown
        assert "mood" in result.breakdown
        
        print(f"? Detailed XP calculation: {result.final_xp} XP")
        print(f"  - Base: {result.base_xp}")
        print(f"  - Mood coefficient: {result.mood_coefficient}")
        print(f"  - ADHD assist: {result.adhd_assist_multiplier}")
        print(f"  - Time efficiency: {result.time_efficiency_bonus}")
        print(f"  - Priority bonus: {result.priority_bonus}")
    
    def test_xp_preview(self):
        """XPプレビュー"""
        preview_xp = TaskXPCalculator.get_xp_preview(
            task_type=TaskType.SKILL_UP,
            difficulty=TaskDifficulty.HARD,
            mood_score=3,
            adhd_support_level=ADHDSupportLevel.MODERATE
        )
        
        assert isinstance(preview_xp, int)
        assert preview_xp > 0
        print(f"? XP Preview: {preview_xp} XP for SKILL_UP/HARD task")


class TestTaskTypeRecommender:
    """TaskTypeRecommender?"""
    
    def test_crystal_attribute_recommendation(self):
        """?"""
        # ROUTINEタスク
        routine_attrs = TaskTypeRecommender.recommend_crystal_attributes(TaskType.ROUTINE)
        assert CrystalAttribute.SELF_DISCIPLINE in routine_attrs
        assert CrystalAttribute.RESILIENCE in routine_attrs
        print(f"? ROUTINE task attributes: {[attr.value for attr in routine_attrs]}")
        
        # SOCIALタスク
        social_attrs = TaskTypeRecommender.recommend_crystal_attributes(TaskType.SOCIAL)
        assert CrystalAttribute.EMPATHY in social_attrs
        assert CrystalAttribute.COMMUNICATION in social_attrs
        print(f"? SOCIAL task attributes: {[attr.value for attr in social_attrs]}")
    
    def test_task_type_recommendation(self):
        """タスク"""
        test_cases = [
            ("?", TaskType.ROUTINE),
            ("?", TaskType.SOCIAL),
            ("プレビュー", TaskType.SKILL_UP),
            ("?", TaskType.ONE_SHOT)
        ]
        
        for goal, expected_type in test_cases:
            recommended_type = TaskTypeRecommender.recommend_task_type(goal)
            assert recommended_type == expected_type
            print(f"? '{goal}' -> {recommended_type.value}")


class TestTaskValidator:
    """TaskValidator?"""
    
    def test_task_creation_validation(self):
        """タスク"""
        # ?
        valid_task_data = {
            'task_id': 'valid_task',
            'uid': 'test_user',
            'task_type': TaskType.ONE_SHOT,
            'title': '?',
            'difficulty': TaskDifficulty.MEDIUM,
            'description': 'こ',
            'estimated_duration': 30,
            'tags': ['?', '?']
        }
        
        is_valid, errors = TaskValidator.validate_task_creation(valid_task_data)
        assert is_valid is True
        assert len(errors) == 0
        print("? Valid task data passed validation")
        
        # 無
        invalid_task_data = valid_task_data.copy()
        invalid_task_data['title'] = 'あ' * 101  # 101文字
        
        is_valid, errors = TaskValidator.validate_task_creation(invalid_task_data)
        assert is_valid is False
        assert len(errors) > 0
        print(f"? Invalid task data rejected: {errors[0]}")
    
    def test_task_completion_validation(self):
        """タスク"""
        task = Task(
            task_id="completion_test",
            uid="test_user",
            task_type=TaskType.ONE_SHOT,
            title="?",
            difficulty=TaskDifficulty.MEDIUM
        )
        
        # ?
        is_valid, errors = TaskValidator.validate_task_completion(task, 3)
        assert is_valid is False
        assert "?" in errors[0]
        print("? Non-in-progress task completion rejected")
        
        # ?
        task.start_task()
        is_valid, errors = TaskValidator.validate_task_completion(task, 3)
        assert is_valid is True
        assert len(errors) == 0
        print("? In-progress task completion validated")


class TestTaskBusinessRules:
    """TaskBusinessRules?"""
    
    def test_daily_task_limit(self):
        """?"""
        # ?
        can_create, message = TaskBusinessRules.can_user_create_task("user1", 10, 16)
        assert can_create is True
        print("? Within daily limit: can create task")
        
        # ?
        can_create, message = TaskBusinessRules.can_user_create_task("user1", 16, 16)
        assert can_create is False
        assert "?" in message
        print(f"? Over daily limit: {message}")
    
    def test_urgency_score_calculation(self):
        """?"""
        # 2?
        due_date = datetime.utcnow() + timedelta(hours=2)
        urgency_score = TaskBusinessRules.calculate_urgency_score(
            due_date, TaskPriority.HIGH, TaskDifficulty.MEDIUM
        )
        
        assert 0.0 <= urgency_score <= 1.0
        assert urgency_score > 0.5  # 2?
        print(f"? Urgency score for 2h deadline: {urgency_score:.2f}")


class TestTaskMetrics:
    """TaskMetrics?"""
    
    def test_completion_rate_calculation(self):
        """?"""
        completion_rate = TaskMetrics.calculate_completion_rate(8, 10)
        assert completion_rate == 0.8
        print(f"? Completion rate: {completion_rate * 100}%")
    
    def test_time_estimation_accuracy(self):
        """?"""
        estimated = [30, 45, 60, 20]
        actual = [35, 40, 65, 18]
        
        accuracy = TaskMetrics.calculate_time_estimation_accuracy(estimated, actual)
        assert 0.0 <= accuracy <= 1.0
        print(f"? Time estimation accuracy: {accuracy * 100:.1f}%")


def run_all_tests():
    """?"""
    print("=== Running Task System Tests ===")
    
    # 基本
    task_test = TestTaskSystem()
    task_test.test_task_creation()
    task_test.test_base_xp_calculation()
    task_test.test_task_lifecycle()
    task_test.test_xp_calculation_with_mood()
    print("? Basic task system tests passed\n")
    
    # XP計算
    xp_calc_test = TestTaskXPCalculator()
    xp_calc_test.test_detailed_xp_calculation()
    xp_calc_test.test_xp_preview()
    print("? XP calculation tests passed\n")
    
    # ?
    recommender_test = TestTaskTypeRecommender()
    recommender_test.test_crystal_attribute_recommendation()
    recommender_test.test_task_type_recommendation()
    print("? Task type recommender tests passed\n")
    
    # バリデーション
    validator_test = TestTaskValidator()
    validator_test.test_task_creation_validation()
    validator_test.test_task_completion_validation()
    print("? Task validation tests passed\n")
    
    # ビジネス
    business_test = TestTaskBusinessRules()
    business_test.test_daily_task_limit()
    business_test.test_urgency_score_calculation()
    print("? Business rules tests passed\n")
    
    # メイン
    metrics_test = TestTaskMetrics()
    metrics_test.test_completion_rate_calculation()
    metrics_test.test_time_estimation_accuracy()
    print("? Task metrics tests passed\n")
    
    print("=== All Task System Tests Passed! ===")


if __name__ == "__main__":
    run_all_tests()