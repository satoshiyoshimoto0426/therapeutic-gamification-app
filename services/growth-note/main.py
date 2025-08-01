"""
?Growth Note? - ?

4つ:
1. ?
2. 理
3. 理
4. ?
"""

import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EmotionalTone(Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class ActionOrientation(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ReflectionPrompts:
    current_problems_prompt: str
    ideal_world_prompt: str
    ideal_emotions_prompt: str
    tomorrow_actions_prompt: str
    estimated_time: str
    xp_reward: int

@dataclass
class ReflectionAnalysis:
    emotional_tone: EmotionalTone
    problem_themes: List[str]
    action_orientation: ActionOrientation
    key_insights: List[str]
    story_personalization_data: Dict

class GrowthNoteSystem:
    def __init__(self):
        self.reflection_prompts = {
            "current_problems": [
                "?",
                "?",
                "?",
                "?",
                "?"
            ],
            "ideal_world": [
                "あ",
                "も",
                "理",
                "?",
                "?"
            ],
            "ideal_emotions": [
                "理",
                "?",
                "理",
                "理",
                "?"
            ],
            "tomorrow_actions": [
                "?",
                "理",
                "?",
                "理",
                "?"
            ]
        }
        
        self.reflection_xp_base = 25
        self.problem_keywords = {
            "social": ["?", "?", "?", "?", "学", "コア", "?"],
            "work_study": ["?", "?", "学", "?", "?", "?", "成", "?"],
            "health": ["?", "?", "?", "?", "?", "?", "?"],
            "mental": ["?", "?", "ストーリー", "?", "気分", "?", "メイン"],
            "time": ["?", "ストーリー", "?", "?", "?", "?"],
            "motivation": ["や", "モデル", "?", "?", "?", "?"]
        }
        
        self.positive_emotion_words = [
            "?", "?", "?", "?", "?", "安全", "?", "希",
            "?", "?", "?", "自動", "リスト", "?", "?"
        ]
        
        self.negative_emotion_words = [
            "?", "?", "?", "?", "?", "ストーリー", "?", "?",
            "?", "?", "?", "?", "?", "?"
        ]

    def generate_reflection_prompt(self, user_context: Dict) -> ReflectionPrompts:
        """ユーザー"""
        mood = user_context.get("mood", 3)
        completed_tasks = user_context.get("completed_tasks", 0)
        recent_struggles = user_context.get("recent_struggles", [])
        
        return ReflectionPrompts(
            current_problems_prompt=self._select_contextual_prompt(
                "current_problems", mood, completed_tasks, recent_struggles
            ),
            ideal_world_prompt=self._select_contextual_prompt(
                "ideal_world", mood, completed_tasks, recent_struggles
            ),
            ideal_emotions_prompt=self._select_contextual_prompt(
                "ideal_emotions", mood, completed_tasks, recent_struggles
            ),
            tomorrow_actions_prompt=self._select_contextual_prompt(
                "tomorrow_actions", mood, completed_tasks, recent_struggles
            ),
            estimated_time="10-15?",
            xp_reward=self.reflection_xp_base
        )

    def _select_contextual_prompt(self, category: str, mood: int, 
                                completed_tasks: int, recent_struggles: List[str]) -> str:
        """コア"""
        base_prompts = self.reflection_prompts[category]
        
        # 気分
        if mood <= 2:  # ?
            if category == "current_problems":
                return "?"
            elif category == "ideal_world":
                return "理"
            elif category == "ideal_emotions":
                return "理"
            elif category == "tomorrow_actions":
                return "?"
        
        elif mood >= 4:  # ?
            if category == "current_problems":
                return "?"
            elif category == "ideal_world":
                return "?"
            elif category == "ideal_emotions":
                return "理"
            elif category == "tomorrow_actions":
                return "こ"
        
        # タスク
        if completed_tasks == 0:
            if category == "tomorrow_actions":
                return "?"
        elif completed_tasks >= 5:
            if category == "tomorrow_actions":
                return "?"
        
        # デフォルト
        return random.choice(base_prompts)

    def process_reflection(self, reflection_data: Dict) -> ReflectionAnalysis:
        """?"""
        current_problems = reflection_data.get("current_problems", "")
        ideal_world = reflection_data.get("ideal_world", "")
        ideal_emotions = reflection_data.get("ideal_emotions", "")
        tomorrow_actions = reflection_data.get("tomorrow_actions", "")
        
        # ?
        emotional_tone = self._analyze_emotional_tone(ideal_emotions)
        
        # ?
        problem_themes = self._extract_problem_themes(current_problems)
        
        # ?
        action_orientation = self._analyze_action_orientation(tomorrow_actions)
        
        # ?
        key_insights = self._extract_key_insights(reflection_data)
        
        # ストーリー
        story_personalization_data = {
            "current_challenges": problem_themes,
            "ideal_vision": self._extract_key_themes(ideal_world),
            "emotional_state": emotional_tone.value,
            "action_readiness": action_orientation.value,
            "reflection_timestamp": datetime.now().isoformat()
        }
        
        return ReflectionAnalysis(
            emotional_tone=emotional_tone,
            problem_themes=problem_themes,
            action_orientation=action_orientation,
            key_insights=key_insights,
            story_personalization_data=story_personalization_data
        )

    def _analyze_emotional_tone(self, emotional_text: str) -> EmotionalTone:
        """?"""
        if not emotional_text:
            return EmotionalTone.NEUTRAL
        
        text_lower = emotional_text.lower()
        
        positive_count = sum(1 for word in self.positive_emotion_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_emotion_words if word in text_lower)
        
        if positive_count > negative_count:
            if positive_count >= 3:
                return EmotionalTone.VERY_POSITIVE
            else:
                return EmotionalTone.POSITIVE
        elif negative_count > positive_count:
            if negative_count >= 3:
                return EmotionalTone.VERY_NEGATIVE
            else:
                return EmotionalTone.NEGATIVE
        else:
            return EmotionalTone.NEUTRAL

    def _extract_problem_themes(self, problems_text: str) -> List[str]:
        """?"""
        if not problems_text:
            return []
        
        themes = []
        text_lower = problems_text.lower()
        
        for theme, keywords in self.problem_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes

    def _analyze_action_orientation(self, actions_text: str) -> ActionOrientation:
        """?"""
        if not actions_text:
            return ActionOrientation.LOW
        
        # ?
        action_keywords = [
            "す", "や", "?", "?", "?", "実装", "実装",
            "挑", "?", "?", "?", "実装", "?"
        ]
        
        # ?
        time_keywords = [
            "?", "?", "?", "す", "?", "?", "?"
        ]
        
        action_count = sum(1 for word in action_keywords if word in actions_text)
        time_count = sum(1 for word in time_keywords if word in actions_text)
        
        total_score = action_count + time_count
        text_length = len(actions_text)
        
        if total_score >= 3 and text_length > 30:
            return ActionOrientation.HIGH
        elif total_score >= 1 and text_length > 10:
            return ActionOrientation.MEDIUM
        else:
            return ActionOrientation.LOW

    def _extract_key_insights(self, reflection_data: Dict) -> List[str]:
        """?"""
        insights = []
        
        current_problems = reflection_data.get("current_problems", "")
        ideal_world = reflection_data.get("ideal_world", "")
        tomorrow_actions = reflection_data.get("tomorrow_actions", "")
        
        # ?
        if current_problems and ideal_world:
            insights.append("?")
        
        # ?
        if len(tomorrow_actions) > 30:
            insights.append("?")
        
        # ?
        ideal_emotions = reflection_data.get("ideal_emotions", "")
        if len(ideal_emotions) > 20:
            insights.append("理")
        
        return insights

    def _extract_key_themes(self, text: str) -> List[str]:
        """?"""
        if not text:
            return []
        
        # ?NLP?
        themes = []
        
        # ?
        important_concepts = [
            "?", "?", "?", "?", "学", "成", "?", "安全",
            "自動", "創", "挑", "?", "つ", "?", "?"
        ]
        
        for concept in important_concepts:
            if concept in text:
                themes.append(concept)
        
        return themes[:5]  # ?5つ

    def calculate_reflection_xp(self, reflection_analysis: ReflectionAnalysis) -> int:
        """?XP計算"""
        base_xp = self.reflection_xp_base
        
        # ?
        if reflection_analysis.action_orientation == ActionOrientation.HIGH:
            base_xp += 10
        elif reflection_analysis.action_orientation == ActionOrientation.MEDIUM:
            base_xp += 5
        
        # ?
        insight_bonus = len(reflection_analysis.key_insights) * 3
        
        # ?
        theme_bonus = len(reflection_analysis.problem_themes) * 2
        
        return base_xp + insight_bonus + theme_bonus

# 使用
def demo_growth_note_system():
    """?"""
    system = GrowthNoteSystem()
    
    # ?
    user_context = {
        "mood": 3,
        "completed_tasks": 2,
        "recent_struggles": ["social", "motivation"]
    }
    
    # プレビュー
    prompts = system.generate_reflection_prompt(user_context)
    print("=== ? ===")
    print(f"?: {prompts.current_problems_prompt}")
    print(f"理: {prompts.ideal_world_prompt}")
    print(f"理: {prompts.ideal_emotions_prompt}")
    print(f"?: {prompts.tomorrow_actions_prompt}")
    print(f"?: {prompts.estimated_time}")
    print(f"XP?: {prompts.xp_reward}")
    
    # ?
    sample_reflection = {
        "current_problems": "?",
        "ideal_world": "?",
        "ideal_emotions": "安全",
        "tomorrow_actions": "?"
    }
    
    # ?
    analysis = system.process_reflection(sample_reflection)
    print("\n=== ? ===")
    print(f"?: {analysis.emotional_tone.value}")
    print(f"?: {analysis.problem_themes}")
    print(f"?: {analysis.action_orientation.value}")
    print(f"?: {analysis.key_insights}")
    
    # XP計算
    xp_earned = system.calculate_reflection_xp(analysis)
    print(f"?XP: {xp_earned}")
    
    return system, analysis

if __name__ == "__main__":
    demo_growth_note_system()