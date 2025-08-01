"""
? - メイン

6つ
?
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class JobType(Enum):
    """?"""
    WARRIOR = "warrior"      # ?
    HERO = "hero"           # 勇
    MAGE = "mage"           # ?
    PRIEST = "priest"       # ?
    SAGE = "sage"           # ?
    NINJA = "ninja"         # ?
    
    # ?
    PALADIN = "paladin"         # ?
    ARCHMAGE = "archmage"       # ?
    SHADOW_MASTER = "shadow_master"  # ?


@dataclass
class JobSkill:
    """?"""
    skill_id: str
    name: str
    description: str
    effect_type: str  # "stat_bonus", "task_efficiency", "special_ability"
    effect_value: float
    unlock_level: int = 1


@dataclass
class Job:
    """?"""
    job_type: JobType
    name: str
    focus_attribute: str  # ?
    stat_bonuses: Dict[str, int]
    skills: List[JobSkill]
    therapeutic_focus: str
    description: str
    is_advanced: bool = False
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)


class JobSystem:
    """基本"""
    
    def __init__(self):
        self.base_jobs = self._initialize_base_jobs()
        self.advanced_jobs = self._initialize_advanced_jobs()
        self.all_jobs = {**self.base_jobs, **self.advanced_jobs}
    
    def _initialize_base_jobs(self) -> Dict[JobType, Job]:
        """6つ"""
        
        # ?
        warrior_skills = [
            JobSkill("iron_will", "?", "?+20%", "task_efficiency", 0.2, 1),
            JobSkill("task_crusher", "タスク", "?XP+15%", "stat_bonus", 0.15, 3),
            JobSkill("deadline_guardian", "?", "?24?+30%", "special_ability", 0.3, 5)
        ]
        
        # 勇
        hero_skills = [
            JobSkill("fear_conqueror", "?", "?-25%", "special_ability", 0.25, 1),
            JobSkill("social_bridge", "?", "?XP+20%", "stat_bonus", 0.2, 3),
            JobSkill("hope_bringer", "希", "?+10%", "special_ability", 0.1, 5)
        ]
        
        # ?
        mage_skills = [
            JobSkill("idea_spark", "アプリ", "創+25%", "task_efficiency", 0.25, 1),
            JobSkill("problem_solver", "?", "?+20%", "stat_bonus", 0.2, 3),
            JobSkill("innovation_master", "?", "?XP?+30%", "special_ability", 0.3, 5)
        ]
        
        # ?
        priest_skills = [
            JobSkill("emotional_heal", "?", "ストーリー+30%", "special_ability", 0.3, 1),
            JobSkill("empathy_boost", "共有", "?+25%", "task_efficiency", 0.25, 3),
            JobSkill("community_bond", "コア", "?XP+20%", "stat_bonus", 0.2, 5)
        ]
        
        # ?
        sage_skills = [
            JobSkill("deep_insight", "?", "学+30%", "task_efficiency", 0.3, 1),
            JobSkill("learning_accelerator", "学", "ストーリーXP+25%", "stat_bonus", 0.25, 3),
            JobSkill("mindful_awareness", "?", "自動+35%", "special_ability", 0.35, 5)
        ]
        
        # ?
        ninja_skills = [
            JobSkill("stress_shadow", "ストーリー", "?+20%", "special_ability", 0.2, 1),
            JobSkill("adaptation_master", "?", "?+25%", "task_efficiency", 0.25, 3),
            JobSkill("stealth_progress", "ストーリー", "?+30%", "stat_bonus", 0.3, 5)
        ]
        
        return {
            JobType.WARRIOR: Job(
                job_type=JobType.WARRIOR,
                name="?",
                focus_attribute="Self-Discipline",
                stat_bonuses={"resilience": 2, "focus": 1},
                skills=warrior_skills,
                therapeutic_focus="?",
                description="?"
            ),
            JobType.HERO: Job(
                job_type=JobType.HERO,
                name="勇",
                focus_attribute="Courage",
                stat_bonuses={"motivation": 2, "social": 1},
                skills=hero_skills,
                therapeutic_focus="?",
                description="?"
            ),
            JobType.MAGE: Job(
                job_type=JobType.MAGE,
                name="?",
                focus_attribute="Creativity",
                stat_bonuses={"creativity": 2, "wisdom": 1},
                skills=mage_skills,
                therapeutic_focus="創",
                description="?"
            ),
            JobType.PRIEST: Job(
                job_type=JobType.PRIEST,
                name="?",
                focus_attribute="Empathy",
                stat_bonuses={"social": 2, "resilience": 1},
                skills=priest_skills,
                therapeutic_focus="共有",
                description="?"
            ),
            JobType.SAGE: Job(
                job_type=JobType.SAGE,
                name="?",
                focus_attribute="Wisdom",
                stat_bonuses={"wisdom": 2, "focus": 1},
                skills=sage_skills,
                therapeutic_focus="学",
                description="?"
            ),
            JobType.NINJA: Job(
                job_type=JobType.NINJA,
                name="?",
                focus_attribute="Resilience",
                stat_bonuses={"resilience": 2, "motivation": 1},
                skills=ninja_skills,
                therapeutic_focus="ストーリー",
                description="?"
            )
        }
    
    def _initialize_advanced_jobs(self) -> Dict[JobType, Job]:
        """?"""
        
        # ?
        paladin_skills = [
            JobSkill("divine_protection", "?", "?-20%", "special_ability", 0.2, 1),
            JobSkill("righteous_fury", "?", "?+40%", "task_efficiency", 0.4, 3),
            JobSkill("healing_light", "?", "自動+35%", "stat_bonus", 0.35, 5)
        ]
        
        # ?
        archmage_skills = [
            JobSkill("reality_shaper", "?", "創+50%", "special_ability", 0.5, 1),
            JobSkill("wisdom_amplifier", "?", "学+45%", "task_efficiency", 0.45, 3),
            JobSkill("innovation_storm", "?", "?XP?+60%", "stat_bonus", 0.6, 5)
        ]
        
        # ?
        shadow_master_skills = [
            JobSkill("shadow_step", "?", "?+40%", "special_ability", 0.4, 1),
            JobSkill("stress_immunity", "ストーリー", "?+50%", "task_efficiency", 0.5, 3),
            JobSkill("perfect_adaptation", "?", "あ+45%", "stat_bonus", 0.45, 5)
        ]
        
        return {
            JobType.PALADIN: Job(
                job_type=JobType.PALADIN,
                name="?",
                focus_attribute="Courage + Empathy",
                stat_bonuses={"resilience": 3, "social": 2, "motivation": 1},
                skills=paladin_skills,
                therapeutic_focus="リスト",
                description="?",
                is_advanced=True,
                unlock_requirements={"warrior": 10, "priest": 5, "social_tasks": 50}
            ),
            JobType.ARCHMAGE: Job(
                job_type=JobType.ARCHMAGE,
                name="?",
                focus_attribute="Creativity + Wisdom",
                stat_bonuses={"creativity": 4, "wisdom": 3},
                skills=archmage_skills,
                therapeutic_focus="?",
                description="?",
                is_advanced=True,
                unlock_requirements={"mage": 15, "wisdom": 20, "creative_tasks": 100}
            ),
            JobType.SHADOW_MASTER: Job(
                job_type=JobType.SHADOW_MASTER,
                name="?",
                focus_attribute="Resilience + Adaptation",
                stat_bonuses={"resilience": 4, "focus": 2},
                skills=shadow_master_skills,
                therapeutic_focus="?",
                description="?",
                is_advanced=True,
                unlock_requirements={"ninja": 12, "resilience": 25, "stress_overcome": 30}
            )
        }
    
    def get_job(self, job_type: JobType) -> Optional[Job]:
        """?"""
        return self.all_jobs.get(job_type)
    
    def get_base_jobs(self) -> List[Job]:
        """基本"""
        return list(self.base_jobs.values())
    
    def get_advanced_jobs(self) -> List[Job]:
        """?"""
        return list(self.advanced_jobs.values())
    
    def check_job_unlock(self, user_stats: Dict[str, Any], target_job: JobType) -> bool:
        """?"""
        job = self.all_jobs.get(target_job)
        if not job or not job.is_advanced:
            return True  # 基本
        
        requirements = job.unlock_requirements
        for req_key, req_value in requirements.items():
            if user_stats.get(req_key, 0) < req_value:
                return False
        return True
    
    def get_unlocked_jobs(self, user_stats: Dict[str, Any]) -> List[Job]:
        """ユーザー"""
        unlocked = []
        for job in self.all_jobs.values():
            if self.check_job_unlock(user_stats, job.job_type):
                unlocked.append(job)
        return unlocked
    
    def calculate_stat_bonuses(self, job_type: JobType, job_level: int = 1) -> Dict[str, int]:
        """?"""
        job = self.all_jobs.get(job_type)
        if not job:
            return {}
        
        # レベル
        level_multiplier = 1.0 + (job_level - 1) * 0.1  # レベル10%?
        
        bonuses = {}
        for stat, base_bonus in job.stat_bonuses.items():
            bonuses[stat] = int(base_bonus * level_multiplier)
        
        return bonuses
    
    def get_available_skills(self, job_type: JobType, job_level: int) -> List[JobSkill]:
        """?"""
        job = self.all_jobs.get(job_type)
        if not job:
            return []
        
        return [skill for skill in job.skills if skill.unlock_level <= job_level]
    
    def calculate_task_efficiency_bonus(self, job_type: JobType, job_level: int, 
                                      task_type: str) -> float:
        """タスク"""
        available_skills = self.get_available_skills(job_type, job_level)
        
        total_bonus = 0.0
        for skill in available_skills:
            if skill.effect_type == "task_efficiency":
                # ストーリー
                if self._skill_applies_to_task(skill, task_type):
                    total_bonus += skill.effect_value
        
        return total_bonus
    
    def _skill_applies_to_task(self, skill: JobSkill, task_type: str) -> bool:
        """ストーリー"""
        # ?
        skill_task_mapping = {
            "iron_will": ["routine", "difficult"],
            "task_crusher": ["routine"],
            "fear_conqueror": ["social"],
            "social_bridge": ["social"],
            "idea_spark": ["creative", "skill_up"],
            "problem_solver": ["skill_up", "complex"],
            "emotional_heal": ["stress_related"],
            "empathy_boost": ["social", "communication"],
            "deep_insight": ["learning", "skill_up"],
            "learning_accelerator": ["skill_up"],
            "stress_shadow": ["high_stress"],
            "adaptation_master": ["change_related"]
        }
        
        applicable_tasks = skill_task_mapping.get(skill.skill_id, [])
        return task_type in applicable_tasks or task_type == "all"


@dataclass
class UserJobData:
    """ユーザー"""
    uid: str
    current_job: JobType
    job_level: int = 1
    job_experience: int = 0
    unlocked_jobs: List[JobType] = field(default_factory=list)
    job_change_history: List[Dict[str, Any]] = field(default_factory=list)
    last_job_change: Optional[datetime] = None


class JobManager:
    """?"""
    
    def __init__(self):
        self.job_system = JobSystem()
        self.user_jobs: Dict[str, UserJobData] = {}
    
    def initialize_user_job(self, uid: str, starting_job: JobType = JobType.WARRIOR) -> UserJobData:
        """ユーザー"""
        user_job_data = UserJobData(
            uid=uid,
            current_job=starting_job,
            job_level=1,
            job_experience=0,
            unlocked_jobs=[job_type for job_type in JobType if not self.job_system.all_jobs[job_type].is_advanced],
            job_change_history=[{
                "job": starting_job.value,
                "timestamp": datetime.now().isoformat(),
                "reason": "initial_selection"
            }]
        )
        
        self.user_jobs[uid] = user_job_data
        return user_job_data
    
    def change_job(self, uid: str, new_job: JobType, user_stats: Dict[str, Any]) -> bool:
        """?"""
        if uid not in self.user_jobs:
            return False
        
        # アプリ
        if not self.job_system.check_job_unlock(user_stats, new_job):
            return False
        
        user_job_data = self.user_jobs[uid]
        old_job = user_job_data.current_job
        
        # ?
        user_job_data.current_job = new_job
        user_job_data.job_level = 1  # ?1か
        user_job_data.job_experience = 0
        user_job_data.last_job_change = datetime.now()
        
        # ?
        user_job_data.job_change_history.append({
            "from_job": old_job.value,
            "to_job": new_job.value,
            "timestamp": datetime.now().isoformat(),
            "reason": "user_choice"
        })
        
        # アプリ
        if new_job not in user_job_data.unlocked_jobs:
            user_job_data.unlocked_jobs.append(new_job)
        
        return True
    
    def add_job_experience(self, uid: str, experience: int) -> bool:
        """?"""
        if uid not in self.user_jobs:
            return False
        
        user_job_data = self.user_jobs[uid]
        user_job_data.job_experience += experience
        
        # レベル
        required_exp = self._calculate_required_experience(user_job_data.job_level)
        if user_job_data.job_experience >= required_exp:
            user_job_data.job_level += 1
            user_job_data.job_experience -= required_exp
            return True  # レベル
        
        return False
    
    def _calculate_required_experience(self, current_level: int) -> int:
        """?"""
        return current_level * 100  # レベル100の
    
    def get_user_job_info(self, uid: str) -> Optional[Dict[str, Any]]:
        """ユーザー"""
        if uid not in self.user_jobs:
            return None
        
        user_job_data = self.user_jobs[uid]
        current_job = self.job_system.get_job(user_job_data.current_job)
        
        if not current_job:
            return None
        
        return {
            "uid": uid,
            "current_job": {
                "type": current_job.job_type.value,
                "name": current_job.name,
                "level": user_job_data.job_level,
                "experience": user_job_data.job_experience,
                "required_exp": self._calculate_required_experience(user_job_data.job_level),
                "focus_attribute": current_job.focus_attribute,
                "therapeutic_focus": current_job.therapeutic_focus,
                "description": current_job.description
            },
            "stat_bonuses": self.job_system.calculate_stat_bonuses(
                user_job_data.current_job, user_job_data.job_level
            ),
            "available_skills": [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "effect_type": skill.effect_type,
                    "effect_value": skill.effect_value
                }
                for skill in self.job_system.get_available_skills(
                    user_job_data.current_job, user_job_data.job_level
                )
            ],
            "unlocked_jobs": [job_type.value for job_type in user_job_data.unlocked_jobs],
            "job_change_history": user_job_data.job_change_history[-5:]  # ?5?
        }


# API エラー
def create_job_manager() -> JobManager:
    """JobManager?"""
    return JobManager()


if __name__ == "__main__":
    # 基本
    job_manager = create_job_manager()
    
    # ユーザー
    user_data = job_manager.initialize_user_job("test_user", JobType.WARRIOR)
    print(f"?: {user_data.current_job.value}")
    
    # ?
    job_info = job_manager.get_user_job_info("test_user")
    print(f"?: {json.dumps(job_info, indent=2, ensure_ascii=False)}")
    
    # ?
    leveled_up = job_manager.add_job_experience("test_user", 150)
    print(f"レベル: {leveled_up}")
    
    # ?
    updated_info = job_manager.get_user_job_info("test_user")
    print(f"?: {updated_info['current_job']['level']}")