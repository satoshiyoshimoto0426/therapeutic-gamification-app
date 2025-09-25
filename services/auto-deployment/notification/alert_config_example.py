"""
Example configuration for the alert and escalation system.

This module provides example configurations for different alert scenarios
and demonstrates how to set up alert rules, escalation procedures, and
notification channels.
"""

from typing import Dict, Any

# Example alert system configuration
ALERT_SYSTEM_CONFIG: Dict[str, Any] = {
    'enabled': True,
    'rules': {
        # Critical deployment failures
        'deployment_failure': {
            'severity': 'critical',
            'conditions': {
                'deployment_status': 'failed',
                'error_type': ['build_error', 'deployment_error', 'health_check_failure']
            },
            'escalation_levels': ['level_1', 'level_2', 'level_3'],
            'escalation_intervals': [5, 15, 30],  # Minutes between escalations
            'max_escalations': 3,
            'throttle_window': 30,  # Minutes
            'max_alerts_per_window': 3,
            'auto_resolve': False,
            'notification_channels': ['slack-ops', 'email-oncall'],
            'escalation_channels': {
                'level_2': ['slack-leads', 'email-leads'],
                'level_3': ['slack-management', 'email-management']
            }
        },
        
        # Health check failures
        'health_check_failure': {
            'severity': 'high',
            'conditions': {
                'health_status': 'unhealthy',
                'consecutive_failures': {'>=': 3}
            },
            'escalation_levels': ['level_1', 'level_2'],
            'escalation_intervals': [10, 20],
            'max_escalations': 2,
            'throttle_window': 15,
            'max_alerts_per_window': 5,
            'auto_resolve': True,
            'auto_resolve_timeout': 10,  # Auto-resolve after 10 minutes
            'notification_channels': ['slack-ops'],
            'escalation_channels': {
                'level_2': ['slack-leads', 'email-oncall']
            }
        },
        
        # Performance degradation
        'performance_degradation': {
            'severity': 'medium',
            'conditions': {
                'response_time': {'>=': 2000},  # ms
                'error_rate': {'>=': 0.05}  # 5%
            },
            'escalation_levels': ['level_1', 'level_2'],
            'escalation_intervals': [15, 30],
            'max_escalations': 2,
            'throttle_window': 60,
            'max_alerts_per_window': 3,
            'auto_resolve': True,
            'auto_resolve_timeout': 20,
            'notification_channels': ['slack-ops'],
            'escalation_channels': {
                'level_2': ['slack-leads']
            }
        },
        
        # Security alerts
        'security_violation': {
            'severity': 'emergency',
            'conditions': {
                'security_scan_result': 'critical_vulnerability',
                'authentication_failure': {'>=': 10}
            },
            'escalation_levels': ['level_1', 'level_2', 'level_3', 'level_4'],
            'escalation_intervals': [2, 5, 10, 15],  # Rapid escalation
            'max_escalations': 4,
            'throttle_window': 10,  # Short window for security
            'max_alerts_per_window': 2,
            'auto_resolve': False,
            'notification_channels': ['slack-security', 'email-security'],
            'escalation_channels': {
                'level_2': ['slack-security-leads', 'email-security-leads'],
                'level_3': ['slack-management', 'email-management'],
                'level_4': ['slack-executives', 'email-executives']
            }
        },
        
        # Resource exhaustion
        'resource_exhaustion': {
            'severity': 'high',
            'conditions': {
                'cpu_usage': {'>=': 90},
                'memory_usage': {'>=': 95},
                'disk_usage': {'>=': 90}
            },
            'escalation_levels': ['level_1', 'level_2'],
            'escalation_intervals': [5, 15],
            'max_escalations': 2,
            'throttle_window': 30,
            'max_alerts_per_window': 2,
            'auto_resolve': True,
            'auto_resolve_timeout': 15,
            'notification_channels': ['slack-ops', 'email-oncall'],
            'escalation_channels': {
                'level_2': ['slack-leads', 'email-leads']
            }
        },
        
        # Rollback triggered
        'rollback_triggered': {
            'severity': 'critical',
            'conditions': {
                'rollback_reason': ['health_check_failure', 'performance_degradation', 'error_spike']
            },
            'escalation_levels': ['level_1', 'level_2'],
            'escalation_intervals': [5, 15],
            'max_escalations': 2,
            'throttle_window': 60,
            'max_alerts_per_window': 1,  # Only one rollback alert per hour
            'auto_resolve': False,
            'notification_channels': ['slack-ops', 'slack-leads', 'email-oncall'],
            'escalation_channels': {
                'level_2': ['slack-management', 'email-management']
            }
        },
        
        # Configuration drift
        'configuration_drift': {
            'severity': 'medium',
            'conditions': {
                'config_validation': 'failed',
                'drift_severity': ['medium', 'high']
            },
            'escalation_levels': ['level_1'],
            'escalation_intervals': [60],  # Single notification
            'max_escalations': 1,
            'throttle_window': 240,  # 4 hours
            'max_alerts_per_window': 1,
            'auto_resolve': True,
            'auto_resolve_timeout': 60,
            'notification_channels': ['slack-ops']
        },
        
        # Dependency failures
        'dependency_failure': {
            'severity': 'high',
            'conditions': {
                'dependency_status': 'unavailable',
                'dependency_type': ['database', 'external_api', 'cache']
            },
            'escalation_levels': ['level_1', 'level_2'],
            'escalation_intervals': [10, 20],
            'max_escalations': 2,
            'throttle_window': 30,
            'max_alerts_per_window': 3,
            'auto_resolve': True,
            'auto_resolve_timeout': 15,
            'notification_channels': ['slack-ops'],
            'escalation_channels': {
                'level_2': ['slack-leads', 'email-oncall']
            }
        }
    }
}

