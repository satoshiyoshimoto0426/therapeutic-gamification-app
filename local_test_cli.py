#!/usr/bin/env python3
"""
ローカルテスト環境 CLI

このスクリプトは、ローカルテスト環境の管理を統一的なCLIインターフェースで提供します。
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import json

# 既存モジュールのインポート
from local_test_setup import LocalTestSetup, EnvironmentChecker, Colors
from local_service_manager import LocalServiceManager
from local_test_runner import LocalTestRunner


class LocalTestCLI:
    """ローカルテスト環境のCLIインターフェース"""
    
    def __init__(self):
        self.setup = LocalTestSetup()
        self.service_manager: Optional[LocalServiceManager] = None
        self.test_runner = LocalTestRunner()
        
    def _ensure_service_manager(self) -> LocalServiceManager:
        """サービスマネージャーの初期化"""
        if self.service_manager is None:
            try:
                self.service_manager = LocalServiceManager()
            except Exception as e:
                print(f"{Colors.FAIL}サービスマネージャーの初期化に失敗しました: {e}{Colors.ENDC}")
                sys.exit(1)
        return self.service_manager
    
    def cmd_setup(self, args) -> int:
        """環境セットアップコマンド"""
        print(f"{Colors.HEADER}環境セットアップを開始します{Colors.ENDC}\n")
        
        success = self.setup.run_setup()
        return 0 if success else 1
    
    def cmd_start(self, args) -> int:
        """サービス起動コマンド"""
        manager = self._ensure_service_manager()
        
        if args.service:
            # 個別サービスの起動
            print(f"{Colors.OKCYAN}サービスを起動します: {args.service}{Colors.ENDC}\n")
            success = manager.start_service(args.service)
        else:
            # 全サービスの起動
            print(f"{Colors.OKCYAN}全サービスを起動します{Colors.ENDC}\n")
            results = manager.start_all_services(include_optional=args.all)
            success = all(results.values())
        
        return 0 if success else 1
    
    def cmd_stop(self, args) -> int:
        """サービス停止コマンド"""
        manager = self._ensure_service_manager()
        
        if args.service:
            # 個別サービスの停止
            print(f"{Colors.OKCYAN}サービスを停止します: {args.service}{Colors.ENDC}\n")
            success = manager.stop_service(args.service, graceful=not args.force)
        else:
            # 全サービスの停止
            print(f"{Colors.OKCYAN}全サービスを停止します{Colors.ENDC}\n")
            success = manager.stop_all_services(graceful=not args.force)
        
        return 0 if success else 1
    
    def cmd_restart(self, args) -> int:
        """サービス再起動コマンド"""
        manager = self._ensure_service_manager()
        
        if not args.service:
            print(f"{Colors.FAIL}サービス名を指定してください{Colors.ENDC}")
            return 1
        
        print(f"{Colors.OKCYAN}サービスを再起動します: {args.service}{Colors.ENDC}\n")
        success = manager.restart_service(args.service)
        
        return 0 if success else 1
    
    def cmd_health(self, args) -> int:
        """ヘルスチェックコマンド"""
        manager = self._ensure_service_manager()
        
        if args.service:
            # 個別サービスのヘルスチェック
            health = manager.check_service_health(args.service)
            self._print_health_result(args.service, health)
        else:
            # 全サービスのヘルスチェック
            results = manager.check_all_services_health()
            
            print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.HEADER}{Colors.BOLD}ヘルスチェック結果{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
            
            for service_name, health in results.items():
                self._print_health_result(service_name, health)
            
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        return 0
    
    def _print_health_result(self, service_name: str, health: dict):
        """ヘルスチェック結果の表示"""
        healthy = health.get("healthy", False)
        status_icon = f"{Colors.OKGREEN}✓{Colors.ENDC}" if healthy else f"{Colors.FAIL}✗{Colors.ENDC}"
        
        display_name = health.get("display_name", service_name)
        status = health.get("status", "unknown")
        
        print(f"{status_icon} {display_name} ({service_name})")
        print(f"   状態: {status}")
        
        if health.get("port"):
            print(f"   ポート: {health['port']}")
        
        if health.get("uptime"):
            uptime_str = f"{health['uptime']:.1f}秒"
            print(f"   稼働時間: {uptime_str}")
        
        if health.get("message"):
            print(f"   メッセージ: {health['message']}")
        
        print()

    def cmd_status(self, args) -> int:
        """システム状態表示コマンド"""
        manager = self._ensure_service_manager()
        
        if args.service:
            # 個別サービスの状態
            status = manager.get_service_status(args.service)
            if "error" in status:
                print(f"{Colors.FAIL}{status['error']}{Colors.ENDC}")
                return 1
            
            self._print_service_status(args.service, status)
        else:
            # 全サービスの状態
            manager.display_status_summary()
        
        return 0
    
    def _print_service_status(self, service_name: str, status: dict):
        """サービス状態の表示"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}サービス状態: {status.get('display_name', service_name)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        print(f"サービス名: {service_name}")
        print(f"表示名: {status.get('display_name', 'N/A')}")
        print(f"説明: {status.get('description', 'N/A')}")
        print(f"状態: {status.get('status', 'unknown')}")
        print(f"ポート: {status.get('port', 'N/A')}")
        print(f"必須: {'はい' if status.get('required') else 'いいえ'}")
        
        if status.get('pid'):
            print(f"プロセスID: {status['pid']}")
        
        if status.get('uptime'):
            uptime_str = f"{status['uptime']:.1f}秒"
            print(f"稼働時間: {uptime_str}")
        
        if status.get('start_time'):
            print(f"起動時刻: {status['start_time']}")
        
        if status.get('error_message'):
            print(f"{Colors.FAIL}エラー: {status['error_message']}{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    def cmd_logs(self, args) -> int:
        """ログ表示コマンド"""
        manager = self._ensure_service_manager()
        
        if not args.service:
            print(f"{Colors.FAIL}サービス名を指定してください{Colors.ENDC}")
            return 1
        
        if args.follow:
            # リアルタイムログ表示
            manager.tail_service_logs(args.service, follow=True)
        elif args.save:
            # ログをファイルに保存
            success = manager.save_service_logs(args.service, args.save, level=args.level)
            return 0 if success else 1
        else:
            # ログ表示
            manager.display_service_logs(args.service, lines=args.lines, level=args.level)
        
        return 0
    
    def cmd_cleanup(self, args) -> int:
        """クリーンアップコマンド"""
        print(f"{Colors.OKCYAN}クリーンアップを実行します{Colors.ENDC}\n")
        
        # サービスの停止
        if not args.keep_services:
            manager = self._ensure_service_manager()
            print("サービスを停止中...")
            manager.stop_all_services()
        
        # ログの保存
        if args.save_logs:
            manager = self._ensure_service_manager()
            print("ログを保存中...")
            manager.save_all_logs()
        
        # テストデータのクリーンアップ
        if not args.keep_data:
            print("テストデータをクリーンアップ中...")
            try:
                from mock_database import MockFirestoreClient
                mock_db = MockFirestoreClient()
                mock_db.clear_all_data()
                print(f"{Colors.OKGREEN}✓ テストデータをクリーンアップしました{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.WARNING}⚠️  テストデータのクリーンアップに失敗しました: {e}{Colors.ENDC}")
        
        # 一時ファイルの削除
        if args.temp_files:
            print("一時ファイルを削除中...")
            temp_patterns = ["*.pyc", "__pycache__", ".pytest_cache", ".coverage"]
            for pattern in temp_patterns:
                try:
                    import glob
                    for file in glob.glob(f"**/{pattern}", recursive=True):
                        path = Path(file)
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            import shutil
                            shutil.rmtree(path)
                except Exception as e:
                    print(f"{Colors.WARNING}⚠️  {pattern}の削除に失敗しました: {e}{Colors.ENDC}")
            
            print(f"{Colors.OKGREEN}✓ 一時ファイルを削除しました{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✓ クリーンアップが完了しました{Colors.ENDC}\n")
        return 0
    
    def cmd_test(self, args) -> int:
        """テスト実行コマンド"""
        test_type = args.test_type
        
        if test_type == 'unit':
            result = self.test_runner.run_unit_tests(
                pattern=args.pattern,
                path=args.path,
                verbose=args.verbose
            )
            return 0 if result.failed == 0 else 1
        
        elif test_type == 'integration':
            result = self.test_runner.run_integration_tests(
                setup_env=not args.no_setup,
                teardown_env=not args.no_teardown,
                verbose=args.verbose
            )
            return 0 if result.failed == 0 else 1
        
        elif test_type == 'e2e':
            result = self.test_runner.run_e2e_tests(
                headless=not args.no_headless,
                screenshot=args.screenshot,
                verbose=args.verbose
            )
            return 0 if result.failed == 0 else 1
        
        elif test_type == 'all':
            summary = self.test_runner.run_all_tests(verbose=args.verbose)
            total_failed = (summary.unit_tests.failed + 
                           summary.integration_tests.failed + 
                           summary.e2e_tests.failed)
            return 0 if total_failed == 0 else 1
        
        elif test_type == 'coverage':
            success = self.test_runner.generate_coverage_report(
                output_dir=args.output,
                html=not args.no_html
            )
            return 0 if success else 1
        
        return 1


def create_parser() -> argparse.ArgumentParser:
    """コマンドラインパーサーの作成"""
    parser = argparse.ArgumentParser(
        prog='local_test_cli',
        description='ローカルテスト環境管理CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境セットアップ
  python local_test_cli.py setup
  
  # 全サービス起動
  python local_test_cli.py start
  
  # 個別サービス起動
  python local_test_cli.py start --service auth
  
  # ヘルスチェック
  python local_test_cli.py health
  
  # ユニットテスト実行
  python local_test_cli.py test unit
  
  # 統合テスト実行
  python local_test_cli.py test integration
  
  # ログ表示
  python local_test_cli.py logs --service auth --lines 100
  
  # サービス停止
  python local_test_cli.py stop
  
  # クリーンアップ
  python local_test_cli.py cleanup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
    subparsers.required = True
    
    # setupコマンド
    parser_setup = subparsers.add_parser('setup', help='環境セットアップ')
    parser_setup.set_defaults(func=lambda cli, args: cli.cmd_setup(args))
    
    # startコマンド
    parser_start = subparsers.add_parser('start', help='サービス起動')
    parser_start.add_argument('--service', '-s', help='起動するサービス名')
    parser_start.add_argument('--all', '-a', action='store_true', 
                             help='オプションサービスも起動')
    parser_start.set_defaults(func=lambda cli, args: cli.cmd_start(args))
    
    # stopコマンド
    parser_stop = subparsers.add_parser('stop', help='サービス停止')
    parser_stop.add_argument('--service', '-s', help='停止するサービス名')
    parser_stop.add_argument('--force', '-f', action='store_true',
                            help='強制終了')
    parser_stop.set_defaults(func=lambda cli, args: cli.cmd_stop(args))
    
    # restartコマンド
    parser_restart = subparsers.add_parser('restart', help='サービス再起動')
    parser_restart.add_argument('service', help='再起動するサービス名')
    parser_restart.set_defaults(func=lambda cli, args: cli.cmd_restart(args))
    
    # healthコマンド
    parser_health = subparsers.add_parser('health', help='ヘルスチェック')
    parser_health.add_argument('--service', '-s', help='チェックするサービス名')
    parser_health.set_defaults(func=lambda cli, args: cli.cmd_health(args))
    
    # statusコマンド
    parser_status = subparsers.add_parser('status', help='システム状態表示')
    parser_status.add_argument('--service', '-s', help='表示するサービス名')
    parser_status.set_defaults(func=lambda cli, args: cli.cmd_status(args))
    
    # logsコマンド
    parser_logs = subparsers.add_parser('logs', help='ログ表示')
    parser_logs.add_argument('--service', '-s', required=True, help='サービス名')
    parser_logs.add_argument('--lines', '-n', type=int, default=50,
                            help='表示する行数（デフォルト: 50）')
    parser_logs.add_argument('--level', '-l', 
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                            help='ログレベルでフィルタリング')
    parser_logs.add_argument('--follow', '-f', action='store_true',
                            help='リアルタイムでログを表示')
    parser_logs.add_argument('--save', help='ログをファイルに保存')
    parser_logs.set_defaults(func=lambda cli, args: cli.cmd_logs(args))
    
    # cleanupコマンド
    parser_cleanup = subparsers.add_parser('cleanup', help='クリーンアップ')
    parser_cleanup.add_argument('--keep-services', action='store_true',
                               help='サービスを停止しない')
    parser_cleanup.add_argument('--keep-data', action='store_true',
                               help='テストデータを削除しない')
    parser_cleanup.add_argument('--save-logs', action='store_true',
                               help='ログを保存してから削除')
    parser_cleanup.add_argument('--temp-files', action='store_true',
                               help='一時ファイルも削除')
    parser_cleanup.set_defaults(func=lambda cli, args: cli.cmd_cleanup(args))
    
    # testコマンド
    parser_test = subparsers.add_parser('test', help='テスト実行')
    parser_test.add_argument('test_type',
                            choices=['unit', 'integration', 'e2e', 'all', 'coverage'],
                            help='実行するテストタイプ')
    parser_test.add_argument('-v', '--verbose', action='store_true',
                            help='詳細出力')
    parser_test.add_argument('-p', '--pattern', default='test_*.py',
                            help='ユニットテストのパターン')
    parser_test.add_argument('--path', help='テストを実行するパス')
    parser_test.add_argument('--no-setup', action='store_true',
                            help='テスト環境のセットアップをスキップ')
    parser_test.add_argument('--no-teardown', action='store_true',
                            help='テスト環境のティアダウンをスキップ')
    parser_test.add_argument('--no-headless', action='store_true',
                            help='ヘッドレスモードを無効化（E2Eテスト）')
    parser_test.add_argument('--screenshot', action='store_true',
                            help='スクリーンショットを撮る（E2Eテスト）')
    parser_test.add_argument('--output', '-o',
                            help='カバレッジレポートの出力先')
    parser_test.add_argument('--no-html', action='store_true',
                            help='HTMLレポートを生成しない')
    parser_test.set_defaults(func=lambda cli, args: cli.cmd_test(args))
    
    return parser


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # CLIインスタンスの作成
    cli = LocalTestCLI()
    
    try:
        # コマンドの実行
        exit_code = args.func(cli, args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}操作が中断されました{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}エラーが発生しました: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
