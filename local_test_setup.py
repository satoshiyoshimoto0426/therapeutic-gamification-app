#!/usr/bin/env python3
"""
ローカルテスト環境セットアップスクリプト

このスクリプトは、治療的ゲーミフィケーションアプリをローカル環境で
テストするための環境を自動的にセットアップします。
"""

import sys
import os
import subprocess
import shutil
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import platform


class Colors:
    """ターミナルカラーコード"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class EnvironmentChecker:
    """環境チェッククラス"""
    
    def __init__(self):
        self.results = {}
        self.is_windows = platform.system() == "Windows"
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Pythonバージョンチェック"""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version.major == 3 and version.minor >= 9:
                return True, f"Python {version_str} ✓"
            else:
                return False, f"Python {version_str} (3.9以上が必要)"
        except Exception as e:
            return False, f"Pythonバージョン確認エラー: {str(e)}"
    
    def check_node_version(self) -> Tuple[bool, str]:
        """Node.jsバージョンチェック"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # v16.0.0 形式から数値を抽出
                version_num = int(version_str.lstrip('v').split('.')[0])
                
                if version_num >= 16:
                    return True, f"Node.js {version_str} ✓"
                else:
                    return False, f"Node.js {version_str} (v16以上が必要)"
            else:
                return False, "Node.jsが見つかりません"
        except FileNotFoundError:
            return False, "Node.jsがインストールされていません"
        except Exception as e:
            return False, f"Node.jsバージョン確認エラー: {str(e)}"
    
    def check_npm(self) -> Tuple[bool, str]:
        """npmの存在確認"""
        try:
            # Windowsの場合、npm.cmdを試す
            npm_cmd = "npm.cmd" if self.is_windows else "npm"
            result = subprocess.run(
                [npm_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=self.is_windows
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                return True, f"npm {version_str} ✓"
            else:
                return False, "npmが見つかりません"
        except FileNotFoundError:
            # フロントエンドが不要な場合は警告のみ
            return True, "⚠️  npmが見つかりません (フロントエンド開発には必要)"
        except Exception as e:
            return True, f"⚠️  npm確認エラー: {str(e)} (フロントエンド開発には必要)"
    
    def check_pip(self) -> Tuple[bool, str]:
        """pipの存在確認"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip().split()[1]
                return True, f"pip {version_str} ✓"
            else:
                return False, "pipが見つかりません"
        except Exception as e:
            return False, f"pip確認エラー: {str(e)}"
    
    def check_disk_space(self) -> Tuple[bool, str]:
        """ディスク空き容量チェック"""
        try:
            stat = shutil.disk_usage(os.getcwd())
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb >= 2.0:
                return True, f"ディスク空き容量: {free_gb:.1f}GB ✓"
            else:
                return False, f"ディスク空き容量不足: {free_gb:.1f}GB (2GB以上推奨)"
        except Exception as e:
            return False, f"ディスク容量確認エラー: {str(e)}"
    
    def check_memory(self) -> Tuple[bool, str]:
        """メモリ容量チェック"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            used_percent = mem.percent
            
            if available_gb >= 2.0:
                return True, f"利用可能メモリ: {available_gb:.1f}GB / {total_gb:.1f}GB (使用率: {used_percent:.1f}%) ✓"
            else:
                # 警告だが続行可能
                return True, f"⚠️  利用可能メモリ: {available_gb:.1f}GB / {total_gb:.1f}GB (2GB以上推奨、続行可能)"
        except ImportError:
            return True, "⚠️  メモリチェックをスキップ (psutilが未インストール、続行可能)"
        except Exception as e:
            return True, f"⚠️  メモリ確認エラー: {str(e)} (続行可能)"
    
    def check_cpu(self) -> Tuple[bool, str]:
        """CPU情報チェック"""
        try:
            import psutil
            cpu_count = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_count >= 2:
                return True, f"CPU: {cpu_count}コア (使用率: {cpu_percent:.1f}%) ✓"
            else:
                return True, f"⚠️  CPU: {cpu_count}コア (2コア以上推奨、続行可能)"
        except ImportError:
            return True, "⚠️  CPUチェックをスキップ (psutilが未インストール、続行可能)"
        except Exception as e:
            return True, f"⚠️  CPU確認エラー: {str(e)} (続行可能)"
    
    def check_required_files(self) -> Tuple[bool, str]:
        """必要なファイルの存在確認"""
        required_files = [
            "requirements.txt",
            "frontend/package.json",
            "services/auth/main.py",
            "services/core-game/main.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            return True, "必要なファイル: すべて存在 ✓"
        else:
            return False, f"不足ファイル: {', '.join(missing_files)}"
    
    def run_all_checks(self) -> Dict[str, Tuple[bool, str]]:
        """全チェックの実行"""
        checks = {
            "Python": self.check_python_version(),
            "Node.js": self.check_node_version(),
            "npm": self.check_npm(),
            "pip": self.check_pip(),
            "CPU": self.check_cpu(),
            "メモリ": self.check_memory(),
            "ディスク容量": self.check_disk_space(),
            "必要ファイル": self.check_required_files()
        }
        
        self.results = checks
        return checks
    
    def get_system_info(self) -> Dict[str, str]:
        """システム情報の取得"""
        info = {
            "OS": platform.system(),
            "OSバージョン": platform.version(),
            "アーキテクチャ": platform.machine(),
            "Pythonバージョン": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "作業ディレクトリ": os.getcwd()
        }
        
        try:
            import psutil
            info["総メモリ"] = f"{psutil.virtual_memory().total / (1024 ** 3):.1f}GB"
            info["CPUコア数"] = str(psutil.cpu_count(logical=True))
        except ImportError:
            pass
        
        return info
    
    def print_results(self):
        """チェック結果の表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}環境チェック結果{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        all_passed = True
        failed_checks = []
        
        for check_name, (passed, message) in self.results.items():
            if passed:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} {check_name}: {message}")
            else:
                print(f"{Colors.FAIL}✗{Colors.ENDC} {check_name}: {message}")
                all_passed = False
                failed_checks.append(check_name)
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        if all_passed:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ すべてのチェックに合格しました！{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ 一部のチェックに失敗しました{Colors.ENDC}")
            self._print_recovery_hints(failed_checks)
            return False
    
    def _print_recovery_hints(self, failed_checks: List[str]):
        """復旧ヒントの表示"""
        print(f"\n{Colors.WARNING}{Colors.BOLD}💡 解決方法:{Colors.ENDC}\n")
        
        hints = {
            "Python": "Python 3.9以上をインストールしてください: https://www.python.org/downloads/",
            "Node.js": "Node.js v16以上をインストールしてください: https://nodejs.org/",
            "npm": "Node.jsをインストールすると、npmも自動的にインストールされます",
            "pip": "pipをインストールしてください: python -m ensurepip --upgrade",
            "ディスク容量": "不要なファイルを削除して、2GB以上の空き容量を確保してください",
            "メモリ": "他のアプリケーションを終了して、メモリを解放してください",
            "CPU": "このシステムでも動作しますが、パフォーマンスが低下する可能性があります",
            "必要ファイル": "プロジェクトのルートディレクトリで実行していることを確認してください"
        }
        
        for check_name in failed_checks:
            if check_name in hints:
                print(f"  • {Colors.OKCYAN}{check_name}{Colors.ENDC}: {hints[check_name]}")
        
        print(f"\n{Colors.WARNING}問題を解決してから再度実行してください{Colors.ENDC}\n")


class DependencyInstaller:
    """依存関係インストールクラス"""
    
    def __init__(self, max_retries: int = 3):
        self.is_windows = platform.system() == "Windows"
        self.max_retries = max_retries
    
    def _count_packages_in_requirements(self) -> int:
        """requirements.txtのパッケージ数をカウント"""
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                return len(lines)
        except Exception:
            return 0
    
    def _print_progress(self, current: int, total: int, package_name: str = ""):
        """進捗バーの表示"""
        if total == 0:
            return
        
        percent = int((current / total) * 100)
        bar_length = 40
        filled = int((bar_length * current) / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        package_info = f" - {package_name}" if package_name else ""
        print(f"\r  進捗: [{bar}] {percent}%{package_info}", end="", flush=True)
    
    def install_python_dependencies(self) -> bool:
        """Python依存関係のインストール（再試行機能付き、進捗表示あり）"""
        print(f"\n{Colors.OKCYAN}Python依存関係をインストール中...{Colors.ENDC}")
        
        # パッケージ数を取得
        package_count = self._count_packages_in_requirements()
        if package_count > 0:
            print(f"  インストール対象: {package_count}個のパッケージ")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    print(f"\n{Colors.WARNING}再試行 {attempt}/{self.max_retries}...{Colors.ENDC}")
                
                # リアルタイム進捗表示のため、stdoutをキャプチャせずに実行
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--progress-bar", "off"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                installed_count = 0
                current_package = ""
                
                # リアルタイムで出力を読み取り
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        # パッケージ名を抽出
                        if "Collecting" in line or "Installing" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                current_package = parts[1]
                                installed_count += 1
                                if package_count > 0:
                                    self._print_progress(installed_count, package_count, current_package)
                        elif "Successfully installed" in line:
                            if package_count > 0:
                                self._print_progress(package_count, package_count, "完了")
                            print()  # 改行
                
                process.wait(timeout=300)
                
                if process.returncode == 0:
                    print(f"{Colors.OKGREEN}✓ Python依存関係のインストール完了{Colors.ENDC}")
                    return True
                else:
                    print(f"\n{Colors.FAIL}✗ Python依存関係のインストール失敗 (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                    
                    if attempt < self.max_retries:
                        print(f"{Colors.OKCYAN}再試行します...{Colors.ENDC}")
                        continue
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"\n{Colors.FAIL}✗ インストールがタイムアウトしました (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                if attempt < self.max_retries:
                    continue
                return False
            except Exception as e:
                print(f"\n{Colors.FAIL}✗ インストールエラー: {str(e)} (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                if attempt < self.max_retries:
                    continue
                return False
        
        return False
    
    def _count_packages_in_package_json(self) -> int:
        """package.jsonのパッケージ数をカウント"""
        try:
            package_json_path = Path("frontend/package.json")
            if not package_json_path.exists():
                return 0
            
            with open(package_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                deps = len(data.get("dependencies", {}))
                dev_deps = len(data.get("devDependencies", {}))
                return deps + dev_deps
        except Exception:
            return 0
    
    def install_frontend_dependencies(self) -> bool:
        """フロントエンド依存関係のインストール（再試行機能付き、進捗表示あり）"""
        print(f"\n{Colors.OKCYAN}フロントエンド依存関係をインストール中...{Colors.ENDC}")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print(f"{Colors.WARNING}frontendディレクトリが見つかりません{Colors.ENDC}")
            return False
        
        # パッケージ数を取得
        package_count = self._count_packages_in_package_json()
        if package_count > 0:
            print(f"  インストール対象: {package_count}個のパッケージ")
        
        # Windowsの場合、npm.cmdを使用し、shellをTrueに設定
        if self.is_windows:
            npm_cmd = "npm.cmd"
            use_shell = True
        else:
            npm_cmd = "npm"
            use_shell = False
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    print(f"\n{Colors.WARNING}再試行 {attempt}/{self.max_retries}...{Colors.ENDC}")
                
                # リアルタイム進捗表示のため、stdoutをキャプチャせずに実行
                process = subprocess.Popen(
                    [npm_cmd, "install", "--progress=true"],
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    shell=use_shell,
                    bufsize=1,
                    universal_newlines=True
                )
                
                installed_count = 0
                current_package = ""
                
                # リアルタイムで出力を読み取り
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        # npmの進捗情報を抽出
                        if "added" in line.lower() or "updated" in line.lower():
                            # "added 123 packages" のような行から数値を抽出
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part.isdigit() and i + 1 < len(parts) and "package" in parts[i + 1]:
                                    installed_count = int(part)
                                    if package_count > 0:
                                        self._print_progress(min(installed_count, package_count), package_count, "")
                                    break
                        elif line.startswith("npm"):
                            # npm WARN などのメッセージは表示しない
                            continue
                
                process.wait(timeout=600)
                
                if process.returncode == 0:
                    if package_count > 0:
                        self._print_progress(package_count, package_count, "完了")
                        print()  # 改行
                    print(f"{Colors.OKGREEN}✓ フロントエンド依存関係のインストール完了{Colors.ENDC}")
                    return True
                else:
                    print(f"\n{Colors.FAIL}✗ フロントエンド依存関係のインストール失敗 (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                    
                    if attempt < self.max_retries:
                        print(f"{Colors.OKCYAN}再試行します...{Colors.ENDC}")
                        continue
                    return False
                    
            except FileNotFoundError:
                print(f"{Colors.WARNING}⚠️  npmが見つかりません。フロントエンド開発にはNode.jsとnpmが必要です{Colors.ENDC}")
                print(f"{Colors.OKCYAN}バックエンドのみのテストは可能です{Colors.ENDC}")
                return True  # バックエンドのみでも続行可能
            except subprocess.TimeoutExpired:
                print(f"\n{Colors.FAIL}✗ インストールがタイムアウトしました (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                if attempt < self.max_retries:
                    continue
                print(f"{Colors.OKCYAN}バックエンドのみのテストは可能です{Colors.ENDC}")
                return True  # バックエンドのみでも続行可能
            except Exception as e:
                print(f"\n{Colors.FAIL}✗ インストールエラー: {str(e)} (試行 {attempt}/{self.max_retries}){Colors.ENDC}")
                if attempt < self.max_retries:
                    continue
                print(f"{Colors.OKCYAN}バックエンドのみのテストは可能です{Colors.ENDC}")
                return True  # バックエンドのみでも続行可能
        
        return False
    
    def install_all(self) -> bool:
        """全依存関係のインストール"""
        python_ok = self.install_python_dependencies()
        frontend_ok = self.install_frontend_dependencies()
        
        return python_ok and frontend_ok


class EnvFileGenerator:
    """環境変数ファイル生成クラス"""
    
    def __init__(self):
        self.env_file = Path(".env.local")
        self.template = self._get_template()
    
    def _get_template(self) -> str:
        """環境変数テンプレート"""
        return """# ローカルテスト環境設定
# このファイルは自動生成されました

# データベース設定
USE_MOCK_DATABASE=true
MOCK_DATABASE_PERSIST=false
MOCK_DATABASE_FILE=./data/mock_firestore.json

# サービスポート設定
AUTH_SERVICE_PORT=8002
CORE_GAME_SERVICE_PORT=8001
TASK_MGMT_SERVICE_PORT=8003
MANDALA_SERVICE_PORT=8004
MOOD_TRACKING_SERVICE_PORT=8005

# フロントエンド設定
FRONTEND_PORT=3000
VITE_API_BASE_URL=http://localhost:8001

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=./logs/local_test.log

# テスト設定
TEST_DATA_DIR=./test_data
ENABLE_TEST_FIXTURES=true

# Python設定
PYTHONIOENCODING=utf-8
PYTHONPATH=.
"""
    
    def generate(self, force: bool = False) -> bool:
        """環境変数ファイルの生成"""
        if self.env_file.exists() and not force:
            print(f"{Colors.WARNING}.env.localファイルは既に存在します{Colors.ENDC}")
            response = input("上書きしますか？ (y/N): ")
            if response.lower() != 'y':
                print(f"{Colors.OKCYAN}既存のファイルを使用します{Colors.ENDC}")
                return True
            
            # バックアップ作成
            backup_file = Path(f".env.local.backup")
            shutil.copy(self.env_file, backup_file)
            print(f"{Colors.OKCYAN}バックアップを作成しました: {backup_file}{Colors.ENDC}")
        
        try:
            self.env_file.write_text(self.template, encoding='utf-8')
            print(f"{Colors.OKGREEN}✓ .env.localファイルを生成しました{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗ ファイル生成エラー: {str(e)}{Colors.ENDC}")
            return False


class InteractiveSetupWizard:
    """対話的セットアップウィザード"""
    
    def __init__(self):
        self.config = {}
        self.selected_services = []
        self.services_config = self._load_services_config()
    
    def _load_services_config(self) -> Dict:
        """サービス設定の読み込み"""
        try:
            config_path = Path("local_services_config.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"services": [], "frontend": {}}
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  サービス設定の読み込みに失敗: {str(e)}{Colors.ENDC}")
            return {"services": [], "frontend": {}}
    
    def _print_step_header(self, step_num: int, total_steps: int, title: str):
        """ステップヘッダーの表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}ステップ {step_num}/{total_steps}: {title}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    def _get_user_input(self, prompt: str, default: str = "", validator=None) -> str:
        """ユーザー入力の取得と検証"""
        while True:
            if default:
                user_input = input(f"{prompt} [{Colors.OKCYAN}{default}{Colors.ENDC}]: ").strip()
                if not user_input:
                    user_input = default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if validator:
                is_valid, message = validator(user_input)
                if not is_valid:
                    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
                    continue
            
            return user_input
    
    def _get_yes_no_input(self, prompt: str, default: bool = True) -> bool:
        """Yes/No入力の取得"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} ({default_str}): ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'はい']
    
    def welcome_screen(self):
        """ウェルカム画面"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🎮 ローカルテスト環境セットアップウィザード{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        print(f"{Colors.OKCYAN}このウィザードでは、以下の設定を対話的に行います:{Colors.ENDC}\n")
        print(f"  1. 環境チェック")
        print(f"  2. 起動するサービスの選択")
        print(f"  3. 設定の確認とプレビュー")
        print(f"  4. 依存関係のインストール")
        print(f"  5. 環境変数ファイルの生成\n")
        
        if not self._get_yes_no_input("セットアップを開始しますか？", True):
            print(f"{Colors.WARNING}セットアップをキャンセルしました{Colors.ENDC}")
            return False
        
        return True
    
    def step_environment_check(self) -> bool:
        """ステップ1: 環境チェック"""
        self._print_step_header(1, 5, "環境チェック")
        
        env_checker = EnvironmentChecker()
        env_checker.run_all_checks()
        
        if not env_checker.print_results():
            print(f"\n{Colors.WARNING}環境チェックで問題が見つかりました{Colors.ENDC}")
            if not self._get_yes_no_input("続行しますか？", False):
                return False
        
        return True
    
    def step_select_services(self):
        """ステップ2: サービス選択"""
        self._print_step_header(2, 5, "起動するサービスの選択")
        
        print(f"{Colors.OKCYAN}起動するサービスを選択してください{Colors.ENDC}\n")
        
        # 必須サービスの表示
        required_services = [s for s in self.services_config.get("services", []) if s.get("required", False)]
        optional_services = [s for s in self.services_config.get("services", []) if not s.get("required", False)]
        
        print(f"{Colors.BOLD}必須サービス (自動的に起動されます):{Colors.ENDC}")
        for service in required_services:
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {service.get('display_name', service['name'])}")
            print(f"    {Colors.OKCYAN}→ {service.get('description', 'N/A')}{Colors.ENDC}")
            self.selected_services.append(service['name'])
        
        # オプションサービスの選択
        if optional_services:
            print(f"\n{Colors.BOLD}オプションサービス:{Colors.ENDC}")
            for i, service in enumerate(optional_services, 1):
                print(f"\n  {i}. {service.get('display_name', service['name'])}")
                print(f"     {Colors.OKCYAN}→ {service.get('description', 'N/A')}{Colors.ENDC}")
                print(f"     ポート: {service.get('port', 'N/A')}")
                
                if self._get_yes_no_input(f"     このサービスを起動しますか？", True):
                    self.selected_services.append(service['name'])
                    print(f"     {Colors.OKGREEN}✓ 選択されました{Colors.ENDC}")
                else:
                    print(f"     {Colors.WARNING}スキップされました{Colors.ENDC}")
        
        # フロントエンドの選択
        frontend_config = self.services_config.get("frontend", {})
        if frontend_config:
            print(f"\n{Colors.BOLD}フロントエンド:{Colors.ENDC}")
            print(f"  {frontend_config.get('display_name', 'フロントエンド')}")
            print(f"  {Colors.OKCYAN}→ {frontend_config.get('description', 'N/A')}{Colors.ENDC}")
            
            if self._get_yes_no_input("  フロントエンドを起動しますか？", True):
                self.selected_services.append("frontend")
                print(f"  {Colors.OKGREEN}✓ 選択されました{Colors.ENDC}")
            else:
                print(f"  {Colors.WARNING}スキップされました (バックエンドのみ){Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}選択完了: {len(self.selected_services)}個のサービス{Colors.ENDC}")
    
    def step_configure_settings(self):
        """ステップ3: 設定の確認と編集"""
        self._print_step_header(3, 5, "設定の確認とプレビュー")
        
        print(f"{Colors.OKCYAN}環境変数の設定を行います{Colors.ENDC}\n")
        
        # データベース設定
        print(f"{Colors.BOLD}データベース設定:{Colors.ENDC}")
        use_mock = self._get_yes_no_input("  モックデータベースを使用しますか？", True)
        self.config['USE_MOCK_DATABASE'] = str(use_mock).lower()
        
        if use_mock:
            persist = self._get_yes_no_input("  データを永続化しますか？", False)
            self.config['MOCK_DATABASE_PERSIST'] = str(persist).lower()
        
        # ログ設定
        print(f"\n{Colors.BOLD}ログ設定:{Colors.ENDC}")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        print(f"  利用可能なログレベル: {', '.join(log_levels)}")
        
        def validate_log_level(level):
            if level.upper() in log_levels:
                return True, ""
            return False, f"無効なログレベルです。{', '.join(log_levels)}から選択してください"
        
        log_level = self._get_user_input("  ログレベル", "INFO", validate_log_level)
        self.config['LOG_LEVEL'] = log_level.upper()
        
        # ポート設定のカスタマイズ
        print(f"\n{Colors.BOLD}ポート設定:{Colors.ENDC}")
        if self._get_yes_no_input("  デフォルトのポート設定を使用しますか？", True):
            print(f"  {Colors.OKGREEN}✓ デフォルト設定を使用します{Colors.ENDC}")
        else:
            print(f"  {Colors.OKCYAN}カスタムポート設定 (Enter でデフォルト値を使用){Colors.ENDC}")
            
            def validate_port(port_str):
                try:
                    port = int(port_str)
                    if 1024 <= port <= 65535:
                        return True, ""
                    return False, "ポート番号は1024-65535の範囲で指定してください"
                except ValueError:
                    return False, "数値を入力してください"
            
            for service in self.services_config.get("services", []):
                if service['name'] in self.selected_services:
                    default_port = str(service.get('port', 8000))
                    port = self._get_user_input(
                        f"  {service.get('display_name', service['name'])}のポート",
                        default_port,
                        validate_port
                    )
                    self.config[f"{service['name'].upper().replace('-', '_')}_SERVICE_PORT"] = port
    
    def step_preview_settings(self):
        """設定のプレビュー表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}設定プレビュー{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}選択されたサービス:{Colors.ENDC}")
        for service_name in self.selected_services:
            # サービス情報を取得
            service_info = None
            for s in self.services_config.get("services", []):
                if s['name'] == service_name:
                    service_info = s
                    break
            
            if service_name == "frontend":
                service_info = self.services_config.get("frontend", {})
            
            if service_info:
                display_name = service_info.get('display_name', service_name)
                port = service_info.get('port', 'N/A')
                print(f"  • {display_name} (ポート: {port})")
        
        print(f"\n{Colors.BOLD}環境変数:{Colors.ENDC}")
        for key, value in self.config.items():
            print(f"  {key}={value}")
        
        print()
        return self._get_yes_no_input("この設定で続行しますか？", True)
    
    def step_install_dependencies(self) -> bool:
        """ステップ4: 依存関係のインストール"""
        self._print_step_header(4, 5, "依存関係のインストール")
        
        installer = DependencyInstaller()
        
        # Python依存関係
        if not installer.install_python_dependencies():
            print(f"{Colors.FAIL}Python依存関係のインストールに失敗しました{Colors.ENDC}")
            if not self._get_yes_no_input("続行しますか？", False):
                return False
        
        # フロントエンド依存関係
        if "frontend" in self.selected_services:
            if not installer.install_frontend_dependencies():
                print(f"{Colors.WARNING}フロントエンド依存関係のインストールに問題がありました{Colors.ENDC}")
                if not self._get_yes_no_input("続行しますか？", True):
                    return False
        
        return True
    
    def step_generate_env_file(self) -> bool:
        """ステップ5: 環境変数ファイルの生成"""
        self._print_step_header(5, 5, "環境変数ファイルの生成")
        
        env_generator = EnvFileGenerator()
        
        # カスタム設定を反映
        if self.config:
            template = env_generator._get_template()
            
            # 設定値を上書き
            for key, value in self.config.items():
                # テンプレート内の該当行を置換
                import re
                pattern = f"^{key}=.*$"
                replacement = f"{key}={value}"
                template = re.sub(pattern, replacement, template, flags=re.MULTILINE)
            
            # カスタムテンプレートを設定
            env_generator.template = template
        
        return env_generator.generate()
    
    def run(self) -> bool:
        """ウィザードの実行"""
        try:
            # ウェルカム画面
            if not self.welcome_screen():
                return False
            
            # ステップ1: 環境チェック
            if not self.step_environment_check():
                return False
            
            # ステップ2: サービス選択
            self.step_select_services()
            
            # ステップ3: 設定の確認と編集
            self.step_configure_settings()
            
            # 設定プレビュー
            if not self.step_preview_settings():
                print(f"{Colors.WARNING}設定を中止しました{Colors.ENDC}")
                if self._get_yes_no_input("最初からやり直しますか？", True):
                    return self.run()  # 再帰的に再実行
                return False
            
            # ステップ4: 依存関係のインストール
            if not self.step_install_dependencies():
                return False
            
            # ステップ5: 環境変数ファイルの生成
            if not self.step_generate_env_file():
                return False
            
            # 完了メッセージ
            self._print_completion_message()
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}ウィザードが中断されました{Colors.ENDC}")
            return False
    
    def _print_completion_message(self):
        """完了メッセージの表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ セットアップウィザードが完了しました！{Colors.ENDC}\n")
        print(f"{Colors.BOLD}次のステップ:{Colors.ENDC}")
        print(f"  1. サービスを起動:")
        print(f"     {Colors.OKCYAN}python local_test_cli.py start{Colors.ENDC}")
        print(f"  2. ヘルスチェック:")
        print(f"     {Colors.OKCYAN}python local_test_cli.py health{Colors.ENDC}")
        print(f"  3. テスト実行:")
        print(f"     {Colors.OKCYAN}python local_test_cli.py test all{Colors.ENDC}")
        
        if "frontend" in self.selected_services:
            print(f"  4. ブラウザでアクセス:")
            print(f"     {Colors.OKCYAN}http://localhost:3000{Colors.ENDC}")
        
        print(f"\n{Colors.OKCYAN}詳細は README_LOCAL_TEST.md を参照してください{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


class LocalTestSetup:
    """ローカルテスト環境セットアップメインクラス"""
    
    def __init__(self):
        self.env_checker = EnvironmentChecker()
        self.dep_installer = DependencyInstaller()
        self.env_generator = EnvFileGenerator()
    
    def print_header(self):
        """ヘッダー表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🎮 治療的ゲーミフィケーションアプリ{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}   ローカルテスト環境セットアップ{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    def print_system_info(self):
        """システム情報の表示"""
        print(f"{Colors.OKCYAN}{Colors.BOLD}システム情報:{Colors.ENDC}")
        info = self.env_checker.get_system_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
    
    def run_setup(self) -> bool:
        """セットアップの実行"""
        self.print_header()
        self.print_system_info()
        
        # ステップ1: 環境チェック
        print(f"{Colors.BOLD}ステップ 1/3: 環境チェック{Colors.ENDC}")
        self.env_checker.run_all_checks()
        if not self.env_checker.print_results():
            return False
        
        # ステップ2: 依存関係インストール
        print(f"\n{Colors.BOLD}ステップ 2/3: 依存関係インストール{Colors.ENDC}")
        if not self.dep_installer.install_all():
            print(f"{Colors.FAIL}依存関係のインストールに失敗しました{Colors.ENDC}")
            return False
        
        # ステップ3: 環境変数ファイル生成
        print(f"\n{Colors.BOLD}ステップ 3/3: 環境変数ファイル生成{Colors.ENDC}")
        if not self.env_generator.generate():
            print(f"{Colors.FAIL}環境変数ファイルの生成に失敗しました{Colors.ENDC}")
            return False
        
        # 完了メッセージ
        self.print_completion_message()
        return True
    
    def print_completion_message(self):
        """完了メッセージの表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ セットアップが完了しました！{Colors.ENDC}\n")
        print(f"{Colors.BOLD}次のステップ:{Colors.ENDC}")
        print(f"  1. サービスを起動:")
        print(f"     {Colors.OKCYAN}python start_mvp_services.py{Colors.ENDC}")
        print(f"  2. フロントエンドを起動:")
        print(f"     {Colors.OKCYAN}cd frontend && npm run dev{Colors.ENDC}")
        print(f"  3. ブラウザでアクセス:")
        print(f"     {Colors.OKCYAN}http://localhost:3000{Colors.ENDC}")
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ローカルテスト環境セットアップスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python local_test_setup.py              # 自動セットアップ
  python local_test_setup.py --interactive # インタラクティブモード
  python local_test_setup.py -i           # インタラクティブモード (短縮形)
        """
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='インタラクティブセットアップウィザードを起動'
    )
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            # インタラクティブモード
            wizard = InteractiveSetupWizard()
            success = wizard.run()
        else:
            # 自動セットアップモード
            setup = LocalTestSetup()
            success = setup.run_setup()
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}セットアップが中断されました{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}予期しないエラーが発生しました: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
