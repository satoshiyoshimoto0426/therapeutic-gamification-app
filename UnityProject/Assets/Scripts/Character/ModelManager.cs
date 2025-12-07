using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Character
{
    /// <summary>
    /// 3Dモデル管理クラス
    /// プレイヤー・敵・アイテムのモデルをロード・管理
    /// </summary>
    public class ModelManager : MonoBehaviour
    {
        #region Singleton
        private static ModelManager instance;
        public static ModelManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<ModelManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("ModelManager");
                        instance = go.AddComponent<ModelManager>();
                    }
                }
                return instance;
            }
        }
        #endregion

        [Header("Player Models")]
        [Tooltip("プレイヤーのデフォルトモデル")]
        public GameObject defaultPlayerModel;
        
        [Tooltip("プレイヤーモデルのバリエーション（レベルや装備で変化）")]
        public List<PlayerModelData> playerModelVariations = new List<PlayerModelData>();

        [Header("Enemy Models")]
        [Tooltip("敵モデルのデータベース")]
        public List<EnemyModelData> enemyModels = new List<EnemyModelData>();

        [Header("Item Models")]
        [Tooltip("アイテムの3Dモデル")]
        public List<ItemModelData> itemModels = new List<ItemModelData>();

        [Header("Equipment Models")]
        [Tooltip("装備品の3Dモデル（装着時にプレイヤーに表示）")]
        public List<EquipmentModelData> equipmentModels = new List<EquipmentModelData>();

        [Header("Effect Prefabs")]
        [Tooltip("攻撃エフェクト")]
        public List<EffectData> attackEffects = new List<EffectData>();
        
        [Tooltip("魔法エフェクト")]
        public List<EffectData> magicEffects = new List<EffectData>();
        
        [Tooltip("回復エフェクト")]
        public GameObject healEffect;
        
        [Tooltip("レベルアップエフェクト")]
        public GameObject levelUpEffect;

        [Header("Model Settings")]
        [Tooltip("モデルのスケール")]
        public float defaultScale = 1.0f;
        
        [Tooltip("プレイヤーモデルのオフセット")]
        public Vector3 playerModelOffset = Vector3.zero;
        
        [Tooltip("敵モデルのオフセット")]
        public Vector3 enemyModelOffset = Vector3.zero;

        // モデルキャッシュ
        private Dictionary<string, GameObject> modelCache = new Dictionary<string, GameObject>();

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
            }
        }

        #region Player Model Management

        /// <summary>
        /// プレイヤーモデルをロード
        /// </summary>
        public GameObject LoadPlayerModel(int level = 1, string className = "Default")
        {
            // レベルやクラスに応じたモデルを検索
            PlayerModelData modelData = playerModelVariations.Find(m => 
                m.minLevel <= level && m.maxLevel >= level && m.className == className
            );

            GameObject modelPrefab = modelData != null ? modelData.modelPrefab : defaultPlayerModel;

            if (modelPrefab == null)
            {
                Debug.LogError("Player model not found!");
                return null;
            }

            return InstantiateModel(modelPrefab, playerModelOffset);
        }

        /// <summary>
        /// プレイヤーの装備を更新
        /// </summary>
        public void UpdatePlayerEquipment(GameObject playerModel, Items.Equipment equipment)
        {
            if (playerModel == null || equipment == null) return;

            EquipmentModelData equipData = equipmentModels.Find(e => e.equipmentId == equipment.id);
            
            if (equipData != null)
            {
                // 装備タイプに応じたアタッチポイントを取得
                Transform attachPoint = GetAttachPoint(playerModel, equipData.slot);
                
                if (attachPoint != null && equipData.modelPrefab != null)
                {
                    // 既存の装備モデルを削除
                    foreach (Transform child in attachPoint)
                    {
                        Destroy(child.gameObject);
                    }

                    // 新しい装備モデルを配置
                    GameObject equipModel = Instantiate(equipData.modelPrefab, attachPoint);
                    equipModel.transform.localPosition = equipData.localPosition;
                    equipModel.transform.localRotation = Quaternion.Euler(equipData.localRotation);
                    equipModel.transform.localScale = equipData.localScale;
                }
            }
        }

        #endregion

        #region Enemy Model Management

        /// <summary>
        /// 敵モデルをロード
        /// </summary>
        public GameObject LoadEnemyModel(string enemyType, int level = 1)
        {
            EnemyModelData modelData = enemyModels.Find(e => e.enemyType == enemyType);

            if (modelData == null)
            {
                Debug.LogWarning($"Enemy model not found for type: {enemyType}");
                return null;
            }

            // レベルに応じたバリエーションを選択
            GameObject modelPrefab = modelData.modelPrefab;
            
            if (modelData.levelVariations.Count > 0)
            {
                foreach (var variation in modelData.levelVariations)
                {
                    if (level >= variation.minLevel && level <= variation.maxLevel)
                    {
                        modelPrefab = variation.variantPrefab;
                        break;
                    }
                }
            }

            return InstantiateModel(modelPrefab, enemyModelOffset);
        }

        #endregion

        #region Item Model Management

        /// <summary>
        /// アイテムモデルをロード
        /// </summary>
        public GameObject LoadItemModel(string itemId)
        {
            ItemModelData modelData = itemModels.Find(i => i.itemId == itemId);

            if (modelData == null)
            {
                Debug.LogWarning($"Item model not found for id: {itemId}");
                return null;
            }

            return InstantiateModel(modelData.modelPrefab, Vector3.zero);
        }

        #endregion

        #region Effect Management

        /// <summary>
        /// 攻撃エフェクトを再生
        /// </summary>
        public void PlayAttackEffect(string effectName, Vector3 position, Quaternion rotation)
        {
            EffectData effectData = attackEffects.Find(e => e.effectName == effectName);
            
            if (effectData != null && effectData.effectPrefab != null)
            {
                PlayEffect(effectData.effectPrefab, position, rotation, effectData.duration);
            }
        }

        /// <summary>
        /// 魔法エフェクトを再生
        /// </summary>
        public void PlayMagicEffect(string effectName, Vector3 position, Quaternion rotation)
        {
            EffectData effectData = magicEffects.Find(e => e.effectName == effectName);
            
            if (effectData != null && effectData.effectPrefab != null)
            {
                PlayEffect(effectData.effectPrefab, position, rotation, effectData.duration);
            }
        }

        /// <summary>
        /// 回復エフェクトを再生
        /// </summary>
        public void PlayHealEffect(Vector3 position)
        {
            if (healEffect != null)
            {
                PlayEffect(healEffect, position, Quaternion.identity, 1.5f);
            }
        }

        /// <summary>
        /// レベルアップエフェクトを再生
        /// </summary>
        public void PlayLevelUpEffect(Vector3 position)
        {
            if (levelUpEffect != null)
            {
                PlayEffect(levelUpEffect, position, Quaternion.identity, 2.0f);
            }
        }

        #endregion

        #region Helper Methods

        /// <summary>
        /// モデルをインスタンス化
        /// </summary>
        private GameObject InstantiateModel(GameObject prefab, Vector3 offset)
        {
            if (prefab == null) return null;

            GameObject model = Instantiate(prefab);
            model.transform.localPosition = offset;
            model.transform.localScale = Vector3.one * defaultScale;

            return model;
        }

        /// <summary>
        /// 装備のアタッチポイントを取得
        /// </summary>
        private Transform GetAttachPoint(GameObject character, Items.EquipmentSlot slot)
        {
            // キャラクターのボーン構造から適切なアタッチポイントを検索
            Animator animator = character.GetComponent<Animator>();
            
            if (animator == null) return null;

            switch (slot)
            {
                case Items.EquipmentSlot.Weapon:
                    return animator.GetBoneTransform(HumanBodyBones.RightHand);
                
                case Items.EquipmentSlot.Shield:
                    return animator.GetBoneTransform(HumanBodyBones.LeftHand);
                
                case Items.EquipmentSlot.Head:
                    return animator.GetBoneTransform(HumanBodyBones.Head);
                
                case Items.EquipmentSlot.Body:
                    return animator.GetBoneTransform(HumanBodyBones.Chest);
                
                case Items.EquipmentSlot.Accessory1:
                case Items.EquipmentSlot.Accessory2:
                    return animator.GetBoneTransform(HumanBodyBones.Neck);
                
                default:
                    return character.transform;
            }
        }

        /// <summary>
        /// エフェクトを再生
        /// </summary>
        private void PlayEffect(GameObject effectPrefab, Vector3 position, Quaternion rotation, float duration)
        {
            GameObject effect = Instantiate(effectPrefab, position, rotation);
            Destroy(effect, duration);
        }

        #endregion
    }

    #region Data Classes

    /// <summary>
    /// プレイヤーモデルデータ
    /// </summary>
    [System.Serializable]
    public class PlayerModelData
    {
        public string className = "Warrior";
        public int minLevel = 1;
        public int maxLevel = 99;
        public GameObject modelPrefab;
        public Sprite icon;
    }

    /// <summary>
    /// 敵モデルデータ
    /// </summary>
    [System.Serializable]
    public class EnemyModelData
    {
        public string enemyType;
        public string displayName;
        public GameObject modelPrefab;
        public List<EnemyModelVariation> levelVariations = new List<EnemyModelVariation>();
        public Sprite icon;
    }

    /// <summary>
    /// 敵モデルバリエーション
    /// </summary>
    [System.Serializable]
    public class EnemyModelVariation
    {
        public int minLevel;
        public int maxLevel;
        public GameObject variantPrefab;
        public string variantName;
    }

    /// <summary>
    /// アイテムモデルデータ
    /// </summary>
    [System.Serializable]
    public class ItemModelData
    {
        public string itemId;
        public string itemName;
        public GameObject modelPrefab;
        public Sprite icon;
    }

    /// <summary>
    /// 装備品モデルデータ
    /// </summary>
    [System.Serializable]
    public class EquipmentModelData
    {
        public string equipmentId;
        public string equipmentName;
        public Items.EquipmentSlot slot;
        public GameObject modelPrefab;
        public Vector3 localPosition;
        public Vector3 localRotation;
        public Vector3 localScale = Vector3.one;
        public Sprite icon;
    }

    /// <summary>
    /// エフェクトデータ
    /// </summary>
    [System.Serializable]
    public class EffectData
    {
        public string effectName;
        public GameObject effectPrefab;
        public float duration = 1.0f;
        public AudioClip soundEffect;
    }

    #endregion
}
