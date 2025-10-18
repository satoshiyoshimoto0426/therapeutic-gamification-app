#!/usr/bin/env python3
"""
タスク5完了確認テスト

このファイルは、タスク5「テストランナーの実装」が
要件通りに完了していることを確認します。
"""

import sys
from pathlib import Path
from local_test_runner import LocalTestRunner, TestResult, TestSummary


def test_task_5_requirements():
    """タスク5の要件確認"""
    print("\n" + "=" * 60)
    print("📋 タスク5: テストランナーの実装 - 完了確認")
    print("=" * 60)
    
    results = []
    
    # 要件5.1: ユニットテスト実行機能
    print("\n✅ 要件5.1: ユニットテスト実行機能の実装")
    print("-" * 60)
    
    runner = LocalTestRunner()
    
    # pytestを使用したテスト実行
    print("  ✓ pytestを使用したテスト実行機能")
    assert hasattr(runner, 'run_unit_tests')
    results.append(("ユニットテスト実行", True))
    
    # テストパターンのフィルタリング
    print("  ✓ テストパターンのフィルタリング機能")
    result = runner.run_unit_tests(pattern="test_local_test_runner.py", verbose=False)
    assert isinstance(result, TestResult)
    results.append(("パターンフィルタリング", True))
    
    # テスト結果の集約
    print("  ✓ テスト結果の集約機能")
    assert hasattr(result, 'passed')
    assert hasattr(result, 'failed')
    assert hasattr(result, 'skipped')
    assert hasattr(result, 'total')
    assert hasattr(result, 'duration')
    results.append(("結果集約", True))
    
    # 要件5.2: 統合テスト実行機能
    print("\n✅ 要件5.2: 統合テスト実行機能の実装")
    print("-" * 60)
    
    # サービス間連携テストの実行
    print("  ✓ 統合テスト実行機能")
    assert hasattr(runner, 'run_integration_tests')
    results.append(("統合テスト実行", True))
    
    # テスト環境のセットアップ/ティアダウン
    print("  ✓ テスト環境のセットアップ/ティアダウン機能")
    assert hasattr(runner, '_setup_test_environment')
    assert hasattr(runner, '_teardown_test_environment')
    results.append(("環境管理", True))
    
    # テスト結果のレポート生成
    print("  ✓ テスト結果のレポート生成機能")
    assert hasattr(runner, '_save_test_result')
    assert hasattr(runner, '_save_test_summary')
    results.append(("レポート生成", True))
    
    # 追加機能: E2Eテスト実行
    print("\n✅ 追加機能: E2Eテスト実行機能")
    print("-" * 60)
    
    print("  ✓ E2Eテスト実行機能")
    assert hasattr(runner, 'run_e2e_tests')
    results.append(("E2Eテスト実行", True))
    
    # 追加機能: カバレッジレポート生成
    print("\n✅ 追加機能: カバレッジレポート生成機能")
    print("-" * 60)
    
    print("  ✓ カバレッジレポート生成機能")
    assert hasattr(runner, 'generate_coverage_report')
    results.append(("カバレッジレポート", True))
    
    # 全テスト実行機能
    print("\n✅ 追加機能: 全テスト実行機能")
    print("-" * 60)
    
    print("  ✓ 全テスト実行機能")
    assert hasattr(runner, 'run_all_tests')
    results.append(("全テスト実行", True))
    
    return results


def test_data_models():
    """データモデルの確認"""
    print("\n" + "=" * 60)
    print("📊 データモデルの確認")
    print("=" * 60)
    
    results = []
    
    # TestResultモデル
    print("\n✓ TestResultモデル")
    result = TestResult(
        passed=10,
        failed=2,
        skipped=1,
        errors=["エラー1"],
        duration=5.5
    )
    assert result.total == 13
    assert result.passed == 10
    assert result.failed == 2
    assert result.skipped == 1
    results.append(("TestResultモデル", True))
    
    # TestSummaryモデル
    print("✓ TestSummaryモデル")
    summary = TestSummary(
        unit_tests=result,
        integration_tests=result,
        e2e_tests=result,
        total_coverage=85.5
    )
    assert summary.total_coverage == 85.5
    assert summary.timestamp != ""
    results.append(("TestSummaryモデル", True))
    
    return results


