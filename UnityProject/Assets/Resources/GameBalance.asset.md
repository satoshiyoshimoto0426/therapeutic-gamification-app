# GameBalance ScriptableObject の作成方法

このファイルは、ゲームバランス設定用のScriptableObjectを作成する手順を説明します。

## 📝 作成手順

### 1. Unity Editorで作成

```
1. Projectウィンドウで Assets/Resources フォルダを選択
   （Resourcesフォルダがない場合は作成）

2. 右クリック → Create → KokoroNoBoukensha → Game Balance

3. 作成されたアセット名を "GameBalance" に変更

4. Inspectorで各パラメータを設定
```

## ⚙️ デフォルト設定値

### Player Stats
- **Initial HP**: 100
- **Initial Attack**: 10
- **Initial Defense**: 5
- **HP Gain Per Level**: 10
- **Attack Gain Per Level**: 2
- **Defense Gain Per Level**: 1

### Experience
- **Base Exp Requirement**: 100
- **Exp Growth Rate**: 1.2

### Hunger System
- **Initial Hunger**: 100
- **Max Hunger**: 150
- **Hunger Decrease Per Turn**: 1
- **Hunger Damage**: 5

### Combat
- **Critical Chance**: 10%
- **Critical Multiplier**: 2.0
- **Dodge Chance**: 5%

### Enemy Stats
- **Enemy Level Multiplier**: 1.0
- **Enemy HP Multiplier**: 1.2
- **Enemy Attack Multiplier**: 0.9
- **Enemy Defense Multiplier**: 0.8

### Boss Stats
- **Boss HP Multiplier**: 5.0
- **Boss Attack Multiplier**: 1.5
- **Boss Defense Multiplier**: 1.2

### Rewards
- **Exp Reward Multiplier**: 1.0
- **Gold Reward Multiplier**: 1.0
- **Boss Exp Bonus**: 1000
- **Boss Gold Bonus**: 500

### Items
- **Potion Heal Amount**: 50
- **Food Hunger Amount**: 30
- **Item Drop Rate**: 30%

### Gacha
- **Normal Gacha Cost**: 100
- **Premium Gacha Cost**: 300
- **Super Gacha Cost**: 500
- **Gacha Pity Limit**: 50

### Dungeon
- **Dungeon Width**: 50
- **Dungeon Height**: 50
- **Min Room Size**: 4
- **Max Room Size**: 10
- **Max Enemies Per Floor**: 20
- **Max Items Per Floor**: 10

### Difficulty Scaling
- **Difficulty Scale Per Floor**: 1.05
- **Boss Floor Interval**: 10

## 🎮 使用方法

### スクリプトから参照

```csharp
using KokoroNoBoukensha.Core;

// Resourcesから読み込み
GameBalance balance = Resources.Load<GameBalance>("GameBalance");

// パラメータ取得
int playerHP = balance.initialHP;
int requiredExp = balance.GetExpRequirement(5); // レベル5に必要な経験値

// 敵のステータス計算
var (hp, attack, defense) = balance.CalculateEnemyStats(playerLevel: 5, floor: 3);

// 報酬計算
var (exp, gold) = balance.CalculateRewards(enemyLevel: 5, isBoss: false);
```

## 🔧 バランス調整

### Game Balance Tuner を使用（推奨）

```
Tools > Kokoro no Boukensha > Game Balance Tuner

1. 各タブでパラメータを調整
2. リアルタイムでプレビュー確認
3. "Apply Changes" で適用
4. "Export to JSON" でバックアップ
```

### 直接編集

```
1. Assets/Resources/GameBalance を選択
2. Inspectorで値を直接編集
3. Play Modeで確認
4. 適切な値が見つかったら保存
```

## 📊 バランステストのヒント

### プレイヤーが強すぎる場合
- Enemy HP Multiplier を 1.2 → 1.5 に上げる
- Enemy Attack Multiplier を 0.9 → 1.1 に上げる
- Exp Reward Multiplier を 1.0 → 0.8 に下げる

### プレイヤーが弱すぎる場合
- Initial HP を 100 → 120 に上げる
- Initial Attack を 10 → 12 に上げる
- Potion Heal Amount を 50 → 70 に上げる

### ゲームが簡単すぎる場合
- Difficulty Scale Per Floor を 1.05 → 1.08 に上げる
- Boss HP Multiplier を 5.0 → 7.0 に上げる

### ゲームが難しすぎる場合
- Item Drop Rate を 30% → 40% に上げる
- Hunger Decrease Per Turn を 1 → 0 にする（空腹システムOFF）

## 🔗 関連

- `GameBalance.cs` - ScriptableObject定義
- `GameBalanceTuner.cs` - エディタツール
- `FINAL_OPTIMIZATION_GUIDE.md` - バランス調整ガイド
