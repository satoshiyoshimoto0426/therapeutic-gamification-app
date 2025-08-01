"""
LINE Bot?UI?

22:00のFlexメイン
"""

import json
import random
from datetime import datetime, time
from typing import Dict, List, Optional
from dataclasses import dataclass
from main import GrowthNoteSystem, ReflectionAnalysis

@dataclass
class ReflectionSession:
    user_id: str
    session_id: str
    started_at: datetime
    prompts: Dict[str, str]
    responses: Dict[str, str]
    completed: bool = False
    xp_earned: int = 0

class ReflectionLINEInterface:
    def __init__(self, growth_note_system: GrowthNoteSystem):
        self.growth_note_system = growth_note_system
        self.active_sessions: Dict[str, ReflectionSession] = {}
        self.reflection_time = time(22, 0)  # 22:00
        
    def create_reflection_prompt_message(self, user_id: str, user_context: Dict) -> Dict:
        """22:00の"""
        prompts = self.growth_note_system.generate_reflection_prompt(user_context)
        
        # ?
        session_id = f"reflection_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = ReflectionSession(
            user_id=user_id,
            session_id=session_id,
            started_at=datetime.now(),
            prompts={
                "current_problems": prompts.current_problems_prompt,
                "ideal_world": prompts.ideal_world_prompt,
                "ideal_emotions": prompts.ideal_emotions_prompt,
                "tomorrow_actions": prompts.tomorrow_actions_prompt
            },
            responses={}
        )
        self.active_sessions[user_id] = session
        
        return {
            "type": "flex",
            "altText": "?",
            "contents": {
                "type": "bubble",
                "size": "kilo",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "? ?",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "?",
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True,
                            "align": "center",
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": "#F8F9FA",
                    "paddingAll": "lg"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "4つ",
                            "weight": "bold",
                            "size": "md",
                            "color": "#2E3A59",
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        self._create_category_preview("?", "?"),
                        self._create_category_preview("?", "理"),
                        self._create_category_preview("?", "理"),
                        self._create_category_preview("?", "?"),
                        {
                            "type": "text",
                            "text": f"?: {prompts.estimated_time}",
                            "size": "xs",
                            "color": "#999999",
                            "margin": "md"
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
                                "label": f"? (+{prompts.xp_reward} XP)",
                                "data": f"action=start_reflection&session_id={session_id}"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": "action=skip_reflection"
                            },
                            "margin": "sm"
                        }
                    ],
                    "paddingAll": "lg"
                }
            }
        }
    
    def _create_category_preview(self, emoji: str, title: str) -> Dict:
        """カスタム"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": emoji,
                    "size": "sm",
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": title,
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "sm"
                }
            ],
            "margin": "sm"
        }
    
    def create_growth_note_form(self, user_id: str) -> Dict:
        """?"""
        session = self.active_sessions.get(user_id)
        if not session:
            return self._create_error_message("?")
        
        return {
            "type": "flex",
            "altText": "?",
            "contents": {
                "type": "carousel",
                "contents": [
                    self._create_form_bubble(
                        "? ?", 
                        "current_problems", 
                        session.prompts["current_problems"],
                        session.session_id
                    ),
                    self._create_form_bubble(
                        "? ?", 
                        "ideal_world", 
                        session.prompts["ideal_world"],
                        session.session_id
                    ),
                    self._create_form_bubble(
                        "? ?", 
                        "ideal_emotions", 
                        session.prompts["ideal_emotions"],
                        session.session_id
                    ),
                    self._create_form_bubble(
                        "? ?", 
                        "tomorrow_actions", 
                        session.prompts["tomorrow_actions"],
                        session.session_id
                    )
                ]
            }
        }
    
    def _create_form_bubble(self, title: str, field_name: str, prompt: str, session_id: str) -> Dict:
        """?"""
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                        "color": "#2E3A59"
                    }
                ],
                "backgroundColor": "#F8F9FA",
                "paddingAll": "md"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": prompt,
                        "size": "sm",
                        "wrap": True,
                        "color": "#666666",
                        "margin": "md"
                    }
                ],
                "paddingAll": "md"
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
                            "data": f"action=input_reflection&field={field_name}&session_id={session_id}"
                        }
                    }
                ],
                "paddingAll": "md"
            }
        }
    
    def create_input_form(self, field_name: str, prompt: str, session_id: str) -> Dict:
        """?"""
        field_titles = {
            "current_problems": "? ?",
            "ideal_world": "? 理",
            "ideal_emotions": "? 理",
            "tomorrow_actions": "? ?"
        }
        
        return {
            "type": "flex",
            "altText": f"{field_titles.get(field_name, '?')}の",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": field_titles.get(field_name, "?"),
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59"
                        }
                    ],
                    "backgroundColor": "#F8F9FA",
                    "paddingAll": "lg"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": prompt,
                            "size": "sm",
                            "wrap": True,
                            "color": "#666666",
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "?",
                            "size": "xs",
                            "color": "#999999",
                            "margin": "lg"
                        }
                    ],
                    "paddingAll": "lg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "入力",
                            "size": "xs",
                            "color": "#999999",
                            "align": "center"
                        }
                    ],
                    "paddingAll": "md"
                }
            }
        }
    
    def process_reflection_input(self, user_id: str, field_name: str, response_text: str) -> Dict:
        """?"""
        session = self.active_sessions.get(user_id)
        if not session:
            return self._create_error_message("?")
        
        # ?
        session.responses[field_name] = response_text
        
        # ?
        completed_fields = len(session.responses)
        total_fields = 4
        
        if completed_fields < total_fields:
            # ま
            remaining_fields = [
                field for field in ["current_problems", "ideal_world", "ideal_emotions", "tomorrow_actions"]
                if field not in session.responses
            ]
            
            return {
                "type": "text",
                "text": f"? ?\n\n?: {completed_fields}/{total_fields}\n\n?: {len(remaining_fields)}?",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": f"action=continue_reflection&session_id={session.session_id}"
                            }
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "postback",
                                "label": "一般",
                                "data": f"action=pause_reflection&session_id={session.session_id}"
                            }
                        }
                    ]
                }
            }
        else:
            # ?
            return self._complete_reflection(user_id)
    
    def _complete_reflection(self, user_id: str) -> Dict:
        """?"""
        session = self.active_sessions.get(user_id)
        if not session:
            return self._create_error_message("?")
        
        # ?
        analysis = self.growth_note_system.process_reflection(session.responses)
        xp_earned = self.growth_note_system.calculate_reflection_xp(analysis)
        
        # ?
        session.completed = True
        session.xp_earned = xp_earned
        
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
                            "text": "? ?",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": "#E8F5E8",
                    "paddingAll": "lg"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"?XP: +{xp_earned} XP",
                            "weight": "bold",
                            "size": "md",
                            "color": "#FFC857",
                            "align": "center"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "?:",
                            "weight": "bold",
                            "size": "sm",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": f"?: {self._get_emotion_display(analysis.emotional_tone)}",
                            "size": "sm",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": f"?: {self._get_action_display(analysis.action_orientation)}",
                            "size": "sm",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": "?",
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True,
                            "margin": "lg"
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
                            "color": "#2E3A59",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": "action=view_story"
                            }
                        }
                    ],
                    "paddingAll": "lg"
                }
            }
        }
    
    def _get_emotion_display(self, emotional_tone) -> str:
        """?"""
        emotion_map = {
            "very_positive": "と ?",
            "positive": "? ?",
            "neutral": "? ?",
            "negative": "? ?",
            "very_negative": "と ?"
        }
        return emotion_map.get(emotional_tone.value, "?")
    
    def _get_action_display(self, action_orientation) -> str:
        """?"""
        action_map = {
            "high": "? ?",
            "medium": "? ?",
            "low": "? ?"
        }
        return action_map.get(action_orientation.value, "?")
    
    def create_reflection_reminder(self, user_id: str, missed_days: int) -> Dict:
        """2?"""
        encouragement_messages = [
            "?",
            "?",
            "?",
            "?",
            "あ"
        ]
        
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
                            "text": "? ?",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#2E3A59",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": "#FFF8E1",
                    "paddingAll": "lg"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": random.choice(encouragement_messages),
                            "size": "sm",
                            "wrap": True,
                            "color": "#666666"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": f"?{missed_days}?",
                            "size": "sm",
                            "color": "#999999",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "無",
                            "size": "sm",
                            "wrap": True,
                            "color": "#666666",
                            "margin": "sm"
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
                                "data": "action=start_reflection_now"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "?",
                                "data": "action=postpone_reflection"
                            },
                            "margin": "sm"
                        }
                    ],
                    "paddingAll": "lg"
                }
            }
        }
    
    def _create_error_message(self, message: str) -> Dict:
        """エラー"""
        return {
            "type": "text",
            "text": f"? エラー: {message}\n\nも"
        }
    
    def get_session_status(self, user_id: str) -> Optional[ReflectionSession]:
        """?"""
        return self.active_sessions.get(user_id)
    
    def cleanup_old_sessions(self, hours: int = 24):
        """?"""
        current_time = datetime.now()
        expired_sessions = []
        
        for user_id, session in self.active_sessions.items():
            if (current_time - session.started_at).total_seconds() > hours * 3600:
                expired_sessions.append(user_id)
        
        for user_id in expired_sessions:
            del self.active_sessions[user_id]
        
        return len(expired_sessions)

# 使用
def demo_line_bot_integration():
    """LINE Bot?"""
    growth_note_system = GrowthNoteSystem()
    line_interface = ReflectionLINEInterface(growth_note_system)
    
    # ?
    user_context = {
        "mood": 3,
        "completed_tasks": 2,
        "recent_struggles": ["social"]
    }
    
    # 22:00の
    prompt_message = line_interface.create_reflection_prompt_message("user123", user_context)
    print("=== 22:00プレビュー ===")
    print(json.dumps(prompt_message, ensure_ascii=False, indent=2))
    
    # ?
    form_message = line_interface.create_growth_note_form("user123")
    print("\n=== ? ===")
    print(json.dumps(form_message, ensure_ascii=False, indent=2))
    
    # 入力
    print("\n=== 入力 ===")
    
    # 1つ
    response1 = line_interface.process_reflection_input(
        "user123", 
        "current_problems", 
        "?"
    )
    print("?1?:", response1["text"])
    
    # ?
    line_interface.process_reflection_input("user123", "ideal_world", "?")
    line_interface.process_reflection_input("user123", "ideal_emotions", "?")
    
    # ?
    completion_response = line_interface.process_reflection_input(
        "user123", 
        "tomorrow_actions", 
        "?"
    )
    print("\n=== ? ===")
    print(json.dumps(completion_response, ensure_ascii=False, indent=2))
    
    return line_interface

if __name__ == "__main__":
    demo_line_bot_integration()