"""
レベル
Level system comprehensive tests
Requirements: 4.4, 4.5
"""

import pytest
import math
from datetime import datetime
from shared.interfaces.level_system import (
    LevelCalculator, PlayerLevelManager, YuLevelManager, 
    LevelSystemManager, LevelProgression
)


class TestLevelCalculator:
    """LevelCalculator?"""
    
    def test_basic_xp_calculation(self):
        """基本XP計算"""
        # レベル1は0XP
        assert LevelCalculator.calculate_xp_for_level(1) == 0
        
        # レベル2はXP
        level_2_xp = LevelCalculator.calculate_xp_for_level(2)
        assert level_2_xp > 0
        print(f"? Level 2 requires: {level_2_xp} XP")
        
        # レベル3はXP
        level_3_xp = LevelCalculator.calculate_xp_for_level(3)
        assert level_3_xp > level_2_xp
        print(f"? Level 3 requires: {level_3_xp} XP")
        
        # ?
        level_10_xp = LevelCalculator.calculate_xp_for_level(10)
        level_20_xp = LevelCalculator.calculate_xp_for_level(20)
        
        # レベル20は10の2?XPが
        assert level_20_xp > level_10_xp * 2
        print(f"? Level 10: {level_10_xp} XP, Level 20: {level_20_xp} XP")
    
    def test_exponential_growth(self):
        """?"""
        xp_values = []
        for level in [1, 5, 10, 15, 20, 25, 30]:
            xp = LevelCalculator.calculate_xp_for_level(level)
            xp_values.append((level, xp))
            print(f"? Level {level}: {xp:,} XP")
        
        # 成
        for i in range(1, len(xp_values)):
            prev_level, prev_xp = xp_values[i-1]
            curr_level, curr_xp = xp_values[i]
            
            if prev_xp > 0:
                growth_rate = curr_xp / prev_xp
                # ?1?
                assert growth_rate > 1.0
    
    def test_level_from_xp(self):
        """XPか"""
        test_cases = [
            (0, 1),      # 0XPは1
            (50, 1),     # ?XPは1
            (100, 2),    # 基本XPで2
            (500, 3),    # ?XPで
        ]
        
        for xp, expected_min_level in test_cases:
            calculated_level = LevelCalculator.get_level_from_xp(xp)
            assert calculated_level >= expected_min_level
            print(f"? {xp} XP = Level {calculated_level}")
    
    def test_level_progression(self):
        """レベル"""
        test_xp = 1000
        progression = LevelCalculator.get_level_progression(test_xp)
        
        assert isinstance(progression, LevelProgression)
        assert progression.current_level >= 1
        assert progression.current_xp == test_xp
        assert progression.xp_for_current_level <= test_xp
        assert progression.xp_for_next_level > test_xp
        assert progression.xp_needed_for_next > 0
        assert 0 <= progression.progress_percentage <= 100
        
        print(f"? {test_xp} XP progression:")
        print(f"  - Current Level: {progression.current_level}")
        print(f"  - Progress: {progression.progress_percentage:.1f}%")
        print(f"  - XP needed for next: {progression.xp_needed_for_next}")
    
    def test_level_up_rewards(self):
        """レベル"""
        # レベル4か6?5で
        rewards = LevelCalculator.calculate_level_up_rewards(4, 6)
        assert len(rewards) > 0
        assert any("milestone_reward_level_5" in reward for reward in rewards)
        print(f"? Level 4?6 rewards: {rewards}")
        
        # レベル9か11?10で
        rewards = LevelCalculator.calculate_level_up_rewards(9, 11)
        assert any("major_milestone_level_10" in reward for reward in rewards)
        assert any("bonus_crystal_growth" in reward for reward in rewards)
        print(f"? Level 9?11 rewards: {rewards}")


