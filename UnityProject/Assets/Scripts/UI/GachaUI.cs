using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.UI
{
    /// <summary>
    /// ガチャUI管理
    /// </summary>
    public class GachaUI : MonoBehaviour
    {
        public static GachaUI Instance { get; private set; }

        [Header("UI Panels")]
        public GameObject gachaPanel;
        public GameObject resultPanel;
        public GameObject historyPanel;

        [Header("Gacha Buttons")]
        public Button normalGachaButton;
        public Button premiumGachaButton;
        public Button superGachaButton;
        public Button historyButton;
        public Button closeButton;

        [Header("Pull Buttons")]
        public Button singlePullButton;
        public Button multiPullButton;

        [Header("Info Display")]
        public TextMeshProUGUI gachaNameText;
        public TextMeshProUGUI probabilityText;
        public TextMeshProUGUI playerGoldText;
        public TextMeshProUGUI pityCounterText;

        [Header("Result Display")]
        public Transform resultItemContainer;
        public GameObject resultItemPrefab;
        public TextMeshProUGUI resultSummaryText;
        public Button resultCloseButton;

        [Header("History Display")]
        public Transform historyContainer;
        public GameObject historyItemPrefab;
        public Button historyCloseButton;

        [Header("Animation")]
        public GameObject gachaAnimationPrefab;
        public Transform animationContainer;
        public float animationDuration = 2f;

        [Header("Audio")]
        public AudioClip gachaStartSound;
        public AudioClip gachaRevealSound;
        public AudioClip legendarySound;

        private API.GachaType selectedGachaType = API.GachaType.Normal;
        private bool isOpen = false;
        private AudioSource audioSource;

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

            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
            }
        }

        private void Start()
        {
            // パネルを非表示で初期化
            if (gachaPanel != null) gachaPanel.SetActive(false);
            if (resultPanel != null) resultPanel.SetActive(false);
            if (historyPanel != null) historyPanel.SetActive(false);

            // ボタンイベント登録
            SetupButtonEvents();

            // ガチャイベント登録
            if (API.GachaManager.Instance != null)
            {
                API.GachaManager.Instance.OnGachaCompleted += OnGachaCompleted;
            }

            // デフォルトでノーマルガチャを選択
            SelectGachaType(API.GachaType.Normal);
        }

        private void Update()
        {
            // Gキーでガチャ画面を開閉
            if (Input.GetKeyDown(KeyCode.G))
            {
                ToggleGacha();
            }

            // Escキーで閉じる
            if (Input.GetKeyDown(KeyCode.Escape) && isOpen)
            {
                CloseGacha();
            }

            // プレイヤーのゴールドを更新
            UpdatePlayerGoldDisplay();
        }

        /// <summary>
        /// ボタンイベントをセットアップ
        /// </summary>
        private void SetupButtonEvents()
        {
            if (normalGachaButton != null)
            {
                normalGachaButton.onClick.AddListener(() => SelectGachaType(API.GachaType.Normal));
            }

            if (premiumGachaButton != null)
            {
                premiumGachaButton.onClick.AddListener(() => SelectGachaType(API.GachaType.Premium));
            }

            if (superGachaButton != null)
            {
                superGachaButton.onClick.AddListener(() => SelectGachaType(API.GachaType.Super));
            }

            if (singlePullButton != null)
            {
                singlePullButton.onClick.AddListener(OnSinglePullClicked);
            }

            if (multiPullButton != null)
            {
                multiPullButton.onClick.AddListener(OnMultiPullClicked);
            }

            if (historyButton != null)
            {
                historyButton.onClick.AddListener(ShowHistory);
            }

            if (closeButton != null)
            {
                closeButton.onClick.AddListener(CloseGacha);
            }

            if (resultCloseButton != null)
            {
                resultCloseButton.onClick.AddListener(CloseResult);
            }

            if (historyCloseButton != null)
            {
                historyCloseButton.onClick.AddListener(CloseHistory);
            }
        }

        /// <summary>
        /// ガチャ画面を開閉
        /// </summary>
        public void ToggleGacha()
        {
            if (isOpen)
            {
                CloseGacha();
            }
            else
            {
                OpenGacha();
            }
        }

        /// <summary>
        /// ガチャ画面を開く
        /// </summary>
        public void OpenGacha()
        {
            if (gachaPanel != null)
            {
                gachaPanel.SetActive(true);
                isOpen = true;

                // ゲームを一時停止
                if (Core.GameManager.Instance != null)
                {
                    Core.GameManager.Instance.PauseGame();
                }

                UpdateGachaInfo();
                Debug.Log("[GachaUI] Opened");
            }
        }

        /// <summary>
        /// ガチャ画面を閉じる
        /// </summary>
        public void CloseGacha()
        {
            if (gachaPanel != null)
            {
                gachaPanel.SetActive(false);
                isOpen = false;

                // ゲームを再開
                if (Core.GameManager.Instance != null)
                {
                    Core.GameManager.Instance.ResumeGame();
                }

                Debug.Log("[GachaUI] Closed");
            }
        }

        /// <summary>
        /// ガチャタイプを選択
        /// </summary>
        private void SelectGachaType(API.GachaType gachaType)
        {
            selectedGachaType = gachaType;
            UpdateGachaInfo();
        }

        /// <summary>
        /// ガチャ情報を更新
        /// </summary>
        private void UpdateGachaInfo()
        {
            if (API.GachaManager.Instance == null) return;

            // ガチャ名
            if (gachaNameText != null)
            {
                gachaNameText.text = GetGachaName(selectedGachaType);
            }

            // 確率表示
            if (probabilityText != null)
            {
                API.GachaProbabilityTable table = GetSelectedTable();
                probabilityText.text = table?.GetProbabilityText() ?? "";
            }

            // 天井カウンター
            UpdatePityDisplay();

            // ボタンのコスト表示
            UpdateButtonCosts();
        }

        /// <summary>
        /// プレイヤーのゴールド表示を更新
        /// </summary>
        private void UpdatePlayerGoldDisplay()
        {
            if (playerGoldText == null) return;

            Character.Player player = FindObjectOfType<Character.Player>();
            if (player != null)
            {
                playerGoldText.text = $"所持ゴールド: {player.stats.Gold}G";
            }
        }

        /// <summary>
        /// 天井カウンター表示を更新
        /// </summary>
        private void UpdatePityDisplay()
        {
            if (pityCounterText == null || API.GachaManager.Instance == null) return;

            int remaining = API.GachaManager.Instance.GetPityRemaining();
            pityCounterText.text = $"天井まで: あと{remaining}回";

            // 天井が近い場合は色を変える
            if (remaining <= 10)
            {
                pityCounterText.color = Color.yellow;
            }
            else if (remaining <= 5)
            {
                pityCounterText.color = Color.red;
            }
            else
            {
                pityCounterText.color = Color.white;
            }
        }

        /// <summary>
        /// ボタンのコスト表示を更新
        /// </summary>
        private void UpdateButtonCosts()
        {
            if (API.GachaManager.Instance == null) return;

            int singleCost = GetGachaCost(selectedGachaType);
            int multiCost = singleCost * 10;

            if (singlePullButton != null)
            {
                var buttonText = singlePullButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = $"単発 ({singleCost}G)";
                }
            }

            if (multiPullButton != null)
            {
                var buttonText = multiPullButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = $"10連 ({multiCost}G)";
                }
            }
        }

        /// <summary>
        /// 単発ガチャボタンがクリックされた
        /// </summary>
        private void OnSinglePullClicked()
        {
            if (API.GachaManager.Instance == null) return;

            PlaySound(gachaStartSound);
            API.GachaManager.Instance.DrawGacha(selectedGachaType, null);
        }

        /// <summary>
        /// 10連ガチャボタンがクリックされた
        /// </summary>
        private void OnMultiPullClicked()
        {
            if (API.GachaManager.Instance == null) return;

            PlaySound(gachaStartSound);
            API.GachaManager.Instance.DrawMultiGacha(selectedGachaType, 10, null);
        }

        /// <summary>
        /// ガチャ完了時のコールバック
        /// </summary>
        private void OnGachaCompleted(API.GachaResult result)
        {
            if (result == null) return;

            StartCoroutine(ShowGachaResultAnimation(result));
        }

        /// <summary>
        /// ガチャ結果アニメーションを表示
        /// </summary>
        private IEnumerator ShowGachaResultAnimation(API.GachaResult result)
        {
            // アニメーション演出
            if (gachaAnimationPrefab != null && animationContainer != null)
            {
                GameObject animation = Instantiate(gachaAnimationPrefab, animationContainer);
                yield return new WaitForSeconds(animationDuration);
                Destroy(animation);
            }

            PlaySound(gachaRevealSound);

            // レジェンドが含まれている場合は特別な演出
            if (result.HasLegendary())
            {
                PlaySound(legendarySound);
                // TODO: レジェンド専用の演出
            }

            // 結果画面を表示
            ShowResult(result);
        }

        /// <summary>
        /// 結果画面を表示
        /// </summary>
        private void ShowResult(API.GachaResult result)
        {
            if (resultPanel == null) return;

            resultPanel.SetActive(true);

            // 既存のアイテムをクリア
            ClearResultItems();

            // 結果アイテムを表示
            foreach (var item in result.items)
            {
                CreateResultItem(item);
            }

            // サマリーテキスト
            if (resultSummaryText != null)
            {
                resultSummaryText.text = $"結果: {result.GetSummary()}\n消費: {result.totalCost}G";
            }

            UpdatePityDisplay();
        }

        /// <summary>
        /// 結果アイテムを作成
        /// </summary>
        private void CreateResultItem(Items.Equipment equipment)
        {
            if (resultItemPrefab == null || resultItemContainer == null) return;

            GameObject itemObj = Instantiate(resultItemPrefab, resultItemContainer);
            GachaResultItemUI itemUI = itemObj.GetComponent<GachaResultItemUI>();

            if (itemUI != null)
            {
                itemUI.SetEquipment(equipment);
            }
        }

        /// <summary>
        /// 結果アイテムをクリア
        /// </summary>
        private void ClearResultItems()
        {
            if (resultItemContainer == null) return;

            foreach (Transform child in resultItemContainer)
            {
                Destroy(child.gameObject);
            }
        }

        /// <summary>
        /// 結果画面を閉じる
        /// </summary>
        private void CloseResult()
        {
            if (resultPanel != null)
            {
                resultPanel.SetActive(false);
            }
        }

        /// <summary>
        /// 履歴を表示
        /// </summary>
        private void ShowHistory()
        {
            if (historyPanel == null || API.GachaManager.Instance == null) return;

            historyPanel.SetActive(true);

            // 既存の履歴をクリア
            ClearHistoryItems();

            // 履歴を表示
            List<API.GachaResult> history = API.GachaManager.Instance.GetHistory();
            foreach (var result in history)
            {
                CreateHistoryItem(result);
            }
        }

        /// <summary>
        /// 履歴アイテムを作成
        /// </summary>
        private void CreateHistoryItem(API.GachaResult result)
        {
            if (historyItemPrefab == null || historyContainer == null) return;

            GameObject itemObj = Instantiate(historyItemPrefab, historyContainer);
            GachaHistoryItemUI itemUI = itemObj.GetComponent<GachaHistoryItemUI>();

            if (itemUI != null)
            {
                itemUI.SetResult(result);
            }
        }

        /// <summary>
        /// 履歴アイテムをクリア
        /// </summary>
        private void ClearHistoryItems()
        {
            if (historyContainer == null) return;

            foreach (Transform child in historyContainer)
            {
                Destroy(child.gameObject);
            }
        }

        /// <summary>
        /// 履歴を閉じる
        /// </summary>
        private void CloseHistory()
        {
            if (historyPanel != null)
            {
                historyPanel.SetActive(false);
            }
        }

        /// <summary>
        /// 選択中のガチャテーブルを取得
        /// </summary>
        private API.GachaProbabilityTable GetSelectedTable()
        {
            if (API.GachaManager.Instance == null) return null;

            switch (selectedGachaType)
            {
                case API.GachaType.Normal:
                    return API.GachaManager.Instance.normalGacha;
                case API.GachaType.Premium:
                    return API.GachaManager.Instance.premiumGacha;
                case API.GachaType.Super:
                    return API.GachaManager.Instance.superGacha;
                default:
                    return null;
            }
        }

        /// <summary>
        /// ガチャ名を取得
        /// </summary>
        private string GetGachaName(API.GachaType gachaType)
        {
            switch (gachaType)
            {
                case API.GachaType.Normal:
                    return "ノーマルガチャ";
                case API.GachaType.Premium:
                    return "プレミアムガチャ";
                case API.GachaType.Super:
                    return "スーパーガチャ";
                default:
                    return "ガチャ";
            }
        }

        /// <summary>
        /// ガチャコストを取得
        /// </summary>
        private int GetGachaCost(API.GachaType gachaType)
        {
            if (API.GachaManager.Instance == null) return 0;

            switch (gachaType)
            {
                case API.GachaType.Normal:
                    return API.GachaManager.Instance.normalGachaCost;
                case API.GachaType.Premium:
                    return API.GachaManager.Instance.premiumGachaCost;
                case API.GachaType.Super:
                    return API.GachaManager.Instance.superGachaCost;
                default:
                    return 0;
            }
        }

        /// <summary>
        /// サウンドを再生
        /// </summary>
        private void PlaySound(AudioClip clip)
        {
            if (audioSource != null && clip != null)
            {
                audioSource.PlayOneShot(clip);
            }
        }
    }

    /// <summary>
    /// ガチャ結果アイテムUI（プレハブで使用）
    /// </summary>
    public class GachaResultItemUI : MonoBehaviour
    {
        public Image iconImage;
        public TextMeshProUGUI nameText;
        public Image rarityBorder;
        public GameObject newBadge;

        public void SetEquipment(Items.Equipment equipment)
        {
            if (nameText != null)
            {
                nameText.text = equipment.itemName;
                nameText.color = equipment.GetRarityColor();
            }

            if (iconImage != null && equipment.icon != null)
            {
                iconImage.sprite = equipment.icon;
            }

            if (rarityBorder != null)
            {
                rarityBorder.color = equipment.GetRarityColor();
            }

            // TODO: 新規獲得かチェック
        }
    }

    /// <summary>
    /// ガチャ履歴アイテムUI（プレハブで使用）
    /// </summary>
    public class GachaHistoryItemUI : MonoBehaviour
    {
        public TextMeshProUGUI timestampText;
        public TextMeshProUGUI gachaTypeText;
        public TextMeshProUGUI summaryText;

        public void SetResult(API.GachaResult result)
        {
            if (timestampText != null)
            {
                timestampText.text = result.timestamp;
            }

            if (gachaTypeText != null)
            {
                gachaTypeText.text = $"{result.gachaType} x{result.pullCount}";
            }

            if (summaryText != null)
            {
                summaryText.text = result.GetSummary();
            }
        }
    }
}
