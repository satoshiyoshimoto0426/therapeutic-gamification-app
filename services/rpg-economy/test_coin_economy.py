"""
コア

タスク
?
"""

import unittest
import sys
import os
from datetime import datetime

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from main import (
    CoinEconomy, ActionType, DemonRarity, CoinReward
)
from shared.interfaces.core_types import TaskType
from shared.utils.exceptions import ValidationError


class TestCoinEconomy(unittest.TestCase):
    """コア"""
    
    def setUp(self):
        """?"""
        self.economy = CoinEconomy()
    
    def test_basic_task_completion_reward(self):
        """基本"""
        reward = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=3,
            performance_multiplier=1.0,
            user_total_coins=0,
            task_type=TaskType.ROUTINE
        )
        
        # ROUTINE タスク10コア
        # ?3 ? ?1.0 = 30コア
        self.assertEqual(reward.final_amount, 30)
        self.assertEqual(reward.base_amount, 10)
        self.assertEqual(reward.difficulty_multiplier, 3.0)
        self.assertEqual(reward.performance_multiplier, 1.0)
        self.assertEqual(reward.inflation_adjustment, 1.0)
    
    def test_different_task_types_rewards(self):
        """?"""
        test_cases = [
            (TaskType.ROUTINE, 10),
            (TaskType.ONE_SHOT, 15),
            (TaskType.SKILL_UP, 20),
            (TaskType.SOCIAL, 25)
        ]
        
        for task_type, expected_base in test_cases:
            with self.subTest(task_type=task_type):
                reward = self.economy.calculate_coin_reward(
                    action_type=ActionType.TASK_COMPLETION,
                    difficulty=1,
                    performance_multiplier=1.0,
                    user_total_coins=0,
                    task_type=task_type
                )
                self.assertEqual(reward.base_amount, expected_base)
                self.assertEqual(reward.final_amount, expected_base)
    
    def test_demon_defeat_rewards(self):
        """?"""
        test_cases = [
            (DemonRarity.COMMON, 50),
            (DemonRarity.RARE, 100),
            (DemonRarity.EPIC, 200),
            (DemonRarity.LEGENDARY, 500)
        ]
        
        for rarity, expected_base in test_cases:
            with self.subTest(rarity=rarity):
                reward = self.economy.calculate_coin_reward(
                    action_type=ActionType.DEMON_DEFEAT,
                    difficulty=1,
                    performance_multiplier=1.0,
                    user_total_coins=0,
                    demon_rarity=rarity
                )
                self.assertEqual(reward.base_amount, expected_base)
                self.assertEqual(reward.final_amount, expected_base)
    
    def test_inflation_control(self):
        """?"""
        test_cases = [
            (0, 1.0),      # ?
            (500, 1.0),    # ?
            (1000, 0.95),  # 5%?
            (5000, 0.9),   # 10%?
            (10000, 0.8),  # 20%?
            (15000, 0.8)   # 20%?
        ]
        
        for total_coins, expected_adjustment in test_cases:
            with self.subTest(total_coins=total_coins):
                adjustment = self.economy.apply_inflation_control(total_coins)
                self.assertEqual(adjustment, expected_adjustment)
    
    def test_inflation_control_in_reward_calculation(self):
        """?"""
        # ?
        reward_low = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=3,
            performance_multiplier=1.0,
            user_total_coins=0,  # ?
            task_type=TaskType.ROUTINE
        )
        
        reward_high = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=3,
            performance_multiplier=1.0,
            user_total_coins=10000,  # ?
            task_type=TaskType.ROUTINE
        )
        
        # ?20%?
        self.assertEqual(reward_low.final_amount, 30)
        self.assertEqual(reward_high.final_amount, 24)  # 30 * 0.8
        self.assertEqual(reward_high.inflation_adjustment, 0.8)
    
    def test_performance_multiplier_effects(self):
        """?"""
        base_reward = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=2,
            performance_multiplier=1.0,
            user_total_coins=0,
            task_type=TaskType.ROUTINE
        )
        
        high_performance_reward = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=2,
            performance_multiplier=1.5,
            user_total_coins=0,
            task_type=TaskType.ROUTINE
        )
        
        low_performance_reward = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=2,
            performance_multiplier=0.8,
            user_total_coins=0,
            task_type=TaskType.ROUTINE
        )
        
        self.assertEqual(base_reward.final_amount, 20)  # 10 * 2 * 1.0
        self.assertEqual(high_performance_reward.final_amount, 30)  # 10 * 2 * 1.5
        self.assertEqual(low_performance_reward.final_amount, 16)  # 10 * 2 * 0.8
    
    def test_task_completion_coins_integration(self):
        """タスク"""
        reward = self.economy.calculate_task_completion_coins(
            task_type=TaskType.SKILL_UP,
            difficulty=4,
            mood_coefficient=1.1,
            adhd_assist=1.2,
            user_total_coins=2000
        )
        
        # SKILL_UP: 20? ? ?4 ? (気分1.1 ? ADHD1.2) ? ?0.95
        expected = int(20 * 4 * 1.1 * 1.2 * 0.95)
        self.assertEqual(reward.final_amount, expected)
        self.assertEqual(reward.action_type, ActionType.TASK_COMPLETION)
    
    def test_demon_defeat_coins_integration(self):
        """?"""
        reward = self.economy.calculate_demon_defeat_coins(
            demon_rarity=DemonRarity.EPIC,
            battle_performance=1.8,
            user_total_coins=6000
        )
        
        # EPIC: 200? ? ?1.8 ? ?0.9
        expected = int(200 * 1.8 * 0.9)
        self.assertEqual(reward.final_amount, expected)
        self.assertEqual(reward.action_type, ActionType.DEMON_DEFEAT)
    
    def test_streak_bonus_calculation(self):
        """ストーリー"""
        test_cases = [
            (7, 100),
            (30, 500),
            (100, 2000),
            (150, 2000)  # 100?
        ]
        
        for streak_days, expected_base in test_cases:
            with self.subTest(streak_days=streak_days):
                reward = self.economy.calculate_coin_reward(
                    action_type=ActionType.STREAK_BONUS,
                    difficulty=1,
                    performance_multiplier=1.0,
                    user_total_coins=0,
                    streak_days=streak_days
                )
                self.assertEqual(reward.base_amount, expected_base)
    
    def test_daily_bonus_calculation(self):
        """デフォルト"""
        reward = self.economy.calculate_coin_reward(
            action_type=ActionType.DAILY_BONUS,
            difficulty=1,
            performance_multiplier=1.0,
            user_total_coins=0
        )
        
        self.assertEqual(reward.base_amount, 30)
        self.assertEqual(reward.final_amount, 30)
    
    def test_economic_status(self):
        """?"""
        status = self.economy.get_economic_status(7500)
        
        self.assertEqual(status["total_coins"], 7500)
        self.assertEqual(status["inflation_adjustment"], 0.9)
        self.assertAlmostEqual(status["inflation_reduction_percent"], 10, delta=1)
        self.assertEqual(status["next_threshold"], 10000)
        self.assertEqual(status["coins_to_next_threshold"], 2500)
        self.assertEqual(status["economic_tier"], "comfortable")
    
    def test_economic_tiers(self):
        """?"""
        test_cases = [
            (500, "starting"),
            (1500, "stable"),
            (7000, "comfortable"),
            (15000, "wealthy")
        ]
        
        for coins, expected_tier in test_cases:
            with self.subTest(coins=coins):
                status = self.economy.get_economic_status(coins)
                self.assertEqual(status["economic_tier"], expected_tier)
    
    def test_validation_errors(self):
        """バリデーション"""
        # 無
        with self.assertRaises(ValidationError):
            self.economy.calculate_coin_reward(
                action_type=ActionType.TASK_COMPLETION,
                difficulty=0,  # 無
                performance_multiplier=1.0,
                user_total_coins=0,
                task_type=TaskType.ROUTINE
            )
        
        # 無
        with self.assertRaises(ValidationError):
            self.economy.calculate_coin_reward(
                action_type=ActionType.TASK_COMPLETION,
                difficulty=3,
                performance_multiplier=3.0,  # ?
                user_total_coins=0,
                task_type=TaskType.ROUTINE
            )
        
        # ?
        with self.assertRaises(ValidationError):
            self.economy.calculate_coin_reward(
                action_type=ActionType.TASK_COMPLETION,
                difficulty=3,
                performance_multiplier=1.0,
                user_total_coins=0
                # task_type が
            )
    
    def test_reward_data_structure(self):
        """?"""
        reward = self.economy.calculate_coin_reward(
            action_type=ActionType.TASK_COMPLETION,
            difficulty=2,
            performance_multiplier=1.2,
            user_total_coins=1500,
            task_type=TaskType.SOCIAL
        )
        
        # デフォルト
        self.assertIsInstance(reward, CoinReward)
        self.assertIsInstance(reward.timestamp, datetime)
        self.assertEqual(reward.action_type, ActionType.TASK_COMPLETION)
        
        # 計算
        self.assertEqual(reward.base_amount, 25)  # SOCIAL タスク
        self.assertEqual(reward.difficulty_multiplier, 2.0)
        self.assertEqual(reward.performance_multiplier, 1.2)
        self.assertEqual(reward.inflation_adjustment, 0.95)  # 1500コア
        
        expected_final = int(25 * 2 * 1.2 * 0.95)
        self.assertEqual(reward.final_amount, expected_final)


