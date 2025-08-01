"""
パフォーマンスとスケーラビリティの基本確認システム
- 同時接続数の基本テスト（10-50ユーザー）
- API応答時間の測定と最適化
- メモリ使用量とCPU使用率の監視
- 基本的なロードテストの実行
"""

import asyncio
import aiohttp
import time
import threading
import psutil
import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from collections import defaultdict
import requests

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestResult:
    """ロードテスト結果"""
    test_name: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    error_rate: float
    test_duration: float
    timestamp: datetime

@dataclass
class SystemMetrics:
    """システムメトリクス"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    timestamp: datetime

@dataclass
class APIResponseMetrics:
    """API応答メトリクス"""
    endpoint: str
    response_time: float
    status_code: int
    response_size: int
    error_message: Optional[str]
    timestamp: datetime

class SystemMonitor:
    """システムリソース監視"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics_history: List[SystemMetrics] = []
        self.monitor_thread = None
        self.lock = threading.Lock()
    
    def start_monitoring(self, interval: float = 1.0):
        """監視開始"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("システム監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("システム監視を停止しました")
    
    def _monitor_loop(self, interval: float):
        """監視ループ"""
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # メモリ使用率
                memory = psutil.virtual_memory()
                
                # ディスク使用率
                disk = psutil.disk_usage('/')
                
                # ネットワーク統計
                network = psutil.net_io_counters()
                
                # アクティブ接続数
                connections = len(psutil.net_connections())
                
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    memory_available_mb=memory.available / (1024 * 1024),
                    disk_usage_percent=disk.percent,
                    network_sent_mb=network.bytes_sent / (1024 * 1024),
                    network_recv_mb=network.bytes_recv / (1024 * 1024),
                    active_connections=connections,
                    timestamp=datetime.now()
                )
                
                with self.lock:
                    self.metrics_history.append(metrics)
                    # 過去1時間のデータのみ保持
                    cutoff = datetime.now() - timedelta(hours=1)
                    self.metrics_history = [
                        m for m in self.metrics_history 
                        if m.timestamp > cutoff
                    ]
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"システム監視エラー: {e}")
                time.sleep(1)
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """現在のメトリクス取得"""
        with self.lock:
            return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """メトリクス要約"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp > cutoff
            ]
        
        if not recent_metrics:
            return {"error": "メトリクスデータがありません"}
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "period_minutes": minutes,
            "sample_count": len(recent_metrics),
            "cpu": {
                "avg": statistics.mean(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values),
                "current": recent_metrics[-1].cpu_percent
            },
            "memory": {
                "avg": statistics.mean(memory_values),
                "min": min(memory_values),
                "max": max(memory_values),
                "current": recent_metrics[-1].memory_percent,
                "used_mb": recent_metrics[-1].memory_used_mb,
                "available_mb": recent_metrics[-1].memory_available_mb
            },
            "network": {
                "sent_mb": recent_metrics[-1].network_sent_mb,
                "recv_mb": recent_metrics[-1].network_recv_mb
            },
            "connections": recent_metrics[-1].active_connections,
            "timestamp": datetime.now().isoformat()
        }

