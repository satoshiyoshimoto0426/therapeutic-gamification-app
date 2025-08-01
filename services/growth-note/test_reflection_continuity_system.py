"""
?
"""

import pytest
from datetime import datetime, date, timedelta
from reflection_continuity_system import (
    ReflectionContinuitySystem,
    ReflectionStreak,
    StoryPersonalizationData,
    ReminderType
)
from main import GrowthNoteSystem, EmotionalTone, ActionOrientation, ReflectionAnalysis

class TestReflectionContinuitySystem:
    
    def setup_method(self):
        """?"""
        self.growth_note_system = GrowthNoteSystem()
        self.continuity_system = ReflectionContinuitySystem(self.growth_note_system)
    
    def test_update_reflection_streak_first_time(self):
        """?"""
        result = self.continuity_system.update_reflection_streak("user1", True)
        
        assert result["status"] == "completed"
        assert result["streak"] == 1
        assert result["total_reflections"] == 1
        assert result["milestone_reward"] is None
        
        # ストーリー
        streak = self.continuity_system.user_streaks["user1"]
        assert streak.current_streak == 1
        assert streak.longest_streak == 1
        assert streak.total_reflections == 1
        assert streak.last_reflection_date == date.today()
        assert streak.missed_days_in_row == 0
    
    def test_update_reflection_streak_consecutive(self):
        """?"""
        user_id = "user2"
        
        # 1?
        self.continuity_system.update_reflection_streak(user_id, True)
        
        # 2?
        streak = self.continuity_system.user_streaks[user_id]
        streak.last_reflection_date = date.today() - timedelta(days=1)
        
        result = self.continuity_system.update_reflection_streak(user_id, True)
        
        assert result["status"] == "completed"
        assert result["streak"] == 2
        assert result["total_reflections"] == 2
        
        streak = self.continuity_system.user_streaks[user_id]
        assert streak.current_streak == 2
        assert streak.longest_streak == 2
        assert streak.missed_days_in_row == 0
    
    def test_update_reflection_streak_milestone(self):
        """?"""
        user_id = "user3"
        
        # 3?
        self.continuity_system.update_reflection_streak(user_id, True)
        streak = self.continuity_system.user_streaks[user_id]
        streak.current_streak = 2
        streak.last_reflection_date = date.today() - timedelta(days=1)
        
        result = self.continuity_system.update_reflection_streak(user_id, True)
        
        assert result["status"] == "completed"
        assert result["streak"] == 3
        assert result["milestone_reward"] is not None
        assert result["milestone_reward"]["milestone"] == 3
        assert result["milestone_reward"]["xp_bonus"] == 50
        assert "3?" in result["milestone_reward"]["message"]
        
        # ?
        assert 3 in streak.streak_milestones
    
    def test_update_reflection_streak_already_completed(self):
        """?"""
        user_id = "user4"
        
        # 1?
        result1 = self.continuity_system.update_reflection_streak(user_id, True)
        assert result1["status"] == "completed"
        
        # ?2?
        result2 = self.continuity_system.update_reflection_streak(user_id, True)
        assert result2["status"] == "already_completed"
        assert result2["streak"] == 1
        
        # ?
        streak = self.continuity_system.user_streaks[user_id]
        assert streak.total_reflections == 1
    
    def test_update_reflection_streak_skip(self):
        """?"""
        user_id = "user5"
        
        # ま1?
        self.continuity_system.update_reflection_streak(user_id, True)
        
        # 2?
        streak = self.continuity_system.user_streaks[user_id]
        streak.last_reflection_date = date.today() - timedelta(days=2)
        
        result = self.continuity_system.update_reflection_streak(user_id, False)
        
        assert result["status"] == "skipped"
        assert result["missed_days"] == 2
        assert result["needs_reminder"] == True
        
        # ストーリー
        assert streak.current_streak == 0
        assert streak.missed_days_in_row == 2
    
    def test_generate_reminder_message_gentle(self):
        """?"""
        user_id = "user6"
        
        # ?
        reminder = self.continuity_system.generate_reminder_message(user_id, 2)
        
        assert reminder["type"] == "flex"
        assert reminder["altText"] == "?"
        assert reminder["contents"]["type"] == "bubble"
        
        # ヘルパー
        header = reminder["contents"]["header"]
        assert "?" in header["contents"][0]["text"]
        assert "?" in header["contents"][0]["text"]
        
        # ?
        body = reminder["contents"]["body"]
        message_text = body["contents"][0]["text"]
        assert len(message_text) > 0
        
        # ?
        footer = reminder["contents"]["footer"]
        buttons = footer["contents"]
        assert len(buttons) == 2
        assert "?" in buttons[0]["action"]["label"]
        assert "?" in buttons[1]["action"]["label"]
    
    def test_generate_reminder_message_encouraging(self):
        """?"""
        user_id = "user7"
        
        # ?
        reminder = self.continuity_system.generate_reminder_message(user_id, 5)
        
        header = reminder["contents"]["header"]
        assert "?" in header["contents"][0]["text"]
    
    def test_generate_reminder_message_motivational(self):
        """や"""
        user_id = "user8"
        
        # ?
        reminder = self.continuity_system.generate_reminder_message(user_id, 10)
        
        header = reminder["contents"]["header"]
        assert "?" in header["contents"][0]["text"]
    
    def test_update_story_personalization_data(self):
        """ストーリー"""
        user_id = "user9"
        
        # ?
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.POSITIVE,
            problem_themes=["social", "work_study"],
            action_orientation=ActionOrientation.HIGH,
            key_insights=["?", "?"],
            story_personalization_data={}
        )
        
        self.continuity_system.update_story_personalization_data(user_id, analysis)
        
        # デフォルト
        assert user_id in self.continuity_system.story_personalization
        data = self.continuity_system.story_personalization[user_id]
        
        assert data.user_id == user_id
        assert "social" in data.recent_themes
        assert "work_study" in data.recent_themes
        assert "positive" in data.emotional_patterns
        assert "high" in data.action_tendencies
        assert len(data.reflection_insights) == 1
        assert len(data.growth_areas) > 0
    
    def test_get_story_personalization_context(self):
        """ストーリー"""
        user_id = "user10"
        
        # ま
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.POSITIVE,
            problem_themes=["social"],
            action_orientation=ActionOrientation.MEDIUM,
            key_insights=["?"],
            story_personalization_data={}
        )
        
        self.continuity_system.update_story_personalization_data(user_id, analysis)
        
        # コア
        context = self.continuity_system.get_story_personalization_context(user_id)
        
        assert context["user_id"] == user_id
        assert "social" in context["recent_themes"]
        assert context["dominant_emotion"] == "positive"
        assert context["dominant_action_tendency"] == "medium"
        assert len(context["growth_areas"]) > 0
        assert context["reflection_frequency"] == 1
        assert "last_updated" in context
    
    def test_get_story_personalization_context_empty(self):
        """デフォルト"""
        context = self.continuity_system.get_story_personalization_context("nonexistent_user")
        
        assert context == {}
    
    def test_get_streak_status(self):
        """ストーリー"""
        user_id = "user11"
        
        # デフォルト
        status = self.continuity_system.get_streak_status(user_id)
        
        assert status["current_streak"] == 0
        assert status["longest_streak"] == 0
        assert status["total_reflections"] == 0
        assert status["missed_days_in_row"] == 0
        assert status["needs_reminder"] == False  # ?
        assert status["last_reflection_date"] is None
        
        # デフォルト
        self.continuity_system.update_reflection_streak(user_id, True)
        status = self.continuity_system.get_streak_status(user_id)
        
        assert status["current_streak"] == 1
        assert status["longest_streak"] == 1
        assert status["total_reflections"] == 1
        assert status["missed_days_in_row"] == 0
        assert status["needs_reminder"] == False
        assert status["last_reflection_date"] == date.today().isoformat()
    
    def test_identify_growth_areas(self):
        """成"""
        analysis = ReflectionAnalysis(
            emotional_tone=EmotionalTone.NEUTRAL,
            problem_themes=["social", "mental", "time"],
            action_orientation=ActionOrientation.LOW,
            key_insights=[],
            story_personalization_data={}
        )
        
        growth_areas = self.continuity_system._identify_growth_areas(analysis)
        
        assert "?" in growth_areas
        assert "メイン" in growth_areas
        assert "?" in growth_areas
        assert "?" in growth_areas  # ?
    
    def test_milestone_rewards_structure(self):
        """?"""
        milestones = self.continuity_system.milestone_rewards
        
        # ?
        assert 3 in milestones
        assert 7 in milestones
        assert 21 in milestones
        assert 100 in milestones
        
        # ?
        for milestone, reward in milestones.items():
            assert "xp" in reward
            assert "message" in reward
            assert isinstance(reward["xp"], int)
            assert isinstance(reward["message"], str)
            assert reward["xp"] > 0
    
    def test_reminder_messages_structure(self):
        """リスト"""
        messages = self.continuity_system.reminder_messages
        
        # ?
        assert ReminderType.GENTLE in messages
        assert ReminderType.ENCOURAGING in messages
        assert ReminderType.MOTIVATIONAL in messages
        
        # ?
        for reminder_type, message_list in messages.items():
            assert isinstance(message_list, list)
            assert len(message_list) > 0
            for message in message_list:
                assert isinstance(message, str)
                assert len(message) > 0
    
    def test_reflection_streak_dataclass(self):
        """ReflectionStreakデフォルト"""
        streak = ReflectionStreak(user_id="test_user")
        
        assert streak.user_id == "test_user"
        assert streak.current_streak == 0
        assert streak.longest_streak == 0
        assert streak.total_reflections == 0
        assert streak.last_reflection_date is None
        assert streak.missed_days_in_row == 0
        assert streak.streak_milestones == []
    
    def test_story_personalization_data_dataclass(self):
        """StoryPersonalizationDataデフォルト"""
        data = StoryPersonalizationData(
            user_id="test_user",
            recent_themes=["test"],
            emotional_patterns=["positive"],
            action_tendencies=["high"],
            growth_areas=["test_area"],
            reflection_insights=[{"test": "insight"}],
            last_updated=datetime.now()
        )
        
        assert data.user_id == "test_user"
        assert data.recent_themes == ["test"]
        assert data.emotional_patterns == ["positive"]
        assert data.action_tendencies == ["high"]
        assert data.growth_areas == ["test_area"]
        assert data.reflection_insights == [{"test": "insight"}]
        assert isinstance(data.last_updated, datetime)

def test_demo_function():
    """デフォルト"""
    from reflection_continuity_system import demo_continuity_system
    
    continuity_system = demo_continuity_system()
    
    assert isinstance(continuity_system, ReflectionContinuitySystem)
    assert "demo_user" in continuity_system.user_streaks
    assert "demo_user" in continuity_system.story_personalization
    
    # ストーリー
    streak = continuity_system.user_streaks["demo_user"]
    assert streak.current_streak >= 1
    assert streak.total_reflections >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])