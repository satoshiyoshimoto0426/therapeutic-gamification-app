"""
Task Management Service Simple Validation

タスク

Requirements: 5.1, 5.5
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.task_system import (
    Task, TaskType, TaskDifficulty, TaskPriority, TaskStatus, ADHDSupportLevel,
    TaskXPCalculator, TaskTypeRecommender
)
from shared.interfaces.core_types import CrystalAttribute


def test_task_creation():
    """タスク"""
    print("=== タスク ===")
    
    # 1. ?
    print("\n1. ?")
    routine_task = Task(
        task_id="routine_001",
        uid="test_user",
        task_type=TaskType.ROUTINE,
        title="?",
        description="?30?",
        difficulty=TaskDifficulty.EASY,
        priority=TaskPriority.HIGH,
        estimated_duration=30,
        adhd_support_level=ADHDSupportLevel.BASIC,
        primary_crystal_attribute=CrystalAttribute.SELF_DISCIPLINE,
        tags=["?", "?"],
        is_recurring=True,
        recurrence_pattern="daily"
    )
    
    print(f"? ?")
    print(f"  - タスクID: {routine_task.task_id}")
    print(f"  - タスク: {routine_task.title}")
    print(f"  - タスク: {routine_task.task_type.value}")
    print(f"  - ?: {routine_task.difficulty.value}")
    print(f"  - 基本XP: {routine_task.base_xp}")
    print(f"  - ?: {routine_task.primary_crystal_attribute.value}")
    
    # 2. ストーリー
    print("\n2. ストーリー")
    skill_task = Task(
        task_id="skill_001",
        uid="test_user",
        task_type=TaskType.SKILL_UP,
        title="Python学",
        description="Pythonの",
        difficulty=TaskDifficulty.MEDIUM,
        estimated_duration=60,
        adhd_support_level=ADHDSupportLevel.INTENSIVE,
        pomodoro_sessions_planned=2,
        focus_music_enabled=True,
        primary_crystal_attribute=CrystalAttribute.WISDOM,
        secondary_crystal_attributes=[CrystalAttribute.CREATIVITY],
        tags=["学", "プレビュー"]
    )
    
    print(f"? ストーリー")
    print(f"  - タスクID: {skill_task.task_id}")
    print(f"  - タスク: {skill_task.title}")
    print(f"  - タスク: {skill_task.task_type.value}")
    print(f"  - 基本XP: {skill_task.base_xp}")
    print(f"  - ADHD支援: {skill_task.adhd_support_level.value}")
    
    # 3. ?
    print("\n3. ?")
    social_task = Task(
        task_id="social_001",
        uid="test_user",
        task_type=TaskType.SOCIAL,
        title="?",
        description="?",
        difficulty=TaskDifficulty.EASY,
        estimated_duration=45,
        primary_crystal_attribute=CrystalAttribute.COMMUNICATION,
        secondary_crystal_attributes=[CrystalAttribute.EMPATHY],
        tags=["?", "?"]
    )
    
    print(f"? ?")
    print(f"  - タスクID: {social_task.task_id}")
    print(f"  - タスク: {social_task.title}")
    print(f"  - タスク: {social_task.task_type.value}")
    print(f"  - 基本XP: {social_task.base_xp}")
    
    # 4. ?
    print("\n4. ?")
    oneshot_task = Task(
        task_id="oneshot_001",
        uid="test_user",
        task_type=TaskType.ONE_SHOT,
        title="プレビュー",
        description="?",
        difficulty=TaskDifficulty.HARD,
        priority=TaskPriority.URGENT,
        estimated_duration=120,
        due_date=datetime.utcnow() + timedelta(days=7),
        adhd_support_level=ADHDSupportLevel.MODERATE,
        pomodoro_sessions_planned=4,
        primary_crystal_attribute=CrystalAttribute.COURAGE,
        tags=["?", "?"]
    )
    
    print(f"? ?")
    print(f"  - タスクID: {oneshot_task.task_id}")
    print(f"  - タスク: {oneshot_task.title}")
    print(f"  - タスク: {oneshot_task.task_type.value}")
    print(f"  - ?: {oneshot_task.priority.value}")
    print(f"  - ?: {oneshot_task.due_date}")
    print(f"  - 基本XP: {oneshot_task.base_xp}")
    
    return [routine_task, skill_task, social_task, oneshot_task]


def test_task_lifecycle():
    """タスク"""
    print("\n=== タスク ===")
    
    # タスク
    task = Task(
        task_id="lifecycle_001",
        uid="test_user",
        task_type=TaskType.SKILL_UP,
        title="?",
        description="タスク",
        difficulty=TaskDifficulty.MEDIUM,
        estimated_duration=45,
        adhd_support_level=ADHDSupportLevel.MODERATE,
        pomodoro_sessions_planned=2
    )
    
    print(f"\n1. タスク")
    print(f"? ?: {task.status.value}")
    print(f"? 基本XP: {task.base_xp}")
    
    # タスク
    print(f"\n2. タスク")
    task.start_task()
    print(f"? ?: {task.status.value}")
    print(f"? ?: {task.started_at}")
    
    # タスク
    print(f"\n3. タスク")
    mood_score = 4
    actual_duration = 40
    notes = "?"
    
    # Pomodoro?
    task.pomodoro_sessions_completed = 2
    
    xp_earned = task.complete_task(mood_score, actual_duration, notes)
    
    print(f"? ?: {task.status.value}")
    print(f"? ?: {task.completed_at}")
    print(f"? 気分: {task.mood_at_completion}")
    print(f"? 実装: {task.actual_duration}?")
    print(f"? ?XP: {xp_earned}")
    print(f"? メイン: {task.notes}")
    
    return task


def test_xp_calculation():
    """XP計算"""
    print("\n=== XP計算 ===")
    
    # ?XP計算
    test_cases = [
        {
            "name": "基本",
            "task_type": TaskType.ROUTINE,
            "difficulty": TaskDifficulty.EASY,
            "mood_score": 3,
            "adhd_support": ADHDSupportLevel.NONE
        },
        {
            "name": "?",
            "task_type": TaskType.SKILL_UP,
            "difficulty": TaskDifficulty.VERY_HARD,
            "mood_score": 5,
            "adhd_support": ADHDSupportLevel.INTENSIVE
        },
        {
            "name": "?",
            "task_type": TaskType.SOCIAL,
            "difficulty": TaskDifficulty.MEDIUM,
            "mood_score": 2,
            "adhd_support": ADHDSupportLevel.BASIC
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        
        # ?
        task = Task(
            task_id=f"xp_test_{case['name']}",
            uid="test_user",
            task_type=case["task_type"],
            title=f"XP? - {case['name']}",
            difficulty=case["difficulty"],
            adhd_support_level=case["adhd_support"],
            pomodoro_sessions_planned=2
        )
        
        # Pomodoro?ADHD支援
        task.pomodoro_sessions_completed = 2
        
        # ?XP計算
        xp_result = TaskXPCalculator.calculate_detailed_xp(
            task, case["mood_score"], 30
        )
        
        print(f"  - タスク: {case['task_type'].value}")
        print(f"  - ?: {case['difficulty'].value}")
        print(f"  - 気分: {case['mood_score']}")
        print(f"  - ADHD支援: {case['adhd_support'].value}")
        print(f"  - 基本XP: {xp_result.base_xp}")
        print(f"  - 気分: {xp_result.mood_coefficient:.2f}")
        print(f"  - ADHD支援: {xp_result.adhd_assist_multiplier:.2f}")
        print(f"  - ?: {xp_result.time_efficiency_bonus:.2f}")
        print(f"  - ?: {xp_result.priority_bonus:.2f}")
        print(f"  - ?XP: {xp_result.final_xp}")


def test_task_recommendations():
    """タスク"""
    print("\n=== タスク ===")
    
    # ?
    test_goals = [
        "?",
        "プレビュー", 
        "?",
        "?"
    ]
    
    print("\n1. ?:")
    for goal in test_goals:
        recommended_type = TaskTypeRecommender.recommend_task_type(goal)
        recommended_crystals = TaskTypeRecommender.recommend_crystal_attributes(recommended_type)
        
        print(f"  ?: {goal}")
        print(f"  ?: {recommended_type.value}")
        print(f"  ?: {[c.value for c in recommended_crystals]}")
        print()
    
    # ?
    print("2. ?:")
    difficulty_cases = [
        {"experience": 1, "complexity": "simple", "confidence": 2},
        {"experience": 3, "complexity": "moderate", "confidence": 4},
        {"experience": 5, "complexity": "complex", "confidence": 5}
    ]
    
    for case in difficulty_cases:
        recommended_difficulty = TaskTypeRecommender.recommend_difficulty(
            case["experience"], case["complexity"], case["confidence"]
        )
        
        print(f"  ?: {case['experience']}, ?: {case['complexity']}, 自動: {case['confidence']}")
        print(f"  ?: {recommended_difficulty.value}")
        print()


def test_crystal_growth_events():
    """?"""
    print("\n=== ? ===")
    
    # ?
    tasks = [
        Task(
            task_id="crystal_routine",
            uid="test_user",
            task_type=TaskType.ROUTINE,
            title="?",
            difficulty=TaskDifficulty.EASY,
            primary_crystal_attribute=CrystalAttribute.SELF_DISCIPLINE,
            secondary_crystal_attributes=[CrystalAttribute.RESILIENCE]
        ),
        Task(
            task_id="crystal_skill",
            uid="test_user", 
            task_type=TaskType.SKILL_UP,
            title="学",
            difficulty=TaskDifficulty.MEDIUM,
            primary_crystal_attribute=CrystalAttribute.WISDOM,
            secondary_crystal_attributes=[CrystalAttribute.CREATIVITY, CrystalAttribute.CURIOSITY]
        )
    ]
    
    for task in tasks:
        growth_events = task.get_crystal_growth_events()
        
        print(f"\nタスク: {task.title} ({task.task_type.value})")
        print(f"?: {len(growth_events)}")
        
        for attribute, event_type in growth_events:
            print(f"  - {attribute.value}: {event_type.value}")


def main():
    """メイン"""
    print("Task Management Service Simple Validation")
    print("=" * 50)
    
    try:
        # 1. タスク
        tasks = test_task_creation()
        
        # 2. タスク
        completed_task = test_task_lifecycle()
        
        # 3. XP計算
        test_xp_calculation()
        
        # 4. タスク
        test_task_recommendations()
        
        # 5. ?
        test_crystal_growth_events()
        
        print("\n" + "=" * 50)
        print("? ?")
        print(f"実装:")
        print(f"  - 4?Routine?One-Shot?Skill-Up?Social?")
        print(f"  - XP計算ADHD支援")
        print(f"  - タスク")
        print(f"  - ?")
        print(f"  - タスク")
        print(f"  - ADHD支援")
        
        return True
        
    except Exception as e:
        print(f"\n? 検証: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)