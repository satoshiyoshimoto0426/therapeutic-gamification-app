# Authentication Service

## 概要

Guardian/Support System Portal用の認証・認可サービスです。RBAC（Role-Based Access Control）権限システムとJWT認証を統合し、3つの権限レベルによる細かなアクセス制御を提供します。

## 実装された機能

### RBAC権限システム
- **3つの権限レベル**: view-only、task-edit、chat-send
- **リソースベースアクセス制御**: 8種類のリソースタイプに対する細かな権限管理
- **期限付きロール**: 有効期限設定と自動クリーンアップ
- **複数保護者対応**: 1ユーザーに対する複数保護者の権限管理

### JWT認証システム
- **セキュアなトークン**: HS256アルゴリズムによる署名
- **自動期限管理**: 24時間の有効期限と自動検証
- **トークン検証**: 改ざん検出と期限切れチェック

### APIエンドポイント

#### 認証関連
- **POST /auth/guardian/login**: 保護者ログイン
- **POST /auth/guardian/grant**: アクセス権限付与
- **POST /auth/guardian/revoke**: アクセス権限取り消し

#### 権限管理
- **POST /auth/permission/check**: 権限チェック
- **GET /auth/guardian/{guardian_id}/users**: 保護者が管理するユーザー一覧
- **GET /auth/user/{user_id}/guardians**: ユーザーの保護者一覧

#### 認証済みエンドポイント
- **GET /auth/me**: 現在の保護者情報取得
- **GET /auth/permissions/summary**: 権限サマリー取得

#### システム管理
- **GET /auth/system/roles**: システムロール一覧
- **POST /auth/system/cleanup**: 期限切れロールクリーンアップ

## 権限レベル詳細

### View-Only（閲覧のみ）
**対象**: 親、家族など
**許可される操作**:
- ユーザープロファイル閲覧
- 進捗データ閲覧
- レポート閲覧
- Mandalaグリッド閲覧
- 気分データ閲覧

### Task-Edit（タスク編集）
**対象**: カウンセラー、教師など
**許可される操作**:
- View-Onlyの全機能
- タスクデータ編集
- Mandalaグリッド編集

### Chat-Send（フルアクセス）
**対象**: 支援員、専門スタッフなど
**許可される操作**:
- Task-Editの全機能
- チャットメッセージ送信
- ストーリーデータ閲覧

## データモデル

### Permission（権限）
```python
@dataclass
class Permission:
    resource_type: ResourceType  # リソースタイプ
    actions: Set[Action]         # 許可されたアクション
    conditions: Dict[str, Any]   # 条件（オプション）
```

### Role（ロール）
```python
@dataclass
class Role:
    name: str                           # ロール名
    permission_level: PermissionLevel   # 権限レベル
    permissions: List[Permission]       # 権限リスト
    description: str                    # 説明
    is_active: bool                     # アクティブ状態
```

### UserRole（ユーザーロール）
```python
@dataclass
class UserRole:
    user_id: str            # ユーザーID
    guardian_id: str        # 保護者ID
    role: Role             # ロール
    granted_by: str        # 権限付与者
    granted_at: datetime   # 付与日時
    expires_at: datetime   # 有効期限（オプション）
    is_active: bool        # アクティブ状態
```

## リソースタイプ

- **USER_PROFILE**: ユーザープロファイル
- **TASK_DATA**: タスクデータ
- **PROGRESS_DATA**: 進捗データ
- **CHAT_MESSAGES**: チャットメッセージ
- **REPORTS**: レポート
- **MANDALA_GRID**: Mandalaグリッド
- **STORY_DATA**: ストーリーデータ
- **MOOD_DATA**: 気分データ

## アクション

- **READ**: 読み取り
- **WRITE**: 書き込み
- **DELETE**: 削除
- **EXECUTE**: 実行

## 使用例

### 保護者アクセス権限付与
```python
# カウンセラーにタスク編集権限を付与
grant_request = {
    "user_id": "student_001",
    "guardian_id": "counselor_001",
    "permission_level": "task-edit",
    "granted_by": "school_admin",
    "expires_at": "2024-12-31T23:59:59"
}

response = requests.post("/auth/guardian/grant", json=grant_request)
```

### 保護者ログイン
```python
# カウンセラーとしてログイン
login_request = {
    "guardian_id": "counselor_001",
    "user_id": "student_001",
    "permission_level": "task-edit"
}

response = requests.post("/auth/guardian/login", json=login_request)
access_token = response.json()["access_token"]
```

### 認証済みAPIアクセス
```python
# 認証ヘッダーを設定
headers = {"Authorization": f"Bearer {access_token}"}

# 保護者情報取得
response = requests.get("/auth/me", headers=headers)
```

### 権限チェック
```python
# タスク編集権限をチェック
check_request = {
    "guardian_id": "counselor_001",
    "user_id": "student_001",
    "resource_type": "task_data",
    "action": "write"
}

response = requests.post("/auth/permission/check", json=check_request)
has_permission = response.json()["has_permission"]
```

## セキュリティ機能

### JWT トークンセキュリティ
- **署名検証**: HS256アルゴリズムによる改ざん検出
- **有効期限**: 24時間の自動期限切れ
- **トークンタイプ検証**: guardian_accessタイプのみ受け入れ

### アクセス制御
- **最小権限の原則**: 必要最小限の権限のみ付与
- **期限管理**: 自動期限切れとクリーンアップ
- **監査ログ**: 権限付与・取り消しの記録

### エラーハンドリング
- **401 Unauthorized**: 認証失敗
- **403 Forbidden**: 権限不足
- **422 Unprocessable Entity**: 入力データエラー
- **500 Internal Server Error**: システムエラー

## テスト

### 単体テスト
- **RBAC権限システム**: `shared/tests/test_rbac_system.py`
- **権限チェック**: 各権限レベルの動作確認
- **期限切れロール**: 自動クリーンアップ機能

### 統合テスト
- **認証API**: `services/auth/test_auth.py`
- **エンドツーエンド**: ログインから権限チェックまで
- **エラーケース**: 無効なトークン、権限不足など

### 実装検証
- **システム検証**: `services/auth/validate_implementation.py`
- **パフォーマンステスト**: 大量データでの動作確認
- **堅牢性テスト**: 異常ケースでの動作確認

## 設定

### 環境変数
```bash
# JWT秘密鍵（本番環境では必ず変更）
JWT_SECRET_KEY=your-secret-key-change-in-production

# JWT有効期限（時間）
JWT_EXPIRATION_HOURS=24
```

### CORS設定
```python
# 本番環境では適切なオリジンを設定
allow_origins=["https://your-domain.com"]
```

## 要件対応

### Requirement 6.1: Guardian/Support System Portal
✅ 3つの権限レベル（view-only、task-edit、chat-send）実装
✅ RBAC権限システム実装
✅ ユーザー権限チェック機能実装
✅ 権限ベースのアクセス制御実装

## 使用技術

- **FastAPI**: REST API実装
- **PyJWT**: JWT認証
- **Pydantic**: データバリデーション
- **Python Dataclasses**: データモデル
- **CORS Middleware**: クロスオリジン対応

## 次のステップ

1. **Supabase Auth統合**: SAML、Magic Link認証
2. **データベース永続化**: Firestore統合
3. **監査ログ**: 権限変更の記録
4. **レート制限**: API使用量制限
5. **本番環境設定**: セキュリティ強化