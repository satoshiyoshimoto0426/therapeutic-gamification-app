# ADHD Support Module Service
# Pomodoro timer, hyperfocus detection, daily buffer, UI constraints

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field
import uuid
import asyncio
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from interfaces.core_types import Task, TaskType, TaskStatus

# Mock Firestore for development
class MockFirestore:
    def __init__(self):
        self.data = {}
    
    def collection(self, name):
        if name not in self.data:
            self.data[name] = {}
        return MockCollection(self.data[name])

class MockCollection:
    def __init__(self, data):
        self.data = data
    
    def document(self, doc_id):
        return MockDocument(self.data, doc_id)

class MockDocument:
    def __init__(self, data, doc_id):
        self.data = data
        self.doc_id = doc_id
    
    def get(self):
        return MockDocSnapshot(self.data.get(self.doc_id))
    
    def set(self, data):
        self.data[self.doc_id] = data
    
    def update(self, data):
        if self.doc_id in self.data:
            self.data[self.doc_id].update(data)

class MockDocSnapshot:
    def __init__(self, data):
        self._data = data
    
    def exists(self):
        return self._data is not None
    
    def to_dict(self):
        return self._data or {}

app = FastAPI(title="ADHD Support Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
db = MockFirestore()

# Mock JWT verification
async def verify_jwt_token() -> dict:
    return {"uid": "test_user_123", "email": "test@example.com"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "adhd-support"}

# Pomodoro Timer Implementation
class PomodoroTimer:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.work_duration = 25 * 60  # 25 minutes
        self.short_break_duration = 5 * 60  # 5 minutes
        self.long_break_duration = 15 * 60  # 15 minutes
        self.cycles_before_long_break = 4
    
    async def start_cycle(self) -> Dict:
        """Start a new Pomodoro cycle"""
        cycle_id = str(uuid.uuid4())
        cycle_data = {
            "cycle_id": cycle_id,
            "user_id": self.user_id,
            "current_phase": "work",
            "phase_duration": self.work_duration,
            "cycle_count": 1,
            "is_active": True,
            "start_time": datetime.utcnow(),
            "paused_at": None
        }
        
        # Save to database
        db.collection("pomodoro_cycles").document(cycle_id).set(cycle_data)
        
        return cycle_data
    
    async def complete_phase(self, cycle_id: str) -> Dict:
        """Complete current phase and transition to next"""
        doc = db.collection("pomodoro_cycles").document(cycle_id).get()
        if not doc.exists():
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        cycle_data = doc.to_dict()
        
        if cycle_data["current_phase"] == "work":
            # Transition to break
            if cycle_data["cycle_count"] % self.cycles_before_long_break == 0:
                cycle_data["current_phase"] = "long_break"
                cycle_data["phase_duration"] = self.long_break_duration
            else:
                cycle_data["current_phase"] = "short_break"
                cycle_data["phase_duration"] = self.short_break_duration
        else:
            # Transition to work
            cycle_data["current_phase"] = "work"
            cycle_data["phase_duration"] = self.work_duration
            cycle_data["cycle_count"] += 1
        
        cycle_data["start_time"] = datetime.utcnow()
        db.collection("pomodoro_cycles").document(cycle_id).update(cycle_data)
        
        # Send LINE notification for phase transition
        notification_service = LINENotificationService()
        if cycle_data["current_phase"] == "work":
            await notification_service.send_pomodoro_notification({
                "user_id": cycle_data["user_id"],
                "message_type": "pomodoro_start",
                "duration": cycle_data["phase_duration"] // 60
            })
        else:
            await notification_service.send_pomodoro_notification({
                "user_id": cycle_data["user_id"],
                "message_type": "break_start",
                "duration": cycle_data["phase_duration"] // 60
            })
        
        return cycle_data
    
    async def pause_cycle(self, cycle_id: str) -> Dict:
        """Pause current cycle"""
        doc = db.collection("pomodoro_cycles").document(cycle_id).get()
        if not doc.exists():
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        cycle_data = doc.to_dict()
        cycle_data["is_active"] = False
        cycle_data["paused_at"] = datetime.utcnow()
        
        db.collection("pomodoro_cycles").document(cycle_id).update(cycle_data)
        return cycle_data
    
    async def resume_cycle(self, cycle_id: str) -> Dict:
        """Resume paused cycle"""
        doc = db.collection("pomodoro_cycles").document(cycle_id).get()
        if not doc.exists():
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        cycle_data = doc.to_dict()
        cycle_data["is_active"] = True
        cycle_data["paused_at"] = None
        
        db.collection("pomodoro_cycles").document(cycle_id).update(cycle_data)
        return cycle_data

# Hyperfocus Detection System
class HyperfocusDetector:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.hyperfocus_threshold = 60 * 60  # 60 minutes in seconds
    
    async def start_work_session(self, task_name: str) -> Dict:
        """Start tracking a work session"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": self.user_id,
            "task_name": task_name,
            "start_time": datetime.utcnow(),
            "is_active": True,
            "break_suggestions": 0,
            "continuous_work_time": 0
        }
        
        db.collection("work_sessions").document(session_id).set(session_data)
        return session_data
    
    async def check_hyperfocus_alert(self, session: Dict) -> bool:
        """Check if hyperfocus alert should trigger"""
        if not session["is_active"]:
            return False
        
        work_duration = (datetime.utcnow() - session["start_time"]).total_seconds()
        return work_duration >= self.hyperfocus_threshold
    
    async def generate_break_suggestion(self, suggestion_count: int) -> Dict:
        """Generate escalating break suggestions"""
        if suggestion_count == 0:
            return {
                "urgency_level": "gentle",
                "message": "?",
                "suggested_break_duration": 5
            }
        elif suggestion_count == 1:
            return {
                "urgency_level": "concerned",
                "message": "?",
                "suggested_break_duration": 10
            }
        else:
            return {
                "urgency_level": "firm",
                "message": "?",
                "suggested_break_duration": 15,
                "force_break": True
            }
    
    async def take_break(self, session_id: str) -> Dict:
        """Record that user took a break"""
        doc = db.collection("work_sessions").document(session_id).get()
        if not doc.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = doc.to_dict()
        session_data["continuous_work_time"] = 0
        session_data["break_suggestions"] = 0
        
        db.collection("work_sessions").document(session_id).update(session_data)
        
        return {
            "break_taken": True,
            "break_duration": 5 * 60,  # Minimum 5 minutes
            "session_reset": True
        }
    
    async def get_session(self, session_id: str) -> Dict:
        """Get work session data"""
        doc = db.collection("work_sessions").document(session_id).get()
        if not doc.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        
        return doc.to_dict()

# Daily Buffer Manager
class DailyBufferManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.max_extensions_per_day = 2
    
    async def get_daily_buffer_status(self) -> Dict:
        """Get current daily buffer status"""
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        
        doc = db.collection("daily_buffers").document(doc_id).get()
        
        if not doc.exists():
            # Initialize daily buffer
            buffer_data = {
                "user_id": self.user_id,
                "reset_date": today,
                "extensions_used": 0,
                "extensions_available": self.max_extensions_per_day
            }
            db.collection("daily_buffers").document(doc_id).set(buffer_data)
            return buffer_data
        
        return doc.to_dict()
    
    async def request_extension(self, task_id: str, hours: int = 2) -> Dict:
        """Request deadline extension"""
        buffer_status = await self.get_daily_buffer_status()
        
        if buffer_status["extensions_used"] >= self.max_extensions_per_day:
            return {
                "granted": False,
                "reason": "daily_limit_exceeded",
                "extensions_remaining": 0
            }
        
        # Grant extension
        new_due_date = datetime.utcnow() + timedelta(hours=hours)
        buffer_status["extensions_used"] += 1
        buffer_status["extensions_available"] -= 1
        
        # Update buffer status
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        db.collection("daily_buffers").document(doc_id).update(buffer_status)
        
        return {
            "granted": True,
            "new_due_date": new_due_date,
            "extensions_remaining": buffer_status["extensions_available"],
            "task_id": task_id
        }
    
    async def reset_daily_buffer(self):
        """Reset daily buffer (called at midnight)"""
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        
        buffer_data = {
            "user_id": self.user_id,
            "reset_date": today,
            "extensions_used": 0,
            "extensions_available": self.max_extensions_per_day
        }
        
        db.collection("daily_buffers").document(doc_id).set(buffer_data)

# Cognitive Load Reduction System
class CognitiveLoadReducer:
    def __init__(self):
        self.max_choices = 3  # ?3.1: ?3?
        self.max_primary_actions = 1  # ?
        self.font_settings = {
            "family": "BIZ UDGothic",  # ?3.3: BIZ UDGothic?
            "line_height": 1.6,        # ?3.3: ?
            "max_lines_per_page": 4    # ?3.3: ?4?
        }
        self.layout_constraints = {
            "one_screen_one_action": True,  # ?3.1: ?
            "max_simultaneous_inputs": 1,
            "max_visual_elements": 5
        }
    
    async def validate_one_screen_one_action(self, screen_config: Dict) -> Dict:
        """?"""
        violations = []
        
        # ?
        primary_actions = screen_config.get("primary_actions", [])
        if len(primary_actions) > self.max_primary_actions:
            violations.append({
                "type": "multiple_primary_actions",
                "current": len(primary_actions),
                "max_allowed": self.max_primary_actions,
                "severity": "high"
            })
        
        # ?
        simultaneous_inputs = screen_config.get("simultaneous_inputs", 0)
        if simultaneous_inputs > self.layout_constraints["max_simultaneous_inputs"]:
            violations.append({
                "type": "multiple_simultaneous_inputs",
                "current": simultaneous_inputs,
                "max_allowed": self.layout_constraints["max_simultaneous_inputs"],
                "severity": "high"
            })
        
        # ?
        visual_elements = screen_config.get("visual_elements", 0)
        if visual_elements > self.layout_constraints["max_visual_elements"]:
            violations.append({
                "type": "too_many_visual_elements",
                "current": visual_elements,
                "max_allowed": self.layout_constraints["max_visual_elements"],
                "severity": "medium"
            })
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "constraint_type": "one_screen_one_action",
            "screen_id": screen_config.get("screen_id")
        }
    
    async def validate_choice_limit(self, screen_config: Dict) -> Dict:
        """?3?"""
        violations = []
        
        # ?
        choice_count = screen_config.get("choice_count", 0)
        if choice_count > self.max_choices:
            violations.append({
                "type": "too_many_choices",
                "current": choice_count,
                "max_allowed": self.max_choices,
                "severity": "high",
                "suggestion": "?3つ"
            })
        
        # ?
        choices = screen_config.get("choices", [])
        for i, choice in enumerate(choices):
            if isinstance(choice, dict):
                text_length = len(choice.get("text", ""))
                if text_length > 20:  # 20文字
                    violations.append({
                        "type": "choice_text_too_long",
                        "choice_index": i,
                        "current_length": text_length,
                        "max_recommended": 20,
                        "severity": "medium"
                    })
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "constraint_type": "choice_limit",
            "screen_id": screen_config.get("screen_id")
        }
    
    async def validate_font_settings(self, screen_config: Dict) -> Dict:
        """BIZ UDGothic?"""
        violations = []
        
        # ?
        font_config = screen_config.get("font", {})
        
        if font_config.get("family") != self.font_settings["family"]:
            violations.append({
                "type": "incorrect_font_family",
                "current": font_config.get("family", "?"),
                "required": self.font_settings["family"],
                "severity": "high"
            })
        
        # ?
        line_height = font_config.get("line_height", 1.0)
        if line_height < self.font_settings["line_height"]:
            violations.append({
                "type": "insufficient_line_height",
                "current": line_height,
                "required": self.font_settings["line_height"],
                "severity": "medium"
            })
        
        # ?
        text_lines = screen_config.get("text_lines", 0)
        if text_lines > self.font_settings["max_lines_per_page"]:
            violations.append({
                "type": "too_many_text_lines",
                "current": text_lines,
                "max_allowed": self.font_settings["max_lines_per_page"],
                "severity": "medium",
                "suggestion": "?"
            })
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "constraint_type": "font_settings",
            "screen_id": screen_config.get("screen_id")
        }
    
    async def assess_cognitive_load(self, screen_config: Dict) -> Dict:
        """?"""
        load_score = 0
        load_factors = []
        
        # ?
        info_density = screen_config.get("information_density", "low")
        if info_density == "high":
            load_score += 4
            load_factors.append("high_information_density")
        elif info_density == "medium":
            load_score += 2
            load_factors.append("medium_information_density")
        
        # ?
        choice_count = screen_config.get("choice_count", 0)
        if choice_count > 3:
            load_score += 3
            load_factors.append("too_many_choices")
        elif choice_count > 1:
            load_score += 1
            load_factors.append("multiple_choices")
        
        # ?
        simultaneous_inputs = screen_config.get("simultaneous_inputs", 0)
        load_score += simultaneous_inputs * 2
        if simultaneous_inputs > 0:
            load_factors.append("simultaneous_inputs")
        
        # ?
        visual_elements = screen_config.get("visual_elements", 0)
        if visual_elements > 10:
            load_score += 3
            load_factors.append("too_many_visual_elements")
        elif visual_elements > 5:
            load_score += 1
            load_factors.append("many_visual_elements")
        
        # アプリ
        animations = screen_config.get("animations", 0)
        if animations > 2:
            load_score += 2
            load_factors.append("too_many_animations")
        
        # ?
        if load_score <= 2:
            load_level = "low"
            adhd_friendly = True
        elif load_score <= 5:
            load_level = "medium"
            adhd_friendly = True
        elif load_score <= 8:
            load_level = "high"
            adhd_friendly = False
        else:
            load_level = "very_high"
            adhd_friendly = False
        
        return {
            "load_level": load_level,
            "load_score": load_score,
            "load_factors": load_factors,
            "adhd_friendly": adhd_friendly,
            "recommendations": await self._generate_load_reduction_recommendations(load_factors)
        }
    
    async def _generate_load_reduction_recommendations(self, load_factors: List[str]) -> List[Dict]:
        """?"""
        recommendations = []
        
        if "too_many_choices" in load_factors:
            recommendations.append({
                "type": "reduce_choices",
                "description": "?3つ",
                "priority": "high",
                "implementation": "?"
            })
        
        if "high_information_density" in load_factors:
            recommendations.append({
                "type": "reduce_information_density",
                "description": "?",
                "priority": "high",
                "implementation": "?"
            })
        
        if "simultaneous_inputs" in load_factors:
            recommendations.append({
                "type": "sequential_inputs",
                "description": "入力",
                "priority": "high",
                "implementation": "一般"
            })
        
        if "too_many_visual_elements" in load_factors:
            recommendations.append({
                "type": "simplify_visual_design",
                "description": "?",
                "priority": "medium",
                "implementation": "?"
            })
        
        if "too_many_animations" in load_factors:
            recommendations.append({
                "type": "reduce_animations",
                "description": "アプリ",
                "priority": "medium",
                "implementation": "?"
            })
        
        return recommendations
    
    async def generate_adhd_optimized_layout(self, content_data: Dict) -> Dict:
        """ADHD?"""
        optimized_layout = {
            "layout_type": "adhd_optimized",
            "font": self.font_settings,
            "constraints": self.layout_constraints,
            "content_structure": {}
        }
        
        # コア
        if "text" in content_data:
            text_lines = content_data["text"].split('\n')
            if len(text_lines) > self.font_settings["max_lines_per_page"]:
                # ?
                pages = []
                for i in range(0, len(text_lines), self.font_settings["max_lines_per_page"]):
                    page_lines = text_lines[i:i + self.font_settings["max_lines_per_page"]]
                    pages.append('\n'.join(page_lines))
                optimized_layout["content_structure"]["text_pages"] = pages
            else:
                optimized_layout["content_structure"]["text"] = content_data["text"]
        
        # ?
        if "choices" in content_data:
            choices = content_data["choices"][:self.max_choices]  # ?3つ
            optimized_layout["content_structure"]["choices"] = choices
        
        # ?
        if "actions" in content_data:
            actions = content_data["actions"]
            primary_actions = [a for a in actions if a.get("type") == "primary"][:1]
            secondary_actions = [a for a in actions if a.get("type") != "primary"]
            optimized_layout["content_structure"]["primary_action"] = primary_actions[0] if primary_actions else None
            optimized_layout["content_structure"]["secondary_actions"] = secondary_actions
        
        return optimized_layout

# UI Constraint Validator (?)
class UIConstraintValidator(CognitiveLoadReducer):
    def __init__(self):
        super().__init__()
        self.validation_rules = {
            "one_screen_one_action": True,
            "choice_limit": True,
            "font_settings": True,
            "cognitive_load": True
        }
    
    async def validate_screen(self, screen_config: Dict) -> Dict:
        """?ADHD?"""
        validation_results = {
            "screen_id": screen_config.get("screen_id"),
            "overall_valid": True,
            "validations": {},
            "violations": [],
            "recommendations": []
        }
        
        # ?
        if self.validation_rules["one_screen_one_action"]:
            one_action_result = await self.validate_one_screen_one_action(screen_config)
            validation_results["validations"]["one_screen_one_action"] = one_action_result
            if not one_action_result["is_valid"]:
                validation_results["overall_valid"] = False
                validation_results["violations"].extend(one_action_result["violations"])
        
        # ?
        if self.validation_rules["choice_limit"]:
            choice_result = await self.validate_choice_limit(screen_config)
            validation_results["validations"]["choice_limit"] = choice_result
            if not choice_result["is_valid"]:
                validation_results["overall_valid"] = False
                validation_results["violations"].extend(choice_result["violations"])
        
        # ?
        if self.validation_rules["font_settings"]:
            font_result = await self.validate_font_settings(screen_config)
            validation_results["validations"]["font_settings"] = font_result
            if not font_result["is_valid"]:
                validation_results["overall_valid"] = False
                validation_results["violations"].extend(font_result["violations"])
        
        # ?
        if self.validation_rules["cognitive_load"]:
            load_result = await self.assess_cognitive_load(screen_config)
            validation_results["validations"]["cognitive_load"] = load_result
            if not load_result["adhd_friendly"]:
                validation_results["overall_valid"] = False
            validation_results["recommendations"].extend(load_result["recommendations"])
        
        return validation_results
    
    async def get_adhd_optimizations(self, screen_config: Dict) -> List[Dict]:
        """ADHD?"""
        optimizations = []
        
        # ?
        load_result = await self.assess_cognitive_load(screen_config)
        optimizations.extend(load_result["recommendations"])
        
        # ?
        if screen_config.get("color_contrast", "normal") == "low":
            optimizations.append({
                "type": "improve_contrast",
                "description": "?",
                "priority": "medium",
                "implementation": "?4.5:1?"
            })
        
        if not screen_config.get("keyboard_navigation", False):
            optimizations.append({
                "type": "add_keyboard_navigation",
                "description": "?",
                "priority": "medium",
                "implementation": "Tab?"
            })
        
        return optimizations

# ADHD Assist Multiplier Calculator
class ADHDAssistCalculator:
    def __init__(self):
        self.base_multiplier = 1.0
        self.max_multiplier = 1.3
        self.feature_bonuses = {
            "pomodoro_enabled": 0.1,
            "reminders_enabled": 0.1,
            "break_detection": 0.1,
            "hyperfocus_alerts": 0.05,
            "daily_buffer_used": 0.05,
            "ui_optimized": 0.05
        }
    
    async def calculate_multiplier(self, user_id: str, task_data: Dict) -> float:
        """Calculate ADHD assist multiplier for XP calculation"""
        multiplier = self.base_multiplier
        adhd_support = task_data.get("adhd_support", {})
        
        # Add bonuses for enabled features
        for feature, bonus in self.feature_bonuses.items():
            if adhd_support.get(feature, False):
                multiplier += bonus
        
        # Cap at maximum multiplier
        multiplier = min(multiplier, self.max_multiplier)
        
        return multiplier
    
    async def get_user_adhd_profile(self, user_id: str) -> Dict:
        """Get user's ADHD profile for personalized multipliers"""
        # Mock implementation
        return {
            "adhd_severity": "moderate",
            "primary_symptoms": ["inattention"],
            "support_tool_usage": "medium"
        }

# Time Perception Support System
class TimePerceptionSupport:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.reminder_interval = 15 * 60  # ?3.5: 15?
        self.active_reminders = {}
        self.daily_buffer_manager = DailyBufferManager(user_id)
    
    async def start_time_perception_reminders(self, task_name: str, config: Dict = None) -> Dict:
        """15?"""
        if config is None:
            config = {}
        
        reminder_id = str(uuid.uuid4())
        reminder_data = {
            "reminder_id": reminder_id,
            "user_id": self.user_id,
            "task_name": task_name,
            "start_time": datetime.utcnow(),
            "next_reminder": datetime.utcnow() + timedelta(seconds=self.reminder_interval),
            "reminder_count": 0,
            "is_active": True,
            "config": config,
            "total_elapsed_time": 0,
            "reminder_history": []
        }
        
        # デフォルト
        db.collection("time_perception_reminders").document(reminder_id).set(reminder_data)
        self.active_reminders[reminder_id] = reminder_data
        
        return reminder_data
    
    async def check_reminder_due(self, reminder_id: str) -> bool:
        """リスト"""
        if reminder_id not in self.active_reminders:
            # デフォルト
            doc = db.collection("time_perception_reminders").document(reminder_id).get()
            if doc.exists():
                self.active_reminders[reminder_id] = doc.to_dict()
            else:
                return False
        
        reminder = self.active_reminders[reminder_id]
        if not reminder["is_active"]:
            return False
        
        return datetime.utcnow() >= reminder["next_reminder"]
    
    async def trigger_reminder(self, reminder_id: str) -> Dict:
        """15?"""
        if reminder_id not in self.active_reminders:
            doc = db.collection("time_perception_reminders").document(reminder_id).get()
            if not doc.exists():
                raise HTTPException(status_code=404, detail="Reminder not found")
            self.active_reminders[reminder_id] = doc.to_dict()
        
        reminder = self.active_reminders[reminder_id]
        reminder["reminder_count"] += 1
        reminder["next_reminder"] = datetime.utcnow() + timedelta(seconds=self.reminder_interval)
        
        elapsed_minutes = (datetime.utcnow() - reminder["start_time"]).total_seconds() / 60
        reminder["total_elapsed_time"] = elapsed_minutes
        
        # リスト
        reminder_entry = {
            "timestamp": datetime.utcnow(),
            "elapsed_minutes": int(elapsed_minutes),
            "reminder_number": reminder["reminder_count"]
        }
        reminder["reminder_history"].append(reminder_entry)
        
        # デフォルト
        db.collection("time_perception_reminders").document(reminder_id).update(reminder)
        
        # ?
        message = await self._generate_time_perception_message(reminder)
        
        # LINE?
        notification_service = LINENotificationService()
        await notification_service.send_15_minute_reminder(
            self.user_id, 
            reminder["task_name"],
            int(elapsed_minutes),
            reminder["reminder_count"]
        )
        
        return {
            "reminder_triggered": True,
            "elapsed_minutes": int(elapsed_minutes),
            "task_name": reminder["task_name"],
            "reminder_count": reminder["reminder_count"],
            "message": message,
            "next_reminder_in": self.reminder_interval // 60,
            "total_reminders_today": await self._get_daily_reminder_count()
        }
    
    async def _generate_time_perception_message(self, reminder: Dict) -> str:
        """?"""
        elapsed_minutes = int(reminder["total_elapsed_time"])
        reminder_count = reminder["reminder_count"]
        task_name = reminder["task_name"]
        
        # ?
        if elapsed_minutes <= 15:
            return f"? 15?{task_name}?"
        elif elapsed_minutes <= 30:
            return f"? {elapsed_minutes}?{task_name}?"
        elif elapsed_minutes <= 60:
            return f"? {elapsed_minutes}?{task_name}?1?"
        else:
            hours = elapsed_minutes // 60
            minutes = elapsed_minutes % 60
            return f"? {hours}?{minutes}?{task_name}?"
    
    async def _get_daily_reminder_count(self) -> int:
        """?"""
        today = date.today()
        # ?Firestore?
        return len([r for r in self.active_reminders.values() 
                   if r["start_time"].date() == today])
    
    async def pause_reminders(self, reminder_id: str) -> Dict:
        """リスト"""
        if reminder_id not in self.active_reminders:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        reminder = self.active_reminders[reminder_id]
        reminder["is_active"] = False
        reminder["paused_at"] = datetime.utcnow()
        
        db.collection("time_perception_reminders").document(reminder_id).update(reminder)
        
        return {
            "paused": True,
            "reminder_id": reminder_id,
            "paused_at": reminder["paused_at"]
        }
    
    async def resume_reminders(self, reminder_id: str) -> Dict:
        """リスト"""
        if reminder_id not in self.active_reminders:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        reminder = self.active_reminders[reminder_id]
        reminder["is_active"] = True
        reminder["next_reminder"] = datetime.utcnow() + timedelta(seconds=self.reminder_interval)
        
        db.collection("time_perception_reminders").document(reminder_id).update(reminder)
        
        return {
            "resumed": True,
            "reminder_id": reminder_id,
            "next_reminder": reminder["next_reminder"]
        }
    
    async def stop_reminders(self, reminder_id: str) -> Dict:
        """リスト"""
        if reminder_id not in self.active_reminders:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        reminder = self.active_reminders[reminder_id]
        reminder["is_active"] = False
        reminder["stopped_at"] = datetime.utcnow()
        
        total_time = (datetime.utcnow() - reminder["start_time"]).total_seconds() / 60
        
        db.collection("time_perception_reminders").document(reminder_id).update(reminder)
        del self.active_reminders[reminder_id]
        
        return {
            "stopped": True,
            "reminder_id": reminder_id,
            "total_time_minutes": int(total_time),
            "total_reminders": reminder["reminder_count"]
        }

# Daily Buffer Manager (?)
class DailyBufferManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.max_extensions_per_day = 2  # ?3.5: 1?2?
        self.extension_duration_hours = 2  # デフォルト
        self.buffer_reset_time = "00:00"  # ?0?
    
    async def get_daily_buffer_status(self) -> Dict:
        """デフォルト"""
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        
        doc = db.collection("daily_buffers").document(doc_id).get()
        
        if not doc.exists():
            # ?
            buffer_data = {
                "user_id": self.user_id,
                "reset_date": today,
                "extensions_used": 0,
                "extensions_available": self.max_extensions_per_day,
                "extension_history": [],
                "created_at": datetime.utcnow()
            }
            db.collection("daily_buffers").document(doc_id).set(buffer_data)
            return buffer_data
        
        buffer_data = doc.to_dict()
        
        # ?
        if buffer_data["reset_date"] != today:
            await self.reset_daily_buffer()
            return await self.get_daily_buffer_status()
        
        return buffer_data
    
    async def request_extension(self, task_id: str, hours: int = None, reason: str = None) -> Dict:
        """?"""
        if hours is None:
            hours = self.extension_duration_hours
        
        buffer_status = await self.get_daily_buffer_status()
        
        # ?
        if buffer_status["extensions_used"] >= self.max_extensions_per_day:
            return {
                "granted": False,
                "reason": "daily_limit_exceeded",
                "extensions_remaining": 0,
                "next_reset": await self._get_next_reset_time(),
                "message": f"?{self.max_extensions_per_day}?0?"
            }
        
        # ?
        new_due_date = datetime.utcnow() + timedelta(hours=hours)
        buffer_status["extensions_used"] += 1
        buffer_status["extensions_available"] -= 1
        
        # ?
        extension_record = {
            "task_id": task_id,
            "granted_at": datetime.utcnow(),
            "extension_hours": hours,
            "new_due_date": new_due_date,
            "reason": reason or "user_request"
        }
        buffer_status["extension_history"].append(extension_record)
        
        # デフォルト
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        db.collection("daily_buffers").document(doc_id).update(buffer_status)
        
        return {
            "granted": True,
            "new_due_date": new_due_date,
            "extensions_remaining": buffer_status["extensions_available"],
            "task_id": task_id,
            "extension_hours": hours,
            "message": f"?{hours}?: {buffer_status['extensions_available']}?"
        }
    
    async def get_extension_history(self, days: int = 7) -> List[Dict]:
        """?"""
        history = []
        
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            doc_id = f"{self.user_id}_{target_date}"
            
            doc = db.collection("daily_buffers").document(doc_id).get()
            if doc.exists():
                buffer_data = doc.to_dict()
                for extension in buffer_data.get("extension_history", []):
                    extension["date"] = target_date
                    history.append(extension)
        
        return sorted(history, key=lambda x: x["granted_at"], reverse=True)
    
    async def _get_next_reset_time(self) -> datetime:
        """?"""
        tomorrow = date.today() + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.strptime(self.buffer_reset_time, "%H:%M").time())
    
    async def reset_daily_buffer(self):
        """デフォルト0?"""
        today = date.today()
        doc_id = f"{self.user_id}_{today}"
        
        buffer_data = {
            "user_id": self.user_id,
            "reset_date": today,
            "extensions_used": 0,
            "extensions_available": self.max_extensions_per_day,
            "extension_history": [],
            "reset_at": datetime.utcnow()
        }
        
        db.collection("daily_buffers").document(doc_id).set(buffer_data)
        
        return buffer_data
    
    async def check_extension_eligibility(self, task_id: str) -> Dict:
        """?"""
        buffer_status = await self.get_daily_buffer_status()
        
        # ?
        task_extensions_today = [
            ext for ext in buffer_status.get("extension_history", [])
            if ext["task_id"] == task_id
        ]
        
        return {
            "eligible": buffer_status["extensions_available"] > 0,
            "extensions_remaining": buffer_status["extensions_available"],
            "task_extended_today": len(task_extensions_today) > 0,
            "task_extension_count": len(task_extensions_today)
        }

