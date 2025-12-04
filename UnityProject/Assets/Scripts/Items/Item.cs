using UnityEngine;

namespace KokoroNoBoukensha.Items
{
    /// <summary>
    /// アイテムの基底クラス
    /// 風来のシレン風のアイテムシステム
    /// </summary>
    [System.Serializable]
    public class Item
    {
        [Header("Basic Info")]
        public string itemId;
        public string itemName;
        public string description;
        public ItemType itemType;
        public Rarity rarity;

        [Header("Value")]
        public int buyPrice;
        public int sellPrice;
        public bool isStackable;
        public int maxStackSize = 99;

        [Header("Visual")]
        public Sprite icon;
        public GameObject prefab;

        public Item()
        {
            itemId = System.Guid.NewGuid().ToString();
        }

        /// <summary>
        /// アイテムを使用
        /// </summary>
        public virtual bool Use(Character.Player player)
        {
            Debug.Log($"[Item] Used {itemName}");
            return true;
        }

        /// <summary>
        /// アイテムの詳細情報を取得
        /// </summary>
        public virtual string GetDetailedInfo()
        {
            string rarityText = GetRarityText(rarity);
            return $"<b>{itemName}</b> [{rarityText}]\n\n{description}\n\n価格: {buyPrice}G";
        }

        /// <summary>
        /// レアリティのテキスト表現
        /// </summary>
        private string GetRarityText(Rarity rarity)
        {
            switch (rarity)
            {
                case Rarity.Normal: return "ノーマル";
                case Rarity.Rare: return "レア";
                case Rarity.SuperRare: return "スーパーレア";
                case Rarity.Legendary: return "レジェンド";
                default: return "不明";
            }
        }

        /// <summary>
        /// レアリティの色を取得
        /// </summary>
        public Color GetRarityColor()
        {
            switch (rarity)
            {
                case Rarity.Normal: return Color.white;
                case Rarity.Rare: return new Color(0.3f, 0.5f, 1f); // 青
                case Rarity.SuperRare: return new Color(0.7f, 0.3f, 1f); // 紫
                case Rarity.Legendary: return new Color(1f, 0.8f, 0f); // 金
                default: return Color.white;
            }
        }
    }

    /// <summary>
    /// アイテムの種類
    /// </summary>
    public enum ItemType
    {
        Consumable,     // 消費アイテム
        Equipment,      // 装備品
        Material,       // 素材
        KeyItem,        // 重要アイテム
        Throwable       // 投擲アイテム
    }

    /// <summary>
    /// レアリティ
    /// </summary>
    public enum Rarity
    {
        Normal,         // N (白)
        Rare,           // R (青)
        SuperRare,      // SR (紫)
        Legendary       // レジェンド (金)
    }

    /// <summary>
    /// 消費アイテム
    /// </summary>
    [System.Serializable]
    public class ConsumableItem : Item
    {
        [Header("Consumable Properties")]
        public ConsumableType consumableType;
        public int effectValue;
        public int duration;

        public override bool Use(Character.Player player)
        {
            if (player == null) return false;

            switch (consumableType)
            {
                case ConsumableType.HPPotion:
                    player.Heal(effectValue);
                    Debug.Log($"[Item] HP回復: +{effectValue}");
                    break;

                case ConsumableType.FullRecover:
                    player.stats.CurrentHP = player.stats.MaxHP;
                    Debug.Log($"[Item] HP全回復");
                    break;

                case ConsumableType.BreadRation:
                    player.stats.Hunger += effectValue;
                    player.stats.Hunger = Mathf.Min(player.stats.Hunger, 100);
                    Debug.Log($"[Item] 満腹度回復: +{effectValue}");
                    break;

                case ConsumableType.AntidoteHerb:
                    // TODO: 毒状態を治療
                    Debug.Log($"[Item] 毒を治療");
                    break;

                case ConsumableType.ScrollOfTeleport:
                    // TODO: ランダムワープ
                    Debug.Log($"[Item] ワープ");
                    break;

                case ConsumableType.ScrollOfMap:
                    // TODO: マップ全体表示
                    Debug.Log($"[Item] マップ表示");
                    break;

                case ConsumableType.RevivalGrass:
                    // TODO: 復活効果（死亡時自動発動）
                    Debug.Log($"[Item] 復活の草を持っています");
                    break;

                default:
                    Debug.LogWarning($"[Item] Unknown consumable type: {consumableType}");
                    return false;
            }

            return true;
        }

