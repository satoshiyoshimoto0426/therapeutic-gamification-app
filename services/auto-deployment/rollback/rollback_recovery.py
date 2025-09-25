"""
ロールバック復旧システム

このモジュールは、ロールバック失敗時の復旧手順、
緊急時対応、システム復旧を提供します。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from .rollback_executor import RollbackResult, RollbackStatus
    from .rollback_monitor import EscalationEvent, EscalationLevel
    from ..deployment.cloud_run.traffic_manager import TrafficManager
    from ..deployment.cloud_run.revision_manager import RevisionManager
    from ..monitoring.health_check import HealthCheckFramework
    from ..notification.notification_manager import NotificationManager
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_executor import RollbackResult, RollbackStatus
    from rollback.rollback_monitor import EscalationEvent, EscalationLevel
    from deployment.cloud_run.traffic_manager import TrafficManager
    from deployment.cloud_run.revision_manager import RevisionManager
    from monitoring.health_check import HealthCheckFramework
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class RecoveryStatus(Enum):
    """復旧ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecoveryStrategy(Enum):
    """復旧戦略"""
    EMERGENCY_ROLLBACK = "emergency_rollback"  # 緊急ロールバック
    TRAFFIC_ISOLATION = "traffic_isolation"   # トラフィック分離
    SERVICE_RESTART = "service_restart"       # サービス再起動
    MANUAL_INTERVENTION = "manual_intervention"  # 手動介入
    SYSTEM_MAINTENANCE = "system_maintenance"    # システムメンテナンス


@dataclass
class RecoveryConfig:
    """復旧設定"""
    # 復旧タイムアウト
    emergency_recovery_timeout_minutes: int = 15
    standard_recovery_timeout_minutes: int = 60
    
    # 復旧戦略設定
    auto_emergency_rollback: bool = True
    auto_traffic_isolation: bool = True
    auto_service_restart: bool = False
    
    # 通知設定
    immediate_notification: bool = True
    escalation_notification: bool = True
    recovery_completion_notification: bool = True
    
    # 復旧試行設定
    max_recovery_attempts: int = 3
    recovery_retry_interval_seconds: int = 300


@dataclass
class RecoveryAction:
    """復旧アクション"""
    action_id: str
    strategy: RecoveryStrategy
    description: str
    timestamp: datetime
    success: bool = False
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


@dataclass
class RecoveryPlan:
    """復旧計画"""
    plan_id: str
    rollback_id: str
    escalation_level: EscalationLevel
    strategies: List[RecoveryStrategy]
    created_time: datetime
    estimated_duration_minutes: int
    priority: int = 1  # 1が最高優先度


@dataclass
class RecoveryResult:
    """復旧結果"""
    recovery_id: str
    rollback_id: str
    status: RecoveryStatus
    plan: RecoveryPlan
    actions_taken: List[RecoveryAction] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    success: bool = False
    final_message: Optional[str] = None


