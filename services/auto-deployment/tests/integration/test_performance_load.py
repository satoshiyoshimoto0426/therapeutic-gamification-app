"""
Performance and load testing integration tests.

Tests system performance under various load conditions,
including concurrent deployments, memory usage, and scalability.
"""

import pytest
import asyncio
import time
import psutil
import gc
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import threading
from concurrent.futures import ThreadPoolExecutor

from services.auto_deployment.orchestrator import DeploymentOrchestrator
from services.auto_deployment.config import DeploymentConfig
from services.auto_deployment.exceptions import DeploymentError


class TestPerformanceScenarios:
    """Test performance under various load conditions."""
    
    @pytest.fixture
    def deployment_config(self):
        """Create test deployment configuration."""
        return DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging",
            memory="1Gi",
            cpu="1",
            min_instances=1,
            max_instances=10
        )
    
    @pytest.mark.asyncio
    async def test_concurrent_deployments_performance(self, deployment_config):
        """Test performance with multiple concurrent deployments."""
        num_concurrent = 10
        orchestrators = []
        
        # Create multiple orchestrators
        for i in range(num_concurrent):
            config = deployment_config.copy()
            config.service_name = f"test-service-{i}"
            
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Mock deployment with realistic delay
                async def mock_deploy():
                    await asyncio.sleep(0.1)  # Simulate deployment time
                    return {
                        'revision_name': f'{config.service_name}-staging-001',
                        'status': 'success'
                    }
                
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                orchestrators.append(orchestrator)
        
        # Execute concurrent deployments and measure performance
        start_time = time.time()
        tasks = [orchestrator.deploy() for orchestrator in orchestrators]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all deployments succeeded
        for result in results:
            assert result['status'] == 'success'
        
        # Verify deployments ran concurrently (should take ~0.1s, not 1.0s)
        total_time = end_time - start_time
        assert total_time < 0.3, f"Concurrent deployments took {total_time:.2f}s, expected < 0.3s"
        
        # Calculate throughput
        throughput = num_concurrent / total_time
        assert throughput > 30, f"Throughput {throughput:.2f} deployments/sec is too low"
    
    @pytest.mark.asyncio
    async def test_deployment_timeout_handling(self, deployment_config):
        """Test handling of deployment timeouts under load."""
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            orchestrator.deployment_timeout = 0.1  # Very short timeout for testing
            
            # Mock slow deployment
            async def slow_deploy():
                await asyncio.sleep(0.2)  # Longer than timeout
                return {'revision_name': 'test-revision-001', 'status': 'success'}
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=slow_deploy)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Execute deployment and expect timeout
            start_time = time.time()
            with pytest.raises(asyncio.TimeoutError):
                await orchestrator.deploy_with_timeout()
            end_time = time.time()
            
            # Verify timeout was enforced
            assert end_time - start_time < 0.15, "Timeout not properly enforced"
    
    def test_memory_usage_during_deployment(self, deployment_config):
        """Test memory usage remains reasonable during deployment."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create and destroy multiple orchestrators to test memory leaks
        for i in range(100):
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                config = deployment_config.copy()
                config.service_name = f"test-service-{i}"
                orchestrator = DeploymentOrchestrator(config)
                
                # Simulate some work
                orchestrator.config.service_name = f"test-service-{i}"
                orchestrator.config.environment = "staging"
        
        # Force garbage collection
        gc.collect()
        
        # Measure final memory
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"
    
    @pytest.mark.asyncio
    async def test_high_frequency_deployments(self, deployment_config):
        """Test system performance with high-frequency deployments."""
        num_deployments = 50
        deployment_interval = 0.02  # 50 deployments per second
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock fast deployment
            deployment_count = 0
            async def mock_deploy():
                nonlocal deployment_count
                deployment_count += 1
                await asyncio.sleep(0.01)  # Very fast deployment
                return {
                    'revision_name': f'test-service-staging-{deployment_count:03d}',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Execute high-frequency deployments
            start_time = time.time()
            tasks = []
            
            for i in range(num_deployments):
                task = asyncio.create_task(orchestrator.deploy())
                tasks.append(task)
                await asyncio.sleep(deployment_interval)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify all deployments succeeded
            success_count = sum(1 for result in results if result['status'] == 'success')
            assert success_count == num_deployments
            
            # Verify performance metrics
            total_time = end_time - start_time
            actual_frequency = num_deployments / total_time
            assert actual_frequency > 20, f"Deployment frequency {actual_frequency:.2f}/sec is too low"
    
    @pytest.mark.asyncio
    async def test_resource_contention_handling(self, deployment_config):
        """Test handling of resource contention scenarios."""
        num_services = 5
        
        # Create multiple services competing for resources
        tasks = []
        
        for i in range(num_services):
            config = deployment_config.copy()
            config.service_name = f"resource-intensive-service-{i}"
            config.memory = "2Gi"  # High memory requirement
            config.cpu = "2"       # High CPU requirement
            
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Mock resource-intensive deployment
                async def mock_resource_intensive_deploy():
                    await asyncio.sleep(0.1)  # Simulate resource allocation time
                    # Simulate occasional resource contention
                    if i % 3 == 0:  # Every third service faces contention
                        raise DeploymentError("Resource quota exceeded")
                    return {
                        'revision_name': f'{config.service_name}-staging-001',
                        'status': 'success'
                    }
                
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_resource_intensive_deploy)
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                tasks.append(orchestrator.deploy())
        
        # Execute deployments and handle resource contention
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful vs failed deployments
        successful = sum(1 for result in results if isinstance(result, dict) and result.get('status') == 'success')
        failed = sum(1 for result in results if isinstance(result, Exception))
        
        # Should have some successes and some failures due to resource contention
        assert successful > 0, "No deployments succeeded"
        assert failed > 0, "No resource contention occurred"
        assert successful + failed == num_services
    
    @pytest.mark.asyncio
    async def test_scalability_limits(self, deployment_config):
        """Test system behavior at scalability limits."""
        max_concurrent = 100  # Test with high concurrency
        
        # Create a large number of concurrent deployments
        tasks = []
        
        for i in range(max_concurrent):
            config = deployment_config.copy()
            config.service_name = f"scale-test-service-{i}"
            
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Mock deployment with variable delay to simulate real conditions
                async def mock_variable_deploy():
                    delay = 0.05 + (i % 10) * 0.01  # Variable delay 0.05-0.14s
                    await asyncio.sleep(delay)
                    return {
                        'revision_name': f'{config.service_name}-staging-001',
                        'status': 'success'
                    }
                
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_variable_deploy)
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                tasks.append(orchestrator.deploy())
        
        # Execute all deployments and measure performance
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful = sum(1 for result in results if isinstance(result, dict) and result.get('status') == 'success')
        failed = sum(1 for result in results if isinstance(result, Exception))
        
        total_time = end_time - start_time
        throughput = successful / total_time
        
        # Verify system handled high concurrency reasonably
        success_rate = successful / max_concurrent
        assert success_rate > 0.8, f"Success rate {success_rate:.2%} is too low for scalability test"
        assert throughput > 50, f"Throughput {throughput:.2f} deployments/sec is insufficient at scale"


class TestLoadTestingScenarios:
    """Test specific load testing scenarios."""
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self):
        """Test performance under sustained load over time."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="load-test-service",
            region="us-central1",
            environment="staging"
        )
        
        duration = 2.0  # Test for 2 seconds
        deployment_rate = 10  # 10 deployments per second
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Track performance metrics
            deployment_times = []
            
            async def mock_timed_deploy():
                start = time.time()
                await asyncio.sleep(0.05)  # Simulate deployment work
                end = time.time()
                deployment_times.append(end - start)
                return {
                    'revision_name': f'load-test-service-staging-{len(deployment_times):03d}',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_timed_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Generate sustained load
            start_time = time.time()
            tasks = []
            
            while time.time() - start_time < duration:
                task = asyncio.create_task(orchestrator.deploy())
                tasks.append(task)
                await asyncio.sleep(1.0 / deployment_rate)
            
            results = await asyncio.gather(*tasks)
            
            # Analyze performance under sustained load
            successful_deployments = len([r for r in results if r['status'] == 'success'])
            avg_deployment_time = sum(deployment_times) / len(deployment_times)
            max_deployment_time = max(deployment_times)
            
            # Verify performance remained stable under load
            assert successful_deployments > duration * deployment_rate * 0.8
            assert avg_deployment_time < 0.1, f"Average deployment time {avg_deployment_time:.3f}s too high"
            assert max_deployment_time < 0.2, f"Max deployment time {max_deployment_time:.3f}s too high"
    
    @pytest.mark.asyncio
    async def test_burst_load_handling(self):
        """Test handling of sudden burst loads."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="burst-test-service",
            region="us-central1",
            environment="staging"
        )
        
        # Simulate burst: 50 deployments in quick succession
        burst_size = 50
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock deployment with queue simulation
            queue_delay = 0
            
            async def mock_queued_deploy():
                nonlocal queue_delay
                queue_delay += 0.001  # Simulate increasing queue delay
                await asyncio.sleep(0.02 + queue_delay)
                return {
                    'revision_name': f'burst-test-service-staging-{int(time.time() * 1000)}',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_queued_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Create burst load
            start_time = time.time()
            tasks = [orchestrator.deploy() for _ in range(burst_size)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify burst handling
            successful = sum(1 for result in results if result['status'] == 'success')
            total_time = end_time - start_time
            
            assert successful == burst_size, f"Only {successful}/{burst_size} deployments succeeded"
            assert total_time < 5.0, f"Burst took {total_time:.2f}s, too slow"
    
    def test_thread_safety_under_load(self):
        """Test thread safety with concurrent access."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="thread-test-service",
            region="us-central1",
            environment="staging"
        )
        
        # Shared state to test thread safety
        shared_counter = {'value': 0}
        lock = threading.Lock()
        
        def deployment_worker(worker_id):
            """Worker function for thread-based deployment."""
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Mock thread-safe deployment
                def mock_thread_safe_deploy():
                    with lock:
                        shared_counter['value'] += 1
                        current_value = shared_counter['value']
                    
                    time.sleep(0.01)  # Simulate work
                    
                    return {
                        'revision_name': f'thread-test-service-staging-{current_value:03d}',
                        'status': 'success',
                        'worker_id': worker_id
                    }
                
                orchestrator.validator.validate_all = Mock(return_value=True)
                orchestrator.environment_manager.setup_environment = Mock(return_value=True)
                orchestrator.deployment_engine.deploy = Mock(side_effect=mock_thread_safe_deploy)
                orchestrator.health_monitor.check_health = Mock(return_value=True)
                orchestrator.notification_manager.send_notification = Mock()
                
                # Perform multiple deployments per worker
                results = []
                for _ in range(5):
                    try:
                        result = asyncio.run(orchestrator.deploy())
                        results.append(result)
                    except Exception as e:
                        results.append({'status': 'failed', 'error': str(e)})
                
                return results
        
        # Run multiple workers concurrently
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(deployment_worker, i) for i in range(num_workers)]
            all_results = []
            
            for future in futures:
                worker_results = future.result()
                all_results.extend(worker_results)
        
        # Verify thread safety
        successful = sum(1 for result in all_results if result['status'] == 'success')
        expected_total = num_workers * 5
        
        assert successful == expected_total, f"Thread safety issue: {successful}/{expected_total} succeeded"
        assert shared_counter['value'] == expected_total, f"Counter mismatch: {shared_counter['value']}/{expected_total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])