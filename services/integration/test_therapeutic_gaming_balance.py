"""
治療 - タスク20.2

治療
ユーザー
ゲーム

?: 14.1-14.5
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# プレビュー
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from therapeutic_gaming_balance import (
    TherapeuticGamingBalanceSystem, 
    TherapeuticMetric, 
    GamingMetric,
    BalanceRisk
)


class TherapeuticGamingBalanceTestSuite:
    """治療"""
    
    def __init__(self):
        self.balance_system = TherapeuticGamingBalanceSystem()
        self.test_user = "therapeutic_balance_test_user"
    
    def test_therapeutic_effectiveness_assessment(self) -> Dict[str, Any]:
        """治療"""
        print("\n? 治療...")
        
        result = {
            "test_name": "治療",
            "passed": True,
            "details": []
        }
        
        try:
            # ?
            user_activities = {
                "consecutive_active_days": 20,
                "activity_level_stability": 0.8,
                "adhd_support_usage_rate": 0.7,
                "break_compliance_rate": 0.85,
                "social_interactions": 8,
                "positive_social_feedback": 6
            }
            
            mood_logs = [
                {"mood_score": 3, "date": "2024-01-01"},
                {"mood_score": 4, "date": "2024-01-02"},
                {"mood_score": 4, "date": "2024-01-03"},
                {"mood_score": 3, "date": "2024-01-04"},
                {"mood_score": 4, "date": "2024-01-05"},
                {"mood_score": 5, "date": "2024-01-06"},
                {"mood_score": 4, "date": "2024-01-07"}
            ]
            
            task_history = [
                {"status": "completed", "difficulty": 2, "task_type": "routine", "estimated_duration": 30, "actual_duration": 25},
                {"status": "completed", "difficulty": 3, "task_type": "social", "estimated_duration": 45, "actual_duration": 40},
                {"status": "completed", "difficulty": 3, "task_type": "skill_up", "estimated_duration": 60, "actual_duration": 55},
                {"status": "completed", "difficulty": 2, "task_type": "routine", "estimated_duration": 20, "actual_duration": 18},
                {"status": "completed", "difficulty": 4, "task_type": "social", "estimated_duration": 90, "actual_duration": 85}
            ]
            
            # 治療
            assessment = self.balance_system.assess_therapeutic_effectiveness(
                self.test_user, user_activities, mood_logs, task_history
            )
            
            # ?
            assert 0.0 <= assessment.overall_therapeutic_score <= 1.0, "治療"
            assert len(assessment.metrics) == len(TherapeuticMetric), "治療"
            
            # ?
            for metric, score in assessment.metrics.items():
                assert 0.0 <= score <= 1.0, f"{metric.value}の: {score}"
            
            result["details"].append({
                "step": "治療",
                "overall_score": assessment.overall_therapeutic_score,
                "metrics_count": len(assessment.metrics),
                "strengths_count": len(assessment.strengths),
                "improvement_areas_count": len(assessment.improvement_areas),
                "risk_factors_count": len(assessment.risk_factors)
            })
            
            # ?
            self_efficacy_score = assessment.metrics[TherapeuticMetric.SELF_EFFICACY]
            mood_stability_score = assessment.metrics[TherapeuticMetric.MOOD_STABILITY]
            
            result["details"].append({
                "step": "?",
                "self_efficacy": self_efficacy_score,
                "mood_stability": mood_stability_score,
                "task_completion_confidence": assessment.metrics[TherapeuticMetric.TASK_COMPLETION_CONFIDENCE]
            })
            
            print("? 治療")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? 治療: {e}")
        
        return result
    
    def test_gaming_engagement_assessment(self) -> Dict[str, Any]:
        """ゲーム"""
        print("\n? ゲーム...")
        
        result = {
            "test_name": "ゲーム",
            "passed": True,
            "details": []
        }
        
        try:
            # ?
            gaming_activities = {
                "daily_playtime_minutes": 75,
                "level_progression_rate": 0.8,
                "achievement_unlock_rate": 0.6,
                "task_difficulty_distribution": {"1": 2, "2": 5, "3": 4, "4": 1, "5": 0},
                "reward_satisfaction_score": 0.8,
                "reward_usage_rate": 0.7,
                "social_interactions_count": 6,
                "community_participation_rate": 0.5,
                "goal_setting_frequency": 0.7,
                "goal_achievement_rate": 0.75,
                "flow_state_sessions": 2,
                "reality_avoidance_indicators": 0.1,
                "social_isolation_score": 0.2
            }
            
            session_data = [
                {"duration": 25, "flow_state": True},
                {"duration": 30, "flow_state": False},
                {"duration": 20, "flow_state": True},
                {"duration": 35, "flow_state": False}
            ]
            
            # ゲーム
            assessment = self.balance_system.assess_gaming_engagement(
                self.test_user, gaming_activities, session_data
            )
            
            # ?
            assert 0.0 <= assessment.overall_gaming_score <= 1.0, "ゲーム"
            assert len(assessment.metrics) == len(GamingMetric), "ゲーム"
            assert assessment.engagement_quality in ["low", "moderate", "good", "excellent"], "エラー"
            assert 0.0 <= assessment.addiction_risk_score <= 1.0, "?"
            
            # ?
            for metric, score in assessment.metrics.items():
                assert 0.0 <= score <= 1.0, f"{metric.value}の: {score}"
            
            result["details"].append({
                "step": "ゲーム",
                "overall_score": assessment.overall_gaming_score,
                "engagement_quality": assessment.engagement_quality,
                "addiction_risk": assessment.addiction_risk_score,
                "healthy_indicators_count": len(assessment.healthy_gaming_indicators)
            })
            
            # ?
            engagement_level = assessment.metrics[GamingMetric.ENGAGEMENT_LEVEL]
            progression_satisfaction = assessment.metrics[GamingMetric.PROGRESSION_SATISFACTION]
            
            result["details"].append({
                "step": "?",
                "engagement_level": engagement_level,
                "progression_satisfaction": progression_satisfaction,
                "challenge_balance": assessment.metrics[GamingMetric.CHALLENGE_BALANCE],
                "addiction_risk_acceptable": assessment.addiction_risk_score <= 0.5
            })
            
            print("? ゲーム")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? ゲーム: {e}")
        
        return result
    
    def test_therapeutic_gaming_balance_analysis(self) -> Dict[str, Any]:
        """治療"""
        print("\n? 治療...")
        
        result = {
            "test_name": "治療",
            "passed": True,
            "details": []
        }
        
        try:
            # ?
            user_activities = {
                "consecutive_active_days": 15,
                "activity_level_stability": 0.75,
                "adhd_support_usage_rate": 0.8,
                "break_compliance_rate": 0.9,
                "social_interactions": 5,
                "positive_social_feedback": 4
            }
            
            mood_logs = [{"mood_score": 4, "date": f"2024-01-0{i}"} for i in range(1, 8)]
            task_history = [
                {"status": "completed", "difficulty": 3, "task_type": "routine", "estimated_duration": 30, "actual_duration": 28}
                for _ in range(5)
            ]
            
            gaming_activities = {
                "daily_playtime_minutes": 60,
                "level_progression_rate": 0.7,
                "achievement_unlock_rate": 0.65,
                "task_difficulty_distribution": {"2": 3, "3": 4, "4": 2},
                "reward_satisfaction_score": 0.8,
                "reward_usage_rate": 0.75,
                "social_interactions_count": 5,
                "community_participation_rate": 0.4,
                "goal_setting_frequency": 0.6,
                "goal_achievement_rate": 0.7,
                "flow_state_sessions": 1,
                "reality_avoidance_indicators": 0.15,
                "social_isolation_score": 0.25
            }
            
            session_data = [{"duration": 30, "flow_state": True}, {"duration": 30, "flow_state": False}]
            
            # ?
            therapeutic_assessment = self.balance_system.assess_therapeutic_effectiveness(
                self.test_user, user_activities, mood_logs, task_history
            )
            
            gaming_assessment = self.balance_system.assess_gaming_engagement(
                self.test_user, gaming_activities, session_data
            )
            
            # バリデーション
            balance_analysis = self.balance_system.analyze_therapeutic_gaming_balance(
                self.test_user, therapeutic_assessment, gaming_assessment
            )
            
            # バリデーション
            assert balance_analysis.balance_ratio > 0, "バリデーション"
            assert balance_analysis.balance_risk in [risk for risk in BalanceRisk], "バリデーション"
            assert isinstance(balance_analysis.intervention_needed, bool), "?"
            assert isinstance(balance_analysis.optimization_recommendations, list), "?"
            
            result["details"].append({
                "step": "バリデーション",
                "therapeutic_score": balance_analysis.therapeutic_score,
                "gaming_score": balance_analysis.gaming_score,
                "balance_ratio": balance_analysis.balance_ratio,
                "balance_risk": balance_analysis.balance_risk.value,
                "intervention_needed": balance_analysis.intervention_needed,
                "recommendations_count": len(balance_analysis.optimization_recommendations)
            })
            
            # バリデーション
            balance_quality = "good"
            if balance_analysis.balance_risk in [BalanceRisk.HIGH, BalanceRisk.CRITICAL]:
                balance_quality = "poor"
            elif balance_analysis.balance_risk == BalanceRisk.MODERATE:
                balance_quality = "moderate"
            
            result["details"].append({
                "step": "バリデーション",
                "balance_quality": balance_quality,
                "therapeutic_effectiveness": "good" if therapeutic_assessment.overall_therapeutic_score >= 0.6 else "needs_improvement",
                "gaming_healthiness": "healthy" if gaming_assessment.addiction_risk_score <= 0.5 else "at_risk"
            })
            
            print("? 治療")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? 治療: {e}")
        
        return result
    
    def test_engagement_metrics_monitoring(self) -> Dict[str, Any]:
        """エラー"""
        print("\n? エラー...")
        
        result = {
            "test_name": "エラー",
            "passed": True,
            "details": []
        }
        
        try:
            # 7?
            daily_metrics = []
            
            for day in range(1, 8):
                daily_data = {
                    "active_time_minutes": 60 + (day * 5),
                    "session_count": 2 + (day % 3),
                    "task_completion_rate": 0.7 + (day * 0.02),
                    "story_engagement_rate": 0.6 + (day * 0.03),
                    "social_interactions": 3 + (day % 4),
                    "achievement_unlock_rate": 0.5 + (day * 0.04),
                    "consecutive_active_days": day
                }
                
                metrics = self.balance_system.monitor_engagement_metrics(
                    self.test_user, daily_data
                )
                daily_metrics.append(metrics)
                
                # ?
                assert metrics.daily_active_time >= 0, "アプリ"
                assert metrics.session_frequency >= 0, "?"
                assert 0.0 <= metrics.task_completion_rate <= 1.0, "タスク"
                assert 0.0 <= metrics.story_engagement_rate <= 1.0, "ストーリー"
                assert metrics.social_interaction_count >= 0, "?"
                assert 0.0 <= metrics.achievement_unlock_rate <= 1.0, "?"
                assert 0.0 <= metrics.retention_score <= 1.0, "?"
            
            result["details"].append({
                "step": "7?",
                "monitored_days": len(daily_metrics),
                "avg_active_time": sum(m.daily_active_time for m in daily_metrics) / len(daily_metrics),
                "avg_task_completion": sum(m.task_completion_rate for m in daily_metrics) / len(daily_metrics),
                "final_retention_score": daily_metrics[-1].retention_score
            })
            
            # ?
            active_time_trend = daily_metrics[-1].daily_active_time - daily_metrics[0].daily_active_time
            completion_trend = daily_metrics[-1].task_completion_rate - daily_metrics[0].task_completion_rate
            
            result["details"].append({
                "step": "エラー",
                "active_time_trend": active_time_trend,
                "completion_rate_trend": completion_trend,
                "trend_direction": "improving" if completion_trend > 0 else "stable"
            })
            
            print("? エラー")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? エラー: {e}")
        
        return result
    
    def test_therapeutic_safety_verification(self) -> Dict[str, Any]:
        """治療"""
        print("\n? 治療...")
        
        result = {
            "test_name": "治療",
            "passed": True,
            "details": []
        }
        
        try:
            # 安全
            # ?
            healthy_user_activities = {
                "consecutive_active_days": 25,
                "activity_level_stability": 0.85,
                "adhd_support_usage_rate": 0.8,
                "break_compliance_rate": 0.9,
                "social_interactions": 8,
                "positive_social_feedback": 7
            }
            
            healthy_mood_logs = [{"mood_score": 4, "date": f"2024-01-0{i}"} for i in range(1, 8)]
            healthy_task_history = [
                {"status": "completed", "difficulty": 3, "task_type": "routine", "estimated_duration": 30, "actual_duration": 25}
                for _ in range(8)
            ]
            
            healthy_gaming_activities = {
                "daily_playtime_minutes": 45,  # ?
                "level_progression_rate": 0.75,
                "achievement_unlock_rate": 0.7,
                "task_difficulty_distribution": {"2": 2, "3": 5, "4": 2},
                "reward_satisfaction_score": 0.85,
                "reward_usage_rate": 0.8,
                "social_interactions_count": 6,
                "community_participation_rate": 0.5,
                "goal_setting_frequency": 0.7,
                "goal_achievement_rate": 0.8,
                "flow_state_sessions": 2,
                "reality_avoidance_indicators": 0.1,  # ?
                "social_isolation_score": 0.15  # ?
            }
            
            healthy_session_data = [
                {"duration": 25, "flow_state": True},
                {"duration": 20, "flow_state": False}
            ]
            
            # ?
            therapeutic_assessment = self.balance_system.assess_therapeutic_effectiveness(
                self.test_user, healthy_user_activities, healthy_mood_logs, healthy_task_history
            )
            
            gaming_assessment = self.balance_system.assess_gaming_engagement(
                self.test_user, healthy_gaming_activities, healthy_session_data
            )
            
            balance_analysis = self.balance_system.analyze_therapeutic_gaming_balance(
                self.test_user, therapeutic_assessment, gaming_assessment
            )
            
            # 安全
            safety_report = self.balance_system.verify_therapeutic_safety(self.test_user)
            
            # 安全
            assert "overall_safety" in safety_report, "?"
            assert "safety_checks" in safety_report, "安全"
            assert "recommendations" in safety_report, "?"
            
            assert safety_report["overall_safety"] in ["safe", "needs_attention", "critical"], "安全"
            
            safety_checks = safety_report["safety_checks"]
            assert "therapeutic_effectiveness" in safety_checks, "治療"
            assert "gaming_addiction_risk" in safety_checks, "ゲーム"
            assert "balance_stability" in safety_checks, "バリデーション"
            
            result["details"].append({
                "step": "?",
                "overall_safety": safety_report["overall_safety"],
                "therapeutic_status": safety_checks["therapeutic_effectiveness"]["status"],
                "addiction_risk_status": safety_checks["gaming_addiction_risk"]["status"],
                "balance_status": safety_checks["balance_stability"]["status"],
                "recommendations_count": len(safety_report["recommendations"])
            })
            
            # リスト
            risky_gaming_activities = healthy_gaming_activities.copy()
            risky_gaming_activities.update({
                "daily_playtime_minutes": 200,  # ?
                "reality_avoidance_indicators": 0.8,  # ?
                "social_isolation_score": 0.7  # ?
            })
            
            risky_gaming_assessment = self.balance_system.assess_gaming_engagement(
                f"{self.test_user}_risky", risky_gaming_activities, healthy_session_data * 5
            )
            
            risky_balance_analysis = self.balance_system.analyze_therapeutic_gaming_balance(
                f"{self.test_user}_risky", therapeutic_assessment, risky_gaming_assessment
            )
            
            risky_safety_report = self.balance_system.verify_therapeutic_safety(f"{self.test_user}_risky")
            
            result["details"].append({
                "step": "リスト",
                "overall_safety": risky_safety_report["overall_safety"],
                "addiction_risk_detected": risky_gaming_assessment.addiction_risk_score > 0.5,
                "intervention_recommended": risky_balance_analysis.intervention_needed,
                "safety_degraded": risky_safety_report["overall_safety"] != "safe"
            })
            
            print("? 治療")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? 治療: {e}")
        
        return result
    
    def test_balance_optimization_recommendations(self) -> Dict[str, Any]:
        """バリデーション"""
        print("\n? バリデーション...")
        
        result = {
            "test_name": "バリデーション",
            "passed": True,
            "details": []
        }
        
        try:
            # ?
            test_scenarios = [
                {
                    "name": "治療",
                    "therapeutic_score": 0.3,
                    "gaming_score": 0.8,
                    "addiction_risk": 0.2
                },
                {
                    "name": "ゲーム",
                    "therapeutic_score": 0.7,
                    "gaming_score": 0.9,
                    "addiction_risk": 0.8
                },
                {
                    "name": "バリデーション",
                    "therapeutic_score": 0.8,
                    "gaming_score": 0.7,
                    "addiction_risk": 0.2
                }
            ]
            
            scenario_results = []
            
            for scenario in test_scenarios:
                # システム
                user_activities = {
                    "consecutive_active_days": 10 if scenario["therapeutic_score"] < 0.5 else 20,
                    "activity_level_stability": scenario["therapeutic_score"],
                    "adhd_support_usage_rate": scenario["therapeutic_score"],
                    "break_compliance_rate": scenario["therapeutic_score"],
                    "social_interactions": int(scenario["therapeutic_score"] * 10),
                    "positive_social_feedback": int(scenario["therapeutic_score"] * 8)
                }
                
                gaming_activities = {
                    "daily_playtime_minutes": int(scenario["gaming_score"] * 120 + scenario["addiction_risk"] * 100),
                    "level_progression_rate": scenario["gaming_score"],
                    "achievement_unlock_rate": scenario["gaming_score"],
                    "task_difficulty_distribution": {"2": 3, "3": 4, "4": 2},
                    "reward_satisfaction_score": scenario["gaming_score"],
                    "reward_usage_rate": scenario["gaming_score"],
                    "social_interactions_count": int(scenario["gaming_score"] * 8),
                    "community_participation_rate": scenario["gaming_score"] * 0.6,
                    "goal_setting_frequency": scenario["gaming_score"],
                    "goal_achievement_rate": scenario["gaming_score"],
                    "flow_state_sessions": int(scenario["gaming_score"] * 3),
                    "reality_avoidance_indicators": scenario["addiction_risk"],
                    "social_isolation_score": scenario["addiction_risk"]
                }
                
                # ?
                mood_logs = [{"mood_score": int(scenario["therapeutic_score"] * 3 + 2), "date": f"2024-01-0{i}"} for i in range(1, 8)]
                task_history = [
                    {"status": "completed" if scenario["therapeutic_score"] > 0.5 else "pending", 
                     "difficulty": 2, "task_type": "routine", "estimated_duration": 30, "actual_duration": 28}
                    for _ in range(5)
                ]
                session_data = [{"duration": 30, "flow_state": True}] * int(scenario["gaming_score"] * 4)
                
                test_user_scenario = f"{self.test_user}_{scenario['name']}"
                
                therapeutic_assessment = self.balance_system.assess_therapeutic_effectiveness(
                    test_user_scenario, user_activities, mood_logs, task_history
                )
                
                gaming_assessment = self.balance_system.assess_gaming_engagement(
                    test_user_scenario, gaming_activities, session_data
                )
                
                balance_analysis = self.balance_system.analyze_therapeutic_gaming_balance(
                    test_user_scenario, therapeutic_assessment, gaming_assessment
                )
                
                # ?
                recommendations = balance_analysis.optimization_recommendations
                assert isinstance(recommendations, list), "?"
                
                # システム
                if scenario["therapeutic_score"] < 0.5:
                    assert any("治療" in rec for rec in recommendations), "治療"
                
                if scenario["addiction_risk"] > 0.6:
                    assert any("?" in rec or "?" in rec for rec in recommendations), "?"
                
                scenario_results.append({
                    "scenario": scenario["name"],
                    "therapeutic_score": therapeutic_assessment.overall_therapeutic_score,
                    "gaming_score": gaming_assessment.overall_gaming_score,
                    "balance_risk": balance_analysis.balance_risk.value,
                    "recommendations_count": len(recommendations),
                    "intervention_needed": balance_analysis.intervention_needed
                })
            
            result["details"].append({
                "step": "システム",
                "scenarios_tested": len(scenario_results),
                "scenario_results": scenario_results
            })
            
            # ?
            total_recommendations = sum(sr["recommendations_count"] for sr in scenario_results)
            interventions_needed = sum(1 for sr in scenario_results if sr["intervention_needed"])
            
            result["details"].append({
                "step": "?",
                "total_recommendations": total_recommendations,
                "interventions_needed": interventions_needed,
                "avg_recommendations_per_scenario": total_recommendations / len(scenario_results)
            })
            
            print("? バリデーション")
            
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
            print(f"? バリデーション: {e}")
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """?"""
        print("? 治療")
        print("=" * 70)
        
        test_results = {
            "test_suite": "治療",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
        # ?
        tests = [
            self.test_therapeutic_effectiveness_assessment,
            self.test_gaming_engagement_assessment,
            self.test_therapeutic_gaming_balance_analysis,
            self.test_engagement_metrics_monitoring,
            self.test_therapeutic_safety_verification,
            self.test_balance_optimization_recommendations
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                test_results["tests"].append(result)
                
                if result["passed"]:
                    test_results["summary"]["passed_tests"] += 1
                else:
                    test_results["summary"]["failed_tests"] += 1
                    
            except Exception as e:
                test_results["tests"].append({
                    "test_name": test_func.__name__,
                    "passed": False,
                    "error": f"?: {str(e)}"
                })
                test_results["summary"]["failed_tests"] += 1
        
        # ?
        test_results["summary"]["total_tests"] = len(tests)
        if test_results["summary"]["total_tests"] > 0:
            test_results["summary"]["success_rate"] = (
                test_results["summary"]["passed_tests"] / test_results["summary"]["total_tests"]
            ) * 100
        
        # ?
        print("\n" + "=" * 70)
        print("? 治療")
        print("=" * 70)
        print(f"?: {test_results['summary']['total_tests']}")
        print(f"成: {test_results['summary']['passed_tests']}")
        print(f"?: {test_results['summary']['failed_tests']}")
        print(f"成: {test_results['summary']['success_rate']:.1f}%")
        
        if test_results["summary"]["success_rate"] == 100.0:
            print("? ?")
        else:
            print("?  一般")
        
        return test_results


def main():
    """メイン"""
    test_suite = TherapeuticGamingBalanceTestSuite()
    results = test_suite.run_all_tests()
    
    # ?JSON?
    output_file = "therapeutic_gaming_balance_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n? ? {output_file} に")
    
    # 実装
    if results["summary"]["success_rate"] == 100.0:
        print("\n? タスク20.2実装:")
        print("   - 治療")
        print("   - ユーザー")
        print("   - ゲーム")
        print("   - 治療")
        print("   - バリデーション")
        
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()