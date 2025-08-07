"""
Task management repository implementation
Handles CRUD operations for tasks with ADHD-optimized features
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
from dataclasses import dataclass

from .base_repository import BaseRepository
from ..config.firestore_collections import TaskType, TaskStatus

@dataclass
class Task:
    task_id: str
    uid: str
    task_type: TaskType
    title: str
    description: str
    difficulty: int
    status: TaskStatus
    created_at: datetime
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    xp_earned: int = 0
    mood_coefficient: float = 1.0
    adhd_assist: float = 1.0
    mandala_cell_id: Optional[str] = None
    habit_tag: Optional[str] = None
    pomodoro_sessions: int = 0
    linked_story_edge: Optional[str] = None
    estimated_duration: Optional[int] = None  # minutes

class TaskRepository(BaseRepository[Task]):
    """Repository for task management with ADHD optimization"""
    
    def __init__(self, db_client):
        super().__init__(db_client, "tasks")
    
    def _to_entity(self, doc_data: Dict[str, Any], doc_id: str = None) -> Task:
        """Convert Firestore document to Task entity"""
        return Task(
            task_id=doc_data.get("task_id", doc_id),
            uid=doc_data["uid"],
            task_type=TaskType(doc_data["task_type"]),
            title=doc_data["title"],
            description=doc_data["description"],
            difficulty=doc_data["difficulty"],
            status=TaskStatus(doc_data["status"]),
            created_at=doc_data["created_at"],
            due_date=doc_data.get("due_date"),
            completed_at=doc_data.get("completed_at"),
            xp_earned=doc_data.get("xp_earned", 0),
            mood_coefficient=doc_data.get("mood_coefficient", 1.0),
            adhd_assist=doc_data.get("adhd_assist", 1.0),
            mandala_cell_id=doc_data.get("mandala_cell_id"),
            habit_tag=doc_data.get("habit_tag"),
            pomodoro_sessions=doc_data.get("pomodoro_sessions", 0),
            linked_story_edge=doc_data.get("linked_story_edge"),
            estimated_duration=doc_data.get("estimated_duration")
        )
    
    def _to_document(self, entity: Task) -> Dict[str, Any]:
        """Convert Task entity to Firestore document"""
        task_type_value = getattr(entity.task_type, "value", entity.task_type)
        status_value = getattr(entity.status, "value", entity.status)
        return {
            "task_id": entity.task_id,
            "uid": entity.uid,
            "task_type": task_type_value,
            "title": entity.title,
            "description": entity.description,
            "difficulty": entity.difficulty,
            "status": status_value,
            "created_at": entity.created_at,
            "due_date": entity.due_date,
            "completed_at": entity.completed_at,
            "xp_earned": entity.xp_earned,
            "mood_coefficient": entity.mood_coefficient,
            "adhd_assist": entity.adhd_assist,
            "mandala_cell_id": entity.mandala_cell_id,
            "habit_tag": entity.habit_tag,
            "pomodoro_sessions": entity.pomodoro_sessions,
            "linked_story_edge": entity.linked_story_edge,
            "estimated_duration": entity.estimated_duration,
        }
    
    async def get_user_tasks(self, uid: str, status: TaskStatus = None, limit: int = None) -> List[Task]:
        """Get tasks for a specific user"""
        filters = {"uid": uid}
        if status:
            filters["status"] = getattr(status, "value", status)
        
        return await self.find_by_multiple_fields(filters, limit)
    
    async def get_daily_tasks(self, uid: str, target_date: date = None) -> List[Task]:
        """Get tasks for a specific day (ADHD daily limit: 16 tasks)"""
        if target_date is None:
            target_date = datetime.utcnow().date()
        
        start_date = datetime.combine(target_date, datetime.min.time())
        end_date = datetime.combine(target_date, datetime.max.time())
        
        return await self.find_by_date_range(
            "created_at",
            start_date,
            end_date,
            additional_filters={"uid": uid}
        )
    
    async def check_daily_task_limit(self, uid: str, target_date: date = None) -> Dict[str, Any]:
        """Check if user has reached daily task limit (ADHD consideration)"""
        daily_tasks = await self.get_daily_tasks(uid, target_date)
        
        return {
            "current_count": len(daily_tasks),
            "limit": 16,
            "can_add_more": len(daily_tasks) < 16,
            "remaining": max(0, 16 - len(daily_tasks))
        }
    
    async def create_task_with_limit_check(self, task: Task) -> str:
        """Create task with daily limit validation"""
        limit_check = await self.check_daily_task_limit(task.uid)
        
        if not limit_check["can_add_more"]:
            raise ValueError("Daily task limit (16) reached. This helps manage cognitive load for ADHD users.")
        
        return await self.create(task, task.task_id)
    
    async def complete_task(self, task_id: str, mood_coefficient: float = 1.0, adhd_assist: float = 1.0) -> Dict[str, Any]:
        """Complete a task and calculate XP"""
        task = await self.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")
        
        # Calculate XP: difficulty ? mood_coefficient ? adhd_assist ? base_multiplier
        base_multiplier = 10
        xp_earned = int(task.difficulty * mood_coefficient * adhd_assist * base_multiplier)
        
        completion_time = datetime.utcnow()
        
        updates = {
            "status": TaskStatus.COMPLETED.value,
            "completed_at": completion_time,
            "xp_earned": xp_earned,
            "mood_coefficient": mood_coefficient,
            "adhd_assist": adhd_assist
        }
        
        await self.update(task_id, updates)
        
        task_type_value = getattr(task.task_type, "value", task.task_type)
        return {
            "task_id": task_id,
            "xp_earned": xp_earned,
            "completed_at": completion_time,
            "difficulty": task.difficulty,
            "mood_coefficient": mood_coefficient,
            "adhd_assist": adhd_assist,
            "task_type": task_type_value,
        }
    
    async def get_tasks_by_mandala_cell(self, mandala_cell_id: str, status: TaskStatus = None) -> List[Task]:
        """Get tasks associated with a Mandala cell"""
        filters = {"mandala_cell_id": mandala_cell_id}
        if status:
            filters["status"] = getattr(status, "value", status)
        
        return await self.find_by_multiple_fields(filters)
    
    async def get_tasks_by_habit_tag(self, habit_tag: str, uid: str = None, limit: int = None) -> List[Task]:
        """Get tasks by habit tag"""
        filters = {"habit_tag": habit_tag}
        if uid:
            filters["uid"] = uid
        
        return await self.find_by_multiple_fields(filters, limit)
    
    async def get_overdue_tasks(self, uid: str = None) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.utcnow()
        
        # Find tasks with due_date in the past and not completed
        filters = {
            "status": TaskStatus.PENDING.value,
            "due_date": {"operator": "<", "value": now}
        }
        
        if uid:
            filters["uid"] = uid
        
        return await self.find_by_multiple_fields(filters)
    
    async def get_task_statistics(self, uid: str, days: int = 30) -> Dict[str, Any]:
        """Get task completion statistics for user"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all tasks in date range
        tasks = await self.find_by_date_range(
            "created_at",
            start_date,
            end_date,
            additional_filters={"uid": uid}
        )
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        
        # Group by task type
        type_stats = {}
        for task_type in TaskType:
            type_tasks = [t for t in tasks if t.task_type == task_type]
            type_completed = [t for t in type_tasks if t.status == TaskStatus.COMPLETED]
            
            type_stats[task_type.value] = {
                "total": len(type_tasks),
                "completed": len(type_completed),
                "completion_rate": len(type_completed) / len(type_tasks) if type_tasks else 0,
                "total_xp": sum(t.xp_earned for t in type_completed)
            }
        
        # Calculate daily averages
        daily_average = total_tasks / days if days > 0 else 0
        completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
        
        return {
            "period_days": days,
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "completion_rate": completion_rate,
            "daily_average": daily_average,
            "total_xp_earned": sum(t.xp_earned for t in completed_tasks),
            "average_difficulty": sum(t.difficulty for t in tasks) / total_tasks if total_tasks > 0 else 0,
            "type_breakdown": type_stats,
            "pomodoro_sessions": sum(t.pomodoro_sessions for t in tasks)
        }
    
    async def get_habit_progress(self, uid: str, habit_tag: str, days: int = 30) -> Dict[str, Any]:
        """Get progress for a specific habit"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        habit_tasks = await self.find_by_date_range(
            "created_at",
            start_date,
            end_date,
            additional_filters={"uid": uid, "habit_tag": habit_tag}
        )
        
        completed_tasks = [t for t in habit_tasks if t.status == TaskStatus.COMPLETED]
        
        # Calculate streak
        current_streak = await self._calculate_habit_streak(uid, habit_tag)
        
        return {
            "habit_tag": habit_tag,
            "period_days": days,
            "total_tasks": len(habit_tasks),
            "completed_tasks": len(completed_tasks),
            "completion_rate": len(completed_tasks) / len(habit_tasks) if habit_tasks else 0,
            "current_streak": current_streak,
            "total_xp": sum(t.xp_earned for t in completed_tasks),
            "average_difficulty": sum(t.difficulty for t in habit_tasks) / len(habit_tasks) if habit_tasks else 0
        }
    
    async def _calculate_habit_streak(self, uid: str, habit_tag: str) -> int:
        """Calculate current streak for a habit"""
        # Get recent tasks for this habit, ordered by completion date
        recent_tasks = await self.find_by_multiple_fields(
            {"uid": uid, "habit_tag": habit_tag, "status": TaskStatus.COMPLETED.value}
        )
        
        if not recent_tasks:
            return 0
        
        # Sort by completion date (most recent first)
        recent_tasks.sort(key=lambda t: t.completed_at, reverse=True)
        
        # Calculate consecutive days
        streak = 0
        current_date = datetime.utcnow().date()
        
        for task in recent_tasks:
            task_date = task.completed_at.date()
            
            if task_date == current_date or task_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = task_date
            else:
                break
        
        return streak
    
    async def update_pomodoro_sessions(self, task_id: str, sessions_increment: int = 1) -> bool:
        """Update Pomodoro session count for task"""
        task = await self.get_by_id(task_id)
        if not task:
            return False
        
        new_sessions = task.pomodoro_sessions + sessions_increment
        return await self.update(task_id, {"pomodoro_sessions": new_sessions})
    
    async def link_to_story_edge(self, task_id: str, story_edge_id: str) -> bool:
        """Link task to story edge for narrative integration"""
        return await self.update(task_id, {"linked_story_edge": story_edge_id})
    
    async def get_tasks_for_story_integration(self, uid: str) -> List[Task]:
        """Get tasks that can be integrated with story progression"""
        # Get pending tasks that are not yet linked to story edges
        return await self.find_by_multiple_fields({
            "uid": uid,
            "status": TaskStatus.PENDING.value,
            "linked_story_edge": None
        })
    
    async def bulk_update_task_coefficients(self, uid: str, mood_coefficient: float, adhd_assist: float) -> int:
        """Bulk update mood and ADHD assist coefficients for pending tasks"""
        pending_tasks = await self.get_user_tasks(uid, TaskStatus.PENDING)
        
        updates = {}
        for task in pending_tasks:
            updates[task.task_id] = {
                "mood_coefficient": mood_coefficient,
                "adhd_assist": adhd_assist
            }
        
        if updates:
            await self.batch_update(updates)
        
        return len(updates)
    
    async def get_weekly_task_distribution(self, uid: str) -> Dict[str, Any]:
        """Get task distribution across the week"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        weekly_tasks = await self.find_by_date_range(
            "created_at",
            start_date,
            end_date,
            additional_filters={"uid": uid}
        )
        
        # Group by day of week
        daily_distribution = {i: {"total": 0, "completed": 0} for i in range(7)}  # 0=Monday
        
        for task in weekly_tasks:
            day_of_week = task.created_at.weekday()
            daily_distribution[day_of_week]["total"] += 1
            
            if task.status == TaskStatus.COMPLETED:
                daily_distribution[day_of_week]["completed"] += 1
        
        # Convert to readable format
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        formatted_distribution = {}
        
        for day_num, stats in daily_distribution.items():
            day_name = day_names[day_num]
            completion_rate = stats["completed"] / stats["total"] if stats["total"] > 0 else 0
            
            formatted_distribution[day_name] = {
                "total_tasks": stats["total"],
                "completed_tasks": stats["completed"],
                "completion_rate": completion_rate
            }
        
        return formatted_distribution