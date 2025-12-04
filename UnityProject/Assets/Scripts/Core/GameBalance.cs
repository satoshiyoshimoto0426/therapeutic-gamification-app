using UnityEngine;

namespace KokoroNoBoukensha.Core
{
    /// <summary>
    /// ゲームバランス設定
    /// 各種パラメータを一元管理
    /// </summary>
    [CreateAssetMenu(fileName = "GameBalance", menuName = "KokoroNoBoukensha/Game Balance")]
    public class GameBalance : ScriptableObject
    {
        [Header("Player Stats")]
        [Tooltip("初期HP")]
        public int initialHP = 100;
        
        [Tooltip("初期攻撃力")]
        public int initialAttack = 10;
        
        [Tooltip("初期防御力")]
        public int initialDefense = 5;
        
        [Tooltip("レベルアップ時HP上昇量")]
        public int hpGainPerLevel = 10;
        
        [Tooltip("レベルアップ時攻撃力上昇量")]
        public int attackGainPerLevel = 2;
        
        [Tooltip("レベルアップ時防御力上昇量")]
        public int defenseGainPerLevel = 1;

        [Header("Experience")]
        [Tooltip("レベル2到達に必要な経験値")]
        public int baseExpRequirement = 100;
        
        [Tooltip("レベルアップ毎の経験値増加率")]
        [Range(1.0f, 2.0f)]
        public float expGrowthRate = 1.2f;

        [Header("Hunger System")]
        [Tooltip("初期満腹度")]
        public int initialHunger = 100;
        
        [Tooltip("最大満腹度")]
        public int maxHunger = 150;
        
        [Tooltip("1ターンあたりの満腹度減少")]
        public int hungerDecreasePerTurn = 1;
        
        [Tooltip("満腹度0時のHP減少量")]
        public int hungerDamage = 5;

        [Header("Combat")]
        [Tooltip("クリティカル確率 (%)")]
        [Range(0f, 100f)]
        public float criticalChance = 10f;
        
        [Tooltip("クリティカル倍率")]
        [Range(1.5f, 3.0f)]
        public float criticalMultiplier = 2.0f;
        
        [Tooltip("回避確率 (%)")]
        [Range(0f, 50f)]
        public float dodgeChance = 5f;

        [Header("Enemy Stats")]
        [Tooltip("敵のレベル倍率（プレイヤーレベルに対する割合）")]
        [Range(0.5f, 2.0f)]
        public float enemyLevelMultiplier = 1.0f;
        
        [Tooltip("敵のHP倍率")]
        [Range(0.5f, 3.0f)]
        public float enemyHPMultiplier = 1.2f;
        
        [Tooltip("敵の攻撃力倍率")]
        [Range(0.5f, 2.0f)]
        public float enemyAttackMultiplier = 0.9f;
        
        [Tooltip("敵の防御力倍率")]
        [Range(0.5f, 2.0f)]
        public float enemyDefenseMultiplier = 0.8f;

        [Header("Boss Stats")]
        [Tooltip("ボスのHP倍率")]
        [Range(2.0f, 10.0f)]
        public float bossHPMultiplier = 5.0f;
        
        [Tooltip("ボスの攻撃力倍率")]
        [Range(1.0f, 3.0f)]
        public float bossAttackMultiplier = 1.5f;
        
        [Tooltip("ボスの防御力倍率")]
        [Range(1.0f, 3.0f)]
        public float bossDefenseMultiplier = 1.2f;

        [Header("Rewards")]
        [Tooltip("敵撃破時の経験値倍率")]
        [Range(0.5f, 2.0f)]
        public float expRewardMultiplier = 1.0f;
        
        [Tooltip("敵撃破時のゴールド倍率")]
        [Range(0.5f, 2.0f)]
        public float goldRewardMultiplier = 1.0f;
        
        [Tooltip("ボス撃破時の経験値ボーナス")]
        public int bossExpBonus = 1000;
        
        [Tooltip("ボス撃破時のゴールドボーナス")]
        public int bossGoldBonus = 500;

        [Header("Items")]
        [Tooltip("ポーション回復量")]
        public int potionHealAmount = 50;
        
        [Tooltip("食料回復量（満腹度）")]
        public int foodHungerAmount = 30;
        
        [Tooltip("アイテムドロップ率 (%)")]
        [Range(0f, 100f)]
        public float itemDropRate = 30f;

