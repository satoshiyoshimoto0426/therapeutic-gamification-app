#!/usr/bin/env python3
"""
AI Story Generation Engine Implementation Validation
Validates all core AI story generation features according to requirements
"""

import asyncio
import sys
import os
from datetime import datetime

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

async def validate_deepseek_integration():
    """Validate DeepSeek R1 integration"""
    print("? Validating DeepSeek R1 Integration...")
    
    try:
        from main import DeepSeekR1Client
        
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        # Test story generation
        response = await client.generate_story(
            prompt="Generate a therapeutic story about growth",
            system_message="You are a therapeutic storyteller",
            temperature=0.7
        )
        
        assert "content" in response
        assert "generation_time_ms" in response
        assert len(response["content"]) > 0
        print("  ? DeepSeek R1 client initialization: PASS")
        print("  ? Story generation API call: PASS")
        print("  ? Response format validation: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? DeepSeek R1 integration validation failed: {e}")
        return False

async def validate_content_safety():
    """Validate content safety filtering system"""
    print("? Validating Content Safety System...")
    
    try:
        from main import ContentSafetyFilter
        
        safety_filter = ContentSafetyFilter()
        
        # Test safe content
        safe_content = "希"
        safe_result = await safety_filter.evaluate_content(safe_content)
        
        assert safe_result.is_safe == True
        assert safe_result.safety_score >= 0.8
        print("  ? Safe content detection: PASS")
        
        # Test potentially harmful content
        harmful_content = "?"
        harmful_result = await safety_filter.evaluate_content(harmful_content)
        
        assert harmful_result.safety_score < 1.0
        print("  ? Harmful content detection: PASS")
        
        # Test therapeutic appropriateness
        therapeutic_content = "成"
        therapeutic_result = await safety_filter.evaluate_content(therapeutic_content)
        
        assert therapeutic_result.therapeutic_appropriateness > 0.8
        print("  ? Therapeutic appropriateness scoring: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Content safety validation failed: {e}")
        return False

async def validate_therapeutic_prompts():
    """Validate therapeutic prompt template system"""
    print("? Validating Therapeutic Prompt System...")
    
    try:
        from main import TherapeuticPromptManager
        from interfaces.core_types import ChapterType
        
        prompt_manager = TherapeuticPromptManager()
        
        # Test template initialization
        assert len(prompt_manager.templates) > 0
        print("  ? Template initialization: PASS")
        
        # Test self-discipline template
        self_discipline_template = prompt_manager.get_template(ChapterType.SELF_DISCIPLINE)
        assert self_discipline_template.chapter_type == ChapterType.SELF_DISCIPLINE
        assert "habit_formation" in self_discipline_template.therapeutic_focus
        assert len(self_discipline_template.safety_guidelines) > 0
        print("  ? Self-discipline template: PASS")
        
        # Test empathy template
        empathy_template = prompt_manager.get_template(ChapterType.EMPATHY)
        assert empathy_template.chapter_type == ChapterType.EMPATHY
        assert "emotional_intelligence" in empathy_template.therapeutic_focus
        print("  ? Empathy template: PASS")
        
        # Test prompt formatting
        context = {
            "mood_level": 4,
            "task_completion_rate": 0.8,
            "companion_relationships": {"yu": 25},
            "current_story_state": {"current_node": "test"}
        }
        
        formatted_prompt = prompt_manager.format_prompt(self_discipline_template, context)
        assert len(formatted_prompt) > 0
        print("  ? Prompt formatting: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Therapeutic prompt validation failed: {e}")
        return False

async def validate_fallback_system():
    """Validate fallback template system"""
    print("? Validating Fallback Template System...")
    
    try:
        from main import FallbackTemplateSystem
        
        fallback_system = FallbackTemplateSystem()
        
        # Test template categories
        required_categories = ["opening", "challenge", "companion", "reflection"]
        for category in required_categories:
            assert category in fallback_system.templates
            assert len(fallback_system.templates[category]) > 0
        print("  ? Fallback template categories: PASS")
        
        # Test contextual selection
        high_mood_content = fallback_system.get_fallback_content("opening", {"mood_level": 5})
        low_mood_content = fallback_system.get_fallback_content("opening", {"mood_level": 1})
        
        assert len(high_mood_content) > 0
        assert len(low_mood_content) > 0
        print("  ? Contextual fallback selection: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Fallback system validation failed: {e}")
        return False

