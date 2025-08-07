from __future__ import annotations
from enum import StrEnum
from datetime import datetime
from typing import Any, Dict, List
from .mandala_models import MemoryCell, CellStatus


class CoreValue(StrEnum):
    PURPOSE = "Purpose"
    GROWTH = "Growth"
    MINDFULNESS = "Mindfulness"
    COURAGE = "Courage"
    COMPASSION = "Compassion"
    DISCIPLINE = "Discipline"
    CREATIVITY = "Creativity"
    RESILIENCE = "Resilience"
    BALANCE = "Balance"


class MandalaGrid:
    def __init__(self, uid: str):
        self.uid = uid
        self.total_cells = 81
        self.unlocked_count = 0
        self.last_updated = datetime.now().isoformat()
        self.grid: List[List[MemoryCell]] = [
            [MemoryCell(position=(r, c)) for c in range(9)] for r in range(9)
        ]
        self.core_values: List[CoreValue] = list(CoreValue)

        center = self.grid[4][4]
        center.status = CellStatus.CORE_VALUE
        center.quest_title = "Core Self"

    def unlock_cell(self, r: int, c: int, data: Dict[str, Any]) -> bool:
        cell = self.grid[r][c]
        if cell.status in (CellStatus.CORE_VALUE, CellStatus.UNLOCKED, CellStatus.COMPLETED):
            return False
        cell.status = CellStatus.UNLOCKED
        cell.cell_id = data.get("cell_id")
        cell.quest_title = data.get("quest_title")
        cell.quest_description = data.get("quest_description")
        cell.xp_reward = int(data.get("xp_reward", 0))
        cell.difficulty = int(data.get("difficulty", 1))
        cell.therapeutic_focus = data.get("therapeutic_focus")
        self.unlocked_count += 1
        self.last_updated = datetime.now().isoformat()
        return True

    def complete_cell(self, r: int, c: int) -> bool:
        cell = self.grid[r][c]
        if cell.status != CellStatus.UNLOCKED:
            return False
        cell.status = CellStatus.COMPLETED
        self.last_updated = datetime.now().isoformat()
        return True

    def get_unlocked_cells(self):
        return [cell for row in self.grid for cell in row if cell.status == CellStatus.UNLOCKED]

    def get_completed_cells(self):
        return [cell for row in self.grid for cell in row if cell.status == CellStatus.COMPLETED]

    def get_daily_core_value_reminder(self) -> str:
        return "今日のコアバリューを意識しましょう"

    def serialize_grid(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "unlocked_count": self.unlocked_count,
            "total_cells": self.total_cells,
            "last_updated": self.last_updated,
            "grid": [
                [cell.model_dump() | {"status": cell.status.value} for cell in row]
                for row in self.grid
            ],
        }

    @classmethod
    def deserialize_grid(cls, data: Dict[str, Any]) -> "MandalaGrid":
        g = cls(data["uid"])
        g.unlocked_count = data.get("unlocked_count", 0)
        g.total_cells = data.get("total_cells", 81)
        g.last_updated = data.get("last_updated")
        from .mandala_models import CellStatus as CS
        for r in range(9):
            for c in range(9):
                raw = dict(data["grid"][r][c])
                raw["position"] = tuple(raw.get("position", (r, c)))
                raw["status"] = CS(raw.get("status", "locked"))
                g.grid[r][c] = MemoryCell(**raw)
        return g


class MandalaSystemInterface:
    def __init__(self):
        self._grids: Dict[str, MandalaGrid] = {}

    def get_or_create_grid(self, uid: str) -> MandalaGrid:
        return self._grids.setdefault(uid, MandalaGrid(uid))

    def get_grid_api_response(self, uid: str) -> Dict[str, Any]:
        return self.get_or_create_grid(uid).serialize_grid()

    def unlock_cell_for_user(self, uid: str, r: int, c: int, data: Dict[str, Any]) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.unlock_cell(r, c, data)

    def complete_cell_for_user(self, uid: str, r: int, c: int) -> bool:
        grid = self.get_or_create_grid(uid)
        return grid.complete_cell(r, c)

    def get_daily_reminder_for_user(self, uid: str) -> str:
        return self.get_or_create_grid(uid).get_daily_core_value_reminder()

