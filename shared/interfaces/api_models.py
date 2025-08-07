from __future__ import annotations
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class CrystalGrowthRequest(BaseModel):
    uid: str
    attribute: str
    growth_event: Optional[str] = None
    amount: int = 0
    note: Optional[str] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class CrystalGrowthResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    new_state: Dict = Field(default_factory=dict)
    bonuses: Dict = Field(default_factory=dict)


class CrystalSystemResponse(BaseModel):
    success: bool = True
    state: Dict = Field(default_factory=dict)
    milestones: List[Dict] = Field(default_factory=list)
    synergies: List[Dict] = Field(default_factory=list)


class CrystalResonanceRequest(BaseModel):
    uid: str
    gauges: Dict[str, int] = Field(default_factory=dict)
    synergy_count: int = 0
    mood_coefficient: float = 1.0
    base_xp: int = 0
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class CrystalResonanceResponse(BaseModel):
    success: bool = True
    intensity: float = 0.0
    bonus_xp: int = 0
    details: Dict[str, float] = Field(default_factory=dict)


class CrystalMilestoneResponse(BaseModel):
    success: bool = True
    milestone: Dict = Field(default_factory=dict)
    rewards: List[str] = Field(default_factory=list)

