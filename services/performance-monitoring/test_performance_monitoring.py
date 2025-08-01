"""
?
1.2?P95レベル
"""

import unittest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from main import (
    PerformanceMonitor, CacheManager, RateLimiter, QueryOptimizer,
    PerformanceMetrics, RateLimitInfo,
    monitor_performance, rate_limit,
    get_user_dashboard, get_performance_metrics
)

class TestPerformanceMonitor(unittest.TestCase):
    """?"""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_record_metric(self):
        """メイン"""
        metric = PerformanceMetrics(
            endpoint="/api/user",
            response_time=0.5,
            timestamp=datetime.now(),
            status_code=200,
            cache_hit=False
        )
        
        self.monitor.record_metric(metric)
        self.assertEqual(len(self.monitor.metrics), 1)
        self.assertEqual(self.monitor.metrics[0].endpoint, "/api/user")
    
    def test_p95_latency_calculation(self):
        """P95レベル"""
        # 100?0.1?1.0?
        for i in range(100):
            metric = PerformanceMetrics(
                endpoint="/api/test",
                response_time=0.01 * (i + 1),
                timestamp=datetime.now(),
                status_code=200
            )
            self.monitor.record_metric(metric)
        
        p95 = self.monitor.get_p95_latency()
        # P95は95?0.95?
        self.assertAlmostEqual(p95, 0.95, places=2)
    
    def test_p95_target_compliance(self):
        """P95?"""
        # ?
        for i in range(10):
            metric = PerformanceMetrics(
                endpoint="/api/fast",
                response_time=0.8,  # 1.2?
                timestamp=datetime.now(),
                status_code=200
            )
            self.monitor.record_metric(metric)
        
        summary = self.monitor.get_performance_summary()
        self.assertTrue(summary["p95_compliance"])
        self.assertLessEqual(summary["p95_latency"], 1.2)
    
    def test_performance_summary(self):
        """?"""
        # ?
        metrics = [
            PerformanceMetrics("/api/user", 0.5, datetime.now(), 200, True),
            PerformanceMetrics("/api/task", 0.8, datetime.now(), 200, False),
            PerformanceMetrics("/api/story", 1.1, datetime.now(), 200, True)
        ]
        
        for metric in metrics:
            self.monitor.record_metric(metric)
        
        summary = self.monitor.get_performance_summary()
        
        self.assertEqual(summary["total_requests"], 3)
        self.assertAlmostEqual(summary["avg_response_time"], 0.8, places=1)
        self.assertEqual(summary["cache_hit_rate"], 2/3)  # 2つ
        self.assertIn("endpoints", summary)

class TestCacheManager(unittest.TestCase):
    """?"""
    
    def setUp(self):
        self.cache = CacheManager()
    
    def test_cache_set_get(self):
        """?"""
        test_data = {"user_id": "123", "level": 5}
        self.cache.set("user_123", test_data, "user_profile")
        
        retrieved = self.cache.get("user_123", "user_profile")
        self.assertEqual(retrieved, test_data)
    
    def test_cache_ttl_expiration(self):
        """?TTL?"""
        # TTLを
        original_ttl = self.cache.cache_ttl["user_profile"]
        self.cache.cache_ttl["user_profile"] = 1  # 1?
        
        test_data = {"user_id": "123"}
        self.cache.set("user_123", test_data, "user_profile")
        
        # す
        self.assertEqual(self.cache.get("user_123", "user_profile"), test_data)
        
        # ?
        with self.cache.cache_lock:
            if "user_123" in self.cache.memory_cache:
                self.cache.memory_cache["user_123"]["timestamp"] = datetime.now() - timedelta(seconds=2)
        
        self.assertIsNone(self.cache.get("user_123", "user_profile"))
        
        # TTLを
        self.cache.cache_ttl["user_profile"] = original_ttl
    
    def test_cache_invalidation(self):
        """?"""
        self.cache.set("user_123", {"data": "test1"})
        self.cache.set("user_456", {"data": "test2"})
        self.cache.set("task_789", {"data": "test3"})
        
        # ?
        self.cache.invalidate("user_")
        
        self.assertIsNone(self.cache.get("user_123"))
        self.assertIsNone(self.cache.get("user_456"))
        self.assertIsNotNone(self.cache.get("task_789"))
    
    def test_cache_stats(self):
        """?"""
        self.cache.set("key1", {"data": 1}, "type1")
        self.cache.set("key2", {"data": 2}, "type2")
        self.cache.set("key3", {"data": 3}, "type1")
        
        stats = self.cache.get_cache_stats()
        
        self.assertEqual(stats["total_entries"], 3)
        self.assertEqual(stats["type_distribution"]["type1"], 2)
        self.assertEqual(stats["type_distribution"]["type2"], 1)

