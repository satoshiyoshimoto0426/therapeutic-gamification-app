# ロールバック実行エンジン統合システム

このディレクトリには、自動デプロイメントシステムのロールバック実行エンジンの統合システムが含まれています。このシステムは、トリガーシステムと実行エンジンを統合し、包括的な自動ロールバック機能を提供します。

## 概要

ロールバック実行エンジンの統合システムは以下のコンポーネントで構成されています：

- **RollbackManager**: 統合管理システム
- **RollbackExecutor**: ロールバック実行エンジン
- **RollbackTriggers**: 自動・手動トリガーシステム
- **FailureDetector**: 障害検出システム

## 主要機能

### 1. 統合管理システム (RollbackManager)

- 全コンポーネントの統合管理
- 自動・手動ロールバックの統一インターフェース
- システム状態監視とヘルスチェック
- 統計情報の収集と報告

### 2. ロールバック実行エンジン (RollbackExecutor)

- 複数のロールバック戦略をサポート：
  - **即座ロールバック**: 全トラフィックを即座に切り替え
  - **段階的ロールバック**: トラフィックを段階的に移行
  - **Blue-Greenロールバック**: Blue-Green方式でのロールバック

- ロールバック検証システム：
  - ヘルスチェック検証
  - パフォーマンス検証
  - トラフィック配分検証

### 3. トリガーシステム

#### 自動トリガー (AutomaticRollbackTrigger)
- ヘルスチェック失敗の検出
- パフォーマンス劣化の検出
- エラー率急増の検出
- リソース枯渇の検出

#### 手動トリガー (ManualRollbackTrigger)
- オペレーター主導のロールバック
- 緊急ロールバック
- スケジュールされたロールバック

### 4. 障害検出システム (FailureDetector)

- リアルタイム監視
- 設定可能な閾値
- 複数の障害タイプの検出
- 履歴管理と分析

## 使用方法

### 基本的な使用例

```python
import asyncio
from rollback_manager import RollbackManager, RollbackManagerConfig
from rollback_executor import RollbackConfig, RollbackStrategy

# 設定の作成
config = RollbackManagerConfig(
    service_name="my-service",
    environment="production",
    auto_rollback_enabled=True,
    manual_rollback_enabled=True,
    failure_detection_enabled=True
)

# ロールバック設定
rollback_config = RollbackConfig(
    strategy=RollbackStrategy.GRADUAL,
    verification_timeout_seconds=300,
    gradual_rollback_steps=3
)
config.rollback_config = rollback_config

# 依存関係の準備（実際の実装では適切なインスタンスを使用）
traffic_manager = TrafficManager()
revision_manager = RevisionManager()
health_check_manager = HealthCheckFramework()
performance_monitor = PerformanceMonitor()
notification_manager = NotificationManager()

# ロールバックマネージャーの作成
rollback_manager = RollbackManager(
    traffic_manager=traffic_manager,
    revision_manager=revision_manager,
    health_check_manager=health_check_manager,
    performance_monitor=performance_monitor,
    notification_manager=notification_manager,
    config=config
)

async def main():
    # システム開始
    await rollback_manager.start()
    
    try:
        # 手動ロールバックの実行
        rollback_id = await rollback_manager.trigger_manual_rollback(
            reason="パフォーマンス問題のため",
            operator_id="admin-user",
            severity="warning"
        )
        
        print(f"ロールバック開始: {rollback_id}")
        
        # システム状態の確認
        status = rollback_manager.get_status()
        print(f"システム状態: {status['status']}")
        print(f"統計情報: {status['statistics']}")
        
        # 最近のロールバック履歴
        recent_rollbacks = rollback_manager.get_recent_rollbacks(10)
        for rollback in recent_rollbacks:
            print(f"ロールバック: {rollback.rollback_id} - {rollback.status.value}")
        
    finally:
        # システム停止
        await rollback_manager.stop()

# 実行
asyncio.run(main())
```

### 設定オプション

#### RollbackManagerConfig

```python
config = RollbackManagerConfig(
    # サービス設定
    service_name="my-service",
    environment="production",
    
    # 機能の有効/無効
    auto_rollback_enabled=True,
    manual_rollback_enabled=True,
    failure_detection_enabled=True,
    notification_enabled=True,
    
    # 監視間隔
    monitoring_interval_seconds=30,
    health_check_interval_seconds=60
)
```

#### RollbackConfig

```python
rollback_config = RollbackConfig(
    # ロールバック戦略
    strategy=RollbackStrategy.GRADUAL,
    
    # タイムアウト設定
    verification_timeout_seconds=300,
    health_check_timeout_seconds=120,
    
    # 段階的ロールバック設定
    gradual_rollback_steps=3,
    gradual_rollback_interval_seconds=60,
    
    # リトライ設定
    max_retry_attempts=3,
    
    # 通知設定
    notification_enabled=True
)
```

