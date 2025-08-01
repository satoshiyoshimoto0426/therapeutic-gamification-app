"""
Tests for data model validation and integrity functions
Ensures validation logic works correctly across all scenarios
"""

import pytest
from datetime import datetime, timedelta
from .core_types import UserProfile, TaskRecord, TaskType, TaskStatus, GrowthNoteEntry
from .model_factory import ModelFactory
from .validation import DataIntegrityValidator, BusinessRuleValidator
from ..utils.exceptions import ValidationError

class TestModelFactory:
    """Test model factory functions"""
    
    def test_create_user_profile_valid(self):
        """Test creating a valid user profile"""
        profile = ModelFactory.create_user_profile(
            uid="test_user_123",
            email="test@example.com",
            display_name="?",
            therapeutic_goals=["?", "?"]
        )
        
        assert profile.uid == "test_user_123"
        assert profile.email == "test@example.com"
        assert profile.display_name == "?"
        assert len(profile.crystal_gauges) == 8
        assert profile.daily_task_limit == 16
        assert "?" in profile.therapeutic_goals
    
    def test_create_user_profile_invalid_email(self):
        """Test creating user profile with invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            ModelFactory.create_user_profile(
                uid="test_user_123",
                email="invalid-email",
                display_name="?"
            )
        
        assert "無" in str(exc_info.value)
    
    def test_create_task_record_valid(self):
        """Test creating a valid task record"""
        task = ModelFactory.create_task_record(
            task_id="task_123",
            uid="user_123",
            task_type=TaskType.ROUTINE,
            title="?",
            description="30?",
            difficulty=3
        )
        
        assert task.task_id == "task_123"
        assert task.task_type == TaskType.ROUTINE
        assert task.title == "?"
        assert task.difficulty == 3
        assert task.status == TaskStatus.PENDING
    
    def test_create_task_record_invalid_difficulty(self):
        """Test creating task with invalid difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            ModelFactory.create_task_record(
                task_id="task_123",
                uid="user_123",
                task_type=TaskType.ROUTINE,
                title="?",
                description="?",
                difficulty=6  # Invalid: should be 1-5
            )
        
        assert "?1-5の" in str(exc_info.value)
    
    def test_create_growth_note_entry_valid(self):
        """Test creating a valid growth note entry"""
        entry = ModelFactory.create_growth_note_entry(
            uid="user_123",
            current_problems="?",
            ideal_world="?",
            ideal_emotions="?",
            tomorrow_actions="?"
        )
        
        assert entry.uid == "user_123"
        assert "ストーリー" in entry.current_problems
        assert entry.emotional_tone in ["positive", "negative", "neutral"]
        assert len(entry.key_themes) >= 0
        assert entry.xp_earned == 25

