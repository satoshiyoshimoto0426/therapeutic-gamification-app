"""
Mandala System Interface

9x9[UNICODE_30B0]ACT[UNICODE_7642]
[UNICODE_30B0]Mandala[UNICODE_30B7]

Requirements: 4.1, 4.3
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class CellStatus(Enum):
    """[UNICODE_30BB]"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"
    CORE_VALUE = "core_value"


@dataclass
class MemoryCell:
    """[UNICODE_30E1]"""
    cell_id: str
    position: Tuple[int, int]  # (x, y) coordinates
    status: CellStatus
    quest_title: str
    quest_description: str
    xp_reward: int
    difficulty: int  # 1-5
    unlock_requirements: List[str] = field(default_factory=list)
    completion_time: Optional[datetime] = None
    linked_story_node: Optional[str] = None
    therapeutic_focus: Optional[str] = None


@dataclass
class CoreValue:
    """[UNICODE_4E2D]ACT[UNICODE_7642]"""
    name: str
    description: str
    daily_reminder: str
    position: Tuple[int, int]
    therapeutic_principle: str


class MandalaGrid:
    """
    9x9 Mandala[UNICODE_30B0]
    
    [UNICODE_4E2D]ACT[UNICODE_7642]
    81[UNICODE_500B]
    """
    
    def __init__(self, uid: str):
        self.uid = uid
        self.grid: List[List[Optional[MemoryCell]]] = [[None for _ in range(9)] for _ in range(9)]
        self.core_values: Dict[Tuple[int, int], CoreValue] = {}
        self.unlocked_count = 0
        self.total_cells = 81
        self.last_updated = datetime.now()
        
        # [UNICODE_4E2D]
        self._initialize_core_values()
    
    def _initialize_core_values(self) -> None:
        """[UNICODE_4E2D]ACT[UNICODE_7642]"""
        core_values_data = [
            {
                "name": "Core Self",
                "description": "[UNICODE_771F]",
                "daily_reminder": "[UNICODE_4ECA]",
                "position": (4, 4),  # [UNICODE_4E2D]
                "therapeutic_principle": "Self-Acceptance"
            },
            {
                "name": "Compassion",
                "description": "[UNICODE_6148]",
                "daily_reminder": "[UNICODE_81EA]",
                "position": (3, 4),
                "therapeutic_principle": "Self-Compassion"
            },
            {
                "name": "Growth",
                "description": "[UNICODE_6210]",
                "daily_reminder": "[UNICODE_5C0F]",
                "position": (5, 4),
                "therapeutic_principle": "Growth Mindset"
            },
            {
                "name": "Authenticity",
                "description": "[UNICODE_771F]",
                "daily_reminder": "[UNICODE_81EA]",
                "position": (4, 3),
                "therapeutic_principle": "Authentic Living"
            },
            {
                "name": "Connection",
                "description": "[UNICODE_3064]",
                "daily_reminder": "[UNICODE_4EBA]",
                "position": (4, 5),
                "therapeutic_principle": "Social Connection"
            },
            {
                "name": "Present Moment",
                "description": "[UNICODE_4ECA]",
                "daily_reminder": "[UNICODE_4ECA]",
                "position": (3, 3),
                "therapeutic_principle": "Mindfulness"
            },
            {
                "name": "Values Action",
                "description": "[UNICODE_4FA1]",
                "daily_reminder": "[UNICODE_5927]",
                "position": (5, 5),
                "therapeutic_principle": "Values-Based Action"
            },
            {
                "name": "Acceptance",
                "description": "[UNICODE_53D7]",
                "daily_reminder": "[UNICODE_5909]",
                "position": (3, 5),
                "therapeutic_principle": "Radical Acceptance"
            },
            {
                "name": "Commitment",
                "description": "[UNICODE_30B3]",
                "daily_reminder": "[UNICODE_5927]",
                "position": (5, 3),
                "therapeutic_principle": "Psychological Flexibility"
            }
        ]
        
        for value_data in core_values_data:
            core_value = CoreValue(**value_data)
            self.core_values[core_value.position] = core_value
            
            # [UNICODE_30B0]
            x, y = core_value.position
            value_cell = MemoryCell(
                cell_id=f"core_value_{x}_{y}",
                position=(x, y),
                status=CellStatus.CORE_VALUE,
                quest_title=core_value.name,
                quest_description=core_value.description,
                xp_reward=0,
                difficulty=0,
                therapeutic_focus=core_value.therapeutic_principle
            )
            self.grid[x][y] = value_cell
    
    def unlock_cell(self, x: int, y: int, quest_data: Dict[str, Any]) -> bool:
        """
        [UNICODE_30BB]
        
        Args:
            x, y: [UNICODE_30B0]
            quest_data: [UNICODE_30AF]
            
        Returns:
            bool: [UNICODE_30A2]/[UNICODE_5931]
        """
        if not self._is_valid_position(x, y):
            return False
        
        if not self.can_unlock(x, y):
            return False
        
        # [UNICODE_65E2]
        if (x, y) in self.core_values:
            return False
        
        # [UNICODE_30E1]
        memory_cell = MemoryCell(
            cell_id=quest_data.get("cell_id", f"cell_{x}_{y}"),
            position=(x, y),
            status=CellStatus.UNLOCKED,
            quest_title=quest_data.get("quest_title", ""),
            quest_description=quest_data.get("quest_description", ""),
            xp_reward=quest_data.get("xp_reward", 10),
            difficulty=quest_data.get("difficulty", 1),
            unlock_requirements=quest_data.get("unlock_requirements", []),
            linked_story_node=quest_data.get("linked_story_node"),
            therapeutic_focus=quest_data.get("therapeutic_focus")
        )
        
        self.grid[x][y] = memory_cell
        self.unlocked_count += 1
        self.last_updated = datetime.now()
        
        return True
    
    def complete_cell(self, x: int, y: int) -> bool:
        """
        [UNICODE_30BB]
        
        Args:
            x, y: [UNICODE_30B0]
            
        Returns:
            bool: [UNICODE_5B8C]/[UNICODE_5931]
        """
        if not self._is_valid_position(x, y):
            return False
        
        cell = self.grid[x][y]
        if not cell or cell.status != CellStatus.UNLOCKED:
            return False
        
        cell.status = CellStatus.COMPLETED
        cell.completion_time = datetime.now()
        self.last_updated = datetime.now()
        
        return True
    
    def get_cell(self, x: int, y: int) -> Optional[MemoryCell]:
        """[UNICODE_6307]"""
        if not self._is_valid_position(x, y):
            return None
        return self.grid[x][y]
    
    def get_unlocked_cells(self) -> List[MemoryCell]:
        """[UNICODE_30A2]"""
        unlocked_cells = []
        for row in self.grid:
            for cell in row:
                if cell and cell.status == CellStatus.UNLOCKED:
                    unlocked_cells.append(cell)
        return unlocked_cells
    
    def get_completed_cells(self) -> List[MemoryCell]:
        """[UNICODE_5B8C]"""
        completed_cells = []
        for row in self.grid:
            for cell in row:
                if cell and cell.status == CellStatus.COMPLETED:
                    completed_cells.append(cell)
        return completed_cells
    
    def get_daily_core_value_reminder(self) -> str:
        """[UNICODE_4ECA]"""
        import random
        core_values_list = list(self.core_values.values())
        if core_values_list:
            selected_value = random.choice(core_values_list)
            return f"[UNICODE_1F48E] {selected_value.name}: {selected_value.daily_reminder}"
        return "[UNICODE_1F48E] [UNICODE_4ECA]"
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """[UNICODE_5EA7]"""
        return 0 <= x < 9 and 0 <= y < 9
    
    def can_unlock(self, x: int, y: int) -> bool:
        """[UNICODE_30BB]"""
        # [UNICODE_65E2]
        if self.grid[x][y] is not None:
            return False
        
        # [UNICODE_96A3]
        adjacent_positions = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1),
            (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)
        ]
        
        for adj_x, adj_y in adjacent_positions:
            if self._is_valid_position(adj_x, adj_y):
                adj_cell = self.grid[adj_x][adj_y]
                if adj_cell and adj_cell.status in [CellStatus.UNLOCKED, CellStatus.COMPLETED, CellStatus.CORE_VALUE]:
                    return True
        
        return False
    
    def serialize_grid(self) -> Dict[str, Any]:
        """[UNICODE_30B0]JSON[UNICODE_5F62]"""
        grid_data = []
        
        for x in range(9):
            row = []
            for y in range(9):
                cell = self.grid[x][y]
                if cell is None:
                    row.append({"status": "locked"})
                else:
                    cell_data = {
                        "cell_id": cell.cell_id,
                        "position": cell.position,
                        "status": cell.status.value,
                        "quest_title": cell.quest_title,
                        "quest_description": cell.quest_description,
                        "xp_reward": cell.xp_reward,
                        "difficulty": cell.difficulty,
                        "therapeutic_focus": cell.therapeutic_focus
                    }
                    
                    if cell.completion_time:
                        cell_data["completion_time"] = cell.completion_time.isoformat()
                    
                    if cell.linked_story_node:
                        cell_data["linked_story_node"] = cell.linked_story_node
                    
                    row.append(cell_data)
            grid_data.append(row)
        
        return {
            "uid": self.uid,
            "grid": grid_data,
            "unlocked_count": self.unlocked_count,
            "total_cells": self.total_cells,
            "completion_rate": self.unlocked_count / self.total_cells if self.total_cells > 0 else 0,
            "last_updated": self.last_updated.isoformat(),
            "core_values": {
                f"{pos[0]}_{pos[1]}": {
                    "name": value.name,
                    "description": value.description,
                    "daily_reminder": value.daily_reminder,
                    "therapeutic_principle": value.therapeutic_principle
                }
                for pos, value in self.core_values.items()
            }
        }
    
    @classmethod
    def deserialize_grid(cls, data: Dict[str, Any]) -> 'MandalaGrid':
        """JSON[UNICODE_5F62]"""
        mandala = cls(data["uid"])
        mandala.unlocked_count = data.get("unlocked_count", 0)
        mandala.last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        
        grid_data = data.get("grid", [])
        for x in range(9):
            for y in range(9):
                if x < len(grid_data) and y < len(grid_data[x]):
                    cell_data = grid_data[x][y]
                    if cell_data.get("status") != "locked":
                        cell = MemoryCell(
                            cell_id=cell_data.get("cell_id", f"cell_{x}_{y}"),
                            position=(x, y),
                            status=CellStatus(cell_data.get("status", "locked")),
                            quest_title=cell_data.get("quest_title", ""),
                            quest_description=cell_data.get("quest_description", ""),
                            xp_reward=cell_data.get("xp_reward", 0),
                            difficulty=cell_data.get("difficulty", 1),
                            therapeutic_focus=cell_data.get("therapeutic_focus")
                        )
                        
                        if cell_data.get("completion_time"):
                            cell.completion_time = datetime.fromisoformat(cell_data["completion_time"])
                        
                        if cell_data.get("linked_story_node"):
                            cell.linked_story_node = cell_data["linked_story_node"]
                        
                        mandala.grid[x][y] = cell
        
        return mandala


