"""
?
"""

import pytest
from datetime import datetime
from main import (
    JobSystem, JobManager, JobType, Job, JobSkill, UserJobData,
    create_job_manager
)


class TestJobSystem:
    """JobSystem?"""
    
    def setup_method(self):
        """?"""
        self.job_system = JobSystem()
    
    def test_initialize_base_jobs(self):
        """基本"""
        base_jobs = self.job_system.get_base_jobs()
        
        # 6つ
        assert len(base_jobs) == 6
        
        # ?
        job_names = [job.name for job in base_jobs]
        expected_names = ["?", "勇", "?", "?", "?", "?"]
        for name in expected_names:
            assert name in job_names
    
    def test_warrior_job_details(self):
        """?"""
        warrior = self.job_system.get_job(JobType.WARRIOR)
        
        assert warrior is not None
        assert warrior.name == "?"
        assert warrior.focus_attribute == "Self-Discipline"
        assert warrior.therapeutic_focus == "?"
        assert warrior.stat_bonuses == {"resilience": 2, "focus": 1}
        assert len(warrior.skills) == 3
        assert not warrior.is_advanced
        
        # ストーリー
        skill_names = [skill.name for skill in warrior.skills]
        assert "?" in skill_names
        assert "タスク" in skill_names
        assert "?" in skill_names
    
    def test_mage_job_details(self):
        """?"""
        mage = self.job_system.get_job(JobType.MAGE)
        
        assert mage is not None
        assert mage.name == "?"
        assert mage.focus_attribute == "Creativity"
        assert mage.therapeutic_focus == "創"
        assert mage.stat_bonuses == {"creativity": 2, "wisdom": 1}
        assert len(mage.skills) == 3
    
    def test_advanced_jobs(self):
        """?"""
        advanced_jobs = self.job_system.get_advanced_jobs()
        
        # 3つ
        assert len(advanced_jobs) == 3
        
        # ?
        paladin = self.job_system.get_job(JobType.PALADIN)
        assert paladin is not None
        assert paladin.name == "?"
        assert paladin.is_advanced
        assert paladin.unlock_requirements == {"warrior": 10, "priest": 5, "social_tasks": 50}
        assert paladin.stat_bonuses == {"resilience": 3, "social": 2, "motivation": 1}
    
    def test_job_unlock_conditions(self):
        """?"""
        # 基本
        assert self.job_system.check_job_unlock({}, JobType.WARRIOR)
        assert self.job_system.check_job_unlock({}, JobType.MAGE)
        
        # ?
        insufficient_stats = {"warrior": 5, "priest": 2, "social_tasks": 20}
        assert not self.job_system.check_job_unlock(insufficient_stats, JobType.PALADIN)
        
        sufficient_stats = {"warrior": 10, "priest": 5, "social_tasks": 50}
        assert self.job_system.check_job_unlock(sufficient_stats, JobType.PALADIN)
        
        # ?
        archmage_stats = {"mage": 15, "wisdom": 20, "creative_tasks": 100}
        assert self.job_system.check_job_unlock(archmage_stats, JobType.ARCHMAGE)
    
    def test_stat_bonuses_calculation(self):
        """?"""
        # レベル1の
        bonuses_lv1 = self.job_system.calculate_stat_bonuses(JobType.WARRIOR, 1)
        assert bonuses_lv1 == {"resilience": 2, "focus": 1}
        
        # レベル3の10%?
        bonuses_lv3 = self.job_system.calculate_stat_bonuses(JobType.WARRIOR, 3)
        expected_resilience = int(2 * (1.0 + (3-1) * 0.1))  # 2 * 1.2 = 2.4 -> 2
        expected_focus = int(1 * (1.0 + (3-1) * 0.1))       # 1 * 1.2 = 1.2 -> 1
        assert bonuses_lv3 == {"resilience": expected_resilience, "focus": expected_focus}
    
    def test_available_skills(self):
        """?"""
        # レベル1で
        skills_lv1 = self.job_system.get_available_skills(JobType.WARRIOR, 1)
        assert len(skills_lv1) == 1
        assert skills_lv1[0].name == "?"
        
        # レベル3で
        skills_lv3 = self.job_system.get_available_skills(JobType.WARRIOR, 3)
        assert len(skills_lv3) == 2
        skill_names = [skill.name for skill in skills_lv3]
        assert "?" in skill_names
        assert "タスク" in skill_names
        
        # レベル5で
        skills_lv5 = self.job_system.get_available_skills(JobType.WARRIOR, 5)
        assert len(skills_lv5) == 3
    
    def test_task_efficiency_bonus(self):
        """タスク"""
        # レベル1?
        bonus_lv1 = self.job_system.calculate_task_efficiency_bonus(JobType.WARRIOR, 1, "routine")
        assert bonus_lv1 == 0.2  # ?
        
        # レベル3?
        bonus_lv3 = self.job_system.calculate_task_efficiency_bonus(JobType.WARRIOR, 3, "routine")
        assert bonus_lv3 == 0.2  # ?XP?
        
        # ?
        mage_bonus = self.job_system.calculate_task_efficiency_bonus(JobType.MAGE, 1, "creative")
        assert mage_bonus == 0.25  # アプリ


