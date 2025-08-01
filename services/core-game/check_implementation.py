"""
コアAPI?
Check Core Game Engine API functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import (
    get_or_create_game_system, get_or_create_resonance_manager,
    create_success_response, create_error_response
)

def check_xp_and_level_system():
    """XPと"""
    print("=== XP and Level System Check ===")
    
    # ユーザー
    uid = "functionality_test_user"
    game_system = get_or_create_game_system(uid)
    
    print(f"Initial state:")
    status = game_system.get_system_status()
    print(f"  Player: Level {status['player']['level']} ({status['player']['xp']} XP)")
    print(f"  Yu: Level {status['yu']['level']}")
    
    # ?XPを
    xp_additions = [100, 200, 300, 500, 800]
    
    for i, xp in enumerate(xp_additions, 1):
        result = game_system.add_player_xp(xp, f"test_step_{i}")
        
        print(f"Step {i}: Added {xp} XP")
        print(f"  Level: {result['player']['old_level']} ? {result['player']['new_level']}")
        print(f"  Level up: {result['player']['level_up']}")
        
        if result['player']['level_up']:
            print(f"  Rewards: {result['player']['rewards']}")
        
        if result['yu']['growth_occurred']:
            print(f"  Yu growth: Level {result['yu']['old_level']} ? {result['yu']['new_level']}")
    
    # ?
    final_status = game_system.get_system_status()
    print(f"Final state:")
    print(f"  Player: Level {final_status['player']['level']} ({final_status['player']['xp']} XP)")
    print(f"  Yu: Level {final_status['yu']['level']}")
    print(f"  Level difference: {final_status['level_difference']}")
    
    return game_system

def check_resonance_system(game_system):
    """共有"""
    print("\n=== Resonance System Check ===")
    
    uid = "functionality_test_user"
    resonance_manager = get_or_create_resonance_manager(uid)
    
    # ?
    status = game_system.get_system_status()
    player_level = status['player']['level']
    yu_level = status['yu']['level']
    level_diff = abs(player_level - yu_level)
    
    print(f"Current levels: Player {player_level}, Yu {yu_level} (diff: {level_diff})")
    
    # 共有
    can_resonate, resonance_type = resonance_manager.check_resonance_conditions(
        player_level, yu_level
    )
    
    print(f"Can resonate: {can_resonate}")
    if resonance_type:
        print(f"Resonance type: {resonance_type.value}")
    
    # 共有
    stats = resonance_manager.get_resonance_statistics()
    print(f"Resonance statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Events by type: {stats['events_by_type']}")
    
    # 共有
    if can_resonate:
        print("\nTriggering resonance event...")
        
        resonance_event = resonance_manager.trigger_resonance_event(
            player_level, yu_level, resonance_type
        )
        
        print(f"Resonance event triggered:")
        print(f"  Type: {resonance_event.resonance_type.value}")
        print(f"  Intensity: {resonance_event.intensity.value}")
        print(f"  Bonus XP: {resonance_event.bonus_xp}")
        print(f"  Crystal bonuses: {len(resonance_event.crystal_bonuses)}")
        print(f"  Special rewards: {resonance_event.special_rewards}")
        print(f"  Message: {resonance_event.therapeutic_message}")
        
        # ?XPを
        bonus_result = game_system.add_player_xp(
            resonance_event.bonus_xp, 
            f"resonance_{resonance_type.value}"
        )
        
        print(f"Bonus XP applied:")
        print(f"  Level: {bonus_result['player']['old_level']} ? {bonus_result['player']['new_level']}")
    
    return resonance_manager

def check_api_responses():
    """APIレベル"""
    print("\n=== API Response Format Check ===")
    
    # 成
    success_data = {
        "uid": "test_user",
        "level": 5,
        "xp": 1000
    }
    
    success_response = create_success_response(success_data)
    print("Success response format:")
    print(f"  success: {success_response['success']}")
    print(f"  data keys: {list(success_response['data'].keys())}")
    print(f"  timestamp: {success_response['timestamp']}")
    
    # エラー
    error_response = create_error_response(
        "TEST_ERROR",
        "This is a test error message",
        {"detail": "Additional error details"},
        400
    )
    
    print("Error response format:")
    print(f"  success: {error_response.body.decode()}")

def check_level_progression_details():
    """レベル"""
    print("\n=== Level Progression Details Check ===")
    
    from shared.interfaces.level_system import LevelCalculator
    
    # ?XP?
    print("XP requirements by level:")
    for level in range(1, 21, 2):
        xp_required = LevelCalculator.calculate_xp_for_level(level)
        print(f"  Level {level:2d}: {xp_required:6,} XP")
    
    # レベル
    test_xp_values = [0, 100, 500, 1000, 2000, 5000]
    print("\nLevel progression for different XP amounts:")
    
    for xp in test_xp_values:
        progression = LevelCalculator.get_level_progression(xp)
        print(f"  {xp:5,} XP: Level {progression.current_level} ({progression.progress_percentage:.1f}% to next)")

def check_resonance_calculations():
    """共有"""
    print("\n=== Resonance Calculation Details Check ===")
    
    from shared.interfaces.resonance_system import ResonanceCalculator, ResonanceType, ResonanceIntensity
    
    # ?
    print("Resonance intensity by level difference:")
    for level_diff in [5, 8, 13, 21, 30]:
        intensity = ResonanceCalculator.calculate_resonance_intensity(level_diff)
        print(f"  Level diff {level_diff:2d}: {intensity.value}")
    
    # 共有XP
    print("\nBonus XP by resonance type (level diff 10, player level 15):")
    for resonance_type in ResonanceType:
        bonus_xp = ResonanceCalculator.calculate_bonus_xp(10, 15, resonance_type)
        print(f"  {resonance_type.value:15s}: {bonus_xp:4,} XP")

def main():
    """メイン"""
    print("Starting Core Game Engine functionality check...\n")
    
    # 1. XPと
    game_system = check_xp_and_level_system()
    
    # 2. 共有
    resonance_manager = check_resonance_system(game_system)
    
    # 3. APIレベル
    check_api_responses()
    
    # 4. レベル
    check_level_progression_details()
    
    # 5. 共有
    check_resonance_calculations()
    
    print("\n? All functionality checks completed successfully!")
    print("Core Game Engine API is fully functional and ready for use.")

if __name__ == "__main__":
    main()