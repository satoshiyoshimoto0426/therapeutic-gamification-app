#!/usr/bin/env python3
"""
ローカルテストCLIのテスト

タスク6の実装を検証するテストスクリプト
"""

import subprocess
import sys
import json
from pathlib import Path


class Colors:
    """ターミナルカラーコード"""
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def run_command(cmd: list, check_output: bool = True) -> tuple:
    """
    コマンドを実行して結果を返す
    
    Args:
        cmd: 実行するコマンド
        check_output: 出力をチェックするか
        
    Returns:
        (success, output, error)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "コマンドがタイムアウトしました"
    except Exception as e:
        return False, "", str(e)


def test_cli_help():
    """ヘルプメッセージのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: CLIヘルプメッセージ{Colors.ENDC}")
    
    success, output, error = run_command(["python", "local_test_cli.py", "--help"])
    
    if success and "usage:" in output.lower():
        print(f"{Colors.OKGREEN}✓ ヘルプメッセージが表示されました{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}✗ ヘルプメッセージの表示に失敗しました{Colors.ENDC}")
        if error:
            print(f"  エラー: {error}")
        return False


def test_setup_command():
    """setupコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: setupコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "setup", "--help"])
    
    if success and "setup" in output.lower():
        print(f"{Colors.OKGREEN}✓ setupコマンドのヘルプが表示されました{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}✗ setupコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_start_command():
    """startコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: startコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "start", "--help"])
    
    if success and "start" in output.lower():
        print(f"{Colors.OKGREEN}✓ startコマンドのヘルプが表示されました{Colors.ENDC}")
        
        # オプションの確認
        has_service_option = "--service" in output or "-s" in output
        has_all_option = "--all" in output or "-a" in output
        
        if has_service_option and has_all_option:
            print(f"{Colors.OKGREEN}✓ 必要なオプションが定義されています{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  一部のオプションが不足しています{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}✗ startコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_stop_command():
    """stopコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: stopコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "stop", "--help"])
    
    if success and "stop" in output.lower():
        print(f"{Colors.OKGREEN}✓ stopコマンドのヘルプが表示されました{Colors.ENDC}")
        
        # オプションの確認
        has_service_option = "--service" in output or "-s" in output
        has_force_option = "--force" in output or "-f" in output
        
        if has_service_option and has_force_option:
            print(f"{Colors.OKGREEN}✓ 必要なオプションが定義されています{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  一部のオプションが不足しています{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}✗ stopコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_health_command():
    """healthコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: healthコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "health", "--help"])
    
    if success and "health" in output.lower():
        print(f"{Colors.OKGREEN}✓ healthコマンドのヘルプが表示されました{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}✗ healthコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_test_command():
    """testコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: testコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "test", "--help"])
    
    if success and "test" in output.lower():
        print(f"{Colors.OKGREEN}✓ testコマンドのヘルプが表示されました{Colors.ENDC}")
        
        # テストタイプの確認
        has_unit = "unit" in output
        has_integration = "integration" in output
        has_e2e = "e2e" in output
        has_all = "all" in output
        
        if has_unit and has_integration and has_e2e and has_all:
            print(f"{Colors.OKGREEN}✓ 全てのテストタイプが定義されています{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  一部のテストタイプが不足しています{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}✗ testコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_logs_command():
    """logsコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: logsコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "logs", "--help"])
    
    if success and "logs" in output.lower():
        print(f"{Colors.OKGREEN}✓ logsコマンドのヘルプが表示されました{Colors.ENDC}")
        
        # オプションの確認
        has_service = "--service" in output or "-s" in output
        has_lines = "--lines" in output or "-n" in output
        has_level = "--level" in output or "-l" in output
        has_follow = "--follow" in output or "-f" in output
        
        if has_service and has_lines and has_level and has_follow:
            print(f"{Colors.OKGREEN}✓ 必要なオプションが定義されています{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  一部のオプションが不足しています{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}✗ logsコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_cleanup_command():
    """cleanupコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: cleanupコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "cleanup", "--help"])
    
    if success and "cleanup" in output.lower():
        print(f"{Colors.OKGREEN}✓ cleanupコマンドのヘルプが表示されました{Colors.ENDC}")
        
        # オプションの確認
        has_keep_services = "--keep-services" in output
        has_keep_data = "--keep-data" in output
        has_save_logs = "--save-logs" in output
        
        if has_keep_services and has_keep_data and has_save_logs:
            print(f"{Colors.OKGREEN}✓ 必要なオプションが定義されています{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  一部のオプションが不足しています{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}✗ cleanupコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_status_command():
    """statusコマンドのテスト"""
    print(f"\n{Colors.OKCYAN}テスト: statusコマンド{Colors.ENDC}")
    
    # ヘルプの確認
    success, output, error = run_command(["python", "local_test_cli.py", "status", "--help"])
    
    if success and "status" in output.lower():
        print(f"{Colors.OKGREEN}✓ statusコマンドのヘルプが表示されました{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}✗ statusコマンドのヘルプ表示に失敗しました{Colors.ENDC}")
        return False


def test_all_commands_available():
    """全コマンドが利用可能かテスト"""
    print(f"\n{Colors.OKCYAN}テスト: 全コマンドの利用可能性{Colors.ENDC}")
    
    success, output, error = run_command(["python", "local_test_cli.py", "--help"])
    
    if not success:
        print(f"{Colors.FAIL}✗ CLIの起動に失敗しました{Colors.ENDC}")
        return False
    
    required_commands = [
        "setup", "start", "stop", "restart", "health",
        "status", "logs", "cleanup", "test"
    ]
    
    missing_commands = []
    for cmd in required_commands:
        if cmd not in output:
            missing_commands.append(cmd)
    
    if not missing_commands:
        print(f"{Colors.OKGREEN}✓ 全ての必須コマンドが定義されています{Colors.ENDC}")
        for cmd in required_commands:
            print(f"  • {cmd}")
        return True
    else:
        print(f"{Colors.FAIL}✗ 一部のコマンドが不足しています{Colors.ENDC}")
        for cmd in missing_commands:
            print(f"  • {cmd}")
        return False


def main():
    """メイン関数"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}ローカルテストCLI - タスク6 検証テスト{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    tests = [
        ("CLIヘルプ", test_cli_help),
        ("全コマンド利用可能性", test_all_commands_available),
        ("setupコマンド", test_setup_command),
        ("startコマンド", test_start_command),
        ("stopコマンド", test_stop_command),
        ("healthコマンド", test_health_command),
        ("testコマンド", test_test_command),
        ("logsコマンド", test_logs_command),
        ("cleanupコマンド", test_cleanup_command),
        ("statusコマンド", test_status_command),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{Colors.FAIL}✗ テスト実行中にエラーが発生しました: {e}{Colors.ENDC}")
            results.append((test_name, False))
    
    # 結果サマリー
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}テスト結果サマリー{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"{status} {test_name}")
    
    print(f"\n{Colors.BOLD}合計: {passed}/{total} テスト成功{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ 全てのテストが成功しました！{Colors.ENDC}\n")
        
        # タスク完了レポート
        print(f"{Colors.BOLD}タスク6 実装完了{Colors.ENDC}")
        print(f"\n実装された機能:")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 6.1 基本CLIコマンド (setup, start, stop, health)")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 6.2 テスト関連コマンド (test unit/integration/e2e/all)")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} 6.3 ユーティリティコマンド (logs, cleanup, status)")
        print()
        
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ {total - passed}件のテストが失敗しました{Colors.ENDC}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
