"""
RPG? - タスク20.1

XP?
?

?: 11.1-11.5, 12.1-12.5, 13.1-13.5
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# プレビュー
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# RPGシステム
from rpg_economy.main import CoinEconomy, ActionType, DemonRarity
from job_system.main import JobManager, JobType
from inner_demon_battle.main import InnerDemonBattle, DemonType
from core_game.main import get_or_create_game_system, get_or_create_resonance_manager
from task_mgmt.main import get_user_tasks, generate_task_id

# 共有
from shared.interfaces.core_types import TaskType, TaskStatus
from shared.interfaces.task_system import Task, TaskDifficulty, TaskPriority, ADHDSupportLevel
from shared.interfaces.level_system import LevelSystemManager


class RPGIntegrationTestSuite:
    """RPG?"""
    
    def __init__(self):
        self.test_uid = "rpg_integration_test_user"
        self.coin_economy = CoinEconomy()
        self.job_manager = JobManager()
        self.battle_system = InnerDemonBattle()
        self.game_system = None
        self.resonance_manager = None
        
    def setup_test_environment(self):
        """?"""
        # ゲーム
        self.game_system = get_or_create_game_system(self.test_uid)
        self.resonance_manager = get_or_create_resonance_manager(self.test_uid)
        
        # ?
        self.job_manager.initialize_user_job(self.test_uid, JobType.WARRIOR)
        
        print(f"? ? - ユーザー: {self.test_uid}")
    
    def test_xp_coin_integration(self) -> Dict[str, Any]:
        """XPと"""
        print("\n? XP?...")
        
        results = {
            "test_name": "XP?",
            "passed": True,
            "details": []
        }
        
        try:
            # 1. タスクXPと
            task_completion_xp = 150
            task_difficulty = 3
            mood_coefficient = 1.1
            adhd_assist = 1.2
            
            # XP?
            xp_result = self.game_system.add_player_xp(task_completion_xp, "task_completion")
            
            # コア
            coin_reward = self.coin_economy.calculate_task_completion_coins(
                task_type=TaskType.ROUTINE,
                difficulty=task_difficulty,
                mood_coefficient=mood_coefficient,
                adhd_assist=adhd_assist,
                user_total_coins=0
            )
            
            results["details"].append({
                "step": "タスク",
                "xp_earned": task_completion_xp,
                "coins_earned": coin_reward.final_amount,
                "player_level": xp_result["player"]["new_level"],
                "level_up": xp_result["player"]["level_up"]
            })
            
            # 2. ?XP
            demon_defeat_coins = self.coin_economy.calculate_demon_defeat_coins(
                demon_rarity=DemonRarity.RARE,
                battle_performance=1.5,
                user_total_coins=coin_reward.final_amount
            )
            
            # ?XP?
            demon_defeat_xp = 75
            xp_result_2 = self.game_system.add_player_xp(demon_defeat_xp, "demon_defeat")
            
            results["details"].append({
                "step": "?",
                "xp_earned": demon_defeat_xp,
                "coins_earned": demon_defeat_coins.final_amount,
                "player_level": xp_result_2["player"]["new_level"],
                "total_coins": coin_reward.final_amount + demon_defeat_coins.final_amount
            })
            
            # 3. ?
            total_coins = coin_reward.final_amount + demon_defeat_coins.final_amount
            economic_status = self.coin_economy.get_economic_status(total_coins)
            
            results["details"].append({
                "step": "?",
                "total_coins": total_coins,
                "economic_tier": economic_status["economic_tier"],
                "inflation_adjustment": economic_status["inflation_adjustment"]
            })
            
            print(f"? XP?")
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
            print(f"? XP?: {e}")
        
        return results
    
    def test_job_equipment_integration(self) -> Dict[str, Any]:
        """?"""
        print("\n? ?...")
        
        results = {
            "test_name": "?",
            "passed": True,
            "details": []
        }
        
        try:
            # 1. ?
            job_info = self.job_manager.get_user_job_info(self.test_uid)
            initial_level = job_info["current_job"]["level"]
            
            # ?
            leveled_up = self.job_manager.add_job_experience(self.test_uid, 150)
            
            updated_job_info = self.job_manager.get_user_job_info(self.test_uid)
            
            results["details"].append({
                "step": "?",
                "initial_level": initial_level,
                "new_level": updated_job_info["current_job"]["level"],
                "leveled_up": leveled_up,
                "stat_bonuses": updated_job_info["stat_bonuses"],
                "available_skills": len(updated_job_info["available_skills"])
            })
            
            # 2. ?RPG?
            # ?
            from services.rpg_economy.gacha_system import GachaSystem
            gacha_system = GachaSystem()
            
            # ?
            gacha_result = gacha_system.perform_gacha("single", 1000)
            
            if gacha_result["success"]:
                items = gacha_result["items"]
                results["details"].append({
                    "step": "?",
                    "items_obtained": len(items),
                    "item_rarities": [item["rarity"] for item in items],
                    "coins_spent": gacha_result["coins_spent"]
                })
            
            # 3. ?
            current_job = JobType(updated_job_info["current_job"]["type"])
            task_efficiency_bonus = self.job_manager.job_system.calculate_task_efficiency_bonus(
                current_job, updated_job_info["current_job"]["level"], "routine"
            )
            
            results["details"].append({
                "step": "タスク",
                "job_type": current_job.value,
                "job_level": updated_job_info["current_job"]["level"],
                "efficiency_bonus": task_efficiency_bonus
            })
            
            print(f"? ?")
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
            print(f"? ?: {e}")
        
        return results
    
    def test_demon_battle_task_integration(self) -> Dict[str, Any]:
        """?"""
        print("\n? ?...")
        
        results = {
            "test_name": "?",
            "passed": True,
            "details": []
        }
        
        try:
            # 1. タスク
            user_tasks = get_user_tasks(self.test_uid)
            task_id = generate_task_id(self.test_uid)
            
            # ?
            routine_task = Task(
                task_id=task_id,
                uid=self.test_uid,
                task_type=TaskType.ROUTINE,
                title="?",
                description="30?",
                difficulty=TaskDifficulty.MEDIUM,
                priority=TaskPriority.HIGH,
                estimated_duration=30,
                adhd_support_level=ADHDSupportLevel.BASIC
            )
            
            user_tasks[task_id] = routine_task
            
            # 2. タスク
            routine_task.start_task()
            xp_earned = routine_task.complete_task(
                mood_score=4,
                actual_duration=25,
                notes="気分",
                adhd_assist_multiplier=1.1
            )
            
            # ?
            user_actions = [
                "routine_task_completion",
                "morning_routine",
                "physical_activity"
            ]
            
            results["details"].append({
                "step": "タスク",
                "task_id": task_id,
                "xp_earned": xp_earned,
                "task_status": routine_task.status.value,
                "user_actions": user_actions
            })
            
            # 3. ?
            battle_result = self.battle_system.initiate_battle(
                self.test_uid,
                DemonType.PROCRASTINATION_DRAGON,
                user_actions
            )
            
            results["details"].append({
                "step": "?",
                "demon_type": DemonType.PROCRASTINATION_DRAGON.value,
                "battle_result": battle_result["result"],
                "damage_dealt": battle_result.get("total_damage", 0)
            })
            
            # 4. バリデーション
            if battle_result["result"] == "victory":
                # ?
                battle_rewards = battle_result["rewards"]
                
                # コア
                demon_coins = self.coin_economy.calculate_demon_defeat_coins(
                    demon_rarity=DemonRarity.COMMON,
                    battle_performance=1.2,
                    user_total_coins=500
                )
                
                # XPシステム
                battle_xp_result = self.game_system.add_player_xp(
                    battle_rewards["xp"], "demon_battle_victory"
                )
                
                results["details"].append({
                    "step": "バリデーション",
                    "battle_coins": battle_rewards["coins"],
                    "system_coins": demon_coins.final_amount,
                    "battle_xp": battle_rewards["xp"],
                    "level_up": battle_xp_result["player"]["level_up"],
                    "items_obtained": len(battle_rewards["items"]),
                    "therapeutic_message": battle_result["therapeutic_message"]
                })
            
            # 5. ?
            elif battle_result["result"] == "ongoing":
                # ?
                additional_actions = ["pomodoro_usage", "small_step_action"]
                continue_result = self.battle_system.continue_battle(
                    self.test_uid, additional_actions
                )
                
                results["details"].append({
                    "step": "バリデーション",
                    "additional_actions": additional_actions,
                    "continue_result": continue_result["result"],
                    "demon_hp": continue_result.get("demon_hp", 0)
                })
            
            print(f"? ?")
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
            print(f"? ?: {e}")
        
        return results
    
    def test_economic_balance_adjustment(self) -> Dict[str, Any]:
        """?"""
        print("\n? ?...")
        
        results = {
            "test_name": "?",
            "passed": True,
            "details": []
        }
        
        try:
            # 1. ?
            coin_accumulation_test = []
            total_coins = 0
            
            # ?
            test_amounts = [500, 2000, 6000, 12000]
            
            for amount in test_amounts:
                total_coins += amount
                
                # タスク
                task_reward = self.coin_economy.calculate_task_completion_coins(
                    task_type=TaskType.SKILL_UP,
                    difficulty=4,
                    mood_coefficient=1.0,
                    adhd_assist=1.0,
                    user_total_coins=total_coins
                )
                
                # ?
                demon_reward = self.coin_economy.calculate_demon_defeat_coins(
                    demon_rarity=DemonRarity.EPIC,
                    battle_performance=1.0,
                    user_total_coins=total_coins
                )
                
                economic_status = self.coin_economy.get_economic_status(total_coins)
                
                coin_accumulation_test.append({
                    "total_coins": total_coins,
                    "economic_tier": economic_status["economic_tier"],
                    "inflation_adjustment": economic_status["inflation_adjustment"],
                    "task_reward": task_reward.final_amount,
                    "demon_reward": demon_reward.final_amount,
                    "reduction_percent": economic_status["inflation_reduction_percent"]
                })
            
            results["details"].append({
                "step": "?",
                "coin_progression": coin_accumulation_test
            })
            
            # 2. レベル
            level_progression_test = []
            
            # ?XPで
            xp_amounts = [100, 500, 1000, 2000, 5000]
            
            for xp_amount in xp_amounts:
                xp_result = self.game_system.add_player_xp(xp_amount, "balance_test")
                system_status = self.game_system.get_system_status()
                
                level_progression_test.append({
                    "xp_added": xp_amount,
                    "player_level": system_status["player"]["level"],
                    "yu_level": system_status["yu"]["level"],
                    "level_difference": system_status["level_difference"],
                    "level_up_occurred": xp_result["player"]["level_up"]
                })
            
            results["details"].append({
                "step": "レベル",
                "level_progression": level_progression_test
            })
            
            # 3. ?
            # ?
            user_stats = {
                "warrior": 15,
                "priest": 8,
                "social_tasks": 60,
                "wisdom": 25,
                "creative_tasks": 120,
                "ninja": 15,
                "resilience": 30,
                "stress_overcome": 35
            }
            
            advanced_job_tests = []
            for job_type in [JobType.PALADIN, JobType.ARCHMAGE, JobType.SHADOW_MASTER]:
                can_unlock = self.job_manager.job_system.check_job_unlock(user_stats, job_type)
                job_info = self.job_manager.job_system.get_job(job_type)
                
                advanced_job_tests.append({
                    "job_type": job_type.value,
                    "can_unlock": can_unlock,
                    "requirements": job_info.unlock_requirements if job_info else {},
                    "stat_bonuses": job_info.stat_bonuses if job_info else {}
                })
            
            results["details"].append({
                "step": "?",
                "user_stats": user_stats,
                "advanced_jobs": advanced_job_tests
            })
            
            print(f"? ?")
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
            print(f"? ?: {e}")
        
        return results
    
    def test_complete_rpg_flow(self) -> Dict[str, Any]:
        """?RPG?"""
        print("\n? ?RPG?...")
        
        results = {
            "test_name": "?RPG?",
            "passed": True,
            "details": []
        }
        
        try:
            # 1. ?RPG?
            journey_uid = "rpg_journey_test_user"
            
            # ゲーム
            journey_game_system = get_or_create_game_system(journey_uid)
            journey_job_manager = JobManager()
            journey_job_manager.initialize_user_job(journey_uid, JobType.MAGE)
            
            # 2. ?
            growth_stages = []
            
            for day in range(1, 8):  # 7?
                daily_results = {
                    "day": day,
                    "tasks_completed": 0,
                    "xp_earned": 0,
                    "coins_earned": 0,
                    "battles_won": 0,
                    "level_ups": 0
                }
                
                # ?3-5タスク
                daily_tasks = min(5, day + 2)  # ?
                
                for task_num in range(daily_tasks):
                    # タスクXP
                    task_xp = 50 + (day * 10)  # ?
                    xp_result = journey_game_system.add_player_xp(task_xp, f"day_{day}_task_{task_num}")
                    
                    # コア
                    coin_reward = self.coin_economy.calculate_task_completion_coins(
                        task_type=TaskType.SKILL_UP,
                        difficulty=min(5, day // 2 + 1),
                        mood_coefficient=1.0 + (day * 0.02),
                        adhd_assist=1.0 + (day * 0.01),
                        user_total_coins=daily_results["coins_earned"]
                    )
                    
                    daily_results["tasks_completed"] += 1
                    daily_results["xp_earned"] += task_xp
                    daily_results["coins_earned"] += coin_reward.final_amount
                    
                    if xp_result["player"]["level_up"]:
                        daily_results["level_ups"] += 1
                
                # ?2?1?
                if day % 2 == 0:
                    battle_actions = ["skill_up_task", "creative_expression", "problem_solving"]
                    battle_result = self.battle_system.initiate_battle(
                        journey_uid, DemonType.ANXIETY_SHADOW, battle_actions
                    )
                    
                    if battle_result["result"] == "victory":
                        daily_results["battles_won"] += 1
                        
                        # バリデーションXP
                        battle_xp = battle_result["rewards"]["xp"]
                        journey_game_system.add_player_xp(battle_xp, f"day_{day}_battle")
                        daily_results["xp_earned"] += battle_xp
                
                # ?
                job_exp = daily_results["xp_earned"] // 3  # XPの1/3を
                journey_job_manager.add_job_experience(journey_uid, job_exp)
                
                growth_stages.append(daily_results)
            
            # 3. ?
            final_system_status = journey_game_system.get_system_status()
            final_job_info = journey_job_manager.get_user_job_info(journey_uid)
            
            results["details"].append({
                "step": "7?",
                "growth_stages": growth_stages,
                "final_player_level": final_system_status["player"]["level"],
                "final_yu_level": final_system_status["yu"]["level"],
                "final_job_level": final_job_info["current_job"]["level"],
                "total_xp": sum(stage["xp_earned"] for stage in growth_stages),
                "total_coins": sum(stage["coins_earned"] for stage in growth_stages),
                "total_battles_won": sum(stage["battles_won"] for stage in growth_stages)
            })
            
            print(f"? ?RPG?")
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
            print(f"? ?RPG?: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """?"""
        print("? RPG?")
        print("=" * 60)
        
        self.setup_test_environment()
        
        test_results = {
            "test_suite": "RPG?",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
        # ?
        tests = [
            self.test_xp_coin_integration,
            self.test_job_equipment_integration,
            self.test_demon_battle_task_integration,
            self.test_economic_balance_adjustment,
            self.test_complete_rpg_flow
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                test_results["tests"].append(result)
                
                if result["passed"]:
                    test_results["summary"]["passed_tests"] += 1
                else:
                    test_results["summary"]["failed_tests"] += 1
                    
            except Exception as e:
                test_results["tests"].append({
                    "test_name": test_func.__name__,
                    "passed": False,
                    "error": f"?: {str(e)}"
                })
                test_results["summary"]["failed_tests"] += 1
        
        # ?
        test_results["summary"]["total_tests"] = len(tests)
        if test_results["summary"]["total_tests"] > 0:
            test_results["summary"]["success_rate"] = (
                test_results["summary"]["passed_tests"] / test_results["summary"]["total_tests"]
            ) * 100
        
        # ?
        print("\n" + "=" * 60)
        print("? RPG?")
        print("=" * 60)
        print(f"?: {test_results['summary']['total_tests']}")
        print(f"成: {test_results['summary']['passed_tests']}")
        print(f"?: {test_results['summary']['failed_tests']}")
        print(f"成: {test_results['summary']['success_rate']:.1f}%")
        
        if test_results["summary"]["success_rate"] == 100.0:
            print("? ?RPG?")
        else:
            print("?  一般")
        
        return test_results


def main():
    """メイン"""
    test_suite = RPGIntegrationTestSuite()
    results = test_suite.run_all_tests()
    
    # ?JSON?
    output_file = "rpg_integration_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n? ? {output_file} に")
    
    # ?1
    if results["summary"]["failed_tests"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()