using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Tutorial
{
    /// <summary>
    /// チュートリアルハイライトシステム
    /// UI要素を強調表示する
    /// </summary>
    public class TutorialHighlight : MonoBehaviour
    {
        [Header("Highlight Settings")]
        [Tooltip("ハイライトオーバーレイ")]
        public GameObject highlightOverlay;
        
        [Tooltip("ハイライトフレーム")]
        public RectTransform highlightFrame;
        
        [Tooltip("ハイライト色")]
        public Color highlightColor = new Color(1f, 1f, 0f, 0.5f);
        
        [Tooltip("パルスアニメーション速度")]
        public float pulseSpeed = 2f;
        
        [Tooltip("パルスアニメーション強度")]
        public float pulseIntensity = 0.2f;

        [Header("UI Element Registry")]
        [Tooltip("ハイライト対象のUI要素")]
        public List<HighlightTarget> highlightTargets = new List<HighlightTarget>();

        private RectTransform currentTarget;
        private Image overlayImage;
        private Image frameImage;
        private bool isHighlighting = false;
        private float pulseTimer = 0f;

        private void Awake()
        {
            // オーバーレイ画像取得
            if (highlightOverlay != null)
            {
                overlayImage = highlightOverlay.GetComponent<Image>();
                if (overlayImage == null)
                {
                    overlayImage = highlightOverlay.AddComponent<Image>();
                }
                overlayImage.color = new Color(0, 0, 0, 0.7f); // 半透明黒
                overlayImage.raycastTarget = false;
            }

            // フレーム画像取得
            if (highlightFrame != null)
            {
                frameImage = highlightFrame.GetComponent<Image>();
                if (frameImage == null)
                {
                    frameImage = highlightFrame.AddComponent<Image>();
                }
                frameImage.color = highlightColor;
            }

            // 初期状態は非表示
            ClearHighlight();
        }

        private void Update()
        {
            if (isHighlighting && highlightFrame != null)
            {
                // パルスアニメーション
                pulseTimer += Time.deltaTime * pulseSpeed;
                float pulse = 1f + Mathf.Sin(pulseTimer) * pulseIntensity;
                highlightFrame.localScale = Vector3.one * pulse;

                // ターゲットの位置に追従
                if (currentTarget != null)
                {
                    UpdateHighlightPosition();
                }
            }
        }

        /// <summary>
        /// UI要素をハイライト
        /// </summary>
        public void HighlightUI(string targetId)
        {
            HighlightTarget target = highlightTargets.Find(t => t.id == targetId);
            
            if (target == null || target.targetRect == null)
            {
                Debug.LogWarning($"[TutorialHighlight] Target not found: {targetId}");
                return;
            }

            currentTarget = target.targetRect;
            isHighlighting = true;

            // オーバーレイ表示
            if (highlightOverlay != null)
            {
                highlightOverlay.SetActive(true);
            }

            // ハイライトフレーム表示
            if (highlightFrame != null)
            {
                highlightFrame.gameObject.SetActive(true);
                UpdateHighlightPosition();
            }

            Debug.Log($"[TutorialHighlight] Highlighting: {targetId}");
        }

        /// <summary>
        /// ハイライト位置を更新
        /// </summary>
        private void UpdateHighlightPosition()
        {
            if (currentTarget == null || highlightFrame == null) return;

            // ターゲットの位置とサイズに合わせる
            highlightFrame.position = currentTarget.position;
            highlightFrame.sizeDelta = currentTarget.sizeDelta * 1.1f; // 少し大きめ
        }

        /// <summary>
        /// ハイライトをクリア
        /// </summary>
        public void ClearHighlight()
        {
            isHighlighting = false;
            currentTarget = null;
            pulseTimer = 0f;

            if (highlightOverlay != null)
            {
                highlightOverlay.SetActive(false);
            }

            if (highlightFrame != null)
            {
                highlightFrame.gameObject.SetActive(false);
            }
        }

        /// <summary>
        /// ハイライトターゲットを登録
        /// </summary>
        public void RegisterTarget(string id, RectTransform rect)
        {
            if (highlightTargets.Find(t => t.id == id) == null)
            {
                highlightTargets.Add(new HighlightTarget { id = id, targetRect = rect });
            }
        }

        /// <summary>
        /// ハイライトターゲットを解除
        /// </summary>
        public void UnregisterTarget(string id)
        {
            highlightTargets.RemoveAll(t => t.id == id);
        }
    }

    /// <summary>
    /// ハイライトターゲット
    /// </summary>
    [System.Serializable]
    public class HighlightTarget
    {
        public string id;
        public RectTransform targetRect;
    }
}
