"""
モデル - 共有
?
"""

from typing import Dict, List, Optional
from datetime import datetime
from .core_types import (
    CrystalAttribute, CrystalState, UserCrystalSystem,
    CrystalMilestone, CrystalSynergy, UserProfile,
    GameState, ChapterType
)

class CrystalSystemFactory:
    """?"""
    
    @staticmethod
    def create_initial_crystal_system(uid: str) -> UserCrystalSystem:
        """?"""
        crystals = {}
        
        # ?
        for attribute in CrystalAttribute:
            crystals[attribute] = CrystalState(
                attribute=attribute,
                current_value=0,
                growth_rate=1.0,
                last_growth_event=None,
                milestone_rewards=[],
                therapeutic_insights=[]
            )
        
        return UserCrystalSystem(
            uid=uid,
            crystals=crystals,
            total_growth_events=0,
            resonance_level=0,
            last_resonance_check=None,
            active_synergies=[],
            growth_history=[]
        )
    
    @staticmethod
    def create_crystal_with_value(
        attribute: CrystalAttribute, 
        value: int,
        growth_rate: float = 1.0
    ) -> CrystalState:
        """?"""
        if not (0 <= value <= 100):
            raise ValueError(f"Crystal value must be between 0 and 100, got {value}")
        
        if not (0.5 <= growth_rate <= 2.0):
            raise ValueError(f"Growth rate must be between 0.5 and 2.0, got {growth_rate}")
        
        return CrystalState(
            attribute=attribute,
            current_value=value,
            growth_rate=growth_rate,
            last_growth_event=datetime.utcnow() if value > 0 else None,
            milestone_rewards=[],
            therapeutic_insights=[]
        )

class MilestoneFactory:
    """?"""
    
    # ?
    STANDARD_MILESTONES = {
        CrystalAttribute.SELF_DISCIPLINE: [
            {
                "threshold": 25,
                "title": "自動",
                "description": "自動",
                "rewards": ["discipline_badge", "focus_potion"],
                "therapeutic_benefit": "?",
                "unlock_content": ["discipline_story_1"]
            },
            {
                "threshold": 50,
                "title": "自動",
                "description": "?",
                "rewards": ["discipline_crystal", "time_management_skill"],
                "therapeutic_benefit": "計算",
                "unlock_content": ["discipline_story_2", "advanced_task_features"]
            },
            {
                "threshold": 75,
                "title": "自動",
                "description": "?",
                "rewards": ["master_discipline_item", "leadership_skill"],
                "therapeutic_benefit": "?",
                "unlock_content": ["discipline_story_3", "mentor_features"]
            },
            {
                "threshold": 100,
                "title": "自動",
                "description": "?",
                "rewards": ["legendary_discipline_crystal", "sage_wisdom"],
                "therapeutic_benefit": "?",
                "unlock_content": ["discipline_ending", "master_class_unlock"]
            }
        ],
        CrystalAttribute.EMPATHY: [
            {
                "threshold": 25,
                "title": "共有",
                "description": "?",
                "rewards": ["empathy_badge", "heart_potion"],
                "therapeutic_benefit": "?",
                "unlock_content": ["empathy_story_1"]
            },
            {
                "threshold": 50,
                "title": "共有",
                "description": "?",
                "rewards": ["empathy_crystal", "communication_skill"],
                "therapeutic_benefit": "?",
                "unlock_content": ["empathy_story_2", "social_features"]
            },
            {
                "threshold": 75,
                "title": "共有",
                "description": "?",
                "rewards": ["master_empathy_item", "healing_skill"],
                "therapeutic_benefit": "?",
                "unlock_content": ["empathy_story_3", "counselor_features"]
            },
            {
                "threshold": 100,
                "title": "共有",
                "description": "?",
                "rewards": ["legendary_empathy_crystal", "universal_love"],
                "therapeutic_benefit": "?",
                "unlock_content": ["empathy_ending", "healer_class_unlock"]
            }
        ]
        # ?...
    }
    
    @staticmethod
    def create_milestone(
        attribute: CrystalAttribute,
        threshold: int,
        title: str,
        description: str,
        rewards: List[str],
        therapeutic_benefit: str,
        unlock_content: List[str] = None
    ) -> CrystalMilestone:
        """カスタム"""
        return CrystalMilestone(
            attribute=attribute,
            threshold=threshold,
            title=title,
            description=description,
            rewards=rewards,
            therapeutic_benefit=therapeutic_benefit,
            unlock_content=unlock_content or []
        )
    
    @staticmethod
    def get_standard_milestones(attribute: CrystalAttribute) -> List[CrystalMilestone]:
        """?"""
        milestone_data = MilestoneFactory.STANDARD_MILESTONES.get(attribute, [])
        milestones = []
        
        for data in milestone_data:
            milestone = CrystalMilestone(
                attribute=attribute,
                threshold=data["threshold"],
                title=data["title"],
                description=data["description"],
                rewards=data["rewards"],
                therapeutic_benefit=data["therapeutic_benefit"],
                unlock_content=data["unlock_content"]
            )
            milestones.append(milestone)
        
        return milestones
    
    @staticmethod
    def get_all_standard_milestones() -> Dict[CrystalAttribute, List[CrystalMilestone]]:
        """?"""
        all_milestones = {}
        
        for attribute in CrystalAttribute:
            all_milestones[attribute] = MilestoneFactory.get_standard_milestones(attribute)
        
        return all_milestones

