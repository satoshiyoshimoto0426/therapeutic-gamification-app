"""
?

?
"""

import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from main import GrowthNoteSystem, ReflectionAnalysis

class ReminderType(Enum):
    GENTLE = "gentle"
    ENCOURAGING = "encouraging"
    MOTIVATIONAL = "motivational"

@dataclass
class ReflectionStreak:
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    total_reflections: int = 0
    last_reflection_date: Optional[date] = None
    missed_days_in_row: int = 0
    streak_milestones: List[int] = field(default_factory=lambda: [])

@dataclass
class StoryPersonalizationData:
    user_id: str
    recent_themes: List[str]
    emotional_patterns: List[str]
    action_tendencies: List[str]
    growth_areas: List[str]
    reflection_insights: List[Dict]
    last_updated: datetime

class ReflectionContinuitySystem:
    def __init__(self, growth_note_system: GrowthNoteSystem):
        self.growth_note_system = growth_note_system
        self.user_streaks: Dict[str, ReflectionStreak] = {}
        self.story_personalization: Dict[str, StoryPersonalizationData] = {}
        self.milestone_rewards = {
            3: {"xp": 50, "message": "3?"},
            7: {"xp": 100, "message": "1?"},
            14: {"xp": 200, "message": "2?"},
            21: {"xp": 300, "message": "3?"},
            30: {"xp": 500, "message": "1?"},
            50: {"xp": 750, "message": "50?"},
            100: {"xp": 1500, "message": "100?"}
        }
        
        self.reminder_messages = {
            ReminderType.GENTLE: [
                "?",
                "無",
                "あ",
                "?"
            ],
            ReminderType.ENCOURAGING: [
                "?",
                "?",
                "?",
                "あ"
            ],
            ReminderType.MOTIVATIONAL: [
                "?",
                "あ",
                "?",
                "?"
            ]
        }

    def update_reflection_streak(self, user_id: str, reflection_completed: bool = True) -> Dict:
        """?"""
        today = date.today()
        
        if user_id not in self.user_streaks:
            self.user_streaks[user_id] = ReflectionStreak(user_id=user_id)
        
        streak = self.user_streaks[user_id]
        
        if reflection_completed:
            # ?
            if streak.last_reflection_date == today:
                # ?
                return {"status": "already_completed", "streak": streak.current_streak}
            
            elif streak.last_reflection_date == today - timedelta(days=1):
                # ?
                streak.current_streak += 1
                streak.missed_days_in_row = 0
            
            elif streak.last_reflection_date is None or streak.last_reflection_date < today - timedelta(days=1):
                # ?
                streak.current_streak = 1
                streak.missed_days_in_row = 0
            
            streak.last_reflection_date = today
            streak.total_reflections += 1
            
            # ?
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            
            # ?
            milestone_reward = self._check_milestone(streak)
            
            return {
                "status": "completed",
                "streak": streak.current_streak,
                "total_reflections": streak.total_reflections,
                "milestone_reward": milestone_reward
            }
        
        else:
            # ?
            if streak.last_reflection_date and streak.last_reflection_date < today:
                days_missed = (today - streak.last_reflection_date).days
                streak.missed_days_in_row = days_missed
                
                if days_missed > 1:
                    # 2?
                    streak.current_streak = 0
            
            return {
                "status": "skipped",
                "missed_days": streak.missed_days_in_row,
                "needs_reminder": streak.missed_days_in_row >= 2
            }

    def _check_milestone(self, streak: ReflectionStreak) -> Optional[Dict]:
        """?"""
        if streak.current_streak in self.milestone_rewards:
            if streak.current_streak not in streak.streak_milestones:
                streak.streak_milestones.append(streak.current_streak)
                reward = self.milestone_rewards[streak.current_streak]
                return {
                    "milestone": streak.current_streak,
                    "xp_bonus": reward["xp"],
                    "message": reward["message"]
                }
        return None

    def generate_reminder_message(self, user_id: str, missed_days: int) -> Dict:
        """リスト"""
        # リスト
        if missed_days <= 3:
            reminder_type = ReminderType.GENTLE
        elif missed_days <= 7:
            reminder_type = ReminderType.ENCOURAGING
        else:
            reminder_type = ReminderType.MOTIVATIONAL
        
        # ユーザー
        streak = self.user_streaks.get(user_id, ReflectionStreak(user_id=user_id))
        
        # メイン
        import random
        base_message = random.choice(self.reminder_messages[reminder_type])
        
        # ?
        personalized_message = self._personalize_reminder(base_message, streak, missed_days)
        
        return {
            "type": "flex",
            "altText": "?",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": self._get_reminder_emoji(reminder_type) + " ?",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": self._get_reminder_color(reminder_type),
                    "paddingAll": "lg"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": personalized_message,
                            "size": "sm",
                            "wrap": True,
                            "color": "#666666"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "あ",
                                    "weight": "bold",
                                    "size": "sm",
                                    "margin": "lg"
                                },
                                {
                                    "type": "text",
                                    "text": f"?: {streak.current_streak}?",
                                    "size": "xs",
                                    "color": "#999999",
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": f"?: {streak.longest_streak}?",
                                    "size": "xs",
                                    "color": "#999999",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": f"?: {streak.total_reflections}?",
                                    "size": "xs",
                                    "color": "#999999",
                                    "margin": "xs"
                                }
                            ]
                        }
                    ],
                    "paddingAll": "lg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#FFC857",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": "action=start_reflection_reminder"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": "action=postpone_reflection_reminder"
                            },
                            "margin": "sm"
                        }
                    ],
                    "paddingAll": "lg"
                }
            }
        }

    def _personalize_reminder(self, base_message: str, streak: ReflectionStreak, missed_days: int) -> str:
        """リスト"""
        if streak.longest_streak > 0:
            if missed_days <= 2:
                return f"{base_message}\n\n?{streak.longest_streak}?"
            else:
                return f"{base_message}\n\n{missed_days}?{streak.total_reflections}?"
        else:
            return f"{base_message}\n\n?"

    def _get_reminder_emoji(self, reminder_type: ReminderType) -> str:
        """リスト"""
        emoji_map = {
            ReminderType.GENTLE: "?",
            ReminderType.ENCOURAGING: "?",
            ReminderType.MOTIVATIONAL: "?"
        }
        return emoji_map.get(reminder_type, "?")

    def _get_reminder_color(self, reminder_type: ReminderType) -> str:
        """リスト"""
        color_map = {
            ReminderType.GENTLE: "#F0F4F8",
            ReminderType.ENCOURAGING: "#FFF8E1",
            ReminderType.MOTIVATIONAL: "#FFE8E8"
        }
        return color_map.get(reminder_type, "#F8F9FA")

    def update_story_personalization_data(self, user_id: str, reflection_analysis: ReflectionAnalysis):
        """ストーリー"""
        if user_id not in self.story_personalization:
            self.story_personalization[user_id] = StoryPersonalizationData(
                user_id=user_id,
                recent_themes=[],
                emotional_patterns=[],
                action_tendencies=[],
                growth_areas=[],
                reflection_insights=[],
                last_updated=datetime.now()
            )
        
        data = self.story_personalization[user_id]
        
        # ?10?
        data.recent_themes.extend(reflection_analysis.problem_themes)
        data.recent_themes = list(set(data.recent_themes))[-10:]
        
        # ?
        emotion_value = reflection_analysis.emotional_tone.value
        data.emotional_patterns.append(emotion_value)
        data.emotional_patterns = data.emotional_patterns[-20:]  # ?20?
        
        # ?
        action_value = reflection_analysis.action_orientation.value
        data.action_tendencies.append(action_value)
        data.action_tendencies = data.action_tendencies[-20:]  # ?20?
        
        # 成
        data.growth_areas = self._identify_growth_areas(reflection_analysis)
        
        # ?
        insight_data = {
            "date": datetime.now().isoformat(),
            "insights": reflection_analysis.key_insights,
            "emotional_tone": emotion_value,
            "action_orientation": action_value,
            "themes": reflection_analysis.problem_themes
        }
        data.reflection_insights.append(insight_data)
        data.reflection_insights = data.reflection_insights[-30:]  # ?30?
        
        data.last_updated = datetime.now()

    def _identify_growth_areas(self, reflection_analysis: ReflectionAnalysis) -> List[str]:
        """成"""
        growth_areas = []
        
        # ?
        theme_to_growth = {
            "social": "?",
            "work_study": "学",
            "health": "?",
            "mental": "メイン",
            "time": "?",
            "motivation": "モデル"
        }
        
        for theme in reflection_analysis.problem_themes:
            if theme in theme_to_growth:
                growth_areas.append(theme_to_growth[theme])
        
        # ?
        if reflection_analysis.action_orientation.value == "low":
            growth_areas.append("?")
        elif reflection_analysis.action_orientation.value == "high":
            growth_areas.append("計算")
        
        return list(set(growth_areas))

    def get_story_personalization_context(self, user_id: str) -> Dict:
        """ストーリー"""
        if user_id not in self.story_personalization:
            return {}
        
        data = self.story_personalization[user_id]
        
        # ?
        recent_emotions = data.emotional_patterns[-7:]  # ?7?
        dominant_emotion = max(set(recent_emotions), key=recent_emotions.count) if recent_emotions else "neutral"
        
        # ?
        recent_actions = data.action_tendencies[-7:]  # ?7?
        dominant_action = max(set(recent_actions), key=recent_actions.count) if recent_actions else "medium"
        
        # ?
        recent_insights = data.reflection_insights[-3:]  # ?3?
        
        return {
            "user_id": user_id,
            "recent_themes": data.recent_themes,
            "dominant_emotion": dominant_emotion,
            "dominant_action_tendency": dominant_action,
            "growth_areas": data.growth_areas,
            "recent_insights": [insight["insights"] for insight in recent_insights],
            "reflection_frequency": len(data.reflection_insights),
            "last_updated": data.last_updated.isoformat()
        }

    def get_streak_status(self, user_id: str) -> Dict:
        """ストーリー"""
        if user_id not in self.user_streaks:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_reflections": 0,
                "missed_days_in_row": 0,
                "needs_reminder": False,
                "last_reflection_date": None
            }
        
        streak = self.user_streaks[user_id]
        today = date.today()
        
        # ?
        if streak.last_reflection_date:
            days_since_last = (today - streak.last_reflection_date).days
            needs_reminder = days_since_last >= 2
        else:
            days_since_last = 0
            needs_reminder = False  # ?
        
        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "total_reflections": streak.total_reflections,
            "missed_days_in_row": days_since_last,
            "needs_reminder": needs_reminder,
            "last_reflection_date": streak.last_reflection_date.isoformat() if streak.last_reflection_date else None
        }

