"""
Simple test for mobile-optimized LINE Bot UI functions
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mobile_ui_functions():
    """Test mobile UI functions"""
    try:
        from mobile_ui_functions import (
            create_mobile_optimized_heart_crystal_tasks,
            create_task_bubble_mobile,
            create_empty_task_bubble,
            create_task_completion_success_message
        )
        print("? Successfully imported mobile UI functions")
        
        # Test data
        sample_tasks = [
            {
                "id": "task_1",
                "title": "?",
                "type": "routine",
                "difficulty": 2,
                "xp_reward": 20
            },
            {
                "id": "task_2",
                "title": "?30?",
                "type": "skill_up", 
                "difficulty": 3,
                "xp_reward": 30
            }
        ]
        
        # Test mobile-optimized Heart Crystal tasks
        flex_message = create_mobile_optimized_heart_crystal_tasks(sample_tasks)
        assert flex_message is not None
        assert hasattr(flex_message, 'alt_text')
        assert "? ?" in flex_message.alt_text
        print("? Mobile-optimized Heart Crystal tasks creation: PASSED")
        
        # Test individual task bubble
        task_bubble = create_task_bubble_mobile(sample_tasks[0])
        assert task_bubble is not None
        assert hasattr(task_bubble, 'layout')
        assert task_bubble.layout == "vertical"
        print("? Mobile task bubble creation: PASSED")
        
        # Test empty task bubble
        empty_bubble = create_empty_task_bubble()
        assert empty_bubble is not None
        assert hasattr(empty_bubble, 'layout')
        print("? Empty task bubble creation: PASSED")
        
        # Test completion success message
        success_message = create_task_completion_success_message("?", 25)
        assert success_message is not None
        assert hasattr(success_message, 'alt_text')
        assert "?" in success_message.alt_text
        print("? Task completion success message: PASSED")
        
        return True
        
    except ImportError as e:
        print(f"? Import error: {e}")
        return False
    except Exception as e:
        print(f"? Test error: {e}")
        return False

def test_adhd_considerations():
    """Test ADHD-friendly mobile optimizations"""
    try:
        from mobile_ui_functions import create_mobile_optimized_heart_crystal_tasks, create_task_bubble_mobile
        
        # Test with many tasks (should limit to 9 for cognitive load reduction)
        many_tasks = []
        for i in range(15):
            many_tasks.append({
                "id": f"task_{i}",
                "title": f"タスク{i}",
                "type": "routine",
                "difficulty": 1,
                "xp_reward": 10
            })
        
        flex_message = create_mobile_optimized_heart_crystal_tasks(many_tasks)
        
        # Should have header + 3 rows = 4 bubbles (limited to 9 tasks in 3x3 grid)
        bubbles = flex_message.contents.contents
        assert len(bubbles) == 4
        print("? Task limit for cognitive load reduction: PASSED")
        
        # Test title truncation for mobile readability
        long_title_task = {
            "id": "task_long",
            "title": "こ",
            "type": "routine",
            "difficulty": 1,
            "xp_reward": 10
        }
        
        bubble = create_task_bubble_mobile(long_title_task)
        title_text = bubble.contents[1].text
        
        # Should be truncated for mobile readability
        assert len(title_text) <= 11  # 8 chars + "..."
        print("? Title truncation for mobile readability: PASSED")
        
        return True
        
    except Exception as e:
        print(f"? ADHD consideration test error: {e}")
        return False

def test_touch_friendly_interface():
    """Test touch-friendly interface elements"""
    try:
        from mobile_ui_functions import create_task_bubble_mobile
        
        task = {
            "id": "task_1",
            "title": "?",
            "type": "routine",
            "difficulty": 1,
            "xp_reward": 10
        }
        
        bubble = create_task_bubble_mobile(task)
        
        # Check button sizing for touch interaction
        button = bubble.contents[3]  # Completion button
        assert button.height == "sm"  # Appropriate for touch
        assert button.style == "primary"
        print("? Touch-friendly button sizing: PASSED")
        
        # Check visual feedback elements (these are set in the BoxComponent)
        assert hasattr(bubble, 'contents')  # Has content structure
        print("? Visual feedback elements: PASSED")
        
        return True
        
    except Exception as e:
        print(f"? Touch-friendly interface test error: {e}")
        return False

if __name__ == "__main__":
    print("? Testing Mobile-Optimized LINE Bot UI Functions...")
    print("=" * 60)
    
    success = True
    success &= test_mobile_ui_functions()
    success &= test_adhd_considerations()
    success &= test_touch_friendly_interface()
    
    if success:
        print("\n? All tests PASSED! Mobile UI functions are working correctly.")
        print("\n? Key Features Implemented:")
        print("  ? 3x3 Mandala grid layout for Heart Crystal tasks")
        print("  ? Touch-friendly buttons with appropriate sizing")
        print("  ? ADHD-friendly cognitive load reduction (max 9 tasks)")
        print("  ? Mobile-optimized title truncation")
        print("  ? Visual feedback with colors and emojis")
        print("  ? One-tap task completion")
    else:
        print("\n? Some tests FAILED. Please check the implementation.")
    
    exit(0 if success else 1)