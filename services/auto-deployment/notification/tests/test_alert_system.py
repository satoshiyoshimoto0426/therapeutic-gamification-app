"""
Tests for the alert and escalation system.

This module contains comprehensive tests for alert severity classification,
escalation procedures, notification scheduling, and throttling mechanisms.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from ..alert_system import (
    AlertSystem, AlertSeverity, EscalationLevel, AlertRule, Alert, ThrottleState
)
from ..notification_manager import NotificationManager
from ..base import NotificationSeverity


class TestAlertSystem:
    """Test cases for AlertSystem class."""
    
    @pytest.fixture
    def mock_notification_manager(self):
        """Create mock notification manager."""
        manager = Mock(spec=NotificationManager)
        manager.send_notification = AsyncMock(return_value=[])
        return manager
    
    @pytest.fixture
    def alert_config(self):
        """Create test alert system configuration."""
        return {
            'enabled': True,
            'rules': {
                'deployment_failure': {
                    'severity': 'critical',
                    'conditions': {'deployment_status': 'failed'},
                    'escalation_levels': ['level_1', 'level_2', 'level_3'],
                    'escalation_intervals': [5, 15, 30],
                    'max_escalations': 3,
                    'throttle_window': 30,
                    'max_alerts_per_window': 3,
                    'auto_resolve': False,
                    'notification_channels': ['slack-ops', 'email-team'],
                    'escalation_channels': {
                        'level_2': ['slack-leads', 'email-leads'],
                        'level_3': ['slack-mgmt', 'email-mgmt']
                    }
                },
                'health_check_failure': {
                    'severity': 'high',
                    'conditions': {'health_status': 'unhealthy'},
                    'escalation_levels': ['level_1', 'level_2'],
                    'escalation_intervals': [10, 20],
                    'max_escalations': 2,
                    'throttle_window': 15,
                    'max_alerts_per_window': 5,
                    'auto_resolve': True,
                    'auto_resolve_timeout': 10,
                    'notification_channels': ['slack-ops']
                }
            }
        }
    
    @pytest.fixture
    def alert_system(self, mock_notification_manager, alert_config):
        """Create AlertSystem instance for testing."""
        with patch('asyncio.create_task'):
            return AlertSystem(mock_notification_manager, alert_config)
    
    def test_initialization(self, alert_system, alert_config):
        """Test alert system initialization."""
        assert alert_system.enabled is True
        assert len(alert_system.alert_rules) == 2
        assert 'deployment_failure' in alert_system.alert_rules
        assert 'health_check_failure' in alert_system.alert_rules
        
        # Test rule configuration
        deployment_rule = alert_system.alert_rules['deployment_failure']
        assert deployment_rule.severity == AlertSeverity.CRITICAL
        assert deployment_rule.max_escalations == 3
        assert deployment_rule.throttle_window == 30
        assert deployment_rule.max_alerts_per_window == 3
        assert deployment_rule.auto_resolve is False
    
    @pytest.mark.asyncio
    async def test_create_alert_basic(self, alert_system, mock_notification_manager):
        """Test basic alert creation."""
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Deployment Failed',
            description='Production deployment failed with error code 500',
            source='deployment_engine',
            deployment_id='deploy-123',
            environment='production'
        )
        
        assert alert is not None
        assert alert.rule_name == 'deployment_failure'
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == 'Deployment Failed'
        assert alert.deployment_id == 'deploy-123'
        assert alert.environment == 'production'
        assert alert.current_escalation_level == EscalationLevel.LEVEL_1
        assert alert.escalation_count == 0
        assert not alert.acknowledged
        assert not alert.resolved
        
        # Verify alert is stored
        assert alert.id in alert_system.active_alerts
        assert len(alert_system.alert_history) == 1
        
        # Verify notification was sent
        mock_notification_manager.send_notification.assert_called_once()
        call_args = mock_notification_manager.send_notification.call_args
        assert call_args[1]['title'] == 'Deployment Failed'
        assert call_args[1]['severity'] == NotificationSeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_create_alert_unknown_rule(self, alert_system):
        """Test creating alert with unknown rule."""
        alert = await alert_system.create_alert(
            rule_name='unknown_rule',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        assert alert is None
        assert len(alert_system.active_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_create_alert_disabled_system(self, mock_notification_manager, alert_config):
        """Test creating alert when system is disabled."""
        alert_config['enabled'] = False
        with patch('asyncio.create_task'):
            alert_system = AlertSystem(mock_notification_manager, alert_config)
        
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        assert alert is None
    
    def test_throttling_mechanism(self, alert_system):
        """Test alert throttling mechanism."""
        rule_name = 'deployment_failure'
        
        # Initially not throttled
        assert not alert_system._is_throttled(rule_name)
        
        # Simulate alerts up to the limit
        for i in range(3):  # max_alerts_per_window = 3
            alert_system._update_throttle_state(rule_name)
        
        # Should now be throttled
        assert alert_system._is_throttled(rule_name)
        
        # Test throttle state
        throttle_state = alert_system.throttle_states[rule_name]
        assert throttle_state.alert_count == 3
    
    def test_throttling_window_reset(self, alert_system):
        """Test throttling window reset."""
        rule_name = 'deployment_failure'
        
        # Set up throttle state with old window
        throttle_state = alert_system.throttle_states[rule_name]
        throttle_state.alert_count = 5
        throttle_state.window_start = datetime.utcnow() - timedelta(minutes=35)  # Older than window
        
        # Should not be throttled due to window reset
        assert not alert_system._is_throttled(rule_name)
        
        # Verify state was reset
        assert throttle_state.alert_count == 0
        assert len(throttle_state.suppressed_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_alert_escalation_scheduling(self, alert_system):
        """Test alert escalation scheduling."""
        # Create alert
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        # Verify escalation is scheduled
        assert alert.id in alert_system.escalation_tasks
        assert alert.next_escalation is not None
        
        # Verify escalation timing
        expected_time = alert.timestamp + timedelta(minutes=5)  # First interval
        time_diff = abs((alert.next_escalation - expected_time).total_seconds())
        assert time_diff < 1  # Within 1 second
    
    @pytest.mark.asyncio
    async def test_alert_escalation_execution(self, alert_system, mock_notification_manager):
        """Test alert escalation execution."""
        # Create alert
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        # Reset mock to clear initial notification
        mock_notification_manager.send_notification.reset_mock()
        
        # Manually trigger escalation
        await alert_system._escalate_alert(alert)
        
        # Verify escalation state
        assert alert.escalation_count == 1
        assert alert.current_escalation_level == EscalationLevel.LEVEL_2
        assert alert.last_escalation is not None
        
        # Verify escalated notification was sent
        mock_notification_manager.send_notification.assert_called_once()
        call_args = mock_notification_manager.send_notification.call_args
        assert '🚨 ESCALATED (LEVEL_2)' in call_args[1]['title']
        assert call_args[1]['channels'] == ['slack-leads', 'email-leads']
    
    @pytest.mark.asyncio
    async def test_alert_acknowledgment(self, alert_system, mock_notification_manager):
        """Test alert acknowledgment."""
        # Create alert
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        # Reset mock
        mock_notification_manager.send_notification.reset_mock()
        
        # Acknowledge alert
        result = await alert_system.acknowledge_alert(alert.id, 'john.doe')
        
        assert result is True
        assert alert.acknowledged is True
        assert alert.acknowledged_by == 'john.doe'
        assert alert.acknowledged_at is not None
        
        # Verify escalation task was cancelled
        assert alert.id not in alert_system.escalation_tasks
        
        # Verify acknowledgment notification was sent
        mock_notification_manager.send_notification.assert_called_once()
        call_args = mock_notification_manager.send_notification.call_args
        assert 'Alert Acknowledged' in call_args[1]['title']
    
    @pytest.mark.asyncio
    async def test_alert_resolution(self, alert_system, mock_notification_manager):
        """Test alert resolution."""
        # Create alert
        alert = await alert_system.create_alert(
            rule_name='deployment_failure',
            title='Test Alert',
            description='Test description',
            source='test'
        )
        
        alert_id = alert.id
        
        # Reset mock
        mock_notification_manager.send_notification.reset_mock()
        
        # Resolve alert
        result = await alert_system.resolve_alert(
            alert_id, 
            'jane.doe', 
            'Fixed deployment configuration'
        )
        
        assert result is True
        assert alert.resolved is True
        assert alert.resolved_by == 'jane.doe'
        assert alert.resolved_at is not None
        assert alert.metadata['resolution_note'] == 'Fixed deployment configuration'
        
        # Verify alert was removed from active alerts
        assert alert_id not in alert_system.active_alerts
        
        # Verify escalation task was cancelled
        assert alert_id not in alert_system.escalation_tasks
        
        # Verify resolution notification was sent
        mock_notification_manager.send_notification.assert_called_once()
        call_args = mock_notification_manager.send_notification.call_args
        assert 'Alert Resolved' in call_args[1]['title']
    
    @pytest.mark.asyncio
    async def test_alert_acknowledgment_nonexistent(self, alert_system):
        """Test acknowledging non-existent alert."""
        result = await alert_system.acknowledge_alert('nonexistent-id', 'user')
        assert result is False
    
    @pytest.mark.asyncio
    async def test_alert_resolution_nonexistent(self, alert_system):
        """Test resolving non-existent alert."""
        result = await alert_system.resolve_alert('nonexistent-id', 'user', 'note')
        assert result is False
    
    def test_get_active_alerts(self, alert_system):
        """Test getting active alerts."""
        # Initially empty
        alerts = alert_system.get_active_alerts()
        assert len(alerts) == 0
        
        # Add some test alerts
        alert1 = Alert(
            id='alert-1',
            rule_name='test_rule',
            severity=AlertSeverity.HIGH,
            title='Test Alert 1',
            description='Description 1',
            source='test',
            timestamp=datetime.utcnow()
        )
        alert2 = Alert(
            id='alert-2',
            rule_name='test_rule',
            severity=AlertSeverity.MEDIUM,
            title='Test Alert 2',
            description='Description 2',
            source='test',
            timestamp=datetime.utcnow()
        )
        
        alert_system.active_alerts['alert-1'] = alert1
        alert_system.active_alerts['alert-2'] = alert2
        
        alerts = alert_system.get_active_alerts()
        assert len(alerts) == 2
        assert alert1 in alerts
        assert alert2 in alerts
    
    def test_get_alert_by_id(self, alert_system):
        """Test getting alert by ID."""
        # Test with non-existent alert
        alert = alert_system.get_alert_by_id('nonexistent')
        assert alert is None
        
        # Add test alert
        test_alert = Alert(
            id='test-alert',
            rule_name='test_rule',
            severity=AlertSeverity.HIGH,
            title='Test Alert',
            description='Description',
            source='test',
            timestamp=datetime.utcnow()
        )
        
        alert_system.active_alerts['test-alert'] = test_alert
        
        # Test finding active alert
        alert = alert_system.get_alert_by_id('test-alert')
        assert alert is test_alert
        
        # Move to history and test finding historical alert
        del alert_system.active_alerts['test-alert']
        alert_system.alert_history.append(test_alert)
        
        alert = alert_system.get_alert_by_id('test-alert')
        assert alert is test_alert
    
    def test_get_alerts_by_rule(self, alert_system):
        """Test getting alerts by rule name."""
        # Create test alerts
        alert1 = Alert(
            id='alert-1',
            rule_name='rule_a',
            severity=AlertSeverity.HIGH,
            title='Alert 1',
            description='Description 1',
            source='test',
            timestamp=datetime.utcnow()
        )
        alert2 = Alert(
            id='alert-2',
            rule_name='rule_b',
            severity=AlertSeverity.MEDIUM,
            title='Alert 2',
            description='Description 2',
            source='test',
            timestamp=datetime.utcnow()
        )
        alert3 = Alert(
            id='alert-3',
            rule_name='rule_a',
            severity=AlertSeverity.LOW,
            title='Alert 3',
            description='Description 3',
            source='test',
            timestamp=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # Add to active and history
        alert_system.active_alerts['alert-1'] = alert1
        alert_system.active_alerts['alert-2'] = alert2
        alert_system.alert_history.extend([alert1, alert2, alert3])
        
        # Test getting alerts for rule_a
        alerts = alert_system.get_alerts_by_rule('rule_a')
        assert len(alerts) == 2
        assert alert1 in alerts
        assert alert3 in alerts
        assert alert2 not in alerts
        
        # Verify sorting (newest first)
        assert alerts[0] is alert3  # Newer timestamp
        assert alerts[1] is alert1
    
    def test_get_system_status(self, alert_system):
        """Test getting system status."""
        # Add some test data
        alert = Alert(
            id='test-alert',
            rule_name='test_rule',
            severity=AlertSeverity.HIGH,
            title='Test Alert',
            description='Description',
            source='test',
            timestamp=datetime.utcnow()
        )
        
        alert_system.active_alerts['test-alert'] = alert
        alert_system.alert_history.append(alert)
        alert_system.throttle_states['test_rule'].alert_count = 2
        
        status = alert_system.get_system_status()
        
        assert status['enabled'] is True
        assert status['active_alerts_count'] == 1
        assert status['total_rules'] == 2
        assert status['alert_history_size'] == 1
        assert 'throttle_states' in status
        assert 'test_rule' in status['throttle_states']
        assert status['throttle_states']['test_rule']['alert_count'] == 2
    
    def test_alert_callbacks(self, alert_system):
        """Test alert callback functionality."""
        callback_calls = []
        
        def test_callback(alert: Alert):
            callback_calls.append(alert.id)
        
        # Add callback
        alert_system.add_alert_callback(test_callback)
        assert test_callback in alert_system.alert_callbacks
        
        # Remove callback
        alert_system.remove_alert_callback(test_callback)
        assert test_callback not in alert_system.alert_callbacks
    
    @pytest.mark.asyncio
    async def test_severity_mapping(self, alert_system, mock_notification_manager):
        """Test alert severity to notification severity mapping."""
        # Test different severity levels
        severity_tests = [
            (AlertSeverity.LOW, NotificationSeverity.INFO),
            (AlertSeverity.MEDIUM, NotificationSeverity.WARNING),
            (AlertSeverity.HIGH, NotificationSeverity.ERROR),
            (AlertSeverity.CRITICAL, NotificationSeverity.CRITICAL),
            (AlertSeverity.EMERGENCY, NotificationSeverity.CRITICAL)
        ]
        
        for alert_severity, expected_notification_severity in severity_tests:
            # Create rule with specific severity
            rule_name = f'test_rule_{alert_severity.value}'
            alert_system.alert_rules[rule_name] = AlertRule(
                name=rule_name,
                severity=alert_severity,
                conditions={},
                escalation_levels=[EscalationLevel.LEVEL_1],
                escalation_intervals=[15],
                notification_channels=['test-channel']
            )
            
            # Reset mock
            mock_notification_manager.send_notification.reset_mock()
            
            # Create alert
            await alert_system.create_alert(
                rule_name=rule_name,
                title=f'Test {alert_severity.value}',
                description='Test description',
                source='test'
            )
            
            # Verify correct notification severity was used
            call_args = mock_notification_manager.send_notification.call_args
            assert call_args[1]['severity'] == expected_notification_severity


class TestAlertRule:
    """Test cases for AlertRule class."""
    
    def test_alert_rule_creation(self):
        """Test AlertRule creation with all parameters."""
        rule = AlertRule(
            name='test_rule',
            severity=AlertSeverity.HIGH,
            conditions={'status': 'failed'},
            escalation_levels=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
            escalation_intervals=[10, 30],
            max_escalations=2,
            throttle_window=60,
            max_alerts_per_window=5,
            auto_resolve=True,
            auto_resolve_timeout=15,
            notification_channels=['slack', 'email'],
            escalation_channels={
                EscalationLevel.LEVEL_2: ['management-slack']
            }
        )
        
        assert rule.name == 'test_rule'
        assert rule.severity == AlertSeverity.HIGH
        assert rule.conditions == {'status': 'failed'}
        assert len(rule.escalation_levels) == 2
        assert rule.escalation_intervals == [10, 30]
        assert rule.max_escalations == 2
        assert rule.throttle_window == 60
        assert rule.max_alerts_per_window == 5
        assert rule.auto_resolve is True
        assert rule.auto_resolve_timeout == 15
        assert rule.notification_channels == ['slack', 'email']
        assert EscalationLevel.LEVEL_2 in rule.escalation_channels


class TestAlert:
    """Test cases for Alert class."""
    
    def test_alert_creation(self):
        """Test Alert creation with all parameters."""
        timestamp = datetime.utcnow()
        metadata = {'key': 'value'}
        
        alert = Alert(
            id='test-alert-123',
            rule_name='test_rule',
            severity=AlertSeverity.CRITICAL,
            title='Test Alert',
            description='This is a test alert',
            source='test_source',
            timestamp=timestamp,
            deployment_id='deploy-456',
            environment='production',
            metadata=metadata
        )
        
        assert alert.id == 'test-alert-123'
        assert alert.rule_name == 'test_rule'
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == 'Test Alert'
        assert alert.description == 'This is a test alert'
        assert alert.source == 'test_source'
        assert alert.timestamp == timestamp
        assert alert.deployment_id == 'deploy-456'
        assert alert.environment == 'production'
        assert alert.metadata == metadata
        
        # Test default values
        assert alert.current_escalation_level == EscalationLevel.LEVEL_1
        assert alert.escalation_count == 0
        assert alert.last_escalation is None
        assert alert.next_escalation is None
        assert alert.acknowledged is False
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None
        assert alert.resolved is False
        assert alert.resolved_by is None
        assert alert.resolved_at is None
        assert alert.notifications_sent == []
        assert alert.last_notification is None


class TestThrottleState:
    """Test cases for ThrottleState class."""
    
    def test_throttle_state_creation(self):
        """Test ThrottleState creation with default values."""
        state = ThrottleState()
        
        assert state.alert_count == 0
        assert isinstance(state.window_start, datetime)
        assert state.suppressed_alerts == []
    
    def test_throttle_state_with_values(self):
        """Test ThrottleState creation with specific values."""
        window_start = datetime.utcnow()
        suppressed = ['alert-1', 'alert-2']
        
        state = ThrottleState(
            alert_count=5,
            window_start=window_start,
            suppressed_alerts=suppressed
        )
        
        assert state.alert_count == 5
        assert state.window_start == window_start
        assert state.suppressed_alerts == suppressed


@pytest.mark.asyncio
async def test_integration_alert_lifecycle():
    """Integration test for complete alert lifecycle."""
    # Setup
    mock_notification_manager = Mock(spec=NotificationManager)
    mock_notification_manager.send_notification = AsyncMock(return_value=[])
    
    config = {
        'enabled': True,
        'rules': {
            'test_rule': {
                'severity': 'high',
                'conditions': {},
                'escalation_levels': ['level_1', 'level_2'],
                'escalation_intervals': [1, 2],  # Short intervals for testing
                'max_escalations': 2,
                'throttle_window': 60,
                'max_alerts_per_window': 10,
                'auto_resolve': False,
                'notification_channels': ['test-channel']
            }
        }
    }
    
    with patch('asyncio.create_task'):
        alert_system = AlertSystem(mock_notification_manager, config)
    
    # Create alert
    alert = await alert_system.create_alert(
        rule_name='test_rule',
        title='Integration Test Alert',
        description='Testing complete lifecycle',
        source='integration_test'
    )
    
    assert alert is not None
    assert len(alert_system.active_alerts) == 1
    
    # Acknowledge alert
    ack_result = await alert_system.acknowledge_alert(alert.id, 'test_user')
    assert ack_result is True
    assert alert.acknowledged is True
    
    # Resolve alert
    resolve_result = await alert_system.resolve_alert(
        alert.id, 
        'test_user', 
        'Integration test completed'
    )
    assert resolve_result is True
    assert alert.resolved is True
    assert len(alert_system.active_alerts) == 0
    
    # Verify notifications were sent (create, acknowledge, resolve)
    assert mock_notification_manager.send_notification.call_count == 3