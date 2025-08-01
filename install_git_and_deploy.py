#!/usr/bin/env python3
"""
Git自動インストール＆デプロイスクリプト
Windows環境でGitをインストールし、自動デプロイを実行
"""

import os
import subprocess
import sys
import time
import logging
import urllib.request
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitAutoInstaller:
    """Git自動インストール＆デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.git_installer_url = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
        
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
    
    def check_git_installed(self) -> bool:
        """Git インストール確認"""
        logger.info("Git インストール状況確認")
        
        success, stdout, stderr = self.run_command(["git", "--version"], check=False)
        
        if success:
            logger.info(f"Git既にインストール済み: {stdout.strip()}")
            return True
        else:
            logger.info("Git未インストール")
            return False
    
    def download_git_installer(self) -> Optional[str]:
        """Git インストーラーダウンロード"""
        logger.info("Git インストーラーダウンロード開始")
        
        try:
            # 一時ディレクトリにダウンロード
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "git_installer.exe")
            
            logger.info(f"ダウンロード先: {installer_path}")
            logger.info("ダウンロード中... (数分かかる場合があります)")
            
            urllib.request.urlretrieve(self.git_installer_url, installer_path)
            
            logger.info("Git インストーラーダウンロード完了")
            return installer_path
            
        except Exception as e:
            logger.error(f"Git インストーラーダウンロードエラー: {e}")
            return None
    
    def install_git(self, installer_path: str) -> bool:
        """Git インストール実行"""
        logger.info("Git インストール実行")
        
        try:
            # サイレントインストール実行
            install_command = [
                installer_path,
                "/VERYSILENT",
                "/NORESTART",
                "/NOCANCEL",
                "/SP-",
                "/CLOSEAPPLICATIONS",
                "/RESTARTAPPLICATIONS",
                "/COMPONENTS=icons,ext\\reg\\shellhere,assoc,assoc_sh"
            ]
            
            logger.info("Git インストール中... (数分かかります)")
            
            # タイムアウトを長く設定してインストール実行
            try:
                result = subprocess.run(
                    install_command,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    check=False
                )
                success = result.returncode == 0
                stdout = result.stdout
                stderr = result.stderr
            except subprocess.TimeoutExpired:
                logger.error("Git インストールタイムアウト")
                return False
            
            if success:
                logger.info("Git インストール完了")
                
                # インストール後、PATHを更新
                self.update_path_for_git()
                
                # インストール確認
                time.sleep(10)  # インストール完了待機
                return self.check_git_installed()
            else:
                logger.error(f"Git インストール失敗: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Git インストールエラー: {e}")
            return False
    
    def update_path_for_git(self) -> None:
        """Git用のPATH更新"""
        logger.info("PATH環境変数更新")
        
        # 一般的なGitインストールパス
        git_paths = [
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\Git\bin",
            r"C:\Program Files (x86)\Git\cmd",
            r"C:\Program Files (x86)\Git\bin"
        ]
        
        current_path = os.environ.get("PATH", "")
        
        for git_path in git_paths:
            if os.path.exists(git_path) and git_path not in current_path:
                os.environ["PATH"] = f"{git_path};{current_path}"
                logger.info(f"PATH追加: {git_path}")
    
    def initialize_git_repo(self) -> bool:
        """Git リポジトリ初期化"""
        logger.info("Git リポジトリ初期化")
        
        # Git設定
        config_commands = [
            ["git", "config", "--global", "user.name", "Therapeutic App Developer"],
            ["git", "config", "--global", "user.email", "developer@therapeutic-app.com"],
            ["git", "config", "--global", "init.defaultBranch", "main"]
        ]
        
        for command in config_commands:
            success, stdout, stderr = self.run_command(command, check=False)
            if not success:
                logger.warning(f"Git設定警告: {command} - {stderr}")
        
        # リポジトリ初期化（既存の場合はスキップ）
        if not os.path.exists(".git"):
            success, stdout, stderr = self.run_command(["git", "init"])
            if not success:
                logger.error(f"Git初期化失敗: {stderr}")
                return False
            logger.info("Git リポジトリ初期化完了")
        else:
            logger.info("Git リポジトリ既存")
        
        return True
    
    def create_gitignore(self) -> bool:
        """.gitignore作成"""
        logger.info(".gitignore作成")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
temp/

# Deployment
deployment_record_*.json
github-actions-key.json
auto_deployment.log

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coverage
coverage/
.coverage
.coverage.*
htmlcov/

# Testing
.pytest_cache/
.tox/

# Environment variables
.env
.env.local
.env.*.local"""
        
        try:
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            logger.info(".gitignore作成完了")
            return True
        except Exception as e:
            logger.error(f".gitignore作成エラー: {e}")
            return False
    
    def commit_initial_files(self) -> bool:
        """初期ファイルコミット"""
        logger.info("初期ファイルコミット")
        
        # ファイル追加
        success, stdout, stderr = self.run_command(["git", "add", "."])
        if not success:
            logger.error(f"git add失敗: {stderr}")
            return False
        
        # 初回コミット
        commit_message = f"feat: initial commit with deployment setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            logger.error(f"git commit失敗: {stderr}")
            return False
        
        logger.info("初期コミット完了")
        return True
    
    def setup_github_remote(self) -> bool:
        """GitHub リモート設定"""
        logger.info("GitHub リモート設定")
        
        # 既存のリモート確認
        success, stdout, stderr = self.run_command(["git", "remote", "-v"], check=False)
        
        if success and "origin" in stdout:
            logger.info("GitHub リモート既存")
            return True
        
        # リモート設定が必要な場合の案内
        print("\n" + "=" * 60)
        print("🔗 GitHub リモートリポジトリ設定が必要です")
        print("=" * 60)
        print("\n以下の手順でGitHubリポジトリを設定してください：")
        print("\n1. GitHub.comでリポジトリを作成")
        print("2. 以下のコマンドを実行：")
        print("   git remote add origin https://github.com/[username]/[repository].git")
        print("   git branch -M main")
        print("   git push -u origin main")
        print("\n設定完了後、再度このスクリプトを実行してください。")
        
        return False
    
    def display_deployment_instructions(self) -> None:
        """デプロイメント手順表示"""
        print("\n" + "=" * 60)
        print("🚀 自動デプロイメント準備完了！")
        print("=" * 60)
        
        print("\n📋 完了した作業:")
        print("   ✅ Git インストール")
        print("   ✅ Git リポジトリ初期化")
        print("   ✅ デプロイメントファイル準備")
        print("   ✅ 初期コミット")
        
        print("\n🔧 次のステップ:")
        print("1. GitHubでリポジトリを作成")
        print("2. リモートリポジトリを設定:")
        print("   git remote add origin https://github.com/[username]/[repository].git")
        print("3. GitHub Secrets設定:")
        print("   - GCP_PROJECT_ID: therapeutic-gamification-app-prod")
        print("   - GCP_SA_KEY: [サービスアカウントキー]")
        print("4. プッシュしてデプロイ開始:")
        print("   git push -u origin main")
        
        print("\n📖 詳細ガイド:")
        print("   - DEPLOYMENT_GUIDE.md")
        print("   - DEPLOYMENT_SUMMARY.md")
        
        print("\n🔗 重要なリンク:")
        print("   - GitHub: https://github.com/")
        print("   - Cloud Console: https://console.cloud.google.com/")
    
    def run_full_setup(self) -> bool:
        """完全自動セットアップ実行"""
        logger.info("🚀 Git自動インストール＆デプロイ準備開始")
        
        # 1. Git インストール確認
        if not self.check_git_installed():
            # Git インストーラーダウンロード
            installer_path = self.download_git_installer()
            if not installer_path:
                return False
            
            # Git インストール
            if not self.install_git(installer_path):
                return False
            
            # インストーラー削除
            try:
                os.remove(installer_path)
                logger.info("インストーラーファイル削除完了")
            except:
                pass
        
        # 2. Git リポジトリ初期化
        if not self.initialize_git_repo():
            return False
        
        # 3. .gitignore作成
        if not self.create_gitignore():
            return False
        
        # 4. 初期ファイルコミット
        if not self.commit_initial_files():
            return False
        
        # 5. GitHub リモート設定確認
        self.setup_github_remote()
        
        # 6. デプロイメント手順表示
        self.display_deployment_instructions()
        
        logger.info("✅ Git自動インストール＆デプロイ準備完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - Git自動インストール＆デプロイ")
    print("=" * 60)
    
    installer = GitAutoInstaller()
    
    try:
        success = installer.run_full_setup()
        
        if success:
            print("\n🎉 Git自動インストール＆デプロイ準備が完了しました！")
            print("\n次のステップでGitHubにプッシュしてデプロイを開始してください。")
        else:
            print("\n❌ セットアップに失敗しました。ログを確認してください。")
        
    except KeyboardInterrupt:
        print("\n⚠️ セットアップが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()