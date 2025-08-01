# 職業システムサービス

治療的ゲーミフィケーションアプリの職業システムを管理するサービスです。

## 概要

このサービスは以下の機能を提供します：

- **6つの基本職業**: 戦士、勇者、魔法使い、僧侶、賢者、忍者
- **3つの上級職業**: パラディン、大魔法使い、影の達人
- **職業固有スキルシステム**: 各職業に3つの固有スキル
- **能力値ボーナス**: 職業とレベルに応じた能力値向上
- **アンロック条件管理**: 上級職業の解放条件チェック

## 基本職業

### 戦士 (Warrior)
- **治療的焦点**: 習慣形成と自制心
- **主要属性**: Self-Discipline
- **能力値ボーナス**: 回復力+2, 集中力+1
- **固有スキル**:
  - 鉄の意志: 困難なタスクに対する集中力+20%
  - タスククラッシャー: ルーチンタスクのXP+15%
  - 締切の守護者: 締切前24時間の作業効率+30%

### 勇者 (Hero)
- **治療的焦点**: 社会復帰と勇気
- **主要属性**: Courage
- **能力値ボーナス**: やる気+2, 社会性+1
- **固有スキル**:
  - 恐怖征服者: 社会的タスクの不安軽減-25%
  - 社会の架け橋: 社会的タスクのXP+20%
  - 希望の使者: チーム内の他メンバーにやる気ボーナス+10%

### 魔法使い (Mage)
- **治療的焦点**: 創造性と問題解決
- **主要属性**: Creativity
- **能力値ボーナス**: 創造性+2, 知恵+1
- **固有スキル**:
  - アイデアスパーク: 創造的タスクの発想力+25%
  - 問題解決者: 複雑なタスクの理解力+20%
  - 革新の達人: 新しいアプローチでのXPボーナス+30%

### 僧侶 (Priest)
- **治療的焦点**: 共感力と癒し
- **主要属性**: Empathy
- **能力値ボーナス**: 社会性+2, 回復力+1
- **固有スキル**:
  - 感情の癒し: ストレス回復速度+30%
  - 共感力向上: 他者理解タスクの効果+25%
  - コミュニティの絆: グループ活動でのボーナスXP+20%

### 賢者 (Sage)
- **治療的焦点**: 学習と自己理解
- **主要属性**: Wisdom
- **能力値ボーナス**: 知恵+2, 集中力+1
- **固有スキル**:
  - 深い洞察: 学習タスクの理解度+30%
  - 学習加速器: スキルアップタスクのXP+25%
  - マインドフル認識: 自己理解タスクの効果+35%

### 忍者 (Ninja)
- **治療的焦点**: ストレス管理と適応力
- **主要属性**: Resilience
- **能力値ボーナス**: 回復力+2, やる気+1
- **固有スキル**:
  - ストレスの影: 高ストレス時の作業効率維持+20%
  - 適応の達人: 環境変化への対応力+25%
  - ステルス進歩: 小さな改善の積み重ね効果+30%

## 上級職業

### パラディン (Paladin)
- **アンロック条件**: 戦士レベル10 + 僧侶レベル5 + 社会的タスク50回完了
- **治療的焦点**: リーダーシップと他者支援
- **主要属性**: Courage + Empathy
- **能力値ボーナス**: 回復力+3, 社会性+2, やる気+1

### 大魔法使い (Archmage)
- **アンロック条件**: 魔法使いレベル15 + 知恵20 + 創造的タスク100回完了
- **治療的焦点**: 高度な問題解決と革新
- **主要属性**: Creativity + Wisdom
- **能力値ボーナス**: 創造性+4, 知恵+3

### 影の達人 (Shadow Master)
- **アンロック条件**: 忍者レベル12 + 回復力25 + ストレス克服30回
- **治療的焦点**: 極限適応とストレス克服
- **主要属性**: Resilience + Adaptation
- **能力値ボーナス**: 回復力+4, 集中力+2

## API使用例

