"""
Email通知チャンネルのテスト。

このモジュールはEmail統合機能の包括的なテストを提供します。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import smtplib

from ..email_channel import EmailChannel
from ..base import NotificationMessage, NotificationSeverity


class TestEmailChannel:
    """EmailChannelクラスのテスト。"""
    
    def test_email_channel_initialization(self):
        """Emailチャンネルの初期化をテストします。"""
        config = {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password123',
            'from_email': 'deploy@example.com',
            'recipients': ['admin@example.com', 'dev@example.com'],
            'use_tls': True,
            'use_ssl': False,
            'severity_filter': ['warning', 'error', 'critical']
        }
        
        channel = EmailChannel("email-test", config)
        
        assert channel.name == "email-test"
        assert channel.smtp_server == 'smtp.example.com'
        assert channel.smtp_port == 587
        assert channel.username == 'test@example.com'
        assert channel.password == 'password123'
        assert channel.from_email == 'deploy@example.com'
        assert channel.recipients == ['admin@example.com', 'dev@example.com']
        assert channel.use_tls is True
        assert channel.use_ssl is False
        assert channel.enabled is True
    
    def test_email_channel_default_values(self):
        """Emailチャンネルのデフォルト値をテストします。"""
        config = {
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("email-default", config)
        
        assert channel.smtp_server == 'smtp.gmail.com'
        assert channel.smtp_port == 587
        assert channel.from_email == 'test@example.com'  # usernameと同じ
        assert channel.use_tls is True
        assert channel.use_ssl is False
    
    def test_config_validation_success(self):
        """有効な設定の検証をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("valid-email", config)
        assert channel.validate_config() is True
    
    def test_config_validation_missing_smtp_server(self):
        """SMTP サーバーが欠如している場合の検証をテストします。"""
        config = {
            'smtp_server': '',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("invalid-smtp", config)
        assert channel.validate_config() is False
    
    def test_config_validation_missing_username(self):
        """ユーザー名が欠如している場合の検証をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("invalid-username", config)
        assert channel.validate_config() is False
    
    def test_config_validation_missing_password(self):
        """パスワードが欠如している場合の検証をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("invalid-password", config)
        assert channel.validate_config() is False
    
    def test_config_validation_missing_recipients(self):
        """受信者が欠如している場合の検証をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123'
        }
        
        channel = EmailChannel("invalid-recipients", config)
        assert channel.validate_config() is False
    
    def test_config_validation_invalid_recipients_type(self):
        """受信者の型が無効な場合の検証をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': 'admin@example.com'  # 文字列（リストではない）
        }
        
        channel = EmailChannel("invalid-recipients-type", config)
        assert channel.validate_config() is False
    
    def test_create_text_content(self):
        """プレーンテキストコンテンツの作成をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("text-test", config)
        
        message = NotificationMessage(
            title="デプロイメント完了",
            content="本番環境へのデプロイメントが正常に完了しました。",
            severity=NotificationSeverity.INFO,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={'version': '1.2.3', 'duration': '5分'},
            deployment_id="deploy-789",
            environment="production"
        )
        
        text_content = channel._create_text_content(message)
        
        assert "デプロイメント完了" in text_content
        assert "本番環境へのデプロイメントが正常に完了しました。" in text_content
        assert "Severity: INFO" in text_content
        assert "2024-01-15 10:30:00 UTC" in text_content
        assert "deploy-789" in text_content
        assert "production" in text_content
        assert "version: 1.2.3" in text_content
        assert "duration: 5分" in text_content
    
    def test_create_html_content(self):
        """HTMLコンテンツの作成をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("html-test", config)
        
        message = NotificationMessage(
            title="エラー発生",
            content="デプロイメント中にエラーが発生しました。\n詳細を確認してください。",
            severity=NotificationSeverity.ERROR,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={'error_code': '500', 'service': 'api'},
            deployment_id="deploy-error-123",
            environment="staging"
        )
        
        html_content = channel._create_html_content(message)
        
        assert "<html>" in html_content
        assert "エラー発生" in html_content
        assert "デプロイメント中にエラーが発生しました。<br>詳細を確認してください。" in html_content
        assert "#f8d7da" in html_content  # エラーの背景色
        assert "deploy-error-123" in html_content
        assert "staging" in html_content
        assert "Error Code" in html_content
        assert "500" in html_content
    
    @pytest.mark.asyncio
    async def test_send_success_with_tls(self):
        """TLS使用時の正常な送信をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password123',
            'from_email': 'deploy@example.com',
            'recipients': ['admin@example.com'],
            'use_tls': True,
            'use_ssl': False
        }
        
        # SMTPサーバーのモック
        mock_server = MagicMock()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value = mock_server
            
            channel = EmailChannel("tls-test", config)
            
            message = NotificationMessage(
                title="TLSテスト",
                content="TLS送信テスト",
                severity=NotificationSeverity.INFO,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            # SMTPサーバーの呼び出しを確認
            mock_smtp.assert_called_once_with('smtp.example.com', 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@example.com', 'password123')
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
            
            assert result.success is True
            assert result.channel_name == "tls-test"
            assert result.message_id is not None
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_send_success_with_ssl(self):
        """SSL使用時の正常な送信をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 465,
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com'],
            'use_tls': False,
            'use_ssl': True
        }
        
        # SMTP_SSLサーバーのモック
        mock_server = MagicMock()
        
        with patch('smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_smtp_ssl.return_value = mock_server
            
            channel = EmailChannel("ssl-test", config)
            
            message = NotificationMessage(
                title="SSLテスト",
                content="SSL送信テスト",
                severity=NotificationSeverity.INFO,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            # SMTP_SSLサーバーの呼び出しを確認
            mock_smtp_ssl.assert_called_once_with('smtp.example.com', 465)
            mock_server.starttls.assert_not_called()  # SSLでは不要
            mock_server.login.assert_called_once_with('test@example.com', 'password123')
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
            
            assert result.success is True
            assert result.channel_name == "ssl-test"
    
    @pytest.mark.asyncio
    async def test_send_smtp_error(self):
        """SMTP エラーの処理をテストします。"""
        config = {
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPAuthenticationError(535, "認証エラー")
            
            channel = EmailChannel("smtp-error-test", config)
            
            message = NotificationMessage(
                title="SMTPエラーテスト",
                content="SMTPエラーメッセージ",
                severity=NotificationSeverity.ERROR,
                timestamp=datetime.utcnow(),
                metadata={}
            )
            
            result = await channel.send(message)
            
            assert result.success is False
            assert result.channel_name == "smtp-error-test"
            assert "SMTP error" in result.error_message
            assert "認証エラー" in result.error_message
    
    @pytest.mark.asyncio
    async def test_send_invalid_config(self):
        """無効な設定での送信をテストします。"""
        config = {}  # 必要な設定が欠如
        
        channel = EmailChannel("invalid-config-test", config)
        
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
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password123',
            'recipients': ['admin@example.com']
        }
        
        channel = EmailChannel("format-test", config)
        
        message = NotificationMessage(
            title="フォーマットテスト",
            content="フォーマットされるメッセージ",
            severity=NotificationSeverity.WARNING,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        formatted = channel.format_message(message)
        
        assert "[WARNING]" in formatted
        assert "フォーマットテスト" in formatted
        assert "フォーマットされるメッセージ" in formatted