        [Header("Gacha")]
        [Tooltip("ノーマルガチャコスト")]
        public int normalGachaCost = 100;
        
        [Tooltip("プレミアムガチャコスト")]
        public int premiumGachaCost = 300;
        
        [Tooltip("スーパーガチャコスト")]
        public int superGachaCost = 500;
        
        [Tooltip("天井到達回数")]
        public int gachaPityLimit = 50;

        [Header("Dungeon")]
        [Tooltip("ダンジョンの幅")]
        public int dungeonWidth = 50;
        
        [Tooltip("ダンジョンの高さ")]
        public int dungeonHeight = 50;
        
        [Tooltip("部屋の最小サイズ")]
        public int minRoomSize = 4;
        
        [Tooltip("部屋の最大サイズ")]
        public int maxRoomSize = 10;
        
        [Tooltip("敵の最大数（フロアあたり）")]
        public int maxEnemiesPerFloor = 20;
        
        [Tooltip("アイテムの最大数（フロアあたり）")]
        public int maxItemsPerFloor = 10;

        [Header("Difficulty Scaling")]
        [Tooltip("難易度上昇率（フロア毎）")]
        [Range(1.0f, 1.5f)]
        public float difficultyScalePerFloor = 1.05f;
        
        [Tooltip("ボスフロア（10階毎）")]
        public int bossFloorInterval = 10;

        /// <summary>
        /// レベルに必要な経験値を計算
        /// </summary>
        public int GetExpRequirement(int level)
        {
            return Mathf.RoundToInt(baseExpRequirement * Mathf.Pow(expGrowthRate, level - 1));
        }

        /// <summary>
        /// フロアの難易度倍率を取得
        /// </summary>
        public float GetFloorDifficultyMultiplier(int floor)
        {
            return Mathf.Pow(difficultyScalePerFloor, floor - 1);
        }

        /// <summary>
        /// ボスフロアか判定
        /// </summary>
        public bool IsBossFloor(int floor)
        {
            return floor % bossFloorInterval == 0;
        }

        /// <summary>
        /// 敵のステータスを計算
        /// </summary>
        public (int hp, int attack, int defense) CalculateEnemyStats(int playerLevel, int floor, bool isBoss = false)
        {
            float difficultyMultiplier = GetFloorDifficultyMultiplier(floor);
            int enemyLevel = Mathf.RoundToInt(playerLevel * enemyLevelMultiplier);

            int baseHP = initialHP + (hpGainPerLevel * enemyLevel);
            int baseAttack = initialAttack + (attackGainPerLevel * enemyLevel);
            int baseDefense = initialDefense + (defenseGainPerLevel * enemyLevel);

            if (isBoss)
            {
                baseHP = Mathf.RoundToInt(baseHP * bossHPMultiplier);
                baseAttack = Mathf.RoundToInt(baseAttack * bossAttackMultiplier);
                baseDefense = Mathf.RoundToInt(baseDefense * bossDefenseMultiplier);
            }
            else
            {
                baseHP = Mathf.RoundToInt(baseHP * enemyHPMultiplier);
                baseAttack = Mathf.RoundToInt(baseAttack * enemyAttackMultiplier);
                baseDefense = Mathf.RoundToInt(baseDefense * enemyDefenseMultiplier);
            }

            // 難易度倍率適用
            baseHP = Mathf.RoundToInt(baseHP * difficultyMultiplier);
            baseAttack = Mathf.RoundToInt(baseAttack * difficultyMultiplier);
            baseDefense = Mathf.RoundToInt(baseDefense * difficultyMultiplier);

            return (baseHP, baseAttack, baseDefense);
        }

        /// <summary>
        /// 報酬を計算
        /// </summary>
        public (int exp, int gold) CalculateRewards(int enemyLevel, bool isBoss = false)
        {
            int baseExp = Mathf.RoundToInt(50 * Mathf.Pow(1.1f, enemyLevel));
            int baseGold = Mathf.RoundToInt(20 * Mathf.Pow(1.1f, enemyLevel));

            baseExp = Mathf.RoundToInt(baseExp * expRewardMultiplier);
            baseGold = Mathf.RoundToInt(baseGold * goldRewardMultiplier);

            if (isBoss)
            {
                baseExp += bossExpBonus;
                baseGold += bossGoldBonus;
            }

            return (baseExp, baseGold);
        }
    }
}
