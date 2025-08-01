"""
治療 - タスク20.2

治療
ユーザー
ゲーム

?: 14.1-14.5
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math
import sys
import os

# プレビュー
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.core_types import TaskType


class TherapeuticMetric(Enum):
    """治療"""
    SELF_EFFICACY = "self_efficacy"           # 自動
    MOOD_STABILITY = "mood_stability"         # 気分
    TASK_COMPLETION_CONFIDENCE = "task_completion_confidence"  # タスク
    SOCIAL_ENGAGEMENT = "social_engagement"   # ?
    STRESS_MANAGEMENT = "stress_management"   # ストーリー
    COGNITIVE_FLEXIBILITY = "cognitive_flexibility"  # ?
    MOTIVATION_SUSTAINABILITY = "motivation_sustainability"  # ?


class GamingMetric(Enum):
    """ゲーム"""
    ENGAGEMENT_LEVEL = "engagement_level"     # エラー
    PROGRESSION_SATISFACTION = "progression_satisfaction"  # ?
    CHALLENGE_BALANCE = "challenge_balance"   # 挑
    REWARD_MEANINGFULNESS = "reward_meaningfulness"  # ?
    SOCIAL_INTERACTION = "social_interaction"  # ?
    ACHIEVEMENT_MOTIVATION = "achievement_motivation"  # ?
    FLOW_STATE_FREQUENCY = "flow_state_frequency"  # ?


class BalanceRisk(Enum):
    """バリデーション"""
    LOW = "low"           # ?
    MODERATE = "moderate" # ?
    HIGH = "high"         # ?
    CRITICAL = "critical" # ?


@dataclass
class TherapeuticAssessment:
    """治療"""
    user_id: str
    timestamp: datetime
    metrics: Dict[TherapeuticMetric, float]  # 0.0-1.0ストーリー
    overall_therapeutic_score: float
    improvement_areas: List[str]
    strengths: List[str]
    risk_factors: List[str]


@dataclass
class GamingAssessment:
    """ゲーム"""
    user_id: str
    timestamp: datetime
    metrics: Dict[GamingMetric, float]  # 0.0-1.0ストーリー
    overall_gaming_score: float
    engagement_quality: str
    addiction_risk_score: float
    healthy_gaming_indicators: List[str]


@dataclass
class BalanceAnalysis:
    """バリデーション"""
    user_id: str
    timestamp: datetime
    therapeutic_score: float
    gaming_score: float
    balance_ratio: float  # therapeutic/gaming
    balance_risk: BalanceRisk
    optimization_recommendations: List[str]
    intervention_needed: bool


@dataclass
class EngagementMetrics:
    """エラー"""
    daily_active_time: float  # ?
    session_frequency: int
    task_completion_rate: float
    story_engagement_rate: float
    social_interaction_count: int
    achievement_unlock_rate: float
    retention_score: float


class TherapeuticGamingBalanceSystem:
    """治療"""
    
    def __init__(self):
        self.therapeutic_assessments: Dict[str, List[TherapeuticAssessment]] = {}
        self.gaming_assessments: Dict[str, List[GamingAssessment]] = {}
        self.balance_analyses: Dict[str, List[BalanceAnalysis]] = {}
        self.engagement_history: Dict[str, List[EngagementMetrics]] = {}
        
        # 治療
        self.therapeutic_targets = {
            TherapeuticMetric.SELF_EFFICACY: {"min": 0.6, "optimal": 0.8},
            TherapeuticMetric.MOOD_STABILITY: {"min": 0.5, "optimal": 0.75},
            TherapeuticMetric.TASK_COMPLETION_CONFIDENCE: {"min": 0.7, "optimal": 0.85},
            TherapeuticMetric.SOCIAL_ENGAGEMENT: {"min": 0.4, "optimal": 0.7},
            TherapeuticMetric.STRESS_MANAGEMENT: {"min": 0.6, "optimal": 0.8},
            TherapeuticMetric.COGNITIVE_FLEXIBILITY: {"min": 0.5, "optimal": 0.75},
            TherapeuticMetric.MOTIVATION_SUSTAINABILITY: {"min": 0.6, "optimal": 0.8}
        }
        
        # ゲーム
        self.gaming_healthy_ranges = {
            GamingMetric.ENGAGEMENT_LEVEL: {"min": 0.4, "max": 0.8, "optimal": 0.6},
            GamingMetric.PROGRESSION_SATISFACTION: {"min": 0.6, "max": 0.9, "optimal": 0.75},
            GamingMetric.CHALLENGE_BALANCE: {"min": 0.5, "max": 0.8, "optimal": 0.65},
            GamingMetric.REWARD_MEANINGFULNESS: {"min": 0.7, "max": 1.0, "optimal": 0.85},
            GamingMetric.SOCIAL_INTERACTION: {"min": 0.3, "max": 0.7, "optimal": 0.5},
            GamingMetric.ACHIEVEMENT_MOTIVATION: {"min": 0.5, "max": 0.8, "optimal": 0.65},
            GamingMetric.FLOW_STATE_FREQUENCY: {"min": 0.3, "max": 0.7, "optimal": 0.5}
        }
    
    def assess_therapeutic_effectiveness(
        self, 
        user_id: str, 
        user_activities: Dict[str, Any],
        mood_logs: List[Dict[str, Any]],
        task_history: List[Dict[str, Any]]
    ) -> TherapeuticAssessment:
        """治療"""
        
        metrics = {}
        
        # 1. 自動
        task_success_rate = self._calculate_task_success_rate(task_history)
        challenge_progression = self._calculate_challenge_progression(task_history)
        metrics[TherapeuticMetric.SELF_EFFICACY] = min(1.0, (task_success_rate * 0.6) + (challenge_progression * 0.4))
        
        # 2. 気分
        mood_variance = self._calculate_mood_variance(mood_logs)
        mood_trend = self._calculate_mood_trend(mood_logs)
        metrics[TherapeuticMetric.MOOD_STABILITY] = min(1.0, (1.0 - mood_variance) * 0.7 + mood_trend * 0.3)
        
        # 3. タスク
        completion_confidence = self._calculate_completion_confidence(task_history)
        metrics[TherapeuticMetric.TASK_COMPLETION_CONFIDENCE] = completion_confidence
        
        # 4. ?
        social_tasks_rate = self._calculate_social_tasks_rate(task_history)
        social_interaction_quality = self._calculate_social_interaction_quality(user_activities)
        metrics[TherapeuticMetric.SOCIAL_ENGAGEMENT] = (social_tasks_rate * 0.6) + (social_interaction_quality * 0.4)
        
        # 5. ストーリー
        stress_coping_score = self._calculate_stress_coping_score(user_activities, mood_logs)
        metrics[TherapeuticMetric.STRESS_MANAGEMENT] = stress_coping_score
        
        # 6. ?
        cognitive_flexibility = self._calculate_cognitive_flexibility(task_history, user_activities)
        metrics[TherapeuticMetric.COGNITIVE_FLEXIBILITY] = cognitive_flexibility
        
        # 7. ?
        motivation_sustainability = self._calculate_motivation_sustainability(user_activities)
        metrics[TherapeuticMetric.MOTIVATION_SUSTAINABILITY] = motivation_sustainability
        
        # ?
        overall_score = statistics.mean(metrics.values())
        
        # ?
        improvement_areas = []
        strengths = []
        risk_factors = []
        
        for metric, score in metrics.items():
            target = self.therapeutic_targets[metric]
            if score < target["min"]:
                improvement_areas.append(f"{metric.value}: {score:.2f} < {target['min']}")
                if score < target["min"] * 0.7:  # 30%?
                    risk_factors.append(f"{metric.value}の")
            elif score >= target["optimal"]:
                strengths.append(f"{metric.value}: {score:.2f} (?)")
        
        assessment = TherapeuticAssessment(
            user_id=user_id,
            timestamp=datetime.now(),
            metrics=metrics,
            overall_therapeutic_score=overall_score,
            improvement_areas=improvement_areas,
            strengths=strengths,
            risk_factors=risk_factors
        )
        
        # ?
        if user_id not in self.therapeutic_assessments:
            self.therapeutic_assessments[user_id] = []
        self.therapeutic_assessments[user_id].append(assessment)
        
        return assessment
    
    def assess_gaming_engagement(
        self, 
        user_id: str, 
        gaming_activities: Dict[str, Any],
        session_data: List[Dict[str, Any]]
    ) -> GamingAssessment:
        """ゲーム"""
        
        metrics = {}
        
        # 1. エラー
        daily_playtime = gaming_activities.get("daily_playtime_minutes", 0)
        session_frequency = len(session_data)
        engagement_level = min(1.0, (daily_playtime / 120) * 0.6 + (session_frequency / 5) * 0.4)
        metrics[GamingMetric.ENGAGEMENT_LEVEL] = engagement_level
        
        # 2. ?
        level_progression = gaming_activities.get("level_progression_rate", 0)
        achievement_rate = gaming_activities.get("achievement_unlock_rate", 0)
        progression_satisfaction = (level_progression * 0.5) + (achievement_rate * 0.5)
        metrics[GamingMetric.PROGRESSION_SATISFACTION] = min(1.0, progression_satisfaction)
        
        # 3. 挑
        task_difficulty_distribution = gaming_activities.get("task_difficulty_distribution", {})
        challenge_balance = self._calculate_challenge_balance(task_difficulty_distribution)
        metrics[GamingMetric.CHALLENGE_BALANCE] = challenge_balance
        
        # 4. ?
        reward_satisfaction = gaming_activities.get("reward_satisfaction_score", 0.5)
        reward_usage_rate = gaming_activities.get("reward_usage_rate", 0.5)
        reward_meaningfulness = (reward_satisfaction * 0.7) + (reward_usage_rate * 0.3)
        metrics[GamingMetric.REWARD_MEANINGFULNESS] = reward_meaningfulness
        
        # 5. ?
        social_interactions = gaming_activities.get("social_interactions_count", 0)
        community_participation = gaming_activities.get("community_participation_rate", 0)
        social_interaction = min(1.0, (social_interactions / 10) * 0.6 + community_participation * 0.4)
        metrics[GamingMetric.SOCIAL_INTERACTION] = social_interaction
        
        # 6. ?
        goal_setting_frequency = gaming_activities.get("goal_setting_frequency", 0)
        goal_achievement_rate = gaming_activities.get("goal_achievement_rate", 0)
        achievement_motivation = (goal_setting_frequency * 0.4) + (goal_achievement_rate * 0.6)
        metrics[GamingMetric.ACHIEVEMENT_MOTIVATION] = min(1.0, achievement_motivation)
        
        # 7. ?
        flow_state_sessions = gaming_activities.get("flow_state_sessions", 0)
        total_sessions = max(1, len(session_data))
        flow_frequency = min(1.0, flow_state_sessions / total_sessions)
        metrics[GamingMetric.FLOW_STATE_FREQUENCY] = flow_frequency
        
        # ?
        overall_score = statistics.mean(metrics.values())
        
        # エラー
        if overall_score >= 0.8:
            engagement_quality = "excellent"
        elif overall_score >= 0.6:
            engagement_quality = "good"
        elif overall_score >= 0.4:
            engagement_quality = "moderate"
        else:
            engagement_quality = "low"
        
        # ?
        addiction_risk_score = self._calculate_addiction_risk(gaming_activities, session_data)
        
        # ?
        healthy_indicators = []
        for metric, score in metrics.items():
            range_info = self.gaming_healthy_ranges[metric]
            if range_info["min"] <= score <= range_info["max"]:
                healthy_indicators.append(f"{metric.value}が")
        
        assessment = GamingAssessment(
            user_id=user_id,
            timestamp=datetime.now(),
            metrics=metrics,
            overall_gaming_score=overall_score,
            engagement_quality=engagement_quality,
            addiction_risk_score=addiction_risk_score,
            healthy_gaming_indicators=healthy_indicators
        )
        
        # ?
        if user_id not in self.gaming_assessments:
            self.gaming_assessments[user_id] = []
        self.gaming_assessments[user_id].append(assessment)
        
        return assessment
    
    def analyze_therapeutic_gaming_balance(
        self, 
        user_id: str,
        therapeutic_assessment: TherapeuticAssessment,
        gaming_assessment: GamingAssessment
    ) -> BalanceAnalysis:
        """治療"""
        
        therapeutic_score = therapeutic_assessment.overall_therapeutic_score
        gaming_score = gaming_assessment.overall_gaming_score
        
        # バリデーション/ゲーム
        balance_ratio = therapeutic_score / max(0.1, gaming_score)
        
        # バリデーション
        balance_risk = self._determine_balance_risk(
            therapeutic_score, gaming_score, balance_ratio, gaming_assessment.addiction_risk_score
        )
        
        # ?
        optimization_recommendations = self._generate_optimization_recommendations(
            therapeutic_assessment, gaming_assessment, balance_ratio
        )
        
        # ?
        intervention_needed = (
            balance_risk in [BalanceRisk.HIGH, BalanceRisk.CRITICAL] or
            therapeutic_score < 0.4 or
            gaming_assessment.addiction_risk_score > 0.7
        )
        
        analysis = BalanceAnalysis(
            user_id=user_id,
            timestamp=datetime.now(),
            therapeutic_score=therapeutic_score,
            gaming_score=gaming_score,
            balance_ratio=balance_ratio,
            balance_risk=balance_risk,
            optimization_recommendations=optimization_recommendations,
            intervention_needed=intervention_needed
        )
        
        # ?
        if user_id not in self.balance_analyses:
            self.balance_analyses[user_id] = []
        self.balance_analyses[user_id].append(analysis)
        
        return analysis
    
    def monitor_engagement_metrics(
        self, 
        user_id: str, 
        daily_data: Dict[str, Any]
    ) -> EngagementMetrics:
        """エラー"""
        
        metrics = EngagementMetrics(
            daily_active_time=daily_data.get("active_time_minutes", 0),
            session_frequency=daily_data.get("session_count", 0),
            task_completion_rate=daily_data.get("task_completion_rate", 0.0),
            story_engagement_rate=daily_data.get("story_engagement_rate", 0.0),
            social_interaction_count=daily_data.get("social_interactions", 0),
            achievement_unlock_rate=daily_data.get("achievement_unlock_rate", 0.0),
            retention_score=self._calculate_retention_score(user_id, daily_data)
        )
        
        # エラー
        if user_id not in self.engagement_history:
            self.engagement_history[user_id] = []
        self.engagement_history[user_id].append(metrics)
        
        # ?30?
        cutoff_date = datetime.now() - timedelta(days=30)
        # ?30?
        if len(self.engagement_history[user_id]) > 30:
            self.engagement_history[user_id] = self.engagement_history[user_id][-30:]
        
        return metrics
    
    def verify_therapeutic_safety(self, user_id: str) -> Dict[str, Any]:
        """治療"""
        
        if user_id not in self.therapeutic_assessments or user_id not in self.gaming_assessments:
            return {
                "error": "?",
                "overall_safety": "unknown",
                "safety_checks": {},
                "recommendations": ["?"]
            }
        
        recent_therapeutic = self.therapeutic_assessments[user_id][-1]
        recent_gaming = self.gaming_assessments[user_id][-1]
        recent_balance = self.balance_analyses[user_id][-1] if user_id in self.balance_analyses else None
        
        safety_checks = {
            "therapeutic_effectiveness": {
                "status": "safe" if recent_therapeutic.overall_therapeutic_score >= 0.5 else "at_risk",
                "score": recent_therapeutic.overall_therapeutic_score,
                "risk_factors": recent_therapeutic.risk_factors
            },
            "gaming_addiction_risk": {
                "status": "safe" if recent_gaming.addiction_risk_score <= 0.5 else "at_risk",
                "risk_score": recent_gaming.addiction_risk_score,
                "warning_signs": self._identify_addiction_warning_signs(recent_gaming)
            },
            "balance_stability": {
                "status": "stable" if recent_balance and recent_balance.balance_risk in [BalanceRisk.LOW, BalanceRisk.MODERATE] else "unstable",
                "balance_ratio": recent_balance.balance_ratio if recent_balance else 0,
                "intervention_needed": recent_balance.intervention_needed if recent_balance else True
            }
        }
        
        # ?
        overall_safety = "safe"
        if any(check["status"] in ["at_risk", "unstable"] for check in safety_checks.values()):
            overall_safety = "needs_attention"
        
        if (safety_checks["therapeutic_effectiveness"]["score"] < 0.3 or 
            safety_checks["gaming_addiction_risk"]["risk_score"] > 0.8):
            overall_safety = "critical"
        
        return {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "overall_safety": overall_safety,
            "safety_checks": safety_checks,
            "recommendations": self._generate_safety_recommendations(safety_checks)
        }
    
    def generate_balance_report(self, user_id: str) -> Dict[str, Any]:
        """バリデーション"""
        
        if (user_id not in self.therapeutic_assessments or 
            user_id not in self.gaming_assessments):
            return {"error": "?"}
        
        # ?
        latest_therapeutic = self.therapeutic_assessments[user_id][-1]
        latest_gaming = self.gaming_assessments[user_id][-1]
        latest_balance = self.balance_analyses[user_id][-1] if user_id in self.balance_analyses else None
        
        # ?7?
        recent_engagement = self.engagement_history[user_id][-7:] if user_id in self.engagement_history else []
        avg_engagement = self._calculate_average_engagement(recent_engagement)
        
        # ?
        therapeutic_trend = self._calculate_therapeutic_trend(user_id)
        gaming_trend = self._calculate_gaming_trend(user_id)
        
        return {
            "user_id": user_id,
            "report_timestamp": datetime.now().isoformat(),
            "current_state": {
                "therapeutic_score": latest_therapeutic.overall_therapeutic_score,
                "gaming_score": latest_gaming.overall_gaming_score,
                "balance_ratio": latest_balance.balance_ratio if latest_balance else 0,
                "balance_risk": latest_balance.balance_risk.value if latest_balance else "unknown"
            },
            "trends": {
                "therapeutic_trend": therapeutic_trend,
                "gaming_trend": gaming_trend
            },
            "engagement_metrics": avg_engagement,
            "therapeutic_details": {
                "strengths": latest_therapeutic.strengths,
                "improvement_areas": latest_therapeutic.improvement_areas,
                "risk_factors": latest_therapeutic.risk_factors
            },
            "gaming_details": {
                "engagement_quality": latest_gaming.engagement_quality,
                "addiction_risk": latest_gaming.addiction_risk_score,
                "healthy_indicators": latest_gaming.healthy_gaming_indicators
            },
            "optimization_recommendations": latest_balance.optimization_recommendations if latest_balance else [],
            "safety_verification": self.verify_therapeutic_safety(user_id)
        }
    
    # ヘルパー
    def _calculate_task_success_rate(self, task_history: List[Dict[str, Any]]) -> float:
        """タスク"""
        if not task_history:
            return 0.5
        
        completed_tasks = sum(1 for task in task_history if task.get("status") == "completed")
        return completed_tasks / len(task_history)
    
    def _calculate_challenge_progression(self, task_history: List[Dict[str, Any]]) -> float:
        """挑"""
        if len(task_history) < 2:
            return 0.5
        
        # ?
        difficulties = [task.get("difficulty", 1) for task in task_history[-10:]]  # ?10?
        if len(difficulties) < 2:
            return 0.5
        
        trend = (difficulties[-1] - difficulties[0]) / max(1, len(difficulties) - 1)
        return min(1.0, 0.5 + trend * 0.1)  # ?
    
    def _calculate_mood_variance(self, mood_logs: List[Dict[str, Any]]) -> float:
        """気分"""
        if not mood_logs:
            return 0.5
        
        mood_scores = [log.get("mood_score", 3) for log in mood_logs[-14:]]  # ?14?
        if len(mood_scores) < 2:
            return 0.5
        
        variance = statistics.variance(mood_scores)
        return min(1.0, variance / 4.0)  # 1-5ストーリー
    
    def _calculate_mood_trend(self, mood_logs: List[Dict[str, Any]]) -> float:
        """気分"""
        if len(mood_logs) < 2:
            return 0.5
        
        recent_moods = [log.get("mood_score", 3) for log in mood_logs[-7:]]  # ?7?
        if len(recent_moods) < 2:
            return 0.5
        
        trend = (recent_moods[-1] - recent_moods[0]) / max(1, len(recent_moods) - 1)
        return min(1.0, 0.5 + trend * 0.1)  # ?
    
    def _calculate_completion_confidence(self, task_history: List[Dict[str, Any]]) -> float:
        """?"""
        if not task_history:
            return 0.5
        
        # ?
        confidence_scores = []
        for task in task_history[-20:]:  # ?20?
            if task.get("status") == "completed":
                # ?
                difficulty = task.get("difficulty", 1)
                estimated_duration = task.get("estimated_duration", 30)
                actual_duration = task.get("actual_duration", estimated_duration)
                
                time_efficiency = estimated_duration / max(1, actual_duration)
                confidence = min(1.0, time_efficiency * (1.0 - (difficulty - 1) * 0.1))
                confidence_scores.append(confidence)
        
        return statistics.mean(confidence_scores) if confidence_scores else 0.5
    
    def _calculate_social_tasks_rate(self, task_history: List[Dict[str, Any]]) -> float:
        """?"""
        if not task_history:
            return 0.0
        
        social_tasks = sum(1 for task in task_history if task.get("task_type") == "social")
        return social_tasks / len(task_history)
    
    def _calculate_social_interaction_quality(self, user_activities: Dict[str, Any]) -> float:
        """?"""
        interactions = user_activities.get("social_interactions", 0)
        positive_feedback = user_activities.get("positive_social_feedback", 0)
        
        if interactions == 0:
            return 0.0
        
        quality_ratio = positive_feedback / interactions
        return min(1.0, quality_ratio)
    
    def _calculate_stress_coping_score(
        self, 
        user_activities: Dict[str, Any], 
        mood_logs: List[Dict[str, Any]]
    ) -> float:
        """ストーリー"""
        # ADHD支援
        adhd_support_usage = user_activities.get("adhd_support_usage_rate", 0)
        
        # ?
        break_compliance = user_activities.get("break_compliance_rate", 0)
        
        # 気分
        mood_recovery_rate = self._calculate_mood_recovery_rate(mood_logs)
        
        return (adhd_support_usage * 0.4) + (break_compliance * 0.3) + (mood_recovery_rate * 0.3)
    
    def _calculate_cognitive_flexibility(
        self, 
        task_history: List[Dict[str, Any]], 
        user_activities: Dict[str, Any]
    ) -> float:
        """?"""
        # タスク
        task_types = set(task.get("task_type", "routine") for task in task_history[-20:])
        type_diversity = len(task_types) / 4.0  # 4?
        
        # ?
        approach_changes = user_activities.get("problem_solving_approach_changes", 0)
        approach_flexibility = min(1.0, approach_changes / 10.0)
        
        return (type_diversity * 0.6) + (approach_flexibility * 0.4)
    
    def _calculate_motivation_sustainability(self, user_activities: Dict[str, Any]) -> float:
        """?"""
        # ?
        consecutive_days = user_activities.get("consecutive_active_days", 0)
        consistency_score = min(1.0, consecutive_days / 30.0)  # 30?
        
        # ?
        activity_stability = user_activities.get("activity_level_stability", 0.5)
        
        return (consistency_score * 0.7) + (activity_stability * 0.3)
    
    def _calculate_challenge_balance(self, difficulty_distribution: Dict[str, int]) -> float:
        """挑"""
        if not difficulty_distribution:
            return 0.5
        
        total_tasks = sum(difficulty_distribution.values())
        if total_tasks == 0:
            return 0.5
        
        # 理: ?20%, ?40%, ?30%, ?10%
        ideal_distribution = {"1": 0.2, "2": 0.4, "3": 0.3, "4": 0.1, "5": 0.0}
        
        balance_score = 0.0
        for difficulty, count in difficulty_distribution.items():
            actual_ratio = count / total_tasks
            ideal_ratio = ideal_distribution.get(str(difficulty), 0.0)
            balance_score += 1.0 - abs(actual_ratio - ideal_ratio)
        
        return balance_score / len(ideal_distribution)
    
    def _calculate_addiction_risk(
        self, 
        gaming_activities: Dict[str, Any], 
        session_data: List[Dict[str, Any]]
    ) -> float:
        """?"""
        risk_factors = []
        
        # 1. ?
        daily_playtime = gaming_activities.get("daily_playtime_minutes", 0)
        if daily_playtime > 180:  # 3?
            risk_factors.append(0.3)
        
        # 2. ?
        session_frequency = len(session_data)
        if session_frequency > 10:  # 1?10?
            risk_factors.append(0.2)
        
        # 3. ?
        reality_avoidance_score = gaming_activities.get("reality_avoidance_indicators", 0)
        risk_factors.append(reality_avoidance_score * 0.3)
        
        # 4. ?
        social_isolation_score = gaming_activities.get("social_isolation_score", 0)
        risk_factors.append(social_isolation_score * 0.2)
        
        return min(1.0, sum(risk_factors))
    
    def _determine_balance_risk(
        self, 
        therapeutic_score: float, 
        gaming_score: float, 
        balance_ratio: float,
        addiction_risk: float
    ) -> BalanceRisk:
        """バリデーション"""
        
        # ?
        if (therapeutic_score < 0.3 or addiction_risk > 0.8 or balance_ratio < 0.3):
            return BalanceRisk.CRITICAL
        
        # ?
        if (therapeutic_score < 0.5 or addiction_risk > 0.6 or balance_ratio < 0.5):
            return BalanceRisk.HIGH
        
        # ?
        if (therapeutic_score < 0.7 or addiction_risk > 0.4 or balance_ratio < 0.7):
            return BalanceRisk.MODERATE
        
        return BalanceRisk.LOW
    
    def _generate_optimization_recommendations(
        self, 
        therapeutic_assessment: TherapeuticAssessment,
        gaming_assessment: GamingAssessment,
        balance_ratio: float
    ) -> List[str]:
        """?"""
        
        recommendations = []
        
        # 治療
        if therapeutic_assessment.overall_therapeutic_score < 0.6:
            recommendations.append("治療")
        
        # ゲーム
        if gaming_assessment.addiction_risk_score > 0.5:
            recommendations.append("ゲーム")
        
        # バリデーション
        if balance_ratio < 0.5:
            recommendations.append("治療")
        elif balance_ratio > 2.0:
            recommendations.append("エラー")
        
        # ?
        for area in therapeutic_assessment.improvement_areas:
            if "self_efficacy" in area:
                recommendations.append("自動")
            elif "social_engagement" in area:
                recommendations.append("?")
        
        return recommendations
    
    def _identify_addiction_warning_signs(self, gaming_assessment: GamingAssessment) -> List[str]:
        """?"""
        warning_signs = []
        
        if gaming_assessment.metrics[GamingMetric.ENGAGEMENT_LEVEL] > 0.9:
            warning_signs.append("?")
        
        if gaming_assessment.addiction_risk_score > 0.6:
            warning_signs.append("?")
        
        return warning_signs
    
    def _generate_safety_recommendations(self, safety_checks: Dict[str, Any]) -> List[str]:
        """安全"""
        recommendations = []
        
        if safety_checks["therapeutic_effectiveness"]["status"] == "at_risk":
            recommendations.append("治療")
        
        if safety_checks["gaming_addiction_risk"]["status"] == "at_risk":
            recommendations.append("ゲーム")
        
        if safety_checks["balance_stability"]["status"] == "unstable":
            recommendations.append("治療")
        
        return recommendations
    
    def _calculate_retention_score(self, user_id: str, daily_data: Dict[str, Any]) -> float:
        """?"""
        # ?
        consecutive_days = daily_data.get("consecutive_active_days", 0)
        return min(1.0, consecutive_days / 30.0)
    
    def _calculate_average_engagement(self, engagement_metrics: List[EngagementMetrics]) -> Dict[str, float]:
        """?"""
        if not engagement_metrics:
            return {}
        
        return {
            "avg_daily_active_time": statistics.mean([m.daily_active_time for m in engagement_metrics]),
            "avg_session_frequency": statistics.mean([m.session_frequency for m in engagement_metrics]),
            "avg_task_completion_rate": statistics.mean([m.task_completion_rate for m in engagement_metrics]),
            "avg_story_engagement_rate": statistics.mean([m.story_engagement_rate for m in engagement_metrics]),
            "avg_social_interaction_count": statistics.mean([m.social_interaction_count for m in engagement_metrics]),
            "avg_achievement_unlock_rate": statistics.mean([m.achievement_unlock_rate for m in engagement_metrics]),
            "avg_retention_score": statistics.mean([m.retention_score for m in engagement_metrics])
        }
    
    def _calculate_therapeutic_trend(self, user_id: str) -> str:
        """治療"""
        if user_id not in self.therapeutic_assessments or len(self.therapeutic_assessments[user_id]) < 2:
            return "insufficient_data"
        
        recent_scores = [a.overall_therapeutic_score for a in self.therapeutic_assessments[user_id][-5:]]
        if len(recent_scores) < 2:
            return "insufficient_data"
        
        trend = recent_scores[-1] - recent_scores[0]
        if trend > 0.1:
            return "improving"
        elif trend < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_gaming_trend(self, user_id: str) -> str:
        """ゲーム"""
        if user_id not in self.gaming_assessments or len(self.gaming_assessments[user_id]) < 2:
            return "insufficient_data"
        
        recent_scores = [a.overall_gaming_score for a in self.gaming_assessments[user_id][-5:]]
        if len(recent_scores) < 2:
            return "insufficient_data"
        
        trend = recent_scores[-1] - recent_scores[0]
        if trend > 0.1:
            return "increasing"
        elif trend < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_mood_recovery_rate(self, mood_logs: List[Dict[str, Any]]) -> float:
        """気分"""
        if len(mood_logs) < 3:
            return 0.5
        
        recovery_instances = 0
        total_low_moods = 0
        
        for i in range(1, len(mood_logs) - 1):
            current_mood = mood_logs[i].get("mood_score", 3)
            next_mood = mood_logs[i + 1].get("mood_score", 3)
            
            if current_mood <= 2:  # ?
                total_low_moods += 1
                if next_mood > current_mood:  # ?
                    recovery_instances += 1
        
        return recovery_instances / max(1, total_low_moods)


def main():
    """?"""
    balance_system = TherapeuticGamingBalanceSystem()
    
    # ?
    test_user = "balance_test_user"
    
    # ?
    user_activities = {
        "daily_playtime_minutes": 90,
        "session_count": 3,
        "task_completion_rate": 0.75,
        "story_engagement_rate": 0.8,
        "social_interactions": 5,
        "achievement_unlock_rate": 0.6,
        "consecutive_active_days": 15,
        "activity_level_stability": 0.7,
        "adhd_support_usage_rate": 0.8,
        "break_compliance_rate": 0.9,
        "social_isolation_score": 0.2,
        "reality_avoidance_indicators": 0.1
    }
    
    # ?
    mood_logs = [
        {"mood_score": 3, "date": "2024-01-01"},
        {"mood_score": 4, "date": "2024-01-02"},
        {"mood_score": 2, "date": "2024-01-03"},
        {"mood_score": 4, "date": "2024-01-04"},
        {"mood_score": 4, "date": "2024-01-05"}
    ]
    
    # ?
    task_history = [
        {"status": "completed", "difficulty": 2, "task_type": "routine", "estimated_duration": 30, "actual_duration": 25},
        {"status": "completed", "difficulty": 3, "task_type": "social", "estimated_duration": 45, "actual_duration": 40},
        {"status": "completed", "difficulty": 1, "task_type": "skill_up", "estimated_duration": 60, "actual_duration": 55},
        {"status": "pending", "difficulty": 4, "task_type": "one_shot", "estimated_duration": 90, "actual_duration": None}
    ]
    
    # ?
    session_data = [
        {"duration": 30, "flow_state": True},
        {"duration": 45, "flow_state": False},
        {"duration": 25, "flow_state": True}
    ]
    
    # 治療
    therapeutic_assessment = balance_system.assess_therapeutic_effectiveness(
        test_user, user_activities, mood_logs, task_history
    )
    
    print("治療:")
    print(f"  ?: {therapeutic_assessment.overall_therapeutic_score:.2f}")
    print(f"  ?: {len(therapeutic_assessment.strengths)}?")
    print(f"  ?: {len(therapeutic_assessment.improvement_areas)}?")
    
    # ゲーム
    gaming_assessment = balance_system.assess_gaming_engagement(
        test_user, user_activities, session_data
    )
    
    print(f"\nゲーム:")
    print(f"  ?: {gaming_assessment.overall_gaming_score:.2f}")
    print(f"  エラー: {gaming_assessment.engagement_quality}")
    print(f"  ?: {gaming_assessment.addiction_risk_score:.2f}")
    
    # バリデーション
    balance_analysis = balance_system.analyze_therapeutic_gaming_balance(
        test_user, therapeutic_assessment, gaming_assessment
    )
    
    print(f"\nバリデーション:")
    print(f"  バリデーション: {balance_analysis.balance_ratio:.2f}")
    print(f"  リスト: {balance_analysis.balance_risk.value}")
    print(f"  ?: {balance_analysis.intervention_needed}")
    
    # 安全
    safety_report = balance_system.verify_therapeutic_safety(test_user)
    print(f"\n安全:")
    print(f"  ?: {safety_report['overall_safety']}")
    
    # ?
    full_report = balance_system.generate_balance_report(test_user)
    print(f"\n?")
    print(f"  ?: {len(full_report['optimization_recommendations'])}?")


if __name__ == "__main__":
    main()