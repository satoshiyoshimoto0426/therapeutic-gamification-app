using UnityEngine;
using UnityEngine.UI;
using System.Collections;

namespace KokoroNoBoukensha.Tutorial
{
    /// <summary>
    /// チュートリアルポインターシステム
    /// 3D空間やUI要素を指し示す矢印を表示
    /// </summary>
    public class TutorialPointer : MonoBehaviour
    {
        [Header("Pointer Settings")]
        [Tooltip("ポインターアイコン")]
        public RectTransform pointerIcon;
        
        [Tooltip("ポインター画像")]
        public Image pointerImage;
        
        [Tooltip("ポインター色")]
        public Color pointerColor = Color.yellow;
        
        [Tooltip("オフセット")]
        public Vector3 offset = new Vector3(0, 50, 0);

        [Header("Animation Settings")]
        [Tooltip("バウンスアニメーション")]
        public bool enableBounce = true;
        
        [Tooltip("バウンス速度")]
        public float bounceSpeed = 3f;
        
        [Tooltip("バウンス距離")]
        public float bounceDistance = 10f;
        
        [Tooltip("回転アニメーション")]
        public bool enableRotation = false;
        
        [Tooltip("回転速度")]
        public float rotationSpeed = 90f;

        private Transform worldTarget;
        private RectTransform uiTarget;
        private Camera mainCamera;
        private Canvas canvas;
        private bool isShowing = false;
        private Vector3 initialPosition;
        private float animationTimer = 0f;

        private void Awake()
        {
            mainCamera = Camera.main;
            canvas = GetComponentInParent<Canvas>();

            if (pointerImage != null)
            {
                pointerImage.color = pointerColor;
            }

            // 初期状態は非表示
            HidePointer();
        }

        private void Update()
        {
            if (!isShowing) return;

            // ターゲットを追跡
            UpdatePointerPosition();

            // アニメーション
            if (enableBounce || enableRotation)
            {
                AnimatePointer();
            }
        }

        /// <summary>
        /// ポインターを表示（ワールド座標）
        /// </summary>
        public void ShowPointer(Transform target)
        {
            worldTarget = target;
            uiTarget = null;
            isShowing = true;
            animationTimer = 0f;

            if (pointerIcon != null)
            {
                pointerIcon.gameObject.SetActive(true);
                initialPosition = pointerIcon.anchoredPosition;
            }
        }

        /// <summary>
        /// ポインターを表示（UI座標）
        /// </summary>
        public void ShowPointer(RectTransform target)
        {
            uiTarget = target;
            worldTarget = null;
            isShowing = true;
            animationTimer = 0f;

            if (pointerIcon != null)
            {
                pointerIcon.gameObject.SetActive(true);
                initialPosition = pointerIcon.anchoredPosition;
            }
        }

        /// <summary>
        /// ポインターを表示（名前で検索）
        /// </summary>
        public void ShowPointer(string targetName)
        {
            // ワールドオブジェクトを検索
            GameObject worldObj = GameObject.Find(targetName);
            if (worldObj != null)
            {
                ShowPointer(worldObj.transform);
                return;
            }

            // UIオブジェクトを検索
            GameObject[] allObjects = FindObjectsOfType<GameObject>();
            foreach (GameObject obj in allObjects)
            {
                if (obj.name == targetName)
                {
                    RectTransform rectTransform = obj.GetComponent<RectTransform>();
                    if (rectTransform != null)
                    {
                        ShowPointer(rectTransform);
                        return;
                    }
                }
            }

            Debug.LogWarning($"[TutorialPointer] Target not found: {targetName}");
        }

        /// <summary>
        /// ポインター位置を更新
        /// </summary>
        private void UpdatePointerPosition()
        {
            if (pointerIcon == null) return;

            Vector2 screenPosition;

            if (worldTarget != null)
            {
                // ワールド座標をスクリーン座標に変換
                Vector3 worldPosition = worldTarget.position + offset;
                Vector3 screenPos = mainCamera.WorldToScreenPoint(worldPosition);

                // カメラの背後にある場合は非表示
                if (screenPos.z < 0)
                {
                    pointerIcon.gameObject.SetActive(false);
                    return;
                }

                pointerIcon.gameObject.SetActive(true);

                // Canvas座標に変換
                RectTransformUtility.ScreenPointToLocalPointInRectangle(
                    canvas.transform as RectTransform,
                    screenPos,
                    canvas.worldCamera,
                    out screenPosition
                );

                pointerIcon.anchoredPosition = screenPosition;
            }
            else if (uiTarget != null)
            {
                // UI座標の場合
                pointerIcon.position = uiTarget.position + offset;
            }
        }

        /// <summary>
        /// ポインターアニメーション
        /// </summary>
        private void AnimatePointer()
        {
            animationTimer += Time.deltaTime;

            if (enableBounce)
            {
                float bounce = Mathf.Sin(animationTimer * bounceSpeed) * bounceDistance;
                pointerIcon.anchoredPosition = initialPosition + new Vector2(0, bounce);
            }

            if (enableRotation)
            {
                float rotation = animationTimer * rotationSpeed;
                pointerIcon.rotation = Quaternion.Euler(0, 0, rotation);
            }
        }

        /// <summary>
        /// ポインターを非表示
        /// </summary>
        public void HidePointer()
        {
            isShowing = false;
            worldTarget = null;
            uiTarget = null;

            if (pointerIcon != null)
            {
                pointerIcon.gameObject.SetActive(false);
            }
        }
    }
}
