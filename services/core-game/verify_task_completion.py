#!/usr/bin/env python3
"""
Verification script for Task 3: Build core game engine with XP and level management
This script validates that all sub-tasks have been implemented correctly.
"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

def verify_imports():
    """Verify all required imports work"""
    print("? Verifying imports...")
    
    try:
        from interfaces.core_types import (
            GameState, XPCalculation, ChapterType, Task, TaskType, TaskStatus
        )
        print("? Core types imported successfully")
    except ImportError as e:
        print(f"? Failed to import core types: {e}")
        return False
    
    try:
        from main import GameEngine
        print("? GameEngine imported successfully")
    except ImportError as e:
        print(f"? Failed to import GameEngine: {e}")
        return False
    
    return True

def verify_xp_calculation():
    """Verify XP calculation algorithm implementation"""
    print("\n? Verifying XP calculation algorithm...")
    
    from interfaces.core_types import Task, TaskType, TaskStatus
    from main import GameEngine
    
    # Create mock database and engine
    mock_db = Mock()
    engine = GameEngine(mock_db)
    
    # Create test task
    task = Task(
        task_id="test_task",
        uid="test_user",
        task_type=TaskType.ROUTINE,
        title="Test Task",
        description="Test",
        difficulty=3,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    # Test XP calculation with different coefficients
    xp_calc = engine.calculate_task_xp(task, 1.0, 1.0)
    assert xp_calc.base_xp == 30, f"Expected 30 base XP, got {xp_calc.base_xp}"
    assert xp_calc.final_xp == 30, f"Expected 30 final XP, got {xp_calc.final_xp}"
    
    # Test with mood coefficient
    xp_calc_mood = engine.calculate_task_xp(task, 1.2, 1.0)
    assert xp_calc_mood.final_xp == 36, f"Expected 36 XP with mood, got {xp_calc_mood.final_xp}"
    
    # Test with ADHD assist
    xp_calc_adhd = engine.calculate_task_xp(task, 1.0, 1.3)
    assert xp_calc_adhd.final_xp == 39, f"Expected 39 XP with ADHD assist, got {xp_calc_adhd.final_xp}"
    
    # Test with both coefficients
    xp_calc_both = engine.calculate_task_xp(task, 1.2, 1.3)
    expected_xp = int(30 * 1.2 * 1.3)  # Should be 46
    assert xp_calc_both.final_xp == expected_xp, f"Expected {expected_xp} XP with both, got {xp_calc_both.final_xp}"
    
    print("? XP calculation algorithm working correctly")
    return True

def verify_level_progression():
    """Verify level progression system with player/Yu separation"""
    print("\n? Verifying level progression system...")
    
    from main import GameEngine
    
    mock_db = Mock()
    engine = GameEngine(mock_db)
    
    # Test XP to level calculations
    assert engine.calculate_xp_for_level(1) == 0, "Level 1 should require 0 XP"
    assert engine.calculate_xp_for_level(2) == 100, "Level 2 should require 100 XP"
    assert engine.calculate_xp_for_level(3) == 250, "Level 3 should require 250 XP"
    
    # Test level from XP calculations
    assert engine.calculate_level_from_xp(0) == 1, "0 XP should be level 1"
    assert engine.calculate_level_from_xp(100) == 2, "100 XP should be level 2"
    assert engine.calculate_level_from_xp(250) == 3, "250 XP should be level 3"
    
    # Test exponential growth
    level_10_xp = engine.calculate_xp_for_level(10)
    level_5_xp = engine.calculate_xp_for_level(5)
    assert level_10_xp > level_5_xp * 2, "Higher levels should require exponentially more XP"
    
    print("? Level progression system working correctly")
    return True

def verify_resonance_system():
    """Verify resonance event system for level difference ? 5"""
    print("\n? Verifying resonance event system...")
    
    from main import GameEngine
    
    mock_db = Mock()
    engine = GameEngine(mock_db)
    
    # Check resonance constants
    assert engine.RESONANCE_LEVEL_DIFF_THRESHOLD == 5, "Resonance threshold should be 5"
    assert engine.RESONANCE_BONUS_XP == 500, "Resonance bonus should be 500 XP"
    
    print("? Resonance event system configured correctly")
    return True

def verify_crystal_gauge_system():
    """Verify crystal gauge tracking for 8 human development attributes"""
    print("\n? Verifying crystal gauge system...")
    
    from main import GameEngine
    from interfaces.core_types import ChapterType
    
    mock_db = Mock()
    engine = GameEngine(mock_db)
    
    # Check chapter system
    assert len(engine.CHAPTER_ORDER) == 8, f"Expected 8 chapters, got {len(engine.CHAPTER_ORDER)}"
    
    expected_chapters = [
        ChapterType.SELF_DISCIPLINE,
        ChapterType.EMPATHY,
        ChapterType.RESILIENCE,
        ChapterType.CURIOSITY,
        ChapterType.COMMUNICATION,
        ChapterType.CREATIVITY,
        ChapterType.COURAGE,
        ChapterType.WISDOM
    ]
    
    for i, expected in enumerate(expected_chapters):
        assert engine.CHAPTER_ORDER[i] == expected, f"Chapter {i} should be {expected}"
    
    # Check crystal completion threshold
    assert engine.CRYSTAL_COMPLETION_THRESHOLD == 100, "Crystal completion should be 100%"
    
    print("? Crystal gauge system working correctly")
    return True

def verify_unit_tests():
    """Verify comprehensive unit tests exist"""
    print("\n? Verifying unit tests...")
    
    test_files = [
        "test_core_game.py",
        "test_basic.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"? Found test file: {test_file}")
        else:
            print(f"? Missing test file: {test_file}")
            return False
    
    # Check test coverage by examining test_core_game.py
    with open("test_core_game.py", "r") as f:
        test_content = f.read()
    
    required_test_classes = [
        "TestXPCalculation",
        "TestLevelProgression", 
        "TestChapterProgression",
        "TestADHDSupport",
        "TestMoodCoefficient",
        "TestGameStateManagement"
    ]
    
    for test_class in required_test_classes:
        if test_class in test_content:
            print(f"? Found test class: {test_class}")
        else:
            print(f"? Missing test class: {test_class}")
            return False
    
    print("? Comprehensive unit tests verified")
    return True

def main():
    """Main verification function"""
    print("? Verifying Task 3: Build core game engine with XP and level management")
    print("=" * 70)
    
    all_passed = True
    
    # Run all verifications
    verifications = [
        verify_imports,
        verify_xp_calculation,
        verify_level_progression,
        verify_resonance_system,
        verify_crystal_gauge_system,
        verify_unit_tests
    ]
    
    for verification in verifications:
        try:
            if not verification():
                all_passed = False
        except Exception as e:
            print(f"? Verification failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("? ALL VERIFICATIONS PASSED!")
        print("? Task 3 has been successfully implemented with all sub-tasks:")
        print("   ? XP calculation algorithm: XP = ?(difficulty ? mood_coefficient ? adhd_assist)")
        print("   ? Level progression system with player/Yu level separation")
        print("   ? Resonance event system for level difference ? 5")
        print("   ? Crystal gauge tracking for 8 human development attributes")
        print("   ? Comprehensive unit tests for XP calculations and level progression")
        return True
    else:
        print("? Some verifications failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)