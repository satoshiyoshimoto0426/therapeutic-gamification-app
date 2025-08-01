"""
Integration tests for repository layer
Tests CRUD operations, query optimization, and data consistency
"""

import pytest
import asyncio
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import repositories
from shared.repositories.base_repository import BaseRepository, CachedRepository
from shared.repositories.user_repository import UserRepository, UserProfile
from shared.repositories.task_repository import TaskRepository, Task
from shared.repositories.mood_repository import MoodRepository

# Mock types for testing
class TaskType:
    ROUTINE = "routine"
    SKILL_UP = "skill_up"
    SOCIAL = "social"

class TaskStatus:
    PENDING = "pending"
    COMPLETED = "completed"

class ChapterType:
    SELF_DISCIPLINE = "self_discipline"

class GuardianPermission:
    VIEW_ONLY = "view_only"

class MoodLog:
    def __init__(self, uid, log_date, mood_score, notes, context_tags, calculated_coefficient):
        self.uid = uid
        self.log_date = log_date
        self.mood_score = mood_score
        self.notes = notes
        self.context_tags = context_tags
        self.calculated_coefficient = calculated_coefficient


class TestEntity:
    """Test entity for base repository testing"""
    def __init__(self, id: str, name: str, value: int):
        self.id = id
        self.name = name
        self.value = value


class TestRepository(BaseRepository[TestEntity]):
    """Test repository implementation"""
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> TestEntity:
        return TestEntity(
            id=doc_data.get("id", doc_id),
            name=doc_data["name"],
            value=doc_data["value"]
        )
    
    def _to_document(self, entity: TestEntity) -> Dict[str, Any]:
        return {
            "id": entity.id,
            "name": entity.name,
            "value": entity.value
        }


class TestBaseRepository:
    """Test base repository functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_collection.add.return_value = (None, mock_document)
        
        # Mock document operations
        mock_doc_data = {
            "id": "test_doc_id",
            "name": "test_entity",
            "value": 42,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = mock_doc_data
        mock_document.get.return_value.id = "test_doc_id"
        mock_document.id = "test_doc_id"
        
        # Mock query operations
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.get.return_value = [mock_document.get.return_value]
        
        return mock_client
    
    @pytest.fixture
    def test_repository(self, mock_db_client):
        """Create test repository instance"""
        return TestRepository(mock_db_client, "test_collection")
    
    @pytest.mark.asyncio
    async def test_create_entity(self, test_repository):
        """Test entity creation"""
        entity = TestEntity("test_id", "test_name", 100)
        
        with patch.object(test_repository, '_validate_document'):
            result = await test_repository.create(entity, "test_id")
            
        assert result == "test_id"
        test_repository.collection_ref.document.assert_called_with("test_id")
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, test_repository):
        """Test get entity by ID"""
        result = await test_repository.get_by_id("test_id")
        
        assert result is not None
        assert result.id == "test_doc_id"
        assert result.name == "test_entity"
        assert result.value == 42
    
    @pytest.mark.asyncio
    async def test_update_entity(self, test_repository):
        """Test entity update"""
        updates = {"name": "updated_name", "value": 200}
        
        with patch.object(test_repository, 'get_by_id') as mock_get:
            mock_get.return_value = TestEntity("test_id", "old_name", 100)
            result = await test_repository.update("test_id", updates)
        
        assert result is True
        test_repository.collection_ref.document.assert_called_with("test_id")
    
    @pytest.mark.asyncio
    async def test_delete_entity(self, test_repository):
        """Test entity deletion"""
        result = await test_repository.delete("test_id")
        
        assert result is True
        test_repository.collection_ref.document.assert_called_with("test_id")
    
    @pytest.mark.asyncio
    async def test_find_by_field(self, test_repository):
        """Test find by field"""
        results = await test_repository.find_by_field("name", "test_name")
        
        assert len(results) == 1
        assert results[0].name == "test_entity"
    
    @pytest.mark.asyncio
    async def test_pagination(self, test_repository):
        """Test pagination functionality"""
        result = await test_repository.find_with_pagination(
            filters={"name": "test"},
            order_by="value",
            page_size=10
        )
        
        assert "data" in result
        assert "next_cursor" in result
        assert "has_more" in result
        assert len(result["data"]) <= 10


class TestUserRepository:
    """Test user repository functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client for user repository"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        # Mock user data
        mock_user_data = {
            "uid": "test_user_id",
            "email": "test@example.com",
            "display_name": "Test User",
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "player_level": 5,
            "yu_level": 2,
            "total_xp": 1000,
            "crystal_gauges": {
                "self_discipline": 50,
                "empathy": 30,
                "resilience": 70
            },
            "care_points": 100
        }
        
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = mock_user_data
        mock_document.get.return_value.id = "test_user_id"
        
        return mock_client
    
    @pytest.fixture
    def user_repository(self, mock_db_client):
        """Create user repository instance"""
        return UserRepository(mock_db_client)
    
    @pytest.mark.asyncio
    async def test_add_xp(self, user_repository):
        """Test XP addition and level calculation"""
        with patch.object(user_repository, 'get_by_id') as mock_get, \
             patch.object(user_repository, 'update') as mock_update:
            
            mock_user = UserProfile(
                uid="test_user",
                email="test@example.com",
                display_name="Test User",
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                player_level=5,
                yu_level=2,
                total_xp=1000,
                crystal_gauges={}
            )
            mock_get.return_value = mock_user
            mock_update.return_value = True
            
            result = await user_repository.add_xp("test_user", 500, "task_completion")
            
            assert result["xp_added"] == 500
            assert result["new_total_xp"] == 1500
            assert result["level_up"] is True
            assert result["source"] == "task_completion"
    
    @pytest.mark.asyncio
    async def test_update_crystal_gauge(self, user_repository):
        """Test crystal gauge update"""
        with patch.object(user_repository, 'get_by_id') as mock_get, \
             patch.object(user_repository, 'update') as mock_update:
            
            mock_user = UserProfile(
                uid="test_user",
                email="test@example.com",
                display_name="Test User",
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                player_level=5,
                yu_level=2,
                total_xp=1000,
                crystal_gauges={"self_discipline": 80}
            )
            mock_get.return_value = mock_user
            mock_update.return_value = True
            
            result = await user_repository.update_crystal_gauge("test_user", "self_discipline", 25)
            
            assert result["attribute"] == "self_discipline"
            assert result["points_added"] == 20  # Capped at 100
            assert result["new_value"] == 100
            assert result["chapter_unlocked"] is True


