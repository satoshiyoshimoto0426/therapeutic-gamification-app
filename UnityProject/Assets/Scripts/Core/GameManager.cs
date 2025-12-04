using UnityEngine;
using System.Collections;

namespace KokoroNoBoukensha.Core
{
    /// <summary>
    /// ゲーム全体を管理するシングルトンクラス
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Game State")]
        public GameState currentState;
        public int currentFloor = 1;
        public bool isPlayerTurn = true;

        [Header("Player Reference")]
        public Player player;

        [Header("Dungeon Reference")]
        public DungeonGenerator dungeonGenerator;

        [Header("Settings")]
        public int maxFloor = 30;
        public float turnDelay = 0.3f;

        private void Awake()
        {
            // シングルトンパターン
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
                return;
            }

            InitializeGame();
        }

        private void Start()
        {
            StartNewGame();
        }

        /// <summary>
        /// ゲーム初期化
        /// </summary>
        private void InitializeGame()
        {
            currentState = GameState.MainMenu;
            Debug.Log("[GameManager] Game Initialized");
        }

        /// <summary>
        /// 新しいゲームを開始
        /// </summary>
        public void StartNewGame()
        {
            currentFloor = 1;
            currentState = GameState.Playing;
            
            // ダンジョン生成
            GenerateNewFloor();
            
            // プレイヤー初期化
            if (player != null)
            {
                player.InitializePlayer();
            }

            Debug.Log("[GameManager] New Game Started");
        }

        /// <summary>
        /// 新しい階層を生成
        /// </summary>
        public void GenerateNewFloor()
        {
            if (dungeonGenerator != null)
            {
                int seed = Random.Range(0, 100000);
                dungeonGenerator.Generate(currentFloor, seed);
                Debug.Log($"[GameManager] Floor {currentFloor} generated with seed {seed}");
            }
            else
            {
                Debug.LogError("[GameManager] DungeonGenerator not found!");
            }
        }

        /// <summary>
        /// 次の階層へ進む
        /// </summary>
        public void DescendToNextFloor()
        {
            if (currentFloor >= maxFloor)
            {
                OnGameClear();
                return;
            }

            currentFloor++;
            GenerateNewFloor();
            
            // プレイヤーを階段位置に配置
            if (player != null)
            {
                player.OnFloorChanged();
            }

            Debug.Log($"[GameManager] Descended to Floor {currentFloor}");
        }

        /// <summary>
        /// ゲームクリア
        /// </summary>
        private void OnGameClear()
        {
            currentState = GameState.GameClear;
            Debug.Log("[GameManager] Game Clear!");
            
            // TODO: クリア演出とスコア計算
            // TODO: バックエンドAPIに結果送信
        }

        /// <summary>
        /// ゲームオーバー
        /// </summary>
        public void OnGameOver()
        {
            currentState = GameState.GameOver;
            Debug.Log("[GameManager] Game Over");
            
            // TODO: ゲームオーバー画面表示
            // TODO: スコア保存
        }

        /// <summary>
        /// ターン進行
        /// </summary>
        public IEnumerator ProcessTurn()
        {
            if (!isPlayerTurn) yield break;

            isPlayerTurn = false;

            // 敵のターン処理
            yield return StartCoroutine(ProcessEnemyTurns());

            // ターン経過処理
            ProcessTurnEffects();

            yield return new WaitForSeconds(turnDelay);

            isPlayerTurn = true;
        }

        /// <summary>
        /// 敵の行動処理
        /// </summary>
        private IEnumerator ProcessEnemyTurns()
        {
            // TODO: すべての敵を取得して行動させる
            Enemy[] enemies = FindObjectsOfType<Enemy>();
            
            foreach (Enemy enemy in enemies)
            {
                if (enemy != null && enemy.IsAlive())
                {
                    enemy.TakeTurn();
                    yield return new WaitForSeconds(0.1f);
                }
            }
        }

        /// <summary>
        /// ターン経過による効果処理
        /// </summary>
        private void ProcessTurnEffects()
        {
            if (player != null)
            {
                // 満腹度減少
                player.DecreaseHunger(1);
                
                // HP自然回復
                if (player.stats.Hunger > 50)
                {
                    player.Heal(1);
                }
            }
        }

        /// <summary>
        /// ゲームを一時停止
        /// </summary>
        public void PauseGame()
        {
            currentState = GameState.Paused;
            Time.timeScale = 0f;
            Debug.Log("[GameManager] Game Paused");
        }

        /// <summary>
        /// ゲームを再開
        /// </summary>
        public void ResumeGame()
        {
            currentState = GameState.Playing;
            Time.timeScale = 1f;
            Debug.Log("[GameManager] Game Resumed");
        }

        /// <summary>
        /// ゲーム状態を取得
        /// </summary>
        public bool IsPlaying()
        {
            return currentState == GameState.Playing;
        }

        /// <summary>
        /// プレイヤーのターンかチェック
        /// </summary>
        public bool IsPlayerTurn()
        {
            return isPlayerTurn && IsPlaying();
        }
    }

    /// <summary>
    /// ゲームの状態
    /// </summary>
    public enum GameState
    {
        MainMenu,      // メインメニュー
        Playing,       // プレイ中
        Paused,        // 一時停止
        Inventory,     // インベントリ画面
        Battle,        // 戦闘中
        Story,         // ストーリー表示
        GameOver,      // ゲームオーバー
        GameClear      // ゲームクリア
    }
}
