using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Effects
{
    /// <summary>
    /// エフェクト管理システム
    /// パーティクル、サウンド、画面効果を統合管理
    /// </summary>
    public class EffectManager : MonoBehaviour
    {
        public static EffectManager Instance { get; private set; }

        [Header("Prefabs")]
        public GameObject attackEffectPrefab;
        public GameObject damageEffectPrefab;
        public GameObject healEffectPrefab;
        public GameObject levelUpEffectPrefab;
        public GameObject itemGetEffectPrefab;
        public GameObject deathEffectPrefab;

        [Header("Particle Pools")]
        private Dictionary<string, Queue<GameObject>> effectPools = new Dictionary<string, Queue<GameObject>>();
        public int poolSize = 10;

        [Header("Audio")]
        public AudioSource audioSource;
        public AudioClip attackSound;
        public AudioClip damageSound;
        public AudioClip healSound;
        public AudioClip levelUpSound;
        public AudioClip itemGetSound;
        public AudioClip deathSound;

        [Header("Screen Effects")]
        public bool enableScreenShake = true;
        public bool enableFlash = true;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }

            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
            }

            InitializeEffectPools();
        }

        /// <summary>
        /// エフェクトプールを初期化
        /// </summary>
        private void InitializeEffectPools()
        {
            // 各エフェクトタイプのプールを作成
            CreateEffectPool("Attack", attackEffectPrefab);
            CreateEffectPool("Damage", damageEffectPrefab);
            CreateEffectPool("Heal", healEffectPrefab);
            CreateEffectPool("LevelUp", levelUpEffectPrefab);
            CreateEffectPool("ItemGet", itemGetEffectPrefab);
            CreateEffectPool("Death", deathEffectPrefab);
        }

        /// <summary>
        /// エフェクトプールを作成
        /// </summary>
        private void CreateEffectPool(string poolName, GameObject prefab)
        {
            if (prefab == null) return;

            Queue<GameObject> pool = new Queue<GameObject>();

            for (int i = 0; i < poolSize; i++)
            {
                GameObject obj = Instantiate(prefab);
                obj.SetActive(false);
                obj.transform.SetParent(transform);
                pool.Enqueue(obj);
            }

            effectPools[poolName] = pool;
        }

        /// <summary>
        /// 攻撃エフェクト
        /// </summary>
        public void PlayAttackEffect(Vector3 position, Vector3 direction)
        {
            GameObject effect = GetPooledEffect("Attack");
            if (effect != null)
            {
                effect.transform.position = position;
                effect.transform.rotation = Quaternion.LookRotation(direction);
                effect.SetActive(true);

                StartCoroutine(ReturnToPool(effect, "Attack", 1f));
            }

            PlaySound(attackSound);
        }

        /// <summary>
        /// ダメージエフェクト
        /// </summary>
        public void PlayDamageEffect(Vector3 position, int damage)
        {
            GameObject effect = GetPooledEffect("Damage");
            if (effect != null)
            {
                effect.transform.position = position + Vector3.up;
                effect.SetActive(true);

                // ダメージ数値を表示（TextMeshがあれば）
                var textMesh = effect.GetComponentInChildren<TMPro.TextMeshPro>();
                if (textMesh != null)
                {
                    textMesh.text = damage.ToString();
                }

                StartCoroutine(ReturnToPool(effect, "Damage", 1f));
            }

            PlaySound(damageSound);

            // 画面シェイク
            if (enableScreenShake && Core.CameraController.Instance != null)
            {
                Core.CameraController.Instance.Shake(0.15f, 0.1f);
            }
        }

        /// <summary>
        /// 回復エフェクト
        /// </summary>
        public void PlayHealEffect(Vector3 position, int healAmount)
        {
            GameObject effect = GetPooledEffect("Heal");
            if (effect != null)
            {
                effect.transform.position = position + Vector3.up;
                effect.SetActive(true);

                var textMesh = effect.GetComponentInChildren<TMPro.TextMeshPro>();
                if (textMesh != null)
                {
                    textMesh.text = $"+{healAmount}";
                    textMesh.color = Color.green;
                }

                StartCoroutine(ReturnToPool(effect, "Heal", 1f));
            }

            PlaySound(healSound);
        }

        /// <summary>
        /// レベルアップエフェクト
        /// </summary>
        public void PlayLevelUpEffect(Vector3 position)
        {
            GameObject effect = GetPooledEffect("LevelUp");
            if (effect != null)
            {
                effect.transform.position = position;
                effect.SetActive(true);

                StartCoroutine(ReturnToPool(effect, "LevelUp", 2f));
            }

            PlaySound(levelUpSound);
        }

        /// <summary>
        /// アイテム獲得エフェクト
        /// </summary>
        public void PlayItemGetEffect(Vector3 position)
        {
            GameObject effect = GetPooledEffect("ItemGet");
            if (effect != null)
            {
                effect.transform.position = position;
                effect.SetActive(true);

                StartCoroutine(ReturnToPool(effect, "ItemGet", 1f));
            }

            PlaySound(itemGetSound);
        }

        /// <summary>
        /// 死亡エフェクト
        /// </summary>
        public void PlayDeathEffect(Vector3 position)
        {
            GameObject effect = GetPooledEffect("Death");
            if (effect != null)
            {
                effect.transform.position = position;
                effect.SetActive(true);

                StartCoroutine(ReturnToPool(effect, "Death", 2f));
            }

            PlaySound(deathSound);
        }

        /// <summary>
        /// プールからエフェクトを取得
        /// </summary>
        private GameObject GetPooledEffect(string poolName)
        {
            if (!effectPools.ContainsKey(poolName)) return null;

            Queue<GameObject> pool = effectPools[poolName];
            
            if (pool.Count > 0)
            {
                return pool.Dequeue();
            }

            return null;
        }

        /// <summary>
        /// エフェクトをプールに戻す
        /// </summary>
        private IEnumerator ReturnToPool(GameObject effect, string poolName, float delay)
        {
            yield return new WaitForSeconds(delay);

            if (effect != null)
            {
                effect.SetActive(false);
                effect.transform.SetParent(transform);

                if (effectPools.ContainsKey(poolName))
                {
                    effectPools[poolName].Enqueue(effect);
                }
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

        /// <summary>
        /// 画面フラッシュ
        /// </summary>
        public void FlashScreen(Color color, float duration = 0.1f)
        {
            if (!enableFlash) return;

            StartCoroutine(FlashCoroutine(color, duration));
        }

        private IEnumerator FlashCoroutine(Color color, float duration)
        {
            // TODO: UIパネルを使った画面フラッシュ実装
            yield return new WaitForSeconds(duration);
        }

        /// <summary>
        /// カスタムエフェクトを再生
        /// </summary>
        public void PlayCustomEffect(GameObject prefab, Vector3 position, float duration = 1f)
        {
            if (prefab == null) return;

            GameObject effect = Instantiate(prefab, position, Quaternion.identity);
            Destroy(effect, duration);
        }

        /// <summary>
        /// パーティクルシステムを再生
        /// </summary>
        public void PlayParticle(ParticleSystem particleSystem, Vector3 position)
        {
            if (particleSystem == null) return;

            particleSystem.transform.position = position;
            particleSystem.Play();
        }
    }
}
