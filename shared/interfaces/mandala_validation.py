"""
Mandala Validation Interface

Mandalaシステムのバリデーション機能
Requirements: 4.1, 4.3
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from .mandala_system import MandalaGrid, MemoryCell
from .core_types import ChapterType, CellStatus


class ValidationResult(BaseModel):
    """バリデーション結果"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {}


class MandalaBusinessRules:
    """Mandalaビジネスルール"""
    
    MAX_DAILY_COMPLETIONS = 3
    MIN_CELL_COMPLETION_INTERVAL_HOURS = 1
    REQUIRED_CENTER_COMPLETION_FOR_CHAPTER = True
    
    @staticmethod
    def validate_cell_unlock_sequence(grid: MandalaGrid, row: int, col: int) -> ValidationResult:
        """セルアンロック順序の妥当性チェック"""
        errors = []
        warnings = []
        
        cell = grid.get_cell(row, col)
        if not cell:
            errors.append(f"セル({row}, {col})が存在しません")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 中央セルは常にアンロック可能
        if cell.is_center_cell():
            return ValidationResult(is_valid=True)
        
        # アンロック条件チェック
        completed_cells = grid._get_completed_cell_ids()
        
        for condition in cell.unlock_conditions:
            if condition not in completed_cells:
                errors.append(f"アンロック条件が満たされていません: {condition}")
        
        # 距離チェック（中央から遠すぎる場合の警告）
        distance = max(abs(row - 4), abs(col - 4))
        if distance > 3:
            warnings.append("中央から離れすぎたセルです。段階的な進行を推奨します。")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    @staticmethod
    def validate_daily_completion_limit(
        uid: str, 
        completion_history: List[datetime]
    ) -> ValidationResult:
        """日次完了制限チェック"""
        today = datetime.utcnow().date()
        today_completions = [
            dt for dt in completion_history 
            if dt.date() == today
        ]
        
        if len(today_completions) >= MandalaBusinessRules.MAX_DAILY_COMPLETIONS:
            return ValidationResult(
                is_valid=False,
                errors=[f"本日の完了制限({MandalaBusinessRules.MAX_DAILY_COMPLETIONS}個)に達しています"]
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_completion_interval(
        last_completion: Optional[datetime]
    ) -> ValidationResult:
        """完了間隔チェック"""
        if not last_completion:
            return ValidationResult(is_valid=True)
        
        hours_since_last = (datetime.utcnow() - last_completion).total_seconds() / 3600
        
        if hours_since_last < MandalaBusinessRules.MIN_CELL_COMPLETION_INTERVAL_HOURS:
            return ValidationResult(
                is_valid=False,
                errors=[f"前回の完了から{MandalaBusinessRules.MIN_CELL_COMPLETION_INTERVAL_HOURS}時間経過する必要があります"]
            )
        
        return ValidationResult(is_valid=True)


class MandalaValidator:
    """Mandalaバリデーター"""
    
    def __init__(self):
        self.business_rules = MandalaBusinessRules()
    
    def validate_cell_unlock(
        self, 
        uid: str, 
        grid: MandalaGrid, 
        row: int, 
        col: int
    ) -> ValidationResult:
        """セルアンロックの総合バリデーション"""
        # 基本的な範囲チェック
        if not (0 <= row < 9 and 0 <= col < 9):
            return ValidationResult(
                is_valid=False,
                errors=["無効な座標です"]
            )
        
        cell = grid.get_cell(row, col)
        if not cell:
            return ValidationResult(
                is_valid=False,
                errors=["セルが存在しません"]
            )
        
        # 既にアンロック済みかチェック
        if cell.status != CellStatus.LOCKED:
            return ValidationResult(
                is_valid=False,
                errors=["セルは既にアンロック済みです"]
            )
        
        # ビジネスルールチェック
        sequence_result = self.business_rules.validate_cell_unlock_sequence(grid, row, col)
        
        return sequence_result
    
    def validate_cell_completion(
        self, 
        uid: str, 
        grid: MandalaGrid, 
        row: int, 
        col: int,
        completion_history: List[datetime] = None
    ) -> ValidationResult:
        """セル完了の総合バリデーション"""
        # 基本的な範囲チェック
        if not (0 <= row < 9 and 0 <= col < 9):
            return ValidationResult(
                is_valid=False,
                errors=["無効な座標です"]
            )
        
        cell = grid.get_cell(row, col)
        if not cell:
            return ValidationResult(
                is_valid=False,
                errors=["セルが存在しません"]
            )
        
        # セルがアンロック済みかチェック
        if cell.status != CellStatus.AVAILABLE:
            return ValidationResult(
                is_valid=False,
                errors=["セルはアンロックされていません"]
            )
        
        # 日次制限チェック
        if completion_history:
            daily_limit_result = self.business_rules.validate_daily_completion_limit(
                uid, completion_history
            )
            if not daily_limit_result.is_valid:
                return daily_limit_result
        
        # 完了間隔チェック
        last_completion = None
        if completion_history:
            last_completion = max(completion_history) if completion_history else None
        
        interval_result = self.business_rules.validate_completion_interval(last_completion)
        if not interval_result.is_valid:
            return interval_result
        
        return ValidationResult(is_valid=True)
    
    def validate_grid_integrity(self, grid: MandalaGrid) -> ValidationResult:
        """グリッド整合性チェック"""
        errors = []
        warnings = []
        
        # グリッドサイズチェック
        if len(grid.cells) != 9:
            errors.append("グリッドの行数が正しくありません")
        
        for i, row in enumerate(grid.cells):
            if len(row) != 9:
                errors.append(f"行{i}の列数が正しくありません")
        
        # 中央セルチェック
        center_cell = grid.get_cell(4, 4)
        if not center_cell:
            errors.append("中央セルが存在しません")
        elif center_cell.status == CellStatus.LOCKED:
            warnings.append("中央セルがロックされています")
        
        # セル位置の整合性チェック
        for row in range(9):
            for col in range(9):
                cell = grid.get_cell(row, col)
                if cell and cell.position != (row, col):
                    errors.append(f"セル({row}, {col})の位置情報が不正です")
        
        # 統計の整合性チェック
        actual_unlocked = len(grid.get_unlocked_cells())
        actual_completed = len(grid.get_completed_cells())
        
        if grid.unlocked_count != actual_unlocked:
            errors.append("アンロック数の統計が不正です")
        
        if grid.completed_count != actual_completed:
            errors.append("完了数の統計が不正です")
        
        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid, 
            errors=errors, 
            warnings=warnings,
            details={
                "actual_unlocked": actual_unlocked,
                "actual_completed": actual_completed,
                "reported_unlocked": grid.unlocked_count,
                "reported_completed": grid.completed_count
            }
        )
    
    def validate_chapter_progression(
        self, 
        uid: str, 
        current_chapter: ChapterType,
        user_grids: Dict[ChapterType, MandalaGrid]
    ) -> ValidationResult:
        """章進行の妥当性チェック"""
        errors = []
        warnings = []
        
        # 前の章の完了チェック
        chapter_order = [
            ChapterType.SELF_DISCIPLINE,
            ChapterType.EMPATHY,
            ChapterType.RESILIENCE,
            ChapterType.CURIOSITY,
            ChapterType.COMMUNICATION,
            ChapterType.CREATIVITY,
            ChapterType.COURAGE,
            ChapterType.WISDOM
        ]
        
        try:
            current_index = chapter_order.index(current_chapter)
            
            # 前の章がすべて完了しているかチェック
            for i in range(current_index):
                prev_chapter = chapter_order[i]
                if prev_chapter in user_grids:
                    prev_grid = user_grids[prev_chapter]
                    if prev_grid.completion_percentage < 100.0:
                        warnings.append(f"前の章({prev_chapter.value})が未完了です")
                else:
                    warnings.append(f"前の章({prev_chapter.value})が開始されていません")
        
        except ValueError:
            errors.append("無効な章タイプです")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)