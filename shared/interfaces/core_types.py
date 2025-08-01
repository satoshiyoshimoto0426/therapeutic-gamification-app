"""
Core TypeScript-style interfaces for the therapeutic gamification app
These interfaces define the core entities and data structures used across all services
"""

from typing import Dict, List, Optional, Union, Literal, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

# Core Enums
class ChapterType(str, Enum):
    SELF_DISCIPLINE = "self_discipline"
    EMPATHY = "empathy"
    RESILIENCE = "resilience"
    CURIOSITY = "curiosity"
    COMMUNICATION = "communication"
    CREATIVITY = "creativity"
    COURAGE = "courage"
    WISDOM = "wisdom"

class CrystalAttribute(str, Enum):
    """8つ"""
    SELF_DISCIPLINE = "self_discipline"  # 自動
    EMPATHY = "empathy"                  # 共有
    RESILIENCE = "resilience"            # ?
    CURIOSITY = "curiosity"              # ?
    COMMUNICATION = "communication"      # コア
    CREATIVITY = "creativity"            # 創
    COURAGE = "courage"                  # 勇
    WISDOM = "wisdom"                    # ?

class CrystalGrowthEvent(str, Enum):
    """?"""
    TASK_COMPLETION = "task_completion"
    STORY_CHOICE = "story_choice"
    MOOD_IMPROVEMENT = "mood_improvement"
    REFLECTION_ENTRY = "reflection_entry"
    SOCIAL_INTERACTION = "social_interaction"
    CREATIVE_ACTIVITY = "creative_activity"
    CHALLENGE_OVERCOME = "challenge_overcome"
    WISDOM_GAINED = "wisdom_gained"

