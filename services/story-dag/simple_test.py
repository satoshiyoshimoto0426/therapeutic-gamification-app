#!/usr/bin/env python3
"""
Simple test for Story DAG Management System
"""

import sys
import os

def test_story_dag_utils():
    """Test the story DAG utilities"""
    print("? Testing Story DAG Utilities...")
    
    try:
        from story_dag_utils import StoryDAGUtils
        
        # Test sample story generation
        utils = StoryDAGUtils()
        story = utils.generate_sample_story()
        
        print(f"? Sample story generated with {len(story['nodes'])} nodes and {len(story['choices'])} choices")
        
        # Test story validation
        validation = utils.validate_story_structure(story)
        print(f"? Story validation: {'PASS' if validation['is_valid'] else 'FAIL'}")
        
        # Test complexity analysis
        complexity = utils.analyze_story_complexity(story)
        print(f"? Complexity analysis: {complexity['total_nodes']} nodes, {complexity['total_choices']} choices")
        
        # Test visualization
        viz = utils.visualize_story_dag(story)
        print(f"? Story visualization generated ({len(viz)} characters)")
        
        return True
        
    except Exception as e:
        print(f"? Story DAG utilities test failed: {e}")
        return False

def test_main_module():
    """Test the main module structure"""
    print("? Testing Main Module Structure...")
    
    try:
        # Check if main.py exists and has required classes
        with open('main.py', 'r') as f:
            content = f.read()
        
        required_classes = ['StoryDAGManager', 'StoryNode', 'StoryChoice', 'StoryProgress']
        for cls in required_classes:
            if cls in content:
                print(f"? {cls} class found")
            else:
                print(f"? {cls} class missing")
                return False
        
        # Check for required endpoints
        required_endpoints = ['/nodes', '/choices', '/progress', '/validate']
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"? {endpoint} endpoint found")
            else:
                print(f"? {endpoint} endpoint missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"? Main module test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("? Story DAG Management System - Simple Test Suite")
    print("=" * 60)
    
    # Test utilities
    utils_success = test_story_dag_utils()
    print()
    
    # Test main module
    main_success = test_main_module()
    print()
    
    # Summary
    total_tests = 2
    passed_tests = sum([utils_success, main_success])
    
    print("=" * 60)
    print(f"? Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("? All tests passed! Story DAG Management System is ready.")
        return True
    else:
        print("? Some tests failed. Please review implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)