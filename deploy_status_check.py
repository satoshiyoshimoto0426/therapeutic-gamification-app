#!/usr/bin/env python3
"""
デプロイメント状況確認スクリプト
GitHub ActionsとCloud Runの状況を確認
"""

import subprocess
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentStatusChecker:
    """デプロイメント状況確認クラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.region = "asia-northeast1"
    
    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except FileNotFoundError:
            return False, "", f"Command not found: {command[0]}"
    
    def check_github_actions_status(self) -> Dict[str, str]:
        """GitHub Actions状況確認"""
        logger.info("GitHub Actions状況確認")
        
        status = {
            "available": "unknown",
            "latest_run": "unknown",
            "status": "unknown"
        }
        
        # GitHub CLI確認
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        
        if success:
            status["available"] = "yes"
            
            # 最新のワークフロー実行状況取得
            success, stdout, stderr = self.run_command([
                "gh", "run", "list", "--limit", "1", "--json", "status,conclusion,createdAt"
            ], check=False)
            
            if success and stdout.strip():
                try:
                    import json
                    runs = json.loads(stdout)
                    if runs:
                        latest_run = runs[0]
                        status["latest_run"] = latest_run.get("createdAt", "unknown")
                        status["status"] = f"{latest_run.get('status', 'unknown')} - {latest_run.get('conclusion', 'unknown')}"
                except:
                    pass
        else:
            status["available"] = "no"
            status["error"] = stderr
        
        return status
    
    def check_cloud_run_status(self) -> Dict[str, str]:
        """Cloud Run状況確認"""
        logger.info("Cloud Run状況確認")
        
        status = {
            "available": "unknown",
            "service_exists": "unknown",
            "service_url": "unknown",
            "latest_revision": "unknown",
            "traffic": "unknown"
        }
        
        # gcloud確認
        success, stdout, stderr = self.run_command(["gcloud", "--version"], check=False)
        
        if success:
            status["available"] = "yes"
            
            # サービス存在確認
            success, stdout, stderr = self.run_command([
                "gcloud", "run", "services", "describe", self.service_name,
                "--region", self.region,
                "--format", "json"
            ], check=False)
            
            if success:
                status["service_exists"] = "yes"
                
                try:
                    import json
                    service_info = json.loads(stdout)
                    
                    # サービスURL取得
                    if "status" in service_info and "url" in service_info["status"]:
                        status["service_url"] = service_info["status"]["url"]
                    
                    # 最新リビジョン取得
                    if "status" in service_info and "latestReadyRevisionName" in service_info["status"]:
                        status["latest_revision"] = service_info["status"]["latestReadyRevisionName"]
                    
                    # トラフィック配分取得
                    if "status" in service_info and "traffic" in service_info["status"]:
                        traffic_info = service_info["status"]["traffic"]
                        if traffic_info:
                            status["traffic"] = f"{traffic_info[0].get('percent', 0)}% to {traffic_info[0].get('revisionName', 'unknown')}"
                
                except:
                    pass
            else:
                status["service_exists"] = "no"
                if "not found" in stderr.lower():
                    status["error"] = "Service not deployed yet"
                else:
                    status["error"] = stderr
        else:
            status["available"] = "no"
            status["error"] = stderr
        
        return status
    
    def check_deployment_files(self) -> Dict[str, bool]:
        """デプロイメントファイル確認"""
        logger.info("デプロイメントファイル確認")
        
        import os
        
        files_to_check = [
            "requirements.txt",
            "Dockerfile",
            ".dockerignore",
            "deployment_trigger.txt",
            "DEPLOYMENT_GUIDE.md",
            ".github/workflows/ci-cd-pipeline.yml"
        ]
        
        file_status = {}
        for file_path in files_to_check:
            file_status[file_path] = os.path.exists(file_path)
        
        return file_status
    
    def perform_health_check(self, service_url: str) -> Dict[str, str]:
        """ヘルスチェック実行"""
        logger.info(f"ヘルスチェック実行: {service_url}")
        
        health_status = {
            "reachable": "unknown",
            "status": "unknown",
            "response_time": "unknown"
        }
        
        try:
            import requests
            start_time = time.time()
            
            health_url = f"{service_url}/health"
            response = requests.get(health_url, timeout=30)
            
            response_time = time.time() - start_time
            health_status["response_time"] = f"{response_time:.2f}s"
            
            if response.status_code == 200:
                health_status["reachable"] = "yes"
                try:
                    health_data = response.json()
                    health_status["status"] = health_data.get("status", "unknown")
                except:
                    health_status["status"] = "response_received"
            else:
                health_status["reachable"] = "yes"
                health_status["status"] = f"HTTP {response.status_code}"
                
        except ImportError:
            health_status["error"] = "requests library not available"
        except Exception as e:
            health_status["reachable"] = "no"
            health_status["error"] = str(e)
        
        return health_status
    
    def display_status_report(self) -> None:
        """状況レポート表示"""
        print("\n" + "=" * 60)
        print("🔍 Therapeutic Gamification App - デプロイメント状況確認")
        print("=" * 60)
        
        # 1. デプロイメントファイル確認
        print("\n📋 デプロイメントファイル状況:")
        file_status = self.check_deployment_files()
        
        for file_path, exists in file_status.items():
            status_icon = "✅" if exists else "❌"
            print(f"   {status_icon} {file_path}")
        
        # 2. GitHub Actions状況
        print("\n🔄 GitHub Actions状況:")
        github_status = self.check_github_actions_status()
        
        if github_status["available"] == "yes":
            print("   ✅ GitHub CLI利用可能")
            print(f"   📊 最新実行: {github_status['latest_run']}")
            print(f"   📈 状況: {github_status['status']}")
        else:
            print("   ❌ GitHub CLI利用不可")
            if "error" in github_status:
                print(f"   ⚠️ エラー: {github_status['error']}")
        
        # 3. Cloud Run状況
        print("\n☁️ Cloud Run状況:")
        cloudrun_status = self.check_cloud_run_status()
        
        if cloudrun_status["available"] == "yes":
            print("   ✅ gcloud CLI利用可能")
            
            if cloudrun_status["service_exists"] == "yes":
                print("   ✅ サービス存在")
                print(f"   🌐 URL: {cloudrun_status['service_url']}")
                print(f"   📦 最新リビジョン: {cloudrun_status['latest_revision']}")
                print(f"   🚦 トラフィック: {cloudrun_status['traffic']}")
                
                # ヘルスチェック実行
                if cloudrun_status["service_url"] != "unknown":
                    print("\n🏥 ヘルスチェック:")
                    health_status = self.perform_health_check(cloudrun_status["service_url"])
                    
                    if health_status["reachable"] == "yes":
                        print(f"   ✅ サービス到達可能")
                        print(f"   📊 状況: {health_status['status']}")
                        print(f"   ⏱️ レスポンス時間: {health_status['response_time']}")
                    else:
                        print(f"   ❌ サービス到達不可")
                        if "error" in health_status:
                            print(f"   ⚠️ エラー: {health_status['error']}")
            else:
                print("   ❌ サービス未デプロイ")
                if "error" in cloudrun_status:
                    print(f"   ⚠️ 理由: {cloudrun_status['error']}")
        else:
            print("   ❌ gcloud CLI利用不可")
            if "error" in cloudrun_status:
                print(f"   ⚠️ エラー: {cloudrun_status['error']}")
        
        # 4. 推奨アクション
        print("\n💡 推奨アクション:")
        
        missing_files = [f for f, exists in file_status.items() if not exists]
        if missing_files:
            print("   📝 不足ファイルを作成してください:")
            for file_path in missing_files:
                print(f"      - {file_path}")
        
        if github_status["available"] == "no":
            print("   🔧 GitHub CLIをインストールしてください")
            print("      https://cli.github.com/")
        
        if cloudrun_status["available"] == "no":
            print("   🔧 Google Cloud SDKをインストールしてください")
            print("      https://cloud.google.com/sdk/docs/install")
        
        if cloudrun_status["service_exists"] == "no":
            print("   🚀 デプロイメントを実行してください:")
            print("      1. GitHub Secretsを設定")
            print("      2. commit_and_deploy.bat を実行")
            print("      3. GitHub Actionsタブで進行状況を確認")
        
        print("\n🔗 重要なリンク:")
        print("   - GitHub Actions: https://github.com/[your-repo]/actions")
        print("   - Cloud Run Console: https://console.cloud.google.com/run")
        print("   - Deployment Guide: DEPLOYMENT_GUIDE.md")

def main():
    """メイン実行関数"""
    checker = DeploymentStatusChecker()
    
    try:
        checker.display_status_report()
        
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()