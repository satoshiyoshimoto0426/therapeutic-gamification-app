using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using System.Text;

namespace KokoroNoBoukensha.API
{
    /// <summary>
    /// FastAPIバックエンドとの通信を管理するクライアント
    /// </summary>
    public class APIClient : MonoBehaviour
    {
        public static APIClient Instance { get; private set; }

        [Header("API Settings")]
        public string baseURL = "http://localhost";
        public int authPort = 8000;
        public int coreGamePort = 8001;
        public int taskPort = 8002;
        public int moodPort = 8003;
        public int storyPort = 8004;

        [Header("Authentication")]
        private string accessToken = "";
        private string refreshToken = "";

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

            LoadTokens();
        }

        /// <summary>
        /// トークンをロード
        /// </summary>
        private void LoadTokens()
        {
            accessToken = PlayerPrefs.GetString("access_token", "");
            refreshToken = PlayerPrefs.GetString("refresh_token", "");
        }

        /// <summary>
        /// トークンを保存
        /// </summary>
        private void SaveTokens(string access, string refresh)
        {
            accessToken = access;
            refreshToken = refresh;
            PlayerPrefs.SetString("access_token", access);
            PlayerPrefs.SetString("refresh_token", refresh);
            PlayerPrefs.Save();
        }

        /// <summary>
        /// トークンをクリア
        /// </summary>
        public void ClearTokens()
        {
            accessToken = "";
            refreshToken = "";
            PlayerPrefs.DeleteKey("access_token");
            PlayerPrefs.DeleteKey("refresh_token");
            PlayerPrefs.Save();
        }

        /// <summary>
        /// 認証済みかチェック
        /// </summary>
        public bool IsAuthenticated()
        {
            return !string.IsNullOrEmpty(accessToken);
        }

        /// <summary>
        /// GETリクエスト
        /// </summary>
        public IEnumerator GetRequest(string endpoint, int port, Action<APIResponse> callback, bool requiresAuth = true)
        {
            string url = $"{baseURL}:{port}{endpoint}";

            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                // 認証ヘッダー追加
                if (requiresAuth && IsAuthenticated())
                {
                    request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                }

                yield return request.SendWebRequest();

                APIResponse response = new APIResponse();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    response.success = true;
                    response.data = request.downloadHandler.text;
                    response.statusCode = request.responseCode;
                }
                else
                {
                    response.success = false;
                    response.error = request.error;
                    response.statusCode = request.responseCode;
                    Debug.LogError($"[APIClient] GET failed: {url} - {request.error}");
                }

                callback?.Invoke(response);
            }
        }

        /// <summary>
        /// POSTリクエスト
        /// </summary>
        public IEnumerator PostRequest(string endpoint, int port, string jsonData, Action<APIResponse> callback, bool requiresAuth = true)
        {
            string url = $"{baseURL}:{port}{endpoint}";

            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                // 認証ヘッダー追加
                if (requiresAuth && IsAuthenticated())
                {
                    request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                }

                yield return request.SendWebRequest();

                APIResponse response = new APIResponse();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    response.success = true;
                    response.data = request.downloadHandler.text;
                    response.statusCode = request.responseCode;
                }
                else
                {
                    response.success = false;
                    response.error = request.error;
                    response.statusCode = request.responseCode;
                    Debug.LogError($"[APIClient] POST failed: {url} - {request.error}");
                }

                callback?.Invoke(response);
            }
        }

        /// <summary>
        /// PUTリクエスト
        /// </summary>
        public IEnumerator PutRequest(string endpoint, int port, string jsonData, Action<APIResponse> callback, bool requiresAuth = true)
        {
            string url = $"{baseURL}:{port}{endpoint}";

            using (UnityWebRequest request = UnityWebRequest.Put(url, jsonData))
            {
                request.SetRequestHeader("Content-Type", "application/json");

                // 認証ヘッダー追加
                if (requiresAuth && IsAuthenticated())
                {
                    request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                }

                yield return request.SendWebRequest();

                APIResponse response = new APIResponse();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    response.success = true;
                    response.data = request.downloadHandler.text;
                    response.statusCode = request.responseCode;
                }
                else
                {
                    response.success = false;
                    response.error = request.error;
                    response.statusCode = request.responseCode;
                    Debug.LogError($"[APIClient] PUT failed: {url} - {request.error}");
                }

                callback?.Invoke(response);
            }
        }

        /// <summary>
        /// DELETEリクエスト
        /// </summary>
        public IEnumerator DeleteRequest(string endpoint, int port, Action<APIResponse> callback, bool requiresAuth = true)
        {
            string url = $"{baseURL}:{port}{endpoint}";

            using (UnityWebRequest request = UnityWebRequest.Delete(url))
            {
                // 認証ヘッダー追加
                if (requiresAuth && IsAuthenticated())
                {
                    request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                }

                yield return request.SendWebRequest();

                APIResponse response = new APIResponse();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    response.success = true;
                    response.data = request.downloadHandler.text;
                    response.statusCode = request.responseCode;
                }
                else
                {
                    response.success = false;
                    response.error = request.error;
                    response.statusCode = request.responseCode;
                    Debug.LogError($"[APIClient] DELETE failed: {url} - {request.error}");
                }

                callback?.Invoke(response);
            }
        }

        /// <summary>
        /// トークンをセット（外部から設定用）
        /// </summary>
        public void SetTokens(string access, string refresh)
        {
            SaveTokens(access, refresh);
        }
    }

    /// <summary>
    /// APIレスポンスのデータ構造
    /// </summary>
    [System.Serializable]
    public class APIResponse
    {
        public bool success;
        public string data;
        public string error;
        public long statusCode;

        public T GetData<T>()
        {
            if (success && !string.IsNullOrEmpty(data))
            {
                return JsonUtility.FromJson<T>(data);
            }
            return default(T);
        }
    }
}
