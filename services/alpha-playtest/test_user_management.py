"""
?
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from main import AlphaPlaytestEngine, TestUserStatus, ABTestVariant, FeedbackType
import uuid

class TestUserManagementSystem:
    """?"""
    
    @pytest.fixture
    def playtest_engine(self):
        """?"""
        return AlphaPlaytestEngine()
    
    @pytest.mark.asyncio
    async def test_user_registration(self, playtest_engine):
        """ユーザー"""
        email = "test@example.com"
        demographics = {"age": 25, "gender": "male", "condition": "adhd"}
        
        user = await playtest_engine.register_test_user(email, demographics)
        
        assert user.user_id is not None
        assert user.status == TestUserStatus.INVITED
        assert user.assigned_variant in ABTestVariant
        assert user.demographics == demographics
        assert user.consent_given is True
        
        # ユーザー
        assert user.user_id in playtest_engine.test_users
    
    @pytest.mark.asyncio
    async def test_user_limit_enforcement(self, playtest_engine):
        """ユーザー"""
        # ?3に
        playtest_engine.max_test_users = 3
        
        # 3?
        for i in range(3):
            await playtest_engine.register_test_user(f"test{i}@example.com")
        
        # 4?
        with pytest.raises(Exception) as exc_info:
            await playtest_engine.register_test_user("test4@example.com")
        
        assert "?" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_ab_variant_assignment(self, playtest_engine):
        """A/B?"""
        users = []
        
        # 9?3つ
        for i in range(9):
            user = await playtest_engine.register_test_user(f"test{i}@example.com")
            users.append(user)
        
        # バリデーション
        variant_counts = {}
        for user in users:
            variant = user.assigned_variant
            variant_counts[variant] = variant_counts.get(variant, 0) + 1
        
        # ?3?
        for variant in ABTestVariant:
            assert variant_counts[variant] == 3
    
    @pytest.mark.asyncio
    async def test_email_anonymization(self, playtest_engine):
        """メイン"""
        original_email = "sensitive@example.com"
        user = await playtest_engine.register_test_user(original_email)
        
        # ?
        assert user.email != original_email
        assert len(user.email) == 16  # ?
        assert "@" not in user.email  # メイン
    
    @pytest.mark.asyncio
    async def test_user_status_transitions(self, playtest_engine):
        """ユーザー"""
        user = await playtest_engine.register_test_user("test@example.com")
        
        # ?INVITED
        assert user.status == TestUserStatus.INVITED
        
        # ?ACTIVEに
        await playtest_engine.log_user_behavior(
            user.user_id, "login", {"timestamp": datetime.now().isoformat()}
        )
        
        assert user.status == TestUserStatus.ACTIVE
        assert user.last_active_date is not None
    
    def test_privacy_settings_default(self, playtest_engine):
        """プレビュー"""
        user = asyncio.run(playtest_engine.register_test_user("test@example.com"))
        
        expected_settings = {
            "data_collection": True,
            "analytics": True,
            "feedback_collection": True
        }
        
        assert user.privacy_settings == expected_settings

class TestBehaviorLogging:
    """?"""
    
    @pytest.fixture
    def playtest_engine_with_user(self):
        """ユーザー"""
        engine = AlphaPlaytestEngine()
        user = asyncio.run(engine.register_test_user("test@example.com"))
        return engine, user.user_id
    
    @pytest.mark.asyncio
    async def test_behavior_logging(self, playtest_engine_with_user):
        """?"""
        engine, user_id = playtest_engine_with_user
        
        event_data = {
            "action": "task_completion",
            "task_id": "task_123",
            "completion_time": 300,
            "difficulty": 3
        }
        
        success = await engine.log_user_behavior(
            user_id, "task_completion", event_data, "session_123"
        )
        
        assert success is True
        assert len(engine.behavior_logs) == 1
        
        log = engine.behavior_logs[0]
        assert log.user_id == user_id
        assert log.event_type == "task_completion"
        assert log.session_id == "session_123"
        assert log.anonymized is True
    
    @pytest.mark.asyncio
    async def test_data_anonymization(self, playtest_engine_with_user):
        """デフォルト"""
        engine, user_id = playtest_engine_with_user
        
        sensitive_data = {
            "email": "user@example.com",
            "name": "John Doe",
            "ip_address": "192.168.1.1",
            "location": {"lat": 35.6762, "lng": 139.6503},
            "timestamp": "2024-01-01T12:00:00",
            "safe_data": "this should remain"
        }
        
        await engine.log_user_behavior(user_id, "test_event", sensitive_data)
        
        log = engine.behavior_logs[0]
        event_data = log.event_data
        
        # ?
        assert "email" not in event_data
        assert "name" not in event_data
        assert "ip_address" not in event_data
        
        # ?
        assert event_data["location"]["lat"] == 35.68  # ?2?
        assert event_data["location"]["lng"] == 139.65
        
        # 安全
        assert event_data["safe_data"] == "this should remain"
    
    @pytest.mark.asyncio
    async def test_privacy_settings_respect(self, playtest_engine_with_user):
        """プレビュー"""
        engine, user_id = playtest_engine_with_user
        
        # デフォルト
        user = engine.test_users[user_id]
        user.privacy_settings["data_collection"] = False
        
        # ログ
        success = await engine.log_user_behavior(
            user_id, "test_event", {"data": "test"}
        )
        
        # ログ
        assert success is False
        assert len(engine.behavior_logs) == 0
    
    @pytest.mark.asyncio
    async def test_log_retention_cleanup(self, playtest_engine_with_user):
        """ログ"""
        engine, user_id = playtest_engine_with_user
        
        # ?
        old_log = engine.behavior_logs[0] if engine.behavior_logs else None
        if old_log:
            old_log.timestamp = datetime.now() - timedelta(days=100)
        else:
            # ?
            from main import BehaviorLog
            old_log = BehaviorLog(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                session_id="old_session",
                event_type="old_event",
                event_data={},
                timestamp=datetime.now() - timedelta(days=100),
                anonymized=True
            )
            engine.behavior_logs.append(old_log)
        
        # ?
        await engine.log_user_behavior(user_id, "new_event", {"data": "new"})
        
        # ?
        await engine._cleanup_old_logs()
        
        # ?
        remaining_logs = [log for log in engine.behavior_logs if log.event_type == "new_event"]
        old_logs = [log for log in engine.behavior_logs if log.event_type == "old_event"]
        
        assert len(remaining_logs) > 0
        assert len(old_logs) == 0

class TestRealTimeAnalytics:
    """リスト"""
    
    @pytest.fixture
    def populated_engine(self):
        """デフォルト"""
        engine = AlphaPlaytestEngine()
        
        # ?
        users = []
        for i in range(10):
            user = asyncio.run(engine.register_test_user(f"test{i}@example.com"))
            users.append(user)
        
        # 一般
        for i in range(3):
            users[i].status = TestUserStatus.COMPLETED
            users[i].completion_date = datetime.now()
        
        # ?
        for i, user in enumerate(users[:5]):
            asyncio.run(engine.log_user_behavior(
                user.user_id, "login", {"session_start": True}, f"session_{i}"
            ))
            asyncio.run(engine.log_user_behavior(
                user.user_id, "task_completion", {"task_id": f"task_{i}"}, f"session_{i}"
            ))
        
        return engine
    
    @pytest.mark.asyncio
    async def test_analytics_report_generation(self, populated_engine):
        """?"""
        report = await populated_engine.generate_analytics_report()
        
        assert report.total_users == 10
        assert report.active_users == 7  # 10 - 3 completed
        assert report.completion_rate == 0.3  # 3/10
        assert report.average_session_duration >= 0
        assert isinstance(report.retention_rates, dict)
        assert isinstance(report.feature_usage, dict)
        assert report.bug_reports_count >= 0
        assert report.satisfaction_score >= 0
    
    @pytest.mark.asyncio
    async def test_session_duration_calculation(self, populated_engine):
        """?"""
        durations = await populated_engine._calculate_session_durations()
        
        # ?
        assert len(durations) > 0
        
        # ?
        for duration in durations:
            assert duration >= 0
    
    @pytest.mark.asyncio
    async def test_retention_rate_calculation(self, populated_engine):
        """リスト"""
        retention_rates = await populated_engine._calculate_retention_rates()
        
        expected_periods = ["day_1", "day_3", "day_7", "day_14", "day_30"]
        
        for period in expected_periods:
            assert period in retention_rates
            assert 0 <= retention_rates[period] <= 1
    
    @pytest.mark.asyncio
    async def test_feature_usage_calculation(self, populated_engine):
        """?"""
        usage_rates = await populated_engine._calculate_feature_usage()
        
        # ログ
        assert "login" in usage_rates
        assert "task_completion" in usage_rates
        
        # 使用0-1の
        for feature, rate in usage_rates.items():
            assert 0 <= rate <= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])