class RollbackRecovery:
    """
    ロールバック復旧システム
    
    ロールバック失敗時の自動復旧、緊急時対応、
    システム復旧手順を提供します。
    """
    
    def __init__(self,
                 traffic_manager: TrafficManager,
                 revision_manager: RevisionManager,
                 health_check_manager: HealthCheckFramework,
                 notification_manager: NotificationManager,
                 config: Optional[RecoveryConfig] = None):
        """
        ロールバック復旧システムを初期化
        
        Args:
            traffic_manager: トラフィック管理システム
            revision_manager: リビジョン管理システム
            health_check_manager: ヘルスチェック管理システム
            notification_manager: 通知管理システム
            config: 復旧設定
        """
        self.traffic_manager = traffic_manager
        self.revision_manager = revision_manager
        self.health_check_manager = health_check_manager
        self.notification_manager = notification_manager
        self.config = config or RecoveryConfig()
        self.logger = logging.getLogger(__name__)
        
        # 復旧状態管理
        self.active_recoveries: Dict[str, RecoveryResult] = {}
        self.recovery_history: List[RecoveryResult] = []
        
        # 復旧戦略マッピング
        self.strategy_handlers = {
            RecoveryStrategy.EMERGENCY_ROLLBACK: self._execute_emergency_rollback,
            RecoveryStrategy.TRAFFIC_ISOLATION: self._execute_traffic_isolation,
            RecoveryStrategy.SERVICE_RESTART: self._execute_service_restart,
            RecoveryStrategy.MANUAL_INTERVENTION: self._execute_manual_intervention,
            RecoveryStrategy.SYSTEM_MAINTENANCE: self._execute_system_maintenance
        }
        
        # コールバック
        self._callbacks: Dict[str, List[Callable]] = {
            'recovery_started': [],
            'recovery_progress': [],
            'recovery_completed': [],
            'recovery_failed': [],
            'manual_intervention_required': []
        }
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """イベントコールバックを追加"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def initiate_recovery(self, rollback_result: RollbackResult, escalation_event: EscalationEvent) -> str:
        """
        復旧プロセスを開始
        
        Args:
            rollback_result: 失敗したロールバック結果
            escalation_event: エスカレーションイベント
            
        Returns:
            復旧ID
        """
        recovery_id = f"recovery_{rollback_result.rollback_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"復旧プロセスを開始: {recovery_id}")
            
            # 復旧計画を作成
            recovery_plan = await self._create_recovery_plan(rollback_result, escalation_event)
            
            # 復旧結果を初期化
            recovery_result = RecoveryResult(
                recovery_id=recovery_id,
                rollback_id=rollback_result.rollback_id,
                status=RecoveryStatus.PENDING,
                plan=recovery_plan
            )
            
            self.active_recoveries[recovery_id] = recovery_result
            
            # 復旧開始通知
            await self._notify_callbacks('recovery_started', recovery_result)
            
            if self.config.immediate_notification:
                await self._send_recovery_notification("開始", recovery_result)
            
            # 復旧実行タスクを開始
            asyncio.create_task(self._execute_recovery(recovery_result))
            
            return recovery_id
        
        except Exception as e:
            self.logger.error(f"復旧プロセスの開始に失敗: {recovery_id} - {e}")
            raise RollbackError(f"復旧プロセスの開始に失敗: {e}")
    
    async def _create_recovery_plan(self, rollback_result: RollbackResult, escalation_event: EscalationEvent) -> RecoveryPlan:
        """復旧計画を作成"""
        plan_id = f"plan_{rollback_result.rollback_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # エスカレーションレベルに基づいて復旧戦略を決定
        strategies = []
        estimated_duration = 0
        priority = 1
        
        if escalation_event.level == EscalationLevel.CRITICAL:
            # 緊急時は即座に対応
            if self.config.auto_emergency_rollback:
                strategies.append(RecoveryStrategy.EMERGENCY_ROLLBACK)
                estimated_duration += 5
            
            if self.config.auto_traffic_isolation:
                strategies.append(RecoveryStrategy.TRAFFIC_ISOLATION)
                estimated_duration += 3
            
            strategies.append(RecoveryStrategy.MANUAL_INTERVENTION)
            estimated_duration += 15
            priority = 1
        
        elif escalation_event.level == EscalationLevel.HIGH:
            # 高レベルは段階的対応
            if self.config.auto_emergency_rollback:
                strategies.append(RecoveryStrategy.EMERGENCY_ROLLBACK)
                estimated_duration += 10
            
            if self.config.auto_service_restart:
                strategies.append(RecoveryStrategy.SERVICE_RESTART)
                estimated_duration += 15
            
            strategies.append(RecoveryStrategy.MANUAL_INTERVENTION)
            estimated_duration += 30
            priority = 2
        
        elif escalation_event.level == EscalationLevel.MEDIUM:
            # 中レベルは慎重な対応
            if self.config.auto_traffic_isolation:
                strategies.append(RecoveryStrategy.TRAFFIC_ISOLATION)
                estimated_duration += 10
            
            if self.config.auto_service_restart:
                strategies.append(RecoveryStrategy.SERVICE_RESTART)
                estimated_duration += 20
            
            strategies.append(RecoveryStrategy.MANUAL_INTERVENTION)
            estimated_duration += 45
            priority = 3
        
        else:  # LOW
            # 低レベルは監視重視
            strategies.append(RecoveryStrategy.MANUAL_INTERVENTION)
            estimated_duration += 60
            priority = 4
        
        return RecoveryPlan(
            plan_id=plan_id,
            rollback_id=rollback_result.rollback_id,
            escalation_level=escalation_event.level,
            strategies=strategies,
            created_time=datetime.now(),
            estimated_duration_minutes=estimated_duration,
            priority=priority
        )
    
    async def _execute_recovery(self, recovery_result: RecoveryResult) -> None:
        """復旧を実行"""
        recovery_id = recovery_result.recovery_id
        
        try:
            recovery_result.status = RecoveryStatus.IN_PROGRESS
            self.logger.info(f"復旧実行を開始: {recovery_id}")
            
            # 復旧戦略を順次実行
            for strategy in recovery_result.plan.strategies:
                action_success = await self._execute_recovery_strategy(recovery_result, strategy)
                
                if action_success:
                    # 戦略が成功した場合、復旧完了をチェック
                    if await self._verify_recovery_success(recovery_result):
                        recovery_result.status = RecoveryStatus.COMPLETED
                        recovery_result.success = True
                        recovery_result.end_time = datetime.now()
                        recovery_result.final_message = f"復旧が成功しました (戦略: {strategy.value})"
                        
                        self.logger.info(f"復旧が成功しました: {recovery_id}")
                        await self._notify_callbacks('recovery_completed', recovery_result)
                        
                        if self.config.recovery_completion_notification:
                            await self._send_recovery_notification("完了", recovery_result)
                        
                        return
                else:
                    # 戦略が失敗した場合、次の戦略に進む
                    self.logger.warning(f"復旧戦略が失敗しました: {strategy.value} - {recovery_id}")
                    continue
            
            # すべての戦略が失敗した場合
            recovery_result.status = RecoveryStatus.FAILED
            recovery_result.end_time = datetime.now()
            recovery_result.final_message = "すべての復旧戦略が失敗しました"
            
            self.logger.error(f"復旧が失敗しました: {recovery_id}")
            await self._notify_callbacks('recovery_failed', recovery_result)
            
            if self.config.escalation_notification:
                await self._send_recovery_notification("失敗", recovery_result)
        
        except Exception as e:
            recovery_result.status = RecoveryStatus.FAILED
            recovery_result.end_time = datetime.now()
            recovery_result.final_message = f"復旧実行中にエラーが発生: {e}"
            
            self.logger.error(f"復旧実行中にエラーが発生: {recovery_id} - {e}")
            await self._notify_callbacks('recovery_failed', recovery_result)
        
        finally:
            # アクティブな復旧から履歴に移動
            if recovery_id in self.active_recoveries:
                del self.active_recoveries[recovery_id]
            self.recovery_history.append(recovery_result)
            
            # 履歴のサイズ制限
            if len(self.recovery_history) > 100:
                self.recovery_history = self.recovery_history[-100:]
    
    async def _execute_recovery_strategy(self, recovery_result: RecoveryResult, strategy: RecoveryStrategy) -> bool:
        """復旧戦略を実行"""
        action_id = f"action_{strategy.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        action = RecoveryAction(
            action_id=action_id,
            strategy=strategy,
            description=f"{strategy.value}を実行中",
            timestamp=datetime.now()
        )
        
        recovery_result.actions_taken.append(action)
        
        try:
            self.logger.info(f"復旧戦略を実行: {strategy.value} - {recovery_result.recovery_id}")
            
            start_time = datetime.now()
            
            # 戦略ハンドラーを実行
            handler = self.strategy_handlers.get(strategy)
            if handler:
                success = await handler(recovery_result, action)
            else:
                self.logger.error(f"未知の復旧戦略: {strategy.value}")
                success = False
            
            end_time = datetime.now()
            action.duration_seconds = (end_time - start_time).total_seconds()
            action.success = success
            
            if success:
                action.description = f"{strategy.value}が成功しました"
                self.logger.info(f"復旧戦略が成功: {strategy.value} - {recovery_result.recovery_id}")
            else:
                action.description = f"{strategy.value}が失敗しました"
                self.logger.warning(f"復旧戦略が失敗: {strategy.value} - {recovery_result.recovery_id}")
            
            # 進捗通知
            await self._notify_callbacks('recovery_progress', recovery_result)
            
            return success
        
        except Exception as e:
            action.success = False
            action.error_message = str(e)
            action.description = f"{strategy.value}でエラーが発生: {e}"
            
            self.logger.error(f"復旧戦略実行中にエラー: {strategy.value} - {recovery_result.recovery_id} - {e}")
            return False
    
    async def _execute_emergency_rollback(self, recovery_result: RecoveryResult, action: RecoveryAction) -> bool:
        """緊急ロールバックを実行"""
        try:
            # 最後の安定したリビジョンを取得
            stable_revisions = await self.revision_manager.get_revision_history(
                service_name=recovery_result.rollback_id.split('_')[1],  # サービス名を抽出
                limit=5
            )
            
            if not stable_revisions:
                action.error_message = "安定したリビジョンが見つかりません"
                return False
            
            # 最も古い安定リビジョンを選択
            target_revision = stable_revisions[-1].name
            
            # 緊急トラフィック切り替え
            traffic_result = self.traffic_manager.emergency_traffic_switch(
                service_name=recovery_result.rollback_id.split('_')[1],
                target_revision=target_revision
            )
            
            if traffic_result.success:
                action.description += f" - リビジョン {target_revision} に緊急切り替え完了"
                return True
            else:
                action.error_message = f"緊急トラフィック切り替えに失敗: {traffic_result.error_message}"
                return False
        
        except Exception as e:
            action.error_message = f"緊急ロールバック実行中にエラー: {e}"
            return False
    
    async def _execute_traffic_isolation(self, recovery_result: RecoveryResult, action: RecoveryAction) -> bool:
        """トラフィック分離を実行"""
        try:
            # 問題のあるリビジョンからトラフィックを完全に分離
            service_name = recovery_result.rollback_id.split('_')[1]
            
            # 現在のトラフィック配分を取得
            current_traffic = self.traffic_manager.get_current_traffic(service_name)
            
            if not current_traffic:
                action.error_message = "現在のトラフィック情報を取得できません"
                return False
            
            # 問題のあるリビジョンを特定（最新のリビジョンと仮定）
            problem_revision = max(current_traffic.keys(), key=lambda x: current_traffic[x])
            
            # トラフィックを他のリビジョンに分散
            remaining_revisions = {k: v for k, v in current_traffic.items() if k != problem_revision}
            
            if not remaining_revisions:
                action.error_message = "トラフィックを分散できる他のリビジョンがありません"
                return False
            
            # トラフィックを均等に分散
            total_remaining = sum(remaining_revisions.values())
            if total_remaining > 0:
                # 既存の比率を維持しながら100%に調整
                from ..deployment.cloud_run.traffic_manager import TrafficSplit
                traffic_splits = []
                
                for revision, current_percentage in remaining_revisions.items():
                    new_percentage = int((current_percentage / total_remaining) * 100)
                    if new_percentage > 0:
                        traffic_splits.append(TrafficSplit(
                            revision_name=revision,
                            percentage=new_percentage,
                            tag="isolated"
                        ))
                
                # トラフィック更新
                traffic_result = self.traffic_manager.update_traffic(
                    service_name=service_name,
                    traffic_splits=traffic_splits
                )
                
                if traffic_result.success:
                    action.description += f" - リビジョン {problem_revision} からトラフィックを分離完了"
                    return True
                else:
                    action.error_message = f"トラフィック分離に失敗: {traffic_result.error_message}"
                    return False
            else:
                action.error_message = "有効な代替リビジョンがありません"
                return False
        
        except Exception as e:
            action.error_message = f"トラフィック分離実行中にエラー: {e}"
            return False
    
    async def _execute_service_restart(self, recovery_result: RecoveryResult, action: RecoveryAction) -> bool:
        """サービス再起動を実行"""
        try:
            service_name = recovery_result.rollback_id.split('_')[1]
            
            # サービスの現在のリビジョンを取得
            current_revision = await self.revision_manager.get_current_revision(service_name)
            
            if not current_revision:
                action.error_message = "現在のリビジョン情報を取得できません"
                return False
            
            # リビジョンの再起動（実際の実装では Cloud Run API を使用）
            # ここでは簡略化した実装
            restart_result = await self._restart_revision(service_name, current_revision)
            
            if restart_result:
                action.description += f" - リビジョン {current_revision} の再起動完了"
                
                # 再起動後のヘルスチェック
                await asyncio.sleep(30)  # 起動待機
                
                health_results = await self.health_check_manager.run_health_checks()
                if health_results and all(result.success for result in health_results):
                    action.description += " - 再起動後のヘルスチェック正常"
                    return True
                else:
                    action.error_message = "再起動後のヘルスチェックに失敗"
                    return False
            else:
                action.error_message = "サービス再起動に失敗"
                return False
        
        except Exception as e:
            action.error_message = f"サービス再起動実行中にエラー: {e}"
            return False
    
    async def _restart_revision(self, service_name: str, revision_name: str) -> bool:
        """リビジョンを再起動（簡略化実装）"""
        try:
            # 実際の実装では Cloud Run API を使用してリビジョンを再起動
            # ここでは成功を仮定
            await asyncio.sleep(5)  # 再起動シミュレーション
            return True
        except Exception:
            return False
    
    async def _execute_manual_intervention(self, recovery_result: RecoveryResult, action: RecoveryAction) -> bool:
        """手動介入を要求"""
        try:
            # 手動介入要求の通知
            await self._notify_callbacks('manual_intervention_required', recovery_result)
            
            intervention_message = f"""
