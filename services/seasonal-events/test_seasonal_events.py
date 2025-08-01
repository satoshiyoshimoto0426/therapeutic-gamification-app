"""
?
"""

import pytest
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.seasonal_events.main import (
    SeasonalEventSystem, GuildSystem, CommunityGoalSystem, EngagementSystem,
    EventType, EventStatus, SeasonalEvent, Guild, CommunityGoal
)

class TestSeasonalEventSystem:
    """?"""
    
    def setup_method(self):
        self.event_system = SeasonalEventSystem()
    
    def test_create_seasonal_event(self):
        """?"""
        event = self.event_system.create_seasonal_event("spring_renewal")
        
        assert event is not None
        assert event.name == "?"
        assert event.event_type == EventType.SEASONAL
        assert event.status == EventStatus.ACTIVE
        assert "new_habits_started" in event.requirements
        assert event.requirements["new_habits_started"] == 3
        assert event.rewards["xp"] == 200
    
    def test_create_invalid_seasonal_event(self):
        """無"""
        event = self.event_system.create_seasonal_event("invalid_season")
        assert event is None
    
    def test_check_event_completion_success(self):
        """?"""
        event = self.event_system.create_seasonal_event("spring_renewal")
        
        user_progress = {
            "new_habits_started": 3,
            "consecutive_days": 7
        }
        
        is_completed = self.event_system.check_event_completion(event.event_id, user_progress)
        assert is_completed is True
    
    def test_check_event_completion_failure(self):
        """?"""
        event = self.event_system.create_seasonal_event("spring_renewal")
        
        user_progress = {
            "new_habits_started": 2,  # ?
            "consecutive_days": 7
        }
        
        is_completed = self.event_system.check_event_completion(event.event_id, user_progress)
        assert is_completed is False
    
    def test_get_active_events(self):
        """アプリ"""
        # ?
        current_event = self.event_system.create_seasonal_event("spring_renewal")
        
        # ?
        past_event = self.event_system.create_seasonal_event("summer_energy")
        past_event.start_date = datetime.now() - timedelta(days=30)
        past_event.end_date = datetime.now() - timedelta(days=10)
        
        active_events = self.event_system.get_active_events()
        
        assert len(active_events) == 1
        assert active_events[0].event_id == current_event.event_id
        assert active_events[0].status == EventStatus.ACTIVE

