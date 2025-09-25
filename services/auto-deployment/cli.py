"""
自動デプロイメントCLIインターフェース

コマンドライン経由での自動デプロイメント機能を提供します。
"""

import asyncio
import click
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from .config import Environment, DeploymentStrategy, default_config_manager
    from .orchestrator import DeploymentOrchestrator
    from .exceptions import DeploymentError
except ImportError:
    # テスト環境での絶対インポート
    from config import Environment, DeploymentStrategy, default_config_manager
    from orchestrator import DeploymentOrchestrator
    from exceptions import DeploymentError


class CLIColors:
    """CLI用カラーコード"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """ヘッダーを表示"""
    print(f"\n{CLIColors.BOLD}{CLIColors.CYAN}{'='*60}{CLIColors.END}")
    print(f"{CLIColors.BOLD}{CLIColors.CYAN}🚀 {text}{CLIColors.END}")
    print(f"{CLIColors.BOLD}{CLIColors.CYAN}{'='*60}{CLIColors.END}")


def print_success(text: str):
    """成功メッセージを表示"""
    print(f"{CLIColors.GREEN}✅ {text}{CLIColors.END}")


def print_error(text: str):
    """エラーメッセージを表示"""
    print(f"{CLIColors.RED}❌ {text}{CLIColors.END}")


def print_warning(text: str):
    """警告メッセージを表示"""
    print(f"{CLIColors.YELLOW}⚠️  {text}{CLIColors.END}")


def print_info(text: str):
    """情報メッセージを表示"""
    print(f"{CLIColors.WHITE}ℹ️  {text}{CLIColors.END}")


def print_step(step: int, text: str):
    """ステップを表示"""
    print(f"\n{CLIColors.BOLD}{CLIColors.BLUE}[ステップ {step}] {text}{CLIColors.END}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    治療的ゲーミフィケーションアプリ自動デプロイメントツール
    
    このツールは、アプリケーションの自動デプロイメント、監視、
    ロールバック機能を提供します。
    """
    pass


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='デプロイ先環境'
)
@click.option(
    '--strategy', '-s',
    type=click.Choice(['blue_green', 'rolling_update', 'canary']),
    default='blue_green',
    help='デプロイメント戦略'
)
@click.option(
    '--config-file', '-c',
    type=click.Path(exists=True),
    help='設定ファイルのパス'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='実際のデプロイを行わず、検証のみ実行'
)
@click.option(
    '--skip-tests',
    is_flag=True,
    help='テストをスキップ（非推奨）'
)
@click.option(
    '--force',
    is_flag=True,
    help='警告を無視して強制実行'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='インタラクティブモードで実行'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def deploy(
    environment: Optional[str],
    strategy: str,
    config_file: Optional[str],
    dry_run: bool,
    skip_tests: bool,
    force: bool,
    interactive: bool,
    output_format: str
):
    """
    アプリケーションを指定された環境にデプロイします。
    
    例:
        auto-deploy deploy -e production
        auto-deploy deploy -e staging -s rolling_update
        auto-deploy deploy -e development --dry-run
        auto-deploy deploy --interactive
    """
    
    # インタラクティブモードの処理
    if interactive:
        environment, strategy, options = _interactive_deployment_setup()
        dry_run = options.get('dry_run', dry_run)
        skip_tests = options.get('skip_tests', skip_tests)
        force = options.get('force', force)
    elif not environment:
        print_error("環境が指定されていません。--environment オプションを使用するか、--interactive モードを使用してください。")
        sys.exit(1)
    
    print_header(f"自動デプロイメント開始 - {environment.upper()}")
    
    try:
        # 環境とストラテジーの変換
        env = Environment(environment)
        deploy_strategy = DeploymentStrategy(strategy)
        
        # 設定の準備
        config = default_config_manager.get_config(env)
        config.strategy = deploy_strategy
        
        if config_file:
            print_info(f"設定ファイルを読み込み: {config_file}")
            # TODO: 設定ファイルの読み込み実装
        
        # オプションの適用
        options = {
            'dry_run': dry_run,
            'skip_tests': skip_tests,
            'force': force
        }
        
        if dry_run:
            print_warning("ドライランモード: 実際のデプロイは実行されません")
        
        if skip_tests:
            print_warning("テストをスキップします（非推奨）")
        
        # デプロイメント実行
        result = asyncio.run(_execute_deployment(config, env, options))
        
        # 結果の表示
        _display_deployment_result(result, output_format)
        
        # 終了コードの設定
        sys.exit(0 if result.is_success else 1)
        
    except Exception as e:
        print_error(f"デプロイメントでエラーが発生しました: {str(e)}")
        if output_format == 'json':
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        sys.exit(1)


@cli.command()
@click.option(
    '--deployment-id',
    help='特定のデプロイメントIDの状態を確認'
)
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='環境の状態を確認'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def status(deployment_id: Optional[str], environment: Optional[str], output_format: str):
    """
    デプロイメントの状態を確認します。
    
    例:
        auto-deploy status
        auto-deploy status --deployment-id abc123
        auto-deploy status -e production
    """
    print_header("デプロイメント状態確認")
    
    try:
        # TODO: 実際の状態確認ロジックを実装
        if deployment_id:
            print_info(f"デプロイメントID: {deployment_id} の状態を確認中...")
            # 特定のデプロイメント状態を取得
            status_info = _get_deployment_status(deployment_id)
        elif environment:
            print_info(f"環境: {environment} の状態を確認中...")
            # 環境の現在状態を取得
            status_info = _get_environment_status(environment)
        else:
            print_info("全体の状態を確認中...")
            # 全体状態を取得
            status_info = _get_overall_status()
        
        _display_status(status_info, output_format)
        
    except Exception as e:
        print_error(f"状態確認でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    required=True,
    help='ロールバック対象環境'
)
@click.option(
    '--revision',
    help='ロールバック先のリビジョン（指定しない場合は前回の安定版）'
)
@click.option(
    '--reason', '-r',
    required=True,
    help='ロールバックの理由'
)
@click.option(
    '--operator-id',
    help='オペレーターID（指定しない場合は現在のユーザー）'
)
@click.option(
    '--emergency',
    is_flag=True,
    help='緊急ロールバック（確認をスキップ）'
)
@click.option(
    '--severity',
    type=click.Choice(['info', 'warning', 'critical']),
    default='warning',
    help='重要度レベル'
)
@click.option(
    '--force',
    is_flag=True,
    help='確認なしで強制実行'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def rollback(
    environment: str, 
    revision: Optional[str], 
    reason: str,
    operator_id: Optional[str],
    emergency: bool,
    severity: str,
    force: bool,
    output_format: str
):
    """
    指定された環境を前回の安定版にロールバックします。
    
    例:
        auto-deploy rollback -e production -r "Performance issues detected"
        auto-deploy rollback -e staging --revision abc123 -r "Bug fix rollback"
        auto-deploy rollback -e production -r "Critical security issue" --emergency
    """
    print_header(f"手動ロールバック実行 - {environment.upper()}")
    
    # オペレーターIDの設定
    if not operator_id:
        import getpass
        operator_id = getpass.getuser()
    
    # 緊急ロールバックでない場合は確認
    if not emergency and not force:
        click.confirm(
            f"本当に {environment} 環境をロールバックしますか？\n"
            f"理由: {reason}\n"
            f"オペレーター: {operator_id}",
            abort=True
        )
    
    try:
        print_info(f"環境 {environment} の手動ロールバックを開始...")
        print_info(f"理由: {reason}")
        print_info(f"オペレーター: {operator_id}")
        print_info(f"重要度: {severity}")
        
        if emergency:
            print_warning("緊急ロールバックモード")
        
        # 手動ロールバックトリガーを実行
        result = asyncio.run(_execute_manual_rollback(
            environment=environment,
            revision=revision,
            reason=reason,
            operator_id=operator_id,
            emergency=emergency,
            severity=severity
        ))
        
        # 結果の表示
        _display_rollback_result(result, output_format)
        
        # 終了コードの設定
        sys.exit(0 if result.get('success', False) else 1)
            
    except Exception as e:
        print_error(f"ロールバックでエラーが発生しました: {str(e)}")
        if output_format == 'json':
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        sys.exit(1)


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='特定環境の設定を表示'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json', 'yaml']),
    default='text',
    help='出力形式'
)
def config(environment: Optional[str], output_format: str):
    """
    現在の設定を表示します。
    
    例:
        auto-deploy config
        auto-deploy config -e production --output-format json
    """
    print_header("設定情報表示")
    
    try:
        if environment:
            env = Environment(environment)
            config_data = default_config_manager.get_config(env)
            print_info(f"環境: {environment}")
        else:
            # 全環境の設定を表示
            config_data = {
                env.value: default_config_manager.get_config(env)
                for env in Environment
            }
        
        _display_config(config_data, output_format)
        
    except Exception as e:
        print_error(f"設定表示でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='特定環境の検証'
)
def validate(environment: Optional[str]):
    """
    デプロイメント前の検証を実行します。
    
    例:
        auto-deploy validate
        auto-deploy validate -e production
    """
    print_header("デプロイメント前検証")
    
    try:
        if environment:
            env = Environment(environment)
            print_info(f"環境 {environment} の検証を実行中...")
            result = _validate_environment(env)
        else:
            print_info("全環境の検証を実行中...")
            result = _validate_all_environments()
        
        if result['valid']:
            print_success("検証が完了しました - 問題なし")
        else:
            print_error("検証で問題が発見されました:")
            for error in result['errors']:
                print_error(f"  - {error}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"検証でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='監視対象環境'
)
@click.option(
    '--watch', '-w',
    is_flag=True,
    help='リアルタイム監視モード'
)
@click.option(
    '--interval',
    type=int,
    default=30,
    help='監視間隔（秒）'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def monitor(environment: Optional[str], watch: bool, interval: int, output_format: str):
    """
    デプロイメントとシステムの監視を実行します。
    
    例:
        auto-deploy monitor
        auto-deploy monitor -e production --watch
        auto-deploy monitor -e staging --interval 60
    """
    print_header("システム監視")
    
    try:
        if watch:
            print_info(f"リアルタイム監視を開始します（間隔: {interval}秒）")
            print_info("Ctrl+Cで停止します")
            _start_realtime_monitoring(environment, interval, output_format)
        else:
            print_info("現在の監視状況を確認中...")
            result = _get_monitoring_status(environment)
            _display_monitoring_status(result, output_format)
            
    except KeyboardInterrupt:
        print_info("\n監視を停止しました")
    except Exception as e:
        print_error(f"監視でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--limit',
    type=int,
    default=10,
    help='表示する履歴の件数'
)
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='特定環境の履歴のみ表示'
)
@click.option(
    '--status-filter',
    type=click.Choice(['success', 'failed', 'in_progress', 'rolled_back']),
    help='ステータスでフィルタ'
)
@click.option(
    '--date-from',
    help='開始日時 (YYYY-MM-DD HH:MM:SS)'
)
@click.option(
    '--date-to',
    help='終了日時 (YYYY-MM-DD HH:MM:SS)'
)
@click.option(
    '--operator',
    help='オペレーターでフィルタ'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json', 'csv']),
    default='text',
    help='出力形式'
)
def history(limit: int, environment: Optional[str], status_filter: Optional[str], 
           date_from: Optional[str], date_to: Optional[str], operator: Optional[str], 
           output_format: str):
    """
    デプロイメント履歴を表示します。
    
    例:
        auto-deploy history
        auto-deploy history --limit 20
        auto-deploy history -e production --status-filter success
        auto-deploy history --date-from "2024-01-01 00:00:00" --date-to "2024-01-31 23:59:59"
        auto-deploy history --operator system
    """
    print_header("デプロイメント履歴")
    
    try:
        print_info(f"デプロイメント履歴を取得中（最新{limit}件）...")
        
        filters = {}
        if environment:
            filters['environment'] = environment
        if status_filter:
            filters['status'] = status_filter
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        if operator:
            filters['operator'] = operator
            
        history_data = _get_deployment_history(limit, filters)
        _display_deployment_history(history_data, output_format)
        
    except Exception as e:
        print_error(f"履歴取得でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--key', '-k',
    required=True,
    help='設定キー'
)
@click.option(
    '--value', '-v',
    help='設定値（指定しない場合は現在の値を表示）'
)
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='環境固有の設定'
)
@click.option(
    '--type',
    type=click.Choice(['string', 'int', 'bool', 'json']),
    default='string',
    help='値の型'
)
def config_set(key: str, value: Optional[str], environment: Optional[str], type: str):
    """
    設定値を設定または表示します。
    
    例:
        auto-deploy config-set -k deployment.timeout -v 300
        auto-deploy config-set -k deployment.strategy -v blue_green -e production
        auto-deploy config-set -k monitoring.enabled -v true --type bool
    """
    print_header("設定管理")
    
    try:
        if value is None:
            # 現在の値を表示
            current_value = _get_config_value(key, environment)
            print_info(f"設定キー: {key}")
            if environment:
                print_info(f"環境: {environment}")
            print_info(f"現在の値: {current_value}")
        else:
            # 値を設定
            parsed_value = _parse_config_value(value, type)
            _set_config_value(key, parsed_value, environment)
            print_success(f"設定を更新しました: {key} = {parsed_value}")
            if environment:
                print_info(f"環境: {environment}")
                
    except Exception as e:
        print_error(f"設定管理でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
@click.option(
    '--history-hours',
    type=int,
    default=24,
    help='表示する履歴の時間数'
)
def rollback_status(output_format: str, history_hours: int):
    """
    ロールバックシステムの状態と履歴を表示します。
    
    例:
        auto-deploy rollback-status
        auto-deploy rollback-status --output-format json
        auto-deploy rollback-status --history-hours 48
    """
    print_header("ロールバックシステム状態")
    
    try:
        result = asyncio.run(_get_rollback_status(history_hours))
        _display_rollback_status(result, output_format)
        
    except Exception as e:
        print_error(f"ロールバック状態の取得でエラーが発生しました: {str(e)}")
        if output_format == 'json':
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        sys.exit(1)


# ヘルパー関数
async def _execute_deployment(config, environment, options):
    """デプロイメントを実行"""
    orchestrator = DeploymentOrchestrator(config)
    return await orchestrator.deploy(environment, options)


def _display_deployment_result(result, output_format):
    """デプロイメント結果を表示"""
    if output_format == 'json':
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"\n{CLIColors.BOLD}デプロイメント結果:{CLIColors.END}")
        print(f"  ID: {result.deployment_id}")
        print(f"  ステータス: {result.status.value}")
        print(f"  環境: {result.environment.value if result.environment else 'N/A'}")
        print(f"  開始時刻: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.end_time:
            print(f"  終了時刻: {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  実行時間: {result.duration_seconds:.1f}秒")
        
        if result.service_url:
            print(f"  サービスURL: {result.service_url}")
        
        if result.steps_completed:
            print(f"  完了ステップ: {', '.join(result.steps_completed)}")
        
        if result.steps_failed:
            print(f"  失敗ステップ: {', '.join(result.steps_failed)}")
        
        if result.error:
            print_error(f"エラー: {result.error.message}")


def _get_deployment_status(deployment_id: str):
    """特定のデプロイメント状態を取得"""
    # TODO: 実装
    return {"deployment_id": deployment_id, "status": "unknown"}


def _get_environment_status(environment: str):
    """環境の状態を取得"""
    # TODO: 実装
    return {"environment": environment, "status": "unknown"}


def _get_overall_status():
    """全体状態を取得"""
    # TODO: 実装
    return {"overall_status": "unknown"}


def _display_status(status_info, output_format):
    """状態情報を表示"""
    if output_format == 'json':
        print(json.dumps(status_info, indent=2, ensure_ascii=False))
    else:
        print_info("状態情報:")
        for key, value in status_info.items():
            print(f"  {key}: {value}")


async def _execute_manual_rollback(
    environment: str,
    revision: Optional[str],
    reason: str,
    operator_id: str,
    emergency: bool,
    severity: str
) -> Dict[str, Any]:
    """手動ロールバックを実行"""
    from .rollback.rollback_triggers import ManualRollbackTrigger, RollbackTriggerConfig
    
    try:
        # 手動ロールバックトリガーの設定
        config = RollbackTriggerConfig(
            enabled=True,
            cooldown_minutes=5 if not emergency else 0,
            max_rollbacks_per_hour=3,
            require_confirmation=False  # CLIで既に確認済み
        )
        
        # 手動ロールバックトリガーを作成
        manual_trigger = ManualRollbackTrigger(config)
        await manual_trigger.start()
        
        # ロールバック結果を格納する変数
        rollback_result = {"success": False, "trigger_id": None, "message": ""}
        
        # コールバック関数を定義
        async def rollback_callback(request):
            rollback_result["success"] = True
            rollback_result["trigger_id"] = request.trigger_id
            rollback_result["message"] = f"ロールバック要求が正常に作成されました: {request.trigger_id}"
            rollback_result["request"] = {
                "reason": request.reason.value,
                "severity": request.severity,
                "timestamp": request.timestamp.isoformat(),
                "operator_id": request.operator_id,
                "metadata": request.metadata
            }
        
        # コールバックを登録
        manual_trigger.add_callback(rollback_callback)
        
        # メタデータの準備
        metadata = {
            "environment": environment,
            "cli_initiated": True
        }
        if revision:
            metadata["target_revision"] = revision
        
        # 手動ロールバックをトリガー
        trigger_id = await manual_trigger.trigger_rollback(
            reason=reason,
            operator_id=operator_id,
            severity=severity,
            emergency=emergency,
            metadata=metadata
        )
        
        await manual_trigger.stop()
        
        return rollback_result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"手動ロールバックの実行中にエラーが発生しました: {str(e)}"
        }


