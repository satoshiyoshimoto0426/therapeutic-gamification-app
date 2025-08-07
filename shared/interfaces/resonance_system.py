"""
[UNICODE_5171]
Resonance event system for Player-Yu level synchronization
Requirements: 4.4, 4.5
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum

from .core_types import CrystalAttribute, CrystalGrowthEvent


class ResonanceType(str, Enum):
    """[UNICODE_5171]"""
    LEVEL_SYNC = "level_sync"           # [UNICODE_30EC]
    CRYSTAL_HARMONY = "crystal_harmony" # [UNICODE_30AF]
    EMOTIONAL_BOND = "emotional_bond"   # [UNICODE_611F]
    WISDOM_SHARING = "wisdom_sharing"   # [UNICODE_77E5]


class ResonanceIntensity(str, Enum):
    """[UNICODE_5171]"""
    WEAK = "weak"         # [UNICODE_5F31]5-7[UNICODE_FF09]
    MODERATE = "moderate" # [UNICODE_4E2D]8-12[UNICODE_FF09]
    STRONG = "strong"     # [UNICODE_5F37]13-20[UNICODE_FF09]
    INTENSE = "intense"   # [UNICODE_6FC0]21[UNICODE_4EE5]


class ResonanceEvent(BaseModel):
    """[UNICODE_5171]"""
    event_id: str
    resonance_type: ResonanceType
    intensity: ResonanceIntensity
    player_level: int
    yu_level: int
    level_difference: int
    bonus_xp: int
    crystal_bonuses: Dict[CrystalAttribute, int] = {}
    special_rewards: List[str] = []
    therapeutic_message: str
    story_unlock: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)


class ResonanceCondition(BaseModel):
    """[UNICODE_5171]"""
    min_level_difference: int = 5
    max_level_difference: int = 50
    cooldown_hours: int = 24  # [UNICODE_540C]
    player_min_level: int = 3  # [UNICODE_30D7]


class ResonanceCalculator:
    """[UNICODE_5171]"""
    
    # [UNICODE_5171]
    INTENSITY_MULTIPLIERS = {
        ResonanceIntensity.WEAK: 1.5,
        ResonanceIntensity.MODERATE: 2.0,
        ResonanceIntensity.STRONG: 3.0,
        ResonanceIntensity.INTENSE: 4.0
    }
    
    # [UNICODE_30EC]XP[UNICODE_30DC]
    BASE_BONUS_PER_LEVEL_DIFF = 50
    
    @staticmethod
    def calculate_resonance_intensity(level_difference: int) -> ResonanceIntensity:
        """[UNICODE_30EC]"""
        if level_difference >= 21:
            return ResonanceIntensity.INTENSE
        elif level_difference >= 13:
            return ResonanceIntensity.STRONG
        elif level_difference >= 8:
            return ResonanceIntensity.MODERATE
        else:
            return ResonanceIntensity.WEAK
    
    @staticmethod
    def calculate_bonus_xp(
        level_difference: int,
        player_level: int,
        resonance_type: ResonanceType
    ) -> int:
        """[UNICODE_30DC]XP[UNICODE_3092]"""
        # [UNICODE_57FA]
        base_bonus = level_difference * ResonanceCalculator.BASE_BONUS_PER_LEVEL_DIFF
        
        # [UNICODE_5F37]
        intensity = ResonanceCalculator.calculate_resonance_intensity(level_difference)
        intensity_multiplier = ResonanceCalculator.INTENSITY_MULTIPLIERS[intensity]
        
        # [UNICODE_30D7]
        level_multiplier = 1.0 + (player_level * 0.05)
        
        # [UNICODE_5171]
        type_multipliers = {
            ResonanceType.LEVEL_SYNC: 1.0,
            ResonanceType.CRYSTAL_HARMONY: 1.2,
            ResonanceType.EMOTIONAL_BOND: 0.8,
            ResonanceType.WISDOM_SHARING: 1.1
        }
        type_multiplier = type_multipliers.get(resonance_type, 1.0)
        
        # [UNICODE_6700]XP[UNICODE_8A08]
        final_bonus = int(
            base_bonus * 
            intensity_multiplier * 
            level_multiplier * 
            type_multiplier
        )
        
        return max(100, final_bonus)  # [UNICODE_6700]100XP[UNICODE_306F]
    
    @staticmethod
    def calculate_crystal_bonuses(
        resonance_type: ResonanceType,
        intensity: ResonanceIntensity,
        player_level: int
    ) -> Dict[CrystalAttribute, int]:
        """[UNICODE_30AF]"""
        bonuses = {}
        
        # [UNICODE_5F37]
        base_bonus = {
            ResonanceIntensity.WEAK: 5,
            ResonanceIntensity.MODERATE: 8,
            ResonanceIntensity.STRONG: 12,
            ResonanceIntensity.INTENSE: 18
        }[intensity]
        
        # [UNICODE_5171]
        if resonance_type == ResonanceType.LEVEL_SYNC:
            # [UNICODE_30D0]
            for attr in CrystalAttribute:
                bonuses[attr] = base_bonus // 2
        
        elif resonance_type == ResonanceType.CRYSTAL_HARMONY:
            # [UNICODE_8ABF]
            bonuses[CrystalAttribute.WISDOM] = base_bonus
            bonuses[CrystalAttribute.EMPATHY] = base_bonus
            bonuses[CrystalAttribute.RESILIENCE] = base_bonus // 2
        
        elif resonance_type == ResonanceType.EMOTIONAL_BOND:
            # [UNICODE_611F]
            bonuses[CrystalAttribute.EMPATHY] = base_bonus
            bonuses[CrystalAttribute.COMMUNICATION] = base_bonus
            bonuses[CrystalAttribute.COURAGE] = base_bonus // 2
        
        elif resonance_type == ResonanceType.WISDOM_SHARING:
            # [UNICODE_77E5]
            bonuses[CrystalAttribute.WISDOM] = base_bonus
            bonuses[CrystalAttribute.CURIOSITY] = base_bonus
            bonuses[CrystalAttribute.CREATIVITY] = base_bonus // 2
        
        return bonuses
    
    @staticmethod
    def generate_therapeutic_message(
        resonance_type: ResonanceType,
        intensity: ResonanceIntensity,
        player_level: int,
        yu_level: int
    ) -> str:
        """[UNICODE_6CBB]"""
        intensity_descriptions = {
            ResonanceIntensity.WEAK: "[UNICODE_7A4F]",
            ResonanceIntensity.MODERATE: "[UNICODE_5FC3]",
            ResonanceIntensity.STRONG: "[UNICODE_529B]",
            ResonanceIntensity.INTENSE: "[UNICODE_6DF1]"
        }
        
        intensity_desc = intensity_descriptions[intensity]
        
        messages = {
            ResonanceType.LEVEL_SYNC: [
                f"[UNICODE_3042]{intensity_desc}[UNICODE_5171]",
                f"[UNICODE_30EC]{player_level}[UNICODE_306E]{yu_level}[UNICODE_306E]{intensity_desc}[UNICODE_7D46]",
                f"{intensity_desc}[UNICODE_5171]"
            ],
            ResonanceType.CRYSTAL_HARMONY: [
                f"[UNICODE_30AF]{intensity_desc}[UNICODE_8ABF]",
                f"8[UNICODE_3064]{intensity_desc}[UNICODE_5149]",
                f"{intensity_desc}[UNICODE_30AF]"
            ],
            ResonanceType.EMOTIONAL_BOND: [
                f"[UNICODE_3042]{intensity_desc}[UNICODE_611F]",
                f"{intensity_desc}[UNICODE_611F]",
                f"[UNICODE_5FC3]{intensity_desc}[UNICODE_7D46]"
            ],
            ResonanceType.WISDOM_SHARING: [
                f"[UNICODE_30E6]{intensity_desc}[UNICODE_5171]",
                f"{intensity_desc}[UNICODE_77E5]",
                f"[UNICODE_3042]{intensity_desc}[UNICODE_77E5]"
            ]
        }
        
        type_messages = messages.get(resonance_type, messages[ResonanceType.LEVEL_SYNC])
        return random.choice(type_messages)


class ResonanceEventManager:
    """[UNICODE_5171]"""
    
    def __init__(self):
        self.conditions = ResonanceCondition()
        self.event_history: List[ResonanceEvent] = []
        self.last_event_times: Dict[ResonanceType, datetime] = {}
    
    def check_resonance_conditions(
        self,
        player_level: int,
        yu_level: int,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[ResonanceType]]:
        """[UNICODE_5171]"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        # [UNICODE_57FA]
        level_difference = abs(player_level - yu_level)
        
        if level_difference < self.conditions.min_level_difference:
            return False, None
        
        if level_difference > self.conditions.max_level_difference:
            return False, None
        
        if player_level < self.conditions.player_min_level:
            return False, None
        
        # [UNICODE_30AF]
        available_types = []
        for resonance_type in ResonanceType:
            last_event_time = self.last_event_times.get(resonance_type)
            if last_event_time is None:
                available_types.append(resonance_type)
            else:
                time_since_last = current_time - last_event_time
                if time_since_last.total_seconds() >= self.conditions.cooldown_hours * 3600:
                    available_types.append(resonance_type)
        
        if not available_types:
            return False, None
        
        # [UNICODE_5171]
        selected_type = self._select_resonance_type(
            level_difference, player_level, yu_level, available_types
        )
        
        return True, selected_type
    
    def _select_resonance_type(
        self,
        level_difference: int,
        player_level: int,
        yu_level: int,
        available_types: List[ResonanceType]
    ) -> ResonanceType:
        """[UNICODE_72B6]"""
        # [UNICODE_30EC]
        type_weights = {}
        
        for resonance_type in available_types:
            if resonance_type == ResonanceType.LEVEL_SYNC:
                # [UNICODE_30EC]
                type_weights[resonance_type] = level_difference * 2
            
            elif resonance_type == ResonanceType.CRYSTAL_HARMONY:
                # [UNICODE_4E2D]
                optimal_diff = 10
                weight = max(1, optimal_diff - abs(level_difference - optimal_diff))
                type_weights[resonance_type] = weight * 1.5
            
            elif resonance_type == ResonanceType.EMOTIONAL_BOND:
                # [UNICODE_30D7]
                type_weights[resonance_type] = player_level * 0.5
            
            elif resonance_type == ResonanceType.WISDOM_SHARING:
                # [UNICODE_30E6]
                type_weights[resonance_type] = yu_level * 0.8
        
        # [UNICODE_91CD]
        total_weight = sum(type_weights.values())
        if total_weight == 0:
            return random.choice(available_types)
        
        rand_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for resonance_type, weight in type_weights.items():
            cumulative_weight += weight
            if rand_value <= cumulative_weight:
                return resonance_type
        
        return available_types[0]  # [UNICODE_30D5]
    
    def trigger_resonance_event(
        self,
        player_level: int,
        yu_level: int,
        resonance_type: ResonanceType,
        current_time: Optional[datetime] = None
    ) -> ResonanceEvent:
        """[UNICODE_5171]"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        level_difference = abs(player_level - yu_level)
        intensity = ResonanceCalculator.calculate_resonance_intensity(level_difference)
        
        # [UNICODE_30DC]XP[UNICODE_8A08]
        bonus_xp = ResonanceCalculator.calculate_bonus_xp(
            level_difference, player_level, resonance_type
        )
        
        # [UNICODE_30AF]
        crystal_bonuses = ResonanceCalculator.calculate_crystal_bonuses(
            resonance_type, intensity, player_level
        )
        
        # [UNICODE_7279]
        special_rewards = self._generate_special_rewards(intensity, resonance_type)
        
        # [UNICODE_6CBB]
        therapeutic_message = ResonanceCalculator.generate_therapeutic_message(
            resonance_type, intensity, player_level, yu_level
        )
        
        # [UNICODE_30B9]
        story_unlock = self._check_story_unlock(intensity, resonance_type, player_level)
        
        # [UNICODE_30A4]
        event = ResonanceEvent(
            event_id=f"resonance_{current_time.strftime('%Y%m%d_%H%M%S')}_{resonance_type.value}",
            resonance_type=resonance_type,
            intensity=intensity,
            player_level=player_level,
            yu_level=yu_level,
            level_difference=level_difference,
            bonus_xp=bonus_xp,
            crystal_bonuses=crystal_bonuses,
            special_rewards=special_rewards,
            therapeutic_message=therapeutic_message,
            story_unlock=story_unlock,
            triggered_at=current_time
        )
        
        # [UNICODE_30A4]
        self.event_history.append(event)
        self.last_event_times[resonance_type] = current_time
        
        return event
    
    def _generate_special_rewards(
        self,
        intensity: ResonanceIntensity,
        resonance_type: ResonanceType
    ) -> List[str]:
        """[UNICODE_7279]"""
        rewards = []
        
        # [UNICODE_5F37]
        if intensity == ResonanceIntensity.WEAK:
            rewards.append("resonance_crystal_fragment")
        elif intensity == ResonanceIntensity.MODERATE:
            rewards.extend(["resonance_crystal_fragment", "harmony_potion"])
        elif intensity == ResonanceIntensity.STRONG:
            rewards.extend(["resonance_crystal", "harmony_elixir", "bond_strengthener"])
        elif intensity == ResonanceIntensity.INTENSE:
            rewards.extend([
                "legendary_resonance_crystal", "ultimate_harmony_elixir",
                "eternal_bond_seal", "wisdom_of_ages"
            ])
        
        # [UNICODE_30BF]
        type_rewards = {
            ResonanceType.LEVEL_SYNC: ["sync_amplifier", "level_harmony_badge"],
            ResonanceType.CRYSTAL_HARMONY: ["crystal_tuner", "harmony_conductor"],
            ResonanceType.EMOTIONAL_BOND: ["empathy_enhancer", "bond_deepener"],
            ResonanceType.WISDOM_SHARING: ["wisdom_scroll", "knowledge_crystal"]
        }
        
        if resonance_type in type_rewards:
            rewards.extend(type_rewards[resonance_type])
        
        return rewards
    
    def _check_story_unlock(
        self,
        intensity: ResonanceIntensity,
        resonance_type: ResonanceType,
        player_level: int
    ) -> Optional[str]:
        """[UNICODE_30B9]"""
        # [UNICODE_5F37]
        if intensity in [ResonanceIntensity.STRONG, ResonanceIntensity.INTENSE]:
            story_unlocks = {
                ResonanceType.LEVEL_SYNC: "resonance_sync_chapter",
                ResonanceType.CRYSTAL_HARMONY: "crystal_harmony_chapter",
                ResonanceType.EMOTIONAL_BOND: "emotional_bond_chapter",
                ResonanceType.WISDOM_SHARING: "wisdom_sharing_chapter"
            }
            
            # [UNICODE_30D7]
            if player_level >= 10:
                return story_unlocks.get(resonance_type)
        
        return None
    
    def get_resonance_statistics(self) -> Dict:
        """[UNICODE_5171]"""
        if not self.event_history:
            return {
                "total_events": 0,
                "events_by_type": {},
                "events_by_intensity": {},
                "total_bonus_xp": 0,
                "average_bonus_xp": 0,
                "last_event": None
            }
        
        # [UNICODE_30BF]
        events_by_type = {}
        for event in self.event_history:
            event_type = event.resonance_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        # [UNICODE_5F37]
        events_by_intensity = {}
        for event in self.event_history:
            intensity = event.intensity.value
            events_by_intensity[intensity] = events_by_intensity.get(intensity, 0) + 1
        
        # XP[UNICODE_7D71]
        total_bonus_xp = sum(event.bonus_xp for event in self.event_history)
        average_bonus_xp = total_bonus_xp / len(self.event_history)
        
        return {
            "total_events": len(self.event_history),
            "events_by_type": events_by_type,
            "events_by_intensity": events_by_intensity,
            "total_bonus_xp": total_bonus_xp,
            "average_bonus_xp": average_bonus_xp,
            "last_event": self.event_history[-1].triggered_at if self.event_history else None
        }
    
    def simulate_resonance_probability(
        self,
        player_level: int,
        yu_level: int,
        days_ahead: int = 7
    ) -> Dict:
        """[UNICODE_5171]"""
        current_time = datetime.utcnow()
        simulation_results = []
        
        for day in range(days_ahead):
            sim_time = current_time + timedelta(days=day)
            can_resonate, resonance_type = self.check_resonance_conditions(
                player_level, yu_level, sim_time
            )
            
            simulation_results.append({
                "day": day + 1,
                "can_resonate": can_resonate,
                "resonance_type": resonance_type.value if resonance_type else None,
                "level_difference": abs(player_level - yu_level)
            })
        
        return {
            "simulation_days": days_ahead,
            "results": simulation_results,
            "resonance_possible_days": sum(1 for r in simulation_results if r["can_resonate"])
        }