"""
タスク27.3 パフォーマンスとスケーラビリティの基本確認 - 包括的テスト
- 同時接続数の基本テスト（10-50ユーザー）
- API応答時間の測定と最適化
- メモリ使用量とCPU使用率の監視
- 基本的なロードテストの実行
"""

import asyncio
import time
import json
import statistics
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import requests
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceTestResult:
    """パフォーマンステスト結果"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    metrics: Dict[str, Any]
    errors: List[str]
    recommendations: List[str]

class MVPPerformanceTester:
    """MVP パフォーマンステスター"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results: List[PerformanceTestResult] = []
        self.services_running = False
    
    def check_services_status(self) -> Dict[str, bool]:
        """サービス状態確認"""
        services = {
            "core-game": 8001,
            "auth": 8002,
            "task-mgmt": 8003,
            "mood-tracking": 8004,
            "ai-story": 8005
        }
        
        status = {}
        for service, port in services.items():
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                status[service] = response.status_code == 200
            except:
                status[service] = False
        
        self.services_running = all(status.values())
        return status
    
    def start_mvp_services(self) -> bool:
        """MVPサービス起動"""
        try:
            logger.info("MVPサービスを起動中...")
            
            # deploy_local.pyを使用してサービス起動
            result = subprocess.run([
                "python", "deploy_local.py"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # サービス起動確認のため少し待機
                time.sleep(10)
                
                # サービス状態確認
                status = self.check_services_status()
                if all(status.values()):
                    logger.info("全サービスが正常に起動しました")
                    return True
                else:
                    logger.warning(f"一部サービスが起動していません: {status}")
                    return False
            else:
                logger.error(f"サービス起動エラー: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"サービス起動例外: {e}")
            return False
    
    def test_api_response_times(self) -> PerformanceTestResult:
        """API応答時間テスト"""
        test_name = "API応答時間テスト"
        start_time = datetime.now()
        errors = []
        recommendations = []
        
        logger.info(f"{test_name}を開始...")
        
        # テスト対象エンドポイント
        endpoints = [
            "/health",
            "/api/user/test_user/dashboard",
            "/api/user/test_user/tasks",
            "/api/user/test_user/mandala",
            "/api/performance/metrics"
        ]
        
        endpoint_results = {}
        overall_success = True
        
        for endpoint in endpoints:
            response_times = []
            success_count = 0
            total_requests = 50
            
            logger.info(f"  エンドポイント {endpoint} をテスト中...")
            
            for i in range(total_requests):
                try:
                    request_start = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    response_time = time.time() - request_start
                    
                    response_times.append(response_time)
                    if response.status_code < 400:
                        success_count += 1
                    
                except Exception as e:
                    errors.append(f"{endpoint}: {str(e)}")
                    response_times.append(10.0)  # タイムアウト値
            
            if response_times:
                avg_time = statistics.mean(response_times)
                p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                
                endpoint_results[endpoint] = {
                    "total_requests": total_requests,
                    "successful_requests": success_count,
                    "success_rate": success_count / total_requests,
                    "avg_response_time": avg_time,
                    "p95_response_time": p95_time,
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "meets_sla": p95_time <= 1.2  # 1.2秒SLA
                }
                
                # SLA違反チェック
                if p95_time > 1.2:
                    overall_success = False
                    recommendations.append(f"{endpoint}: P95応答時間が1.2秒を超過 ({p95_time:.2f}秒)")
                
                # 成功率チェック
                if success_count / total_requests < 0.95:
                    overall_success = False
                    recommendations.append(f"{endpoint}: 成功率が95%未満 ({success_count/total_requests:.1%})")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 全体統計計算
        all_response_times = []
        total_requests = 0
        total_successful = 0
        
        for result in endpoint_results.values():
            total_requests += result["total_requests"]
            total_successful += result["successful_requests"]
            # 個別の応答時間は取得できないので、平均値を使用
            all_response_times.extend([result["avg_response_time"]] * result["total_requests"])
        
        overall_metrics = {
            "endpoints": endpoint_results,
            "overall": {
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "overall_success_rate": total_successful / total_requests if total_requests > 0 else 0,
                "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                "sla_compliant_endpoints": len([r for r in endpoint_results.values() if r["meets_sla"]]),
                "total_endpoints": len(endpoint_results)
            }
        }
        
        if overall_success:
            recommendations.append("全エンドポイントがSLA要件を満たしています")
        
        return PerformanceTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            success=overall_success,
            metrics=overall_metrics,
            errors=errors,
            recommendations=recommendations
        )
    
    def test_concurrent_users(self, user_count: int, duration_seconds: int = 30) -> PerformanceTestResult:
        """同時ユーザーテスト"""
        test_name = f"同時ユーザーテスト ({user_count}ユーザー)"
        start_time = datetime.now()
        errors = []
        recommendations = []
        
        logger.info(f"{test_name}を開始...")
        
        # システムリソース監視開始
        system_metrics = []
        monitoring = True
        
        def monitor_system():
            while monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    system_metrics.append({
                        "timestamp": datetime.now(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_mb": memory.used / (1024 * 1024)
                    })
                except Exception as e:
                    errors.append(f"システム監視エラー: {e}")
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        
        # 同時ユーザーシミュレーション
        all_response_times = []
        successful_requests = 0
        total_requests = 0
        
        def simulate_user(user_id: int):
            user_response_times = []
            user_successful = 0
            user_total = 0
            
            endpoints = [
                "/health",
                f"/api/user/user_{user_id}/dashboard",
                f"/api/user/user_{user_id}/tasks"
            ]
            
            end_time = time.time() + duration_seconds
            
            while time.time() < end_time:
                for endpoint in endpoints:
                    try:
                        request_start = time.time()
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                        response_time = time.time() - request_start
                        
                        user_response_times.append(response_time)
                        user_total += 1
                        
                        if response.status_code < 400:
                            user_successful += 1
                        
                        # ユーザー行動の間隔をシミュレート
                        time.sleep(0.5)
                        
                    except Exception as e:
                        errors.append(f"ユーザー{user_id} エラー: {e}")
                        user_response_times.append(10.0)
                        user_total += 1
                    
                    if time.time() >= end_time:
                        break
            
            return user_response_times, user_successful, user_total
        
        # ThreadPoolExecutorで同時ユーザーを実行
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = []
            for i in range(user_count):
                future = executor.submit(simulate_user, i)
                futures.append(future)
            
            # 全ユーザーの完了を待機
            for future in as_completed(futures):
                try:
                    user_times, user_success, user_total = future.result()
                    all_response_times.extend(user_times)
                    successful_requests += user_success
                    total_requests += user_total
                except Exception as e:
                    errors.append(f"ユーザーシミュレーションエラー: {e}")
        
        # システム監視停止
        monitoring = False
        monitor_thread.join(timeout=5)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 結果分析
        success = True
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times)
            error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 1
            
            # SLA チェック
            if p95_response_time > 1.2:
                success = False
                recommendations.append(f"P95応答時間がSLAを超過: {p95_response_time:.2f}秒 > 1.2秒")
            
            if error_rate > 0.05:
                success = False
                recommendations.append(f"エラー率が高すぎます: {error_rate:.1%} > 5%")
            
            # システムリソース分析
            if system_metrics:
                avg_cpu = statistics.mean([m["cpu_percent"] for m in system_metrics])
                max_cpu = max([m["cpu_percent"] for m in system_metrics])
                avg_memory = statistics.mean([m["memory_percent"] for m in system_metrics])
                max_memory = max([m["memory_percent"] for m in system_metrics])
                
                if max_cpu > 80:
                    recommendations.append(f"CPU使用率が高すぎます: 最大{max_cpu:.1f}%")
                
                if max_memory > 80:
                    recommendations.append(f"メモリ使用率が高すぎます: 最大{max_memory:.1f}%")
            
            metrics = {
                "concurrent_users": user_count,
                "test_duration": duration,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "p95_response_time": p95_response_time,
                "requests_per_second": total_requests / duration if duration > 0 else 0,
                "system_resources": {
                    "avg_cpu_percent": statistics.mean([m["cpu_percent"] for m in system_metrics]) if system_metrics else 0,
                    "max_cpu_percent": max([m["cpu_percent"] for m in system_metrics]) if system_metrics else 0,
                    "avg_memory_percent": statistics.mean([m["memory_percent"] for m in system_metrics]) if system_metrics else 0,
                    "max_memory_percent": max([m["memory_percent"] for m in system_metrics]) if system_metrics else 0,
                    "samples": len(system_metrics)
                }
            }
        else:
            success = False
            errors.append("レスポンスデータが取得できませんでした")
            metrics = {"error": "テストデータなし"}
        
        if success:
            recommendations.append(f"{user_count}ユーザーでの同時接続テストが成功しました")
        
        return PerformanceTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            success=success,
            metrics=metrics,
            errors=errors,
            recommendations=recommendations
        )
    
    def test_memory_cpu_monitoring(self, duration_seconds: int = 60) -> PerformanceTestResult:
        """メモリ・CPU監視テスト"""
        test_name = "メモリ・CPU監視テスト"
        start_time = datetime.now()
        errors = []
        recommendations = []
        
        logger.info(f"{test_name}を開始...")
        
        system_metrics = []
        monitoring = True
        
        def monitor_resources():
            while monitoring:
                try:
                    # CPU使用率
                    cpu_percent = psutil.cpu_percent(interval=1)
                    
                    # メモリ使用率
                    memory = psutil.virtual_memory()
                    
                    # ディスク使用率
                    disk = psutil.disk_usage('/')
                    
                    # プロセス情報
                    process_count = len(psutil.pids())
                    
                    system_metrics.append({
                        "timestamp": datetime.now(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_mb": memory.used / (1024 * 1024),
                        "memory_available_mb": memory.available / (1024 * 1024),
                        "disk_percent": disk.percent,
                        "process_count": process_count
                    })
                    
                except Exception as e:
                    errors.append(f"リソース監視エラー: {e}")
                
                time.sleep(1)
        
        # 監視開始
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
        
        # 負荷生成（軽い負荷でリソース使用量を測定）
        def generate_light_load():
            for _ in range(duration_seconds):
                try:
                    # 軽いAPI呼び出し
                    requests.get(f"{self.base_url}/health", timeout=5)
                    time.sleep(1)
                except:
                    pass
        
        load_thread = threading.Thread(target=generate_light_load, daemon=True)
        load_thread.start()
        
        # 指定時間待機
        time.sleep(duration_seconds)
        
        # 監視停止
        monitoring = False
        monitor_thread.join(timeout=5)
        load_thread.join(timeout=5)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 結果分析
        success = True
        
        if system_metrics:
            cpu_values = [m["cpu_percent"] for m in system_metrics]
            memory_values = [m["memory_percent"] for m in system_metrics]
            memory_used_values = [m["memory_used_mb"] for m in system_metrics]
            
            avg_cpu = statistics.mean(cpu_values)
            max_cpu = max(cpu_values)
            avg_memory = statistics.mean(memory_values)
            max_memory = max(memory_values)
            avg_memory_used = statistics.mean(memory_used_values)
            max_memory_used = max(memory_used_values)
            
            # リソース使用量チェック
            if max_cpu > 90:
                success = False
                recommendations.append(f"CPU使用率が危険レベル: 最大{max_cpu:.1f}%")
            elif max_cpu > 70:
                recommendations.append(f"CPU使用率が高め: 最大{max_cpu:.1f}%")
            
            if max_memory > 90:
                success = False
                recommendations.append(f"メモリ使用率が危険レベル: 最大{max_memory:.1f}%")
            elif max_memory > 70:
                recommendations.append(f"メモリ使用率が高め: 最大{max_memory:.1f}%")
            
            metrics = {
                "monitoring_duration": duration,
                "sample_count": len(system_metrics),
                "cpu": {
                    "avg_percent": avg_cpu,
                    "max_percent": max_cpu,
                    "min_percent": min(cpu_values)
                },
                "memory": {
                    "avg_percent": avg_memory,
                    "max_percent": max_memory,
                    "min_percent": min(memory_values),
                    "avg_used_mb": avg_memory_used,
                    "max_used_mb": max_memory_used
                },
                "disk_percent": system_metrics[-1]["disk_percent"] if system_metrics else 0,
                "process_count": system_metrics[-1]["process_count"] if system_metrics else 0
            }
            
            if success:
                recommendations.append("システムリソース使用量は正常範囲内です")
        else:
            success = False
            errors.append("システムメトリクスが取得できませんでした")
            metrics = {"error": "監視データなし"}
        
        return PerformanceTestResult(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            success=success,
            metrics=metrics,
            errors=errors,
            recommendations=recommendations
        )
    
    def run_comprehensive_performance_tests(self) -> Dict[str, Any]:
        """包括的パフォーマンステスト実行"""
        logger.info("包括的パフォーマンステスト開始")
        
        test_start_time = datetime.now()
        
        # サービス状態確認
        service_status = self.check_services_status()
        if not self.services_running:
            logger.warning("一部サービスが起動していません。サービスを起動します...")
            if not self.start_mvp_services():
                return {
                    "error": "サービス起動に失敗しました",
                    "service_status": service_status,
                    "timestamp": datetime.now().isoformat()
                }
        
        results = {
            "test_suite": "comprehensive_performance_tests",
            "start_time": test_start_time.isoformat(),
            "service_status": service_status,
            "tests": {}
        }
        
        # 1. API応答時間テスト
        api_test = self.test_api_response_times()
        results["tests"]["api_response_times"] = asdict(api_test)
        self.test_results.append(api_test)
        
        # 2. 同時接続テスト（10ユーザー）
        concurrent_10 = self.test_concurrent_users(10, 30)
        results["tests"]["concurrent_10_users"] = asdict(concurrent_10)
        self.test_results.append(concurrent_10)
        
        # 3. 同時接続テスト（25ユーザー）
        concurrent_25 = self.test_concurrent_users(25, 30)
        results["tests"]["concurrent_25_users"] = asdict(concurrent_25)
        self.test_results.append(concurrent_25)
        
        # 4. 同時接続テスト（50ユーザー）
        concurrent_50 = self.test_concurrent_users(50, 30)
        results["tests"]["concurrent_50_users"] = asdict(concurrent_50)
        self.test_results.append(concurrent_50)
        
        # 5. メモリ・CPU監視テスト
        resource_test = self.test_memory_cpu_monitoring(60)
        results["tests"]["memory_cpu_monitoring"] = asdict(resource_test)
        self.test_results.append(resource_test)
        
        test_end_time = datetime.now()
        results["end_time"] = test_end_time.isoformat()
        results["total_duration"] = (test_end_time - test_start_time).total_seconds()
        
        # 総合評価
        results["summary"] = self.generate_test_summary()
        
        logger.info("包括的パフォーマンステスト完了")
        return results
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """テスト結果サマリー生成"""
        if not self.test_results:
            return {"error": "テスト結果がありません"}
        
        total_tests = len(self.test_results)
        successful_tests = len([t for t in self.test_results if t.success])
        
        all_errors = []
        all_recommendations = []
        
        for test in self.test_results:
            all_errors.extend(test.errors)
            all_recommendations.extend(test.recommendations)
        
        # パフォーマンスグレード計算
        success_rate = successful_tests / total_tests
        if success_rate >= 0.9:
            grade = "A"
        elif success_rate >= 0.8:
            grade = "B"
        elif success_rate >= 0.7:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "performance_grade": grade,
            "total_errors": len(all_errors),
            "total_recommendations": len(all_recommendations),
            "key_findings": self.extract_key_findings(),
            "next_steps": self.generate_next_steps()
        }
    
    def extract_key_findings(self) -> List[str]:
        """主要な発見事項抽出"""
        findings = []
        
        # API応答時間の発見事項
        api_tests = [t for t in self.test_results if "API応答時間" in t.test_name]
        if api_tests:
            api_test = api_tests[0]
            if api_test.success:
                findings.append("✅ API応答時間がSLA要件（1.2秒）を満たしています")
            else:
                findings.append("❌ API応答時間がSLA要件を超過しています")
        
        # 同時接続テストの発見事項
        concurrent_tests = [t for t in self.test_results if "同時ユーザー" in t.test_name]
        max_successful_users = 0
        for test in concurrent_tests:
            if test.success and "concurrent_users" in test.metrics:
                max_successful_users = max(max_successful_users, test.metrics["concurrent_users"])
        
        if max_successful_users >= 50:
            findings.append(f"✅ 50ユーザーまでの同時接続に対応できています")
        elif max_successful_users >= 25:
            findings.append(f"⚠️ 25ユーザーまでの同時接続は可能ですが、50ユーザーで問題があります")
        else:
            findings.append(f"❌ 同時接続性能に問題があります（最大成功: {max_successful_users}ユーザー）")
        
        # リソース使用量の発見事項
        resource_tests = [t for t in self.test_results if "メモリ・CPU" in t.test_name]
        if resource_tests:
            resource_test = resource_tests[0]
            if resource_test.success:
                findings.append("✅ システムリソース使用量は正常範囲内です")
            else:
                findings.append("❌ システムリソース使用量に問題があります")
        
        return findings
    
    def generate_next_steps(self) -> List[str]:
        """次のステップ生成"""
        steps = []
        
        failed_tests = [t for t in self.test_results if not t.success]
        
        if not failed_tests:
            steps.append("全テストが成功しました。本番環境でのより大規模なテストを検討してください")
            steps.append("継続的な監視システムの導入を推奨します")
        else:
            steps.append("失敗したテストの原因を調査し、改善を実施してください")
            
            # 具体的な改善提案
            for test in failed_tests:
                if "API応答時間" in test.test_name:
                    steps.append("- キャッシュ戦略の見直し")
                    steps.append("- データベースクエリの最適化")
                elif "同時ユーザー" in test.test_name:
                    steps.append("- 接続プールの設定見直し")
                    steps.append("- 非同期処理の導入検討")
                elif "メモリ・CPU" in test.test_name:
                    steps.append("- メモリリークの調査")
                    steps.append("- CPU集約的処理の最適化")
        
        steps.append("定期的なパフォーマンステストの実施")
        
        return steps

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("タスク27.3 パフォーマンスとスケーラビリティの基本確認")
    print("=" * 60)
    
    tester = MVPPerformanceTester()
    
    # 包括的パフォーマンステスト実行
    results = tester.run_comprehensive_performance_tests()
    
    # 結果出力
    print("\n" + "=" * 60)
    print("テスト結果")
    print("=" * 60)
    print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    
    # サマリー出力
    summary = results.get("summary", {})
    print(f"\n総合評価: {summary.get('performance_grade', 'N/A')}")
    print(f"成功率: {summary.get('success_rate', 0):.1%}")
    
    # 主要な発見事項
    findings = summary.get("key_findings", [])
    if findings:
        print("\n主要な発見事項:")
        for finding in findings:
            print(f"  {finding}")
    
    # 次のステップ
    next_steps = summary.get("next_steps", [])
    if next_steps:
        print("\n次のステップ:")
        for step in next_steps:
            print(f"  {step}")
    
    print("\n" + "=" * 60)
    print("パフォーマンステスト完了")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()