"""
Mobile-optimized LINE Flex Message components
Provides optimized Flex Message layouts for mobile devices with ADHD considerations
"""

from linebot.models import (
    FlexSendMessage, BubbleContainer, CarouselContainer, BoxComponent,
    TextComponent, ButtonComponent, SeparatorComponent,
    ImageComponent, FillerComponent, PostbackAction, URIAction, MessageAction
)
from typing import List, Dict, Optional, Any
import math

class MobileFlexOptimizer:
    """Mobile-optimized Flex Message builder with ADHD considerations"""
    
    def __init__(self):
        # Mobile-optimized sizing
        self.mobile_sizes = {
            "bubble": "kilo",  # Compact size for mobile
            "text_primary": "md",
            "text_secondary": "sm", 
            "text_caption": "xs",
            "button_height": "sm",
            "spacing": "xs"
        }
        
        # ADHD-friendly colors
        self.colors = {
            "primary": "#2E3A59",      # Calming base color
            "accent": "#FFC857",       # Achievement color
            "success": "#2E7D32",      # Task completion
            "warning": "#FF6B9D",      # Heart Crystal
            "info": "#805AD5",         # Story/choice
            "muted": "#718096",        # Secondary text
            "background": "#F7FAFC"    # Light background
        }
    
    def create_3x3_mandala_carousel(self, items: List[Dict], title: str = "Mandala") -> FlexSendMessage:
        """Create 3x3 Mandala layout using carousel bubbles"""
        # Limit to 9 items for 3x3 grid
        grid_items = items[:9]
        
        # Create header bubble
        header_bubble = self._create_header_bubble(title)
        
        # Create 3x3 grid bubbles (3 rows)
        grid_bubbles = []
        for i in range(0, 9, 3):
            row_items = grid_items[i:i+3] if i < len(grid_items) else []
            
            # Fill empty slots
            while len(row_items) < 3:
                row_items.append({"type": "empty"})
            
            row_bubble = self._create_mandala_row_bubble(row_items, i // 3)
            grid_bubbles.append(row_bubble)
        
        # Combine all bubbles
        all_bubbles = [header_bubble] + grid_bubbles
        carousel = CarouselContainer(contents=all_bubbles)
        
        return FlexSendMessage(
            alt_text=f"? {title} - モデル",
            contents=carousel
        )
    
    def _create_header_bubble(self, title: str) -> BubbleContainer:
        """Create header bubble for Mandala grid"""
        return BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing=self.mobile_sizes["spacing"],
                paddingAll="md",
                contents=[
                    TextComponent(
                        text=f"? {title}",
                        weight="bold",
                        size="lg",
                        color=self.colors["primary"],
                        align="center"
                    ),
                    TextComponent(
                        text="タスク",
                        size=self.mobile_sizes["text_caption"],
                        color=self.colors["muted"],
                        align="center"
                    ),
                    SeparatorComponent(margin="sm")
                ]
            )
        )
    
    def _create_mandala_row_bubble(self, row_items: List[Dict], row_index: int) -> BubbleContainer:
        """Create a row bubble for 3x3 Mandala grid"""
        row_contents = []
        
        for item in row_items:
            if item.get("type") == "empty":
                cell = self._create_empty_mandala_cell()
            else:
                cell = self._create_mandala_cell(item)
            row_contents.append(cell)
        
        return BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="horizontal",
                spacing=self.mobile_sizes["spacing"],
                paddingAll="xs",
                contents=row_contents
            )
        )
    
    def _create_mandala_cell(self, item: Dict) -> BoxComponent:
        """Create individual Mandala cell optimized for mobile touch"""
        item_type = item.get("type", "task")
        title = item.get("title", "?")
        item_id = item.get("id", "")
        
        # Emoji mapping for different item types
        emoji_map = {
            "task": "?",
            "routine": "?", 
            "one_shot": "?",
            "skill_up": "?",
            "social": "?",
            "story": "?",
            "choice": "?",
            "growth": "?",
            "challenge": "?",
            "reward": "?"
        }
        
        emoji = emoji_map.get(item_type, "?")
        
        # Truncate title for mobile display
        display_title = title[:6] + ("..." if len(title) > 6 else "")
        
        # Determine background color based on status
        bg_color = self.colors["background"]
        if item.get("completed"):
            bg_color = "#E8F5E8"  # Light green for completed
        elif item.get("locked"):
            bg_color = "#F0F0F0"  # Gray for locked
        
        return BoxComponent(
            layout="vertical",
            spacing="xs",
            paddingAll="xs",
            cornerRadius="sm",
            contents=[
                TextComponent(
                    text=emoji,
                    size=self.mobile_sizes["text_primary"],
                    align="center"
                ),
                TextComponent(
                    text=display_title,
                    size=self.mobile_sizes["text_caption"],
                    align="center",
                    wrap=True,
                    maxLines=1,
                    color=self.colors["primary"]
                ),
                # Progress indicator if applicable
                self._create_progress_indicator(item.get("progress", 0))
            ],
            action=PostbackAction(
                data=f"mandala_item_{item_id}"
            )
        )
    
    def _create_empty_mandala_cell(self) -> BoxComponent:
        """Create empty cell for Mandala grid"""
        return BoxComponent(
            layout="vertical",
            spacing="xs",
            paddingAll="xs",
            cornerRadius="sm",
            contents=[
                TextComponent(
                    text="?",
                    size=self.mobile_sizes["text_primary"],
                    align="center",
                    color="#CBD5E0"
                ),
                TextComponent(
                    text="?",
                    size=self.mobile_sizes["text_caption"],
                    align="center",
                    color="#A0AEC0"
                )
            ]
        )
    
    def _create_progress_indicator(self, progress: int) -> TextComponent:
        """Create progress indicator for mobile display"""
        if progress <= 0:
            return TextComponent(text="", size="xxs")
        
        # Create simple dot-based progress (max 5 dots)
        filled_dots = min(5, progress // 20)
        empty_dots = 5 - filled_dots
        
        progress_text = "?" * filled_dots + "?" * empty_dots
        
        return TextComponent(
            text=progress_text,
            size="xxs",
            align="center",
            color=self.colors["accent"]
        )
    
    def create_compact_task_bubble(self, task: Dict) -> BubbleContainer:
        """Create compact task bubble optimized for mobile"""
        task_title = task.get("title", "タスク")
        task_type = task.get("type", "routine")
        difficulty = task.get("difficulty", 1)
        xp_reward = task.get("xp_reward", 10)
        
        # Task type styling
        type_config = {
            "routine": {"emoji": "?", "color": self.colors["info"]},
            "one_shot": {"emoji": "?", "color": self.colors["warning"]},
            "skill_up": {"emoji": "?", "color": self.colors["success"]},
            "social": {"emoji": "?", "color": self.colors["accent"]}
        }
        
        config = type_config.get(task_type, type_config["routine"])
        
        return BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing=self.mobile_sizes["spacing"],
                paddingAll="sm",
                contents=[
                    # Header with emoji and type
                    BoxComponent(
                        layout="horizontal",
                        spacing="xs",
                        contents=[
                            TextComponent(
                                text=config["emoji"],
                                size=self.mobile_sizes["text_primary"],
                                flex=0
                            ),
                            TextComponent(
                                text=task_title,
                                size=self.mobile_sizes["text_primary"],
                                weight="bold",
                                wrap=True,
                                maxLines=2,
                                flex=1
                            )
                        ]
                    ),
                    
                    SeparatorComponent(margin="xs"),
                    
                    # Task details
                    BoxComponent(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            TextComponent(
                                text=f"?: {'?' * difficulty}",
                                size=self.mobile_sizes["text_caption"],
                                color=self.colors["muted"],
                                flex=1
                            ),
                            TextComponent(
                                text=f"+{xp_reward} XP",
                                size=self.mobile_sizes["text_caption"],
                                color=self.colors["accent"],
                                weight="bold",
                                flex=0
                            )
                        ]
                    ),
                    
                    FillerComponent(flex=0),
                    
                    # Action button
                    ButtonComponent(
                        style="primary",
                        height=self.mobile_sizes["button_height"],
                        color=config["color"],
                        action=PostbackAction(
                            label="?",
                            data=f"complete_task_{task.get('id', '')}"
                        )
                    )
                ]
            )
        )
    
    def create_story_choice_carousel(self, story_data: Dict) -> FlexSendMessage:
        """Create story choice carousel optimized for mobile"""
        story_title = story_data.get("title", "?")
        story_content = story_data.get("content", "")
        choices = story_data.get("choices", [])
        
        # Main story bubble
        story_bubble = BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing=self.mobile_sizes["spacing"],
                paddingAll="md",
                contents=[
                    TextComponent(
                        text=f"? {story_title}",
                        weight="bold",
                        size="lg",
                        color=self.colors["primary"]
                    ),
                    SeparatorComponent(margin="sm"),
                    TextComponent(
                        text=self._format_story_content_mobile(story_content),
                        size=self.mobile_sizes["text_secondary"],
                        wrap=True,
                        lineSpacing="md",
                        color=self.colors["primary"]
                    ),
                    FillerComponent(flex=1),
                    TextComponent(
                        text="? ?",
                        size=self.mobile_sizes["text_caption"],
                        color=self.colors["info"],
                        align="center"
                    )
                ]
            )
        )
        
        # Choice bubbles (limit to 6 for mobile optimization)
        choice_bubbles = []
        for choice in choices[:6]:
            choice_bubble = self._create_story_choice_bubble(choice)
            choice_bubbles.append(choice_bubble)
        
        # Combine all bubbles
        all_bubbles = [story_bubble] + choice_bubbles
        carousel = CarouselContainer(contents=all_bubbles)
        
        return FlexSendMessage(
            alt_text=f"? {story_title} - ?",
            contents=carousel
        )
    
    def _create_story_choice_bubble(self, choice: Dict) -> BubbleContainer:
        """Create individual story choice bubble"""
        choice_text = choice.get("text", "?")
        choice_id = choice.get("id", "")
        xp_reward = choice.get("xp_reward", 0)
        
        # Determine choice type
        has_task = choice.get("real_task_id") is not None
        has_habit = choice.get("habit_tag") is not None
        
        choice_emoji = "?"
        if has_task:
            choice_emoji = "?"
        elif has_habit:
            choice_emoji = "?"
        
        return BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing=self.mobile_sizes["spacing"],
                paddingAll="sm",
                contents=[
                    TextComponent(
                        text=choice_emoji,
                        size="xl",
                        align="center",
                        color=self.colors["info"]
                    ),
                    TextComponent(
                        text=choice_text,
                        size=self.mobile_sizes["text_secondary"],
                        weight="bold",
                        wrap=True,
                        maxLines=3,
                        align="center",
                        color=self.colors["primary"]
                    ),
                    FillerComponent(flex=1),
                    
                    # XP reward if applicable
                    TextComponent(
                        text=f"+{xp_reward} XP" if xp_reward > 0 else "",
                        size=self.mobile_sizes["text_caption"],
                        color=self.colors["accent"],
                        align="center"
                    ) if xp_reward > 0 else FillerComponent(flex=0),
                    
                    FillerComponent(flex=0),
                    
                    ButtonComponent(
                        style="primary",
                        height=self.mobile_sizes["button_height"],
                        color=self.colors["info"],
                        action=PostbackAction(
                            label="こ",
                            data=f"story_choice_{choice_id}"
                        )
                    )
                ]
            )
        )
    
    def _format_story_content_mobile(self, content: str) -> str:
        """Format story content for mobile readability"""
        # Split into sentences and limit length
        sentences = content.split('?')
        formatted_sentences = []
        
        for sentence in sentences[:3]:  # Max 3 sentences for mobile
            if sentence.strip():
                formatted_sentences.append(sentence.strip() + '?')
        
        formatted_content = '\n\n'.join(formatted_sentences)
        
        # Add continuation indicator if truncated
        if len(sentences) > 3:
            formatted_content += "\n\n? ?..."
        
        return formatted_content
    
    def create_achievement_notification(self, achievement: Dict) -> FlexSendMessage:
        """Create achievement notification optimized for mobile"""
        achievement_title = achievement.get("title", "?")
        achievement_description = achievement.get("description", "?")
        xp_earned = achievement.get("xp_earned", 0)
        badge_emoji = achievement.get("emoji", "?")
        
        bubble = BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing="md",
                paddingAll="lg",

                contents=[
                    TextComponent(
                        text=badge_emoji,
                        size="xxl",
                        align="center"
                    ),
                    TextComponent(
                        text="? ?",
                        weight="bold",
                        size="lg",
                        color=self.colors["success"],
                        align="center"
                    ),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text=achievement_title,
                        size=self.mobile_sizes["text_primary"],
                        weight="bold",
                        wrap=True,
                        align="center",
                        color=self.colors["primary"]
                    ),
                    TextComponent(
                        text=achievement_description,
                        size=self.mobile_sizes["text_secondary"],
                        wrap=True,
                        align="center",
                        color=self.colors["muted"]
                    ),
                    FillerComponent(flex=1),
                    BoxComponent(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            TextComponent(
                                text="?XP:",
                                size=self.mobile_sizes["text_secondary"],
                                color=self.colors["muted"],
                                flex=1
                            ),
                            TextComponent(
                                text=f"+{xp_earned} XP",
                                size=self.mobile_sizes["text_secondary"],
                                weight="bold",
                                color=self.colors["accent"],
                                flex=1,
                                align="end"
                            )
                        ]
                    ) if xp_earned > 0 else FillerComponent(flex=0)
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text=f"? {achievement_title} ?",
            contents=bubble
        )
    
    def create_daily_summary_bubble(self, summary_data: Dict) -> FlexSendMessage:
        """Create daily summary bubble optimized for mobile"""
        completed_tasks = summary_data.get("completed_tasks", 0)
        total_xp = summary_data.get("total_xp", 0)
        level_progress = summary_data.get("level_progress", 0)
        mood_score = summary_data.get("mood_score", 3)
        
        # Mood emoji mapping
        mood_emojis = ["?", "?", "?", "?", "?"]
        mood_emoji = mood_emojis[min(4, max(0, mood_score - 1))]
        
        bubble = BubbleContainer(
            size=self.mobile_sizes["bubble"],
            body=BoxComponent(
                layout="vertical",
                spacing="md",
                paddingAll="lg",
                contents=[
                    TextComponent(
                        text="? ?",
                        weight="bold",
                        size="lg",
                        color=self.colors["primary"],
                        align="center"
                    ),
                    SeparatorComponent(margin="md"),
                    
                    # Stats grid
                    BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        contents=[
                            self._create_stat_row("? ?", f"{completed_tasks}?"),
                            self._create_stat_row("? ?XP", f"{total_xp} XP"),
                            self._create_stat_row("? レベル", f"{level_progress}%"),
                            self._create_stat_row("? ?", f"{mood_emoji} {mood_score}/5")
                        ]
                    ),
                    
                    FillerComponent(flex=1),
                    
                    TextComponent(
                        text="?",
                        size=self.mobile_sizes["text_secondary"],
                        color=self.colors["success"],
                        align="center"
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="? ?",
            contents=bubble
        )
    
    def _create_stat_row(self, label: str, value: str) -> BoxComponent:
        """Create stat row for summary display"""
        return BoxComponent(
            layout="horizontal",
            spacing="sm",
            contents=[
                TextComponent(
                    text=label,
                    size=self.mobile_sizes["text_secondary"],
                    color=self.colors["muted"],
                    flex=2
                ),
                TextComponent(
                    text=value,
                    size=self.mobile_sizes["text_secondary"],
                    weight="bold",
                    color=self.colors["primary"],
                    flex=1,
                    align="end"
                )
            ]
        )

# Global instance for easy access
mobile_flex = MobileFlexOptimizer()