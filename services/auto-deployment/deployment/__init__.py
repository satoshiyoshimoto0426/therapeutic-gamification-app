"""
Auto-deployment deployment engine module.
"""

from .strategies.base import DeploymentStrategy, DeploymentResult
from .strategies.blue_green import BlueGreenDeploymentStrategy
from .strategies.rolling_update import RollingUpdateDeploymentStrategy
from .github_actions.github_client import GitHubClient
from .github_actions.workflow_trigger import WorkflowTrigger
from .github_actions.workflow_monitor import WorkflowMonitor
from .github_actions.parameter_manager import ParameterManager

__all__ = [
    'DeploymentStrategy',
    'DeploymentResult',
    'BlueGreenDeploymentStrategy',
    'RollingUpdateDeploymentStrategy',
    'GitHubClient',
    'WorkflowTrigger',
    'WorkflowMonitor',
    'ParameterManager'
]