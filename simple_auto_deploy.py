#!/usr/bin/env python3
"""
シンプル自動デプロイスクリプト
既存のGitを使用してデプロイメントファイルを準備し、手順を案内
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

class SimpleAutoDeploy:
    """シンプル自動デプロイクラス"""
    
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
    
    def create_deployment_files(self) -> bool:
        """デプロイメントファイル作成"""
        logger.info("デプロイメントファイル作成")
        
        # README.md作成
        readme_content = f"""# {self.repo_name}

Therapeutic Gamification App for ADHD Support

## 🎮 概要

ADHD支援のための治療的ゲーミフィケーションアプリケーション

### 主な機能
- **タスク管理**: ポモドーロタイマー・習慣トラッキング
- **RPG要素**: XP・レベル・装備・ガチャシステム
- **AI生成ストーリー**: パーソナライズド治療体験
- **ADHD支援**: 認知負荷軽減・時間知覚支援
- **保護者支援**: 進捗レポート・安全性監視

## 🚀 デプロイメント

このリポジトリはGitHub Actionsを使用した自動デプロイメントに対応しています。

### 必要な設定

1. **GitHub Secrets設定**:
   - `GCP_PROJECT_ID`: `{self.project_id}`
   - `GCP_SA_KEY`: Google Cloud サービスアカウントキー

2. **自動デプロイ**:
   - `main`ブランチへのプッシュで自動デプロイ開始
   - 約15-20分でCloud Runにデプロイ完了

## 📊 技術スタック

- **Backend**: Python 3.12 + FastAPI
- **Frontend**: TypeScript + React
- **Database**: Google Cloud Firestore
- **Infrastructure**: Google Cloud Run
- **CI/CD**: GitHub Actions

## 🛡️ セキュリティ・プライバシー

- GDPR準拠
- 治療的安全性AI監視
- エンドツーエンド暗号化
- 24/7セキュリティ監視

---

**作成日**: {datetime.now().strftime('%Y-%m-%d')}  
**ステータス**: Production Ready ✅
"""
        
        try:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(readme_content)
            logger.info("README.md作成完了")
        except Exception as e:
            logger.error(f"README.md作成エラー: {e}")
            return False
        
        # デプロイメント設定ファイル作成
        deploy_config = f"""# Deployment Configuration

PROJECT_ID={self.project_id}
SERVICE_NAME={self.service_name}
REGION=asia-northeast1
ENVIRONMENT=production

