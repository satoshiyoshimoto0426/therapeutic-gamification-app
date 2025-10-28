"""
Unit tests for performance monitoring system.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from performance_monitor import (
    PerformanceMonitor,
    PerformanceMetric,
    ErrorMetric,
    MetricType,
    AlertSeverity,
    AlertRule,
    Alert,
    MetricValue,
    ResourceUtilization,
    BaseMetricCollector,
    SystemResourceCollector,
    HTTPMetricCollector
)


class TestMetricValue:
    """Test MetricValue dataclass."""
    
    def test_metric_value_creation(self):
        """Test creating a metric value."""
        now = datetime.now()
        value = MetricValue(
            value=42.5,
            timestamp=now,
            labels={"service": "test"}
        )
        
        assert value.value == 42.5
        assert value.timestamp == now
        assert value.labels == {"service": "test"}


class TestPerformanceMetric:
    """Test PerformanceMetric class."""
    
    def test_metric_creation(self):
        """Test creating a performance metric."""
        metric = PerformanceMetric(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            description="Test metric",
            unit="bytes"
        )
        
        assert metric.name == "test_metric"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.description == "Test metric"
        assert metric.unit == "bytes"
        assert len(metric.values) == 0
        
    def test_add_value(self):
        """Test adding values to metric."""
        metric = PerformanceMetric("test", MetricType.COUNTER)
        
        metric.add_value(10.0, {"label": "value"})
        metric.add_value(20.0)
        
        assert len(metric.values) == 2
        assert metric.values[0].value == 10.0
        assert metric.values[0].labels == {"label": "value"}
        assert metric.values[1].value == 20.0
        assert metric.values[1].labels == {}
        
    def test_get_latest_value(self):
        """Test getting latest metric value."""
        metric = PerformanceMetric("test", MetricType.GAUGE)
        
        # No values yet
        assert metric.get_latest_value() is None
        
        # Add values
        metric.add_value(10.0)
        metric.add_value(20.0)
        
        latest = metric.get_latest_value()
        assert latest is not None
        assert latest.value == 20.0
        
    def test_get_average(self):
        """Test getting average value."""
        metric = PerformanceMetric("test", MetricType.GAUGE)
        
        # No values
        assert metric.get_average() is None
        
        # Add values (all recent)
        metric.add_value(10.0)
        metric.add_value(20.0)
        metric.add_value(30.0)
        
        average = metric.get_average(duration_minutes=5)
        assert average == 20.0  # (10 + 20 + 30) / 3


class TestErrorMetric:
    """Test ErrorMetric class."""
    
    def test_error_metric_creation(self):
        """Test creating an error metric."""
        error_metric = ErrorMetric("test_error")
        
        assert error_metric.error_type == "test_error"
        assert error_metric.count == 0
        assert error_metric.last_occurrence is None
        assert error_metric.error_rate == 0.0
        assert len(error_metric.recent_errors) == 0
        
    def test_record_error(self):
        """Test recording errors."""
        error_metric = ErrorMetric("test_error")
        
        error_metric.record_error()
        
        assert error_metric.count == 1
        assert error_metric.last_occurrence is not None
        assert len(error_metric.recent_errors) == 1
        assert error_metric.error_rate == 1.0  # 1 error in last minute
        
    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        error_metric = ErrorMetric("test_error")
        
        # Record multiple errors
        for _ in range(5):
            error_metric.record_error()
            
        assert error_metric.count == 5
        assert error_metric.error_rate == 5.0  # 5 errors in last minute


class TestResourceUtilization:
    """Test ResourceUtilization dataclass."""
    
    def test_resource_utilization_creation(self):
        """Test creating resource utilization."""
        resource_util = ResourceUtilization(
            cpu_percent=50.0,
            memory_percent=75.0,
            disk_usage_percent=80.0,
            network_io_bytes={"sent": 1000, "recv": 2000}
        )
        
        assert resource_util.cpu_percent == 50.0
        assert resource_util.memory_percent == 75.0
        assert resource_util.disk_usage_percent == 80.0
        assert resource_util.network_io_bytes == {"sent": 1000, "recv": 2000}
        assert isinstance(resource_util.timestamp, datetime)


class TestAlertRule:
    """Test AlertRule dataclass."""
    
    def test_alert_rule_creation(self):
        """Test creating an alert rule."""
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_percent",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            duration_minutes=2
        )
        
        assert rule.name == "high_cpu"
        assert rule.metric_name == "cpu_percent"
        assert rule.condition == "greater_than"
        assert rule.threshold == 80.0
        assert rule.severity == AlertSeverity.HIGH
        assert rule.duration_minutes == 2
        assert rule.enabled is True


class TestAlert:
    """Test Alert dataclass."""
    
    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            rule_name="high_cpu",
            metric_name="cpu_percent",
            current_value=85.0,
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            message="CPU usage is high"
        )
        
        assert alert.rule_name == "high_cpu"
        assert alert.metric_name == "cpu_percent"
        assert alert.current_value == 85.0
        assert alert.threshold == 80.0
        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == "CPU usage is high"
        assert alert.resolved is False
        assert alert.resolved_at is None


class MockMetricCollector(BaseMetricCollector):
    """Mock metric collector for testing."""
    
    def __init__(self, name: str, metrics: dict):
        super().__init__(name)
        self.metrics = metrics
        
    async def collect(self) -> dict:
        return self.metrics


class TestHTTPMetricCollector:
    """Test HTTP metric collector."""
    
    def test_http_collector_initialization(self):
        """Test HTTP collector initialization."""
        collector = HTTPMetricCollector()
        
        assert collector.name == "http_metrics"
        assert collector.request_count == 0
        assert len(collector.response_times) == 0
        assert len(collector.status_codes) == 0
        
    def test_record_request(self):
        """Test recording HTTP requests."""
        collector = HTTPMetricCollector()
        
        collector.record_request(150.0, 200)
        collector.record_request(200.0, 404)
        collector.record_request(100.0, 200)
        
        assert collector.request_count == 3
        assert len(collector.response_times) == 3
        assert collector.status_codes[200] == 2
        assert collector.status_codes[404] == 1
        
    @pytest.mark.asyncio
    async def test_collect_metrics(self):
        """Test collecting HTTP metrics."""
        collector = HTTPMetricCollector()
        
        # Record some requests
        collector.record_request(100.0, 200)
        collector.record_request(200.0, 200)
        collector.record_request(300.0, 500)
        
        metrics = await collector.collect()
        
        assert metrics["http_requests_total"] == 3.0
        assert metrics["http_request_duration_avg"] == 200.0  # (100+200+300)/3
        assert metrics["http_responses_200"] == 2.0
        assert metrics["http_responses_500"] == 1.0
        assert "http_request_duration_p95" in metrics
        assert "http_request_duration_p99" in metrics


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor()
        
        assert len(monitor.metrics) == 0
        assert len(monitor.error_metrics) == 0
        assert len(monitor.collectors) == 2  # Default collectors
        assert len(monitor.alert_rules) == 0
        assert len(monitor.active_alerts) == 0
        assert not monitor.is_running
        
    def test_create_metric(self):
        """Test creating metrics."""
        monitor = PerformanceMonitor()
        
        monitor.create_metric("test_metric", MetricType.GAUGE, "Test metric", "bytes")
        
        assert "test_metric" in monitor.metrics
        metric = monitor.metrics["test_metric"]
        assert metric.name == "test_metric"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.description == "Test metric"
        assert metric.unit == "bytes"
        
    def test_record_metric(self):
        """Test recording metric values."""
        monitor = PerformanceMonitor()
        
        # Record to non-existent metric (should auto-create)
        monitor.record_metric("cpu_usage", 75.0, {"host": "server1"})
        
        assert "cpu_usage" in monitor.metrics
        metric = monitor.metrics["cpu_usage"]
        assert metric.metric_type == MetricType.GAUGE
        
        latest = metric.get_latest_value()
        assert latest.value == 75.0
        assert latest.labels == {"host": "server1"}
        
    def test_increment_counter(self):
        """Test incrementing counter metrics."""
        monitor = PerformanceMonitor()
        
        # Increment non-existent counter (should auto-create)
        monitor.increment_counter("requests_total")
        monitor.increment_counter("requests_total")
        monitor.increment_counter("requests_total")
        
        assert "requests_total" in monitor.metrics
        metric = monitor.metrics["requests_total"]
        assert metric.metric_type == MetricType.COUNTER
        
        latest = metric.get_latest_value()
        assert latest.value == 3.0
        
    def test_record_error(self):
        """Test recording errors."""
        monitor = PerformanceMonitor()
        
        monitor.record_error("connection_error", "Failed to connect to database")
        monitor.record_error("connection_error", "Another connection error")
        monitor.record_error("timeout_error", "Request timeout")
        
        assert "connection_error" in monitor.error_metrics
        assert "timeout_error" in monitor.error_metrics
        
        connection_errors = monitor.error_metrics["connection_error"]
        assert connection_errors.count == 2
        assert connection_errors.error_rate == 2.0
        
        timeout_errors = monitor.error_metrics["timeout_error"]
        assert timeout_errors.count == 1
        assert timeout_errors.error_rate == 1.0
        
    def test_get_metric(self):
        """Test getting metrics."""
        monitor = PerformanceMonitor()
        
        monitor.create_metric("test_metric", MetricType.GAUGE)
        
        metric = monitor.get_metric("test_metric")
        assert metric is not None
        assert metric.name == "test_metric"
        
        non_existent = monitor.get_metric("non_existent")
        assert non_existent is None
        
    def test_get_error_metric(self):
        """Test getting error metrics."""
        monitor = PerformanceMonitor()
        
        monitor.record_error("test_error")
        
        error_metric = monitor.get_error_metric("test_error")
        assert error_metric is not None
        assert error_metric.error_type == "test_error"
        
        non_existent = monitor.get_error_metric("non_existent")
        assert non_existent is None
        
    def test_add_collector(self):
        """Test adding metric collectors."""
        monitor = PerformanceMonitor()
        initial_count = len(monitor.collectors)
        
        mock_collector = MockMetricCollector("test_collector", {"test_metric": 42.0})
        monitor.add_collector(mock_collector)
        
        assert len(monitor.collectors) == initial_count + 1
        assert mock_collector in monitor.collectors
        
    def test_add_alert_rule(self):
        """Test adding alert rules."""
        monitor = PerformanceMonitor()
        
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_percent",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )
        
        monitor.add_alert_rule(rule)
        
        assert "high_cpu" in monitor.alert_rules
        assert monitor.alert_rules["high_cpu"] == rule
        
    def test_remove_alert_rule(self):
        """Test removing alert rules."""
        monitor = PerformanceMonitor()
        
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_percent",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )
        
        monitor.add_alert_rule(rule)
        assert "high_cpu" in monitor.alert_rules
        
        monitor.remove_alert_rule("high_cpu")
        assert "high_cpu" not in monitor.alert_rules
        
    @pytest.mark.asyncio
    async def test_collect_all_metrics(self):
        """Test collecting metrics from all collectors."""
        monitor = PerformanceMonitor()
        
        # Clear default collectors for cleaner test
        monitor.collectors = []
        
        # Add mock collector
        mock_collector = MockMetricCollector("test_collector", {
            "test_metric_1": 10.0,
            "test_metric_2": 20.0
        })
        monitor.add_collector(mock_collector)
        
        await monitor.collect_all_metrics()
        
        assert "test_metric_1" in monitor.metrics
        assert "test_metric_2" in monitor.metrics
        
        metric1 = monitor.get_metric("test_metric_1")
        metric2 = monitor.get_metric("test_metric_2")
        
        assert metric1.get_latest_value().value == 10.0
        assert metric2.get_latest_value().value == 20.0
        
    def test_get_active_alerts(self):
        """Test getting active alerts."""
        monitor = PerformanceMonitor()
        
        # Create some alerts
        alert1 = Alert(
            rule_name="rule1",
            metric_name="metric1",
            current_value=90.0,
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            message="High alert"
        )
        
        alert2 = Alert(
            rule_name="rule2",
            metric_name="metric2",
            current_value=95.0,
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            message="Critical alert"
        )
        
        alert3 = Alert(
            rule_name="rule3",
            metric_name="metric3",
            current_value=60.0,
            threshold=50.0,
            severity=AlertSeverity.LOW,
            message="Low alert",
            resolved=True
        )
        
        monitor.active_alerts = [alert1, alert2, alert3]
        
        # Get all active alerts (should exclude resolved)
        active_alerts = monitor.get_active_alerts()
        assert len(active_alerts) == 2
        assert alert1 in active_alerts
        assert alert2 in active_alerts
        assert alert3 not in active_alerts
        
        # Get alerts by severity
        high_alerts = monitor.get_active_alerts(AlertSeverity.HIGH)
        assert len(high_alerts) == 1
        assert alert1 in high_alerts
        
        critical_alerts = monitor.get_active_alerts(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert alert2 in critical_alerts
        
    def test_resolve_alert(self):
        """Test resolving alerts."""
        monitor = PerformanceMonitor()
        
        alert = Alert(
            rule_name="test_rule",
            metric_name="test_metric",
            current_value=90.0,
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            message="Test alert"
        )
        
        monitor.active_alerts = [alert]
        
        # Resolve the alert
        result = monitor.resolve_alert("test_rule")
        assert result is True
        assert alert.resolved is True
        assert alert.resolved_at is not None
        
        # Try to resolve non-existent alert
        result = monitor.resolve_alert("non_existent")
        assert result is False
        
    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        monitor = PerformanceMonitor()
        
        # Add some metrics and errors
        monitor.record_metric("cpu_usage", 75.0)
        monitor.record_error("test_error")
        
        summary = monitor.get_metrics_summary()
        
        assert "metrics_count" in summary
        assert "error_types_count" in summary
        assert "active_alerts_count" in summary
        assert "collectors_count" in summary
        assert "metrics" in summary
        assert "errors" in summary
        
        assert summary["metrics_count"] == 1
        assert summary["error_types_count"] == 1
        assert "cpu_usage" in summary["metrics"]
        assert "test_error" in summary["errors"]


if __name__ == "__main__":
    pytest.main([__file__])