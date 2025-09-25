"""
Alert and escalation system for auto-deployment notifications.

This module provides advanced alerting capabilities including severity classification,
escalation procedures, notification scheduling, and throttling mechanisms.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from collections import defaultdict
import json

from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationSeverity
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Extended alert severity levels with escalation priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class EscalationLevel(Enum):
    """Escalation levels for alert handling."""
    LEVEL_1 = "level_1"  # Initial notification
    LEVEL_2 = "level_2"  # Team lead notification
    LEVEL_3 = "level_3"  # Management notification
    LEVEL_4 = "level_4"  # Executive notification


@dataclass
class AlertRule:
    """Configuration for alert behavior and escalation."""
    name: str
    severity: AlertSeverity
    conditions: Dict[str, Any]
    escalation_levels: List[EscalationLevel]
    escalation_intervals: List[int]  # Minutes between escalations
    max_escalations: int = 3
    throttle_window: int = 60  # Minutes
    max_alerts_per_window: int = 5
    auto_resolve: bool = False
    auto_resolve_timeout: int = 30  # Minutes
    notification_channels: List[str] = field(default_factory=list)
    escalation_channels: Dict[EscalationLevel, List[str]] = field(default_factory=dict)


@dataclass
class Alert:
    """Active alert instance."""
    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    description: str
    source: str
    timestamp: datetime
    deployment_id: Optional[str] = None
    environment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Escalation tracking
    current_escalation_level: EscalationLevel = EscalationLevel.LEVEL_1
    escalation_count: int = 0
    last_escalation: Optional[datetime] = None
    next_escalation: Optional[datetime] = None
    
    # Status tracking
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Notification tracking
    notifications_sent: List[str] = field(default_factory=list)
    last_notification: Optional[datetime] = None


@dataclass
class ThrottleState:
    """Throttling state for alert rules."""
    alert_count: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    suppressed_alerts: List[str] = field(default_factory=list)


class AlertSystem:
    """Advanced alert and escalation system."""
    
    def __init__(self, notification_manager: NotificationManager, config: Dict[str, Any]):
        """
        Initialize alert system.
        
        Args:
            notification_manager: Notification manager instance
            config: Alert system configuration
        """
        self.notification_manager = notification_manager
        self.config = config
        self.enabled = config.get('enabled', True)
        
        # Alert management
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Throttling and scheduling
        self.throttle_states: Dict[str, ThrottleState] = defaultdict(ThrottleState)
        self.escalation_tasks: Dict[str, asyncio.Task] = {}
        
        # Callbacks for external integration
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        self._initialize_rules()
        self._start_background_tasks()
    
    def _initialize_rules(self):
        """Initialize alert rules from configuration."""
        rules_config = self.config.get('rules', {})
        
        for rule_name, rule_config in rules_config.items():
            try:
                rule = AlertRule(
                    name=rule_name,
                    severity=AlertSeverity(rule_config.get('severity', 'medium')),
                    conditions=rule_config.get('conditions', {}),
                    escalation_levels=[
                        EscalationLevel(level) for level in 
                        rule_config.get('escalation_levels', ['level_1'])
                    ],
                    escalation_intervals=rule_config.get('escalation_intervals', [15, 30, 60]),
                    max_escalations=rule_config.get('max_escalations', 3),
                    throttle_window=rule_config.get('throttle_window', 60),
                    max_alerts_per_window=rule_config.get('max_alerts_per_window', 5),
                    auto_resolve=rule_config.get('auto_resolve', False),
                    auto_resolve_timeout=rule_config.get('auto_resolve_timeout', 30),
                    notification_channels=rule_config.get('notification_channels', []),
                    escalation_channels={
                        EscalationLevel(k) if isinstance(k, str) else k: v
                        for k, v in rule_config.get('escalation_channels', {}).items()
                    }
                )
                
                self.alert_rules[rule_name] = rule
                logger.info(f"Initialized alert rule: {rule_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize alert rule {rule_name}: {str(e)}")
    
    def _start_background_tasks(self):
        """Start background tasks for alert management."""
        if self.enabled:
            # Start cleanup task
            asyncio.create_task(self._cleanup_task())
            # Start auto-resolution task
            asyncio.create_task(self._auto_resolve_task())
    
    async def create_alert(
        self,
        rule_name: str,
        title: str,
        description: str,
        source: str,
        deployment_id: Optional[str] = None,
        environment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Alert]:
        """
        Create a new alert based on configured rules.
        
        Args:
            rule_name: Name of the alert rule to apply
            title: Alert title
            description: Alert description
            source: Source of the alert
            deployment_id: Optional deployment identifier
            environment: Optional environment name
            metadata: Optional additional metadata
            
        Returns:
            Created alert or None if throttled/suppressed
        """
        if not self.enabled:
            logger.debug("Alert system is disabled")
            return None
        
        if rule_name not in self.alert_rules:
            logger.error(f"Unknown alert rule: {rule_name}")
            return None
        
        rule = self.alert_rules[rule_name]
        
        # Check throttling
        if self._is_throttled(rule_name):
            logger.info(f"Alert throttled for rule: {rule_name}")
            return None
        
        # Create alert
        alert_id = f"{rule_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        alert = Alert(
            id=alert_id,
            rule_name=rule_name,
            severity=rule.severity,
            title=title,
            description=description,
            source=source,
            timestamp=datetime.utcnow(),
            deployment_id=deployment_id,
            environment=environment,
            metadata=metadata or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Update throttling state
        self._update_throttle_state(rule_name)
        
        # Send initial notification
        await self._send_alert_notification(alert, EscalationLevel.LEVEL_1)
        
        # Schedule escalation if needed
        if len(rule.escalation_levels) > 1:
            self._schedule_escalation(alert)
        
        # Call external callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {str(e)}")
        
        logger.info(f"Created alert: {alert_id} for rule: {rule_name}")
        return alert
    
    def _is_throttled(self, rule_name: str) -> bool:
        """Check if alert rule is currently throttled."""
        if rule_name not in self.alert_rules:
            return False
        
        rule = self.alert_rules[rule_name]
        throttle_state = self.throttle_states[rule_name]
        
        # Check if we're in a new window
        now = datetime.utcnow()
        window_elapsed = (now - throttle_state.window_start).total_seconds() / 60
        
        if window_elapsed >= rule.throttle_window:
            # Reset throttle state for new window
            throttle_state.alert_count = 0
            throttle_state.window_start = now
            throttle_state.suppressed_alerts.clear()
            return False
        
        # Check if we've exceeded the limit
        return throttle_state.alert_count >= rule.max_alerts_per_window
    
    def _update_throttle_state(self, rule_name: str):
        """Update throttling state after creating an alert."""
        throttle_state = self.throttle_states[rule_name]
        throttle_state.alert_count += 1
    
    async def _send_alert_notification(self, alert: Alert, escalation_level: EscalationLevel):
        """Send notification for an alert at specified escalation level."""
        rule = self.alert_rules[alert.rule_name]
        
        # Determine notification channels
        # Convert escalation_channels keys to EscalationLevel enum if they're strings
        escalation_channels = {}
        for level, channels_list in rule.escalation_channels.items():
            if isinstance(level, str):
                escalation_channels[EscalationLevel(level)] = channels_list
            else:
                escalation_channels[level] = channels_list
        
        if escalation_level in escalation_channels:
            channels = escalation_channels[escalation_level]
        else:
            channels = rule.notification_channels
        
        # Map alert severity to notification severity
        severity_mapping = {
            AlertSeverity.LOW: NotificationSeverity.INFO,
            AlertSeverity.MEDIUM: NotificationSeverity.WARNING,
            AlertSeverity.HIGH: NotificationSeverity.ERROR,
            AlertSeverity.CRITICAL: NotificationSeverity.CRITICAL,
            AlertSeverity.EMERGENCY: NotificationSeverity.CRITICAL
        }
        
        notification_severity = severity_mapping.get(alert.severity, NotificationSeverity.WARNING)
        
        # Create escalation-specific content
        escalation_prefix = ""
        if escalation_level != EscalationLevel.LEVEL_1:
            escalation_prefix = f"🚨 ESCALATED ({escalation_level.value.upper()}) - "
        
        # Enhanced metadata for escalation
        enhanced_metadata = alert.metadata.copy()
        enhanced_metadata.update({
            'alert_id': alert.id,
            'rule_name': alert.rule_name,
            'escalation_level': escalation_level.value,
            'escalation_count': alert.escalation_count,
            'source': alert.source
        })
        
        # Send notification
        results = await self.notification_manager.send_notification(
            title=f"{escalation_prefix}{alert.title}",
            content=alert.description,
            severity=notification_severity,
            deployment_id=alert.deployment_id,
            environment=alert.environment,
            metadata=enhanced_metadata,
            channels=channels if channels else None
        )
        
        # Track notification
        alert.notifications_sent.extend([r.channel_name for r in results if r.success])
        alert.last_notification = datetime.utcnow()
        
        logger.info(f"Sent alert notification for {alert.id} at {escalation_level.value}")
    
    def _schedule_escalation(self, alert: Alert):
        """Schedule escalation for an alert."""
        rule = self.alert_rules[alert.rule_name]
        
        if alert.escalation_count >= rule.max_escalations:
            logger.debug(f"Max escalations reached for alert: {alert.id}")
            return
        
        if alert.escalation_count >= len(rule.escalation_intervals):
            logger.debug(f"No more escalation intervals for alert: {alert.id}")
            return
        
        # Calculate next escalation time
        interval_minutes = rule.escalation_intervals[alert.escalation_count]
        next_escalation = datetime.utcnow() + timedelta(minutes=interval_minutes)
        alert.next_escalation = next_escalation
        
        # Schedule escalation task
        task = asyncio.create_task(self._escalate_alert_after_delay(alert, interval_minutes))
        self.escalation_tasks[alert.id] = task
        
        logger.debug(f"Scheduled escalation for alert {alert.id} in {interval_minutes} minutes")
    
    async def _escalate_alert_after_delay(self, alert: Alert, delay_minutes: int):
        """Escalate alert after specified delay."""
        try:
            await asyncio.sleep(delay_minutes * 60)
            
            # Check if alert is still active and not acknowledged/resolved
            if (alert.id in self.active_alerts and 
                not alert.acknowledged and 
                not alert.resolved):
                
                await self._escalate_alert(alert)
            else:
                logger.debug(f"Skipping escalation for resolved/acknowledged alert: {alert.id}")
                
        except asyncio.CancelledError:
            logger.debug(f"Escalation cancelled for alert: {alert.id}")
        except Exception as e:
            logger.error(f"Error during alert escalation: {str(e)}")
    
    async def _escalate_alert(self, alert: Alert):
        """Escalate an alert to the next level."""
        rule = self.alert_rules[alert.rule_name]
        
        # Update escalation state
        alert.escalation_count += 1
        alert.last_escalation = datetime.utcnow()
        
        # Determine next escalation level
        if alert.escalation_count < len(rule.escalation_levels):
            alert.current_escalation_level = rule.escalation_levels[alert.escalation_count]
        else:
            alert.current_escalation_level = rule.escalation_levels[-1]
        
        # Send escalated notification
        await self._send_alert_notification(alert, alert.current_escalation_level)
        
        # Schedule next escalation if needed
        if alert.escalation_count < rule.max_escalations:
            self._schedule_escalation(alert)
        
        logger.warning(f"Escalated alert {alert.id} to {alert.current_escalation_level.value}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert to stop escalation.
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: Person acknowledging the alert
            
        Returns:
            True if alert was acknowledged successfully
        """
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert not found for acknowledgment: {alert_id}")
            return False
        
        alert = self.active_alerts[alert_id]
        
        if alert.acknowledged:
            logger.info(f"Alert already acknowledged: {alert_id}")
            return True
        
        # Update alert state
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        # Cancel escalation task
        if alert_id in self.escalation_tasks:
            self.escalation_tasks[alert_id].cancel()
            del self.escalation_tasks[alert_id]
        
        # Send acknowledgment notification
        await self.notification_manager.send_notification(
            title=f"Alert Acknowledged: {alert.title}",
            content=f"Alert {alert_id} has been acknowledged by {acknowledged_by}",
            severity=NotificationSeverity.INFO,
            deployment_id=alert.deployment_id,
            environment=alert.environment,
            metadata={'alert_id': alert_id, 'acknowledged_by': acknowledged_by},
            channels=self.alert_rules[alert.rule_name].notification_channels
        )
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_note: str = "") -> bool:
        """
        Resolve an alert and remove it from active alerts.
        
        Args:
            alert_id: Alert identifier
            resolved_by: Person resolving the alert
            resolution_note: Optional resolution note
            
        Returns:
            True if alert was resolved successfully
        """
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert not found for resolution: {alert_id}")
            return False
        
        alert = self.active_alerts[alert_id]
        
        # Update alert state
        alert.resolved = True
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.utcnow()
        if resolution_note:
            alert.metadata['resolution_note'] = resolution_note
        
        # Cancel escalation task
        if alert_id in self.escalation_tasks:
            self.escalation_tasks[alert_id].cancel()
            del self.escalation_tasks[alert_id]
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Send resolution notification
        await self.notification_manager.send_notification(
            title=f"Alert Resolved: {alert.title}",
            content=f"Alert {alert_id} has been resolved by {resolved_by}. {resolution_note}",
            severity=NotificationSeverity.INFO,
            deployment_id=alert.deployment_id,
            environment=alert.environment,
            metadata={
                'alert_id': alert_id, 
                'resolved_by': resolved_by,
                'resolution_note': resolution_note
            },
            channels=self.alert_rules[alert.rule_name].notification_channels
        )
        
        logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
        return True
    
    async def _cleanup_task(self):
        """Background task to clean up old alerts and throttle states."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                now = datetime.utcnow()
                
                # Clean up old throttle states
                for rule_name, throttle_state in list(self.throttle_states.items()):
                    window_elapsed = (now - throttle_state.window_start).total_seconds() / 60
                    rule = self.alert_rules.get(rule_name)
                    
                    if rule and window_elapsed >= rule.throttle_window * 2:
                        # Reset old throttle states
                        throttle_state.alert_count = 0
                        throttle_state.window_start = now
                        throttle_state.suppressed_alerts.clear()
                
                # Clean up old alert history (keep last 1000 alerts)
                if len(self.alert_history) > 1000:
                    self.alert_history = self.alert_history[-1000:]
                
                logger.debug("Completed alert system cleanup")
                
            except Exception as e:
                logger.error(f"Error in alert cleanup task: {str(e)}")
    
    async def _auto_resolve_task(self):
        """Background task to auto-resolve alerts based on rules."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.utcnow()
                alerts_to_resolve = []
                
                for alert_id, alert in self.active_alerts.items():
                    rule = self.alert_rules.get(alert.rule_name)
                    
                    if (rule and rule.auto_resolve and 
                        not alert.acknowledged and not alert.resolved):
                        
                        # Check if auto-resolve timeout has passed
                        elapsed_minutes = (now - alert.timestamp).total_seconds() / 60
                        
                        if elapsed_minutes >= rule.auto_resolve_timeout:
                            alerts_to_resolve.append((alert_id, alert))
                
                # Auto-resolve expired alerts
                for alert_id, alert in alerts_to_resolve:
                    await self.resolve_alert(
                        alert_id, 
                        "system", 
                        f"Auto-resolved after {rule.auto_resolve_timeout} minutes"
                    )
                    logger.info(f"Auto-resolved alert: {alert_id}")
                
            except Exception as e:
                logger.error(f"Error in auto-resolve task: {str(e)}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get list of all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID from active alerts or history."""
        if alert_id in self.active_alerts:
            return self.active_alerts[alert_id]
        
        for alert in self.alert_history:
            if alert.id == alert_id:
                return alert
        
        return None
    
    def get_alerts_by_rule(self, rule_name: str) -> List[Alert]:
        """Get all alerts (active and historical) for a specific rule."""
        alerts = []
        
        # Add active alerts
        for alert in self.active_alerts.values():
            if alert.rule_name == rule_name:
                alerts.append(alert)
        
        # Add historical alerts
        for alert in self.alert_history:
            if alert.rule_name == rule_name and alert.id not in self.active_alerts:
                alerts.append(alert)
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'enabled': self.enabled,
            'active_alerts_count': len(self.active_alerts),
            'total_rules': len(self.alert_rules),
            'escalation_tasks_count': len(self.escalation_tasks),
            'throttle_states': {
                rule_name: {
                    'alert_count': state.alert_count,
                    'window_start': state.window_start.isoformat(),
                    'suppressed_count': len(state.suppressed_alerts)
                }
                for rule_name, state in self.throttle_states.items()
            },
            'alert_history_size': len(self.alert_history)
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function to be called when alerts are created."""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[Alert], None]):
        """Remove alert callback function."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)