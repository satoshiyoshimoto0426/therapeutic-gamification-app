"""
Daily Trio Service - 1?3つ

?
- ADHDの1?3つ
- AIが
- 3タスク3?
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import asyncio

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="Daily Trio Service", version="1.0.0")
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    HIGH = "high"      # 治療
    MEDIUM = "medium"  # ?
    LOW = "low"        # ?

class TaskCategory(Enum):
    THERAPEUTIC = "therapeutic"  # 治療
    HABIT = "habit"             # ?
    SOCIAL = "social"           # ?
    MAINTENANCE = "maintenance" # ?

class DailyTrioTask(BaseModel):
    task_id: str
    title: str
    description: str
    category: TaskCategory
    priority: TaskPriority
    estimated_duration: int  # ?
    difficulty: int  # 1-5
    xp_reward: int
    therapeutic_focus: str  # "Self-Discipline", "Empathy", etc.
    completion_criteria: str
    micro_rewards: List[str]  # 3?

class UserState(BaseModel):
    user_id: str
    current_state: str  # APATHY, INTEREST, ACTION, CONTINUATION, HABITUATION
    mood_trend: float  # -1.0 to 1.0
    energy_level: int  # 1-5
    available_time: int  # ?
    therapeutic_goals: List[str]
    completed_tasks_today: int
    streak_days: int
    adhd_assist_level: float  # 1.0-1.3

class DailyTrioResponse(BaseModel):
    user_id: str
    selected_date: str
    trio_tasks: List[DailyTrioTask]
    selection_reasoning: str
    estimated_total_time: int
    expected_xp: int
    therapeutic_balance: Dict[str, int]

class DailyTrioEngine:
    def __init__(self):
        self.task_pool = self._initialize_task_pool()
        self.selection_weights = {
            "therapeutic_alignment": 0.4,  # 治療
            "user_state_match": 0.3,       # ユーザー
            "difficulty_balance": 0.2,     # ?
            "variety_bonus": 0.1           # ?
        }
    
    def _initialize_task_pool(self) -> List[DailyTrioTask]:
        """タスク"""
        return [
            # 治療Self-Discipline?
            DailyTrioTask(
                task_id="therapeutic_001",
                title="?",
                description="5?1?",
                category=TaskCategory.THERAPEUTIC,
                priority=TaskPriority.HIGH,
                estimated_duration=5,
                difficulty=2,
                xp_reward=30,
                therapeutic_focus="Self-Discipline",
                completion_criteria="5?",
                micro_rewards=["?", "?", "?+10"]
            ),
            DailyTrioTask(
                task_id="therapeutic_002",
                title="?",
                description="?3つ",
                category=TaskCategory.THERAPEUTIC,
                priority=TaskPriority.HIGH,
                estimated_duration=3,
                difficulty=1,
                xp_reward=20,
                therapeutic_focus="Empathy",
                completion_criteria="?3つ",
                micro_rewards=["?", "共有+5", "自動"]
            ),
            
            # ?
            DailyTrioTask(
                task_id="habit_001",
                title="?",
                description="コア1?",
                category=TaskCategory.HABIT,
                priority=TaskPriority.MEDIUM,
                estimated_duration=1,
                difficulty=1,
                xp_reward=10,
                therapeutic_focus="Self-Discipline",
                completion_criteria="?",
                micro_rewards=["?", "?+3", "?"]
            ),
            DailyTrioTask(
                task_id="habit_002",
                title="?5?",
                description="デフォルト5?",
                category=TaskCategory.HABIT,
                priority=TaskPriority.MEDIUM,
                estimated_duration=5,
                difficulty=2,
                xp_reward=25,
                therapeutic_focus="Self-Discipline",
                completion_criteria="?",
                micro_rewards=["?", "?+10", "?"]
            ),
            
            # ?
            DailyTrioTask(
                task_id="social_001",
                title="?",
                description="?5?",
                category=TaskCategory.SOCIAL,
                priority=TaskPriority.MEDIUM,
                estimated_duration=5,
                difficulty=3,
                xp_reward=35,
                therapeutic_focus="Communication",
                completion_criteria="?",
                micro_rewards=["コア", "?+15", "?"]
            ),
            DailyTrioTask(
                task_id="social_002",
                title="?",
                description="?",
                category=TaskCategory.SOCIAL,
                priority=TaskPriority.MEDIUM,
                estimated_duration=10,
                difficulty=3,
                xp_reward=40,
                therapeutic_focus="Courage",
                completion_criteria="準拠",
                micro_rewards=["準拠", "勇+10", "自動"]
            ),
            
            # ?
            DailyTrioTask(
                task_id="maintenance_001",
                title="?",
                description="お1?",
                category=TaskCategory.MAINTENANCE,
                priority=TaskPriority.LOW,
                estimated_duration=4,
                difficulty=1,
                xp_reward=15,
                therapeutic_focus="Resilience",
                completion_criteria="?",
                micro_rewards=["?", "リスト+5", "気分"]
            )
        ]
    
    async def select_daily_trio(self, user_state: UserState) -> DailyTrioResponse:
        """Daily Trio自動"""
        try:
            # 1. ユーザー
            state_analysis = self._analyze_user_state(user_state)
            
            # 2. ?
            scored_tasks = self._score_tasks(user_state, state_analysis)
            
            # 3. ?3つ
            selected_tasks = self._select_optimal_trio(scored_tasks, user_state)
            
            # 4. ?
            reasoning = self._generate_selection_reasoning(selected_tasks, user_state)
            
            # 5. レベル
            return DailyTrioResponse(
                user_id=user_state.user_id,
                selected_date=datetime.now().strftime("%Y-%m-%d"),
                trio_tasks=selected_tasks,
                selection_reasoning=reasoning,
                estimated_total_time=sum(task.estimated_duration for task in selected_tasks),
                expected_xp=sum(task.xp_reward for task in selected_tasks),
                therapeutic_balance=self._calculate_therapeutic_balance(selected_tasks)
            )
            
        except Exception as e:
            logger.error(f"Daily Trio selection failed for user {user_state.user_id}: {e}")
            raise HTTPException(status_code=500, detail="Daily Trio?")
    
    def _analyze_user_state(self, user_state: UserState) -> Dict[str, Any]:
        """ユーザー"""
        return {
            "energy_category": self._categorize_energy(user_state.energy_level),
            "time_availability": self._categorize_time(user_state.available_time),
            "therapeutic_priority": self._determine_therapeutic_priority(user_state),
            "difficulty_preference": self._calculate_difficulty_preference(user_state),
            "motivation_level": self._assess_motivation(user_state)
        }
    
    def _categorize_energy(self, energy_level: int) -> str:
        """エラー"""
        if energy_level >= 4:
            return "high"
        elif energy_level >= 3:
            return "medium"
        else:
            return "low"
    
    def _categorize_time(self, available_time: int) -> str:
        """?"""
        if available_time >= 30:
            return "abundant"
        elif available_time >= 15:
            return "moderate"
        else:
            return "limited"
    
    def _determine_therapeutic_priority(self, user_state: UserState) -> str:
        """治療"""
        if user_state.current_state in ["APATHY", "INTEREST"]:
            return "engagement"  # エラー
        elif user_state.current_state == "ACTION":
            return "momentum"    # ?
        elif user_state.current_state == "CONTINUATION":
            return "consistency" # 一般
        else:  # HABITUATION
            return "mastery"     # ?
    
    def _calculate_difficulty_preference(self, user_state: UserState) -> float:
        """?"""
        base_difficulty = 2.0
        
        # エラー
        energy_modifier = (user_state.energy_level - 3) * 0.3
        
        # 気分
        mood_modifier = user_state.mood_trend * 0.5
        
        # ストーリー
        streak_modifier = min(user_state.streak_days * 0.1, 0.5)
        
        return max(1.0, min(5.0, base_difficulty + energy_modifier + mood_modifier + streak_modifier))
    
    def _assess_motivation(self, user_state: UserState) -> float:
        """モデル"""
        motivation = 0.5  # ?
        
        # ?
        state_modifiers = {
            "APATHY": -0.3,
            "INTEREST": 0.0,
            "ACTION": 0.2,
            "CONTINUATION": 0.1,
            "HABITUATION": 0.3
        }
        motivation += state_modifiers.get(user_state.current_state, 0.0)
        
        # 気分
        motivation += user_state.mood_trend * 0.3
        
        # ストーリー
        if user_state.streak_days > 0:
            motivation += min(user_state.streak_days * 0.05, 0.2)
        
        return max(0.0, min(1.0, motivation))
    
    def _score_tasks(self, user_state: UserState, state_analysis: Dict[str, Any]) -> List[tuple]:
        """タスク"""
        scored_tasks = []
        
        for task in self.task_pool:
            score = 0.0
            
            # 治療
            therapeutic_score = self._calculate_therapeutic_alignment(task, user_state)
            score += therapeutic_score * self.selection_weights["therapeutic_alignment"]
            
            # ユーザー
            state_match_score = self._calculate_state_match(task, state_analysis)
            score += state_match_score * self.selection_weights["user_state_match"]
            
            # ?
            difficulty_score = self._calculate_difficulty_balance(task, state_analysis)
            score += difficulty_score * self.selection_weights["difficulty_balance"]
            
            # ?
            variety_score = self._calculate_variety_bonus(task, user_state)
            score += variety_score * self.selection_weights["variety_bonus"]
            
            scored_tasks.append((task, score))
        
        return sorted(scored_tasks, key=lambda x: x[1], reverse=True)
    
    def _calculate_therapeutic_alignment(self, task: DailyTrioTask, user_state: UserState) -> float:
        """治療"""
        if task.therapeutic_focus in user_state.therapeutic_goals:
            return 1.0
        elif task.category == TaskCategory.THERAPEUTIC:
            return 0.8
        else:
            return 0.5
    
    def _calculate_state_match(self, task: DailyTrioTask, state_analysis: Dict[str, Any]) -> float:
        """?"""
        score = 0.0
        
        # エラー
        energy_category = state_analysis["energy_category"]
        if energy_category == "high" and task.difficulty >= 3:
            score += 0.3
        elif energy_category == "medium" and 2 <= task.difficulty <= 3:
            score += 0.3
        elif energy_category == "low" and task.difficulty <= 2:
            score += 0.3
        
        # ?
        time_category = state_analysis["time_availability"]
        if time_category == "limited" and task.estimated_duration <= 5:
            score += 0.3
        elif time_category == "moderate" and task.estimated_duration <= 10:
            score += 0.3
        elif time_category == "abundant":
            score += 0.2
        
        # 治療
        therapeutic_priority = state_analysis["therapeutic_priority"]
        if therapeutic_priority == "engagement" and task.category == TaskCategory.THERAPEUTIC:
            score += 0.4
        elif therapeutic_priority == "momentum" and task.priority == TaskPriority.HIGH:
            score += 0.4
        elif therapeutic_priority == "consistency" and task.category == TaskCategory.HABIT:
            score += 0.4
        elif therapeutic_priority == "mastery" and task.difficulty >= 3:
            score += 0.4
        
        return min(1.0, score)
    
    def _calculate_difficulty_balance(self, task: DailyTrioTask, state_analysis: Dict[str, Any]) -> float:
        """?"""
        preferred_difficulty = state_analysis["difficulty_preference"]
        difficulty_diff = abs(task.difficulty - preferred_difficulty)
        
        # ?
        return max(0.0, 1.0 - (difficulty_diff / 4.0))
    
    def _calculate_variety_bonus(self, task: DailyTrioTask, user_state: UserState) -> float:
        """?"""
        # 実装
        # こ
        return 0.5
    
    def _select_optimal_trio(self, scored_tasks: List[tuple], user_state: UserState) -> List[DailyTrioTask]:
        """?3つ"""
        selected = []
        used_categories = set()
        total_time = 0
        max_time = min(user_state.available_time, 30)  # ?30?
        
        for task, score in scored_tasks:
            if len(selected) >= 3:
                break
            
            # ?
            if total_time + task.estimated_duration > max_time:
                continue
            
            # カスタム2つ
            category_count = sum(1 for t in selected if t.category == task.category)
            if category_count >= 2:
                continue
            
            selected.append(task)
            used_categories.add(task.category)
            total_time += task.estimated_duration
        
        # 3つ
        while len(selected) < 3 and total_time < max_time:
            for task, score in scored_tasks:
                if task not in selected and total_time + task.estimated_duration <= max_time:
                    selected.append(task)
                    total_time += task.estimated_duration
                    break
            else:
                break
        
        return selected
    
    def _generate_selection_reasoning(self, selected_tasks: List[DailyTrioTask], user_state: UserState) -> str:
        """?"""
        reasons = []
        
        # エラー
        if user_state.energy_level >= 4:
            reasons.append("?")
        elif user_state.energy_level <= 2:
            reasons.append("?")
        
        # 治療
        therapeutic_tasks = [t for t in selected_tasks if t.category == TaskCategory.THERAPEUTIC]
        if therapeutic_tasks:
            reasons.append(f"治療{therapeutic_tasks[0].therapeutic_focus}?")
        
        # ?
        total_time = sum(task.estimated_duration for task in selected_tasks)
        reasons.append(f"?{user_state.available_time}?{total_time}?")
        
        return "?".join(reasons) + "し"
    
    def _calculate_therapeutic_balance(self, selected_tasks: List[DailyTrioTask]) -> Dict[str, int]:
        """治療"""
        balance = {}
        for task in selected_tasks:
            focus = task.therapeutic_focus
            balance[focus] = balance.get(focus, 0) + 1
        return balance

# ?
daily_trio_engine = DailyTrioEngine()

# APIエラー

@app.post("/daily-trio/select", response_model=DailyTrioResponse)
async def select_daily_trio(user_state: UserState):
    """Daily Trio自動"""
    return await daily_trio_engine.select_daily_trio(user_state)

@app.get("/daily-trio/{user_id}")
async def get_daily_trio(user_id: str, date: Optional[str] = None):
    """Daily Trio?"""
    # 実装Daily Trioを
    # こ
    demo_user_state = UserState(
        user_id=user_id,
        current_state="ACTION",
        mood_trend=0.2,
        energy_level=3,
        available_time=20,
        therapeutic_goals=["Self-Discipline", "Communication"],
        completed_tasks_today=1,
        streak_days=5,
        adhd_assist_level=1.1
    )
    
    return await daily_trio_engine.select_daily_trio(demo_user_state)

@app.post("/daily-trio/{user_id}/complete/{task_id}")
async def complete_trio_task(user_id: str, task_id: str):
    """Daily Trioタスク"""
    # 実装XP?
    return {
        "success": True,
        "task_id": task_id,
        "xp_earned": 30,
        "micro_rewards": ["?", "?+1"],
        "completion_time": datetime.now().isoformat(),
        "next_task_available": True
    }

@app.get("/daily-trio/{user_id}/progress")
async def get_trio_progress(user_id: str):
    """Daily Trio?"""
    return {
        "user_id": user_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "completed_tasks": 2,
        "total_tasks": 3,
        "completion_rate": 0.67,
        "total_xp_earned": 65,
        "estimated_remaining_time": 5,
        "next_task_hint": "?Daily Trioを"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)