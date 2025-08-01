"""
内部 - メイン
治療
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random
import json
from datetime import datetime, timedelta
from battle_rewards import BattleRewardSystem, BattleRewards

class DemonType(Enum):
    """?"""
    PROCRASTINATION_DRAGON = "procrastination_dragon"
    ANXIETY_SHADOW = "anxiety_shadow"
    DEPRESSION_VOID = "depression_void"
    SOCIAL_FEAR_GOBLIN = "social_fear_goblin"

class BattleResult(Enum):
    """バリデーション"""
    VICTORY = "victory"
    DEFEAT = "defeat"
    ONGOING = "ongoing"

@dataclass
class DemonStats:
    """?"""
    name: str
    max_hp: int
    current_hp: int
    weaknesses: List[str]
    therapeutic_theme: str
    description: str

@dataclass
class BattleReward:
    """バリデーション"""
    coins: int
    items: List[str]
    xp: int
    therapeutic_message: str

class InnerDemonBattle:
    """内部"""
    
    def __init__(self):
        self.demon_types = self._initialize_demon_types()
        self.active_battles = {}  # user_id -> battle_state
        self.reward_system = BattleRewardSystem()
    
    def _initialize_demon_types(self) -> Dict[DemonType, Dict[str, Any]]:
        """?"""
        return {
            DemonType.PROCRASTINATION_DRAGON: {
                "name": "?",
                "max_hp": 100,
                "weaknesses": [
                    "routine_task_completion",
                    "pomodoro_usage",
                    "small_step_action",
                    "deadline_adherence",
                    "morning_routine"
                ],
                "therapeutic_theme": "?",
                "description": "?",
                "rewards": {
                    "coins": 150,
                    "items": ["focus_potion", "time_crystal", "motivation_gem"],
                    "xp": 75,
                    "therapeutic_message": "?"
                }
            },
            DemonType.ANXIETY_SHADOW: {
                "name": "?",
                "max_hp": 80,
                "weaknesses": [
                    "breathing_exercise",
                    "positive_affirmation",
                    "mindfulness_practice",
                    "social_connection",
                    "grounding_technique"
                ],
                "therapeutic_theme": "?",
                "description": "?",
                "rewards": {
                    "coins": 120,
                    "items": ["calm_amulet", "courage_ring", "peace_stone"],
                    "xp": 60,
                    "therapeutic_message": "?"
                }
            },
            DemonType.DEPRESSION_VOID: {
                "name": "?",
                "max_hp": 150,
                "weaknesses": [
                    "social_connection",
                    "creative_expression",
                    "physical_activity",
                    "gratitude_practice",
                    "meaningful_activity"
                ],
                "therapeutic_theme": "無",
                "description": "?",
                "rewards": {
                    "coins": 200,
                    "items": ["hope_crystal", "energy_elixir", "connection_charm"],
                    "xp": 100,
                    "therapeutic_message": "つ"
                }
            },
            DemonType.SOCIAL_FEAR_GOBLIN: {
                "name": "?",
                "max_hp": 60,
                "weaknesses": [
                    "small_social_task",
                    "communication_practice",
                    "eye_contact_practice",
                    "group_participation",
                    "assertiveness_training"
                ],
                "therapeutic_theme": "?",
                "description": "?",
                "rewards": {
                    "coins": 100,
                    "items": ["confidence_badge", "social_key", "communication_scroll"],
                    "xp": 50,
                    "therapeutic_message": "?"
                }
            }
        }
    
    def initiate_battle(self, user_id: str, demon_type: DemonType, 
                       user_recent_actions: List[str]) -> Dict[str, Any]:
        """バリデーション"""
        demon_data = self.demon_types[demon_type].copy()
        
        # ?
        demon_stats = DemonStats(
            name=demon_data["name"],
            max_hp=demon_data["max_hp"],
            current_hp=demon_data["max_hp"],
            weaknesses=demon_data["weaknesses"],
            therapeutic_theme=demon_data["therapeutic_theme"],
            description=demon_data["description"]
        )
        
        # ?
        initial_damage = self._calculate_damage(user_recent_actions, demon_stats.weaknesses)
        demon_stats.current_hp = max(0, demon_stats.current_hp - initial_damage)
        
        # バリデーション
        battle_state = {
            "demon_stats": demon_stats,
            "demon_type": demon_type,
            "start_time": datetime.now(),
            "turn_count": 1,
            "damage_dealt": initial_damage,
            "user_actions": user_recent_actions.copy()
        }
        
        self.active_battles[user_id] = battle_state
        
        # バリデーション
        if demon_stats.current_hp <= 0:
            return self._handle_victory(user_id, demon_data)
        else:
            return self._handle_ongoing_battle(user_id, demon_stats, initial_damage)
    
    def continue_battle(self, user_id: str, new_actions: List[str]) -> Dict[str, Any]:
        """バリデーション"""
        if user_id not in self.active_battles:
            return {"error": "アプリ"}
        
        battle_state = self.active_battles[user_id]
        demon_stats = battle_state["demon_stats"]
        demon_data = self.demon_types[battle_state["demon_type"]]
        
        # ?
        damage = self._calculate_damage(new_actions, demon_stats.weaknesses)
        demon_stats.current_hp = max(0, demon_stats.current_hp - damage)
        
        # バリデーション
        battle_state["turn_count"] += 1
        battle_state["damage_dealt"] += damage
        battle_state["user_actions"].extend(new_actions)
        
        # バリデーション
        if demon_stats.current_hp <= 0:
            return self._handle_victory(user_id, demon_data)
        elif battle_state["turn_count"] > 10:  # ?10タスク
            return self._handle_defeat(user_id, demon_data)
        else:
            return self._handle_ongoing_battle(user_id, demon_stats, damage)
    
    def _calculate_damage(self, actions: List[str], weaknesses: List[str]) -> int:
        """アプリ"""
        damage = 0
        for action in actions:
            if action in weaknesses:
                # ?
                damage += 25
            elif any(action in weakness or weakness in action for weakness in weaknesses):
                # ?
                damage += 15
            else:
                # ?
                damage += 5
        
        # ?20%?
        variance = random.uniform(0.8, 1.2)
        return int(damage * variance)
    
    def _handle_victory(self, user_id: str, demon_data: Dict[str, Any]) -> Dict[str, Any]:
        """?"""
        battle_state = self.active_battles.pop(user_id)
        
        # バリデーション
        battle_performance = {
            "turns_taken": battle_state["turn_count"],
            "damage_efficiency": battle_state["damage_dealt"] / demon_data["max_hp"],
            "weakness_hits": self._count_weakness_hits(battle_state["user_actions"], demon_data["weaknesses"])
        }
        
        # ?
        battle_rewards = self.reward_system.calculate_victory_rewards(
            battle_state["demon_type"].value, 
            battle_performance
        )
        
        return {
            "result": BattleResult.VICTORY.value,
            "demon_name": demon_data["name"],
            "turns_taken": battle_state["turn_count"],
            "total_damage": battle_state["damage_dealt"],
            "battle_performance": battle_performance,
            "rewards": {
                "coins": battle_rewards.coins,
                "xp": battle_rewards.xp,
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "description": item.description,
                        "rarity": item.rarity.value,
                        "therapeutic_effect": item.therapeutic_effect,
                        "stat_bonus": item.stat_bonus
                    } for item in battle_rewards.items
                ]
            },
            "therapeutic_message": battle_rewards.therapeutic_message,
            "cbt_reflection_prompt": battle_rewards.cbt_reflection_prompt,
            "next_actions": self._suggest_reinforcement_actions(demon_data["weaknesses"])
        }
    
    def _handle_defeat(self, user_id: str, demon_data: Dict[str, Any]) -> Dict[str, Any]:
        """?"""
        battle_state = self.active_battles.pop(user_id)
        
        # バリデーション
        battle_performance = {
            "turns_taken": battle_state["turn_count"],
            "damage_efficiency": battle_state["damage_dealt"] / demon_data["max_hp"],
            "weakness_hits": self._count_weakness_hits(battle_state["user_actions"], demon_data["weaknesses"])
        }
        
        # ?
        defeat_rewards = self.reward_system.calculate_defeat_rewards(
            battle_state["demon_type"].value,
            battle_performance
        )
        
        return {
            "result": BattleResult.DEFEAT.value,
            "demon_name": demon_data["name"],
            "turns_taken": battle_state["turn_count"],
            "battle_performance": battle_performance,
            "support_message": defeat_rewards.therapeutic_message,
            "cbt_reflection_prompt": defeat_rewards.cbt_reflection_prompt,
            "alternative_strategies": self._suggest_alternative_strategies(demon_data["weaknesses"]),
            "retry_suggestion": "こ",
            "consolation_reward": {
                "coins": defeat_rewards.coins,
                "xp": defeat_rewards.xp,
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "description": item.description,
                        "rarity": item.rarity.value,
                        "therapeutic_effect": item.therapeutic_effect
                    } for item in defeat_rewards.items
                ],
                "message": "挑"
            }
        }
    
    def _handle_ongoing_battle(self, user_id: str, demon_stats: DemonStats, 
                             damage_dealt: int) -> Dict[str, Any]:
        """?"""
        battle_state = self.active_battles[user_id]
        
        return {
            "result": BattleResult.ONGOING.value,
            "demon_name": demon_stats.name,
            "demon_hp": demon_stats.current_hp,
            "demon_max_hp": demon_stats.max_hp,
            "damage_dealt": damage_dealt,
            "turn_count": battle_state["turn_count"],
            "hp_percentage": (demon_stats.current_hp / demon_stats.max_hp) * 100,
            "suggested_actions": self._get_effective_actions(demon_stats.weaknesses),
            "encouragement": self._generate_encouragement_message(demon_stats, damage_dealt),
            "battle_tips": self._get_battle_tips(demon_stats.therapeutic_theme)
        }
    
    def _generate_victory_reflection(self, demon_data: Dict[str, Any]) -> str:
        """?"""
        theme = demon_data["therapeutic_theme"]
        name = demon_data["name"]
        
        prompts = {
            "?": f"{name}を",
            "?": f"{name}と",
            "無": f"{name}を",
            "?": f"{name}を"
        }
        
        return prompts.get(theme, f"{name}と")
    
    def _generate_support_message(self, demon_data: Dict[str, Any]) -> str:
        """?"""
        name = demon_data["name"]
        theme = demon_data["therapeutic_theme"]
        
        messages = {
            "?": f"{name}は",
            "?": f"{name}と",
            "無": f"{name}は",
            "?": f"{name}に"
        }
        
        return messages.get(theme, f"{name}と")
    
    def _suggest_alternative_strategies(self, weaknesses: List[str]) -> List[str]:
        """?"""
        strategy_map = {
            "routine_task_completion": "?1つ",
            "pomodoro_usage": "5?",
            "breathing_exercise": "4-7-8?1?",
            "social_connection": "?",
            "creative_expression": "?1?",
            "physical_activity": "?3?"
        }
        
        strategies = []
        for weakness in weaknesses[:3]:  # ?3つ
            if weakness in strategy_map:
                strategies.append(strategy_map[weakness])
        
        return strategies
    
    def _get_effective_actions(self, weaknesses: List[str]) -> List[str]:
        """?"""
        return weaknesses[:3]  # ?3つ
    
    def _generate_encouragement_message(self, demon_stats: DemonStats, damage: int) -> str:
        """?"""
        hp_percentage = (demon_stats.current_hp / demon_stats.max_hp) * 100
        
        if damage > 20:
            return f"?{demon_stats.name}に"
        elif hp_percentage < 30:
            return f"{demon_stats.name}は"
        elif hp_percentage < 60:
            return f"?"
        else:
            return f"{demon_stats.name}と"
    
    def _get_battle_tips(self, therapeutic_theme: str) -> List[str]:
        """バリデーション"""
        tips = {
            "?": [
                "?",
                "タスク",
                "?1つ"
            ],
            "?": [
                "?",
                "?",
                "?"
            ],
            "無": [
                "?",
                "?",
                "?1つ"
            ],
            "?": [
                "?",
                "?",
                "自動"
            ]
        }
        
        return tips.get(therapeutic_theme, ["あ"])
    
    def _suggest_reinforcement_actions(self, weaknesses: List[str]) -> List[str]:
        """?"""
        reinforcement_map = {
            "routine_task_completion": "?",
            "pomodoro_usage": "?",
            "breathing_exercise": "ストーリー",
            "social_connection": "?",
            "creative_expression": "創",
            "physical_activity": "?",
            "mindfulness_practice": "?",
            "positive_affirmation": "?"
        }
        
        actions = []
        for weakness in weaknesses[:3]:  # ?3つ
            if weakness in reinforcement_map:
                actions.append(reinforcement_map[weakness])
        
        return actions
    
    def _count_weakness_hits(self, user_actions: List[str], weaknesses: List[str]) -> int:
        """?"""
        hits = 0
        for action in user_actions:
            if action in weaknesses:
                hits += 1
        return hits
    
    def get_battle_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """バリデーション"""
        if user_id not in self.active_battles:
            return None
        
        battle_state = self.active_battles[user_id]
        demon_stats = battle_state["demon_stats"]
        
        return {
            "demon_name": demon_stats.name,
            "demon_hp": demon_stats.current_hp,
            "demon_max_hp": demon_stats.max_hp,
            "turn_count": battle_state["turn_count"],
            "therapeutic_theme": demon_stats.therapeutic_theme,
            "weaknesses": demon_stats.weaknesses,
            "battle_duration": (datetime.now() - battle_state["start_time"]).seconds
        }
    
    def get_available_demons(self) -> List[Dict[str, Any]]:
        """?"""
        demons = []
        for demon_type, data in self.demon_types.items():
            demons.append({
                "type": demon_type.value,
                "name": data["name"],
                "description": data["description"],
                "therapeutic_theme": data["therapeutic_theme"],
                "max_hp": data["max_hp"],
                "weaknesses": data["weaknesses"]
            })
        return demons

# APIエラー
def create_battle_system():
    """バリデーション"""
    return InnerDemonBattle()

if __name__ == "__main__":
    # ?
    battle_system = create_battle_system()
    
    # ?
    print("=== ? ===")
    demons = battle_system.get_available_demons()
    for demon in demons:
        print(f"{demon['name']}: {demon['description']}")
    
    # バリデーション
    print("\n=== バリデーション ===")
    user_actions = ["routine_task_completion", "pomodoro_usage"]
    result = battle_system.initiate_battle("test_user", DemonType.PROCRASTINATION_DRAGON, user_actions)
    print(json.dumps(result, ensure_ascii=False, indent=2))