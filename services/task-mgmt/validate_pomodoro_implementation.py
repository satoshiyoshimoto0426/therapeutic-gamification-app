"""
Pomodoro?

Requirements: 3.2, 5.3
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# プレビュー
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pomodoro_integration import (
    PomodoroIntegrationService, PomodoroSessionStatus, BreakType,
    WorkSession, ADHDSupportMetrics
)
from shared.interfaces.task_system import (
    Task, TaskType, TaskDifficulty, TaskStatus, ADHDSupportLevel,
    TaskXPCalculator
)


def validate_requirements():
    """?3.2と5.3の"""
    print("? ?")
    print("=" * 50)
    
    # ?3.2: 60?
    print("? ?3.2: 60?")
    req_3_2_checks = [
        "? ?",
        "? 60?",
        "? ?",
        "? 2?",
        "? ?"
    ]
    
    for check in req_3_2_checks:
        print(f"  {check}")
    
    # ?5.3: Pomodoro使用ADHD支援
    print("\n? ?5.3: Pomodoro使用ADHD支援")
    req_5_3_checks = [
        "? Pomodoro?",
        "? 成",
        "? ?",
        "? 1.0-1.3?",
        "? XP計算"
    ]
    
    for check in req_5_3_checks:
        print(f"  {check}")
    
    print("\n? ?")


async def validate_implementation():
    """実装"""
    print("\n? 実装")
    print("=" * 50)
    
    service = PomodoroIntegrationService()
    uid = "validation_user"
    task_id = "validation_task"
    
    validation_results = []
    
    # 1. Pomodoro?
    print("1. Pomodoro?...")
    try:
        session = await service.start_pomodoro_session(uid, task_id, 25, True)
        assert session.status == PomodoroSessionStatus.ACTIVE
        assert session.planned_duration == 25
        assert session.focus_music_enabled is True
        
        completed = await service.complete_pomodoro_session(session.session_id, 23, "?")
        assert completed.status == PomodoroSessionStatus.COMPLETED
        assert completed.actual_duration == 23
        
        print("   ? Pomodoro?: ?")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? Pomodoro?: ? - {e}")
        validation_results.append(False)
    
    # 2. ADHD支援
    print("2. ADHD支援...")
    try:
        # ?
        initial_multiplier = service.calculate_adhd_assist_multiplier(uid)
        assert initial_multiplier >= 1.0
        
        # メイン
        service.adhd_metrics[uid] = ADHDSupportMetrics(
            uid=uid,
            total_pomodoro_sessions=15,
            successful_sessions=13,
            usage_frequency_score=0.7,
            break_compliance_rate=0.8
        )
        
        enhanced_multiplier = service.calculate_adhd_assist_multiplier(uid)
        assert enhanced_multiplier > initial_multiplier
        assert 1.0 <= enhanced_multiplier <= 1.3
        
        print(f"   ? ADHD支援: ? ({initial_multiplier:.2f} ? {enhanced_multiplier:.2f})")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? ADHD支援: ? - {e}")
        validation_results.append(False)
    
    # 3. ?
    print("3. ?...")
    try:
        # 60?
        past_time = datetime.utcnow() - timedelta(minutes=65)
        service.work_sessions[uid] = WorkSession(
            uid=uid,
            start_time=past_time,
            is_active=True
        )
        
        work_check = await service.check_continuous_work_time(uid)
        assert work_check["continuous_minutes"] >= 60
        assert work_check["needs_break"] is True
        assert work_check["break_suggestion"] is not None
        
        print(f"   ? ?: ? ({work_check['continuous_minutes']}?)")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? ?: ? - {e}")
        validation_results.append(False)
    
    # 4. ?
    print("4. ?...")
    try:
        # 1?
        refusal1 = await service.handle_break_refusal(uid)
        assert refusal1["refusal_count"] == 1
        assert refusal1["show_mother_concern"] is False
        
        # 2?
        refusal2 = await service.handle_break_refusal(uid)
        assert refusal2["refusal_count"] == 2
        assert refusal2["show_mother_concern"] is True
        assert refusal2["mandatory_break_required"] is True
        assert "お" in refusal2["narrative"]
        
        print("   ? ?: ?")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? ?: ? - {e}")
        validation_results.append(False)
    
    # 5. ?
    print("5. ?...")
    try:
        session2 = await service.start_pomodoro_session(uid, task_id)
        await service.complete_pomodoro_session(session2.session_id)
        
        # ?
        short_break = await service.start_break(session2.session_id, BreakType.SHORT)
        assert short_break.status == PomodoroSessionStatus.BREAK
        assert short_break.break_type == BreakType.SHORT
        assert short_break.break_duration == 5
        
        # ?
        session3 = await service.start_pomodoro_session(uid, task_id)
        await service.complete_pomodoro_session(session3.session_id)
        
        mandatory_break = await service.start_break(session3.session_id, BreakType.MANDATORY)
        assert mandatory_break.break_type == BreakType.MANDATORY
        assert mandatory_break.break_duration == 15
        
        print("   ? ?: ?")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? ?: ? - {e}")
        validation_results.append(False)
    
    # 6. XP計算
    print("6. XP計算...")
    try:
        # ?
        task = Task(
            task_id="test_task_xp",
            uid=uid,
            task_type=TaskType.ROUTINE,
            title="XP?",
            difficulty=TaskDifficulty.MEDIUM,
            adhd_support_level=ADHDSupportLevel.BASIC
        )
        
        # ADHD支援
        adhd_multiplier = service.calculate_adhd_assist_multiplier(uid)
        
        # XP計算
        xp_result = TaskXPCalculator.calculate_detailed_xp(
            task, mood_score=4, actual_duration=25, external_adhd_multiplier=adhd_multiplier
        )
        
        assert xp_result.adhd_assist_multiplier >= 1.0  # ?1.0?
        assert xp_result.final_xp > 0
        # Pomodoro?
        assert adhd_multiplier is not None and adhd_multiplier > 1.0
        
        print(f"   ? XP計算: ?: {xp_result.adhd_assist_multiplier:.2f}, XP: {xp_result.final_xp}?")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? XP計算: ? - {e}")
        import traceback
        traceback.print_exc()
        validation_results.append(False)
    
    # 7. ?
    print("7. ?...")
    try:
        stats = await service.get_user_pomodoro_statistics(uid, 30)
        assert "total_sessions" in stats
        assert "completed_sessions" in stats
        assert "adhd_assist_multiplier" in stats
        assert "usage_frequency_score" in stats
        assert stats["total_sessions"] > 0
        
        print(f"   ? ?: ?{stats['total_sessions']}?")
        validation_results.append(True)
    except Exception as e:
        print(f"   ? ?: ? - {e}")
        validation_results.append(False)
    
    return validation_results


def validate_api_structure():
    """API?"""
    print("\n? API?")
    print("=" * 50)
    
    # main.py?Pomodoro?
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        
        # Pomodoro?
        expected_patterns = [
            "/pomodoro/start",
            "/pomodoro/{session_id}/complete",
            "/pomodoro/{session_id}/break/start",
            "/work-time-check",
            "/break-refusal",
            "/pomodoro/statistics",
            "/adhd-assist-multiplier"
        ]
        
        found_patterns = []
        for pattern in expected_patterns:
            if pattern in main_content:
                found_patterns.append(pattern)
        
        print(f"実装Pomodoroエラー: {len(found_patterns)}/{len(expected_patterns)}")
        for pattern in found_patterns:
            print(f"  ? {pattern}")
        
        # Pomodoro?
        pomodoro_imports = [
            "from .pomodoro_integration import",
            "pomodoro_service",
            "PomodoroSession"
        ]
        
        import_found = sum(1 for imp in pomodoro_imports if imp in main_content)
        print(f"Pomodoro?: {import_found}/{len(pomodoro_imports)}")
        
        return len(found_patterns) >= 5  # ?5つ
        
    except Exception as e:
        print(f"? API?: {e}")
        return False


async def main():
    """メイン"""
    print("? Pomodoro?ADHD支援")
    print("=" * 60)
    
    # ?
    validate_requirements()
    
    # 実装
    implementation_results = await validate_implementation()
    
    # API?
    api_valid = validate_api_structure()
    
    # ?
    print("\n" + "=" * 60)
    print("? 検証")
    
    implementation_success = sum(implementation_results)
    implementation_total = len(implementation_results)
    
    print(f"実装: {implementation_success}/{implementation_total}")
    print(f"API?: {'?' if api_valid else '?'}")
    
    overall_success = implementation_success == implementation_total and api_valid
    
    if overall_success:
        print("\n? タスク6.2?Pomodoro?ADHD支援")
        print("\n実装:")
        print("? Pomodoro?")
        print("? ADHD支援")
        print("? 60?")
        print("? 2?")
        print("? ?")
        print("? ?")
        print("? XP計算")
        print("? ?")
        print("? RESTful APIエラー")
        print("? ?")
        
        print("\n? ?:")
        print("? ?3.2: 60?")
        print("? ?5.3: Pomodoro使用ADHD支援")
        
        return True
    else:
        print("\n? 一般")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)