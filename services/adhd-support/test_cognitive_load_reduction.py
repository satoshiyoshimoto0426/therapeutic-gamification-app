#!/usr/bin/env python3
"""
ADHD支援 - ?
タスク10.1: ?

?3.1: ?
?3.3: BIZ UDGothic?
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path to import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CognitiveLoadReducer, UIConstraintValidator

class TestCognitiveLoadReducer:
    """?"""
    
    def setup_method(self):
        """?"""
        self.reducer = CognitiveLoadReducer()
    
    @pytest.mark.asyncio
    async def test_one_screen_one_action_validation_success(self):
        """? - 成"""
        screen_config = {
            "screen_id": "test_screen_1",
            "primary_actions": [{"type": "submit", "label": "?"}],
            "simultaneous_inputs": 1,
            "visual_elements": 3
        }
        
        result = await self.reducer.validate_one_screen_one_action(screen_config)
        
        assert result["is_valid"] == True
        assert result["constraint_type"] == "one_screen_one_action"
        assert len(result["violations"]) == 0
        assert result["screen_id"] == "test_screen_1"
    
    @pytest.mark.asyncio
    async def test_one_screen_one_action_validation_failure(self):
        """? - ?"""
        screen_config = {
            "screen_id": "test_screen_2",
            "primary_actions": [
                {"type": "submit", "label": "?"},
                {"type": "save", "label": "?"}
            ],
            "simultaneous_inputs": 2,
            "visual_elements": 12
        }
        
        result = await self.reducer.validate_one_screen_one_action(screen_config)
        
        assert result["is_valid"] == False
        assert len(result["violations"]) == 3
        
        # ?
        violation_types = [v["type"] for v in result["violations"]]
        assert "multiple_primary_actions" in violation_types
        assert "multiple_simultaneous_inputs" in violation_types
        assert "too_many_visual_elements" in violation_types
    
    @pytest.mark.asyncio
    async def test_choice_limit_validation_success(self):
        """?3? - 成"""
        screen_config = {
            "screen_id": "choice_test_1",
            "choice_count": 3,
            "choices": [
                {"text": "?1", "value": "option1"},
                {"text": "?2", "value": "option2"},
                {"text": "?3", "value": "option3"}
            ]
        }
        
        result = await self.reducer.validate_choice_limit(screen_config)
        
        assert result["is_valid"] == True
        assert result["constraint_type"] == "choice_limit"
        assert len(result["violations"]) == 0
    
    @pytest.mark.asyncio
    async def test_choice_limit_validation_failure(self):
        """?3? - ?"""
        screen_config = {
            "screen_id": "choice_test_2",
            "choice_count": 5,
            "choices": [
                {"text": "?1", "value": "option1"},
                {"text": "?2", "value": "option2"},
                {"text": "?3", "value": "option3"},
                {"text": "?4", "value": "option4"},
                {"text": "こ", "value": "option5"}
            ]
        }
        
        result = await self.reducer.validate_choice_limit(screen_config)
        
        assert result["is_valid"] == False
        assert len(result["violations"]) == 2
        
        # ?
        violation_types = [v["type"] for v in result["violations"]]
        assert "too_many_choices" in violation_types
        assert "choice_text_too_long" in violation_types
    
    @pytest.mark.asyncio
    async def test_font_settings_validation_success(self):
        """BIZ UDGothic? - 成"""
        screen_config = {
            "screen_id": "font_test_1",
            "font": {
                "family": "BIZ UDGothic",
                "line_height": 1.6
            },
            "text_lines": 3
        }
        
        result = await self.reducer.validate_font_settings(screen_config)
        
        assert result["is_valid"] == True
        assert result["constraint_type"] == "font_settings"
        assert len(result["violations"]) == 0
    
    @pytest.mark.asyncio
    async def test_font_settings_validation_failure(self):
        """BIZ UDGothic? - ?"""
        screen_config = {
            "screen_id": "font_test_2",
            "font": {
                "family": "Arial",
                "line_height": 1.2
            },
            "text_lines": 6
        }
        
        result = await self.reducer.validate_font_settings(screen_config)
        
        assert result["is_valid"] == False
        assert len(result["violations"]) == 3
        
        # ?
        violation_types = [v["type"] for v in result["violations"]]
        assert "incorrect_font_family" in violation_types
        assert "insufficient_line_height" in violation_types
        assert "too_many_text_lines" in violation_types
    
    @pytest.mark.asyncio
    async def test_cognitive_load_assessment_low(self):
        """? - ?"""
        screen_config = {
            "information_density": "low",
            "choice_count": 1,
            "simultaneous_inputs": 0,
            "visual_elements": 3,
            "animations": 0
        }
        
        result = await self.reducer.assess_cognitive_load(screen_config)
        
        assert result["load_level"] == "low"
        assert result["adhd_friendly"] == True
        assert result["load_score"] <= 2
    
    @pytest.mark.asyncio
    async def test_cognitive_load_assessment_high(self):
        """? - ?"""
        screen_config = {
            "information_density": "high",
            "choice_count": 5,
            "simultaneous_inputs": 3,
            "visual_elements": 15,
            "animations": 4
        }
        
        result = await self.reducer.assess_cognitive_load(screen_config)
        
        assert result["load_level"] in ["high", "very_high"]
        assert result["adhd_friendly"] == False
        assert result["load_score"] > 5
        assert len(result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_adhd_optimized_layout_generation(self):
        """ADHD?"""
        content_data = {
            "text": "こ\n?\n?\n?\nわ\n表\n内部",
            "choices": [
                {"text": "?1", "value": "1"},
                {"text": "?2", "value": "2"},
                {"text": "?3", "value": "3"},
                {"text": "?4", "value": "4"},  # ?
                {"text": "?5", "value": "5"}   # ?
            ],
            "actions": [
                {"type": "primary", "label": "メイン"},
                {"type": "secondary", "label": "?1"},
                {"type": "secondary", "label": "?2"}
            ]
        }
        
        result = await self.reducer.generate_adhd_optimized_layout(content_data)
        
        assert result["layout_type"] == "adhd_optimized"
        assert result["font"]["family"] == "BIZ UDGothic"
        assert result["font"]["line_height"] == 1.6
        
        # ?
        assert "text_pages" in result["content_structure"]
        assert len(result["content_structure"]["text_pages"]) > 1
        
        # ?3つ
        assert len(result["content_structure"]["choices"]) == 3
        
        # ?1つ
        assert result["content_structure"]["primary_action"] is not None
        assert result["content_structure"]["primary_action"]["type"] == "primary"

class TestUIConstraintValidator:
    """UI?"""
    
    def setup_method(self):
        """?"""
        self.validator = UIConstraintValidator()
    
    @pytest.mark.asyncio
    async def test_comprehensive_screen_validation_success(self):
        """? - 成"""
        screen_config = {
            "screen_id": "comprehensive_test_1",
            "primary_actions": [{"type": "submit", "label": "?"}],
            "simultaneous_inputs": 1,
            "visual_elements": 4,
            "choice_count": 2,
            "choices": [
                {"text": "は", "value": "yes"},
                {"text": "い", "value": "no"}
            ],
            "font": {
                "family": "BIZ UDGothic",
                "line_height": 1.6
            },
            "text_lines": 3,
            "information_density": "low",
            "animations": 1
        }
        
        result = await self.validator.validate_screen(screen_config)
        
        assert result["overall_valid"] == True
        assert len(result["violations"]) == 0
        assert "one_screen_one_action" in result["validations"]
        assert "choice_limit" in result["validations"]
        assert "font_settings" in result["validations"]
        assert "cognitive_load" in result["validations"]
    
    @pytest.mark.asyncio
    async def test_comprehensive_screen_validation_failure(self):
        """? - ?"""
        screen_config = {
            "screen_id": "comprehensive_test_2",
            "primary_actions": [
                {"type": "submit", "label": "?"},
                {"type": "save", "label": "?"}
            ],
            "simultaneous_inputs": 3,
            "visual_elements": 12,
            "choice_count": 6,
            "choices": [
                {"text": "?1", "value": "1"},
                {"text": "?2", "value": "2"},
                {"text": "?3", "value": "3"},
                {"text": "?4", "value": "4"},
                {"text": "?5", "value": "5"},
                {"text": "?", "value": "6"}
            ],
            "font": {
                "family": "Arial",
                "line_height": 1.0
            },
            "text_lines": 8,
            "information_density": "high",
            "animations": 5
        }
        
        result = await self.validator.validate_screen(screen_config)
        
        assert result["overall_valid"] == False
        assert len(result["violations"]) > 0
        assert len(result["recommendations"]) > 0
        
        # ?
        assert result["validations"]["one_screen_one_action"]["is_valid"] == False
        assert result["validations"]["choice_limit"]["is_valid"] == False
        assert result["validations"]["font_settings"]["is_valid"] == False
        assert result["validations"]["cognitive_load"]["adhd_friendly"] == False
    
    @pytest.mark.asyncio
    async def test_adhd_optimizations_generation(self):
        """ADHD?"""
        screen_config = {
            "choice_count": 5,
            "information_density": "high",
            "color_contrast": "low",
            "keyboard_navigation": False,
            "simultaneous_inputs": 2,
            "visual_elements": 15,
            "animations": 4
        }
        
        result = await self.validator.get_adhd_optimizations(screen_config)
        
        assert len(result) > 0
        
        # ?
        optimization_types = [opt["type"] for opt in result]
        assert "reduce_choices" in optimization_types
        assert "reduce_information_density" in optimization_types
        assert "improve_contrast" in optimization_types
        assert "add_keyboard_navigation" in optimization_types
        
        # ?
        for optimization in result:
            assert "priority" in optimization
            assert optimization["priority"] in ["high", "medium", "low"]
            assert "description" in optimization
            assert "implementation" in optimization

class TestIntegration:
    """?"""
    
    def setup_method(self):
        """?"""
        self.validator = UIConstraintValidator()
    
    @pytest.mark.asyncio
    async def test_real_world_screen_validation(self):
        """実装"""
        # タスク
        task_creation_screen = {
            "screen_id": "task_creation",
            "primary_actions": [{"type": "create", "label": "タスク"}],
            "simultaneous_inputs": 1,
            "visual_elements": 6,
            "choice_count": 3,
            "choices": [
                {"text": "?", "value": "routine"},
                {"text": "?", "value": "one_shot"},
                {"text": "ストーリー", "value": "skill_up"}
            ],
            "font": {
                "family": "BIZ UDGothic",
                "line_height": 1.6
            },
            "text_lines": 2,
            "information_density": "medium",
            "animations": 1,
            "color_contrast": "normal",
            "keyboard_navigation": True
        }
        
        result = await self.validator.validate_screen(task_creation_screen)
        
        # ?ADHD?
        assert result["validations"]["cognitive_load"]["adhd_friendly"] == True or result["validations"]["cognitive_load"]["load_level"] == "medium"
    
    @pytest.mark.asyncio
    async def test_mandala_grid_screen_validation(self):
        """Mandala?"""
        mandala_screen = {
            "screen_id": "mandala_grid",
            "primary_actions": [{"type": "select", "label": "?"}],
            "simultaneous_inputs": 0,  # タスク
            "visual_elements": 9,  # 3x3?
            "choice_count": 0,  # ?
            "font": {
                "family": "BIZ UDGothic",
                "line_height": 1.6
            },
            "text_lines": 1,
            "information_density": "medium",
            "animations": 2,  # ?
            "color_contrast": "high",
            "keyboard_navigation": True
        }
        
        result = await self.validator.validate_screen(mandala_screen)
        
        # Mandala?UIな
        assert result["validations"]["font_settings"]["is_valid"] == True
        assert result["validations"]["cognitive_load"]["load_level"] in ["low", "medium", "high"]
        # ?

def run_tests():
    """?"""
    print("? ADHD支援 - ?...")
    
    # pytest実装
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])
    
    if exit_code == 0:
        print("? す")
        print("\n? 実装:")
        print("  - ?")
        print("  - ?3?")
        print("  - BIZ UDGothic?")
        print("  - ?")
        print("  - ADHD?")
        print("  - UI?")
    else:
        print("? ?")
    
    return exit_code == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)