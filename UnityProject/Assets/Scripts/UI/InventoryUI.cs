using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

namespace KokoroNoBoukensha.UI
{
    /// <summary>
    /// インベントリUI管理
    /// </summary>
    public class InventoryUI : MonoBehaviour
    {
        public static InventoryUI Instance { get; private set; }

        [Header("UI References")]
        public GameObject inventoryPanel;
        public Transform itemSlotContainer;
        public GameObject itemSlotPrefab;

        [Header("Item Details")]
        public TextMeshProUGUI itemNameText;
        public TextMeshProUGUI itemDescriptionText;
        public Image itemIconImage;
        public Button useButton;
        public Button dropButton;

        [Header("Filters")]
        public TMP_Dropdown filterDropdown;
        public TMP_Dropdown sortDropdown;

        [Header("Equipment Slots")]
        public EquipmentSlotUI weaponSlot;
        public EquipmentSlotUI armorSlot;
        public EquipmentSlotUI accessorySlot;

        private List<GameObject> itemSlots = new List<GameObject>();
        private Items.ItemStack selectedItemStack;
        private bool isOpen = false;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            // インベントリを非表示で初期化
            if (inventoryPanel != null)
            {
                inventoryPanel.SetActive(false);
            }

            // イベント登録
            if (Items.Inventory.Instance != null)
            {
                Items.Inventory.Instance.OnInventoryChanged += RefreshInventoryUI;
            }

            // ボタンイベント
            if (useButton != null)
            {
                useButton.onClick.AddListener(OnUseButtonClicked);
            }

            if (dropButton != null)
            {
                dropButton.onClick.AddListener(OnDropButtonClicked);
            }

            // ドロップダウンイベント
            if (filterDropdown != null)
            {
                filterDropdown.onValueChanged.AddListener(OnFilterChanged);
            }

            if (sortDropdown != null)
            {
                sortDropdown.onValueChanged.AddListener(OnSortChanged);
            }
        }

        private void Update()
        {
            // Iキーでインベントリを開閉
            if (Input.GetKeyDown(KeyCode.I))
            {
                ToggleInventory();
            }

            // Escキーで閉じる
            if (Input.GetKeyDown(KeyCode.Escape) && isOpen)
            {
                CloseInventory();
            }
        }

        /// <summary>
        /// インベントリを開閉
        /// </summary>
        public void ToggleInventory()
        {
            if (isOpen)
            {
                CloseInventory();
            }
            else
            {
                OpenInventory();
            }
        }

        /// <summary>
        /// インベントリを開く
        /// </summary>
        public void OpenInventory()
        {
            if (inventoryPanel != null)
            {
                inventoryPanel.SetActive(true);
                isOpen = true;
                RefreshInventoryUI();

                // ゲームを一時停止
                if (Core.GameManager.Instance != null)
                {
                    Core.GameManager.Instance.PauseGame();
                }

                Debug.Log("[InventoryUI] Opened");
            }
        }

        /// <summary>
        /// インベントリを閉じる
        /// </summary>
        public void CloseInventory()
        {
            if (inventoryPanel != null)
            {
                inventoryPanel.SetActive(false);
                isOpen = false;
                ClearItemDetails();

                // ゲームを再開
                if (Core.GameManager.Instance != null)
                {
                    Core.GameManager.Instance.ResumeGame();
                }

                Debug.Log("[InventoryUI] Closed");
            }
        }

        /// <summary>
        /// インベントリUIを更新
        /// </summary>
        public void RefreshInventoryUI()
        {
            if (Items.Inventory.Instance == null) return;

            // 既存のスロットをクリア
            ClearItemSlots();

            // アイテムスロットを生成
            List<Items.ItemStack> items = Items.Inventory.Instance.GetAllItems();

            foreach (var itemStack in items)
            {
                CreateItemSlot(itemStack);
            }

            Debug.Log($"[InventoryUI] Refreshed with {items.Count} items");
        }

        /// <summary>
        /// アイテムスロットを作成
        /// </summary>
        private void CreateItemSlot(Items.ItemStack itemStack)
        {
            if (itemSlotPrefab == null || itemSlotContainer == null) return;

            GameObject slot = Instantiate(itemSlotPrefab, itemSlotContainer);
            itemSlots.Add(slot);

            // スロットのUI要素を設定
            ItemSlotUI slotUI = slot.GetComponent<ItemSlotUI>();
            if (slotUI != null)
            {
                slotUI.SetItemStack(itemStack);
                slotUI.OnSlotClicked += () => OnItemSlotClicked(itemStack);
            }
        }

        /// <summary>
        /// アイテムスロットをクリア
        /// </summary>
        private void ClearItemSlots()
        {
            foreach (var slot in itemSlots)
            {
                Destroy(slot);
            }
            itemSlots.Clear();
        }

        /// <summary>
        /// アイテムスロットがクリックされた
        /// </summary>
        private void OnItemSlotClicked(Items.ItemStack itemStack)
        {
            selectedItemStack = itemStack;
            ShowItemDetails(itemStack);
        }