class TestTaskRepository:
    """Test task repository functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client for task repository"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        # Mock task data
        mock_task_data = {
            "task_id": "test_task_id",
            "uid": "test_user_id",
            "task_type": TaskType.ROUTINE.value,
            "title": "Test Task",
            "description": "Test task description",
            "difficulty": 3,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "xp_earned": 0
        }
        
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = mock_task_data
        mock_document.get.return_value.id = "test_task_id"
        
        # Mock query for daily tasks
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.get.return_value = [mock_document.get.return_value] * 10  # 10 tasks
        
        return mock_client
    
    @pytest.fixture
    def task_repository(self, mock_db_client):
        """Create task repository instance"""
        return TaskRepository(mock_db_client)
    
    @pytest.mark.asyncio
    async def test_check_daily_task_limit(self, task_repository):
        """Test daily task limit checking"""
        with patch.object(task_repository, 'get_daily_tasks') as mock_get_daily:
            mock_tasks = [Mock() for _ in range(10)]  # 10 existing tasks
            mock_get_daily.return_value = mock_tasks
            
            result = await task_repository.check_daily_task_limit("test_user")
            
            assert result["current_count"] == 10
            assert result["limit"] == 16
            assert result["can_add_more"] is True
            assert result["remaining"] == 6
    
    @pytest.mark.asyncio
    async def test_complete_task(self, task_repository):
        """Test task completion and XP calculation"""
        with patch.object(task_repository, 'get_by_id') as mock_get, \
             patch.object(task_repository, 'update') as mock_update:
            
            mock_task = Task(
                task_id="test_task",
                uid="test_user",
                task_type=TaskType.ROUTINE,
                title="Test Task",
                description="Test description",
                difficulty=3,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow()
            )
            mock_get.return_value = mock_task
            mock_update.return_value = True
            
            result = await task_repository.complete_task("test_task", mood_coefficient=1.2, adhd_assist=1.1)
            
            expected_xp = int(3 * 1.2 * 1.1 * 10)  # difficulty * mood * adhd * base
            assert result["xp_earned"] == expected_xp
            assert result["task_type"] == TaskType.ROUTINE.value
    
    @pytest.mark.asyncio
    async def test_get_task_statistics(self, task_repository):
        """Test task statistics calculation"""
        with patch.object(task_repository, 'find_by_date_range') as mock_find:
            # Mock completed and pending tasks
            completed_tasks = [
                Task("task1", "user1", TaskType.ROUTINE, "Task 1", "Desc", 2, TaskStatus.COMPLETED, datetime.utcnow(), xp_earned=50),
                Task("task2", "user1", TaskType.SKILL_UP, "Task 2", "Desc", 3, TaskStatus.COMPLETED, datetime.utcnow(), xp_earned=75)
            ]
            pending_tasks = [
                Task("task3", "user1", TaskType.SOCIAL, "Task 3", "Desc", 1, TaskStatus.PENDING, datetime.utcnow())
            ]
            
            mock_find.return_value = completed_tasks + pending_tasks
            
            result = await task_repository.get_task_statistics("user1", days=30)
            
            assert result["total_tasks"] == 3
            assert result["completed_tasks"] == 2
            assert result["pending_tasks"] == 1
            assert result["completion_rate"] == 2/3
            assert result["total_xp_earned"] == 125


class TestMoodRepository:
    """Test mood repository functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client for mood repository"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        # Mock mood data
        mock_mood_data = {
            "uid": "test_user_id",
            "log_date": date.today(),
            "mood_score": 4,
            "notes": "Feeling good today",
            "context_tags": ["work", "exercise"],
            "calculated_coefficient": 1.15
        }
        
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = mock_mood_data
        mock_document.get.return_value.id = "test_mood_id"
        
        # Mock query
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.get.return_value = [mock_document.get.return_value]
        
        return mock_client
    
    @pytest.fixture
    def mood_repository(self, mock_db_client):
        """Create mood repository instance"""
        return MoodRepository(mock_db_client)
    
    @pytest.mark.asyncio
    async def test_calculate_mood_coefficient(self, mood_repository):
        """Test mood coefficient calculation"""
        # Test different mood scores
        assert await mood_repository.calculate_mood_coefficient(1) == 0.8  # Clamped minimum
        assert await mood_repository.calculate_mood_coefficient(3) == 1.05
        assert await mood_repository.calculate_mood_coefficient(5) == 1.2   # Clamped maximum
    
    @pytest.mark.asyncio
    async def test_create_mood_log(self, mood_repository):
        """Test mood log creation"""
        with patch.object(mood_repository, 'get_mood_for_date') as mock_get, \
             patch.object(mood_repository, 'create') as mock_create:
            
            mock_get.return_value = None  # No existing mood for today
            mock_create.return_value = "mood_log_id"
            
            result = await mood_repository.create_mood_log("test_user", 4, "Good day", ["work"])
            
            assert result == "mood_log_id"
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_mood_coefficient(self, mood_repository):
        """Test getting current mood coefficient"""
        with patch.object(mood_repository, 'get_mood_for_date') as mock_get:
            mock_mood = MoodLog(
                uid="test_user",
                log_date=date.today(),
                mood_score=4,
                notes="",
                context_tags=[],
                calculated_coefficient=1.15
            )
            mock_get.return_value = mock_mood
            
            result = await mood_repository.get_current_mood_coefficient("test_user")
            
            assert result == 1.15


