# 治療的ゲーミフィケーションアプリ設計文書

## 概要

本システムは、ADHD、不登校、若年NEET層を対象とした治療グレードのゲーミフィケーションアプリケーションです。リアルタスク完了とストーリー進行を完全同期させる「パラレルプロット構造」により、キャラクター「ユウ」と利用者自身の両方を同時にレベルアップさせる革新的なシステムです。

システムは5段階の状態機械（無関心→興味→行動→継続→習慣化）に基づいて設計され、JIS X 8341-3 AAA及びWCAG 2.2 AA準拠のアクセシビリティを提供します。治療安全性を最優先とし、CBTベースの認知再構成とACT療法統合により、心理的に安全な環境での自己効力感再構築を支援します。

**設計原則:**
- **治療グレード品質**: 98% F1スコアの安全性検出と心理的配慮
- **ADHD最適化**: 認知負荷軽減とワンスクリーン・ワンアクション設計
- **モバイルファースト**: スマートフォン・タブレット最適化UI/UX
- **アクセシビリティファースト**: JIS X 8341-3 AAA準拠の包括的設計
- **パフォーマンス重視**: 1.2秒P95レイテンシと20,000同時ユーザー対応

システムは5段階の状態機械（無関心→興味→行動→継続→習慣化）に基づいて設計され、JIS X 8341-3 AAA及びWCAG 2.2 AA準拠のアクセシビリティを提供します。治療安全性を最優先とし、CBTベースの認知再構成とACT療法統合により、心理的に安全な環境での自己効力感再構築を支援します。

**設計原則:**
- **治療グレード品質**: 98% F1スコアの安全性検出と心理的配慮
- **ADHD最適化**: 認知負荷軽減とワンスクリーン・ワンアクション設計
- **アクセシビリティファースト**: JIS X 8341-3 AAA準拠の包括的設計
- **パフォーマンス重視**: 1.2秒P95レイテンシと20,000同時ユーザー対応

## アーキテクチャ

### システム全体構成

```mermaid
graph TB
    subgraph "フロントエンド"
        LINE[LINE Bot Interface]
        WEB[Web Portal]
        GUARD[Guardian Portal]
    end
    
    subgraph "コアサービス"
        AUTH[認証サービス]
        GAME[コアゲームエンジン]
        STORY[AIストーリーエンジン]
        TASK[タスク管理]
        MOOD[気分追跡]
    end
    
    subgraph "専門サービス"
        ADHD[ADHD支援]
        SAFETY[治療安全性]
        MANDALA[Mandalaシステム]
    end
    
    subgraph "データ層"
        FIRESTORE[(Firestore)]
        STORAGE[(Cloud Storage)]
    end
    
    LINE --> AUTH
    WEB --> AUTH
    GUARD --> AUTH
    
    AUTH --> GAME
    GAME --> STORY
    GAME --> TASK
    GAME --> MOOD
    GAME --> ADHD
    GAME --> SAFETY
    GAME --> MANDALA
    
    GAME --> FIRESTORE
    STORY --> FIRESTORE
    TASK --> FIRESTORE
</mermaid>

### マイクロサービス構成

- **認証サービス** (`services/auth/`): RBAC、SAML、Magic Link認証
- **コアゲームエンジン** (`services/core-game/`): XP、レベル、共鳴イベント管理
- **AIストーリーエンジン** (`services/ai-story/`): GPT-4o駆動の動的ストーリー生成
- **タスク管理** (`services/task-mgmt/`): 4種類のタスクタイプとPomodoro統合
- **気分追跡** (`services/mood-tracking/`): 日次気分ログとXP係数調整
- **ADHD支援** (`services/adhd-support/`): 認知負荷軽減とアシスト機能
- **治療安全性** (`services/therapeutic-safety/`): コンテンツモデレーションとCBT介入
- **LINE Bot** (`services/line-bot/`): 主要インターフェース
- **ストーリーDAG** (`services/story-dag/`): ストーリー構造管理

## コンポーネントと インターフェース

### コアゲームエンジン

#### XPシステム設計

```python
# XP計算式
XP = Σ(difficulty × mood_coefficient × adhd_assist)

# 係数範囲
mood_coefficient: 0.8-1.2  # 気分ログ(1-5)に基づく
adhd_assist: 1.0-1.3       # Pomodoro/リマインダー使用頻度
difficulty: 1-5            # タスク難易度
```

#### レベル進行システム

```python
class LevelSystem:
    def calculate_level(self, total_xp: int) -> int:
        # 指数関数的レベル進行
        return int(math.log2(total_xp / 100 + 1))
    
    def xp_for_next_level(self, current_level: int) -> int:
        return (2 ** (current_level + 1) - 1) * 100
    
    def check_resonance_event(self, yu_level: int, player_level: int) -> bool:
        # レベル差5以上で共鳴イベント発生
        return abs(yu_level - player_level) >= 5
