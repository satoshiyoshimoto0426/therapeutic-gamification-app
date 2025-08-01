"""
Self-Efficacy Gauge Service - 自動

?
- 21?MAX ? ?
- 治療
- ?
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import math

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="Self-Efficacy Gauge Service", version="1.0.0")
logger = logging.getLogger(__name__)

class EfficacyLevel(Enum):
    NOVICE = "novice"          # ? (0-20%)
    DEVELOPING = "developing"  # 発 (21-40%)
    COMPETENT = "competent"    # ? (41-60%)
    PROFICIENT = "proficient"  # ? (61-80%)
    EXPERT = "expert"          # ? (81-100%)

class PassiveSkillType(Enum):
    XP_BOOST = "xp_boost"                    # XP?
    TASK_EFFICIENCY = "task_efficiency"      # タスク
    MOOD_STABILITY = "mood_stability"        # 気分
    FOCUS_ENHANCEMENT = "focus_enhancement"  # ?
    RESILIENCE_BOOST = "resilience_boost"    # ?
    SOCIAL_CONFIDENCE = "social_confidence"  # ?
    CREATIVE_FLOW = "creative_flow"          # 創
    WISDOM_INSIGHT = "wisdom_insight"        # ?

class PassiveSkill(BaseModel):
    skill_id: str
    skill_type: PassiveSkillType
    name: str
    description: str
    effect_value: float  # ?1.2 = 20%?
    unlock_requirement: int  # ?
    therapeutic_focus: str
    visual_effect: str
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None

class EfficacyGauge(BaseModel):
    user_id: str
    therapeutic_focus: str  # "Self-Discipline", "Empathy", etc.
    current_level: EfficacyLevel
    current_percentage: float  # 0.0-100.0
    consecutive_days: int
    total_days_active: int
    last_activity_date: datetime
    milestone_reached: List[int]  # ?
    passive_skills: List[PassiveSkill]
    efficacy_history: List[Dict[str, Any]]  # ?

class EfficacyMilestone(BaseModel):
    day: int
    title: str
    description: str
    reward_type: str
    reward_value: Any
    celebration_message: str

class EfficacyUpdateRequest(BaseModel):
    user_id: str
    therapeutic_focus: str
    task_completed: bool
    task_difficulty: int  # 1-5
    mood_rating: int  # 1-5
    reflection_quality: Optional[int] = None  # 1-5

class SelfEfficacyEngine:
    def __init__(self):
        self.milestones = self._initialize_milestones()
        self.passive_skills_pool = self._initialize_passive_skills()
        self.efficacy_formula_weights = {
            "consistency": 0.4,      # ?
            "task_completion": 0.3,  # タスク
            "difficulty_challenge": 0.2,  # ?
            "reflection_depth": 0.1  # ?
        }
    
    def _initialize_milestones(self) -> List[EfficacyMilestone]:
        """?"""
        return [
            EfficacyMilestone(
                day=3,
                title="?",
                description="3?",
                reward_type="xp_bonus",
                reward_value=50,
                celebration_message="? ?"
            ),
            EfficacyMilestone(
                day=7,
                title="1?",
                description="1?",
                reward_type="passive_skill",
                reward_value="xp_boost_basic",
                celebration_message="? 1?"
            ),
            EfficacyMilestone(
                day=14,
                title="2?",
                description="2?",
                reward_type="gauge_boost",
                reward_value=10,
                celebration_message="? 2?"
            ),
            EfficacyMilestone(
                day=21,
                title="?",
                description="21?",
                reward_type="passive_skill_unlock",
                reward_value="all_available",
                celebration_message="? 21?"
            ),
            EfficacyMilestone(
                day=30,
                title="1?",
                description="30?",
                reward_type="special_ability",
                reward_value="efficacy_master",
                celebration_message="? 30?"
            ),
            EfficacyMilestone(
                day=50,
                title="?",
                description="50?",
                reward_type="mentor_unlock",
                reward_value="peer_mentoring",
                celebration_message="? 50?"
            ),
            EfficacyMilestone(
                day=100,
                title="?",
                description="100?",
                reward_type="legend_status",
                reward_value="hundred_day_legend",
                celebration_message="? 100?"
            )
        ]
    
    def _initialize_passive_skills(self) -> List[PassiveSkill]:
        """?"""
        return [
            PassiveSkill(
                skill_id="xp_boost_basic",
                skill_type=PassiveSkillType.XP_BOOST,
                name="?",
                description="?XPが20%?",
                effect_value=1.2,
                unlock_requirement=7,
                therapeutic_focus="Self-Discipline",
                visual_effect="golden_sparkle"
            ),
            PassiveSkill(
                skill_id="task_efficiency_basic",
                skill_type=PassiveSkillType.TASK_EFFICIENCY,
                name="?",
                description="タスク15%?",
                effect_value=0.85,
                unlock_requirement=14,
                therapeutic_focus="Self-Discipline",
                visual_effect="speed_lines"
            ),
            PassiveSkill(
                skill_id="mood_stability_basic",
                skill_type=PassiveSkillType.MOOD_STABILITY,
                name="?",
                description="気分25%?",
                effect_value=0.75,
                unlock_requirement=21,
                therapeutic_focus="Resilience",
                visual_effect="calm_aura"
            ),
            PassiveSkill(
                skill_id="focus_enhancement_basic",
                skill_type=PassiveSkillType.FOCUS_ENHANCEMENT,
                name="?",
                description="ADHD支援30%?",
                effect_value=1.3,
                unlock_requirement=21,
                therapeutic_focus="Self-Discipline",
                visual_effect="focus_beam"
            ),
            PassiveSkill(
                skill_id="resilience_boost_basic",
                skill_type=PassiveSkillType.RESILIENCE_BOOST,
                name="?",
                description="?40%?",
                effect_value=1.4,
                unlock_requirement=30,
                therapeutic_focus="Resilience",
                visual_effect="phoenix_flame"
            ),
            PassiveSkill(
                skill_id="social_confidence_basic",
                skill_type=PassiveSkillType.SOCIAL_CONFIDENCE,
                name="?",
                description="?XPが50%?",
                effect_value=1.5,
                unlock_requirement=21,
                therapeutic_focus="Communication",
                visual_effect="confidence_glow"
            ),
            PassiveSkill(
                skill_id="creative_flow_basic",
                skill_type=PassiveSkillType.CREATIVE_FLOW,
                name="創",
                description="創",
                effect_value=1.25,
                unlock_requirement=21,
                therapeutic_focus="Creativity",
                visual_effect="inspiration_burst"
            ),
            PassiveSkill(
                skill_id="wisdom_insight_basic",
                skill_type=PassiveSkillType.WISDOM_INSIGHT,
                name="?",
                description="?",
                effect_value=1.3,
                unlock_requirement=21,
                therapeutic_focus="Wisdom",
                visual_effect="wisdom_eye"
            )
        ]
    
    async def update_efficacy_gauge(self, request: EfficacyUpdateRequest) -> Dict[str, Any]:
        """自動"""
        try:
            # ?
            current_gauge = await self._get_or_create_gauge(request.user_id, request.therapeutic_focus)
            
            # ?
            today = datetime.now().date()
            last_activity = current_gauge.last_activity_date.date() if current_gauge.last_activity_date else None
            
            if last_activity == today:
                # ?
                pass
            elif last_activity == today - timedelta(days=1) or last_activity is None:
                # ?
                if request.task_completed:
                    current_gauge.consecutive_days += 1
            elif last_activity is None or last_activity < today - timedelta(days=1):
                # ?
                if request.task_completed:
                    current_gauge.consecutive_days = 1
                else:
                    current_gauge.consecutive_days = 0
            
            # ?
            if last_activity != today and request.task_completed:
                current_gauge.total_days_active += 1
            
            # ?
            efficacy_increase = self._calculate_efficacy_increase(request, current_gauge)
            current_gauge.current_percentage = min(100.0, current_gauge.current_percentage + efficacy_increase)
            
            # レベル
            current_gauge.current_level = self._calculate_efficacy_level(current_gauge.current_percentage)
            
            # ?
            current_gauge.last_activity_date = datetime.now()
            
            # ?
            current_gauge.efficacy_history.append({
                "date": today.isoformat(),
                "percentage": current_gauge.current_percentage,
                "consecutive_days": current_gauge.consecutive_days,
                "efficacy_increase": efficacy_increase,
                "task_completed": request.task_completed,
                "mood_rating": request.mood_rating
            })
            
            # ?
            milestone_rewards = await self._check_milestones(current_gauge)
            
            # ?
            newly_unlocked_skills = await self._check_passive_skill_unlocks(current_gauge)
            
            return {
                "success": True,
                "gauge": current_gauge,
                "efficacy_increase": efficacy_increase,
                "milestone_rewards": milestone_rewards,
                "newly_unlocked_skills": newly_unlocked_skills,
                "celebration_message": self._generate_celebration_message(current_gauge, milestone_rewards)
            }
            
        except Exception as e:
            logger.error(f"Efficacy gauge update failed for user {request.user_id}: {e}")
            raise HTTPException(status_code=500, detail="自動")
    
    async def _get_or_create_gauge(self, user_id: str, therapeutic_focus: str) -> EfficacyGauge:
        """ゲーム"""
        # 実装Firestoreか
        # ?
        gauge_key = f"{user_id}_{therapeutic_focus}"
        if not hasattr(self, '_test_gauges'):
            self._test_gauges = {}
        
        if gauge_key in self._test_gauges:
            return self._test_gauges[gauge_key]
        
        # ?
        gauge = EfficacyGauge(
            user_id=user_id,
            therapeutic_focus=therapeutic_focus,
            current_level=EfficacyLevel.NOVICE,
            current_percentage=0.0,
            consecutive_days=0,
            total_days_active=0,
            last_activity_date=datetime.now() - timedelta(days=1),
            milestone_reached=[],
            passive_skills=[],
            efficacy_history=[]
        )
        
        self._test_gauges[gauge_key] = gauge
        return gauge
    
    def _calculate_efficacy_increase(self, request: EfficacyUpdateRequest, gauge: EfficacyGauge) -> float:
        """?"""
        if not request.task_completed:
            return 0.0
        
        base_increase = 2.0  # ?
        
        # ?
        consistency_bonus = min(gauge.consecutive_days * 0.1, 2.0)
        
        # タスク
        completion_bonus = 1.0 if request.task_completed else 0.0
        
        # ?
        difficulty_bonus = (request.task_difficulty - 2) * 0.3
        
        # ?
        reflection_bonus = (request.reflection_quality or 3) * 0.2
        
        # 気分
        mood_modifier = (request.mood_rating - 3) * 0.1
        
        total_increase = (
            base_increase +
            consistency_bonus * self.efficacy_formula_weights["consistency"] +
            completion_bonus * self.efficacy_formula_weights["task_completion"] +
            difficulty_bonus * self.efficacy_formula_weights["difficulty_challenge"] +
            reflection_bonus * self.efficacy_formula_weights["reflection_depth"] +
            mood_modifier
        )
        
        return max(0.1, total_increase)
    
    def _calculate_efficacy_level(self, percentage: float) -> EfficacyLevel:
        """?"""
        if percentage >= 81:
            return EfficacyLevel.EXPERT
        elif percentage >= 61:
            return EfficacyLevel.PROFICIENT
        elif percentage >= 41:
            return EfficacyLevel.COMPETENT
        elif percentage >= 21:
            return EfficacyLevel.DEVELOPING
        else:
            return EfficacyLevel.NOVICE
    
    async def _check_milestones(self, gauge: EfficacyGauge) -> List[Dict[str, Any]]:
        """?"""
        rewards = []
        
        for milestone in self.milestones:
            if (milestone.day <= gauge.consecutive_days and 
                milestone.day not in gauge.milestone_reached):
                
                gauge.milestone_reached.append(milestone.day)
                rewards.append({
                    "milestone": milestone,
                    "achieved_at": datetime.now().isoformat()
                })
        
        return rewards
    
    async def _check_passive_skill_unlocks(self, gauge: EfficacyGauge) -> List[PassiveSkill]:
        """?"""
        newly_unlocked = []
        
        for skill in self.passive_skills_pool:
            if (gauge.consecutive_days >= skill.unlock_requirement and
                skill.therapeutic_focus == gauge.therapeutic_focus and
                not any(s.skill_id == skill.skill_id for s in gauge.passive_skills)):
                
                skill.is_unlocked = True
                skill.unlocked_at = datetime.now()
                gauge.passive_skills.append(skill)
                newly_unlocked.append(skill)
        
        return newly_unlocked
    
    def _generate_celebration_message(self, gauge: EfficacyGauge, milestone_rewards: List[Dict[str, Any]]) -> str:
        """お"""
        if milestone_rewards:
            return milestone_rewards[-1]["milestone"].celebration_message
        
        if gauge.consecutive_days > 0:
            if gauge.consecutive_days % 10 == 0:
                return f"? {gauge.consecutive_days}?"
            elif gauge.consecutive_days % 5 == 0:
                return f"? {gauge.consecutive_days}?"
            else:
                return f"? {gauge.consecutive_days}?"
        
        return "?"
    
    async def get_efficacy_dashboard(self, user_id: str) -> Dict[str, Any]:
        """?"""
        # ?
        therapeutic_focuses = ["Self-Discipline", "Empathy", "Resilience", "Curiosity", 
                             "Communication", "Creativity", "Courage", "Wisdom"]
        
        gauges = {}
        total_efficacy = 0.0
        total_consecutive_days = 0
        
        for focus in therapeutic_focuses:
            gauge = await self._get_or_create_gauge(user_id, focus)
            gauges[focus] = gauge
            total_efficacy += gauge.current_percentage
            total_consecutive_days = max(total_consecutive_days, gauge.consecutive_days)
        
        average_efficacy = total_efficacy / len(therapeutic_focuses)
        
        # ?
        next_milestone = None
        for milestone in self.milestones:
            if milestone.day > total_consecutive_days:
                next_milestone = milestone
                break
        
        return {
            "user_id": user_id,
            "overall_efficacy_level": self._calculate_efficacy_level(average_efficacy),
            "average_efficacy_percentage": average_efficacy,
            "max_consecutive_days": total_consecutive_days,
            "therapeutic_gauges": gauges,
            "next_milestone": next_milestone,
            "total_passive_skills": sum(len(gauge.passive_skills) for gauge in gauges.values()),
            "efficacy_trend": self._calculate_efficacy_trend(gauges),
            "motivational_message": self._generate_motivational_message(average_efficacy, total_consecutive_days)
        }
    
    def _calculate_efficacy_trend(self, gauges: Dict[str, EfficacyGauge]) -> str:
        """?"""
        recent_changes = []
        
        for gauge in gauges.values():
            if len(gauge.efficacy_history) >= 2:
                recent = gauge.efficacy_history[-1]["percentage"]
                previous = gauge.efficacy_history[-2]["percentage"]
                recent_changes.append(recent - previous)
        
        if not recent_changes:
            return "stable"
        
        average_change = sum(recent_changes) / len(recent_changes)
        
        if average_change > 1.0:
            return "improving"
        elif average_change < -1.0:
            return "declining"
        else:
            return "stable"
    
    def _generate_motivational_message(self, average_efficacy: float, consecutive_days: int) -> str:
        """モデル"""
        if consecutive_days >= 21:
            return "? ?"
        elif consecutive_days >= 14:
            return "? 2?"
        elif consecutive_days >= 7:
            return "? 1?"
        elif consecutive_days >= 3:
            return "? ?"
        elif average_efficacy >= 50:
            return "? 自動"
        else:
            return "? ?"

# ?
efficacy_engine = SelfEfficacyEngine()

# APIエラー

@app.post("/efficacy/update")
async def update_efficacy_gauge(request: EfficacyUpdateRequest):
    """自動"""
    return await efficacy_engine.update_efficacy_gauge(request)

@app.get("/efficacy/{user_id}/dashboard")
async def get_efficacy_dashboard(user_id: str):
    """?"""
    return await efficacy_engine.get_efficacy_dashboard(user_id)

@app.get("/efficacy/{user_id}/{therapeutic_focus}")
async def get_specific_gauge(user_id: str, therapeutic_focus: str):
    """?"""
    gauge = await efficacy_engine._get_or_create_gauge(user_id, therapeutic_focus)
    return {
        "gauge": gauge,
        "available_skills": [skill for skill in efficacy_engine.passive_skills_pool 
                           if skill.therapeutic_focus == therapeutic_focus],
        "next_milestone": next((m for m in efficacy_engine.milestones 
                              if m.day > gauge.consecutive_days), None)
    }

@app.get("/efficacy/milestones")
async def get_milestones():
    """?"""
    return {
        "milestones": efficacy_engine.milestones,
        "description": "?"
    }

@app.get("/efficacy/passive-skills")
async def get_passive_skills():
    """?"""
    return {
        "passive_skills": efficacy_engine.passive_skills_pool,
        "description": "?"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)