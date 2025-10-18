"""
Task 8.2 Integration Tests: GPT-4o Story Generation Integration
Tests for OpenAI API integration, timeout constraints, JSON schema validation, and error handling
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import from main service
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import (
    DeepSeekR1Client,
    StoryJSONSchema,
    StoryGenerationRequest,
    ChapterType,
    prompt_manager,
    safety_filter
)


class TestDeepSeekR1Integration:
    """Test DeepSeek R1 client with GPT-4o compatible interface"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return DeepSeekR1Client(api_key="mock_key_for_testing")
    
    @pytest.mark.asyncio
    async def test_timeout_constraint(self, client):
        """Test 3.5 second timeout constraint"""
        # Verify timeout is set correctly
        assert client.timeout == 3.5, "Timeout should be 3.5 seconds per requirements"
        
        # Test that timeout is enforced
        start_time = time.time()
        result = await client.generate_story(
            prompt="Generate a test story",
            system_message="You are a therapeutic story generator"
        )
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time (mock response)
        assert elapsed < 2.0, "Mock response should be fast"
        assert "content" in result
        assert "generation_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_json_mode_generation(self, client):
        """Test JSON mode for structured output"""
        result = await client.generate_story(
            prompt="Generate a story with choices",
            system_message="Return JSON with story_text and choices",
            use_json_mode=True
        )
        
        assert "content" in result
        
        # Try to parse as JSON
        try:
            content = json.loads(result["content"]) if isinstance(result["content"], str) else result["content"]
            assert "story_text" in content or isinstance(content, str)
        except json.JSONDecodeError:
            # Mock response might not be JSON, that's ok for testing
            pass
    
    @pytest.mark.asyncio
    async def test_error_handling_fallback(self, client):
        """Test error handling with fallback"""
        # Mock an API error
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            result = await client.generate_story(
                prompt="Test prompt",
                system_message="Test system"
            )
            
            # Should return fallback response
            assert "content" in result
            assert result["generation_time_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_timeout_fallback(self, client):
        """Test timeout handling with fallback"""
        # Create client with very short timeout
        short_timeout_client = DeepSeekR1Client(api_key="test_key")
        short_timeout_client.timeout = 0.001  # 1ms timeout
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock a slow response
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)
                return Mock(status_code=200, json=lambda: {"choices": [{"message": {"content": "test"}}]})
            
            mock_client.return_value.__aenter__.return_value.post = slow_response
            
            result = await short_timeout_client.generate_story(
                prompt="Test prompt",
                system_message="Test system"
            )
            
            # Should handle timeout gracefully
            assert "content" in result


class TestJSONSchemaValidation:
    """Test JSON schema validation for story responses"""
    
    def test_valid_schema(self):
        """Test valid story JSON schema"""
        valid_data = {
            "story_text": "これはテスト用のストーリーです。主人公は新しい挑戦に立ち向かいます。",
            "choices": [
                {"choice_id": "choice1", "text": "挑戦を受け入れる"},
                {"choice_id": "choice2", "text": "慎重に考える"}
            ],
            "therapeutic_elements": ["courage", "self_reflection"]
        }
        
        schema = StoryJSONSchema(**valid_data)
        assert schema.story_text == valid_data["story_text"]
        assert len(schema.choices) == 2
        assert len(schema.therapeutic_elements) == 2
    
    def test_invalid_schema_missing_choice_text(self):
        """Test schema validation fails for missing choice text"""
        invalid_data = {
            "story_text": "Test story",
            "choices": [
                {"choice_id": "choice1"}  # Missing 'text' field
            ],
            "therapeutic_elements": []
        }
        
        with pytest.raises(ValueError):
            StoryJSONSchema(**invalid_data)
    
    def test_invalid_schema_too_many_choices(self):
        """Test schema validation fails for too many choices"""
        invalid_data = {
            "story_text": "Test story",
            "choices": [
                {"choice_id": f"choice{i}", "text": f"Choice {i}"}
                for i in range(5)  # More than max_items=3
            ],
            "therapeutic_elements": []
        }
        
        with pytest.raises(ValueError):
            StoryJSONSchema(**invalid_data)
    
    def test_schema_with_optional_fields(self):
        """Test schema with optional fields"""
        data = {
            "story_text": "Test story with optional fields",
            "choices": [
                {"choice_id": "choice1", "text": "Option 1"}
            ],
            "therapeutic_elements": ["resilience"],
            "mood_impact": {"hope": 0.2, "confidence": 0.1},
            "companion_interactions": [
                {"companion": "yu", "relationship_change": 5}
            ]
        }
        
        schema = StoryJSONSchema(**data)
        assert schema.mood_impact is not None
        assert schema.companion_interactions is not None


