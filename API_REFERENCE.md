# API リファレンス

このドキュメントでは、ローカルテスト環境で利用可能なすべてのAPIエンドポイントの詳細を説明します。

## 📖 目次

- [概要](#概要)
- [認証](#認証)
- [認証サービス API](#認証サービス-api)
- [コアゲームサービス API](#コアゲームサービス-api)
- [タスク管理サービス API](#タスク管理サービス-api)
- [Mandalaサービス API](#mandalaサービス-api)
- [エラーハンドリング](#エラーハンドリング)
- [レート制限](#レート制限)
- [バージョニング](#バージョニング)

---

## 概要

### ベースURL

| サービス | ベースURL | ポート |
|---------|----------|--------|
| 認証サービス | `http://localhost:8002` | 8002 |
| コアゲームサービス | `http://localhost:8001` | 8001 |
| タスク管理サービス | `http://localhost:8003` | 8003 |
| Mandalaサービス | `http://localhost:8004` | 8004 |

### 共通ヘッダー

すべてのAPIリクエストには以下のヘッダーを含めることを推奨します：

```http
Content-Type: application/json
Accept: application/json
```

認証が必要なエンドポイントには、以下のヘッダーも必要です：

```http
Authorization: Bearer <jwt_token>
```

### レスポンス形式

すべてのレスポンスはJSON形式です。

**成功レスポンス:**
```json
{
  "data": { ... },
  "message": "Success"
}
```

**エラーレスポンス:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  }
}
```

---

## 認証

### JWT トークン

認証が必要なエンドポイントにアクセスするには、JWT トークンが必要です。

**トークンの取得:**
1. `/auth/login` または `/auth/register` エンドポイントを使用
2. レスポンスから `token` を取得
3. 以降のリクエストで `Authorization` ヘッダーに含める

**トークンの形式:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**トークンの有効期限:**
- デフォルト: 24時間
- リフレッシュ: `/auth/refresh` エンドポイントを使用

---

## 認証サービス API

### POST /auth/register

新しいユーザーを登録します。

**エンドポイント:** `POST http://localhost:8002/auth/register`

**認証:** 不要

**リクエストボディ:**
```json
{
  "username": "string (required, 3-50文字)",
  "email": "string (required, 有効なメールアドレス)",
  "password": "string (required, 8文字以上)"
}
```

**レスポンス (201 Created):**
```json
{
  "uid": "user_001",
  "username": "testuser",
  "email": "test@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "created_at": "2024-10-18T10:00:00Z"
}
```

**エラーレスポンス:**

| ステータスコード | 説明 |
|----------------|------|
| 400 | 不正なリクエスト（バリデーションエラー） |
| 409 | ユーザー名またはメールアドレスが既に存在 |

**例:**
```bash
curl -X POST http://localhost:8002/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

---

### POST /auth/login

ユーザーをログインさせます。

**エンドポイント:** `POST http://localhost:8002/auth/login`

**認証:** 不要

**リクエストボディ:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**レスポンス (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "uid": "user_001",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

**エラーレスポンス:**

| ステータスコード | 説明 |
|----------------|------|
| 400 | 不正なリクエスト |
| 401 | 認証失敗（ユーザー名またはパスワードが間違っている） |

**例:**
```bash
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'
```

---

### POST /auth/logout

ユーザーをログアウトさせます。

**エンドポイント:** `POST http://localhost:8002/auth/logout`

**認証:** 必要

**リクエストボディ:** なし

**レスポンス (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**例:**
```bash
curl -X POST http://localhost:8002/auth/logout \
  -H "Authorization: Bearer <token>"
```

---

### POST /auth/refresh

JWT トークンをリフレッシュします。

**エンドポイント:** `POST http://localhost:8002/auth/refresh`

**認証:** 必要

**リクエストボディ:** なし

**レスポンス (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

**例:**
```bash
curl -X POST http://localhost:8002/auth/refresh \
  -H "Authorization: Bearer <token>"
```

---

### GET /auth/verify

JWT トークンを検証します。

**エンドポイント:** `GET http://localhost:8002/auth/verify`

**認証:** 必要

**レスポンス (200 OK):**
```json
{
  "valid": true,
  "uid": "user_001",
  "username": "testuser",
  "expires_at": "2024-10-19T10:00:00Z"
}
```

**例:**
```bash
curl -X GET http://localhost:8002/auth/verify \
  -H "Authorization: Bearer <token>"
```

---

### GET /health

認証サービスのヘルスチェック。

**エンドポイント:** `GET http://localhost:8002/health`

**認証:** 不要

**レスポンス (200 OK):**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "timestamp": "2024-10-18T10:00:00Z"
}
```

---

## コアゲームサービス API

### GET /api/user/profile

ユーザープロフィールを取得します。

**エンドポイント:** `GET http://localhost:8001/api/user/profile`

**認証:** 必要

**クエリパラメータ:**
- `uid` (optional): ユーザーID（指定しない場合は認証トークンから取得）

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "username": "testuser",
  "email": "test@example.com",
  "player_level": 5,
  "total_xp": 150,
  "yu_level": 3,
  "created_at": "2024-10-01T00:00:00Z",
  "last_login": "2024-10-18T10:00:00Z"
}
```

**例:**
```bash
curl -X GET http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer <token>"
```

---

### PUT /api/user/profile

ユーザープロフィールを更新します。

**エンドポイント:** `PUT http://localhost:8001/api/user/profile`

**認証:** 必要

**リクエストボディ:**
```json
{
  "username": "string (optional)",
  "email": "string (optional)"
}
```

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "username": "newusername",
  "email": "newemail@example.com",
  "updated_at": "2024-10-18T10:00:00Z"
}
```

**例:**
```bash
curl -X PUT http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newusername"
  }'
```

---

### POST /api/xp/add

ユーザーにXPを追加します。

**エンドポイント:** `POST http://localhost:8001/api/xp/add`

**認証:** 必要

**リクエストボディ:**
```json
{
  "uid": "string (required)",
  "xp_amount": "number (required, 正の整数)",
  "source": "string (required, 例: task_completion, mood_entry)"
}
```

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "previous_xp": 150,
  "added_xp": 10,
  "new_total_xp": 160,
  "level_up": false,
  "current_level": 5,
  "xp_to_next_level": 40
}
```

**レベルアップ時のレスポンス:**
```json
{
  "uid": "user_001",
  "previous_xp": 190,
  "added_xp": 10,
  "new_total_xp": 200,
  "level_up": true,
  "previous_level": 5,
  "current_level": 6,
  "xp_to_next_level": 100
}
```

**例:**
```bash
curl -X POST http://localhost:8001/api/xp/add \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "user_001",
    "xp_amount": 10,
    "source": "task_completion"
  }'
```


---

### GET /api/level/check

ユーザーの現在のレベル情報を取得します。

**エンドポイント:** `GET http://localhost:8001/api/level/check`

**認証:** 必要

**クエリパラメータ:**
- `uid` (required): ユーザーID

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "current_level": 5,
  "total_xp": 160,
  "xp_for_current_level": 100,
  "xp_to_next_level": 40,
  "progress_percentage": 60.0
}
```

**例:**
```bash
curl -X GET "http://localhost:8001/api/level/check?uid=user_001" \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/resonance/calculate

共鳴値を計算します。

**エンドポイント:** `POST http://localhost:8001/api/resonance/calculate`

**認証:** 必要

**リクエストボディ:**
```json
{
  "uid": "string (required)",
  "task_difficulty": "number (required, 1-5)",
  "mood_score": "number (required, 1-5)"
}
```

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "resonance_value": 0.85,
  "xp_multiplier": 1.2,
  "message": "高い共鳴が発生しています"
}
```

**例:**
```bash
curl -X POST http://localhost:8001/api/resonance/calculate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "user_001",
    "task_difficulty": 3,
    "mood_score": 4
  }'
```

---

### GET /health

コアゲームサービスのヘルスチェック。

**エンドポイント:** `GET http://localhost:8001/health`

**認証:** 不要

**レスポンス (200 OK):**
```json
{
  "status": "healthy",
  "service": "core-game-service",
  "timestamp": "2024-10-18T10:00:00Z"
}
```

---

## タスク管理サービス API

### GET /api/tasks

タスク一覧を取得します。

**エンドポイント:** `GET http://localhost:8003/api/tasks`

**認証:** 必要

**クエリパラメータ:**
- `status` (optional): タスクステータス（pending, in_progress, completed）
- `limit` (optional): 取得件数（デフォルト: 20, 最大: 100）
- `offset` (optional): オフセット（デフォルト: 0）
- `sort_by` (optional): ソート項目（created_at, difficulty, title）
- `order` (optional): ソート順（asc, desc）

**レスポンス (200 OK):**
```json
{
  "tasks": [
    {
      "task_id": "task_001",
      "uid": "user_001",
      "title": "サンプルタスク",
      "description": "タスクの説明",
      "difficulty": 2,
      "status": "pending",
      "created_at": "2024-10-18T10:00:00Z",
      "updated_at": "2024-10-18T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

**例:**
```bash
curl -X GET "http://localhost:8003/api/tasks?status=pending&limit=10" \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/tasks

新しいタスクを作成します。

**エンドポイント:** `POST http://localhost:8003/api/tasks`

**認証:** 必要

**リクエストボディ:**
```json
{
  "title": "string (required, 1-200文字)",
  "description": "string (optional, 最大1000文字)",
  "difficulty": "number (required, 1-5)"
}
```

**レスポンス (201 Created):**
```json
{
  "task_id": "task_002",
  "uid": "user_001",
  "title": "新しいタスク",
  "description": "タスクの説明",
  "difficulty": 2,
  "status": "pending",
  "created_at": "2024-10-18T11:00:00Z"
}
```

**例:**
```bash
curl -X POST http://localhost:8003/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新しいタスク",
    "description": "タスクの説明",
    "difficulty": 2
  }'
```

---

### GET /api/tasks/{task_id}

特定のタスクの詳細を取得します。

**エンドポイント:** `GET http://localhost:8003/api/tasks/{task_id}`

**認証:** 必要

**パスパラメータ:**
- `task_id` (required): タスクID

**レスポンス (200 OK):**
```json
{
  "task_id": "task_001",
  "uid": "user_001",
  "title": "サンプルタスク",
  "description": "タスクの説明",
  "difficulty": 2,
  "status": "pending",
  "created_at": "2024-10-18T10:00:00Z",
  "updated_at": "2024-10-18T10:00:00Z",
  "completed_at": null
}
```

**エラーレスポンス:**

| ステータスコード | 説明 |
|----------------|------|
| 404 | タスクが見つからない |

**例:**
```bash
curl -X GET http://localhost:8003/api/tasks/task_001 \
  -H "Authorization: Bearer <token>"
```

---

### PUT /api/tasks/{task_id}

タスクを更新します。

**エンドポイント:** `PUT http://localhost:8003/api/tasks/{task_id}`

**認証:** 必要

**パスパラメータ:**
- `task_id` (required): タスクID

**リクエストボディ:**
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "difficulty": "number (optional, 1-5)",
  "status": "string (optional, pending/in_progress/completed)"
}
```

**レスポンス (200 OK):**
```json
{
  "task_id": "task_001",
  "uid": "user_001",
  "title": "更新されたタスク",
  "description": "更新された説明",
  "difficulty": 3,
  "status": "in_progress",
  "updated_at": "2024-10-18T12:00:00Z"
}
```

**例:**
```bash
curl -X PUT http://localhost:8003/api/tasks/task_001 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新されたタスク",
    "status": "in_progress"
  }'
