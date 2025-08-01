#!/usr/bin/env python3
"""
完全自動デプロイスクリプト
GitHub CLI使用でリポジトリ作成からデプロイまで完全自動化
"""

import os
import subprocess
import sys
import time
import logging
import urllib.request
import tempfile
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FullyAutomatedDeploy:
    """完全自動デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        self.github_cli_url = "https://github.com/cli/cli/releases/download/v2.40.1/gh_2.40.1_windows_amd64.msi"
        
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 300) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            logger.info(f"実行中: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
                shell=shell
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            logger.error(f"コマンド実行エラー: {e}")
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            logger.error("コマンドタイムアウト")
            return False, "", "Command timed out"
        except FileNotFoundError:
            return False, "", f"Command not found: {command[0]}"
    
    def check_github_cli_installed(self) -> bool:
        """GitHub CLI インストール確認"""
        logger.info("GitHub CLI インストール状況確認")
        
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        
        if success:
            logger.info(f"GitHub CLI既にインストール済み: {stdout.strip()}")
            return True
        else:
            logger.info("GitHub CLI未インストール")
            return False
    
    def download_github_cli_installer(self) -> Optional[str]:
        """GitHub CLI インストーラーダウンロード"""
        logger.info("GitHub CLI インストーラーダウンロード開始")
        
        try:
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "gh_installer.msi")
            
            logger.info(f"ダウンロード先: {installer_path}")
            logger.info("ダウンロード中... (数分かかる場合があります)")
            
            urllib.request.urlretrieve(self.github_cli_url, installer_path)
            
            logger.info("GitHub CLI インストーラーダウンロード完了")
            return installer_path
            
        except Exception as e:
            logger.error(f"GitHub CLI インストーラーダウンロードエラー: {e}")
            return None
    
    def install_github_cli(self, installer_path: str) -> bool:
        """GitHub CLI インストール実行"""
        logger.info("GitHub CLI インストール実行")
        
        try:
            # MSIインストール実行
            install_command = [
                "msiexec",
                "/i", installer_path,
                "/quiet",
                "/norestart"
            ]
            
            logger.info("GitHub CLI インストール中... (数分かかります)")
            
            result = subprocess.run(
                install_command,
                capture_output=True,
                text=True,
                timeout=600,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("GitHub CLI インストール完了")
                
                # インストール後、PATHを更新
                self.update_path_for_github_cli()
                
                # インストール確認
                time.sleep(10)
                return self.check_github_cli_installed()
            else:
                logger.error(f"GitHub CLI インストール失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"GitHub CLI インストールエラー: {e}")
            return False
    
    def update_path_for_github_cli(self) -> None:
        """GitHub CLI用のPATH更新"""
        logger.info("PATH環境変数更新（GitHub CLI）")
        
        # 一般的なGitHub CLIインストールパス
        gh_paths = [
            r"C:\Program Files\GitHub CLI",
            r"C:\Program Files (x86)\GitHub CLI"
        ]
        
        current_path = os.environ.get("PATH", "")
        
        for gh_path in gh_paths:
            if os.path.exists(gh_path) and gh_path not in current_path:
                os.environ["PATH"] = f"{gh_path};{current_path}"
                logger.info(f"PATH追加: {gh_path}")
    
    def authenticate_github(self) -> bool:
        """GitHub認証"""
        logger.info("GitHub認証開始")
        
        # 既存の認証確認
        success, stdout, stderr = self.run_command(["gh", "auth", "status"], check=False)
        
        if success and "Logged in" in stdout:
            logger.info("GitHub認証済み")
            return True
        
        logger.info("GitHub認証が必要です")
        
        # ブラウザ認証実行
        success, stdout, stderr = self.run_command([
            "gh", "auth", "login", "--web", "--git-protocol", "https"
        ], timeout=600)
        
        if success:
            logger.info("GitHub認証完了")
            return True
        else:
            logger.error(f"GitHub認証失敗: {stderr}")
            return False
    
    def create_github_repository(self) -> bool:
        """GitHubリポジトリ作成"""
        logger.info("GitHubリポジトリ作成")
        
        # リポジトリ作成
        success, stdout, stderr = self.run_command([
            "gh", "repo", "create", self.repo_name,
            "--description", "Therapeutic Gamification App for ADHD Support",
            "--public",
            "--clone=false"
        ], check=False)
        
        if success:
            logger.info(f"GitHubリポジトリ作成成功: {self.repo_name}")
            return True
        elif "already exists" in stderr:
            logger.info("GitHubリポジトリ既存")
            return True
        else:
            logger.error(f"GitHubリポジトリ作成失敗: {stderr}")
            return False
    
    def setup_git_remote(self) -> bool:
        """Gitリモート設定"""
        logger.info("Gitリモート設定")
        
        # 現在のユーザー名取得
        success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"], check=False)
        
        if not success:
            logger.error("GitHubユーザー名取得失敗")
            return False
        
        username = stdout.strip()
        repo_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        # 既存のリモート削除
        self.run_command(["git", "remote", "remove", "origin"], check=False)
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ])
        
        if success:
            logger.info(f"Gitリモート設定完了: {repo_url}")
            return True
        else:
            logger.error(f"Gitリモート設定失敗: {stderr}")
            return False
    
    def push_to_github(self) -> bool:
        """GitHubにプッシュ"""
        logger.info("GitHubにプッシュ")
        
        # ブランチ設定
        success, stdout, stderr = self.run_command([
            "git", "branch", "-M", "main"
        ], check=False)
        
        # プッシュ実行
        success, stdout, stderr = self.run_command([
            "git", "push", "-u", "origin", "main"
        ])
        
        if success:
            logger.info("GitHubプッシュ成功")
            return True
        else:
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            return False
    
    def setup_github_secrets(self) -> bool:
        """GitHub Secrets設定"""
        logger.info("GitHub Secrets設定")
        
        print("\n" + "=" * 60)
        print("🔧 GitHub Secrets自動設定")
        print("=" * 60)
        
        # GCP_PROJECT_ID設定
        success, stdout, stderr = self.run_command([
            "gh", "secret", "set", "GCP_PROJECT_ID",
            "--body", self.project_id
        ], check=False)
        
        if success:
            logger.info("GCP_PROJECT_ID設定完了")
        else:
            logger.warning(f"GCP_PROJECT_ID設定失敗: {stderr}")
        
        # GCP_SA_KEY設定案内
        print("\n🔑 GCP_SA_KEY設定が必要です")
        print("以下の手順でサービスアカウントキーを設定してください：")
        
        print("\n1. Google Cloud Consoleを開きます...")
        try:
            webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
            time.sleep(2)
        except:
            pass
        
        print("\n2. 以下のコマンドを実行してサービスアカウントを作成：")
        print(f"   gcloud config set project {self.project_id}")
        print("   gcloud iam service-accounts create github-actions --description='GitHub Actions CI/CD' --display-name='GitHub Actions'")
        
        print("\n3. 権限付与：")
        roles = [
            "roles/run.admin",
            "roles/cloudbuild.builds.editor", 
            "roles/storage.admin",
            "roles/iam.serviceAccountUser",
            "roles/datastore.owner",
            "roles/secretmanager.admin",
            "roles/logging.viewer"
        ]
        
        for role in roles:
            print(f"   gcloud projects add-iam-policy-binding {self.project_id} --member='serviceAccount:github-actions@{self.project_id}.iam.gserviceaccount.com' --role='{role}'")
        
        print("\n4. キー生成：")
        print(f"   gcloud iam service-accounts keys create github-actions-key.json --iam-account=github-actions@{self.project_id}.iam.gserviceaccount.com")
        
        print("\n5. GitHub Secretに設定：")
        print("   gh secret set GCP_SA_KEY < github-actions-key.json")
        
        input("\nサービスアカウントキー設定完了後、Enterキーを押してください...")
        
        return True
    
    def monitor_deployment(self) -> None:
        """デプロイメント監視"""
        logger.info("デプロイメント監視開始")
        
        print("\n" + "=" * 60)
        print("📊 GitHub Actions デプロイメント監視")
        print("=" * 60)
        
        # GitHub Actionsページを開く
        success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"], check=False)
        
        if success:
            username = stdout.strip()
            actions_url = f"https://github.com/{username}/{self.repo_name}/actions"
            
            print(f"\n🌐 GitHub Actionsページを開きます...")
            try:
                webbrowser.open(actions_url)
                time.sleep(2)
            except:
                pass
            
            print(f"\n📈 デプロイメント進行状況:")
            print(f"   🔗 URL: {actions_url}")
            print(f"   ⏱️ 所要時間: 約15-20分")
            print(f"   📋 処理順序: テスト → ビルド → デプロイ → 監視")
            
            print(f"\n✅ デプロイ成功の確認方法:")
            print(f"   - 全ジョブが緑色（成功）")
            print(f"   - Cloud Runにサービスが作成される")
            print(f"   - サービスURLにアクセス可能")
            
            print(f"\n🚨 エラー時の対応:")
            print(f"   - 自動ロールバックが実行される")
            print(f"   - ログを確認してエラー原因を特定")
            print(f"   - 必要に応じて修正してプッシュ")
    
    def run_fully_automated_deploy(self) -> bool:
        """完全自動デプロイ実行"""
        logger.info("🚀 完全自動デプロイ開始")
        
        # 1. GitHub CLI インストール確認
        if not self.check_github_cli_installed():
            installer_path = self.download_github_cli_installer()
            if not installer_path:
                return False
            
            if not self.install_github_cli(installer_path):
                return False
            
            # インストーラー削除
            try:
                os.remove(installer_path)
                logger.info("インストーラーファイル削除完了")
            except:
                pass
        
        # 2. GitHub認証
        if not self.authenticate_github():
            return False
        
        # 3. GitHubリポジトリ作成
        if not self.create_github_repository():
            return False
        
        # 4. Gitリモート設定
        if not self.setup_git_remote():
            return False
        
        # 5. GitHubにプッシュ
        if not self.push_to_github():
            return False
        
        # 6. GitHub Secrets設定
        if not self.setup_github_secrets():
            return False
        
        # 7. デプロイメント監視
        self.monitor_deployment()
        
        logger.info("✅ 完全自動デプロイ設定完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - 完全自動デプロイ")
    print("=" * 60)
    
    deployer = FullyAutomatedDeploy()
    
    try:
        success = deployer.run_fully_automated_deploy()
        
        if success:
            print("\n🎉 完全自動デプロイが完了しました！")
            print("\n📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            print("🎮 デプロイ完了後、素晴らしいアプリケーションをお楽しみください！")
            
            print("\n🔗 重要なリンク:")
            print("   - GitHub Actions: リポジトリ > Actions タブ")
            print("   - Cloud Run: https://console.cloud.google.com/run")
            print("   - アプリケーション: デプロイ完了後にCloud RunでURL確認")
            
        else:
            print("\n❌ デプロイ設定に失敗しました。ログを確認してください。")
        
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()