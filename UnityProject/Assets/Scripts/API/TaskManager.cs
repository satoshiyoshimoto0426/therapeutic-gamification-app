using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.API
{
    /// <summary>
    /// タスク管理を行うクラス
    /// FastAPIのタスク管理サービス（Port 8002）と連携
    /// </summary>
    public class TaskManager : MonoBehaviour
    {
        public static TaskManager Instance { get; private set; }

        [Header("Current Tasks")]
        public List<TaskData> dailyTasks = new List<TaskData>();
        public List<TaskData> completedTasks = new List<TaskData>();

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
        /// 今日のタスクを取得
        /// </summary>
        public void GetDailyTasks(System.Action<List<TaskData>> callback)
        {
            StartCoroutine(GetDailyTasksCoroutine(callback));
        }

        private IEnumerator GetDailyTasksCoroutine(System.Action<List<TaskData>> callback)
        {
            string userId = AuthManager.Instance.userId;

            yield return APIClient.Instance.GetRequest($"/tasks/daily?user_id={userId}", APIClient.Instance.taskPort, (response) =>
            {
                if (response.success)
                {
                    TaskListResponse taskListResponse = response.GetData<TaskListResponse>();

                    if (taskListResponse != null && taskListResponse.tasks != null)
                    {
                        dailyTasks = new List<TaskData>(taskListResponse.tasks);
                        Debug.Log($"[TaskManager] Retrieved {dailyTasks.Count} daily tasks");
                        callback?.Invoke(dailyTasks);
                    }
                    else
                    {
                        callback?.Invoke(new List<TaskData>());
                    }
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to get daily tasks: {response.error}");
                    callback?.Invoke(new List<TaskData>());
                }
            });
        }

        /// <summary>
        /// タスクを作成
        /// </summary>
        public void CreateTask(string title, string description, int difficulty, System.Action<TaskData> callback)
        {
            StartCoroutine(CreateTaskCoroutine(title, description, difficulty, callback));
        }

        private IEnumerator CreateTaskCoroutine(string title, string description, int difficulty, System.Action<TaskData> callback)
        {
            CreateTaskRequest taskData = new CreateTaskRequest
            {
                user_id = AuthManager.Instance.userId,
                title = title,
                description = description,
                difficulty = difficulty
            };

            string jsonData = JsonUtility.ToJson(taskData);

            yield return APIClient.Instance.PostRequest("/tasks/create", APIClient.Instance.taskPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    TaskData newTask = response.GetData<TaskData>();
                    
                    if (newTask != null)
                    {
                        dailyTasks.Add(newTask);
                        Debug.Log($"[TaskManager] Task created: {title}");
                        callback?.Invoke(newTask);
                    }
                    else
                    {
                        callback?.Invoke(null);
                    }
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to create task: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// タスクを完了
        /// </summary>
        public void CompleteTask(string taskId, System.Action<TaskCompletionReward> callback)
        {
            StartCoroutine(CompleteTaskCoroutine(taskId, callback));
        }

        private IEnumerator CompleteTaskCoroutine(string taskId, System.Action<TaskCompletionReward> callback)
        {
            CompleteTaskRequest completeData = new CompleteTaskRequest
            {
                task_id = taskId,
                user_id = AuthManager.Instance.userId
            };

            string jsonData = JsonUtility.ToJson(completeData);

            yield return APIClient.Instance.PostRequest("/tasks/complete", APIClient.Instance.taskPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    TaskCompletionReward reward = response.GetData<TaskCompletionReward>();

                    if (reward != null)
                    {
                        // タスクを完了リストに移動
                        TaskData completedTask = dailyTasks.Find(t => t.task_id == taskId);
                        if (completedTask != null)
                        {
                            completedTask.is_completed = true;
                            completedTasks.Add(completedTask);
                            dailyTasks.Remove(completedTask);
                        }

                        Debug.Log($"[TaskManager] Task completed: {taskId}, XP: {reward.xp_earned}, Gold: {reward.gold_earned}");
                        callback?.Invoke(reward);
                    }
                    else
                    {
                        callback?.Invoke(null);
                    }
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to complete task: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }

        /// <summary>
        /// タスクを更新
        /// </summary>
        public void UpdateTask(string taskId, string title, string description, System.Action<bool> callback)
        {
            StartCoroutine(UpdateTaskCoroutine(taskId, title, description, callback));
        }

        private IEnumerator UpdateTaskCoroutine(string taskId, string title, string description, System.Action<bool> callback)
        {
            UpdateTaskRequest updateData = new UpdateTaskRequest
            {
                task_id = taskId,
                title = title,
                description = description
            };

            string jsonData = JsonUtility.ToJson(updateData);

            yield return APIClient.Instance.PutRequest($"/tasks/{taskId}", APIClient.Instance.taskPort, jsonData, (response) =>
            {
                if (response.success)
                {
                    TaskData task = dailyTasks.Find(t => t.task_id == taskId);
                    if (task != null)
                    {
                        task.title = title;
                        task.description = description;
                    }

                    Debug.Log($"[TaskManager] Task updated: {taskId}");
                    callback?.Invoke(true);
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to update task: {response.error}");
                    callback?.Invoke(false);
                }
            });
        }

        /// <summary>
        /// タスクを削除
        /// </summary>
        public void DeleteTask(string taskId, System.Action<bool> callback)
        {
            StartCoroutine(DeleteTaskCoroutine(taskId, callback));
        }

        private IEnumerator DeleteTaskCoroutine(string taskId, System.Action<bool> callback)
        {
            yield return APIClient.Instance.DeleteRequest($"/tasks/{taskId}", APIClient.Instance.taskPort, (response) =>
            {
                if (response.success)
                {
                    dailyTasks.RemoveAll(t => t.task_id == taskId);
                    Debug.Log($"[TaskManager] Task deleted: {taskId}");
                    callback?.Invoke(true);
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to delete task: {response.error}");
                    callback?.Invoke(false);
                }
            });
        }

        /// <summary>
        /// タスクの進捗を取得
        /// </summary>
        public void GetTaskProgress(System.Action<TaskProgressData> callback)
        {
            StartCoroutine(GetTaskProgressCoroutine(callback));
        }

        private IEnumerator GetTaskProgressCoroutine(System.Action<TaskProgressData> callback)
        {
            string userId = AuthManager.Instance.userId;

            yield return APIClient.Instance.GetRequest($"/tasks/progress?user_id={userId}", APIClient.Instance.taskPort, (response) =>
            {
                if (response.success)
                {
                    TaskProgressData progress = response.GetData<TaskProgressData>();
                    callback?.Invoke(progress);
                }
                else
                {
                    Debug.LogError($"[TaskManager] Failed to get task progress: {response.error}");
                    callback?.Invoke(null);
                }
            });
        }
    }

    // データ構造

    [System.Serializable]
    public class TaskData
    {
        public string task_id;
        public string user_id;
        public string title;
        public string description;
        public int difficulty;  // 1-5
        public bool is_completed;
        public string created_at;
        public string completed_at;
    }

    [System.Serializable]
    public class TaskListResponse
    {
        public TaskData[] tasks;
    }

    [System.Serializable]
    public class CreateTaskRequest
    {
        public string user_id;
        public string title;
        public string description;
        public int difficulty;
    }

    [System.Serializable]
    public class CompleteTaskRequest
    {
        public string task_id;
        public string user_id;
    }

    [System.Serializable]
    public class UpdateTaskRequest
    {
        public string task_id;
        public string title;
        public string description;
    }

    [System.Serializable]
    public class TaskCompletionReward
    {
        public int xp_earned;
        public int gold_earned;
        public bool level_up;
        public int new_level;
    }

    [System.Serializable]
    public class TaskProgressData
    {
        public int total_tasks;
        public int completed_tasks;
        public int completion_rate;
        public int total_xp_earned;
        public int total_gold_earned;
    }
}