class TestDataIntegrityValidator:
    """Test data integrity validation functions"""
    
    def test_validate_user_profile_consistency_valid(self):
        """Test validating a consistent user profile"""
        profile = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="?",
            player_level=5,
            yu_level=4,
            total_xp=500,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        result = DataIntegrityValidator.validate_user_profile_consistency(profile)
        
        assert result["valid"] == True
        assert len(result["errors"]) == 0
        assert result["level_difference"] == 1
        assert result["resonance_available"] == False
    
    def test_validate_user_profile_consistency_resonance(self):
        """Test validating user profile with resonance event available"""
        profile = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="?",
            player_level=10,
            yu_level=5,  # Difference of 5 triggers resonance
            total_xp=1000,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        result = DataIntegrityValidator.validate_user_profile_consistency(profile)
        
        assert result["valid"] == True
        assert result["level_difference"] == 5
        assert result["resonance_available"] == True
        assert "共有" in result["warnings"][0]
    
    def test_validate_task_business_rules_within_limit(self):
        """Test task validation within daily limit"""
        user_profile = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="?",
            daily_task_limit=16,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        task = TaskRecord(
            task_id="new_task",
            uid="test_user",
            task_type=TaskType.ROUTINE,
            title="?",
            description="?",
            difficulty=3,
            created_at=datetime.now()
        )
        
        # Create some existing tasks (within limit)
        existing_tasks = []
        for i in range(10):  # 10 tasks < 16 limit
            existing_tasks.append(TaskRecord(
                task_id=f"task_{i}",
                uid="test_user",
                task_type=TaskType.ROUTINE,
                title=f"タスク {i}",
                description="?",
                difficulty=2,
                created_at=datetime.now()
            ))
        
        result = DataIntegrityValidator.validate_task_business_rules(
            task, user_profile, existing_tasks
        )
        
        assert result["valid"] == True
        assert result["daily_task_count"] == 10
        assert result["remaining_tasks"] == 6
    
    def test_validate_task_business_rules_exceeds_limit(self):
        """Test task validation exceeding daily limit"""
        user_profile = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="?",
            daily_task_limit=5,  # Low limit for testing
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        task = TaskRecord(
            task_id="new_task",
            uid="test_user",
            task_type=TaskType.ROUTINE,
            title="?",
            description="?",
            difficulty=3,
            created_at=datetime.now()
        )
        
        # Create tasks at the limit
        existing_tasks = []
        for i in range(5):  # 5 tasks = limit
            existing_tasks.append(TaskRecord(
                task_id=f"task_{i}",
                uid="test_user",
                task_type=TaskType.ROUTINE,
                title=f"タスク {i}",
                description="?",
                difficulty=2,
                created_at=datetime.now()
            ))
        
        result = DataIntegrityValidator.validate_task_business_rules(
            task, user_profile, existing_tasks
        )
        
        assert result["valid"] == False
        assert "?" in result["errors"][0]
        assert result["remaining_tasks"] == 0
    
    def test_validate_xp_calculation_integrity_correct(self):
        """Test XP calculation validation with correct values"""
        task = TaskRecord(
            task_id="task_123",
            uid="user_123",
            task_type=TaskType.ROUTINE,
            title="?",
            description="?",
            difficulty=3,
            created_at=datetime.now()
        )
        
        mood_score = 4  # mood_coefficient = 1.1
        adhd_assist = 1.2
        expected_xp = int(3 * 10 * 1.1 * 1.2)  # 39.6 -> 39
        
        result = DataIntegrityValidator.validate_xp_calculation_integrity(
            task, mood_score, adhd_assist, expected_xp
        )
        
        assert result["valid"] == True
        assert len(result["errors"]) == 0
        assert result["calculated_xp"] == expected_xp
    
    def test_validate_growth_note_consistency_valid(self):
        """Test growth note validation with valid entry"""
        entry = GrowthNoteEntry(
            uid="user_123",
            entry_date=datetime.now(),
            current_problems="?",
            ideal_world="理",
            ideal_emotions="?",
            tomorrow_actions="?",
            created_at=datetime.now()
        )
        
        # No previous entries for today
        previous_entries = []
        
        result = DataIntegrityValidator.validate_growth_note_consistency(
            entry, previous_entries
        )
        
        assert result["valid"] == True
        assert result["streak_eligible"] == True
        assert result["content_length"] > 0

class TestBusinessRuleValidator:
    """Test business rule validation functions"""
    
    def test_validate_adhd_accommodation_rules(self):
        """Test ADHD accommodation validation"""
        # User with ADHD profile
        user_profile = UserProfile(
            uid="test_user",
            email="test@example.com",
            display_name="?",
            adhd_profile={"diagnosed": True, "severity": "moderate"},
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        # High difficulty task without ADHD support
        task = TaskRecord(
            task_id="difficult_task",
            uid="test_user",
            task_type=TaskType.SKILL_UP,
            title="?",
            description="?" * 10,  # Long description
            difficulty=5,  # High difficulty
            due_date=datetime.now() + timedelta(hours=12),  # Due soon
            adhd_support={},  # No support configured
            created_at=datetime.now()
        )
        
        result = BusinessRuleValidator.validate_adhd_accommodation_rules(
            task, user_profile
        )
        
        assert result["accommodations_needed"] == True
        assert len(result["recommendations"]) > 0
        assert result["adhd_friendly"] == False
        
        # Check for specific recommendations
        recommendations_text = " ".join(result["recommendations"])
        assert "Pomodoro" in recommendations_text or "リスト" in recommendations_text

if __name__ == "__main__":
    pytest.main([__file__])