class TestCoinEconomyIntegration(unittest.TestCase):
    """コア"""
    
    def setUp(self):
        """?"""
        self.economy = CoinEconomy()
    
    def test_complete_user_journey(self):
        """?"""
        user_coins = 0
        rewards_history = []
        
        # 1. ?
        reward1 = self.economy.calculate_task_completion_coins(
            task_type=TaskType.ROUTINE,
            difficulty=2,
            mood_coefficient=1.0,
            adhd_assist=1.0,
            user_total_coins=user_coins
        )
        user_coins += reward1.final_amount
        rewards_history.append(reward1)
        
        # 2. ストーリー
        reward2 = self.economy.calculate_task_completion_coins(
            task_type=TaskType.SKILL_UP,
            difficulty=3,
            mood_coefficient=1.1,
            adhd_assist=1.2,
            user_total_coins=user_coins
        )
        user_coins += reward2.final_amount
        rewards_history.append(reward2)
        
        # 3. ?
        reward3 = self.economy.calculate_demon_defeat_coins(
            demon_rarity=DemonRarity.RARE,
            battle_performance=1.5,
            user_total_coins=user_coins
        )
        user_coins += reward3.final_amount
        rewards_history.append(reward3)
        
        # 4. ?
        status = self.economy.get_economic_status(user_coins)
        
        # ?
        self.assertGreater(user_coins, 0)
        self.assertEqual(len(rewards_history), 3)
        self.assertIn("economic_tier", status)
        
        # ?
        self.assertEqual(reward1.final_amount, 20)  # 10 * 2 * 1.0 * 1.0
        expected_reward2 = int(20 * 3 * 1.1 * 1.2)  # ?
        self.assertEqual(reward2.final_amount, expected_reward2)
        
        print(f"ユーザー: ? {user_coins}")
        print(f"?: {status['economic_tier']}")
    
    def test_inflation_progression(self):
        """?"""
        # ?
        coin_amounts = [0, 1000, 5000, 10000]
        
        for coins in coin_amounts:
            reward = self.economy.calculate_task_completion_coins(
                task_type=TaskType.ROUTINE,
                difficulty=3,
                mood_coefficient=1.0,
                adhd_assist=1.0,
                user_total_coins=coins
            )
            
            status = self.economy.get_economic_status(coins)
            
            print(f"コア: {coins}, ?: {reward.final_amount}, "
                  f"?: {reward.inflation_adjustment}, "
                  f"?: {status['economic_tier']}")
        
        # ?
        self.assertTrue(True)  # ?printで


if __name__ == "__main__":
    # ?
    unittest.main(verbosity=2)