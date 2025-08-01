"""
Mandala grid repository for 9x9 grid management and cell tracking
Handles mandala data storage, cell unlocking, and progress tracking
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from google.cloud import firestore

from .base_repository import BaseRepository
from ..interfaces.core_types import MandalaGrid, MandalaCell, CellStatus, ChapterType
from ..utils.exceptions import ValidationError, NotFoundError


class MandalaRepository(BaseRepository[MandalaGrid]):
    """Repository for mandala grid data"""
    
    def __init__(self, db_client: firestore.Client):
        super().__init__(db_client, "mandala_grids")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> MandalaGrid:
        """Convert Firestore document to MandalaGrid entity"""
        # Convert cells data back to MandalaCell objects
        cells_data = doc_data.get("cells", [])
        cells = []
        
        for row_data in cells_data:
            row = []
            for cell_data in row_data:
                cell = MandalaCell(
                    id=cell_data["id"],
                    position=(cell_data["position"][0], cell_data["position"][1]),
                    status=CellStatus(cell_data["status"]),
                    task_id=cell_data.get("task_id"),
                    unlock_conditions=cell_data.get("unlock_conditions", []),
                    xp_reward=cell_data.get("xp_reward", 0),
                    chapter_type=ChapterType(cell_data["chapter_type"])
                )
                row.append(cell)
            cells.append(row)
        
        return MandalaGrid(
            chapter_type=ChapterType(doc_data["chapter_type"]),
            cells=cells,
            center_value=doc_data["center_value"],
            completion_percentage=doc_data.get("completion_percentage", 0.0)
        )
    
    def _to_document(self, entity: MandalaGrid) -> Dict[str, Any]:
        """Convert MandalaGrid entity to Firestore document"""
        # Convert cells to serializable format
        cells_data = []
        for row in entity.cells:
            row_data = []
            for cell in row:
                cell_data = {
                    "id": cell.id,
                    "position": list(cell.position),
                    "status": cell.status.value,
                    "task_id": cell.task_id,
                    "unlock_conditions": cell.unlock_conditions,
                    "xp_reward": cell.xp_reward,
                    "chapter_type": cell.chapter_type.value
                }
                row_data.append(cell_data)
            cells_data.append(row_data)
        
        return {
            "chapter_type": entity.chapter_type.value,
            "cells": cells_data,
            "center_value": entity.center_value,
            "completion_percentage": entity.completion_percentage
        }
    
    async def get_user_mandala(self, uid: str, chapter_type: ChapterType) -> Optional[MandalaGrid]:
        """Get user's mandala grid for specific chapter"""
        try:
            query = (self.collection_ref
                    .where("uid", "==", uid)
                    .where("chapter_type", "==", chapter_type.value))
            
            docs = query.get()
            
            if not docs:
                return None
            
            # Should only be one mandala per user per chapter
            doc = docs[0]
            return self._to_entity(doc.to_dict(), doc.id)
            
        except Exception as e:
            self.logger.error(f"Failed to get mandala for user {uid}, chapter {chapter_type}: {str(e)}")
            raise
    
    async def create_initial_mandala(self, uid: str, chapter_type: ChapterType) -> str:
        """Create initial 9x9 mandala grid for user"""
        try:
            # Check if mandala already exists
            existing = await self.get_user_mandala(uid, chapter_type)
            if existing:
                raise ValidationError(f"Mandala already exists for chapter {chapter_type}")
            
            # Create 9x9 grid with initial state
            cells = []
            center_values = self._get_chapter_center_values()
            center_value = center_values.get(chapter_type, "Growth")
            
            for row in range(9):
                cell_row = []
                for col in range(9):
                    cell_id = f"{uid}_{chapter_type.value}_{row}_{col}"
                    
                    # Center cell (4,4) is always unlocked
                    if row == 4 and col == 4:
                        status = CellStatus.AVAILABLE
                        unlock_conditions = []
                    else:
                        status = CellStatus.LOCKED
                        unlock_conditions = self._generate_unlock_conditions(row, col)
                    
                    cell = MandalaCell(
                        id=cell_id,
                        position=(row, col),
                        status=status,
                        task_id=None,
                        unlock_conditions=unlock_conditions,
                        xp_reward=self._calculate_cell_xp_reward(row, col),
                        chapter_type=chapter_type
                    )
                    cell_row.append(cell)
                cells.append(cell_row)
            
            mandala = MandalaGrid(
                chapter_type=chapter_type,
                cells=cells,
                center_value=center_value,
                completion_percentage=0.0
            )
            
            # Add uid to document for querying
            doc_data = self._to_document(mandala)
            doc_data["uid"] = uid
            
            doc_ref = self.collection_ref.add(doc_data)[1]
            
            self.logger.info(f"Created initial mandala for user {uid}, chapter {chapter_type}")
            return doc_ref.id
            
        except Exception as e:
            self.logger.error(f"Failed to create initial mandala for user {uid}: {str(e)}")
            raise
    
    def _get_chapter_center_values(self) -> Dict[ChapterType, str]:
        """Get center values for each chapter type"""
        return {
            ChapterType.SELF_DISCIPLINE: "自動",
            ChapterType.EMPATHY: "共有",
            ChapterType.RESILIENCE: "?",
            ChapterType.CURIOSITY: "?",
            ChapterType.COMMUNICATION: "コア",
            ChapterType.CREATIVITY: "創",
            ChapterType.COURAGE: "勇",
            ChapterType.WISDOM: "?"
        }
    
    def _generate_unlock_conditions(self, row: int, col: int) -> List[str]:
        """Generate unlock conditions based on cell position"""
        conditions = []
        
        # Adjacent to center (4,4) - unlock immediately
        if abs(row - 4) <= 1 and abs(col - 4) <= 1 and not (row == 4 and col == 4):
            return []  # No conditions, available after center
        
        # Ring-based unlocking
        distance_from_center = max(abs(row - 4), abs(col - 4))
        
        if distance_from_center == 2:
            conditions.append("complete_adjacent_cells:1")
        elif distance_from_center == 3:
            conditions.append("complete_adjacent_cells:2")
        elif distance_from_center == 4:
            conditions.append("complete_adjacent_cells:3")
            conditions.append("chapter_progress:50")  # 50% chapter progress
        
        return conditions
    
    def _calculate_cell_xp_reward(self, row: int, col: int) -> int:
        """Calculate XP reward based on cell position"""
        # Center cell
        if row == 4 and col == 4:
            return 100
        
        # Distance from center determines reward
        distance_from_center = max(abs(row - 4), abs(col - 4))
        
        base_rewards = {
            1: 25,   # Adjacent to center
            2: 50,   # Second ring
            3: 75,   # Third ring
            4: 100   # Outer ring
        }
        
        return base_rewards.get(distance_from_center, 25)
    
    async def unlock_cell(self, uid: str, chapter_type: ChapterType, row: int, col: int) -> bool:
        """Unlock a specific cell if conditions are met"""
        try:
            mandala = await self.get_user_mandala(uid, chapter_type)
            if not mandala:
                raise NotFoundError(f"Mandala not found for user {uid}, chapter {chapter_type}")
            
            if not (0 <= row < 9 and 0 <= col < 9):
                raise ValidationError("Invalid cell position")
            
            cell = mandala.cells[row][col]
            
            if cell.status != CellStatus.LOCKED:
                return False  # Already unlocked or in progress
            
            # Check unlock conditions
            conditions_met = await self._check_unlock_conditions(uid, cell.unlock_conditions, mandala)
            
            if not conditions_met:
                return False
            
            # Update cell status
            mandala.cells[row][col].status = CellStatus.AVAILABLE
            
            # Update in database
            await self._update_mandala(uid, chapter_type, mandala)
            
            self.logger.info(f"Unlocked cell ({row}, {col}) for user {uid}, chapter {chapter_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unlock cell for user {uid}: {str(e)}")
            raise
    
    async def _check_unlock_conditions(self, uid: str, conditions: List[str], mandala: MandalaGrid) -> bool:
        """Check if unlock conditions are met"""
        for condition in conditions:
            if condition.startswith("complete_adjacent_cells:"):
                required_count = int(condition.split(":")[1])
                # Implementation would check adjacent completed cells
                # For now, simplified check
                completed_cells = sum(1 for row in mandala.cells for cell in row if cell.status == CellStatus.COMPLETED)
                if completed_cells < required_count:
                    return False
            
            elif condition.startswith("chapter_progress:"):
                required_progress = int(condition.split(":")[1])
                if mandala.completion_percentage < required_progress:
                    return False
        
        return True
    
    async def assign_task_to_cell(self, uid: str, chapter_type: ChapterType, 
                                row: int, col: int, task_id: str) -> bool:
        """Assign a task to a specific cell"""
        try:
            mandala = await self.get_user_mandala(uid, chapter_type)
            if not mandala:
                raise NotFoundError(f"Mandala not found for user {uid}, chapter {chapter_type}")
            
            if not (0 <= row < 9 and 0 <= col < 9):
                raise ValidationError("Invalid cell position")
            
            cell = mandala.cells[row][col]
            
            if cell.status != CellStatus.AVAILABLE:
                raise ValidationError("Cell is not available for task assignment")
            
            # Update cell
            mandala.cells[row][col].task_id = task_id
            mandala.cells[row][col].status = CellStatus.IN_PROGRESS
            
            # Update in database
            await self._update_mandala(uid, chapter_type, mandala)
            
            self.logger.info(f"Assigned task {task_id} to cell ({row}, {col}) for user {uid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign task to cell for user {uid}: {str(e)}")
            raise
    
    async def complete_cell(self, uid: str, chapter_type: ChapterType, 
                          row: int, col: int) -> Dict[str, Any]:
        """Mark cell as completed and return rewards"""
        try:
            mandala = await self.get_user_mandala(uid, chapter_type)
            if not mandala:
                raise NotFoundError(f"Mandala not found for user {uid}, chapter {chapter_type}")
            
            if not (0 <= row < 9 and 0 <= col < 9):
                raise ValidationError("Invalid cell position")
            
            cell = mandala.cells[row][col]
            
            if cell.status != CellStatus.IN_PROGRESS:
                raise ValidationError("Cell is not in progress")
            
            # Update cell status
            mandala.cells[row][col].status = CellStatus.COMPLETED
            
            # Recalculate completion percentage
            completed_cells = sum(1 for row in mandala.cells for cell in row if cell.status == CellStatus.COMPLETED)
            mandala.completion_percentage = (completed_cells / 81) * 100
            
            # Check for newly unlocked cells
            newly_unlocked = await self._check_and_unlock_adjacent_cells(uid, mandala, row, col)
            
            # Update in database
            await self._update_mandala(uid, chapter_type, mandala)
            
            rewards = {
                "xp_earned": cell.xp_reward,
                "completion_percentage": mandala.completion_percentage,
                "newly_unlocked_cells": newly_unlocked
            }
            
            self.logger.info(f"Completed cell ({row}, {col}) for user {uid}, chapter {chapter_type}")
            return rewards
            
        except Exception as e:
            self.logger.error(f"Failed to complete cell for user {uid}: {str(e)}")
            raise
    
    async def _check_and_unlock_adjacent_cells(self, uid: str, mandala: MandalaGrid, 
                                             completed_row: int, completed_col: int) -> List[Tuple[int, int]]:
        """Check and unlock adjacent cells after completion"""
        newly_unlocked = []
        
        # Check all adjacent cells (8 directions)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                new_row, new_col = completed_row + dr, completed_col + dc
                
                if 0 <= new_row < 9 and 0 <= new_col < 9:
                    cell = mandala.cells[new_row][new_col]
                    
                    if cell.status == CellStatus.LOCKED:
                        conditions_met = await self._check_unlock_conditions(uid, cell.unlock_conditions, mandala)
                        
                        if conditions_met:
                            mandala.cells[new_row][new_col].status = CellStatus.AVAILABLE
                            newly_unlocked.append((new_row, new_col))
        
        return newly_unlocked
    
    async def _update_mandala(self, uid: str, chapter_type: ChapterType, mandala: MandalaGrid) -> bool:
        """Update mandala in database"""
        try:
            # Find document ID
            query = (self.collection_ref
                    .where("uid", "==", uid)
                    .where("chapter_type", "==", chapter_type.value))
            
            docs = query.get()
            
            if docs:
                doc_id = docs[0].id
                doc_data = self._to_document(mandala)
                doc_data["uid"] = uid  # Ensure uid is included
                
                doc_ref = self.collection_ref.document(doc_id)
                doc_ref.set(doc_data)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update mandala for user {uid}: {str(e)}")
            raise
    
    async def get_mandala_progress(self, uid: str, chapter_type: ChapterType) -> Dict[str, Any]:
        """Get detailed mandala progress information"""
        try:
            mandala = await self.get_user_mandala(uid, chapter_type)
            if not mandala:
                return {"exists": False}
            
            # Count cells by status
            status_counts = {
                "locked": 0,
                "available": 0,
                "in_progress": 0,
                "completed": 0
            }
            
            available_cells = []
            in_progress_cells = []
            
            for row_idx, row in enumerate(mandala.cells):
                for col_idx, cell in enumerate(row):
                    status_counts[cell.status.value] += 1
                    
                    if cell.status == CellStatus.AVAILABLE:
                        available_cells.append({
                            "position": (row_idx, col_idx),
                            "xp_reward": cell.xp_reward
                        })
                    elif cell.status == CellStatus.IN_PROGRESS:
                        in_progress_cells.append({
                            "position": (row_idx, col_idx),
                            "task_id": cell.task_id,
                            "xp_reward": cell.xp_reward
                        })
            
            return {
                "exists": True,
                "chapter_type": chapter_type.value,
                "center_value": mandala.center_value,
                "completion_percentage": mandala.completion_percentage,
                "status_counts": status_counts,
                "available_cells": available_cells,
                "in_progress_cells": in_progress_cells,
                "total_cells": 81
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mandala progress for user {uid}: {str(e)}")
            raise
    
    async def get_all_user_mandalas(self, uid: str) -> List[Dict[str, Any]]:
        """Get all mandala grids for a user"""
        try:
            query = self.collection_ref.where("uid", "==", uid)
            docs = query.get()
            
            mandalas = []
            for doc in docs:
                doc_data = doc.to_dict()
                mandala = self._to_entity(doc_data, doc.id)
                
                progress = await self.get_mandala_progress(uid, mandala.chapter_type)
                mandalas.append(progress)
            
            return mandalas
            
        except Exception as e:
            self.logger.error(f"Failed to get all mandalas for user {uid}: {str(e)}")
            raise