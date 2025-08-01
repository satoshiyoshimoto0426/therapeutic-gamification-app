#!/bin/bash

# 治療的ゲーミフィケーションアプリ監視・ログ・アラートシステム設定スクリプト
set -euo pipefail

# 設定変数
PROJECT_ID="${PROJECT_ID:-therapeutic-gamification-prod}"
REGION="${REGION:-asia-northeast1}"

echo "📊 治療的ゲーミフィケーションアプリ監視システム設定開始"
echo "プロジェクト: $PROJECT_ID"
echo "リージョン: $REGION"

# 1. プロジェクト設定
echo "📋 プロジェクト設定中..."
gcloud config set project $PROJECT_ID

# 2. 必要なAPIの有効化
echo "🔧 監視関連APIを有効化中..."
gcloud services enable \
  monitoring.googleapis.com \
  logging.googleapis.com \
  clouderrorreporting.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com \
  bigquery.googleapis.com

# 3. BigQueryデータセットの作成
echo "🗄️ BigQueryデータセットを作成中..."
bq mk --dataset \
  --location=$REGION \
  --description="治療アプリエラーログ" \
  $PROJECT_ID:therapeutic_app_errors || echo "データセットは既に存在します"

bq mk --dataset \
  --location=$REGION \
  --description="治療安全性ログ" \
  $PROJECT_ID:therapeutic_safety_logs || echo "データセットは既に存在します"

bq mk --dataset \
  --location=$REGION \
  --description="パフォーマンスログ" \
  $PROJECT_ID:therapeutic_performance_logs || echo "データセットは既に存在します"

# 4. Cloud Storageバケット（監査ログ用）の作成
echo "🪣 監査ログ用バケットを作成中..."
gsutil mb -p $PROJECT_ID -c COLDLINE -l $REGION gs://therapeutic-app-audit-logs-prod || echo "バケットは既に存在します"

# バケットの保持ポリシー設定（7年）
gsutil lifecycle set - gs://therapeutic-app-audit-logs-prod <<EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 2555}
    }
  ]
}
EOF

# 5. 通知チャンネルの作成
echo "📢 通知チャンネルを作成中..."

# Slack通知チャンネル（通常）
gcloud alpha monitoring channels create \
  --display-name="Therapeutic App Slack Alerts" \
  --type=slack \
  --channel-labels=url=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  --channel-labels=channel_name="#therapeutic-app-alerts" || echo "通知チャンネルは既に存在します"

# Slack通知チャンネル（緊急）
gcloud alpha monitoring channels create \
  --display-name="Therapeutic App Emergency Slack" \
  --type=slack \
  --channel-labels=url=https://hooks.slack.com/services/YOUR/EMERGENCY/WEBHOOK \
  --channel-labels=channel_name="#therapeutic-app-emergency" || echo "緊急通知チャンネルは既に存在します"

# メール通知チャンネル
gcloud alpha monitoring channels create \
  --display-name="Therapeutic App Email Alerts" \
  --type=email \
  --channel-labels=email_address=therapeutic-alerts@example.com || echo "メール通知チャンネルは既に存在します"

# 安全性チームメール通知
gcloud alpha monitoring channels create \
  --display-name="Therapeutic Safety Team Email" \
  --type=email \
  --channel-labels=email_address=safety-team@example.com || echo "安全性チームメール通知は既に存在します"

# SMS通知チャンネル
gcloud alpha monitoring channels create \
  --display-name="Therapeutic On-call SMS" \
  --type=sms \
  --channel-labels=number="+81-90-XXXX-XXXX" || echo "SMS通知チャンネルは既に存在します"

# 6. カスタムメトリクスの作成
echo "📈 カスタムメトリクスを作成中..."

# 治療安全性F1スコアメトリクス
gcloud logging metrics create therapeutic_safety_f1_score \
  --description="治療安全性F1スコア" \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" jsonPayload.f1_score EXISTS' \
  --value-extractor='EXTRACT(jsonPayload.f1_score)' \
  --label-extractors='service=EXTRACT(jsonPayload.service),model_version=EXTRACT(jsonPayload.model_version)' || echo "メトリクスは既に存在します"

# API応答時間メトリクス
gcloud logging metrics create therapeutic_api_latency \
  --description="API応答時間" \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" jsonPayload.api_latency EXISTS' \
  --value-extractor='EXTRACT(jsonPayload.api_latency)' \
  --label-extractors='endpoint=EXTRACT(jsonPayload.endpoint),method=EXTRACT(jsonPayload.method)' || echo "メトリクスは既に存在します"

# ユーザーエンゲージメントメトリクス
gcloud logging metrics create therapeutic_user_engagement \
  --description="ユーザーエンゲージメント" \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" jsonPayload.engagement_score EXISTS' \
  --value-extractor='EXTRACT(jsonPayload.engagement_score)' \
  --label-extractors='user_state=EXTRACT(jsonPayload.user_state),age_group=EXTRACT(jsonPayload.age_group)' || echo "メトリクスは既に存在します"

