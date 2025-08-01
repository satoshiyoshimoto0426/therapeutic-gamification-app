#!/usr/bin/env python3
"""
タスク4: Mandalaシステム9x9?

?4.1と4.2の
"""

import sys
import os

# プレビュー
sys.path.append(os.path.dirname(__file__))

from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid, CellStatus
from shared.interfaces.mandala_validation import MandalaValidator


def verify_task_4_1():
    """4.1 MandalaGrid?"""
    print("=== タスク4.1: MandalaGrid? ===")
    
    # 9x9?
    grid = MandalaGrid("test_user")
    assert grid.total_cells == 81, "9x9?81?"
    assert len(grid.grid) == 9, "?9で"
    assert len(grid.grid[0]) == 9, "?9で"
    print("? 9x9?")
    
    # ?ACT?
    core_value_positions = [(4, 4), (3, 4), (5, 4), (4, 3), (4, 5), (3, 3), (5, 5), (3, 5), (5, 3)]
    for x, y in core_value_positions:
        cell = grid.get_cell(x, y)
        assert cell is not None, f"?({x}, {y})が"
        assert cell.status == CellStatus.CORE_VALUE, f"?({x}, {y})が"
        assert cell.therapeutic_focus is not None, f"?({x}, {y})に"
    print("? ?ACT?")
    
    # ?
    serialized = grid.serialize_grid()
    assert "uid" in serialized, "システムuidが"
    assert "grid" in serialized, "システムgridが"
    assert "core_values" in serialized, "システムcore_valuesが"
    assert len(serialized["grid"]) == 9, "システム9で"
    print("? ?")
    
    # デフォルト
    restored_grid = MandalaGrid.deserialize_grid(serialized)
    assert restored_grid.uid == grid.uid, "?uidが"
    assert restored_grid.total_cells == grid.total_cells, "?"
    print("? ?")
    
    print("タスク4.1: ? ?\n")


def verify_task_4_2():
    """4.2 ?API実装"""
    print("=== タスク4.2: ?API実装 ===")
    
    interface = MandalaSystemInterface()
    validator = MandalaValidator()
    test_uid = "test_user_4_2"
    
    # ?
    grid = interface.get_or_create_grid(test_uid)
    
    # ?
    assert grid.can_unlock(4, 2), "?(4,2)が"
    
    # ?
    assert not grid.can_unlock(0, 0), "?(0,0)が"
    print("? ?")
    
    # ?
    quest_data = {
        "quest_title": "?",
        "quest_description": "?",
        "xp_reward": 25,
        "difficulty": 2,
        "therapeutic_focus": "Mindfulness"
    }
    
    success = interface.unlock_cell_for_user(test_uid, 4, 2, quest_data)
    assert success, "?"
    
    updated_grid = interface.get_or_create_grid(test_uid)
    assert updated_grid.unlocked_count == 1, "アプリ"
    
    unlocked_cell = updated_grid.get_cell(4, 2)
    assert unlocked_cell is not None, "アプリ"
    assert unlocked_cell.status == CellStatus.UNLOCKED, "?UNLOCKEDで"
    print("? ?")
    
    # API?
    api_response = interface.get_grid_api_response(test_uid)
    assert "uid" in api_response, "API?uidが"
    assert "grid" in api_response, "API?gridが"
    assert "unlocked_count" in api_response, "API?unlocked_countが"
    assert "completion_rate" in api_response, "API?completion_rateが"
    print("? API?")
    
    # ログ
    validation_result = validator.validate_api_response_data(api_response)
    assert validation_result.is_valid, f"API?: {validation_result.error_message}"
    print("? ログJSON?")
    
    print("タスク4.2: ? ?\n")


def main():
    """メイン"""
    print("タスク4: Mandalaシステム9x9?\n")
    
    try:
        verify_task_4_1()
        verify_task_4_2()
        
        print("? タスク4: Mandalaシステム9x9? - ?!")
        print("   - 4.1 MandalaGrid?: ?")
        print("   - 4.2 ?API実装: ?")
        print("\n?4.1, 4.3が")
        
        return True
        
    except Exception as e:
        print(f"? 検証: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)