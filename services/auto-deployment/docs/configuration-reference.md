# Auto-Deployment System 設定リファレンス

## 概要

このドキュメントでは、Auto-Deployment Systemのすべての設定オプションについて詳細に説明します。設定は主に `config.yaml` ファイルで管理されます。

## 設定ファイルの構造

```yaml
# メイン設定ファイル: services/auto-deployment/config/config.yaml
project:
  # プロジェクト基本設定
  
deployment:
  # デプロイメント設定
  
environments:
  # 環境別設定
  
validation:
  # 検証設定
  
security:
  # セキュリティ設定
  
notifications:
  # 通知設定
  
monitoring:
  # 監視設定
  
rollback:
  # ロールバック設定
```

## 詳細設定項目

### 1. プロジェクト設定 (project)

```yaml
project:
  # Google Cloud プロジェクトID（必須）
  id: "your-project-id"
  
  # デプロイメント対象リージョン（必須）
  region: "asia-northeast1"
  
  # プロジェクト名（表示用）
  name: "Therapeutic Gamification App"
  
  # プロジェクト説明
  description: "治療的ゲーミフィケーションアプリケーション"
  
  # タグ（リソース管理用）
  tags:
    environment: "production"
    team: "platform"
    cost-center: "engineering"
```

**設定項目の詳細:**

| 項目 | 型 | 必須 | デフォルト | 説明 |
|------|----|----|-----------|------|
| `id` | string | ✓ | - | Google Cloud プロジェクトID |
| `region` | string | ✓ | - | デプロイメント対象リージョン |
| `name` | string | - | プロジェクトID | プロジェクト表示名 |
| `description` | string | - | - | プロジェクト説明 |
| `tags` | object | - | {} | リソースタグ |

### 2. デプロイメント設定 (deployment)

```yaml
deployment:
  # デプロイメント戦略
  strategy: "blue-green"  # blue-green, rolling, canary
  
  # タイムアウト（秒）
  timeout: 1800  # 30分
  
  # 並列デプロイメント
  parallel_services: true
  max_parallel_jobs: 3
  
  # リトライ設定
  retry_attempts: 3
  retry_delay: 60  # 秒
  
  # ビルド設定
  build:
    enable_cache: true
    cache_from: ["gcr.io/your-project/cache:latest"]
    cpu: "2"
    memory: "4Gi"
    timeout: 1200  # 20分
  
  # トラフィック管理
  traffic:
    canary_percentage: 10  # カナリアデプロイメント時の初期トラフィック
    ramp_up_duration: 300  # 5分でトラフィックを段階的に増加
    
  # フック（カスタムスクリプト実行）
  hooks:
    pre_deploy:
      - "scripts/backup_database.sh"
      - "scripts/notify_team.py"
    post_deploy:
      - "scripts/warm_up_cache.py"
      - "scripts/run_smoke_tests.sh"
    pre_rollback:
      - "scripts/prepare_rollback.sh"
    post_rollback:
      - "scripts/notify_rollback.py"
```

**デプロイメント戦略の詳細:**

| 戦略 | 説明 | 適用場面 | ダウンタイム |
|------|------|----------|-------------|
| `blue-green` | 新環境を構築後、トラフィックを一括切り替え | プロダクション環境 | なし |
| `rolling` | 既存インスタンスを段階的に更新 | ステージング環境 | なし |
| `canary` | 一部のトラフィックを新バージョンに流す | 段階的ロールアウト | なし |

### 3. 環境別設定 (environments)

```yaml
environments:
  # 開発環境
  development:
    # Cloud Run 設定
    min_instances: 0
    max_instances: 10
    memory: "1Gi"
    cpu: "1"
    
    # 環境変数
    env_vars:
      LOG_LEVEL: "DEBUG"
      ENABLE_DEBUG: "true"
    
    # ドメイン設定
    domain: "dev.your-app.com"
    
    # データベース設定
    database:
      instance: "dev-instance"
      database: "dev-database"
    
  # ステージング環境
  staging:
    min_instances: 1
    max_instances: 20
    memory: "2Gi"
    cpu: "2"
    
    env_vars:
      LOG_LEVEL: "INFO"
      ENABLE_DEBUG: "false"
    
    domain: "staging.your-app.com"
    
    database:
      instance: "staging-instance"
      database: "staging-database"
    
    # ステージング固有の設定
    auto_deploy_on_merge: true
    require_approval: false
    
  # プロダクション環境
  production:
    min_instances: 2
    max_instances: 100
    memory: "4Gi"
    cpu: "4"
    
    env_vars:
      LOG_LEVEL: "WARN"
      ENABLE_DEBUG: "false"
    
    domain: "your-app.com"
    
    database:
      instance: "prod-instance"
      database: "prod-database"
    
    # プロダクション固有の設定
    require_approval: true
    approved_deployers:
      - "admin@example.com"
      - "lead-dev@example.com"
    
    # 高可用性設定
    multi_region: true
    backup_enabled: true
    
    # セキュリティ設定
    vpc_connector: "prod-vpc-connector"
    ingress: "internal-and-cloud-load-balancing"
```

