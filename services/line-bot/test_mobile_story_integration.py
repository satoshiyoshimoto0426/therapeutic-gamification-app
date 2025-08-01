"""
Integration tests for mobile-optimized story delivery system
Tests the complete workflow from evening story generation to user interaction
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

def test_mobile_story_delivery_integration():
    """Test complete mobile story delivery integration"""
    try:
        from mobile_story_delivery import (
            create_mobile_optimized_evening_story,
            create_mobile_story_choices,
            create_story_choice_confirmation,
            create_mandala_story_grid,
            format_story_for_mobile
        )
        
        # Test story data
        sample_story_data = {
            "title": "?",
            "content": "?",
            "choices": [
                {
                    "id": "choice_1",
                    "text": "?",
                    "real_task_id": "task_123",
                    "xp_reward": 50
                },
                {
                    "id": "choice_2", 
                    "text": "?",
                    "habit_tag": "social_connection",
                    "xp_reward": 30
                },
                {
                    "id": "choice_3",
                    "text": "創",
                    "habit_tag": "creativity",
                    "xp_reward": 40
                }
            ],
            "mandala_elements": [
                {"id": "elem_1", "type": "growth", "text": "成"},
                {"id": "elem_2", "type": "challenge", "text": "?"},
                {"id": "elem_3", "type": "connection", "text": "?"}
            ]
        }
        
        # Test mobile-optimized story creation
        story_message = create_mobile_optimized_evening_story(sample_story_data)
        assert story_message is not None
        assert hasattr(story_message, 'alt_text')
        assert "?" in story_message.alt_text
        
        # Test story content formatting for mobile
        formatted_content = format_story_for_mobile(sample_story_data["content"])
        assert len(formatted_content.split('\n\n')) <= 4  # Max 4 paragraphs for mobile
        
        # Test choice creation
        choice_bubbles = create_mobile_story_choices(sample_story_data["choices"])
        assert len(choice_bubbles) == 3  # Should create 3 rows for 3x3 grid
        
        # Test Mandala grid creation
        mandala_message = create_mandala_story_grid(sample_story_data["mandala_elements"])
        assert mandala_message is not None
        assert "? 物語Mandala" in mandala_message.alt_text
        
        # Test choice confirmation
        choice_data = sample_story_data["choices"][0]
        task_info = {"title": "プレビュー", "difficulty": 3}
        confirmation_message = create_story_choice_confirmation(choice_data, task_info)
        assert confirmation_message is not None
        assert "?" in confirmation_message.alt_text
        
        print("? Mobile story delivery integration test passed")
        return True
        
    except Exception as e:
        print(f"? Mobile story delivery integration test failed: {e}")
        return False

def test_evening_story_workflow():
    """Test complete evening story workflow"""
    try:
        # Test story workflow components without importing main functions
        from mobile_story_delivery import (
            create_mobile_optimized_evening_story,
            create_evening_motivation_message
        )
        
        # Test story data
        test_story_data = {
            "title": "?",
            "content": "?",
            "choices": [
                {"id": "test_choice", "text": "?", "real_task_id": "task_test"}
            ]
        }
        
        # Test story message creation
        story_message = create_mobile_optimized_evening_story(test_story_data)
        assert story_message is not None
        
        # Test motivation message creation
        motivation_message = create_evening_motivation_message()
        assert motivation_message is not None
        
        print("? Evening story workflow test passed")
        return True
                
    except Exception as e:
        print(f"? Evening story workflow test failed: {e}")
        return False

def test_3x3_mandala_mobile_layout():
    """Test 3x3 Mandala layout optimization for mobile"""
    try:
        from mobile_story_delivery import (
            create_mobile_story_choices,
            create_mandala_story_grid,
            create_empty_choice_slot
        )
        
        # Test with various numbers of choices
        test_cases = [
            {"choices": 1, "expected_rows": 3},  # Should pad to 3x3
            {"choices": 5, "expected_rows": 3},  # Should create 3 rows
            {"choices": 9, "expected_rows": 3},  # Perfect 3x3
            {"choices": 12, "expected_rows": 3}  # Should limit to 9 (3x3)
        ]
        
        for case in test_cases:
            # Create test choices
            choices = []
            for i in range(case["choices"]):
                choices.append({
                    "id": f"choice_{i}",
                    "text": f"?{i+1}",
                    "real_task_id": f"task_{i}"
                })
            
            # Test choice layout
            choice_bubbles = create_mobile_story_choices(choices)
            assert len(choice_bubbles) == case["expected_rows"]
            
            # Test Mandala elements
            mandala_elements = []
            for i in range(case["choices"]):
                mandala_elements.append({
                    "id": f"elem_{i}",
                    "type": "test",
                    "text": f"?{i+1}"
                })
            
            mandala_message = create_mandala_story_grid(mandala_elements)
            assert mandala_message is not None
        
        print("? 3x3 Mandala mobile layout test passed")
        return True
        
    except Exception as e:
        print(f"? 3x3 Mandala mobile layout test failed: {e}")
        return False

def test_mobile_touch_optimization():
    """Test mobile touch-friendly UI optimization"""
    try:
        from mobile_story_delivery import (
            create_mobile_choice_button,
            create_mandala_story_cell
        )
        
        # Test choice button touch optimization
        choice_data = {
            "id": "test_choice",
            "text": "こ",  # Long text for truncation test
            "real_task_id": "task_123"
        }
        
        choice_button = create_mobile_choice_button(choice_data)
        assert choice_button is not None
        
        # Check text truncation for mobile
        text_component = None
        for content in choice_button.contents:
            if hasattr(content, 'text') and "こ" in content.text:
                text_component = content
                break
        
        assert text_component is not None
        assert len(text_component.text) <= 15  # Should be truncated
        
        # Test Mandala cell touch optimization
        element_data = {
            "id": "test_element",
            "type": "growth",
            "text": "成"
        }
        
        mandala_cell = create_mandala_story_cell(element_data)
        assert mandala_cell is not None
        assert hasattr(mandala_cell, 'action')  # Should have touch action
        
        print("? Mobile touch optimization test passed")
        return True
        
    except Exception as e:
        print(f"? Mobile touch optimization test failed: {e}")
        return False

def test_story_task_integration():
    """Test story choice to task integration"""
    try:
        from mobile_story_delivery import create_story_choice_confirmation
        
        # Test choice with real task
        choice_with_task = {
            "id": "choice_task",
            "text": "?",
            "real_task_id": "task_123"
        }
        
        task_info = {
            "title": "Python学",
            "difficulty": 3,
            "type": "skill_up"
        }
        
        confirmation_message = create_story_choice_confirmation(choice_with_task, task_info)
        assert confirmation_message is not None
        
        # Test choice with habit tag
        choice_with_habit = {
            "id": "choice_habit",
            "text": "?",
            "habit_tag": "daily_exercise"
        }
        
        confirmation_message_habit = create_story_choice_confirmation(choice_with_habit)
        assert confirmation_message_habit is not None
        
        print("? Story task integration test passed")
        return True
        
    except Exception as e:
        print(f"? Story task integration test failed: {e}")
        return False

def test_evening_story_scheduling():
    """Test evening story scheduling and timing"""
    try:
        from mobile_story_delivery import get_evening_story_motivational_messages
        
        # Test motivational messages collection
        messages = get_evening_story_motivational_messages()
        assert len(messages) > 0
        assert all(isinstance(msg, str) for msg in messages)
        assert all(len(msg) > 10 for msg in messages)  # Reasonable message length
        
        # Test that all messages are encouraging and positive
        positive_keywords = ["成", "?", "?", "?", "?", "お", "一般", "?", "?", "?", "?"]
        for i, message in enumerate(messages):
            has_positive = any(keyword in message for keyword in positive_keywords)
            if not has_positive:
                print(f"Message {i}: {message}")
            assert has_positive, f"Message lacks positive keywords: {message}"
        
        print("? Evening story scheduling test passed")
        return True
        
    except Exception as e:
        print(f"? Evening story scheduling test failed: {e}")
        return False

def run_all_tests():
    """Run all mobile story delivery integration tests"""
    print("? Running mobile story delivery integration tests...")
    
    success = True
    success &= test_mobile_story_delivery_integration()
    success &= test_3x3_mandala_mobile_layout()
    success &= test_mobile_touch_optimization()
    success &= test_story_task_integration()
    success &= test_evening_story_scheduling()
    
    # Run workflow test
    success &= test_evening_story_workflow()
    
    if success:
        print("? All mobile story delivery integration tests passed!")
    else:
        print("? Some mobile story delivery integration tests failed")
    
    return success

if __name__ == "__main__":
    run_all_tests()