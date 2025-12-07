using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.API
{
    /// <summary>
    /// AIストーリー生成を管理するクラス
    /// FastAPIのAIストーリーサービス（Port 8004）と連携
    /// </summary>
    public class StoryManager : MonoBehaviour
    {
        public static StoryManager Instance { get; private set; }

        [Header("Current Story")]
        public StoryData currentStory;
        public List<StoryData> storyHistory = new List<StoryData>();

        [Header("Settings")]
        public int maxHistoryCount = 30;

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
        /// 毎日のストーリーを生成
        /// </summary>
        public void GenerateDailyStory(System.Action<StoryData> callback)
        {
            StartCoroutine(GenerateDailyStoryCoroutine(callback));
        }

        private IEnumerator GenerateDailyStoryCoroutine(System.Action<StoryData> callback)
        {
            string userId = AuthManager.Instance.userId;

            // プレイヤーの最近の行動を取得
            PlayerActionSummary actionSummary = GetRecentPlayerActions();

            StoryGenerationRequest requestData = new StoryGenerationRequest
            {
                user_id = userId,
                player_level = actionSummary.level,
                tasks_completed = actionSummary.tasksCompleted,
                enemies_defeated = actionSummary.enemiesDefeated,
                floors_cleared = actionSummary.floorsCleared,
                current_mood = actionSummary.currentMood,
                recent_challenges = actionSummary.recentChallenges
            };

            string jsonData = JsonUtility.ToJson(requestData);

            yield return APIClient.Instance.PostRequest("/story/generate", APIClient.Instance.storyPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    StoryData story = response.GetData<StoryData>();

                    if (story != null)
                    {
                        currentStory = story;
                        AddToHistory(story);
                        Debug.Log($"[StoryManager] Generated daily story: {story.title}");
                        callback?.Invoke(story);
                    }
                    else
                    {
                        Debug.LogError("[StoryManager] Failed to parse story data");
                        callback?.Invoke(null);
                    }
                }
                else
                {
                    Debug.LogError($"[StoryManager] Failed to generate story: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// ボス戦後のストーリーを生成
        /// </summary>
        public void GenerateBossVictoryStory(int floor, string bossName, System.Action<StoryData> callback)
        {
            StartCoroutine(GenerateBossVictoryStoryCoroutine(floor, bossName, callback));
        }

        private IEnumerator GenerateBossVictoryStoryCoroutine(int floor, string bossName, System.Action<StoryData> callback)
        {
            string userId = AuthManager.Instance.userId;

            BossVictoryRequest requestData = new BossVictoryRequest
            {
                user_id = userId,
                floor = floor,
                boss_name = bossName,
                victory_time = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            };

            string jsonData = JsonUtility.ToJson(requestData);

            yield return APIClient.Instance.PostRequest("/story/boss-victory", APIClient.Instance.storyPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    StoryData story = response.GetData<StoryData>();
                    
                    if (story != null)
                    {
                        currentStory = story;
                        AddToHistory(story);
                        Debug.Log($"[StoryManager] Generated boss victory story");
                        callback?.Invoke(story);
                    }
                    else
                    {
                        callback?.Invoke(null);
                    }
                }
                else
                {
                    Debug.LogError($"[StoryManager] Failed to generate boss story: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// レベルアップストーリーを生成
        /// </summary>
        public void GenerateLevelUpStory(int newLevel, System.Action<StoryData> callback)
        {
            StartCoroutine(GenerateLevelUpStoryCoroutine(newLevel, callback));
        }

        private IEnumerator GenerateLevelUpStoryCoroutine(int newLevel, System.Action<StoryData> callback)
        {
            string userId = AuthManager.Instance.userId;

            LevelUpRequest requestData = new LevelUpRequest
            {
                user_id = userId,
                new_level = newLevel,
                timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            };

            string jsonData = JsonUtility.ToJson(requestData);

            yield return APIClient.Instance.PostRequest("/story/level-up", APIClient.Instance.storyPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    StoryData story = response.GetData<StoryData>();
                    
                    if (story != null)
                    {
                        currentStory = story;
                        AddToHistory(story);
                        Debug.Log($"[StoryManager] Generated level-up story");
                        callback?.Invoke(story);
                    }
                    else
                    {
                        callback?.Invoke(null);
                    }
                }
                else
                {
                    Debug.LogError($"[StoryManager] Failed to generate level-up story: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// ストーリー履歴を取得
        /// </summary>
        public void GetStoryHistory(System.Action<List<StoryData>> callback)
        {
            StartCoroutine(GetStoryHistoryCoroutine(callback));
        }

        private IEnumerator GetStoryHistoryCoroutine(System.Action<List<StoryData>> callback)
        {
            string userId = AuthManager.Instance.userId;

            yield return APIClient.Instance.GetRequest($"/story/history?user_id={userId}&limit={maxHistoryCount}", 
                APIClient.Instance.storyPort, (response) =>
            {
                if (response.success)
                {
                    StoryHistoryResponse historyResponse = response.GetData<StoryHistoryResponse>();
                    
                    if (historyResponse != null && historyResponse.stories != null)
                    {
                        storyHistory = new List<StoryData>(historyResponse.stories);
                        Debug.Log($"[StoryManager] Retrieved {storyHistory.Count} stories");
                        callback?.Invoke(storyHistory);
                    }
                    else
                    {
                        callback?.Invoke(new List<StoryData>());
                    }
                }
                else
                {
                    Debug.LogError($"[StoryManager] Failed to get story history: {response.error}");
                    callback?.Invoke(new List<StoryData>());
                }
            });
        }

        /// <summary>
        /// プレイヤーの最近の行動を取得
        /// </summary>
        private PlayerActionSummary GetRecentPlayerActions()
        {
            PlayerActionSummary summary = new PlayerActionSummary();

            // プレイヤー情報を取得
            Character.Player player = FindObjectOfType<Character.Player>();
            if (player != null)
            {
                summary.level = player.stats.Level;
                summary.currentFloor = Core.GameManager.Instance?.currentFloor ?? 1;
            }

            // タスク完了数を取得
            if (TaskManager.Instance != null)
            {
                summary.tasksCompleted = TaskManager.Instance.completedTasks.Count;
            }

            // TODO: 敵撃破数、フロアクリア数などの統計情報を取得

            return summary;
        }

        /// <summary>
        /// ストーリーを履歴に追加
        /// </summary>
        private void AddToHistory(StoryData story)
        {
            if (story == null) return;

            storyHistory.Insert(0, story);

            // 履歴の上限を管理
            if (storyHistory.Count > maxHistoryCount)
            {
                storyHistory.RemoveAt(storyHistory.Count - 1);
            }
        }

        /// <summary>
        /// ストーリーを表示（UI連携）
        /// </summary>
        public void ShowStory(StoryData story)
        {
            if (story == null) return;

            // TODO: ストーリーUIを表示
            Debug.Log($"[StoryManager] Showing story: {story.title}");
            Debug.Log(story.content);
        }
    }

    // データ構造

    [System.Serializable]
    public class StoryData
    {
        public string story_id;
        public string user_id;
        public string title;
        public string content;
        public string story_type;  // daily, boss_victory, level_up
        public string created_at;
        public string[] tags;
    }

    [System.Serializable]
    public class StoryGenerationRequest
    {
        public string user_id;
        public int player_level;
        public int tasks_completed;
        public int enemies_defeated;
        public int floors_cleared;
        public string current_mood;
        public string[] recent_challenges;
    }

    [System.Serializable]
    public class BossVictoryRequest
    {
        public string user_id;
        public int floor;
        public string boss_name;
        public string victory_time;
    }

    [System.Serializable]
    public class LevelUpRequest
    {
        public string user_id;
        public int new_level;
        public string timestamp;
    }

    [System.Serializable]
    public class StoryHistoryResponse
    {
        public StoryData[] stories;
        public int total_count;
    }

    [System.Serializable]
    public class PlayerActionSummary
    {
        public int level;
        public int currentFloor;
        public int tasksCompleted;
        public int enemiesDefeated;
        public int floorsCleared;
        public string currentMood = "normal";
        public string[] recentChallenges = new string[] { };
    }
}
