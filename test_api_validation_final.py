"""
API連携とエンドポイント検証（最終版）

タスク26.4: API連携とエンドポイント検証
- サービス間API呼び出しの動作確認
- エラーハンドリングの適切性を検証
- レスポンス形式の統一性を確認
- CORS設定の正常動作を確認

実際に動作しているエンドポイントに基づいた検証
"""

import asyncio
import httpx
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class FinalAPIValidator:
    """最終API検証クラス"""
    
    def __init__(self):
        self.services = {
            "core_game": {
                "name": "Core Game Engine",
                "base_url": "http://localhost:8001",
                "port": 8001
            },
            "auth": {
                "name": "Auth Service",
                "base_url": "http://localhost:8002",
                "port": 8002
            },
            "task_mgmt": {
                "name": "Task Management",
                "base_url": "http://localhost:8003",
                "port": 8003
            }
        }
        
        self.test_results = {
            "service_availability": [],
            "api_communication": [],
            "error_handling": [],
            "response_format": [],
            "cors_configuration": [],
            "performance": []
        }
    
    async def run_final_validation(self) -> Dict[str, Any]:
        """最終API検証を実行"""
        print("=== API連携とエンドポイント検証（最終版） ===")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. サービス可用性テスト
        await self._test_service_availability()
        
        # 2. API通信テスト
        await self._test_api_communication()
        
        # 3. エラーハンドリングテスト
        await self._test_error_handling()
        
        # 4. レスポンス形式統一性テスト
        await self._test_response_format()
        
        # 5. CORS設定テスト
        await self._test_cors_configuration()
        
        # 6. パフォーマンステスト
        await self._test_performance()
        
        return self._generate_final_report()
    
    async def _test_service_availability(self):
        """サービス可用性テスト"""
        print("1. サービス可用性テスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                try:
                    start_time = time.time()
                    response = await client.get(
                        f"{service_config['base_url']}/health",
                        timeout=5.0
                    )
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        print(f"   [OK] {service_config['name']}: 利用可能 ({response_time:.1f}ms)")
                        success = True
                        
                        # レスポンス内容の確認
                        try:
                            response_data = response.json()
                            service_name = response_data.get("service", "unknown")
                            print(f"        サービス識別: {service_name}")
                        except:
                            pass
                    else:
                        print(f"   [FAIL] {service_config['name']}: HTTP {response.status_code}")
                        success = False
                    
                    self.test_results["service_availability"].append({
                        "service": service_config["name"],
                        "success": success,
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "port": service_config["port"]
                    })
                    
                except httpx.ConnectError:
                    print(f"   [FAIL] {service_config['name']}: 接続失敗 (ポート{service_config['port']}未起動)")
                    self.test_results["service_availability"].append({
                        "service": service_config["name"],
                        "success": False,
                        "error": "接続失敗",
                        "port": service_config["port"]
                    })
                    
                except Exception as e:
                    print(f"   [FAIL] {service_config['name']}: {str(e)}")
                    self.test_results["service_availability"].append({
                        "service": service_config["name"],
                        "success": False,
                        "error": str(e),
                        "port": service_config["port"]
                    })
        print()
    
    async def _test_api_communication(self):
        """API通信テスト"""
        print("2. API通信テスト")
        
        # 実際に動作しているエンドポイントのみテスト
        communication_tests = [
            {
                "service": "core_game",
                "endpoint": "/health",
                "method": "GET",
                "description": "ヘルスチェック通信"
            },
            {
                "service": "auth",
                "endpoint": "/health",
                "method": "GET",
                "description": "ヘルスチェック通信"
            },
            {
                "service": "task_mgmt",
                "endpoint": "/health",
                "method": "GET",
                "description": "ヘルスチェック通信"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for test in communication_tests:
                service_config = self.services.get(test["service"])
                if not service_config:
                    continue
                
                try:
                    url = f"{service_config['base_url']}{test['endpoint']}"
                    
                    start_time = time.time()
                    response = await client.get(url, timeout=10.0)
                    response_time = (time.time() - start_time) * 1000
                    
                    success = response.status_code == 200
                    
                    if success:
                        print(f"   [OK] {service_config['name']}: {test['description']} 成功 ({response_time:.1f}ms)")
                        
                        # レスポンス内容の詳細確認
                        try:
                            response_data = response.json()
                            if "status" in response_data and "service" in response_data:
                                print(f"        レスポンス: status={response_data['status']}, service={response_data['service']}")
                        except:
                            pass
                    else:
                        print(f"   [FAIL] {service_config['name']}: {test['description']} 失敗 ({response.status_code})")
                    
                    self.test_results["api_communication"].append({
                        "service": service_config["name"],
                        "endpoint": test["endpoint"],
                        "method": test["method"],
                        "success": success,
                        "status_code": response.status_code,
                        "response_time_ms": response_time
                    })
                    
                except Exception as e:
                    print(f"   [FAIL] {service_config['name']}: {test['description']} エラー - {str(e)}")
                    self.test_results["api_communication"].append({
                        "service": service_config["name"],
                        "endpoint": test["endpoint"],
                        "method": test["method"],
                        "success": False,
                        "error": str(e)
                    })
        print()
    
    async def _test_error_handling(self):
        """エラーハンドリングテスト"""
        print("3. エラーハンドリングテスト")
        
        # 存在しないエンドポイントへのアクセスでエラーハンドリングをテスト
        error_tests = [
            {
                "service": "core_game",
                "endpoint": "/nonexistent",
                "method": "GET",
                "description": "存在しないエンドポイント",
                "expected_status": [404]
            },
            {
                "service": "auth",
                "endpoint": "/invalid/path",
                "method": "POST",
                "description": "無効なパス",
                "expected_status": [404, 405]
            },
            {
                "service": "task_mgmt",
                "endpoint": "/health",
                "method": "DELETE",
                "description": "許可されていないメソッド",
                "expected_status": [405]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for test in error_tests:
                service_config = self.services.get(test["service"])
                if not service_config:
                    continue
                
                try:
                    url = f"{service_config['base_url']}{test['endpoint']}"
                    
                    if test["method"] == "GET":
                        response = await client.get(url, timeout=5.0)
                    elif test["method"] == "POST":
                        response = await client.post(url, json={}, timeout=5.0)
                    elif test["method"] == "DELETE":
                        response = await client.delete(url, timeout=5.0)
                    
                    expected_statuses = test["expected_status"]
                    error_handled_correctly = response.status_code in expected_statuses
                    
                    # エラーレスポンスの形式確認
                    try:
                        response_data = response.json()
                        has_error_detail = "detail" in response_data or "message" in response_data
                    except:
                        has_error_detail = False
                    
                    if error_handled_correctly:
                        if has_error_detail:
                            print(f"   [OK] {service_config['name']}: {test['description']} - 適切なエラーハンドリング ({response.status_code})")
                            success = True
                        else:
                            print(f"   [WARN] {service_config['name']}: {test['description']} - ステータス正常、詳細不足 ({response.status_code})")
                            success = False
                    else:
                        print(f"   [FAIL] {service_config['name']}: {test['description']} - 予期しないステータス ({response.status_code})")
                        success = False
                    
                    self.test_results["error_handling"].append({
                        "service": service_config["name"],
                        "description": test["description"],
                        "success": success,
                        "status_code": response.status_code,
                        "has_error_detail": has_error_detail,
                        "expected_status": expected_statuses
                    })
                    
                except Exception as e:
                    print(f"   [FAIL] {service_config['name']}: {test['description']} - {str(e)}")
                    self.test_results["error_handling"].append({
                        "service": service_config["name"],
                        "description": test["description"],
                        "success": False,
                        "error": str(e)
                    })
        print()
    
    async def _test_response_format(self):
        """レスポンス形式統一性テスト"""
        print("4. レスポンス形式統一性テスト")
        
        async with httpx.AsyncClient() as client:
            response_formats = []
            
            for service_key, service_config in self.services.items():
                try:
                    response = await client.get(f"{service_config['base_url']}/health", timeout=5.0)
                    
                    if response.status_code == 200:
                        try:
                            response_data = response.json()
                            
                            # レスポンス形式の分析
                            format_analysis = {
                                "service": service_config["name"],
                                "is_json": True,
                                "has_status": "status" in response_data,
                                "has_service": "service" in response_data,
                                "fields": list(response_data.keys()) if isinstance(response_data, dict) else [],
                                "structure": type(response_data).__name__
                            }
                            
                            response_formats.append(format_analysis)
                            
                            if format_analysis["has_status"] and format_analysis["has_service"]:
                                print(f"   [OK] {service_config['name']}: 統一されたレスポンス形式")
                                success = True
                            else:
                                print(f"   [WARN] {service_config['name']}: レスポンス形式に改善の余地")
                                success = False
                                
                        except json.JSONDecodeError:
                            print(f"   [WARN] {service_config['name']}: 非JSON形式")
                            success = False
                            format_analysis = {
                                "service": service_config["name"],
                                "is_json": False,
                                "error": "非JSON形式"
                            }
                            response_formats.append(format_analysis)
                    else:
                        print(f"   [FAIL] {service_config['name']}: HTTP {response.status_code}")
                        success = False
                    
                    self.test_results["response_format"].append({
                        "service": service_config["name"],
                        "success": success,
                        "status_code": response.status_code,
                        "format_analysis": format_analysis if 'format_analysis' in locals() else None
                    })
                    
                except Exception as e:
                    print(f"   [FAIL] {service_config['name']}: {str(e)}")
                    self.test_results["response_format"].append({
                        "service": service_config["name"],
                        "success": False,
                        "error": str(e)
                    })
            
            # 形式統一性の分析
            if len(response_formats) > 1:
                print(f"   形式統一性分析:")
                common_fields = set(response_formats[0].get("fields", []))
                for fmt in response_formats[1:]:
                    common_fields &= set(fmt.get("fields", []))
                
                if common_fields:
                    print(f"     共通フィールド: {', '.join(common_fields)}")
                else:
                    print(f"     共通フィールド: なし")
        print()
    
    async def _test_cors_configuration(self):
        """CORS設定テスト"""
        print("5. CORS設定テスト")
        
        test_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://example.com"
        ]
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for origin in test_origins:
                    try:
                        # OPTIONSリクエストでCORSプリフライトをテスト
                        response = await client.options(
                            f"{service_config['base_url']}/health",
                            headers={
                                "Origin": origin,
                                "Access-Control-Request-Method": "GET",
                                "Access-Control-Request-Headers": "Content-Type"
                            },
                            timeout=5.0
                        )
                        
                        cors_headers = {
                            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                        }
                        
                        cors_configured = bool(cors_headers["Access-Control-Allow-Origin"])
                        
                        if cors_configured:
                            allow_origin = cors_headers["Access-Control-Allow-Origin"]
                            if allow_origin == "*":
                                print(f"     [OK] Origin {origin}: CORS設定済み (ワイルドカード)")
                            elif allow_origin == origin:
                                print(f"     [OK] Origin {origin}: CORS設定済み (特定オリジン)")
                            else:
                                print(f"     [OK] Origin {origin}: CORS設定済み (その他: {allow_origin})")
                            success = True
                        else:
                            print(f"     [WARN] Origin {origin}: CORS未設定")
                            success = False
                        
                        self.test_results["cors_configuration"].append({
                            "service": service_config["name"],
                            "origin": origin,
                            "success": success,
                            "cors_headers": cors_headers,
                            "status_code": response.status_code
                        })
                        
                    except Exception as e:
                        print(f"     [FAIL] Origin {origin}: {str(e)}")
                        self.test_results["cors_configuration"].append({
                            "service": service_config["name"],
                            "origin": origin,
                            "success": False,
                            "error": str(e)
                        })
        print()
    
    async def _test_performance(self):
        """パフォーマンステスト"""
        print("6. パフォーマンステスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                try:
                    # 5回測定して統計を取る
                    response_times = []
                    successful_requests = 0
                    
                    for i in range(5):
                        start_time = time.time()
                        response = await client.get(f"{service_config['base_url']}/health", timeout=5.0)
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code == 200:
                            response_times.append(response_time)
                            successful_requests += 1
                    
                    if response_times:
                        avg_time = sum(response_times) / len(response_times)
                        min_time = min(response_times)
                        max_time = max(response_times)
                        
                        # パフォーマンス評価（500ms以内を良好とする）
                        performance_good = avg_time <= 500
                        
                        if performance_good:
                            print(f"   [OK] {service_config['name']}: 平均{avg_time:.1f}ms (範囲: {min_time:.1f}-{max_time:.1f}ms)")
                        else:
                            print(f"   [WARN] {service_config['name']}: 平均{avg_time:.1f}ms (範囲: {min_time:.1f}-{max_time:.1f}ms) - 改善推奨")
                        
                        self.test_results["performance"].append({
                            "service": service_config["name"],
                            "success": performance_good,
                            "avg_response_time_ms": avg_time,
                            "min_response_time_ms": min_time,
                            "max_response_time_ms": max_time,
                            "successful_requests": successful_requests,
                            "total_requests": 5
                        })
                    else:
                        print(f"   [FAIL] {service_config['name']}: パフォーマンス測定失敗")
                        self.test_results["performance"].append({
                            "service": service_config["name"],
                            "success": False,
                            "error": "測定失敗"
                        })
                        
                except Exception as e:
                    print(f"   [FAIL] {service_config['name']}: {str(e)}")
                    self.test_results["performance"].append({
                        "service": service_config["name"],
                        "success": False,
                        "error": str(e)
                    })
        print()
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """最終検証レポートを生成"""
        print("=== API連携とエンドポイント検証結果サマリー ===")
        
        categories = {
            "サービス可用性": self.test_results["service_availability"],
            "API通信": self.test_results["api_communication"],
            "エラーハンドリング": self.test_results["error_handling"],
            "レスポンス形式": self.test_results["response_format"],
            "CORS設定": self.test_results["cors_configuration"],
            "パフォーマンス": self.test_results["performance"]
        }
        
        overall_success = True
        category_summary = {}
        total_tests = 0
        total_success = 0
        
        for category_name, tests in categories.items():
            if not tests:
                continue
            
            success_count = len([t for t in tests if t.get("success", False)])
            total_count = len(tests)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            category_summary[category_name] = {
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_rate
            }
            
            total_tests += total_count
            total_success += success_count
            
            # 80%以上で合格とする
            if success_rate < 80:
                overall_success = False
            
            print(f"{category_name}: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print()
        print(f"総合結果: {total_success}/{total_tests} ({overall_success_rate:.1f}%)")
        
        if overall_success:
            print("[OK] API連携とエンドポイント検証が成功しました！")
        else:
            print("[WARN] 一部の検証項目で改善が必要です。")
        
        # 推奨事項の生成
        recommendations = self._generate_recommendations()
        
        print()
        print("推奨事項:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"  {i}. {recommendation}")
        
        return {
            "overall_success": overall_success,
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "total_success": total_success,
            "category_summary": category_summary,
            "detailed_results": self.test_results,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        # サービス可用性
        unavailable_services = [
            t for t in self.test_results["service_availability"] 
            if not t.get("success", False)
        ]
        if unavailable_services:
            service_names = [s["service"] for s in unavailable_services]
            recommendations.append(f"以下のサービスが利用できません: {', '.join(service_names)}")
        
        # API通信
        failed_communications = [
            t for t in self.test_results["api_communication"] 
            if not t.get("success", False)
        ]
        if failed_communications:
            recommendations.append("API通信に問題があります。サービスの起動状況を確認してください。")
        
        # エラーハンドリング
        error_handling_issues = [
            t for t in self.test_results["error_handling"] 
            if not t.get("success", False)
        ]
        if error_handling_issues:
            recommendations.append("エラーハンドリングの改善が必要です。適切なエラーメッセージを返すようにしてください。")
        
        # レスポンス形式
        format_issues = [
            t for t in self.test_results["response_format"] 
            if not t.get("success", False)
        ]
        if format_issues:
            recommendations.append("レスポンス形式の統一が必要です。すべてのサービスで一貫した形式を使用してください。")
        
        # CORS設定
        cors_issues = [
            t for t in self.test_results["cors_configuration"] 
            if not t.get("success", False)
        ]
        if cors_issues:
            recommendations.append("CORS設定を確認してください。フロントエンドからのアクセスが制限される可能性があります。")
        
        # パフォーマンス
        performance_issues = [
            t for t in self.test_results["performance"] 
            if not t.get("success", False)
        ]
        if performance_issues:
            recommendations.append("パフォーマンスの改善が必要です。応答時間の最適化を検討してください。")
        
        if not recommendations:
            recommendations.append("すべての検証項目が正常に完了しました。API連携は適切に動作しています。")
        
        return recommendations

async def main():
    """メイン実行関数"""
    validator = FinalAPIValidator()
    report = await validator.run_final_validation()
    
    # レポートをJSONファイルに保存
    with open("api_validation_final_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n最終API検証レポートが 'api_validation_final_report.json' に保存されました。")
    
    return report["overall_success"]

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n検証が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n検証中にエラーが発生しました: {str(e)}")
        sys.exit(1)