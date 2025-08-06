# 🔐 GitHub Secrets 簡単設定ガイド

## 📝 Secretに入力する内容

### 1つ目のSecret: GCP_PROJECT_ID

**Name欄に入力**: `GCP_PROJECT_ID`

**Secret欄（Value）に入力**: 
```
therapeutic-gamification-app-prod
```

### 2つ目のSecret: GCP_SA_KEY

**Name欄に入力**: `GCP_SA_KEY`

**Secret欄（Value）に入力**: Google CloudのJSONキー全体
```json
{
  "type": "service_account",
  "project_id": "therapeutic-gamification-app-prod",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/github-actions%40therapeutic-gamification-app-prod.iam.gserviceaccount.com"
}
```

## 🎯 具体的な手順

### ステップ1: Google Cloud Service Account作成
1. https://console.cloud.google.com/iam-admin/serviceaccounts にアクセス
2. プロジェクト: `therapeutic-gamification-app-prod` を選択
3. **CREATE SERVICE ACCOUNT** をクリック
4. **Service account name**: `github-actions` と入力
5. **CREATE AND CONTINUE** をクリック
6. 以下の権限を追加:
   - Cloud Run Admin
   - Cloud Build Editor
   - Storage Admin
   - Service Account User
   - Cloud Datastore Owner
   - Secret Manager Admin
   - Logging Viewer
7. **CONTINUE** → **DONE** をクリック

### ステップ2: JSONキーをダウンロード
1. 作成した `github-actions` Service Accountをクリック
2. **KEYS** タブをクリック
3. **ADD KEY** → **Create new key** をクリック
4. **JSON** を選択 → **CREATE** をクリック
5. JSONファイルがダウンロードされる

### ステップ3: JSONファイルを開く
1. ダウンロードしたJSONファイルをメモ帳で開く
2. 内容全体をコピー（Ctrl+A → Ctrl+C）

### ステップ4: GitHub Secretsに設定
1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions にアクセス
2. **New repository secret** をクリック

**1つ目のSecret**:
- Name: `GCP_PROJECT_ID`
- Secret: `therapeutic-gamification-app-prod`
- **Add secret** をクリック

**2つ目のSecret**:
- Name: `GCP_SA_KEY`
- Secret: JSONファイルの内容全体を貼り付け
- **Add secret** をクリック

## ✅ 設定完了後
GitHub Actionsを手動実行:
1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions
2. **CI/CD Pipeline** を選択
3. **Run workflow** をクリック
4. **Run workflow** ボタンを押す

約15-20分でデプロイ完了！