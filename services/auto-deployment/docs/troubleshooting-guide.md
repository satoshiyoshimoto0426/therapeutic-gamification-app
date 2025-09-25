# Auto-Deployment System トラブルシューティングガイド

## 概要

このガイドでは、Auto-Deployment Systemの使用中に発生する可能性のある一般的な問題とその解決方法について説明します。

## 一般的な問題と解決方法

### 1. 認証関連の問題

#### 問題: Google Cloud認証エラー

**症状:**
```
ERROR: Authentication failed. Please check your Google Cloud credentials.
```

**解決方法:**

1. **認証状況の確認**
```bash
gcloud auth list
gcloud auth application-default print-access-token
```

2. **再認証**
```bash
gcloud auth login
gcloud auth application-default login
```

3. **プロジェクト設定の確認**
```bash
gcloud config get-value project
gcloud config set project YOUR_PROJECT_ID
```

4. **サービスアカウントキーの確認**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

#### 問題: GitHub認証エラー

**症状:**
```
ERROR: GitHub API authentication failed
```

**解決方法:**

1. **GitHub CLIの認証**
```bash
gh auth login
gh auth status
```

2. **Personal Access Tokenの設定**
```bash
export GITHUB_TOKEN="your_personal_access_token"
```

3. **権限の確認**
- Repository への書き込み権限
- Actions の実行権限
- Secrets の読み書き権限

### 2. デプロイメント失敗

#### 問題: 事前検証の失敗

**症状:**
```
ERROR: Pre-deployment validation failed
- Code quality check failed: Test coverage below threshold (75% < 80%)
- Security scan failed: 3 vulnerabilities found
```

**解決方法:**

1. **テストカバレッジの改善**
```bash
# テストカバレッジの確認
python -m pytest --cov=services --cov-report=html

# 不足しているテストを追加
# カバレッジレポートを確認して対象ファイルを特定
```

2. **セキュリティ脆弱性の修正**
```bash
# 依存関係の脆弱性スキャン
pip audit

# 脆弱性のある依存関係を更新
pip install --upgrade package_name
```

3. **検証設定の調整**（一時的な対処）
```yaml
# config.yaml
validation:
  min_test_coverage: 0.75  # 閾値を一時的に下げる
  security_scan_required: false  # セキュリティスキャンを一時的に無効化
```

#### 問題: Cloud Run デプロイメント失敗

**症状:**
```
ERROR: Cloud Run deployment failed
- Service deployment timeout
- Insufficient memory allocation
```

**解決方法:**

1. **タイムアウトの延長**
```yaml
# config.yaml
deployment:
  timeout: 3600  # 1時間に延長
```

2. **リソース設定の調整**
```yaml
# config.yaml
environments:
  production:
    memory: "4Gi"  # メモリを増加
    cpu: "4"       # CPUを増加
```

3. **ログの詳細確認**
```bash
# Cloud Run ログの確認
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# デプロイメントログの確認
python -m services.auto_deployment.cli logs --level error --since "1 hour ago"
```

#### 問題: Docker イメージビルド失敗

**症状:**
```
ERROR: Docker image build failed
- Build context too large
- Dockerfile syntax error
```

**解決方法:**

1. **.dockerignoreの確認**
```bash
# .dockerignore ファイルを確認・更新
echo "node_modules/" >> .dockerignore
echo "*.log" >> .dockerignore
echo ".git/" >> .dockerignore
```

2. **Dockerfileの構文確認**
```bash
# Dockerfile の構文チェック
docker build --no-cache -t test-image .
```

3. **マルチステージビルドの使用**
```dockerfile
# Dockerfile
FROM python:3.9-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
COPY . .
```

### 3. ヘルスチェック失敗

#### 問題: サービスヘルスチェック失敗

**症状:**
```
ERROR: Health check failed
- /health endpoint returned 500
- Response time exceeded threshold (3000ms > 2000ms)
```

**解決方法:**

