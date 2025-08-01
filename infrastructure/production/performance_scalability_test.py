#!/usr/bin/env python3
"""
パフォーマンステストとスケーラビリティ確認スクリプト
"""

import asyncio
import json
import logging
import sys
import time
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp
import concurrent.futures
import psutil
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceScalabilityTester:
    """パフォーマンス・スケーラビリティテストクラス"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "target": base_url,
            "tests": {},
            "summary": {},
            "overall_status": "UNKNOWN"
        }
    
    async def test_response_time(self) -> Dict:
        """レスポンス時間テスト"""
        logger.info("レスポンス時間テスト開始...")
        
        test_result = {
            "name": "response_time",
            "status": "UNKNOWN",
            "metrics": {},
            "details": {}
        }
        
        try:
            # 複数エンドポイントのレスポンス時間測定
            endpoints = [
                "/health",
                "/api/auth/health",
                "/api/game/health",
                "/api/tasks/health",
                "/api/mandala/health"
            ]
            
            endpoint_results = {}
            
            for endpoint in endpoints:
                response_times = []
                
                # 各エンドポイントを10回測定
                for _ in range(10):
                    start_time = time.time()
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            response_times.append((end_time - start_time) * 1000)  # ミリ秒
                    except Exception:
                        pass
                
                if response_times:
                    endpoint_results[endpoint] = {
                        "samples": len(response_times),
                        "min_ms": min(response_times),
                        "max_ms": max(response_times),
                        "avg_ms": statistics.mean(response_times),
                        "median_ms": statistics.median(response_times),
                        "p95_ms": sorted(response_times)[int(len(response_times) * 0.95)],
                        "p99_ms": sorted(response_times)[int(len(response_times) * 0.99)]
                    }
            
            test_result["details"]["endpoints"] = endpoint_results
            
            # 全体統計
            all_response_times = []
            for endpoint_data in endpoint_results.values():
                # 各エンドポイントの平均値を使用
                all_response_times.append(endpoint_data["avg_ms"])
            
            if all_response_times:
                test_result["metrics"] = {
                    "overall_avg_ms": statistics.mean(all_response_times),
                    "overall_p95_ms": sorted(all_response_times)[int(len(all_response_times) * 0.95)],
                    "target_p95_ms": 1200,  # 1.2秒目標
                    "meets_target": sorted(all_response_times)[int(len(all_response_times) * 0.95)] <= 1200
                }
                
                if test_result["metrics"]["meets_target"]:
                    test_result["status"] = "PASS"
                else:
                    test_result["status"] = "FAIL"
            else:
                test_result["status"] = "ERROR"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
        
        return test_result
    
    async def test_throughput(self) -> Dict:
        """スループットテスト"""
        logger.info("スループットテスト開始...")
        
        test_result = {
            "name": "throughput",
            "status": "UNKNOWN",
            "metrics": {},
            "details": {}
        }
        
        try:
            # 段階的負荷テスト
            load_levels = [10, 25, 50, 100, 200]
            throughput_results = {}
            
            for concurrent_users in load_levels:
                logger.info(f"同時ユーザー数 {concurrent_users} でテスト中...")
                
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    
                    # 同時リクエスト実行
                    tasks = []
                    for _ in range(concurrent_users):
                        task = self.make_async_request(session, f"{self.base_url}/health")
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.time()
                    
                    # 結果分析
                    successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
                    total_time = end_time - start_time
                    
                    throughput_results[concurrent_users] = {
                        "concurrent_users": concurrent_users,
                        "total_requests": len(results),
                        "successful_requests": successful_requests,
                        "failed_requests": len(results) - successful_requests,
                        "success_rate": successful_requests / len(results),
                        "total_time_seconds": total_time,
                        "requests_per_second": successful_requests / total_time if total_time > 0 else 0,
                        "avg_response_time_ms": statistics.mean([r.get("response_time", 0) for r in results if isinstance(r, dict) and r.get("response_time")])
                    }
                    
                    # 成功率が90%を下回ったら停止
                    if successful_requests / len(results) < 0.9:
                        logger.warning(f"成功率が90%を下回りました: {successful_requests / len(results):.1%}")
                        break
            
            test_result["details"]["load_levels"] = throughput_results
            
            # 最大スループット計算
            max_rps = max(data["requests_per_second"] for data in throughput_results.values())
            target_rps = 120  # 120 req/min = 2 req/sec
            
            test_result["metrics"] = {
                "max_requests_per_second": max_rps,
                "target_requests_per_second": target_rps,
                "meets_target": max_rps >= target_rps,
                "max_concurrent_users": max(throughput_results.keys())
            }
            
            if test_result["metrics"]["meets_target"]:
                test_result["status"] = "PASS"
            else:
                test_result["status"] = "FAIL"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
        
        return test_result
    
    async def make_async_request(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """非同期リクエスト実行"""
        try:
            start_time = time.time()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                end_time = time.time()
                
                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": (end_time - start_time) * 1000  # ミリ秒
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }  
  
    async def test_scalability(self) -> Dict:
        """スケーラビリティテスト"""
        logger.info("スケーラビリティテスト開始...")
        
        test_result = {
            "name": "scalability",
            "status": "UNKNOWN",
            "metrics": {},
            "details": {}
        }
        
        try:
            # 段階的負荷増加テスト
            scalability_phases = [
                {"users": 100, "duration": 30},   # 100ユーザー、30秒
                {"users": 500, "duration": 60},   # 500ユーザー、60秒
                {"users": 1000, "duration": 60},  # 1000ユーザー、60秒
                {"users": 2000, "duration": 30}   # 2000ユーザー、30秒
            ]
            
            phase_results = {}
            
            for i, phase in enumerate(scalability_phases):
                logger.info(f"フェーズ {i+1}: {phase['users']}ユーザー、{phase['duration']}秒")
                
                # システムリソース監視開始
                initial_cpu = psutil.cpu_percent(interval=1)
                initial_memory = psutil.virtual_memory().percent
                
                # 負荷テスト実行
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    # 指定時間内で継続的にリクエスト送信
                    tasks = []
                    end_time = start_time + phase["duration"]
                    
                    while time.time() < end_time:
                        # 同時ユーザー数分のタスクを作成
                        batch_tasks = []
                        for _ in range(min(phase["users"], 50)):  # 一度に最大50リクエスト
                            task = self.make_async_request(session, f"{self.base_url}/health")
                            batch_tasks.append(task)
                        
                        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                        tasks.extend(batch_results)
                        
                        # 短時間待機
                        await asyncio.sleep(0.1)
                
                # システムリソース監視終了
                final_cpu = psutil.cpu_percent(interval=1)
                final_memory = psutil.virtual_memory().percent
                
                # 結果分析
                successful_requests = sum(1 for r in tasks if isinstance(r, dict) and r.get("success", False))
                total_requests = len(tasks)
                actual_duration = time.time() - start_time
                
                phase_results[f"phase_{i+1}"] = {
                    "target_users": phase["users"],
                    "duration_seconds": actual_duration,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                    "requests_per_second": successful_requests / actual_duration if actual_duration > 0 else 0,
                    "system_resources": {
                        "cpu_before": initial_cpu,
                        "cpu_after": final_cpu,
                        "cpu_increase": final_cpu - initial_cpu,
                        "memory_before": initial_memory,
                        "memory_after": final_memory,
                        "memory_increase": final_memory - initial_memory
                    }
                }
                
                # 成功率が80%を下回ったら停止
                if successful_requests / total_requests < 0.8:
                    logger.warning(f"成功率が80%を下回りました: {successful_requests / total_requests:.1%}")
                    break
                
                # フェーズ間の休憩
                await asyncio.sleep(5)
            
            test_result["details"]["phases"] = phase_results
            
            # スケーラビリティ評価
            max_successful_users = 0
            for phase_name, phase_data in phase_results.items():
                if phase_data["success_rate"] >= 0.9:  # 90%以上の成功率
                    max_successful_users = max(max_successful_users, phase_data["target_users"])
            
            target_users = 20000  # 20,000同時ユーザー目標
            
            test_result["metrics"] = {
                "max_successful_concurrent_users": max_successful_users,
                "target_concurrent_users": target_users,
                "scalability_ratio": max_successful_users / target_users,
                "meets_target": max_successful_users >= target_users * 0.1  # 10%でも部分的成功
            }
            
            if max_successful_users >= target_users:
                test_result["status"] = "PASS"
            elif max_successful_users >= target_users * 0.1:
                test_result["status"] = "PARTIAL"
            else:
                test_result["status"] = "FAIL"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
        
        return test_result
    
    async def test_resource_usage(self) -> Dict:
        """リソース使用量テスト"""
        logger.info("リソース使用量テスト開始...")
        
        test_result = {
            "name": "resource_usage",
            "status": "UNKNOWN",
            "metrics": {},
            "details": {}
        }
        
        try:
            # ベースライン測定
            baseline_cpu = psutil.cpu_percent(interval=1)
            baseline_memory = psutil.virtual_memory().percent
            baseline_disk = psutil.disk_usage('/').percent
            
            # 負荷をかけながらリソース監視
            monitoring_duration = 60  # 60秒間監視
            monitoring_interval = 5   # 5秒間隔
            
            resource_samples = []
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # 継続的な負荷生成
                load_task = asyncio.create_task(self.generate_continuous_load(session))
                
                # リソース監視
                while time.time() - start_time < monitoring_duration:
                    sample_time = time.time()
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_info = psutil.virtual_memory()
                    disk_info = psutil.disk_usage('/')
                    
                    resource_samples.append({
                        "timestamp": sample_time - start_time,
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_info.percent,
                        "memory_used_gb": memory_info.used / (1024**3),
                        "disk_percent": disk_info.percent
                    })
                    
                    await asyncio.sleep(monitoring_interval)
                
                # 負荷生成停止
                load_task.cancel()
                try:
                    await load_task
                except asyncio.CancelledError:
                    pass
            
            # リソース使用量分析
            if resource_samples:
                cpu_values = [s["cpu_percent"] for s in resource_samples]
                memory_values = [s["memory_percent"] for s in resource_samples]
                
                test_result["details"]["samples"] = resource_samples
                test_result["metrics"] = {
                    "baseline": {
                        "cpu_percent": baseline_cpu,
                        "memory_percent": baseline_memory,
                        "disk_percent": baseline_disk
                    },
                    "under_load": {
                        "cpu_avg": statistics.mean(cpu_values),
                        "cpu_max": max(cpu_values),
                        "memory_avg": statistics.mean(memory_values),
                        "memory_max": max(memory_values)
                    },
                    "thresholds": {
                        "cpu_threshold": 80,
                        "memory_threshold": 80
                    }
                }
                
                # 閾値チェック
                cpu_ok = max(cpu_values) <= 80
                memory_ok = max(memory_values) <= 80
                
                if cpu_ok and memory_ok:
                    test_result["status"] = "PASS"
                elif cpu_ok or memory_ok:
                    test_result["status"] = "PARTIAL"
                else:
                    test_result["status"] = "FAIL"
            else:
                test_result["status"] = "ERROR"
                test_result["error"] = "No resource samples collected"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
        
        return test_result
    
    async def generate_continuous_load(self, session: aiohttp.ClientSession):
        """継続的な負荷生成"""
        try:
            while True:
                # 複数のエンドポイントに同時リクエスト
                tasks = []
                endpoints = ["/health", "/api/auth/health", "/api/game/health"]
                
                for endpoint in endpoints:
                    for _ in range(5):  # 各エンドポイントに5リクエスト
                        task = self.make_async_request(session, f"{self.base_url}{endpoint}")
                        tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.5)  # 0.5秒間隔
                
        except asyncio.CancelledError:
            pass
    
    async def test_memory_leaks(self) -> Dict:
        """メモリリークテスト"""
        logger.info("メモリリークテスト開始...")
        
        test_result = {
            "name": "memory_leaks",
            "status": "UNKNOWN",
            "metrics": {},
            "details": {}
        }
        
        try:
            # 長時間の継続的負荷でメモリ使用量の変化を監視
            test_duration = 300  # 5分間
            sample_interval = 30  # 30秒間隔
            
            memory_samples = []
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # 継続的負荷生成開始
                load_task = asyncio.create_task(self.generate_continuous_load(session))
                
                # メモリ使用量監視
                while time.time() - start_time < test_duration:
                    elapsed_time = time.time() - start_time
                    memory_info = psutil.virtual_memory()
                    
                    memory_samples.append({
                        "elapsed_seconds": elapsed_time,
                        "memory_used_gb": memory_info.used / (1024**3),
                        "memory_percent": memory_info.percent
                    })
                    
                    logger.info(f"メモリ使用量: {memory_info.percent:.1f}% ({memory_info.used / (1024**3):.2f}GB)")
                    
                    await asyncio.sleep(sample_interval)
                
                # 負荷生成停止
                load_task.cancel()
                try:
                    await load_task
                except asyncio.CancelledError:
                    pass
            
            # メモリリーク分析
            if len(memory_samples) >= 3:
                initial_memory = memory_samples[0]["memory_used_gb"]
                final_memory = memory_samples[-1]["memory_used_gb"]
                memory_increase = final_memory - initial_memory
                
                # 線形回帰でメモリ増加傾向を分析
                x_values = [s["elapsed_seconds"] for s in memory_samples]
                y_values = [s["memory_used_gb"] for s in memory_samples]
                
                # 簡易線形回帰
                n = len(x_values)
                sum_x = sum(x_values)
                sum_y = sum(y_values)
                sum_xy = sum(x * y for x, y in zip(x_values, y_values))
                sum_x2 = sum(x * x for x in x_values)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                test_result["details"]["samples"] = memory_samples
                test_result["metrics"] = {
                    "initial_memory_gb": initial_memory,
                    "final_memory_gb": final_memory,
                    "memory_increase_gb": memory_increase,
                    "memory_increase_rate_gb_per_hour": slope * 3600,  # 1時間あたりの増加率
                    "test_duration_minutes": test_duration / 60
                }
                
                # メモリリーク判定
                # 1時間あたり100MB以上の増加をリークとみなす
                leak_threshold = 0.1  # 0.1GB = 100MB
                
                if abs(slope * 3600) <= leak_threshold:
                    test_result["status"] = "PASS"
                elif abs(slope * 3600) <= leak_threshold * 2:
                    test_result["status"] = "PARTIAL"
                else:
                    test_result["status"] = "FAIL"
            else:
                test_result["status"] = "ERROR"
                test_result["error"] = "Insufficient memory samples"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
        
        return test_result   
 
    async def run_all_tests(self) -> Dict:
        """全パフォーマンステストの実行"""
        logger.info("パフォーマンス・スケーラビリティテスト開始...")
        
        # 各テストを順次実行（リソースの競合を避けるため）
        tests = [
            self.test_response_time(),
            self.test_throughput(),
            self.test_scalability(),
            self.test_resource_usage(),
            self.test_memory_leaks()
        ]
        
        for test_coro in tests:
            try:
                result = await test_coro
                self.test_results["tests"][result["name"]] = result
                
                # テスト間の休憩
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"テスト実行エラー: {e}")
                self.test_results["tests"]["error"] = {
                    "name": "execution_error",
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # サマリー作成
        self.create_summary()
        
        return self.test_results
    
    def create_summary(self):
        """テスト結果サマリー作成"""
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(1 for t in self.test_results["tests"].values() if t.get("status") == "PASS")
        partial_tests = sum(1 for t in self.test_results["tests"].values() if t.get("status") == "PARTIAL")
        failed_tests = sum(1 for t in self.test_results["tests"].values() if t.get("status") == "FAIL")
        error_tests = sum(1 for t in self.test_results["tests"].values() if t.get("status") == "ERROR")
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "partial_tests": partial_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "completion_rate": (passed_tests + partial_tests) / total_tests if total_tests > 0 else 0
        }
        
        # 全体ステータス決定
        if failed_tests == 0 and error_tests == 0:
            if passed_tests == total_tests:
                self.test_results["overall_status"] = "PASS"
            else:
                self.test_results["overall_status"] = "PARTIAL"
        else:
            self.test_results["overall_status"] = "FAIL"
    
    def generate_report(self) -> str:
        """パフォーマンステストレポート生成"""
        report = f"""
