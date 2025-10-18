# ローカルテスト環境セットアップ - 設計ドキュメント

## 概要

このドキュメントは、治療的ゲーミフィケーションアプリをローカル環境でテストするための包括的な設計を定義します。開発者が最小限の手動設定で、フルスタックアプリケーションをローカルで起動し、テストできる環境を提供します。

## アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                    ローカルテスト環境                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────────────────┐      │
│  │  セットアップ  │────────▶│  環境変数・設定ファイル    │      │
│  │  スクリプト    │         └──────────────────────────┘      │
│  └──────────────┘                                            │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │           依存関係インストール                      │       │
│  │  • Python (requirements.txt)                     │       │
│  │  • Node.js (package.json)                        │       │
│  └──────────────────────────────────────────────────┘       │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │         モックデータベース初期化                    │       │
│  │  • インメモリFirestore                             │       │
│  │  • サンプルデータロード                             │       │
│  └──────────────────────────────────────────────────┘       │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              サービス起動                             │    │
│  │                                                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │  Auth    │  │Core Game │  │Task Mgmt │          │    │
│  │  │  :8002   │  │  :8001   │  │  :8003   │  ...     │    │
│  │  └──────────┘  └──────────┘  └──────────┘          │    │
│  │                                                       │    │
│  │  ┌──────────────────────────────────────┐           │    │
│  │  │      Frontend Dev Server             │           │    │
│  │  │         :3000                         │           │    │
│  │  └──────────────────────────────────────┘           │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │           テスト実行                                │       │
│  │  • ユニットテスト                                   │       │
│  │  • 統合テスト                                      │       │
│  │  • E2Eテスト                                       │       │
│  └──────────────────────────────────────────────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## コンポーネントと インターフェース

### 1. セットアップスクリプト (`local_test_setup.py`)

#### 責務
- 環境の検証と準備
- 依存関係のインストール
- 設定ファイルの生成
- モックデータベースの初期化

#### インターフェース

```python
class LocalTestSetup:
    def check_prerequisites() -> Dict[str, bool]:
        """必要なツールの存在確認"""
        
    def install_dependencies() -> bool:
        """Python/Node.js依存関係のインストール"""
        
    def generate_env_file() -> bool:
        """環境変数ファイルの生成"""
        
    def initialize_mock_database() -> bool:
        """モックデータベースの初期化"""
        
    def run_setup() -> bool:
        """全セットアップ処理の実行"""
```

### 2. モックデータベースマネージャー (`mock_database.py`)

#### 責務
- Firestoreのモック実装
- テストデータの管理
- データの永続化（オプション）

#### インターフェース

```python
class MockFirestoreClient:
    def __init__(self, persist_data: bool = False):
        """初期化"""
        
    def collection(self, name: str) -> MockCollection:
        """コレクション取得"""
        
    def load_sample_data(self, data_file: str) -> bool:
        """サンプルデータのロード"""
        
    def clear_all_data() -> bool:
        """全データのクリア"""
        
    def export_data(self, output_file: str) -> bool:
        """データのエクスポート"""

class MockCollection:
    def document(self, doc_id: str) -> MockDocument:
        """ドキュメント取得"""
        
    def add(self, data: Dict) -> MockDocument:
        """ドキュメント追加"""
        
    def stream() -> Iterator[MockDocument]:
        """全ドキュメント取得"""

class MockDocument:
    def get() -> MockDocumentSnapshot:
        """ドキュメント取得"""
        
    def set(self, data: Dict) -> None:
        """ドキュメント設定"""
        
    def update(self, data: Dict) -> None:
        """ドキュメント更新"""
        
    def delete() -> None:
        """ドキュメント削除"""
```

### 3. サービスマネージャー (`local_service_manager.py`)

#### 責務
- マイクロサービスの起動・停止
- ヘルスチェック
- ログ管理

#### インターフェース

```python
class LocalServiceManager:
    def __init__(self, services_config: Dict):
        """サービス設定の読み込み"""
        
    def start_service(self, service_name: str) -> bool:
        """個別サービスの起動"""
        
    def start_all_services() -> Dict[str, bool]:
        """全サービスの起動"""
        
    def stop_service(self, service_name: str) -> bool:
        """個別サービスの停止"""
        
    def stop_all_services() -> bool:
        """全サービスの停止"""
        
    def check_service_health(self, service_name: str) -> Dict:
        """サービスヘルスチェック"""
        
    def get_service_logs(self, service_name: str, lines: int = 50) -> List[str]:
        """サービスログの取得"""
        
    def restart_service(self, service_name: str) -> bool:
        """サービスの再起動"""
```