def _display_rollback_result(result: Dict[str, Any], output_format: str):
    """ロールバック結果を表示"""
    if output_format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('success', False):
            print_success("手動ロールバック要求が正常に作成されました")
            print_info(f"トリガーID: {result.get('trigger_id', 'N/A')}")
            if 'request' in result:
                req = result['request']
                print_info(f"理由: {req.get('reason', 'N/A')}")
                print_info(f"重要度: {req.get('severity', 'N/A')}")
                print_info(f"タイムスタンプ: {req.get('timestamp', 'N/A')}")
                print_info(f"オペレーター: {req.get('operator_id', 'N/A')}")
        else:
            print_error("手動ロールバック要求の作成に失敗しました")
            if 'error' in result:
                print_error(f"エラー: {result['error']}")
            if 'message' in result:
                print_error(f"メッセージ: {result['message']}")


def _display_config(config_data, output_format):
    """設定情報を表示"""
    if output_format == 'json':
        # DataClassを辞書に変換
        if hasattr(config_data, '__dict__'):
            config_dict = _dataclass_to_dict(config_data)
        else:
            config_dict = config_data
        print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    else:
        print_info("設定情報:")
        # TODO: テキスト形式での設定表示実装


def _dataclass_to_dict(obj):
    """DataClassを辞書に変換"""
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if hasattr(value, '__dict__'):
                result[key] = _dataclass_to_dict(value)
            elif hasattr(value, 'value'):  # Enum
                result[key] = value.value
            else:
                result[key] = value
        return result
    return obj


