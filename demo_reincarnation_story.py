#!/usr/bin/env python3
"""
? デフォルト

60?
"""

import sys
import os
import asyncio
from datetime import datetime

def demo_story_content():
    """ストーリー"""
    print("? ? デフォルト")
    print("=" * 60)
    
    # Story DAGか
    sys.path.append(os.path.join('services', 'story-dag'))
    from main import db
    
    # ?
    reincarnation_chapter = None
    for chapter in db.chapters.values():
        if "?" in chapter.title or "?" in chapter.title:
            reincarnation_chapter = chapter
            break
    
    if reincarnation_chapter:
        print(f"? Chapter: {reincarnation_chapter.title}")
        print(f"? Description: {reincarnation_chapter.description}")
        print(f"? Therapeutic Focus: {', '.join(reincarnation_chapter.therapeutic_focus)}")
        print()
        
        # ?
        chapter_nodes = [n for n in db.nodes.values() if n.chapter_id == reincarnation_chapter.chapter_id]
        chapter_nodes.sort(key=lambda x: x.node_type.value)  # opening, choice, resolution?
        
        for i, node in enumerate(chapter_nodes, 1):
            print(f"? Scene {i}: {node.title} ({node.node_type.value})")
            print("-" * 50)
            print(node.content)
            print()
            
            if node.companion_effects:
                print(f"? Companion Effects: {node.companion_effects}")
            if node.mood_effects:
                print(f"? Mood Effects: {node.mood_effects}")
            if node.therapeutic_tags:
                print(f"? Therapeutic Tags: {', '.join(node.therapeutic_tags)}")
            print()

async def demo_ai_generation():
    """AI?"""
    print("? AI Story Generation デフォルト")
    print("=" * 60)
    
    sys.path.append(os.path.join('services', 'ai-story'))
    from main import deepseek_client
    
    scenarios = [
        ("opening", "?"),
        ("challenge", "?"),
        ("companion", "?"),
        ("level", "レベル")
    ]
    
    for scenario, description in scenarios:
        print(f"? {description}")
        print("-" * 40)
        
        response = await deepseek_client._mock_deepseek_response(scenario, None)
        content = response["content"]
        
        print(content)
        print(f"? Generation time: {response['generation_time_ms']}ms")
        print()

def demo_task_integration():
    """タスク"""
    print("? Task Integration デフォルト")
    print("=" * 60)
    
    sys.path.append(os.path.join('services', 'task-story-integration'))
    from main import ServiceIntegration, StoryChoiceHook
    
    service = ServiceIntegration()
    
    # ?
    reincarnation_choices = [
        "勇",
        "?", 
        "?",
        "?"
    ]
    
    for i, choice_text in enumerate(reincarnation_choices, 1):
        print(f"? Choice {i}: {choice_text}")
        print("-" * 50)
        
        choice_hook = StoryChoiceHook(
            choice_id=f"reincarnation_choice_{i}",
            choice_text=choice_text,
            habit_tag=f"hero_action_{i}",
            therapeutic_weight=1.2
        )
        
        task_data = service._build_task_from_choice(choice_hook)
        
        print(f"? Generated Task:")
        print(f"   Type: {task_data['task_type']}")
        print(f"   Title: {task_data['title']}")
        print(f"   Description: {task_data['description']}")
        print(f"   Crystal Attribute: {task_data['primary_crystal_attribute']}")
        print(f"   Difficulty: {task_data['difficulty']}")
        print()

def demo_therapeutic_impact():
    """治療"""
    print("? Therapeutic Impact デフォルト")
    print("=" * 60)
    
    therapeutic_elements = {
        "? Second Chance Motivation": [
            "?60?",
            "?",
            "?"
        ],
        "? Growth Mindset": [
            "?",
            "? = ?",
            "?"
        ],
        "? Social Support": [
            "?",
            "?",
            "?"
        ],
        "? Meta-Gaming Effect": [
            "? = ?",
            "?",
            "?"
        ]
    }
    
    for category, examples in therapeutic_elements.items():
        print(f"{category}")
        for example in examples:
            print(f"   ? {example}")
        print()

def demo_user_scenarios():
    """ユーザー"""
    print("? User Scenarios デフォルト")
    print("=" * 60)
    
    user_personas = [
        {
            "name": "? (35?, ?)",
            "background": "?",
            "regrets": ["ストーリー", "?"],
            "reincarnation_appeal": "60?"
        },
        {
            "name": "? (50?, ?)",
            "background": "?",
            "regrets": ["?", "自動"],
            "reincarnation_appeal": "?"
        },
        {
            "name": "? (28?, ?)",
            "background": "?",
            "regrets": ["や", "?"],
            "reincarnation_appeal": "レベル"
        }
    ]
    
    for persona in user_personas:
        print(f"? {persona['name']}")
        print(f"   Background: {persona['background']}")
        print(f"   Regrets: {', '.join(persona['regrets'])}")
        print(f"   ? Appeal: {persona['reincarnation_appeal']}")
        print()

def demo_game_revolution():
    """ゲーム"""
    print("? Game Industry Revolution デフォルト")
    print("=" * 60)
    
    revolution_points = [
        {
            "title": "? ?",
            "description": "エラー",
            "limitation": "?"
        },
        {
            "title": "? ?",
            "description": "治療",
            "limitation": "?"
        },
        {
            "title": "? ?",
            "description": "治療",
            "innovation": "ゲーム = ?"
        }
    ]
    
    for point in revolution_points:
        print(f"{point['title']}")
        print(f"   Description: {point['description']}")
        if 'limitation' in point:
            print(f"   ? Limitation: {point['limitation']}")
        if 'innovation' in point:
            print(f"   ? Innovation: {point['innovation']}")
        print()
    
    print("? ?:")
    revolutionary_features = [
        "60?",
        "?",
        "?",
        "?",
        "治療",
        "?"
    ]
    
    for feature in revolutionary_features:
        print(f"   ? {feature}")
    print()
    
    print("? ?:")
    market_impact = [
        "ゲーム: ?",
        "?: ゲーム",
        "?: ?",
        "?: ?",
        "?: アプリ"
    ]
    
    for impact in market_impact:
        print(f"   ? {impact}")

async def main():
    """メイン"""
    
    print("?" * 30)
    print("? ?")
    print("? ゲーム")
    print("?" * 30)
    print()
    
    # デフォルト
    demo_sections = [
        ("Story Content", demo_story_content),
        ("AI Generation", demo_ai_generation),
        ("Task Integration", demo_task_integration),
        ("Therapeutic Impact", demo_therapeutic_impact),
        ("User Scenarios", demo_user_scenarios),
        ("Game Revolution", demo_game_revolution)
    ]
    
    for section_name, demo_func in demo_sections:
        if asyncio.iscoroutinefunction(demo_func):
            await demo_func()
        else:
            demo_func()
        
        input("Press Enter to continue to next section...")
        print("\n" + "="*80 + "\n")
    
    # ?
    print("? デフォルト")
    print()
    print("? こ")
    print("   ? プレビュー60?")
    print("   ? ?")
    print("   ? ?")
    print("   ? ?")
    print("   ? 治療")
    print()
    print("? ま = ?")
    print("? ?")
    print("? ゲーム")

if __name__ == "__main__":
    asyncio.run(main())