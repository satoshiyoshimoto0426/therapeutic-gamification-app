#!/usr/bin/env python3
"""
Simple test for mood tracking service
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_mood_system_import():
    """Test importing mood system"""
    try:
        from shared.interfaces.mood_system import (
            MoodTrackingSystem, MoodEntry, MoodLevel, MoodCategory, MoodTrigger
        )
        print("? Mood system interfaces imported successfully")
        return True
    except Exception as e:
        print(f"? Failed to import mood system: {e}")
        return False

def test_mood_tracking_basic():
    """Test basic mood tracking functionality"""
    try:
        from shared.interfaces.mood_system import mood_tracking_system, MoodLevel
        
        # Test logging a mood
        mood_data = {
            'overall_mood': 4,
            'notes': 'Test mood entry'
        }
        
        mood_entry = mood_tracking_system.log_mood("test_user", mood_data)
        print(f"? Mood logged successfully: {mood_entry.entry_id}")
        
        # Test coefficient calculation
        coefficient = mood_entry.get_mood_coefficient()
        expected = 0.8 + (4 - 1) * 0.1  # Should be 1.1
        assert abs(coefficient - expected) < 0.01, f"Expected {expected}, got {coefficient}"
        print(f"? Mood coefficient calculated correctly: {coefficient}")
        
        # Test weighted coefficient
        weighted_coeff = mood_entry.get_weighted_mood_coefficient()
        assert 0.8 <= weighted_coeff <= 1.2, f"Weighted coefficient out of range: {weighted_coeff}"
        print(f"? Weighted mood coefficient in range: {weighted_coeff}")
        
        return True
    except Exception as e:
        print(f"? Basic mood tracking test failed: {e}")
        return False

def test_mood_api_import():
    """Test importing mood API"""
    try:
        # Import directly from main.py in current directory
        import main
        print("? Mood tracking API imported successfully")
        return True
    except Exception as e:
        print(f"? Failed to import mood API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Mood Tracking Service...")
    print("=" * 50)
    
    tests = [
        test_mood_system_import,
        test_mood_tracking_basic,
        test_mood_api_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("? All mood tracking tests passed!")
        exit(0)
    else:
        print("? Some tests failed")
        exit(1)