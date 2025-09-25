"""
ロールバック監視システムのテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rollback.rollback_monitor import (
    RollbackMonitor, MonitoringConfig, VerificationResult, 
    EscalationEvent, MonitoringStatus, VerificationStatus, EscalationLevel
)
from rollback.rollback_executor import RollbackResult, RollbackStatus, RollbackTarget
from monitoring.health_check import HealthCheckResult
from monitoring.performance_monitor import PerformanceMetrics


class TestRollbackMonitor:
    """ロールバック監視システムのテスト"""
    
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
    def monitoring_config(self):
        """監視設定"""
        return MonitoringConfig(
            initial_monitoring_duration_minutes=1,  # テスト用に短縮
            extended_monitoring_duration_minutes=2,
            monitoring_interval_seconds=1,
            health_check_timeout_seconds=10,
            performance_check_duration_minutes=1,
            success_threshold_percentage=90.0,
            max_consecutive_failures=2,
            auto_recovery_enabled=True
        )
    
    @pytest.fixture
    def rollback_monitor(self, mock_health_check_manager, mock_performance_monitor, 
                        mock_notification_manager, monitoring_config):
        """ロールバック監視システム"""
        return RollbackMonitor(
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=monitoring_config
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
    async def test_start_stop_monitoring(self, rollback_monitor):
        """監視システムの開始・停止テスト"""
        # 初期状態は停止
        assert rollback_monitor.status == MonitoringStatus.STOPPED
        
        # 監視開始
        await rollback_monitor.start_monitoring()
        assert rollback_monitor.status == MonitoringStatus.ACTIVE
        
        # 監視停止
        await rollback_monitor.stop_monitoring()
        assert rollback_monitor.status == MonitoringStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_monitor_rollback_success(self, rollback_monitor, sample_rollback_result,
                                          mock_health_check_manager, mock_performance_monitor):
        """ロールバック監視成功テスト"""
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
        metrics = [
            PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=150.0,
                request_count=100,
                error_count=2
            )
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        # 監視開始
        await rollback_monitor.start_monitoring()
        
        # ロールバック監視を開始
        monitor_id = await rollback_monitor.monitor_rollback(sample_rollback_result)
        assert monitor_id == sample_rollback_result.rollback_id
        
        # 少し待機して監視が実行されることを確認
        await asyncio.sleep(0.5)
        
        # ヘルスチェックが呼ばれたことを確認
        assert mock_health_check_manager.run_health_checks.called
        
        # 監視停止
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_initial_verification_success(self, rollback_monitor, sample_rollback_result,
                                              mock_health_check_manager, mock_performance_monitor):
        """初期検証成功テスト"""
        # 成功するヘルスチェックを設定
        health_results = [
            HealthCheckResult("/health", datetime.now(), 200, 100.0, True),
            HealthCheckResult("/api/health", datetime.now(), 200, 120.0, True)
        ]
        mock_health_check_manager.run_health_checks.return_value = health_results
        
        # 良好なパフォーマンスメトリクスを設定
        metrics = [
            PerformanceMetrics(datetime.now(), 200.0, 100, 1),  # 1%エラー率
            PerformanceMetrics(datetime.now(), 180.0, 100, 2)   # 2%エラー率
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        await rollback_monitor.start_monitoring()
        
        # 初期検証を実行
        verification_result = await rollback_monitor._perform_initial_verification(sample_rollback_result)
        
        # 検証成功を確認
        assert verification_result.status == VerificationStatus.PASSED
        assert verification_result.success_rate == 100.0
        assert len(verification_result.health_check_results) > 0
        assert len(verification_result.performance_metrics) > 0
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_initial_verification_failure(self, rollback_monitor, sample_rollback_result,
                                              mock_health_check_manager, mock_performance_monitor):
        """初期検証失敗テスト"""
        # 失敗するヘルスチェックを設定
        health_results = [
            HealthCheckResult("/health", datetime.now(), 500, 5000.0, False),
            HealthCheckResult("/api/health", datetime.now(), 200, 120.0, True)
        ]
        mock_health_check_manager.run_health_checks.return_value = health_results
        
        # 悪いパフォーマンスメトリクスを設定
        metrics = [
            PerformanceMetrics(datetime.now(), 8000.0, 100, 15),  # 15%エラー率、8秒レスポンス
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        await rollback_monitor.start_monitoring()
        
        # 初期検証を実行
        verification_result = await rollback_monitor._perform_initial_verification(sample_rollback_result)
        
        # 検証失敗を確認
        assert verification_result.status == VerificationStatus.FAILED
        assert len(verification_result.error_messages) > 0
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_escalation_trigger(self, rollback_monitor, sample_rollback_result):
        """エスカレーショントリガーテスト"""
        escalation_triggered = False
        escalation_event = None
        
        def escalation_callback(event):
            nonlocal escalation_triggered, escalation_event
            escalation_triggered = True
            escalation_event = event
        
        rollback_monitor.add_callback('escalation_triggered', escalation_callback)
        
        await rollback_monitor.start_monitoring()
        
        # エスカレーションをトリガー
        await rollback_monitor._trigger_escalation(
            sample_rollback_result,
            EscalationLevel.HIGH,
            "テストエスカレーション"
        )
        
        # エスカレーションがトリガーされたことを確認
        assert escalation_triggered
        assert escalation_event is not None
        assert escalation_event.level == EscalationLevel.HIGH
        assert escalation_event.reason == "テストエスカレーション"
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_auto_recovery_success(self, rollback_monitor, sample_rollback_result,
                                       mock_health_check_manager):
        """自動復旧成功テスト"""
        # 最初は失敗、その後成功するヘルスチェックを設定
        health_calls = 0
        
        async def mock_health_check():
            nonlocal health_calls
            health_calls += 1
            if health_calls <= 2:
                # 最初の2回は失敗
                return [HealthCheckResult("/health", datetime.now(), 500, 5000.0, False)]
            else:
                # その後は成功
                return [HealthCheckResult("/health", datetime.now(), 200, 100.0, True)]
        
        mock_health_check_manager.run_health_checks.side_effect = mock_health_check
        
        await rollback_monitor.start_monitoring()
        
        # エスカレーションイベントを作成
        escalation_event = EscalationEvent(
            event_id="test_escalation",
            rollback_id=sample_rollback_result.rollback_id,
            level=EscalationLevel.MEDIUM,
            reason="テスト用エスカレーション",
            timestamp=datetime.now()
        )
        
        # 自動復旧を試行
        recovery_success = await rollback_monitor._attempt_auto_recovery(
            sample_rollback_result, escalation_event
        )
        
        # 復旧成功を確認
        assert recovery_success
        assert escalation_event.resolved
        assert "ヘルスチェックが正常に戻りました" in escalation_event.actions_taken
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_monitoring_status_api(self, rollback_monitor):
        """監視ステータスAPI テスト"""
        await rollback_monitor.start_monitoring()
        
        status = rollback_monitor.get_monitoring_status()
        
        # ステータス情報を確認
        assert status["status"] == "active"
        assert "active_monitors" in status
        assert "total_verifications" in status
        assert "total_escalations" in status
        assert "config" in status
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_verification_results_api(self, rollback_monitor, sample_rollback_result,
                                          mock_health_check_manager, mock_performance_monitor):
        """検証結果API テスト"""
        # 成功するヘルスチェックを設定
        mock_health_check_manager.run_health_checks.return_value = [
            HealthCheckResult("/health", datetime.now(), 200, 100.0, True)
        ]
        mock_performance_monitor.get_metrics_history.return_value = [
            PerformanceMetrics(datetime.now(), 200.0, 100, 1)
        ]
        
        await rollback_monitor.start_monitoring()
        
        # 検証を実行
        verification_result = await rollback_monitor._perform_initial_verification(sample_rollback_result)
        
        # API経由で検証結果を取得
        all_results = rollback_monitor.get_verification_results()
        rollback_results = rollback_monitor.get_verification_results(sample_rollback_result.rollback_id)
        
        # 結果を確認
        assert len(all_results) == 1
        assert len(rollback_results) == 1
        assert rollback_results[0].rollback_id == sample_rollback_result.rollback_id
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_escalation_resolution(self, rollback_monitor, sample_rollback_result):
        """エスカレーション解決テスト"""
        await rollback_monitor.start_monitoring()
        
        # エスカレーションをトリガー
        await rollback_monitor._trigger_escalation(
            sample_rollback_result,
            EscalationLevel.LOW,
            "テスト用エスカレーション"
        )
        
        # エスカレーションイベントを取得
        events = rollback_monitor.get_escalation_events(resolved=False)
        assert len(events) == 1
        
        event_id = events[0].event_id
        
        # エスカレーションを手動で解決
        resolution_success = await rollback_monitor.resolve_escalation(
            event_id, "テスト解決"
        )
        
        # 解決成功を確認
        assert resolution_success
        
        # 解決済みエスカレーションを確認
        resolved_events = rollback_monitor.get_escalation_events(resolved=True)
        assert len(resolved_events) == 1
        assert resolved_events[0].resolved
        assert "手動解決: テスト解決" in resolved_events[0].actions_taken
        
        await rollback_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_stop_rollback_monitoring(self, rollback_monitor, sample_rollback_result,
                                          mock_health_check_manager):
        """ロールバック監視停止テスト"""
        mock_health_check_manager.run_health_checks.return_value = [
            HealthCheckResult("/health", datetime.now(), 200, 100.0, True)
        ]
        
        await rollback_monitor.start_monitoring()
        
        # ロールバック監視を開始
        monitor_id = await rollback_monitor.monitor_rollback(sample_rollback_result)
        
        # アクティブな監視があることを確認
        assert monitor_id in rollback_monitor.active_monitors
        
        # 監視を停止
        stop_success = await rollback_monitor.stop_rollback_monitoring(monitor_id)
        
        # 停止成功を確認
        assert stop_success
        assert monitor_id not in rollback_monitor.active_monitors
        
        await rollback_monitor.stop_monitoring()
    
    def test_monitoring_config_validation(self):
        """監視設定検証テスト"""
        config = MonitoringConfig(
            initial_monitoring_duration_minutes=30,
            extended_monitoring_duration_minutes=120,
            monitoring_interval_seconds=30,
            success_threshold_percentage=95.0,
            max_consecutive_failures=3
        )
        
        # 設定値を確認
        assert config.initial_monitoring_duration_minutes == 30
        assert config.extended_monitoring_duration_minutes == 120
        assert config.monitoring_interval_seconds == 30
        assert config.success_threshold_percentage == 95.0
        assert config.max_consecutive_failures == 3
    
    @pytest.mark.asyncio
    async def test_error_handling(self, rollback_monitor, sample_rollback_result,
                                mock_health_check_manager):
        """エラーハンドリングテスト"""
        # ヘルスチェックでエラーを発生させる
        mock_health_check_manager.run_health_checks.side_effect = Exception("テストエラー")
        
        await rollback_monitor.start_monitoring()
        
        # 初期検証を実行（エラーが発生するはず）
        verification_result = await rollback_monitor._perform_initial_verification(sample_rollback_result)
        
        # エラーが適切に処理されていることを確認
        assert verification_result.status == VerificationStatus.FAILED
        assert any("テストエラー" in msg for msg in verification_result.error_messages)
        
        await rollback_monitor.stop_monitoring()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])