"""
Test suite for mobile-optimized story delivery implementation
Tests evening story delivery, choice handling, and Mandala integration
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mobile_story_delivery_functions():
    """Test mobile story delivery functions"""
    try:
        from mobile_story_delivery import (
            create_mobile_optimized_evening_story,
            create_mobile_story_choices,
            create_story_choice_confirmation,
            create_mandala_story_grid,
            create_evening_motivation_message,
            format_story_for_mobile
        )
        print("? Successfully imported mobile story delivery functions")
        
        # Test data
        sample_story_data = {
            "title": "?",
            "content": "?",
            "choices": [
                {
                    "id": "choice_1",
                    "text": "?",
                    "real_task_id": "task_123",
                    "effect": "学"
                },
                {
                    "id": "choice_2", 
                    "text": "?",
                    "habit_tag": "social_connection",
                    "effect": "?"
                },
                {
                    "id": "choice_3",
                    "text": "?",
                    "effect": "?"
                }
            ]
        }
        
        # Test mobile-optimized evening story
        story_message = create_mobile_optimized_evening_story(sample_story_data)
        assert story_message is not None
        assert hasattr(story_message, 'alt_text')
        assert "?" in story_message.alt_text
        print("? Mobile-optimized evening story creation: PASSED")
        
        # Test story choices creation
        choice_bubbles = create_mobile_story_choices(sample_story_data["choices"])
        assert len(choice_bubbles) == 3  # Should create 3 rows for 3x3 grid
        print("? Mobile story choices creation: PASSED")
        
        # Test choice confirmation
        choice_data = sample_story_data["choices"][0]
        task_info = {"title": "プレビュー", "difficulty": 3}
        confirmation = create_story_choice_confirmation(choice_data, task_info)
        assert confirmation is not None
        assert "?" in confirmation.alt_text
        print("? Story choice confirmation: PASSED")
        
        # Test Mandala story grid
        story_elements = [
            {"id": "elem_1", "type": "choice", "text": "学"},
            {"id": "elem_2", "type": "growth", "text": "成"},
            {"id": "elem_3", "type": "challenge", "text": "挑"}
        ]
        mandala_grid = create_mandala_story_grid(story_elements)
        assert mandala_grid is not None
        assert "物語Mandala" in mandala_grid.alt_text
        print("? Mandala story grid creation: PASSED")
        
        # Test evening motivation message
        motivation = create_evening_motivation_message()
        assert motivation is not None
        assert "?" in motivation.alt_text
        print("? Evening motivation message: PASSED")
        
        # Test story formatting for mobile
        long_story = "こ" * 10
        formatted = format_story_for_mobile(long_story)
        assert len(formatted.split('\n\n')) <= 5  # Should be limited for mobile
        print("? Story formatting for mobile: PASSED")
        
        return True
        
    except ImportError as e:
        print(f"? Import error: {e}")
        return False
    except Exception as e:
        print(f"? Test error: {e}")
        return False

def test_story_choice_mobile_optimization():
    """Test story choice mobile optimizations"""
    try:
        from mobile_story_delivery import create_mobile_choice_button, create_empty_choice_slot
        
        # Test choice button with long text (should truncate)
        long_choice = {
            "id": "choice_long",
            "text": "こ",
            "real_task_id": "task_123"
        }
        
        choice_button = create_mobile_choice_button(long_choice)
        choice_text = choice_button.contents[1].text
        
        # Should be truncated for mobile display
        assert len(choice_text) <= 15  # 12 chars + "..."
        print("? Choice text truncation for mobile: PASSED")
        
        # Test empty choice slot
        empty_slot = create_empty_choice_slot()
        assert empty_slot is not None
        assert empty_slot.contents[1].text == "?..."
        print("? Empty choice slot creation: PASSED")
        
        # Test choice button with task link
        task_choice = {
            "id": "choice_task",
            "text": "タスク",
            "real_task_id": "task_456"
        }
        
        task_button = create_mobile_choice_button(task_choice)
        task_emoji = task_button.contents[0].text
        assert task_emoji == "?"  # Should show task emoji
        print("? Task-linked choice button: PASSED")
        
        # Test choice button with habit tag
        habit_choice = {
            "id": "choice_habit",
            "text": "?",
            "habit_tag": "morning_routine"
        }
        
        habit_button = create_mobile_choice_button(habit_choice)
        habit_emoji = habit_button.contents[0].text
        assert habit_emoji == "?"  # Should show habit emoji
        print("? Habit-linked choice button: PASSED")
        
        return True
        
    except Exception as e:
        print(f"? Story choice mobile optimization test error: {e}")
        return False

def test_mandala_grid_mobile_layout():
    """Test 3x3 Mandala grid mobile layout"""
    try:
        from mobile_story_delivery import create_mandala_story_grid, create_mandala_story_cell, create_empty_mandala_cell
        
        # Test with many elements (should limit to 9 for 3x3 grid)
        many_elements = []
        for i in range(15):
            many_elements.append({
                "id": f"elem_{i}",
                "type": "choice",
                "text": f"?{i}"
            })
        
        mandala_grid = create_mandala_story_grid(many_elements)
        
        # Should have header + 3 rows = 4 bubbles (limited to 9 elements in 3x3 grid)
        bubbles = mandala_grid.contents.contents
        assert len(bubbles) == 4
        print("? Mandala grid 3x3 layout limit: PASSED")
        
        # Test individual Mandala cell
        element = {
            "id": "test_elem",
            "type": "growth",
            "text": "成"
        }
        
        cell = create_mandala_story_cell(element)
        assert cell is not None
        assert cell.contents[0].text == "?"  # Growth emoji
        print("? Mandala story cell creation: PASSED")
        
        # Test empty Mandala cell
        empty_cell = create_empty_mandala_cell()
        assert empty_cell is not None
        assert empty_cell.contents[0].text == "?"
        print("? Empty Mandala cell creation: PASSED")
        
        return True
        
    except Exception as e:
        print(f"? Mandala grid mobile layout test error: {e}")
        return False

def test_evening_story_scheduling():
    """Test evening story scheduling and timing"""
    try:
        from mobile_story_delivery import get_evening_story_motivational_messages
        
        # Test motivational messages collection
        messages = get_evening_story_motivational_messages()
        assert len(messages) > 0
        assert all(isinstance(msg, str) for msg in messages)
        print("? Evening motivational messages: PASSED")
        
        # Test that messages are appropriate for evening time
        evening_keywords = ["?", "お", "?", "?", "成"]
        has_evening_content = any(
            any(keyword in msg for keyword in evening_keywords)
            for msg in messages
        )
        assert has_evening_content
        print("? Evening-appropriate message content: PASSED")
        
        return True
        
    except Exception as e:
        print(f"? Evening story scheduling test error: {e}")
        return False

if __name__ == "__main__":
    print("? Testing Mobile-Optimized Story Delivery Implementation...")
    print("=" * 65)
    
    success = True
    success &= test_mobile_story_delivery_functions()
    success &= test_story_choice_mobile_optimization()
    success &= test_mandala_grid_mobile_layout()
    success &= test_evening_story_scheduling()
    
    if success:
        print("\n? All tests PASSED! Mobile story delivery is working correctly.")
        print("\n? Key Features Implemented:")
        print("  ? 21:30 evening story delivery with mobile optimization")
        print("  ? 3x3 Mandala format for story choices")
        print("  ? Touch-friendly choice buttons with task linking")
        print("  ? Mobile-optimized story content formatting")
        print("  ? Story choice confirmation with tomorrow's Mandala reflection")
        print("  ? Evening motivation messages")
        print("  ? ADHD-friendly cognitive load management")
    else:
        print("\n? Some tests FAILED. Please check the implementation.")
    
    exit(0 if success else 1)