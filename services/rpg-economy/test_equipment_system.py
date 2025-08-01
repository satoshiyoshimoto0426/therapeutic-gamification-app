"""
?

6ストーリー6?
?
"""

import unittest
import sys
import os
from datetime import datetime

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from equipment_system import (
    EquipmentSystem, EquipmentSet, EquipmentSlot, StatType, EquipmentStats, TaskCompletionBonus
)
from gacha_system import GachaSystem, Item, ItemType, ItemRarity, TherapeuticTheme
from shared.utils.exceptions import ValidationError


class TestEquipmentSystem(unittest.TestCase):
    """?"""
    
    def setUp(self):
        """?"""
        self.equipment_system = EquipmentSystem()
        self.equipment_set = EquipmentSet()
        self.gacha_system = GachaSystem()
        
        # ?
        self.test_weapon = self._create_test_item(
            "?", ItemType.WEAPON, ItemRarity.RARE,
            {"focus": 5, "motivation": 3}, ["task_focus_boost"]
        )
        
        self.test_armor = self._create_test_item(
            "?", ItemType.ARMOR, ItemRarity.UNCOMMON,
            {"resilience": 4, "social": 2}, ["productivity_enhance"]
        )
        
        self.test_accessory = self._create_test_item(
            "?", ItemType.ACCESSORY, ItemRarity.EPIC,
            {"wisdom": 8, "creativity": 6}, ["deep_work_mode"]
        )
        
        self.test_consumable = self._create_test_item(
            "?", ItemType.CONSUMABLE, ItemRarity.COMMON,
            {"motivation": 2}, ["energy_boost"]
        )
    
    def _create_test_item(self, name: str, item_type: ItemType, rarity: ItemRarity,
                         stat_bonuses: dict, special_effects: list) -> Item:
        """?"""
        return Item(
            id=f"test_{name}",
            name=name,
            description=f"{name}の",
            rarity=rarity,
            item_type=item_type,
            therapeutic_theme=TherapeuticTheme.FOCUS,
            stat_bonuses=stat_bonuses,
            special_effects=special_effects,
            flavor_text=f"{name}の",
            created_at=datetime.now()
        )
    
    def test_equip_item_success(self):
        """アプリ"""
        success, message = self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        
        self.assertTrue(success)
        self.assertIn("?", message)
        self.assertEqual(self.equipment_set.weapon, self.test_weapon)
    
    def test_equip_item_replace(self):
        """アプリ"""
        # ?
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        
        # ?
        new_weapon = self._create_test_item(
            "?", ItemType.WEAPON, ItemRarity.LEGENDARY,
            {"focus": 10}, ["motivation_boost"]
        )
        
        success, message = self.equipment_system.equip_item(
            self.equipment_set, new_weapon, EquipmentSlot.WEAPON
        )
        
        self.assertTrue(success)
        self.assertIn("?", message)
        self.assertIn("?", message)
        self.assertEqual(self.equipment_set.weapon, new_weapon)
    
    def test_equip_item_wrong_type(self):
        """?"""
        success, message = self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.ARMOR
        )
        
        self.assertFalse(success)
        self.assertIn("?", message)
    
    def test_unequip_item_success(self):
        """アプリ"""
        # ま
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        
        # ?
        success, message = self.equipment_system.unequip_item(
            self.equipment_set, EquipmentSlot.WEAPON
        )
        
        self.assertTrue(success)
        self.assertIn("?", message)
        self.assertIsNone(self.equipment_set.weapon)
    
    def test_unequip_empty_slot(self):
        """?"""
        success, message = self.equipment_system.unequip_item(
            self.equipment_set, EquipmentSlot.WEAPON
        )
        
        self.assertFalse(success)
        self.assertIn("?", message)
    
    def test_calculate_total_stats(self):
        """?"""
        # ?
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        self.equipment_system.equip_item(
            self.equipment_set, self.test_armor, EquipmentSlot.ARMOR
        )
        self.equipment_system.equip_item(
            self.equipment_set, self.test_accessory, EquipmentSlot.ACCESSORY
        )
        
        total_stats = self.equipment_system.calculate_total_stats(self.equipment_set)
        
        # ?: weapon(focus:5, motivation:3) + armor(resilience:4, social:2) + accessory(wisdom:8, creativity:6)
        self.assertEqual(total_stats.focus, 5)
        self.assertEqual(total_stats.motivation, 3)
        self.assertEqual(total_stats.resilience, 4)
        self.assertEqual(total_stats.social, 2)
        self.assertEqual(total_stats.wisdom, 8)
        self.assertEqual(total_stats.creativity, 6)
    
    def test_calculate_task_completion_bonus(self):
        """タスク"""
        # アプリ
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        
        bonus = self.equipment_system.calculate_task_completion_bonus(self.equipment_set)
        
        self.assertIsInstance(bonus, TaskCompletionBonus)
        self.assertGreater(bonus.total_bonus, 0)
        self.assertGreater(bonus.focus_bonus, 0)
        self.assertIn("task_focus_boost", bonus.active_effects)
        
        # ? (focus:5 * 0.02 = 0.1)
        expected_focus_bonus = 5 * 0.02
        self.assertAlmostEqual(bonus.focus_bonus, expected_focus_bonus, places=3)
    
    def test_max_bonus_limit(self):
        """?"""
        # ?
        super_item = self._create_test_item(
            "?", ItemType.WEAPON, ItemRarity.LEGENDARY,
            {"focus": 100, "motivation": 100}, ["task_focus_boost", "motivation_boost", "deep_work_mode"]
        )
        
        self.equipment_system.equip_item(
            self.equipment_set, super_item, EquipmentSlot.WEAPON
        )
        
        bonus = self.equipment_system.calculate_task_completion_bonus(self.equipment_set)
        
        # ?50%?
        self.assertLessEqual(bonus.total_bonus, 0.5)
    
    def test_equipment_stats_operations(self):
        """EquipmentStats?"""
        stats1 = EquipmentStats(focus=5, motivation=3, resilience=2)
        stats2 = EquipmentStats(focus=2, wisdom=4, creativity=1)
        
        # ?
        result_add = stats1 + stats2
        self.assertEqual(result_add.focus, 7)
        self.assertEqual(result_add.motivation, 3)
        self.assertEqual(result_add.wisdom, 4)
        
        # ?
        result_sub = stats1 - stats2
        self.assertEqual(result_sub.focus, 3)
        self.assertEqual(result_sub.motivation, 3)
        self.assertEqual(result_sub.wisdom, -4)
        
        # ?
        stats_dict = stats1.to_dict()
        self.assertEqual(stats_dict["focus"], 5)
        self.assertEqual(stats_dict["motivation"], 3)
        
        # ?
        stats_from_dict = EquipmentStats.from_dict(stats_dict)
        self.assertEqual(stats_from_dict.focus, 5)
        self.assertEqual(stats_from_dict.motivation, 3)
    
    def test_equipment_summary(self):
        """?"""
        # ?
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        self.equipment_system.equip_item(
            self.equipment_set, self.test_armor, EquipmentSlot.ARMOR
        )
        
        summary = self.equipment_system.get_equipment_summary(self.equipment_set)
        
        self.assertEqual(summary["total_equipped"], 2)
        self.assertTrue(summary["slot_status"]["weapon"]["equipped"])
        self.assertTrue(summary["slot_status"]["armor"]["equipped"])
        self.assertFalse(summary["slot_status"]["accessory"]["equipped"])
        
        self.assertIn("total_stats", summary)
        self.assertIn("completion_bonus", summary)
        self.assertIn("rarity_distribution", summary)
        
        # レベル
        self.assertEqual(summary["rarity_distribution"]["rare"], 1)  # weapon
        self.assertEqual(summary["rarity_distribution"]["uncommon"], 1)  # armor
    
    def test_consumable_slots(self):
        """消"""
        consumable1 = self._create_test_item("?1", ItemType.CONSUMABLE, ItemRarity.COMMON, {"focus": 1}, [])
        consumable2 = self._create_test_item("?2", ItemType.CONSUMABLE, ItemRarity.COMMON, {"motivation": 1}, [])
        consumable3 = self._create_test_item("?3", ItemType.CONSUMABLE, ItemRarity.COMMON, {"resilience": 1}, [])
        
        # 3つ
        self.equipment_system.equip_item(self.equipment_set, consumable1, EquipmentSlot.CONSUMABLE_1)
        self.equipment_system.equip_item(self.equipment_set, consumable2, EquipmentSlot.CONSUMABLE_2)
        self.equipment_system.equip_item(self.equipment_set, consumable3, EquipmentSlot.CONSUMABLE_3)
        
        total_stats = self.equipment_system.calculate_total_stats(self.equipment_set)
        
        self.assertEqual(total_stats.focus, 1)
        self.assertEqual(total_stats.motivation, 1)
        self.assertEqual(total_stats.resilience, 1)
    
    def test_equipment_validation(self):
        """?"""
        # ?
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        
        valid, errors = self.equipment_system.validate_equipment_set(self.equipment_set)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
        
        # ?
        invalid_equipment = EquipmentSet()
        invalid_equipment.weapon = self.test_armor  # ?
        
        valid, errors = self.equipment_system.validate_equipment_set(invalid_equipment)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_stat_breakdown(self):
        """?"""
        self.equipment_system.equip_item(
            self.equipment_set, self.test_weapon, EquipmentSlot.WEAPON
        )
        self.equipment_system.equip_item(
            self.equipment_set, self.test_accessory, EquipmentSlot.ACCESSORY
        )
        
        breakdown = self.equipment_system.get_stat_breakdown(self.equipment_set)
        
        self.assertIn("by_item", breakdown)
        self.assertIn("by_stat", breakdown)
        self.assertIn("efficiency_contribution", breakdown)
        
        # アプリ
        self.assertIn("weapon", breakdown["by_item"])
        self.assertIn("accessory", breakdown["by_item"])
        
        # ?
        self.assertEqual(breakdown["by_stat"]["focus"], 5)  # weaponか
        self.assertEqual(breakdown["by_stat"]["wisdom"], 8)  # accessoryか
        self.assertEqual(breakdown["by_stat"]["creativity"], 6)  # accessoryか
        
        # ?
        focus_contribution = breakdown["efficiency_contribution"]["focus"]
        self.assertEqual(focus_contribution["stat_points"], 5)
        self.assertAlmostEqual(focus_contribution["efficiency_bonus"], 5 * 0.02, places=3)


