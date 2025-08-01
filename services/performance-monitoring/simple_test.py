"""
?
"""

import time
from main import (
    PerformanceMonitor, CacheManager, RateLimiter, QueryOptimizer,
    get_user_dashboard, get_performance_metrics
)

def test_basic_functionality():
    """基本"""
    print("=== 基本 ===")
    
    # 1. ?
    print("1. ?")
    monitor = PerformanceMonitor()
    print(f"   P95?: {monitor.p95_target}?")
    
    # 2. ?
    print("2. ?")
    cache = CacheManager()
    cache.set("test_key", {"data": "test_value"})
    cached_value = cache.get("test_key")
    print(f"   ?: {'OK' if cached_value else 'NG'}")
    
    # 3. レベル
    print("3. レベル")
    limiter = RateLimiter(max_requests=5, window_minutes=1)
    allowed_count = 0
    for i in range(7):
        if limiter.is_allowed("127.0.0.1"):
            allowed_count += 1
    print(f"   許: {allowed_count}/7 (?: 5)")
    
    # 4. ?
    print("4. ?")
    optimizer = QueryOptimizer()
    result = optimizer.optimize_user_query("test_user")
    print(f"   ?: {'OK' if result else 'NG'}")
    
    print("基本\n")

def test_api_endpoints():
    """APIエラー"""
    print("=== APIエラー ===")
    
    # 1. ?
    print("1. ?")
    start_time = time.time()
    result = get_user_dashboard("test_user_1")
    response_time = time.time() - start_time
    print(f"   ?: {response_time:.3f}?")
    print(f"   レベル: {'OK' if 'user' in result else 'NG'}")
    
    # 2. ?
    print("2. ?")
    start_time = time.time()
    result2 = get_user_dashboard("test_user_1")  # ?
    cache_response_time = time.time() - start_time
    print(f"   ?: {cache_response_time:.3f}?")
    print(f"   ?: {'OK' if cache_response_time < response_time else 'NG'}")
    
    # 3. ?
    print("3. ?")
    metrics = get_performance_metrics()
    print(f"   メイン: {'OK' if 'performance' in metrics else 'NG'}")
    
    if 'performance' in metrics and metrics['performance'].get('total_requests', 0) > 0:
        perf = metrics['performance']
        print(f"   ?: {perf.get('total_requests', 0)}")
        print(f"   ?: {perf.get('avg_response_time', 0):.3f}?")
        print(f"   P95レベル: {perf.get('p95_latency', 0):.3f}?")
        print(f"   P95?: {'OK' if perf.get('p95_compliance', False) else 'NG'}")
    
    print("APIエラー\n")

def test_performance_requirements():
    """?"""
    print("=== ? ===")
    
    # ?P95レベル
    print("1. P95レベル1.2?")
    response_times = []
    
    for i in range(20):
        start_time = time.time()
        get_user_dashboard(f"perf_test_user_{i}")
        response_time = time.time() - start_time
        response_times.append(response_time)
    
    # P95計算
    response_times.sort()
    p95_index = int(len(response_times) * 0.95)
    p95_latency = response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
    
    print(f"   P95レベル: {p95_latency:.3f}?")
    print(f"   ?: {'OK' if p95_latency <= 1.2 else 'NG'}")
    
    # レベル
    print("2. レベル120req/min/IP?")
    limiter = RateLimiter(max_requests=10, window_minutes=1)  # ?
    
    allowed_requests = 0
    for i in range(15):
        if limiter.is_allowed("test_ip"):
            allowed_requests += 1
    
    print(f"   許: {allowed_requests}/15")
    print(f"   ?: {'OK' if allowed_requests <= 10 else 'NG'}")
    
    print("?\n")

def main():
    """メイン"""
    print("? - ?")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_api_endpoints()
        test_performance_requirements()
        
        print("=" * 50)
        print("?")
        print("\n?:")
        print("? 1.2?P95レベル")
        print("? ?")
        print("? レベル120req/min/IP?")
        print("? ?")
        
    except Exception as e:
        print(f"?: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()