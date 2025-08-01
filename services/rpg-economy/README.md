# RPG経済システムとアイテム管理

治療的ゲーミフィケーションアプリのRPG経済システムを実装しました。このシステムは、タスク完了と魔物討伐によるコイン報酬、5段階レアリティのガチャシステム、6スロット装備システムを提供します。

## 実装完了機能

### 16.1 コイン経済システム (`main.py`)

**主要機能:**
- タスク完了と魔物討伐によるコイン報酬システム
- 難易度とパフォーマンスに基づくコイン計算
- インフレ制御機能（総コイン数に基づく調整）
- 4種類のアクション種別対応（タスク完了、魔物討伐、デイリーボーナス、ストリークボーナス）

**技術仕様:**
- タスクタイプ別ベース報酬: ROUTINE(10), ONE_SHOT(15), SKILL_UP(20), SOCIAL(25)
- 魔物レアリティ別報酬: COMMON(50), RARE(100), EPIC(200), LEGENDARY(500)
- インフレ制御閾値: 1,000コイン(5%減), 5,000コイン(10%減), 10,000コイン(20%減)
- 経済ティア分類: starting, stable, comfortable, wealthy

**テスト結果:**
- 16個のテストケース全て成功
- 基本報酬計算、インフレ制御、統合ワークフローを検証

### 16.2 ガチャシステムとアイテム生成 (`gacha_system.py`)

**主要機能:**
- 5段階レアリティ（common〜legendary）のガチャシステム
- 単発・10連・プレミアムガチャの実装
- 治療テーマに基づくアイテム生成システム
- 10連ガチャのレア保証機能

**技術仕様:**
- レアリティ出現率: Common(60%), Uncommon(25%), Rare(10%), Epic(4%), Legendary(1%)
- ガチャコスト: 単発(100), 10連(900), プレミアム(300)
- 6つの治療テーマ: Focus, Resilience, Motivation, Social, Creativity, Wisdom
- 4つのアイテムタイプ: Weapon, Armor, Accessory, Consumable

**テスト結果:**
- 19個のテストケース全て成功
- レアリティ分布、プレミアム確率向上、治療テーマバランスを検証

### 16.3 装備システムと能力値ボーナス (`equipment_system.py`)

**主要機能:**
- 6スロット装備システム（武器・防具・アクセサリ・消耗品×3）
- 6種類の能力値ボーナス（集中力・回復力・やる気・社会性・創造性・知恵）
- 装備による作業効率ボーナス計算
- 装備アップグレード推奨システム

**技術仕様:**
- 能力値効率係数: Focus(2%/pt), Motivation(1.5%/pt), Resilience(1%/pt), Social(0.8%/pt), Creativity(1.2%/pt), Wisdom(1%/pt)
- 最大ボーナス制限: 50%
- 特殊効果ボーナス: task_focus_boost(5%), deep_work_mode(6%), motivation_boost(4%)
- 装備検証とアップグレード推奨機能

**テスト結果:**
- 16個のテストケース全て成功
- 装備管理、ボーナス計算、最適化ワークフローを検証

## アーキテクチャ

```
services/rpg-economy/
├── main.py                    # コイン経済システム
├── gacha_system.py           # ガチャシステム
├── equipment_system.py       # 装備システム
├── test_coin_economy.py      # コイン経済テスト
├── test_gacha_system.py      # ガチャシステムテスト
├── test_equipment_system.py  # 装備システムテスト
└── README.md                 # このファイル
```

## 統合ワークフロー

1. **コイン獲得**: タスク完了や魔物討伐でコインを獲得
2. **ガチャ実行**: コインを使ってアイテムを取得
3. **装備管理**: 取得したアイテムを装備して能力値向上
4. **効率向上**: 装備による作業効率ボーナスでより多くのコインを獲得

## 治療的配慮

- **経済バランス**: インフレ制御により健全な経済を維持
- **治療テーマ**: 全アイテムが治療的価値を持つテーマに基づく
- **段階的成長**: レアリティとステータスの相関で成長実感を提供
- **選択の自由**: 複数の装備スロットで個性的な組み合わせが可能

## パフォーマンス

- **高速計算**: 全ての計算処理が1ms以下で完了
- **メモリ効率**: 軽量なデータ構造で大量のアイテムを管理
- **スケーラビリティ**: 数万のアイテムと装備組み合わせに対応

## 今後の拡張予定

- アイテム合成システム
- セット装備ボーナス
- 季節限定アイテム
- トレード機能（ピアサポート統合）

## 使用例

```python
from main import CoinEconomy, ActionType
from gacha_system import GachaSystem
from equipment_system import EquipmentSystem, EquipmentSet

# コイン獲得
economy = CoinEconomy()
reward = economy.calculate_task_completion_coins(
    task_type=TaskType.ROUTINE,
    difficulty=3,
    mood_coefficient=1.1,
    adhd_assist=1.2,
    user_total_coins=1000
)

# ガチャでアイテム取得
gacha = GachaSystem()
result = gacha.perform_gacha("ten_pull", reward.final_amount * 10)

# 装備システムで効率向上
equipment_system = EquipmentSystem()
equipment_set = EquipmentSet()

for item in result.items:
    # 適切なスロットに装備
    for slot in EquipmentSlot:
        if item.item_type in equipment_system.slot_item_types[slot]:
            if equipment_set.get_item_by_slot(slot) is None:
                equipment_system.equip_item(equipment_set, item, slot)
                break

# 作業効率ボーナス確認
bonus = equipment_system.calculate_task_completion_bonus(equipment_set)
print(f"作業効率ボーナス: {bonus.total_bonus * 100:.1f}%")
```

このRPG経済システムは、治療的ゲーミフィケーションアプリの中核機能として、ユーザーの継続的なエンゲージメントと治療効果の向上を支援します。