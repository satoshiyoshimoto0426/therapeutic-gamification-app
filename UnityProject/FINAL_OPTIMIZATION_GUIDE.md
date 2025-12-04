# 心の冒険者 - 最終最適化ガイド

このガイドでは、ゲームの最終調整、パフォーマンス最適化、バランス調整について説明します。

## 📋 目次

1. [WebGL最適化](#webgl最適化)
2. [ゲームバランス調整](#ゲームバランス調整)
3. [バグ修正チェックリスト](#バグ修正チェックリスト)
4. [パフォーマンステスト](#パフォーマンステスト)
5. [リリース前チェックリスト](#リリース前チェックリスト)

---

## 🎮 WebGL最適化

### 1. オブジェクトプーリングの実装

`PoolManager`を使用して、頻繁に生成/破棄されるオブジェクトを再利用します。

#### セットアップ方法

1. **PoolManagerの設置**
   - ヒエラルキーに空のGameObjectを作成し、`PoolManager`をアタッチ
   - または、最初のシーン読み込み時に自動生成されます

2. **プール設定の追加**
   ```csharp
   // PoolManagerコンポーネントのインスペクタで設定
   Pool Configurations:
   - Pool Name: "DamageEffect"
     Prefab: DamageEffectPrefab
     Initial Size: 20
     Max Size: 50
     Auto Expand: true
   
   - Pool Name: "Projectile"
     Prefab: ProjectilePrefab
     Initial Size: 30
     Max Size: 100
   ```

3. **使用例**
   ```csharp
   // オブジェクトの取得
   GameObject effect = PoolManager.Instance.Get("DamageEffect", position);
   
   // 3秒後に自動返却
   PoolManager.Instance.ReturnAfterDelay("DamageEffect", effect, 3f);
   ```

#### 推奨プール設定

| プール名 | プレハブ | 初期サイズ | 最大サイズ | 用途 |
|---------|---------|----------|----------|------|
| DamageEffect | ダメージエフェクト | 20 | 50 | 戦闘時のダメージ表示 |
| HealEffect | 回復エフェクト | 10 | 30 | アイテム使用時 |
| LevelUpEffect | レベルアップエフェクト | 5 | 10 | レベルアップ時 |
| Projectile | 発射物 | 30 | 100 | 遠距離攻撃 |
| ItemDrop | ドロップアイテム | 50 | 200 | 敵撃破時 |
| Enemy_Slime | スライム | 20 | 50 | 敵の出現 |
| Enemy_Goblin | ゴブリン | 15 | 40 | 敵の出現 |

### 2. テクスチャ圧縮

WebGL向けにテクスチャを最適化します。

```
Unity Editor:
1. テクスチャを選択
2. Inspector → Platform Settings → WebGL
3. 設定:
   - Max Size: 1024 (必要に応じて512)
   - Compression: High Quality
   - Format: ASTC 4x4 (または DXT5 Compressed)
4. Apply
```

### 3. アセットバンドルの使用

大きなアセットは遅延ロードします。

```csharp
// AudioManagerで実装済み
// BGMは必要になった時のみロード
AudioManager.Instance.PlayBGM(BGMType.Battle);
```

### 4. ビルド設定

```
File → Build Settings → Player Settings → WebGL:

- Code Optimization: Runtime Speed
- Managed Stripping Level: High
- IL2CPP Code Generation: Faster runtime
- Compression Format: Brotli
- Memory Size: 256 MB (必要に応じて調整)
- Enable Exceptions: None
- WebAssembly Streaming: On
```

---

## ⚖️ ゲームバランス調整

### 1. 敵のステータス調整

`GameBalance.cs`で敵の強さを調整します。

```csharp
// 例：スライムが強すぎる場合
public static void AdjustEnemyBalance()
{
    var slimeConfig = GetEnemyConfig(EnemyType.Slime);
    slimeConfig.baseAttack = 3;  // 5から3に減少
    slimeConfig.baseDefense = 1; // 2から1に減少
}
```

#### 推奨バランス（フロア1-10）

| 敵タイプ | HP | 攻撃力 | 防御力 | 経験値 | ゴールド |
|---------|-----|--------|--------|--------|---------|
| Slime | 10-20 | 3-5 | 1-2 | 5-10 | 3-8 |
| Goblin | 20-40 | 5-8 | 2-4 | 10-20 | 8-15 |
| Orc | 50-80 | 10-15 | 5-8 | 30-50 | 20-40 |

### 2. アイテムドロップ率調整

```csharp
// GameBalance.csのドロップ率設定
public static DropRateConfig GetDropRates(int floor)
{
    return new DropRateConfig
    {
        NormalRate = 0.60f,    // 60% (通常)
        RareRate = 0.25f,      // 25% (レア)
        SuperRareRate = 0.10f, // 10% (SR)
        LegendRate = 0.05f     // 5% (伝説)
    };
}
```

### 3. レベルアップ曲線

プレイヤーの成長速度を調整します。

```csharp
// 経験値テーブル調整
public static int GetRequiredExp(int level)
{
    // 緩やかな成長: level * 100
    // 標準的な成長: (int)(level * level * 1.5f)
    // 急激な成長: level * level * 2
    
    return (int)(level * level * 1.5f); // 標準的な成長
}
```

### 4. ガチャ確率調整

```csharp
// ガチャのピックアップ設定
public static GachaPickupConfig GetCurrentPickup()
{
    return new GachaPickupConfig
    {
        PickupItemId = "legendary_sword_001",
        PickupRate = 0.02f,  // 2% (通常の伝説5%より低確率だが特定アイテム)
        TotalLegendRate = 0.05f // 全体の伝説確率は5%維持
    };
}
```

---

## 🐛 バグ修正チェックリスト

### 高優先度

- [ ] **ターン同期エラー**
  - プレイヤー移動後、敵が動かない
  - → `TurnManager.ProcessPlayerTurn()`の最後に`StartEnemyTurns()`を確認

- [ ] **インベントリ表示バグ**
  - アイテムが重複表示される
  - → `InventoryUI.Refresh()`で古いUIを`Clear()`してから再生成

- [ ] **セーブデータ破損**
  - ロード時にクラッシュ
  - → `SaveManager.LoadGame()`でtry-catchを追加、JSONバージョン確認

- [ ] **WebGL音声が再生されない**
  - BGM/SEが聞こえない
  - → `AudioManager`でWebGL用にユーザー操作後に初期化

### 中優先度

- [ ] **UIスケーリング問題**
  - 異なる解像度で表示崩れ
  - → Canvas ScalerをScale with Screen Sizeに設定

- [ ] **メモリリーク**
  - 長時間プレイ後に動作が重くなる
  - → `PoolManager`の使用、不要なリスナー解除

- [ ] **敵AIの異常行動**
  - 壁に向かって移動し続ける
  - → `EnemyAI.FindPath()`のパスファインディング修正

### 低優先度

- [ ] **アニメーション遷移の違和感**
  - 攻撃モーションが途中で切れる
  - → AnimatorのTransition設定を調整（Has Exit Time）

- [ ] **エフェクトのちらつき**
  - ダメージエフェクトが瞬間表示される
  - → Fade In/Outのタイミング調整

---

## 🔬 パフォーマンステスト

### FPS測定

```csharp
// デバッグ用FPSカウンター
public class FPSCounter : MonoBehaviour
{
    private float deltaTime = 0.0f;

    void Update()
    {
        deltaTime += (Time.unscaledDeltaTime - deltaTime) * 0.1f;
    }

    void OnGUI()
    {
        float fps = 1.0f / deltaTime;
        GUI.Label(new Rect(10, 10, 100, 20), $"FPS: {fps:0.}");
    }
}
```

### メモリ使用量チェック

```csharp
// Unity Profilerを使用
// Window → Analysis → Profiler
// WebGLビルド後、ブラウザのDeveloper Toolsでメモリ確認
```

### 目標値

| プラットフォーム | FPS | メモリ使用量 | ロード時間 |
|---------------|-----|------------|----------|
| WebGL (PC) | 60 FPS | < 200 MB | < 10秒 |
| WebGL (Mobile) | 30 FPS | < 150 MB | < 15秒 |
| Windows | 60 FPS | < 500 MB | < 5秒 |

---

## ✅ リリース前チェックリスト

### ゲームプレイテスト

- [ ] チュートリアルを最初から最後まで完了できる
- [ ] フロア1から30まで到達できる
- [ ] ボス戦（フロア10, 20, 30）が正常に動作
- [ ] セーブ/ロードが正常に機能
- [ ] 全アイテムタイプが使用可能
- [ ] 全装備が正常に装着/解除できる
- [ ] ガチャシステムが正常に動作
- [ ] 現実連携タスクがリワードを付与
- [ ] AIストーリー生成が動作
- [ ] BGM/SEが適切に再生される

### UI/UXテスト

- [ ] 全ボタンが反応する
- [ ] マウス/キーボード操作が快適
- [ ] 異なる解像度で表示が正常
- [ ] モバイルでタッチ操作が可能（WebGL）
- [ ] ローディング画面が表示される
- [ ] エラーメッセージが適切に表示

### 技術テスト

- [ ] WebGLビルドが成功
- [ ] ブラウザで起動できる（Chrome, Firefox, Safari）
- [ ] メモリリークがない（長時間プレイ）
- [ ] FPSが安定している
- [ ] バックエンドAPIとの通信が正常
- [ ] 認証フローが動作
- [ ] タスク同期が機能

### ドキュメント

- [ ] README.mdが最新
- [ ] セットアップ手順が正確
- [ ] 既知の問題が記載
- [ ] ライセンス情報が記載
- [ ] クレジット（使用アセット）が記載

### デプロイ準備

- [ ] Gitコミットが整理されている
- [ ] PRがマージ可能
- [ ] バージョン番号が更新
- [ ] CHANGELOG.mdが更新
- [ ] ビルド設定が本番用に設定

---

## 🚀 最適化のヒント

### 1. 描画呼び出し削減

- Static Batchingを有効化（動かないオブジェクトに`Static`フラグ）
- マテリアルの数を削減（同じマテリアルを共有）
- テクスチャアトラスを使用

### 2. GCアロケーション削減

```csharp
// 悪い例
void Update()
{
    string text = "HP: " + player.HP; // 毎フレーム文字列アロケーション
}

// 良い例
private StringBuilder sb = new StringBuilder();
void Update()
{
    sb.Clear();
    sb.Append("HP: ").Append(player.HP);
    string text = sb.ToString();
}
```

### 3. コルーチンの最適化

```csharp
// WaitForSecondsをキャッシュ
private WaitForSeconds wait1sec = new WaitForSeconds(1f);

IEnumerator MyCoroutine()
{
    yield return wait1sec; // 再利用
}
```

### 4. Physics最適化

```
Edit → Project Settings → Physics:
- Fixed Timestep: 0.02 (デフォルト)
- Default Max Angular Speed: 7 (軽量化: 5)
- Sleep Threshold: 0.005 (軽量化: 0.01)
```

---

## 📊 パフォーマンスモニタリング

### Unity Profilerの使用

```
1. Window → Analysis → Profiler
2. WebGLビルドをDevelopment Buildでビルド
3. Autoconnect to Profilerを有効化
4. ゲームプレイ中のCPU/GPU/Memory使用量を確認
```

### 重要な指標

- **CPU Usage**: < 50ms/frame (60FPS目標)
- **Rendering**: < 16ms/frame
- **Scripts**: < 10ms/frame
- **Garbage Collection**: < 1回/秒
- **Batches**: < 100 draws/frame
- **Vertices**: < 100k/frame

---

## 🎯 最終調整の流れ

1. **Alpha版テスト** (内部テスト)
   - 基本機能の動作確認
   - クリティカルバグの修正
   - パフォーマンス計測

2. **Beta版テスト** (限定公開)
   - ユーザーフィードバック収集
   - バランス調整
   - UI/UX改善

3. **Release Candidate** (リリース候補)
   - 最終バグ修正
   - ドキュメント整備
   - デプロイ準備

4. **製品版リリース**
   - 本番環境デプロイ
   - モニタリング開始
   - ユーザーサポート体制確立

---

## 📝 関連ドキュメント

- `WEBGL_OPTIMIZATION_GUIDE.md` - WebGL最適化詳細
- `AUDIO_ASSET_GUIDE.md` - オーディオアセット設定
- `TUTORIAL_INTEGRATION_GUIDE.md` - チュートリアル統合
- `ASSET_IMPORT_GUIDE.md` - 3Dモデル/アセット導入
- `3D_MODEL_SETUP_GUIDE.md` - 3Dモデルセットアップ
- `UNITY_ROGUELIKE_DESIGN.md` - ゲーム設計書

---

**最終更新**: 2025-12-04  
**バージョン**: 1.0  
**プロジェクト**: 心の冒険者 - Unity 3Dローグライク
