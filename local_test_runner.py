#!/usr/bin/env python3
"""
ローカルテストランナー

このモジュールは、ローカル環境でのテスト実行を管理します。
- ユニットテストの実行
- 統合テストの実行
- E2Eテストの実行
- テスト結果の集約とレポート生成
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class TestResult:
    """テスト結果を表すデータクラス"""
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: List[str] = None
    duration: float = 0.0
    total: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        self.total = self.passed + self.failed + self.skipped


@dataclass
class TestSummary:
    """テストサマリーを表すデータクラス"""
    unit_tests: TestResult
    integration_tests: TestResult
    e2e_tests: TestResult
    total_coverage: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class LocalTestRunner:
    """ローカルテスト実行を管理するクラス"""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        初期化
        
        Args:
            workspace_root: ワークスペースのルートディレクトリ
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.test_results_dir = self.workspace_root / "test_results"
        self.test_results_dir.mkdir(exist_ok=True)
        
    def run_unit_tests(self, pattern: str = "test_*.py", 
                      path: Optional[str] = None,
                      verbose: bool = False) -> TestResult:
        """
        ユニットテストを実行
        
        Args:
            pattern: テストファイルのパターン
            path: テストを実行するパス（指定しない場合は全体）
            verbose: 詳細出力を有効にするか
            
        Returns:
            TestResult: テスト結果
        """
        print("🧪 ユニットテストを実行中...")
        print("=" * 60)
        
        start_time = time.time()
        
        # pytestコマンドの構築
        cmd = ["python", "-m", "pytest"]
        
        # パスの指定
        if path:
            cmd.append(path)
        else:
            # パターンでファイルを指定
            if pattern != "test_*.py":
                cmd.extend(["-k", pattern.replace("test_", "").replace(".py", "")])
        
        # 詳細出力
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # JSON出力用のオプション
        cmd.extend(["--tb=short", "--no-header"])
        
        try:
            # テスト実行
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分のタイムアウト
            )
            
            duration = time.time() - start_time
            
            # 結果のパース
            test_result = self._parse_pytest_output(result.stdout, result.stderr, duration)
            
            # 結果の表示
            self._print_test_result("ユニットテスト", test_result)
            
            # 結果の保存
            self._save_test_result("unit_tests", test_result)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print("❌ テストがタイムアウトしました")
            return TestResult(errors=["テストがタイムアウトしました"])
        except FileNotFoundError:
            print("❌ pytestが見つかりません。pip install pytestを実行してください")
            return TestResult(errors=["pytestが見つかりません"])
        except Exception as e:
            print(f"❌ テスト実行中にエラーが発生しました: {e}")
            return TestResult(errors=[str(e)])
    
    def run_integration_tests(self, setup_env: bool = True,
                             teardown_env: bool = True,
                             verbose: bool = False) -> TestResult:
        """
        統合テストを実行
        
        Args:
            setup_env: テスト環境のセットアップを行うか
            teardown_env: テスト環境のティアダウンを行うか
            verbose: 詳細出力を有効にするか
            
        Returns:
            TestResult: テスト結果
        """
        print("🔗 統合テストを実行中...")
        print("=" * 60)
        
        start_time = time.time()
        errors = []
        
        try:
            # テスト環境のセットアップ
            if setup_env:
                print("📦 テスト環境をセットアップ中...")
                if not self._setup_test_environment():
                    errors.append("テスト環境のセットアップに失敗しました")
                    return TestResult(errors=errors)
            
            # 統合テストの実行
            cmd = [
                "python", "-m", "pytest",
                "-m", "integration",  # integrationマーカーのテストのみ
                "--tb=short",
                "--no-header"
            ]
            
            if verbose:
                cmd.append("-v")
            else:
                cmd.append("-q")
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分のタイムアウト
            )
            
            duration = time.time() - start_time
            
            # 結果のパース
            test_result = self._parse_pytest_output(result.stdout, result.stderr, duration)
            
            # 結果の表示
            self._print_test_result("統合テスト", test_result)
            
            # 結果の保存
            self._save_test_result("integration_tests", test_result)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print("❌ 統合テストがタイムアウトしました")
            return TestResult(errors=["統合テストがタイムアウトしました"])
        except Exception as e:
            print(f"❌ 統合テスト実行中にエラーが発生しました: {e}")
            return TestResult(errors=[str(e)])
        finally:
            # テスト環境のティアダウン
            if teardown_env:
                print("🧹 テスト環境をクリーンアップ中...")
                self._teardown_test_environment()
    
    def run_e2e_tests(self, headless: bool = True,
                     screenshot: bool = True,
                     verbose: bool = False) -> TestResult:
        """
        E2Eテストを実行
        
        Args:
            headless: ヘッドレスモードで実行するか
            screenshot: スクリーンショットを撮るか
            verbose: 詳細出力を有効にするか
            
        Returns:
            TestResult: テスト結果
        """
        print("🌐 E2Eテストを実行中...")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # E2Eテストの実行
            cmd = [
                "python", "-m", "pytest",
                "-m", "e2e",  # e2eマーカーのテストのみ
                "--tb=short",
                "--no-header"
            ]
            
            if verbose:
                cmd.append("-v")
            else:
                cmd.append("-q")
            
            # ヘッドレスモードの設定
            env = {}
            if headless:
                env["HEADLESS"] = "true"
            if screenshot:
                env["SCREENSHOT"] = "true"
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=900,  # 15分のタイムアウト
                env={**subprocess.os.environ, **env}
            )
            
            duration = time.time() - start_time
            
            # 結果のパース
            test_result = self._parse_pytest_output(result.stdout, result.stderr, duration)
            
            # 結果の表示
            self._print_test_result("E2Eテスト", test_result)
            
            # 結果の保存
            self._save_test_result("e2e_tests", test_result)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print("❌ E2Eテストがタイムアウトしました")
            return TestResult(errors=["E2Eテストがタイムアウトしました"])
        except Exception as e:
            print(f"❌ E2Eテスト実行中にエラーが発生しました: {e}")
            return TestResult(errors=[str(e)])

    def run_all_tests(self, verbose: bool = False) -> TestSummary:
        """
        全テストを実行
        
        Args:
            verbose: 詳細出力を有効にするか
            
        Returns:
            TestSummary: テストサマリー
        """
        print("🚀 全テストを実行中...")
        print("=" * 60)
        
        # ユニットテスト
        unit_result = self.run_unit_tests(verbose=verbose)
        print()
        
        # 統合テスト
        integration_result = self.run_integration_tests(verbose=verbose)
        print()
        
        # E2Eテスト
        e2e_result = self.run_e2e_tests(verbose=verbose)
        print()
        
        # カバレッジの計算
        coverage = self._calculate_coverage()
        
        # サマリーの作成
        summary = TestSummary(
            unit_tests=unit_result,
            integration_tests=integration_result,
            e2e_tests=e2e_result,
            total_coverage=coverage
        )
        
        # サマリーの表示
        self._print_test_summary(summary)
        
        # サマリーの保存
        self._save_test_summary(summary)
        
        return summary
    
    def generate_coverage_report(self, output_dir: Optional[str] = None,
                                html: bool = True) -> bool:
        """
        カバレッジレポートを生成
        
        Args:
            output_dir: 出力ディレクトリ
            html: HTMLレポートを生成するか
            
        Returns:
            bool: 成功したかどうか
        """
        print("📊 カバレッジレポートを生成中...")
        
        if output_dir is None:
            output_dir = str(self.test_results_dir / "coverage")
        
        try:
            # カバレッジ付きでテスト実行
            cmd = [
                "python", "-m", "pytest",
                "--cov=services",
                "--cov=shared",
                "--cov-report=term",
            ]
            
            if html:
                cmd.append(f"--cov-report=html:{output_dir}")
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0 or "passed" in result.stdout.lower():
                print(f"✅ カバレッジレポートを生成しました: {output_dir}")
                if html:
                    print(f"   HTMLレポート: {output_dir}/index.html")
                return True
            else:
                print("❌ カバレッジレポートの生成に失敗しました")
                if result.stderr:
                    print(f"エラー詳細: {result.stderr}")
                if result.stdout:
                    print(f"出力: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ カバレッジレポート生成がタイムアウトしました")
            return False
        except FileNotFoundError:
            print("❌ pytest-covが見つかりません。pip install pytest-covを実行してください")
            return False
        except Exception as e:
            print(f"❌ カバレッジレポート生成中にエラーが発生しました: {e}")
            return False
    
    def _parse_pytest_output(self, stdout: str, stderr: str, 
                            duration: float) -> TestResult:
        """
        pytestの出力をパースしてTestResultを作成
        
        Args:
            stdout: 標準出力
            stderr: 標準エラー出力
            duration: 実行時間
            
        Returns:
            TestResult: テスト結果
        """
        passed = 0
        failed = 0
        skipped = 0
        errors = []
        
        # 出力から結果を抽出
        output = stdout + stderr
        
        # "X passed" のパターンを検索
        passed_match = re.search(r'(\d+) passed', output)
        if passed_match:
            passed = int(passed_match.group(1))
        
        # "X failed" のパターンを検索
        failed_match = re.search(r'(\d+) failed', output)
        if failed_match:
            failed = int(failed_match.group(1))
        
        # "X skipped" のパターンを検索
        skipped_match = re.search(r'(\d+) skipped', output)
        if skipped_match:
            skipped = int(skipped_match.group(1))
        
        # エラーメッセージの抽出
        if "FAILED" in output:
            # FAILEDの行を抽出
            for line in output.split('\n'):
                if "FAILED" in line or "ERROR" in line:
                    errors.append(line.strip())
        
        # エラー出力がある場合
        if stderr and "error" in stderr.lower():
            errors.append(stderr.strip())
        
        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors[:10],  # 最初の10個のエラーのみ
            duration=duration
        )
    
    def _setup_test_environment(self) -> bool:
        """
        テスト環境をセットアップ
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            # モックデータベースの初期化
            from mock_database import MockFirestoreClient
            
            mock_db = MockFirestoreClient(persist_data=False)
            
            # サンプルデータのロード
            sample_data_file = self.workspace_root / "test_data" / "sample_data.json"
            if sample_data_file.exists():
                mock_db.load_sample_data(str(sample_data_file))
                print("✅ サンプルデータをロードしました")
            
            return True
            
        except Exception as e:
            print(f"❌ テスト環境のセットアップに失敗しました: {e}")
            return False
    
    def _teardown_test_environment(self) -> bool:
        """
        テスト環境をティアダウン
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            # モックデータベースのクリーンアップ
            from mock_database import MockFirestoreClient
            
            mock_db = MockFirestoreClient()
            mock_db.clear_all_data()
            
            print("✅ テスト環境をクリーンアップしました")
            return True
            
        except Exception as e:
            print(f"⚠️  テスト環境のクリーンアップに失敗しました: {e}")
            return False
    
    def _calculate_coverage(self) -> float:
        """
        コードカバレッジを計算
        
        Returns:
            float: カバレッジ率（0-100）
        """
        try:
            # カバレッジファイルの確認
            coverage_file = self.workspace_root / ".coverage"
            if not coverage_file.exists():
                return 0.0
            
            # カバレッジの取得
            cmd = ["python", "-m", "coverage", "report", "--format=total"]
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 出力から数値を抽出
                coverage_match = re.search(r'(\d+)%', result.stdout)
                if coverage_match:
                    return float(coverage_match.group(1))
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _print_test_result(self, test_type: str, result: TestResult):
        """
        テスト結果を表示
        
        Args:
            test_type: テストタイプ
            result: テスト結果
        """
        print(f"\n📋 {test_type}結果:")
        print(f"   ✅ 成功: {result.passed}")
        print(f"   ❌ 失敗: {result.failed}")
        print(f"   ⏭️  スキップ: {result.skipped}")
        print(f"   📊 合計: {result.total}")
        print(f"   ⏱️  実行時間: {result.duration:.2f}秒")
        
        if result.errors:
            print(f"\n   ⚠️  エラー詳細:")
            for error in result.errors[:5]:  # 最初の5個のみ表示
                print(f"      - {error}")
            if len(result.errors) > 5:
                print(f"      ... 他 {len(result.errors) - 5} 件のエラー")
    
    def _print_test_summary(self, summary: TestSummary):
        """
        テストサマリーを表示
        
        Args:
            summary: テストサマリー
        """
        print("\n" + "=" * 60)
        print("📊 テスト実行サマリー")
        print("=" * 60)
        
        total_passed = (summary.unit_tests.passed + 
                       summary.integration_tests.passed + 
                       summary.e2e_tests.passed)
        total_failed = (summary.unit_tests.failed + 
                       summary.integration_tests.failed + 
                       summary.e2e_tests.failed)
        total_tests = (summary.unit_tests.total + 
                      summary.integration_tests.total + 
                      summary.e2e_tests.total)
        
        print(f"\n全体:")
        print(f"  ✅ 成功: {total_passed}/{total_tests}")
        print(f"  ❌ 失敗: {total_failed}/{total_tests}")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"  📈 成功率: {success_rate:.1f}%")
        
        if summary.total_coverage > 0:
            print(f"  📊 カバレッジ: {summary.total_coverage:.1f}%")
        
        print(f"\n実行時刻: {summary.timestamp}")
        
        # 結果の判定
        if total_failed == 0:
            print("\n🎉 全てのテストが成功しました！")
        else:
            print(f"\n⚠️  {total_failed}件のテストが失敗しました")
    
    def _save_test_result(self, test_type: str, result: TestResult):
        """
        テスト結果をファイルに保存
        
        Args:
            test_type: テストタイプ
            result: テスト結果
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_type}_{timestamp}.json"
            filepath = self.test_results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, ensure_ascii=False)
            
            print(f"   💾 結果を保存しました: {filepath}")
            
        except Exception as e:
            print(f"   ⚠️  結果の保存に失敗しました: {e}")
    
    def _save_test_summary(self, summary: TestSummary):
        """
        テストサマリーをファイルに保存
        
        Args:
            summary: テストサマリー
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_summary_{timestamp}.json"
            filepath = self.test_results_dir / filename
            
            # TestSummaryをdictに変換
            summary_dict = {
                'unit_tests': asdict(summary.unit_tests),
                'integration_tests': asdict(summary.integration_tests),
                'e2e_tests': asdict(summary.e2e_tests),
                'total_coverage': summary.total_coverage,
                'timestamp': summary.timestamp
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_dict, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 サマリーを保存しました: {filepath}")
            
        except Exception as e:
            print(f"⚠️  サマリーの保存に失敗しました: {e}")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ローカルテストランナー",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'test_type',
        choices=['unit', 'integration', 'e2e', 'all', 'coverage'],
        help='実行するテストタイプ'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細出力を有効にする'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        default='test_*.py',
        help='ユニットテストのパターン（デフォルト: test_*.py）'
    )
    
    parser.add_argument(
        '--path',
        help='テストを実行するパス'
    )
    
    parser.add_argument(
        '--no-setup',
        action='store_true',
        help='テスト環境のセットアップをスキップ'
    )
    
    parser.add_argument(
        '--no-teardown',
        action='store_true',
        help='テスト環境のティアダウンをスキップ'
    )
    
    args = parser.parse_args()
    
    # テストランナーの作成
    runner = LocalTestRunner()
    
    # テストの実行
    if args.test_type == 'unit':
        result = runner.run_unit_tests(
            pattern=args.pattern,
            path=args.path,
            verbose=args.verbose
        )
        sys.exit(0 if result.failed == 0 else 1)
        
    elif args.test_type == 'integration':
        result = runner.run_integration_tests(
            setup_env=not args.no_setup,
            teardown_env=not args.no_teardown,
            verbose=args.verbose
        )
        sys.exit(0 if result.failed == 0 else 1)
        
    elif args.test_type == 'e2e':
        result = runner.run_e2e_tests(
            verbose=args.verbose
        )
        sys.exit(0 if result.failed == 0 else 1)
        
    elif args.test_type == 'all':
        summary = runner.run_all_tests(verbose=args.verbose)
        total_failed = (summary.unit_tests.failed + 
                       summary.integration_tests.failed + 
                       summary.e2e_tests.failed)
        sys.exit(0 if total_failed == 0 else 1)
        
    elif args.test_type == 'coverage':
        success = runner.generate_coverage_report()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
