#!/usr/bin/env python3
"""
直接GitHub CLI使用デプロイスクリプト
既存のGitHub CLIを使用して完全自動デプロイ
"""

import os
import subprocess
import sys
import time
import logging
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectGitHubDeploy:
    """直接GitHub CLIデプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        
        # GitHub CLIのパスを明示的に設定
        self.gh_path = r"C:\Program Files\GitHub CLI\gh.exe"
        if not os.path.exists(self.gh_path):
            self.gh_path = "gh"  # PATHから検索
    
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 300) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            # GitHub CLIコマンドの場合、パスを置換
            if command[0] == "gh" and self.gh_path != "gh":
                command[0] = self.gh_path
            
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
    
    def check_prerequisites(self) -> bool:
        """前提条件確認"""
        logger.info("前提条件確認")
        
        # Git確認
        success, stdout, stderr = self.run_command(["git", "--version"], check=False)
        if not success:
            logger.error("Gitがインストールされていません")
            return False
        
        # GitHub CLI確認
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        if not success:
            logger.error("GitHub CLIがインストールされていません")
            return False
        
        # Gitリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "status"], check=False)
        if not success:
            logger.error("Gitリポジトリではありません")
            return False
        
        logger.info("前提条件確認完了")
        return True
    
    def authenticate_github(self) -> bool:
        """GitHub認証"""
        logger.info("GitHub認証確認")
        
        # 既存の認証確認
        success, stdout, stderr = self.run_command(["gh", "auth", "status"], check=False)
        
        if success and "Logged in" in stdout:
            logger.info("GitHub認証済み")
            return True
        
        logger.info("GitHub認証が必要です")
        print("\n" + "=" * 60)
        print("🔐 GitHub認証")
        print("=" * 60)
        print("\nブラウザでGitHub認証を行います...")
        
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
        
        print("\n" + "=" * 60)
        print("📝 GitHubリポジトリ作成")
        print("=" * 60)
        
        # リポジトリ作成
        success, stdout, stderr = self.run_command([
            "gh", "repo", "create", self.repo_name,
            "--description", "Therapeutic Gamification App for ADHD Support",
            "--public",
            "--clone=false"
        ], check=False)
        
        if success:
            logger.info(f"GitHubリポジトリ作成成功: {self.repo_name}")
            print(f"✅ リポジトリ作成完了: {self.repo_name}")
            return True
        elif "already exists" in stderr:
            logger.info("GitHubリポジトリ既存")
            print(f"ℹ️ リポジトリ既存: {self.repo_name}")
            return True
        else:
            logger.error(f"GitHubリポジトリ作成失敗: {stderr}")
            print(f"❌ リポジトリ作成失敗: {stderr}")
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
            print(f"✅ リモート設定完了: {username}/{self.repo_name}")
            return True
        else:
            logger.error(f"Gitリモート設定失敗: {stderr}")
            return False
    
    def commit_and_push(self) -> bool:
        """コミット・プッシュ"""
        logger.info("コミット・プッシュ")
        
        print("\n📦 ファイルをコミット・プッシュ中...")
        
        # ファイル追加
        success, stdout, stderr = self.run_command(["git", "add", "."])
        if not success:
            logger.error(f"git add失敗: {stderr}")
            return False
        
        # コミット
        commit_message = f"feat: complete deployment setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            logger.error(f"git commit失敗: {stderr}")
            return False
        
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
            print("✅ プッシュ完了")
            return True
        else:
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            print(f"❌ プッシュ失敗: {stderr}")
            return False
    
    def setup_github_secrets(self) -> bool:
        """GitHub Secrets設定"""
        logger.info("GitHub Secrets設定")
        
        print("\n" + "=" * 60)
        print("🔧 GitHub Secrets設定")
        print("=" * 60)
        
        # GCP_PROJECT_ID設定
        success, stdout, stderr = self.run_command([
            "gh", "secret", "set", "GCP_PROJECT_ID",
            "--body", self.project_id
        ], check=False)
        
        if success:
            logger.info("GCP_PROJECT_ID設定完了")
            print("✅ GCP_PROJECT_ID設定完了")
        else:
            logger.warning(f"GCP_PROJECT_ID設定失敗: {stderr}")
            print(f"⚠️ GCP_PROJECT_ID設定失敗: {stderr}")
        
        # GCP_SA_KEY設定案内
        print("\n🔑 GCP_SA_KEY設定が必要です")
        print("Google Cloud Consoleでサービスアカウントキーを作成してください。")
        
        print("\n🌐 Google Cloud Consoleを開きます...")
        try:
            webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
            time.sleep(2)
        except:
            pass
        
        print("\n📋 サービスアカウント作成手順:")
        print("1. 'CREATE SERVICE ACCOUNT' をクリック")
        print("2. Name: github-actions")
        print("3. Description: GitHub Actions CI/CD")
        print("4. 以下の権限を付与:")
        
        roles = [
            "Cloud Run Admin",
            "Cloud Build Editor", 
            "Storage Admin",
            "Service Account User",
            "Cloud Datastore Owner",
            "Secret Manager Admin",
            "Logging Viewer"
        ]
        
        for role in roles:
            print(f"   - {role}")
        
        print("\n5. Keys タブ > ADD KEY > Create new key > JSON")
        print("6. ダウンロードしたJSONファイルの内容をコピー")
        
        input("\nサービスアカウントキー作成完了後、Enterキーを押してください...")
        
        # GCP_SA_KEY設定
        print("\n📝 GCP_SA_KEYを設定します...")
        print("JSONファイルの内容全体を貼り付けてください:")
        print("（Ctrl+V で貼り付け、Enter で完了）")
        
        sa_key_lines = []
        print("\n--- JSON内容を貼り付けてください ---")
        
        try:
            while True:
                line = input()
                if line.strip() == "":
                    break
                sa_key_lines.append(line)
        except KeyboardInterrupt:
            print("\n設定をスキップします")
            return True
        
        if sa_key_lines:
            sa_key_content = "\n".join(sa_key_lines)
            
            # GitHub Secretに設定
            success, stdout, stderr = self.run_command([
                "gh", "secret", "set", "GCP_SA_KEY",
                "--body", sa_key_content
            ], check=False)
            
            if success:
                logger.info("GCP_SA_KEY設定完了")
                print("✅ GCP_SA_KEY設定完了")
                return True
            else:
                logger.error(f"GCP_SA_KEY設定失敗: {stderr}")
                print(f"❌ GCP_SA_KEY設定失敗: {stderr}")
                return False
        
        return True
    
    def monitor_deployment(self) -> None:
        """デプロイメント監視"""
        logger.info("デプロイメント監視開始")
        
        print("\n" + "=" * 60)
        print("📊 GitHub Actions デプロイメント監視")
        print("=" * 60)
        
        # 現在のユーザー名取得
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
            
            print(f"\n📈 デプロイメント情報:")
            print(f"   🔗 GitHub Actions: {actions_url}")
            print(f"   ⏱️ 所要時間: 約15-20分")
            print(f"   📋 処理順序: テスト → ビルド → デプロイ → 監視")
            
            print(f"\n✅ デプロイ成功の確認方法:")
            print(f"   - 全ジョブが緑色（成功）")
            print(f"   - Cloud Runにサービスが作成される")
            print(f"   - サービスURLにアクセス可能")
            
            print(f"\n🎮 デプロイ完了後:")
            print(f"   - Cloud Run Console でサービスURL確認")
            print(f"   - https://console.cloud.google.com/run")
            print(f"   - アプリケーションにアクセスして動作確認")
    
    def run_direct_deploy(self) -> bool:
        """直接デプロイ実行"""
        logger.info("🚀 直接GitHub CLIデプロイ開始")
        
        # 1. 前提条件確認
        if not self.check_prerequisites():
            return False
        
        # 2. GitHub認証
        if not self.authenticate_github():
            return False
        
        # 3. GitHubリポジトリ作成
        if not self.create_github_repository():
            return False
        
        # 4. Gitリモート設定
        if not self.setup_git_remote():
            return False
        
        # 5. コミット・プッシュ
        if not self.commit_and_push():
            return False
        
        # 6. GitHub Secrets設定
        if not self.setup_github_secrets():
            return False
        
        # 7. デプロイメント監視
        self.monitor_deployment()
        
        logger.info("✅ 直接GitHub CLIデプロイ完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - 直接GitHub CLIデプロイ")
    print("=" * 60)
    
    deployer = DirectGitHubDeploy()
    
    try:
        success = deployer.run_direct_deploy()
        
        if success:
            print("\n🎉 GitHub CLIデプロイが完了しました！")
            print("\n📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            print("🎮 デプロイ完了後、素晴らしいアプリケーションをお楽しみください！")
            
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