using UnityEngine;
using System.Collections;

namespace KokoroNoBoukensha.API
{
    /// <summary>
    /// 認証を管理するクラス
    /// FastAPIの認証サービス（Port 8000）と連携
    /// </summary>
    public class AuthManager : MonoBehaviour
    {
        public static AuthManager Instance { get; private set; }

        [Header("User Info")]
        public string userId = "";
        public string username = "";
        public bool isLoggedIn = false;

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
        }

        /// <summary>
        /// ログイン
        /// </summary>
        public void Login(string username, string password, System.Action<bool, string> callback)
        {
            StartCoroutine(LoginCoroutine(username, password, callback));
        }

        private IEnumerator LoginCoroutine(string username, string password, System.Action<bool, string> callback)
        {
            LoginRequest loginData = new LoginRequest
            {
                username = username,
                password = password
            };

            string jsonData = JsonUtility.ToJson(loginData);

            yield return APIClient.Instance.PostRequest("/auth/login", APIClient.Instance.authPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    LoginResponse loginResponse = response.GetData<LoginResponse>();

                    if (loginResponse != null)
                    {
                        // トークンを保存
                        APIClient.Instance.SetTokens(loginResponse.access_token, loginResponse.refresh_token);

                        // ユーザー情報を保存
                        this.userId = loginResponse.user_id;
                        this.username = username;
                        this.isLoggedIn = true;

                        PlayerPrefs.SetString("user_id", userId);
                        PlayerPrefs.SetString("username", username);
                        PlayerPrefs.Save();

                        Debug.Log($"[AuthManager] Login successful: {username}");
                        callback?.Invoke(true, "ログイン成功");
                    }
                    else
                    {
                        Debug.LogError("[AuthManager] Failed to parse login response");
                        callback?.Invoke(false, "ログイン失敗：レスポンス解析エラー");
                    }
                }
                else
                {
                    Debug.LogError($"[AuthManager] Login failed: {response.error}");
                    callback?.Invoke(false, $"ログイン失敗：{response.error}");
                }
            }, requiresAuth: false);
        }

        /// <summary>
        /// 新規登録
        /// </summary>
        public void Register(string username, string email, string password, System.Action<bool, string> callback)
        {
            StartCoroutine(RegisterCoroutine(username, email, password, callback));
        }

        private IEnumerator RegisterCoroutine(string username, string email, string password, System.Action<bool, string> callback)
        {
            RegisterRequest registerData = new RegisterRequest
            {
                username = username,
                email = email,
                password = password
            };

            string jsonData = JsonUtility.ToJson(registerData);

            yield return APIClient.Instance.PostRequest("/auth/register", APIClient.Instance.authPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    Debug.Log($"[AuthManager] Registration successful: {username}");
                    callback?.Invoke(true, "登録成功");
                }
                else
                {
                    Debug.LogError($"[AuthManager] Registration failed: {response.error}");
                    callback?.Invoke(false, $"登録失敗：{response.error}");
                }
            }, requiresAuth: false);
        }

        /// <summary>
        /// ログアウト
        /// </summary>
        public void Logout()
        {
            APIClient.Instance.ClearTokens();
            userId = "";
            username = "";
            isLoggedIn = false;

            PlayerPrefs.DeleteKey("user_id");
            PlayerPrefs.DeleteKey("username");
            PlayerPrefs.Save();

            Debug.Log("[AuthManager] Logged out");
        }

        /// <summary>
        /// トークンリフレッシュ
        /// </summary>
        public void RefreshToken(System.Action<bool> callback)
        {
            StartCoroutine(RefreshTokenCoroutine(callback));
        }

        private IEnumerator RefreshTokenCoroutine(System.Action<bool> callback)
        {
            yield return APIClient.Instance.PostRequest("/auth/refresh", APIClient.Instance.authPort, "{}", (response) =>
            {
                if (response.success)
                {
                    LoginResponse refreshResponse = response.GetData<LoginResponse>();

                    if (refreshResponse != null)
                    {
                        APIClient.Instance.SetTokens(refreshResponse.access_token, refreshResponse.refresh_token);
                        Debug.Log("[AuthManager] Token refreshed");
                        callback?.Invoke(true);
                    }
                    else
                    {
                        callback?.Invoke(false);
                    }
                }
                else
                {
                    Debug.LogError($"[AuthManager] Token refresh failed: {response.error}");
                    callback?.Invoke(false);
                }
            });
        }

        /// <summary>
        /// ユーザー情報を取得
        /// </summary>
        public void GetUserProfile(System.Action<UserProfile> callback)
        {
            StartCoroutine(GetUserProfileCoroutine(callback));
        }

        private IEnumerator GetUserProfileCoroutine(System.Action<UserProfile> callback)
        {
            yield return APIClient.Instance.GetRequest("/auth/profile", APIClient.Instance.authPort, (response) =>
            {
                if (response.success)
                {
                    UserProfile profile = response.GetData<UserProfile>();
                    callback?.Invoke(profile);
                }
                else
                {
                    Debug.LogError($"[AuthManager] Failed to get user profile: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// 自動ログイン（保存されたトークンを使用）
        /// </summary>
        public void TryAutoLogin(System.Action<bool> callback)
        {
            if (APIClient.Instance.IsAuthenticated())
            {
                // 保存されたユーザー情報をロード
                userId = PlayerPrefs.GetString("user_id", "");
                username = PlayerPrefs.GetString("username", "");

                if (!string.IsNullOrEmpty(userId))
                {
                    isLoggedIn = true;
                    Debug.Log($"[AuthManager] Auto-login successful: {username}");
                    callback?.Invoke(true);
                }
                else
                {
                    callback?.Invoke(false);
                }
            }
            else
            {
                callback?.Invoke(false);
            }
        }
    }

    // データ構造

    [System.Serializable]
    public class LoginRequest
    {
        public string username;
        public string password;
    }

    [System.Serializable]
    public class RegisterRequest
    {
        public string username;
        public string email;
        public string password;
    }

    [System.Serializable]
    public class LoginResponse
    {
        public string access_token;
        public string refresh_token;
        public string token_type;
        public string user_id;
    }

    [System.Serializable]
    public class UserProfile
    {
        public string user_id;
        public string username;
        public string email;
        public int level;
        public int experience;
        public int gold;
        public string created_at;
    }
}
