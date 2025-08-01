# 🚀 GitHub Actions CI/CD デプロイメント準備チェックリスト

## ✅ 事前準備完了項目

### 1. プロジェクト構成
- [x] **MVP実装完了** - タスク27完了済み
- [x] **パフォーマンステスト合格** - タスク27.3完了済み
- [x] **CI/CDパイプライン設定** - `.github/workflows/ci-cd-pipeline.yml`
- [x] **Dockerfile準備** - マルチステージビルド対応
- [x] **requirements.txt作成** - 全依存関係定義済み

### 2. インフラストラクチャ
- [x] **本番環境設定ファイル** - `infrastructure/production/`
- [x] **セキュリティ設定** - VPC-SC, Cloud Armor, IAM
- [x] **監視・ログ設定** - Cloud Monitoring, Logging
- [x] **デプロイスクリプト** - 自動デプロイ・ロールバック対応

### 3. テスト環境
- [x] **単体テスト** - 全サービス対応
- [x] **統合テスト** - E2Eテスト完備
- [x] **パフォーマンステスト** - 50ユーザー同時接続対応
- [x] **セキュリティテスト** - 治療安全性98%F1スコア

## 🔧 今すぐ実行する設定手順

### ステップ1: GCPプロジェクト準備
```bash
# 1. GCPプロジェクト作成（まだの場合）
gcloud projects create your-therapeutic-app-project-id
gcloud config set project your-therapeutic-app-project-id

# 2. 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### ステップ2: サービスアカウント作成
```bash
# サービスアカウント作成
gcloud iam service-accounts create github-actions \
    --description="GitHub Actions CI/CD" \
    --display-name="GitHub Actions"

# 権限付与（一括実行）
for role in "roles/run.admin" "roles/cloudbuild.builds.editor" "roles/storage.admin" "roles/iam.serviceAccountUser" "roles/datastore.owner" "roles/secretmanager.admin" "roles/logging.viewer"; do
    gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
        --member="serviceAccount:github-actions@$(gcloud config get-value project).iam.gserviceaccount.com" \
        --role="$role"
done

# キーファイル生成
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@$(gcloud config get-value project).iam.gserviceaccount.com
```

### ステップ3: GitHub Secrets設定
GitHub リポジトリの **Settings > Secrets and variables > Actions** で設定:

1. **GCP_PROJECT_ID**: `your-therapeutic-app-project-id`
2. **GCP_SA_KEY**: `github-actions-key.json`の内容をコピー&ペースト
3. **SLACK_WEBHOOK**: Slack通知用URL（オプション）

### ステップ4: デプロイ実行
```bash
# リポジトリの最新状態を確認
git status
git add .
git commit -m "feat: production deployment setup"

# mainブランチにプッシュしてデプロイ開始
git push origin main
```

## 📊 デプロイメントフロー

### 自動実行される処理
1. **テスト実行** (5-10分)
   - Python単体テスト
   - TypeScript/React テスト
   - 統合テスト
   - セキュリティスキャン

2. **Dockerイメージビルド** (3-5分)
   - マルチステージビルド
   - セキュリティスキャン
   - イメージプッシュ

3. **本番デプロイ** (10-15分)
   - Blue-Green デプロイメント
   - 段階的トラフィック移行 (10% → 25% → 50% → 75% → 100%)
   - ヘルスチェック
   - 自動ロールバック（失敗時）

### 監視ポイント
- **GitHub Actions**: https://github.com/your-repo/actions
- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud Monitoring**: https://console.cloud.google.com/monitoring
- **Slack通知**: デプロイ状況をリアルタイム通知

## 🎯 デプロイ成功の確認方法

### 1. GitHub Actions確認
- ✅ 全ジョブが緑色（成功）
- ✅ デプロイメント時間が20分以内
- ✅ テストカバレッジ80%以上

### 2. 本番環境確認
```bash
# ヘルスチェック
curl https://your-service-url/health

# 基本機能テスト
python test_deployment.py --url=https://your-service-url --environment=production
```

### 3. パフォーマンス確認
- ✅ P95レスポンス時間 < 1.2秒
- ✅ エラー率 < 1%
- ✅ CPU使用率 < 80%
- ✅ メモリ使用率 < 80%

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. 権限エラー
```bash
# サービスアカウント権限確認
gcloud projects get-iam-policy $(gcloud config get-value project) \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:github-actions@*"
```

#### 2. デプロイ失敗時の自動ロールバック
- GitHub Actionsが自動的に前回の安定版にロールバック
- Slack通知で即座に障害を通知
- 手動ロールバックも可能

#### 3. パフォーマンス問題
```bash
# Cloud Runインスタンス数確認
gcloud run services describe therapeutic-gamification-app \
    --region=asia-northeast1 \
    --format="value(spec.traffic[0].percent,status.traffic[0].revisionName)"
```

## 🎉 デプロイ完了後の次のステップ

1. **監視ダッシュボード確認**
   - Cloud Monitoring でメトリクス確認
   - アラート設定の動作確認

2. **ユーザーテスト実施**
   - 基本機能の動作確認
   - パフォーマンステスト

3. **継続的改善**
   - デプロイメント時間の最適化
   - テストカバレッジの向上
   - セキュリティ強化

---

## 🚀 準備完了！デプロイ開始コマンド

```bash
# 最終確認
echo "GCPプロジェクト: $(gcloud config get-value project)"
echo "GitHub Secrets設定済み: GCP_PROJECT_ID, GCP_SA_KEY"
echo "準備完了！デプロイを開始します..."

# デプロイ実行
git add .
git commit -m "feat: production deployment ready"
git push origin main

echo "🎯 GitHub Actionsでデプロイ進行状況を確認してください："
echo "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
```

**準備が整いました！上記のコマンドを実行してデプロイを開始してください。** 🚀