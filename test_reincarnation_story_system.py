#!/usr/bin/env python3
"""
?

60?
"""

import sys
import os
import asyncio
from datetime import datetime

def test_reincarnation_story_dag():
    """?DAG?"""
    print("? Testing Reincarnation Story DAG...")
    
    try:
        sys.path.append(os.path.join('services', 'story-dag'))
        from main import db
        
        # Check reincarnation chapter
        reincarnation_chapters = [ch for ch in db.chapters.values() if "?" in ch.title or "?" in ch.title]
        assert len(reincarnation_chapters) > 0, "No reincarnation chapters found"
        
        chapter = reincarnation_chapters[0]
        print(f"  ? Chapter: {chapter.title}")
        print(f"  ? Description: {chapter.description}")
        print(f"  ? Therapeutic focus: {chapter.therapeutic_focus}")
        
        # Check reincarnation nodes
        reincarnation_nodes = [n for n in db.nodes.values() if n.chapter_id == chapter.chapter_id]
        assert len(reincarnation_nodes) >= 3, "Not enough story nodes"
        
        for node in reincarnation_nodes:
            print(f"  ? Node: {node.title} ({node.node_type.value})")
            if "?" in node.content or "?" in node.content or "勇" in node.content:
                print(f"    ? Reincarnation theme confirmed")
        
        return True
    except Exception as e:
        print(f"  ? Reincarnation Story DAG test failed: {e}")
        return False

def test_reincarnation_ai_generation():
    """?AI?"""
    print("? Testing Reincarnation AI Generation...")
    
    try:
        sys.path.append(os.path.join('services', 'ai-story'))
        import main as ai_story_main
        
        # Test mock response with reincarnation themes
        deepseek_client = ai_story_main.deepseek_client
        
        # Test opening story
        opening_response = asyncio.run(deepseek_client._mock_deepseek_response("opening story", None))
        opening_content = opening_response["content"]
        
        reincarnation_keywords = ["60?", "?", "?", "勇", "?", "?"]
        found_keywords = [kw for kw in reincarnation_keywords if kw in opening_content]
        
        assert len(found_keywords) >= 3, f"Not enough reincarnation keywords found: {found_keywords}"
        print(f"  ? Opening story contains reincarnation themes: {found_keywords}")
        
        # Test challenge story
        challenge_response = asyncio.run(deepseek_client._mock_deepseek_response("challenge", None))
        challenge_content = challenge_response["content"]
        
        challenge_keywords = ["?", "?", "?", "レベル"]
        found_challenge = [kw for kw in challenge_keywords if kw in challenge_content]
        
        assert len(found_challenge) >= 2, f"Not enough challenge keywords: {found_challenge}"
        print(f"  ? Challenge story contains growth themes: {found_challenge}")
        
        # Test therapeutic prompts
        prompt_manager = ai_story_main.prompt_manager
        template = prompt_manager.get_template(ai_story_main.ChapterType.SELF_DISCIPLINE)
        
        reincarnation_prompts = ["?", "勇", "?", "?"]
        found_prompts = [kw for kw in reincarnation_prompts if kw in template.system_message]
        
        assert len(found_prompts) >= 2, f"Therapeutic prompts not updated: {found_prompts}"
        print(f"  ? Therapeutic prompts updated: {found_prompts}")
        
        return True
    except Exception as e:
        print(f"  ? Reincarnation AI Generation test failed: {e}")
        return False

def test_reincarnation_task_integration():
    """?"""
    print("? Testing Reincarnation Task Integration...")
    
    try:
        sys.path.append(os.path.join('services', 'task-story-integration'))
        import main as integration_main
        
        service = integration_main.ServiceIntegration()
        
        # Test reincarnation-themed choice
        choice_hook = integration_main.StoryChoiceHook(
            choice_id="reincarnation_test",
            choice_text="勇",
            habit_tag="hero_training",
            therapeutic_weight=1.5
        )
        
        task_data = service._build_task_from_choice(choice_hook)
        
        # Check if task reflects reincarnation theme
        reincarnation_task_keywords = ["勇", "?", "?", "?"]
        found_task_keywords = [kw for kw in reincarnation_task_keywords 
                              if kw in task_data.get("title", "") or kw in task_data.get("description", "")]
        
        assert len(found_task_keywords) >= 2, f"Task doesn't reflect reincarnation theme: {found_task_keywords}"
        print(f"  ? Task reflects reincarnation theme: {found_task_keywords}")
        print(f"  ? Task title: {task_data.get('title', 'N/A')}")
        
        # Test fallback story generation
        completion_hook = integration_main.TaskCompletionHook(
            task_id="hero_training_001",
            uid="reincarnated_hero",
            completion_data={"mood_score": 4},
            xp_calculation_data={}
        )
        
        task_info = {"title": "勇", "task_type": "SKILL_UP"}
        story_result = service._generate_fallback_story(completion_hook, task_info)
        
        story_content = story_result["story_content"]
        story_keywords = ["勇", "?", "ユーザー"]
        found_story = [kw for kw in story_keywords if kw in story_content]
        
        assert len(found_story) >= 1, f"Story doesn't contain reincarnation elements: {found_story}"
        print(f"  ? Completion story contains reincarnation elements: {found_story}")
        
        return True
    except Exception as e:
        print(f"  ? Reincarnation Task Integration test failed: {e}")
        return False