# Generated at: {datetime.now().isoformat()}
"""
        
        try:
            with open("deploy.config", "w", encoding="utf-8") as f:
                f.write(deploy_config)
            logger.info("deploy.config作成完了")
        except Exception as e:
            logger.error(f"deploy.config作成エラー: {e}")
            return False
        
        return True
    
    def commit_changes(self) -> bool:
        """変更をコミット"""
        logger.info("変更をコミット")
        
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
        
        logger.info("コミット完了")
        return True
    
    def open_github_new_repo(self) -> None:
        """GitHub新規リポジトリページを開く"""
        logger.info("GitHub新規リポジトリページを開く")
        
        print("\n" + "=" * 60)
        print("📝 GitHubリポジトリ作成")
        print("=" * 60)
        
        print("\n🌐 GitHubの新規リポジトリ作成ページを開きます...")
        
        try:
            webbrowser.open("https://github.com/new")
            time.sleep(2)
        except:
            pass
        
        print(f"\n📋 以下の設定でリポジトリを作成してください：")
        print(f"   📁 Repository name: {self.repo_name}")
        print("   📖 Description: Therapeutic Gamification App for ADHD Support")
        print("   🔓 Visibility: Public (推奨) または Private")
        print("   ❌ Initialize with README: チェックしない")
        print("   ❌ Add .gitignore: None")
        print("   ❌ Choose a license: None")
        
        print("\n✅ 'Create repository' ボタンをクリック")
    
    def get_github_info(self) -> Tuple[str, str]:
        """GitHub情報取得"""
        print("\n" + "=" * 60)
        print("👤 GitHub情報入力")
        print("=" * 60)
        
        while True:
            username = input("\nGitHubユーザー名を入力してください: ").strip()
            if username:
                break
            print("❌ ユーザー名を入力してください")
        
        # リポジトリ名確認
        print(f"\nリポジトリ名: {self.repo_name}")
        use_default = input("このリポジトリ名を使用しますか？ (y/n): ").strip().lower()
        
        if use_default != 'y':
            while True:
                repo_name = input("リポジトリ名を入力してください: ").strip()
                if repo_name:
                    self.repo_name = repo_name
                    break
                print("❌ リポジトリ名を入力してください")
        
        return username, self.repo_name
    
    def setup_remote_and_push(self, username: str, repo_name: str) -> bool:
        """リモート設定とプッシュ"""
        logger.info("リモート設定とプッシュ")
        
        repo_url = f"https://github.com/{username}/{repo_name}.git"
        
        # 既存のリモート削除
        self.run_command(["git", "remote", "remove", "origin"], check=False)
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ])
        
        if not success:
            logger.error(f"リモート追加失敗: {stderr}")
            return False
        
        # ブランチ設定
        success, stdout, stderr = self.run_command([
            "git", "branch", "-M", "main"
        ], check=False)
        
        # プッシュ実行
        print(f"\n🚀 GitHubにプッシュ中...")
        success, stdout, stderr = self.run_command([
            "git", "push", "-u", "origin", "main"
        ])
        
        if success:
            logger.info("GitHubプッシュ成功")
            return True
        else:
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            
            # 認証が必要な場合の案内
            if "authentication" in stderr.lower() or "permission" in stderr.lower():
                print("\n" + "=" * 60)
                print("🔐 GitHub認証が必要です")
                print("=" * 60)
                print("\n以下の方法で認証してください：")
                print("\n1. Personal Access Token使用:")
                print("   - GitHub > Settings > Developer settings > Personal access tokens")
                print("   - Generate new token (classic)")
                print("   - repo権限を選択")
                print("   - プッシュ時にユーザー名とトークンを入力")
                
                input("\n認証設定完了後、Enterキーを押してください...")
                
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
    
    def setup_github_secrets(self, username: str, repo_name: str) -> None:
        """GitHub Secrets設定案内"""
        print("\n" + "=" * 60)
        print("🔧 GitHub Secrets設定")
        print("=" * 60)
        
        repo_url = f"https://github.com/{username}/{repo_name}"
        secrets_url = f"{repo_url}/settings/secrets/actions"
        
        print(f"\n🌐 GitHub Secretsページを開きます...")
        
        try:
            webbrowser.open(secrets_url)
            time.sleep(2)
        except:
            pass
        
        print(f"\n📋 以下の2つのSecretsを設定してください：")
        
        print(f"\n🔑 Secret 1:")
        print(f"   Name: GCP_PROJECT_ID")
        print(f"   Value: {self.project_id}")
        
        print(f"\n🔑 Secret 2:")
        print(f"   Name: GCP_SA_KEY")
        print(f"   Value: [Google Cloudサービスアカウントキー]")
        
        print(f"\n📖 サービスアカウントキー取得手順:")
        print(f"   1. Google Cloud Console を開く")
        print(f"   2. プロジェクト '{self.project_id}' を選択")
        print(f"   3. IAM & Admin > Service Accounts")
        print(f"   4. 'Create Service Account' をクリック")
        print(f"   5. Name: github-actions, Description: GitHub Actions CI/CD")
        print(f"   6. 以下の権限を付与:")
        
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
            print(f"      - {role}")
        
        print(f"   7. Keys タブ > Add Key > Create new key > JSON")
        print(f"   8. ダウンロードしたJSONファイルの内容全体をコピー")
        print(f"   9. GitHub SecretsのGCP_SA_KEYに貼り付け")
        
        print(f"\n🌐 Google Cloud Console:")
        try:
            webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
            time.sleep(1)
        except:
            pass
    
    def monitor_deployment(self, username: str, repo_name: str) -> None:
        """デプロイメント監視案内"""
        print("\n" + "=" * 60)
        print("📊 GitHub Actions デプロイメント監視")
        print("=" * 60)
        
        actions_url = f"https://github.com/{username}/{repo_name}/actions"
        
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
        
        print(f"\n🎮 デプロイ完了後:")
        print(f"   - Cloud Run Console でサービスURL確認")
        print(f"   - アプリケーションにアクセスして動作確認")
        print(f"   - 素晴らしい治療的ゲーミフィケーションアプリをお楽しみください！")
    
    def run_simple_auto_deploy(self) -> bool:
        """シンプル自動デプロイ実行"""
        logger.info("🚀 シンプル自動デプロイ開始")
        
        # 1. Git状態確認
        if not self.check_git_status():
            return False
        
        # 2. デプロイメントファイル作成
        if not self.create_deployment_files():
            return False
        
        # 3. 変更をコミット
        if not self.commit_changes():
            return False
        
        # 4. GitHubリポジトリ作成ページを開く
        self.open_github_new_repo()
        
        input("\nGitHubリポジトリ作成完了後、Enterキーを押してください...")
        
        # 5. GitHub情報取得
        username, repo_name = self.get_github_info()
        
        # 6. リモート設定とプッシュ
        if not self.setup_remote_and_push(username, repo_name):
            return False
        
        # 7. GitHub Secrets設定案内
        self.setup_github_secrets(username, repo_name)
        
        input("\nGitHub Secrets設定完了後、Enterキーを押してください...")
        
        # 8. デプロイメント監視案内
        self.monitor_deployment(username, repo_name)
        
        logger.info("✅ シンプル自動デプロイ設定完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - シンプル自動デプロイ")
    print("=" * 60)
    
    deployer = SimpleAutoDeploy()
    
    try:
        success = deployer.run_simple_auto_deploy()
        
        if success:
            print("\n🎉 シンプル自動デプロイが完了しました！")
            print("\n📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            print("🎮 デプロイ完了後、素晴らしいアプリケーションをお楽しみください！")
            
            print("\n🔗 重要なリンク:")
            print("   - GitHub Actions: リポジトリ > Actions タブ")
            print("   - Cloud Run: https://console.cloud.google.com/run")
            print("   - Google Cloud Console: https://console.cloud.google.com/")
            
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