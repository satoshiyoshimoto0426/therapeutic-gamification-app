"""Mandala system interface using a 9x9 grid of memory cells."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CellStatus(Enum):
    """Status of a mandala grid cell."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"
    CORE_VALUE = "core_value"


@dataclass
class MemoryCell:
    """A single cell within the mandala grid."""

    cell_id: str
    position: Tuple[int, int]
    status: CellStatus
    quest_title: str
    quest_description: str
    xp_reward: int
    difficulty: int
    unlock_requirements: List[str] = field(default_factory=list)
    completion_time: Optional[datetime] = None
    linked_story_node: Optional[str] = None
    therapeutic_focus: Optional[str] = None


@dataclass
class CoreValue:
    """Core value positioned around the centre of the grid."""

    name: str
    description: str
    daily_reminder: str
    position: Tuple[int, int]
    therapeutic_principle: str


class MandalaGrid:
    """Represents a 9x9 grid of memory cells with core values in the centre."""

    def __init__(self, uid: str):
        self.uid = uid
        self.grid: List[List[Optional[MemoryCell]]] = [[None for _ in range(9)] for _ in range(9)]
        self.core_values: Dict[Tuple[int, int], CoreValue] = {}
        self.unlocked_count = 0
        self.total_cells = 81
        self.last_updated = datetime.utcnow()
        self._initialize_core_values()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------
    def _initialize_core_values(self) -> None:
        """Create the nine core values and populate the grid."""

        core_values_data = [
            {
                "name": "Core Self",
                "description": "The authentic self",
                "daily_reminder": "Remember who you are",
                "position": (4, 4),
                "therapeutic_principle": "Self-Acceptance",
            },
            {
                "name": "Compassion",
                "description": "Be kind to yourself",
                "daily_reminder": "Offer kindness",
                "position": (3, 4),
                "therapeutic_principle": "Self-Compassion",
            },
            {
                "name": "Growth",
                "description": "Embrace development",
                "daily_reminder": "Keep growing",
                "position": (5, 4),
                "therapeutic_principle": "Growth Mindset",
            },
            {
                "name": "Authenticity",
                "description": "Live your truth",
                "daily_reminder": "Stay genuine",
                "position": (4, 3),
                "therapeutic_principle": "Authentic Living",
            },
            {
                "name": "Connection",
                "description": "Reach out to others",
                "daily_reminder": "You are not alone",
                "position": (4, 5),
                "therapeutic_principle": "Social Connection",
            },
            {
                "name": "Present Moment",
                "description": "Focus on now",
                "daily_reminder": "Be here now",
                "position": (3, 3),
                "therapeutic_principle": "Mindfulness",
            },
            {
                "name": "Values Action",
                "description": "Act on values",
                "daily_reminder": "Take meaningful steps",
                "position": (5, 5),
                "therapeutic_principle": "Values-Based Action",
            },
            {
                "name": "Acceptance",
                "description": "Accept experiences",
                "daily_reminder": "Let it be",
                "position": (3, 5),
                "therapeutic_principle": "Radical Acceptance",
            },
            {
                "name": "Commitment",
                "description": "Stay committed",
                "daily_reminder": "Choose direction",
                "position": (5, 3),
                "therapeutic_principle": "Psychological Flexibility",
            },
        ]

        for data in core_values_data:
            core = CoreValue(**data)
            self.core_values[core.position] = core
            x, y = core.position
            self.grid[x][y] = MemoryCell(
                cell_id=f"core_value_{x}_{y}",
                position=core.position,
                status=CellStatus.CORE_VALUE,
                quest_title=core.name,
                quest_description=core.description,
                xp_reward=0,
                difficulty=0,
                therapeutic_focus=core.therapeutic_principle,
            )

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------
    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < 9 and 0 <= y < 9

    def can_unlock(self, x: int, y: int) -> bool:
        if not self._is_valid_position(x, y) or self.grid[x][y] is not None:
            return False

        adjacent = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
            (x - 1, y - 1),
            (x - 1, y + 1),
            (x + 1, y - 1),
            (x + 1, y + 1),
        ]

        for ax, ay in adjacent:
            if self._is_valid_position(ax, ay):
                cell = self.grid[ax][ay]
                if cell and cell.status in [
                    CellStatus.UNLOCKED,
                    CellStatus.COMPLETED,
                    CellStatus.CORE_VALUE,
                ]:
                    return True
        return False

    # ------------------------------------------------------------------
    # Cell manipulation
    # ------------------------------------------------------------------
    def unlock_cell(self, x: int, y: int, quest_data: Dict[str, Any]) -> bool:
        if not self.can_unlock(x, y) or (x, y) in self.core_values:
            return False

        cell = MemoryCell(
            cell_id=quest_data.get("cell_id", f"cell_{x}_{y}"),
            position=(x, y),
            status=CellStatus.UNLOCKED,
            quest_title=quest_data.get("quest_title", ""),
            quest_description=quest_data.get("quest_description", ""),
            xp_reward=quest_data.get("xp_reward", 10),
            difficulty=quest_data.get("difficulty", 1),
            unlock_requirements=quest_data.get("unlock_requirements", []),
            linked_story_node=quest_data.get("linked_story_node"),
            therapeutic_focus=quest_data.get("therapeutic_focus"),
        )

        self.grid[x][y] = cell
        self.unlocked_count += 1
        self.last_updated = datetime.utcnow()
        return True

    def complete_cell(self, x: int, y: int) -> bool:
        if not self._is_valid_position(x, y):
            return False

        cell = self.grid[x][y]
        if not cell or cell.status != CellStatus.UNLOCKED:
            return False

        cell.status = CellStatus.COMPLETED
        cell.completion_time = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        return True

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_cell(self, x: int, y: int) -> Optional[MemoryCell]:
        if not self._is_valid_position(x, y):
            return None
        return self.grid[x][y]

    def get_unlocked_cells(self) -> List[MemoryCell]:
        return [
            cell
            for row in self.grid
            for cell in row
            if cell and cell.status == CellStatus.UNLOCKED
        ]

    def get_completed_cells(self) -> List[MemoryCell]:
        return [
            cell
            for row in self.grid
            for cell in row
            if cell and cell.status == CellStatus.COMPLETED
        ]


class MandalaSystemInterface:
    """Simple in-memory interface for managing mandala grids per user."""

    def __init__(self):
        self.grids: Dict[str, MandalaGrid] = {}

    def get_or_create_grid(self, uid: str) -> MandalaGrid:
        if uid not in self.grids:
            self.grids[uid] = MandalaGrid(uid)
        return self.grids[uid]

    def unlock_cell_for_user(self, uid: str, x: int, y: int, quest_data: Dict[str, Any]) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.unlock_cell(x, y, quest_data)

    def complete_cell_for_user(self, uid: str, x: int, y: int) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.complete_cell(x, y)

    def get_grid_api_response(self, uid: str) -> Dict[str, Any]:
        grid = self.get_or_create_grid(uid)
        return {
            "uid": uid,
            "unlocked_count": grid.unlocked_count,
            "total_cells": grid.total_cells,
        }

