"""
Parameter Manager テスト
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch

from ..parameter_manager import (
    ParameterManager, ParameterDefinition, ParameterType, WorkflowParameterSet
)
try:
    from ....config import DeploymentConfig, Environment
    from ....exceptions import DeploymentError
except ImportError:
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


class TestParameterManager:
    """ParameterManager テストクラス"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.config = DeploymentConfig(environment=Environment.STAGING)
        self.manager = ParameterManager(self.config)
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.manager.config == self.config
        assert "ci-cd-pipeline.yml" in self.manager.parameter_sets
        assert "deploy-only.yml" in self.manager.parameter_sets
        assert "rollback.yml" in self.manager.parameter_sets
    
    def test_get_workflow_parameters(self):
        """ワークフローパラメータ取得テスト"""
        with patch('time.time', return_value=1234567890):
            params = self.manager.get_workflow_parameters(
                Environment.PRODUCTION, "manual"
            )
        
        assert params["environment"] == "production"
        assert params["trigger_type"] == "manual"
        assert params["project_id"] == self.config.cloud_config.project_id
        assert params["service_name"] == self.config.cloud_config.service_name
        assert params["region"] == self.config.cloud_config.region
        assert params["timestamp"] == "1234567890"
        assert params["deployment_strategy"] == self.config.strategy.value
    
    def test_validate_parameters_success(self):
        """パラメータ検証成功テスト"""
        parameters = {
            "environment": "staging",
            "skip_tests": "false",
            "force_deploy": "true",
            "image_tag": "v1.2.3"
        }
        
        errors = self.manager.validate_parameters("ci-cd-pipeline.yml", parameters)
        
        assert errors == []
    
    def test_validate_parameters_missing_required(self):
        """必須パラメータ不足テスト"""
        parameters = {
            "image_tag": "v1.2.3"
            # environment が不足
        }
        
        errors = self.manager.validate_parameters("deploy-only.yml", parameters)
        
        assert len(errors) > 0
        assert any("必須パラメータが不足しています: environment" in error for error in errors)
    
    def test_validate_parameters_invalid_choice(self):
        """無効な選択肢テスト"""
        parameters = {
            "environment": "invalid_env",
            "image_tag": "v1.2.3"
        }
        
        errors = self.manager.validate_parameters("deploy-only.yml", parameters)
        
        assert len(errors) > 0
        assert any("次のいずれかである必要があります" in error for error in errors)
    
    def test_validate_parameters_invalid_integer(self):
        """無効な整数値テスト"""
        parameters = {
            "environment": "staging",
            "image_tag": "v1.2.3",
            "traffic_percentage": "invalid_number"
        }
        
        errors = self.manager.validate_parameters("deploy-only.yml", parameters)
        
        assert len(errors) > 0
        assert any("integer型である必要があります" in error for error in errors)
    
    def test_validate_parameters_integer_range(self):
        """整数値範囲テスト"""
        parameters = {
            "environment": "staging",
            "image_tag": "v1.2.3",
            "traffic_percentage": "150"  # 最大値100を超過
        }
        
        errors = self.manager.validate_parameters("deploy-only.yml", parameters)
        
        assert len(errors) > 0
        assert any("100 以下である必要があります" in error for error in errors)
    
    def test_validate_parameters_invalid_pattern(self):
        """無効なパターンテスト"""
        parameters = {
            "environment": "staging",
            "image_tag": "invalid@tag!"  # パターンにマッチしない
        }
        
        errors = self.manager.validate_parameters("deploy-only.yml", parameters)
        
        assert len(errors) > 0
        assert any("パターンにマッチしません" in error for error in errors)
    
    def test_validate_parameters_unknown_workflow(self):
        """未知のワークフローテスト"""
        parameters = {"key": "value"}
        
        errors = self.manager.validate_parameters("unknown.yml", parameters)
        
        assert len(errors) == 1
        assert "未知のワークフローID: unknown.yml" in errors[0]
    
    def test_apply_defaults(self):
        """デフォルト値適用テスト"""
        parameters = {
            "environment": "staging"
        }
        
        result = self.manager.apply_defaults("ci-cd-pipeline.yml", parameters)
        
        assert result["environment"] == "staging"  # 元の値を保持
        assert result["skip_tests"] is False  # デフォルト値が適用
        assert result["force_deploy"] is False  # デフォルト値が適用
    
    def test_apply_defaults_with_environment(self):
        """環境固有のデフォルト値適用テスト"""
        parameters = {
            "environment": "production"
        }
        
        result = self.manager.apply_defaults(
            "ci-cd-pipeline.yml", parameters, Environment.PRODUCTION
        )
        
        assert result["environment"] == "production"
        assert result["force_deploy"] is False  # 環境固有のデフォルト値
        assert result["notification_channel"] == "#therapeutic-app-production"
    
    def test_get_parameter_definition(self):
        """パラメータ定義取得テスト"""
        param_def = self.manager.get_parameter_definition(
            "ci-cd-pipeline.yml", "environment"
        )
        
        assert param_def is not None
        assert param_def.name == "environment"
        assert param_def.type == ParameterType.CHOICE
        assert param_def.required is True
        assert "production" in param_def.choices
        
        # 存在しないパラメータ
        param_def = self.manager.get_parameter_definition(
            "ci-cd-pipeline.yml", "nonexistent"
        )
        assert param_def is None
        
        # 存在しないワークフロー
        param_def = self.manager.get_parameter_definition(
            "nonexistent.yml", "environment"
        )
        assert param_def is None
    
    def test_get_workflow_parameter_schema(self):
        """ワークフローパラメータスキーマ取得テスト"""
        schema = self.manager.get_workflow_parameter_schema("ci-cd-pipeline.yml")
        
        assert schema is not None
        assert schema["workflow_id"] == "ci-cd-pipeline.yml"
        assert "parameters" in schema
        assert "environment" in schema["parameters"]
        assert schema["parameters"]["environment"]["type"] == "choice"
        assert schema["parameters"]["environment"]["required"] is True
        assert "environment_specific" in schema
        
        # 存在しないワークフロー
        schema = self.manager.get_workflow_parameter_schema("nonexistent.yml")
        assert schema is None
    
    def test_convert_to_github_format(self):
        """GitHub Actions形式変換テスト"""
        parameters = {
            "string_param": "test",
            "bool_param": True,
            "int_param": 42,
            "float_param": 3.14,
            "none_param": None
        }
        
        github_params = self.manager.convert_to_github_format(parameters)
        
        assert github_params["string_param"] == "test"
        assert github_params["bool_param"] == "true"
        assert github_params["int_param"] == "42"
        assert github_params["float_param"] == "3.14"
        assert github_params["none_param"] == ""
    
    def test_load_parameters_from_json_file(self):
        """JSONファイルからのパラメータ読み込みテスト"""
        test_params = {
            "environment": "staging",
            "skip_tests": True,
            "image_tag": "v1.2.3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_params, f)
            temp_file = f.name
        
        try:
            loaded_params = self.manager.load_parameters_from_file(temp_file)
            assert loaded_params == test_params
        finally:
            os.unlink(temp_file)
    
    def test_load_parameters_from_yaml_file(self):
        """YAMLファイルからのパラメータ読み込みテスト"""
        test_params = {
            "environment": "staging",
            "skip_tests": True,
            "image_tag": "v1.2.3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("environment: staging\\n")
            f.write("skip_tests: true\\n")
            f.write("image_tag: v1.2.3\\n")
            temp_file = f.name
        
        try:
            with patch('yaml.safe_load', return_value=test_params):
                loaded_params = self.manager.load_parameters_from_file(temp_file)
                assert loaded_params == test_params
        finally:
            os.unlink(temp_file)
    
    def test_load_parameters_file_not_found(self):
        """存在しないファイルからの読み込みテスト"""
        with pytest.raises(DeploymentError, match="パラメータファイルが見つかりません"):
            self.manager.load_parameters_from_file("nonexistent.json")
    
    def test_load_parameters_unsupported_format(self):
        """サポートされていないファイル形式テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            with pytest.raises(DeploymentError, match="サポートされていないファイル形式"):
                self.manager.load_parameters_from_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_save_parameters_to_json_file(self):
        """JSONファイルへのパラメータ保存テスト"""
        test_params = {
            "environment": "staging",
            "skip_tests": True,
            "image_tag": "v1.2.3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            self.manager.save_parameters_to_file(test_params, temp_file)
            
            # ファイルが正しく保存されたか確認
            with open(temp_file, 'r') as f:
                loaded_params = json.load(f)
                assert loaded_params == test_params
        finally:
            os.unlink(temp_file)
    
    def test_save_parameters_to_yaml_file(self):
        """YAMLファイルへのパラメータ保存テスト"""
        test_params = {
            "environment": "staging",
            "skip_tests": True,
            "image_tag": "v1.2.3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_file = f.name
        
        try:
            with patch('yaml.dump') as mock_dump:
                self.manager.save_parameters_to_file(test_params, temp_file)
                mock_dump.assert_called_once()
        finally:
            os.unlink(temp_file)


class TestParameterDefinition:
    """ParameterDefinition テストクラス"""
    
    def test_parameter_definition_creation(self):
        """ParameterDefinition作成テスト"""
        param_def = ParameterDefinition(
            name="test_param",
            type=ParameterType.STRING,
            description="Test parameter",
            required=True,
            default_value="default",
            choices=["option1", "option2"],
            min_value=1,
            max_value=10,
            pattern=r"^[a-z]+$"
        )
        
        assert param_def.name == "test_param"
        assert param_def.type == ParameterType.STRING
        assert param_def.description == "Test parameter"
        assert param_def.required is True
        assert param_def.default_value == "default"
        assert param_def.choices == ["option1", "option2"]
        assert param_def.min_value == 1
        assert param_def.max_value == 10
        assert param_def.pattern == r"^[a-z]+$"


class TestParameterType:
    """ParameterType テストクラス"""
    
    def test_parameter_type_values(self):
        """ParameterType値テスト"""
        assert ParameterType.STRING.value == "string"
        assert ParameterType.BOOLEAN.value == "boolean"
        assert ParameterType.INTEGER.value == "integer"
        assert ParameterType.CHOICE.value == "choice"
        assert ParameterType.ENVIRONMENT.value == "environment"


class TestWorkflowParameterSet:
    """WorkflowParameterSet テストクラス"""
    
    def test_workflow_parameter_set_creation(self):
        """WorkflowParameterSet作成テスト"""
        param_set = WorkflowParameterSet(
            workflow_id="test.yml",
            parameters={
                "param1": ParameterDefinition(
                    name="param1",
                    type=ParameterType.STRING,
                    description="Parameter 1"
                )
            },
            environment_specific={
                Environment.PRODUCTION: {"param1": "prod_value"}
            }
        )
        
        assert param_set.workflow_id == "test.yml"
        assert "param1" in param_set.parameters
        assert Environment.PRODUCTION in param_set.environment_specific
        assert param_set.environment_specific[Environment.PRODUCTION]["param1"] == "prod_value"