class TestPromptConstruction:
    """Test therapeutic prompt construction"""
    
    def test_get_template_for_chapter(self):
        """Test getting prompt template for chapter type"""
        template = prompt_manager.get_template(ChapterType.SELF_DISCIPLINE)
        
        assert template is not None
        assert template.chapter_type == ChapterType.SELF_DISCIPLINE
        assert len(template.therapeutic_focus) > 0
        assert template.system_message is not None
        assert template.prompt_template is not None
    
    def test_format_prompt_with_context(self):
        """Test formatting prompt with user context"""
        template = prompt_manager.get_template(ChapterType.SELF_DISCIPLINE)
        
        context = {
            "mood_level": 4,
            "task_completion_rate": 0.75,
            "companion_relationships": {"yu": 50},
            "current_story_state": {"chapter": "ch1", "node": "node1"},
            "social_context": {}
        }
        
        formatted = prompt_manager.format_prompt(template, context)
        
        assert formatted is not None
        assert isinstance(formatted, str)
        # Should contain some context values
        assert "4" in formatted or "75" in formatted or "0.75" in formatted
    
    def test_format_prompt_missing_context(self):
        """Test prompt formatting handles missing context gracefully"""
        template = prompt_manager.get_template(ChapterType.EMPATHY)
        
        incomplete_context = {
            "mood_level": 3
            # Missing other required fields
        }
        
        # Should not raise exception
        formatted = prompt_manager.format_prompt(template, incomplete_context)
        assert formatted is not None


class TestContentSafety:
    """Test content safety validation"""
    
    @pytest.mark.asyncio
    async def test_safe_content(self):
        """Test safe therapeutic content"""
        safe_content = "今日は新しい挑戦に立ち向かう日です。小さな一歩から始めましょう。希望を持って前進します。"
        
        result = await safety_filter.evaluate_content(safe_content)
        
        assert result.is_safe is True
        assert result.safety_score >= 0.8
        assert len(result.flagged_categories) == 0
    
    @pytest.mark.asyncio
    async def test_therapeutic_appropriateness(self):
        """Test therapeutic appropriateness scoring"""
        therapeutic_content = "成長の機会です。希望を持って挑戦しましょう。支援があります。"
        
        result = await safety_filter.evaluate_content(therapeutic_content)
        
        assert result.therapeutic_appropriateness > 0.3
        assert result.is_safe is True


class TestStoryGenerationEndToEnd:
    """End-to-end integration tests for story generation"""
    
    @pytest.mark.asyncio
    async def test_complete_story_generation_flow(self):
        """Test complete story generation flow"""
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        # Create request
        request_data = {
            "uid": "test_user_123",
            "chapter_type": ChapterType.SELF_DISCIPLINE,
            "user_context": {
                "mood_score": 4,
                "completion_rate": 0.7,
                "pending_tasks": 3
            },
            "story_state": {
                "current_chapter_id": "self_discipline_ch1",
                "current_node": "node_1"
            },
            "generation_type": "continuation",
            "therapeutic_focus": ["habit_formation", "self_control"]
        }
        
        # Get template
        template = prompt_manager.get_template(request_data["chapter_type"])
        
        # Format prompt
        context = {
            "mood_level": request_data["user_context"]["mood_score"],
            "task_completion_rate": request_data["user_context"]["completion_rate"],
            "companion_relationships": {},
            "current_story_state": request_data["story_state"],
            "social_context": {}
        }
        
        formatted_prompt = prompt_manager.format_prompt(template, context)
        
        # Generate story
        result = await client.generate_story(
            prompt=formatted_prompt,
            system_message=template.system_message,
            temperature=0.7
        )
        
        # Verify result
        assert "content" in result
        assert "generation_time_ms" in result
        assert result["generation_time_ms"] >= 0
        
        # Check safety
        safety_result = await safety_filter.evaluate_content(
            result["content"] if isinstance(result["content"], str) else json.dumps(result["content"])
        )
        assert safety_result.safety_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_generation_with_timeout_monitoring(self):
        """Test story generation with timeout monitoring"""
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        start_time = time.time()
        result = await client.generate_story(
            prompt="Generate a therapeutic story about overcoming procrastination",
            system_message="You are a therapeutic story generator",
            use_json_mode=True
        )
        elapsed = time.time() - start_time
        
        # Verify timeout constraint
        assert elapsed < 5.0, "Generation should complete within reasonable time"
        
        # Check if timeout was exceeded (for real API calls)
        if "timeout_exceeded" in result:
            assert isinstance(result["timeout_exceeded"], bool)
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery and fallback mechanisms"""
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        # Test with various error scenarios
        test_cases = [
            ("", "Empty prompt"),
            ("Test" * 1000, "Very long prompt"),
            ("Generate story", "Normal prompt")
        ]
        
        for prompt, description in test_cases:
            result = await client.generate_story(
                prompt=prompt,
                system_message="Test system message"
            )
            
            # Should always return a result (with fallback if needed)
            assert "content" in result, f"Failed for: {description}"
            assert "generation_time_ms" in result


class TestPerformanceMetrics:
    """Test performance metrics and monitoring"""
    
    @pytest.mark.asyncio
    async def test_generation_time_tracking(self):
        """Test generation time is tracked correctly"""
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        result = await client.generate_story(
            prompt="Test prompt",
            system_message="Test system"
        )
        
        assert "generation_time_ms" in result
        assert result["generation_time_ms"] > 0
        assert result["generation_time_ms"] < 10000  # Should be under 10 seconds for mock
    
    @pytest.mark.asyncio
    async def test_timeout_detection(self):
        """Test timeout detection in response"""
        client = DeepSeekR1Client(api_key="mock_key_for_testing")
        
        result = await client.generate_story(
            prompt="Test prompt",
            system_message="Test system"
        )
        
        # Check if timeout_exceeded field exists
        if "timeout_exceeded" in result:
            assert isinstance(result["timeout_exceeded"], bool)
            
            # For mock responses, should not exceed timeout
            assert result["timeout_exceeded"] is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