🚨 手動介入が必要です

復旧ID: {recovery_result.recovery_id}
ロールバックID: {recovery_result.rollback_id}
エスカレーションレベル: {recovery_result.plan.escalation_level.value}

実行済みアクション:
{chr(10).join([f"- {a.description}" for a in recovery_result.actions_taken[:-1]])}

推奨される手動対応:
1. サービスログの詳細確認
2. インフラストラクチャの状態確認
3. 必要に応じてメンテナンスモードへの切り替え
4. 根本原因の調査と修正

緊急連絡先: [運用チーム]
            """
            
            await self.notification_manager.send_notification(
                channel="emergency",
                message=intervention_message,
                severity="critical"
            )
            
            action.description += " - 手動介入要求を送信しました"
            
            # 手動介入は常に「成功」とみなす（通知が送信されたため）
            return True
        
        except Exception as e:
            action.error_message = f"手動介入要求中にエラー: {e}"
            return False
    
    async def _execute_system_maintenance(self, recovery_result: RecoveryResult, action: RecoveryAction) -> bool:
        """システムメンテナンスモードを実行"""
        try:
            service_name = recovery_result.rollback_id.split('_')[1]
            
            # メンテナンスページへのトラフィック切り替え
            maintenance_result = await self._switch_to_maintenance_mode(service_name)
            
            if maintenance_result:
                action.description += " - メンテナンスモードに切り替え完了"
                
                # メンテナンス通知
                maintenance_message = f"""