# LINE Notification Service
class LINENotificationService:
    def __init__(self):
        self.line_available = True  # Mock LINE availability
        self.notification_history = {}  # Track notification frequency
        self.rate_limits = {
            "hourly_limit": 10,
            "daily_limit": 50
        }
    
    async def send_message(self, user_id: str, message: str):
        """Send LINE message (mock implementation)"""
        if not self.line_available:
            raise Exception("LINE service unavailable")
        
        # Check rate limits
        frequency = await self.get_notification_frequency(user_id)
        if frequency["hourly_count"] >= self.rate_limits["hourly_limit"]:
            raise Exception("Hourly notification limit exceeded")
        if frequency["daily_count"] >= self.rate_limits["daily_limit"]:
            raise Exception("Daily notification limit exceeded")
        
        # Track notification frequency
        if user_id not in self.notification_history:
            self.notification_history[user_id] = []
        
        self.notification_history[user_id].append({
            "message": message,
            "timestamp": datetime.utcnow(),
            "type": "line"
        })
        
        # Mock LINE API call
        print(f"LINE message to {user_id}: {message}")
    
    async def send_pomodoro_notification(self, notification_data: Dict):
        """Send Pomodoro-related notification"""
        user_id = notification_data["user_id"]
        message_type = notification_data["message_type"]
        
        if message_type == "pomodoro_start":
            duration = notification_data.get("duration", 25)
            message = f"? {duration}?"
        elif message_type == "pomodoro_complete":
            message = "? ?"
        elif message_type == "break_start":
            duration = notification_data.get("duration", 5)
            message = f"? {duration}?"
        elif message_type == "break_complete":
            message = "? ?"
        else:
            message = "?"
        
        try:
            await self.send_message(user_id, message)
        except Exception:
            await self.send_fcm_fallback(user_id, message)
    
    async def send_break_reminder(self, notification_data: Dict):
        """Send break reminder notification with escalating urgency"""
        user_id = notification_data["user_id"]
        work_duration = notification_data["work_duration"]
        urgency = notification_data.get("urgency", "gentle")
        suggestion_count = notification_data.get("suggestion_count", 0)
        
        # Generate escalating messages based on suggestion count
        if suggestion_count == 0:
            message = f"? {work_duration}?"
        elif suggestion_count == 1:
            message = f"? {work_duration}?"
        else:
            message = f"? {work_duration}?"
        
        try:
            await self.send_message(user_id, message)
        except Exception:
            await self.send_fcm_fallback(user_id, message)
    
    async def send_15_minute_reminder(self, user_id: str, task_name: str, elapsed_minutes: int = 15, reminder_count: int = 1):
        """15?"""
        # ?
        if elapsed_minutes <= 15:
            message = f"? 15?{task_name}?"
        elif elapsed_minutes <= 30:
            message = f"? {elapsed_minutes}?{task_name}?"
        elif elapsed_minutes <= 60:
            message = f"? {elapsed_minutes}?{task_name}?1?"
        else:
            hours = elapsed_minutes // 60
            minutes = elapsed_minutes % 60
            if minutes > 0:
                message = f"? {hours}?{minutes}?{task_name}?"
            else:
                message = f"? {hours}?{task_name}?"
        
        # リスト
        if reminder_count >= 4:  # 1?
            message += "\n\n? ?"
        elif reminder_count >= 8:  # 2?
            message += "\n\n? 2?"
        
        try:
            await self.send_message(user_id, message)
        except Exception:
            await self.send_fcm_fallback(user_id, message)
    
    async def send_daily_buffer_notification(self, user_id: str, notification_type: str, data: Dict):
        """デフォルト"""
        if notification_type == "extension_granted":
            task_id = data.get("task_id", "タスク")
            hours = data.get("hours", 2)
            remaining = data.get("remaining", 0)
            message = f"? ?\n\n? ?: {task_id}\n? ?: {hours}?\n? ?: {remaining}?"
        
        elif notification_type == "extension_denied":
            reason = data.get("reason", "unknown")
            if reason == "daily_limit_exceeded":
                message = "? ?\n\n理: ?\n? ?: ?0?"
            else:
                message = "? ?"
        
        elif notification_type == "buffer_reset":
            message = "? デフォルト\n\n?2?"
        
        elif notification_type == "extension_warning":
            remaining = data.get("remaining", 0)
            message = f"? ?{remaining}?\n\n計算"
        
        else:
            message = "デフォルト"
        
        try:
            await self.send_message(user_id, message)
        except Exception:
            await self.send_fcm_fallback(user_id, message)
    
    async def send_fcm_fallback(self, user_id: str, message: str):
        """Fallback to Firebase Cloud Messaging"""
        if user_id not in self.notification_history:
            self.notification_history[user_id] = []
        
        self.notification_history[user_id].append({
            "message": message,
            "timestamp": datetime.utcnow(),
            "type": "fcm_fallback"
        })
        
        print(f"FCM fallback to {user_id}: {message}")
    
    async def get_notification_frequency(self, user_id: str) -> Dict:
        """Get notification frequency for user"""
        if user_id not in self.notification_history:
            return {"daily_count": 0, "hourly_count": 0}
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        daily_count = len([n for n in self.notification_history[user_id] 
                          if n["timestamp"] >= today_start])
        hourly_count = len([n for n in self.notification_history[user_id] 
                           if n["timestamp"] >= hour_start])
        
        return {
            "daily_count": daily_count,
            "hourly_count": hourly_count,
            "last_notification": self.notification_history[user_id][-1]["timestamp"] if self.notification_history[user_id] else None
        }

