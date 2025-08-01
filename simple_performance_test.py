"""
簡単なパフォーマンステスト - タスク27.3
"""

import requests
import time
import statistics
import threading
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

class SimplePerformanceTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = {}
    
    def test_api_response_times(self):
        """API応答時間テスト"""
        print("1. API応答時間テスト実行中...")
        
        endpoints = [
            "/health",
            "/api/user/test_user/dashboard",
            "/api/user/test_user/tasks",
            "/api/user/test_user/mandala"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            response_times = []
            success_count = 0
            
            print(f"   テスト中: {endpoint}")
            
            for i in range(20):  # 20回テスト
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    response_time = time.time() - start_time
                    
                    response_times.append(response_time)
                    if response.status_code < 400:
                        success_count += 1
                
                except Exception as e:
                    print(f"     エラー: {e}")
                    response_times.append(10.0)
            
            if response_times:
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                results[endpoint] = {
                    "avg_response_time": avg_time,
                    "max_response_time": max_time,
                    "min_response_time": min_time,
                    "success_rate": success_count / len(response_times),
                    "meets_sla": avg_time <= 1.2
                }
                
                print(f"     平均: {avg_time:.3f}秒, 最大: {max_time:.3f}秒, 成功率: {success_count/len(response_times):.1%}")
        
        self.results["api_response_times"] = results
        return results
    
    def test_concurrent_users(self, user_count, duration=20):
        """同時ユーザーテスト"""
        print(f"\n2. 同時ユーザーテスト ({user_count}ユーザー, {duration}秒)")
        
        # システムリソース監視
        system_metrics = []
        monitoring = True
        
        def monitor_system():
            while monitoring:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    system_metrics.append({
                        "cpu_percent": cpu,
                        "memory_percent": memory.percent,
                        "timestamp": time.time()
                    })
                except:
                    pass
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        
        # ユーザーシミュレーション
        all_response_times = []
        successful_requests = 0
        total_requests = 0
        
        def simulate_user(user_id):
            user_times = []
            user_success = 0
            user_total = 0
            
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}/api/user/user_{user_id}/dashboard", timeout=5)
                    response_time = time.time() - start_time
                    
                    user_times.append(response_time)
                    user_total += 1
                    
                    if response.status_code < 400:
                        user_success += 1
                    
                    time.sleep(0.5)  # ユーザー行動間隔
                    
                except Exception:
                    user_times.append(5.0)
                    user_total += 1
            
            return user_times, user_success, user_total
        
        # 同時実行
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(user_count)]
            
            for future in as_completed(futures):
                try:
                    times, success, total = future.result()
                    all_response_times.extend(times)
                    successful_requests += success
                    total_requests += total
                except Exception as e:
                    print(f"   ユーザーシミュレーションエラー: {e}")
        
        # 監視停止
        monitoring = False
        monitor_thread.join(timeout=2)
        
        # 結果分析
        if all_response_times:
            avg_response = statistics.mean(all_response_times)
            max_response = max(all_response_times)
            error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 1
            
            # システムリソース分析
            if system_metrics:
                avg_cpu = statistics.mean([m["cpu_percent"] for m in system_metrics])
                max_cpu = max([m["cpu_percent"] for m in system_metrics])
                avg_memory = statistics.mean([m["memory_percent"] for m in system_metrics])
                max_memory = max([m["memory_percent"] for m in system_metrics])
            else:
                avg_cpu = max_cpu = avg_memory = max_memory = 0
            
            result = {
                "concurrent_users": user_count,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_rate": error_rate,
                "avg_response_time": avg_response,
                "max_response_time": max_response,
                "requests_per_second": total_requests / duration,
                "system_resources": {
                    "avg_cpu": avg_cpu,
                    "max_cpu": max_cpu,
                    "avg_memory": avg_memory,
                    "max_memory": max_memory
                },
                "meets_requirements": avg_response <= 1.2 and error_rate <= 0.05
            }
            
            print(f"   総リクエスト: {total_requests}, 成功: {successful_requests}")
            print(f"   平均応答時間: {avg_response:.3f}秒, エラー率: {error_rate:.1%}")
            print(f"   CPU使用率: 平均{avg_cpu:.1f}% / 最大{max_cpu:.1f}%")
            print(f"   メモリ使用率: 平均{avg_memory:.1f}% / 最大{max_memory:.1f}%")
            print(f"   要件達成: {'✅' if result['meets_requirements'] else '❌'}")
            
            self.results[f"concurrent_{user_count}_users"] = result
            return result
        
        return None
    
    def test_memory_cpu_monitoring(self, duration=30):
        """メモリ・CPU監視テスト"""
        print(f"\n3. システムリソース監視テスト ({duration}秒)")
        
        metrics = []
        
        # 軽い負荷をかけながら監視
        def generate_load():
            end_time = time.time() + duration
            while time.time() < end_time:
                try:
                    requests.get(f"{self.base_url}/health", timeout=2)
                    time.sleep(0.5)
                except:
                    pass
        
        load_thread = threading.Thread(target=generate_load, daemon=True)
        load_thread.start()
        
        # リソース監視
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                metrics.append({
                    "cpu_percent": cpu,
                    "memory_percent": memory.percent,
                    "memory_used_mb": memory.used / (1024 * 1024),
                    "disk_percent": disk.percent,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                print(f"   監視エラー: {e}")
        
        load_thread.join(timeout=2)
        
        # 結果分析
        if metrics:
            cpu_values = [m["cpu_percent"] for m in metrics]
            memory_values = [m["memory_percent"] for m in metrics]
            
            result = {
                "monitoring_duration": duration,
                "sample_count": len(metrics),
                "cpu": {
                    "avg": statistics.mean(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values)
                },
                "memory": {
                    "avg": statistics.mean(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values),
                    "avg_used_mb": statistics.mean([m["memory_used_mb"] for m in metrics])
                },
                "disk_percent": metrics[-1]["disk_percent"],
                "resource_healthy": max(cpu_values) < 80 and max(memory_values) < 80
            }
            
            print(f"   CPU使用率: 平均{result['cpu']['avg']:.1f}% / 最大{result['cpu']['max']:.1f}%")
            print(f"   メモリ使用率: 平均{result['memory']['avg']:.1f}% / 最大{result['memory']['max']:.1f}%")
            print(f"   ディスク使用率: {result['disk_percent']:.1f}%")
            print(f"   リソース健全性: {'✅' if result['resource_healthy'] else '❌'}")
            
            self.results["resource_monitoring"] = result
            return result
        
        return None
    
    def run_all_tests(self):
        """全テスト実行"""
        print("=" * 60)
        print("タスク27.3 パフォーマンスとスケーラビリティの基本確認")
        print("=" * 60)
        
        # 1. API応答時間テスト
        self.test_api_response_times()
        
        # 2. 同時ユーザーテスト（段階的に増加）
        for user_count in [10, 25, 50]:
            self.test_concurrent_users(user_count, 20)
        
        # 3. リソース監視テスト
        self.test_memory_cpu_monitoring(30)
        
        # 結果サマリー
        self.print_summary()
    
    def print_summary(self):
        """結果サマリー出力"""
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        
        # API応答時間の評価
        api_results = self.results.get("api_response_times", {})
        api_pass = all(result.get("meets_sla", False) for result in api_results.values())
        print(f"API応答時間テスト: {'✅ 合格' if api_pass else '❌ 不合格'}")
        
        # 同時ユーザーテストの評価
        concurrent_tests = [k for k in self.results.keys() if k.startswith("concurrent_")]
        concurrent_pass = 0
        for test_key in concurrent_tests:
            if self.results[test_key].get("meets_requirements", False):
                concurrent_pass += 1
        
        print(f"同時ユーザーテスト: {concurrent_pass}/{len(concurrent_tests)} 合格")
        
        # リソース監視の評価
        resource_result = self.results.get("resource_monitoring", {})
        resource_pass = resource_result.get("resource_healthy", False)
        print(f"リソース監視テスト: {'✅ 合格' if resource_pass else '❌ 不合格'}")
        
        # 総合評価
        total_tests = 1 + len(concurrent_tests) + 1  # API + 同時ユーザー + リソース
        passed_tests = (1 if api_pass else 0) + concurrent_pass + (1 if resource_pass else 0)
        
        success_rate = passed_tests / total_tests
        
        print(f"\n総合結果: {passed_tests}/{total_tests} 合格 ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 パフォーマンステスト合格！")
            grade = "A" if success_rate >= 0.9 else "B"
        elif success_rate >= 0.6:
            print("⚠️ パフォーマンステスト部分合格")
            grade = "C"
        else:
            print("❌ パフォーマンステスト不合格")
            grade = "D"
        
        print(f"パフォーマンスグレード: {grade}")
        
        # 推奨事項
        print("\n推奨事項:")
        if not api_pass:
            print("  - API応答時間の最適化が必要です")
        if concurrent_pass < len(concurrent_tests):
            print("  - 同時接続処理の改善が必要です")
        if not resource_pass:
            print("  - システムリソース使用量の最適化が必要です")
        if success_rate >= 0.8:
            print("  - 継続的な監視システムの導入を推奨します")
        
        print("\n" + "=" * 60)
        print("パフォーマンステスト完了")
        print("=" * 60)
        
        return success_rate >= 0.8

def main():
    tester = SimplePerformanceTester()
    success = tester.run_all_tests()
    
    # 詳細結果をファイルに保存
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": tester.results,
            "success": success
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n詳細結果は performance_test_results.json に保存されました")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)