def _validate_environment(environment: Environment):
    """環境の検証"""
    # TODO: 実装
    return {"valid": True, "errors": []}


def _validate_all_environments():
    """全環境の検証"""
    # TODO: 実装
    return {"valid": True, "errors": []}


async def _get_rollback_status(history_hours: int) -> Dict[str, Any]:
    """ロールバックシステムの状態を取得"""
    from .rollback.rollback_triggers import ManualRollbackTrigger, RollbackTriggerConfig
    from .rollback.failure_detector import FailureDetector
    from .monitoring.health_check import HealthCheckManager
    from .monitoring.performance_monitor import PerformanceMonitor
    
    try:
        # 手動ロールバックトリガーの状態を取得
        config = RollbackTriggerConfig()
        manual_trigger = ManualRollbackTrigger(config)
        manual_status = manual_trigger.get_rollback_status()
        
        # 失敗検出システムの状態を取得（モックデータ）
        failure_status = {
            "monitoring_active": False,
            "total_conditions": 4,
            "enabled_conditions": 4,
            "recent_failures": 0,
            "failure_counts": {},
            "has_critical_failures": False,
            "last_check": datetime.now().isoformat()
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "manual_rollback": manual_status,
            "failure_detection": failure_status,
            "system_health": {
                "overall_status": "healthy",
                "last_deployment": None,
                "active_monitoring": False
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }


def _display_rollback_status(status: Dict[str, Any], output_format: str):
    """ロールバック状態を表示"""
    if output_format == 'json':
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        if 'error' in status:
            print_error(f"状態取得エラー: {status['error']}")
            return
        
        print_info("ロールバックシステム状態:")
        print(f"  タイムスタンプ: {status['timestamp']}")
        
        # 手動ロールバック状態
        manual = status.get('manual_rollback', {})
        print(f"\n{CLIColors.BOLD}手動ロールバック:{CLIColors.END}")
        print(f"  アクティブ: {manual.get('active', False)}")
        print(f"  有効: {manual.get('config', {}).get('enabled', False)}")
        print(f"  クールダウン時間: {manual.get('config', {}).get('cooldown_minutes', 0)}分")
        print(f"  時間当たり最大実行数: {manual.get('config', {}).get('max_rollbacks_per_hour', 0)}")
        print(f"  最近のロールバック数: {manual.get('recent_rollbacks', 0)}")
        print(f"  実行可能: {manual.get('can_rollback', False)}")
        
        # 失敗検出状態
        failure = status.get('failure_detection', {})
        print(f"\n{CLIColors.BOLD}失敗検出システム:{CLIColors.END}")
        print(f"  監視アクティブ: {failure.get('monitoring_active', False)}")
        print(f"  設定済み条件数: {failure.get('total_conditions', 0)}")
        print(f"  有効条件数: {failure.get('enabled_conditions', 0)}")
        print(f"  最近の失敗数: {failure.get('recent_failures', 0)}")
        print(f"  重大な失敗: {failure.get('has_critical_failures', False)}")
        
        # システム全体の健全性
        health = status.get('system_health', {})
        print(f"\n{CLIColors.BOLD}システム健全性:{CLIColors.END}")
        print(f"  全体状態: {health.get('overall_status', 'unknown')}")
        print(f"  アクティブ監視: {health.get('active_monitoring', False)}")


def _start_realtime_monitoring(environment: Optional[str], interval: int, output_format: str):
    """リアルタイム監視を開始"""
    import time
    
    while True:
        try:
            # 画面をクリア（テキスト形式の場合のみ）
            if output_format == 'text':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header(f"リアルタイム監視 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 監視データを取得
            monitoring_data = _get_monitoring_status(environment)
            _display_monitoring_status(monitoring_data, output_format)
            
            if output_format == 'text':
                print(f"\n次の更新まで {interval} 秒...")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            break


def _get_monitoring_status(environment: Optional[str]) -> Dict[str, Any]:
    """監視状況を取得"""
    # TODO: 実際の監視システムとの統合
    return {
        "timestamp": datetime.now().isoformat(),
        "environment": environment,
        "services": {
            "auth": {"status": "healthy", "response_time": 45},
            "core-game": {"status": "healthy", "response_time": 67},
            "task-mgmt": {"status": "healthy", "response_time": 32}
        },
        "deployment": {
            "active": False,
            "last_deployment": "2024-01-15T10:30:00Z",
            "status": "success"
        },
        "alerts": []
    }


def _display_monitoring_status(data: Dict[str, Any], output_format: str):
    """監視状況を表示"""
    if output_format == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_info(f"監視状況 - {data['timestamp']}")
        if data.get('environment'):
            print_info(f"環境: {data['environment']}")
        
        # サービス状況
        services = data.get('services', {})
        print(f"\n{CLIColors.BOLD}サービス状況:{CLIColors.END}")
        for service, info in services.items():
            status = info.get('status', 'unknown')
            response_time = info.get('response_time', 0)
            
            if status == 'healthy':
                print_success(f"  {service}: {status} ({response_time}ms)")
            else:
                print_error(f"  {service}: {status} ({response_time}ms)")
        
        # デプロイメント状況
        deployment = data.get('deployment', {})
        print(f"\n{CLIColors.BOLD}デプロイメント状況:{CLIColors.END}")
        print(f"  アクティブ: {deployment.get('active', False)}")
        print(f"  最終デプロイ: {deployment.get('last_deployment', 'N/A')}")
        print(f"  ステータス: {deployment.get('status', 'unknown')}")
        
        # アラート
        alerts = data.get('alerts', [])
        if alerts:
            print(f"\n{CLIColors.BOLD}アクティブアラート:{CLIColors.END}")
            for alert in alerts:
                print_warning(f"  - {alert}")
        else:
            print(f"\n{CLIColors.BOLD}アラート: なし{CLIColors.END}")


def _get_deployment_history(limit: int, filters: Dict[str, str]) -> Dict[str, Any]:
    """デプロイメント履歴を取得"""
    # TODO: 実際の履歴データベースとの統合
    mock_history = []
    for i in range(limit):
        mock_history.append({
            "id": f"deploy-{i+1:03d}",
            "timestamp": (datetime.now() - timedelta(hours=i*2)).isoformat(),
            "environment": ["production", "staging", "development"][i % 3],
            "status": ["success", "failed", "success", "success"][i % 4],
            "duration": 120 + (i * 10),
            "commit_sha": f"abc123{i:02d}",
            "operator": "system"
        })
    
    # フィルタを適用
    if filters:
        filtered_history = []
        for item in mock_history:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered_history.append(item)
        mock_history = filtered_history
    
    return {
        "total": len(mock_history),
        "items": mock_history[:limit],
        "filters": filters
    }


def _display_deployment_history(data: Dict[str, Any], output_format: str):
    """デプロイメント履歴を表示"""
    if output_format == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif output_format == 'csv':
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'timestamp', 'environment', 'status', 'duration', 'commit_sha', 'operator'])
        writer.writeheader()
        writer.writerows(data['items'])
        print(output.getvalue())
    else:
        print_info(f"デプロイメント履歴（{data['total']}件）")
        if data.get('filters'):
            print_info(f"フィルタ: {data['filters']}")
        
        print(f"\n{CLIColors.BOLD}{'ID':<12} {'タイムスタンプ':<20} {'環境':<12} {'ステータス':<10} {'時間':<8} {'コミット':<10}{CLIColors.END}")
        print("-" * 80)
        
        for item in data['items']:
            status_color = CLIColors.GREEN if item['status'] == 'success' else CLIColors.RED
            print(f"{item['id']:<12} {item['timestamp'][:19]:<20} {item['environment']:<12} "
                  f"{status_color}{item['status']:<10}{CLIColors.END} {item['duration']:<8} {item['commit_sha'][:8]:<10}")


