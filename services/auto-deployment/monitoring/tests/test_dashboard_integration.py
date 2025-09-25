"""
Integration tests for monitoring dashboard and alerting system.

Tests the complete monitoring dashboard system including real-time monitoring,
alerting, and data persistence.
"""

import asyncio
import json
import os
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# Add the monitoring directory to path for relative imports
monitoring_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, monitoring_dir)

from dashboard import (
    MonitoringDashboardSystem, DashboardConfig, DashboardTheme, AlertChannel,
    DashboardWidget, AlertingSystem, RealTimeDashboard, MonitoringDataPersistence
)
from health_check import HealthCheckResult, HealthStatus
from performance_monitor import Alert, AlertSeverity, MetricType


class TestMonitoringDashboardIntegration(unittest.TestCase):
    """Integration tests for monitoring dashboard system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.config = DashboardConfig(
            refresh_interval_seconds=1,  # Fast refresh for testing
            database_path=self.temp_db.name,
            theme=DashboardTheme.DARK,
            alert_channels=[AlertChannel.EMAIL]
        )
        
        self.monitoring_system = MonitoringDashboardSystem(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.monitoring_system.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_system_initialization(self):
        """Test monitoring system initialization."""
        # Verify components are initialized
        self.assertIsNotNone(self.monitoring_system.persistence)
        self.assertIsNotNone(self.monitoring_system.health_check_framework)
        self.assertIsNotNone(self.monitoring_system.performance_monitor)
        self.assertIsNotNone(self.monitoring_system.alerting_system)
        self.assertIsNotNone(self.monitoring_system.dashboard)
        
        # Verify database is initialized
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['health_checks', 'performance_metrics', 'alerts', 'alert_notifications']
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_health_check_data_flow(self):
        """Test health check data collection and storage."""
        # Create mock health check result
        health_result = HealthCheckResult(
            service_name="test-service",
            endpoint="/health",
            status=HealthStatus.HEALTHY,
            response_time_ms=150.0,
            timestamp=datetime.now(),
            error_message=None
        )
        
        # Store health check result
        self.monitoring_system.persistence.store_health_check(health_result)
        
        # Verify data is stored
        recent_checks = self.monitoring_system.persistence.get_recent_health_checks()
        self.assertEqual(len(recent_checks), 1)
        self.assertEqual(recent_checks[0]['service_name'], 'test-service')
        self.assertEqual(recent_checks[0]['status'], 'healthy')
    
    def test_performance_metrics_data_flow(self):
        """Test performance metrics collection and storage."""
        # Store performance metric
        self.monitoring_system.persistence.store_performance_metric(
            service_name="test-service",
            metric_type="response_time",
            metric_name="api_response_time",
            value=250.0,
            unit="ms"
        )
        
        # Verify data is stored
        metrics = self.monitoring_system.persistence.get_performance_metrics()
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]['service_name'], 'test-service')
        self.assertEqual(metrics[0]['metric_type'], 'response_time')
        self.assertEqual(metrics[0]['value'], 250.0)
    
    def test_alert_generation_and_storage(self):
        """Test alert generation and storage."""
        # Create alert
        alert = Alert(
            id="test-alert-1",
            service_name="test-service",
            severity=AlertSeverity.HIGH,
            message="Test alert message",
            timestamp=datetime.now(),
            metric_type="response_time",
            metric_value=3000.0
        )
        
        # Send alert through system
        self.monitoring_system.alerting_system.send_alert(alert)
        
        # Verify alert is stored
        active_alerts = self.monitoring_system.persistence.get_active_alerts()
        self.assertEqual(len(active_alerts), 1)
        self.assertEqual(active_alerts[0]['alert_id'], 'test-alert-1')
        self.assertEqual(active_alerts[0]['severity'], 'high')
    
    def test_threshold_breach_detection(self):
        """Test automatic threshold breach detection."""
        # Add alert rule
        self.monitoring_system.alerting_system.add_alert_rule(
            service_name="test-service",
            metric_type="response_time",
            threshold=1000.0,
            severity=AlertSeverity.MEDIUM,
            comparison="greater_than"
        )
        
        # Trigger threshold breach
        self.monitoring_system.alerting_system.check_thresholds(
            service_name="test-service",
            metric_type="response_time",
            metric_name="api_response_time",
            value=1500.0
        )
        
        # Verify alert was generated
        active_alerts = self.monitoring_system.persistence.get_active_alerts()
        self.assertGreater(len(active_alerts), 0)
        
        # Find the threshold breach alert
        threshold_alert = next(
            (alert for alert in active_alerts if "threshold breach" in alert['message']),
            None
        )
        self.assertIsNotNone(threshold_alert)
        self.assertEqual(threshold_alert['service_name'], 'test-service')
    
    def test_dashboard_widget_configuration(self):
        """Test dashboard widget configuration."""
        # Add custom widget
        custom_widget = DashboardWidget(
            id="custom-chart",
            title="Custom Metrics Chart",
            widget_type="chart",
            data_source="performance_metrics",
            config={"metric_type": "custom_metric"},
            position={"x": 0, "y": 0, "width": 6, "height": 4}
        )
        
        self.monitoring_system.dashboard.add_widget(custom_widget)
        
        # Verify widget is added
        widget_data = self.monitoring_system.dashboard.get_widget_data("custom-chart")
        self.assertIsNotNone(widget_data)
        self.assertEqual(widget_data['widget']['title'], 'Custom Metrics Chart')
    
    def test_dashboard_data_cache(self):
        """Test dashboard data caching."""
        # Add some test data
        self.monitoring_system.persistence.store_performance_metric(
            "test-service", "response_time", "api_time", 200.0, "ms"
        )
        
        health_result = HealthCheckResult(
            service_name="test-service",
            endpoint="/health",
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0,
            timestamp=datetime.now()
        )
        self.monitoring_system.persistence.store_health_check(health_result)
        
        # Update cache
        self.monitoring_system.dashboard._update_cache()
        
        # Verify cache contains data
        dashboard_data = self.monitoring_system.dashboard.get_dashboard_data()
        self.assertIn('health_checks', dashboard_data)
        self.assertIn('performance_metrics', dashboard_data)
        self.assertIn('last_updated', dashboard_data)
        
        self.assertGreater(len(dashboard_data['health_checks']), 0)
        self.assertGreater(len(dashboard_data['performance_metrics']), 0)
    
    def test_system_status_calculation(self):
        """Test overall system status calculation."""
        # Add healthy service data
        for i in range(8):
            health_result = HealthCheckResult(
                service_name=f"service-{i}",
                endpoint="/health",
                status=HealthStatus.HEALTHY,
                response_time_ms=100.0,
                timestamp=datetime.now()
            )
            self.monitoring_system.persistence.store_health_check(health_result)
        
        # Add unhealthy service data
        for i in range(2):
            health_result = HealthCheckResult(
                service_name=f"unhealthy-service-{i}",
                endpoint="/health",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=5000.0,
                timestamp=datetime.now(),
                error_message="Service unavailable"
            )
            self.monitoring_system.persistence.store_health_check(health_result)
        
        # Update cache
        self.monitoring_system.dashboard._update_cache()
        
        # Get system status
        status = self.monitoring_system.get_system_status()
        
        # Verify status calculation
        self.assertIn('overall_health_score', status)
        self.assertIn('services_monitored', status)
        self.assertIn('active_alerts_count', status)
        
        # Health score should be 80% (8 healthy out of 10 total)
        self.assertEqual(status['overall_health_score'], 80.0)
        self.assertEqual(status['services_monitored'], 10)
    
    @patch('services.auto_deployment.monitoring.dashboard.logger')
    def test_error_handling_in_data_collection(self, mock_logger):
        """Test error handling during data collection."""
        # Mock health check framework to raise exception
        self.monitoring_system.dashboard.health_check_framework.run_all_checks = Mock(
            side_effect=Exception("Health check failed")
        )
        
        # Try to collect health data
        self.monitoring_system.dashboard._collect_health_data()
        
        # Verify error was logged
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("Error collecting health data", error_call)
    
    def test_dashboard_config_export_import(self):
        """Test dashboard configuration export and import."""
        # Add custom widget
        custom_widget = DashboardWidget(
            id="test-widget",
            title="Test Widget",
            widget_type="gauge",
            data_source="test_data"
        )
        self.monitoring_system.dashboard.add_widget(custom_widget)
        
        # Export configuration
        config_data = self.monitoring_system.dashboard.export_dashboard_config()
        
        # Verify export structure
        self.assertIn('config', config_data)
        self.assertIn('widgets', config_data)
        self.assertGreater(len(config_data['widgets']), 0)
        
        # Clear widgets and import
        self.monitoring_system.dashboard.widgets = []
        self.monitoring_system.dashboard.import_dashboard_config(config_data)
        
        # Verify import worked
        imported_widget = next(
            (w for w in self.monitoring_system.dashboard.widgets if w.id == "test-widget"),
            None
        )
        self.assertIsNotNone(imported_widget)
        self.assertEqual(imported_widget.title, "Test Widget")
    
    def test_alert_notification_recording(self):
        """Test alert notification recording."""
        # Create alert
        alert = Alert(
            id="notification-test-alert",
            service_name="test-service",
            severity=AlertSeverity.MEDIUM,
            message="Test notification alert",
            timestamp=datetime.now(),
            metric_type="test_metric",
            metric_value=100.0
        )
        
        # Send alert
        self.monitoring_system.alerting_system.send_alert(alert)
        
        # Verify notification was recorded
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute("""
                SELECT * FROM alert_notifications 
                WHERE alert_id = ?
            """, (alert.id,))
            notifications = cursor.fetchall()
        
        self.assertGreater(len(notifications), 0)
        # Should have one notification per configured channel
        self.assertEqual(len(notifications), len(self.config.alert_channels))
    
    def test_real_time_monitoring_start_stop(self):
        """Test real-time monitoring start and stop."""
        # Initially not running
        self.assertFalse(self.monitoring_system.dashboard.is_running)
        
        # Start monitoring
        self.monitoring_system.start()
        self.assertTrue(self.monitoring_system.dashboard.is_running)
        
        # Stop monitoring
        self.monitoring_system.stop()
        self.assertFalse(self.monitoring_system.dashboard.is_running)
    
    def test_multiple_service_monitoring(self):
        """Test monitoring multiple services simultaneously."""
        services = ["auth-service", "core-game", "task-mgmt", "ai-story"]
        
        # Add health checks for multiple services
        for service in services:
            health_result = HealthCheckResult(
                service_name=service,
                endpoint="/health",
                status=HealthStatus.HEALTHY,
                response_time_ms=150.0,
                timestamp=datetime.now()
            )
            self.monitoring_system.persistence.store_health_check(health_result)
            
            # Add performance metrics
            self.monitoring_system.persistence.store_performance_metric(
                service_name=service,
                metric_type="response_time",
                metric_name="api_response_time",
                value=200.0,
                unit="ms"
            )
        
        # Update cache
        self.monitoring_system.dashboard._update_cache()
        
        # Get system status
        status = self.monitoring_system.get_system_status()
        
        # Verify all services are monitored
        self.assertEqual(status['services_monitored'], len(services))
        self.assertEqual(status['overall_health_score'], 100.0)


class TestDashboardPerformance(unittest.TestCase):
    """Performance tests for dashboard system."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.config = DashboardConfig(
            database_path=self.temp_db.name,
            max_data_points=10000
        )
        
        self.monitoring_system = MonitoringDashboardSystem(self.config)
    
    def tearDown(self):
        """Clean up performance test environment."""
        self.monitoring_system.stop()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        # Insert large number of health checks
        start_time = time.time()
        
        for i in range(1000):
            health_result = HealthCheckResult(
                service_name=f"service-{i % 10}",
                endpoint="/health",
                status=HealthStatus.HEALTHY if i % 10 != 0 else HealthStatus.UNHEALTHY,
                response_time_ms=100.0 + (i % 100),
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            self.monitoring_system.persistence.store_health_check(health_result)
        
        insert_time = time.time() - start_time
        
        # Query recent data
        start_time = time.time()
        recent_checks = self.monitoring_system.persistence.get_recent_health_checks(hours=24)
        query_time = time.time() - start_time
        
        # Verify performance is acceptable
        self.assertLess(insert_time, 10.0)  # Should insert 1000 records in under 10 seconds
        self.assertLess(query_time, 1.0)    # Should query in under 1 second
        self.assertGreater(len(recent_checks), 0)
    
    def test_concurrent_data_access(self):
        """Test concurrent data access performance."""
        import threading
        
        results = []
        errors = []
        
        def worker():
            try:
                # Simulate concurrent health check storage
                for i in range(100):
                    health_result = HealthCheckResult(
                        service_name="concurrent-service",
                        endpoint="/health",
                        status=HealthStatus.HEALTHY,
                        response_time_ms=100.0,
                        timestamp=datetime.now()
                    )
                    self.monitoring_system.persistence.store_health_check(health_result)
                results.append("success")
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")
        self.assertEqual(len(results), 5)
        
        # Verify data integrity
        recent_checks = self.monitoring_system.persistence.get_recent_health_checks()
        self.assertEqual(len(recent_checks), 500)  # 5 threads * 100 records each


if __name__ == '__main__':
    unittest.main()