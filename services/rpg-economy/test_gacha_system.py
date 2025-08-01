"""
?

5?
アプリ
"""

import unittest
import sys
import os
from datetime import datetime
from collections import Counter

# ?
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from gacha_system import (
    GachaSystem, ItemRarity, ItemType, TherapeuticTheme, Item, GachaResult
)
from shared.utils.exceptions import ValidationError


class TestGachaSystem(unittest.TestCase):
    """?"""
    
    def setUp(self):
        """?"""
        self.gacha = GachaSystem()
    
    def test_single_gacha_success(self):
        """?"""
        result = self.gacha.perform_gacha("single", 1000)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.coins_spent, 100)
        self.assertEqual(result.gacha_type, "single")
        self.assertFalse(result.guaranteed_rare)
        self.assertIsNone(result.error_message)
        
        # アプリ
        item = result.items[0]
        self.assertIsInstance(item, Item)
        self.assertIsInstance(item.rarity, ItemRarity)
        self.assertIsInstance(item.item_type, ItemType)
        self.assertIsInstance(item.therapeutic_theme, TherapeuticTheme)
        self.assertIsInstance(item.stat_bonuses, dict)
        self.assertIsInstance(item.special_effects, list)
    
    def test_ten_pull_gacha_success(self):
        """10?"""
        result = self.gacha.perform_gacha("ten_pull", 1000)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.items), 10)
        self.assertEqual(result.coins_spent, 900)
        self.assertEqual(result.gacha_type, "ten_pull")
        self.assertIsNone(result.error_message)
        
        # ?
        for item in result.items:
            self.assertIsInstance(item, Item)
            self.assertTrue(len(item.name) > 0)
            self.assertTrue(len(item.description) > 0)
            self.assertTrue(len(item.stat_bonuses) > 0)
    
    def test_premium_gacha_success(self):
        """プレビュー"""
        result = self.gacha.perform_gacha("premium", 1000)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.coins_spent, 300)
        self.assertEqual(result.gacha_type, "premium")
        self.assertFalse(result.guaranteed_rare)
        self.assertIsNone(result.error_message)
    
    def test_insufficient_coins_error(self):
        """コア"""
        result = self.gacha.perform_gacha("single", 50)  # 100コア50し
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.coins_spent, 0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("コア", result.error_message)
    
    def test_invalid_gacha_type_error(self):
        """無"""
        result = self.gacha.perform_gacha("invalid_type", 1000)
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.coins_spent, 0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("無", result.error_message)
    
    def test_rarity_distribution(self):
        """レベル"""
        # ?
        results = []
        for _ in range(1000):  # 1000?
            result = self.gacha.perform_gacha("single", 100000)
            if result.success:
                results.extend(result.items)
        
        # レベル
        rarity_counts = Counter(item.rarity for item in results)
        total = len(results)
        
        # ?5%?
        expected_rates = {
            ItemRarity.COMMON: 0.60,
            ItemRarity.UNCOMMON: 0.25,
            ItemRarity.RARE: 0.10,
            ItemRarity.EPIC: 0.04,
            ItemRarity.LEGENDARY: 0.01
        }
        
        for rarity, expected_rate in expected_rates.items():
            actual_rate = rarity_counts[rarity] / total
            self.assertAlmostEqual(actual_rate, expected_rate, delta=0.05,
                                 msg=f"{rarity.value}の")
    
    def test_ten_pull_guaranteed_rare(self):
        """10?"""
        # レベル
        # 実装
        # ?
        
        guaranteed_count = 0
        total_tests = 100
        
        for _ in range(total_tests):
            result = self.gacha.perform_gacha("ten_pull", 100000)
            if result.success:
                # レベル
                has_rare_or_better = any(
                    item.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]
                    for item in result.items
                )
                self.assertTrue(has_rare_or_better, "10?1つ")
                
                if result.guaranteed_rare:
                    guaranteed_count += 1
        
        # ?
        # ?
        print(f"10?: {guaranteed_count}/{total_tests} ({guaranteed_count/total_tests*100:.1f}%)")
    
    def test_premium_gacha_enhanced_rates(self):
        """プレビュー"""
        # ?
        normal_results = []
        premium_results = []
        
        # ?500?
        for _ in range(500):
            normal_result = self.gacha.perform_gacha("single", 100000)
            premium_result = self.gacha.perform_gacha("premium", 100000)
            
            if normal_result.success:
                normal_results.extend(normal_result.items)
            if premium_result.success:
                premium_results.extend(premium_result.items)
        
        # レベル
        normal_rare_count = sum(1 for item in normal_results 
                               if item.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY])
        premium_rare_count = sum(1 for item in premium_results 
                                if item.rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY])
        
        normal_rare_rate = normal_rare_count / len(normal_results)
        premium_rare_rate = premium_rare_count / len(premium_results)
        
        # プレビュー
        self.assertGreater(premium_rare_rate, normal_rare_rate,
                          "プレビュー")
        
        print(f"?: {normal_rare_rate:.3f}")
        print(f"プレビュー: {premium_rare_rate:.3f}")
    
    def test_item_generation_therapeutic_themes(self):
        """治療"""
        # ?
        theme_counts = Counter()
        
        for _ in range(100):
            result = self.gacha.perform_gacha("single", 100000)
            if result.success:
                theme_counts[result.items[0].therapeutic_theme] += 1
        
        # ?
        for theme in TherapeuticTheme:
            self.assertGreater(theme_counts[theme], 0, 
                             f"治療 {theme.value} の")
    
    def test_stat_bonuses_by_rarity(self):
        """レベル"""
        # ?
        rarity_stats = {}
        
        for rarity in ItemRarity:
            # ?
            item = self.gacha._generate_item(rarity)
            rarity_stats[rarity] = sum(item.stat_bonuses.values())
        
        # レベル
        self.assertLess(rarity_stats[ItemRarity.COMMON], rarity_stats[ItemRarity.UNCOMMON])
        self.assertLess(rarity_stats[ItemRarity.UNCOMMON], rarity_stats[ItemRarity.RARE])
        self.assertLess(rarity_stats[ItemRarity.RARE], rarity_stats[ItemRarity.EPIC])
        self.assertLess(rarity_stats[ItemRarity.EPIC], rarity_stats[ItemRarity.LEGENDARY])
    
    def test_item_naming_and_description(self):
        """アプリ"""
        result = self.gacha.perform_gacha("ten_pull", 100000)
        self.assertTrue(result.success)
        
        for item in result.items:
            # ?
            self.assertTrue(len(item.name.strip()) > 0)
            self.assertTrue(len(item.description.strip()) > 0)
            self.assertTrue(len(item.flavor_text.strip()) > 0)
            
            # レベル
            if item.rarity != ItemRarity.COMMON:
                # COMMONで
                rarity_prefixes = ["?", "希", "?", "?"]
                has_prefix = any(prefix in item.name for prefix in rarity_prefixes)
                # ?
                if not has_prefix:
                    print(f"?: {item.rarity.value}アプリ '{item.name}' に")
    
    def test_special_effects_generation(self):
        """?"""
        result = self.gacha.perform_gacha("ten_pull", 100000)
        self.assertTrue(result.success)
        
        for item in result.items:
            # ?
            self.assertIsInstance(item.special_effects, list)
            self.assertGreater(len(item.special_effects), 0)
            
            # ?
            for effect in item.special_effects:
                self.assertIsInstance(effect, str)
                self.assertTrue(len(effect.strip()) > 0)
    
    def test_gacha_rates_info(self):
        """?"""
        # ?
        for gacha_type in ["single", "ten_pull", "premium"]:
            rates = self.gacha.get_gacha_rates(gacha_type)
            
            self.assertEqual(rates["gacha_type"], gacha_type)
            self.assertIn("cost", rates)
            self.assertIn("rates", rates)
            self.assertIn("guaranteed_rare", rates)
            self.assertIn("premium_bonus", rates)
            
            # ?100%で
            total_rate = sum(float(rate.rstrip('%')) for rate in rates["rates"].values())
            self.assertAlmostEqual(total_rate, 100.0, delta=0.1)
    
    def test_invalid_gacha_rates_request(self):
        """無"""
        with self.assertRaises(ValidationError):
            self.gacha.get_gacha_rates("invalid_type")
    
    def test_item_statistics(self):
        """アプリ"""
        result = self.gacha.perform_gacha("ten_pull", 100000)
        self.assertTrue(result.success)
        
        stats = self.gacha.get_item_statistics(result.items)
        
        self.assertEqual(stats["total"], 10)
        self.assertIn("by_rarity", stats)
        self.assertIn("by_theme", stats)
        self.assertIn("by_type", stats)
        self.assertIn("average_stats", stats)
        
        # レベル
        rarity_total = sum(stats["by_rarity"].values())
        self.assertEqual(rarity_total, 10)
        
        # ?
        for stat_name, avg_value in stats["average_stats"].items():
            self.assertIsInstance(avg_value, (int, float))
            self.assertGreaterEqual(avg_value, 0)
    
    def test_empty_item_statistics(self):
        """?"""
        stats = self.gacha.get_item_statistics([])
        
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["by_rarity"], {})
        self.assertEqual(stats["by_theme"], {})
        self.assertEqual(stats["by_type"], {})


