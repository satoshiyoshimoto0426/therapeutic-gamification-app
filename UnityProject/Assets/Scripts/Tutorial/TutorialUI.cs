using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

namespace KokoroNoBoukensha.Tutorial
{
    /// <summary>
    /// チュートリアルUI表示システム
    /// </summary>
    public class TutorialUI : MonoBehaviour
    {
        [Header("UI Elements")]
        [Tooltip("チュートリアルパネル")]
        public GameObject tutorialPanel;
        
        [Tooltip("タイトルテキスト")]
        public TextMeshProUGUI titleText;
        
        [Tooltip("説明テキスト")]
        public TextMeshProUGUI descriptionText;
        
        [Tooltip("進行状況テキスト")]
        public TextMeshProUGUI progressText;
        
        [Tooltip("次へボタン")]
        public Button nextButton;
        
        [Tooltip("スキップボタン")]
        public Button skipButton;
        
        [Tooltip("閉じるボタン")]
        public Button closeButton;

        [Header("Animation Settings")]
        [Tooltip("フェードイン時間")]
        public float fadeInDuration = 0.3f;
        
        [Tooltip("フェードアウト時間")]
        public float fadeOutDuration = 0.3f;
        
        [Tooltip("テキストタイプライター速度")]
        public float typewriterSpeed = 0.05f;

        [Header("Visual Effects")]
        [Tooltip("背景ぼかし")]
        public Image backgroundOverlay;
        
        [Tooltip("キャラクターアイコン")]
        public Image characterIcon;
        
        [Tooltip("キャラクターアイコンスプライト")]
        public Sprite tutorialCharacterSprite;

        private CanvasGroup canvasGroup;
        private TutorialStep currentStep;
        private bool isTyping = false;
        private Coroutine typingCoroutine;

        private void Awake()
        {
            // CanvasGroup取得または追加
            canvasGroup = tutorialPanel.GetComponent<CanvasGroup>();
            if (canvasGroup == null)
            {
                canvasGroup = tutorialPanel.AddComponent<CanvasGroup>();
            }

            // ボタンイベント設定
            if (nextButton != null)
            {
                nextButton.onClick.AddListener(OnNextButtonClicked);
            }

            if (skipButton != null)
            {
                skipButton.onClick.AddListener(OnSkipButtonClicked);
            }

            if (closeButton != null)
            {
                closeButton.onClick.AddListener(OnCloseButtonClicked);
            }

            // 初期状態は非表示
            Hide();
        }

        /// <summary>
        /// チュートリアルステップを表示
        /// </summary>
        public void ShowStep(TutorialStep step)
        {
            currentStep = step;

            // タイトル設定
            if (titleText != null)
            {
                titleText.text = step.title;
            }

            // 進行状況表示
            if (progressText != null)
            {
                int current = TutorialManager.Instance.CurrentStepIndex + 1;
                int total = TutorialManager.Instance.TotalSteps;
                progressText.text = $"ステップ {current} / {total}";
            }

            // キャラクターアイコン設定
            if (characterIcon != null && tutorialCharacterSprite != null)
            {
                characterIcon.sprite = tutorialCharacterSprite;
                characterIcon.enabled = true;
            }

            // 次へボタンの表示/非表示
            if (nextButton != null)
            {
                nextButton.gameObject.SetActive(step.waitForInput || step.stepType == TutorialStepType.Message);
            }

            // 説明テキストをタイプライター表示
            if (descriptionText != null)
            {
                if (typingCoroutine != null)
                {
                    StopCoroutine(typingCoroutine);
                }
                typingCoroutine = StartCoroutine(TypewriterEffect(step.description));
            }

            // フェードイン
            StartCoroutine(FadeIn());
        }

        /// <summary>
        /// タイプライターエフェクト
        /// </summary>
        private IEnumerator TypewriterEffect(string text)
        {
            isTyping = true;
            descriptionText.text = "";

            foreach (char c in text)
            {
                descriptionText.text += c;
                yield return new WaitForSeconds(typewriterSpeed);
            }

            isTyping = false;
        }

        /// <summary>
        /// タイプライターエフェクトをスキップ
        /// </summary>
        public void SkipTypewriter()
        {
            if (isTyping && typingCoroutine != null)
            {
                StopCoroutine(typingCoroutine);
                descriptionText.text = currentStep.description;
                isTyping = false;
            }
        }

        /// <summary>
        /// フェードイン
        /// </summary>
        private IEnumerator FadeIn()
        {
            tutorialPanel.SetActive(true);
            canvasGroup.alpha = 0f;
            canvasGroup.interactable = false;
            canvasGroup.blocksRaycasts = true;

            float elapsed = 0f;
            while (elapsed < fadeInDuration)
            {
                elapsed += Time.deltaTime;
                canvasGroup.alpha = Mathf.Clamp01(elapsed / fadeInDuration);
                yield return null;
            }

            canvasGroup.alpha = 1f;
            canvasGroup.interactable = true;
        }

        /// <summary>
        /// フェードアウト
        /// </summary>
        private IEnumerator FadeOut()
        {
            canvasGroup.interactable = false;

            float elapsed = 0f;
            while (elapsed < fadeOutDuration)
            {
                elapsed += Time.deltaTime;
                canvasGroup.alpha = Mathf.Clamp01(1f - (elapsed / fadeOutDuration));
                yield return null;
            }

            canvasGroup.alpha = 0f;
            canvasGroup.blocksRaycasts = false;
            tutorialPanel.SetActive(false);
        }

        /// <summary>
        /// 非表示
        /// </summary>
        public void Hide()
        {
            StartCoroutine(FadeOut());
        }

        /// <summary>
        /// 即座に非表示
        /// </summary>
        public void HideImmediate()
        {
            if (tutorialPanel != null)
            {
                tutorialPanel.SetActive(false);
                canvasGroup.alpha = 0f;
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
        }

        /// <summary>
        /// 次へボタンクリック
        /// </summary>
        private void OnNextButtonClicked()
        {
            // タイプライター中なら完了させる
            if (isTyping)
            {
                SkipTypewriter();
                return;
            }

            TutorialManager.Instance.NextStep();
        }

        /// <summary>
        /// スキップボタンクリック
        /// </summary>
        private void OnSkipButtonClicked()
        {
            // 確認ダイアログを表示
            ShowSkipConfirmation();
        }

        /// <summary>
        /// 閉じるボタンクリック
        /// </summary>
        private void OnCloseButtonClicked()
        {
            Hide();
        }

        /// <summary>
        /// スキップ確認ダイアログ
        /// </summary>
        private void ShowSkipConfirmation()
        {
            // TODO: 確認ダイアログの実装
            // 簡易実装
            if (UnityEngine.Application.isEditor)
            {
                Debug.Log("[TutorialUI] Skip confirmation - Yes");
                TutorialManager.Instance.SkipTutorial();
            }
            else
            {
                // 実際のゲームでは確認ダイアログを表示
                TutorialManager.Instance.SkipTutorial();
            }
        }

        /// <summary>
        /// 入力検知（キーボード）
        /// </summary>
        private void Update()
        {
            if (!tutorialPanel.activeSelf) return;

            // Enterキーで次へ
            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space))
            {
                OnNextButtonClicked();
            }

            // Escキーでスキップ確認
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                OnSkipButtonClicked();
            }
        }
    }
}
