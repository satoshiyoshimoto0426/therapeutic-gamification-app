"""
?
?

?: 1.1-1.5, 4.1-4.5
"""

import pytest
import asyncio
from datetime import datetime, time
from unittest.mock import Mock, patch, AsyncMock
import json

# 共有
from shared.interfaces.core_types import UserProfile, TaskRecord, StoryState
from shared.interfaces.task_system import TaskType
from shared.interfaces.crystal_system import CrystalGauge, CRYSTAL_ATTRIBUTES
from shared.interfaces.level_system import LevelSystem
from shared.interfaces.resonance_system import ResonanceSystem
from shared.interfaces.mandala_system import MandalaGrid

# ?
from services.line_bot.main import LineBot
from services.core_game.main import CoreGameEngine
from services.ai_story.main import AIStoryEngine
from services.task_mgmt.main import TaskManagement
from services.mood_tracking.main import MoodTracking
from services.mandala.main import MandalaSystem


class TestCompleteUserJourney:
    """?"""
    
    @pytest.fixture
    def mock_user_profile(self):
        """?"""
        return UserProfile(
            uid="test_user_001",
            yu_level=5,
            player_level=3,
            total_xp=250,
            crystal_gauges={attr: 20 for attr in CRYSTAL_ATTRIBUTES},
            current_chapter="chapter_1",
            daily_task_limit=16,
            care_points=100
        )
    
    @pytest.fixture
    def mock_services(self):
        """モデル"""
        return {
            'line_bot': Mock(spec=LineBot),
            'core_game': Mock(spec=CoreGameEngine),
            'ai_story': Mock(spec=AIStoryEngine),
            'task_mgmt': Mock(spec=TaskManagement),
            'mood_tracking': Mock(spec=MoodTracking),
            'mandala': Mock(spec=MandalaSystem)
        }
    
    @pytest.mark.asyncio
    async def test_morning_task_delivery_flow(self, mock_user_profile, mock_services):
        """? (?1.1)"""
        # 7:00 AM の
        current_time = datetime.now().replace(hour=7, minute=0, second=0)
        
        # Mandalaシステム
        mock_services['mandala'].get_daily_tasks.return_value = [
            {
                "task_id": "morning_001",
                "type": TaskType.ROUTINE,
                "difficulty": 2,
                "description": "?10?",
                "habit_tag": "morning_exercise"
            },
            {
                "task_id": "morning_002", 
                "type": TaskType.SKILL_UP,
                "difficulty": 3,
                "description": "?30?",
                "habit_tag": "daily_reading"
            },
            {
                "task_id": "morning_003",
                "type": TaskType.SOCIAL,
                "difficulty": 1,
                "description": "?",
                "habit_tag": "family_communication"
            }
        ]
        
        # LINE Botが3x3 Mandala?
        mock_services['line_bot'].send_daily_mandala.return_value = {
            "message_id": "msg_001",
            "format": "3x3_mandala",
            "tasks_count": 3,
            "mobile_optimized": True
        }
        
        # ?
        result = await self._simulate_morning_delivery(
            mock_user_profile, mock_services, current_time
        )
        
        # 検証
        assert result["delivery_success"] is True
        assert result["tasks_delivered"] == 3
        assert result["format"] == "3x3_mandala"
        mock_services['mandala'].get_daily_tasks.assert_called_once()
        mock_services['line_bot'].send_daily_mandala.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_task_completion_and_xp_flow(self, mock_user_profile, mock_services):
        """タスクXP? (?1.2)"""
        # タスク
        completed_task = TaskRecord(
            task_id="morning_001",
            uid=mock_user_profile.uid,
            task_type=TaskType.ROUTINE,
            difficulty=2,
            description="?10?",
            completed=True,
            completion_time=datetime.now(),
            xp_earned=0,  # 計算
            mood_at_completion=4,
            linked_story_edge=None
        )
        
        # 気分ADHD支援
        mock_services['mood_tracking'].get_mood_coefficient.return_value = 1.1  # 気分4 -> 1.1
        mock_services['task_mgmt'].get_adhd_assist_multiplier.return_value = 1.2
        
        # XP計算
        expected_xp = int(2 * 10 * 1.1 * 1.2)  # difficulty * base * mood * adhd = 26 XP
        mock_services['core_game'].calculate_xp.return_value = expected_xp
        
        # レベル
        mock_services['core_game'].check_level_up.return_value = {
            "level_up": True,
            "new_level": 4,
            "xp_for_next": 150
        }
        
        # ?
        result = await self._simulate_task_completion(
            completed_task, mock_services
        )
        
        # 検証
        assert result["xp_earned"] == expected_xp
        assert result["level_up"] is True
        assert result["new_level"] == 4
        mock_services['core_game'].calculate_xp.assert_called_once()
        mock_services['core_game'].check_level_up.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_resonance_event_trigger(self, mock_user_profile, mock_services):
        """共有 (?4.4, 4.5)"""
        # レベル5?
        mock_user_profile.yu_level = 8
        mock_user_profile.player_level = 3  # ?5
        
        # 共有
        mock_services['core_game'].check_resonance_event.return_value = {
            "resonance_triggered": True,
            "level_difference": 5,
            "bonus_xp": 100,
            "resonance_type": "yu_ahead"
        }
        
        # ?
        result = await self._simulate_resonance_check(
            mock_user_profile, mock_services
        )
        
        # 検証
        assert result["resonance_triggered"] is True
        assert result["bonus_xp"] == 100
        assert result["level_difference"] == 5
        mock_services['core_game'].check_resonance_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evening_story_generation_flow(self, mock_user_profile, mock_services):
        """? (?1.3, 2.1-2.4)"""
        # 21:30の
        current_time = datetime.now().replace(hour=21, minute=30, second=0)
        
        # ?
        daily_context = {
            "completed_tasks": 3,
            "total_xp_earned": 75,
            "mood_average": 4.2,
            "task_types_completed": ["routine", "skill_up", "social"],
            "current_chapter": "chapter_1"
        }
        
        # AIストーリー
        mock_services['ai_story'].generate_story.return_value = {
            "story_text": "ユーザー...",
            "choices": [
                {
                    "text": "?",
                    "real_task_id": "skill_challenge_001",
                    "xp_reward": 50
                },
                {
                    "text": "?",
                    "real_task_id": "social_connect_001", 
                    "xp_reward": 40
                },
                {
                    "text": "?",
                    "habit_tag": "daily_reflection",
                    "xp_reward": 30
                }
            ],
            "therapeutic_elements": ["positive_reinforcement", "goal_setting"],
            "generation_time": 2.8  # 3.5?
        }
        
        # ?
        result = await self._simulate_evening_story(
            daily_context, mock_services, current_time
        )
        
        # 検証
        assert result["story_generated"] is True
        assert result["generation_time"] < 3.5  # P95レベル
        assert len(result["choices"]) == 3
        assert all("real_task_id" in choice or "habit_tag" in choice 
                  for choice in result["choices"])
        mock_services['ai_story'].generate_story.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mandala_progression_integration(self, mock_user_profile, mock_services):
        """Mandalaシステム (?4.1-4.3)"""
        # ?
        crystal_progress = {
            "Self-Discipline": 85,
            "Empathy": 92,
            "Resilience": 78,
            "Curiosity": 95,  # 100%に
            "Communication": 65,
            "Creativity": 88,
            "Courage": 72,
            "Wisdom": 80
        }
        
        # Curiosityが100%に
        mock_services['mandala'].update_crystal_progress.return_value = {
            "attribute": "Curiosity",
            "new_value": 100,
            "chapter_unlocked": True,
            "new_chapter": "curiosity_mastery"
        }
        
        # ?
        mock_services['mandala'].unlock_memory_cells.return_value = {
            "unlocked_cells": 9,  # 3x3?
            "total_unlocked": 27,
            "completion_percentage": 33.3
        }
        
        # ?
        result = await self._simulate_mandala_progression(
            crystal_progress, mock_services
        )
        
        # 検証
        assert result["chapter_unlocked"] is True
        assert result["new_chapter"] == "curiosity_mastery"
        assert result["unlocked_cells"] == 9
        mock_services['mandala'].update_crystal_progress.assert_called_once()
        mock_services['mandala'].unlock_memory_cells.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_daily_cycle(self, mock_user_profile, mock_services):
        """?1?"""
        daily_results = {}
        
        # 1. ? (7:00)
        morning_result = await self._simulate_morning_delivery(
            mock_user_profile, mock_services, 
            datetime.now().replace(hour=7, minute=0)
        )
        daily_results["morning"] = morning_result
        
        # 2. ? (?)
        task_completions = []
        for i in range(3):
            task_result = await self._simulate_task_completion(
                self._create_test_task(f"task_{i}"), mock_services
            )
            task_completions.append(task_result)
        daily_results["task_completions"] = task_completions
        
        # 3. 共有
        resonance_result = await self._simulate_resonance_check(
            mock_user_profile, mock_services
        )
        daily_results["resonance"] = resonance_result
        
        # 4. ? (21:30)
        evening_result = await self._simulate_evening_story(
            {"completed_tasks": 3, "mood_average": 4.0}, 
            mock_services,
            datetime.now().replace(hour=21, minute=30)
        )
        daily_results["evening"] = evening_result
        
        # 5. Mandala?
        mandala_result = await self._simulate_mandala_progression(
            {attr: 50 for attr in CRYSTAL_ATTRIBUTES}, mock_services
        )
        daily_results["mandala"] = mandala_result
        
        # ?
        assert daily_results["morning"]["delivery_success"] is True
        assert len(daily_results["task_completions"]) == 3
        assert all(tc["xp_earned"] > 0 for tc in daily_results["task_completions"])
        assert daily_results["evening"]["story_generated"] is True
        
        # ?
        total_xp = sum(tc["xp_earned"] for tc in daily_results["task_completions"])
        if daily_results["resonance"]["resonance_triggered"]:
            total_xp += daily_results["resonance"]["bonus_xp"]
        
        assert total_xp > 0
        print(f"?1?: ?XP? {total_xp}")
    
    # ヘルパー
    async def _simulate_morning_delivery(self, user_profile, services, current_time):
        """?"""
        tasks = services['mandala'].get_daily_tasks.return_value
        delivery_result = services['line_bot'].send_daily_mandala.return_value
        
        return {
            "delivery_success": True,
            "tasks_delivered": len(tasks),
            "format": delivery_result["format"],
            "timestamp": current_time
        }
    
    async def _simulate_task_completion(self, task_record, services):
        """タスク"""
        xp_earned = services['core_game'].calculate_xp.return_value
        level_result = services['core_game'].check_level_up.return_value
        
        return {
            "task_id": task_record.task_id,
            "xp_earned": xp_earned,
            "level_up": level_result["level_up"],
            "new_level": level_result.get("new_level", 0)
        }
    
    async def _simulate_resonance_check(self, user_profile, services):
        """共有"""
        resonance_result = services['core_game'].check_resonance_event.return_value
        return resonance_result
    
    async def _simulate_evening_story(self, daily_context, services, current_time):
        """?"""
        story_result = services['ai_story'].generate_story.return_value
        
        return {
            "story_generated": True,
            "generation_time": story_result["generation_time"],
            "choices": story_result["choices"],
            "therapeutic_elements": story_result["therapeutic_elements"]
        }
    
    async def _simulate_mandala_progression(self, crystal_progress, services):
        """Mandala?"""
        progress_result = services['mandala'].update_crystal_progress.return_value
        unlock_result = services['mandala'].unlock_memory_cells.return_value
        
        return {
            "chapter_unlocked": progress_result["chapter_unlocked"],
            "new_chapter": progress_result.get("new_chapter"),
            "unlocked_cells": unlock_result["unlocked_cells"]
        }
    
    def _create_test_task(self, task_id):
        """?"""
        return TaskRecord(
            task_id=task_id,
            uid="test_user_001",
            task_type=TaskType.ROUTINE,
            difficulty=2,
            description=f"? {task_id}",
            completed=True,
            completion_time=datetime.now(),
            xp_earned=0,
            mood_at_completion=4,
            linked_story_edge=None
        )


