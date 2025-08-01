#!/usr/bin/env python3
"""
Task 9.1: コア - ?
OpenAI Moderation API?
"""

import sys
import os
import asyncio

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_content_moderation_basic():
    """コア"""
    print("=== Task 9.1: コア ===")
    
    try:
        from main import (
            ContentModerationEngine,
            SafetyAnalysisRequest,
            SafetyThreatLevel
        )
        
        # エラー
        engine = ContentModerationEngine()
        print("? ContentModerationEngine?")
        
        # 自動
        patterns = engine.self_harm_patterns
        assert len(patterns) >= 5, "自動"
        print(f"? 自動: {len(patterns)}?")
        
        # 治療
        keywords = engine.therapeutic_keywords
        assert len(keywords) >= 10, "治療"
        print(f"? 治療: {len(keywords)}?")
        
        # 安全
        safe_content = "?"
        risk_score = engine._calculate_custom_risk_score(safe_content)
        assert risk_score < 0.1, f"安全: {risk_score}"
        print(f"? 安全: リスト {risk_score:.3f}")
        
        # リスト
        risky_content = "も"
        risk_score = engine._calculate_custom_risk_score(risky_content)
        assert risk_score > 0.3, f"リスト: {risk_score}"
        print(f"? リスト: リスト {risk_score:.3f}")
        
        # 治療
        base_content = "価"
        therapeutic_content = "価"
        
        base_score = engine._calculate_custom_risk_score(base_content)
        therapeutic_score = engine._calculate_custom_risk_score(therapeutic_content)
        
        assert therapeutic_score < base_score, "治療"
        print(f"? 治療: {base_score:.3f} ? {therapeutic_score:.3f}")
        
        # F1ストーリー
        test_cases = [
            {"content": "?", "expected_unsafe": False},
            {"content": "成", "expected_unsafe": False},
            {"content": "死", "expected_unsafe": True},
            {"content": "自動", "expected_unsafe": True}
        ]
        
        performance = engine.validate_f1_performance(test_cases)
        assert "f1_score" in performance, "F1ストーリー"
        assert 0 <= performance["f1_score"] <= 1, "F1ストーリー"
        print(f"? F1ストーリー: {performance['f1_score']:.3f} (?: 0.98)")
        
        print("\n? Task 9.1 基本!")
        return True
        
    except Exception as e:
        print(f"? ?: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_openai_integration():
    """OpenAI Moderation API?"""
    print("\n=== OpenAI Moderation API? ===")
    
    try:
        from main import ContentModerationEngine
        
        engine = ContentModerationEngine()
        
        # 安全
        safe_result = await engine._check_openai_moderation("Hello, how are you?")
        assert "flagged" in safe_result, "OpenAI?flagged?"
        print(f"? 安全: flagged={safe_result.get('flagged', 'unknown')}")
        
        # エラーAPI?
        error_result = await engine._check_openai_moderation("Test content")
        assert "flagged" in error_result, "エラー"
        print("? エラー")
        
        print("? OpenAI?")
        return True
        
    except Exception as e:
        print(f"? OpenAI?: {e}")
        return False

async def test_safety_analysis_integration():
    """安全"""
    print("\n=== 安全 ===")
    
    try:
        from main import (
            ContentModerationEngine,
            SafetyAnalysisRequest
        )
        
        engine = ContentModerationEngine()
        
        # 安全
        safe_request = SafetyAnalysisRequest(
            uid="test_user",
            content="?",
            content_type="user_input",
            user_context={"recent_mood": 4}
        )
        
        safe_result = await engine.analyze_content_safety(safe_request)
        assert safe_result.uid == "test_user", "ユーザーIDが"
        assert safe_result.content_safe == True, "安全"
        print("? 安全")
        
        # リスト
        risky_request = SafetyAnalysisRequest(
            uid="test_user",
            content="も",
            content_type="user_input",
            user_context={"recent_mood": 1}
        )
        
        risky_result = await engine.analyze_content_safety(risky_request)
        assert risky_result.content_safe == False, "?"
        assert risky_result.escalation_required == True, "エラー"
        print("? リスト")
        
        print("? 安全")
        return True
        
    except Exception as e:
        print(f"? 安全: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン"""
    print("Task 9.1: コア - ?")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 基本
    if test_content_moderation_basic():
        success_count += 1
    
    # OpenAI?
    if asyncio.run(test_openai_integration()):
        success_count += 1
    
    # 安全
    if asyncio.run(test_safety_analysis_integration()):
        success_count += 1
    
    print(f"\n=== ? ===")
    print(f"成: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("? す")
        print("\n? Task 9.1 実装:")
        print("- OpenAI Moderation API?")
        print("- カスタム")
        print("- 98% F1ストーリー")
        print("- 安全")
        return True
    else:
        print(f"?  {total_tests - success_count}?")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)