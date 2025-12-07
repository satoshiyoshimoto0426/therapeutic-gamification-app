using UnityEngine;
using UnityEditor;

/// <summary>
/// Unity 6.x 対応の最小限メニューテスト
/// </summary>
public static class SimpleMenuTest
{
    // パターン1: 最もシンプルな形式
    [MenuItem("Tools/Test Menu 1")]
    static void TestMenu1()
    {
        Debug.Log("Test Menu 1 clicked!");
        EditorUtility.DisplayDialog("Success", "Test Menu 1 is working!", "OK");
    }

    // パターン2: Kokoro no Boukensha 形式
    [MenuItem("Tools/Kokoro no Boukensha/Test Menu 2")]
    static void TestMenu2()
    {
        Debug.Log("Test Menu 2 clicked!");
        EditorUtility.DisplayDialog("Success", "Test Menu 2 is working!", "OK");
    }

    // パターン3: 日本語メニュー
    [MenuItem("Tools/テストメニュー3")]
    static void TestMenu3()
    {
        Debug.Log("Test Menu 3 clicked!");
        EditorUtility.DisplayDialog("成功", "テストメニュー3が動作しています！", "OK");
    }

    // パターン4: 優先度指定
    [MenuItem("Tools/Kokoro no Boukensha/優先テスト", false, 0)]
    static void TestMenu4()
    {
        Debug.Log("Priority Test Menu clicked!");
        
        string message = "Unity 6.3 LTS で正常に動作しています！\n\n";
        message += "Editor スクリプトの確認：\n";
        message += "✅ MenuItem 属性が認識されています\n";
        message += "✅ Tools メニューが表示されています\n";
        message += "✅ Kokoro no Boukensha サブメニューが機能しています\n\n";
        message += "他のツールも利用可能になっているはずです。";
        
        EditorUtility.DisplayDialog("Unity 6.3 LTS 対応確認", message, "OK");
        
        // Consoleに詳細情報を出力
        Debug.Log("===== Unity 6.3 LTS Editor Menu Test =====");
        Debug.Log("Unity Version: " + Application.unityVersion);
        Debug.Log("Editor Version: " + UnityEditorInternal.InternalEditorUtility.GetFullUnityVersion());
        Debug.Log("Platform: " + Application.platform);
        Debug.Log("==========================================");
    }

    // パターン5: EditorWindowを開く形式
    [MenuItem("Tools/Kokoro no Boukensha/ウィンドウテスト")]
    static void OpenTestWindow()
    {
        var window = EditorWindow.GetWindow<TestEditorWindow>("テストウィンドウ");
        window.Show();
    }

    // テスト用EditorWindow
    public class TestEditorWindow : EditorWindow
    {
        void OnGUI()
        {
            GUILayout.Label("Unity 6.3 LTS テストウィンドウ", EditorStyles.boldLabel);
            
            EditorGUILayout.Space();
            
            EditorGUILayout.HelpBox(
                "このウィンドウが表示されれば、EditorWindow も正常に動作しています。",
                MessageType.Info
            );
            
            EditorGUILayout.Space();
            
            if (GUILayout.Button("Unity バージョン情報"))
            {
                Debug.Log("Unity Version: " + Application.unityVersion);
                EditorUtility.DisplayDialog(
                    "バージョン情報",
                    "Unity Version: " + Application.unityVersion,
                    "OK"
                );
            }
            
            if (GUILayout.Button("Console に情報を出力"))
            {
                Debug.Log("===== Editor Window Test =====");
                Debug.Log("Unity Version: " + Application.unityVersion);
                Debug.Log("Editor: " + UnityEditorInternal.InternalEditorUtility.GetFullUnityVersion());
                Debug.Log("============================");
            }
        }
    }
}
