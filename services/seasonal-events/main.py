"""
?

こ
- ?
- ?
- コア
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

class EventType(Enum):
    SEASONAL = "seasonal"
    LIMITED_TIME = "limited_time"
    COMMUNITY = "community"
    GUILD = "guild"

class EventStatus(Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class SeasonalEvent:
    """?"""
    event_id: str
    name: str
    description: str
    event_type: EventType
    start_date: datetime
    end_date: datetime
    status: EventStatus
    rewards: Dict[str, int]  # {"xp": 100, "coins": 50, "items": ["spring_flower"]}
    requirements: Dict[str, int]  # {"tasks_completed": 10, "social_interactions": 5}
    therapeutic_theme: str
    participation_count: int = 0
    max_participants: Optional[int] = None

@dataclass
class Guild:
    """?"""
    guild_id: str
    name: str
    description: str
    leader_uid: str
    members: List[str]
    max_members: int = 10
    created_date: datetime
    guild_level: int = 1
    total_xp: int = 0
    therapeutic_focus: str  # "anxiety_support", "adhd_peer", "social_reintegration"
    is_active: bool = True

@dataclass
class CommunityGoal:
    """コア"""
    goal_id: str
    title: str
    description: str
    target_value: int
    current_value: int = 0
    start_date: datetime
    end_date: datetime
    reward_per_participant: Dict[str, int]
    participating_users: List[str]
    is_completed: bool = False

class SeasonalEventSystem:
    """?"""
    
    def __init__(self):
        self.active_events: Dict[str, SeasonalEvent] = {}
        self.event_templates = self._initialize_seasonal_templates()
    
    def _initialize_seasonal_templates(self) -> Dict[str, dict]:
        """?"""
        return {
            "spring_renewal": {
                "name": "?",
                "description": "?",
                "therapeutic_theme": "?",
                "duration_days": 14,
                "requirements": {"new_habits_started": 3, "consecutive_days": 7},
                "rewards": {"xp": 200, "coins": 150, "items": ["spring_crystal", "renewal_badge"]}
            },
            "summer_energy": {
                "name": "?",
                "description": "?",
                "therapeutic_theme": "?",
                "duration_days": 21,
                "requirements": {"physical_tasks": 15, "social_tasks": 8},
                "rewards": {"xp": 300, "coins": 200, "items": ["energy_potion", "summer_crown"]}
            },
            "autumn_reflection": {
                "name": "?",
                "description": "こ",
                "therapeutic_theme": "?",
                "duration_days": 10,
                "requirements": {"reflection_entries": 10, "gratitude_tasks": 5},
                "rewards": {"xp": 250, "coins": 180, "items": ["wisdom_scroll", "gratitude_gem"]}
            },
            "winter_warmth": {
                "name": "?",
                "description": "?",
                "therapeutic_theme": "つ",
                "duration_days": 18,
                "requirements": {"guild_activities": 10, "support_messages": 15},
                "rewards": {"xp": 280, "coins": 220, "items": ["warmth_cloak", "bond_ring"]}
            }
        }
    
    def create_seasonal_event(self, season: str) -> Optional[SeasonalEvent]:
        """?"""
        if season not in self.event_templates:
            return None
        
        template = self.event_templates[season]
        event_id = f"{season}_{datetime.now().year}_{uuid.uuid4().hex[:8]}"
        
        event = SeasonalEvent(
            event_id=event_id,
            name=template["name"],
            description=template["description"],
            event_type=EventType.SEASONAL,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=template["duration_days"]),
            status=EventStatus.ACTIVE,
            rewards=template["rewards"],
            requirements=template["requirements"],
            therapeutic_theme=template["therapeutic_theme"]
        )
        
        self.active_events[event_id] = event
        return event
    
    def check_event_completion(self, event_id: str, user_progress: Dict[str, int]) -> bool:
        """?"""
        if event_id not in self.active_events:
            return False
        
        event = self.active_events[event_id]
        
        for requirement, target_value in event.requirements.items():
            if user_progress.get(requirement, 0) < target_value:
                return False
        
        return True
    
    def get_active_events(self) -> List[SeasonalEvent]:
        """アプリ"""
        now = datetime.now()
        active_events = []
        
        for event in self.active_events.values():
            if event.start_date <= now <= event.end_date:
                event.status = EventStatus.ACTIVE
                active_events.append(event)
            elif now > event.end_date:
                event.status = EventStatus.EXPIRED
        
        return active_events

class GuildSystem:
    """?"""
    
    def __init__(self):
        self.guilds: Dict[str, Guild] = {}
        self.user_guild_mapping: Dict[str, str] = {}  # uid -> guild_id
    
    def create_guild(self, leader_uid: str, name: str, description: str, 
                    therapeutic_focus: str) -> Guild:
        """?"""
        guild_id = f"guild_{uuid.uuid4().hex[:12]}"
        
        guild = Guild(
            guild_id=guild_id,
            name=name,
            description=description,
            leader_uid=leader_uid,
            members=[leader_uid],
            created_date=datetime.now(),
            therapeutic_focus=therapeutic_focus
        )
        
        self.guilds[guild_id] = guild
        self.user_guild_mapping[leader_uid] = guild_id
        
        return guild
    
    def join_guild(self, guild_id: str, user_uid: str) -> bool:
        """?"""
        if guild_id not in self.guilds:
            return False
        
        guild = self.guilds[guild_id]
        
        if len(guild.members) >= guild.max_members:
            return False
        
        if user_uid in guild.members:
            return False
        
        guild.members.append(user_uid)
        self.user_guild_mapping[user_uid] = guild_id
        
        return True
    
    def leave_guild(self, user_uid: str) -> bool:
        """?"""
        if user_uid not in self.user_guild_mapping:
            return False
        
        guild_id = self.user_guild_mapping[user_uid]
        guild = self.guilds[guild_id]
        
        if user_uid in guild.members:
            guild.members.remove(user_uid)
            del self.user_guild_mapping[user_uid]
            
            # リスト
            if guild.leader_uid == user_uid and guild.members:
                guild.leader_uid = guild.members[0]
            elif not guild.members:
                guild.is_active = False
            
            return True
        
        return False
    
    def get_user_guild(self, user_uid: str) -> Optional[Guild]:
        """ユーザー"""
        if user_uid not in self.user_guild_mapping:
            return None
        
        guild_id = self.user_guild_mapping[user_uid]
        return self.guilds.get(guild_id)
    
    def add_guild_xp(self, guild_id: str, xp_amount: int):
        """?XPの"""
        if guild_id in self.guilds:
            guild = self.guilds[guild_id]
            guild.total_xp += xp_amount
            
            # ?1000 XP?
            new_level = (guild.total_xp // 1000) + 1
            guild.guild_level = new_level
    
    def get_guild_leaderboard(self) -> List[Guild]:
        """?"""
        active_guilds = [g for g in self.guilds.values() if g.is_active]
        return sorted(active_guilds, key=lambda g: g.total_xp, reverse=True)

class CommunityGoalSystem:
    """コア"""
    
    def __init__(self):
        self.community_goals: Dict[str, CommunityGoal] = {}
    
    def create_community_goal(self, title: str, description: str, 
                            target_value: int, duration_days: int,
                            reward_per_participant: Dict[str, int]) -> CommunityGoal:
        """コア"""
        goal_id = f"goal_{uuid.uuid4().hex[:12]}"
        
        goal = CommunityGoal(
            goal_id=goal_id,
            title=title,
            description=description,
            target_value=target_value,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            reward_per_participant=reward_per_participant,
            participating_users=[]
        )
        
        self.community_goals[goal_id] = goal
        return goal
    
    def contribute_to_goal(self, goal_id: str, user_uid: str, contribution: int) -> bool:
        """コア"""
        if goal_id not in self.community_goals:
            return False
        
        goal = self.community_goals[goal_id]
        
        if datetime.now() > goal.end_date:
            return False
        
        if user_uid not in goal.participating_users:
            goal.participating_users.append(user_uid)
        
        goal.current_value += contribution
        
        # ?
        if goal.current_value >= goal.target_value and not goal.is_completed:
            goal.is_completed = True
            self._distribute_community_rewards(goal)
        
        return True
    
    def _distribute_community_rewards(self, goal: CommunityGoal):
        """コア"""
        # 実装
        print(f"コア '{goal.title}' が")
        print(f"? {len(goal.participating_users)} ?")
    
    def get_active_community_goals(self) -> List[CommunityGoal]:
        """アプリ"""
        now = datetime.now()
        return [goal for goal in self.community_goals.values() 
                if goal.start_date <= now <= goal.end_date and not goal.is_completed]

# メイン
class EngagementSystem:
    """ゲーム"""
    
    def __init__(self):
        self.seasonal_events = SeasonalEventSystem()
        self.guild_system = GuildSystem()
        self.community_goals = CommunityGoalSystem()
    
    def get_user_engagement_data(self, user_uid: str) -> Dict:
        """ユーザー"""
        user_guild = self.guild_system.get_user_guild(user_uid)
        active_events = self.seasonal_events.get_active_events()
        active_goals = self.community_goals.get_active_community_goals()
        
        return {
            "user_guild": asdict(user_guild) if user_guild else None,
            "active_events": [asdict(event) for event in active_events],
            "community_goals": [asdict(goal) for goal in active_goals],
            "guild_leaderboard": [asdict(guild) for guild in self.guild_system.get_guild_leaderboard()[:10]]
        }
    
    def process_user_action(self, user_uid: str, action_type: str, value: int = 1):
        """ユーザー"""
        # ?XPの
        user_guild = self.guild_system.get_user_guild(user_uid)
        if user_guild:
            self.guild_system.add_guild_xp(user_guild.guild_id, value * 10)
        
        # コア
        for goal in self.community_goals.get_active_community_goals():
            if action_type in ["task_completed", "social_interaction", "reflection_entry"]:
                self.community_goals.contribute_to_goal(goal.goal_id, user_uid, value)

if __name__ == "__main__":
    # システム
    engagement = EngagementSystem()
    
    # ?
    spring_event = engagement.seasonal_events.create_seasonal_event("spring_renewal")
    print(f"?: {spring_event.name}")
    
    # ?
    guild = engagement.guild_system.create_guild(
        leader_uid="user_001",
        name="ADHD支援",
        description="ADHD?",
        therapeutic_focus="adhd_peer"
    )
    print(f"?: {guild.name}")
    
    # コア
    community_goal = engagement.community_goals.create_community_goal(
        title="み1000タスク",
        description="コア1000?",
        target_value=1000,
        duration_days=30,
        reward_per_participant={"xp": 100, "coins": 50}
    )
    print(f"コア: {community_goal.title}")
    
    # ユーザー
    engagement_data = engagement.get_user_engagement_data("user_001")
    print(f"エラー: {json.dumps(engagement_data, indent=2, default=str)}")