```

---

### DELETE /api/tasks/{task_id}

タスクを削除します。

**エンドポイント:** `DELETE http://localhost:8003/api/tasks/{task_id}`

**認証:** 必要

**パスパラメータ:**
- `task_id` (required): タスクID

**レスポンス (200 OK):**
```json
{
  "message": "Task deleted successfully",
  "task_id": "task_001"
}
```

**例:**
```bash
curl -X DELETE http://localhost:8003/api/tasks/task_001 \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/tasks/{task_id}/complete

タスクを完了します。

**エンドポイント:** `POST http://localhost:8003/api/tasks/{task_id}/complete`

**認証:** 必要

**パスパラメータ:**
- `task_id` (required): タスクID

**リクエストボディ:** なし

**レスポンス (200 OK):**
```json
{
  "task_id": "task_001",
  "status": "completed",
  "completed_at": "2024-10-18T13:00:00Z",
  "xp_earned": 10,
  "new_total_xp": 170,
  "level_up": false
}
```

**例:**
```bash
curl -X POST http://localhost:8003/api/tasks/task_001/complete \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/pomodoro/start

ポモドーロタイマーを開始します。

**エンドポイント:** `POST http://localhost:8003/api/pomodoro/start`

**認証:** 必要

**リクエストボディ:**
```json
{
  "task_id": "string (required)",
  "duration": "number (optional, デフォルト: 25分)"
}
```

