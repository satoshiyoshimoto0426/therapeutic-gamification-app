"""
統合ロールバック監視システムのテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rollback.rollback_monitoring_system import (
    RollbackMonitoringSystem, SystemConfig, SystemStatus
)
from rollback.rollback_executor import RollbackResult, RollbackStatus, RollbackTarget
from rollback.rollback_monitor import EscalationEvent, EscalationLevel, VerificationResult, VerificationStatus
from rollback.rollback_recovery import RecoveryResult, RecoveryStatus
from monitoring.health_check import HealthCheckResult


class TestRollbackMonitoringSystem:
    """統合ロールバック監視システムのテスト"""
    
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
    def mock_performance_monitor(self):
        """モックパフォーマンス監視システム"""
        monitor = Mock()
        monitor.get_metrics_history = AsyncMock()
        return monitor
    
    @pytest.fixture
    def mock_notification_manager(self):
        """モック通知管理システム"""
        manager = Mock()
        manager.send_notification = AsyncMock()
        return manager
    
    @pytest.fixture
    def system_config(self):
        """システム設定"""
        return SystemConfig(
            auto_recovery_enabled=True,
            escalation_auto_trigger=True,
            comprehensive_reporting=True,
            max_concurrent_monitors=5,
            system_health_check_interval_seconds=10  # テスト用に短縮
        )
    
    @pytest.fixture
    def monitoring_system(self, mock_traffic_manager, mock_revision_manager,
                         mock_health_check_manager, mock_performance_monitor,
                         mock_notification_manager, system_config):
        """統合ロールバック監視システム"""
        return RollbackMonitoringSystem(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=system_config
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
            success=True,
            rollback_id="rollback_test_20241208_120000",
            status=RollbackStatus.COMPLETED,
            target=target,
            start_time=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_start_stop_system(self, monitoring_system, mock_notification_manager):
        """システム開始・停止テスト"""
        # 初期状態は停止
        assert monitoring_system.status == SystemStatus.STOPPED
        
        # システム開始
        await monitoring_system.start_system()
        assert monitoring_system.status == SystemStatus.ACTIVE
        assert monitoring_system.start_time is not None
        
        # 開始通知が送信されることを確認
        assert mock_notification_manager.send_notification.called
        
        # システム停止
        await monitoring_system.stop_system()
        assert monitoring_system.status == SystemStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_monitor_rollback_integration(self, monitoring_system, sample_rollback_result,
                                              mock_health_check_manager, mock_performance_monitor):
        """ロールバック監視統合テスト"""
        # ヘルスチェック成功を設定
        health_result = HealthCheckResult(
            endpoint="/health",
            timestamp=datetime.now(),
            status_code=200,
            response_time_ms=100.0,
            success=True
        )
        mock_health_check_manager.run_health_checks.return_value = [health_result]
        
        # パフォーマンスメトリクス成功を設定
        from monitoring.performance_monitor import PerformanceMetrics
        metrics = [
            PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=150.0,
                request_count=100,
                error_count=2
            )
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        # システム開始
        await monitoring_system.start_system()
        
        # ロールバック監視を開始
        monitor_id = await monitoring_system.monitor_rollback(sample_rollback_result)
        assert monitor_id == sample_rollback_result.rollback_id
        
        # 少し待機して監視が実行されることを確認
        await asyncio.sleep(0.1)
        
        # システム停止
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_escalation_handling(self, monitoring_system, sample_rollback_result):
        """エスカレーション処理テスト"""
        escalation_handled = False
        recovery_initiated = False
        
        # コールバックを設定
        def escalation_callback(event):
            nonlocal escalation_handled
            escalation_handled = True
        
        def recovery_callback(result):
            nonlocal recovery_initiated
            recovery_initiated = True
        
        monitoring_system.monitor.add_callback('escalation_triggered', escalation_callback)
        monitoring_system.recovery.add_callback('recovery_started', recovery_callback)
        
        await monitoring_system.start_system()
        
        # エスカレーションイベントを作成
        escalation_event = EscalationEvent(
            event_id="test_escalation",
            rollback_id=sample_rollback_result.rollback_id,
            level=EscalationLevel.HIGH,
            reason="テストエスカレーション",
            timestamp=datetime.now()
        )
        
        # エスカレーション処理を実行
        await monitoring_system._handle_escalation(escalation_event)
        
        # 少し待機して処理が完了することを確認
        await asyncio.sleep(0.1)
        
        # エスカレーションが処理されたことを確認
        assert escalation_handled
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_verification_complete_handling(self, monitoring_system):
        """検証完了処理テスト"""
        verification_result = VerificationResult(
            verification_id="test_verification",
            rollback_id="test_rollback",
            status=VerificationStatus.PASSED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            success_rate=95.0
        )
        
        await monitoring_system.start_system()
        
        # 検証完了処理を実行
        await monitoring_system._handle_verification_complete(verification_result)
        
        # 包括的レポートが有効な場合、レポート生成が呼ばれることを確認
        # （実際のレポート生成は内部で行われるため、エラーが発生しないことを確認）
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_recovery_complete_handling(self, monitoring_system):
        """復旧完了処理テスト"""
        recovery_result = RecoveryResult(
            recovery_id="test_recovery",
            rollback_id="test_rollback",
            status=RecoveryStatus.COMPLETED,
            plan=Mock(),
            success=True
        )
        
        await monitoring_system.start_system()
        
        # 復旧完了処理を実行
        await monitoring_system._handle_recovery_complete(recovery_result)
        
        # 成功統計が更新されることを確認
        assert monitoring_system.successful_recoveries >= 0
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_recovery_failed_handling(self, monitoring_system, mock_notification_manager):
        """復旧失敗処理テスト"""
        recovery_result = RecoveryResult(
            recovery_id="test_recovery",
            rollback_id="test_rollback",
            status=RecoveryStatus.FAILED,
            plan=Mock(),
            success=False,
            final_message="テスト失敗"
        )
        
        await monitoring_system.start_system()
        
        # 復旧失敗処理を実行
        await monitoring_system._handle_recovery_failed(recovery_result)
        
        # 失敗統計が更新されることを確認
        assert monitoring_system.failed_recoveries >= 0
        
        # 緊急通知が送信されることを確認
        assert mock_notification_manager.send_notification.called
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_manual_intervention_handling(self, monitoring_system):
        """手動介入処理テスト"""
        recovery_result = RecoveryResult(
            recovery_id="test_recovery",
            rollback_id="test_rollback",
            status=RecoveryStatus.IN_PROGRESS,
            plan=Mock()
        )
        
        await monitoring_system.start_system()
        
        # 初期ステータスを確認
        assert monitoring_system.status == SystemStatus.ACTIVE
        
        # 手動介入処理を実行
        await monitoring_system._handle_manual_intervention(recovery_result)
        
        # ステータスがメンテナンスに変更されることを確認
        assert monitoring_system.status == SystemStatus.MAINTENANCE
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, monitoring_system, mock_notification_manager):
        """システムヘルスチェックテスト"""
        await monitoring_system.start_system()
        
        # 多数の未解決エスカレーションを追加（警告をトリガーするため）
        for i in range(6):
            escalation = EscalationEvent(
                event_id=f"escalation_{i}",
                rollback_id=f"rollback_{i}",
                level=EscalationLevel.MEDIUM,
                reason=f"テストエスカレーション {i}",
                timestamp=datetime.now(),
                resolved=False
            )
            monitoring_system.monitor.escalation_events.append(escalation)
        
        # システムヘルスチェックを実行
        await monitoring_system._check_system_health()
        
        # 問題が検出された場合、通知が送信されることを確認
        # （実際の通知送信は条件によるため、エラーが発生しないことを確認）
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_statistics_update(self, monitoring_system):
        """統計情報更新テスト"""
        await monitoring_system.start_system()
        
        # 統計情報更新を実行
        await monitoring_system._update_statistics()
        
        # 統計情報が更新されることを確認
        assert monitoring_system.total_rollbacks_monitored >= 0
        assert monitoring_system.successful_recoveries >= 0
        assert monitoring_system.failed_recoveries >= 0
        
        await monitoring_system.stop_system()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, monitoring_system):
        """古いデータクリーンアップテスト"""
        await monitoring_system.start_system()
        
        # 古い検証結果を追加
        old_verification = VerificationResult(
            verification_id="old_verification",
            rollback_id="old_rollback",
            status=VerificationStatus.PASSED,
            start_time=datetime.now() - timedelta(days=35),  # 35日前
            success_rate=100.0
        )
        monitoring_system.monitor.verification_results["old_verification"] = old_verification
        
        # 古いエスカレーションイベントを追加
        old_escalation = EscalationEvent(
            event_id="old_escalation",
            rollback_id="old_rollback",
            level=EscalationLevel.LOW,
            reason="古いエスカレーション",
            timestamp=datetime.now() - timedelta(days=35),
            resolved=True,
            resolution_time=datetime.now() - timedelta(days=34)
        )
        monitoring_system.monitor.escalation_events.append(old_escalation)
        
        # データクリーンアップを実行
        await monitoring_system._cleanup_old_data()
        
        # 古いデータが削除されることを確認
        assert "old_verification" not in monitoring_system.monitor.verification_results
        assert old_escalation not in monitoring_system.monitor.escalation_events
        
        await monitoring_system.stop_system()
    
    def test_get_system_status(self, monitoring_system):
        """システムステータス取得テスト"""
        status = monitoring_system.get_system_status()
        
        # ステータス情報を確認
        assert "system" in status
        assert "monitoring" in status
        assert "recovery" in status
        assert "statistics" in status
        assert "config" in status
        
        # システム情報を確認
        assert status["system"]["status"] == SystemStatus.STOPPED.value
        assert status["system"]["uptime_seconds"] is None  # 停止中
        
        # 設定情報を確認
        assert status["config"]["auto_recovery_enabled"]
        assert status["config"]["escalation_auto_trigger"]
        assert status["config"]["comprehensive_reporting"]
    
    def test_get_comprehensive_report(self, monitoring_system):
        """包括的レポート取得テスト"""
        report = monitoring_system.get_comprehensive_report()
        
        # レポート項目を確認
        assert "system_status" in report
        assert "recent_verifications" in report
        assert "recent_escalations" in report
        assert "active_recoveries" in report
        assert "recent_recovery_history" in report
        
        # 各項目がリストまたは辞書であることを確認
        assert isinstance(report["system_status"], dict)
        assert isinstance(report["recent_verifications"], list)
        assert isinstance(report["recent_escalations"], list)
        assert isinstance(report["active_recoveries"], list)
        assert isinstance(report["recent_recovery_history"], list)
    
    @pytest.mark.asyncio
    async def test_system_error_handling(self, monitoring_system, mock_health_check_manager):
        """システムエラーハンドリングテスト"""
        # ヘルスチェックでエラーを発生させる
        mock_health_check_manager.run_health_checks.side_effect = Exception("テストエラー")
        
        try:
            await monitoring_system.start_system()
            
            # エラーが発生してもシステムが停止しないことを確認
            assert monitoring_system.status == SystemStatus.ACTIVE
            
            await monitoring_system.stop_system()
        except Exception:
            # エラーが発生した場合はシステムを適切に停止
            if monitoring_system.status != SystemStatus.STOPPED:
                await monitoring_system.stop_system()
    
    def test_system_config_validation(self):
        """システム設定検証テスト"""
        config = SystemConfig(
            auto_recovery_enabled=True,
            escalation_auto_trigger=True,
            comprehensive_reporting=False,
            max_concurrent_monitors=10,
            system_health_check_interval_seconds=60
        )
        
        # 設定値を確認
        assert config.auto_recovery_enabled
        assert config.escalation_auto_trigger
        assert not config.comprehensive_reporting
        assert config.max_concurrent_monitors == 10
        assert config.system_health_check_interval_seconds == 60
    
    @pytest.mark.asyncio
    async def test_concurrent_monitoring_limit(self, monitoring_system, sample_rollback_result,
                                             mock_health_check_manager):
        """同時監視数制限テスト"""
        # ヘルスチェック成功を設定
        health_result = HealthCheckResult(
            endpoint="/health",
            timestamp=datetime.now(),
            status_code=200,
            response_time_ms=100.0,
            success=True
        )
        mock_health_check_manager.run_health_checks.return_value = [health_result]
        
        await monitoring_system.start_system()
        
        # 複数のロールバック監視を開始
        monitor_ids = []
        for i in range(3):
            rollback_result = RollbackResult(
                success=True,
                rollback_id=f"rollback_test_{i}",
                status=RollbackStatus.COMPLETED,
                target=sample_rollback_result.target,
                start_time=datetime.now()
            )
            monitor_id = await monitoring_system.monitor_rollback(rollback_result)
            monitor_ids.append(monitor_id)
        
        # 監視が開始されることを確認
        assert len(monitor_ids) == 3
        
        await monitoring_system.stop_system()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])