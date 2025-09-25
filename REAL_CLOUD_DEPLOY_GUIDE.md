# 🚀 治療ゲーミフィケーションアプリ 本格クラウドデプロイガイド

## 📋 事前準備チェックリスト

### 1. 必要なアカウント
- [ ] Googleアカウント（Gmail等）
- [ ] Google Cloudアカウント（無料枠あり）
- [ ] OpenAI APIアカウント（ChatGPT API用）
- [ ] LINE Developersアカウント（LINE Bot用）

### 2. 必要な情報
- [ ] クレジットカード（Google Cloud用、無料枠内でも必要）
- [ ] 電話番号（認証用）

## 🎯 ステップ1: Google Cloudアカウント設定

### 1-1. Google Cloudコンソールにアクセス
1. ブラウザで https://console.cloud.google.com/ にアクセス
2. Googleアカウントでログイン
3. 利用規約に同意

### 1-2. 新しいプロジェクト作成
1. 画面上部の「プロジェクトを選択」をクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名: `therapeutic-gamification-app`
4. 「作成」をクリック

### 1-3. 請求先アカウント設定
1. 左メニューから「お支払い」を選択
2. 「請求先アカウントをリンク」をクリック
3. クレジットカード情報を入力（無料枠内で使用予定）
4. 住所情報を入力

## 🎯 ステップ2: 必要なAPIの有効化

### 2-1. Cloud Shell起動
1. Google Cloudコンソール右上の「Cloud Shell」アイコンをクリック
2. ターミナルが画面下部に表示されるまで待機

### 2-2. APIの一括有効化
Cloud Shellで以下のコマンドを実行：

```bash
# プロジェクトIDを設定
gcloud config set project therapeutic-gamification-app

# 必要なAPIを一括有効化
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudkms.googleapis.com \
  cloudsecurity.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com
```

## 🎯 ステップ3: OpenAI API設定

### 3-1. OpenAIアカウント作成
1. https://platform.openai.com/ にアクセス
2. 「Sign up」でアカウント作成
3. 電話番号認証を完了

### 3-2. APIキー取得
1. https://platform.openai.com/api-keys にアクセス
2. 「Create new secret key」をクリック
3. 名前: `therapeutic-app`
4. APIキーをコピー（後で使用）

### 3-3. 使用量制限設定
1. https://platform.openai.com/usage にアクセス
2. 「Usage limits」で月額上限を設定（例：$10）

## 🎯 ステップ4: LINE Bot設定

### 4-1. LINE Developersアカウント作成
1. https://developers.line.biz/ にアクセス
2. LINEアカウントでログイン
3. 開発者登録を完了

### 4-2. プロバイダー作成
1. 「プロバイダー」タブで「作成」をクリック
2. プロバイダー名: `TherapeuticApp`
3. 「作成」をクリック

### 4-3. Messaging APIチャネル作成
1. 「Messaging API」を選択
2. チャネル名: `治療ゲーミフィケーションBot`
3. チャネル説明: `ADHD支援のための治療的ゲームBot`
4. 大業種: `教育・学習支援業`
5. 小業種: `その他の教育・学習支援業`
6. 「作成」をクリック

### 4-4. チャネル設定
1. 作成したチャネルを選択
2. 「チャネル基本設定」タブで以下を設定：
   - 応答メッセージ: `無効`
   - あいさつメッセージ: `無効`
   - Webhook: `有効`
3. 「Messaging API設定」タブで：
   - チャネルアクセストークンを発行・コピー
   - チャネルシークレットをコピー

## 🎯 ステップ5: Firestore設定

### 5-1. Firestoreデータベース作成
1. Google Cloudコンソールで「Firestore」を検索
2. 「データベースの作成」をクリック
3. 「ネイティブモード」を選択
4. ロケーション: `asia-northeast1 (Tokyo)`
5. 「作成」をクリック

