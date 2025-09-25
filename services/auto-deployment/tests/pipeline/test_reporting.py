"""
Test reporting and metrics collection for automated testing pipeline.

Provides comprehensive reporting, metrics collection, and analysis
for automated test execution results.
"""

import pytest
import asyncio
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from unittest.mock import Mock, patch, AsyncMock
import statistics


@dataclass
class TestResult:
    """Data class for individual test results."""
    test_name: str
    status: str  # 'passed', 'failed', 'skipped'
    execution_time: float
    start_time: str
    end_time: str
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    test_type: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Data class for test suite results."""
    suite_name: str
    start_time: str
    end_time: str
    total_execution_time: float
    test_results: List[TestResult]
    summary: Dict[str, int]
    environment_info: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None


class TestMetricsCollector:
    """Collects and analyzes test execution metrics."""
    
    def __init__(self):
        self.metrics_history = []
        self.performance_baselines = {}
    
    def collect_test_metrics(self, test_result: TestResult) -> Dict[str, Any]:
        """Collect metrics from a single test result."""
        metrics = {
            'test_name': test_result.test_name,
            'execution_time': test_result.execution_time,
            'status': test_result.status,
            'timestamp': test_result.start_time,
            'environment': test_result.environment,
            'test_type': test_result.test_type
        }
        
        # Add custom metrics if available
        if test_result.metrics:
            metrics.update(test_result.metrics)
        
        # Calculate performance metrics
        if test_result.test_type == 'performance_load':
            metrics.update(self._calculate_performance_metrics(test_result))
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _calculate_performance_metrics(self, test_result: TestResult) -> Dict[str, Any]:
        """Calculate performance-specific metrics."""
        performance_metrics = {}
        
        if test_result.metrics:
            # Throughput metrics
            if 'successful_deployments' in test_result.metrics and 'execution_time' in test_result.metrics:
                throughput = test_result.metrics['successful_deployments'] / test_result.metrics['execution_time']
                performance_metrics['throughput'] = throughput
            
            # Success rate metrics
            if 'successful_deployments' in test_result.metrics and 'total_deployments' in test_result.metrics:
                success_rate = test_result.metrics['successful_deployments'] / test_result.metrics['total_deployments']
                performance_metrics['success_rate'] = success_rate
            
            # Response time metrics
            if 'response_times' in test_result.metrics:
                response_times = test_result.metrics['response_times']
                performance_metrics.update({
                    'avg_response_time': statistics.mean(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'p99_response_time': self._calculate_percentile(response_times, 99)
                })
        
        return performance_metrics
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value from a list of numbers."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def collect_suite_metrics(self, suite_result: TestSuiteResult) -> Dict[str, Any]:
        """Collect metrics from a test suite result."""
        suite_metrics = {
            'suite_name': suite_result.suite_name,
            'total_execution_time': suite_result.total_execution_time,
            'total_tests': suite_result.summary['total_tests'],
            'passed_tests': suite_result.summary['passed'],
            'failed_tests': suite_result.summary['failed'],
            'skipped_tests': suite_result.summary['skipped'],
            'success_rate': suite_result.summary['passed'] / suite_result.summary['total_tests'] if suite_result.summary['total_tests'] > 0 else 0,
            'timestamp': suite_result.start_time
        }
        
        # Calculate test execution time statistics
        execution_times = [test.execution_time for test in suite_result.test_results]
        if execution_times:
            suite_metrics.update({
                'avg_test_execution_time': statistics.mean(execution_times),
                'median_test_execution_time': statistics.median(execution_times),
                'max_test_execution_time': max(execution_times),
                'min_test_execution_time': min(execution_times)
            })
        
        # Calculate test type distribution
        test_types = {}
        for test in suite_result.test_results:
            test_type = test.test_type or 'unknown'
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        suite_metrics['test_type_distribution'] = test_types
        
        return suite_metrics
    
    def analyze_trends(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze trends in test metrics over a specified time window."""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Filter metrics within time window
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available in specified time window'}
        
        # Calculate trend analysis
        trends = {
            'time_window_hours': time_window_hours,
            'total_tests': len(recent_metrics),
            'success_rate_trend': self._calculate_success_rate_trend(recent_metrics),
            'performance_trend': self._calculate_performance_trend(recent_metrics),
            'failure_analysis': self._analyze_failures(recent_metrics)
        }
        
        return trends
    
    def _calculate_success_rate_trend(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate success rate trends."""
        passed_tests = sum(1 for m in metrics if m['status'] == 'passed')
        total_tests = len(metrics)
        
        return {
            'current_success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_tests_analyzed': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests
        }
    
    def _calculate_performance_trend(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance trends."""
        execution_times = [m['execution_time'] for m in metrics if 'execution_time' in m]
        
        if not execution_times:
            return {'error': 'No execution time data available'}
        
        return {
            'avg_execution_time': statistics.mean(execution_times),
            'median_execution_time': statistics.median(execution_times),
            'execution_time_trend': 'stable'  # Could implement more sophisticated trend analysis
        }
    
    def _analyze_failures(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failure patterns."""
        failed_tests = [m for m in metrics if m['status'] == 'failed']
        
        if not failed_tests:
            return {'total_failures': 0}
        
        # Group failures by test type
        failure_by_type = {}
        for test in failed_tests:
            test_type = test.get('test_type', 'unknown')
            failure_by_type[test_type] = failure_by_type.get(test_type, 0) + 1
        
        return {
            'total_failures': len(failed_tests),
            'failure_by_type': failure_by_type,
            'failure_rate': len(failed_tests) / len(metrics) if metrics else 0
        }


class TestReportGenerator:
    """Generates comprehensive test reports in various formats."""
    
    def __init__(self, metrics_collector: TestMetricsCollector):
        self.metrics_collector = metrics_collector
        self.report_templates = {}
    
    def generate_html_report(self, suite_result: TestSuiteResult, output_file: str) -> str:
        """Generate an HTML test report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report - {suite_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .test-results {{ margin: 20px 0; }}
                .test-passed {{ color: green; }}
                .test-failed {{ color: red; }}
                .test-skipped {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metrics {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Test Report: {suite_name}</h1>
                <p>Generated: {generated_time}</p>
                <p>Execution Time: {total_execution_time:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p class="test-passed">Passed: {passed_tests}</p>
                <p class="test-failed">Failed: {failed_tests}</p>
                <p class="test-skipped">Skipped: {skipped_tests}</p>
                <p>Success Rate: {success_rate:.1%}</p>
            </div>
            
            <div class="test-results">
                <h2>Test Results</h2>
                <table>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Execution Time</th>
                        <th>Environment</th>
                        <th>Error Message</th>
                    </tr>
                    {test_rows}
                </table>
            </div>
            
            <div class="metrics">
                <h2>Metrics</h2>
                {metrics_content}
            </div>
        </body>
        </html>
        """
        
        # Generate test result rows
        test_rows = ""
        for test in suite_result.test_results:
            status_class = f"test-{test.status}"
            error_msg = test.error_message or ""
            test_rows += f"""
                <tr>
                    <td>{test.test_name}</td>
                    <td class="{status_class}">{test.status.upper()}</td>
                    <td>{test.execution_time:.2f}s</td>
                    <td>{test.environment or 'N/A'}</td>
                    <td>{error_msg}</td>
                </tr>
            """
        
        # Generate metrics content
        suite_metrics = self.metrics_collector.collect_suite_metrics(suite_result)
        metrics_content = "<ul>"
        for key, value in suite_metrics.items():
            if key not in ['suite_name', 'timestamp']:
                metrics_content += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        metrics_content += "</ul>"
        
        # Fill template
        html_content = html_template.format(
            suite_name=suite_result.suite_name,
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_execution_time=suite_result.total_execution_time,
            total_tests=suite_result.summary['total_tests'],
            passed_tests=suite_result.summary['passed'],
            failed_tests=suite_result.summary['failed'],
            skipped_tests=suite_result.summary['skipped'],
            success_rate=suite_result.summary['passed'] / suite_result.summary['total_tests'] if suite_result.summary['total_tests'] > 0 else 0,
            test_rows=test_rows,
            metrics_content=metrics_content
        )
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def generate_json_report(self, suite_result: TestSuiteResult, output_file: str) -> str:
        """Generate a JSON test report."""
        report_data = {
            'suite_name': suite_result.suite_name,
            'generated_time': datetime.now().isoformat(),
            'execution_summary': {
                'start_time': suite_result.start_time,
                'end_time': suite_result.end_time,
                'total_execution_time': suite_result.total_execution_time
            },
            'test_summary': suite_result.summary,
            'test_results': [asdict(test) for test in suite_result.test_results],
            'metrics': self.metrics_collector.collect_suite_metrics(suite_result),
            'environment_info': suite_result.environment_info,
            'configuration': suite_result.configuration
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_file
    
    def generate_csv_report(self, suite_result: TestSuiteResult, output_file: str) -> str:
        """Generate a CSV test report."""
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'test_name', 'status', 'execution_time', 'start_time', 'end_time',
                'environment', 'test_type', 'error_message'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for test in suite_result.test_results:
                writer.writerow({
                    'test_name': test.test_name,
                    'status': test.status,
                    'execution_time': test.execution_time,
                    'start_time': test.start_time,
                    'end_time': test.end_time,
                    'environment': test.environment or '',
                    'test_type': test.test_type or '',
                    'error_message': test.error_message or ''
                })
        
        return output_file
    
    def generate_trend_report(self, time_window_hours: int = 24, output_file: str = None) -> Dict[str, Any]:
        """Generate a trend analysis report."""
        trends = self.metrics_collector.analyze_trends(time_window_hours)
        
        report = {
            'generated_time': datetime.now().isoformat(),
            'analysis_period': f"Last {time_window_hours} hours",
            'trends': trends,
            'recommendations': self._generate_recommendations(trends)
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        # Success rate recommendations
        if 'success_rate_trend' in trends:
            success_rate = trends['success_rate_trend'].get('current_success_rate', 0)
            if success_rate < 0.8:
                recommendations.append("Success rate is below 80%. Consider reviewing failed tests and improving test stability.")
            elif success_rate < 0.9:
                recommendations.append("Success rate is below 90%. Monitor for potential issues.")
        
        # Performance recommendations
        if 'performance_trend' in trends:
            avg_time = trends['performance_trend'].get('avg_execution_time', 0)
            if avg_time > 300:  # 5 minutes
                recommendations.append("Average test execution time is high. Consider optimizing test performance.")
        
        # Failure analysis recommendations
        if 'failure_analysis' in trends:
            failure_rate = trends['failure_analysis'].get('failure_rate', 0)
            if failure_rate > 0.2:
                recommendations.append("High failure rate detected. Investigate common failure patterns.")
        
        if not recommendations:
            recommendations.append("Test metrics look healthy. Continue monitoring.")
        
        return recommendations


class TestReportingPipeline:
    """Main pipeline for test reporting and metrics collection."""
    
    def __init__(self):
        self.metrics_collector = TestMetricsCollector()
        self.report_generator = TestReportGenerator(self.metrics_collector)
        self.report_history = []
    
    async def process_test_results(self, suite_result: TestSuiteResult, output_dir: str = "test_reports") -> Dict[str, str]:
        """Process test results and generate comprehensive reports."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate timestamp for file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suite_name_clean = suite_result.suite_name.replace(' ', '_').lower()
        
        # Collect metrics for all tests
        for test_result in suite_result.test_results:
            self.metrics_collector.collect_test_metrics(test_result)
        
        # Generate reports in different formats
        reports = {}
        
        # HTML Report
        html_file = output_path / f"{suite_name_clean}_{timestamp}.html"
        reports['html'] = self.report_generator.generate_html_report(suite_result, str(html_file))
        
        # JSON Report
        json_file = output_path / f"{suite_name_clean}_{timestamp}.json"
        reports['json'] = self.report_generator.generate_json_report(suite_result, str(json_file))
        
        # CSV Report
        csv_file = output_path / f"{suite_name_clean}_{timestamp}.csv"
        reports['csv'] = self.report_generator.generate_csv_report(suite_result, str(csv_file))
        
        # Trend Report (if enough historical data)
        if len(self.metrics_collector.metrics_history) > 10:
            trend_file = output_path / f"trend_analysis_{timestamp}.json"
            trend_report = self.report_generator.generate_trend_report(24, str(trend_file))
            reports['trend'] = str(trend_file)
        
        # Store report metadata
        report_metadata = {
            'suite_name': suite_result.suite_name,
            'timestamp': timestamp,
            'reports': reports,
            'summary': suite_result.summary
        }
        
        self.report_history.append(report_metadata)
        
        return reports
    
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for a test dashboard."""
        if not self.report_history:
            return {'error': 'No test data available'}
        
        # Get recent test data
        recent_reports = self.report_history[-10:]  # Last 10 test runs
        
        dashboard_data = {
            'last_updated': datetime.now().isoformat(),
            'recent_test_runs': len(recent_reports),
            'overall_metrics': self._calculate_overall_metrics(recent_reports),
            'test_history': [
                {
                    'suite_name': report['suite_name'],
                    'timestamp': report['timestamp'],
                    'summary': report['summary']
                }
                for report in recent_reports
            ],
            'trends': self.metrics_collector.analyze_trends(168)  # Last week
        }
        
        return dashboard_data
    
    def _calculate_overall_metrics(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall metrics across multiple test runs."""
        if not reports:
            return {}
        
        total_tests = sum(report['summary']['total_tests'] for report in reports)
        total_passed = sum(report['summary']['passed'] for report in reports)
        total_failed = sum(report['summary']['failed'] for report in reports)
        
        return {
            'total_test_runs': len(reports),
            'total_tests_executed': total_tests,
            'overall_success_rate': total_passed / total_tests if total_tests > 0 else 0,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'avg_tests_per_run': total_tests / len(reports) if reports else 0
        }
    
    async def cleanup_old_reports(self, retention_days: int = 30, report_dir: str = "test_reports"):
        """Clean up old test reports based on retention policy."""
        report_path = Path(report_dir)
        if not report_path.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for file_path in report_path.glob("*"):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    print(f"Deleted old report: {file_path}")


# Test cases for the reporting system
class TestReportingTests:
    """Test cases for the test reporting system."""
    
    @pytest.fixture
    def sample_test_results(self):
        """Create sample test results for testing."""
        return [
            TestResult(
                test_name="test_basic_deployment",
                status="passed",
                execution_time=5.2,
                start_time="2024-01-01T10:00:00",
                end_time="2024-01-01T10:00:05",
                environment="testing",
                test_type="basic_deployment"
            ),
            TestResult(
                test_name="test_failure_recovery",
                status="failed",
                execution_time=12.8,
                start_time="2024-01-01T10:00:10",
                end_time="2024-01-01T10:00:23",
                error_message="Network timeout",
                environment="testing",
                test_type="failure_recovery"
            ),
            TestResult(
                test_name="test_performance_load",
                status="passed",
                execution_time=30.5,
                start_time="2024-01-01T10:00:30",
                end_time="2024-01-01T10:01:00",
                environment="testing",
                test_type="performance_load",
                metrics={
                    'successful_deployments': 50,
                    'total_deployments': 50,
                    'execution_time': 30.5,
                    'response_times': [0.1, 0.2, 0.15, 0.3, 0.25]
                }
            )
        ]
    
    @pytest.fixture
    def sample_suite_result(self, sample_test_results):
        """Create a sample test suite result."""
        return TestSuiteResult(
            suite_name="automated_test_suite",
            start_time="2024-01-01T10:00:00",
            end_time="2024-01-01T10:01:30",
            total_execution_time=90.0,
            test_results=sample_test_results,
            summary={
                'total_tests': 3,
                'passed': 2,
                'failed': 1,
                'skipped': 0
            }
        )
    
    def test_metrics_collector(self, sample_test_results):
        """Test metrics collection functionality."""
        collector = TestMetricsCollector()
        
        # Test individual test metrics collection
        for test_result in sample_test_results:
            metrics = collector.collect_test_metrics(test_result)
            assert metrics['test_name'] == test_result.test_name
            assert metrics['status'] == test_result.status
            assert metrics['execution_time'] == test_result.execution_time
        
        # Test performance metrics calculation
        perf_test = sample_test_results[2]  # Performance test
        perf_metrics = collector.collect_test_metrics(perf_test)
        assert 'throughput' in perf_metrics
        assert 'success_rate' in perf_metrics
        assert 'avg_response_time' in perf_metrics
    
    def test_report_generation(self, sample_suite_result):
        """Test report generation in different formats."""
        collector = TestMetricsCollector()
        generator = TestReportGenerator(collector)
        
        # Test HTML report generation
        html_file = "test_report.html"
        result = generator.generate_html_report(sample_suite_result, html_file)
        assert result == html_file
        assert Path(html_file).exists()
        
        # Test JSON report generation
        json_file = "test_report.json"
        result = generator.generate_json_report(sample_suite_result, json_file)
        assert result == json_file
        assert Path(json_file).exists()
        
        # Test CSV report generation
        csv_file = "test_report.csv"
        result = generator.generate_csv_report(sample_suite_result, csv_file)
        assert result == csv_file
        assert Path(csv_file).exists()
        
        # Clean up
        for file in [html_file, json_file, csv_file]:
            if Path(file).exists():
                Path(file).unlink()
    
    @pytest.mark.asyncio
    async def test_reporting_pipeline(self, sample_suite_result):
        """Test the complete reporting pipeline."""
        pipeline = TestReportingPipeline()
        
        # Process test results
        reports = await pipeline.process_test_results(sample_suite_result, "test_output")
        
        # Verify reports were generated
        assert 'html' in reports
        assert 'json' in reports
        assert 'csv' in reports
        
        # Verify files exist
        for report_file in reports.values():
            assert Path(report_file).exists()
        
        # Test dashboard data generation
        dashboard_data = await pipeline.generate_dashboard_data()
        assert 'recent_test_runs' in dashboard_data
        assert 'overall_metrics' in dashboard_data
        
        # Clean up
        import shutil
        if Path("test_output").exists():
            shutil.rmtree("test_output")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])