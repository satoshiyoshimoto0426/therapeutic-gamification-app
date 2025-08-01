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
    PomodoroIntegrationService, PomodoroSessionStatus, BreakType
)


async def test_pomodoro_basic_flow():
    """Pomodoro基本"""
    print("=== Pomodoro基本 ===")
    
    service = PomodoroIntegrationService()
    uid = "test_user_123"
    task_id = "task_test_123"
    
    try:
        # 1. Pomodoro?
        print("1. Pomodoro?...")
        session = await service.start_pomodoro_session(
            uid=uid,
            task_id=task_id,
            duration=25,
            focus_music_enabled=True
        )
        
        assert session.status == PomodoroSessionStatus.ACTIVE
        assert session.planned_duration == 25
        assert session.focus_music_enabled is True
        print(f"   ? ?: {session.session_id}")
        
        # 2. Pomodoro?
        print("2. Pomodoro?...")
        completed_session = await service.complete_pomodoro_session(
            session_id=session.session_id,
            actual_duration=23,
            notes="?"
        )
        
        assert completed_session.status == PomodoroSessionStatus.COMPLETED
        assert completed_session.actual_duration == 23
        print("   ? ?")
        
        # 3. ADHD支援
        print("3. ADHD支援...")
        multiplier = service.calculate_adhd_assist_multiplier(uid)
        assert 1.0 <= multiplier <= 1.3
        print(f"   ? ADHD支援: {multiplier}")
        
        # 4. ?
        print("4. ?...")
        stats = await service.get_user_pomodoro_statistics(uid, 30)
        assert stats["total_sessions"] == 1
        assert stats["completed_sessions"] == 1
        assert stats["completion_rate"] == 1.0
        print(f"   ? ?: {stats['total_sessions']}?")
        
        print("? Pomodoro基本")
        return True
        
    except Exception as e:
        print(f"? Pomodoro基本: {str(e)}")
        return False


async def test_continuous_work_monitoring():
    """?3.2?"""
    print("\n=== ? ===")
    
    service = PomodoroIntegrationService()
    uid = "test_user_456"
    
    try:
        # 60?
        print("1. 60?...")
        past_time = datetime.utcnow() - timedelta(minutes=65)
        from pomodoro_integration import WorkSession
        
        service.work_sessions[uid] = WorkSession(
            uid=uid,
            start_time=past_time,
            is_active=True
        )
        
        # ?
        print("2. ?...")
        work_check = await service.check_continuous_work_time(uid)
        
        assert work_check["continuous_minutes"] >= 60
        assert work_check["needs_break"] is True
        assert work_check["break_suggestion"] is not None
        print(f"   ? ?: {work_check['continuous_minutes']}?")
        print(f"   ? ?: {work_check['break_suggestion']['type']}")
        
        # ?1?
        print("3. ?1?...")
        refusal1 = await service.handle_break_refusal(uid)
        assert refusal1["refusal_count"] == 1
        assert refusal1["show_mother_concern"] is False
        print("   ? 1?")
        
        # ?2?
        print("4. ?2?...")
        refusal2 = await service.handle_break_refusal(uid)
        assert refusal2["refusal_count"] == 2
        assert refusal2["show_mother_concern"] is True
        assert refusal2["mandatory_break_required"] is True
        assert "お" in refusal2["narrative"]
        print("   ? ?")
        
        print("? ?")
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


async def test_adhd_assist_multiplier_calculation():
    """ADHD支援5.3?"""
    print("\n=== ADHD支援 ===")
    
    service = PomodoroIntegrationService()
    uid = "test_user_789"
    
    try:
        # ?
        print("1. ?ADHD支援...")
        multiplier_initial = service.calculate_adhd_assist_multiplier(uid)
        assert multiplier_initial == 1.0
        print(f"   ? ?: {multiplier_initial}")
        
        # ?
        print("2. 使用...")
        from pomodoro_integration import ADHDSupportMetrics
        
        service.adhd_metrics[uid] = ADHDSupportMetrics(
            uid=uid,
            total_pomodoro_sessions=20,
            successful_sessions=18,
            usage_frequency_score=0.8,  # ?
            break_compliance_rate=0.9   # ?
        )
        
        # 使用
        print("3. 使用...")
        multiplier_with_data = service.calculate_adhd_assist_multiplier(uid)
        assert multiplier_with_data > multiplier_initial
        assert 1.2 <= multiplier_with_data <= 1.3
        print(f"   ? 使用: {multiplier_with_data}")
        
        # ?
        print("4. ?...")
        task_id = "task_test_789"
        
        # 3つ
        for i in range(3):
            session = await service.start_pomodoro_session(uid, f"{task_id}_{i}")
            await service.complete_pomodoro_session(session.session_id)
        
        # 係数
        multiplier_after_sessions = service.calculate_adhd_assist_multiplier(uid)
        print(f"   ? ?: {multiplier_after_sessions}")
        
        print("? ADHD支援")
        return True
        
    except Exception as e:
        print(f"? ADHD支援: {str(e)}")
        return False


async def test_break_management():
    """?"""
    print("\n=== ? ===")
    
    service = PomodoroIntegrationService()
    uid = "test_user_break"
    task_id = "task_break_test"
    
    try:
        # ?
        print("1. Pomodoro?...")
        session = await service.start_pomodoro_session(uid, task_id)
        await service.complete_pomodoro_session(session.session_id)
        
        # ?
        print("2. ?...")
        break_session = await service.start_break(
            session_id=session.session_id,
            break_type=BreakType.SHORT
        )
        
        assert break_session.status == PomodoroSessionStatus.BREAK
        assert break_session.break_type == BreakType.SHORT
        assert break_session.break_duration == 5
        print("   ? ?")
        
        # ?
        print("3. ?...")
        completed_break = await service.complete_break(session.session_id)
        assert completed_break.status == PomodoroSessionStatus.COMPLETED
        print("   ? ?")
        
        # ?
        print("4. ?...")
        session2 = await service.start_pomodoro_session(uid, task_id)
        await service.complete_pomodoro_session(session2.session_id)
        
        mandatory_break = await service.start_break(
            session_id=session2.session_id,
            break_type=BreakType.MANDATORY
        )
        
        assert mandatory_break.break_type == BreakType.MANDATORY
        assert mandatory_break.break_duration == 15
        print("   ? ?")
        
        print("? ?")
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


async def main():
    """メイン"""
    print("? Pomodoro?ADHD支援")
    print("=" * 50)
    
    tests = [
        test_pomodoro_basic_flow,
        test_continuous_work_monitoring,
        test_adhd_assist_multiplier_calculation,
        test_break_management
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("? ?")
    print(f"成: {sum(results)}/{len(results)}")
    
    if all(results):
        print("? ?")
        print("\n実装:")
        print("? Pomodoro?")
        print("? ADHD支援")
        print("? 60?")
        print("? 2?")
        print("? ?")
        print("? ?")
        print("? ?")
        return True
    else:
        print("? 一般")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)