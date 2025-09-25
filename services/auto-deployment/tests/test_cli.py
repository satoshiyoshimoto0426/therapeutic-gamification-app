"""
CLI インターフェースのユニットテスト

Requirements: 1.1, 1.2
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner
from datetime import datetime, timedelta

import sys
import os

# 現在のディレクトリから親ディレクトリのモジュールをインポート
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from cli import cli, CLIColors
from config import Environment, DeploymentStrategy


class TestCLICommands:
    """CLI コマンドのテスト"""
    
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


class TestDeployCommand:
    """deploy コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
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
    
    @patch('cli._execute_deployment')
    def test_deploy_success(self, mock_execute):
        """正常なデプロイメントテスト"""
        # モックの設定
        mock_result = Mock()
        mock_result.is_success = True
        mock_result.deployment_id = 'test-deploy-001'
        mock_result.status.value = 'success'
        mock_result.environment.value = 'development'
        mock_result.start_time = datetime.now()
        mock_result.end_time = datetime.now() + timedelta(minutes=5)
        mock_result.duration_seconds = 300.0
        mock_result.service_url = 'https://test.example.com'
        mock_result.steps_completed = ['validation', 'build', 'deploy']
        mock_result.steps_failed = []
        mock_result.error = None
        
        mock_execute.return_value = mock_result
        
        result = self.runner.invoke(cli, ['deploy', '-e', 'development'])
        assert result.exit_code == 0
        assert 'デプロイメント結果' in result.output
        assert 'test-deploy-001' in result.output
    
    @patch('cli._execute_deployment')
    def test_deploy_failure(self, mock_execute):
        """デプロイメント失敗テスト"""
        # モックの設定
        mock_result = Mock()
        mock_result.is_success = False
        mock_result.deployment_id = 'test-deploy-002'
        mock_result.status.value = 'failed'
        mock_result.environment.value = 'development'
        mock_result.start_time = datetime.now()
        mock_result.end_time = datetime.now() + timedelta(minutes=2)
        mock_result.duration_seconds = 120.0
        mock_result.service_url = None
        mock_result.steps_completed = ['validation']
        mock_result.steps_failed = ['build']
        mock_result.error = Mock()
        mock_result.error.message = 'Build failed'
        
        mock_execute.return_value = mock_result
        
        result = self.runner.invoke(cli, ['deploy', '-e', 'development'])
        assert result.exit_code == 1
        assert 'Build failed' in result.output
    
    def test_deploy_dry_run(self):
        """ドライランモードテスト"""
        with patch('cli._execute_deployment') as mock_execute:
            mock_result = Mock()
            mock_result.is_success = True
            mock_execute.return_value = mock_result
            
            result = self.runner.invoke(cli, ['deploy', '-e', 'development', '--dry-run'])
            assert 'ドライランモード' in result.output
    
    def test_deploy_json_output(self):
        """JSON出力形式テスト"""
        with patch('cli._execute_deployment') as mock_execute:
            mock_result = Mock()
            mock_result.is_success = True
            mock_result.to_dict.return_value = {'status': 'success', 'id': 'test-001'}
            mock_execute.return_value = mock_result
            
            result = self.runner.invoke(cli, ['deploy', '-e', 'development', '--output-format', 'json'])
            assert result.exit_code == 0
            # JSON形式の出力を確認
            try:
                json.loads(result.output.split('\n')[-2])  # 最後の行はJSONのはず
            except (json.JSONDecodeError, IndexError):
                pytest.fail("JSON出力が正しくありません")


