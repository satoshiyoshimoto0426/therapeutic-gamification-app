"""
デプロイメントオーケストレータのテスト

自動デプロイメントシステムのコア機能をテストします。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from .orchestrator import (
    DeploymentOrchestrator, DeploymentResult, DeploymentStatus,
    DeploymentStep, DeploymentPhase
)
from .config import Environment, DeploymentStrategy, DeploymentConfig, CloudConfig
from .exceptions import (
    DeploymentError, PreDeploymentError, DeploymentExecutionError,
    ErrorSeverity, ErrorCategory
)


class TestDeploymentOrchestrator:
    """デプロイメントオーケストレータのテストクラス"""
    
    @pytest.fixture
    def config(self):
        """テスト用設定"""
        cloud_config = CloudConfig(
            project_id="test-project",
            service_name="test-service"
        )
        return DeploymentConfig(
            environment=Environment.DEVELOPMENT,
            strategy=DeploymentStrategy.BLUE_GREEN,
            cloud_config=cloud_config
        )
    
    @pytest.fixture
    def orchestrator(self, config):
        """テスト用オーケストレータ"""
        return DeploymentOrchestrator(config)
    
    def test_orchestrator_initialization(self, orchestrator):
        """オーケストレータの初期化テスト"""
        assert orchestrator.config is not None
        assert len(orchestrator.deployment_steps) > 0
        assert orchestrator.current_deployment is None
        
        # デフォルトステップが登録されているか確認
        step_names = [step.name for step in orchestrator.deployment_steps]
        expected_steps = [
            "validate_prerequisites",
            "setup_environment", 
            "build_and_deploy",
            "health_check",
            "migrate_traffic",
            "post_deployment_monitoring",
            "cleanup"
        ]
        
        for expected_step in expected_steps:
            assert expected_step in step_names
    
    def test_step_registration(self, orchestrator):
        """ステップ登録のテスト"""
        # カスタムステップを作成
        custom_step = DeploymentStep(
            name="custom_test_step",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock()
        )
        
        # ステップを登録
        orchestrator.register_step(custom_step)
        
        # 登録されたか確認
        assert "custom_test_step" in orchestrator._step_registry
        assert custom_step in orchestrator.deployment_steps
    
    def test_dependency_resolution(self, orchestrator):
        """依存関係解決のテスト"""
        # 依存関係を持つステップを追加
        step_a = DeploymentStep(
            name="step_a",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock()
        )
        step_b = DeploymentStep(
            name="step_b",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock(),
            dependencies=["step_a"]
        )
        step_c = DeploymentStep(
            name="step_c",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock(),
            dependencies=["step_a", "step_b"]
        )
        
        # 既存のステップをクリアして新しいステップを設定
        orchestrator.deployment_steps = [step_c, step_a, step_b]  # 意図的に順序を混乱
        
        # 依存関係を解決
        resolved_steps = orchestrator._resolve_dependencies()
        
        # 正しい順序で解決されているか確認
        step_names = [step.name for step in resolved_steps]
        assert step_names.index("step_a") < step_names.index("step_b")
        assert step_names.index("step_b") < step_names.index("step_c")
    
    def test_circular_dependency_detection(self, orchestrator):
        """循環依存関係の検出テスト"""
        # 循環依存関係を持つステップを作成
        step_a = DeploymentStep(
            name="step_a",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock(),
            dependencies=["step_b"]
        )
        step_b = DeploymentStep(
            name="step_b",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock(),
            dependencies=["step_a"]
        )
        
        orchestrator.deployment_steps = [step_a, step_b]
        
        # 循環依存関係が検出されることを確認
        with pytest.raises(PreDeploymentError) as exc_info:
            orchestrator._resolve_dependencies()
        
        assert "循環依存関係" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_successful_deployment(self, orchestrator):
        """成功デプロイメントのテスト"""
        # モックステップを作成
        mock_steps = []
        for i, step in enumerate(orchestrator.deployment_steps):
            mock_step = AsyncMock()
            mock_step.return_value = None
            step.function = mock_step
            mock_steps.append(mock_step)
        
        # デプロイメント実行
        result = await orchestrator.deploy(Environment.DEVELOPMENT)
        
        # 結果の確認
        assert result.status == DeploymentStatus.COMPLETED
        assert result.is_success
        assert result.error is None
        assert len(result.steps_completed) > 0
        assert len(result.steps_failed) == 0
        assert result.duration_seconds is not None
        assert result.duration_seconds > 0
        
        # 全てのステップが実行されたか確認
        for mock_step in mock_steps:
            mock_step.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deployment_with_step_failure(self, orchestrator):
        """ステップ失敗時のデプロイメントテスト"""
        # 最初のステップを失敗させる
        first_step = orchestrator.deployment_steps[0]
        first_step.function = AsyncMock(side_effect=Exception("テストエラー"))
        
        # 他のステップは成功させる
        for step in orchestrator.deployment_steps[1:]:
            step.function = AsyncMock()
        
        # デプロイメント実行
        result = await orchestrator.deploy(Environment.DEVELOPMENT)
        
        # 結果の確認
        assert result.status == DeploymentStatus.FAILED
        assert not result.is_success
        assert result.error is not None
        assert len(result.steps_failed) > 0
        assert first_step.name in result.steps_failed
    
    @pytest.mark.asyncio
    async def test_deployment_timeout(self, orchestrator):
        """デプロイメントタイムアウトのテスト"""
        # タイムアウトを短く設定
        first_step = orchestrator.deployment_steps[0]
        first_step.timeout_seconds = 0.1
        
        # ステップを長時間実行させる
        async def slow_function():
            await asyncio.sleep(1)  # タイムアウトより長い時間
        
        first_step.function = slow_function
        
        # デプロイメント実行
        result = await orchestrator.deploy(Environment.DEVELOPMENT)
        
        # タイムアウトで失敗することを確認
        assert result.status == DeploymentStatus.FAILED
        assert not result.is_success
        assert "タイムアウト" in str(result.error.message)
    
    @pytest.mark.asyncio
    async def test_non_required_step_failure(self, orchestrator):
        """必須でないステップの失敗テスト"""
        # 最後のステップ（cleanup）は通常必須でない
        cleanup_step = next(
            step for step in orchestrator.deployment_steps 
            if step.name == "cleanup"
        )
        cleanup_step.required = False
        cleanup_step.function = AsyncMock(side_effect=Exception("クリーンアップエラー"))
        
        # 他のステップは成功させる
        for step in orchestrator.deployment_steps:
            if step.name != "cleanup":
                step.function = AsyncMock()
        
        # デプロイメント実行
        result = await orchestrator.deploy(Environment.DEVELOPMENT)
        
        # 必須でないステップの失敗でもデプロイメントは成功
        assert result.status == DeploymentStatus.COMPLETED
        assert result.is_success
        assert "cleanup" in result.steps_failed
    
    @pytest.mark.asyncio
    async def test_rollback_on_failure(self, orchestrator):
        """失敗時の自動ロールバックテスト"""
        # ロールバック設定を有効化
        orchestrator.config.rollback_on_failure = True
        
        # ロールバックマネージャーのモック
        orchestrator.rollback_manager = Mock()
        orchestrator.rollback_manager.execute_rollback = AsyncMock()
        
        # 重要なステップを失敗させる
        critical_step = orchestrator.deployment_steps[2]  # build_and_deploy
        critical_step.function = AsyncMock(
            side_effect=DeploymentExecutionError(
                "重要なエラー",
                severity=ErrorSeverity.CRITICAL
            )
        )
        
        # デプロイメント実行
        result = await orchestrator.deploy(Environment.DEVELOPMENT)
        
        # ロールバックが実行されたか確認
        assert result.status == DeploymentStatus.ROLLED_BACK
        orchestrator.rollback_manager.execute_rollback.assert_called_once()
    
    def test_deployment_result_serialization(self):
        """デプロイメント結果のシリアライゼーションテスト"""
        result = DeploymentResult(
            deployment_id="test-123",
            status=DeploymentStatus.COMPLETED,
            start_time=datetime.utcnow(),
            environment=Environment.DEVELOPMENT
        )
        result.end_time = result.start_time + timedelta(seconds=30)
        result.service_url = "https://test-service.example.com"
        result.steps_completed = ["step1", "step2"]
        
        # 辞書形式に変換
        result_dict = result.to_dict()
        
        # 必要なフィールドが含まれているか確認
        assert result_dict["deployment_id"] == "test-123"
        assert result_dict["status"] == "completed"
        assert result_dict["environment"] == "development"
        assert result_dict["service_url"] == "https://test-service.example.com"
        assert result_dict["duration_seconds"] == 30.0
        assert result_dict["steps_completed"] == ["step1", "step2"]
    
    def test_get_deployment_status(self, orchestrator):
        """デプロイメント状態取得のテスト"""
        # デプロイメントが実行されていない場合
        assert orchestrator.get_deployment_status() is None
        
        # デプロイメント結果を設定
        orchestrator.current_deployment = DeploymentResult(
            deployment_id="test-456",
            status=DeploymentStatus.DEPLOYING,
            start_time=datetime.utcnow(),
            environment=Environment.STAGING
        )
        
        # 状態が取得できることを確認
        status = orchestrator.get_deployment_status()
        assert status is not None
        assert status["deployment_id"] == "test-456"
        assert status["status"] == "deploying"
    
    @pytest.mark.asyncio
    async def test_deployment_cancellation(self, orchestrator):
        """デプロイメントキャンセルのテスト"""
        # 実行中のデプロイメントを模擬
        orchestrator.current_deployment = DeploymentResult(
            deployment_id="test-789",
            status=DeploymentStatus.DEPLOYING,
            start_time=datetime.utcnow(),
            environment=Environment.PRODUCTION
        )
        
        # キャンセル実行
        cancelled = await orchestrator.cancel_deployment()
        
        # キャンセルが成功することを確認
        assert cancelled is True
        
        # 完了済みデプロイメントはキャンセルできない
        orchestrator.current_deployment.status = DeploymentStatus.COMPLETED
        cancelled = await orchestrator.cancel_deployment()
        assert cancelled is False


@pytest.mark.asyncio
class TestDeploymentSteps:
    """デプロイメントステップのテスト"""
    
    @pytest.fixture
    def orchestrator(self):
        """テスト用オーケストレータ"""
        config = DeploymentConfig(
            environment=Environment.DEVELOPMENT,
            cloud_config=CloudConfig(project_id="test", service_name="test")
        )
        return DeploymentOrchestrator(config)
    
    async def test_step_execution_success(self, orchestrator):
        """ステップ実行成功のテスト"""
        # テスト用ステップを作成
        test_step = DeploymentStep(
            name="test_step",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock()
        )
        
        # デプロイメント結果を初期化
        orchestrator.current_deployment = DeploymentResult(
            deployment_id="test",
            status=DeploymentStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        # ロガーを初期化
        from .logging_config import initialize_logging
        log_manager = initialize_logging(orchestrator.config)
        orchestrator.logger = log_manager.get_deployment_logger("test")
        
        # ステップ実行
        await orchestrator._execute_step(test_step)
        
        # 成功が記録されているか確認
        assert "test_step" in orchestrator.current_deployment.steps_completed
        assert "test_step" not in orchestrator.current_deployment.steps_failed
        test_step.function.assert_called_once()
    
    async def test_step_execution_failure(self, orchestrator):
        """ステップ実行失敗のテスト"""
        # 失敗するステップを作成
        test_step = DeploymentStep(
            name="failing_step",
            phase=DeploymentPhase.PRE_VALIDATION,
            function=AsyncMock(side_effect=Exception("テストエラー")),
            required=True
        )
        
        # デプロイメント結果を初期化
        orchestrator.current_deployment = DeploymentResult(
            deployment_id="test",
            status=DeploymentStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        # ロガーを初期化
        from .logging_config import initialize_logging
        log_manager = initialize_logging(orchestrator.config)
        orchestrator.logger = log_manager.get_deployment_logger("test")
        
        # ステップ実行（例外が発生することを期待）
        with pytest.raises(DeploymentExecutionError):
            await orchestrator._execute_step(test_step)
        
        # 失敗が記録されているか確認
        assert "failing_step" in orchestrator.current_deployment.steps_failed
        assert "failing_step" not in orchestrator.current_deployment.steps_completed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])