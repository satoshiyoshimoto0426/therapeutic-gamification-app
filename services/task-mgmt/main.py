"""
Task Management Service

4?XP計算
Routine?One-Shot?Skill-Up?Socialタスク

Requirements: 5.1, 5.5
"""

from fastapi import FastAPI, HTTPException, Depends, Body, Path, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.task_system import (
    Task, TaskType, TaskDifficulty, TaskPriority, TaskStatus, ADHDSupportLevel,
    TaskXPCalculator, TaskTypeRecommender, XPCalculationResult
)
from shared.interfaces.core_types import CrystalAttribute
# from shared.middleware.rbac_middleware import (
#     require_task_edit_access, get_current_guardian
# )
from pomodoro_integration_fixed import (
    pomodoro_service, PomodoroSession, PomodoroSessionStatus, 
    BreakType, ADHDSupportMetrics
)

app = FastAPI(
    title="Task Management Service",
    description="4?XP計算",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ?
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ?Firestoreを
task_storage: Dict[str, Dict[str, Task]] = {}  # uid -> task_id -> Task

# Request/Response Models
class CreateTaskRequest(BaseModel):
    """タスク"""
    task_type: TaskType = Field(..., description="タスク")
    title: str = Field(..., min_length=1, max_length=100, description="タスク")
    description: str = Field("", max_length=500, description="タスク")
    difficulty: TaskDifficulty = Field(..., description="?")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="?")
    estimated_duration: int = Field(30, ge=5, le=480, description="?")
    due_date: Optional[datetime] = Field(None, description="?")
    adhd_support_level: ADHDSupportLevel = Field(ADHDSupportLevel.NONE, description="ADHD支援")
    pomodoro_sessions_planned: int = Field(1, ge=1, le=10, description="?Pomodoro?")
    break_reminders_enabled: bool = Field(True, description="?")
    focus_music_enabled: bool = Field(False, description="?")
    linked_story_edge: Optional[str] = Field(None, description="?")
    habit_tag: Optional[str] = Field(None, description="?")
    mandala_cell_id: Optional[str] = Field(None, description="Mandala?ID")
    primary_crystal_attribute: Optional[CrystalAttribute] = Field(None, description="?")
    secondary_crystal_attributes: List[CrystalAttribute] = Field([], description="?")
    tags: List[str] = Field([], description="タスク")
    is_recurring: bool = Field(False, description="?")
    recurrence_pattern: Optional[str] = Field(None, description="?")


