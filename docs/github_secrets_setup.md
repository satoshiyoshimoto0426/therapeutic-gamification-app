# GitHub Secrets 設定ガイド

## 必要なSecrets

GitHub リポジトリの Settings > Secrets and variables > Actions で以下のSecretsを設定してください。

### 1. GCP_PROJECT_ID
```
your-therapeutic-app-project-id
```
- GCPプロジェクトのID
- 例: `therapeutic-gamification-app-prod`

### 2. GCP_SA_KEY
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/github-actions%40your-project-id.iam.gserviceaccount.com"
}
```

### 3. SLACK_WEBHOOK (オプション)
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

## GCPサービスアカウント作成手順

### 1. サービスアカウント作成
```bash
# GCPプロジェクト設定
export PROJECT_ID="your-therapeutic-app-project-id"
gcloud config set project $PROJECT_ID

# サービスアカウント作成
gcloud iam service-accounts create github-actions \
    --description="GitHub Actions CI/CD" \
    --display-name="GitHub Actions"
```

### 2. 必要な権限付与
```bash
# Cloud Run管理者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Cloud Build編集者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

# Container Registry管理者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# IAM管理者（サービスアカウント作成用）
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Firestore管理者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.owner"

# Secret Manager管理者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

# ログ閲覧者
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.viewer"
```

### 3. キーファイル生成
```bash
# キーファイル生成
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# キーファイル内容をコピー（GitHub Secretsに貼り付け）
cat github-actions-key.json
```

### 4. 必要なGCP APIの有効化
```bash
# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

## セキュリティ設定確認

### 1. サービスアカウントキーの安全な管理
- ✅ キーファイルはGitHubにコミットしない
- ✅ ローカルファイルは作業完了後に削除
- ✅ 定期的なキーローテーション（90日ごと推奨）

### 2. 最小権限の原則
- ✅ 必要最小限の権限のみ付与
- ✅ 定期的な権限レビュー
- ✅ 未使用権限の削除

### 3. 監査ログの有効化
```bash
# 監査ログ設定確認
gcloud logging sinks list
gcloud logging metrics list
```

## トラブルシューティング

### よくあるエラーと解決方法

#### 1. 権限エラー
```
Error: The caller does not have permission
```
**解決方法**: サービスアカウントに必要な権限が付与されているか確認

#### 2. API無効エラー
```
Error: API [xxx] not enabled
```
**解決方法**: 必要なAPIを有効化
```bash
gcloud services enable [API_NAME]
```

#### 3. プロジェクトIDエラー
```
Error: Invalid project ID
```
**解決方法**: GCP_PROJECT_IDが正しく設定されているか確認

## 設定確認チェックリスト

- [ ] GCPプロジェクト作成済み
- [ ] 必要なAPIが有効化済み
- [ ] サービスアカウント作成済み
- [ ] 必要な権限が付与済み
- [ ] サービスアカウントキーが生成済み
- [ ] GitHub SecretsにGCP_PROJECT_ID設定済み
- [ ] GitHub SecretsにGCP_SA_KEY設定済み
- [ ] Slack通知用WebhookURL設定済み（オプション）

## 次のステップ

1. ✅ GitHub Secrets設定完了
2. 🚀 mainブランチにプッシュしてデプロイ開始
3. 📊 GitHub Actionsタブでデプロイ進行状況確認
4. 🎯 本番環境での動作確認