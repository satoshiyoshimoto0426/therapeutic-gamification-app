"""
共有
Resonance event system comprehensive tests
Requirements: 4.4, 4.5
"""

import pytest
from datetime import datetime, timedelta
from shared.interfaces.resonance_system import (
    ResonanceType, ResonanceIntensity, ResonanceEvent, ResonanceCondition,
    ResonanceCalculator, ResonanceEventManager
)
from shared.interfaces.core_types import CrystalAttribute


class TestResonanceCalculator:
    """ResonanceCalculator?"""
    
    def test_resonance_intensity_calculation(self):
        """共有"""
        test_cases = [
            (5, ResonanceIntensity.WEAK),
            (7, ResonanceIntensity.WEAK),
            (8, ResonanceIntensity.MODERATE),
            (12, ResonanceIntensity.MODERATE),
            (13, ResonanceIntensity.STRONG),
            (20, ResonanceIntensity.STRONG),
            (21, ResonanceIntensity.INTENSE),
            (30, ResonanceIntensity.INTENSE)
        ]
        
        for level_diff, expected_intensity in test_cases:
            intensity = ResonanceCalculator.calculate_resonance_intensity(level_diff)
            assert intensity == expected_intensity
            print(f"? Level difference {level_diff} ? {intensity.value}")
    
    def test_bonus_xp_calculation(self):
        """?XP計算"""
        # 基本
        bonus_xp = ResonanceCalculator.calculate_bonus_xp(
            level_difference=5,
            player_level=10,
            resonance_type=ResonanceType.LEVEL_SYNC
        )
        
        assert bonus_xp >= 100  # ?XP
        print(f"? Basic resonance bonus: {bonus_xp} XP")
        
        # レベル
        high_diff_bonus = ResonanceCalculator.calculate_bonus_xp(
            level_difference=15,
            player_level=20,
            resonance_type=ResonanceType.CRYSTAL_HARMONY
        )
        
        assert high_diff_bonus > bonus_xp
        print(f"? High difference bonus: {high_diff_bonus} XP")
        
        # ?
        type_bonuses = {}
        for resonance_type in ResonanceType:
            bonus = ResonanceCalculator.calculate_bonus_xp(
                level_difference=10,
                player_level=15,
                resonance_type=resonance_type
            )
            type_bonuses[resonance_type.value] = bonus
            print(f"? {resonance_type.value}: {bonus} XP")
        
        # CRYSTAL_HARMONYが
        assert type_bonuses["crystal_harmony"] >= type_bonuses["level_sync"]
    
    def test_crystal_bonuses_calculation(self):
        """?"""
        bonuses = ResonanceCalculator.calculate_crystal_bonuses(
            resonance_type=ResonanceType.CRYSTAL_HARMONY,
            intensity=ResonanceIntensity.MODERATE,
            player_level=15
        )
        
        assert isinstance(bonuses, dict)
        assert len(bonuses) > 0
        
        # CRYSTAL_HARMONYは
        assert CrystalAttribute.WISDOM in bonuses
        assert CrystalAttribute.EMPATHY in bonuses
        assert CrystalAttribute.RESILIENCE in bonuses
        
        print(f"? Crystal harmony bonuses: {bonuses}")
        
        # ?
        for resonance_type in ResonanceType:
            type_bonuses = ResonanceCalculator.calculate_crystal_bonuses(
                resonance_type=resonance_type,
                intensity=ResonanceIntensity.STRONG,
                player_level=20
            )
            print(f"? {resonance_type.value} bonuses: {len(type_bonuses)} attributes")
    
    def test_therapeutic_message_generation(self):
        """治療"""
        message = ResonanceCalculator.generate_therapeutic_message(
            resonance_type=ResonanceType.EMOTIONAL_BOND,
            intensity=ResonanceIntensity.STRONG,
            player_level=15,
            yu_level=8
        )
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert "共有" in message or "?" in message
        print(f"? Therapeutic message: {message}")
        
        # ?
        for resonance_type in ResonanceType:
            for intensity in ResonanceIntensity:
                msg = ResonanceCalculator.generate_therapeutic_message(
                    resonance_type=resonance_type,
                    intensity=intensity,
                    player_level=10,
                    yu_level=5
                )
                assert len(msg) > 0
                print(f"? {resonance_type.value} + {intensity.value}: Message generated")


