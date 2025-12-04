# 3Dモデル・アニメーション セットアップガイド

「心の冒険者」Unity 3Dローグライクゲームの3Dモデル・アニメーション実装ガイド

## 📋 目次

1. [概要](#概要)
2. [プレイヤーモデル](#プレイヤーモデル)
3. [敵モデル](#敵モデル)
4. [ダンジョン環境](#ダンジョン環境)
5. [アニメーション設定](#アニメーション設定)
6. [エフェクト](#エフェクト)
7. [推奨アセット](#推奨アセット)

---

## 概要

### 実装済みスクリプト

- ✅ `PlayerAnimationController.cs` - プレイヤーアニメーション制御
- ✅ `EnemyAnimationController.cs` - 敵アニメーション制御
- ✅ `DungeonVisualizer.cs` - ダンジョン3D環境生成
- ✅ `CameraController.cs` - カメラ制御
- ✅ `EffectManager.cs` - エフェクト管理
- ✅ `ModelManager.cs` - 3Dモデル管理

### 必要なアセット

各カテゴリのプレハブを準備してください。

---

## プレイヤーモデル

### 1. モデル要件

#### 基本仕様
- **フォーマット**: FBX / Blend
- **ポリゴン数**: 5,000 - 15,000 (モバイル対応)
- **テクスチャ**: 1024x1024 or 2048x2048
- **リグ**: Humanoid Rig (Unity標準)

#### ボーン構造 (必須)
```
Root
├─ Hips
│  ├─ Spine
│  │  ├─ Chest
│  │  │  ├─ Neck
│  │  │  │  └─ Head
│  │  │  ├─ LeftShoulder
│  │  │  │  └─ LeftArm (武器装着)
│  │  │  └─ RightShoulder
│  │  │     └─ RightArm (盾装着)
│  ├─ LeftUpLeg
│  │  └─ LeftLeg
│  └─ RightUpLeg
     └─ RightLeg
```

### 2. アニメーション

#### 必須アニメーション (8方向対応)

| アニメーション名 | 説明 | ループ | 長さ |
|---------------|------|-------|------|
| `Idle` | 待機 | Yes | 2-3s |
| `Walk_N` | 北へ移動 | Yes | 1s |
| `Walk_NE` | 北東へ移動 | Yes | 1s |
| `Walk_E` | 東へ移動 | Yes | 1s |
| `Walk_SE` | 南東へ移動 | Yes | 1s |
| `Walk_S` | 南へ移動 | Yes | 1s |
| `Walk_SW` | 南西へ移動 | Yes | 1s |
| `Walk_W` | 西へ移動 | Yes | 1s |
| `Walk_NW` | 北西へ移動 | Yes | 1s |
| `Attack_Melee` | 近接攻撃 | No | 0.5s |
| `Attack_Range` | 遠距離攻撃 | No | 0.7s |
| `TakeDamage` | 被ダメージ | No | 0.3s |
| `Death` | 死亡 | No | 1.5s |
| `UseItem` | アイテム使用 | No | 0.8s |
| `LevelUp` | レベルアップ | No | 2.0s |

#### Animator Controller設定

```
PlayerAnimator
├─ Parameters
│  ├─ IsMoving (Bool)
│  ├─ DirectionX (Float) -1 to 1
│  ├─ DirectionZ (Float) -1 to 1
│  ├─ IsAttacking (Bool)
│  ├─ Attack (Trigger)
│  ├─ TakeDamage (Trigger)
│  ├─ Death (Trigger)
│  ├─ UseItem (Trigger)
│  └─ LevelUp (Trigger)
└─ States
   ├─ Idle (Default)
   ├─ Movement BlendTree (8方向)
   ├─ Attack
   ├─ TakeDamage
   ├─ Death
   ├─ UseItem
   └─ LevelUp
```

### 3. プレハブ構成

#### Player Prefab構造
```
PlayerCharacter (Empty GameObject)
├─ Model (FBX Model)
│  └─ Armature
│     └─ [Mesh]
├─ AnimationController
├─ Collider (CapsuleCollider)
├─ Rigidbody
├─ Player.cs
├─ PlayerAnimationController.cs
└─ EquipmentSlots (Empty)
   ├─ RightHandSlot (武器)
   ├─ LeftHandSlot (盾)
   ├─ HeadSlot (兜)
   └─ BodySlot (鎧)
```

### 4. モデル配置手順

#### Step 1: モデルインポート
1. FBXファイルを `Assets/Models/Characters/` にドラッグ
2. Inspector → Rig → Animation Type: **Humanoid**
3. Inspector → Materials → Extract Materials

#### Step 2: アニメーションセットアップ
1. FBXのAnimationsタブを開く
2. 各アニメーションクリップに名前を設定
3. Loop Timeを設定 (Idle, Walk系はループ)

#### Step 3: Animator作成
1. `Assets/Animations/Player/` に `PlayerAnimator` 作成
2. States追加・遷移設定
3. BlendTreeで8方向移動を設定

#### Step 4: Prefab作成
1. Hierarchyに空のGameObject作成 → 名前: `PlayerCharacter`
2. モデルを子オブジェクトとして配置
3. 必要なコンポーネントをアタッチ
4. Prefab化: `Assets/Prefabs/Characters/PlayerCharacter.prefab`

---

## 敵モデル

### 1. 敵タイプ一覧

#### 通常敵 (レベル 1-10)
- **スライム** (Slime)
- **ゴブリン** (Goblin)
- **コウモリ** (Bat)
- **オオカミ** (Wolf)

#### 中級敵 (レベル 11-20)
- **オーク** (Orc)
- **スケルトン** (Skeleton)
- **ゴーレム** (Golem)
- **ワイバーン** (Wyvern)

#### 上級敵 (レベル 21-30)
- **デーモン** (Demon)
- **ドラゴン** (Dragon)
- **リッチ** (Lich)
- **ビホルダー** (Beholder)

### 2. 敵アニメーション

#### 必須アニメーション

| アニメーション名 | 説明 | ループ |
|---------------|------|-------|
| `Idle` | 待機 | Yes |
| `Walk` | 移動 | Yes |
| `Attack` | 攻撃 | No |
| `TakeDamage` | 被ダメージ | No |
| `Death` | 死亡 | No |
| `Special` | 特殊技（ボス用） | No |

### 3. 敵Prefab構成

```
EnemyCharacter
├─ Model
│  └─ Armature
├─ AnimationController
├─ Collider
├─ Enemy.cs
├─ EnemyAnimationController.cs
└─ HealthBar (UI Canvas)
```

---

## ダンジョン環境

### 1. タイルプレハブ

#### 床タイル
- `Floor_Normal.prefab` - 通常部屋の床
- `Floor_Special.prefab` - 特殊部屋の床
- `Floor_Corridor.prefab` - 通路の床

#### 壁タイル
- `Wall_Outer.prefab` - 外壁
- `Wall_Inner.prefab` - 内壁
- `Wall_Corner.prefab` - コーナー壁

#### 階段
- `StairsDown.prefab` - 下り階段
- `StairsUp.prefab` - 上り階段

### 2. 装飾オブジェクト

- `Pillar.prefab` - 柱
- `Torch.prefab` - 松明
- `Barrel.prefab` - 樽
- `Crate.prefab` - 木箱
- `Chest.prefab` - 宝箱

### 3. ライティング

- `RoomLight.prefab` - 部屋用ポイントライト
  - Type: Point Light
  - Range: 10
  - Intensity: 1.5
  - Color: Warm White (255, 244, 214)

- `CorridorLight.prefab` - 通路用ポイントライト
  - Type: Point Light
  - Range: 5
  - Intensity: 0.8
  - Color: Cool White (214, 228, 255)

### 4. DungeonVisualizerへのアサイン

```csharp
// GameManagerから呼び出し
DungeonVisualizer visualizer = GetComponent<DungeonVisualizer>();

// プレハブをアサイン
visualizer.floorPrefab = floorTile;
visualizer.wallPrefab = wallTile;
visualizer.stairsDownPrefab = stairsDown;
visualizer.stairsUpPrefab = stairsUp;

// ダンジョン生成後に視覚化
visualizer.VisualizeDungeon(tiles, rooms);
```

---

## アニメーション設定

### 1. Blend Tree (8方向移動)

#### Movement Blend Tree設定

```
Movement (2D Freeform Directional)
├─ Idle (0, 0)
├─ Walk_N (0, 1)
├─ Walk_NE (0.707, 0.707)
├─ Walk_E (1, 0)
├─ Walk_SE (0.707, -0.707)
├─ Walk_S (0, -1)
├─ Walk_SW (-0.707, -0.707)
├─ Walk_W (-1, 0)
└─ Walk_NW (-0.707, 0.707)

Parameters:
- DirectionX (Float)
- DirectionZ (Float)
```

### 2. Animation Events

#### 攻撃アニメーション
- **Frame 40%**: `OnAttackStart()` - 攻撃判定開始
- **Frame 60%**: `OnAttackHit()` - ダメージ発生
- **Frame 100%**: `OnAttackEnd()` - 攻撃終了

#### アイテム使用アニメーション
- **Frame 50%**: `OnUseItem()` - アイテム効果発動

---

## エフェクト

### 1. 攻撃エフェクト

#### 近接攻撃
- `SlashEffect.prefab` - 斬撃エフェクト
  - Particle System
  - Duration: 0.5s
  - Color: White → Transparent

#### 遠距離攻撃
- `ArrowEffect.prefab` - 矢エフェクト
- `MagicBoltEffect.prefab` - 魔法弾エフェクト

### 2. 魔法エフェクト

- `FireballEffect.prefab` - 火球
- `IceSpellEffect.prefab` - 氷魔法
- `ThunderEffect.prefab` - 雷魔法
- `HealEffect.prefab` - 回復魔法

### 3. システムエフェクト

- `LevelUpEffect.prefab` - レベルアップ演出
  - Particle System (上昇する光)
  - Duration: 2.0s
  - Color: Gold

- `DamageNumberEffect.prefab` - ダメージ数値表示
  - TextMeshPro
  - Animation: 上昇→フェードアウト

---

## 推奨アセット

### 無料アセット

#### キャラクター
1. **Mixamo** (https://www.mixamo.com/)
   - 無料のキャラクターモデル・アニメーション
   - Humanoidリグ対応

2. **Quaternius Ultimate Animated Creatures Pack**
   - Unity Asset Store無料
   - モンスター多数

#### 環境
1. **Modular Dungeon**
   - Unity Asset Store無料
   - ダンジョンタイルセット

2. **Simple Dungeon - Cartoon Assets**
   - Unity Asset Store無料
   - シンプルなダンジョン素材

#### エフェクト
1. **Cartoon FX Free**
   - Unity Asset Store無料
   - パーティクルエフェクト集

2. **Simple FX - Cartoon Particles**
   - Unity Asset Store無料
   - 魔法エフェクト多数

### 有料推奨アセット (オプション)

1. **Fantasy Characters Pack** ($29.99)
   - 高品質キャラクターモデル

2. **Medieval Dungeon Environment** ($49.99)
   - 本格的なダンジョン環境

3. **Magic Effects Pack** ($19.99)
   - プロ仕様のエフェクト

---

## セットアップ手順まとめ

### 1. アセットの配置

```
Assets/
├─ Models/
│  ├─ Characters/
│  │  ├─ Player/
│  │  └─ Enemies/
│  ├─ Environment/
│  │  ├─ Tiles/
│  │  └─ Props/
│  └─ Items/
├─ Animations/
│  ├─ Player/
│  └─ Enemies/
├─ Prefabs/
│  ├─ Characters/
│  ├─ Dungeon/
│  └─ Effects/
└─ Materials/
   ├─ Characters/
   └─ Environment/
```

### 2. ModelManagerへの登録

```csharp
// Inspectorで設定
ModelManager modelManager = FindObjectOfType<ModelManager>();

// プレイヤーモデル
modelManager.defaultPlayerModel = playerPrefab;

// 敵モデル
modelManager.enemyModels.Add(new EnemyModelData {
    enemyType = "Slime",
    displayName = "スライム",
    modelPrefab = slimePrefab
});

// エフェクト
modelManager.attackEffects.Add(new EffectData {
    effectName = "Slash",
    effectPrefab = slashEffect,
    duration = 0.5f
});
```

### 3. ゲームへの統合

```csharp
// Player.cs から呼び出し
GameObject playerModel = ModelManager.Instance.LoadPlayerModel(level, "Warrior");
playerModel.transform.SetParent(transform);

// Enemy.cs から呼び出し
GameObject enemyModel = ModelManager.Instance.LoadEnemyModel(enemyType, level);
enemyModel.transform.SetParent(transform);

// エフェクト再生
ModelManager.Instance.PlayAttackEffect("Slash", transform.position, transform.rotation);
```

---

## トラブルシューティング

### Q: アニメーションが再生されない
**A**: 
1. Animator Controllerが正しくアタッチされているか確認
2. Animation Parametersが正しく設定されているか確認
3. Animation Transitionsの条件を確認

### Q: モデルのスケールがおかしい
**A**: 
1. FBXインポート設定でScale Factorを確認
2. ModelManager.defaultScaleを調整

### Q: 装備がキャラクターに正しく装着されない
**A**: 
1. Humanoid Rigが正しく設定されているか確認
2. ボーン名が標準に準拠しているか確認
3. EquipmentModelDataのlocalPosition/Rotationを調整

### Q: エフェクトが表示されない
**A**: 
1. Particle Systemが有効か確認
2. Rendering ModeをWorld Spaceに設定
3. Sortinが LayerをUIより手前に設定

---

## 次のステップ

1. ✅ 3Dモデル・アニメーションスクリプト実装完了
2. ⏳ Mixamoから無料モデル・アニメーションをダウンロード
3. ⏳ Unityエディタでプレハブ作成
4. ⏳ ModelManagerへのアサイン
5. ⏳ ゲーム内でテストプレイ
6. ⏳ WebGLビルド最適化

---

**実装日**: 2025-12-04  
**バージョン**: 1.0  
**関連スクリプト**:
- `PlayerAnimationController.cs`
- `EnemyAnimationController.cs`
- `ModelManager.cs`
- `DungeonVisualizer.cs`
- `CameraController.cs`
- `EffectManager.cs`