class TestJobManager:
    """JobManager?"""
    
    def setup_method(self):
        """?"""
        self.job_manager = JobManager()
    
    def test_initialize_user_job(self):
        """ユーザー"""
        user_data = self.job_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        assert user_data.uid == "test_user"
        assert user_data.current_job == JobType.WARRIOR
        assert user_data.job_level == 1
        assert user_data.job_experience == 0
        assert len(user_data.unlocked_jobs) == 6  # 基本6つ
        assert len(user_data.job_change_history) == 1
        
        # アプリ
        advanced_jobs = [JobType.PALADIN, JobType.ARCHMAGE, JobType.SHADOW_MASTER]
        for advanced_job in advanced_jobs:
            assert advanced_job not in user_data.unlocked_jobs
    
    def test_job_change_success(self):
        """?"""
        # ユーザー
        self.job_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        # 基本
        user_stats = {}  # 基本
        success = self.job_manager.change_job("test_user", JobType.MAGE, user_stats)
        
        assert success
        user_data = self.job_manager.user_jobs["test_user"]
        assert user_data.current_job == JobType.MAGE
        assert user_data.job_level == 1  # ?1か
        assert user_data.job_experience == 0
        assert len(user_data.job_change_history) == 2
    
    def test_job_change_failure(self):
        """?"""
        # ユーザー
        self.job_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        # ?
        insufficient_stats = {"warrior": 5, "priest": 2, "social_tasks": 20}
        success = self.job_manager.change_job("test_user", JobType.PALADIN, insufficient_stats)
        
        assert not success
        user_data = self.job_manager.user_jobs["test_user"]
        assert user_data.current_job == JobType.WARRIOR  # ?
    
    def test_add_job_experience(self):
        """?"""
        # ユーザー
        self.job_manager.initialize_user_job("test_user", JobType.WARRIOR)
        
        # ?
        leveled_up = self.job_manager.add_job_experience("test_user", 50)
        assert not leveled_up
        
        user_data = self.job_manager.user_jobs["test_user"]
        assert user_data.job_experience == 50
        assert user_data.job_level == 1
        
        # ?
        leveled_up = self.job_manager.add_job_experience("test_user", 60)  # ?110
        assert leveled_up
        
        user_data = self.job_manager.user_jobs["test_user"]
        assert user_data.job_level == 2
        assert user_data.job_experience == 10  # 100消10?
    
    def test_get_user_job_info(self):
        """ユーザー"""
        # ユーザー
        self.job_manager.initialize_user_job("test_user", JobType.WARRIOR)
        self.job_manager.add_job_experience("test_user", 50)
        
        job_info = self.job_manager.get_user_job_info("test_user")
        
        assert job_info is not None
        assert job_info["uid"] == "test_user"
        assert job_info["current_job"]["type"] == "warrior"
        assert job_info["current_job"]["name"] == "?"
        assert job_info["current_job"]["level"] == 1
        assert job_info["current_job"]["experience"] == 50
        assert job_info["current_job"]["required_exp"] == 100
        
        # ?
        assert "stat_bonuses" in job_info
        assert job_info["stat_bonuses"]["resilience"] == 2
        assert job_info["stat_bonuses"]["focus"] == 1
        
        # ?
        assert "available_skills" in job_info
        assert len(job_info["available_skills"]) == 1
        assert job_info["available_skills"][0]["name"] == "?"
    
    def test_required_experience_calculation(self):
        """?"""
        # レベル1 -> 2: 100?
        assert self.job_manager._calculate_required_experience(1) == 100
        
        # レベル2 -> 3: 200?
        assert self.job_manager._calculate_required_experience(2) == 200
        
        # レベル5 -> 6: 500?
        assert self.job_manager._calculate_required_experience(5) == 500


