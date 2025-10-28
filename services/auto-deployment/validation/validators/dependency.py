"""
Dependency validator for pre-deployment checks.
"""

import subprocess
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple

import sys
import os

# Add validation directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
validation_dir = os.path.dirname(current_dir)
if validation_dir not in sys.path:
    sys.path.insert(0, validation_dir)

from base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class DependencyValidator(BaseValidator):
    """Validator for dependency compatibility and management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.check_compatibility = self.config.get('check_compatibility', True)
        self.check_outdated = self.config.get('check_outdated', True)
        self.check_conflicts = self.config.get('check_conflicts', True)
        self.project_root = Path(self.config.get('project_root', '.'))
        self.requirements_files = self.config.get('requirements_files', [
            'requirements.txt', 'requirements-dev.txt', 'pyproject.toml'
        ])
        self.allowed_outdated_days = self.config.get('allowed_outdated_days', 90)
    
    @property
    def description(self) -> str:
        return "Validates dependency compatibility, conflicts, and security"
    
    async def validate(self) -> ValidationResult:
        """Run dependency validation checks."""
        try:
            issues = []
            details = {}
            
            # Check for dependency conflicts
            if self.check_conflicts:
                conflict_result = await self._check_dependency_conflicts()
                if conflict_result:
                    issues.extend(conflict_result.get('issues', []))
                    details['conflicts'] = conflict_result
            
            # Check for compatibility issues
            if self.check_compatibility:
                compat_result = await self._check_compatibility()
                if compat_result:
                    issues.extend(compat_result.get('issues', []))
                    details['compatibility'] = compat_result
            
            # Check for outdated dependencies
            if self.check_outdated:
                outdated_result = await self._check_outdated_dependencies()
                if outdated_result:
                    issues.extend(outdated_result.get('issues', []))
                    details['outdated'] = outdated_result
            
            # Check requirements file consistency
            consistency_result = await self._check_requirements_consistency()
            if consistency_result:
                issues.extend(consistency_result.get('issues', []))
                details['consistency'] = consistency_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    "All dependency checks passed",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            error_issues = [i for i in issues if i.get('severity') == 'error']
            warning_issues = [i for i in issues if i.get('severity') == 'warning']
            
            if critical_issues:
                return self._critical(
                    f"Critical dependency issues found: {len(critical_issues)} critical, "
                    f"{len(error_issues)} errors, {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            elif error_issues:
                return self._error(
                    f"Dependency issues found: {len(error_issues)} errors, "
                    f"{len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            else:
                return self._warning(
                    f"Dependency warnings found: {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
                
        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            return self._error(
                f"Dependency validation failed: {str(e)}",
                details={'error': str(e)},
                remediation_steps=[
                    "Check that pip and packaging tools are installed",
                    "Ensure requirements files are properly formatted",
                    "Review validator configuration"
                ]
            )
    
    async def _check_dependency_conflicts(self) -> Optional[Dict[str, Any]]:
        """Check for dependency conflicts using pip-check."""
        try:
            # Run pip check to find conflicts
            result = subprocess.run([
                'python', '-m', 'pip', 'check'
            ], capture_output=True, text=True)
            
            issues = []
            
            if result.returncode != 0 and result.stdout:
                # Parse pip check output
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # Parse conflict information
                        conflict_match = re.match(
                            r'(\S+) \S+ has requirement (\S+) ([<>=!]+) (\S+), but you have (\S+) (\S+)',
                            line
                        )
                        if conflict_match:
                            package, dep_name, operator, required_version, current_name, current_version = conflict_match.groups()
                            issues.append({
                                'type': 'dependency_conflict',
                                'severity': 'error',
                                'message': f'Dependency conflict: {package} requires {dep_name} {operator} {required_version}, but {current_name} {current_version} is installed',
                                'package': package,
                                'dependency': dep_name,
                                'required_version': f'{operator} {required_version}',
                                'current_version': current_version
                            })
                        else:
                            # Generic conflict
                            issues.append({
                                'type': 'dependency_conflict',
                                'severity': 'error',
                                'message': f'Dependency conflict: {line.strip()}',
                                'details': line.strip()
                            })
            
            return {
                'total_conflicts': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Dependency conflict check failed: {e}")
            return {
                'total_conflicts': 1,
                'issues': [{
                    'type': 'conflict_check_error',
                    'severity': 'error',
                    'message': f'Dependency conflict check failed: {str(e)}'
                }]
            }
    
    async def _check_compatibility(self) -> Optional[Dict[str, Any]]:
        """Check Python version compatibility."""
        try:
            issues = []
            
            # Get current Python version
            import sys
            current_python = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            # Check pyproject.toml for Python version requirements
            pyproject_path = self.project_root / 'pyproject.toml'
            if pyproject_path.exists():
                try:
                    import tomli
                    with open(pyproject_path, 'rb') as f:
                        pyproject_data = tomli.load(f)
                    
                    python_requires = pyproject_data.get('project', {}).get('requires-python')
                    if python_requires:
                        if not self._check_python_version_compatibility(current_python, python_requires):
                            issues.append({
                                'type': 'python_version_incompatible',
                                'severity': 'error',
                                'message': f'Current Python version {current_python} does not satisfy requirement {python_requires}',
                                'current_version': current_python,
                                'required_version': python_requires
                            })
                            
                except ImportError:
                    logger.warning("tomli not available, skipping pyproject.toml parsing")
                except Exception as e:
                    logger.warning(f"Could not parse pyproject.toml: {e}")
            
            # Check installed packages for compatibility
            try:
                import pkg_resources
                installed_packages = list(pkg_resources.working_set)
                for package in installed_packages:
                    if hasattr(package, 'requires'):
                        for req in package.requires():
                            try:
                                pkg_resources.get_distribution(req)
                            except pkg_resources.DistributionNotFound:
                                issues.append({
                                    'type': 'missing_dependency',
                                    'severity': 'error',
                                    'message': f'Missing dependency: {package.project_name} requires {req}',
                                    'package': package.project_name,
                                    'missing_dependency': str(req)
                                })
                            except pkg_resources.VersionConflict as e:
                                issues.append({
                                    'type': 'version_conflict',
                                    'severity': 'error',
                                    'message': f'Version conflict: {str(e)}',
                                    'package': package.project_name,
                                    'conflict_details': str(e)
                                })
                                
            except ImportError:
                logger.warning("pkg_resources not available, skipping installed package check")
            except Exception as e:
                logger.warning(f"Could not check installed packages: {e}")
            
            return {
                'python_version': current_python,
                'total_issues': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Compatibility check failed: {e}")
            return {
                'total_issues': 1,
                'issues': [{
                    'type': 'compatibility_check_error',
                    'severity': 'error',
                    'message': f'Compatibility check failed: {str(e)}'
                }]
            }
    
    async def _check_outdated_dependencies(self) -> Optional[Dict[str, Any]]:
        """Check for outdated dependencies."""
        try:
            # Run pip list --outdated
            result = subprocess.run([
                'python', '-m', 'pip', 'list', '--outdated', '--format=json'
            ], capture_output=True, text=True)
            
            issues = []
            outdated_packages = []
            
            if result.returncode == 0 and result.stdout:
                try:
                    outdated_data = json.loads(result.stdout)
                    
                    for package in outdated_data:
                        package_name = package.get('name', '')
                        current_version = package.get('version', '')
                        latest_version = package.get('latest_version', '')
                        
                        outdated_packages.append({
                            'name': package_name,
                            'current_version': current_version,
                            'latest_version': latest_version
                        })
                        
                        # Determine severity based on version difference
                        severity = self._get_outdated_severity(current_version, latest_version)
                        
                        issues.append({
                            'type': 'outdated_dependency',
                            'severity': severity,
                            'message': f'Outdated dependency: {package_name} {current_version} (latest: {latest_version})',
                            'package': package_name,
                            'current_version': current_version,
                            'latest_version': latest_version
                        })
                        
                except json.JSONDecodeError:
                    logger.warning("Could not parse pip list output")
            
            return {
                'total_outdated': len(outdated_packages),
                'outdated_packages': outdated_packages,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Outdated dependency check failed: {e}")
            return {
                'total_outdated': 0,
                'issues': [{
                    'type': 'outdated_check_error',
                    'severity': 'error',
                    'message': f'Outdated dependency check failed: {str(e)}'
                }]
            }
    
    async def _check_requirements_consistency(self) -> Optional[Dict[str, Any]]:
        """Check consistency between requirements files."""
        try:
            issues = []
            requirements_data = {}
            
            # Parse all requirements files
            for req_file in self.requirements_files:
                req_path = self.project_root / req_file
                if req_path.exists():
                    try:
                        if req_file.endswith('.toml'):
                            requirements_data[req_file] = self._parse_pyproject_toml(req_path)
                        else:
                            requirements_data[req_file] = self._parse_requirements_txt(req_path)
                    except Exception as e:
                        issues.append({
                            'type': 'requirements_parse_error',
                            'severity': 'error',
                            'message': f'Could not parse {req_file}: {str(e)}',
                            'file': req_file
                        })
            
            # Check for inconsistencies between files
            if len(requirements_data) > 1:
                all_packages = set()
                for packages in requirements_data.values():
                    all_packages.update(packages.keys())
                
                for package in all_packages:
                    versions = {}
                    for file_name, packages in requirements_data.items():
                        if package in packages:
                            versions[file_name] = packages[package]
                    
                    if len(set(versions.values())) > 1:
                        issues.append({
                            'type': 'version_inconsistency',
                            'severity': 'warning',
                            'message': f'Inconsistent versions for {package}: {versions}',
                            'package': package,
                            'versions': versions
                        })
            
            return {
                'files_checked': list(requirements_data.keys()),
                'total_issues': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Requirements consistency check failed: {e}")
            return {
                'files_checked': [],
                'total_issues': 1,
                'issues': [{
                    'type': 'consistency_check_error',
                    'severity': 'error',
                    'message': f'Requirements consistency check failed: {str(e)}'
                }]
            }
    
    def _check_python_version_compatibility(self, current_version: str, required_version: str) -> bool:
        """Check if current Python version satisfies requirements."""
        try:
            from packaging.specifiers import SpecifierSet
            from packaging import version
            spec = SpecifierSet(required_version)
            return version.parse(current_version) in spec
        except ImportError:
            logger.warning("packaging not available, assuming Python version is compatible")
            return True
        except Exception:
            return True  # If we can't parse, assume compatible
    
    def _get_outdated_severity(self, current_version: str, latest_version: str) -> str:
        """Determine severity of outdated dependency."""
        try:
            from packaging import version
            current = version.parse(current_version)
            latest = version.parse(latest_version)
            
            # Major version difference
            if latest.major > current.major:
                return 'error'
            # Minor version difference
            elif latest.minor > current.minor:
                return 'warning'
            # Patch version difference
            else:
                return 'info'
                
        except ImportError:
            return 'warning'
        except Exception:
            return 'warning'
    
    def _parse_requirements_txt(self, file_path: Path) -> Dict[str, str]:
        """Parse requirements.txt file."""
        requirements = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Parse package==version or package>=version
                    match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!]+)(.+)$', line)
                    if match:
                        package, operator, version_spec = match.groups()
                        requirements[package] = f'{operator}{version_spec}'
                    else:
                        # Package without version
                        requirements[line] = ''
        
        return requirements
    
    def _parse_pyproject_toml(self, file_path: Path) -> Dict[str, str]:
        """Parse pyproject.toml file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                data = tomli.load(f)
            
            requirements = {}
            
            # Get dependencies from project section
            project_deps = data.get('project', {}).get('dependencies', [])
            for dep in project_deps:
                match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!]+)(.+)$', dep)
                if match:
                    package, operator, version_spec = match.groups()
                    requirements[package] = f'{operator}{version_spec}'
                else:
                    requirements[dep] = ''
            
            return requirements
            
        except ImportError:
            logger.warning("tomli not available for parsing pyproject.toml")
            return {}
        except Exception as e:
            logger.warning(f"Could not parse pyproject.toml: {e}")
            return {}
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate remediation steps based on issues found."""
        steps = []
        
        # Conflict issues
        conflict_issues = [i for i in issues if i.get('type') == 'dependency_conflict']
        if conflict_issues:
            steps.append("Resolve dependency conflicts by updating conflicting packages")
            steps.append("Use pip install --upgrade to update packages to compatible versions")
            steps.append("Consider using pip-tools to manage dependencies")
        
        # Compatibility issues
        compat_issues = [i for i in issues if i.get('type') in ['python_version_incompatible', 'missing_dependency', 'version_conflict']]
        if compat_issues:
            steps.append("Fix compatibility issues by updating Python version or dependencies")
            steps.append("Install missing dependencies: pip install <missing_package>")
        
        # Outdated issues
        outdated_issues = [i for i in issues if i.get('type') == 'outdated_dependency']
        if outdated_issues:
            steps.append("Update outdated dependencies: pip install --upgrade <package_name>")
            steps.append("Review changelog for breaking changes before updating major versions")
        
        # Consistency issues
        consistency_issues = [i for i in issues if i.get('type') == 'version_inconsistency']
        if consistency_issues:
            steps.append("Fix version inconsistencies between requirements files")
            steps.append("Ensure all requirements files specify the same versions for shared dependencies")
        
        if not steps:
            steps.append("Review dependency configuration and ensure all tools are properly set up")
        
        return steps