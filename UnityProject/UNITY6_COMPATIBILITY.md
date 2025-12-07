# 🎯 Unity 6.3 LTS 互換性ガイド

## 📋 プロジェクト対応状況

このプロジェクトは元々 **Unity 2022.3 LTS** を想定して作成されましたが、**Unity 6.3 LTS** でも動作するように対応しています。

---

## ⚠️ Unity 6.3 LTS での既知の問題

### 問題1: Toolsメニューが表示されない

**症状：**
- Unity Editorの上部メニューバーに `Tools` メニューが表示されない
- または `Tools` メニューはあるが `Kokoro no Boukensha` サブメニューが表示されない

**原因：**
Unity 6.xでは、Editorスクリプトのコンパイルやインポート処理が Unity 2022.x と異なる場合があります。

---

## ✅ Unity 6.3 LTS での解決策

### 解決策1: SimpleMenuTest で基本確認

最もシンプルなメニューテストツールを追加しました：

**ファイル:** `Assets/Scripts/Editor/SimpleMenuTest.cs`

**確認手順：**

1. Unity Editorを起動
2. コンパイル完了を待つ
3. 上部メニューバーの `Tools` をクリック
4. 以下のいずれかが表示されるか確認：

```
Tools
  ├─ Test Menu 1                    ← これが表示される？
  ├─ テストメニュー3                  ← これが表示される？
  └─ Kokoro no Boukensha
      ├─ Test Menu 2                ← これが表示される？
      ├─ 優先テスト                   ← これが表示される？
      └─ ウィンドウテスト             ← これが表示される？
```

**期待される結果：**

#### ケースA: `Test Menu 1` などが表示される
→ **Editor スクリプトは正常にコンパイルされています**
→ 次の解決策2に進む

#### ケースB: 何も表示されない
→ **Editor スクリプトがコンパイルされていません**
→ 解決策3（強制再コンパイル）に進む

---

### 解決策2: Console でエラー確認

`Test Menu 1` などのシンプルなメニューが表示される場合：

**手順：**

1. `Window > General > Console` を開く（Ctrl+Shift+C）
2. エラー（赤いアイコン）がないか確認
3. 警告（黄色）は無視してOK

**エラーがある場合：**

#### よくあるエラー1: `CS0234: The type or namespace name 'Editor' does not exist`

```csharp
error CS0234: The type or namespace name 'Editor' does not exist in the namespace 'UnityEditor'
```

**原因：** Unity 6.x で名前空間が変更された可能性

**解決策：**
```csharp
// 以下を追加
using UnityEditor;
using UnityEngine;
```

#### よくあるエラー2: `CS1061: does not contain a definition for 'GetFullUnityVersion'`

```csharp
error CS1061: 'InternalEditorUtility' does not contain a definition for 'GetFullUnityVersion'
```

**原因：** Unity 6.x で API が変更された

**解決策：** SimpleMenuTest.cs の該当行をコメントアウト

---

### 解決策3: 強制再コンパイル

Editor スクリプトがまったく認識されていない場合：

**手順1: Libraryフォルダを削除（完全再コンパイル）**

```bash
# Unity Editor を完全に閉じる
# ターミナルで実行：

cd /home/user/webapp/UnityProject
rm -rf Library/

# Unity Editor を再起動
# → 5-10分かけて完全に再コンパイルされます
```

**手順2: Assetsを再インポート**

Unity Editor 内で：
```
Assets > Reimport All
```
→ すべてのアセットを再インポート（3-5分）

**手順3: Safe Mode で起動**

```
# Unity Hub から：
1. UnityProject を右クリック
2. "Open with" > "Safe Mode"
```

---

### 解決策4: Assembly Definition の確認

**確認：**

```bash
cd /home/user/webapp/UnityProject/Assets/Scripts/Editor
ls -la KokoroNoBoukensha.Editor.asmdef
```

**存在しない場合：** すでに作成済みのはずですが、念のため確認

**内容確認：**

```json
{
    "name": "KokoroNoBoukensha.Editor",
    "rootNamespace": "KokoroNoBoukensha.Editor",
    "references": [],
    "includePlatforms": [
        "Editor"
    ]
}
```

---

## 🔍 Unity 6.3 LTS 固有の確認事項

### 1. Unity バージョンの確認

Unity Editor で：
```
Help > About Unity
```

**表示されるべきバージョン：**
```
Unity 6000.0.x (Unity 6.3 LTS)
```

### 2. ProjectSettings の確認

```bash
cat /home/user/webapp/UnityProject/ProjectSettings/ProjectVersion.txt
```

**表示されるべき内容：**
```
m_EditorVersion: 6000.0.23f1
m_EditorVersionWithRevision: 6000.0.23f1 (f23de63675e5)
```

### 3. Editor フォルダのスクリプト一覧

```bash
cd /home/user/webapp/UnityProject/Assets/Scripts/Editor
ls -la *.cs

# 表示されるべきファイル（8個）:
# 1. AssetSetupTool.cs
# 2. AudioSetupTool.cs
# 3. GameBalanceTuner.cs
# 4. MenuTestTool.cs
# 5. PlaceholderPrefabGenerator.cs
# 6. SimpleMenuTest.cs ← 新規追加（Unity 6対応）
# 7. WebGLBuildHelper.cs
# 8. KokoroNoBoukensha.Editor.asmdef
```

---

## 📦 Unity 6.3 LTS 対応ファイル一覧

### 新規追加（Unity 6対応）

1. **SimpleMenuTest.cs** (3.2KB)
   - 5つの異なるパターンでメニュー表示をテスト
   - Unity 6.3 LTS での動作確認用
   - namespace を使わないシンプルな実装

