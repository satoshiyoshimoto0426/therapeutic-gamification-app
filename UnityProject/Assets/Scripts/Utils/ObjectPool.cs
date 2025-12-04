using System.Collections.Generic;
using UnityEngine;

namespace KokoroNoBoukensha.Utils
{
    /// <summary>
    /// オブジェクトプーリングシステム
    /// WebGL最適化のため、頻繁に生成/破棄されるオブジェクトを再利用
    /// </summary>
    public class ObjectPool : MonoBehaviour
    {
        [Header("Pool Settings")]
        [SerializeField] private GameObject prefab;
        [SerializeField] private int initialSize = 10;
        [SerializeField] private int maxSize = 50;
        [SerializeField] private bool autoExpand = true;
        [SerializeField] private Transform poolParent;

        private Queue<GameObject> availableObjects = new Queue<GameObject>();
        private HashSet<GameObject> activeObjects = new HashSet<GameObject>();
        private int currentSize = 0;

        // 静的プール管理
        private static Dictionary<string, ObjectPool> pools = new Dictionary<string, ObjectPool>();

        private void Awake()
        {
            if (poolParent == null)
            {
                poolParent = transform;
            }

            InitializePool();
        }

        /// <summary>
        /// プールの初期化
        /// </summary>
        private void InitializePool()
        {
            for (int i = 0; i < initialSize; i++)
            {
                CreateNewObject();
            }
        }

        /// <summary>
        /// 新しいオブジェクトを作成
        /// </summary>
        private GameObject CreateNewObject()
        {
            if (currentSize >= maxSize && !autoExpand)
            {
                Debug.LogWarning($"[ObjectPool] Max size ({maxSize}) reached for {prefab.name}");
                return null;
            }

            GameObject obj = Instantiate(prefab, poolParent);
            obj.SetActive(false);
            availableObjects.Enqueue(obj);
            currentSize++;
            return obj;
        }

        /// <summary>
        /// プールからオブジェクトを取得
        /// </summary>
        public GameObject Get(Vector3 position, Quaternion rotation)
        {
            GameObject obj;

            if (availableObjects.Count > 0)
            {
                obj = availableObjects.Dequeue();
            }
            else
            {
                obj = CreateNewObject();
                if (obj == null)
                {
                    Debug.LogError($"[ObjectPool] Failed to get object from pool: {prefab.name}");
                    return null;
                }
            }

            obj.transform.position = position;
            obj.transform.rotation = rotation;
            obj.SetActive(true);
            activeObjects.Add(obj);

            return obj;
        }

        /// <summary>
        /// プールからオブジェクトを取得（位置のみ指定）
        /// </summary>
        public GameObject Get(Vector3 position)
        {
            return Get(position, Quaternion.identity);
        }

        /// <summary>
        /// プールからオブジェクトを取得（親指定）
        /// </summary>
        public GameObject Get(Vector3 position, Transform parent)
        {
            GameObject obj = Get(position, Quaternion.identity);
            if (obj != null)
            {
                obj.transform.SetParent(parent);
            }
            return obj;
        }

        /// <summary>
        /// オブジェクトをプールに返却
        /// </summary>
        public void Return(GameObject obj)
        {
            if (obj == null) return;

            if (!activeObjects.Contains(obj))
            {
                Debug.LogWarning($"[ObjectPool] Trying to return object that wasn't from this pool: {obj.name}");
                return;
            }

            obj.SetActive(false);
            obj.transform.SetParent(poolParent);
            activeObjects.Remove(obj);
            availableObjects.Enqueue(obj);
        }

        /// <summary>
        /// 一定時間後にプールに返却
        /// </summary>
        public void ReturnAfterDelay(GameObject obj, float delay)
        {
            if (obj != null)
            {
                StartCoroutine(ReturnAfterDelayCoroutine(obj, delay));
            }
        }

        private System.Collections.IEnumerator ReturnAfterDelayCoroutine(GameObject obj, float delay)
        {
            yield return new WaitForSeconds(delay);
            Return(obj);
        }

        /// <summary>
        /// アクティブなオブジェクトを全て返却
        /// </summary>
        public void ReturnAll()
        {
            var objectsToReturn = new List<GameObject>(activeObjects);
            foreach (var obj in objectsToReturn)
            {
                Return(obj);
            }
        }

        /// <summary>
        /// プールをクリア（全オブジェクトを破棄）
        /// </summary>
        public void Clear()
        {
            ReturnAll();

            while (availableObjects.Count > 0)
            {
                var obj = availableObjects.Dequeue();
                if (obj != null)
                {
                    Destroy(obj);
                }
            }

            currentSize = 0;
        }

        /// <summary>
        /// プールの統計情報を取得
        /// </summary>
        public PoolStats GetStats()
        {
            return new PoolStats
            {
                PrefabName = prefab.name,
                TotalSize = currentSize,
                ActiveCount = activeObjects.Count,
                AvailableCount = availableObjects.Count,
                MaxSize = maxSize
            };
        }

        // 静的メソッド: 名前でプールを取得
        public static ObjectPool GetPool(string poolName)
        {
            pools.TryGetValue(poolName, out ObjectPool pool);
            return pool;
        }

        // 静的メソッド: プールを登録
        public static void RegisterPool(string poolName, ObjectPool pool)
        {
            if (pools.ContainsKey(poolName))
            {
                Debug.LogWarning($"[ObjectPool] Pool '{poolName}' already registered. Overwriting.");
            }
            pools[poolName] = pool;
        }

        // 静的メソッド: プールを削除
        public static void UnregisterPool(string poolName)
        {
            if (pools.ContainsKey(poolName))
            {
                pools[poolName].Clear();
                pools.Remove(poolName);
            }
        }

        // 静的メソッド: 全プールをクリア
        public static void ClearAllPools()
        {
            foreach (var pool in pools.Values)
            {
                pool?.Clear();
            }
            pools.Clear();
        }

        private void OnDestroy()
        {
            Clear();
        }

        #if UNITY_EDITOR
        [ContextMenu("Debug: Print Pool Stats")]
        private void DebugPrintStats()
        {
            var stats = GetStats();
            Debug.Log($"[ObjectPool] {stats.PrefabName} - Total: {stats.TotalSize}, Active: {stats.ActiveCount}, Available: {stats.AvailableCount}, Max: {stats.MaxSize}");
        }
        #endif
    }

    /// <summary>
    /// プールの統計情報
    /// </summary>
    public struct PoolStats
    {
        public string PrefabName;
        public int TotalSize;
        public int ActiveCount;
        public int AvailableCount;
        public int MaxSize;
    }
}
