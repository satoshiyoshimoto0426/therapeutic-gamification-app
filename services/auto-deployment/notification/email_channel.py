"""
Email notification channel implementation.

This module provides email integration for deployment notifications.
"""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime

from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationSeverity

logger = logging.getLogger(__name__)


class EmailChannel(NotificationChannel):
    """Email notification channel implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize email channel.
        
        Args:
            name: Channel name
            config: Email configuration including SMTP settings and recipients
        """
        super().__init__(name, config)
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email', self.username)
        self.recipients = config.get('recipients', [])
        self.use_tls = config.get('use_tls', True)
        self.use_ssl = config.get('use_ssl', False)
        
    def validate_config(self) -> bool:
        """
        Validate email configuration.
        
        Returns:
            True if configuration is valid
        """
        if not self.smtp_server:
            logger.error(f"Email channel {self.name}: smtp_server is required")
            return False
            
        if not self.username:
            logger.error(f"Email channel {self.name}: username is required")
            return False
            
        if not self.password:
            logger.error(f"Email channel {self.name}: password is required")
            return False
            
        if not self.recipients:
            logger.error(f"Email channel {self.name}: recipients list is required")
            return False
            
        if not isinstance(self.recipients, list):
            logger.error(f"Email channel {self.name}: recipients must be a list")
            return False
            
        return True
    
    async def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Send notification via email.
        
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
            # Run email sending in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._send_email_sync, message)
            return result
            
        except Exception as e:
            error_msg = f"Email notification failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message=error_msg
            )
    
    def _send_email_sync(self, message: NotificationMessage) -> NotificationResult:
        """
        Send email synchronously (called from thread pool).
        
        Args:
            message: Notification message to send
            
        Returns:
            Result of the notification attempt
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{message.severity.value.upper()}] {message.title}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.recipients)
            
            # Create HTML and text versions
            text_content = self._create_text_content(message)
            html_content = self._create_html_content(message)
            
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent successfully to {len(self.recipients)} recipients")
            return NotificationResult(
                success=True,
                channel_name=self.name,
                message_id=f"email_{datetime.utcnow().timestamp()}"
            )
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Email sending failed: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                channel_name=self.name,
                error_message=error_msg
            )
    
    def _create_text_content(self, message: NotificationMessage) -> str:
        """
        Create plain text email content.
        
        Args:
            message: Notification message
            
        Returns:
            Plain text email content
        """
        content = f"{message.title}\n"
        content += "=" * len(message.title) + "\n\n"
        content += f"{message.content}\n\n"
        
        content += "Details:\n"
        content += f"Severity: {message.severity.value.upper()}\n"
        content += f"Timestamp: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        if message.deployment_id:
            content += f"Deployment ID: {message.deployment_id}\n"
            
        if message.environment:
            content += f"Environment: {message.environment}\n"
            
        if message.metadata:
            content += "\nMetadata:\n"
            for key, value in message.metadata.items():
                content += f"  {key}: {value}\n"
        
        return content
    
    def _create_html_content(self, message: NotificationMessage) -> str:
        """
        Create HTML email content.
        
        Args:
            message: Notification message
            
        Returns:
            HTML email content
        """
        severity_colors = {
            NotificationSeverity.INFO: "#d4edda",
            NotificationSeverity.WARNING: "#fff3cd", 
            NotificationSeverity.ERROR: "#f8d7da",
            NotificationSeverity.CRITICAL: "#f5c6cb"
        }
        
        severity_text_colors = {
            NotificationSeverity.INFO: "#155724",
            NotificationSeverity.WARNING: "#856404",
            NotificationSeverity.ERROR: "#721c24", 
            NotificationSeverity.CRITICAL: "#721c24"
        }
        
        bg_color = severity_colors.get(message.severity, "#f8f9fa")
        text_color = severity_text_colors.get(message.severity, "#212529")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {bg_color}; color: {text_color}; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 0 0 5px 5px; font-size: 12px; color: #6c757d; }}
                .metadata {{ background-color: #f8f9fa; padding: 10px; margin-top: 15px; border-radius: 3px; }}
                .severity {{ font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{message.title}</h2>
                    <span class="severity">[{message.severity.value}]</span>
                </div>
                <div class="content">
                    <p>{message.content.replace(chr(10), '<br>')}</p>
                    
                    <div class="metadata">
                        <strong>Details:</strong><br>
                        <strong>Timestamp:</strong> {message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
        """
        
        if message.deployment_id:
            html += f"                        <strong>Deployment ID:</strong> {message.deployment_id}<br>\n"
            
        if message.environment:
            html += f"                        <strong>Environment:</strong> {message.environment}<br>\n"
            
        if message.metadata:
            html += "                        <br><strong>Metadata:</strong><br>\n"
            for key, value in message.metadata.items():
                html += f"                        <strong>{key.replace('_', ' ').title()}:</strong> {value}<br>\n"
        
        html += """
                    </div>
                </div>
                <div class="footer">
                    This is an automated notification from the Auto-Deployment System.
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def format_message(self, message: NotificationMessage) -> str:
        """
        Format message for email (uses HTML formatting).
        
        Args:
            message: Message to format
            
        Returns:
            Simple text format (rich formatting handled by HTML)
        """
        return f"[{message.severity.value.upper()}] {message.title}: {message.content}"