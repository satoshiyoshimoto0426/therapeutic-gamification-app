#!/usr/bin/env python3
"""
Web ベースデプロイスクリプト
GitHub Web UI + Git HTTPS認証を使用した確実なデプロイ
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

class WebBasedDeploy:
    """Web ベースデプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        self.git_path = r"C:\Program Files\Git\cmd\git.exe"
    
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 60) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            if command[0] == "git":
                command[0] = self.git_path
            
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
    
    def create_github_repo_web(self) -> str:
        """GitHub Web UIでリポジトリ作成"""
        print("\n📝 GitHubリポジトリ作成")
        print("=" * 40)
        
        print("🌐 GitHub新規リポジトリ作成ページを開きます...")
        
        try:
            webbrowser.open("https://github.com/new")
            time.sleep(3)
        except:
            pass
        
        print("\n📋 以下の設定でリポジトリを作成してください：")
        print(f"   📁 Repository name: {self.repo_name}")
        print("   📖 Description: Therapeutic Gamification App for ADHD Support")
        print("   🔓 Visibility: Public (推奨)")
        print("   ❌ Initialize with README: チェックしない")
        print("   ❌ Add .gitignore: None")
        print("   ❌ Choose a license: None")
        print("\n✅ 'Create repository' ボタンをクリック")
        
        input("\nリポジトリ作成完了後、Enterキーを押してください...")
        
        while True:
            username = input("\nGitHubユーザー名を入力してください: ").strip()
            if username:
                return username
            print("❌ ユーザー名を入力してください")
    
    def setup_git_credentials(self, username: str) -> bool:
        """Git認証設定"""
        print("\n🔐 Git認証設定")
        print("=" * 40)
        
        print("Personal Access Token (PAT) を作成します...")
        
        try:
            webbrowser.open("https://github.com/settings/tokens/new")
            time.sleep(3)
        except:
            pass
        
        print("\n📋 Personal Access Token作成手順：")
        print("1. Token name: therapeutic-app-deploy")
        print("2. Expiration: 90 days (推奨)")
        print("3. Select scopes:")
        print("   ✅ repo (Full control of private repositories)")
        print("   ✅ workflow (Update GitHub Action workflows)")
        print("4. 'Generate token' をクリック")
        print("5. 生成されたトークンをコピー（一度しか表示されません）")
        
        input("\nPersonal Access Token作成完了後、Enterキーを押してください...")
        
        # Git認証設定
        repo_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        print(f"\n🔗 Gitリモート設定: {username}/{self.repo_name}")
        
        # 既存のリモート削除
        self.run_command(["git", "remote", "remove", "origin"], check=False)
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ])
        
        if success:
            print("✅ リモート設定完了")
            return True
        else:
            print(f"❌ リモート設定失敗: {stderr}")
            return False
    
    def commit_and_push_with_auth(self) -> bool:
        """認証付きコミット・プッシュ"""
        print("\n📦 ファイルをコミット・プッシュ")
        print("=" * 40)
        
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
        
        print("\n🚀 GitHubにプッシュします...")
        print("認証が求められたら以下を入力してください：")
        print("   Username: [GitHubユーザー名]")
        print("   Password: [Personal Access Token]")
        
        # プッシュ実行
        success, stdout, stderr = self.run_command([
            "git", "push", "-u", "origin", "main"
        ])
        
        if success:
            print("✅ プッシュ完了")
            return True
        else:
            print(f"❌ プッシュ失敗: {stderr}")
            print("\n🔧 トラブルシューティング:")
            print("1. GitHubユーザー名が正しいか確認")
            print("2. Personal Access Tokenが正しいか確認")
            print("3. リポジトリが正しく作成されているか確認")
            return False
    
    def setup_github_secrets_web(self, username: str) -> bool:
        """GitHub Secrets Web設定"""
        print("\n🔧 GitHub Secrets設定")
        print("=" * 40)
        
        secrets_url = f"https://github.com/{username}/{self.repo_name}/settings/secrets/actions"
        
        print("🌐 GitHub Secretsページを開きます...")
        
        try:
            webbrowser.open(secrets_url)
            time.sleep(3)
        except:
            pass
        
        print(f"\n📋 以下の2つのSecretsを設定してください：")
        
        print(f"\n🔑 Secret 1:")
        print(f"   Name: GCP_PROJECT_ID")
        print(f"   Value: {self.project_id}")
        
        print(f"\n🔑 Secret 2:")
        print(f"   Name: GCP_SA_KEY")
        print(f"   Value: [Google Cloudサービスアカウントキー]")
        
        # Google Cloud Console を開く
        print(f"\n🌐 Google Cloud Consoleを開きます...")
        try:
            webbrowser.open(f"https://console.cloud.google.com/iam-admin/serviceaccounts?project={self.project_id}")
            time.sleep(3)
        except:
            pass
        
        print(f"\n📖 サービスアカウントキー作成手順:")
        print("1. 'CREATE SERVICE ACCOUNT' をクリック")
        print("2. Service account name: github-actions")
        print("3. Description: GitHub Actions CI/CD")
        print("4. CREATE AND CONTINUE をクリック")
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
        
        for i, role in enumerate(roles, 1):
            print(f"   {i}. {role}")
        
        print("\n6. CONTINUE → DONE をクリック")
        print("7. 作成したサービスアカウントをクリック")
        print("8. KEYS タブ → ADD KEY → Create new key → JSON → CREATE")
        print("9. ダウンロードしたJSONファイルをメモ帳で開く")
        print("10. JSON内容全体をコピーしてGitHub SecretsのGCP_SA_KEYに設定")
        
        input("\nGitHub Secrets設定完了後、Enterキーを押してください...")
        
        return True
    
    def display_deployment_success(self, username: str) -> None:
        """デプロイ成功表示"""
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
            time.sleep(3)
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
        
        print(f"\n🎊 素晴らしいTherapeutic Gamification Appをお楽しみください！")
    
    def run_web_deploy(self) -> bool:
        """Web ベースデプロイ実行"""
        logger.info("🚀 Web ベースデプロイ開始")
        
        print("🚀 Therapeutic Gamification App - Web ベースデプロイ")
        print("=" * 60)
        print("GitHub CLI認証問題を回避し、Web UIを使用して確実にデプロイします")
        
        # 1. GitHub Web UIでリポジトリ作成
        username = self.create_github_repo_web()
        
        # 2. Git認証設定
        if not self.setup_git_credentials(username):
            return False
        
        # 3. コミット・プッシュ
        if not self.commit_and_push_with_auth():
            return False
        
        # 4. GitHub Secrets設定
        if not self.setup_github_secrets_web(username):
            return False
        
        # 5. デプロイ成功表示
        self.display_deployment_success(username)
        
        logger.info("✅ Web ベースデプロイ完了")
        return True

def main():
    """メイン実行関数"""
    deployer = WebBasedDeploy()
    
    try:
        success = deployer.run_web_deploy()
        
        if success:
            print("\n🎉 Web ベースデプロイが完了しました！")
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