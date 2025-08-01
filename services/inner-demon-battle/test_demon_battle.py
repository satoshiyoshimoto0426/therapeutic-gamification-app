"""
内部
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from main import (
    InnerDemonBattle, DemonType, BattleResult, DemonStats, BattleReward
)

class TestInnerDemonBattle(unittest.TestCase):
    """内部"""
    
    def setUp(self):
        """?"""
        self.battle_system = InnerDemonBattle()
        self.test_user_id = "test_user_123"
    
    def test_demon_types_initialization(self):
        """?"""
        # 4?
        self.assertEqual(len(self.battle_system.demon_types), 4)
        
        # ?
        expected_demons = [
            DemonType.PROCRASTINATION_DRAGON,
            DemonType.ANXIETY_SHADOW,
            DemonType.DEPRESSION_VOID,
            DemonType.SOCIAL_FEAR_GOBLIN
        ]
        
        for demon_type in expected_demons:
            self.assertIn(demon_type, self.battle_system.demon_types)
            demon_data = self.battle_system.demon_types[demon_type]
            
            # ?
            self.assertIn("name", demon_data)
            self.assertIn("max_hp", demon_data)
            self.assertIn("weaknesses", demon_data)
            self.assertIn("therapeutic_theme", demon_data)
            self.assertIn("description", demon_data)
            self.assertIn("rewards", demon_data)
    
    def test_procrastination_dragon_properties(self):
        """?"""
        dragon = self.battle_system.demon_types[DemonType.PROCRASTINATION_DRAGON]
        
        self.assertEqual(dragon["name"], "?")
        self.assertEqual(dragon["max_hp"], 100)
        self.assertEqual(dragon["therapeutic_theme"], "?")
        
        # ?
        expected_weaknesses = [
            "routine_task_completion",
            "pomodoro_usage",
            "small_step_action",
            "deadline_adherence",
            "morning_routine"
        ]
        self.assertEqual(dragon["weaknesses"], expected_weaknesses)
        
        # ?
        rewards = dragon["rewards"]
        self.assertEqual(rewards["coins"], 150)
        self.assertEqual(rewards["xp"], 75)
        self.assertIn("focus_potion", rewards["items"])
    
    def test_anxiety_shadow_properties(self):
        """?"""
        shadow = self.battle_system.demon_types[DemonType.ANXIETY_SHADOW]
        
        self.assertEqual(shadow["name"], "?")
        self.assertEqual(shadow["max_hp"], 80)
        self.assertEqual(shadow["therapeutic_theme"], "?")
        
        # ?
        expected_weaknesses = [
            "breathing_exercise",
            "positive_affirmation",
            "mindfulness_practice",
            "social_connection",
            "grounding_technique"
        ]
        self.assertEqual(shadow["weaknesses"], expected_weaknesses)
    
    def test_depression_void_properties(self):
        """?"""
        void = self.battle_system.demon_types[DemonType.DEPRESSION_VOID]
        
        self.assertEqual(void["name"], "?")
        self.assertEqual(void["max_hp"], 150)
        self.assertEqual(void["therapeutic_theme"], "無")
        
        # ?
        max_hp_values = [demon["max_hp"] for demon in self.battle_system.demon_types.values()]
        self.assertEqual(void["max_hp"], max(max_hp_values))
    
    def test_social_fear_goblin_properties(self):
        """?"""
        goblin = self.battle_system.demon_types[DemonType.SOCIAL_FEAR_GOBLIN]
        
        self.assertEqual(goblin["name"], "?")
        self.assertEqual(goblin["max_hp"], 60)
        self.assertEqual(goblin["therapeutic_theme"], "?")
        
        # ?
        min_hp_values = [demon["max_hp"] for demon in self.battle_system.demon_types.values()]
        self.assertEqual(goblin["max_hp"], min(min_hp_values))
    
    def test_damage_calculation_direct_weakness(self):
        """?"""
        weaknesses = ["routine_task_completion", "pomodoro_usage"]
        actions = ["routine_task_completion", "pomodoro_usage"]
        
        with patch('random.uniform', return_value=1.0):  # ?
            damage = self.battle_system._calculate_damage(actions, weaknesses)
            expected_damage = 25 + 25  # ?25?
            self.assertEqual(damage, expected_damage)
    
    def test_damage_calculation_partial_match(self):
        """?"""
        weaknesses = ["routine_task_completion"]
        actions = ["routine_task"]  # ?
        
        with patch('random.uniform', return_value=1.0):
            damage = self.battle_system._calculate_damage(actions, weaknesses)
            expected_damage = 15  # ?15?
            self.assertEqual(damage, expected_damage)
    
    def test_damage_calculation_no_match(self):
        """?"""
        weaknesses = ["routine_task_completion"]
        actions = ["unrelated_action"]
        
        with patch('random.uniform', return_value=1.0):
            damage = self.battle_system._calculate_damage(actions, weaknesses)
            expected_damage = 5  # ?5?
            self.assertEqual(damage, expected_damage)
    
    def test_initiate_battle_victory(self):
        """バリデーション"""
        # ?
        powerful_actions = ["routine_task_completion"] * 5  # 125?
        
        with patch('random.uniform', return_value=1.0):
            result = self.battle_system.initiate_battle(
                self.test_user_id, 
                DemonType.PROCRASTINATION_DRAGON, 
                powerful_actions
            )
        
        self.assertEqual(result["result"], BattleResult.VICTORY.value)
        self.assertEqual(result["demon_name"], "?")
        self.assertIn("rewards", result)
        self.assertIn("therapeutic_message", result)
        self.assertIn("reflection_prompt", result)
        
        # バリデーション
        self.assertNotIn(self.test_user_id, self.battle_system.active_battles)
    
    def test_initiate_battle_ongoing(self):
        """バリデーション"""
        # ?
        moderate_actions = ["routine_task_completion"]  # 25?
        
        with patch('random.uniform', return_value=1.0):
            result = self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.PROCRASTINATION_DRAGON,
                moderate_actions
            )
        
        self.assertEqual(result["result"], BattleResult.ONGOING.value)
        self.assertEqual(result["demon_name"], "?")
        self.assertEqual(result["demon_hp"], 75)  # 100 - 25
        self.assertEqual(result["demon_max_hp"], 100)
        self.assertIn("suggested_actions", result)
        self.assertIn("encouragement", result)
        
        # バリデーション
        self.assertIn(self.test_user_id, self.battle_system.active_battles)
    
    def test_continue_battle_victory(self):
        """バリデーション"""
        # ?
        initial_actions = ["routine_task_completion"]
        
        with patch('random.uniform', return_value=1.0):
            self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.PROCRASTINATION_DRAGON,
                initial_actions
            )
            
            # ?
            additional_actions = ["pomodoro_usage"] * 3  # 75?
            result = self.battle_system.continue_battle(self.test_user_id, additional_actions)
        
        self.assertEqual(result["result"], BattleResult.VICTORY.value)
        self.assertIn("rewards", result)
        self.assertIn("turns_taken", result)
        
        # バリデーション
        self.assertNotIn(self.test_user_id, self.battle_system.active_battles)
    
    def test_continue_battle_defeat(self):
        """バリデーション"""
        # ?
        weak_actions = ["unrelated_action"]
        
        with patch('random.uniform', return_value=1.0):
            self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.PROCRASTINATION_DRAGON,
                weak_actions
            )
            
            # 10タスク
            for _ in range(10):
                result = self.battle_system.continue_battle(self.test_user_id, weak_actions)
        
        self.assertEqual(result["result"], BattleResult.DEFEAT.value)
        self.assertIn("support_message", result)
        self.assertIn("alternative_strategies", result)
        self.assertIn("consolation_reward", result)
        
        # ?
        consolation = result["consolation_reward"]
        self.assertEqual(consolation["coins"], 37)  # 150 // 4
        self.assertEqual(consolation["xp"], 18)     # 75 // 4
    
    def test_continue_battle_no_active_battle(self):
        """アプリ"""
        result = self.battle_system.continue_battle("nonexistent_user", ["action"])
        self.assertIn("error", result)
    
    def test_get_battle_status(self):
        """バリデーション"""
        # バリデーション
        actions = ["breathing_exercise"]  # ?
        
        with patch('random.uniform', return_value=1.0):
            self.battle_system.initiate_battle(
                self.test_user_id,
                DemonType.ANXIETY_SHADOW,
                actions
            )
        
        status = self.battle_system.get_battle_status(self.test_user_id)
        
        self.assertIsNotNone(status)
        self.assertEqual(status["demon_name"], "?")
        self.assertEqual(status["demon_hp"], 55)  # 80 - 25
        self.assertEqual(status["demon_max_hp"], 80)
        self.assertEqual(status["turn_count"], 1)
        self.assertEqual(status["therapeutic_theme"], "?")
    
    def test_get_battle_status_no_battle(self):
        """バリデーション"""
        status = self.battle_system.get_battle_status("nonexistent_user")
        self.assertIsNone(status)
    
    def test_get_available_demons(self):
        """?"""
        demons = self.battle_system.get_available_demons()
        
        self.assertEqual(len(demons), 4)
        
        # ?
        demon_names = [demon["name"] for demon in demons]
        expected_names = ["?", "?", "?", "?"]
        
        for name in expected_names:
            self.assertIn(name, demon_names)
        
        # ?
        for demon in demons:
            self.assertIn("type", demon)
            self.assertIn("name", demon)
            self.assertIn("description", demon)
            self.assertIn("therapeutic_theme", demon)
            self.assertIn("max_hp", demon)
            self.assertIn("weaknesses", demon)
    
    def test_victory_reflection_generation(self):
        """?"""
        demon_data = self.battle_system.demon_types[DemonType.PROCRASTINATION_DRAGON]
        reflection = self.battle_system._generate_victory_reflection(demon_data)
        
        self.assertIsInstance(reflection, str)
        self.assertIn("?", reflection)
        self.assertIn("?", reflection)
    
    def test_support_message_generation(self):
        """?"""
        demon_data = self.battle_system.demon_types[DemonType.ANXIETY_SHADOW]
        support_message = self.battle_system._generate_support_message(demon_data)
        
        self.assertIsInstance(support_message, str)
        self.assertIn("?", support_message)
        self.assertGreater(len(support_message), 20)  # 意
    
    def test_alternative_strategies_suggestion(self):
        """?"""
        weaknesses = ["routine_task_completion", "pomodoro_usage", "breathing_exercise"]
        strategies = self.battle_system._suggest_alternative_strategies(weaknesses)
        
        self.assertIsInstance(strategies, list)
        self.assertLessEqual(len(strategies), 3)  # ?3つ
        
        for strategy in strategies:
            self.assertIsInstance(strategy, str)
            self.assertGreater(len(strategy), 10)  # 意
    
    def test_encouragement_message_high_damage(self):
        """?"""
        demon_stats = DemonStats(
            name="?",
            max_hp=100,
            current_hp=50,
            weaknesses=[],
            therapeutic_theme="?",
            description="?"
        )
        
        message = self.battle_system._generate_encouragement_message(demon_stats, 25)
        self.assertIn("?", message)
        self.assertIn("?", message)
    
    def test_encouragement_message_low_hp(self):
        """?HP?"""
        demon_stats = DemonStats(
            name="?",
            max_hp=100,
            current_hp=20,  # 20% HP
            weaknesses=[],
            therapeutic_theme="?",
            description="?"
        )
        
        message = self.battle_system._generate_encouragement_message(demon_stats, 10)
        self.assertIn("?", message)
        self.assertIn("?", message)
    
    def test_battle_tips_generation(self):
        """バリデーション"""
        tips = self.battle_system._get_battle_tips("?")
        
        self.assertIsInstance(tips, list)
        self.assertGreater(len(tips), 0)
        
        for tip in tips:
            self.assertIsInstance(tip, str)
            self.assertGreater(len(tip), 10)

class TestDemonStats(unittest.TestCase):
    """DemonStatsデフォルト"""
    
    def test_demon_stats_creation(self):
        """DemonStats?"""
        stats = DemonStats(
            name="?",
            max_hp=100,
            current_hp=80,
            weaknesses=["test_weakness"],
            therapeutic_theme="?",
            description="?"
        )
        
        self.assertEqual(stats.name, "?")
        self.assertEqual(stats.max_hp, 100)
        self.assertEqual(stats.current_hp, 80)
        self.assertEqual(stats.weaknesses, ["test_weakness"])
        self.assertEqual(stats.therapeutic_theme, "?")
        self.assertEqual(stats.description, "?")

class TestBattleReward(unittest.TestCase):
    """BattleRewardデフォルト"""
    
    def test_battle_reward_creation(self):
        """BattleReward?"""
        reward = BattleReward(
            coins=100,
            items=["test_item"],
            xp=50,
            therapeutic_message="?"
        )
        
        self.assertEqual(reward.coins, 100)
        self.assertEqual(reward.items, ["test_item"])
        self.assertEqual(reward.xp, 50)
        self.assertEqual(reward.therapeutic_message, "?")

if __name__ == "__main__":
    unittest.main()