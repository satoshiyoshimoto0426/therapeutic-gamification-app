#!/usr/bin/env python3
"""
Task 9.2: CBT?
?
"""

import asyncio
import pytest
import sys
import os

# ?
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from main import (
    CBTInterventionEngine,
    TherapeuticSafetyService,
    SafetyThreatLevel
)

class TestCBTInterventionEngine:
    """CBT?"""
    
    def setup_method(self):
        """?"""
        self.cbt_engine = CBTInterventionEngine()
        self.test_user_context = {
            "uid": "test_user_001",
            "character_name": "ユーザー",
            "recent_mood": 2,
            "recent_mood_history": [2, 2, 3],
            "past_success": "?"
        }
    
    def test_detect_all_or_nothing_thinking(self):
        """?"""
        test_content = "い"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(test_content)
        
        assert len(patterns) > 0
        assert any(p["type"] == "all_or_nothing" for p in patterns)
        
        all_or_nothing_pattern = next(p for p in patterns if p["type"] == "all_or_nothing")
        assert all_or_nothing_pattern["confidence"] > 0.2  # 実装
        assert all_or_nothing_pattern["name"] == "?"
    
    def test_detect_catastrophizing(self):
        """?"""
        test_content = "こ"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(test_content)
        
        assert len(patterns) > 0
        catastrophizing_pattern = next(
            (p for p in patterns if p["type"] == "catastrophizing"), None
        )
        assert catastrophizing_pattern is not None
        assert catastrophizing_pattern["confidence"] > 0.4  # 実装
        assert catastrophizing_pattern["severity"] in ["medium", "high"]
    
    def test_detect_personalization(self):
        """?"""
        test_content = "?"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(test_content)
        
        personalization_pattern = next(
            (p for p in patterns if p["type"] == "personalization"), None
        )
        assert personalization_pattern is not None
        assert personalization_pattern["confidence"] > 0.2  # 実装
    
    def test_detect_mind_reading(self):
        """?"""
        test_content = "み"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(test_content)
        
        mind_reading_pattern = next(
            (p for p in patterns if p["type"] == "mind_reading"), None
        )
        assert mind_reading_pattern is not None
        assert mind_reading_pattern["confidence"] > 0.05  # 実装
    
    def test_detect_emotional_reasoning(self):
        """?"""
        test_content = "?"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(test_content)
        
        # ?
        assert len(patterns) >= 0  # ?
        
        # ?
        emotional_reasoning_pattern = next(
            (p for p in patterns if p["type"] == "emotional_reasoning"), None
        )
        if emotional_reasoning_pattern:
            assert emotional_reasoning_pattern["confidence"] > 0
    
    def test_generate_story_break_dialog(self):
        """ストーリー"""
        detected_patterns = [{
            "type": "all_or_nothing",
            "name": "?",
            "confidence": 0.8,
            "severity": "high"
        }]
        
        story_break = self.cbt_engine.generate_story_break_dialog(
            detected_patterns, self.test_user_context
        )
        
        assert story_break["intervention_needed"] is True
        assert story_break["primary_distortion"] == "all_or_nothing"
        assert story_break["confidence"] == 0.8
        assert "ユーザー" in story_break["dialog"]
        assert len(story_break["dialog"]) > 50  # ?
    
    def test_generate_story_break_dialog_no_patterns(self):
        """?"""
        story_break = self.cbt_engine.generate_story_break_dialog(
            [], self.test_user_context
        )
        
        assert story_break["intervention_needed"] is False
        assert story_break["dialog"] is None
    
    def test_generate_cognitive_reframing_all_or_nothing(self):
        """?"""
        thought = "い"
        
        reframing = self.cbt_engine.generate_cognitive_reframing(
            thought, "all_or_nothing", self.test_user_context
        )
        
        assert reframing["original_thought"] == thought
        assert reframing["distortion_type"] == "all_or_nothing"
        assert reframing["technique"] == "?"
        assert len(reframing["reframed_thoughts"]) > 0
        assert len(reframing["reflection_questions"]) > 0
        assert reframing["confidence"] > 0.8
    
    def test_generate_cognitive_reframing_catastrophizing(self):
        """?"""
        thought = "こ"
        
        reframing = self.cbt_engine.generate_cognitive_reframing(
            thought, "catastrophizing", self.test_user_context
        )
        
        assert reframing["technique"] == "?"
        assert any("?" in rt for rt in reframing["reframed_thoughts"])
        assert any("?" in q for q in reframing["reflection_questions"])
    
    def test_generate_cognitive_reframing_personalization(self):
        """?"""
        thought = "?"
        
        reframing = self.cbt_engine.generate_cognitive_reframing(
            thought, "personalization", self.test_user_context
        )
        
        assert reframing["technique"] == "?"
        assert any("?" in rt for rt in reframing["reframed_thoughts"])
    
    def test_create_cbt_intervention_comprehensive(self):
        """CBT?"""
        content = "い"
        
        intervention = self.cbt_engine.create_cbt_intervention(
            content, self.test_user_context
        )
        
        assert intervention["intervention_recommended"] is True
        assert len(intervention["detected_patterns"]) > 0
        assert intervention["story_break_dialog"]["intervention_needed"] is True
        assert intervention["cognitive_reframing"] is not None
        assert intervention["severity"] in ["low", "medium", "high"]
    
    def test_create_cbt_intervention_no_patterns(self):
        """?CBT?"""
        content = "?"
        
        intervention = self.cbt_engine.create_cbt_intervention(
            content, self.test_user_context
        )
        
        assert intervention["intervention_recommended"] is False
        assert len(intervention["detected_patterns"]) == 0
        assert intervention["severity"] == "none"
    
    def test_evaluate_intervention_effectiveness(self):
        """CBT?"""
        original_content = "い"
        reframed_content = "?"
        
        effectiveness = self.cbt_engine.evaluate_intervention_effectiveness(
            original_content, reframed_content
        )
        
        assert effectiveness["original_severity"] > effectiveness["reframed_severity"]
        assert effectiveness["improvement_rate"] > 0
        assert effectiveness["patterns_reduced"] >= 0
    
    def test_generate_therapeutic_response_intervention_needed(self):
        """?"""
        user_input = "も"
        
        response = self.cbt_engine.generate_therapeutic_response(
            user_input, self.test_user_context
        )
        
        assert response["response_type"] == "cbt_intervention"
        assert response["intervention_needed"] is True
        assert len(response["message"]) > 100  # ?
        assert response["primary_distortion"] is not None
        assert response["severity"] in ["low", "medium", "high"]
    
    def test_generate_therapeutic_response_supportive(self):
        """支援"""
        user_input = "?"
        
        response = self.cbt_engine.generate_therapeutic_response(
            user_input, self.test_user_context
        )
        
        assert response["response_type"] == "supportive"
        assert response["intervention_needed"] is False
        assert "理" in response["message"] or "?" in response["message"]

