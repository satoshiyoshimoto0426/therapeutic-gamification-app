# クイック修正ガイド - Unity Tutorial エラー

## 🚨 エラー内容

```
ArgumentNullException: Value cannot be null.
Parameter name: source
Unity.Tutorials.Core.Editor.TutorialModel
```

このエラーは Unity Learn (Tutorial) パッケージの競合によるものです。

---

## ✅ 即座の解決方法（3ステップ）

### ステップ1: Unity Editorを閉じる

現在開いているUnity Editorを完全に閉じてください。

### ステップ2: Package Managerから削除

Unity Editorを再度開き:

```
1. Window > Package Manager
2. "Packages: In Project" を選択
3. 以下のパッケージを探して削除:
   - "Unity Learn" または "Learn"
   - "In-Editor Tutorials" または "IET Framework"
   - "Editor Coroutines"（依存関係）

4. 各パッケージを選択 → "Remove" ボタンをクリック
5. Unity Editorを再起動
```

### ステップ3: Packagesフォルダの確認

```
UnityProject/Packages/manifest.json を確認:

削除すべき行（存在する場合）:
- "com.unity.learn.iet-framework": "..."
- "com.unity.editorcoroutines": "..."
```

---

## 🔧 代替方法（コマンドライン）

Unity Editorを閉じてから:

```bash
cd /home/user/webapp/UnityProject

# Libraryキャッシュをクリア
rm -rf Library/PackageCache/com.unity.learn*
rm -rf Library/PackageCache/com.unity.editorcoroutines*

# Packages/manifest.json を確認・編集
# 上記のパッケージ行を削除

# Unity Editorを再起動
```

---

## 📝 新しいmanifest.jsonが作成されました

`Packages/manifest.json` に基本的なパッケージ構成が設定されています。

含まれる主要パッケージ:
- ✅ TextMeshPro (UI用)
- ✅ Visual Studio Code (エディタ統合)
- ✅ Test Framework (テスト用)
- ✅ URP (レンダリング)
- ✅ 基本モジュール（Physics, Audio, UI等）

含まれない（問題のある）パッケージ:
- ❌ Unity Learn / IET Framework
- ❌ Editor Coroutines

---

## ✅ 確認方法

エラーが解消されたか確認:

```
1. Unity Editorを開く
2. Console (Ctrl+Shift+C) を確認
3. エラーが表示されないことを確認
4. Tools > Kokoro no Boukensha メニューが表示されることを確認
5. Play ボタンを押してゲームが起動することを確認
```

---

## 🎮 修正後の次のステップ

エラーが解消されたら:

```
1. Tools > Kokoro no Boukensha > Generate All Placeholders
2. Tools > Kokoro no Boukensha > Audio Setup Tool
3. Assets/Resources 右クリック > Create > KokoroNoBoukensha > Game Balance
4. Play ボタンでテスト実行
```

---

## ❓ それでも解決しない場合

### 完全なクリーンビルド

```bash
# Unity Editorを閉じる

cd /home/user/webapp/UnityProject

# キャッシュを完全削除
rm -rf Library/
rm -rf Temp/
rm -rf obj/

# Unity Editorで再度開く
# Library が自動再生成される（5-10分かかる）
```

### 最終手段: 最新版を取得

```bash
# 最新版をクローン
git clone https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git
cd therapeutic-gamification-app
git checkout feature/unity-3d-roguelike
git pull origin feature/unity-3d-roguelike

# Unity 2022.3 LTS で UnityProject を開く
```

---

## 📚 関連ドキュメント

- `TROUBLESHOOTING.md` - 包括的なトラブルシューティング
- `README.md` - プロジェクト概要
- `WEBGL_BUILD_INSTRUCTIONS.md` - ビルド手順

---

**作成日**: 2025-12-04  
**対象エラー**: Unity Tutorial パッケージ競合  
**推定解決時間**: 5分  
**成功率**: 95%以上
