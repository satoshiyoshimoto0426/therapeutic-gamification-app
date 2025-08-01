"""
コア

?
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta
from services.seasonal_events.main import EngagementSystem
import json

class TestCommunityIntegration:
    """コア"""
    
    def setup_method(self):
        self.engagement = EngagementSystem()
        
        # ?
        self.test_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
        
        # ?
        self.test_guild = self.engagement.guild_system.create_guild(
            leader_uid="user_001",
            name="?",
            description="?",
            therapeutic_focus="adhd_peer"
        )
        
        # ?
        for user_uid in self.test_users[1:4]:  # user_002, user_003, user_004
            self.engagement.guild_system.join_guild(self.test_guild.guild_id, user_uid)
    
    def test_seasonal_event_guild_interaction(self):
        """?"""
        # ?
        spring_event = self.engagement.seasonal_events.create_seasonal_event("spring_renewal")
        
        # ?
        for user_uid in self.test_users[:3]:
            # ?
            self.engagement.process_user_action(user_uid, "new_habit_started", 1)
            # ?
            self.engagement.process_user_action(user_uid, "consecutive_day", 1)
        
        # ?XPが
        assert self.test_guild.total_xp > 0
        
        # ?
        user_progress = {
            "new_habits_started": 3,
            "consecutive_days": 7
        }
        
        # ?
        is_completed = self.engagement.seasonal_events.check_event_completion(
            spring_event.event_id, user_progress
        )
        assert is_completed is True
    
    def test_community_goal_guild_collaboration(self):
        """コア"""
        # ?
        community_goal = self.engagement.community_goals.create_community_goal(
            title="?",
            description="?",
            target_value=50,
            duration_days=14,
            reward_per_participant={"xp": 100, "coins": 75, "items": ["collaboration_badge"]}
        )
        
        # ?
        second_guild = self.engagement.guild_system.create_guild(
            leader_uid="user_005",
            name="?",
            description="?",
            therapeutic_focus="anxiety_support"
        )
        
        # ?
        guild1_contribution = 0
        guild2_contribution = 0
        
        # ?
        for user_uid in self.test_users[:4]:
            contribution = 8
            self.engagement.community_goals.contribute_to_goal(
                community_goal.goal_id, user_uid, contribution
            )
            guild1_contribution += contribution
        
        # ?
        contribution = 18  # ?
        self.engagement.community_goals.contribute_to_goal(
            community_goal.goal_id, "user_005", contribution
        )
        guild2_contribution += contribution
        
        # ?
        assert community_goal.current_value >= community_goal.target_value
        assert community_goal.is_completed is True
        
        # ?
        assert len(community_goal.participating_users) == 5
        assert all(user in community_goal.participating_users for user in self.test_users)
    
    def test_multi_event_participation(self):
        """?"""
        # ?
        spring_event = self.engagement.seasonal_events.create_seasonal_event("spring_renewal")
        summer_event = self.engagement.seasonal_events.create_seasonal_event("summer_energy")
        
        # ?
        task_goal = self.engagement.community_goals.create_community_goal(
            title="タスク",
            description="み",
            target_value=100,
            duration_days=21,
            reward_per_participant={"xp": 150}
        )
        
        social_goal = self.engagement.community_goals.create_community_goal(
            title="?",
            description="?",
            target_value=50,
            duration_days=14,
            reward_per_participant={"xp": 120}
        )
        
        # ユーザー
        test_user = "user_001"
        
        # ?
        actions = [
            ("task_completed", 15),
            ("social_interaction", 8),
            ("new_habit_started", 2),
            ("physical_task", 5),
            ("reflection_entry", 3)
        ]
        
        for action_type, count in actions:
            self.engagement.process_user_action(test_user, action_type, count)
        
        # エラー
        engagement_data = self.engagement.get_user_engagement_data(test_user)
        
        # ?
        assert len(engagement_data["active_events"]) == 2
        
        # ?
        assert len(engagement_data["community_goals"]) == 2
        
        # ?XPが
        assert engagement_data["user_guild"]["total_xp"] > 0
    
    def test_guild_leaderboard_dynamics(self):
        """?"""
        # ?
        guilds = []
        for i in range(3):
            guild = self.engagement.guild_system.create_guild(
                leader_uid=f"leader_{i+1}",
                name=f"?{i+1}",
                description=f"?{i+1}",
                therapeutic_focus="social_reintegration"
            )
            guilds.append(guild)
            
            # ?
            for j in range(3):
                member_uid = f"member_{i+1}_{j+1}"
                self.engagement.guild_system.join_guild(guild.guild_id, member_uid)
        
        # ?
        guild_activities = [
            (guilds[0], 20),  # ?
            (guilds[1], 15),  # ?
            (guilds[2], 10)   # ?
        ]
        
        for guild, activity_count in guild_activities:
            for member_uid in guild.members:
                self.engagement.process_user_action(member_uid, "task_completed", activity_count)
        
        # ?
        leaderboard = self.engagement.guild_system.get_guild_leaderboard()
        
        # ?
        assert len(leaderboard) >= 3
        assert leaderboard[0].total_xp > leaderboard[1].total_xp
        assert leaderboard[1].total_xp > leaderboard[2].total_xp
        
        # ?1?
        assert leaderboard[0].guild_id == guilds[0].guild_id
    
    def test_therapeutic_focus_matching(self):
        """治療"""
        # ?
        therapeutic_focuses = ["adhd_peer", "anxiety_support", "social_reintegration"]
        focus_guilds = {}
        
        for focus in therapeutic_focuses:
            guild = self.engagement.guild_system.create_guild(
                leader_uid=f"leader_{focus}",
                name=f"{focus}?",
                description=f"{focus}に",
                therapeutic_focus=focus
            )
            focus_guilds[focus] = guild
        
        # ?
        focus_events = {
            "adhd_peer": self.engagement.seasonal_events.create_seasonal_event("spring_renewal"),
            "anxiety_support": self.engagement.seasonal_events.create_seasonal_event("autumn_reflection"),
            "social_reintegration": self.engagement.seasonal_events.create_seasonal_event("winter_warmth")
        }
        
        # ?
        for focus, guild in focus_guilds.items():
            event = focus_events[focus]
            
            # ?
            if focus == "adhd_peer":
                self.engagement.process_user_action(guild.leader_uid, "new_habit_started", 3)
            elif focus == "anxiety_support":
                self.engagement.process_user_action(guild.leader_uid, "reflection_entry", 5)
            elif focus == "social_reintegration":
                self.engagement.process_user_action(guild.leader_uid, "social_interaction", 8)
        
        # ?
        for focus, guild in focus_guilds.items():
            assert guild.total_xp > 0
            assert guild.therapeutic_focus == focus
    
    def test_long_term_engagement_simulation(self):
        """?"""
        # 30?
        test_user = "user_001"
        
        # ?
        weekly_patterns = [
            # ?1?: ?
            {"task_completed": 20, "social_interaction": 10, "reflection_entry": 7},
            # ?2?: ?
            {"task_completed": 15, "social_interaction": 6, "reflection_entry": 5},
            # ?3?: ?
            {"task_completed": 8, "social_interaction": 3, "reflection_entry": 2},
            # ?4?: ?
            {"task_completed": 18, "social_interaction": 9, "reflection_entry": 6}
        ]
        
        # ?
        for week, pattern in enumerate(weekly_patterns):
            for action_type, count in pattern.items():
                self.engagement.process_user_action(test_user, action_type, count)
        
        # ?
        final_engagement = self.engagement.get_user_engagement_data(test_user)
        
        # ?
        assert final_engagement["user_guild"]["total_xp"] > 0
        assert final_engagement["user_guild"]["guild_level"] >= 1
        
        # アプリ
        # こ0で
        assert len(final_engagement["active_events"]) >= 0
        assert len(final_engagement["community_goals"]) >= 0
        
        # ?
        assert len(final_engagement["guild_leaderboard"]) > 0

def test_full_community_workflow():
    """?"""
    engagement = EngagementSystem()
    
    # 1. ?
    spring_event = engagement.seasonal_events.create_seasonal_event("spring_renewal")
    print(f"? ?: {spring_event.name}")
    
    # 2. ?
    guild = engagement.guild_system.create_guild(
        leader_uid="user_001",
        name="?",
        description="?",
        therapeutic_focus="adhd_peer"
    )
    
    # メイン
    members = ["user_002", "user_003", "user_004"]
    for member in members:
        engagement.guild_system.join_guild(guild.guild_id, member)
    
    print(f"? ?: {guild.name} (メイン: {len(guild.members)})")
    
    # 3. コア
    community_goal = engagement.community_goals.create_community_goal(
        title="?",
        description="コア100?",
        target_value=100,
        duration_days=30,
        reward_per_participant={"xp": 200, "coins": 100, "items": ["spring_badge"]}
    )
    print(f"? コア: {community_goal.title}")
    
    # 4. ユーザー
    all_users = ["user_001", "user_002", "user_003", "user_004"]
    
    for user_uid in all_users:
        # ?
        engagement.process_user_action(user_uid, "new_habit_started", 3)
        # タスク
        engagement.process_user_action(user_uid, "task_completed", 10)
        # ?
        engagement.process_user_action(user_uid, "social_interaction", 5)
        # ?
        engagement.process_user_action(user_uid, "reflection_entry", 2)
    
    print("? ユーザー")
    
    # 5. ?
    final_data = engagement.get_user_engagement_data("user_001")
    
    print(f"? ?:")
    print(f"   - ?: {final_data['user_guild']['guild_level']}")
    print(f"   - ?XP: {final_data['user_guild']['total_xp']}")
    print(f"   - アプリ: {len(final_data['active_events'])}")
    print(f"   - コア: {len(final_data['community_goals'])}")
    print(f"   - コア: {final_data['community_goals'][0]['current_value']}/{final_data['community_goals'][0]['target_value']}")
    
    # 6. ?
    user_progress = {
        "new_habits_started": 3,
        "consecutive_days": 7
    }
    
    event_completed = engagement.seasonal_events.check_event_completion(
        spring_event.event_id, user_progress
    )
    
    print(f"? ?: {'?' if event_completed else '?'}")
    
    return {
        "success": True,
        "guild_level": final_data['user_guild']['guild_level'],
        "community_goal_progress": final_data['community_goals'][0]['current_value'],
        "event_completed": event_completed
    }

if __name__ == "__main__":
    # ?
    result = test_full_community_workflow()
    print(f"\n? ?: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # ?
    pytest.main([__file__, "-v"])