# パフォーマンス・スケーラビリティテストレポート

## 概要
- **実行日時**: {self.test_results['timestamp']}
- **テスト対象**: {self.test_results['target']}
- **全体ステータス**: {self.test_results['overall_status']}

## サマリー
- **総テスト数**: {self.test_results['summary']['total_tests']}
- **成功**: {self.test_results['summary']['passed_tests']}
- **部分成功**: {self.test_results['summary']['partial_tests']}
- **失敗**: {self.test_results['summary']['failed_tests']}
- **エラー**: {self.test_results['summary']['error_tests']}
- **成功率**: {self.test_results['summary']['success_rate']:.1%}

## テスト結果詳細

"""
        
        for test_name, test_result in self.test_results["tests"].items():
            status_icon = {
                "PASS": "✅",
                "PARTIAL": "⚠️",
                "FAIL": "❌",
                "ERROR": "💥",
                "UNKNOWN": "❓"
            }.get(test_result.get("status", "UNKNOWN"), "❓")
            
            report += f"### {status_icon} {test_result.get('name', test_name).upper()}\n"
            report += f"**ステータス**: {test_result.get('status', 'UNKNOWN')}\n\n"
            
            # メトリクス表示
            if test_result.get("metrics"):
                report += "**メトリクス**:\n"
                for key, value in test_result["metrics"].items():
                    if isinstance(value, dict):
                        report += f"- **{key}**:\n"
                        for sub_key, sub_value in value.items():
                            report += f"  - {sub_key}: {sub_value}\n"
                    else:
                        if isinstance(value, float):
                            report += f"- **{key}**: {value:.2f}\n"
                        else:
                            report += f"- **{key}**: {value}\n"
                report += "\n"
            
            # エラー表示
            if test_result.get("error"):
                report += f"**エラー**: {test_result['error']}\n\n"
        
        # パフォーマンス要件との比較
        report += "## パフォーマンス要件との比較\n\n"
        
        response_time_test = self.test_results["tests"].get("response_time", {})
        if response_time_test.get("metrics"):
            p95_time = response_time_test["metrics"].get("overall_p95_ms", 0)
            target_time = response_time_test["metrics"].get("target_p95_ms", 1200)
            
            if p95_time <= target_time:
                report += f"- ✅ **レスポンス時間**: {p95_time:.1f}ms (目標: {target_time}ms以下)\n"
            else:
                report += f"- ❌ **レスポンス時間**: {p95_time:.1f}ms (目標: {target_time}ms以下)\n"
        
        throughput_test = self.test_results["tests"].get("throughput", {})
        if throughput_test.get("metrics"):
            max_rps = throughput_test["metrics"].get("max_requests_per_second", 0)
            target_rps = throughput_test["metrics"].get("target_requests_per_second", 2)
            
            if max_rps >= target_rps:
                report += f"- ✅ **スループット**: {max_rps:.1f} req/sec (目標: {target_rps} req/sec以上)\n"
            else:
                report += f"- ❌ **スループット**: {max_rps:.1f} req/sec (目標: {target_rps} req/sec以上)\n"
        
        scalability_test = self.test_results["tests"].get("scalability", {})
        if scalability_test.get("metrics"):
            max_users = scalability_test["metrics"].get("max_successful_concurrent_users", 0)
            target_users = scalability_test["metrics"].get("target_concurrent_users", 20000)
            
            if max_users >= target_users:
                report += f"- ✅ **同時接続数**: {max_users} users (目標: {target_users} users以上)\n"
            else:
                report += f"- ⚠️ **同時接続数**: {max_users} users (目標: {target_users} users以上)\n"
        
        # 推奨事項
        report += "\n## 推奨事項\n\n"
        
        if self.test_results["overall_status"] == "PASS":
            report += "- ✅ すべてのパフォーマンステストに合格しました。\n"
            report += "- 定期的なパフォーマンス監視を継続してください。\n"
        elif self.test_results["overall_status"] == "PARTIAL":
            report += "- ⚠️ 一部のパフォーマンス要件を満たしていません。\n"
            report += "- 以下の最適化を検討してください：\n"
            report += "  - データベースクエリの最適化\n"
            report += "  - キャッシュ戦略の見直し\n"
            report += "  - リソース配分の調整\n"
        else:
            report += "- ❌ パフォーマンス要件を満たしていません。\n"
            report += "- 本番リリース前に以下の対応が必要です：\n"
            report += "  - アプリケーションの最適化\n"
            report += "  - インフラストラクチャの強化\n"
            report += "  - ボトルネックの特定と解決\n"
        
        return report

async def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="パフォーマンス・スケーラビリティテスト実行")
    parser.add_argument("--target", default="http://localhost:8080", help="テスト対象URL")
    parser.add_argument("--output", help="レポート出力ファイル")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="出力形式")
    parser.add_argument("--quick", action="store_true", help="クイックテスト（短時間）")
    
    args = parser.parse_args()
    
    try:
        # パフォーマンステスト実行
        tester = PerformanceScalabilityTester(args.target)
        
        if args.quick:
            # クイックテスト（レスポンス時間とスループットのみ）
            logger.info("クイックテストモードで実行...")
            response_time_result = await tester.test_response_time()
            throughput_result = await tester.test_throughput()
            
            tester.test_results["tests"]["response_time"] = response_time_result
            tester.test_results["tests"]["throughput"] = throughput_result
            tester.create_summary()
            
            results = tester.test_results
        else:
            # フルテスト
            results = await tester.run_all_tests()
        
        # 結果出力
        if args.format == "json":
            output_content = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            output_content = tester.generate_report()
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_content)
            logger.info(f"レポート出力: {args.output}")
        else:
            print(output_content)
        
        # 終了コード決定
        if results["overall_status"] == "PASS":
            sys.exit(0)
        elif results["overall_status"] == "PARTIAL":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        logger.error(f"パフォーマンステストエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())