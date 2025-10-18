# 技術スタック

## アーキテクチャ

マイクロサービスアーキテクチャ（29サービス）を採用。各サービスは独立して動作し、疎結合・高凝集の設計原則に従う。

## フロントエンド

- **フレームワーク**: React 18 + TypeScript
- **ビルドツール**: Vite 5
- **UIライブラリ**: Material-UI (MUI) v5
- **ルーティング**: React Router v6
- **状態管理**: Context API
- **チャート**: Recharts, MUI X-Charts
- **HTTPクライアント**: Axios

## バックエンド

- **フレームワーク**: FastAPI 0.104+
- **言語**: Python 3.9+（推奨: 3.11）
- **サーバー**: Uvicorn (ASGI)
- **バリデーション**: Pydantic v2
- **認証**: JWT (PyJWT, python-jose)
- **パスワード**: Passlib with bcrypt

## データベース

- **本番**: Google Cloud Firestore
- **ローカル**: モックFirestore（インメモリ/ファイルベース）

## インフラ・デプロイ

- **クラウド**: Google Cloud Platform (GCP)
- **コンテナ**: Docker
- **CI/CD**: GitHub Actions
- **ホスティング**: Cloud Run, GitHub Pages

## 開発ツール

- **テスト**: pytest, pytest-asyncio, pytest-cov
- **フォーマット**: Black (line-length: 88)
- **リント**: flake8, ESLint
- **型チェック**: mypy, TypeScript

## 共通コマンド

### 環境セットアップ
```bash
# Python依存関係
pip install -r requirements.txt

# フロントエンド依存関係
cd frontend
npm install
```

### 開発サーバー起動
```bash
# すべてのサービスを起動
python start_mvp_services.py

# フロントエンド開発サーバー
cd frontend
npm run dev
```

### テスト実行
```bash
# Pytestでバックエンドテスト
pytest

# カバレッジ付き
pytest --cov=services --cov=shared

# 特定のマーカー
pytest -m unit
pytest -m integration
pytest -m e2e

# フロントエンド型チェック
cd frontend
npm run type-check
```

### ビルド
```bash
# フロントエンドビルド
cd frontend
npm run build
```

### ローカルテスト環境
```bash
# CLIを使用
python local_test_cli.py setup
python local_test_cli.py start
python local_test_cli.py test
python local_test_cli.py stop
```

## ポート割り当て

- **3000**: フロントエンド (Vite Dev Server)
- **8001**: Core Game Service
- **8002**: Auth Service
- **8003**: Task Management Service
- **8004**: Mandala Service
- **8005+**: その他のマイクロサービス

## コーディング規約

- Python: PEP 8準拠、Black自動フォーマット
- TypeScript: ESLint設定に従う
- 関数・クラスには型ヒントを必須とする
- テストは各サービスディレクトリ内に配置（`test_*.py`）
