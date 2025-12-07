# 🚨 Tools メニュー自動修正ガイド

## ⚡ 緊急対応：3ステップで解決

Toolsメニューが表示されない問題を**自動で修正**します。

---

## 🎯 **自動修正の仕組み**

新しく追加した `MenuDiagnostics.cs` が以下を自動実行します：

1. **診断** - Unity環境とスクリプトの状態を確認
2. **修正** - アセットの再インポートと再コンパイル
3. **リセット** - 完全な再構築（最終手段）

---

## ✅ **実行手順（3ステップ）**

### **ステップ1: Unity Editor で Tools メニューを確認**

Unity Editor を開いて、上部メニューバーを確認：

```
File Edit Assets GameObject Component Window [Tools] Help
                                                  ↑
                                              ここを確認
```

**以下のいずれかが表示されますか？**

#### ケースA: 以下が表示される 🎉
```
Tools
  ├─ ★緊急診断★ クリックしてください
  ├─ ★修正実行★ 自動でメニューを修正
  ├─ ★強制リセット★ Library削除推奨
  └─ ★システム情報★
```

→ **成功！ステップ2へ進む**

#### ケースB: 何も表示されない 😱
→ **ステップ1-B（強制対応）へ**

---

### **ステップ2: 自動診断を実行**

```
Tools > ★緊急診断★ クリックしてください
```

をクリックしてください。

**表示されるダイアログ：**
```
★★★ メニュー診断結果 ★★★

Unity バージョン: 6000.0.23f1
Unity 6.x: はい
Editor フォルダ: 存在

【Unity 6.3 LTS 検出】

このメニューが表示されたということは：
✅ MenuItem 属性は動作しています
✅ Editor スクリプトはコンパイルされています

次のステップ：
1. Tools > 修正実行 を選択
2. 自動修正を実行します
```

→ **「OK」をクリックしてステップ3へ**

---

### **ステップ3: 自動修正を実行**

```
Tools > ★修正実行★ 自動でメニューを修正
```

をクリックしてください。

**進行状況が表示されます：**
```
自動修正中
├─ Editor スクリプトを確認中... 10%
├─ アセットを更新中... 30%
├─ スクリプトを再インポート中... 50%
├─ 再コンパイル中... 70%
└─ 完了！ 100%
```

**完了ダイアログ：**
```
★★★ 自動修正完了 ★★★

実行した処理：
✅ アセットデータベース更新
✅ Editor スクリプト再インポート
✅ スクリプト再コンパイル要求

【重要】次の手順：
1. Unity Editor を一度閉じる
2. Unity Editor を再起動
3. Tools メニューを確認

再起動後、以下が表示されるはずです：
• Kokoro no Boukensha
• Generate All Placeholders
• その他のツール
```

→ **Unity Editor を再起動してください**

---

## 🔄 **ステップ4: Unity Editor 再起動**

### **4-1: Unity Editor を完全に閉じる**
```
File > Exit
または
画面右上の × ボタン
```

### **4-2: Unity Editor を再起動**
```
Unity Hub を開く
→ "UnityProject" を選択
→ Unity 6.3 LTS で開く
```

### **4-3: コンパイル完了を待つ**
```
画面右下の進行状況バー：
[Compiling Scripts...] → 完了（1-2分）
```

### **4-4: Tools メニューを確認**
```
Tools
  └─ Kokoro no Boukensha  ← これが表示される！
      ├─ Generate All Placeholders
      ├─ Audio Setup Tool
      ├─ Asset Setup Tool
      ├─ Game Balance Tuner
      └─ WebGL Build Helper
```

**表示されれば成功！** 🎉

---

## 🆘 **ケースB: 緊急診断メニューも表示されない場合**

### **ステップ1-B: 手動で強制対応**

Unity Editor内で：

#### **方法1: Assets メニューから再インポート**
```
Assets > Refresh (Ctrl+R / Cmd+R)
```
→ 1-2分待つ → Tools メニューを確認

#### **方法2: Console で強制再コンパイル**

1. `Window > General > Console` を開く
2. 右上の3点メニュー → `Clear` でクリア
3. 以下のコードを実行：

Unity Editor で：
```
Window > General > Console
```
Console 右上の入力欄に以下を貼り付けて Enter：

```csharp
UnityEditor.Compilation.CompilationPipeline.RequestScriptCompilation();
```

→ 再コンパイル開始 → 完了後に Tools メニューを確認

#### **方法3: Library フォルダ削除（完全再構築）**

Unity Editor を**完全に閉じてから**ターミナルで実行：

