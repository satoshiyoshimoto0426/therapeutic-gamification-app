"""
通知フレームワークの基底クラスのテスト。

このモジュールは通知システムの基底クラスと
データモデルの機能をテストします。
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from base import (
    NotificationChannel, NotificationMessage, NotificationResult, 
    NotificationSeverity
)


class TestNotificationMessage:
    """NotificationMessageクラスのテスト。"""
    
    def test_message_creation(self):
        """メッセージの作成をテストします。"""
        timestamp = datetime.utcnow()
        metadata = {'key': 'value', 'number': 42}
        
        message = NotificationMessage(
            title="テストタイトル",
            content="テストコンテンツ",
            severity=NotificationSeverity.INFO,
            timestamp=timestamp,
            metadata=metadata,
            deployment_id="test-deploy-123",
            environment="staging"
        )
        
        assert message.title == "テストタイトル"
        assert message.content == "テストコンテンツ"
        assert message.severity == NotificationSeverity.INFO
        assert message.timestamp == timestamp
        assert message.metadata == metadata
        assert message.deployment_id == "test-deploy-123"
        assert message.environment == "staging"
    
    def test_message_to_dict(self):
        """メッセージの辞書変換をテストします。"""
        timestamp = datetime.utcnow()
        metadata = {'test': True}
        
        message = NotificationMessage(
            title="テスト",
            content="内容",
            severity=NotificationSeverity.WARNING,
            timestamp=timestamp,
            metadata=metadata,
            deployment_id="deploy-456",
            environment="production"
        )
        
        result = message.to_dict()
        
        assert result['title'] == "テスト"
        assert result['content'] == "内容"
        assert result['severity'] == "warning"
        assert result['timestamp'] == timestamp.isoformat()
        assert result['metadata'] == metadata
        assert result['deployment_id'] == "deploy-456"
        assert result['environment'] == "production"


class TestNotificationResult:
    """NotificationResultクラスのテスト。"""
    
    def test_result_creation(self):
        """結果オブジェクトの作成をテストします。"""
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
    
    def test_result_with_error(self):
        """エラー付きの結果をテストします。"""
        result = NotificationResult(
            success=False,
            channel_name="failed-channel",
            error_message="テストエラー"
        )
        
        assert result.success is False
        assert result.channel_name == "failed-channel"
        assert result.message_id is None
        assert result.error_message == "テストエラー"
        assert result.timestamp is not None


class MockNotificationChannel(NotificationChannel):
    """テスト用のモック通知チャンネル。"""
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.send_called = False
        self.validate_called = False
        self.send_result = NotificationResult(success=True, channel_name=name)
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        self.send_called = True
        self.last_message = message
        return self.send_result
    
    def validate_config(self) -> bool:
        self.validate_called = True
        return True


class TestNotificationChannel:
    """NotificationChannelベースクラスのテスト。"""
    
    def test_channel_initialization(self):
        """チャンネルの初期化をテストします。"""
        config = {
            'enabled': True,
            'severity_filter': ['warning', 'error', 'critical']
        }
        
        channel = MockNotificationChannel("test-channel", config)
        
        assert channel.name == "test-channel"
        assert channel.config == config
        assert channel.enabled is True
        assert len(channel.severity_filter) == 3
        assert NotificationSeverity.WARNING in channel.severity_filter
        assert NotificationSeverity.ERROR in channel.severity_filter
        assert NotificationSeverity.CRITICAL in channel.severity_filter
        assert NotificationSeverity.INFO not in channel.severity_filter
    
    def test_channel_disabled(self):
        """無効化されたチャンネルをテストします。"""
        config = {'enabled': False}
        channel = MockNotificationChannel("disabled-channel", config)
        
        assert channel.enabled is False
        
        message = NotificationMessage(
            title="テスト",
            content="内容",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        assert channel.should_send(message) is False
    
    def test_severity_filtering(self):
        """重要度フィルタリングをテストします。"""
        config = {
            'enabled': True,
            'severity_filter': ['error', 'critical']
        }
        
        channel = MockNotificationChannel("filtered-channel", config)
        
        # エラーメッセージは送信される
        error_message = NotificationMessage(
            title="エラー",
            content="エラー内容",
            severity=NotificationSeverity.ERROR,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        assert channel.should_send(error_message) is True
        
        # 情報メッセージは送信されない
        info_message = NotificationMessage(
            title="情報",
            content="情報内容",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        assert channel.should_send(info_message) is False
    
    def test_invalid_severity_filter(self):
        """無効な重要度フィルタの処理をテストします。"""
        config = {
            'enabled': True,
            'severity_filter': ['invalid', 'error', 'unknown']
        }
        
        channel = MockNotificationChannel("invalid-filter-channel", config)
        
        # 無効な重要度は無視され、全ての重要度が許可される
        assert len(channel.severity_filter) == 4  # 全ての有効な重要度
    
    def test_message_formatting(self):
        """メッセージフォーマットをテストします。"""
        config = {'enabled': True}
        channel = MockNotificationChannel("format-channel", config)
        
        message = NotificationMessage(
            title="デプロイメント完了",
            content="本番環境へのデプロイメントが正常に完了しました。",
            severity=NotificationSeverity.INFO,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={'version': '1.2.3', 'duration': '5分'},
            deployment_id="deploy-789",
            environment="production"
        )
        
        formatted = channel.format_message(message)
        
        assert "ℹ️" in formatted  # 情報アイコン
        assert "**デプロイメント完了**" in formatted
        assert "本番環境へのデプロイメントが正常に完了しました。" in formatted
        assert "deploy-789" in formatted
        assert "production" in formatted
        assert "2024-01-15 10:30:00 UTC" in formatted
    
    @pytest.mark.asyncio
    async def test_channel_send_method(self):
        """チャンネルの送信メソッドをテストします。"""
        config = {'enabled': True}
        channel = MockNotificationChannel("send-channel", config)
        
        message = NotificationMessage(
            title="テスト送信",
            content="送信テスト",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        result = await channel.send(message)
        
        assert channel.send_called is True
        assert channel.last_message == message
        assert result.success is True
        assert result.channel_name == "send-channel"
    
    def test_config_validation(self):
        """設定の検証をテストします。"""
        config = {'enabled': True}
        channel = MockNotificationChannel("validate-channel", config)
        
        is_valid = channel.validate_config()
        
        assert channel.validate_called is True
        assert is_valid is True