### 5-2. セキュリティルール設定
1. 「ルール」タブを選択
2. 以下のルールを設定：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザーは自分のデータのみアクセス可能
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // タスクは認証済みユーザーのみアクセス可能
    match /tasks/{taskId} {
      allow read, write: if request.auth != null;
    }
    
    // ストーリーは認証済みユーザーのみアクセス可能
    match /stories/{storyId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 🎯 ステップ6: Secret Manager設定

Cloud Shellで以下のコマンドを実行：

```bash
# OpenAI APIキーを保存
echo "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-

# LINE Bot設定を保存
echo "YOUR_LINE_CHANNEL_ACCESS_TOKEN" | gcloud secrets create line-channel-access-token --data-file=-
echo "YOUR_LINE_CHANNEL_SECRET" | gcloud secrets create line-channel-secret --data-file=-

# Firestore設定を保存
echo "therapeutic-gamification-app" | gcloud secrets create firestore-project-id --data-file=-
```

**注意**: `YOUR_OPENAI_API_KEY`等は実際の値に置き換えてください。

## 🎯 ステップ7: アプリケーションデプロイ

### 7-1. ソースコードのアップロード
1. Cloud Shellで以下を実行：

```bash
# GitHubからソースコードをクローン（または手動アップロード）
git clone https://github.com/YOUR_USERNAME/therapeutic-gamification-app.git
cd therapeutic-gamification-app
```

### 7-2. 環境変数設定
```bash
# 環境変数ファイル作成
cat > .env << EOF
OPENAI_API_KEY=\$(gcloud secrets versions access latest --secret="openai-api-key")
LINE_CHANNEL_ACCESS_TOKEN=\$(gcloud secrets versions access latest --secret="line-channel-access-token")
LINE_CHANNEL_SECRET=\$(gcloud secrets versions access latest --secret="line-channel-secret")
FIRESTORE_PROJECT_ID=therapeutic-gamification-app
ENVIRONMENT=production
EOF
```

### 7-3. Dockerファイル作成
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
```

### 7-4. Cloud Runデプロイ
```bash
# アプリケーションをCloud Runにデプロイ
gcloud run deploy therapeutic-app \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="$(gcloud secrets versions access latest --secret='openai-api-key')" \
  --set-env-vars LINE_CHANNEL_ACCESS_TOKEN="$(gcloud secrets versions access latest --secret='line-channel-access-token')" \
  --set-env-vars LINE_CHANNEL_SECRET="$(gcloud secrets versions access latest --secret='line-channel-secret')" \
  --set-env-vars FIRESTORE_PROJECT_ID=therapeutic-gamification-app
```

## 🎯 ステップ8: LINE Bot Webhook設定

### 8-1. デプロイ完了後のURL取得
デプロイ完了後、表示されるURLをコピー（例：https://therapeutic-app-xxx-an.a.run.app）

### 8-2. LINE DevelopersでWebhook URL設定
1. LINE Developersコンソールに戻る
2. 「Messaging API設定」タブ
3. Webhook URL: `https://YOUR_CLOUD_RUN_URL/webhook`
4. 「検証」をクリックして成功を確認

## 🎯 ステップ9: 動作確認

### 9-1. Webアプリアクセス
ブラウザで Cloud Run URL にアクセス

### 9-2. LINE Bot友達追加
1. LINE Developersコンソールで QR コードを表示
2. LINEアプリでQRコードをスキャン
3. 友達追加

### 9-3. 基本機能テスト
- タスク作成・完了
- XP獲得
- レベルアップ
- ストーリー生成

## 🚨 トラブルシューティング

### よくある問題と解決方法

**問題**: デプロイエラー
**解決**: ログを確認 `gcloud run logs read --service=therapeutic-app`

**問題**: LINE Botが反応しない
**解決**: Webhook URLが正しく設定されているか確認

**問題**: OpenAI APIエラー
**解決**: APIキーが正しく設定されているか確認

## 💰 料金について

### 無料枠内での利用
- Google Cloud: 月額$300の無料クレジット（初回）
- OpenAI: 月額$5の無料クレジット（初回）
- LINE Messaging API: 月1000通まで無料

### 予想月額料金（無料枠後）
- Google Cloud Run: $5-20
- OpenAI API: $10-50
- LINE Messaging API: $0-10
- **合計**: $15-80/月

## 🎉 完了！

すべてのステップが完了すると、実際にインターネット上でアクセス可能な治療ゲーミフィケーションアプリが完成します！

---

**次のステップ**: 実際の設定を始めましょう！