# α版プレイテストサービス

## 概要

50名のテストユーザーを対象としたα版プレイテスト環境とデータ収集システムです。
ユーザビリティ検証とデータ収集を目的とし、プライバシー保護を重視した設計となっています。

## 機能

### 24.1 プレイテスト環境とデータ収集システム
- テストユーザー管理システム
- 行動ログ収集とプライバシー保護機能
- リアルタイム分析ダッシュボード
- テスト環境の統合テスト

### 24.2 フィードバック収集と分析システム
- アプリ内フィードバック機能
- 感情分析とテーマ抽出機能
- 改善提案の自動生成機能
- フィードバックシステムの統合テスト

### 24.3 A/Bテスト機能とパフォーマンス測定
- 機能別A/Bテストフレームワーク
- 治療効果の統計的検証機能
- パフォーマンス指標の自動収集
- A/Bテストシステムの統合テスト

## API エンドポイント

### テストユーザー管理
- `POST /api/playtest/users` - テストユーザー登録
- `GET /api/playtest/users/{user_id}` - ユーザー情報取得
- `PUT /api/playtest/users/{user_id}/status` - ユーザー状態更新

### データ収集
- `POST /api/playtest/events` - 行動ログ記録
- `GET /api/playtest/analytics/dashboard` - リアルタイム分析データ
- `GET /api/playtest/analytics/reports` - 分析レポート

### フィードバック
- `POST /api/playtest/feedback` - フィードバック投稿
- `GET /api/playtest/feedback/analysis` - フィードバック分析結果
- `GET /api/playtest/feedback/suggestions` - 改善提案

### A/Bテスト
- `POST /api/playtest/ab-tests` - A/Bテスト作成
- `GET /api/playtest/ab-tests/{test_id}/results` - テスト結果
- `POST /api/playtest/ab-tests/{test_id}/assign` - ユーザー割り当て

## データモデル

### TestUser
- user_id: str
- email: str
- consent_given: bool
- test_group: str
- registration_date: datetime
- status: str (active, inactive, completed)

### BehaviorLog
- log_id: str
- user_id: str
- event_type: str
- event_data: dict
- timestamp: datetime
- session_id: str

### Feedback
- feedback_id: str
- user_id: str
- content: str
- rating: int
- category: str
- timestamp: datetime
- sentiment_score: float

## プライバシー保護

- 個人識別情報の暗号化
- データ最小化原則の適用
- 同意管理システム
- データ保持期間の制限（90日）
- 匿名化処理