### 4. 検証設定 (validation)

```yaml
validation:
  # 有効化する検証項目
  enabled_validators:
    - "code_quality"
    - "security"
    - "dependency"
    - "cloud_resource"
    - "authentication"
    - "environment"
  
  # コード品質検証
  code_quality:
    min_test_coverage: 0.8  # 80%
    enable_linting: true
    enable_type_checking: true
    
    # 品質ゲート
    quality_gates:
      complexity_threshold: 10
      duplication_threshold: 0.03  # 3%
      maintainability_rating: "A"
  
  # セキュリティ検証
  security:
    enable_vulnerability_scan: true
    enable_secret_scan: true
    enable_license_check: true
    
    # 許可されるライセンス
    allowed_licenses:
      - "MIT"
      - "Apache-2.0"
      - "BSD-3-Clause"
    
    # 脆弱性の許容レベル
    vulnerability_threshold:
      critical: 0
      high: 0
      medium: 5
      low: 10
  
  # 依存関係検証
  dependency:
    check_outdated: true
    check_conflicts: true
    auto_update_minor: false
    
    # 除外パッケージ
    exclude_packages:
      - "legacy-package"
  
  # クラウドリソース検証
  cloud_resource:
    check_quotas: true
    check_apis: true
    check_permissions: true
    
    # 必要なAPI
    required_apis:
      - "run.googleapis.com"
      - "cloudbuild.googleapis.com"
      - "firestore.googleapis.com"
      - "secretmanager.googleapis.com"
  
  # 認証検証
  authentication:
    check_service_accounts: true
    check_iam_policies: true
    
    # 必要な権限
    required_permissions:
      - "run.services.create"
      - "run.services.update"
      - "cloudbuild.builds.create"
  
  # 環境検証
  environment:
    check_env_vars: true
    check_secrets: true
    check_configs: true
    
    # 必須環境変数
    required_env_vars:
      - "PROJECT_ID"
      - "ENVIRONMENT"
```

### 5. セキュリティ設定 (security)

```yaml
security:
  # 全般設定
  enable_audit_logging: true
  enable_compliance_check: true
  
  # 認証・認可
  authentication:
    require_mfa: true
    session_timeout: 3600  # 1時間
    
    # 許可されたデプロイヤー
    allowed_deployers:
      - "admin@example.com"
      - "devops@example.com"
    
    # 許可されたIPアドレス
    allowed_ip_ranges:
      - "10.0.0.0/8"
      - "192.168.0.0/16"
  
  # 暗号化
  encryption:
    enable_at_rest: true
    enable_in_transit: true
    kms_key_id: "projects/your-project/locations/global/keyRings/deployment/cryptoKeys/deployment-key"
  
  # ネットワークセキュリティ
  network:
    enable_vpc: true
    vpc_connector: "deployment-vpc-connector"
    enable_private_google_access: true
    
    # ファイアウォールルール
    firewall_rules:
      - name: "allow-deployment"
        direction: "INGRESS"
        priority: 1000
        source_ranges: ["10.0.0.0/8"]
        allowed:
          - protocol: "tcp"
            ports: ["8080", "443"]
  
  # コンプライアンス
  compliance:
    enable_gdpr: true
    enable_hipaa: false
    data_retention_days: 90
    
    # 監査ログ設定
    audit_log:
      retention_days: 365
      export_to_bigquery: true
      bigquery_dataset: "audit_logs"
```

### 6. 通知設定 (notifications)

