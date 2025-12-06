# 🛠️ Toolsメニューへのアクセス方法

## 📍 Toolsメニューの場所

Unity Editorの**最上部のメニューバー**にあります：

```
┌────────────────────────────────────────────────────────┐
│ File  Edit  Assets  GameObject  Component  Window  Tools  Help │ ← ここ！
└────────────────────────────────────────────────────────┘
```

---

## ✅ 手順（3ステップ）

### ステップ1: Unity Editorを開く

```
1. Unity Hub を起動
2. Projects リストから "UnityProject" を選択
3. Unity 2022.3 LTS で開く
```

### ステップ2: コンパイル完了を待つ

Unity Editorが開いたら：

```
1. 画面右下の進行状況バーを確認
   "Importing..." や "Compiling..." が表示される
2. 完了するまで待つ（初回は5-10分）
3. Console (Ctrl+Shift+C) でエラーがないことを確認
```

### ステップ3: Toolsメニューをクリック

```
1. 最上部メニューバーの "Tools" をクリック
2. メニューが開く
3. 下の方に "Kokoro no Boukensha" が表示される ← これです！
4. マウスオーバーでサブメニューが開く
```

---

## 🎯 正確なメニューパス

### 完全なメニュー構造

```
Tools
├── (Unity デフォルトメニュー)
├── ...
└── Kokoro no Boukensha ◄─────────── これをクリック！
    ├── Generate All Placeholders
    ├── Audio Setup Tool
    ├── Asset Setup Tool
    ├── Game Balance Tuner
    └── WebGL Build Helper
```

### 各ツールの正確なパス

| ツール名 | メニューパス |
|---------|------------|
| プレースホルダー生成 | `Tools > Kokoro no Boukensha > Generate All Placeholders` |
| オーディオセットアップ | `Tools > Kokoro no Boukensha > Audio Setup Tool` |
| アセットセットアップ | `Tools > Kokoro no Boukensha > Asset Setup Tool` |
| ゲームバランス調整 | `Tools > Kokoro no Boukensha > Game Balance Tuner` |
| WebGLビルド | `Tools > Kokoro no Boukensha > WebGL Build Helper` |

---

## 🖼️ 視覚的ガイド

### Unity Editorの画面レイアウト

```
┌─────────────────────────────────────────────────────────────┐
│ [File] [Edit] [Assets] [GameObject] [Component] [Window] [Tools] [Help] │
│                                                             ↑
│                                                    ここをクリック！
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Hierarchy          Scene/Game View           Inspector     │
│  ├─ Main Camera     ┌────────────────┐       ┌──────────┐  │
│  ├─ Directional Light│                │       │          │  │
│  ├─ GameManager     │                │       │          │  │
│  └─ ...             │                │       │          │  │
│                     └────────────────┘       └──────────┘  │
│                                                              │
│  Project                                Console             │
│  Assets/                                ┌───────────────┐   │
│  ├─ Scenes                              │ 0 errors      │   │
│  ├─ Scripts                             │ 0 warnings    │   │
│  │  ├─ Core                             └───────────────┘   │
│  │  ├─ Editor ← これが重要！                                │
│  │  └─ ...                                                  │
│  └─ ...                                                     │
└─────────────────────────────────────────────────────────────┘
```

### Toolsメニューをクリックした時

```
Tools ◄── クリック
┌───────────────────────────────┐
│ Unity Default Items          │
│ ...                          │
├───────────────────────────────┤
│ Kokoro no Boukensha         ► │ ◄── マウスオーバー
└───────────────────────────────┘
        │
        └──► ┌─────────────────────────────────┐
             │ Generate All Placeholders      │
             │ Audio Setup Tool               │
             │ Asset Setup Tool               │
             │ Game Balance Tuner             │
             │ WebGL Build Helper             │
             └─────────────────────────────────┘
```

---

## ⚠️ メニューが表示されない場合

### 原因1: コンパイルエラー

**確認方法**:
```
1. Window > General > Console を開く (Ctrl+Shift+C)
2. 赤いエラーメッセージがないか確認
```

**エラーがある場合**:
```
- エラーメッセージをコピー
- TROUBLESHOOTING.md を参照
- または QUICK_FIX.md を確認
```

### 原因2: まだコンパイル中

**確認方法**:
```
Unity Editor 右下に進行状況バーが表示されているか確認
"Importing..." や "Compiling..." の表示
```

**対処法**:
```
待つだけです！初回は5-10分かかります。
```

### 原因3: Editorフォルダが正しくない

**確認方法**:
```
Project ウィンドウで以下を確認:
Assets
└── Scripts
    └── Editor ← この名前が正確か確認（大文字小文字も）
        ├── AssetSetupTool.cs
        ├── AudioSetupTool.cs
        ├── GameBalanceTuner.cs
        ├── PlaceholderPrefabGenerator.cs
        └── WebGLBuildHelper.cs
```