# Main ADHD Support Service
class ADHDSupportService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.pomodoro_timer = PomodoroTimer(user_id)
        self.hyperfocus_detector = HyperfocusDetector(user_id)
        self.buffer_manager = DailyBufferManager(user_id)
        self.ui_validator = UIConstraintValidator()
        self.assist_calculator = ADHDAssistCalculator()
        self.notification_service = LINENotificationService()
    
    async def start_supported_work_session(self, task_name: str, config: Dict) -> Dict:
        """Start work session with full ADHD support"""
        session_data = {
            "task_name": task_name,
            "user_id": self.user_id,
            "start_time": datetime.utcnow()
        }
        
        # Start Pomodoro if enabled
        if config.get("pomodoro_enabled"):
            pomodoro_cycle = await self.pomodoro_timer.start_cycle()
            session_data["pomodoro_active"] = True
            session_data["pomodoro_cycle_id"] = pomodoro_cycle["cycle_id"]
        
        # Start hyperfocus monitoring if enabled
        if config.get("break_detection"):
            work_session = await self.hyperfocus_detector.start_work_session(task_name)
            session_data["hyperfocus_monitoring"] = True
            session_data["work_session_id"] = work_session["session_id"]
        
        # Set up reminders if enabled
        if config.get("reminders_enabled"):
            session_data["reminder_schedule"] = await self._setup_reminders()
        
        # Calculate ADHD multiplier
        task_data = {"adhd_support": config}
        multiplier = await self.assist_calculator.calculate_multiplier(self.user_id, task_data)
        session_data["adhd_multiplier"] = multiplier
        
        return session_data
    
    async def _setup_reminders(self) -> Dict:
        """Set up reminder schedule"""
        return {
            "interval": 15,  # 15 minutes
            "next_reminder": datetime.utcnow() + timedelta(minutes=15)
        }
    
    async def trigger_crisis_intervention(self, crisis_data: Dict) -> Dict:
        """Trigger crisis intervention for extreme hyperfocus"""
        intervention = {
            "intervention_level": "high",
            "forced_break": True,
            "guardian_notification": True,
            "break_duration": 30,  # Force 30-minute break
            "message": "?"
        }
        
        return intervention
    
    async def adapt_support_features(self, behavior_data: Dict) -> Dict:
        """Adapt support features based on user behavior"""
        recommendations = []
        
        if behavior_data["pomodoro_completion_rate"] < 0.5:
            recommendations.append("reduce_pomodoro_duration")
        
        if behavior_data["break_compliance"] > 0.7:
            recommendations.append("maintain_break_system")
        
        if behavior_data["hyperfocus_episodes"] > 2:
            recommendations.append("increase_break_frequency")
        
        # Calculate new multiplier based on adaptations
        new_multiplier = 1.0 + (len(recommendations) * 0.05)
        new_multiplier = min(new_multiplier, 1.3)
        
        return {
            "recommendations": recommendations,
            "new_multiplier": new_multiplier,
            "adaptation_reason": "behavior_analysis"
        }

