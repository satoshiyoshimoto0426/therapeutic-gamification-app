# Task Management Service

## 概要

4種類のタスクタイプ管理機能とXP計算統合を提供するサービスです。Routine、One-Shot、Skill-Up、Socialタスクの作成・管理機能を実装し、ADHD支援機能とクリスタル属性システムを統合しています。

## 実装された機能

### 4種類のタスクタイプ
- **Routine（ルーチン）**: 日常習慣タスク（朝の運動、読書など）
- **One-Shot（単発）**: 一回限りのタスク（プレゼン準備、買い物など）
- **Skill-Up（スキルアップ）**: 学習・成長タスク（プログラミング学習、語学など）
- **Social（社会的）**: コミュニケーションタスク（友人との電話、会議参加など）

### XP計算システム
- **基本XP**: タスクタイプと難易度に基づく基本経験値
- **気分係数**: 1-5スケールの気分を0.8-1.2の係数に変換
- **ADHD支援係数**: 支援レベルとPomodoro使用に基づく1.0-1.3の係数
- **時間効率ボーナス**: 予定時間内完了での追加ボーナス
- **優先度ボーナス**: タスク優先度による係数調整

### ADHD支援機能
- **4段階の支援レベル**: None、Basic、Moderate、Intensive
- **Pomodoro統合**: セッション計画・実行管理
- **休憩リマインダー**: 自動休憩提案機能
- **集中音楽**: 集中力向上のための音楽機能
- **日次制限**: 1日最大16タスクの制限

### クリスタル属性システム統合
- **8つのクリスタル属性**: Self-Discipline、Empathy、Resilience、Curiosity、Communication、Creativity、Courage、Wisdom
- **自動推奨**: タスクタイプに基づく属性推奨
- **成長イベント**: タスク完了時のクリスタル成長

## APIエンドポイント

### タスク管理
- **POST /tasks/{uid}/create**: 新しいタスクを作成
- **GET /tasks/{uid}**: ユーザーのタスク一覧を取得
- **GET /tasks/{uid}/{task_id}**: 特定のタスクを取得
- **PUT /tasks/{uid}/{task_id}**: タスクを更新
- **DELETE /tasks/{uid}/{task_id}**: タスクを削除

### タスクライフサイクル
- **POST /tasks/{uid}/{task_id}/start**: タスクを開始
- **POST /tasks/{uid}/{task_id}/complete**: タスクを完了

### XPと推奨
- **POST /tasks/xp-preview**: タスク作成時のXPプレビュー
- **POST /tasks/recommendations**: タスクタイプと難易度の推奨

### 統計・分析
- **GET /tasks/{uid}/statistics**: タスク統計情報
- **GET /tasks/{uid}/daily-summary**: 日次タスクサマリー

## データモデル

### Task（タスク）
```python
class Task(BaseModel):
    task_id: str                    # タスクID
    uid: str                        # ユーザーID
    task_type: TaskType            # タスクタイプ
    title: str                     # タイトル
    description: str               # 説明
    difficulty: TaskDifficulty     # 難易度（1-5）
    priority: TaskPriority         # 優先度
    status: TaskStatus             # ステータス
    estimated_duration: int        # 予想所要時間（分）
    actual_duration: int           # 実際の所要時間（分）
    due_date: datetime             # 期限
    base_xp: int                   # 基本XP
    xp_earned: int                 # 獲得XP
    adhd_support_level: ADHDSupportLevel  # ADHD支援レベル
    pomodoro_sessions_planned: int        # 予定Pomodoroセッション数
    pomodoro_sessions_completed: int      # 完了Pomodoroセッション数
    primary_crystal_attribute: CrystalAttribute      # 主要クリスタル属性
    secondary_crystal_attributes: List[CrystalAttribute]  # 副次クリスタル属性
    tags: List[str]                # タグ
    is_recurring: bool             # 繰り返しタスク
    recurrence_pattern: str        # 繰り返しパターン
```

### XPCalculationResult（XP計算結果）
```python
class XPCalculationResult(BaseModel):
    base_xp: int                   # 基本XP
    mood_coefficient: float        # 気分係数
    adhd_assist_multiplier: float  # ADHD支援係数
    time_efficiency_bonus: float   # 時間効率ボーナス
    priority_bonus: float          # 優先度ボーナス
    final_xp: int                  # 最終XP
    breakdown: Dict[str, float]    # 詳細内訳
```

## 使用例

### ルーチンタスク作成
```python
task_request = {
    "task_type": "routine",
    "title": "朝の運動",
    "description": "毎朝30分の軽い運動を行う",
    "difficulty": 2,
    "priority": "high",
    "estimated_duration": 30,
    "adhd_support_level": "basic",
    "pomodoro_sessions_planned": 1,
    "break_reminders_enabled": True,
    "tags": ["健康", "習慣"],
    "is_recurring": True,
    "recurrence_pattern": "daily"
}

response = requests.post(f"/tasks/{user_id}/create", json=task_request)
```

### スキルアップタスク作成
```python
task_request = {
    "task_type": "skill_up",
    "title": "Python学習",
    "description": "Pythonの基礎を学習する",
    "difficulty": 3,
    "estimated_duration": 60,
    "adhd_support_level": "intensive",
    "pomodoro_sessions_planned": 2,
    "focus_music_enabled": True,
    "primary_crystal_attribute": "wisdom",
    "secondary_crystal_attributes": ["creativity"],
    "tags": ["学習", "プログラミング"]
}

response = requests.post(f"/tasks/{user_id}/create", json=task_request)
```

