using System.Collections.Generic;
using UnityEngine;

namespace KokoroNoBoukensha.Utils
{
    /// <summary>
    /// 複数のオブジェクトプールを管理するマネージャー
    /// シングルトンパターンで実装
    /// </summary>
    public class PoolManager : MonoBehaviour
    {
        private static PoolManager instance;
        public static PoolManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<PoolManager>();
                    if (instance == null)
                    {
                        GameObject obj = new GameObject("PoolManager");
                        instance = obj.AddComponent<PoolManager>();
                    }
                }
                return instance;
            }
        }

        [System.Serializable]
        public class PoolConfig
        {
            public string poolName;
            public GameObject prefab;
            public int initialSize = 10;
            public int maxSize = 50;
            public bool autoExpand = true;
        }

        [Header("Pool Configurations")]
        [SerializeField] private List<PoolConfig> poolConfigs = new List<PoolConfig>();

        private Dictionary<string, ObjectPool> pools = new Dictionary<string, ObjectPool>();

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);

            InitializePools();
        }

        /// <summary>
        /// 設定済みのプールを初期化
        /// </summary>
        private void InitializePools()
        {
            foreach (var config in poolConfigs)
            {
                CreatePool(config.poolName, config.prefab, config.initialSize, config.maxSize, config.autoExpand);
            }
        }

        /// <summary>
        /// 新しいプールを作成
        /// </summary>
        public ObjectPool CreatePool(string poolName, GameObject prefab, int initialSize = 10, int maxSize = 50, bool autoExpand = true)
        {
            if (pools.ContainsKey(poolName))
            {
                Debug.LogWarning($"[PoolManager] Pool '{poolName}' already exists.");
                return pools[poolName];
            }

            GameObject poolObj = new GameObject($"Pool_{poolName}");
            poolObj.transform.SetParent(transform);

            ObjectPool pool = poolObj.AddComponent<ObjectPool>();
            
            // リフレクションで内部フィールドを設定（エディタで設定できない場合の代替）
            var poolType = typeof(ObjectPool);
            poolType.GetField("prefab", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(pool, prefab);
            poolType.GetField("initialSize", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(pool, initialSize);
            poolType.GetField("maxSize", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(pool, maxSize);
            poolType.GetField("autoExpand", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(pool, autoExpand);

            pools[poolName] = pool;
            ObjectPool.RegisterPool(poolName, pool);

            Debug.Log($"[PoolManager] Created pool '{poolName}' for prefab '{prefab.name}'");
            return pool;
        }

        /// <summary>
        /// プールからオブジェクトを取得
        /// </summary>
        public GameObject Get(string poolName, Vector3 position, Quaternion rotation)
        {
            if (!pools.ContainsKey(poolName))
            {
                Debug.LogError($"[PoolManager] Pool '{poolName}' not found.");
                return null;
            }

            return pools[poolName].Get(position, rotation);
        }

        public GameObject Get(string poolName, Vector3 position)
        {
            return Get(poolName, position, Quaternion.identity);
        }

        /// <summary>
        /// オブジェクトをプールに返却
        /// </summary>
        public void Return(string poolName, GameObject obj)
        {
            if (!pools.ContainsKey(poolName))
            {
                Debug.LogError($"[PoolManager] Pool '{poolName}' not found.");
                return;
            }

            pools[poolName].Return(obj);
        }

        /// <summary>
        /// 一定時間後にプールに返却
        /// </summary>
        public void ReturnAfterDelay(string poolName, GameObject obj, float delay)
        {
            if (!pools.ContainsKey(poolName))
            {
                Debug.LogError($"[PoolManager] Pool '{poolName}' not found.");
                return;
            }

            pools[poolName].ReturnAfterDelay(obj, delay);
        }

        /// <summary>
        /// 特定のプールをクリア
        /// </summary>
        public void ClearPool(string poolName)
        {
            if (pools.ContainsKey(poolName))
            {
                pools[poolName].Clear();
            }
        }

        /// <summary>
        /// 全プールをクリア
        /// </summary>
        public void ClearAllPools()
        {
            foreach (var pool in pools.Values)
            {
                pool?.Clear();
            }
        }

        /// <summary>
        /// プールの統計情報を取得
        /// </summary>
        public PoolStats GetPoolStats(string poolName)
        {
            if (pools.ContainsKey(poolName))
            {
                return pools[poolName].GetStats();
            }

            return default;
        }

        /// <summary>
        /// 全プールの統計情報を取得
        /// </summary>
        public Dictionary<string, PoolStats> GetAllPoolStats()
        {
            var stats = new Dictionary<string, PoolStats>();
            foreach (var kvp in pools)
            {
                stats[kvp.Key] = kvp.Value.GetStats();
            }
            return stats;
        }

        #if UNITY_EDITOR
        [ContextMenu("Debug: Print All Pool Stats")]
        private void DebugPrintAllStats()
        {
            var allStats = GetAllPoolStats();
            foreach (var kvp in allStats)
            {
                var stats = kvp.Value;
                Debug.Log($"[PoolManager] {kvp.Key} - Prefab: {stats.PrefabName}, Total: {stats.TotalSize}, Active: {stats.ActiveCount}, Available: {stats.AvailableCount}");
            }
        }
        #endif

        private void OnDestroy()
        {
            ClearAllPools();
        }
    }
}
