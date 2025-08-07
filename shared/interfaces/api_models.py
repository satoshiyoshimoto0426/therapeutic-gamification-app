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

