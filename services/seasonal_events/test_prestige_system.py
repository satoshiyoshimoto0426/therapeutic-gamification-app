"""
プレビュー
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta
from services.seasonal_events.prestige_system import (
    LongTermEngagementSystem, StoryBranchSystem, CosmeticSystem, PrestigeSystem,
    PrestigeLevel, TherapeuticMilestone, CosmeticType
)

class TestStoryBranchSystem:
    """?"""
    
    def setup_method(self):
        self.story_system = StoryBranchSystem()
    
    def test_initialize_milestone_branches(self):
        """?"""
        assert len(self.story_system.story_branches) >= 4
        assert "first_step_journey" in self.story_system.story_branches
        assert "habit_master_saga" in self.story_system.story_branches
        assert "reconnection_chronicle" in self.story_system.story_branches
        assert "inner_peace_odyssey" in self.story_system.story_branches
    
    def test_check_branch_unlock_success(self):
        """?"""
        user_progress = {
            "tasks_completed": 15,
            "consecutive_days": 5
        }
        
        can_unlock = self.story_system.check_branch_unlock("first_step_journey", user_progress)
        assert can_unlock is True
    
    def test_check_branch_unlock_failure(self):
        """?"""
        user_progress = {
            "tasks_completed": 5,  # ?
            "consecutive_days": 2   # ?
        }
        
        can_unlock = self.story_system.check_branch_unlock("first_step_journey", user_progress)
        assert can_unlock is False
    
    def test_unlock_branch(self):
        """?"""
        success = self.story_system.unlock_branch("first_step_journey", "user_001")
        
        assert success is True
        assert self.story_system.story_branches["first_step_journey"].is_unlocked is True
    
    def test_get_available_branches(self):
        """?"""
        achieved_milestones = {
            TherapeuticMilestone.FIRST_STEP,
            TherapeuticMilestone.HABIT_FORMATION
        }
        
        available_branches = self.story_system.get_available_branches(achieved_milestones)
        
        assert len(available_branches) == 2
        branch_ids = [branch.branch_id for branch in available_branches]
        assert "first_step_journey" in branch_ids
        assert "habit_master_saga" in branch_ids

class TestCosmeticSystem:
    """コア"""
    
    def setup_method(self):
        self.cosmetic_system = CosmeticSystem()
    
    def test_initialize_cosmetic_catalog(self):
        """コア"""
        assert len(self.cosmetic_system.cosmetic_catalog) > 0
        
        # ?
        avatar_items = self.cosmetic_system.get_cosmetics_by_type(CosmeticType.AVATAR)
        background_items = self.cosmetic_system.get_cosmetics_by_type(CosmeticType.BACKGROUND)
        title_items = self.cosmetic_system.get_cosmetics_by_type(CosmeticType.TITLE)
        badge_items = self.cosmetic_system.get_cosmetics_by_type(CosmeticType.BADGE)
        
        assert len(avatar_items) > 0
        assert len(background_items) > 0
        assert len(title_items) > 0
        assert len(badge_items) > 0
    
    def test_check_unlock_condition_success(self):
        """アプリ"""
        user_achievements = {
            "complete_first_task": True,
            "complete_first_week": True
        }
        
        can_unlock = self.cosmetic_system.check_unlock_condition("title_first_steps", user_achievements)
        assert can_unlock is True
    
    def test_check_unlock_condition_failure(self):
        """アプリ"""
        user_achievements = {
            "complete_first_task": False  # ?
        }
        
        can_unlock = self.cosmetic_system.check_unlock_condition("title_first_steps", user_achievements)
        assert can_unlock is False
    
    def test_unlock_cosmetic(self):
        """コア"""
        unlocked_item = self.cosmetic_system.unlock_cosmetic("title_first_steps", "user_001")
        
        assert unlocked_item is not None
        assert unlocked_item.is_unlocked is True
        assert unlocked_item.unlock_date is not None
        assert unlocked_item.name == "は"
    
    def test_get_cosmetics_by_type(self):
        """タスク"""
        avatar_items = self.cosmetic_system.get_cosmetics_by_type(CosmeticType.AVATAR)
        
        assert len(avatar_items) > 0
        for item in avatar_items:
            assert item.cosmetic_type == CosmeticType.AVATAR

class TestPrestigeSystem:
    """プレビュー"""
    
    def setup_method(self):
        self.prestige_system = PrestigeSystem()
    
    def test_calculate_prestige_level(self):
        """プレビュー"""
        # ?
        level = self.prestige_system.calculate_prestige_level(500)
        assert level == PrestigeLevel.NOVICE
        
        # ?
        level = self.prestige_system.calculate_prestige_level(2000)
        assert level == PrestigeLevel.APPRENTICE
        
        # ?
        level = self.prestige_system.calculate_prestige_level(10000)
        assert level == PrestigeLevel.JOURNEYMAN
        
        # ?
        level = self.prestige_system.calculate_prestige_level(20000)
        assert level == PrestigeLevel.EXPERT
    
    def test_check_milestone_achievement(self):
        """?"""
        user_data = {
            "tasks_completed": 5,
            "habit_streak": 25,
            "social_interactions": 60
        }
        
        # ?
        assert self.prestige_system.check_milestone_achievement(
            TherapeuticMilestone.FIRST_STEP, user_data
        ) is True
        
        # ?
        assert self.prestige_system.check_milestone_achievement(
            TherapeuticMilestone.HABIT_FORMATION, user_data
        ) is True
        
        # ?
        assert self.prestige_system.check_milestone_achievement(
            TherapeuticMilestone.SOCIAL_RECONNECTION, user_data
        ) is True
        
        # ?
        assert self.prestige_system.check_milestone_achievement(
            TherapeuticMilestone.EMOTIONAL_STABILITY, user_data
        ) is False

class TestLongTermEngagementSystem:
    """?"""
    
    def setup_method(self):
        self.engagement = LongTermEngagementSystem()
    
    def test_create_prestige_profile(self):
        """プレビュー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        assert profile.user_uid == "user_001"
        assert profile.prestige_level == PrestigeLevel.NOVICE
        assert profile.total_prestige_points == 0
        assert len(profile.achieved_milestones) == 0
        assert len(profile.cosmetic_collection) == 0
    
    def test_update_user_progress_milestone_achievement(self):
        """ユーザー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        progress_data = {
            "tasks_completed": 10,
            "consecutive_days": 5,
            "habit_streak": 25,
            "social_interactions": 60
        }
        
        updates = self.engagement.update_user_progress("user_001", progress_data)
        
        # ?
        assert len(updates["milestones_achieved"]) > 0
        
        # プレビュー
        assert len(profile.achieved_milestones) > 0
        assert profile.total_prestige_points > 0
    
    def test_update_user_progress_story_branch_unlock(self):
        """ユーザー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        # ま
        progress_data = {
            "tasks_completed": 15,
            "consecutive_days": 5
        }
        
        updates = self.engagement.update_user_progress("user_001", progress_data)
        
        # ?
        if updates["branches_unlocked"]:
            assert len(updates["branches_unlocked"]) > 0
            assert len(profile.unlocked_story_branches) > 0
    
    def test_update_user_progress_cosmetic_unlock(self):
        """ユーザー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        progress_data = {
            "tasks_completed": 5,
            "consecutive_days": 10,
            "habit_streak": 25
        }
        
        updates = self.engagement.update_user_progress("user_001", progress_data)
        
        # コア
        if updates["cosmetics_unlocked"]:
            assert len(updates["cosmetics_unlocked"]) > 0
            assert len(profile.cosmetic_collection) > 0
    
    def test_get_user_engagement_summary(self):
        """ユーザー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        # ?
        progress_data = {
            "tasks_completed": 20,
            "consecutive_days": 10,
            "habit_streak": 25,
            "social_interactions": 40
        }
        
        self.engagement.update_user_progress("user_001", progress_data)
        
        summary = self.engagement.get_user_engagement_summary("user_001")
        
        assert "prestige_level" in summary
        assert "total_prestige_points" in summary
        assert "achieved_milestones" in summary
        assert "cosmetic_collection_size" in summary
        assert "available_story_branches" in summary
        assert summary["days_since_creation"] >= 0
    
    def test_equip_cosmetic(self):
        """コア"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        # ま
        progress_data = {
            "tasks_completed": 5,
            "consecutive_days": 10
        }
        
        self.engagement.update_user_progress("user_001", progress_data)
        
        # ?
        if profile.cosmetic_collection:
            item_id = list(profile.cosmetic_collection.keys())[0]
            success = self.engagement.equip_cosmetic("user_001", item_id)
            
            assert success is True
            
            # ?
            item = profile.cosmetic_collection[item_id]
            assert profile.equipped_cosmetics[item.cosmetic_type] == item_id
    
    def test_prestige_level_progression(self):
        """プレビュー"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        # ?
        progress_stages = [
            {"tasks_completed": 10, "habit_streak": 25},
            {"tasks_completed": 50, "habit_streak": 50, "social_interactions": 60},
            {"tasks_completed": 100, "habit_streak": 100, "social_interactions": 100, 
             "mood_stability_days": 35, "self_efficacy_score": 85}
        ]
        
        initial_level = profile.prestige_level
        
        for stage in progress_stages:
            updates = self.engagement.update_user_progress("user_001", stage)
            
            # レベル
            if updates["prestige_level_up"]:
                assert profile.prestige_level.value != initial_level.value
                initial_level = profile.prestige_level
    
    def test_long_term_engagement_simulation(self):
        """?"""
        profile = self.engagement.create_prestige_profile("user_001")
        
        # 3?
        monthly_progress = [
            # 1?
            {
                "tasks_completed": 30,
                "consecutive_days": 15,
                "habit_streak": 15,
                "social_interactions": 20,
                "reflection_entries": 10
            },
            # 2?
            {
                "tasks_completed": 80,
                "consecutive_days": 25,
                "habit_streak": 30,
                "social_interactions": 50,
                "reflection_entries": 30,
                "mood_stability_days": 20
            },
            # 3?
            {
                "tasks_completed": 150,
                "consecutive_days": 40,
                "habit_streak": 50,
                "social_interactions": 100,
                "reflection_entries": 60,
                "mood_stability_days": 35,
                "self_efficacy_score": 85,
                "peer_support_given": 30
            }
        ]
        
        for month, progress in enumerate(monthly_progress):
            updates = self.engagement.update_user_progress("user_001", progress)
            
            print(f"? {month + 1}: ? = {len(updates['milestones_achieved'])}")
            print(f"? {month + 1}: ? = {len(updates['branches_unlocked'])}")
            print(f"? {month + 1}: コア = {len(updates['cosmetics_unlocked'])}")
        
        # ?
        final_summary = self.engagement.get_user_engagement_summary("user_001")
        
        assert len(final_summary["achieved_milestones"]) > 0
        assert final_summary["total_prestige_points"] > 0
        assert final_summary["cosmetic_collection_size"] > 0
        assert final_summary["prestige_level"] != "novice"  # ?

