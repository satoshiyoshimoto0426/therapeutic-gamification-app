using UnityEngine;

namespace KokoroNoBoukensha.Audio
{
    /// <summary>
    /// オーディオトリガー
    /// ゲーム内の各イベントでAudioManagerを呼び出す静的メソッド集
    /// </summary>
    public static class AudioTrigger
    {
        #region BGM Triggers

        /// <summary>
        /// メインメニューBGM再生
        /// </summary>
        public static void PlayMenuBGM()
        {
            AudioManager.Instance?.PlayBGM("MainMenu");
        }

        /// <summary>
        /// ダンジョンBGM再生
        /// </summary>
        public static void PlayDungeonBGM(int floorLevel)
        {
            if (floorLevel >= 21)
            {
                AudioManager.Instance?.PlayBGM("Dungeon_Deep");
            }
            else if (floorLevel >= 11)
            {
                AudioManager.Instance?.PlayBGM("Dungeon_Mid");
            }
            else
            {
                AudioManager.Instance?.PlayBGM("Dungeon_Normal");
            }
        }

        /// <summary>
        /// ボスBGM再生
        /// </summary>
        public static void PlayBossBGM()
        {
            AudioManager.Instance?.PlayBGM("Boss_Battle");
        }

        /// <summary>
        /// ゲームオーバーBGM再生
        /// </summary>
        public static void PlayGameOverBGM()
        {
            AudioManager.Instance?.PlayBGM("GameOver");
        }

        /// <summary>
        /// 勝利BGM再生
        /// </summary>
        public static void PlayVictoryBGM()
        {
            AudioManager.Instance?.PlayBGM("Victory");
        }

        #endregion

        #region Player SFX Triggers

        /// <summary>
        /// 移動SE
        /// </summary>
        public static void PlayFootstep()
        {
            AudioManager.Instance?.PlaySFX("Footstep", 0.5f);
        }

        /// <summary>
        /// 攻撃SE
        /// </summary>
        public static void PlayAttack()
        {
            AudioManager.Instance?.PlaySFX("Attack_Swing");
        }

        /// <summary>
        /// 攻撃ヒットSE
        /// </summary>
        public static void PlayAttackHit()
        {
            AudioManager.Instance?.PlaySFX("Attack_Hit");
        }

        /// <summary>
        /// 被ダメージSE
        /// </summary>
        public static void PlayTakeDamage()
        {
            AudioManager.Instance?.PlaySFX("Player_Damage");
        }

        /// <summary>
        /// 死亡SE
        /// </summary>
        public static void PlayPlayerDeath()
        {
            AudioManager.Instance?.PlaySFX("Player_Death");
        }

        #endregion

        #region Enemy SFX Triggers

        /// <summary>
        /// 敵攻撃SE
        /// </summary>
        public static void PlayEnemyAttack()
        {
            AudioManager.Instance?.PlaySFX("Enemy_Attack");
        }

        /// <summary>
        /// 敵ダメージSE
        /// </summary>
        public static void PlayEnemyDamage()
        {
            AudioManager.Instance?.PlaySFX("Enemy_Damage");
        }

        /// <summary>
        /// 敵死亡SE
        /// </summary>
        public static void PlayEnemyDeath()
        {
            AudioManager.Instance?.PlaySFX("Enemy_Death");
        }

        #endregion

        #region Item SFX Triggers

        /// <summary>
        /// アイテム取得SE
        /// </summary>
        public static void PlayItemPickup()
        {
            AudioManager.Instance?.PlaySFX("Item_Pickup");
        }

        /// <summary>
        /// アイテム使用SE
        /// </summary>
        public static void PlayItemUse()
        {
            AudioManager.Instance?.PlaySFX("Item_Use");
        }

        /// <summary>
        /// 回復SE
        /// </summary>
        public static void PlayHeal()
        {
            AudioManager.Instance?.PlaySFX("Heal");
        }