class TestJobSkill:
    """JobSkill?"""
    
    def test_job_skill_creation(self):
        """JobSkillの"""
        skill = JobSkill(
            skill_id="test_skill",
            name="?",
            description="?",
            effect_type="stat_bonus",
            effect_value=0.15,
            unlock_level=3
        )
        
        assert skill.skill_id == "test_skill"
        assert skill.name == "?"
        assert skill.description == "?"
        assert skill.effect_type == "stat_bonus"
        assert skill.effect_value == 0.15
        assert skill.unlock_level == 3


class TestIntegration:
    """?"""
    
    def test_complete_job_workflow(self):
        """?"""
        job_manager = create_job_manager()
        
        # 1. ユーザー
        user_data = job_manager.initialize_user_job("integration_user", JobType.WARRIOR)
        assert user_data.current_job == JobType.WARRIOR
        
        # 2. ?
        for _ in range(3):
            job_manager.add_job_experience("integration_user", 100)
        
        job_info = job_manager.get_user_job_info("integration_user")
        assert job_info["current_job"]["level"] == 3
        
        # 3. ?
        success = job_manager.change_job("integration_user", JobType.MAGE, {})
        assert success
        
        # 4. ?
        job_info = job_manager.get_user_job_info("integration_user")
        assert job_info["current_job"]["type"] == "mage"
        assert job_info["current_job"]["level"] == 1  # ?1か
        assert job_info["current_job"]["focus_attribute"] == "Creativity"
        
        # 5. ?
        assert len(job_info["job_change_history"]) == 2
        assert job_info["job_change_history"][0]["reason"] == "initial_selection"
        assert job_info["job_change_history"][1]["from_job"] == "warrior"
        assert job_info["job_change_history"][1]["to_job"] == "mage"
    
    def test_advanced_job_unlock_workflow(self):
        """?"""
        job_manager = create_job_manager()
        
        # ユーザー
        job_manager.initialize_user_job("advanced_user", JobType.WARRIOR)
        
        # ?
        user_stats = {
            "warrior": 10,
            "priest": 5,
            "social_tasks": 50
        }
        
        # ?
        success = job_manager.change_job("advanced_user", JobType.PALADIN, user_stats)
        assert success
        
        # ?
        job_info = job_manager.get_user_job_info("advanced_user")
        assert job_info["current_job"]["type"] == "paladin"
        assert job_info["current_job"]["name"] == "?"
        assert job_info["stat_bonuses"]["resilience"] == 3
        assert job_info["stat_bonuses"]["social"] == 2
        assert job_info["stat_bonuses"]["motivation"] == 1


if __name__ == "__main__":
    # ?
    pytest.main([__file__, "-v"])