# Example notification manager configuration with alert system
NOTIFICATION_CONFIG_WITH_ALERTS: Dict[str, Any] = {
    'enabled': True,
    'channels': {
        # Slack channels
        'slack-ops': {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
            'channel': '#ops-alerts',
            'username': 'Auto-Deploy Bot',
            'severity_filter': ['info', 'warning', 'error', 'critical']
        },
        'slack-leads': {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
            'channel': '#team-leads',
            'username': 'Auto-Deploy Bot',
            'severity_filter': ['warning', 'error', 'critical']
        },
        'slack-management': {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
            'channel': '#management',
            'username': 'Auto-Deploy Bot',
            'severity_filter': ['error', 'critical']
        },
        'slack-security': {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/SECURITY/WEBHOOK',
            'channel': '#security-alerts',
            'username': 'Security Alert Bot',
            'severity_filter': ['critical']
        },
        'slack-executives': {
            'type': 'slack',
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/EXEC/WEBHOOK',
            'channel': '#executives',
            'username': 'Critical Alert Bot',
            'severity_filter': ['critical']
        },
        
        # Email channels
        'email-oncall': {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'alerts@company.com',
            'password': 'your-email-password',
            'from_address': 'alerts@company.com',
            'to_addresses': ['oncall@company.com'],
            'severity_filter': ['error', 'critical']
        },
        'email-leads': {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'alerts@company.com',
            'password': 'your-email-password',
            'from_address': 'alerts@company.com',
            'to_addresses': ['leads@company.com'],
            'severity_filter': ['error', 'critical']
        },
        'email-management': {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'alerts@company.com',
            'password': 'your-email-password',
            'from_address': 'alerts@company.com',
            'to_addresses': ['management@company.com'],
            'severity_filter': ['critical']
        },
        'email-security': {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'security-alerts@company.com',
            'password': 'your-security-password',
            'from_address': 'security-alerts@company.com',
            'to_addresses': ['security-team@company.com'],
            'severity_filter': ['critical']
        },
        'email-executives': {
            'type': 'email',
            'enabled': True,
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'critical-alerts@company.com',
            'password': 'your-exec-password',
            'from_address': 'critical-alerts@company.com',
            'to_addresses': ['executives@company.com'],
            'severity_filter': ['critical']
        }
    },
    
    # Alert system configuration
    'alert_system': ALERT_SYSTEM_CONFIG
}