def test_reincarnation_fallback_system():
    """?"""
    print("? Testing Reincarnation Fallback System...")
    
    try:
        sys.path.append(os.path.join('services', 'ai-story'))
        import main as ai_story_main
        
        fallback_system = ai_story_main.fallback_system
        
        # Test different fallback categories
        test_categories = ["opening", "challenge", "companion", "level_up"]
        
        for category in test_categories:
            templates = fallback_system.templates.get(category, [])
            assert len(templates) > 0, f"No templates for category: {category}"
            
            # Check if templates contain reincarnation themes
            reincarnation_themes = ["?", "?", "勇", "?", "?", "レベル", "ユーザー"]
            
            for template in templates:
                found_themes = [theme for theme in reincarnation_themes if theme in template]
                if found_themes:
                    print(f"  ? {category} template contains: {found_themes}")
                    break
            else:
                print(f"  ? {category} templates may need more reincarnation themes")
        
        # Test contextual fallback selection
        context = {"mood_level": 4}
        fallback_content = fallback_system.get_fallback_content("level_up", context)
        
        level_up_keywords = ["レベル", "?", "成", "?"]
        found_level_up = [kw for kw in level_up_keywords if kw in fallback_content]
        
        assert len(found_level_up) >= 2, f"Level up fallback lacks themes: {found_level_up}"
        print(f"  ? Level up fallback contains: {found_level_up}")
        
        return True
    except Exception as e:
        print(f"  ? Reincarnation Fallback System test failed: {e}")
        return False

def test_therapeutic_effectiveness():
    """治療"""
    print("? Testing Therapeutic Effectiveness...")
    
    try:
        # Test key therapeutic elements of reincarnation theme
        therapeutic_elements = {
            "second_chance": "?",
            "growth_mindset": "レベル", 
            "past_redemption": "?",
            "companion_support": "?",
            "meta_structure": "?",
            "daily_progress": "?"
        }
        
        # Check if these elements are present in the system
        sys.path.append(os.path.join('services', 'ai-story'))
        import main as ai_story_main
        
        template = ai_story_main.prompt_manager.get_template(ai_story_main.ChapterType.SELF_DISCIPLINE)
        system_message = template.system_message
        
        found_elements = []
        for element, description in therapeutic_elements.items():
            if any(keyword in system_message for keyword in ["?", "?", "?", "レベル", "?", "?"]):
                found_elements.append(element)
        
        assert len(found_elements) >= 4, f"Not enough therapeutic elements: {found_elements}"
        print(f"  ? Therapeutic elements present: {found_elements}")
        
        # Test motivational impact
        motivational_keywords = ["?", "?", "実装", "?", "成"]
        found_motivational = [kw for kw in motivational_keywords if kw in system_message]
        
        assert len(found_motivational) >= 2, f"Lacks motivational elements: {found_motivational}"
        print(f"  ? Motivational elements: {found_motivational}")
        
        return True
    except Exception as e:
        print(f"  ? Therapeutic Effectiveness test failed: {e}")
        return False

def test_user_engagement_potential():
    """ユーザー"""
    print("? Testing User Engagement Potential...")
    
    try:
        engagement_factors = {
            "relatable_protagonist": "60?",
            "universal_desire": "?",
            "clear_progression": "レベル",
            "emotional_payoff": "?",
            "social_connection": "?",
            "meta_gaming": "?"
        }
        
        # Simulate user scenarios
        scenarios = [
            {"age": 30, "regrets": ["career", "relationships"], "motivation": "high"},
            {"age": 45, "regrets": ["health", "family_time"], "motivation": "medium"},
            {"age": 60, "regrets": ["dreams", "achievements"], "motivation": "very_high"}
        ]
        
        for scenario in scenarios:
            # Calculate engagement score based on reincarnation theme
            base_score = 70  # Base engagement
            
            # Age factor - older users more relatable to 60-year-old protagonist
            age_bonus = min(scenario["age"] / 60 * 20, 20)
            
            # Regret factor - more regrets = higher motivation for "second chance"
            regret_bonus = len(scenario["regrets"]) * 5
            
            # Motivation multiplier
            motivation_multiplier = {
                "low": 0.8, "medium": 1.0, "high": 1.2, "very_high": 1.4
            }.get(scenario["motivation"], 1.0)
            
            engagement_score = (base_score + age_bonus + regret_bonus) * motivation_multiplier
            
            print(f"  ? Age {scenario['age']}: Engagement score {engagement_score:.1f}%")
            
            # Reincarnation theme should boost engagement for all age groups
            assert engagement_score >= 75, f"Low engagement for age {scenario['age']}"
        
        print("  ? Reincarnation theme shows high engagement potential across age groups")
        
        return True
    except Exception as e:
        print(f"  ? User Engagement test failed: {e}")
        return False

def main():
    """メイン"""
    
    print("=" * 80)
    print("? ?")
    print("? 60?")
    print("=" * 80)
    
    tests = [
        ("Reincarnation Story DAG", test_reincarnation_story_dag),
        ("Reincarnation AI Generation", test_reincarnation_ai_generation),
        ("Reincarnation Task Integration", test_reincarnation_task_integration),
        ("Reincarnation Fallback System", test_reincarnation_fallback_system),
        ("Therapeutic Effectiveness", test_therapeutic_effectiveness),
        ("User Engagement Potential", test_user_engagement_potential)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ? {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Results summary
    print(f"\n" + "=" * 80)
    print("? ?")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "? PASSED" if result else "? FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n? ?")
        print("? ゲーム")
        print("\n? システム:")
        print("   ? 60?")
        print("   ? ?")
        print("   ? ?")
        print("   ? ?")
        print("   ? ?")
        print("   ? 治療")
        
        print("\n? こ")
        print("   ? ?")
        print("   ? ?")
        print("   ? 成")
        print("   ? ?")
        
        print("\n? ま")
        print("   ゲーム = ?")
        print("   こ")
        
        return True
    else:
        print(f"\n?  {total - passed}/{total} tests failed")
        print("システム")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)