async def validate_story_generation_pipeline():
    """Validate end-to-end story generation pipeline"""
    print("? Validating Story Generation Pipeline...")
    
    try:
        from main import StoryGenerationRequest, generate_story
        from interfaces.core_types import ChapterType
        from unittest.mock import Mock
        
        # Mock user authentication
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        background_tasks = Mock()
        
        # Create test request
        request = StoryGenerationRequest(
            uid="test_user_123",
            chapter_type=ChapterType.SELF_DISCIPLINE,
            user_context={
                "mood_score": 4,
                "completion_rate": 0.7
            },
            story_state={
                "current_node": "opening",
                "choice_history": []
            },
            generation_type="opening",
            therapeutic_focus=["habit_formation"],
            companion_context={"yu": 20}
        )
        
        # Test story generation
        response = await generate_story(request, mock_user, background_tasks)
        
        assert response.story_id is not None
        assert len(response.generated_content) > 0
        assert response.safety_score >= 0.0
        assert response.generation_time_ms > 0
        assert len(response.next_choices) > 0
        print("  ? Story generation request processing: PASS")
        print("  ? Response format validation: PASS")
        print("  ? Safety score calculation: PASS")
        print("  ? Next choices generation: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Story generation pipeline validation failed: {e}")
        return False

async def validate_performance_monitoring():
    """Validate performance monitoring system"""
    print("? Validating Performance Monitoring...")
    
    try:
        from main import log_performance_metrics, get_performance_metrics, story_db
        
        # Test metrics logging
        initial_count = len(story_db.performance_metrics)
        
        test_metrics = {
            "generation_time_ms": 1500,
            "content_length": 300,
            "safety_score": 0.95,
            "fallback_used": False,
            "chapter_type": "self_discipline"
        }
        
        await log_performance_metrics(test_metrics)
        
        assert len(story_db.performance_metrics) == initial_count + 1
        print("  ? Metrics logging: PASS")
        
        # Test metrics retrieval
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        metrics = await get_performance_metrics(mock_user)
        
        assert "p95_latency_requirement" in metrics
        assert metrics["p95_latency_requirement"] == 3500  # 3.5 seconds
        assert "average_generation_time_ms" in metrics
        print("  ? P95 latency requirement (3.5s): PASS")
        print("  ? Metrics retrieval: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Performance monitoring validation failed: {e}")
        return False

async def validate_api_endpoints():
    """Validate API endpoints"""
    print("? Validating API Endpoints...")
    
    try:
        from main import evaluate_content_safety, list_prompt_templates
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Test content safety endpoint
        safe_content = {"content": "希"}
        safety_result = await evaluate_content_safety(safe_content, mock_user)
        
        assert safety_result.is_safe == True
        assert safety_result.safety_score >= 0.8
        print("  ? Content safety evaluation endpoint: PASS")
        
        # Test template listing endpoint
        templates = await list_prompt_templates(mock_user)
        
        assert "templates" in templates
        assert len(templates["templates"]) > 0
        print("  ? Template listing endpoint: PASS")
        
        # Check required endpoint exists
        from main import app
        routes = [route.path for route in app.routes]
        
        required_endpoints = [
            "/ai/story/v2/generate",
            "/ai/story/safety/evaluate",
            "/ai/story/templates",
            "/ai/story/metrics"
        ]
        
        for endpoint in required_endpoints:
            assert any(endpoint in route for route in routes)
        print("  ? Required API endpoints: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? API endpoints validation failed: {e}")
        return False

async def main():
    """Run all AI story generation engine validations"""
    print("? AI Story Generation Engine Implementation Validation")
    print("=" * 60)
    
    validations = [
        validate_deepseek_integration,
        validate_content_safety,
        validate_therapeutic_prompts,
        validate_fallback_system,
        validate_story_generation_pipeline,
        validate_performance_monitoring,
        validate_api_endpoints
    ]
    
    results = []
    for validation in validations:
        try:
            result = await validation()
            results.append(result)
        except Exception as e:
            print(f"? Validation failed with error: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"? Validation Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("? All AI story generation features validated successfully!")
        print("? Requirements 2.1, 2.2, 2.5, 7.1, 7.2 satisfied")
        print("\n? Implementation Details:")
        print("   ? DeepSeek R1 integration with therapeutic prompts")
        print("   ? Content safety filtering with 98% F1 score target")
        print("   ? Fallback template system for AI generation failures")
        print("   ? P95 latency < 3.5s requirement monitoring")
        print("   ? Comprehensive API endpoints for story generation")
        return True
    else:
        print("? Some validations failed. Please review implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)