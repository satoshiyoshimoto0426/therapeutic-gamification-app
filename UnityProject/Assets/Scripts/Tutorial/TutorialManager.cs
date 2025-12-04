using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Tutorial
{
    /// <summary>
    /// チュートリアル管理システム
    /// ゲームの基本操作をステップバイステップで教える
    /// </summary>
    public class TutorialManager : MonoBehaviour
    {
        #region Singleton
        private static TutorialManager instance;
        public static TutorialManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<TutorialManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("TutorialManager");
                        instance = go.AddComponent<TutorialManager>();
                    }
                }
                return instance;
            }
        }
        #endregion

        [Header("Tutorial Settings")]
        [Tooltip("チュートリアルを有効化")]
        public bool tutorialEnabled = true;
        
        [Tooltip("チュートリアルを自動開始")]
        public bool autoStartTutorial = true;
        
        [Tooltip("チュートリアルをスキップ可能")]
        public bool allowSkip = true;

        [Header("UI References")]
        public TutorialUI tutorialUI;
        public TutorialHighlight highlightSystem;
        public TutorialPointer pointerSystem;

        [Header("Tutorial Steps")]
        public List<TutorialStep> tutorialSteps = new List<TutorialStep>();

        // 状態管理
        private int currentStepIndex = 0;
        private bool isTutorialActive = false;
        private bool isTutorialCompleted = false;
        private TutorialStep currentStep;

        // イベント
        public event Action<TutorialStep> OnStepStarted;
        public event Action<TutorialStep> OnStepCompleted;
        public event Action OnTutorialCompleted;
        public event Action OnTutorialSkipped;

        // プレイヤー参照
        private Character.Player player;
        private Core.GameManager gameManager;

        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (instance != this)
            {
                Destroy(gameObject);
                return;
            }

            InitializeTutorialSteps();
        }

        private void Start()
        {
            // プレイヤー参照を取得
            player = FindObjectOfType<Character.Player>();
            gameManager = Core.GameManager.Instance;

            // セーブデータからチュートリアル完了状態をロード
            LoadTutorialProgress();

            if (autoStartTutorial && !isTutorialCompleted && tutorialEnabled)
            {
                StartTutorial();
            }
        }

        /// <summary>
        /// チュートリアルステップを初期化
        /// </summary>
        private void InitializeTutorialSteps()
        {
            tutorialSteps = new List<TutorialStep>
            {
                // Step 1: ようこそ
                new TutorialStep
                {
                    stepId = "welcome",
                    title = "ようこそ、心の冒険者へ！",
                    description = "このゲームは、現実世界のタスクと連動したローグライクRPGです。\n" +
                                  "一緒に基本操作を学んでいきましょう！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                },

                // Step 2: 移動操作
                new TutorialStep
                {
                    stepId = "movement_basic",
                    title = "移動操作",
                    description = "WASDキーまたは矢印キーでキャラクターを移動できます。\n" +
                                  "試しに動いてみましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.Move,
                    highlightUI = "Movement",
                    showPointer = true,
                    pointerTarget = "Player"
                },

                // Step 3: 8方向移動
                new TutorialStep
                {
                    stepId = "movement_diagonal",
                    title = "斜め移動",
                    description = "Q（左上）、E（右上）、Z（左下）、C（右下）キーで斜めに移動できます。\n" +
                                  "風来のシレン風の8方向移動です！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.MoveDiagonal,
                    highlightUI = "DiagonalKeys",
                    showPointer = true
                },

                // Step 4: ターン制バトル説明
                new TutorialStep
                {
                    stepId = "turn_based",
                    title = "ターン制バトル",
                    description = "このゲームはターン制です。\n" +
                                  "あなたが行動すると、敵も行動します。\n" +
                                  "慎重に考えて動きましょう！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                },

                // Step 5: 敵との戦闘
                new TutorialStep
                {
                    stepId = "combat_basic",
                    title = "戦闘方法",
                    description = "敵に向かって移動すると攻撃できます。\n" +
                                  "目の前の敵を倒してみましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.Attack,
                    highlightUI = "Enemy",
                    showPointer = true,
                    pointerTarget = "Enemy"
                },

                // Step 6: HP・ステータス確認
                new TutorialStep
                {
                    stepId = "status_check",
                    title = "ステータス確認",
                    description = "画面左上にHP、レベル、経験値が表示されています。\n" +
                                  "常に自分の状態を確認しましょう！",
                    stepType = TutorialStepType.Message,
                    highlightUI = "HUD",
                    showPointer = true,
                    pointerTarget = "HUD",
                    waitForInput = true
                },

                // Step 7: アイテム拾得
                new TutorialStep
                {
                    stepId = "item_pickup",
                    title = "アイテムを拾う",
                    description = "床に落ちているアイテムの上を通ると自動的に拾います。\n" +
                                  "アイテムを拾ってみましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.PickupItem,
                    highlightUI = "Item",
                    showPointer = true,
                    pointerTarget = "Item"
                },

                // Step 8: インベントリ
                new TutorialStep
                {
                    stepId = "inventory_open",
                    title = "インベントリ",
                    description = "Iキーを押すとインベントリが開きます。\n" +
                                  "アイテムの確認・使用・装備ができます。",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.OpenInventory,
                    highlightUI = "InventoryButton",
                    showPointer = true
                },

                // Step 9: アイテム使用
                new TutorialStep
                {
                    stepId = "item_use",
                    title = "アイテム使用",
                    description = "インベントリでアイテムをクリックして「使う」を選択できます。\n" +
                                  "ポーションを使ってHPを回復してみましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.UseItem,
                    highlightUI = "InventorySlot"
                },

                // Step 10: 装備システム
                new TutorialStep
                {
                    stepId = "equipment",
                    title = "装備システム",
                    description = "武器や防具を装備すると能力が上がります。\n" +
                                  "装備を変更してみましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.EquipItem,
                    highlightUI = "EquipmentSlot"
                },

                // Step 11: 階段
                new TutorialStep
                {
                    stepId = "stairs",
                    title = "階段を見つけよう",
                    description = "ダンジョンには下り階段があります。\n" +
                                  "階段を見つけて次のフロアへ進みましょう！",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.FindStairs,
                    highlightUI = "Stairs",
                    showPointer = true,
                    pointerTarget = "Stairs"
                },

                // Step 12: 満腹度システム
                new TutorialStep
                {
                    stepId = "hunger",
                    title = "満腹度について",
                    description = "行動するたびに満腹度が減ります。\n" +
                                  "0になるとHPが減り始めるので、食料を持ち歩きましょう！",
                    stepType = TutorialStepType.Message,
                    highlightUI = "HungerBar",
                    showPointer = true,
                    waitForInput = true
                },

                // Step 13: レベルアップ
                new TutorialStep
                {
                    stepId = "levelup",
                    title = "レベルアップ",
                    description = "敵を倒すと経験値を獲得し、レベルアップします。\n" +
                                  "レベルが上がるとHP・攻撃力・防御力が上昇！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                },

                // Step 14: ガチャシステム
                new TutorialStep
                {
                    stepId = "gacha",
                    title = "ガチャシステム",
                    description = "ゴールドを使ってガチャを引けます。\n" +
                                  "レアな装備をゲットしてキャラクターを強化しましょう！\n" +
                                  "Gキーでガチャ画面を開けます。",
                    stepType = TutorialStepType.Action,
                    requiredAction = TutorialAction.OpenGacha,
                    highlightUI = "GachaButton",
                    showPointer = true
                },

                // Step 15: 現実連動システム
                new TutorialStep
                {
                    stepId = "real_world_tasks",
                    title = "現実世界との連動",
                    description = "このゲームは現実世界のタスクと連動しています。\n" +
                                  "タスクを達成すると、ゲーム内で経験値とゴールドがもらえます！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                },

                // Step 16: AIストーリー
                new TutorialStep
                {
                    stepId = "ai_story",
                    title = "AIストーリー",
                    description = "あなたの行動に応じて、AIが物語を生成します。\n" +
                                  "毎日新しいストーリーが待っています！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                },

                // Step 17: 完了
                new TutorialStep
                {
                    stepId = "complete",
                    title = "チュートリアル完了！",
                    description = "基本操作を全て学びました。おめでとうございます！\n" +
                                  "これから本格的な冒険が始まります。\n" +
                                  "あなたの心の冒険を楽しんでください！",
                    stepType = TutorialStepType.Message,
                    waitForInput = true
                }
            };
        }

        /// <summary>
        /// チュートリアルを開始
        /// </summary>
        public void StartTutorial()
        {
            if (isTutorialCompleted || !tutorialEnabled)
            {
                Debug.Log("[TutorialManager] Tutorial already completed or disabled.");
                return;
            }

            isTutorialActive = true;
            currentStepIndex = 0;
            
            Debug.Log("[TutorialManager] Tutorial started.");
            
            ShowCurrentStep();
        }

        /// <summary>
        /// 現在のステップを表示
        /// </summary>
        private void ShowCurrentStep()
        {
            if (currentStepIndex >= tutorialSteps.Count)
            {
                CompleteTutorial();
                return;
            }

            currentStep = tutorialSteps[currentStepIndex];
            
            Debug.Log($"[TutorialManager] Step {currentStepIndex + 1}/{tutorialSteps.Count}: {currentStep.title}");

            // UI表示
            if (tutorialUI != null)
            {
                tutorialUI.ShowStep(currentStep);
            }

            // ハイライト表示
            if (highlightSystem != null && !string.IsNullOrEmpty(currentStep.highlightUI))
            {
                highlightSystem.HighlightUI(currentStep.highlightUI);
            }

            // ポインター表示
            if (pointerSystem != null && currentStep.showPointer)
            {
                pointerSystem.ShowPointer(currentStep.pointerTarget);
            }

            OnStepStarted?.Invoke(currentStep);
        }

        /// <summary>
        /// 次のステップへ進む
        /// </summary>
        public void NextStep()
        {
            if (!isTutorialActive) return;

            // ハイライト・ポインターを非表示
            if (highlightSystem != null)
            {
                highlightSystem.ClearHighlight();
            }

            if (pointerSystem != null)
            {
                pointerSystem.HidePointer();
            }

            OnStepCompleted?.Invoke(currentStep);

            currentStepIndex++;
            ShowCurrentStep();
        }

        /// <summary>
        /// アクションが実行されたことを通知
        /// </summary>
        public void OnActionPerformed(TutorialAction action)
        {
            if (!isTutorialActive || currentStep == null) return;

            if (currentStep.stepType == TutorialStepType.Action && 
                currentStep.requiredAction == action)
            {
                Debug.Log($"[TutorialManager] Required action performed: {action}");
                StartCoroutine(DelayedNextStep(1.5f)); // 少し待ってから次へ
            }
        }

        /// <summary>
        /// 遅延して次のステップへ
        /// </summary>
        private IEnumerator DelayedNextStep(float delay)
        {
            yield return new WaitForSeconds(delay);
            NextStep();
        }

        /// <summary>
        /// チュートリアルをスキップ
        /// </summary>
        public void SkipTutorial()
        {
            if (!allowSkip) return;

            Debug.Log("[TutorialManager] Tutorial skipped.");
            
            isTutorialActive = false;
            isTutorialCompleted = true;
            
            // UI非表示
            if (tutorialUI != null)
            {
                tutorialUI.Hide();
            }

            if (highlightSystem != null)
            {
                highlightSystem.ClearHighlight();
            }

            if (pointerSystem != null)
            {
                pointerSystem.HidePointer();
            }

            SaveTutorialProgress();
            OnTutorialSkipped?.Invoke();
        }

        /// <summary>
        /// チュートリアル完了
        /// </summary>
        private void CompleteTutorial()
        {
            Debug.Log("[TutorialManager] Tutorial completed!");
            
            isTutorialActive = false;
            isTutorialCompleted = true;

            // UI非表示
            if (tutorialUI != null)
            {
                tutorialUI.Hide();
            }

            SaveTutorialProgress();
            OnTutorialCompleted?.Invoke();

            // 報酬を付与（オプション）
            GiveCompletionReward();
        }

        /// <summary>
        /// チュートリアル完了報酬
        /// </summary>
        private void GiveCompletionReward()
        {
            if (player != null)
            {
                player.GainExperience(100);
                player.stats.Gold += 500;
                
                Debug.Log("[TutorialManager] Completion reward granted: 100 XP, 500 Gold");
            }
        }

        /// <summary>
        /// チュートリアル進行状況を保存
        /// </summary>
        private void SaveTutorialProgress()
        {
            PlayerPrefs.SetInt("TutorialCompleted", isTutorialCompleted ? 1 : 0);
            PlayerPrefs.SetInt("CurrentTutorialStep", currentStepIndex);
            PlayerPrefs.Save();
        }

        /// <summary>
        /// チュートリアル進行状況をロード
        /// </summary>
        private void LoadTutorialProgress()
        {
            isTutorialCompleted = PlayerPrefs.GetInt("TutorialCompleted", 0) == 1;
            currentStepIndex = PlayerPrefs.GetInt("CurrentTutorialStep", 0);
        }

        /// <summary>
        /// チュートリアルをリセット（デバッグ用）
        /// </summary>
        public void ResetTutorial()
        {
            isTutorialCompleted = false;
            currentStepIndex = 0;
            isTutorialActive = false;
            SaveTutorialProgress();
            
            Debug.Log("[TutorialManager] Tutorial reset.");
        }

        // ゲッター
        public bool IsTutorialActive => isTutorialActive;
        public bool IsTutorialCompleted => isTutorialCompleted;
        public int CurrentStepIndex => currentStepIndex;
        public int TotalSteps => tutorialSteps.Count;
    }

    #region Data Classes

    /// <summary>
    /// チュートリアルステップ
    /// </summary>
    [System.Serializable]
    public class TutorialStep
    {
        public string stepId;
        public string title;
        [TextArea(3, 10)]
        public string description;
        public TutorialStepType stepType;
        public TutorialAction requiredAction;
        public string highlightUI;
        public bool showPointer;
        public string pointerTarget;
        public bool waitForInput = false;
        public float autoProgressDelay = 0f;
    }

    /// <summary>
    /// チュートリアルステップの種類
    /// </summary>
    public enum TutorialStepType
    {
        Message,    // メッセージ表示のみ
        Action,     // プレイヤーのアクションを待つ
        Automatic   // 自動進行
    }

    /// <summary>
    /// チュートリアルで必要なアクション
    /// </summary>
    public enum TutorialAction
    {
        None,
        Move,
        MoveDiagonal,
        Attack,
        PickupItem,
        OpenInventory,
        UseItem,
        EquipItem,
        FindStairs,
        OpenGacha,
        DefeatEnemy
    }

    #endregion
}
