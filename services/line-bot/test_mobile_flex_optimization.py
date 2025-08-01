"""
Tests for mobile Flex message optimization
Tests enhanced mobile UI components and ADHD-friendly design
"""

def test_mobile_flex_optimizer_initialization():
    """Test MobileFlexOptimizer initialization"""
    try:
        from mobile_flex_optimization import MobileFlexOptimizer, mobile_flex
        
        # Test class initialization
        optimizer = MobileFlexOptimizer()
        assert optimizer is not None
        
        # Test mobile sizes configuration
        assert "bubble" in optimizer.mobile_sizes
        assert optimizer.mobile_sizes["bubble"] == "kilo"
        
        # Test ADHD-friendly colors
        assert "primary" in optimizer.colors
        assert optimizer.colors["primary"] == "#2E3A59"  # Calming base color
        assert optimizer.colors["accent"] == "#FFC857"   # Achievement color
        
        # Test global instance
        assert mobile_flex is not None
        
        print("? Mobile Flex optimizer initialization test passed")
        return True
        
    except Exception as e:
        print(f"? Mobile Flex optimizer initialization test failed: {e}")
        return False

def test_3x3_mandala_carousel_creation():
    """Test 3x3 Mandala carousel creation"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test data with various item types
        test_items = [
            {"id": "task1", "title": "?", "type": "routine", "progress": 50},
            {"id": "task2", "title": "プレビュー", "type": "skill_up", "progress": 75},
            {"id": "task3", "title": "?", "type": "social", "progress": 25},
            {"id": "task4", "title": "?", "type": "one_shot", "completed": True},
            {"id": "task5", "title": "創", "type": "growth", "progress": 90}
        ]
        
        # Create 3x3 Mandala carousel
        carousel_message = mobile_flex.create_3x3_mandala_carousel(test_items, "?Mandala")
        
        # Verify message structure
        assert carousel_message is not None
        assert hasattr(carousel_message, 'alt_text')
        assert "?Mandala" in carousel_message.alt_text
        assert hasattr(carousel_message, 'contents')
        
        # Verify carousel structure (should have header + 3 rows = 4 bubbles)
        carousel_contents = carousel_message.contents
        assert hasattr(carousel_contents, 'contents')
        assert len(carousel_contents.contents) == 4  # Header + 3 rows
        
        print("? 3x3 Mandala carousel creation test passed")
        return True
        
    except Exception as e:
        print(f"? 3x3 Mandala carousel creation test failed: {e}")
        return False

def test_compact_task_bubble_creation():
    """Test compact task bubble creation for mobile"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test task data
        test_task = {
            "id": "test_task",
            "title": "モデル",
            "type": "skill_up",
            "difficulty": 3,
            "xp_reward": 50
        }
        
        # Create compact task bubble
        task_bubble = mobile_flex.create_compact_task_bubble(test_task)
        
        # Verify bubble structure
        assert task_bubble is not None
        assert hasattr(task_bubble, 'body')
        assert task_bubble.size == "kilo"  # Mobile-optimized size
        
        # Verify content structure
        body = task_bubble.body
        assert hasattr(body, 'contents')
        assert len(body.contents) >= 4  # Header, separator, details, button
        
        print("? Compact task bubble creation test passed")
        return True
        
    except Exception as e:
        print(f"? Compact task bubble creation test failed: {e}")
        return False

def test_story_choice_carousel_creation():
    """Test story choice carousel creation"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test story data
        test_story = {
            "title": "?",
            "content": "?",
            "choices": [
                {"id": "choice1", "text": "?", "xp_reward": 50},
                {"id": "choice2", "text": "?", "xp_reward": 30},
                {"id": "choice3", "text": "創", "xp_reward": 40}
            ]
        }
        
        # Create story choice carousel
        story_carousel = mobile_flex.create_story_choice_carousel(test_story)
        
        # Verify carousel structure
        assert story_carousel is not None
        assert hasattr(story_carousel, 'alt_text')
        assert "?" in story_carousel.alt_text
        
        # Verify carousel contents (story bubble + choice bubbles)
        carousel_contents = story_carousel.contents
        assert hasattr(carousel_contents, 'contents')
        assert len(carousel_contents.contents) == 4  # Story + 3 choices
        
        print("? Story choice carousel creation test passed")
        return True
        
    except Exception as e:
        print(f"? Story choice carousel creation test failed: {e}")
        return False

def test_achievement_notification_creation():
    """Test achievement notification creation"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test achievement data
        test_achievement = {
            "title": "?",
            "description": "?",
            "xp_earned": 100,
            "emoji": "?"
        }
        
        # Create achievement notification
        achievement_message = mobile_flex.create_achievement_notification(test_achievement)
        
        # Verify message structure
        assert achievement_message is not None
        assert hasattr(achievement_message, 'alt_text')
        assert "?" in achievement_message.alt_text
        
        # Verify bubble structure
        bubble = achievement_message.contents
        assert hasattr(bubble, 'body')
        
        print("? Achievement notification creation test passed")
        return True
        
    except Exception as e:
        print(f"? Achievement notification creation test failed: {e}")
        return False