```

#### 8属性クリスタルシステム

```python
CRYSTAL_ATTRIBUTES = [
    "Self-Discipline",    # 自律性
    "Empathy",           # 共感力
    "Resilience",        # 回復力
    "Curiosity",         # 好奇心
    "Communication",     # コミュニケーション
    "Creativity",        # 創造性
    "Courage",           # 勇気
    "Wisdom"             # 知恵
]

class CrystalGauge:
    def __init__(self):
        self.gauges = {attr: 0 for attr in CRYSTAL_ATTRIBUTES}
        self.max_value = 100
    
    def add_progress(self, attribute: str, points: int):
        self.gauges[attribute] = min(self.max_value, 
                                   self.gauges[attribute] + points)
    
    def is_chapter_unlocked(self, attribute: str) -> bool:
        return self.gauges[attribute] >= 100
```

### Mandalaシステム

#### 9x9グリッド構造

```python
class MandalaGrid:
    def __init__(self):
        self.grid = [[None for _ in range(9)] for _ in range(9)]
        self.center_values = self._initialize_core_values()
        self.memory_cells = {}  # 81個のクエスト
    
    def _initialize_core_values(self):
        # 中央に固定価値観（ACT療法統合）
        return {
            (4, 4): "Core Self",  # 中心
            (3, 4): "Compassion",
            (5, 4): "Growth",
            (4, 3): "Authenticity",
            (4, 5): "Connection"
        }
    
    def unlock_cell(self, x: int, y: int, quest_data: dict):
        if self._can_unlock(x, y):
            self.grid[x][y] = quest_data
            return True
        return False
    
    def get_api_response(self, uid: str) -> dict:
        return {
            "uid": uid,
            "grid": self._serialize_grid(),
            "unlocked_count": self._count_unlocked(),
            "total_cells": 81
        }
```

### AIストーリーエンジン

#### ストーリーDAG構造

```python
class StoryDAG:
    def __init__(self):
        self.chapters = {}  # CHAPTER -> NODE -> EDGE
        self.current_state = {}
    
    def generate_story_content(self, user_context: dict) -> dict:
        prompt = self._build_prompt(user_context)
        
        # GPT-4o呼び出し（3.5秒以内）
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=3.5
        )
        
        return self._validate_story_schema(response.choices[0].message.content)
    
    def _build_prompt(self, context: dict) -> str:
        return f"""
        治療的ストーリー生成:
        - ユーザー状態: {context['mood']}/5
        - 完了タスク: {context['completed_tasks']}
        - 現在章: {context['current_chapter']}
        
        以下のJSON形式で応答:
        {{
            "story_text": "ストーリー内容",
            "choices": [
                {{
                    "text": "選択肢テキスト",
                    "real_task_id": "task_123",
                    "xp_reward": 50
                }}
            ],
            "therapeutic_elements": ["CBT", "ACT"]
        }}
        """
```

#### 治療安全性チェック

```python
class TherapeuticSafety:
    def __init__(self):
        self.moderation_client = OpenAI()
        self.custom_filters = self._load_custom_filters()
    
    def validate_content(self, content: str) -> dict:
        # OpenAI Moderation
        moderation = self.moderation_client.moderations.create(input=content)
        
        # カスタムフィルター（自傷リスク検出）
        custom_score = self._check_self_harm_triggers(content)
        
        return {
            "safe": not moderation.results[0].flagged and custom_score < 0.02,
            "confidence": custom_score,
            "target_f1": 0.98  # 98% F1スコア目標
        }
    
    def generate_cbt_intervention(self, negative_pattern: str) -> str:
        # CBTベースの認知再構成ダイアログ
        return self._create_story_break_dialog(negative_pattern)
```

### RPG経済システムとアイテム管理

#### コイン経済システム

```python
class CoinEconomy:
    def __init__(self):
        self.base_coin_rates = {
            "task_completion": {"routine": 10, "one_shot": 15, "skill_up": 20, "social": 25},
            "demon_defeat": {"common": 50, "rare": 100, "epic": 200, "legendary": 500},
            "daily_bonus": 30,
            "streak_bonus": {"7_days": 100, "30_days": 500, "100_days": 2000}
        }
    
    def calculate_coin_reward(self, action_type: str, difficulty: int, 
                            performance_multiplier: float = 1.0) -> int:
        base_coins = self.base_coin_rates.get(action_type, {}).get("routine", 10)
        return int(base_coins * difficulty * performance_multiplier)
    
    def apply_inflation_control(self, user_total_coins: int) -> float:
        # 経済バランス維持のためのインフレ制御
        if user_total_coins > 10000:
            return 0.8  # 20%減少
        elif user_total_coins > 5000:
            return 0.9  # 10%減少
        return 1.0
