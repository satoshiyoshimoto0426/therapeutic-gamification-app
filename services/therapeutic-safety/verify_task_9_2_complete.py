#!/usr/bin/env python3
"""
Task 9.2: CBT?
?7.2の
"""

import sys
import os

# ?
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from main import CBTInterventionEngine, TherapeuticSafetyService

def verify_negative_pattern_detection():
    """?"""
    print("1. ?...")
    
    cbt_engine = CBTInterventionEngine()
    
    # ?
    required_distortions = [
        "all_or_nothing",
        "catastrophizing", 
        "personalization",
        "mind_reading",
        "emotional_reasoning"
    ]
    
    implemented_distortions = list(cbt_engine.cognitive_distortions.keys())
    
    for distortion in required_distortions:
        if distortion in implemented_distortions:
            print(f"  ? {distortion} - 実装")
        else:
            print(f"  ? {distortion} - ?")
            return False
    
    # ?
    test_content = "い"
    patterns = cbt_engine.detect_negative_thought_patterns(test_content)
    
    if len(patterns) > 0:
        print(f"  ? ? - ? ({len(patterns)}?)")
        return True
    else:
        print("  ? ? - ?")
        return False

def verify_story_break_dialog():
    """ストーリー"""
    print("2. ストーリー...")
    
    cbt_engine = CBTInterventionEngine()
    
    # ?
    required_templates = [
        "gentle_interruption",
        "cognitive_challenge",
        "reframing_support",
        "encouragement"
    ]
    
    implemented_templates = list(cbt_engine.story_break_templates.keys())
    
    for template in required_templates:
        if template in implemented_templates:
            print(f"  ? {template} - 実装")
        else:
            print(f"  ? {template} - ?")
            return False
    
    # ?
    test_patterns = [{
        "type": "all_or_nothing",
        "name": "?",
        "confidence": 0.8,
        "severity": "high"
    }]
    
    user_context = {"character_name": "ユーザー", "recent_mood": 2}
    story_break = cbt_engine.generate_story_break_dialog(test_patterns, user_context)
    
    if story_break["intervention_needed"] and story_break["dialog"]:
        print(f"  ? ? - ?")
        return True
    else:
        print("  ? ? - ?")
        return False

def verify_cognitive_reframing():
    """?"""
    print("3. ?...")
    
    cbt_engine = CBTInterventionEngine()
    
    # ?
    required_techniques = [
        "all_or_nothing",
        "catastrophizing",
        "personalization", 
        "mind_reading",
        "emotional_reasoning"
    ]
    
    implemented_techniques = list(cbt_engine.reframing_techniques.keys())
    
    for technique in required_techniques:
        if technique in implemented_techniques:
            print(f"  ? {technique} - 実装")
        else:
            print(f"  ? {technique} - ?")
            return False
    
    # ?
    test_thought = "い"
    reframing = cbt_engine.generate_cognitive_reframing(test_thought, "all_or_nothing")
    
    if (reframing["reframed_thoughts"] and 
        reframing["reflection_questions"] and
        reframing["technique"]):
        print(f"  ? ? - ?")
        return True
    else:
        print("  ? ? - ?")
        return False

def verify_integration_functionality():
    """CBT?"""
    print("4. CBT?...")
    
    cbt_engine = CBTInterventionEngine()
    
    # ?
    test_content = "い"
    user_context = {"character_name": "ユーザー", "recent_mood": 2}
    
    intervention = cbt_engine.create_cbt_intervention(test_content, user_context)
    
    required_keys = [
        "detected_patterns",
        "story_break_dialog", 
        "cognitive_reframing",
        "intervention_recommended",
        "severity"
    ]
    
    for key in required_keys:
        if key in intervention:
            print(f"  ? {key} - 実装")
        else:
            print(f"  ? {key} - ?")
            return False
    
    # 治療
    therapeutic_response = cbt_engine.generate_therapeutic_response(test_content, user_context)
    
    if (therapeutic_response["response_type"] and 
        therapeutic_response["message"] and
        "intervention_needed" in therapeutic_response):
        print(f"  ? 治療 - ?")
        return True
    else:
        print("  ? 治療 - ?")
        return False

def verify_comprehensive_safety_service():
    """?"""
    print("5. ?...")
    
    safety_service = TherapeuticSafetyService()
    
    # ?
    if hasattr(safety_service, 'content_moderation'):
        print("  ? コア - ?")
    else:
        print("  ? コア - ?")
        return False
    
    if hasattr(safety_service, 'cbt_intervention'):
        print("  ? CBT? - ?")
    else:
        print("  ? CBT? - ?")
        return False
    
    # comprehensive_safety_analysis メイン
    if hasattr(safety_service, 'comprehensive_safety_analysis'):
        print("  ? ? - 実装")
        return True
    else:
        print("  ? ? - ?")
        return False

def main():
    """Task 9.2の"""
    print("=== Task 9.2: CBT? ===")
    print("?7.2: ?")
    print()
    
    verification_results = []
    
    # ?
    verification_results.append(verify_negative_pattern_detection())
    verification_results.append(verify_story_break_dialog())
    verification_results.append(verify_cognitive_reframing())
    verification_results.append(verify_integration_functionality())
    verification_results.append(verify_comprehensive_safety_service())
    
    print()
    print("=== 検証 ===")
    
    passed = sum(verification_results)
    total = len(verification_results)
    
    print(f"検証: {total}")
    print(f"成: {passed}")
    print(f"?: {total - passed}")
    print(f"成: {passed/total*100:.1f}%")
    
    if passed == total:
        print()
        print("? Task 9.2: CBT?")
        print()
        print("実装:")
        print("? ? (5?)")
        print("? 文字")
        print("? CBT?")
        print("? ?")
        print("? ?")
        print()
        print("?7.2の")
        return True
    else:
        print()
        print("?  一般")
        print("実装")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)