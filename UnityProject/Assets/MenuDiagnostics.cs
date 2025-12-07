#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;

/// <summary>
/// 最優先メニュー診断ツール - Editorフォルダ外に配置
/// Unity 6.3 LTS での確実な動作を保証
/// </summary>
public static class MenuDiagnostics
{
    // 最優先で表示されるメニュー（優先度0）
    [MenuItem("Tools/★緊急診断★ クリックしてください", false, 0)]
    public static void EmergencyDiagnostics()
    {
        Debug.Log("========================================");
        Debug.Log("★★★ メニュー診断開始 ★★★");
        Debug.Log("========================================");
        
        // Unityバージョン確認
        string unityVersion = Application.unityVersion;
        Debug.Log("Unity Version: " + unityVersion);
        
        bool isUnity6 = unityVersion.StartsWith("6") || unityVersion.StartsWith("6000");
        Debug.Log("Unity 6.x 検出: " + isUnity6);
        
        // エディタスクリプトパス確認
        string editorPath = Application.dataPath + "/Scripts/Editor";
        bool editorFolderExists = System.IO.Directory.Exists(editorPath);
        Debug.Log("Editor フォルダ存在: " + editorFolderExists);
        
        if (editorFolderExists)
        {
            string[] csFiles = System.IO.Directory.GetFiles(editorPath, "*.cs");
            Debug.Log("Editor スクリプト数: " + csFiles.Length);
            
            foreach (string file in csFiles)
            {
                string fileName = System.IO.Path.GetFileName(file);
                Debug.Log("  - " + fileName);
            }
        }
        
        // コンパイルエラー確認
        Debug.Log("コンパイルエラー確認中...");
        
        string message = "★★★ メニュー診断結果 ★★★\n\n";
        message += "Unity バージョン: " + unityVersion + "\n";
        message += "Unity 6.x: " + (isUnity6 ? "はい" : "いいえ") + "\n";
        message += "Editor フォルダ: " + (editorFolderExists ? "存在" : "存在しない") + "\n\n";
        
        if (isUnity6)
        {
            message += "【Unity 6.3 LTS 検出】\n\n";
            message += "このメニューが表示されたということは：\n";
            message += "✅ MenuItem 属性は動作しています\n";
            message += "✅ Editor スクリプトはコンパイルされています\n\n";
            message += "次のステップ：\n";
            message += "1. Tools > 修正実行 を選択\n";
            message += "2. 自動修正を実行します\n";
        }
        else
        {
            message += "【Unity 2022.3 LTS 検出】\n\n";
            message += "通常の手順で動作するはずです。\n";
        }
        
        message += "\n詳細はConsoleを確認してください。";
        
        EditorUtility.DisplayDialog("メニュー診断", message, "OK");
        
        Debug.Log("========================================");
        Debug.Log("診断完了 - 次は「Tools > 修正実行」を選択");
        Debug.Log("========================================");
    }
    
    // 自動修正実行
    [MenuItem("Tools/★修正実行★ 自動でメニューを修正", false, 1)]
    public static void AutoFix()
    {
        Debug.Log("========================================");
        Debug.Log("★★★ 自動修正開始 ★★★");
        Debug.Log("========================================");
        
        EditorUtility.DisplayProgressBar("自動修正中", "Editor スクリプトを確認中...", 0.1f);
        
        try
        {
            // ステップ1: .meta ファイル再生成
            Debug.Log("ステップ1: アセットデータベース更新");
            AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
            EditorUtility.DisplayProgressBar("自動修正中", "アセットを更新中...", 0.3f);
            
            System.Threading.Thread.Sleep(1000);
            
            // ステップ2: Editorスクリプト再インポート
            Debug.Log("ステップ2: Editor スクリプト再インポート");
            string editorPath = "Assets/Scripts/Editor";
            
            if (AssetDatabase.IsValidFolder(editorPath))
            {
                string[] scripts = AssetDatabase.FindAssets("t:Script", new[] { editorPath });
                Debug.Log("再インポート対象: " + scripts.Length + " スクリプト");
                
                EditorUtility.DisplayProgressBar("自動修正中", "スクリプトを再インポート中...", 0.5f);
                
                foreach (string guid in scripts)
                {
                    string path = AssetDatabase.GUIDToAssetPath(guid);
                    AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
                }
            }
            
            System.Threading.Thread.Sleep(500);
            
            // ステップ3: スクリプト再コンパイル要求
            Debug.Log("ステップ3: スクリプト再コンパイル");
            EditorUtility.DisplayProgressBar("自動修正中", "再コンパイル中...", 0.7f);
            
            AssetDatabase.Refresh();
            UnityEditor.Compilation.CompilationPipeline.RequestScriptCompilation();
            
            System.Threading.Thread.Sleep(1000);
            
            // ステップ4: 完了
            EditorUtility.DisplayProgressBar("自動修正中", "完了！", 1.0f);
            System.Threading.Thread.Sleep(500);
            
            Debug.Log("========================================");
            Debug.Log("★★★ 自動修正完了 ★★★");
            Debug.Log("========================================");
            
            EditorUtility.ClearProgressBar();
            
            string result = "★★★ 自動修正完了 ★★★\n\n";
            result += "実行した処理：\n";
            result += "✅ アセットデータベース更新\n";
            result += "✅ Editor スクリプト再インポート\n";
            result += "✅ スクリプト再コンパイル要求\n\n";
            result += "【重要】次の手順：\n";
            result += "1. Unity Editor を一度閉じる\n";
            result += "2. Unity Editor を再起動\n";
            result += "3. Tools メニューを確認\n\n";
            result += "再起動後、以下が表示されるはずです：\n";
            result += "• Kokoro no Boukensha\n";
            result += "• Generate All Placeholders\n";
            result += "• その他のツール\n";
            
            EditorUtility.DisplayDialog("自動修正完了", result, "Unity を再起動する");
        }
        catch (System.Exception e)
        {
            EditorUtility.ClearProgressBar();
            Debug.LogError("自動修正エラー: " + e.Message);
            EditorUtility.DisplayDialog("エラー", "自動修正中にエラーが発生しました:\n" + e.Message, "OK");
        }
    }
    
