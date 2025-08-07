from enum import StrEnum
from pydantic import BaseModel
from typing import Optional, Tuple

class CellStatus(StrEnum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"
    CORE_VALUE = "core_value"

class MemoryCell(BaseModel):
    cell_id: Optional[str] = None
    position: Tuple[int, int]
    status: CellStatus = CellStatus.LOCKED
    quest_title: Optional[str] = None
    quest_description: Optional[str] = None
    xp_reward: int = 0
    difficulty: int = 1
    therapeutic_focus: Optional[str] = None