1. **ヘルスチェックエンドポイントの確認**
```bash
# 直接エンドポイントをテスト
curl -v https://your-service-url/health

# ローカルでのテスト
python -m services.core_game.main &
curl http://localhost:8080/health
```

2. **ヘルスチェック設定の調整**
```yaml
# config.yaml
health_checks:
  timeout: 60  # タイムアウトを延長
  retry_attempts: 5  # リトライ回数を増加
  success_threshold: 0.8  # 成功率の閾値を下げる
```

3. **サービス固有の問題の確認**
```bash
# サービスログの確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=your-service" --limit=20

# データベース接続の確認
python -c "from shared.config.firestore_setup import test_connection; test_connection()"
```

### 4. ロールバック関連の問題

#### 問題: 自動ロールバック失敗

**症状:**
```
ERROR: Automatic rollback failed
- Previous revision not found
- Traffic rollback timeout
```

**解決方法:**

1. **手動ロールバック**
```bash
# 利用可能なリビジョンの確認
gcloud run revisions list --service=your-service

# 特定のリビジョンにロールバック
python -m services.auto_deployment.cli rollback --revision your-service-00001-abc
```

2. **トラフィック管理の確認**
```bash
# 現在のトラフィック配分を確認
gcloud run services describe your-service --format="value(status.traffic)"

# 手動でトラフィックを調整
gcloud run services update-traffic your-service --to-revisions=your-service-00001-abc=100
```

3. **ロールバック設定の調整**
```yaml
# config.yaml
rollback:
  timeout: 600  # 10分に延長
  verification_attempts: 10
```

### 5. 通知システムの問題

#### 問題: Slack通知が送信されない

**症状:**
```
WARNING: Slack notification failed
- Webhook URL not accessible
- Invalid channel configuration
```

**解決方法:**

1. **Webhook URLの確認**
```bash
# Webhook URLのテスト
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_SLACK_WEBHOOK_URL
```

2. **設定の確認**
```yaml
# config.yaml
notifications:
  slack:
    webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    channel: "#deployments"  # チャンネル名の確認
```

3. **権限の確認**
- Slack アプリの権限設定
- チャンネルへの投稿権限

#### 問題: メール通知が送信されない

**症状:**
```
ERROR: Email notification failed
- SMTP authentication failed
- Invalid recipient address
```

**解決方法:**

1. **SMTP設定の確認**
```yaml
# config.yaml
notifications:
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"  # アプリパスワードを使用
```

2. **認証情報の確認**
```bash
# 環境変数での設定
export SMTP_PASSWORD="your-app-password"
```

### 6. パフォーマンス関連の問題

#### 問題: デプロイメントが遅い

**症状:**
- デプロイメントに30分以上かかる
- タイムアウトエラーが頻発

**解決方法:**

1. **並列処理の有効化**
```yaml
# config.yaml
deployment:
  parallel_services: true
  max_parallel_jobs: 3
```

2. **キャッシュの活用**
```yaml
# config.yaml
build:
  enable_cache: true
  cache_from: ["gcr.io/your-project/cache:latest"]
```

3. **リソース配分の最適化**
```yaml
# config.yaml
build:
  cpu: "4"
  memory: "8Gi"
```

#### 問題: メモリ不足エラー

**症状:**
```
ERROR: Out of memory during deployment
- Container killed due to memory limit
```

**解決方法:**

1. **メモリ制限の増加**
```yaml
# config.yaml
environments:
  production:
    memory: "4Gi"  # 2Gi から 4Gi に増加
```

2. **メモリ使用量の最適化**
```python
# アプリケーションコードの最適化
import gc

# 不要なオブジェクトの削除
gc.collect()

# メモリプロファイリング
import tracemalloc
tracemalloc.start()
```

## 診断ツール

### 1. システム状態の確認

```bash
# 全体的な状態確認
python -m services.auto_deployment.cli diagnose

# 詳細な診断情報
python -m services.auto_deployment.cli diagnose --verbose

# 特定のコンポーネントの診断
python -m services.auto_deployment.cli diagnose --component validation
```

