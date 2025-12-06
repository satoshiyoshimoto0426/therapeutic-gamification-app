# Unity Editor メニューの確認ガイド

## 📍 「Tools」メニューの場所

### Unity Editorの上部メニューバー

```
File  Edit  Assets  GameObject  Component  Window  Tools  Help
                                                    ↑
                                              ここにあります
```

---

## ⚠️ メニューが表示されない場合

### 原因1: エディタツールがコンパイルされていない

**確認方法**:
```
1. Unity Editorのウィンドウ下部「Console」タブを確認
2. 赤いエラーメッセージがないか確認
```

**解決方法**:
```
1. Window > General > Console を開く (Ctrl+Shift+C)
2. エラーがある場合は内容を確認
3. エラーがなければ、Unity Editorを再起動
```

### 原因2: スクリプトの配置場所が間違っている

**確認方法**:
```
Project ウィンドウで以下のパスを確認:
Assets/Scripts/Editor/ に以下のファイルがあるか:
- AssetSetupTool.cs
- AudioSetupTool.cs
- GameBalanceTuner.cs
- PlaceholderPrefabGenerator.cs
- WebGLBuildHelper.cs
```

**正しい構造**:
```
UnityProject/
└── Assets/
    └── Scripts/
        └── Editor/          ← ここが重要！
            ├── AssetSetupTool.cs
            ├── AudioSetupTool.cs
            ├── GameBalanceTuner.cs
            ├── PlaceholderPrefabGenerator.cs
            └── WebGLBuildHelper.cs
```

### 原因3: Unity Editorのキャッシュ問題

**解決方法**:
```
1. Unity Editorを完全に閉じる
2. 以下のフォルダを削除:
   - UnityProject/Library/
   - UnityProject/Temp/
3. Unity Editorで再度プロジェクトを開く
4. 再コンパイル（5-10分かかります）
```

---

## ✅ 正常な状態の確認

### Toolsメニューの内容

正常にコンパイルされていれば、以下のようなメニューが表示されます:

```
Tools
├── (他のUnityデフォルトメニュー)
└── Kokoro no Boukensha                    ← これが表示される
    ├── Generate All Placeholders
    ├── Audio Setup Tool
    ├── Asset Setup Tool
    ├── Game Balance Tuner
    └── WebGL Build Helper
```

### メニュー項目の説明

| メニュー項目 | 機能 | 推奨実行順 |
|------------|------|----------|
| **Generate All Placeholders** | テスト用3Dモデル20種類を自動生成 | 1番目 |
| **Audio Setup Tool** | オーディオフォルダ作成 + プレースホルダー29個生成 | 2番目 |
| **Asset Setup Tool** | 3DモデルのFBX設定とAnimator自動生成 | 3番目 |
| **Game Balance Tuner** | リアルタイムバランス調整ツール | 必要時 |
| **WebGL Build Helper** | ワンクリックWebGLビルド | ビルド時 |

---

## 🔧 トラブルシューティング手順

### ステップ1: Consoleエラーの確認

```
1. Window > General > Console (Ctrl+Shift+C)
2. 右上の「Clear」ボタンでクリア
3. Assets > Reimport All でスクリプトを再コンパイル
4. エラーが出ないか確認
```

### ステップ2: エディタツールの存在確認

```
1. Project ウィンドウで検索: "t:Script Editor"
2. 以下の5ファイルが見つかるか確認:
   - AssetSetupTool
   - AudioSetupTool
   - GameBalanceTuner
   - PlaceholderPrefabGenerator
   - WebGLBuildHelper
```

### ステップ3: コンパイル強制実行

```
1. Assets > Refresh (Ctrl+R)
2. または Assets > Reimport All
3. Unity Editorの再起動
```

### ステップ4: それでもダメな場合

```bash
# Unity Editorを閉じてから実行
cd /home/user/webapp/UnityProject

# キャッシュ完全削除
rm -rf Library/
rm -rf Temp/
rm -rf obj/

# Unity Editorで再度開く
# 初回コンパイルに5-10分かかります
```

---

## 🎯 代替方法：エディタツールを使わない場合

### 手動でのセットアップ

エディタツールが使えなくても、以下の方法で手動セットアップ可能です：