### タスク完了とXP獲得
```python
# タスク開始
start_response = requests.post(f"/tasks/{user_id}/{task_id}/start", json={})

# タスク完了
complete_request = {
    "mood_score": 4,
    "actual_duration": 55,
    "notes": "学習完了！理解が深まった",
    "pomodoro_sessions_completed": 2
}

response = requests.post(f"/tasks/{user_id}/{task_id}/complete", json=complete_request)
result = response.json()

print(f"獲得XP: {result['xp_earned']}")
print(f"XP詳細: {result['xp_calculation']}")
print(f"クリスタル成長: {result['crystal_growth_events']}")
```

### XPプレビュー
```python
preview_request = {
    "task_type": "skill_up",
    "difficulty": 4,
    "mood_score": 5,
    "adhd_support_level": "intensive"
}

response = requests.post("/tasks/xp-preview", json=preview_request)
estimated_xp = response.json()["estimated_xp"]
```

### タスク推奨
```python
recommendation_request = {
    "primary_goal": "プログラミングスキルを向上させたい",
    "user_experience_level": 3,
    "task_complexity": "moderate",
    "user_confidence": 4
}

response = requests.post("/tasks/recommendations", json=recommendation_request)
recommendations = response.json()

print(f"推奨タスクタイプ: {recommendations['recommended_task_type']}")
print(f"推奨難易度: {recommendations['recommended_difficulty']}")
print(f"推奨クリスタル: {recommendations['recommended_crystals']}")
```

## XP計算式

### 基本計算式
```
XP = base_xp × mood_coefficient × adhd_assist_multiplier × time_efficiency_bonus × priority_bonus
```

### 係数詳細
- **気分係数**: `0.8 + (mood_score - 1) × 0.1` (1-5スケール → 0.8-1.2)
- **ADHD支援係数**: 支援レベル(1.0-1.3) × Pomodoro完了率ボーナス(最大1.2)
- **時間効率ボーナス**: 予定時間内完了で最大1.3倍
- **優先度ボーナス**: Low(0.9), Medium(1.0), High(1.1), Urgent(1.2)

### タスクタイプ別基本XP
- **Routine**: 基本XP × 0.8（継続性重視）
- **One-Shot**: 基本XP × 1.0（標準）
- **Skill-Up**: 基本XP × 1.3（成長重視）
- **Social**: 基本XP × 1.2（社会性重視）

## ADHD支援機能

### 支援レベル
- **None**: 支援なし（係数1.0）
- **Basic**: 基本的な支援（係数1.1）
- **Moderate**: 中程度の支援（係数1.2）
- **Intensive**: 集中的な支援（係数1.3）

### Pomodoro統合
- セッション計画・実行管理
- 完了率に基づくボーナス（最大20%）
- 休憩リマインダー機能
- 60分連続作業時の自動休憩提案

### 日次制限
- 1日最大16タスクの制限（ADHD配慮）
- 制限超過時は429エラーを返却

## クリスタル属性マッピング

### タスクタイプ別推奨属性
- **Routine**: Self-Discipline, Resilience
- **One-Shot**: Courage, Curiosity  
- **Skill-Up**: Wisdom, Creativity
- **Social**: Empathy, Communication

### 成長イベント
- タスク完了時に主要・副次属性の成長イベントを生成
- ゲームエンジンとの連携でクリスタルゲージ更新

## 統計・分析機能

### タスク統計
- 期間別完了率
- タスクタイプ別統計
- 難易度別統計
- 総獲得XP
- 平均XP/タスク

### 日次サマリー
- 日別タスク完了状況
- 日別獲得XP
- タスクタイプ別完了数
- 残りタスク枠数

## エラーハンドリング

- **400 Bad Request**: 無効なリクエストデータ
- **404 Not Found**: タスクが見つからない
- **429 Too Many Requests**: 日次タスク制限超過
- **500 Internal Server Error**: システムエラー

## テスト

### 統合テスト
- **タスク管理API**: `test_task_management.py`
- **4種類のタスクタイプ**: 作成・更新・完了テスト
- **XP計算**: 各種係数の動作確認
- **ADHD支援機能**: 支援レベル・Pomodoro統合

### 実装検証
- **基本機能**: `simple_validation.py`
- **タスクライフサイクル**: 作成→開始→完了フロー
- **推奨システム**: タスクタイプ・難易度推奨
- **クリスタル統合**: 属性推奨・成長イベント

## 要件対応

### Requirement 5.1: Multi-Modal Task Management
✅ 4種類のタスクタイプ（Routine、One-Shot、Skill-Up、Social）実装
✅ XP計算式（difficulty × mood_coefficient × adhd_assist）実装
✅ Pomodoro統合とADHD支援係数実装

### Requirement 5.5: Story Integration
✅ real_task_idとhabit_tagによるストーリー連携
✅ クリスタル属性システム統合
✅ タスク完了とXP計算統合

## 使用技術

- **FastAPI**: REST API実装
- **Pydantic**: データバリデーション
- **Python Dataclasses**: データモデル
- **Datetime**: 時間管理
- **Enum**: 型安全な定数定義

## 次のステップ

1. **Firestore統合**: データ永続化
2. **ストーリーエンジン連携**: real_task_id/habit_tag統合
3. **Mandalaシステム連携**: セル連携機能
4. **通知システム**: 期限・リマインダー通知
5. **分析機能強化**: より詳細な統計・レポート