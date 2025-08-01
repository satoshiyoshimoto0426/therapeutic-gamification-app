"""
エラーハンドリング統一性検証

タスク26.4の一部: エラーハンドリングの適切性を検証
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

class ErrorHandlingValidator:
    """エラーハンドリング統一性検証クラス"""
    
    def __init__(self):
        self.services = {
            "core_game": {
                "name": "Core Game Engine",
                "base_url": "http://localhost:8001"
            },
            "auth": {
                "name": "Auth Service",
                "base_url": "http://localhost:8002"
            },
            "task_mgmt": {
                "name": "Task Management",
                "base_url": "http://localhost:8003"
            }
        }
        
        # エラーシナリオの定義
        self.error_scenarios = [
            # バリデーションエラー (400/422)
            {
                "category": "validation_errors",
                "description": "バリデーションエラー",
                "expected_status": [400, 422],
                "tests": [
                    {
                        "service": "core_game",
                        "endpoint": "/xp/add",
                        "method": "POST",
                        "data": {"uid": "", "xp_amount": 50, "source": "test"},
                        "description": "空のUID"
                    },
                    {
                        "service": "core_game",
                        "endpoint": "/xp/add",
                        "method": "POST",
                        "data": {"uid": "test", "xp_amount": -10, "source": "test"},
                        "description": "負のXP値"
                    },
                    {
                        "service": "core_game",
                        "endpoint": "/level/progress",
                        "method": "POST",
                        "data": {},
                        "description": "必須フィールド不足"
                    },
                    {
                        "service": "auth",
                        "endpoint": "/auth/token",
                        "method": "POST",
                        "data": {"guardian_id": "", "user_id": "test", "permission_level": "invalid"},
                        "description": "無効な権限レベル"
                    },
                    {
                        "service": "auth",
                        "endpoint": "/auth/verify",
                        "method": "POST",
                        "data": {"token": ""},
                        "description": "空のトークン"
                    },
                    {
                        "service": "task_mgmt",
                        "endpoint": "/tasks/test_user/create",
                        "method": "POST",
                        "data": {"task_type": "invalid_type", "title": "", "difficulty": 10},
                        "description": "無効なタスクタイプ"
                    },
                    {
                        "service": "task_mgmt",
                        "endpoint": "/tasks/test_user/create",
                        "method": "POST",
                        "data": {"task_type": "routine", "title": "test", "difficulty": -1},
                        "description": "無効な難易度"
                    }
                ]
            },
            # リソース不存在エラー (404)
            {
                "category": "not_found_errors",
                "description": "リソース不存在エラー",
                "expected_status": [404],
                "tests": [
                    {
                        "service": "task_mgmt",
                        "endpoint": "/tasks/nonexistent_user/list",
                        "method": "GET",
                        "data": {},
                        "description": "存在しないユーザーのタスク一覧"
                    },
                    {
                        "service": "task_mgmt",
                        "endpoint": "/tasks/test_user/nonexistent_task",
                        "method": "GET",
                        "data": {},
                        "description": "存在しないタスク"
                    },
                    {
                        "service": "core_game",
                        "endpoint": "/nonexistent/endpoint",
                        "method": "GET",
                        "data": {},
                        "description": "存在しないエンドポイント"
                    }
                ]
            },
            # メソッド不許可エラー (405)
            {
                "category": "method_not_allowed_errors",
                "description": "メソッド不許可エラー",
                "expected_status": [405],
                "tests": [
                    {
                        "service": "core_game",
                        "endpoint": "/health",
                        "method": "DELETE",
                        "data": {},
                        "description": "ヘルスチェックにDELETE"
                    },
                    {
                        "service": "auth",
                        "endpoint": "/health",
                        "method": "PUT",
                        "data": {},
                        "description": "ヘルスチェックにPUT"
                    },
                    {
                        "service": "task_mgmt",
                        "endpoint": "/health",
                        "method": "PATCH",
                        "data": {},
                        "description": "ヘルスチェックにPATCH"
                    }
                ]
            },
            # 内部サーバーエラー (500)
            {
                "category": "server_errors",
                "description": "内部サーバーエラー",
                "expected_status": [500],
                "tests": [
                    {
                        "service": "core_game",
                        "endpoint": "/xp/add",
                        "method": "POST",
                        "data": {"uid": "test", "xp_amount": "invalid_type", "source": "test"},
                        "description": "型不一致データ"
                    }
                ]
            }
        ]
        
        # 期待されるエラーレスポンス形式
        self.expected_error_fields = [
            "detail",      # FastAPI標準
            "message",     # 一般的
            "error",       # 一般的
            "errors"       # 複数エラー用
        ]
        
        self.expected_metadata_fields = [
            "timestamp",   # エラー発生時刻
            "path",        # エラーが発生したパス
            "method",      # HTTPメソッド
            "status_code", # ステータスコード
            "request_id"   # リクエストID（オプション）
        ]
    
    async def run_error_handling_validation(self) -> Dict[str, Any]:
        """エラーハンドリング検証を実行"""
        print("=== エラーハンドリング統一性検証 ===")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "error_response_tests": [],
            "error_format_consistency": [],
            "error_detail_completeness": [],
            "http_status_accuracy": []
        }
        
        # 1. エラーレスポンステスト
        await self._test_error_responses(results)
        
        # 2. エラー形式統一性テスト
        await self._test_error_format_consistency(results)
        
        # 3. エラー詳細完全性テスト
        await self._test_error_detail_completeness(results)
        
        # 4. HTTPステータス精度テスト
        await self._test_http_status_accuracy(results)
        
        return self._generate_error_handling_report(results)
    
    async def _test_error_responses(self, results: Dict[str, Any]):
        """エラーレスポンステスト"""
        print("1. エラーレスポンステスト")
        
        async with httpx.AsyncClient() as client:
            for scenario in self.error_scenarios:
                print(f"   {scenario['description']}:")
                
                for test in scenario["tests"]:
                    service_config = self.services.get(test["service"])
                    if not service_config:
                        continue
                    
                    try:
                        url = f"{service_config['base_url']}{test['endpoint']}"
                        method = test["method"]
                        data = test["data"]
                        
                        # リクエスト送信
                        if method == "POST":
                            response = await client.post(url, json=data, timeout=10.0)
                        elif method == "PUT":
                            response = await client.put(url, json=data, timeout=10.0)
                        elif method == "DELETE":
                            response = await client.delete(url, timeout=10.0)
                        elif method == "PATCH":
                            response = await client.patch(url, json=data, timeout=10.0)
                        else:  # GET
                            response = await client.get(url, timeout=10.0)
                        
                        # レスポンス解析
                        try:
                            response_data = response.json()
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response.text}
                        
                        # ステータスコード確認
                        expected_statuses = scenario["expected_status"]
                        status_correct = response.status_code in expected_statuses
                        
                        # エラー詳細の存在確認
                        has_error_detail = any(
                            field in response_data for field in self.expected_error_fields
                        )
                        
                        test_result = {
                            "service": service_config["name"],
                            "endpoint": test["endpoint"],
                            "method": method,
                            "description": test["description"],
                            "expected_status": expected_statuses,
                            "actual_status": response.status_code,
                            "status_correct": status_correct,
                            "response_data": response_data,
                            "has_error_detail": has_error_detail,
                            "response_is_json": isinstance(response_data, dict) and "raw_response" not in response_data
                        }
                        
                        if status_correct and has_error_detail:
                            print(f"     ✓ {test['description']}: 適切なエラーハンドリング")
                        elif status_correct:
                            print(f"     ⚠ {test['description']}: ステータス正常、詳細不足")
                        else:
                            print(f"     ✗ {test['description']}: 予期しないステータス ({response.status_code})")
                        
                        results["error_response_tests"].append(test_result)
                        
                    except httpx.ConnectError:
                        test_result = {
                            "service": service_config["name"],
                            "endpoint": test["endpoint"],
                            "method": test["method"],
                            "description": test["description"],
                            "error": "接続失敗",
                            "status_correct": False,
                            "has_error_detail": False
                        }
                        print(f"     ✗ {test['description']}: 接続失敗")
                        results["error_response_tests"].append(test_result)
                        
                    except Exception as e:
                        test_result = {
                            "service": service_config["name"],
                            "endpoint": test["endpoint"],
                            "method": test["method"],
                            "description": test["description"],
                            "error": str(e),
                            "status_correct": False,
                            "has_error_detail": False
                        }
                        print(f"     ✗ {test['description']}: {str(e)}")
                        results["error_response_tests"].append(test_result)
        print()
    
    async def _test_error_format_consistency(self, results: Dict[str, Any]):
        """エラー形式統一性テスト"""
        print("2. エラー形式統一性テスト")
        
        # 各サービスからエラーレスポンスを収集
        error_responses = {}
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                try:
                    # 意図的にバリデーションエラーを発生させる
                    if service_key == "core_game":
                        response = await client.post(
                            f"{service_config['base_url']}/xp/add",
                            json={"uid": "", "xp_amount": 50, "source": "test"},
                            timeout=5.0
                        )
                    elif service_key == "auth":
                        response = await client.post(
                            f"{service_config['base_url']}/auth/token",
                            json={"guardian_id": "", "user_id": "test", "permission_level": "invalid"},
                            timeout=5.0
                        )
                    elif service_key == "task_mgmt":
                        response = await client.post(
                            f"{service_config['base_url']}/tasks/test_user/create",
                            json={"task_type": "invalid", "title": "", "difficulty": 10},
                            timeout=5.0
                        )
                    
                    if response.status_code in [400, 422]:
                        try:
                            error_data = response.json()
                            error_responses[service_key] = {
                                "service": service_config["name"],
                                "status_code": response.status_code,
                                "error_data": error_data,
                                "error_fields": list(error_data.keys()) if isinstance(error_data, dict) else [],
                                "has_standard_fields": any(
                                    field in error_data for field in self.expected_error_fields
                                ) if isinstance(error_data, dict) else False
                            }
                            
                            if error_responses[service_key]["has_standard_fields"]:
                                print(f"     ✓ 標準的なエラー形式")
                            else:
                                print(f"     ⚠ 非標準的なエラー形式")
                                
                        except json.JSONDecodeError:
                            error_responses[service_key] = {
                                "service": service_config["name"],
                                "status_code": response.status_code,
                                "error_data": response.text,
                                "error_fields": [],
                                "has_standard_fields": False
                            }
                            print(f"     ⚠ 非JSON形式のエラーレスポンス")
                    else:
                        print(f"     ⚠ 期待されるエラーステータスではありません ({response.status_code})")
                        
                except Exception as e:
                    print(f"     ✗ エラー形式テスト失敗: {str(e)}")
        
        # 形式の一貫性を分析
        if len(error_responses) > 1:
            consistency_analysis = self._analyze_error_format_consistency(error_responses)
            results["error_format_consistency"].append(consistency_analysis)
        
        print()
    
    async def _test_error_detail_completeness(self, results: Dict[str, Any]):
        """エラー詳細完全性テスト"""
        print("3. エラー詳細完全性テスト")
        
        detail_tests = [
            {
                "service": "core_game",
                "endpoint": "/xp/add",
                "method": "POST",
                "data": {"uid": "", "xp_amount": "invalid", "source": "test"},
                "description": "複数のバリデーションエラー"
            },
            {
                "service": "auth",
                "endpoint": "/auth/token",
                "method": "POST",
                "data": {},
                "description": "全フィールド不足"
            },
            {
                "service": "task_mgmt",
                "endpoint": "/tasks/test_user/create",
                "method": "POST",
                "data": {"task_type": "routine"},
                "description": "部分的フィールド不足"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for test in detail_tests:
                service_config = self.services.get(test["service"])
                if not service_config:
                    continue
                
                try:
                    url = f"{service_config['base_url']}{test['endpoint']}"
                    response = await client.post(url, json=test["data"], timeout=5.0)
                    
                    if response.status_code in [400, 422]:
                        try:
                            error_data = response.json()
                            
                            # エラー詳細の完全性を評価
                            completeness_score = self._evaluate_error_completeness(error_data)
                            
                            test_result = {
                                "service": service_config["name"],
                                "description": test["description"],
                                "error_data": error_data,
                                "completeness_score": completeness_score,
                                "has_field_specific_errors": self._has_field_specific_errors(error_data),
                                "has_helpful_messages": self._has_helpful_messages(error_data)
                            }
                            
                            if completeness_score >= 0.7:
                                print(f"   ✓ {test['description']}: 詳細なエラー情報 ({completeness_score:.1f})")
                            else:
                                print(f"   ⚠ {test['description']}: エラー詳細不足 ({completeness_score:.1f})")
                            
                            results["error_detail_completeness"].append(test_result)
                            
                        except json.JSONDecodeError:
                            print(f"   ✗ {test['description']}: 非JSON形式")
                    else:
                        print(f"   ⚠ {test['description']}: 予期しないステータス ({response.status_code})")
                        
                except Exception as e:
                    print(f"   ✗ {test['description']}: {str(e)}")
        print()
    
    async def _test_http_status_accuracy(self, results: Dict[str, Any]):
        """HTTPステータス精度テスト"""
        print("4. HTTPステータス精度テスト")
        
        status_tests = [
            {
                "expected_status": 400,
                "description": "バリデーションエラー",
                "tests": [
                    {
                        "service": "core_game",
                        "endpoint": "/xp/add",
                        "data": {"uid": "", "xp_amount": 50, "source": "test"}
                    }
                ]
            },
            {
                "expected_status": 404,
                "description": "リソース不存在",
                "tests": [
                    {
                        "service": "task_mgmt",
                        "endpoint": "/tasks/nonexistent_user/list",
                        "data": {}
                    }
                ]
            },
            {
                "expected_status": 405,
                "description": "メソッド不許可",
                "tests": [
                    {
                        "service": "core_game",
                        "endpoint": "/health",
                        "method": "DELETE",
                        "data": {}
                    }
                ]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for status_test in status_tests:
                print(f"   {status_test['description']} (期待: {status_test['expected_status']}):")
                
                for test in status_test["tests"]:
                    service_config = self.services.get(test["service"])
                    if not service_config:
                        continue
                    
                    try:
                        url = f"{service_config['base_url']}{test['endpoint']}"
                        method = test.get("method", "POST")
                        data = test["data"]
                        
                        if method == "POST":
                            response = await client.post(url, json=data, timeout=5.0)
                        elif method == "DELETE":
                            response = await client.delete(url, timeout=5.0)
                        elif method == "GET":
                            response = await client.get(url, timeout=5.0)
                        
                        status_accurate = response.status_code == status_test["expected_status"]
                        
                        test_result = {
                            "service": service_config["name"],
                            "endpoint": test["endpoint"],
                            "method": method,
                            "expected_status": status_test["expected_status"],
                            "actual_status": response.status_code,
                            "status_accurate": status_accurate
                        }
                        
                        if status_accurate:
                            print(f"     ✓ {service_config['name']}: 正確なステータス")
                        else:
                            print(f"     ⚠ {service_config['name']}: ステータス不正確 ({response.status_code})")
                        
                        results["http_status_accuracy"].append(test_result)
                        
                    except Exception as e:
                        print(f"     ✗ {service_config['name']}: {str(e)}")
        print()
    
    def _analyze_error_format_consistency(self, error_responses: Dict[str, Any]) -> Dict[str, Any]:
        """エラー形式の一貫性を分析"""
        services = list(error_responses.keys())
        
        # 共通フィールドの分析
        all_fields = set()
        for response in error_responses.values():
            all_fields.update(response["error_fields"])
        
        common_fields = set(error_responses[services[0]]["error_fields"])
        for service in services[1:]:
            common_fields &= set(error_responses[service]["error_fields"])
        
        # 標準フィールドの使用状況
        standard_field_usage = {}
        for field in self.expected_error_fields:
            usage = [
                service for service, response in error_responses.items()
                if field in response["error_fields"]
            ]
            if usage:
                standard_field_usage[field] = usage
        
        consistency_score = len(common_fields) / len(all_fields) if all_fields else 0
        
        return {
            "services_analyzed": [response["service"] for response in error_responses.values()],
            "all_fields": list(all_fields),
            "common_fields": list(common_fields),
            "standard_field_usage": standard_field_usage,
            "consistency_score": consistency_score,
            "is_consistent": consistency_score >= 0.5
        }
    
    def _evaluate_error_completeness(self, error_data: Dict[str, Any]) -> float:
        """エラー詳細の完全性を評価（0.0-1.0）"""
        score = 0.0
        
        # 基本エラーメッセージの存在 (0.3)
        if any(field in error_data for field in self.expected_error_fields):
            score += 0.3
        
        # フィールド固有エラーの存在 (0.3)
        if self._has_field_specific_errors(error_data):
            score += 0.3
        
        # 有用なメッセージの存在 (0.2)
        if self._has_helpful_messages(error_data):
            score += 0.2
        
        # メタデータの存在 (0.2)
        if any(field in error_data for field in self.expected_metadata_fields):
            score += 0.2
        
        return min(1.0, score)
    
    def _has_field_specific_errors(self, error_data: Dict[str, Any]) -> bool:
        """フィールド固有のエラーがあるかチェック"""
        # FastAPIスタイルのフィールドエラー
        if "detail" in error_data and isinstance(error_data["detail"], list):
            return any("loc" in item for item in error_data["detail"] if isinstance(item, dict))
        
        # その他の形式のフィールドエラー
        field_indicators = ["field", "fields", "validation_errors", "errors"]
        return any(indicator in error_data for indicator in field_indicators)
    
    def _has_helpful_messages(self, error_data: Dict[str, Any]) -> bool:
        """有用なエラーメッセージがあるかチェック"""
        messages = []
        
        if "detail" in error_data:
            if isinstance(error_data["detail"], str):
                messages.append(error_data["detail"])
            elif isinstance(error_data["detail"], list):
                messages.extend([
                    item.get("msg", "") for item in error_data["detail"]
                    if isinstance(item, dict)
                ])
        
        if "message" in error_data:
            messages.append(error_data["message"])
        
        # メッセージが具体的で有用かチェック
        helpful_indicators = ["required", "invalid", "must", "should", "expected"]
        return any(
            any(indicator in msg.lower() for indicator in helpful_indicators)
            for msg in messages if isinstance(msg, str)
        )
    
    def _generate_error_handling_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """エラーハンドリング検証レポートを生成"""
        print("=== エラーハンドリング検証結果サマリー ===")
        
        categories = {
            "エラーレスポンス": results["error_response_tests"],
            "形式統一性": results["error_format_consistency"],
            "詳細完全性": results["error_detail_completeness"],
            "ステータス精度": results["http_status_accuracy"]
        }
        
        overall_success = True
        category_summary = {}
        
        for category_name, tests in categories.items():
            if not tests:
                continue
            
            if category_name == "エラーレスポンス":
                success_count = len([t for t in tests if t.get("status_correct", False) and t.get("has_error_detail", False)])
            elif category_name == "形式統一性":
                success_count = len([t for t in tests if t.get("is_consistent", False)])
            elif category_name == "詳細完全性":
                success_count = len([t for t in tests if t.get("completeness_score", 0) >= 0.7])
            elif category_name == "ステータス精度":
                success_count = len([t for t in tests if t.get("status_accurate", False)])
            else:
                success_count = 0
            
            total_count = len(tests)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            category_summary[category_name] = {
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_rate
            }
            
            if success_rate < 70:
                overall_success = False
            
            print(f"{category_name}: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        print()
        if overall_success:
            print("✓ エラーハンドリングは適切に実装されています")
        else:
            print("⚠ エラーハンドリングに改善が必要な箇所があります")
        
        return {
            "overall_success": overall_success,
            "category_summary": category_summary,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_error_handling_recommendations(results)
        }
    
    def _generate_error_handling_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """エラーハンドリングの改善提案を生成"""
        recommendations = []
        
        # エラーレスポンステストの結果から
        error_response_issues = [
            t for t in results.get("error_response_tests", [])
            if not (t.get("status_correct", False) and t.get("has_error_detail", False))
        ]
        
        if error_response_issues:
            recommendations.append("適切なHTTPステータスコードとエラー詳細を含むレスポンスを返すようにしてください")
        
        # 形式統一性の結果から
        consistency_issues = [
            t for t in results.get("error_format_consistency", [])
            if not t.get("is_consistent", False)
        ]
        
        if consistency_issues:
            recommendations.append("全サービスで統一されたエラーレスポンス形式を使用してください")
        
        # 詳細完全性の結果から
        completeness_issues = [
            t for t in results.get("error_detail_completeness", [])
            if t.get("completeness_score", 0) < 0.7
        ]
        
        if completeness_issues:
            recommendations.append("より詳細で有用なエラーメッセージを提供してください")
        
        # ステータス精度の結果から
        status_issues = [
            t for t in results.get("http_status_accuracy", [])
            if not t.get("status_accurate", False)
        ]
        
        if status_issues:
            recommendations.append("エラーの種類に応じて適切なHTTPステータスコードを使用してください")
        
        if not recommendations:
            recommendations.append("エラーハンドリングは適切に実装されています")
        
        return recommendations

async def main():
    """メイン実行関数"""
    validator = ErrorHandlingValidator()
    report = await validator.run_error_handling_validation()
    
    # レポートをJSONファイルに保存
    with open("error_handling_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nエラーハンドリング検証レポートが 'error_handling_validation_report.json' に保存されました。")
    
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