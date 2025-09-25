"""
統合ロールバック監視システム

このモジュールは、ロールバック監視、復旧、エスカレーション機能を
統合した包括的なシステムを提供します。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

try:
    from .rollback_executor import RollbackResult, RollbackStatus
    from .rollback_monitor import RollbackMonitor, MonitoringConfig, VerificationResult, EscalationEvent
    from .rollback_recovery import RollbackRecovery, RecoveryConfig, RecoveryResult
    from ..deployment.cloud_run.traffic_manager import TrafficManager
    from ..deployment.cloud_run.revision_manager import RevisionManager
    from ..monitoring.health_check import HealthCheckFramework
    from ..monitoring.performance_monitor import PerformanceMonitor
    from ..notification.notification_manager import NotificationManager
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_executor import RollbackResult, RollbackStatus
    from rollback.rollback_monitor import RollbackMonitor, MonitoringConfig, VerificationResult, EscalationEvent
    from rollback.rollback_recovery import RollbackRecovery, RecoveryConfig, RecoveryResult
    from deployment.cloud_run.traffic_manager import TrafficManager
    from deployment.cloud_run.revision_manager import RevisionManager
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class SystemStatus(Enum):
    """システムステータス"""
    STOPPED = "stopped"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class SystemConfig:
    """システム設定"""
    monitoring_config: Optional[MonitoringConfig] = None
    recovery_config: Optional[RecoveryConfig] = None
    
    # 統合設定
    auto_recovery_enabled: bool = True
    escalation_auto_trigger: bool = True
    comprehensive_reporting: bool = True
    
    # システム設定
    max_concurrent_monitors: int = 10
    system_health_check_interval_seconds: int = 60


class RollbackMonitoringSystem:
    """
    統合ロールバック監視システム
    
    ロールバック監視、復旧、エスカレーション機能を統合し、
    包括的なロールバック管理を提供します。
    """
    
    def __init__(self,
                 traffic_manager: TrafficManager,
                 revision_manager: RevisionManager,
                 health_check_manager: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 notification_manager: NotificationManager,
                 config: Optional[SystemConfig] = None):
        """
        統合ロールバック監視システムを初期化
        
        Args:
            traffic_manager: トラフィック管理システム
            revision_manager: リビジョン管理システム
            health_check_manager: ヘルスチェック管理システム
            performance_monitor: パフォーマンス監視システム
            notification_manager: 通知管理システム
            config: システム設定
        """
        self.config = config or SystemConfig()
        self.logger = logging.getLogger(__name__)
        
        # コアコンポーネント
        self.traffic_manager = traffic_manager
        self.revision_manager = revision_manager
        self.health_check_manager = health_check_manager
        self.performance_monitor = performance_monitor
        self.notification_manager = notification_manager
        
        # 監視・復旧システム
        self.monitor = RollbackMonitor(
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=self.config.monitoring_config or MonitoringConfig()
        )
        
        self.recovery = RollbackRecovery(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            notification_manager=notification_manager,
            config=self.config.recovery_config or RecoveryConfig()
        )
        
        # システム状態
        self.status = SystemStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self._system_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # 統計情報
        self.total_rollbacks_monitored = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        
        # イベント統合
        self._setup_event_integration()
    
    def _setup_event_integration(self) -> None:
        """イベント統合を設定"""
        # 監視システムのコールバック
        self.monitor.add_callback('escalation_triggered', self._handle_escalation)
        self.monitor.add_callback('verification_complete', self._handle_verification_complete)
        self.monitor.add_callback('monitoring_error', self._handle_monitoring_error)
        
        # 復旧システムのコールバック
        self.recovery.add_callback('recovery_completed', self._handle_recovery_complete)
        self.recovery.add_callback('recovery_failed', self._handle_recovery_failed)
        self.recovery.add_callback('manual_intervention_required', self._handle_manual_intervention)
    
    async def start_system(self) -> None:
        """システムを開始"""
        if self.status != SystemStatus.STOPPED:
            self.logger.warning(f"システムは既に実行中です: {self.status}")
            return
        
        try:
            self.status = SystemStatus.STARTING
            self.start_time = datetime.now()
            
            self.logger.info("統合ロールバック監視システムを開始中...")
            
            # 監視システムを開始
            await self.monitor.start_monitoring()
            
            # システム管理タスクを開始
            self._system_task = asyncio.create_task(self._system_management_loop())
            
            self.status = SystemStatus.ACTIVE
            
            self.logger.info("統合ロールバック監視システムが開始されました")
            
            # 開始通知
            await self._send_system_notification(
                "統合ロールバック監視システムが開始されました",
                "info"
            )
        
        except Exception as e:
            self.status = SystemStatus.ERROR
            self.logger.error(f"システム開始に失敗: {e}")
            await self._cleanup()
            raise RollbackError(f"システム開始に失敗: {e}")
    
    async def stop_system(self) -> None:
        """システムを停止"""
        if self.status == SystemStatus.STOPPED:
            self.logger.info("システムは既に停止しています")
            return
        
        try:
            self.status = SystemStatus.STOPPING
            self.logger.info("統合ロールバック監視システムを停止中...")
            
            # シャットダウンシグナル
            self._shutdown_event.set()
            
            # システム管理タスクを停止
            if self._system_task:
                self._system_task.cancel()
                try:
                    await self._system_task
                except asyncio.CancelledError:
                    pass
            
            await self._cleanup()
            
            self.status = SystemStatus.STOPPED
            
            self.logger.info("統合ロールバック監視システムが停止されました")
            
            # 停止通知
            await self._send_system_notification(
                "統合ロールバック監視システムが停止されました",
                "info"
            )
        
        except Exception as e:
            self.status = SystemStatus.ERROR
            self.logger.error(f"システム停止に失敗: {e}")
            raise RollbackError(f"システム停止に失敗: {e}")
    
    async def _cleanup(self) -> None:
        """リソースをクリーンアップ"""
        try:
            # 監視システムを停止
            await self.monitor.stop_monitoring()
            
            # アクティブな復旧をキャンセル
            active_recoveries = self.recovery.get_active_recoveries()
            for recovery in active_recoveries:
                await self.recovery.cancel_recovery(
                    recovery.recovery_id,
                    "システム停止のため"
                )
        
        except Exception as e:
            self.logger.error(f"クリーンアップ中にエラー: {e}")
    
    async def _system_management_loop(self) -> None:
        """システム管理ループ"""
        try:
            while not self._shutdown_event.is_set():
                await self._perform_system_maintenance()
                
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.config.system_health_check_interval_seconds
                    )
                    break  # シャットダウン要求
                except asyncio.TimeoutError:
                    continue  # 継続
        
        except asyncio.CancelledError:
            self.logger.info("システム管理ループがキャンセルされました")
        except Exception as e:
            self.logger.error(f"システム管理ループでエラー: {e}")
            self.status = SystemStatus.ERROR
    
    async def _perform_system_maintenance(self) -> None:
        """システムメンテナンスを実行"""
        try:
            # システムヘルスチェック
            await self._check_system_health()
            
            # 統計情報の更新
            await self._update_statistics()
            
            # 古いデータのクリーンアップ
            await self._cleanup_old_data()
        
        except Exception as e:
            self.logger.error(f"システムメンテナンス中にエラー: {e}")
    
    async def _check_system_health(self) -> None:
        """システムヘルスをチェック"""
        try:
            # 各コンポーネントの状態をチェック
            monitor_status = self.monitor.get_monitoring_status()
            recovery_status = self.recovery.get_system_status()
            
            # 問題のあるコンポーネントを特定
            issues = []
            
            if monitor_status["status"] != "active":
                issues.append(f"監視システム異常: {monitor_status['status']}")
            
            if monitor_status["unresolved_escalations"] > 5:
                issues.append(f"未解決エスカレーション多数: {monitor_status['unresolved_escalations']}件")
            
            if recovery_status["active_recoveries"] > self.config.max_concurrent_monitors:
                issues.append(f"同時復旧数が上限を超過: {recovery_status['active_recoveries']}件")
            
            # 問題がある場合は警告
            if issues:
                self.logger.warning(f"システムヘルス問題を検出: {', '.join(issues)}")
                
                # 重要な問題の場合は通知
                if len(issues) > 2:
                    await self._send_system_notification(
                        f"システムヘルス問題: {', '.join(issues)}",
                        "warning"
                    )
        
        except Exception as e:
            self.logger.error(f"システムヘルスチェック中にエラー: {e}")
    
    async def _update_statistics(self) -> None:
        """統計情報を更新"""
        try:
            # 監視統計
            monitor_status = self.monitor.get_monitoring_status()
            self.total_rollbacks_monitored = monitor_status.get("total_verifications", 0)
            
            # 復旧統計
            recovery_history = self.recovery.get_recovery_history()
            self.successful_recoveries = len([r for r in recovery_history if r.success])
            self.failed_recoveries = len([r for r in recovery_history if not r.success])
        
        except Exception as e:
            self.logger.error(f"統計情報更新中にエラー: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """古いデータをクリーンアップ"""
        try:
            # 古い検証結果をクリーンアップ（30日以上前）
            cutoff_date = datetime.now() - timedelta(days=30)
            
            old_verifications = [
                v for v in self.monitor.verification_results.values()
                if v.start_time < cutoff_date
            ]
            
            for verification in old_verifications:
                if verification.verification_id in self.monitor.verification_results:
                    del self.monitor.verification_results[verification.verification_id]
            
            if old_verifications:
                self.logger.info(f"古い検証結果をクリーンアップ: {len(old_verifications)}件")
            
            # 古いエスカレーションイベントをクリーンアップ（解決済みで7日以上前）
            old_escalations = [
                e for e in self.monitor.escalation_events
                if e.resolved and e.timestamp < cutoff_date - timedelta(days=23)  # 7日前
            ]
            
            for escalation in old_escalations:
                self.monitor.escalation_events.remove(escalation)
            
            if old_escalations:
                self.logger.info(f"古いエスカレーションイベントをクリーンアップ: {len(old_escalations)}件")
        
        except Exception as e:
            self.logger.error(f"データクリーンアップ中にエラー: {e}")
    
    # イベントハンドラー
    
    async def _handle_escalation(self, escalation_event: EscalationEvent) -> None:
        """エスカレーションイベントを処理"""
        try:
            self.logger.info(f"エスカレーションイベントを処理: {escalation_event.event_id}")
            
            # 自動復旧が有効な場合は復旧を開始
            if self.config.auto_recovery_enabled and self.config.escalation_auto_trigger:
                # ロールバック結果を取得（簡略化）
                rollback_result = RollbackResult(
                    success=False,
                    rollback_id=escalation_event.rollback_id,
                    status=RollbackStatus.FAILED,
                    target=None,  # 実際の実装では適切な値を設定
                    start_time=escalation_event.timestamp
                )
                
                # 復旧を開始
                recovery_id = await self.recovery.initiate_recovery(rollback_result, escalation_event)
                
                self.logger.info(f"自動復旧を開始: {recovery_id}")
        
        except Exception as e:
            self.logger.error(f"エスカレーション処理中にエラー: {e}")
    
    async def _handle_verification_complete(self, verification_result: VerificationResult) -> None:
        """検証完了イベントを処理"""
        try:
            if verification_result.status.value == "passed":
                self.logger.info(f"検証が成功しました: {verification_result.verification_id}")
            else:
                self.logger.warning(f"検証が失敗しました: {verification_result.verification_id}")
                
                # 包括的レポートが有効な場合は詳細レポートを生成
                if self.config.comprehensive_reporting:
                    await self._generate_verification_report(verification_result)
        
        except Exception as e:
            self.logger.error(f"検証完了処理中にエラー: {e}")
    
    async def _handle_monitoring_error(self, rollback_result: RollbackResult) -> None:
        """監視エラーイベントを処理"""
        try:
            self.logger.error(f"監視エラーが発生: {rollback_result.rollback_id}")
            
            # エラー通知
            await self._send_system_notification(
                f"ロールバック監視エラー: {rollback_result.rollback_id}",
                "error"
            )
        
        except Exception as e:
            self.logger.error(f"監視エラー処理中にエラー: {e}")
    
    async def _handle_recovery_complete(self, recovery_result: RecoveryResult) -> None:
        """復旧完了イベントを処理"""
        try:
            self.logger.info(f"復旧が完了しました: {recovery_result.recovery_id}")
            
            # 成功統計を更新
            if recovery_result.success:
                self.successful_recoveries += 1
            
            # 包括的レポートを生成
            if self.config.comprehensive_reporting:
                await self._generate_recovery_report(recovery_result)
        
        except Exception as e:
            self.logger.error(f"復旧完了処理中にエラー: {e}")
    
    async def _handle_recovery_failed(self, recovery_result: RecoveryResult) -> None:
        """復旧失敗イベントを処理"""
        try:
            self.logger.error(f"復旧が失敗しました: {recovery_result.recovery_id}")
            
            # 失敗統計を更新
            self.failed_recoveries += 1
            
            # 緊急通知
            await self._send_system_notification(
                f"復旧失敗: {recovery_result.recovery_id} - {recovery_result.final_message}",
                "critical"
            )
        
        except Exception as e:
            self.logger.error(f"復旧失敗処理中にエラー: {e}")
    
    async def _handle_manual_intervention(self, recovery_result: RecoveryResult) -> None:
        """手動介入要求イベントを処理"""
        try:
            self.logger.warning(f"手動介入が要求されました: {recovery_result.recovery_id}")
            
            # システムステータスを一時的にメンテナンスに変更
            if self.status == SystemStatus.ACTIVE:
                previous_status = self.status
                self.status = SystemStatus.MAINTENANCE
                
                # 一定時間後に元のステータスに戻す
                async def restore_status():
                    await asyncio.sleep(3600)  # 1時間後
                    if self.status == SystemStatus.MAINTENANCE:
                        self.status = previous_status
                
                asyncio.create_task(restore_status())
        
        except Exception as e:
            self.logger.error(f"手動介入処理中にエラー: {e}")
    
    # レポート生成
    
    async def _generate_verification_report(self, verification_result: VerificationResult) -> None:
        """検証レポートを生成"""
        try:
            report = f"""