        public override string GetDetailedInfo()
        {
            string baseInfo = base.GetDetailedInfo();
            string effectText = GetEffectText();
            return $"{baseInfo}\n\n{effectText}";
        }

        private string GetEffectText()
        {
            switch (consumableType)
            {
                case ConsumableType.HPPotion:
                    return $"効果: HP +{effectValue}";
                case ConsumableType.FullRecover:
                    return "効果: HP全回復";
                case ConsumableType.BreadRation:
                    return $"効果: 満腹度 +{effectValue}";
                case ConsumableType.AntidoteHerb:
                    return "効果: 毒を治療";
                case ConsumableType.ScrollOfTeleport:
                    return "効果: ランダムワープ";
                case ConsumableType.ScrollOfMap:
                    return "効果: マップ全体を表示";
                case ConsumableType.RevivalGrass:
                    return "効果: 死亡時に自動復活";
                default:
                    return "効果: 不明";
            }
        }
    }

    /// <summary>
    /// 消費アイテムの種類
    /// </summary>
    public enum ConsumableType
    {
        HPPotion,           // HP回復ポーション
        FullRecover,        // HP全回復
        BreadRation,        // パンの配給（満腹度回復）
        AntidoteHerb,       // 解毒の草
        ScrollOfTeleport,   // テレポートの巻物
        ScrollOfMap,        // マップの巻物
        RevivalGrass,       // 復活の草
        MonsterMeat         // モンスターの肉（変身）
    }

    /// <summary>
    /// 投擲アイテム
    /// </summary>
    [System.Serializable]
    public class ThrowableItem : Item
    {
        [Header("Throwable Properties")]
        public int damage;
        public int range;
        public bool isAreaOfEffect;
        public int aoeRadius;

        public override bool Use(Character.Player player)
        {
            // TODO: 投擲モード開始
            Debug.Log($"[Item] {itemName} を投げる準備");
            return true;
        }

        public void Throw(Vector2Int targetPosition)
        {
            Debug.Log($"[Item] {itemName} を {targetPosition} に投げた");

            if (isAreaOfEffect)
            {
                // 範囲攻撃
                DealAOEDamage(targetPosition);
            }
            else
            {
                // 単体攻撃
                DealSingleDamage(targetPosition);
            }
        }

        private void DealSingleDamage(Vector2Int position)
        {
            // TODO: 指定位置の敵にダメージ
            Debug.Log($"[Item] {damage} ダメージ");
        }

        private void DealAOEDamage(Vector2Int center)
        {
            // TODO: 範囲内の敵全てにダメージ
            Debug.Log($"[Item] 範囲 {aoeRadius} に {damage} ダメージ");
        }
    }

    /// <summary>
    /// アイテムのインスタンス（スタック可能）
    /// </summary>
    [System.Serializable]
    public class ItemStack
    {
        public Item item;
        public int quantity;

        public ItemStack(Item item, int quantity = 1)
        {
            this.item = item;
            this.quantity = quantity;
        }

        /// <summary>
        /// スタックに追加
        /// </summary>
        public bool AddQuantity(int amount)
        {
            if (!item.isStackable) return false;

            int newQuantity = quantity + amount;
            if (newQuantity > item.maxStackSize)
            {
                return false;
            }

            quantity = newQuantity;
            return true;
        }

        /// <summary>
        /// スタックから減らす
        /// </summary>
        public bool RemoveQuantity(int amount)
        {
            if (quantity < amount) return false;

            quantity -= amount;
            return true;
        }

        /// <summary>
        /// スタックが空か
        /// </summary>
        public bool IsEmpty()
        {
            return quantity <= 0;
        }
    }
}