class UpdateTaskRequest(BaseModel):
    """タスク"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="タスク")
    description: Optional[str] = Field(None, max_length=500, description="タスク")
    difficulty: Optional[TaskDifficulty] = Field(None, description="?")
    priority: Optional[TaskPriority] = Field(None, description="?")
    estimated_duration: Optional[int] = Field(None, ge=5, le=480, description="?")
    due_date: Optional[datetime] = Field(None, description="?")
    adhd_support_level: Optional[ADHDSupportLevel] = Field(None, description="ADHD支援")
    pomodoro_sessions_planned: Optional[int] = Field(None, ge=1, le=10, description="?Pomodoro?")
    break_reminders_enabled: Optional[bool] = Field(None, description="?")
    focus_music_enabled: Optional[bool] = Field(None, description="?")
    tags: Optional[List[str]] = Field(None, description="タスク")
    notes: Optional[str] = Field(None, description="メイン")


class StartTaskRequest(BaseModel):
    """タスク"""
    pomodoro_session: bool = Field(False, description="Pomodoro?")


class CompleteTaskRequest(BaseModel):
    """タスク"""
    mood_score: int = Field(..., ge=1, le=5, description="?")
    actual_duration: Optional[int] = Field(None, ge=1, le=1440, description="実装")
    notes: str = Field("", max_length=1000, description="?")
    pomodoro_sessions_completed: int = Field(0, ge=0, le=20, description="?Pomodoro?")


class TaskResponse(BaseModel):
    """タスク"""
    task_id: str
    uid: str
    task_type: str
    title: str
    description: str
    difficulty: int
    priority: str
    status: str
    estimated_duration: int
    actual_duration: Optional[int]
    due_date: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    base_xp: int
    xp_earned: int
    mood_at_completion: Optional[int]
    adhd_support_level: str
    pomodoro_sessions_planned: int
    pomodoro_sessions_completed: int
    break_reminders_enabled: bool
    focus_music_enabled: bool
    linked_story_edge: Optional[str]
    habit_tag: Optional[str]
    mandala_cell_id: Optional[str]
    primary_crystal_attribute: Optional[str]
    secondary_crystal_attributes: List[str]
    tags: List[str]
    notes: str
    is_recurring: bool
    recurrence_pattern: Optional[str]
    is_overdue: bool
    time_remaining_minutes: Optional[int]


class XPPreviewRequest(BaseModel):
    """XPプレビュー"""
    task_type: TaskType = Field(..., description="タスク")
    difficulty: TaskDifficulty = Field(..., description="?")
    mood_score: int = Field(..., ge=1, le=5, description="気分")
    adhd_support_level: ADHDSupportLevel = Field(ADHDSupportLevel.NONE, description="ADHD支援")


class TaskRecommendationRequest(BaseModel):
    """タスク"""
    primary_goal: str = Field(..., min_length=1, max_length=200, description="?")
    user_experience_level: int = Field(..., ge=1, le=5, description="ユーザー")
    task_complexity: str = Field(..., description="タスク", pattern="^(simple|moderate|complex)$")
    user_confidence: int = Field(..., ge=1, le=5, description="ユーザー")


# Pomodoro?Request/Response Models
class StartPomodoroRequest(BaseModel):
    """Pomodoro?"""
    duration: int = Field(25, ge=5, le=60, description="?")
    focus_music_enabled: bool = Field(False, description="?")


class CompletePomodoroRequest(BaseModel):
    """Pomodoro?"""
    actual_duration: Optional[int] = Field(None, ge=1, le=120, description="実装")
    notes: str = Field("", max_length=500, description="?")


class PomodoroSessionResponse(BaseModel):
    """Pomodoro?"""
    session_id: str
    uid: str
    task_id: str
    planned_duration: int
    actual_duration: Optional[int]
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    break_type: Optional[str]
    break_duration: int
    break_started_at: Optional[str]
    break_completed_at: Optional[str]
    focus_music_enabled: bool
    interruption_count: int
    notes: str


# Helper Functions
def task_to_response(task: Task) -> TaskResponse:
    """Task?TaskResponseに"""
    time_remaining = task.get_time_remaining()
    time_remaining_minutes = int(time_remaining.total_seconds() / 60) if time_remaining else None
    
    return TaskResponse(
        task_id=task.task_id,
        uid=task.uid,
        task_type=task.task_type.value,
        title=task.title,
        description=task.description,
        difficulty=task.difficulty.value,
        priority=task.priority.value,
        status=task.status.value,
        estimated_duration=task.estimated_duration,
        actual_duration=task.actual_duration,
        due_date=task.due_date.isoformat() if task.due_date else None,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        base_xp=task.base_xp,
        xp_earned=task.xp_earned,
        mood_at_completion=task.mood_at_completion,
        adhd_support_level=task.adhd_support_level.value,
        pomodoro_sessions_planned=task.pomodoro_sessions_planned,
        pomodoro_sessions_completed=task.pomodoro_sessions_completed,
        break_reminders_enabled=task.break_reminders_enabled,
        focus_music_enabled=task.focus_music_enabled,
        linked_story_edge=task.linked_story_edge,
        habit_tag=task.habit_tag,
        mandala_cell_id=task.mandala_cell_id,
        primary_crystal_attribute=task.primary_crystal_attribute.value if task.primary_crystal_attribute else None,
        secondary_crystal_attributes=[attr.value for attr in task.secondary_crystal_attributes],
        tags=task.tags,
        notes=task.notes,
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern,
        is_overdue=task.is_overdue(),
        time_remaining_minutes=time_remaining_minutes
    )


def get_user_tasks(uid: str) -> Dict[str, Task]:
    """ユーザー"""
    if uid not in task_storage:
        task_storage[uid] = {}
    return task_storage[uid]


def generate_task_id(uid: str) -> str:
    """?IDを"""
    import uuid
    return f"task_{uid}_{uuid.uuid4().hex[:8]}"


def pomodoro_session_to_response(session: PomodoroSession) -> PomodoroSessionResponse:
    """PomodoroSessionをPomodoroSessionResponseに"""
    return PomodoroSessionResponse(
        session_id=session.session_id,
        uid=session.uid,
        task_id=session.task_id,
        planned_duration=session.planned_duration,
        actual_duration=session.actual_duration,
        status=session.status.value,
        started_at=session.started_at.isoformat() if session.started_at else None,
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        break_type=session.break_type.value if session.break_type else None,
        break_duration=session.break_duration,
        break_started_at=session.break_started_at.isoformat() if session.break_started_at else None,
        break_completed_at=session.break_completed_at.isoformat() if session.break_completed_at else None,
        focus_music_enabled=session.focus_music_enabled,
        interruption_count=session.interruption_count,
        notes=session.notes
    )


# Task Management Endpoints
@app.post("/tasks/{uid}/create", response_model=TaskResponse)
async def create_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: CreateTaskRequest = Body(..., description="タスク")
) -> TaskResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        request: タスク
        
    Returns:
        TaskResponse: ?
        
    Raises:
        HTTPException: タスク
    """
    try:
        # ?16タスク
        user_tasks = get_user_tasks(uid)
        today = datetime.utcnow().date()
        today_tasks = [
            task for task in user_tasks.values()
            if task.created_at.date() == today
        ]
        
        if len(today_tasks) >= 16:
            raise HTTPException(
                status_code=429,
                detail="Daily task limit exceeded (16 tasks per day)"
            )
        
        # タスクID?
        task_id = generate_task_id(uid)
        
        # ?
        primary_crystal = request.primary_crystal_attribute
        secondary_crystals = request.secondary_crystal_attributes
        
        if not primary_crystal:
            recommended_crystals = TaskTypeRecommender.recommend_crystal_attributes(request.task_type)
            if recommended_crystals:
                primary_crystal = recommended_crystals[0]
                secondary_crystals = recommended_crystals[1:] if len(recommended_crystals) > 1 else []
        
        # タスク
        task = Task(
            task_id=task_id,
            uid=uid,
            task_type=request.task_type,
            title=request.title,
            description=request.description,
            difficulty=request.difficulty,
            priority=request.priority,
            estimated_duration=request.estimated_duration,
            due_date=request.due_date,
            adhd_support_level=request.adhd_support_level,
            pomodoro_sessions_planned=request.pomodoro_sessions_planned,
            break_reminders_enabled=request.break_reminders_enabled,
            focus_music_enabled=request.focus_music_enabled,
            linked_story_edge=request.linked_story_edge,
            habit_tag=request.habit_tag,
            mandala_cell_id=request.mandala_cell_id,
            primary_crystal_attribute=primary_crystal,
            secondary_crystal_attributes=secondary_crystals,
            tags=request.tags,
            is_recurring=request.is_recurring,
            recurrence_pattern=request.recurrence_pattern
        )
        
        # ストーリー
        user_tasks[task_id] = task
        
        return task_to_response(task)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task creation error: {str(e)}"
        )


