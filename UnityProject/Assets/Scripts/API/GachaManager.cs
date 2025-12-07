using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

namespace KokoroNoBoukensha.API
{
    /// <summary>
    /// ガチャシステム管理
    /// FastAPIのガチャサービスと連携、ローカルガチャシミュレーションも可能
    /// </summary>
    public class GachaManager : MonoBehaviour
    {
        public static GachaManager Instance { get; private set; }

        [Header("Gacha Settings")]
        public int normalGachaCost = 100;      // ノーマルガチャのコスト（ゴールド）
        public int premiumGachaCost = 300;     // プレミアムガチャのコスト
        public int superGachaCost = 1000;      // スーパーガチャのコスト

        [Header("Pull Counts")]
        public int single = 1;                 // 単発
        public int multi = 10;                 // 10連

        [Header("Probability Tables")]
        public GachaProbabilityTable normalGacha;
        public GachaProbabilityTable premiumGacha;
        public GachaProbabilityTable superGacha;

        [Header("Events")]
        public System.Action<GachaResult> OnGachaCompleted;

        [Header("History")]
        public List<GachaResult> gachaHistory = new List<GachaResult>();
        public int maxHistoryCount = 50;

        private int pityCounter = 0;           // 天井カウンター
        private const int PITY_THRESHOLD = 50; // 天井保証（50連でレジェンド確定）

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

            InitializeGachaTables();
        }

        /// <summary>
        /// ガチャ確率テーブルを初期化
        /// </summary>
        private void InitializeGachaTables()
        {
            // ノーマルガチャ
            normalGacha = new GachaProbabilityTable
            {
                name = "ノーマルガチャ",
                probabilities = new Dictionary<Items.Rarity, float>
                {
                    { Items.Rarity.Normal, 0.70f },      // 70%
                    { Items.Rarity.Rare, 0.25f },        // 25%
                    { Items.Rarity.SuperRare, 0.04f },   // 4%
                    { Items.Rarity.Legendary, 0.01f }    // 1%
                }
            };

            // プレミアムガチャ
            premiumGacha = new GachaProbabilityTable
            {
                name = "プレミアムガチャ",
                probabilities = new Dictionary<Items.Rarity, float>
                {
                    { Items.Rarity.Normal, 0.50f },      // 50%
                    { Items.Rarity.Rare, 0.35f },        // 35%
                    { Items.Rarity.SuperRare, 0.12f },   // 12%
                    { Items.Rarity.Legendary, 0.03f }    // 3%
                }
            };

            // スーパーガチャ
            superGacha = new GachaProbabilityTable
            {
                name = "スーパーガチャ",
                probabilities = new Dictionary<Items.Rarity, float>
                {
                    { Items.Rarity.Normal, 0.30f },      // 30%
                    { Items.Rarity.Rare, 0.40f },        // 40%
                    { Items.Rarity.SuperRare, 0.23f },   // 23%
                    { Items.Rarity.Legendary, 0.07f }    // 7%
                }
            };

            Debug.Log("[GachaManager] Probability tables initialized");
        }

        /// <summary>
        /// ガチャを引く（単発）
        /// </summary>
        public void DrawGacha(GachaType gachaType, System.Action<GachaResult> callback)
        {
            DrawMultiGacha(gachaType, 1, callback);
        }

        /// <summary>
        /// ガチャを引く（複数回）
        /// </summary>
        public void DrawMultiGacha(GachaType gachaType, int count, System.Action<GachaResult> callback)
        {
            // プレイヤーのゴールドをチェック
            Character.Player player = FindObjectOfType<Character.Player>();
            if (player == null)
            {
                Debug.LogError("[GachaManager] Player not found");
                callback?.Invoke(null);
                return;
            }

            int totalCost = GetGachaCost(gachaType) * count;

            if (player.stats.Gold < totalCost)
            {
                Debug.LogWarning($"[GachaManager] Not enough gold. Need: {totalCost}, Have: {player.stats.Gold}");
                UI.HUDManager.Instance?.ShowNotification("ゴールドが足りません", Color.red);
                callback?.Invoke(null);
                return;
            }

            // ゴールドを消費
            player.stats.Gold -= totalCost;

            // ガチャ実行（ローカルシミュレーション）
            StartCoroutine(DrawGachaCoroutine(gachaType, count, callback));
        }