class TestGuildSystem:
    """?"""
    
    def setup_method(self):
        self.guild_system = GuildSystem()
    
    def test_create_guild(self):
        """?"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        assert guild.name == "?"
        assert guild.leader_uid == "user_001"
        assert "user_001" in guild.members
        assert len(guild.members) == 1
        assert guild.therapeutic_focus == "adhd_peer"
        assert guild.is_active is True
    
    def test_join_guild(self):
        """?"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        success = self.guild_system.join_guild(guild.guild_id, "user_002")
        
        assert success is True
        assert "user_002" in guild.members
        assert len(guild.members) == 2
        assert self.guild_system.user_guild_mapping["user_002"] == guild.guild_id
    
    def test_join_full_guild(self):
        """?"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        # ?
        for i in range(2, 11):  # user_002 か user_010 ま
            self.guild_system.join_guild(guild.guild_id, f"user_{i:03d}")
        
        # ?
        success = self.guild_system.join_guild(guild.guild_id, "user_011")
        
        assert success is False
        assert len(guild.members) == 10
    
    def test_leave_guild(self):
        """?"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        self.guild_system.join_guild(guild.guild_id, "user_002")
        
        success = self.guild_system.leave_guild("user_002")
        
        assert success is True
        assert "user_002" not in guild.members
        assert "user_002" not in self.guild_system.user_guild_mapping
    
    def test_leader_leave_guild(self):
        """リスト"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        self.guild_system.join_guild(guild.guild_id, "user_002")
        
        # リスト
        success = self.guild_system.leave_guild("user_001")
        
        assert success is True
        assert guild.leader_uid == "user_002"  # ?
        assert "user_001" not in guild.members
    
    def test_add_guild_xp(self):
        """?XP?"""
        guild = self.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        initial_level = guild.guild_level
        
        # 1500 XPを
        self.guild_system.add_guild_xp(guild.guild_id, 1500)
        
        assert guild.total_xp == 1500
        assert guild.guild_level == initial_level + 1
    
    def test_get_guild_leaderboard(self):
        """?"""
        guild1 = self.guild_system.create_guild("user_001", "?1", "?1", "adhd_peer")
        guild2 = self.guild_system.create_guild("user_002", "?2", "?2", "anxiety_support")
        guild3 = self.guild_system.create_guild("user_003", "?3", "?3", "social_reintegration")
        
        # ?XPを
        self.guild_system.add_guild_xp(guild1.guild_id, 500)
        self.guild_system.add_guild_xp(guild2.guild_id, 1500)
        self.guild_system.add_guild_xp(guild3.guild_id, 1000)
        
        leaderboard = self.guild_system.get_guild_leaderboard()
        
        assert len(leaderboard) == 3
        assert leaderboard[0].guild_id == guild2.guild_id  # ?XP
        assert leaderboard[1].guild_id == guild3.guild_id  # 2?
        assert leaderboard[2].guild_id == guild1.guild_id  # ?XP

class TestCommunityGoalSystem:
    """コア"""
    
    def setup_method(self):
        self.goal_system = CommunityGoalSystem()
    
    def test_create_community_goal(self):
        """コア"""
        goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50, "coins": 25}
        )
        
        assert goal.title == "?"
        assert goal.target_value == 100
        assert goal.current_value == 0
        assert goal.is_completed is False
        assert len(goal.participating_users) == 0
    
    def test_contribute_to_goal(self):
        """コア"""
        goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50, "coins": 25}
        )
        
        success = self.goal_system.contribute_to_goal(goal.goal_id, "user_001", 25)
        
        assert success is True
        assert goal.current_value == 25
        assert "user_001" in goal.participating_users
        assert goal.is_completed is False
    
    def test_goal_completion(self):
        """コア"""
        goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50, "coins": 25}
        )
        
        # ?
        self.goal_system.contribute_to_goal(goal.goal_id, "user_001", 60)
        self.goal_system.contribute_to_goal(goal.goal_id, "user_002", 40)
        
        assert goal.current_value == 100
        assert goal.is_completed is True
        assert len(goal.participating_users) == 2
    
    def test_expired_goal_contribution(self):
        """?"""
        goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50, "coins": 25}
        )
        
        # ?
        goal.end_date = datetime.now() - timedelta(days=1)
        
        success = self.goal_system.contribute_to_goal(goal.goal_id, "user_001", 25)
        
        assert success is False
        assert goal.current_value == 0
    
    def test_get_active_community_goals(self):
        """アプリ"""
        # アプリ
        active_goal = self.goal_system.create_community_goal(
            title="アプリ",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50}
        )
        
        # ?
        completed_goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=50,
            duration_days=7,
            reward_per_participant={"xp": 50}
        )
        completed_goal.is_completed = True
        
        # ?
        expired_goal = self.goal_system.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50}
        )
        expired_goal.end_date = datetime.now() - timedelta(days=1)
        
        active_goals = self.goal_system.get_active_community_goals()
        
        assert len(active_goals) == 1
        assert active_goals[0].goal_id == active_goal.goal_id

class TestEngagementSystem:
    """エラー"""
    
    def setup_method(self):
        self.engagement = EngagementSystem()
    
    def test_get_user_engagement_data(self):
        """ユーザー"""
        # ?
        guild = self.engagement.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        # ?
        event = self.engagement.seasonal_events.create_seasonal_event("spring_renewal")
        
        # コア
        goal = self.engagement.community_goals.create_community_goal(
            title="?",
            description="?",
            target_value=100,
            duration_days=7,
            reward_per_participant={"xp": 50}
        )
        
        engagement_data = self.engagement.get_user_engagement_data("user_001")
        
        assert engagement_data["user_guild"] is not None
        assert engagement_data["user_guild"]["name"] == "?"
        assert len(engagement_data["active_events"]) == 1
        assert engagement_data["active_events"][0]["name"] == "?"
        assert len(engagement_data["community_goals"]) == 1
        assert engagement_data["community_goals"][0]["title"] == "?"
    
    def test_process_user_action(self):
        """ユーザー"""
        # ?
        guild = self.engagement.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        # コア
        goal = self.engagement.community_goals.create_community_goal(
            title="タスク",
            description="み",
            target_value=10,
            duration_days=7,
            reward_per_participant={"xp": 50}
        )
        
        initial_guild_xp = guild.total_xp
        initial_goal_value = goal.current_value
        
        # ユーザー
        self.engagement.process_user_action("user_001", "task_completed", 2)
        
        # ?XPが
        assert guild.total_xp == initial_guild_xp + 20  # 2 * 10
        
        # コア
        assert goal.current_value == initial_goal_value + 2
        assert "user_001" in goal.participating_users

if __name__ == "__main__":
    pytest.main([__file__, "-v"])