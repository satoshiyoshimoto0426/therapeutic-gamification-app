"""
Micro Rewards Service ?

?
"""

import asyncio
import time
from main import micro_rewards_engine, UserAction
from datetime import datetime, timedelta

async def test_basic_functionality():
    """基本"""
    print("Micro Rewards Service ?")
    print("=" * 50)
    
    user_id = "simple_test_user"
    
    # 1. ログ
    print("1. ログ")
    login_action = UserAction(
        user_id=user_id,
        action_type="login",
        timestamp=datetime.now(),
        context={}
    )
    
    start_time = time.time()
    response = await micro_rewards_engine.process_user_action(login_action)
    execution_time = (time.time() - start_time) * 1000
    
    print(f"   ? 実装: {execution_time:.1f}ms")
    print(f"   ? 成: {response.success}")
    print(f"   ? リスト: {len(response.rewards)}?")
    print(f"   ? ?XP: {response.total_xp}")
    print(f"   ? お: {response.celebration_message}")
    print(f"   ? ?: {response.next_action_hint}")
    
    # 2. タスク
    print("\n2. タスク")
    task_start_action = UserAction(
        user_id=user_id,
        action_type="task_start",
        timestamp=datetime.now(),
        context={"task_id": "test_task_001"}
    )
    
    start_time = time.time()
    response = await micro_rewards_engine.process_user_action(task_start_action)
    execution_time = (time.time() - start_time) * 1000
    
    print(f"   ? 実装: {execution_time:.1f}ms")
    print(f"   ? リスト: {len(response.rewards)}?")
    print(f"   ? ?XP: {response.total_xp}")
    print(f"   ? お: {response.celebration_message}")
    
    # 3. 3タスク3?
    print("\n3. 3タスク3?")
    quick_complete_action = UserAction(
        user_id=user_id,
        action_type="task_complete",
        timestamp=datetime.now(),
        context={
            "task_id": "test_task_001",
            "tap_count": 2,  # 3タスク
            "duration_seconds": 120  # 2?3?
        }
    )
    
    start_time = time.time()
    response = await micro_rewards_engine.process_user_action(quick_complete_action)
    execution_time = (time.time() - start_time) * 1000
    
    print(f"   ? 実装: {execution_time:.1f}ms")
    print(f"   ? リスト: {len(response.rewards)}?")
    print(f"   ? ?XP: {response.total_xp}")
    print(f"   ? お: {response.celebration_message}")
    
    # ?
    for i, reward in enumerate(response.rewards):
        print(f"       リスト{i+1}: {reward.title} ({reward.xp_value} XP)")
    
    # 4. リスト
    print("\n4. リスト")
    recovery_user_id = "recovery_test_user"
    
    # ユーザー3?
    user_state = await micro_rewards_engine._get_or_create_user_state(recovery_user_id)
    user_state.last_login = datetime.now() - timedelta(days=3)
    user_state.missed_days = 3
    
    recovery_action = UserAction(
        user_id=recovery_user_id,
        action_type="login",
        timestamp=datetime.now(),
        context={}
    )
    
    response = await micro_rewards_engine.process_user_action(recovery_action)
    
    print(f"   ? リスト: {len(response.rewards)}?")
    print(f"   ? ?XP: {response.total_xp}")
    print(f"   ? お: {response.celebration_message}")
    
    # 5. ?
    print("\n5. ?")
    streak_user_id = "streak_test_user"
    
    # 5?
    for day in range(1, 6):
        user_state = await micro_rewards_engine._get_or_create_user_state(streak_user_id)
        user_state.consecutive_days = day - 1  # ?
        user_state.last_login = datetime.now() - timedelta(days=1)
        
        streak_action = UserAction(
            user_id=streak_user_id,
            action_type="login",
            timestamp=datetime.now(),
            context={}
        )
        
        response = await micro_rewards_engine.process_user_action(streak_action)
        
        if day == 5:  # 5?
            print(f"   ? 5?: {len(response.rewards)}?")
            print(f"   ? ?XP: {response.total_xp}")
            print(f"   ? お: {response.celebration_message}")
    
    # 6. ?
    print("\n6. ?10?")
    performance_user_id = "performance_test_user"
    response_times = []
    
    for i in range(10):
        perf_action = UserAction(
            user_id=performance_user_id,
            action_type="task_complete",
            timestamp=datetime.now(),
            context={"task_id": f"perf_task_{i}"}
        )
        
        start_time = time.time()
        response = await micro_rewards_engine.process_user_action(perf_action)
        execution_time = (time.time() - start_time) * 1000
        
        response_times.append(execution_time)
    
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"   ? ?: {avg_time:.1f}ms")
    print(f"   ? ?: {max_time:.1f}ms")
    print(f"   ? ?: {min_time:.1f}ms")
    print(f"   ? 1.2?: {'?' if max_time < 1200 else '?'}")
    
    # 7. エラー
    print("\n7. エラー")
    stats = await micro_rewards_engine.get_user_engagement_stats(user_id)
    
    print(f"   ? ユーザーID: {stats['user_id']}")
    print(f"   ? ?: {stats['consecutive_days']}?")
    print(f"   ? ?: {stats['daily_actions']}?")
    print(f"   ? ?: {stats['total_actions']}?")
    print(f"   ? リスト: {stats['recovery_boost_available']}")
    
    # 8. リスト
    print("\n8. リスト")
    templates = micro_rewards_engine.reward_templates
    
    print(f"   ? ?: {len(templates)}?")
    print("   ? ?:")
    
    for template in templates[:5]:  # ?5つ
        print(f"       - {template.title}: {template.description} ({template.xp_value} XP)")
    
    print("\n" + "=" * 50)
    print("? Micro Rewards Service ?")
    print("\n?:")
    print("- 3タスク3? ?")
    print("- 1.2? ?")
    print("- ADHDの ?")
    print("- リスト ?")
    print("- ? ?")
    print("- ? ?")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())