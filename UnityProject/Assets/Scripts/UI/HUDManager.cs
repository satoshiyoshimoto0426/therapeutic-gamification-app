using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace KokoroNoBoukensha.UI
{
    /// <summary>
    /// HUD（ヘッドアップディスプレイ）管理
    /// プレイヤーのステータスを常時表示
    /// </summary>
    public class HUDManager : MonoBehaviour
    {
        public static HUDManager Instance { get; private set; }

        [Header("Player Stats")]
        public TextMeshProUGUI levelText;
        public TextMeshProUGUI hpText;
        public Slider hpBar;
        public TextMeshProUGUI hungerText;
        public Slider hungerBar;
        public TextMeshProUGUI goldText;
        public TextMeshProUGUI expText;
        public Slider expBar;

        [Header("Dungeon Info")]
        public TextMeshProUGUI floorText;
        public TextMeshProUGUI turnText;

        [Header("Notifications")]
        public TextMeshProUGUI notificationText;
        public float notificationDuration = 3f;

        [Header("Mini Map")]
        public RawImage miniMapImage;

        private Character.Player player;
        private float notificationTimer = 0f;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            player = FindObjectOfType<Character.Player>();
            
            if (notificationText != null)
            {
                notificationText.gameObject.SetActive(false);
            }
        }

        private void Update()
        {
            UpdateHUD();
            UpdateNotificationTimer();
        }

        /// <summary>
        /// HUDを更新
        /// </summary>
        private void UpdateHUD()
        {
            if (player == null)
            {
                player = FindObjectOfType<Character.Player>();
                if (player == null) return;
            }

            // レベル
            if (levelText != null)
            {
                levelText.text = $"Lv.{player.stats.Level}";
            }

            // HP
            if (hpText != null)
            {
                hpText.text = $"HP: {player.stats.CurrentHP}/{player.stats.MaxHP}";
            }

            if (hpBar != null)
            {
                hpBar.maxValue = player.stats.MaxHP;
                hpBar.value = player.stats.CurrentHP;
            }

            // 満腹度
            if (hungerText != null)
            {
                hungerText.text = $"満腹度: {player.stats.Hunger}/100";
            }

            if (hungerBar != null)
            {
                hungerBar.maxValue = 100;
                hungerBar.value = player.stats.Hunger;
            }

            // ゴールド
            if (goldText != null)
            {
                goldText.text = $"{player.stats.Gold}G";
            }

            // 経験値
            if (expText != null)
            {
                int requiredExp = GetRequiredExp(player.stats.Level);
                expText.text = $"EXP: {player.stats.Experience}/{requiredExp}";
            }

            if (expBar != null)
            {
                int requiredExp = GetRequiredExp(player.stats.Level);
                expBar.maxValue = requiredExp;
                expBar.value = player.stats.Experience;
            }

            // 階層
            if (floorText != null && Core.GameManager.Instance != null)
            {
                floorText.text = $"地下{Core.GameManager.Instance.currentFloor}階";
            }

            // ターン数
            if (turnText != null && Core.TurnManager.Instance != null)
            {
                turnText.text = $"Turn: {Core.TurnManager.Instance.GetCurrentTurn()}";
            }
        }

        /// <summary>
        /// 必要経験値を計算
        /// </summary>
        private int GetRequiredExp(int level)
        {
            return (int)(100 * Mathf.Pow(1.2f, level - 1));
        }

        /// <summary>
        /// 通知を表示
        /// </summary>
        public void ShowNotification(string message, Color? color = null)
        {
            if (notificationText == null) return;

            notificationText.text = message;
            notificationText.color = color ?? Color.white;
            notificationText.gameObject.SetActive(true);
            notificationTimer = notificationDuration;

            Debug.Log($"[HUD] Notification: {message}");
        }

        /// <summary>
        /// ダメージ通知
        /// </summary>
        public void ShowDamageNotification(int damage)
        {
            ShowNotification($"-{damage} HP", Color.red);
        }

        /// <summary>
        /// 回復通知
        /// </summary>
        public void ShowHealNotification(int amount)
        {
            ShowNotification($"+{amount} HP", Color.green);
        }

        /// <summary>
        /// 経験値獲得通知
        /// </summary>
        public void ShowExpGainNotification(int exp)
        {
            ShowNotification($"+{exp} EXP", Color.cyan);
        }

        /// <summary>
        /// レベルアップ通知
        /// </summary>
        public void ShowLevelUpNotification(int newLevel)
        {
            ShowNotification($"レベルアップ！ Lv.{newLevel}", Color.yellow);
        }

        /// <summary>
        /// ゴールド獲得通知
        /// </summary>
        public void ShowGoldGainNotification(int gold)
        {
            ShowNotification($"+{gold}G", Color.yellow);
        }

        /// <summary>
        /// アイテム獲得通知
        /// </summary>
        public void ShowItemGetNotification(string itemName)
        {
            ShowNotification($"{itemName} を入手", Color.white);
        }

        /// <summary>
        /// 通知タイマーを更新
        /// </summary>
        private void UpdateNotificationTimer()
        {
            if (notificationTimer > 0)
            {
                notificationTimer -= Time.deltaTime;

                if (notificationTimer <= 0 && notificationText != null)
                {
                    notificationText.gameObject.SetActive(false);
                }
            }
        }

        /// <summary>
        /// ミニマップを更新（将来実装用）
        /// </summary>
        public void UpdateMiniMap(Texture2D mapTexture)
        {
            if (miniMapImage != null && mapTexture != null)
            {
                miniMapImage.texture = mapTexture;
            }
        }

        /// <summary>
        /// HUDの表示/非表示
        /// </summary>
        public void SetHUDVisible(bool visible)
        {
            gameObject.SetActive(visible);
        }
    }
}