class MandalaSystemInterface:
    """Mandala[UNICODE_30B7]"""
    
    def __init__(self):
        self.grids: Dict[str, MandalaGrid] = {}
    
    def get_or_create_grid(self, uid: str) -> MandalaGrid:
        """[UNICODE_30E6]Mandala[UNICODE_30B0]"""
        if uid not in self.grids:
            self.grids[uid] = MandalaGrid(uid)
        return self.grids[uid]
    
    def get_grid_api_response(self, uid: str) -> Dict[str, Any]:
        """API[UNICODE_5FDC]"""
        grid = self.get_or_create_grid(uid)
        return grid.serialize_grid()
    
    def unlock_cell_for_user(self, uid: str, x: int, y: int, quest_data: Dict[str, Any]) -> bool:
        """[UNICODE_30E6]"""
        grid = self.get_or_create_grid(uid)
        return grid.unlock_cell(x, y, quest_data)
    
    def complete_cell_for_user(self, uid: str, x: int, y: int) -> bool:
        """[UNICODE_30E6]"""
        grid = self.get_or_create_grid(uid)
        return grid.complete_cell(x, y)
    
    def get_daily_reminder_for_user(self, uid: str) -> str:
        """[UNICODE_30E6]"""
        grid = self.get_or_create_grid(uid)
        return grid.get_daily_core_value_reminder()
    
    def save_grid(self, uid: str) -> Dict[str, Any]:
        """[UNICODE_30B0]"""
        if uid in self.grids:
            return self.grids[uid].serialize_grid()
        return {}
    
    def load_grid(self, uid: str, data: Dict[str, Any]) -> None:
        """[UNICODE_4FDD]"""
        self.grids[uid] = MandalaGrid.deserialize_grid(data)