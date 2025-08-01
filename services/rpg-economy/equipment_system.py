"""
?

6ストーリー3?
6?
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import copy

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from gacha_system import Item, ItemType, ItemRarity
from shared.utils.exceptions import ValidationError, InvalidEquipmentSlotError, ItemNotFoundError


class EquipmentSlot(Enum):
    """?"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE_1 = "consumable_1"
    CONSUMABLE_2 = "consumable_2"
    CONSUMABLE_3 = "consumable_3"


class StatType(Enum):
    """?"""
    FOCUS = "focus"           # ?
    RESILIENCE = "resilience" # ?
    MOTIVATION = "motivation" # や
    SOCIAL = "social"         # ?
    CREATIVITY = "creativity" # 創
    WISDOM = "wisdom"         # ?


@dataclass
class EquipmentStats:
    """?"""
    focus: int = 0
    resilience: int = 0
    motivation: int = 0
    social: int = 0
    creativity: int = 0
    wisdom: int = 0
    
    def __add__(self, other: 'EquipmentStats') -> 'EquipmentStats':
        """?"""
        return EquipmentStats(
            focus=self.focus + other.focus,
            resilience=self.resilience + other.resilience,
            motivation=self.motivation + other.motivation,
            social=self.social + other.social,
            creativity=self.creativity + other.creativity,
            wisdom=self.wisdom + other.wisdom
        )
    
    def __sub__(self, other: 'EquipmentStats') -> 'EquipmentStats':
        """?"""
        return EquipmentStats(
            focus=self.focus - other.focus,
            resilience=self.resilience - other.resilience,
            motivation=self.motivation - other.motivation,
            social=self.social - other.social,
            creativity=self.creativity - other.creativity,
            wisdom=self.wisdom - other.wisdom
        )
    
    def to_dict(self) -> Dict[str, int]:
        """?"""
        return {
            "focus": self.focus,
            "resilience": self.resilience,
            "motivation": self.motivation,
            "social": self.social,
            "creativity": self.creativity,
            "wisdom": self.wisdom
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'EquipmentStats':
        """?"""
        return cls(
            focus=data.get("focus", 0),
            resilience=data.get("resilience", 0),
            motivation=data.get("motivation", 0),
            social=data.get("social", 0),
            creativity=data.get("creativity", 0),
            wisdom=data.get("wisdom", 0)
        )
    
    def get_total_bonus(self) -> int:
        """?"""
        return self.focus + self.resilience + self.motivation + self.social + self.creativity + self.wisdom


@dataclass
class EquipmentSet:
    """?"""
    weapon: Optional[Item] = None
    armor: Optional[Item] = None
    accessory: Optional[Item] = None
    consumable_1: Optional[Item] = None
    consumable_2: Optional[Item] = None
    consumable_3: Optional[Item] = None
    
    def get_equipped_items(self) -> List[Item]:
        """?"""
        items = []
        for slot in EquipmentSlot:
            item = getattr(self, slot.value)
            if item:
                items.append(item)
        return items
    
    def get_item_by_slot(self, slot: EquipmentSlot) -> Optional[Item]:
        """ストーリー"""
        return getattr(self, slot.value)
    
    def set_item_by_slot(self, slot: EquipmentSlot, item: Optional[Item]) -> None:
        """ストーリー"""
        setattr(self, slot.value, item)


@dataclass
class TaskCompletionBonus:
    """タスク"""
    base_efficiency: float
    focus_bonus: float
    motivation_bonus: float
    total_bonus: float
    active_effects: List[str]
    timestamp: datetime


class EquipmentSystem:
    """
    ?
    
    6ストーリー6?
    ?
    """
    
    def __init__(self):
        # ストーリー
        self.slot_item_types = {
            EquipmentSlot.WEAPON: [ItemType.WEAPON],
            EquipmentSlot.ARMOR: [ItemType.ARMOR],
            EquipmentSlot.ACCESSORY: [ItemType.ACCESSORY],
            EquipmentSlot.CONSUMABLE_1: [ItemType.CONSUMABLE],
            EquipmentSlot.CONSUMABLE_2: [ItemType.CONSUMABLE],
            EquipmentSlot.CONSUMABLE_3: [ItemType.CONSUMABLE]
        }
        
        # ?
        self.stat_efficiency_coefficients = {
            StatType.FOCUS: 0.02,      # ?: 2%/point
            StatType.MOTIVATION: 0.015, # や: 1.5%/point
            StatType.RESILIENCE: 0.01,  # ?: 1%/point
            StatType.SOCIAL: 0.008,     # ?: 0.8%/point
            StatType.CREATIVITY: 0.012, # 創: 1.2%/point
            StatType.WISDOM: 0.01       # ?: 1%/point
        }
        
        # ?
        self.max_total_bonus = 0.5  # ?50%?
        
        # ?
        self.special_effect_bonuses = {
            "task_focus_boost": 0.05,
            "motivation_boost": 0.04,
            "deep_work_mode": 0.06,
            "productivity_enhance": 0.03,
            "efficiency_boost": 0.04,
            "concentration_aid": 0.03,
            "energy_boost": 0.02,
            "performance_enhance": 0.05
        }
    
    def equip_item(self, equipment_set: EquipmentSet, item: Item, slot: EquipmentSlot) -> Tuple[bool, str]:
        """
        アプリ
        
        Args:
            equipment_set: ?
            item: ?
            slot: ?
            
        Returns:
            Tuple[bool, str]: (成, メイン)
        """
        # ストーリー
        if slot not in EquipmentSlot:
            return False, f"無: {slot}"
        
        # アプリ
        allowed_types = self.slot_item_types[slot]
        if item.item_type not in allowed_types:
            return False, f"こ{slot.value}ストーリー"
        
        # ?
        old_item = equipment_set.get_item_by_slot(slot)
        
        # ?
        equipment_set.set_item_by_slot(slot, item)
        
        # メイン
        if old_item:
            message = f"{old_item.name}を{item.name}を"
        else:
            message = f"{item.name}を"
        
        return True, message
    
    def unequip_item(self, equipment_set: EquipmentSet, slot: EquipmentSlot) -> Tuple[bool, str]:
        """
        アプリ
        
        Args:
            equipment_set: ?
            slot: ?
            
        Returns:
            Tuple[bool, str]: (成, メイン)
        """
        if slot not in EquipmentSlot:
            return False, f"無: {slot}"
        
        item = equipment_set.get_item_by_slot(slot)
        if not item:
            return False, f"{slot.value}ストーリー"
        
        equipment_set.set_item_by_slot(slot, None)
        return True, f"{item.name}を"
    
    def calculate_total_stats(self, equipment_set: EquipmentSet) -> EquipmentStats:
        """
        ?
        
        Args:
            equipment_set: ?
            
        Returns:
            EquipmentStats: ?
        """
        total_stats = EquipmentStats()
        
        for item in equipment_set.get_equipped_items():
            item_stats = EquipmentStats.from_dict(item.stat_bonuses)
            total_stats = total_stats + item_stats
        
        return total_stats
    
    def calculate_task_completion_bonus(self, equipment_set: EquipmentSet) -> TaskCompletionBonus:
        """
        ?
        
        Args:
            equipment_set: ?
            
        Returns:
            TaskCompletionBonus: タスク
        """
        total_stats = self.calculate_total_stats(equipment_set)
        
        # 基本
        focus_bonus = total_stats.focus * self.stat_efficiency_coefficients[StatType.FOCUS]
        motivation_bonus = total_stats.motivation * self.stat_efficiency_coefficients[StatType.MOTIVATION]
        resilience_bonus = total_stats.resilience * self.stat_efficiency_coefficients[StatType.RESILIENCE]
        social_bonus = total_stats.social * self.stat_efficiency_coefficients[StatType.SOCIAL]
        creativity_bonus = total_stats.creativity * self.stat_efficiency_coefficients[StatType.CREATIVITY]
        wisdom_bonus = total_stats.wisdom * self.stat_efficiency_coefficients[StatType.WISDOM]
        
        base_efficiency = (focus_bonus + motivation_bonus + resilience_bonus + 
                          social_bonus + creativity_bonus + wisdom_bonus)
        
        # ?
        special_effects_bonus = 0
        active_effects = []
        
        for item in equipment_set.get_equipped_items():
            for effect in item.special_effects:
                if effect in self.special_effect_bonuses:
                    special_effects_bonus += self.special_effect_bonuses[effect]
                    active_effects.append(effect)
        
        # ?
        total_bonus = min(self.max_total_bonus, base_efficiency + special_effects_bonus)
        
        return TaskCompletionBonus(
            base_efficiency=base_efficiency,
            focus_bonus=focus_bonus,
            motivation_bonus=motivation_bonus,
            total_bonus=total_bonus,
            active_effects=active_effects,
            timestamp=datetime.now()
        )
    
    def get_equipment_summary(self, equipment_set: EquipmentSet) -> Dict:
        """
        ?
        
        Args:
            equipment_set: ?
            
        Returns:
            Dict: ?
        """
        equipped_items = equipment_set.get_equipped_items()
        total_stats = self.calculate_total_stats(equipment_set)
        completion_bonus = self.calculate_task_completion_bonus(equipment_set)
        
        # ストーリー
        slot_status = {}
        for slot in EquipmentSlot:
            item = equipment_set.get_item_by_slot(slot)
            slot_status[slot.value] = {
                "equipped": item is not None,
                "item_name": item.name if item else None,
                "item_rarity": item.rarity.value if item else None,
                "item_id": item.id if item else None
            }
        
        # レベル
        rarity_count = {}
        for item in equipped_items:
            rarity = item.rarity.value
            rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
        
        return {
            "total_equipped": len(equipped_items),
            "slot_status": slot_status,
            "total_stats": total_stats.to_dict(),
            "completion_bonus": {
                "base_efficiency": completion_bonus.base_efficiency,
                "total_bonus": completion_bonus.total_bonus,
                "bonus_percentage": f"{completion_bonus.total_bonus * 100:.1f}%",
                "active_effects": completion_bonus.active_effects
            },
            "rarity_distribution": rarity_count,
            "equipment_power": total_stats.get_total_bonus()
        }
    
    def recommend_equipment_upgrade(self, equipment_set: EquipmentSet, available_items: List[Item]) -> List[Dict]:
        """
        ?
        
        Args:
            equipment_set: ?
            available_items: ?
            
        Returns:
            List[Dict]: アプリ
        """
        recommendations = []
        current_stats = self.calculate_total_stats(equipment_set)
        current_bonus = self.calculate_task_completion_bonus(equipment_set)
        
        for item in available_items:
            # ?
            compatible_slots = []
            for slot, allowed_types in self.slot_item_types.items():
                if item.item_type in allowed_types:
                    compatible_slots.append(slot)
            
            for slot in compatible_slots:
                # ?
                temp_equipment = copy.deepcopy(equipment_set)
                current_item = temp_equipment.get_item_by_slot(slot)
                
                # ?
                temp_equipment.set_item_by_slot(slot, item)
                new_bonus = self.calculate_task_completion_bonus(temp_equipment)
                
                # ?
                improvement = new_bonus.total_bonus - current_bonus.total_bonus
                
                if improvement > 0:
                    recommendations.append({
                        "item": item,
                        "slot": slot.value,
                        "current_item": current_item,
                        "improvement": improvement,
                        "improvement_percentage": f"{improvement * 100:.1f}%",
                        "new_total_bonus": f"{new_bonus.total_bonus * 100:.1f}%",
                        "priority": self._calculate_upgrade_priority(improvement, item.rarity)
                    })
        
        # ?
        recommendations.sort(key=lambda x: x["improvement"], reverse=True)
        return recommendations[:10]  # ?10?
    
    def _calculate_upgrade_priority(self, improvement: float, rarity: ItemRarity) -> str:
        """アプリ"""
        rarity_weights = {
            ItemRarity.COMMON: 1,
            ItemRarity.UNCOMMON: 2,
            ItemRarity.RARE: 3,
            ItemRarity.EPIC: 4,
            ItemRarity.LEGENDARY: 5
        }
        
        score = improvement * 100 + rarity_weights[rarity]
        
        if score >= 15:
            return "high"
        elif score >= 8:
            return "medium"
        else:
            return "low"
    
    def validate_equipment_set(self, equipment_set: EquipmentSet) -> Tuple[bool, List[str]]:
        """
        ?
        
        Args:
            equipment_set: ?
            
        Returns:
            Tuple[bool, List[str]]: (?, エラー)
        """
        errors = []
        
        for slot in EquipmentSlot:
            item = equipment_set.get_item_by_slot(slot)
            if item:
                # アプリ
                allowed_types = self.slot_item_types[slot]
                if item.item_type not in allowed_types:
                    errors.append(f"{slot.value}ストーリー: {item.name}")
                
                # アプリ
                if not hasattr(item, 'stat_bonuses') or not isinstance(item.stat_bonuses, dict):
                    errors.append(f"アプリ {item.name} の")
                
                if not hasattr(item, 'special_effects') or not isinstance(item.special_effects, list):
                    errors.append(f"アプリ {item.name} の")
        
        return len(errors) == 0, errors
    
    def get_stat_breakdown(self, equipment_set: EquipmentSet) -> Dict:
        """
        ?
        
        Args:
            equipment_set: ?
            
        Returns:
            Dict: ?
        """
        breakdown = {
            "by_item": {},
            "by_stat": {stat.value: 0 for stat in StatType},
            "efficiency_contribution": {}
        }
        
        for slot in EquipmentSlot:
            item = equipment_set.get_item_by_slot(slot)
            if item:
                item_stats = EquipmentStats.from_dict(item.stat_bonuses)
                breakdown["by_item"][slot.value] = {
                    "item_name": item.name,
                    "stats": item_stats.to_dict()
                }
                
                # ?
                for stat in StatType:
                    stat_value = getattr(item_stats, stat.value)
                    breakdown["by_stat"][stat.value] += stat_value
        
        # ?
        for stat in StatType:
            stat_value = breakdown["by_stat"][stat.value]
            efficiency = stat_value * self.stat_efficiency_coefficients[stat]
            breakdown["efficiency_contribution"][stat.value] = {
                "stat_points": stat_value,
                "efficiency_bonus": efficiency,
                "percentage": f"{efficiency * 100:.2f}%"
            }
        
        return breakdown


if __name__ == "__main__":
    # 基本
    from gacha_system import GachaSystem
    
    # ?
    gacha = GachaSystem()
    result = gacha.perform_gacha("ten_pull", 10000)
    
    if result.success:
        equipment_system = EquipmentSystem()
        equipment_set = EquipmentSet()
        
        # アプリ
        equipped_count = 0
        for item in result.items:
            for slot in EquipmentSlot:
                if equipment_system.slot_item_types[slot] and item.item_type in equipment_system.slot_item_types[slot]:
                    if equipment_set.get_item_by_slot(slot) is None:
                        success, message = equipment_system.equip_item(equipment_set, item, slot)
                        if success:
                            print(f"?: {message}")
                            equipped_count += 1
                            break
        
        # ?
        summary = equipment_system.get_equipment_summary(equipment_set)
        print(f"\n?:")
        print(f"  ?: {summary['total_equipped']}")
        print(f"  ?: {summary['total_stats']}")
        print(f"  ?: {summary['completion_bonus']['bonus_percentage']}")
        print(f"  アプリ: {summary['completion_bonus']['active_effects']}")
        
        # ?
        breakdown = equipment_system.get_stat_breakdown(equipment_set)
        print(f"\n?:")
        for stat, contribution in breakdown["efficiency_contribution"].items():
            if contribution["stat_points"] > 0:
                print(f"  {stat}: {contribution['stat_points']}pt ? {contribution['percentage']}")
    else:
        print("?")