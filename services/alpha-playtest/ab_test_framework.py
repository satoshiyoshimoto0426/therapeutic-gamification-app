"""
A/B?
?A/B?
"""
import uuid
import json
import statistics
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from collections import defaultdict, Counter
import logging
import asyncio
import random
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

class ABTestStatus(Enum):
    """A/B?"""
    DRAFT = "draft"           # ?
    ACTIVE = "active"         # 実装
    PAUSED = "paused"         # 一般
    COMPLETED = "completed"   # ?
    CANCELLED = "cancelled"   # ?

class MetricType(Enum):
    """メイン"""
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    SESSION_DURATION = "session_duration"
    TASK_COMPLETION_RATE = "task_completion_rate"
    USER_SATISFACTION = "user_satisfaction"
    THERAPEUTIC_PROGRESS = "therapeutic_progress"
    ENGAGEMENT_SCORE = "engagement_score"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"

class StatisticalSignificance(Enum):
    """?"""
    NOT_SIGNIFICANT = "not_significant"      # p > 0.05
    MARGINALLY_SIGNIFICANT = "marginally"    # 0.01 < p <= 0.05
    SIGNIFICANT = "significant"              # 0.001 < p <= 0.01
    HIGHLY_SIGNIFICANT = "highly"            # p <= 0.001

@dataclass
class ABTestVariant:
    """A/B?"""
    variant_id: str
    name: str
    description: str
    traffic_allocation: float  # 0.0-1.0
    configuration: Dict[str, Any]
    is_control: bool = False

@dataclass
class MetricResult:
    """メイン"""
    metric_type: MetricType
    variant_id: str
    value: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    standard_error: float

@dataclass
class StatisticalTest:
    """?"""
    test_type: str
    p_value: float
    significance_level: StatisticalSignificance
    effect_size: float
    power: float
    confidence_level: float = 0.95

class ABTestExperiment(BaseModel):
    """A/B?"""
    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    hypothesis: str
    
    # 実装
    variants: List[ABTestVariant] = Field(default_factory=list)
    primary_metric: MetricType
    secondary_metrics: List[MetricType] = Field(default_factory=list)
    
    # 実装
    start_date: datetime
    end_date: datetime
    minimum_sample_size: int = 100
    minimum_duration_days: int = 7
    
    # ストーリー
    status: ABTestStatus = ABTestStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # ?
    results: Dict[str, Any] = Field(default_factory=dict)
    statistical_tests: List[StatisticalTest] = Field(default_factory=list)
    winner: Optional[str] = None
    
    # メイン
    created_by: str = "system"
    tags: List[str] = Field(default_factory=list)

class PerformanceMetric(BaseModel):
    """?"""
    metric_id: str = Field(default_factory=lambda: f"perf_{uuid.uuid4().hex[:8]}")
    experiment_id: Optional[str] = None
    variant_id: Optional[str] = None
    user_id: str
    
    # メイン
    metric_type: MetricType
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # コア
    session_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None

