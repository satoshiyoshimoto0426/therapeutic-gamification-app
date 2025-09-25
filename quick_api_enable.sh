#!/bin/bash

# Google Cloud APIs 一括有効化スクリプト
# 治療的ゲーミフィケーションアプリ用

PROJECT_ID="abiding-beanbag-467909-d8"

echo "🚀 Google Cloud APIs を有効化中..."
echo "プロジェクト: $PROJECT_ID"

# プロジェクト設定
gcloud config set project $PROJECT_ID

# 必要なAPIを一括で有効化
echo "📦 APIを有効化中..."

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  storage-api.googleapis.com \
  storage-component.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  clouderrorreporting.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudscheduler.googleapis.com \
  pubsub.googleapis.com \
  cloudkms.googleapis.com \
  binaryauthorization.googleapis.com \
  dns.googleapis.com \
  certificatemanager.googleapis.com

echo "✅ API有効化完了！"

# 重要なAPIの確認
echo "🔍 重要なAPIの確認中..."

CRITICAL_APIS=(
  "run.googleapis.com"
  "cloudbuild.googleapis.com" 
  "firestore.googleapis.com"
  "iam.googleapis.com"
)

for api in "${CRITICAL_APIS[@]}"; do
  if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
    echo "✅ $api"
  else
    echo "❌ $api"
  fi
done

echo "🎉 設定完了！GitHub Actionsでデプロイを再実行してください。"