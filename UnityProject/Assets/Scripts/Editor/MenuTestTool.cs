using UnityEngine;
using UnityEditor;

namespace KokoroNoBoukensha.Editor
{
    /// <summary>
    /// メニュー表示テスト用の最小限のツール
    /// このメニューが表示されれば、Editorスクリプトが正常にコンパイルされています
    /// </summary>
    public static class MenuTestTool
    {
        [MenuItem("Tools/Kokoro no Boukensha/【テスト】メニュー表示確認")]
        public static void TestMenu()
        {
            EditorUtility.DisplayDialog(
                "成功！", 
                "Tools > Kokoro no Boukensha メニューが正常に表示されています！\n\n" +
                "このメニューが見える場合：\n" +
                "✅ Editorスクリプトが正常にコンパイルされています\n" +
                "✅ 他のツールも利用可能です\n\n" +
                "5つのエディタツールが使えます：\n" +
                "1. Generate All Placeholders\n" +
                "2. Audio Setup Tool\n" +
                "3. Asset Setup Tool\n" +
                "4. Game Balance Tuner\n" +
                "5. WebGL Build Helper",
                "OK"
            );
            
            Debug.Log("===== Kokoro no Boukensha Editor Tools =====");
            Debug.Log("✅ メニューテスト成功！");
            Debug.Log("利用可能なツール：");
            Debug.Log("  1. Generate All Placeholders");
            Debug.Log("  2. Audio Setup Tool");
            Debug.Log("  3. Asset Setup Tool");
            Debug.Log("  4. Game Balance Tuner");
            Debug.Log("  5. WebGL Build Helper");
            Debug.Log("==========================================");
        }

        [MenuItem("Tools/Kokoro no Boukensha/【ヘルプ】ツールの使い方")]
        public static void ShowHelp()
        {
            string helpMessage = @"心の冒険者 - エディタツール ヘルプ

【基本的な使い方】

1. Generate All Placeholders
   → テスト用プレースホルダー（仮モデル）を一括生成
   → 最初に実行してください

2. Audio Setup Tool
   → オーディオフォルダとプレースホルダーを作成
   → Window として開きます

3. Asset Setup Tool
   → 3Dモデルの自動セットアップ
   → Window として開きます

4. Game Balance Tuner
   → ゲームバランス調整ツール
   → Window として開きます

5. WebGL Build Helper
   → ワンクリックWebGLビルド
   → Window として開きます

【推奨実行順序】
1. Generate All Placeholders （プレースホルダー生成）
2. Audio Setup Tool （オーディオ設定）
3. Game Balance Tuner でバランス調整
4. WebGL Build Helper でビルド

【詳細ドキュメント】
UnityProject/ フォルダ内の以下を参照：
- HOW_TO_ACCESS_TOOLS.md
- EDITOR_MENU_GUIDE.md
- WEBGL_BUILD_INSTRUCTIONS.md
";

            EditorUtility.DisplayDialog("エディタツール ヘルプ", helpMessage, "OK");
            Debug.Log(helpMessage);
        }
    }
}
