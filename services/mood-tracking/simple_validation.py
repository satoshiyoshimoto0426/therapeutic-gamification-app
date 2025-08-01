#!/usr/bin/env python3
"""
気分
Simple validation script for mood tracking service (no dependencies)
"""

def calculate_mood_coefficient_simple(mood_score: int, recent_scores: list = None) -> float:
    """
    気分
    Simple version of mood coefficient calculation
    """
    # Base coefficient mapping: 1->0.8, 2->0.9, 3->1.0, 4->1.1, 5->1.2
    base_coefficient = 0.6 + (mood_score * 0.1)
    
    # Apply trend adjustment if recent scores available
    if recent_scores and len(recent_scores) >= 3:
        recent_avg = sum(recent_scores[-3:]) / len(recent_scores[-3:])
        trend_factor = (recent_avg - 3.0) * 0.05  # -0.1 to +0.1 adjustment
        base_coefficient += trend_factor
    
    # Ensure coefficient stays within bounds
    return max(0.8, min(1.2, base_coefficient))

def analyze_mood_trend_simple(mood_scores: list) -> str:
    """
    気分
    Simple version of mood trend analysis
    """
    if len(mood_scores) < 3:
        return "stable"
    
    # Calculate trend using simple slope
    n = len(mood_scores)
    x_values = list(range(n))
    
    # Simple linear regression
    x_mean = sum(x_values) / n
    y_mean = sum(mood_scores) / n
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, mood_scores))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        return "stable"
    
    slope = numerator / denominator
    
    if slope > 0.1:
        return "improving"
    elif slope < -0.1:
        return "declining"
    else:
        return "stable"

def validate_coefficient_calculation():
    """気分"""
    print("=== 気分 ===")
    
    # 基本
    test_cases = [
        (1, 0.8, "?"),
        (2, 0.9, "?"),
        (3, 1.0, "?"),
        (4, 1.1, "?"),
        (5, 1.2, "?")
    ]
    
    all_passed = True
    for mood_score, expected, description in test_cases:
        result = calculate_mood_coefficient_simple(mood_score)
        passed = abs(result - expected) < 0.001
        status = "?" if passed else "?"
        print(f"{status} {description}: {mood_score} -> {result} (?: {expected})")
        if not passed:
            all_passed = False
    
    # ?
    print("\n--- ? ---")
    
    base_coeff = calculate_mood_coefficient_simple(3)
    improving_coeff = calculate_mood_coefficient_simple(3, [1, 2, 3])
    declining_coeff = calculate_mood_coefficient_simple(3, [5, 4, 3])
    
    print(f"基本 (気分3): {base_coeff}")
    print(f"? (1->2->3): {improving_coeff}")
    print(f"? (5->4->3): {declining_coeff}")
    
    # ?
    if improving_coeff > base_coeff:
        print("? ?")
    else:
        print("? ?")
        all_passed = False
    
    # ?
    if declining_coeff < base_coeff:
        print("? ?")
    else:
        print("? ?")
        all_passed = False
    
    return all_passed

def validate_trend_analysis():
    """?"""
    print("\n=== ? ===")
    
    # ?
    trend_cases = [
        ([1, 2, 3, 4, 5], "improving", "?"),
        ([5, 4, 3, 2, 1], "declining", "?"),
        ([3, 3, 3, 3, 3], "stable", "?"),
        ([2, 3, 4, 3, 4], "improving", "?"),
        ([4, 3, 2, 3, 2], "declining", "?"),
        ([3, 2, 4, 2, 3], "stable", "?"),
        ([1, 5], "stable", "デフォルト"),
        ([3], "stable", "?")
    ]
    
    all_passed = True
    for scores, expected_trend, description in trend_cases:
        result = analyze_mood_trend_simple(scores)
        passed = result == expected_trend
        status = "?" if passed else "?"
        print(f"{status} {description}: {scores} -> {result} (?: {expected_trend})")
        if not passed:
            all_passed = False
    
    return all_passed

def validate_boundary_conditions():
    """?"""
    print("\n=== ? ===")
    
    # ?
    extreme_cases = [
        (1, [1, 1, 1, 1, 1], "一般"),
        (5, [5, 5, 5, 5, 5], "一般"),
        (1, [5, 4, 3, 2, 1], "?"),
        (5, [1, 2, 3, 4, 5], "?")
    ]
    
    all_passed = True
    for mood_score, recent_scores, description in extreme_cases:
        coeff = calculate_mood_coefficient_simple(mood_score, recent_scores)
        in_bounds = 0.8 <= coeff <= 1.2
        status = "?" if in_bounds else "?"
        print(f"{status} {description}: 気分{mood_score} -> 係数{coeff:.3f} (?: {in_bounds})")
        if not in_bounds:
            all_passed = False
    
    return all_passed

def validate_xp_impact_scenarios():
    """XP?"""
    print("\n=== XP? ===")
    
    # 実装XP計算
    base_xp = 100
    scenarios = [
        {
            "name": "?",
            "mood_score": 2,
            "recent_scores": [2, 2, 2],
            "expected_reduction": True
        },
        {
            "name": "?",
            "mood_score": 3,
            "recent_scores": [3, 3, 3],
            "expected_reduction": False
        },
        {
            "name": "?",
            "mood_score": 4,
            "recent_scores": [4, 4, 4],
            "expected_reduction": False
        },
        {
            "name": "?",
            "mood_score": 4,
            "recent_scores": [2, 3, 4],
            "expected_reduction": False
        }
    ]
    
    all_passed = True
    for scenario in scenarios:
        coeff = calculate_mood_coefficient_simple(
            scenario["mood_score"], 
            scenario["recent_scores"]
        )
        
        final_xp = int(base_xp * coeff)
        is_reduced = final_xp < base_xp
        
        expected_reduction = scenario["expected_reduction"]
        passed = is_reduced == expected_reduction
        status = "?" if passed else "?"
        
        print(f"{status} {scenario['name']}: 基本XP{base_xp} ? 係数{coeff:.3f} = {final_xp}XP")
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """メイン"""
    print("気分")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(validate_coefficient_calculation())
        results.append(validate_trend_analysis())
        results.append(validate_boundary_conditions())
        results.append(validate_xp_impact_scenarios())
        
        print("\n" + "=" * 50)
        
        if all(results):
            print("? ?")
            print("\n実装:")
            print("? 1-5ストーリー")
            print("? 0.8-1.2?")
            print("? ?")
            print("? ?")
            print("? XP?")
            return True
        else:
            failed_count = sum(1 for r in results if not r)
            print(f"? {failed_count}?")
            return False
            
    except Exception as e:
        print(f"\n? 検証: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)