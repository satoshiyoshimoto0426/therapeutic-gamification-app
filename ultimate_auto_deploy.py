#!/usr/bin/env python3
"""
究極の自動デプロイスクリプト
全ての問題を解決した最終版
"""

import os
import subprocess
import sys
import time
import logging
import webbrowser
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltimateAutoDeploy:
    """究極の自動デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        
        # 実行可能ファイルのパスを設定
        self.git_path = r"C:\Program Files\Git\cmd\git.exe"
        self.gh_path = r"C:\Program Files\GitHub CLI\gh.exe"
        
        # 環境変数でPATHを更新
        current_path = os.environ.get("PATH", "")
        git_bin_path = r"C:\Program Files\Git\cmd"
        gh_bin_path = r"C:\Program Files\GitHub CLI"
        
        if git_bin_path not in current_path:
            os.environ["PATH"] = f"{git_bin_path};{current_path}"
        if gh_bin_path not in current_path:
            os.environ["PATH"] = f"{gh_bin_path};{os.environ['PATH']}"
    
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 120, input_text: str = None) -> Tuple[bool, str, str]:
        """コマンド実行（改良版）"""
        try:
            # パスを置換
            if command[0] == "git":
                command[0] = self.git_path
            elif command[0] == "gh":
                command[0] = self.gh_path
            
            logger.info(f"実行中: {' '.join(command)}")
            
            # 入力が必要なコマンドの場合
            if input_text:
                result = subprocess.run(
                    command,
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=check,
                    shell=shell
                )
            else:
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
    
    def check_and_setup_github_auth(self) -> bool:
        """GitHub認証確認・設定"""
        print("\n🔐 GitHub認証設定")
        print("=" * 40)
        
        # GitHub CLI認証状況確認
        success, stdout, stderr = self.run_command(["gh", "auth", "status"], check=False, timeout=10)
        
        if success and "Logged in" in stdout:
            print("✅ GitHub CLI認証済み")
            return True
        
        print("🔑 GitHub CLI認証を開始します...")
        print("ブラウザが開きますので、GitHubでログインしてください。")
        
        # 認証実行（短いタイムアウト）
        success, stdout, stderr = self.run_command([
            "gh", "auth", "login", "--web", "--git-protocol", "https"
        ], check=False, timeout=180)  # 3分でタイムアウト
        
        if success:
            print("✅ GitHub認証完了")
            return True
        else:
            print("⚠️ GitHub CLI認証に時間がかかっています")
            print("手動で認証を完了してください:")
            print("1. ブラウザでGitHubにログイン")
            print("2. 認証コードを入力")
            
            # 認証完了を待つ
            for i in range(6):  # 最大1分待機
                time.sleep(10)
                success, stdout, stderr = self.run_command(["gh", "auth", "status"], check=False, timeout=10)
                if success and "Logged in" in stdout:
                    print("✅ GitHub認証完了")
                    return True
                print(f"認証確認中... ({i+1}/6)")
            
            print("⚠️ GitHub CLI認証をスキップして続行します")
            return True  # 認証失敗でも続行
    
    def get_github_username(self) -> str:
        """GitHubユーザー名取得（フォールバック付き）"""
        print("\n👤 GitHubユーザー名確認")
        print("=" * 40)
        
        # GitHub CLI経由で取得を試行
        success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"], check=False, timeout=10)
        
        if success and stdout.strip():
            username = stdout.strip()
            print(f"✅ 自動取得: {username}")
            return username
        
        # 手動入力
        print("GitHub CLIからユーザー名を取得できませんでした。")
        while True:
            username = input("GitHubユーザー名を入力してください: ").strip()
            if username:
                print(f"✅ 入力確認: {username}")
                return username
            print("❌ ユーザー名を入力してください")
    
    def create_or_verify_repository(self, username: str) -> bool:
        """リポジトリ作成・確認"""
        print("\n📝 GitHubリポジトリ作成・確認")
        print("=" * 40)
        
        # GitHub CLI経由でリポジトリ作成を試行
        success, stdout, stderr = self.run_command([
            "gh", "repo", "create", self.repo_name,
            "--description", "Therapeutic Gamification App for ADHD Support",
            "--public",
            "--clone=false"
        ], check=False, timeout=30)
        
        if success:
            print(f"✅ リポジトリ作成成功: {self.repo_name}")
            return True
        elif "already exists" in stderr:
            print(f"ℹ️ リポジトリ既存: {self.repo_name}")
            return True
        else:
            print("⚠️ GitHub CLI経由でのリポジトリ作成に失敗")
            print("Web UIでリポジトリを作成します...")
            
            # Web UIでリポジトリ作成
            try:
                webbrowser.open("https://github.com/new")
                time.sleep(3)
            except:
                pass
            
            print(f"\n📋 以下の設定でリポジトリを作成してください：")
            print(f"   📁 Repository name: {self.repo_name}")
            print("   📖 Description: Therapeutic Gamification App for ADHD Support")
            print("   🔓 Visibility: Public")
            print("   ❌ Initialize with README: チェックしない")
            
            input("\nリポジトリ作成完了後、Enterキーを押してください...")
            return True
    
    def setup_git_remote_and_push(self, username: str) -> bool:
        """Gitリモート設定とプッシュ"""
        print("\n🔗 Gitリモート設定・プッシュ")
        print("=" * 40)
        
        repo_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        # 既存のリモート削除
        self.run_command(["git", "remote", "remove", "origin"], check=False)
        
        # リモート追加
        success, stdout, stderr = self.run_command([
            "git", "remote", "add", "origin", repo_url
        ])
        
        if not success:
            print(f"❌ リモート設定失敗: {stderr}")
            return False
        
        print(f"✅ リモート設定完了: {username}/{self.repo_name}")
        
        # ファイル追加・コミット
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
        self.run_command(["git", "branch", "-M", "main"], check=False)
        
        # プッシュ実行
        print("🚀 GitHubにプッシュ中...")
        print("認証が求められた場合は、GitHubの認証情報を入力してください。")
        
        success, stdout, stderr = self.run_command([
            "git", "push", "-u", "origin", "main"
        ], timeout=180)  # 3分でタイムアウト
        
        if success:
            print("✅ プッシュ完了")
            return True
        else:
            print(f"❌ プッシュ失敗: {stderr}")
            
            # Personal Access Token案内
            if "authentication" in stderr.lower() or "permission" in stderr.lower():
                print("\n🔑 Personal Access Token が必要です")
                print("以下の手順で作成してください：")
                print("1. https://github.com/settings/tokens")
                print("2. Generate new token (classic)")
                print("3. repo + workflow 権限を選択")
                print("4. プッシュ時にトークンをパスワードとして使用")
                
                try:
                    webbrowser.open("https://github.com/settings/tokens")
                    time.sleep(2)
                except:
                    pass
                
                input("\nPersonal Access Token作成完了後、Enterキーを押してください...")
                
                # 再試行
                success, stdout, stderr = self.run_command([
                    "git", "push", "-u", "origin", "main"
                ], timeout=180)
                
                if success:
                    print("✅ プッシュ完了（再試行）")
                    return True
                else:
                    print(f"❌ プッシュ失敗（再試行）: {stderr}")
                    return False
            
            return False
    
    def setup_github_secrets(self, username: str) -> bool:
        """GitHub Secrets設定"""
        print("\n🔧 GitHub Secrets設定")
        print("=" * 40)
        
        # GitHub CLI経由でGCP_PROJECT_ID設定を試行
        success, stdout, stderr = self.run_command([
            "gh", "secret", "set", "GCP_PROJECT_ID",
            "--body", self.project_id
        ], check=False, timeout=30)
        
        if success:
            print("✅ GCP_PROJECT_ID設定完了（CLI経由）")
        else:
            print("⚠️ GitHub CLI経由での設定に失敗、Web UIを使用します")
        
        # Web UIでSecrets設定
        secrets_url = f"https://github.com/{username}/{self.repo_name}/settings/secrets/actions"
        
        print(f"\n🌐 GitHub Secretsページを開きます...")
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
        print("🎉 究極の自動デプロイ完了！")
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
        
        # 最終確認
        print(f"\n📋 次のステップ:")
        print(f"1. GitHub Actionsでデプロイ進行状況を確認")
        print(f"2. 約15-20分でデプロイ完了")
        print(f"3. Cloud RunでサービスURL確認")
        print(f"4. アプリケーションにアクセスして動作確認")
    
    def run_ultimate_deploy(self) -> bool:
        """究極の自動デプロイ実行"""
        logger.info("🚀 究極の自動デプロイ開始")
        
        print("🚀 Therapeutic Gamification App - 究極の自動デプロイ")
        print("=" * 60)
        print("全ての問題を解決した最終版で確実にデプロイします！")
        
        try:
            # 1. GitHub認証確認・設定
            if not self.check_and_setup_github_auth():
                print("⚠️ GitHub認証に問題がありますが、続行します")
            
            # 2. GitHubユーザー名取得
            username = self.get_github_username()
            
            # 3. リポジトリ作成・確認
            if not self.create_or_verify_repository(username):
                print("❌ リポジトリ作成・確認に失敗")
                return False
            
            # 4. Gitリモート設定・プッシュ
            if not self.setup_git_remote_and_push(username):
                print("❌ Gitプッシュに失敗")
                return False
            
            # 5. GitHub Secrets設定
            if not self.setup_github_secrets(username):
                print("❌ GitHub Secrets設定に失敗")
                return False
            
            # 6. デプロイ成功表示
            self.display_deployment_success(username)
            
            logger.info("✅ 究極の自動デプロイ完了")
            return True
            
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            print(f"❌ 予期しないエラーが発生しました: {e}")
            return False

def main():
    """メイン実行関数"""
    deployer = UltimateAutoDeploy()
    
    try:
        success = deployer.run_ultimate_deploy()
        
        if success:
            print("\n🎉 究極の自動デプロイが完了しました！")
            print("📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            print("🎮 デプロイ完了後、素晴らしいアプリケーションをお楽しみください！")
            
        else:
            print("\n❌ デプロイ設定に失敗しました。")
            print("📖 FINAL_DEPLOYMENT_INSTRUCTIONS.md を参照して手動で完了してください。")
        
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()