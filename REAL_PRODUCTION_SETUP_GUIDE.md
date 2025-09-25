# 🌐 実際の本番環境セットアップガイド

## 📋 前提条件

1. **Google Cloudアカウント**
2. **ドメイン名**（例：your-domain.com）
3. **GitHub アカウント**
4. **クレジットカード**（Google Cloud課金用）

## 🚀 ステップ1: Google Cloudプロジェクト作成

```bash
# Google Cloud CLIインストール（まだの場合）
# https://cloud.google.com/sdk/docs/install

# ログイン
gcloud auth login

# プロジェクト作成
gcloud projects create therapeutic-gamification-app --name="治療的ゲーミフィケーションアプリ"

# プロジェクト設定
gcloud config set project therapeutic-gamification-app

# 課金アカウント設定（必須）
gcloud billing accounts list
gcloud billing projects link therapeutic-gamification-app --billing-account=YOUR_BILLING_ACCOUNT_ID
```

## 🔧 ステップ2: 必要なAPIの有効化

```bash
# 必要なGoogle Cloud APIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable cloudkms.googleapis.com
gcloud services enable cloudsecurity.googleapis.com
gcloud services enable firebase.googleapis.com
```

## 🏗️ ステップ3: インフラストラクチャ設定

```bash
# Firestoreデータベース作成
gcloud firestore databases create --region=asia-northeast1

# Secret Manager設定
gcloud secrets create jwt-secret --data-file=jwt-secret.txt
gcloud secrets create line-bot-secret --data-file=line-bot-secret.txt
```

## 📦 ステップ4: コンテナイメージビルド

```bash
# 各サービスのDockerイメージをビルド
for service in auth core-game task-mgmt mandala mood-tracking ai-story story-dag therapeutic-safety adhd-support line-bot guardian-portal kpi-dashboard performance-monitoring gdpr-compliance alpha-playtest edge-ai-cache; do
  echo "Building $service..."
  cd services/$service
  gcloud builds submit --tag gcr.io/therapeutic-gamification-app/$service:latest
  cd ../..
done

# フロントエンドビルド
cd frontend
npm run build
firebase deploy --project therapeutic-gamification-app
cd ..
```

## 🚀 ステップ5: Cloud Runサービスデプロイ

```bash
# 各マイクロサービスをCloud Runにデプロイ
for service in auth core-game task-mgmt mandala mood-tracking ai-story story-dag therapeutic-safety adhd-support line-bot guardian-portal kpi-dashboard performance-monitoring gdpr-compliance alpha-playtest edge-ai-cache; do
  echo "Deploying $service to Cloud Run..."
  gcloud run deploy $service \
    --image gcr.io/therapeutic-gamification-app/$service:latest \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 100 \
    --min-instances 1
done
```

## 🌐 ステップ6: ドメイン設定

### 6.1 ドメイン取得
- Google Domains、Namecheap、GoDaddyなどでドメインを取得

### 6.2 Cloud Run カスタムドメイン設定
```bash
# メインアプリ用ドメイン設定
gcloud run domain-mappings create \
  --service core-game \
  --domain your-domain.com \
  --region asia-northeast1

# Guardian Portal用サブドメイン
gcloud run domain-mappings create \
  --service guardian-portal \
  --domain guardian.your-domain.com \
  --region asia-northeast1

# KPI Dashboard用サブドメイン
gcloud run domain-mappings create \
  --service kpi-dashboard \
  --domain kpi.your-domain.com \
  --region asia-northeast1
```

### 6.3 DNS設定
ドメインプロバイダーで以下のCNAMEレコードを設定：

```
your-domain.com → ghs.googlehosted.com
guardian.your-domain.com → ghs.googlehosted.com
kpi.your-domain.com → ghs.googlehosted.com
```

## 🔒 ステップ7: SSL証明書設定

```bash
# SSL証明書は自動的に設定されますが、確認
gcloud run domain-mappings describe \
  --domain your-domain.com \
  --region asia-northeast1
```

## 📱 ステップ8: LINE Bot設定

1. **LINE Developers Console**にアクセス
2. **新しいプロバイダー**を作成
3. **Messaging API**チャンネルを作成
4. **Webhook URL**を設定：`https://your-domain.com/line/webhook`
5. **Channel Secret**と**Channel Access Token**を取得
6. Google Secret Managerに保存

## 🔧 ステップ9: 環境変数設定

```bash
# 各サービスに環境変数を設定
for service in auth core-game task-mgmt mandala mood-tracking ai-story story-dag therapeutic-safety adhd-support line-bot guardian-portal kpi-dashboard performance-monitoring gdpr-compliance alpha-playtest edge-ai-cache; do
  gcloud run services update $service \
    --region asia-northeast1 \
    --set-env-vars="ENVIRONMENT=production,PROJECT_ID=therapeutic-gamification-app,REGION=asia-northeast1"
done
```

## 📊 ステップ10: 監視・アラート設定

```bash
# Cloud Monitoring設定
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml

# ログベースのアラート設定
gcloud logging sinks create error-sink \
  bigquery.googleapis.com/projects/therapeutic-gamification-app/datasets/error_logs \
  --log-filter='severity>=ERROR'
```

## 🧪 ステップ11: 本番テスト

```bash
# ヘルスチェック
curl https://your-domain.com/health

# API テスト
curl https://your-domain.com/api/auth/health
curl https://guardian.your-domain.com/health
curl https://kpi.your-domain.com/health
```

## 🎯 最終確認チェックリスト

- [ ] Google Cloudプロジェクト作成完了
- [ ] 課金アカウント設定完了
- [ ] 必要なAPI有効化完了
- [ ] Firestoreデータベース作成完了
- [ ] 全サービスのDockerイメージビルド完了
- [ ] 全サービスのCloud Runデプロイ完了
- [ ] ドメイン取得・設定完了
- [ ] DNS設定完了
- [ ] SSL証明書設定完了
- [ ] LINE Bot設定完了
- [ ] 環境変数設定完了
- [ ] 監視・アラート設定完了
- [ ] 本番テスト完了

## 💰 予想コスト

### 月額料金（概算）
- **Cloud Run**: $50-200（トラフィック次第）
- **Firestore**: $10-50（データ量次第）
- **Cloud Build**: $10-30
- **Monitoring**: $5-20
- **ドメイン**: $10-15/年
- **合計**: 約$85-315/月

## 🚨 重要な注意事項

1. **セキュリティ**: 本番環境では必ずIAMロールを適切に設定
2. **バックアップ**: Firestoreの自動バックアップを設定
3. **監視**: アラートとログ監視を必ず設定
4. **コスト管理**: 予算アラートを設定
5. **GDPR準拠**: EU圏内のユーザーがいる場合は追加設定が必要

## 📞 サポート

問題が発生した場合：
1. Google Cloud サポート
2. Firebase サポート
3. LINE Developers サポート

---

**このガイドに従って設定すれば、実際にアクセス可能な本番環境が構築できます！**