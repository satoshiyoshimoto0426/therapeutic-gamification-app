"""
?

?
"""

import pytest
import json
from datetime import datetime, date, timedelta
from main import GrowthNoteSystem
from line_bot_integration import ReflectionLINEInterface
from reflection_continuity_system import ReflectionContinuitySystem

class TestGrowthNoteIntegration:
    
    def setup_method(self):
        """?"""
        self.growth_note_system = GrowthNoteSystem()
        self.line_interface = ReflectionLINEInterface(self.growth_note_system)
        self.continuity_system = ReflectionContinuitySystem(self.growth_note_system)
    
    def test_complete_reflection_flow(self):
        """?"""
        user_id = "integration_user"
        user_context = {
            "mood": 3,
            "completed_tasks": 4,
            "recent_struggles": ["social", "work_study"]
        }
        
        # 1. 22:00プレビュー
        prompt_message = self.line_interface.create_reflection_prompt_message(user_id, user_context)
        assert prompt_message["type"] == "flex"
        assert user_id in self.line_interface.active_sessions
        
        # 2. ?
        form = self.line_interface.create_growth_note_form(user_id)
        assert form["type"] == "flex"
        assert form["contents"]["type"] == "carousel"
        assert len(form["contents"]["contents"]) == 4
        
        # 3. ?
        responses = [
            ("current_problems", "?"),
            ("ideal_world", "?"),
            ("ideal_emotions", "?"),
            ("tomorrow_actions", "?")
        ]
        
        for i, (field, response) in enumerate(responses):
            result = self.line_interface.process_reflection_input(user_id, field, response)
            
            if i < len(responses) - 1:
                # ?
                assert result["type"] == "text"
                assert "?" in result["text"]
                assert f"?: {i+1}/4" in result["text"]
            else:
                # ?
                assert result["type"] == "flex"
                assert "?" in result["altText"]
        
        # 4. ?
        session = self.line_interface.get_session_status(user_id)
        assert session.completed
        assert len(session.responses) == 4
        assert session.xp_earned > 0
        
        # 5. ストーリー
        streak_result = self.continuity_system.update_reflection_streak(user_id, True)
        assert streak_result["status"] == "completed"
        assert streak_result["streak"] == 1
        
        # 6. ストーリー
        analysis = self.growth_note_system.process_reflection(session.responses)
        self.continuity_system.update_story_personalization_data(user_id, analysis)
        
        # 7. ?
        context = self.continuity_system.get_story_personalization_context(user_id)
        assert context["user_id"] == user_id
        assert len(context["recent_themes"]) > 0
        assert context["reflection_frequency"] == 1
    
    def test_streak_and_milestone_flow(self):
        """ストーリー"""
        user_id = "streak_user"
        
        # 3?
        for day in range(3):
            # ?
            user_context = {"mood": 3 + day, "completed_tasks": day + 1}
            self.line_interface.create_reflection_prompt_message(user_id, user_context)
            
            # ?
            responses = {
                "current_problems": f"Day {day+1}: ?",
                "ideal_world": f"Day {day+1}: 理",
                "ideal_emotions": f"Day {day+1}: ?",
                "tomorrow_actions": f"Day {day+1}: ?"
            }
            
            for field, response in responses.items():
                self.line_interface.process_reflection_input(user_id, field, response)
            
            # ストーリー
            if day > 0:
                streak = self.continuity_system.user_streaks[user_id]
                streak.last_reflection_date = date.today() - timedelta(days=1)
            
            result = self.continuity_system.update_reflection_streak(user_id, True)
            
            if day == 2:  # 3?
                assert result["milestone_reward"] is not None
                assert result["milestone_reward"]["milestone"] == 3
                assert result["milestone_reward"]["xp_bonus"] == 50
            else:
                assert result["milestone_reward"] is None
            
            # ストーリー
            session = self.line_interface.active_sessions[user_id]
            analysis = self.growth_note_system.process_reflection(session.responses)
            self.continuity_system.update_story_personalization_data(user_id, analysis)
        
        # ?
        status = self.continuity_system.get_streak_status(user_id)
        assert status["current_streak"] == 3
        assert status["longest_streak"] == 3
        assert status["total_reflections"] == 3
        
        # ?
        context = self.continuity_system.get_story_personalization_context(user_id)
        assert context["reflection_frequency"] == 3
        assert len(context["recent_insights"]) == 3
    
    def test_reminder_flow(self):
        """リスト"""
        user_id = "reminder_user"
        
        # ?
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message(user_id, user_context)
        
        responses = {
            "current_problems": "?",
            "ideal_world": "?",
            "ideal_emotions": "?",
            "tomorrow_actions": "?"
        }
        
        for field, response in responses.items():
            self.line_interface.process_reflection_input(user_id, field, response)
        
        self.continuity_system.update_reflection_streak(user_id, True)
        
        # 3?
        streak = self.continuity_system.user_streaks[user_id]
        streak.last_reflection_date = date.today() - timedelta(days=3)
        
        skip_result = self.continuity_system.update_reflection_streak(user_id, False)
        assert skip_result["status"] == "skipped"
        assert skip_result["needs_reminder"] == True
        
        # リスト
        reminder = self.continuity_system.generate_reminder_message(user_id, 3)
        assert reminder["type"] == "flex"
        assert "?" in reminder["contents"]["header"]["contents"][0]["text"]
        
        # ストーリー
        status = self.continuity_system.get_streak_status(user_id)
        assert status["current_streak"] == 0  # リスト
        assert status["missed_days_in_row"] == 3
        assert status["needs_reminder"] == True
    
    def test_xp_calculation_integration(self):
        """XP計算"""
        user_id = "xp_user"
        
        # ?
        user_context = {"mood": 4, "completed_tasks": 6}
        self.line_interface.create_reflection_prompt_message(user_id, user_context)
        
        # ?
        detailed_responses = {
            "current_problems": "?",
            "ideal_world": "?",
            "ideal_emotions": "と",
            "tomorrow_actions": "?"
        }
        
        for field, response in detailed_responses.items():
            self.line_interface.process_reflection_input(user_id, field, response)
        
        # ?
        session = self.line_interface.active_sessions[user_id]
        assert session.completed
        
        # ?XP計算
        analysis = self.growth_note_system.process_reflection(session.responses)
        xp_earned = self.growth_note_system.calculate_reflection_xp(analysis)
        
        # ?XP?
        assert xp_earned > 25  # 基本XP
        assert session.xp_earned == xp_earned
        
        # ?
        assert len(analysis.problem_themes) > 0
        assert len(analysis.key_insights) > 0
        assert analysis.action_orientation.value in ["medium", "high"]
    
    def test_error_handling_integration(self):
        """エラー"""
        # ?
        error_response = self.line_interface.process_reflection_input(
            "nonexistent_user", "current_problems", "?"
        )
        assert error_response["type"] == "text"
        assert "エラー" in error_response["text"]
        
        # ?
        error_form = self.line_interface.create_growth_note_form("nonexistent_user")
        assert error_form["type"] == "text"
        assert "エラー" in error_form["text"]
        
        # ?
        empty_context = self.continuity_system.get_story_personalization_context("nonexistent_user")
        assert empty_context == {}
    
    def test_session_cleanup_integration(self):
        """?"""
        # ?
        for i in range(3):
            user_id = f"cleanup_user_{i}"
            user_context = {"mood": 3, "completed_tasks": 2}
            self.line_interface.create_reflection_prompt_message(user_id, user_context)
        
        # 1つ
        old_session = self.line_interface.active_sessions["cleanup_user_0"]
        old_session.started_at = datetime.now() - timedelta(hours=25)
        
        # ?
        cleaned_count = self.line_interface.cleanup_old_sessions(24)
        
        assert cleaned_count == 1
        assert "cleanup_user_0" not in self.line_interface.active_sessions
        assert "cleanup_user_1" in self.line_interface.active_sessions
        assert "cleanup_user_2" in self.line_interface.active_sessions

def test_demo_functions_integration():
    """デフォルト"""
    from main import demo_growth_note_system
    from line_bot_integration import demo_line_bot_integration
    from reflection_continuity_system import demo_continuity_system
    
    # ?
    growth_system, analysis = demo_growth_note_system()
    assert growth_system is not None
    assert analysis is not None
    
    line_interface = demo_line_bot_integration()
    assert line_interface is not None
    assert "user123" in line_interface.active_sessions
    
    continuity_system = demo_continuity_system()
    assert continuity_system is not None
    assert "demo_user" in continuity_system.user_streaks

if __name__ == "__main__":
    pytest.main([__file__, "-v"])