### 4. テストランナー (`local_test_runner.py`)

#### 責務
- テストスイートの実行
- テスト結果の集約
- カバレッジレポートの生成

#### インターフェース

```python
class LocalTestRunner:
    def run_unit_tests(self, pattern: str = "test_*.py") -> TestResult:
        """ユニットテストの実行"""
        
    def run_integration_tests() -> TestResult:
        """統合テストの実行"""
        
    def run_e2e_tests() -> TestResult:
        """E2Eテストの実行"""
        
    def run_all_tests() -> TestSummary:
        """全テストの実行"""
        
    def generate_coverage_report(self, output_dir: str) -> bool:
        """カバレッジレポートの生成"""

class TestResult:
    passed: int
    failed: int
    skipped: int
    errors: List[str]
    duration: float

class TestSummary:
    unit_tests: TestResult
    integration_tests: TestResult
    e2e_tests: TestResult
    total_coverage: float
```

## データモデル

### 環境設定 (`.env.local`)

```bash
# データベース設定
USE_MOCK_DATABASE=true
MOCK_DATABASE_PERSIST=false
MOCK_DATABASE_FILE=./data/mock_firestore.json

# サービスポート設定
AUTH_SERVICE_PORT=8002
CORE_GAME_SERVICE_PORT=8001
TASK_MGMT_SERVICE_PORT=8003
MANDALA_SERVICE_PORT=8004
MOOD_TRACKING_SERVICE_PORT=8005

# フロントエンド設定
FRONTEND_PORT=3000
API_BASE_URL=http://localhost:8001

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=./logs/local_test.log

# テスト設定
TEST_DATA_DIR=./test_data
ENABLE_TEST_FIXTURES=true
```

### サービス設定 (`local_services_config.json`)

```json
{
  "services": [
    {
      "name": "auth",
      "path": "services/auth",
      "port": 8002,
      "command": "uvicorn main:app --host 0.0.0.0 --port 8002 --reload",
      "health_endpoint": "/health",
      "required": true,
      "startup_timeout": 10
    },
    {
      "name": "core-game",
      "path": "services/core-game",
      "port": 8001,
      "command": "uvicorn main:app --host 0.0.0.0 --port 8001 --reload",
      "health_endpoint": "/health",
      "required": true,
      "startup_timeout": 10
    },
    {
      "name": "task-mgmt",
      "path": "services/task-mgmt",
      "port": 8003,
      "command": "uvicorn main:app --host 0.0.0.0 --port 8003 --reload",
      "health_endpoint": "/health",
      "required": true,
      "startup_timeout": 10
    },
    {
      "name": "mandala",
      "path": "services/mandala",
      "port": 8004,
      "command": "uvicorn main:app --host 0.0.0.0 --port 8004 --reload",
      "health_endpoint": "/health",
      "required": false,
      "startup_timeout": 10
    }
  ],
  "frontend": {
    "path": "frontend",
    "port": 3000,
    "command": "npm run dev",
    "required": true,
    "startup_timeout": 30
  }
}
```

### サンプルデータ (`test_data/sample_data.json`)

```json
{
  "users": [
    {
      "uid": "test_user_001",
      "username": "テストユーザー1",
      "email": "test1@example.com",
      "created_at": "2024-01-01T00:00:00Z",
      "player_level": 5,
      "total_xp": 150,
      "yu_level": 3
    }
  ],
  "tasks": [
    {
      "task_id": "task_001",
      "uid": "test_user_001",
      "title": "サンプルタスク",
      "description": "テスト用のタスク",
      "difficulty": 2,
      "status": "pending",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "mood_entries": [
    {
      "entry_id": "mood_001",
      "uid": "test_user_001",
      "mood_score": 4,
      "timestamp": "2024-01-01T12:00:00Z",
      "notes": "良い気分"
    }
  ]
}
```

## エラーハンドリング

### エラーカテゴリ

1. **環境エラー**
   - Python/Node.jsが見つからない
   - バージョン不一致
   - 権限エラー

2. **依存関係エラー**
   - パッケージインストール失敗
   - 互換性の問題

3. **サービス起動エラー**
   - ポート競合
   - 設定ファイル不正
   - サービスクラッシュ

