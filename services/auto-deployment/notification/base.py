"""
Base notification framework classes and interfaces.

This module defines the abstract base classes and data models for the notification system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class NotificationSeverity(Enum):
    """Severity levels for notifications."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotificationMessage:
    """Data model for notification messages."""
    title: str
    content: str
    severity: NotificationSeverity
    timestamp: datetime
    metadata: Dict[str, Any]
    deployment_id: Optional[str] = None
    environment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            'title': self.title,
            'content': self.content,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'deployment_id': self.deployment_id,
            'environment': self.environment
        }


@dataclass
class NotificationResult:
    """Result of a notification attempt."""
    success: bool
    channel_name: str
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class NotificationChannel(ABC):
    """Abstract base class for notification channels."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize notification channel.
        
        Args:
            name: Channel name identifier
            config: Channel-specific configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.severity_filter = self._parse_severity_filter(
            config.get('severity_filter', ['info', 'warning', 'error', 'critical'])
        )
        
    def _parse_severity_filter(self, severity_list: List[str]) -> List[NotificationSeverity]:
        """Parse severity filter from configuration."""
        try:
            return [NotificationSeverity(s.lower()) for s in severity_list]
        except ValueError as e:
            logger.warning(f"Invalid severity in filter: {e}")
            return list(NotificationSeverity)
    
    def should_send(self, message: NotificationMessage) -> bool:
        """
        Determine if message should be sent through this channel.
        
        Args:
            message: Notification message to evaluate
            
        Returns:
            True if message should be sent
        """
        if not self.enabled:
            return False
            
        return message.severity in self.severity_filter
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification message through this channel.
        
        Args:
            message: Notification message to send
            
        Returns:
            Result of the notification attempt
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate channel configuration.
        
        Returns:
            True if configuration is valid
        """
        pass
    
    def format_message(self, message: NotificationMessage) -> str:
        """
        Format message for this channel.
        
        Args:
            message: Message to format
            
        Returns:
            Formatted message string
        """
        severity_emoji = {
            NotificationSeverity.INFO: "ℹ️",
            NotificationSeverity.WARNING: "⚠️", 
            NotificationSeverity.ERROR: "❌",
            NotificationSeverity.CRITICAL: "🚨"
        }
        
        emoji = severity_emoji.get(message.severity, "📢")
        
        formatted = f"{emoji} **{message.title}**\n\n{message.content}"
        
        if message.deployment_id:
            formatted += f"\n\n**Deployment ID:** {message.deployment_id}"
            
        if message.environment:
            formatted += f"\n**Environment:** {message.environment}"
            
        if message.metadata:
            formatted += f"\n**Metadata:** {message.metadata}"
            
        formatted += f"\n**Time:** {message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        return formatted