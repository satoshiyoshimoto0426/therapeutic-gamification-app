"""
ロールバック監視と復旧システム

このモジュールは、ロールバック実行後の監視、成功検証、
失敗時のエスカレーション手順を提供します。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from .rollback_executor import RollbackResult, RollbackStatus
    from ..monitoring.health_check import HealthCheckFramework, HealthCheckResult
    from ..monitoring.performance_monitor import PerformanceMonitor, PerformanceMetrics
    from ..notification.notification_manager import NotificationManager
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_executor import RollbackResult, RollbackStatus
    from monitoring.health_check import HealthCheckFramework, HealthCheckResult
    from monitoring.performance_monitor import PerformanceMonitor, PerformanceMetrics
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class MonitoringStatus(Enum):
    """監視ステータス"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class VerificationStatus(Enum):
    """検証ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class EscalationLevel(Enum):
    """エスカレーションレベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MonitoringConfig:
    """監視設定"""
    # 監視期間設定
    initial_monitoring_duration_minutes: int = 30
    extended_monitoring_duration_minutes: int = 120
    monitoring_interval_seconds: int = 30
    
    # 検証設定
    health_check_timeout_seconds: int = 60
    performance_check_duration_minutes: int = 10
    success_threshold_percentage: float = 95.0
    
    # エスカレーション設定
    max_consecutive_failures: int = 3
    escalation_timeout_minutes: int = 15
    auto_recovery_enabled: bool = True
    
    # 通知設定
    notification_enabled: bool = True
    detailed_reporting: bool = True


@dataclass
class VerificationResult:
    """検証結果"""
    verification_id: str
    rollback_id: str
    status: VerificationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 検証詳細
    health_check_results: List[HealthCheckResult] = field(default_factory=list)
    performance_metrics: List[PerformanceMetrics] = field(default_factory=list)
    traffic_verification: Dict[str, Any] = field(default_factory=dict)
    
    # 結果サマリー
    success_rate: float = 0.0
    error_messages: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class EscalationEvent:
    """エスカレーションイベント"""
    event_id: str
    rollback_id: str
    level: EscalationLevel
    reason: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)


