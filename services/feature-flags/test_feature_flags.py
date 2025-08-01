"""
Feature Flag Service ?

?
- A/B?Kill-Switch?
- 治療
- リスト
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

# ?
from main import app, feature_flag_engine, UserContext, ABTestConfig, TargetingRule

client = TestClient(app)

class TestFeatureFlagEngine:
    """Feature Flag エラー"""
    
    async def test_basic_flag_evaluation(self):
        """基本"""
        user_context = UserContext(
            user_id="test_user_001",
            attributes={
                "age": 25,
                "adhd_level": "moderate",
                "therapeutic_state": "ACTION",
                "user_type": "standard"
            }
        )
        
        # Daily Trio?
        evaluation = await feature_flag_engine.evaluate_flag("daily_trio_enabled", user_context)
        
        assert evaluation.flag_key == "daily_trio_enabled"
        assert evaluation.value is True  # デフォルト
        assert evaluation.user_id == "test_user_001"
        assert evaluation.reason in ["default_value", "targeting_rule_match"]
        
        print("? 基本")
    
    async def test_targeting_rule_evaluation(self):
        """タスク"""
        user_context = UserContext(
            user_id="beta_user_001",
            attributes={
                "user_type": "beta",
                "adhd_level": "high",
                "therapeutic_state": "CONTINUATION"
            }
        )
        
        # CBT?
        evaluation = await feature_flag_engine.evaluate_flag("new_cbt_integration", user_context)
        
        assert evaluation.flag_key == "new_cbt_integration"
        assert evaluation.value is True  # ?
        assert evaluation.reason == "targeting_rule_match"
        assert evaluation.rule_matched == "?"
        
        print("? タスク")
    
    async def test_percentage_rollout(self):
        """?"""
        # ?
        results = {"true": 0, "false": 0}
        
        for i in range(100):
            user_context = UserContext(
                user_id=f"rollout_user_{i:03d}",
                attributes={"user_type": "standard"}
            )
            
            # 50%ログ
            from main import FeatureFlag, FlagType, TargetingRule
            test_flag = FeatureFlag(
                flag_key="test_50_percent_rollout",
                name="50%ログ",
                description="?50%ログ",
                flag_type=FlagType.BOOLEAN,
                default_value=False,
                enabled=True,
                targeting_rules=[
                    TargetingRule(
                        rule_id="fifty_percent",
                        name="50%ログ",
                        conditions=[],
                        percentage=0.5,
                        value=True,
                        priority=1
                    )
                ],
                therapeutic_safety_level="low",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            feature_flag_engine.flags["test_50_percent_rollout"] = test_flag
            
            evaluation = await feature_flag_engine.evaluate_flag("test_50_percent_rollout", user_context)
            results[str(evaluation.value).lower()] += 1
        
        # 50%?20%の
        true_percentage = results["true"] / 100
        assert 0.3 <= true_percentage <= 0.7
        
        print(f"? ?: {true_percentage*100:.1f}% がTrue")
    
    async def test_kill_switch_functionality(self):
        """Kill Switch?"""
        flag_key = "daily_trio_enabled"
        user_context = UserContext(
            user_id="kill_switch_test_user",
            attributes={"user_type": "standard"}
        )
        
        # ?
        evaluation_before = await feature_flag_engine.evaluate_flag(flag_key, user_context)
        assert evaluation_before.value is True
        
        # Kill Switch発
        kill_result = await feature_flag_engine.activate_kill_switch(
            flag_key, "?", "test_admin"
        )
        assert kill_result["success"] is True
        
        # Kill Switch発
        evaluation_after = await feature_flag_engine.evaluate_flag(flag_key, user_context)
        assert evaluation_after.reason == "kill_switch_active"
        # Kill Switch発
        
        # Kill Switch?
        deactivate_result = await feature_flag_engine.deactivate_kill_switch(flag_key, "test_admin")
        assert deactivate_result["success"] is True
        
        # ?
        evaluation_restored = await feature_flag_engine.evaluate_flag(flag_key, user_context)
        assert evaluation_restored.reason != "kill_switch_active"
        
        print("? Kill Switch?")
    
    async def test_ab_test_creation(self):
        """A/B?"""
        ab_test = ABTestConfig(
            test_id="test_micro_rewards_timing",
            name="?",
            description="リスト",
            flag_key="micro_rewards_timing_test",
            variations=[
                {"id": "control", "value": "immediate"},
                {"id": "treatment", "value": "delayed_500ms"}
            ],
            traffic_allocation={"control": 0.5, "treatment": 0.5},
            targeting_rules=[],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),
            therapeutic_safety_check=True
        )
        
        result = await feature_flag_engine.create_ab_test(ab_test)
        
        assert result["success"] is True
        assert result["test_id"] == "test_micro_rewards_timing"
        assert result["flag_key"] == "micro_rewards_timing_test"
        
        # ?
        assert "micro_rewards_timing_test" in feature_flag_engine.flags
        
        print("? A/B?")
    
    async def test_therapeutic_safety_check(self):
        """治療"""
        # ?A/B?100%を
        unsafe_ab_test = ABTestConfig(
            test_id="unsafe_test",
            name="?",
            description="安全",
            flag_key="unsafe_test_flag",
            variations=[
                {"id": "control", "value": False},
                {"id": "treatment", "value": True}
            ],
            traffic_allocation={"control": 0.6, "treatment": 0.6},  # ?120%
            targeting_rules=[],
            start_date=datetime.now(),
            therapeutic_safety_check=True
        )
        
        # 安全
        try:
            await feature_flag_engine.create_ab_test(unsafe_ab_test)
            assert False, "安全"
        except Exception as e:
            # HTTPExceptionまExceptionを
            error_message = str(e)
            assert ("治療" in error_message or 
                   "A/B?" in error_message)
        
        print("? 治療")
    
    async def test_flag_analytics(self):
        """?"""
        flag_key = "daily_trio_enabled"
        
        # ?
        for i in range(10):
            user_context = UserContext(
                user_id=f"analytics_user_{i}",
                attributes={"user_type": "standard"}
            )
            await feature_flag_engine.evaluate_flag(flag_key, user_context)
        
        # ?
        analytics = await feature_flag_engine.get_flag_analytics(flag_key, hours=1)
        
        assert analytics["flag_key"] == flag_key
        assert analytics["total_evaluations"] >= 10
        assert analytics["unique_users"] >= 10
        assert "value_distribution" in analytics
        assert "reason_distribution" in analytics
        
        print(f"? ?: {analytics['total_evaluations']}?")

class TestTherapeuticSafety:
    """治療"""
    
    def test_safety_level_classification(self):
        """安全"""
        flags = feature_flag_engine.flags
        
        # ?
        safety_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for flag in flags.values():
            if flag.therapeutic_safety_level in safety_levels:
                safety_levels[flag.therapeutic_safety_level] += 1
        
        # ?1つ
        assert safety_levels["critical"] > 0, "Critical レベル"
        assert safety_levels["high"] > 0, "High レベル"
        assert safety_levels["medium"] > 0, "Medium レベル"
        
        print(f"? 安全: {safety_levels}")
    
    async def test_gradual_rollout_safety(self):
        """?"""
        # ?
        rollout_percentages = [0.01, 0.05, 0.10, 0.25, 0.50, 1.0]
        
        for percentage in rollout_percentages:
            # ?
            enabled_count = 0
            total_users = 100
            
            for i in range(total_users):
                user_id = f"gradual_user_{percentage}_{i}"
                is_enabled = feature_flag_engine._is_user_in_percentage(
                    user_id, "gradual_test", percentage
                )
                if is_enabled:
                    enabled_count += 1
            
            actual_percentage = enabled_count / total_users
            
            # ?15%の
            assert abs(actual_percentage - percentage) <= 0.15
        
        print("? ?")
    
    def test_flag_tagging_system(self):
        """?"""
        # コア
        core_flags = [
            flag for flag in feature_flag_engine.flags.values()
            if "core_feature" in flag.tags
        ]
        
        assert len(core_flags) >= 3, "コア"
        
        # ADHD支援
        adhd_flags = [
            flag for flag in feature_flag_engine.flags.values()
            if "adhd_support" in flag.tags
        ]
        
        assert len(adhd_flags) >= 1, "ADHD支援"
        
        print(f"? ?: コア{len(core_flags)}?, ADHD支援{len(adhd_flags)}?")

class TestAPIEndpoints:
    """APIエラー"""
    
    def test_evaluate_flag_endpoint(self):
        """?"""
        user_context_data = {
            "user_id": "api_test_user",
            "attributes": {
                "age": 28,
                "user_type": "standard",
                "therapeutic_state": "ACTION"
            }
        }
        
        response = client.post(
            "/flags/evaluate?flag_key=daily_trio_enabled",
            json=user_context_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["flag_key"] == "daily_trio_enabled"
        assert "value" in data
        assert "reason" in data
        assert data["user_id"] == "api_test_user"
        
        print("? ?")
    
    def test_batch_evaluation_endpoint(self):
        """一般"""
        request_data = {
            "flag_keys": ["daily_trio_enabled", "micro_rewards_enabled", "self_efficacy_gauge_enabled"],
            "user_context": {
                "user_id": "batch_test_user",
                "attributes": {"user_type": "standard"}
            }
        }
        
        response = client.post("/flags/evaluate-batch", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "batch_test_user"
        assert "evaluations" in data
        assert len(data["evaluations"]) == 3
        
        print("? 一般")
    
    def test_list_flags_endpoint(self):
        """?"""
        response = client.get("/flags")
        
        assert response.status_code == 200
        data = response.json()
        assert "flags" in data
        assert "total_count" in data
        assert data["total_count"] > 0
        
        print(f"? ?: {data['total_count']}?")
    
    def test_kill_switch_endpoints(self):
        """Kill Switchエラー"""
        flag_key = "micro_rewards_enabled"
        
        # Kill Switch発
        activate_response = client.post(
            f"/flags/{flag_key}/kill-switch/activate",
            params={
                "reason": "?",
                "activated_by": "test_admin"
            }
        )
        
        assert activate_response.status_code == 200
        activate_data = activate_response.json()
        assert activate_data["success"] is True
        
        # Kill Switch?
        deactivate_response = client.post(
            f"/flags/{flag_key}/kill-switch/deactivate",
            params={"deactivated_by": "test_admin"}
        )
        
        assert deactivate_response.status_code == 200
        deactivate_data = deactivate_response.json()
        assert deactivate_data["success"] is True
        
        print("? Kill Switchエラー")
    
    def test_analytics_endpoint(self):
        """?"""
        flag_key = "daily_trio_enabled"
        
        response = client.get(f"/flags/{flag_key}/analytics?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert data["flag_key"] == flag_key
        assert "total_evaluations" in data
        assert "unique_users" in data
        assert "value_distribution" in data
        
        print("? ?")
    
    def test_therapeutic_safety_dashboard(self):
        """治療"""
        response = client.get("/therapeutic-safety/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "critical_flags" in data
        assert "high_risk_flags" in data
        assert "active_kill_switches" in data
        assert "recent_safety_events" in data
        
        print("? 治療")
    
    def test_health_check_endpoint(self):
        """ヘルパー"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "total_flags" in data
        assert "active_kill_switches" in data
        
        print("? ヘルパー")

