using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Items
{
    /// <summary>
    /// 装備品クラス
    /// </summary>
    [System.Serializable]
    public class Equipment : Item
    {
        [Header("Equipment Properties")]
        public EquipmentType equipmentType;
        public EquipmentSlot equipmentSlot;

        [Header("Stats Bonus")]
        public int attackBonus;
        public int defenseBonus;
        public int speedBonus;
        public int hpBonus;

        [Header("Special Effects")]
        public List<EquipmentEffect> specialEffects = new List<EquipmentEffect>();

        [Header("Requirements")]
        public int requiredLevel = 1;

        public Equipment()
        {
            itemType = ItemType.Equipment;
        }

        /// <summary>
        /// 装備を装着
        /// </summary>
        public override bool Use(Character.Player player)
        {
            if (player == null) return false;

            // レベル要件チェック
            if (player.stats.Level < requiredLevel)
            {
                Debug.LogWarning($"[Equipment] レベル不足: Lv.{requiredLevel} 必要");
                return false;
            }

            // 装備マネージャーに装備を依頼
            EquipmentManager equipManager = Object.FindObjectOfType<EquipmentManager>();
            if (equipManager != null)
            {
                return equipManager.EquipItem(this);
            }

            return false;
        }

        /// <summary>
        /// 装備の詳細情報を取得
        /// </summary>
        public override string GetDetailedInfo()
        {
            string baseInfo = base.GetDetailedInfo();
            string statsText = GetStatsText();
            string effectsText = GetEffectsText();
            string reqText = $"\n必要レベル: {requiredLevel}";

            return $"{baseInfo}\n\n{statsText}{effectsText}{reqText}";
        }

        /// <summary>
        /// ステータスボーナスのテキスト
        /// </summary>
        private string GetStatsText()
        {
            List<string> stats = new List<string>();

            if (attackBonus > 0) stats.Add($"攻撃力 +{attackBonus}");
            if (defenseBonus > 0) stats.Add($"防御力 +{defenseBonus}");
            if (speedBonus > 0) stats.Add($"素早さ +{speedBonus}");
            if (hpBonus > 0) stats.Add($"最大HP +{hpBonus}");

            if (stats.Count > 0)
            {
                return string.Join("\n", stats);
            }

            return "";
        }

        /// <summary>
        /// 特殊効果のテキスト
        /// </summary>
        private string GetEffectsText()
        {
            if (specialEffects.Count == 0) return "";

            List<string> effects = new List<string>();
            foreach (var effect in specialEffects)
            {
                effects.Add($"• {effect.effectName}");
            }

            return "\n\n特殊効果:\n" + string.Join("\n", effects);
        }

        /// <summary>
        /// 装備のカテゴリ名を取得
        /// </summary>
        public string GetCategoryName()
        {
            switch (equipmentType)
            {
                case EquipmentType.Weapon: return "武器";
                case EquipmentType.Armor: return "防具";
                case EquipmentType.Shield: return "盾";
                case EquipmentType.Accessory: return "アクセサリー";
                case EquipmentType.Charm: return "お守り";
                default: return "装備";
            }
        }
    }

    /// <summary>
    /// 装備の種類
    /// </summary>
    public enum EquipmentType
    {
        Weapon,      // 武器
        Armor,       // 防具
        Shield,      // 盾
        Accessory,   // アクセサリー
        Charm        // お守り
    }

    /// <summary>
    /// 装備スロット
    /// </summary>
    public enum EquipmentSlot
    {
        Weapon,      // 武器スロット
        Head,        // 頭
        Body,        // 体
        Legs,        // 脚
        Accessory1,  // アクセサリー1
        Accessory2,  // アクセサリー2
        Charm        // お守り
    }

    /// <summary>
    /// 装備の特殊効果
    /// </summary>
    [System.Serializable]
    public class EquipmentEffect
    {
        public string effectId;
        public string effectName;
        public string description;
        public EffectType effectType;
        public float value;

        public EquipmentEffect(string name, string desc, EffectType type, float val)
        {
            effectId = System.Guid.NewGuid().ToString();
            effectName = name;
            description = desc;
            effectType = type;
            value = val;
        }
    }

    /// <summary>
    /// 効果の種類
    /// </summary>
    public enum EffectType
    {
        CriticalChance,      // クリティカル率上昇
        DodgeChance,         // 回避率上昇
        HPRegen,             // HP自動回復
        ExpBoost,            // 経験値獲得量増加
        GoldBoost,           // ゴールド獲得量増加
        PoisonResist,        // 毒耐性
        TrapResist,          // トラップ耐性
        FireResist,          // 炎耐性
        IceResist,           // 氷耐性
        Lifesteal,           // ライフスティール
        AreaDamage,          // 範囲攻撃
        DoubleAttack,        // 二回攻撃
        CounterAttack,       // 反撃
        TaskEfficiency       // タスク効率アップ（独自）
    }

    /// <summary>
    /// 装備プリセット（初期データ用）
    /// </summary>
    public static class EquipmentPresets
    {
        /// <summary>
        /// 初期装備を生成
        /// </summary>
        public static Equipment CreateStarterWeapon()
        {
            Equipment weapon = new Equipment
            {
                itemName = "木の剣",
                description = "初心者向けの木製の剣。頼りないが、ないよりはマシ。",
                equipmentType = EquipmentType.Weapon,
                equipmentSlot = EquipmentSlot.Weapon,
                rarity = Rarity.Normal,
                attackBonus = 5,
                buyPrice = 50,
                sellPrice = 10,
                requiredLevel = 1
            };

            return weapon;
        }

        /// <summary>
        /// ランダムな武器を生成
        /// </summary>
        public static Equipment CreateRandomWeapon(int level, Rarity rarity)
        {
            Equipment weapon = new Equipment
            {
                equipmentType = EquipmentType.Weapon,
                equipmentSlot = EquipmentSlot.Weapon,
                rarity = rarity,
                requiredLevel = Mathf.Max(1, level - 2)
            };

            // レアリティに応じたステータス
            float rarityMultiplier = GetRarityMultiplier(rarity);
            weapon.attackBonus = Mathf.RoundToInt(level * 2 * rarityMultiplier);
            weapon.buyPrice = Mathf.RoundToInt(level * 50 * rarityMultiplier);
            weapon.sellPrice = weapon.buyPrice / 5;

            // 武器名を生成
            weapon.itemName = GenerateWeaponName(rarity);
            weapon.description = "強力な武器。敵を倒すのに役立つ。";

            // レアリティに応じて特殊効果を追加
            if (rarity >= Rarity.Rare)
            {
                weapon.specialEffects.Add(new EquipmentEffect(
                    "クリティカル",
                    "クリティカル率が上昇する",
                    EffectType.CriticalChance,
                    0.1f
                ));
            }

            if (rarity >= Rarity.SuperRare)
            {
                weapon.specialEffects.Add(new EquipmentEffect(
                    "経験値ブースト",
                    "獲得経験値が10%増加する",
                    EffectType.ExpBoost,
                    0.1f
                ));
            }

            if (rarity == Rarity.Legendary)
            {
                weapon.specialEffects.Add(new EquipmentEffect(
                    "二回攻撃",
                    "通常攻撃が2回発動する",
                    EffectType.DoubleAttack,
                    1f
                ));
            }

            return weapon;
        }

        /// <summary>
        /// ランダムな防具を生成
        /// </summary>
        public static Equipment CreateRandomArmor(int level, Rarity rarity)
        {
            Equipment armor = new Equipment
            {
                equipmentType = EquipmentType.Armor,
                equipmentSlot = EquipmentSlot.Body,
                rarity = rarity,
                requiredLevel = Mathf.Max(1, level - 2)
            };

            float rarityMultiplier = GetRarityMultiplier(rarity);
            armor.defenseBonus = Mathf.RoundToInt(level * 1.5f * rarityMultiplier);
            armor.hpBonus = Mathf.RoundToInt(level * 5 * rarityMultiplier);
            armor.buyPrice = Mathf.RoundToInt(level * 60 * rarityMultiplier);
            armor.sellPrice = armor.buyPrice / 5;

            armor.itemName = GenerateArmorName(rarity);
            armor.description = "身を守る防具。HP上昇効果もある。";

            if (rarity >= Rarity.Rare)
            {
                armor.specialEffects.Add(new EquipmentEffect(
                    "HP自動回復",
                    "毎ターンHPが少し回復する",
                    EffectType.HPRegen,
                    1f
                ));
            }

            if (rarity >= Rarity.SuperRare)
            {
                armor.specialEffects.Add(new EquipmentEffect(
                    "毒耐性",
                    "毒状態になりにくい",
                    EffectType.PoisonResist,
                    0.5f
                ));
            }

            return armor;
        }

        /// <summary>
        /// レアリティの倍率を取得
        /// </summary>
        private static float GetRarityMultiplier(Rarity rarity)
        {
            switch (rarity)
            {
                case Rarity.Normal: return 1.0f;
                case Rarity.Rare: return 1.5f;
                case Rarity.SuperRare: return 2.0f;
                case Rarity.Legendary: return 3.0f;
                default: return 1.0f;
            }
        }

        /// <summary>
        /// 武器名を生成
        /// </summary>
        private static string GenerateWeaponName(Rarity rarity)
        {
            string[] prefixes = { "勇気の", "希望の", "決意の", "成長の", "挑戦の" };
            string[] suffixes = { "剣", "槍", "斧", "杖", "弓" };

            string prefix = rarity >= Rarity.Rare ? prefixes[Random.Range(0, prefixes.Length)] : "";
            string suffix = suffixes[Random.Range(0, suffixes.Length)];

            return prefix + suffix;
        }

        /// <summary>
        /// 防具名を生成
        /// </summary>
        private static string GenerateArmorName(Rarity rarity)
        {
            string[] prefixes = { "守護の", "不屈の", "信念の", "忍耐の", "継続の" };
            string[] suffixes = { "鎧", "ローブ", "服", "コート", "マント" };

            string prefix = rarity >= Rarity.Rare ? prefixes[Random.Range(0, prefixes.Length)] : "";
            string suffix = suffixes[Random.Range(0, suffixes.Length)];

            return prefix + suffix;
        }
    }
}
