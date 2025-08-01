"""
?
"""

import pytest
from datetime import datetime, timedelta
from advanced_job_system import (
    AdvancedJobSystem, AdvancedJobManager, UnlockCondition, UnlockConditionType,
    StoryIntegration, AchievementTracker, create_advanced_job_manager
)
from main import JobSystem, JobType


class TestAdvancedJobSystem:
    """AdvancedJobSystem?"""
    
    def setup_method(self):
        """?"""
        self.base_job_system = JobSystem()
        self.advanced_system = AdvancedJobSystem(self.base_job_system)
    
    def test_advanced_unlock_conditions_initialization(self):
        """?"""
        conditions = self.advanced_system.advanced_unlock_conditions
        
        # 3つ
        assert JobType.PALADIN in conditions
        assert JobType.ARCHMAGE in conditions
        assert JobType.SHADOW_MASTER in conditions
        
        # ?
        paladin_conditions = conditions[JobType.PALADIN]
        assert len(paladin_conditions) == 5
        
        # ?
        condition_types = [cond.condition_type for cond in paladin_conditions]
        assert UnlockConditionType.JOB_LEVEL in condition_types
        assert UnlockConditionType.TASK_COMPLETION in condition_types
        assert UnlockConditionType.STORY_BRANCH in condition_types
        assert UnlockConditionType.ACHIEVEMENT in condition_types
    
    def test_paladin_unlock_conditions_success(self):
        """?"""
        user_data = {
            "job_levels": {"warrior": 10, "priest": 5},
            "task_completions": {"social_tasks": 50},
            "story_branches": {"helped_others_count": 10},
            "achievements": {"community_leader": True}
        }
        
        result = self.advanced_system.check_advanced_unlock_conditions(JobType.PALADIN, user_data)
        
        assert result["unlocked"] == True
        assert len(result["conditions_met"]) == 5
        assert len(result["conditions_failed"]) == 0
    
    def test_paladin_unlock_conditions_failure(self):
        """?"""
        user_data = {
            "job_levels": {"warrior": 8, "priest": 3},  # ?
            "task_completions": {"social_tasks": 30},   # ?
            "story_branches": {"helped_others_count": 5}, # ?
            "achievements": {"community_leader": False}  # ?
        }
        
        result = self.advanced_system.check_advanced_unlock_conditions(JobType.PALADIN, user_data)
        
        assert result["unlocked"] == False
        assert len(result["conditions_met"]) == 0
        assert len(result["conditions_failed"]) == 5
        
        # ?
        warrior_progress = result["progress"]["warrior_level"]
        assert warrior_progress["current_value"] == 8
        assert warrior_progress["required_value"] == 10
        assert warrior_progress["progress_percentage"] == 80.0
    
    def test_archmage_unlock_conditions(self):
        """?"""
        user_data = {
            "job_levels": {"mage": 15},
            "stats": {"wisdom": 20},
            "task_completions": {"creative_tasks": 100},
            "story_branches": {"innovative_solutions": 15},
            "achievements": {"master_innovator": True},
            "time_based": {"continuous_learning_days": 30}
        }
        
        result = self.advanced_system.check_advanced_unlock_conditions(JobType.ARCHMAGE, user_data)
        
        assert result["unlocked"] == True
        assert len(result["conditions_met"]) == 6
    
    def test_shadow_master_combination_condition(self):
        """?"""
        user_data = {
            "job_levels": {"ninja": 12},
            "stats": {"resilience": 25},
            "task_completions": {"stress_overcome": 30},
            "story_branches": {"shadow_path_choices": 20},
            "achievements": {"stress_master": True},
            "combination_conditions": {
                "environment_changes_adapted": 50,
                "crisis_overcome": 10,
                "flexibility_score": 0.8
            }
        }
        
        result = self.advanced_system.check_advanced_unlock_conditions(JobType.SHADOW_MASTER, user_data)
        
        assert result["unlocked"] == True
        
        # ?
        combination_progress = result["progress"]["adaptation_mastery"]
        assert "current_value" in combination_progress
        assert isinstance(combination_progress["current_value"], dict)
    
    def test_unlock_progress_summary(self):
        """アプリ"""
        user_data = {
            "job_levels": {"warrior": 8, "priest": 3, "mage": 10, "ninja": 8},
            "stats": {"wisdom": 15, "resilience": 20},
            "task_completions": {"social_tasks": 30, "creative_tasks": 60, "stress_overcome": 20},
            "story_branches": {"helped_others_count": 5, "innovative_solutions": 8, "shadow_path_choices": 12},
            "achievements": {"community_leader": False, "master_innovator": False, "stress_master": False},
            "time_based": {"continuous_learning_days": 20},
            "combination_conditions": {
                "environment_changes_adapted": 30,
                "crisis_overcome": 5,
                "flexibility_score": 0.6
            }
        }
        
        summary = self.advanced_system.get_unlock_progress_summary(user_data)
        
        # 3つ
        assert "paladin" in summary
        assert "archmage" in summary
        assert "shadow_master" in summary
        
        # ?
        paladin_info = summary["paladin"]
        assert paladin_info["name"] == "?"
        assert paladin_info["unlocked"] == False
        assert paladin_info["conditions_total"] == 5
        assert "overall_progress" in paladin_info
        assert "next_milestone" in paladin_info
    
    def test_story_integration(self):
        """ストーリー"""
        story_integrations = self.advanced_system.story_integrations
        
        # 3つ
        assert JobType.PALADIN in story_integrations
        assert JobType.ARCHMAGE in story_integrations
        assert JobType.SHADOW_MASTER in story_integrations
        
        # ?
        paladin_story = story_integrations[JobType.PALADIN]
        assert paladin_story.job_unlock_story_node == "paladin_awakening"
        assert "?" in paladin_story.job_change_dialogue
        assert len(paladin_story.special_story_branches) == 4
        assert "自動" in paladin_story.character_development_arc
    
    def test_job_change_story_generation(self):
        """?"""
        user_context = {"current_level": 15, "recent_achievements": ["community_leader"]}
        
        story = self.advanced_system.generate_job_change_story(JobType.PALADIN, user_context)
        
        assert "story_node" in story
        assert story["story_node"] == "paladin_awakening"
        assert "dialogue" in story
        assert "character_arc" in story
        assert "special_choices" in story
        assert len(story["special_choices"]) <= 3  # ADHD?3?
        assert "therapeutic_message" in story
        
        # ?
        for choice in story["special_choices"]:
            assert "choice_id" in choice
            assert "text" in choice
            assert "story_impact" in choice