🔧 システムメンテナンス開始

サービス: {service_name}
開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
理由: ロールバック復旧のため

ユーザーにはメンテナンスページが表示されます。
復旧完了後、通常運用に戻します。
                """
                
                await self.notification_manager.send_notification(
                    channel="maintenance",
                    message=maintenance_message,
                    severity="warning"
                )
                
                return True
            else:
                action.error_message = "メンテナンスモードへの切り替えに失敗"
                return False
        
        except Exception as e:
            action.error_message = f"システムメンテナンス実行中にエラー: {e}"
            return False
    
    async def _switch_to_maintenance_mode(self, service_name: str) -> bool:
        """メンテナンスモードに切り替え（簡略化実装）"""
        try:
            # 実際の実装では、メンテナンスページを提供するリビジョンに
            # トラフィックを切り替える
            await asyncio.sleep(3)  # 切り替えシミュレーション
            return True
        except Exception:
            return False
    
    async def _verify_recovery_success(self, recovery_result: RecoveryResult) -> bool:
        """復旧成功を検証"""
        try:
            # ヘルスチェックによる検証
            health_results = await self.health_check_manager.run_health_checks()
            
            if not health_results:
                self.logger.warning("ヘルスチェック結果が取得できません")
                return False
            
            # すべてのヘルスチェックが成功している必要がある
            all_healthy = all(result.success for result in health_results)
            
            if all_healthy:
                self.logger.info(f"復旧成功を確認: {recovery_result.recovery_id}")
                return True
            else:
                failed_checks = [r.endpoint for r in health_results if not r.success]
                self.logger.warning(f"復旧検証失敗 - 失敗したヘルスチェック: {failed_checks}")
                return False
        
        except Exception as e:
            self.logger.error(f"復旧成功検証中にエラー: {recovery_result.recovery_id} - {e}")
            return False
    
    async def _send_recovery_notification(self, status: str, recovery_result: RecoveryResult) -> None:
        """復旧通知を送信"""
        try:
            message = f"復旧{status}: {recovery_result.recovery_id}\n"
            message += f"ロールバックID: {recovery_result.rollback_id}\n"
            message += f"ステータス: {recovery_result.status.value}\n"
            
            if recovery_result.final_message:
                message += f"メッセージ: {recovery_result.final_message}\n"
            
            if recovery_result.actions_taken:
                message += f"実行されたアクション: {len(recovery_result.actions_taken)}件\n"
            
            severity = "info" if recovery_result.success else "error"
            
            await self.notification_manager.send_notification(
                channel="recovery",
                message=message,
                severity=severity
            )
        
        except Exception as e:
            self.logger.error(f"復旧通知送信中にエラー: {e}")
    
    async def _notify_callbacks(self, event: str, data: Any) -> None:
        """コールバックに通知"""
        for callback in self._callbacks.get(event, []):
            try:
                await callback(data)
            except Exception as e:
                self.logger.error(f"復旧コールバック実行中にエラー: {e}")
    
    # パブリックAPI
    
    def get_recovery_status(self, recovery_id: str) -> Optional[RecoveryResult]:
        """復旧ステータスを取得"""
        # アクティブな復旧をチェック
        if recovery_id in self.active_recoveries:
            return self.active_recoveries[recovery_id]
        
        # 履歴をチェック
        for result in self.recovery_history:
            if result.recovery_id == recovery_id:
                return result
        
        return None
    
    def get_active_recoveries(self) -> List[RecoveryResult]:
        """アクティブな復旧を取得"""
        return list(self.active_recoveries.values())
    
    def get_recovery_history(self, limit: int = 50) -> List[RecoveryResult]:
        """復旧履歴を取得"""
        return self.recovery_history[-limit:] if limit > 0 else self.recovery_history
    
    async def cancel_recovery(self, recovery_id: str, reason: str) -> bool:
        """復旧をキャンセル"""
        if recovery_id not in self.active_recoveries:
            self.logger.warning(f"アクティブな復旧が見つかりません: {recovery_id}")
            return False
        
        try:
            recovery_result = self.active_recoveries[recovery_id]
            recovery_result.status = RecoveryStatus.CANCELLED
            recovery_result.end_time = datetime.now()
            recovery_result.final_message = f"復旧がキャンセルされました: {reason}"
            
            # 履歴に移動
            del self.active_recoveries[recovery_id]
            self.recovery_history.append(recovery_result)
            
            self.logger.info(f"復旧がキャンセルされました: {recovery_id} - {reason}")
            
            # キャンセル通知
            if self.config.escalation_notification:
                await self._send_recovery_notification("キャンセル", recovery_result)
            
            return True
        
        except Exception as e:
            self.logger.error(f"復旧キャンセル中にエラー: {recovery_id} - {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        return {
            "active_recoveries": len(self.active_recoveries),
            "total_recoveries": len(self.recovery_history),
            "successful_recoveries": len([r for r in self.recovery_history if r.success]),
            "failed_recoveries": len([r for r in self.recovery_history if not r.success and r.status == RecoveryStatus.FAILED]),
            "config": {
                "auto_emergency_rollback": self.config.auto_emergency_rollback,
                "auto_traffic_isolation": self.config.auto_traffic_isolation,
                "auto_service_restart": self.config.auto_service_restart,
                "max_recovery_attempts": self.config.max_recovery_attempts
            }
        }