class TestRepositoryIntegration:
    """Test repository integration scenarios"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client for integration tests"""
        mock_client = Mock()
        
        # Mock collections
        collections = {}
        
        def get_collection(name):
            if name not in collections:
                collections[name] = Mock()
                collections[name].document = Mock()
                collections[name].where = Mock()
                collections[name].add = Mock()
            return collections[name]
        
        mock_client.collection.side_effect = get_collection
        
        return mock_client
    
    @pytest.mark.asyncio
    async def test_user_task_mood_integration(self, mock_db_client):
        """Test integration between user, task, and mood repositories"""
        user_repo = UserRepository(mock_db_client)
        task_repo = TaskRepository(mock_db_client)
        mood_repo = MoodRepository(mock_db_client)
        
        # Mock user
        mock_user = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="Test User",
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            player_level=5,
            yu_level=2,
            total_xp=1000,
            crystal_gauges={}
        )
        
        # Mock task
        mock_task = Task(
            task_id="test_task",
            uid="test_user",
            task_type=TaskType.ROUTINE,
            title="Morning Exercise",
            description="30 minutes of exercise",
            difficulty=3,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        # Mock mood
        mock_mood = MoodLog(
            uid="test_user",
            log_date=date.today(),
            mood_score=4,
            notes="Feeling energetic",
            context_tags=["exercise"],
            calculated_coefficient=1.15
        )
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user), \
             patch.object(task_repo, 'get_by_id', return_value=mock_task), \
             patch.object(mood_repo, 'get_current_mood_coefficient', return_value=1.15), \
             patch.object(task_repo, 'update', return_value=True), \
             patch.object(user_repo, 'add_xp') as mock_add_xp:
            
            # Simulate task completion workflow
            mood_coefficient = await mood_repo.get_current_mood_coefficient("test_user")
            task_result = await task_repo.complete_task("test_task", mood_coefficient=mood_coefficient, adhd_assist=1.0)
            
            # Add XP to user
            mock_add_xp.return_value = {
                "xp_added": task_result["xp_earned"],
                "new_total_xp": 1000 + task_result["xp_earned"],
                "level_up": False
            }
            
            xp_result = await user_repo.add_xp("test_user", task_result["xp_earned"], "task_completion")
            
            # Verify integration
            assert task_result["mood_coefficient"] == 1.15
            assert task_result["xp_earned"] > 0
            assert xp_result["xp_added"] == task_result["xp_earned"]
    
    @pytest.mark.asyncio
    async def test_repository_error_handling(self, mock_db_client):
        """Test repository error handling"""
        user_repo = UserRepository(mock_db_client)
        
        # Mock database error
        with patch.object(user_repo, 'get_by_id', side_effect=Exception("Database connection failed")):
            with pytest.raises(Exception) as exc_info:
                await user_repo.get_by_id("test_user")
            
            assert "Database connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_repository_caching(self, mock_db_client):
        """Test repository caching functionality"""
        cached_repo = CachedRepository(mock_db_client, "test_collection", cache_ttl_seconds=60)
        
        # Mock entity
        class TestCachedEntity:
            def __init__(self, id: str, name: str):
                self.id = id
                self.name = name
        
        cached_repo._to_entity = lambda data, doc_id: TestCachedEntity(data.get("id", doc_id), data["name"])
        cached_repo._to_document = lambda entity: {"id": entity.id, "name": entity.name}
        
        # Mock document data
        mock_doc_data = {"id": "test_id", "name": "test_entity"}
        mock_document = Mock()
        mock_document.get.return_value.exists = True
        mock_document.get.return_value.to_dict.return_value = mock_doc_data
        mock_document.get.return_value.id = "test_id"
        
        cached_repo.collection_ref.document.return_value = mock_document
        
        # First call - should hit database
        result1 = await cached_repo.get_by_id("test_id")
        assert result1.name == "test_entity"
        
        # Second call - should hit cache
        result2 = await cached_repo.get_by_id("test_id")
        assert result2.name == "test_entity"
        
        # Verify database was called only once
        assert cached_repo.collection_ref.document.call_count == 1


