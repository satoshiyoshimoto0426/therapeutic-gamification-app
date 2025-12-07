# オーディオアセットガイド

「心の冒険者」Unity 3Dローグライクゲームのオーディオアセット導入ガイド

## 📋 目次

1. [概要](#概要)
2. [BGM（背景音楽）](#bgm背景音楽)
3. [SFX（効果音）](#sfx効果音)
4. [無料オーディオアセット](#無料オーディオアセット)
5. [AudioManagerセットアップ](#audiomanagerセットアップ)
6. [オーディオミキサー設定](#オーディオミキサー設定)
7. [統合方法](#統合方法)

---

## 概要

### 実装済みシステム

- ✅ **AudioManager.cs** (15,380 bytes) - BGM・SE統合管理
- ✅ **AudioTrigger.cs** (7,614 bytes) - ゲーム内イベントトリガー

### 必要なオーディオファイル

| カテゴリ | 数 | フォーマット | サンプルレート |
|---------|---|------------|--------------|
| BGM | 6種類 | .wav / .ogg | 44.1kHz |
| SFX | 30種類以上 | .wav | 44.1kHz |

---

## BGM（背景音楽）

### 必要なBGM一覧

| BGM名 | 用途 | 長さ | ムード | 優先度 |
|-------|------|------|--------|--------|
| **MainMenu** | メインメニュー | 2-3分 | 穏やか、希望 | 高 |
| **Dungeon_Normal** | 通常ダンジョン(1-10F) | 3-4分 | 探索、緊張 | 高 |
| **Dungeon_Mid** | 中層ダンジョン(11-20F) | 3-4分 | 緊迫、不安 | 高 |
| **Dungeon_Deep** | 深層ダンジョン(21-30F) | 3-4分 | 恐怖、絶望 | 高 |
| **Boss_Battle** | ボス戦 | 2-3分 | 激戦、勇気 | 高 |
| **GameOver** | ゲームオーバー | 30秒 | 悲しみ、挫折 | 中 |
| **Victory** | 勝利 | 30秒 | 喜び、達成感 | 中 |

### BGM仕様

**フォーマット**: 
- .ogg (推奨 - ファイルサイズ小、ループ対応)
- .wav (高品質だがファイルサイズ大)

**サンプルレート**: 44.1kHz (CD品質)

**ビットレート**: 
- .ogg: 128-192 kbps
- .wav: 16-bit

**ループ設定**: 
- Unity Inspector で Loop を有効化
- シームレスループを考慮した作曲

---

## SFX（効果音）

### プレイヤーアクション

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **Footstep** | 移動 | 0.1-0.2s | 高 |
| **Attack_Swing** | 攻撃スイング | 0.2-0.3s | 高 |
| **Attack_Hit** | 攻撃命中 | 0.1-0.2s | 高 |
| **Player_Damage** | 被ダメージ | 0.3-0.5s | 高 |
| **Player_Death** | 死亡 | 1-2s | 高 |

### 敵アクション

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **Enemy_Attack** | 敵攻撃 | 0.2-0.3s | 高 |
| **Enemy_Damage** | 敵ダメージ | 0.2-0.3s | 高 |
| **Enemy_Death** | 敵死亡 | 0.5-1s | 高 |

### アイテム

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **Item_Pickup** | アイテム取得 | 0.3-0.5s | 高 |
| **Item_Use** | アイテム使用 | 0.3-0.5s | 高 |
| **Heal** | 回復 | 0.5-1s | 高 |
| **Equip** | 装備 | 0.3-0.5s | 中 |

### UI

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **UI_Click** | ボタンクリック | 0.1s | 高 |
| **UI_Hover** | ボタンホバー | 0.05s | 中 |
| **UI_MenuOpen** | メニュー開く | 0.2-0.3s | 中 |
| **UI_MenuClose** | メニュー閉じる | 0.2-0.3s | 中 |
| **UI_Error** | エラー | 0.3-0.5s | 中 |

### システム

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **LevelUp** | レベルアップ | 1-2s | 高 |
| **Exp_Gain** | 経験値取得 | 0.3s | 中 |
| **Gold_Gain** | ゴールド取得 | 0.3s | 中 |
| **Stairs_Found** | 階段発見 | 0.5s | 中 |
| **Floor_Transition** | フロア移動 | 1s | 中 |

### ガチャ

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **Gacha_Start** | ガチャ開始 | 0.5s | 高 |
| **Gacha_Spin** | ガチャ回転 | 2-3s | 高 |
| **Gacha_Normal** | ノーマル排出 | 0.5s | 高 |
| **Gacha_Rare** | レア排出 | 1s | 高 |
| **Gacha_SuperRare** | SRレア排出 | 1.5s | 高 |
| **Gacha_Legendary** | レジェンド排出 | 2s | 高 |

### アンビエント（環境音）

| SE名 | 用途 | 長さ | 優先度 |
|------|------|------|--------|
| **Dungeon_Ambient** | ダンジョン環境音 | ループ | 低 |
| **Water_Splash** | 水音 | 0.5s | 低 |

---

## 無料オーディオアセット

### Unity Asset Store - BGM

#### 1. **Fantasy Music Pack** (無料)
**URL**: https://assetstore.unity.com/packages/audio/music/fantasy-music-pack-51245

**内容**:
- メインメニュー向けBGM
- ダンジョン探索BGM
- ボス戦BGM

#### 2. **Free Music Pack** (無料)
**URL**: https://assetstore.unity.com/packages/audio/music/free-music-pack-195752

**内容**:
- 複数ジャンルのBGM
- ループ対応

#### 3. **8-Bit Fantasy & Adventure Music** (無料)
**URL**: https://assetstore.unity.com/packages/audio/music/8-bit-fantasy-adventure-music-188211

**内容**:
- レトロな雰囲気のBGM
- ローグライクに最適

### Unity Asset Store - SFX

#### 1. **Universal Sound FX** (無料)
**URL**: https://assetstore.unity.com/packages/audio/sound-fx/universal-sound-fx-17256

**内容**:
- 500以上の効果音
- UI、アクション、システム音含む

#### 2. **Fantasy SFX** (無料)
**URL**: https://assetstore.unity.com/packages/audio/sound-fx/fantasy-sfx-32833

**内容**:
- 剣、魔法、モンスター
- RPG向けSE

#### 3. **Free Casual Game SFX Pack** (無料)
**URL**: https://assetstore.unity.com/packages/audio/sound-fx/free-casual-game-sfx-pack-54116

**内容**:
- UI効果音
- カジュアルなSE

### 外部サイト

#### 1. **Freesound.org**
**URL**: https://freesound.org/

**特徴**:
- 完全無料（CC0, CCライセンス）
- 膨大なSEライブラリ
- ダウンロード無制限

#### 2. **OpenGameArt.org**
**URL**: https://opengameart.org/

**特徴**:
- ゲーム用音楽・SE
- オープンソース
- 商用利用可能

#### 3. **Incompetech.com**
**URL**: https://incompetech.com/music/

**特徴**:
- Kevin MacLeod作のフリーBGM
- ジャンル豊富
- クレジット表記のみで使用可

---

## AudioManagerセットアップ

### 1. AudioManagerオブジェクト作成

```
Hierarchy:
├── AudioManager (GameObject)
    ├── AudioManager.cs (Script)
    ├── BGM_Source (AudioSource) - 自動生成
    └── SFX_Source_0 ~ 9 (AudioSource) - 自動生成
```

### 2. Inspector設定

#### Audio Mixer
```
Audio Mixer: GameAudioMixer (作成方法は後述)
```

#### BGM Settings
```
BGM Clips (リストサイズ: 7)
[0]
  Clip Name: MainMenu
  Audio Clip: MainMenu_BGM.ogg
  Description: メインメニューBGM

[1]
  Clip Name: Dungeon_Normal
  Audio Clip: Dungeon1_BGM.ogg
  Description: 通常ダンジョンBGM（1-10F）

[2]
  Clip Name: Dungeon_Mid
  Audio Clip: Dungeon2_BGM.ogg
  Description: 中層ダンジョンBGM（11-20F）

[3]
  Clip Name: Dungeon_Deep
  Audio Clip: Dungeon3_BGM.ogg
  Description: 深層ダンジョンBGM（21-30F）

[4]
  Clip Name: Boss_Battle
  Audio Clip: Boss_BGM.ogg
  Description: ボス戦BGM

[5]
  Clip Name: GameOver
  Audio Clip: GameOver_BGM.ogg
  Description: ゲームオーバーBGM

[6]
  Clip Name: Victory
  Audio Clip: Victory_BGM.ogg
  Description: 勝利BGM

BGM Fade Duration: 1.5
BGM Loop: ✓
```

#### SFX Settings
```
SFX Clips (リストサイズ: 30+)
[0]
  Clip Name: Footstep
  Audio Clip: footstep.wav
  Default Volume: 0.5
  Description: 移動音

[1]
  Clip Name: Attack_Swing
  Audio Clip: attack_swing.wav
  Default Volume: 1.0
  Description: 攻撃スイング音

// ... 以下同様に全てのSEを登録
```

#### Volume Settings
```
Master Volume: 1.0
BGM Volume: 0.7
SFX Volume: 1.0
```

---

## オーディオミキサー設定

### 1. Audio Mixerアセット作成

1. Project ウィンドウで右クリック
2. Create > Audio Mixer
3. 名前: `GameAudioMixer`

### 2. グループ構造

```
Master
├── BGM
├── SFX
└── Voice (将来的に追加)
```

### 3. 各グループの設定

#### Master
- Volume: 0 dB
- Exposed Parameter: "MasterVolume"

#### BGM
- Volume: -10 dB
- Exposed Parameter: "BGMVolume"
- Lowpass: Cutoff 22000 Hz

#### SFX
- Volume: 0 dB
- Exposed Parameter: "SFXVolume"

### 4. Exposed Parameters設定

1. Masterグループを選択
2. Volume右クリック → Expose "Volume (of Master)" to script
3. Exposed Parameters タブで "MyExposedParam" を "MasterVolume" に変更
4. BGM、SFXも同様に設定

---

## 統合方法

### 1. Player.cs への統合

```csharp
// Player.cs

// 移動時
public void Move(Vector2Int direction)
{
    // 既存の移動処理...
    
    // SE再生
    Audio.AudioTrigger.PlayFootstep();
}

// 攻撃時
public void Attack(Enemy enemy)
{
    // 攻撃開始
    Audio.AudioTrigger.PlayAttack();
    
    // 既存の攻撃処理...
    
    // ヒット時
    if (attackHit)
    {
        Audio.AudioTrigger.PlayAttackHit();
    }
}

// ダメージ受けた時
public void TakeDamage(int damage)
{
    // 既存のダメージ処理...
    
    // SE再生
    Audio.AudioTrigger.PlayTakeDamage();
}

// 死亡時
public void Die()
{
    // SE再生
    Audio.AudioTrigger.PlayPlayerDeath();
    
    // 既存の死亡処理...
}
```

### 2. Enemy.cs への統合

```csharp
// Enemy.cs

// 攻撃時
public void Attack(Player player)
{
    Audio.AudioTrigger.PlayEnemyAttack();
    // 既存の攻撃処理...
}

// ダメージ受けた時
public void TakeDamage(int damage)
{
    Audio.AudioTrigger.PlayEnemyDamage();
    // 既存のダメージ処理...
}

// 死亡時
public void Die()
{
    Audio.AudioTrigger.PlayEnemyDeath();
    // 既存の死亡処理...
}
```

### 3. GameManager.cs への統合

```csharp
// GameManager.cs

private void Start()
{
    // BGM再生
    Audio.AudioTrigger.PlayMenuBGM();
}

public void StartGame()
{
    // ダンジョンBGMに切り替え
    Audio.AudioTrigger.PlayDungeonBGM(currentFloor);
}

public void OnFloorChange(int newFloor)
{
    // フロア移動SE
    Audio.AudioTrigger.PlayFloorTransition();
    
    // BGM切り替え
    Audio.AudioTrigger.PlayDungeonBGM(newFloor);
}

public void OnBossBattle()
{
    // ボスBGMに切り替え
    Audio.AudioTrigger.PlayBossBGM();
}

public void OnGameOver()
{
    // ゲームオーバーBGM
    Audio.AudioTrigger.PlayGameOverBGM();
}
```

### 4. InventoryUI.cs への統合

```csharp
// InventoryUI.cs

public void Show()
{
    Audio.AudioTrigger.PlayMenuOpen();
    // 既存のUI表示処理...
}

public void Hide()
{
    Audio.AudioTrigger.PlayMenuClose();
    // 既存のUI非表示処理...
}

private void UseItem(Item item)
{
    Audio.AudioTrigger.PlayItemUse();
    
    // 回復アイテムの場合
    if (item is HealingItem)
    {
        Audio.AudioTrigger.PlayHeal();
    }
    
    // 既存のアイテム使用処理...
}
```

### 5. GachaUI.cs への統合

```csharp
// GachaUI.cs

public void ShowGachaScreen()
{
    Audio.AudioTrigger.PlayMenuOpen();
    // 既存のUI表示処理...
}

public void StartGacha()
{
    Audio.AudioTrigger.PlayGachaStart();
    Audio.AudioTrigger.PlayGachaSpin();
    
    // 既存のガチャ処理...
}

public void ShowGachaResult(Equipment equipment)
{
    // レアリティに応じたSE
    Audio.AudioTrigger.PlayGachaResult(equipment.rarity);
    
    // 既存の結果表示処理...
}
```

### 6. UIボタンへの統合

```csharp
// UI Button の OnClick イベントに追加

public void OnButtonClick()
{
    Audio.AudioTrigger.PlayButtonClick();
    // ボタン処理...
}

// EventTrigger でホバー検知
public void OnButtonHover()
{
    Audio.AudioTrigger.PlayButtonHover();
}
```

---

## ボリューム調整UI

### 設定画面の実装例

```csharp
// SettingsUI.cs

using UnityEngine.UI;
using KokoroNoBoukensha.Audio;

public class SettingsUI : MonoBehaviour
{
    public Slider masterVolumeSlider;
    public Slider bgmVolumeSlider;
    public Slider sfxVolumeSlider;

    private void Start()
    {
        // 現在の値を取得
        masterVolumeSlider.value = AudioManager.Instance.masterVolume;
        bgmVolumeSlider.value = AudioManager.Instance.bgmVolume;
        sfxVolumeSlider.value = AudioManager.Instance.sfxVolume;

        // リスナー登録
        masterVolumeSlider.onValueChanged.AddListener(OnMasterVolumeChanged);
        bgmVolumeSlider.onValueChanged.AddListener(OnBGMVolumeChanged);
        sfxVolumeSlider.onValueChanged.AddListener(OnSFXVolumeChanged);
    }

    private void OnMasterVolumeChanged(float value)
    {
        AudioManager.Instance.SetMasterVolume(value);
    }

    private void OnBGMVolumeChanged(float value)
    {
        AudioManager.Instance.SetBGMVolume(value);
    }

    private void OnSFXVolumeChanged(float value)
    {
        AudioManager.Instance.SetSFXVolume(value);
        
        // テストSE再生
        AudioTrigger.PlayButtonClick();
    }
}
```

---

## トラブルシューティング

### Q: 音が再生されない

**A**: 以下を確認:
1. AudioManager が Scene に存在するか
2. AudioClip が正しくアサインされているか
3. Volume が 0 になっていないか
4. Audio Listener が Camera にアタッチされているか

### Q: BGMがループしない

**A**:
1. AudioSource の Loop を有効化
2. AudioClip の Import Settings で Loop を確認

### Q: SEが重なって聞こえにくい

**A**:
1. maxSimultaneousSFX を調整
2. 重要なSEの volumeScale を上げる
3. Audio Mixer で優先度を設定

### Q: フェードがうまくいかない

**A**:
1. bgmFadeDuration を調整
2. Time.timeScale が 0 になっていないか確認

---

## オーディオファイル配置

```
Assets/
└── Audio/
    ├── BGM/
    │   ├── MainMenu_BGM.ogg
    │   ├── Dungeon1_BGM.ogg
    │   ├── Dungeon2_BGM.ogg
    │   ├── Dungeon3_BGM.ogg
    │   ├── Boss_BGM.ogg
    │   ├── GameOver_BGM.ogg
    │   └── Victory_BGM.ogg
    └── SFX/
        ├── Player/
        │   ├── footstep.wav
        │   ├── attack_swing.wav
        │   ├── attack_hit.wav
        │   ├── player_damage.wav
        │   └── player_death.wav
        ├── Enemy/
        │   ├── enemy_attack.wav
        │   ├── enemy_damage.wav
        │   └── enemy_death.wav
        ├── Items/
        │   ├── item_pickup.wav
        │   ├── item_use.wav
        │   ├── heal.wav
        │   └── equip.wav
        ├── UI/
        │   ├── ui_click.wav
        │   ├── ui_hover.wav
        │   ├── ui_menu_open.wav
        │   ├── ui_menu_close.wav
        │   └── ui_error.wav
        ├── System/
        │   ├── levelup.wav
        │   ├── exp_gain.wav
        │   ├── gold_gain.wav
        │   ├── stairs_found.wav
        │   └── floor_transition.wav
        └── Gacha/
            ├── gacha_start.wav
            ├── gacha_spin.wav
            ├── gacha_normal.wav
            ├── gacha_rare.wav
            ├── gacha_superrare.wav
            └── gacha_legendary.wav
```

---

## 次のステップ

1. ✅ AudioManager・AudioTrigger実装完了
2. ⏳ 無料アセットからBGM・SEをダウンロード
3. ⏳ AudioMixerを作成・設定
4. ⏳ AudioManagerに全てのクリップをアサイン
5. ⏳ 既存スクリプトにAudioTrigger呼び出しを追加
6. ⏳ ボリューム調整UIを作成
7. ⏳ テストプレイで音量バランスを調整

---

**作成日**: 2025-12-04  
**バージョン**: 1.0  
**関連スクリプト**:
- `AudioManager.cs`
- `AudioTrigger.cs`
