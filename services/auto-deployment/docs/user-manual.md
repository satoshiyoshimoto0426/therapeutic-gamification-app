# Auto-Deployment System User Manual

## 概要

Auto-Deployment Systemは、治療的ゲーミフィケーションアプリケーションのための包括的な自動デプロイメントシステムです。このシステムは、ワンクリックでプロダクション環境への安全で信頼性の高いデプロイメントを可能にします。

## 主な機能

- **自動化されたデプロイメント**: 単一のコマンドで完全なデプロイメントプロセスを実行
- **事前検証**: コード品質、セキュリティ、依存関係の自動チェック
- **環境管理**: 開発、ステージング、プロダクション環境の自動設定
- **ヘルスモニタリング**: デプロイメント中およびデプロイメント後の継続的な監視
- **自動ロールバック**: 問題検出時の自動復旧機能
- **通知システム**: Slack、メール、ダッシュボードでのリアルタイム更新

## システム要件

### 前提条件

- Python 3.8以上
- Google Cloud SDK
- Docker
- Git
- GitHub CLI (推奨)

### 必要な権限

- Google Cloud Project Owner または Editor権限
- GitHub repository への書き込み権限
- Cloud Run、Firestore、Secret Manager へのアクセス権限

## インストールとセットアップ

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd your-project-directory

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. Google Cloud認証の設定

```bash
# Google Cloud SDKにログイン
gcloud auth login

# アプリケーションデフォルト認証を設定
gcloud auth application-default login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID
```

### 3. 環境設定

```bash
# 設定ファイルをコピー
cp services/auto-deployment/config/config.example.yaml services/auto-deployment/config/config.yaml

# 設定ファイルを編集
nano services/auto-deployment/config/config.yaml
```

## 基本的な使用方法

### デプロイメントの実行

#### 1. 基本的なデプロイメント

```bash
# プロダクション環境へのデプロイ
python -m services.auto_deployment.cli deploy --environment production

# ステージング環境へのデプロイ
python -m services.auto_deployment.cli deploy --environment staging
```

#### 2. 詳細オプション付きデプロイメント

```bash
# 詳細ログ付きでデプロイ
python -m services.auto_deployment.cli deploy --environment production --verbose

# 特定のサービスのみデプロイ
python -m services.auto_deployment.cli deploy --environment production --services auth,core-game

# ドライランモード（実際のデプロイは行わない）
python -m services.auto_deployment.cli deploy --environment production --dry-run
```

### デプロイメント状況の確認

```bash
# 現在のデプロイメント状況を確認
python -m services.auto_deployment.cli status

# 詳細な状況を確認
python -m services.auto_deployment.cli status --detailed

# 特定のサービスの状況を確認
python -m services.auto_deployment.cli status --service auth
```

### ロールバック

```bash
# 最新の安定版にロールバック
python -m services.auto_deployment.cli rollback

# 特定のリビジョンにロールバック
python -m services.auto_deployment.cli rollback --revision REVISION_NAME

# 特定のサービスのみロールバック
python -m services.auto_deployment.cli rollback --service auth
```

## 設定ガイド

### 基本設定

`services/auto-deployment/config/config.yaml`ファイルで基本設定を行います：

```yaml
# プロジェクト設定
project:
  id: "your-project-id"
  region: "asia-northeast1"

# デプロイメント設定
deployment:
  strategy: "blue-green"  # blue-green, rolling, canary
  timeout: 1800  # 30分
  
# 通知設定
notifications:
  slack:
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#deployments"
  email:
    smtp_server: "smtp.gmail.com"
    recipients: ["admin@example.com"]

# ヘルスチェック設定
health_checks:
  endpoints: ["/health", "/api/health"]
  timeout: 30
  retry_attempts: 3
```

### 環境別設定

各環境（development、staging、production）に対して個別の設定が可能です：

```yaml
environments:
  production:
    min_instances: 2
    max_instances: 100
    memory: "2Gi"
    cpu: "2"
    
  staging:
    min_instances: 1
    max_instances: 10
    memory: "1Gi"
    cpu: "1"
```

### セキュリティ設定

```yaml
security:
  enable_vulnerability_scan: true
  min_test_coverage: 0.8
  require_approval_for_production: true
  allowed_deployers: ["user1@example.com", "user2@example.com"]
```

## 高度な機能

### カスタムバリデーター

独自の検証ロジックを追加できます：

```python
from services.auto_deployment.validation.base import BaseValidator

class CustomValidator(BaseValidator):
    def validate(self, context):
        # カスタム検証ロジック
        if not self.check_custom_condition():
            return ValidationResult(
                success=False,
                message="カスタム検証に失敗しました"
            )
        return ValidationResult(success=True)
```

### カスタム通知チャネル

独自の通知方法を追加できます：

