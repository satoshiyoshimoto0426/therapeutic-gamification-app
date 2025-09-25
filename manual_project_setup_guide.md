# 🚀 手動プロジェクト設定ガイド

## 🚫 まず現在の質問をキャンセル
Cloud Shellで以下を入力してください：
```bash
n
```

## 🔍 プロジェクトIDを確認・設定

### 1. 利用可能なプロジェクト一覧を確認
```bash
gcloud projects list
```

### 2. 現在のプロジェクト確認
```bash
gcloud config get-value project
```

### 3. 正しいプロジェクトIDを設定
上記で表示されたプロジェクトIDを使用して設定してください：
```bash
# 例：プロジェクトIDが "my-therapeutic-app-123456" の場合
gcloud config set project my-therapeutic-app-123456
```

### 4. 設定確認
```bash
gcloud config get-value project
```

## 🚀 必要なAPIを有効化
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 📝 シンプルなアプリファイルを作成

### main.py
```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "🎮 Therapeutic Gamification App",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/test')
def test():
    return jsonify({
        "test": "success",
        "message": "APIが正常に動作しています"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
RUN pip install flask gunicorn

# アプリケーションファイルをコピー
COPY . .

# ポートを公開
EXPOSE 8080

# Gunicornでアプリを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "main:app"]
```

## 🚀 Cloud Runにデプロイ
```bash
gcloud run deploy therapeutic-app \
    --source . \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --timeout 300
```

## 📋 重要なポイント

1. **「n」と入力** - 現在の設定をキャンセル
2. **`gcloud projects list`** - 利用可能なプロジェクトを確認
3. **実際のプロジェクトIDを使用** - `YOUR_EXISTING_PROJECT_ID` を実際のIDに置き換え
4. **APIを有効化** - 必要なGoogle Cloud APIを有効化
5. **シンプルなアプリを作成** - 最小限のFlaskアプリでテスト

## 🔧 トラブルシューティング

### プロジェクトが見つからない場合
```bash
# 新しいプロジェクトを作成
gcloud projects create therapeutic-app-$(date +%s) --name="Therapeutic App"

# 作成したプロジェクトを設定
gcloud config set project therapeutic-app-$(date +%s)
```

### 権限エラーの場合
```bash
# 認証を再実行
gcloud auth login

# アプリケーションデフォルト認証を設定
gcloud auth application-default login
```

まず **「n」** と入力して、プロジェクト設定を修正しましょう！🚀