#### 1. プレースホルダー3Dモデルの手動作成

```
1. GameObject > 3D Object > Cube を作成
2. 名前を "Player_Placeholder" に変更
3. Project > Create > Prefab で保存
4. 同様に敵のプレースホルダーを作成
```

#### 2. オーディオフォルダの手動作成

```
1. Project > Assets 右クリック > Create > Folder
2. フォルダ名: "Audio"
3. Audioフォルダ内に "BGM" と "SFX" フォルダを作成
4. SFX内に "Player", "Enemy", "Item", "UI", "Gacha" フォルダを作成
```

#### 3. GameBalance ScriptableObjectの手動作成

```
1. Project > Assets/Resources フォルダを選択
   （Resourcesフォルダがなければ作成）
2. 右クリック > Create > KokoroNoBoukensha > Game Balance
3. 名前を "GameBalance" に変更
```

---

## 📱 UIからのアクセス（Unity 2022.3）

### Toolsメニューの表示方法

#### 方法1: 上部メニューバー（デフォルト）
```
File - Edit - Assets - GameObject - Component - Window - Tools - Help
                                                         ↑
```

#### 方法2: ウィンドウレイアウトをリセット
```
Window > Layouts > Default
または
Window > Layouts > 2 by 3

これでメニューバーが正しく表示されます
```

#### 方法3: フルスクリーンモードの確認
```
もしフルスクリーンモードになっている場合:
- F11キーでフルスクリーン解除
- または Alt+Enter
```

---

## 🖼️ スクリーンショット参考

### 正常なUnity Editorレイアウト

```
┌─────────────────────────────────────────────────────┐
│ File Edit Assets GameObject ... Window Tools Help  │ ← メニューバー
├─────────────────────────────────────────────────────┤
│                                                     │
│  Hierarchy          Scene View        Inspector   │
│  ├─ Main Camera     ┌──────────┐      ┌────────┐  │
│  ├─ Player          │          │      │        │  │
│  └─ GameManager     │          │      │        │  │
│                     └──────────┘      └────────┘  │
│  Project            Console                        │
│  Assets/            ┌────────────────────────────┐ │
│  ├─ Scripts         │ No errors                  │ │
│  └─ Scenes          └────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## ✅ 確認チェックリスト

正常に動作している場合、以下が全てチェックできます：

- [ ] Unity Editorが開いている
- [ ] 上部に「File Edit Assets ... Tools Help」メニューバーが見える
- [ ] Consoleウィンドウ（下部）にエラーがない
- [ ] Project > Assets/Scripts/Editor フォルダに5ファイルある
- [ ] Toolsメニューをクリックすると「Kokoro no Boukensha」が表示される
- [ ] サブメニューに5項目が表示される

---

## 🆘 緊急対応

### どうしてもメニューが表示されない場合

**スクリプトから直接実行**:

```csharp
// Unity Editorのウィンドウ上部で:
// Window > General > Console を開く
// Consoleの入力欄（存在しない場合はスクリプトから）

// プレースホルダー生成を実行
var generator = new KokoroNoBoukensha.Editor.PlaceholderPrefabGenerator();
generator.GenerateAllPlaceholders();

// オーディオセットアップを実行
var audioSetup = new KokoroNoBoukensha.Editor.AudioSetupTool();
audioSetup.SetupAudio();
```

ただし、これは通常の方法ではありません。

---

## 📞 サポート情報

### 関連ドキュメント
- `TROUBLESHOOTING.md` - トラブルシューティング全般
- `QUICK_FIX.md` - Unity Tutorial エラー修正
- `README.md` - プロジェクト概要

### 確認が必要な情報

問題が解決しない場合、以下を確認してください：

1. **Unity バージョン**: 2022.3 LTS が推奨
2. **OS**: Windows / macOS / Linux
3. **Consoleエラー**: 具体的なエラーメッセージ
4. **フォルダ構造**: Assets/Scripts/Editor/ の存在

---

**作成日**: 2025-12-04  
**対象**: Unity Editor メニューの確認  
**推奨Unity**: 2022.3 LTS  
**プロジェクト**: 心の冒険者 - Unity 3Dローグライク
