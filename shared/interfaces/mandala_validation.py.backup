"""
Mandala System Validation

Mandala[UNICODE_30B7]

Requirements: 4.1, 4.3
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from .mandala_system import MandalaGrid, MemoryCell, CellStatus


@dataclass
class ValidationResult:
    """[UNICODE_691C]"""
    is_valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class MandalaValidator:
    """Mandala[UNICODE_30B7]"""
    
    def __init__(self):
        self.max_difficulty = 5
        self.min_difficulty = 1
        self.max_xp_reward = 1000
        self.min_xp_reward = 1
        self.max_quest_title_length = 100
        self.max_quest_description_length = 500
    
    def validate_grid_structure(self, grid: MandalaGrid) -> ValidationResult:
        """[UNICODE_30B0]"""
        errors = []
        warnings = []
        
        # [UNICODE_30B0]
        if len(grid.grid) != 9:
            errors.append("[UNICODE_30B0]9[UNICODE_3067]")
        
        for i, row in enumerate(grid.grid):
            if len(row) != 9:
                errors.append(f"[UNICODE_30B0]{i}[UNICODE_306E]9[UNICODE_3067]")
        
        # [UNICODE_4E2D]
        core_value_positions = [(4, 4), (3, 4), (5, 4), (4, 3), (4, 5), (3, 3), (5, 5), (3, 5), (5, 3)]
        for pos in core_value_positions:
            x, y = pos
            cell = grid.grid[x][y]
            if not cell or cell.status != CellStatus.CORE_VALUE:
                errors.append(f"[UNICODE_4E2D]({x}, {y})[UNICODE_304C]")
        
        # [UNICODE_30A2]
        actual_unlocked = sum(1 for row in grid.grid for cell in row 
                            if cell and cell.status in [CellStatus.UNLOCKED, CellStatus.COMPLETED])
        if actual_unlocked != grid.unlocked_count:
            warnings.append(f"[UNICODE_30A2]: [UNICODE_5B9F]={actual_unlocked}, [UNICODE_8A18]={grid.unlocked_count}")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_code="GRID_STRUCTURE_INVALID",
                error_message="; ".join(errors),
                warnings=warnings
            )
        
        return ValidationResult(is_valid=True, warnings=warnings)
    
    def validate_cell_data(self, cell: MemoryCell) -> ValidationResult:
        """[UNICODE_30BB]"""
        errors = []
        warnings = []
        
        # [UNICODE_5EA7]
        x, y = cell.position
        if not (0 <= x < 9 and 0 <= y < 9):
            errors.append(f"[UNICODE_7121]: ({x}, {y})")
        
        # [UNICODE_96E3]
        if not (self.min_difficulty <= cell.difficulty <= self.max_difficulty):
            errors.append(f"[UNICODE_96E3]: {cell.difficulty} ([UNICODE_7BC4]: {self.min_difficulty}-{self.max_difficulty})")
        
        # XP[UNICODE_5831]
        if not (self.min_xp_reward <= cell.xp_reward <= self.max_xp_reward):
            errors.append(f"XP[UNICODE_5831]: {cell.xp_reward} ([UNICODE_7BC4]: {self.min_xp_reward}-{self.max_xp_reward})")
        
        # [UNICODE_30AF]
        if not cell.quest_title or len(cell.quest_title.strip()) == 0:
            errors.append("[UNICODE_30AF]")
        elif len(cell.quest_title) > self.max_quest_title_length:
            errors.append(f"[UNICODE_30AF]: {len(cell.quest_title)} > {self.max_quest_title_length}")
        
        # [UNICODE_30AF]
        if not cell.quest_description or len(cell.quest_description.strip()) == 0:
            warnings.append("[UNICODE_30AF]")
        elif len(cell.quest_description) > self.max_quest_description_length:
            errors.append(f"[UNICODE_30AF]: {len(cell.quest_description)} > {self.max_quest_description_length}")
        
        # [UNICODE_30BB]ID[UNICODE_306E]
        if not cell.cell_id or len(cell.cell_id.strip()) == 0:
            errors.append("[UNICODE_30BB]ID[UNICODE_304C]")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_code="CELL_DATA_INVALID",
                error_message="; ".join(errors),
                warnings=warnings
            )
        
        return ValidationResult(is_valid=True, warnings=warnings)
    
    def validate_unlock_request(self, grid: MandalaGrid, x: int, y: int, 
                              quest_data: Dict[str, Any]) -> ValidationResult:
        """[UNICODE_30BB]"""
        errors = []
        warnings = []
        
        # [UNICODE_5EA7]
        if not (0 <= x < 9 and 0 <= y < 9):
            errors.append(f"[UNICODE_7121]: ({x}, {y})")
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_COORDINATES",
                error_message=errors[0]
            )
        
        # [UNICODE_65E2]
        existing_cell = grid.grid[x][y]
        if existing_cell is not None:
            if existing_cell.status == CellStatus.CORE_VALUE:
                errors.append("[UNICODE_4E2D]")
            else:
                errors.append("[UNICODE_65E2]")
        
        # [UNICODE_30A2]
        if not grid.can_unlock(x, y):
            errors.append("[UNICODE_30A2]")
        
        # [UNICODE_30AF]
        required_fields = ["quest_title", "quest_description", "xp_reward", "difficulty"]
        for field in required_fields:
            if field not in quest_data:
                errors.append(f"[UNICODE_5FC5]: {field}")
        
        # [UNICODE_96E3]
        difficulty = quest_data.get("difficulty", 0)
        if not isinstance(difficulty, int) or not (self.min_difficulty <= difficulty <= self.max_difficulty):
            errors.append(f"[UNICODE_7121]: {difficulty}")
        
        # XP[UNICODE_5831]
        xp_reward = quest_data.get("xp_reward", 0)
        if not isinstance(xp_reward, int) or not (self.min_xp_reward <= xp_reward <= self.max_xp_reward):
            errors.append(f"[UNICODE_7121]XP[UNICODE_5831]: {xp_reward}")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_code="UNLOCK_REQUEST_INVALID",
                error_message="; ".join(errors),
                warnings=warnings
            )
        
        return ValidationResult(is_valid=True, warnings=warnings)
    
    def validate_completion_request(self, grid: MandalaGrid, x: int, y: int) -> ValidationResult:
        """[UNICODE_30BB]"""
        errors = []
        
        # [UNICODE_5EA7]
        if not (0 <= x < 9 and 0 <= y < 9):
            errors.append(f"[UNICODE_7121]: ({x}, {y})")
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_COORDINATES",
                error_message=errors[0]
            )
        
        # [UNICODE_30BB]
        cell = grid.grid[x][y]
        if cell is None:
            errors.append("[UNICODE_30BB]")
        elif cell.status != CellStatus.UNLOCKED:
            if cell.status == CellStatus.LOCKED:
                errors.append("[UNICODE_30ED]")
            elif cell.status == CellStatus.COMPLETED:
                errors.append("[UNICODE_65E2]")
            elif cell.status == CellStatus.CORE_VALUE:
                errors.append("[UNICODE_4E2D]")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_code="COMPLETION_REQUEST_INVALID",
                error_message="; ".join(errors)
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_api_response_data(self, data: Dict[str, Any]) -> ValidationResult:
        """API[UNICODE_5FDC]"""
        errors = []
        warnings = []
        
        # [UNICODE_5FC5]
        required_fields = ["uid", "grid", "unlocked_count", "total_cells"]
        for field in required_fields:
            if field not in data:
                errors.append(f"[UNICODE_5FC5]: {field}")
        
        # [UNICODE_30B0]
        if "grid" in data:
            grid_data = data["grid"]
            if not isinstance(grid_data, list) or len(grid_data) != 9:
                errors.append("[UNICODE_30B0]")
            else:
                for i, row in enumerate(grid_data):
                    if not isinstance(row, list) or len(row) != 9:
                        errors.append(f"[UNICODE_30B0]{i}[UNICODE_306E]")
        
        # [UNICODE_6570]
        if "unlocked_count" in data:
            if not isinstance(data["unlocked_count"], int) or data["unlocked_count"] < 0:
                errors.append("unlocked_count[UNICODE_304C]")
        
        if "total_cells" in data:
            if data["total_cells"] != 81:
                warnings.append(f"total_cells[UNICODE_304C]: {data['total_cells']} != 81")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                error_code="API_RESPONSE_INVALID",
                error_message="; ".join(errors),
                warnings=warnings
            )
        
        return ValidationResult(is_valid=True, warnings=warnings)
    
    def validate_therapeutic_focus(self, therapeutic_focus: Optional[str]) -> ValidationResult:
        """[UNICODE_6CBB]"""
        if not therapeutic_focus:
            return ValidationResult(is_valid=True)
        
        valid_focuses = [
            "Self-Discipline", "Empathy", "Resilience", "Curiosity",
            "Communication", "Creativity", "Courage", "Wisdom",
            "Self-Acceptance", "Self-Compassion", "Growth Mindset",
            "Authentic Living", "Social Connection", "Mindfulness",
            "Values-Based Action", "Radical Acceptance", "Psychological Flexibility"
        ]
        
        if therapeutic_focus not in valid_focuses:
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_THERAPEUTIC_FOCUS",
                error_message=f"[UNICODE_7121]: {therapeutic_focus}"
            )
        
        return ValidationResult(is_valid=True)


class MandalaBusinessRules:
    """Mandala[UNICODE_30B7]"""
    
    def __init__(self):
        self.max_daily_unlocks = 3  # 1[UNICODE_65E5]3[UNICODE_30BB]
        self.min_completion_interval_hours = 1  # [UNICODE_30BB]1[UNICODE_6642]
    
    def can_unlock_today(self, grid: MandalaGrid, today_unlocks: int) -> ValidationResult:
        """[UNICODE_4ECA]"""
        if today_unlocks >= self.max_daily_unlocks:
            return ValidationResult(
                is_valid=False,
                error_code="DAILY_UNLOCK_LIMIT_EXCEEDED",
                error_message=f"1[UNICODE_65E5]({self.max_daily_unlocks})[UNICODE_306B]"
            )
        
        return ValidationResult(is_valid=True)
    
    def can_complete_now(self, grid: MandalaGrid, x: int, y: int, 
                        last_completion_time: Optional[str]) -> ValidationResult:
        """[UNICODE_73FE]"""
        if last_completion_time:
            from datetime import datetime, timedelta
            try:
                last_time = datetime.fromisoformat(last_completion_time)
                now = datetime.now()
                if now - last_time < timedelta(hours=self.min_completion_interval_hours):
                    return ValidationResult(
                        is_valid=False,
                        error_code="COMPLETION_INTERVAL_TOO_SHORT",
                        error_message=f"[UNICODE_524D]{self.min_completion_interval_hours}[UNICODE_6642]"
                    )
            except ValueError:
                pass  # [UNICODE_65E5]
        
        return ValidationResult(is_valid=True)
    
    def validate_progression_path(self, grid: MandalaGrid) -> ValidationResult:
        """[UNICODE_9032]"""
        warnings = []
        
        # [UNICODE_5B64]
        isolated_cells = []
        for x in range(9):
            for y in range(9):
                cell = grid.grid[x][y]
                if cell and cell.status == CellStatus.UNLOCKED:
                    if self._is_isolated_cell(grid, x, y):
                        isolated_cells.append((x, y))
        
        if isolated_cells:
            warnings.append(f"[UNICODE_5B64]: {isolated_cells}")
        
        # [UNICODE_30D0]
        quadrant_counts = self._count_quadrant_unlocks(grid)
        max_diff = max(quadrant_counts) - min(quadrant_counts)
        if max_diff > 5:
            warnings.append(f"[UNICODE_8C61]: {quadrant_counts}")
        
        return ValidationResult(is_valid=True, warnings=warnings)
    
    def _is_isolated_cell(self, grid: MandalaGrid, x: int, y: int) -> bool:
        """[UNICODE_30BB]"""
        adjacent_positions = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1),
            (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)
        ]
        
        connected_count = 0
        for adj_x, adj_y in adjacent_positions:
            if 0 <= adj_x < 9 and 0 <= adj_y < 9:
                adj_cell = grid.grid[adj_x][adj_y]
                if adj_cell and adj_cell.status in [CellStatus.UNLOCKED, CellStatus.COMPLETED, CellStatus.CORE_VALUE]:
                    connected_count += 1
        
        return connected_count <= 1  # 1[UNICODE_3064]
    
    def _count_quadrant_unlocks(self, grid: MandalaGrid) -> List[int]:
        """[UNICODE_5404]"""
        quadrants = [
            [(0, 4), (0, 4)],  # [UNICODE_5DE6]
            [(0, 4), (5, 8)],  # [UNICODE_53F3]
            [(5, 8), (0, 4)],  # [UNICODE_5DE6]
            [(5, 8), (5, 8)]   # [UNICODE_53F3]
        ]
        
        counts = []
        for (x_range, y_range) in quadrants:
            count = 0
            for x in range(x_range[0], x_range[1] + 1):
                for y in range(y_range[0], y_range[1] + 1):
                    cell = grid.grid[x][y]
                    if cell and cell.status in [CellStatus.UNLOCKED, CellStatus.COMPLETED]:
                        count += 1
            counts.append(count)
        
        return counts