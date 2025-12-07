# Changelog - 心の冒険者 (Kokoro no Boukensha)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Game Balance Tuner エディタツール（リアルタイムバランス調整）
- Object Pooling システム（パフォーマンス最適化）
- Pool Manager（複数プールの一括管理）
- 最終最適化ガイド（WebGL, バランス, テスト）
- 無料オーディオアセット推奨リスト
- JSON形式でのバランス設定エクスポート/インポート

### Changed
- ObjectPool.cs をより高機能なシステムに更新
- AudioManager のメモリ管理を最適化

---

## [0.9.0] - 2025-12-04

### Added
- **オーディオシステム完全実装**
  - AudioManager.cs（BGM/SFX管理、AudioMixer統合）
  - AudioTrigger.cs（50以上のトリガー関数）
  - AUDIO_ASSET_GUIDE.md（アセット推奨とセットアップ）
  - BGM 7種類対応（Title, Dungeon, Battle, Boss, GameOver, Victory, Ending）
  - SFX 30種類以上対応（Player, Enemy, Item, UI, Gacha, Ambient）
  - ボリューム個別制御（Master/BGM/SFX）
  - 3D空間SE再生
  - AudioSourceプーリング（最大10個同時再生）

- **チュートリアルシステム完全実装**
  - TutorialManager.cs（17ステップ、ハイブリッド進行）
  - TutorialUI.cs（タイプライター効果、進捗表示）
  - TutorialHighlight.cs（UI要素強調）
  - TutorialPointer.cs（3D/UIオブジェクト指示）
  - TutorialTrigger.cs（10種類のアクション検出）
  - TUTORIAL_INTEGRATION_GUIDE.md（統合手順）
  - 完了報酬: 100 EXP + 500 Gold

- **3Dアセット配置ツール**
  - ASSET_IMPORT_GUIDE.md（Mixamo/Unity Asset Storeインポート）
  - AssetSetupTool.cs（自動セットアップ、20KB）
  - PlaceholderPrefabGenerator.cs（プレースホルダー20種類以上）
  - ワンクリックで全プレースホルダー生成機能

### Changed
- README.md に統合手順を追加
- プロジェクト進捗: 95% → 100%（コア機能完成）

### Fixed
- 3Dモデルインポート時のFBX設定自動化
- Animator Controller自動生成機能

---

## [0.8.0] - 2025-12-03

### Added
- **3Dモデル・アニメーションシステム**
  - PlayerAnimationController.cs（8方向移動、戦闘アニメ）
  - EnemyAnimationController.cs（敵AI連動アニメ）
  - ModelManager.cs（動的ロード、装備表示）
  - DungeonVisualizer.cs（3Dダンジョン生成、ライティング）
  - CameraController.cs（プレイヤー追従、ズーム、回転、障害物回避）
  - EffectManager.cs（エフェクト再生管理）
  - AnimationHelper.cs（アニメーションユーティリティ）
  - 3D_MODEL_SETUP_GUIDE.md（セットアップガイド）

### Changed
- ゲームビューを2Dから3Dに完全移行
- 装備システムを3Dモデル対応に拡張

---

## [0.7.0] - 2025-12-02

### Added
- **ガチャシステム完全実装**
  - GachaManager.cs（3種類のガチャ、天井システム）
  - GachaUI.cs（ガチャ演出、結果表示）
  - GachaResultDisplay.cs（レアリティ別演出）
  - GachaHistoryUI.cs（履歴表示）
  - 通常ガチャ: 100ゴールド
  - レアガチャ: 300ゴールド
  - スーパーガチャ: 1000ゴールド
  - 天井システム: 50連で伝説確定

- **バックエンド連携強化**
  - GachaAPIClient.cs（FastAPI連携）
  - リアルタイムガチャ同期
  - ガチャ履歴バックエンド保存

### Changed
- ItemRarity列挙型を全システムで統一（N, R, SR, Legend）

---

## [0.6.0] - 2025-12-01

### Added
- **インベントリ・装備システム**
  - InventoryUI.cs（アイテム管理UI）
  - EquipmentUI.cs（装備管理UI、3部位: 武器/防具/アクセサリー）
  - ItemManager.cs（アイテムデータ管理）
  - Item.cs, Equipment.cs（アイテムクラス）
  - ドラッグ&ドロップ機能
  - アイテム使用/装備機能
  - レアリティ表示（N, R, SR, Legend）

### Fixed
- InventoryUIの重複表示バグ修正
- 装備解除時のステータス反映漏れ修正

---

## [0.5.0] - 2025-11-30

### Added
- **ターン制戦闘システム**
  - TurnManager.cs（ターン管理、順序制御）
  - CombatManager.cs（戦闘処理、ダメージ計算）
  - AttackCommand.cs, MoveCommand.cs（コマンドパターン実装）
  - 8方向移動対応（WASD + QEZC）
  - プレイヤー行動 → 敵全員行動のターン制

