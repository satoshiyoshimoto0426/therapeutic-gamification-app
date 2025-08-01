"""
?

実装3つ
1. Daily Trio ログ
2. Self-Efficacy Gauge?21?
3. Micro Rewards?3?
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import time

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ?
import importlib.util

# Daily Trio
spec = importlib.util.spec_from_file_location("daily_trio_main", "../daily-trio/main.py")
daily_trio_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily_trio_main)
daily_trio_engine = daily_trio_main.daily_trio_engine
TrioUserState = daily_trio_main.UserState

# Self-Efficacy
spec = importlib.util.spec_from_file_location("self_efficacy_main", "../self-efficacy/main.py")
self_efficacy_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(self_efficacy_main)
efficacy_engine = self_efficacy_main.efficacy_engine
EfficacyUpdateRequest = self_efficacy_main.EfficacyUpdateRequest

# Micro Rewards
spec = importlib.util.spec_from_file_location("micro_rewards_main", "../micro-rewards/main.py")
micro_rewards_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(micro_rewards_main)
micro_rewards_engine = micro_rewards_main.micro_rewards_engine
UserAction = micro_rewards_main.UserAction

async def test_complete_user_journey():
    """?"""
    print("?")
    print("=" * 60)
    
    user_id = "integration_test_user"
    therapeutic_focus = "Self-Discipline"
    
    # === 1. ?Micro Rewards? ===
    print("1. ? - Micro Rewards")
    login_action = UserAction(
        user_id=user_id,
        action_type="login",
        timestamp=datetime.now(),
        context={}
    )
    
    start_time = time.time()
    login_response = await micro_rewards_engine.process_user_action(login_action)
    login_time = (time.time() - start_time) * 1000
    
    print(f"   ? ログ: {login_time:.1f}ms")
    print(f"   ? ?: {login_response.total_xp} XP")
    print(f"   ? お: {login_response.celebration_message}")
    
    # === 2. Daily Trio? ===
    print("\n2. Daily Trio? - ?")
    trio_user_state = TrioUserState(
        user_id=user_id,
        current_state="ACTION",
        mood_trend=0.2,
        energy_level=3,
        available_time=20,
        therapeutic_goals=[therapeutic_focus, "Communication"],
        completed_tasks_today=0,
        streak_days=5,
        adhd_assist_level=1.1
    )
    
    start_time = time.time()
    trio_response = await daily_trio_engine.select_daily_trio(trio_user_state)
    trio_time = (time.time() - start_time) * 1000
    
    print(f"   ? Daily Trio?: {trio_time:.1f}ms")
    print(f"   ? ?: {len(trio_response.trio_tasks)}?")
    print(f"   ? ?: {trio_response.estimated_total_time}?")
    print(f"   ? ?XP: {trio_response.expected_xp}")
    print(f"   ? ?: {trio_response.selection_reasoning}")
    
    # タスク
    for i, task in enumerate(trio_response.trio_tasks):
        print(f"       タスク{i+1}: {task.title} ({task.estimated_duration}?, {task.xp_reward} XP)")
    
    # === 3. タスク3タスク3? ===
    print("\n3. タスク - ?")
    
    total_journey_xp = login_response.total_xp
    completed_tasks = 0
    
    for i, task in enumerate(trio_response.trio_tasks):
        print(f"\n   タスク{i+1}実装: {task.title}")
        
        # タスク
        task_start_action = UserAction(
            user_id=user_id,
            action_type="task_start",
            timestamp=datetime.now(),
            context={"task_id": task.task_id}
        )
        
        start_response = await micro_rewards_engine.process_user_action(task_start_action)
        print(f"     ? ?: {start_response.total_xp} XP")
        
        # タスク3タスク3?
        task_complete_action = UserAction(
            user_id=user_id,
            action_type="task_complete",
            timestamp=datetime.now(),
            context={
                "task_id": task.task_id,
                "tap_count": 2,  # 3タスク
                "duration_seconds": min(task.estimated_duration * 60, 180)  # 3?
            }
        )
        
        start_time = time.time()
        complete_response = await micro_rewards_engine.process_user_action(task_complete_action)
        complete_time = (time.time() - start_time) * 1000
        
        print(f"     ? ?: {complete_time:.1f}ms")
        print(f"     ? ?: {complete_response.total_xp} XP")
        print(f"     ? お: {complete_response.celebration_message}")
        
        # Self-Efficacy Gauge?
        efficacy_request = EfficacyUpdateRequest(
            user_id=user_id,
            therapeutic_focus=therapeutic_focus,
            task_completed=True,
            task_difficulty=task.difficulty,
            mood_rating=4,
            reflection_quality=4
        )
        
        efficacy_response = await efficacy_engine.update_efficacy_gauge(efficacy_request)
        print(f"     ? ?: {efficacy_response['efficacy_increase']:.2f}%")
        
        total_journey_xp += start_response.total_xp + complete_response.total_xp
        completed_tasks += 1
    
    # === 4. ? ===
    print(f"\n4. ?")
    print(f"   ? ?: {completed_tasks}/3")
    print(f"   ? ?XP: {total_journey_xp}")
    
    # ?
    efficacy_dashboard = await efficacy_engine.get_efficacy_dashboard(user_id)
    print(f"   ? ?: {efficacy_dashboard['overall_efficacy_level'].value}")
    print(f"   ? ?: {efficacy_dashboard['average_efficacy_percentage']:.1f}%")
    print(f"   ? ?: {efficacy_dashboard['max_consecutive_days']}?")
    
    # エラー
    engagement_stats = await micro_rewards_engine.get_user_engagement_stats(user_id)
    print(f"   ? ?: {engagement_stats['daily_actions']}?")
    print(f"   ? ?: {engagement_stats['total_actions']}?")
    
    return {
        "completed_tasks": completed_tasks,
        "total_xp": total_journey_xp,
        "efficacy_level": efficacy_dashboard['overall_efficacy_level'].value,
        "daily_actions": engagement_stats['daily_actions']
    }

async def test_21_day_habit_formation_integration():
    """21?"""
    print("\n" + "=" * 60)
    print("21?")
    
    user_id = "habit_formation_integration_user"
    therapeutic_focus = "Self-Discipline"
    
    # 21?
    milestone_days = [1, 7, 14, 21]
    
    for day in milestone_days:
        print(f"\n{day}?:")
        
        # Daily Trio?
        trio_user_state = TrioUserState(
            user_id=user_id,
            current_state="ACTION" if day <= 7 else "CONTINUATION",
            mood_trend=0.1 + (day * 0.01),
            energy_level=3 + (day // 7),
            available_time=20,
            therapeutic_goals=[therapeutic_focus],
            completed_tasks_today=0,
            streak_days=day,
            adhd_assist_level=1.0 + (day * 0.01)
        )
        
        trio_response = await daily_trio_engine.select_daily_trio(trio_user_state)
        print(f"   ? Daily Trio: {len(trio_response.trio_tasks)}?")
        
        # 1つ
        if trio_response.trio_tasks:
            task = trio_response.trio_tasks[0]
            
            # Micro Rewards
            complete_action = UserAction(
                user_id=user_id,
                action_type="task_complete",
                timestamp=datetime.now(),
                context={
                    "task_id": task.task_id,
                    "tap_count": 2,
                    "duration_seconds": 120
                }
            )
            
            micro_response = await micro_rewards_engine.process_user_action(complete_action)
            print(f"   ? Micro Rewards: {micro_response.total_xp} XP")
            
            # Self-Efficacy?
            efficacy_request = EfficacyUpdateRequest(
                user_id=user_id,
                therapeutic_focus=therapeutic_focus,
                task_completed=True,
                task_difficulty=task.difficulty,
                mood_rating=4,
                reflection_quality=4
            )
            
            # ?
            gauge = await efficacy_engine._get_or_create_gauge(user_id, therapeutic_focus)
            gauge.consecutive_days = day
            gauge.total_days_active = day
            gauge.current_percentage = min(100.0, day * 3.0)  # ?
            gauge.current_level = efficacy_engine._calculate_efficacy_level(gauge.current_percentage)
            
            # ?
            milestone_rewards = await efficacy_engine._check_milestones(gauge)
            unlocked_skills = await efficacy_engine._check_passive_skill_unlocks(gauge)
            
            print(f"   ? ?: {gauge.current_percentage:.1f}% ({gauge.current_level.value})")
            print(f"   ? ?: {len(milestone_rewards)}?")
            print(f"   ? ?: {len(unlocked_skills)}?")
            
            if day == 21:
                print(f"   ? 21?")
                print(f"       - ?: {len(gauge.passive_skills)}?")
                print(f"       - ?: {gauge.milestone_reached}")
    
    print("\n? 21?")

async def test_performance_integration():
    """?"""
    print("\n" + "=" * 60)
    print("?")
    
    user_id = "performance_integration_user"
    response_times = []
    
    # ?10?
    for i in range(10):
        start_time = time.time()
        
        # 1. Daily Trio?
        trio_user_state = TrioUserState(
            user_id=f"{user_id}_{i}",
            current_state="ACTION",
            mood_trend=0.2,
            energy_level=3,
            available_time=15,
            therapeutic_goals=["Self-Discipline"],
            completed_tasks_today=0,
            streak_days=3,
            adhd_assist_level=1.1
        )
        
        trio_response = await daily_trio_engine.select_daily_trio(trio_user_state)
        
        # 2. Micro Rewards?
        if trio_response.trio_tasks:
            complete_action = UserAction(
                user_id=f"{user_id}_{i}",
                action_type="task_complete",
                timestamp=datetime.now(),
                context={
                    "task_id": trio_response.trio_tasks[0].task_id,
                    "tap_count": 3,
                    "duration_seconds": 180
                }
            )
            
            micro_response = await micro_rewards_engine.process_user_action(complete_action)
        
        # 3. Self-Efficacy?
        efficacy_request = EfficacyUpdateRequest(
            user_id=f"{user_id}_{i}",
            therapeutic_focus="Self-Discipline",
            task_completed=True,
            task_difficulty=2,
            mood_rating=4,
            reflection_quality=3
        )
        
        efficacy_response = await efficacy_engine.update_efficacy_gauge(efficacy_request)
        
        total_time = (time.time() - start_time) * 1000
        response_times.append(total_time)
    
    # ?
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"   ? ?: {avg_time:.1f}ms")
    print(f"   ? ?: {max_time:.1f}ms")
    print(f"   ? ?: {min_time:.1f}ms")
    print(f"   ? 3?: {'?' if max_time < 180000 else '?'}")
    print(f"   ? 1.2?: {'?' if max_time < 1200 else '?'}")
    
    print("\n? ?")

async def main():
    """メイン"""
    # ?
    journey_result = await test_complete_user_journey()
    
    # 21?
    await test_21_day_habit_formation_integration()
    
    # ?
    await test_performance_integration()
    
    # ?
    print("\n" + "=" * 60)
    print("? ?")
    print("\n? ?:")
    print("1. Daily Trio ログ ?")
    print("   - 1?3つ")
    print("   - ADHD?")
    print("   - AI?")
    
    print("\n2. Self-Efficacy Gauge UI ?")
    print("   - 21?")
    print("   - ?")
    print("   - 治療")
    
    print("\n3. ?3? ?")
    print("   - 3タスク3?")
    print("   - 1.2?")
    print("   - ADHDの")
    print("   - リスト")
    
    print(f"\n? ?:")
    print(f"- ?: {journey_result['completed_tasks']}/3")
    print(f"- ?XP: {journey_result['total_xp']}")
    print(f"- ?: {journey_result['efficacy_level']}")
    print(f"- ?: {journey_result['daily_actions']}")
    
    print(f"\n? ?:")
    print("- Feature Flag基本")
    print("- CBT ABCモデル")
    print("- KPI?")
    print("- ?")

if __name__ == "__main__":
    asyncio.run(main())