        /// <summary>
        /// 装備SE
        /// </summary>
        public static void PlayEquip()
        {
            AudioManager.Instance?.PlaySFX("Equip");
        }

        #endregion

        #region UI SFX Triggers

        /// <summary>
        /// ボタンクリックSE
        /// </summary>
        public static void PlayButtonClick()
        {
            AudioManager.Instance?.PlaySFX("UI_Click");
        }

        /// <summary>
        /// ボタンホバーSE
        /// </summary>
        public static void PlayButtonHover()
        {
            AudioManager.Instance?.PlaySFX("UI_Hover", 0.3f);
        }

        /// <summary>
        /// メニュー開くSE
        /// </summary>
        public static void PlayMenuOpen()
        {
            AudioManager.Instance?.PlaySFX("UI_MenuOpen");
        }

        /// <summary>
        /// メニュー閉じるSE
        /// </summary>
        public static void PlayMenuClose()
        {
            AudioManager.Instance?.PlaySFX("UI_MenuClose");
        }

        /// <summary>
        /// エラーSE
        /// </summary>
        public static void PlayError()
        {
            AudioManager.Instance?.PlaySFX("UI_Error");
        }

        #endregion

        #region System SFX Triggers

        /// <summary>
        /// レベルアップSE
        /// </summary>
        public static void PlayLevelUp()
        {
            AudioManager.Instance?.PlaySFX("LevelUp");
        }

        /// <summary>
        /// 経験値取得SE
        /// </summary>
        public static void PlayExpGain()
        {
            AudioManager.Instance?.PlaySFX("Exp_Gain", 0.6f);
        }

        /// <summary>
        /// ゴールド取得SE
        /// </summary>
        public static void PlayGoldGain()
        {
            AudioManager.Instance?.PlaySFX("Gold_Gain");
        }

        /// <summary>
        /// 階段発見SE
        /// </summary>
        public static void PlayStairsFound()
        {
            AudioManager.Instance?.PlaySFX("Stairs_Found");
        }

        /// <summary>
        /// フロア移動SE
        /// </summary>
        public static void PlayFloorTransition()
        {
            AudioManager.Instance?.PlaySFX("Floor_Transition");
        }

        #endregion

        #region Gacha SFX Triggers

        /// <summary>
        /// ガチャ開始SE
        /// </summary>
        public static void PlayGachaStart()
        {
            AudioManager.Instance?.PlaySFX("Gacha_Start");
        }

        /// <summary>
        /// ガチャ回転SE
        /// </summary>
        public static void PlayGachaSpin()
        {
            AudioManager.Instance?.PlaySFX("Gacha_Spin");
        }

        /// <summary>
        /// ガチャ結果SE（レアリティ別）
        /// </summary>
        public static void PlayGachaResult(Items.Rarity rarity)
        {
            switch (rarity)
            {
                case Items.Rarity.Legendary:
                    AudioManager.Instance?.PlaySFX("Gacha_Legendary");
                    break;
                case Items.Rarity.SuperRare:
                    AudioManager.Instance?.PlaySFX("Gacha_SuperRare");
                    break;
                case Items.Rarity.Rare:
                    AudioManager.Instance?.PlaySFX("Gacha_Rare");
                    break;
                default:
                    AudioManager.Instance?.PlaySFX("Gacha_Normal");
                    break;
            }
        }

        #endregion

        #region Ambient SFX

        /// <summary>
        /// ダンジョンアンビエント再生（3D位置指定）
        /// </summary>
        public static void PlayDungeonAmbient(Vector3 position)
        {
            AudioManager.Instance?.PlaySFX3D("Dungeon_Ambient", position, 0.3f);
        }

        /// <summary>
        /// 水音再生（3D位置指定）
        /// </summary>
        public static void PlayWaterSplash(Vector3 position)
        {
            AudioManager.Instance?.PlaySFX3D("Water_Splash", position);
        }

        #endregion
    }
}