**レスポンス (200 OK):**
```json
{
  "pomodoro_id": "pomo_001",
  "task_id": "task_001",
  "start_time": "2024-10-18T13:00:00Z",
  "end_time": "2024-10-18T13:25:00Z",
  "duration": 25,
  "status": "active"
}
```

**例:**
```bash
curl -X POST http://localhost:8003/api/pomodoro/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task_001",
    "duration": 25
  }'
```

---

### POST /api/pomodoro/{pomodoro_id}/complete

ポモドーロセッションを完了します。

**エンドポイント:** `POST http://localhost:8003/api/pomodoro/{pomodoro_id}/complete`

**認証:** 必要

**パスパラメータ:**
- `pomodoro_id` (required): ポモドーロID

**レスポンス (200 OK):**
```json
{
  "pomodoro_id": "pomo_001",
  "task_id": "task_001",
  "completed_at": "2024-10-18T13:25:00Z",
  "actual_duration": 25,
  "xp_earned": 5
}
```

**例:**
```bash
curl -X POST http://localhost:8003/api/pomodoro/pomo_001/complete \
  -H "Authorization: Bearer <token>"
```

---

### GET /health

タスク管理サービスのヘルスチェック。

**エンドポイント:** `GET http://localhost:8003/health`

**認証:** 不要

