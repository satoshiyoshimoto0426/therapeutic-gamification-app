using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Core
{
    /// <summary>
    /// ターン制システムを管理するクラス
    /// 風来のシレン風のターンベースゲームプレイを実現
    /// </summary>
    public class TurnManager : MonoBehaviour
    {
        public static TurnManager Instance { get; private set; }

        [Header("Turn Settings")]
        public int currentTurn = 0;
        public float actionDelay = 0.2f;

        [Header("Turn Queue")]
        private Queue<ITurnBasedEntity> turnQueue = new Queue<ITurnBasedEntity>();
        private List<ITurnBasedEntity> allEntities = new List<ITurnBasedEntity>();

        private bool isProcessingTurn = false;

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

        /// <summary>
        /// エンティティを登録
        /// </summary>
        public void RegisterEntity(ITurnBasedEntity entity)
        {
            if (!allEntities.Contains(entity))
            {
                allEntities.Add(entity);
                Debug.Log($"[TurnManager] Entity registered: {entity.GetEntityName()}");
            }
        }

        /// <summary>
        /// エンティティの登録解除
        /// </summary>
        public void UnregisterEntity(ITurnBasedEntity entity)
        {
            if (allEntities.Contains(entity))
            {
                allEntities.Remove(entity);
                Debug.Log($"[TurnManager] Entity unregistered: {entity.GetEntityName()}");
            }
        }

        /// <summary>
        /// プレイヤーのアクション実行後、ターン進行
        /// </summary>
        public void PlayerActionCompleted()
        {
            if (!isProcessingTurn && GameManager.Instance.IsPlaying())
            {
                StartCoroutine(ProcessTurnCycle());
            }
        }

        /// <summary>
        /// ターンサイクル処理
        /// </summary>
        private IEnumerator ProcessTurnCycle()
        {
            isProcessingTurn = true;
            currentTurn++;

            Debug.Log($"[TurnManager] Turn {currentTurn} started");

            // 1. 敵の行動フェーズ
            yield return StartCoroutine(ProcessEnemyPhase());

            // 2. ターン経過効果の処理
            ProcessTurnEffects();

            // 3. 状態更新
            UpdateAllEntities();

            yield return new WaitForSeconds(actionDelay);

            isProcessingTurn = false;

            Debug.Log($"[TurnManager] Turn {currentTurn} completed");
        }

        /// <summary>
        /// 敵の行動フェーズ
        /// </summary>
        private IEnumerator ProcessEnemyPhase()
        {
            // アクティブな敵を取得
            List<ITurnBasedEntity> activeEnemies = GetActiveEnemies();

            foreach (ITurnBasedEntity entity in activeEnemies)
            {
                if (entity.IsActive())
                {
                    entity.OnTurnStart();
                    yield return new WaitForSeconds(actionDelay * 0.5f);
                }
            }
        }

        /// <summary>
        /// アクティブな敵を取得
        /// </summary>
        private List<ITurnBasedEntity> GetActiveEnemies()
        {
            List<ITurnBasedEntity> enemies = new List<ITurnBasedEntity>();

            foreach (ITurnBasedEntity entity in allEntities)
            {
                if (entity != null && entity.IsActive() && !entity.IsPlayer())
                {
                    enemies.Add(entity);
                }
            }

            return enemies;
        }

        /// <summary>
        /// ターン経過効果の処理
        /// </summary>
        private void ProcessTurnEffects()
        {
            // プレイヤーの満腹度減少
            Player player = GameManager.Instance.player;
            if (player != null)
            {
                // 100ターンごとに満腹度-1
                if (currentTurn % 100 == 0)
                {
                    player.DecreaseHunger(1);
                }

                // 満腹度が50%以上ならHP自然回復
                if (player.stats.Hunger >= 50)
                {
                    player.Heal(1);
                }

                // 満腹度が0なら毎ターンダメージ
                if (player.stats.Hunger <= 0)
                {
                    player.TakeDamage(5, DamageType.Hunger);
                }
            }
        }

        /// <summary>
        /// すべてのエンティティを更新
        /// </summary>
        private void UpdateAllEntities()
        {
            foreach (ITurnBasedEntity entity in allEntities)
            {
                if (entity != null && entity.IsActive())
                {
                    entity.OnTurnEnd();
                }
            }

            // 死亡したエンティティを削除
            allEntities.RemoveAll(e => e == null || !e.IsActive());
        }

        /// <summary>
        /// ターン処理中かチェック
        /// </summary>
        public bool IsProcessingTurn()
        {
            return isProcessingTurn;
        }

        /// <summary>
        /// プレイヤーが行動可能かチェック
        /// </summary>
        public bool CanPlayerAct()
        {
            return !isProcessingTurn && GameManager.Instance.IsPlayerTurn();
        }

        /// <summary>
        /// 現在のターン数を取得
        /// </summary>
        public int GetCurrentTurn()
        {
            return currentTurn;
        }

        /// <summary>
        /// ターンをリセット
        /// </summary>
        public void ResetTurn()
        {
            currentTurn = 0;
            turnQueue.Clear();
            allEntities.Clear();
            isProcessingTurn = false;
            Debug.Log("[TurnManager] Turn reset");
        }
    }

    /// <summary>
    /// ターンベースエンティティのインターフェース
    /// </summary>
    public interface ITurnBasedEntity
    {
        /// <summary>
        /// ターン開始時の処理
        /// </summary>
        void OnTurnStart();

        /// <summary>
        /// ターン終了時の処理
        /// </summary>
        void OnTurnEnd();

        /// <summary>
        /// エンティティがアクティブか
        /// </summary>
        bool IsActive();

        /// <summary>
        /// プレイヤーかどうか
        /// </summary>
        bool IsPlayer();

        /// <summary>
        /// エンティティ名を取得
        /// </summary>
        string GetEntityName();
    }
}
