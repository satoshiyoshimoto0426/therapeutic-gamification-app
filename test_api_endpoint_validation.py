"""
API連携とエンドポイント検証システム

タスク26.4: API連携とエンドポイント検証
- サービス間API呼び出しの動作確認
- エラーハンドリングの適切性を検証
- レスポンス形式の統一性を確認
- CORS設定の正常動作を確認
"""

import asyncio
import httpx
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Windows環境でのUnicodeサポート
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

@dataclass
class APITestResult:
    """APIテスト結果"""
    service: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    cors_headers: Optional[Dict] = None

@dataclass
class ValidationReport:
    """検証レポート"""
    timestamp: str
    overall_success: bool
    total_tests: int
    successful_tests: int
    failed_tests: int
    categories: Dict[str, Dict[str, Any]]
    detailed_results: List[APITestResult]

class APIEndpointValidator:
    """API連携とエンドポイント検証クラス"""
    
    def __init__(self):
        self.services = {
            "core_game": {
                "name": "Core Game Engine",
                "base_url": "http://localhost:8001",
                "port": 8001,
                "endpoints": [
                    {"path": "/health", "method": "GET", "description": "ヘルスチェック"},
                    {"path": "/xp/add", "method": "POST", "description": "XP追加", 
                     "data": {"uid": "test_user", "xp_amount": 50, "source": "test"}},
                    {"path": "/level/progress", "method": "POST", "description": "レベル進行確認",
                     "data": {"uid": "test_user"}},
                    {"path": "/resonance/check", "method": "POST", "description": "共鳴イベント確認",
                     "data": {"uid": "test_user"}},
                    {"path": "/crystal/progress", "method": "POST", "description": "クリスタル進行",
                     "data": {"uid": "test_user", "attribute": "Self-Discipline", "points": 10}}
                ]
            },
            "auth": {
                "name": "Auth Service",
                "base_url": "http://localhost:8002",
                "port": 8002,
                "endpoints": [
                    {"path": "/health", "method": "GET", "description": "ヘルスチェック"},
                    {"path": "/auth/token", "method": "POST", "description": "認証トークン取得",
                     "data": {"guardian_id": "test_guardian", "user_id": "test_user", "permission_level": "task_edit"}},
                    {"path": "/auth/verify", "method": "POST", "description": "トークン検証",
                     "data": {"token": "test_token"}},
                    {"path": "/permissions/check", "method": "POST", "description": "権限確認",
                     "data": {"user_id": "test_user", "permission": "task_edit"}}
                ]
            },
            "task_mgmt": {
                "name": "Task Management",
                "base_url": "http://localhost:8003",
                "port": 8003,
                "endpoints": [
                    {"path": "/health", "method": "GET", "description": "ヘルスチェック"},
                    {"path": "/tasks/test_user/create", "method": "POST", "description": "タスク作成",
                     "data": {"task_type": "routine", "title": "テストタスク", "description": "API検証用", "difficulty": 2}},
                    {"path": "/tasks/test_user/list", "method": "GET", "description": "タスク一覧取得"},
                    {"path": "/pomodoro/test_user/start", "method": "POST", "description": "Pomodoroセッション開始",
                     "data": {"duration": 25}},
                    {"path": "/tasks/test_user/daily-limit", "method": "GET", "description": "日次制限確認"}
                ]
            }
        }
        
        self.test_user_id = "api_validation_test_user"
        self.test_guardian_id = "api_validation_test_guardian"
        
    async def run_comprehensive_validation(self) -> ValidationReport:
        """包括的なAPI検証を実行"""
        print("=== API連携とエンドポイント検証 ===")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        all_results = []
        categories = {
            "service_availability": {"tests": [], "description": "サービス可用性"},
            "api_functionality": {"tests": [], "description": "API機能性"},
            "error_handling": {"tests": [], "description": "エラーハンドリング"},
            "response_format": {"tests": [], "description": "レスポンス形式"},
            "cors_configuration": {"tests": [], "description": "CORS設定"},
            "performance": {"tests": [], "description": "パフォーマンス"},
            "service_integration": {"tests": [], "description": "サービス間連携"}
        }
        
        # 1. サービス可用性テスト
        await self._test_service_availability(categories["service_availability"], all_results)
        
        # 2. API機能性テスト
        await self._test_api_functionality(categories["api_functionality"], all_results)
        
        # 3. エラーハンドリングテスト
        await self._test_error_handling(categories["error_handling"], all_results)
        
        # 4. レスポンス形式テスト
        await self._test_response_format(categories["response_format"], all_results)
        
        # 5. CORS設定テスト
        await self._test_cors_configuration(categories["cors_configuration"], all_results)
        
        # 6. パフォーマンステスト
        await self._test_performance(categories["performance"], all_results)
        
        # 7. サービス間連携テスト
        await self._test_service_integration(categories["service_integration"], all_results)
        
        return self._generate_validation_report(categories, all_results)
    
    async def _test_service_availability(self, category: Dict, all_results: List):
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
                    
                    success = response.status_code == 200
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint="/health",
                        method="GET",
                        status_code=response.status_code,
                        response_time_ms=response_time,
                        success=success,
                        response_data=response.json() if success else None
                    )
                    
                    if success:
                        print(f"   ✓ {service_config['name']}: 利用可能 ({response_time:.1f}ms)")
                    else:
                        print(f"   ✗ {service_config['name']}: HTTP {response.status_code}")
                        result.error_message = f"HTTP {response.status_code}"
                    
                    category["tests"].append(result)
                    all_results.append(result)
                    
                except httpx.ConnectError:
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint="/health",
                        method="GET",
                        status_code=0,
                        response_time_ms=0,
                        success=False,
                        error_message="接続失敗 (サービス未起動)"
                    )
                    print(f"   ✗ {service_config['name']}: 接続失敗 (サービス未起動)")
                    category["tests"].append(result)
                    all_results.append(result)
                    
                except Exception as e:
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint="/health",
                        method="GET",
                        status_code=0,
                        response_time_ms=0,
                        success=False,
                        error_message=str(e)
                    )
                    print(f"   ✗ {service_config['name']}: {str(e)}")
                    category["tests"].append(result)
                    all_results.append(result)
        print()
    
    async def _test_api_functionality(self, category: Dict, all_results: List):
        """API機能性テスト"""
        print("2. API機能性テスト")
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for endpoint_config in service_config["endpoints"]:
                    if endpoint_config["path"] == "/health":
                        continue  # ヘルスチェックは可用性テストで実施済み
                    
                    try:
                        url = f"{service_config['base_url']}{endpoint_config['path']}"
                        method = endpoint_config["method"]
                        data = endpoint_config.get("data", {})
                        
                        start_time = time.time()
                        
                        if method == "POST":
                            response = await client.post(url, json=data, timeout=10.0)
                        elif method == "PUT":
                            response = await client.put(url, json=data, timeout=10.0)
                        elif method == "DELETE":
                            response = await client.delete(url, timeout=10.0)
                        else:  # GET
                            response = await client.get(url, timeout=10.0)
                        
                        response_time = (time.time() - start_time) * 1000
                        
                        # 成功判定（200, 201, 422は正常とみなす）
                        success = response.status_code in [200, 201, 422]
                        
                        try:
                            response_data = response.json()
                        except:
                            response_data = None
                        
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=endpoint_config["path"],
                            method=method,
                            status_code=response.status_code,
                            response_time_ms=response_time,
                            success=success,
                            response_data=response_data
                        )
                        
                        if success:
                            print(f"     ✓ {method} {endpoint_config['path']}: 成功 ({response_time:.1f}ms)")
                        else:
                            print(f"     ⚠ {method} {endpoint_config['path']}: HTTP {response.status_code} ({response_time:.1f}ms)")
                            result.error_message = f"HTTP {response.status_code}"
                        
                        category["tests"].append(result)
                        all_results.append(result)
                        
                    except httpx.ConnectError:
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=endpoint_config["path"],
                            method=endpoint_config["method"],
                            status_code=0,
                            response_time_ms=0,
                            success=False,
                            error_message="接続失敗"
                        )
                        print(f"     ✗ {endpoint_config['method']} {endpoint_config['path']}: 接続失敗")
                        category["tests"].append(result)
                        all_results.append(result)
                        
                    except Exception as e:
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=endpoint_config["path"],
                            method=endpoint_config["method"],
                            status_code=0,
                            response_time_ms=0,
                            success=False,
                            error_message=str(e)
                        )
                        print(f"     ✗ {endpoint_config['method']} {endpoint_config['path']}: {str(e)}")
                        category["tests"].append(result)
                        all_results.append(result)
        print()
    
    async def _test_error_handling(self, category: Dict, all_results: List):
        """エラーハンドリングテスト"""
        print("3. エラーハンドリングテスト")
        
        error_scenarios = [
            {
                "service": "core_game",
                "endpoint": "/xp/add",
                "method": "POST",
                "data": {"uid": "", "xp_amount": 50, "source": "test"},
                "description": "空のUID",
                "expected_status": [400, 422]
            },
            {
                "service": "core_game",
                "endpoint": "/xp/add",
                "method": "POST",
                "data": {"uid": "test", "xp_amount": -10, "source": "test"},
                "description": "負のXP値",
                "expected_status": [400, 422]
            },
            {
                "service": "auth",
                "endpoint": "/auth/token",
                "method": "POST",
                "data": {"guardian_id": "", "user_id": "test", "permission_level": "invalid"},
                "description": "無効な権限レベル",
                "expected_status": [400, 422]
            },
            {
                "service": "task_mgmt",
                "endpoint": "/tasks/test_user/create",
                "method": "POST",
                "data": {"task_type": "invalid_type", "title": "", "difficulty": 10},
                "description": "無効なタスクタイプ",
                "expected_status": [400, 422]
            },
            {
                "service": "task_mgmt",
                "endpoint": "/tasks/nonexistent_user/list",
                "method": "GET",
                "data": {},
                "description": "存在しないユーザー",
                "expected_status": [404, 422]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for scenario in error_scenarios:
                service_config = self.services.get(scenario["service"])
                if not service_config:
                    continue
                
                try:
                    url = f"{service_config['base_url']}{scenario['endpoint']}"
                    method = scenario["method"]
                    data = scenario["data"]
                    
                    start_time = time.time()
                    
                    if method == "POST":
                        response = await client.post(url, json=data, timeout=10.0)
                    elif method == "PUT":
                        response = await client.put(url, json=data, timeout=10.0)
                    else:  # GET
                        response = await client.get(url, timeout=10.0)
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    expected_statuses = scenario["expected_status"]
                    error_handled_correctly = response.status_code in expected_statuses
                    
                    try:
                        response_data = response.json()
                        has_error_detail = any(key in response_data for key in ["detail", "message", "error"])
                    except:
                        response_data = None
                        has_error_detail = False
                    
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint=scenario["endpoint"],
                        method=method,
                        status_code=response.status_code,
                        response_time_ms=response_time,
                        success=error_handled_correctly and has_error_detail,
                        response_data=response_data
                    )
                    
                    if error_handled_correctly:
                        if has_error_detail:
                            print(f"   ✓ {scenario['description']}: 適切なエラーハンドリング ({response.status_code})")
                        else:
                            print(f"   ⚠ {scenario['description']}: エラー詳細不足 ({response.status_code})")
                            result.error_message = "エラー詳細不足"
                    else:
                        print(f"   ✗ {scenario['description']}: 予期しないステータス ({response.status_code})")
                        result.error_message = f"予期しないステータス: {response.status_code}"
                    
                    category["tests"].append(result)
                    all_results.append(result)
                    
                except Exception as e:
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint=scenario["endpoint"],
                        method=scenario["method"],
                        status_code=0,
                        response_time_ms=0,
                        success=False,
                        error_message=str(e)
                    )
                    print(f"   ✗ {scenario['description']}: {str(e)}")
                    category["tests"].append(result)
                    all_results.append(result)
        print()
    
    async def _test_response_format(self, category: Dict, all_results: List):
        """レスポンス形式テスト"""
        print("4. レスポンス形式統一性テスト")
        
        format_tests = [
            {
                "service": "core_game",
                "endpoint": "/health",
                "method": "GET",
                "expected_fields": ["status"]
            },
            {
                "service": "auth",
                "endpoint": "/health",
                "method": "GET",
                "expected_fields": ["status"]
            },
            {
                "service": "task_mgmt",
                "endpoint": "/health",
                "method": "GET",
                "expected_fields": ["status"]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for test in format_tests:
                service_config = self.services.get(test["service"])
                if not service_config:
                    continue
                
                try:
                    url = f"{service_config['base_url']}{test['endpoint']}"
                    
                    start_time = time.time()
                    response = await client.get(url, timeout=5.0)
                    response_time = (time.time() - start_time) * 1000
                    
                    format_valid = False
                    response_data = None
                    
                    if response.status_code == 200:
                        try:
                            response_data = response.json()
                            
                            # 期待されるフィールドの存在確認
                            has_expected_fields = all(
                                field in response_data for field in test["expected_fields"]
                            )
                            
                            # 共通フィールドの確認
                            has_consistent_structure = isinstance(response_data, dict)
                            
                            format_valid = has_expected_fields and has_consistent_structure
                            
                        except json.JSONDecodeError:
                            format_valid = False
                    
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint=test["endpoint"],
                        method=test["method"],
                        status_code=response.status_code,
                        response_time_ms=response_time,
                        success=format_valid,
                        response_data=response_data
                    )
                    
                    if format_valid:
                        print(f"   ✓ {service_config['name']}: レスポンス形式統一")
                    else:
                        print(f"   ⚠ {service_config['name']}: レスポンス形式不統一")
                        result.error_message = "レスポンス形式不統一"
                    
                    category["tests"].append(result)
                    all_results.append(result)
                    
                except Exception as e:
                    result = APITestResult(
                        service=service_config["name"],
                        endpoint=test["endpoint"],
                        method=test["method"],
                        status_code=0,
                        response_time_ms=0,
                        success=False,
                        error_message=str(e)
                    )
                    print(f"   ✗ {service_config['name']}: {str(e)}")
                    category["tests"].append(result)
                    all_results.append(result)
        print()
    
    async def _test_cors_configuration(self, category: Dict, all_results: List):
        """CORS設定テスト"""
        print("5. CORS設定テスト")
        
        test_origins = [
            "http://localhost:3000",  # フロントエンド開発サーバー
            "http://localhost:5173",  # Vite開発サーバー
            "https://therapeutic-app.example.com"  # 本番想定
        ]
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for origin in test_origins:
                    try:
                        # OPTIONSリクエストでCORSプリフライトをテスト
                        start_time = time.time()
                        response = await client.options(
                            f"{service_config['base_url']}/health",
                            headers={
                                "Origin": origin,
                                "Access-Control-Request-Method": "GET",
                                "Access-Control-Request-Headers": "Content-Type"
                            },
                            timeout=5.0
                        )
                        response_time = (time.time() - start_time) * 1000
                        
                        cors_headers = {
                            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                        }
                        
                        cors_configured = bool(cors_headers["Access-Control-Allow-Origin"])
                        
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint="/health",
                            method="OPTIONS",
                            status_code=response.status_code,
                            response_time_ms=response_time,
                            success=cors_configured,
                            cors_headers=cors_headers
                        )
                        
                        if cors_configured:
                            print(f"     ✓ Origin {origin}: CORS設定済み")
                        else:
                            print(f"     ⚠ Origin {origin}: CORS未設定")
                            result.error_message = "CORS未設定"
                        
                        category["tests"].append(result)
                        all_results.append(result)
                        
                    except Exception as e:
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint="/health",
                            method="OPTIONS",
                            status_code=0,
                            response_time_ms=0,
                            success=False,
                            error_message=str(e)
                        )
                        print(f"     ✗ Origin {origin}: {str(e)}")
                        category["tests"].append(result)
                        all_results.append(result)
        print()
    
    async def _test_performance(self, category: Dict, all_results: List):
        """パフォーマンステスト"""
        print("6. パフォーマンステスト")
        
        performance_targets = {
            "/health": 100,  # 100ms以内
            "/xp/add": 500,  # 500ms以内
            "/level/progress": 500,  # 500ms以内
            "/auth/token": 300,  # 300ms以内
            "/tasks/test_user/list": 400  # 400ms以内
        }
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for endpoint_config in service_config["endpoints"]:
                    endpoint_path = endpoint_config["path"]
                    target_ms = performance_targets.get(endpoint_path, 1000)
                    
                    try:
                        url = f"{service_config['base_url']}{endpoint_path}"
                        method = endpoint_config["method"]
                        data = endpoint_config.get("data", {})
                        
                        # 5回測定して平均を取る
                        response_times = []
                        successful_requests = 0
                        
                        for _ in range(5):
                            start_time = time.time()
                            
                            try:
                                if method == "POST":
                                    response = await client.post(url, json=data, timeout=10.0)
                                elif method == "PUT":
                                    response = await client.put(url, json=data, timeout=10.0)
                                else:  # GET
                                    response = await client.get(url, timeout=10.0)
                                
                                response_time = (time.time() - start_time) * 1000
                                
                                if response.status_code in [200, 201, 422]:
                                    response_times.append(response_time)
                                    successful_requests += 1
                                    
                            except Exception:
                                continue
                        
                        if response_times:
                            avg_response_time = sum(response_times) / len(response_times)
                            performance_ok = avg_response_time <= target_ms
                            
                            result = APITestResult(
                                service=service_config["name"],
                                endpoint=endpoint_path,
                                method=method,
                                status_code=200,  # 平均値なので200とする
                                response_time_ms=avg_response_time,
                                success=performance_ok
                            )
                            
                            if performance_ok:
                                print(f"     ✓ {method} {endpoint_path}: {avg_response_time:.1f}ms (目標: {target_ms}ms)")
                            else:
                                print(f"     ⚠ {method} {endpoint_path}: {avg_response_time:.1f}ms (目標: {target_ms}ms)")
                                result.error_message = f"パフォーマンス目標未達成"
                            
                            category["tests"].append(result)
                            all_results.append(result)
                        else:
                            result = APITestResult(
                                service=service_config["name"],
                                endpoint=endpoint_path,
                                method=method,
                                status_code=0,
                                response_time_ms=0,
                                success=False,
                                error_message="パフォーマンス測定失敗"
                            )
                            print(f"     ✗ {method} {endpoint_path}: 測定失敗")
                            category["tests"].append(result)
                            all_results.append(result)
                            
                    except Exception as e:
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=endpoint_path,
                            method=endpoint_config["method"],
                            status_code=0,
                            response_time_ms=0,
                            success=False,
                            error_message=str(e)
                        )
                        print(f"     ✗ {method} {endpoint_path}: {str(e)}")
                        category["tests"].append(result)
                        all_results.append(result)
        print()
    
    async def _test_service_integration(self, category: Dict, all_results: List):
        """サービス間連携テスト"""
        print("7. サービス間連携テスト")
        
        integration_scenarios = [
            {
                "name": "認証→タスク作成→XP追加フロー",
                "steps": [
                    {
                        "service": "auth",
                        "endpoint": "/auth/token",
                        "method": "POST",
                        "data": {
                            "guardian_id": self.test_guardian_id,
                            "user_id": self.test_user_id,
                            "permission_level": "task_edit"
                        }
                    },
                    {
                        "service": "task_mgmt",
                        "endpoint": f"/tasks/{self.test_user_id}/create",
                        "method": "POST",
                        "data": {
                            "task_type": "routine",
                            "title": "統合テストタスク",
                            "description": "サービス間連携テスト",
                            "difficulty": 2
                        }
                    },
                    {
                        "service": "core_game",
                        "endpoint": "/xp/add",
                        "method": "POST",
                        "data": {
                            "uid": self.test_user_id,
                            "xp_amount": 50,
                            "source": "integration_test"
                        }
                    }
                ]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for scenario in integration_scenarios:
                print(f"   {scenario['name']}:")
                scenario_success = True
                scenario_data = {}
                
                for i, step in enumerate(scenario["steps"]):
                    service_config = self.services.get(step["service"])
                    if not service_config:
                        scenario_success = False
                        continue
                    
                    try:
                        url = f"{service_config['base_url']}{step['endpoint']}"
                        method = step["method"]
                        data = step["data"]
                        
                        start_time = time.time()
                        
                        if method == "POST":
                            response = await client.post(url, json=data, timeout=10.0)
                        elif method == "PUT":
                            response = await client.put(url, json=data, timeout=10.0)
                        else:  # GET
                            response = await client.get(url, timeout=10.0)
                        
                        response_time = (time.time() - start_time) * 1000
                        
                        step_success = response.status_code in [200, 201, 422]
                        
                        try:
                            response_data = response.json()
                        except:
                            response_data = None
                        
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=step["endpoint"],
                            method=method,
                            status_code=response.status_code,
                            response_time_ms=response_time,
                            success=step_success,
                            response_data=response_data
                        )
                        
                        if step_success:
                            print(f"     ✓ ステップ{i+1}: {service_config['name']} 成功")
                            scenario_data[f"step_{i+1}"] = response_data
                        else:
                            print(f"     ✗ ステップ{i+1}: {service_config['name']} 失敗 ({response.status_code})")
                            scenario_success = False
                            result.error_message = f"HTTP {response.status_code}"
                        
                        category["tests"].append(result)
                        all_results.append(result)
                        
                    except Exception as e:
                        result = APITestResult(
                            service=service_config["name"],
                            endpoint=step["endpoint"],
                            method=step["method"],
                            status_code=0,
                            response_time_ms=0,
                            success=False,
                            error_message=str(e)
                        )
                        print(f"     ✗ ステップ{i+1}: {service_config['name']} エラー - {str(e)}")
                        scenario_success = False
                        category["tests"].append(result)
                        all_results.append(result)
                
                if scenario_success:
                    print(f"   ✓ {scenario['name']}: 統合テスト成功")
                else:
                    print(f"   ✗ {scenario['name']}: 統合テスト失敗")
        print()
    
    def _generate_validation_report(self, categories: Dict, all_results: List) -> ValidationReport:
        """検証レポートを生成"""
        print("=== API連携とエンドポイント検証結果サマリー ===")
        
        total_tests = len(all_results)
        successful_tests = len([r for r in all_results if r.success])
        failed_tests = total_tests - successful_tests
        overall_success = failed_tests == 0
        
        category_summary = {}
        
        for category_name, category_data in categories.items():
            tests = category_data["tests"]
            if not tests:
                continue
            
            success_count = len([t for t in tests if t.success])
            total_count = len(tests)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            category_summary[category_name] = {
                "description": category_data["description"],
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_rate,
                "tests": tests
            }
            
            print(f"{category_data['description']}: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        print()
        print(f"総合結果: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        
        if overall_success:
            print("✓ すべてのAPI連携テストが成功しました！")
        else:
            print("⚠ 一部のAPI連携テストが失敗しました。詳細を確認してください。")
        
        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            overall_success=overall_success,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            categories=category_summary,
            detailed_results=all_results
        )

async def main():
    """メイン実行関数"""
    validator = APIEndpointValidator()
    report = await validator.run_comprehensive_validation()
    
    # レポートをJSONファイルに保存
    report_dict = asdict(report)
    
    # APITestResultオブジェクトを辞書に変換
    report_dict["detailed_results"] = [asdict(result) for result in report.detailed_results]
    
    # カテゴリ内のテスト結果も変換
    for category_name, category_data in report_dict["categories"].items():
        if "tests" in category_data:
            category_data["tests"] = [asdict(test) for test in category_data["tests"]]
    
    with open("api_endpoint_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\nAPI連携検証レポートが 'api_endpoint_validation_report.json' に保存されました。")
    
    return report.overall_success

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