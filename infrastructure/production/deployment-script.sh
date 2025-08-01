#!/bin/bash

# 治療的ゲーミフィケーションアプリ本番環境デプロイメントスクリプト
set -euo pipefail

# 設定変数
PROJECT_ID="${PROJECT_ID:-therapeutic-gamification-prod}"
REGION="${REGION:-asia-northeast1}"
SERVICE_NAME="therapeutic-gamification-app"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 治療的ゲーミフィケーションアプリ本番環境デプロイメント開始"
echo "プロジェクト: $PROJECT_ID"
echo "リージョン: $REGION"

# 1. プロジェクト設定
echo "📋 プロジェクト設定中..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 2. 必要なAPIの有効化
echo "🔧 必要なAPIを有効化中..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  cloudkms.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  accesscontextmanager.googleapis.com

# 3. KMSキーリングとキーの作成
echo "🔐 KMS暗号化キーを設定中..."
gcloud kms keyrings create therapeutic-app-keyring \
  --location=$REGION || echo "キーリングは既に存在します"

# 各サービス用のキーを作成
for key in openai-key line-key jwt-key stripe-key storage-key user-data-key backup-key; do
  gcloud kms keys create $key \
    --location=$REGION \
    --keyring=therapeutic-app-keyring \
    --purpose=encryption \
    --rotation-period=90d || echo "キー $key は既に存在します"
done

# 4. Secret Managerシークレットの作成
echo "🔒 Secret Managerシークレットを作成中..."
for secret in openai-api-key line-channel-secret jwt-secret stripe-secret-key; do
  gcloud secrets create $secret \
    --replication-policy="user-managed" \
    --locations=$REGION || echo "シークレット $secret は既に存在します"
done

# 5. サービスアカウントの作成
echo "👤 サービスアカウントを作成中..."
gcloud iam service-accounts create therapeutic-app-service-account \
  --display-name="Therapeutic Gamification App Service Account" \
  --description="Service account for therapeutic gamification application" || echo "サービスアカウントは既に存在します"

# 6. IAM権限の設定
echo "🔑 IAM権限を設定中..."
SERVICE_ACCOUNT="therapeutic-app-service-account@$PROJECT_ID.iam.gserviceaccount.com"

# 基本権限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/logging.logWriter"

# 7. Cloud Storageバケットの作成
echo "🪣 Cloud Storageバケットを作成中..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://therapeutic-app-storage-prod || echo "バケットは既に存在します"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://therapeutic-app-user-data-prod || echo "バケットは既に存在します"
gsutil mb -p $PROJECT_ID -c COLDLINE -l asia-northeast2 gs://therapeutic-app-backup-prod || echo "バケットは既に存在します"

# バケットの暗号化設定
gsutil kms encryption -k projects/$PROJECT_ID/locations/$REGION/keyRings/therapeutic-app-keyring/cryptoKeys/storage-key gs://therapeutic-app-storage-prod
gsutil kms encryption -k projects/$PROJECT_ID/locations/$REGION/keyRings/therapeutic-app-keyring/cryptoKeys/user-data-key gs://therapeutic-app-user-data-prod

# 8. Firestoreデータベースの設定
echo "🗄️ Firestoreデータベースを設定中..."
gcloud firestore databases create --region=$REGION || echo "Firestoreデータベースは既に存在します"

# セキュリティルールのデプロイ
firebase deploy --only firestore:rules --project $PROJECT_ID || echo "Firebaseセキュリティルールのデプロイに失敗しました"

# 9. VPCコネクタの作成
echo "🌐 VPCコネクタを作成中..."
gcloud compute networks vpc-access connectors create vpc-connector \
  --region=$REGION \
  --subnet=default \
  --subnet-project=$PROJECT_ID \
  --min-instances=2 \
  --max-instances=10 || echo "VPCコネクタは既に存在します"

# 10. Cloud Armorセキュリティポリシーの作成
echo "🛡️ Cloud Armorセキュリティポリシーを作成中..."
gcloud compute security-policies create therapeutic-app-security-policy \
  --description="WAF security policy for Therapeutic Gamification App" || echo "セキュリティポリシーは既に存在します"

# レート制限ルールの追加
gcloud compute security-policies rules create 1100 \
  --security-policy=therapeutic-app-security-policy \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=120 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=300 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP || echo "レート制限ルールは既に存在します"

# 11. アプリケーションのビルドとデプロイ
echo "🏗️ アプリケーションをビルド中..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG .

# 12. Cloud Runサービスのデプロイ
echo "☁️ Cloud Runサービスをデプロイ中..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --service-account $SERVICE_ACCOUNT \
  --set-env-vars "ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID,FIRESTORE_DATABASE=therapeutic-app-prod,CLOUD_STORAGE_BUCKET=therapeutic-app-storage-prod" \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 100 \
  --timeout 300 \
  --min-instances 5 \
  --max-instances 1000 \
  --vpc-connector projects/$PROJECT_ID/locations/$REGION/connectors/vpc-connector \
  --vpc-egress private-ranges-only \
  --allow-unauthenticated

# 13. ロードバランサーとCloud Armorの設定
echo "⚖️ ロードバランサーを設定中..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

# NEGの作成
gcloud compute network-endpoint-groups create $SERVICE_NAME-neg \
  --region=$REGION \
  --network-endpoint-type=serverless \
  --cloud-run-service=$SERVICE_NAME || echo "NEGは既に存在します"

# バックエンドサービスの作成
gcloud compute backend-services create $SERVICE_NAME-backend \
  --global \
  --security-policy=therapeutic-app-security-policy || echo "バックエンドサービスは既に存在します"

gcloud compute backend-services add-backend $SERVICE_NAME-backend \
  --global \
  --network-endpoint-group=$SERVICE_NAME-neg \
  --network-endpoint-group-region=$REGION

# 14. 監視とアラートの設定
echo "📊 監視とアラートを設定中..."
# 監視設定は次のサブタスクで実装

# 15. ヘルスチェックの確認
echo "🏥 ヘルスチェックを確認中..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "サービスURL: $SERVICE_URL"

# ヘルスチェック
curl -f "$SERVICE_URL/health" || echo "⚠️ ヘルスチェックに失敗しました"

echo "✅ 本番環境デプロイメント完了!"
echo "サービスURL: $SERVICE_URL"
echo "次のステップ: 監視とアラートシステムの設定"