class ABTestFramework:
    """A/B?"""
    
    def __init__(self):
        self.experiments: Dict[str, ABTestExperiment] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant_id}
        self.performance_metrics: List[PerformanceMetric] = []
        self.statistical_engine = StatisticalEngine()
        
    async def create_experiment(self, name: str, description: str, hypothesis: str,
                              variants: List[Dict[str, Any]], primary_metric: MetricType,
                              duration_days: int = 14, minimum_sample_size: int = 100) -> ABTestExperiment:
        """A/B?"""
        
        # バリデーション
        ab_variants = []
        total_allocation = 0.0
        
        for i, variant_data in enumerate(variants):
            allocation = variant_data.get("traffic_allocation", 1.0 / len(variants))
            total_allocation += allocation
            
            variant = ABTestVariant(
                variant_id=variant_data.get("variant_id", f"variant_{i}"),
                name=variant_data["name"],
                description=variant_data.get("description", ""),
                traffic_allocation=allocation,
                configuration=variant_data.get("configuration", {}),
                is_control=variant_data.get("is_control", i == 0)
            )
            ab_variants.append(variant)
        
        # ?
        if abs(total_allocation - 1.0) > 0.01:
            for variant in ab_variants:
                variant.traffic_allocation /= total_allocation
        
        # 実装
        experiment = ABTestExperiment(
            name=name,
            description=description,
            hypothesis=hypothesis,
            variants=ab_variants,
            primary_metric=primary_metric,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            minimum_sample_size=minimum_sample_size,
            minimum_duration_days=min(duration_days, 7)
        )
        
        self.experiments[experiment.experiment_id] = experiment
        
        logger.info(f"A/B test experiment created: {experiment.experiment_id}")
        return experiment
    
    async def assign_user_to_variant(self, user_id: str, experiment_id: str) -> Optional[str]:
        """ユーザー"""
        
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return None
        
        experiment = self.experiments[experiment_id]
        
        # 実装
        if experiment.status != ABTestStatus.ACTIVE:
            return None
        
        # ?
        if user_id in self.user_assignments and experiment_id in self.user_assignments[user_id]:
            return self.user_assignments[user_id][experiment_id]
        
        # ?
        variant_id = self._select_variant(user_id, experiment.variants)
        
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        
        self.user_assignments[user_id][experiment_id] = variant_id
        
        logger.info(f"User {user_id} assigned to variant {variant_id} in experiment {experiment_id}")
        return variant_id
    
    def _select_variant(self, user_id: str, variants: List[ABTestVariant]) -> str:
        """バリデーション"""
        
        # ユーザーID?
        hash_value = hash(user_id) % 10000 / 10000.0  # 0.0-1.0の
        
        cumulative_allocation = 0.0
        for variant in variants:
            cumulative_allocation += variant.traffic_allocation
            if hash_value <= cumulative_allocation:
                return variant.variant_id
        
        # ?
        return variants[-1].variant_id
    
    async def record_metric(self, user_id: str, metric_type: MetricType, value: float,
                          experiment_id: Optional[str] = None, session_id: Optional[str] = None,
                          device_info: Optional[Dict] = None) -> PerformanceMetric:
        """メイン"""
        
        variant_id = None
        if experiment_id and user_id in self.user_assignments:
            variant_id = self.user_assignments[user_id].get(experiment_id)
        
        metric = PerformanceMetric(
            experiment_id=experiment_id,
            variant_id=variant_id,
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            session_id=session_id,
            device_info=device_info
        )
        
        self.performance_metrics.append(metric)
        
        logger.debug(f"Metric recorded: {metric_type.value} = {value} for user {user_id}")
        return metric
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """実装"""
        
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        
        # バリデーション
        if len(experiment.variants) < 2:
            logger.error(f"Experiment {experiment_id} needs at least 2 variants")
            return False
        
        # ?
        total_allocation = sum(v.traffic_allocation for v in experiment.variants)
        if abs(total_allocation - 1.0) > 0.01:
            logger.error(f"Experiment {experiment_id} traffic allocation must sum to 1.0")
            return False
        
        experiment.status = ABTestStatus.ACTIVE
        experiment.start_date = datetime.now()
        experiment.updated_at = datetime.now()
        
        logger.info(f"A/B test experiment started: {experiment_id}")
        return True
    
    async def stop_experiment(self, experiment_id: str, reason: str = "manual") -> bool:
        """実装"""
        
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.status = ABTestStatus.COMPLETED
        experiment.end_date = datetime.now()
        experiment.updated_at = datetime.now()
        
        # ?
        await self.analyze_experiment(experiment_id)
        
        logger.info(f"A/B test experiment stopped: {experiment_id} (reason: {reason})")
        return True
    
    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """実装"""
        
        if experiment_id not in self.experiments:
            return {}
        
        experiment = self.experiments[experiment_id]
        
        # メイン
        experiment_metrics = [
            m for m in self.performance_metrics
            if m.experiment_id == experiment_id
        ]
        
        if not experiment_metrics:
            return {"error": "No metrics found for experiment"}
        
        # バリデーション
        variant_results = {}
        for variant in experiment.variants:
            variant_metrics = [m for m in experiment_metrics if m.variant_id == variant.variant_id]
            
            if variant_metrics:
                result = await self._analyze_variant_metrics(variant_metrics, experiment.primary_metric)
                variant_results[variant.variant_id] = result
        
        # ?
        statistical_tests = await self._perform_statistical_tests(variant_results, experiment)
        
        # ?
        winner = self._determine_winner(variant_results, statistical_tests)
        
        # ?
        analysis_result = {
            "experiment_id": experiment_id,
            "analyzed_at": datetime.now().isoformat(),
            "variant_results": variant_results,
            "statistical_tests": [test.__dict__ for test in statistical_tests],
            "winner": winner,
            "sample_sizes": {vid: len([m for m in experiment_metrics if m.variant_id == vid]) 
                           for vid in variant_results.keys()},
            "duration_days": (datetime.now() - experiment.start_date).days,
            "total_users": len(set(m.user_id for m in experiment_metrics))
        }
        
        experiment.results = analysis_result
        experiment.statistical_tests = statistical_tests
        experiment.winner = winner
        experiment.updated_at = datetime.now()
        
        return analysis_result
    
    async def _analyze_variant_metrics(self, metrics: List[PerformanceMetric], 
                                     primary_metric: MetricType) -> Dict[str, Any]:
        """バリデーション"""
        
        # ?
        primary_values = [m.value for m in metrics if m.metric_type == primary_metric]
        
        if not primary_values:
            return {"error": "No primary metric values found"}
        
        # 基本
        mean_value = statistics.mean(primary_values)
        std_dev = statistics.stdev(primary_values) if len(primary_values) > 1 else 0
        sample_size = len(primary_values)
        
        # 信頼95%?
        if sample_size > 1:
            std_error = std_dev / math.sqrt(sample_size)
            margin_of_error = 1.96 * std_error  # 95%信頼
            confidence_interval = (mean_value - margin_of_error, mean_value + margin_of_error)
        else:
            confidence_interval = (mean_value, mean_value)
            std_error = 0
        
        # ?
        secondary_metrics = {}
        for metric_type in MetricType:
            if metric_type != primary_metric:
                secondary_values = [m.value for m in metrics if m.metric_type == metric_type]
                if secondary_values:
                    secondary_metrics[metric_type.value] = {
                        "mean": statistics.mean(secondary_values),
                        "sample_size": len(secondary_values)
                    }
        
        return {
            "primary_metric": {
                "mean": mean_value,
                "std_dev": std_dev,
                "std_error": std_error,
                "sample_size": sample_size,
                "confidence_interval": confidence_interval
            },
            "secondary_metrics": secondary_metrics
        }
    
    async def _perform_statistical_tests(self, variant_results: Dict[str, Any], 
                                        experiment: ABTestExperiment) -> List[StatisticalTest]:
        """?"""
        
        tests = []
        
        # コア
        control_variant = next((v for v in experiment.variants if v.is_control), None)
        if not control_variant:
            control_variant = experiment.variants[0]  # ?
        
        control_result = variant_results.get(control_variant.variant_id)
        if not control_result or "primary_metric" not in control_result:
            return tests
        
        control_mean = control_result["primary_metric"]["mean"]
        control_std = control_result["primary_metric"]["std_dev"]
        control_n = control_result["primary_metric"]["sample_size"]
        
        # ?
        for variant in experiment.variants:
            if variant.variant_id == control_variant.variant_id:
                continue
            
            variant_result = variant_results.get(variant.variant_id)
            if not variant_result or "primary_metric" not in variant_result:
                continue
            
            variant_mean = variant_result["primary_metric"]["mean"]
            variant_std = variant_result["primary_metric"]["std_dev"]
            variant_n = variant_result["primary_metric"]["sample_size"]
            
            # t検証
            test_result = self.statistical_engine.perform_t_test(
                control_mean, control_std, control_n,
                variant_mean, variant_std, variant_n
            )
            
            tests.append(test_result)
        
        return tests
    
    def _determine_winner(self, variant_results: Dict[str, Any], 
                         statistical_tests: List[StatisticalTest]) -> Optional[str]:
        """?"""
        
        # ?
        significant_tests = [
            test for test in statistical_tests
            if test.significance_level in [StatisticalSignificance.SIGNIFICANT, 
                                         StatisticalSignificance.HIGHLY_SIGNIFICANT,
                                         StatisticalSignificance.MARGINALLY_SIGNIFICANT]
        ]
        
        if not significant_tests:
            return None  # ?
        
        # ?
        best_test = max(significant_tests, key=lambda t: abs(t.effect_size))
        
        # ?
        if best_test.effect_size > 0:
            # ?
            best_variant = None
            best_mean = float('-inf')
            
            for variant_id, result in variant_results.items():
                if "primary_metric" in result:
                    mean_value = result["primary_metric"]["mean"]
                    if mean_value > best_mean:
                        best_mean = mean_value
                        best_variant = variant_id
            
            return best_variant
        
        return None
    
    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """実装"""
        
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        experiment = self.experiments[experiment_id]
        
        # ?
        experiment_metrics = [
            m for m in self.performance_metrics
            if m.experiment_id == experiment_id
        ]
        
        unique_users = len(set(m.user_id for m in experiment_metrics))
        
        # バリデーション
        variant_users = {}
        for variant in experiment.variants:
            variant_metrics = [m for m in experiment_metrics if m.variant_id == variant.variant_id]
            variant_users[variant.variant_id] = len(set(m.user_id for m in variant_metrics))
        
        # ?
        days_running = (datetime.now() - experiment.start_date).days
        progress_by_time = min(1.0, days_running / experiment.minimum_duration_days)
        progress_by_sample = min(1.0, unique_users / experiment.minimum_sample_size)
        
        return {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "status": experiment.status.value,
            "start_date": experiment.start_date.isoformat(),
            "end_date": experiment.end_date.isoformat(),
            "days_running": days_running,
            "total_users": unique_users,
            "variant_users": variant_users,
            "progress": {
                "by_time": progress_by_time,
                "by_sample_size": progress_by_sample,
                "overall": min(progress_by_time, progress_by_sample)
            },
            "ready_for_analysis": (
                progress_by_time >= 1.0 and 
                progress_by_sample >= 1.0 and
                experiment.status == ABTestStatus.ACTIVE
            )
        }
    
    def get_user_experiments(self, user_id: str) -> Dict[str, str]:
        """ユーザー"""
        return self.user_assignments.get(user_id, {})
    
    def list_experiments(self, status: Optional[ABTestStatus] = None) -> List[Dict[str, Any]]:
        """実装"""
        experiments = list(self.experiments.values())
        
        if status:
            experiments = [exp for exp in experiments if exp.status == status]
        
        return [
            {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "status": exp.status.value,
                "primary_metric": exp.primary_metric.value,
                "variants_count": len(exp.variants),
                "start_date": exp.start_date.isoformat(),
                "end_date": exp.end_date.isoformat(),
                "created_at": exp.created_at.isoformat()
            }
            for exp in experiments
        ]

