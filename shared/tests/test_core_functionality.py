"""
コア
?
"""

import pytest
from datetime import datetime
from shared.interfaces.core_types import CrystalAttribute, CrystalGrowthEvent
from shared.interfaces.model_factory import (
    CrystalSystemFactory, MilestoneFactory, SynergyFactory, GameStateFactory
)
from shared.interfaces.crystal_validation import CrystalValidator, CrystalGrowthCalculator

class TestCrystalSystemIntegration:
    """?"""
    
    def test_complete_crystal_system_workflow(self):
        """?"""
        # 1. ?
        uid = "test_user_integration"
        crystal_system = CrystalSystemFactory.create_initial_crystal_system(uid)
        
        # ?
        assert crystal_system.uid == uid
        assert len(crystal_system.crystals) == 8
        assert crystal_system.total_growth_events == 0
        assert crystal_system.resonance_level == 0
        
        # 2. ?
        attribute = CrystalAttribute.SELF_DISCIPLINE
        event_type = CrystalGrowthEvent.TASK_COMPLETION
        
        # 成
        growth_amount = CrystalGrowthCalculator.calculate_growth_amount(
            attribute, event_type
        )
        assert growth_amount > 0
        
        # ?
        crystal = crystal_system.crystals[attribute]
        old_value = crystal.current_value
        
        updated_crystal, milestone_reached = CrystalValidator.apply_growth_to_crystal(
            crystal, growth_amount, datetime.utcnow()
        )
        
        # 成
        assert updated_crystal.current_value > old_value
        assert updated_crystal.last_growth_event is not None
        
        # 3. ?
        for _ in range(10):  # ?
            for attr in list(CrystalAttribute)[:4]:  # ?4つ
                growth = CrystalGrowthCalculator.calculate_growth_amount(
                    attr, CrystalGrowthEvent.TASK_COMPLETION
                )
                crystal_system.crystals[attr], _ = CrystalValidator.apply_growth_to_crystal(
                    crystal_system.crystals[attr], growth, datetime.utcnow()
                )
        
        # 共有
        new_resonance_level = CrystalValidator.calculate_resonance_level(crystal_system)
        assert new_resonance_level >= 0
        
        # 4. システム
        errors = CrystalValidator.validate_crystal_system_integrity(crystal_system)
        # 共有
        assert len([e for e in errors if "Resonance level mismatch" not in e]) == 0
        
        print(f"Integration test completed successfully!")
        print(f"Final resonance level: {new_resonance_level}")
        print(f"Crystal values: {[(attr.value, crystal.current_value) for attr, crystal in crystal_system.crystals.items()]}")

    def test_milestone_and_synergy_integration(self):
        """?"""
        # 1. ?
        discipline_milestones = MilestoneFactory.get_standard_milestones(
            CrystalAttribute.SELF_DISCIPLINE
        )
        assert len(discipline_milestones) > 0
        
        # ?
        first_milestone = discipline_milestones[0]
        assert first_milestone.threshold == 25
        assert first_milestone.title == "自動"
        assert len(first_milestone.rewards) > 0
        
        # 2. ?
        synergies = SynergyFactory.get_standard_synergies()
        assert len(synergies) > 0
        
        # ?
        first_synergy = synergies[0]
        assert len(first_synergy.required_attributes) >= 2
        assert len(first_synergy.min_levels) >= 2
        assert len(first_synergy.stat_bonuses) > 0
        
        # 3. システム
        crystal_system = CrystalSystemFactory.create_initial_crystal_system("test_user")
        
        # ?
        assert not CrystalValidator.check_synergy_requirements(crystal_system, first_synergy)
        
        # ?
        for attr, min_level in first_synergy.min_levels.items():
            crystal_system.crystals[attr].current_value = min_level
        
        # システム
        assert CrystalValidator.check_synergy_requirements(crystal_system, first_synergy)
        
        print("Milestone and synergy integration test passed!")

    def test_therapeutic_message_generation(self):
        """治療"""
        test_cases = [
            (CrystalAttribute.SELF_DISCIPLINE, CrystalGrowthEvent.TASK_COMPLETION, 3),
            (CrystalAttribute.EMPATHY, CrystalGrowthEvent.SOCIAL_INTERACTION, 6),
            (CrystalAttribute.RESILIENCE, CrystalGrowthEvent.CHALLENGE_OVERCOME, 10),
            (CrystalAttribute.WISDOM, CrystalGrowthEvent.REFLECTION_ENTRY, 8)
        ]
        
        for attribute, event_type, growth_amount in test_cases:
            message = CrystalGrowthCalculator.get_therapeutic_message(
                attribute, event_type, growth_amount
            )
            
            assert isinstance(message, str)
            assert len(message) > 0
            print(f"{attribute.value} + {event_type.value} ({growth_amount}): {message}")
        
        print("Therapeutic message generation test passed!")

    def test_harmony_bonus_calculation(self):
        """?"""
        crystal_system = CrystalSystemFactory.create_initial_crystal_system("test_user")
        
        # 1. ?0の
        harmony_bonus = CrystalValidator.calculate_harmony_bonus(crystal_system)
        assert harmony_bonus >= 1.0
        
        # 2. ?
        for crystal in crystal_system.crystals.values():
            crystal.current_value = 25
        
        harmony_bonus_equal = CrystalValidator.calculate_harmony_bonus(crystal_system)
        assert harmony_bonus_equal >= harmony_bonus  # ?
        
        # 3. ?
        crystal_system.crystals[CrystalAttribute.SELF_DISCIPLINE].current_value = 80
        crystal_system.crystals[CrystalAttribute.EMPATHY].current_value = 5
        
        harmony_bonus_unequal = CrystalValidator.calculate_harmony_bonus(crystal_system)
        assert harmony_bonus_unequal < harmony_bonus_equal
        
        print(f"Harmony bonuses - Initial: {harmony_bonus:.2f}, Equal: {harmony_bonus_equal:.2f}, Unequal: {harmony_bonus_unequal:.2f}")
        print("Harmony bonus calculation test passed!")

