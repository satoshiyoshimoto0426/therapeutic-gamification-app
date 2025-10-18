#!/usr/bin/env python3
"""
環境チェック機能のエラーケーステスト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_test_setup import EnvironmentChecker, Colors


def test_recovery_hints():
    """復旧ヒント機能のテスト"""
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}復旧ヒント機能テスト{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    checker = EnvironmentChecker()
    
    # 失敗シナリオをシミュレート
    print(f"{Colors.BOLD}失敗シナリオのシミュレーション:{Colors.ENDC}\n")
    
    # 手動で失敗結果を設定
    checker.results = {
        "Python": (False, "Python 2.7.0 (3.9以上が必要)"),
        "Node.js": (False, "Node.jsが見つかりません"),
        "npm": (True, "npm 8.0.0 ✓"),
        "pip": (False, "pipが見つかりません"),
        "CPU": (True, "CPU: 8コア (使用率: 10.0%) ✓"),
        "メモリ": (True, "利用可能メモリ: 4.0GB / 8.0GB ✓"),
        "ディスク容量": (False, "ディスク空き容量不足: 1.5GB (2GB以上推奨)"),
        "必要ファイル": (True, "必要なファイル: すべて存在 ✓")
    }
    
    # 結果を表示（復旧ヒント付き）
    result = checker.print_results()
    
    if not result:
        print(f"\n{Colors.OKGREEN}✓ 復旧ヒントが正しく表示されました{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}✗ テストが期待通りに失敗しませんでした{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}テスト完了{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def test_edge_cases():
    """エッジケースのテスト"""
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}エッジケーステスト{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    checker = EnvironmentChecker()
    
    # 空の結果
    print(f"{Colors.BOLD}1. 空の結果セット:{Colors.ENDC}")
    checker.results = {}
    try:
        checker.print_results()
        print(f"{Colors.OKGREEN}✓ 空の結果セットを処理できました{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}✗ エラー: {str(e)}{Colors.ENDC}\n")
    
    # すべて警告（続行可能）
    print(f"{Colors.BOLD}2. すべて警告（続行可能）:{Colors.ENDC}")
    checker.results = {
        "メモリ": (True, "⚠️  利用可能メモリ: 1.5GB (2GB以上推奨、続行可能)"),
        "CPU": (True, "⚠️  CPU: 1コア (2コア以上推奨、続行可能)")
    }
    try:
        result = checker.print_results()
        if result:
            print(f"{Colors.OKGREEN}✓ 警告付きで合格しました{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}✗ 予期しない失敗{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}✗ エラー: {str(e)}{Colors.ENDC}\n")
    
    # システム情報取得のエッジケース
    print(f"{Colors.BOLD}3. システム情報取得:{Colors.ENDC}")
    try:
        info = checker.get_system_info()
        required_keys = ["OS", "OSバージョン", "アーキテクチャ", "Pythonバージョン", "作業ディレクトリ"]
        missing_keys = [key for key in required_keys if key not in info]
        
        if not missing_keys:
            print(f"{Colors.OKGREEN}✓ すべての必須情報が取得できました{Colors.ENDC}")
            print(f"  取得した情報: {', '.join(info.keys())}\n")
        else:
            print(f"{Colors.FAIL}✗ 不足している情報: {', '.join(missing_keys)}{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}✗ エラー: {str(e)}{Colors.ENDC}\n")
    
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}エッジケーステスト完了{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        print(f"\n{Colors.OKCYAN}復旧ヒント機能のテストを実行します...{Colors.ENDC}\n")
        test_recovery_hints()
        
        print(f"\n{Colors.OKCYAN}エッジケースのテストを実行します...{Colors.ENDC}\n")
        test_edge_cases()
        
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ すべてのテストが完了しました！{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}テスト実行エラー: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
