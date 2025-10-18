#!/usr/bin/env python3
"""
ローカルテストランナーのテスト

このファイルは、local_test_runner.pyの機能をテストします。
"""

import pytest
import json
from pathlib import Path
from local_test_runner import LocalTestRunner, TestResult, TestSummary


class TestLocalTestRunner:
    """LocalTestRunnerのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.runner = LocalTestRunner()
    
    def test_runner_initialization(self):
        """テストランナーの初期化をテスト"""
        assert self.runner is not None
        assert self.runner.workspace_root.exists()
        assert self.runner.test_results_dir.exists()
        print("✅ テストランナーの初期化が成功しました")
    
    def test_test_result_creation(self):
        """TestResultの作成をテスト"""
        result = TestResult(
            passed=10,
            failed=2,
            skipped=1,
            errors=["エラー1", "エラー2"],
            duration=5.5
        )
        
        assert result.passed == 10
        assert result.failed == 2
        assert result.skipped == 1
        assert result.total == 13
        assert result.duration == 5.5
        assert len(result.errors) == 2
        print("✅ TestResultの作成が成功しました")
    
    def test_test_summary_creation(self):
        """TestSummaryの作成をテスト"""
        unit_result = TestResult(passed=10, failed=0, skipped=0)
        integration_result = TestResult(passed=5, failed=1, skipped=0)
        e2e_result = TestResult(passed=3, failed=0, skipped=1)
        
        summary = TestSummary(
            unit_tests=unit_result,
            integration_tests=integration_result,
            e2e_tests=e2e_result,
            total_coverage=85.5
        )
        
        assert summary.unit_tests.passed == 10
        assert summary.integration_tests.failed == 1
        assert summary.e2e_tests.skipped == 1
        assert summary.total_coverage == 85.5
        assert summary.timestamp != ""
        print("✅ TestSummaryの作成が成功しました")
    
    def test_parse_pytest_output(self):
        """pytestの出力パースをテスト"""
        stdout = """
        test_example.py::test_one PASSED
        test_example.py::test_two FAILED
        test_example.py::test_three SKIPPED
        
        ========== 5 passed, 2 failed, 1 skipped in 3.45s ==========
        """
        
        result = self.runner._parse_pytest_output(stdout, "", 3.45)
        
        assert result.passed == 5
        assert result.failed == 2
        assert result.skipped == 1
        assert result.duration == 3.45
        print("✅ pytestの出力パースが成功しました")
    
    def test_save_test_result(self):
        """テスト結果の保存をテスト"""
        result = TestResult(
            passed=10,
            failed=0,
            skipped=1,
            duration=5.0
        )
        
        self.runner._save_test_result("test_type", result)
        
        # 保存されたファイルを確認
        result_files = list(self.runner.test_results_dir.glob("test_type_*.json"))
        assert len(result_files) > 0
        
        # ファイルの内容を確認
        with open(result_files[-1], 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            assert saved_data['passed'] == 10
            assert saved_data['failed'] == 0
            assert saved_data['skipped'] == 1
        
        print("✅ テスト結果の保存が成功しました")
    
    def test_print_test_result(self):
        """テスト結果の表示をテスト"""
        result = TestResult(
            passed=10,
            failed=2,
            skipped=1,
            errors=["エラー1"],
            duration=5.5
        )
        
        # 例外が発生しないことを確認
        try:
            self.runner._print_test_result("ユニットテスト", result)
            print("✅ テスト結果の表示が成功しました")
        except Exception as e:
            pytest.fail(f"テスト結果の表示に失敗しました: {e}")
    
    def test_print_test_summary(self):
        """テストサマリーの表示をテスト"""
        summary = TestSummary(
            unit_tests=TestResult(passed=10, failed=0, skipped=0),
            integration_tests=TestResult(passed=5, failed=1, skipped=0),
            e2e_tests=TestResult(passed=3, failed=0, skipped=1),
            total_coverage=85.5
        )
        
        # 例外が発生しないことを確認
        try:
            self.runner._print_test_summary(summary)
            print("✅ テストサマリーの表示が成功しました")
        except Exception as e:
            pytest.fail(f"テストサマリーの表示に失敗しました: {e}")
    
    def test_calculate_coverage(self):
        """カバレッジ計算をテスト"""
        coverage = self.runner._calculate_coverage()
        
        # カバレッジは0以上100以下
        assert 0 <= coverage <= 100
        print(f"✅ カバレッジ計算が成功しました: {coverage}%")


def test_basic_functionality():
    """基本機能のテスト"""
    print("\n" + "=" * 60)
    print("🧪 ローカルテストランナーの基本機能テスト")
    print("=" * 60)
    
    # テストランナーの作成
    runner = LocalTestRunner()
    print("✅ テストランナーを作成しました")
    
    # TestResultの作成
    result = TestResult(passed=5, failed=0, skipped=0, duration=2.5)
    assert result.total == 5
    print("✅ TestResultを作成しました")
    
    # TestSummaryの作成
    summary = TestSummary(
        unit_tests=result,
        integration_tests=result,
        e2e_tests=result
    )
    assert summary.timestamp != ""
    print("✅ TestSummaryを作成しました")
    
    print("\n🎉 全ての基本機能テストが成功しました！")


def test_integration_with_mock_database():
    """モックデータベースとの統合テスト"""
    print("\n" + "=" * 60)
    print("🔗 モックデータベースとの統合テスト")
    print("=" * 60)
    
    runner = LocalTestRunner()
    
    # テスト環境のセットアップ
    try:
        success = runner._setup_test_environment()
        if success:
            print("✅ テスト環境のセットアップが成功しました")
        else:
            print("⚠️  テスト環境のセットアップをスキップしました（モックDBが利用できない可能性）")
    except Exception as e:
        print(f"⚠️  テスト環境のセットアップ中にエラー: {e}")
    
    # テスト環境のティアダウン
    try:
        success = runner._teardown_test_environment()
        if success:
            print("✅ テスト環境のティアダウンが成功しました")
        else:
            print("⚠️  テスト環境のティアダウンをスキップしました")
    except Exception as e:
        print(f"⚠️  テスト環境のティアダウン中にエラー: {e}")


def test_result_file_operations():
    """結果ファイル操作のテスト"""
    print("\n" + "=" * 60)
    print("💾 結果ファイル操作のテスト")
    print("=" * 60)
    
    runner = LocalTestRunner()
    
    # テスト結果の保存
    result = TestResult(
        passed=15,
        failed=2,
        skipped=3,
        errors=["テストエラー1", "テストエラー2"],
        duration=10.5
    )
    
    runner._save_test_result("unit_tests", result)
    print("✅ ユニットテスト結果を保存しました")
    
    # サマリーの保存
    summary = TestSummary(
        unit_tests=result,
        integration_tests=TestResult(passed=8, failed=1, skipped=0),
        e2e_tests=TestResult(passed=5, failed=0, skipped=1),
        total_coverage=78.5
    )
    
    runner._save_test_summary(summary)
    print("✅ テストサマリーを保存しました")
    
    # 保存されたファイルの確認
    result_files = list(runner.test_results_dir.glob("*.json"))
    print(f"✅ {len(result_files)}個の結果ファイルが保存されています")


if __name__ == '__main__':
    print("🚀 ローカルテストランナーのテストを開始します\n")
    
    # 基本機能のテスト
    test_basic_functionality()
    
    # モックデータベースとの統合テスト
    test_integration_with_mock_database()
    
    # 結果ファイル操作のテスト
    test_result_file_operations()
    
    print("\n" + "=" * 60)
    print("🎉 全てのテストが完了しました！")
    print("=" * 60)
    
    # pytestを使用したテストも実行
    print("\n📋 pytestを使用した詳細テストを実行中...")
    pytest.main([__file__, '-v'])
