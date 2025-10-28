"""
Unit tests for health check framework.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

from health_check import (
    HealthCheckFramework,
    HealthCheckResult,
    HealthCheckConfig,
    HealthStatus,
    HTTPHealthCheck,
    CustomHealthCheck
)


class TestHealthCheckResult:
    """Test HealthCheckResult dataclass."""
    
    def test_health_check_result_creation(self):
        """Test creating a health check result."""
        result = HealthCheckResult(
            check_name="test_check",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            response_time_ms=150.5,
            message="All good"
        )
        
        assert result.check_name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms == 150.5
        assert result.message == "All good"
        assert result.details == {}
        assert result.error is None


class TestHealthCheckConfig:
    """Test HealthCheckConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HealthCheckConfig()
        
        assert config.endpoints == ["/health", "/api/health"]
        assert config.timeout_seconds == 30
        assert config.retry_attempts == 3
        assert config.success_threshold == 0.95
        assert config.performance_threshold_ms == 2000
        
    def test_custom_config(self):
        """Test custom configuration values."""
        config = HealthCheckConfig(
            endpoints=["/custom/health"],
            timeout_seconds=10,
            retry_attempts=1,
            success_threshold=0.8
        )
        
        assert config.endpoints == ["/custom/health"]
        assert config.timeout_seconds == 10
        assert config.retry_attempts == 1
        assert config.success_threshold == 0.8


class TestHTTPHealthCheck:
    """Test HTTP health check implementation."""
    
    def test_http_check_initialization(self):
        """Test HTTP health check initialization."""
        config = HealthCheckConfig(timeout_seconds=5)
        check = HTTPHealthCheck("test_http", "http://example.com/health", config)
        
        assert check.name == "test_http"
        assert check.url == "http://example.com/health"
        assert check.config.timeout_seconds == 5
        
    @pytest.mark.asyncio
    async def test_http_check_exception_handling(self):
        """Test HTTP health check exception handling."""
        config = HealthCheckConfig(timeout_seconds=1)
        check = HTTPHealthCheck("test_http", "http://invalid-url", config)
        
        # This will fail due to invalid URL, testing exception handling
        result = await check.execute()
        
        assert result.check_name == "test_http"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message in ["Health check failed", "Request timeout"]  # Either is acceptable
        assert result.error is not None
        assert result.details["url"] == "http://invalid-url"


class TestCustomHealthCheck:
    """Test custom health check implementation."""
    
    @pytest.mark.asyncio
    async def test_successful_custom_check(self):
        """Test successful custom health check."""
        def custom_check():
            return HealthCheckResult(
                check_name="custom_test",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=50,
                message="Custom check passed"
            )
            
        check = CustomHealthCheck("custom_test", custom_check)
        result = await check.execute()
        
        assert result.check_name == "custom_test"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Custom check passed"
        
    @pytest.mark.asyncio
    async def test_async_custom_check(self):
        """Test async custom health check."""
        async def async_custom_check():
            await asyncio.sleep(0.01)  # Simulate async work
            return HealthCheckResult(
                check_name="async_custom_test",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=10,
                message="Async custom check passed"
            )
            
        check = CustomHealthCheck("async_custom_test", async_custom_check)
        result = await check.execute()
        
        assert result.check_name == "async_custom_test"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Async custom check passed"
        
    @pytest.mark.asyncio
    async def test_failed_custom_check(self):
        """Test failed custom health check."""
        def failing_check():
            raise Exception("Custom check failed")
            
        check = CustomHealthCheck("failing_test", failing_check)
        result = await check.execute()
        
        assert result.check_name == "failing_test"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Custom check failed"
        assert "Custom check failed" in result.error


