"""
通知マネージャーのテスト。

このモジュールは通知マネージャーの機能を包括的にテストします。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from notification_manager import NotificationManager
from base import NotificationMessage, NotificationResult, NotificationSeverity
from slack_channel import SlackChannel
from email_channel import EmailChannel


class MockChannel:
    """テスト用のモック通知チャンネル。"""
    
    def __init__(self, name: str, channel_type: str = "mock", enabled: bool = True, 
                 severity_filter: list = None, should_validate: bool = True):
        self.name = name
        self.channel_type = channel_type
        self.enabled = enabled
        self.severity_filter = severity_filter or [
            NotificationSeverity.INFO, NotificationSeverity.WARNING,
            NotificationSeverity.ERROR, NotificationSeverity.CRITICAL
        ]
        self.should_validate = should_validate
        self.send_called = False
        self.last_message = None
        self.send_result = NotificationResult(success=True, channel_name=name)
    
    def should_send(self, message: NotificationMessage) -> bool:
        return self.enabled and message.severity in self.severity_filter
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        self.send_called = True
        self.last_message = message
        return self.send_result
    
    def validate_config(self) -> bool:
        return self.should_validate


class TestNotificationManager:
    """NotificationManagerクラスのテスト。"""
    
    def test_manager_initialization_empty_config(self):
        """空の設定での初期化をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        assert manager.enabled is True
        assert len(manager.channels) == 0
    
    def test_manager_initialization_disabled(self):
        """無効化された設定での初期化をテストします。"""
        config = {'enabled': False}
        manager = NotificationManager(config)
        
        assert manager.enabled is False
    
    @patch('services.auto_deployment.notification.notification_manager.SlackChannel')
    def test_manager_initialization_with_slack(self, mock_slack_class):
        """Slackチャンネル付きの初期化をテストします。"""
        mock_slack = Mock()
        mock_slack.validate_config.return_value = True
        mock_slack_class.return_value = mock_slack
        
        config = {
            'enabled': True,
            'channels': {
                'slack-prod': {
                    'type': 'slack',
                    'webhook_url': 'https://hooks.slack.com/test',
                    'channel': '#deployments'
                }
            }
        }
        
        manager = NotificationManager(config)
        
        assert len(manager.channels) == 1
        assert 'slack-prod' in manager.channels
        mock_slack_class.assert_called_once_with('slack-prod', config['channels']['slack-prod'])
        mock_slack.validate_config.assert_called_once()
    
    @patch('services.auto_deployment.notification.notification_manager.EmailChannel')
    def test_manager_initialization_with_email(self, mock_email_class):
        """Emailチャンネル付きの初期化をテストします。"""
        mock_email = Mock()
        mock_email.validate_config.return_value = True
        mock_email_class.return_value = mock_email
        
        config = {
            'enabled': True,
            'channels': {
                'email-alerts': {
                    'type': 'email',
                    'smtp_server': 'smtp.example.com',
                    'username': 'test@example.com',
                    'password': 'password',
                    'recipients': ['admin@example.com']
                }
            }
        }
        
        manager = NotificationManager(config)
        
        assert len(manager.channels) == 1
        assert 'email-alerts' in manager.channels
        mock_email_class.assert_called_once_with('email-alerts', config['channels']['email-alerts'])
        mock_email.validate_config.assert_called_once()
    
    def test_manager_initialization_invalid_channel_type(self):
        """無効なチャンネルタイプでの初期化をテストします。"""
        config = {
            'enabled': True,
            'channels': {
                'unknown-channel': {
                    'type': 'unknown',
                    'some_config': 'value'
                }
            }
        }
        
        manager = NotificationManager(config)
        
        assert len(manager.channels) == 0  # 無効なチャンネルは追加されない
    
    def test_manager_initialization_invalid_config(self):
        """無効な設定のチャンネルでの初期化をテストします。"""
        with patch('services.auto_deployment.notification.notification_manager.SlackChannel') as mock_slack_class:
            mock_slack = Mock()
            mock_slack.validate_config.return_value = False  # 設定が無効
            mock_slack_class.return_value = mock_slack
            
            config = {
                'enabled': True,
                'channels': {
                    'invalid-slack': {
                        'type': 'slack',
                        'webhook_url': 'invalid-url'
                    }
                }
            }
            
            manager = NotificationManager(config)
            
            assert len(manager.channels) == 0  # 無効な設定のチャンネルは追加されない
    
    @pytest.mark.asyncio
    async def test_send_notification_disabled_manager(self):
        """無効化されたマネージャーでの送信をテストします。"""
        config = {'enabled': False}
        manager = NotificationManager(config)
        
        results = await manager.send_notification(
            title="テスト",
            content="無効化されたマネージャー",
            severity=NotificationSeverity.INFO
        )
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_send_notification_no_channels(self):
        """チャンネルがない場合の送信をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        results = await manager.send_notification(
            title="テスト",
            content="チャンネルなし",
            severity=NotificationSeverity.INFO
        )
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self):
        """正常な通知送信をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # モックチャンネルを手動で追加
        mock_channel = MockChannel("test-channel")
        manager.channels["test-channel"] = mock_channel
        
        results = await manager.send_notification(
            title="成功テスト",
            content="正常な送信テスト",
            severity=NotificationSeverity.INFO,
            deployment_id="deploy-123",
            environment="production",
            metadata={'version': '1.0.0'}
        )
        
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].channel_name == "test-channel"
        assert mock_channel.send_called is True
        
        # 送信されたメッセージの確認
        sent_message = mock_channel.last_message
        assert sent_message.title == "成功テスト"
        assert sent_message.content == "正常な送信テスト"
        assert sent_message.severity == NotificationSeverity.INFO
        assert sent_message.deployment_id == "deploy-123"
        assert sent_message.environment == "production"
        assert sent_message.metadata['version'] == '1.0.0'
    
    @pytest.mark.asyncio
    async def test_send_notification_severity_filtering(self):
        """重要度フィルタリングをテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # エラーのみを受け入れるチャンネル
        error_only_channel = MockChannel(
            "error-only", 
            severity_filter=[NotificationSeverity.ERROR, NotificationSeverity.CRITICAL]
        )
        manager.channels["error-only"] = error_only_channel
        
        # 情報メッセージを送信（フィルタリングされるはず）
        results = await manager.send_notification(
            title="情報メッセージ",
            content="これは情報メッセージです",
            severity=NotificationSeverity.INFO
        )
        
        assert len(results) == 0  # フィルタリングされて送信されない
        assert error_only_channel.send_called is False
    
    @pytest.mark.asyncio
    async def test_send_notification_specific_channels(self):
        """特定のチャンネルへの送信をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # 複数のチャンネルを追加
        channel1 = MockChannel("channel1")
        channel2 = MockChannel("channel2")
        channel3 = MockChannel("channel3")
        
        manager.channels["channel1"] = channel1
        manager.channels["channel2"] = channel2
        manager.channels["channel3"] = channel3
        
        # 特定のチャンネルのみに送信
        results = await manager.send_notification(
            title="特定チャンネルテスト",
            content="特定のチャンネルのみ",
            severity=NotificationSeverity.INFO,
            channels=["channel1", "channel3"]
        )
        
        assert len(results) == 2
        assert channel1.send_called is True
        assert channel2.send_called is False  # 指定されていない
        assert channel3.send_called is True
    
    @pytest.mark.asyncio
    async def test_send_notification_nonexistent_channel(self):
        """存在しないチャンネルの指定をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        channel1 = MockChannel("channel1")
        manager.channels["channel1"] = channel1
        
        # 存在しないチャンネルを含む指定
        results = await manager.send_notification(
            title="存在しないチャンネルテスト",
            content="存在しないチャンネル指定",
            severity=NotificationSeverity.INFO,
            channels=["channel1", "nonexistent"]
        )
        
        assert len(results) == 1  # 存在するチャンネルのみ
        assert results[0].channel_name == "channel1"
        assert channel1.send_called is True
    
    @pytest.mark.asyncio
    async def test_send_notification_channel_error(self):
        """チャンネルでのエラー処理をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # エラーを返すチャンネル
        error_channel = MockChannel("error-channel")
        error_channel.send_result = NotificationResult(
            success=False,
            channel_name="error-channel",
            error_message="送信エラー"
        )
        manager.channels["error-channel"] = error_channel
        
        results = await manager.send_notification(
            title="エラーテスト",
            content="チャンネルエラー",
            severity=NotificationSeverity.ERROR
        )
        
        assert len(results) == 1
        assert results[0].success is False
        assert results[0].error_message == "送信エラー"
    
    def test_get_channel_status(self):
        """チャンネルステータスの取得をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # モックチャンネルを追加
        channel1 = MockChannel("channel1", "mock", True, [NotificationSeverity.INFO])
        channel2 = MockChannel("channel2", "mock", False, [NotificationSeverity.ERROR])
        
        manager.channels["channel1"] = channel1
        manager.channels["channel2"] = channel2
        
        status = manager.get_channel_status()
        
        assert len(status) == 2
        assert status["channel1"]["name"] == "channel1"
        assert status["channel1"]["enabled"] is True
        assert status["channel1"]["config_valid"] is True
        assert status["channel2"]["enabled"] is False
    
    def test_add_channel(self):
        """チャンネルの追加をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        new_channel = MockChannel("new-channel")
        result = manager.add_channel("new-channel", new_channel)
        
        assert result is True
        assert "new-channel" in manager.channels
        assert manager.channels["new-channel"] == new_channel
    
    def test_add_channel_invalid_config(self):
        """無効な設定のチャンネル追加をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        invalid_channel = MockChannel("invalid-channel", should_validate=False)
        result = manager.add_channel("invalid-channel", invalid_channel)
        
        assert result is False
        assert "invalid-channel" not in manager.channels
    
    def test_remove_channel(self):
        """チャンネルの削除をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        channel = MockChannel("remove-me")
        manager.channels["remove-me"] = channel
        
        result = manager.remove_channel("remove-me")
        
        assert result is True
        assert "remove-me" not in manager.channels
    
    def test_remove_nonexistent_channel(self):
        """存在しないチャンネルの削除をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        result = manager.remove_channel("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_test_channels(self):
        """チャンネルテスト機能をテストします。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # テスト用チャンネルを追加
        test_channel = MockChannel("test-channel")
        manager.channels["test-channel"] = test_channel
        
        results = await manager.test_channels()
        
        assert len(results) == 1
        assert results[0].success is True
        assert test_channel.send_called is True
        
        # テストメッセージの確認
        sent_message = test_channel.last_message
        assert "Test" in sent_message.title
        assert sent_message.metadata['test'] is True
        assert sent_message.deployment_id == "test-deployment"