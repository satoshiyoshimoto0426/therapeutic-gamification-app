"""
Mandala実装

?API実装

Requirements: 4.1, 4.3
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mandala_system import MandalaSystemInterface, CellStatus
from shared.interfaces.mandala_validation import MandalaValidator, MandalaBusinessRules


def test_mandala_grid_creation():
    """Mandala?"""
    print("=== Mandala? ===")
    
    interface = MandalaSystemInterface()
    test_uid = "validation_user_001"
    
    # ?
    grid = interface.get_or_create_grid(test_uid)
    print(f"? ?: UID={grid.uid}")
    print(f"? ?: {grid.total_cells}")
    print(f"? アプリ: {grid.unlocked_count}")
    
    # ?
    core_value_count = 0
    for x in range(9):
        for y in range(9):
            cell = grid.get_cell(x, y)
            if cell and cell.status == CellStatus.CORE_VALUE:
                core_value_count += 1
                print(f"  - 価({x},{y}): {cell.quest_title}")
    
    print(f"? ?: {core_value_count}/9")
    
    return interface, test_uid


def test_cell_unlock_functionality(interface, test_uid):
    """?"""
    print("\n=== ? ===")
    
    # ?
    test_positions = [
        (4, 2, "?", "5?", 25, 2),
        (4, 6, "?", "?", 30, 2),
        (2, 4, "?", "30?", 35, 3),
        (6, 4, "?", "?", 40, 3)
    ]
    
    for x, y, title, desc, xp, difficulty in test_positions:
        quest_data = {
            "quest_title": title,
            "quest_description": desc,
            "xp_reward": xp,
            "difficulty": difficulty,
            "therapeutic_focus": "Self-Discipline"
        }
        
        success = interface.unlock_cell_for_user(test_uid, x, y, quest_data)
        if success:
            print(f"? ?: ({x},{y}) - {title}")
        else:
            print(f"? ?: ({x},{y}) - {title}")
    
    # アプリ
    grid = interface.get_or_create_grid(test_uid)
    print(f"? アプリ: {grid.unlocked_count}")
    
    return grid


def test_cell_completion_functionality(interface, test_uid, grid):
    """?"""
    print("\n=== ? ===")
    
    # アプリ
    unlocked_cells = grid.get_unlocked_cells()
    completed_count = 0
    
    for cell in unlocked_cells[:2]:  # ?2つ
        x, y = cell.position
        success = interface.complete_cell_for_user(test_uid, x, y)
        if success:
            print(f"? ?: ({x},{y}) - {cell.quest_title}")
            completed_count += 1
        else:
            print(f"? ?: ({x},{y}) - {cell.quest_title}")
    
    # ?
    updated_grid = interface.get_or_create_grid(test_uid)
    completed_cells = updated_grid.get_completed_cells()
    print(f"? ?: {len(completed_cells)}")
    
    return updated_grid


def test_validation_functionality():
    """バリデーション"""
    print("\n=== バリデーション ===")
    
    validator = MandalaValidator()
    business_rules = MandalaBusinessRules()
    
    # ?
    interface = MandalaSystemInterface()
    grid = interface.get_or_create_grid("validation_test")
    
    structure_result = validator.validate_grid_structure(grid)
    print(f"? ?: {'成' if structure_result.is_valid else '?'}")
    if structure_result.warnings:
        for warning in structure_result.warnings:
            print(f"  ?: {warning}")
    
    # アプリ
    valid_quest_data = {
        "quest_title": "?",
        "quest_description": "?",
        "xp_reward": 25,
        "difficulty": 2
    }
    
    unlock_result = validator.validate_unlock_request(grid, 4, 2, valid_quest_data)
    print(f"? アプリ: {'成' if unlock_result.is_valid else '?'}")
    
    # 無
    invalid_quest_data = {
        "quest_title": "",  # ?
        "quest_description": "?",
        "xp_reward": 2000,  # ?XP
        "difficulty": 10    # ?
    }
    
    invalid_result = validator.validate_unlock_request(grid, 4, 2, invalid_quest_data)
    print(f"? 無: {'?' if not invalid_result.is_valid else '?'}")
    if not invalid_result.is_valid:
        print(f"  エラー: {invalid_result.error_message}")
    
    # ビジネス
    daily_unlock_result = business_rules.can_unlock_today(grid, 0)
    print(f"? ?: {'成' if daily_unlock_result.is_valid else '?'}")
    
    # ?
    limit_exceeded_result = business_rules.can_unlock_today(grid, 5)
    print(f"? ?: {'?' if not limit_exceeded_result.is_valid else '?'}")


def test_api_response_generation(interface, test_uid):
    """API?"""
    print("\n=== API? ===")
    
    # API?
    api_response = interface.get_grid_api_response(test_uid)
    
    print(f"? API?")
    print(f"  - UID: {api_response['uid']}")
    print(f"  - ?: {api_response['total_cells']}")
    print(f"  - アプリ: {api_response['unlocked_count']}")
    print(f"  - ?: {api_response['completion_rate']:.2%}")
    print(f"  - ?: {api_response['last_updated']}")
    
    # ?
    grid_data = api_response['grid']
    print(f"? ?: {len(grid_data)}x{len(grid_data[0])}")
    
    # ?
    core_values = api_response['core_values']
    print(f"? ?: {len(core_values)}?")
    
    # バリデーション
    validator = MandalaValidator()
    validation_result = validator.validate_api_response_data(api_response)
    print(f"? API?: {'成' if validation_result.is_valid else '?'}")
    
    return api_response


def test_daily_reminder_functionality(interface, test_uid):
    """?"""
    print("\n=== ? ===")
    
    # リスト
    reminder = interface.get_daily_reminder_for_user(test_uid)
    print(f"? ?: {reminder}")
    
    # ?
    reminders = set()
    for _ in range(5):
        reminder = interface.get_daily_reminder_for_user(test_uid)
        reminders.add(reminder)
    
    print(f"? リスト: {len(reminders)}?")


def test_serialization_functionality(interface, test_uid):
    """システム"""
    print("\n=== システム ===")
    
    # ?
    save_data = interface.save_grid(test_uid)
    print(f"? ?: {len(json.dumps(save_data))}バリデーション")
    
    # ?
    new_interface = MandalaSystemInterface()
    new_interface.load_grid(test_uid, save_data)
    
    # ?
    restored_response = new_interface.get_grid_api_response(test_uid)
    original_response = interface.get_grid_api_response(test_uid)
    
    # デフォルト
    data_match = (
        restored_response['unlocked_count'] == original_response['unlocked_count'] and
        restored_response['total_cells'] == original_response['total_cells'] and
        len(restored_response['core_values']) == len(original_response['core_values'])
    )
    
    print(f"? デフォルト: {'成' if data_match else '?'}")


def main():
    """メイン"""
    print("Mandala実装")
    print("=" * 50)
    
    try:
        # 1. ?
        interface, test_uid = test_mandala_grid_creation()
        
        # 2. ?
        grid = test_cell_unlock_functionality(interface, test_uid)
        
        # 3. ?
        updated_grid = test_cell_completion_functionality(interface, test_uid, grid)
        
        # 4. バリデーション
        test_validation_functionality()
        
        # 5. API?
        api_response = test_api_response_generation(interface, test_uid)
        
        # 6. ?
        test_daily_reminder_functionality(interface, test_uid)
        
        # 7. システム
        test_serialization_functionality(interface, test_uid)
        
        print("\n" + "=" * 50)
        print("? ?")
        print(f"?:")
        print(f"  - アプリ: {updated_grid.unlocked_count}")
        print(f"  - ?: {len(updated_grid.get_completed_cells())}")
        print(f"  - ?: {len(updated_grid.core_values)}")
        
    except Exception as e:
        print(f"\n? 検証: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)