class TestAchievementTracker:
    """AchievementTracker?"""
    
    def setup_method(self):
        """?"""
        self.achievement_tracker = AchievementTracker()
    
    def test_achievement_initialization(self):
        """実装"""
        achievements = self.achievement_tracker.achievements
        
        # 3つ
        assert "community_leader" in achievements
        assert "master_innovator" in achievements
        assert "stress_master" in achievements
        
        # コア
        community_leader = achievements["community_leader"]
        assert community_leader["name"] == "コア"
        assert "requirements" in community_leader
        assert "therapeutic_value" in community_leader
    
    def test_achievement_check_success(self):
        """実装"""
        user_data = {
            "help_others_count": 25,
            "group_activities": 15,
            "positive_feedback": 20
        }
        
        result = self.achievement_tracker.check_achievement("community_leader", user_data)
        assert result == True
    
    def test_achievement_check_failure(self):
        """実装"""
        user_data = {
            "help_others_count": 15,  # ?
            "group_activities": 8,    # ?
            "positive_feedback": 10   # ?
        }
        
        result = self.achievement_tracker.check_achievement("community_leader", user_data)
        assert result == False
    
    def test_achievement_progress(self):
        """実装"""
        user_data = {
            "help_others_count": 15,
            "group_activities": 8,
            "positive_feedback": 10
        }
        
        progress = self.achievement_tracker.get_achievement_progress("community_leader", user_data)
        
        assert progress["achievement_id"] == "community_leader"
        assert progress["name"] == "コア"
        assert progress["completed"] == False
        assert "progress" in progress
        
        # ?
        help_progress = progress["progress"]["help_others_count"]
        assert help_progress["current"] == 15
        assert help_progress["required"] == 20
        assert help_progress["percentage"] == 75.0


