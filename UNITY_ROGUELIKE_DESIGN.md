# 心の冒険者 - Unity 3Dローグライク設計書

## プロジェクト概要

**プロジェクト名**: 心の冒険者 (Kokoro no Boukensha)  
**ジャンル**: 3Dローグライク RPG × 習慣形成  
**ターゲット**: 不登校・発達障害のある子供たち  
**開発環境**: Unity 2022.3 LTS + C#  
**参考作品**: 風来のシレン、不思議のダンジョンシリーズ

---

## ゲームシステム設計

### 1. コアループ

```
現実世界のタスク達成
    ↓
ゲーム内で経験値・ゴールド獲得
    ↓
ダンジョン探索（ターン制）
    ↓
敵との戦闘・アイテム収集
    ↓
装備強化・レベルアップ
    ↓
ボス戦（週1回）
    ↓
ストーリー進行（AI生成）
    ↓
新しいタスク設定
```

---

## 技術仕様

### アーキテクチャ

```
Unity 3D Frontend (C#)
├── Scene Management
│   ├── MainMenu
│   ├── DungeonExploration
│   ├── Battle
│   ├── Inventory
│   └── Story
├── Game Systems
│   ├── Procedural Dungeon Generation
│   ├── Turn-based Movement
│   ├── Combat System
│   ├── Item & Equipment
│   ├── Character Stats
│   └── AI Enemy Behavior
├── UI/UX
│   ├── HUD (HP, Level, Inventory)
│   ├── Dialogue System
│   ├── Menu System
│   └── Tutorial Overlay
└── Backend Integration (API)
    ├── Authentication (JWT)
    ├── Task Management
    ├── XP & Gold Sync
    ├── Equipment Gacha
    └── AI Story Generation

Existing FastAPI Backend (Python)
├── Auth Service (Port 8000)
├── Core Game Service (Port 8001)
├── Task Management (Port 8002)
├── Mood Tracking (Port 8003)
├── AI Story Service (Port 8004)
└── RPG Economy (Gacha, Equipment)
```

---

## ダンジョン生成システム（風来のシレン風）

### 特徴
- **プロシージャル生成**: 毎回異なるダンジョン構造
- **部屋＋通路方式**: BSP（Binary Space Partitioning）アルゴリズム使用
- **敵・アイテム配置**: ランダム配置（難易度調整あり）
- **階層システム**: 地下1階～地下30階（ボスは10階・20階・30階）

### 生成アルゴリズム

```csharp
// DungeonGenerator.cs
public class DungeonGenerator
{
    // BSPでダンジョン生成
    public Dungeon Generate(int floor, int seed)
    {
        1. グリッドベースマップ作成（50x50マス）
        2. BSPで部屋分割（最小6x6、最大15x15）
        3. 部屋間を通路で接続
        4. プレイヤー開始位置（階段上）
        5. 階段下（次の階へ）配置
        6. 敵配置（floor * 2～4体）
        7. アイテム配置（floor * 1～3個）
        8. トラップ配置（floor * 0～2個）
    }
}
```

### マップ要素
- **床タイル**: 移動可能
- **壁**: 移動不可
- **階段**: 次の階へ進む
- **トラップ**: HP減少、状態異常
- **宝箱**: アイテム・装備入手

---

## ターン制システム

### 基本ルール
1. **プレイヤーの行動（1ターン）**
   - 移動（上下左右斜め8方向）
   - 攻撃（隣接する敵）
   - アイテム使用
   - 足踏み（ターン経過、HP自然回復）
   - スキル発動

2. **敵の行動（プレイヤー行動後）**
   - 視界内にプレイヤーがいれば追跡
   - 隣接していれば攻撃
   - ランダム移動（視界外）

3. **ターン経過効果**
   - 満腹度減少（100ターンごとに-1）
   - HP自然回復（満腹度50%以上で+1/ターン）
   - 状態異常継続時間減少

### 戦闘計算

```csharp
// CombatSystem.cs
public int CalculateDamage(Character attacker, Character defender)
{
    int baseDamage = attacker.Attack - defender.Defense;
    baseDamage = Mathf.Max(1, baseDamage); // 最低1ダメージ
    
    // クリティカル（10%確率で1.5倍）
    if (Random.value < 0.1f)
    {
        baseDamage = (int)(baseDamage * 1.5f);
    }
    
    return baseDamage;
}
```

---

## キャラクターシステム

### プレイヤー能力値

```csharp
public class PlayerStats
{
    // 基本ステータス
    public int Level;              // レベル（1～99）
    public int Experience;         // 現在経験値
    public int MaxHP;              // 最大HP
    public int CurrentHP;          // 現在HP
    public int Attack;             // 攻撃力
    public int Defense;            // 防御力
    public int Speed;              // 素早さ（行動順）
    
    // ローグライク固有
    public int Hunger;             // 満腹度（0～100）
    public int Gold;               // 所持ゴールド
    public int Floor;              // 現在の階層
    
    // 「心の冒険者」独自能力値
    public int Concentration;      // 集中力（タスク持続時間）
    public int ActionPoints;       // 行動力（設定可能タスク数）
    public int Willpower;          // 意志力（失敗時抵抗）
    public int Intelligence;       // 知力（効率的計画支援）
}
```