class ConcurrentUserSimulator:
    """同時ユーザーシミュレーター"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def simulate_user_session(self, user_id: str, session_duration: int = 60) -> List[APIResponseMetrics]:
        """ユーザーセッションシミュレーション"""
        metrics = []
        start_time = time.time()
        
        # 典型的なユーザー行動パターン
        endpoints = [
            "/health",
            f"/api/user/{user_id}/dashboard",
            f"/api/user/{user_id}/tasks",
            f"/api/user/{user_id}/mandala",
            f"/api/user/{user_id}/story",
            "/api/performance/metrics"
        ]
        
        while time.time() - start_time < session_duration:
            for endpoint in endpoints:
                try:
                    request_start = time.time()
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    response_time = time.time() - request_start
                    
                    metrics.append(APIResponseMetrics(
                        endpoint=endpoint,
                        response_time=response_time,
                        status_code=response.status_code,
                        response_size=len(response.content),
                        error_message=None if response.status_code < 400 else response.text,
                        timestamp=datetime.now()
                    ))
                    
                    # ユーザー行動の間隔をシミュレート
                    time.sleep(0.5 + (time.time() % 2))
                    
                except Exception as e:
                    metrics.append(APIResponseMetrics(
                        endpoint=endpoint,
                        response_time=30.0,  # タイムアウト
                        status_code=0,
                        response_size=0,
                        error_message=str(e),
                        timestamp=datetime.now()
                    ))
                
                # セッション終了チェック
                if time.time() - start_time >= session_duration:
                    break
        
        return metrics
    
    async def async_simulate_user(self, user_id: str, session_duration: int = 60) -> List[APIResponseMetrics]:
        """非同期ユーザーシミュレーション"""
        metrics = []
        start_time = time.time()
        
        endpoints = [
            "/health",
            f"/api/user/{user_id}/dashboard",
            f"/api/user/{user_id}/tasks",
            f"/api/user/{user_id}/mandala"
        ]
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            while time.time() - start_time < session_duration:
                for endpoint in endpoints:
                    try:
                        request_start = time.time()
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            response_time = time.time() - request_start
                            content = await response.read()
                            
                            metrics.append(APIResponseMetrics(
                                endpoint=endpoint,
                                response_time=response_time,
                                status_code=response.status,
                                response_size=len(content),
                                error_message=None if response.status < 400 else str(content),
                                timestamp=datetime.now()
                            ))
                    
                    except Exception as e:
                        metrics.append(APIResponseMetrics(
                            endpoint=endpoint,
                            response_time=30.0,
                            status_code=0,
                            response_size=0,
                            error_message=str(e),
                            timestamp=datetime.now()
                        ))
                    
                    await asyncio.sleep(0.5)
                    
                    if time.time() - start_time >= session_duration:
                        break
        
        return metrics

class LoadTestRunner:
    """ロードテスト実行器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.system_monitor = SystemMonitor()
        self.user_simulator = ConcurrentUserSimulator(base_url)
    
    def run_concurrent_user_test(self, concurrent_users: int, test_duration: int = 60) -> LoadTestResult:
        """同時ユーザーテスト実行"""
        logger.info(f"同時ユーザーテスト開始: {concurrent_users}ユーザー, {test_duration}秒")
        
        # システム監視開始
        self.system_monitor.start_monitoring()
        
        start_time = time.time()
        all_metrics = []
        
        try:
            # ThreadPoolExecutorで同時ユーザーをシミュレート
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                
                for i in range(concurrent_users):
                    user_id = f"load_test_user_{i}"
                    future = executor.submit(
                        self.user_simulator.simulate_user_session,
                        user_id,
                        test_duration
                    )
                    futures.append(future)
                
                # 全ユーザーセッション完了を待機
                for future in as_completed(futures):
                    try:
                        user_metrics = future.result()
                        all_metrics.extend(user_metrics)
                    except Exception as e:
                        logger.error(f"ユーザーセッションエラー: {e}")
        
        finally:
            self.system_monitor.stop_monitoring()
        
        actual_duration = time.time() - start_time
        
        # 結果分析
        return self._analyze_test_results(
            "concurrent_user_test",
            concurrent_users,
            all_metrics,
            actual_duration
        )
    
    async def run_async_load_test(self, concurrent_users: int, test_duration: int = 60) -> LoadTestResult:
        """非同期ロードテスト実行"""
        logger.info(f"非同期ロードテスト開始: {concurrent_users}ユーザー, {test_duration}秒")
        
        self.system_monitor.start_monitoring()
        
        start_time = time.time()
        
        try:
            # 非同期でユーザーセッションを実行
            tasks = []
            for i in range(concurrent_users):
                user_id = f"async_test_user_{i}"
                task = self.user_simulator.async_simulate_user(user_id, test_duration)
                tasks.append(task)
            
            # 全タスク完了を待機
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_metrics = []
            for result in results:
                if isinstance(result, list):
                    all_metrics.extend(result)
                else:
                    logger.error(f"非同期タスクエラー: {result}")
        
        finally:
            self.system_monitor.stop_monitoring()
        
        actual_duration = time.time() - start_time
        
        return self._analyze_test_results(
            "async_load_test",
            concurrent_users,
            all_metrics,
            actual_duration
        )
    
    def run_api_response_time_test(self, requests_count: int = 100) -> Dict[str, Any]:
        """API応答時間テスト"""
        logger.info(f"API応答時間テスト開始: {requests_count}リクエスト")
        
        endpoints = [
            "/health",
            "/api/user/test_user/dashboard",
            "/api/user/test_user/tasks",
            "/api/user/test_user/mandala",
            "/api/performance/metrics"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            response_times = []
            success_count = 0
            
            for i in range(requests_count):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                    response_time = time.time() - start_time
                    
                    response_times.append(response_time)
                    if response.status_code < 400:
                        success_count += 1
                
                except Exception as e:
                    logger.warning(f"リクエストエラー {endpoint}: {e}")
                    response_times.append(30.0)  # タイムアウト値
            
            if response_times:
                results[endpoint] = {
                    "total_requests": requests_count,
                    "successful_requests": success_count,
                    "success_rate": success_count / requests_count,
                    "avg_response_time": statistics.mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "p95_response_time": statistics.quantiles(response_times, n=20)[18],  # 95パーセンタイル
                    "p99_response_time": statistics.quantiles(response_times, n=100)[98],  # 99パーセンタイル
                    "meets_sla": statistics.quantiles(response_times, n=20)[18] <= 1.2  # 1.2秒SLA
                }
        
        return {
            "test_type": "api_response_time_test",
            "requests_per_endpoint": requests_count,
            "endpoints": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_test_results(self, test_name: str, concurrent_users: int, 
                            metrics: List[APIResponseMetrics], duration: float) -> LoadTestResult:
        """テスト結果分析"""
        if not metrics:
            return LoadTestResult(
                test_name=test_name,
                concurrent_users=concurrent_users,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                p95_response_time=0.0,
                requests_per_second=0.0,
                error_rate=1.0,
                test_duration=duration,
                timestamp=datetime.now()
            )
        
        successful_requests = len([m for m in metrics if m.status_code < 400])
        failed_requests = len(metrics) - successful_requests
        response_times = [m.response_time for m in metrics]
        
        return LoadTestResult(
            test_name=test_name,
            concurrent_users=concurrent_users,
            total_requests=len(metrics),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
            requests_per_second=len(metrics) / duration if duration > 0 else 0,
            error_rate=failed_requests / len(metrics),
            test_duration=duration,
            timestamp=datetime.now()
        )

class PerformanceTestSuite:
    """パフォーマンステストスイート"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.load_test_runner = LoadTestRunner(base_url)
        self.test_results: List[LoadTestResult] = []
    
    def run_basic_performance_tests(self) -> Dict[str, Any]:
        """基本パフォーマンステスト実行"""
        logger.info("基本パフォーマンステスト開始")
        
        results = {
            "test_suite": "basic_performance_tests",
            "start_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. API応答時間テスト
        logger.info("API応答時間テストを実行中...")
        api_test_result = self.load_test_runner.run_api_response_time_test(50)
        results["tests"]["api_response_time"] = api_test_result
        
        # 2. 同時接続数テスト（10ユーザー）
        logger.info("同時接続テスト（10ユーザー）を実行中...")
        load_test_10 = self.load_test_runner.run_concurrent_user_test(10, 30)
        results["tests"]["concurrent_10_users"] = asdict(load_test_10)
        self.test_results.append(load_test_10)
        
        # 3. 同時接続数テスト（25ユーザー）
        logger.info("同時接続テスト（25ユーザー）を実行中...")
        load_test_25 = self.load_test_runner.run_concurrent_user_test(25, 30)
        results["tests"]["concurrent_25_users"] = asdict(load_test_25)
        self.test_results.append(load_test_25)
        
        # 4. 同時接続数テスト（50ユーザー）
        logger.info("同時接続テスト（50ユーザー）を実行中...")
        load_test_50 = self.load_test_runner.run_concurrent_user_test(50, 30)
        results["tests"]["concurrent_50_users"] = asdict(load_test_50)
        self.test_results.append(load_test_50)
        
        # 5. システムリソース監視結果
        system_summary = self.load_test_runner.system_monitor.get_metrics_summary(10)
        results["tests"]["system_resources"] = system_summary
        
        results["end_time"] = datetime.now().isoformat()
        results["summary"] = self._generate_test_summary()
        
        logger.info("基本パフォーマンステスト完了")
        return results
    
    async def run_async_performance_tests(self) -> Dict[str, Any]:
        """非同期パフォーマンステスト実行"""
        logger.info("非同期パフォーマンステスト開始")
        
        results = {
            "test_suite": "async_performance_tests",
            "start_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 非同期ロードテスト
        async_test_25 = await self.load_test_runner.run_async_load_test(25, 30)
        results["tests"]["async_25_users"] = asdict(async_test_25)
        self.test_results.append(async_test_25)
        
        async_test_50 = await self.load_test_runner.run_async_load_test(50, 30)
        results["tests"]["async_50_users"] = asdict(async_test_50)
        self.test_results.append(async_test_50)
        
        results["end_time"] = datetime.now().isoformat()
        results["summary"] = self._generate_test_summary()
        
        logger.info("非同期パフォーマンステスト完了")
        return results
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """テスト結果サマリー生成"""
        if not self.test_results:
            return {"message": "テスト結果がありません"}
        
        # SLA準拠チェック（1.2秒P95レイテンシ）
        sla_compliant_tests = [
            t for t in self.test_results 
            if t.p95_response_time <= 1.2
        ]
        
        # エラー率チェック（5%未満）
        low_error_tests = [
            t for t in self.test_results 
            if t.error_rate < 0.05
        ]
        
        return {
            "total_tests": len(self.test_results),
            "sla_compliant_tests": len(sla_compliant_tests),
            "sla_compliance_rate": len(sla_compliant_tests) / len(self.test_results),
            "low_error_tests": len(low_error_tests),
            "avg_p95_response_time": statistics.mean([t.p95_response_time for t in self.test_results]),
            "avg_error_rate": statistics.mean([t.error_rate for t in self.test_results]),
            "max_concurrent_users_tested": max([t.concurrent_users for t in self.test_results]),
            "performance_grade": self._calculate_performance_grade(),
            "recommendations": self._generate_recommendations()
        }
    
    def _calculate_performance_grade(self) -> str:
        """パフォーマンスグレード計算"""
        if not self.test_results:
            return "N/A"
        
        sla_compliance = len([t for t in self.test_results if t.p95_response_time <= 1.2]) / len(self.test_results)
        error_rate = statistics.mean([t.error_rate for t in self.test_results])
        
        if sla_compliance >= 0.9 and error_rate < 0.01:
            return "A"
        elif sla_compliance >= 0.8 and error_rate < 0.03:
            return "B"
        elif sla_compliance >= 0.7 and error_rate < 0.05:
            return "C"
        else:
            return "D"
    
    def _generate_recommendations(self) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        if not self.test_results:
            return ["テスト結果がないため推奨事項を生成できません"]
        
        avg_p95 = statistics.mean([t.p95_response_time for t in self.test_results])
        avg_error_rate = statistics.mean([t.error_rate for t in self.test_results])
        
        if avg_p95 > 1.2:
            recommendations.append(f"P95レスポンス時間が目標値1.2秒を超えています（{avg_p95:.2f}秒）。キャッシュ戦略の見直しを推奨します。")
        
        if avg_error_rate > 0.05:
            recommendations.append(f"エラー率が高すぎます（{avg_error_rate:.1%}）。エラーハンドリングの改善が必要です。")
        
        max_users = max([t.concurrent_users for t in self.test_results])
        if max_users < 50:
            recommendations.append("50ユーザー以上での負荷テストを実施して、スケーラビリティを確認してください。")
        
        if len(recommendations) == 0:
            recommendations.append("パフォーマンスは良好です。継続的な監視を推奨します。")
        
        return recommendations

# メイン実行関数
def run_performance_test_suite(base_url: str = "http://localhost:8001") -> Dict[str, Any]:
    """パフォーマンステストスイート実行"""
    test_suite = PerformanceTestSuite(base_url)
    return test_suite.run_basic_performance_tests()

async def run_async_performance_test_suite(base_url: str = "http://localhost:8001") -> Dict[str, Any]:
    """非同期パフォーマンステストスイート実行"""
    test_suite = PerformanceTestSuite(base_url)
    return await test_suite.run_async_performance_tests()

if __name__ == "__main__":
    print("パフォーマンスとスケーラビリティの基本確認テスト開始")
    
    # 基本パフォーマンステスト実行
    print("\n=== 基本パフォーマンステスト ===")
    basic_results = run_performance_test_suite()
    print(json.dumps(basic_results, indent=2, ensure_ascii=False, default=str))
    
    # 非同期パフォーマンステスト実行
    print("\n=== 非同期パフォーマンステスト ===")
    async_results = asyncio.run(run_async_performance_test_suite())
    print(json.dumps(async_results, indent=2, ensure_ascii=False, default=str))
    
    print("\nパフォーマンステスト完了")