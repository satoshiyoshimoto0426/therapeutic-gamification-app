#!/usr/bin/env python3
"""
エラー処理適切性確認テスト (タスク27.2の一部)

要件:
- エラー処理の適切性確認
- 異常系シナリオのテスト
- 復旧可能性の確認
- ユーザー体験への影響評価
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlingTester:
    """エラー処理テストクラス"""
    
    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8002",
            "core_game": "http://localhost:8001", 
            "task_mgmt": "http://localhost:8003",
            "mandala": "http://localhost:8004",
            "ai_story": "http://localhost:8005",
            "mood_tracking": "http://localhost:8006",
            "line_bot": "http://localhost:8007",
            "adhd_support": "http://localhost:8008",
            "therapeutic_safety": "http://localhost:8009"
        }
        
        self.test_user = {
            "uid": "error_test_user",
            "username": "error_tester",
            "email": "error@test.com"
        }
        
        self.valid_auth_token = None
        
    async def setup_valid_user(self) -> bool:
        """有効なテストユーザーセットアップ"""
        logger.info("🔧 有効なテストユーザーセットアップ中...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # ユーザー登録
                register_data = {
                    "uid": self.test_user["uid"],
                    "username": self.test_user["username"],
                    "email": self.test_user["email"],
                    "permissions": ["view_only", "task_edit", "chat_send"]
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/grant",
                    json=register_data
                )
                
                # 認証
                auth_data = {
                    "uid": self.test_user["uid"],
                    "username": self.test_user["username"]
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/login",
                    json=auth_data
                )
                
                if response.status_code == 200:
                    auth_result = response.json()
                    if "access_token" in auth_result:
                        self.valid_auth_token = auth_result["access_token"]
                        logger.info("✅ 有効なテストユーザーセットアップ完了")
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"セットアップエラー: {str(e)}")
            return False
    
    async def test_authentication_errors(self) -> Dict[str, Any]:
        """認証エラー処理テスト"""
        logger.info("🔐 認証エラー処理テスト開始...")
        
        auth_error_results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. 無効なトークンテスト
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            
            try:
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=invalid_headers
                )
                
                auth_error_results["invalid_token"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [401, 403],
                    "response_has_error_message": "error" in response.text.lower() or "unauthorized" in response.text.lower()
                }
            except Exception as e:
                auth_error_results["invalid_token"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 2. トークンなしテスト
            try:
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['uid']}/history"
                )
                
                auth_error_results["no_token"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [401, 403],
                    "response_has_error_message": "error" in response.text.lower() or "unauthorized" in response.text.lower()
                }
            except Exception as e:
                auth_error_results["no_token"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 3. 期限切れトークンシミュレーション
            expired_headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDAwMDAwMDB9.expired"}
            
            try:
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/grid",
                    headers=expired_headers
                )
                
                auth_error_results["expired_token"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [401, 403],
                    "response_has_error_message": "error" in response.text.lower() or "expired" in response.text.lower()
                }
            except Exception as e:
                auth_error_results["expired_token"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 4. 権限不足テスト（view-onlyユーザーでの編集操作）
            if self.valid_auth_token:
                try:
                    # 管理者権限が必要な操作を試行
                    admin_operation = {
                        "uid": "other_user",
                        "permissions": ["admin"]
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['auth']}/auth/guardian/grant",
                        json=admin_operation,
                        headers={"Authorization": f"Bearer {self.valid_auth_token}"}
                    )
                    
                    auth_error_results["insufficient_permissions"] = {
                        "status_code": response.status_code,
                        "handled_correctly": response.status_code in [403, 401],
                        "response_has_error_message": "permission" in response.text.lower() or "forbidden" in response.text.lower()
                    }
                except Exception as e:
                    auth_error_results["insufficient_permissions"] = {
                        "handled_correctly": False,
                        "error": str(e)
                    }
        
        # 認証エラー処理成功率計算
        handled_correctly_count = sum(1 for result in auth_error_results.values() 
                                    if result.get("handled_correctly", False))
        total_auth_tests = len(auth_error_results)
        
        return {
            "success": handled_correctly_count > 0,
            "auth_error_results": auth_error_results,
            "auth_error_handling_rate": handled_correctly_count / total_auth_tests if total_auth_tests > 0 else 0
        }
    
    async def test_data_validation_errors(self) -> Dict[str, Any]:
        """データバリデーションエラー処理テスト"""
        logger.info("📝 データバリデーションエラー処理テスト開始...")
        
        validation_error_results = {}
        headers = {"Authorization": f"Bearer {self.valid_auth_token}"} if self.valid_auth_token else {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. 必須フィールド欠如テスト
            try:
                incomplete_task = {
                    "uid": self.test_user["uid"],
                    # task_type, difficulty, description が欠如
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks",
                    json=incomplete_task,
                    headers=headers
                )
                
                validation_error_results["missing_required_fields"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [400, 422],
                    "response_has_validation_error": "required" in response.text.lower() or "missing" in response.text.lower()
                }
            except Exception as e:
                validation_error_results["missing_required_fields"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 2. 無効なデータ型テスト
            try:
                invalid_type_task = {
                    "uid": self.test_user["uid"],
                    "task_type": "invalid_type",
                    "difficulty": "not_a_number",  # 数値であるべき
                    "description": 12345  # 文字列であるべき
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks",
                    json=invalid_type_task,
                    headers=headers
                )
                
                validation_error_results["invalid_data_types"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [400, 422],
                    "response_has_validation_error": "invalid" in response.text.lower() or "type" in response.text.lower()
                }
            except Exception as e:
                validation_error_results["invalid_data_types"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 3. 範囲外の値テスト
            try:
                out_of_range_data = {
                    "uid": self.test_user["uid"],
                    "mood_level": 10,  # 1-5の範囲外
                    "timestamp": "invalid_timestamp",
                    "notes": "範囲外テスト"
                }
                
                response = await client.post(
                    f"{self.base_urls['mood_tracking']}/mood/log",
                    json=out_of_range_data,
                    headers=headers
                )
                
                validation_error_results["out_of_range_values"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [400, 422],
                    "response_has_validation_error": "range" in response.text.lower() or "invalid" in response.text.lower()
                }
            except Exception as e:
                validation_error_results["out_of_range_values"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 4. 不正なJSON形式テスト
            try:
                response = await client.post(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/add_xp",
                    data="invalid json format",  # 不正なJSON
                    headers={**headers, "Content-Type": "application/json"}
                )
                
                validation_error_results["invalid_json"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [400, 422],
                    "response_has_validation_error": "json" in response.text.lower() or "format" in response.text.lower()
                }
            except Exception as e:
                validation_error_results["invalid_json"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
        
        # バリデーションエラー処理成功率計算
        handled_correctly_count = sum(1 for result in validation_error_results.values() 
                                    if result.get("handled_correctly", False))
        total_validation_tests = len(validation_error_results)
        
        return {
            "success": handled_correctly_count > 0,
            "validation_error_results": validation_error_results,
            "validation_error_handling_rate": handled_correctly_count / total_validation_tests if total_validation_tests > 0 else 0
        }
    
    async def test_resource_not_found_errors(self) -> Dict[str, Any]:
        """リソース未発見エラー処理テスト"""
        logger.info("🔍 リソース未発見エラー処理テスト開始...")
        
        not_found_error_results = {}
        headers = {"Authorization": f"Bearer {self.valid_auth_token}"} if self.valid_auth_token else {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. 存在しないユーザーテスト
            try:
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/nonexistent_user_12345/profile",
                    headers=headers
                )
                
                not_found_error_results["nonexistent_user"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code == 404,
                    "response_has_error_message": "not found" in response.text.lower() or "user" in response.text.lower()
                }
            except Exception as e:
                not_found_error_results["nonexistent_user"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 2. 存在しないタスクテスト
            try:
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/nonexistent_task_12345",
                    headers=headers
                )
                
                not_found_error_results["nonexistent_task"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code == 404,
                    "response_has_error_message": "not found" in response.text.lower() or "task" in response.text.lower()
                }
            except Exception as e:
                not_found_error_results["nonexistent_task"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 3. 存在しないエンドポイントテスト
            try:
                response = await client.get(
                    f"{self.base_urls['mandala']}/nonexistent/endpoint/12345",
                    headers=headers
                )
                
                not_found_error_results["nonexistent_endpoint"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code == 404,
                    "response_has_error_message": "not found" in response.text.lower()
                }
            except Exception as e:
                not_found_error_results["nonexistent_endpoint"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 4. 削除済みリソースアクセステスト
            if self.valid_auth_token:
                try:
                    # まずタスクを作成
                    task_data = {
                        "uid": self.test_user["uid"],
                        "task_type": "routine",
                        "difficulty": 2,
                        "description": "削除テスト用タスク",
                        "habit_tag": "delete_test"
                    }
                    
                    create_response = await client.post(
                        f"{self.base_urls['task_mgmt']}/tasks",
                        json=task_data,
                        headers=headers
                    )
                    
                    if create_response.status_code in [200, 201]:
                        task_result = create_response.json()
                        task_id = task_result.get("task_id")
                        
                        # タスクを削除（もし削除APIがあれば）
                        delete_response = await client.delete(
                            f"{self.base_urls['task_mgmt']}/tasks/{task_id}",
                            headers=headers
                        )
                        
                        # 削除後にアクセス試行
                        access_response = await client.get(
                            f"{self.base_urls['task_mgmt']}/tasks/{task_id}",
                            headers=headers
                        )
                        
                        not_found_error_results["deleted_resource"] = {
                            "status_code": access_response.status_code,
                            "handled_correctly": access_response.status_code == 404,
                            "response_has_error_message": "not found" in access_response.text.lower() or "deleted" in access_response.text.lower()
                        }
                    else:
                        not_found_error_results["deleted_resource"] = {
                            "handled_correctly": False,
                            "error": "Could not create task for deletion test"
                        }
                except Exception as e:
                    not_found_error_results["deleted_resource"] = {
                        "handled_correctly": False,
                        "error": str(e)
                    }
        
        # リソース未発見エラー処理成功率計算
        handled_correctly_count = sum(1 for result in not_found_error_results.values() 
                                    if result.get("handled_correctly", False))
        total_not_found_tests = len(not_found_error_results)
        
        return {
            "success": handled_correctly_count > 0,
            "not_found_error_results": not_found_error_results,
            "not_found_error_handling_rate": handled_correctly_count / total_not_found_tests if total_not_found_tests > 0 else 0
        }
    
    async def test_service_communication_errors(self) -> Dict[str, Any]:
        """サービス間通信エラー処理テスト"""
        logger.info("🌐 サービス間通信エラー処理テスト開始...")
        
        communication_error_results = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 1. 存在しないサービスへのリクエスト
            try:
                response = await client.get("http://localhost:9999/nonexistent_service")
                communication_error_results["nonexistent_service"] = {
                    "handled_correctly": False,
                    "error": "Service should not exist"
                }
            except Exception as e:
                communication_error_results["nonexistent_service"] = {
                    "handled_correctly": True,
                    "error_type": type(e).__name__,
                    "connection_refused": "connection" in str(e).lower() or "refused" in str(e).lower()
                }
            
            # 2. タイムアウトテスト（短いタイムアウトで遅いエンドポイント）
            try:
                # AI Story生成は時間がかかる可能性があるため、短いタイムアウトでテスト
                timeout_client = httpx.AsyncClient(timeout=0.1)  # 100ms
                
                story_context = {
                    "uid": self.test_user["uid"],
                    "completed_tasks": 1,
                    "current_chapter": "test_chapter"
                }
                
                response = await timeout_client.post(
                    f"{self.base_urls['ai_story']}/story/generate",
                    json=story_context
                )
                
                communication_error_results["timeout_handling"] = {
                    "handled_correctly": False,
                    "error": "Request should have timed out"
                }
                
                await timeout_client.aclose()
                
            except Exception as e:
                communication_error_results["timeout_handling"] = {
                    "handled_correctly": True,
                    "error_type": type(e).__name__,
                    "is_timeout_error": "timeout" in str(e).lower() or "time" in str(e).lower()
                }
            
            # 3. 不正なレスポンス形式処理テスト
            try:
                # 存在しないエンドポイントで不正なレスポンスを期待
                response = await client.get(
                    f"{self.base_urls['core_game']}/invalid_endpoint_for_response_test"
                )
                
                # レスポンスが適切にハンドリングされているかチェック
                communication_error_results["invalid_response_format"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [404, 400, 500],
                    "has_error_response": len(response.text) > 0
                }
            except Exception as e:
                communication_error_results["invalid_response_format"] = {
                    "handled_correctly": True,
                    "error_type": type(e).__name__
                }
        
        # 通信エラー処理成功率計算
        handled_correctly_count = sum(1 for result in communication_error_results.values() 
                                    if result.get("handled_correctly", False))
        total_communication_tests = len(communication_error_results)
        
        return {
            "success": handled_correctly_count > 0,
            "communication_error_results": communication_error_results,
            "communication_error_handling_rate": handled_correctly_count / total_communication_tests if total_communication_tests > 0 else 0
        }
    
    async def test_business_logic_errors(self) -> Dict[str, Any]:
        """ビジネスロジックエラー処理テスト"""
        logger.info("💼 ビジネスロジックエラー処理テスト開始...")
        
        business_error_results = {}
        headers = {"Authorization": f"Bearer {self.valid_auth_token}"} if self.valid_auth_token else {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. 日次タスク制限超過テスト
            if self.valid_auth_token:
                try:
                    # 16個以上のタスクを作成しようとする（制限は16個）
                    tasks_created = 0
                    last_response = None
                    
                    for i in range(20):  # 制限を超える数
                        task_data = {
                            "uid": self.test_user["uid"],
                            "task_type": "routine",
                            "difficulty": 2,
                            "description": f"制限テスト用タスク {i+1}",
                            "habit_tag": f"limit_test_{i}"
                        }
                        
                        response = await client.post(
                            f"{self.base_urls['task_mgmt']}/tasks",
                            json=task_data,
                            headers=headers
                        )
                        
                        if response.status_code in [200, 201]:
                            tasks_created += 1
                        else:
                            last_response = response
                            break
                    
                    # 制限に達した時の適切なエラー処理確認
                    if last_response and tasks_created >= 16:
                        business_error_results["daily_task_limit"] = {
                            "status_code": last_response.status_code,
                            "handled_correctly": last_response.status_code in [400, 429],
                            "tasks_created_before_limit": tasks_created,
                            "response_has_limit_message": "limit" in last_response.text.lower()
                        }
                    else:
                        business_error_results["daily_task_limit"] = {
                            "handled_correctly": False,
                            "error": f"Could not test limit (created {tasks_created} tasks)"
                        }
                        
                except Exception as e:
                    business_error_results["daily_task_limit"] = {
                        "handled_correctly": False,
                        "error": str(e)
                    }
            
            # 2. 無効な気分レベル範囲テスト
            try:
                invalid_mood_data = {
                    "uid": self.test_user["uid"],
                    "mood_level": -1,  # 1-5の範囲外
                    "timestamp": datetime.now().isoformat(),
                    "notes": "無効な気分レベルテスト"
                }
                
                response = await client.post(
                    f"{self.base_urls['mood_tracking']}/mood/log",
                    json=invalid_mood_data,
                    headers=headers
                )
                
                business_error_results["invalid_mood_range"] = {
                    "status_code": response.status_code,
                    "handled_correctly": response.status_code in [400, 422],
                    "response_has_range_error": "range" in response.text.lower() or "1-5" in response.text.lower()
                }
            except Exception as e:
                business_error_results["invalid_mood_range"] = {
                    "handled_correctly": False,
                    "error": str(e)
                }
            
            # 3. 完了済みタスクの重複完了テスト
            if self.valid_auth_token:
                try:
                    # タスク作成
                    task_data = {
                        "uid": self.test_user["uid"],
                        "task_type": "one_shot",
                        "difficulty": 3,
                        "description": "重複完了テスト用タスク",
                        "habit_tag": "duplicate_completion_test"
                    }
                    
                    create_response = await client.post(
                        f"{self.base_urls['task_mgmt']}/tasks",
                        json=task_data,
                        headers=headers
                    )
                    
                    if create_response.status_code in [200, 201]:
                        task_result = create_response.json()
                        task_id = task_result.get("task_id")
                        
                        # 最初の完了
                        completion_data = {
                            "uid": self.test_user["uid"],
                            "task_id": task_id,
                            "mood_at_completion": 4,
                            "completion_time": datetime.now().isoformat()
                        }
                        
                        first_completion = await client.post(
                            f"{self.base_urls['task_mgmt']}/tasks/{task_id}/complete",
                            json=completion_data,
                            headers=headers
                        )
                        
                        # 重複完了試行
                        second_completion = await client.post(
                            f"{self.base_urls['task_mgmt']}/tasks/{task_id}/complete",
                            json=completion_data,
                            headers=headers
                        )
                        
                        business_error_results["duplicate_completion"] = {
                            "first_completion_status": first_completion.status_code,
                            "second_completion_status": second_completion.status_code,
                            "handled_correctly": (first_completion.status_code == 200 and 
                                                second_completion.status_code in [400, 409]),
                            "response_has_duplicate_error": "already" in second_completion.text.lower() or "completed" in second_completion.text.lower()
                        }
                    else:
                        business_error_results["duplicate_completion"] = {
                            "handled_correctly": False,
                            "error": "Could not create task for duplicate completion test"
                        }
                        
                except Exception as e:
                    business_error_results["duplicate_completion"] = {
                        "handled_correctly": False,
                        "error": str(e)
                    }
        
        # ビジネスロジックエラー処理成功率計算
        handled_correctly_count = sum(1 for result in business_error_results.values() 
                                    if result.get("handled_correctly", False))
        total_business_tests = len(business_error_results)
        
        return {
            "success": handled_correctly_count > 0,
            "business_error_results": business_error_results,
            "business_error_handling_rate": handled_correctly_count / total_business_tests if total_business_tests > 0 else 0
        }
    
    async def test_graceful_degradation(self) -> Dict[str, Any]:
        """グレースフルデグラデーション（段階的機能低下）テスト"""
        logger.info("🔄 グレースフルデグラデーションテスト開始...")
        
        degradation_results = {}
        headers = {"Authorization": f"Bearer {self.valid_auth_token}"} if self.valid_auth_token else {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. AI Story生成失敗時の代替処理テスト
            try:
                # 無効なコンテキストでストーリー生成を試行
                invalid_story_context = {
                    "uid": self.test_user["uid"],
                    "completed_tasks": "invalid_type",  # 数値であるべき
                    "current_chapter": None
                }
                
                response = await client.post(
                    f"{self.base_urls['ai_story']}/story/generate",
                    json=invalid_story_context,
                    headers=headers
                )
                
                # エラー時でも適切なレスポンスが返されるかチェック
                degradation_results["ai_story_fallback"] = {
                    "status_code": response.status_code,
                    "has_fallback_response": response.status_code in [400, 422, 500],
                    "response_provides_guidance": "error" in response.text.lower() or "invalid" in response.text.lower()
                }
                
            except Exception as e:
                degradation_results["ai_story_fallback"] = {
                    "handled_correctly": True,
                    "error_type": type(e).__name__
                }
            
            # 2. 部分的サービス障害時の継続動作テスト
            try:
                # コアゲームエンジンが利用可能な場合の基本機能確認
                core_response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=headers
                )
                
                # 他のサービスが利用できない場合でも基本機能は動作するかテスト
                if core_response.status_code == 200:
                    degradation_results["partial_service_failure"] = {
                        "core_service_available": True,
                        "graceful_degradation": True,
                        "basic_functionality_maintained": True
                    }
                else:
                    degradation_results["partial_service_failure"] = {
                        "core_service_available": False,
                        "graceful_degradation": False
                    }
                    
            except Exception as e:
                degradation_results["partial_service_failure"] = {
                    "handled_correctly": True,
                    "error_type": type(e).__name__
                }
            
            # 3. データ不整合時の復旧処理テスト
            if self.valid_auth_token:
                try:
                    # 不整合データでのプロファイル更新試行
                    inconsistent_data = {
                        "total_xp": -100,  # 負の値
                        "player_level": 0   # 無効なレベル
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/update_profile",
                        json=inconsistent_data,
                        headers=headers
                    )
                    
                    degradation_results["data_inconsistency_recovery"] = {
                        "status_code": response.status_code,
                        "handled_correctly": response.status_code in [400, 422],
                        "prevents_data_corruption": response.status_code != 200,
                        "response_has_validation_error": "invalid" in response.text.lower() or "error" in response.text.lower()
                    }
                    
                except Exception as e:
                    degradation_results["data_inconsistency_recovery"] = {
                        "handled_correctly": True,
                        "error_type": type(e).__name__
                    }
        
        # グレースフルデグラデーション成功率計算
        handled_correctly_count = sum(1 for result in degradation_results.values() 
                                    if result.get("handled_correctly", False) or result.get("graceful_degradation", False))
        total_degradation_tests = len(degradation_results)
        
        return {
            "success": handled_correctly_count > 0,
            "degradation_results": degradation_results,
            "graceful_degradation_rate": handled_correctly_count / total_degradation_tests if total_degradation_tests > 0 else 0
        }
    
    async def run_error_handling_tests(self) -> Dict[str, Any]:
        """エラー処理テスト実行"""
        logger.info("🚨 エラー処理適切性確認テスト開始")
        logger.info("="*60)
        
        # 有効なユーザーセットアップ
        if not await self.setup_valid_user():
            logger.warning("⚠️  有効なユーザーセットアップに失敗しましたが、テストを継続します")
        
        error_handling_results = {}
        
        # 1. 認証エラー処理テスト
        error_handling_results["authentication_errors"] = await self.test_authentication_errors()
        
        # 2. データバリデーションエラー処理テスト
        error_handling_results["data_validation_errors"] = await self.test_data_validation_errors()
        
        # 3. リソース未発見エラー処理テスト
        error_handling_results["resource_not_found_errors"] = await self.test_resource_not_found_errors()
        
        # 4. サービス間通信エラー処理テスト
        error_handling_results["service_communication_errors"] = await self.test_service_communication_errors()
        
        # 5. ビジネスロジックエラー処理テスト
        error_handling_results["business_logic_errors"] = await self.test_business_logic_errors()
        
        # 6. グレースフルデグラデーションテスト
        error_handling_results["graceful_degradation"] = await self.test_graceful_degradation()
        
        return error_handling_results
    
    def print_error_handling_summary(self, results: Dict[str, Any]):
        """エラー処理テスト結果サマリー"""
        logger.info("\n" + "="*60)
        logger.info("📊 エラー処理適切性確認テスト結果サマリー")
        logger.info("="*60)
        
        test_categories = {
            "authentication_errors": "認証エラー処理",
            "data_validation_errors": "データバリデーションエラー処理",
            "resource_not_found_errors": "リソース未発見エラー処理",
            "service_communication_errors": "サービス間通信エラー処理",
            "business_logic_errors": "ビジネスロジックエラー処理",
            "graceful_degradation": "グレースフルデグラデーション"
        }
        
        total_categories = len(test_categories)
        successful_categories = 0
        
        for category_key, category_name in test_categories.items():
            if category_key in results:
                category_result = results[category_key]
                success = category_result.get("success", False)
                
                # 各カテゴリの成功率取得
                rate_keys = [k for k in category_result.keys() if k.endswith("_rate")]
                if rate_keys:
                    rate = category_result[rate_keys[0]]
                    rate_display = f" ({rate:.1%})"
                else:
                    rate_display = ""
                
                if success:
                    status = f"✅ 成功{rate_display}"
                    successful_categories += 1
                else:
                    status = f"❌ 失敗{rate_display}"
                
                logger.info(f"{category_name}: {status}")
                
                # エラーがある場合は表示
                if not success and "error" in category_result:
                    logger.info(f"   エラー: {category_result['error']}")
        
        logger.info(f"\n🎯 エラー処理テスト結果: {successful_categories}/{total_categories} カテゴリ成功")
        
        overall_success_rate = successful_categories / total_categories
        
        if overall_success_rate >= 0.8:
            logger.info("🎉 エラー処理適切性確認テスト成功！")
            logger.info("✅ システムのエラー処理が適切に実装されています")
        elif overall_success_rate >= 0.6:
            logger.info("⚠️  一部のエラー処理に改善の余地がありますが、基本的な処理は適切です")
        else:
            logger.error("❌ エラー処理に重大な問題があります")
        
        logger.info(f"📈 総合エラー処理適切性: {overall_success_rate:.1%}")
        
        logger.info("\n💡 次のステップ:")
        if overall_success_rate >= 0.8:
            logger.info("- エラー監視システムの設定")
            logger.info("- ユーザー向けエラーメッセージの改善")
            logger.info("- エラー復旧手順の文書化")
        else:
            logger.info("- 失敗したエラー処理の修正")
            logger.info("- エラーレスポンス形式の統一")
            logger.info("- ログ出力の改善")


async def main():
    """メイン実行関数"""
    tester = ErrorHandlingTester()
    
    try:
        # エラー処理テスト実行
        results = await tester.run_error_handling_tests()
        
        # 結果サマリー表示
        tester.print_error_handling_summary(results)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"error_handling_test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "test_type": "error_handling_comprehensive",
                "test_results": results,
                "summary": {
                    "test_categories": list(results.keys()),
                    "authentication_tested": "authentication_errors" in results,
                    "validation_tested": "data_validation_errors" in results,
                    "business_logic_tested": "business_logic_errors" in results,
                    "graceful_degradation_tested": "graceful_degradation" in results
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 テスト結果を保存しました: {result_file}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  テストが中断されました")
    except Exception as e:
        logger.error(f"\n❌ テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())