class TestResonanceEventManager:
    """ResonanceEventManager?"""
    
    def test_manager_initialization(self):
        """?"""
        manager = ResonanceEventManager()
        
        assert isinstance(manager.conditions, ResonanceCondition)
        assert len(manager.event_history) == 0
        assert len(manager.last_event_times) == 0
        print("? Resonance event manager initialized correctly")
    
    def test_resonance_conditions_check(self):
        """共有"""
        manager = ResonanceEventManager()
        
        # レベル
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level=5, yu_level=3  # レベル2
        )
        assert can_resonate is False
        assert resonance_type is None
        print("? Insufficient level difference rejected")
        
        # ?
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level=10, yu_level=3  # レベル7
        )
        assert can_resonate is True
        assert resonance_type is not None
        print(f"? Sufficient level difference accepted: {resonance_type.value}")
        
        # プレビュー
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level=2, yu_level=8  # レベル6だ
        )
        assert can_resonate is False
        print("? Low player level rejected")
    
    def test_resonance_event_trigger(self):
        """共有"""
        manager = ResonanceEventManager()
        
        event = manager.trigger_resonance_event(
            player_level=15,
            yu_level=8,
            resonance_type=ResonanceType.LEVEL_SYNC
        )
        
        assert isinstance(event, ResonanceEvent)
        assert event.resonance_type == ResonanceType.LEVEL_SYNC
        assert event.player_level == 15
        assert event.yu_level == 8
        assert event.level_difference == 7
        assert event.bonus_xp > 0
        assert len(event.therapeutic_message) > 0
        
        print(f"? Resonance event triggered:")
        print(f"  - Type: {event.resonance_type.value}")
        print(f"  - Intensity: {event.intensity.value}")
        print(f"  - Bonus XP: {event.bonus_xp}")
        print(f"  - Crystal bonuses: {len(event.crystal_bonuses)}")
        print(f"  - Special rewards: {len(event.special_rewards)}")
        
        # ?
        assert len(manager.event_history) == 1
        assert ResonanceType.LEVEL_SYNC in manager.last_event_times
    
    def test_cooldown_mechanism(self):
        """?"""
        manager = ResonanceEventManager()
        current_time = datetime.utcnow()
        
        # ?
        event1 = manager.trigger_resonance_event(
            player_level=15,
            yu_level=8,
            resonance_type=ResonanceType.LEVEL_SYNC,
            current_time=current_time
        )
        
        # ?
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level=16,
            yu_level=8,
            current_time=current_time + timedelta(hours=1)
        )
        
        # LEVEL_SYNCは
        if can_resonate:
            assert resonance_type != ResonanceType.LEVEL_SYNC
            print(f"? Cooldown working: different type selected ({resonance_type.value})")
        else:
            print("? Cooldown working: no resonance available")
        
        # 24?
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level=16,
            yu_level=8,
            current_time=current_time + timedelta(hours=25)
        )
        
        assert can_resonate is True
        print("? Cooldown expired: resonance available again")
    
    def test_resonance_statistics(self):
        """共有"""
        manager = ResonanceEventManager()
        
        # ?
        events_data = [
            (15, 8, ResonanceType.LEVEL_SYNC),
            (20, 10, ResonanceType.CRYSTAL_HARMONY),
            (25, 12, ResonanceType.EMOTIONAL_BOND),
            (18, 15, ResonanceType.WISDOM_SHARING)
        ]
        
        for player_level, yu_level, resonance_type in events_data:
            manager.trigger_resonance_event(player_level, yu_level, resonance_type)
        
        stats = manager.get_resonance_statistics()
        
        assert stats["total_events"] == 4
        assert len(stats["events_by_type"]) > 0
        assert len(stats["events_by_intensity"]) > 0
        assert stats["total_bonus_xp"] > 0
        assert stats["average_bonus_xp"] > 0
        assert stats["last_event"] is not None
        
        print("? Resonance statistics:")
        print(f"  - Total events: {stats['total_events']}")
        print(f"  - Events by type: {stats['events_by_type']}")
        print(f"  - Events by intensity: {stats['events_by_intensity']}")
        print(f"  - Total bonus XP: {stats['total_bonus_xp']}")
        print(f"  - Average bonus XP: {stats['average_bonus_xp']:.1f}")
    
    def test_resonance_simulation(self):
        """共有"""
        manager = ResonanceEventManager()
        
        simulation = manager.simulate_resonance_probability(
            player_level=20,
            yu_level=10,
            days_ahead=7
        )
        
        assert simulation["simulation_days"] == 7
        assert len(simulation["results"]) == 7
        assert "resonance_possible_days" in simulation
        
        print("? Resonance simulation:")
        print(f"  - Simulation days: {simulation['simulation_days']}")
        print(f"  - Possible resonance days: {simulation['resonance_possible_days']}")
        
        for day_result in simulation["results"][:3]:  # ?3?
            print(f"  - Day {day_result['day']}: {day_result['can_resonate']} ({day_result['resonance_type']})")