class TestAdvancedJobManager:
    """AdvancedJobManager?"""
    
    def setup_method(self):
        """?"""
        self.advanced_manager = AdvancedJobManager()
    
    def test_advanced_unlock_status(self):
        """?"""
        user_stats = {
            "job_levels": {"warrior": 8, "priest": 4, "mage": 12},
            "stats": {"wisdom": 18, "resilience": 22},
            "task_completions": {"social_tasks": 40, "creative_tasks": 80},
            "achievements": {"community_leader": False, "master_innovator": False}
        }
        
        status = self.advanced_manager.get_advanced_unlock_status("test_user", user_stats)
        
        assert "paladin" in status
        assert "archmage" in status
        assert "shadow_master" in status
        
        # ?
        for job_key in status:
            job_info = status[job_key]
            assert "name" in job_info
            assert "unlocked" in job_info
            assert "conditions_met" in job_info
            assert "conditions_total" in job_info
            assert "overall_progress" in job_info
    
    def test_advanced_job_change_success(self):
        """?"""
        # ユーザー
        self.advanced_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        # ?
        user_stats = {
            "job_levels": {"warrior": 10, "priest": 5},
            "task_completions": {"social_tasks": 50},
            "story_branches": {"helped_others_count": 10},
            "achievements": {"community_leader": True}
        }
        
        result = self.advanced_manager.attempt_advanced_job_change("test_user", JobType.PALADIN, user_stats)
        
        assert result["success"] == True
        assert result["job_changed"] == True
        assert "story_content" in result
        assert "unlock_status" in result
        
        # ストーリー
        story = result["story_content"]
        assert "dialogue" in story
        assert "special_choices" in story
        assert "therapeutic_message" in story
    
    def test_advanced_job_change_failure(self):
        """?"""
        # ユーザー
        self.advanced_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        # ?
        user_stats = {
            "job_levels": {"warrior": 5, "priest": 2},
            "task_completions": {"social_tasks": 20},
            "story_branches": {"helped_others_count": 3},
            "achievements": {"community_leader": False}
        }
        
        result = self.advanced_manager.attempt_advanced_job_change("test_user", JobType.PALADIN, user_stats)
        
        assert result["success"] == False
        assert result["reason"] == "conditions_not_met"
        assert "unlock_status" in result
        
        # アプリ
        unlock_status = result["unlock_status"]
        assert unlock_status["unlocked"] == False
        assert len(unlock_status["conditions_failed"]) > 0
    
    def test_next_milestones(self):
        """?"""
        user_stats = {
            "job_levels": {"warrior": 8, "priest": 4, "mage": 12, "ninja": 10},
            "stats": {"wisdom": 18, "resilience": 22},
            "task_completions": {"social_tasks": 40, "creative_tasks": 80, "stress_overcome": 25},
            "story_branches": {"helped_others_count": 8, "innovative_solutions": 12, "shadow_path_choices": 15},
            "achievements": {"community_leader": False, "master_innovator": False, "stress_master": False},
            "time_based": {"continuous_learning_days": 25},
            "combination_conditions": {
                "environment_changes_adapted": 40,
                "crisis_overcome": 8,
                "flexibility_score": 0.7
            }
        }
        
        milestones = self.advanced_manager.get_next_milestones("test_user", user_stats)
        
        # ?
        assert len(milestones) > 0
        
        for i in range(len(milestones) - 1):
            assert milestones[i]["overall_progress"] >= milestones[i + 1]["overall_progress"]
        
        # ?
        for milestone in milestones:
            assert "job_type" in milestone
            assert "job_name" in milestone
            assert "milestone" in milestone
            assert "overall_progress" in milestone


class TestIntegration:
    """?"""
    
    def test_complete_advanced_job_workflow(self):
        """?"""
        advanced_manager = create_advanced_job_manager()
        
        # 1. ユーザー
        advanced_manager.initialize_user_job("integration_user", JobType.WARRIOR)
        
        # 2. 基本
        for _ in range(10):
            advanced_manager.add_job_experience("integration_user", 100)
        
        # 3. ?
        advanced_manager.change_job("integration_user", JobType.PRIEST, {})
        for _ in range(5):
            advanced_manager.add_job_experience("integration_user", 100)
        
        # 4. ?
        user_stats = {
            "job_levels": {"warrior": 10, "priest": 5},
            "task_completions": {"social_tasks": 50},
            "story_branches": {"helped_others_count": 10},
            "achievements": {"community_leader": True}
        }
        
        # 5. アプリ
        unlock_status = advanced_manager.get_advanced_unlock_status("integration_user", user_stats)
        assert unlock_status["paladin"]["unlocked"] == True
        
        # 6. ?
        change_result = advanced_manager.attempt_advanced_job_change("integration_user", JobType.PALADIN, user_stats)
        assert change_result["success"] == True
        
        # 7. ?
        job_info = advanced_manager.get_user_job_info("integration_user")
        assert job_info["current_job"]["type"] == "paladin"
        assert job_info["current_job"]["name"] == "?"
        
        # 8. ストーリー
        story = change_result["story_content"]
        assert "?" in story["dialogue"] or "?" in story["dialogue"]
        assert len(story["special_choices"]) <= 3  # ADHD?
    
    def test_multiple_advanced_jobs_progression(self):
        """?"""
        advanced_manager = create_advanced_job_manager()
        
        # ?
        super_user_stats = {
            "job_levels": {"warrior": 15, "priest": 10, "mage": 20, "ninja": 15},
            "stats": {"wisdom": 25, "resilience": 30},
            "task_completions": {"social_tasks": 100, "creative_tasks": 150, "stress_overcome": 50},
            "story_branches": {"helped_others_count": 20, "innovative_solutions": 25, "shadow_path_choices": 30},
            "achievements": {"community_leader": True, "master_innovator": True, "stress_master": True},
            "time_based": {"continuous_learning_days": 45},
            "combination_conditions": {
                "environment_changes_adapted": 80,
                "crisis_overcome": 20,
                "flexibility_score": 0.95
            }
        }
        
        # ?
        unlock_status = advanced_manager.get_advanced_unlock_status("super_user", super_user_stats)
        
        assert unlock_status["paladin"]["unlocked"] == True
        assert unlock_status["archmage"]["unlocked"] == True
        assert unlock_status["shadow_master"]["unlocked"] == True
        
        # ?100%で
        for job_key in unlock_status:
            assert unlock_status[job_key]["overall_progress"] == 100.0


if __name__ == "__main__":
    # ?
    pytest.main([__file__, "-v"])