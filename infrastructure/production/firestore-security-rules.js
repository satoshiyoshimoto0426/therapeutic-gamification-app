// Firestore本番環境セキュリティルール
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // ユーザープロファイル - 本人のみアクセス可能
    match /user_profiles/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      
      // Guardian権限チェック
      allow read: if request.auth != null && 
        exists(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)) &&
        get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.permissions.hasAny(['view-only', 'task-edit']) &&
        get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.target_user == userId;
    }
    
    // タスク管理 - 本人とGuardian（task-edit権限）
    match /tasks/{taskId} {
      allow read: if request.auth != null && 
        (resource.data.uid == request.auth.uid ||
         (exists(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.permissions.hasAny(['view-only', 'task-edit']) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.target_user == resource.data.uid));
      
      allow write: if request.auth != null && 
        (resource.data.uid == request.auth.uid ||
         (exists(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.permissions.hasAny(['task-edit']) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.target_user == resource.data.uid));
    }
    
    // ストーリー状態 - 本人のみ
    match /story_states/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 気分ログ - 本人とGuardian（view-only以上）
    match /mood_logs/{logId} {
      allow read: if request.auth != null && 
        (resource.data.uid == request.auth.uid ||
         (exists(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.permissions.hasAny(['view-only', 'task-edit']) &&
          get(/databases/$(database)/documents/guardian_permissions/$(request.auth.uid)).data.target_user == resource.data.uid));
      
      allow write: if request.auth != null && resource.data.uid == request.auth.uid;
    }
    
    // Mandalaグリッド - 本人のみ
    match /mandala_grids/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Guardian権限管理 - システム管理者のみ
    match /guardian_permissions/{permissionId} {
      allow read: if request.auth != null && 
        (request.auth.uid == resource.data.guardian_uid || 
         request.auth.uid == resource.data.target_user);
      allow write: if request.auth != null && 
        request.auth.token.admin == true;
    }
    
    // 治療安全性ログ - システムのみ
    match /safety_logs/{logId} {
      allow read, write: if request.auth != null && 
        request.auth.token.service_account == true;
    }
    
    // パフォーマンスメトリクス - システムのみ
    match /performance_metrics/{metricId} {
      allow read, write: if request.auth != null && 
        request.auth.token.service_account == true;
    }
    
    // データ検証関数
    function isValidUserData(data) {
      return data.keys().hasAll(['uid', 'created_at']) &&
             data.uid is string &&
             data.created_at is timestamp;
    }
    
    function isValidTaskData(data) {
      return data.keys().hasAll(['uid', 'task_type', 'difficulty', 'created_at']) &&
             data.uid is string &&
             data.task_type in ['routine', 'one_shot', 'skill_up', 'social'] &&
             data.difficulty >= 1 && data.difficulty <= 5 &&
             data.created_at is timestamp;
    }
    
    // レート制限（1分間に120リクエスト）
    function checkRateLimit() {
      return request.time > resource.data.last_request_time + duration.value(0, 500); // 500ms間隔
    }
  }
}