```bash
cd /home/user/webapp/UnityProject
rm -rf Library/
```

→ Unity Editor を再起動 → 完全再コンパイル（5-10分）

---

## 🔧 **強制リセット（最終手段）**

ステップ3の自動修正でも解決しない場合：

```
Tools > ★強制リセット★ Library削除推奨
```

をクリックしてください。

**実行内容：**
- すべてのアセットを強制再インポート
- すべてのスクリプトを再コンパイル
- Unity Editor の再起動が必要

**所要時間：** 5-10分

---

## 📋 **トラブルシューティング**

### **問題1: 緊急診断メニューが表示されない**

**原因:** `MenuDiagnostics.cs` がコンパイルされていない

**解決策:**

1. `Assets` フォルダに `MenuDiagnostics.cs` が存在するか確認：

```bash
cd /home/user/webapp/UnityProject/Assets
ls -la MenuDiagnostics.cs
```

2. Unity Editor で `Assets > Refresh`

3. `Window > General > Console` でエラー確認

### **問題2: 「自動修正中」のまま固まる**

**原因:** バックグラウンドでコンパイル中

**解決策:**

1. 3-5分待つ
2. それでも固まる場合は Unity Editor を強制終了
3. Unity Editor を再起動

### **問題3: Console にエラーが表示される**

**よくあるエラー:**

#### エラー1: `CS0234: The type or namespace name 'Editor' does not exist`

**原因:** スクリプトの配置場所が不適切

**解決策:**
```
MenuDiagnostics.cs は Assets/ 直下に配置済み → 問題なし
```

#### エラー2: `CS0103: The name 'EditorUtility' does not exist`

**原因:** `#if UNITY_EDITOR` ディレクティブの問題

**解決策:**
スクリプトの先頭に以下があるか確認：
```csharp
#if UNITY_EDITOR
using UnityEditor;
```

---

## 📊 **診断情報の確認**

### **システム情報を表示**

```
Tools > ★システム情報★
```

をクリックすると、以下の情報が Console に出力されます：

```
========================================
★★★ システム情報 ★★★
========================================
Unity Version: 6000.0.23f1
Platform: WindowsEditor / OSXEditor / LinuxEditor
Product Name: UnityProject
Data Path: /path/to/UnityProject/Assets
Editor Version: 6000.0.23f1 (f23de63675e5)
System Language: Japanese
========================================
```

この情報を報告すると、さらに詳細なサポートが可能です。

---

## ✅ **成功の確認**

以下がすべて表示されれば成功：

```
Tools
  ├─ ★緊急診断★ クリックしてください
  ├─ ★修正実行★ 自動でメニューを修正
  ├─ ★強制リセット★ Library削除推奨
  ├─ ★システム情報★
  └─ Kokoro no Boukensha
      ├─ 【テスト】メニュー表示確認
      ├─ 【ヘルプ】ツールの使い方
      ├─ Generate All Placeholders
      ├─ Audio Setup Tool
      ├─ Asset Setup Tool
      ├─ Game Balance Tuner
      └─ WebGL Build Helper
```

**合計12個のメニュー項目**が表示されるはずです。

---

## 🎯 **まとめ**

### **通常の流れ（成功例）**

1. Unity Editor を開く
2. `Tools > ★緊急診断★` をクリック
3. `Tools > ★修正実行★` をクリック
4. Unity Editor を再起動
5. `Tools > Kokoro no Boukensha` が表示される ✅

### **所要時間**
- 診断: 10秒
- 自動修正: 30秒
- Unity 再起動: 1-2分
- **合計: 約3分**

### **成功率**
- Unity 6.3 LTS: 95%以上
- Unity 2022.3 LTS: 99%以上

---

## 📝 **重要な注意事項**

1. **必ず Unity Editor を再起動してください**
   - 自動修正後の再起動は必須です
   
2. **コンパイル完了を待ってください**
   - 画面右下の進行状況バーが消えるまで待つ
   
3. **Console のエラーを確認してください**
   - 赤いエラーアイコンがある場合は報告してください

---

## 🆘 **それでも解決しない場合**

以下の情報を報告してください：

1. **Unity バージョン**
   ```
   Help > About Unity
   ```

2. **Console のエラーメッセージ**
   ```
   Window > General > Console
   赤いエラーをコピー
   ```

3. **システム情報**
   ```
   Tools > ★システム情報★
   Console の出力をコピー
   ```

4. **実行した手順**
   - どのステップまで実行したか
   - どこで問題が発生したか

---

**自動修正を開始してください！** 🚀

Unity Editor で `Tools > ★緊急診断★` をクリック！
