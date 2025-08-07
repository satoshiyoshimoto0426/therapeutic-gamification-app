"""
Mandala System Interface

Simplified models for managing the 9x9 Mandala grid used in tests.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class CellStatus(str, Enum):
    """Status of a Mandala cell"""
    LOCKED = "locked"
    CORE_VALUE = "core_value"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"


class CoreValue(BaseModel):
    """Core value information displayed in the grid"""
    name: str
    therapeutic_principle: str
    daily_reminder: str


class MemoryCell(BaseModel):
    """Individual cell within the Mandala grid"""
    cell_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: Tuple[int, int]
    status: CellStatus = CellStatus.LOCKED
    quest_title: str = ""
    quest_description: str = ""
    xp_reward: int = 0
    difficulty: int = 1
    therapeutic_focus: Optional[str] = None
    completion_time: Optional[datetime] = None


class MandalaGrid:
    """9x9 grid with central core values"""

    def __init__(self, uid: str):
        self.uid = uid
        self.grid: List[List[Optional[MemoryCell]]] = [[None for _ in range(9)] for _ in range(9)]
        self.total_cells = 81
        self.unlocked_count = 0
        self.core_values: Dict[Tuple[int, int], CoreValue] = {}
        self._initialize_core_values()

    # ------------------------------------------------------------------
    def _initialize_core_values(self) -> None:
        names = {
            (4, 4): "Core Self",
            (3, 4): "Compassion",
            (5, 4): "Growth",
            (4, 3): "Authenticity",
            (4, 5): "Connection",
            (3, 3): "Mindfulness",
            (5, 5): "Purpose",
            (3, 5): "Balance",
            (5, 3): "Creativity",
        }
        for position, name in names.items():
            core = CoreValue(
                name=name,
                therapeutic_principle=name,
                daily_reminder=f"Remember {name}"
            )
            self.core_values[position] = core
            self.grid[position[0]][position[1]] = MemoryCell(
                position=position,
                status=CellStatus.CORE_VALUE,
                quest_title=name,
            )

    # ------------------------------------------------------------------
    def _has_adjacent_unlocked(self, x: int, y: int) -> bool:
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                neighbor = self.grid[nx][ny]
                if neighbor and neighbor.status in {
                    CellStatus.CORE_VALUE,
                    CellStatus.UNLOCKED,
                    CellStatus.COMPLETED,
                }:
                    return True
        return False

    # ------------------------------------------------------------------
    def unlock_cell(self, x: int, y: int, quest_data: Dict) -> bool:
        if not (0 <= x < 9 and 0 <= y < 9):
            return False
        if (x, y) in self.core_values:
            return False
        cell = self.grid[x][y]
        if cell is not None and cell.status != CellStatus.LOCKED:
            return False
        if not self._has_adjacent_unlocked(x, y):
            return False

        self.grid[x][y] = MemoryCell(
            position=(x, y),
            status=CellStatus.UNLOCKED,
            quest_title=quest_data.get("quest_title", ""),
            quest_description=quest_data.get("quest_description", ""),
            xp_reward=quest_data.get("xp_reward", 0),
            difficulty=quest_data.get("difficulty", 1),
            therapeutic_focus=quest_data.get("therapeutic_focus"),
        )
        self.unlocked_count += 1
        return True

    # ------------------------------------------------------------------
    def complete_cell(self, x: int, y: int) -> bool:
        if not (0 <= x < 9 and 0 <= y < 9):
            return False
        cell = self.grid[x][y]
        if not cell or cell.status != CellStatus.UNLOCKED:
            return False
        cell.status = CellStatus.COMPLETED
        cell.completion_time = datetime.utcnow()
        return True

    # ------------------------------------------------------------------
    def get_unlocked_cells(self) -> List[MemoryCell]:
        return [
            cell
            for row in self.grid
            for cell in row
            if cell and cell.status == CellStatus.UNLOCKED
        ]


class MandalaSystemInterface:
    """Simple in-memory manager for Mandala grids"""

    def __init__(self):
        self.grids: Dict[str, MandalaGrid] = {}

    def get_or_create_grid(self, uid: str) -> MandalaGrid:
        if uid not in self.grids:
            self.grids[uid] = MandalaGrid(uid)
        return self.grids[uid]

    def get_grid_api_response(self, uid: str) -> Dict[str, Any]:
        grid = self.get_or_create_grid(uid)
        return {
            "uid": grid.uid,
            "grid": [[
                cell.status.value if cell else None for cell in row
            ] for row in grid.grid],
            "unlocked_count": grid.unlocked_count,
            "total_cells": grid.total_cells,
        }

    def unlock_cell_for_user(self, uid: str, x: int, y: int, quest_data: Dict) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.unlock_cell(x, y, quest_data)

    def complete_cell_for_user(self, uid: str, x: int, y: int) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.complete_cell(x, y)

    def get_daily_reminder_for_user(self, uid: str) -> str:
        grid = self.get_or_create_grid(uid)
        return grid.core_values[(4, 4)].daily_reminder