```yaml
notifications:
  # 通知チャネル
  channels:
    # Slack通知
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
      channel: "#deployments"
      username: "Auto-Deploy Bot"
      icon_emoji: ":rocket:"
      
      # 通知レベル
      notify_on:
        - "deployment_start"
        - "deployment_success"
        - "deployment_failure"
        - "rollback_triggered"
        - "health_check_failure"
    
    # メール通知
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "notifications@your-domain.com"
      password_secret: "email-password"  # Secret Manager のシークレット名
      
      # 受信者設定
      recipients:
        critical: ["admin@example.com", "oncall@example.com"]
        warning: ["team@example.com"]
        info: ["dev-team@example.com"]
      
      # メールテンプレート
      templates:
        deployment_success: "templates/deployment_success.html"
        deployment_failure: "templates/deployment_failure.html"
    
    # Microsoft Teams通知
    teams:
      enabled: false
      webhook_url: "https://outlook.office.com/webhook/..."
      
    # PagerDuty統合
    pagerduty:
      enabled: false
      integration_key: "your-integration-key"
      severity_mapping:
        critical: "critical"
        high: "error"
        medium: "warning"
        low: "info"
  
  # 通知ルール
  rules:
    # 営業時間外の通知制限
    quiet_hours:
      enabled: true
      start_time: "22:00"
      end_time: "08:00"
      timezone: "Asia/Tokyo"
      emergency_override: true
    
    # 通知頻度制限
    rate_limiting:
      max_notifications_per_hour: 10
      cooldown_period: 300  # 5分
    
    # 条件付き通知
    conditional_notifications:
      - condition: "environment == 'production'"
        channels: ["slack", "email", "pagerduty"]
      - condition: "severity == 'critical'"
        channels: ["email", "pagerduty"]
        override_quiet_hours: true
```

### 7. 監視設定 (monitoring)

```yaml
monitoring:
  # ヘルスチェック
  health_checks:
    enabled: true
    endpoints:
      - path: "/health"
        timeout: 30
        interval: 60
      - path: "/api/health"
        timeout: 30
        interval: 60
      - path: "/ready"
        timeout: 10
        interval: 30
    
    # 成功条件
    success_criteria:
      status_code: 200
      response_time_ms: 2000
      success_rate: 0.95
    
    # リトライ設定
    retry_attempts: 3
    retry_delay: 10
  
  # パフォーマンス監視
  performance:
    enabled: true
    
    # メトリクス収集
    metrics:
      - name: "response_time"
        threshold: 2000  # ms
        aggregation: "p95"
      - name: "error_rate"
        threshold: 0.05  # 5%
        aggregation: "avg"
      - name: "cpu_usage"
        threshold: 0.8   # 80%
        aggregation: "avg"
      - name: "memory_usage"
        threshold: 0.8   # 80%
        aggregation: "avg"
    
    # 収集間隔
    collection_interval: 60  # 秒
    retention_period: 30     # 日
  
  # アラート設定
  alerts:
    enabled: true
    
    # アラートルール
    rules:
      - name: "high_error_rate"
        condition: "error_rate > 0.05"
        duration: "5m"
        severity: "critical"
        
      - name: "slow_response_time"
        condition: "response_time_p95 > 2000"
        duration: "10m"
        severity: "warning"
        
      - name: "high_cpu_usage"
        condition: "cpu_usage > 0.8"
        duration: "15m"
        severity: "warning"
    
    # エスカレーション
    escalation:
      - level: 1
        delay: "0m"
        channels: ["slack"]
      - level: 2
        delay: "15m"
        channels: ["email"]
      - level: 3
        delay: "30m"
        channels: ["pagerduty"]
  
  # ダッシュボード
  dashboard:
    enabled: true
    port: 8080
    
    # 表示項目
    widgets:
      - type: "deployment_status"
        position: [0, 0]
        size: [2, 1]
      - type: "health_metrics"
        position: [2, 0]
        size: [2, 1]
      - type: "performance_chart"
        position: [0, 1]
        size: [4, 2]
```

### 8. ロールバック設定 (rollback)