```

#### ガチャシステム設計

```python
class GachaSystem:
    def __init__(self):
        self.rarity_rates = {
            "common": 0.60,     # 60%
            "uncommon": 0.25,   # 25%
            "rare": 0.10,       # 10%
            "epic": 0.04,       # 4%
            "legendary": 0.01   # 1%
        }
        self.gacha_costs = {
            "single": 100,
            "ten_pull": 900,    # 10%割引
            "premium": 300      # レア確率2倍
        }
    
    def perform_gacha(self, gacha_type: str, user_coins: int) -> dict:
        cost = self.gacha_costs[gacha_type]
        if user_coins < cost:
            return {"success": False, "error": "insufficient_coins"}
        
        items = []
        pulls = 10 if gacha_type == "ten_pull" else 1
        
        for _ in range(pulls):
            rarity = self._determine_rarity(gacha_type == "premium")
            item = self._generate_item(rarity)
            items.append(item)
        
        return {
            "success": True,
            "items": items,
            "coins_spent": cost,
            "guaranteed_rare": gacha_type == "ten_pull" and not any(i["rarity"] in ["rare", "epic", "legendary"] for i in items)
        }
```

#### 装備システム

```python
class EquipmentSystem:
    def __init__(self):
        self.equipment_slots = {
            "weapon": None,
            "armor": None,
            "accessory": None,
            "consumable_1": None,
            "consumable_2": None,
            "consumable_3": None
        }
        self.stat_bonuses = {
            "focus": 0,      # タスク集中力向上
            "resilience": 0, # ストレス耐性
            "motivation": 0, # やる気持続
            "social": 0,     # 社会性向上
            "creativity": 0, # 創造性向上
            "wisdom": 0      # 学習効率
        }
    
    def equip_item(self, item: dict, slot: str) -> bool:
        if slot not in self.equipment_slots:
            return False
        
        # 既存装備の効果を削除
        if self.equipment_slots[slot]:
            self._remove_stat_bonuses(self.equipment_slots[slot])
        
        # 新装備の効果を適用
        self.equipment_slots[slot] = item
        self._apply_stat_bonuses(item)
        return True
    
    def calculate_task_completion_bonus(self) -> float:
        # 装備による作業効率ボーナス
        focus_bonus = self.stat_bonuses["focus"] * 0.02  # 2%/point
        motivation_bonus = self.stat_bonuses["motivation"] * 0.015  # 1.5%/point
        return min(0.5, focus_bonus + motivation_bonus)  # 最大50%ボーナス
```

### 職業システムと成長パス

#### 基本職業システム

```python
class JobSystem:
    def __init__(self):
        self.base_jobs = {
            "warrior": {
                "name": "戦士",
                "focus": "Self-Discipline",
                "bonuses": {"resilience": 2, "focus": 1},
                "skills": ["iron_will", "task_crusher", "deadline_guardian"],
                "therapeutic_focus": "習慣形成と自制心"
            },
            "hero": {
                "name": "勇者",
                "focus": "Courage",
                "bonuses": {"motivation": 2, "social": 1},
                "skills": ["fear_conqueror", "social_bridge", "hope_bringer"],
                "therapeutic_focus": "社会復帰と勇気"
            },
            "mage": {
                "name": "魔法使い",
                "focus": "Creativity",
                "bonuses": {"creativity": 2, "wisdom": 1},
                "skills": ["idea_spark", "problem_solver", "innovation_master"],
                "therapeutic_focus": "創造性と問題解決"
            },
            "priest": {
                "name": "僧侶",
                "focus": "Empathy",
                "bonuses": {"social": 2, "resilience": 1},
                "skills": ["emotional_heal", "empathy_boost", "community_bond"],
                "therapeutic_focus": "共感力と癒し"
            },
            "sage": {
                "name": "賢者",
                "focus": "Wisdom",
                "bonuses": {"wisdom": 2, "focus": 1},
                "skills": ["deep_insight", "learning_accelerator", "mindful_awareness"],
                "therapeutic_focus": "学習と自己理解"
            },
            "ninja": {
                "name": "忍者",
                "focus": "Resilience",
                "bonuses": {"resilience": 2, "motivation": 1},
                "skills": ["stress_shadow", "adaptation_master", "stealth_progress"],
                "therapeutic_focus": "ストレス管理と適応力"
            }
        }
        
        self.advanced_jobs = {
            "paladin": {
                "requirements": {"warrior": 10, "priest": 5, "social_tasks": 50},
                "bonuses": {"resilience": 3, "social": 2, "motivation": 1}
            },
            "archmage": {
                "requirements": {"mage": 15, "wisdom": 20, "creative_tasks": 100},
                "bonuses": {"creativity": 4, "wisdom": 3}
            },
            "shadow_master": {
                "requirements": {"ninja": 12, "resilience": 25, "stress_overcome": 30},
                "bonuses": {"resilience": 4, "focus": 2}
            }
        }
    
    def check_job_unlock(self, user_stats: dict, target_job: str) -> bool:
        requirements = self.advanced_jobs.get(target_job, {}).get("requirements", {})
        for req_key, req_value in requirements.items():
            if user_stats.get(req_key, 0) < req_value:
                return False
        return True
