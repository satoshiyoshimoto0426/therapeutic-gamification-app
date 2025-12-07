using UnityEngine;
using KokoroNoBoukensha.Core;
using KokoroNoBoukensha.Dungeon;

namespace KokoroNoBoukensha.Character
{
    /// <summary>
    /// 敵キャラクターの基底クラス
    /// </summary>
    public class Enemy : MonoBehaviour, ITurnBasedEntity
    {
        [Header("Enemy Info")]
        public string enemyName = "Enemy";
        public EnemyType enemyType;
        public int level = 1;

        [Header("Stats")]
        public EnemyStats stats;

        [Header("AI")]
        public EnemyAIType aiType = EnemyAIType.Chase;
        public int visionRange = 5;
        public int attackRange = 1;

        [Header("Movement")]
        public float moveSpeed = 3f;
        public bool isMoving = false;

        [Header("Loot")]
        public int expReward = 10;
        public int goldReward = 5;

        private Vector3 targetPosition;
        private Vector2Int gridPosition;
        private Player player;

        private void Start()
        {
            InitializeEnemy();

            // TurnManagerに登録
            if (TurnManager.Instance != null)
            {
                TurnManager.Instance.RegisterEntity(this);
            }
        }

        /// <summary>
        /// 敵を初期化
        /// </summary>
        public void InitializeEnemy()
        {
            stats = new EnemyStats();
            stats.InitializeForLevel(level);

            // グリッド位置を設定
            gridPosition = new Vector2Int((int)transform.position.x, (int)transform.position.z);
            targetPosition = transform.position;

            // プレイヤー参照を取得
            player = FindObjectOfType<Player>();

            Debug.Log($"[Enemy] {enemyName} initialized at {gridPosition}");
        }

        private void Update()
        {
            // スムーズ移動
            if (isMoving)
            {
                MoveTowardsTarget();
            }
        }

        /// <summary>
        /// ターン処理（敵の行動）
        /// </summary>
        public void TakeTurn()
        {
            if (!IsAlive() || player == null) return;

            switch (aiType)
            {
                case EnemyAIType.Passive:
                    // 何もしない
                    break;

                case EnemyAIType.Patrol:
                    PatrolBehavior();
                    break;

                case EnemyAIType.Chase:
                    ChaseBehavior();
                    break;

                case EnemyAIType.Ranged:
                    RangedBehavior();
                    break;

                case EnemyAIType.Support:
                    SupportBehavior();
                    break;

                case EnemyAIType.Boss:
                    BossBehavior();
                    break;
            }
        }

        /// <summary>
        /// 追跡行動
        /// </summary>
        private void ChaseBehavior()
        {
            float distanceToPlayer = Vector2Int.Distance(gridPosition, player.GetGridPosition());

            // 視界内にプレイヤーがいるか
            if (distanceToPlayer <= visionRange)
            {
                // 攻撃範囲内なら攻撃
                if (distanceToPlayer <= attackRange)
                {
                    AttackPlayer();
                }
                else
                {
                    // プレイヤーに近づく
                    MoveTowardsPlayer();
                }
            }
            else
            {
                // ランダム移動
                RandomMove();
            }
        }

        /// <summary>
        /// 巡回行動
        /// </summary>
        private void PatrolBehavior()
        {
            // TODO: 巡回ルートに沿って移動
            RandomMove();
        }

        /// <summary>
        /// 遠距離攻撃行動
        /// </summary>
        private void RangedBehavior()
        {
            float distanceToPlayer = Vector2Int.Distance(gridPosition, player.GetGridPosition());

            if (distanceToPlayer <= visionRange)
            {
                if (distanceToPlayer <= 3 && distanceToPlayer > 1)
                {
                    // 遠距離攻撃
                    RangedAttack();
                }
                else if (distanceToPlayer > 3)
                {
                    // プレイヤーに近づく
                    MoveTowardsPlayer();
                }
                else
                {
                    // 距離を取る
                    MoveAwayFromPlayer();
                }
            }
        }

        /// <summary>
        /// サポート行動
        /// </summary>
        private void SupportBehavior()
        {
            // TODO: 味方を回復・強化
            RandomMove();
        }

        /// <summary>
        /// ボス行動
        /// </summary>
        private void BossBehavior()
        {
            // TODO: 複雑なパターン攻撃
            ChaseBehavior();
        }

        /// <summary>
        /// プレイヤーに向かって移動
        /// </summary>
        private void MoveTowardsPlayer()
        {
            Vector2Int direction = GetDirectionToPlayer();
            TryMove(direction);
        }

        /// <summary>
        /// プレイヤーから離れる
        /// </summary>
        private void MoveAwayFromPlayer()
        {
            Vector2Int direction = -GetDirectionToPlayer();
            TryMove(direction);
        }

        /// <summary>
        /// プレイヤーへの方向を取得
        /// </summary>
        private Vector2Int GetDirectionToPlayer()
        {
            Vector2Int playerPos = player.GetGridPosition();
            Vector2Int diff = playerPos - gridPosition;

            int x = diff.x != 0 ? (int)Mathf.Sign(diff.x) : 0;
            int y = diff.y != 0 ? (int)Mathf.Sign(diff.y) : 0;

            return new Vector2Int(x, y);
        }

        /// <summary>
        /// ランダム移動
        /// </summary>
        private void RandomMove()
        {
            Vector2Int[] directions = {
                Vector2Int.up, Vector2Int.down, Vector2Int.left, Vector2Int.right,
                new Vector2Int(1, 1), new Vector2Int(-1, 1), new Vector2Int(1, -1), new Vector2Int(-1, -1)
            };

            Vector2Int randomDirection = directions[Random.Range(0, directions.Length)];
            TryMove(randomDirection);
        }