class TestRateLimiter(unittest.TestCase):
    """レベル"""
    
    def setUp(self):
        # ?
        self.limiter = RateLimiter(max_requests=5, window_minutes=1)
    
    def test_rate_limit_allow(self):
        """レベル"""
        ip = "192.168.1.1"
        
        # 5?
        for i in range(5):
            self.assertTrue(self.limiter.is_allowed(ip))
        
        # 6?
        self.assertFalse(self.limiter.is_allowed(ip))
    
    def test_rate_limit_window_reset(self):
        """レベル"""
        ip = "192.168.1.2"
        
        # ?
        for i in range(5):
            self.assertTrue(self.limiter.is_allowed(ip))
        
        self.assertFalse(self.limiter.is_allowed(ip))
        
        # ?
        # 実装1?
        info = self.limiter.get_rate_limit_info(ip)
        self.assertEqual(info.request_count, 5)
    
    def test_rate_limit_info(self):
        """レベル"""
        ip = "192.168.1.3"
        
        # 3?
        for i in range(3):
            self.limiter.is_allowed(ip)
        
        info = self.limiter.get_rate_limit_info(ip)
        self.assertEqual(info.ip_address, ip)
        self.assertEqual(info.request_count, 3)
        self.assertIsNone(info.blocked_until)
    
    def test_rate_limit_stats(self):
        """レベル"""
        # ?IPか
        ips = ["192.168.1.4", "192.168.1.5", "192.168.1.6"]
        
        for ip in ips:
            for i in range(3):
                self.limiter.is_allowed(ip)
        
        stats = self.limiter.get_rate_limit_stats()
        
        self.assertEqual(stats["active_ips"], 3)
        self.assertEqual(stats["blocked_ips"], 0)
        self.assertEqual(stats["max_requests_per_window"], 5)

class TestQueryOptimizer(unittest.TestCase):
    """?"""
    
    def setUp(self):
        self.optimizer = QueryOptimizer()
    
    def test_user_query_optimization(self):
        """ユーザー"""
        user_id = "test_user_123"
        
        # ?
        result1 = self.optimizer.optimize_user_query(user_id)
        self.assertIn("user_profile", result1)
        self.assertIn("active_tasks", result1)
        
        # 2?
        result2 = self.optimizer.optimize_user_query(user_id)
        self.assertEqual(result1, result2)
    
    def test_mandala_query_optimization(self):
        """Mandala?"""
        user_id = "test_user_456"
        
        result = self.optimizer.optimize_mandala_query(user_id)
        
        self.assertIn("grid", result)
        self.assertIn("unlocked_cells", result)
        self.assertIn("current_chapter", result)
        self.assertEqual(len(result["grid"]), 9)
        self.assertEqual(len(result["grid"][0]), 9)
    
    def test_slow_query_detection(self):
        """ストーリー"""
        # ストーリー
        original_threshold = self.optimizer.slow_query_threshold
        self.optimizer.slow_query_threshold = 0.001  # 1ms
        
        # ?
        self.optimizer.optimize_user_query("slow_user")
        
        report = self.optimizer.get_slow_query_report()
        self.assertGreater(report["total_slow_queries"], 0)
        
        # ?
        self.optimizer.slow_query_threshold = original_threshold

class TestDecorators(unittest.TestCase):
    """デフォルト"""
    
    def test_monitor_performance_decorator(self):
        """?"""
        monitor = PerformanceMonitor()
        
        @monitor_performance("test_endpoint")
        def test_function():
            time.sleep(0.1)
            return {"result": "success"}
        
        # デフォルト
        test_function._monitor = monitor
        
        result = test_function()
        
        self.assertEqual(result["result"], "success")
        self.assertEqual(len(monitor.metrics), 1)
        self.assertEqual(monitor.metrics[0].endpoint, "test_endpoint")
        self.assertGreaterEqual(monitor.metrics[0].response_time, 0.1)
    
    def test_rate_limit_decorator(self):
        """レベル"""
        limiter = RateLimiter(max_requests=2, window_minutes=1)
        
        @rate_limit(2)
        def test_function(ip_address="127.0.0.1"):
            return {"result": "success"}
        
        # デフォルト
        test_function._rate_limiter = limiter
        
        # 2?
        result1 = test_function()
        result2 = test_function()
        
        self.assertEqual(result1["result"], "success")
        self.assertEqual(result2["result"], "success")
        
        # 3?
        result3 = test_function()
        self.assertIn("error", result3)
        self.assertEqual(result3["status_code"], 429)