@app.get("/tasks/{uid}/statistics", response_model=Dict[str, Any])
async def get_task_statistics(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    days: int = Query(30, ge=1, le=365, description="?")
) -> Dict[str, Any]:
    """
    タスク
    
    Args:
        uid: ユーザーID
        days: ?
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        # ?
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        period_tasks = [
            task for task in user_tasks.values()
            if task.created_at >= cutoff_date
        ]
        
        # ?
        total_tasks = len(period_tasks)
        completed_tasks = len([task for task in period_tasks if task.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([task for task in period_tasks if task.status == TaskStatus.IN_PROGRESS])
        pending_tasks = len([task for task in period_tasks if task.status == TaskStatus.PENDING])
        
        # タスク
        task_type_stats = {}
        for task_type in TaskType:
            type_tasks = [task for task in period_tasks if task.task_type == task_type]
            task_type_stats[task_type.value] = {
                "total": len(type_tasks),
                "completed": len([task for task in type_tasks if task.status == TaskStatus.COMPLETED]),
                "completion_rate": len([task for task in type_tasks if task.status == TaskStatus.COMPLETED]) / len(type_tasks) if type_tasks else 0
            }
        
        # XP?
        total_xp = sum(task.xp_earned for task in period_tasks if task.status == TaskStatus.COMPLETED)
        avg_xp_per_task = total_xp / completed_tasks if completed_tasks > 0 else 0
        
        # ?
        difficulty_stats = {}
        for difficulty in TaskDifficulty:
            diff_tasks = [task for task in period_tasks if task.difficulty == difficulty]
            difficulty_stats[difficulty.value] = {
                "total": len(diff_tasks),
                "completed": len([task for task in diff_tasks if task.status == TaskStatus.COMPLETED])
            }
        
        return {
            "period_days": days,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "total_xp_earned": total_xp,
            "average_xp_per_task": avg_xp_per_task,
            "task_type_statistics": task_type_stats,
            "difficulty_statistics": difficulty_stats,
            "overdue_tasks": len([task for task in period_tasks if task.is_overdue()])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Statistics error: {str(e)}"
        )


@app.get("/tasks/{uid}/daily-summary", response_model=Dict[str, Any])
async def get_daily_task_summary(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    date: Optional[str] = Query(None, description="?YYYY-MM-DD?")
) -> Dict[str, Any]:
    """
    ?
    
    Args:
        uid: ユーザーID
        date: ?
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        # ?
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            target_date = datetime.utcnow().date()
        
        user_tasks = get_user_tasks(uid)
        
        # ?
        daily_tasks = [
            task for task in user_tasks.values()
            if task.created_at.date() == target_date
        ]
        
        # ?
        total_tasks = len(daily_tasks)
        completed_tasks = len([task for task in daily_tasks if task.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([task for task in daily_tasks if task.status == TaskStatus.IN_PROGRESS])
        pending_tasks = len([task for task in daily_tasks if task.status == TaskStatus.PENDING])
        daily_xp = sum(task.xp_earned for task in daily_tasks if task.status == TaskStatus.COMPLETED)
        
        # タスク
        task_type_completion = {}
        for task_type in TaskType:
            completed_count = len([
                task for task in daily_tasks 
                if task.task_type == task_type and task.status == TaskStatus.COMPLETED
            ])
            task_type_completion[task_type.value] = completed_count
        
        # ?
        remaining_slots = max(0, 16 - total_tasks)
        
        return {
            "date": target_date.isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "daily_xp_earned": daily_xp,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "task_type_completion": task_type_completion,
            "remaining_slots": remaining_slots,
            "daily_limit": 16,
            "limit_reached": total_tasks >= 16
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Daily summary error: {str(e)}"
        )


@app.get("/tasks/{uid}", response_model=List[TaskResponse])
async def get_user_tasks_list(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    status: Optional[TaskStatus] = Query(None, description="ストーリー"),
    task_type: Optional[TaskType] = Query(None, description="タスク"),
    limit: int = Query(50, ge=1, le=100, description="?"),
    offset: int = Query(0, ge=0, description="?")
) -> List[TaskResponse]:
    """
    ユーザー
    
    Args:
        uid: ユーザーID
        status: ストーリー
        task_type: タスク
        limit: ?
        offset: ?
        
    Returns:
        List[TaskResponse]: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        tasks = list(user_tasks.values())
        
        # ?
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]
        
        # ?
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # ?
        tasks = tasks[offset:offset + limit]
        
        return [task_to_response(task) for task in tasks]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get tasks error: {str(e)}"
        )


@app.get("/tasks/{uid}/{task_id}", response_model=TaskResponse)
async def get_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100)
) -> TaskResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        
    Returns:
        TaskResponse: タスク
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        return task_to_response(task)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get task error: {str(e)}"
        )


@app.put("/tasks/{uid}/{task_id}", response_model=TaskResponse)
async def update_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100),
    request: UpdateTaskRequest = Body(..., description="タスク")
) -> TaskResponse:
    """
    タスク
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        request: タスク
        
    Returns:
        TaskResponse: ?
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        
        # ?
        if task.status == TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Cannot update completed task"
            )
        
        # ?
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(task, field):
                setattr(task, field, value)
        
        # 基本XPを
        task.base_xp = task._calculate_base_xp()
        
        return task_to_response(task)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Update task error: {str(e)}"
        )


