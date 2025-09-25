# 🚀 クイック本番セットアップ手順

## 📋 事前準備（5分）

### 1. Google Cloudアカウント作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. Googleアカウントでログイン
3. 無料トライアル開始（$300クレジット付与）

### 2. gcloud CLI インストール
```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 3. 認証設定
```bash
gcloud auth login
gcloud auth application-default login
```

## 🎯 ワンクリックデプロイメント

### 自動デプロイメント実行
```bash
python AUTO_PRODUCTION_DEPLOYMENT.py
```

**これだけで完了！** 約15-30分で本番環境が構築されます。

## 📊 デプロイメント内容

### 自動作成されるもの
- ✅ Google Cloudプロジェクト
- ✅ 課金設定
- ✅ 必要なAPI有効化
- ✅ Firestoreデータベース
- ✅ 16個のマイクロサービス
- ✅ Cloud Runデプロイメント
- ✅ 監視システム
- ✅ セキュリティ設定

### デプロイ後のURL例
```
https://core-game-xxx-an.a.run.app          # メインアプリ
https://guardian-portal-xxx-an.a.run.app    # 保護者ポータル
https://kpi-dashboard-xxx-an.a.run.app      # KPIダッシュボード
https://line-bot-xxx-an.a.run.app           # LINE Bot
```

## 🔧 追加設定（オプション）

### カスタムドメイン設定
```bash
# ドメインを取得後
gcloud run domain-mappings create \
  --service core-game \
  --domain your-domain.com \
  --region asia-northeast1
```

### LINE Bot設定
1. [LINE Developers Console](https://developers.line.biz/) でチャンネル作成
2. Webhook URL設定: `https://line-bot-xxx-an.a.run.app/webhook`
3. Channel SecretとAccess Tokenを取得
4. Google Secret Managerに保存

## 💰 コスト管理

### 予算アラート設定
```bash
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="治療的ゲーミフィケーションアプリ予算" \
  --budget-amount=100USD
```

### 予想月額コスト
- **開発・テスト段階**: $20-50/月
- **本格運用開始**: $80-200/月
- **大規模運用**: $200-500/月

## 🔍 動作確認

### ヘルスチェック
```bash
# 各サービスの動作確認
curl https://core-game-xxx-an.a.run.app/health
curl https://auth-xxx-an.a.run.app/health
curl https://guardian-portal-xxx-an.a.run.app/health
```

### 管理画面アクセス
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=therapeutic-gamification-app)
- [Cloud Run Services](https://console.cloud.google.com/run?project=therapeutic-gamification-app)
- [Firestore Database](https://console.cloud.google.com/firestore?project=therapeutic-gamification-app)
- [Monitoring Dashboard](https://console.cloud.google.com/monitoring?project=therapeutic-gamification-app)

## 🆘 トラブルシューティング

### よくある問題と解決法

#### 1. 課金アカウントエラー
```bash
# 課金アカウント確認
gcloud billing accounts list

# 課金アカウント設定
gcloud billing projects link therapeutic-gamification-app --billing-account=YOUR_ACCOUNT_ID
```

#### 2. API有効化エラー
```bash
# 手動でAPI有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 3. デプロイメントエラー
```bash
# ログ確認
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# サービス再デプロイ
gcloud run deploy SERVICE_NAME --image gcr.io/therapeutic-gamification-app/SERVICE_NAME:latest --region asia-northeast1
```

## 📞 サポート

### 問題が発生した場合
1. **エラーログ確認**: `deployment_report.md` を確認
2. **Google Cloud サポート**: [サポートページ](https://cloud.google.com/support)
3. **コミュニティ**: [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)

---

**🎉 これで実際にアクセス可能な本番環境が完成します！**