```

### 内なる魔物バトルシステム

#### バトルエンジン

```python
class InnerDemonBattle:
    def __init__(self):
        self.demon_types = {
            "procrastination_dragon": {
                "name": "先延ばしドラゴン",
                "hp": 100,
                "weakness": ["routine_tasks", "pomodoro_usage"],
                "rewards": {"coins": 150, "items": ["focus_potion", "time_crystal"]},
                "therapeutic_message": "小さな一歩から始めることの大切さ"
            },
            "anxiety_shadow": {
                "name": "不安の影",
                "hp": 80,
                "weakness": ["breathing_exercise", "positive_affirmation"],
                "rewards": {"coins": 120, "items": ["calm_amulet", "courage_ring"]},
                "therapeutic_message": "不安は成長のサイン"
            },
            "depression_void": {
                "name": "憂鬱の虚無",
                "hp": 150,
                "weakness": ["social_connection", "creative_expression"],
                "rewards": {"coins": 200, "items": ["hope_crystal", "energy_elixir"]},
                "therapeutic_message": "つながりが闇を照らす"
            },
            "social_fear_goblin": {
                "name": "社会恐怖ゴブリン",
                "hp": 60,
                "weakness": ["small_social_tasks", "communication_practice"],
                "rewards": {"coins": 100, "items": ["confidence_badge", "social_key"]},
                "therapeutic_message": "小さな勇気が大きな変化を生む"
            }
        }
    
    def initiate_battle(self, demon_type: str, user_recent_actions: List[str]) -> dict:
        demon = self.demon_types[demon_type].copy()
        
        # ユーザーの最近の行動に基づくダメージ計算
        damage = 0
        for action in user_recent_actions:
            if action in demon["weakness"]:
                damage += 25
        
        demon["hp"] -= damage
        
        if demon["hp"] <= 0:
            return {
                "result": "victory",
                "rewards": demon["rewards"],
                "message": demon["therapeutic_message"],
                "reflection_prompt": self._generate_cbt_reflection(demon_type)
            }
        else:
            return {
                "result": "ongoing",
                "demon_hp": demon["hp"],
                "suggested_actions": demon["weakness"],
                "encouragement": "この魔物を倒すには、日々の小さな行動が武器になります"
            }
```

### 日次振り返りとグルノートシステム

#### グルノート構造化振り返り

```python
class GrowthNoteSystem:
    def __init__(self):
        self.reflection_prompts = {
            "current_problems": [
                "現実世界で今困っていることは何ですか？",
                "今日直面した課題や悩みはありますか？",
                "解決したいと思っている問題は何ですか？"
            ],
            "ideal_world": [
                "あなたにとって理想的な世界とはどのような世界ですか？",
                "もし全てが思い通りになるとしたら、どんな状況になっていたいですか？",
                "理想の自分や環境について教えてください"
            ],
            "ideal_emotions": [
                "理想的な世界に住むあなたはどんな感情を感じていますか？",
                "その理想の状況で、あなたはどんな気持ちになっていますか？",
                "理想が実現した時の感情を具体的に想像してみてください"
            ],
            "tomorrow_actions": [
                "明日から何ができますか？",
                "理想に近づくために明日できる小さな一歩は何ですか？",
                "今日の振り返りを踏まえて、明日取り組みたいことは？"
            ]
        }
        self.reflection_xp_base = 25
    
    def generate_reflection_prompt(self, user_context: dict) -> dict:
        # ユーザーの状態に基づいてプロンプトをカスタマイズ
        mood = user_context.get("mood", 3)
        completed_tasks = user_context.get("completed_tasks", 0)
        
        return {
            "current_problems_prompt": self._select_contextual_prompt("current_problems", mood, completed_tasks),
            "ideal_world_prompt": self._select_contextual_prompt("ideal_world", mood, completed_tasks),
            "ideal_emotions_prompt": self._select_contextual_prompt("ideal_emotions", mood, completed_tasks),
            "tomorrow_actions_prompt": self._select_contextual_prompt("tomorrow_actions", mood, completed_tasks),
            "estimated_time": "10-15分",
            "xp_reward": self.reflection_xp_base
        }
    
    def process_reflection(self, reflection_data: dict) -> dict:
        # 振り返り内容の分析と次回ストーリー生成への活用
        current_problems = reflection_data.get("current_problems", "")
        ideal_world = reflection_data.get("ideal_world", "")
        ideal_emotions = reflection_data.get("ideal_emotions", "")
        tomorrow_actions = reflection_data.get("tomorrow_actions", "")
        
        # 感情分析とキーワード抽出
        emotional_tone = self._analyze_emotional_tone(ideal_emotions)
        problem_themes = self._extract_problem_themes(current_problems)
        action_orientation = self._analyze_action_orientation(tomorrow_actions)
        
        return {
            "reflection_completed": True,
            "emotional_tone": emotional_tone,
            "problem_themes": problem_themes,
            "action_orientation": action_orientation,
            "xp_earned": self.reflection_xp_base,
            "story_personalization_data": {
                "current_challenges": problem_themes,
                "ideal_vision": self._extract_key_themes(ideal_world),
                "emotional_state": emotional_tone,
                "action_readiness": action_orientation
            }
        }
    
    def check_reflection_streak(self, user_id: str) -> dict:
        # 振り返り継続状況の確認
        streak_data = self._get_reflection_history(user_id)
        
        return {
            "current_streak": streak_data["consecutive_days"],
            "total_reflections": streak_data["total_count"],
            "missed_days": streak_data["missed_in_last_week"],
            "needs_reminder": streak_data["missed_in_last_week"] >= 2
        }
