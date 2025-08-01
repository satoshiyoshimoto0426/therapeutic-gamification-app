"""
? - タスク20.1

RPG?
ゲーム

?: 11.1-11.5, 12.1-12.5, 13.1-13.5
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
import statistics
import sys
import os

# プレビュー
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.rpg_economy.main import CoinEconomy, ActionType, DemonRarity
from services.job_system.main import JobManager, JobType
from services.inner_demon_battle.main import InnerDemonBattle, DemonType
from shared.interfaces.core_types import TaskType


class EconomicTier(Enum):
    """?"""
    STARTING = "starting"      # 0-999コア
    STABLE = "stable"          # 1,000-4,999コア
    COMFORTABLE = "comfortable" # 5,000-9,999コア
    WEALTHY = "wealthy"        # 10,000+コア


class BalanceMetric(Enum):
    """バリデーション"""
    COIN_INFLATION = "coin_inflation"
    XP_PROGRESSION = "xp_progression"
    TASK_DIFFICULTY = "task_difficulty"
    BATTLE_REWARDS = "battle_rewards"
    JOB_PROGRESSION = "job_progression"


@dataclass
class EconomicSnapshot:
    """?"""
    timestamp: datetime
    user_id: str
    total_coins: int
    economic_tier: EconomicTier
    inflation_adjustment: float
    daily_coin_income: int
    weekly_coin_income: int
    coin_spending_rate: float
    balance_score: float  # 0.0-1.0


@dataclass
class ProgressionMetrics:
    """?"""
    player_level: int
    yu_level: int
    job_level: int
    job_type: JobType
    total_xp: int
    daily_xp_rate: float
    weekly_xp_rate: float
    task_completion_rate: float
    battle_win_rate: float
    progression_velocity: float  # ?


@dataclass
class BalanceAdjustment:
    """バリデーション"""
    metric: BalanceMetric
    current_value: float
    target_value: float
    adjustment_factor: float
    reason: str
    applied_at: datetime


class EconomicBalanceSystem:
    """?"""
    
    def __init__(self):
        self.coin_economy = CoinEconomy()
        self.user_snapshots: Dict[str, List[EconomicSnapshot]] = {}
        self.user_progressions: Dict[str, List[ProgressionMetrics]] = {}
        self.balance_adjustments: Dict[str, List[BalanceAdjustment]] = {}
        
        # バリデーション
        self.target_metrics = {
            "daily_coin_income": {"min": 200, "max": 800, "optimal": 400},
            "weekly_coin_income": {"min": 1400, "max": 5600, "optimal": 2800},
            "coin_spending_rate": {"min": 0.6, "max": 0.9, "optimal": 0.75},
            "daily_xp_rate": {"min": 100, "max": 500, "optimal": 250},
            "task_completion_rate": {"min": 0.6, "max": 0.9, "optimal": 0.75},
            "battle_win_rate": {"min": 0.5, "max": 0.8, "optimal": 0.65}
        }
    
    def capture_economic_snapshot(
        self, 
        user_id: str, 
        total_coins: int,
        daily_activities: Dict[str, Any]
    ) -> EconomicSnapshot:
        """?"""
        
        # ?
        economic_tier = self._determine_economic_tier(total_coins)
        
        # ?
        inflation_adjustment = self.coin_economy.apply_inflation_control(total_coins)
        
        # ?
        daily_coin_income = daily_activities.get("coins_earned", 0)
        
        # ?
        weekly_coin_income = self._calculate_weekly_income(user_id, daily_coin_income)
        
        # 支援
        coin_spending_rate = self._calculate_spending_rate(user_id, daily_activities)
        
        # バリデーション
        balance_score = self._calculate_balance_score(
            total_coins, daily_coin_income, weekly_coin_income, coin_spending_rate
        )
        
        snapshot = EconomicSnapshot(
            timestamp=datetime.now(),
            user_id=user_id,
            total_coins=total_coins,
            economic_tier=economic_tier,
            inflation_adjustment=inflation_adjustment,
            daily_coin_income=daily_coin_income,
            weekly_coin_income=weekly_coin_income,
            coin_spending_rate=coin_spending_rate,
            balance_score=balance_score
        )
        
        # ストーリー
        if user_id not in self.user_snapshots:
            self.user_snapshots[user_id] = []
        self.user_snapshots[user_id].append(snapshot)
        
        # ?30?
        cutoff_date = datetime.now() - timedelta(days=30)
        self.user_snapshots[user_id] = [
            s for s in self.user_snapshots[user_id] 
            if s.timestamp >= cutoff_date
        ]
        
        return snapshot
    
    def capture_progression_metrics(
        self,
        user_id: str,
        player_level: int,
        yu_level: int,
        job_level: int,
        job_type: JobType,
        total_xp: int,
        daily_activities: Dict[str, Any]
    ) -> ProgressionMetrics:
        """?"""
        
        # XP?
        daily_xp_rate = daily_activities.get("xp_earned", 0)
        weekly_xp_rate = self._calculate_weekly_xp_rate(user_id, daily_xp_rate)
        
        # ?
        task_completion_rate = self._calculate_task_completion_rate(user_id, daily_activities)
        battle_win_rate = self._calculate_battle_win_rate(user_id, daily_activities)
        
        # ?
        progression_velocity = self._calculate_progression_velocity(
            user_id, player_level, job_level, total_xp
        )
        
        metrics = ProgressionMetrics(
            player_level=player_level,
            yu_level=yu_level,
            job_level=job_level,
            job_type=job_type,
            total_xp=total_xp,
            daily_xp_rate=daily_xp_rate,
            weekly_xp_rate=weekly_xp_rate,
            task_completion_rate=task_completion_rate,
            battle_win_rate=battle_win_rate,
            progression_velocity=progression_velocity
        )
        
        # ?
        if user_id not in self.user_progressions:
            self.user_progressions[user_id] = []
        self.user_progressions[user_id].append(metrics)
        
        # ?30?
        cutoff_date = datetime.now() - timedelta(days=30)
        self.user_progressions[user_id] = [
            m for m in self.user_progressions[user_id] 
            if hasattr(m, 'timestamp') or True  # ?
        ]
        
        return metrics
    
    def analyze_balance_needs(self, user_id: str) -> List[BalanceAdjustment]:
        """バリデーション"""
        
        if user_id not in self.user_snapshots or user_id not in self.user_progressions:
            return []
        
        recent_snapshots = self.user_snapshots[user_id][-7:]  # ?7?
        recent_progressions = self.user_progressions[user_id][-7:]  # ?7?
        
        if not recent_snapshots or not recent_progressions:
            return []
        
        adjustments = []
        
        # 1. コア
        avg_daily_income = statistics.mean([s.daily_coin_income for s in recent_snapshots])
        target_income = self.target_metrics["daily_coin_income"]
        
        if avg_daily_income < target_income["min"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.COIN_INFLATION,
                current_value=avg_daily_income,
                target_value=target_income["optimal"],
                adjustment_factor=1.2,  # 20%?
                reason="?",
                applied_at=datetime.now()
            ))
        elif avg_daily_income > target_income["max"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.COIN_INFLATION,
                current_value=avg_daily_income,
                target_value=target_income["optimal"],
                adjustment_factor=0.8,  # 20%?
                reason="?",
                applied_at=datetime.now()
            ))
        
        # 2. XP?
        avg_daily_xp = statistics.mean([p.daily_xp_rate for p in recent_progressions])
        target_xp = self.target_metrics["daily_xp_rate"]
        
        if avg_daily_xp < target_xp["min"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.XP_PROGRESSION,
                current_value=avg_daily_xp,
                target_value=target_xp["optimal"],
                adjustment_factor=1.15,  # 15%?
                reason="?XP?",
                applied_at=datetime.now()
            ))
        elif avg_daily_xp > target_xp["max"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.XP_PROGRESSION,
                current_value=avg_daily_xp,
                target_value=target_xp["optimal"],
                adjustment_factor=0.85,  # 15%?
                reason="?XP?",
                applied_at=datetime.now()
            ))
        
        # 3. タスク
        avg_completion_rate = statistics.mean([p.task_completion_rate for p in recent_progressions])
        target_completion = self.target_metrics["task_completion_rate"]
        
        if avg_completion_rate < target_completion["min"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.TASK_DIFFICULTY,
                current_value=avg_completion_rate,
                target_value=target_completion["optimal"],
                adjustment_factor=0.9,  # ?10%?
                reason="タスク",
                applied_at=datetime.now()
            ))
        elif avg_completion_rate > target_completion["max"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.TASK_DIFFICULTY,
                current_value=avg_completion_rate,
                target_value=target_completion["optimal"],
                adjustment_factor=1.1,  # ?10%?
                reason="タスク",
                applied_at=datetime.now()
            ))
        
        # 4. バリデーション
        avg_battle_win_rate = statistics.mean([p.battle_win_rate for p in recent_progressions])
        target_battle = self.target_metrics["battle_win_rate"]
        
        if avg_battle_win_rate < target_battle["min"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.BATTLE_REWARDS,
                current_value=avg_battle_win_rate,
                target_value=target_battle["optimal"],
                adjustment_factor=0.9,  # バリデーション10%?
                reason="バリデーション",
                applied_at=datetime.now()
            ))
        elif avg_battle_win_rate > target_battle["max"]:
            adjustments.append(BalanceAdjustment(
                metric=BalanceMetric.BATTLE_REWARDS,
                current_value=avg_battle_win_rate,
                target_value=target_battle["optimal"],
                adjustment_factor=1.1,  # バリデーション10%?
                reason="バリデーション",
                applied_at=datetime.now()
            ))
        
        # ?
        if user_id not in self.balance_adjustments:
            self.balance_adjustments[user_id] = []
        self.balance_adjustments[user_id].extend(adjustments)
        
        return adjustments
    
    def apply_dynamic_adjustments(
        self, 
        user_id: str, 
        adjustments: List[BalanceAdjustment]
    ) -> Dict[str, Any]:
        """?"""
        
        applied_adjustments = {
            "coin_multipliers": {},
            "xp_multipliers": {},
            "difficulty_adjustments": {},
            "battle_adjustments": {}
        }
        
        for adjustment in adjustments:
            if adjustment.metric == BalanceMetric.COIN_INFLATION:
                applied_adjustments["coin_multipliers"]["global"] = adjustment.adjustment_factor
                
            elif adjustment.metric == BalanceMetric.XP_PROGRESSION:
                applied_adjustments["xp_multipliers"]["global"] = adjustment.adjustment_factor
                
            elif adjustment.metric == BalanceMetric.TASK_DIFFICULTY:
                applied_adjustments["difficulty_adjustments"]["task_difficulty"] = adjustment.adjustment_factor
                
            elif adjustment.metric == BalanceMetric.BATTLE_REWARDS:
                applied_adjustments["battle_adjustments"]["demon_hp"] = adjustment.adjustment_factor
                applied_adjustments["battle_adjustments"]["reward_multiplier"] = 2.0 - adjustment.adjustment_factor
        
        return applied_adjustments
    
    def get_balance_report(self, user_id: str) -> Dict[str, Any]:
        """バリデーション"""
        
        if user_id not in self.user_snapshots or user_id not in self.user_progressions:
            return {"error": "ユーザー"}
        
        recent_snapshots = self.user_snapshots[user_id][-7:]
        recent_progressions = self.user_progressions[user_id][-7:]
        recent_adjustments = self.balance_adjustments.get(user_id, [])[-10:]
        
        # ?
        current_snapshot = recent_snapshots[-1] if recent_snapshots else None
        current_progression = recent_progressions[-1] if recent_progressions else None
        
        # ?
        avg_metrics = {}
        if recent_snapshots:
            avg_metrics.update({
                "avg_daily_coins": statistics.mean([s.daily_coin_income for s in recent_snapshots]),
                "avg_balance_score": statistics.mean([s.balance_score for s in recent_snapshots]),
                "avg_inflation_adjustment": statistics.mean([s.inflation_adjustment for s in recent_snapshots])
            })
        
        if recent_progressions:
            avg_metrics.update({
                "avg_daily_xp": statistics.mean([p.daily_xp_rate for p in recent_progressions]),
                "avg_task_completion": statistics.mean([p.task_completion_rate for p in recent_progressions]),
                "avg_battle_win_rate": statistics.mean([p.battle_win_rate for p in recent_progressions]),
                "avg_progression_velocity": statistics.mean([p.progression_velocity for p in recent_progressions])
            })
        
        # バリデーション
        balance_evaluation = self._evaluate_overall_balance(avg_metrics)
        
        return {
            "user_id": user_id,
            "report_timestamp": datetime.now().isoformat(),
            "current_state": {
                "economic_snapshot": current_snapshot.__dict__ if current_snapshot else None,
                "progression_metrics": current_progression.__dict__ if current_progression else None
            },
            "average_metrics": avg_metrics,
            "balance_evaluation": balance_evaluation,
            "recent_adjustments": [adj.__dict__ for adj in recent_adjustments],
            "recommendations": self._generate_balance_recommendations(user_id, avg_metrics)
        }
    
    def _determine_economic_tier(self, total_coins: int) -> EconomicTier:
        """?"""
        if total_coins >= 10000:
            return EconomicTier.WEALTHY
        elif total_coins >= 5000:
            return EconomicTier.COMFORTABLE
        elif total_coins >= 1000:
            return EconomicTier.STABLE
        else:
            return EconomicTier.STARTING
    
    def _calculate_weekly_income(self, user_id: str, daily_income: int) -> int:
        """?"""
        if user_id not in self.user_snapshots:
            return daily_income * 7
        
        recent_snapshots = self.user_snapshots[user_id][-7:]
        if len(recent_snapshots) < 7:
            return daily_income * 7
        
        return sum(s.daily_coin_income for s in recent_snapshots)
    
    def _calculate_spending_rate(self, user_id: str, daily_activities: Dict[str, Any]) -> float:
        """支援"""
        coins_spent = daily_activities.get("coins_spent", 0)
        coins_earned = daily_activities.get("coins_earned", 1)
        
        if coins_earned == 0:
            return 0.0
        
        return min(1.0, coins_spent / coins_earned)
    
    def _calculate_balance_score(
        self, 
        total_coins: int, 
        daily_income: int, 
        weekly_income: int, 
        spending_rate: float
    ) -> float:
        """バリデーション0.0-1.0?"""
        
        # ?
        coin_score = min(1.0, total_coins / 10000)  # 10,000コア
        income_score = min(1.0, daily_income / 400)  # 400コア/?
        weekly_score = min(1.0, weekly_income / 2800)  # 2,800コア/?
        spending_score = 1.0 - abs(spending_rate - 0.75)  # 75%支援
        
        # ?
        weights = [0.3, 0.3, 0.2, 0.2]
        scores = [coin_score, income_score, weekly_score, spending_score]
        
        return sum(w * s for w, s in zip(weights, scores))
    
    def _calculate_weekly_xp_rate(self, user_id: str, daily_xp: float) -> float:
        """?XP?"""
        if user_id not in self.user_progressions:
            return daily_xp * 7
        
        recent_progressions = self.user_progressions[user_id][-7:]
        if len(recent_progressions) < 7:
            return daily_xp * 7
        
        return sum(p.daily_xp_rate for p in recent_progressions)
    
    def _calculate_task_completion_rate(self, user_id: str, daily_activities: Dict[str, Any]) -> float:
        """タスク"""
        tasks_completed = daily_activities.get("tasks_completed", 0)
        tasks_created = daily_activities.get("tasks_created", 1)
        
        return min(1.0, tasks_completed / tasks_created)
    
    def _calculate_battle_win_rate(self, user_id: str, daily_activities: Dict[str, Any]) -> float:
        """バリデーション"""
        battles_won = daily_activities.get("battles_won", 0)
        battles_fought = daily_activities.get("battles_fought", 1)
        
        return battles_won / battles_fought if battles_fought > 0 else 0.0
    
    def _calculate_progression_velocity(
        self, 
        user_id: str, 
        player_level: int, 
        job_level: int, 
        total_xp: int
    ) -> float:
        """?"""
        
        if user_id not in self.user_progressions or len(self.user_progressions[user_id]) < 2:
            return 1.0  # デフォルト
        
        previous_progression = self.user_progressions[user_id][-2]
        
        # レベル
        level_change = (player_level - previous_progression.player_level) + \
                      (job_level - previous_progression.job_level)
        
        # XP?
        xp_change_rate = (total_xp - previous_progression.total_xp) / max(1, previous_progression.total_xp)
        
        # ?
        return (level_change * 0.6) + (xp_change_rate * 0.4)
    
    def _evaluate_overall_balance(self, avg_metrics: Dict[str, float]) -> Dict[str, Any]:
        """?"""
        
        evaluation = {
            "overall_score": 0.0,
            "category_scores": {},
            "balance_status": "unknown",
            "critical_issues": [],
            "strengths": []
        }
        
        if not avg_metrics:
            return evaluation
        
        # カスタム
        categories = {
            "economy": ["avg_daily_coins", "avg_balance_score"],
            "progression": ["avg_daily_xp", "avg_progression_velocity"],
            "engagement": ["avg_task_completion", "avg_battle_win_rate"]
        }
        
        category_scores = {}
        for category, metrics in categories.items():
            scores = []
            for metric in metrics:
                if metric in avg_metrics:
                    target = self.target_metrics.get(metric.replace("avg_", ""), {})
                    if target:
                        optimal = target.get("optimal", 1.0)
                        score = min(1.0, avg_metrics[metric] / optimal)
                        scores.append(score)
            
            if scores:
                category_scores[category] = statistics.mean(scores)
        
        evaluation["category_scores"] = category_scores
        
        # ?
        if category_scores:
            evaluation["overall_score"] = statistics.mean(category_scores.values())
        
        # バリデーション
        overall_score = evaluation["overall_score"]
        if overall_score >= 0.8:
            evaluation["balance_status"] = "excellent"
        elif overall_score >= 0.6:
            evaluation["balance_status"] = "good"
        elif overall_score >= 0.4:
            evaluation["balance_status"] = "needs_improvement"
        else:
            evaluation["balance_status"] = "critical"
        
        # ?
        for category, score in category_scores.items():
            if score < 0.4:
                evaluation["critical_issues"].append(f"{category}カスタム")
            elif score > 0.8:
                evaluation["strengths"].append(f"{category}カスタム")
        
        return evaluation
    
    def _generate_balance_recommendations(
        self, 
        user_id: str, 
        avg_metrics: Dict[str, float]
    ) -> List[str]:
        """バリデーション"""
        
        recommendations = []
        
        # コア
        daily_coins = avg_metrics.get("avg_daily_coins", 0)
        if daily_coins < 200:
            recommendations.append("タスク")
        elif daily_coins > 800:
            recommendations.append("コア")
        
        # XP?
        daily_xp = avg_metrics.get("avg_daily_xp", 0)
        if daily_xp < 100:
            recommendations.append("?XP?")
        elif daily_xp > 500:
            recommendations.append("安全")
        
        # タスク
        completion_rate = avg_metrics.get("avg_task_completion", 0)
        if completion_rate < 0.6:
            recommendations.append("タスクADHD支援")
        elif completion_rate > 0.9:
            recommendations.append("?")
        
        # バリデーション
        battle_win_rate = avg_metrics.get("avg_battle_win_rate", 0)
        if battle_win_rate < 0.5:
            recommendations.append("?")
        elif battle_win_rate > 0.8:
            recommendations.append("?")
        
        if not recommendations:
            recommendations.append("?")
        
        return recommendations


def main():
    """?"""
    balance_system = EconomicBalanceSystem()
    
    # ?
    test_user = "balance_test_user"
    
    # 7?
    for day in range(1, 8):
        # ?
        daily_activities = {
            "coins_earned": 300 + (day * 50),
            "coins_spent": 200 + (day * 30),
            "xp_earned": 200 + (day * 25),
            "tasks_completed": 4 + (day // 2),
            "tasks_created": 5 + (day // 2),
            "battles_won": 1 if day % 2 == 0 else 0,
            "battles_fought": 1 if day % 2 == 0 else 0
        }
        
        # ストーリー
        total_coins = 1000 + (day * 100)
        snapshot = balance_system.capture_economic_snapshot(
            test_user, total_coins, daily_activities
        )
        
        # ?
        progression = balance_system.capture_progression_metrics(
            user_id=test_user,
            player_level=5 + (day // 2),
            yu_level=4 + (day // 3),
            job_level=2 + (day // 4),
            job_type=JobType.WARRIOR,
            total_xp=500 + (day * 200),
            daily_activities=daily_activities
        )
        
        print(f"Day {day}: Coins={total_coins}, XP={daily_activities['xp_earned']}, Balance={snapshot.balance_score:.2f}")
    
    # バリデーション
    adjustments = balance_system.analyze_balance_needs(test_user)
    print(f"\n?: {len(adjustments)}")
    
    for adj in adjustments:
        print(f"- {adj.metric.value}: {adj.current_value:.2f} ? {adj.target_value:.2f} (?{adj.adjustment_factor:.2f})")
    
    # レベル
    report = balance_system.get_balance_report(test_user)
    print(f"\n?: {report['balance_evaluation']['overall_score']:.2f}")
    print(f"バリデーション: {report['balance_evaluation']['balance_status']}")
    
    print("\n?:")
    for rec in report['recommendations']:
        print(f"- {rec}")


if __name__ == "__main__":
    main()