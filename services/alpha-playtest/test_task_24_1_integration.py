"""
Task 24.1 ?: プレビュー
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

# ?
from user_management import PlaytestUserManager, PlaytestUserStatus, ConsentType
from privacy_protection import PrivacyProtectionEngine, DataSensitivityLevel
from realtime_dashboard import RealTimeDashboard, initialize_dashboard
from main import AlphaPlaytestEngine, FeedbackType, ABTestVariant

class TestPlaytestEnvironmentIntegration:
    """プレビュー"""
    
    @pytest.fixture
    def user_manager(self):
        """?"""
        return PlaytestUserManager(max_users=10)  # ?
    
    @pytest.fixture
    def privacy_engine(self):
        """プレビュー"""
        return PrivacyProtectionEngine()
    
    @pytest.fixture
    def playtest_engine(self):
        """プレビュー"""
        engine = AlphaPlaytestEngine()
        engine.max_test_users = 10  # ?
        return engine
    
    @pytest.fixture
    def dashboard(self, playtest_engine):
        """リスト"""
        return initialize_dashboard(playtest_engine)
    
    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(self, user_manager, privacy_engine):
        """?"""
        # 1. ユーザー
        email = "test@example.com"
        demographics = {
            "age_range": "20-25",
            "tech_proficiency": "high",
            "gaming_experience": "medium"
        }
        
        user = await user_manager.register_user(email, demographics)
        
        # 2. 基本
        assert user.user_id is not None
        assert user.status == PlaytestUserStatus.INVITED
        assert user.demographics.age_range == "20-25"
        assert len(user.consents) >= 2  # 基本
        
        # 3. プレビュー
        privacy_engine.record_consent(
            user.user_id, ConsentType.ANALYTICS, True, "192.168.1.1"
        )
        
        # 4. ?
        # プレビュー
        assert privacy_engine.check_consent(user.user_id, ConsentType.ANALYTICS)
        
        # 5. ユーザー
        activity_data = {
            "last_login": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "session_duration": 15.5,
            "feature_used": "task_completion",
            "task_completed": 1
        }
        
        updated_user = await user_manager.update_user_activity(user.user_id, activity_data)
        
        # 6. ?
        assert updated_user.activity.session_count == 1
        assert updated_user.activity.total_session_duration == 15.5
        assert updated_user.activity.task_completion_count == 1
        assert updated_user.status == PlaytestUserStatus.ACTIVE  # 自動
    
    @pytest.mark.asyncio
    async def test_data_collection_and_anonymization(self, playtest_engine, privacy_engine):
        """デフォルト"""
        # 1. ?
        user = await playtest_engine.register_test_user(
            "privacy@example.com",
            {"age_range": "25-30", "location": "Tokyo"}
        )
        
        # 2. ?
        sensitive_event_data = {
            "action": "task_completed",
            "task_id": "task_123",
            "email": "privacy@example.com",  # ?
            "ip_address": "192.168.1.100",   # ?
            "location": {"lat": 35.6762, "lng": 139.6503},  # ?
            "timestamp": datetime.now().isoformat(),
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        }
        
        success = await playtest_engine.log_user_behavior(
            user.user_id, "task_completion", sensitive_event_data
        )
        
        assert success
        
        # 3. ログ
        logged_event = playtest_engine.behavior_logs[-1]
        assert "email" not in logged_event.event_data
        assert "ip_address" not in logged_event.event_data
        assert logged_event.anonymized
        
        # ?
        if "location" in logged_event.event_data:
            location = logged_event.event_data["location"]
            assert location["lat"] == 35.68  # ?2?
            assert location["lng"] == 139.65
        
        # 4. デフォルト
        minimized_data = privacy_engine.validate_data_minimization(
            sensitive_event_data, "user_analytics"
        )
        
        # ?
        required_fields = ["timestamp", "user_agent"]  # user_analytics?
        for field in required_fields:
            if field in sensitive_event_data:
                assert field in minimized_data or field == "user_agent"  # user_agentは
        
        # ?
        assert "email" not in minimized_data
    
    @pytest.mark.asyncio
    async def test_realtime_dashboard_metrics(self, dashboard, playtest_engine):
        """リスト"""
        # 1. ?
        # ?
        users = []
        for i in range(5):
            user = await playtest_engine.register_test_user(
                f"user{i}@example.com",
                {"age_range": "20-30", "tech_proficiency": "medium"}
            )
            users.append(user)
        
        # 2. ?
        for i, user in enumerate(users):
            for j in range(3):  # ?3つ
                await playtest_engine.log_user_behavior(
                    user.user_id,
                    "task_completion",
                    {
                        "task_id": f"task_{i}_{j}",
                        "duration": 300 + i * 60,  # 5-9?
                        "completed": True
                    },
                    session_id=f"session_{user.user_id}_{j}"
                )
        
        # 3. ?
        for i, user in enumerate(users[:3]):  # 3?
            await playtest_engine.collect_feedback(
                user.user_id,
                FeedbackType.USABILITY,
                "?",
                f"ユーザー{i}か",
                rating=4 + (i % 2)  # 4ま5の
            )
        
        # 4. ?
        await dashboard.update_all_metrics()
        
        # 5. メイン
        dashboard_data = dashboard.get_dashboard_data()
        
        # ユーザー
        engagement = dashboard_data["metrics"]["user_engagement"]
        assert engagement["daily_active_users"] == 5
        assert engagement["average_session_duration"] > 0
        assert 0 <= engagement["bounce_rate"] <= 1
        
        # ?
        feature_usage = dashboard_data["metrics"]["feature_usage"]
        assert len(feature_usage) > 0
        task_completion_feature = next(
            (f for f in feature_usage if f["feature_name"] == "task_completion"), None
        )
        assert task_completion_feature is not None
        assert task_completion_feature["usage_count"] == 15  # 5ユーザー ? 3?
        assert task_completion_feature["unique_users"] == 5
        
        # ?
        feedback = dashboard_data["metrics"]["feedback"]
        assert feedback["total_feedback"] == 3
        assert feedback["average_rating"] >= 4.0
        assert feedback["response_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_ab_test_assignment_and_analysis(self, playtest_engine):
        """A/B?"""
        # 1. ?A/B?
        users = []
        for i in range(9):  # 3の
            user = await playtest_engine.register_test_user(f"abtest{i}@example.com")
            users.append(user)
        
        # 2. バリデーション
        variant_counts = {}
        for user in users:
            variant = user.assigned_variant
            variant_counts[variant] = variant_counts.get(variant, 0) + 1
        
        # ?1の
        expected_per_variant = len(users) // 3
        for variant, count in variant_counts.items():
            assert abs(count - expected_per_variant) <= 1
        
        # 3. バリデーション
        for user in users:
            # コア: ?
            # バリデーションA: ?  
            # バリデーションB: ?
            if user.assigned_variant == ABTestVariant.CONTROL:
                completion_rate = 0.6
            elif user.assigned_variant == ABTestVariant.VARIANT_A:
                completion_rate = 0.7
            else:  # VARIANT_B
                completion_rate = 0.8
            
            # ?
            if completion_rate > 0.7:  # ?
                from main import TestUserStatus
                playtest_engine.test_users[user.user_id].status = TestUserStatus.COMPLETED
        
        # 4. A/B?
        test_result = await playtest_engine.run_ab_test_analysis("onboarding_flow")
        
        # 5. ?
        assert test_result.test_id == "onboarding_flow"
        assert test_result.control_value >= 0
        assert test_result.variant_a_value >= 0
        assert test_result.variant_b_value >= 0
        assert test_result.statistical_significance >= 0
        
        # ?
        total_sample_size = sum(test_result.sample_sizes.values())
        assert total_sample_size == len(users)
    
    @pytest.mark.asyncio
    async def test_privacy_compliance_and_data_deletion(self, user_manager, privacy_engine):
        """プレビュー"""
        # 1. ユーザー
        user = await user_manager.register_user("gdpr@example.com")
        
        # 2. デフォルト
        privacy_engine.record_data_processing(
            user.user_id, "behavior_logs", "user_analytics"
        )
        privacy_engine.record_data_processing(
            user.user_id, "feedback_data", "product_improvement"
        )
        
        # 3. プレビュー
        privacy_report = privacy_engine.generate_privacy_report(user.user_id)
        
        assert privacy_report["user_id"] == user.user_id
        assert len(privacy_report["data_processing"]) == 2
        assert "consent_status" in privacy_report
        assert "retention_info" in privacy_report
        
        # 4. デフォルト
        deletion_result = privacy_engine.request_data_deletion(
            user.user_id, ["behavior_logs", "feedback_data"]
        )
        
        assert user.user_id == deletion_result["user_id"]
        assert "behavior_logs" in deletion_result["deleted_data_types"]
        assert "feedback_data" in deletion_result["deleted_data_types"]
        
        # 5. ?
        remaining_records = [
            record for record in privacy_engine.processing_records
            if record.user_id == user.user_id
        ]
        assert len(remaining_records) == 0
    
    @pytest.mark.asyncio
    async def test_alert_system(self, dashboard, playtest_engine):
        """アプリ"""
        # 1. ?
        await dashboard.update_all_metrics()
        await dashboard.check_alerts()
        
        initial_alerts = len(dashboard.active_alerts)
        
        # 2. ?
        for i in range(10):
            user = await playtest_engine.register_test_user(f"error{i}@example.com")
            await playtest_engine.log_user_behavior(
                user.user_id,
                "error_occurred",
                {"error_type": "system_error", "severity": "high"}
            )
        
        # 3. メイン
        await dashboard.update_all_metrics()
        await dashboard.check_alerts()
        
        # 4. アプリ
        assert len(dashboard.active_alerts) > initial_alerts
        
        # エラー
        error_alerts = [
            alert for alert in dashboard.active_alerts
            if alert["category"] == "system_performance" and "エラー" in alert["message"]
        ]
        assert len(error_alerts) > 0
    
    @pytest.mark.asyncio
    async def test_data_retention_and_cleanup(self, privacy_engine):
        """デフォルト"""
        # 1. ?
        old_timestamp = datetime.now() - timedelta(days=100)
        
        # ?
        from privacy_protection import DataProcessingRecord
        old_record = DataProcessingRecord(
            record_id="old_record_1",
            user_id="test_user",
            data_type="behavior_logs",
            processing_purpose="analytics",
            timestamp=old_timestamp,
            retention_until=old_timestamp + timedelta(days=90)  # ?
        )
        privacy_engine.processing_records.append(old_record)
        
        # 2. ?
        privacy_engine.record_data_processing(
            "test_user", "behavior_logs", "current_analytics"
        )
        
        initial_count = len(privacy_engine.processing_records)
        
        # 3. ?
        cleanup_stats = privacy_engine.cleanup_expired_data()
        
        # 4. ?
        assert cleanup_stats["processing_records"] >= 1
        assert len(privacy_engine.processing_records) < initial_count
        
        # ?
        remaining_records = [
            record for record in privacy_engine.processing_records
            if record.processing_purpose == "current_analytics"
        ]
        assert len(remaining_records) == 1
    
    @pytest.mark.asyncio
    async def test_user_statistics_and_reporting(self, user_manager):
        """ユーザー"""
        # 1. ?
        demographics_variations = [
            {"age_range": "18-25", "tech_proficiency": "high", "gaming_experience": "high"},
            {"age_range": "26-35", "tech_proficiency": "medium", "gaming_experience": "medium"},
            {"age_range": "36-45", "tech_proficiency": "low", "gaming_experience": "low"},
        ]
        
        users = []
        for i, demo in enumerate(demographics_variations):
            user = await user_manager.register_user(f"stats{i}@example.com", demo)
            users.append(user)
        
        # 2. ユーザー
        await user_manager.update_user_status(users[0].user_id, PlaytestUserStatus.ACTIVE)
        await user_manager.update_user_status(users[1].user_id, PlaytestUserStatus.COMPLETED)
        await user_manager.update_user_status(users[2].user_id, PlaytestUserStatus.DROPPED)
        
        # 3. ?
        stats = user_manager.get_user_statistics()
        
        # 4. ?
        assert stats["total_users"] == 3
        assert stats["capacity_utilization"] == 0.3  # 3/10
        
        # ストーリー
        status_dist = stats["status_distribution"]
        assert status_dist[PlaytestUserStatus.ACTIVE] == 1
        assert status_dist[PlaytestUserStatus.COMPLETED] == 1
        assert status_dist[PlaytestUserStatus.DROPPED] == 1
        
        # ?
        demographics = stats["demographics"]
        assert len(demographics["age_ranges"]) == 3
        assert len(demographics["tech_proficiency"]) == 3
        
        # ?
        activity = stats["activity_metrics"]
        assert "completion_rate" in activity
        assert "dropout_rate" in activity
        assert abs(activity["completion_rate"] - 1/3) < 0.01  # 1?/3?
        assert abs(activity["dropout_rate"] - 1/3) < 0.01     # 1?/3?

if __name__ == "__main__":
    pytest.main([__file__, "-v"])