#!/usr/bin/env python3
"""
自動デプロイメント実行スクリプト
GCPプロジェクト設定からGitHubへのプッシュまで自動化
"""

import os
import subprocess
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AutoDeploymentSetup:
    """自動デプロイメント設定クラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.region = "asia-northeast1"
        self.service_account_name = "github-actions"
        
    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            logger.info(f"実行中: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            logger.error(f"コマンド実行エラー: {e}")
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            logger.error("コマンドタイムアウト")
            return False, "", "Command timed out"
    
    def check_gcloud_auth(self) -> bool:
        """gcloud認証確認"""
        success, stdout, stderr = self.run_command(["gcloud", "auth", "list"], check=False)
        
        if success and "ACTIVE" in stdout:
            logger.info("gcloud認証済み")
            return True
        else:
            logger.error("gcloud認証が必要です")
            logger.info("以下のコマンドで認証してください:")
            logger.info("gcloud auth login")
            return False
    
    def setup_gcp_project(self) -> bool:
        """GCPプロジェクト設定"""
        logger.info("GCPプロジェクト設定開始")
        
        # プロジェクト作成（既存の場合はスキップ）
        success, stdout, stderr = self.run_command([
            "gcloud", "projects", "create", self.project_id
        ], check=False)
        
        if not success and "already exists" not in stderr:
            logger.error(f"プロジェクト作成失敗: {stderr}")
            return False
        
        # プロジェクト設定
        success, stdout, stderr = self.run_command([
            "gcloud", "config", "set", "project", self.project_id
        ])
        
        if not success:
            logger.error(f"プロジェクト設定失敗: {stderr}")
            return False
        
        logger.info(f"プロジェクト設定完了: {self.project_id}")
        return True
    
    def enable_apis(self) -> bool:
        """必要なAPIを有効化"""
        logger.info("API有効化開始")
        
        apis = [
            "run.googleapis.com",
            "cloudbuild.googleapis.com",
            "containerregistry.googleapis.com",
            "firestore.googleapis.com",
            "secretmanager.googleapis.com",
            "logging.googleapis.com",
            "monitoring.googleapis.com"
        ]
        
        for api in apis:
            success, stdout, stderr = self.run_command([
                "gcloud", "services", "enable", api
            ])
            
            if success:
                logger.info(f"API有効化成功: {api}")
            else:
                logger.error(f"API有効化失敗: {api} - {stderr}")
                return False
        
        logger.info("全API有効化完了")
        return True
    
    def create_service_account(self) -> bool:
        """サービスアカウント作成"""
        logger.info("サービスアカウント作成開始")
        
        # サービスアカウント作成
        success, stdout, stderr = self.run_command([
            "gcloud", "iam", "service-accounts", "create", self.service_account_name,
            "--description", "GitHub Actions CI/CD",
            "--display-name", "GitHub Actions"
        ], check=False)
        
        if not success and "already exists" not in stderr:
            logger.error(f"サービスアカウント作成失敗: {stderr}")
            return False
        
        # 権限付与
        roles = [
            "roles/run.admin",
            "roles/cloudbuild.builds.editor",
            "roles/storage.admin",
            "roles/iam.serviceAccountUser",
            "roles/datastore.owner",
            "roles/secretmanager.admin",
            "roles/logging.viewer"
        ]
        
        service_account_email = f"{self.service_account_name}@{self.project_id}.iam.gserviceaccount.com"
        
        for role in roles:
            success, stdout, stderr = self.run_command([
                "gcloud", "projects", "add-iam-policy-binding", self.project_id,
                "--member", f"serviceAccount:{service_account_email}",
                "--role", role
            ])
            
            if success:
                logger.info(f"権限付与成功: {role}")
            else:
                logger.error(f"権限付与失敗: {role} - {stderr}")
                return False
        
        logger.info("サービスアカウント設定完了")
        return True
    
    def generate_service_account_key(self) -> Optional[str]:
        """サービスアカウントキー生成"""
        logger.info("サービスアカウントキー生成開始")
        
        key_file = "github-actions-key.json"
        service_account_email = f"{self.service_account_name}@{self.project_id}.iam.gserviceaccount.com"
        
        success, stdout, stderr = self.run_command([
            "gcloud", "iam", "service-accounts", "keys", "create", key_file,
            "--iam-account", service_account_email
        ])
        
        if success:
            logger.info("サービスアカウントキー生成成功")
            
            # キーファイル内容を読み取り
            try:
                with open(key_file, 'r') as f:
                    key_content = f.read()
                
                # セキュリティのためキーファイルを削除
                os.remove(key_file)
                logger.info("キーファイル削除完了")
                
                return key_content
            except Exception as e:
                logger.error(f"キーファイル読み取りエラー: {e}")
                return None
        else:
            logger.error(f"サービスアカウントキー生成失敗: {stderr}")
            return None
    
    def check_git_status(self) -> bool:
        """Git状態確認"""
        logger.info("Git状態確認")
        
        # Gitリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "status"], check=False)
        
        if not success:
            logger.error("Gitリポジトリではありません")
            return False
        
        # リモートリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "remote", "-v"], check=False)
        
        if success and "github.com" in stdout:
            logger.info("GitHubリポジトリ確認済み")
            return True
        else:
            logger.error("GitHubリモートリポジトリが設定されていません")
            return False
    
    def prepare_deployment_files(self) -> bool:
        """デプロイメントファイル準備"""
        logger.info("デプロイメントファイル準備")
        
        # requirements.txtの確認・作成
        if not os.path.exists("requirements.txt"):
            logger.info("requirements.txt作成")
            requirements = [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "pydantic==2.5.0",
                "google-cloud-firestore==2.13.1",
                "google-cloud-secret-manager==2.17.0",
                "google-auth==2.25.2",
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6",
                "requests==2.31.0",
                "pytest==7.4.3",
                "pytest-asyncio==0.21.1",
                "pytest-cov==4.1.0"
            ]
            
            with open("requirements.txt", "w") as f:
                f.write("\n".join(requirements))
        
        # Dockerfileの確認
        if not os.path.exists("Dockerfile"):
            logger.error("Dockerfileが見つかりません")
            return False
        
        # CI/CDパイプライン確認
        if not os.path.exists(".github/workflows/ci-cd-pipeline.yml"):
            logger.error("CI/CDパイプラインファイルが見つかりません")
            return False
        
        logger.info("デプロイメントファイル準備完了")
        return True
    
    def commit_and_push(self) -> bool:
        """コミット・プッシュ実行"""
        logger.info("Git コミット・プッシュ開始")
        
        # 変更をステージング
        success, stdout, stderr = self.run_command(["git", "add", "."])
        
        if not success:
            logger.error(f"git add失敗: {stderr}")
            return False
        
        # コミット
        commit_message = f"feat: automatic deployment setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            logger.error(f"git commit失敗: {stderr}")
            return False
        
        # プッシュ
        success, stdout, stderr = self.run_command(["git", "push", "origin", "main"])
        
        if success:
            logger.info("Git プッシュ成功")
            return True
        else:
            logger.error(f"git push失敗: {stderr}")
            return False
    
    def display_github_secrets_info(self, service_account_key: str) -> None:
        """GitHub Secrets設定情報表示"""
        logger.info("=" * 60)
        logger.info("GitHub Secrets 設定情報")
        logger.info("=" * 60)
        
        print("\n🔧 GitHub リポジトリの Settings > Secrets and variables > Actions で以下を設定してください:\n")
        
        print("1. GCP_PROJECT_ID:")
        print(f"   {self.project_id}")
        
        print("\n2. GCP_SA_KEY:")
        print("   以下のJSON全体をコピー&ペーストしてください:")
        print("   " + "=" * 50)
        print(service_account_key)
        print("   " + "=" * 50)
        
        print("\n3. SLACK_WEBHOOK (オプション):")
        print("   Slack通知用のWebhook URLを設定してください")
        
        print("\n🚀 設定完了後、GitHub Actionsタブでデプロイ進行状況を確認してください:")
        
        # GitHubリポジトリURLを取得
        success, stdout, stderr = self.run_command(["git", "remote", "get-url", "origin"], check=False)
        if success:
            repo_url = stdout.strip().replace(".git", "")
            if "github.com" in repo_url:
                actions_url = f"{repo_url}/actions"
                print(f"   {actions_url}")
    
    def run_full_setup(self) -> bool:
        """完全自動セットアップ実行"""
        logger.info("🚀 自動デプロイメントセットアップ開始")
        
        # 1. gcloud認証確認
        if not self.check_gcloud_auth():
            return False
        
        # 2. GCPプロジェクト設定
        if not self.setup_gcp_project():
            return False
        
        # 3. API有効化
        if not self.enable_apis():
            return False
        
        # 4. サービスアカウント作成
        if not self.create_service_account():
            return False
        
        # 5. サービスアカウントキー生成
        service_account_key = self.generate_service_account_key()
        if not service_account_key:
            return False
        
        # 6. Git状態確認
        if not self.check_git_status():
            return False
        
        # 7. デプロイメントファイル準備
        if not self.prepare_deployment_files():
            return False
        
        # 8. コミット・プッシュ
        if not self.commit_and_push():
            return False
        
        # 9. GitHub Secrets設定情報表示
        self.display_github_secrets_info(service_account_key)
        
        logger.info("✅ 自動デプロイメントセットアップ完了")
        return True

def main():
    """メイン実行関数"""
    setup = AutoDeploymentSetup()
    
    try:
        success = setup.run_full_setup()
        
        if success:
            print("\n🎉 自動デプロイメントセットアップが完了しました！")
            print("\n次のステップ:")
            print("1. 上記のGitHub Secrets情報をGitHubリポジトリに設定")
            print("2. GitHub Actionsタブでデプロイ進行状況を確認")
            print("3. デプロイ完了後、本番環境での動作確認")
            sys.exit(0)
        else:
            print("\n❌ セットアップに失敗しました。ログを確認してください。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ セットアップが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()