- **敵AIシステム**
  - EnemyAI.cs（追跡、攻撃判定）
  - 視野範囲による敵発見
  - A*パスファインディング（簡易版）

### Changed
- Player.csにターンベース移動を統合
- ダメージ計算式: `Max(1, 攻撃力 - 防御力)`

---

## [0.4.0] - 2025-11-29

### Added
- **プロシージャルダンジョン生成（BSPアルゴリズム）**
  - DungeonGenerator.cs（BSP分割、部屋・通路生成）
  - Room.cs（部屋データ構造）
  - ミニマップ表示機能
  - 階段配置（上り/下り）
  - 敵・アイテムランダム配置

### Changed
- 固定マップからプロシージャル生成に変更
- フロア数: 30階、ボス階: 10, 20, 30

---

## [0.3.0] - 2025-11-28

### Added
- **キャラクター移動・成長システム**
  - Player.cs（移動、経験値、レベルアップ）
  - Enemy.cs（敵基本クラス）
  - Slime.cs, Goblin.cs, Orc.cs, Dragon.cs（敵種別）
  - 8方向移動アニメーション
  - レベルアップによるステータス上昇
  - 空腹度システム

### Fixed
- 壁抜けバグ修正
- アニメーション遷移のスムーズ化

---

## [0.2.0] - 2025-11-27

### Added
- **Unityプロジェクト構造**
  - Core: GameManager, TurnManager, SaveManager
  - Dungeon: DungeonGenerator, TileManager
  - Character: Player, Enemy, BaseCharacter
  - Combat: CombatManager, DamageCalculator
  - Item: ItemManager, Inventory, Equipment
  - UI: HUDManager, InventoryUI, GachaUI
  - Backend: APIClient, AuthManager, TaskManager, StoryManager

- **バックエンド連携準備**
  - FastAPI接続スクリプト（認証、タスク、ガチャ、ストーリー）
  - JWT認証フロー

### Changed
- プロジェクトをUnity 2022.3 LTSに移行

---

## [0.1.0] - 2025-11-26

### Added
- **初期プロジェクト構想**
  - ゲーム設計書（UNITY_ROGUELIKE_DESIGN.md）
  - ターゲットプラットフォーム: WebGL, Windows, macOS, Linux
  - 技術スタック: Unity 2022.3 LTS, C# 9.0+
  - バックエンド: FastAPI (Python)
  - ゲームジャンル: 3Dローグライク（風来のシレン系）

- **コア設計**
  - 現実連携システム（リアルタスク → ゲーム報酬）
  - AIストーリー生成（OpenAI GPT-4 API）
  - ガチャシステム（N, R, SR, Legend）
  - 30階ダンジョン（10階ごとにボス）

---

## 今後の予定

### v1.0.0 (リリース候補)
- [ ] WebGLビルド最適化完了
- [ ] 全バグ修正
- [ ] チュートリアル完全統合
- [ ] オーディオアセット配置完了
- [ ] 最終バランス調整
- [ ] パフォーマンステスト（FPS 30+, ロード < 10秒）
- [ ] ドキュメント最終更新
- [ ] デプロイ準備

### v1.1.0 (追加コンテンツ)
- [ ] 新ダンジョンタイプ（火山、氷雪、森林）
- [ ] 追加キャラクタークラス（戦士、魔法使い、盗賊）
- [ ] マルチプレイヤー協力モード（検討中）
- [ ] モバイル最適化（iOS/Android）

### v1.2.0 (高度な機能)
- [ ] リーダーボード
- [ ] デイリークエスト
- [ ] シーズンイベント
- [ ] カスタムダンジョンエディタ

---

## 技術的負債

### 優先度: 高
- [ ] WebGLメモリ最適化（現在500MB → 目標200MB）
- [ ] AudioManagerのSEプーリング最適化

### 優先度: 中
- [ ] セーブデータのクラウド同期
- [ ] 敵AIのパスファインディング改善（A*完全実装）
- [ ] アニメーション遷移のさらなるスムーズ化

### 優先度: 低
- [ ] 設定画面の拡充（キーバインド変更、言語切替）
- [ ] アクセシビリティ機能（色覚サポート、字幕）

---

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## クレジット

### 使用アセット
- 3Dモデル: Mixamo, Unity Asset Store
- BGM: 魔王魂, DOVA-SYNDROME, MusMus
- 効果音: 効果音ラボ, ポケットサウンド
- Unity Asset Store Free Packages

### 開発チーム
- プロジェクトリード: @satoshiyoshimoto0426
- AI開発支援: Claude (Anthropic)

---

**プロジェクト**: 心の冒険者 - Unity 3Dローグライク  
**リポジトリ**: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app  
**ブランチ**: feature/unity-3d-roguelike
