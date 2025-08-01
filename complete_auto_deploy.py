#!/usr/bin/env python3
"""
完全自動デプロイスクリプト
GitHubリポジトリ作成からデプロイまで完全自動化
"""

import os
import subprocess
import sys
import time
import logging
import json
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteAutoDeploy:
    """完全自動デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        
    def run_command(self, command: List[str], check: bool = True, shell: bool = False) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            logger.info(f"実行中: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
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
    
    def check_git_status(self) -> bool:
        """Git状態確認"""
        logger.info("Git状態確認")
        
        # Git確認
        success, stdout, stderr = self.run_command(["git", "--version"], check=False)
        if not success:
            logger.error("Gitがインストールされていません")
            return False
        
        # リポジトリ確認
        success, stdout, stderr = self.run_command(["git", "status"], check=False)
        if not success:
            logger.error("Gitリポジトリではありません")
            return False
        
        logger.info("Git状態確認完了")
        return True
    
    def create_github_repo_instructions(self) -> None:
        """GitHubリポジトリ作成手順表示"""
        print("\n" + "=" * 60)
        print("📝 GitHubリポジトリ作成手順")
        print("=" * 60)
        
        print("\n🌐 ブラウザでGitHub.comを開きます...")
        
        # GitHubを自動で開く
        try:
            webbrowser.open("https://github.com/new")
            time.sleep(2)
        except:
            pass
        
        print("\n📋 以下の設定でリポジトリを作成してください：")
        print(f"   📁 Repository name: {self.repo_name}")
        print("   📖 Description: Therapeutic Gamification App for ADHD Support")
        print("   🔓 Visibility: Public (または Private)")
        print("   ❌ Initialize with README: チェックしない")
        print("   ❌ Add .gitignore: None")
        print("   ❌ Choose a license: None")
        
        print("\n✅ 'Create repository' ボタンをクリック")
        
        input("\nリポジトリ作成完了後、Enterキーを押してください...")
    
    def get_github_username(self) -> str:
        """GitHubユーザー名取得"""
        print("\n" + "=" * 60)
        print("👤 GitHubユーザー名入力")
        print("=" * 60)
        
        while True:
            username = input("\nGitHubユーザー名を入力してください: ").strip()
            if username:
                return username
            print("❌ ユーザー名を入力してください")
    
    def setup_github_remote(self, username: str) -> bool:
        """GitHubリモート設定"""
        logger.info("GitHubリモート設定")
        
        repo_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ], check=False)
        
        if not success and "already exists" not in stderr:
            logger.error(f"リモート追加失敗: {stderr}")
            return False
        
        # ブランチ設定
        success, stdout, stderr = self.run_command([
            "git", "branch", "-M", "main"
        ], check=False)
        
        if not success:
            logger.warning(f"ブランチ設定警告: {stderr}")
        
        logger.info(f"GitHubリモート設定完了: {repo_url}")
        return True
    
    def push_to_github(self) -> bool:
        """GitHubにプッシュ"""
        logger.info("GitHubにプッシュ")
        
        # 初回プッシュ
        success, stdout, stderr = self.run_command([
            "git", "push", "-u", "origin", "main"
        ])
        
        if success:
            logger.info("GitHubプッシュ成功")
            return True
        else:
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            
            # 認証エラーの場合の案内
            if "authentication" in stderr.lower() or "permission" in stderr.lower():
                print("\n" + "=" * 60)
                print("🔐 GitHub認証が必要です")
                print("=" * 60)
                print("\n以下のいずれかの方法で認証してください：")
                print("\n1. Personal Access Token使用:")
                print("   - GitHub > Settings > Developer settings > Personal access tokens")
                print("   - Generate new token (classic)")
                print("   - repo権限を選択")
                print("   - プッシュ時にユーザー名とトークンを入力")
                print("\n2. GitHub CLI使用:")
                print("   - gh auth login")
                print("   - ブラウザで認証")
                
                input("\n認証完了後、Enterキーを押してください...")
                
                # 再試行
                success, stdout, stderr = self.run_command([
                    "git", "push", "-u", "origin", "main"
                ])
                
                if success:
                    logger.info("GitHubプッシュ成功（再試行）")
                    return True
                else:
                    logger.error(f"GitHubプッシュ失敗（再試行）: {stderr}")
                    return False
            
            return False
    
    def display_github_secrets_setup(self, username: str) -> None:
        """GitHub Secrets設定手順表示"""
        print("\n" + "=" * 60)
        print("🔧 GitHub Secrets設定")
        print("=" * 60)
        
        repo_url = f"https://github.com/{username}/{self.repo_name}"
        secrets_url = f"{repo_url}/settings/secrets/actions"
        
        print(f"\n🌐 GitHub Secretsページを開きます...")
        
        # GitHub Secretsページを自動で開く
        try:
            webbrowser.open(secrets_url)
            time.sleep(2)
        except:
            pass
        
        print(f"\n📋 以下のSecretsを設定してください：")
        print("\n1. 'New repository secret' をクリック")
        print("\n2. 以下の2つのSecretsを作成：")
        
        print(f"\n   🔑 Secret 1:")
        print(f"   Name: GCP_PROJECT_ID")
        print(f"   Value: {self.project_id}")
        
        print(f"\n   🔑 Secret 2:")
        print(f"   Name: GCP_SA_KEY")
        print(f"   Value: [以下の手順でサービスアカウントキーを取得]")
        
        print(f"\n📖 サービスアカウントキー取得手順:")
        print(f"   1. Google Cloud Console を開く")
        print(f"   2. プロジェクト '{self.project_id}' を選択")
        print(f"   3. IAM & Admin > Service Accounts")
        print(f"   4. 'github-actions' サービスアカウントを作成")
        print(f"   5. キーを生成してJSON全体をコピー")
        
        input("\nGitHub Secrets設定完了後、Enterキーを押してください...")
    
    def monitor_github_actions(self, username: str) -> None:
        """GitHub Actions監視"""
        print("\n" + "=" * 60)
        print("📊 GitHub Actions監視")
        print("=" * 60)
        
        actions_url = f"https://github.com/{username}/{self.repo_name}/actions"
        
        print(f"\n🌐 GitHub Actionsページを開きます...")
        
        # GitHub Actionsページを自動で開く
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
    
    def run_complete_deploy(self) -> bool:
        """完全自動デプロイ実行"""
        logger.info("🚀 完全自動デプロイ開始")
        
        # 1. Git状態確認
        if not self.check_git_status():
            return False
        
        # 2. GitHubリポジトリ作成手順
        self.create_github_repo_instructions()
        
        # 3. GitHubユーザー名取得
        username = self.get_github_username()
        
        # 4. GitHubリモート設定
        if not self.setup_github_remote(username):
            return False
        
        # 5. GitHubにプッシュ
        if not self.push_to_github():
            return False
        
        # 6. GitHub Secrets設定
        self.display_github_secrets_setup(username)
        
        # 7. GitHub Actions監視
        self.monitor_github_actions(username)
        
        logger.info("✅ 完全自動デプロイ設定完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - 完全自動デプロイ")
    print("=" * 60)
    
    deployer = CompleteAutoDeploy()
    
    try:
        success = deployer.run_complete_deploy()
        
        if success:
            print("\n🎉 完全自動デプロイ設定が完了しました！")
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