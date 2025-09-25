"""
Monitoring dashboard and alerting system for auto-deployment.

This module provides real-time monitoring dashboard, alerting system for threshold breaches,
and monitoring data persistence layer.
"""

import asyncio
import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
import logging
import threading
import time
from collections import defaultdict

try:
    from .health_check import HealthCheckFramework, HealthCheckResult, HealthStatus
    from .performance_monitor import PerformanceMonitor, Alert, AlertSeverity, MetricType
except ImportError:
    # Fallback for testing - create mock classes
    class HealthStatus:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"
        WARNING = "warning"
    
    class HealthCheckResult:
        def __init__(self, service_name, endpoint, status, response_time_ms, timestamp, error_message=None):
            self.service_name = service_name
            self.endpoint = endpoint
            self.status = status
            self.response_time_ms = response_time_ms
            self.timestamp = timestamp
            self.error_message = error_message
    
    class HealthCheckFramework:
        async def run_all_checks(self):
            return []
    
    class AlertSeverity:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class Alert:
        def __init__(self, id, service_name, severity, message, timestamp, metric_type=None, metric_value=None):
            self.id = id
            self.service_name = service_name
            self.severity = severity
            self.message = message
            self.timestamp = timestamp
            self.metric_type = metric_type
            self.metric_value = metric_value
    
    class PerformanceMonitor:
        def get_current_metrics(self):
            return {}
    
    class MetricType:
        COUNTER = "counter"
        GAUGE = "gauge"

logger = logging.getLogger(__name__)


class DashboardTheme(Enum):
    """Dashboard theme options."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


@dataclass
class DashboardConfig:
    """Configuration for monitoring dashboard."""
    refresh_interval_seconds: int = 30
    max_data_points: int = 1000
    theme: DashboardTheme = DashboardTheme.DARK
    enable_real_time: bool = True
    alert_channels: List[AlertChannel] = None
    database_path: str = "monitoring.db"
    
    def __post_init__(self):
        if self.alert_channels is None:
            self.alert_channels = [AlertChannel.EMAIL]


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    id: str
    title: str
    widget_type: str  # "chart", "gauge", "table", "alert_list"
    data_source: str
    config: Dict[str, Any] = None
    position: Dict[str, int] = None  # {"x": 0, "y": 0, "width": 4, "height": 3}
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.position is None:
            self.position = {"x": 0, "y": 0, "width": 4, "height": 3}


@dataclass
class AlertNotification:
    """Alert notification configuration."""
    id: str
    alert_id: str
    channel: AlertChannel
    recipient: str
    sent_at: datetime
    status: str = "pending"  # pending, sent, failed
    retry_count: int = 0
    error_message: Optional[str] = None


class MonitoringDataPersistence:
    """Data persistence layer for monitoring data."""
    
    def __init__(self, database_path: str = "monitoring.db"):
        self.database_path = database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the monitoring database."""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    service_name TEXT,
                    endpoint TEXT,
                    status TEXT,
                    response_time_ms REAL,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    service_name TEXT,
                    metric_type TEXT,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    alert_id TEXT UNIQUE,
                    service_name TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alert_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT,
                    channel TEXT,
                    recipient TEXT,
                    sent_at DATETIME,
                    status TEXT,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
    
    def store_health_check(self, result: HealthCheckResult):
        """Store health check result."""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT INTO health_checks 
                (timestamp, service_name, endpoint, status, response_time_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                result.timestamp,
                result.service_name,
                result.endpoint,
                result.status.value,
                result.response_time_ms,
                result.error_message
            ))
    
    def store_performance_metric(self, service_name: str, metric_type: str, 
                               metric_name: str, value: float, unit: str = ""):
        """Store performance metric."""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT INTO performance_metrics 
                (timestamp, service_name, metric_type, metric_name, value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                service_name,
                metric_type,
                metric_name,
                value,
                unit
            ))
    
    def store_alert(self, alert: Alert):
        """Store alert."""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO alerts 
                (timestamp, alert_id, service_name, severity, message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert.timestamp,
                alert.id,
                alert.service_name,
                alert.severity.value,
                alert.message
            ))
    
    def get_recent_health_checks(self, service_name: str = None, 
                               hours: int = 24) -> List[Dict]:
        """Get recent health check results."""
        query = """
            SELECT * FROM health_checks 
            WHERE timestamp > datetime('now', '-{} hours')
        """.format(hours)
        
        params = []
        if service_name:
            query += " AND service_name = ?"
            params.append(service_name)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_performance_metrics(self, service_name: str = None, 
                              metric_type: str = None, hours: int = 24) -> List[Dict]:
        """Get performance metrics."""
        query = """
            SELECT * FROM performance_metrics 
            WHERE timestamp > datetime('now', '-{} hours')
        """.format(hours)
        
        params = []
        if service_name:
            query += " AND service_name = ?"
            params.append(service_name)
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_active_alerts(self, service_name: str = None) -> List[Dict]:
        """Get active alerts."""
        query = "SELECT * FROM alerts WHERE resolved = FALSE"
        
        params = []
        if service_name:
            query += " AND service_name = ?"
            params.append(service_name)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]


