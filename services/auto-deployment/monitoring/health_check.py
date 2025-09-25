"""
Health check framework for auto-deployment monitoring.

This module provides a configurable health check system with support for
HTTP endpoint checks and custom health check implementations.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import aiohttp
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check execution."""
    check_name: str
    status: HealthStatus
    timestamp: datetime
    response_time_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    endpoints: List[str] = field(default_factory=lambda: ["/health", "/api/health"])
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    success_threshold: float = 0.95
    performance_threshold_ms: int = 2000
    check_interval_seconds: int = 60
    custom_headers: Dict[str, str] = field(default_factory=dict)
    expected_status_codes: List[int] = field(default_factory=lambda: [200])


class BaseHealthCheck(ABC):
    """Abstract base class for health checks."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    async def execute(self) -> HealthCheckResult:
        """Execute the health check and return result."""
        pass


class HTTPHealthCheck(BaseHealthCheck):
    """HTTP endpoint health check implementation."""
    
    def __init__(self, name: str, url: str, config: Optional[HealthCheckConfig] = None):
        super().__init__(name)
        self.url = url
        self.config = config or HealthCheckConfig()
        
    async def execute(self) -> HealthCheckResult:
        """Execute HTTP health check."""
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.url,
                    headers=self.config.custom_headers
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    # Check status code
                    if response.status in self.config.expected_status_codes:
                        status = HealthStatus.HEALTHY
                        message = f"HTTP check passed: {response.status}"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Unexpected status code: {response.status}"
                    
                    # Check performance threshold
                    if response_time_ms > self.config.performance_threshold_ms:
                        if status == HealthStatus.HEALTHY:
                            status = HealthStatus.WARNING
                        message += f" (slow response: {response_time_ms:.1f}ms)"
                    
                    response_text = await response.text()
                    
                    return HealthCheckResult(
                        check_name=self.name,
                        status=status,
                        timestamp=datetime.now(),
                        response_time_ms=response_time_ms,
                        message=message,
                        details={
                            "url": self.url,
                            "status_code": response.status,
                            "response_body": response_text[:500]  # Truncate long responses
                        }
                    )
                    
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(),
                response_time_ms=response_time_ms,
                message="Request timeout",
                error=f"Timeout after {self.config.timeout_seconds}s",
                details={"url": self.url}
            )
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Health check {self.name} failed: {str(e)}")
            
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(),
                response_time_ms=response_time_ms,
                message="Health check failed",
                error=str(e),
                details={"url": self.url}
            )


class CustomHealthCheck(BaseHealthCheck):
    """Custom health check implementation using user-provided function."""
    
    def __init__(self, name: str, check_function: Callable[[], HealthCheckResult]):
        super().__init__(name)
        self.check_function = check_function
        
    async def execute(self) -> HealthCheckResult:
        """Execute custom health check function."""
        try:
            if asyncio.iscoroutinefunction(self.check_function):
                return await self.check_function()
            else:
                return self.check_function()
        except Exception as e:
            logger.error(f"Custom health check {self.name} failed: {str(e)}")
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(),
                response_time_ms=0,
                message="Custom check failed",
                error=str(e)
            )


class HealthCheckFramework:
    """Main health check framework orchestrator."""
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self.checks: Dict[str, BaseHealthCheck] = {}
        self.results_history: List[HealthCheckResult] = []
        self.is_running = False
        
    def register_http_check(self, name: str, url: str, config: Optional[HealthCheckConfig] = None) -> None:
        """Register an HTTP health check."""
        check_config = config or self.config
        self.checks[name] = HTTPHealthCheck(name, url, check_config)
        logger.info(f"Registered HTTP health check: {name} -> {url}")
        
    def register_custom_check(self, name: str, check_function: Callable[[], HealthCheckResult]) -> None:
        """Register a custom health check."""
        self.checks[name] = CustomHealthCheck(name, check_function)
        logger.info(f"Registered custom health check: {name}")
        
    def unregister_check(self, name: str) -> None:
        """Unregister a health check."""
        if name in self.checks:
            del self.checks[name]
            logger.info(f"Unregistered health check: {name}")
            
    async def execute_check(self, name: str) -> Optional[HealthCheckResult]:
        """Execute a single health check by name."""
        if name not in self.checks:
            logger.warning(f"Health check not found: {name}")
            return None
            
        check = self.checks[name]
        result = await self._execute_with_retry(check)
        self.results_history.append(result)
        
        # Keep history limited
        if len(self.results_history) > 1000:
            self.results_history = self.results_history[-500:]
            
        return result
        
    async def execute_all_checks(self) -> List[HealthCheckResult]:
        """Execute all registered health checks."""
        if not self.checks:
            logger.warning("No health checks registered")
            return []
            
        tasks = []
        for name in self.checks:
            tasks.append(self.execute_check(name))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, HealthCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Health check execution failed: {str(result)}")
                
        return valid_results
        
    async def _execute_with_retry(self, check: BaseHealthCheck) -> HealthCheckResult:
        """Execute health check with retry logic."""
        last_result = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                result = await check.execute()
                
                # If check is healthy, return immediately
                if result.status == HealthStatus.HEALTHY:
                    return result
                    
                last_result = result
                
                # If not the last attempt, wait before retry
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay_seconds)
                    
            except Exception as e:
                logger.error(f"Health check {check.name} attempt {attempt + 1} failed: {str(e)}")
                last_result = HealthCheckResult(
                    check_name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    timestamp=datetime.now(),
                    response_time_ms=0,
                    message="Health check execution failed",
                    error=str(e)
                )
                
        return last_result or HealthCheckResult(
            check_name=check.name,
            status=HealthStatus.UNKNOWN,
            timestamp=datetime.now(),
            response_time_ms=0,
            message="No result available"
        )
        
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health based on recent check results."""
        if not self.results_history:
            return HealthStatus.UNKNOWN
            
        # Get latest results for each check
        latest_results = {}
        for result in reversed(self.results_history):
            if result.check_name not in latest_results:
                latest_results[result.check_name] = result
                
        if not latest_results:
            return HealthStatus.UNKNOWN
            
        # Calculate health based on success threshold
        healthy_count = sum(1 for r in latest_results.values() if r.status == HealthStatus.HEALTHY)
        total_count = len(latest_results)
        success_rate = healthy_count / total_count
        
        if success_rate >= self.config.success_threshold:
            return HealthStatus.HEALTHY
        elif success_rate >= 0.5:
            return HealthStatus.WARNING
        else:
            return HealthStatus.UNHEALTHY
            
    def get_check_results(self, check_name: Optional[str] = None, limit: int = 100) -> List[HealthCheckResult]:
        """Get health check results history."""
        if check_name:
            results = [r for r in self.results_history if r.check_name == check_name]
        else:
            results = self.results_history
            
        return results[-limit:] if limit > 0 else results
        
    async def start_continuous_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self.is_running:
            logger.warning("Health monitoring is already running")
            return
            
        self.is_running = True
        logger.info("Starting continuous health monitoring")
        
        try:
            while self.is_running:
                await self.execute_all_checks()
                await asyncio.sleep(self.config.check_interval_seconds)
        except Exception as e:
            logger.error(f"Continuous monitoring error: {str(e)}")
        finally:
            self.is_running = False
            
    def stop_continuous_monitoring(self) -> None:
        """Stop continuous health monitoring."""
        self.is_running = False
        logger.info("Stopped continuous health monitoring")