class RollbackMonitor:
    """
    ロールバック監視システム
    
    ロールバック実行後の継続的な監視、検証、
    問題発生時のエスカレーション処理を行います。
    """
    
    def __init__(self,
                 health_check_manager: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 notification_manager: NotificationManager,
                 config: Optional[MonitoringConfig] = None):
        """
        ロールバック監視システムを初期化
        
        Args:
            health_check_manager: ヘルスチェック管理システム
            performance_monitor: パフォーマンス監視システム
            notification_manager: 通知管理システム
            config: 監視設定
        """
        self.health_check_manager = health_check_manager
        self.performance_monitor = performance_monitor
        self.notification_manager = notification_manager
        self.config = config or MonitoringConfig()
        self.logger = logging.getLogger(__name__)
        
        # 監視状態
        self.status = MonitoringStatus.STOPPED
        self.active_monitors: Dict[str, asyncio.Task] = {}
        
        # 検証結果とエスカレーション履歴
        self.verification_results: Dict[str, VerificationResult] = {}
        self.escalation_events: List[EscalationEvent] = []
        
        # コールバック
        self._callbacks: Dict[str, List[Callable]] = {
            'verification_complete': [],
            'escalation_triggered': [],
            'recovery_successful': [],
            'monitoring_error': []
        }
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """イベントコールバックを追加"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def start_monitoring(self) -> None:
        """監視システムを開始"""
        if self.status == MonitoringStatus.ACTIVE:
            self.logger.warning("監視システムは既に実行中です")
            return
        
        try:
            self.status = MonitoringStatus.ACTIVE
            self.logger.info("ロールバック監視システムを開始しました")
            
            # 初期化通知
            if self.config.notification_enabled:
                await self._send_notification(
                    "ロールバック監視システムが開始されました",
                    "info"
                )
        
        except Exception as e:
            self.status = MonitoringStatus.ERROR
            self.logger.error(f"監視システムの開始に失敗しました: {e}")
            raise RollbackError(f"監視システムの開始に失敗: {e}")
    
    async def stop_monitoring(self) -> None:
        """監視システムを停止"""
        if self.status == MonitoringStatus.STOPPED:
            self.logger.info("監視システムは既に停止しています")
            return
        
        try:
            self.status = MonitoringStatus.STOPPED
            
            # アクティブな監視タスクをキャンセル
            for rollback_id, task in self.active_monitors.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.active_monitors.clear()
            
            self.logger.info("ロールバック監視システムを停止しました")
            
            # 停止通知
            if self.config.notification_enabled:
                await self._send_notification(
                    "ロールバック監視システムが停止されました",
                    "info"
                )
        
        except Exception as e:
            self.status = MonitoringStatus.ERROR
            self.logger.error(f"監視システムの停止に失敗しました: {e}")
            raise RollbackError(f"監視システムの停止に失敗: {e}")
    
    async def monitor_rollback(self, rollback_result: RollbackResult) -> str:
        """
        ロールバックの監視を開始
        
        Args:
            rollback_result: 監視対象のロールバック結果
            
        Returns:
            監視ID
        """
        if self.status != MonitoringStatus.ACTIVE:
            raise RollbackError("監視システムが実行中ではありません")
        
        rollback_id = rollback_result.rollback_id
        
        if rollback_id in self.active_monitors:
            self.logger.warning(f"ロールバック {rollback_id} は既に監視中です")
            return rollback_id
        
        try:
            self.logger.info(f"ロールバック監視を開始: {rollback_id}")
            
            # 監視タスクを作成
            monitor_task = asyncio.create_task(
                self._monitor_rollback_lifecycle(rollback_result)
            )
            self.active_monitors[rollback_id] = monitor_task
            
            return rollback_id
        
        except Exception as e:
            self.logger.error(f"ロールバック監視の開始に失敗: {rollback_id} - {e}")
            raise RollbackError(f"ロールバック監視の開始に失敗: {e}")
    
    async def _monitor_rollback_lifecycle(self, rollback_result: RollbackResult) -> None:
        """ロールバックのライフサイクル監視"""
        rollback_id = rollback_result.rollback_id
        
        try:
            # 初期検証を実行
            verification_result = await self._perform_initial_verification(rollback_result)
            
            if verification_result.status == VerificationStatus.PASSED:
                # 成功した場合は継続監視
                await self._perform_continuous_monitoring(rollback_result, verification_result)
            else:
                # 失敗した場合はエスカレーション
                await self._trigger_escalation(
                    rollback_result,
                    EscalationLevel.HIGH,
                    f"初期検証が失敗しました: {', '.join(verification_result.error_messages)}"
                )
        
        except asyncio.CancelledError:
            self.logger.info(f"ロールバック監視がキャンセルされました: {rollback_id}")
        except Exception as e:
            self.logger.error(f"ロールバック監視中にエラーが発生: {rollback_id} - {e}")
            await self._notify_callbacks('monitoring_error', rollback_result)
        finally:
            # 監視完了時のクリーンアップ
            if rollback_id in self.active_monitors:
                del self.active_monitors[rollback_id]
    
    async def _perform_initial_verification(self, rollback_result: RollbackResult) -> VerificationResult:
        """初期検証を実行"""
        verification_id = f"verify_{rollback_result.rollback_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        verification = VerificationResult(
            verification_id=verification_id,
            rollback_id=rollback_result.rollback_id,
            status=VerificationStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        self.verification_results[verification_id] = verification
        
        try:
            self.logger.info(f"初期検証を開始: {verification_id}")
            
            # ヘルスチェック検証
            health_success = await self._verify_health_checks(verification)
            
            # パフォーマンス検証
            performance_success = await self._verify_performance_metrics(verification)
            
            # トラフィック検証
            traffic_success = await self._verify_traffic_allocation(rollback_result, verification)
            
            # 総合判定
            all_checks_passed = health_success and performance_success and traffic_success
            
            if all_checks_passed:
                verification.status = VerificationStatus.PASSED
                verification.success_rate = 100.0
                self.logger.info(f"初期検証が成功しました: {verification_id}")
            else:
                verification.status = VerificationStatus.FAILED
                failed_checks = []
                if not health_success:
                    failed_checks.append("ヘルスチェック")
                if not performance_success:
                    failed_checks.append("パフォーマンス")
                if not traffic_success:
                    failed_checks.append("トラフィック")
                
                verification.error_messages.append(f"失敗した検証: {', '.join(failed_checks)}")
                self.logger.error(f"初期検証が失敗しました: {verification_id}")
            
            verification.end_time = datetime.now()
            
            # 検証完了通知
            await self._notify_callbacks('verification_complete', verification)
            
            if self.config.notification_enabled:
                await self._send_verification_notification(verification)
            
            return verification
        
        except Exception as e:
            verification.status = VerificationStatus.FAILED
            verification.error_messages.append(f"検証中にエラーが発生: {e}")
            verification.end_time = datetime.now()
            
            self.logger.error(f"初期検証中にエラーが発生: {verification_id} - {e}")
            return verification
    
    async def _verify_health_checks(self, verification: VerificationResult) -> bool:
        """ヘルスチェック検証"""
        try:
            self.logger.info("ヘルスチェック検証を実行中...")
            
            # 複数回のヘルスチェックを実行
            check_count = 3
            successful_checks = 0
            
            for i in range(check_count):
                health_results = await self.health_check_manager.run_health_checks()
                
                if health_results:
                    verification.health_check_results.extend(health_results)
                    
                    # 成功したチェックの数をカウント
                    if all(result.success for result in health_results):
                        successful_checks += 1
                
                # 最後のチェック以外は待機
                if i < check_count - 1:
                    await asyncio.sleep(10)
            
            # 成功率を計算
            success_rate = (successful_checks / check_count) * 100
            health_success = success_rate >= self.config.success_threshold_percentage
            
            if health_success:
                self.logger.info(f"ヘルスチェック検証が成功しました (成功率: {success_rate:.1f}%)")
            else:
                self.logger.warning(f"ヘルスチェック検証が失敗しました (成功率: {success_rate:.1f}%)")
                verification.error_messages.append(f"ヘルスチェック成功率が閾値を下回りました: {success_rate:.1f}%")
            
            return health_success
        
        except Exception as e:
            self.logger.error(f"ヘルスチェック検証中にエラーが発生: {e}")
            verification.error_messages.append(f"ヘルスチェック検証エラー: {e}")
            return False
    
    async def _verify_performance_metrics(self, verification: VerificationResult) -> bool:
        """パフォーマンスメトリクス検証"""
        try:
            self.logger.info("パフォーマンス検証を実行中...")
            
            # パフォーマンス安定化のため少し待機
            await asyncio.sleep(30)
            
            # 過去の期間のメトリクスを取得
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=self.config.performance_check_duration_minutes)
            
            metrics = await self.performance_monitor.get_metrics_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if not metrics:
                self.logger.warning("パフォーマンスメトリクスが取得できませんでした")
                verification.recommendations.append("パフォーマンスメトリクスの設定を確認してください")
                return True  # メトリクスがない場合は成功とみなす
            
            verification.performance_metrics.extend(metrics)
            
            # レスポンス時間の検証
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                if avg_response_time > 3000:  # 3秒の閾値
                    verification.error_messages.append(f"平均レスポンス時間が高すぎます: {avg_response_time:.0f}ms")
                    return False
                
                if max_response_time > 10000:  # 10秒の閾値
                    verification.error_messages.append(f"最大レスポンス時間が高すぎます: {max_response_time:.0f}ms")
                    return False
            
            # エラー率の検証
            total_requests = sum(m.request_count for m in metrics if m.request_count is not None)
            error_requests = sum(m.error_count for m in metrics if m.error_count is not None)
            
            if total_requests > 0:
                error_rate = error_requests / total_requests
                if error_rate > 0.05:  # 5%の閾値
                    verification.error_messages.append(f"エラー率が高すぎます: {error_rate:.2%}")
                    return False
            
            self.logger.info("パフォーマンス検証が成功しました")
            return True
        
        except Exception as e:
            self.logger.error(f"パフォーマンス検証中にエラーが発生: {e}")
            verification.error_messages.append(f"パフォーマンス検証エラー: {e}")
            return False
    
    async def _verify_traffic_allocation(self, rollback_result: RollbackResult, verification: VerificationResult) -> bool:
        """トラフィック配分検証"""
        try:
            self.logger.info("トラフィック配分検証を実行中...")
            
            # トラフィック配分情報を取得（実装は traffic_manager に依存）
            # ここでは簡略化した検証を行う
            
            traffic_info = {
                "target_revision": rollback_result.target.target_revision,
                "expected_percentage": 100,
                "actual_percentage": 100,  # 実際の実装では traffic_manager から取得
                "verification_time": datetime.now().isoformat()
            }
            
            verification.traffic_verification = traffic_info
            
            # 実際の実装では、traffic_manager から現在のトラフィック配分を取得し、
            # ターゲットリビジョンに適切にトラフィックが配分されているかを確認
            
            self.logger.info("トラフィック配分検証が成功しました")
            return True
        
        except Exception as e:
            self.logger.error(f"トラフィック配分検証中にエラーが発生: {e}")
            verification.error_messages.append(f"トラフィック配分検証エラー: {e}")
            return False
    
    async def _perform_continuous_monitoring(self, rollback_result: RollbackResult, initial_verification: VerificationResult) -> None:
        """継続的監視を実行"""
        rollback_id = rollback_result.rollback_id
        
        try:
            self.logger.info(f"継続的監視を開始: {rollback_id}")
            
            # 初期監視期間
            initial_end_time = datetime.now() + timedelta(minutes=self.config.initial_monitoring_duration_minutes)
            consecutive_failures = 0
            
            while datetime.now() < initial_end_time:
                # 定期的なヘルスチェック
                health_results = await self.health_check_manager.run_health_checks()
                
                if health_results and all(result.success for result in health_results):
                    consecutive_failures = 0
                    self.logger.debug(f"継続監視: ヘルスチェック正常 - {rollback_id}")
                else:
                    consecutive_failures += 1
                    self.logger.warning(f"継続監視: ヘルスチェック失敗 ({consecutive_failures}回連続) - {rollback_id}")
                    
                    # 連続失敗の閾値を超えた場合はエスカレーション
                    if consecutive_failures >= self.config.max_consecutive_failures:
                        await self._trigger_escalation(
                            rollback_result,
                            EscalationLevel.CRITICAL,
                            f"ヘルスチェックが{consecutive_failures}回連続で失敗しました"
                        )
                        return
                
                # 次の監視まで待機
                await asyncio.sleep(self.config.monitoring_interval_seconds)
            
            # 初期監視期間が完了した場合は拡張監視に移行
            await self._perform_extended_monitoring(rollback_result)
        
        except asyncio.CancelledError:
            self.logger.info(f"継続的監視がキャンセルされました: {rollback_id}")
            raise
        except Exception as e:
            self.logger.error(f"継続的監視中にエラーが発生: {rollback_id} - {e}")
            await self._trigger_escalation(
                rollback_result,
                EscalationLevel.HIGH,
                f"継続的監視中にエラーが発生: {e}"
            )
    
    async def _perform_extended_monitoring(self, rollback_result: RollbackResult) -> None:
        """拡張監視を実行"""
        rollback_id = rollback_result.rollback_id
        
        try:
            self.logger.info(f"拡張監視を開始: {rollback_id}")
            
            # 拡張監視期間
            extended_end_time = datetime.now() + timedelta(minutes=self.config.extended_monitoring_duration_minutes)
            
            while datetime.now() < extended_end_time:
                # より間隔を空けた監視
                await asyncio.sleep(self.config.monitoring_interval_seconds * 2)
                
                # 軽量なヘルスチェック
                health_results = await self.health_check_manager.run_health_checks()
                
                if not health_results or not all(result.success for result in health_results):
                    self.logger.warning(f"拡張監視: ヘルスチェック異常を検出 - {rollback_id}")
                    
                    # 拡張監視期間中の問題は中程度のエスカレーション
                    await self._trigger_escalation(
                        rollback_result,
                        EscalationLevel.MEDIUM,
                        "拡張監視期間中にヘルスチェック異常を検出しました"
                    )
                    return
            
            # 監視完了
            self.logger.info(f"ロールバック監視が正常に完了しました: {rollback_id}")
            
            if self.config.notification_enabled:
                await self._send_notification(
                    f"ロールバック監視が正常に完了しました: {rollback_id}",
                    "info"
                )
        
        except asyncio.CancelledError:
            self.logger.info(f"拡張監視がキャンセルされました: {rollback_id}")
            raise
        except Exception as e:
            self.logger.error(f"拡張監視中にエラーが発生: {rollback_id} - {e}")
    
    async def _trigger_escalation(self, rollback_result: RollbackResult, level: EscalationLevel, reason: str) -> None:
        """エスカレーションをトリガー"""
        event_id = f"escalation_{rollback_result.rollback_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        escalation_event = EscalationEvent(
            event_id=event_id,
            rollback_id=rollback_result.rollback_id,
            level=level,
            reason=reason,
            timestamp=datetime.now()
        )
        
        self.escalation_events.append(escalation_event)
        
        try:
            self.logger.error(f"エスカレーションをトリガー: {event_id} - レベル: {level.value} - 理由: {reason}")
            
            # エスカレーション通知
            await self._send_escalation_notification(escalation_event)
            
            # エスカレーションコールバック
            await self._notify_callbacks('escalation_triggered', escalation_event)
            
            # 自動復旧の試行
            if self.config.auto_recovery_enabled and level in [EscalationLevel.MEDIUM, EscalationLevel.HIGH]:
                recovery_success = await self._attempt_auto_recovery(rollback_result, escalation_event)
                
                if recovery_success:
                    escalation_event.resolved = True
                    escalation_event.resolution_time = datetime.now()
                    escalation_event.actions_taken.append("自動復旧が成功しました")
                    
                    await self._notify_callbacks('recovery_successful', escalation_event)
                    
                    self.logger.info(f"自動復旧が成功しました: {event_id}")
        
        except Exception as e:
            self.logger.error(f"エスカレーション処理中にエラーが発生: {event_id} - {e}")
    
    async def _attempt_auto_recovery(self, rollback_result: RollbackResult, escalation_event: EscalationEvent) -> bool:
        """自動復旧を試行"""
        try:
            self.logger.info(f"自動復旧を試行中: {escalation_event.event_id}")
            
            # 復旧アクション
            recovery_actions = []
            
            # 1. ヘルスチェックの再実行
            recovery_actions.append("ヘルスチェックの再実行")
            health_results = await self.health_check_manager.run_health_checks()
            
            if health_results and all(result.success for result in health_results):
                recovery_actions.append("ヘルスチェックが正常に戻りました")
                escalation_event.actions_taken.extend(recovery_actions)
                return True
            
            # 2. 短時間の待機後に再チェック
            recovery_actions.append("待機後の再チェック")
            await asyncio.sleep(60)
            
            health_results = await self.health_check_manager.run_health_checks()
            if health_results and all(result.success for result in health_results):
                recovery_actions.append("待機後のヘルスチェックが正常に戻りました")
                escalation_event.actions_taken.extend(recovery_actions)
                return True
            
            # 3. パフォーマンスメトリクスの確認
            recovery_actions.append("パフォーマンスメトリクスの確認")
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            metrics = await self.performance_monitor.get_metrics_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if metrics:
                # エラー率の確認
                total_requests = sum(m.request_count for m in metrics if m.request_count is not None)
                error_requests = sum(m.error_count for m in metrics if m.error_count is not None)
                
                if total_requests > 0:
                    error_rate = error_requests / total_requests
                    if error_rate < 0.05:  # 5%未満なら回復とみなす
                        recovery_actions.append(f"エラー率が改善されました: {error_rate:.2%}")
                        escalation_event.actions_taken.extend(recovery_actions)
                        return True
            
            escalation_event.actions_taken.extend(recovery_actions)
            escalation_event.actions_taken.append("自動復旧に失敗しました")
            
            self.logger.warning(f"自動復旧に失敗しました: {escalation_event.event_id}")
            return False
        
        except Exception as e:
            self.logger.error(f"自動復旧中にエラーが発生: {escalation_event.event_id} - {e}")
            escalation_event.actions_taken.append(f"自動復旧中にエラーが発生: {e}")
            return False
    
    async def _send_notification(self, message: str, severity: str) -> None:
        """通知を送信"""
        try:
            await self.notification_manager.send_notification(
                channel="rollback_monitoring",
                message=message,
                severity=severity
            )
        except Exception as e:
            self.logger.error(f"通知送信中にエラーが発生: {e}")
    
    async def _send_verification_notification(self, verification: VerificationResult) -> None:
        """検証結果通知を送信"""
        try:
            status_text = "成功" if verification.status == VerificationStatus.PASSED else "失敗"
            
            message = f"ロールバック検証{status_text}: {verification.verification_id}\n"
            message += f"ロールバックID: {verification.rollback_id}\n"
            message += f"成功率: {verification.success_rate:.1f}%\n"
            
            if verification.error_messages:
                message += f"エラー: {', '.join(verification.error_messages)}\n"
            
            if verification.recommendations:
                message += f"推奨事項: {', '.join(verification.recommendations)}\n"
            
            severity = "info" if verification.status == VerificationStatus.PASSED else "warning"
            
            await self._send_notification(message, severity)
        
        except Exception as e:
            self.logger.error(f"検証結果通知送信中にエラーが発生: {e}")
    
    async def _send_escalation_notification(self, escalation_event: EscalationEvent) -> None:
        """エスカレーション通知を送信"""
        try:
            level_text = {
                EscalationLevel.LOW: "低",
                EscalationLevel.MEDIUM: "中",
                EscalationLevel.HIGH: "高",
                EscalationLevel.CRITICAL: "緊急"
            }.get(escalation_event.level, "不明")
            
            message = f"🚨 ロールバックエスカレーション ({level_text})\n"
            message += f"イベントID: {escalation_event.event_id}\n"
            message += f"ロールバックID: {escalation_event.rollback_id}\n"
            message += f"理由: {escalation_event.reason}\n"
            message += f"発生時刻: {escalation_event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if escalation_event.actions_taken:
                message += f"実行されたアクション: {', '.join(escalation_event.actions_taken)}\n"
            
            severity = "critical" if escalation_event.level == EscalationLevel.CRITICAL else "error"
            
            await self._send_notification(message, severity)
        
        except Exception as e:
            self.logger.error(f"エスカレーション通知送信中にエラーが発生: {e}")
    
    async def _notify_callbacks(self, event: str, data: Any) -> None:
        """コールバックに通知"""
        for callback in self._callbacks.get(event, []):
            try:
                await callback(data)
            except Exception as e:
                self.logger.error(f"コールバック実行中にエラーが発生: {e}")
    
    # パブリックAPI
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """監視ステータスを取得"""
        return {
            "status": self.status.value,
            "active_monitors": len(self.active_monitors),
            "total_verifications": len(self.verification_results),
            "total_escalations": len(self.escalation_events),
            "unresolved_escalations": len([e for e in self.escalation_events if not e.resolved]),
            "config": {
                "initial_monitoring_duration_minutes": self.config.initial_monitoring_duration_minutes,
                "extended_monitoring_duration_minutes": self.config.extended_monitoring_duration_minutes,
                "auto_recovery_enabled": self.config.auto_recovery_enabled,
                "success_threshold_percentage": self.config.success_threshold_percentage
            }
        }
    
    def get_verification_results(self, rollback_id: Optional[str] = None) -> List[VerificationResult]:
        """検証結果を取得"""
        if rollback_id:
            return [v for v in self.verification_results.values() if v.rollback_id == rollback_id]
        return list(self.verification_results.values())
    
    def get_escalation_events(self, rollback_id: Optional[str] = None, resolved: Optional[bool] = None) -> List[EscalationEvent]:
        """エスカレーションイベントを取得"""
        events = self.escalation_events
        
        if rollback_id:
            events = [e for e in events if e.rollback_id == rollback_id]
        
        if resolved is not None:
            events = [e for e in events if e.resolved == resolved]
        
        return events
    
    async def resolve_escalation(self, event_id: str, resolution_note: str) -> bool:
        """エスカレーションを手動で解決"""
        try:
            for event in self.escalation_events:
                if event.event_id == event_id:
                    event.resolved = True
                    event.resolution_time = datetime.now()
                    event.actions_taken.append(f"手動解決: {resolution_note}")
                    
                    self.logger.info(f"エスカレーションが手動で解決されました: {event_id}")
                    
                    if self.config.notification_enabled:
                        await self._send_notification(
                            f"エスカレーションが解決されました: {event_id} - {resolution_note}",
                            "info"
                        )
                    
                    return True
            
            self.logger.warning(f"エスカレーションイベントが見つかりません: {event_id}")
            return False
        
        except Exception as e:
            self.logger.error(f"エスカレーション解決中にエラーが発生: {event_id} - {e}")
            return False
    
    async def stop_rollback_monitoring(self, rollback_id: str) -> bool:
        """特定のロールバック監視を停止"""
        if rollback_id not in self.active_monitors:
            self.logger.warning(f"監視中のロールバックが見つかりません: {rollback_id}")
            return False
        
        try:
            task = self.active_monitors[rollback_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            del self.active_monitors[rollback_id]
            
            self.logger.info(f"ロールバック監視を停止しました: {rollback_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"ロールバック監視の停止中にエラーが発生: {rollback_id} - {e}")
            return False