### 2. ログ分析

```bash
# エラーログの抽出
python -m services.auto_deployment.cli logs --level error --since "24 hours ago"

# パフォーマンスログの確認
python -m services.auto_deployment.cli logs --grep "performance" --since "1 hour ago"

# 特定のサービスのログ
python -m services.auto_deployment.cli logs --service auth --detailed
```

### 3. 設定検証

```bash
# 設定ファイルの検証
python -m services.auto_deployment.cli validate-config

# 環境設定の確認
python -m services.auto_deployment.cli validate --environment production

# 権限の確認
python -m services.auto_deployment.cli check-permissions
```

## FAQ（よくある質問）

### Q1: デプロイメントが途中で止まってしまいます

**A:** 以下を確認してください：
1. ネットワーク接続の安定性
2. Google Cloud APIの制限
3. リソースの可用性
4. タイムアウト設定

### Q2: ロールバックが自動で実行されません

**A:** 自動ロールバックの条件を確認してください：
```yaml
rollback:
  auto_rollback_enabled: true
  failure_threshold: 0.05  # 5%のエラー率で自動ロールバック
  monitoring_duration: 300  # 5分間監視
```

### Q3: 特定のサービスだけデプロイしたい場合は？

**A:** `--services` オプションを使用してください：
```bash
python -m services.auto_deployment.cli deploy --environment production --services auth,core-game
```

### Q4: デプロイメント履歴を確認したい

**A:** 履歴コマンドを使用してください：
```bash
python -m services.auto_deployment.cli history --limit 10
python -m services.auto_deployment.cli history --service auth
```

### Q5: カスタム検証ルールを追加したい

**A:** カスタムバリデーターを作成してください：
```python
from services.auto_deployment.validation.base import BaseValidator

class CustomValidator(BaseValidator):
    def validate(self, context):
        # カスタムロジック
        return ValidationResult(success=True)
```

## エラーコード一覧

| コード | 説明 | 対処方法 |
|--------|------|----------|
| E001 | 認証エラー | 認証情報を確認 |
| E002 | 設定エラー | config.yaml を確認 |
| E003 | ネットワークエラー | 接続を確認 |
| E004 | リソース不足 | リソース設定を調整 |
| E005 | タイムアウト | タイムアウト値を増加 |
| E006 | 権限エラー | IAM権限を確認 |
| E007 | 検証失敗 | コード品質を改善 |
| E008 | デプロイメント失敗 | ログを詳細確認 |
| E009 | ヘルスチェック失敗 | サービス状態を確認 |
| E010 | ロールバック失敗 | 手動ロールバックを実行 |

## サポートとエスカレーション

### レベル1: セルフサービス
1. このトラブルシューティングガイドを確認
2. ログとエラーメッセージを分析
3. 設定を確認・調整

### レベル2: コミュニティサポート
1. GitHub Issues で問題を報告
2. Slack チャンネル #auto-deployment で質問
3. ドキュメントの改善提案

### レベル3: エスカレーション
1. 緊急時は on-call エンジニアに連絡
2. 詳細なログとエラー情報を提供
3. 再現手順を明確に記載

## 予防的メンテナンス

### 定期的なチェック項目

1. **週次チェック**
   - デプロイメント成功率の確認
   - エラーログの分析
   - パフォーマンスメトリクスの確認

2. **月次チェック**
   - 依存関係の更新
   - セキュリティパッチの適用
   - 設定の見直し

3. **四半期チェック**
   - システム全体の見直し
   - 容量計画の更新
   - 災害復旧テスト

### 監視とアラート

```yaml
# config.yaml
monitoring:
  alerts:
    deployment_failure_rate: 0.1  # 10%
    response_time_threshold: 2000  # 2秒
    error_rate_threshold: 0.05     # 5%
    
  notifications:
    critical: ["admin@example.com"]
    warning: ["team@example.com"]
```

このトラブルシューティングガイドを定期的に更新し、新しい問題や解決方法を追加してください。