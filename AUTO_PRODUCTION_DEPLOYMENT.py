#!/usr/bin/env python3
"""
🚀 治療的ゲーミフィケーションアプリ 自動本番デプロイメント

このスクリプトを実行すると、実際の本番環境が自動構築されます。
事前にGoogle Cloudアカウントとgcloud CLIの設定が必要です。
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class AutoProductionDeployment:
    def __init__(self):
        self.project_id = "therapeutic-gamification-app"
        self.region = "asia-northeast1"
        self.services = [
            "auth", "core-game", "task-mgmt", "mandala", "mood-tracking",
            "ai-story", "story-dag", "therapeutic-safety", "adhd-support",
            "line-bot", "guardian-portal", "kpi-dashboard", "performance-monitoring",
            "gdpr-compliance", "alpha-playtest", "edge-ai-cache"
        ]
        self.deployment_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        
        if level == "ERROR":
            print(f"❌ {message}")
        elif level == "SUCCESS":
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """コマンド実行"""
        self.log(f"実行中: {command}")
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                check=check
            )
            if result.returncode == 0:
                self.log(f"成功: {command}", "SUCCESS")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"エラー: {command} - {e}", "ERROR")
            raise
    
    def check_prerequisites(self) -> bool:
        """前提条件チェック"""
        self.log("前提条件をチェック中...")
        
        try:
            # gcloud CLIの確認
            result = self.run_command("gcloud version", check=False)
            if result.returncode != 0:
                self.log("gcloud CLIがインストールされていません", "ERROR")
                return False
            
            # 認証確認
            result = self.run_command("gcloud auth list", check=False)
            if "ACTIVE" not in result.stdout:
                self.log("Google Cloudにログインしてください: gcloud auth login", "ERROR")
                return False
            
            self.log("前提条件チェック完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"前提条件チェックエラー: {e}", "ERROR")
            return False
    
    def create_project(self) -> bool:
        """プロジェクト作成"""
        self.log("Google Cloudプロジェクト作成中...")
        
        try:
            # プロジェクト作成
            self.run_command(f"gcloud projects create {self.project_id} --name=治療的ゲーミフィケーションアプリ")
            
            # プロジェクト設定
            self.run_command(f"gcloud config set project {self.project_id}")
            
            self.log("プロジェクト作成完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"プロジェクト作成エラー: {e}", "ERROR")
            return False
    
    def setup_billing(self) -> bool:
        """課金設定"""
        self.log("課金設定中...")
        
        try:
            # 課金アカウント一覧取得
            result = self.run_command("gcloud billing accounts list")
            
            if "ACCOUNT_ID" not in result.stdout:
                self.log("課金アカウントが見つかりません。Google Cloud Consoleで設定してください。", "ERROR")
                return False
            
            # 最初の課金アカウントを使用
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                account_id = lines[1].split()[0]
                self.run_command(f"gcloud billing projects link {self.project_id} --billing-account={account_id}")
                self.log("課金設定完了", "SUCCESS")
                return True
            else:
                self.log("有効な課金アカウントがありません", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"課金設定エラー: {e}", "ERROR")
            return False
    
    def enable_apis(self) -> bool:
        """API有効化"""
        self.log("必要なAPIを有効化中...")
        
        apis = [
            "run.googleapis.com",
            "cloudbuild.googleapis.com",
            "firestore.googleapis.com",
            "secretmanager.googleapis.com",
            "monitoring.googleapis.com",
            "logging.googleapis.com",
            "cloudkms.googleapis.com",
            "firebase.googleapis.com"
        ]
        
        try:
            for api in apis:
                self.run_command(f"gcloud services enable {api}")
                time.sleep(2)  # API有効化の待機
            
            self.log("API有効化完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"API有効化エラー: {e}", "ERROR")
            return False
    
    def setup_firestore(self) -> bool:
        """Firestore設定"""
        self.log("Firestoreデータベース作成中...")
        
        try:
            self.run_command(f"gcloud firestore databases create --region={self.region}")
            self.log("Firestore設定完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Firestore設定エラー: {e}", "ERROR")
            return False
    
    def create_secrets(self) -> bool:
        """シークレット作成"""
        self.log("シークレット作成中...")
        
        try:
            # JWT シークレット
            jwt_secret = "your-super-secret-jwt-key-change-this-in-production"
            with open("jwt-secret.txt", "w") as f:
                f.write(jwt_secret)
            
            self.run_command("gcloud secrets create jwt-secret --data-file=jwt-secret.txt")
            os.remove("jwt-secret.txt")
            
            # LINE Bot シークレット（プレースホルダー）
            line_secret = "your-line-bot-channel-secret"
            with open("line-secret.txt", "w") as f:
                f.write(line_secret)
            
            self.run_command("gcloud secrets create line-bot-secret --data-file=line-secret.txt")
            os.remove("line-secret.txt")
            
            self.log("シークレット作成完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"シークレット作成エラー: {e}", "ERROR")
            return False
    
    def build_images(self) -> bool:
        """Dockerイメージビルド"""
        self.log("Dockerイメージビルド中...")
        
        try:
            for service in self.services:
                service_path = f"services/{service}"
                if os.path.exists(service_path):
                    self.log(f"{service}サービスをビルド中...")
                    
                    # Dockerfileが存在しない場合は作成
                    dockerfile_path = f"{service_path}/Dockerfile"
                    if not os.path.exists(dockerfile_path):
                        self.create_dockerfile(service_path, service)
                    
                    # Cloud Buildでビルド
                    self.run_command(f"gcloud builds submit --tag gcr.io/{self.project_id}/{service}:latest {service_path}")
                else:
                    self.log(f"サービスディレクトリが見つかりません: {service_path}", "ERROR")
            
            self.log("Dockerイメージビルド完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Dockerイメージビルドエラー: {e}", "ERROR")
            return False
    
    def create_dockerfile(self, service_path: str, service_name: str):
        """Dockerfileを作成"""
        dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
"""
        
        with open(f"{service_path}/Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # requirements.txtも作成
        requirements_content = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
google-cloud-firestore==2.13.1
google-cloud-secret-manager==2.17.0
"""
        
        with open(f"{service_path}/requirements.txt", "w") as f:
            f.write(requirements_content)
    
    def deploy_services(self) -> bool:
        """Cloud Runサービスデプロイ"""
        self.log("Cloud Runサービスデプロイ中...")
        
        try:
            for service in self.services:
                self.log(f"{service}サービスをデプロイ中...")
                
                deploy_cmd = f"""gcloud run deploy {service} 
                    --image gcr.io/{self.project_id}/{service}:latest 
                    --platform managed 
                    --region {self.region} 
                    --allow-unauthenticated 
                    --memory 2Gi 
                    --cpu 1 
                    --max-instances 100 
                    --min-instances 1 
                    --set-env-vars ENVIRONMENT=production,PROJECT_ID={self.project_id},REGION={self.region}""".replace('\n', ' ')
                
                self.run_command(deploy_cmd)
            
            self.log("Cloud Runサービスデプロイ完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Cloud Runサービスデプロイエラー: {e}", "ERROR")
            return False
    
    def setup_monitoring(self) -> bool:
        """監視設定"""
        self.log("監視システム設定中...")
        
        try:
            # Cloud Monitoringは自動的に有効化される
            self.log("監視システム設定完了", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"監視システム設定エラー: {e}", "ERROR")
            return False
    
    def get_service_urls(self) -> Dict[str, str]:
        """サービスURL取得"""
        urls = {}
        
        try:
            for service in self.services:
                result = self.run_command(f"gcloud run services describe {service} --region {self.region} --format='value(status.url)'")
                if result.stdout.strip():
                    urls[service] = result.stdout.strip()
            
            return urls
            
        except Exception as e:
            self.log(f"サービスURL取得エラー: {e}", "ERROR")
            return {}
    
    def generate_deployment_report(self, urls: Dict[str, str]) -> str:
        """デプロイメントレポート生成"""
        report = f"""
# 🎉 本番デプロイメント完了レポート

## 📊 デプロイメント情報
- **プロジェクトID**: {self.project_id}
- **リージョン**: {self.region}
- **デプロイ日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **デプロイ済みサービス**: {len(self.services)}個

## 🌐 サービスURL
"""
        
        for service, url in urls.items():
            report += f"- **{service}**: {url}\n"
        
        report += f"""
## 📝 次のステップ
1. **ドメイン設定**: カスタムドメインを設定してください
2. **LINE Bot設定**: LINE Developers Consoleで設定してください
3. **監視設定**: アラートとダッシュボードを設定してください
4. **セキュリティ設定**: WAFとSSL証明書を設定してください

## 💰 予想月額コスト
- Cloud Run: $50-200
- Firestore: $10-50
- その他: $20-50
- **合計**: $80-300/月

## 🔗 管理リンク
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project={self.project_id})
- [Cloud Run](https://console.cloud.google.com/run?project={self.project_id})
- [Firestore](https://console.cloud.google.com/firestore?project={self.project_id})
- [Monitoring](https://console.cloud.google.com/monitoring?project={self.project_id})
"""
        
        return report
    
    def execute_deployment(self) -> bool:
        """デプロイメント実行"""
        print("🚀 治療的ゲーミフィケーションアプリ 自動本番デプロイメント開始")
        print("=" * 80)
        
        steps = [
            ("前提条件チェック", self.check_prerequisites),
            ("プロジェクト作成", self.create_project),
            ("課金設定", self.setup_billing),
            ("API有効化", self.enable_apis),
            ("Firestore設定", self.setup_firestore),
            ("シークレット作成", self.create_secrets),
            ("Dockerイメージビルド", self.build_images),
            ("Cloud Runサービスデプロイ", self.deploy_services),
            ("監視システム設定", self.setup_monitoring)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"❌ {step_name}に失敗しました")
                return False
            print(f"✅ {step_name}完了")
        
        # サービスURL取得
        print("\n🔍 サービスURL取得中...")
        urls = self.get_service_urls()
        
        # レポート生成
        report = self.generate_deployment_report(urls)
        
        with open("deployment_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n" + "=" * 80)
        print("🎉 デプロイメント完了！")
        print("=" * 80)
        print(f"📊 デプロイ済みサービス: {len(self.services)}個")
        print(f"📝 詳細レポート: deployment_report.md")
        print("\n🌐 主要サービスURL:")
        
        key_services = ["core-game", "guardian-portal", "kpi-dashboard"]
        for service in key_services:
            if service in urls:
                print(f"   {service}: {urls[service]}")
        
        return True

def main():
    """メイン実行"""
    deployment = AutoProductionDeployment()
    
    try:
        success = deployment.execute_deployment()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ デプロイメントが中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())