class TestGachaSystemIntegration(unittest.TestCase):
    """?"""
    
    def setUp(self):
        """?"""
        self.gacha = GachaSystem()
    
    def test_complete_gacha_workflow(self):
        """?"""
        user_coins = 10000
        gacha_history = []
        
        # 1. ?
        for _ in range(5):
            result = self.gacha.perform_gacha("single", user_coins)
            self.assertTrue(result.success)
            user_coins -= result.coins_spent
            gacha_history.extend(result.items)
        
        # 2. 10?
        result_10 = self.gacha.perform_gacha("ten_pull", user_coins)
        self.assertTrue(result_10.success)
        user_coins -= result_10.coins_spent
        gacha_history.extend(result_10.items)
        
        # 3. プレビュー
        result_premium = self.gacha.perform_gacha("premium", user_coins)
        self.assertTrue(result_premium.success)
        user_coins -= result_premium.coins_spent
        gacha_history.extend(result_premium.items)
        
        # 4. ?
        stats = self.gacha.get_item_statistics(gacha_history)
        
        self.assertEqual(stats["total"], 16)  # 5 + 10 + 1
        self.assertGreater(len(stats["by_rarity"]), 0)
        self.assertGreater(len(stats["by_theme"]), 0)
        
        print(f"?:")
        print(f"  ?: {stats['total']}")
        print(f"  ?: {user_coins}")
        print(f"  レベル: {stats['by_rarity']}")
        print(f"  ?: {stats['by_theme']}")
    
    def test_therapeutic_theme_balance(self):
        """治療"""
        # ?
        all_items = []
        
        for _ in range(100):
            result = self.gacha.perform_gacha("ten_pull", 100000)
            if result.success:
                all_items.extend(result.items)
        
        stats = self.gacha.get_item_statistics(all_items)
        theme_distribution = stats["by_theme"]
        
        # ?
        total_items = len(all_items)
        expected_rate_per_theme = 1.0 / len(TherapeuticTheme)
        
        for theme in TherapeuticTheme:
            theme_count = theme_distribution.get(theme.value, 0)
            actual_rate = theme_count / total_items
            
            # ?30%?
            self.assertAlmostEqual(actual_rate, expected_rate_per_theme, delta=0.3,
                                 msg=f"治療 {theme.value} の")
        
        print(f"治療:")
        for theme, count in theme_distribution.items():
            rate = count / total_items * 100
            print(f"  {theme}: {count} ({rate:.1f}%)")
    
    def test_rarity_stat_correlation(self):
        """レベル"""
        # ?
        rarity_stats = {rarity: [] for rarity in ItemRarity}
        
        for _ in range(200):
            for rarity in ItemRarity:
                item = self.gacha._generate_item(rarity)
                total_stats = sum(item.stat_bonuses.values())
                rarity_stats[rarity].append(total_stats)
        
        # ?
        avg_stats = {}
        for rarity, stats_list in rarity_stats.items():
            avg_stats[rarity] = sum(stats_list) / len(stats_list)
        
        # レベル
        rarities = [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, 
                   ItemRarity.EPIC, ItemRarity.LEGENDARY]
        
        for i in range(len(rarities) - 1):
            current_rarity = rarities[i]
            next_rarity = rarities[i + 1]
            
            self.assertLess(avg_stats[current_rarity], avg_stats[next_rarity],
                           f"{current_rarity.value}の{next_rarity.value}?")
        
        print(f"レベル:")
        for rarity in rarities:
            print(f"  {rarity.value}: {avg_stats[rarity]:.2f}")


if __name__ == "__main__":
    # ?
    unittest.main(verbosity=2)