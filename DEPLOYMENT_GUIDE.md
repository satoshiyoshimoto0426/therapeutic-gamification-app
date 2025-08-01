# GitHub Secrets 設定ガイド

## 🔧 必要なSecrets設定

GitHubリポジトリの **Settings > Secrets and variables > Actions** で以下を設定してください：

### 1. GCP_PROJECT_ID
```
therapeutic-gamification-app-prod
```

### 2. GCP_SA_KEY
以下の手順でサービスアカウントキーを生成し、JSON全体をコピー&ペーストしてください：

```bash
# 1. GCPプロジェクト設定
gcloud config set project therapeutic-gamification-app-prod

# 2. サービスアカウント作成
gcloud iam service-accounts create github-actions \
    --description="GitHub Actions CI/CD" \
    --display-name="GitHub Actions"

# 3. 権限付与
for role in "roles/run.admin" "roles/cloudbuild.builds.editor" "roles/storage.admin" "roles/iam.serviceAccountUser" "roles/datastore.owner" "roles/secretmanager.admin" "roles/logging.viewer"; do
    gcloud projects add-iam-policy-binding therapeutic-gamification-app-prod \
        --member="serviceAccount:github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com" \
        --role="$role"
done

# 4. キーファイル生成
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com

# 5. キーファイル内容をコピー
cat github-actions-key.json
```

### 3. SLACK_WEBHOOK (オプション)
Slack通知用のWebhook URLを設定してください。

## 🚀 デプロイメント実行手順

1. **ファイル準備完了** ✅
   - requirements.txt
   - Dockerfile
   - .dockerignore
   - deployment_trigger.txt

2. **GitHub Secrets設定**
   - 上記の手順でGCP_PROJECT_IDとGCP_SA_KEYを設定

3. **GitHubにプッシュ**
   ```bash
   git add .
   git commit -m "feat: setup automatic deployment - 2025-08-01 12:06:16"
   git push origin main
   ```

4. **デプロイメント監視**
   - GitHub ActionsタブでCI/CDパイプラインの進行状況を確認
   - 通常15-20分でデプロイ完了
   - エラー時は自動ロールバック実行

## 📊 デプロイメント後の確認

1. **サービス確認**
   - Cloud Runコンソールでサービス状態確認
   - サービスURLにアクセスして動作確認

2. **ログ確認**
   - Cloud Loggingでアプリケーションログ確認
   - エラーがないかチェック

3. **パフォーマンステスト**
   - 基本機能の動作確認
   - レスポンス時間の確認

## 🆘 トラブルシューティング

### よくある問題

1. **権限エラー**
   - サービスアカウントの権限を再確認
   - 必要なAPIが有効化されているか確認

2. **ビルドエラー**
   - requirements.txtの依存関係を確認
   - Dockerfileの構文を確認

3. **デプロイエラー**
   - Cloud Runの設定を確認
   - メモリ・CPU制限を確認

---

**準備完了！** 上記の手順に従ってデプロイを実行してください。
