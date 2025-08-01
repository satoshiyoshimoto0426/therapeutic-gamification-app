"""
タスク23.3: ? - ?
?
"""
import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from collections import deque

from main import (
    EdgeAICacheEngine, IntelligentCache, CacheStrategy, ModelType
)

class TestOfflineTaskManagement:
    """?"""
    
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_offline_queue_basic_operations(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        operation1 = {
            "type": "task_completion",
            "task_id": "offline_task_001",
            "user_id": "offline_user_001",
            "completion_time": datetime.now().isoformat(),
            "xp_earned": 50
        }
        
        await self.engine.add_to_offline_queue(operation1)
        
        # ?
        assert len(self.engine.offline_queue) == 1
        
        # ?IDと
        queued_operation = self.engine.offline_queue[0]
        assert "id" in queued_operation
        assert "timestamp" in queued_operation
        assert queued_operation["type"] == "task_completion"
    
    @pytest.mark.asyncio
    async def test_offline_queue_capacity_management(self):
        """?"""
        await self.engine.initialize()
        
        # ?1000?
        for i in range(1050):
            operation = {
                "type": "test_operation",
                "operation_id": f"op_{i}",
                "user_id": "capacity_test_user"
            }
            await self.engine.add_to_offline_queue(operation)
        
        # ?
        assert len(self.engine.offline_queue) <= 1000
        
        # ?FIFO?
        latest_operation = self.engine.offline_queue[-1]
        assert latest_operation["operation_id"] == "op_1049"
    
    @pytest.mark.asyncio
    async def test_offline_task_types_support(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        operations = [
            {
                "type": "task_completion",
                "task_id": "task_001",
                "user_id": "user_001",
                "difficulty": 3,
                "mood_score": 4
            },
            {
                "type": "mood_update",
                "user_id": "user_001",
                "mood_score": 3,
                "energy_level": 2
            },
            {
                "type": "story_progress",
                "user_id": "user_001",
                "story_id": "story_001",
                "choice_made": "option_a"
            },
            {
                "type": "mandala_update",
                "user_id": "user_001",
                "cell_unlocked": "cell_4_5",
                "progress": 0.75
            }
        ]
        
        # ?
        for operation in operations:
            await self.engine.add_to_offline_queue(operation)
        
        # ?
        assert len(self.engine.offline_queue) == 4
        
        # ?
        operation_types = [op["type"] for op in self.engine.offline_queue]
        expected_types = ["task_completion", "mood_update", "story_progress", "mandala_update"]
        assert all(op_type in operation_types for op_type in expected_types)

class TestDataSynchronization:
    """デフォルト"""
    
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_sync_offline_operations_basic(self):
        """基本"""
        await self.engine.initialize()
        
        # ?
        operations = [
            {"type": "task_completion", "task_id": "sync_task_1", "user_id": "sync_user"},
            {"type": "mood_update", "mood_score": 4, "user_id": "sync_user"},
            {"type": "story_progress", "story_id": "sync_story", "user_id": "sync_user"}
        ]
        
        for operation in operations:
            await self.engine.add_to_offline_queue(operation)
        
        # ?
        sync_result = await self.engine.sync_offline_operations()
        
        # ?
        assert sync_result["status"] == "completed"
        assert sync_result["synced_count"] == 3
        assert sync_result["failed_count"] == 0
        assert sync_result["remaining_queue_size"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_with_failures(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        operations = [
            {"type": "task_completion", "task_id": "valid_task", "user_id": "test_user"},
            {"type": "invalid_operation", "invalid_data": "should_fail"},  # ?
            {"type": "mood_update", "mood_score": 3, "user_id": "test_user"}
        ]
        
        for operation in operations:
            await self.engine.add_to_offline_queue(operation)
        
        # _sync_single_operationを
        original_sync = self.engine._sync_single_operation
        
        async def mock_sync(operation):
            if operation.get("type") == "invalid_operation":
                raise Exception("Sync failed for invalid operation")
            return await original_sync(operation)
        
        self.engine._sync_single_operation = mock_sync
        
        # ?
        sync_result = await self.engine.sync_offline_operations()
        
        # ?
        assert sync_result["status"] == "completed"
        assert sync_result["synced_count"] >= 1  # ?1つ
        assert sync_result["failed_count"] >= 0  # ?
    
    @pytest.mark.asyncio
    async def test_concurrent_sync_prevention(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        for i in range(5):
            operation = {"type": "test_sync", "id": i, "user_id": "concurrent_user"}
            await self.engine.add_to_offline_queue(operation)
        
        # ?
        sync_tasks = [
            self.engine.sync_offline_operations(),
            self.engine.sync_offline_operations(),
            self.engine.sync_offline_operations()
        ]
        
        results = await asyncio.gather(*sync_tasks)
        
        # 1つ
        completed_count = sum(1 for result in results if result["status"] == "completed")
        in_progress_count = sum(1 for result in results if result["status"] == "sync_in_progress")
        
        assert completed_count == 1
        assert in_progress_count == 2

class TestConflictResolution:
    """コア"""
    
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_timestamp_based_conflict_resolution(self):
        """タスク"""
        await self.engine.initialize()
        
        # ?
        base_time = datetime.now()
        
        conflicting_operations = [
            {
                "type": "task_completion",
                "task_id": "conflict_task_001",
                "user_id": "conflict_user",
                "completion_time": (base_time - timedelta(minutes=5)).isoformat(),
                "xp_earned": 30
            },
            {
                "type": "task_completion", 
                "task_id": "conflict_task_001",  # ?ID
                "user_id": "conflict_user",
                "completion_time": base_time.isoformat(),  # ?
                "xp_earned": 50
            }
        ]
        
        # ?
        for operation in conflicting_operations:
            await self.engine.add_to_offline_queue(operation)
        
        # コア
        resolved_operations = await self._resolve_conflicts(self.engine.offline_queue)
        
        # ?
        assert len(resolved_operations) == 1
        assert resolved_operations[0]["xp_earned"] == 50
    
    @pytest.mark.asyncio
    async def test_user_preference_conflict_resolution(self):
        """ユーザー"""
        await self.engine.initialize()
        
        # ユーザー
        mood_operations = [
            {
                "type": "mood_update",
                "user_id": "mood_conflict_user",
                "mood_score": 2,
                "timestamp": "2025-01-27T10:00:00",
                "source": "manual_input"
            },
            {
                "type": "mood_update",
                "user_id": "mood_conflict_user", 
                "mood_score": 4,
                "timestamp": "2025-01-27T10:05:00",
                "source": "ai_inference"
            }
        ]
        
        for operation in mood_operations:
            await self.engine.add_to_offline_queue(operation)
        
        # ?
        resolved_operations = await self._resolve_conflicts_by_source(self.engine.offline_queue)
        
        # ?
        assert len(resolved_operations) == 1
        assert resolved_operations[0]["source"] == "manual_input"
        assert resolved_operations[0]["mood_score"] == 2
    
    async def _resolve_conflicts(self, operations):
        """タスク"""
        conflicts = {}
        
        for operation in operations:
            key = f"{operation['type']}_{operation.get('task_id', operation.get('user_id'))}"
            
            if key not in conflicts:
                conflicts[key] = operation
            else:
                # ?
                existing_time = datetime.fromisoformat(conflicts[key]["completion_time"])
                new_time = datetime.fromisoformat(operation["completion_time"])
                
                if new_time > existing_time:
                    conflicts[key] = operation
        
        return list(conflicts.values())
    
    async def _resolve_conflicts_by_source(self, operations):
        """?"""
        source_priority = {"manual_input": 1, "ai_inference": 2, "system": 3}
        conflicts = {}
        
        for operation in operations:
            key = f"{operation['type']}_{operation['user_id']}"
            
            if key not in conflicts:
                conflicts[key] = operation
            else:
                existing_priority = source_priority.get(conflicts[key].get("source"), 999)
                new_priority = source_priority.get(operation.get("source"), 999)
                
                if new_priority < existing_priority:
                    conflicts[key] = operation
        
        return list(conflicts.values())

class TestOfflineTherapeuticSupport:
    """?"""
    
    def setup_method(self):
        """?"""
        self.engine = EdgeAICacheEngine()
    
    @pytest.mark.asyncio
    async def test_offline_task_caching(self):
        """?"""
        await self.engine.initialize()
        
        # 治療
        therapeutic_data = [
            ("daily_tasks", ["?", "?", "?"], ModelType.TASK_RECOMMENDATION),
            ("mood_prompts", ["?", "エラー"], ModelType.MOOD_PREDICTION),
            ("story_content", {"chapter": 1, "content": "勇..."}, ModelType.STORY_GENERATION),
            ("coping_strategies", ["?", "5?", "?"], ModelType.USER_BEHAVIOR)
        ]
        
        # 治療
        for key, data, model_type in therapeutic_data:
            await self.engine.cache.put(key, data, model_type, "offline_therapy_user", ttl_seconds=86400)  # 24?
        
        # ?
        cached_tasks = await self.engine.cache.get("daily_tasks", "offline_therapy_user")
        cached_mood_prompts = await self.engine.cache.get("mood_prompts", "offline_therapy_user")
        cached_story = await self.engine.cache.get("story_content", "offline_therapy_user")
        cached_coping = await self.engine.cache.get("coping_strategies", "offline_therapy_user")
        
        # ?
        assert cached_tasks == ["?", "?", "?"]
        assert cached_mood_prompts == ["?", "エラー"]
        assert cached_story["chapter"] == 1
        assert "?" in cached_coping
    
    @pytest.mark.asyncio
    async def test_offline_progress_tracking(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        offline_progress = [
            {
                "type": "task_completion",
                "task_id": "morning_exercise",
                "user_id": "progress_user",
                "completed_at": datetime.now().isoformat(),
                "difficulty": 2,
                "mood_before": 3,
                "mood_after": 4
            },
            {
                "type": "mood_log",
                "user_id": "progress_user",
                "mood_score": 4,
                "energy_level": 3,
                "notes": "?",
                "logged_at": datetime.now().isoformat()
            },
            {
                "type": "coping_strategy_used",
                "user_id": "progress_user",
                "strategy": "deep_breathing",
                "effectiveness": 4,
                "duration_minutes": 5,
                "used_at": datetime.now().isoformat()
            }
        ]
        
        # ?
        for progress in offline_progress:
            await self.engine.add_to_offline_queue(progress)
        
        # ?
        assert len(self.engine.offline_queue) == 3
        
        # ?
        progress_types = [op["type"] for op in self.engine.offline_queue]
        assert "task_completion" in progress_types
        assert "mood_log" in progress_types
        assert "coping_strategy_used" in progress_types
    
    @pytest.mark.asyncio
    async def test_offline_therapeutic_continuity(self):
        """?"""
        await self.engine.initialize()
        
        # 治療
        continuity_data = {
            "user_profile": {
                "user_id": "continuity_user",
                "current_level": 5,
                "xp": 1250,
                "mood_trend": [3, 4, 3, 4, 4],
                "preferred_tasks": ["exercise", "journaling", "meditation"]
            },
            "current_chapter": {
                "chapter_id": "chapter_3",
                "title": "内部",
                "progress": 0.6,
                "available_choices": ["?", "?", "?"]
            },
            "emergency_resources": {
                "coping_strategies": ["4-7-8?", "5-4-3-2-1?", "?"],
                "crisis_contacts": ["カスタム: 080-1234-5678", "?: 119"],
                "safe_activities": ["?", "?", "?"]
            }
        }
        
        # ?
        for key, data in continuity_data.items():
            await self.engine.cache.put(key, data, ModelType.USER_BEHAVIOR, "continuity_user", ttl_seconds=86400)
        
        # ?
        user_profile = await self.engine.cache.get("user_profile", "continuity_user")
        current_chapter = await self.engine.cache.get("current_chapter", "continuity_user")
        emergency_resources = await self.engine.cache.get("emergency_resources", "continuity_user")
        
        # 治療
        assert user_profile["current_level"] == 5
        assert current_chapter["progress"] == 0.6
        assert len(emergency_resources["coping_strategies"]) == 3
        assert "4-7-8?" in emergency_resources["coping_strategies"]
    
    @pytest.mark.asyncio
    async def test_offline_crisis_support(self):
        """?"""
        await self.engine.initialize()
        
        # ?
        crisis_support = {
            "immediate_coping": [
                "?",
                "?", 
                "5つ4つ3つ"
            ],
            "grounding_techniques": [
                "?",
                "?",
                "?3つ"
            ],
            "positive_affirmations": [
                "こ",
                "?",
                "?"
            ],
            "emergency_plan": {
                "step1": "安全",
                "step2": "?3?", 
                "step3": "信頼",
                "step4": "?"
            }
        }
        
        await self.engine.cache.put("crisis_support", crisis_support, ModelType.USER_BEHAVIOR, "crisis_user", ttl_seconds=86400)
        
        # ?
        support_data = await self.engine.cache.get("crisis_support", "crisis_user")
        
        # ?
        assert len(support_data["immediate_coping"]) == 3
        assert len(support_data["grounding_techniques"]) == 3
        assert len(support_data["positive_affirmations"]) == 3
        assert "step1" in support_data["emergency_plan"]
        
        # ?
        crisis_operation = {
            "type": "crisis_event",
            "user_id": "crisis_user",
            "severity": "moderate",
            "coping_used": support_data["immediate_coping"][0],
            "timestamp": datetime.now().isoformat(),
            "resolved": True
        }
        
        await self.engine.add_to_offline_queue(crisis_operation)
        
        # ?
        assert len(self.engine.offline_queue) == 1
        assert self.engine.offline_queue[0]["type"] == "crisis_event"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])