```python
from services.auto_deployment.notification.base import BaseNotificationChannel

class CustomNotificationChannel(BaseNotificationChannel):
    def send_notification(self, message, severity):
        # カスタム通知ロジック
        pass
```

### デプロイメントフック

デプロイメントの各段階でカスタムスクリプトを実行できます：

```yaml
hooks:
  pre_deploy:
    - "scripts/backup_database.sh"
    - "scripts/notify_team.py"
  post_deploy:
    - "scripts/warm_up_cache.py"
    - "scripts/run_smoke_tests.sh"
```

## モニタリングとアラート

### ダッシュボード

デプロイメントダッシュボードにアクセス：

```bash
# ダッシュボードを起動
python -m services.auto_deployment.monitoring.dashboard
```

ブラウザで `http://localhost:8080` にアクセスしてダッシュボードを表示します。

### アラート設定

```yaml
alerts:
  error_rate_threshold: 0.05  # 5%
  response_time_threshold: 2000  # 2秒
  cpu_usage_threshold: 0.8  # 80%
  memory_usage_threshold: 0.8  # 80%
```

### ログの確認

```bash
# デプロイメントログを確認
python -m services.auto_deployment.cli logs

# 特定の期間のログを確認
python -m services.auto_deployment.cli logs --since "2024-01-01" --until "2024-01-02"

# エラーログのみを確認
python -m services.auto_deployment.cli logs --level error
```

## ベストプラクティス

### デプロイメント前のチェックリスト

1. **コードレビュー**: すべての変更がレビュー済みであることを確認
2. **テスト実行**: 単体テスト、統合テストがすべて通過していることを確認
3. **セキュリティスキャン**: 脆弱性スキャンを実行し、問題がないことを確認
4. **設定確認**: 環境固有の設定が正しく設定されていることを確認
5. **バックアップ**: 必要に応じてデータベースのバックアップを作成

### デプロイメント戦略の選択

- **Blue-Green**: プロダクション環境での安全なデプロイメント（推奨）
- **Rolling Update**: ダウンタイムを最小化したい場合
- **Canary**: 段階的なロールアウトが必要な場合

### 監視とアラート

- デプロイメント後は最低30分間システムを監視
- エラー率、レスポンス時間、リソース使用率を確認
- 異常を検出した場合は即座にロールバックを検討

## 例とチュートリアル

### チュートリアル1: 初回デプロイメント

1. **環境準備**
```bash
# Google Cloud認証
gcloud auth login
gcloud config set project your-project-id

# 設定ファイルの準備
cp config/config.example.yaml config/config.yaml
```

2. **設定の編集**
```yaml
project:
  id: "your-project-id"
  region: "asia-northeast1"

notifications:
  slack:
    webhook_url: "your-slack-webhook-url"
```

3. **デプロイメント実行**
```bash
# ドライランで確認
python -m services.auto_deployment.cli deploy --environment staging --dry-run

# 実際のデプロイメント
python -m services.auto_deployment.cli deploy --environment staging
```

### チュートリアル2: プロダクションデプロイメント

1. **事前検証**
```bash
# 設定の検証
python -m services.auto_deployment.cli validate --environment production

# ヘルスチェック
python -m services.auto_deployment.cli health-check
```

2. **デプロイメント実行**
```bash
# プロダクションデプロイメント
python -m services.auto_deployment.cli deploy --environment production --strategy blue-green
```

3. **デプロイメント後の確認**
```bash
# 状況確認
python -m services.auto_deployment.cli status --detailed

# ログ確認
python -m services.auto_deployment.cli logs --since "10 minutes ago"
```

### チュートリアル3: 問題発生時の対応

1. **問題の検出**
```bash
# エラーログの確認
python -m services.auto_deployment.cli logs --level error

# ヘルスチェック
python -m services.auto_deployment.cli health-check
```

2. **ロールバック**
```bash
# 自動ロールバック（推奨）
python -m services.auto_deployment.cli rollback

# 手動ロールバック（特定のリビジョン）
python -m services.auto_deployment.cli rollback --revision previous-stable
```

3. **問題の分析**
```bash
# デプロイメント履歴の確認
python -m services.auto_deployment.cli history

# 詳細なログ分析
python -m services.auto_deployment.cli logs --detailed --since "1 hour ago"
```

## 次のステップ

このユーザーマニュアルを読み終えたら、以下のドキュメントも参照してください：

- [トラブルシューティングガイド](troubleshooting-guide.md)
- [設定リファレンス](configuration-reference.md)
- [API ドキュメント](api-documentation.md)
- [運用・保守ガイド](operational-guide.md)

## サポート

問題が発生した場合は、以下の方法でサポートを受けることができます：

1. [トラブルシューティングガイド](troubleshooting-guide.md)を確認
2. GitHub Issues でバグレポートや機能要求を提出
3. Slack チャンネル #auto-deployment でコミュニティサポートを受ける
4. 緊急時は on-call エンジニアに連絡