# 7. ログシンクの作成
echo "📝 ログシンクを作成中..."

# 監査ログシンク
gcloud logging sinks create therapeutic-app-audit-logs \
  storage.googleapis.com/therapeutic-app-audit-logs-prod \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" (jsonPayload.event_type="user_authentication" OR jsonPayload.event_type="guardian_access" OR jsonPayload.event_type="data_access" OR jsonPayload.event_type="safety_violation" OR jsonPayload.event_type="cbt_intervention" OR jsonPayload.event_type="task_completion" OR jsonPayload.event_type="story_generation")' || echo "監査ログシンクは既に存在します"

# エラーログシンク
gcloud logging sinks create therapeutic-app-error-logs \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/therapeutic_app_errors \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" severity>=ERROR' || echo "エラーログシンクは既に存在します"

# 治療安全性ログシンク
gcloud logging sinks create therapeutic-safety-logs \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/therapeutic_safety_logs \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" (jsonPayload.component="therapeutic_safety" OR jsonPayload.component="content_moderation" OR jsonPayload.component="cbt_intervention" OR jsonPayload.f1_score EXISTS OR jsonPayload.safety_violation EXISTS)' || echo "安全性ログシンクは既に存在します"

# パフォーマンスログシンク
gcloud logging sinks create therapeutic-performance-logs \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/therapeutic_performance_logs \
  --log-filter='resource.type="cloud_run_revision" resource.labels.service_name="therapeutic-gamification-app" (jsonPayload.response_time EXISTS OR jsonPayload.memory_usage EXISTS OR jsonPayload.cpu_usage EXISTS OR jsonPayload.concurrent_users EXISTS OR jsonPayload.api_latency EXISTS)' || echo "パフォーマンスログシンクは既に存在します"

# 8. アップタイムチェックの作成
echo "🏥 アップタイムチェックを作成中..."
gcloud monitoring uptime create \
  --display-name="Therapeutic App Uptime Check" \
  --http-check-path="/health" \
  --http-check-port=443 \
  --http-check-use-ssl \
  --hostname="therapeutic-app.example.com" \
  --timeout=10s \
  --period=60s \
  --selected-regions=ASIA_PACIFIC,USA,EUROPE || echo "アップタイムチェックは既に存在します"

# 9. アラートポリシーの作成
echo "🚨 アラートポリシーを作成中..."

# パフォーマンスアラート
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring-config.yaml || echo "パフォーマンスアラートポリシーは既に存在します"

# 10. ダッシュボードの作成
echo "📊 監視ダッシュボードを作成中..."
gcloud monitoring dashboards create \
  --config-from-file=monitoring-dashboard.json || echo "ダッシュボードは既に存在します"

# 11. Error Reportingの設定
echo "🐛 Error Reportingを設定中..."
# Error Reportingは自動的に有効化されるため、特別な設定は不要

# 12. Cloud Traceの設定
echo "🔍 Cloud Traceを設定中..."
# Cloud Traceも自動的に有効化されるため、特別な設定は不要

# 13. Cloud Profilerの設定
echo "⚡ Cloud Profilerを設定中..."
# Cloud Profilerはアプリケーションコードで有効化する必要がある

# 14. 監視設定の検証
echo "✅ 監視設定を検証中..."

# アップタイムチェックの確認
gcloud monitoring uptime list --filter="displayName:Therapeutic App Uptime Check"

# アラートポリシーの確認
gcloud alpha monitoring policies list --filter="displayName:Therapeutic App Performance Alerts"

# ログシンクの確認
gcloud logging sinks list --filter="name:therapeutic-app-audit-logs"

# カスタムメトリクスの確認
gcloud logging metrics list --filter="name:therapeutic_safety_f1_score"

# 15. 監視データの初期化
echo "🔄 監視データを初期化中..."

# サンプルメトリクスの送信（テスト用）
gcloud logging write therapeutic-app-test \
  '{"message": "監視システムテスト", "severity": "INFO", "component": "monitoring_setup", "f1_score": 0.99, "api_latency": 800, "engagement_score": 0.75, "user_state": "ACTION"}' \
  --severity=INFO

echo "✅ 監視・ログ・アラートシステム設定完了!"
echo ""
echo "📊 ダッシュボードURL: https://console.cloud.google.com/monitoring/dashboards"
echo "📝 ログURL: https://console.cloud.google.com/logs"
echo "🚨 アラートURL: https://console.cloud.google.com/monitoring/alerting"
echo ""
echo "次のステップ:"
echo "1. Slack Webhook URLを実際のURLに更新"
echo "2. メールアドレスを実際のアドレスに更新"
echo "3. SMS番号を実際の番号に更新"
echo "4. アプリケーションコードでカスタムメトリクスの送信を実装"
echo "5. 治療安全性F1スコアの定期的な計算と送信を実装"