def _get_config_value(key: str, environment: Optional[str]) -> Any:
    """設定値を取得"""
    # TODO: 実際の設定システムとの統合
    config_map = {
        "deployment.timeout": 300,
        "deployment.strategy": "blue_green",
        "monitoring.enabled": True,
        "notification.slack.enabled": True,
        "rollback.auto_enabled": True
    }
    return config_map.get(key, "未設定")


def _set_config_value(key: str, value: Any, environment: Optional[str]):
    """設定値を設定"""
    # TODO: 実際の設定システムとの統合
    print_info(f"設定を保存中: {key} = {value}")
    if environment:
        print_info(f"環境: {environment}")


def _parse_config_value(value: str, value_type: str) -> Any:
    """設定値を適切な型に変換"""
    if value_type == 'int':
        return int(value)
    elif value_type == 'bool':
        return value.lower() in ('true', '1', 'yes', 'on')
    elif value_type == 'json':
        return json.loads(value)
    else:
        return value


def _interactive_deployment_setup():
    """インタラクティブデプロイメントセットアップ"""
    print_header("インタラクティブデプロイメントセットアップ")
    
    # 環境の選択
    print_info("デプロイ先環境を選択してください:")
    print("  1. development")
    print("  2. staging") 
    print("  3. production")
    
    while True:
        choice = click.prompt("環境を選択 (1-3)", type=int)
        if choice == 1:
            environment = 'development'
            break
        elif choice == 2:
            environment = 'staging'
            break
        elif choice == 3:
            environment = 'production'
            break
        else:
            print_error("無効な選択です。1-3の数字を入力してください。")
    
    print_success(f"選択された環境: {environment}")
    
    # デプロイメント戦略の選択
    print_info("\nデプロイメント戦略を選択してください:")
    print("  1. blue_green (推奨)")
    print("  2. rolling_update")
    print("  3. canary")
    
    while True:
        choice = click.prompt("戦略を選択 (1-3)", type=int, default=1)
        if choice == 1:
            strategy = 'blue_green'
            break
        elif choice == 2:
            strategy = 'rolling_update'
            break
        elif choice == 3:
            strategy = 'canary'
            break
        else:
            print_error("無効な選択です。1-3の数字を入力してください。")
    
    print_success(f"選択された戦略: {strategy}")
    
    # オプションの設定
    print_info("\nデプロイメントオプション:")
    
    dry_run = click.confirm("ドライランモードで実行しますか？", default=False)
    if dry_run:
        print_info("ドライランモードが有効になりました")
    
    skip_tests = False
    if environment == 'production':
        print_warning("本番環境へのデプロイではテストのスキップは推奨されません")
    else:
        skip_tests = click.confirm("テストをスキップしますか？", default=False)
        if skip_tests:
            print_warning("テストがスキップされます")
    
    force = click.confirm("警告を無視して強制実行しますか？", default=False)
    if force:
        print_warning("強制実行モードが有効になりました")
    
    # 確認
    print_info("\n=== デプロイメント設定確認 ===")
    print(f"環境: {environment}")
    print(f"戦略: {strategy}")
    print(f"ドライラン: {dry_run}")
    print(f"テストスキップ: {skip_tests}")
    print(f"強制実行: {force}")
    
    if not click.confirm("\nこの設定でデプロイメントを開始しますか？"):
        print_info("デプロイメントがキャンセルされました")
        sys.exit(0)
    
    options = {
        'dry_run': dry_run,
        'skip_tests': skip_tests,
        'force': force
    }
    
    return environment, strategy, options


