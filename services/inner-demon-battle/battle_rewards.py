"""
バリデーションCBT?
?CBT?
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import random
from datetime import datetime

class ItemRarity(Enum):
    """アプリ"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class BattleItem:
    """バリデーション"""
    id: str
    name: str
    description: str
    rarity: ItemRarity
    therapeutic_effect: str
    stat_bonus: Dict[str, int]

@dataclass
class BattleRewards:
    """バリデーション"""
    coins: int
    xp: int
    items: List[BattleItem]
    therapeutic_message: str
    cbt_reflection_prompt: str

class BattleRewardSystem:
    """バリデーション"""
    
    def __init__(self):
        self.item_pool = self._initialize_item_pool()
        self.rarity_rates = {
            ItemRarity.COMMON: 0.50,
            ItemRarity.UNCOMMON: 0.30,
            ItemRarity.RARE: 0.15,
            ItemRarity.EPIC: 0.04,
            ItemRarity.LEGENDARY: 0.01
        }
    
    def _initialize_item_pool(self) -> Dict[str, List[BattleItem]]:
        """アプリ"""
        return {
            "procrastination_dragon": [
                BattleItem(
                    id="focus_potion",
                    name="?",
                    description="?",
                    rarity=ItemRarity.COMMON,
                    therapeutic_effect="?",
                    stat_bonus={"focus": 2, "motivation": 1}
                ),
                BattleItem(
                    id="time_crystal",
                    name="?",
                    description="?",
                    rarity=ItemRarity.UNCOMMON,
                    therapeutic_effect="?",
                    stat_bonus={"focus": 3, "wisdom": 2}
                ),
                BattleItem(
                    id="motivation_gem",
                    name="や",
                    description="?",
                    rarity=ItemRarity.RARE,
                    therapeutic_effect="?",
                    stat_bonus={"motivation": 4, "resilience": 2}
                ),
                BattleItem(
                    id="procrastination_slayer",
                    name="?",
                    description="?",
                    rarity=ItemRarity.LEGENDARY,
                    therapeutic_effect="?",
                    stat_bonus={"focus": 8, "motivation": 6, "resilience": 4}
                )
            ],
            "anxiety_shadow": [
                BattleItem(
                    id="calm_amulet",
                    name="?",
                    description="?",
                    rarity=ItemRarity.COMMON,
                    therapeutic_effect="?",
                    stat_bonus={"resilience": 2, "social": 1}
                ),
                BattleItem(
                    id="courage_ring",
                    name="勇",
                    description="?",
                    rarity=ItemRarity.UNCOMMON,
                    therapeutic_effect="勇",
                    stat_bonus={"resilience": 3, "social": 2}
                ),
                BattleItem(
                    id="peace_stone",
                    name="安全",
                    description="?",
                    rarity=ItemRarity.RARE,
                    therapeutic_effect="?",
                    stat_bonus={"resilience": 4, "wisdom": 3}
                ),
                BattleItem(
                    id="anxiety_vanquisher",
                    name="?",
                    description="あ",
                    rarity=ItemRarity.LEGENDARY,
                    therapeutic_effect="?",
                    stat_bonus={"resilience": 8, "social": 6, "wisdom": 4}
                )
            ],
            "depression_void": [
                BattleItem(
                    id="hope_crystal",
                    name="希",
                    description="?",
                    rarity=ItemRarity.COMMON,
                    therapeutic_effect="希",
                    stat_bonus={"motivation": 2, "creativity": 1}
                ),
                BattleItem(
                    id="energy_elixir",
                    name="?",
                    description="?",
                    rarity=ItemRarity.UNCOMMON,
                    therapeutic_effect="?",
                    stat_bonus={"motivation": 3, "resilience": 2}
                ),
                BattleItem(
                    id="connection_charm",
                    name="つ",
                    description="?",
                    rarity=ItemRarity.RARE,
                    therapeutic_effect="?",
                    stat_bonus={"social": 4, "creativity": 3}
                ),
                BattleItem(
                    id="void_destroyer",
                    name="?",
                    description="あ",
                    rarity=ItemRarity.LEGENDARY,
                    therapeutic_effect="?",
                    stat_bonus={"motivation": 8, "creativity": 6, "social": 4}
                )
            ],
            "social_fear_goblin": [
                BattleItem(
                    id="confidence_badge",
                    name="自動",
                    description="自動",
                    rarity=ItemRarity.COMMON,
                    therapeutic_effect="自動",
                    stat_bonus={"social": 2, "motivation": 1}
                ),
                BattleItem(
                    id="social_key",
                    name="?",
                    description="?",
                    rarity=ItemRarity.UNCOMMON,
                    therapeutic_effect="?",
                    stat_bonus={"social": 3, "creativity": 2}
                ),
                BattleItem(
                    id="communication_scroll",
                    name="コア",
                    description="?",
                    rarity=ItemRarity.RARE,
                    therapeutic_effect="コア",
                    stat_bonus={"social": 4, "wisdom": 3}
                ),
                BattleItem(
                    id="social_master_crown",
                    name="?",
                    description="あ",
                    rarity=ItemRarity.LEGENDARY,
                    therapeutic_effect="?",
                    stat_bonus={"social": 8, "creativity": 6, "wisdom": 4}
                )
            ]
        }
    
    def calculate_victory_rewards(self, demon_type: str, battle_performance: Dict[str, Any]) -> BattleRewards:
        """?"""
        base_rewards = self._get_base_rewards(demon_type)
        
        # ?
        performance_multiplier = self._calculate_performance_multiplier(battle_performance)
        
        # コアXP計算
        coins = int(base_rewards["coins"] * performance_multiplier)
        xp = int(base_rewards["xp"] * performance_multiplier)
        
        # アプリ
        items = self._generate_battle_items(demon_type, performance_multiplier)
        
        # CBT?
        cbt_prompt = self._generate_cbt_reflection(demon_type, battle_performance)
        
        return BattleRewards(
            coins=coins,
            xp=xp,
            items=items,
            therapeutic_message=base_rewards["therapeutic_message"],
            cbt_reflection_prompt=cbt_prompt
        )
    
    def calculate_defeat_rewards(self, demon_type: str, battle_performance: Dict[str, Any]) -> BattleRewards:
        """?"""
        base_rewards = self._get_base_rewards(demon_type)
        
        # ?25%?
        coins = base_rewards["coins"] // 4
        xp = base_rewards["xp"] // 4
        
        # ?1?
        items = self._generate_consolation_items(demon_type)
        
        # ?CBT?
        support_message = self._generate_support_message(demon_type)
        cbt_prompt = self._generate_defeat_cbt_reflection(demon_type, battle_performance)
        
        return BattleRewards(
            coins=coins,
            xp=xp,
            items=items,
            therapeutic_message=support_message,
            cbt_reflection_prompt=cbt_prompt
        )
    
    def _get_base_rewards(self, demon_type: str) -> Dict[str, Any]:
        """基本"""
        base_rewards = {
            "procrastination_dragon": {
                "coins": 150,
                "xp": 75,
                "therapeutic_message": "?"
            },
            "anxiety_shadow": {
                "coins": 120,
                "xp": 60,
                "therapeutic_message": "?"
            },
            "depression_void": {
                "coins": 200,
                "xp": 100,
                "therapeutic_message": "つ"
            },
            "social_fear_goblin": {
                "coins": 100,
                "xp": 50,
                "therapeutic_message": "?"
            }
        }
        
        return base_rewards.get(demon_type, base_rewards["procrastination_dragon"])
    
    def _calculate_performance_multiplier(self, battle_performance: Dict[str, Any]) -> float:
        """?"""
        base_multiplier = 1.0
        
        # タスク
        turns = battle_performance.get("turns_taken", 5)
        if turns <= 2:
            base_multiplier += 0.5  # 50%?
        elif turns <= 3:
            base_multiplier += 0.3  # 30%?
        elif turns <= 4:
            base_multiplier += 0.1  # 10%?
        
        # ?
        damage_efficiency = battle_performance.get("damage_efficiency", 0.5)
        if damage_efficiency > 0.8:
            base_multiplier += 0.3
        elif damage_efficiency > 0.6:
            base_multiplier += 0.2
        elif damage_efficiency > 0.4:
            base_multiplier += 0.1
        
        # ?
        weakness_hits = battle_performance.get("weakness_hits", 0)
        base_multiplier += min(0.4, weakness_hits * 0.1)  # ?40%?
        
        return min(2.0, base_multiplier)  # ?200%
    
    def _generate_battle_items(self, demon_type: str, performance_multiplier: float) -> List[BattleItem]:
        """バリデーション"""
        items = []
        item_pool = self.item_pool.get(demon_type, [])
        
        if not item_pool:
            return items
        
        # アプリ
        base_item_count = 1
        if performance_multiplier > 1.5:
            base_item_count = 3
        elif performance_multiplier > 1.2:
            base_item_count = 2
        
        for _ in range(base_item_count):
            # レベル
            rarity = self._determine_item_rarity(performance_multiplier)
            
            # ?
            rarity_items = [item for item in item_pool if item.rarity == rarity]
            if rarity_items:
                items.append(random.choice(rarity_items))
            else:
                # ?
                common_items = [item for item in item_pool if item.rarity == ItemRarity.COMMON]
                if common_items:
                    items.append(random.choice(common_items))
        
        return items
    
    def _generate_consolation_items(self, demon_type: str) -> List[BattleItem]:
        """?"""
        item_pool = self.item_pool.get(demon_type, [])
        common_items = [item for item in item_pool if item.rarity == ItemRarity.COMMON]
        
        if common_items:
            return [random.choice(common_items)]
        return []
    
    def _determine_item_rarity(self, performance_multiplier: float) -> ItemRarity:
        """アプリ"""
        # ?
        adjusted_rates = self.rarity_rates.copy()
        
        if performance_multiplier > 1.5:
            # ?
            adjusted_rates[ItemRarity.LEGENDARY] *= 3
            adjusted_rates[ItemRarity.EPIC] *= 2
            adjusted_rates[ItemRarity.RARE] *= 1.5
        elif performance_multiplier > 1.2:
            adjusted_rates[ItemRarity.EPIC] *= 1.5
            adjusted_rates[ItemRarity.RARE] *= 1.3
        
        # ?
        total_rate = sum(adjusted_rates.values())
        normalized_rates = {k: v/total_rate for k, v in adjusted_rates.items()}
        
        # ?
        rand = random.random()
        cumulative = 0
        
        for rarity, rate in normalized_rates.items():
            cumulative += rate
            if rand <= cumulative:
                return rarity
        
        return ItemRarity.COMMON
    
    def _generate_cbt_reflection(self, demon_type: str, battle_performance: Dict[str, Any]) -> str:
        """CBT?"""
        cbt_prompts = {
            "procrastination_dragon": [
                "?",
                "?",
                "?",
                "?"
            ],
            "anxiety_shadow": [
                "?",
                "?",
                "?",
                "?"
            ],
            "depression_void": [
                "?",
                "?",
                "?",
                "?"
            ],
            "social_fear_goblin": [
                "?",
                "?",
                "?",
                "?"
            ]
        }
        
        prompts = cbt_prompts.get(demon_type, cbt_prompts["procrastination_dragon"])
        
        # バリデーション
        turns = battle_performance.get("turns_taken", 3)
        if turns <= 2:
            # ?
            return f"{prompts[0]} ?"
        elif turns >= 5:
            # ?
            return f"{prompts[1]} ?"
        else:
            return random.choice(prompts)
    
    def _generate_defeat_cbt_reflection(self, demon_type: str, battle_performance: Dict[str, Any]) -> str:
        """?CBT?"""
        defeat_prompts = {
            "procrastination_dragon": [
                "?",
                "?",
                "?"
            ],
            "anxiety_shadow": [
                "?",
                "?",
                "?"
            ],
            "depression_void": [
                "?",
                "?",
                "支援"
            ],
            "social_fear_goblin": [
                "?",
                "?",
                "?"
            ]
        }
        
        prompts = defeat_prompts.get(demon_type, defeat_prompts["procrastination_dragon"])
        return random.choice(prompts)
    
    def _generate_support_message(self, demon_type: str) -> str:
        """?"""
        support_messages = {
            "procrastination_dragon": "?",
            "anxiety_shadow": "?",
            "depression_void": "?",
            "social_fear_goblin": "?"
        }
        
        return support_messages.get(demon_type, support_messages["procrastination_dragon"])

