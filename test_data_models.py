#!/usr/bin/env python3
"""
共有
Task 2: 共有
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from shared.interfaces.core_types import (
    UserProfile, TaskRecord, StoryState, CrystalAttribute, 
    TaskType, TaskStatus
)
from shared.interfaces.task_system import Task, TaskXPCalculator, TaskDifficulty
from shared.interfaces.crystal_validation import CrystalValidator, CrystalGrowthCalculator
from shared.interfaces.validation import DataIntegrityValidator

def test_core_data_models():
    """コア"""
    print("=== コア ===")
    
    # 1. UserProfileの
    print("1. UserProfileの...")
    user_profile = UserProfile(
        uid="test_user_001",
        email="test@example.com",
        display_name="?",
        player_level=5,
        yu_level=3,
        total_xp=250,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    print(f"   ? ユーザー: {user_profile.display_name}")
    print(f"   ? プレビュー: {user_profile.player_level}")
    print(f"   ? ?: {len(user_profile.crystal_gauges)}")
    
    # UserProfileの
    validation_result = DataIntegrityValidator.validate_user_profile_consistency(user_profile)
    print(f"   ? バリデーション: {'?' if validation_result['valid'] else '無'}")
    if validation_result['warnings']:
        print(f"   ? ?: {validation_result['warnings']}")
    
    # 2. TaskRecordのXP計算
    print("\n2. TaskRecordのXP計算...")
    task = Task(
        task_id="test_task_001",
        uid="test_user_001",
        task_type=TaskType.ONE_SHOT,
        title="?",
        description="こ",
        difficulty=TaskDifficulty.MEDIUM
    )
    
    print(f"   ? タスク: {task.title}")
    print(f"   ? 基本XP: {task.base_xp}")
    
    # タスク
    task.start_task()
    xp_earned = task.complete_task(mood_score=4, actual_duration=25)
    
    print(f"   ? ?XP: {xp_earned}")
    print(f"   ? ストーリー: {task.status}")
    
    # 3. StoryStateの
    print("\n3. StoryStateの...")
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
        last_updated=datetime.utcnow()
    )
    
    print(f"   ? ストーリー: {story_state.current_chapter}")
    print(f"   ? ?: {story_state.current_node}")
    print(f"   ? ?: {len(story_state.available_edges)}")

def test_crystal_system():
    """?"""
    print("\n=== ? ===")
    
    # 1. ?
    print("1. ?...")
    growth_amount = CrystalGrowthCalculator.calculate_growth_amount(
        CrystalAttribute.SELF_DISCIPLINE,
        "task_completion"  # CrystalGrowthEventの
    )
    print(f"   ? 自動 + タスク: {growth_amount} ?")
    
    # 2. 治療
    message = CrystalGrowthCalculator.get_therapeutic_message(
        CrystalAttribute.SELF_DISCIPLINE,
        "task_completion",
        growth_amount
    )
    print(f"   ? 治療: {message}")
    
    # 3. バリデーション
    print("\n2. バリデーション...")
    
    # 成
    valid_growth = CrystalValidator.validate_growth_amount(5)
    invalid_growth = CrystalValidator.validate_growth_amount(25)  # ?
    
    print(f"   ? ?(5): {valid_growth}")
    print(f"   ? 無(25): {invalid_growth}")
    
    # ?
    valid_value = CrystalValidator.validate_crystal_value(75)
    invalid_value = CrystalValidator.validate_crystal_value(150)  # ?
    
    print(f"   ? ?(75): {valid_value}")
    print(f"   ? 無(150): {invalid_value}")

def test_xp_calculation():
    """XP計算"""
    print("\n=== XP計算 ===")
    
    # 1. ?XP計算
    print("1. ?XP計算...")
    task = Task(
        task_id="xp_test_task",
        uid="test_user",
        task_type=TaskType.SKILL_UP,
        title="XP計算",
        difficulty=TaskDifficulty.HARD,
        estimated_duration=45
    )
    
    result = TaskXPCalculator.calculate_detailed_xp(
        task=task,
        mood_score=4,
        actual_duration=40  # ?
    )
    
    print(f"   ? 基本XP: {result.base_xp}")
    print(f"   ? 気分: {result.mood_coefficient}")
    print(f"   ? ADHD支援: {result.adhd_assist_multiplier}")
    print(f"   ? ?: {result.time_efficiency_bonus}")
    print(f"   ? ?: {result.priority_bonus}")
    print(f"   ? ?XP: {result.final_xp}")
    
    # 2. XPプレビュー
    print("\n2. XPプレビュー...")
    preview_xp = TaskXPCalculator.get_xp_preview(
        task_type=TaskType.ROUTINE,
        difficulty=TaskDifficulty.EASY,
        mood_score=3
    )
    print(f"   ? ?(?)のXPプレビュー: {preview_xp}")

def test_validation_system():
    """バリデーション"""
    print("\n=== バリデーション ===")
    
    # 1. タスク
    print("1. タスク...")
    
    # ?
    user_profile = UserProfile(
        uid="test_user",
        email="test@example.com",
        display_name="?",
        daily_task_limit=16,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    task_record = TaskRecord(
        task_id="validation_test",
        uid="test_user",
        task_type=TaskType.ONE_SHOT,
        title="バリデーション",
        description="バリデーション",
        difficulty=3,
        created_at=datetime.utcnow()
    )
    
    # ?
    existing_tasks = []
    
    validation_result = DataIntegrityValidator.validate_task_business_rules(
        task_record, user_profile, existing_tasks
    )
    
    print(f"   ? バリデーション: {'?' if validation_result['valid'] else '無'}")
    print(f"   ? ?: {validation_result['daily_task_count']}")
    print(f"   ? ?: {validation_result['remaining_tasks']}")
    
    if validation_result['warnings']:
        print(f"   ? ?: {validation_result['warnings']}")

def main():
    """メイン"""
    print("共有")
    print("=" * 60)
    
    try:
        test_core_data_models()
        test_crystal_system()
        test_xp_calculation()
        test_validation_system()
        
        print("\n" + "=" * 60)
        print("? ?")
        print("\nタスク2?:")
        print("  ? 2.1 コア")
        print("  ? 2.2 8?")
        print("  ? 2.3 タスクXP計算")
        print("  ? デフォルト")
        
    except Exception as e:
        print(f"\n? ?: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)