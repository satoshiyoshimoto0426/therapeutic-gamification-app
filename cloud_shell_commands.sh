#!/bin/bash

# Google Cloud プロジェクト設定とAPI有効化
echo "🚀 Google Cloud プロジェクト設定開始..."

# 既存のプロジェクトに切り替え
gcloud config set project abiding-beanbag-467909-d8

# プロジェクトが正しく設定されたか確認
echo "📋 現在のプロジェクト:"
gcloud config get-value project

# 必要なAPIを有効化
echo "🔧 必要なAPIを有効化中..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  artifactregistry.googleapis.com

echo "✅ Google Cloud設定完了！"