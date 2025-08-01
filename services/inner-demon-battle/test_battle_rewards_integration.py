"""
バリデーションCBT?
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from main import InnerDemonBattle, DemonType, BattleResult
from battle_rewards import BattleRewardSystem, ItemRarity

class TestBattleRewardsIntegration(unittest.TestCase):
    """バリデーション"""
    
    def setUp(self):
        """?"""
        self.battle_system = InnerDemonBattle()
        self.reward_system = BattleRewardSystem()
        self.test_user_id = "test_user_123"
    
    def test_victory_rewards_calculation(self):
        """?"""
        # ?
        powerful_actions = ["routine_task_completion"] * 5
        
        with patch('random.uniform', return_value=1.0):
            result = self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.PROCRASTINATION_DRAGON,
                powerful_actions
            )
        
        self.assertEqual(result["result"], BattleResult.VICTORY.value)
        
        # ?
        self.assertIn("rewards", result)
        rewards = result["rewards"]
        
        # 基本XPが
        self.assertGreaterEqual(rewards["coins"], 150)  # 基本150?
        self.assertGreaterEqual(rewards["xp"], 75)      # 基本75?
        
        # アプリ
        self.assertIn("items", rewards)
        self.assertGreater(len(rewards["items"]), 0)
        
        # CBT?
        self.assertIn("cbt_reflection_prompt", result)
        self.assertIsInstance(result["cbt_reflection_prompt"], str)
        self.assertGreater(len(result["cbt_reflection_prompt"]), 20)
    
    def test_defeat_rewards_calculation(self):
        """?"""
        # ?
        weak_actions = ["unrelated_action"]
        
        with patch('random.uniform', return_value=1.0):
            self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.ANXIETY_SHADOW,
                weak_actions
            )
            
            # 10タスク
            for _ in range(10):
                result = self.battle_system.continue_battle(self.test_user_id, weak_actions)
        
        self.assertEqual(result["result"], BattleResult.DEFEAT.value)
        
        # ?
        self.assertIn("consolation_reward", result)
        consolation = result["consolation_reward"]
        
        # ?25%?
        self.assertLessEqual(consolation["coins"], 30)  # 120の25%
        self.assertLessEqual(consolation["xp"], 15)     # 60の25%
        
        # ?
        self.assertIn("items", consolation)
        
        # CBT?
        self.assertIn("cbt_reflection_prompt", result)
        self.assertIsInstance(result["cbt_reflection_prompt"], str)
        self.assertGreater(len(result["cbt_reflection_prompt"]), 20)
    
    def test_performance_multiplier_calculation(self):
        """?"""
        battle_performance = {
            "turns_taken": 2,      # ?
            "damage_efficiency": 0.9,  # ?
            "weakness_hits": 4     # ?
        }
        
        multiplier = self.reward_system._calculate_performance_multiplier(battle_performance)
        
        # ?1.0?
        self.assertGreaterEqual(multiplier, 1.0)
        # ?2.0を
        self.assertLessEqual(multiplier, 2.0)
    
    def test_item_rarity_distribution(self):
        """アプリ"""
        # ?
        high_performance_items = self.reward_system._generate_battle_items(
            "procrastination_dragon", 1.8
        )
        
        # ?
        low_performance_items = self.reward_system._generate_battle_items(
            "procrastination_dragon", 1.0
        )
        
        # ?
        self.assertGreaterEqual(len(high_performance_items), len(low_performance_items))
    
    def test_cbt_reflection_generation(self):
        """CBT?"""
        battle_performance = {
            "turns_taken": 3,
            "damage_efficiency": 0.7,
            "weakness_hits": 2
        }
        
        # ?CBT?
        demon_types = ["procrastination_dragon", "anxiety_shadow", "depression_void", "social_fear_goblin"]
        
        for demon_type in demon_types:
            # ?
            victory_prompt = self.reward_system._generate_cbt_reflection(demon_type, battle_performance)
            self.assertIsInstance(victory_prompt, str)
            self.assertGreater(len(victory_prompt), 20)
            
            # ?
            defeat_prompt = self.reward_system._generate_defeat_cbt_reflection(demon_type, battle_performance)
            self.assertIsInstance(defeat_prompt, str)
            self.assertGreater(len(defeat_prompt), 20)
    
    def test_therapeutic_message_generation(self):
        """治療"""
        demon_types = ["procrastination_dragon", "anxiety_shadow", "depression_void", "social_fear_goblin"]
        
        for demon_type in demon_types:
            # ?
            support_message = self.reward_system._generate_support_message(demon_type)
            self.assertIsInstance(support_message, str)
            self.assertGreater(len(support_message), 20)
            
            # 治療
            self.assertTrue(
                any(keyword in support_message for keyword in 
                    ["挑", "勇", "成", "一般", "つ", "希", "?", "?", "?", "?"])
            )
    
    def test_item_therapeutic_effects(self):
        """アプリ"""
        # ?
        for demon_type, items in self.reward_system.item_pool.items():
            for item in items:
                # 治療
                self.assertIsInstance(item.therapeutic_effect, str)
                self.assertGreaterEqual(len(item.therapeutic_effect), 3)
                
                # ストーリー
                self.assertIsInstance(item.stat_bonus, dict)
                self.assertGreater(len(item.stat_bonus), 0)
                
                # ?
                for stat, bonus in item.stat_bonus.items():
                    self.assertGreaterEqual(bonus, 1)
                    self.assertLessEqual(bonus, 10)
    
    def test_consolation_items_generation(self):
        """?"""
        demon_types = ["procrastination_dragon", "anxiety_shadow", "depression_void", "social_fear_goblin"]
        
        for demon_type in demon_types:
            consolation_items = self.reward_system._generate_consolation_items(demon_type)
            
            # ?
            self.assertGreater(len(consolation_items), 0)
            
            # コア
            for item in consolation_items:
                self.assertEqual(item.rarity, ItemRarity.COMMON)
    
    def test_weakness_hits_counting(self):
        """?"""
        user_actions = ["routine_task_completion", "pomodoro_usage", "unrelated_action", "routine_task_completion"]
        weaknesses = ["routine_task_completion", "pomodoro_usage", "small_step_action"]
        
        hits = self.battle_system._count_weakness_hits(user_actions, weaknesses)
        
        # ?
        self.assertEqual(hits, 3)  # routine_task_completion x2, pomodoro_usage x1
    
    def test_battle_performance_tracking(self):
        """バリデーション"""
        actions = ["routine_task_completion", "pomodoro_usage"]
        
        with patch('random.uniform', return_value=1.0):
            result = self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.PROCRASTINATION_DRAGON,
                actions
            )
        
        # バリデーション
        if result["result"] == BattleResult.VICTORY.value:
            self.assertIn("battle_performance", result)
            performance = result["battle_performance"]
            
            self.assertIn("turns_taken", performance)
            self.assertIn("damage_efficiency", performance)
            self.assertIn("weakness_hits", performance)
            
            # ?
            self.assertGreaterEqual(performance["turns_taken"], 1)
            self.assertGreaterEqual(performance["damage_efficiency"], 0.0)
            self.assertLessEqual(performance["damage_efficiency"], 1.0)
            self.assertGreaterEqual(performance["weakness_hits"], 0)
    
    def test_integrated_battle_flow(self):
        """?"""
        # ?
        powerful_actions = ["small_social_task"] * 4  # ?
        
        with patch('random.uniform', return_value=1.0):
            # バリデーション
            result = self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.SOCIAL_FEAR_GOBLIN,  # ?
                powerful_actions
            )
            
            # ?
            if result["result"] == BattleResult.ONGOING.value:
                additional_actions = ["communication_practice"] * 3
                result = self.battle_system.continue_battle(self.test_user_id, additional_actions)
        
        # ?
        self.assertIn(result["result"], [BattleResult.VICTORY.value, BattleResult.DEFEAT.value, BattleResult.ONGOING.value])
        
        # ?CBT?
        if result["result"] == BattleResult.VICTORY.value:
            self.assertIn("rewards", result)
            self.assertIn("cbt_reflection_prompt", result)
        elif result["result"] == BattleResult.DEFEAT.value:
            self.assertIn("consolation_reward", result)
            self.assertIn("cbt_reflection_prompt", result)
        else:
            # ?
            self.assertIn("suggested_actions", result)
            self.assertIn("encouragement", result)

class TestBattleRewardSystem(unittest.TestCase):
    """バリデーション"""
    
    def setUp(self):
        """?"""
        self.reward_system = BattleRewardSystem()
    
    def test_item_pool_initialization(self):
        """アプリ"""
        # 4?
        expected_demons = ["procrastination_dragon", "anxiety_shadow", "depression_void", "social_fear_goblin"]
        
        for demon_type in expected_demons:
            self.assertIn(demon_type, self.reward_system.item_pool)
            items = self.reward_system.item_pool[demon_type]
            
            # ?
            rarities = [item.rarity for item in items]
            self.assertIn(ItemRarity.COMMON, rarities)
            self.assertIn(ItemRarity.LEGENDARY, rarities)
    
    def test_rarity_rates_sum(self):
        """レベル"""
        total_rate = sum(self.reward_system.rarity_rates.values())
        self.assertAlmostEqual(total_rate, 1.0, places=2)

if __name__ == "__main__":
    unittest.main()