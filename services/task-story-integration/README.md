# Task-Story Integration Service

タスク-ストーリー統合サービス（Task 8.3）の実装

## 概要

このサービスは、ストーリー選択肢とreal_task_id/habit_tagの連携、明日のMandalaへの反映機能、タスク完了とストーリー進行の同期を実装します。

## 主要機能

### 1. ストーリー選択肢からタスク作成
- ストーリー選択肢を実世界のタスクに変換
- real_task_idがある場合は既存タスクを更新
- task_templateがある場合はテンプレートからタスク作成
- 選択肢テキストからタスクタイプを推論

### 2. タスク完了とストーリー進行の同期
- タスク完了時にストーリー進行をトリガー
- XP計算とコアゲーム統合
- クリスタル成長イベント処理
- 共鳴イベントチェック
- 次のストーリー選択肢生成

### 3. 明日のMandalaへの反映
- ストーリー選択肢をMandalaセルに反映
- 治療的重みに基づく影響度計算
- 選択肢からタスク生成（明日用）
- セル位置の自動決定

### 4. リアルタイムフック処理
- 21:30のストーリー生成時の処理
- 今日の選択肢から明日のタスク生成
- Mandala反映のスケジューリング

## API エンドポイント

### ストーリー選択肢からタスク変換
```
POST /integration/story-choice-to-task
```

### タスク完了同期
```
POST /integration/task-completion-sync
```

### Mandala反映
```
POST /integration/mandala-reflection
```

### リアルタイムフック処理
```
POST /integration/process-real-time-hooks
```

### 統合状態取得
```
GET /integration/status/{uid}
```

### 統合分析データ
```
GET /integration/analytics
```

## データモデル

### StoryChoiceHook
ストーリー選択肢フック情報
- choice_id: 選択肢ID
- choice_text: 選択肢テキスト
- real_task_id: 既存タスクID（オプション）
- habit_tag: 習慣タグ
- task_template: タスクテンプレート
- mandala_impact: Mandala影響
- therapeutic_weight: 治療的重み

### TaskCompletionHook
タスク完了フック情報
- task_id: タスクID
- uid: ユーザーID
- completion_data: 完了データ
- story_progression_trigger: ストーリー進行トリガー
- mandala_update_trigger: Mandala更新トリガー
- xp_calculation_data: XP計算データ

### MandalaReflectionData
Mandala反映データ
- uid: ユーザーID
- story_choices: ストーリー選択肢リスト
- completion_date: 完了日時
- target_date: 対象日時（明日）
- chapter_context: チャプターコンテキスト
- therapeutic_focus: 治療的焦点

## サービス統合

### 連携サービス
- Task Management Service (port 8001)
- AI Story Service (port 8006)
- Mandala System (port 8003)
- Core Game Engine (port 8002)

### 統合機能
- タスク作成・更新
- ストーリー生成
- Mandala更新
- XP計算
- クリスタル成長
- 共鳴イベント

## 実装の特徴

### 1. 選択肢からタスク推論
選択肢テキストの内容に基づいてタスクタイプを自動推論：
- "挑戦", "チャレンジ" → SKILL_UP
- "つながり", "コミュニケーション" → SOCIAL
- "継続", "習慣" → ROUTINE
- "勇気", "行動" → ONE_SHOT

### 2. クリスタル属性マッピング
タスクタイプに基づいてクリスタル属性を自動設定：
- SKILL_UP → CURIOSITY + COURAGE
- SOCIAL → EMPATHY + COMMUNICATION
- ROUTINE → SELF_DISCIPLINE + RESILIENCE
- ONE_SHOT → WISDOM + RESILIENCE

### 3. Mandalaセル位置決定
選択肢内容に基づいてMandalaセル位置を自動決定：
- "挑戦" → 好奇心エリア (2,4)
- "つながり" → コミュニケーションエリア (4,6)
- "継続" → 自律性エリア (1,1)
- "勇気" → 勇気エリア (6,2)

### 4. フォールバック機能
外部サービス呼び出し失敗時のフォールバック：
- モックレスポンス生成
- 基本的なXP計算
- 簡単なストーリー生成
- Mandalaセル影響計算

## テスト

### 統合テスト
```bash
python -m pytest services/task-story-integration/test_task_story_integration.py -v
```

### 簡単なテスト
```bash
python services/task-story-integration/simple_test.py
```

## 実行方法

### サービス起動
```bash
cd services/task-story-integration
python main.py
```

サービスは http://localhost:8007 で起動します。

### 依存関係
- FastAPI
- httpx (外部API呼び出し用)
- pydantic (データバリデーション)
- shared interfaces (共有型定義)

## 要件対応

### Requirement 1.4
- ストーリー選択肢とreal_task_id/habit_tagの連携 ✅
- 明日のMandalaへの反映機能 ✅

### Requirement 5.5
- タスク完了とストーリー進行の同期 ✅
- XP計算統合 ✅
- クリスタル成長イベント ✅

## 今後の拡張

1. **高度な推論機能**
   - 自然言語処理による選択肢分析
   - ユーザー履歴に基づく推論改善

2. **パフォーマンス最適化**
   - 非同期処理の最適化
   - キャッシュ機能の追加

3. **監視・ログ機能**
   - 統合処理の詳細ログ
   - パフォーマンスメトリクス

4. **エラーハンドリング強化**
   - リトライ機能
   - 部分的失敗の処理