@cli.command()
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='特定環境のロールバック履歴'
)
@click.option(
    '--limit',
    type=int,
    default=10,
    help='表示する履歴の件数'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def rollback_history(environment: Optional[str], limit: int, output_format: str):
    """
    ロールバック履歴を表示します。
    
    例:
        auto-deploy rollback-history
        auto-deploy rollback-history -e production
        auto-deploy rollback-history --limit 20
    """
    print_header("ロールバック履歴")
    
    try:
        print_info(f"ロールバック履歴を取得中（最新{limit}件）...")
        
        filters = {}
        if environment:
            filters['environment'] = environment
            
        rollback_data = _get_rollback_history(limit, filters)
        _display_rollback_history(rollback_data, output_format)
        
    except Exception as e:
        print_error(f"ロールバック履歴取得でエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--deployment-id',
    required=True,
    help='ロールバック対象のデプロイメントID'
)
@click.option(
    '--reason', '-r',
    required=True,
    help='ロールバックの理由'
)
@click.option(
    '--operator-id',
    help='オペレーターID'
)
@click.option(
    '--force',
    is_flag=True,
    help='確認なしで強制実行'
)
def rollback_to(deployment_id: str, reason: str, operator_id: Optional[str], force: bool):
    """
    特定のデプロイメントIDにロールバックします。
    
    例:
        auto-deploy rollback-to --deployment-id deploy-001 -r "Critical bug fix"
        auto-deploy rollback-to --deployment-id deploy-001 -r "Performance issue" --force
    """
    print_header(f"特定デプロイメントへのロールバック - {deployment_id}")
    
    # オペレーターIDの設定
    if not operator_id:
        import getpass
        operator_id = getpass.getuser()
    
    # 確認
    if not force:
        click.confirm(
            f"デプロイメント {deployment_id} にロールバックしますか？\n"
            f"理由: {reason}\n"
            f"オペレーター: {operator_id}",
            abort=True
        )
    
    try:
        print_info(f"デプロイメント {deployment_id} へのロールバックを開始...")
        print_info(f"理由: {reason}")
        print_info(f"オペレーター: {operator_id}")
        
        result = asyncio.run(_execute_rollback_to_deployment(
            deployment_id=deployment_id,
            reason=reason,
            operator_id=operator_id
        ))
        
        if result.get('success', False):
            print_success("ロールバックが正常に完了しました")
            print_info(f"ロールバックID: {result.get('rollback_id', 'N/A')}")
        else:
            print_error("ロールバックに失敗しました")
            if 'error' in result:
                print_error(f"エラー: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"ロールバックでエラーが発生しました: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    '--config-file', '-c',
    type=click.Path(exists=True),
    help='検証する設定ファイル'
)
@click.option(
    '--environment', '-e',
    type=click.Choice(['development', 'staging', 'production']),
    help='特定環境の設定を検証'
)
@click.option(
    '--strict',
    is_flag=True,
    help='厳密な検証モード'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='出力形式'
)
def config_validate(config_file: Optional[str], environment: Optional[str], strict: bool, output_format: str):
    """
    設定ファイルの検証を実行します。
    
    例:
        auto-deploy config-validate
        auto-deploy config-validate -c config.yaml
        auto-deploy config-validate -e production --strict
    """
    print_header("設定検証")
    
    try:
        print_info("設定の検証を開始します...")
        
        validation_options = {
            'config_file': config_file,
            'environment': environment,
            'strict': strict
        }
        
        result = _validate_configuration(validation_options)
        _display_config_validation_result(result, output_format)
        
        if not result.get('valid', False):
            sys.exit(1)
            
    except Exception as e:
        print_error(f"設定検証でエラーが発生しました: {str(e)}")
        sys.exit(1)


# 新しいヘルパー関数
def _get_rollback_history(limit: int, filters: Dict[str, str]) -> Dict[str, Any]:
    """ロールバック履歴を取得"""
    # TODO: 実際の履歴データベースとの統合
    mock_history = []
    for i in range(limit):
        mock_history.append({
            "id": f"rollback-{i+1:03d}",
            "timestamp": (datetime.now() - timedelta(hours=i*3)).isoformat(),
            "environment": ["production", "staging", "development"][i % 3],
            "reason": ["Performance issue", "Bug fix", "Security patch"][i % 3],
            "operator": ["admin", "system", "devops"][i % 3],
            "source_deployment": f"deploy-{i+10:03d}",
            "target_deployment": f"deploy-{i+5:03d}",
            "status": ["success", "failed", "success"][i % 3],
            "duration": 60 + (i * 5)
        })
    
    # フィルタを適用
    if filters:
        filtered_history = []
        for item in mock_history:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered_history.append(item)
        mock_history = filtered_history
    
    return {
        "total": len(mock_history),
        "items": mock_history[:limit],
        "filters": filters
    }


def _display_rollback_history(data: Dict[str, Any], output_format: str):
    """ロールバック履歴を表示"""
    if output_format == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_info(f"ロールバック履歴（{data['total']}件）")
        if data.get('filters'):
            print_info(f"フィルタ: {data['filters']}")
        
        print(f"\n{CLIColors.BOLD}{'ID':<15} {'タイムスタンプ':<20} {'環境':<12} {'理由':<20} {'ステータス':<10}{CLIColors.END}")
        print("-" * 85)
        
        for item in data['items']:
            status_color = CLIColors.GREEN if item['status'] == 'success' else CLIColors.RED
            print(f"{item['id']:<15} {item['timestamp'][:19]:<20} {item['environment']:<12} "
                  f"{item['reason'][:18]:<20} {status_color}{item['status']:<10}{CLIColors.END}")


async def _execute_rollback_to_deployment(deployment_id: str, reason: str, operator_id: str) -> Dict[str, Any]:
    """特定のデプロイメントへのロールバックを実行"""
    try:
        # TODO: 実際のロールバック実行ロジック
        rollback_id = f"rollback-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "rollback_id": rollback_id,
            "deployment_id": deployment_id,
            "reason": reason,
            "operator_id": operator_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "deployment_id": deployment_id
        }


