#!/usr/bin/env python3
"""
タスク2?
?
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from shared.interfaces.core_types import (
    UserProfile, TaskRecord, StoryState, CrystalAttribute, 
    TaskType, TaskStatus, CrystalState, UserCrystalSystem
)
from shared.interfaces.task_system import (
    Task, TaskXPCalculator, TaskDifficulty, TaskPriority, 
    ADHDSupportLevel, TaskTypeRecommender
)
from shared.interfaces.crystal_validation import (
    CrystalValidator, CrystalGrowthCalculator
)
from shared.interfaces.task_validation import (
    TaskValidator, TaskBusinessRules, TaskMetrics
)
from shared.interfaces.validation import DataIntegrityValidator
from shared.interfaces.model_factory import (
    CrystalSystemFactory, MilestoneFactory, SynergyFactory, GameStateFactory
)

def test_subtask_2_1():
    """?2.1: コア"""
    print("=== ?2.1: コア ===")
    
    # UserProfile?
    print("1. UserProfile?...")
    user_profile = UserProfile(
        uid="test_user_001",
        email="test@example.com",
        display_name="?",
        player_level=5,
        yu_level=3,
        total_xp=250,
        created_at=datetime.now(),
        last_active=datetime.now()
    )
    
    assert user_profile.uid == "test_user_001"
    assert user_profile.player_level == 5
    assert user_profile.yu_level == 3
    assert len(user_profile.crystal_gauges) == 8  # 8?
    print("   ? UserProfile?")
    
    # StoryState?
    print("2. StoryState?...")
    story_state = StoryState(
        uid="test_user_001",
        current_chapter="self_discipline",
        current_node="intro_node_1",
        available_edges=["edge_1", "edge_2"],
        story_history=[],
        unlocked_chapters=["self_discipline"],
        unlocked_nodes=["intro_node_1"],
        completed_nodes=[],
        choice_history=[],
        companion_relationships={},
        ending_scores={},
        story_flags={},
        last_updated=datetime.now()
    )
    
    assert story_state.uid == "test_user_001"
    assert story_state.current_chapter == "self_discipline"
    assert len(story_state.available_edges) == 2
    print("   ? StoryState?")
    
    # TaskRecord?
    print("3. TaskRecord?...")
    task_record = TaskRecord(
        task_id="test_task_001",
        uid="test_user_001",
        task_type=TaskType.ONE_SHOT,
        title="?",
        description="?",
        difficulty=3,
        created_at=datetime.now()
    )
    
    assert task_record.task_id == "test_task_001"
    assert task_record.task_type == TaskType.ONE_SHOT
    assert task_record.difficulty == 3
    print("   ? TaskRecord?")
    
    # デフォルト
    print("4. デフォルト...")
    validation_result = DataIntegrityValidator.validate_user_profile_consistency(user_profile)
    assert validation_result['valid'] == True
    print("   ? デフォルト")
    
    print("? ?2.1 ?: コア\n")

def test_subtask_2_2():
    """?2.2: 8?"""
    print("=== ?2.2: 8? ===")
    
    # CRYSTAL_ATTRIBUTES?
    print("1. CRYSTAL_ATTRIBUTES?...")
    crystal_attributes = list(CrystalAttribute)
    assert len(crystal_attributes) == 8
    expected_attributes = [
        "self_discipline", "empathy", "resilience", "curiosity",
        "communication", "creativity", "courage", "wisdom"
    ]
    for attr in expected_attributes:
        assert any(crystal_attr.value == attr for crystal_attr in crystal_attributes)
    print("   ? 8つ")
    
    # CrystalGauge?UserCrystalSystem?
    print("2. CrystalGauge?UserCrystalSystem?...")
    crystal_system = CrystalSystemFactory.create_initial_crystal_system("test_user")
    
    assert crystal_system.uid == "test_user"
    assert len(crystal_system.crystals) == 8
    assert crystal_system.total_growth_events == 0
    assert crystal_system.resonance_level == 0
    print("   ? CrystalGauge?")
    
    # ?
    print("3. ?...")
    crystal = crystal_system.crystals[CrystalAttribute.SELF_DISCIPLINE]
    old_value = crystal.current_value
    
    updated_crystal, milestone_reached = CrystalValidator.apply_growth_to_crystal(
        crystal, 10, datetime.now()
    )
    
    assert updated_crystal.current_value > old_value
    assert updated_crystal.last_growth_event is not None
    print("   ? ?")
    
    # ?
    print("4. ?...")
    # ?100%ま
    crystal.current_value = 100
    milestone_reached = CrystalValidator.check_milestone_reached(99, 100)
    assert milestone_reached == True
    print("   ? ?")
    
    # ?
    print("5. ?...")
    # 成
    growth_amount = CrystalGrowthCalculator.calculate_growth_amount(
        CrystalAttribute.SELF_DISCIPLINE,
        "task_completion"
    )
    assert growth_amount > 0
    assert growth_amount <= 20  # ?
    
    # バリデーション
    assert CrystalValidator.validate_growth_amount(5) == True
    assert CrystalValidator.validate_growth_amount(25) == False
    assert CrystalValidator.validate_crystal_value(75) == True
    assert CrystalValidator.validate_crystal_value(150) == False
    print("   ? ?")
    
    print("? ?2.2 ?: 8?\n")

def test_subtask_2_3():
    """?2.3: タスクXP計算"""
    print("=== ?2.3: タスクXP計算 ===")
    
    # TaskType?
    print("1. TaskType?...")
    task_types = list(TaskType)
    expected_types = ["routine", "one_shot", "skill_up", "social"]
    for task_type in expected_types:
        assert any(t.value == task_type for t in task_types)
    print("   ? TaskType?")
    
    # Task?
    print("2. Task?...")
    task = Task(
        task_id="test_task_xp",
        uid="test_user",
        task_type=TaskType.ONE_SHOT,
        title="XP計算",
        difficulty=TaskDifficulty.MEDIUM
    )
    
    assert task.task_id == "test_task_xp"
    assert task.task_type == TaskType.ONE_SHOT
    assert task.difficulty == TaskDifficulty.MEDIUM
    assert task.base_xp > 0  # 自動
    print("   ? Task?")
    
    # XP計算difficulty ? mood_coefficient ? adhd_assist?
    print("3. XP計算...")
    task.start_task()
    xp_earned = task.complete_task(mood_score=4, external_adhd_multiplier=1.2)
    
    # ?
    expected_mood_coefficient = 0.8 + (4 - 1) * 0.1  # 1.1
    expected_base_xp = task.base_xp
    # 実装XPが
    assert xp_earned > 0
    assert task.xp_earned == xp_earned
    print(f"   ? XP計算XP: {xp_earned}?")
    
    # ?XP計算
    print("4. ?XP計算...")
    detailed_task = Task(
        task_id="detailed_xp_test",
        uid="test_user",
        task_type=TaskType.SKILL_UP,
        title="?XP計算",
        difficulty=TaskDifficulty.HARD,
        priority=TaskPriority.HIGH,
        adhd_support_level=ADHDSupportLevel.BASIC
    )
    
    result = TaskXPCalculator.calculate_detailed_xp(
        task=detailed_task,
        mood_score=4,
        actual_duration=30
    )
    
    assert result.base_xp > 0
    assert 0.8 <= result.mood_coefficient <= 1.2
    assert 1.0 <= result.adhd_assist_multiplier <= 1.5
    assert result.final_xp > 0
    print("   ? ?XP計算")
    
    # タスクXP計算
    print("5. タスクXP計算...")
    
    # ?XP計算
    difficulties = [TaskDifficulty.VERY_EASY, TaskDifficulty.EASY, TaskDifficulty.MEDIUM, 
                   TaskDifficulty.HARD, TaskDifficulty.VERY_HARD]
    
    for difficulty in difficulties:
        test_task = Task(
            task_id=f"test_{difficulty.name}",
            uid="test_user",
            task_type=TaskType.ONE_SHOT,
            title=f"Test {difficulty.name}",
            difficulty=difficulty
        )
        test_task.start_task()
        xp = test_task.complete_task(mood_score=3)
        assert xp > 0
        print(f"     ? {difficulty.name}: {xp} XP")
    
    # タスク
    print("6. タスク...")
    routine_attrs = TaskTypeRecommender.recommend_crystal_attributes(TaskType.ROUTINE)
    assert CrystalAttribute.SELF_DISCIPLINE in routine_attrs
    
    social_attrs = TaskTypeRecommender.recommend_crystal_attributes(TaskType.SOCIAL)
    assert CrystalAttribute.EMPATHY in social_attrs
    
    recommended_type = TaskTypeRecommender.recommend_task_type("?")
    assert recommended_type == TaskType.ROUTINE
    print("   ? タスク")
    
    print("? ?2.3 ?: タスクXP計算\n")

def test_additional_validation_features():
    """?"""
    print("=== ? ===")
    
    # タスク
    print("1. タスク...")
    valid_task_data = {
        'task_id': 'valid_task',
        'uid': 'test_user',
        'task_type': TaskType.ONE_SHOT,
        'title': '?',
        'difficulty': TaskDifficulty.MEDIUM,
        'description': 'こ',
        'estimated_duration': 30,
        'tags': ['?']
    }
    
    is_valid, errors = TaskValidator.validate_task_creation(valid_task_data)
    assert is_valid == True
    assert len(errors) == 0
    print("   ? タスク")
    
    # ビジネス
    print("2. ビジネス...")
    can_create, message = TaskBusinessRules.can_user_create_task("user1", 10, 16)
    assert can_create == True
    
    can_create, message = TaskBusinessRules.can_user_create_task("user1", 16, 16)
    assert can_create == False
    print("   ? ビジネス")
    
    # メイン
    print("3. メイン...")
    completion_rate = TaskMetrics.calculate_completion_rate(8, 10)
    assert completion_rate == 0.8
    
    accuracy = TaskMetrics.calculate_time_estimation_accuracy([30, 45], [35, 40])
    assert 0.0 <= accuracy <= 1.0
    print("   ? メイン")
    
    print("? ?\n")

def main():
    """メイン"""
    print("タスク2?")
    print("=" * 80)
    
    try:
        # ?2.1の
        test_subtask_2_1()
        
        # ?2.2の
        test_subtask_2_2()
        
        # ?2.3の
        test_subtask_2_3()
        
        # ?
        test_additional_validation_features()
        
        print("=" * 80)
        print("? タスク2?")
        print("\n? 実装:")
        print("  ? 2.1 コア")
        print("    - UserProfile?StoryState?TaskRecordのTypeScript/Python?")
        print("    - デフォルト")
        print("  ? 2.2 8?")
        print("    - CRYSTAL_ATTRIBUTES?CrystalGauge?")
        print("    - ?")
        print("    - ?")
        print("  ? 2.3 タスクXP計算")
        print("    - TaskType?Task?")
        print("    - XP計算difficulty ? mood_coefficient ? adhd_assist?")
        print("    - タスクXP計算")
        print("\n? ?:")
        print("  ? ?1.2: ユーザー")
        print("  ? ?4.2: 8?")
        print("  ? ?4.5: ?")
        print("  ? ?5.1: 4?")
        print("  ? ?5.2: XP計算")
        
        return True
        
    except Exception as e:
        print(f"\n? ?: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)