```

#### LINE Bot振り返りUI

```python
class ReflectionLINEInterface:
    def create_reflection_prompt_message(self, prompts: dict) -> dict:
        """22:00の振り返りプロンプトメッセージ"""
        return {
            "type": "flex",
            "altText": "今日の振り返りタイム🌙",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "今日の振り返りタイム",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59"
                        },
                        {
                            "type": "text",
                            "text": "グルノート形式で今日を振り返りましょう",
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_reflection_section("😟 ①現実世界で困っていること", prompts["current_problems_prompt"]),
                        self._create_reflection_section("✨ ②理想的な世界とは", prompts["ideal_world_prompt"]),
                        self._create_reflection_section("😊 ③理想的な世界に住むあなたの感情は？", prompts["ideal_emotions_prompt"]),
                        self._create_reflection_section("🚀 ④明日から何が出来る？", prompts["tomorrow_actions_prompt"])
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "グルノートを始める (+25 XP)",
                                "uri": "line://app/growth-note-form"
                            }
                        }
                    ]
                }
            }
        }
    
    def create_reflection_reminder(self, missed_days: int) -> dict:
        """2日連続スキップ時のリマインダー"""
        encouragement_messages = [
            "グルノートは自分の成長を見つめる大切な時間です",
            "現実と理想のギャップを埋める第一歩は振り返りから始まります",
            "今日の自分と向き合ってみませんか？"
        ]
        
        return {
            "type": "text",
            "text": f"🌟 {random.choice(encouragement_messages)}\n\nグルノートを{missed_days}日お休みしていますね。無理をする必要はありませんが、短時間でも自分の現実と理想について考えてみませんか？",
            "quickReply": {
                "items": [
                    {
                        "type": "action",
                        "action": {
                            "type": "message",
                            "label": "今からグルノート",
                            "text": "グルノートを始める"
                        }
                    },
                    {
                        "type": "action",
                        "action": {
                            "type": "message",
                            "label": "明日にする",
                            "text": "明日グルノートする"
                        }
                    }
                ]
            }
        }
    
    def create_growth_note_form(self) -> dict:
        """グルノート入力フォーム"""
        return {
            "type": "flex",
            "altText": "グルノート入力フォーム",
            "contents": {
                "type": "carousel",
                "contents": [
                    self._create_form_bubble("①現実世界で困っていること", "current_problems", "😟"),
                    self._create_form_bubble("②理想的な世界とは", "ideal_world", "✨"),
                    self._create_form_bubble("③理想的な世界に住むあなたの感情は？", "ideal_emotions", "😊"),
                    self._create_form_bubble("④明日から何が出来る？", "tomorrow_actions", "🚀")
                ]
            }
        }
    
    def _create_form_bubble(self, title: str, field_name: str, emoji: str) -> dict:
        """各グルノートカテゴリの入力バブル"""
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{emoji} {title}",
                        "weight": "bold",
                        "size": "sm",
                        "wrap": True
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "入力する",
                            "uri": f"line://app/growth-note-input?field={field_name}"
                        }
                    }
                ]
            }
        }
```

### ユーザー状態管理システム

#### 5段階状態機械

```python
class UserStateEngine:
    def __init__(self):
        self.states = {
            "APATHY": 0,      # 無関心
            "INTEREST": 1,    # 興味
            "ACTION": 2,      # 行動
            "CONTINUATION": 3, # 継続
            "HABITUATION": 4  # 習慣化
        }
        self.transition_thresholds = {
            "APATHY_TO_INTEREST": {"login_days": 3, "story_engagement": 0.2},
            "INTEREST_TO_ACTION": {"tasks_completed": 5, "xp_earned": 100},
            "ACTION_TO_CONTINUATION": {"consecutive_days": 7, "task_variety": 3},
            "CONTINUATION_TO_HABITUATION": {"streak_days": 21, "self_efficacy": 0.8}
        }
    
    def evaluate_state_transition(self, user_metrics: dict) -> str:
        current_state = user_metrics.get("current_state", "APATHY")
        
        # 状態遷移ロジック
        if current_state == "APATHY" and self._check_interest_criteria(user_metrics):
            return "INTEREST"
        elif current_state == "INTEREST" and self._check_action_criteria(user_metrics):
            return "ACTION"
        # ... 他の遷移条件
        
        return current_state
    
    def get_therapeutic_interventions(self, state: str) -> List[str]:
        interventions = {
            "APATHY": ["curiosity_sparking", "low_commitment_tasks"],
            "INTEREST": ["goal_setting", "achievement_visualization"],
            "ACTION": ["habit_stacking", "progress_tracking"],
            "CONTINUATION": ["challenge_scaling", "social_connection"],
            "HABITUATION": ["mastery_focus", "mentoring_others"]
        }
        return interventions.get(state, [])