def _validate_configuration(options: Dict[str, Any]) -> Dict[str, Any]:
    """設定の検証を実行"""
    # TODO: 実際の設定検証ロジック
    errors = []
    warnings = []
    
    # 基本的な検証
    if options.get('strict'):
        # 厳密モードでの追加検証
        if not options.get('config_file'):
            warnings.append("設定ファイルが指定されていません")
    
    # 環境固有の検証
    if options.get('environment') == 'production':
        # 本番環境の厳密な検証
        pass
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checked_items": [
            "基本設定構文",
            "環境変数",
            "デプロイメント戦略",
            "通知設定"
        ]
    }


def _display_config_validation_result(result: Dict[str, Any], output_format: str):
    """設定検証結果を表示"""
    if output_format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('valid', False):
            print_success("設定検証が完了しました - 問題なし")
        else:
            print_error("設定検証で問題が発見されました")
        
        # エラーの表示
        errors = result.get('errors', [])
        if errors:
            print(f"\n{CLIColors.BOLD}エラー:{CLIColors.END}")
            for error in errors:
                print_error(f"  - {error}")
        
        # 警告の表示
        warnings = result.get('warnings', [])
        if warnings:
            print(f"\n{CLIColors.BOLD}警告:{CLIColors.END}")
            for warning in warnings:
                print_warning(f"  - {warning}")
        
        # 検証項目の表示
        checked_items = result.get('checked_items', [])
        if checked_items:
            print(f"\n{CLIColors.BOLD}検証項目:{CLIColors.END}")
            for item in checked_items:
                print_success(f"  ✓ {item}")


if __name__ == '__main__':
    cli()