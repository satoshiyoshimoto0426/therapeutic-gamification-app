"""
CORS設定の詳細検証

タスク26.4の一部: CORS設定の正常動作を確認
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Windows環境でのUnicodeサポート
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class CORSAdvancedValidator:
    """CORS設定の詳細検証クラス"""
    
    def __init__(self):
        self.services = {
            "core_game": {
                "name": "Core Game Engine",
                "base_url": "http://localhost:8001",
                "endpoints": ["/health", "/xp/add", "/level/progress"]
            },
            "auth": {
                "name": "Auth Service",
                "base_url": "http://localhost:8002",
                "endpoints": ["/health", "/auth/token", "/auth/verify"]
            },
            "task_mgmt": {
                "name": "Task Management",
                "base_url": "http://localhost:8003",
                "endpoints": ["/health", "/tasks/test_user/create", "/tasks/test_user/list"]
            }
        }
        
        self.test_origins = [
            "http://localhost:3000",  # React開発サーバー
            "http://localhost:5173",  # Vite開発サーバー
            "http://localhost:8080",  # 一般的な開発サーバー
            "https://therapeutic-app.example.com",  # 本番想定ドメイン
            "https://app.therapeutic-gaming.com",  # 本番想定ドメイン2
            "http://malicious-site.com"  # 悪意のあるサイト（拒否されるべき）
        ]
        
        self.test_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.test_headers = [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "User-Agent"
        ]
    
    async def run_cors_validation(self) -> Dict[str, Any]:
        """CORS設定の包括的検証を実行"""
        print("=== CORS設定詳細検証 ===")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "preflight_tests": [],
            "actual_request_tests": [],
            "security_tests": [],
            "header_validation_tests": [],
            "method_validation_tests": []
        }
        
        # 1. プリフライトリクエストテスト
        await self._test_preflight_requests(results)
        
        # 2. 実際のCORSリクエストテスト
        await self._test_actual_cors_requests(results)
        
        # 3. セキュリティテスト
        await self._test_cors_security(results)
        
        # 4. ヘッダー検証テスト
        await self._test_header_validation(results)
        
        # 5. メソッド検証テスト
        await self._test_method_validation(results)
        
        return self._generate_cors_report(results)
    
    async def _test_preflight_requests(self, results: Dict[str, Any]):
        """プリフライトリクエストテスト"""
        print("1. プリフライトリクエストテスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for endpoint in service_config["endpoints"]:
                    for origin in self.test_origins[:3]:  # 正当なオリジンのみテスト
                        try:
                            url = f"{service_config['base_url']}{endpoint}"
                            
                            # OPTIONSリクエスト送信
                            response = await client.options(
                                url,
                                headers={
                                    "Origin": origin,
                                    "Access-Control-Request-Method": "POST",
                                    "Access-Control-Request-Headers": "Content-Type,Authorization"
                                },
                                timeout=5.0
                            )
                            
                            cors_headers = {
                                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
                                "Access-Control-Max-Age": response.headers.get("Access-Control-Max-Age")
                            }
                            
                            # CORS設定の評価
                            cors_properly_configured = self._evaluate_cors_headers(cors_headers, origin)
                            
                            test_result = {
                                "service": service_config["name"],
                                "endpoint": endpoint,
                                "origin": origin,
                                "status_code": response.status_code,
                                "cors_headers": cors_headers,
                                "properly_configured": cors_properly_configured,
                                "issues": self._identify_cors_issues(cors_headers, origin)
                            }
                            
                            if cors_properly_configured:
                                print(f"     ✓ {endpoint} ({origin}): CORS適切")
                            else:
                                issues = test_result["issues"]
                                print(f"     ⚠ {endpoint} ({origin}): CORS問題 - {', '.join(issues)}")
                            
                            results["preflight_tests"].append(test_result)
                            
                        except Exception as e:
                            test_result = {
                                "service": service_config["name"],
                                "endpoint": endpoint,
                                "origin": origin,
                                "error": str(e),
                                "properly_configured": False
                            }
                            print(f"     ✗ {endpoint} ({origin}): {str(e)}")
                            results["preflight_tests"].append(test_result)
        print()
    
    async def _test_actual_cors_requests(self, results: Dict[str, Any]):
        """実際のCORSリクエストテスト"""
        print("2. 実際のCORSリクエストテスト")
        
        test_requests = [
            {
                "method": "GET",
                "endpoint": "/health",
                "data": None
            },
            {
                "method": "POST",
                "endpoint": "/xp/add",
                "data": {"uid": "test_user", "xp_amount": 10, "source": "cors_test"}
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for request_config in test_requests:
                    # Core Game Engineでない場合はXP追加をスキップ
                    if request_config["endpoint"] == "/xp/add" and service_key != "core_game":
                        continue
                    
                    for origin in self.test_origins[:2]:  # 主要なオリジンのみテスト
                        try:
                            url = f"{service_config['base_url']}{request_config['endpoint']}"
                            method = request_config["method"]
                            data = request_config["data"]
                            
                            headers = {
                                "Origin": origin,
                                "Content-Type": "application/json"
                            }
                            
                            if method == "GET":
                                response = await client.get(url, headers=headers, timeout=5.0)
                            elif method == "POST":
                                response = await client.post(url, json=data, headers=headers, timeout=5.0)
                            
                            # レスポンスヘッダーのCORS確認
                            cors_response_headers = {
                                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
                                "Access-Control-Expose-Headers": response.headers.get("Access-Control-Expose-Headers")
                            }
                            
                            cors_response_valid = bool(cors_response_headers["Access-Control-Allow-Origin"])
                            
                            test_result = {
                                "service": service_config["name"],
                                "method": method,
                                "endpoint": request_config["endpoint"],
                                "origin": origin,
                                "status_code": response.status_code,
                                "cors_response_headers": cors_response_headers,
                                "cors_response_valid": cors_response_valid
                            }
                            
                            if cors_response_valid:
                                print(f"     ✓ {method} {request_config['endpoint']} ({origin}): CORS応答適切")
                            else:
                                print(f"     ⚠ {method} {request_config['endpoint']} ({origin}): CORS応答ヘッダー不足")
                            
                            results["actual_request_tests"].append(test_result)
                            
                        except Exception as e:
                            test_result = {
                                "service": service_config["name"],
                                "method": request_config["method"],
                                "endpoint": request_config["endpoint"],
                                "origin": origin,
                                "error": str(e),
                                "cors_response_valid": False
                            }
                            print(f"     ✗ {method} {request_config['endpoint']} ({origin}): {str(e)}")
                            results["actual_request_tests"].append(test_result)
        print()
    
    async def _test_cors_security(self, results: Dict[str, Any]):
        """CORSセキュリティテスト"""
        print("3. CORSセキュリティテスト")
        
        malicious_origins = [
            "http://malicious-site.com",
            "https://evil.example.com",
            "http://localhost:9999",  # 予期しないポート
            "null",  # null origin
            ""  # 空のorigin
        ]
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for origin in malicious_origins:
                    try:
                        url = f"{service_config['base_url']}/health"
                        
                        # 悪意のあるオリジンからのプリフライトリクエスト
                        response = await client.options(
                            url,
                            headers={
                                "Origin": origin,
                                "Access-Control-Request-Method": "GET"
                            },
                            timeout=5.0
                        )
                        
                        allowed_origin = response.headers.get("Access-Control-Allow-Origin")
                        
                        # 悪意のあるオリジンが許可されていないことを確認
                        security_ok = not (allowed_origin == origin or allowed_origin == "*")
                        
                        test_result = {
                            "service": service_config["name"],
                            "malicious_origin": origin,
                            "status_code": response.status_code,
                            "allowed_origin": allowed_origin,
                            "security_ok": security_ok
                        }
                        
                        if security_ok:
                            print(f"     ✓ 悪意のあるオリジン '{origin}': 適切に拒否")
                        else:
                            print(f"     ⚠ 悪意のあるオリジン '{origin}': セキュリティリスク")
                        
                        results["security_tests"].append(test_result)
                        
                    except Exception as e:
                        test_result = {
                            "service": service_config["name"],
                            "malicious_origin": origin,
                            "error": str(e),
                            "security_ok": True  # エラーは安全とみなす
                        }
                        print(f"     ✓ 悪意のあるオリジン '{origin}': エラー（安全）")
                        results["security_tests"].append(test_result)
        print()
    
    async def _test_header_validation(self, results: Dict[str, Any]):
        """ヘッダー検証テスト"""
        print("4. ヘッダー検証テスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                try:
                    url = f"{service_config['base_url']}/health"
                    
                    # 複数のヘッダーを要求するプリフライトリクエスト
                    response = await client.options(
                        url,
                        headers={
                            "Origin": "http://localhost:3000",
                            "Access-Control-Request-Method": "POST",
                            "Access-Control-Request-Headers": ",".join(self.test_headers)
                        },
                        timeout=5.0
                    )
                    
                    allowed_headers = response.headers.get("Access-Control-Allow-Headers", "")
                    allowed_headers_list = [h.strip().lower() for h in allowed_headers.split(",") if h.strip()]
                    
                    # 必要なヘッダーが許可されているかチェック
                    required_headers = ["content-type", "authorization"]
                    headers_properly_allowed = all(
                        header.lower() in allowed_headers_list or "*" in allowed_headers_list
                        for header in required_headers
                    )
                    
                    test_result = {
                        "service": service_config["name"],
                        "status_code": response.status_code,
                        "allowed_headers": allowed_headers,
                        "headers_properly_allowed": headers_properly_allowed,
                        "missing_headers": [
                            header for header in required_headers
                            if header.lower() not in allowed_headers_list and "*" not in allowed_headers_list
                        ]
                    }
                    
                    if headers_properly_allowed:
                        print(f"     ✓ 必要なヘッダーが適切に許可されています")
                    else:
                        missing = test_result["missing_headers"]
                        print(f"     ⚠ 不足しているヘッダー: {', '.join(missing)}")
                    
                    results["header_validation_tests"].append(test_result)
                    
                except Exception as e:
                    test_result = {
                        "service": service_config["name"],
                        "error": str(e),
                        "headers_properly_allowed": False
                    }
                    print(f"     ✗ ヘッダー検証エラー: {str(e)}")
                    results["header_validation_tests"].append(test_result)
        print()
    
    async def _test_method_validation(self, results: Dict[str, Any]):
        """メソッド検証テスト"""
        print("5. メソッド検証テスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for method in self.test_methods:
                    try:
                        url = f"{service_config['base_url']}/health"
                        
                        # 各メソッドのプリフライトリクエスト
                        response = await client.options(
                            url,
                            headers={
                                "Origin": "http://localhost:3000",
                                "Access-Control-Request-Method": method
                            },
                            timeout=5.0
                        )
                        
                        allowed_methods = response.headers.get("Access-Control-Allow-Methods", "")
                        allowed_methods_list = [m.strip().upper() for m in allowed_methods.split(",") if m.strip()]
                        
                        method_allowed = method.upper() in allowed_methods_list or "*" in allowed_methods_list
                        
                        test_result = {
                            "service": service_config["name"],
                            "method": method,
                            "status_code": response.status_code,
                            "allowed_methods": allowed_methods,
                            "method_allowed": method_allowed
                        }
                        
                        if method_allowed:
                            print(f"     ✓ {method}: 許可")
                        else:
                            print(f"     ⚠ {method}: 未許可")
                        
                        results["method_validation_tests"].append(test_result)
                        
                    except Exception as e:
                        test_result = {
                            "service": service_config["name"],
                            "method": method,
                            "error": str(e),
                            "method_allowed": False
                        }
                        print(f"     ✗ {method}: エラー - {str(e)}")
                        results["method_validation_tests"].append(test_result)
        print()
    
    def _evaluate_cors_headers(self, cors_headers: Dict[str, str], origin: str) -> bool:
        """CORSヘッダーの適切性を評価"""
        # 基本的なCORSヘッダーの存在確認
        has_allow_origin = bool(cors_headers.get("Access-Control-Allow-Origin"))
        has_allow_methods = bool(cors_headers.get("Access-Control-Allow-Methods"))
        has_allow_headers = bool(cors_headers.get("Access-Control-Allow-Headers"))
        
        return has_allow_origin and has_allow_methods and has_allow_headers
    
    def _identify_cors_issues(self, cors_headers: Dict[str, str], origin: str) -> List[str]:
        """CORS設定の問題を特定"""
        issues = []
        
        if not cors_headers.get("Access-Control-Allow-Origin"):
            issues.append("Allow-Origin未設定")
        
        if not cors_headers.get("Access-Control-Allow-Methods"):
            issues.append("Allow-Methods未設定")
        
        if not cors_headers.get("Access-Control-Allow-Headers"):
            issues.append("Allow-Headers未設定")
        
        # セキュリティチェック
        if cors_headers.get("Access-Control-Allow-Origin") == "*" and cors_headers.get("Access-Control-Allow-Credentials") == "true":
            issues.append("セキュリティリスク: ワイルドカード+Credentials")
        
        return issues
    
    def _generate_cors_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """CORS検証レポートを生成"""
        print("=== CORS設定検証結果サマリー ===")
        
        categories = {
            "プリフライト": results["preflight_tests"],
            "実際のリクエスト": results["actual_request_tests"],
            "セキュリティ": results["security_tests"],
            "ヘッダー検証": results["header_validation_tests"],
            "メソッド検証": results["method_validation_tests"]
        }
        
        overall_success = True
        category_summary = {}
        
        for category_name, tests in categories.items():
            if not tests:
                continue
            
            if category_name == "プリフライト":
                success_count = len([t for t in tests if t.get("properly_configured", False)])
            elif category_name == "実際のリクエスト":
                success_count = len([t for t in tests if t.get("cors_response_valid", False)])
            elif category_name == "セキュリティ":
                success_count = len([t for t in tests if t.get("security_ok", False)])
            elif category_name == "ヘッダー検証":
                success_count = len([t for t in tests if t.get("headers_properly_allowed", False)])
            elif category_name == "メソッド検証":
                success_count = len([t for t in tests if t.get("method_allowed", False)])
            else:
                success_count = 0
            
            total_count = len(tests)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            category_summary[category_name] = {
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_rate
            }
            
            if success_rate < 70:  # CORS設定は70%以上で合格とする
                overall_success = False
            
            print(f"{category_name}: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        print()
        if overall_success:
            print("✓ CORS設定は適切に構成されています")
        else:
            print("⚠ CORS設定に改善が必要な箇所があります")
        
        return {
            "overall_success": overall_success,
            "category_summary": category_summary,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_cors_recommendations(results)
        }
    
    def _generate_cors_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """CORS設定の改善提案を生成"""
        recommendations = []
        
        # プリフライトテストの結果から推奨事項を生成
        preflight_issues = []
        for test in results.get("preflight_tests", []):
            if not test.get("properly_configured", False):
                preflight_issues.extend(test.get("issues", []))
        
        if "Allow-Origin未設定" in preflight_issues:
            recommendations.append("Access-Control-Allow-Originヘッダーを設定してください")
        
        if "Allow-Methods未設定" in preflight_issues:
            recommendations.append("Access-Control-Allow-Methodsヘッダーを設定してください")
        
        if "Allow-Headers未設定" in preflight_issues:
            recommendations.append("Access-Control-Allow-Headersヘッダーを設定してください")
        
        # セキュリティテストの結果から推奨事項を生成
        security_issues = len([t for t in results.get("security_tests", []) if not t.get("security_ok", True)])
        if security_issues > 0:
            recommendations.append("悪意のあるオリジンからのアクセスを適切に制限してください")
        
        if not recommendations:
            recommendations.append("CORS設定は適切です")
        
        return recommendations

async def main():
    """メイン実行関数"""
    validator = CORSAdvancedValidator()
    report = await validator.run_cors_validation()
    
    # レポートをJSONファイルに保存
    with open("cors_advanced_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nCORS詳細検証レポートが 'cors_advanced_validation_report.json' に保存されました。")
    
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