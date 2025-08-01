#!/usr/bin/env python3
"""
Quick test for task management service
"""

import sys
import os
import asyncio
from datetime import datetime

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

def test_imports():
    """Test basic imports"""
    try:
        from interfaces.core_types import (
            Task, TaskType, TaskStatus, MandalaGrid, MandalaCell, 
            CellStatus, ChapterType
        )
        print("? Core types imported successfully")
        return True
    except ImportError as e:
        print(f"? Import error: {e}")
        return False

def test_main_imports():
    """Test main module imports"""
    try:
        from main import create_mandala_grid, MockFirestore
        print("? Main module imported successfully")
        return True
    except ImportError as e:
        print(f"? Main import error: {e}")
        return False

async def test_mandala_creation():
    """Test Mandala grid creation"""
    try:
        from main import create_mandala_grid
        from interfaces.core_types import ChapterType
        
        grid = await create_mandala_grid("test_user", ChapterType.SELF_DISCIPLINE)
        
        # Basic validation
        assert grid.chapter_type == ChapterType.SELF_DISCIPLINE
        assert len(grid.cells) == 9
        assert len(grid.cells[0]) == 9
        assert grid.center_value == "自動"
        
        print("? Mandala grid creation working")
        return True
    except Exception as e:
        print(f"? Mandala creation error: {e}")
        return False

async def test_task_creation():
    """Test task creation"""
    try:
        from main import create_task
        from interfaces.core_types import TaskType, TaskStatus
        
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        task_data = {
            "task_type": "routine",
            "title": "Test Task",
            "description": "Test description",
            "difficulty": 2
        }
        
        task = await create_task(task_data, mock_user)
        
        # Basic validation
        assert task.uid == "test_user_123"
        assert task.task_type == TaskType.ROUTINE
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        
        print("? Task creation working")
        return True
    except Exception as e:
        print(f"? Task creation error: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== Task Management Service Quick Test ===")
    
    tests = [
        ("Import Test", test_imports),
        ("Main Import Test", test_main_imports),
        ("Mandala Creation Test", test_mandala_creation),
        ("Task Creation Test", test_task_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"? {test_name} failed with exception: {e}")
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("? All tests passed! Task Management Service is working correctly.")
        return True
    else:
        print("? Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())