class TestHealthCheckFramework:
    """Test health check framework."""
    
    def test_framework_initialization(self):
        """Test framework initialization."""
        config = HealthCheckConfig(timeout_seconds=10)
        framework = HealthCheckFramework(config)
        
        assert framework.config.timeout_seconds == 10
        assert len(framework.checks) == 0
        assert len(framework.results_history) == 0
        assert not framework.is_running
        
    def test_register_http_check(self):
        """Test registering HTTP health check."""
        framework = HealthCheckFramework()
        framework.register_http_check("test_http", "http://example.com/health")
        
        assert "test_http" in framework.checks
        assert isinstance(framework.checks["test_http"], HTTPHealthCheck)
        
    def test_register_custom_check(self):
        """Test registering custom health check."""
        framework = HealthCheckFramework()
        
        def custom_check():
            return HealthCheckResult(
                check_name="custom",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        framework.register_custom_check("custom", custom_check)
        
        assert "custom" in framework.checks
        assert isinstance(framework.checks["custom"], CustomHealthCheck)
        
    def test_unregister_check(self):
        """Test unregistering health check."""
        framework = HealthCheckFramework()
        framework.register_http_check("test_http", "http://example.com/health")
        
        assert "test_http" in framework.checks
        
        framework.unregister_check("test_http")
        
        assert "test_http" not in framework.checks
        
    @pytest.mark.asyncio
    async def test_execute_single_check(self):
        """Test executing single health check."""
        framework = HealthCheckFramework()
        
        def custom_check():
            return HealthCheckResult(
                check_name="test",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=100
            )
            
        framework.register_custom_check("test", custom_check)
        result = await framework.execute_check("test")
        
        assert result is not None
        assert result.check_name == "test"
        assert result.status == HealthStatus.HEALTHY
        assert len(framework.results_history) == 1
        
    @pytest.mark.asyncio
    async def test_execute_nonexistent_check(self):
        """Test executing non-existent health check."""
        framework = HealthCheckFramework()
        result = await framework.execute_check("nonexistent")
        
        assert result is None
        
    @pytest.mark.asyncio
    async def test_execute_all_checks(self):
        """Test executing all health checks."""
        framework = HealthCheckFramework()
        
        def check1():
            return HealthCheckResult(
                check_name="check1",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=50
            )
            
        def check2():
            return HealthCheckResult(
                check_name="check2",
                status=HealthStatus.WARNING,
                timestamp=datetime.now(),
                response_time_ms=150
            )
            
        framework.register_custom_check("check1", check1)
        framework.register_custom_check("check2", check2)
        
        results = await framework.execute_all_checks()
        
        assert len(results) == 2
        assert len(framework.results_history) == 2
        
    def test_get_overall_health_healthy(self):
        """Test overall health calculation - healthy."""
        framework = HealthCheckFramework()
        
        # Add healthy results
        for i in range(3):
            framework.results_history.append(
                HealthCheckResult(
                    check_name=f"check{i}",
                    status=HealthStatus.HEALTHY,
                    timestamp=datetime.now(),
                    response_time_ms=100
                )
            )
            
        overall_health = framework.get_overall_health()
        assert overall_health == HealthStatus.HEALTHY
        
    def test_get_overall_health_unhealthy(self):
        """Test overall health calculation - unhealthy."""
        framework = HealthCheckFramework()
        
        # Add mostly unhealthy results
        for i in range(3):
            status = HealthStatus.UNHEALTHY if i < 2 else HealthStatus.HEALTHY
            framework.results_history.append(
                HealthCheckResult(
                    check_name=f"check{i}",
                    status=status,
                    timestamp=datetime.now(),
                    response_time_ms=100
                )
            )
            
        overall_health = framework.get_overall_health()
        assert overall_health == HealthStatus.UNHEALTHY
        
    def test_get_overall_health_unknown(self):
        """Test overall health calculation - unknown."""
        framework = HealthCheckFramework()
        overall_health = framework.get_overall_health()
        assert overall_health == HealthStatus.UNKNOWN
        
    def test_get_check_results_filtered(self):
        """Test getting filtered check results."""
        framework = HealthCheckFramework()
        
        # Add results for different checks
        framework.results_history.extend([
            HealthCheckResult(
                check_name="check1",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=100
            ),
            HealthCheckResult(
                check_name="check2",
                status=HealthStatus.WARNING,
                timestamp=datetime.now(),
                response_time_ms=200
            ),
            HealthCheckResult(
                check_name="check1",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=120
            )
        ])
        
        check1_results = framework.get_check_results("check1")
        assert len(check1_results) == 2
        assert all(r.check_name == "check1" for r in check1_results)
        
        all_results = framework.get_check_results()
        assert len(all_results) == 3
        
    def test_get_check_results_limited(self):
        """Test getting limited check results."""
        framework = HealthCheckFramework()
        
        # Add many results
        for i in range(10):
            framework.results_history.append(
                HealthCheckResult(
                    check_name="test",
                    status=HealthStatus.HEALTHY,
                    timestamp=datetime.now(),
                    response_time_ms=100
                )
            )
            
        limited_results = framework.get_check_results(limit=5)
        assert len(limited_results) == 5
        
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry logic for failed checks."""
        config = HealthCheckConfig(retry_attempts=2, retry_delay_seconds=0.01)
        framework = HealthCheckFramework(config)
        
        call_count = 0
        
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt fails")
            return HealthCheckResult(
                check_name="retry_test",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time_ms=50
            )
            
        framework.register_custom_check("retry_test", failing_then_success)
        result = await framework.execute_check("retry_test")
        
        assert result.status == HealthStatus.HEALTHY
        assert call_count == 2  # First failed, second succeeded


if __name__ == "__main__":
    pytest.main([__file__])