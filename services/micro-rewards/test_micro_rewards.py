"""
Micro Rewards Service ?

?
- 3タスク3?
- 1.2?
- リスト
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
import time

# ?
from main import app, micro_rewards_engine, UserAction, RewardType

client = TestClient(app)

class TestMicroRewardsEngine:
    """Micro Rewards エラー"""
    
    async def test_instant_login_reward(self):
        """?"""
        action = UserAction(
            user_id="instant_test_user",
            action_type="login",
            timestamp=datetime.now(),
            context={}
        )
        
        start_time = time.time()
        response = await micro_rewards_engine.process_user_action(action)
        execution_time = (time.time() - start_time) * 1000
        
        assert response.success is True
        assert len(response.rewards) > 0
        assert response.total_xp > 0
        assert execution_time < 1200  # 1.2?
        assert "お" in response.celebration_message or "ログ" in response.celebration_message
        
        print(f"? ?: {execution_time:.1f}ms")
    
    async def test_task_completion_reward(self):
        """タスク"""
        action = UserAction(
            user_id="task_test_user",
            action_type="task_complete",
            timestamp=datetime.now(),
            context={"task_id": "test_task_001"}
        )
        
        start_time = time.time()
        response = await micro_rewards_engine.process_user_action(action)
        execution_time = (time.time() - start_time) * 1000
        
        assert response.success is True
        assert any(reward.reward_type == RewardType.ACHIEVEMENT_BADGE for reward in response.rewards)
        assert response.total_xp >= 15  # タスクXP
        assert execution_time < 1200
        
        print(f"? タスク: {execution_time:.1f}ms")
    
    async def test_three_tap_efficiency_bonus(self):
        """3タスク"""
        action = UserAction(
            user_id="efficiency_test_user",
            action_type="task_complete",
            timestamp=datetime.now(),
            context={
                "tap_count": 2,  # 3タスク
                "task_id": "efficiency_task"
            }
        )
        
        response = await micro_rewards_engine.process_user_action(action)
        
        # ?
        efficiency_rewards = [r for r in response.rewards if "?" in r.title or "efficiency" in r.reward_id]
        assert len(efficiency_rewards) > 0
        
        print("? 3タスク")
    
    async def test_three_minute_speed_bonus(self):
        """3?"""
        action = UserAction(
            user_id="speed_test_user",
            action_type="task_complete",
            timestamp=datetime.now(),
            context={
                "duration_seconds": 120,  # 2? = 120?3?
                "task_id": "speed_task"
            }
        )
        
        response = await micro_rewards_engine.process_user_action(action)
        
        # ストーリー
        speed_rewards = [r for r in response.rewards if "ストーリー" in r.title or "speed" in r.reward_id]
        assert len(speed_rewards) > 0
        
        print("? 3?")
    
    async def test_recovery_boost_system(self):
        """リスト"""
        user_id = "recovery_test_user"
        
        # ユーザー2?
        user_state = await micro_rewards_engine._get_or_create_user_state(user_id)
        user_state.last_login = datetime.now() - timedelta(days=3)
        user_state.missed_days = 3
        
        # ログ
        action = UserAction(
            user_id=user_id,
            action_type="login",
            timestamp=datetime.now(),
            context={}
        )
        
        response = await micro_rewards_engine.process_user_action(action)
        
        # リスト
        recovery_rewards = [r for r in response.rewards if "recovery" in r.reward_id or "?" in r.title]
        assert len(recovery_rewards) > 0
        assert "お" in response.celebration_message
        
        print("? リスト")
    
    async def test_consecutive_login_streak(self):
        """?"""
        user_id = "streak_test_user"
        
        # 5?
        for day in range(1, 6):
            user_state = await micro_rewards_engine._get_or_create_user_state(user_id)
            user_state.consecutive_days = day
            user_state.last_login = datetime.now() - timedelta(days=1)
            
            action = UserAction(
                user_id=user_id,
                action_type="login",
                timestamp=datetime.now(),
                context={}
            )
            
            response = await micro_rewards_engine.process_user_action(action)
            
            if day == 5:  # 5?5の
                streak_rewards = [r for r in response.rewards if "streak" in r.reward_id or "?" in r.title]
                assert len(streak_rewards) > 0
                print(f"? 5?")
        
        print("? ?")
    
    async def test_performance_guarantee(self):
        """?"""
        user_id = "performance_test_user"
        response_times = []
        
        # 10?
        for i in range(10):
            action = UserAction(
                user_id=user_id,
                action_type="task_complete",
                timestamp=datetime.now(),
                context={"task_id": f"perf_task_{i}"}
            )
            
            start_time = time.time()
            response = await micro_rewards_engine.process_user_action(action)
            execution_time = (time.time() - start_time) * 1000
            
            response_times.append(execution_time)
            assert execution_time < 1200  # 1.2?
        
        average_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        print(f"? ?:")
        print(f"  - ?: {average_time:.1f}ms")
        print(f"  - ?: {max_time:.1f}ms")
        print(f"  - ?1.2?: {'?' if max_time < 1200 else '?'}")

class TestADHDOptimization:
    """ADHD?"""
    
    async def test_immediate_feedback_loop(self):
        """?"""
        user_id = "adhd_test_user"
        
        # ログ ? タスク ? タスク3ストーリー
        steps = [
            ("login", {}),
            ("task_start", {"task_id": "adhd_task"}),
            ("task_complete", {"task_id": "adhd_task", "tap_count": 3, "duration_seconds": 150})
        ]
        
        total_xp = 0
        total_time = 0
        
        for step_type, context in steps:
            action = UserAction(
                user_id=user_id,
                action_type=step_type,
                timestamp=datetime.now(),
                context=context
            )
            
            start_time = time.time()
            response = await micro_rewards_engine.process_user_action(action)
            execution_time = (time.time() - start_time) * 1000
            
            total_xp += response.total_xp
            total_time += execution_time
            
            # ?
            assert len(response.rewards) > 0
            assert response.total_xp > 0
            assert len(response.celebration_message) > 0
        
        print(f"? ?:")
        print(f"  - 3ストーリーXP: {total_xp}")
        print(f"  - 3ストーリー: {total_time:.1f}ms")
        print(f"  - ?: {total_time/3:.1f}ms")
    
    async def test_reward_variety_and_engagement(self):
        """リスト"""
        user_id = "variety_test_user"
        reward_types_seen = set()
        
        # ?
        actions = [
            ("login", {}),
            ("task_start", {}),
            ("task_complete", {"duration_seconds": 60}),  # 1?
            ("task_complete", {"tap_count": 2}),  # 2タスク
            ("progress_check", {}),
        ]
        
        for action_type, context in actions:
            action = UserAction(
                user_id=user_id,
                action_type=action_type,
                timestamp=datetime.now(),
                context=context
            )
            
            response = await micro_rewards_engine.process_user_action(action)
            
            for reward in response.rewards:
                reward_types_seen.add(reward.reward_type.value)
        
        # ?
        assert len(reward_types_seen) >= 3
        
        print(f"? リスト: {len(reward_types_seen)}?")
    
    def test_reward_template_adhd_compliance(self):
        """リストADHD準拠"""
        templates = micro_rewards_engine.reward_templates
        
        for template in templates:
            # ?1.5?
            assert template.duration_ms <= 1500
            
            # ?
            assert len(template.visual_effect) > 0
            assert len(template.sound_effect) > 0
            
            # ?
            assert len(template.celebration_message) > 0
        
        print(f"? リストADHD準拠: {len(templates)}?")

class TestAPIEndpoints:
    """APIエラー"""
    
    def test_process_action_endpoint(self):
        """アプリ"""
        action_data = {
            "user_id": "api_test_user",
            "action_type": "login",
            "timestamp": datetime.now().isoformat(),
            "context": {}
        }
        
        response = client.post("/micro-rewards/action", json=action_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "rewards" in data
        assert "total_xp" in data
        assert "execution_time_ms" in data
        
        print("? アプリ")
    
    def test_engagement_stats_endpoint(self):
        """エラー"""
        response = client.get("/micro-rewards/api_stats_user/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "consecutive_days" in data
        assert "daily_actions" in data
        assert "performance_metrics" in data
        
        print("? エラー")
    
    def test_reward_templates_endpoint(self):
        """リスト"""
        response = client.get("/micro-rewards/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "performance_targets" in data
        assert len(data["templates"]) > 0
        
        # ?
        targets = data["performance_targets"]
        assert targets["max_response_time_ms"] == 1200
        assert targets["recovery_boost_threshold_days"] == 2
        
        print("? リスト")
    
    def test_quick_action_endpoint(self):
        """?"""
        response = client.post("/micro-rewards/quick-action", params={
            "user_id": "quick_test_user",
            "action_type": "task_complete",
            "tap_count": 2,
            "duration_seconds": 90
        })
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["execution_time_ms"] < 1200
        
        # 3タスク3?
        rewards = data["rewards"]
        bonus_rewards = [r for r in rewards if "?" in r["title"] or "ストーリー" in r["title"]]
        assert len(bonus_rewards) > 0
        
        print("? ?")

def run_all_tests():
    """?"""
    print("Micro Rewards Service ?")
    print("=" * 50)
    
    # 基本
    engine_tests = TestMicroRewardsEngine()
    
    async def run_async_engine_tests():
        await engine_tests.test_instant_login_reward()
        await engine_tests.test_task_completion_reward()
        await engine_tests.test_three_tap_efficiency_bonus()
        await engine_tests.test_three_minute_speed_bonus()
        await engine_tests.test_recovery_boost_system()
        await engine_tests.test_consecutive_login_streak()
        await engine_tests.test_performance_guarantee()
    
    asyncio.run(run_async_engine_tests())
    
    # ADHD?
    adhd_tests = TestADHDOptimization()
    
    async def run_async_adhd_tests():
        await adhd_tests.test_immediate_feedback_loop()
        await adhd_tests.test_reward_variety_and_engagement()
    
    asyncio.run(run_async_adhd_tests())
    
    adhd_tests.test_reward_template_adhd_compliance()
    
    # APIエラー
    api_tests = TestAPIEndpoints()
    api_tests.test_process_action_endpoint()
    api_tests.test_engagement_stats_endpoint()
    api_tests.test_reward_templates_endpoint()
    api_tests.test_quick_action_endpoint()
    
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
    run_all_tests()