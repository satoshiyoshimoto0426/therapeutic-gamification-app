# ローカルテスト環境 - アーキテクチャドキュメント

このドキュメントでは、ローカルテスト環境のシステム構成、サービス間の依存関係、データフローについて詳しく説明します。

## 📖 目次

- [システム概要](#システム概要)
- [アーキテクチャ図](#アーキテクチャ図)
- [コンポーネント詳細](#コンポーネント詳細)
- [サービス間の依存関係](#サービス間の依存関係)
- [データフロー](#データフロー)
- [通信プロトコル](#通信プロトコル)
- [セキュリティアーキテクチャ](#セキュリティアーキテクチャ)
- [スケーラビリティ考慮事項](#スケーラビリティ考慮事項)

---

## システム概要

ローカルテスト環境は、治療的ゲーミフィケーションアプリケーションを開発者のマシン上で実行するための包括的な環境です。マイクロサービスアーキテクチャを採用し、各サービスが独立して動作しながら、統一されたAPIゲートウェイを通じて連携します。

### 主要な設計原則

1. **疎結合**: サービス間の依存関係を最小限に抑える
2. **高凝集**: 各サービスは明確な責務を持つ
3. **テスタビリティ**: 各コンポーネントを独立してテスト可能
4. **開発者体験**: セットアップと使用が簡単
5. **本番環境との整合性**: 本番環境と同様のアーキテクチャ

---

## アーキテクチャ図

### 全体システム構成

```
┌─────────────────────────────────────────────────────────────────┐
│                     ローカルテスト環境                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              開発者のブラウザ                              │   │
│  │            http://localhost:3000                          │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │                                           │
│                       ▼                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         フロントエンド (React + Vite)                      │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ UI Components│  │ State Mgmt   │  │ API Client   │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │                                                            │   │
│  │  Port: 3000                                               │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │                                           │
│                       │ HTTP/REST                                 │
│                       │                                           │
│                       ▼                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Vite Dev Server Proxy                        │   │
│  │         (CORS & Request Routing)                          │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │                                           │
│         ┌─────────────┼─────────────┬─────────────┐             │
│         │             │             │             │             │
│         ▼             ▼             ▼             ▼             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Auth   │  │Core Game │  │Task Mgmt │  │ Mandala  │       │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │       │
│  │          │  │          │  │          │  │          │       │
│  │ Port:    │  │ Port:    │  │ Port:    │  │ Port:    │       │
│  │ 8002     │  │ 8001     │  │ 8003     │  │ 8004     │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │             │
│       └─────────────┴─────────────┴─────────────┘             │
│                       │                                           │
│                       ▼                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           モックFirestoreデータベース                      │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │   Users      │  │    Tasks     │  │ Mood Entries │  │   │
│  │  │  Collection  │  │  Collection  │  │  Collection  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │                                                            │   │
│  │  In-Memory / File-based Storage                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### レイヤー構成

```
┌─────────────────────────────────────────────────────────┐
│                  プレゼンテーション層                      │
│              (React Components, UI)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   API ゲートウェイ層                       │
│              (Vite Proxy, Routing)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  ビジネスロジック層                        │
│         (FastAPI Services, Domain Logic)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   データアクセス層                         │
│         (Repository Pattern, Mock Firestore)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    データ永続化層                          │
│         (In-Memory / File-based Storage)                │
└─────────────────────────────────────────────────────────┘
```

---

## コンポーネント詳細

### 1. フロントエンド (React + Vite)

**責務:**
- ユーザーインターフェースの提供
- ユーザー入力の処理
- バックエンドAPIとの通信
- 状態管理

**技術スタック:**
- React 18
- TypeScript
- Vite (開発サーバー & ビルドツール)
- React Router (ルーティング)
- Context API (状態管理)

**主要コンポーネント:**

```
frontend/
├── src/
│   ├── components/      # UIコンポーネント
│   │   ├── dashboard/   # ダッシュボード関連
│   │   ├── task/        # タスク管理関連
│   │   ├── gamification/# ゲーミフィケーション要素
│   │   └── common/      # 共通コンポーネント
│   ├── contexts/        # Context API
│   │   ├── AuthContext.tsx
│   │   └── ApiContext.tsx
│   ├── pages/           # ページコンポーネント
│   │   ├── Login.tsx
│   │   └── Dashboard.tsx
│   └── App.tsx          # ルートコンポーネント
└── vite.config.ts       # Vite設定
```

**ポート:** 3000


### 2. 認証サービス (Auth Service)

**責務:**
- ユーザー認証
- JWT トークンの発行と検証
- セッション管理
- RBAC (ロールベースアクセス制御)

**技術スタック:**
- FastAPI
- Python 3.11
- PyJWT (JWT処理)
- Passlib (パスワードハッシュ化)

**主要エンドポイント:**

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/auth/register` | POST | ユーザー登録 |
| `/auth/login` | POST | ログイン |
| `/auth/logout` | POST | ログアウト |
| `/auth/refresh` | POST | トークンリフレッシュ |
| `/auth/verify` | GET | トークン検証 |
| `/health` | GET | ヘルスチェック |

**ポート:** 8002

**ディレクトリ構造:**
```
services/auth/
├── main.py              # FastAPIアプリケーション
├── auth_middleware.py   # 認証ミドルウェア
├── jwt_service.py       # JWT処理
└── test_auth.py         # テスト
```

### 3. コアゲームサービス (Core Game Service)

**責務:**
- ゲームロジックの管理
- XP (経験値) とレベルシステム
- 共鳴システム
- プレイヤー状態の管理

**技術スタック:**
- FastAPI
- Python 3.11
- Pydantic (データバリデーション)

**主要エンドポイント:**

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/api/user/profile` | GET | ユーザープロフィール取得 |
| `/api/user/profile` | PUT | プロフィール更新 |
| `/api/xp/add` | POST | XP追加 |
| `/api/level/check` | GET | レベル確認 |
| `/api/resonance/calculate` | POST | 共鳴計算 |
| `/health` | GET | ヘルスチェック |

**ポート:** 8001

**ディレクトリ構造:**
```
services/core-game/
├── main.py              # FastAPIアプリケーション
├── xp_system.py         # XPシステム
├── level_system.py      # レベルシステム
├── resonance_system.py  # 共鳴システム
└── test_core_game.py    # テスト
```

### 4. タスク管理サービス (Task Management Service)

**責務:**
- タスクのCRUD操作
- タスクステータス管理
- ポモドーロタイマー統合
- タスク完了時のXP計算

**技術スタック:**
- FastAPI
- Python 3.11
- Pydantic

**主要エンドポイント:**

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/api/tasks` | GET | タスク一覧取得 |
| `/api/tasks` | POST | タスク作成 |
| `/api/tasks/{id}` | GET | タスク詳細取得 |
| `/api/tasks/{id}` | PUT | タスク更新 |
| `/api/tasks/{id}` | DELETE | タスク削除 |
| `/api/tasks/{id}/complete` | POST | タスク完了 |
| `/api/pomodoro/start` | POST | ポモドーロ開始 |
| `/health` | GET | ヘルスチェック |

**ポート:** 8003

**ディレクトリ構造:**
```
services/task-mgmt/
├── main.py                  # FastAPIアプリケーション
├── task_system.py           # タスクシステム
├── pomodoro_integration.py  # ポモドーロ統合
└── test_task_management.py  # テスト
```

### 5. Mandalaサービス (Mandala Service)

**責務:**
- Mandala進捗管理
- セクション完了追跡
- ビジュアライゼーションデータ提供

**技術スタック:**
- FastAPI
- Python 3.11

**主要エンドポイント:**

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/api/mandala/{uid}` | GET | Mandala状態取得 |
| `/api/mandala/{uid}/section/{id}` | POST | セクション完了 |
| `/api/mandala/{uid}/progress` | GET | 進捗取得 |
| `/health` | GET | ヘルスチェック |

**ポート:** 8004

### 6. モックFirestoreデータベース

**責務:**
- データの永続化（オプション）
- Firestore APIの互換インターフェース
- テストデータの管理

**実装:**
- インメモリストレージ
- ファイルベースストレージ（オプション）
- コレクション/ドキュメント構造

**主要コレクション:**

```
users/
  {uid}/
    - username: string
    - email: string
    - player_level: number
    - total_xp: number
    - created_at: timestamp

tasks/
  {task_id}/
    - uid: string
    - title: string
    - description: string
    - difficulty: number
    - status: string
    - created_at: timestamp

mood_entries/
  {entry_id}/
    - uid: string
    - mood_score: number
    - timestamp: timestamp
    - notes: string

mandala_progress/
  {uid}/
    - sections_completed: array
    - total_progress: number
    - last_updated: timestamp
```

### 7. サービスマネージャー

**責務:**
- サービスのライフサイクル管理
- ヘルスチェック
- ログ収集
- プロセス監視

**実装ファイル:**
- `local_service_manager.py`
- `local_services_config.json`

**機能:**
- 並列サービス起動
- グレースフルシャットダウン
- 自動再起動（オプション）
- リソース監視

### 8. テストランナー

**責務:**
- テストスイートの実行
- カバレッジレポート生成
- テスト結果の集約

**実装ファイル:**
- `local_test_runner.py`

**サポートするテストタイプ:**
- ユニットテスト
- 統合テスト
- E2Eテスト

### 9. CLIインターフェース

**責務:**
- コマンドライン操作の提供
- ユーザーフレンドリーなインターフェース
- 自動化サポート

**実装ファイル:**
- `local_test_cli.py`

**主要コマンド:**
- `setup`: 環境セットアップ
- `start`: サービス起動
- `stop`: サービス停止
- `test`: テスト実行
- `logs`: ログ表示
- `health`: ヘルスチェック

---

## サービス間の依存関係

### 依存関係グラフ

```
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
       ├──────────────────────────────┐
       │                              │
       ▼                              ▼
┌─────────────┐              ┌─────────────┐
│Auth Service │              │Core Game    │
│             │              │Service      │
└──────┬──────┘              └──────┬──────┘
       │                            │
       │                            │
       ▼                            ▼
┌─────────────────────────────────────────┐
│         Mock Firestore Database         │
└─────────────────────────────────────────┘
       ▲                            ▲
       │                            │
       │                            │
┌──────┴──────┐              ┌──────┴──────┐
│Task Mgmt    │              │  Mandala    │
│Service      │              │  Service    │
└─────────────┘              └─────────────┘
       ▲                            ▲
       │                            │
       └────────────┬───────────────┘
                    │
             ┌──────┴──────┐
             │  Frontend   │
             └─────────────┘
```

### 依存関係マトリックス

| サービス | Auth | Core Game | Task Mgmt | Mandala | Database |
|---------|------|-----------|-----------|---------|----------|
| **Frontend** | ✓ | ✓ | ✓ | ✓ | - |
| **Auth** | - | - | - | - | ✓ |
| **Core Game** | ✓ | - | - | - | ✓ |
| **Task Mgmt** | ✓ | ✓ | - | - | ✓ |
| **Mandala** | ✓ | - | - | - | ✓ |

**凡例:**
- ✓: 依存関係あり
- -: 依存関係なし

### 起動順序

サービスは以下の順序で起動する必要があります：

1. **モックデータベース** (常に最初)
2. **認証サービス** (他のサービスが依存)
3. **コアゲームサービス**
4. **タスク管理サービス** (コアゲームサービスに依存)
5. **Mandalaサービス**
6. **フロントエンド** (すべてのバックエンドサービスに依存)


---

## データフロー

### ユーザー登録フロー

```
┌─────────┐     1. Register Request      ┌──────────┐
│ Browser │ ──────────────────────────▶ │ Frontend │
└─────────┘                              └────┬─────┘
                                              │
                                              │ 2. POST /auth/register
                                              │
                                              ▼
                                         ┌────────────┐
                                         │   Auth     │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 3. Create User
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Mock     │
                                         │ Firestore  │
                                         └─────┬──────┘
                                               │
                                               │ 4. User Created
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Auth     │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 5. JWT Token
                                               │
                                               ▼
┌─────────┐     6. Token Response       ┌──────────┐
│ Browser │ ◀────────────────────────── │ Frontend │
└─────────┘                              └──────────┘
```

### タスク完了フロー

```
┌─────────┐     1. Complete Task        ┌──────────┐
│ Browser │ ──────────────────────────▶ │ Frontend │
└─────────┘                              └────┬─────┘
                                              │
                                              │ 2. POST /api/tasks/{id}/complete
                                              │    (with JWT token)
                                              ▼
                                         ┌────────────┐
                                         │   Task     │
                                         │   Mgmt     │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 3. Verify Token
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Auth     │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 4. Token Valid
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Task     │
                                         │   Mgmt     │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 5. Update Task Status
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Mock     │
                                         │ Firestore  │
                                         └─────┬──────┘
                                               │
                                               │ 6. Calculate XP
                                               │
                                               ▼
                                         ┌────────────┐
                                         │Core Game   │
                                         │  Service   │
                                         └─────┬──────┘
                                               │
                                               │ 7. Add XP
                                               │
                                               ▼
                                         ┌────────────┐
                                         │   Mock     │
                                         │ Firestore  │
                                         └─────┬──────┘
                                               │
                                               │ 8. Response
                                               │
                                               ▼
┌─────────┐     9. Updated Data         ┌──────────┐
│ Browser │ ◀────────────────────────── │ Frontend │
└─────────┘                              └──────────┘
```

### 認証フロー

```
┌─────────┐
│ Browser │
└────┬────┘
     │
     │ 1. Login Request
     │
     ▼
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     │ 2. POST /auth/login
     │    { username, password }
     │
     ▼
┌────────────┐
│   Auth     │
│  Service   │
└─────┬──────┘
     │
     │ 3. Verify Credentials
     │
     ▼
┌────────────┐
│   Mock     │
│ Firestore  │
└─────┬──────┘
     │
     │ 4. User Found
     │
     ▼
┌────────────┐
│   Auth     │
│  Service   │
└─────┬──────┘
     │
     │ 5. Generate JWT
     │    { uid, role, exp }
     │
     ▼
┌──────────┐
│ Frontend │
└────┬─────┘
     │
     │ 6. Store Token
     │    (localStorage)
     │
     ▼
┌─────────┐
│ Browser │
└─────────┘
```

### データ同期フロー

```
┌──────────┐                    ┌────────────┐
│ Frontend │                    │   Mock     │
│          │                    │ Firestore  │
└────┬─────┘                    └─────┬──────┘
     │                                │
     │ 1. Request Data                │
     │ ──────────────────────────────▶│
     │                                │
     │                                │ 2. Query Data
     │                                │
     │ 3. Return Data                 │
     │ ◀──────────────────────────────│
     │                                │
     │ 4. Update UI                   │
     │                                │
     │ 5. User Action                 │
     │                                │
     │ 6. Update Request              │
     │ ──────────────────────────────▶│
     │                                │
     │                                │ 7. Update Data
     │                                │
     │ 8. Confirmation                │
     │ ◀──────────────────────────────│
     │                                │
     │ 9. Update UI                   │
     │                                │
```

---

## 通信プロトコル

### HTTP/REST API

すべてのサービス間通信はHTTP/RESTプロトコルを使用します。

**リクエスト形式:**
```http
POST /api/tasks HTTP/1.1
Host: localhost:8003
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "title": "新しいタスク",
  "description": "タスクの説明",
  "difficulty": 2
}
```

**レスポンス形式:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "task_id": "task_001",
  "title": "新しいタスク",
  "status": "pending",
  "created_at": "2024-10-18T10:00:00Z"
}
```

### エラーハンドリング

**標準エラーレスポンス:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "title",
      "issue": "Title is required"
    }
  }
}
```

**HTTPステータスコード:**

| コード | 意味 | 使用例 |
|-------|------|--------|
| 200 | OK | 成功 |
| 201 | Created | リソース作成成功 |
| 400 | Bad Request | 不正なリクエスト |
| 401 | Unauthorized | 認証エラー |
| 403 | Forbidden | 権限エラー |
| 404 | Not Found | リソースが見つからない |
| 500 | Internal Server Error | サーバーエラー |

### 認証・認可

**JWT トークン構造:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "uid": "user_001",
    "username": "testuser",
    "role": "user",
    "exp": 1697654400
  },
  "signature": "..."
}
```

**認証フロー:**
1. クライアントがログイン
2. サーバーがJWTトークンを発行
3. クライアントがトークンを保存
4. 以降のリクエストでトークンを送信
5. サーバーがトークンを検証

---

## セキュリティアーキテクチャ

### 認証・認可

```
┌─────────────────────────────────────────────────────────┐
│                    セキュリティ層                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐             │
│  │     JWT      │────────▶│    RBAC      │             │
│  │ Verification │         │   Middleware │             │
│  └──────────────┘         └──────────────┘             │
│         │                        │                       │
│         ▼                        ▼                       │
│  ┌──────────────────────────────────────┐              │
│  │        Protected Endpoints           │              │
│  └──────────────────────────────────────┘              │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### セキュリティ対策

1. **認証情報の保護**
   - パスワードのハッシュ化（bcrypt）
   - JWT トークンの有効期限設定
   - トークンのリフレッシュメカニズム

2. **通信の保護**
   - ローカルホストのみバインド
   - CORS設定の適切な管理
   - HTTPS（本番環境）

3. **データの保護**
   - 入力バリデーション
   - SQLインジェクション対策（NoSQL使用）
   - XSS対策

4. **アクセス制御**
   - ロールベースアクセス制御（RBAC）
   - リソースレベルの権限チェック
   - API レート制限（本番環境）

### セキュリティベストプラクティス

```python
# パスワードハッシュ化
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(plain_password)

# JWT トークン生成
import jwt
from datetime import datetime, timedelta

token = jwt.encode(
    {
        "uid": user.uid,
        "exp": datetime.utcnow() + timedelta(hours=24)
    },
    SECRET_KEY,
    algorithm="HS256"
)

# 入力バリデーション
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    description: str
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