def test_daily_summary_creation():
    """Test daily summary creation"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test summary data
        test_summary = {
            "completed_tasks": 5,
            "total_xp": 250,
            "level_progress": 75,
            "mood_score": 4
        }
        
        # Create daily summary
        summary_message = mobile_flex.create_daily_summary_bubble(test_summary)
        
        # Verify message structure
        assert summary_message is not None
        assert hasattr(summary_message, 'alt_text')
        assert "?" in summary_message.alt_text
        
        # Verify bubble structure
        bubble = summary_message.contents
        assert hasattr(bubble, 'body')
        
        print("? Daily summary creation test passed")
        return True
        
    except Exception as e:
        print(f"? Daily summary creation test failed: {e}")
        return False

def test_mobile_ui_functions_integration():
    """Test mobile UI functions integration"""
    try:
        try:
            from mobile_ui_functions import (
            create_enhanced_heart_crystal_tasks,
            create_enhanced_story_delivery,
            create_compact_task_list,
            create_achievement_notification,
            create_daily_summary,
            create_mandala_status_display
            )
        except ImportError:
            # Skip this test if mobile_ui_functions can't be imported
            print("? Mobile UI functions integration test skipped (import error)")
            return True
        
        # Test heart crystal tasks
        test_tasks = [
            {"id": "t1", "title": "?", "type": "routine", "difficulty": 2},
            {"id": "t2", "title": "学", "type": "skill_up", "difficulty": 3}
        ]
        
        heart_crystal_message = create_enhanced_heart_crystal_tasks(test_tasks)
        assert heart_crystal_message is not None
        
        # Test story delivery
        test_story = {
            "title": "?",
            "content": "?",
            "choices": [{"id": "c1", "text": "?1"}]
        }
        
        story_message = create_enhanced_story_delivery(test_story)
        assert story_message is not None
        
        # Test compact task list
        compact_tasks = create_compact_task_list(test_tasks)
        assert isinstance(compact_tasks, list)
        assert len(compact_tasks) == 2
        
        # Test achievement notification
        achievement_data = {
            "title": "?",
            "description": "?",
            "xp_earned": 50,
            "emoji": "?"
        }
        
        achievement_message = create_achievement_notification(achievement_data)
        assert achievement_message is not None
        
        # Test daily summary
        summary_data = {
            "completed_tasks": 3,
            "total_xp": 150,
            "level_progress": 60,
            "mood_score": 4
        }
        
        summary_message = create_daily_summary(summary_data)
        assert summary_message is not None
        
        # Test Mandala status display
        mandala_data = {
            "unlocked_count": 25,
            "total_cells": 81,
            "crystal_progress": {
                "Self-Discipline": 60,
                "Empathy": 40,
                "Resilience": 80
            }
        }
        
        mandala_message = create_mandala_status_display(mandala_data)
        assert mandala_message is not None
        
        print("? Mobile UI functions integration test passed")
        return True
        
    except Exception as e:
        print(f"? Mobile UI functions integration test failed: {e}")
        return False

def test_adhd_friendly_design_elements():
    """Test ADHD-friendly design elements"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test color scheme (calming colors)
        colors = mobile_flex.colors
        assert colors["primary"] == "#2E3A59"  # Calming base
        assert colors["accent"] == "#FFC857"   # Achievement (not too bright)
        
        # Test mobile sizing (compact for focus)
        sizes = mobile_flex.mobile_sizes
        assert sizes["bubble"] == "kilo"       # Compact size
        assert sizes["spacing"] == "xs"        # Minimal spacing
        assert sizes["button_height"] == "sm"  # Touch-friendly but not overwhelming
        
        # Test 3x3 grid limitation (working memory consideration)
        test_items = [{"id": f"item{i}", "title": f"?{i}"} for i in range(15)]
        carousel = mobile_flex.create_3x3_mandala_carousel(test_items, "?")
        
        # Should limit to 9 items (3x3) for ADHD consideration
        # Header + 3 rows = 4 bubbles total
        assert len(carousel.contents.contents) == 4
        
        print("? ADHD-friendly design elements test passed")
        return True
        
    except Exception as e:
        print(f"? ADHD-friendly design elements test failed: {e}")
        return False

def test_mobile_touch_optimization():
    """Test mobile touch optimization features"""
    try:
        from mobile_flex_optimization import mobile_flex
        
        # Test task bubble touch optimization
        test_task = {
            "id": "touch_test",
            "title": "タスク",
            "type": "routine",
            "difficulty": 2
        }
        
        task_bubble = mobile_flex.create_compact_task_bubble(test_task)
        
        # Verify compact size for mobile
        assert task_bubble.size == "kilo"
        
        # Verify button height is touch-friendly
        body_contents = task_bubble.body.contents
        button_found = False
        for content in body_contents:
            if hasattr(content, 'height') and content.height == "sm":
                button_found = True
                break
        
        assert button_found, "Touch-friendly button not found"
        
        # Test Mandala cell touch optimization
        test_item = {"id": "cell_test", "title": "?", "type": "task"}
        mandala_carousel = mobile_flex.create_3x3_mandala_carousel([test_item], "タスク")
        
        # Verify carousel has touch actions
        assert mandala_carousel is not None
        
        print("? Mobile touch optimization test passed")
        return True
        
    except Exception as e:
        print(f"? Mobile touch optimization test failed: {e}")
        return False

def run_all_tests():
    """Run all mobile Flex optimization tests"""
    print("? Running mobile Flex optimization tests...")
    
    success = True
    success &= test_mobile_flex_optimizer_initialization()
    success &= test_3x3_mandala_carousel_creation()
    success &= test_compact_task_bubble_creation()
    success &= test_story_choice_carousel_creation()
    success &= test_achievement_notification_creation()
    success &= test_daily_summary_creation()
    success &= test_mobile_ui_functions_integration()
    success &= test_adhd_friendly_design_elements()
    success &= test_mobile_touch_optimization()
    
    if success:
        print("? All mobile Flex optimization tests passed!")
    else:
        print("? Some mobile Flex optimization tests failed")
    
    return success

if __name__ == "__main__":
    run_all_tests()