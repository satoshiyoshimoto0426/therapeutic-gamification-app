using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Items
{
    /// <summary>
    /// 装備管理システム
    /// プレイヤーの現在の装備を管理
    /// </summary>
    public class EquipmentManager : MonoBehaviour
    {
        public static EquipmentManager Instance { get; private set; }

        [Header("Equipment Slots")]
        public Dictionary<EquipmentSlot, Equipment> equippedItems = new Dictionary<EquipmentSlot, Equipment>();

        [Header("Events")]
        public System.Action OnEquipmentChanged;

        private Character.Player player;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }

            InitializeEquipmentSlots();
        }

        private void Start()
        {
            player = FindObjectOfType<Character.Player>();
        }

        /// <summary>
        /// 装備スロットを初期化
        /// </summary>
        private void InitializeEquipmentSlots()
        {
            equippedItems.Clear();

            // すべてのスロットをnullで初期化
            foreach (EquipmentSlot slot in System.Enum.GetValues(typeof(EquipmentSlot)))
            {
                equippedItems[slot] = null;
            }

            Debug.Log("[EquipmentManager] Equipment slots initialized");
        }

        /// <summary>
        /// 装備を装着
        /// </summary>
        public bool EquipItem(Equipment equipment)
        {
            if (equipment == null) return false;
            if (player == null)
            {
                player = FindObjectOfType<Character.Player>();
                if (player == null)
                {
                    Debug.LogError("[EquipmentManager] Player not found");
                    return false;
                }
            }

            // レベル要件チェック
            if (player.stats.Level < equipment.requiredLevel)
            {
                Debug.LogWarning($"[EquipmentManager] Level requirement not met: {equipment.requiredLevel}");
                return false;
            }

            EquipmentSlot slot = equipment.equipmentSlot;

            // 既存の装備があれば外す
            if (equippedItems[slot] != null)
            {
                UnequipItem(slot);
            }

            // 装備を装着
            equippedItems[slot] = equipment;
            ApplyEquipmentStats(equipment, true);

            Debug.Log($"[EquipmentManager] Equipped {equipment.itemName} to {slot}");
            OnEquipmentChanged?.Invoke();

            return true;
        }

        /// <summary>
        /// 装備を外す
        /// </summary>
        public Equipment UnequipItem(EquipmentSlot slot)
        {
            if (!equippedItems.ContainsKey(slot) || equippedItems[slot] == null)
            {
                Debug.LogWarning($"[EquipmentManager] No equipment in slot: {slot}");
                return null;
            }

            Equipment equipment = equippedItems[slot];
            equippedItems[slot] = null;

            // ステータスボーナスを削除
            ApplyEquipmentStats(equipment, false);

            // インベントリに戻す
            if (Inventory.Instance != null)
            {
                Inventory.Instance.AddItem(equipment);
            }

            Debug.Log($"[EquipmentManager] Unequipped {equipment.itemName} from {slot}");
            OnEquipmentChanged?.Invoke();

            return equipment;
        }

        /// <summary>
        /// 装備のステータスボーナスを適用/削除
        /// </summary>
        private void ApplyEquipmentStats(Equipment equipment, bool apply)
        {
            if (player == null) return;

            int multiplier = apply ? 1 : -1;

            player.stats.Attack += equipment.attackBonus * multiplier;
            player.stats.Defense += equipment.defenseBonus * multiplier;
            player.stats.Speed += equipment.speedBonus * multiplier;
            player.stats.MaxHP += equipment.hpBonus * multiplier;

            // HP上限が増えた場合、現在HPも回復
            if (apply && equipment.hpBonus > 0)
            {
                player.stats.CurrentHP += equipment.hpBonus;
            }

            // HP上限が減った場合、現在HPも減らす（最低1）
            if (!apply && equipment.hpBonus > 0)
            {
                player.stats.CurrentHP = Mathf.Max(1, player.stats.CurrentHP - equipment.hpBonus);
            }

            Debug.Log($"[EquipmentManager] {(apply ? "Applied" : "Removed")} stats from {equipment.itemName}");
        }

        /// <summary>
        /// 指定スロットの装備を取得
        /// </summary>
        public Equipment GetEquippedItem(EquipmentSlot slot)
        {
            if (equippedItems.ContainsKey(slot))
            {
                return equippedItems[slot];
            }
            return null;
        }

        /// <summary>
        /// すべての装備を取得
        /// </summary>
        public List<Equipment> GetAllEquippedItems()
        {
            List<Equipment> equipped = new List<Equipment>();

            foreach (var kvp in equippedItems)
            {
                if (kvp.Value != null)
                {
                    equipped.Add(kvp.Value);
                }
            }

            return equipped;
        }

        /// <summary>
        /// 特定のスロットが装備されているかチェック
        /// </summary>
        public bool IsSlotEquipped(EquipmentSlot slot)
        {
            return equippedItems.ContainsKey(slot) && equippedItems[slot] != null;
        }

        /// <summary>
        /// すべての装備を外す
        /// </summary>
        public void UnequipAll()
        {
            foreach (EquipmentSlot slot in System.Enum.GetValues(typeof(EquipmentSlot)))
            {
                if (IsSlotEquipped(slot))
                {
                    UnequipItem(slot);
                }
            }

            Debug.Log("[EquipmentManager] All equipment unequipped");
        }

        /// <summary>
        /// 装備の総ボーナスを計算
        /// </summary>
        public EquipmentBonusTotal GetTotalBonus()
        {
            EquipmentBonusTotal total = new EquipmentBonusTotal();

            foreach (var equipment in equippedItems.Values)
            {
                if (equipment != null)
                {
                    total.attackBonus += equipment.attackBonus;
                    total.defenseBonus += equipment.defenseBonus;
                    total.speedBonus += equipment.speedBonus;
                    total.hpBonus += equipment.hpBonus;
                }
            }

            return total;
        }

        /// <summary>
        /// すべての特殊効果を取得
        /// </summary>
        public List<EquipmentEffect> GetAllActiveEffects()
        {
            List<EquipmentEffect> effects = new List<EquipmentEffect>();

            foreach (var equipment in equippedItems.Values)
            {
                if (equipment != null && equipment.specialEffects != null)
                {
                    effects.AddRange(equipment.specialEffects);
                }
            }

            return effects;
        }

        /// <summary>
        /// 特定の効果を持っているかチェック
        /// </summary>
        public bool HasEffect(EffectType effectType)
        {
            foreach (var equipment in equippedItems.Values)
            {
                if (equipment != null && equipment.specialEffects != null)
                {
                    foreach (var effect in equipment.specialEffects)
                    {
                        if (effect.effectType == effectType)
                        {
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        /// <summary>
        /// 特定の効果の値を取得
        /// </summary>
        public float GetEffectValue(EffectType effectType)
        {
            float totalValue = 0f;

            foreach (var equipment in equippedItems.Values)
            {
                if (equipment != null && equipment.specialEffects != null)
                {
                    foreach (var effect in equipment.specialEffects)
                    {
                        if (effect.effectType == effectType)
                        {
                            totalValue += effect.value;
                        }
                    }
                }
            }

            return totalValue;
        }

        /// <summary>
        /// 装備セットボーナスをチェック（将来実装用）
        /// </summary>
        public bool HasSetBonus(string setName)
        {
            // TODO: 装備セット効果の実装
            return false;
        }

        /// <summary>
        /// 装備の状態を文字列で取得（デバッグ用）
        /// </summary>
        public string GetEquipmentInfo()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendLine("=== 現在の装備 ===");

            foreach (var kvp in equippedItems)
            {
                string slotName = GetSlotName(kvp.Key);
                string itemName = kvp.Value != null ? kvp.Value.itemName : "なし";
                sb.AppendLine($"{slotName}: {itemName}");
            }

            EquipmentBonusTotal total = GetTotalBonus();
            sb.AppendLine("\n=== 合計ボーナス ===");
            sb.AppendLine($"攻撃力: +{total.attackBonus}");
            sb.AppendLine($"防御力: +{total.defenseBonus}");
            sb.AppendLine($"素早さ: +{total.speedBonus}");
            sb.AppendLine($"HP: +{total.hpBonus}");

            List<EquipmentEffect> effects = GetAllActiveEffects();
            if (effects.Count > 0)
            {
                sb.AppendLine("\n=== 特殊効果 ===");
                foreach (var effect in effects)
                {
                    sb.AppendLine($"• {effect.effectName}");
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// スロット名を取得
        /// </summary>
        private string GetSlotName(EquipmentSlot slot)
        {
            switch (slot)
            {
                case EquipmentSlot.Weapon: return "武器";
                case EquipmentSlot.Head: return "頭";
                case EquipmentSlot.Body: return "体";
                case EquipmentSlot.Legs: return "脚";
                case EquipmentSlot.Accessory1: return "アクセサリー1";
                case EquipmentSlot.Accessory2: return "アクセサリー2";
                case EquipmentSlot.Charm: return "お守り";
                default: return "不明";
            }
        }
    }

    /// <summary>
    /// 装備の合計ボーナス
    /// </summary>
    [System.Serializable]
    public class EquipmentBonusTotal
    {
        public int attackBonus;
        public int defenseBonus;
        public int speedBonus;
        public int hpBonus;
    }
}
