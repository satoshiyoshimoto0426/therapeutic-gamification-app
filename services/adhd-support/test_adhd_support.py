"""
Comprehensive tests for ADHD Support Module
Tests Pomodoro timer, hyperfocus detection, daily buffer, and UI constraints
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from interfaces.core_types import Task, TaskType, TaskStatus

class TestPomodoroTimer:
    """Test Pomodoro timer functionality with 25-5-25-5 cycle"""
    
    @pytest.mark.asyncio
    async def test_pomodoro_cycle_creation(self):
        """Test creating a new Pomodoro cycle"""
        from main import PomodoroTimer
        
        timer = PomodoroTimer("test_user_123")
        cycle = await timer.start_cycle()
        
        assert cycle["user_id"] == "test_user_123"
        assert cycle["current_phase"] == "work"
        assert cycle["phase_duration"] == 25 * 60  # 25 minutes in seconds
        assert cycle["cycle_count"] == 1
        assert cycle["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_pomodoro_phase_transitions(self):
        """Test transitions between work and break phases"""
        from main import PomodoroTimer
        
        timer = PomodoroTimer("test_user_123")
        
        # Start with work phase
        cycle = await timer.start_cycle()
        assert cycle["current_phase"] == "work"
        assert cycle["phase_duration"] == 25 * 60
        
        # Complete work phase, should transition to short break
        next_phase = await timer.complete_phase(cycle["cycle_id"])
        assert next_phase["current_phase"] == "short_break"
        assert next_phase["phase_duration"] == 5 * 60
        
        # Complete short break, should transition to work
        next_phase = await timer.complete_phase(next_phase["cycle_id"])
        assert next_phase["current_phase"] == "work"
        assert next_phase["cycle_count"] == 2

class TestHyperfocusDetection:
    """Test hyperfocus detection system for 60-minute continuous work alerts"""
    
    @pytest.mark.asyncio
    async def test_continuous_work_tracking(self):
        """Test tracking continuous work time"""
        from main import HyperfocusDetector
        
        detector = HyperfocusDetector("test_user_123")
        
        # Start work session
        session = await detector.start_work_session("coding_task")
        assert session["user_id"] == "test_user_123"
        assert session["task_name"] == "coding_task"
        assert session["start_time"] is not None
        assert session["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_hyperfocus_alert_trigger(self):
        """Test hyperfocus alert after 60 minutes"""
        from main import HyperfocusDetector
        
        detector = HyperfocusDetector("test_user_123")
        
        # Mock a work session that started 60 minutes ago
        past_time = datetime.utcnow() - timedelta(minutes=60)
        session = {
            "session_id": "test_session",
            "user_id": "test_user_123",
            "start_time": past_time,
            "is_active": True,
            "break_suggestions": 0
        }
        
        # Check if alert should trigger
        should_alert = await detector.check_hyperfocus_alert(session)
        assert should_alert == True

class TestDailyBuffer:
    """Test daily buffer system allowing 2 free deadline extensions"""
    
    @pytest.mark.asyncio
    async def test_daily_buffer_initialization(self):
        """Test daily buffer initialization"""
        from main import DailyBufferManager
        
        buffer_mgr = DailyBufferManager("test_user_123")
        buffer_status = await buffer_mgr.get_daily_buffer_status()
        
        assert buffer_status["user_id"] == "test_user_123"
        assert buffer_status["extensions_used"] == 0
        assert buffer_status["extensions_available"] == 2
        assert buffer_status["reset_date"] == datetime.utcnow().date()
    
    @pytest.mark.asyncio
    async def test_deadline_extension_request(self):
        """Test requesting deadline extension"""
        from main import DailyBufferManager
        
        buffer_mgr = DailyBufferManager("test_user_123")
        
        # Request extension
        extension_result = await buffer_mgr.request_extension("test_task_123", hours=2)
        
        assert extension_result["granted"] == True
        assert extension_result["new_due_date"] is not None
        assert extension_result["extensions_remaining"] == 1

class TestADHDAssistMultiplier:
    """Test ADHD assist multiplier calculation (1.0-1.3 range)"""
    
    @pytest.mark.asyncio
    async def test_base_multiplier_calculation(self):
        """Test base ADHD assist multiplier"""
        from main import ADHDAssistCalculator
        
        calculator = ADHDAssistCalculator()
        
        # Task with no ADHD support features
        basic_task = {
            "task_id": "basic_task",
            "adhd_support": {}
        }
        
        multiplier = await calculator.calculate_multiplier("test_user", basic_task)
        assert multiplier == 1.0
    
    @pytest.mark.asyncio
    async def test_pomodoro_multiplier_bonus(self):
        """Test multiplier bonus for Pomodoro timer usage"""
        from main import ADHDAssistCalculator
        
        calculator = ADHDAssistCalculator()
        
        # Task with Pomodoro enabled
        pomodoro_task = {
            "task_id": "pomodoro_task",
            "adhd_support": {
                "pomodoro_enabled": True
            }
        }
        
        multiplier = await calculator.calculate_multiplier("test_user", pomodoro_task)
        assert multiplier == 1.1  # Base 1.0 + 0.1 for Pomodoro
    
    @pytest.mark.asyncio
    async def test_maximum_multiplier_cap(self):
        """Test that multiplier is capped at 1.3"""
        from main import ADHDAssistCalculator
        
        calculator = ADHDAssistCalculator()
        
        # Task with all ADHD support features enabled
        full_support_task = {
            "task_id": "full_support_task",
            "adhd_support": {
                "pomodoro_enabled": True,
                "reminders_enabled": True,
                "break_detection": True,
                "hyperfocus_alerts": True,
                "daily_buffer_used": True,
                "ui_optimized": True
            }
        }
        
        multiplier = await calculator.calculate_multiplier("test_user", full_support_task)
        assert multiplier == 1.3  # Should be capped at maximum

class TestTimePerceptionSupport:
    """Test 15-minute time perception reminder system"""
    
    @pytest.mark.asyncio
    async def test_start_time_perception_reminders(self):
        """Test starting 15-minute reminders"""
        from main import TimePerceptionSupport
        
        time_support = TimePerceptionSupport("test_user_123")
        reminder = await time_support.start_time_perception_reminders("coding_task")
        
        assert reminder["user_id"] == "test_user_123"
        assert reminder["task_name"] == "coding_task"
        assert reminder["reminder_count"] == 0
        assert reminder["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_trigger_reminder(self):
        """Test triggering 15-minute reminder"""
        from main import TimePerceptionSupport
        
        time_support = TimePerceptionSupport("test_user_123")
        
        # Start reminder
        reminder = await time_support.start_time_perception_reminders("coding_task")
        
        # Trigger reminder
        result = await time_support.trigger_reminder(reminder["reminder_id"])
        
        assert result["reminder_triggered"] == True
        assert result["task_name"] == "coding_task"
        assert result["reminder_count"] == 1
        assert "⏰" in result["message"]

class TestUIConstraintValidator:
    """Test UI constraint validation for ADHD-friendly design"""
    
    @pytest.mark.asyncio
    async def test_validate_screen_with_too_many_choices(self):
        """Test screen validation with too many choices"""
        from main import UIConstraintValidator
        
        validator = UIConstraintValidator()
        
        # Screen with too many choices
        screen_config = {
            "screen_id": "test_screen",
            "choice_count": 5,  # Exceeds limit of 3
            "primary_actions": ["submit"]
        }
        
        result = await validator.validate_screen(screen_config)
        
        assert result["is_valid"] == False
        assert "too_many_choices" in result["violations"]
    
    @pytest.mark.asyncio
    async def test_assess_cognitive_load(self):
        """Test cognitive load assessment"""
        from main import UIConstraintValidator
        
        validator = UIConstraintValidator()
        
        # High cognitive load screen
        high_load_screen = {
            "information_density": "high",
            "simultaneous_inputs": 3,
            "visual_elements": 15
        }
        
        result = await validator.assess_cognitive_load(high_load_screen)
        
        assert result["load_level"] == "high"
        assert result["adhd_friendly"] == False
    
    @pytest.mark.asyncio
    async def test_get_adhd_optimizations(self):
        """Test ADHD optimization suggestions"""
        from main import UIConstraintValidator
        
        validator = UIConstraintValidator()
        
        # Screen needing optimization
        screen_config = {
            "choice_count": 5,
            "color_contrast": "low"
        }
        
        suggestions = await validator.get_adhd_optimizations(screen_config)
        
        assert len(suggestions) == 2
        assert any(s["type"] == "reduce_choices" for s in suggestions)
        assert any(s["type"] == "improve_contrast" for s in suggestions)

class TestLINENotificationService:
    """Test LINE notification service with rate limiting"""
    
    @pytest.mark.asyncio
    async def test_send_pomodoro_notification(self):
        """Test sending Pomodoro notifications"""
        from main import LINENotificationService
        
        notification_service = LINENotificationService()
        
        notification_data = {
            "user_id": "test_user_123",
            "message_type": "pomodoro_start",
            "duration": 25
        }
        
        await notification_service.send_pomodoro_notification(notification_data)
        
        # Check notification was recorded
        frequency = await notification_service.get_notification_frequency("test_user_123")
        assert frequency["daily_count"] == 1
    
    @pytest.mark.asyncio
    async def test_escalating_break_reminders(self):
        """Test escalating break reminder messages"""
        from main import LINENotificationService
        
        notification_service = LINENotificationService()
        
        # First reminder (gentle)
        notification_data = {
            "user_id": "test_user_123",
            "work_duration": 60,
            "suggestion_count": 0
        }
        
        await notification_service.send_break_reminder(notification_data)
        
        # Second reminder (concerned)
        notification_data["suggestion_count"] = 1
        await notification_service.send_break_reminder(notification_data)
        
        # Third reminder (firm)
        notification_data["suggestion_count"] = 2
        await notification_service.send_break_reminder(notification_data)
        
        frequency = await notification_service.get_notification_frequency("test_user_123")
        assert frequency["daily_count"] == 3

class TestADHDSupportService:
    """Test integrated ADHD support service"""
    
    @pytest.mark.asyncio
    async def test_start_supported_work_session(self):
        """Test starting work session with full ADHD support"""
        from main import ADHDSupportService
        
        adhd_service = ADHDSupportService("test_user_123")
        
        config = {
            "pomodoro_enabled": True,
            "break_detection": True,
            "reminders_enabled": True
        }
        
        session = await adhd_service.start_supported_work_session("coding_task", config)
        
        assert session["task_name"] == "coding_task"
        assert session["user_id"] == "test_user_123"
        assert session["pomodoro_active"] == True
        assert session["hyperfocus_monitoring"] == True
        assert "adhd_multiplier" in session
    
    @pytest.mark.asyncio
    async def test_adapt_support_features(self):
        """Test adaptive support feature recommendations"""
        from main import ADHDSupportService
        
        adhd_service = ADHDSupportService("test_user_123")
        
        behavior_data = {
            "pomodoro_completion_rate": 0.3,  # Low completion rate
            "break_compliance": 0.8,  # Good break compliance
            "hyperfocus_episodes": 3  # High hyperfocus episodes
        }
        
        adaptations = await adhd_service.adapt_support_features(behavior_data)
        
        assert "reduce_pomodoro_duration" in adaptations["recommendations"]
        assert "maintain_break_system" in adaptations["recommendations"]
        assert "increase_break_frequency" in adaptations["recommendations"]
        assert adaptations["new_multiplier"] > 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])