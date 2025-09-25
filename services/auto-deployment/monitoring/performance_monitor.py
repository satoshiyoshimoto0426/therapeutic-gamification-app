"""
Performance and error monitoring system for auto-deployment.

This module provides comprehensive performance metrics collection,
error rate monitoring, and resource utilization tracking.
"""

import asyncio
import time
import psutil
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Deque
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """A single metric value with timestamp."""
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance metric definition and current state."""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    values: Deque[MetricValue] = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_value(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a new metric value."""
        self.values.append(MetricValue(
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        ))
        
    def get_latest_value(self) -> Optional[MetricValue]:
        """Get the most recent metric value."""
        return self.values[-1] if self.values else None
        
    def get_average(self, duration_minutes: int = 5) -> Optional[float]:
        """Get average value over specified duration."""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_values = [
            mv.value for mv in self.values 
            if mv.timestamp >= cutoff_time
        ]
        return sum(recent_values) / len(recent_values) if recent_values else None


@dataclass
class ErrorMetric:
    """Error tracking metric."""
    error_type: str
    count: int = 0
    last_occurrence: Optional[datetime] = None
    error_rate: float = 0.0  # errors per minute
    recent_errors: Deque[datetime] = field(default_factory=lambda: deque(maxlen=100))
    
    def record_error(self) -> None:
        """Record a new error occurrence."""
        now = datetime.now()
        self.count += 1
        self.last_occurrence = now
        self.recent_errors.append(now)
        self._update_error_rate()
        
    def _update_error_rate(self) -> None:
        """Update the error rate based on recent errors."""
        if not self.recent_errors:
            self.error_rate = 0.0
            return
            
        # Calculate errors in the last minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_count = sum(1 for error_time in self.recent_errors if error_time >= one_minute_ago)
        self.error_rate = recent_count


@dataclass
class ResourceUtilization:
    """System resource utilization metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric_name: str
    condition: str  # e.g., "greater_than", "less_than", "equals"
    threshold: float
    severity: AlertSeverity
    duration_minutes: int = 1  # How long condition must persist
    enabled: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class Alert:
    """Generated alert."""
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class BaseMetricCollector(ABC):
    """Abstract base class for metric collectors."""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    async def collect(self) -> Dict[str, float]:
        """Collect metrics and return as dictionary."""
        pass


class SystemResourceCollector(BaseMetricCollector):
    """Collector for system resource metrics."""
    
    def __init__(self):
        super().__init__("system_resources")
        
    async def collect(self) -> Dict[str, float]:
        """Collect system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage (root partition)
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_bytes_sent": float(network.bytes_sent),
                "network_bytes_recv": float(network.bytes_recv)
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return {}


class HTTPMetricCollector(BaseMetricCollector):
    """Collector for HTTP-related metrics."""
    
    def __init__(self):
        super().__init__("http_metrics")
        self.request_count = 0
        self.response_times = deque(maxlen=1000)
        self.status_codes = defaultdict(int)
        
    def record_request(self, response_time_ms: float, status_code: int) -> None:
        """Record an HTTP request."""
        self.request_count += 1
        self.response_times.append(response_time_ms)
        self.status_codes[status_code] += 1
        
    async def collect(self) -> Dict[str, float]:
        """Collect HTTP metrics."""
        metrics = {
            "http_requests_total": float(self.request_count),
            "http_request_duration_avg": 0.0,
            "http_request_duration_p95": 0.0,
            "http_request_duration_p99": 0.0
        }
        
        if self.response_times:
            sorted_times = sorted(self.response_times)
            metrics["http_request_duration_avg"] = sum(sorted_times) / len(sorted_times)
            
            # Calculate percentiles
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            if p95_index < len(sorted_times):
                metrics["http_request_duration_p95"] = sorted_times[p95_index]
            if p99_index < len(sorted_times):
                metrics["http_request_duration_p99"] = sorted_times[p99_index]
        
        # Add status code metrics
        for status_code, count in self.status_codes.items():
            metrics[f"http_responses_{status_code}"] = float(count)
            
        return metrics