def test_full_prestige_workflow():
    """?"""
    engagement = LongTermEngagementSystem()
    
    # 1. プレビュー
    user_uid = "test_user"
    profile = engagement.create_prestige_profile(user_uid)
    print(f"? プレビュー: {user_uid}")
    
    # 2. ?
    initial_progress = {
        "tasks_completed": 15,
        "consecutive_days": 10,
        "habit_streak": 25,
        "social_interactions": 30
    }
    
    updates = engagement.update_user_progress(user_uid, initial_progress)
    print(f"? ?: ? {len(updates['milestones_achieved'])} ?")
    
    # 3. ?
    mid_progress = {
        "tasks_completed": 60,
        "consecutive_days": 25,
        "habit_streak": 40,
        "social_interactions": 80,
        "reflection_entries": 40,
        "mood_stability_days": 25
    }
    
    updates = engagement.update_user_progress(user_uid, mid_progress)
    print(f"? ?: ? {len(updates['branches_unlocked'])} ?")
    
    # 4. ?
    long_progress = {
        "tasks_completed": 120,
        "consecutive_days": 50,
        "habit_streak": 60,
        "social_interactions": 150,
        "reflection_entries": 80,
        "mood_stability_days": 40,
        "self_efficacy_score": 90,
        "peer_support_given": 40
    }
    
    updates = engagement.update_user_progress(user_uid, long_progress)
    print(f"? ?: コア {len(updates['cosmetics_unlocked'])} ?")
    
    # 5. ?
    final_summary = engagement.get_user_engagement_summary(user_uid)
    
    print(f"? ?:")
    print(f"   - プレビュー: {final_summary['prestige_level']}")
    print(f"   - ?: {final_summary['total_prestige_points']}")
    print(f"   - ?: {len(final_summary['achieved_milestones'])}")
    print(f"   - コア: {final_summary['cosmetic_collection_size']} ?")
    print(f"   - ?: {final_summary['unlocked_story_branches']} ?")
    print(f"   - レベル: {len(final_summary['legacy_achievements'])} ?")
    
    return {
        "success": True,
        "prestige_level": final_summary['prestige_level'],
        "total_points": final_summary['total_prestige_points'],
        "milestones": len(final_summary['achieved_milestones']),
        "cosmetics": final_summary['cosmetic_collection_size']
    }

if __name__ == "__main__":
    # ?
    result = test_full_prestige_workflow()
    print(f"\n? プレビュー: {result}")
    
    # ?
    pytest.main([__file__, "-v"])