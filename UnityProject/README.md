# 心の冒険者 - Unity 3Dローグライク

## プロジェクト概要

「心の冒険者」は、風来のシレン風の3Dローグライクゲームと現実世界のタスク管理を組み合わせた、革新的なゲームセラピーアプリです。

## 技術スタック

- **ゲームエンジン**: Unity 2022.3 LTS
- **言語**: C# 9.0+
- **バックエンド**: FastAPI (Python) - 既存のマイクロサービス群
- **ビルドターゲット**: WebGL, Windows, macOS, Linux

## プロジェクト構造

```
UnityProject/
├── Assets/
│   ├── Scripts/
│   │   ├── Core/              # コアシステム
│   │   │   ├── GameManager.cs         # ゲーム全体管理
│   │   │   ├── TurnManager.cs         # ターン制システム
│   │   │   └── SaveManager.cs         # セーブ/ロード
│   │   ├── Dungeon/           # ダンジョン生成
│   │   │   ├── DungeonGenerator.cs    # BSPダンジョン生成
│   │   │   ├── Room.cs                # 部屋クラス
│   │   │   └── Tile.cs                # タイルクラス
│   │   ├── Character/         # キャラクター
│   │   │   ├── Player.cs              # プレイヤー
│   │   │   ├── Enemy.cs               # 敵
│   │   │   └── EnemyAI.cs             # 敵AI
│   │   ├── Combat/            # 戦闘システム
│   │   │   ├── CombatSystem.cs        # 戦闘処理
│   │   │   └── StatusEffect.cs        # 状態異常
│   │   ├── Items/             # アイテム・装備
│   │   │   ├── Item.cs                # アイテム基底
│   │   │   ├── Equipment.cs           # 装備
│   │   │   ├── Inventory.cs           # インベントリ
│   │   │   └── EquipmentManager.cs    # 装備管理
│   │   ├── UI/                # ユーザーインターフェース
│   │   │   ├── HUDManager.cs          # HUD管理
│   │   │   ├── InventoryUI.cs         # インベントリUI
│   │   │   └── GachaUI.cs             # ガチャUI
│   │   ├── API/               # バックエンド連携
│   │   │   ├── APIClient.cs           # API通信
│   │   │   ├── AuthManager.cs         # 認証
│   │   │   ├── TaskManager.cs         # タスク管理
│   │   │   ├── StoryManager.cs        # AIストーリー
│   │   │   └── GachaManager.cs        # ガチャシステム
│   │   ├── Animation/         # アニメーションシステム
│   │   │   ├── PlayerAnimationController.cs  # プレイヤーアニメ
│   │   │   ├── EnemyAnimationController.cs   # 敵アニメ
│   │   │   ├── ModelManager.cs               # 3Dモデル管理
│   │   │   └── DungeonVisualizer.cs          # ダンジョン視覚化
│   │   ├── Tutorial/          # チュートリアルシステム
│   │   │   ├── TutorialManager.cs            # チュートリアル管理
│   │   │   ├── TutorialUI.cs                 # チュートリアルUI
│   │   │   ├── TutorialHighlight.cs          # ハイライト表示
│   │   │   ├── TutorialPointer.cs            # ポインター表示
│   │   │   └── TutorialTrigger.cs            # アクション検知
│   │   └── Utilities/         # ユーティリティ
│   │       ├── GridHelper.cs          # グリッド計算
│   │       ├── Pathfinding.cs         # 経路探索
│   │       └── AnimationHelper.cs     # アニメーション補助
│   ├── Prefabs/               # プレハブ
│   ├── Scenes/                # シーン
│   ├── Materials/             # マテリアル
│   ├── Textures/              # テクスチャ
│   └── Audio/                 # オーディオ
├── Packages/                  # パッケージ
└── ProjectSettings/           # プロジェクト設定
```

## ゲームシステム

### 1. ダンジョン探索

- **プロシージャル生成**: BSPアルゴリズムで毎回異なるダンジョン
- **階層システム**: 地下1階～地下30階
- **ボス戦**: 10階、20階、30階

### 2. ターン制バトル

- **8方向移動**: WASDキー + QEZCキーで斜め移動
- **ターン制**: プレイヤーの行動後に敵が行動
- **戦闘計算**: 攻撃力 - 防御力 = ダメージ

### 3. キャラクター成長

- **経験値システム**: 敵を倒してレベルアップ
- **ステータス上昇**: HP、攻撃力、防御力、素早さ
- **装備システム**: 武器、防具、アクセサリー

### 4. アイテム・装備

- **消費アイテム**: ポーション、食料、巻物
- **装備品**: 武器、防具、盾、アクセサリー
- **レアリティ**: N、R、SR、レジェンド

### 5. ガチャシステム

- **3種類のガチャ**: ノーマル、プレミアム、スーパー
- **レアリティシステム**: N、R、SR、レジェンド
- **天井保証**: 50連でレジェンド確定
- **装備獲得**: ランダムな武器・防具を入手
- **ガチャ履歴**: 過去の結果を確認可能

