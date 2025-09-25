"""
Auto-deployment monitoring package.
"""

# Import only what's available to avoid circular imports
try:
    from .dashboard import MonitoringDashboardSystem, DashboardConfig, DashboardTheme, AlertChannel
    from .health_check import HealthCheckFramework, HealthCheckResult, HealthStatus
    from .performance_monitor import PerformanceMonitor, Alert, AlertSeverity
    
    __all__ = [
        'MonitoringDashboardSystem',
        'DashboardConfig', 
        'DashboardTheme',
        'AlertChannel',
        'HealthCheckFramework',
        'HealthCheckResult',
        'HealthStatus',
        'PerformanceMonitor',
        'Alert',
        'AlertSeverity'
    ]
except ImportError:
    # If imports fail, just define the package
    __all__ = []