### レベルアップ計算

```csharp
// 経験値テーブル（シレン風）
public int GetRequiredExp(int level)
{
    return (int)(100 * Mathf.Pow(1.2f, level - 1));
}

public void LevelUp()
{
    Level++;
    MaxHP += Random.Range(3, 8);
    Attack += Random.Range(1, 3);
    Defense += Random.Range(1, 3);
    Speed += Random.Range(0, 2);
    CurrentHP = MaxHP;
}
```

---

## 装備・アイテムシステム

### 装備カテゴリ

```csharp
public enum EquipmentType
{
    Weapon,      // 武器（攻撃力+）
    Armor,       // 防具（防御力+）
    Shield,      // 盾（防御力++、攻撃-）
    Accessory,   // アクセサリー（特殊効果）
    Charm        // お守り（状態異常耐性）
}

public enum Rarity
{
    Normal,      // N （白）
    Rare,        // R （青）
    SuperRare,   // SR（紫）
    Legendary    // レジェンド（金）
}
```

### アイテムシステム

```csharp
public enum ItemType
{
    // 消費アイテム
    HPPotion,           // HP回復（+30HP）
    FullRecover,        // HP全回復
    BreadRation,        // 満腹度回復（+30）
    AntidoteHerb,       // 毒治療
    ScrollOfTeleport,   // ランダムワープ
    ScrollOfMap,        // 全マップ表示
    
    // 投擲アイテム
    Stone,              // 石（5ダメージ）
    Bomb,               // 爆弾（20ダメージ範囲）
    
    // 特殊アイテム
    RevivalGrass,       // 復活の草（死亡時1回復活）
    MonsterMeat         // モンスターの肉（変身）
}
```

### ガチャシステム連携

```csharp
// Gacha.cs - FastAPI連携
public async Task<Equipment> DrawGacha(int gachaType)
{
    // バックエンドAPI呼び出し
    var response = await apiClient.PostAsync(
        "http://localhost:8009/gacha/draw",
        new { user_id = playerId, gacha_type = gachaType }
    );
    
    var equipment = JsonUtility.FromJson<Equipment>(response);
    return equipment;
}
```

---

## 敵キャラクターシステム

### 敵AIパターン

```csharp
public enum EnemyAIType
{
    Passive,      // 攻撃されるまで動かない
    Patrol,       // 決まったルートを巡回
    Chase,        // プレイヤーを発見したら追いかける
    Ranged,       // 遠距離攻撃（射程3マス）
    Support,      // 仲間を回復・強化
    Boss          // ボス専用AI（複雑なパターン）
}
```

### 敵配置テーブル

| 階層 | 敵の種類 | 特徴 |
|------|---------|------|
| 1-5階 | 先延ばしスライム | 低HP、低攻撃力 |
| 3-8階 | 不安の影 | 状態異常：不安（命中率低下） |
| 6-12階 | 怒りオーガ | 高攻撃力、低防御 |
| 10階 | ボス：混乱のドラゴン | HP500、範囲攻撃 |
| 11-18階 | 孤独ゴースト | 分裂する |
| 15-22階 | 後悔の騎士 | 高防御、反撃持ち |
| 20階 | ボス：絶望のヒドラ | HP1000、3体同時戦闘 |
| 23-28階 | 自己否定デーモン | 能力値低下攻撃 |
| 30階 | 最終ボス：心の闇 | HP2000、全パターン使用 |

---

## UIシステム

### HUD構成

```
┌──────────────────────────────────────┐
│ HP: ████████░░ 80/100   Lv.12       │
│ 満腹度: ████████ 78/100              │
│ 階層: 地下7階                        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│                                      │
│         [ダンジョンビュー]            │
│                                      │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ [攻撃] [アイテム] [装備] [スキル]     │
└──────────────────────────────────────┘
```

### メニュー階層

```
メインメニュー
├── ダンジョンに潜る
├── 装備・アイテム管理
├── ステータス確認
├── 今日のタスク（LINE連携）
├── ストーリー閲覧
├── ガチャ
├── ギルド・コミュニティ
└── 設定
```

---

## バックエンドAPI連携

### 認証フロー

```csharp
// AuthManager.cs
public async Task<bool> Login(string username, string password)
{
    var response = await apiClient.PostAsync(
        "http://localhost:8000/auth/login",
        new { username, password }
    );
    
    if (response.IsSuccess)
    {
        var token = response.Data.access_token;
        PlayerPrefs.SetString("jwt_token", token);
        return true;
    }
    return false;
}
```

### タスク連携

```csharp
// TaskManager.cs
public async Task<List<TaskData>> GetDailyTasks()
{
    var response = await apiClient.GetAsync(
        "http://localhost:8002/tasks/daily"
    );
    return response.Data.tasks;
}

public async Task CompleteTask(string taskId)
{
    // タスク完了 → XP・ゴールド獲得
    var response = await apiClient.PostAsync(
        "http://localhost:8002/tasks/complete",
        new { task_id = taskId }
    );
    
    // ゲーム内に反映
    playerStats.Experience += response.Data.xp_earned;
    playerStats.Gold += response.Data.gold_earned;
}
```

