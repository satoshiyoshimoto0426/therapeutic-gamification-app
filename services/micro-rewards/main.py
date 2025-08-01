"""
Micro Rewards Service - ?3?

?
- ログ3タスク3?XP/?
- ADHDの
- ?
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import asyncio
import json

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="Micro Rewards Service", version="1.0.0")
logger = logging.getLogger(__name__)

class RewardType(Enum):
    INSTANT_XP = "instant_xp"           # ?XP?
    VISUAL_EFFECT = "visual_effect"     # ?
    SOUND_FEEDBACK = "sound_feedback"   # ?
    PROGRESS_PULSE = "progress_pulse"   # ?
    ACHIEVEMENT_BADGE = "achievement_badge"  # ?
    STREAK_BONUS = "streak_bonus"       # ?
    RECOVERY_BOOST = "recovery_boost"   # リスト

class MicroReward(BaseModel):
    reward_id: str
    reward_type: RewardType
    title: str
    description: str
    xp_value: int
    visual_effect: str
    sound_effect: str
    duration_ms: int  # ?
    trigger_condition: str
    celebration_message: str

class UserAction(BaseModel):
    user_id: str
    action_type: str  # "login", "task_start", "task_complete", "daily_check"
    timestamp: datetime
    context: Dict[str, Any]

class RewardResponse(BaseModel):
    success: bool
    rewards: List[MicroReward]
    total_xp: int
    celebration_message: str
    next_action_hint: str
    execution_time_ms: int

class UserEngagementState(BaseModel):
    user_id: str
    last_login: datetime
    consecutive_days: int
    daily_actions: int
    total_actions: int
    last_reward_time: datetime
    recovery_boost_active: bool
    recovery_boost_multiplier: float
    engagement_streak: int
    missed_days: int

class MicroRewardsEngine:
    def __init__(self):
        self.reward_templates = self._initialize_reward_templates()
        self.user_states = {}  # 実装Redisを
        self.websocket_connections = {}  # リスト
        
        # ADHD?
        self.max_response_time_ms = 1200  # 1.2?
        self.recovery_boost_threshold = 2  # 2?
        self.recovery_boost_multiplier = 1.2  # 20%?
        self.max_daily_rewards = 50  # 1?50?
    
    def _initialize_reward_templates(self) -> List[MicroReward]:
        """?"""
        return [
            # ログ
            MicroReward(
                reward_id="instant_login",
                reward_type=RewardType.INSTANT_XP,
                title="お",
                description="ログ",
                xp_value=5,
                visual_effect="welcome_sparkle",
                sound_effect="gentle_chime",
                duration_ms=800,
                trigger_condition="login",
                celebration_message="? ?"
            ),
            
            # タスク
            MicroReward(
                reward_id="task_start_boost",
                reward_type=RewardType.VISUAL_EFFECT,
                title="ストーリー",
                description="タスク",
                xp_value=3,
                visual_effect="start_glow",
                sound_effect="start_bell",
                duration_ms=600,
                trigger_condition="task_start",
                celebration_message="? ?"
            ),
            
            # タスク
            MicroReward(
                reward_id="task_complete_celebration",
                reward_type=RewardType.ACHIEVEMENT_BADGE,
                title="?",
                description="タスク",
                xp_value=15,
                visual_effect="completion_burst",
                sound_effect="success_fanfare",
                duration_ms=1000,
                trigger_condition="task_complete",
                celebration_message="? や"
            ),
            
            # ?
            MicroReward(
                reward_id="progress_pulse",
                reward_type=RewardType.PROGRESS_PULSE,
                title="?",
                description="?",
                xp_value=2,
                visual_effect="progress_wave",
                sound_effect="gentle_pulse",
                duration_ms=400,
                trigger_condition="progress_check",
                celebration_message="? ?"
            ),
            
            # ?
            MicroReward(
                reward_id="streak_bonus",
                reward_type=RewardType.STREAK_BONUS,
                title="?",
                description="?",
                xp_value=10,
                visual_effect="streak_fire",
                sound_effect="streak_chime",
                duration_ms=1200,
                trigger_condition="streak_milestone",
                celebration_message="? ?"
            ),
            
            # リスト
            MicroReward(
                reward_id="recovery_boost",
                reward_type=RewardType.RECOVERY_BOOST,
                title="お",
                description="?",
                xp_value=20,
                visual_effect="recovery_aura",
                sound_effect="welcome_back",
                duration_ms=1500,
                trigger_condition="recovery_login",
                celebration_message="? お"
            ),
            
            # 3?
            MicroReward(
                reward_id="speed_bonus",
                reward_type=RewardType.INSTANT_XP,
                title="ストーリー",
                description="3?",
                xp_value=8,
                visual_effect="speed_trail",
                sound_effect="speed_whoosh",
                duration_ms=700,
                trigger_condition="speed_complete",
                celebration_message="? 3?"
            ),
            
            # 3タスク
            MicroReward(
                reward_id="efficiency_bonus",
                reward_type=RewardType.VISUAL_EFFECT,
                title="?",
                description="3タスク",
                xp_value=5,
                visual_effect="efficiency_glow",
                sound_effect="efficiency_ding",
                duration_ms=500,
                trigger_condition="tap_efficiency",
                celebration_message="? 3タスク"
            )
        ]
    
    async def process_user_action(self, action: UserAction) -> RewardResponse:
        """ユーザー"""
        start_time = datetime.now()
        
        try:
            # ユーザー
            user_state = await self._get_or_create_user_state(action.user_id)
            await self._update_user_state(user_state, action)
            
            # ?
            applicable_rewards = await self._determine_applicable_rewards(action, user_state)
            
            # リスト
            if user_state.recovery_boost_active:
                applicable_rewards = self._apply_recovery_boost(applicable_rewards, user_state)
            
            # XP?
            total_xp = sum(reward.xp_value for reward in applicable_rewards)
            
            # お
            celebration_message = self._generate_celebration_message(applicable_rewards, user_state)
            
            # ?
            next_hint = self._generate_next_action_hint(action, user_state)
            
            # 実装
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # WebSocket?
            await self._send_realtime_notification(action.user_id, applicable_rewards)
            
            response = RewardResponse(
                success=True,
                rewards=applicable_rewards,
                total_xp=total_xp,
                celebration_message=celebration_message,
                next_action_hint=next_hint,
                execution_time_ms=int(execution_time)
            )
            
            # ?
            if execution_time > self.max_response_time_ms:
                logger.warning(f"Slow micro reward response: {execution_time}ms for user {action.user_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Micro reward processing failed for user {action.user_id}: {e}")
            # エラー
            return RewardResponse(
                success=False,
                rewards=[self.reward_templates[0]],  # 基本
                total_xp=5,
                celebration_message="? お",
                next_action_hint="?",
                execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def _get_or_create_user_state(self, user_id: str) -> UserEngagementState:
        """ユーザー"""
        if user_id not in self.user_states:
            self.user_states[user_id] = UserEngagementState(
                user_id=user_id,
                last_login=datetime.now(),
                consecutive_days=0,
                daily_actions=0,
                total_actions=0,
                last_reward_time=datetime.now(),
                recovery_boost_active=False,
                recovery_boost_multiplier=1.0,
                engagement_streak=0,
                missed_days=0
            )
        
        return self.user_states[user_id]
    
    async def _update_user_state(self, user_state: UserEngagementState, action: UserAction):
        """ユーザー"""
        now = datetime.now()
        today = now.date()
        last_login_date = user_state.last_login.date()
        
        # ログ
        if action.action_type == "login":
            if last_login_date == today:
                # ?
                pass
            elif last_login_date == today - timedelta(days=1):
                # ?
                user_state.consecutive_days += 1
                user_state.daily_actions = 0  # ?
            else:
                # ログ
                days_missed = (today - last_login_date).days - 1
                user_state.missed_days = days_missed
                
                if days_missed >= self.recovery_boost_threshold:
                    user_state.recovery_boost_active = True
                    user_state.recovery_boost_multiplier = self.recovery_boost_multiplier
                
                user_state.consecutive_days = 1
                user_state.daily_actions = 0
            
            user_state.last_login = now
        
        # アプリ
        user_state.daily_actions += 1
        user_state.total_actions += 1
        user_state.last_reward_time = now
    
    async def _determine_applicable_rewards(self, action: UserAction, user_state: UserEngagementState) -> List[MicroReward]:
        """?"""
        applicable_rewards = []
        
        # 基本
        for template in self.reward_templates:
            if self._matches_trigger_condition(template, action, user_state):
                applicable_rewards.append(template)
        
        # 1?
        if user_state.daily_actions > self.max_daily_rewards:
            applicable_rewards = applicable_rewards[:1]  # ?1つ
        
        return applicable_rewards
    
    def _matches_trigger_condition(self, template: MicroReward, action: UserAction, user_state: UserEngagementState) -> bool:
        """?"""
        condition = template.trigger_condition
        
        if condition == "login" and action.action_type == "login":
            return True
        elif condition == "task_start" and action.action_type == "task_start":
            return True
        elif condition == "task_complete" and action.action_type == "task_complete":
            return True
        elif condition == "progress_check" and action.action_type == "progress_check":
            return True
        elif condition == "streak_milestone" and action.action_type == "login" and user_state.consecutive_days % 5 == 0:
            return True
        elif condition == "recovery_login" and action.action_type == "login" and user_state.recovery_boost_active:
            return True
        elif condition == "speed_complete" and action.action_type == "task_complete":
            # 3?
            task_duration = action.context.get("duration_seconds", 0)
            return task_duration <= 180  # 3? = 180?
        elif condition == "tap_efficiency" and action.action_type == "task_complete":
            # 3タスク
            tap_count = action.context.get("tap_count", 0)
            return tap_count <= 3
        
        return False
    
    def _apply_recovery_boost(self, rewards: List[MicroReward], user_state: UserEngagementState) -> List[MicroReward]:
        """リスト"""
        boosted_rewards = []
        
        for reward in rewards:
            boosted_reward = reward.copy()
            boosted_reward.xp_value = int(reward.xp_value * user_state.recovery_boost_multiplier)
            boosted_rewards.append(boosted_reward)
        
        # ?
        user_state.recovery_boost_active = False
        user_state.recovery_boost_multiplier = 1.0
        
        return boosted_rewards
    
    def _generate_celebration_message(self, rewards: List[MicroReward], user_state: UserEngagementState) -> str:
        """お"""
        if not rewards:
            return "? お"
        
        # ?
        primary_reward = max(rewards, key=lambda r: r.xp_value)
        message = primary_reward.celebration_message
        
        # ?
        if user_state.consecutive_days >= 7:
            message += f" ({user_state.consecutive_days}?)"
        
        return message
    
    def _generate_next_action_hint(self, action: UserAction, user_state: UserEngagementState) -> str:
        """?"""
        hints = {
            "login": "?Daily Trioを",
            "task_start": "?",
            "task_complete": "?",
            "progress_check": "?"
        }
        
        base_hint = hints.get(action.action_type, "?")
        
        # ?
        current_hour = datetime.now().hour
        if current_hour < 12:
            return f"? {base_hint}"
        elif current_hour < 18:
            return f"? {base_hint}"
        else:
            return f"? {base_hint}"
    
    async def _send_realtime_notification(self, user_id: str, rewards: List[MicroReward]):
        """リスト"""
        if user_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[user_id]
                notification = {
                    "type": "micro_reward",
                    "rewards": [reward.dict() for reward in rewards],
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(notification))
            except Exception as e:
                logger.error(f"WebSocket notification failed for user {user_id}: {e}")
    
    async def get_user_engagement_stats(self, user_id: str) -> Dict[str, Any]:
        """ユーザー"""
        user_state = await self._get_or_create_user_state(user_id)
        
        return {
            "user_id": user_id,
            "consecutive_days": user_state.consecutive_days,
            "daily_actions": user_state.daily_actions,
            "total_actions": user_state.total_actions,
            "engagement_streak": user_state.engagement_streak,
            "recovery_boost_available": user_state.recovery_boost_active,
            "last_login": user_state.last_login.isoformat(),
            "performance_metrics": {
                "average_response_time_ms": 800,  # 実装
                "three_tap_completion_rate": 0.85,
                "three_minute_completion_rate": 0.92
            }
        }

# ?
micro_rewards_engine = MicroRewardsEngine()

# APIエラー

@app.post("/micro-rewards/action", response_model=RewardResponse)
async def process_action(action: UserAction):
    """ユーザー"""
    return await micro_rewards_engine.process_user_action(action)

@app.get("/micro-rewards/{user_id}/stats")
async def get_engagement_stats(user_id: str):
    """エラー"""
    return await micro_rewards_engine.get_user_engagement_stats(user_id)

@app.get("/micro-rewards/templates")
async def get_reward_templates():
    """リスト"""
    return {
        "templates": micro_rewards_engine.reward_templates,
        "performance_targets": {
            "max_response_time_ms": micro_rewards_engine.max_response_time_ms,
            "recovery_boost_threshold_days": micro_rewards_engine.recovery_boost_threshold,
            "recovery_boost_multiplier": micro_rewards_engine.recovery_boost_multiplier
        }
    }

@app.websocket("/micro-rewards/{user_id}/realtime")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """リストWebSocket"""
    await websocket.accept()
    micro_rewards_engine.websocket_connections[user_id] = websocket
    
    try:
        while True:
            # ?ping
            await asyncio.sleep(30)
            await websocket.ping()
    except WebSocketDisconnect:
        if user_id in micro_rewards_engine.websocket_connections:
            del micro_rewards_engine.websocket_connections[user_id]

# 3タスク3?
@app.post("/micro-rewards/quick-action")
async def quick_action_reward(user_id: str, action_type: str, tap_count: int, duration_seconds: int):
    """3タスク3?"""
    action = UserAction(
        user_id=user_id,
        action_type=action_type,
        timestamp=datetime.now(),
        context={
            "tap_count": tap_count,
            "duration_seconds": duration_seconds,
            "quick_action": True
        }
    )
    
    response = await micro_rewards_engine.process_user_action(action)
    
    # ?
    if response.execution_time_ms > 1200:
        logger.warning(f"Quick action exceeded 1.2s limit: {response.execution_time_ms}ms")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)