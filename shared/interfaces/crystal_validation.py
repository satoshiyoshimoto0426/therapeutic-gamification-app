"""
8?
?
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .core_types import (
    CrystalAttribute, CrystalGrowthEvent, CrystalState,
    CrystalGrowthRecord, UserCrystalSystem, CrystalMilestone,
    CrystalSynergy
)

class CrystalValidator:
    """?"""
    
    # 成
    MAX_GROWTH_PER_EVENT = 20
    MIN_GROWTH_PER_EVENT = 1
    
    # 共有
    RESONANCE_THRESHOLDS = [0, 200, 500, 1000, 1800, 2800, 4000, 5500, 7200]
    
    @staticmethod
    def validate_growth_amount(growth_amount: int) -> bool:
        """成"""
        return (CrystalValidator.MIN_GROWTH_PER_EVENT <= 
                growth_amount <= 
                CrystalValidator.MAX_GROWTH_PER_EVENT)
    
    @staticmethod
    def validate_crystal_value(value: int) -> bool:
        """?0-100の"""
        return 0 <= value <= 100
    
    @staticmethod
    def calculate_growth_with_rate(base_growth: int, growth_rate: float) -> int:
        """成"""
        if not CrystalValidator.validate_growth_amount(base_growth):
            raise ValueError(f"Invalid growth amount: {base_growth}")
        
        if growth_rate < 0.5 or growth_rate > 2.0:
            raise ValueError(f"Invalid growth rate: {growth_rate}")
        
        calculated_growth = int(base_growth * growth_rate)
        return max(1, min(calculated_growth, CrystalValidator.MAX_GROWTH_PER_EVENT))
    
    @staticmethod
    def apply_growth_to_crystal(
        crystal: CrystalState, 
        growth_amount: int,
        event_time: datetime
    ) -> Tuple[CrystalState, bool]:
        """
        ?
        Returns: (?, ?)
        """
        if not CrystalValidator.validate_growth_amount(growth_amount):
            raise ValueError(f"Invalid growth amount: {growth_amount}")
        
        old_value = crystal.current_value
        actual_growth = CrystalValidator.calculate_growth_with_rate(
            growth_amount, crystal.growth_rate
        )
        
        new_value = min(100, old_value + actual_growth)
        milestone_reached = CrystalValidator.check_milestone_reached(old_value, new_value)
        
        # ?
        crystal.current_value = new_value
        crystal.last_growth_event = event_time
        
        return crystal, milestone_reached
    
    @staticmethod
    def check_milestone_reached(old_value: int, new_value: int) -> bool:
        """?25, 50, 75, 100の"""
        milestones = [25, 50, 75, 100]
        
        for milestone in milestones:
            if old_value < milestone <= new_value:
                return True
        return False
    
    @staticmethod
    def get_milestone_for_value(value: int) -> Optional[int]:
        """?"""
        milestones = [25, 50, 75, 100]
        
        for milestone in reversed(milestones):
            if value >= milestone:
                return milestone
        return None
    
    @staticmethod
    def calculate_resonance_level(crystal_system: UserCrystalSystem) -> int:
        """
        ?
        ?
        """
        total_crystal_value = sum(
            crystal.current_value for crystal in crystal_system.crystals.values()
        )
        
        for level, threshold in enumerate(CrystalValidator.RESONANCE_THRESHOLDS):
            if total_crystal_value < threshold:
                return max(0, level - 1)
        
        return len(CrystalValidator.RESONANCE_THRESHOLDS) - 1
    
    @staticmethod
    def check_synergy_requirements(
        crystal_system: UserCrystalSystem,
        synergy: CrystalSynergy
    ) -> bool:
        """システム"""
        for attribute in synergy.required_attributes:
            if attribute not in crystal_system.crystals:
                return False
            
            required_level = synergy.min_levels.get(attribute, 0)
            current_level = crystal_system.crystals[attribute].current_value
            
            if current_level < required_level:
                return False
        
        return True
    
    @staticmethod
    def get_available_synergies(
        crystal_system: UserCrystalSystem,
        all_synergies: List[CrystalSynergy]
    ) -> List[CrystalSynergy]:
        """?"""
        available = []
        
        for synergy in all_synergies:
            if CrystalValidator.check_synergy_requirements(crystal_system, synergy):
                available.append(synergy)
        
        return available
    
    @staticmethod
    def calculate_harmony_bonus(crystal_system: UserCrystalSystem) -> float:
        """
        ?
        ?
        """
        crystal_values = [
            crystal.current_value for crystal in crystal_system.crystals.values()
        ]
        
        if not crystal_values:
            return 0.0
        
        # ?
        mean_value = sum(crystal_values) / len(crystal_values)
        variance = sum((value - mean_value) ** 2 for value in crystal_values) / len(crystal_values)
        std_deviation = variance ** 0.5
        
        # ?1.5?
        max_std = 50  # ?
        harmony_ratio = max(0, (max_std - std_deviation) / max_std)
        
        return 1.0 + (harmony_ratio * 0.5)
    
    @staticmethod
    def validate_crystal_system_integrity(crystal_system: UserCrystalSystem) -> List[str]:
        """?"""
        errors = []
        
        # ?
        expected_attributes = set(CrystalAttribute)
        actual_attributes = set(crystal_system.crystals.keys())
        
        missing_attributes = expected_attributes - actual_attributes
        if missing_attributes:
            errors.append(f"Missing crystal attributes: {missing_attributes}")
        
        # ?
        for attribute, crystal in crystal_system.crystals.items():
            if not CrystalValidator.validate_crystal_value(crystal.current_value):
                errors.append(f"Invalid crystal value for {attribute}: {crystal.current_value}")
            
            if crystal.growth_rate < 0.5 or crystal.growth_rate > 2.0:
                errors.append(f"Invalid growth rate for {attribute}: {crystal.growth_rate}")
        
        # 共有
        calculated_resonance = CrystalValidator.calculate_resonance_level(crystal_system)
        if crystal_system.resonance_level != calculated_resonance:
            errors.append(
                f"Resonance level mismatch: stored={crystal_system.resonance_level}, "
                f"calculated={calculated_resonance}"
            )
        
        return errors

class CrystalGrowthCalculator:
    """?"""
    
    # ?
    BASE_GROWTH_BY_EVENT = {
        CrystalGrowthEvent.TASK_COMPLETION: 5,
        CrystalGrowthEvent.STORY_CHOICE: 3,
        CrystalGrowthEvent.MOOD_IMPROVEMENT: 4,
        CrystalGrowthEvent.REFLECTION_ENTRY: 6,
        CrystalGrowthEvent.SOCIAL_INTERACTION: 4,
        CrystalGrowthEvent.CREATIVE_ACTIVITY: 5,
        CrystalGrowthEvent.CHALLENGE_OVERCOME: 8,
        CrystalGrowthEvent.WISDOM_GAINED: 7
    }
    
    # ?
    ATTRIBUTE_EVENT_MULTIPLIERS = {
        CrystalAttribute.SELF_DISCIPLINE: {
            CrystalGrowthEvent.TASK_COMPLETION: 1.5,
            CrystalGrowthEvent.CHALLENGE_OVERCOME: 1.3,
            CrystalGrowthEvent.REFLECTION_ENTRY: 1.2
        },
        CrystalAttribute.EMPATHY: {
            CrystalGrowthEvent.SOCIAL_INTERACTION: 1.5,
            CrystalGrowthEvent.STORY_CHOICE: 1.3,
            CrystalGrowthEvent.MOOD_IMPROVEMENT: 1.2
        },
        CrystalAttribute.RESILIENCE: {
            CrystalGrowthEvent.CHALLENGE_OVERCOME: 1.5,
            CrystalGrowthEvent.MOOD_IMPROVEMENT: 1.3,
            CrystalGrowthEvent.TASK_COMPLETION: 1.2
        },
        CrystalAttribute.CURIOSITY: {
            CrystalGrowthEvent.STORY_CHOICE: 1.5,
            CrystalGrowthEvent.CREATIVE_ACTIVITY: 1.3,
            CrystalGrowthEvent.WISDOM_GAINED: 1.2
        },
        CrystalAttribute.COMMUNICATION: {
            CrystalGrowthEvent.SOCIAL_INTERACTION: 1.5,
            CrystalGrowthEvent.REFLECTION_ENTRY: 1.3,
            CrystalGrowthEvent.STORY_CHOICE: 1.2
        },
        CrystalAttribute.CREATIVITY: {
            CrystalGrowthEvent.CREATIVE_ACTIVITY: 1.5,
            CrystalGrowthEvent.STORY_CHOICE: 1.3,
            CrystalGrowthEvent.CHALLENGE_OVERCOME: 1.2
        },
        CrystalAttribute.COURAGE: {
            CrystalGrowthEvent.CHALLENGE_OVERCOME: 1.5,
            CrystalGrowthEvent.TASK_COMPLETION: 1.3,
            CrystalGrowthEvent.SOCIAL_INTERACTION: 1.2
        },
        CrystalAttribute.WISDOM: {
            CrystalGrowthEvent.WISDOM_GAINED: 1.5,
            CrystalGrowthEvent.REFLECTION_ENTRY: 1.3,
            CrystalGrowthEvent.CHALLENGE_OVERCOME: 1.2
        }
    }
    
    @staticmethod
    def calculate_growth_amount(
        attribute: CrystalAttribute,
        event_type: CrystalGrowthEvent,
        base_multiplier: float = 1.0
    ) -> int:
        """?"""
        base_growth = CrystalGrowthCalculator.BASE_GROWTH_BY_EVENT.get(event_type, 3)
        
        # ?
        attribute_multipliers = CrystalGrowthCalculator.ATTRIBUTE_EVENT_MULTIPLIERS.get(
            attribute, {}
        )
        event_multiplier = attribute_multipliers.get(event_type, 1.0)
        
        # ?
        final_growth = int(base_growth * event_multiplier * base_multiplier)
        
        # ?
        return max(
            CrystalValidator.MIN_GROWTH_PER_EVENT,
            min(final_growth, CrystalValidator.MAX_GROWTH_PER_EVENT)
        )
    
    @staticmethod
    def get_therapeutic_message(
        attribute: CrystalAttribute,
        event_type: CrystalGrowthEvent,
        growth_amount: int
    ) -> str:
        """成"""
        attribute_messages = {
            CrystalAttribute.SELF_DISCIPLINE: {
                "low": "自動",
                "medium": "自動",
                "high": "?"
            },
            CrystalAttribute.EMPATHY: {
                "low": "?",
                "medium": "共有",
                "high": "?"
            },
            CrystalAttribute.RESILIENCE: {
                "low": "?",
                "medium": "?",
                "high": "?"
            },
            CrystalAttribute.CURIOSITY: {
                "low": "?",
                "medium": "?",
                "high": "?"
            },
            CrystalAttribute.COMMUNICATION: {
                "low": "コア",
                "medium": "表",
                "high": "?"
            },
            CrystalAttribute.CREATIVITY: {
                "low": "創",
                "medium": "創",
                "high": "?"
            },
            CrystalAttribute.COURAGE: {
                "low": "勇",
                "medium": "?",
                "high": "?"
            },
            CrystalAttribute.WISDOM: {
                "low": "?",
                "medium": "?",
                "high": "?"
            }
        }
        
        # 成
        if growth_amount <= 3:
            level = "low"
        elif growth_amount <= 7:
            level = "medium"
        else:
            level = "high"
        
        messages = attribute_messages.get(attribute, {})
        return messages.get(level, "成")