# ロールバック検証レポート

## 基本情報
- 検証ID: {verification_result.verification_id}
- ロールバックID: {verification_result.rollback_id}
- ステータス: {verification_result.status.value}
- 開始時刻: {verification_result.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- 終了時刻: {verification_result.end_time.strftime('%Y-%m-%d %H:%M:%S') if verification_result.end_time else 'N/A'}
- 成功率: {verification_result.success_rate:.1f}%

## ヘルスチェック結果
{chr(10).join([f"- {r.endpoint}: {'成功' if r.success else '失敗'} ({r.response_time_ms}ms)" for r in verification_result.health_check_results])}

## パフォーマンスメトリクス
{chr(10).join([f"- {m.timestamp}: レスポンス時間 {m.response_time_ms}ms, エラー率 {(m.error_count/m.request_count*100):.1f}%" for m in verification_result.performance_metrics[:5]])}

## エラーメッセージ
{chr(10).join([f"- {msg}" for msg in verification_result.error_messages])}

## 推奨事項
{chr(10).join([f"- {rec}" for rec in verification_result.recommendations])}
            """
            
            # レポートを通知として送信
            await self.notification_manager.send_notification(
                channel="reports",
                message=report,
                severity="info"
            )
        
        except Exception as e:
            self.logger.error(f"検証レポート生成中にエラー: {e}")
    
    async def _generate_recovery_report(self, recovery_result: RecoveryResult) -> None:
        """復旧レポートを生成"""
        try:
            duration = (recovery_result.end_time - recovery_result.start_time).total_seconds() if recovery_result.end_time else 0
            
            report = f"""
# ロールバック復旧レポート

## 基本情報
- 復旧ID: {recovery_result.recovery_id}
- ロールバックID: {recovery_result.rollback_id}
- ステータス: {recovery_result.status.value}
- 成功: {'はい' if recovery_result.success else 'いいえ'}
- 開始時刻: {recovery_result.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- 終了時刻: {recovery_result.end_time.strftime('%Y-%m-%d %H:%M:%S') if recovery_result.end_time else 'N/A'}
- 所要時間: {duration:.0f}秒

## 復旧計画
- 計画ID: {recovery_result.plan.plan_id}
- エスカレーションレベル: {recovery_result.plan.escalation_level.value}
- 予想所要時間: {recovery_result.plan.estimated_duration_minutes}分
- 優先度: {recovery_result.plan.priority}

## 実行されたアクション
{chr(10).join([f"- {a.timestamp.strftime('%H:%M:%S')} {a.strategy.value}: {a.description} ({'成功' if a.success else '失敗'})" for a in recovery_result.actions_taken])}

## 最終メッセージ
{recovery_result.final_message or 'なし'}
            """
            
            # レポートを通知として送信
            await self.notification_manager.send_notification(
                channel="reports",
                message=report,
                severity="info" if recovery_result.success else "warning"
            )
        
        except Exception as e:
            self.logger.error(f"復旧レポート生成中にエラー: {e}")
    
    async def _send_system_notification(self, message: str, severity: str) -> None:
        """システム通知を送信"""
        try:
            await self.notification_manager.send_notification(
                channel="system",
                message=f"[統合監視システム] {message}",
                severity=severity
            )
        except Exception as e:
            self.logger.error(f"システム通知送信中にエラー: {e}")
    
    # パブリックAPI
    
    async def monitor_rollback(self, rollback_result: RollbackResult) -> str:
        """ロールバックの監視を開始"""
        if self.status != SystemStatus.ACTIVE:
            raise RollbackError("システムがアクティブではありません")
        
        return await self.monitor.monitor_rollback(rollback_result)
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        monitor_status = self.monitor.get_monitoring_status()
        recovery_status = self.recovery.get_system_status()
        
        return {
            "system": {
                "status": self.status.value,
                "uptime_seconds": uptime,
                "start_time": self.start_time.isoformat() if self.start_time else None
            },
            "monitoring": monitor_status,
            "recovery": recovery_status,
            "statistics": {
                "total_rollbacks_monitored": self.total_rollbacks_monitored,
                "successful_recoveries": self.successful_recoveries,
                "failed_recoveries": self.failed_recoveries,
                "recovery_success_rate": (self.successful_recoveries / (self.successful_recoveries + self.failed_recoveries) * 100) if (self.successful_recoveries + self.failed_recoveries) > 0 else 0
            },
            "config": {
                "auto_recovery_enabled": self.config.auto_recovery_enabled,
                "escalation_auto_trigger": self.config.escalation_auto_trigger,
                "comprehensive_reporting": self.config.comprehensive_reporting,
                "max_concurrent_monitors": self.config.max_concurrent_monitors
            }
        }
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """包括的レポートを取得"""
        return {
            "system_status": self.get_system_status(),
            "recent_verifications": self.monitor.get_verification_results()[-10:],
            "recent_escalations": self.monitor.get_escalation_events(resolved=False),
            "active_recoveries": self.recovery.get_active_recoveries(),
            "recent_recovery_history": self.recovery.get_recovery_history(10)
        }