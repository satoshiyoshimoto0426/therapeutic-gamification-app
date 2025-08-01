# 季節イベントとコミュニティ機能サービス

## 概要

このサービスは、治療的ゲーミフィケーションアプリケーションにおけるゲーム性強化とエンゲージメント機能を提供します。長期的なユーザーエンゲージメントを維持し、コミュニティベースの治療的支援を実現します。

## 主要機能

### 1. 季節イベントシステム
- **春の再生祭**: 新しい習慣形成と希望の育成
- **夏のエネルギー祭**: 活動的な行動と社会参加の促進
- **秋の振り返り祭**: 成長の振り返りと感謝の気持ち育成
- **冬の温もり祭**: コミュニティのつながりと支え合い

### 2. ギルドシステム（ピアサポート）
- **治療的焦点別ギルド**: ADHD支援、不安サポート、社会復帰支援
- **ギルドレベルシステム**: 協力によるレベルアップ
- **リーダーシップ機能**: ギルドリーダーの責任と権限
- **メンバー管理**: 参加・脱退・権限管理

### 3. コミュニティ目標システム
- **協力型チャレンジ**: 全体で達成する大きな目標
- **進行状況の可視化**: リアルタイムでの進捗確認
- **報酬システム**: 参加者全員への報酬配布
- **期間限定目標**: 時間制限のあるチャレンジ

## プレステージシステムと長期エンゲージメント

### プレステージシステム
- **7段階のプレステージレベル**: Novice → Apprentice → Journeyman → Expert → Master → Grandmaster → Legend
- **治療マイルストーン**: 8つの治療的成長段階（最初の一歩、習慣形成、社会復帰、感情安定、自己効力感、ピアサポート、メンターシップ、生活統合）
- **プレステージポイント**: マイルストーン達成によるポイント獲得システム

### 分岐ストーリーシステム
- **治療テーマ別ストーリー**: 各マイルストーンに対応した分岐ストーリー
- **段階的アンロック**: 進捗に応じたストーリー分岐の解放
- **治療的意味**: 各ストーリーが持つ治療的価値と成長メッセージ

### コスメティックシステム
- **4つのカテゴリ**: アバター、背景、称号、バッジ
- **4つのレアリティ**: Common、Rare、Epic、Legendary
- **治療的意味**: 各アイテムが持つ治療的メッセージ
- **装備システム**: アンロックしたアイテムの装備・カスタマイズ

## アーキテクチャ

```
EngagementSystem
├── SeasonalEventSystem     # 季節イベント管理
├── GuildSystem            # ギルド管理
└── CommunityGoalSystem    # コミュニティ目標管理

LongTermEngagementSystem
├── StoryBranchSystem      # 分岐ストーリー管理
├── CosmeticSystem         # コスメティック管理
└── PrestigeSystem         # プレステージ管理
```

## 使用例

### 基本的な使用方法

```python
from services.seasonal_events.main import EngagementSystem

# システムの初期化
engagement = EngagementSystem()

# 季節イベントの作成
spring_event = engagement.seasonal_events.create_seasonal_event("spring_renewal")

# ギルドの作成
guild = engagement.guild_system.create_guild(
    leader_uid="user_001",
    name="ADHD支援ギルド",
    description="ADHD当事者同士で支え合うギルド",
    therapeutic_focus="adhd_peer"
)

# コミュニティ目標の作成
community_goal = engagement.community_goals.create_community_goal(
    title="みんなで1000タスク達成",
    description="コミュニティ全体で1000個のタスクを完了しよう",
    target_value=1000,
    duration_days=30,
    reward_per_participant={"xp": 100, "coins": 50}
)

# ユーザーアクションの処理
engagement.process_user_action("user_001", "task_completed", 5)

# エンゲージメントデータの取得
engagement_data = engagement.get_user_engagement_data("user_001")
```

### プレステージシステムの使用方法