```

### タスク管理システム

#### 4種類のタスクタイプ

```python
class TaskType(Enum):
    ROUTINE = "routine"      # 日常習慣
    ONE_SHOT = "one_shot"    # 単発タスク
    SKILL_UP = "skill_up"    # スキル向上
    SOCIAL = "social"        # 社会的活動

class Task:
    def __init__(self, task_type: TaskType, difficulty: int, 
                 description: str, habit_tag: str = None):
        self.type = task_type
        self.difficulty = difficulty  # 1-5
        self.description = description
        self.habit_tag = habit_tag
        self.completed = False
        self.completion_time = None
    
    def calculate_xp(self, mood_coefficient: float, 
                    adhd_assist: float) -> int:
        base_xp = self.difficulty * 10
        return int(base_xp * mood_coefficient * adhd_assist)
```

#### Pomodoro統合

```python
class PomodoroIntegration:
    def __init__(self):
        self.session_count = 0
        self.break_suggestions = []
    
    def start_session(self, duration: int = 25):
        # 25分作業セッション開始
        self.session_count += 1
        
    def suggest_break(self, continuous_minutes: int) -> dict:
        if continuous_minutes >= 60:
            return {
                "type": "mandatory",
                "message": "「母の心配」ナラティブ",
                "refuse_count": self._get_refuse_count()
            }
        return None
    
    def get_adhd_assist_multiplier(self) -> float:
        # 使用頻度に基づくアシスト係数
        usage_rate = self.session_count / 30  # 月間使用率
        return min(1.3, 1.0 + (usage_rate * 0.3))
```

## データモデル

### ユーザープロファイル

```python
@dataclass
class UserProfile:
    uid: str
    yu_level: int
    player_level: int
    total_xp: int
    crystal_gauges: Dict[str, int]
    current_chapter: str
    daily_task_limit: int = 16  # ADHD配慮
    care_points: int = 0
    guardian_permissions: List[str] = None
```

### ストーリー状態

```python
@dataclass
class StoryState:
    uid: str
    current_chapter: str
    current_node: str
    available_edges: List[str]
    story_history: List[dict]
    last_generation_time: datetime
```

### タスク記録

```python
@dataclass
class TaskRecord:
    task_id: str
    uid: str
    task_type: TaskType
    difficulty: int
    description: str
    completed: bool
    completion_time: Optional[datetime]
    xp_earned: int
    mood_at_completion: int
    linked_story_edge: Optional[str]
```

## エラーハンドリング

### 段階的エラー処理

1. **バリデーションエラー**: 入力データの検証
2. **ビジネスロジックエラー**: ゲームルール違反
3. **外部サービスエラー**: OpenAI API、Firestore接続
4. **システムエラー**: 予期しない例外

```python
class GameEngineError(Exception):
    def __init__(self, message: str, error_code: str, 
                 recovery_action: str = None):
        self.message = message
        self.error_code = error_code
        self.recovery_action = recovery_action
        super().__init__(message)

class ErrorHandler:
    def handle_xp_calculation_error(self, error: Exception) -> dict:
        return {
            "success": False,
            "error_code": "XP_CALC_FAILED",
            "message": "XP計算に失敗しました",
            "recovery_action": "デフォルト値を使用"
        }
```

## テスト戦略

### 単体テスト

- XP計算ロジックの正確性
- レベル進行アルゴリズム
- 共鳴イベント発生条件
- クリスタルゲージ進行

### 統合テスト

- ストーリー生成とタスク連携
- Mandalaシステムとゲームエンジン連携
- 治療安全性チェック統合

### パフォーマンステスト

- AI応答時間（3.5秒以内）
- 同時ユーザー数（20,000人）
- API応答時間（1.2秒以内）

### 治療効果テスト

- CBT介入の適切性
- 自傷リスク検出精度（F1スコア98%）
- ADHD配慮機能の有効性

```python
class TestSuite:
    def test_xp_calculation(self):
        # XP計算の正確性テスト
        task = Task(TaskType.ROUTINE, difficulty=3, description="朝の運動")
        xp = task.calculate_xp(mood_coefficient=1.1, adhd_assist=1.2)
        assert xp == int(30 * 1.1 * 1.2)  # 39 XP
    
    def test_resonance_event(self):
        # 共鳴イベント発生テスト
        level_system = LevelSystem()
        assert level_system.check_resonance_event(yu_level=10, player_level=5)
        assert not level_system.check_resonance_event(yu_level=10, player_level=8)
    
    def test_therapeutic_safety(self):
        # 治療安全性テスト
        safety = TherapeuticSafety()
        result = safety.validate_content("ポジティブなストーリー内容")
        assert result["safe"] == True
        assert result["confidence"] < 0.02