**対処法**:
```
フォルダ名が "Editor" でない場合（例: "editor", "Editors"）:
1. フォルダ名を右クリック > Rename
2. 正確に "Editor" に変更（E は大文字）
3. Unity Editorを再起動
```

---

## 🔍 詳細な確認手順

### 1. Projectウィンドウでスクリプトを確認

```
1. Project ウィンドウを開く（通常は下部にある）
2. Assets > Scripts > Editor フォルダを開く
3. 以下の5ファイルがあるか確認:
   ✓ AssetSetupTool.cs
   ✓ AudioSetupTool.cs
   ✓ GameBalanceTuner.cs
   ✓ PlaceholderPrefabGenerator.cs
   ✓ WebGLBuildHelper.cs
```

### 2. スクリプトをダブルクリックして確認

```
1. AssetSetupTool.cs をダブルクリック
2. Visual Studio Code または他のエディタで開く
3. 以下の行があるか確認:
   [MenuItem("Tools/Kokoro no Boukensha/Asset Setup Tool")]
   
これがメニュー登録のコードです！
```

### 3. 強制的に再コンパイル

```
1. Assets > Refresh (Ctrl+R) を実行
2. または Assets > Reimport All を実行
3. Unity Editorを再起動
4. Tools メニューを再確認
```

---

## 🚀 最速の確認方法

### ワンコマンド確認

Unity Editorで以下を実行：

```
1. Alt キーを押しながら Tools をクリック
   （メニューがフラッシュして再読み込み）

2. または Unity Editor を再起動
   File > Exit または Ctrl+Q
   Unity Hub から再度開く
```

---

## 💡 ショートカットキー

Toolsメニューには直接のショートカットはありませんが、以下で高速アクセス可能：

```
Alt + T (Windowsの場合)
Option + T (macOSの場合)

→ Toolsメニューが開く
→ 下矢印キーで "Kokoro no Boukensha" まで移動
→ Enter または 右矢印でサブメニュー展開
→ 上下矢印で選択
→ Enter で実行
```

---

## 🎬 実行例

### 例1: プレースホルダー生成

```
手順:
1. Tools をクリック
2. Kokoro no Boukensha にマウスオーバー
3. Generate All Placeholders をクリック

結果:
- 進行状況ダイアログが表示される
- "Generated 20+ placeholders" とメッセージ
- Assets/Prefabs フォルダに自動生成される
```

### 例2: オーディオセットアップ

```
手順:
1. Tools > Kokoro no Boukensha > Audio Setup Tool

結果:
- ウィンドウが開く
- "セットアップ実行" ボタンをクリック
- Assets/Audio/ フォルダ構造が自動作成
- 29個のプレースホルダーオーディオが生成
```

### 例3: ゲームバランス調整

```
手順:
1. Tools > Kokoro no Boukensha > Game Balance Tuner

結果:
- 調整ウィンドウが開く
- 5つのタブ（Player, Enemies, Items, Gacha, Floors）
- スライダーで値を調整
- "Apply Changes" で適用
```

---

## 📋 チェックリスト

メニューが正常に表示されるための条件：

- [ ] Unity 2022.3 LTS で開いている
- [ ] Assets/Scripts/Editor フォルダが存在
- [ ] Editor フォルダ内に5個の .cs ファイルが存在
- [ ] Console にエラーがない（赤い×マーク）
- [ ] コンパイルが完了している（右下の進行状況バー）
- [ ] Unity Editorが完全に起動している

**全てチェックできれば、Toolsメニューに表示されるはずです！**

---

## 🆘 それでも見つからない場合

### 最終手段: 検索機能

Unity 2022.3以降では検索可能：

```
1. Ctrl+K（Quick Search）
2. "Asset Setup Tool" と入力
3. スクリプトが見つかる
4. ダブルクリックでコードを開く
5. [MenuItem] 属性を確認
```

---

## 📞 サポート

### 関連ドキュメント
- `EDITOR_MENU_GUIDE.md` - 詳細ガイド
- `TROUBLESHOOTING.md` - トラブルシューティング
- `QUICK_FIX.md` - エラー修正

### 確認済みの情報
- ✅ エディタスクリプト: 5ファイル存在確認
- ✅ MenuItem属性: 全ファイルに設定済み
- ✅ フォルダ構造: Assets/Scripts/Editor 正しい配置
- ✅ 名前空間: KokoroNoBoukensha.Editor で統一

**スクリプトは正しく配置されています！Unity Editorで開けばメニューが表示されるはずです。**

---

**作成日**: 2025-12-04  
**対象**: Unity Tools メニューアクセス  
**Unity**: 2022.3 LTS  
**ステータス**: ✅ 全スクリプト確認済み
