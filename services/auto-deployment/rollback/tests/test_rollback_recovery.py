"""
ロールバック復旧システムのテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rollback.rollback_recovery import (
    RollbackRecovery, RecoveryConfig, RecoveryResult, RecoveryPlan,
    RecoveryStatus, RecoveryStrategy, EscalationLevel
)
from rollback.rollback_executor import RollbackResult, RollbackStatus, RollbackTarget
from rollback.rollback_monitor import EscalationEvent
from monitoring.health_check import HealthCheckResult


class TestRollbackRecovery:
    """ロールバック復旧システムのテスト"""
    
    @pytest.fixture
    def mock_traffic_manager(self):
        """モックトラフィック管理システム"""
        manager = Mock()
        manager.emergency_traffic_switch = Mock()
        manager.get_current_traffic = Mock()
        manager.update_traffic = Mock()
        return manager
    
    @pytest.fixture
    def mock_revision_manager(self):
        """モックリビジョン管理システム"""
        manager = Mock()
        manager.get_revision_history = AsyncMock()
        manager.get_current_revision = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_health_check_manager(self):
        """モックヘルスチェック管理システム"""
        manager = Mock()
        manager.run_health_checks = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_notification_manager(self):
        """モック通知管理システム"""
        manager = Mock()
        manager.send_notification = AsyncMock()
        return manager
    
    @pytest.fixture
    def recovery_config(self):
        """復旧設定"""
        return RecoveryConfig(
            emergency_recovery_timeout_minutes=5,  # テスト用に短縮
            standard_recovery_timeout_minutes=10,
            auto_emergency_rollback=True,
            auto_traffic_isolation=True,
            auto_service_restart=False,
            max_recovery_attempts=2
        )
    
    @pytest.fixture
    def rollback_recovery(self, mock_traffic_manager, mock_revision_manager,
                         mock_health_check_manager, mock_notification_manager, recovery_config):
        """ロールバック復旧システム"""
        return RollbackRecovery(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            notification_manager=mock_notification_manager,
            config=recovery_config
        )
    
    @pytest.fixture
    def sample_rollback_result(self):
        """サンプルロールバック結果"""
        target = RollbackTarget(
            service_name="test-service",
            target_revision="test-revision-1",
            environment="test"
        )
        
        return RollbackResult(
            success=False,
            rollback_id="rollback_test_20241208_120000",
            status=RollbackStatus.FAILED,
            target=target,
            start_time=datetime.now()
        )
    
    @pytest.fixture
    def sample_escalation_event(self, sample_rollback_result):
        """サンプルエスカレーションイベント"""
        return EscalationEvent(
            event_id="escalation_test_001",
            rollback_id=sample_rollback_result.rollback_id,
            level=EscalationLevel.HIGH,
            reason="ロールバック失敗のため",
            timestamp=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_create_recovery_plan_critical(self, rollback_recovery, sample_rollback_result):
        """緊急レベル復旧計画作成テスト"""
        escalation_event = EscalationEvent(
            event_id="critical_test",
            rollback_id=sample_rollback_result.rollback_id,
            level=EscalationLevel.CRITICAL,
            reason="緊急事態",
            timestamp=datetime.now()
        )
        
        plan = await rollback_recovery._create_recovery_plan(sample_rollback_result, escalation_event)
        
        # 緊急レベルの計画を確認
        assert plan.escalation_level == EscalationLevel.CRITICAL
        assert plan.priority == 1
        assert RecoveryStrategy.EMERGENCY_ROLLBACK in plan.strategies
        assert RecoveryStrategy.TRAFFIC_ISOLATION in plan.strategies
        assert RecoveryStrategy.MANUAL_INTERVENTION in plan.strategies
        assert plan.estimated_duration_minutes < 30  # 緊急時は短時間
    
    @pytest.mark.asyncio
    async def test_create_recovery_plan_medium(self, rollback_recovery, sample_rollback_result):
        """中レベル復旧計画作成テスト"""
        escalation_event = EscalationEvent(
            event_id="medium_test",
            rollback_id=sample_rollback_result.rollback_id,
            level=EscalationLevel.MEDIUM,
            reason="中程度の問題",
            timestamp=datetime.now()
        )
        
        plan = await rollback_recovery._create_recovery_plan(sample_rollback_result, escalation_event)
        
        # 中レベルの計画を確認
        assert plan.escalation_level == EscalationLevel.MEDIUM
        assert plan.priority == 3
        assert RecoveryStrategy.TRAFFIC_ISOLATION in plan.strategies
        assert RecoveryStrategy.MANUAL_INTERVENTION in plan.strategies
    
    @pytest.mark.asyncio
    async def test_emergency_rollback_success(self, rollback_recovery, sample_rollback_result,
                                            mock_revision_manager, mock_traffic_manager):
        """緊急ロールバック成功テスト"""
        # リビジョン履歴を設定
        mock_revision = Mock()
        mock_revision.name = "stable-revision-1"
        mock_revision_manager.get_revision_history.return_value = [mock_revision]
        
        # トラフィック切り替え成功を設定
        traffic_result = Mock()
        traffic_result.success = True
        mock_traffic_manager.emergency_traffic_switch.return_value = traffic_result
        
        # 復旧結果を作成
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        action = Mock()
        action.description = "緊急ロールバック実行中"
        
        # 緊急ロールバックを実行
        success = await rollback_recovery._execute_emergency_rollback(recovery_result, action)
        
        # 成功を確認
        assert success
        assert mock_revision_manager.get_revision_history.called
        assert mock_traffic_manager.emergency_traffic_switch.called
    
    @pytest.mark.asyncio
    async def test_emergency_rollback_failure(self, rollback_recovery, sample_rollback_result,
                                            mock_revision_manager, mock_traffic_manager):
        """緊急ロールバック失敗テスト"""
        # リビジョン履歴なしを設定
        mock_revision_manager.get_revision_history.return_value = []
        
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        action = Mock()
        action.description = "緊急ロールバック実行中"
        
        # 緊急ロールバックを実行
        success = await rollback_recovery._execute_emergency_rollback(recovery_result, action)
        
        # 失敗を確認
        assert not success
        assert action.error_message == "安定したリビジョンが見つかりません"
    
    @pytest.mark.asyncio
    async def test_traffic_isolation_success(self, rollback_recovery, sample_rollback_result,
                                           mock_traffic_manager):
        """トラフィック分離成功テスト"""
        # 現在のトラフィック配分を設定
        mock_traffic_manager.get_current_traffic.return_value = {
            "problem-revision": 70,
            "stable-revision-1": 20,
            "stable-revision-2": 10
        }
        
        # トラフィック更新成功を設定
        traffic_result = Mock()
        traffic_result.success = True
        mock_traffic_manager.update_traffic.return_value = traffic_result
        
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        action = Mock()
        action.description = "トラフィック分離実行中"
        
        # トラフィック分離を実行
        success = await rollback_recovery._execute_traffic_isolation(recovery_result, action)
        
        # 成功を確認
        assert success
        assert mock_traffic_manager.get_current_traffic.called
        assert mock_traffic_manager.update_traffic.called
    
    @pytest.mark.asyncio
    async def test_service_restart_success(self, rollback_recovery, sample_rollback_result,
                                         mock_revision_manager, mock_health_check_manager):
        """サービス再起動成功テスト"""
        # 現在のリビジョンを設定
        mock_revision_manager.get_current_revision.return_value = "current-revision"
        
        # ヘルスチェック成功を設定
        health_result = HealthCheckResult(
            endpoint="/health",
            timestamp=datetime.now(),
            status_code=200,
            response_time_ms=100.0,
            success=True
        )
        mock_health_check_manager.run_health_checks.return_value = [health_result]
        
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        action = Mock()
        action.description = "サービス再起動実行中"
        
        # サービス再起動を実行
        with patch.object(rollback_recovery, '_restart_revision', return_value=True):
            success = await rollback_recovery._execute_service_restart(recovery_result, action)
        
        # 成功を確認
        assert success
        assert mock_revision_manager.get_current_revision.called
        assert mock_health_check_manager.run_health_checks.called
    
    @pytest.mark.asyncio
    async def test_manual_intervention_request(self, rollback_recovery, sample_rollback_result,
                                             mock_notification_manager):
        """手動介入要求テスト"""
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        recovery_result.plan.escalation_level = EscalationLevel.HIGH
        
        action = Mock()
        action.description = "手動介入要求中"
        
        # 手動介入を実行
        success = await rollback_recovery._execute_manual_intervention(recovery_result, action)
        
        # 成功を確認（通知が送信されたため）
        assert success
        assert mock_notification_manager.send_notification.called
        
        # 緊急チャンネルに通知が送信されたことを確認
        call_args = mock_notification_manager.send_notification.call_args
        assert call_args[1]["channel"] == "emergency"
        assert call_args[1]["severity"] == "critical"
    
    @pytest.mark.asyncio
    async def test_recovery_success_verification(self, rollback_recovery, sample_rollback_result,
                                               mock_health_check_manager):
        """復旧成功検証テスト"""
        # ヘルスチェック成功を設定
        health_results = [
            HealthCheckResult("/health", datetime.now(), 200, 100.0, True),
            HealthCheckResult("/api/health", datetime.now(), 200, 120.0, True)
        ]
        mock_health_check_manager.run_health_checks.return_value = health_results
        
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        # 復旧成功検証を実行
        success = await rollback_recovery._verify_recovery_success(recovery_result)
        
        # 成功を確認
        assert success
        assert mock_health_check_manager.run_health_checks.called
    
    @pytest.mark.asyncio
    async def test_recovery_failure_verification(self, rollback_recovery, sample_rollback_result,
                                               mock_health_check_manager):
        """復旧失敗検証テスト"""
        # ヘルスチェック失敗を設定
        health_results = [
            HealthCheckResult("/health", datetime.now(), 500, 5000.0, False),
            HealthCheckResult("/api/health", datetime.now(), 200, 120.0, True)
        ]
        mock_health_check_manager.run_health_checks.return_value = health_results
        
        recovery_result = RecoveryResult(
            recovery_id="recovery_test",
            rollback_id=sample_rollback_result.rollback_id,
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        # 復旧成功検証を実行
        success = await rollback_recovery._verify_recovery_success(recovery_result)
        
        # 失敗を確認
        assert not success
    
    @pytest.mark.asyncio
    async def test_initiate_recovery(self, rollback_recovery, sample_rollback_result,
                                   sample_escalation_event, mock_notification_manager):
        """復旧開始テスト"""
        # 復旧を開始
        recovery_id = await rollback_recovery.initiate_recovery(
            sample_rollback_result, sample_escalation_event
        )
        
        # 復旧IDが返されることを確認
        assert recovery_id.startswith("recovery_")
        
        # アクティブな復旧に追加されることを確認
        assert recovery_id in rollback_recovery.active_recoveries
        
        # 通知が送信されることを確認
        assert mock_notification_manager.send_notification.called
    
    @pytest.mark.asyncio
    async def test_cancel_recovery(self, rollback_recovery, sample_rollback_result,
                                 sample_escalation_event):
        """復旧キャンセルテスト"""
        # 復旧を開始
        recovery_id = await rollback_recovery.initiate_recovery(
            sample_rollback_result, sample_escalation_event
        )
        
        # 復旧をキャンセル
        cancel_success = await rollback_recovery.cancel_recovery(
            recovery_id, "テストキャンセル"
        )
        
        # キャンセル成功を確認
        assert cancel_success
        assert recovery_id not in rollback_recovery.active_recoveries
        
        # 履歴に移動されることを確認
        history = rollback_recovery.get_recovery_history()
        assert len(history) == 1
        assert history[0].status == RecoveryStatus.CANCELLED
    
    def test_get_recovery_status(self, rollback_recovery):
        """復旧ステータス取得テスト"""
        # 存在しない復旧ID
        status = rollback_recovery.get_recovery_status("nonexistent")
        assert status is None
        
        # 履歴に復旧結果を追加
        recovery_result = RecoveryResult(
            recovery_id="test_recovery",
            rollback_id="test_rollback",
            status=RecoveryStatus.COMPLETED,
            plan=Mock(),
            success=True
        )
        rollback_recovery.recovery_history.append(recovery_result)
        
        # 履歴から取得
        status = rollback_recovery.get_recovery_status("test_recovery")
        assert status is not None
        assert status.recovery_id == "test_recovery"
        assert status.success
    
    def test_get_active_recoveries(self, rollback_recovery):
        """アクティブ復旧取得テスト"""
        # 初期状態では空
        active = rollback_recovery.get_active_recoveries()
        assert len(active) == 0
        
        # アクティブな復旧を追加
        recovery_result = RecoveryResult(
            recovery_id="active_recovery",
            rollback_id="test_rollback",
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        rollback_recovery.active_recoveries["active_recovery"] = recovery_result
        
        # アクティブな復旧を取得
        active = rollback_recovery.get_active_recoveries()
        assert len(active) == 1
        assert active[0].recovery_id == "active_recovery"
    
    def test_get_system_status(self, rollback_recovery):
        """システムステータス取得テスト"""
        # 履歴に復旧結果を追加
        successful_recovery = RecoveryResult(
            recovery_id="success_1",
            rollback_id="test_1",
            status=RecoveryStatus.COMPLETED,
            plan=Mock(),
            success=True
        )
        failed_recovery = RecoveryResult(
            recovery_id="failed_1",
            rollback_id="test_2",
            status=RecoveryStatus.FAILED,
            plan=Mock(),
            success=False
        )
        
        rollback_recovery.recovery_history.extend([successful_recovery, failed_recovery])
        
        # システムステータスを取得
        status = rollback_recovery.get_system_status()
        
        # ステータス情報を確認
        assert status["active_recoveries"] == 0
        assert status["total_recoveries"] == 2
        assert status["successful_recoveries"] == 1
        assert status["failed_recoveries"] == 1
        assert "config" in status
    
    def test_recovery_config_validation(self):
        """復旧設定検証テスト"""
        config = RecoveryConfig(
            emergency_recovery_timeout_minutes=15,
            standard_recovery_timeout_minutes=60,
            auto_emergency_rollback=True,
            auto_traffic_isolation=True,
            auto_service_restart=False,
            max_recovery_attempts=3
        )
        
        # 設定値を確認
        assert config.emergency_recovery_timeout_minutes == 15
        assert config.standard_recovery_timeout_minutes == 60
        assert config.auto_emergency_rollback
        assert config.auto_traffic_isolation
        assert not config.auto_service_restart
        assert config.max_recovery_attempts == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])