# Example usage patterns
USAGE_EXAMPLES = {
    'deployment_failure_alert': {
        'rule_name': 'deployment_failure',
        'title': 'Production Deployment Failed',
        'description': 'Deployment to production environment failed during health check phase. Error: Service unhealthy after 5 minutes.',
        'source': 'deployment_engine',
        'deployment_id': 'deploy-prod-20240108-001',
        'environment': 'production',
        'metadata': {
            'error_code': 'HEALTH_CHECK_TIMEOUT',
            'service_name': 'api-service',
            'revision': 'api-service-00042-abc',
            'build_id': 'build-12345'
        }
    },
    
    'security_violation_alert': {
        'rule_name': 'security_violation',
        'title': 'Critical Security Vulnerability Detected',
        'description': 'Security scan detected critical vulnerability in deployed code. CVE-2024-1234 with CVSS score 9.8.',
        'source': 'security_scanner',
        'deployment_id': 'deploy-staging-20240108-002',
        'environment': 'staging',
        'metadata': {
            'vulnerability_id': 'CVE-2024-1234',
            'cvss_score': 9.8,
            'affected_package': 'example-lib@1.2.3',
            'scan_id': 'scan-67890'
        }
    },
    
    'performance_degradation_alert': {
        'rule_name': 'performance_degradation',
        'title': 'Performance Degradation Detected',
        'description': 'API response time increased to 3.2s (threshold: 2.0s) and error rate is 7.5% (threshold: 5%).',
        'source': 'performance_monitor',
        'deployment_id': 'deploy-prod-20240108-001',
        'environment': 'production',
        'metadata': {
            'avg_response_time_ms': 3200,
            'error_rate_percent': 7.5,
            'requests_per_minute': 1250,
            'affected_endpoints': ['/api/users', '/api/tasks']
        }
    }
}

# Configuration validation helpers
def validate_alert_config(config: Dict[str, Any]) -> bool:
    """
    Validate alert system configuration.
    
    Args:
        config: Alert system configuration to validate
        
    Returns:
        True if configuration is valid
    """
    required_fields = ['enabled', 'rules']
    
    for field in required_fields:
        if field not in config:
            print(f"Missing required field: {field}")
            return False
    
    # Validate rules
    for rule_name, rule_config in config['rules'].items():
        if not validate_rule_config(rule_name, rule_config):
            return False
    
    return True

def validate_rule_config(rule_name: str, rule_config: Dict[str, Any]) -> bool:
    """
    Validate individual alert rule configuration.
    
    Args:
        rule_name: Name of the rule
        rule_config: Rule configuration to validate
        
    Returns:
        True if rule configuration is valid
    """
    required_fields = [
        'severity', 'conditions', 'escalation_levels', 
        'escalation_intervals', 'max_escalations'
    ]
    
    for field in required_fields:
        if field not in rule_config:
            print(f"Rule {rule_name} missing required field: {field}")
            return False
    
    # Validate severity
    valid_severities = ['low', 'medium', 'high', 'critical', 'emergency']
    if rule_config['severity'] not in valid_severities:
        print(f"Rule {rule_name} has invalid severity: {rule_config['severity']}")
        return False
    
    # Validate escalation levels
    valid_levels = ['level_1', 'level_2', 'level_3', 'level_4']
    for level in rule_config['escalation_levels']:
        if level not in valid_levels:
            print(f"Rule {rule_name} has invalid escalation level: {level}")
            return False
    
    # Validate escalation intervals
    if len(rule_config['escalation_intervals']) < len(rule_config['escalation_levels']) - 1:
        print(f"Rule {rule_name} has insufficient escalation intervals")
        return False
    
    return True

# Example integration with deployment orchestrator
def create_alert_system_integration():
    """
    Example of how to integrate alert system with deployment orchestrator.
    """
    from ..notification_manager import NotificationManager
    from ..alert_system import AlertSystem
    
    # Initialize notification manager
    notification_manager = NotificationManager(NOTIFICATION_CONFIG_WITH_ALERTS)
    
    # Initialize alert system
    alert_system = AlertSystem(notification_manager, ALERT_SYSTEM_CONFIG)
    
    # Example callback for deployment events
    async def handle_deployment_failure(deployment_id: str, error_details: Dict[str, Any]):
        """Handle deployment failure by creating alert."""
        await alert_system.create_alert(
            rule_name='deployment_failure',
            title=f'Deployment Failed: {deployment_id}',
            description=f"Deployment failed with error: {error_details.get('error_message', 'Unknown error')}",
            source='deployment_orchestrator',
            deployment_id=deployment_id,
            environment=error_details.get('environment', 'unknown'),
            metadata=error_details
        )
    
    # Example callback for health check failures
    async def handle_health_check_failure(service_name: str, health_details: Dict[str, Any]):
        """Handle health check failure by creating alert."""
        await alert_system.create_alert(
            rule_name='health_check_failure',
            title=f'Health Check Failed: {service_name}',
            description=f"Service {service_name} failed health check: {health_details.get('error', 'Unknown error')}",
            source='health_monitor',
            deployment_id=health_details.get('deployment_id'),
            environment=health_details.get('environment', 'unknown'),
            metadata=health_details
        )
    
    return alert_system, handle_deployment_failure, handle_health_check_failure