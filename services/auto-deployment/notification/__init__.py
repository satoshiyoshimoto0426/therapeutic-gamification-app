"""
Auto-deployment notification system.

This module provides a comprehensive notification framework for deployment events,
including support for multiple channels (Slack, email) and message formatting.
"""

from .base import NotificationChannel, NotificationMessage, NotificationSeverity
from .slack_channel import SlackChannel
from .email_channel import EmailChannel
from .notification_manager import NotificationManager

__all__ = [
    'NotificationChannel',
    'NotificationMessage', 
    'NotificationSeverity',
    'SlackChannel',
    'EmailChannel',
    'NotificationManager'
]