# 使用
def demo_continuity_system():
    """?"""
    growth_note_system = GrowthNoteSystem()
    continuity_system = ReflectionContinuitySystem(growth_note_system)
    
    user_id = "demo_user"
    
    print("=== ? ===")
    
    # ?
    result1 = continuity_system.update_reflection_streak(user_id, True)
    print(f"?: {result1}")
    
    # 2?
    streak = continuity_system.user_streaks[user_id]
    streak.last_reflection_date = date.today() - timedelta(days=1)
    result2 = continuity_system.update_reflection_streak(user_id, True)
    print(f"2?: {result2}")
    
    # 3?
    streak.last_reflection_date = date.today() - timedelta(days=1)
    streak.current_streak = 2
    result3 = continuity_system.update_reflection_streak(user_id, True)
    print(f"3?: {result3}")
    
    # リスト
    reminder = continuity_system.generate_reminder_message(user_id, 3)
    print(f"\n=== リスト ===")
    print(json.dumps(reminder, ensure_ascii=False, indent=2))
    
    # ストーリー
    sample_analysis = growth_note_system.process_reflection({
        "current_problems": "?",
        "ideal_world": "?",
        "ideal_emotions": "?",
        "tomorrow_actions": "?"
    })
    
    continuity_system.update_story_personalization_data(user_id, sample_analysis)
    
    # ?
    context = continuity_system.get_story_personalization_context(user_id)
    print(f"\n=== ストーリー ===")
    print(json.dumps(context, ensure_ascii=False, indent=2))
    
    # ストーリー
    status = continuity_system.get_streak_status(user_id)
    print(f"\n=== ストーリー ===")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    
    return continuity_system

if __name__ == "__main__":
    demo_continuity_system()