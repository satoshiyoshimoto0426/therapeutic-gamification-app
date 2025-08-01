"""
Mandala System Interface

Mandalaシステムのインターフェース定義
Requirements: 4.1, 4.3
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from .core_types import ChapterType, CellStatus


class MemoryCell(BaseModel):
    """メモリセル（Mandalaの個別セル）"""
    cell_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: Tuple[int, int]  # (row, col) 0-8の範囲
    chapter_type: ChapterType
    status: CellStatus = CellStatus.LOCKED
    title: str = ""
    description: str = ""
    task_id: Optional[str] = None
    unlock_conditions: List[str] = []
    xp_reward: int = 0
    completion_date: Optional[datetime] = None
    therapeutic_insight: str = ""
    story_connection: Optional[str] = None
    
    def is_center_cell(self) -> bool:
        """中央セルかどうか判定"""
        return self.position == (4, 4)
    
    def is_core_value_cell(self) -> bool:
        """コア価値セル（中央周辺）かどうか判定"""
        row, col = self.position
        return abs(row - 4) <= 1 and abs(col - 4) <= 1 and not self.is_center_cell()
    
    def can_unlock(self, completed_cells: List[str]) -> bool:
        """アンロック可能かチェック"""
        if self.status != CellStatus.LOCKED:
            return False
        
        # アンロック条件チェック
        for condition in self.unlock_conditions:
            if condition not in completed_cells:
                return False
        
        return True


class MandalaGrid(BaseModel):
    """9x9 Mandalaグリッド"""
    chapter_type: ChapterType
    cells: List[List[Optional[MemoryCell]]] = []  # 9x9グリッド
    center_value: str = ""
    completion_percentage: float = 0.0
    unlocked_count: int = 0
    completed_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.cells:
            self._initialize_grid()
        self._update_statistics()
    
    def _initialize_grid(self):
        """グリッド初期化"""
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        
        # 中央価値設定
        center_values = {
            ChapterType.SELF_DISCIPLINE: "自律性",
            ChapterType.EMPATHY: "共感力",
            ChapterType.RESILIENCE: "回復力",
            ChapterType.CURIOSITY: "好奇心",
            ChapterType.COMMUNICATION: "コミュニケーション",
            ChapterType.CREATIVITY: "創造性",
            ChapterType.COURAGE: "勇気",
            ChapterType.WISDOM: "知恵"
        }
        self.center_value = center_values.get(self.chapter_type, "成長")
        
        # セル初期化
        for row in range(9):
            for col in range(9):
                cell = MemoryCell(
                    position=(row, col),
                    chapter_type=self.chapter_type,
                    title=self._generate_cell_title(row, col),
                    description=self._generate_cell_description(row, col),
                    unlock_conditions=self._generate_unlock_conditions(row, col)
                )
                
                # 中央セルは最初からアンロック
                if cell.is_center_cell():
                    cell.status = CellStatus.AVAILABLE
                
                self.cells[row][col] = cell
    
    def _generate_cell_title(self, row: int, col: int) -> str:
        """セルタイトル生成"""
        if (row, col) == (4, 4):
            return f"{self.center_value}の核心"
        
        # 章タイプに基づくタイトル生成
        chapter_titles = {
            ChapterType.SELF_DISCIPLINE: [
                "朝の習慣", "時間管理", "目標設定", "集中力", "継続力",
                "自制心", "規律", "責任感", "計画性"
            ],
            ChapterType.EMPATHY: [
                "他者理解", "感情認識", "共感表現", "傾聴", "思いやり",
                "配慮", "支援", "協調", "理解"
            ],
            # 他の章タイプも同様に定義
        }
        
        titles = chapter_titles.get(self.chapter_type, ["成長", "発見", "学び"])
        index = (row * 9 + col) % len(titles)
        return titles[index]
    
    def _generate_cell_description(self, row: int, col: int) -> str:
        """セル説明生成"""
        if (row, col) == (4, 4):
            return f"{self.center_value}の本質を理解し、実践する"
        
        return f"{self._generate_cell_title(row, col)}に関する課題や活動"
    
    def _generate_unlock_conditions(self, row: int, col: int) -> List[str]:
        """アンロック条件生成"""
        if (row, col) == (4, 4):
            return []  # 中央は条件なし
        
        conditions = []
        
        # 中央から近い順にアンロック
        distance = max(abs(row - 4), abs(col - 4))
        
        if distance == 1:
            # 中央周辺は中央完了が条件
            conditions.append("center_completed")
        elif distance == 2:
            # 2層目は1層目の隣接セル完了が条件
            adjacent_positions = self._get_adjacent_positions(row, col, distance - 1)
            for pos in adjacent_positions:
                conditions.append(f"cell_{pos[0]}_{pos[1]}_completed")
        
        return conditions
    
    def _get_adjacent_positions(self, row: int, col: int, target_distance: int) -> List[Tuple[int, int]]:
        """指定距離の隣接位置取得"""
        positions = []
        for r in range(max(0, row - 1), min(9, row + 2)):
            for c in range(max(0, col - 1), min(9, col + 2)):
                if (r, c) != (row, col):
                    distance = max(abs(r - 4), abs(c - 4))
                    if distance == target_distance:
                        positions.append((r, c))
        return positions
    
    def unlock_cell(self, row: int, col: int) -> bool:
        """セルアンロック"""
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        
        cell = self.cells[row][col]
        if not cell or cell.status != CellStatus.LOCKED:
            return False
        
        # アンロック条件チェック
        completed_cells = self._get_completed_cell_ids()
        if not cell.can_unlock(completed_cells):
            return False
        
        cell.status = CellStatus.AVAILABLE
        self.last_updated = datetime.utcnow()
        self._update_statistics()
        
        return True
    
    def complete_cell(self, row: int, col: int, task_id: Optional[str] = None) -> bool:
        """セル完了"""
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        
        cell = self.cells[row][col]
        if not cell or cell.status != CellStatus.AVAILABLE:
            return False
        
        cell.status = CellStatus.COMPLETED
        cell.completion_date = datetime.utcnow()
        cell.task_id = task_id
        
        # 隣接セルのアンロックチェック
        self._check_adjacent_unlocks(row, col)
        
        self.last_updated = datetime.utcnow()
        self._update_statistics()
        
        return True
    
    def _check_adjacent_unlocks(self, row: int, col: int):
        """隣接セルのアンロック可能性チェック"""
        for r in range(max(0, row - 2), min(9, row + 3)):
            for c in range(max(0, col - 2), min(9, col + 3)):
                if (r, c) != (row, col):
                    self.unlock_cell(r, c)
    
    def _get_completed_cell_ids(self) -> List[str]:
        """完了済みセルID一覧取得"""
        completed = []
        
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if cell and cell.status == CellStatus.COMPLETED:
                    completed.append(f"cell_{row}_{col}_completed")
        
        # 中央セル特別処理
        center_cell = self.cells[4][4]
        if center_cell and center_cell.status == CellStatus.COMPLETED:
            completed.append("center_completed")
        
        return completed
    
    def _update_statistics(self):
        """統計更新"""
        total_cells = 81
        unlocked = 0
        completed = 0
        
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if cell:
                    if cell.status in [CellStatus.AVAILABLE, CellStatus.IN_PROGRESS, CellStatus.COMPLETED]:
                        unlocked += 1
                    if cell.status == CellStatus.COMPLETED:
                        completed += 1
        
        self.unlocked_count = unlocked
        self.completed_count = completed
        self.completion_percentage = (completed / total_cells) * 100
    
    def get_cell(self, x: int, y: int) -> Optional[MemoryCell]:
        """指定位置のセル取得"""
        if not (0 <= x < 9 and 0 <= y < 9):
            return None
        return self.cells[x][y]
    
    def can_unlock(self, x: int, y: int) -> bool:
        """指定位置のセルがアンロック可能かチェック"""
        cell = self.get_cell(x, y)
        if not cell:
            return False
        
        completed_cells = self._get_completed_cell_ids()
        return cell.can_unlock(completed_cells)
    
    def get_unlocked_cells(self) -> List[MemoryCell]:
        """アンロック済みセル一覧取得"""
        unlocked = []
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if cell and cell.status in [CellStatus.AVAILABLE, CellStatus.IN_PROGRESS, CellStatus.COMPLETED]:
                    unlocked.append(cell)
        return unlocked
    
    def get_completed_cells(self) -> List[MemoryCell]:
        """完了済みセル一覧取得"""
        completed = []
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                if cell and cell.status == CellStatus.COMPLETED:
                    completed.append(cell)
        return completed
    
    @property
    def total_cells(self) -> int:
        """総セル数"""
        return 81
    
    @property
    def core_values(self) -> Dict[str, str]:
        """コア価値一覧"""
        return {
            "center": self.center_value,
            "chapter": self.chapter_type.value
        }
    
    def to_api_response(self, uid: str) -> Dict[str, Any]:
        """API応答形式に変換"""
        grid_data = []
        
        for row in range(9):
            row_data = []
            for col in range(9):
                cell = self.cells[row][col]
                if cell:
                    cell_data = {
                        "id": cell.cell_id,
                        "position": cell.position,
                        "status": cell.status.value,
                        "title": cell.title,
                        "description": cell.description,
                        "xp_reward": cell.xp_reward,
                        "task_id": cell.task_id,
                        "completion_date": cell.completion_date.isoformat() if cell.completion_date else None
                    }
                else:
                    cell_data = {"status": "locked"}
                
                row_data.append(cell_data)
            grid_data.append(row_data)
        
        return {
            "uid": uid,
            "chapter_type": self.chapter_type.value,
            "center_value": self.center_value,
            "grid": grid_data,
            "unlocked_count": self.unlocked_count,
            "completed_count": self.completed_count,
            "completion_percentage": self.completion_percentage,
            "total_cells": 81,
            "core_values": self.core_values,
            "last_updated": self.last_updated.isoformat()
        }


class MandalaSystemInterface:
    """Mandalaシステムインターフェース"""
    
    def __init__(self):
        # 実際の実装ではFirestoreを使用
        self.user_grids: Dict[str, Dict[ChapterType, MandalaGrid]] = {}
    
    def get_user_grid(self, uid: str, chapter_type: ChapterType) -> MandalaGrid:
        """ユーザーのMandalaグリッド取得"""
        if uid not in self.user_grids:
            self.user_grids[uid] = {}
        
        if chapter_type not in self.user_grids[uid]:
            self.user_grids[uid][chapter_type] = MandalaGrid(chapter_type=chapter_type)
        
        return self.user_grids[uid][chapter_type]
    
    def unlock_cell(self, uid: str, chapter_type: ChapterType, row: int, col: int) -> bool:
        """セルアンロック"""
        grid = self.get_user_grid(uid, chapter_type)
        return grid.unlock_cell(row, col)
    
    def complete_cell(
        self, 
        uid: str, 
        chapter_type: ChapterType, 
        row: int, 
        col: int,
        task_id: Optional[str] = None
    ) -> bool:
        """セル完了"""
        grid = self.get_user_grid(uid, chapter_type)
        return grid.complete_cell(row, col, task_id)
    
    def get_grid_api_response(self, uid: str, chapter_type: ChapterType) -> Dict[str, Any]:
        """グリッドAPI応答取得"""
        grid = self.get_user_grid(uid, chapter_type)
        return grid.to_api_response(uid)
    
    def get_user_progress_summary(self, uid: str) -> Dict[str, Any]:
        """ユーザー進捗サマリー取得"""
        if uid not in self.user_grids:
            return {
                "uid": uid,
                "total_chapters": 0,
                "completed_chapters": 0,
                "total_cells": 0,
                "completed_cells": 0,
                "overall_completion": 0.0,
                "chapter_progress": {}
            }
        
        total_cells = 0
        completed_cells = 0
        completed_chapters = 0
        chapter_progress = {}
        
        for chapter_type, grid in self.user_grids[uid].items():
            total_cells += 81
            completed_cells += grid.completed_count
            
            chapter_progress[chapter_type.value] = {
                "completion_percentage": grid.completion_percentage,
                "completed_count": grid.completed_count,
                "unlocked_count": grid.unlocked_count
            }
            
            if grid.completion_percentage >= 100.0:
                completed_chapters += 1
        
        overall_completion = (completed_cells / total_cells * 100) if total_cells > 0 else 0.0
        
        return {
            "uid": uid,
            "total_chapters": len(self.user_grids[uid]),
            "completed_chapters": completed_chapters,
            "total_cells": total_cells,
            "completed_cells": completed_cells,
            "overall_completion": overall_completion,
            "chapter_progress": chapter_progress
        }
    
    # 統合テスト用の互換性メソッド
    def get_or_create_grid(self, uid: str, chapter_type: ChapterType = ChapterType.SELF_DISCIPLINE) -> MandalaGrid:
        """グリッド取得または作成（統合テスト用）"""
        return self.get_user_grid(uid, chapter_type)
    
    def unlock_cell_for_user(self, uid: str, x: int, y: int, quest_data: Dict[str, Any]) -> bool:
        """ユーザー用セルアンロック（統合テスト用）"""
        # デフォルトのchapter_typeを使用
        return self.unlock_cell(uid, ChapterType.SELF_DISCIPLINE, x, y)
    
    def complete_cell_for_user(self, uid: str, x: int, y: int) -> bool:
        """ユーザー用セル完了（統合テスト用）"""
        # デフォルトのchapter_typeを使用
        return self.complete_cell(uid, ChapterType.SELF_DISCIPLINE, x, y)
    
    def get_daily_reminder_for_user(self, uid: str) -> str:
        """ユーザー用日次リマインダー取得（統合テスト用）"""
        return f"{uid}さん、今日もMandalaで成長の一歩を踏み出しましょう！"