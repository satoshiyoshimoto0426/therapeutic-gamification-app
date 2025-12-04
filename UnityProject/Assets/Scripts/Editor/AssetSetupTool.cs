using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// アセット自動セットアップツール
    /// Unity エディタメニューからアクセス可能
    /// </summary>
    public class AssetSetupTool : EditorWindow
    {
        private static readonly string MODELS_PATH = "Assets/Models";
        private static readonly string PREFABS_PATH = "Assets/Prefabs";
        private static readonly string ANIMATIONS_PATH = "Assets/Animations";
        private static readonly string MATERIALS_PATH = "Assets/Materials";

        private Vector2 scrollPosition;
        private bool showPlayerSetup = true;
        private bool showEnemySetup = true;
        private bool showDungeonSetup = true;
        private bool showEffectSetup = true;

        [MenuItem("Tools/Kokoro no Boukensha/Asset Setup Tool")]
        public static void ShowWindow()
        {
            GetWindow<AssetSetupTool>("Asset Setup Tool");
        }

        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            GUILayout.Label("心の冒険者 - アセットセットアップツール", EditorStyles.boldLabel);
            EditorGUILayout.Space();

            EditorGUILayout.HelpBox(
                "このツールは、インポートされたアセットを自動的にセットアップします。\n" +
                "各セクションのボタンをクリックして、アセットを設定してください。",
                MessageType.Info
            );

            EditorGUILayout.Space();

            // フォルダ構造作成
            if (GUILayout.Button("1. フォルダ構造を作成", GUILayout.Height(30)))
            {
                CreateFolderStructure();
            }

            EditorGUILayout.Space();

            // プレイヤーセットアップ
            showPlayerSetup = EditorGUILayout.Foldout(showPlayerSetup, "2. プレイヤーキャラクター", true);
            if (showPlayerSetup)
            {
                EditorGUI.indentLevel++;
                
                EditorGUILayout.HelpBox(
                    "Mixamoからダウンロードしたプレイヤーモデルとアニメーションをインポート後、クリックしてください。",
                    MessageType.Info
                );

                if (GUILayout.Button("プレイヤーモデルをセットアップ"))
                {
                    SetupPlayerModel();
                }

                if (GUILayout.Button("プレイヤーAnimatorを作成"))
                {
                    CreatePlayerAnimator();
                }

                if (GUILayout.Button("プレイヤーPrefabを作成"))
                {
                    CreatePlayerPrefab();
                }

                EditorGUI.indentLevel--;
            }

            EditorGUILayout.Space();

            // 敵セットアップ
            showEnemySetup = EditorGUILayout.Foldout(showEnemySetup, "3. 敵キャラクター", true);
            if (showEnemySetup)
            {
                EditorGUI.indentLevel++;
                
                EditorGUILayout.HelpBox(
                    "Mixamoからダウンロードした敵モデルをインポート後、クリックしてください。",
                    MessageType.Info
                );

                if (GUILayout.Button("敵モデルを一括セットアップ"))
                {
                    SetupEnemyModels();
                }

                if (GUILayout.Button("敵Prefabを一括作成"))
                {
                    CreateEnemyPrefabs();
                }

                EditorGUI.indentLevel--;
            }

            EditorGUILayout.Space();

            // ダンジョンセットアップ
            showDungeonSetup = EditorGUILayout.Foldout(showDungeonSetup, "4. ダンジョン環境", true);
            if (showDungeonSetup)
            {
                EditorGUI.indentLevel++;
                
                EditorGUILayout.HelpBox(
                    "Unity Asset Storeからダンジョンアセットをインポート後、クリックしてください。",
                    MessageType.Info
                );

                if (GUILayout.Button("ダンジョンPrefabをセットアップ"))
                {
                    SetupDungeonPrefabs();
                }

                if (GUILayout.Button("ライティングPrefabを作成"))
                {
                    CreateLightingPrefabs();
                }

                EditorGUI.indentLevel--;
            }

            EditorGUILayout.Space();

            // エフェクトセットアップ
            showEffectSetup = EditorGUILayout.Foldout(showEffectSetup, "5. エフェクト", true);
            if (showEffectSetup)
            {
                EditorGUI.indentLevel++;
                
                EditorGUILayout.HelpBox(
                    "Unity Asset Storeからエフェクトアセットをインポート後、クリックしてください。",
                    MessageType.Info
                );

                if (GUILayout.Button("エフェクトPrefabをセットアップ"))
                {
                    SetupEffectPrefabs();
                }

                EditorGUI.indentLevel--;
            }

            EditorGUILayout.Space();

            // 最終設定
            if (GUILayout.Button("6. ModelManagerを自動設定", GUILayout.Height(30)))
            {
                ConfigureModelManager();
            }

            EditorGUILayout.Space();

            // プレースホルダー作成
            EditorGUILayout.HelpBox(
                "アセットがまだない場合、プレースホルダー（仮モデル）を作成できます。",
                MessageType.Warning
            );

            if (GUILayout.Button("プレースホルダーを作成（テスト用）", GUILayout.Height(30)))
            {
                CreatePlaceholders();
            }

            EditorGUILayout.EndScrollView();
        }

        /// <summary>
        /// フォルダ構造を作成
        /// </summary>
        private void CreateFolderStructure()
        {
            CreateFolder("Assets/Models");
            CreateFolder("Assets/Models/Characters");
            CreateFolder("Assets/Models/Characters/Player");
            CreateFolder("Assets/Models/Characters/Player/Animations");
            CreateFolder("Assets/Models/Characters/Enemies");
            CreateFolder("Assets/Models/Characters/Enemies/Goblin");
            CreateFolder("Assets/Models/Characters/Enemies/Wolf");
            CreateFolder("Assets/Models/Characters/Enemies/Orc");
            CreateFolder("Assets/Models/Characters/Enemies/Skeleton");
            CreateFolder("Assets/Models/Characters/Enemies/Dragon");
            CreateFolder("Assets/Models/Environment");
            CreateFolder("Assets/Models/Environment/Dungeon");
            CreateFolder("Assets/Models/Items");

            CreateFolder("Assets/Prefabs");
            CreateFolder("Assets/Prefabs/Characters");
            CreateFolder("Assets/Prefabs/Characters/Enemies");
            CreateFolder("Assets/Prefabs/Dungeon");
            CreateFolder("Assets/Prefabs/Effects");
            CreateFolder("Assets/Prefabs/Lighting");

            CreateFolder("Assets/Animations");
            CreateFolder("Assets/Animations/Player");
            CreateFolder("Assets/Animations/Enemies");

            CreateFolder("Assets/Materials");
            CreateFolder("Assets/Materials/Characters");
            CreateFolder("Assets/Materials/Environment");

            AssetDatabase.Refresh();
            Debug.Log("[AssetSetupTool] フォルダ構造を作成しました。");
        }

        /// <summary>
        /// プレイヤーモデルをセットアップ
        /// </summary>
        private void SetupPlayerModel()
        {
            string modelPath = "Assets/Models/Characters/Player";
            
            // FBXファイルを検索
            string[] fbxFiles = Directory.GetFiles(modelPath, "*.fbx", SearchOption.AllDirectories);

            if (fbxFiles.Length == 0)
            {
                EditorUtility.DisplayDialog("エラー", 
                    $"{modelPath} にFBXファイルが見つかりません。\nMixamoからモデルをダウンロードしてインポートしてください。", 
                    "OK");
                return;
            }

            int count = 0;
            foreach (string fbxPath in fbxFiles)
            {
                ModelImporter importer = AssetImporter.GetAtPath(fbxPath) as ModelImporter;
                if (importer != null)
                {
                    // モデル設定
                    importer.globalScale = 1.0f;
                    importer.meshCompression = ModelImporterMeshCompression.Off;
                    importer.isReadable = true;
                    importer.optimizeMeshPolygons = true;
                    importer.importBlendShapes = true;

                    // Rig設定
                    importer.animationType = ModelImporterAnimationType.Human;
                    importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                    importer.optimizeGameObjects = true;

                    // アニメーション設定（アニメーションファイルの場合）
                    if (fbxPath.Contains("Animations"))
                    {
                        importer.importAnimation = true;
                        importer.animationCompression = ModelImporterAnimationCompression.Optimal;
                        importer.resampleCurves = true;

                        // Idle, Walk系はループ
                        string fileName = Path.GetFileNameWithoutExtension(fbxPath).ToLower();
                        if (fileName.Contains("idle") || fileName.Contains("walk"))
                        {
                            ModelImporterClipAnimation[] clipAnimations = importer.defaultClipAnimations;
                            if (clipAnimations.Length > 0)
                            {
                                clipAnimations[0].loopTime = true;
                                clipAnimations[0].loopPose = true;
                                importer.clipAnimations = clipAnimations;
                            }
                        }
                    }

                    importer.SaveAndReimport();
                    count++;
                }
            }

            AssetDatabase.Refresh();
            Debug.Log($"[AssetSetupTool] プレイヤーモデルを {count} 個セットアップしました。");
            EditorUtility.DisplayDialog("完了", $"プレイヤーモデルを {count} 個セットアップしました。", "OK");
        }

        /// <summary>
        /// プレイヤーAnimatorを作成
        /// </summary>
        private void CreatePlayerAnimator()
        {
            string animatorPath = "Assets/Animations/Player/PlayerAnimator.controller";

            // 既に存在する場合はスキップ
            if (File.Exists(animatorPath))
            {
                EditorUtility.DisplayDialog("情報", 
                    "PlayerAnimator.controller は既に存在します。", 
                    "OK");
                return;
            }

            // Animator Controllerを作成
            UnityEditor.Animations.AnimatorController animator = 
                UnityEditor.Animations.AnimatorController.CreateAnimatorControllerAtPath(animatorPath);

            // Parameters追加
            animator.AddParameter("IsMoving", AnimatorControllerParameterType.Bool);
            animator.AddParameter("DirectionX", AnimatorControllerParameterType.Float);
            animator.AddParameter("DirectionZ", AnimatorControllerParameterType.Float);
            animator.AddParameter("IsAttacking", AnimatorControllerParameterType.Bool);
            animator.AddParameter("Attack", AnimatorControllerParameterType.Trigger);
            animator.AddParameter("TakeDamage", AnimatorControllerParameterType.Trigger);
            animator.AddParameter("Death", AnimatorControllerParameterType.Trigger);
            animator.AddParameter("UseItem", AnimatorControllerParameterType.Trigger);
            animator.AddParameter("LevelUp", AnimatorControllerParameterType.Trigger);

            // TODO: States と Transitions を追加
            // （手動でBlendTreeを設定する必要があります）

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[AssetSetupTool] PlayerAnimator.controller を作成しました。");
            EditorUtility.DisplayDialog("完了", 
                "PlayerAnimator.controller を作成しました。\n\n" +
                "手動でBlendTreeとStatesを設定してください。", 
                "OK");
        }

        /// <summary>
        /// プレイヤーPrefabを作成
        /// </summary>
        private void CreatePlayerPrefab()
        {
            // TODO: 実装
            Debug.Log("[AssetSetupTool] プレイヤーPrefab作成（未実装）");
            EditorUtility.DisplayDialog("未実装", 
                "プレイヤーPrefab作成機能は手動で行ってください。\n\n" +
                "ASSET_IMPORT_GUIDE.md を参照してください。", 
                "OK");
        }

        /// <summary>
        /// 敵モデルを一括セットアップ
        /// </summary>
        private void SetupEnemyModels()
        {
            string enemiesPath = "Assets/Models/Characters/Enemies";
            
            if (!Directory.Exists(enemiesPath))
            {
                EditorUtility.DisplayDialog("エラー", 
                    $"{enemiesPath} フォルダが見つかりません。", 
                    "OK");
                return;
            }

            string[] fbxFiles = Directory.GetFiles(enemiesPath, "*.fbx", SearchOption.AllDirectories);

            if (fbxFiles.Length == 0)
            {
                EditorUtility.DisplayDialog("エラー", 
                    $"{enemiesPath} にFBXファイルが見つかりません。", 
                    "OK");
                return;
            }

            int count = 0;
            foreach (string fbxPath in fbxFiles)
            {
                ModelImporter importer = AssetImporter.GetAtPath(fbxPath) as ModelImporter;
                if (importer != null)
                {
                    importer.globalScale = 1.0f;
                    importer.animationType = ModelImporterAnimationType.Human;
                    importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                    importer.SaveAndReimport();
                    count++;
                }
            }

            AssetDatabase.Refresh();
            Debug.Log($"[AssetSetupTool] 敵モデルを {count} 個セットアップしました。");
            EditorUtility.DisplayDialog("完了", $"敵モデルを {count} 個セットアップしました。", "OK");
        }

        /// <summary>
        /// 敵Prefabを一括作成
        /// </summary>
        private void CreateEnemyPrefabs()
        {
            // TODO: 実装
            Debug.Log("[AssetSetupTool] 敵Prefab作成（未実装）");
            EditorUtility.DisplayDialog("未実装", 
                "敵Prefab作成機能は手動で行ってください。\n\n" +
                "ASSET_IMPORT_GUIDE.md を参照してください。", 
                "OK");
        }

        /// <summary>
        /// ダンジョンPrefabをセットアップ
        /// </summary>
        private void SetupDungeonPrefabs()
        {
            // TODO: 実装
            Debug.Log("[AssetSetupTool] ダンジョンPrefabセットアップ（未実装）");
            EditorUtility.DisplayDialog("未実装", 
                "ダンジョンPrefabセットアップ機能は手動で行ってください。\n\n" +
                "ASSET_IMPORT_GUIDE.md を参照してください。", 
                "OK");
        }

        /// <summary>
        /// ライティングPrefabを作成
        /// </summary>
        private void CreateLightingPrefabs()
        {
            CreateFolder("Assets/Prefabs/Lighting");

            // Room Light
            GameObject roomLight = new GameObject("RoomLight");
            Light roomLightComponent = roomLight.AddComponent<Light>();
            roomLightComponent.type = LightType.Point;
            roomLightComponent.range = 10f;
            roomLightComponent.intensity = 1.5f;
            roomLightComponent.color = new Color(1f, 0.956f, 0.839f); // Warm White
            roomLightComponent.shadows = LightShadows.Soft;

            string roomLightPath = "Assets/Prefabs/Lighting/RoomLight.prefab";
            PrefabUtility.SaveAsPrefabAsset(roomLight, roomLightPath);
            DestroyImmediate(roomLight);

            // Corridor Light
            GameObject corridorLight = new GameObject("CorridorLight");
            Light corridorLightComponent = corridorLight.AddComponent<Light>();
            corridorLightComponent.type = LightType.Point;
            corridorLightComponent.range = 5f;
            corridorLightComponent.intensity = 0.8f;
            corridorLightComponent.color = new Color(0.839f, 0.894f, 1f); // Cool White
            corridorLightComponent.shadows = LightShadows.None;

            string corridorLightPath = "Assets/Prefabs/Lighting/CorridorLight.prefab";
            PrefabUtility.SaveAsPrefabAsset(corridorLight, corridorLightPath);
            DestroyImmediate(corridorLight);

            AssetDatabase.Refresh();
            Debug.Log("[AssetSetupTool] ライティングPrefabを作成しました。");
            EditorUtility.DisplayDialog("完了", 
                "RoomLight.prefab と CorridorLight.prefab を作成しました。", 
                "OK");
        }

        /// <summary>
        /// エフェクトPrefabをセットアップ
        /// </summary>
        private void SetupEffectPrefabs()
        {
            // TODO: 実装
            Debug.Log("[AssetSetupTool] エフェクトPrefabセットアップ（未実装）");
            EditorUtility.DisplayDialog("未実装", 
                "エフェクトPrefabセットアップ機能は手動で行ってください。\n\n" +
                "ASSET_IMPORT_GUIDE.md を参照してください。", 
                "OK");
        }

        /// <summary>
        /// ModelManagerを自動設定
        /// </summary>
        private void ConfigureModelManager()
        {
            // TODO: 実装
            Debug.Log("[AssetSetupTool] ModelManager自動設定（未実装）");
            EditorUtility.DisplayDialog("未実装", 
                "ModelManager自動設定機能は手動で行ってください。\n\n" +
                "ASSET_IMPORT_GUIDE.md を参照してください。", 
                "OK");
        }

        /// <summary>
        /// プレースホルダー（仮モデル）を作成
        /// </summary>
        private void CreatePlaceholders()
        {
            CreateFolder("Assets/Prefabs/Placeholders");

            // プレイヤープレースホルダー
            GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            player.name = "PlayerPlaceholder";
            player.GetComponent<Renderer>().material.color = Color.blue;
            string playerPath = "Assets/Prefabs/Placeholders/PlayerPlaceholder.prefab";
            PrefabUtility.SaveAsPrefabAsset(player, playerPath);
            DestroyImmediate(player);

            // 敵プレースホルダー（複数種類）
            string[] enemyTypes = { "Goblin", "Wolf", "Orc", "Skeleton", "Dragon" };
            Color[] enemyColors = { Color.green, Color.yellow, Color.red, Color.white, Color.magenta };

            for (int i = 0; i < enemyTypes.Length; i++)
            {
                GameObject enemy = GameObject.CreatePrimitive(PrimitiveType.Cube);
                enemy.name = $"{enemyTypes[i]}Placeholder";
                enemy.GetComponent<Renderer>().material.color = enemyColors[i];
                string enemyPath = $"Assets/Prefabs/Placeholders/{enemyTypes[i]}Placeholder.prefab";
                PrefabUtility.SaveAsPrefabAsset(enemy, enemyPath);
                DestroyImmediate(enemy);
            }

            // ダンジョンタイルプレースホルダー
            GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "FloorPlaceholder";
            floor.transform.localScale = new Vector3(1, 0.1f, 1);
            floor.GetComponent<Renderer>().material.color = Color.gray;
            string floorPath = "Assets/Prefabs/Placeholders/FloorPlaceholder.prefab";
            PrefabUtility.SaveAsPrefabAsset(floor, floorPath);
            DestroyImmediate(floor);

            GameObject wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = "WallPlaceholder";
            wall.transform.localScale = new Vector3(1, 3, 1);
            wall.GetComponent<Renderer>().material.color = new Color(0.3f, 0.3f, 0.3f);
            string wallPath = "Assets/Prefabs/Placeholders/WallPlaceholder.prefab";
            PrefabUtility.SaveAsPrefabAsset(wall, wallPath);
            DestroyImmediate(wall);

            AssetDatabase.Refresh();
            Debug.Log("[AssetSetupTool] プレースホルダーを作成しました。");
            EditorUtility.DisplayDialog("完了", 
                "テスト用プレースホルダーを作成しました。\n\n" +
                "Assets/Prefabs/Placeholders/ にあります。", 
                "OK");
        }

        /// <summary>
        /// フォルダを作成（既に存在する場合はスキップ）
        /// </summary>
        private void CreateFolder(string path)
        {
            if (!AssetDatabase.IsValidFolder(path))
            {
                string parentFolder = Path.GetDirectoryName(path);
                string folderName = Path.GetFileName(path);
                AssetDatabase.CreateFolder(parentFolder, folderName);
            }
        }
    }
}
