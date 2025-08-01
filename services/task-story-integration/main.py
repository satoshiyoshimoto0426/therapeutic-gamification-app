#!/usr/bin/env python3
"""
Task-Story Integration Service

ストーリーreal_task_id/habit_tagのMandala?
タスク

Requirements: 1.4, 5.5
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import json
import uuid
import sys
import os
import time

# Optional httpx import for external API calls
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available, external API calls will be mocked")

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from interfaces.core_types import (
    ChapterType, TaskType, TaskStatus, CrystalAttribute
)

app = FastAPI(title="Task-Story Integration Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Integration Models
class StoryChoiceHook(BaseModel):
    """ストーリー"""
    choice_id: str
    choice_text: str
    real_task_id: Optional[str] = None
    habit_tag: Optional[str] = None
    task_template: Optional[Dict[str, Any]] = None
    mandala_impact: Optional[Dict[str, Any]] = None
    therapeutic_weight: float = 1.0

class TaskCompletionHook(BaseModel):
    """タスク"""
    task_id: str
    uid: str
    completion_data: Dict[str, Any]
    story_progression_trigger: bool = True
    mandala_update_trigger: bool = True
    xp_calculation_data: Dict[str, Any] = {}

class MandalaReflectionData(BaseModel):
    """Mandala?"""
    uid: str
    story_choices: List[StoryChoiceHook]
    completion_date: datetime
    target_date: datetime  # ?
    chapter_context: ChapterType
    therapeutic_focus: List[str] = []

class TaskStorySync(BaseModel):
    """タスク-ストーリー"""
    uid: str
    task_id: str
    story_edge_id: Optional[str] = None
    habit_tag: Optional[str] = None
    sync_status: str = "pending"  # pending, synced, failed
    last_sync_attempt: Optional[datetime] = None

# Service Integration Layer
class ServiceIntegration:
    """?"""
    
    def __init__(self):
        self.task_service_url = os.getenv("TASK_SERVICE_URL", "http://localhost:8001")
        self.story_service_url = os.getenv("STORY_SERVICE_URL", "http://localhost:8006")
        self.mandala_service_url = os.getenv("MANDALA_SERVICE_URL", "http://localhost:8003")
        self.core_game_service_url = os.getenv("CORE_GAME_SERVICE_URL", "http://localhost:8002")
    
    async def create_task_from_story_choice(
        self, 
        uid: str, 
        choice_hook: StoryChoiceHook
    ) -> Dict[str, Any]:
        """ストーリー"""
        
        # real_task_idもtask_templateも
        if not choice_hook.real_task_id and not choice_hook.task_template and not choice_hook.choice_text:
            return {"success": False, "error": "No task creation data provided"}
        
        # ?real_task_idが
        if choice_hook.real_task_id:
            existing_task_result = await self._update_existing_task(uid, choice_hook)
            if existing_task_result["success"]:
                return existing_task_result
        
        # タスク
        task_data = self._build_task_from_choice(choice_hook)
        
        # タスク
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.task_service_url}/tasks/{uid}/create",
                        json=task_data,
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "task_id": result.get("task_id"),
                            "task_data": task_data,
                            "choice_hook": choice_hook,
                            "integration_type": "story_choice_to_task"
                        }
            except Exception as e:
                print(f"Task creation failed: {e}")
        
        # ?: モデル
        return {
            "success": True,
            "task_id": str(uuid.uuid4()),
            "task_data": task_data,
            "choice_hook": choice_hook,
            "mock": True,
            "integration_type": "story_choice_to_task"
        }
    
    async def _update_existing_task(
        self, 
        uid: str, 
        choice_hook: StoryChoiceHook
    ) -> Dict[str, Any]:
        """?"""
        
        if HTTPX_AVAILABLE:
            try:
                # ?
                async with httpx.AsyncClient(timeout=10.0) as client:
                    get_response = await client.get(
                        f"{self.task_service_url}/tasks/{uid}/{choice_hook.real_task_id}",
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if get_response.status_code == 200:
                        task_data = get_response.json()
                        
                        # ストーリー
                        update_data = {
                            "linked_story_edge": choice_hook.choice_id,
                            "notes": f"ストーリー{choice_hook.choice_text}?"
                        }
                        
                        # habit_tagが
                        if choice_hook.habit_tag:
                            update_data["habit_tag"] = choice_hook.habit_tag
                        
                        # タスク
                        update_response = await client.put(
                            f"{self.task_service_url}/tasks/{uid}/{choice_hook.real_task_id}",
                            json=update_data,
                            headers={"Authorization": "Bearer mock_token"}
                        )
                        
                        if update_response.status_code == 200:
                            updated_task = update_response.json()
                            return {
                                "success": True,
                                "task_id": choice_hook.real_task_id,
                                "task_data": updated_task,
                                "choice_hook": choice_hook,
                                "integration_type": "story_choice_to_existing_task",
                                "updated": True
                            }
            except Exception as e:
                print(f"Existing task update failed: {e}")
        
        return {"success": False, "error": "Failed to update existing task"}
    
    def _build_task_from_choice(self, choice_hook: StoryChoiceHook) -> Dict[str, Any]:
        """?"""
        
        if choice_hook.task_template:
            # ?
            task_data = choice_hook.task_template.copy()
            task_data["linked_story_edge"] = choice_hook.choice_id
            if choice_hook.habit_tag:
                task_data["habit_tag"] = choice_hook.habit_tag
            return task_data
        
        # ?
        choice_text = choice_hook.choice_text.lower()
        
        # 基本
        base_task_data = {
            "linked_story_edge": choice_hook.choice_id,
            "habit_tag": choice_hook.habit_tag,
            "tags": ["story_generated", "therapeutic"],
            "therapeutic_weight": choice_hook.therapeutic_weight
        }
        
        if any(word in choice_text for word in ["挑", "?", "?", "学", "ストーリー", "?"]):
            task_data = {
                "task_type": "SKILL_UP",
                "title": f"勇: {choice_hook.choice_text}",
                "description": f"?{choice_hook.choice_text}?",
                "difficulty": "MEDIUM",
                "priority": "HIGH",
                "estimated_duration": 45,
                "primary_crystal_attribute": "CURIOSITY",
                "secondary_crystal_attributes": ["COURAGE"],
                **base_task_data
            }
        
        elif any(word in choice_text for word in ["つ", "?", "コア", "?", "?", "?"]):
            task_data = {
                "task_type": "SOCIAL",
                "title": f"?: {choice_hook.choice_text}",
                "description": f"?",
                "difficulty": "EASY",
                "priority": "MEDIUM",
                "estimated_duration": 20,
                "primary_crystal_attribute": "EMPATHY",
                "secondary_crystal_attributes": ["COMMUNICATION"],
                **base_task_data
            }
        
        elif any(word in choice_text for word in ["?", "?", "?", "?", "?", "?"]):
            task_data = {
                "task_type": "ROUTINE",
                "title": f"勇: {choice_hook.choice_text}",
                "description": f"?",
                "difficulty": "EASY",
                "priority": "MEDIUM",
                "estimated_duration": 15,
                "primary_crystal_attribute": "SELF_DISCIPLINE",
                "secondary_crystal_attributes": ["RESILIENCE"],
                "is_recurring": True,
                "recurrence_pattern": "daily",
                **base_task_data
            }
        
        elif any(word in choice_text for word in ["勇", "?", "?", "や", "挑", "?"]):
            task_data = {
                "task_type": "ONE_SHOT",
                "title": f"勇: {choice_hook.choice_text}",
                "description": f"?{choice_hook.choice_text}?",
                "difficulty": "MEDIUM",
                "priority": "HIGH",
                "estimated_duration": 30,
                "primary_crystal_attribute": "COURAGE",
                "secondary_crystal_attributes": ["SELF_DISCIPLINE"],
                **base_task_data
            }
        
        else:
            # デフォルト
            task_data = {
                "task_type": "ONE_SHOT",
                "title": f"物語: {choice_hook.choice_text}",
                "description": f"?{choice_hook.choice_text}?",
                "difficulty": "EASY",
                "priority": "MEDIUM",
                "estimated_duration": 25,
                "primary_crystal_attribute": "WISDOM",
                "secondary_crystal_attributes": ["RESILIENCE"],
                **base_task_data
            }
        
        # Mandala?
        if choice_hook.mandala_impact:
            task_data["mandala_impact"] = choice_hook.mandala_impact
        
        return task_data
    
    async def update_mandala_from_story_choices(
        self, 
        reflection_data: MandalaReflectionData
    ) -> Dict[str, Any]:
        """ストーリーMandalaを"""
        
        mandala_updates = []
        generated_tasks = []
        
        for choice_hook in reflection_data.story_choices:
            # Mandala?
            if choice_hook.mandala_impact:
                mandala_updates.append({
                    "choice_id": choice_hook.choice_id,
                    "choice_text": choice_hook.choice_text,
                    "impact": choice_hook.mandala_impact,
                    "therapeutic_weight": choice_hook.therapeutic_weight,
                    "target_date": reflection_data.target_date.isoformat()
                })
            
            # ?
            if choice_hook.real_task_id or choice_hook.task_template:
                task_result = await self.create_task_from_story_choice(
                    reflection_data.uid, 
                    choice_hook
                )
                if task_result["success"]:
                    generated_tasks.append(task_result)
        
        # Mandala?
        mandala_result = {"success": False}
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.mandala_service_url}/mandala/{reflection_data.uid}/reflect-story-choices",
                        json={
                            "target_date": reflection_data.target_date.isoformat(),
                            "chapter_context": reflection_data.chapter_context.value,
                            "story_updates": mandala_updates,
                            "therapeutic_focus": reflection_data.therapeutic_focus,
                            "generated_tasks": [task["task_id"] for task in generated_tasks if "task_id" in task]
                        },
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        mandala_result = response.json()
            except Exception as e:
                print(f"Mandala update failed: {e}")
        
        # ?
        if not mandala_result["success"]:
            mandala_result = {
                "success": True,
                "updated_cells": len(mandala_updates),
                "target_date": reflection_data.target_date.isoformat(),
                "mock": True,
                "cells_affected": self._generate_mock_mandala_cells(mandala_updates)
            }
        
        return {
            **mandala_result,
            "story_choices_processed": len(reflection_data.story_choices),
            "mandala_updates": mandala_updates,
            "generated_tasks": generated_tasks,
            "reflection_completion_date": reflection_data.completion_date.isoformat()
        }
    
    def _generate_mock_mandala_cells(self, mandala_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """モデルMandala?"""
        cells_affected = []
        
        for update in mandala_updates:
            # ?
            choice_text = update.get("choice_text", "")
            
            if "挑" in choice_text or "?" in choice_text:
                cell_position = (2, 4)  # ?
                attribute = "CURIOSITY"
            elif "つ" in choice_text or "コア" in choice_text:
                cell_position = (4, 6)  # コア
                attribute = "COMMUNICATION"
            elif "?" in choice_text or "?" in choice_text:
                cell_position = (1, 1)  # 自動
                attribute = "SELF_DISCIPLINE"
            elif "勇" in choice_text or "?" in choice_text:
                cell_position = (6, 2)  # 勇
                attribute = "COURAGE"
            else:
                cell_position = (4, 4)  # ?
                attribute = "WISDOM"
            
            cells_affected.append({
                "cell_position": cell_position,
                "attribute": attribute,
                "impact_type": "story_choice_reflection",
                "impact_strength": update.get("therapeutic_weight", 1.0),
                "choice_id": update.get("choice_id"),
                "unlocked": True
            })
        
        return cells_affected
    
    async def sync_task_completion_with_story(
        self, 
        completion_hook: TaskCompletionHook
    ) -> Dict[str, Any]:
        """タスク"""
        
        sync_results = []
        
        # タスク
        task_info = await self._get_task_info(completion_hook.uid, completion_hook.task_id)
        
        # ストーリー
        if completion_hook.story_progression_trigger:
            story_result = await self._trigger_story_progression(completion_hook, task_info)
            sync_results.append({"type": "story_progression", "result": story_result})
        
        # Mandala?
        if completion_hook.mandala_update_trigger:
            mandala_result = await self._trigger_mandala_update(completion_hook, task_info)
            sync_results.append({"type": "mandala_update", "result": mandala_result})
        
        # XP計算
        xp_result = await self._trigger_xp_calculation(completion_hook, task_info)
        sync_results.append({"type": "xp_calculation", "result": xp_result})
        
        # ?
        crystal_result = await self._trigger_crystal_growth(completion_hook, task_info)
        sync_results.append({"type": "crystal_growth", "result": crystal_result})
        
        # 共有
        resonance_result = await self._check_resonance_events(completion_hook, task_info)
        if resonance_result["triggered"]:
            sync_results.append({"type": "resonance_event", "result": resonance_result})
        
        # ?
        next_choices_result = await self._generate_next_story_choices(completion_hook, task_info)
        sync_results.append({"type": "next_choices", "result": next_choices_result})
        
        return {
            "success": True,
            "sync_results": sync_results,
            "task_id": completion_hook.task_id,
            "uid": completion_hook.uid,
            "task_info": task_info,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_task_info(self, uid: str, task_id: str) -> Dict[str, Any]:
        """タスク"""
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{self.task_service_url}/tasks/{uid}/{task_id}",
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"Failed to get task info: {e}")
        
        # ?
        return {
            "task_id": task_id,
            "uid": uid,
            "task_type": "ONE_SHOT",
            "title": "Unknown Task",
            "difficulty": "MEDIUM",
            "primary_crystal_attribute": "WISDOM",
            "mock": True
        }
    
    async def _trigger_story_progression(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ストーリー"""
        
        # ストーリー
        story_context = {
            "uid": completion_hook.uid,
            "task_completion": {
                "task_id": completion_hook.task_id,
                "task_type": task_info.get("task_type", "ONE_SHOT"),
                "task_title": task_info.get("title", "Unknown Task"),
                "difficulty": task_info.get("difficulty", "MEDIUM"),
                "completion_data": completion_hook.completion_data,
                "linked_story_edge": task_info.get("linked_story_edge"),
                "habit_tag": task_info.get("habit_tag"),
                "primary_crystal_attribute": task_info.get("primary_crystal_attribute")
            },
            "user_context": {
                "mood_score": completion_hook.completion_data.get("mood_score", 3),
                "xp_calculation": completion_hook.xp_calculation_data
            },
            "generation_type": "task_completion_reflection",
            "therapeutic_focus": ["achievement", "progress_recognition", "next_steps"]
        }
        
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.story_service_url}/ai/story/v2/generate",
                        json=story_context,
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        story_result = response.json()
                        return {
                            "success": True,
                            "story_generated": True,
                            "story_content": story_result.get("generated_content"),
                            "next_choices": story_result.get("next_choices", []),
                            "therapeutic_tags": story_result.get("therapeutic_tags", []),
                            "generation_time_ms": story_result.get("generation_time_ms", 0)
                        }
            except Exception as e:
                print(f"Story progression failed: {e}")
        
        # ?: タスク
        return self._generate_fallback_story(completion_hook, task_info)
    
    def _generate_fallback_story(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """? - ?"""
        
        task_title = task_info.get("title", "?")
        mood_score = completion_hook.completion_data.get("mood_score", 3)
        
        if mood_score >= 4:
            story_content = f"""?{task_title}?

?

?"""
            next_choices = [
                {"choice_id": "continue_momentum", "choice_text": "こ"},
                {"choice_id": "celebrate", "choice_text": "レベル"},
                {"choice_id": "reflect", "choice_text": "?"}
            ]
        elif mood_score <= 2:
            story_content = f"""?{task_title}?

?

?"""
            next_choices = [
                {"choice_id": "rest", "choice_text": "?"},
                {"choice_id": "gentle_next", "choice_text": "無"},
                {"choice_id": "support", "choice_text": "?"}
            ]
        else:
            story_content = f"""?{task_title}?

?...?
あ

60?"""
            next_choices = [
                {"choice_id": "steady_progress", "choice_text": "?"},
                {"choice_id": "skill_up", "choice_text": "?"},
                {"choice_id": "connect", "choice_text": "?"}
            ]
        
        return {
            "success": True,
            "story_generated": True,
            "story_content": story_content,
            "next_choices": next_choices,
            "therapeutic_tags": ["achievement", "progress", "encouragement"],
            "fallback_used": True
        }
    
    async def _trigger_mandala_update(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mandala?"""
        
        # Mandala?
        mandala_update_data = {
            "task_id": completion_hook.task_id,
            "completion_data": completion_hook.completion_data,
            "task_info": {
                "task_type": task_info.get("task_type"),
                "difficulty": task_info.get("difficulty"),
                "primary_crystal_attribute": task_info.get("primary_crystal_attribute"),
                "secondary_crystal_attributes": task_info.get("secondary_crystal_attributes", []),
                "mandala_cell_id": task_info.get("mandala_cell_id")
            },
            "completion_timestamp": datetime.utcnow().isoformat()
        }
        
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.mandala_service_url}/mandala/{completion_hook.uid}/task-completion",
                        json=mandala_update_data,
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"Mandala update failed: {e}")
        
        # ?: モデルMandala?
        return self._generate_mock_mandala_update(completion_hook, task_info)
    
    def _generate_mock_mandala_update(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """モデルMandala?"""
        
        primary_attribute = task_info.get("primary_crystal_attribute", "WISDOM")
        task_type = task_info.get("task_type", "ONE_SHOT")
        mood_score = completion_hook.completion_data.get("mood_score", 3)
        
        # ?
        attribute_positions = {
            "SELF_DISCIPLINE": (1, 1),
            "EMPATHY": (1, 7),
            "RESILIENCE": (7, 1),
            "CURIOSITY": (2, 4),
            "COMMUNICATION": (4, 6),
            "CREATIVITY": (6, 6),
            "COURAGE": (6, 2),
            "WISDOM": (4, 4)
        }
        
        cell_position = attribute_positions.get(primary_attribute, (4, 4))
        
        # ?
        base_progress = 10
        if task_type == "ROUTINE":
            base_progress = 5
        elif task_type == "SKILL_UP":
            base_progress = 15
        elif task_type == "SOCIAL":
            base_progress = 12
        
        # 気分
        mood_multiplier = 0.5 + (mood_score / 5.0)
        final_progress = int(base_progress * mood_multiplier)
        
        return {
            "success": True,
            "cells_updated": 1,
            "updated_cells": [
                {
                    "cell_position": cell_position,
                    "attribute": primary_attribute,
                    "progress_added": final_progress,
                    "new_progress": min(100, 45 + final_progress),  # ?
                    "unlocked": True
                }
            ],
            "mock": True
        }
    
    async def _trigger_xp_calculation(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """XP計算"""
        
        xp_calculation_data = {
            "uid": completion_hook.uid,
            "task_id": completion_hook.task_id,
            "completion_data": completion_hook.completion_data,
            "task_info": task_info,
            "calculation_context": completion_hook.xp_calculation_data
        }
        
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.core_game_service_url}/xp/calculate",
                        json=xp_calculation_data,
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"XP calculation failed: {e}")
        
        # ?: XP計算
        return self._calculate_fallback_xp(completion_hook, task_info)
    
    def _calculate_fallback_xp(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """?XP計算"""
        
        # 基本XP
        difficulty_xp = {
            "EASY": 20,
            "MEDIUM": 35,
            "HARD": 50,
            "VERY_HARD": 70
        }
        
        base_xp = difficulty_xp.get(task_info.get("difficulty", "MEDIUM"), 35)
        
        # 気分
        mood_score = completion_hook.completion_data.get("mood_score", 3)
        mood_coefficient = 0.8 + (mood_score - 1) * 0.1  # 0.8-1.2の
        
        # ADHD支援
        adhd_assist = 1.0
        if completion_hook.completion_data.get("pomodoro_used", False):
            adhd_assist = 1.2
        
        final_xp = int(base_xp * mood_coefficient * adhd_assist)
        
        return {
            "success": True,
            "xp_earned": final_xp,
            "calculation_breakdown": {
                "base_xp": base_xp,
                "mood_coefficient": mood_coefficient,
                "adhd_assist": adhd_assist,
                "final_xp": final_xp
            },
            "mock": True
        }
    
    async def _trigger_crystal_growth(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """?"""
        
        primary_attribute = task_info.get("primary_crystal_attribute")
        secondary_attributes = task_info.get("secondary_crystal_attributes", [])
        
        if not primary_attribute:
            return {"success": True, "growth_events": [], "message": "No crystal attributes"}
        
        growth_events = []
        
        # ?
        growth_events.append({
            "attribute": primary_attribute,
            "growth_amount": 15,
            "growth_type": "primary_task_completion"
        })
        
        # ?
        for attr in secondary_attributes:
            growth_events.append({
                "attribute": attr,
                "growth_amount": 8,
                "growth_type": "secondary_task_completion"
            })
        
        return {
            "success": True,
            "growth_events": growth_events,
            "total_attributes_affected": len(growth_events)
        }
    
    async def _check_resonance_events(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """共有"""
        
        if HTTPX_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{self.core_game_service_url}/resonance/{completion_hook.uid}/check",
                        headers={"Authorization": "Bearer mock_token"}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"Resonance check failed: {e}")
        
        # ?: ?
        return {
            "triggered": False,
            "reason": "No significant level difference detected",
            "mock": True
        }
    
    async def _generate_next_story_choices(
        self, 
        completion_hook: TaskCompletionHook,
        task_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """?"""
        
        task_type = task_info.get("task_type", "ONE_SHOT")
        primary_attribute = task_info.get("primary_crystal_attribute", "WISDOM")
        mood_score = completion_hook.completion_data.get("mood_score", 3)
        
        # タスク
        choices = []
        
        if task_type == "ROUTINE":
            choices = [
                {
                    "choice_id": "continue_routine",
                    "choice_text": "こ",
                    "habit_tag": "routine_continuation",
                    "therapeutic_weight": 1.2
                },
                {
                    "choice_id": "expand_routine",
                    "choice_text": "?",
                    "habit_tag": "routine_expansion",
                    "therapeutic_weight": 1.5
                }
            ]
        elif task_type == "SKILL_UP":
            choices = [
                {
                    "choice_id": "practice_more",
                    "choice_text": "さ",
                    "habit_tag": "skill_practice",
                    "therapeutic_weight": 1.3
                },
                {
                    "choice_id": "teach_others",
                    "choice_text": "?",
                    "habit_tag": "knowledge_sharing",
                    "therapeutic_weight": 1.4
                }
            ]
        elif task_type == "SOCIAL":
            choices = [
                {
                    "choice_id": "deepen_connection",
                    "choice_text": "?",
                    "habit_tag": "social_deepening",
                    "therapeutic_weight": 1.3
                },
                {
                    "choice_id": "expand_network",
                    "choice_text": "?",
                    "habit_tag": "network_expansion",
                    "therapeutic_weight": 1.2
                }
            ]
        else:
            choices = [
                {
                    "choice_id": "reflect_achievement",
                    "choice_text": "?",
                    "habit_tag": "reflection",
                    "therapeutic_weight": 1.0
                },
                {
                    "choice_id": "plan_next",
                    "choice_text": "?",
                    "habit_tag": "goal_setting",
                    "therapeutic_weight": 1.1
                }
            ]
        
        # 気分
        if mood_score >= 4:
            choices.append({
                "choice_id": "celebrate",
                "choice_text": "成",
                "habit_tag": "celebration",
                "therapeutic_weight": 1.0
            })
        elif mood_score <= 2:
            choices.append({
                "choice_id": "self_care",
                "choice_text": "自動",
                "habit_tag": "self_care",
                "therapeutic_weight": 1.1
            })
        
        return {
            "success": True,
            "next_choices": choices,
            "choice_context": {
                "task_type": task_type,
                "primary_attribute": primary_attribute,
                "mood_score": mood_score
            }
        }

# Initialize service integration
service_integration = ServiceIntegration()

# Mock database for development
class IntegrationDatabase:
    def __init__(self):
        self.story_choice_hooks: Dict[str, List[StoryChoiceHook]] = {}  # uid -> hooks
        self.task_story_syncs: Dict[str, TaskStorySync] = {}  # task_id -> sync
        self.mandala_reflections: Dict[str, List[MandalaReflectionData]] = {}  # uid -> reflections

integration_db = IntegrationDatabase()

# Authentication
async def verify_jwt_token() -> dict:
    """Mock JWT verification for testing purposes"""
    return {"uid": "test_user_123", "email": "test@example.com"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-story-integration"}

# Story Choice to Task Integration
@app.post("/integration/story-choice-to-task")
async def convert_story_choice_to_task(
    choice_data: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """ストーリー"""
    
    uid = choice_data.get("uid")
    if not uid:
        raise HTTPException(status_code=400, detail="User ID required")
    
    # ストーリー
    choice_hook = StoryChoiceHook(
        choice_id=choice_data.get("choice_id", str(uuid.uuid4())),
        choice_text=choice_data["choice_text"],
        real_task_id=choice_data.get("real_task_id"),
        habit_tag=choice_data.get("habit_tag"),
        task_template=choice_data.get("task_template"),
        mandala_impact=choice_data.get("mandala_impact"),
        therapeutic_weight=choice_data.get("therapeutic_weight", 1.0)
    )
    
    # タスク
    task_result = await service_integration.create_task_from_story_choice(uid, choice_hook)
    
    # ?
    if uid not in integration_db.story_choice_hooks:
        integration_db.story_choice_hooks[uid] = []
    integration_db.story_choice_hooks[uid].append(choice_hook)
    
    # バリデーションMandala?
    if choice_hook.mandala_impact:
        background_tasks.add_task(
            schedule_mandala_reflection,
            uid,
            [choice_hook],
            choice_data.get("chapter_context", ChapterType.SELF_DISCIPLINE)
        )
    
    return {
        "success": task_result["success"],
        "task_creation": task_result,
        "choice_hook": choice_hook,
        "integration_type": "story_to_task",
        "mandala_scheduled": bool(choice_hook.mandala_impact)
    }

# Task Completion to Story Integration
@app.post("/integration/task-completion-sync")
async def sync_task_completion(
    completion_data: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """タスク"""
    
    uid = completion_data.get("uid")
    task_id = completion_data.get("task_id")
    
    if not uid or not task_id:
        raise HTTPException(status_code=400, detail="User ID and Task ID required")
    
    # タスク
    completion_hook = TaskCompletionHook(
        task_id=task_id,
        uid=uid,
        completion_data=completion_data.get("completion_data", {}),
        story_progression_trigger=completion_data.get("story_progression_trigger", True),
        mandala_update_trigger=completion_data.get("mandala_update_trigger", True),
        xp_calculation_data=completion_data.get("xp_calculation_data", {})
    )
    
    # ?
    sync_result = await service_integration.sync_task_completion_with_story(completion_hook)
    
    # ?
    task_sync = TaskStorySync(
        uid=uid,
        task_id=task_id,
        story_edge_id=completion_data.get("story_edge_id"),
        habit_tag=completion_data.get("habit_tag"),
        sync_status="synced" if sync_result["success"] else "failed",
        last_sync_attempt=datetime.utcnow()
    )
    integration_db.task_story_syncs[task_id] = task_sync
    
    return {
        "success": sync_result["success"],
        "sync_result": sync_result,
        "task_sync": task_sync,
        "integration_type": "task_to_story"
    }

# Mandala Reflection Integration
@app.post("/integration/mandala-reflection")
async def reflect_story_choices_to_mandala(
    reflection_request: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token)
):
    """ストーリーMandalaに"""
    
    uid = reflection_request.get("uid")
    if not uid:
        raise HTTPException(status_code=400, detail="User ID required")
    
    # ?
    story_choices = []
    for choice_data in reflection_request.get("story_choices", []):
        choice_hook = StoryChoiceHook(**choice_data)
        story_choices.append(choice_hook)
    
    reflection_data = MandalaReflectionData(
        uid=uid,
        story_choices=story_choices,
        completion_date=datetime.utcnow(),
        target_date=datetime.utcnow() + timedelta(days=1),
        chapter_context=ChapterType(reflection_request.get("chapter_context", "self_discipline")),
        therapeutic_focus=reflection_request.get("therapeutic_focus", [])
    )
    
    # Mandala?
    update_result = await service_integration.update_mandala_from_story_choices(reflection_data)
    
    # ?
    if uid not in integration_db.mandala_reflections:
        integration_db.mandala_reflections[uid] = []
    integration_db.mandala_reflections[uid].append(reflection_data)
    
    return {
        "success": update_result.get("success", True),
        "mandala_update": update_result,
        "reflection_data": reflection_data,
        "integration_type": "story_to_mandala"
    }

# Real-time Hook Processing
@app.post("/integration/process-real-time-hooks")
async def process_real_time_hooks(
    hook_data: Dict[str, Any],
    current_user: dict = Depends(verify_jwt_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """リスト21:30ストーリー"""
    
    uid = hook_data.get("uid")
    if not uid:
        raise HTTPException(status_code=400, detail="User ID required")
    
    # ?
    user_choices = integration_db.story_choice_hooks.get(uid, [])
    
    # ?
    tomorrow_tasks = []
    for choice_hook in user_choices:
        if choice_hook.real_task_id or choice_hook.task_template:
            task_result = await service_integration.create_task_from_story_choice(uid, choice_hook)
            if task_result["success"]:
                tomorrow_tasks.append(task_result)
    
    # Mandala?
    if user_choices:
        background_tasks.add_task(
            schedule_mandala_reflection,
            uid,
            user_choices,
            hook_data.get("chapter_context", ChapterType.SELF_DISCIPLINE)
        )
    
    return {
        "success": True,
        "processed_choices": len(user_choices),
        "generated_tasks": len(tomorrow_tasks),
        "tomorrow_tasks": tomorrow_tasks,
        "mandala_reflection_scheduled": len(user_choices) > 0,
        "processing_time": datetime.utcnow().isoformat()
    }

# Background Tasks
async def schedule_mandala_reflection(
    uid: str, 
    story_choices: List[StoryChoiceHook], 
    chapter_context: ChapterType
):
    """Mandala?"""
    
    reflection_data = MandalaReflectionData(
        uid=uid,
        story_choices=story_choices,
        completion_date=datetime.utcnow(),
        target_date=datetime.utcnow() + timedelta(days=1),
        chapter_context=chapter_context,
        therapeutic_focus=[]
    )
    
    # Mandala?
    await service_integration.update_mandala_from_story_choices(reflection_data)
    
    # ?
    if uid not in integration_db.mandala_reflections:
        integration_db.mandala_reflections[uid] = []
    integration_db.mandala_reflections[uid].append(reflection_data)

# Status and Analytics
@app.get("/integration/status/{uid}")
async def get_integration_status(
    uid: str,
    current_user: dict = Depends(verify_jwt_token)
):
    """?"""
    
    if current_user["uid"] != uid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_hooks = integration_db.story_choice_hooks.get(uid, [])
    user_syncs = [sync for sync in integration_db.task_story_syncs.values() if sync.uid == uid]
    user_reflections = integration_db.mandala_reflections.get(uid, [])
    
    return {
        "uid": uid,
        "story_choice_hooks": len(user_hooks),
        "task_story_syncs": len(user_syncs),
        "mandala_reflections": len(user_reflections),
        "recent_hooks": user_hooks[-5:] if user_hooks else [],
        "recent_syncs": user_syncs[-5:] if user_syncs else [],
        "recent_reflections": user_reflections[-3:] if user_reflections else [],
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/integration/analytics")
async def get_integration_analytics(
    current_user: dict = Depends(verify_jwt_token)
):
    """?"""
    
    total_hooks = sum(len(hooks) for hooks in integration_db.story_choice_hooks.values())
    total_syncs = len(integration_db.task_story_syncs)
    total_reflections = sum(len(refs) for refs in integration_db.mandala_reflections.values())
    
    successful_syncs = len([sync for sync in integration_db.task_story_syncs.values() if sync.sync_status == "synced"])
    sync_success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
    
    return {
        "total_story_choice_hooks": total_hooks,
        "total_task_story_syncs": total_syncs,
        "total_mandala_reflections": total_reflections,
        "sync_success_rate": round(sync_success_rate, 2),
        "active_users": len(integration_db.story_choice_hooks),
        "integration_health": "healthy" if sync_success_rate > 80 else "needs_attention"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)