        /// <summary>
        /// 移動を試みる
        /// </summary>
        private bool TryMove(Vector2Int direction)
        {
            Vector2Int newGridPos = gridPosition + direction;

            // 移動先のタイルをチェック
            if (GameManager.Instance != null && GameManager.Instance.dungeonGenerator != null)
            {
                Tile tile = GameManager.Instance.dungeonGenerator.GetTile(newGridPos.x, newGridPos.y);

                if (tile != null && tile.IsWalkable())
                {
                    // プレイヤーがいるかチェック
                    if (player.GetGridPosition() == newGridPos)
                    {
                        return false;  // プレイヤーのマスには移動できない
                    }

                    // 他の敵がいるかチェック
                    if (IsEnemyAt(newGridPos))
                    {
                        return false;
                    }

                    // 移動実行
                    gridPosition = newGridPos;
                    targetPosition = new Vector3(newGridPos.x, transform.position.y, newGridPos.y);
                    isMoving = true;

                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// 目標位置へ移動
        /// </summary>
        private void MoveTowardsTarget()
        {
            transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);

            if (Vector3.Distance(transform.position, targetPosition) < 0.01f)
            {
                transform.position = targetPosition;
                isMoving = false;
            }
        }

        /// <summary>
        /// 指定位置に敵がいるかチェック
        /// </summary>
        private bool IsEnemyAt(Vector2Int position)
        {
            Enemy[] enemies = FindObjectsOfType<Enemy>();
            foreach (Enemy enemy in enemies)
            {
                if (enemy != this && enemy.gridPosition == position && enemy.IsAlive())
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// プレイヤーを攻撃
        /// </summary>
        private void AttackPlayer()
        {
            if (player == null) return;

            int damage = CalculateDamage();
            player.TakeDamage(damage, DamageType.Physical);

            Debug.Log($"[Enemy] {enemyName} attacked Player for {damage} damage");
        }

        /// <summary>
        /// 遠距離攻撃
        /// </summary>
        private void RangedAttack()
        {
            if (player == null) return;

            int damage = CalculateDamage() / 2;  // 遠距離は威力が低い
            player.TakeDamage(damage, DamageType.Physical);

            Debug.Log($"[Enemy] {enemyName} ranged attacked Player for {damage} damage");
        }

        /// <summary>
        /// ダメージ計算
        /// </summary>
        private int CalculateDamage()
        {
            int baseDamage = stats.Attack - player.stats.Defense;
            baseDamage = Mathf.Max(1, baseDamage);
            return baseDamage;
        }

        /// <summary>
        /// ダメージを受ける
        /// </summary>
        public void TakeDamage(int damage, DamageType type)
        {
            stats.CurrentHP -= damage;
            stats.CurrentHP = Mathf.Max(0, stats.CurrentHP);

            Debug.Log($"[Enemy] {enemyName} took {damage} damage. HP: {stats.CurrentHP}/{stats.MaxHP}");

            if (stats.CurrentHP <= 0)
            {
                OnDeath();
            }
        }

        /// <summary>
        /// 死亡処理
        /// </summary>
        private void OnDeath()
        {
            Debug.Log($"[Enemy] {enemyName} defeated");

            // 報酬を与える
            if (player != null)
            {
                player.GainExperience(expReward);
                player.stats.Gold += goldReward;
            }

            // TurnManagerから登録解除
            if (TurnManager.Instance != null)
            {
                TurnManager.Instance.UnregisterEntity(this);
            }

            // オブジェクトを削除
            Destroy(gameObject);
        }

        /// <summary>
        /// 生存チェック
        /// </summary>
        public bool IsAlive()
        {
            return stats.CurrentHP > 0;
        }

        /// <summary>
        /// 現在のグリッド位置を取得
        /// </summary>
        public Vector2Int GetGridPosition()
        {
            return gridPosition;
        }

        // ITurnBasedEntity実装
        public void OnTurnStart()
        {
            TakeTurn();
        }

        public void OnTurnEnd() { }

        public bool IsActive()
        {
            return IsAlive();
        }

        public bool IsPlayer()
        {
            return false;
        }

        public string GetEntityName()
        {
            return enemyName;
        }
    }

    /// <summary>
    /// 敵のステータス
    /// </summary>
    [System.Serializable]
    public class EnemyStats
    {
        public int MaxHP;
        public int CurrentHP;
        public int Attack;
        public int Defense;
        public int Speed;

        public void InitializeForLevel(int level)
        {
            MaxHP = 20 + (level * 5);
            CurrentHP = MaxHP;
            Attack = 5 + (level * 2);
            Defense = 2 + level;
            Speed = 5 + level;
        }
    }

    /// <summary>
    /// 敵の種類
    /// </summary>
    public enum EnemyType
    {
        Slime,           // 先延ばしスライム
        Shadow,          // 不安の影
        Ogre,            // 怒りオーガ
        Ghost,           // 孤独ゴースト
        Knight,          // 後悔の騎士
        Demon,           // 自己否定デーモン
        BossDragon,      // ボス：混乱のドラゴン
        BossHydra,       // ボス：絶望のヒドラ
        BossDarkness     // 最終ボス：心の闇
    }

    /// <summary>
    /// 敵AIのタイプ
    /// </summary>
    public enum EnemyAIType
    {
        Passive,   // 受動的（攻撃されるまで動かない）
        Patrol,    // 巡回
        Chase,     // 追跡
        Ranged,    // 遠距離攻撃
        Support,   // サポート（味方を回復）
        Boss       // ボス専用AI
    }
}
