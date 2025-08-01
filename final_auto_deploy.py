#!/usr/bin/env python3
"""
最終自動デプロイスクリプト
パス問題を解決して完全自動デプロイを実行
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

class FinalAutoDeploy:
    """最終自動デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.repo_name = "therapeutic-gamification-app"
        
        # 実行可能ファイルのパスを明示的に設定
        self.git_path = self.find_executable("git", [
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files (x86)\Git\cmd\git.exe"
        ])
        
        self.gh_path = self.find_executable("gh", [
            r"C:\Program Files\GitHub CLI\gh.exe",
            r"C:\Program Files (x86)\GitHub CLI\gh.exe"
        ])
        
        logger.info(f"Git path: {self.git_path}")
        logger.info(f"GitHub CLI path: {self.gh_path}")
    
    def find_executable(self, name: str, paths: List[str]) -> str:
        """実行可能ファイルを検索"""
        # 指定されたパスから検索
        for path in paths:
            if os.path.exists(path):
                return path
        
        # PATHから検索
        try:
            result = subprocess.run(["where", name], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # デフォルトとしてコマンド名を返す
        return name
    
    def run_command(self, command: List[str], check: bool = True, shell: bool = False, timeout: int = 300) -> Tuple[bool, str, str]:
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
    
    def check_prerequisites(self) -> bool:
        """前提条件確認"""
        logger.info("前提条件確認")
        
        print("\n🔍 システム確認中...")
        
        # Git確認
        success, stdout, stderr = self.run_command(["git", "--version"], check=False)
        if success:
            print(f"✅ Git: {stdout.strip()}")
        else:
            print(f"❌ Git: 見つかりません")
            return False
        
        # GitHub CLI確認
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        if success:
            print(f"✅ GitHub CLI: {stdout.strip()}")
        else:
            print(f"❌ GitHub CLI: 見つかりません")
            return False
        
        # Gitリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "status"], check=False)
        if success:
            print("✅ Gitリポジトリ: 確認済み")
        else:
            print("❌ Gitリポジトリ: 初期化が必要")
            return False
        
        logger.info("前提条件確認完了")
        return True
    
    def authenticate_github(self) -> bool:
        """GitHub認証"""
        logger.info("GitHub認証確認")
        
        print("\n🔐 GitHub認証確認中...")
        
        # 既存の認証確認
        success, stdout, stderr = self.run_command(["gh", "auth", "status"], check=False)
        
        if success and "Logged in" in stdout:
            print("✅ GitHub認証済み")
            logger.info("GitHub認証済み")
            return True
        
        print("🔑 GitHub認証が必要です")
        print("ブラウザでGitHub認証を行います...")
        
        # ブラウザ認証実行
        success, stdout, stderr = self.run_command([
            "gh", "auth", "login", "--web", "--git-protocol", "https"
        ], timeout=600)
        
        if success:
            print("✅ GitHub認証完了")
            logger.info("GitHub認証完了")
            return True
        else:
            print(f"❌ GitHub認証失敗: {stderr}")
            logger.error(f"GitHub認証失敗: {stderr}")
            return False
    
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
    
    def setup_git_remote(self) -> bool:
        """Gitリモート設定"""
        logger.info("Gitリモート設定")
        
        print("\n🔗 Gitリモート設定中...")
        
        # 現在のユーザー名取得
        success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"], check=False)
        
        if not success:
            print("❌ GitHubユーザー名取得失敗")
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
            logger.error(f"git add失敗: {stderr}")
            return False
        
        # コミット
        commit_message = f"feat: complete deployment setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            print(f"❌ git commit失敗: {stderr}")
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
            print("✅ プッシュ完了")
            logger.info("GitHubプッシュ成功")
            return True
        else:
            print(f"❌ プッシュ失敗: {stderr}")
            logger.error(f"GitHubプッシュ失敗: {stderr}")
            return False
    
    def setup_github_secrets_auto(self) -> bool:
        """GitHub Secrets自動設定"""
        logger.info("GitHub Secrets自動設定")
        
        print("\n🔧 GitHub Secrets設定中...")
        
        # GCP_PROJECT_ID設定
        success, stdout, stderr = self.run_command([
            "gh", "secret", "set", "GCP_PROJECT_ID",
            "--body", self.project_id
        ], check=False)
        
        if success:
            print("✅ GCP_PROJECT_ID設定完了")
            logger.info("GCP_PROJECT_ID設定完了")
        else:
            print(f"⚠️ GCP_PROJECT_ID設定失敗: {stderr}")
            logger.warning(f"GCP_PROJECT_ID設定失敗: {stderr}")
        
        # GCP_SA_KEY設定案内
        print("\n🔑 GCP_SA_KEY設定が必要です")
        print("Google Cloud Consoleを開いてサービスアカウントキーを作成します...")
        
        try:
            webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
            time.sleep(2)
        except:
            pass
        
        print("\n📋 以下の手順でサービスアカウントを作成してください：")
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
        print("10. JSON内容全体をコピー")
        
        input("\nサービスアカウントキー作成完了後、Enterキーを押してください...")
        
        # 簡易的なGCP_SA_KEY設定
        print("\n📝 以下のコマンドでGCP_SA_KEYを設定してください：")
        print("gh secret set GCP_SA_KEY")
        print("（実行後、JSON内容を貼り付けてEnterキーを押す）")
        
        return True
    
    def display_final_instructions(self) -> None:
        """最終手順表示"""
        print("\n" + "=" * 60)
        print("🎉 自動デプロイ設定完了！")
        print("=" * 60)
        
        # 現在のユーザー名取得
        success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"], check=False)
        
        if success:
            username = stdout.strip()
            repo_url = f"https://github.com/{username}/{self.repo_name}"
            actions_url = f"{repo_url}/actions"
            
            print(f"\n📊 デプロイメント監視:")
            print(f"   🔗 GitHub Actions: {actions_url}")
            print(f"   ⏱️ 所要時間: 約15-20分")
            print(f"   📋 処理順序: テスト → ビルド → デプロイ → 監視")
            
            print(f"\n🌐 GitHub Actionsページを開きます...")
            try:
                webbrowser.open(actions_url)
                time.sleep(2)
            except:
                pass
            
            print(f"\n✅ デプロイ成功の確認方法:")
            print(f"   - 全ジョブが緑色（成功）")
            print(f"   - Cloud Runにサービスが作成される")
            print(f"   - サービスURLにアクセス可能")
            
            print(f"\n🎮 デプロイ完了後:")
            print(f"   - Cloud Run Console: https://console.cloud.google.com/run")
            print(f"   - サービスURLでアプリケーション確認")
            print(f"   - 素晴らしい治療的ゲーミフィケーションアプリをお楽しみください！")
    
    def run_final_deploy(self) -> bool:
        """最終デプロイ実行"""
        logger.info("🚀 最終自動デプロイ開始")
        
        print("🚀 Therapeutic Gamification App - 最終自動デプロイ")
        print("=" * 60)
        
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
        if not self.setup_github_secrets_auto():
            return False
        
        # 7. 最終手順表示
        self.display_final_instructions()
        
        logger.info("✅ 最終自動デプロイ完了")
        return True

def main():
    """メイン実行関数"""
    deployer = FinalAutoDeploy()
    
    try:
        success = deployer.run_final_deploy()
        
        if success:
            print("\n🎉 最終自動デプロイが完了しました！")
            print("📊 GitHub Actionsでデプロイ進行状況を確認してください。")
            
        else:
            print("\n❌ デプロイ設定に失敗しました。")
            print("🔧 手動で以下を確認してください：")
            print("   - Git がインストールされているか")
            print("   - GitHub CLI がインストールされているか")
            print("   - Gitリポジトリが初期化されているか")
        
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()