# ?
def create_reward_system():
    """?"""
    return BattleRewardSystem()

if __name__ == "__main__":
    # ?
    reward_system = create_reward_system()
    
    # ?
    print("=== ? ===")
    battle_performance = {
        "turns_taken": 2,
        "damage_efficiency": 0.9,
        "weakness_hits": 4
    }
    
    victory_rewards = reward_system.calculate_victory_rewards("procrastination_dragon", battle_performance)
    print(f"コア: {victory_rewards.coins}")
    print(f"XP: {victory_rewards.xp}")
    print(f"アプリ: {len(victory_rewards.items)}")
    for item in victory_rewards.items:
        print(f"  - {item.name} ({item.rarity.value}): {item.description}")
    print(f"CBT?: {victory_rewards.cbt_reflection_prompt}")
    
    # ?
    print("\n=== ? ===")
    defeat_performance = {
        "turns_taken": 10,
        "damage_efficiency": 0.3,
        "weakness_hits": 1
    }
    
    defeat_rewards = reward_system.calculate_defeat_rewards("anxiety_shadow", defeat_performance)
    print(f"?: {defeat_rewards.coins}")
    print(f"?XP: {defeat_rewards.xp}")
    print(f"?: {defeat_rewards.items[0].name if defeat_rewards.items else 'な'}")
    print(f"?: {defeat_rewards.therapeutic_message}")
    print(f"CBT?: {defeat_rewards.cbt_reflection_prompt}")