        /// <summary>
        /// ガチャ実行コルーチン
        /// </summary>
        private IEnumerator DrawGachaCoroutine(GachaType gachaType, int count, System.Action<GachaResult> callback)
        {
            GachaResult result = new GachaResult
            {
                gachaType = gachaType,
                pullCount = count,
                items = new List<Items.Equipment>(),
                totalCost = GetGachaCost(gachaType) * count,
                timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            };

            GachaProbabilityTable table = GetGachaTable(gachaType);

            // 各回のガチャを実行
            for (int i = 0; i < count; i++)
            {
                Items.Rarity rarity = DetermineRarity(table);
                Items.Equipment equipment = GenerateEquipment(rarity);
                result.items.Add(equipment);

                pityCounter++;

                // 天井保証チェック
                if (pityCounter >= PITY_THRESHOLD && rarity != Items.Rarity.Legendary)
                {
                    Debug.Log("[GachaManager] Pity triggered! Legendary guaranteed.");
                    equipment = GenerateEquipment(Items.Rarity.Legendary);
                    result.items[result.items.Count - 1] = equipment;
                    pityCounter = 0;
                }
                else if (rarity == Items.Rarity.Legendary)
                {
                    pityCounter = 0; // レジェンドが出たらリセット
                }

                yield return new WaitForSeconds(0.1f); // 演出用の待機
            }

            // インベントリに追加
            foreach (var item in result.items)
            {
                if (Items.Inventory.Instance != null)
                {
                    Items.Inventory.Instance.AddItem(item);
                }
            }

            // 履歴に追加
            AddToHistory(result);

            // 統計情報を計算
            result.CalculateStatistics();

            Debug.Log($"[GachaManager] Drew {count}x {gachaType}: {result.GetSummary()}");

            // イベント発火
            OnGachaCompleted?.Invoke(result);
            callback?.Invoke(result);
        }

        /// <summary>
        /// レアリティを決定
        /// </summary>
        private Items.Rarity DetermineRarity(GachaProbabilityTable table)
        {
            float random = Random.value;
            float cumulative = 0f;

            // 確率に基づいてレアリティを決定
            foreach (var kvp in table.probabilities.OrderBy(x => x.Key))
            {
                cumulative += kvp.Value;
                if (random <= cumulative)
                {
                    return kvp.Key;
                }
            }

            return Items.Rarity.Normal; // フォールバック
        }

        /// <summary>
        /// 装備を生成
        /// </summary>
        private Items.Equipment GenerateEquipment(Items.Rarity rarity)
        {
            // プレイヤーのレベルを取得
            Character.Player player = FindObjectOfType<Character.Player>();
            int playerLevel = player != null ? player.stats.Level : 1;

            // ランダムで武器か防具を決定
            bool isWeapon = Random.value > 0.5f;

            Items.Equipment equipment;

            if (isWeapon)
            {
                equipment = Items.EquipmentPresets.CreateRandomWeapon(playerLevel, rarity);
            }
            else
            {
                equipment = Items.EquipmentPresets.CreateRandomArmor(playerLevel, rarity);
            }

            return equipment;
        }

        /// <summary>
        /// ガチャテーブルを取得
        /// </summary>
        private GachaProbabilityTable GetGachaTable(GachaType gachaType)
        {
            switch (gachaType)
            {
                case GachaType.Normal:
                    return normalGacha;
                case GachaType.Premium:
                    return premiumGacha;
                case GachaType.Super:
                    return superGacha;
                default:
                    return normalGacha;
            }
        }

        /// <summary>
        /// ガチャコストを取得
        /// </summary>
        private int GetGachaCost(GachaType gachaType)
        {
            switch (gachaType)
            {
                case GachaType.Normal:
                    return normalGachaCost;
                case GachaType.Premium:
                    return premiumGachaCost;
                case GachaType.Super:
                    return superGachaCost;
                default:
                    return normalGachaCost;
            }
        }

        /// <summary>
        /// 履歴に追加
        /// </summary>
        private void AddToHistory(GachaResult result)
        {
            gachaHistory.Insert(0, result);

            if (gachaHistory.Count > maxHistoryCount)
            {
                gachaHistory.RemoveAt(gachaHistory.Count - 1);
            }
        }

        /// <summary>
        /// 天井カウンターを取得
        /// </summary>
        public int GetPityCounter()
        {
            return pityCounter;
        }

        /// <summary>
        /// 天井までの残り回数を取得
        /// </summary>
        public int GetPityRemaining()
        {
            return PITY_THRESHOLD - pityCounter;
        }

