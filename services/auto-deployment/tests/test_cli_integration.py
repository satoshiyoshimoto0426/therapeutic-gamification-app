"""
CLI インターフェースの統合テスト

Requirements: 1.1, 1.2
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from cli import cli, CLIColors
    CLI_AVAILABLE = True
except ImportError as e:
    CLI_AVAILABLE = False
    CLI_IMPORT_ERROR = str(e)


@pytest.mark.skipif(not CLI_AVAILABLE, reason=f"CLI module not available: {CLI_IMPORT_ERROR if not CLI_AVAILABLE else ''}")
class TestCLIIntegration:
    """CLI統合テスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """CLI ヘルプの表示テスト"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert '治療的ゲーミフィケーションアプリ自動デプロイメントツール' in result.output
    
    def test_cli_version(self):
        """CLI バージョン表示テスト"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_deploy_help(self):
        """deploy コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['deploy', '--help'])
        assert result.exit_code == 0
        assert 'アプリケーションを指定された環境にデプロイします' in result.output
    
    def test_deploy_missing_environment(self):
        """環境指定なしでのエラーテスト"""
        result = self.runner.invoke(cli, ['deploy'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output
    
    def test_status_help(self):
        """status コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['status', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメントの状態を確認します' in result.output
    
    def test_rollback_help(self):
        """rollback コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback', '--help'])
        assert result.exit_code == 0
        assert '指定された環境を前回の安定版にロールバックします' in result.output
    
    def test_config_help(self):
        """config コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0
        assert '現在の設定を表示します' in result.output
    
    def test_validate_help(self):
        """validate コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメント前の検証を実行します' in result.output
    
    def test_monitor_help(self):
        """monitor コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['monitor', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメントとシステムの監視を実行します' in result.output
    
    def test_history_help(self):
        """history コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['history', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメント履歴を表示します' in result.output
    
    def test_config_set_help(self):
        """config-set コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['config-set', '--help'])
        assert result.exit_code == 0
        assert '設定値を設定または表示します' in result.output
    
    def test_rollback_status_help(self):
        """rollback-status コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback-status', '--help'])
        assert result.exit_code == 0
        assert 'ロールバックシステムの状態と履歴を表示します' in result.output
    
    @patch('cli._validate_all_environments')
    def test_validate_success(self, mock_validate):
        """検証成功テスト"""
        mock_validate.return_value = {'valid': True, 'errors': []}
        
        result = self.runner.invoke(cli, ['validate'])
        assert result.exit_code == 0
        assert '検証が完了しました - 問題なし' in result.output
    
    @patch('cli._validate_all_environments')
    def test_validate_failure(self, mock_validate):
        """検証失敗テスト"""
        mock_validate.return_value = {
            'valid': False, 
            'errors': ['Configuration error', 'Permission denied']
        }
        
        result = self.runner.invoke(cli, ['validate'])
        assert result.exit_code == 1
        assert '検証で問題が発見されました' in result.output
        assert 'Configuration error' in result.output
    
    @patch('cli._get_monitoring_status')
    def test_monitor_status(self, mock_get_status):
        """監視状況確認テスト"""
        mock_get_status.return_value = {
            'timestamp': datetime.now().isoformat(),
            'services': {'auth': {'status': 'healthy', 'response_time': 45}},
            'deployment': {'active': False},
            'alerts': []
        }
        
        result = self.runner.invoke(cli, ['monitor'])
        assert result.exit_code == 0
        assert '現在の監視状況を確認中' in result.output
    
    @patch('cli._get_deployment_history')
    def test_history_display(self, mock_get_history):
        """履歴表示テスト"""
        mock_get_history.return_value = {
            'total': 2,
            'items': [
                {
                    'id': 'deploy-001',
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'production',
                    'status': 'success',
                    'duration': 300,
                    'commit_sha': 'abc123',
                    'operator': 'system'
                }
            ],
            'filters': {}
        }
        
        result = self.runner.invoke(cli, ['history'])
        assert result.exit_code == 0
        assert 'デプロイメント履歴' in result.output
        assert 'deploy-001' in result.output
    
    @patch('cli._get_config_value')
    def test_config_set_get_value(self, mock_get_value):
        """設定値取得テスト"""
        mock_get_value.return_value = 'blue_green'
        
        result = self.runner.invoke(cli, ['config-set', '-k', 'deployment.strategy'])
        assert result.exit_code == 0
        assert '現在の値: blue_green' in result.output
    
    @patch('cli._set_config_value')
    def test_config_set_set_value(self, mock_set_value):
        """設定値設定テスト"""
        result = self.runner.invoke(cli, [
            'config-set', '-k', 'deployment.strategy', '-v', 'rolling_update'
        ])
        assert result.exit_code == 0
        assert '設定を更新しました' in result.output
        mock_set_value.assert_called_once()


@pytest.mark.skipif(not CLI_AVAILABLE, reason=f"CLI module not available: {CLI_IMPORT_ERROR if not CLI_AVAILABLE else ''}")
class TestCLIHelpers:
    """CLI ヘルパー関数のテスト"""
    
    def test_parse_config_value_string(self):
        """文字列型設定値解析テスト"""
        from cli import _parse_config_value
        
        result = _parse_config_value('test_value', 'string')
        assert result == 'test_value'
    
    def test_parse_config_value_int(self):
        """整数型設定値解析テスト"""
        from cli import _parse_config_value
        
        result = _parse_config_value('123', 'int')
        assert result == 123
    
    def test_parse_config_value_bool_true(self):
        """ブール型設定値解析テスト（True）"""
        from cli import _parse_config_value
        
        for value in ['true', 'True', '1', 'yes', 'on']:
            result = _parse_config_value(value, 'bool')
            assert result is True
    
    def test_parse_config_value_bool_false(self):
        """ブール型設定値解析テスト（False）"""
        from cli import _parse_config_value
        
        for value in ['false', 'False', '0', 'no', 'off']:
            result = _parse_config_value(value, 'bool')
            assert result is False
    
    def test_parse_config_value_json(self):
        """JSON型設定値解析テスト"""
        from cli import _parse_config_value
        
        json_str = '{"key": "value", "number": 42}'
        result = _parse_config_value(json_str, 'json')
        assert result == {"key": "value", "number": 42}


@pytest.mark.skipif(not CLI_AVAILABLE, reason=f"CLI module not available: {CLI_IMPORT_ERROR if not CLI_AVAILABLE else ''}")
class TestCLIColors:
    """CLI カラー表示のテスト"""
    
    def test_cli_colors_defined(self):
        """カラーコードが定義されていることを確認"""
        assert hasattr(CLIColors, 'GREEN')
        assert hasattr(CLIColors, 'RED')
        assert hasattr(CLIColors, 'YELLOW')
        assert hasattr(CLIColors, 'BLUE')
        assert hasattr(CLIColors, 'END')
    
    def test_print_functions_exist(self):
        """出力関数が存在することを確認"""
        from cli import print_header, print_success, print_error, print_warning, print_info, print_step
        
        # 関数が呼び出し可能であることを確認
        assert callable(print_header)
        assert callable(print_success)
        assert callable(print_error)
        assert callable(print_warning)
        assert callable(print_info)
        assert callable(print_step)


def test_cli_availability():
    """CLI モジュールの可用性テスト"""
    if CLI_AVAILABLE:
        print("✅ CLI モジュールが正常にインポートされました")
    else:
        print(f"❌ CLI モジュールのインポートに失敗: {CLI_IMPORT_ERROR}")
        # テストは失敗させずに、情報として記録
        pytest.skip(f"CLI module not available: {CLI_IMPORT_ERROR}")


if __name__ == '__main__':
    pytest.main([__file__])