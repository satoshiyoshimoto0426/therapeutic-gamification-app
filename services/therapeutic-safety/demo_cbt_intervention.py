#!/usr/bin/env python3
"""
CBT?
Task 9.2の
"""

import asyncio
import sys
import os

# ?
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from main import CBTInterventionEngine, TherapeuticSafetyService

def demo_negative_pattern_detection():
    """?"""
    print("=== ? ===")
    
    cbt_engine = CBTInterventionEngine()
    
    test_cases = [
        "い",
        "こ",
        "?",
        "み",
        "?"
    ]
    
    for i, content in enumerate(test_cases, 1):
        print(f"\n? {i}?")
        print(f"入力: {content}")
        
        patterns = cbt_engine.detect_negative_thought_patterns(content)
        
        if patterns:
            print("検証:")
            for pattern in patterns:
                print(f"  ? {pattern['name']} (信頼: {pattern['confidence']:.2f}, ?: {pattern['severity']})")
        else:
            print("  ?")

def demo_story_break_dialog():
    """ストーリー"""
    print("\n=== ストーリー ===")
    
    cbt_engine = CBTInterventionEngine()
    
    user_context = {
        "character_name": "ユーザー",
        "recent_mood": 2
    }
    
    test_content = "い"
    print(f"入力: {test_content}")
    
    patterns = cbt_engine.detect_negative_thought_patterns(test_content)
    story_break = cbt_engine.generate_story_break_dialog(patterns, user_context)
    
    if story_break["intervention_needed"]:
        print("\n?")
        print(story_break["dialog"])
        print(f"\n?: {story_break['primary_distortion']}")
        print(f"信頼: {story_break['confidence']:.2f}")
    else:
        print("?")

def demo_cognitive_reframing():
    """?"""
    print("\n=== ? ===")
    
    cbt_engine = CBTInterventionEngine()
    
    test_cases = [
        ("い", "all_or_nothing"),
        ("こ", "catastrophizing"),
        ("?", "personalization")
    ]
    
    for thought, distortion_type in test_cases:
        print(f"\n?")
        print(f"?: {thought}")
        
        reframing = cbt_engine.generate_cognitive_reframing(thought, distortion_type)
        
        print(f"?: {reframing['distortion_type']}")
        print(f"使用: {reframing['technique']}")
        
        print("?:")
        for i, reframed in enumerate(reframing['reframed_thoughts'], 1):
            print(f"  {i}. {reframed}")
        
        print("?:")
        for i, question in enumerate(reframing['reflection_questions'], 1):
            print(f"  {i}. {question}")

async def demo_comprehensive_intervention():
    """?CBT?"""
    print("\n=== ?CBT? ===")
    
    safety_service = TherapeuticSafetyService()
    
    user_context = {
        "uid": "demo_user",
        "character_name": "ユーザー",
        "recent_mood": 1,
        "recent_mood_history": [1, 2, 1]
    }
    
    test_content = "も"
    print(f"入力: {test_content}")
    
    result = await safety_service.comprehensive_safety_analysis(test_content, user_context)
    
    print("\n?")
    safety = result["safety_analysis"]
    print(f"コア: {'安全' if safety['content_safe'] else '?'}")
    print(f"総合: {safety['threat_level']}")
    print(f"エラー: {'は' if safety['escalation_required'] else 'い'}")
    
    print("\n?CBT?")
    cbt = result["cbt_analysis"]
    print(f"?: {'は' if cbt['intervention_recommended'] else 'い'}")
    print(f"?: {cbt['severity']}")
    
    if cbt["detected_patterns"]:
        print("検証:")
        for pattern in cbt["detected_patterns"]:
            print(f"  ? {pattern['name']} (信頼: {pattern['confidence']:.2f})")
    
    print("\n?")
    therapeutic = result["therapeutic_response"]
    print(f"?: {therapeutic['response_type']}")
    print(f"?: {'は' if therapeutic['intervention_needed'] else 'い'}")
    print("\n?:")
    print(therapeutic["message"])
    
    print(f"\n?")
    print(f"?: {result['recommended_action']}")

def demo_intervention_effectiveness():
    """?"""
    print("\n=== ? ===")
    
    cbt_engine = CBTInterventionEngine()
    
    original_content = "い"
    reframed_content = "?"
    
    print(f"?: {original_content}")
    print(f"?: {reframed_content}")
    
    effectiveness = cbt_engine.evaluate_intervention_effectiveness(
        original_content, reframed_content
    )
    
    print(f"\n?")
    print(f"?: {effectiveness['original_severity']:.2f}")
    print(f"?: {effectiveness['reframed_severity']:.2f}")
    print(f"?: {effectiveness['improvement_rate']:.1%}")
    print(f"?: {effectiveness['patterns_reduced']}")
    print(f"?: {'?' if effectiveness['intervention_effective'] else '?'}")

async def main():
    """メイン"""
    print("? CBT? デフォルト")
    print("Task 9.2: ?")
    print("=" * 80)
    
    # ?
    demo_negative_pattern_detection()
    demo_story_break_dialog()
    demo_cognitive_reframing()
    await demo_comprehensive_intervention()
    demo_intervention_effectiveness()
    
    print("\n" + "=" * 80)
    print("? CBT?")
    print("こ:")
    print("? ?")
    print("? 文字")
    print("? CBT?")
    print("? ?")
    print("? ?")

if __name__ == "__main__":
    asyncio.run(main())