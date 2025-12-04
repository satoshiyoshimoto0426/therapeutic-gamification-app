using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace KokoroNoBoukensha.Items
{
    /// <summary>
    /// インベントリシステム
    /// プレイヤーが持つアイテムを管理
    /// </summary>
    public class Inventory : MonoBehaviour
    {
        public static Inventory Instance { get; private set; }

        [Header("Inventory Settings")]
        public int maxSlots = 20;
        
        [Header("Current Items")]
        public List<ItemStack> items = new List<ItemStack>();

        [Header("Events")]
        public System.Action OnInventoryChanged;

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

            InitializeInventory();
        }

        /// <summary>
        /// インベントリを初期化
        /// </summary>
        private void InitializeInventory()
        {
            items.Clear();
            Debug.Log("[Inventory] Initialized");
        }

        /// <summary>
        /// アイテムを追加
        /// </summary>
        public bool AddItem(Item item, int quantity = 1)
        {
            if (item == null) return false;

            // スタック可能なアイテムの場合、既存のスタックに追加
            if (item.isStackable)
            {
                ItemStack existingStack = items.FirstOrDefault(stack => 
                    stack.item.itemId == item.itemId && 
                    stack.quantity < item.maxStackSize
                );

                if (existingStack != null)
                {
                    int spaceLeft = item.maxStackSize - existingStack.quantity;
                    int amountToAdd = Mathf.Min(quantity, spaceLeft);
                    
                    existingStack.AddQuantity(amountToAdd);
                    quantity -= amountToAdd;

                    if (quantity <= 0)
                    {
                        Debug.Log($"[Inventory] Added {amountToAdd}x {item.itemName} to existing stack");
                        OnInventoryChanged?.Invoke();
                        return true;
                    }
                }
            }

            // 新しいスタックを作成
            if (items.Count >= maxSlots)
            {
                Debug.LogWarning("[Inventory] Inventory is full!");
                return false;
            }

            ItemStack newStack = new ItemStack(item, quantity);
            items.Add(newStack);

            Debug.Log($"[Inventory] Added {quantity}x {item.itemName}");
            OnInventoryChanged?.Invoke();
            return true;
        }

        /// <summary>
        /// アイテムを削除
        /// </summary>
        public bool RemoveItem(string itemId, int quantity = 1)
        {
            ItemStack stack = items.FirstOrDefault(s => s.item.itemId == itemId);
            
            if (stack == null)
            {
                Debug.LogWarning($"[Inventory] Item not found: {itemId}");
                return false;
            }

            if (stack.quantity < quantity)
            {
                Debug.LogWarning($"[Inventory] Not enough items to remove");
                return false;
            }

            stack.RemoveQuantity(quantity);

            if (stack.IsEmpty())
            {
                items.Remove(stack);
            }

            Debug.Log($"[Inventory] Removed {quantity}x {stack.item.itemName}");
            OnInventoryChanged?.Invoke();
            return true;
        }

        /// <summary>
        /// アイテムを使用
        /// </summary>
        public bool UseItem(string itemId)
        {
            ItemStack stack = items.FirstOrDefault(s => s.item.itemId == itemId);
            
            if (stack == null)
            {
                Debug.LogWarning($"[Inventory] Item not found: {itemId}");
                return false;
            }

            // プレイヤーを取得
            Character.Player player = FindObjectOfType<Character.Player>();
            if (player == null)
            {
                Debug.LogError("[Inventory] Player not found");
                return false;
            }

            // アイテムを使用
            bool success = stack.item.Use(player);

            if (success)
            {
                // 消費アイテムの場合は削除
                if (stack.item.itemType == ItemType.Consumable)
                {
                    RemoveItem(itemId, 1);
                }
            }

            return success;
        }

        /// <summary>
        /// アイテムを持っているかチェック
        /// </summary>
        public bool HasItem(string itemId, int quantity = 1)
        {
            ItemStack stack = items.FirstOrDefault(s => s.item.itemId == itemId);
            return stack != null && stack.quantity >= quantity;
        }

        /// <summary>
        /// アイテムの所持数を取得
        /// </summary>
        public int GetItemCount(string itemId)
        {
            ItemStack stack = items.FirstOrDefault(s => s.item.itemId == itemId);
            return stack?.quantity ?? 0;
        }

        /// <summary>
        /// アイテムを名前で検索
        /// </summary>
        public List<ItemStack> FindItemsByName(string name)
        {
            return items.Where(stack => 
                stack.item.itemName.Contains(name)
            ).ToList();
        }

        /// <summary>
        /// タイプでアイテムをフィルタ
        /// </summary>
        public List<ItemStack> GetItemsByType(ItemType type)
        {
            return items.Where(stack => stack.item.itemType == type).ToList();
        }

        /// <summary>
        /// レアリティでアイテムをフィルタ
        /// </summary>
        public List<ItemStack> GetItemsByRarity(Rarity rarity)
        {
            return items.Where(stack => stack.item.rarity == rarity).ToList();
        }

        /// <summary>
        /// すべてのアイテムを取得
        /// </summary>
        public List<ItemStack> GetAllItems()
        {
            return new List<ItemStack>(items);
        }

        /// <summary>
        /// インベントリがいっぱいかチェック
        /// </summary>
        public bool IsFull()
        {
            return items.Count >= maxSlots;
        }

        /// <summary>
        /// 空きスロット数を取得
        /// </summary>
        public int GetEmptySlots()
        {
            return maxSlots - items.Count;
        }

        /// <summary>
        /// インベントリをクリア
        /// </summary>
        public void Clear()
        {
            items.Clear();
            Debug.Log("[Inventory] Cleared");
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// アイテムをソート
        /// </summary>
        public void SortByType()
        {
            items = items.OrderBy(stack => stack.item.itemType)
                        .ThenBy(stack => stack.item.rarity)
                        .ToList();
            
            Debug.Log("[Inventory] Sorted by type");
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// レアリティでソート
        /// </summary>
        public void SortByRarity()
        {
            items = items.OrderByDescending(stack => stack.item.rarity)
                        .ThenBy(stack => stack.item.itemName)
                        .ToList();
            
            Debug.Log("[Inventory] Sorted by rarity");
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// 名前でソート
        /// </summary>
        public void SortByName()
        {
            items = items.OrderBy(stack => stack.item.itemName).ToList();
            
            Debug.Log("[Inventory] Sorted by name");
            OnInventoryChanged?.Invoke();
        }

        /// <summary>
        /// 総アイテム価値を計算
        /// </summary>
        public int GetTotalValue()
        {
            int total = 0;
            foreach (var stack in items)
            {
                total += stack.item.sellPrice * stack.quantity;
            }
            return total;
        }

        /// <summary>
        /// インベントリの状態を文字列で取得（デバッグ用）
        /// </summary>
        public string GetInventoryInfo()
        {
            if (items.Count == 0)
            {
                return "インベントリは空です";
            }

            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendLine($"=== インベントリ ({items.Count}/{maxSlots}) ===");

            foreach (var stack in items)
            {
                string quantity = stack.item.isStackable ? $"x{stack.quantity}" : "";
                string rarity = stack.item.rarity.ToString();
                sb.AppendLine($"[{rarity}] {stack.item.itemName} {quantity}");
            }

            sb.AppendLine($"総価値: {GetTotalValue()}G");

            return sb.ToString();
        }
    }
}