```

## モバイルファーストUI/UX設計

### レスポンシブデザイン戦略

#### 画面サイズ対応

```css
/* モバイルファースト CSS設計 */
.mobile-container {
  /* 基本: 320px-480px (スマートフォン縦) */
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: 16px;
}

@media (min-width: 481px) and (max-width: 768px) {
  /* タブレット縦: 481px-768px */
  .mobile-container {
    max-width: 768px;
    padding: 24px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  /* タブレット横: 769px-1024px */
  .mobile-container {
    max-width: 1024px;
    padding: 32px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
}
```

#### タッチフレンドリーUI設計

```python
class TouchUIConfig:
    """タッチ操作最適化設定"""
    
    # タッチターゲットサイズ（Apple HIG & Material Design準拠）
    MIN_TOUCH_TARGET = 44  # px
    RECOMMENDED_TOUCH_TARGET = 48  # px
    
    # ジェスチャー設定
    SWIPE_THRESHOLD = 50  # px
    TAP_TIMEOUT = 300  # ms
    LONG_PRESS_DURATION = 500  # ms
    
    # ADHD配慮のタッチ設定
    ACCIDENTAL_TOUCH_PREVENTION = True
    DOUBLE_TAP_CONFIRMATION = True  # 重要なアクション用
    
    @staticmethod
    def get_touch_styles() -> dict:
        return {
            "button": {
                "min-height": "48px",
                "min-width": "48px",
                "padding": "12px 16px",
                "margin": "8px",
                "border-radius": "8px",
                "font-size": "16px",  # iOS zoom防止
                "line-height": "1.5"
            },
            "input": {
                "min-height": "44px",
                "padding": "12px",
                "font-size": "16px",  # iOS zoom防止
                "border-radius": "8px"
            }
        }
```

### Mandalaシステムのモバイル最適化

#### 3x3グリッド表示の適応設計

```python
class MobileMandalaRenderer:
    """モバイル向けMandala表示システム"""
    
    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self.grid_size = self._calculate_optimal_grid_size()
        self.zoom_enabled = screen_width < 480
    
    def _calculate_optimal_grid_size(self) -> int:
        """画面サイズに基づく最適グリッドサイズ計算"""
        if self.screen_width < 360:
            return 90  # 小型スマートフォン
        elif self.screen_width < 480:
            return 110  # 標準スマートフォン
        elif self.screen_width < 768:
            return 140  # 大型スマートフォン
        else:
            return 180  # タブレット
    
    def render_mandala_grid(self, mandala_data: dict) -> dict:
        """モバイル最適化されたMandalaグリッド描画"""
        return {
            "grid_config": {
                "cell_size": self.grid_size,
                "gap": 4,
                "total_width": (self.grid_size + 4) * 3 - 4,
                "touch_padding": 8
            },
            "interaction": {
                "zoom_enabled": self.zoom_enabled,
                "swipe_navigation": True,
                "long_press_info": True,
                "haptic_feedback": True
            },
            "accessibility": {
                "voice_over_labels": True,
                "high_contrast_mode": True,
                "large_text_support": True
            }
        }
    
    def handle_touch_interaction(self, touch_event: dict) -> dict:
        """タッチイベント処理"""
        if touch_event["type"] == "tap":
            return self._handle_cell_tap(touch_event)
        elif touch_event["type"] == "long_press":
            return self._show_cell_info(touch_event)
        elif touch_event["type"] == "swipe":
            return self._handle_swipe_navigation(touch_event)
```

### LINE Bot モバイル最適化

#### リッチメニューとカルーセル設計

```python
class MobileLINEBotUI:
    """LINE Bot モバイル最適化UI"""
    
    def create_morning_mandala_carousel(self, tasks: List[dict]) -> dict:
        """朝のMandala形式タスク表示（3x3グリッド）"""
        return {
            "type": "flex",
            "altText": "今日のハートクリスタルタスク",
            "contents": {
                "type": "carousel",
                "contents": self._create_mandala_bubbles(tasks)
            }
        }
    
    def _create_mandala_bubbles(self, tasks: List[dict]) -> List[dict]:
        """3x3 Mandalaを3つのバブルに分割"""
        bubbles = []
        
        # 各バブルに3x1のグリッドを配置
        for i in range(3):
            bubble = {
                "type": "bubble",
                "size": "kilo",  # コンパクトサイズ
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": []
                }
            }
            
            # 3つのタスクを縦に配置
            for j in range(3):
                task_index = i * 3 + j
                if task_index < len(tasks):
                    task_button = self._create_task_button(tasks[task_index])
                    bubble["body"]["contents"].append(task_button)
            
            bubbles.append(bubble)
        
        return bubbles
    
    def _create_task_button(self, task: dict) -> dict:
        """タッチフレンドリーなタスクボタン"""
        return {
            "type": "button",
            "style": "primary",
            "height": "sm",
            "action": {
                "type": "postback",
                "label": f"✓ {task['title'][:10]}...",
                "data": f"complete_task_{task['id']}"
            }
        }
```

### パフォーマンス最適化

#### プログレッシブローディング

```python
class MobilePerformanceOptimizer:
    """モバイル向けパフォーマンス最適化"""
    
    def __init__(self):
        self.skeleton_screens = True
        self.lazy_loading = True
        self.image_optimization = True
    
    def create_skeleton_screen(self, component_type: str) -> dict:
        """スケルトンスクリーン生成"""
        skeletons = {
            "mandala_grid": {
                "type": "grid",
                "rows": 3,
                "cols": 3,
                "cell_height": "60px",
                "animation": "pulse"
            },
            "story_content": {
                "type": "text_blocks",
                "lines": [
                    {"width": "100%", "height": "20px"},
                    {"width": "80%", "height": "20px"},
                    {"width": "90%", "height": "20px"}
                ],
                "animation": "shimmer"
            },
            "task_list": {
                "type": "list_items",
                "count": 5,
                "item_height": "48px",
                "animation": "wave"
            }
        }
        return skeletons.get(component_type, {})
    
    def optimize_images(self, image_config: dict) -> dict:
        """画像最適化設定"""
        return {
            "formats": ["webp", "avif", "jpg"],
            "sizes": {
                "mobile": "320w",
                "tablet": "768w",
                "desktop": "1024w"
            },
            "lazy_loading": True,
            "placeholder": "blur",
            "quality": 85
        }
    
    def get_3g_optimization_config(self) -> dict:
        """3G回線対応最適化"""
        return {
            "bundle_splitting": True,
            "code_splitting": True,
            "resource_hints": ["preload", "prefetch"],
            "compression": "gzip",
            "caching_strategy": "stale-while-revalidate",
            "offline_support": True
        }
```

### ADHD配慮のモバイルUX

#### 認知負荷軽減設計

```python
class ADHDMobileUX:
    """ADHD配慮のモバイルUX設計"""
    
    def __init__(self):
        self.max_choices_per_screen = 3
        self.auto_save_interval = 30  # seconds
        self.distraction_prevention = True
    
    def create_simplified_navigation(self) -> dict:
        """シンプルナビゲーション設計"""
        return {
            "type": "bottom_tab",
            "items": [
                {
                    "icon": "🏠",
                    "label": "ホーム",
                    "route": "/home",
                    "primary": True
                },
                {
                    "icon": "📋",
                    "label": "タスク",
                    "route": "/tasks",
                    "badge_count": "dynamic"
                },
                {
                    "icon": "📖",
                    "label": "ストーリー",
                    "route": "/story",
                    "notification": "dynamic"
                }
            ],
            "max_items": 3,  # ADHD配慮
            "large_touch_targets": True
        }
    
    def create_focus_mode_ui(self) -> dict:
        """集中モードUI"""
        return {
            "distraction_blocking": {
                "hide_notifications": True,
                "minimal_ui": True,
                "single_task_focus": True
            },
            "break_reminders": {
                "interval": 25,  # Pomodoro
                "gentle_notification": True,
                "mother_concern_narrative": True
            },
            "progress_visualization": {
                "simple_progress_bar": True,
                "immediate_feedback": True,
                "celebration_animations": True
            }
        }
```

### アクセシビリティ統合

#### JIS X 8341-3 AAA準拠

```python
class MobileAccessibility:
    """モバイルアクセシビリティ実装"""
    
    def __init__(self):
        self.wcag_level = "AAA"
        self.jis_compliance = True
        self.voice_over_support = True
    
    def get_accessibility_config(self) -> dict:
        """アクセシビリティ設定"""
        return {
            "color_contrast": {
                "normal_text": 7.0,  # AAA level
                "large_text": 4.5,
                "ui_components": 3.0
            },
            "font_scaling": {
                "min_size": "16px",
                "max_size": "24px",
                "dynamic_scaling": True
            },
            "touch_targets": {
                "min_size": "44px",
                "spacing": "8px",
                "clear_boundaries": True
            },
            "screen_reader": {
                "aria_labels": True,
                "semantic_html": True,
                "focus_management": True
            },
            "motor_accessibility": {
                "voice_control": True,
                "switch_control": True,
                "gesture_alternatives": True
            }
        }
```

この設計文書は、要件文書で定義された全ての機能要件を技術的に実装可能な形で詳細化しています。特にモバイルファーストの設計思想に基づき、スマートフォン・タブレットでの最適な治療体験を提供するためのUI/UX設計が含まれています。