### 6. 現実連動システム

- **タスク管理**: 現実のタスクをゲーム内に反映
- **報酬システム**: タスク達成で経験値・ゴールド獲得
- **AIストーリー**: 行動に基づいて物語が生成される

## バックエンドAPI連携

### 認証サービス（Port 8000）

```csharp
// ログイン
AuthManager.Instance.Login(username, password, (success, message) => {
    if (success) {
        Debug.Log("ログイン成功");
    }
});
```

### タスク管理サービス（Port 8002）

```csharp
// 今日のタスクを取得
TaskManager.Instance.GetDailyTasks((tasks) => {
    foreach (TaskData task in tasks) {
        Debug.Log($"Task: {task.title}");
    }
});

// タスク完了
TaskManager.Instance.CompleteTask(taskId, (reward) => {
    player.GainExperience(reward.xp_earned);
    player.stats.Gold += reward.gold_earned;
});
```

### コアゲームサービス（Port 8001）

```csharp
// プレイヤーデータの同期
// TODO: CoreGameManagerクラスで実装予定
```

## 操作方法

### 基本操作

- **移動**: WASD / 矢印キー
- **斜め移動**: Q(左上) E(右上) Z(左下) C(右下)
- **足踏み**: スペースキー
- **攻撃**: 敵に向かって移動
- **アイテム使用**: Iキー（インベントリ）
- **メニュー**: Escキー

### ゲームフロー

1. メインメニューでログイン
2. 今日のタスクを確認
3. ダンジョンに潜る
4. 敵を倒して経験値・ゴールド獲得
5. 階段を見つけて次の階へ
6. ボスを倒してストーリー進行
7. 現実世界でタスク達成
8. ゲーム内で報酬を受け取る

## セットアップ

### 必要な環境

1. **Unity 2022.3 LTS** 以上
2. **Visual Studio 2022** または **VS Code**
3. **Git** (バージョン管理)

### インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git
cd therapeutic-gamification-app/UnityProject

# 2. Unity Hubでプロジェクトを開く
# Unity Hub > Add > UnityProject フォルダを選択

