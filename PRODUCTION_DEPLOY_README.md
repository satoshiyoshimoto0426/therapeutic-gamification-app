# 🚀 治療的ゲーミフィケーションアプリ - 本番デプロイガイド

## 📋 概要
このガイドでは、治療的ゲーミフィケーションアプリを Google Cloud Run に本番デプロイする手順を説明します。

**プロジェクト**: `abiding-beanbag-467909-d8`

## 🎯 クイックスタート

### ステップ1: 事前チェック
```bash
# デプロイ前の最終チェック
python pre_deploy_check.py
```

### ステップ2: 本番デプロイ実行
```bash
# 本番デプロイを実行
python FINAL_PRODUCTION_DEPLOY.py
```

### ステップ3: デプロイ後監視
```bash
# デプロイ状態を監視・確認
python monitor_deployment.py
```

## 📚 詳細手順

### 🔧 事前準備

1. **Google Cloud CLI のインストール・認証**
   ```bash
   # gcloud CLI のインストール確認
   gcloud --version
   
   # 認証（必要に応じて）
   gcloud auth login
   gcloud auth application-default login
   
   # プロジェクト設定
   gcloud config set project abiding-beanbag-467909-d8
   ```

2. **必要なAPIの有効化**
   ```bash
   # 自動で全APIを有効化
   python enable_all_google_cloud_apis.py
   
   # または PowerShell で
   .\quick_api_enable.ps1
   ```

3. **ファイル構成の確認**
   - ✅ `Dockerfile` - コンテナ設定
   - ✅ `pyproject.toml` - Python依存関係
   - ✅ `shared/` - 共有ライブラリ
   - ✅ `services/` - マイクロサービス
   - ✅ `frontend/` - フロントエンド

### 🚀 デプロイプロセス

#### 1. 事前チェック実行
```bash
python pre_deploy_check.py
```

**チェック項目:**
- ✅ 必要ファイルの存在確認
- ✅ Docker設定の検証
- ✅ gcloud認証状態
- ✅ Google Cloud APIs有効化状態
- ✅ 依存関係の確認

#### 2. 本番デプロイ実行
```bash
python FINAL_PRODUCTION_DEPLOY.py
```

**デプロイ処理:**
1. 前提条件の最終確認
2. Google Cloud APIs状態確認
3. Firestoreデータベース設定
4. IAM権限設定
5. Cloud Runへのデプロイ
6. デプロイメントテスト
7. レポート生成

#### 3. デプロイ後監視
```bash
python monitor_deployment.py
```

**監視項目:**
- 🔍 Cloud Runサービス状態
- 🔍 エンドポイント応答テスト
- 🔍 ログ確認
- 🔍 基本メトリクス
- 📊 監視レポート生成

## 🎛️ 設定詳細

### Cloud Run設定
- **リージョン**: `asia-northeast1`
- **メモリ**: `2Gi`
- **CPU**: `2`
- **タイムアウト**: `3600秒`
- **同時実行数**: `100`
- **最大インスタンス**: `10`

### 環境変数
- `PROJECT_ID`: `abiding-beanbag-467909-d8`
- `ENVIRONMENT`: `production`

### 必要な権限
- `roles/datastore.user` - Firestore アクセス
- `roles/logging.logWriter` - ログ書き込み
- `roles/monitoring.metricWriter` - メトリクス書き込み
- `roles/cloudtrace.agent` - トレース

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. API未有効化エラー
```
ERROR: API [run.googleapis.com] not enabled
```
**解決**: APIを有効化
```bash
python enable_all_google_cloud_apis.py
```

#### 2. 認証エラー
```
ERROR: Your current active account does not have any valid credentials
```
**解決**: 再認証
```bash
gcloud auth login
gcloud auth application-default login
```

#### 3. 権限エラー
```
ERROR: does not have permission to access
```
**解決**: 権限確認・付与
```bash
gcloud projects get-iam-policy abiding-beanbag-467909-d8
```

#### 4. ビルドエラー
```
ERROR: build failed
```
**解決**: Dockerfileとソースコードを確認

#### 5. デプロイタイムアウト
```
ERROR: deployment timed out
```
**解決**: リソース設定を調整、または再実行

### ログ確認方法
```bash
# Cloud Runログ確認
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# 特定サービスのログ
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=therapeutic-gamification-app" --limit=20
```

### サービス状態確認
```bash
# サービス一覧
gcloud run services list --region=asia-northeast1

# サービス詳細
gcloud run services describe therapeutic-gamification-app --region=asia-northeast1
```

## 📊 監視・運用

### 継続監視
```bash
# 定期的な状態確認
python monitor_deployment.py

# ログ監視
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=therapeutic-gamification-app"
```

### パフォーマンステスト
```bash
# 基本的な負荷テスト（サービスURL取得後）
curl -w "@curl-format.txt" -o /dev/null -s "https://your-service-url/"
```

### アラート設定
Google Cloud Console でアラートポリシーを設定:
- CPU使用率 > 80%
- メモリ使用率 > 80%
- エラー率 > 5%
- レスポンス時間 > 5秒

## 🎉 成功確認

デプロイが成功すると以下が表示されます:

```
🎉 デプロイ完了！
✅ サービスURL: https://therapeutic-gamification-app-xxx-an.a.run.app
ℹ️  ブラウザでアクセスして動作を確認してください！

📋 次のステップ:
1. サービスの動作確認
2. 監視・アラートの設定
3. ドメインの設定（必要に応じて）
4. パフォーマンステスト

🎯 デプロイ成功！おめでとうございます！
```

## 📁 生成されるファイル

デプロイ実行後、以下のファイルが生成されます:
- `deployment_report.json` - デプロイレポート
- `monitoring_report.json` - 監視レポート

## 🔗 関連リンク

- [Google Cloud Console](https://console.cloud.google.com/run?project=abiding-beanbag-467909-d8)
- [Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Firestore ドキュメント](https://cloud.google.com/firestore/docs)

## 📞 サポート

問題が発生した場合:
1. エラーメッセージを確認
2. ログを確認 (`gcloud logs read`)
3. Google Cloud Console で状態確認
4. 必要に応じて再デプロイ実行

---

**🎯 今度こそ完璧にデプロイを成功させましょう！**