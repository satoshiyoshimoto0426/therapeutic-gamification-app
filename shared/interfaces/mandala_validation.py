from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .mandala_system import MandalaGrid
from .mandala_models import MemoryCell, CellStatus

class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)
    error_code: Optional[str] = None

class MandalaValidator:
    def validate_grid_structure(self, grid: MandalaGrid) -> ValidationResult:
        result = ValidationResult()
        if len(grid.grid) != 9 or any(len(row) != 9 for row in grid.grid):
            result.is_valid = False
            result.errors.append("グリッドは9x9である必要があります")
            result.error_code = "INVALID_GRID_SIZE"
        return result

    def validate_cell_data(self, cell: MemoryCell) -> ValidationResult:
        result = ValidationResult()
        if not (1 <= cell.difficulty <= 5):
            result.is_valid = False
            result.field_errors.setdefault("difficulty", []).append("難易度は1-5の範囲である必要があります")
            result.error_code = "INVALID_DIFFICULTY"
        return result

    def _validate_coordinates(self, r: int, c: int) -> ValidationResult:
        res = ValidationResult()
        if not (0 <= r <= 8):
            res.is_valid = False
            res.field_errors.setdefault("row", []).append("行は0-8の範囲である必要があります")
            res.error_code = "INVALID_COORDINATES"
        if not (0 <= c <= 8):
            res.is_valid = False
            res.field_errors.setdefault("col", []).append("列は0-8の範囲である必要があります")
            res.error_code = "INVALID_COORDINATES"
        return res

    def validate_unlock_request(self, grid: MandalaGrid, r: int, c: int, data: dict) -> ValidationResult:
        res = self._validate_coordinates(r, c)
        if not res.is_valid:
            return res
        cell = grid.grid[r][c]
        if cell.status != CellStatus.LOCKED:
            res.is_valid = False
            res.error_code = "CELL_NOT_LOCKED"
        return res

    def validate_completion_request(self, grid: MandalaGrid, r: int, c: int) -> ValidationResult:
        res = self._validate_coordinates(r, c)
        if not res.is_valid:
            return res
        cell = grid.grid[r][c]
        if cell.status != CellStatus.UNLOCKED:
            res.is_valid = False
            res.error_code = "CELL_NOT_UNLOCKED"
        return res

class MandalaBusinessRules:
    def can_unlock_today(self, grid: MandalaGrid, daily_limit: int) -> ValidationResult:
        res = ValidationResult()
        if grid.unlocked_count >= daily_limit:
            res.is_valid = False
            res.error_code = "DAILY_UNLOCK_LIMIT_EXCEEDED"
        return res

    def can_complete_now(self, grid: MandalaGrid, r: int, c: int, last_time_iso: Optional[str]) -> ValidationResult:
        res = ValidationResult()
        if last_time_iso:
            try:
                last_time = datetime.fromisoformat(last_time_iso)
                if datetime.now() - last_time < timedelta(minutes=60):
                    res.is_valid = False
                    res.error_code = "COMPLETION_INTERVAL_TOO_SHORT"
            except Exception:
                pass
        return res
