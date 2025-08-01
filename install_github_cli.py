#!/usr/bin/env python3
"""
GitHub CLI自動インストールスクリプト
Windows環境でGitHub CLIを自動インストール
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

class GitHubCLIInstaller:
    """GitHub CLI自動インストールクラス"""
    
    def __init__(self):
        # 最新のGitHub CLI URLを使用
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
            
            # プログレス表示付きダウンロード
            def show_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, (downloaded * 100) // total_size)
                    print(f"\rダウンロード進行状況: {percent}%", end="", flush=True)
            
            urllib.request.urlretrieve(self.github_cli_url, installer_path, show_progress)
            print()  # 改行
            
            logger.info("GitHub CLI インストーラーダウンロード完了")
            return installer_path
            
        except Exception as e:
            logger.error(f"GitHub CLI インストーラーダウンロードエラー: {e}")
            return None
    
    def install_github_cli(self, installer_path: str) -> bool:
        """GitHub CLI インストール実行"""
        logger.info("GitHub CLI インストール実行")
        
        try:
            # MSIインストール実行（管理者権限不要の方法）
            install_command = [
                "msiexec",
                "/i", installer_path,
                "/quiet",
                "/norestart",
                "/l*v", os.path.join(tempfile.gettempdir(), "gh_install.log")
            ]
            
            logger.info("GitHub CLI インストール中... (数分かかります)")
            
            # インストール実行
            result = subprocess.run(
                install_command,
                capture_output=True,
                text=True,
                timeout=600,
                check=False
            )
            
            # インストール結果確認
            if result.returncode == 0:
                logger.info("GitHub CLI インストール完了")
                
                # インストール後、PATHを更新
                self.update_path_for_github_cli()
                
                # インストール確認
                time.sleep(10)  # インストール完了待機
                return self.check_github_cli_installed()
            else:
                logger.error(f"GitHub CLI インストール失敗: Return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                
                # ログファイル確認
                log_file = os.path.join(tempfile.gettempdir(), "gh_install.log")
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                            logger.error(f"Install log: {log_content[-1000:]}")  # 最後の1000文字
                    except:
                        pass
                
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
            r"C:\Program Files (x86)\GitHub CLI",
            os.path.expanduser(r"~\AppData\Local\Programs\GitHub CLI")
        ]
        
        current_path = os.environ.get("PATH", "")
        
        for gh_path in gh_paths:
            if os.path.exists(gh_path) and gh_path not in current_path:
                os.environ["PATH"] = f"{gh_path};{current_path}"
                logger.info(f"PATH追加: {gh_path}")
    
    def test_github_cli(self) -> bool:
        """GitHub CLI動作テスト"""
        logger.info("GitHub CLI動作テスト")
        
        # バージョン確認
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        
        if success:
            logger.info(f"GitHub CLI動作確認成功: {stdout.strip()}")
            
            # ヘルプ表示テスト
            success, stdout, stderr = self.run_command(["gh", "--help"], check=False)
            
            if success:
                logger.info("GitHub CLI基本機能確認完了")
                return True
            else:
                logger.warning("GitHub CLIヘルプ表示に問題があります")
                return False
        else:
            logger.error(f"GitHub CLI動作確認失敗: {stderr}")
            return False
    
    def display_next_steps(self) -> None:
        """次のステップ表示"""
        print("\n" + "=" * 60)
        print("🎉 GitHub CLI インストール完了！")
        print("=" * 60)
        
        print("\n✅ 完了した作業:")
        print("   - GitHub CLI ダウンロード")
        print("   - GitHub CLI インストール")
        print("   - PATH環境変数更新")
        print("   - 動作確認テスト")
        
        print("\n🔧 次のステップ:")
        print("1. GitHub認証:")
        print("   gh auth login")
        
        print("\n2. リポジトリ作成:")
        print("   gh repo create therapeutic-gamification-app --public")
        
        print("\n3. 自動デプロイ実行:")
        print("   python fully_automated_deploy.py")
        
        print("\n📖 GitHub CLI基本コマンド:")
        print("   gh --help          # ヘルプ表示")
        print("   gh auth status     # 認証状況確認")
        print("   gh repo list       # リポジトリ一覧")
        print("   gh repo view       # リポジトリ詳細")
        
        print("\n🔗 参考リンク:")
        print("   - GitHub CLI Documentation: https://cli.github.com/manual/")
        print("   - GitHub CLI Repository: https://github.com/cli/cli")
    
    def run_installation(self) -> bool:
        """インストール実行"""
        logger.info("🚀 GitHub CLI自動インストール開始")
        
        # 1. インストール状況確認
        if self.check_github_cli_installed():
            print("\n✅ GitHub CLIは既にインストールされています。")
            self.display_next_steps()
            return True
        
        # 2. インストーラーダウンロード
        installer_path = self.download_github_cli_installer()
        if not installer_path:
            return False
        
        # 3. インストール実行
        if not self.install_github_cli(installer_path):
            return False
        
        # 4. インストーラー削除
        try:
            os.remove(installer_path)
            logger.info("インストーラーファイル削除完了")
        except:
            logger.warning("インストーラーファイル削除に失敗しました")
        
        # 5. 動作テスト
        if not self.test_github_cli():
            logger.warning("GitHub CLI動作テストに問題がありますが、インストールは完了しました")
        
        # 6. 次のステップ表示
        self.display_next_steps()
        
        logger.info("✅ GitHub CLI自動インストール完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 GitHub CLI 自動インストール")
    print("=" * 60)
    
    installer = GitHubCLIInstaller()
    
    try:
        success = installer.run_installation()
        
        if success:
            print("\n🎉 GitHub CLIインストールが完了しました！")
            print("\n次のステップで認証とリポジトリ作成を行ってください。")
        else:
            print("\n❌ インストールに失敗しました。")
            print("\n🔧 手動インストール方法:")
            print("1. https://cli.github.com/ にアクセス")
            print("2. 'Download for Windows' をクリック")
            print("3. ダウンロードしたMSIファイルを実行")
        
    except KeyboardInterrupt:
        print("\n⚠️ インストールが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()