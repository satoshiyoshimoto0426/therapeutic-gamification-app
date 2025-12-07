# 心の冒険者 - 無料オーディオアセット推奨リスト

このドキュメントでは、ゲームで使用できる無料のBGM・効果音アセットを紹介します。

## 📋 目次

1. [Unity Asset Store 推奨パッケージ](#unity-asset-store-推奨パッケージ)
2. [外部サイト（無料音源）](#外部サイト無料音源)
3. [ダウンロード＆インポート手順](#ダウンロードインポート手順)
4. [AudioManagerへの設定方法](#audiomanagerへの設定方法)

---

## 🎵 Unity Asset Store 推奨パッケージ

### BGM用アセット

#### 1. **Free Music Bundle - Orchestral & Fantasy**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/music/free-music-bundle-orchestral-fantasy-156712)
- **価格**: 無料
- **内容**: オーケストラ風のBGM 10曲
- **推奨用途**:
  - タイトル画面
  - ダンジョン探索
  - ボス戦
- **ライセンス**: 商用利用可能

#### 2. **RPG Music Pack**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/music/rpg-music-pack-85636)
- **価格**: 無料
- **内容**: RPG向けBGM 8曲
- **推奨用途**:
  - 街・拠点
  - 戦闘
  - イベント
- **ライセンス**: 商用利用可能

#### 3. **Fantasy Music Free Pack**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/music/fantasy-music-free-pack-220396)
- **価格**: 無料
- **内容**: ファンタジー系BGM 5曲
- **推奨用途**:
  - ダンジョン
  - ボス戦
  - エンディング
- **ライセンス**: 商用利用可能

### 効果音用アセット

#### 4. **Universal Sound FX**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/sound-fx/universal-sound-fx-17256)
- **価格**: 無料
- **内容**: 500種類以上の効果音
- **推奨用途**:
  - UI音
  - 攻撃音
  - アイテム音
  - 環境音
- **ライセンス**: 商用利用可能

#### 5. **Free SFX Pack**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/sound-fx/free-sfx-pack-155768)
- **価格**: 無料
- **内容**: ゲーム汎用効果音 100種類
- **推奨用途**:
  - 足音
  - ドア開閉
  - ボタン音
  - 魔法音
- **ライセンス**: 商用利用可能

#### 6. **8-Bit SFX**
- **URL**: [Unity Asset Store](https://assetstore.unity.com/packages/audio/sound-fx/8-bit-sfx-32831)
- **価格**: 無料
- **内容**: レトロゲーム風効果音 50種類
- **推奨用途**:
  - ガチャ演出
  - レベルアップ
  - アイテム取得
- **ライセンス**: 商用利用可能

---

## 🌐 外部サイト（無料音源）

### BGM素材サイト

#### 7. **魔王魂（Maoudamashii）**
- **URL**: https://maoudamashii.jokersounds.com/
- **価格**: 無料（クレジット表記推奨）
- **内容**: 日本の有名フリー音楽サイト、1000曲以上
- **推奨用途**:
  - ダンジョンBGM
  - 戦闘BGM
  - タイトル画面
- **ライセンス**: 商用利用可能、クレジット表記推奨

#### 8. **DOVA-SYNDROME**
- **URL**: https://dova-s.jp/
- **価格**: 無料（作曲者によってはクレジット必須）
- **内容**: 1万曲以上、多様なジャンル
- **推奨用途**:
  - 全般
- **ライセンス**: 楽曲ごとに異なる、要確認

#### 9. **MusMus**
- **URL**: https://musmus.main.jp/
- **価格**: 無料（クレジット表記推奨）
- **内容**: ゲーム向けBGM 400曲以上
- **推奨用途**:
  - RPGダンジョン
  - 戦闘シーン
- **ライセンス**: 商用利用可能

### 効果音素材サイト

#### 10. **効果音ラボ**
- **URL**: https://soundeffect-lab.info/
- **価格**: 無料（クレジット表記不要）
- **内容**: ゲーム向け効果音 2000種類以上
- **推奨用途**:
  - 攻撃音
  - UI音
  - 環境音
- **ライセンス**: 商用利用可能

#### 11. **ポケットサウンド**
- **URL**: https://pocket-se.info/
- **価格**: 無料
- **内容**: ゲーム効果音 1500種類
- **推奨用途**:
  - 戦闘音
  - アイテム音
  - システム音
- **ライセンス**: 商用利用可能

---

## 🛠️ ダウンロード＆インポート手順

### Unity Asset Storeからのインポート

```
1. Unity Editorを開く
2. Window → Asset Store
3. 検索窓でアセット名を検索
4. ダウンロード → Import
5. Import Unityパッケージウィンドウで「Import」をクリック
```

### 外部サイトからのダウンロード

```
1. 各サイトで音源をダウンロード（通常はMP3/WAV/OGG形式）
2. Unityプロジェクトの `Assets/Audio/BGM/` または `Assets/Audio/SFX/` にファイルをドラッグ
3. インポートされたAudioClipを選択
4. Inspector → Platform Settings → WebGL:
   - Load Type: Compressed In Memory (BGM) / Decompress On Load (SFX)
   - Compression Format: Vorbis (BGM) / PCM (短いSFX)
   - Quality: 70-100 (BGM) / 100 (SFX)
5. Apply
```

---

## 🎧 AudioManagerへの設定方法

### ステップ1: AudioClipの配置

```
UnityProject/
└── Assets/
    └── Audio/
        ├── BGM/
        │   ├── bgm_title.ogg
        │   ├── bgm_dungeon.ogg
        │   ├── bgm_battle.ogg
        │   ├── bgm_boss.ogg
        │   ├── bgm_gameover.ogg
        │   ├── bgm_victory.ogg
        │   └── bgm_ending.ogg
        └── SFX/
            ├── Player/
            │   ├── sfx_player_walk.wav
            │   ├── sfx_player_attack.wav
            │   ├── sfx_player_damage.wav
            │   └── sfx_player_death.wav
            ├── Enemy/
            │   ├── sfx_enemy_hit.wav
            │   ├── sfx_enemy_death.wav
            │   └── sfx_slime_move.wav
            ├── Item/
            │   ├── sfx_item_pickup.wav
            │   ├── sfx_item_use.wav
            │   ├── sfx_potion_drink.wav
            │   └── sfx_equipment_equip.wav
            ├── UI/
            │   ├── sfx_button_click.wav
            │   ├── sfx_menu_open.wav
            │   ├── sfx_menu_close.wav
            │   ├── sfx_levelup.wav
            │   └── sfx_notification.wav
            └── Gacha/
                ├── sfx_gacha_start.wav
                ├── sfx_gacha_roll.wav
                ├── sfx_gacha_result_normal.wav
                ├── sfx_gacha_result_rare.wav
                └── sfx_gacha_result_legend.wav
```

### ステップ2: AudioManagerの設定

1. **ヒエラルキーでAudioManagerを選択**

2. **Inspectorで各BGMクリップを設定**
   ```
   BGM Clips:
   - Title: bgm_title
   - Dungeon: bgm_dungeon
   - Battle: bgm_battle
   - Boss: bgm_boss
   - GameOver: bgm_gameover
   - Victory: bgm_victory
   - Ending: bgm_ending
   ```

3. **SFXクリップを設定**
   ```
   SFX Clips (Dictionary):
   - "player_walk": sfx_player_walk
   - "player_attack": sfx_player_attack
   - "player_damage": sfx_player_damage
   - "enemy_hit": sfx_enemy_hit
   - "item_pickup": sfx_item_pickup
   - "button_click": sfx_button_click
   - "gacha_roll": sfx_gacha_roll
   - "levelup": sfx_levelup
   // ... 他のSFXも同様に設定
   ```

### ステップ3: AudioMixerの設定

1. **AudioMixerを作成**
   ```
   Assets → Create → Audio Mixer
   名前: MainAudioMixer
   ```

2. **グループを作成**
   ```
   MainAudioMixer:
   ├── Master
   │   ├── BGM
   │   └── SFX
   ```

3. **Exposed Parametersを追加**
   ```
   - MasterVolume (Master/Volume)
   - BGMVolume (BGM/Volume)
   - SFXVolume (SFX/Volume)
   ```

4. **AudioManagerに設定**
   ```
   AudioManager Inspector:
   - Audio Mixer: MainAudioMixer
   ```

### ステップ4: 使用例（スクリプトから）

```csharp
using KokoroNoBoukensha.Audio;

// BGMを再生
AudioManager.Instance.PlayBGM(BGMType.Title);

// SEを再生
AudioTrigger.PlayPlayerAttack();

// ボリューム調整
AudioManager.Instance.SetMasterVolume(0.8f);
AudioManager.Instance.SetBGMVolume(0.7f);
AudioManager.Instance.SetSFXVolume(0.9f);

// 3D空間でSEを再生
AudioTrigger.PlaySE("enemy_hit", enemyPosition);
```

---

## 🎼 推奨BGM・SFX割り当て

### BGM

| シーン | 推奨アセット | ファイル名例 | ループ |
|--------|------------|------------|--------|
| タイトル画面 | RPG Music Pack | RPG_Title_Theme.ogg | Yes |
| ダンジョン探索 | Fantasy Music Free | Dungeon_Ambience.ogg | Yes |
| 通常戦闘 | Free Music Bundle | Battle_Action.ogg | Yes |
| ボス戦 | Fantasy Music Free | Boss_Battle_Epic.ogg | Yes |
| ゲームオーバー | RPG Music Pack | GameOver_Sad.ogg | No |
| 勝利 | 魔王魂 | Victory_Fanfare.ogg | No |
| エンディング | Free Music Bundle | Ending_Credits.ogg | Yes |

### SFX

| カテゴリ | アクション | 推奨アセット | ファイル名例 |
|---------|----------|------------|------------|
| プレイヤー | 歩行 | Universal Sound FX | footstep_stone.wav |
| プレイヤー | 攻撃 | Free SFX Pack | sword_slash.wav |
| プレイヤー | ダメージ | Universal Sound FX | player_hurt.wav |
| 敵 | 被弾 | Free SFX Pack | enemy_hit.wav |
| 敵 | 死亡 | Universal Sound FX | enemy_death.wav |
| アイテム | 拾得 | 効果音ラボ | item_get.wav |
| アイテム | 使用 | Free SFX Pack | potion_use.wav |
| UI | クリック | 8-Bit SFX | button_click.wav |
| UI | レベルアップ | 8-Bit SFX | levelup.wav |
| ガチャ | ロール | 効果音ラボ | gacha_spin.wav |
| ガチャ | 伝説 | 8-Bit SFX | legendary_fanfare.wav |

---

## ⚖️ ライセンス表記例

ゲーム内のクレジット画面やREADME.mdに以下のように記載します。

```markdown
## 使用音源

### BGM
- 魔王魂 (https://maoudamashii.jokersounds.com/)
- DOVA-SYNDROME (https://dova-s.jp/)
- MusMus (https://musmus.main.jp/)

### 効果音
- 効果音ラボ (https://soundeffect-lab.info/)
- ポケットサウンド (https://pocket-se.info/)

### Unity Asset Store
- Free Music Bundle - Orchestral & Fantasy
- Universal Sound FX
- 8-Bit SFX

全ての音源は各サイトのライセンスに従って使用しています。
```

---

## 🚀 クイックスタートガイド

### 最小構成でのセットアップ（30分）

1. **Unity Asset Storeから3つダウンロード**
   - Free Music Bundle (BGM 10曲)
   - Universal Sound FX (効果音 500種類)
   - 8-Bit SFX (ガチャ/システム音 50種類)

2. **AudioManagerに最小限のクリップを設定**
   - BGM: Title, Dungeon, Battle
   - SFX: player_attack, enemy_hit, item_pickup, button_click, levelup

3. **AudioMixerを作成・設定**

4. **テスト再生**
   ```csharp
   AudioManager.Instance.PlayBGM(BGMType.Title);
   AudioTrigger.PlayButtonClick();
   ```

これで基本的なオーディオ機能が動作します！

---

## 📝 関連ドキュメント

- `AUDIO_ASSET_GUIDE.md` - オーディオシステム詳細
- `WEBGL_OPTIMIZATION_GUIDE.md` - WebGL向けオーディオ最適化
- `FINAL_OPTIMIZATION_GUIDE.md` - 最終調整ガイド

---

**最終更新**: 2025-12-04  
**バージョン**: 1.0  
**プロジェクト**: 心の冒険者 - Unity 3Dローグライク
