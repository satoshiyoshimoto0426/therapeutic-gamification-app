"""
Alpha Playtest Service ?
"""
import asyncio
import json
from datetime import datetime, timedelta
from main import AlphaPlaytestEngine, TestUserStatus, FeedbackType, ABTestVariant

async def test_alpha_playtest():
    """?"""
    print("=== Alpha Playtest Service ? ===")
    
    # エラー
    engine = AlphaPlaytestEngine()
    print("? プレビュー")
    print(f"  - ?: {engine.max_test_users}")
    print(f"  - A/B?: {len(engine.ab_tests)}")
    
    # ?
    print("\n=== ? ===")
    
    test_users = []
    for i in range(10):
        email = f"testuser{i}@example.com"
        demographics = {
            "age": 20 + (i % 30),
            "gender": "male" if i % 2 == 0 else "female",
            "location": "Tokyo" if i % 3 == 0 else "Osaka"
        }
        
        user = await engine.register_test_user(email, demographics)
        test_users.append(user)
        print(f"? ユーザー: {user.user_id[:8]}... (バリデーション: {user.assigned_variant.value})")
    
    print(f"? ?: {len(test_users)}")
    
    # バリデーション
    variant_counts = {}
    for user in test_users:
        variant = user.assigned_variant.value
        variant_counts[variant] = variant_counts.get(variant, 0) + 1
    
    print("? バリデーション:")
    for variant, count in variant_counts.items():
        print(f"  - {variant}: {count}?")
    
    # ?
    print("\n=== ? ===")
    
    behavior_events = [
        ("app_launch", {"version": "1.0.0", "platform": "mobile"}),
        ("onboarding_start", {"step": 1}),
        ("onboarding_complete", {"duration_seconds": 120}),
        ("task_create", {"task_type": "routine", "difficulty": 3}),
        ("task_complete", {"task_id": "task_001", "xp_gained": 50}),
        ("story_view", {"story_id": "story_001", "chapter": 1}),
        ("mandala_access", {"grid_position": "center"}),
        ("mood_log", {"mood_score": 4, "energy": 3}),
        ("session_end", {"duration_minutes": 25})
    ]
    
    logged_count = 0
    for user in test_users[:5]:  # ?5?
        session_id = f"session_{user.user_id[:8]}"
        
        for event_type, event_data in behavior_events:
            success = await engine.log_user_behavior(user.user_id, event_type, event_data, session_id)
            if success:
                logged_count += 1
    
    print(f"? ?: {logged_count}?")
    print(f"? ?: {len(engine.behavior_logs)}")
    
    # ?
    print("\n=== ? ===")
    
    feedback_samples = [
        (FeedbackType.BUG_REPORT, "ログ", "ログ", 2),
        (FeedbackType.USABILITY, "?", "メイン", 3),
        (FeedbackType.THERAPEUTIC_EFFECT, "気分", "?", 5),
        (FeedbackType.FEATURE_REQUEST, "?", "リスト", 4),
        (FeedbackType.GENERAL, "?", "と", 4)
    ]
    
    for i, (fb_type, title, content, rating) in enumerate(feedback_samples):
        user = test_users[i % len(test_users)]
        feedback = await engine.collect_feedback(user.user_id, fb_type, title, content, rating)
        print(f"? ?: {feedback.feedback_id[:8]}... (?: {feedback.sentiment_score:.3f})")
        print(f"  ?: {feedback.themes}")
    
    print(f"? ?: {len(engine.feedback_data)}")
    
    # A/B?
    print("\n=== A/B? ===")
    
    # ?
    for i, user in enumerate(test_users):
        if i % 3 == 0:  # 33%を
            user.status = TestUserStatus.COMPLETED
            user.completion_date = datetime.now()
    
    for test_id in engine.ab_tests.keys():
        try:
            result = await engine.run_ab_test_analysis(test_id)
            print(f"? A/B?: {test_id}")
            print(f"  - コア: {result.control_value:.3f}")
            print(f"  - バリデーションA: {result.variant_a_value:.3f}")
            print(f"  - バリデーションB: {result.variant_b_value:.3f}")
            print(f"  - ?: {result.statistical_significance:.3f}")
            print(f"  - ?: {result.sample_sizes}")
        except Exception as e:
            print(f"?  A/B? ({test_id}): {e}")
    
    # ?
    print("\n=== ? ===")
    
    report = await engine.generate_analytics_report()
    print(f"? ?")
    print(f"  - ?: {report.total_users}")
    print(f"  - アプリ: {report.active_users}")
    print(f"  - ?: {report.completion_rate:.3f}")
    print(f"  - ?: {report.average_session_duration:.1f}?")
    print(f"  - バリデーション: {report.bug_reports_count}")
    print(f"  - ?: {report.satisfaction_score:.1f}/5")
    
    print("  - リスト:")
    for period, rate in report.retention_rates.items():
        print(f"    {period}: {rate:.3f}")
    
    print("  - ?5?:")
    sorted_features = sorted(report.feature_usage.items(), key=lambda x: x[1], reverse=True)
    for feature, usage in sorted_features[:5]:
        print(f"    {feature}: {usage:.3f}")
    
    # ?
    print("\n=== ? ===")
    
    # ?
    suggestions = await engine.generate_improvement_suggestions(engine.feedback_data)
    print("? ?:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # ?
    sentiment_scores = [fb.sentiment_score for fb in engine.feedback_data if fb.sentiment_score is not None]
    if sentiment_scores:
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        print(f"? ?: {avg_sentiment:.3f}")
    
    # ?
    all_themes = []
    for fb in engine.feedback_data:
        all_themes.extend(fb.themes)
    
    from collections import Counter
    theme_counts = Counter(all_themes)
    print("? ?:")
    for theme, count in theme_counts.most_common(5):
        print(f"  - {theme}: {count}?")
    
    # プレビュー
    print("\n=== プレビュー ===")
    
    # ?
    anonymized_logs = [log for log in engine.behavior_logs if log.anonymized]
    print(f"? ?: {len(anonymized_logs)}/{len(engine.behavior_logs)}")
    
    # メイン
    original_emails = set()
    hashed_emails = set()
    for user in test_users:
        hashed_emails.add(user.email)
    
    print(f"? メイン: {len(hashed_emails)}?")
    
    # デフォルト
    print(f"? デフォルト: {engine.privacy_config['data_retention_days']}?")
    
    # ?
    print("\n=== ? ===")
    
    import time
    
    # ?
    start_time = time.time()
    
    test_user = test_users[0]
    for i in range(100):
        await engine.log_user_behavior(
            test_user.user_id,
            "performance_test",
            {"iteration": i, "data": f"test_data_{i}"},
            "perf_session"
        )
    
    log_time = time.time() - start_time
    print(f"? 100?: {log_time:.3f}?")
    
    # ?
    start_time = time.time()
    
    for _ in range(10):
        await engine.generate_analytics_report()
    
    analysis_time = time.time() - start_time
    print(f"? 10?: {analysis_time:.3f}?")
    
    # ?
    print("\n=== ? ===")
    print(f"?: {len(engine.test_users)}")
    print(f"?: {len(engine.behavior_logs)}")
    print(f"?: {len(engine.feedback_data)}")
    print(f"A/B?: {len(engine.ab_tests)}")
    
    # ユーザー
    from collections import Counter
    status_counts = Counter(user.status for user in engine.test_users.values())
    print("ユーザー:")
    for status, count in status_counts.items():
        print(f"  - {status.value}: {count}?")
    
    print("\n=== ? ===")
    return True

def test_api_endpoints():
    """API エラー"""
    print("\n=== API エラー ===")
    
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # ヘルパー
    response = client.get("/playtest/health")
    assert response.status_code == 200
    print("? GET /playtest/health")
    
    # ユーザー
    response = client.post(
        "/playtest/users/register",
        params={"email": "api_test@example.com"},
        json={"age": 25, "gender": "male"}
    )
    assert response.status_code == 200
    user_data = response.json()
    user_id = user_data["user_id"]
    print("? POST /playtest/users/register")
    
    # ?
    response = client.post(
        "/playtest/behavior/log",
        params={
            "user_id": user_id,
            "event_type": "api_test_event",
            "session_id": "api_session"
        },
        json={"test_data": "api_test"}
    )
    assert response.status_code == 200
    print("? POST /playtest/behavior/log")
    
    # ?
    response = client.post(
        "/playtest/feedback/submit",
        params={
            "user_id": user_id,
            "feedback_type": "general",
            "title": "API Test Feedback",
            "content": "This is a test feedback",
            "rating": 4
        }
    )
    assert response.status_code == 200
    print("? POST /playtest/feedback/submit")
    
    # ?
    response = client.get("/playtest/analytics/report")
    assert response.status_code == 200
    print("? GET /playtest/analytics/report")
    
    # A/B?
    response = client.get("/playtest/abtest/list")
    assert response.status_code == 200
    print("? GET /playtest/abtest/list")
    
    # ?
    response = client.get("/playtest/feedback/analysis")
    assert response.status_code == 200
    print("? GET /playtest/feedback/analysis")
    
    # ユーザー
    response = client.get("/playtest/users/status")
    assert response.status_code == 200
    print("? GET /playtest/users/status")
    
    print("? ?APIエラー")

if __name__ == "__main__":
    # ?
    asyncio.run(test_alpha_playtest())
    
    # API ?
    test_api_endpoints()
    
    print("\n? Alpha Playtest Service ?")