**レスポンス (200 OK):**
```json
{
  "status": "healthy",
  "service": "task-mgmt-service",
  "timestamp": "2024-10-18T10:00:00Z"
}
```

---

## Mandalaサービス API

### GET /api/mandala/{uid}

ユーザーのMandala状態を取得します。

**エンドポイント:** `GET http://localhost:8004/api/mandala/{uid}`

**認証:** 必要

**パスパラメータ:**
- `uid` (required): ユーザーID

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "total_sections": 81,
  "completed_sections": 15,
  "progress_percentage": 18.52,
  "sections": [
    {
      "section_id": 1,
      "status": "completed",
      "completed_at": "2024-10-15T10:00:00Z"
    },
    {
      "section_id": 2,
      "status": "pending",
      "completed_at": null
    }
  ],
  "last_updated": "2024-10-18T10:00:00Z"
}
```

**例:**
```bash
curl -X GET http://localhost:8004/api/mandala/user_001 \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/mandala/{uid}/section/{section_id}

Mandalaのセクションを完了します。

**エンドポイント:** `POST http://localhost:8004/api/mandala/{uid}/section/{section_id}`

**認証:** 必要

**パスパラメータ:**
- `uid` (required): ユーザーID
- `section_id` (required): セクションID（1-81）

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "section_id": 16,
  "status": "completed",
  "completed_at": "2024-10-18T14:00:00Z",
  "total_completed": 16,
  "progress_percentage": 19.75,
  "xp_earned": 5
}
```

**例:**
```bash
curl -X POST http://localhost:8004/api/mandala/user_001/section/16 \
  -H "Authorization: Bearer <token>"
```

---

### GET /api/mandala/{uid}/progress

Mandalaの進捗情報を取得します。

**エンドポイント:** `GET http://localhost:8004/api/mandala/{uid}/progress`

**認証:** 必要

**パスパラメータ:**
- `uid` (required): ユーザーID

**レスポンス (200 OK):**
```json
{
  "uid": "user_001",
  "total_sections": 81,
  "completed_sections": 16,
  "progress_percentage": 19.75,
  "sections_by_ring": {
    "inner": {
      "total": 9,
      "completed": 5
    },
    "middle": {
      "total": 24,
      "completed": 8
    },
    "outer": {
      "total": 48,
      "completed": 3
    }
  },
  "estimated_completion_date": "2025-02-15T00:00:00Z"
}
```

**例:**
```bash
curl -X GET http://localhost:8004/api/mandala/user_001/progress \
  -H "Authorization: Bearer <token>"
```

---

### GET /health

Mandalaサービスのヘルスチェック。

**エンドポイント:** `GET http://localhost:8004/health`

**認証:** 不要

**レスポンス (200 OK):**
```json
{
  "status": "healthy",
  "service": "mandala-service",
  "timestamp": "2024-10-18T10:00:00Z"
}
```

---

## エラーハンドリング

### エラーレスポンス形式

