"""
LINE Bot?UI?
"""

import pytest
import json
from datetime import datetime, timedelta
from line_bot_integration import ReflectionLINEInterface, ReflectionSession
from main import GrowthNoteSystem

class TestReflectionLINEInterface:
    
    def setup_method(self):
        """?"""
        self.growth_note_system = GrowthNoteSystem()
        self.line_interface = ReflectionLINEInterface(self.growth_note_system)
    
    def test_create_reflection_prompt_message(self):
        """22:00?"""
        user_context = {
            "mood": 3,
            "completed_tasks": 2,
            "recent_struggles": ["social"]
        }
        
        message = self.line_interface.create_reflection_prompt_message("user123", user_context)
        
        assert message["type"] == "flex"
        assert message["altText"] == "?"
        assert "bubble" in message["contents"]["type"]
        
        # ヘルパー
        header = message["contents"]["header"]
        assert "?" in header["contents"][0]["text"]
        
        # ?
        footer = message["contents"]["footer"]
        buttons = footer["contents"]
        assert len(buttons) == 2
        assert "?" in buttons[0]["action"]["label"]
        assert "?" in buttons[1]["action"]["label"]
        
        # ?
        assert "user123" in self.line_interface.active_sessions
        session = self.line_interface.active_sessions["user123"]
        assert session.user_id == "user123"
        assert len(session.prompts) == 4
    
    def test_create_growth_note_form(self):
        """?"""
        # ま
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message("user123", user_context)
        
        form = self.line_interface.create_growth_note_form("user123")
        
        assert form["type"] == "flex"
        assert form["altText"] == "?"
        assert form["contents"]["type"] == "carousel"
        
        # 4つ
        bubbles = form["contents"]["contents"]
        assert len(bubbles) == 4
        
        # ?
        expected_titles = [
            "? ?",
            "? ?", 
            "? ?",
            "? ?"
        ]
        
        for i, bubble in enumerate(bubbles):
            assert bubble["type"] == "bubble"
            assert bubble["size"] == "kilo"
            assert expected_titles[i] in bubble["header"]["contents"][0]["text"]
            assert bubble["footer"]["contents"][0]["action"]["type"] == "postback"
    
    def test_create_growth_note_form_no_session(self):
        """?"""
        form = self.line_interface.create_growth_note_form("nonexistent_user")
        
        assert form["type"] == "text"
        assert "エラー" in form["text"]
        assert "?" in form["text"]
    
    def test_create_input_form(self):
        """?"""
        form = self.line_interface.create_input_form(
            "current_problems", 
            "?",
            "session123"
        )
        
        assert form["type"] == "flex"
        assert "?" in form["altText"]
        assert form["contents"]["type"] == "bubble"
        
        # ヘルパー
        header = form["contents"]["header"]
        assert "? ?" in header["contents"][0]["text"]
        
        # ?
        body = form["contents"]["body"]
        assert "?" in body["contents"][0]["text"]
        
        # ?
        footer = form["contents"]["footer"]
        assert "入力" in footer["contents"][0]["text"]
    
    def test_process_reflection_input_partial(self):
        """?"""
        # ?
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message("user123", user_context)
        
        # 1つ
        response = self.line_interface.process_reflection_input(
            "user123",
            "current_problems",
            "?"
        )
        
        assert response["type"] == "text"
        assert "?" in response["text"]
        assert "?: 1/4" in response["text"]
        assert "quickReply" in response
        
        # ?
        session = self.line_interface.active_sessions["user123"]
        assert "current_problems" in session.responses
        assert session.responses["current_problems"] == "?"
        assert not session.completed
    
    def test_process_reflection_input_complete(self):
        """?"""
        # ?
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message("user123", user_context)
        
        # 4つ
        self.line_interface.process_reflection_input("user123", "current_problems", "?")
        self.line_interface.process_reflection_input("user123", "ideal_world", "?")
        self.line_interface.process_reflection_input("user123", "ideal_emotions", "?")
        
        # ?
        response = self.line_interface.process_reflection_input(
            "user123",
            "tomorrow_actions",
            "?"
        )
        
        assert response["type"] == "flex"
        assert "?" in response["altText"]
        
        # ?
        contents = response["contents"]
        assert contents["type"] == "bubble"
        assert "? ?" in contents["header"]["contents"][0]["text"]
        
        # XP表
        body_contents = contents["body"]["contents"]
        xp_text = next((item["text"] for item in body_contents if "?XP" in item["text"]), None)
        assert xp_text is not None
        assert "+25 XP" in xp_text or "XP" in xp_text
        
        # ?
        session = self.line_interface.active_sessions["user123"]
        assert session.completed
        assert session.xp_earned > 0
        assert len(session.responses) == 4
    
    def test_process_reflection_input_no_session(self):
        """?"""
        response = self.line_interface.process_reflection_input(
            "nonexistent_user",
            "current_problems",
            "?"
        )
        
        assert response["type"] == "text"
        assert "エラー" in response["text"]
        assert "?" in response["text"]
    
    def test_create_reflection_reminder(self):
        """?"""
        reminder = self.line_interface.create_reflection_reminder("user123", 3)
        
        assert reminder["type"] == "flex"
        assert reminder["altText"] == "?"
        assert reminder["contents"]["type"] == "bubble"
        
        # ヘルパー
        header = reminder["contents"]["header"]
        assert "? ?" in header["contents"][0]["text"]
        
        # ?
        body_contents = reminder["contents"]["body"]["contents"]
        missed_days_text = next((item.get("text", "") for item in body_contents if "3?" in item.get("text", "")), None)
        assert missed_days_text is not None
        
        # ?
        footer = reminder["contents"]["footer"]
        buttons = footer["contents"]
        assert len(buttons) == 2
        assert "?" in buttons[0]["action"]["label"]
        assert "?" in buttons[1]["action"]["label"]
    
    def test_get_session_status(self):
        """?"""
        # ?
        status = self.line_interface.get_session_status("nonexistent_user")
        assert status is None
        
        # ?
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message("user123", user_context)
        
        status = self.line_interface.get_session_status("user123")
        assert status is not None
        assert isinstance(status, ReflectionSession)
        assert status.user_id == "user123"
        assert not status.completed
    
    def test_cleanup_old_sessions(self):
        """?"""
        # ?
        user_context = {"mood": 3, "completed_tasks": 2}
        self.line_interface.create_reflection_prompt_message("user1", user_context)
        self.line_interface.create_reflection_prompt_message("user2", user_context)
        
        # 1つ
        old_session = self.line_interface.active_sessions["user1"]
        old_session.started_at = datetime.now() - timedelta(hours=25)
        
        # ?
        cleaned_count = self.line_interface.cleanup_old_sessions(24)
        
        assert cleaned_count == 1
        assert "user1" not in self.line_interface.active_sessions
        assert "user2" in self.line_interface.active_sessions
    
    def test_emotion_display_mapping(self):
        """?"""
        from main import EmotionalTone
        
        # ?
        display = self.line_interface._get_emotion_display(EmotionalTone.VERY_POSITIVE)
        assert "と" in display and "?" in display
        
        display = self.line_interface._get_emotion_display(EmotionalTone.POSITIVE)
        assert "?" in display and "?" in display
        
        display = self.line_interface._get_emotion_display(EmotionalTone.NEUTRAL)
        assert "?" in display and "?" in display
        
        display = self.line_interface._get_emotion_display(EmotionalTone.NEGATIVE)
        assert "?" in display and "?" in display
        
        display = self.line_interface._get_emotion_display(EmotionalTone.VERY_NEGATIVE)
        assert "と" in display and "?" in display
    
    def test_action_display_mapping(self):
        """?"""
        from main import ActionOrientation
        
        # ?
        display = self.line_interface._get_action_display(ActionOrientation.HIGH)
        assert "?" in display and "?" in display
        
        display = self.line_interface._get_action_display(ActionOrientation.MEDIUM)
        assert "?" in display and "?" in display
        
        display = self.line_interface._get_action_display(ActionOrientation.LOW)
        assert "?" in display and "?" in display
    
    def test_reflection_session_dataclass(self):
        """ReflectionSessionデフォルト"""
        session = ReflectionSession(
            user_id="test_user",
            session_id="test_session",
            started_at=datetime.now(),
            prompts={"test": "prompt"},
            responses={"test": "response"}
        )
        
        assert session.user_id == "test_user"
        assert session.session_id == "test_session"
        assert isinstance(session.started_at, datetime)
        assert session.prompts == {"test": "prompt"}
        assert session.responses == {"test": "response"}
        assert not session.completed  # デフォルト
        assert session.xp_earned == 0  # デフォルト

def test_demo_function():
    """デフォルト"""
    from line_bot_integration import demo_line_bot_integration
    
    line_interface = demo_line_bot_integration()
    
    assert isinstance(line_interface, ReflectionLINEInterface)
    assert "user123" in line_interface.active_sessions
    
    # ?
    session = line_interface.active_sessions["user123"]
    assert session.completed
    assert len(session.responses) == 4
    assert session.xp_earned > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])