# 🔐 GitHub Secrets 正しい設定方法

## ❌ エラーの原因
GitHub Secretsの名前に無効な文字が含まれています。

## ✅ 正しいSecret名

### Secret 1: GCP_PROJECT_ID
- **Name**: `GCP_PROJECT_ID` ✅
- **Value**: `therapeutic-gamification-app-prod`

### Secret 2: GCP_SA_KEY  
- **Name**: `GCP_SA_KEY` ✅
- **Value**: Google Cloud Service Account の JSON キー

## 📋 設定手順

### 1. GitHub Secretsページにアクセス
https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions

### 2. 1つ目のSecret設定
1. **New repository secret** をクリック
2. **Name**: `GCP_PROJECT_ID` (正確にこの通り入力)
3. **Secret**: `therapeutic-gamification-app-prod`
4. **Add secret** をクリック

### 3. 2つ目のSecret設定
1. **New repository secret** をクリック
2. **Name**: `GCP_SA_KEY` (正確にこの通り入力)
3. **Secret**: Google Cloud Service AccountのJSONキー全体
4. **Add secret** をクリック

## 🔑 Google Cloud Service Account JSONキー取得方法

### ステップ1: Google Cloud Consoleにアクセス
1. https://console.cloud.google.com/
2. プロジェクト選択: `therapeutic-gamification-app-prod`

### ステップ2: Service Account作成
1. **IAM & Admin** → **Service Accounts**
2. **CREATE SERVICE ACCOUNT**
3. **Service account name**: `github-actions`
4. **Service account ID**: `github-actions`

### ステップ3: 権限設定
以下のロールを追加:
- Cloud Run Admin
- Cloud Build Editor
- Storage Admin
- Service Account User
- Cloud Datastore Owner
- Secret Manager Admin
- Logging Viewer

### ステップ4: JSONキー生成
1. 作成したService Accountをクリック
2. **KEYS** タブ
3. **ADD KEY** → **Create new key**
4. **JSON** を選択 → **CREATE**
5. ダウンロードされたJSONファイルを開く
6. 内容全体をコピー

## 📝 JSONキーの例
```json
{
  "type": "service_account",
  "project_id": "therapeutic-gamification-app-prod",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## ✅ 設定完了後の確認

### GitHub Actionsを手動実行
1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions
2. **CI/CD Pipeline** を選択
3. **Run workflow** をクリック
4. **Run workflow** ボタンを押す

### デプロイ成功確認
約15-20分後、以下のURLでアプリにアクセス可能:
https://therapeutic-gamification-app-asia-northeast1.a.run.app

## 🚨 重要な注意点

1. **Secret名は正確に**: `GCP_PROJECT_ID` と `GCP_SA_KEY`
2. **JSONキーは全体をコピー**: 改行も含めて完全にコピー
3. **権限は全て設定**: 不足すると認証エラーが発生
4. **プロジェクトIDは正確に**: `therapeutic-gamification-app-prod`