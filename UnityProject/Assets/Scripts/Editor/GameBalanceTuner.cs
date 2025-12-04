using UnityEngine;
using UnityEditor;
using KokoroNoBoukensha.Core;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// ゲームバランスをエディタ上でリアルタイム調整するツール
    /// Tools > Kokoro no Boukensha > Game Balance Tuner
    /// </summary>
    public class GameBalanceTuner : EditorWindow
    {
        private Vector2 scrollPosition;
        private int selectedTab = 0;
        private string[] tabNames = { "Player", "Enemies", "Items", "Gacha", "Floors" };

        // Player Settings
        private int playerStartHP = 100;
        private int playerStartAttack = 10;
        private int playerStartDefense = 5;
        private float playerHungerDecreaseRate = 0.1f;
        private float playerExpMultiplier = 1.0f;

        // Enemy Settings
        private float enemyStatMultiplier = 1.0f;
        private float enemyExpMultiplier = 1.0f;
        private float enemyGoldMultiplier = 1.0f;

        // Item Settings
        private float itemDropRate = 0.3f;
        private float rarityNormal = 0.60f;
        private float rarityRare = 0.25f;
        private float raritySR = 0.10f;
        private float rarityLegend = 0.05f;

        // Gacha Settings
        private float gachaNormal = 0.60f;
        private float gachaRare = 0.25f;
        private float gachaSR = 0.10f;
        private float gachaLegend = 0.05f;
        private int gachaGuaranteedPity = 50;

        // Floor Settings
        private int maxFloors = 30;
        private int enemiesPerFloor = 8;
        private int itemsPerFloor = 5;

        [MenuItem("Tools/Kokoro no Boukensha/Game Balance Tuner")]
        public static void ShowWindow()
        {
            GetWindow<GameBalanceTuner>("Game Balance Tuner");
        }

        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            GUILayout.Label("Game Balance Tuner", EditorStyles.boldLabel);
            GUILayout.Space(10);

            selectedTab = GUILayout.Toolbar(selectedTab, tabNames);
            GUILayout.Space(10);

            switch (selectedTab)
            {
                case 0: DrawPlayerTab(); break;
                case 1: DrawEnemiesTab(); break;
                case 2: DrawItemsTab(); break;
                case 3: DrawGachaTab(); break;
                case 4: DrawFloorsTab(); break;
            }

            GUILayout.Space(20);

            // Apply/Reset Buttons
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Apply Changes", GUILayout.Height(30)))
            {
                ApplyChanges();
            }
            if (GUILayout.Button("Reset to Default", GUILayout.Height(30)))
            {
                ResetToDefault();
            }
            if (GUILayout.Button("Load Current", GUILayout.Height(30)))
            {
                LoadCurrentSettings();
            }
            EditorGUILayout.EndHorizontal();

            GUILayout.Space(10);

            // Export/Import
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Export to JSON"))
            {
                ExportToJSON();
            }
            if (GUILayout.Button("Import from JSON"))
            {
                ImportFromJSON();
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.EndScrollView();
        }

        private void DrawPlayerTab()
        {
            GUILayout.Label("Player Settings", EditorStyles.boldLabel);

            playerStartHP = EditorGUILayout.IntSlider("Start HP", playerStartHP, 50, 200);
            playerStartAttack = EditorGUILayout.IntSlider("Start Attack", playerStartAttack, 5, 30);
            playerStartDefense = EditorGUILayout.IntSlider("Start Defense", playerStartDefense, 1, 20);
            playerHungerDecreaseRate = EditorGUILayout.Slider("Hunger Decrease Rate", playerHungerDecreaseRate, 0.01f, 1f);
            playerExpMultiplier = EditorGUILayout.Slider("EXP Multiplier", playerExpMultiplier, 0.5f, 3f);

            GUILayout.Space(10);
            GUILayout.Label("Player Stats Preview", EditorStyles.miniLabel);
            EditorGUILayout.HelpBox(
                $"Level 1: HP {playerStartHP}, ATK {playerStartAttack}, DEF {playerStartDefense}\n" +
                $"Level 10: HP {playerStartHP + 90}, ATK {playerStartAttack + 18}, DEF {playerStartDefense + 9}\n" +
                $"Hunger: {playerHungerDecreaseRate * 100:F0}% per turn",
                MessageType.Info
            );
        }

        private void DrawEnemiesTab()
        {
            GUILayout.Label("Enemy Settings", EditorStyles.boldLabel);

            enemyStatMultiplier = EditorGUILayout.Slider("Stat Multiplier", enemyStatMultiplier, 0.5f, 2f);
            enemyExpMultiplier = EditorGUILayout.Slider("EXP Multiplier", enemyExpMultiplier, 0.5f, 3f);
            enemyGoldMultiplier = EditorGUILayout.Slider("Gold Multiplier", enemyGoldMultiplier, 0.5f, 3f);

            GUILayout.Space(10);
            GUILayout.Label("Enemy Preview (Floor 1)", EditorStyles.miniLabel);

            int slimeHP = (int)(10 * enemyStatMultiplier);
            int slimeATK = (int)(3 * enemyStatMultiplier);
            int slimeDEF = (int)(1 * enemyStatMultiplier);
            int slimeEXP = (int)(5 * enemyExpMultiplier);
            int slimeGold = (int)(3 * enemyGoldMultiplier);

            EditorGUILayout.HelpBox(
                $"Slime: HP {slimeHP}, ATK {slimeATK}, DEF {slimeDEF}\n" +
                $"Reward: {slimeEXP} EXP, {slimeGold} Gold\n\n" +
                $"Player Damage to Slime: {Mathf.Max(1, playerStartAttack - slimeDEF)}\n" +
                $"Slime Damage to Player: {Mathf.Max(1, slimeATK - playerStartDefense)}",
                MessageType.Info
            );
        }

        private void DrawItemsTab()
        {
            GUILayout.Label("Item Drop Settings", EditorStyles.boldLabel);

            itemDropRate = EditorGUILayout.Slider("Drop Rate", itemDropRate, 0f, 1f);

            GUILayout.Label("Rarity Distribution", EditorStyles.miniLabel);
            rarityNormal = EditorGUILayout.Slider("Normal (N)", rarityNormal, 0f, 1f);
            rarityRare = EditorGUILayout.Slider("Rare (R)", rarityRare, 0f, 1f);
            raritySR = EditorGUILayout.Slider("Super Rare (SR)", raritySR, 0f, 1f);
            rarityLegend = EditorGUILayout.Slider("Legend", rarityLegend, 0f, 1f);

            float total = rarityNormal + rarityRare + raritySR + rarityLegend;
            if (total != 1f)
            {
                EditorGUILayout.HelpBox($"Total: {total:F2} (should be 1.0). Click 'Normalize' to fix.", MessageType.Warning);
                if (GUILayout.Button("Normalize Rarities"))
                {
                    rarityNormal /= total;
                    rarityRare /= total;
                    raritySR /= total;
                    rarityLegend /= total;
                }
            }

            GUILayout.Space(10);
            EditorGUILayout.HelpBox(
                $"In 100 enemy defeats:\n" +
                $"Items dropped: {itemDropRate * 100:F0}\n" +
                $"  - Normal: {itemDropRate * 100 * rarityNormal:F0}\n" +
                $"  - Rare: {itemDropRate * 100 * rarityRare:F0}\n" +
                $"  - SR: {itemDropRate * 100 * raritySR:F0}\n" +
                $"  - Legend: {itemDropRate * 100 * rarityLegend:F0}",
                MessageType.Info
            );
        }

        private void DrawGachaTab()
        {
            GUILayout.Label("Gacha Settings", EditorStyles.boldLabel);

            GUILayout.Label("Rarity Rates", EditorStyles.miniLabel);
            gachaNormal = EditorGUILayout.Slider("Normal (N)", gachaNormal, 0f, 1f);
            gachaRare = EditorGUILayout.Slider("Rare (R)", gachaRare, 0f, 1f);
            gachaSR = EditorGUILayout.Slider("Super Rare (SR)", gachaSR, 0f, 1f);
            gachaLegend = EditorGUILayout.Slider("Legend", gachaLegend, 0f, 1f);

            float total = gachaNormal + gachaRare + gachaSR + gachaLegend;
            if (total != 1f)
            {
                EditorGUILayout.HelpBox($"Total: {total:F2} (should be 1.0). Click 'Normalize' to fix.", MessageType.Warning);
                if (GUILayout.Button("Normalize Rarities"))
                {
                    gachaNormal /= total;
                    gachaRare /= total;
                    gachaSR /= total;
                    gachaLegend /= total;
                }
            }

            GUILayout.Space(10);
            gachaGuaranteedPity = EditorGUILayout.IntSlider("Guaranteed Legend (Pity)", gachaGuaranteedPity, 10, 100);

            GUILayout.Space(10);
            EditorGUILayout.HelpBox(
                $"10-Pull Gacha Expected Results:\n" +
                $"  - Normal: {10 * gachaNormal:F1}\n" +
                $"  - Rare: {10 * gachaRare:F1}\n" +
                $"  - SR: {10 * gachaSR:F1}\n" +
                $"  - Legend: {10 * gachaLegend:F1}\n\n" +
                $"Guaranteed Legend every {gachaGuaranteedPity} pulls",
                MessageType.Info
            );
        }

        private void DrawFloorsTab()
        {
            GUILayout.Label("Floor Settings", EditorStyles.boldLabel);

            maxFloors = EditorGUILayout.IntSlider("Max Floors", maxFloors, 10, 100);
            enemiesPerFloor = EditorGUILayout.IntSlider("Enemies per Floor", enemiesPerFloor, 1, 20);
            itemsPerFloor = EditorGUILayout.IntSlider("Items per Floor", itemsPerFloor, 0, 10);

            GUILayout.Space(10);
            EditorGUILayout.HelpBox(
                $"Dungeon Configuration:\n" +
                $"  - Total Floors: {maxFloors}\n" +
                $"  - Boss Floors: 10, 20, {maxFloors}\n" +
                $"  - Total Enemies: {maxFloors * enemiesPerFloor}\n" +
                $"  - Total Items: {maxFloors * itemsPerFloor}",
                MessageType.Info
            );
        }

        private void ApplyChanges()
        {
            // GameBalance.csのScriptableObjectを探す
            // 実際の実装では、GameBalanceのstaticメソッドやScriptableObjectに書き込む
            Debug.Log("Balance changes applied!");

            // 例: PlayerPrefsに保存（実際はScriptableObjectやJSONに保存する）
            PlayerPrefs.SetInt("Balance_PlayerStartHP", playerStartHP);
            PlayerPrefs.SetInt("Balance_PlayerStartAttack", playerStartAttack);
            PlayerPrefs.SetFloat("Balance_EnemyStatMultiplier", enemyStatMultiplier);
            PlayerPrefs.Save();

            EditorUtility.DisplayDialog("Success", "Game balance settings applied!", "OK");
        }

        private void ResetToDefault()
        {
            if (EditorUtility.DisplayDialog("Reset to Default", "Are you sure you want to reset all settings to default?", "Yes", "Cancel"))
            {
                playerStartHP = 100;
                playerStartAttack = 10;
                playerStartDefense = 5;
                playerHungerDecreaseRate = 0.1f;
                playerExpMultiplier = 1.0f;

                enemyStatMultiplier = 1.0f;
                enemyExpMultiplier = 1.0f;
                enemyGoldMultiplier = 1.0f;

                itemDropRate = 0.3f;
                rarityNormal = 0.60f;
                rarityRare = 0.25f;
                raritySR = 0.10f;
                rarityLegend = 0.05f;

                gachaNormal = 0.60f;
                gachaRare = 0.25f;
                gachaSR = 0.10f;
                gachaLegend = 0.05f;
                gachaGuaranteedPity = 50;

                maxFloors = 30;
                enemiesPerFloor = 8;
                itemsPerFloor = 5;

                Debug.Log("Settings reset to default");
            }
        }

        private void LoadCurrentSettings()
        {
            // PlayerPrefsから読み込み（実際はScriptableObjectやJSONから読み込む）
            if (PlayerPrefs.HasKey("Balance_PlayerStartHP"))
            {
                playerStartHP = PlayerPrefs.GetInt("Balance_PlayerStartHP", 100);
                playerStartAttack = PlayerPrefs.GetInt("Balance_PlayerStartAttack", 10);
                enemyStatMultiplier = PlayerPrefs.GetFloat("Balance_EnemyStatMultiplier", 1.0f);
                Debug.Log("Current settings loaded");
            }
            else
            {
                EditorUtility.DisplayDialog("No Saved Settings", "No saved settings found. Using current values.", "OK");
            }
        }

        private void ExportToJSON()
        {
            string path = EditorUtility.SaveFilePanel("Export Balance Settings", "", "game_balance.json", "json");
            if (!string.IsNullOrEmpty(path))
            {
                var settings = new GameBalanceSettings
                {
                    playerStartHP = this.playerStartHP,
                    playerStartAttack = this.playerStartAttack,
                    playerStartDefense = this.playerStartDefense,
                    enemyStatMultiplier = this.enemyStatMultiplier,
                    itemDropRate = this.itemDropRate,
                    rarityNormal = this.rarityNormal,
                    rarityRare = this.rarityRare,
                    raritySR = this.raritySR,
                    rarityLegend = this.rarityLegend
                };

                string json = JsonUtility.ToJson(settings, true);
                System.IO.File.WriteAllText(path, json);
                Debug.Log($"Balance settings exported to {path}");
                EditorUtility.DisplayDialog("Export Successful", $"Settings exported to:\n{path}", "OK");
            }
        }

        private void ImportFromJSON()
        {
            string path = EditorUtility.OpenFilePanel("Import Balance Settings", "", "json");
            if (!string.IsNullOrEmpty(path))
            {
                string json = System.IO.File.ReadAllText(path);
                var settings = JsonUtility.FromJson<GameBalanceSettings>(json);

                playerStartHP = settings.playerStartHP;
                playerStartAttack = settings.playerStartAttack;
                playerStartDefense = settings.playerStartDefense;
                enemyStatMultiplier = settings.enemyStatMultiplier;
                itemDropRate = settings.itemDropRate;
                rarityNormal = settings.rarityNormal;
                rarityRare = settings.rarityRare;
                raritySR = settings.raritySR;
                rarityLegend = settings.rarityLegend;

                Debug.Log($"Balance settings imported from {path}");
                EditorUtility.DisplayDialog("Import Successful", $"Settings imported from:\n{path}", "OK");
            }
        }

        [System.Serializable]
        private class GameBalanceSettings
        {
            public int playerStartHP;
            public int playerStartAttack;
            public int playerStartDefense;
            public float enemyStatMultiplier;
            public float itemDropRate;
            public float rarityNormal;
            public float rarityRare;
            public float raritySR;
            public float rarityLegend;
        }
    }
}