```python
from main import create_job_manager, JobType

# JobManagerインスタンス作成
job_manager = create_job_manager()

# ユーザー初期化（戦士として開始）
user_data = job_manager.initialize_user_job("user123", JobType.WARRIOR)

# 職業情報取得
job_info = job_manager.get_user_job_info("user123")
print(f"現在の職業: {job_info['current_job']['name']}")
print(f"レベル: {job_info['current_job']['level']}")

# 経験値追加
leveled_up = job_manager.add_job_experience("user123", 150)
if leveled_up:
    print("レベルアップしました！")

# 職業変更（魔法使いに変更）
user_stats = {}  # 基本職業は条件なし
success = job_manager.change_job("user123", JobType.MAGE, user_stats)
if success:
    print("職業変更成功")

# 上級職業への変更（条件チェック付き）
advanced_stats = {
    "warrior": 10,
    "priest": 5,
    "social_tasks": 50
}
success = job_manager.change_job("user123", JobType.PALADIN, advanced_stats)
```

## データ構造

### UserJobData
```python
@dataclass
class UserJobData:
    uid: str                                    # ユーザーID
    current_job: JobType                        # 現在の職業
    job_level: int = 1                         # 職業レベル
    job_experience: int = 0                    # 職業経験値
    unlocked_jobs: List[JobType]               # アンロック済み職業
    job_change_history: List[Dict[str, Any]]   # 職業変更履歴
    last_job_change: Optional[datetime] = None # 最後の職業変更時刻
```

### Job
```python
@dataclass
class Job:
    job_type: JobType                          # 職業タイプ
    name: str                                  # 職業名
    focus_attribute: str                       # 主要な治療的焦点
    stat_bonuses: Dict[str, int]              # 能力値ボーナス
    skills: List[JobSkill]                    # 固有スキル
    therapeutic_focus: str                     # 治療的焦点の説明
    description: str                           # 職業説明
    is_advanced: bool = False                  # 上級職業フラグ
    unlock_requirements: Dict[str, Any]        # アンロック条件
```

## テスト実行

```bash
# 単体テスト実行
python -m pytest test_job_system.py -v

# 基本動作確認
python main.py
```

## 上級職業システム

### 詳細なアンロック条件

上級職業は複数の条件を同時に満たす必要があります：

```python
from advanced_job_system import create_advanced_job_manager

advanced_manager = create_advanced_job_manager()

# アンロック状況確認
user_stats = {
    "job_levels": {"warrior": 10, "priest": 5},
    "stats": {"wisdom": 20, "resilience": 25},
    "task_completions": {"social_tasks": 50, "creative_tasks": 100},
    "story_branches": {"helped_others_count": 10},
    "achievements": {"community_leader": True},
    "time_based": {"continuous_learning_days": 30}
}

unlock_status = advanced_manager.get_advanced_unlock_status("user123", user_stats)

# 上級職業への変更試行
change_result = advanced_manager.attempt_advanced_job_change("user123", JobType.PALADIN, user_stats)
if change_result["success"]:
    print("職業変更成功！")
    print(f"ストーリー: {change_result['story_content']['dialogue']}")
```

### ストーリー統合

上級職業への変更時には特別なストーリーコンテンツが生成されます：

- **職業覚醒ストーリー**: 新しい力の目覚めを描く
- **キャラクター成長アーク**: 治療的な成長の物語
- **特別選択肢**: 職業固有のストーリー分岐（最大3選択肢）
- **治療的メッセージ**: 現実世界への応用を促すメッセージ

### 実績システム

上級職業のアンロックには実績の獲得が必要：

- **コミュニティリーダー**: 他者支援と社会貢献
- **マスターイノベーター**: 創造的問題解決
- **ストレスマスター**: 困難克服と適応力

## 統合ポイント

このサービスは以下のサービスと連携します：

- **コアゲームエンジン**: XP計算とレベル管理
- **タスク管理**: タスク完了時の職業経験値付与
- **ストーリーエンジン**: 職業に応じたストーリー分岐とアンロック条件
- **RPG経済システム**: 職業固有装備とアイテム
- **実績システム**: 上級職業アンロック条件の追跡

## 治療的配慮

- 各職業は特定の治療的目標に焦点を当てている
- スキルは実世界での行動改善を促進する
- 職業変更により多様な成長パスを提供
- 上級職業は長期的な目標設定を支援
- アンロック条件は段階的な成長を促進
- ストーリー統合により意味のある変化体験を提供