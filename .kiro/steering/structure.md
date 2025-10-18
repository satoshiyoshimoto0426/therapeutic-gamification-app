# プロジェクト構造

## ディレクトリ構成

```
therapeutic-gamification-app/
├── services/              # マイクロサービス（29サービス）
│   ├── auth/             # 認証サービス（JWT、RBAC）
│   ├── core-game/        # コアゲームロジック（XP、レベル、共鳴）
│   ├── task-mgmt/        # タスク管理（ポモドーロ統合）
│   ├── mandala/          # Mandala進捗管理
│   ├── mood-tracking/    # ムード追跡
│   ├── ai-story/         # AI物語生成
│   ├── story-dag/        # ストーリーDAG管理
│   ├── adhd-support/     # ADHD支援機能
│   ├── therapeutic-safety/ # 治療安全性（CBT介入）
│   ├── guardian-portal/  # 保護者ポータル
│   ├── line-bot/         # LINEボット統合
│   ├── rpg-economy/      # RPG経済（ガチャ、装備、コイン）
│   ├── job-system/       # ジョブシステム
│   ├── inner-demon-battle/ # 内なる悪魔バトル
│   ├── seasonal-events/  # 季節イベント
│   ├── integration/      # サービス統合テスト
│   ├── performance-monitoring/ # パフォーマンス監視
│   ├── kpi-dashboard/    # KPIダッシュボード
│   ├── gdpr-compliance/  # GDPR準拠
│   ├── alpha-playtest/   # アルファプレイテスト
│   ├── edge-ai-cache/    # エッジAIキャッシュ
│   ├── growth-note/      # 成長ノート
│   ├── micro-rewards/    # マイクロリワード
│   ├── self-efficacy/    # 自己効力感
│   ├── daily-trio/       # デイリートリオ
│   ├── cbt-integration/  # CBT統合
│   ├── feature-flags/    # 機能フラグ
│   ├── task-story-integration/ # タスク・ストーリー統合
│   └── auto-deployment/  # 自動デプロイメント
├── shared/               # 共有コード
│   ├── config/          # 設定（Firestore、依存関係）
│   ├── interfaces/      # 共通インターフェース・型定義
│   ├── middleware/      # 共通ミドルウェア（RBAC等）
│   ├── repositories/    # データアクセス層（Repository Pattern）
│   ├── utils/           # ユーティリティ関数
│   └── tests/           # 共有コードのテスト
├── frontend/            # Reactフロントエンド
│   ├── src/
│   │   ├── components/  # UIコンポーネント
│   │   │   ├── dashboard/
│   │   │   ├── task/
│   │   │   ├── gamification/
│   │   │   ├── adhd/    # ADHD支援UI
│   │   │   ├── kpi/     # KPIダッシュボード
│   │   │   └── common/
│   │   ├── contexts/    # Context API
│   │   ├── pages/       # ページコンポーネント
│   │   └── App.tsx
│   ├── components/      # レガシーコンポーネント
│   ├── package.json
│   └── vite.config.ts
├── infrastructure/      # インフラコード
│   └── production/      # 本番環境設定
├── docs/               # ドキュメント
├── test_results/       # テスト結果
├── .github/            # GitHub Actions
│   └── workflows/
├── .kiro/              # Kiro設定
│   ├── specs/          # 仕様書
│   └── steering/       # ステアリングルール
├── requirements.txt    # Python依存関係
├── pyproject.toml      # Pythonプロジェクト設定
├── Dockerfile          # Dockerイメージ
├── README.md           # プロジェクトREADME
└── ARCHITECTURE.md     # アーキテクチャドキュメント
```

## サービス構造パターン

各マイクロサービスは以下の標準構造に従う：

```
services/<service-name>/
├── main.py              # FastAPIアプリケーション（エントリーポイント）
├── <feature>_system.py  # ビジネスロジック
├── test_<feature>.py    # ユニット・統合テスト
├── simple_test.py       # 簡易テスト（オプション）
├── validate_implementation.py # 実装検証（オプション）
└── README.md            # サービス固有のドキュメント
```

## 共有コード構造

### interfaces/
型定義、データモデル、バリデーションロジック。TypeScriptとPythonの両方で使用可能な共通インターフェース。

### repositories/
Repository Patternを使用したデータアクセス層。Firestoreとの通信を抽象化。

### middleware/
認証、RBAC、ロギングなどの横断的関心事。

## 命名規則

- **ファイル**: スネークケース（`task_system.py`）
- **クラス**: パスカルケース（`TaskSystem`）
- **関数・変数**: スネークケース（`get_user_tasks`）
- **定数**: 大文字スネークケース（`MAX_RETRY_COUNT`）
- **テストファイル**: `test_`プレフィックス（`test_auth.py`）
- **TypeScript**: キャメルケース（変数・関数）、パスカルケース（コンポーネント・型）

## 重要な設定ファイル

- `pyproject.toml`: Pythonプロジェクト設定、pytest設定、mypy設定
- `requirements.txt`: Python依存関係
- `frontend/package.json`: フロントエンド依存関係
- `frontend/vite.config.ts`: Vite設定（プロキシ、ビルド）
- `local_services_config.json`: ローカルサービス設定
- `.env.local`: ローカル環境変数
- `.env.production.template`: 本番環境変数テンプレート

## テスト配置

- サービス固有のテスト: `services/<service>/test_*.py`
- 共有コードのテスト: `shared/tests/test_*.py`
- 統合テスト: `services/integration/test_*.py`
- E2Eテスト: ルートディレクトリの`test_*_e2e.py`
- テスト結果: `test_results/`ディレクトリに保存
