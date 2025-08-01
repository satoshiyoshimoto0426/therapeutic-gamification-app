"""
RPG? - コア

こRPG?
- コア
- ?5?
- ?6ストーリー6?
"""

from typing import Dict, List, Optional, Tuple
import random
import math
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.core_types import TaskType
from shared.utils.exceptions import ValidationError, BusinessLogicError


class ActionType(Enum):
    """アプリ"""
    TASK_COMPLETION = "task_completion"
    DEMON_DEFEAT = "demon_defeat"
    DAILY_BONUS = "daily_bonus"
    STREAK_BONUS = "streak_bonus"


class DemonRarity(Enum):
    """?"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class CoinReward:
    """コア"""
    base_amount: int
    difficulty_multiplier: float
    performance_multiplier: float
    inflation_adjustment: float
    final_amount: int
    action_type: ActionType
    timestamp: datetime


class CoinEconomy:
    """
    コア
    
    タスク
    ?
    """
    
    def __init__(self):
        self.base_coin_rates = {
            "task_completion": {
                TaskType.ROUTINE.value: 10,
                TaskType.ONE_SHOT.value: 15,
                TaskType.SKILL_UP.value: 20,
                TaskType.SOCIAL.value: 25
            },
            "demon_defeat": {
                DemonRarity.COMMON.value: 50,
                DemonRarity.RARE.value: 100,
                DemonRarity.EPIC.value: 200,
                DemonRarity.LEGENDARY.value: 500
            },
            "daily_bonus": 30,
            "streak_bonus": {
                "7_days": 100,
                "30_days": 500,
                "100_days": 2000
            }
        }
        
        # ?
        self.inflation_thresholds = {
            10000: 0.8,  # 10,000コア20%?
            5000: 0.9,   # 5,000コア10%?
            1000: 0.95   # 1,000コア5%?
        }
    
    def calculate_coin_reward(
        self, 
        action_type: ActionType, 
        difficulty: int = 1,
        performance_multiplier: float = 1.0,
        user_total_coins: int = 0,
        task_type: Optional[TaskType] = None,
        demon_rarity: Optional[DemonRarity] = None,
        streak_days: Optional[int] = None
    ) -> CoinReward:
        """
        コア
        
        Args:
            action_type: アプリ
            difficulty: ? (1-5)
            performance_multiplier: ? (0.5-2.0)
            user_total_coins: ユーザー
            task_type: タスク
            demon_rarity: ?
            streak_days: ?
        
        Returns:
            CoinReward: 計算
        """
        # バリデーション
        if not isinstance(difficulty, int) or difficulty <= 0:
            raise ValidationError("difficulty must be a positive integer")
        if not (1 <= difficulty <= 5):
            raise ValidationError("difficulty must be between 1 and 5")
        if not isinstance(performance_multiplier, (int, float)) or not (0.5 <= performance_multiplier <= 2.0):
            raise ValidationError("performance_multiplier must be between 0.5 and 2.0")
        if not isinstance(user_total_coins, int) or user_total_coins < 0:
            raise ValidationError("user_total_coins must be a non-negative integer")
        
        # ?
        base_coins = self._get_base_coins(action_type, task_type, demon_rarity, streak_days)
        
        # ?
        adjusted_coins = base_coins * difficulty * performance_multiplier
        
        # ?
        inflation_adjustment = self.apply_inflation_control(user_total_coins)
        final_amount = int(adjusted_coins * inflation_adjustment)
        
        return CoinReward(
            base_amount=base_coins,
            difficulty_multiplier=float(difficulty),
            performance_multiplier=performance_multiplier,
            inflation_adjustment=inflation_adjustment,
            final_amount=final_amount,
            action_type=action_type,
            timestamp=datetime.now()
        )
    
    def _get_base_coins(
        self, 
        action_type: ActionType, 
        task_type: Optional[TaskType] = None,
        demon_rarity: Optional[DemonRarity] = None,
        streak_days: Optional[int] = None
    ) -> int:
        """?"""
        
        if action_type == ActionType.TASK_COMPLETION:
            if not task_type:
                raise ValidationError("task_type is required for TASK_COMPLETION")
            return self.base_coin_rates["task_completion"].get(task_type.value, 10)
        
        elif action_type == ActionType.DEMON_DEFEAT:
            if not demon_rarity:
                raise ValidationError("demon_rarity is required for DEMON_DEFEAT")
            return self.base_coin_rates["demon_defeat"].get(demon_rarity.value, 50)
        
        elif action_type == ActionType.DAILY_BONUS:
            return self.base_coin_rates["daily_bonus"]
        
        elif action_type == ActionType.STREAK_BONUS:
            if not streak_days:
                raise ValidationError("streak_days is required for STREAK_BONUS")
            
            # ストーリー
            if streak_days >= 100:
                return self.base_coin_rates["streak_bonus"]["100_days"]
            elif streak_days >= 30:
                return self.base_coin_rates["streak_bonus"]["30_days"]
            elif streak_days >= 7:
                return self.base_coin_rates["streak_bonus"]["7_days"]
            else:
                return 0
        
        else:
            raise ValidationError(f"Unknown action_type: {action_type}")
    
    def apply_inflation_control(self, user_total_coins: int) -> float:
        """
        ?
        
        ?
        
        Args:
            user_total_coins: ユーザー
            
        Returns:
            float: ? (0.8-1.0)
        """
        if not isinstance(user_total_coins, int) or user_total_coins < 0:
            raise ValidationError("user_total_coins must be a non-negative integer")
        
        # ?
        for threshold in sorted(self.inflation_thresholds.keys(), reverse=True):
            if user_total_coins >= threshold:
                return self.inflation_thresholds[threshold]
        
        return 1.0  # ?
    
    def calculate_task_completion_coins(
        self, 
        task_type: TaskType, 
        difficulty: int,
        mood_coefficient: float,
        adhd_assist: float,
        user_total_coins: int
    ) -> CoinReward:
        """
        タスク
        
        Args:
            task_type: タスク
            difficulty: ?
            mood_coefficient: 気分 (0.8-1.2)
            adhd_assist: ADHD支援 (1.0-1.3)
            user_total_coins: ユーザー
            
        Returns:
            CoinReward: 計算
        """
        # ?ADHD支援
        performance_multiplier = mood_coefficient * adhd_assist
        
        return self.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=difficulty,
            performance_multiplier=performance_multiplier,
            user_total_coins=user_total_coins,
            task_type=task_type
        )
    
    def calculate_demon_defeat_coins(
        self, 
        demon_rarity: DemonRarity,
        battle_performance: float,
        user_total_coins: int
    ) -> CoinReward:
        """
        ?
        
        Args:
            demon_rarity: ?
            battle_performance: バリデーション (0.5-2.0)
            user_total_coins: ユーザー
            
        Returns:
            CoinReward: 計算
        """
        return self.calculate_coin_reward(
            action_type=ActionType.DEMON_DEFEAT,
            difficulty=1,  # ?
            performance_multiplier=battle_performance,
            user_total_coins=user_total_coins,
            demon_rarity=demon_rarity
        )
    
    def get_economic_status(self, user_total_coins: int) -> Dict:
        """
        ?
        
        Args:
            user_total_coins: ユーザー
            
        Returns:
            Dict: ?
        """
        inflation_adjustment = self.apply_inflation_control(user_total_coins)
        
        # ?
        next_threshold = None
        for threshold in sorted(self.inflation_thresholds.keys()):
            if user_total_coins < threshold:
                next_threshold = threshold
                break
        
        return {
            "total_coins": user_total_coins,
            "inflation_adjustment": inflation_adjustment,
            "inflation_reduction_percent": int((1 - inflation_adjustment) * 100),
            "next_threshold": next_threshold,
            "coins_to_next_threshold": next_threshold - user_total_coins if next_threshold else None,
            "economic_tier": self._get_economic_tier(user_total_coins)
        }
    
    def _get_economic_tier(self, total_coins: int) -> str:
        """?"""
        if total_coins >= 10000:
            return "wealthy"
        elif total_coins >= 5000:
            return "comfortable"
        elif total_coins >= 1000:
            return "stable"
        else:
            return "starting"


if __name__ == "__main__":
    # 基本
    economy = CoinEconomy()
    
    # タスク
    reward = economy.calculate_task_completion_coins(
        task_type=TaskType.ROUTINE,
        difficulty=3,
        mood_coefficient=1.1,
        adhd_assist=1.2,
        user_total_coins=0
    )
    
    print(f"タスク: {reward.final_amount}コア")
    print(f"?: {reward.base_amount}, ?: {reward.final_amount}")
    
    # ?
    demon_reward = economy.calculate_demon_defeat_coins(
        demon_rarity=DemonRarity.RARE,
        battle_performance=1.5,
        user_total_coins=0
    )
    
    print(f"?: {demon_reward.final_amount}コア")
    
    # ?
    status = economy.get_economic_status(7500)
    print(f"?: {status}")