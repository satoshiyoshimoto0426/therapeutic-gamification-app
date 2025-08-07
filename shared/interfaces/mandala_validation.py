"""
Mandala Validation Interface

Mandalaシステムのバリデーション機能
Requirements: 4.1, 4.3
"""

from typing import Dict, List, Optional, Tuple, Any
from .core_types import ChapterType, CellStatus
from .validation import ValidationResult, BaseValidator
from datetime import datetime, timedelta

from .mandala_system import MandalaGrid


class MandalaValidator(BaseValidator):
    """Mandalaバリデーター"""
    
    @classmethod
    def validate_grid_position(cls, row: int, col: int) -> ValidationResult:
        """グリッド位置バリデーション"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(row, int) or not isinstance(col, int):
            result.add_error("行と列は整数である必要があります")
            return result
        
        if not (0 <= row <= 8):
            result.add_error("行は0-8の範囲である必要があります", "row")
        
        if not (0 <= col <= 8):
            result.add_error("列は0-8の範囲である必要があります", "col")
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_chapter_type(cls, chapter_type: str) -> ValidationResult:
        """チャプタータイプバリデーション"""
        result = ValidationResult(is_valid=True)
        
        try:
            ChapterType(chapter_type)
        except ValueError:
            result.add_error("無効なチャプタータイプです", "chapter_type")
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_cell_unlock_request(cls, unlock_data: Dict[str, Any]) -> ValidationResult:
        """セルアンロックリクエストバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 必須フィールドチェック
        required_fields = ["uid", "chapter_type", "row", "col"]
        for field in required_fields:
            if field not in unlock_data:
                result.add_error(f"{field}は必須です", field)
        
        # 位置バリデーション
        if "row" in unlock_data and "col" in unlock_data:
            position_result = cls.validate_grid_position(
                unlock_data["row"], unlock_data["col"]
            )
            if not position_result.is_valid:
                result.errors.extend(position_result.errors)
                result.field_errors.update(position_result.field_errors)
        
        # チャプタータイプバリデーション
        if "chapter_type" in unlock_data:
            chapter_result = cls.validate_chapter_type(unlock_data["chapter_type"])
            if not chapter_result.is_valid:
                result.errors.extend(chapter_result.errors)
                result.field_errors.update(chapter_result.field_errors)
        
        # UIDバリデーション
        if "uid" in unlock_data:
            uid_result = cls.validate_string_length(
                unlock_data["uid"], "uid", min_length=1, max_length=50
            )
            if not uid_result.is_valid:
                result.errors.extend(uid_result.errors)
                result.field_errors.update(uid_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_cell_completion_request(cls, completion_data: Dict[str, Any]) -> ValidationResult:
        """セル完了リクエストバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 基本的なアンロックリクエストバリデーション
        unlock_result = cls.validate_cell_unlock_request(completion_data)
        if not unlock_result.is_valid:
            result.errors.extend(unlock_result.errors)
            result.field_errors.update(unlock_result.field_errors)
        
        # タスクIDバリデーション（オプション）
        if "task_id" in completion_data and completion_data["task_id"]:
            task_id_result = cls.validate_string_length(
                completion_data["task_id"], "task_id", min_length=1, max_length=100
            )
            if not task_id_result.is_valid:
                result.errors.extend(task_id_result.errors)
                result.field_errors.update(task_id_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_mandala_grid_data(cls, grid_data: Dict[str, Any]) -> ValidationResult:
        """Mandalaグリッドデータバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 必須フィールドチェック
        required_fields = ["chapter_type", "cells"]
        for field in required_fields:
            if field not in grid_data:
                result.add_error(f"{field}は必須です", field)
        
        # チャプタータイプバリデーション
        if "chapter_type" in grid_data:
            chapter_result = cls.validate_chapter_type(grid_data["chapter_type"])
            if not chapter_result.is_valid:
                result.errors.extend(chapter_result.errors)
                result.field_errors.update(chapter_result.field_errors)
        
        # セルデータバリデーション
        if "cells" in grid_data:
            cells_result = cls._validate_cells_data(grid_data["cells"])
            if not cells_result.is_valid:
                result.errors.extend(cells_result.errors)
                result.field_errors.update(cells_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def _validate_cells_data(cls, cells_data: Any) -> ValidationResult:
        """Simplified cell data validation used in tests"""
        result = ValidationResult(is_valid=True)
        if not isinstance(cells_data, list) or len(cells_data) != 9:
            result.add_error("cellsは9行のリストである必要があります", "cells")
            result.is_valid = False
            return result
        for row_idx, row_data in enumerate(cells_data):
            if not isinstance(row_data, list) or len(row_data) != 9:
                result.add_error(f"行{row_idx}は9列のリストである必要があります", f"cells[{row_idx}]")
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def _validate_single_cell_data(cls, cell_data: Dict[str, Any], row: int, col: int) -> ValidationResult:
        """単一セルデータバリデーション"""
        result = ValidationResult(is_valid=True)
        
        cell_prefix = f"cells[{row}][{col}]"
        
        # 必須フィールドチェック
        required_fields = ["position", "status"]
        for field in required_fields:
            if field not in cell_data:
                result.add_error(f"{field}は必須です", f"{cell_prefix}.{field}")
        
        # 位置チェック
        if "position" in cell_data:
            position = cell_data["position"]
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                result.add_error("positionは[row, col]形式である必要があります", f"{cell_prefix}.position")
            elif position != (row, col):
                result.add_error(f"位置が一致しません。期待値: ({row}, {col}), 実際: {position}", f"{cell_prefix}.position")
        
        # ステータスチェック
        if "status" in cell_data:
            try:
                CellStatus(cell_data["status"])
            except ValueError:
                result.add_error("無効なセルステータスです", f"{cell_prefix}.status")
        
        # オプションフィールドバリデーション
        if "title" in cell_data and cell_data["title"]:
            title_result = cls.validate_string_length(
                cell_data["title"], f"{cell_prefix}.title", max_length=100
            )
            if not title_result.is_valid:
                result.errors.extend(title_result.errors)
                result.field_errors.update(title_result.field_errors)
        
        if "description" in cell_data and cell_data["description"]:
            desc_result = cls.validate_string_length(
                cell_data["description"], f"{cell_prefix}.description", max_length=500
            )
            if not desc_result.is_valid:
                result.errors.extend(desc_result.errors)
                result.field_errors.update(desc_result.field_errors)
        
        if "xp_reward" in cell_data:
            xp_result = cls.validate_numeric_range(
                cell_data["xp_reward"], f"{cell_prefix}.xp_reward", min_value=0, max_value=1000
            )
            if not xp_result.is_valid:
                result.errors.extend(xp_result.errors)
                result.field_errors.update(xp_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_progress_summary_request(cls, request_data: Dict[str, Any]) -> ValidationResult:
        """進捗サマリーリクエストバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # UIDチェック
        if "uid" not in request_data:
            result.add_error("uidは必須です", "uid")
        else:
            uid_result = cls.validate_string_length(
                request_data["uid"], "uid", min_length=1, max_length=50
            )
            if not uid_result.is_valid:
                result.errors.extend(uid_result.errors)
                result.field_errors.update(uid_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_api_response_data(cls, response_data: Dict[str, Any]) -> ValidationResult:
        """API応答データバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 必須フィールドチェック
        required_fields = ["uid", "grid", "unlocked_count", "total_cells"]
        for field in required_fields:
            if field not in response_data:
                result.add_error(f"{field}は必須です", field)
        
        # UIDバリデーション
        if "uid" in response_data:
            uid_result = cls.validate_string_length(
                response_data["uid"], "uid", min_length=1, max_length=50
            )
            if not uid_result.is_valid:
                result.errors.extend(uid_result.errors)
                result.field_errors.update(uid_result.field_errors)
        
        # グリッドデータバリデーション
        if "grid" in response_data:
            grid_result = cls._validate_cells_data(response_data["grid"])
            if not grid_result.is_valid:
                result.errors.extend(grid_result.errors)
                result.field_errors.update(grid_result.field_errors)
        
        # 数値フィールドバリデーション
        numeric_fields = ["unlocked_count", "total_cells", "completed_count"]
        for field in numeric_fields:
            if field in response_data:
                numeric_result = cls.validate_numeric_range(
                    response_data[field], field, min_value=0, max_value=81
                )
                if not numeric_result.is_valid:
                    result.errors.extend(numeric_result.errors)
                    result.field_errors.update(numeric_result.field_errors)
        
        # 完了率バリデーション
        if "completion_percentage" in response_data:
            percentage_result = cls.validate_numeric_range(
                response_data["completion_percentage"], "completion_percentage", 
                min_value=0.0, max_value=100.0
            )
            if not percentage_result.is_valid:
                result.errors.extend(percentage_result.errors)
                result.field_errors.update(percentage_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_unlock_request(cls, grid: Any, x: int, y: int, quest_data: Dict[str, Any]) -> ValidationResult:
        """アンロックリクエストバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 位置バリデーション
        position_result = cls.validate_grid_position(x, y)
        if not position_result.is_valid:
            result.errors.extend(position_result.errors)
            result.field_errors.update(position_result.field_errors)
        
        # クエストデータバリデーション
        if "quest_title" in quest_data:
            title_result = cls.validate_string_length(
                quest_data["quest_title"], "quest_title", min_length=1, max_length=100
            )
            if not title_result.is_valid:
                result.errors.extend(title_result.errors)
                result.field_errors.update(title_result.field_errors)
        
        if "quest_description" in quest_data:
            desc_result = cls.validate_string_length(
                quest_data["quest_description"], "quest_description", min_length=1, max_length=500
            )
            if not desc_result.is_valid:
                result.errors.extend(desc_result.errors)
                result.field_errors.update(desc_result.field_errors)
        
        if "xp_reward" in quest_data:
            xp_result = cls.validate_numeric_range(
                quest_data["xp_reward"], "xp_reward", min_value=1, max_value=1000
            )
            if not xp_result.is_valid:
                result.errors.extend(xp_result.errors)
                result.field_errors.update(xp_result.field_errors)
        
        if "difficulty" in quest_data:
            difficulty_result = cls.validate_numeric_range(
                quest_data["difficulty"], "difficulty", min_value=1, max_value=5
            )
            if not difficulty_result.is_valid:
                result.errors.extend(difficulty_result.errors)
                result.field_errors.update(difficulty_result.field_errors)
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_completion_request(cls, grid: Any, x: int, y: int) -> ValidationResult:
        """完了リクエストバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 位置バリデーション
        position_result = cls.validate_grid_position(x, y)
        if not position_result.is_valid:
            result.errors.extend(position_result.errors)
            result.field_errors.update(position_result.field_errors)
        
        # グリッドの状態チェック（実装されている場合）
        if hasattr(grid, 'get_cell'):
            cell = grid.get_cell(x, y)
            if cell is None:
                result.add_error("指定されたセルが存在しません", "cell")
            elif hasattr(cell, 'status') and cell.status.value != "available":
                result.add_error("セルが完了可能な状態ではありません", "cell_status")
        
        result.is_valid = len(result.errors) == 0
        return result
    
    @classmethod
    def validate_therapeutic_focus(cls, therapeutic_focus: str) -> ValidationResult:
        """治療フォーカスバリデーション"""
        result = ValidationResult(is_valid=True)
        
        # 基本的な文字列バリデーション
        focus_result = cls.validate_string_length(
            therapeutic_focus, "therapeutic_focus", min_length=1, max_length=100
        )
        if not focus_result.is_valid:
            result.errors.extend(focus_result.errors)
            result.field_errors.update(focus_result.field_errors)
        
        # 許可された治療フォーカス一覧（例）
        valid_focuses = [
            "self_discipline", "empathy", "resilience", "curiosity",
            "communication", "creativity", "courage", "wisdom",
            "mindfulness", "emotional_regulation", "social_skills"
        ]
        
        if therapeutic_focus not in valid_focuses:
            result.add_warning(f"未知の治療フォーカス: {therapeutic_focus}")
        
        result.is_valid = len(result.errors) == 0
        return result

class MandalaBusinessRules:
    """Simple business rule checks for Mandala operations"""

    MAX_DAILY_UNLOCKS = 2
    MIN_COMPLETION_INTERVAL_MINUTES = 60

    def can_unlock_today(self, grid: MandalaGrid, unlocked_today: int) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if unlocked_today >= self.MAX_DAILY_UNLOCKS:
            result.is_valid = False
            result.error_code = "DAILY_UNLOCK_LIMIT_EXCEEDED"
        return result

    def can_complete_now(self, grid: MandalaGrid, x: int, y: int, last_completion_time: Optional[str]) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if last_completion_time:
            last_time = datetime.fromisoformat(last_completion_time)
            if datetime.now() - last_time < timedelta(minutes=self.MIN_COMPLETION_INTERVAL_MINUTES):
                result.is_valid = False
                result.error_code = "COMPLETION_INTERVAL_TOO_SHORT"
        return result