def run_all_tests():
    """?"""
    print("Feature Flag Service ?")
    print("=" * 50)
    
    # 基本
    engine_tests = TestFeatureFlagEngine()
    
    async def run_async_engine_tests():
        await engine_tests.test_basic_flag_evaluation()
        await engine_tests.test_targeting_rule_evaluation()
        await engine_tests.test_percentage_rollout()
        await engine_tests.test_kill_switch_functionality()
        await engine_tests.test_ab_test_creation()
        await engine_tests.test_therapeutic_safety_check()
        await engine_tests.test_flag_analytics()
    
    asyncio.run(run_async_engine_tests())
    
    # 治療
    safety_tests = TestTherapeuticSafety()
    safety_tests.test_safety_level_classification()
    
    async def run_async_safety_tests():
        await safety_tests.test_gradual_rollout_safety()
    
    asyncio.run(run_async_safety_tests())
    
    safety_tests.test_flag_tagging_system()
    
    # APIエラー
    api_tests = TestAPIEndpoints()
    api_tests.test_evaluate_flag_endpoint()
    api_tests.test_batch_evaluation_endpoint()
    api_tests.test_list_flags_endpoint()
    api_tests.test_kill_switch_endpoints()
    api_tests.test_analytics_endpoint()
    api_tests.test_therapeutic_safety_dashboard()
    api_tests.test_health_check_endpoint()
    
    print("\n" + "=" * 50)
    print("? Feature Flag Service ?")
    print("\n?:")
    print("- A/B?Kill-Switch基本 ?")
    print("- 治療 ?")
    print("- リスト ?")
    print("- ? ?")
    print("- ? ?")

if __name__ == "__main__":
    run_all_tests()