#!/usr/bin/env python3
"""
手動入力デプロイスクリプト
ユーザー名を手動入力して確実にデプロイを実行
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

class ManualInputDeploy:
    """手動入力デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        
        # 実行可能ファイルのパスを設定
        self.git_path = r"C:\Program Files\Git\cmd\git.exe"
        self.gh_path = r"C:\Program Files\GitHub CLI\gh.exe"
    
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 60) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            # パスを置換
            if command[0] == "git":
                command[0] = self.git_path
            elif command[0] == "gh":
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
        except FileNotFoundError as e:
            logger.error(f"ファイルが見つかりません: {e}")
            return False, "", f"File not found: {command[0]}"
    
    def get_github_username_manual(self) -> str:
        """GitHubユーザー名を手動入力"""
        print("\n👤 GitHubユーザー名入力")
        print("=" * 40)
        
        while True:
            username = input("GitHubユーザー名を入力してください: ").strip()
            if username:
                print(f"✅ ユーザー名: {username}")
                return username
            print("❌ ユーザー名を入力してください")
    
    def create_github_repository(self) -> bool:
        """GitHubリポジトリ作成"""
        logger.info("GitHubリポジトリ作成")
        
        print("\n📝 GitHubリポジトリ作成中...")
        
        # リポジトリ作成
        success, stdout, stderr = self.run_command([
            "gh", "repo", "create", self.repo_name,
            "--description", "Therapeutic Gamification App for ADHD Support",
            "--public",
            "--clone=false"
        ], check=False)
        
        if success:
            print(f"✅ リポジトリ作成完了: {self.repo_name}")
            logger.info(f"GitHubリポジトリ作成成功: {self.repo_name}")
            return True
        elif "already exists" in stderr:
            print(f"ℹ️ リポジトリ既存: {self.repo_name}")
            logger.info("GitHubリポジトリ既存")
            return True
        else:
            print(f"❌ リポジトリ作成失敗: {stderr}")
            logger.error(f"GitHubリポジトリ作成失敗: {stderr}")
            return False
    
    def setup_git_remote(self, username: str) -> bool:
        """Gitリモート設定"""
        logger.info("Gitリモート設定")
        
        print("\n🔗 Gitリモート設定中...")
        
        repo_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        # 既存のリモート削除
        self.run_command(["git", "remote", "remove", "origin"], check=False)
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ])
        
        if success:
            print(f"✅ リモート設定完了: {username}/{self.repo_name}")
            logger.info(f"Gitリモート設定完了: {repo_url}")
            return True
        else:
            print(f"❌ リモート設定失敗: {stderr}")
            logger.error(f"Gitリモート設定失敗: {stderr}")
            return False
    
    def commit_and_push(self) -> bool:
        """コミット・プッシュ"""
        logger.info("コミット・プッシュ")
        
        print("\n📦 ファイルをコミット・プッシュ中...")
        
        # ファイル追加
        success, stdout, stderr = self.run_command(["git", "add", "."])
        if not success:
            print(f"❌ git add失敗: {stderr}")
            return False
        
        # コミット
        commit_message = f"feat: complete deployment setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            print(f"❌ git commit失敗: {stderr}")
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
            print("✅ プッシュ完了")
            logger.info("GitHubプッシュ成功")
            return True
        else:
            print(f"❌ プッシュ失敗: {stderr}")
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            return False
    
    def setup_github_secrets_simple(self) -> bool:
        """GitHub Secrets簡単設定"""
        logger.info("GitHub Secrets簡単設定")
        
        print("\n🔧 GitHub Secrets設定")
        print("=" * 40)
        
        # GCP_PROJECT_ID設定
        print("1. GCP_PROJECT_ID設定中...")
        success, stdout, stderr = self.run_command([
            "gh", "secret", "set", "GCP_PROJECT_ID",
            "--body", self.project_id
        ], check=False)
        
        if success:
            print("✅ GCP_PROJECT_ID設定完了")
        else:
            print(f"⚠️ GCP_PROJECT_ID設定失敗: {stderr}")
        
        # GCP_SA_KEY設定案内
        print("\n2. GCP_SA_KEY設定")
        print("以下のコマンドを別のPowerShellウィンドウで実行してください：")
        print(f"   gh secret set GCP_SA_KEY")
        print("実行後、サービスアカウントキーのJSON内容を貼り付けてください。")
        
        print("\n📋 サービスアカウントキー作成手順:")
        print("1. Google Cloud Console を開く")
        print("2. IAM & Admin > Service Accounts")
        print("3. CREATE SERVICE ACCOUNT")
        print("4. Name: github-actions")
        print("5. 以下のロールを追加:")
        
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
        
        print("6. KEYS > ADD KEY > Create new key > JSON")
        print("7. ダウンロードしたJSONファイルの内容をコピー")
        print("8. gh secret set GCP_SA_KEY コマンドで設定")
        
        # Google Cloud Console を開く
        try:
            webbrowser.open(f"https://console.cloud.google.com/iam-admin/serviceaccounts?project={self.project_id}")
            time.sleep(2)
        except:
            pass
        
        input("\nGCP_SA_KEY設定完了後、Enterキーを押してください...")
        
        return True
    
    def display_final_status(self, username: str) -> None:
        """最終状況表示"""
        print("\n" + "=" * 60)
        print("🎉 デプロイ設定完了！")
        print("=" * 60)
        
        repo_url = f"https://github.com/{username}/{self.repo_name}"
        actions_url = f"{repo_url}/actions"
        
        print(f"\n📊 デプロイメント情報:")
        print(f"   👤 GitHubユーザー: {username}")
        print(f"   📁 リポジトリ: {self.repo_name}")
        print(f"   🔗 URL: {repo_url}")
        
        print(f"\n🚀 GitHub Actions:")
        print(f"   📈 監視URL: {actions_url}")
        print(f"   ⏱️ 所要時間: 約15-20分")
        print(f"   📋 処理順序: テスト → ビルド → デプロイ → 監視")
        
        # GitHub Actionsページを開く
        print(f"\n🌐 GitHub Actionsページを開きます...")
        try:
            webbrowser.open(actions_url)
            time.sleep(2)
        except:
            pass
        
        print(f"\n✅ デプロイ成功の確認方法:")
        print(f"   - GitHub Actionsで全ジョブが緑色（成功）")
        print(f"   - Cloud Runにサービスが作成される")
        print(f"   - サービスURLにアクセス可能")
        
        print(f"\n🎮 デプロイ完了後:")
        print(f"   - Cloud Run Console: https://console.cloud.google.com/run")
        print(f"   - プロジェクト: {self.project_id}")
        print(f"   - サービス名: {self.service_name}")
        print(f"   - アプリケーションURLでアクセス確認")
        
        print(f"\n🔗 重要なリンク:")
        print(f"   - GitHub Repository: {repo_url}")
        print(f"   - GitHub Actions: {actions_url}")
        print(f"   - Cloud Console: https://console.cloud.google.com/")
        print(f"   - Cloud Run: https://console.cloud.google.com/run")
    
    def run_manual_deploy(self) -> bool:
        """手動入力デプロイ実行"""
        logger.info("🚀 手動入力デプロイ開始")
        
        print("🚀 Therapeutic Gamification App - 手動入力デプロイ")
        print("=" * 60)
        
        # 1. GitHubユーザー名入力
        username = self.get_github_username_manual()
        
        # 2. GitHubリポジトリ作成
        if not self.create_github_repository():
            return False
        
        # 3. Gitリモート設定
        if not self.setup_git_remote(username):
            return False
        
        # 4. コミット・プッシュ
        if not self.commit_and_push():
            return False
        
        # 5. GitHub Secrets設定
        if not self.setup_github_secrets_simple():
            return False
        
        # 6. 最終状況表示
        self.display_final_status(username)
        
        logger.info("✅ 手動入力デプロイ完了")
        return True

def main():
    """メイン実行関数"""
    deployer = ManualInputDeploy()
    
    try:
        success = deployer.run_manual_deploy()
        
        if success:
            print("\n🎉 手動入力デプロイが完了しました！")
            print("📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            print("🎮 デプロイ完了後、素晴らしいアプリケーションをお楽しみください！")
            
        else:
            print("\n❌ デプロイ設定に失敗しました。")
        
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()