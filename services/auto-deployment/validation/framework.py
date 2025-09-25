"""
Main validation framework orchestrator.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Type
from datetime import datetime

from .base import BaseValidator, ValidationResult, ValidationSeverity
from .config import ValidationConfig


logger = logging.getLogger(__name__)


class ValidationFramework:
    """Main validation framework that orchestrates all validators."""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validators: Dict[str, BaseValidator] = {}
        self.results: List[ValidationResult] = []
        
    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator with the framework."""
        self.validators[validator.name] = validator
        logger.info(f"Registered validator: {validator.name}")
    
    def register_validator_class(
        self,
        validator_class: Type[BaseValidator],
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a validator class with optional configuration."""
        validator_config = config or self.config.get_validator_config(validator_class.__name__)
        validator = validator_class(validator_config)
        self.register_validator(validator)
    
    def get_enabled_validators(self) -> List[BaseValidator]:
        """Get list of enabled validators."""
        return [
            validator for validator in self.validators.values()
            if validator.is_enabled and self.config.is_validator_enabled(validator.name)
        ]
    
    async def run_validation(
        self,
        validators: Optional[List[str]] = None,
        environment: Optional[str] = None
    ) -> List[ValidationResult]:
        """
        Run validation checks.
        
        Args:
            validators: Optional list of validator names to run. If None, runs all enabled validators.
            environment: Target environment for deployment
            
        Returns:
            List of validation results
        """
        if not self.config.enabled:
            logger.info("Validation framework is disabled")
            return []
        
        # Determine which validators to run
        if validators:
            validators_to_run = [
                self.validators[name] for name in validators
                if name in self.validators and self.validators[name].is_enabled
            ]
        else:
            validators_to_run = self.get_enabled_validators()
        
        if not validators_to_run:
            logger.warning("No validators to run")
            return []
        
        logger.info(f"Running {len(validators_to_run)} validators")
        
        # Apply environment-specific configuration
        if environment:
            env_config = self.config.get_environment_config(environment)
            logger.info(f"Applying environment config for: {environment}")
        
        # Run validators
        if self.config.parallel_execution:
            results = await self._run_parallel(validators_to_run)
        else:
            results = await self._run_sequential(validators_to_run)
        
        self.results.extend(results)
        
        # Log summary
        self._log_validation_summary(results)
        
        return results
    
    async def _run_parallel(self, validators: List[BaseValidator]) -> List[ValidationResult]:
        """Run validators in parallel."""
        tasks = []
        
        for validator in validators:
            task = asyncio.create_task(
                self._run_single_validator(validator),
                name=f"validate_{validator.name}"
            )
            tasks.append(task)
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"Validation timed out after {self.config.timeout_seconds} seconds")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # Create timeout results for incomplete validators
            results = []
            for i, validator in enumerate(validators):
                if i < len(tasks) and tasks[i].done():
                    try:
                        result = tasks[i].result()
                        if isinstance(result, Exception):
                            results.append(self._create_error_result(validator, result))
                        else:
                            results.append(result)
                    except asyncio.CancelledError:
                        results.append(self._create_timeout_result(validator))
                else:
                    results.append(self._create_timeout_result(validator))
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(self._create_error_result(validators[i], result))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _run_sequential(self, validators: List[BaseValidator]) -> List[ValidationResult]:
        """Run validators sequentially."""
        results = []
        
        for validator in validators:
            try:
                result = await self._run_single_validator(validator)
                results.append(result)
                
                # Check if we should fail fast
                if self.config.fail_fast and result.is_blocking:
                    logger.info(f"Failing fast due to blocking error from {validator.name}")
                    break
                    
            except Exception as e:
                logger.error(f"Error running validator {validator.name}: {e}")
                results.append(self._create_error_result(validator, e))
                
                if self.config.fail_fast:
                    break
        
        return results
    
    async def _run_single_validator(self, validator: BaseValidator) -> ValidationResult:
        """Run a single validator with error handling."""
        logger.info(f"Running validator: {validator.name}")
        start_time = datetime.utcnow()
        
        try:
            result = await validator.validate()
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Validator {validator.name} completed in {duration:.2f}s: {result.severity.value}")
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Validator {validator.name} failed after {duration:.2f}s: {e}")
            raise
    
    def _create_error_result(self, validator: BaseValidator, error: Exception) -> ValidationResult:
        """Create an error result for a failed validator."""
        return ValidationResult(
            validator_name=validator.name,
            severity=ValidationSeverity.ERROR,
            message=f"Validator failed with error: {str(error)}",
            success=False,
            timestamp=datetime.utcnow(),
            details={'error_type': type(error).__name__, 'error_message': str(error)},
            remediation_steps=[
                "Check validator configuration",
                "Review validator logs for detailed error information",
                "Ensure all dependencies are available"
            ]
        )
    
    def _create_timeout_result(self, validator: BaseValidator) -> ValidationResult:
        """Create a timeout result for a validator that didn't complete."""
        return ValidationResult(
            validator_name=validator.name,
            severity=ValidationSeverity.ERROR,
            message=f"Validator timed out after {self.config.timeout_seconds} seconds",
            success=False,
            timestamp=datetime.utcnow(),
            details={'timeout_seconds': self.config.timeout_seconds},
            remediation_steps=[
                "Increase validation timeout in configuration",
                "Check if validator is hanging on external dependencies",
                "Consider running validator separately for debugging"
            ]
        )
    
    def _log_validation_summary(self, results: List[ValidationResult]) -> None:
        """Log a summary of validation results."""
        if not results:
            return
        
        summary = {
            'total': len(results),
            'success': len([r for r in results if r.success]),
            'warnings': len([r for r in results if r.severity == ValidationSeverity.WARNING]),
            'errors': len([r for r in results if r.severity == ValidationSeverity.ERROR]),
            'critical': len([r for r in results if r.severity == ValidationSeverity.CRITICAL])
        }
        
        logger.info(f"Validation summary: {summary}")
        
        # Log individual failures
        for result in results:
            if not result.success:
                logger.error(f"{result.validator_name}: {result.message}")
    
    def has_blocking_errors(self, results: Optional[List[ValidationResult]] = None) -> bool:
        """Check if there are any blocking errors in the results."""
        results_to_check = results or self.results
        return any(result.is_blocking for result in results_to_check)
    
    def get_results_by_severity(
        self,
        severity: ValidationSeverity,
        results: Optional[List[ValidationResult]] = None
    ) -> List[ValidationResult]:
        """Get results filtered by severity."""
        results_to_filter = results or self.results
        return [result for result in results_to_filter if result.severity == severity]
    
    def clear_results(self) -> None:
        """Clear stored validation results."""
        self.results.clear()
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        if not self.results:
            return {'status': 'no_validation_run', 'results': []}
        
        blocking_errors = self.has_blocking_errors()
        
        return {
            'status': 'failed' if blocking_errors else 'passed',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_validators': len(self.results),
                'successful': len([r for r in self.results if r.success]),
                'warnings': len(self.get_results_by_severity(ValidationSeverity.WARNING)),
                'errors': len(self.get_results_by_severity(ValidationSeverity.ERROR)),
                'critical': len(self.get_results_by_severity(ValidationSeverity.CRITICAL)),
                'blocking_errors': blocking_errors
            },
            'results': [
                {
                    'validator': result.validator_name,
                    'severity': result.severity.value,
                    'message': result.message,
                    'success': result.success,
                    'timestamp': result.timestamp.isoformat(),
                    'details': result.details,
                    'remediation_steps': result.remediation_steps
                }
                for result in self.results
            ]
        }