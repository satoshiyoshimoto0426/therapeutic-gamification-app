using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// オーディオアセットのセットアップを自動化するツール
    /// Tools > Kokoro no Boukensha > Audio Setup Tool
    /// </summary>
    public class AudioSetupTool : EditorWindow
    {
        private Vector2 scrollPosition;
        private bool setupFolders = true;
        private bool generatePlaceholders = true;
        private bool optimizeSettings = true;

        [MenuItem("Tools/Kokoro no Boukensha/Audio Setup Tool")]
        public static void ShowWindow()
        {
            GetWindow<AudioSetupTool>("Audio Setup Tool");
        }

        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            GUILayout.Label("Audio Setup Tool", EditorStyles.boldLabel);
            GUILayout.Space(10);

            EditorGUILayout.HelpBox(
                "このツールはオーディオアセットのセットアップを自動化します。\n" +
                "1. フォルダ構造の作成\n" +
                "2. プレースホルダーオーディオの生成（テスト用）\n" +
                "3. インポート設定の最適化",
                MessageType.Info
            );

            GUILayout.Space(10);

            setupFolders = EditorGUILayout.Toggle("フォルダ構造を作成", setupFolders);
            generatePlaceholders = EditorGUILayout.Toggle("プレースホルダーを生成", generatePlaceholders);
            optimizeSettings = EditorGUILayout.Toggle("インポート設定を最適化", optimizeSettings);

            GUILayout.Space(20);

            if (GUILayout.Button("セットアップ実行", GUILayout.Height(40)))
            {
                ExecuteSetup();
            }

            GUILayout.Space(20);

            EditorGUILayout.HelpBox(
                "⚠️ 注意: プレースホルダーは無音のテスト用ファイルです。\n" +
                "実際のゲームでは FREE_AUDIO_ASSETS.md を参照して\n" +
                "本物のオーディオアセットをダウンロードしてください。",
                MessageType.Warning
            );

            EditorGUILayout.EndScrollView();
        }

        private void ExecuteSetup()
        {
            int steps = 0;
            int totalSteps = 3;

            try
            {
                if (setupFolders)
                {
                    EditorUtility.DisplayProgressBar("Audio Setup", "フォルダ構造を作成中...", (float)steps / totalSteps);
                    CreateFolderStructure();
                    steps++;
                }

                if (generatePlaceholders)
                {
                    EditorUtility.DisplayProgressBar("Audio Setup", "プレースホルダーを生成中...", (float)steps / totalSteps);
                    GeneratePlaceholders();
                    steps++;
                }

                if (optimizeSettings)
                {
                    EditorUtility.DisplayProgressBar("Audio Setup", "インポート設定を最適化中...", (float)steps / totalSteps);
                    OptimizeAudioSettings();
                    steps++;
                }

                AssetDatabase.Refresh();
                EditorUtility.ClearProgressBar();

                EditorUtility.DisplayDialog(
                    "セットアップ完了",
                    $"オーディオセットアップが完了しました！\n\n" +
                    $"実行された処理:\n" +
                    $"- フォルダ作成: {setupFolders}\n" +
                    $"- プレースホルダー生成: {generatePlaceholders}\n" +
                    $"- 設定最適化: {optimizeSettings}\n\n" +
                    $"次のステップ:\n" +
                    $"1. Assets/Audio/ フォルダに実際の音源を配置\n" +
                    $"2. AudioManager にクリップをアサイン\n" +
                    $"3. AudioMixer を作成して設定",
                    "OK"
                );
            }
            catch (System.Exception e)
            {
                EditorUtility.ClearProgressBar();
                EditorUtility.DisplayDialog("エラー", $"セットアップ中にエラーが発生しました:\n{e.Message}", "OK");
                Debug.LogError($"[AudioSetupTool] Error: {e}");
            }
        }

        private void CreateFolderStructure()
        {
            string baseFolder = "Assets/Audio";
            List<string> folders = new List<string>
            {
                baseFolder,
                $"{baseFolder}/BGM",
                $"{baseFolder}/SFX",
                $"{baseFolder}/SFX/Player",
                $"{baseFolder}/SFX/Enemy",
                $"{baseFolder}/SFX/Item",
                $"{baseFolder}/SFX/UI",
                $"{baseFolder}/SFX/Gacha",
                $"{baseFolder}/SFX/Ambient"
            };

            foreach (string folder in folders)
            {
                if (!AssetDatabase.IsValidFolder(folder))
                {
                    string parentFolder = Path.GetDirectoryName(folder).Replace("\\", "/");
                    string folderName = Path.GetFileName(folder);
                    AssetDatabase.CreateFolder(parentFolder, folderName);
                    Debug.Log($"[AudioSetupTool] Created folder: {folder}");
                }
            }
        }

        private void GeneratePlaceholders()
        {
            // BGMプレースホルダー
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_title.wav", 3.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_dungeon.wav", 5.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_battle.wav", 4.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_boss.wav", 6.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_gameover.wav", 3.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_victory.wav", 2.0f);
            CreatePlaceholderAudioClip("Assets/Audio/BGM/bgm_ending.wav", 4.0f);

            // Player SFX
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Player/player_walk.wav", 0.3f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Player/player_attack.wav", 0.5f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Player/player_damage.wav", 0.4f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Player/player_death.wav", 1.0f);

            // Enemy SFX
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Enemy/enemy_hit.wav", 0.3f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Enemy/enemy_death.wav", 0.8f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Enemy/slime_move.wav", 0.2f);

            // Item SFX
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Item/item_pickup.wav", 0.3f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Item/item_use.wav", 0.4f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Item/potion_drink.wav", 0.5f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Item/equipment_equip.wav", 0.3f);

            // UI SFX
            CreatePlaceholderAudioClip("Assets/Audio/SFX/UI/button_click.wav", 0.1f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/UI/menu_open.wav", 0.2f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/UI/menu_close.wav", 0.2f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/UI/levelup.wav", 1.0f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/UI/notification.wav", 0.3f);

            // Gacha SFX
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Gacha/gacha_start.wav", 0.5f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Gacha/gacha_roll.wav", 2.0f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Gacha/gacha_result_normal.wav", 0.5f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Gacha/gacha_result_rare.wav", 0.8f);
            CreatePlaceholderAudioClip("Assets/Audio/SFX/Gacha/gacha_result_legend.wav", 1.5f);

            Debug.Log("[AudioSetupTool] Generated 29 placeholder audio files");
        }

        private void CreatePlaceholderAudioClip(string path, float duration)
        {
            // WAVファイルのヘッダーを作成（無音）
            int sampleRate = 22050;
            int samples = Mathf.RoundToInt(sampleRate * duration);
            
            // 簡易的なWAVファイル作成（実際には無音データ）
            // 注: これはプレースホルダーなので、実際のオーディオは外部から取得する必要があります
            
            string directory = Path.GetDirectoryName(path);
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            // ダミーファイル作成（実際のWAVデータではなく、識別用のテキスト）
            string content = $"# Audio Placeholder\n# Duration: {duration}s\n# Sample Rate: {sampleRate}Hz\n# Samples: {samples}\n" +
                            $"# This is a placeholder. Replace with actual audio from FREE_AUDIO_ASSETS.md\n";
            File.WriteAllText(path, content);
        }

        private void OptimizeAudioSettings()
        {
            string[] audioGuids = AssetDatabase.FindAssets("t:AudioClip", new[] { "Assets/Audio" });
            int optimized = 0;

            foreach (string guid in audioGuids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                AudioImporter importer = AssetImporter.GetAtPath(path) as AudioImporter;

                if (importer != null)
                {
                    bool isBGM = path.Contains("/BGM/");

                    // WebGL用設定
                    AudioImporterSampleSettings webglSettings = importer.GetOverrideSampleSettings("WebGL");
                    webglSettings.loadType = isBGM ? AudioClipLoadType.CompressedInMemory : AudioClipLoadType.DecompressOnLoad;
                    webglSettings.compressionFormat = AudioCompressionFormat.Vorbis;
                    webglSettings.quality = isBGM ? 0.7f : 1.0f;
                    webglSettings.sampleRateSetting = isBGM ? AudioSampleRateSetting.PreserveSampleRate : AudioSampleRateSetting.OptimizeSampleRate;
                    importer.SetOverrideSampleSettings("WebGL", webglSettings);

                    // デフォルト設定
                    AudioImporterSampleSettings defaultSettings = importer.defaultSampleSettings;
                    defaultSettings.loadType = isBGM ? AudioClipLoadType.CompressedInMemory : AudioClipLoadType.DecompressOnLoad;
                    defaultSettings.compressionFormat = AudioCompressionFormat.Vorbis;
                    defaultSettings.quality = isBGM ? 0.7f : 1.0f;
                    importer.defaultSampleSettings = defaultSettings;

                    importer.forceToMono = !isBGM; // SEはモノラル、BGMはステレオ保持
                    importer.preloadAudioData = !isBGM; // BGMは遅延ロード

                    importer.SaveAndReimport();
                    optimized++;
                }
            }

            Debug.Log($"[AudioSetupTool] Optimized {optimized} audio files");
        }
    }
}
