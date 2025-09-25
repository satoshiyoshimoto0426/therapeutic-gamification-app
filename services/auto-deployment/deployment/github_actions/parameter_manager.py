"""
GitHub Actions パラメータ管理システム

ワークフローに渡すパラメータの管理と検証を行います。
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

try:
    from services.auto_deployment.config import DeploymentConfig, Environment
    from services.auto_deployment.exceptions import DeploymentError, ValidationError
    from services.auto_deployment.logging_config import get_logger
except ImportError:
    # フォールバック用のクラス
    from enum import Enum
    from dataclasses import dataclass
    
    class Environment(Enum):
        DEVELOPMENT = "development"
        STAGING = "staging"
        PRODUCTION = "production"
    
    @dataclass
    class DeploymentConfig:
        environment: Environment
    
    class DeploymentError(Exception):
        pass
    
    class ValidationError(Exception):
        pass
    
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class ParameterType(Enum):
    """パラメータタイプ"""
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    CHOICE = "choice"
    ENVIRONMENT = "environment"


@dataclass
class ParameterDefinition:
    """パラメータ定義"""
    name: str
    type: ParameterType
    description: str
    required: bool = False
    default_value: Optional[Any] = None
    choices: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    pattern: Optional[str] = None


@dataclass
class WorkflowParameterSet:
    """ワークフローパラメータセット"""
    workflow_id: str
    parameters: Dict[str, ParameterDefinition] = field(default_factory=dict)
    environment_specific: Dict[Environment, Dict[str, Any]] = field(default_factory=dict)


class ParameterManager:
    """パラメータ管理"""
    
    def __init__(self, config: DeploymentConfig):
        """
        初期化
        
        Args:
            config: デプロイメント設定
        """
        self.config = config
        
        # パラメータ定義を初期化
        self.parameter_sets = self._initialize_parameter_definitions()
        
        logger.info("ParameterManager initialized")
    
    def _initialize_parameter_definitions(self) -> Dict[str, WorkflowParameterSet]:
        """パラメータ定義を初期化"""
        parameter_sets = {}
        
        # CI/CDパイプライン用パラメータ
        ci_cd_params = WorkflowParameterSet(workflow_id="ci-cd-pipeline.yml")
        ci_cd_params.parameters = {
            "environment": ParameterDefinition(
                name="environment",
                type=ParameterType.CHOICE,
                description="デプロイメント環境",
                required=True,
                choices=["development", "staging", "production"],
                default_value="staging"
            ),
            "skip_tests": ParameterDefinition(
                name="skip_tests",
                type=ParameterType.BOOLEAN,
                description="テストをスキップするかどうか",
                required=False,
                default_value=False
            ),
            "force_deploy": ParameterDefinition(
                name="force_deploy",
                type=ParameterType.BOOLEAN,
                description="強制デプロイを実行するかどうか",
                required=False,
                default_value=False
            ),
            "image_tag": ParameterDefinition(
                name="image_tag",
                type=ParameterType.STRING,
                description="デプロイするDockerイメージタグ",
                required=False,
                pattern=r"^[a-zA-Z0-9._-]+$"
            ),
            "notification_channel": ParameterDefinition(
                name="notification_channel",
                type=ParameterType.STRING,
                description="通知チャンネル",
                required=False,
                default_value="#therapeutic-app-deployments"
            )
        }
        
        # 環境固有のパラメータ
        ci_cd_params.environment_specific = {
            Environment.DEVELOPMENT: {
                "skip_tests": True,
                "notification_channel": "#therapeutic-app-dev"
            },
            Environment.STAGING: {
                "skip_tests": False,
                "notification_channel": "#therapeutic-app-staging"
            },
            Environment.PRODUCTION: {
                "skip_tests": False,
                "force_deploy": False,
                "notification_channel": "#therapeutic-app-production"
            }
        }
        
        parameter_sets["ci-cd-pipeline.yml"] = ci_cd_params
        
        # デプロイのみワークフロー用パラメータ
        deploy_only_params = WorkflowParameterSet(workflow_id="deploy-only.yml")
        deploy_only_params.parameters = {
            "environment": ParameterDefinition(
                name="environment",
                type=ParameterType.CHOICE,
                description="デプロイメント環境",
                required=True,
                choices=["development", "staging", "production"]
            ),
            "image_tag": ParameterDefinition(
                name="image_tag",
                type=ParameterType.STRING,
                description="デプロイするDockerイメージタグ",
                required=True,
                pattern=r"^[a-zA-Z0-9._-]+$"
            ),
            "skip_health_check": ParameterDefinition(
                name="skip_health_check",
                type=ParameterType.BOOLEAN,
                description="ヘルスチェックをスキップするかどうか",
                required=False,
                default_value=False
            ),
            "traffic_percentage": ParameterDefinition(
                name="traffic_percentage",
                type=ParameterType.INTEGER,
                description="初期トラフィック割合",
                required=False,
                default_value=10,
                min_value=1,
                max_value=100
            )
        }
        
        parameter_sets["deploy-only.yml"] = deploy_only_params
        
        # ロールバックワークフロー用パラメータ
        rollback_params = WorkflowParameterSet(workflow_id="rollback.yml")
        rollback_params.parameters = {
            "environment": ParameterDefinition(
                name="environment",
                type=ParameterType.CHOICE,
                description="ロールバック対象環境",
                required=True,
                choices=["staging", "production"]
            ),
            "target_revision": ParameterDefinition(
                name="target_revision",
                type=ParameterType.STRING,
                description="ロールバック先のリビジョン",
                required=True,
                pattern=r"^[a-zA-Z0-9-]+$"
            ),
            "reason": ParameterDefinition(
                name="reason",
                type=ParameterType.STRING,
                description="ロールバック理由",
                required=False,
                default_value="Manual rollback"
            ),
            "skip_confirmation": ParameterDefinition(
                name="skip_confirmation",
                type=ParameterType.BOOLEAN,
                description="確認をスキップするかどうか",
                required=False,
                default_value=False
            )
        }
        
        parameter_sets["rollback.yml"] = rollback_params
        
        return parameter_sets
    
    def get_workflow_parameters(self, environment: Environment, 
                               trigger_type: str = "manual") -> Dict[str, Any]:
        """
        ワークフロー用の基本パラメータを取得
        
        Args:
            environment: デプロイメント環境
            trigger_type: トリガータイプ
            
        Returns:
            基本パラメータ
        """
        base_params = {
            "environment": environment.value,
            "trigger_type": trigger_type,
            "project_id": self.config.cloud_config.project_id,
            "service_name": self.config.cloud_config.service_name,
            "region": self.config.cloud_config.region,
            "timestamp": str(int(time.time())),
            "deployment_strategy": self.config.strategy.value
        }
        
        # 環境固有の設定を追加
        if environment == Environment.PRODUCTION:
            base_params.update({
                "min_instances": str(self.config.cloud_config.min_instances),
                "max_instances": str(self.config.cloud_config.max_instances),
                "memory": self.config.cloud_config.memory,
                "cpu": self.config.cloud_config.cpu
            })
        
        # 通知設定
        if self.config.notification_config.slack_webhook_url:
            base_params["slack_webhook_url"] = self.config.notification_config.slack_webhook_url
        
        return base_params
    
    def validate_parameters(self, workflow_id: str, 
                           parameters: Dict[str, Any]) -> List[str]:
        """
        パラメータを検証
        
        Args:
            workflow_id: ワークフローID
            parameters: 検証するパラメータ
            
        Returns:
            エラーメッセージのリスト（空の場合は検証成功）
        """
        errors = []
        
        if workflow_id not in self.parameter_sets:
            errors.append(f"未知のワークフローID: {workflow_id}")
            return errors
        
        parameter_set = self.parameter_sets[workflow_id]
        
        # 必須パラメータのチェック
        for param_name, param_def in parameter_set.parameters.items():
            if param_def.required and param_name not in parameters:
                errors.append(f"必須パラメータが不足しています: {param_name}")
                continue
            
            if param_name not in parameters:
                continue
            
            value = parameters[param_name]
            
            # タイプ別検証
            validation_error = self._validate_parameter_value(param_def, value)
            if validation_error:
                errors.append(f"パラメータ '{param_name}': {validation_error}")
        
        # 未定義パラメータの警告
        for param_name in parameters:
            if param_name not in parameter_set.parameters:
                logger.warning(f"未定義のパラメータが指定されました: {param_name}")
        
        return errors
    
    def _validate_parameter_value(self, param_def: ParameterDefinition, 
                                 value: Any) -> Optional[str]:
        """
        パラメータ値を検証
        
        Args:
            param_def: パラメータ定義
            value: 検証する値
            
        Returns:
            エラーメッセージ（正常な場合はNone）
        """
        # 型チェック
        if param_def.type == ParameterType.BOOLEAN:
            if not isinstance(value, (bool, str)):
                return "boolean型である必要があります"
            if isinstance(value, str) and value.lower() not in ["true", "false"]:
                return "boolean値は 'true' または 'false' である必要があります"
        
        elif param_def.type == ParameterType.INTEGER:
            try:
                int_value = int(value)
                if param_def.min_value is not None and int_value < param_def.min_value:
                    return f"値は {param_def.min_value} 以上である必要があります"
                if param_def.max_value is not None and int_value > param_def.max_value:
                    return f"値は {param_def.max_value} 以下である必要があります"
            except (ValueError, TypeError):
                return "integer型である必要があります"
        
        elif param_def.type == ParameterType.CHOICE:
            if param_def.choices and str(value) not in param_def.choices:
                return f"値は次のいずれかである必要があります: {', '.join(param_def.choices)}"
        
        elif param_def.type == ParameterType.STRING:
            if not isinstance(value, str):
                return "string型である必要があります"
            
            # パターンマッチング
            if param_def.pattern:
                import re
                if not re.match(param_def.pattern, value):
                    return f"値がパターンにマッチしません: {param_def.pattern}"
        
        return None
    
    def apply_defaults(self, workflow_id: str, parameters: Dict[str, Any],
                      environment: Optional[Environment] = None) -> Dict[str, Any]:
        """
        デフォルト値を適用
        
        Args:
            workflow_id: ワークフローID
            parameters: パラメータ
            environment: 環境（環境固有のデフォルト値適用用）
            
        Returns:
            デフォルト値が適用されたパラメータ
        """
        if workflow_id not in self.parameter_sets:
            return parameters
        
        parameter_set = self.parameter_sets[workflow_id]
        result = parameters.copy()
        
        # 基本デフォルト値を適用
        for param_name, param_def in parameter_set.parameters.items():
            if param_name not in result and param_def.default_value is not None:
                result[param_name] = param_def.default_value
        
        # 環境固有のデフォルト値を適用
        if environment and environment in parameter_set.environment_specific:
            env_params = parameter_set.environment_specific[environment]
            for param_name, param_value in env_params.items():
                if param_name not in parameters:  # 明示的に指定されていない場合のみ
                    result[param_name] = param_value
        
        return result
    
    def get_parameter_definition(self, workflow_id: str, 
                               parameter_name: str) -> Optional[ParameterDefinition]:
        """
        パラメータ定義を取得
        
        Args:
            workflow_id: ワークフローID
            parameter_name: パラメータ名
            
        Returns:
            パラメータ定義（存在しない場合はNone）
        """
        if workflow_id not in self.parameter_sets:
            return None
        
        parameter_set = self.parameter_sets[workflow_id]
        return parameter_set.parameters.get(parameter_name)
    
    def get_workflow_parameter_schema(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        ワークフローのパラメータスキーマを取得
        
        Args:
            workflow_id: ワークフローID
            
        Returns:
            パラメータスキーマ（存在しない場合はNone）
        """
        if workflow_id not in self.parameter_sets:
            return None
        
        parameter_set = self.parameter_sets[workflow_id]
        schema = {
            "workflow_id": workflow_id,
            "parameters": {}
        }
        
        for param_name, param_def in parameter_set.parameters.items():
            param_schema = {
                "type": param_def.type.value,
                "description": param_def.description,
                "required": param_def.required
            }
            
            if param_def.default_value is not None:
                param_schema["default"] = param_def.default_value
            
            if param_def.choices:
                param_schema["choices"] = param_def.choices
            
            if param_def.min_value is not None:
                param_schema["min_value"] = param_def.min_value
            
            if param_def.max_value is not None:
                param_schema["max_value"] = param_def.max_value
            
            if param_def.pattern:
                param_schema["pattern"] = param_def.pattern
            
            schema["parameters"][param_name] = param_schema
        
        # 環境固有のパラメータも追加
        if parameter_set.environment_specific:
            schema["environment_specific"] = {}
            for env, env_params in parameter_set.environment_specific.items():
                schema["environment_specific"][env.value] = env_params
        
        return schema
    
    def convert_to_github_format(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """
        GitHub Actions形式にパラメータを変換
        
        Args:
            parameters: 変換するパラメータ
            
        Returns:
            GitHub Actions形式のパラメータ（全て文字列）
        """
        github_params = {}
        
        for key, value in parameters.items():
            if isinstance(value, bool):
                github_params[key] = str(value).lower()
            elif isinstance(value, (int, float)):
                github_params[key] = str(value)
            elif value is None:
                github_params[key] = ""
            else:
                github_params[key] = str(value)
        
        return github_params
    
    def load_parameters_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        ファイルからパラメータを読み込み
        
        Args:
            file_path: パラメータファイルのパス
            
        Returns:
            読み込まれたパラメータ
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    return json.load(f)
                elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    import yaml
                    return yaml.safe_load(f)
                else:
                    raise DeploymentError(f"サポートされていないファイル形式: {file_path}")
        
        except FileNotFoundError:
            raise DeploymentError(f"パラメータファイルが見つかりません: {file_path}")
        except Exception as e:
            raise DeploymentError(f"パラメータファイルの読み込みに失敗しました: {e}")
    
    def save_parameters_to_file(self, parameters: Dict[str, Any], 
                               file_path: str) -> None:
        """
        パラメータをファイルに保存
        
        Args:
            parameters: 保存するパラメータ
            file_path: 保存先ファイルのパス
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(parameters, f, indent=2, ensure_ascii=False)
                elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    import yaml
                    yaml.dump(parameters, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                else:
                    raise DeploymentError(f"サポートされていないファイル形式: {file_path}")
        
        except Exception as e:
            raise DeploymentError(f"パラメータファイルの保存に失敗しました: {e}")


# 時間モジュールのインポートを追加
import time