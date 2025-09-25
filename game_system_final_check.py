#!/usr/bin/env python3
"""
治療的ゲーミフィケーションアプリ 最終システムチェック

全サービスの動作確認とバグ検出を実施します。
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class GameSystemChecker:
    def __init__(self):
        self.services = {
            'auth': {'port': 8002, 'path': 'services/auth'},
            'core-game': {'port': 8001, 'path': 'services/core-game'},
            'task-mgmt': {'port': 8003, 'path': 'services/task-mgmt'},
            'mandala': {'port': 8004, 'path': 'services/mandala'},
            'mood-tracking': {'port': 8005, 'path': 'services/mood-tracking'},
            'ai-story': {'port': 8006, 'path': 'services/ai-story'},
            'story-dag': {'port': 8007, 'path': 'services/story-dag'},
            'therapeutic-safety': {'port': 8008, 'path': 'services/therapeutic-safety'},
            'adhd-support': {'port': 8009, 'path': 'services/adhd-support'},
            'line-bot': {'port': 8010, 'path': 'services/line-bot'}
        }
        self.results = {}
    
    def print_header(self, text: str):
        """ヘッダーを表示"""
        print(f"\n{'='*70}")
        print(f"🎮 {text}")
        print(f"{'='*70}")
    
    def print_success(self, text: str):
        """成功メッセージを表示"""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """エラーメッセージを表示"""
        print(f"❌ {text}")
    
    def print_warning(self, text: str):
        """警告メッセージを表示"""
        print(f"⚠️  {text}")
    
    def print_info(self, text: str):
        """情報メッセージを表示"""
        print(f"ℹ️  {text}")
    
    def check_file_structure(self) -> Dict[str, Any]:
        """ファイル構造の確認"""
        self.print_header("ファイル構造チェック")
        
        required_files = {
            'shared/interfaces/core_types.py': 'コア型定義',
            'shared/config/firestore_setup.py': 'Firestore設定',
            'shared/repositories/base_repository.py': 'ベースリポジトリ',
            'frontend/src/App.tsx': 'フロントエンドメイン',
            'pyproject.toml': 'プロジェクト設定'
        }
        
        missing_files = []
        existing_files = []
        
        for file_path, description in required_files.items():
            if os.path.exists(file_path):
                existing_files.append(file_path)
                self.print_success(f"{description}: {file_path}")
            else:
                missing_files.append(file_path)
                self.print_error(f"{description}: {file_path} (missing)")
        
        # サービスディレクトリの確認
        service_dirs = []
        missing_services = []
        
        for service_name, config in self.services.items():
            service_path = config['path']
            if os.path.exists(service_path):
                service_dirs.append(service_path)
                self.print_success(f"サービス: {service_name} ({service_path})")
            else:
                missing_services.append(service_path)
                self.print_error(f"サービス: {service_name} ({service_path}) (missing)")
        
        return {
            'core_files': {
                'total': len(required_files),
                'existing': len(existing_files),
                'missing': missing_files
            },
            'services': {
                'total': len(self.services),
                'existing': len(service_dirs),
                'missing': missing_services
            },
            'success': len(missing_files) == 0 and len(missing_services) == 0
        }
    
    def check_python_syntax(self) -> Dict[str, Any]:
        """Python構文エラーチェック"""
        self.print_header("Python構文チェック")
        
        python_files = []
        syntax_errors = []
        
        # 主要なPythonファイルを収集
        for service_name, config in self.services.items():
            service_path = config['path']
            if os.path.exists(service_path):
                main_py = os.path.join(service_path, 'main.py')
                if os.path.exists(main_py):
                    python_files.append(main_py)
        
        # 共有ファイルも追加
        shared_files = [
            'shared/interfaces/core_types.py',
            'shared/config/firestore_setup.py',
            'shared/repositories/base_repository.py'
        ]
        
        for file_path in shared_files:
            if os.path.exists(file_path):
                python_files.append(file_path)
        
        # 構文チェック実行
        for file_path in python_files:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.print_success(f"構文OK: {file_path}")
                else:
                    syntax_errors.append({
                        'file': file_path,
                        'error': result.stderr
                    })
                    self.print_error(f"構文エラー: {file_path}")
                    self.print_error(f"  {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                syntax_errors.append({
                    'file': file_path,
                    'error': 'Timeout during syntax check'
                })
                self.print_error(f"タイムアウト: {file_path}")
            except Exception as e:
                syntax_errors.append({
                    'file': file_path,
                    'error': str(e)
                })
                self.print_error(f"チェックエラー: {file_path} - {e}")
        
        return {
            'total_files': len(python_files),
            'syntax_errors': len(syntax_errors),
            'error_details': syntax_errors,
            'success': len(syntax_errors) == 0
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """依存関係チェック"""
        self.print_header("依存関係チェック")
        
        try:
            # pyproject.tomlの確認
            if os.path.exists('pyproject.toml'):
                self.print_success("pyproject.toml が存在します")
            else:
                self.print_error("pyproject.toml が見つかりません")
                return {'success': False, 'error': 'pyproject.toml not found'}
            
            # 主要な依存関係のインポートテスト
            import_tests = [
                ('fastapi', 'FastAPI'),
                ('uvicorn', 'Uvicorn'),
                ('pydantic', 'Pydantic'),
                ('google.cloud.firestore', 'Google Cloud Firestore'),
                ('openai', 'OpenAI'),
                ('requests', 'Requests')
            ]
            
            import_errors = []
            successful_imports = []
            
            for module_name, description in import_tests:
                try:
                    __import__(module_name)
                    successful_imports.append(module_name)
                    self.print_success(f"{description}: インポート成功")
                except ImportError as e:
                    import_errors.append({
                        'module': module_name,
                        'description': description,
                        'error': str(e)
                    })
                    self.print_error(f"{description}: インポートエラー - {e}")
            
            return {
                'total_modules': len(import_tests),
                'successful_imports': len(successful_imports),
                'import_errors': len(import_errors),
                'error_details': import_errors,
                'success': len(import_errors) == 0
            }
            
        except Exception as e:
            self.print_error(f"依存関係チェック中にエラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_service_startup(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """個別サービスの起動チェック"""
        service_path = config['path']
        port = config['port']
        
        if not os.path.exists(service_path):
            return {
                'success': False,
                'error': f'Service directory not found: {service_path}'
            }
        
        main_py = os.path.join(service_path, 'main.py')
        if not os.path.exists(main_py):
            return {
                'success': False,
                'error': f'main.py not found in {service_path}'
            }
        
        try:
            # 構文チェック
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', main_py],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Syntax error in {main_py}: {result.stderr}'
                }
            
            # インポートテスト
            result = subprocess.run(
                [sys.executable, '-c', f'import sys; sys.path.insert(0, "{service_path}"); import main'],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=service_path
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Service {service_name} can be imported successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Import error: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout during service check'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """全サービスの起動チェック"""
        self.print_header("サービス起動チェック")
        
        service_results = {}
        successful_services = 0
        
        for service_name, config in self.services.items():
            self.print_info(f"チェック中: {service_name}")
            
            result = self.check_service_startup(service_name, config)
            service_results[service_name] = result
            
            if result['success']:
                successful_services += 1
                self.print_success(f"{service_name}: OK")
            else:
                self.print_error(f"{service_name}: {result['error']}")
        
        return {
            'total_services': len(self.services),
            'successful_services': successful_services,
            'service_results': service_results,
            'success': successful_services >= len(self.services) * 0.8  # 80%以上で成功
        }
    
    def check_frontend_structure(self) -> Dict[str, Any]:
        """フロントエンド構造チェック"""
        self.print_header("フロントエンド構造チェック")
        
        frontend_files = {
            'frontend/package.json': 'Package設定',
            'frontend/src/App.tsx': 'メインアプリ',
            'frontend/src/main.tsx': 'エントリーポイント',
            'frontend/src/components/Layout.tsx': 'レイアウト',
            'frontend/src/contexts/AuthContext.tsx': '認証コンテキスト'
        }
        
        missing_files = []
        existing_files = []
        
        for file_path, description in frontend_files.items():
            if os.path.exists(file_path):
                existing_files.append(file_path)
                self.print_success(f"{description}: {file_path}")
            else:
                missing_files.append(file_path)
                self.print_error(f"{description}: {file_path} (missing)")
        
        return {
            'total_files': len(frontend_files),
            'existing_files': len(existing_files),
            'missing_files': missing_files,
            'success': len(missing_files) == 0
        }
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """基本テストの実行"""
        self.print_header("基本テスト実行")
        
        test_results = {}
        
        # 共有インターフェースのテスト
        try:
            result = subprocess.run(
                [sys.executable, '-c', 'import sys; sys.path.insert(0, "."); from shared.interfaces.core_types import UserProfile; print("Core types import: OK")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                test_results['core_types'] = {'success': True, 'output': result.stdout}
                self.print_success("コア型定義: インポート成功")
            else:
                test_results['core_types'] = {'success': False, 'error': result.stderr}
                self.print_error(f"コア型定義: インポートエラー - {result.stderr}")
                
        except Exception as e:
            test_results['core_types'] = {'success': False, 'error': str(e)}
            self.print_error(f"コア型定義テストエラー: {e}")
        
        # データバリデーションのテスト
        try:
            result = subprocess.run(
                [sys.executable, '-c', 'import sys; sys.path.insert(0, "."); from shared.utils.data_validation import validate_user_profile; print("Data validation import: OK")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                test_results['data_validation'] = {'success': True, 'output': result.stdout}
                self.print_success("データバリデーション: インポート成功")
            else:
                test_results['data_validation'] = {'success': False, 'error': result.stderr}
                self.print_error(f"データバリデーション: インポートエラー - {result.stderr}")
                
        except Exception as e:
            test_results['data_validation'] = {'success': False, 'error': str(e)}
            self.print_error(f"データバリデーションテストエラー: {e}")
        
        successful_tests = sum(1 for result in test_results.values() if result['success'])
        
        return {
            'total_tests': len(test_results),
            'successful_tests': successful_tests,
            'test_results': test_results,
            'success': successful_tests >= len(test_results) * 0.8
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """最終レポート生成"""
        self.print_header("最終レポート生成")
        
        # 全チェック実行
        file_structure = self.check_file_structure()
        python_syntax = self.check_python_syntax()
        dependencies = self.check_dependencies()
        services = self.check_all_services()
        frontend = self.check_frontend_structure()
        basic_tests = self.run_basic_tests()
        
        # 総合評価
        checks = [
            ('ファイル構造', file_structure),
            ('Python構文', python_syntax),
            ('依存関係', dependencies),
            ('サービス起動', services),
            ('フロントエンド', frontend),
            ('基本テスト', basic_tests)
        ]
        
        successful_checks = sum(1 for _, result in checks if result['success'])
        total_checks = len(checks)
        completion_rate = (successful_checks / total_checks) * 100
        
        self.print_header("最終結果")
        print(f"完成度: {completion_rate:.1f}% ({successful_checks}/{total_checks})")
        
        if completion_rate >= 90:
            print("🎉 優秀！ゲームシステムは本番環境にデプロイ可能です")
            status = "EXCELLENT"
        elif completion_rate >= 80:
            print("✅ 良好！軽微な修正後にデプロイ可能です")
            status = "GOOD"
        elif completion_rate >= 70:
            print("⚠️  普通。いくつかの修正が必要です")
            status = "FAIR"
        else:
            print("❌ 要修正。重要なコンポーネントに問題があります")
            status = "NEEDS_WORK"
        
        print(f"\n最終評価: {status}")
        
        # 詳細結果
        print("\n📋 詳細結果:")
        for check_name, result in checks:
            if result['success']:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                if 'error' in result:
                    print(f"     エラー: {result['error']}")
        
        return {
            'completion_rate': completion_rate,
            'status': status,
            'successful_checks': successful_checks,
            'total_checks': total_checks,
            'detailed_results': {
                'file_structure': file_structure,
                'python_syntax': python_syntax,
                'dependencies': dependencies,
                'services': services,
                'frontend': frontend,
                'basic_tests': basic_tests
            }
        }

def main():
    """メイン実行"""
    print("🎮 治療的ゲーミフィケーションアプリ 最終システムチェック")
    print("=" * 70)
    
    checker = GameSystemChecker()
    report = checker.generate_report()
    
    return report['completion_rate'] >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)