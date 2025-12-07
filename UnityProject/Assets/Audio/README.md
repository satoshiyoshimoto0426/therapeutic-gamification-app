# Audio Assets Directory

このディレクトリにはゲームで使用するBGMと効果音を配置します。

## 📁 ディレクトリ構造

```
Assets/Audio/
├── BGM/
│   ├── bgm_title.ogg          # タイトル画面
│   ├── bgm_dungeon.ogg        # ダンジョン探索
│   ├── bgm_battle.ogg         # 通常戦闘
│   ├── bgm_boss.ogg           # ボス戦
│   ├── bgm_gameover.ogg       # ゲームオーバー
│   ├── bgm_victory.ogg        # 勝利
│   └── bgm_ending.ogg         # エンディング
│
└── SFX/
    ├── Player/
    │   ├── player_walk.wav
    │   ├── player_attack.wav
    │   ├── player_damage.wav
    │   └── player_death.wav
    │
    ├── Enemy/
    │   ├── enemy_hit.wav
    │   ├── enemy_death.wav
    │   └── slime_move.wav
    │
    ├── Item/
    │   ├── item_pickup.wav
    │   ├── item_use.wav
    │   ├── potion_drink.wav
    │   └── equipment_equip.wav
    │
    ├── UI/
    │   ├── button_click.wav
    │   ├── menu_open.wav
    │   ├── menu_close.wav
    │   ├── levelup.wav
    │   └── notification.wav
    │
    └── Gacha/
        ├── gacha_start.wav
        ├── gacha_roll.wav
        ├── gacha_result_normal.wav
        ├── gacha_result_rare.wav
        └── gacha_result_legend.wav
```

## 🎵 推奨アセット

詳細は`/UnityProject/FREE_AUDIO_ASSETS.md`を参照してください。

### Unity Asset Store（無料）
1. **Free Music Bundle** - BGM用
2. **Universal Sound FX** - 汎用効果音
3. **8-Bit SFX** - システム音・ガチャ音

### 外部サイト（無料）
1. **魔王魂** - BGM全般
2. **DOVA-SYNDROME** - BGM多数
3. **効果音ラボ** - 効果音2000種類以上

## ⚙️ インポート設定

### BGM（.ogg推奨）
```
Load Type: Compressed In Memory
Compression Format: Vorbis
Quality: 70-100
Sample Rate: 44100 Hz
```

### SFX（.wav推奨）
```
Load Type: Decompress On Load
Compression Format: PCM（短い音）/ ADPCM（長い音）
Quality: 100
Sample Rate: 22050 Hz
```

## 🔗 関連ドキュメント

- `FREE_AUDIO_ASSETS.md` - 詳細な推奨アセットリスト
- `AUDIO_ASSET_GUIDE.md` - AudioManagerセットアップ手順
