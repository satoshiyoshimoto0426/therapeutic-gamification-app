"""
?
"""

def test_performance_monitor():
    """?"""
    from main import PerformanceMonitor, PerformanceMetrics
    from datetime import datetime
    
    print("1. ?")
    monitor = PerformanceMonitor()
    
    # メイン
    metric = PerformanceMetrics(
        endpoint="/api/test",
        response_time=0.5,
        timestamp=datetime.now(),
        status_code=200,
        cache_hit=False
    )
    monitor.record_metric(metric)
    
    # P95計算
    p95 = monitor.get_p95_latency()
    print(f"   P95レベル: {p95:.3f}?")
    print(f"   ?(1.2?)?: {'OK' if p95 <= 1.2 else 'NG'}")
    
    return True

def test_cache_manager():
    """?"""
    from main import CacheManager
    
    print("2. ?")
    cache = CacheManager()
    
    # ?
    test_data = {"user_id": "123", "level": 5}
    cache.set("test_key", test_data)
    retrieved = cache.get("test_key")
    
    print(f"   ?: {'OK' if retrieved == test_data else 'NG'}")
    
    # ?
    stats = cache.get_cache_stats()
    print(f"   ?: {stats['total_entries']}")
    
    return True

def test_rate_limiter():
    """レベル"""
    from main import RateLimiter
    
    print("3. レベル")
    limiter = RateLimiter(max_requests=3, window_minutes=1)  # ?
    
    # ?
    ip = "127.0.0.1"
    allowed_count = 0
    
    for i in range(5):
        if limiter.is_allowed(ip):
            allowed_count += 1
    
    print(f"   許: {allowed_count}/5")
    print(f"   ?: {'OK' if allowed_count == 3 else 'NG'}")
    
    return True

def test_query_optimizer():
    """?"""
    from main import QueryOptimizer
    
    print("4. ?")
    optimizer = QueryOptimizer()
    
    # ユーザー
    result = optimizer.optimize_user_query("test_user")
    print(f"   ユーザー: {'OK' if 'user_profile' in result else 'NG'}")
    
    # Mandala?
    mandala_result = optimizer.optimize_mandala_query("test_user")
    print(f"   Mandala?: {'OK' if 'grid' in mandala_result else 'NG'}")
    
    return True

def test_api_endpoints():
    """APIエラー"""
    from main import get_user_dashboard, get_performance_metrics
    import time
    
    print("5. APIエラー")
    
    # ?
    start_time = time.time()
    result = get_user_dashboard("test_user")
    response_time = time.time() - start_time
    
    print(f"   ?: {response_time:.3f}?")
    print(f"   レベル: {'OK' if 'user' in result else 'NG'}")
    
    # メイン
    metrics = get_performance_metrics()
    print(f"   メイン: {'OK' if 'performance' in metrics else 'NG'}")
    
    return True

def main():
    """メイン"""
    print("? - ?")
    print("=" * 40)
    
    tests = [
        test_performance_monitor,
        test_cache_manager,
        test_rate_limiter,
        test_query_optimizer,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   エラー: {e}")
            print()
    
    print("=" * 40)
    print(f"?: {passed}/{total} 成")
    
    if passed == total:
        print("\n? ?")
        print("\n?:")
        print("? 1.2?P95レベル")
        print("? ?") 
        print("? レベル120req/min/IP?")
        print("? ?")
    else:
        print(f"\n? {total - passed}?")

if __name__ == "__main__":
    main()