class TestGameStateFactory:
    """ゲーム"""
    
    def test_initial_game_state_creation(self):
        """?"""
        game_state = GameStateFactory.create_initial_game_state()
        
        assert game_state.player_level == 1
        assert game_state.yu_level == 1
        assert game_state.total_xp == 0
        assert game_state.last_resonance_event is None
        assert len(game_state.crystal_gauges) == len(list(CrystalAttribute))
        
        print("Initial game state creation test passed!")
    
    def test_user_profile_creation(self):
        """ユーザー"""
        uid = "test_user_profile"
        email = "test@example.com"
        display_name = "?"
        
        profile = GameStateFactory.create_user_profile(
            uid=uid,
            email=email,
            display_name=display_name,
            adhd_profile={"pomodoro_duration": 25},
            therapeutic_goals=["自動", "ストーリー"]
        )
        
        assert profile.uid == uid
        assert profile.email == email
        assert profile.display_name == display_name
        assert profile.player_level == 1
        assert profile.yu_level == 1
        assert profile.total_xp == 0
        assert len(profile.crystal_gauges) == 8  # __init__で
        assert profile.adhd_profile["pomodoro_duration"] == 25
        assert "自動" in profile.therapeutic_goals
        
        print("User profile creation test passed!")

def run_all_tests():
    """?"""
    print("=== Running Core Functionality Integration Tests ===")
    
    # ?
    integration_test = TestCrystalSystemIntegration()
    integration_test.test_complete_crystal_system_workflow()
    integration_test.test_milestone_and_synergy_integration()
    integration_test.test_therapeutic_message_generation()
    integration_test.test_harmony_bonus_calculation()
    
    # ゲーム
    factory_test = TestGameStateFactory()
    factory_test.test_initial_game_state_creation()
    factory_test.test_user_profile_creation()
    
    print("\n=== All Core Functionality Tests Passed! ===")

if __name__ == "__main__":
    run_all_tests()