#### RollbackTriggerConfig

```python
trigger_config = RollbackTriggerConfig(
    enabled=True,
    cooldown_minutes=10,
    max_rollbacks_per_hour=3,
    require_confirmation=False,
    notification_channels=["slack", "email"]
)
```

## ロールバック戦略

### 1. 即座ロールバック (IMMEDIATE)

全トラフィックを即座に前のリビジョンに切り替えます。

- **利点**: 最も高速
- **欠点**: 急激な変化によるリスク
- **適用場面**: 緊急時、小規模サービス

### 2. 段階的ロールバック (GRADUAL)

トラフィックを段階的に前のリビジョンに移行します。

- **利点**: リスクを最小化
- **欠点**: 時間がかかる
- **適用場面**: 大規模サービス、慎重な運用

### 3. Blue-Greenロールバック (BLUE_GREEN)

Blue-Green方式でロールバックを実行します。

- **利点**: 確実な切り替え
- **欠点**: リソースが必要
- **適用場面**: 高可用性が必要なサービス

## 監視と通知

### システム状態の監視

```python
# システム状態の取得
status = rollback_manager.get_status()

print(f"ステータス: {status['status']}")
print(f"稼働時間: {status['uptime_seconds']}秒")
print(f"総ロールバック数: {status['statistics']['total_rollbacks']}")
print(f"成功率: {status['statistics']['success_rate']:.1f}%")

# コンポーネント状態
components = status['components']
print(f"障害検出: {'アクティブ' if components['failure_detector']['active'] else '非アクティブ'}")
print(f"自動トリガー: {'アクティブ' if components['automatic_trigger']['active'] else '非アクティブ'}")
```

### 履歴の確認

```python
# 最近のロールバック履歴
recent_rollbacks = rollback_manager.get_recent_rollbacks(20)
for rollback in recent_rollbacks:
    print(f"{rollback.rollback_id}: {rollback.status.value} - {rollback.target.target_revision}")

# アクティブなロールバック
active_rollbacks = rollback_manager.get_active_rollbacks()
print(f"アクティブなロールバック: {len(active_rollbacks)}件")

# 最近の障害
recent_failures = rollback_manager.get_recent_failures(30)
print(f"最近30分の障害: {len(recent_failures)}件")
```

## テスト

### 単体テスト

```bash
# 全テストの実行
python -m pytest services/auto-deployment/rollback/tests/ -v

# 統合テストのみ
python -m pytest services/auto-deployment/rollback/tests/test_rollback_integration.py -v

# 完了検証テスト
python -m pytest services/auto-deployment/rollback/tests/test_task_7_2_completion.py -v
```

### デモンストレーション

```bash
# デモスクリプトの実行
python services/auto-deployment/rollback/rollback_integration_demo.py
```

## エラーハンドリング

システムは以下のエラー状況を適切に処理します：

- **トラフィック切り替え失敗**: 自動リトライとエラー通知
- **ヘルスチェック失敗**: 検証タイムアウトと代替手順
- **リビジョン取得失敗**: グレースフルな劣化
- **通知送信失敗**: ログ記録と継続動作

## ログ

システムは詳細なログを出力します：

```python
import logging

# ログレベルの設定
logging.basicConfig(level=logging.INFO)

# ロールバック関連のログを確認
logger = logging.getLogger('rollback')
```

## セキュリティ

- 認証されたオペレーターのみが手動ロールバックを実行可能
- 全ロールバック操作は監査ログに記録
- 設定可能なレート制限とクールダウン期間
- 確認が必要な操作の設定可能

## パフォーマンス

- 非同期処理による高いスループット
- メモリ効率的な履歴管理
- 設定可能な監視間隔
- リソース使用量の最適化

## トラブルシューティング

### よくある問題

1. **ロールバックが開始されない**
   - クールダウン期間を確認
   - レート制限を確認
   - システム状態を確認

2. **検証が失敗する**
   - ヘルスチェック設定を確認
   - パフォーマンス閾値を確認
   - ネットワーク接続を確認

3. **通知が送信されない**
   - 通知設定を確認
   - 認証情報を確認
   - ネットワーク接続を確認

### デバッグ

```python
# デバッグログの有効化
import logging
logging.getLogger('rollback').setLevel(logging.DEBUG)

# システム状態の詳細確認
status = rollback_manager.get_status()
print(json.dumps(status, indent=2, default=str))
```

## 拡張

システムは以下の拡張が可能です：

- カスタム障害検出アルゴリズム
- 追加のロールバック戦略
- カスタム通知チャネル
- 外部監視システムとの統合

## ライセンス

このプロジェクトのライセンスに従います。

## 貢献

バグ報告や機能要求は、プロジェクトのIssueトラッカーまでお願いします。