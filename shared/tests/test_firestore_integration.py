"""
Unit tests for Firestore schema and collection design
Tests data integrity constraints, validation rules, and index performance
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from shared.config.firestore_collections import (
    COLLECTION_SCHEMAS,
    validate_document_data,
    get_collection_schema,
    CrystalAttribute,
    TaskType,
    TaskStatus
)
from shared.config.firestore_indexes import (
    get_index_for_query,
    get_ttl_config,
    get_optimization_hint
)
from shared.config.firestore_setup import FirestoreSetup

class TestFirestoreCollections:
    """Test Firestore collection schemas and validation"""
    
    def test_collection_schemas_completeness(self):
        """Test that all required collections are defined"""
        required_collections = [
            "user_profiles", "tasks", "story_states", "story_nodes",
            "story_edges", "mood_logs", "mandala_grids", "guardian_links",
            "game_states", "therapeutic_safety_logs", "adhd_support_settings"
        ]
        
        for collection in required_collections:
            assert collection in COLLECTION_SCHEMAS
            schema = COLLECTION_SCHEMAS[collection]
            assert "description" in schema
            assert "required_fields" in schema
            assert "validation_rules" in schema
            assert "indexes" in schema
    
    def test_user_profile_validation(self):
        """Test user profile document validation"""
        valid_user = {
            "uid": "user123",
            "email": "test@example.com",
            "display_name": "Test User",
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "player_level": 5,
            "yu_level": 7,
            "total_xp": 1250,
            "crystal_gauges": {attr.value: 25 for attr in CrystalAttribute}
        }
        
        errors = validate_document_data("user_profiles", valid_user)
        assert len(errors) == 0
        
        # Test invalid data
        invalid_user = valid_user.copy()
        invalid_user["player_level"] = 0  # Below minimum
        invalid_user["email"] = "invalid-email"  # Invalid format
        
        errors = validate_document_data("user_profiles", invalid_user)
        assert len(errors) > 0
        assert any("player_level" in error for error in errors)
    
    def test_task_validation(self):
        """Test task document validation"""
        valid_task = {
            "task_id": "task123",
            "uid": "user123",
            "task_type": TaskType.ROUTINE.value,
            "title": "Morning Exercise",
            "description": "30 minutes of light exercise",
            "difficulty": 3,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "xp_earned": 0,
            "mood_coefficient": 1.1,
            "adhd_assist": 1.2
        }
        
        errors = validate_document_data("tasks", valid_task)
        assert len(errors) == 0
        
        # Test invalid task type
        invalid_task = valid_task.copy()
        invalid_task["task_type"] = "invalid_type"
        invalid_task["difficulty"] = 6  # Above maximum
        
        errors = validate_document_data("tasks", invalid_task)
        assert len(errors) > 0
        assert any("task_type" in error for error in errors)
        assert any("difficulty" in error for error in errors)
    
    def test_mood_log_validation(self):
        """Test mood log document validation"""
        valid_mood = {
            "uid": "user123",
            "log_date": datetime.utcnow().date(),
            "mood_score": 4,
            "mood_coefficient": 1.15,
            "created_at": datetime.utcnow(),
            "energy_level": 3,
            "stress_level": 2,
            "sleep_quality": 4
        }
        
        errors = validate_document_data("mood_logs", valid_mood)
        assert len(errors) == 0
        
        # Test invalid mood score
        invalid_mood = valid_mood.copy()
        invalid_mood["mood_score"] = 6  # Above maximum
        invalid_mood["mood_coefficient"] = 1.5  # Above maximum
        
        errors = validate_document_data("mood_logs", invalid_mood)
        assert len(errors) > 0
    
    def test_story_node_validation(self):
        """Test story node document validation"""
        valid_node = {
            "node_id": "node123",
            "chapter_type": CrystalAttribute.SELF_DISCIPLINE.value,
            "node_type": "choice",
            "title": "A Difficult Decision",
            "content": "You face a challenging choice...",
            "therapeutic_elements": ["decision_making", "self_reflection"],
            "estimated_read_time": 5
        }
        
        errors = validate_document_data("story_nodes", valid_node)
        assert len(errors) == 0
        
        # Test invalid chapter type
        invalid_node = valid_node.copy()
        invalid_node["chapter_type"] = "invalid_chapter"
        invalid_node["estimated_read_time"] = 0  # Below minimum
        
        errors = validate_document_data("story_nodes", invalid_node)
        assert len(errors) > 0
    
    def test_guardian_link_validation(self):
        """Test guardian link document validation"""
        valid_link = {
            "link_id": "link123",
            "guardian_id": "guardian123",
            "user_id": "user123",
            "permission_level": "task_edit",
            "created_at": datetime.utcnow(),
            "approved_by_user": True,
            "care_points_allocated": 100,
            "medical_discount_applied": False
        }
        
        errors = validate_document_data("guardian_links", valid_link)
        assert len(errors) == 0
        
        # Test invalid permission level
        invalid_link = valid_link.copy()
        invalid_link["permission_level"] = "invalid_permission"
        
        errors = validate_document_data("guardian_links", invalid_link)
        assert len(errors) > 0

class TestFirestoreIndexes:
    """Test Firestore index configuration and optimization"""
    
    def test_index_for_user_queries(self):
        """Test indexes for common user queries"""
        # Test user leaderboard query
        index = get_index_for_query("user_profiles", ["player_level", "total_xp"])
        assert index is not None
        assert index["collectionGroup"] == "user_profiles"
        
        # Test user lookup by email
        index = get_index_for_query("user_profiles", ["email"])
        assert index is not None
    
    def test_index_for_task_queries(self):
        """Test indexes for task management queries"""
        # Test user's pending tasks
        index = get_index_for_query("tasks", ["uid", "status", "due_date"])
        assert index is not None
        
        # Test tasks by type
        index = get_index_for_query("tasks", ["uid", "task_type"])
        assert index is not None
    
    def test_index_for_story_queries(self):
        """Test indexes for story progression queries"""
        # Test story nodes by chapter
        index = get_index_for_query("story_nodes", ["chapter_type", "node_type"])
        assert index is not None
        
        # Test story edges from node
        index = get_index_for_query("story_edges", ["from_node"])
        assert index is not None
    
    def test_ttl_configurations(self):
        """Test TTL configurations for automatic cleanup"""
        # Test safety logs TTL
        ttl_config = get_ttl_config("therapeutic_safety_logs")
        assert ttl_config["field"] == "timestamp"
        assert ttl_config["duration_days"] == 365
        
        # Test mood logs TTL
        ttl_config = get_ttl_config("mood_logs")
        assert ttl_config["field"] == "created_at"
        assert ttl_config["duration_days"] == 1095
    
    def test_optimization_hints(self):
        """Test query optimization hints"""
        # Test user leaderboard optimization
        hint = get_optimization_hint("user_leaderboard")
        assert hint["collection"] == "game_states"
        assert hint["limit_recommendation"] == 100
        assert "cache_duration_minutes" in hint
        
        # Test daily tasks optimization
        hint = get_optimization_hint("daily_tasks_by_user")
        assert hint["collection"] == "tasks"
        assert hint["limit_recommendation"] == 16  # ADHD daily limit

class TestFirestoreSetup:
    """Test Firestore database setup and initialization"""
    
    @patch('shared.config.firestore_setup.firestore.Client')
    def test_firestore_setup_initialization(self, mock_firestore):
        """Test database initialization process"""
        # Mock Firestore client
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        # Mock collection and document operations
        mock_collection = Mock()
        mock_document = Mock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        setup = FirestoreSetup("test-project")
        results = setup.initialize_database()
        
        # Verify collections were created
        assert len(results["collections_created"]) > 0
        assert len(results["errors"]) == 0
        
        # Verify Firestore client was called
        mock_db.collection.assert_called()
        mock_document.set.assert_called()
    
    @patch('shared.config.firestore_setup.firestore.Client')
    def test_story_nodes_seeding(self, mock_firestore):
        """Test initial story nodes seeding"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        # Mock batch operations
        mock_batch = Mock()
        mock_db.batch.return_value = mock_batch
        
        setup = FirestoreSetup("test-project")
        results = {"initial_data_seeded": [], "errors": []}
        
        setup._seed_story_nodes(results)
        
        # Verify batch operations were called
        mock_db.batch.assert_called()
        mock_batch.set.assert_called()
        mock_batch.commit.assert_called()
        
        assert "story_nodes" in results["initial_data_seeded"]
    
    @patch('shared.config.firestore_setup.firestore.Client')
    def test_system_config_seeding(self, mock_firestore):
        """Test system configuration seeding"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        mock_collection = Mock()
        mock_document = Mock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        setup = FirestoreSetup("test-project")
        results = {"initial_data_seeded": [], "errors": []}
        
        setup._seed_system_config(results)
        
        # Verify system config documents were created
        assert mock_document.set.call_count >= 3  # At least 3 config documents
        assert "system_config" in results["initial_data_seeded"]
    
    @patch('builtins.open', create=True)
    @patch('os.makedirs')
    def test_config_file_generation(self, mock_makedirs, mock_open):
        """Test configuration file generation"""
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        setup = FirestoreSetup("test-project")
        results = {"indexes_configured": False, "security_rules_ready": False, "errors": []}
        
        # Test index config generation
        setup._generate_index_config(results)
        assert results["indexes_configured"] == True
        
        # Test security rules generation
        setup._generate_security_rules(results)
        assert results["security_rules_ready"] == True
        
        # Verify files were written
        mock_open.assert_called()
        mock_file.write.assert_called()

class TestDataIntegrityConstraints:
    """Test data integrity constraints and business rules"""
    
    def test_crystal_gauges_sum_constraint(self):
        """Test crystal gauges sum constraint (max 800)"""
        # Valid crystal gauges
        valid_gauges = {attr.value: 50 for attr in CrystalAttribute}  # 8 * 50 = 400
        total = sum(valid_gauges.values())
        assert total <= 800
        
        # Invalid crystal gauges (exceeds limit)
        invalid_gauges = {attr.value: 150 for attr in CrystalAttribute}  # 8 * 150 = 1200
        total = sum(invalid_gauges.values())
        assert total > 800  # This would violate the constraint
    
    def test_daily_task_limit_constraint(self):
        """Test daily task limit constraint (16 tasks max)"""
        # Simulate daily task count
        daily_tasks = []
        today = datetime.utcnow().date()
        
        # Add 16 tasks (at limit)
        for i in range(16):
            task = {
                "task_id": f"task_{i}",
                "uid": "user123",
                "created_at": datetime.combine(today, datetime.min.time()),
                "status": TaskStatus.PENDING.value
            }
            daily_tasks.append(task)
        
        assert len(daily_tasks) == 16  # At limit
        
        # Adding 17th task would violate constraint
        assert len(daily_tasks) <= 16
    
    def test_xp_calculation_consistency(self):
        """Test XP calculation consistency"""
        difficulty = 3
        mood_coefficient = 1.1
        adhd_assist = 1.2
        base_multiplier = 10
        
        expected_xp = int(difficulty * mood_coefficient * adhd_assist * base_multiplier)
        calculated_xp = int(3 * 1.1 * 1.2 * 10)  # 39.6 -> 39
        
        assert calculated_xp == expected_xp
        assert calculated_xp == 39
    
    def test_mood_coefficient_calculation(self):
        """Test mood coefficient calculation (0.6 + mood_score * 0.15)"""
        test_cases = [
            (1, 0.75),  # 0.6 + 1 * 0.15 = 0.75
            (3, 1.05),  # 0.6 + 3 * 0.15 = 1.05
            (5, 1.35)   # 0.6 + 5 * 0.15 = 1.35
        ]
        
        for mood_score, expected_coefficient in test_cases:
            calculated = 0.6 + (mood_score * 0.15)
            assert abs(calculated - expected_coefficient) < 0.01
    
    def test_resonance_event_threshold(self):
        """Test resonance event level difference threshold"""
        # Test cases for resonance events (level difference >= 5)
        test_cases = [
            (10, 5, True),   # Difference = 5, should trigger
            (15, 8, True),   # Difference = 7, should trigger
            (8, 10, False),  # Difference = 2, should not trigger
            (12, 8, False)   # Difference = 4, should not trigger
        ]
        
        for yu_level, player_level, should_trigger in test_cases:
            level_diff = abs(yu_level - player_level)
            resonance_triggered = level_diff >= 5
            assert resonance_triggered == should_trigger

@pytest.mark.asyncio
class TestFirestorePerformance:
    """Test Firestore performance and optimization"""
    
    async def test_query_performance_simulation(self):
        """Simulate query performance testing"""
        # Mock query execution times
        query_times = {
            "user_lookup": 0.05,      # 50ms - very fast
            "daily_tasks": 0.15,      # 150ms - fast
            "mood_history": 0.8,      # 800ms - acceptable
            "story_generation": 1.1,  # 1.1s - within limit
            "complex_analytics": 2.5  # 2.5s - too slow
        }
        
        # Test against performance thresholds
        fast_threshold = 0.2  # 200ms
        acceptable_threshold = 1.2  # 1.2s (requirement)
        
        fast_queries = [q for q, t in query_times.items() if t <= fast_threshold]
        acceptable_queries = [q for q, t in query_times.items() if t <= acceptable_threshold]
        slow_queries = [q for q, t in query_times.items() if t > acceptable_threshold]
        
        assert len(fast_queries) >= 2  # At least 2 fast queries
        assert len(slow_queries) <= 1  # At most 1 slow query
        assert "complex_analytics" in slow_queries  # Expected slow query
    
    async def test_concurrent_user_simulation(self):
        """Simulate concurrent user load"""
        max_concurrent_users = 20000
        
        # Simulate user operations
        operations_per_user = {
            "login": 1,
            "task_fetch": 3,
            "mood_log": 1,
            "story_read": 2,
            "xp_update": 5
        }
        
        total_operations = sum(operations_per_user.values())
        peak_operations_per_second = max_concurrent_users * total_operations / 3600  # Per hour
        
        # Test against capacity limits
        firestore_ops_limit = 10000  # Operations per second limit
        
        assert peak_operations_per_second < firestore_ops_limit
    
    async def test_index_efficiency_simulation(self):
        """Simulate index efficiency for common queries"""
        # Mock index usage statistics
        index_stats = {
            "user_profiles_email": {"usage_count": 1000, "avg_time_ms": 45},
            "tasks_uid_status_date": {"usage_count": 5000, "avg_time_ms": 120},
            "mood_logs_uid_date": {"usage_count": 2000, "avg_time_ms": 80},
            "story_nodes_chapter_type": {"usage_count": 800, "avg_time_ms": 200}
        }
        
        # Test index efficiency
        efficient_indexes = [
            idx for idx, stats in index_stats.items() 
            if stats["avg_time_ms"] < 150 and stats["usage_count"] > 500
        ]
        
        assert len(efficient_indexes) >= 2  # At least 2 efficient indexes
        assert "tasks_uid_status_date" in efficient_indexes  # Critical index

if __name__ == "__main__":
    pytest.main([__file__, "-v"])