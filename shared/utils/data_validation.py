"""
デフォルト

こ
コア
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import re
from enum import Enum

from ..interfaces.core_types import (
    UserProfile, StoryState, TaskRecord, TaskType, TaskStatus,
    CrystalAttribute, ChapterType, CellStatus, GuardianPermission,
    NodeType, UnlockConditionType, ItemRarity, ItemType, JobClass, DemonType
)


class ValidationError(Exception):
    """バリデーション"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class ValidationResult:
    """バリデーション"""
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, field: str, message: str, value: Any = None):
        """エラー"""
        self.is_valid = False
        error_msg = f"{field}: {message}"
        if value is not None:
            error_msg += f" (?: {value})"
        self.errors.append(error_msg)
    
    def add_warning(self, field: str, message: str, value: Any = None):
        """?"""
        warning_msg = f"{field}: {message}"
        if value is not None:
            warning_msg += f" (?: {value})"
        self.warnings.append(warning_msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """?"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class DataValidator:
    """デフォルト"""
    
    # ?
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    UID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{8,64}$')
    TASK_ID_PATTERN = re.compile(r'^task_[a-zA-Z0-9_-]{8,32}$')
    NODE_ID_PATTERN = re.compile(r'^node_[a-zA-Z0-9_-]{8,32}$')
    
    # ?
    MIN_LEVEL = 1
    MAX_LEVEL = 100
    MIN_XP = 0
    MAX_XP = 1000000
    MIN_CRYSTAL_VALUE = 0
    MAX_CRYSTAL_VALUE = 100
    MIN_MOOD_SCORE = 1
    MAX_MOOD_SCORE = 5
    MIN_DIFFICULTY = 1
    MAX_DIFFICULTY = 5
    MAX_DAILY_TASKS = 16
    MIN_CARE_POINTS = 0
    MAX_CARE_POINTS = 100000
    
    @classmethod
    def validate_user_profile(cls, profile: UserProfile) -> ValidationResult:
        """UserProfileの"""
        result = ValidationResult()
        
        # UID検証
        if not cls.UID_PATTERN.match(profile.uid):
            result.add_error("uid", "無UID?", profile.uid)
        
        # メイン
        if not cls.EMAIL_PATTERN.match(profile.email):
            result.add_error("email", "無", profile.email)
        
        # 表
        if not profile.display_name or len(profile.display_name.strip()) == 0:
            result.add_error("display_name", "表")
        elif len(profile.display_name) > 50:
            result.add_error("display_name", "表50文字", len(profile.display_name))
        
        # レベル
        if not (cls.MIN_LEVEL <= profile.player_level <= cls.MAX_LEVEL):
            result.add_error("player_level", f"プレビュー{cls.MIN_LEVEL}-{cls.MAX_LEVEL}の", profile.player_level)
        
        if not (cls.MIN_LEVEL <= profile.yu_level <= cls.MAX_LEVEL):
            result.add_error("yu_level", f"ユーザー{cls.MIN_LEVEL}-{cls.MAX_LEVEL}の", profile.yu_level)
        
        # XP検証
        if not (cls.MIN_XP <= profile.total_xp <= cls.MAX_XP):
            result.add_error("total_xp", f"?XPは{cls.MIN_XP}-{cls.MAX_XP}の", profile.total_xp)
        
        # ?
        cls._validate_crystal_gauges(profile.crystal_gauges, result)
        
        # ?
        if profile.current_chapter not in [chapter.value for chapter in ChapterType]:
            result.add_error("current_chapter", "無", profile.current_chapter)
        
        # ?
        if not (1 <= profile.daily_task_limit <= cls.MAX_DAILY_TASKS):
            result.add_error("daily_task_limit", f"?1-{cls.MAX_DAILY_TASKS}の", profile.daily_task_limit)
        
        # ?
        if not (cls.MIN_CARE_POINTS <= profile.care_points <= cls.MAX_CARE_POINTS):
            result.add_error("care_points", f"?{cls.MIN_CARE_POINTS}-{cls.MAX_CARE_POINTS}の", profile.care_points)
        
        # ?
        valid_permissions = [perm.value for perm in GuardianPermission]
        for perm in profile.guardian_permissions:
            if perm not in valid_permissions:
                result.add_error("guardian_permissions", f"無: {perm}")
        
        # ?
        cls._validate_timestamps(profile.created_at, profile.last_active, result)
        
        return result
    
    @classmethod
    def validate_story_state(cls, story_state: StoryState) -> ValidationResult:
        """StoryStateの"""
        result = ValidationResult()
        
        # UID検証
        if not cls.UID_PATTERN.match(story_state.uid):
            result.add_error("uid", "無UID?", story_state.uid)
        
        # ?
        if story_state.current_chapter not in [chapter.value for chapter in ChapterType]:
            result.add_error("current_chapter", "無", story_state.current_chapter)
        
        # ?ID検証
        if not cls.NODE_ID_PATTERN.match(story_state.current_node):
            result.add_error("current_node", "無ID?", story_state.current_node)
        
        # エラー
        for edge in story_state.available_edges:
            if not isinstance(edge, str) or len(edge) == 0:
                result.add_error("available_edges", "無IDで", edge)
        
        # アプリ
        valid_chapters = [chapter.value for chapter in ChapterType]
        for chapter in story_state.unlocked_chapters:
            if chapter not in valid_chapters:
                result.add_error("unlocked_chapters", f"無: {chapter}")
        
        # アプリ
        for node in story_state.unlocked_nodes:
            if not cls.NODE_ID_PATTERN.match(node):
                result.add_error("unlocked_nodes", f"無ID?: {node}")
        
        # ?
        for node in story_state.completed_nodes:
            if not cls.NODE_ID_PATTERN.match(node):
                result.add_error("completed_nodes", f"無ID?: {node}")
        
        # ?
        cls._validate_choice_history(story_state.choice_history, result)
        
        # コア
        cls._validate_companion_relationships(story_state.companion_relationships, result)
        
        # エラー
        cls._validate_ending_scores(story_state.ending_scores, result)
        
        # ストーリー
        cls._validate_story_flags(story_state.story_flags, result)
        
        # ?
        if story_state.last_generation_time:
            if story_state.last_generation_time > datetime.now():
                result.add_error("last_generation_time", "?", story_state.last_generation_time)
        
        # ?
        if story_state.last_updated > datetime.now():
            result.add_error("last_updated", "?", story_state.last_updated)
        
        return result
    
    @classmethod
    def validate_task_record(cls, task_record: TaskRecord) -> ValidationResult:
        """TaskRecordの"""
        result = ValidationResult()
        
        # タスクID検証
        if not cls.TASK_ID_PATTERN.match(task_record.task_id):
            result.add_error("task_id", "無ID?", task_record.task_id)
        
        # UID検証
        if not cls.UID_PATTERN.match(task_record.uid):
            result.add_error("uid", "無UID?", task_record.uid)
        
        # タスク
        if task_record.task_type not in TaskType:
            result.add_error("task_type", "無", task_record.task_type)
        
        # タスク
        if not task_record.title or len(task_record.title.strip()) == 0:
            result.add_error("title", "タスク")
        elif len(task_record.title) > 100:
            result.add_error("title", "タスク100文字", len(task_record.title))
        
        # ?
        if len(task_record.description) > 500:
            result.add_error("description", "?500文字", len(task_record.description))
        
        # ?
        if not (cls.MIN_DIFFICULTY <= task_record.difficulty <= cls.MAX_DIFFICULTY):
            result.add_error("difficulty", f"?{cls.MIN_DIFFICULTY}-{cls.MAX_DIFFICULTY}の", task_record.difficulty)
        
        # ストーリー
        if task_record.status not in TaskStatus:
            result.add_error("status", "無", task_record.status)
        
        # XP検証
        if task_record.xp_earned < 0:
            result.add_error("xp_earned", "?XPは0?", task_record.xp_earned)
        
        # 気分
        if task_record.mood_at_completion is not None:
            if not (cls.MIN_MOOD_SCORE <= task_record.mood_at_completion <= cls.MAX_MOOD_SCORE):
                result.add_error("mood_at_completion", f"気分{cls.MIN_MOOD_SCORE}-{cls.MAX_MOOD_SCORE}の", task_record.mood_at_completion)
        
        # ?
        if task_record.due_date:
            if task_record.due_date < datetime.now() - timedelta(days=365):
                result.add_warning("due_date", "?1?", task_record.due_date)
        
        # ?
        if task_record.completion_time:
            if task_record.completion_time > datetime.now():
                result.add_error("completion_time", "?", task_record.completion_time)
            if task_record.completion_time < task_record.created_at:
                result.add_error("completion_time", "?")
        
        # ストーリー
        if task_record.status == TaskStatus.COMPLETED and not task_record.completion_time:
            result.add_error("completion_time", "?")
        elif task_record.status != TaskStatus.COMPLETED and task_record.completion_time:
            result.add_warning("completion_time", "?")
        
        # ADHD支援
        cls._validate_adhd_support(task_record.adhd_support, result)
        
        return result
    
    @classmethod
    def validate_xp_calculation(cls, difficulty: int, mood_coefficient: float, 
                               adhd_assist: float) -> ValidationResult:
        """XP計算"""
        result = ValidationResult()
        
        # ?
        if not (cls.MIN_DIFFICULTY <= difficulty <= cls.MAX_DIFFICULTY):
            result.add_error("difficulty", f"?{cls.MIN_DIFFICULTY}-{cls.MAX_DIFFICULTY}の", difficulty)
        
        # 気分
        if not (0.8 <= mood_coefficient <= 1.2):
            result.add_error("mood_coefficient", "気分0.8-1.2の", mood_coefficient)
        
        # ADHD支援
        if not (1.0 <= adhd_assist <= 1.3):
            result.add_error("adhd_assist", "ADHD支援1.0-1.3の", adhd_assist)
        
        return result
    
    @classmethod
    def validate_crystal_growth(cls, attribute: str, growth_amount: int) -> ValidationResult:
        """?"""
        result = ValidationResult()
        
        # ?
        if attribute not in [attr.value for attr in CrystalAttribute]:
            result.add_error("attribute", "無", attribute)
        
        # 成
        if not (0 <= growth_amount <= 20):
            result.add_error("growth_amount", "成0-20の", growth_amount)
        
        return result
    
    @classmethod
    def validate_mandala_position(cls, row: int, col: int) -> ValidationResult:
        """Mandala?"""
        result = ValidationResult()
        
        if not (0 <= row < 9):
            result.add_error("row", "?0-8の", row)
        
        if not (0 <= col < 9):
            result.add_error("col", "?0-8の", col)
        
        return result
    
    @classmethod
    def _validate_crystal_gauges(cls, crystal_gauges: Dict[str, int], result: ValidationResult):
        """?"""
        expected_attributes = [attr.value for attr in CrystalAttribute]
        
        for attr_name, value in crystal_gauges.items():
            if attr_name not in expected_attributes:
                result.add_warning("crystal_gauges", f"?: {attr_name}")
            
            if not (cls.MIN_CRYSTAL_VALUE <= value <= cls.MAX_CRYSTAL_VALUE):
                result.add_error("crystal_gauges", f"?{cls.MIN_CRYSTAL_VALUE}-{cls.MAX_CRYSTAL_VALUE}の", f"{attr_name}: {value}")
        
        # ?
        for attr in expected_attributes:
            if attr not in crystal_gauges:
                result.add_warning("crystal_gauges", f"?: {attr}")
    
    @classmethod
    def _validate_timestamps(cls, created_at: datetime, last_active: datetime, result: ValidationResult):
        """タスク"""
        now = datetime.now()
        
        if created_at > now:
            result.add_error("created_at", "?", created_at)
        
        if last_active > now:
            result.add_error("last_active", "?", last_active)
        
        if last_active < created_at:
            result.add_error("last_active", "?")
    
    @classmethod
    def _validate_choice_history(cls, choice_history: List[Dict], result: ValidationResult):
        """?"""
        for i, choice in enumerate(choice_history):
            if not isinstance(choice, dict):
                result.add_error("choice_history", f"?[{i}]は")
                continue
            
            required_fields = ["node_id", "choice_text", "timestamp"]
            for field in required_fields:
                if field not in choice:
                    result.add_error("choice_history", f"?[{i}]に'{field}'が")
    
    @classmethod
    def _validate_companion_relationships(cls, relationships: Dict[str, int], result: ValidationResult):
        """コア"""
        for companion, level in relationships.items():
            if not isinstance(companion, str) or len(companion) == 0:
                result.add_error("companion_relationships", "無", companion)
            
            if not (-100 <= level <= 100):
                result.add_error("companion_relationships", f"?-100か100の", f"{companion}: {level}")
    
    @classmethod
    def _validate_ending_scores(cls, ending_scores: Dict[str, float], result: ValidationResult):
        """エラー"""
        for ending, score in ending_scores.items():
            if not isinstance(ending, str) or len(ending) == 0:
                result.add_error("ending_scores", "無", ending)
            
            if not (0.0 <= score <= 1.0):
                result.add_error("ending_scores", f"エラー0.0-1.0の", f"{ending}: {score}")
    
    @classmethod
    def _validate_story_flags(cls, story_flags: Dict[str, Union[str, int, float, bool]], result: ValidationResult):
        """ストーリー"""
        for flag_name, flag_value in story_flags.items():
            if not isinstance(flag_name, str) or len(flag_name) == 0:
                result.add_error("story_flags", "無", flag_name)
            
            if not isinstance(flag_value, (str, int, float, bool)):
                result.add_error("story_flags", f"?", f"{flag_name}: {type(flag_value)}")
    
    @classmethod
    def _validate_adhd_support(cls, adhd_support: Dict[str, Any], result: ValidationResult):
        """ADHD支援"""
        if "pomodoro_enabled" in adhd_support:
            if not isinstance(adhd_support["pomodoro_enabled"], bool):
                result.add_error("adhd_support.pomodoro_enabled", "?")
        
        if "work_duration" in adhd_support:
            work_duration = adhd_support["work_duration"]
            if not isinstance(work_duration, int) or not (5 <= work_duration <= 60):
                result.add_error("adhd_support.work_duration", "?5-60?", work_duration)
        
        if "break_duration" in adhd_support:
            break_duration = adhd_support["break_duration"]
            if not isinstance(break_duration, int) or not (1 <= break_duration <= 30):
                result.add_error("adhd_support.break_duration", "?1-30?", break_duration)
        
        if "reminder_enabled" in adhd_support:
            if not isinstance(adhd_support["reminder_enabled"], bool):
                result.add_error("adhd_support.reminder_enabled", "リスト")


# バリデーション
def validate_user_profile(profile: UserProfile) -> ValidationResult:
    """UserProfileの"""
    return DataValidator.validate_user_profile(profile)


def validate_story_state(story_state: StoryState) -> ValidationResult:
    """StoryStateの"""
    return DataValidator.validate_story_state(story_state)


def validate_task_record(task_record: TaskRecord) -> ValidationResult:
    """TaskRecordの"""
    return DataValidator.validate_task_record(task_record)


def validate_xp_calculation(difficulty: int, mood_coefficient: float, adhd_assist: float) -> ValidationResult:
    """XP計算"""
    return DataValidator.validate_xp_calculation(difficulty, mood_coefficient, adhd_assist)


def validate_crystal_growth(attribute: str, growth_amount: int) -> ValidationResult:
    """?"""
    return DataValidator.validate_crystal_growth(attribute, growth_amount)


def validate_mandala_position(row: int, col: int) -> ValidationResult:
    """Mandala?"""
    return DataValidator.validate_mandala_position(row, col)


# バリデーション
def validate_multiple_tasks(task_records: List[TaskRecord]) -> Dict[str, ValidationResult]:
    """?"""
    results = {}
    for task in task_records:
        results[task.task_id] = validate_task_record(task)
    return results


def validate_user_data_consistency(profile: UserProfile, story_state: StoryState, 
                                 task_records: List[TaskRecord]) -> ValidationResult:
    """ユーザー"""
    result = ValidationResult()
    
    # UID?
    if profile.uid != story_state.uid:
        result.add_error("uid_consistency", "UserProfileとStoryStateのUIDが")
    
    for task in task_records:
        if task.uid != profile.uid:
            result.add_error("uid_consistency", f"タスク{task.task_id}のUIDが")
    
    # レベルXPの
    expected_level = calculate_level_from_xp(profile.total_xp)
    if abs(profile.player_level - expected_level) > 1:
        result.add_warning("level_xp_consistency", f"レベル({profile.player_level})とXP({profile.total_xp})の")
    
    # ?
    if profile.current_chapter != story_state.current_chapter:
        result.add_error("chapter_consistency", "UserProfileとStoryStateの")
    
    # ?XP?
    completed_tasks = [task for task in task_records if task.status == TaskStatus.COMPLETED]
    total_task_xp = sum(task.xp_earned for task in completed_tasks)
    
    if abs(profile.total_xp - total_task_xp) > profile.total_xp * 0.1:  # 10%の
        result.add_warning("xp_consistency", f"プレビューXP({profile.total_xp})とXP?({total_task_xp})に")
    
    return result


def calculate_level_from_xp(total_xp: int) -> int:
    """XPか"""
    if total_xp < 0:
        return 1
    
    # ?: level = floor(sqrt(total_xp / 100)) + 1
    import math
    level = int(math.sqrt(total_xp / 100)) + 1
    return min(level, 100)  # ?100


def is_valid_email(email: str) -> bool:
    """メイン"""
    return bool(DataValidator.EMAIL_PATTERN.match(email))


def is_valid_uid(uid: str) -> bool:
    """UIDの"""
    return bool(DataValidator.UID_PATTERN.match(uid))


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """ユーザー"""
    if not isinstance(text, str):
        return ""
    
    # ?
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # ?
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # ?
    if len(text) > max_length:
        text = text[:max_length]
    
    # ?
    text = text.strip()
    
    return text