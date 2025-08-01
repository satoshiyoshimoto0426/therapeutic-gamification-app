"""
Simple Mandala Test
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Import the module directly
with open('shared/interfaces/mandala_system.py') as f:
    exec(f.read(), globals())

def test_mandala_basic():
    """Basic Mandala functionality test"""
    print("=== Mandala System Test ===")
    
    # Test grid initialization
    grid = MandalaGrid("test_user")
    print(f"Grid UID: {grid.uid}")
    print(f"Grid size: {len(grid.grid)}x{len(grid.grid[0])}")
    print(f"Core values: {len(grid.core_values)}")
    
    # Test core values
    center_cell = grid.grid[4][4]
    print(f"Center cell: {center_cell.quest_title}")
    print(f"Center status: {center_cell.status}")
    
    # Test cell unlock
    quest_data = {
        "quest_title": "Morning Exercise",
        "quest_description": "30 minutes of light exercise every morning",
        "xp_reward": 50,
        "difficulty": 2
    }
    
    result = grid.unlock_cell(3, 3, quest_data)
    print(f"Unlock result: {result}")
    print(f"Unlocked count: {grid.unlocked_count}")
    
    # Test cell completion
    complete_result = grid.complete_cell(3, 3)
    print(f"Complete result: {complete_result}")
    
    completed_cell = grid.grid[3][3]
    print(f"Cell status after completion: {completed_cell.status}")
    
    # Test serialization
    serialized = grid.serialize_grid()
    print(f"Serialized keys: {list(serialized.keys())}")
    
    # Test system interface
    interface = MandalaSystemInterface()
    api_response = interface.get_grid_api_response("test_user")
    print(f"API response keys: {list(api_response.keys())}")
    
    print("=== All tests passed! ===")

if __name__ == "__main__":
    test_mandala_basic()