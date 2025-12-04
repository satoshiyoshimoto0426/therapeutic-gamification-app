using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// WebGLビルドを簡略化するヘルパーツール
    /// Tools > Kokoro no Boukensha > WebGL Build Helper
    /// </summary>
    public class WebGLBuildHelper : EditorWindow
    {
        private string buildPath = "WebGLBuild";
        private bool developmentBuild = false;
        private bool autoRunAfterBuild = true;
        private Vector2 scrollPosition;

        [MenuItem("Tools/Kokoro no Boukensha/WebGL Build Helper")]
        public static void ShowWindow()
        {
            GetWindow<WebGLBuildHelper>("WebGL Build Helper");
        }

        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

            GUILayout.Label("WebGL Build Helper", EditorStyles.boldLabel);
            GUILayout.Space(10);

            EditorGUILayout.HelpBox(
                "このツールはWebGLビルドを簡単に実行できます。\n" +
                "ビルド前に最適化設定を自動適用します。",
                MessageType.Info
            );

            GUILayout.Space(10);

            // 設定
            GUILayout.Label("ビルド設定", EditorStyles.boldLabel);
            buildPath = EditorGUILayout.TextField("ビルドパス", buildPath);
            developmentBuild = EditorGUILayout.Toggle("Development Build", developmentBuild);
            autoRunAfterBuild = EditorGUILayout.Toggle("ビルド後に実行", autoRunAfterBuild);

            GUILayout.Space(20);

            // ボタン
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("最適化設定を適用", GUILayout.Height(30)))
            {
                ApplyOptimizations();
            }
            EditorGUILayout.EndHorizontal();

            GUILayout.Space(10);

            if (GUILayout.Button("WebGLビルド実行", GUILayout.Height(40)))
            {
                BuildWebGL();
            }

            GUILayout.Space(20);

            // 情報表示
            GUILayout.Label("現在の設定", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                $"Platform: {EditorUserBuildSettings.activeBuildTarget}\n" +
                $"Compression: {PlayerSettings.WebGL.compressionFormat}\n" +
                $"Memory Size: {PlayerSettings.WebGL.memorySize} MB\n" +
                $"Code Stripping: {PlayerSettings.stripEngineCode}\n" +
                $"IL2CPP: {PlayerSettings.GetScriptingBackend(BuildTargetGroup.WebGL)}",
                MessageType.None
            );

            EditorGUILayout.EndScrollView();
        }

        private void ApplyOptimizations()
        {
            if (EditorUtility.DisplayDialog(
                "最適化設定の適用",
                "WebGL向けの最適化設定を適用しますか？\n\n" +
                "以下の設定が変更されます:\n" +
                "- Compression Format: Brotli\n" +
                "- Memory Size: 512 MB\n" +
                "- Code Stripping: High\n" +
                "- Color Space: Gamma\n" +
                "- Quality Settings: Medium",
                "適用", "キャンセル"))
            {
                // Player Settings
                PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
                PlayerSettings.WebGL.memorySize = 512;
                PlayerSettings.WebGL.decompressionFallback = true;
                PlayerSettings.WebGL.dataCaching = true;
                PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.None;

                PlayerSettings.stripEngineCode = true;
                PlayerSettings.SetManagedStrippingLevel(BuildTargetGroup.WebGL, ManagedStrippingLevel.High);
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.WebGL, ScriptingImplementation.IL2CPP);

                PlayerSettings.colorSpace = ColorSpace.Gamma;

                // Quality Settings
                QualitySettings.SetQualityLevel(2); // Medium (0=Low, 1=Medium, 2=High)

                Debug.Log("[WebGLBuildHelper] Optimization settings applied");
                EditorUtility.DisplayDialog("完了", "最適化設定を適用しました！", "OK");
            }
        }

        private void BuildWebGL()
        {
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.WebGL)
            {
                if (EditorUtility.DisplayDialog(
                    "Platform切り替え",
                    "現在のPlatformはWebGLではありません。\nWebGLに切り替えますか？",
                    "切り替える", "キャンセル"))
                {
                    EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.WebGL, BuildTarget.WebGL);
                }
                else
                {
                    return;
                }
            }

            // ビルド対象シーンを取得
            string[] scenes = EditorBuildSettingsScene.GetActiveSceneList(EditorBuildSettings.scenes);

            if (scenes.Length == 0)
            {
                EditorUtility.DisplayDialog("エラー", "ビルド対象シーンが設定されていません。\nFile > Build Settings でシーンを追加してください。", "OK");
                return;
            }

            // ビルドオプション
            BuildPlayerOptions buildOptions = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = buildPath,
                target = BuildTarget.WebGL,
                options = developmentBuild ? BuildOptions.Development : BuildOptions.None
            };

            Debug.Log($"[WebGLBuildHelper] Starting WebGL build to: {buildPath}");
            Debug.Log($"[WebGLBuildHelper] Scenes: {string.Join(", ", scenes)}");

            // ビルド実行
            BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
            BuildSummary summary = report.summary;

            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[WebGLBuildHelper] Build succeeded: {summary.totalSize} bytes in {summary.totalTime}");
                
                string message = $"ビルドが完了しました！\n\n" +
                               $"サイズ: {summary.totalSize / (1024 * 1024)} MB\n" +
                               $"時間: {summary.totalTime}\n" +
                               $"場所: {buildPath}";

                if (autoRunAfterBuild)
                {
                    message += "\n\nブラウザで開きますか？";
                    if (EditorUtility.DisplayDialog("ビルド成功", message, "開く", "閉じる"))
                    {
                        string indexPath = System.IO.Path.Combine(buildPath, "index.html");
                        Application.OpenURL($"file://{System.IO.Path.GetFullPath(indexPath)}");
                    }
                }
                else
                {
                    EditorUtility.DisplayDialog("ビルド成功", message, "OK");
                }
            }
            else if (summary.result == BuildResult.Failed)
            {
                Debug.LogError($"[WebGLBuildHelper] Build failed");
                EditorUtility.DisplayDialog("ビルド失敗", "ビルドが失敗しました。\nConsoleログを確認してください。", "OK");
            }
        }
    }
}
