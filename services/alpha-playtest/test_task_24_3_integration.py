"""
Task 24.3 ?: A/B?
"""
import pytest
import asyncio
import math
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

# ?
from ab_test_framework import (
    ABTestFramework, ABTestStatus, MetricType, StatisticalSignificance,
    ABTestVariant, ABTestExperiment, PerformanceMetric, StatisticalEngine
)

class TestABTestFrameworkIntegration:
    """A/B?"""
    
    @pytest.fixture
    def ab_framework(self):
        """A/B?"""
        return ABTestFramework()
    
    @pytest.fixture
    def statistical_engine(self):
        """?"""
        return StatisticalEngine()
    
    @pytest.mark.asyncio
    async def test_experiment_creation_and_setup(self, ab_framework):
        """実装"""
        
        # 1. 実装
        variants = [
            {
                "variant_id": "control",
                "name": "コア",
                "description": "?",
                "traffic_allocation": 0.5,
                "configuration": {"onboarding_type": "standard"},
                "is_control": True
            },
            {
                "variant_id": "variant_a",
                "name": "?",
                "description": "ストーリー",
                "traffic_allocation": 0.5,
                "configuration": {"onboarding_type": "simplified"}
            }
        ]
        
        experiment = await ab_framework.create_experiment(
            name="?",
            description="?",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.CONVERSION_RATE,
            duration_days=14,
            minimum_sample_size=100
        )
        
        # 2. 基本
        assert experiment.experiment_id is not None
        assert experiment.name == "?"
        assert len(experiment.variants) == 2
        assert experiment.primary_metric == MetricType.CONVERSION_RATE
        assert experiment.status == ABTestStatus.DRAFT
        
        # 3. バリデーション
        control_variant = next(v for v in experiment.variants if v.is_control)
        assert control_variant.variant_id == "control"
        assert control_variant.traffic_allocation == 0.5
        
        variant_a = next(v for v in experiment.variants if not v.is_control)
        assert variant_a.variant_id == "variant_a"
        assert variant_a.traffic_allocation == 0.5
        
        # 4. ?
        total_allocation = sum(v.traffic_allocation for v in experiment.variants)
        assert abs(total_allocation - 1.0) < 0.01
    
    @pytest.mark.asyncio
    async def test_user_assignment_consistency(self, ab_framework):
        """ユーザー"""
        
        # 1. 実装
        variants = [
            {"variant_id": "control", "name": "Control", "is_control": True},
            {"variant_id": "variant_a", "name": "Variant A"}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="一般",
            description="ユーザー",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.CONVERSION_RATE
        )
        
        # 2. 実装
        success = await ab_framework.start_experiment(experiment.experiment_id)
        assert success
        
        # 3. ?
        user_id = "consistency_user"
        
        first_assignment = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
        second_assignment = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
        third_assignment = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
        
        # 4. 一般
        assert first_assignment is not None
        assert first_assignment == second_assignment
        assert second_assignment == third_assignment
        assert first_assignment in ["control", "variant_a"]
    
    @pytest.mark.asyncio
    async def test_traffic_allocation_distribution(self, ab_framework):
        """?"""
        
        # 1. ?
        variants = [
            {"variant_id": "control", "name": "Control", "traffic_allocation": 0.7, "is_control": True},
            {"variant_id": "variant_a", "name": "Variant A", "traffic_allocation": 0.3}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="?",
            description="?",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.CONVERSION_RATE
        )
        
        await ab_framework.start_experiment(experiment.experiment_id)
        
        # 2. ?
        assignments = {}
        num_users = 1000
        
        for i in range(num_users):
            user_id = f"user_{i}"
            variant = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            assignments[variant] = assignments.get(variant, 0) + 1
        
        # 3. ?5%の
        control_ratio = assignments.get("control", 0) / num_users
        variant_a_ratio = assignments.get("variant_a", 0) / num_users
        
        assert abs(control_ratio - 0.7) < 0.05
        assert abs(variant_a_ratio - 0.3) < 0.05
    
    @pytest.mark.asyncio
    async def test_metric_recording_and_analysis(self, ab_framework):
        """メイン"""
        
        # 1. 実装
        variants = [
            {"variant_id": "control", "name": "Control", "is_control": True},
            {"variant_id": "variant_a", "name": "Variant A"}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="メイン",
            description="メイン",
            hypothesis="バリデーションAは",
            variants=variants,
            primary_metric=MetricType.CONVERSION_RATE,
            minimum_sample_size=20
        )
        
        await ab_framework.start_experiment(experiment.experiment_id)
        
        # 2. ユーザー
        control_users = []
        variant_a_users = []
        
        for i in range(50):
            user_id = f"metric_user_{i}"
            variant = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            
            if variant == "control":
                control_users.append(user_id)
                # コア: ?0.3?
                conversion_rate = 0.3 if i % 10 < 3 else 0.0
            else:
                variant_a_users.append(user_id)
                # バリデーションA: ?0.5?
                conversion_rate = 0.5 if i % 10 < 5 else 0.0
            
            # メイン
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.CONVERSION_RATE,
                value=conversion_rate,
                experiment_id=experiment.experiment_id
            )
        
        # 3. ?
        analysis_result = await ab_framework.analyze_experiment(experiment.experiment_id)
        
        # 4. ?
        assert "variant_results" in analysis_result
        assert "control" in analysis_result["variant_results"]
        assert "variant_a" in analysis_result["variant_results"]
        
        control_result = analysis_result["variant_results"]["control"]
        variant_a_result = analysis_result["variant_results"]["variant_a"]
        
        # 基本
        assert "primary_metric" in control_result
        assert "primary_metric" in variant_a_result
        
        control_mean = control_result["primary_metric"]["mean"]
        variant_a_mean = variant_a_result["primary_metric"]["mean"]
        
        # バリデーションAの
        assert variant_a_mean > control_mean
        # 実装
    
    @pytest.mark.asyncio
    async def test_statistical_significance_detection(self, ab_framework):
        """?"""
        
        # 1. 実装
        variants = [
            {"variant_id": "control", "name": "Control", "is_control": True},
            {"variant_id": "variant_b", "name": "Variant B"}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="?",
            description="?",
            hypothesis="バリデーションBは",
            variants=variants,
            primary_metric=MetricType.SESSION_DURATION,
            minimum_sample_size=30
        )
        
        await ab_framework.start_experiment(experiment.experiment_id)
        
        # 2. ?
        for i in range(100):
            user_id = f"sig_user_{i}"
            variant = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            
            if variant == "control":
                # コア: ?300?50
                session_duration = max(0, 300 + (i % 20 - 10) * 5)
            else:
                # バリデーションB: ?400?50?
                session_duration = max(0, 400 + (i % 20 - 10) * 5)
            
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.SESSION_DURATION,
                value=session_duration,
                experiment_id=experiment.experiment_id
            )
        
        # 3. ?
        analysis_result = await ab_framework.analyze_experiment(experiment.experiment_id)
        
        # 4. ?
        assert "statistical_tests" in analysis_result
        assert len(analysis_result["statistical_tests"]) > 0
        
        test_result = analysis_result["statistical_tests"][0]
        
        # ?
        assert test_result["p_value"] < 0.05  # ?
        # Enumの
        significance_str = test_result["significance_level"]
        if hasattr(significance_str, 'value'):
            significance_str = significance_str.value
        assert significance_str in ["significant", "highly_significant", "highly", "marginally"]
        assert test_result["effect_size"] > 0  # ?
        
        # ?
        assert analysis_result["winner"] == "variant_b"
    
    @pytest.mark.asyncio
    async def test_experiment_lifecycle_management(self, ab_framework):
        """実装"""
        
        # 1. 実装
        variants = [
            {"variant_id": "control", "name": "Control", "is_control": True},
            {"variant_id": "variant_c", "name": "Variant C"}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="?",
            description="実装",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.TASK_COMPLETION_RATE
        )
        
        # 2. ?
        assert experiment.status == ABTestStatus.DRAFT
        
        # 3. 実装
        success = await ab_framework.start_experiment(experiment.experiment_id)
        assert success
        assert ab_framework.experiments[experiment.experiment_id].status == ABTestStatus.ACTIVE
        
        # 4. 実装
        status = ab_framework.get_experiment_status(experiment.experiment_id)
        assert status["status"] == "active"
        assert status["total_users"] == 0  # ま
        assert status["progress"]["overall"] == 0.0
        
        # 5. ユーザー
        for i in range(10):
            user_id = f"lifecycle_user_{i}"
            await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.TASK_COMPLETION_RATE,
                value=0.8,
                experiment_id=experiment.experiment_id
            )
        
        # 6. ?
        status = ab_framework.get_experiment_status(experiment.experiment_id)
        assert status["total_users"] == 10
        assert status["progress"]["by_sample_size"] > 0
        
        # 7. 実装
        success = await ab_framework.stop_experiment(experiment.experiment_id, "test_complete")
        assert success
        assert ab_framework.experiments[experiment.experiment_id].status == ABTestStatus.COMPLETED
        
        # 8. ?
        experiment_obj = ab_framework.experiments[experiment.experiment_id]
        assert experiment_obj.results is not None
        assert len(experiment_obj.results) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_experiments_management(self, ab_framework):
        """?"""
        
        # 1. ?
        experiments = []
        
        for i in range(3):
            variants = [
                {"variant_id": f"control_{i}", "name": f"Control {i}", "is_control": True},
                {"variant_id": f"variant_{i}", "name": f"Variant {i}"}
            ]
            
            experiment = await ab_framework.create_experiment(
                name=f"実装{i+1}",
                description=f"?{i+1}",
                hypothesis=f"?{i+1}",
                variants=variants,
                primary_metric=MetricType.USER_SATISFACTION
            )
            experiments.append(experiment)
        
        # 2. 一般
        await ab_framework.start_experiment(experiments[0].experiment_id)
        await ab_framework.start_experiment(experiments[1].experiment_id)
        # experiments[2]はDRAFTの
        
        # 3. 実装
        all_experiments = ab_framework.list_experiments()
        assert len(all_experiments) == 3
        
        active_experiments = ab_framework.list_experiments(status=ABTestStatus.ACTIVE)
        assert len(active_experiments) == 2
        
        draft_experiments = ab_framework.list_experiments(status=ABTestStatus.DRAFT)
        assert len(draft_experiments) == 1
        
        # 4. ユーザー
        user_id = "multi_exp_user"
        
        variant_0 = await ab_framework.assign_user_to_variant(user_id, experiments[0].experiment_id)
        variant_1 = await ab_framework.assign_user_to_variant(user_id, experiments[1].experiment_id)
        variant_2 = await ab_framework.assign_user_to_variant(user_id, experiments[2].experiment_id)  # DRAFT実装
        
        # 5. ?
        assert variant_0 is not None
        assert variant_1 is not None
        assert variant_2 is None  # DRAFT実装
        
        # 6. ユーザー
        user_experiments = ab_framework.get_user_experiments(user_id)
        assert len(user_experiments) == 2
        assert experiments[0].experiment_id in user_experiments
        assert experiments[1].experiment_id in user_experiments
        assert experiments[2].experiment_id not in user_experiments
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, ab_framework):
        """?"""
        
        # 1. 実装
        standalone_metrics = []
        
        for i in range(10):
            metric = await ab_framework.record_metric(
                user_id=f"standalone_user_{i}",
                metric_type=MetricType.RESPONSE_TIME,
                value=100 + i * 10,  # 100-190ms
                session_id=f"session_{i}",
                device_info={"platform": "mobile", "os": "iOS"}
            )
            standalone_metrics.append(metric)
        
        # 2. ?
        assert len(standalone_metrics) == 10
        
        for metric in standalone_metrics:
            assert metric.experiment_id is None
            assert metric.variant_id is None
            assert metric.metric_type == MetricType.RESPONSE_TIME
            assert 100 <= metric.value <= 190
        
        # 3. 実装
        variants = [
            {"variant_id": "fast", "name": "Fast Version", "is_control": True},
            {"variant_id": "slow", "name": "Slow Version"}
        ]
        
        experiment = await ab_framework.create_experiment(
            name="?",
            description="レベル",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.RESPONSE_TIME
        )
        
        await ab_framework.start_experiment(experiment.experiment_id)
        
        # 4. 実装
        experiment_metrics = []
        
        for i in range(20):
            user_id = f"perf_user_{i}"
            variant = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            
            # バリデーション
            if variant == "fast":
                response_time = 50 + i * 2  # 50-88ms
            else:
                response_time = 150 + i * 3  # 150-207ms
            
            metric = await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.RESPONSE_TIME,
                value=response_time,
                experiment_id=experiment.experiment_id
            )
            experiment_metrics.append(metric)
        
        # 5. 実装
        assert len(experiment_metrics) == 20
        
        for metric in experiment_metrics:
            assert metric.experiment_id == experiment.experiment_id
            assert metric.variant_id in ["fast", "slow"]
        
        # 6. ?
        total_metrics = len(ab_framework.performance_metrics)
        assert total_metrics >= 30  # standalone + experiment metrics
    
    def test_statistical_engine_t_test(self, statistical_engine):
        """?t検証"""
        
        # 1. ?
        result_significant = statistical_engine.perform_t_test(
            mean1=100, std1=10, n1=50,  # コア
            mean2=110, std2=12, n2=50   # ?10%?
        )
        
        assert result_significant.test_type == "t_test"
        assert result_significant.p_value < 0.05  # ?
        assert result_significant.significance_level != StatisticalSignificance.NOT_SIGNIFICANT
        assert result_significant.effect_size > 0  # ?
        
        # 2. ?
        result_not_significant = statistical_engine.perform_t_test(
            mean1=100, std1=10, n1=50,
            mean2=101, std2=10, n2=50   # わ
        )
        
        assert result_not_significant.p_value > 0.05  # ?
        assert result_not_significant.significance_level == StatisticalSignificance.NOT_SIGNIFICANT
        
        # 3. ?
        result_small_sample = statistical_engine.perform_t_test(
            mean1=100, std1=10, n1=1,
            mean2=110, std2=10, n2=1
        )
        
        assert result_small_sample.p_value == 1.0
        assert result_small_sample.significance_level == StatisticalSignificance.NOT_SIGNIFICANT
        assert result_small_sample.effect_size == 0.0
    
    @pytest.mark.asyncio
    async def test_therapeutic_effectiveness_measurement(self, ab_framework):
        """治療"""
        
        # 1. 治療
        variants = [
            {
                "variant_id": "standard_therapy",
                "name": "?",
                "is_control": True,
                "configuration": {"therapy_intensity": "standard"}
            },
            {
                "variant_id": "enhanced_therapy",
                "name": "?",
                "configuration": {"therapy_intensity": "enhanced"}
            }
        ]
        
        experiment = await ab_framework.create_experiment(
            name="治療",
            description="治療",
            hypothesis="?",
            variants=variants,
            primary_metric=MetricType.THERAPEUTIC_PROGRESS,
            duration_days=30,
            minimum_sample_size=50
        )
        
        await ab_framework.start_experiment(experiment.experiment_id)
        
        # 2. 治療
        for i in range(80):
            user_id = f"therapy_user_{i}"
            variant = await ab_framework.assign_user_to_variant(user_id, experiment.experiment_id)
            
            # 治療0-100?
            if variant == "standard_therapy":
                # ?: ?60?15
                progress_score = max(0, min(100, 60 + (i % 30 - 15)))
            else:
                # ?: ?75?12?
                progress_score = max(0, min(100, 75 + (i % 24 - 12)))
            
            # ?
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.THERAPEUTIC_PROGRESS,
                value=progress_score,
                experiment_id=experiment.experiment_id
            )
            
            # ?
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.USER_SATISFACTION,
                value=progress_score * 0.8 / 100 * 5,  # 1-5ストーリー
                experiment_id=experiment.experiment_id
            )
            
            await ab_framework.record_metric(
                user_id=user_id,
                metric_type=MetricType.ENGAGEMENT_SCORE,
                value=progress_score * 0.9,
                experiment_id=experiment.experiment_id
            )
        
        # 3. ?
        analysis_result = await ab_framework.analyze_experiment(experiment.experiment_id)
        
        # 4. 治療
        standard_result = analysis_result["variant_results"]["standard_therapy"]
        enhanced_result = analysis_result["variant_results"]["enhanced_therapy"]
        
        standard_progress = standard_result["primary_metric"]["mean"]
        enhanced_progress = enhanced_result["primary_metric"]["mean"]
        
        # ?
        assert enhanced_progress > standard_progress
        # 実装
        
        # ?
        assert "user_satisfaction" in enhanced_result["secondary_metrics"]
        assert "engagement_score" in enhanced_result["secondary_metrics"]
        
        enhanced_satisfaction = enhanced_result["secondary_metrics"]["user_satisfaction"]["mean"]
        standard_satisfaction = standard_result["secondary_metrics"]["user_satisfaction"]["mean"]
        
        assert enhanced_satisfaction > standard_satisfaction
        
        # 5. ?
        if analysis_result["statistical_tests"]:
            test_result = analysis_result["statistical_tests"][0]
            assert test_result["effect_size"] > 0.5  # ?
            
            # 治療
            if test_result["p_value"] < 0.05 and enhanced_progress > standard_progress:
                assert analysis_result["winner"] == "enhanced_therapy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])