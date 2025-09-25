# 🚀 Google Cloud APIs 設定手順

## 📋 概要
治療的ゲーミフィケーションアプリのデプロイに必要なGoogle Cloud APIを一括で有効化します。

**プロジェクトID**: `abiding-beanbag-467909-d8`

## 🎯 クイックスタート

### 方法1: PowerShell (Windows推奨)
```powershell
# PowerShellで実行
.\quick_api_enable.ps1
```

### 方法2: Python
```bash
# Pythonで実行
python enable_all_google_cloud_apis.py
```

### 方法3: Bash (Linux/Mac)
```bash
# Bashで実行
./quick_api_enable.sh
```

### 方法4: 手動コマンド
```bash
# gcloudコマンドで直接実行
gcloud config set project abiding-beanbag-467909-d8

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

## 📚 詳細ガイド
詳しい手順は `google_cloud_api_setup_guide.md` を参照してください。

## ✅ 必要な前提条件

1. **Google Cloud CLI (gcloud) がインストール済み**
   ```bash
   # インストール確認
   gcloud --version
   ```

2. **Google Cloudにログイン済み**
   ```bash
   # ログイン
   gcloud auth login
   gcloud auth application-default login
   ```

3. **プロジェクトへのアクセス権限**
   - プロジェクト `abiding-beanbag-467909-d8` への編集者権限以上

## 🔍 有効化されるAPI一覧

### 🔥 最重要 (必須)
- **Cloud Run API** - アプリケーションのホスティング
- **Cloud Build API** - CI/CDパイプライン
- **Firestore API** - データベース
- **IAM API** - 認証・認可

### 📦 コンテナ関連
- **Container Registry API** - Dockerイメージ保存
- **Artifact Registry API** - アーティファクト管理

### 🔐 セキュリティ
- **Secret Manager API** - 機密情報管理
- **IAM Service Account Credentials API** - サービスアカウント

### 📊 監視・ログ
- **Cloud Logging API** - ログ管理
- **Cloud Monitoring API** - 監視・アラート
- **Cloud Trace API** - パフォーマンス追跡
- **Error Reporting API** - エラー追跡

### 🌐 ネットワーク
- **Compute Engine API** - VPC等のネットワーク
- **Service Networking API** - サービス間通信
- **VPC Access API** - VPCアクセス

### 🔧 その他
- **Cloud Functions API** - サーバーレス関数
- **Cloud Scheduler API** - スケジュール実行
- **Pub/Sub API** - メッセージング
- **Cloud KMS API** - 暗号化キー管理

## 🚨 トラブルシューティング

### よくあるエラー

1. **認証エラー**
   ```
   ERROR: (gcloud.auth.list) Your current active account [...] does not have any valid credentials
   ```
   **解決**: `gcloud auth login` を実行

2. **権限エラー**
   ```
   ERROR: User [...] does not have permission to access project [...]
   ```
   **解決**: プロジェクトオーナーに権限付与を依頼

3. **プロジェクト未設定**
   ```
   ERROR: (gcloud.services.enable) argument --project: required
   ```
   **解決**: `gcloud config set project abiding-beanbag-467909-d8`

### 確認コマンド

```bash
# 現在の設定確認
gcloud config list

# 有効なAPI一覧
gcloud services list --enabled

# 特定のAPIの確認
gcloud services list --enabled --filter="name:run.googleapis.com"
```

## 📞 サポート

問題が解決しない場合:

1. **Google Cloud Console で手動確認**
   - [APIダッシュボード](https://console.cloud.google.com/apis/dashboard?project=abiding-beanbag-467909-d8)

2. **GitHub Actions ログを確認**
   - デプロイ時のエラーメッセージを確認

3. **サービスアカウントの権限確認**
   - IAMページでサービスアカウントの権限を確認

## 🎉 成功後の次のステップ

1. **GitHub Actions でデプロイ再実行**
2. **アプリケーションの動作確認**
3. **監視・ログの設定確認**
4. **セキュリティ設定の確認**