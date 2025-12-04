using UnityEngine;

namespace KokoroNoBoukensha.Core
{
    /// <summary>
    /// カメラコントローラー
    /// プレイヤーを追跡する3Dカメラ
    /// </summary>
    public class CameraController : MonoBehaviour
    {
        public static CameraController Instance { get; private set; }

        [Header("Target")]
        public Transform target;  // プレイヤー
        public Vector3 offset = new Vector3(0f, 10f, -10f);

        [Header("Camera Settings")]
        public CameraMode cameraMode = CameraMode.TopDown;
        public float followSpeed = 5f;
        public float rotationSpeed = 100f;

        [Header("Top-Down Settings")]
        public float topDownHeight = 15f;
        public float topDownAngle = 60f;

        [Header("Third-Person Settings")]
        public float thirdPersonDistance = 8f;
        public float thirdPersonHeight = 3f;

        [Header("Zoom")]
        public float minZoom = 5f;
        public float maxZoom = 20f;
        public float zoomSpeed = 2f;
        private float currentZoom = 10f;

        [Header("Boundaries")]
        public bool useBoundaries = true;
        public Vector2 minBoundary = new Vector2(-50f, -50f);
        public Vector2 maxBoundary = new Vector2(50f, 50f);

        private Vector3 targetPosition;
        private Quaternion targetRotation;

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

        private void Start()
        {
            if (target == null)
            {
                Character.Player player = FindObjectOfType<Character.Player>();
                if (player != null)
                {
                    target = player.transform;
                }
            }

            currentZoom = topDownHeight;
            SetCameraMode(cameraMode);
        }

        private void LateUpdate()
        {
            if (target == null) return;

            HandleInput();
            UpdateCameraPosition();
            UpdateCameraRotation();
        }

        /// <summary>
        /// 入力処理
        /// </summary>
        private void HandleInput()
        {
            // ズーム（マウスホイール）
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (scroll != 0f)
            {
                currentZoom -= scroll * zoomSpeed;
                currentZoom = Mathf.Clamp(currentZoom, minZoom, maxZoom);
            }

            // カメラモード切り替え（Cキー）
            if (Input.GetKeyDown(KeyCode.C))
            {
                ToggleCameraMode();
            }

            // カメラ回転（Q/Eキー）
            if (Input.GetKey(KeyCode.Q))
            {
                RotateCamera(-rotationSpeed * Time.deltaTime);
            }
            if (Input.GetKey(KeyCode.E))
            {
                RotateCamera(rotationSpeed * Time.deltaTime);
            }
        }

        /// <summary>
        /// カメラ位置を更新
        /// </summary>
        private void UpdateCameraPosition()
        {
            switch (cameraMode)
            {
                case CameraMode.TopDown:
                    UpdateTopDownCamera();
                    break;
                case CameraMode.ThirdPerson:
                    UpdateThirdPersonCamera();
                    break;
                case CameraMode.Isometric:
                    UpdateIsometricCamera();
                    break;
            }

            // スムーズに移動
            transform.position = Vector3.Lerp(transform.position, targetPosition, followSpeed * Time.deltaTime);
        }

        /// <summary>
        /// トップダウンカメラ
        /// </summary>
        private void UpdateTopDownCamera()
        {
            targetPosition = target.position + new Vector3(0f, currentZoom, 0f);

            // 境界制限
            if (useBoundaries)
            {
                targetPosition.x = Mathf.Clamp(targetPosition.x, minBoundary.x, maxBoundary.x);
                targetPosition.z = Mathf.Clamp(targetPosition.z, minBoundary.y, maxBoundary.y);
            }

            targetRotation = Quaternion.Euler(topDownAngle, 0f, 0f);
        }

        /// <summary>
        /// 三人称カメラ
        /// </summary>
        private void UpdateThirdPersonCamera()
        {
            Vector3 direction = -transform.forward;
            targetPosition = target.position + direction * thirdPersonDistance + Vector3.up * thirdPersonHeight;

            // 境界制限
            if (useBoundaries)
            {
                targetPosition.x = Mathf.Clamp(targetPosition.x, minBoundary.x, maxBoundary.x);
                targetPosition.z = Mathf.Clamp(targetPosition.z, minBoundary.y, maxBoundary.y);
            }
        }

        /// <summary>
        /// アイソメトリックカメラ
        /// </summary>
        private void UpdateIsometricCamera()
        {
            float isoAngle = 35.264f; // アイソメトリック角度
            Vector3 isoOffset = new Vector3(currentZoom, currentZoom, -currentZoom).normalized * currentZoom;
            targetPosition = target.position + isoOffset;

            targetRotation = Quaternion.Euler(isoAngle, 45f, 0f);
        }

        /// <summary>
        /// カメラ回転を更新
        /// </summary>
        private void UpdateCameraRotation()
        {
            transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, followSpeed * Time.deltaTime);
        }

        /// <summary>
        /// カメラモードを切り替え
        /// </summary>
        public void ToggleCameraMode()
        {
            switch (cameraMode)
            {
                case CameraMode.TopDown:
                    SetCameraMode(CameraMode.ThirdPerson);
                    break;
                case CameraMode.ThirdPerson:
                    SetCameraMode(CameraMode.Isometric);
                    break;
                case CameraMode.Isometric:
                    SetCameraMode(CameraMode.TopDown);
                    break;
            }
        }

        /// <summary>
        /// カメラモードを設定
        /// </summary>
        public void SetCameraMode(CameraMode mode)
        {
            cameraMode = mode;
            
            switch (mode)
            {
                case CameraMode.TopDown:
                    currentZoom = topDownHeight;
                    break;
                case CameraMode.ThirdPerson:
                    currentZoom = thirdPersonDistance;
                    break;
                case CameraMode.Isometric:
                    currentZoom = 15f;
                    break;
            }

            Debug.Log($"[CameraController] Camera mode changed to: {mode}");
        }

        /// <summary>
        /// カメラを回転
        /// </summary>
        public void RotateCamera(float angle)
        {
            transform.RotateAround(target.position, Vector3.up, angle);
        }

        /// <summary>
        /// ターゲットを設定
        /// </summary>
        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
        }

        /// <summary>
        /// カメラを振動させる（ダメージ演出など）
        /// </summary>
        public void Shake(float duration = 0.2f, float magnitude = 0.1f)
        {
            StartCoroutine(ShakeCoroutine(duration, magnitude));
        }

        private System.Collections.IEnumerator ShakeCoroutine(float duration, float magnitude)
        {
            Vector3 originalPosition = transform.position;
            float elapsed = 0f;

            while (elapsed < duration)
            {
                float x = Random.Range(-1f, 1f) * magnitude;
                float y = Random.Range(-1f, 1f) * magnitude;

                transform.position = originalPosition + new Vector3(x, y, 0f);

                elapsed += Time.deltaTime;
                yield return null;
            }

            transform.position = originalPosition;
        }
    }

    /// <summary>
    /// カメラモード
    /// </summary>
    public enum CameraMode
    {
        TopDown,       // 真上から見下ろし
        ThirdPerson,   // 三人称視点
        Isometric      // アイソメトリック
    }
}