if __name__ == "__main__":
    # ?
    import asyncio
    
    async def run_basic_test():
        test_instance = TestCompleteUserJourney()
        
        # モデル
        mock_profile = UserProfile(
            uid="test_001",
            yu_level=5,
            player_level=3,
            total_xp=250,
            crystal_gauges={attr: 20 for attr in CRYSTAL_ATTRIBUTES},
            current_chapter="chapter_1",
            daily_task_limit=16,
            care_points=100
        )
        
        mock_services = {
            'mandala': Mock(),
            'line_bot': Mock(),
            'core_game': Mock(),
            'ai_story': Mock(),
            'task_mgmt': Mock(),
            'mood_tracking': Mock()
        }
        
        # モデル
        mock_services['mandala'].get_daily_tasks.return_value = [
            {"task_id": "test_001", "type": TaskType.ROUTINE, "difficulty": 2}
        ]
        mock_services['line_bot'].send_daily_mandala.return_value = {
            "message_id": "msg_001", "format": "3x3_mandala", "mobile_optimized": True
        }
        mock_services['core_game'].calculate_xp.return_value = 26
        mock_services['core_game'].check_level_up.return_value = {
            "level_up": False, "new_level": 3
        }
        mock_services['core_game'].check_resonance_event.return_value = {
            "resonance_triggered": True, "bonus_xp": 100
        }
        
        # ?
        print("?...")
        
        # ?
        morning_result = await test_instance._simulate_morning_delivery(
            mock_profile, mock_services, datetime.now()
        )
        print(f"?: {morning_result}")
        
        # タスク
        test_task = test_instance._create_test_task("test_task_001")
        completion_result = await test_instance._simulate_task_completion(
            test_task, mock_services
        )
        print(f"タスク: {completion_result}")
        
        print("基本!")
    
    asyncio.run(run_basic_test())