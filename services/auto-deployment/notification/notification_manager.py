"""
Notification manager for coordinating multiple notification channels.

This module provides the main interface for sending notifications through
multiple channels with configuration management and error handling.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationSeverity
from .slack_channel import SlackChannel
from .email_channel import EmailChannel

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages multiple notification channels and coordinates message sending."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize notification manager.
        
        Args:
            config: Notification configuration with channel definitions
        """
        self.config = config
        self.channels: Dict[str, NotificationChannel] = {}
        self.enabled = config.get('enabled', True)
        self._initialize_channels()
    
    def _initialize_channels(self):
        """Initialize notification channels from configuration."""
        channels_config = self.config.get('channels', {})
        
        for channel_name, channel_config in channels_config.items():
            try:
                channel_type = channel_config.get('type')
                
                if channel_type == 'slack':
                    channel = SlackChannel(channel_name, channel_config)
                elif channel_type == 'email':
                    channel = EmailChannel(channel_name, channel_config)
                else:
                    logger.warning(f"Unknown channel type: {channel_type}")
                    continue
                
                if channel.validate_config():
                    self.channels[channel_name] = channel
                    logger.info(f"Initialized {channel_type} channel: {channel_name}")
                else:
                    logger.error(f"Failed to validate {channel_type} channel: {channel_name}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize channel {channel_name}: {str(e)}")
    
    async def send_notification(
        self,
        title: str,
        content: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        deployment_id: Optional[str] = None,
        environment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None
    ) -> List[NotificationResult]:
        """
        Send notification through specified or all channels.
        
        Args:
            title: Notification title
            content: Notification content
            severity: Notification severity level
            deployment_id: Optional deployment identifier
            environment: Optional environment name
            metadata: Optional additional metadata
            channels: Optional list of specific channels to use
            
        Returns:
            List of notification results from all channels
        """
        if not self.enabled:
            logger.debug("Notifications are disabled")
            return []
        
        message = NotificationMessage(
            title=title,
            content=content,
            severity=severity,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            deployment_id=deployment_id,
            environment=environment
        )
        
        return await self.send_message(message, channels)
    
    async def send_message(
        self,
        message: NotificationMessage,
        channels: Optional[List[str]] = None
    ) -> List[NotificationResult]:
        """
        Send notification message through specified or all channels.
        
        Args:
            message: Notification message to send
            channels: Optional list of specific channels to use
            
        Returns:
            List of notification results from all channels
        """
        if not self.enabled:
            logger.debug("Notifications are disabled")
            return []
        
        # Determine which channels to use
        target_channels = self._get_target_channels(channels)
        
        if not target_channels:
            logger.warning("No valid notification channels available")
            return []
        
        # Send notifications concurrently
        tasks = []
        for channel in target_channels:
            if channel.should_send(message):
                tasks.append(self._send_to_channel(channel, message))
            else:
                logger.debug(f"Skipping channel {channel.name} due to severity filter")
        
        if not tasks:
            logger.info("No channels matched severity filter")
            return []
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        notification_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Channel {target_channels[i].name} failed: {str(result)}")
                notification_results.append(NotificationResult(
                    success=False,
                    channel_name=target_channels[i].name,
                    error_message=str(result)
                ))
            else:
                notification_results.append(result)
        
        # Log summary
        successful = sum(1 for r in notification_results if r.success)
        total = len(notification_results)
        logger.info(f"Notification sent: {successful}/{total} channels successful")
        
        return notification_results
    
    def _get_target_channels(self, channels: Optional[List[str]]) -> List[NotificationChannel]:
        """
        Get list of target channels for notification.
        
        Args:
            channels: Optional list of specific channel names
            
        Returns:
            List of notification channels to use
        """
        if channels is None:
            # Use all available channels
            return list(self.channels.values())
        
        # Use only specified channels that exist
        target_channels = []
        for channel_name in channels:
            if channel_name in self.channels:
                target_channels.append(self.channels[channel_name])
            else:
                logger.warning(f"Requested channel '{channel_name}' not found")
        
        return target_channels
    
    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        message: NotificationMessage
    ) -> NotificationResult:
        """
        Send message to a specific channel with error handling.
        
        Args:
            channel: Notification channel
            message: Message to send
            
        Returns:
            Notification result
        """
        try:
            logger.debug(f"Sending notification to {channel.name}")
            result = await channel.send(message)
            
            if result.success:
                logger.debug(f"Successfully sent notification to {channel.name}")
            else:
                logger.warning(f"Failed to send notification to {channel.name}: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error sending to {channel.name}: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=channel.name,
                error_message=error_msg
            )
    
    def get_channel_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all channels.
        
        Returns:
            Dictionary with channel status information
        """
        status = {}
        for name, channel in self.channels.items():
            status[name] = {
                'name': name,
                'type': channel.__class__.__name__,
                'enabled': channel.enabled,
                'severity_filter': [s.value for s in channel.severity_filter],
                'config_valid': channel.validate_config()
            }
        return status
    
    def add_channel(self, name: str, channel: NotificationChannel) -> bool:
        """
        Add a new notification channel.
        
        Args:
            name: Channel name
            channel: Notification channel instance
            
        Returns:
            True if channel was added successfully
        """
        try:
            if channel.validate_config():
                self.channels[name] = channel
                logger.info(f"Added notification channel: {name}")
                return True
            else:
                logger.error(f"Failed to validate channel configuration: {name}")
                return False
        except Exception as e:
            logger.error(f"Failed to add channel {name}: {str(e)}")
            return False
    
    def remove_channel(self, name: str) -> bool:
        """
        Remove a notification channel.
        
        Args:
            name: Channel name to remove
            
        Returns:
            True if channel was removed
        """
        if name in self.channels:
            del self.channels[name]
            logger.info(f"Removed notification channel: {name}")
            return True
        else:
            logger.warning(f"Channel not found for removal: {name}")
            return False
    
    async def test_channels(self, channels: Optional[List[str]] = None) -> List[NotificationResult]:
        """
        Send test notifications to verify channel functionality.
        
        Args:
            channels: Optional list of specific channels to test
            
        Returns:
            List of test results
        """
        test_message = NotificationMessage(
            title="Auto-Deployment System Test",
            content="This is a test notification to verify channel functionality.",
            severity=NotificationSeverity.INFO,
            timestamp=datetime.utcnow(),
            metadata={'test': True, 'source': 'notification_manager'},
            deployment_id="test-deployment",
            environment="test"
        )
        
        logger.info("Sending test notifications")
        results = await self.send_message(test_message, channels)
        
        # Log test results
        for result in results:
            if result.success:
                logger.info(f"Test notification successful for {result.channel_name}")
            else:
                logger.error(f"Test notification failed for {result.channel_name}: {result.error_message}")
        
        return results