class AlertingSystem:
    """Alerting system for threshold breaches."""
    
    def __init__(self, config: DashboardConfig, persistence: MonitoringDataPersistence):
        self.config = config
        self.persistence = persistence
        self.notification_handlers: Dict[AlertChannel, Callable] = {}
        self.alert_rules: List[Dict] = []
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default notification handlers."""
        self.notification_handlers[AlertChannel.EMAIL] = self._send_email_notification
        self.notification_handlers[AlertChannel.SLACK] = self._send_slack_notification
        self.notification_handlers[AlertChannel.WEBHOOK] = self._send_webhook_notification
    
    def add_alert_rule(self, service_name: str, metric_type: str, 
                      threshold: float, severity: AlertSeverity, 
                      comparison: str = "greater_than"):
        """Add alert rule."""
        rule = {
            "service_name": service_name,
            "metric_type": metric_type,
            "threshold": threshold,
            "severity": severity,
            "comparison": comparison,
            "enabled": True
        }
        self.alert_rules.append(rule)
    
    def check_thresholds(self, service_name: str, metric_type: str, 
                        metric_name: str, value: float):
        """Check if value breaches any thresholds."""
        for rule in self.alert_rules:
            if (rule["service_name"] == service_name and 
                rule["metric_type"] == metric_type and 
                rule["enabled"]):
                
                breach = False
                if rule["comparison"] == "greater_than" and value > rule["threshold"]:
                    breach = True
                elif rule["comparison"] == "less_than" and value < rule["threshold"]:
                    breach = True
                
                if breach:
                    alert = Alert(
                        id=f"{service_name}_{metric_type}_{metric_name}_{int(time.time())}",
                        service_name=service_name,
                        severity=rule["severity"],
                        message=f"{metric_name} threshold breach: {value} {rule['comparison']} {rule['threshold']}",
                        timestamp=datetime.now(),
                        metric_type=metric_type,
                        metric_value=value
                    )
                    self.send_alert(alert)
    
    def send_alert(self, alert: Alert):
        """Send alert through configured channels."""
        self.persistence.store_alert(alert)
        
        for channel in self.config.alert_channels:
            try:
                handler = self.notification_handlers.get(channel)
                if handler:
                    handler(alert)
                    self._record_notification(alert.id, channel, "sent")
                else:
                    logger.warning(f"No handler configured for channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
                self._record_notification(alert.id, channel, "failed", str(e))
    
    def _record_notification(self, alert_id: str, channel: AlertChannel, 
                           status: str, error_message: str = None):
        """Record notification attempt."""
        with sqlite3.connect(self.persistence.database_path) as conn:
            conn.execute("""
                INSERT INTO alert_notifications 
                (alert_id, channel, recipient, sent_at, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert_id,
                channel.value,
                "default",  # Could be configured per channel
                datetime.now(),
                status,
                error_message
            ))
    
    def _send_email_notification(self, alert: Alert):
        """Send email notification (placeholder)."""
        logger.info(f"EMAIL ALERT: {alert.severity.value} - {alert.message}")
        # In real implementation, integrate with email service
    
    def _send_slack_notification(self, alert: Alert):
        """Send Slack notification (placeholder)."""
        logger.info(f"SLACK ALERT: {alert.severity.value} - {alert.message}")
        # In real implementation, integrate with Slack API
    
    def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification (placeholder)."""
        logger.info(f"WEBHOOK ALERT: {alert.severity.value} - {alert.message}")
        # In real implementation, send HTTP POST to webhook URL


class RealTimeDashboard:
    """Real-time monitoring dashboard."""
    
    def __init__(self, config: DashboardConfig, 
                 health_check_framework: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 persistence: MonitoringDataPersistence,
                 alerting_system: AlertingSystem):
        self.config = config
        self.health_check_framework = health_check_framework
        self.performance_monitor = performance_monitor
        self.persistence = persistence
        self.alerting_system = alerting_system
        self.widgets: List[DashboardWidget] = []
        self.is_running = False
        self._data_cache: Dict[str, Any] = {}
        self._setup_default_widgets()
    
    def _setup_default_widgets(self):
        """Setup default dashboard widgets."""
        self.widgets = [
            DashboardWidget(
                id="health_overview",
                title="Service Health Overview",
                widget_type="gauge",
                data_source="health_checks",
                position={"x": 0, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id="response_time_chart",
                title="Response Time Trends",
                widget_type="chart",
                data_source="performance_metrics",
                config={"metric_type": "response_time"},
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id="error_rate_chart",
                title="Error Rate",
                widget_type="chart",
                data_source="performance_metrics",
                config={"metric_type": "error_rate"},
                position={"x": 0, "y": 4, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id="active_alerts",
                title="Active Alerts",
                widget_type="alert_list",
                data_source="alerts",
                position={"x": 6, "y": 4, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id="deployment_status",
                title="Recent Deployments",
                widget_type="table",
                data_source="deployments",
                position={"x": 0, "y": 8, "width": 12, "height": 4}
            )
        ]
    
    def start(self):
        """Start the real-time dashboard."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting real-time monitoring dashboard")
        
        # Start background data collection
        if self.config.enable_real_time:
            threading.Thread(target=self._data_collection_loop, daemon=True).start()
    
    def stop(self):
        """Stop the real-time dashboard."""
        self.is_running = False
        logger.info("Stopping real-time monitoring dashboard")
    
    def _data_collection_loop(self):
        """Background data collection loop."""
        while self.is_running:
            try:
                self._collect_health_data()
                self._collect_performance_data()
                self._update_cache()
                time.sleep(self.config.refresh_interval_seconds)
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                time.sleep(5)  # Brief pause before retry
    
    def _collect_health_data(self):
        """Collect health check data."""
        try:
            # Run health checks
            results = asyncio.run(self.health_check_framework.run_all_checks())
            
            for result in results:
                self.persistence.store_health_check(result)
                
                # Check for health-based alerts
                if result.status != HealthStatus.HEALTHY:
                    alert = Alert(
                        id=f"health_{result.service_name}_{int(time.time())}",
                        service_name=result.service_name,
                        severity=AlertSeverity.HIGH if result.status == HealthStatus.UNHEALTHY else AlertSeverity.MEDIUM,
                        message=f"Health check failed for {result.service_name}: {result.error_message}",
                        timestamp=datetime.now(),
                        metric_type="health_check",
                        metric_value=0 if result.status == HealthStatus.UNHEALTHY else 0.5
                    )
                    self.alerting_system.send_alert(alert)
        except Exception as e:
            logger.error(f"Error collecting health data: {e}")
    
    def _collect_performance_data(self):
        """Collect performance metrics."""
        try:
            metrics = self.performance_monitor.get_current_metrics()
            
            for service_name, service_metrics in metrics.items():
                for metric_name, metric_data in service_metrics.items():
                    value = metric_data.get("value", 0)
                    unit = metric_data.get("unit", "")
                    metric_type = metric_data.get("type", "unknown")
                    
                    # Store metric
                    self.persistence.store_performance_metric(
                        service_name, metric_type, metric_name, value, unit
                    )
                    
                    # Check thresholds
                    self.alerting_system.check_thresholds(
                        service_name, metric_type, metric_name, value
                    )
        except Exception as e:
            logger.error(f"Error collecting performance data: {e}")
    
    def _update_cache(self):
        """Update dashboard data cache."""
        try:
            self._data_cache = {
                "health_checks": self.persistence.get_recent_health_checks(hours=1),
                "performance_metrics": self.persistence.get_performance_metrics(hours=1),
                "active_alerts": self.persistence.get_active_alerts(),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating cache: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return self._data_cache.copy()
    
    def get_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for specific widget."""
        widget = next((w for w in self.widgets if w.id == widget_id), None)
        if not widget:
            return {}
        
        data_source = widget.data_source
        if data_source in self._data_cache:
            return {
                "widget": asdict(widget),
                "data": self._data_cache[data_source]
            }
        return {"widget": asdict(widget), "data": []}
    
    def add_widget(self, widget: DashboardWidget):
        """Add widget to dashboard."""
        self.widgets.append(widget)
    
    def remove_widget(self, widget_id: str):
        """Remove widget from dashboard."""
        self.widgets = [w for w in self.widgets if w.id != widget_id]
    
    def export_dashboard_config(self) -> Dict[str, Any]:
        """Export dashboard configuration."""
        return {
            "config": asdict(self.config),
            "widgets": [asdict(w) for w in self.widgets]
        }
    
    def import_dashboard_config(self, config_data: Dict[str, Any]):
        """Import dashboard configuration."""
        if "widgets" in config_data:
            self.widgets = [
                DashboardWidget(**widget_data) 
                for widget_data in config_data["widgets"]
            ]


class MonitoringDashboardSystem:
    """Complete monitoring dashboard system."""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        
        # Initialize components
        self.persistence = MonitoringDataPersistence(self.config.database_path)
        self.health_check_framework = HealthCheckFramework()
        self.performance_monitor = PerformanceMonitor()
        self.alerting_system = AlertingSystem(self.config, self.persistence)
        self.dashboard = RealTimeDashboard(
            self.config,
            self.health_check_framework,
            self.performance_monitor,
            self.persistence,
            self.alerting_system
        )
        
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules."""
        # Response time alerts
        self.alerting_system.add_alert_rule(
            service_name="*",
            metric_type="response_time",
            threshold=2000,  # 2 seconds
            severity=AlertSeverity.MEDIUM,
            comparison="greater_than"
        )
        
        # Error rate alerts
        self.alerting_system.add_alert_rule(
            service_name="*",
            metric_type="error_rate",
            threshold=0.05,  # 5%
            severity=AlertSeverity.HIGH,
            comparison="greater_than"
        )
        
        # CPU usage alerts
        self.alerting_system.add_alert_rule(
            service_name="*",
            metric_type="cpu_usage",
            threshold=80,  # 80%
            severity=AlertSeverity.MEDIUM,
            comparison="greater_than"
        )
        
        # Memory usage alerts
        self.alerting_system.add_alert_rule(
            service_name="*",
            metric_type="memory_usage",
            threshold=85,  # 85%
            severity=AlertSeverity.HIGH,
            comparison="greater_than"
        )
    
    def start(self):
        """Start the monitoring system."""
        logger.info("Starting monitoring dashboard system")
        self.dashboard.start()
    
    def stop(self):
        """Stop the monitoring system."""
        logger.info("Stopping monitoring dashboard system")
        self.dashboard.stop()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        dashboard_data = self.dashboard.get_dashboard_data()
        active_alerts = self.persistence.get_active_alerts()
        
        # Calculate overall health score
        recent_health_checks = dashboard_data.get("health_checks", [])
        if recent_health_checks:
            healthy_count = sum(1 for check in recent_health_checks if check["status"] == "healthy")
            health_score = (healthy_count / len(recent_health_checks)) * 100
        else:
            health_score = 100
        
        return {
            "overall_health_score": health_score,
            "active_alerts_count": len(active_alerts),
            "critical_alerts_count": len([a for a in active_alerts if a["severity"] == "critical"]),
            "services_monitored": len(set(check["service_name"] for check in recent_health_checks)),
            "last_updated": dashboard_data.get("last_updated"),
            "dashboard_running": self.dashboard.is_running
        }


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and start monitoring system
    config = DashboardConfig(
        refresh_interval_seconds=10,
        theme=DashboardTheme.DARK,
        alert_channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
    )
    
    monitoring_system = MonitoringDashboardSystem(config)
    
    try:
        monitoring_system.start()
        
        # Simulate running for a while
        time.sleep(60)
        
        # Get system status
        status = monitoring_system.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
    finally:
        monitoring_system.stop()
 