# API Endpoints
@app.post("/pomodoro/start")
async def start_pomodoro(current_user: dict = Depends(verify_jwt_token)):
    """Start a new Pomodoro cycle"""
    timer = PomodoroTimer(current_user["uid"])
    cycle = await timer.start_cycle()
    return cycle

@app.post("/pomodoro/{cycle_id}/complete")
async def complete_pomodoro_phase(cycle_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Complete current Pomodoro phase"""
    timer = PomodoroTimer(current_user["uid"])
    next_phase = await timer.complete_phase(cycle_id)
    return next_phase

@app.post("/hyperfocus/start")
async def start_work_session(task_name: str, current_user: dict = Depends(verify_jwt_token)):
    """Start hyperfocus monitoring"""
    detector = HyperfocusDetector(current_user["uid"])
    session = await detector.start_work_session(task_name)
    return session

@app.get("/buffer/status")
async def get_buffer_status(current_user: dict = Depends(verify_jwt_token)):
    """Get daily buffer status"""
    buffer_mgr = DailyBufferManager(current_user["uid"])
    status = await buffer_mgr.get_daily_buffer_status()
    return status

@app.post("/buffer/extend")
async def request_extension(task_id: str, hours: int = 2, current_user: dict = Depends(verify_jwt_token)):
    """Request deadline extension"""
    buffer_mgr = DailyBufferManager(current_user["uid"])
    result = await buffer_mgr.request_extension(task_id, hours)
    return result

@app.post("/ui/validate")
async def validate_ui_screen(screen_config: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Validate UI screen for ADHD constraints"""
    validator = UIConstraintValidator()
    validation_result = await validator.validate_screen(screen_config)
    return validation_result

@app.post("/multiplier/calculate")
async def calculate_adhd_multiplier(task_data: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Calculate ADHD assist multiplier"""
    calculator = ADHDAssistCalculator()
    multiplier = await calculator.calculate_multiplier(current_user["uid"], task_data)
    return {"multiplier": multiplier}

@app.post("/time-perception/start")
async def start_time_perception_reminders(task_name: str, current_user: dict = Depends(verify_jwt_token)):
    """Start 15-minute time perception reminders"""
    time_support = TimePerceptionSupport(current_user["uid"])
    reminder = await time_support.start_time_perception_reminders(task_name)
    return reminder

@app.post("/time-perception/{reminder_id}/trigger")
async def trigger_time_reminder(reminder_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Trigger 15-minute time perception reminder"""
    time_support = TimePerceptionSupport(current_user["uid"])
    reminder_result = await time_support.trigger_reminder(reminder_id)
    return reminder_result

@app.post("/time-perception/{reminder_id}/pause")
async def pause_time_reminder(reminder_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Pause time perception reminder"""
    time_support = TimePerceptionSupport(current_user["uid"])
    result = await time_support.pause_reminders(reminder_id)
    return result

@app.post("/time-perception/{reminder_id}/resume")
async def resume_time_reminder(reminder_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Resume time perception reminder"""
    time_support = TimePerceptionSupport(current_user["uid"])
    result = await time_support.resume_reminders(reminder_id)
    return result

@app.post("/time-perception/{reminder_id}/stop")
async def stop_time_reminder(reminder_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Stop time perception reminder"""
    time_support = TimePerceptionSupport(current_user["uid"])
    result = await time_support.stop_reminders(reminder_id)
    return result

@app.post("/buffer/check-eligibility")
async def check_extension_eligibility(task_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Check extension eligibility for a task"""
    buffer_mgr = DailyBufferManager(current_user["uid"])
    eligibility = await buffer_mgr.check_extension_eligibility(task_id)
    return eligibility

@app.get("/buffer/history")
async def get_extension_history(days: int = 7, current_user: dict = Depends(verify_jwt_token)):
    """Get extension history"""
    buffer_mgr = DailyBufferManager(current_user["uid"])
    history = await buffer_mgr.get_extension_history(days)
    return {"history": history}

@app.post("/cognitive-load/validate")
async def validate_cognitive_load(screen_config: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Validate screen for cognitive load constraints"""
    validator = UIConstraintValidator()
    validation_result = await validator.validate_screen(screen_config)
    return validation_result

@app.post("/cognitive-load/optimize")
async def optimize_layout(content_data: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Generate ADHD-optimized layout"""
    reducer = CognitiveLoadReducer()
    optimized_layout = await reducer.generate_adhd_optimized_layout(content_data)
    return optimized_layout

@app.post("/hyperfocus/{session_id}/break-suggestion")
async def generate_break_suggestion(session_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Generate escalating break suggestion for hyperfocus"""
    detector = HyperfocusDetector(current_user["uid"])
    session = await detector.get_session(session_id)
    
    suggestion = await detector.generate_break_suggestion(session["break_suggestions"])
    
    # Update break suggestion count
    session["break_suggestions"] += 1
    db.collection("work_sessions").document(session_id).update({"break_suggestions": session["break_suggestions"]})
    
    return suggestion

@app.post("/hyperfocus/{session_id}/take-break")
async def take_break(session_id: str, current_user: dict = Depends(verify_jwt_token)):
    """Record that user took a break"""
    detector = HyperfocusDetector(current_user["uid"])
    break_result = await detector.take_break(session_id)
    return break_result

@app.post("/ui/assess-cognitive-load")
async def assess_cognitive_load(screen_config: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Assess cognitive load of a screen"""
    validator = UIConstraintValidator()
    load_assessment = await validator.assess_cognitive_load(screen_config)
    return load_assessment

@app.get("/ui/adhd-optimizations")
async def get_adhd_optimizations(screen_config: Dict, current_user: dict = Depends(verify_jwt_token)):
    """Get ADHD optimization suggestions"""
    validator = UIConstraintValidator()
    optimizations = await validator.get_adhd_optimizations(screen_config)
    return {"optimizations": optimizations}

@app.post("/support/start-session")
async def start_supported_work_session(
    task_name: str, 
    config: Dict, 
    current_user: dict = Depends(verify_jwt_token)
):
    """Start work session with full ADHD support"""
    support_service = ADHDSupportService(current_user["uid"])
    session = await support_service.start_supported_work_session(task_name, config)
    return session

@app.post("/support/adapt-features")
async def adapt_support_features(
    behavior_data: Dict, 
    current_user: dict = Depends(verify_jwt_token)
):
    """Adapt support features based on user behavior"""
    support_service = ADHDSupportService(current_user["uid"])
    adaptations = await support_service.adapt_support_features(behavior_data)
    return adaptations

@app.post("/notifications/pomodoro")
async def send_pomodoro_notification(
    notification_data: Dict,
    current_user: dict = Depends(verify_jwt_token)
):
    """Send Pomodoro-related notification via LINE"""
    notification_service = LINENotificationService()
    notification_data["user_id"] = current_user["uid"]
    await notification_service.send_pomodoro_notification(notification_data)
    return {"status": "notification_sent"}

@app.post("/notifications/break-reminder")
async def send_break_reminder(
    notification_data: Dict,
    current_user: dict = Depends(verify_jwt_token)
):
    """Send break reminder notification with escalating urgency"""
    notification_service = LINENotificationService()
    notification_data["user_id"] = current_user["uid"]
    await notification_service.send_break_reminder(notification_data)
    return {"status": "reminder_sent"}

@app.get("/notifications/frequency/{user_id}")
async def get_notification_frequency(
    user_id: str,
    current_user: dict = Depends(verify_jwt_token)
):
    """Get notification frequency for user"""
    notification_service = LINENotificationService()
    frequency = await notification_service.get_notification_frequency(user_id)
    return frequency

@app.post("/session/start-supported")
async def start_supported_work_session(
    task_name: str, 
    config: Dict, 
    current_user: dict = Depends(verify_jwt_token)
):
    """Start work session with full ADHD support"""
    adhd_service = ADHDSupportService(current_user["uid"])
    session_data = await adhd_service.start_supported_work_session(task_name, config)
    return session_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)