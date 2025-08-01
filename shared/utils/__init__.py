"""
Shared utilities package for the therapeutic gamification app
"""

from .validators import *
from .helpers import *
from .exceptions import *

__all__ = [
    # Validators
    'validate_email',
    'validate_password_strength',
    'validate_mood_score',
    'validate_difficulty_level',
    'validate_xp_calculation_inputs',
    'validate_task_title',
    'validate_task_description',
    'validate_daily_task_limit',
    'validate_mandala_coordinates',
    'validate_growth_note_entry',
    'validate_gacha_type',
    'validate_equipment_slot',
    'validate_job_class',
    'validate_demon_type',
    'validate_item_rarity',
    'validate_reflection_time',
    'validate_therapeutic_content_safety',
    'validate_line_user_id',
    'sanitize_user_input',
    
    # Helpers
    'calculate_xp',
    'calculate_level_from_xp',
    'calculate_xp_for_next_level',
    'check_resonance_event',
    'calculate_mood_coefficient',
    'calculate_adhd_assist_multiplier',
    'calculate_coin_reward',
    'determine_gacha_rarity',
    'generate_therapeutic_item_name',
    'calculate_item_stat_bonuses',
    'format_time_remaining',
    'get_next_reflection_time',
    'analyze_emotional_tone',
    'extract_key_themes',
    'generate_encouragement_message',
    
    # Exceptions
    'TherapeuticGameError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'UserNotFoundError',
    'TaskNotFoundError',
    'DailyTaskLimitExceededError',
    'XPCalculationError',
    'StoryGenerationError',
    'TherapeuticSafetyError',
    'MandalaGridError',
    'InsufficientCoinsError',
    'ItemNotFoundError',
    'InvalidEquipmentSlotError',
    'JobClassNotUnlockedError',
    'BattleNotActiveError',
    'ReflectionAlreadyCompletedError',
    'DatabaseConnectionError',
    'ExternalAPIError',
    'RateLimitExceededError',
    'ConfigurationError',
    'get_http_status_code',
]