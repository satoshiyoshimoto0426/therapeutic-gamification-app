# 自動デプロイメントシステム

治療的ゲーミフィケーションアプリの包括的な自動デプロイメント機能を提供します。

## 🎯 概要

このシステムは、アプリケーションの自動デプロイメント、監視、ロールバック機能を提供する包括的なソリューションです。開発者が単一のコマンドで安全かつ確実にアプリケーションをデプロイできるように設計されています。

## 🚀 主な機能

### ✨ コア機能
- **ワンクリックデプロイ**: 単一コマンドでの完全自動デプロイメント
- **環境管理**: 開発・ステージング・本番環境の自動設定
- **デプロイメント戦略**: Blue-Green、Rolling Update、Canaryデプロイメント対応
- **リアルタイム監視**: デプロイメント進行状況のリアルタイム追跡

### 🛡️ 安全性機能
- **事前検証**: コード品質、セキュリティ、依存関係の自動チェック
- **ヘルスモニタリング**: デプロイ後の自動ヘルスチェック
- **自動ロールバック**: 問題検出時の自動復旧機能
- **段階的デプロイ**: トラフィックの段階的移行

### 📊 監視・通知
- **構造化ログ**: JSON形式での詳細ログ出力
- **通知システム**: Slack、メール、ダッシュボード連携
- **メトリクス収集**: パフォーマンスと成功率の追跡
- **監査ログ**: 全デプロイメント活動の記録

## 📦 インストール

### 前提条件
- Python 3.11以上
- Google Cloud CLI (gcloud)
- Docker
- Git

### セットアップ
```bash
# 依存関係のインストール
pip install -r requirements.txt

# Google Cloud認証
gcloud auth login
gcloud auth application-default login

# プロジェクト設定
gcloud config set project your-project-id
```

## 🎮 使用方法

### 基本的なデプロイメント
```bash
# 開発環境へのデプロイ
python -m services.auto-deployment.cli deploy -e development

# ステージング環境へのデプロイ
python -m services.auto-deployment.cli deploy -e staging

# 本番環境へのデプロイ
python -m services.auto-deployment.cli deploy -e production
```

### 高度なオプション
```bash
# Blue-Greenデプロイメント戦略を指定
python -m services.auto-deployment.cli deploy -e production -s blue_green

# ドライランモード（実際のデプロイは実行しない）
python -m services.auto-deployment.cli deploy -e staging --dry-run

# 設定ファイルを指定
python -m services.auto-deployment.cli deploy -e production -c config.yaml
```

### 状態確認
```bash
# 全体の状態確認
python -m services.auto-deployment.cli status

# 特定環境の状態確認
python -m services.auto-deployment.cli status -e production

# 特定デプロイメントの状態確認
python -m services.auto-deployment.cli status --deployment-id abc123
```

### ロールバック
```bash
# 前回の安定版にロールバック
python -m services.auto-deployment.cli rollback -e production

# 特定のリビジョンにロールバック
python -m services.auto-deployment.cli rollback -e production --revision abc123
```

### 設定確認
```bash
# 現在の設定を表示
python -m services.auto-deployment.cli config

# JSON形式で設定を出力
python -m services.auto-deployment.cli config --output-format json
```

### 事前検証
```bash
# デプロイメント前の検証
python -m services.auto-deployment.cli validate

# 特定環境の検証
python -m services.auto-deployment.cli validate -e production
```

## ⚙️ 設定

### 環境変数
```bash
# Google Cloud設定
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="asia-northeast1"
export SERVICE_NAME="therapeutic-gamification-app"

# 通知設定
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."

# セキュリティ設定
export MIN_TEST_COVERAGE="0.8"

# ログ設定
export LOG_LEVEL="INFO"
```

### 設定ファイル例
```yaml
# config.yaml
environment: production
strategy: blue_green

cloud_config:
  project_id: "therapeutic-gamification-app-prod"
  region: "asia-northeast1"
  service_name: "therapeutic-gamification-app"
  memory: "2Gi"
  cpu: "2"
  min_instances: 5
  max_instances: 1000

health_check_config:
  endpoints:
    - "/health"
    - "/api/health"
  timeout_seconds: 30
  success_threshold: 0.95

notification_config:
  slack_webhook_url: "https://hooks.slack.com/..."
  email_recipients:
    - "admin@example.com"

security_config:
  enable_security_scan: true
  min_test_coverage: 0.9
```

## 🏗️ アーキテクチャ

### コンポーネント構成
```
services/auto-deployment/
├── __init__.py              # パッケージ初期化
├── config.py                # 設定管理
├── exceptions.py            # 例外定義
├── logging_config.py        # ログ設定
├── orchestrator.py          # メインオーケストレータ
├── cli.py                   # CLIインターフェース
├── test_orchestrator.py     # テストファイル
└── README.md               # このファイル
```

### 主要クラス
- **DeploymentOrchestrator**: デプロイメントの中央制御
- **DeploymentConfig**: 設定管理
- **DeploymentResult**: デプロイメント結果
- **DeploymentStep**: 個別デプロイメントステップ

## 🧪 テスト

### テスト実行
```bash
# 全テストの実行
pytest services/auto-deployment/test_orchestrator.py -v

# 特定のテストクラスを実行
pytest services/auto-deployment/test_orchestrator.py::TestDeploymentOrchestrator -v

# カバレッジ付きでテスト実行
pytest services/auto-deployment/test_orchestrator.py --cov=services.auto-deployment
```

### テストカテゴリ
- **単体テスト**: 個別コンポーネントのテスト
- **統合テスト**: コンポーネント間の連携テスト
- **エンドツーエンドテスト**: 完全なデプロイメントフローのテスト

## 📊 監視とログ

### ログ形式
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "auto_deployment.deployment",
  "message": "デプロイメントステップ: build_and_deploy - completed",
  "deployment_id": "abc123-def456",
  "step": "build_and_deploy",
  "status": "completed"
}
```

### メトリクス
- デプロイメント成功率
- デプロイメント時間
- ロールバック頻度
- ヘルスチェック成功率

## 🔧 トラブルシューティング

### よくある問題

#### 1. 認証エラー
```bash
ERROR: Your current active account does not have any valid credentials
```
**解決方法**:
```bash
gcloud auth login
gcloud auth application-default login
```

#### 2. API未有効化エラー
```bash
ERROR: API [run.googleapis.com] not enabled
```
**解決方法**:
```bash
gcloud services enable run.googleapis.com
```

#### 3. 権限エラー
```bash
ERROR: does not have permission to access
```
**解決方法**: 必要なIAMロールを確認・付与

### ログ確認
```bash
# デプロイメントログの確認
tail -f deployment.log

# Google Cloud Logsの確認
gcloud logs read "resource.type=cloud_run_revision" --limit=50
```

## 🤝 開発・貢献

### 開発環境セットアップ
```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# pre-commitフックの設定
pre-commit install

# テスト実行
pytest
```

### コード品質
- **フォーマッター**: Black
- **リンター**: Flake8, Pylint
- **型チェック**: MyPy
- **テストカバレッジ**: 最低85%

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 🆘 サポート

問題が発生した場合:
1. [トラブルシューティング](#-トラブルシューティング)を確認
2. ログファイルを確認
3. GitHub Issuesで報告

---

**🎯 自動デプロイメントシステムで、安全で確実なデプロイメントを実現しましょう！**