# APIエンドポイント検出レポート
**生成日時**: 2025年10月16日 11:52:58
---

## AUTH サービス
**ベースURL**: http://localhost:8002

### ✅ 動作中のエンドポイント (1)
- `GET /health` - ヘルスチェック

### ⚠️ 有効なデータが必要 (3)
- `POST /auth/token` - トークン作成 (Status: 422)
- `POST /auth/guardian/login` - Guardian ログイン (Status: 422)
- `POST /auth/guardian/grant` - アクセス許可 (Status: 422)

## CORE_GAME サービス
**ベースURL**: http://localhost:8001

### ✅ 動作中のエンドポイント (4)
- `GET /health` - ヘルスチェック
- `POST /level/progress` - レベル進捗取得
- `POST /resonance/check` - 共鳴チェック
- `POST /system/status` - システム状態取得

### ⚠️ 有効なデータが必要 (3)
- `POST /xp/add` - XP追加 (Status: 422)
- `POST /resonance/trigger` - 共鳴イベント発動 (Status: 400)
- `POST /xp/calculate` - XP計算プレビュー (Status: 422)

## TASK_MGMT サービス
**ベースURL**: http://localhost:8003

### ✅ 動作中のエンドポイント (3)
- `GET /health` - ヘルスチェック
- `GET /tasks/{uid}` - タスク一覧取得
- `GET /tasks/{uid}/statistics` - 統計取得

### ⚠️ 有効なデータが必要 (3)
- `POST /tasks/{uid}/create` - タスク作成 (Status: 422)
- `POST /tasks/{uid}/{task_id}/complete` - タスク完了 (Status: 422)
- `POST /tasks/xp-preview` - XPプレビュー (Status: 422)

### ❌ 未実装 (4)
- `GET /tasks/{uid}/{task_id}` - タスク詳細取得
- `PUT /tasks/{uid}/{task_id}` - タスク更新
- `POST /tasks/{uid}/{task_id}/start` - タスク開始
- `DELETE /tasks/{uid}/{task_id}` - タスク削除

## MANDALA サービス
**ベースURL**: http://localhost:8004

### ✅ 動作中のエンドポイント (2)
- `GET /health` - ヘルスチェック
- `GET /mandala/{uid}/reminder` - リマインダー取得

### ⚠️ 有効なデータが必要 (2)
- `POST /mandala/{uid}/unlock` - セルアンロック (Status: 422)
- `POST /mandala/{uid}/complete` - セル完了 (Status: 422)

### 🔥 エラー (2)
- `GET /mandala/{uid}/grid` - グリッド取得 (Status: 500)
- `GET /mandala/{uid}/status` - ステータス取得 (Status: 500)

---

## 📊 サマリー
- **総エンドポイント数**: 27
- **動作中**: 10
- **データ必要**: 11
- **利用可能**: 21 (77.8%)
