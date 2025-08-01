"""
?

5?common?legendary?
治療
"""

import random
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.utils.exceptions import ValidationError, InsufficientCoinsError


class ItemRarity(Enum):
    """アプリ"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ItemType(Enum):
    """アプリ"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MAGIC = "magic"


class TherapeuticTheme(Enum):
    """治療"""
    FOCUS = "focus"           # ?
    RESILIENCE = "resilience" # ?
    MOTIVATION = "motivation" # や
    SOCIAL = "social"         # ?
    CREATIVITY = "creativity" # 創
    WISDOM = "wisdom"         # ?


@dataclass
class Item:
    """アプリ"""
    id: str
    name: str
    description: str
    rarity: ItemRarity
    item_type: ItemType
    therapeutic_theme: TherapeuticTheme
    stat_bonuses: Dict[str, int]
    special_effects: List[str]
    flavor_text: str
    created_at: datetime


@dataclass
class GachaResult:
    """?"""
    success: bool
    items: List[Item]
    coins_spent: int
    gacha_type: str
    guaranteed_rare: bool
    timestamp: datetime
    error_message: Optional[str] = None


class GachaSystem:
    """
    ?
    
    5?
    アプリ
    """
    
    def __init__(self):
        # レベル
        self.rarity_rates = {
            ItemRarity.COMMON: 0.60,     # 60%
            ItemRarity.UNCOMMON: 0.25,   # 25%
            ItemRarity.RARE: 0.10,       # 10%
            ItemRarity.EPIC: 0.04,       # 4%
            ItemRarity.LEGENDARY: 0.01   # 1%
        }
        
        # ?
        self.gacha_costs = {
            "single": 100,
            "ten_pull": 900,    # 10%?
            "premium": 300      # レベル2?
        }
        
        # 治療
        self.item_templates = self._initialize_item_templates()
        
        # レベル
        self.stat_bonus_ranges = {
            ItemRarity.COMMON: (1, 3),
            ItemRarity.UNCOMMON: (2, 5),
            ItemRarity.RARE: (4, 8),
            ItemRarity.EPIC: (7, 12),
            ItemRarity.LEGENDARY: (10, 20)
        }
    
    def _initialize_item_templates(self) -> Dict:
        """アプリ"""
        return {
            TherapeuticTheme.FOCUS: {
                ItemType.WEAPON: {
                    "names": ["?", "?", "?", "?"],
                    "descriptions": ["?", "?", "?", "?"],
                    "effects": ["task_focus_boost", "distraction_resistance", "deep_work_mode"]
                },
                ItemType.ARMOR: {
                    "names": ["?", "?", "?", "?"],
                    "descriptions": ["?", "?", "?", "気分"],
                    "effects": ["noise_cancellation", "focus_duration_extend", "meditation_boost"]
                },
                ItemType.ACCESSORY: {
                    "names": ["?", "?", "?", "?"],
                    "descriptions": ["?", "?", "?", "?"],
                    "effects": ["attention_sustain", "mind_clarity", "focus_recovery"]
                }
            },
            TherapeuticTheme.RESILIENCE: {
                ItemType.WEAPON: {
                    "names": ["?", "レベル", "?", "希"],
                    "descriptions": ["?", "?", "?", "希"],
                    "effects": ["stress_recovery", "emotional_healing", "bounce_back_boost"]
                },
                ItemType.ARMOR: {
                    "names": ["?", "レベル", "?", "希"],
                    "descriptions": ["?", "?", "?", "希"],
                    "effects": ["damage_reduction", "quick_recovery", "emotional_armor"]
                },
                ItemType.CONSUMABLE: {
                    "names": ["?", "レベル", "希", "?"],
                    "descriptions": ["?", "?", "希", "?"],
                    "effects": ["instant_recovery", "stress_relief", "energy_restore"]
                }
            },
            TherapeuticTheme.MOTIVATION: {
                ItemType.WEAPON: {
                    "names": ["や", "モデル", "?", "意"],
                    "descriptions": ["や", "モデル", "?", "意"],
                    "effects": ["motivation_boost", "passion_ignite", "drive_enhance"]
                },
                ItemType.ACCESSORY: {
                    "names": ["や", "モデル", "?", "意"],
                    "descriptions": ["や", "モデル", "?", "意"],
                    "effects": ["motivation_sustain", "goal_clarity", "persistence_boost"]
                }
            },
            TherapeuticTheme.SOCIAL: {
                ItemType.WEAPON: {
                    "names": ["コア", "?", "共有", "?"],
                    "descriptions": ["?", "?", "共有", "?"],
                    "effects": ["communication_boost", "empathy_enhance", "social_confidence"]
                },
                ItemType.ACCESSORY: {
                    "names": ["?", "?", "共有", "?"],
                    "descriptions": ["?", "?", "共有", "?"],
                    "effects": ["friendship_boost", "social_ease", "connection_strengthen"]
                }
            },
            TherapeuticTheme.CREATIVITY: {
                ItemType.WEAPON: {
                    "names": ["創", "アプリ", "発", "?"],
                    "descriptions": ["?", "創", "発", "?"],
                    "effects": ["creativity_boost", "idea_generation", "artistic_inspiration"]
                },
                ItemType.ACCESSORY: {
                    "names": ["創", "アプリ", "発", "?"],
                    "descriptions": ["創", "アプリ", "発", "?"],
                    "effects": ["creative_flow", "innovation_boost", "artistic_vision"]
                }
            },
            TherapeuticTheme.WISDOM: {
                ItemType.WEAPON: {
                    "names": ["?", "?", "理", "学"],
                    "descriptions": ["?", "物語", "理", "学"],
                    "effects": ["wisdom_boost", "insight_enhance", "learning_accelerate"]
                },
                ItemType.ACCESSORY: {
                    "names": ["?", "?", "理", "学"],
                    "descriptions": ["?", "?", "理", "学"],
                    "effects": ["knowledge_retention", "analytical_thinking", "study_efficiency"]
                }
            }
        }
    
    def perform_gacha(self, gacha_type: str, user_coins: int) -> GachaResult:
        """
        ?
        
        Args:
            gacha_type: ? ("single", "ten_pull", "premium")
            user_coins: ユーザー
            
        Returns:
            GachaResult: ?
        """
        # バリデーション
        if gacha_type not in self.gacha_costs:
            return GachaResult(
                success=False,
                items=[],
                coins_spent=0,
                gacha_type=gacha_type,
                guaranteed_rare=False,
                timestamp=datetime.now(),
                error_message=f"無: {gacha_type}"
            )
        
        cost = self.gacha_costs[gacha_type]
        if user_coins < cost:
            return GachaResult(
                success=False,
                items=[],
                coins_spent=0,
                gacha_type=gacha_type,
                guaranteed_rare=False,
                timestamp=datetime.now(),
                error_message=f"コア: {cost}, ?: {user_coins}"
            )
        
        # ?
        items = []
        pulls = 10 if gacha_type == "ten_pull" else 1
        is_premium = gacha_type == "premium"
        
        for i in range(pulls):
            # 10?
            if gacha_type == "ten_pull" and i == 9:
                has_rare_or_better = any(
                    item.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY] 
                    for item in items
                )
                if not has_rare_or_better:
                    rarity = self._determine_guaranteed_rare_rarity()
                else:
                    rarity = self._determine_rarity(is_premium)
            else:
                rarity = self._determine_rarity(is_premium)
            
            item = self._generate_item(rarity)
            items.append(item)
        
        # 10?
        guaranteed_rare = (gacha_type == "ten_pull" and 
                          not any(item.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY] 
                                 for item in items[:-1]))
        
        return GachaResult(
            success=True,
            items=items,
            coins_spent=cost,
            gacha_type=gacha_type,
            guaranteed_rare=guaranteed_rare,
            timestamp=datetime.now()
        )
    
    def _determine_rarity(self, is_premium: bool = False) -> ItemRarity:
        """レベル"""
        rates = self.rarity_rates.copy()
        
        # プレビュー2?
        if is_premium:
            rates[ItemRarity.RARE] *= 2
            rates[ItemRarity.EPIC] *= 2
            rates[ItemRarity.LEGENDARY] *= 2
            
            # ?
            total = sum(rates.values())
            rates = {k: v / total for k, v in rates.items()}
        
        # ?
        rand = random.random()
        cumulative = 0
        
        for rarity, rate in rates.items():
            cumulative += rate
            if rand <= cumulative:
                return rarity
        
        return ItemRarity.COMMON  # ?
    
    def _determine_guaranteed_rare_rarity(self) -> ItemRarity:
        """?"""
        rare_rates = {
            ItemRarity.RARE: 0.85,      # 85%
            ItemRarity.EPIC: 0.13,      # 13%
            ItemRarity.LEGENDARY: 0.02  # 2%
        }
        
        rand = random.random()
        cumulative = 0
        
        for rarity, rate in rare_rates.items():
            cumulative += rate
            if rand <= cumulative:
                return rarity
        
        return ItemRarity.RARE  # ?
    
    def _generate_item(self, rarity: ItemRarity) -> Item:
        """アプリ"""
        # ?
        theme = random.choice(list(TherapeuticTheme))
        available_types = list(self.item_templates[theme].keys())
        item_type = random.choice(available_types)
        
        # ?
        template = self.item_templates[theme][item_type]
        name = random.choice(template["names"])
        description = random.choice(template["descriptions"])
        effects = random.sample(template["effects"], min(len(template["effects"]), 2))
        
        # ストーリー
        stat_bonuses = self._generate_stat_bonuses(rarity, theme)
        
        # ?
        flavor_text = self._generate_flavor_text(name, rarity, theme)
        
        return Item(
            id=str(uuid.uuid4()),
            name=f"{self._get_rarity_prefix(rarity)}{name}",
            description=description,
            rarity=rarity,
            item_type=item_type,
            therapeutic_theme=theme,
            stat_bonuses=stat_bonuses,
            special_effects=effects,
            flavor_text=flavor_text,
            created_at=datetime.now()
        )
    
    def _generate_stat_bonuses(self, rarity: ItemRarity, theme: TherapeuticTheme) -> Dict[str, int]:
        """ストーリー"""
        min_bonus, max_bonus = self.stat_bonus_ranges[rarity]
        
        # 治療
        primary_stats = {
            TherapeuticTheme.FOCUS: ["focus"],
            TherapeuticTheme.RESILIENCE: ["resilience"],
            TherapeuticTheme.MOTIVATION: ["motivation"],
            TherapeuticTheme.SOCIAL: ["social"],
            TherapeuticTheme.CREATIVITY: ["creativity"],
            TherapeuticTheme.WISDOM: ["wisdom"]
        }
        
        bonuses = {}
        
        # ?
        for stat in primary_stats[theme]:
            bonuses[stat] = random.randint(max(min_bonus, max_bonus - 2), max_bonus)
        
        # レベル
        if rarity in [ItemRarity.EPIC, ItemRarity.LEGENDARY]:
            all_stats = ["focus", "resilience", "motivation", "social", "creativity", "wisdom"]
            secondary_stats = [s for s in all_stats if s not in primary_stats[theme]]
            
            num_secondary = 1 if rarity == ItemRarity.EPIC else 2
            for stat in random.sample(secondary_stats, min(num_secondary, len(secondary_stats))):
                bonuses[stat] = random.randint(min_bonus, max(min_bonus + 2, max_bonus - 3))
        
        return bonuses
    
    def _get_rarity_prefix(self, rarity: ItemRarity) -> str:
        """レベル"""
        prefixes = {
            ItemRarity.COMMON: "",
            ItemRarity.UNCOMMON: "?",
            ItemRarity.RARE: "希",
            ItemRarity.EPIC: "?",
            ItemRarity.LEGENDARY: "?"
        }
        return prefixes.get(rarity, "")
    
    def _generate_flavor_text(self, name: str, rarity: ItemRarity, theme: TherapeuticTheme) -> str:
        """?"""
        theme_messages = {
            TherapeuticTheme.FOCUS: "?",
            TherapeuticTheme.RESILIENCE: "?",
            TherapeuticTheme.MOTIVATION: "や",
            TherapeuticTheme.SOCIAL: "?",
            TherapeuticTheme.CREATIVITY: "?",
            TherapeuticTheme.WISDOM: "?"
        }
        
        rarity_messages = {
            ItemRarity.COMMON: "?",
            ItemRarity.UNCOMMON: "や",
            ItemRarity.RARE: "?",
            ItemRarity.EPIC: "?",
            ItemRarity.LEGENDARY: "?"
        }
        
        return f"{rarity_messages[rarity]}{name}?{theme_messages[theme]}?"
    
    def get_gacha_rates(self, gacha_type: str) -> Dict:
        """?"""
        if gacha_type not in self.gacha_costs:
            raise ValidationError(f"無: {gacha_type}")
        
        rates = self.rarity_rates.copy()
        
        # プレビュー
        if gacha_type == "premium":
            rates[ItemRarity.RARE] *= 2
            rates[ItemRarity.EPIC] *= 2
            rates[ItemRarity.LEGENDARY] *= 2
            
            total = sum(rates.values())
            rates = {k: v / total for k, v in rates.items()}
        
        return {
            "gacha_type": gacha_type,
            "cost": self.gacha_costs[gacha_type],
            "rates": {rarity.value: f"{rate * 100:.1f}%" for rarity, rate in rates.items()},
            "guaranteed_rare": gacha_type == "ten_pull",
            "premium_bonus": gacha_type == "premium"
        }
    
    def get_item_statistics(self, items: List[Item]) -> Dict:
        """アプリ"""
        if not items:
            return {"total": 0, "by_rarity": {}, "by_theme": {}, "by_type": {}}
        
        rarity_count = {}
        theme_count = {}
        type_count = {}
        
        for item in items:
            # レベル
            rarity_count[item.rarity.value] = rarity_count.get(item.rarity.value, 0) + 1
            
            # ?
            theme_count[item.therapeutic_theme.value] = theme_count.get(item.therapeutic_theme.value, 0) + 1
            
            # タスク
            type_count[item.item_type.value] = type_count.get(item.item_type.value, 0) + 1
        
        return {
            "total": len(items),
            "by_rarity": rarity_count,
            "by_theme": theme_count,
            "by_type": type_count,
            "average_stats": self._calculate_average_stats(items)
        }
    
    def _calculate_average_stats(self, items: List[Item]) -> Dict[str, float]:
        """?"""
        if not items:
            return {}
        
        all_stats = ["focus", "resilience", "motivation", "social", "creativity", "wisdom"]
        stat_totals = {stat: 0 for stat in all_stats}
        stat_counts = {stat: 0 for stat in all_stats}
        
        for item in items:
            for stat, value in item.stat_bonuses.items():
                if stat in stat_totals:
                    stat_totals[stat] += value
                    stat_counts[stat] += 1
        
        return {
            stat: round(stat_totals[stat] / stat_counts[stat], 2) if stat_counts[stat] > 0 else 0
            for stat in all_stats
        }


if __name__ == "__main__":
    # 基本
    gacha = GachaSystem()
    
    # ?
    result = gacha.perform_gacha("single", 1000)
    if result.success:
        item = result.items[0]
        print(f"?:")
        print(f"  {item.name} ({item.rarity.value})")
        print(f"  {item.description}")
        print(f"  ストーリー: {item.stat_bonuses}")
        print(f"  ?: {item.special_effects}")
        print(f"  {item.flavor_text}")
    
    # 10?
    result_10 = gacha.perform_gacha("ten_pull", 1000)
    if result_10.success:
        print(f"\n10?:")
        stats = gacha.get_item_statistics(result_10.items)
        print(f"  ?: {stats['total']}")
        print(f"  レベル: {stats['by_rarity']}")
        print(f"  ?: {result_10.guaranteed_rare}")
    
    # ?
    rates = gacha.get_gacha_rates("premium")
    print(f"\nプレビュー:")
    for rarity, rate in rates["rates"].items():
        print(f"  {rarity}: {rate}")