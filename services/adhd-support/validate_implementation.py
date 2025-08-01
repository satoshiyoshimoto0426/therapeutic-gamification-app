#!/usr/bin/env python3
"""
ADHD Support Module Implementation Validation
Validates all core ADHD support features according to requirements
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

async def validate_pomodoro_timer():
    """Validate Pomodoro timer with 25-5-25-5 cycle"""
    print("? Validating Pomodoro Timer...")
    
    try:
        from main import PomodoroTimer
        
        timer = PomodoroTimer("test_user_123")
        
        # Test cycle creation
        cycle = await timer.start_cycle()
        assert cycle["current_phase"] == "work"
        assert cycle["phase_duration"] == 25 * 60  # 25 minutes
        print("  ? Pomodoro cycle creation: PASS")
        
        # Test phase transition
        next_phase = await timer.complete_phase(cycle["cycle_id"])
        assert next_phase["current_phase"] == "short_break"
        assert next_phase["phase_duration"] == 5 * 60  # 5 minutes
        print("  ? Work to break transition: PASS")
        
        # Test pause/resume
        paused = await timer.pause_cycle(cycle["cycle_id"])
        assert paused["is_active"] == False
        print("  ? Pause functionality: PASS")
        
        resumed = await timer.resume_cycle(cycle["cycle_id"])
        assert resumed["is_active"] == True
        print("  ? Resume functionality: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Pomodoro Timer validation failed: {e}")
        return False

async def validate_hyperfocus_detection():
    """Validate hyperfocus detection system (60-minute alerts)"""
    print("? Validating Hyperfocus Detection...")
    
    try:
        from main import HyperfocusDetector
        
        detector = HyperfocusDetector("test_user_123")
        
        # Test work session start
        session = await detector.start_work_session("coding_task")
        assert session["task_name"] == "coding_task"
        assert session["is_active"] == True
        print("  ? Work session tracking: PASS")
        
        # Test hyperfocus alert logic
        past_session = {
            "session_id": "test_session",
            "user_id": "test_user_123",
            "start_time": datetime.utcnow() - timedelta(minutes=60),
            "is_active": True,
            "break_suggestions": 0
        }
        
        should_alert = await detector.check_hyperfocus_alert(past_session)
        assert should_alert == True
        print("  ? 60-minute hyperfocus detection: PASS")
        
        # Test escalating break suggestions
        suggestion = await detector.generate_break_suggestion(0)
        assert suggestion["urgency_level"] == "gentle"
        print("  ? Gentle break suggestion: PASS")
        
        suggestion = await detector.generate_break_suggestion(2)
        assert suggestion["urgency_level"] == "firm"
        assert suggestion.get("force_break") == True
        print("  ? Escalating break suggestions: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Hyperfocus Detection validation failed: {e}")
        return False

async def validate_daily_buffer():
    """Validate daily buffer system (2 free extensions)"""
    print("? Validating Daily Buffer System...")
    
    try:
        from main import DailyBufferManager
        
        buffer_mgr = DailyBufferManager("test_user_123")
        
        # Test buffer initialization
        status = await buffer_mgr.get_daily_buffer_status()
        assert status["extensions_available"] == 2
        assert status["extensions_used"] == 0
        print("  ? Daily buffer initialization: PASS")
        
        # Test first extension
        extension1 = await buffer_mgr.request_extension("task_1", hours=2)
        assert extension1["granted"] == True
        assert extension1["extensions_remaining"] == 1
        print("  ? First extension request: PASS")
        
        # Test second extension
        extension2 = await buffer_mgr.request_extension("task_2", hours=2)
        assert extension2["granted"] == True
        assert extension2["extensions_remaining"] == 0
        print("  ? Second extension request: PASS")
        
        # Test limit exceeded
        extension3 = await buffer_mgr.request_extension("task_3", hours=2)
        assert extension3["granted"] == False
        assert extension3["reason"] == "daily_limit_exceeded"
        print("  ? Extension limit enforcement: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Daily Buffer validation failed: {e}")
        return False

async def validate_ui_constraints():
    """Validate One-Screen, One-Action UI constraints"""
    print("? Validating UI Constraints...")
    
    try:
        from main import UIConstraintValidator
        
        validator = UIConstraintValidator()
        
        # Test valid screen
        valid_screen = {
            "screen_id": "valid_screen",
            "choice_count": 2,
            "primary_actions": ["submit"]
        }
        
        result = await validator.validate_screen(valid_screen)
        assert result["is_valid"] == True
        print("  ? Valid screen validation: PASS")
        
        # Test invalid screen (too many choices)
        invalid_screen = {
            "screen_id": "invalid_screen",
            "choice_count": 5,  # Exceeds limit of 3
            "primary_actions": ["submit", "cancel"]  # Multiple primary actions
        }
        
        result = await validator.validate_screen(invalid_screen)
        assert result["is_valid"] == False
        assert "too_many_choices" in result["violations"]
        assert "multiple_primary_actions" in result["violations"]
        print("  ? Invalid screen detection: PASS")
        
        # Test cognitive load assessment
        high_load_screen = {
            "information_density": "high",
            "simultaneous_inputs": 3,
            "visual_elements": 15
        }
        
        load_result = await validator.assess_cognitive_load(high_load_screen)
        assert load_result["load_level"] == "high"
        assert load_result["adhd_friendly"] == False
        print("  ? Cognitive load assessment: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? UI Constraints validation failed: {e}")
        return False

async def validate_adhd_multiplier():
    """Validate ADHD assist multiplier (1.0-1.3 range)"""
    print("? Validating ADHD Assist Multiplier...")
    
    try:
        from main import ADHDAssistCalculator
        
        calculator = ADHDAssistCalculator()
        
        # Test base multiplier
        basic_task = {"adhd_support": {}}
        multiplier = await calculator.calculate_multiplier("test_user", basic_task)
        assert multiplier == 1.0
        print("  ? Base multiplier (1.0): PASS")
        
        # Test single feature bonus
        pomodoro_task = {"adhd_support": {"pomodoro_enabled": True}}
        multiplier = await calculator.calculate_multiplier("test_user", pomodoro_task)
        assert multiplier == 1.1
        print("  ? Single feature bonus: PASS")
        
        # Test maximum multiplier cap
        full_support_task = {
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
        print("  ? Maximum multiplier cap (1.3): PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? ADHD Multiplier validation failed: {e}")
        return False

async def validate_time_perception_support():
    """Validate 15-minute time perception reminders"""
    print("? Validating Time Perception Support...")
    
    try:
        from main import TimePerceptionSupport
        
        time_support = TimePerceptionSupport("test_user_123")
        
        # Test reminder initialization
        reminder = await time_support.start_time_perception_reminders("coding_task")
        assert reminder["task_name"] == "coding_task"
        assert reminder["reminder_count"] == 0
        print("  ? Reminder initialization: PASS")
        
        # Test reminder trigger
        result = await time_support.trigger_reminder(reminder["reminder_id"])
        assert result["reminder_triggered"] == True
        assert result["reminder_count"] == 1
        assert "?" in result["message"]
        print("  ? 15-minute reminder trigger: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Time Perception Support validation failed: {e}")
        return False

async def validate_line_notifications():
    """Validate LINE notification service"""
    print("? Validating LINE Notification Service...")
    
    try:
        from main import LINENotificationService
        
        notification_service = LINENotificationService()
        
        # Test Pomodoro notification
        pomodoro_data = {
            "user_id": "test_user_123",
            "message_type": "pomodoro_start",
            "duration": 25
        }
        
        await notification_service.send_pomodoro_notification(pomodoro_data)
        print("  ? Pomodoro notification: PASS")
        
        # Test break reminder with escalation
        break_data = {
            "user_id": "test_user_123",
            "work_duration": 60,
            "suggestion_count": 0
        }
        
        await notification_service.send_break_reminder(break_data)
        print("  ? Break reminder notification: PASS")
        
        # Test notification frequency tracking
        frequency = await notification_service.get_notification_frequency("test_user_123")
        assert frequency["daily_count"] >= 2
        print("  ? Notification frequency tracking: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? LINE Notification validation failed: {e}")
        return False

async def validate_integrated_service():
    """Validate integrated ADHD support service"""
    print("? Validating Integrated ADHD Support Service...")
    
    try:
        from main import ADHDSupportService
        
        adhd_service = ADHDSupportService("test_user_123")
        
        # Test full support session
        config = {
            "pomodoro_enabled": True,
            "break_detection": True,
            "reminders_enabled": True
        }
        
        session = await adhd_service.start_supported_work_session("coding_task", config)
        assert session["task_name"] == "coding_task"
        assert session["pomodoro_active"] == True
        assert session["hyperfocus_monitoring"] == True
        assert "adhd_multiplier" in session
        print("  ? Integrated work session: PASS")
        
        # Test adaptive features
        behavior_data = {
            "pomodoro_completion_rate": 0.3,
            "break_compliance": 0.8,
            "hyperfocus_episodes": 3
        }
        
        adaptations = await adhd_service.adapt_support_features(behavior_data)
        assert len(adaptations["recommendations"]) > 0
        assert adaptations["new_multiplier"] > 1.0
        print("  ? Adaptive feature recommendations: PASS")
        
        return True
        
    except Exception as e:
        print(f"  ? Integrated Service validation failed: {e}")
        return False

async def main():
    """Run all ADHD support module validations"""
    print("? ADHD Support Module Implementation Validation")
    print("=" * 60)
    
    validations = [
        validate_pomodoro_timer,
        validate_hyperfocus_detection,
        validate_daily_buffer,
        validate_ui_constraints,
        validate_adhd_multiplier,
        validate_time_perception_support,
        validate_line_notifications,
        validate_integrated_service
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
        print("? All ADHD support features validated successfully!")
        print("? Requirements 3.2, 3.4, 3.5, 5.3, 5.5 satisfied")
        return True
    else:
        print("? Some validations failed. Please review implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)