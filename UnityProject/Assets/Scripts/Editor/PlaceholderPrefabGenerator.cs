using UnityEngine;
using UnityEditor;
using System.IO;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// プレースホルダーPrefab自動生成ツール
    /// 実際のアセットがない場合でもゲームをテストできるようにする
    /// </summary>
    public class PlaceholderPrefabGenerator
    {
        [MenuItem("Tools/Kokoro no Boukensha/Generate All Placeholders")]
        public static void GenerateAllPlaceholders()
        {
            CreateFolders();
            CreatePlayerPlaceholder();
            CreateEnemyPlaceholders();
            CreateDungeonPlaceholders();
            CreateEffectPlaceholders();
            
            AssetDatabase.Refresh();
            
            Debug.Log("[PlaceholderGenerator] 全てのプレースホルダーを生成しました。");
            EditorUtility.DisplayDialog("完了", 
                "全てのプレースホルダーPrefabを生成しました！\n\n" +
                "Assets/Prefabs/ フォルダに配置されています。\n" +
                "これらを使用してゲームをテストできます。", 
                "OK");
        }

        private static void CreateFolders()
        {
            CreateFolderIfNotExists("Assets/Prefabs");
            CreateFolderIfNotExists("Assets/Prefabs/Characters");
            CreateFolderIfNotExists("Assets/Prefabs/Characters/Enemies");
            CreateFolderIfNotExists("Assets/Prefabs/Dungeon");
            CreateFolderIfNotExists("Assets/Prefabs/Effects");
            CreateFolderIfNotExists("Assets/Prefabs/Lighting");
        }

        /// <summary>
        /// プレイヤープレースホルダーを作成
        /// </summary>
        private static void CreatePlayerPlaceholder()
        {
            GameObject playerObj = new GameObject("PlayerCharacter");
            
            // 見た目（Capsule）
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.name = "Visual";
            visual.transform.SetParent(playerObj.transform);
            visual.transform.localPosition = Vector3.zero;
            visual.GetComponent<Renderer>().material.color = new Color(0.2f, 0.5f, 1f); // Blue
            DestroyImmediate(visual.GetComponent<Collider>());

            // Collider
            CapsuleCollider collider = playerObj.AddComponent<CapsuleCollider>();
            collider.height = 2f;
            collider.radius = 0.3f;
            collider.center = new Vector3(0, 1, 0);

            // Rigidbody
            Rigidbody rb = playerObj.AddComponent<Rigidbody>();
            rb.useGravity = true;
            rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;

            // Scripts
            playerObj.AddComponent<Character.Player>();
            playerObj.AddComponent<Character.PlayerAnimationController>();

            // Tag & Layer
            playerObj.tag = "Player";
            playerObj.layer = LayerMask.NameToLayer("Default");

            // Prefab化
            string path = "Assets/Prefabs/Characters/PlayerCharacter.prefab";
            PrefabUtility.SaveAsPrefabAsset(playerObj, path);
            DestroyImmediate(playerObj);

            Debug.Log($"[PlaceholderGenerator] Created: {path}");
        }

        /// <summary>
        /// 敵プレースホルダーを作成
        /// </summary>
        private static void CreateEnemyPlaceholders()
        {
            // 敵タイプと色
            var enemies = new[]
            {
                new { Type = "Slime", Color = new Color(0.3f, 1f, 0.3f), Scale = 0.8f },
                new { Type = "Goblin", Color = new Color(0.3f, 0.8f, 0.3f), Scale = 1.0f },
                new { Type = "Wolf", Color = new Color(0.7f, 0.6f, 0.4f), Scale = 1.0f },
                new { Type = "Orc", Color = new Color(0.3f, 0.6f, 0.3f), Scale = 1.3f },
                new { Type = "Skeleton", Color = new Color(0.9f, 0.9f, 0.9f), Scale = 1.1f },
                new { Type = "Dragon", Color = new Color(0.8f, 0.2f, 0.2f), Scale = 2.0f }
            };

            foreach (var enemy in enemies)
            {
                GameObject enemyObj = new GameObject($"{enemy.Type}Enemy");
                
                // 見た目（Cube）
                GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
                visual.name = "Visual";
                visual.transform.SetParent(enemyObj.transform);
                visual.transform.localPosition = Vector3.zero;
                visual.transform.localScale = Vector3.one * enemy.Scale;
                visual.GetComponent<Renderer>().material.color = enemy.Color;
                DestroyImmediate(visual.GetComponent<Collider>());

                // Collider
                BoxCollider collider = enemyObj.AddComponent<BoxCollider>();
                collider.size = Vector3.one * enemy.Scale;

                // Rigidbody
                Rigidbody rb = enemyObj.AddComponent<Rigidbody>();
                rb.useGravity = true;
                rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;

                // Scripts
                var enemyScript = enemyObj.AddComponent<Character.Enemy>();
                enemyObj.AddComponent<Character.EnemyAnimationController>();

                // Tag & Layer
                enemyObj.tag = "Enemy";
                enemyObj.layer = LayerMask.NameToLayer("Default");

                // Prefab化
                string path = $"Assets/Prefabs/Characters/Enemies/{enemy.Type}Enemy.prefab";
                PrefabUtility.SaveAsPrefabAsset(enemyObj, path);
                DestroyImmediate(enemyObj);

                Debug.Log($"[PlaceholderGenerator] Created: {path}");
            }
        }

        /// <summary>
        /// ダンジョンプレースホルダーを作成
        /// </summary>
        private static void CreateDungeonPlaceholders()
        {
            // Floor
            GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "Floor_Normal";
            floor.transform.localScale = new Vector3(1, 0.1f, 1);
            floor.GetComponent<Renderer>().material.color = new Color(0.5f, 0.5f, 0.5f); // Gray
            floor.tag = "Floor";
            
            string floorPath = "Assets/Prefabs/Dungeon/Floor_Normal.prefab";
            PrefabUtility.SaveAsPrefabAsset(floor, floorPath);
            DestroyImmediate(floor);
            Debug.Log($"[PlaceholderGenerator] Created: {floorPath}");

            // Wall
            GameObject wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = "Wall_Normal";
            wall.transform.localScale = new Vector3(1, 3, 1);
            wall.transform.position = new Vector3(0, 1.5f, 0);
            wall.GetComponent<Renderer>().material.color = new Color(0.3f, 0.3f, 0.3f); // Dark Gray
            wall.tag = "Wall";
            
            string wallPath = "Assets/Prefabs/Dungeon/Wall_Normal.prefab";
            PrefabUtility.SaveAsPrefabAsset(wall, wallPath);
            DestroyImmediate(wall);
            Debug.Log($"[PlaceholderGenerator] Created: {wallPath}");

            // Stairs Down
            GameObject stairsDown = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            stairsDown.name = "StairsDown";
            stairsDown.transform.localScale = new Vector3(0.8f, 0.1f, 0.8f);
            stairsDown.GetComponent<Renderer>().material.color = new Color(0.2f, 0.2f, 0.8f); // Blue
            stairsDown.tag = "Stairs";
            
            // Trigger Collider
            stairsDown.GetComponent<Collider>().isTrigger = true;
            
            string stairsDownPath = "Assets/Prefabs/Dungeon/StairsDown.prefab";
            PrefabUtility.SaveAsPrefabAsset(stairsDown, stairsDownPath);
            DestroyImmediate(stairsDown);
            Debug.Log($"[PlaceholderGenerator] Created: {stairsDownPath}");

            // Stairs Up
            GameObject stairsUp = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            stairsUp.name = "StairsUp";
            stairsUp.transform.localScale = new Vector3(0.8f, 0.1f, 0.8f);
            stairsUp.GetComponent<Renderer>().material.color = new Color(0.8f, 0.8f, 0.2f); // Yellow
            stairsUp.tag = "Stairs";
            stairsUp.GetComponent<Collider>().isTrigger = true;
            
            string stairsUpPath = "Assets/Prefabs/Dungeon/StairsUp.prefab";
            PrefabUtility.SaveAsPrefabAsset(stairsUp, stairsUpPath);
            DestroyImmediate(stairsUp);
            Debug.Log($"[PlaceholderGenerator] Created: {stairsUpPath}");

            // Decoration - Pillar
            GameObject pillar = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pillar.name = "Pillar";
            pillar.transform.localScale = new Vector3(0.3f, 1.5f, 0.3f);
            pillar.GetComponent<Renderer>().material.color = new Color(0.6f, 0.6f, 0.5f);
            
            string pillarPath = "Assets/Prefabs/Dungeon/Pillar.prefab";
            PrefabUtility.SaveAsPrefabAsset(pillar, pillarPath);
            DestroyImmediate(pillar);
            Debug.Log($"[PlaceholderGenerator] Created: {pillarPath}");

            // Decoration - Torch
            GameObject torch = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            torch.name = "Torch";
            torch.transform.localScale = new Vector3(0.2f, 0.2f, 0.2f);
            torch.GetComponent<Renderer>().material.color = new Color(1f, 0.5f, 0f); // Orange
            
            // Light component
            Light light = torch.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = 5f;
            light.intensity = 1f;
            light.color = new Color(1f, 0.7f, 0.3f);
            
            string torchPath = "Assets/Prefabs/Dungeon/Torch.prefab";
            PrefabUtility.SaveAsPrefabAsset(torch, torchPath);
            DestroyImmediate(torch);
            Debug.Log($"[PlaceholderGenerator] Created: {torchPath}");

            // Lighting Prefabs
            CreateLightingPrefabs();
        }

        /// <summary>
        /// ライティングPrefabを作成
        /// </summary>
        private static void CreateLightingPrefabs()
        {
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
            Debug.Log($"[PlaceholderGenerator] Created: {roomLightPath}");

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
            Debug.Log($"[PlaceholderGenerator] Created: {corridorLightPath}");
        }

        /// <summary>
        /// エフェクトプレースホルダーを作成
        /// </summary>
        private static void CreateEffectPlaceholders()
        {
            // Attack Slash Effect
            GameObject slashEffect = new GameObject("AttackSlashEffect");
            ParticleSystem ps = slashEffect.AddComponent<ParticleSystem>();
            
            var main = ps.main;
            main.duration = 0.5f;
            main.startLifetime = 0.3f;
            main.startSpeed = 5f;
            main.startSize = 0.5f;
            main.startColor = Color.white;
            main.loop = false;

            var emission = ps.emission;
            emission.rateOverTime = 0;
            emission.SetBursts(new ParticleSystem.Burst[] { new ParticleSystem.Burst(0, 10) });

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 30f;

            string slashPath = "Assets/Prefabs/Effects/AttackSlashEffect.prefab";
            PrefabUtility.SaveAsPrefabAsset(slashEffect, slashPath);
            DestroyImmediate(slashEffect);
            Debug.Log($"[PlaceholderGenerator] Created: {slashPath}");

            // Level Up Effect
            GameObject levelUpEffect = new GameObject("LevelUpEffect");
            ParticleSystem psLevelUp = levelUpEffect.AddComponent<ParticleSystem>();
            
            var mainLevelUp = psLevelUp.main;
            mainLevelUp.duration = 2f;
            mainLevelUp.startLifetime = 1.5f;
            mainLevelUp.startSpeed = 2f;
            mainLevelUp.startSize = 0.3f;
            mainLevelUp.startColor = new Color(1f, 0.843f, 0f); // Gold
            mainLevelUp.loop = false;

            var emissionLevelUp = psLevelUp.emission;
            emissionLevelUp.rateOverTime = 50;

            var shapeLevelUp = psLevelUp.shape;
            shapeLevelUp.shapeType = ParticleSystemShapeType.Sphere;
            shapeLevelUp.radius = 0.5f;

            string levelUpPath = "Assets/Prefabs/Effects/LevelUpEffect.prefab";
            PrefabUtility.SaveAsPrefabAsset(levelUpEffect, levelUpPath);
            DestroyImmediate(levelUpEffect);
            Debug.Log($"[PlaceholderGenerator] Created: {levelUpPath}");

            // Heal Effect
            GameObject healEffect = new GameObject("HealEffect");
            ParticleSystem psHeal = healEffect.AddComponent<ParticleSystem>();
            
            var mainHeal = psHeal.main;
            mainHeal.duration = 1.5f;
            mainHeal.startLifetime = 1f;
            mainHeal.startSpeed = 1f;
            mainHeal.startSize = 0.2f;
            mainHeal.startColor = new Color(0.3f, 1f, 0.3f); // Green
            mainHeal.loop = false;

            var emissionHeal = psHeal.emission;
            emissionHeal.rateOverTime = 30;

            string healPath = "Assets/Prefabs/Effects/HealEffect.prefab";
            PrefabUtility.SaveAsPrefabAsset(healEffect, healPath);
            DestroyImmediate(healEffect);
            Debug.Log($"[PlaceholderGenerator] Created: {healPath}");
        }

        /// <summary>
        /// フォルダを作成（存在しない場合）
        /// </summary>
        private static void CreateFolderIfNotExists(string path)
        {
            if (!AssetDatabase.IsValidFolder(path))
            {
                string parentFolder = Path.GetDirectoryName(path).Replace("\\", "/");
                string folderName = Path.GetFileName(path);
                AssetDatabase.CreateFolder(parentFolder, folderName);
            }
        }
    }
}
