# トラブルシューティングガイド

「心の冒険者」Unity 3Dローグライクゲームのトラブルシューティング

## 📋 目次

1. [Unity Tutorial パッケージエラー](#unity-tutorial-パッケージエラー)
2. [コンパイルエラー](#コンパイルエラー)
3. [Missing Reference エラー](#missing-reference-エラー)
4. [パフォーマンス問題](#パフォーマンス問題)
5. [WebGLビルドエラー](#webglビルドエラー)

---

## Unity Tutorial パッケージエラー

### エラーメッセージ

```
ArgumentNullException: Value cannot be null.
Parameter name: source
System.Linq.Enumerable.Any[TSource]
Unity.Tutorials.Core.Editor.TutorialModel+<ReopenActiveScenesAsBeforeTutorialStarted>d__44.MoveNext()
```

### 原因

Unity Learn (IET Framework) パッケージが自動的にインストールされ、チュートリアルシステムと競合しています。

### 解決方法

#### 方法1: Unity Learn パッケージの削除（推奨）

```
1. Unity Editor で Window > Package Manager を開く
2. "Packages: In Project" を選択
3. "Unity Learn" または "In-Editor Tutorials" を探す
4. 該当パッケージを選択し、"Remove" をクリック
5. Unity Editorを再起動
```

#### 方法2: Packagesフォルダから直接削除

```bash
# Unityを閉じてから実行
cd /home/user/webapp/UnityProject
rm -rf Library/PackageCache/com.unity.learn.iet-framework@*
rm -rf Library/PackageCache/com.unity.editorcoroutines@*

# manifest.jsonから削除
# Packages/manifest.json を編集
# "com.unity.learn.iet-framework" の行を削除
```

#### 方法3: エディタ設定で無効化

```
1. Edit > Preferences > Learn
2. "Show tutorials" のチェックを外す
3. Unity Editorを再起動
```

### 予防策

`Packages/manifest.json` から以下を削除:

```json
{
  "dependencies": {
    // この行を削除
    "com.unity.learn.iet-framework": "x.x.x",
    "com.unity.editorcoroutines": "x.x.x"
  }
}
```

---

## コンパイルエラー

### エラー: Missing Assembly Reference

**症状**: スクリプトが `UnityEngine.UI` や `TMPro` を認識しない

**解決方法**:

```
1. Assets/Scripts フォルダを選択
2. 各 .asmdef ファイルを開く
3. References に以下を追加:
   - Unity.TextMeshPro
   - Unity.InputSystem
   - UnityEngine.UI
```

### エラー: Namespace conflicts

**症状**: 同じクラス名が複数の名前空間に存在

**解決方法**:

全スクリプトで名前空間を統一:
```csharp
namespace KokoroNoBoukensha.Core
namespace KokoroNoBoukensha.Character
// など
```

---

## Missing Reference エラー

### エラー: NullReferenceException in Inspector

**症状**: Inspectorでアサインされていないフィールドがある

**解決方法**:

#### GameManager
```
Hierarchy > GameManager を選択
Inspector で以下を設定:
- Dungeon Generator: DungeonGenerator オブジェクトをドラッグ
- Player: Player オブジェクトをドラッグ
- Camera: Main Camera をドラッグ
```

#### AudioManager
```
Hierarchy > AudioManager を選択
Inspector で以下を設定:
- Audio Mixer: Assets/Audio/MainAudioMixer をドラッグ
- BGM Clips: Assets/Audio/BGM/ からクリップをアサイン
- SFX Clips: Assets/Audio/SFX/ からクリップをアサイン
```

#### TutorialManager
```
Hierarchy > TutorialManager を選択
Inspector で以下を設定:
- Tutorial UI: TutorialUI オブジェクトをドラッグ
- Player: Player オブジェクトをドラッグ
```

---

## パフォーマンス問題

### 問題: FPSが低い（<30 FPS）

**解決方法**:

1. **Quality Settings を下げる**
```
Edit > Project Settings > Quality
Level: Low または Medium
```

2. **Profilerで重い処理を特定**
```
Window > Analysis > Profiler
CPU Usage を確認
Scripts の処理時間をチェック
```

3. **ObjectPool を使用**
```csharp
// 敵やエフェクトの生成をプーリングに変更
GameObject enemy = PoolManager.Instance.Get("Enemy", position);
```

4. **Draw Callsを削減**
```
Window > Analysis > Frame Debugger
Batches の数を確認
Static Batching を有効化（Static オブジェクトにチェック）
```

### 問題: メモリ使用量が多い（>1GB）

**解決方法**:

1. **Profilerでメモリリークを確認**
```
Window > Analysis > Profiler
Memory タブを確認
Take Sample Playmode でメモリ使用状況を分析
```

2. **UnloadUnusedAssets を実行**
```csharp
// シーン切り替え時
Resources.UnloadUnusedAssets();
System.GC.Collect();
```

3. **テクスチャサイズを削減**
```
全テクスチャを選択
Inspector > Max Size: 1024 → 512
Apply
```

---

## WebGLビルドエラー

### エラー: Build Failed (Out of Memory)

**解決方法**:

```
Player Settings > WebGL:
- Memory Size: 512 MB → 256 MB
- Code Stripping: High
- Managed Stripping Level: High
- Enable Exceptions: None
```

### エラー: IL2CPP Compilation Failed

**解決方法**:

```
1. Build Settings > WebGL
2. "Switch Platform" を再度実行
3. Player Settings > Other Settings:
   - Scripting Backend: IL2CPP
   - C++ Compiler Configuration: Release
4. 再ビルド
```

### エラー: Compression Format not supported

**解決方法**:

```
Player Settings > WebGL > Publishing Settings:
- Compression Format: Gzip（Brotliでエラーが出る場合）
- Decompression Fallback: ON
```

---

## よくある質問

### Q1: "Tools > Kokoro no Boukensha" メニューが表示されない

**A**: エディタツールがコンパイルされていません。

```
1. Assets/Scripts/Editor フォルダを確認
2. 全 .cs ファイルが存在するか確認
3. Console でコンパイルエラーがないか確認
4. Unity Editorを再起動
```

### Q2: プレースホルダーが生成されない

**A**: AudioSetupTool または PlaceholderPrefabGenerator が失敗しています。

```
1. Console でエラーメッセージを確認
2. Assets/Audio/ フォルダが存在するか確認
3. 書き込み権限があるか確認
4. ツールを再実行
```

### Q3: GameBalance ScriptableObject が作成できない

**A**: Resources フォルダが必要です。

```
1. Assets/Resources フォルダを作成（存在しない場合）
2. 右クリック > Create > KokoroNoBoukensha > Game Balance
3. 名前を "GameBalance" に変更
4. Inspector でデフォルト値を設定
```

### Q4: オーディオが再生されない

**A**: WebGLでは初期化タイミングの問題があります。

```csharp
// AudioManager.cs で確認
#if UNITY_WEBGL && !UNITY_EDITOR
void Start() {
    // ユーザー操作後に初期化
    StartCoroutine(WaitForUserInteraction());
}
#endif
```

### Q5: シーンが見つからない

**A**: Build Settings にシーンが追加されていません。

```
1. File > Build Settings
2. Scenes In Build:
   - Assets/Scenes/TitleScene.unity
   - Assets/Scenes/GameScene.unity
   を追加
3. Apply
```

---

## デバッグ方法

### 1. Console ログの確認

```csharp
// デバッグログを追加
Debug.Log($"[GameManager] Current State: {currentState}");
Debug.LogWarning($"[Player] HP is low: {currentHP}");
Debug.LogError($"[DungeonGenerator] Failed to generate room");
```

### 2. Profiler の使用

```
1. Window > Analysis > Profiler
2. CPU Usage タブで処理時間を確認
3. Memory タブでメモリ使用状況を確認
4. Rendering タブで描画負荷を確認
```

### 3. Frame Debugger の使用

```
1. Window > Analysis > Frame Debugger
2. Enable でフレームをキャプチャ
3. Draw Calls を一つずつ確認
4. Batching の状況を確認
```

---

## サポート情報

### ドキュメント
- `README.md` - プロジェクト概要
- `TEST_PLAN.md` - テスト計画
- `WEBGL_BUILD_INSTRUCTIONS.md` - ビルド手順
- `FINAL_OPTIMIZATION_GUIDE.md` - 最適化ガイド

### Gitコミット履歴
- `CHANGELOG.md` - バージョン履歴
- GitHub Issues - バグ報告

### Unity バージョン
- 推奨: Unity 2022.3 LTS
- 最小: Unity 2021.3 LTS

---

## 緊急対応

### プロジェクトが開けない場合

```bash
# 1. Library フォルダを削除（キャッシュクリア）
rm -rf UnityProject/Library/

# 2. Temp フォルダを削除
rm -rf UnityProject/Temp/

# 3. Unity Editorで再度開く
# Library が自動的に再生成される
```

### 全てがうまくいかない場合

```bash
# 最新版をクローン
git clone https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git
cd therapeutic-gamification-app
git checkout feature/unity-3d-roguelike
git pull origin feature/unity-3d-roguelike

# Unity 2022.3 LTS で開く
```

---

**最終更新**: 2025-12-04  
**バージョン**: 1.0  
**プロジェクト**: 心の冒険者 - Unity 3Dローグライク