# 3. バックエンドサービスを起動（別ターミナル）
cd ..
python start_mvp_services.py
```

### アセットのセットアップ

#### オプション1: プレースホルダーを使用（すぐにテスト可能）

1. Unity エディタを開く
2. メニュー → **Tools > Kokoro no Boukensha > Generate All Placeholders**
3. 自動的にテスト用プレースホルダーPrefabが生成されます
4. すぐにゲームをテストできます

#### オプション2: 実際のアセットを使用（推奨）

1. **[ASSET_IMPORT_GUIDE.md](./ASSET_IMPORT_GUIDE.md)** を参照
2. Mixamoから無料キャラクターモデルをダウンロード
3. Unity Asset Storeから無料ダンジョン・エフェクトアセットをインポート
4. メニュー → **Tools > Kokoro no Boukensha > Asset Setup Tool** を使用
5. 各セクションのボタンをクリックして自動セットアップ

### 初回起動

1. Unityエディタでプロジェクトを開く
2. プレースホルダーを生成（上記参照）
3. `Scenes/MainMenu.unity` を開く
4. Playボタンを押してゲーム開始

## ビルド方法

### WebGLビルド

```bash
# Unity エディタ
File > Build Settings
> Platform: WebGL
> Switch Platform
> Build
```

### スタンドアロンビルド（Windows/Mac/Linux）

```bash
# Unity エディタ
File > Build Settings
> Platform: Windows/Mac/Linux
> Switch Platform
> Build
```

## 開発ガイド

### 新しい敵を追加

1. `Scripts/Character/Enemy.cs` を継承
2. `EnemyType` に新しいタイプを追加
3. AIの動作を `TakeTurn()` でカスタマイズ
4. プレハブを作成して `DungeonGenerator` に登録

### 新しいアイテムを追加

1. `Scripts/Items/Item.cs` を継承
2. `ItemType` に新しいタイプを追加
3. 効果を `Use()` メソッドで実装
4. プレハブを作成

### 新しいAPIエンドポイントを追加

1. `Scripts/API/` に新しいマネージャークラスを作成
2. `APIClient` を使用してリクエストを送信
3. レスポンスをデシリアライズ
4. ゲームロジックに統合

## テスト

### ユニットテスト

```bash
# Unity Test Runner
Window > General > Test Runner
> Run All Tests
```

### 統合テスト

```bash
# バックエンドAPIとの連携テスト
python test_integration_simple.py
```

## パフォーマンス最適化

### WebGL最適化

- オブジェクトプーリング（敵・アイテムの再利用）
- バッチング（ドローコール削減）
- LOD（遠距離のポリゴン削減）
- テクスチャ圧縮

### メモリ管理

- アセットバンドル（必要時のみロード）
- 非同期シーン読み込み
- 不要なオブジェクトの破棄

## トラブルシューティング

### ビルドエラー

```
Error: Could not find UnityEngine.dll
→ Unity 2022.3 LTS以上を使用してください
```

### API接続エラー

```
Error: Failed to connect to localhost:8000
→ バックエンドサービスが起動しているか確認
→ python start_mvp_services.py
```

### パフォーマンス問題

```
FPSが低い
→ Quality Settings でグラフィック品質を下げる
→ Edit > Project Settings > Quality
```

## ライセンス

MIT License

## 開発チーム

- **プロジェクトリード**: 吉本達志
- **ゲームデザイン**: AI + 臨床心理士
- **プログラミング**: Unity + FastAPI
- **アート**: プレースホルダー（将来的にアーティスト募集）

## リンク

- **ドキュメント**: [UNITY_ROGUELIKE_DESIGN.md](../UNITY_ROGUELIKE_DESIGN.md)
- **3Dモデルガイド**: [3D_MODEL_SETUP_GUIDE.md](./3D_MODEL_SETUP_GUIDE.md)
- **アセットインポートガイド**: [ASSET_IMPORT_GUIDE.md](./ASSET_IMPORT_GUIDE.md)
- **チュートリアル統合ガイド**: [TUTORIAL_INTEGRATION_GUIDE.md](./TUTORIAL_INTEGRATION_GUIDE.md)
- **元のプロジェクト**: [README.md](../README.md)
- **ビジネスプラン**: [kokoro_no_boukensha_business_presentation.pdf]

## 実装状況

### ✅ 完成したシステム (進捗: 90%)

1. **コアシステム** (100%)
   - ✅ GameManager - ゲーム全体管理
   - ✅ TurnManager - ターン制バトル
   - ✅ SaveManager - セーブ/ロード

2. **ダンジョンシステム** (100%)
   - ✅ DungeonGenerator - BSPプロシージャル生成
   - ✅ DungeonVisualizer - 3D環境構築
   - ✅ Room/Tile システム

3. **キャラクターシステム** (100%)
   - ✅ Player - プレイヤー制御・ステータス
   - ✅ Enemy - 敵AI・戦闘
   - ✅ 経験値・レベルアップ

4. **戦闘システム** (100%)
   - ✅ ターン制バトル
   - ✅ ダメージ計算
   - ✅ 状態異常

5. **アイテム・装備システム** (100%)
   - ✅ Inventory - インベントリ管理
   - ✅ Equipment - 装備システム
   - ✅ Item - 消費・投擲アイテム
   - ✅ レアリティシステム (N/R/SR/レジェンド)

6. **UIシステム** (100%)
   - ✅ HUDManager - ステータス表示
   - ✅ InventoryUI - インベントリ画面
   - ✅ GachaUI - ガチャ演出

7. **ガチャシステム** (100%)
   - ✅ GachaManager - 3種類のガチャ
   - ✅ 天井保証システム
   - ✅ ガチャ履歴・統計

8. **3Dモデル・アニメーション** (100%)
   - ✅ PlayerAnimationController - プレイヤーアニメーション
   - ✅ EnemyAnimationController - 敵アニメーション
   - ✅ ModelManager - 3Dモデル管理
   - ✅ AnimationHelper - 8方向移動補助
   - ✅ CameraController - カメラ制御
   - ✅ EffectManager - エフェクト管理

9. **バックエンド連携** (100%)
   - ✅ APIClient - HTTP通信
   - ✅ AuthManager - JWT認証
   - ✅ TaskManager - タスク管理連携
   - ✅ StoryManager - AIストーリー生成

### ⏳ 残タスク (進捗: 90%)

1. **3Dアセット配置** (0%)
   - ⏳ プレイヤーモデル（Mixamo等）
   - ⏳ 敵モデル（Mixamo等）
   - ⏳ ダンジョンタイルセット
   - ⏳ エフェクトプレハブ

2. **サウンド** (0%)
   - ⏳ BGM（メニュー、ダンジョン、ボス戦）
   - ⏳ SE（攻撃、移動、アイテム取得）

3. **チュートリアル** (0%)
   - ⏳ 操作説明
   - ⏳ システム説明

4. **WebGLビルド最適化** (0%)
   - ⏳ オブジェクトプーリング
   - ⏳ テクスチャ圧縮
   - ⏳ ロード時間短縮

---

**心の冒険者で、すべての子供たちが自分の人生の主人公になれる社会を目指します！**

   - ⏳ オブジェクトプーリング
   - ⏳ テクスチャ圧縮
   - ⏳ ロード時間短縮

3. **最終調整** (0%)
   - ⏳ バランス調整
   - ⏳ バグ修正
   - ⏳ パフォーマンステスト

---

**心の冒険者で、すべての子供たちが自分の人生の主人公になれる社会を目指します！**
