"""
Simple Mandala System Test

基本Mandalaシステム
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mandala_system import MandalaGrid, CellStatus, MandalaSystemInterface


def test_basic_functionality():
    """基本"""
    print("=== Mandala System Basic Test ===")
    
    # 1. ?
    print("1. ?")
    grid = MandalaGrid("test_user_001")
    print(f"   UID: {grid.uid}")
    print(f"   ?: {len(grid.grid)}x{len(grid.grid[0])}")
    print(f"   ?: {len(grid.core_values)}")
    print(f"   ?: {grid.total_cells}")
    assert len(grid.grid) == 9
    assert len(grid.grid[0]) == 9
    assert len(grid.core_values) == 9
    print("   ? ?")
    
    # 2. ?
    print("\n2. ?")
    center_cell = grid.grid[4][4]
    print(f"   ?: {center_cell.quest_title}")
    print(f"   ストーリー: {center_cell.status}")
    assert center_cell.quest_title == "Core Self"
    assert center_cell.status == CellStatus.CORE_VALUE
    print("   ? ?")
    
    # 3. ?
    print("\n3. ?")
    quest_data = {
        "cell_id": "test_cell_001",
        "quest_title": "?",
        "quest_description": "?30?",
        "xp_reward": 50,
        "difficulty": 2,
        "therapeutic_focus": "Self-Discipline"
    }
    
    result = grid.unlock_cell(3, 3, quest_data)
    print(f"   アプリ: {result}")
    print(f"   アプリ: {grid.unlocked_count}")
    
    cell = grid.grid[3][3]
    print(f"   ?: {cell.quest_title}")
    print(f"   ?: {cell.status}")
    assert result is True
    assert grid.unlocked_count == 1
    assert cell.quest_title == "?"
    print("   ? ?")
    
    # 4. ?
    print("\n4. ?")
    complete_result = grid.complete_cell(3, 3)
    print(f"   ?: {complete_result}")
    
    completed_cell = grid.grid[3][3]
    print(f"   ?: {completed_cell.status}")
    print(f"   ?: {completed_cell.completion_time}")
    assert complete_result is True
    assert completed_cell.status == CellStatus.COMPLETED
    print("   ? ?")
    
    # 5. システム
    print("\n5. システム")
    serialized = grid.serialize_grid()
    print(f"   システム: {list(serialized.keys())}")
    print(f"   UID: {serialized['uid']}")
    print(f"   アプリ: {serialized['unlocked_count']}")
    assert serialized["uid"] == "test_user_001"
    assert serialized["unlocked_count"] == 1
    print("   ? システム")
    
    # 6. ?
    print("\n6. ?")
    reminder = grid.get_daily_core_value_reminder()
    print(f"   リスト: {reminder}")
    assert isinstance(reminder, str)
    assert len(reminder) > 0
    assert "?" in reminder
    print("   ? ?")
    
    print("\n=== All Tests Passed! ===")


def test_system_interface():
    """システム"""
    print("\n=== Mandala System Interface Test ===")
    
    interface = MandalaSystemInterface()
    
    # 1. ?
    print("1. ?")
    grid1 = interface.get_or_create_grid("user1")
    grid2 = interface.get_or_create_grid("user1")  # ?
    grid3 = interface.get_or_create_grid("user2")  # ?
    
    print(f"   ?1 UID: {grid1.uid}")
    print(f"   ?2 UID: {grid2.uid}")
    print(f"   ?3 UID: {grid3.uid}")
    print(f"   ?1と2は: {grid1 is grid2}")
    print(f"   管理: {len(interface.grids)}")
    
    assert grid1 is grid2
    assert grid1 is not grid3
    assert len(interface.grids) == 2
    print("   ? ?")
    
    # 2. API?
    print("\n2. API?")
    api_response = interface.get_grid_api_response("user1")
    print(f"   API?: {list(api_response.keys())}")
    print(f"   UID: {api_response['uid']}")
    print(f"   ?: {api_response['total_cells']}")
    
    assert "uid" in api_response
    assert "grid" in api_response
    assert api_response["uid"] == "user1"
    assert api_response["total_cells"] == 81
    print("   ? API?")
    
    print("\n=== Interface Tests Passed! ===")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_system_interface()
        print("\n? All Mandala System Tests Completed Successfully! ?")
    except Exception as e:
        print(f"\n? Test Failed: {e}")
        import traceback
        traceback.print_exc()