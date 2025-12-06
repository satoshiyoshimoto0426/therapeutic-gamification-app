# 🔧 Toolsメニューが表示されない問題の解決方法

## 問題の原因

Toolsメニューが表示されない主な原因：

1. **Editorスクリプトのコンパイルエラー**
2. **Unity Editorの再起動が必要**
3. **Assembly Definition（.asmdef）ファイルの不足**
4. **スクリプトのインポートが完了していない**

---

## 🎯 今回の修正内容

以下のファイルを新規追加しました：

### 1. Assembly Definition ファイル
**ファイル:** `Assets/Scripts/Editor/KokoroNoBoukensha.Editor.asmdef`

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

**役割：**
- Editorスクリプトを独立したアセンブリとして定義
- コンパイルを最適化し、Editorツールの読み込みを確実にする
- Unity 2022.3 LTSでの推奨設定

### 2. メニュー表示テストツール
**ファイル:** `Assets/Scripts/Editor/MenuTestTool.cs`

**機能：**
- **`【テスト】メニュー表示確認`** - メニューが正常に表示されているか確認
- **`【ヘルプ】ツールの使い方`** - 各ツールの使い方を表示

**使い方：**
```
Tools > Kokoro no Boukensha > 【テスト】メニュー表示確認
```

このメニューが見える = すべてのツールが利用可能！

---

## ✅ 解決手順（必須）

### 手順1: Unity Editorを完全に閉じる

**重要：** ファイルを追加したので、完全な再起動が必要です。

```bash
# Unity Editor を完全に終了してください
# 画面右上の × ボタンで閉じる
# または File > Exit
```

### 手順2: Unity Editorを再起動

```bash
1. Unity Hub を開く
2. "UnityProject" を選択
3. Unity 2022.3 LTS で開く
```

### 手順3: コンパイル完了を待つ

```
画面右下の進行状況：
[Importing Assets... 1234/5678]  ← これが消えるまで待つ
```

**目安時間：**
- 初回起動：5-10分
- 再コンパイル：1-2分

### 手順4: Consoleでエラーを確認

```
Window > General > Console (Ctrl+Shift+C)
```

**確認ポイント：**
- ❌ 赤いエラーアイコン → エラーメッセージを確認
- ⚠️ 黄色い警告アイコン → 問題なし（無視可）
- ✅ エラーなし → 次へ進む

### 手順5: Toolsメニューを確認

```
上部メニューバー:
File Edit Assets GameObject Component Window [Tools] Help
                                                  ↑
                                              ここをクリック
```

**表示されるはず：**
```
Tools
  ├─ ...（他のメニュー項目）
  └─ Kokoro no Boukensha  ← これが表示される！
      ├─ 【テスト】メニュー表示確認  ← まずこれをクリック！
      ├─ 【ヘルプ】ツールの使い方
      ├─ Generate All Placeholders
      ├─ Audio Setup Tool
      ├─ Asset Setup Tool
      ├─ Game Balance Tuner
      └─ WebGL Build Helper
```

### 手順6: テストメニューをクリック

```
Tools > Kokoro no Boukensha > 【テスト】メニュー表示確認
```

**成功時：**
- ダイアログが表示される
- Consoleに成功メッセージが出力される
- すべてのツールが利用可能

---

## ⚠️ それでも表示されない場合

### ケース1: Consoleにエラーが表示される

**対処法：**

1. エラーメッセージをダブルクリック
2. 問題のあるスクリプトを確認
3. エラー内容を報告してください

**よくあるエラー：**

#### エラー例1: `CS0246: The type or namespace name 'UnityEditor' could not be found`

**原因：** スクリプトが Editor フォルダに配置されていない

**解決策：**
```bash
# 確認コマンド
ls -la Assets/Scripts/Editor/

# 以下のファイルが存在するか確認：
# - AssetSetupTool.cs
# - AudioSetupTool.cs
# - GameBalanceTuner.cs
# - MenuTestTool.cs
# - PlaceholderPrefabGenerator.cs
# - WebGLBuildHelper.cs
# - KokoroNoBoukensha.Editor.asmdef
```

#### エラー例2: `CS1056: Unexpected character`

**原因：** スクリプトの文字エンコーディング問題

**解決策：**
```bash
# スクリプトをUTF-8で再保存
# Unity Editor で File > Save Project
```

### ケース2: コンパイルは成功するが、メニューが出ない

**対処法：**

#### 方法1: アセットの再インポート

```
Unity Editor で:
Assets > Refresh (Ctrl+R / Cmd+R)
```

#### 方法2: Library フォルダの削除（強制再コンパイル）

```bash
# Unity Editor を完全に閉じてから実行

# プロジェクトフォルダに移動
cd /home/user/webapp/UnityProject

# Library フォルダを削除
rm -rf Library/

# Unity Editor を再起動
# → 完全に再コンパイルされます（5-10分）
```

#### 方法3: スクリプトの再保存

```
Unity Editor で:
1. Assets/Scripts/Editor/MenuTestTool.cs をダブルクリック
2. 外部エディタで開く
3. 何も変更せずに Ctrl+S で保存
4. Unity に戻る → 自動的に再コンパイル
```

### ケース3: "Kokoro no Boukensha" は表示されるが、ツールが少ない

**確認：**

```bash
cd /home/user/webapp/UnityProject/Assets/Scripts/Editor
ls -la

# 以下の7ファイルが必要：
# 1. AssetSetupTool.cs
# 2. AudioSetupTool.cs
# 3. GameBalanceTuner.cs
# 4. MenuTestTool.cs
# 5. PlaceholderPrefabGenerator.cs
# 6. WebGLBuildHelper.cs
# 7. KokoroNoBoukensha.Editor.asmdef
```

---

## 📋 チェックリスト

修正作業が完了したか確認：

- [ ] Unity Editorを完全に終了した
- [ ] Unity Editorを再起動した
- [ ] コンパイルが完了した（右下の進行状況バーが消えた）
- [ ] Consoleにエラーがない（赤いアイコンなし）
- [ ] Toolsメニューが表示される
- [ ] "Kokoro no Boukensha" サブメニューが表示される
- [ ] 【テスト】メニュー表示確認をクリックできた
- [ ] ダイアログが表示された

**すべてチェックできれば成功です！** ✅

---

## 🎉 成功後の次のステップ

メニューが正常に表示されたら：

### 1. プレースホルダー生成（最初に実行）

```
Tools > Kokoro no Boukensha > Generate All Placeholders
```

### 2. オーディオセットアップ

```
Tools > Kokoro no Boukensha > Audio Setup Tool
```

### 3. ゲームバランス調整

```
Tools > Kokoro no Boukensha > Game Balance Tuner
```

### 4. WebGLビルド

```
Tools > Kokoro no Boukensha > WebGL Build Helper
```

---

## 📚 関連ドキュメント

- `HOW_TO_ACCESS_TOOLS.md` - ツールアクセスの詳細ガイド
- `EDITOR_MENU_GUIDE.md` - 各ツールの使い方
- `WEBGL_BUILD_INSTRUCTIONS.md` - WebGLビルド手順
- `TROUBLESHOOTING.md` - 一般的なトラブルシューティング

---

## ❓ サポート

上記の手順でも解決しない場合：

1. **Consoleのエラーメッセージをコピー**
2. **Unity のバージョンを確認**（Help > About Unity）
3. **OSとUnityのバージョン情報と共に報告**

例：
```
Unity 2022.3.15f1
OS: Windows 11 / macOS 13.5 / Ubuntu 22.04
エラー: CS0246: The type or namespace name 'UnityEditor' could not be found
```