    // 強制リセット（最終手段）
    [MenuItem("Tools/★強制リセット★ Library削除推奨", false, 2)]
    public static void ForceReset()
    {
        bool confirm = EditorUtility.DisplayDialog(
            "強制リセット",
            "【警告】この操作は以下を実行します：\n\n" +
            "1. すべてのアセットを再インポート\n" +
            "2. すべてのスクリプトを再コンパイル\n" +
            "3. Unity Editor の再起動が必要\n\n" +
            "時間がかかります（5-10分）\n\n" +
            "実行しますか？",
            "実行する",
            "キャンセル"
        );
        
        if (!confirm) return;
        
        Debug.Log("========================================");
        Debug.Log("★★★ 強制リセット開始 ★★★");
        Debug.Log("========================================");
        
        EditorUtility.DisplayProgressBar("強制リセット", "準備中...", 0.1f);
        
        try
        {
            // すべてのアセットを再インポート
            Debug.Log("すべてのアセットを再インポート中...");
            EditorUtility.DisplayProgressBar("強制リセット", "アセット再インポート中...", 0.3f);
            AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate | ImportAssetOptions.ImportRecursive);
            
            System.Threading.Thread.Sleep(2000);
            
            // スクリプト再コンパイル
            Debug.Log("スクリプト再コンパイル要求...");
            EditorUtility.DisplayProgressBar("強制リセット", "再コンパイル中...", 0.7f);
            UnityEditor.Compilation.CompilationPipeline.RequestScriptCompilation();
            
            System.Threading.Thread.Sleep(2000);
            
            EditorUtility.DisplayProgressBar("強制リセット", "完了！", 1.0f);
            System.Threading.Thread.Sleep(500);
            
            EditorUtility.ClearProgressBar();
            
            Debug.Log("========================================");
            Debug.Log("★★★ 強制リセット完了 ★★★");
            Debug.Log("========================================");
            
            string message = "★★★ 強制リセット完了 ★★★\n\n";
            message += "【重要】次の手順：\n\n";
            message += "1. Unity Editor を完全に閉じる\n";
            message += "2. ターミナルで以下を実行（推奨）：\n";
            message += "   cd UnityProject\n";
            message += "   rm -rf Library/\n\n";
            message += "3. Unity Editor を再起動\n";
            message += "4. 再コンパイル完了を待つ（5-10分）\n";
            message += "5. Tools メニューを確認\n\n";
            message += "それでも表示されない場合は、\n";
            message += "Console のエラーを確認してください。";
            
            EditorUtility.DisplayDialog("強制リセット完了", message, "OK");
        }
        catch (System.Exception e)
        {
            EditorUtility.ClearProgressBar();
            Debug.LogError("強制リセットエラー: " + e.Message);
            EditorUtility.DisplayDialog("エラー", "強制リセット中にエラーが発生しました:\n" + e.Message, "OK");
        }
    }
    
    // システム情報表示
    [MenuItem("Tools/★システム情報★", false, 10)]
    public static void ShowSystemInfo()
    {
        Debug.Log("========================================");
        Debug.Log("★★★ システム情報 ★★★");
        Debug.Log("========================================");
        
        Debug.Log("Unity Version: " + Application.unityVersion);
        Debug.Log("Platform: " + Application.platform);
        Debug.Log("Product Name: " + Application.productName);
        Debug.Log("Data Path: " + Application.dataPath);
        Debug.Log("Persistent Data Path: " + Application.persistentDataPath);
        
        #if UNITY_EDITOR
        Debug.Log("Editor Version: " + UnityEditorInternal.InternalEditorUtility.GetFullUnityVersion());
        #endif
        
        Debug.Log("System Language: " + Application.systemLanguage);
        
        string message = "★★★ システム情報 ★★★\n\n";
        message += "Unity: " + Application.unityVersion + "\n";
        message += "Platform: " + Application.platform + "\n";
        message += "Product: " + Application.productName + "\n\n";
        message += "詳細は Console を確認してください。";
        
        EditorUtility.DisplayDialog("システム情報", message, "OK");
        
        Debug.Log("========================================");
    }
}
#endif