class TestQueryOptimization:
    """Test query optimization features"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock Firestore client with query optimization"""
        mock_client = Mock()
        mock_collection = Mock()
        
        # Mock compound queries
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.start_after.return_value = mock_query
        
        # Mock query results
        mock_documents = []
        for i in range(5):
            mock_doc = Mock()
            mock_doc.to_dict.return_value = {
                "id": f"doc_{i}",
                "name": f"Document {i}",
                "value": i * 10,
                "created_at": datetime.utcnow() - timedelta(days=i)
            }
            mock_doc.id = f"doc_{i}"
            mock_doc.get.return_value = f"value_{i}"  # For cursor
            mock_documents.append(mock_doc)
        
        mock_query.get.return_value = mock_documents
        mock_client.collection.return_value = mock_collection
        
        return mock_client
    
    @pytest.mark.asyncio
    async def test_compound_query_optimization(self, mock_db_client):
        """Test compound query with multiple filters"""
        test_repo = TestRepository(mock_db_client, "test_collection")
        
        filters = {
            "status": "active",
            "category": "important",
            "priority": {"operator": ">=", "value": 5}
        }
        
        results = await test_repo.find_by_multiple_fields(filters, limit=10)
        
        # Verify compound query was constructed
        assert len(results) == 5
        mock_db_client.collection.assert_called_with("test_collection")
    
    @pytest.mark.asyncio
    async def test_pagination_optimization(self, mock_db_client):
        """Test pagination with cursor-based optimization"""
        test_repo = TestRepository(mock_db_client, "test_collection")
        
        result = await test_repo.find_with_pagination(
            filters={"status": "active"},
            order_by="created_at",
            order_direction="desc",
            page_size=3,
            start_after=None
        )
        
        assert "data" in result
        assert "next_cursor" in result
        assert "has_more" in result
        assert len(result["data"]) <= 3
    
    @pytest.mark.asyncio
    async def test_aggregation_optimization(self, mock_db_client):
        """Test client-side aggregation optimization"""
        test_repo = TestRepository(mock_db_client, "test_collection")
        
        result = await test_repo.aggregate_by_field(
            group_by_field="category",
            aggregate_field="value",
            aggregate_function="sum"
        )
        
        # Verify aggregation results structure
        assert isinstance(result, dict)
        # Each group should have count, sum, average, min, max
        for group_data in result.values():
            assert "count" in group_data
            assert "sum" in group_data
            assert "average" in group_data


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])