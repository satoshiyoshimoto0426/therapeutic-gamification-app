#!/usr/bin/env python3
"""
シンプルなCloud Runデプロイメントスクリプト
"""

import subprocess
import sys
import os

def run_command(cmd, capture_output=True):
    """コマンドを実行して結果を返す"""
    try:
        print(f"🔧 実行中: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        if result.stdout:
            print(f"📤 出力: {result.stdout}")
        if result.stderr and result.returncode != 0:
            print(f"⚠️ エラー: {result.stderr}")
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def create_simple_app():
    """シンプルなFlaskアプリを作成"""
    print("📝 シンプルなアプリファイルを作成中...")
    
    # main.py作成
    main_py = '''from flask import Flask, jsonify
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
'''
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(main_py)
    
    # Dockerfile作成
    dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
RUN pip install flask gunicorn

# アプリケーションファイルをコピー
COPY . .

# ポートを公開
EXPOSE 8080

# Gunicornでアプリを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "main:app"]
'''
    
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(dockerfile)
    
    print("✅ アプリファイルが作成されました")

def main():
    print("🚀 シンプルなCloud Runデプロイメントを開始...")
    
    # プロジェクト確認
    stdout, stderr, code = run_command("gcloud config get-value project")
    if code != 0 or not stdout or stdout == "YOUR_EXISTING_PROJECT_ID":
        print("❌ プロジェクトが正しく設定されていません")
        print("先にプロジェクト設定を修正してください")
        return
    
    project_id = stdout
    print(f"✅ プロジェクト: {project_id}")
    
    # アプリファイル作成
    create_simple_app()
    
    # 必要なAPIを有効化
    print("📡 必要なAPIを有効化中...")
    apis = ["run.googleapis.com", "cloudbuild.googleapis.com"]
    for api in apis:
        run_command(f"gcloud services enable {api}")
    
    # Cloud Runにデプロイ
    print("🚀 Cloud Runにデプロイ中...")
    deploy_cmd = f"""gcloud run deploy therapeutic-app \\
        --source . \\
        --region asia-northeast1 \\
        --allow-unauthenticated \\
        --port 8080 \\
        --memory 512Mi \\
        --cpu 1 \\
        --max-instances 5 \\
        --timeout 300"""
    
    stdout, stderr, code = run_command(deploy_cmd, capture_output=False)
    
    if code == 0:
        print("✅ デプロイが完了しました！")
        
        # サービスURLを取得
        stdout, stderr, code = run_command(f"gcloud run services describe therapeutic-app --region=asia-northeast1 --format='value(status.url)'")
        if code == 0 and stdout:
            print(f"🌐 アプリURL: {stdout}")
            print(f"🔗 ヘルスチェック: {stdout}/health")
            print(f"🧪 テストAPI: {stdout}/api/test")
    else:
        print("❌ デプロイに失敗しました")

if __name__ == "__main__":
    main()