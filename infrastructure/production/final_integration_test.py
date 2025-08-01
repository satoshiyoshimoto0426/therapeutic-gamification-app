#!/usr/bin/env python3
"""
最終統合テストスクリプト
全機能の統合テスト、セキュリティ監査、パフォーマンステストを実行
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
import subprocess
import concurrent.futures
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FinalIntegrationTester:
    """最終統合テストクラス"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {},
            "overall_status": "UNKNOWN"
        }
    
    def run_command(self, command: List[str], timeout: int = 300) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
    
    async def test_service_health(self) -> Dict:
        """サービスヘルスチェックテスト"""
        logger.info("サービスヘルスチェック開始...")
        
        test_result = {
            "name": "service_health",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        try:
            # 基本ヘルスチェック
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                test_result["details"]["health_response"] = health_data
                
                if health_data.get("status") == "healthy":
                    test_result["status"] = "PASS"
                else:
                    test_result["status"] = "FAIL"
                    test_result["errors"].append("Health status is not healthy")
            else:
                test_result["status"] = "FAIL"
                test_result["errors"].append(f"Health check failed with status {response.status_code}")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["errors"].append(f"Health check error: {str(e)}")
        
        return test_result
    
    async def test_core_services(self) -> Dict:
        """コアサービステスト"""
        logger.info("コアサービステスト開始...")
        
        test_result = {
            "name": "core_services",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        # テスト対象サービス
        services = [
            ("auth", "/api/auth/health"),
            ("core-game", "/api/game/health"),
            ("task-mgmt", "/api/tasks/health"),
            ("ai-story", "/api/story/health"),
            ("mandala", "/api/mandala/health")
        ]
        
        service_results = {}
        
        for service_name, endpoint in services:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                service_results[service_name] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "healthy": response.status_code == 200
                }
            except Exception as e:
                service_results[service_name] = {
                    "error": str(e),
                    "healthy": False
                }
                test_result["errors"].append(f"{service_name} service error: {str(e)}")
        
        test_result["details"]["services"] = service_results
        
        # 全サービスが正常かチェック
        healthy_services = sum(1 for s in service_results.values() if s.get("healthy", False))
        total_services = len(services)
        
        if healthy_services == total_services:
            test_result["status"] = "PASS"
        elif healthy_services >= total_services * 0.8:  # 80%以上
            test_result["status"] = "PARTIAL"
        else:
            test_result["status"] = "FAIL"
        
        return test_result  
  
    async def test_user_journey(self) -> Dict:
        """ユーザージャーニーテスト"""
        logger.info("ユーザージャーニーテスト開始...")
        
        test_result = {
            "name": "user_journey",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        try:
            # 1. ユーザー登録
            register_data = {
                "username": f"test_user_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "test_password_123"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code != 201:
                test_result["errors"].append(f"User registration failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            user_data = response.json()
            test_result["details"]["user_registration"] = {"status": "success"}
            
            # 2. ログイン
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code != 200:
                test_result["errors"].append(f"User login failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            auth_data = response.json()
            token = auth_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            test_result["details"]["user_login"] = {"status": "success"}
            
            # 3. プロファイル取得
            response = requests.get(
                f"{self.base_url}/api/auth/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                test_result["errors"].append(f"Profile fetch failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            test_result["details"]["profile_fetch"] = {"status": "success"}
            
            # 4. タスク作成
            task_data = {
                "title": "テストタスク",
                "description": "統合テスト用のタスク",
                "task_type": "routine",
                "difficulty": 3
            }
            
            response = requests.post(
                f"{self.base_url}/api/tasks/create",
                json=task_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 201:
                test_result["errors"].append(f"Task creation failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            task_response = response.json()
            task_id = task_response.get("task_id")
            test_result["details"]["task_creation"] = {"status": "success", "task_id": task_id}
            
            # 5. タスク完了
            response = requests.post(
                f"{self.base_url}/api/tasks/{task_id}/complete",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                test_result["errors"].append(f"Task completion failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            completion_data = response.json()
            test_result["details"]["task_completion"] = {
                "status": "success",
                "xp_gained": completion_data.get("xp_gained", 0)
            }
            
            # 6. Mandalaグリッド取得
            response = requests.get(
                f"{self.base_url}/api/mandala/grid",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                test_result["errors"].append(f"Mandala grid fetch failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            test_result["details"]["mandala_grid"] = {"status": "success"}
            
            # 7. ストーリー生成
            response = requests.post(
                f"{self.base_url}/api/story/generate",
                headers=headers,
                timeout=15  # ストーリー生成は時間がかかる
            )
            
            if response.status_code != 200:
                test_result["errors"].append(f"Story generation failed: {response.status_code}")
                test_result["status"] = "FAIL"
                return test_result
            
            test_result["details"]["story_generation"] = {"status": "success"}
            
            test_result["status"] = "PASS"
            
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["errors"].append(f"User journey error: {str(e)}")
        
        return test_result
    
    async def test_performance(self) -> Dict:
        """パフォーマンステスト"""
        logger.info("パフォーマンステスト開始...")
        
        test_result = {
            "name": "performance",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        try:
            # 1. レスポンス時間テスト
            response_times = []
            for i in range(10):
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)  # ミリ秒
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
                
                test_result["details"]["response_time"] = {
                    "average_ms": avg_response_time,
                    "p95_ms": p95_response_time,
                    "samples": len(response_times)
                }
                
                # 1.2秒（1200ms）以内の目標
                if p95_response_time <= 1200:
                    test_result["details"]["response_time"]["status"] = "PASS"
                else:
                    test_result["details"]["response_time"]["status"] = "FAIL"
                    test_result["errors"].append(f"P95 response time too high: {p95_response_time:.1f}ms")
            
            # 2. 同時接続テスト
            concurrent_requests = 50
            
            def make_request():
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}/health", timeout=10)
                    end_time = time.time()
                    return {
                        "status_code": response.status_code,
                        "response_time": (end_time - start_time) * 1000,
                        "success": response.status_code == 200
                    }
                except Exception as e:
                    return {"error": str(e), "success": False}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r.get("success", False))
            success_rate = successful_requests / len(results)
            
            test_result["details"]["concurrent_requests"] = {
                "total_requests": len(results),
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "concurrent_users": concurrent_requests
            }
            
            if success_rate >= 0.95:  # 95%以上成功
                test_result["details"]["concurrent_requests"]["status"] = "PASS"
            else:
                test_result["details"]["concurrent_requests"]["status"] = "FAIL"
                test_result["errors"].append(f"Concurrent request success rate too low: {success_rate:.2%}")
            
            # 全体評価
            response_ok = test_result["details"]["response_time"].get("status") == "PASS"
            concurrent_ok = test_result["details"]["concurrent_requests"].get("status") == "PASS"
            
            if response_ok and concurrent_ok:
                test_result["status"] = "PASS"
            elif response_ok or concurrent_ok:
                test_result["status"] = "PARTIAL"
            else:
                test_result["status"] = "FAIL"
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["errors"].append(f"Performance test error: {str(e)}")
        
        return test_result
    
    async def test_security(self) -> Dict:
        """セキュリティテスト"""
        logger.info("セキュリティテスト開始...")
        
        test_result = {
            "name": "security",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        try:
            # 1. 認証テスト
            # 認証なしでのアクセス試行
            protected_endpoints = [
                "/api/auth/profile",
                "/api/tasks/create",
                "/api/mandala/grid",
                "/api/story/generate"
            ]
            
            auth_test_results = {}
            for endpoint in protected_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                auth_test_results[endpoint] = {
                    "status_code": response.status_code,
                    "properly_protected": response.status_code in [401, 403]
                }
            
            test_result["details"]["authentication"] = auth_test_results
            
            # 2. 入力検証テスト
            # SQLインジェクション試行
            sql_injection_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'--",
                "' UNION SELECT * FROM users --"
            ]
            
            injection_test_results = {}
            for payload in sql_injection_payloads:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/auth/login",
                        json={"username": payload, "password": "test"},
                        timeout=10
                    )
                    injection_test_results[payload] = {
                        "status_code": response.status_code,
                        "properly_handled": response.status_code in [400, 401, 422]
                    }
                except Exception as e:
                    injection_test_results[payload] = {
                        "error": str(e),
                        "properly_handled": True  # エラーで止まるのは良い
                    }
            
            test_result["details"]["sql_injection"] = injection_test_results
            
            # 3. XSS防御テスト
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "';alert('xss');//"
            ]
            
            xss_test_results = {}
            for payload in xss_payloads:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/tasks/create",
                        json={
                            "title": payload,
                            "description": "test",
                            "task_type": "routine",
                            "difficulty": 1
                        },
                        timeout=10
                    )
                    xss_test_results[payload] = {
                        "status_code": response.status_code,
                        "properly_handled": response.status_code in [400, 401, 422]
                    }
                except Exception as e:
                    xss_test_results[payload] = {
                        "error": str(e),
                        "properly_handled": True
                    }
            
            test_result["details"]["xss_protection"] = xss_test_results
            
            # 4. レート制限テスト
            rate_limit_results = []
            for i in range(130):  # 120req/minの制限を超える
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    rate_limit_results.append(response.status_code)
                    if response.status_code == 429:  # Too Many Requests
                        break
                except Exception:
                    break
            
            rate_limited = 429 in rate_limit_results
            test_result["details"]["rate_limiting"] = {
                "requests_made": len(rate_limit_results),
                "rate_limited": rate_limited,
                "properly_configured": rate_limited
            }
            
            # 全体評価
            auth_protected = all(r["properly_protected"] for r in auth_test_results.values())
            injection_handled = all(r["properly_handled"] for r in injection_test_results.values())
            xss_handled = all(r["properly_handled"] for r in xss_test_results.values())
            rate_limit_ok = test_result["details"]["rate_limiting"]["properly_configured"]
            
            security_checks = [auth_protected, injection_handled, xss_handled, rate_limit_ok]
            passed_checks = sum(security_checks)
            
            if passed_checks == len(security_checks):
                test_result["status"] = "PASS"
            elif passed_checks >= len(security_checks) * 0.75:  # 75%以上
                test_result["status"] = "PARTIAL"
            else:
                test_result["status"] = "FAIL"
            
            if not auth_protected:
                test_result["errors"].append("Some endpoints are not properly protected")
            if not injection_handled:
                test_result["errors"].append("SQL injection vulnerabilities detected")
            if not xss_handled:
                test_result["errors"].append("XSS vulnerabilities detected")
            if not rate_limit_ok:
                test_result["errors"].append("Rate limiting not properly configured")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["errors"].append(f"Security test error: {str(e)}")
        
        return test_result
    
    async def test_therapeutic_safety(self) -> Dict:
        """治療安全性テスト"""
        logger.info("治療安全性テスト開始...")
        
        test_result = {
            "name": "therapeutic_safety",
            "status": "UNKNOWN",
            "details": {},
            "errors": []
        }
        
        try:
            # 1. コンテンツモデレーションテスト
            harmful_content = [
                "I want to hurt myself",
                "Life is not worth living",
                "I hate everyone and everything",
                "Violence is the answer"
            ]
            
            moderation_results = {}
            for content in harmful_content:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/safety/moderate",
                        json={"content": content},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        moderation_data = response.json()
                        moderation_results[content] = {
                            "flagged": moderation_data.get("flagged", False),
                            "confidence": moderation_data.get("confidence", 0),
                            "properly_detected": moderation_data.get("flagged", False)
                        }
                    else:
                        moderation_results[content] = {
                            "error": f"HTTP {response.status_code}",
                            "properly_detected": False
                        }
                        
                except Exception as e:
                    moderation_results[content] = {
                        "error": str(e),
                        "properly_detected": False
                    }
            
            test_result["details"]["content_moderation"] = moderation_results
            
            # 2. F1スコア確認
            try:
                response = requests.get(f"{self.base_url}/api/safety/metrics", timeout=10)
                if response.status_code == 200:
                    metrics_data = response.json()
                    f1_score = metrics_data.get("f1_score", 0)
                    
                    test_result["details"]["f1_score"] = {
                        "score": f1_score,
                        "target": 0.98,
                        "meets_target": f1_score >= 0.98
                    }
                else:
                    test_result["details"]["f1_score"] = {
                        "error": f"HTTP {response.status_code}",
                        "meets_target": False
                    }
            except Exception as e:
                test_result["details"]["f1_score"] = {
                    "error": str(e),
                    "meets_target": False
                }
            
            # 3. CBT介入テスト
            try:
                response = requests.post(
                    f"{self.base_url}/api/safety/cbt-intervention",
                    json={"user_input": "I always fail at everything"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    cbt_data = response.json()
                    test_result["details"]["cbt_intervention"] = {
                        "intervention_provided": bool(cbt_data.get("intervention")),
                        "therapeutic_response": bool(cbt_data.get("therapeutic_response"))
                    }
                else:
                    test_result["details"]["cbt_intervention"] = {
                        "error": f"HTTP {response.status_code}",
                        "intervention_provided": False
                    }
            except Exception as e:
                test_result["details"]["cbt_intervention"] = {
                    "error": str(e),
                    "intervention_provided": False
                }
            
            # 全体評価
            moderation_ok = all(r.get("properly_detected", False) for r in moderation_results.values())
            f1_ok = test_result["details"]["f1_score"].get("meets_target", False)
            cbt_ok = test_result["details"]["cbt_intervention"].get("intervention_provided", False)
            
            safety_checks = [moderation_ok, f1_ok, cbt_ok]
            passed_checks = sum(safety_checks)
            
            if passed_checks == len(safety_checks):
                test_result["status"] = "PASS"
            elif passed_checks >= 2:  # 3つ中2つ以上
                test_result["status"] = "PARTIAL"
            else:
                test_result["status"] = "FAIL"
            
            if not moderation_ok:
                test_result["errors"].append("Content moderation not working properly")
            if not f1_ok:
                test_result["errors"].append("F1 score below target (98%)")
            if not cbt_ok:
                test_result["errors"].append("CBT intervention not functioning")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["errors"].append(f"Therapeutic safety test error: {str(e)}")
        
        return test_result    

    async def run_all_tests(self) -> Dict:
        """全テストの実行"""
        logger.info("最終統合テスト開始...")
        
        # 各テストを並行実行
        test_functions = [
            self.test_service_health(),
            self.test_core_services(),
            self.test_user_journey(),
            self.test_performance(),
            self.test_security(),
            self.test_therapeutic_safety()
        ]
        
        test_results = await asyncio.gather(*test_functions, return_exceptions=True)
        
        # 結果をまとめる
        for result in test_results:
            if isinstance(result, Exception):
                logger.error(f"Test execution error: {result}")
                self.test_results["tests"]["error"] = {
                    "name": "execution_error",
                    "status": "ERROR",
                    "errors": [str(result)]
                }
            else:
                self.test_results["tests"][result["name"]] = result
        
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
        """テストレポート生成"""
        report = f"""
# 最終統合テストレポート

## 概要
- **実行日時**: {self.test_results['timestamp']}
- **テスト対象**: {self.test_results['base_url']}
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
            
            if test_result.get("errors"):
                report += "**エラー**:\n"
                for error in test_result["errors"]:
                    report += f"- {error}\n"
                report += "\n"
            
            if test_result.get("details"):
                report += "**詳細**:\n"
                for key, value in test_result["details"].items():
                    if isinstance(value, dict):
                        report += f"- **{key}**: {value.get('status', 'N/A')}\n"
                    else:
                        report += f"- **{key}**: {value}\n"
                report += "\n"
        
        # 推奨事項
        report += "## 推奨事項\n\n"
        
        if self.test_results["overall_status"] == "PASS":
            report += "- ✅ すべてのテストが成功しました。本番リリースの準備が整っています。\n"
        elif self.test_results["overall_status"] == "PARTIAL":
            report += "- ⚠️ 一部のテストで問題が検出されました。以下の項目を確認してください：\n"
            for test_result in self.test_results["tests"].values():
                if test_result.get("status") in ["PARTIAL", "FAIL"]:
                    for error in test_result.get("errors", []):
                        report += f"  - {error}\n"
        else:
            report += "- ❌ 重要な問題が検出されました。本番リリース前に以下の問題を解決してください：\n"
            for test_result in self.test_results["tests"].values():
                if test_result.get("status") in ["FAIL", "ERROR"]:
                    for error in test_result.get("errors", []):
                        report += f"  - {error}\n"
        
        return report

async def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="最終統合テスト実行")
    parser.add_argument("--base-url", default="http://localhost:8080", help="テスト対象のベースURL")
    parser.add_argument("--output", help="レポート出力ファイル")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="出力形式")
    
    args = parser.parse_args()
    
    try:
        # テスト実行
        tester = FinalIntegrationTester(args.base_url)
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
        logger.error(f"テスト実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())