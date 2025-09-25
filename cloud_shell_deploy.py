#!/usr/bin/env python3
"""
🎮 治療的ゲーミフィケーションアプリ Cloud Shell デプロイメント
"""
import subprocess
import sys
import os
import time
from datetime import datetime

class CloudShellDeployment:
    def __init__(self):
        self.project_id = "therapeutic-gamification-app"
        self.region = "asia-northeast1"
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if level == "ERROR":
            print(f"❌ [{timestamp}] {message}")
        elif level == "SUCCESS":
            print(f"✅ [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")
    
    def run_command(self, command):
        self.log(f"実行中: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"成功: {command}", "SUCCESS")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log(f"エラー: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"例外エラー: {e}", "ERROR")
            return False
    
    def enable_apis(self):
        self.log("必要なAPIを有効化中...")
        apis = [
            "run.googleapis.com",
            "cloudbuild.googleapis.com", 
            "firestore.googleapis.com",
            "secretmanager.googleapis.com",
            "monitoring.googleapis.com",
            "logging.googleapis.com"
        ]
        
        for api in apis:
            if self.run_command(f"gcloud services enable {api}"):
                self.log(f"{api} 有効化完了", "SUCCESS")
            time.sleep(2)
    
    def setup_firestore(self):
        self.log("Firestore設定中...")
        return self.run_command(f"gcloud firestore databases create --region={self.region}")
    
    def create_sample_service(self):
        self.log("サンプルサービス作成中...")
        
        # サンプルアプリ作成
        app_code = '''
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "🎮 治療的ゲーミフィケーションアプリ",
        "status": "running",
        "version": "1.0.0",
        "environment": "production"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
'''
        
        dockerfile = '''
FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
'''
        
        # ファイル作成
        with open('main.py', 'w') as f:
            f.write(app_code)
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile)
        
        self.log("サンプルアプリ作成完了", "SUCCESS")
        return True
    
    def deploy_to_cloud_run(self):
        self.log("Cloud Runにデプロイ中...")
        
        # Cloud Buildでビルド&デプロイ
        deploy_cmd = f"""
        gcloud run deploy therapeutic-game-app \
            --source . \
            --platform managed \
            --region {self.region} \
            --allow-unauthenticated \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 10
        """
        
        return self.run_command(deploy_cmd)
    
    def get_service_url(self):
        self.log("サービスURL取得中...")
        try:
            result = subprocess.run(
                f"gcloud run services describe therapeutic-game-app --region {self.region} --format='value(status.url)'",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                self.log(f"サービスURL: {url}", "SUCCESS")
                return url
            return None
        except:
            return None
    
    def deploy(self):
        print("🚀 治療的ゲーミフィケーションアプリ Cloud Shell デプロイメント開始")
        print("=" * 80)
        
        steps = [
            ("API有効化", self.enable_apis),
            ("Firestore設定", self.setup_firestore),
            ("サンプルサービス作成", self.create_sample_service),
            ("Cloud Runデプロイ", self.deploy_to_cloud_run)
        ]
        
        for step_name, step_func in steps:
            self.log(f"ステップ開始: {step_name}")
            if step_func():
                self.log(f"ステップ完了: {step_name}", "SUCCESS")
            else:
                self.log(f"ステップ失敗: {step_name}", "ERROR")
                return False
        
        # 結果表示
        url = self.get_service_url()
        print("\n" + "=" * 80)
        print("🎉 デプロイメント完了！")
        print("=" * 80)
        print(f"✅ プロジェクト: {self.project_id}")
        print(f"✅ リージョン: {self.region}")
        if url:
            print(f"✅ アプリURL: {url}")
            print(f"✅ ヘルスチェック: {url}/health")
        print("=" * 80)
        
        return True

if __name__ == "__main__":
    deployment = CloudShellDeployment()
    success = deployment.deploy()
    sys.exit(0 if success else 1)