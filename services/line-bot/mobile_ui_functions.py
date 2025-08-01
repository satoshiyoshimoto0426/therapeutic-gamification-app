"""
Mobile UI functions for LINE Bot
Enhanced mobile-optimized UI components using Flex optimization
"""

from linebot.models import FlexSendMessage as FlexMessage
from typing import List, Dict
from .mobile_flex_optimization import mobile_flex

def create_enhanced_heart_crystal_tasks(tasks: List[Dict]) -> FlexMessage:
    """Create enhanced mobile-optimized Heart Crystal tasks"""
    # Convert tasks to the format expected by mobile_flex
    mandala_items = []
    for task in tasks:
        mandala_items.append({
            "id": task.get("id", ""),
            "title": task.get("title", "タスク"),
            "type": task.get("type", "routine"),
            "difficulty": task.get("difficulty", 1),
            "xp_reward": task.get("xp_reward", 10),
            "completed": task.get("completed", False),
            "progress": task.get("progress", 0)
        })
    
    return mobile_flex.create_3x3_mandala_carousel(
        mandala_items, 
        "? ?"
    )

def create_enhanced_story_delivery(story_data: Dict) -> FlexMessage:
    """Create enhanced mobile-optimized story delivery"""
    return mobile_flex.create_story_choice_carousel(story_data)

def create_compact_task_list(tasks: List[Dict]) -> List[FlexMessage]:
    """Create compact task list for mobile"""
    task_messages = []
    
    for task in tasks:
        task_bubble = mobile_flex.create_compact_task_bubble(task)
        task_messages.append(task_bubble)
    
    return task_messages

def create_achievement_notification(achievement_data: Dict) -> FlexMessage:
    """Create achievement notification"""
    return mobile_flex.create_achievement_notification(achievement_data)

def create_daily_summary(summary_data: Dict) -> FlexMessage:
    """Create daily summary"""
    return mobile_flex.create_daily_summary_bubble(summary_data)

def create_mandala_status_display(mandala_data: Dict) -> FlexMessage:
    """Create Mandala status display using enhanced optimization"""
    # Convert mandala data to items format
    mandala_items = []
    
    # Add crystal attributes as items
    crystal_progress = mandala_data.get("crystal_progress", {})
    crystal_attributes = [
        ("Self-Discipline", "自動", "?"),
        ("Empathy", "共有", "?"),
        ("Resilience", "?", "?"),
        ("Curiosity", "?", "?"),
        ("Communication", "コア", "?"),
        ("Creativity", "創", "?"),
        ("Courage", "勇", "?"),
        ("Wisdom", "?", "?")
    ]
    
    for attr_en, attr_jp, emoji in crystal_attributes:
        progress = crystal_progress.get(attr_en, 0)
        mandala_items.append({
            "id": f"crystal_{attr_en.lower()}",
            "title": attr_jp,
            "type": "growth",
            "progress": progress,
            "completed": progress >= 100
        })
    
    # Fill to 9 items if needed
    while len(mandala_items) < 9:
        mandala_items.append({"type": "empty"})
    
    return mobile_flex.create_3x3_mandala_carousel(
        mandala_items,
        "? Mandala?"
    )