class TestPlayerLevelManager:
    """PlayerLevelManager?"""
    
    def test_initial_state(self):
        """?"""
        manager = PlayerLevelManager(initial_xp=0)
        
        assert manager.total_xp == 0
        assert manager.level_progression.current_level == 1
        assert len(manager.level_history) == 0
        print("? Player manager initialized correctly")
    
    def test_xp_addition_without_level_up(self):
        """レベルXP?"""
        manager = PlayerLevelManager(initial_xp=0)
        
        result = manager.add_xp(50, "test_task")
        
        assert result["xp_added"] == 50
        assert result["level_up"] is False
        assert result["old_level"] == 1
        assert result["new_level"] == 1
        assert len(result["rewards"]) == 0
        assert manager.total_xp == 50
        
        print(f"? Added 50 XP without level up: Level {result['new_level']}")
    
    def test_xp_addition_with_level_up(self):
        """レベルXP?"""
        manager = PlayerLevelManager(initial_xp=0)
        
        # ?XPを
        large_xp = 500
        result = manager.add_xp(large_xp, "major_achievement")
        
        assert result["xp_added"] == large_xp
        assert result["level_up"] is True
        assert result["new_level"] > result["old_level"]
        assert len(result["rewards"]) > 0
        assert len(manager.level_history) > 0
        
        print(f"? Added {large_xp} XP with level up: Level {result['old_level']}?{result['new_level']}")
        print(f"  - Rewards: {result['rewards']}")
    
    def test_xp_breakdown(self):
        """XP内部"""
        manager = PlayerLevelManager(initial_xp=300)
        breakdown = manager.get_xp_breakdown()
        
        assert breakdown["total_xp"] == 300
        assert breakdown["current_level"] >= 1
        assert breakdown["xp_for_current_level"] <= 300
        assert breakdown["xp_for_next_level"] > 300
        assert breakdown["xp_needed_for_next"] > 0
        assert 0 <= breakdown["progress_percentage"] <= 100
        
        print("? XP breakdown:")
        for key, value in breakdown.items():
            print(f"  - {key}: {value}")
    
    def test_xp_simulation(self):
        """XP?"""
        manager = PlayerLevelManager(initial_xp=100)
        original_xp = manager.total_xp
        original_level = manager.level_progression.current_level
        
        # システム
        simulation = manager.simulate_xp_addition(400)
        
        # 実装XPや
        assert manager.total_xp == original_xp
        assert manager.level_progression.current_level == original_level
        
        # システム
        assert simulation["simulated_total_xp"] == original_xp + 400
        assert simulation["simulated_level"] >= original_level
        
        print(f"? XP simulation: {original_xp}?{simulation['simulated_total_xp']} XP")
        print(f"  - Level: {original_level}?{simulation['simulated_level']}")
        print(f"  - Level up: {simulation['level_up']}")


class TestYuLevelManager:
    """YuLevelManager?"""
    
    def test_initial_state(self):
        """?"""
        manager = YuLevelManager(initial_level=1)
        
        assert manager.current_level == 1
        assert len(manager.growth_events) == 0
        assert len(manager.personality_traits) == 4
        assert all(0 <= trait <= 1 for trait in manager.personality_traits.values())
        
        print("? Yu manager initialized correctly")
        print(f"  - Personality traits: {manager.personality_traits}")
    
    def test_natural_growth(self):
        """自動"""
        manager = YuLevelManager(initial_level=1)
        
        # プレビュー
        result = manager.grow_naturally(player_level=10, days_passed=5)
        
        # 成
        if result["growth_occurred"]:
            assert result["new_level"] > result["old_level"]
            assert len(manager.growth_events) > 0
            print(f"? Yu natural growth: Level {result['old_level']}?{result['new_level']}")
        else:
            print("? Yu natural growth: No growth this time")
        
        print(f"  - Personality traits: {result['personality_traits']}")
    
    def test_interaction_growth(self):
        """?"""
        manager = YuLevelManager(initial_level=1)
        
        # ?
        interaction_types = ["story_choice", "task_completion", "crystal_resonance", "emotional_support"]
        growth_occurred = False
        
        for interaction in interaction_types:
            result = manager.grow_from_interaction(interaction, player_level=5)
            if result["growth_occurred"]:
                growth_occurred = True
                print(f"? Yu interaction growth ({interaction}): Level {result['old_level']}?{result['new_level']}")
                break
        
        if not growth_occurred:
            print("? Yu interaction growth: No growth occurred (probabilistic)")
    
    def test_personality_description(self):
        """?"""
        manager = YuLevelManager(initial_level=1)
        
        # ?
        manager.personality_traits["wisdom"] = 0.8
        
        description = manager.get_personality_description()
        assert isinstance(description, str)
        assert len(description) > 0
        assert "?" in description or "wisdom" in description.lower()
        
        print(f"? Yu personality description: {description}")


