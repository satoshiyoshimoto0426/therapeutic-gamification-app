"""
Rolling update deployment strategy implementation.
"""

import time
from datetime import datetime
from typing import Optional, Dict, List

from .base import DeploymentStrategy, DeploymentResult, DeploymentStatus, DeploymentConfig


class RollingUpdateDeploymentStrategy(DeploymentStrategy):
    """
    Rolling update deployment strategy.
    
    This strategy gradually shifts traffic from the old revision to the new revision,
    allowing for gradual rollout and easy rollback if issues are detected.
    """
    
    def __init__(self, config: DeploymentConfig):
        """Initialize Rolling Update deployment strategy."""
        super().__init__(config)
        self.current_revision = None
        self.new_revision = None
        self.old_revision = None
        self.traffic_steps = [10, 25, 50, 75, 100]  # Gradual traffic increase steps
    
    def deploy(self) -> DeploymentResult:
        """
        Execute Rolling Update deployment.
        
        Steps:
        1. Validate configuration
        2. Deploy new revision with minimal traffic
        3. Gradually increase traffic while monitoring health
        4. Complete rollout or rollback if issues detected
        
        Returns:
            DeploymentResult: Result of the deployment operation
        """
        try:
            # Validate configuration
            self.validate_config()
            
            start_time = datetime.now()
            
            # Step 1: Get current revision
            current_status = self.get_current_status()
            if current_status.revision_name:
                self.old_revision = current_status.revision_name
            
            # Step 2: Deploy new revision with initial traffic
            new_revision_result = self._deploy_new_revision()
            if new_revision_result.status != DeploymentStatus.SUCCESS:
                return new_revision_result
            
            # Step 3: Gradually increase traffic
            rollout_result = self._perform_gradual_rollout()
            if rollout_result.status != DeploymentStatus.SUCCESS:
                return rollout_result
            
            # Step 4: Complete deployment
            self.current_revision = self.new_revision
            
            result = DeploymentResult(
                status=DeploymentStatus.SUCCESS,
                message=f"Rolling update deployment completed successfully",
                timestamp=datetime.now(),
                revision_name=self.new_revision,
                traffic_allocation={self.new_revision: 100},
                rollback_revision=self.old_revision,
                metadata={
                    "strategy": "rolling-update",
                    "deployment_time": (datetime.now() - start_time).total_seconds(),
                    "old_revision": self.old_revision,
                    "new_revision": self.new_revision,
                    "traffic_steps": self.traffic_steps
                }
            )
            
            self.add_to_history(result)
            return result
            
        except Exception as e:
            error_result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                message=f"Rolling update deployment failed: {str(e)}",
                timestamp=datetime.now(),
                error_details=str(e)
            )
            self.add_to_history(error_result)
            return error_result
    
    def rollback(self, target_revision: Optional[str] = None) -> DeploymentResult:
        """
        Rollback to previous revision.
        
        Args:
            target_revision: Specific revision to rollback to
            
        Returns:
            DeploymentResult: Result of the rollback operation
        """
        try:
            rollback_target = target_revision or self.old_revision
            
            if not rollback_target:
                last_successful = self.get_last_successful_deployment()
                if last_successful and last_successful.rollback_revision:
                    rollback_target = last_successful.rollback_revision
                else:
                    return DeploymentResult(
                        status=DeploymentStatus.FAILED,
                        message="No rollback target available",
                        timestamp=datetime.now(),
                        error_details="No previous revision or rollback target specified"
                    )
            
            # Perform immediate rollback (switch all traffic back)
            rollback_result = self._perform_immediate_rollback(rollback_target)
            
            if rollback_result.status == DeploymentStatus.SUCCESS:
                self.current_revision = rollback_target
                
                result = DeploymentResult(
                    status=DeploymentStatus.ROLLED_BACK,
                    message=f"Successfully rolled back to revision {rollback_target}",
                    timestamp=datetime.now(),
                    revision_name=rollback_target,
                    traffic_allocation={rollback_target: 100},
                    metadata={
                        "strategy": "rolling-update",
                        "rollback_target": rollback_target
                    }
                )
            else:
                result = rollback_result
            
            self.add_to_history(result)
            return result
            
        except Exception as e:
            error_result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                message=f"Rollback failed: {str(e)}",
                timestamp=datetime.now(),
                error_details=str(e)
            )
            self.add_to_history(error_result)
            return error_result
    
    def get_current_status(self) -> DeploymentResult:
        """Get current deployment status."""
        # This would typically query the actual Cloud Run service
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Service is running",
            timestamp=datetime.now(),
            revision_name=self.current_revision or f"{self.config.service_name}-mock-revision",
            traffic_allocation={self.current_revision or f"{self.config.service_name}-mock-revision": 100}
        )
    
    def _deploy_new_revision(self) -> DeploymentResult:
        """Deploy new revision with initial traffic allocation."""
        # Generate new revision name
        timestamp = int(time.time())
        self.new_revision = f"{self.config.service_name}-{timestamp}"
        
        # Simulate deployment
        time.sleep(1)
        
        # Start with first traffic step
        initial_traffic = self.traffic_steps[0]
        
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message=f"New revision {self.new_revision} deployed with {initial_traffic}% traffic",
            timestamp=datetime.now(),
            revision_name=self.new_revision,
            traffic_allocation={
                self.new_revision: initial_traffic,
                self.old_revision: 100 - initial_traffic
            } if self.old_revision else {self.new_revision: 100}
        )
    
    def _perform_gradual_rollout(self) -> DeploymentResult:
        """Perform gradual traffic rollout with health monitoring."""
        for i, traffic_percentage in enumerate(self.traffic_steps):
            # Update traffic allocation
            traffic_result = self._update_traffic_allocation(traffic_percentage)
            if traffic_result.status != DeploymentStatus.SUCCESS:
                # Rollback on traffic update failure
                self._perform_immediate_rollback(self.old_revision)
                return DeploymentResult(
                    status=DeploymentStatus.FAILED,
                    message=f"Traffic update failed at {traffic_percentage}%, rolled back",
                    timestamp=datetime.now(),
                    error_details=traffic_result.error_details
                )
            
            # Perform health checks
            if not self._perform_health_checks_at_traffic_level(traffic_percentage):
                # Rollback on health check failure
                self._perform_immediate_rollback(self.old_revision)
                return DeploymentResult(
                    status=DeploymentStatus.FAILED,
                    message=f"Health checks failed at {traffic_percentage}% traffic, rolled back",
                    timestamp=datetime.now(),
                    error_details=f"Health checks failed at traffic level {traffic_percentage}%"
                )
            
            # Wait before next step (except for the last step)
            if i < len(self.traffic_steps) - 1:
                time.sleep(2)  # Wait between traffic increases
        
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Gradual rollout completed successfully",
            timestamp=datetime.now(),
            revision_name=self.new_revision,
            traffic_allocation={self.new_revision: 100}
        )
    
    def _update_traffic_allocation(self, new_revision_percentage: int) -> DeploymentResult:
        """Update traffic allocation between revisions."""
        # Simulate traffic update
        time.sleep(0.5)
        
        old_revision_percentage = 100 - new_revision_percentage
        
        traffic_allocation = {self.new_revision: new_revision_percentage}
        if self.old_revision and old_revision_percentage > 0:
            traffic_allocation[self.old_revision] = old_revision_percentage
        
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message=f"Traffic updated: {new_revision_percentage}% to new revision",
            timestamp=datetime.now(),
            revision_name=self.new_revision,
            traffic_allocation=traffic_allocation
        )
    
    def _perform_health_checks_at_traffic_level(self, traffic_percentage: int) -> bool:
        """Perform health checks at specific traffic level."""
        # Simulate health checks with different duration based on traffic level
        check_duration = max(1, traffic_percentage // 25)  # More thorough checks at higher traffic
        time.sleep(check_duration)
        
        # In real implementation, this would monitor error rates, response times, etc.
        # For now, assume health checks pass
        return True
    
    def _perform_immediate_rollback(self, target_revision: str) -> DeploymentResult:
        """Perform immediate rollback to target revision."""
        # Simulate immediate traffic switch
        time.sleep(1)
        
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message=f"Immediate rollback to {target_revision} completed",
            timestamp=datetime.now(),
            revision_name=target_revision,
            traffic_allocation={target_revision: 100}
        )
    
    def set_traffic_steps(self, steps: List[int]) -> None:
        """Set custom traffic rollout steps."""
        if not steps or not all(0 <= step <= 100 for step in steps):
            raise ValueError("Traffic steps must be between 0 and 100")
        
        # Remove duplicates and sort
        unique_steps = sorted(list(set(steps)))
        
        # Ensure final step is 100%
        if unique_steps[-1] != 100:
            unique_steps.append(100)
        
        self.traffic_steps = unique_steps