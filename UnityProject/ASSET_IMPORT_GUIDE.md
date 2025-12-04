# アセットインポートガイド

「心の冒険者」Unity 3Dローグライクゲーム用の無料アセット入手・インポート手順

## 📋 目次

1. [Mixamo キャラクターモデル](#mixamo-キャラクターモデル)
2. [Unity Asset Store ダンジョンアセット](#unity-asset-store-ダンジョンアセット)
3. [Unity Asset Store エフェクト](#unity-asset-store-エフェクト)
4. [インポート後の設定](#インポート後の設定)

---

## Mixamo キャラクターモデル

Mixamoは無料でキャラクターモデルとアニメーションを提供しているAdobe製サービスです。

### 1. アカウント作成

1. https://www.mixamo.com/ にアクセス
2. Adobeアカウントでログイン（無料）

### 2. プレイヤーキャラクター

#### 推奨モデル: "Kaya" または "Remy"

**ダウンロード手順:**

1. Mixamo Characters タブ → "Kaya" を選択
2. "Download" ボタンをクリック
3. 設定:
   - Format: **FBX for Unity (.fbx)**
   - Pose: **T-Pose**
4. ダウンロード

**必要なアニメーション:**

同じキャラクターで以下のアニメーションをダウンロード:

| アニメーション名 | Mixamo検索ワード | 設定 |
|----------------|----------------|------|
| Idle | "Idle" | In Place, 30fps |
| Walk Forward | "Walking" | In Place, 30fps |
| Walk Backward | "Walking Backward" | In Place, 30fps |
| Walk Left | "Strafe Left" | In Place, 30fps |
| Walk Right | "Strafe Right" | In Place, 30fps |
| Attack (Sword) | "Sword Slash" | In Place, 30fps |
| Take Damage | "Reaction Hit" | In Place, 30fps |
| Death | "Death" | In Place, 30fps |
| Use Item | "Drinking" | In Place, 30fps |
| Level Up | "Victory" | In Place, 30fps |

**ダウンロード設定（アニメーション）:**
- Format: **FBX for Unity (.fbx)**
- Skin: **With Skin**
- Frames per second: **30**
- Keyframe Reduction: **Uniform**

### 3. 敵キャラクター

#### 雑魚敵 (Level 1-10)

**Slime**: プリミティブCubeで代用（Unity標準）

**Goblin**: Mixamo "Goblin" モデル
- アニメーション: Idle, Walk, Attack, Take Damage, Death

**Wolf**: Mixamo "Wolf" モデル
- アニメーション: Idle, Walk, Attack, Take Damage, Death

#### 中級敵 (Level 11-20)

**Orc**: Mixamo "Orc" モデル
- アニメーション: Idle, Walk, Attack, Take Damage, Death

**Skeleton**: Mixamo "Skeleton" モデル
- アニメーション: Idle, Walk, Attack, Take Damage, Death

#### ボス敵 (Level 21-30)

**Dragon**: Mixamo "Dragon" モデル
- アニメーション: Idle, Walk, Attack, Take Damage, Death, Special

### 4. Mixamoファイルの配置

ダウンロードしたFBXファイルを以下のように配置:

```
Assets/
└── Models/
    ├── Characters/
    │   ├── Player/
    │   │   ├── Kaya.fbx
    │   │   └── Animations/
    │   │       ├── Kaya_Idle.fbx
    │   │       ├── Kaya_Walk.fbx
    │   │       ├── Kaya_Attack.fbx
    │   │       ├── Kaya_TakeDamage.fbx
    │   │       ├── Kaya_Death.fbx
    │   │       ├── Kaya_UseItem.fbx
    │   │       └── Kaya_LevelUp.fbx
    │   └── Enemies/
    │       ├── Goblin/
    │       │   ├── Goblin.fbx
    │       │   └── Animations/
    │       ├── Wolf/
    │       ├── Orc/
    │       ├── Skeleton/
    │       └── Dragon/
    └── ...
```

---

## Unity Asset Store ダンジョンアセット

### 1. Modular Dungeon (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/3d/environments/dungeons/modular-dungeon-51337

**インポート手順:**
1. Unity エディタ → Window → Package Manager
2. "My Assets" タブ
3. "Modular Dungeon" を検索
4. "Download" → "Import"

**使用するプレハブ:**
- `Floor_1x1.prefab` → `DungeonVisualizer.floorPrefab`
- `Wall_1x1.prefab` → `DungeonVisualizer.wallPrefab`
- `Stairs_Down.prefab` → `DungeonVisualizer.stairsDownPrefab`
- `Pillar.prefab` → `DungeonVisualizer.decorationPrefabs`
- `Torch.prefab` → `DungeonVisualizer.decorationPrefabs`

### 2. Simple Dungeon - Cartoon Assets (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/3d/environments/dungeons/simple-dungeon-cartoon-assets-177892

**特徴:**
- ローポリ
- WebGL最適化済み
- カラフルで見やすい

### 3. Medieval Dungeon Props (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/3d/props/interior/medieval-dungeon-props-169555

**装飾オブジェクト:**
- Barrel (樽)
- Crate (木箱)
- Chest (宝箱)
- Candles (ろうそく)

---

## Unity Asset Store エフェクト

### 1. Cartoon FX Free (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/vfx/particles/cartoon-fx-free-109565

**使用するエフェクト:**
- `CFXR Slash` → 近接攻撃エフェクト
- `CFXR Hit` → ダメージエフェクト
- `CFXR Explosion` → 魔法エフェクト
- `CFXR Heal` → 回復エフェクト
- `CFXR Sparkle` → レベルアップエフェクト

### 2. Simple FX - Cartoon Particles (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/vfx/particles/simple-fx-cartoon-particles-67834

**魔法エフェクト:**
- Fire
- Ice
- Thunder
- Poison

### 3. Free Stylized Particles (無料)

**Asset Store URL:**
https://assetstore.unity.com/packages/vfx/particles/free-stylized-particles-196106

**追加エフェクト:**
- Arrow Trail
- Buff Effect
- Debuff Effect

---

## インポート後の設定

### 1. Mixamoモデルの設定

#### Step 1: モデルのインポート設定

1. FBXファイルを選択 → Inspector
2. **Model** タブ:
   - Scale Factor: **1.0**
   - Mesh Compression: **Off**
   - Read/Write Enabled: **✓**
   - Optimize Mesh: **✓**
   - Import BlendShapes: **✓** (表情がある場合)

3. **Rig** タブ:
   - Animation Type: **Humanoid**
   - Avatar Definition: **Create From This Model**
   - Optimize Game Objects: **✓**

4. **Animation** タブ (アニメーションFBXのみ):
   - Import Animation: **✓**
   - Bake Animations: **✓**
   - Resample Curves: **✓**
   - Anim. Compression: **Optimal**
   - Loop Time: **✓** (Idle, Walk系のみ)
   - Loop Pose: **✓** (Idle, Walk系のみ)

5. **Materials** タブ:
   - Material Creation Mode: **Standard (Legacy)**
   - Extract Materials: クリックして抽出

#### Step 2: Animator Controllerの作成

```
Assets/Animations/Player/PlayerAnimator.controller
```

**Parameters:**
- `IsMoving` (Bool)
- `DirectionX` (Float)
- `DirectionZ` (Float)
- `IsAttacking` (Bool)
- `Attack` (Trigger)
- `TakeDamage` (Trigger)
- `Death` (Trigger)
- `UseItem` (Trigger)
- `LevelUp` (Trigger)

**States:**
1. **Idle** (Default State)
   - Motion: Kaya_Idle

2. **Movement** (Blend Tree 2D Freeform Directional)
   - Parameter X: DirectionX
   - Parameter Y: DirectionZ
   - Motions:
     - (0, 0): Idle
     - (0, 1): Walk Forward
     - (1, 0): Walk Right
     - (0, -1): Walk Backward
     - (-1, 0): Walk Left

3. **Attack**
   - Motion: Kaya_Attack
   - Transition: Attack Trigger → Attack State
   - Exit Time: 1.0 → Idle

4. **TakeDamage**
   - Motion: Kaya_TakeDamage
   - Transition: TakeDamage Trigger → TakeDamage State
   - Exit Time: 1.0 → Idle

5. **Death**
   - Motion: Kaya_Death
   - Transition: Death Trigger → Death State
   - No Exit

6. **UseItem**
   - Motion: Kaya_UseItem
   - Exit Time: 1.0 → Idle

7. **LevelUp**
   - Motion: Kaya_LevelUp
   - Exit Time: 1.0 → Idle

#### Step 3: Prefabの作成

1. Hierarchy に空のGameObject作成 → 名前: `PlayerCharacter`
2. Kaya.fbx を子オブジェクトとして配置
3. PlayerCharacterに以下をアタッチ:
   - `Player.cs`
   - `PlayerAnimationController.cs`
   - `CapsuleCollider` (Height: 2, Radius: 0.3)
   - `Rigidbody` (Use Gravity: ✓, Constraints: Freeze Rotation X, Z)
4. PlayerAnimationControllerのInspectorで:
   - Animator: Kaya子オブジェクトのAnimatorをドラッグ
5. Prefab化: `Assets/Prefabs/Characters/PlayerCharacter.prefab`

### 2. 敵モデルの設定

同様の手順で各敵のPrefabを作成:

```
Assets/Prefabs/Characters/
├── Enemies/
│   ├── Goblin.prefab
│   ├── Wolf.prefab
│   ├── Orc.prefab
│   ├── Skeleton.prefab
│   └── Dragon.prefab
```

各Prefabに:
- `Enemy.cs`
- `EnemyAnimationController.cs`
- `CapsuleCollider`
- `Rigidbody`

### 3. ダンジョンタイルの設定

#### Floor Prefab

1. Modular Dungeonの `Floor_1x1` を Hierarchy に配置
2. Position: (0, 0, 0)
3. Scale: (1, 1, 1) ※ DungeonVisualizer.tileSize に合わせる
4. Collider追加: `BoxCollider`
   - Center: (0, -0.05, 0)
   - Size: (1, 0.1, 1)
5. Tag: "Floor"
6. Layer: "Ground"
7. Prefab化: `Assets/Prefabs/Dungeon/Floor_Normal.prefab`

#### Wall Prefab

1. Modular Dungeonの `Wall_1x1` を配置
2. Position: (0, 0, 0)
3. Scale: (1, 3, 1) ※ DungeonVisualizer.wallHeight
4. Collider追加: `BoxCollider`
   - Center: (0, 1.5, 0)
   - Size: (1, 3, 1)
5. Tag: "Wall"
6. Layer: "Obstacle"
7. Prefab化: `Assets/Prefabs/Dungeon/Wall_Normal.prefab`

#### Stairs Prefab

1. Modular Dungeonの `Stairs_Down` を配置
2. Collider追加: `BoxCollider` (Trigger: ✓)
3. Tag: "Stairs"
4. Script追加: `StairsTrigger.cs`
5. Prefab化: `Assets/Prefabs/Dungeon/StairsDown.prefab`

### 4. エフェクトの設定

#### 攻撃エフェクト

1. Cartoon FX Freeの `CFXR Slash` を配置
2. Particle Systemの設定:
   - Duration: 0.5
   - Start Lifetime: 0.3
   - Start Speed: 5
   - Start Size: 1
   - Loop: ✗
3. Prefab化: `Assets/Prefabs/Effects/AttackSlash.prefab`

#### レベルアップエフェクト

1. Cartoon FX Freeの `CFXR Sparkle` を配置
2. Particle System:
   - Duration: 2.0
   - Start Color: Gold (255, 215, 0)
   - Emission Rate: 50
3. Prefab化: `Assets/Prefabs/Effects/LevelUpEffect.prefab`

---

## ModelManagerへのアサイン

### GameManagerオブジェクトの設定

1. Hierarchyに空のGameObject作成 → 名前: `ModelManager`
2. `ModelManager.cs` をアタッチ
3. Inspectorで設定:

```csharp
// Player Models
Default Player Model: PlayerCharacter.prefab

// Enemy Models (サイズ: 6)
[0]
  Enemy Type: "Goblin"
  Display Name: "ゴブリン"
  Model Prefab: Goblin.prefab
[1]
  Enemy Type: "Wolf"
  Display Name: "オオカミ"
  Model Prefab: Wolf.prefab
[2]
  Enemy Type: "Orc"
  Display Name: "オーク"
  Model Prefab: Orc.prefab
[3]
  Enemy Type: "Skeleton"
  Display Name: "スケルトン"
  Model Prefab: Skeleton.prefab
[4]
  Enemy Type: "Dragon"
  Display Name: "ドラゴン"
  Model Prefab: Dragon.prefab

// Attack Effects (サイズ: 1)
[0]
  Effect Name: "Slash"
  Effect Prefab: AttackSlash.prefab
  Duration: 0.5
  Sound Effect: (オプション)

// Magic Effects (サイズ: 3)
[0] Fire
[1] Ice
[2] Thunder

// System Effects
Heal Effect: HealEffect.prefab
Level Up Effect: LevelUpEffect.prefab
```

### DungeonVisualizerの設定

1. GameManagerオブジェクトに `DungeonVisualizer.cs` をアタッチ
2. Inspectorで設定:

```csharp
// Tile Prefabs
Floor Prefab: Floor_Normal.prefab
Wall Prefab: Wall_Normal.prefab
Stairs Down Prefab: StairsDown.prefab
Stairs Up Prefab: StairsUp.prefab (同じもの)

// Decoration Objects (サイズ: 3)
[0] Pillar.prefab
[1] Torch.prefab
[2] Barrel.prefab

Decoration Spawn Chance: 0.1

// Lighting
Room Light Prefab: (次のステップで作成)
Corridor Light Prefab: (次のステップで作成)

// Materials
Floor Material: Floor_Mat
Wall Material: Wall_Mat
Special Room Material: SpecialFloor_Mat
```

---

## ライティングPrefabの作成

### Room Light

1. Hierarchy → Create → Light → Point Light
2. 設定:
   - Range: 10
   - Intensity: 1.5
   - Color: Warm White (255, 244, 214)
   - Shadows: Soft Shadows
3. Prefab化: `Assets/Prefabs/Lighting/RoomLight.prefab`

### Corridor Light

1. Hierarchy → Create → Light → Point Light
2. 設定:
   - Range: 5
   - Intensity: 0.8
   - Color: Cool White (214, 228, 255)
   - Shadows: No Shadows
3. Prefab化: `Assets/Prefabs/Lighting/CorridorLight.prefab`

---

## テストシーンの作成

### 1. TestScene.unity

```
Hierarchy:
├── ModelManager (ModelManager.cs, DungeonVisualizer.cs)
├── GameManager (GameManager.cs, TurnManager.cs)
├── Main Camera (CameraController.cs)
├── Directional Light
├── EventSystem
└── Canvas (HUD)
```

### 2. テスト手順

1. Play ボタンを押す
2. ダンジョンが生成されることを確認
3. プレイヤーキャラクターが表示されることを確認
4. WASDで移動し、アニメーションが切り替わることを確認
5. スペースキーで攻撃、エフェクトが再生されることを確認

---

## トラブルシューティング

### モデルが表示されない

**原因**: Materialが正しくインポートされていない

**解決策**:
1. FBXファイルを選択 → Inspector → Materials タブ
2. "Extract Materials" をクリック
3. 保存先フォルダを指定

### アニメーションが再生されない

**原因**: Animator Controllerが正しく設定されていない

**解決策**:
1. Animator Controllerを開く
2. Parametersが正しく設定されているか確認
3. Transitionsの条件を確認

### キャラクターが地面に埋まる/浮く

**原因**: Colliderの位置がずれている

**解決策**:
1. CapsuleColliderのCenterとHeightを調整
2. RigidbodyのConstraintsでY軸回転のみ許可

### エフェクトが表示されない

**原因**: Particle SystemのRendering Modeが間違っている

**解決策**:
1. Particle System → Renderer → Render Mode: **Billboard**
2. Sorting Layer: **Effects**

---

## 次のステップ

1. ✅ アセットのダウンロード
2. ✅ モデルのインポート
3. ✅ Prefabの作成
4. ✅ ModelManagerへのアサイン
5. ⏳ ゲームシーンでのテスト
6. ⏳ WebGLビルドのテスト

---

**作成日**: 2025-12-04  
**更新日**: 2025-12-04  
**バージョン**: 1.0