```yaml
rollback:
  # 自動ロールバック
  auto_rollback:
    enabled: true
    
    # トリガー条件
    triggers:
      - condition: "error_rate > 0.1"
        duration: "5m"
        action: "immediate"
      - condition: "response_time_p95 > 5000"
        duration: "10m"
        action: "gradual"
      - condition: "health_check_failure_rate > 0.5"
        duration: "3m"
        action: "immediate"
    
    # 監視期間
    monitoring_duration: 1800  # 30分
    
    # 除外条件
    exclude_conditions:
      - "maintenance_mode == true"
      - "manual_override == true"
  
  # ロールバック実行
  execution:
    timeout: 600  # 10分
    verification_attempts: 5
    verification_interval: 30  # 秒
    
    # ロールバック戦略
    strategy: "immediate"  # immediate, gradual
    
    # 段階的ロールバック（gradual使用時）
    gradual_rollback:
      initial_percentage: 10
      increment_percentage: 20
      increment_interval: 120  # 2分
  
  # 通知設定
  notifications:
    on_trigger: true
    on_start: true
    on_success: true
    on_failure: true
    
    # 通知チャネル
    channels: ["slack", "email"]
    
    # 緊急時の追加通知
    emergency_channels: ["pagerduty"]
  
  # 履歴管理
  history:
    retention_days: 90
    max_records: 1000
```

## 環境変数による設定オーバーライド

設定ファイルの値は環境変数でオーバーライドできます：

```bash
# プロジェクトID
export AUTO_DEPLOY_PROJECT_ID="your-project-id"

# デプロイメント戦略
export AUTO_DEPLOY_STRATEGY="blue-green"

# 通知設定
export AUTO_DEPLOY_SLACK_WEBHOOK="https://hooks.slack.com/..."
export AUTO_DEPLOY_EMAIL_PASSWORD="your-password"

# セキュリティ設定
export AUTO_DEPLOY_REQUIRE_APPROVAL="true"
```

## 設定の検証

設定ファイルの妥当性を検証：

```bash
# 設定ファイルの構文チェック
python -m services.auto_deployment.cli validate-config

# 特定の環境の設定チェック
python -m services.auto_deployment.cli validate-config --environment production

# 設定の詳細表示
python -m services.auto_deployment.cli show-config --environment production
```

## 設定テンプレート

### 最小構成

```yaml
# config.minimal.yaml
project:
  id: "your-project-id"
  region: "asia-northeast1"

deployment:
  strategy: "rolling"
  timeout: 1800

environments:
  production:
    min_instances: 1
    max_instances: 10
    memory: "2Gi"
    cpu: "2"
```

### 推奨構成

```yaml
# config.recommended.yaml
project:
  id: "your-project-id"
  region: "asia-northeast1"

deployment:
  strategy: "blue-green"
  timeout: 1800
  parallel_services: true

validation:
  enabled_validators: ["code_quality", "security", "dependency"]
  code_quality:
    min_test_coverage: 0.8

security:
  enable_audit_logging: true
  authentication:
    require_mfa: true

notifications:
  channels:
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"

monitoring:
  health_checks:
    enabled: true
  alerts:
    enabled: true

rollback:
  auto_rollback:
    enabled: true
```

### エンタープライズ構成

```yaml
# config.enterprise.yaml
project:
  id: "your-project-id"
  region: "asia-northeast1"

deployment:
  strategy: "blue-green"
  timeout: 3600
  parallel_services: true
  max_parallel_jobs: 5

validation:
  enabled_validators: ["code_quality", "security", "dependency", "cloud_resource", "authentication"]
  code_quality:
    min_test_coverage: 0.9
  security:
    vulnerability_threshold:
      critical: 0
      high: 0

security:
  enable_audit_logging: true
  enable_compliance_check: true
  authentication:
    require_mfa: true
    allowed_deployers: ["admin@company.com"]
  encryption:
    enable_at_rest: true
    enable_in_transit: true

notifications:
  channels:
    slack:
      enabled: true
    email:
      enabled: true
    pagerduty:
      enabled: true

monitoring:
  health_checks:
    enabled: true
  performance:
    enabled: true
  alerts:
    enabled: true

rollback:
  auto_rollback:
    enabled: true
    monitoring_duration: 3600
```

## 設定のベストプラクティス

1. **環境別設定の分離**: 環境ごとに異なる設定ファイルを使用
2. **機密情報の管理**: パスワードやAPIキーは環境変数やSecret Managerを使用
3. **設定の検証**: デプロイメント前に設定の妥当性を確認
4. **バージョン管理**: 設定ファイルをGitで管理し、変更履歴を追跡
5. **ドキュメント化**: 設定変更の理由と影響を文書化

このリファレンスを参考に、プロジェクトの要件に応じて適切な設定を行ってください。