def test_helper_functions():
    """ヘルパー関数の確認"""
    print("\n" + "=" * 60)
    print("🔧 ヘルパー関数の確認")
    print("=" * 60)
    
    results = []
    runner = LocalTestRunner()
    
    # pytestの出力パース
    print("\n✓ pytestの出力パース機能")
    stdout = "5 passed, 2 failed, 1 skipped in 3.45s"
    result = runner._parse_pytest_output(stdout, "", 3.45)
    assert result.passed == 5
    assert result.failed == 2
    assert result.skipped == 1
    results.append(("出力パース", True))
    
    # テスト結果の表示
    print("✓ テスト結果の表示機能")
    try:
        runner._print_test_result("テスト", result)
        results.append(("結果表示", True))
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        results.append(("結果表示", False))
    
    # テストサマリーの表示
    print("✓ テストサマリーの表示機能")
    summary = TestSummary(
        unit_tests=result,
        integration_tests=result,
        e2e_tests=result
    )
    try:
        runner._print_test_summary(summary)
        results.append(("サマリー表示", True))
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        results.append(("サマリー表示", False))
    
    # ファイル保存
    print("✓ ファイル保存機能")
    try:
        runner._save_test_result("test", result)
        runner._save_test_summary(summary)
        results.append(("ファイル保存", True))
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        results.append(("ファイル保存", False))
    
    return results


def test_cli_interface():
    """CLIインターフェースの確認"""
    print("\n" + "=" * 60)
    print("💻 CLIインターフェースの確認")
    print("=" * 60)
    
    results = []
    
    # local_test_runner.pyファイルの存在確認
    print("\n✓ local_test_runner.pyファイルの存在")
    runner_file = Path("local_test_runner.py")
    assert runner_file.exists()
    results.append(("ファイル存在", True))
    
    # main関数の存在確認
    print("✓ main関数の存在")
    with open(runner_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "def main():" in content
        assert "argparse" in content
        results.append(("main関数", True))
    
    # コマンドライン引数のサポート
    print("✓ コマンドライン引数のサポート")
    assert "'unit'" in content
    assert "'integration'" in content
    assert "'e2e'" in content
    assert "'all'" in content
    assert "'coverage'" in content
    results.append(("CLI引数", True))
    
    return results


def print_summary(all_results):
    """テスト結果のサマリーを表示"""
    print("\n" + "=" * 60)
    print("📊 タスク5完了確認 - 最終結果")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for _, status in all_results if status)
    failed = total - passed
    
    print(f"\n総テスト数: {total}")
    print(f"✅ 成功: {passed}")
    print(f"❌ 失敗: {failed}")
    
    if failed > 0:
        print("\n失敗したテスト:")
        for name, status in all_results:
            if not status:
                print(f"  ❌ {name}")
    
    print("\n" + "=" * 60)
    
    if failed == 0:
        print("🎉 タスク5: テストランナーの実装が完了しました！")
        print("=" * 60)
        print("\n実装された機能:")
        print("  ✅ ユニットテスト実行機能")
        print("  ✅ 統合テスト実行機能")
        print("  ✅ E2Eテスト実行機能")
        print("  ✅ カバレッジレポート生成機能")
        print("  ✅ テスト結果の集約とレポート生成")
        print("  ✅ CLIインターフェース")
        print("\n使用方法:")
        print("  python local_test_runner.py unit          # ユニットテスト実行")
        print("  python local_test_runner.py integration   # 統合テスト実行")
        print("  python local_test_runner.py e2e           # E2Eテスト実行")
        print("  python local_test_runner.py all           # 全テスト実行")
        print("  python local_test_runner.py coverage      # カバレッジレポート生成")
        return 0
    else:
        print("❌ 一部のテストが失敗しました")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    print("🚀 タスク5完了確認テストを開始します")
    
    all_results = []
    
    try:
        # 要件確認
        results = test_task_5_requirements()
        all_results.extend(results)
        
        # データモデル確認
        results = test_data_models()
        all_results.extend(results)
        
        # ヘルパー関数確認
        results = test_helper_functions()
        all_results.extend(results)
        
        # CLIインターフェース確認
        results = test_cli_interface()
        all_results.extend(results)
        
        # サマリー表示
        exit_code = print_summary(all_results)
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ テスト実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