すべてのエラーレスポンスは以下の形式に従います：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "issue": "Specific issue description"
    }
  }
}
```

### HTTPステータスコード

| コード | 意味 | 説明 |
|-------|------|------|
| 200 | OK | リクエスト成功 |
| 201 | Created | リソース作成成功 |
| 400 | Bad Request | 不正なリクエスト（バリデーションエラー） |
| 401 | Unauthorized | 認証エラー（トークンが無効または期限切れ） |
| 403 | Forbidden | 権限エラー（アクセス権限がない） |
| 404 | Not Found | リソースが見つからない |
| 409 | Conflict | リソースの競合（既に存在する） |
| 422 | Unprocessable Entity | 処理できないエンティティ |
| 429 | Too Many Requests | レート制限超過 |
| 500 | Internal Server Error | サーバー内部エラー |
| 503 | Service Unavailable | サービス利用不可 |

### エラーコード一覧

#### 認証エラー

| コード | 説明 |
|-------|------|
| `AUTH_INVALID_CREDENTIALS` | ユーザー名またはパスワードが間違っている |
| `AUTH_TOKEN_EXPIRED` | トークンの有効期限が切れている |
| `AUTH_TOKEN_INVALID` | トークンが無効 |
| `AUTH_USER_NOT_FOUND` | ユーザーが見つからない |
| `AUTH_USER_ALREADY_EXISTS` | ユーザーが既に存在する |

#### バリデーションエラー

| コード | 説明 |
|-------|------|
| `VALIDATION_ERROR` | 入力データのバリデーションエラー |
| `VALIDATION_REQUIRED_FIELD` | 必須フィールドが不足 |
| `VALIDATION_INVALID_FORMAT` | フォーマットが不正 |
| `VALIDATION_OUT_OF_RANGE` | 値が範囲外 |

#### リソースエラー

| コード | 説明 |
|-------|------|
| `RESOURCE_NOT_FOUND` | リソースが見つからない |
| `RESOURCE_ALREADY_EXISTS` | リソースが既に存在する |
| `RESOURCE_CONFLICT` | リソースの競合 |

#### サーバーエラー

| コード | 説明 |
|-------|------|
| `INTERNAL_SERVER_ERROR` | サーバー内部エラー |
| `DATABASE_ERROR` | データベースエラー |
| `SERVICE_UNAVAILABLE` | サービス利用不可 |

### エラーレスポンス例

#### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "title",
      "issue": "Title must be between 1 and 200 characters"
    }
  }
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Authentication token has expired",
    "details": {
      "expired_at": "2024-10-17T10:00:00Z"
    }
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Task not found",
    "details": {
      "task_id": "task_999"
    }
  }
}
```

#### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "request_id": "req_12345"
    }
  }
}
```

---

## レート制限

ローカルテスト環境ではレート制限は適用されませんが、本番環境では以下の制限があります：

| エンドポイント | 制限 |
|--------------|------|
| 認証エンドポイント | 10リクエスト/分 |
| 一般的なGETエンドポイント | 100リクエスト/分 |
| 一般的なPOST/PUT/DELETEエンドポイント | 50リクエスト/分 |

レート制限に達した場合、`429 Too Many Requests` が返されます：

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": {
      "retry_after": 60
    }
  }
}
```

---

## バージョニング

現在のAPIバージョン: **v1**

将来的にAPIに破壊的変更が加えられる場合、新しいバージョンが導入されます：

```
http://localhost:8001/v2/api/user/profile
```

---

## Postman コレクション

APIをテストするためのPostmanコレクションを提供しています。

### インポート方法

1. Postmanを開く
2. Import > Link タブを選択
3. 以下のURLを入力（または、ローカルファイルをインポート）

### 環境変数

Postmanで以下の環境変数を設定してください：

```json
{
  "base_url_auth": "http://localhost:8002",
  "base_url_core": "http://localhost:8001",
  "base_url_task": "http://localhost:8003",
  "base_url_mandala": "http://localhost:8004",
  "token": ""
}
```

### 使用方法

1. `/auth/login` または `/auth/register` を実行
2. レスポンスから `token` を取得
3. 環境変数 `token` に設定
4. 他のエンドポイントをテスト

---

## サポート

APIに関する質問や問題がある場合：

1. [トラブルシューティングガイド](TROUBLESHOOTING_GUIDE.md)を確認
2. [GitHub Issues](https://github.com/your-repo/issues)で報告
3. [ディスカッションフォーラム](https://github.com/your-repo/discussions)で質問

---

**最終更新**: 2024年10月18日  
**APIバージョン**: v1  
**メンテナー**: Therapeutic Gamification App Team
