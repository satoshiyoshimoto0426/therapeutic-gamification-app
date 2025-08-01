"""
?
"""

import pytest
from datetime import datetime
from main import (
    GrowthNoteSystem, 
    EmotionalTone, 
    ActionOrientation,
    ReflectionPrompts,
    ReflectionAnalysis
)

class TestGrowthNoteSystem:
    
    def setup_method(self):
        """?"""
        self.system = GrowthNoteSystem()
    
    def test_generate_reflection_prompt_basic(self):
        """基本"""
        user_context = {
            "mood": 3,
            "completed_tasks": 2,
            "recent_struggles": []
        }
        
        prompts = self.system.generate_reflection_prompt(user_context)
        
        assert isinstance(prompts, ReflectionPrompts)
        assert prompts.current_problems_prompt is not None
        assert prompts.ideal_world_prompt is not None
        assert prompts.ideal_emotions_prompt is not None
        assert prompts.tomorrow_actions_prompt is not None
        assert prompts.estimated_time == "10-15?"
        assert prompts.xp_reward == 25
    
    def test_generate_reflection_prompt_low_mood(self):
        """?"""
        user_context = {
            "mood": 1,
            "completed_tasks": 0,
            "recent_struggles": ["mental", "motivation"]
        }
        
        prompts = self.system.generate_reflection_prompt(user_context)
        
        # ?
        assert "無" in prompts.current_problems_prompt or "?" in prompts.current_problems_prompt
        assert len(prompts.current_problems_prompt) > 0
    
    def test_generate_reflection_prompt_high_mood(self):
        """?"""
        user_context = {
            "mood": 5,
            "completed_tasks": 8,
            "recent_struggles": []
        }
        
        prompts = self.system.generate_reflection_prompt(user_context)
        
        # ?
        assert "?" in prompts.current_problems_prompt or "?" in prompts.ideal_world_prompt
    
    def test_analyze_emotional_tone_positive(self):
        """?"""
        positive_text = "と"
        
        tone = self.system._analyze_emotional_tone(positive_text)
        
        assert tone in [EmotionalTone.POSITIVE, EmotionalTone.VERY_POSITIVE]
    
    def test_analyze_emotional_tone_negative(self):
        """?"""
        negative_text = "?"
        
        tone = self.system._analyze_emotional_tone(negative_text)
        
        assert tone in [EmotionalTone.NEGATIVE, EmotionalTone.VERY_NEGATIVE]
    
    def test_analyze_emotional_tone_neutral(self):
        """?"""
        neutral_text = "?"
        
        tone = self.system._analyze_emotional_tone(neutral_text)
        
        assert tone == EmotionalTone.NEUTRAL
    
    def test_analyze_emotional_tone_empty(self):
        """?"""
        tone = self.system._analyze_emotional_tone("")
        
        assert tone == EmotionalTone.NEUTRAL
    
    def test_extract_problem_themes(self):
        """?"""
        problems_text = "?"
        
        themes = self.system._extract_problem_themes(problems_text)
        
        assert "social" in themes
        assert "work_study" in themes
        assert "health" in themes
        assert "mental" in themes  # ストーリー
    
    def test_extract_problem_themes_empty(self):
        """?"""
        themes = self.system._extract_problem_themes("")
        
        assert themes == []
    
    def test_analyze_action_orientation_high(self):
        """?"""
        action_text = "?"
        
        orientation = self.system._analyze_action_orientation(action_text)
        
        assert orientation == ActionOrientation.HIGH
    
    def test_analyze_action_orientation_medium(self):
        """?"""
        action_text = "?"
        
        orientation = self.system._analyze_action_orientation(action_text)
        
        assert orientation == ActionOrientation.MEDIUM
    
    def test_analyze_action_orientation_low(self):
        """?"""
        action_text = "?"
        
        orientation = self.system._analyze_action_orientation(action_text)
        
        assert orientation == ActionOrientation.LOW
    
    def test_analyze_action_orientation_empty(self):
        """?"""
        orientation = self.system._analyze_action_orientation("")
        
        assert orientation == ActionOrientation.LOW
    
    def test_process_reflection_complete(self):
        """?"""
        reflection_data = {
            "current_problems": "?",
            "ideal_world": "?",
            "ideal_emotions": "?",
            "tomorrow_actions": "?"
        }
        
        analysis = self.system.process_reflection(reflection_data)
        
        assert isinstance(analysis, ReflectionAnalysis)
        assert isinstance(analysis.emotional_tone, EmotionalTone)
        assert isinstance(analysis.problem_themes, list)
        assert isinstance(analysis.action_orientation, ActionOrientation)
        assert isinstance(analysis.key_insights, list)
        assert isinstance(analysis.story_personalization_data, dict)
        
        # ストーリー
        story_data = analysis.story_personalization_data
        assert "current_challenges" in story_data
        assert "ideal_vision" in story_data
        assert "emotional_state" in story_data
        assert "action_readiness" in story_data
        assert "reflection_timestamp" in story_data
    
    def test_extract_key_insights(self):
        """?"""
        reflection_data = {
            "current_problems": "?",
            "ideal_world": "?",
            "ideal_emotions": "?",
            "tomorrow_actions": "?"
        }
        
        insights = self.system._extract_key_insights(reflection_data)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any("?" in insight for insight in insights)
        # ?25文字
        assert any("?" in insight for insight in insights) or len(reflection_data["tomorrow_actions"]) > 25
    
    def test_extract_key_themes(self):
        """?"""
        text = "?"
        
        themes = self.system._extract_key_themes(text)
        
        assert isinstance(themes, list)
        assert "?" in themes
        assert "?" in themes
        assert "?" in themes
        assert "?" in themes
        # 自動
        expected_themes = ["?", "?", "?", "?", "自動"]
        found_themes = [theme for theme in expected_themes if theme in themes]
        assert len(found_themes) >= 4  # 5つ4つOK
        assert len(themes) <= 5  # ?5つ
    
    def test_calculate_reflection_xp_basic(self):
        """基本XP計算"""
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.POSITIVE,
            problem_themes=["social", "work_study"],
            action_orientation=ActionOrientation.MEDIUM,
            key_insights=["?"],
            story_personalization_data={}
        )
        
        xp = self.system.calculate_reflection_xp(analysis)
        
        # ?XP(25) + ?(5) + ?(3) + ?(4) = 37
        assert xp == 37
    
    def test_calculate_reflection_xp_high_action(self):
        """?XP計算"""
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.POSITIVE,
            problem_themes=["social"],
            action_orientation=ActionOrientation.HIGH,
            key_insights=["?", "?"],
            story_personalization_data={}
        )
        
        xp = self.system.calculate_reflection_xp(analysis)
        
        # ?XP(25) + ?(10) + ?(6) + ?(2) = 43
        assert xp == 43
    
    def test_calculate_reflection_xp_minimal(self):
        """?XP計算"""
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.NEUTRAL,
            problem_themes=[],
            action_orientation=ActionOrientation.LOW,
            key_insights=[],
            story_personalization_data={}
        )
        
        xp = self.system.calculate_reflection_xp(analysis)
        
        # ?XPの
        assert xp == 25
    
    def test_contextual_prompt_selection(self):
        """コア"""
        # ?
        prompt = self.system._select_contextual_prompt(
            "tomorrow_actions", mood=1, completed_tasks=0, recent_struggles=[]
        )
        
        # ?
        assert ("?" in prompt or 
                "?" in prompt or 
                "?" in prompt)
        
        # ?
        prompt = self.system._select_contextual_prompt(
            "tomorrow_actions", mood=5, completed_tasks=8, recent_struggles=[]
        )
        
        assert ("?" in prompt or 
                "こ" in prompt or 
                "こ" in prompt)

def test_demo_function():
    """デフォルト"""
    from main import demo_growth_note_system
    
    system, analysis = demo_growth_note_system()
    
    assert isinstance(system, GrowthNoteSystem)
    assert isinstance(analysis, ReflectionAnalysis)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])