class TestStatusCommand:
    """status コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_status_help(self):
        """status コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['status', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメントの状態を確認します' in result.output
    
    @patch('cli._get_overall_status')
    def test_status_overall(self, mock_get_status):
        """全体状態確認テスト"""
        mock_get_status.return_value = {'overall_status': 'healthy'}
        
        result = self.runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert '全体の状態を確認中' in result.output
    
    @patch('cli._get_environment_status')
    def test_status_environment(self, mock_get_status):
        """環境状態確認テスト"""
        mock_get_status.return_value = {'environment': 'production', 'status': 'healthy'}
        
        result = self.runner.invoke(cli, ['status', '-e', 'production'])
        assert result.exit_code == 0
        assert '環境: production の状態を確認中' in result.output
    
    @patch('cli._get_deployment_status')
    def test_status_deployment_id(self, mock_get_status):
        """デプロイメントID指定状態確認テスト"""
        mock_get_status.return_value = {'deployment_id': 'test-001', 'status': 'success'}
        
        result = self.runner.invoke(cli, ['status', '--deployment-id', 'test-001'])
        assert result.exit_code == 0
        assert 'デプロイメントID: test-001 の状態を確認中' in result.output


class TestRollbackCommand:
    """rollback コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_rollback_help(self):
        """rollback コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback', '--help'])
        assert result.exit_code == 0
        assert '指定された環境を前回の安定版にロールバックします' in result.output
    
    def test_rollback_missing_required_options(self):
        """必須オプション不足テスト"""
        result = self.runner.invoke(cli, ['rollback'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output
    
    @patch('cli._execute_manual_rollback')
    def test_rollback_success(self, mock_execute):
        """正常なロールバックテスト"""
        mock_execute.return_value = {
            'success': True,
            'trigger_id': 'rollback-001',
            'request': {
                'reason': 'test',
                'severity': 'warning',
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'test-user'
            }
        }
        
        result = self.runner.invoke(cli, [
            'rollback', '-e', 'staging', '-r', 'Test rollback', '--force'
        ])
        assert result.exit_code == 0
        assert '手動ロールバック要求が正常に作成されました' in result.output
    
    @patch('cli._execute_manual_rollback')
    def test_rollback_failure(self, mock_execute):
        """ロールバック失敗テスト"""
        mock_execute.return_value = {
            'success': False,
            'error': 'Rollback failed',
            'message': 'System error occurred'
        }
        
        result = self.runner.invoke(cli, [
            'rollback', '-e', 'staging', '-r', 'Test rollback', '--force'
        ])
        assert result.exit_code == 1
        assert '手動ロールバック要求の作成に失敗しました' in result.output
    
    def test_rollback_emergency_mode(self):
        """緊急ロールバックモードテスト"""
        with patch('cli._execute_manual_rollback') as mock_execute:
            mock_execute.return_value = {'success': True, 'trigger_id': 'emergency-001'}
            
            result = self.runner.invoke(cli, [
                'rollback', '-e', 'production', '-r', 'Emergency rollback', '--emergency'
            ])
            assert '緊急ロールバックモード' in result.output


class TestConfigCommand:
    """config コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_config_help(self):
        """config コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0
        assert '現在の設定を表示します' in result.output
    
    @patch('cli.default_config_manager')
    def test_config_display(self, mock_config_manager):
        """設定表示テスト"""
        mock_config = Mock()
        mock_config_manager.get_config.return_value = mock_config
        
        result = self.runner.invoke(cli, ['config'])
        assert result.exit_code == 0
        assert '設定情報表示' in result.output


class TestValidateCommand:
    """validate コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_validate_help(self):
        """validate コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメント前の検証を実行します' in result.output
    
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


class TestMonitorCommand:
    """monitor コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_monitor_help(self):
        """monitor コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['monitor', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメントとシステムの監視を実行します' in result.output
    
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


class TestHistoryCommand:
    """history コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_history_help(self):
        """history コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['history', '--help'])
        assert result.exit_code == 0
        assert 'デプロイメント履歴を表示します' in result.output
    
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
    
    @patch('cli._get_deployment_history')
    def test_history_with_filters(self, mock_get_history):
        """フィルタ付き履歴表示テスト"""
        mock_get_history.return_value = {
            'total': 1,
            'items': [],
            'filters': {'environment': 'production', 'status': 'success'}
        }
        
        result = self.runner.invoke(cli, [
            'history', '-e', 'production', '--status-filter', 'success'
        ])
        assert result.exit_code == 0


class TestConfigSetCommand:
    """config-set コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_config_set_help(self):
        """config-set コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['config-set', '--help'])
        assert result.exit_code == 0
        assert '設定値を設定または表示します' in result.output
    
    def test_config_set_missing_key(self):
        """キー指定なしエラーテスト"""
        result = self.runner.invoke(cli, ['config-set'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output
    
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
    
    def test_config_set_bool_type(self):
        """ブール型設定テスト"""
        with patch('cli._set_config_value') as mock_set:
            result = self.runner.invoke(cli, [
                'config-set', '-k', 'monitoring.enabled', '-v', 'true', '--type', 'bool'
            ])
            assert result.exit_code == 0
            # ブール値がTrueとして解析されることを確認
            mock_set.assert_called_once()
            args = mock_set.call_args[0]
            assert args[1] is True


class TestRollbackStatusCommand:
    """rollback-status コマンドのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_rollback_status_help(self):
        """rollback-status コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback-status', '--help'])
        assert result.exit_code == 0
        assert 'ロールバックシステムの状態と履歴を表示します' in result.output
    
    @patch('cli._get_rollback_status')
    def test_rollback_status_display(self, mock_get_status):
        """ロールバック状態表示テスト"""
        mock_get_status.return_value = {
            'timestamp': datetime.now().isoformat(),
            'manual_rollback': {
                'active': False,
                'config': {'enabled': True, 'cooldown_minutes': 5},
                'recent_rollbacks': 0,
                'can_rollback': True
            },
            'failure_detection': {
                'monitoring_active': False,
                'total_conditions': 4,
                'enabled_conditions': 4
            },
            'system_health': {
                'overall_status': 'healthy',
                'active_monitoring': False
            }
        }
        
        result = self.runner.invoke(cli, ['rollback-status'])
        assert result.exit_code == 0
        assert 'ロールバックシステム状態' in result.output


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
    
    def test_dataclass_to_dict(self):
        """DataClass辞書変換テスト"""
        from cli import _dataclass_to_dict
        from dataclasses import dataclass
        from enum import Enum
        
        class TestEnum(Enum):
            VALUE = 'test_value'
        
        @dataclass
        class TestClass:
            string_field: str = 'test'
            enum_field: TestEnum = TestEnum.VALUE
        
        obj = TestClass()
        result = _dataclass_to_dict(obj)
        
        assert result['string_field'] == 'test'
        assert result['enum_field'] == 'test_value'


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


if __name__ == '__main__':
    pytest.main([__file__])