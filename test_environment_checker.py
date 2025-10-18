#!/usr/bin/env python3
"""
環境チェック機能のテストスクリプト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_test_setup import EnvironmentChecker, Colors


def test_environment_checker():
    """環境チェッカーのテスト"""
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}環境チェック機能テスト{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    checker = EnvironmentChecker()
    
    # 個別チェックのテスト
    print(f"{Colors.BOLD}個別チェックのテスト:{Colors.ENDC}\n")
    
    tests = [
        ("Pythonバージョン", checker.check_python_version),
        ("Node.jsバージョン", checker.check_node_version),
        ("npm", checker.check_npm),
        ("pip", checker.check_pip),
        ("CPU", checker.check_cpu),
        ("メモリ", checker.check_memory),
        ("ディスク容量", checker.check_disk_space),
        ("必要ファイル", checker.check_required_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
            print(f"{status} {test_name}: {message}")
            results.append((test_name, passed))
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}: エラー - {str(e)}")
            results.append((test_name, False))
    
    # システム情報の取得テスト
    print(f"\n{Colors.BOLD}システム情報の取得テスト:{Colors.ENDC}\n")
    try:
        system_info = checker.get_system_info()
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        print(f"{Colors.OKGREEN}✓ システム情報の取得成功{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ システム情報の取得失敗: {str(e)}{Colors.ENDC}")
    
    # 全チェックの実行テスト
    print(f"\n{Colors.BOLD}全チェックの実行テスト:{Colors.ENDC}\n")
    try:
        all_checks = checker.run_all_checks()
        print(f"{Colors.OKGREEN}✓ 全チェックの実行成功 ({len(all_checks)}項目){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ 全チェックの実行失敗: {str(e)}{Colors.ENDC}")
    
    # 結果の表示テスト
    print(f"\n{Colors.BOLD}結果表示のテスト:{Colors.ENDC}")
    try:
        checker.print_results()
        print(f"{Colors.OKGREEN}✓ 結果表示成功{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ 結果表示失敗: {str(e)}{Colors.ENDC}")
    
    # テスト結果のサマリー
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}テスト結果サマリー{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"合格: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ すべてのテストに合格しました！{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.WARNING}⚠️  一部のテストに失敗しました{Colors.ENDC}\n")
        return False


if __name__ == "__main__":
    try:
        success = test_environment_checker()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n{Colors.FAIL}テスト実行エラー: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
