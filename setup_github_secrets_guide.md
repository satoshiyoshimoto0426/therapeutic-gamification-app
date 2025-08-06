# 🔐 GitHub Secrets 設定ガイド

## 必要なSecrets

### 1. GCP_PROJECT_ID
- **Name**: `GCP_PROJECT_ID`
- **Value**: `therapeutic-gamification-app-prod`

### 2. GCP_SA_KEY
- **Name**: `GCP_SA_KEY`
- **Value**: Google Cloud Service Account の JSON キー

## Google Cloud Service Account作成手順

### ステップ1: Google Cloud Consoleにアクセス
1. https://console.cloud.google.com/ にアクセス
2. プロジェクト `therapeutic-gamification-app-prod` を選択（存在しない場合は作成）

### ステップ2: Service Account作成
1. **IAM & Admin** → **Service Accounts** に移動
2. **CREATE SERVICE ACCOUNT** をクリック
3. 以下の情報を入力:
   - **Service account name**: `github-actions`
   - **Service account ID**: `github-actions`
   - **Description**: `GitHub Actions deployment service account`

### ステップ3: 必要な権限を付与
以下のロールを追加:
- ✅ **Cloud Run Admin**
- ✅ **Cloud Build Editor** 
- ✅ **Storage Admin**
- ✅ **Service Account User**
- ✅ **Cloud Datastore Owner**
- ✅ **Secret Manager Admin**
- ✅ **Logging Viewer**
- ✅ **Monitoring Editor**

### ステップ4: JSONキーを生成
1. 作成したService Accountをクリック
2. **KEYS** タブに移動
3. **ADD KEY** → **Create new key** をクリック
4. **JSON** を選択して **CREATE**
5. ダウンロードされたJSONファイルの内容をコピー

### ステップ5: GitHub Secretsに設定
1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions
2. **New repository secret** をクリック
3. **GCP_SA_KEY** として、JSONファイルの内容全体を貼り付け

## 設定完了後の確認

### 1. GitHub Actionsを手動実行
1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions
2. **CI/CD Pipeline** を選択
3. **Run workflow** をクリック
4. **Run workflow** ボタンを押す

### 2. デプロイメント進捗確認
- 約15-20分でデプロイ完了
- 各ステップの進捗をリアルタイムで確認可能

### 3. 成功確認
デプロイ成功後、以下のURLでアプリケーションにアクセス可能:
- https://therapeutic-gamification-app-asia-northeast1.a.run.app

## トラブルシューティング

### よくあるエラー
1. **認証エラー**: Service Accountの権限不足
2. **プロジェクトエラー**: プロジェクトIDの不一致
3. **APIエラー**: 必要なGoogle Cloud APIが有効化されていない

### 解決方法
1. Service Accountの権限を再確認
2. プロジェクトIDが正確であることを確認
3. 以下のAPIを有効化:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Cloud Resource Manager API

## 🎉 設定完了！

上記の手順を完了すれば、GitHub Actionsが自動的にアプリケーションをデプロイします。