        /// <summary>
        /// アイテムの詳細を表示
        /// </summary>
        private void ShowItemDetails(Items.ItemStack itemStack)
        {
            if (itemStack == null || itemStack.item == null) return;

            if (itemNameText != null)
            {
                itemNameText.text = itemStack.item.itemName;
                itemNameText.color = itemStack.item.GetRarityColor();
            }

            if (itemDescriptionText != null)
            {
                itemDescriptionText.text = itemStack.item.GetDetailedInfo();
            }

            if (itemIconImage != null && itemStack.item.icon != null)
            {
                itemIconImage.sprite = itemStack.item.icon;
                itemIconImage.gameObject.SetActive(true);
            }

            // 使用ボタンの表示
            if (useButton != null)
            {
                useButton.gameObject.SetActive(itemStack.item.itemType == Items.ItemType.Consumable || 
                                               itemStack.item.itemType == Items.ItemType.Equipment);
            }

            // ドロップボタンの表示
            if (dropButton != null)
            {
                dropButton.gameObject.SetActive(true);
            }
        }

        /// <summary>
        /// アイテム詳細をクリア
        /// </summary>
        private void ClearItemDetails()
        {
            selectedItemStack = null;

            if (itemNameText != null) itemNameText.text = "";
            if (itemDescriptionText != null) itemDescriptionText.text = "";
            if (itemIconImage != null) itemIconImage.gameObject.SetActive(false);
            if (useButton != null) useButton.gameObject.SetActive(false);
            if (dropButton != null) dropButton.gameObject.SetActive(false);
        }

        /// <summary>
        /// 使用ボタンがクリックされた
        /// </summary>
        private void OnUseButtonClicked()
        {
            if (selectedItemStack == null || Items.Inventory.Instance == null) return;

            bool success = Items.Inventory.Instance.UseItem(selectedItemStack.item.itemId);

            if (success)
            {
                HUDManager.Instance?.ShowNotification($"{selectedItemStack.item.itemName} を使用した");
                ClearItemDetails();
            }
        }

        /// <summary>
        /// ドロップボタンがクリックされた
        /// </summary>
        private void OnDropButtonClicked()
        {
            if (selectedItemStack == null || Items.Inventory.Instance == null) return;

            // TODO: 確認ダイアログを表示
            Items.Inventory.Instance.RemoveItem(selectedItemStack.item.itemId, 1);
            HUDManager.Instance?.ShowNotification($"{selectedItemStack.item.itemName} を捨てた");
            ClearItemDetails();
        }

        /// <summary>
        /// フィルターが変更された
        /// </summary>
        private void OnFilterChanged(int filterIndex)
        {
            // TODO: フィルター実装
            RefreshInventoryUI();
        }

        /// <summary>
        /// ソートが変更された
        /// </summary>
        private void OnSortChanged(int sortIndex)
        {
            if (Items.Inventory.Instance == null) return;

            switch (sortIndex)
            {
                case 0: // 名前順
                    Items.Inventory.Instance.SortByName();
                    break;
                case 1: // タイプ順
                    Items.Inventory.Instance.SortByType();
                    break;
                case 2: // レアリティ順
                    Items.Inventory.Instance.SortByRarity();
                    break;
            }

            RefreshInventoryUI();
        }

        /// <summary>
        /// 装備スロットを更新
        /// </summary>
        public void UpdateEquipmentSlots()
        {
            if (Items.EquipmentManager.Instance == null) return;

            // 武器スロット
            if (weaponSlot != null)
            {
                var weapon = Items.EquipmentManager.Instance.GetEquippedItem(Items.EquipmentSlot.Weapon);
                weaponSlot.SetEquipment(weapon);
            }

            // 防具スロット
            if (armorSlot != null)
            {
                var armor = Items.EquipmentManager.Instance.GetEquippedItem(Items.EquipmentSlot.Body);
                armorSlot.SetEquipment(armor);
            }

            // アクセサリースロット
            if (accessorySlot != null)
            {
                var accessory = Items.EquipmentManager.Instance.GetEquippedItem(Items.EquipmentSlot.Accessory1);
                accessorySlot.SetEquipment(accessory);
            }
        }
    }

    /// <summary>
    /// アイテムスロットUI（プレハブで使用）
    /// </summary>
    public class ItemSlotUI : MonoBehaviour
    {
        public Image iconImage;
        public TextMeshProUGUI quantityText;
        public Image rarityBorder;
        public Button slotButton;

        public System.Action OnSlotClicked;
        private Items.ItemStack itemStack;

        private void Start()
        {
            if (slotButton != null)
            {
                slotButton.onClick.AddListener(() => OnSlotClicked?.Invoke());
            }
        }

        public void SetItemStack(Items.ItemStack stack)
        {
            itemStack = stack;

            if (iconImage != null && stack.item.icon != null)
            {
                iconImage.sprite = stack.item.icon;
            }

            if (quantityText != null)
            {
                quantityText.text = stack.item.isStackable ? $"x{stack.quantity}" : "";
            }

            if (rarityBorder != null)
            {
                rarityBorder.color = stack.item.GetRarityColor();
            }
        }
    }

    /// <summary>
    /// 装備スロットUI
    /// </summary>
    public class EquipmentSlotUI : MonoBehaviour
    {
        public Image iconImage;
        public TextMeshProUGUI slotNameText;
        public Button slotButton;

        public System.Action<Items.Equipment> OnEquipmentClicked;
        private Items.Equipment equipment;

        private void Start()
        {
            if (slotButton != null)
            {
                slotButton.onClick.AddListener(() => OnEquipmentClicked?.Invoke(equipment));
            }
        }

        public void SetEquipment(Items.Equipment equip)
        {
            equipment = equip;

            if (iconImage != null)
            {
                if (equip != null && equip.icon != null)
                {
                    iconImage.sprite = equip.icon;
                    iconImage.gameObject.SetActive(true);
                }
                else
                {
                    iconImage.gameObject.SetActive(false);
                }
            }
        }
    }
}