class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.error_metrics: Dict[str, ErrorMetric] = {}
        self.collectors: List[BaseMetricCollector] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Alert] = []
        self.is_running = False
        self.collection_interval = 30  # seconds
        
        # Add default collectors
        self.add_collector(SystemResourceCollector())
        self.add_collector(HTTPMetricCollector())
        
    def add_collector(self, collector: BaseMetricCollector) -> None:
        """Add a metric collector."""
        self.collectors.append(collector)
        logger.info(f"Added metric collector: {collector.name}")
        
    def create_metric(self, name: str, metric_type: MetricType, description: str = "", unit: str = "") -> None:
        """Create a new performance metric."""
        self.metrics[name] = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            description=description,
            unit=unit
        )
        logger.info(f"Created metric: {name} ({metric_type.value})")
        
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            # Auto-create gauge metric if it doesn't exist
            self.create_metric(name, MetricType.GAUGE)
            
        self.metrics[name].add_value(value, labels)
        
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        if name not in self.metrics:
            self.create_metric(name, MetricType.COUNTER)
            
        current_value = 0
        latest = self.metrics[name].get_latest_value()
        if latest:
            current_value = latest.value
            
        self.metrics[name].add_value(current_value + 1, labels)
        
    def record_error(self, error_type: str, error_message: str = "") -> None:
        """Record an error occurrence."""
        if error_type not in self.error_metrics:
            self.error_metrics[error_type] = ErrorMetric(error_type=error_type)
            
        self.error_metrics[error_type].record_error()
        logger.warning(f"Error recorded: {error_type} - {error_message}")
        
        # Check for error rate alerts
        self._check_error_alerts(error_type)
        
    def get_metric(self, name: str) -> Optional[PerformanceMetric]:
        """Get a performance metric by name."""
        return self.metrics.get(name)
        
    def get_error_metric(self, error_type: str) -> Optional[ErrorMetric]:
        """Get an error metric by type."""
        return self.error_metrics.get(error_type)
        
    def get_resource_utilization(self) -> Optional[ResourceUtilization]:
        """Get current resource utilization."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return ResourceUtilization(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_io_bytes={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            )
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {str(e)}")
            return None
            
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")
        
    def remove_alert_rule(self, rule_name: str) -> None:
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
            
    def _check_alerts(self) -> None:
        """Check all alert rules and generate alerts if needed."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
                
            metric = self.metrics.get(rule.metric_name)
            if not metric:
                continue
                
            latest_value = metric.get_latest_value()
            if not latest_value:
                continue
                
            should_alert = False
            current_value = latest_value.value
            
            if rule.condition == "greater_than" and current_value > rule.threshold:
                should_alert = True
            elif rule.condition == "less_than" and current_value < rule.threshold:
                should_alert = True
            elif rule.condition == "equals" and current_value == rule.threshold:
                should_alert = True
                
            if should_alert:
                self._generate_alert(rule, current_value)
                
    def _check_error_alerts(self, error_type: str) -> None:
        """Check for error rate alerts."""
        error_metric = self.error_metrics.get(error_type)
        if not error_metric:
            return
            
        # Check if error rate exceeds thresholds
        if error_metric.error_rate > 10:  # More than 10 errors per minute
            alert = Alert(
                rule_name=f"high_error_rate_{error_type}",
                metric_name=f"error_rate_{error_type}",
                current_value=error_metric.error_rate,
                threshold=10.0,
                severity=AlertSeverity.HIGH,
                message=f"High error rate for {error_type}: {error_metric.error_rate} errors/min"
            )
            self.active_alerts.append(alert)
            
    def _generate_alert(self, rule: AlertRule, current_value: float) -> None:
        """Generate an alert based on a rule."""
        # Check if we already have an active alert for this rule
        existing_alert = next(
            (alert for alert in self.active_alerts 
             if alert.rule_name == rule.name and not alert.resolved),
            None
        )
        
        if existing_alert:
            return  # Don't generate duplicate alerts
            
        alert = Alert(
            rule_name=rule.name,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            severity=rule.severity,
            message=f"Alert: {rule.metric_name} is {current_value} (threshold: {rule.threshold})"
        )
        
        self.active_alerts.append(alert)
        rule.last_triggered = datetime.now()
        
        logger.warning(f"Alert generated: {alert.message}")
        
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = [alert for alert in self.active_alerts if not alert.resolved]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
            
        return alerts
        
    def resolve_alert(self, rule_name: str) -> bool:
        """Resolve an active alert."""
        for alert in self.active_alerts:
            if alert.rule_name == rule_name and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Alert resolved: {rule_name}")
                return True
        return False
        
    async def collect_all_metrics(self) -> None:
        """Collect metrics from all registered collectors."""
        for collector in self.collectors:
            try:
                metrics = await collector.collect()
                for name, value in metrics.items():
                    self.record_metric(name, value)
            except Exception as e:
                logger.error(f"Failed to collect metrics from {collector.name}: {str(e)}")
                self.record_error(f"collector_error_{collector.name}", str(e))
                
    async def start_monitoring(self) -> None:
        """Start continuous performance monitoring."""
        if self.is_running:
            logger.warning("Performance monitoring is already running")
            return
            
        self.is_running = True
        logger.info("Starting performance monitoring")
        
        try:
            while self.is_running:
                await self.collect_all_metrics()
                self._check_alerts()
                await asyncio.sleep(self.collection_interval)
        except Exception as e:
            logger.error(f"Performance monitoring error: {str(e)}")
        finally:
            self.is_running = False
            
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.is_running = False
        logger.info("Stopped performance monitoring")
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        summary = {
            "metrics_count": len(self.metrics),
            "error_types_count": len(self.error_metrics),
            "active_alerts_count": len(self.get_active_alerts()),
            "collectors_count": len(self.collectors),
            "metrics": {},
            "errors": {},
            "resource_utilization": None
        }
        
        # Add latest metric values
        for name, metric in self.metrics.items():
            latest = metric.get_latest_value()
            if latest:
                summary["metrics"][name] = {
                    "value": latest.value,
                    "timestamp": latest.timestamp.isoformat(),
                    "type": metric.metric_type.value,
                    "unit": metric.unit
                }
                
        # Add error metrics
        for error_type, error_metric in self.error_metrics.items():
            summary["errors"][error_type] = {
                "count": error_metric.count,
                "error_rate": error_metric.error_rate,
                "last_occurrence": error_metric.last_occurrence.isoformat() if error_metric.last_occurrence else None
            }
            
        # Add resource utilization
        resource_util = self.get_resource_utilization()
        if resource_util:
            summary["resource_utilization"] = {
                "cpu_percent": resource_util.cpu_percent,
                "memory_percent": resource_util.memory_percent,
                "disk_usage_percent": resource_util.disk_usage_percent,
                "network_io_bytes": resource_util.network_io_bytes
            }
            
        return summary