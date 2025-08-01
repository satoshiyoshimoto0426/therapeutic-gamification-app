#!/usr/bin/env python3
"""
CBT?
"""

import sys
import os

# ?
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from main import CBTInterventionEngine

def debug_pattern_detection():
    """?"""
    cbt_engine = CBTInterventionEngine()
    
    test_cases = [
        ("?", "い"),
        ("?", "こ"),
        ("?", "?"),
        ("?", "み"),
        ("?", "?")
    ]
    
    for pattern_name, content in test_cases:
        print(f"\n=== {pattern_name} ===")
        print(f"?: {content}")
        
        try:
            patterns = cbt_engine.detect_negative_thought_patterns(content)
            print(f"検証: {len(patterns)}")
            
            for pattern in patterns:
                print(f"  - タスク: {pattern['type']}")
                print(f"    ?: {pattern['name']}")
                print(f"    信頼: {pattern['confidence']}")
                print(f"    ?: {pattern['severity']}")
                print(f"    ?: {pattern['matches']}")
                
        except Exception as e:
            import traceback
            print(f"エラー: {str(e)}")
            print(f"?: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_pattern_detection()