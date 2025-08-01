# デプロイメントガイド

## 概要
治療的ゲーミフィケーションアプリケーションのデプロイメント手順書です。

## 前提条件

### 必要なツール
- Docker
- Google Cloud SDK
- kubectl
- Python 3.9+
- Node.js 16+

### 環境変数
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-northeast1"
export CLUSTER_NAME="therapeutic-gaming-cluster"
```

## ローカル環境セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/your-org/therapeutic-gaming-app.git
cd therapeutic-gaming-app
```

### 2. 依存関係インストール
```bash
# Python依存関係
pip install -r requirements.txt

# Node.js依存関係（フロントエンド）
cd frontend
npm install
cd ..
```

### 3. ローカル起動
```bash
python deploy_local.py
```

## 本番環境デプロイ

### 1. 事前準備
```bash
# GCPプロジェクト設定
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# 認証
gcloud auth login
gcloud auth configure-docker
```

### 2. インフラストラクチャ構築
```bash
# Terraformでインフラ構築
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 3. アプリケーションデプロイ
```bash
# CI/CDパイプライン実行
cd infrastructure/production
./deploy_script.sh
```

### 4. デプロイ後確認
```bash
# ヘルスチェック
curl https://your-domain.com/health

# 統合テスト実行
python final_integration_test.py --target https://your-domain.com
```

## ロールバック手順

### 1. 前バージョンへのロールバック
```bash
# 最新の安定版リビジョンを取得
python get_last_stable_revision.py

# ロールバック実行
gcloud run services update-traffic therapeutic-gaming-service   --to-revisions=REVISION_NAME=100   --region=$REGION
```

### 2. データベースロールバック
```bash
# バックアップからの復元
gcloud sql backups restore BACKUP_ID   --restore-instance=therapeutic-gaming-db   --backup-instance=therapeutic-gaming-db
```

## 監視設定

### 1. アラート設定
```bash
# 監視ダッシュボード作成
gcloud monitoring dashboards create   --config-from-file=monitoring-dashboard.json
```

### 2. ログ設定
```bash
# ログ集約設定
gcloud logging sinks create therapeutic-gaming-logs   bigquery.googleapis.com/projects/$PROJECT_ID/datasets/app_logs
```

## トラブルシューティング

### よくある問題
1. **デプロイ失敗**: ログを確認し、権限設定を見直す
2. **接続エラー**: ファイアウォール設定を確認
3. **パフォーマンス問題**: リソース配分を調整

### ログ確認方法
```bash
# アプリケーションログ
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# エラーログのみ
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=20
```

## セキュリティ設定

### SSL証明書
```bash
# Let's Encrypt証明書取得
gcloud compute ssl-certificates create therapeutic-gaming-ssl   --domains=your-domain.com
```

### WAF設定
```bash
# Cloud Armor設定
gcloud compute security-policies create therapeutic-gaming-waf   --description="WAF for therapeutic gaming app"
```

## 連絡先
デプロイメントに関する問題は以下にお問い合わせください：
- **DevOpsチーム**: devops@therapeutic-gaming.com
- **緊急時**: emergency@therapeutic-gaming.com