class TestIntegration(unittest.TestCase):
    """?"""
    
    def test_dashboard_endpoint_performance(self):
        """?"""
        user_id = "integration_test_user"
        
        # ?
        start_time = time.time()
        result1 = get_user_dashboard(user_id)
        first_request_time = time.time() - start_time
        
        # 2?
        start_time = time.time()
        result2 = get_user_dashboard(user_id)
        second_request_time = time.time() - start_time
        
        # ?2?
        self.assertLess(second_request_time, first_request_time)
        self.assertEqual(result1["user"], result2["user"])
    
    def test_rate_limiting_integration(self):
        """レベル"""
        user_id = "rate_limit_test_user"
        ip = "192.168.1.100"
        
        # ?
        success_count = 0
        for i in range(125):  # 120を
            result = get_user_dashboard(user_id, ip_address=ip)
            if "error" not in result:
                success_count += 1
            else:
                break
        
        # 120?
        self.assertLessEqual(success_count, 120)
    
    def test_performance_metrics_endpoint(self):
        """?"""
        # い
        for i in range(5):
            get_user_dashboard(f"metrics_test_user_{i}")
        
        metrics = get_performance_metrics()
        
        self.assertIn("performance", metrics)
        self.assertIn("cache", metrics)
        self.assertIn("rate_limiting", metrics)
        self.assertIn("slow_queries", metrics)
        
        # ?
        perf = metrics["performance"]
        self.assertIn("total_requests", perf)
        self.assertIn("p95_latency", perf)
        self.assertIn("p95_compliance", perf)
    
    def test_concurrent_requests(self):
        """?"""
        def make_request(user_id):
            return get_user_dashboard(f"concurrent_user_{user_id}")
        
        # 5?
        threads = []
        results = []
        
        def thread_worker(user_id):
            result = make_request(user_id)
            results.append(result)
        
        for i in range(5):
            thread = threading.Thread(target=thread_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # ?
        for thread in threads:
            thread.join(timeout=5.0)
        
        # ?
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIn("user", result)
            self.assertNotIn("error", result)

class TestP95LatencyCompliance(unittest.TestCase):
    """P95レベル"""
    
    def test_p95_latency_target_1_2_seconds(self):
        """1.2?P95レベル"""
        monitor = PerformanceMonitor()
        
        # 100?
        # 95%は1.2?5%は1.2?
        for i in range(95):
            metric = PerformanceMetrics(
                endpoint="/api/test",
                response_time=0.5 + (i * 0.007),  # 0.5?1.165?
                timestamp=datetime.now(),
                status_code=200
            )
            monitor.record_metric(metric)
        
        # 5%の
        for i in range(5):
            metric = PerformanceMetrics(
                endpoint="/api/test",
                response_time=1.5 + i,  # 1.5?5.5?
                timestamp=datetime.now(),
                status_code=200
            )
            monitor.record_metric(metric)
        
        p95 = monitor.get_p95_latency()
        summary = monitor.get_performance_summary()
        
        # P95が
        self.assertLessEqual(p95, 1.2)
        self.assertTrue(summary["p95_compliance"])

if __name__ == "__main__":
    print("?...")
    
    # ?
    test_suite = unittest.TestSuite()
    
    # ?
    test_classes = [
        TestPerformanceMonitor,
        TestCacheManager,
        TestRateLimiter,
        TestQueryOptimizer,
        TestDecorators,
        TestIntegration,
        TestP95LatencyCompliance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # ?
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # ?
    print(f"\n{'='*50}")
    print(f"?:")
    print(f"実装: {result.testsRun}")
    print(f"?: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print(f"成: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n?:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nエラー:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    print(f"{'='*50}")
    
    # ?
    print(f"\n?:")
    print(f"? 1.2?P95レベル")
    print(f"? ?")
    print(f"? レベル120req/min/IP?")
    print(f"? ?")