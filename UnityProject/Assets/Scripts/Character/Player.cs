using UnityEngine;
using KokoroNoBoukensha.Core;
using KokoroNoBoukensha.Dungeon;

namespace KokoroNoBoukensha.Character
{
    /// <summary>
    /// プレイヤーキャラクターを管理するクラス
    /// </summary>
    public class Player : MonoBehaviour, ITurnBasedEntity
    {
        [Header("Stats")]
        public PlayerStats stats;

        [Header("Movement")]
        public float moveSpeed = 5f;
        public bool isMoving = false;

        [Header("Combat")]
        public int attackRange = 1;

        private Vector3 targetPosition;
        private Vector2Int gridPosition;

        private void Start()
        {
            InitializePlayer();
            
            // TurnManagerに登録
            if (TurnManager.Instance != null)
            {
                TurnManager.Instance.RegisterEntity(this);
            }
        }

        /// <summary>
        /// プレイヤーを初期化
        /// </summary>
        public void InitializePlayer()
        {
            stats = new PlayerStats();
            stats.InitializeDefault();

            // 開始位置に配置
            if (GameManager.Instance != null && GameManager.Instance.dungeonGenerator != null)
            {
                Vector3 startPos = GameManager.Instance.dungeonGenerator.GetPlayerStartPosition();
                transform.position = startPos;
                targetPosition = startPos;
                gridPosition = new Vector2Int((int)startPos.x, (int)startPos.z);
            }

            Debug.Log($"[Player] Initialized at {transform.position}");
        }

        private void Update()
        {
            if (GameManager.Instance == null || !GameManager.Instance.IsPlayerTurn()) return;

            // 移動中でなければ入力を受け付ける
            if (!isMoving)
            {
                HandleInput();
            }

            // スムーズ移動
            if (isMoving)
            {
                MoveTowardsTarget();
            }
        }

