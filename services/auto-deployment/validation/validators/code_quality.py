"""
Code quality validator for pre-deployment checks.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class CodeQualityValidator(BaseValidator):
    """Validator for code quality metrics including test coverage, linting, and type checking."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.min_test_coverage = self.config.get('min_test_coverage', 0.8)
        self.run_linting = self.config.get('run_linting', True)
        self.run_type_checking = self.config.get('run_type_checking', True)
        self.project_root = Path(self.config.get('project_root', '.'))
        self.exclude_patterns = self.config.get('exclude_patterns', [
            '*/tests/*', '*/test_*', '*/__pycache__/*', '*/node_modules/*'
        ])
    
    @property
    def description(self) -> str:
        return "Validates code quality through test coverage, linting, and type checking"
    
    async def validate(self) -> ValidationResult:
        """Run code quality validation checks."""
        try:
            issues = []
            details = {}
            
            # Check test coverage
            coverage_result = await self._check_test_coverage()
            if coverage_result:
                issues.extend(coverage_result.get('issues', []))
                details['coverage'] = coverage_result
            
            # Run linting if enabled
            if self.run_linting:
                linting_result = await self._run_linting()
                if linting_result:
                    issues.extend(linting_result.get('issues', []))
                    details['linting'] = linting_result
            
            # Run type checking if enabled
            if self.run_type_checking:
                type_check_result = await self._run_type_checking()
                if type_check_result:
                    issues.extend(type_check_result.get('issues', []))
                    details['type_checking'] = type_check_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    "All code quality checks passed",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            error_issues = [i for i in issues if i.get('severity') == 'error']
            warning_issues = [i for i in issues if i.get('severity') == 'warning']
            
            if critical_issues:
                return self._critical(
                    f"Critical code quality issues found: {len(critical_issues)} critical, "
                    f"{len(error_issues)} errors, {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            elif error_issues:
                return self._error(
                    f"Code quality issues found: {len(error_issues)} errors, "
                    f"{len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            else:
                return self._warning(
                    f"Code quality warnings found: {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
                
        except Exception as e:
            logger.error(f"Code quality validation failed: {e}")
            return self._error(
                f"Code quality validation failed: {str(e)}",
                details={'error': str(e)},
                remediation_steps=[
                    "Check that all required tools are installed (pytest, coverage, flake8, mypy)",
                    "Ensure the project structure is correct",
                    "Review validator configuration"
                ]
            )
    
    async def _check_test_coverage(self) -> Optional[Dict[str, Any]]:
        """Check test coverage using coverage.py."""
        try:
            # Try to import coverage
            try:
                import coverage
            except ImportError:
                logger.warning("coverage not found, skipping coverage check")
                return {
                    'coverage_percentage': 0,
                    'issues': [{
                        'type': 'tool_missing',
                        'severity': 'warning',
                        'message': 'coverage not installed, skipping coverage checks'
                    }]
                }
            
            # Run coverage analysis
            cov = coverage.Coverage()
            cov.start()
            
            # Try to load existing coverage data
            try:
                cov.load()
            except coverage.CoverageException:
                # No existing coverage data, run tests
                result = subprocess.run([
                    'python', '-m', 'pytest', '--cov=.', '--cov-report=json'
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode != 0:
                    logger.warning(f"Test execution failed: {result.stderr}")
                    return {
                        'coverage_percentage': 0,
                        'issues': [{
                            'type': 'test_execution',
                            'severity': 'error',
                            'message': 'Test execution failed',
                            'details': result.stderr
                        }]
                    }
            
            cov.stop()
            cov.save()
            
            # Get coverage report
            total_coverage = cov.report(show_missing=False, skip_covered=False)
            
            issues = []
            if total_coverage < self.min_test_coverage * 100:
                issues.append({
                    'type': 'low_coverage',
                    'severity': 'error' if total_coverage < 0.5 * 100 else 'warning',
                    'message': f'Test coverage {total_coverage:.1f}% is below minimum {self.min_test_coverage * 100:.1f}%',
                    'current_coverage': total_coverage,
                    'required_coverage': self.min_test_coverage * 100
                })
            
            return {
                'coverage_percentage': total_coverage,
                'required_coverage': self.min_test_coverage * 100,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Coverage check failed: {e}")
            return {
                'coverage_percentage': 0,
                'issues': [{
                    'type': 'coverage_error',
                    'severity': 'error',
                    'message': f'Coverage analysis failed: {str(e)}'
                }]
            }
    
    async def _run_linting(self) -> Optional[Dict[str, Any]]:
        """Run code linting using flake8."""
        try:
            # Run flake8
            result = subprocess.run([
                'python', '-m', 'flake8', '--format=json', str(self.project_root)
            ], capture_output=True, text=True)
            
            issues = []
            
            if result.returncode != 0:
                try:
                    # Parse flake8 JSON output
                    flake8_output = json.loads(result.stdout) if result.stdout else []
                    
                    for issue in flake8_output:
                        severity = self._get_flake8_severity(issue.get('code', ''))
                        issues.append({
                            'type': 'linting',
                            'severity': severity,
                            'message': issue.get('text', ''),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'column': issue.get('column_number', 0),
                            'code': issue.get('code', '')
                        })
                        
                except json.JSONDecodeError:
                    # Fallback to parsing text output
                    if result.stdout:
                        issues.append({
                            'type': 'linting',
                            'severity': 'warning',
                            'message': 'Linting issues found (unable to parse details)',
                            'details': result.stdout
                        })
            
            return {
                'total_issues': len(issues),
                'issues': issues
            }
            
        except FileNotFoundError:
            logger.warning("flake8 not found, skipping linting")
            return {
                'total_issues': 0,
                'issues': [{
                    'type': 'tool_missing',
                    'severity': 'warning',
                    'message': 'flake8 not installed, skipping linting checks'
                }]
            }
        except Exception as e:
            logger.error(f"Linting failed: {e}")
            return {
                'total_issues': 1,
                'issues': [{
                    'type': 'linting_error',
                    'severity': 'error',
                    'message': f'Linting failed: {str(e)}'
                }]
            }
    
    async def _run_type_checking(self) -> Optional[Dict[str, Any]]:
        """Run type checking using mypy."""
        try:
            # Run mypy
            result = subprocess.run([
                'python', '-m', 'mypy', '--json-report', '/tmp/mypy-report', 
                str(self.project_root)
            ], capture_output=True, text=True)
            
            issues = []
            
            if result.returncode != 0:
                # Parse mypy output
                for line in result.stdout.split('\n'):
                    if line.strip() and ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            file_path, line_num, col_num, message = parts
                            severity = self._get_mypy_severity(message)
                            issues.append({
                                'type': 'type_checking',
                                'severity': severity,
                                'message': message.strip(),
                                'file': file_path.strip(),
                                'line': int(line_num) if line_num.isdigit() else 0,
                                'column': int(col_num) if col_num.isdigit() else 0
                            })
            
            return {
                'total_issues': len(issues),
                'issues': issues
            }
            
        except FileNotFoundError:
            logger.warning("mypy not found, skipping type checking")
            return {
                'total_issues': 0,
                'issues': [{
                    'type': 'tool_missing',
                    'severity': 'warning',
                    'message': 'mypy not installed, skipping type checking'
                }]
            }
        except Exception as e:
            logger.error(f"Type checking failed: {e}")
            return {
                'total_issues': 1,
                'issues': [{
                    'type': 'type_checking_error',
                    'severity': 'error',
                    'message': f'Type checking failed: {str(e)}'
                }]
            }
    
    def _get_flake8_severity(self, code: str) -> str:
        """Determine severity based on flake8 error code."""
        if code.startswith('E9') or code.startswith('F'):  # Syntax errors, undefined names
            return 'error'
        elif code.startswith('E1') or code.startswith('E2'):  # Indentation, whitespace
            return 'warning'
        elif code.startswith('W'):  # Warnings
            return 'warning'
        else:
            return 'warning'
    
    def _get_mypy_severity(self, message: str) -> str:
        """Determine severity based on mypy message."""
        message_lower = message.lower()
        if 'error' in message_lower:
            return 'error'
        elif 'note' in message_lower:
            return 'warning'
        else:
            return 'warning'
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate remediation steps based on issues found."""
        steps = []
        
        # Coverage issues
        coverage_issues = [i for i in issues if i.get('type') == 'low_coverage']
        if coverage_issues:
            steps.append("Increase test coverage by writing more unit tests")
            steps.append("Focus on testing critical business logic and edge cases")
        
        # Linting issues
        linting_issues = [i for i in issues if i.get('type') == 'linting']
        if linting_issues:
            steps.append("Fix linting issues by running: python -m flake8 --show-source")
            steps.append("Consider using an auto-formatter like black or autopep8")
        
        # Type checking issues
        type_issues = [i for i in issues if i.get('type') == 'type_checking']
        if type_issues:
            steps.append("Fix type checking issues by adding proper type annotations")
            steps.append("Run: python -m mypy . to see detailed type errors")
        
        # Tool missing issues
        missing_tools = [i for i in issues if i.get('type') == 'tool_missing']
        if missing_tools:
            steps.append("Install missing development tools: pip install flake8 mypy pytest coverage")
        
        if not steps:
            steps.append("Review code quality configuration and ensure all tools are properly set up")
        
        return steps