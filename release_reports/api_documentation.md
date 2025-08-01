# API仕様書

## 概要
治療的ゲーミフィケーションアプリケーションのAPI仕様書です。

## 認証
すべてのAPIエンドポイントはJWTトークンによる認証が必要です。

```
Authorization: Bearer <JWT_TOKEN>
```

## エンドポイント一覧

### 認証API
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/profile` - プロファイル取得
- `POST /api/auth/refresh` - トークン更新

### ゲームAPI
- `GET /api/game/profile` - ゲームプロファイル取得
- `POST /api/game/xp` - XP追加
- `GET /api/game/level` - レベル情報取得
- `POST /api/game/resonance` - 共鳴イベントチェック

### タスク管理API
- `GET /api/tasks` - タスク一覧取得
- `POST /api/tasks/create` - タスク作成
- `POST /api/tasks/{id}/complete` - タスク完了
- `GET /api/tasks/stats` - タスク統計取得

### Mandala API
- `GET /api/mandala/grid` - Mandalaグリッド取得
- `POST /api/mandala/unlock` - セルアンロック
- `GET /api/mandala/progress` - 進捗取得

### ストーリーAPI
- `POST /api/story/generate` - ストーリー生成
- `GET /api/story/current` - 現在のストーリー取得
- `POST /api/story/choice` - 選択肢選択

### 治療安全性API
- `POST /api/safety/moderate` - コンテンツモデレーション
- `GET /api/safety/metrics` - 安全性メトリクス取得
- `POST /api/safety/cbt-intervention` - CBT介入

## エラーレスポンス
```json
{
  "error": "error_code",
  "message": "エラーメッセージ",
  "details": {}
}
```

## レート制限
- 120リクエスト/分/IP
- 認証済みユーザー: 300リクエスト/分

## データ形式
すべてのAPIはJSON形式でデータを送受信します。
