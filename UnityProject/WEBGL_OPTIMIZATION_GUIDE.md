# WebGL ビルド最適化ガイド

「心の冒険者」Unity 3DローグライクゲームのWebGL最適化手順

## 📋 目次

1. [概要](#概要)
2. [ビルド設定](#ビルド設定)
3. [テクスチャ最適化](#テクスチャ最適化)
4. [オブジェクトプーリング](#オブジェクトプーリング)
5. [コード最適化](#コード最適化)
6. [メモリ管理](#メモリ管理)
7. [ロード時間短縮](#ロード時間短縮)
8. [パフォーマンステスト](#パフォーマンステスト)

---

## 概要

### 実装済み最適化システム

- ✅ **ObjectPool.cs** - オブジェクトプーリング
- ✅ **GameBalance.cs** - バランス調整ScriptableObject

### 目標パフォーマンス

| 項目 | 目標値 |
|------|--------|
| **初回ロード時間** | < 10秒 |
| **フレームレート** | 30+ FPS |
| **ビルドサイズ** | < 50 MB |
| **メモリ使用量** | < 500 MB |

---

## ビルド設定

### 1. Player Settings

#### Resolution and Presentation
```
Window > Settings > Player > Resolution and Presentation

Default Canvas Width: 1280
Default Canvas Height: 720
Run In Background: ✓
```

#### WebGL Settings
```
Window > Settings > Player > WebGL Settings

Color Space: Gamma (Linearより軽量)
Auto Graphics API: ✓
Enable Exceptions: None (最軽量)
Publishing Settings:
  - Compression Format: Gzip
  - Enable Decompression Fallback: ✓
Memory Size: 512 MB
```

### 2. Build Settings

```
File > Build Settings > WebGL

Development Build: ✗ (本番ビルド)
Autoconnect Profiler: ✗
Deep Profiling: ✗
Script Debugging: ✗
```

### 3. Quality Settings

```
Edit > Project Settings > Quality

Levels: 3 (Low, Medium, High)
デフォルト: Medium

[Medium Settings]
Pixel Light Count: 2
Texture Quality: Half Res
Anisotropic Textures: Per Texture
Anti Aliasing: 2x Multi Sampling
Soft Particles: ✗
Realtime Reflection Probes: ✗
Shadows: Hard Shadows Only
Shadow Resolution: Medium
Shadow Projection: Close Fit
Shadow Distance: 50
Shadow Cascades: No Cascades
Particle Raycast Budget: 256
```

---

## テクスチャ最適化

### 1. テクスチャインポート設定

#### キャラクターテクスチャ
```
Max Size: 1024
Resize Algorithm: Bilinear
Format: Automatic
Compression: High Quality
Use Crunch Compression: ✓
Compressor Quality: 50
Generate Mip Maps: ✓
```

#### UI テクスチャ
```
Max Size: 512
Format: Automatic
Compression: High Quality
Use Crunch Compression: ✓
Generate Mip Maps: ✗
```

#### エフェクトテクスチャ
```
Max Size: 512
Format: Automatic
Compression: Normal Quality
Use Crunch Compression: ✓
Generate Mip Maps: ✓
```

### 2. テクスチャアトラス作成

```csharp
// Unity Sprite Atlas を使用
// Window > 2D > Sprite Atlas

Sprite Atlas設定:
- Include in Build: ✓
- Allow Rotation: ✓
- Tight Packing: ✓
- Padding: 2
- Max Texture Size: 2048
- Compression: High Quality
```

### 3. 一括設定スクリプト

```csharp
// Editor/TextureOptimizer.cs

using UnityEngine;
using UnityEditor;

public class TextureOptimizer
{
    [MenuItem("Tools/Optimize All Textures")]
    static void OptimizeTextures()
    {
        string[] texturePaths = AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets" });
        
        foreach (string guid in texturePaths)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            
            if (importer != null)
            {
                // WebGL用設定
                TextureImporterPlatformSettings settings = new TextureImporterPlatformSettings();
                settings.name = "WebGL";
                settings.overridden = true;
                settings.maxTextureSize = 1024;
                settings.format = TextureImporterFormat.Automatic;
                settings.compressionQuality = 50;
                settings.crunchedCompression = true;
                
                importer.SetPlatformTextureSettings(settings);
                importer.SaveAndReimport();
            }
        }
        
        Debug.Log($"Optimized {texturePaths.Length} textures");
    }
}
```

---

## オブジェクトプーリング

### 1. ObjectPool 使用方法

#### プール定義

```csharp
// GameManager.cs で ObjectPool を設定

void Start()
{
    // プール設定
    ObjectPool.Instance.pools = new List<ObjectPool.Pool>
    {
        new ObjectPool.Pool
        {
            tag = "Enemy",
            prefab = enemyPrefab,
            size = 20,
            expandable = true
        },
        new ObjectPool.Pool
        {
            tag = "Item",
            prefab = itemPrefab,
            size = 10,
            expandable = true
        },
        new ObjectPool.Pool
        {
            tag = "Effect",
            prefab = effectPrefab,
            size = 15,
            expandable = true
        }
    };
}
```

#### オブジェクト生成

```csharp
// 従来の方法（非推奨）
GameObject enemy = Instantiate(enemyPrefab, position, rotation);

// プーリング使用（推奨）
GameObject enemy = ObjectPool.Instance.SpawnFromPool("Enemy", position, rotation);
```

#### オブジェクト破棄

```csharp
// 従来の方法（非推奨）
Destroy(enemy);

// プーリング使用（推奨）
ObjectPool.Instance.ReturnToPool("Enemy", enemy);

// 遅延破棄
ObjectPool.Instance.ReturnToPoolDelayed("Effect", effectObj, 2.0f);
```

#### IPooledObject 実装

```csharp
// Enemy.cs

using KokoroNoBoukensha.Utils;

public class Enemy : MonoBehaviour, IPooledObject
{
    public void OnObjectSpawn()
    {
        // プールから取得された時の初期化
        ResetStats();
        ResetAnimation();
    }
}
```

### 2. 推奨プール設定

| オブジェクトタイプ | タグ | 初期サイズ | 拡張可能 |
|-----------------|------|----------|---------|
| 敵 | Enemy | 20 | ✓ |
| アイテム | Item | 10 | ✓ |
| エフェクト | Effect | 15 | ✓ |
| ダメージ数値 | DamageText | 10 | ✓ |
| パーティクル | Particle | 20 | ✓ |

---

## コード最適化

### 1. Update() 最適化

#### 悪い例
```csharp
void Update()
{
    // 毎フレーム実行される重い処理
    GameObject[] enemies = FindObjectsOfType<Enemy>();
    foreach (Enemy enemy in enemies)
    {
        // 処理...
    }
}
```

#### 良い例
```csharp
private List<Enemy> enemies = new List<Enemy>();
private float updateInterval = 0.1f;
private float nextUpdateTime;

void Update()
{
    if (Time.time >= nextUpdateTime)
    {
        nextUpdateTime = Time.time + updateInterval;
        UpdateEnemies();
    }
}

void UpdateEnemies()
{
    foreach (Enemy enemy in enemies)
    {
        // 処理...
    }
}
```

### 2. キャッシング

#### 悪い例
```csharp
void Update()
{
    GetComponent<Rigidbody>().velocity = Vector3.forward;
    transform.position += Vector3.up;
}
```

#### 良い例
```csharp
private Rigidbody rb;
private Transform tr;

void Start()
{
    rb = GetComponent<Rigidbody>();
    tr = transform;
}

void Update()
{
    rb.velocity = Vector3.forward;
    tr.position += Vector3.up;
}
```

### 3. LINQ回避（WebGL）

#### 悪い例
```csharp
using System.Linq;

List<Enemy> strongEnemies = enemies.Where(e => e.level > 10).ToList();
```

#### 良い例
```csharp
List<Enemy> strongEnemies = new List<Enemy>();
foreach (Enemy enemy in enemies)
{
    if (enemy.level > 10)
    {
        strongEnemies.Add(enemy);
    }
}
```

### 4. String 連結最適化

#### 悪い例
```csharp
string message = "Player " + playerName + " has " + score + " points";
```

#### 良い例
```csharp
string message = $"Player {playerName} has {score} points";
// または
StringBuilder sb = new StringBuilder();
sb.Append("Player ");
sb.Append(playerName);
sb.Append(" has ");
sb.Append(score);
sb.Append(" points");
string message = sb.ToString();
```

---

## メモリ管理

### 1. Resources.UnloadUnusedAssets

```csharp
// シーン切り替え時など
private IEnumerator UnloadUnusedAssets()
{
    yield return Resources.UnloadUnusedAssets();
    System.GC.Collect();
}
```

### 2. Texture.Compress

```csharp
// ランタイムでテクスチャ圧縮
Texture2D texture = ...; // ロードしたテクスチャ
texture.Compress(true);
```

### 3. Mesh 最適化

```csharp
// MeshFilterのMeshを最適化
MeshFilter meshFilter = GetComponent<MeshFilter>();
meshFilter.mesh.Optimize();
```

---

## ロード時間短縮

### 1. アセットバンドル

```csharp
// ビルド時にアセットバンドル作成
// Editor/BuildAssetBundles.cs

[MenuItem("Assets/Build AssetBundles")]
static void BuildAllAssetBundles()
{
    string assetBundleDirectory = "Assets/StreamingAssets";
    if (!Directory.Exists(assetBundleDirectory))
    {
        Directory.CreateDirectory(assetBundleDirectory);
    }
    
    BuildPipeline.BuildAssetBundles(
        assetBundleDirectory,
        BuildAssetBundleOptions.None,
        BuildTarget.WebGL
    );
}
```

### 2. 非同期シーンロード

```csharp
// GameManager.cs

public void LoadSceneAsync(string sceneName)
{
    StartCoroutine(LoadSceneCoroutine(sceneName));
}

private IEnumerator LoadSceneCoroutine(string sceneName)
{
    AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneName);
    
    while (!asyncLoad.isDone)
    {
        float progress = Mathf.Clamp01(asyncLoad.progress / 0.9f);
        // ローディング画面更新
        loadingSlider.value = progress;
        yield return null;
    }
}
```

### 3. プログレッシブロード

```csharp
// 重いオブジェクトを分割ロード
public IEnumerator LoadDungeonProgressive()
{
    // フロア生成
    GenerateFloor();
    yield return null;
    
    // 壁生成
    GenerateWalls();
    yield return null;
    
    // 敵配置
    SpawnEnemies();
    yield return null;
    
    // アイテム配置
    SpawnItems();
    yield return null;
}
```

---

## パフォーマンステスト

### 1. Profiler 使用

```
Window > Analysis > Profiler

チェック項目:
- CPU Usage (< 33ms for 30 FPS)
- GPU Usage
- Memory
- Rendering
- Scripts
```

### 2. Stats ウィンドウ

```
Game View > Stats

チェック項目:
- FPS
- Batches (少ないほど良い)
- SetPass calls (少ないほど良い)
- Tris (ポリゴン数)
- Verts (頂点数)
```

### 3. Frame Debugger

```
Window > Analysis > Frame Debugger

確認事項:
- Draw Call 数
- Batch 状況
- オーバードロー
```

---

## ビルドサイズ削減

### 1. Code Stripping

```
Edit > Project Settings > Player > Other Settings

Managed Stripping Level: High
```

### 2. 不要アセット削除

```bash
# 未使用アセットを検索
# Unity Pro のみ
Window > Analysis > Build Report
```

### 3. Compression設定

```
Edit > Project Settings > Player > Publishing Settings

Compression Format: Gzip
Name Files As Hashes: ✓
Data Caching: ✓
```

---

## デプロイチェックリスト

### ビルド前

- [ ] 全てのテクスチャを最適化
- [ ] ObjectPool を全オブジェクトに適用
- [ ] LINQ を削除
- [ ] Quality Settings を Medium に設定
- [ ] Code Stripping を High に設定
- [ ] Development Build を無効化

### ビルド後

- [ ] ビルドサイズ確認（< 50 MB）
- [ ] 初回ロード時間計測（< 10秒）
- [ ] FPS 計測（> 30 FPS）
- [ ] メモリ使用量確認（< 500 MB）
- [ ] 全機能動作確認
- [ ] モバイルブラウザテスト

---

## トラブルシューティング

### Q: ビルドサイズが大きすぎる

**A**:
1. Build Report で大きいアセットを確認
2. テクスチャ圧縮を確認
3. 未使用アセットを削除
4. Audio Compression を有効化

### Q: ロード時間が長い

**A**:
1. 非同期ロードを実装
2. アセットバンドルを使用
3. プログレッシブロードを実装
4. Preload Size を削減

### Q: FPS が低い

**A**:
1. Profiler で重い処理を特定
2. Draw Call を削減（Batching）
3. Particle 数を削減
4. Quality Settings を下げる

### Q: メモリ不足

**A**:
1. ObjectPool を使用
2. UnloadUnusedAssets を実行
3. テクスチャサイズを削減
4. Memory Size を増やす（最大 2GB）

---

## 推奨最終設定

```
Player Settings:
- Color Space: Gamma
- Enable Exceptions: None
- Compression: Gzip
- Memory Size: 512 MB
- Managed Stripping Level: High

Quality Settings:
- Quality Level: Medium
- Pixel Light Count: 2
- Texture Quality: Half Res
- Anti Aliasing: 2x
- Shadows: Hard Shadows Only

Build Settings:
- Development Build: ✗
- Compression Format: Gzip
- Data Caching: ✓
```

---

**作成日**: 2025-12-04  
**バージョン**: 1.0  
**関連スクリプト**:
- `ObjectPool.cs`
- `GameBalance.cs`
