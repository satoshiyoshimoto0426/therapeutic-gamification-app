"""
XP?

?: 4.4, 4.5 - レベル
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
import math

# 共有
from shared.interfaces.core_types import UserProfile
from shared.interfaces.level_system import LevelSystem
from shared.interfaces.resonance_system import ResonanceSystem
from shared.interfaces.crystal_system import CrystalGauge, CRYSTAL_ATTRIBUTES
from shared.interfaces.task_system import TaskType

# ?
from services.core_game.main import CoreGameEngine


class TestXPLevelResonanceIntegration:
    """XP?"""
    
    @pytest.fixture
    def level_system(self):
        """レベル"""
        return LevelSystem()
    
    @pytest.fixture
    def resonance_system(self):
        """共有"""
        return ResonanceSystem()
    
    @pytest.fixture
    def crystal_gauge(self):
        """?"""
        return CrystalGauge()
    
    @pytest.fixture
    def test_user_profile(self):
        """?"""
        return UserProfile(
            uid="integration_test_user",
            yu_level=5,
            player_level=3,
            total_xp=250,
            crystal_gauges={attr: 30 for attr in CRYSTAL_ATTRIBUTES},
            current_chapter="chapter_1",
            daily_task_limit=16,
            care_points=50
        )
    
    def test_xp_calculation_accuracy(self):
        """XP計算"""
        # ?: difficulty=3, mood_coefficient=1.2, adhd_assist=1.1
        difficulty = 3
        mood_coefficient = 1.2  # 気分5 -> 1.2
        adhd_assist = 1.1       # Pomodoro使用 -> 1.1
        
        # ?: 3 * 10 * 1.2 * 1.1 = 39.6 -> 39 XP (int)
        expected_xp = int(difficulty * 10 * mood_coefficient * adhd_assist)
        
        # 実装
        calculated_xp = self._calculate_task_xp(difficulty, mood_coefficient, adhd_assist)
        
        assert calculated_xp == expected_xp
        assert calculated_xp == 39
    
    def test_level_progression_algorithm(self, level_system):
        """レベル"""
        # ?
        test_cases = [
            (0, 1),      # 0 XP -> レベル1
            (100, 2),    # 100 XP -> レベル2
            (300, 3),    # 300 XP -> レベル3
            (700, 4),    # 700 XP -> レベル4
            (1500, 5),   # 1500 XP -> レベル5
        ]
        
        for total_xp, expected_level in test_cases:
            calculated_level = level_system.calculate_level(total_xp)
            assert calculated_level == expected_level, \
                f"XP {total_xp} should result in level {expected_level}, got {calculated_level}"
    
    def test_next_level_xp_calculation(self, level_system):
        """?XP計算"""
        test_cases = [
            (1, 100),    # レベル1 -> レベル2ま100 XP
            (2, 200),    # レベル2 -> レベル3ま200 XP
            (3, 400),    # レベル3 -> レベル4ま400 XP
            (4, 800),    # レベル4 -> レベル5ま800 XP
        ]
        
        for current_level, expected_xp in test_cases:
            required_xp = level_system.xp_for_next_level(current_level)
            assert required_xp == expected_xp, \
                f"Level {current_level} should require {expected_xp} XP for next level, got {required_xp}"
    
    def test_resonance_event_trigger_conditions(self, resonance_system):
        """共有"""
        # レベル5?
        test_cases = [
            (10, 5, True),   # ?5 -> 発
            (8, 3, True),    # ?5 -> 発
            (7, 3, False),   # ?4 -> 発
            (5, 5, False),   # ?0 -> 発
            (3, 8, True),    # ?5 -> 発
        ]
        
        for yu_level, player_level, should_trigger in test_cases:
            result = resonance_system.check_resonance_event(yu_level, player_level)
            assert result["resonance_triggered"] == should_trigger, \
                f"Yu:{yu_level}, Player:{player_level} should {'trigger' if should_trigger else 'not trigger'} resonance"
            
            if should_trigger:
                assert result["level_difference"] >= 5
                assert result["bonus_xp"] > 0
    
    def test_resonance_bonus_xp_calculation(self, resonance_system):
        """共有XP計算"""
        # レベルXP
        test_cases = [
            (10, 5, 100),    # ?5 -> 100 XP
            (12, 5, 140),    # ?7 -> 140 XP (20 XP/?)
            (8, 3, 100),     # ?5 -> 100 XP
        ]
        
        for yu_level, player_level, expected_bonus in test_cases:
            result = resonance_system.check_resonance_event(yu_level, player_level)
            if result["resonance_triggered"]:
                assert result["bonus_xp"] == expected_bonus, \
                    f"Level difference {abs(yu_level - player_level)} should give {expected_bonus} bonus XP"
    
    @pytest.mark.asyncio
    async def test_level_up_integration_flow(self, test_user_profile, level_system):
        """レベル"""
        # ?: レベル3, 250 XP
        current_level = test_user_profile.player_level
        current_xp = test_user_profile.total_xp
        
        # レベル4にXP: 700 XP (450 XP?)
        xp_needed = level_system.xp_for_next_level(current_level)
        additional_xp_needed = (2 ** (current_level + 1) - 1) * 100 - current_xp
        
        # ?
        big_task_xp = 500  # ?XP
        new_total_xp = current_xp + big_task_xp
        new_level = level_system.calculate_level(new_total_xp)
        
        # レベル
        assert new_level > current_level
        assert new_level == 4  # 750 XP -> レベル4
        
        # レベル
        test_user_profile.total_xp = new_total_xp
        test_user_profile.player_level = new_level
        
        # ?
        assert test_user_profile.player_level == 4
        assert test_user_profile.total_xp == 750
    
    @pytest.mark.asyncio
    async def test_yu_player_level_synchronization(self, test_user_profile, resonance_system):
        """ユーザー"""
        # ?: Yu=5, Player=3 (?2, 共有)
        initial_yu = test_user_profile.yu_level
        initial_player = test_user_profile.player_level
        
        # プレビューYuに
        test_user_profile.player_level = 5  # Yu=5, Player=5 (?0)
        
        result = resonance_system.check_resonance_event(
            test_user_profile.yu_level, 
            test_user_profile.player_level
        )
        assert result["resonance_triggered"] is False  # ?0な
        
        # プレビューYuを
        test_user_profile.player_level = 11  # Yu=5, Player=11 (?6)
        
        result = resonance_system.check_resonance_event(
            test_user_profile.yu_level,
            test_user_profile.player_level
        )
        assert result["resonance_triggered"] is True  # ?6で
        assert result["resonance_type"] == "player_ahead"
        assert result["bonus_xp"] == 120  # 6? * 20 XP
    
    @pytest.mark.asyncio
    async def test_crystal_gauge_level_integration(self, test_user_profile, crystal_gauge):
        """?"""
        # タスク
        task_completions = [
            ("Self-Discipline", 15),  # ?
            ("Curiosity", 20),        # ?
            ("Communication", 10),    # ?
            ("Resilience", 25),       # ?
        ]
        
        for attribute, points in task_completions:
            crystal_gauge.add_progress(attribute, points)
        
        # ?
        assert crystal_gauge.gauges["Self-Discipline"] == 45  # 30 + 15
        assert crystal_gauge.gauges["Curiosity"] == 50       # 30 + 20
        assert crystal_gauge.gauges["Communication"] == 40   # 30 + 10
        assert crystal_gauge.gauges["Resilience"] == 55      # 30 + 25
        
        # ? (100%で)
        for attribute in CRYSTAL_ATTRIBUTES:
            is_unlocked = crystal_gauge.is_chapter_unlocked(attribute)
            expected = crystal_gauge.gauges[attribute] >= 100
            assert is_unlocked == expected
    
    @pytest.mark.asyncio
    async def test_complete_xp_level_resonance_cycle(self, test_user_profile):
        """?XP-レベル-共有"""
        level_system = LevelSystem()
        resonance_system = ResonanceSystem()
        
        # 1?
        daily_tasks = [
            {"difficulty": 2, "mood": 1.1, "adhd": 1.0},  # 22 XP
            {"difficulty": 3, "mood": 1.2, "adhd": 1.1},  # 39 XP
            {"difficulty": 1, "mood": 0.9, "adhd": 1.2},  # 10 XP
            {"difficulty": 4, "mood": 1.0, "adhd": 1.3},  # 52 XP
        ]
        
        total_daily_xp = 0
        for task in daily_tasks:
            task_xp = self._calculate_task_xp(
                task["difficulty"], 
                task["mood"], 
                task["adhd"]
            )
            total_daily_xp += task_xp
        
        # ?: 22 + 39 + 10 + 52 = 123 XP
        assert total_daily_xp == 123
        
        # レベル
        new_total_xp = test_user_profile.total_xp + total_daily_xp  # 250 + 123 = 373
        new_level = level_system.calculate_level(new_total_xp)
        
        assert new_level == 3  # 373 XP -> ま3 (レベル4は700 XP?)
        
        # 共有 (Yu=5, Player=3, ?2)
        resonance_result = resonance_system.check_resonance_event(
            test_user_profile.yu_level, 
            new_level
        )
        assert resonance_result["resonance_triggered"] is False  # ?2で
        
        # ?XPで4?
        additional_xp = 350  # 373 + 350 = 723 XP -> レベル4
        final_total_xp = new_total_xp + additional_xp
        final_level = level_system.calculate_level(final_total_xp)
        
        assert final_level == 4
        
        # レベル4で (Yu=5, Player=4, ?1)
        final_resonance = resonance_system.check_resonance_event(
            test_user_profile.yu_level,
            final_level
        )
        assert final_resonance["resonance_triggered"] is False
    
    def test_edge_case_level_calculations(self, level_system):
        """エラー"""
        # ?
        edge_cases = [
            (99, 1),     # レベル2?
            (100, 2),    # レベル2?
            (101, 2),    # レベル2?
            (299, 2),    # レベル3?
            (300, 3),    # レベル3?
            (699, 3),    # レベル4?
            (700, 4),    # レベル4?
        ]
        
        for xp, expected_level in edge_cases:
            calculated_level = level_system.calculate_level(xp)
            assert calculated_level == expected_level, \
                f"XP {xp} should be level {expected_level}, got {calculated_level}"
    
    def test_resonance_event_types(self, resonance_system):
        """共有"""
        # Yuが
        result_yu_ahead = resonance_system.check_resonance_event(10, 5)
        assert result_yu_ahead["resonance_type"] == "yu_ahead"
        assert result_yu_ahead["message_type"] == "catch_up_encouragement"
        
        # プレビュー
        result_player_ahead = resonance_system.check_resonance_event(3, 8)
        assert result_player_ahead["resonance_type"] == "player_ahead"
        assert result_player_ahead["message_type"] == "yu_inspiration"
    
    # ヘルパー
    def _calculate_task_xp(self, difficulty: int, mood_coefficient: float, adhd_assist: float) -> int:
        """タスクXP計算"""
        base_xp = difficulty * 10
        return int(base_xp * mood_coefficient * adhd_assist)


if __name__ == "__main__":
    # 基本
    def run_basic_integration_test():
        test_instance = TestXPLevelResonanceIntegration()
        level_system = LevelSystem()
        resonance_system = ResonanceSystem()
        
        print("XP-レベル-共有...")
        
        # XP計算
        xp_result = test_instance._calculate_task_xp(3, 1.2, 1.1)
        print(f"XP計算: difficulty=3, mood=1.2, adhd=1.1 -> {xp_result} XP")
        
        # レベル
        level_result = level_system.calculate_level(750)
        print(f"レベル: 750 XP -> レベル {level_result}")
        
        # 共有
        resonance_result = resonance_system.check_resonance_event(8, 3)
        print(f"共有: Yu=8, Player=3 -> {resonance_result}")
        
        print("基本!")
    
    run_basic_integration_test()