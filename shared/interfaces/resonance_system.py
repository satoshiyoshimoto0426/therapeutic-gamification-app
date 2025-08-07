"""
Resonance system interfaces used in unit tests.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid

from .core_types import CrystalAttribute


class ResonanceType(str, Enum):
    LEVEL_SYNC = "level_sync"
    CRYSTAL_HARMONY = "crystal_harmony"
    EMOTIONAL_BOND = "emotional_bond"
    WISDOM_SHARING = "wisdom_sharing"


class ResonanceIntensity(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    INTENSE = "intense"


class ResonanceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resonance_type: ResonanceType
    intensity: ResonanceIntensity
    player_level: int
    yu_level: int
    level_difference: int
    bonus_xp: int
    crystal_bonuses: Dict[CrystalAttribute, int] = {}
    special_rewards: List[str] = []
    therapeutic_message: str = ""
    story_unlock: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)


class ResonanceCondition(BaseModel):
    min_level_difference: int = 5
    max_level_difference: int = 30
    cooldown_hours: int = 24
    required_player_level: int = 1


class ResonanceCalculator:
    """Helper functions for resonance calculations"""

    @staticmethod
    def calculate_resonance_intensity(level_difference: int) -> ResonanceIntensity:
        if level_difference <= 7:
            return ResonanceIntensity.WEAK
        if level_difference <= 12:
            return ResonanceIntensity.MODERATE
        if level_difference <= 20:
            return ResonanceIntensity.STRONG
        return ResonanceIntensity.INTENSE

    @staticmethod
    def _type_multiplier(resonance_type: ResonanceType) -> float:
        return {
            ResonanceType.LEVEL_SYNC: 1.0,
            ResonanceType.CRYSTAL_HARMONY: 1.2,
            ResonanceType.EMOTIONAL_BOND: 1.4,
            ResonanceType.WISDOM_SHARING: 1.6,
        }[resonance_type]

    @staticmethod
    def calculate_bonus_xp(level_difference: int, player_level: int, resonance_type: ResonanceType) -> int:
        base = level_difference * 10 + player_level * 5
        return int(base * ResonanceCalculator._type_multiplier(resonance_type))

    @staticmethod
    def _intensity_factor(intensity: ResonanceIntensity) -> int:
        return {
            ResonanceIntensity.WEAK: 1,
            ResonanceIntensity.MODERATE: 2,
            ResonanceIntensity.STRONG: 3,
            ResonanceIntensity.INTENSE: 4,
        }[intensity]

    @staticmethod
    def calculate_crystal_bonuses(resonance_type: ResonanceType, intensity: ResonanceIntensity, player_level: int) -> Dict[CrystalAttribute, int]:
        base = ResonanceCalculator._intensity_factor(intensity) * max(1, player_level // 10)
        if resonance_type == ResonanceType.CRYSTAL_HARMONY:
            attrs = [CrystalAttribute.WISDOM, CrystalAttribute.EMPATHY, CrystalAttribute.RESILIENCE]
        elif resonance_type == ResonanceType.EMOTIONAL_BOND:
            attrs = [CrystalAttribute.EMPATHY]
        elif resonance_type == ResonanceType.WISDOM_SHARING:
            attrs = [CrystalAttribute.WISDOM, CrystalAttribute.CURIOSITY]
        else:
            attrs = [CrystalAttribute.WISDOM]
        return {attr: base for attr in attrs}

    @staticmethod
    def generate_therapeutic_message(resonance_type: ResonanceType, intensity: ResonanceIntensity, player_level: int, yu_level: int) -> str:
        return (
            f"共有: {resonance_type.value} resonance at {intensity.value} intensity."
        )


class ResonanceEventManager:
    """Manage resonance events and statistics"""

    def __init__(self):
        self.conditions = ResonanceCondition()
        self.event_history: List[ResonanceEvent] = []
        self.last_event_times: Dict[ResonanceType, datetime] = {}

    # --------------------------------------------------------------
    def _determine_type(self, level_difference: int) -> ResonanceType:
        if level_difference % 4 == 0:
            return ResonanceType.WISDOM_SHARING
        if level_difference % 3 == 0:
            return ResonanceType.EMOTIONAL_BOND
        if level_difference % 2 == 0:
            return ResonanceType.CRYSTAL_HARMONY
        return ResonanceType.LEVEL_SYNC

    # --------------------------------------------------------------
    def check_resonance_conditions(self, player_level: int, yu_level: int, current_time: Optional[datetime] = None) -> Tuple[bool, Optional[ResonanceType]]:
        current_time = current_time or datetime.utcnow()
        level_diff = abs(player_level - yu_level)
        cond = self.conditions

        if level_diff < cond.min_level_difference or level_diff > cond.max_level_difference:
            return False, None
        if player_level < cond.required_player_level:
            return False, None

        res_type = self._determine_type(level_diff)
        if res_type in self.last_event_times:
            last = self.last_event_times[res_type]
            if current_time - last < timedelta(hours=cond.cooldown_hours):
                # try other types not on cooldown
                for other in ResonanceType:
                    if other == res_type:
                        continue
                    last_time = self.last_event_times.get(other)
                    if not last_time or current_time - last_time >= timedelta(hours=cond.cooldown_hours):
                        return True, other
                return False, None

        return True, res_type

    # --------------------------------------------------------------
    def _generate_special_rewards(self, intensity: ResonanceIntensity) -> List[str]:
        rewards = []
        if intensity in (ResonanceIntensity.MODERATE, ResonanceIntensity.STRONG, ResonanceIntensity.INTENSE):
            rewards.append("resonance_token")
        if intensity in (ResonanceIntensity.STRONG, ResonanceIntensity.INTENSE):
            rewards.append("rare_crystal")
        if intensity is ResonanceIntensity.INTENSE:
            rewards.append("legendary_artifact")
        return rewards

    # --------------------------------------------------------------
    def trigger_resonance_event(self, player_level: int, yu_level: int, resonance_type: ResonanceType, current_time: Optional[datetime] = None) -> ResonanceEvent:
        current_time = current_time or datetime.utcnow()
        level_diff = abs(player_level - yu_level)
        intensity = ResonanceCalculator.calculate_resonance_intensity(level_diff)
        bonus_xp = ResonanceCalculator.calculate_bonus_xp(level_diff, player_level, resonance_type)
        bonuses = ResonanceCalculator.calculate_crystal_bonuses(resonance_type, intensity, player_level)
        message = ResonanceCalculator.generate_therapeutic_message(resonance_type, intensity, player_level, yu_level)
        rewards = self._generate_special_rewards(intensity)

        event = ResonanceEvent(
            resonance_type=resonance_type,
            intensity=intensity,
            player_level=player_level,
            yu_level=yu_level,
            level_difference=level_diff,
            bonus_xp=bonus_xp,
            crystal_bonuses=bonuses,
            special_rewards=rewards,
            therapeutic_message=message,
            triggered_at=current_time,
        )

        self.event_history.append(event)
        self.last_event_times[resonance_type] = current_time
        return event

    # --------------------------------------------------------------
    def get_resonance_statistics(self) -> Dict[str, Any]:
        total_events = len(self.event_history)
        events_by_type: Dict[str, int] = {}
        events_by_intensity: Dict[str, int] = {}
        total_bonus_xp = 0
        for event in self.event_history:
            events_by_type[event.resonance_type.value] = events_by_type.get(event.resonance_type.value, 0) + 1
            events_by_intensity[event.intensity.value] = events_by_intensity.get(event.intensity.value, 0) + 1
            total_bonus_xp += event.bonus_xp
        avg_bonus = total_bonus_xp / total_events if total_events else 0
        last_event_time = self.event_history[-1].triggered_at if total_events else None
        return {
            "total_events": total_events,
            "events_by_type": events_by_type,
            "events_by_intensity": events_by_intensity,
            "total_bonus_xp": total_bonus_xp,
            "average_bonus_xp": avg_bonus,
            "last_event": last_event_time,
        }

    # --------------------------------------------------------------
    def simulate_resonance_probability(self, player_level: int, yu_level: int, days_ahead: int = 7) -> Dict[str, Any]:
        results = []
        possible_days = 0
        for day in range(1, days_ahead + 1):
            current_time = datetime.utcnow() + timedelta(days=day)
            can_resonate, r_type = self.check_resonance_conditions(player_level, yu_level, current_time)
            results.append({
                "day": day,
                "can_resonate": can_resonate,
                "resonance_type": r_type.value if r_type else None,
            })
            if can_resonate:
                possible_days += 1
        return {
            "simulation_days": days_ahead,
            "results": results,
            "resonance_possible_days": possible_days,
        }