```python
from services.seasonal_events.prestige_system import LongTermEngagementSystem

# システムの初期化
long_term = LongTermEngagementSystem()

# プレステージプロファイルの作成
profile = long_term.create_prestige_profile("user_001")

# ユーザー進捗の更新
progress_data = {
    "tasks_completed": 50,
    "habit_streak": 30,
    "social_interactions": 25,
    "mood_stability_days": 20
}

updates = long_term.update_user_progress("user_001", progress_data)

# エンゲージメント概要の取得
summary = long_term.get_user_engagement_summary("user_001")

# コスメティックの装備
if summary["cosmetic_collection_size"] > 0:
    # 利用可能なアイテムを装備
    long_term.equip_cosmetic("user_001", "title_first_steps")
```

## テスト

### 単体テスト
```bash
# 季節イベント・コミュニティ機能
python -m pytest services/seasonal_events/test_seasonal_events.py -v

# プレステージシステム
python -m pytest services/seasonal_events/test_prestige_system.py -v
```

### 統合テスト
```bash
# コミュニティ機能統合テスト
python -m pytest services/seasonal_events/test_community_integration.py -v

# 長期エンゲージメント統合テスト
python -m pytest services/seasonal_events/test_long_term_engagement_integration.py -v
```

### 完全ワークフローテスト
```bash
# コミュニティ機能ワークフロー
python services/seasonal_events/test_community_integration.py

# プレステージシステムワークフロー
python services/seasonal_events/test_prestige_system.py

# 長期エンゲージメントワークフロー
python services/seasonal_events/test_long_term_engagement_integration.py
```

## 治療的配慮

### 1. 心理的安全性
- **非競争的環境**: 個人の成長を重視し、他者との比較を避ける
- **支援的コミュニティ**: ピアサポートによる相互支援
- **失敗への寛容**: 挫折を成長の機会として捉える

### 2. ADHD配慮
- **明確な目標設定**: 具体的で達成可能な目標
- **進捗の可視化**: リアルタイムでの進捗確認
- **適度な刺激**: 過度な刺激を避けた設計

### 3. 社会復帰支援
- **段階的な社会参加**: 小さなステップから始める
- **安全な練習環境**: リスクの少ない社会的交流
- **成功体験の積み重ね**: 自信の構築

### 4. 長期エンゲージメント
- **治療マイルストーン**: 治療的成長に基づく進捗評価
- **意味のある報酬**: 治療的価値を持つコスメティックアイテム
- **個人の物語**: 分岐ストーリーによる個別化された体験

## パフォーマンス考慮事項

### 1. スケーラビリティ
- **効率的なデータ構造**: 大量のユーザーとギルドに対応
- **キャッシュ戦略**: 頻繁にアクセスされるデータのキャッシュ
- **非同期処理**: 重い処理の非同期実行

### 2. データ整合性
- **トランザクション管理**: データの一貫性保証
- **競合状態の回避**: 同時アクセス時の整合性
- **エラーハンドリング**: 例外状況への適切な対応

## 今後の拡張予定

### 1. 高度なマッチング
- **興味・関心ベースのマッチング**: より適切なギルド推薦
- **治療進度に基づくグループ分け**: 同じレベルのユーザー同士の交流

### 2. AI支援機能
- **パーソナライズされたイベント**: 個人の状況に応じたイベント提案
- **自動的なサポート**: AIによる適切なタイミングでの介入

### 3. 外部連携
- **治療者ポータル**: 専門家による監督とサポート
- **家族・支援者連携**: 周囲のサポートネットワークとの統合

## 要件対応

このサービスは以下の要件に対応しています：

- **要件14.1**: 季節イベント、期間限定チャレンジ、コミュニティ目標
- **要件14.2**: 分岐ストーリーラインと治療マイルストーン連携
- **要件14.3**: オプションのギルドシステム（ピアサポート）、協力機能
- **要件14.4**: コスメティックカスタマイゼーション機能
- **要件14.5**: プレステージシステムとレガシー機能

## 関連サービス

- `services/core-game/`: XPとレベル管理
- `services/task-mgmt/`: タスク管理システム
- `services/mood-tracking/`: 気分追跡システム
- `services/therapeutic-safety/`: 治療安全性チェック