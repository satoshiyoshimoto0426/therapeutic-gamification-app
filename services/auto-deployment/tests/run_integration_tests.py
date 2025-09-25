#!/usr/bin/env python3
"""
Integration and End-to-End Test Runner

Comprehensive test runner for the auto-deployment system that executes
all integration tests, performance tests, and generates detailed reports.
"""

import asyncio
import sys
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import test frameworks
from services.auto_deployment.tests.pipeline.test_execution_framework import (
    TestAutomationFramework, 
    TestExecutionFramework,
    SAMPLE_TEST_CONFIGURATIONS
)
from services.auto_deployment.tests.pipeline.test_environment_manager import (
    TestEnvironmentManager,
    TestEnvironmentFactory
)
from services.auto_deployment.tests.pipeline.test_reporting import (
    TestReportingPipeline,
    TestSuiteResult,
    TestResult
)


class IntegrationTestRunner:
    """Main runner for integration and end-to-end tests."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.test_config = self._load_configuration()
        self.automation_framework = TestAutomationFramework()
        self.reporting_pipeline = TestReportingPipeline()
        self.environment_manager = TestEnvironmentManager()
        self.environment_factory = TestEnvironmentFactory(self.environment_manager)
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load test configuration from file or use defaults."""
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.json'):
                    return json.load(f)
                elif self.config_file.endswith(('.yml', '.yaml')):
                    return yaml.safe_load(f)
        
        # Default configuration
        return {
            'test_suites': {
                'integration': {
                    'enabled': True,
                    'parallel': True,
                    'timeout': 300
                },
                'performance': {
                    'enabled': True,
                    'parallel': False,
                    'timeout': 600
                },
                'end_to_end': {
                    'enabled': True,
                    'parallel': False,
                    'timeout': 900
                }
            },
            'environments': {
                'testing': {
                    'project_id': 'test-project-integration',
                    'region': 'us-central1'
                }
            },
            'reporting': {
                'formats': ['html', 'json', 'csv'],
                'output_dir': 'test_reports',
                'include_trends': True
            }
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all configured test suites."""
        print("🚀 Starting Auto-Deployment Integration Tests")
        print(f"Configuration: {self.config_file or 'default'}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 60)
        
        overall_results = {
            'start_time': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {
                'total_suites': 0,
                'passed_suites': 0,
                'failed_suites': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        }
        
        try:
            # Run integration tests
            if self.test_config['test_suites']['integration']['enabled']:
                print("📋 Running Integration Tests...")
                integration_results = await self.run_integration_tests()
                overall_results['test_suites']['integration'] = integration_results
                self._update_summary(overall_results['summary'], integration_results)
            
            # Run performance tests
            if self.test_config['test_suites']['performance']['enabled']:
                print("⚡ Running Performance Tests...")
                performance_results = await self.run_performance_tests()
                overall_results['test_suites']['performance'] = performance_results
                self._update_summary(overall_results['summary'], performance_results)
            
            # Run end-to-end tests
            if self.test_config['test_suites']['end_to_end']['enabled']:
                print("🔄 Running End-to-End Tests...")
                e2e_results = await self.run_end_to_end_tests()
                overall_results['test_suites']['end_to_end'] = e2e_results
                self._update_summary(overall_results['summary'], e2e_results)
            
            overall_results['end_time'] = datetime.now().isoformat()
            
            # Generate comprehensive reports
            await self.generate_reports(overall_results)
            
            # Print summary
            self._print_summary(overall_results)
            
            return overall_results
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            overall_results['error'] = str(e)
            overall_results['end_time'] = datetime.now().isoformat()
            return overall_results
        
        finally:
            # Clean up test environments
            await self.environment_manager.cleanup_all_environments()
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration test suite."""
        integration_configs = [
            {
                'name': 'full_deployment_workflow',
                'scenario_type': 'basic_deployment',
                'environment': 'testing',
                'should_succeed': True,
                'test_type': 'integration'
            },
            {
                'name': 'multi_environment_deployment',
                'scenario_type': 'multi_environment',
                'environments': ['dev', 'staging'],
                'test_type': 'integration'
            },
            {
                'name': 'failure_recovery_integration',
                'scenario_type': 'failure_recovery',
                'failure_count': 2,
                'test_type': 'integration'
            },
            {
                'name': 'validation_failure_handling',
                'scenario_type': 'basic_deployment',
                'should_succeed': False,
                'failure_type': 'validation',
                'test_type': 'integration'
            }
        ]
        
        return await self.automation_framework.execution_framework.execute_test_suite(
            "integration_tests",
            integration_configs
        )
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance test suite."""
        performance_configs = [
            {
                'name': 'concurrent_deployments_performance',
                'scenario_type': 'performance_load',
                'concurrent_deployments': 10,
                'max_execution_time': 60.0,
                'min_success_rate': 0.9,
                'min_throughput': 5.0,
                'test_type': 'performance'
            },
            {
                'name': 'high_load_stress_test',
                'scenario_type': 'performance_load',
                'concurrent_deployments': 25,
                'max_execution_time': 120.0,
                'min_success_rate': 0.8,
                'min_throughput': 10.0,
                'test_type': 'performance'
            },
            {
                'name': 'sustained_load_test',
                'scenario_type': 'performance_load',
                'concurrent_deployments': 5,
                'max_execution_time': 300.0,
                'min_success_rate': 0.95,
                'min_throughput': 1.0,
                'test_type': 'performance'
            }
        ]
        
        return await self.automation_framework.execution_framework.execute_test_suite(
            "performance_tests",
            performance_configs
        )
    
    async def run_end_to_end_tests(self) -> Dict[str, Any]:
        """Run end-to-end test suite."""
        e2e_configs = [
            {
                'name': 'complete_deployment_lifecycle',
                'scenario_type': 'multi_environment',
                'environments': ['dev', 'staging', 'prod'],
                'test_type': 'end_to_end'
            },
            {
                'name': 'deployment_with_rollback',
                'scenario_type': 'failure_recovery',
                'failure_count': 1,
                'enable_rollback': True,
                'test_type': 'end_to_end'
            },
            {
                'name': 'security_compliance_e2e',
                'scenario_type': 'basic_deployment',
                'environment': 'production',
                'enable_security_checks': True,
                'test_type': 'end_to_end'
            }
        ]
        
        return await self.automation_framework.execution_framework.execute_test_suite(
            "end_to_end_tests",
            e2e_configs
        )
    
    def _update_summary(self, summary: Dict[str, int], suite_results: Dict[str, Any]):
        """Update overall summary with suite results."""
        summary['total_suites'] += 1
        
        if suite_results.get('summary', {}).get('failed', 0) == 0:
            summary['passed_suites'] += 1
        else:
            summary['failed_suites'] += 1
        
        suite_summary = suite_results.get('summary', {})
        summary['total_tests'] += suite_summary.get('total_tests', 0)
        summary['passed_tests'] += suite_summary.get('passed', 0)
        summary['failed_tests'] += suite_summary.get('failed', 0)
    
    async def generate_reports(self, results: Dict[str, Any]):
        """Generate comprehensive test reports."""
        print("📊 Generating Test Reports...")
        
        # Convert results to TestSuiteResult format for each suite
        for suite_name, suite_data in results['test_suites'].items():
            if 'test_results' in suite_data:
                # Convert to TestResult objects
                test_results = []
                for test_data in suite_data['test_results']:
                    test_result = TestResult(
                        test_name=test_data['test_name'],
                        status=test_data['status'],
                        execution_time=test_data['execution_time'],
                        start_time=test_data['start_time'],
                        end_time=test_data['end_time'],
                        error_message=test_data.get('error'),
                        metrics=test_data.get('metrics'),
                        environment=test_data.get('environment'),
                        test_type=test_data.get('test_type')
                    )
                    test_results.append(test_result)
                
                # Create TestSuiteResult
                suite_result = TestSuiteResult(
                    suite_name=suite_name,
                    start_time=suite_data['start_time'],
                    end_time=suite_data['end_time'],
                    total_execution_time=suite_data['total_execution_time'],
                    test_results=test_results,
                    summary=suite_data['summary']
                )
                
                # Generate reports
                await self.reporting_pipeline.process_test_results(
                    suite_result,
                    self.test_config['reporting']['output_dir']
                )
        
        # Generate overall summary report
        summary_file = Path(self.test_config['reporting']['output_dir']) / 'overall_summary.json'
        summary_file.parent.mkdir(exist_ok=True)
        
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Reports generated in: {self.test_config['reporting']['output_dir']}")
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test execution summary."""
        print("\n" + "=" * 60)
        print("🏁 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        summary = results['summary']
        
        print(f"📊 Overall Results:")
        print(f"   Total Test Suites: {summary['total_suites']}")
        print(f"   Passed Suites: {summary['passed_suites']}")
        print(f"   Failed Suites: {summary['failed_suites']}")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed Tests: {summary['passed_tests']}")
        print(f"   Failed Tests: {summary['failed_tests']}")
        
        if summary['total_tests'] > 0:
            success_rate = summary['passed_tests'] / summary['total_tests']
            print(f"   Success Rate: {success_rate:.1%}")
        
        print(f"\n⏱️  Execution Time:")
        start_time = datetime.fromisoformat(results['start_time'])
        end_time = datetime.fromisoformat(results['end_time'])
        duration = end_time - start_time
        print(f"   Duration: {duration.total_seconds():.2f} seconds")
        
        # Suite-specific results
        print(f"\n📋 Suite Results:")
        for suite_name, suite_data in results['test_suites'].items():
            suite_summary = suite_data.get('summary', {})
            status = "✅ PASSED" if suite_summary.get('failed', 0) == 0 else "❌ FAILED"
            print(f"   {suite_name}: {status} ({suite_summary.get('passed', 0)}/{suite_summary.get('total_tests', 0)} tests passed)")
        
        # Overall status
        overall_status = "✅ ALL TESTS PASSED" if summary['failed_tests'] == 0 else "❌ SOME TESTS FAILED"
        print(f"\n🎯 Overall Status: {overall_status}")
        print("=" * 60)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description='Auto-Deployment Integration Test Runner')
    parser.add_argument('--config', '-c', help='Test configuration file (JSON or YAML)')
    parser.add_argument('--suite', '-s', choices=['integration', 'performance', 'e2e', 'all'], 
                       default='all', help='Test suite to run')
    parser.add_argument('--output', '-o', default='test_reports', help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = IntegrationTestRunner(args.config)
    
    # Override output directory if specified
    if args.output:
        runner.test_config['reporting']['output_dir'] = args.output
    
    # Configure test suites based on selection
    if args.suite != 'all':
        for suite_name in runner.test_config['test_suites']:
            runner.test_config['test_suites'][suite_name]['enabled'] = (suite_name == args.suite)
    
    # Run tests
    try:
        results = asyncio.run(runner.run_all_tests())
        
        # Exit with appropriate code
        if results['summary']['failed_tests'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()