class SynergyFactory:
    """?"""
    
    # ?
    STANDARD_SYNERGIES = [
        {
            "synergy_id": "discipline_resilience",
            "name": "?",
            "required_attributes": [CrystalAttribute.SELF_DISCIPLINE, CrystalAttribute.RESILIENCE],
            "min_levels": {CrystalAttribute.SELF_DISCIPLINE: 30, CrystalAttribute.RESILIENCE: 30},
            "effect_description": "自動",
            "stat_bonuses": {"mental_strength": 10, "task_efficiency": 15},
            "therapeutic_benefit": "ストーリー",
            "story_unlock": "discipline_resilience_chapter"
        },
        {
            "synergy_id": "empathy_communication",
            "name": "?",
            "required_attributes": [CrystalAttribute.EMPATHY, CrystalAttribute.COMMUNICATION],
            "min_levels": {CrystalAttribute.EMPATHY: 25, CrystalAttribute.COMMUNICATION: 25},
            "effect_description": "共有",
            "stat_bonuses": {"social_connection": 20, "emotional_intelligence": 15},
            "therapeutic_benefit": "?",
            "story_unlock": "empathy_communication_chapter"
        },
        {
            "synergy_id": "curiosity_creativity",
            "name": "創",
            "required_attributes": [CrystalAttribute.CURIOSITY, CrystalAttribute.CREATIVITY],
            "min_levels": {CrystalAttribute.CURIOSITY: 35, CrystalAttribute.CREATIVITY: 35},
            "effect_description": "?",
            "stat_bonuses": {"innovation": 25, "problem_solving": 20},
            "therapeutic_benefit": "?",
            "story_unlock": "curiosity_creativity_chapter"
        },
        {
            "synergy_id": "courage_wisdom",
            "name": "?",
            "required_attributes": [CrystalAttribute.COURAGE, CrystalAttribute.WISDOM],
            "min_levels": {CrystalAttribute.COURAGE: 40, CrystalAttribute.WISDOM: 40},
            "effect_description": "勇",
            "stat_bonuses": {"leadership": 30, "decision_making": 25},
            "therapeutic_benefit": "?",
            "story_unlock": "courage_wisdom_chapter"
        }
    ]
    
    @staticmethod
    def create_synergy(
        synergy_id: str,
        name: str,
        required_attributes: List[CrystalAttribute],
        min_levels: Dict[CrystalAttribute, int],
        effect_description: str,
        stat_bonuses: Dict[str, int],
        therapeutic_benefit: str,
        story_unlock: Optional[str] = None
    ) -> CrystalSynergy:
        """カスタム"""
        return CrystalSynergy(
            synergy_id=synergy_id,
            name=name,
            required_attributes=required_attributes,
            min_levels=min_levels,
            effect_description=effect_description,
            stat_bonuses=stat_bonuses,
            therapeutic_benefit=therapeutic_benefit,
            story_unlock=story_unlock
        )
    
    @staticmethod
    def get_standard_synergies() -> List[CrystalSynergy]:
        """?"""
        synergies = []
        
        for data in SynergyFactory.STANDARD_SYNERGIES:
            synergy = CrystalSynergy(
                synergy_id=data["synergy_id"],
                name=data["name"],
                required_attributes=data["required_attributes"],
                min_levels=data["min_levels"],
                effect_description=data["effect_description"],
                stat_bonuses=data["stat_bonuses"],
                therapeutic_benefit=data["therapeutic_benefit"],
                story_unlock=data["story_unlock"]
            )
            synergies.append(synergy)
        
        return synergies

class GameStateFactory:
    """ゲーム"""
    
    @staticmethod
    def create_initial_game_state() -> GameState:
        """?"""
        return GameState(
            player_level=1,
            yu_level=1,
            current_chapter=ChapterType.SELF_DISCIPLINE,
            crystal_gauges={chapter: 0 for chapter in ChapterType},
            total_xp=0,
            last_resonance_event=None
        )
    
    @staticmethod
    def create_user_profile(
        uid: str,
        email: str,
        display_name: str,
        adhd_profile: Optional[Dict] = None,
        therapeutic_goals: Optional[List[str]] = None
    ) -> UserProfile:
        """?"""
        now = datetime.utcnow()
        
        return UserProfile(
            uid=uid,
            email=email,
            display_name=display_name,
            player_level=1,
            yu_level=1,
            total_xp=0,
            crystal_gauges={},  # __init__で
            current_chapter="self_discipline",
            daily_task_limit=16,
            care_points=0,
            guardian_permissions=[],
            adhd_profile=adhd_profile or {},
            therapeutic_goals=therapeutic_goals or [],
            created_at=now,
            last_active=now
        )