        /// <summary>
        /// 入力処理
        /// </summary>
        private void HandleInput()
        {
            Vector2Int direction = Vector2Int.zero;

            // 8方向移動
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow))
                direction = Vector2Int.up;
            else if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow))
                direction = Vector2Int.down;
            else if (Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.LeftArrow))
                direction = Vector2Int.left;
            else if (Input.GetKeyDown(KeyCode.D) || Input.GetKeyDown(KeyCode.RightArrow))
                direction = Vector2Int.right;
            
            // 斜め移動
            else if (Input.GetKeyDown(KeyCode.Q))
                direction = new Vector2Int(-1, 1);  // 左上
            else if (Input.GetKeyDown(KeyCode.E))
                direction = new Vector2Int(1, 1);   // 右上
            else if (Input.GetKeyDown(KeyCode.Z))
                direction = new Vector2Int(-1, -1); // 左下
            else if (Input.GetKeyDown(KeyCode.C))
                direction = new Vector2Int(1, -1);  // 右下

            // 足踏み（ターン経過のみ）
            else if (Input.GetKeyDown(KeyCode.Space))
            {
                Wait();
                return;
            }

            // 移動実行
            if (direction != Vector2Int.zero)
            {
                TryMove(direction);
            }
        }

        /// <summary>
        /// 移動を試みる
        /// </summary>
        public bool TryMove(Vector2Int direction)
        {
            Vector2Int newGridPos = gridPosition + direction;

            // 移動先のタイルをチェック
            if (GameManager.Instance != null && GameManager.Instance.dungeonGenerator != null)
            {
                Tile tile = GameManager.Instance.dungeonGenerator.GetTile(newGridPos.x, newGridPos.y);

                if (tile != null && tile.IsWalkable())
                {
                    // 敵がいるかチェック
                    Enemy enemy = GetEnemyAt(newGridPos);
                    if (enemy != null)
                    {
                        // 攻撃
                        AttackEnemy(enemy);
                        return true;
                    }

                    // 移動実行
                    gridPosition = newGridPos;
                    targetPosition = new Vector3(newGridPos.x, transform.position.y, newGridPos.y);
                    isMoving = true;

                    // 階段チェック
                    if (tile.type == TileType.StairsDown)
                    {
                        OnReachStairs();
                    }

                    // ターン進行
                    if (TurnManager.Instance != null)
                    {
                        TurnManager.Instance.PlayerActionCompleted();
                    }

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
        /// 足踏み
        /// </summary>
        public void Wait()
        {
            Debug.Log("[Player] Wait");

            // ターン進行
            if (TurnManager.Instance != null)
            {
                TurnManager.Instance.PlayerActionCompleted();
            }
        }

        /// <summary>
        /// 敵を攻撃
        /// </summary>
        public void AttackEnemy(Enemy enemy)
        {
            if (enemy == null) return;

            int damage = CalculateDamage(enemy);
            enemy.TakeDamage(damage, DamageType.Physical);

            Debug.Log($"[Player] Attacked {enemy.enemyName} for {damage} damage");

            // ターン進行
            if (TurnManager.Instance != null)
            {
                TurnManager.Instance.PlayerActionCompleted();
            }
        }

        /// <summary>
        /// ダメージ計算
        /// </summary>
        private int CalculateDamage(Enemy enemy)
        {
            int baseDamage = stats.Attack - enemy.stats.Defense;
            baseDamage = Mathf.Max(1, baseDamage);

            // クリティカル判定（10%）
            if (Random.value < 0.1f)
            {
                baseDamage = (int)(baseDamage * 1.5f);
                Debug.Log("[Player] Critical Hit!");
            }

            return baseDamage;
        }

        /// <summary>
        /// 指定位置の敵を取得
        /// </summary>
        private Enemy GetEnemyAt(Vector2Int position)
        {
            Enemy[] enemies = FindObjectsOfType<Enemy>();
            foreach (Enemy enemy in enemies)
            {
                if (enemy.GetGridPosition() == position && enemy.IsAlive())
                {
                    return enemy;
                }
            }
            return null;
        }

        /// <summary>
        /// ダメージを受ける
        /// </summary>
        public void TakeDamage(int damage, DamageType type)
        {
            stats.CurrentHP -= damage;
            stats.CurrentHP = Mathf.Max(0, stats.CurrentHP);

            Debug.Log($"[Player] Took {damage} damage. HP: {stats.CurrentHP}/{stats.MaxHP}");

            if (stats.CurrentHP <= 0)
            {
                OnDeath();
            }
        }

        /// <summary>
        /// HP回復
        /// </summary>
        public void Heal(int amount)
        {
            stats.CurrentHP += amount;
            stats.CurrentHP = Mathf.Min(stats.CurrentHP, stats.MaxHP);
        }

        /// <summary>
        /// 満腹度減少
        /// </summary>
        public void DecreaseHunger(int amount)
        {
            stats.Hunger -= amount;
            stats.Hunger = Mathf.Max(0, stats.Hunger);

            if (stats.Hunger <= 0)
            {
                Debug.LogWarning("[Player] Starving!");
            }
        }

        /// <summary>
        /// 経験値獲得
        /// </summary>
        public void GainExperience(int exp)
        {
            stats.Experience += exp;

            // レベルアップチェック
            int requiredExp = GetRequiredExperience(stats.Level);
            if (stats.Experience >= requiredExp)
            {
                LevelUp();
            }
        }

        /// <summary>
        /// レベルアップ
        /// </summary>
        private void LevelUp()
        {
            stats.Level++;
            stats.Experience = 0;

            // ステータス上昇
            stats.MaxHP += Random.Range(3, 8);
            stats.Attack += Random.Range(1, 3);
            stats.Defense += Random.Range(1, 3);
            stats.Speed += Random.Range(0, 2);
            stats.CurrentHP = stats.MaxHP;

            Debug.Log($"[Player] Level Up! Now Level {stats.Level}");
        }

        /// <summary>
        /// 必要経験値を計算
        /// </summary>
        private int GetRequiredExperience(int level)
        {
            return (int)(100 * Mathf.Pow(1.2f, level - 1));
        }

        /// <summary>
        /// 階段に到達
        /// </summary>
        private void OnReachStairs()
        {
            Debug.Log("[Player] Reached stairs");
            
            if (GameManager.Instance != null)
            {
                GameManager.Instance.DescendToNextFloor();
            }
        }

        /// <summary>
        /// 階層変更時の処理
        /// </summary>
        public void OnFloorChanged()
        {
            // 新しい階層の開始位置へ移動
            if (GameManager.Instance != null && GameManager.Instance.dungeonGenerator != null)
            {
                Vector3 startPos = GameManager.Instance.dungeonGenerator.GetPlayerStartPosition();
                transform.position = startPos;
                targetPosition = startPos;
                gridPosition = new Vector2Int((int)startPos.x, (int)startPos.z);
            }
        }

        /// <summary>
        /// 死亡処理
        /// </summary>
        private void OnDeath()
        {
            Debug.Log("[Player] Death");

            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameOver();
            }
        }

        /// <summary>
        /// 現在のグリッド位置を取得
        /// </summary>
        public Vector2Int GetGridPosition()
        {
            return gridPosition;
        }

        // ITurnBasedEntity実装
        public void OnTurnStart() { }
        public void OnTurnEnd() { }
        public bool IsActive() => stats.CurrentHP > 0;
        public bool IsPlayer() => true;
        public string GetEntityName() => "Player";
    }

    /// <summary>
    /// プレイヤーのステータス
    /// </summary>
    [System.Serializable]
    public class PlayerStats
    {
        public int Level = 1;
        public int Experience = 0;
        public int MaxHP = 100;
        public int CurrentHP = 100;
        public int Attack = 10;
        public int Defense = 5;
        public int Speed = 10;
        public int Hunger = 100;
        public int Gold = 0;

        // 心の冒険者独自パラメータ
        public int Concentration = 50;   // 集中力
        public int ActionPoints = 3;     // 行動力
        public int Willpower = 50;       // 意志力
        public int Intelligence = 50;    // 知力

        public void InitializeDefault()
        {
            Level = 1;
            Experience = 0;
            MaxHP = 100;
            CurrentHP = MaxHP;
            Attack = 10;
            Defense = 5;
            Speed = 10;
            Hunger = 100;
            Gold = 0;
        }
    }

    /// <summary>
    /// ダメージタイプ
    /// </summary>
    public enum DamageType
    {
        Physical,   // 物理ダメージ
        Magical,    // 魔法ダメージ
        Hunger,     // 飢餓ダメージ
        Trap,       // トラップダメージ
        Poison      // 毒ダメージ
    }
}