class TestEquipmentSystemIntegration(unittest.TestCase):
    """?"""
    
    def setUp(self):
        """?"""
        self.equipment_system = EquipmentSystem()
        self.gacha_system = GachaSystem()
    
    def test_gacha_to_equipment_workflow(self):
        """?"""
        # ?
        gacha_result = self.gacha_system.perform_gacha("ten_pull", 10000)
        self.assertTrue(gacha_result.success)
        
        equipment_set = EquipmentSet()
        equipped_items = []
        
        # ?
        for item in gacha_result.items:
            for slot in EquipmentSlot:
                allowed_types = self.equipment_system.slot_item_types[slot]
                if item.item_type in allowed_types and equipment_set.get_item_by_slot(slot) is None:
                    success, message = self.equipment_system.equip_item(equipment_set, item, slot)
                    if success:
                        equipped_items.append(item)
                        break
        
        # ?
        summary = self.equipment_system.get_equipment_summary(equipment_set)
        
        self.assertGreater(summary["total_equipped"], 0)
        self.assertGreaterEqual(summary["completion_bonus"]["total_bonus"], 0)
        
        print(f"?:")
        print(f"  ?: {len(gacha_result.items)}")
        print(f"  ?: {summary['total_equipped']}")
        print(f"  ?: {summary['completion_bonus']['bonus_percentage']}")
    
    def test_equipment_upgrade_recommendations(self):
        """?"""
        # ?
        equipment_set = EquipmentSet()
        
        # ?
        low_weapon = self._create_test_item(
            "?", ItemType.WEAPON, ItemRarity.COMMON,
            {"focus": 1}, []
        )
        self.equipment_system.equip_item(equipment_set, low_weapon, EquipmentSlot.WEAPON)
        
        # ?
        available_items = [
            self._create_test_item(
                "?", ItemType.WEAPON, ItemRarity.RARE,
                {"focus": 6, "motivation": 4}, ["task_focus_boost"]
            ),
            self._create_test_item(
                "?", ItemType.WEAPON, ItemRarity.LEGENDARY,
                {"focus": 15, "motivation": 10}, ["deep_work_mode", "motivation_boost"]
            ),
            self._create_test_item(
                "?", ItemType.ARMOR, ItemRarity.EPIC,
                {"resilience": 8, "social": 5}, ["productivity_enhance"]
            )
        ]
        
        recommendations = self.equipment_system.recommend_equipment_upgrade(
            equipment_set, available_items
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # ?LEGENDARYアプリ
        best_recommendation = recommendations[0]
        self.assertEqual(best_recommendation["item"].rarity, ItemRarity.LEGENDARY)
        self.assertGreater(best_recommendation["improvement"], 0)
        
        print(f"アプリ:")
        for i, rec in enumerate(recommendations[:3]):
            print(f"  {i+1}. {rec['item'].name} ({rec['item'].rarity.value})")
            print(f"     ?: {rec['improvement_percentage']}")
            print(f"     ?: {rec['priority']}")
    
    def _create_test_item(self, name: str, item_type: ItemType, rarity: ItemRarity,
                         stat_bonuses: dict, special_effects: list) -> Item:
        """?"""
        return Item(
            id=f"test_{name}",
            name=name,
            description=f"{name}の",
            rarity=rarity,
            item_type=item_type,
            therapeutic_theme=TherapeuticTheme.FOCUS,
            stat_bonuses=stat_bonuses,
            special_effects=special_effects,
            flavor_text=f"{name}の",
            created_at=datetime.now()
        )
    
    def test_full_equipment_optimization(self):
        """?"""
        # ?
        all_items = []
        for _ in range(50):
            gacha_result = self.gacha_system.perform_gacha("single", 10000)
            if gacha_result.success:
                all_items.extend(gacha_result.items)
        
        equipment_set = EquipmentSet()
        
        # ?
        for slot in EquipmentSlot:
            allowed_types = self.equipment_system.slot_item_types[slot]
            compatible_items = [item for item in all_items if item.item_type in allowed_types]
            
            if compatible_items:
                # ?
                best_item = max(compatible_items, 
                              key=lambda x: sum(x.stat_bonuses.values()))
                self.equipment_system.equip_item(equipment_set, best_item, slot)
        
        # ?
        summary = self.equipment_system.get_equipment_summary(equipment_set)
        breakdown = self.equipment_system.get_stat_breakdown(equipment_set)
        
        self.assertEqual(summary["total_equipped"], 6)  # ?
        self.assertGreater(summary["equipment_power"], 0)
        
        print(f"?:")
        print(f"  ?: {summary['equipment_power']}")
        print(f"  ?: {summary['completion_bonus']['bonus_percentage']}")
        print(f"  アプリ: {len(summary['completion_bonus']['active_effects'])}")
        
        # ?
        print(f"  ?:")
        for stat, contribution in breakdown["efficiency_contribution"].items():
            if contribution["stat_points"] > 0:
                print(f"    {stat}: {contribution['stat_points']}pt ? {contribution['percentage']}")


if __name__ == "__main__":
    # ?
    unittest.main(verbosity=2)