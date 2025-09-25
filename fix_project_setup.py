#!/usr/bin/env python3
"""
🔧 Google Cloud プロジェクト設定修正スクリプト
"""
import subprocess
import sys
import time
from datetime import datetime

class ProjectSetupFixer:
    def __init__(self):
        self.region = "asia-northeast1"
        self.project_id = None
    
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
                return result.stdout.strip()
            else:
                self.log(f"エラー: {result.stderr}", "ERROR")
                return None
        except Exception as e:
            self.log(f"例外エラー: {e}", "ERROR")
            return None
    
    def check_current_project(self):
        self.log("現在のプロジェクト確認中...")
        result = self.run_command("gcloud config get-value project")
        if result:
            self.log(f"現在のプロジェクト: {result}", "SUCCESS")
            return result
        return None
    
    def list_available_projects(self):
        self.log("利用可能なプロジェクト一覧取得中...")
        result = self.run_command("gcloud projects list --format='value(projectId)'")
        if result:
            projects = result.split('\n')
            self.log(f"利用可能なプロジェクト: {projects}", "SUCCESS")
            return projects
        return []
    
    def create_new_project(self):
        self.log("新しいプロジェクト作成中...")
        
        # ユニークなプロジェクトID生成
        import random
        import string
        suffix = ''.join(random.choices(string.digits, k=6))
        project_id = f"therapeutic-game-{suffix}"
        
        result = self.run_command(f"gcloud projects create {project_id} --name='治療的ゲーミフィケーションアプリ'")
        if result is not None:
            self.project_id = project_id
            self.log(f"プロジェクト作成成功: {project_id}", "SUCCESS")
            return project_id
        return None
    
    def set_project(self, project_id):
        self.log(f"プロジェクト設定中: {project_id}")
        result = self.run_command(f"gcloud config set project {project_id}")
        if result is not None:
            self.project_id = project_id
            self.log(f"プロジェクト設定完了: {project_id}", "SUCCESS")
            return True
        return False
    
    def check_billing(self):
        self.log("課金アカウント確認中...")
        result = self.run_command("gcloud billing accounts list --format='value(name)'")
        if result:
            accounts = result.split('\n')
            if accounts and accounts[0]:
                self.log(f"課金アカウント見つかりました: {accounts[0]}", "SUCCESS")
                return accounts[0]
        self.log("課金アカウントが見つかりません", "ERROR")
        return None
    
    def link_billing(self, billing_account):
        if not self.project_id:
            self.log("プロジェクトIDが設定されていません", "ERROR")
            return False
        
        self.log(f"課金アカウントをリンク中: {billing_account}")
        result = self.run_command(f"gcloud billing projects link {self.project_id} --billing-account={billing_account}")
        return result is not None
    
    def enable_apis(self):
        if not self.project_id:
            self.log("プロジェクトIDが設定されていません", "ERROR")
            return False
        
        self.log("必要なAPIを有効化中...")
        apis = [
            "run.googleapis.com",
            "cloudbuild.googleapis.com", 
            "firestore.googleapis.com",
            "secretmanager.googleapis.com"
        ]
        
        for api in apis:
            result = self.run_command(f"gcloud services enable {api}")
            if result is not None:
                self.log(f"{api} 有効化完了", "SUCCESS")
            else:
                self.log(f"{api} 有効化失敗", "ERROR")
                return False
            time.sleep(2)
        return True
    
    def deploy_simple_app(self):
        if not self.project_id:
            self.log("プロジェクトIDが設定されていません", "ERROR")
            return False
        
        self.log("シンプルなアプリをデプロイ中...")
        
        # シンプルなFlaskアプリ作成
        app_code = '''
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "🎮 治療的ゲーミフィケーションアプリ",
        "status": "running",
        "project": os.environ.get('GOOGLE_CLOUD_PROJECT', 'unknown')
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
        
        # Cloud Runにデプロイ
        deploy_cmd = f"""
        gcloud run deploy therapeutic-game-app \
            --source . \
            --platform managed \
            --region {self.region} \
            --allow-unauthenticated \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 5
        """
        
        result = self.run_command(deploy_cmd)
        return result is not None
    
    def get_service_url(self):
        if not self.project_id:
            return None
        
        self.log("サービスURL取得中...")
        result = self.run_command(
            f"gcloud run services describe therapeutic-game-app --region {self.region} --format='value(status.url)'"
        )
        return result
    
    def fix_and_deploy(self):
        print("🔧 Google Cloud プロジェクト設定修正開始")
        print("=" * 80)
        
        # 1. 現在のプロジェクト確認
        current_project = self.check_current_project()
        
        # 2. 利用可能なプロジェクト確認
        available_projects = self.list_available_projects()
        
        # 3. プロジェクト設定
        if current_project and current_project in available_projects:
            self.log(f"既存のプロジェクトを使用: {current_project}", "SUCCESS")
            self.project_id = current_project
        elif available_projects:
            # 最初の利用可能なプロジェクトを使用
            project_to_use = available_projects[0]
            self.log(f"利用可能なプロジェクトを使用: {project_to_use}", "SUCCESS")
            if not self.set_project(project_to_use):
                return False
        else:
            # 新しいプロジェクトを作成
            self.log("新しいプロジェクトを作成します")
            if not self.create_new_project():
                return False
            if not self.set_project(self.project_id):
                return False
        
        # 4. 課金アカウント確認・リンク
        billing_account = self.check_billing()
        if billing_account:
            self.link_billing(billing_account)
        else:
            self.log("⚠️  課金アカウントが設定されていません。Google Cloud Consoleで設定してください。", "ERROR")
        
        # 5. API有効化
        if not self.enable_apis():
            return False
        
        # 6. シンプルなアプリをデプロイ
        if not self.deploy_simple_app():
            return False
        
        # 7. 結果表示
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
    fixer = ProjectSetupFixer()
    success = fixer.fix_and_deploy()
    sys.exit(0 if success else 1)