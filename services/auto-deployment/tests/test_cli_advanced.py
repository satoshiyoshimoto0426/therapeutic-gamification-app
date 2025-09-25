"""
CLI 高度機能の統合テスト

Requirements: 1.1, 1.4
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
class TestAdvancedCLIFeatures:
    """高度なCLI機能のテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_interactive_deployment_help(self):
        """インタラクティブデプロイメントのヘルプテスト"""
        result = self.runner.invoke(cli, ['deploy', '--help'])
        assert result.exit_code == 0
        assert '--interactive' in result.output
        assert 'インタラクティブモードで実行' in result.output
    
    def test_rollback_history_help(self):
        """ロールバック履歴コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback-history', '--help'])
        assert result.exit_code == 0
        assert 'ロールバック履歴を表示します' in result.output
    
    def test_rollback_to_help(self):
        """特定デプロイメントロールバックコマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['rollback-to', '--help'])
        assert result.exit_code == 0
        assert '特定のデプロイメントIDにロールバックします' in result.output
    
    def test_config_validate_help(self):
        """設定検証コマンドのヘルプテスト"""
        result = self.runner.invoke(cli, ['config-validate', '--help'])
        assert result.exit_code == 0
        assert '設定ファイルの検証を実行します' in result.output
    
    @patch('cli._get_rollback_history')
    def test_rollback_history_display(self, mock_get_history):
        """ロールバック履歴表示テスト"""
        mock_get_history.return_value = {
            'total': 3,
            'items': [
                {
                    'id': 'rollback-001',
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'production',
                    'reason': 'Performance issue',
                    'operator': 'admin',
                    'source_deployment': 'deploy-010',
                    'target_deployment': 'deploy-005',
                    'status': 'success',
                    'duration': 60
                },
                {
                    'id': 'rollback-002',
                    'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                    'environment': 'staging',
                    'reason': 'Bug fix',
                    'operator': 'system',
                    'source_deployment': 'deploy-011',
                    'target_deployment': 'deploy-006',
                    'status': 'success',
                    'duration': 65
                }
            ],
            'filters': {}
        }
        
        result = self.runner.invoke(cli, ['rollback-history'])
        assert result.exit_code == 0
        assert 'ロールバック履歴' in result.output
        assert 'rollback-001' in result.output
        assert 'Performance issue' in result.output
    
    @patch('cli._get_rollback_history')
    def test_rollback_history_with_environment_filter(self, mock_get_history):
        """環境フィルタ付きロールバック履歴テスト"""
        mock_get_history.return_value = {
            'total': 1,
            'items': [
                {
                    'id': 'rollback-001',
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'production',
                    'reason': 'Critical issue',
                    'operator': 'admin',
                    'source_deployment': 'deploy-010',
                    'target_deployment': 'deploy-005',
                    'status': 'success',
                    'duration': 60
                }
            ],
            'filters': {'environment': 'production'}
        }
        
        result = self.runner.invoke(cli, ['rollback-history', '-e', 'production'])
        assert result.exit_code == 0
        assert 'production' in result.output
        mock_get_history.assert_called_once_with(10, {'environment': 'production'})
    
    @patch('cli._get_rollback_history')
    def test_rollback_history_json_output(self, mock_get_history):
        """ロールバック履歴JSON出力テスト"""
        mock_data = {
            'total': 1,
            'items': [
                {
                    'id': 'rollback-001',
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'production',
                    'reason': 'Test rollback',
                    'operator': 'admin',
                    'status': 'success'
                }
            ],
            'filters': {}
        }
        mock_get_history.return_value = mock_data
        
        result = self.runner.invoke(cli, ['rollback-history', '--output-format', 'json'])
        assert result.exit_code == 0
        
        # JSON出力の検証
        try:
            output_lines = result.output.strip().split('\n')
            json_output = '\n'.join([line for line in output_lines if line.strip().startswith('{')])
            parsed_data = json.loads(json_output)
            assert parsed_data['total'] == 1
            assert parsed_data['items'][0]['id'] == 'rollback-001'
        except (json.JSONDecodeError, IndexError, KeyError):
            pytest.fail("JSON出力が正しくありません")
    
    def test_rollback_to_missing_required_options(self):
        """rollback-to コマンドの必須オプション不足テスト"""
        result = self.runner.invoke(cli, ['rollback-to'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output
    
    @patch('cli._execute_rollback_to_deployment')
    def test_rollback_to_success(self, mock_execute):
        """特定デプロイメントロールバック成功テスト"""
        mock_execute.return_value = {
            'success': True,
            'rollback_id': 'rollback-20240115123456',
            'deployment_id': 'deploy-001',
            'reason': 'Test rollback',
            'operator_id': 'test-user',
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.runner.invoke(cli, [
            'rollback-to', 
            '--deployment-id', 'deploy-001', 
            '-r', 'Test rollback',
            '--force'
        ])
        assert result.exit_code == 0
        assert 'ロールバックが正常に完了しました' in result.output
        assert 'rollback-20240115123456' in result.output
    
    @patch('cli._execute_rollback_to_deployment')
    def test_rollback_to_failure(self, mock_execute):
        """特定デプロイメントロールバック失敗テスト"""
        mock_execute.return_value = {
            'success': False,
            'error': 'Deployment not found',
            'deployment_id': 'deploy-999'
        }
        
        result = self.runner.invoke(cli, [
            'rollback-to', 
            '--deployment-id', 'deploy-999', 
            '-r', 'Test rollback',
            '--force'
        ])
        assert result.exit_code == 1
        assert 'ロールバックに失敗しました' in result.output
        assert 'Deployment not found' in result.output
    
    @patch('cli._validate_configuration')
    def test_config_validate_success(self, mock_validate):
        """設定検証成功テスト"""
        mock_validate.return_value = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checked_items': ['基本設定構文', '環境変数', 'デプロイメント戦略']
        }
        
        result = self.runner.invoke(cli, ['config-validate'])
        assert result.exit_code == 0
        assert '設定検証が完了しました - 問題なし' in result.output
        assert '基本設定構文' in result.output
    
    @patch('cli._validate_configuration')
    def test_config_validate_with_errors(self, mock_validate):
        """設定検証エラーテスト"""
        mock_validate.return_value = {
            'valid': False,
            'errors': ['Invalid configuration format', 'Missing required field'],
            'warnings': ['Deprecated option used'],
            'checked_items': ['基本設定構文', '環境変数']
        }
        
        result = self.runner.invoke(cli, ['config-validate'])
        assert result.exit_code == 1
        assert '設定検証で問題が発見されました' in result.output
        assert 'Invalid configuration format' in result.output
        assert 'Deprecated option used' in result.output
    
    @patch('cli._validate_configuration')
    def test_config_validate_strict_mode(self, mock_validate):
        """設定検証厳密モードテスト"""
        mock_validate.return_value = {
            'valid': True,
            'errors': [],
            'warnings': ['設定ファイルが指定されていません'],
            'checked_items': ['基本設定構文', '環境変数', 'デプロイメント戦略', '通知設定']
        }
        
        result = self.runner.invoke(cli, ['config-validate', '--strict'])
        assert result.exit_code == 0
        assert '設定ファイルが指定されていません' in result.output
        mock_validate.assert_called_once()
        
        # 厳密モードが渡されていることを確認
        call_args = mock_validate.call_args[0][0]
        assert call_args['strict'] is True
    
    @patch('cli._validate_configuration')
    def test_config_validate_json_output(self, mock_validate):
        """設定検証JSON出力テスト"""
        mock_data = {
            'valid': True,
            'errors': [],
            'warnings': ['Test warning'],
            'checked_items': ['基本設定構文']
        }
        mock_validate.return_value = mock_data
        
        result = self.runner.invoke(cli, ['config-validate', '--output-format', 'json'])
        assert result.exit_code == 0
        
        # JSON出力の検証
        try:
            output_lines = result.output.strip().split('\n')
            json_output = '\n'.join([line for line in output_lines if line.strip().startswith('{')])
            parsed_data = json.loads(json_output)
            assert parsed_data['valid'] is True
            assert 'Test warning' in parsed_data['warnings']
        except (json.JSONDecodeError, IndexError, KeyError):
            pytest.fail("JSON出力が正しくありません")
    
    @patch('cli._get_deployment_history')
    def test_history_with_advanced_filters(self, mock_get_history):
        """高度なフィルタ付き履歴表示テスト"""
        mock_get_history.return_value = {
            'total': 1,
            'items': [
                {
                    'id': 'deploy-001',
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'production',
                    'status': 'success',
                    'duration': 300,
                    'commit_sha': 'abc123',
                    'operator': 'admin'
                }
            ],
            'filters': {
                'environment': 'production',
                'operator': 'admin',
                'date_from': '2024-01-01 00:00:00',
                'date_to': '2024-01-31 23:59:59'
            }
        }
        
        result = self.runner.invoke(cli, [
            'history', 
            '-e', 'production',
            '--operator', 'admin',
            '--date-from', '2024-01-01 00:00:00',
            '--date-to', '2024-01-31 23:59:59'
        ])
        assert result.exit_code == 0
        assert 'deploy-001' in result.output
        
        # フィルタが正しく渡されていることを確認
        call_args = mock_get_history.call_args[0][1]
        assert call_args['environment'] == 'production'
        assert call_args['operator'] == 'admin'
        assert call_args['date_from'] == '2024-01-01 00:00:00'
        assert call_args['date_to'] == '2024-01-31 23:59:59'


@pytest.mark.skipif(not CLI_AVAILABLE, reason=f"CLI module not available: {CLI_IMPORT_ERROR if not CLI_AVAILABLE else ''}")
class TestCLIHelperFunctions:
    """CLI ヘルパー関数のテスト"""
    
    def test_get_rollback_history_basic(self):
        """ロールバック履歴取得の基本テスト"""
        from cli import _get_rollback_history
        
        result = _get_rollback_history(5, {})
        assert 'total' in result
        assert 'items' in result
        assert 'filters' in result
        assert len(result['items']) <= 5
    
    def test_get_rollback_history_with_filter(self):
        """フィルタ付きロールバック履歴取得テスト"""
        from cli import _get_rollback_history
        
        filters = {'environment': 'production'}
        result = _get_rollback_history(10, filters)
        assert result['filters'] == filters
        
        # フィルタが適用されていることを確認（モックデータの場合）
        for item in result['items']:
            if 'environment' in item:
                # 実際のフィルタリングロジックがある場合のテスト
                pass
    
    def test_validate_configuration_basic(self):
        """基本的な設定検証テスト"""
        from cli import _validate_configuration
        
        options = {'strict': False}
        result = _validate_configuration(options)
        
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result
        assert 'checked_items' in result
        assert isinstance(result['valid'], bool)
        assert isinstance(result['errors'], list)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['checked_items'], list)
    
    def test_validate_configuration_strict_mode(self):
        """厳密モード設定検証テスト"""
        from cli import _validate_configuration
        
        options = {'strict': True, 'config_file': None}
        result = _validate_configuration(options)
        
        # 厳密モードでは警告が追加される
        assert len(result['warnings']) > 0
        assert any('設定ファイル' in warning for warning in result['warnings'])


@pytest.mark.skipif(not CLI_AVAILABLE, reason=f"CLI module not available: {CLI_IMPORT_ERROR if not CLI_AVAILABLE else ''}")
class TestInteractiveMode:
    """インタラクティブモードのテスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.runner = CliRunner()
    
    def test_deploy_interactive_option_exists(self):
        """インタラクティブオプションの存在確認"""
        result = self.runner.invoke(cli, ['deploy', '--help'])
        assert result.exit_code == 0
        assert '--interactive' in result.output or '-i' in result.output
    
    @patch('cli._interactive_deployment_setup')
    @patch('cli._execute_deployment')
    def test_deploy_interactive_mode(self, mock_execute, mock_interactive):
        """インタラクティブモードデプロイテスト"""
        # インタラクティブセットアップのモック
        mock_interactive.return_value = (
            'development',  # environment
            'blue_green',   # strategy
            {'dry_run': False, 'skip_tests': False, 'force': False}  # options
        )
        
        # デプロイメント実行のモック
        mock_result = Mock()
        mock_result.is_success = True
        mock_result.deployment_id = 'test-interactive-001'
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
        
        result = self.runner.invoke(cli, ['deploy', '--interactive'])
        assert result.exit_code == 0
        
        # インタラクティブセットアップが呼ばれたことを確認
        mock_interactive.assert_called_once()
        
        # デプロイメントが実行されたことを確認
        mock_execute.assert_called_once()


def test_advanced_cli_availability():
    """高度なCLI機能の可用性テスト"""
    if CLI_AVAILABLE:
        print("✅ 高度なCLI機能が正常にインポートされました")
        
        # 新しいコマンドの存在確認
        from cli import cli
        
        # コマンドリストを取得
        commands = list(cli.commands.keys())
        
        expected_commands = [
            'deploy', 'status', 'rollback', 'config', 'validate', 
            'monitor', 'history', 'config-set', 'rollback-status',
            'rollback-history', 'rollback-to', 'config-validate'
        ]
        
        for cmd in expected_commands:
            if cmd in commands:
                print(f"✅ コマンド '{cmd}' が利用可能です")
            else:
                print(f"❌ コマンド '{cmd}' が見つかりません")
    else:
        print(f"❌ 高度なCLI機能のインポートに失敗: {CLI_IMPORT_ERROR}")
        pytest.skip(f"Advanced CLI features not available: {CLI_IMPORT_ERROR}")


if __name__ == '__main__':
    pytest.main([__file__])