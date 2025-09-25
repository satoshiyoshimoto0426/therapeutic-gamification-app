"""
Slack notification channel implementation.

This module provides Slack integration for deployment notifications.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import aiohttp
except ImportError:
    aiohttp = None

from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationSeverity

logger = logging.getLogger(__name__)


class SlackChannel(NotificationChannel):
    """Slack notification channel implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize Slack channel.
        
        Args:
            name: Channel name
            config: Slack configuration including webhook_url, channel, username
        """
        super().__init__(name, config)
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#deployments')
        self.username = config.get('username', 'Auto-Deploy Bot')
        self.icon_emoji = config.get('icon_emoji', ':robot_face:')
        
    def validate_config(self) -> bool:
        """
        Validate Slack configuration.
        
        Returns:
            True if configuration is valid
        """
        if not self.webhook_url:
            logger.error(f"Slack channel {self.name}: webhook_url is required")
            return False
            
        if not self.webhook_url.startswith('https://hooks.slack.com/'):
            logger.error(f"Slack channel {self.name}: invalid webhook URL format")
            return False
            
        if aiohttp is None:
            logger.error("aiohttp is required for Slack notifications")
            return False
            
        return True
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification to Slack.
        
        Args:
            message: Notification message to send
            
        Returns:
            Result of the notification attempt
        """
        if not self.validate_config():
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message="Invalid configuration"
            )
        
        try:
            slack_payload = self._build_slack_payload(message)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=slack_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent successfully to {self.channel}")
                        return NotificationResult(
                            success=True,
                            channel_name=self.name,
                            message_id=f"slack_{datetime.utcnow().timestamp()}"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Slack API error {response.status}: {error_text}")
                        return NotificationResult(
                            success=False,
                            channel_name=self.name,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
                        
        except asyncio.TimeoutError:
            error_msg = "Slack notification timeout"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Slack notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message=error_msg
            )
    
    def _build_slack_payload(self, message: NotificationMessage) -> Dict[str, Any]:
        """
        Build Slack webhook payload.
        
        Args:
            message: Notification message
            
        Returns:
            Slack webhook payload
        """
        color = self._get_color_for_severity(message.severity)
        
        # Build attachment with rich formatting
        attachment = {
            "color": color,
            "title": message.title,
            "text": message.content,
            "timestamp": int(message.timestamp.timestamp()),
            "fields": []
        }
        
        # Add deployment info fields
        if message.deployment_id:
            attachment["fields"].append({
                "title": "Deployment ID",
                "value": message.deployment_id,
                "short": True
            })
            
        if message.environment:
            attachment["fields"].append({
                "title": "Environment", 
                "value": message.environment,
                "short": True
            })
        
        # Add metadata fields
        if message.metadata:
            for key, value in message.metadata.items():
                if len(attachment["fields"]) < 10:  # Slack limit
                    attachment["fields"].append({
                        "title": key.replace('_', ' ').title(),
                        "value": str(value),
                        "short": True
                    })
        
        payload = {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [attachment]
        }
        
        return payload
    
    def _get_color_for_severity(self, severity: NotificationSeverity) -> str:
        """
        Get Slack color for severity level.
        
        Args:
            severity: Notification severity
            
        Returns:
            Hex color code
        """
        color_map = {
            NotificationSeverity.INFO: "#36a64f",      # Green
            NotificationSeverity.WARNING: "#ff9500",   # Orange  
            NotificationSeverity.ERROR: "#ff0000",     # Red
            NotificationSeverity.CRITICAL: "#8b0000"   # Dark red
        }
        return color_map.get(severity, "#808080")  # Gray default
    
    def format_message(self, message: NotificationMessage) -> str:
        """
        Format message for Slack (uses rich attachments instead).
        
        Args:
            message: Message to format
            
        Returns:
            Simple text format (rich formatting handled by attachments)
        """
        return f"{message.title}: {message.content}"