4. **データベースエラー**
   - データロード失敗
   - データ形式エラー

### エラーハンドリング戦略

```python
class SetupError(Exception):
    """セットアップエラーの基底クラス"""
    def __init__(self, message: str, recovery_hint: str = None):
        self.message = message
        self.recovery_hint = recovery_hint
        super().__init__(self.message)

class EnvironmentError(SetupError):
    """環境関連エラー"""
    pass

class DependencyError(SetupError):
    """依存関係エラー"""
    pass

class ServiceError(SetupError):
    """サービス起動エラー"""
    pass

def handle_setup_error(error: SetupError) -> None:
    """エラーハンドリングと復旧提案"""
    print(f"❌ エラー: {error.message}")
    if error.recovery_hint:
        print(f"💡 解決方法: {error.recovery_hint}")
```

## テスト戦略

### テストレベル

1. **ユニットテスト**
   - 各サービスの個別機能テスト
   - モックを使用した独立テスト
   - 高速実行

2. **統合テスト**
   - サービス間連携テスト
   - API呼び出しテスト
   - データフローテスト

3. **E2Eテスト**
   - ユーザージャーニー全体テスト
   - フロントエンド + バックエンド
   - 実際のユースケース

### テスト実行フロー

```
1. 環境セットアップ
   ↓
2. モックデータベース初期化
   ↓
3. サービス起動
   ↓
4. ユニットテスト実行
   ↓
5. 統合テスト実行
   ↓
6. E2Eテスト実行
   ↓
7. レポート生成
   ↓
8. クリーンアップ
```

## セキュリティ考慮事項

1. **認証情報の管理**
   - `.env.local`はgitignoreに追加
   - テスト用の固定トークン使用
   - 本番環境の認証情報は使用しない

2. **ポートセキュリティ**
   - ローカルホストのみバインド
   - ファイアウォール設定の確認

3. **データ保護**
   - テストデータは匿名化
   - 個人情報を含まない

## パフォーマンス最適化

1. **並列起動**
   - 独立したサービスは並列起動
   - 起動時間の短縮

2. **キャッシング**
   - 依存関係のキャッシュ
   - ビルド成果物のキャッシュ

3. **リソース管理**
   - メモリ使用量の監視
   - 不要なサービスの停止

## 開発者体験の向上

### CLIインターフェース

```bash
# セットアップ
python local_test_setup.py setup

# サービス起動
python local_test_setup.py start [service_name]

# サービス停止
python local_test_setup.py stop [service_name]

# テスト実行
python local_test_setup.py test [unit|integration|e2e|all]

# ヘルスチェック
python local_test_setup.py health

# ログ表示
python local_test_setup.py logs [service_name]

# クリーンアップ
python local_test_setup.py cleanup
```

### インタラクティブモード

```python
class InteractiveMode:
    """対話的なセットアップモード"""
    
    def run(self):
        """インタラクティブセットアップの実行"""
        print("🎮 ローカルテスト環境セットアップ")
        print("=" * 50)
        
        # 1. 環境確認
        self.check_environment()
        
        # 2. サービス選択
        services = self.select_services()
        
        # 3. 設定確認
        self.confirm_settings()
        
        # 4. セットアップ実行
        self.execute_setup(services)
        
        # 5. 完了メッセージ
        self.show_completion_message()
```

## ドキュメント構成

### README_LOCAL_TEST.md

```markdown
# ローカルテスト環境セットアップガイド

## クイックスタート

1. セットアップ実行
   ```bash
   python local_test_setup.py setup
   ```

2. サービス起動
   ```bash
   python local_test_setup.py start
   ```

3. ブラウザでアクセス
   ```
   http://localhost:3000
   ```

## 詳細ガイド

### 前提条件
- Python 3.9以上
- Node.js 16以上
- 8GB以上のRAM

### トラブルシューティング
...
```

## 実装の優先順位

1. **Phase 1: 基本セットアップ**
   - セットアップスクリプト
   - 環境変数管理
   - 依存関係インストール

2. **Phase 2: モックデータベース**
   - Firestoreモック実装
   - サンプルデータロード

3. **Phase 3: サービス管理**
   - サービス起動・停止
   - ヘルスチェック

4. **Phase 4: テスト統合**
   - テストランナー
   - レポート生成

5. **Phase 5: 開発者体験**
   - CLIインターフェース
   - インタラクティブモード
   - ドキュメント
