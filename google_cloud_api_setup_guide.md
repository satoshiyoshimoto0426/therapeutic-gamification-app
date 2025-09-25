# Google Cloud APIs 設定ガイド

## プロジェクト情報
- **プロジェクトID**: `abiding-beanbag-467909-d8`
- **プロジェクト名**: Therapeutic Gamification App

## 🚀 自動設定（推奨）

### 方法1: Pythonスクリプトで一括有効化

```bash
# スクリプトを実行
python enable_all_google_cloud_apis.py
```

### 方法2: gcloudコマンドで一括有効化

```bash
# プロジェクト設定
gcloud config set project abiding-beanbag-467909-d8

# 必要なAPIを一括有効化
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  storage-api.googleapis.com \
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
  dns.googleapis.com \
  certificatemanager.googleapis.com
```

## 🖱️ 手動設定（Google Cloud Console）

### 1. Google Cloud Consoleにアクセス
[https://console.cloud.google.com/apis/dashboard?project=abiding-beanbag-467909-d8](https://console.cloud.google.com/apis/dashboard?project=abiding-beanbag-467909-d8)

### 2. 必要なAPIを個別に有効化

#### 🔥 最重要（必須）
1. **Cloud Run API**
   - [有効化リンク](https://console.developers.google.com/apis/api/run.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
2. **Cloud Build API**
   - [有効化リンク](https://console.developers.google.com/apis/api/cloudbuild.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
3. **Firestore API**
   - [有効化リンク](https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
4. **IAM API**
   - [有効化リンク](https://console.developers.google.com/apis/api/iam.googleapis.com/overview?project=abiding-beanbag-467909-d8)

#### 📦 コンテナ関連
5. **Container Registry API**
   - [有効化リンク](https://console.developers.google.com/apis/api/containerregistry.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
6. **Artifact Registry API**
   - [有効化リンク](https://console.developers.google.com/apis/api/artifactregistry.googleapis.com/overview?project=abiding-beanbag-467909-d8)

#### 🔐 セキュリティ関連
7. **Secret Manager API**
   - [有効化リンク](https://console.developers.google.com/apis/api/secretmanager.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
8. **IAM Service Account Credentials API**
   - [有効化リンク](https://console.developers.google.com/apis/api/iamcredentials.googleapis.com/overview?project=abiding-beanbag-467909-d8)

#### 📊 監視・ログ関連
9. **Cloud Logging API**
   - [有効化リンク](https://console.developers.google.com/apis/api/logging.googleapis.com/overview?project=abiding-beanbag-467909-d8)
   
10. **Cloud Monitoring API**
    - [有効化リンク](https://console.developers.google.com/apis/api/monitoring.googleapis.com/overview?project=abiding-beanbag-467909-d8)

## 🔍 設定確認方法

### APIが有効化されているかチェック
```bash
# 有効なAPIの一覧表示
gcloud services list --enabled --project=abiding-beanbag-467909-d8

# 特定のAPIをチェック
gcloud services list --enabled --filter="name:run.googleapis.com" --project=abiding-beanbag-467909-d8
```

### サービスアカウントの権限確認
```bash
# サービスアカウントの権限確認
gcloud projects get-iam-policy abiding-beanbag-467909-d8 \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:github-aktions@abiding-beanbag-467909-d8.iam.gserviceaccount.com"
```

## ⚠️ トラブルシューティング

### よくあるエラーと解決方法

1. **"API not enabled" エラー**
   ```
   ERROR: (gcloud.run.revisions.list) API [run.googleapis.com] not enabled
   ```
   **解決**: 上記のAPIを有効化してください

2. **"Permission denied" エラー**
   ```
   ERROR: does not have permission to access
   ```
   **解決**: サービスアカウントに適切な権限を付与してください

3. **"Service account not found" エラー**
   ```
   ERROR: Service account github-aktions@... does not exist
   ```
   **解決**: GitHub Actionsのサービスアカウントを再作成してください

### 権限が不足している場合
```bash
# Cloud Run Admin権限を付与
gcloud projects add-iam-policy-binding abiding-beanbag-467909-d8 \
  --member="serviceAccount:github-aktions@abiding-beanbag-467909-d8.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Cloud Build Editor権限を付与
gcloud projects add-iam-policy-binding abiding-beanbag-467909-d8 \
  --member="serviceAccount:github-aktions@abiding-beanbag-467909-d8.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"
```

## 📋 チェックリスト

- [ ] gcloud CLIがインストール済み
- [ ] gcloud認証完了 (`gcloud auth login`)
- [ ] プロジェクト設定完了 (`gcloud config set project abiding-beanbag-467909-d8`)
- [ ] 必要なAPIが全て有効化済み
- [ ] サービスアカウントの権限設定完了
- [ ] GitHub Secretsの設定完了

## 🎯 次のステップ

1. **APIの有効化完了後**:
   - GitHub Actionsでデプロイを再実行
   - エラーログを確認

2. **まだエラーが出る場合**:
   - Google Cloud Consoleでプロジェクトの状態を確認
   - サービスアカウントの権限を再確認
   - GitHub Secretsの設定を確認

3. **成功した場合**:
   - アプリケーションの動作確認
   - 監視・ログの設定確認