class TestLevelSystemManager:
    """LevelSystemManager?"""
    
    def test_system_initialization(self):
        """システム"""
        manager = LevelSystemManager(player_xp=200, yu_level=2)
        
        assert manager.player_manager.total_xp == 200
        assert manager.yu_manager.current_level == 2
        assert len(manager.system_events) == 0
        
        print("? Level system manager initialized correctly")
    
    def test_integrated_xp_addition(self):
        """?XP?"""
        manager = LevelSystemManager(player_xp=100, yu_level=1)
        
        result = manager.add_player_xp(300, "integrated_test")
        
        assert "player" in result
        assert "yu" in result
        assert "system_event" in result
        assert len(manager.system_events) == 1
        
        player_result = result["player"]
        yu_result = result["yu"]
        
        print(f"? Integrated XP addition:")
        print(f"  - Player: Level {player_result['old_level']}?{player_result['new_level']}")
        print(f"  - Yu: Level {yu_result['old_level']}?{yu_result['new_level']}")
    
    def test_yu_interaction_trigger(self):
        """ユーザー"""
        manager = LevelSystemManager(player_xp=500, yu_level=2)
        
        result = manager.trigger_yu_interaction("story_choice")
        
        assert "yu" in result
        assert "system_event" in result
        assert len(manager.system_events) == 1
        
        print(f"? Yu interaction triggered: {result['yu']['growth_occurred']}")
    
    def test_system_status(self):
        """システム"""
        manager = LevelSystemManager(player_xp=1000, yu_level=3)
        
        status = manager.get_system_status()
        
        assert "player" in status
        assert "yu" in status
        assert "level_difference" in status
        assert "recent_events" in status
        
        assert status["player"]["xp"] == 1000
        assert status["yu"]["level"] == 3
        assert isinstance(status["level_difference"], int)
        
        print("? System status:")
        print(f"  - Player Level: {status['player']['level']} (XP: {status['player']['xp']})")
        print(f"  - Yu Level: {status['yu']['level']}")
        print(f"  - Level Difference: {status['level_difference']}")
        print(f"  - Yu Description: {status['yu']['description']}")


class TestLevelSystemIntegration:
    """レベル"""
    
    def test_complete_level_progression(self):
        """?"""
        manager = LevelSystemManager(player_xp=0, yu_level=1)
        
        # ?XPを
        xp_additions = [100, 200, 300, 500, 1000]
        
        for xp in xp_additions:
            result = manager.add_player_xp(xp, f"progression_test_{xp}")
            
            player_level = result["player"]["new_level"]
            yu_level = result["yu"]["new_level"]
            
            print(f"? Added {xp} XP: Player L{player_level}, Yu L{yu_level}")
            
            # プレビューXP?
            assert player_level >= 1
            
            # ユーザー
            assert yu_level <= player_level + 2  # ?
        
        # ?
        final_status = manager.get_system_status()
        print(f"? Final state: Player L{final_status['player']['level']}, Yu L{final_status['yu']['level']}")
        
        # システム
        assert len(manager.system_events) == len(xp_additions)
    
    def test_level_calculation_consistency(self):
        """レベル"""
        # ?XP?
        test_xp_values = [0, 100, 500, 1000, 2000, 5000, 10000]
        
        for xp in test_xp_values:
            level = LevelCalculator.get_level_from_xp(xp)
            required_xp = LevelCalculator.calculate_xp_for_level(level)
            next_level_xp = LevelCalculator.calculate_xp_for_level(level + 1)
            
            # ?XP?
            assert xp >= required_xp
            
            # ?XP?
            assert xp < next_level_xp
            
            print(f"? {xp} XP = Level {level} (range: {required_xp}-{next_level_xp-1})")


def run_all_tests():
    """?"""
    print("=== Running Level System Tests ===")
    
    # レベル
    calc_test = TestLevelCalculator()
    calc_test.test_basic_xp_calculation()
    calc_test.test_exponential_growth()
    calc_test.test_level_from_xp()
    calc_test.test_level_progression()
    calc_test.test_level_up_rewards()
    print("? Level calculator tests passed\n")
    
    # プレビュー
    player_test = TestPlayerLevelManager()
    player_test.test_initial_state()
    player_test.test_xp_addition_without_level_up()
    player_test.test_xp_addition_with_level_up()
    player_test.test_xp_breakdown()
    player_test.test_xp_simulation()
    print("? Player level manager tests passed\n")
    
    # ユーザー
    yu_test = TestYuLevelManager()
    yu_test.test_initial_state()
    yu_test.test_natural_growth()
    yu_test.test_interaction_growth()
    yu_test.test_personality_description()
    print("? Yu level manager tests passed\n")
    
    # システム
    system_test = TestLevelSystemManager()
    system_test.test_system_initialization()
    system_test.test_integrated_xp_addition()
    system_test.test_yu_interaction_trigger()
    system_test.test_system_status()
    print("? Level system manager tests passed\n")
    
    # ?
    integration_test = TestLevelSystemIntegration()
    integration_test.test_complete_level_progression()
    integration_test.test_level_calculation_consistency()
    print("? Integration tests passed\n")
    
    print("=== All Level System Tests Passed! ===")


if __name__ == "__main__":
    run_all_tests()