### AIストーリー連携

```csharp
// StoryManager.cs
public async Task<string> GenerateDailyStory()
{
    var response = await apiClient.PostAsync(
        "http://localhost:8004/story/generate",
        new { 
            user_id = playerId,
            recent_actions = GetRecentPlayerActions()
        }
    );
    
    return response.Data.story_text;
}
```

---

## 開発ロードマップ

### Phase 1: コアシステム（Week 1-2）
- ✅ プロジェクト構造作成
- ✅ ダンジョン生成システム
- ✅ ターン制移動システム
- ✅ 基本戦闘システム

### Phase 2: ゲームプレイ（Week 3-4）
- ✅ アイテム・装備システム
- ✅ 敵AI実装
- ✅ UI/UX実装
- ✅ セーブ・ロード機能

### Phase 3: バックエンド連携（Week 5-6）
- ✅ 認証システム連携
- ✅ タスク管理連携
- ✅ XP・ゴールド同期
- ✅ ガチャシステム連携

### Phase 4: 高度機能（Week 7-8）
- ✅ AIストーリー統合
- ✅ ギルド・マルチプレイ要素
- ✅ チュートリアル実装
- ✅ 最終調整・バランシング

### Phase 5: デプロイ（Week 9）
- ✅ WebGLビルド
- ✅ パフォーマンス最適化
- ✅ ドキュメント整備
- ✅ 本番リリース

---

## フォルダ構造

```
UnityProject/
├── Assets/
│   ├── Scripts/
│   │   ├── Core/
│   │   │   ├── GameManager.cs
│   │   │   ├── TurnManager.cs
│   │   │   └── SaveManager.cs
│   │   ├── Dungeon/
│   │   │   ├── DungeonGenerator.cs
│   │   │   ├── Room.cs
│   │   │   ├── Corridor.cs
│   │   │   └── Tile.cs
│   │   ├── Character/
│   │   │   ├── Player.cs
│   │   │   ├── PlayerController.cs
│   │   │   ├── Enemy.cs
│   │   │   └── EnemyAI.cs
│   │   ├── Combat/
│   │   │   ├── CombatSystem.cs
│   │   │   ├── DamageCalculator.cs
│   │   │   └── StatusEffect.cs
│   │   ├── Items/
│   │   │   ├── Item.cs
│   │   │   ├── Equipment.cs
│   │   │   ├── Inventory.cs
│   │   │   └── EquipmentManager.cs
│   │   ├── UI/
│   │   │   ├── HUDManager.cs
│   │   │   ├── MenuManager.cs
│   │   │   ├── DialogueSystem.cs
│   │   │   └── InventoryUI.cs
│   │   ├── API/
│   │   │   ├── APIClient.cs
│   │   │   ├── AuthManager.cs
│   │   │   ├── TaskManager.cs
│   │   │   └── StoryManager.cs
│   │   └── Utilities/
│   │       ├── GridHelper.cs
│   │       ├── Pathfinding.cs
│   │       └── RandomHelper.cs
│   ├── Prefabs/
│   │   ├── Characters/
│   │   ├── Tiles/
│   │   ├── Items/
│   │   └── UI/
│   ├── Scenes/
│   │   ├── MainMenu.unity
│   │   ├── DungeonExploration.unity
│   │   └── Battle.unity
│   ├── Materials/
│   ├── Textures/
│   └── Audio/
├── Packages/
└── ProjectSettings/
```

---

## パフォーマンス最適化

### WebGL対応
- **オブジェクトプーリング**: 敵・アイテムの再利用
- **LOD（Level of Detail）**: 遠距離はポリゴン削減
- **バッチング**: ドローコール削減
- **非同期ロード**: シーン遷移の高速化

### メモリ管理
- **アセットバンドル**: 必要時のみロード
- **テクスチャ圧縮**: WebP/ETC2使用
- **音声圧縮**: Vorbis/MP3使用

---

## セキュリティ

### JWT認証
- トークンはPlayerPrefsに暗号化保存
- APIリクエストにBearer Token付与
- トークンの定期更新（7日間有効）

### チート対策
- **重要データはサーバー側管理**
  - 経験値
  - ゴールド
  - 装備
  - タスク達成状況
- **クライアント側は表示のみ**

---

## 次のステップ

1. **Unity 2022.3 LTSのインストール確認**
2. **新規Unityプロジェクト作成**
3. **基本フォルダ構造の作成**
4. **GitHubリポジトリへのコミット**
5. **ダンジョン生成プロトタイプの実装**

---

**開発開始日**: 2025-12-04  
**目標リリース**: 2025-02-04（2ヶ月後）  
**開発者**: 吉本達志 & Claude AI

---

## 参考資料

- 風来のシレンシリーズ（Chunsoft）
- ローグライクゲーム開発の基礎（技術書典）
- Unity公式ドキュメント
- 認知行動療法（CBT）ガイドライン
- ゲーミフィケーション研究論文