class TestResonanceIntegration:
    """共有"""
    
    def test_complete_resonance_workflow(self):
        """?"""
        manager = ResonanceEventManager()
        
        # システム: プレビュー20?8?12?
        player_level = 20
        yu_level = 8
        level_difference = abs(player_level - yu_level)
        
        print(f"? Starting resonance workflow:")
        print(f"  - Player Level: {player_level}")
        print(f"  - Yu Level: {yu_level}")
        print(f"  - Level Difference: {level_difference}")
        
        # 1. 共有
        can_resonate, resonance_type = manager.check_resonance_conditions(
            player_level, yu_level
        )
        
        assert can_resonate is True
        assert resonance_type is not None
        print(f"? Resonance conditions met: {resonance_type.value}")
        
        # 2. 共有
        event = manager.trigger_resonance_event(
            player_level, yu_level, resonance_type
        )
        
        # 3. ?
        expected_intensity = ResonanceCalculator.calculate_resonance_intensity(level_difference)
        assert event.intensity == expected_intensity
        assert event.bonus_xp >= 100
        assert len(event.crystal_bonuses) > 0
        assert len(event.special_rewards) > 0
        
        print(f"? Resonance event completed:")
        print(f"  - Event ID: {event.event_id}")
        print(f"  - Intensity: {event.intensity.value}")
        print(f"  - Bonus XP: {event.bonus_xp}")
        print(f"  - Crystal bonuses: {event.crystal_bonuses}")
        print(f"  - Special rewards: {event.special_rewards}")
        print(f"  - Message: {event.therapeutic_message}")
        
        # 4. システム
        stats = manager.get_resonance_statistics()
        assert stats["total_events"] == 1
        assert stats["total_bonus_xp"] == event.bonus_xp
        
        print("? Complete resonance workflow successful")
    
    def test_multiple_resonance_types(self):
        """?"""
        manager = ResonanceEventManager()
        current_time = datetime.utcnow()
        
        # ?
        resonance_scenarios = [
            (15, 8, ResonanceType.LEVEL_SYNC, 0),
            (18, 10, ResonanceType.CRYSTAL_HARMONY, 25),
            (22, 12, ResonanceType.EMOTIONAL_BOND, 50),
            (25, 15, ResonanceType.WISDOM_SHARING, 75)
        ]
        
        events = []
        for player_level, yu_level, resonance_type, hours_offset in resonance_scenarios:
            event_time = current_time + timedelta(hours=hours_offset)
            event = manager.trigger_resonance_event(
                player_level, yu_level, resonance_type, event_time
            )
            events.append(event)
            
            print(f"? {resonance_type.value} resonance:")
            print(f"  - Level difference: {abs(player_level - yu_level)}")
            print(f"  - Intensity: {event.intensity.value}")
            print(f"  - Bonus XP: {event.bonus_xp}")
        
        # ?
        stats = manager.get_resonance_statistics()
        assert stats["total_events"] == 4
        assert len(stats["events_by_type"]) == 4
        
        # ?1?
        for resonance_type in ResonanceType:
            assert stats["events_by_type"][resonance_type.value] == 1
        
        print("? Multiple resonance types test completed")
    
    def test_intensity_scaling(self):
        """?"""
        manager = ResonanceEventManager()
        
        # ?
        level_differences = [5, 10, 15, 25]  # WEAK, MODERATE, STRONG, INTENSE
        
        events = []
        for level_diff in level_differences:
            player_level = 20
            yu_level = player_level - level_diff
            
            event = manager.trigger_resonance_event(
                player_level, yu_level, ResonanceType.LEVEL_SYNC
            )
            events.append(event)
            
            print(f"? Level difference {level_diff}:")
            print(f"  - Intensity: {event.intensity.value}")
            print(f"  - Bonus XP: {event.bonus_xp}")
            print(f"  - Special rewards: {len(event.special_rewards)}")
        
        # ?
        for i in range(1, len(events)):
            assert events[i].bonus_xp >= events[i-1].bonus_xp
            # INTENSEレベル
            if events[i].intensity == ResonanceIntensity.INTENSE:
                assert len(events[i].special_rewards) >= len(events[i-1].special_rewards)
        
        print("? Intensity scaling test completed")


def run_all_tests():
    """?"""
    print("=== Running Resonance System Tests ===")
    
    # 共有
    calc_test = TestResonanceCalculator()
    calc_test.test_resonance_intensity_calculation()
    calc_test.test_bonus_xp_calculation()
    calc_test.test_crystal_bonuses_calculation()
    calc_test.test_therapeutic_message_generation()
    print("? Resonance calculator tests passed\n")
    
    # 共有
    manager_test = TestResonanceEventManager()
    manager_test.test_manager_initialization()
    manager_test.test_resonance_conditions_check()
    manager_test.test_resonance_event_trigger()
    manager_test.test_cooldown_mechanism()
    manager_test.test_resonance_statistics()
    manager_test.test_resonance_simulation()
    print("? Resonance event manager tests passed\n")
    
    # ?
    integration_test = TestResonanceIntegration()
    integration_test.test_complete_resonance_workflow()
    integration_test.test_multiple_resonance_types()
    integration_test.test_intensity_scaling()
    print("? Integration tests passed\n")
    
    print("=== All Resonance System Tests Passed! ===")


if __name__ == "__main__":
    run_all_tests()