class StatisticalEngine:
    """?"""
    
    def perform_t_test(self, mean1: float, std1: float, n1: int,
                      mean2: float, std2: float, n2: int) -> StatisticalTest:
        """t検証"""
        
        if n1 <= 1 or n2 <= 1:
            return StatisticalTest(
                test_type="t_test",
                p_value=1.0,
                significance_level=StatisticalSignificance.NOT_SIGNIFICANT,
                effect_size=0.0,
                power=0.0
            )
        
        # プレビュー
        pooled_std = math.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        # t?
        if pooled_std == 0:
            t_stat = 0
        else:
            t_stat = (mean2 - mean1) / (pooled_std * math.sqrt(1/n1 + 1/n2))
        
        # 自動
        df = n1 + n2 - 2
        
        # p?
        p_value = 2 * (1 - self._normal_cdf(abs(t_stat)))
        p_value = max(0.001, min(1.0, p_value))  # ?
        
        # ?
        if p_value <= 0.001:
            significance = StatisticalSignificance.HIGHLY_SIGNIFICANT
        elif p_value <= 0.01:
            significance = StatisticalSignificance.SIGNIFICANT
        elif p_value <= 0.05:
            significance = StatisticalSignificance.MARGINALLY_SIGNIFICANT
        else:
            significance = StatisticalSignificance.NOT_SIGNIFICANT
        
        # ?Cohen's d?
        if pooled_std == 0:
            effect_size = 0
        else:
            effect_size = (mean2 - mean1) / pooled_std
        
        # 検証
        power = min(1.0, max(0.0, 1 - p_value))
        
        return StatisticalTest(
            test_type="t_test",
            p_value=p_value,
            significance_level=significance,
            effect_size=effect_size,
            power=power
        )
    
    def _normal_cdf(self, x: float) -> float:
        """?"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# ?A/B?
ab_test_framework = ABTestFramework()