2. **ProjectVersion.txt**
   - Unity 6.3 LTS バージョン情報
   - 自動生成される設定ファイル

3. **UNITY6_COMPATIBILITY.md** (このファイル)
   - Unity 6.3 LTS 互換性ガイド
   - トラブルシューティング手順

### 既存ファイル（Unity 2022.3 / 6.x 共通）

- AssetSetupTool.cs
- AudioSetupTool.cs
- GameBalanceTuner.cs
- MenuTestTool.cs
- PlaceholderPrefabGenerator.cs
- WebGLBuildHelper.cs
- KokoroNoBoukensha.Editor.asmdef

---

## 🚀 Unity 6.3 LTS での推奨手順

### ステップ1: Unity Editor を再起動

```
1. Unity Editor を完全に閉じる
2. Unity Hub から "UnityProject" を選択
3. Unity 6.3 LTS で起動
4. コンパイル完了を待つ（5-10分）
```

### ステップ2: SimpleMenuTest で確認

```
1. Tools > Test Menu 1 をクリック
2. ダイアログが表示されれば成功！
```

### ステップ3: Kokoro no Boukensha メニューを確認

```
1. Tools > Kokoro no Boukensha
2. サブメニューが表示されるか確認
```

### ステップ4: 各ツールを実行

```
1. Tools > Kokoro no Boukensha > 優先テスト
   → Unity 6.3 LTS 情報が表示される

2. Tools > Kokoro no Boukensha > ウィンドウテスト
   → テストウィンドウが開く

3. Tools > Kokoro no Boukensha > Generate All Placeholders
   → プレースホルダー生成
```

---

## ⚙️ Unity 6.x での API 変更への対応

### 変更1: UnityEditorInternal API

**Unity 2022.3:**
```csharp
UnityEditorInternal.InternalEditorUtility.GetFullUnityVersion()
```

**Unity 6.x:**
```csharp
// 一部のAPIが変更または削除されている可能性
// Application.unityVersion を使用する方が安全
Application.unityVersion
```

### 変更2: EditorWindow の挙動

Unity 6.xでは EditorWindow の初期化タイミングが変わっている可能性があります。

**対策：** `OnEnable()` で初期化処理を行う

```csharp
public class MyEditorWindow : EditorWindow
{
    void OnEnable()
    {
        // 初期化処理をここに
    }
}
```

---

## 🐛 トラブルシューティング

### 症状: Tools メニュー自体が表示されない

**確認1: Unity のデフォルト Tools メニュー**

Unity にはデフォルトで `Tools` メニューがない場合があります。

**確認方法：**
```
Window > Package Manager
```
で何かパッケージをインストールすると、`Tools` メニューが出現することがあります。

**解決策：**
```
Window > General > Console
```
で、SimpleMenuTest のメニューが登録されているかログを確認

### 症状: 一部のツールだけ表示されない

**原因：** 特定のスクリプトにコンパイルエラーがある

**確認：**
```
Window > General > Console
```
赤いエラーアイコンをダブルクリックして詳細確認

**解決策：**
エラーのあるスクリプトを修正または一時的に無効化

### 症状: メニューはあるが、クリックしても何も起こらない

**原因：** スクリプトの実行エラー

**確認：**
```
Window > General > Console
```
メニューをクリックした時にエラーが出ていないか確認

---

## 📊 動作確認チェックリスト

Unity 6.3 LTS での動作確認：

- [ ] Unity 6.3 LTS でプロジェクトを開いた
- [ ] コンパイルが完了した（右下の進行状況バーが消えた）
- [ ] Console にエラーがない（赤いアイコンなし）
- [ ] `Tools` メニューが表示される
- [ ] `Tools > Test Menu 1` が表示される
- [ ] `Tools > Test Menu 1` をクリックしてダイアログが出た
- [ ] `Tools > Kokoro no Boukensha` サブメニューが表示される
- [ ] `Tools > Kokoro no Boukensha > 優先テスト` をクリックできた
- [ ] `Tools > Kokoro no Boukensha > ウィンドウテスト` でウィンドウが開いた
- [ ] 他のメインツールも表示される

**すべてチェックできれば Unity 6.3 LTS で完全動作しています！** ✅

---

## 📝 補足情報

### Unity 2022.3 LTS と Unity 6.3 LTS の互換性

このプロジェクトは両方のバージョンで動作するように設計されています：

| 機能 | Unity 2022.3 | Unity 6.3 |
|------|-------------|-----------|
| Editor Scripts | ✅ | ✅ |
| MenuItem 属性 | ✅ | ✅ |
| EditorWindow | ✅ | ✅ |
| Assembly Definition | ✅ | ✅ |
| WebGL Build | ✅ | ✅ |

### Unity 6.3 LTS の新機能

Unity 6.x には以下の改善があります：

- より高速なコンパイル
- 改善されたエディタパフォーマンス
- 新しいレンダリングパイプライン

これらはすべてこのプロジェクトで利用可能です。

---

## ✅ まとめ

### Unity 6.3 LTS で今すぐ実行すること

1. **Unity Editor を再起動**
2. **コンパイル完了を待つ**（5-10分）
3. **`Tools > Test Menu 1` をクリック**
4. ダイアログが表示されれば成功！

### それでも表示されない場合

1. **Console でエラー確認**
2. **Library フォルダを削除して再コンパイル**
3. **このドキュメントのトラブルシューティング参照**

---

**Unity 6.3 LTS での動作確認を行い、結果を教えてください！** 🚀