        /// <summary>
        /// ガチャ履歴を取得
        /// </summary>
        public List<GachaResult> GetHistory()
        {
            return new List<GachaResult>(gachaHistory);
        }

        /// <summary>
        /// ガチャ統計を取得
        /// </summary>
        public GachaStatistics GetStatistics()
        {
            GachaStatistics stats = new GachaStatistics();

            foreach (var result in gachaHistory)
            {
                stats.totalPulls += result.pullCount;
                stats.totalSpent += result.totalCost;

                foreach (var item in result.items)
                {
                    switch (item.rarity)
                    {
                        case Items.Rarity.Normal:
                            stats.normalCount++;
                            break;
                        case Items.Rarity.Rare:
                            stats.rareCount++;
                            break;
                        case Items.Rarity.SuperRare:
                            stats.superRareCount++;
                            break;
                        case Items.Rarity.Legendary:
                            stats.legendaryCount++;
                            break;
                    }
                }
            }

            return stats;
        }
    }

    /// <summary>
    /// ガチャの種類
    /// </summary>
    public enum GachaType
    {
        Normal,    // ノーマルガチャ（100G）
        Premium,   // プレミアムガチャ（300G）
        Super      // スーパーガチャ（1000G）
    }

    /// <summary>
    /// ガチャ確率テーブル
    /// </summary>
    [System.Serializable]
    public class GachaProbabilityTable
    {
        public string name;
        public Dictionary<Items.Rarity, float> probabilities;

        public string GetProbabilityText()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendLine($"=== {name} 排出確率 ===");

            foreach (var kvp in probabilities.OrderByDescending(x => x.Value))
            {
                string rarityName = GetRarityName(kvp.Key);
                float percentage = kvp.Value * 100f;
                sb.AppendLine($"{rarityName}: {percentage:F2}%");
            }

            return sb.ToString();
        }

        private string GetRarityName(Items.Rarity rarity)
        {
            switch (rarity)
            {
                case Items.Rarity.Normal: return "ノーマル";
                case Items.Rarity.Rare: return "レア";
                case Items.Rarity.SuperRare: return "スーパーレア";
                case Items.Rarity.Legendary: return "レジェンド";
                default: return "不明";
            }
        }
    }

    /// <summary>
    /// ガチャ結果
    /// </summary>
    [System.Serializable]
    public class GachaResult
    {
        public GachaType gachaType;
        public int pullCount;
        public List<Items.Equipment> items;
        public int totalCost;
        public string timestamp;

        // 統計情報
        public int normalCount;
        public int rareCount;
        public int superRareCount;
        public int legendaryCount;

        public void CalculateStatistics()
        {
            normalCount = items.Count(i => i.rarity == Items.Rarity.Normal);
            rareCount = items.Count(i => i.rarity == Items.Rarity.Rare);
            superRareCount = items.Count(i => i.rarity == Items.Rarity.SuperRare);
            legendaryCount = items.Count(i => i.rarity == Items.Rarity.Legendary);
        }

        public string GetSummary()
        {
            return $"N:{normalCount} R:{rareCount} SR:{superRareCount} L:{legendaryCount}";
        }

        public bool HasLegendary()
        {
            return legendaryCount > 0;
        }
    }

    /// <summary>
    /// ガチャ統計
    /// </summary>
    [System.Serializable]
    public class GachaStatistics
    {
        public int totalPulls;
        public int totalSpent;
        public int normalCount;
        public int rareCount;
        public int superRareCount;
        public int legendaryCount;

        public float GetAverageRarity()
        {
            if (totalPulls == 0) return 0f;

            float totalRarity = normalCount * 1f + rareCount * 2f + superRareCount * 3f + legendaryCount * 4f;
            return totalRarity / totalPulls;
        }

        public string GetSummaryText()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendLine("=== ガチャ統計 ===");
            sb.AppendLine($"総回数: {totalPulls}回");
            sb.AppendLine($"総消費: {totalSpent}G");
            sb.AppendLine($"\nノーマル: {normalCount}個");
            sb.AppendLine($"レア: {rareCount}個");
            sb.AppendLine($"スーパーレア: {superRareCount}個");
            sb.AppendLine($"レジェンド: {legendaryCount}個");
            sb.AppendLine($"\n平均レアリティ: {GetAverageRarity():F2}");

            return sb.ToString();
        }
    }
}
