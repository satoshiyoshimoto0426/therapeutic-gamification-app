"""
Shared helper utilities for the therapeutic gamification app
Common functions used across multiple microservices
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from ..interfaces.core_types import TaskType, JobClass, ItemRarity

def calculate_xp(difficulty: int, mood_coefficient: float, adhd_assist: float) -> int:
    """
    Calculate XP using the formula: XP = difficulty ? mood_coefficient ? adhd_assist
    
    Args:
        difficulty: Task difficulty (1-5)
        mood_coefficient: Mood-based multiplier (0.8-1.2)
        adhd_assist: ADHD assistance multiplier (1.0-1.3)
    
    Returns:
        Calculated XP amount
    """
    base_xp = difficulty * 10
    final_xp = int(base_xp * mood_coefficient * adhd_assist)
    return max(1, final_xp)  # Ensure minimum 1 XP

def calculate_level_from_xp(total_xp: int) -> int:
    """
    Calculate level using exponential progression: level = log2(total_xp/100 + 1)
    
    Args:
        total_xp: Total accumulated XP
    
    Returns:
        Current level
    """
    if total_xp <= 0:
        return 1
    return max(1, int(math.log2(total_xp / 100 + 1)))

def calculate_xp_for_next_level(current_level: int) -> int:
    """
    Calculate XP required for next level: XP = (2^(level+1) - 1) * 100
    
    Args:
        current_level: Current player level
    
    Returns:
        XP required for next level
    """
    return (2 ** (current_level + 1) - 1) * 100

def check_resonance_event(yu_level: int, player_level: int) -> bool:
    """
    Check if resonance event should trigger (level difference >= 5)
    
    Args:
        yu_level: Yu character level
        player_level: Player level
    
    Returns:
        True if resonance event should trigger
    """
    return abs(yu_level - player_level) >= 5

def calculate_mood_coefficient(mood_score: int) -> float:
    """
    Convert mood score (1-5) to XP coefficient (0.8-1.2)
    
    Args:
        mood_score: Mood score from 1-5
    
    Returns:
        Mood coefficient for XP calculation
    """
    if not (1 <= mood_score <= 5):
        return 1.0
    
    # Linear mapping: 1->0.8, 2->0.9, 3->1.0, 4->1.1, 5->1.2
    return 0.6 + (mood_score * 0.1)

def calculate_adhd_assist_multiplier(pomodoro_usage_rate: float) -> float:
    """
    Calculate ADHD assistance multiplier based on tool usage
    
    Args:
        pomodoro_usage_rate: Usage rate of ADHD tools (0.0-1.0)
    
    Returns:
        ADHD assist multiplier (1.0-1.3)
    """
    return min(1.3, 1.0 + (pomodoro_usage_rate * 0.3))

def calculate_coin_reward(action_type: str, difficulty: int, performance_multiplier: float = 1.0) -> int:
    """
    Calculate coin reward for various actions
    
    Args:
        action_type: Type of action ("task_completion", "demon_defeat", etc.)
        difficulty: Difficulty level (1-5)
        performance_multiplier: Performance-based multiplier
    
    Returns:
        Coin reward amount
    """
    base_rates = {
        "task_completion": {"routine": 10, "one_shot": 15, "skill_up": 20, "social": 25},
        "demon_defeat": {"common": 50, "rare": 100, "epic": 200, "legendary": 500},
        "daily_bonus": 30,
        "reflection_bonus": 25
    }
    
    if action_type == "task_completion":
        base_coins = base_rates["task_completion"].get("routine", 10)
    else:
        base_coins = base_rates.get(action_type, 10)
    
    return int(base_coins * difficulty * performance_multiplier)

def determine_gacha_rarity(rates: Dict[str, float], premium: bool = False) -> str:
    """
    Determine item rarity based on gacha rates
    
    Args:
        rates: Rarity rates dictionary
        premium: Whether this is a premium gacha (2x rare chance)
    
    Returns:
        Selected rarity string
    """
    if premium:
        # Double rare+ chances for premium gacha
        adjusted_rates = rates.copy()
        adjusted_rates["rare"] *= 2
        adjusted_rates["epic"] *= 2
        adjusted_rates["legendary"] *= 2
        
        # Normalize rates
        total = sum(adjusted_rates.values())
        adjusted_rates = {k: v/total for k, v in adjusted_rates.items()}
        rates = adjusted_rates
    
    rand = random.random()
    cumulative = 0.0
    
    for rarity, rate in rates.items():
        cumulative += rate
        if rand <= cumulative:
            return rarity
    
    return "common"  # Fallback

def generate_therapeutic_item_name(rarity: str, item_type: str) -> str:
    """
    Generate therapeutic-themed item names
    
    Args:
        rarity: Item rarity
        item_type: Type of item
    
    Returns:
        Generated item name
    """
    prefixes = {
        "common": ["基本", "?", "?"],
        "uncommon": ["?", "?", "?"],
        "rare": ["希", "?", "?"],
        "epic": ["?", "?", "?"],
        "legendary": ["?", "?", "?"]
    }
    
    item_names = {
        "weapon": ["?", "や", "勇", "希"],
        "armor": ["?", "安全", "自動", "成"],
        "accessory": ["?", "共有", "創"],
        "consumable": ["?", "?", "?"]
    }
    
    prefix = random.choice(prefixes.get(rarity, prefixes["common"]))
    name = random.choice(item_names.get(item_type, item_names["weapon"]))
    
    return f"{prefix}{name}"

def calculate_item_stat_bonuses(rarity: str, item_type: str) -> Dict[str, int]:
    """
    Calculate stat bonuses for items based on rarity and type
    
    Args:
        rarity: Item rarity
        item_type: Type of item
    
    Returns:
        Dictionary of stat bonuses
    """
    rarity_multipliers = {
        "common": 1,
        "uncommon": 2,
        "rare": 3,
        "epic": 5,
        "legendary": 8
    }
    
    base_stats = {
        "weapon": {"focus": 2, "motivation": 1},
        "armor": {"resilience": 2, "focus": 1},
        "accessory": {"social": 1, "creativity": 1, "wisdom": 1},
        "consumable": {"motivation": 1}
    }
    
    multiplier = rarity_multipliers.get(rarity, 1)
    base = base_stats.get(item_type, {"focus": 1})
    
    return {stat: value * multiplier for stat, value in base.items()}

def format_time_remaining(target_time: datetime) -> str:
    """
    Format time remaining until target time
    
    Args:
        target_time: Target datetime
    
    Returns:
        Formatted time string
    """
    now = datetime.now()
    if target_time <= now:
        return "?"
    
    diff = target_time - now
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if diff.days > 0:
        return f"{diff.days}?{hours}?{minutes}?"
    elif hours > 0:
        return f"{hours}?{minutes}?"
    else:
        return f"{minutes}?"

def get_next_reflection_time() -> datetime:
    """
    Get next reflection time (22:00 today or tomorrow)
    
    Returns:
        Next reflection datetime
    """
    now = datetime.now()
    today_reflection = now.replace(hour=22, minute=0, second=0, microsecond=0)
    
    if now < today_reflection:
        return today_reflection
    else:
        return today_reflection + timedelta(days=1)

def analyze_emotional_tone(text: str) -> str:
    """
    Basic emotional tone analysis of text
    
    Args:
        text: Text to analyze
    
    Returns:
        Emotional tone category
    """
    positive_words = ["?", "?", "?", "?", "?", "?", "?"]
    negative_words = ["?", "?", "?", "?", "?", "?", "ストーリー"]
    neutral_words = ["?", "ま", "?", "?"]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    neutral_count = sum(1 for word in neutral_words if word in text_lower)
    
    if positive_count > negative_count and positive_count > neutral_count:
        return "positive"
    elif negative_count > positive_count and negative_count > neutral_count:
        return "negative"
    else:
        return "neutral"

def extract_key_themes(text: str) -> List[str]:
    """
    Extract key themes from reflection text
    
    Args:
        text: Text to analyze
    
    Returns:
        List of key themes
    """
    theme_keywords = {
        "work": ["?", "?", "?", "?", "?"],
        "health": ["?", "?", "?", "?", "?"],
        "relationships": ["?", "?", "?", "?", "コア"],
        "learning": ["?", "学", "学", "?", "?"],
        "creativity": ["創", "アプリ", "?", "?", "創"],
        "self_improvement": ["成", "?", "?", "発", "?"]
    }
    
    found_themes = []
    text_lower = text.lower()
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_themes.append(theme)
    
    return found_themes

def generate_encouragement_message(streak: int, missed_days: int) -> str:
    """
    Generate encouragement message based on reflection streak
    
    Args:
        streak: Current reflection streak
        missed_days: Number of missed days
    
    Returns:
        Encouragement message
    """
    if streak >= 30:
        return "?"
    elif streak >= 7:
        return "1?"
    elif streak >= 3:
        return "3?"
    elif missed_days >= 3:
        return "お"
    else:
        return "?"