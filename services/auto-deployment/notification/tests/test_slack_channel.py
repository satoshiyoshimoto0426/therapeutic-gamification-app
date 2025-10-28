"""
Slack通知チャンネルのテスト。

このモジュールはSlack統合機能の包括的なテストを提供します。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from slack_channel import SlackChannel
from base import NotificationMessage, NotificationSeverity


class TestSlackChannel:
    """SlackChannelクラスのテスト。"""
    
    def test_slack_channel_initialization(self):
        """Slackチャンネルの初期化をテストします。"""
        config = {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'channel': '#deployments',
            'username': 'Deploy Bot',
            'icon_emoji': ':rocket:',
            'severity_filter': ['info', 'warning', 'error', 'critical']
        }
        
        channel = SlackChannel("slack-test", config)
        
        assert channel.name == "slack-test"
        assert channel.webhook_url == config['webhook_url']
        assert channel.channel == '#deployments'
        assert channel.username == 'Deploy Bot'
        assert channel.icon_emoji == ':rocket:'
        assert channel.enabled is True
    
    def test_slack_channel_default_values(self):
        """Slackチャンネルのデフォルト値をテストします。"""
        config = {
            'type': 'slack',
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        channel = SlackChannel("slack-default", config)
        
        assert channel.channel == '#deployments'
        assert channel.username == 'Auto-Deploy Bot'
        assert channel.icon_emoji == ':robot_face:'
    
    def test_config_validation_success(self):
        """有効な設定の検証をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/VALID/WEBHOOK/URL'
        }
        
        with patch('services.auto_deployment.notification.slack_channel.aiohttp', Mock()):
            channel = SlackChannel("valid-slack", config)
            assert channel.validate_config() is True
    
    def test_config_validation_missing_webhook(self):
        """webhook_urlが欠如している場合の検証をテストします。"""
        config = {}
        
        channel = SlackChannel("invalid-slack", config)
        assert channel.validate_config() is False
    
    def test_config_validation_invalid_webhook_format(self):
        """無効なwebhook URL形式の検証をテストします。"""
        config = {
            'webhook_url': 'https://invalid.webhook.url'
        }
        
        channel = SlackChannel("invalid-format-slack", config)
        assert channel.validate_config() is False
    
    def test_config_validation_missing_aiohttp(self):
        """aiohttpが利用できない場合の検証をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        with patch('services.auto_deployment.notification.slack_channel.aiohttp', None):
            channel = SlackChannel("no-aiohttp-slack", config)
            assert channel.validate_config() is False
    
    def test_build_slack_payload(self):
        """Slackペイロードの構築をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'channel': '#test-channel',
            'username': 'Test Bot',
            'icon_emoji': ':test:'
        }
        
        channel = SlackChannel("payload-test", config)
        
        message = NotificationMessage(
            title="デプロイメント開始",
            content="本番環境へのデプロイメントを開始します。",
            severity=NotificationSeverity.INFO,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={'version': '1.2.3', 'commit': 'abc123'},
            deployment_id="deploy-456",
            environment="production"
        )
        
        payload = channel._build_slack_payload(message)
        
        assert payload['channel'] == '#test-channel'
        assert payload['username'] == 'Test Bot'
        assert payload['icon_emoji'] == ':test:'
        assert len(payload['attachments']) == 1
        
        attachment = payload['attachments'][0]
        assert attachment['title'] == "デプロイメント開始"
        assert attachment['text'] == "本番環境へのデプロイメントを開始します。"
        assert attachment['color'] == "#36a64f"  # 緑色（INFO）
        assert attachment['timestamp'] == int(datetime(2024, 1, 15, 10, 30, 0).timestamp())
        
        # フィールドの確認
        fields = {field['title']: field['value'] for field in attachment['fields']}
        assert fields['Deployment ID'] == "deploy-456"
        assert fields['Environment'] == "production"
        assert fields['Version'] == "1.2.3"
        assert fields['Commit'] == "abc123"
    
    def test_severity_colors(self):
        """重要度に応じた色の設定をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        channel = SlackChannel("color-test", config)
        
        # 各重要度の色をテスト
        assert channel._get_color_for_severity(NotificationSeverity.INFO) == "#36a64f"
        assert channel._get_color_for_severity(NotificationSeverity.WARNING) == "#ff9500"
        assert channel._get_color_for_severity(NotificationSeverity.ERROR) == "#ff0000"
        assert channel._get_color_for_severity(NotificationSeverity.CRITICAL) == "#8b0000"
    
    @pytest.mark.asyncio
    async def test_send_success(self):
        """正常な送信をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'channel': '#test'
        }
        
        # aiohttpのモック
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch('services.auto_deployment.notification.slack_channel.aiohttp') as mock_aiohttp:
            mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session
            mock_aiohttp.ClientTimeout = Mock()
            
            channel = SlackChannel("success-test", config)
            
            message = NotificationMessage(
                title="テスト成功",
                content="テストメッセージ",
                severity=NotificationSeverity.INFO,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            assert result.success is True
            assert result.channel_name == "success-test"
            assert result.message_id is not None
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_send_http_error(self):
        """HTTP エラーの処理をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        # HTTP 400エラーのモック
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch('services.auto_deployment.notification.slack_channel.aiohttp') as mock_aiohttp:
            mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session
            mock_aiohttp.ClientTimeout = Mock()
            
            channel = SlackChannel("error-test", config)
            
            message = NotificationMessage(
                title="エラーテスト",
                content="エラーメッセージ",
                severity=NotificationSeverity.ERROR,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            assert result.success is False
            assert result.channel_name == "error-test"
            assert result.message_id is None
            assert "HTTP 400" in result.error_message
    
    @pytest.mark.asyncio
    async def test_send_timeout(self):
        """タイムアウトの処理をテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        with patch('services.auto_deployment.notification.slack_channel.aiohttp') as mock_aiohttp:
            mock_aiohttp.ClientSession.return_value.__aenter__.side_effect = TimeoutError()
            mock_aiohttp.ClientTimeout = Mock()
            
            channel = SlackChannel("timeout-test", config)
            
            message = NotificationMessage(
                title="タイムアウトテスト",
                content="タイムアウトメッセージ",
                severity=NotificationSeverity.WARNING,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            assert result.success is False
            assert result.channel_name == "timeout-test"
            assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_send_invalid_config(self):
        """無効な設定での送信をテストします。"""
        config = {}  # webhook_urlが欠如
        
        channel = SlackChannel("invalid-config-test", config)
        
        message = NotificationMessage(
            title="設定無効テスト",
            content="設定が無効です",
            severity=NotificationSeverity.ERROR,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        result = await channel.send(message)
        
        assert result.success is False
        assert result.channel_name == "invalid-config-test"
        assert "Invalid configuration" in result.error_message
    
    def test_format_message(self):
        """メッセージフォーマットをテストします。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL'
        }
        
        channel = SlackChannel("format-test", config)
        
        message = NotificationMessage(
            title="フォーマットテスト",
            content="フォーマットされるメッセージ",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        formatted = channel.format_message(message)
        
        assert "フォーマットテスト" in formatted
        assert "フォーマットされるメッセージ" in formatted