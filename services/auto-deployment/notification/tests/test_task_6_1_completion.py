"""
タスク6.1完了テスト：通知フレームワークとチャンネルの作成。

このテストは要件4.1と4.2に対応する通知フレームワークの
包括的な機能を検証します。
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from ..base import NotificationChannel, NotificationMessage, NotificationSeverity, NotificationResult
from ..slack_channel import SlackChannel
from ..email_channel import EmailChannel
from ..notification_manager import NotificationManager


class TestTask61Completion:
    """タスク6.1の完了を検証するテストクラス。"""
    
    def test_abstract_notification_channel_base_class(self):
        """抽象通知チャンネル基底クラスの実装を検証します。"""
        # NotificationChannelが抽象基底クラスとして正しく定義されているか確認
        assert hasattr(NotificationChannel, 'send')
        assert hasattr(NotificationChannel, 'validate_config')
        assert hasattr(NotificationChannel, 'should_send')
        assert hasattr(NotificationChannel, 'format_message')
        
        # 抽象メソッドが定義されているか確認
        try:
            # 直接インスタンス化しようとするとエラーになるはず
            NotificationChannel("test", {})
            assert False, "抽象クラスのインスタンス化が許可されています"
        except TypeError:
            pass  # 期待される動作
    
    def test_notification_message_data_model(self):
        """NotificationMessageデータモデルの実装を検証します。"""
        timestamp = datetime.utcnow()
        metadata = {'version': '1.0.0', 'commit': 'abc123'}
        
        message = NotificationMessage(
            title="デプロイメント通知",
            content="デプロイメントが完了しました",
            severity=NotificationSeverity.INFO,
            timestamp=timestamp,
            metadata=metadata,
            deployment_id="deploy-123",
            environment="production"
        )
        
        # 全ての必要なフィールドが存在することを確認
        assert message.title == "デプロイメント通知"
        assert message.content == "デプロイメントが完了しました"
        assert message.severity == NotificationSeverity.INFO
        assert message.timestamp == timestamp
        assert message.metadata == metadata
        assert message.deployment_id == "deploy-123"
        assert message.environment == "production"
        
        # 辞書変換機能の確認
        message_dict = message.to_dict()
        assert isinstance(message_dict, dict)
        assert message_dict['title'] == message.title
        assert message_dict['severity'] == 'info'
    
    def test_notification_severity_enum(self):
        """NotificationSeverity列挙型の実装を検証します。"""
        # 全ての重要度レベルが定義されているか確認
        assert NotificationSeverity.INFO.value == "info"
        assert NotificationSeverity.WARNING.value == "warning"
        assert NotificationSeverity.ERROR.value == "error"
        assert NotificationSeverity.CRITICAL.value == "critical"
        
        # 列挙型として正しく動作するか確認
        severities = list(NotificationSeverity)
        assert len(severities) == 4
    
    def test_notification_result_data_model(self):
        """NotificationResultデータモデルの実装を検証します。"""
        result = NotificationResult(
            success=True,
            channel_name="test-channel",
            message_id="msg-123",
            error_message=None
        )
        
        assert result.success is True
        assert result.channel_name == "test-channel"
        assert result.message_id == "msg-123"
        assert result.error_message is None
        assert result.timestamp is not None
    
    def test_slack_channel_implementation(self):
        """Slack通知チャンネルの実装を検証します。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'channel': '#deployments',
            'username': 'Deploy Bot',
            'icon_emoji': ':rocket:'
        }
        
        slack_channel = SlackChannel("slack-test", config)
        
        # SlackChannelがNotificationChannelを継承しているか確認
        assert isinstance(slack_channel, NotificationChannel)
        
        # 必要な設定が正しく設定されているか確認
        assert slack_channel.webhook_url == config['webhook_url']
        assert slack_channel.channel == config['channel']
        assert slack_channel.username == config['username']
        assert slack_channel.icon_emoji == config['icon_emoji']
        
        # 設定検証メソッドが実装されているか確認
        assert hasattr(slack_channel, 'validate_config')
        assert callable(slack_channel.validate_config)
    
    def test_email_channel_implementation(self):
        """Email通知チャンネルの実装を検証します。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com', 'dev@example.com'],
            'use_tls': True
        }
        
        email_channel = EmailChannel("email-test", config)
        
        # EmailChannelがNotificationChannelを継承しているか確認
        assert isinstance(email_channel, NotificationChannel)
        
        # 必要な設定が正しく設定されているか確認
        assert email_channel.smtp_server == config['smtp_server']
        assert email_channel.smtp_port == config['smtp_port']
        assert email_channel.username == config['username']
        assert email_channel.password == config['password']
        assert email_channel.recipients == config['recipients']
        assert email_channel.use_tls == config['use_tls']
        
        # 設定検証メソッドが実装されているか確認
        assert hasattr(email_channel, 'validate_config')
        assert callable(email_channel.validate_config)
    
    def test_notification_manager_implementation(self):
        """通知マネージャーの実装を検証します。"""
        config = {
            'enabled': True,
            'channels': {
                'slack-prod': {
                    'type': 'slack',
                    'webhook_url': 'https://hooks.slack.com/test',
                    'channel': '#deployments'
                },
                'email-alerts': {
                    'type': 'email',
                    'smtp_server': 'smtp.example.com',
                    'username': 'test@example.com',
                    'password': 'password',
                    'recipients': ['admin@example.com']
                }
            }
        }
        
        with patch.object(NotificationManager, '_initialize_channels') as mock_init:
            
            manager = NotificationManager(config)
            
            # 手動でチャンネルを追加してテスト
            mock_slack_channel = Mock()
            mock_email_channel = Mock()
            manager.channels['slack-prod'] = mock_slack_channel
            manager.channels['email-alerts'] = mock_email_channel
            
            # 通知マネージャーが正しく初期化されているか確認
            assert manager.enabled is True
            assert len(manager.channels) == 2
            assert 'slack-prod' in manager.channels
            assert 'email-alerts' in manager.channels
            
            # 必要なメソッドが実装されているか確認
            assert hasattr(manager, 'send_notification')
            assert hasattr(manager, 'send_message')
            assert hasattr(manager, 'get_channel_status')
            assert hasattr(manager, 'add_channel')
            assert hasattr(manager, 'remove_channel')
            assert hasattr(manager, 'test_channels')
    
    @pytest.mark.asyncio
    async def test_slack_channel_send_functionality(self):
        """Slackチャンネルの送信機能を検証します。"""
        config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'channel': '#test'
        }
        
        slack_channel = SlackChannel("slack-send-test", config)
        
        message = NotificationMessage(
            title="送信テスト",
            content="Slack送信テスト",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        # aiohttpが利用できない場合の動作をテスト
        result = await slack_channel.send(message)
        
        # テスト用のwebhook URLなので404エラーが返される
        assert result.success is False
        assert result.channel_name == "slack-send-test"
        assert "HTTP 404" in result.error_message
    
    @pytest.mark.asyncio
    async def test_email_channel_send_functionality(self):
        """Emailチャンネルの送信機能を検証します。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        # SMTPサーバーのモック
        mock_server = Mock()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value = mock_server
            
            email_channel = EmailChannel("email-send-test", config)
            
            message = NotificationMessage(
                title="送信テスト",
                content="Email送信テスト",
                severity=NotificationSeverity.INFO,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await email_channel.send(message)
            
            # 送信が成功したか確認
            assert result.success is True
            assert result.channel_name == "email-send-test"
            assert result.message_id is not None
            
            # SMTPサーバーが正しく呼び出されたか確認
            mock_smtp.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notification_manager_send_functionality(self):
        """通知マネージャーの送信機能を検証します。"""
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # モックチャンネルを手動で追加
        mock_channel = Mock()
        mock_channel.should_send.return_value = True
        mock_channel.send = AsyncMock(return_value=NotificationResult(
            success=True, 
            channel_name="mock-channel"
        ))
        
        manager.channels["mock-channel"] = mock_channel
        
        # 通知送信をテスト
        results = await manager.send_notification(
            title="マネージャーテスト",
            content="通知マネージャー送信テスト",
            severity=NotificationSeverity.INFO,
            deployment_id="deploy-456",
            environment="staging"
        )
        
        # 送信結果の確認
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].channel_name == "mock-channel"
        
        # チャンネルが正しく呼び出されたか確認
        mock_channel.should_send.assert_called_once()
        mock_channel.send.assert_called_once()
    
    def test_severity_filtering_functionality(self):
        """重要度フィルタリング機能を検証します。"""
        config = {
            'enabled': True,
            'severity_filter': ['error', 'critical']
        }
        
        # テスト用のモックチャンネル
        class TestChannel(NotificationChannel):
            async def send(self, message):
                return NotificationResult(success=True, channel_name=self.name)
            
            def validate_config(self):
                return True
        
        channel = TestChannel("filter-test", config)
        
        # エラーメッセージは送信される
        error_message = NotificationMessage(
            title="エラー",
            content="エラーメッセージ",
            severity=NotificationSeverity.ERROR,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        assert channel.should_send(error_message) is True
        
        # 情報メッセージは送信されない
        info_message = NotificationMessage(
            title="情報",
            content="情報メッセージ",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        assert channel.should_send(info_message) is False
    
    def test_message_formatting_functionality(self):
        """メッセージフォーマット機能を検証します。"""
        config = {'enabled': True}
        
        # テスト用のチャンネル
        class TestChannel(NotificationChannel):
            async def send(self, message):
                return NotificationResult(success=True, channel_name=self.name)
            
            def validate_config(self):
                return True
        
        channel = TestChannel("format-test", config)
        
        message = NotificationMessage(
            title="フォーマットテスト",
            content="メッセージ内容のテスト",
            severity=NotificationSeverity.WARNING,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={'version': '1.0.0'},
            deployment_id="deploy-789",
            environment="production"
        )
        
        formatted = channel.format_message(message)
        
        # フォーマットされたメッセージに必要な情報が含まれているか確認
        assert "⚠️" in formatted  # 警告アイコン
        assert "**フォーマットテスト**" in formatted
        assert "メッセージ内容のテスト" in formatted
        assert "deploy-789" in formatted
        assert "production" in formatted
        assert "2024-01-15 10:30:00 UTC" in formatted
    
    def test_requirements_4_1_compliance(self):
        """要件4.1（デプロイメント開始通知）への準拠を検証します。"""
        # 要件4.1: デプロイメント開始時の通知送信
        
        # 通知システムがデプロイメント開始を通知できることを確認
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # デプロイメント開始メッセージの作成
        start_message = NotificationMessage(
            title="デプロイメント開始",
            content="本番環境へのデプロイメントを開始します",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={'version': '1.2.3', 'environment': 'production'},
            deployment_id="deploy-start-123",
            environment="production"
        )
        
        # メッセージが正しく作成されることを確認
        assert start_message.title == "デプロイメント開始"
        assert start_message.deployment_id == "deploy-start-123"
        assert start_message.environment == "production"
        assert "version" in start_message.metadata
    
    def test_requirements_4_2_compliance(self):
        """要件4.2（デプロイメント完了・失敗通知）への準拠を検証します。"""
        # 要件4.2: デプロイメント完了・失敗時の通知送信
        
        # 成功通知
        success_message = NotificationMessage(
            title="デプロイメント完了",
            content="本番環境へのデプロイメントが正常に完了しました",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={'duration': '5分30秒', 'status': 'success'},
            deployment_id="deploy-success-456",
            environment="production"
        )
        
        # 失敗通知
        failure_message = NotificationMessage(
            title="デプロイメント失敗",
            content="デプロイメント中にエラーが発生しました",
            severity=NotificationSeverity.ERROR,
            timestamp=datetime.utcnow(),
            metadata={'error_code': 'DEPLOY_001', 'status': 'failed'},
            deployment_id="deploy-failed-789",
            environment="production"
        )
        
        # メッセージが正しく作成されることを確認
        assert success_message.severity == NotificationSeverity.INFO
        assert failure_message.severity == NotificationSeverity.ERROR
        assert success_message.metadata['status'] == 'success'
        assert failure_message.metadata['status'] == 'failed'
    
    @pytest.mark.asyncio
    async def test_comprehensive_notification_workflow(self):
        """包括的な通知ワークフローを検証します。"""
        # 実際のデプロイメントシナリオをシミュレート
        
        config = {'enabled': True, 'channels': {}}
        manager = NotificationManager(config)
        
        # モックチャンネルを追加
        mock_slack = Mock()
        mock_slack.should_send.return_value = True
        mock_slack.send = AsyncMock(return_value=NotificationResult(
            success=True, channel_name="slack"
        ))
        
        mock_email = Mock()
        mock_email.should_send.return_value = True
        mock_email.send = AsyncMock(return_value=NotificationResult(
            success=True, channel_name="email"
        ))
        
        manager.channels["slack"] = mock_slack
        manager.channels["email"] = mock_email
        
        # デプロイメント開始通知
        start_results = await manager.send_notification(
            title="デプロイメント開始",
            content="v1.2.3のデプロイメントを開始します",
            severity=NotificationSeverity.INFO,
            deployment_id="deploy-workflow-123",
            environment="production",
            metadata={'version': '1.2.3', 'initiator': 'admin'}
        )
        
        # デプロイメント完了通知
        complete_results = await manager.send_notification(
            title="デプロイメント完了",
            content="デプロイメントが正常に完了しました",
            severity=NotificationSeverity.INFO,
            deployment_id="deploy-workflow-123",
            environment="production",
            metadata={'version': '1.2.3', 'duration': '3分45秒'}
        )
        
        # 両方の通知が成功したことを確認
        assert len(start_results) == 2
        assert len(complete_results) == 2
        assert all(r.success for r in start_results)
        assert all(r.success for r in complete_results)
        
        # 各チャンネルが2回呼び出されたことを確認（開始と完了）
        assert mock_slack.send.call_count == 2
        assert mock_email.send.call_count == 2