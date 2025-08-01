"""
Shared validation utilities for the therapeutic gamification app
Provides common validation functions used across all microservices
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..interfaces.core_types import TaskType, JobClass, ItemRarity, DemonType

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength and return detailed feedback"""
    result = {
        "valid": True,
        "score": 0,
        "feedback": []
    }
    
    if len(password) < 8:
        result["valid"] = False
        result["feedback"].append("?8文字")
    else:
        result["score"] += 1
    
    if not re.search(r'[A-Z]', password):
        result["feedback"].append("?")
    else:
        result["score"] += 1
    
    if not re.search(r'[a-z]', password):
        result["feedback"].append("?")
    else:
        result["score"] += 1
    
    if not re.search(r'\d', password):
        result["feedback"].append("?")
    else:
        result["score"] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["feedback"].append("?")
    else:
        result["score"] += 1
    
    return result

def validate_mood_score(score: int) -> bool:
    """Validate mood score (1-5 scale)"""
    return 1 <= score <= 5

def validate_difficulty_level(difficulty: int) -> bool:
    """Validate task difficulty level (1-5 scale)"""
    return 1 <= difficulty <= 5

def validate_xp_calculation_inputs(difficulty: int, mood_score: int, adhd_assist: float) -> Dict[str, Any]:
    """Validate XP calculation input parameters"""
    errors = []
    
    if not validate_difficulty_level(difficulty):
        errors.append("?1-5の")
    
    if not validate_mood_score(mood_score):
        errors.append("気分1-5の")
    
    if not (1.0 <= adhd_assist <= 1.3):
        errors.append("ADHD支援1.0-1.3の")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_task_title(title: str) -> bool:
    """Validate task title"""
    return 1 <= len(title.strip()) <= 100

def validate_task_description(description: str) -> bool:
    """Validate task description"""
    return len(description.strip()) <= 500

def validate_daily_task_limit(task_count: int, limit: int = 16) -> bool:
    """Validate daily task count against ADHD-friendly limit"""
    return task_count <= limit

def validate_mandala_coordinates(x: int, y: int) -> bool:
    """Validate Mandala grid coordinates (0-8 range for 9x9 grid)"""
    return 0 <= x <= 8 and 0 <= y <= 8

def validate_growth_note_entry(entry_data: Dict[str, str]) -> Dict[str, Any]:
    """Validate growth note entry data"""
    required_fields = ["current_problems", "ideal_world", "ideal_emotions", "tomorrow_actions"]
    errors = []
    
    for field in required_fields:
        if field not in entry_data:
            errors.append(f"? '{field}' が")
        elif len(entry_data[field].strip()) > 500:
            errors.append(f"? '{field}' は500文字")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_gacha_type(gacha_type: str) -> bool:
    """Validate gacha type"""
    valid_types = ["single", "ten_pull", "premium"]
    return gacha_type in valid_types

def validate_equipment_slot(slot: str) -> bool:
    """Validate equipment slot name"""
    valid_slots = ["weapon", "armor", "accessory", "consumable_1", "consumable_2", "consumable_3"]
    return slot in valid_slots

def validate_job_class(job_class: str) -> bool:
    """Validate job class"""
    try:
        JobClass(job_class)
        return True
    except ValueError:
        return False

def validate_demon_type(demon_type: str) -> bool:
    """Validate inner demon type"""
    try:
        DemonType(demon_type)
        return True
    except ValueError:
        return False

def validate_item_rarity(rarity: str) -> bool:
    """Validate item rarity"""
    try:
        ItemRarity(rarity)
        return True
    except ValueError:
        return False

def validate_reflection_time(time_str: str) -> bool:
    """Validate reflection time format (HH:MM)"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))

def validate_user_age_for_adhd_features(birth_date: Optional[datetime]) -> bool:
    """Validate user age for ADHD-specific features (typically 13+)"""
    if not birth_date:
        return False
    
    age = (datetime.now() - birth_date).days / 365.25
    return age >= 13

def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input text"""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_therapeutic_content_safety(content: str) -> Dict[str, Any]:
    """Basic validation for therapeutic content safety"""
    # This is a basic implementation - in production, this would integrate
    # with OpenAI Moderation API and custom safety filters
    
    harmful_patterns = [
        r'\b(自動|自動|死)\b',
        r'\b(?|?|?)\b',
        r'\b(?|?|?)\b'
    ]
    
    flags = []
    for pattern in harmful_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            flags.append(f"Potentially harmful content detected: {pattern}")
    
    return {
        "safe": len(flags) == 0,
        "flags": flags,
        "confidence": 0.8 if len(flags) == 0 else 0.2
    }

def validate_line_user_id(user_id: str) -> bool:
    """Validate LINE user ID format"""
    # LINE user IDs are typically 33 characters long and alphanumeric
    pattern = r'^[a-zA-Z0-9]{33}$'
    return bool(re.match(pattern, user_id))

def validate_timezone(timezone_str: str) -> bool:
    """Validate timezone string"""
    # Basic validation for common timezone formats
    pattern = r'^[A-Z]{3,4}([+-]\d{1,2})?$|^UTC([+-]\d{1,2})?$'
    return bool(re.match(pattern, timezone_str))

def validate_positive_int(value: int, field_name: str, allow_zero: bool = False) -> None:
    """Validate positive integer value"""
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    
    if allow_zero and value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    elif not allow_zero and value <= 0:
        raise ValueError(f"{field_name} must be positive")

def validate_range(value: float, min_val: float, max_val: float, field_name: str) -> None:
    """Validate value is within specified range"""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    
    if not (min_val <= value <= max_val):
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}")

def validate_coin_amount(amount: int) -> bool:
    """Validate coin amount"""
    return isinstance(amount, int) and amount >= 0

def validate_performance_multiplier(multiplier: float) -> bool:
    """Validate performance multiplier range"""
    return isinstance(multiplier, (int, float)) and 0.5 <= multiplier <= 2.0