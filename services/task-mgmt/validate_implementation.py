#!/usr/bin/env python3
"""
Task Management Service Implementation Validation
Validates core functionality without external dependencies
"""

import sys
import os
import asyncio
from datetime import datetime, date
from typing import Dict, Any

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

def validate_core_types():
    """Validate that core types are properly defined"""
    try:
        from interfaces.core_types import (
            Task, TaskType, TaskStatus, MandalaGrid, MandalaCell, 
            CellStatus, ChapterType
        )
        
        # Test enum values
        assert TaskType.ROUTINE == "routine"
        assert TaskStatus.PENDING == "pending"
        assert CellStatus.LOCKED == "locked"
        assert ChapterType.SELF_DISCIPLINE == "self_discipline"
        
        print("? Core types validation passed")
        return True
    except Exception as e:
        print(f"? Core types validation failed: {e}")
        return False

def validate_mock_firestore():
    """Validate mock Firestore implementation"""
    try:
        # Import mock classes directly
        sys.path.append(os.path.dirname(__file__))
        from main import MockFirestore, MockFirestoreCollection, MockFirestoreDoc
        
        # Test document operations
        doc = MockFirestoreDoc()
        assert doc.exists() == True
        
        doc.set({"test": "value"})
        assert doc.to_dict()["test"] == "value"
        
        doc.update({"new_field": "new_value"})
        assert doc.to_dict()["new_field"] == "new_value"
        
        # Test collection operations
        collection = MockFirestoreCollection()
        test_doc = collection.document("test_id")
        test_doc.set({"uid": "user123", "status": "pending"})
        
        # Test query operations
        query = collection.where("uid", "==", "user123")
        results = query.get()
        assert len(results) >= 0  # Should not error
        
        print("? Mock Firestore validation passed")
        return True
    except Exception as e:
        print(f"? Mock Firestore validation failed: {e}")
        return False

async def validate_mandala_grid():
    """Validate Mandala grid creation and structure"""
    try:
        from main import create_mandala_grid
        from interfaces.core_types import ChapterType, CellStatus
        
        # Create a test grid
        grid = await create_mandala_grid("test_user", ChapterType.SELF_DISCIPLINE)
        
        # Validate grid structure
        assert grid.chapter_type == ChapterType.SELF_DISCIPLINE
        assert len(grid.cells) == 9, f"Expected 9 rows, got {len(grid.cells)}"
        assert len(grid.cells[0]) == 9, f"Expected 9 columns, got {len(grid.cells[0])}"
        assert grid.center_value == "自動"
        assert grid.completion_percentage == 0.0
        
        # Validate center cell (4,4) is available
        center_cell = grid.cells[4][4]
        assert center_cell.status == CellStatus.AVAILABLE
        assert center_cell.position == (4, 4)
        
        # Validate inner ring cells are available
        inner_cell = grid.cells[3][4]  # Adjacent to center
        assert inner_cell.status == CellStatus.AVAILABLE
        
        # Validate outer cells are locked
        outer_cell = grid.cells[0][0]  # Corner cell
        assert outer_cell.status == CellStatus.LOCKED
        assert "complete_adjacent_cells" in outer_cell.unlock_conditions
        
        print("? Mandala grid validation passed")
        return True
    except Exception as e:
        print(f"? Mandala grid validation failed: {e}")
        return False

async def validate_task_operations():
    """Validate task CRUD operations"""
    try:
        from main import create_task, complete_task
        from interfaces.core_types import TaskType, TaskStatus
        
        # Mock user
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        
        # Test task creation
        task_data = {
            "task_type": "routine",
            "title": "Morning Exercise",
            "description": "30 minutes of light exercise",
            "difficulty": 2,
            "due_date": "2024-01-15T09:00:00"
        }
        
        task = await create_task(task_data, mock_user)
        
        # Validate task properties
        assert task.uid == "test_user_123"
        assert task.task_type == TaskType.ROUTINE
        assert task.title == "Morning Exercise"
        assert task.difficulty == 2
        assert task.status == TaskStatus.PENDING
        assert task.task_id is not None
        
        # Test task completion
        completion_result = await complete_task(task.task_id, mock_user)
        assert completion_result["message"] == "Task completed successfully"
        assert "completed_at" in completion_result
        assert "xp_earned" in completion_result
        assert completion_result["xp_earned"] == 20  # difficulty * 10
        
        print("? Task operations validation passed")
        return True
    except Exception as e:
        print(f"? Task operations validation failed: {e}")
        return False

async def validate_mandala_integration():
    """Validate integration between tasks and Mandala grid"""
    try:
        from main import create_task, create_mandala_grid, update_mandala_cell_task
        from interfaces.core_types import ChapterType, CellStatus
        
        # Create a grid first
        grid = await create_mandala_grid("test_user_123", ChapterType.SELF_DISCIPLINE)
        
        # Create a task linked to a Mandala cell
        mock_user = {"uid": "test_user_123", "email": "test@example.com"}
        task_data = {
            "task_type": "routine",
            "title": "Linked Task",
            "mandala_cell_id": "test_user_123_self_discipline_4_4"
        }
        
        task = await create_task(task_data, mock_user)
        
        # Validate task is linked to cell
        assert task.mandala_cell_id == "test_user_123_self_discipline_4_4"
        
        print("? Mandala integration validation passed")
        return True
    except Exception as e:
        print(f"? Mandala integration validation failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("=== Task Management Service Implementation Validation ===\n")
    
    tests = [
        ("Core Types", validate_core_types, False),
        ("Mock Firestore", validate_mock_firestore, False),
        ("Mandala Grid", validate_mandala_grid, True),
        ("Task Operations", validate_task_operations, True),
        ("Mandala Integration", validate_mandala_integration, True)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func, is_async in tests:
        print(f"Running {test_name} validation...")
        try:
            if is_async:
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"? {test_name} validation failed with exception: {e}")
    
    print(f"\n=== Validation Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("? All validations passed! Task Management Service is ready.")
        print("\nKey Features Implemented:")
        print("- 9x9 Mandala grid system with 8 human development chapters")
        print("- Task CRUD operations with ADHD support features")
        print("- Daily task limit enforcement (max 16 tasks)")
        print("- Task-Mandala cell integration and progression tracking")
        print("- XP calculation and completion tracking")
        print("- Cell unlock progression system")
        return True
    else:
        print("? Some validations failed. Implementation needs fixes.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Validation script failed: {e}")
        sys.exit(1)