class TaskType(str, Enum):
    ROUTINE = "routine"
    ONE_SHOT = "one_shot"
    SKILL_UP = "skill_up"
    SOCIAL = "social"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class CellStatus(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class GuardianPermission(str, Enum):
    VIEW_ONLY = "view_only"
    TASK_EDIT = "task_edit"
    CHAT_SEND = "chat_send"

# Core Data Models
class UserProfile(BaseModel):
    """Core user profile with comprehensive game state and therapeutic data"""
    uid: str
    email: str
    display_name: str
    player_level: int = 1
    yu_level: int = 1
    total_xp: int = 0
    crystal_gauges: Dict[str, int] = {}  # 8 attributes: 0-100 percentage
    current_chapter: str = "self_discipline"
    daily_task_limit: int = 16  # ADHD consideration
    care_points: int = 0
    guardian_permissions: List[str] = []
    adhd_profile: Dict = {}
    therapeutic_goals: List[str] = []
    created_at: datetime
    last_active: datetime
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize crystal gauges if empty
        if not self.crystal_gauges:
            self.crystal_gauges = {
                "Self-Discipline": 0,
                "Empathy": 0,
                "Resilience": 0,
                "Curiosity": 0,
                "Communication": 0,
                "Creativity": 0,
                "Courage": 0,
                "Wisdom": 0
            }

class StoryState(BaseModel):
    """User's story progression state with DAG navigation"""
    uid: str
    current_chapter: str
    current_node: str
    available_edges: List[str] = []
    story_history: List[Dict] = []
    last_generation_time: Optional[datetime] = None
    unlocked_chapters: List[str] = []
    unlocked_nodes: List[str] = []
    completed_nodes: List[str] = []
    choice_history: List[Dict] = []
    companion_relationships: Dict[str, int] = {}
    ending_scores: Dict[str, float] = {}
    story_flags: Dict[str, Union[str, int, float, bool]] = {}
    last_updated: datetime

class TaskRecord(BaseModel):
    """Task record with XP calculation and story integration"""
    task_id: str
    uid: str
    task_type: TaskType
    title: str
    description: str
    difficulty: int  # 1-5 scale
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    xp_earned: int = 0
    mood_at_completion: Optional[int] = None  # 1-5 scale
    linked_story_edge: Optional[str] = None
    habit_tag: Optional[str] = None
    adhd_support: Dict = {}  # Pomodoro settings, reminders
    created_at: datetime
    
    def calculate_xp(self, mood_coefficient: float, adhd_assist: float) -> int:
        """Calculate XP using the formula: difficulty ? mood_coefficient ? adhd_assist"""
        base_xp = self.difficulty * 10
        calculated_xp = int(base_xp * mood_coefficient * adhd_assist)
        return calculated_xp

class GameState(BaseModel):
    """Core game state tracking player and Yu progression"""
    player_level: int
    yu_level: int
    current_chapter: ChapterType
    crystal_gauges: Dict[ChapterType, int]  # 0-100 percentage
    total_xp: int
    last_resonance_event: Optional[datetime]
    
class XPCalculation(BaseModel):
    """XP calculation components"""
    base_xp: int
    difficulty_multiplier: float
    mood_coefficient: float  # 0.8 - 1.2
    adhd_assist_multiplier: float  # 1.0 - 1.3
    final_xp: int

class User(BaseModel):
    """Core user entity"""
    uid: str
    email: str
    display_name: str
    player_level: int = 1
    yu_level: int = 1
    total_xp: int = 0
    created_at: datetime
    last_active: datetime
    adhd_profile: Dict = {}
    therapeutic_goals: List[str] = []
    game_state: GameState

class MandalaCell(BaseModel):
    """Individual cell in the 9x9 Mandala grid"""
    id: str
    position: tuple[int, int]  # (row, col)
    status: CellStatus
    task_id: Optional[str] = None
    unlock_conditions: List[str] = []
    xp_reward: int = 0
    chapter_type: ChapterType

class MandalaGrid(BaseModel):
    """Complete 9x9 Mandala grid for a chapter"""
    chapter_type: ChapterType
    cells: List[List[MandalaCell]]  # 9x9 grid
    center_value: str  # Core value for this chapter
    completion_percentage: float

class Task(BaseModel):
    """Task entity with ADHD support features"""
    task_id: str
    uid: str
    task_type: TaskType
    title: str
    description: str
    difficulty: int  # 1-5 scale
    status: TaskStatus
    due_date: Optional[datetime]
    mandala_cell_id: Optional[str]
    adhd_support: Dict = {}  # Pomodoro settings, reminders, etc.
    created_at: datetime
    completed_at: Optional[datetime]

class MoodLog(BaseModel):
    """Daily mood tracking"""
    uid: str
    log_date: datetime
    mood_score: int  # 1-5 scale
    notes: Optional[str] = ""
    context_tags: List[str] = []
    calculated_coefficient: float  # 0.8-1.2 for XP calculation

class NodeType(str, Enum):
    OPENING = "opening"
    CHALLENGE = "challenge"
    CHOICE = "choice"
    RESOLUTION = "resolution"
    REFLECTION = "reflection"
    COMPANION_INTRO = "companion_intro"
    MONSTER_ENCOUNTER = "monster_encounter"
    ENDING = "ending"

class UnlockConditionType(str, Enum):
    TASK_COMPLETION = "task_completion"
    MOOD_THRESHOLD = "mood_threshold"
    TIME_BASED = "time_based"
    LEVEL_REQUIREMENT = "level_requirement"
    COMPANION_RELATIONSHIP = "companion_relationship"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    DIARY_COMPLETION = "diary_completion"

class UnlockCondition(BaseModel):
    condition_type: UnlockConditionType
    parameters: Dict[str, Union[str, int, float]]
    required: bool = True

class StoryChapter(BaseModel):
    """Story chapter containing multiple nodes - CHAPTER level"""
    chapter_id: str
    chapter_type: ChapterType
    title: str
    description: str
    unlock_conditions: List[UnlockCondition] = []
    estimated_completion_time: int  # minutes
    therapeutic_focus: List[str] = []
    created_at: datetime

class StoryNode(BaseModel):
    """Story DAG node - NODE level"""
    node_id: str
    chapter_id: str  # Links to parent chapter
    node_type: NodeType
    title: str
    content: str
    estimated_read_time: int  # minutes
    therapeutic_tags: List[str] = []
    unlock_conditions: List[UnlockCondition] = []
    companion_effects: Dict[str, int] = {}
    mood_effects: Dict[str, float] = {}
    ending_flags: Dict[str, Union[str, int, float, bool]] = {}
    created_at: datetime

class StoryEdge(BaseModel):
    """Story DAG edge connecting nodes - EDGE level"""
    edge_id: str
    from_node_id: str
    to_node_id: str
    choice_text: str
    real_task_id: Optional[str] = None  # Links to real-world task
    habit_tag: Optional[str] = None     # Links to habit tracking
    probability: float = 1.0
    therapeutic_weight: float = 1.0
    companion_requirements: Dict[str, int] = {}
    achievement_rewards: List[str] = []
    ending_influence: Dict[str, float] = {}

class UserStoryState(BaseModel):
    """User's story progression state with comprehensive tracking"""
    uid: str
    current_chapter_id: str
    current_node_id: str
    unlocked_chapters: List[str] = []
    unlocked_nodes: List[str] = []
    completed_nodes: List[str] = []
    choice_history: List[Dict[str, Union[str, datetime]]] = []
    companion_relationships: Dict[str, int] = {}
    ending_scores: Dict[str, float] = {}
    story_flags: Dict[str, Union[str, int, float, bool]] = {}
    last_updated: datetime

class GuardianLink(BaseModel):
    """Guardian-user relationship"""
    guardian_id: str
    user_id: str
    permission_level: GuardianPermission
    created_at: datetime
    approved_by_user: bool = False
    care_points: int = 0

# RPG System Types
class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MAGIC = "magic"

class JobClass(str, Enum):
    WARRIOR = "warrior"
    HERO = "hero"
    MAGE = "mage"
    PRIEST = "priest"
    SAGE = "sage"
    NINJA = "ninja"
    # Advanced classes
    PALADIN = "paladin"
    ARCHMAGE = "archmage"
    SHADOW_MASTER = "shadow_master"

class DemonType(str, Enum):
    PROCRASTINATION_DRAGON = "procrastination_dragon"
    ANXIETY_SHADOW = "anxiety_shadow"
    DEPRESSION_VOID = "depression_void"
    SOCIAL_FEAR_GOBLIN = "social_fear_goblin"

class RPGItem(BaseModel):
    """RPG item with therapeutic themes"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    stat_bonuses: Dict[str, int] = {}  # focus, resilience, motivation, etc.
    therapeutic_effect: Optional[str] = None
    flavor_text: str = ""
    icon_url: Optional[str] = None

class UserInventory(BaseModel):
    """User's item inventory"""
    uid: str
    items: List[RPGItem] = []
    equipped_items: Dict[str, Optional[str]] = {}  # slot -> item_id
    total_coins: int = 0
    last_updated: datetime

class JobProgression(BaseModel):
    """User's job class progression"""
    uid: str
    current_job: JobClass
    job_levels: Dict[JobClass, int] = {}
    unlocked_jobs: List[JobClass] = []
    job_skills: Dict[str, int] = {}  # skill_name -> level
    stat_bonuses: Dict[str, int] = {}  # from job progression

class InnerDemon(BaseModel):
    """Inner demon battle entity"""
    demon_id: str
    demon_type: DemonType
    name: str
    hp: int
    max_hp: int
    weaknesses: List[str] = []  # action types that damage this demon
    rewards: Dict[str, Union[int, List[str]]] = {}  # coins, items
    therapeutic_message: str
    appearance_conditions: List[str] = []

class BattleState(BaseModel):
    """Current battle state"""
    uid: str
    demon: InnerDemon
    user_recent_actions: List[str] = []
    battle_log: List[str] = []
    is_active: bool = True
    started_at: datetime

# Crystal System Types
class CrystalState(BaseModel):
    """Individual crystal attribute state"""
    attribute: CrystalAttribute
    current_value: int = 0  # 0-100 percentage
    growth_rate: float = 1.0  # Multiplier for growth events
    last_growth_event: Optional[datetime] = None
    milestone_rewards: List[str] = []  # Unlocked rewards at milestones
    therapeutic_insights: List[str] = []  # Generated insights for this attribute

class CrystalGrowthRecord(BaseModel):
    """Record of crystal growth event"""
    uid: str
    attribute: CrystalAttribute
    event_type: CrystalGrowthEvent
    growth_amount: int  # Points added to crystal
    trigger_context: Dict[str, Any] = {}  # Context that triggered growth
    therapeutic_message: Optional[str] = None
    created_at: datetime

class CrystalMilestone(BaseModel):
    """Crystal milestone definition"""
    attribute: CrystalAttribute
    threshold: int  # 0-100 percentage
    title: str
    description: str
    rewards: List[str] = []  # Item IDs, abilities, etc.
    therapeutic_benefit: str
    unlock_content: List[str] = []  # Story nodes, features, etc.

class UserCrystalSystem(BaseModel):
    """User's complete crystal system state"""
    uid: str
    crystals: Dict[CrystalAttribute, CrystalState] = {}
    total_growth_events: int = 0
    resonance_level: int = 0  # Overall harmony between crystals
    last_resonance_check: Optional[datetime] = None
    active_synergies: List[str] = []  # Active crystal combinations
    growth_history: List[CrystalGrowthRecord] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize all crystal states if empty
        if not self.crystals:
            for attr in CrystalAttribute:
                self.crystals[attr] = CrystalState(attribute=attr)

class CrystalSynergy(BaseModel):
    """Crystal synergy combination effects"""
    synergy_id: str
    name: str
    required_attributes: List[CrystalAttribute]
    min_levels: Dict[CrystalAttribute, int]  # Minimum levels required
    effect_description: str
    stat_bonuses: Dict[str, int] = {}
    therapeutic_benefit: str
    story_unlock: Optional[str] = None

# Growth Note (?) System Types
class GrowthNoteEntry(BaseModel):
    """Daily growth note entry"""
    uid: str
    entry_date: datetime
    current_problems: str = ""  # ?
    ideal_world: str = ""       # ?
    ideal_emotions: str = ""    # ?
    tomorrow_actions: str = ""  # ?
    xp_earned: int = 25
    emotional_tone: Optional[str] = None
    key_themes: List[str] = []
    crystal_growth_triggered: List[CrystalAttribute] = []  # Which crystals grew from this entry
    created_at: datetime

class ReflectionStreak(BaseModel):
    """User's reflection streak tracking"""
    uid: str
    current_streak: int = 0
    longest_streak: int = 0
    total_reflections: int = 0
    last_reflection_date: Optional[datetime] = None
    missed_days_this_week: int = 0
    needs_reminder: bool = False