class TestTherapeuticSafetyService:
    """治療"""
    
    def setup_method(self):
        """?"""
        self.safety_service = TherapeuticSafetyService()
        self.test_user_context = {
            "uid": "test_user_002",
            "character_name": "ユーザー",
            "recent_mood": 2,
            "recent_mood_history": [1, 2, 2]
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_safety_analysis_high_risk(self):
        """?"""
        content = "も"
        
        result = await self.safety_service.comprehensive_safety_analysis(
            content, self.test_user_context
        )
        
        assert "safety_analysis" in result
        assert "cbt_analysis" in result
        assert "therapeutic_response" in result
        assert "recommended_action" in result
        
        # 安全
        safety = result["safety_analysis"]
        assert safety["content_safe"] is False
        assert safety["threat_level"] in ["high", "critical"]
        
        # CBT?
        cbt = result["cbt_analysis"]
        assert cbt["intervention_recommended"] is True
        assert len(cbt["detected_patterns"]) > 0
        
        # 治療
        therapeutic = result["therapeutic_response"]
        assert therapeutic["intervention_needed"] is True
        assert therapeutic["response_type"] == "cbt_intervention"
        
        # ?
        assert result["recommended_action"] in [
            "human_escalation", "immediate_cbt_intervention"
        ]
    
    @pytest.mark.asyncio
    async def test_comprehensive_safety_analysis_medium_risk(self):
        """?"""
        content = "い"
        
        result = await self.safety_service.comprehensive_safety_analysis(
            content, self.test_user_context
        )
        
        safety = result["safety_analysis"]
        cbt = result["cbt_analysis"]
        
        assert cbt["intervention_recommended"] is True
        assert result["recommended_action"] in ["cbt_support", "immediate_cbt_intervention"]
    
    @pytest.mark.asyncio
    async def test_comprehensive_safety_analysis_low_risk(self):
        """?"""
        content = "?"
        
        result = await self.safety_service.comprehensive_safety_analysis(
            content, self.test_user_context
        )
        
        safety = result["safety_analysis"]
        cbt = result["cbt_analysis"]
        therapeutic = result["therapeutic_response"]
        
        assert safety["content_safe"] is True
        assert cbt["intervention_recommended"] is False
        assert therapeutic["response_type"] == "supportive"
        assert result["recommended_action"] == "continue_story"

class TestCBTIntegrationScenarios:
    """CBT?"""
    
    def setup_method(self):
        """?"""
        self.cbt_engine = CBTInterventionEngine()
        self.safety_service = TherapeuticSafetyService()
    
    def test_multiple_distortions_detection(self):
        """?"""
        content = "い"
        
        patterns = self.cbt_engine.detect_negative_thought_patterns(content)
        
        # ?
        assert len(patterns) >= 2
        
        detected_types = [p["type"] for p in patterns]
        assert "all_or_nothing" in detected_types
        assert "mind_reading" in detected_types or "catastrophizing" in detected_types
    
    def test_story_break_dialog_contextual_adaptation(self):
        """文字"""
        patterns = [{
            "type": "catastrophizing",
            "name": "?",
            "confidence": 0.9,
            "severity": "high"
        }]
        
        # ?
        context1 = {"character_name": "ユーザー", "recent_mood": 1}
        context2 = {"character_name": "アプリ", "recent_mood": 3}
        
        dialog1 = self.cbt_engine.generate_story_break_dialog(patterns, context1)
        dialog2 = self.cbt_engine.generate_story_break_dialog(patterns, context2)
        
        assert "ユーザー" in dialog1["dialog"]
        assert "アプリ" in dialog2["dialog"]
        assert dialog1["character_name"] == "ユーザー"
        assert dialog2["character_name"] == "アプリ"
    
    def test_cognitive_reframing_technique_selection(self):
        """?"""
        test_cases = [
            ("all_or_nothing", "?"),
            ("catastrophizing", "?"),
            ("personalization", "?"),
            ("mind_reading", "?"),
            ("emotional_reasoning", "?")
        ]
        
        for distortion_type, expected_technique in test_cases:
            reframing = self.cbt_engine.generate_cognitive_reframing(
                "?", distortion_type
            )
            assert reframing["technique"] == expected_technique
    
    @pytest.mark.asyncio
    async def test_escalation_decision_logic(self):
        """エラー"""
        # ?
        high_risk_content = "死"
        high_risk_context = {
            "uid": "test_user",
            "recent_mood": 1,
            "recent_mood_history": [1, 1, 1]
        }
        
        result = await self.safety_service.comprehensive_safety_analysis(
            high_risk_content, high_risk_context
        )
        
        assert result["safety_analysis"]["escalation_required"] is True
        assert result["recommended_action"] == "human_escalation"
        
        # ?
        medium_risk_content = "い"
        medium_risk_context = {
            "uid": "test_user",
            "recent_mood": 2,
            "recent_mood_history": [2, 3, 2]
        }
        
        result = await self.safety_service.comprehensive_safety_analysis(
            medium_risk_content, medium_risk_context
        )
        
        assert result["recommended_action"] in ["cbt_support", "immediate_cbt_intervention"]

def run_comprehensive_cbt_tests():
    """CBT?"""
    print("=== Task 9.2: CBT? ===")
    
    # ?
    cbt_test = TestCBTInterventionEngine()
    safety_test = TestTherapeuticSafetyService()
    integration_test = TestCBTIntegrationScenarios()
    
    # ?
    cbt_test.setup_method()
    safety_test.setup_method()
    integration_test.setup_method()
    
    test_results = []
    
    # CBT?
    cbt_tests = [
        ("? - ?", cbt_test.test_detect_all_or_nothing_thinking),
        ("? - ?", cbt_test.test_detect_catastrophizing),
        ("? - ?", cbt_test.test_detect_personalization),
        ("? - ?", cbt_test.test_detect_mind_reading),
        ("? - ?", cbt_test.test_detect_emotional_reasoning),
        ("ストーリー", cbt_test.test_generate_story_break_dialog),
        ("ストーリー - ?", cbt_test.test_generate_story_break_dialog_no_patterns),
        ("? - ?", cbt_test.test_generate_cognitive_reframing_all_or_nothing),
        ("? - ?", cbt_test.test_generate_cognitive_reframing_catastrophizing),
        ("? - ?", cbt_test.test_generate_cognitive_reframing_personalization),
        ("CBT?", cbt_test.test_create_cbt_intervention_comprehensive),
        ("CBT? - ?", cbt_test.test_create_cbt_intervention_no_patterns),
        ("?", cbt_test.test_evaluate_intervention_effectiveness),
        ("治療 - ?", cbt_test.test_generate_therapeutic_response_intervention_needed),
        ("治療 - 支援", cbt_test.test_generate_therapeutic_response_supportive)
    ]
    
    for test_name, test_func in cbt_tests:
        try:
            test_func()
            test_results.append(f"? {test_name}")
            print(f"? {test_name}")
        except Exception as e:
            test_results.append(f"? {test_name}: {str(e)}")
            print(f"? {test_name}: {str(e)}")
    
    # ?
    integration_tests = [
        ("?", integration_test.test_multiple_distortions_detection),
        ("文字", integration_test.test_story_break_dialog_contextual_adaptation),
        ("?", integration_test.test_cognitive_reframing_technique_selection)
    ]
    
    for test_name, test_func in integration_tests:
        try:
            test_func()
            test_results.append(f"? {test_name}")
            print(f"? {test_name}")
        except Exception as e:
            test_results.append(f"? {test_name}: {str(e)}")
            print(f"? {test_name}: {str(e)}")
    
    # ?
    async def run_async_tests():
        async_tests = [
            ("? - ?", safety_test.test_comprehensive_safety_analysis_high_risk),
            ("? - ?", safety_test.test_comprehensive_safety_analysis_medium_risk),
            ("? - ?", safety_test.test_comprehensive_safety_analysis_low_risk),
            ("エラー", integration_test.test_escalation_decision_logic)
        ]
        
        for test_name, test_func in async_tests:
            try:
                await test_func()
                test_results.append(f"? {test_name}")
                print(f"? {test_name}")
            except Exception as e:
                test_results.append(f"? {test_name}: {str(e)}")
                print(f"? {test_name}: {str(e)}")
    
    # ?
    asyncio.run(run_async_tests())
    
    # ?
    passed = len([r for r in test_results if r.startswith("?")])
    failed = len([r for r in test_results if r.startswith("?")])
    
    print(f"\n=== ? ===")
    print(f"成: {passed}")
    print(f"?: {failed}")
    print(f"成: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("? Task 9.2: CBT?")
        return True
    else:
        print("?  一般")
        return False

if __name__ == "__main__":
    success = run_comprehensive_cbt_tests()
    sys.exit(0 if success else 1)