@app.post("/tasks/{uid}/{task_id}/start", response_model=TaskResponse)
async def start_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100),
    request: StartTaskRequest = Body(..., description="タスク")
) -> TaskResponse:
    """
    タスク
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        request: タスク
        
    Returns:
        TaskResponse: ?
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        
        if task.status != TaskStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Task is not in pending status"
            )
        
        # タスク
        task.start_task()
        
        return task_to_response(task)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Start task error: {str(e)}"
        )


@app.post("/tasks/{uid}/{task_id}/complete", response_model=Dict[str, Any])
async def complete_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100),
    request: CompleteTaskRequest = Body(..., description="タスク")
) -> Dict[str, Any]:
    """
    タスク
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        request: タスク
        
    Returns:
        Dict[str, Any]: ?XP?
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=400,
                detail="Task is not in progress"
            )
        
        # Pomodoro?
        task.pomodoro_sessions_completed = request.pomodoro_sessions_completed
        
        # ADHD支援Pomodoro使用
        adhd_assist_multiplier = pomodoro_service.calculate_adhd_assist_multiplier(uid)
        
        # タスクADHD支援
        xp_earned = task.complete_task(
            request.mood_score,
            request.actual_duration,
            request.notes,
            adhd_assist_multiplier
        )
        
        # ?XP計算ADHD支援
        xp_calculation = TaskXPCalculator.calculate_detailed_xp(
            task, request.mood_score, request.actual_duration, adhd_assist_multiplier
        )
        
        # Pomodoro?
        pomodoro_stats = await pomodoro_service.get_user_pomodoro_statistics(uid, 7)  # ?7?
        
        # ?
        crystal_growth_events = task.get_crystal_growth_events()
        
        return {
            "success": True,
            "task": task_to_response(task),
            "xp_earned": xp_earned,
            "xp_calculation": {
                "base_xp": xp_calculation.base_xp,
                "mood_coefficient": xp_calculation.mood_coefficient,
                "adhd_assist_multiplier": xp_calculation.adhd_assist_multiplier,
                "time_efficiency_bonus": xp_calculation.time_efficiency_bonus,
                "priority_bonus": xp_calculation.priority_bonus,
                "final_xp": xp_calculation.final_xp,
                "breakdown": xp_calculation.breakdown
            },
            "crystal_growth_events": [
                {
                    "attribute": event[0].value,
                    "event_type": event[1].value
                }
                for event in crystal_growth_events
            ],
            "pomodoro_integration": {
                "adhd_assist_multiplier": adhd_assist_multiplier,
                "sessions_completed": request.pomodoro_sessions_completed,
                "usage_frequency_score": pomodoro_stats.get("usage_frequency_score", 0.0),
                "break_compliance_rate": pomodoro_stats.get("break_compliance_rate", 0.0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complete task error: {str(e)}"
        )


@app.delete("/tasks/{uid}/{task_id}")
async def delete_task(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100)
) -> Dict[str, Any]:
    """
    タスク
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        
    Returns:
        Dict[str, Any]: ?
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        
        # ?
        if task.status == TaskStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete task in progress"
            )
        
        # タスク
        del user_tasks[task_id]
        
        return {
            "success": True,
            "message": "Task deleted successfully",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete task error: {str(e)}"
        )


# XP and Recommendation Endpoints
@app.post("/tasks/xp-preview", response_model=Dict[str, Any])
async def get_xp_preview(
    request: XPPreviewRequest = Body(..., description="XPプレビュー")
) -> Dict[str, Any]:
    """
    タスクXPプレビュー
    
    Args:
        request: XPプレビュー
        
    Returns:
        Dict[str, Any]: XPプレビュー
    """
    try:
        preview_xp = TaskXPCalculator.get_xp_preview(
            request.task_type,
            request.difficulty,
            request.mood_score,
            request.adhd_support_level
        )
        
        return {
            "task_type": request.task_type.value,
            "difficulty": request.difficulty.value,
            "mood_score": request.mood_score,
            "adhd_support_level": request.adhd_support_level.value,
            "estimated_xp": preview_xp
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"XP preview error: {str(e)}"
        )


@app.post("/tasks/recommendations", response_model=Dict[str, Any])
async def get_task_recommendations(
    request: TaskRecommendationRequest = Body(..., description="タスク")
) -> Dict[str, Any]:
    """
    タスク
    
    Args:
        request: タスク
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        # タスク
        recommended_task_type = TaskTypeRecommender.recommend_task_type(request.primary_goal)
        
        # ?
        recommended_difficulty = TaskTypeRecommender.recommend_difficulty(
            request.user_experience_level,
            request.task_complexity,
            request.user_confidence
        )
        
        # ?
        recommended_crystals = TaskTypeRecommender.recommend_crystal_attributes(recommended_task_type)
        
        return {
            "primary_goal": request.primary_goal,
            "recommended_task_type": recommended_task_type.value,
            "recommended_difficulty": recommended_difficulty.value,
            "recommended_crystals": [crystal.value for crystal in recommended_crystals],
            "reasoning": {
                "task_type_reason": f"?{request.primary_goal}?",
                "difficulty_reason": f"?{request.user_experience_level}?{request.task_complexity}?{request.user_confidence}に"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task recommendation error: {str(e)}"
        )


# Statistics and Analytics Endpoints
        daily_tasks = [
            task for task in user_tasks.values()
            if task.created_at.date() == target_date
        ]
        
        # ?
        total_tasks = len(daily_tasks)
        completed_tasks = len([task for task in daily_tasks if task.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([task for task in daily_tasks if task.status == TaskStatus.IN_PROGRESS])
        pending_tasks = len([task for task in daily_tasks if task.status == TaskStatus.PENDING])
        
        # XP?
        total_xp = sum(task.xp_earned for task in daily_tasks if task.status == TaskStatus.COMPLETED)
        
        # タスク
        task_type_breakdown = {}
        for task_type in TaskType:
            type_tasks = [task for task in daily_tasks if task.task_type == task_type]
            task_type_breakdown[task_type.value] = len(type_tasks)
        
        # ?
        remaining_task_slots = max(0, 16 - total_tasks)
        
        return {
            "date": target_date.isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "total_xp_earned": total_xp,
            "task_type_breakdown": task_type_breakdown,
            "daily_limit": 16,
            "remaining_slots": remaining_task_slots,
            "limit_reached": total_tasks >= 16,
            "overdue_tasks": len([task for task in daily_tasks if task.is_overdue()])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Daily summary error: {str(e)}"
        )


# Pomodoro Integration Endpoints
@app.post("/tasks/{uid}/{task_id}/pomodoro/start", response_model=PomodoroSessionResponse)
async def start_pomodoro_session(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100),
    request: StartPomodoroRequest = Body(..., description="Pomodoro?")
) -> PomodoroSessionResponse:
    """
    タスクPomodoro?
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        request: Pomodoro?
        
    Returns:
        PomodoroSessionResponse: ?Pomodoro?
        
    Raises:
        HTTPException: タスク
    """
    try:
        user_tasks = get_user_tasks(uid)
        
        if task_id not in user_tasks:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = user_tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=400,
                detail="Task must be in progress to start Pomodoro session"
            )
        
        # Pomodoro?
        session = await pomodoro_service.start_session(
            uid, task_id, request.duration, request.focus_music_enabled
        )
        
        return pomodoro_session_to_response(session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Start Pomodoro session error: {str(e)}"
        )


@app.post("/tasks/{uid}/{task_id}/pomodoro/{session_id}/complete", response_model=Dict[str, Any])
async def complete_pomodoro_session(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_id: str = Path(..., description="タスクID", min_length=1, max_length=100),
    session_id: str = Path(..., description="?ID", min_length=1, max_length=100),
    request: CompletePomodoroRequest = Body(..., description="Pomodoro?")
) -> Dict[str, Any]:
    """
    Pomodoro?
    
    Args:
        uid: ユーザーID
        task_id: タスクID
        session_id: ?ID
        request: Pomodoro?
        
    Returns:
        Dict[str, Any]: ?ADHD支援
        
    Raises:
        HTTPException: ?
    """
    try:
        # Pomodoro?
        session = await pomodoro_service.complete_session(
            session_id, request.actual_duration, request.notes
        )
        
        # ADHD支援
        adhd_metrics = await pomodoro_service.get_adhd_support_metrics(uid)
        
        # 60?
        break_suggestion = await pomodoro_service.check_break_suggestion(uid)
        
        return {
            "success": True,
            "session": pomodoro_session_to_response(session),
            "adhd_support_metrics": {
                "usage_frequency_score": adhd_metrics.usage_frequency_score,
                "break_compliance_rate": adhd_metrics.break_compliance_rate,
                "focus_duration_average": adhd_metrics.focus_duration_average,
                "interruption_rate": adhd_metrics.interruption_rate,
                "adhd_assist_multiplier": adhd_metrics.adhd_assist_multiplier
            },
            "break_suggestion": break_suggestion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complete Pomodoro session error: {str(e)}"
        )


@app.get("/tasks/{uid}/pomodoro/statistics", response_model=Dict[str, Any])
async def get_pomodoro_statistics(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    days: int = Query(7, ge=1, le=30, description="?")
) -> Dict[str, Any]:
    """
    Pomodoro?
    
    Args:
        uid: ユーザーID
        days: ?
        
    Returns:
        Dict[str, Any]: Pomodoro?
    """
    try:
        stats = await pomodoro_service.get_user_pomodoro_statistics(uid, days)
        adhd_metrics = await pomodoro_service.get_adhd_support_metrics(uid)
        
        return {
            "period_days": days,
            "total_sessions": stats.get("total_sessions", 0),
            "completed_sessions": stats.get("completed_sessions", 0),
            "total_focus_time": stats.get("total_focus_time", 0),
            "average_session_duration": stats.get("average_session_duration", 0),
            "break_compliance_rate": stats.get("break_compliance_rate", 0.0),
            "usage_frequency_score": stats.get("usage_frequency_score", 0.0),
            "adhd_assist_multiplier": adhd_metrics.adhd_assist_multiplier,
            "interruption_rate": adhd_metrics.interruption_rate,
            "focus_improvement_trend": stats.get("focus_improvement_trend", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pomodoro statistics error: {str(e)}"
        )


# Health Check



@app.get("/health")
async def health_check():
    """ヘルパー"""
    return {
        "status": "healthy",
        "service": "task-management",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)