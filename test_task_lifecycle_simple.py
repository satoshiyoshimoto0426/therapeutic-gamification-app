#!/usr/bin/env python3
"""
タスクライフサイクル簡単テスト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_task_lifecycle():
    """タスクライフサイクルテスト"""
    try:
        from shared.interfaces.task_system import Task, TaskType, TaskStatus
        from shared.interfaces.core_types import CrystalAttribute
        
        # タスク作成テスト
        task = Task(
            task_id="test_001",
            uid="test_user",
            title="テストタスク",
            task_type=TaskType.ROUTINE,
            difficulty=2,
            primary_crystal_attribute=CrystalAttribute.SELF_DISCIPLINE,
            status=TaskStatus.PENDING
        )
        
        print(f"[OK] タスク作成成功: {task.task_id}")
        
        # タスク状態変更テスト
        task.status = TaskStatus.IN_PROGRESS
        print(f"[OK] タスク状態変更成功: {task.status}")
        
        task.status = TaskStatus.COMPLETED
        print(f"[OK] タスク完了成功: {task.status}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] タスクライフサイクルテスト失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_task_lifecycle()
    sys.exit(0 if success else 1)
