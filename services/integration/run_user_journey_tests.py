"""
?

?15.1の
"""

import asyncio
import sys
import traceback
from datetime import datetime

# ?
from test_complete_user_journey import TestCompleteUserJourney
from test_xp_level_resonance_integration import TestXPLevelResonanceIntegration
from test_mandala_story_integration import TestMandalaStoryIntegration

# 共有
from shared.interfaces.core_types import UserProfile
from shared.interfaces.crystal_system import CRYSTAL_ATTRIBUTES
from shared.interfaces.level_system import LevelSystem
from shared.interfaces.resonance_system import ResonanceSystem
from shared.interfaces.mandala_system import MandalaGrid
from shared.interfaces.crystal_system import CrystalGauge


class UserJourneyTestRunner:
    """ユーザー"""
    
    def __init__(self):
        self.test_results = {
            "complete_journey": [],
            "xp_level_resonance": [],
            "mandala_story": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
    
    async def run_all_tests(self):
        """?"""
        print("=" * 60)
        print("?")
        print(f"実装: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. ?
        await self._run_complete_journey_tests()
        
        # 2. XP?
        await self._run_xp_level_resonance_tests()
        
        # 3. Mandala?
        await self._run_mandala_story_tests()
        
        # ?
        self._print_test_summary()
        
        return self.test_results
    
    async def _run_complete_journey_tests(self):
        """?"""
        print("\n1. ?")
        print("-" * 40)
        
        test_instance = TestCompleteUserJourney()
        
        # ?
        mock_profile = self._create_test_user_profile()
        mock_services = self._create_mock_services()
        
        tests = [
            ("?", test_instance.test_morning_task_delivery_flow),
            ("タスクXP?", test_instance.test_task_completion_and_xp_flow),
            ("共有", test_instance.test_resonance_event_trigger),
            ("?", test_instance.test_evening_story_generation_flow),
            ("Mandala?", test_instance.test_mandala_progression_integration),
            ("?1?", test_instance.test_complete_daily_cycle)
        ]
        
        for test_name, test_method in tests:
            try:
                print(f"  実装: {test_name}")
                
                # ?
                if "mock_user_profile" in test_method.__code__.co_varnames:
                    await test_method(mock_profile, mock_services)
                else:
                    await test_method(mock_profile, mock_services)
                
                print(f"  ? {test_name} - 成")
                self.test_results["complete_journey"].append({
                    "test": test_name,
                    "status": "PASSED",
                    "error": None
                })
                self.test_results["summary"]["passed"] += 1
                
            except Exception as e:
                print(f"  ? {test_name} - ?: {str(e)}")
                self.test_results["complete_journey"].append({
                    "test": test_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                self.test_results["summary"]["failed"] += 1
                self.test_results["summary"]["errors"].append(f"{test_name}: {str(e)}")
            
            self.test_results["summary"]["total_tests"] += 1
    
    async def _run_xp_level_resonance_tests(self):
        """XP?"""
        print("\n2. XP?")
        print("-" * 40)
        
        test_instance = TestXPLevelResonanceIntegration()
        level_system = LevelSystem()
        resonance_system = ResonanceSystem()
        
        tests = [
            ("XP計算", test_instance.test_xp_calculation_accuracy),
            ("レベル", lambda: test_instance.test_level_progression_algorithm(level_system)),
            ("?XP計算", lambda: test_instance.test_next_level_xp_calculation(level_system)),
            ("共有", lambda: test_instance.test_resonance_event_trigger_conditions(resonance_system)),
            ("共有XP計算", lambda: test_instance.test_resonance_bonus_xp_calculation(resonance_system)),
            ("エラー", lambda: test_instance.test_edge_case_level_calculations(level_system)),
            ("共有", lambda: test_instance.test_resonance_event_types(resonance_system))
        ]
        
        for test_name, test_method in tests:
            try:
                print(f"  実装: {test_name}")
                
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
                print(f"  ? {test_name} - 成")
                self.test_results["xp_level_resonance"].append({
                    "test": test_name,
                    "status": "PASSED",
                    "error": None
                })
                self.test_results["summary"]["passed"] += 1
                
            except Exception as e:
                print(f"  ? {test_name} - ?: {str(e)}")
                self.test_results["xp_level_resonance"].append({
                    "test": test_name,
                    "status": "FAILED", 
                    "error": str(e)
                })
                self.test_results["summary"]["failed"] += 1
                self.test_results["summary"]["errors"].append(f"{test_name}: {str(e)}")
            
            self.test_results["summary"]["total_tests"] += 1
    
    async def _run_mandala_story_tests(self):
        """Mandala?"""
        print("\n3. Mandala?")
        print("-" * 40)
        
        test_instance = TestMandalaStoryIntegration()
        mandala_grid = MandalaGrid()
        crystal_gauge = CrystalGauge()
        
        tests = [
            ("Mandala?", lambda: test_instance.test_mandala_grid_initialization(mandala_grid)),
            ("メイン", lambda: test_instance.test_memory_cell_unlock_conditions(mandala_grid, crystal_gauge)),
            ("Mandala API?", lambda: test_instance.test_mandala_api_response_format(mandala_grid, self._create_test_user_profile())),
            ("?", lambda: test_instance.test_crystal_attribute_chapter_mapping(crystal_gauge)),
            ("Mandalaモデル", lambda: test_instance.test_mandala_mobile_optimization(mandala_grid)),
            ("?", test_instance.test_isolated_node_detection_and_merge)
        ]
        
        for test_name, test_method in tests:
            try:
                print(f"  実装: {test_name}")
                
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
                print(f"  ? {test_name} - 成")
                self.test_results["mandala_story"].append({
                    "test": test_name,
                    "status": "PASSED",
                    "error": None
                })
                self.test_results["summary"]["passed"] += 1
                
            except Exception as e:
                print(f"  ? {test_name} - ?: {str(e)}")
                self.test_results["mandala_story"].append({
                    "test": test_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                self.test_results["summary"]["failed"] += 1
                self.test_results["summary"]["errors"].append(f"{test_name}: {str(e)}")
            
            self.test_results["summary"]["total_tests"] += 1
    
    def _create_test_user_profile(self):
        """?"""
        return UserProfile(
            uid="integration_test_user_001",
            yu_level=6,
            player_level=4,
            total_xp=600,
            crystal_gauges={attr: 40 for attr in CRYSTAL_ATTRIBUTES},
            current_chapter="chapter_2",
            daily_task_limit=16,
            care_points=200
        )
    
    def _create_mock_services(self):
        """モデル"""
        from unittest.mock import Mock
        
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
            {"task_id": "morning_001", "type": "routine", "difficulty": 2},
            {"task_id": "morning_002", "type": "skill_up", "difficulty": 3},
            {"task_id": "morning_003", "type": "social", "difficulty": 1}
        ]
        
        mock_services['line_bot'].send_daily_mandala.return_value = {
            "message_id": "msg_001",
            "format": "3x3_mandala",
            "tasks_count": 3,
            "mobile_optimized": True
        }
        
        mock_services['core_game'].calculate_xp.return_value = 35
        mock_services['core_game'].check_level_up.return_value = {
            "level_up": True,
            "new_level": 5,
            "xp_for_next": 200
        }
        mock_services['core_game'].check_resonance_event.return_value = {
            "resonance_triggered": True,
            "level_difference": 6,
            "bonus_xp": 120,
            "resonance_type": "yu_ahead"
        }
        
        mock_services['ai_story'].generate_story.return_value = {
            "story_text": "ユーザー...",
            "choices": [
                {"text": "?", "real_task_id": "challenge_001", "xp_reward": 50},
                {"text": "?", "habit_tag": "teamwork", "xp_reward": 40},
                {"text": "創", "habit_tag": "creativity", "xp_reward": 45}
            ],
            "therapeutic_elements": ["positive_reinforcement", "goal_setting"],
            "generation_time": 2.1
        }
        
        mock_services['mood_tracking'].get_mood_coefficient.return_value = 1.15
        mock_services['task_mgmt'].get_adhd_assist_multiplier.return_value = 1.25
        
        mock_services['mandala'].update_crystal_progress.return_value = {
            "attribute": "Curiosity",
            "new_value": 100,
            "chapter_unlocked": True,
            "new_chapter": "curiosity_mastery"
        }
        
        mock_services['mandala'].unlock_memory_cells.return_value = {
            "unlocked_cells": 9,
            "total_unlocked": 36,
            "completion_percentage": 44.4
        }
        
        return mock_services
    
    def _print_test_summary(self):
        """?"""
        print("\n" + "=" * 60)
        print("?")
        print("=" * 60)
        
        summary = self.test_results["summary"]
        print(f"?: {summary['total_tests']}")
        print(f"成: {summary['passed']}")
        print(f"?: {summary['failed']}")
        print(f"成: {(summary['passed'] / summary['total_tests'] * 100):.1f}%")
        
        if summary['errors']:
            print("\n?:")
            for error in summary['errors']:
                print(f"  - {error}")
        
        print("\n?:")
        
        # ?
        print("\n1. ?:")
        for result in self.test_results["complete_journey"]:
            status_icon = "?" if result["status"] == "PASSED" else "?"
            print(f"  {status_icon} {result['test']}")
        
        # XP?
        print("\n2. XP?:")
        for result in self.test_results["xp_level_resonance"]:
            status_icon = "?" if result["status"] == "PASSED" else "?"
            print(f"  {status_icon} {result['test']}")
        
        # Mandala?
        print("\n3. Mandala?:")
        for result in self.test_results["mandala_story"]:
            status_icon = "?" if result["status"] == "PASSED" else "?"
            print(f"  {status_icon} {result['test']}")
        
        print("\n" + "=" * 60)
        
        # ?
        print("?:")
        covered_requirements = [
            "1.1 - ? (7:00 AM)",
            "1.2 - ?",
            "1.3 - ? (21:30)",
            "1.4 - ストーリーMandala?",
            "1.5 - ?100%で",
            "4.1 - Mandala 9x9?",
            "4.2 - 8?",
            "4.3 - 81メイン",
            "4.4 - ユーザー",
            "4.5 - レベル5?"
        ]
        
        for req in covered_requirements:
            print(f"  ? {req}")
        
        print("=" * 60)


async def main():
    """メイン"""
    try:
        runner = UserJourneyTestRunner()
        results = await runner.run_all_tests()
        
        # ?
        if results["summary"]["failed"] == 0:
            print("\n? ?!")
            sys.exit(0)
        else:
            print(f"\n?  {results['summary']['failed']}?")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n? ?: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # ?
    asyncio.run(main())