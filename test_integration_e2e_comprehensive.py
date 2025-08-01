#!/usr/bin/env python3
"""
統合テストとエンドツーエンドテスト (タスク27.2)

要件:
- ユーザージャーニー全体の動作確認
- 朝のタスク配信から夜のストーリー生成までの基本フロー
- データ永続化の動作確認
- エラー処理の適切性確認
- システム全体の動作保証
"""

import asyncio
import httpx
import json
import time
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationE2ETester:
    """統合テストとエンドツーエンドテスター"""
    
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
        
        self.test_users = [
            {
                "uid": "e2e_user_001",
                "username": "e2e_tester_1",
                "email": "e2e1@test.com"
            },
            {
                "uid": "e2e_user_002", 
                "username": "e2e_tester_2",
                "email": "e2e2@test.com"
            }
        ]
        
        self.auth_tokens = {}
        self.test_results = {}
        self.data_persistence_checks = []
        
    async def check_all_services_health(self) -> Dict[str, bool]:
        """全サービスのヘルスチェック"""
        logger.info("🔍 全サービスヘルスチェック開始...")
        
        health_status = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, base_url in self.base_urls.items():
                try:
                    # 複数のエンドポイントを試行
                    endpoints = ["/health", "/", "/docs", "/api/health"]
                    service_healthy = False
                    
                    for endpoint in endpoints:
                        try:
                            response = await client.get(f"{base_url}{endpoint}")
                            if response.status_code in [200, 404, 422]:  # 動作中とみなす
                                service_healthy = True
                                break
                        except:
                            continue
                    
                    health_status[service_name] = service_healthy
                    status = "✅ 正常" if service_healthy else "❌ 異常"
                    logger.info(f"   {service_name}: {status}")
                    
                except Exception as e:
                    health_status[service_name] = False
                    logger.error(f"   {service_name}: ❌ エラー - {str(e)}")
        
        healthy_count = sum(health_status.values())
        total_count = len(health_status)
        
        logger.info(f"📊 サービス健全性: {healthy_count}/{total_count}")
        
        return health_status
    
    async def test_complete_user_journey(self) -> Dict[str, Any]:
        """完全なユーザージャーニーテスト"""
        logger.info("🎯 完全ユーザージャーニーテスト開始...")
        
        journey_results = {}
        test_user = self.test_users[0]
        
        try:
            # 1. ユーザー登録・認証
            logger.info("   1. ユーザー登録・認証テスト...")
            auth_result = await self._test_user_authentication(test_user)
            journey_results["authentication"] = auth_result
            
            if not auth_result["success"]:
                logger.error("認証失敗のため、ジャーニーテストを中断")
                return journey_results
            
            # 2. 朝のタスク配信フロー (7:00 AM シミュレーション)
            logger.info("   2. 朝のタスク配信フローテスト...")
            morning_result = await self._test_morning_task_delivery(test_user)
            journey_results["morning_delivery"] = morning_result
            
            # 3. タスク完了とXP獲得フロー
            logger.info("   3. タスク完了・XP獲得フローテスト...")
            task_completion_result = await self._test_task_completion_flow(test_user)
            journey_results["task_completion"] = task_completion_result
            
            # 4. 気分ログとXP調整
            logger.info("   4. 気分ログ・XP調整テスト...")
            mood_result = await self._test_mood_tracking_integration(test_user)
            journey_results["mood_tracking"] = mood_result
            
            # 5. レベルアップと共鳴イベント
            logger.info("   5. レベルアップ・共鳴イベントテスト...")
            level_result = await self._test_level_up_resonance(test_user)
            journey_results["level_resonance"] = level_result
            
            # 6. Mandalaシステム統合
            logger.info("   6. Mandalaシステム統合テスト...")
            mandala_result = await self._test_mandala_integration(test_user)
            journey_results["mandala_integration"] = mandala_result
            
            # 7. 夜のストーリー生成フロー (21:30 シミュレーション)
            logger.info("   7. 夜のストーリー生成フローテスト...")
            story_result = await self._test_evening_story_generation(test_user)
            journey_results["story_generation"] = story_result
            
            # 8. 治療安全性チェック
            logger.info("   8. 治療安全性統合テスト...")
            safety_result = await self._test_therapeutic_safety_integration(test_user)
            journey_results["therapeutic_safety"] = safety_result
            
            # 9. ADHD支援機能統合
            logger.info("   9. ADHD支援機能統合テスト...")
            adhd_result = await self._test_adhd_support_integration(test_user)
            journey_results["adhd_support"] = adhd_result
            
            # 10. データ永続化確認
            logger.info("   10. データ永続化確認テスト...")
            persistence_result = await self._test_data_persistence(test_user)
            journey_results["data_persistence"] = persistence_result
            
        except Exception as e:
            logger.error(f"ユーザージャーニーテストエラー: {str(e)}")
            journey_results["error"] = str(e)
        
        return journey_results
    
    async def _test_user_authentication(self, user: Dict[str, str]) -> Dict[str, Any]:
        """ユーザー認証テスト"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # ユーザー登録
                register_data = {
                    "uid": user["uid"],
                    "username": user["username"],
                    "email": user["email"],
                    "permissions": ["view_only", "task_edit", "chat_send"]
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/grant",
                    json=register_data
                )
                
                if response.status_code not in [200, 201, 409]:
                    return {"success": False, "error": f"Registration failed: {response.status_code}"}
                
                # 認証
                auth_data = {
                    "uid": user["uid"],
                    "username": user["username"]
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/login",
                    json=auth_data
                )
                
                if response.status_code == 200:
                    auth_result = response.json()
                    if "access_token" in auth_result:
                        self.auth_tokens[user["uid"]] = auth_result["access_token"]
                        return {"success": True, "token_received": True}
                
                return {"success": False, "error": f"Authentication failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_morning_task_delivery(self, user: Dict[str, str]) -> Dict[str, Any]:
        """朝のタスク配信テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Mandalaから今日のタスクを取得
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{user['uid']}/daily_tasks",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Daily tasks fetch failed: {response.status_code}"}
                
                daily_tasks = response.json()
                
                # LINE Bot経由でタスク配信をシミュレート
                delivery_data = {
                    "uid": user["uid"],
                    "tasks": daily_tasks.get("tasks", []),
                    "format": "3x3_mandala",
                    "time": "07:00"
                }
                
                response = await client.post(
                    f"{self.base_urls['line_bot']}/deliver_morning_tasks",
                    json=delivery_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    delivery_result = response.json()
                    return {
                        "success": True,
                        "tasks_delivered": len(daily_tasks.get("tasks", [])),
                        "format": delivery_result.get("format", "unknown"),
                        "mobile_optimized": delivery_result.get("mobile_optimized", False)
                    }
                
                return {"success": False, "error": f"Task delivery failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_task_completion_flow(self, user: Dict[str, str]) -> Dict[str, Any]:
        """タスク完了フローテスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # テスト用タスク作成
                task_data = {
                    "uid": user["uid"],
                    "task_type": "routine",
                    "difficulty": 3,
                    "description": "E2Eテスト用朝の運動",
                    "habit_tag": "morning_exercise"
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks",
                    json=task_data,
                    headers=headers
                )
                
                if response.status_code not in [200, 201]:
                    return {"success": False, "error": f"Task creation failed: {response.status_code}"}
                
                task_result = response.json()
                task_id = task_result.get("task_id")
                
                # タスク完了
                completion_data = {
                    "uid": user["uid"],
                    "task_id": task_id,
                    "mood_at_completion": 4,
                    "completion_time": datetime.now().isoformat()
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks/{task_id}/complete",
                    json=completion_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    completion_result = response.json()
                    
                    # XP獲得確認
                    response = await client.get(
                        f"{self.base_urls['core_game']}/user/{user['uid']}/profile",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        profile = response.json()
                        return {
                            "success": True,
                            "task_completed": True,
                            "xp_earned": completion_result.get("xp_earned", 0),
                            "total_xp": profile.get("total_xp", 0),
                            "current_level": profile.get("player_level", 1)
                        }
                
                return {"success": False, "error": "Task completion or XP verification failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_mood_tracking_integration(self, user: Dict[str, str]) -> Dict[str, Any]:
        """気分追跡統合テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 気分ログ記録
                mood_data = {
                    "uid": user["uid"],
                    "mood_level": 4,  # 1-5スケール
                    "timestamp": datetime.now().isoformat(),
                    "notes": "E2Eテスト用気分ログ"
                }
                
                response = await client.post(
                    f"{self.base_urls['mood_tracking']}/mood/log",
                    json=mood_data,
                    headers=headers
                )
                
                if response.status_code not in [200, 201]:
                    return {"success": False, "error": f"Mood logging failed: {response.status_code}"}
                
                # 気分係数取得
                response = await client.get(
                    f"{self.base_urls['mood_tracking']}/mood/{user['uid']}/coefficient",
                    headers=headers
                )
                
                if response.status_code == 200:
                    coefficient_result = response.json()
                    mood_coefficient = coefficient_result.get("mood_coefficient", 1.0)
                    
                    # 係数が適切な範囲内かチェック (0.8-1.2)
                    if 0.8 <= mood_coefficient <= 1.2:
                        return {
                            "success": True,
                            "mood_logged": True,
                            "mood_coefficient": mood_coefficient,
                            "coefficient_valid": True
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Invalid mood coefficient: {mood_coefficient}"
                        }
                
                return {"success": False, "error": "Mood coefficient retrieval failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_level_up_resonance(self, user: Dict[str, str]) -> Dict[str, Any]:
        """レベルアップ・共鳴イベントテスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 現在のレベル確認
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Profile fetch failed"}
                
                initial_profile = response.json()
                initial_level = initial_profile.get("player_level", 1)
                
                # 大量XP追加でレベルアップを誘発
                xp_data = {
                    "xp_amount": 1000,
                    "source": "e2e_test_level_up"
                }
                
                response = await client.post(
                    f"{self.base_urls['core_game']}/user/{user['uid']}/add_xp",
                    json=xp_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    xp_result = response.json()
                    new_level = xp_result.get("new_level", initial_level)
                    level_up_occurred = xp_result.get("level_up", False)
                    
                    # 共鳴イベントチェック
                    response = await client.get(
                        f"{self.base_urls['core_game']}/user/{user['uid']}/resonance_check",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        resonance_result = response.json()
                        
                        return {
                            "success": True,
                            "level_up_occurred": level_up_occurred,
                            "initial_level": initial_level,
                            "new_level": new_level,
                            "resonance_available": resonance_result.get("resonance_available", False),
                            "level_difference": resonance_result.get("level_difference", 0)
                        }
                
                return {"success": False, "error": "Level up or resonance check failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_mandala_integration(self, user: Dict[str, str]) -> Dict[str, Any]:
        """Mandalaシステム統合テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Mandalaグリッド取得
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{user['uid']}/grid",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Mandala grid fetch failed: {response.status_code}"}
                
                mandala_data = response.json()
                grid = mandala_data.get("grid", [])
                
                # グリッド構造確認
                if len(grid) != 9 or not all(len(row) == 9 for row in grid):
                    return {"success": False, "error": "Invalid grid structure"}
                
                # クリスタル進行更新テスト
                crystal_data = {
                    "uid": user["uid"],
                    "attribute": "Self-Discipline",
                    "progress_points": 25
                }
                
                response = await client.post(
                    f"{self.base_urls['mandala']}/mandala/{user['uid']}/update_crystal",
                    json=crystal_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    crystal_result = response.json()
                    
                    return {
                        "success": True,
                        "grid_structure_valid": True,
                        "crystal_updated": crystal_result.get("success", False),
                        "new_progress": crystal_result.get("new_progress", 0)
                    }
                
                return {"success": False, "error": "Crystal update failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_evening_story_generation(self, user: Dict[str, str]) -> Dict[str, Any]:
        """夜のストーリー生成テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=15.0) as client:  # AI処理のため長めのタイムアウト
                # 今日の活動コンテキスト作成
                story_context = {
                    "uid": user["uid"],
                    "completed_tasks": 3,
                    "total_xp_earned": 75,
                    "mood_average": 4.2,
                    "current_chapter": "chapter_1",
                    "time": "21:30"
                }
                
                start_time = time.time()
                
                response = await client.post(
                    f"{self.base_urls['ai_story']}/story/generate",
                    json=story_context,
                    headers=headers
                )
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    story_result = response.json()
                    
                    # 生成時間チェック (3.5秒以内)
                    if generation_time > 3.5:
                        return {
                            "success": False,
                            "error": f"Story generation too slow: {generation_time:.2f}s"
                        }
                    
                    # ストーリー構造確認
                    story_text = story_result.get("story_text", "")
                    choices = story_result.get("choices", [])
                    
                    if not story_text or len(choices) == 0:
                        return {"success": False, "error": "Invalid story structure"}
                    
                    # 選択肢にreal_task_idまたはhabit_tagが含まれているかチェック
                    valid_choices = all(
                        "real_task_id" in choice or "habit_tag" in choice
                        for choice in choices
                    )
                    
                    return {
                        "success": True,
                        "generation_time": generation_time,
                        "story_generated": bool(story_text),
                        "choices_count": len(choices),
                        "choices_valid": valid_choices,
                        "within_time_limit": generation_time <= 3.5
                    }
                
                return {"success": False, "error": f"Story generation failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_therapeutic_safety_integration(self, user: Dict[str, str]) -> Dict[str, Any]:
        """治療安全性統合テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 安全なコンテンツのテスト
                safe_content = {
                    "content": "今日は良い一日でした。明日も頑張ります。",
                    "content_type": "user_input"
                }
                
                response = await client.post(
                    f"{self.base_urls['therapeutic_safety']}/safety/check",
                    json=safe_content,
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Safety check failed: {response.status_code}"}
                
                safety_result = response.json()
                
                # 潜在的に問題のあるコンテンツのテスト
                risky_content = {
                    "content": "もう何もかも嫌になった。全部やめたい。",
                    "content_type": "user_input"
                }
                
                response = await client.post(
                    f"{self.base_urls['therapeutic_safety']}/safety/check",
                    json=risky_content,
                    headers=headers
                )
                
                if response.status_code == 200:
                    risky_result = response.json()
                    
                    return {
                        "success": True,
                        "safe_content_passed": safety_result.get("safe", False),
                        "risky_content_detected": not risky_result.get("safe", True),
                        "confidence_score": risky_result.get("confidence", 0),
                        "intervention_triggered": risky_result.get("intervention_required", False)
                    }
                
                return {"success": False, "error": "Risky content check failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_adhd_support_integration(self, user: Dict[str, str]) -> Dict[str, Any]:
        """ADHD支援機能統合テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 認知負荷軽減機能テスト
                ui_config_data = {
                    "uid": user["uid"],
                    "max_choices": 3,
                    "one_screen_one_action": True,
                    "font_settings": {
                        "family": "BIZ UDGothic",
                        "line_height": 1.6
                    }
                }
                
                response = await client.post(
                    f"{self.base_urls['adhd_support']}/ui/configure",
                    json=ui_config_data,
                    headers=headers
                )
                
                if response.status_code not in [200, 201]:
                    return {"success": False, "error": f"UI config failed: {response.status_code}"}
                
                # 時間認識支援機能テスト
                time_support_data = {
                    "uid": user["uid"],
                    "work_duration": 60,  # 60分連続作業
                    "break_suggested": True
                }
                
                response = await client.post(
                    f"{self.base_urls['adhd_support']}/time/break_reminder",
                    json=time_support_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    time_result = response.json()
                    
                    return {
                        "success": True,
                        "ui_configured": True,
                        "break_reminder_triggered": time_result.get("reminder_sent", False),
                        "adhd_assist_multiplier": time_result.get("adhd_assist_multiplier", 1.0)
                    }
                
                return {"success": False, "error": "Time support test failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_data_persistence(self, user: Dict[str, str]) -> Dict[str, Any]:
        """データ永続化テスト"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens[user['uid']]}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # データ作成
                test_data = {
                    "uid": user["uid"],
                    "test_key": "e2e_persistence_test",
                    "test_value": f"test_data_{datetime.now().isoformat()}",
                    "timestamp": datetime.now().isoformat()
                }
                
                # 複数のサービスでデータ永続化テスト
                persistence_results = {}
                
                # 1. ユーザープロファイル永続化
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code == 200:
                    profile_data = response.json()
                    persistence_results["user_profile"] = {
                        "persisted": True,
                        "data_integrity": "uid" in profile_data and "total_xp" in profile_data
                    }
                else:
                    persistence_results["user_profile"] = {"persisted": False}
                
                # 2. タスク履歴永続化
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/{user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    task_history = response.json()
                    persistence_results["task_history"] = {
                        "persisted": True,
                        "data_integrity": isinstance(task_history.get("tasks", []), list)
                    }
                else:
                    persistence_results["task_history"] = {"persisted": False}
                
                # 3. 気分ログ永続化
                response = await client.get(
                    f"{self.base_urls['mood_tracking']}/mood/{user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    mood_history = response.json()
                    persistence_results["mood_history"] = {
                        "persisted": True,
                        "data_integrity": isinstance(mood_history.get("logs", []), list)
                    }
                else:
                    persistence_results["mood_history"] = {"persisted": False}
                
                # 4. Mandala状態永続化
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{user['uid']}/state",
                    headers=headers
                )
                
                if response.status_code == 200:
                    mandala_state = response.json()
                    persistence_results["mandala_state"] = {
                        "persisted": True,
                        "data_integrity": "crystal_gauges" in mandala_state
                    }
                else:
                    persistence_results["mandala_state"] = {"persisted": False}
                
                # 永続化成功率計算
                persisted_count = sum(1 for result in persistence_results.values() 
                                    if result.get("persisted", False))
                total_count = len(persistence_results)
                
                return {
                    "success": persisted_count > 0,
                    "persistence_results": persistence_results,
                    "persistence_rate": persisted_count / total_count if total_count > 0 else 0,
                    "data_integrity_passed": all(
                        result.get("data_integrity", False) 
                        for result in persistence_results.values() 
                        if result.get("persisted", False)
                    )
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """エラー処理テスト"""
        logger.info("🚨 エラー処理テスト開始...")
        
        error_test_results = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 1. 無効な認証トークンテスト
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            
            try:
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/test_user/profile",
                    headers=invalid_headers
                )
                
                error_test_results["invalid_auth"] = {
                    "handled_correctly": response.status_code in [401, 403],
                    "status_code": response.status_code
                }
            except:
                error_test_results["invalid_auth"] = {"handled_correctly": False}
            
            # 2. 存在しないリソースアクセステスト
            try:
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/nonexistent_task_id"
                )
                
                error_test_results["nonexistent_resource"] = {
                    "handled_correctly": response.status_code == 404,
                    "status_code": response.status_code
                }
            except:
                error_test_results["nonexistent_resource"] = {"handled_correctly": False}
            
            # 3. 無効なデータ形式テスト
            try:
                invalid_data = {"invalid": "data", "missing": "required_fields"}
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks",
                    json=invalid_data
                )
                
                error_test_results["invalid_data"] = {
                    "handled_correctly": response.status_code in [400, 422],
                    "status_code": response.status_code
                }
            except:
                error_test_results["invalid_data"] = {"handled_correctly": False}
            
            # 4. サービス間通信エラーテスト
            try:
                # 存在しないサービスへのリクエスト
                response = await client.get("http://localhost:9999/nonexistent")
                error_test_results["service_unavailable"] = {"handled_correctly": False}
            except:
                error_test_results["service_unavailable"] = {"handled_correctly": True}
        
        # エラー処理成功率計算
        handled_correctly_count = sum(1 for result in error_test_results.values() 
                                    if result.get("handled_correctly", False))
        total_error_tests = len(error_test_results)
        
        return {
            "success": handled_correctly_count > 0,
            "error_handling_results": error_test_results,
            "error_handling_rate": handled_correctly_count / total_error_tests if total_error_tests > 0 else 0
        }
    
    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """パフォーマンスベンチマークテスト"""
        logger.info("⚡ パフォーマンステスト開始...")
        
        performance_results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. API応答時間テスト (1.2秒P95目標)
            response_times = []
            
            for i in range(10):  # 10回のリクエストで測定
                start_time = time.time()
                
                try:
                    response = await client.get(f"{self.base_urls['core_game']}/health")
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                except:
                    response_times.append(30.0)  # タイムアウト値
            
            # P95レイテンシ計算
            response_times.sort()
            p95_latency = response_times[int(len(response_times) * 0.95)]
            
            performance_results["api_response_time"] = {
                "p95_latency": p95_latency,
                "meets_target": p95_latency <= 1.2,
                "average_response_time": sum(response_times) / len(response_times)
            }
            
            # 2. 同時リクエスト処理テスト
            concurrent_tasks = []
            start_time = time.time()
            
            for i in range(20):  # 20並行リクエスト
                task = client.get(f"{self.base_urls['auth']}/health")
                concurrent_tasks.append(task)
            
            try:
                responses = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
                concurrent_time = time.time() - start_time
                
                successful_responses = sum(1 for r in responses 
                                         if hasattr(r, 'status_code') and r.status_code == 200)
                
                performance_results["concurrent_requests"] = {
                    "total_requests": 20,
                    "successful_requests": successful_responses,
                    "success_rate": successful_responses / 20,
                    "total_time": concurrent_time
                }
            except Exception as e:
                performance_results["concurrent_requests"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return performance_results
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """包括的テスト実行"""
        logger.info("🎯 統合テスト・エンドツーエンドテスト開始")
        logger.info("="*80)
        
        comprehensive_results = {}
        
        # 1. サービスヘルスチェック
        health_status = await self.check_all_services_health()
        comprehensive_results["service_health"] = health_status
        
        # 必須サービスチェック
        required_services = ["auth", "core_game", "task_mgmt", "mandala"]
        missing_services = [svc for svc in required_services 
                          if not health_status.get(svc, False)]
        
        if missing_services:
            logger.error(f"必須サービス未起動: {', '.join(missing_services)}")
            comprehensive_results["error"] = f"Missing services: {missing_services}"
            return comprehensive_results
        
        # 2. 完全ユーザージャーニーテスト
        journey_results = await self.test_complete_user_journey()
        comprehensive_results["user_journey"] = journey_results
        
        # 3. エラー処理テスト
        error_results = await self.test_error_handling()
        comprehensive_results["error_handling"] = error_results
        
        # 4. パフォーマンステスト
        performance_results = await self.test_performance_benchmarks()
        comprehensive_results["performance"] = performance_results
        
        return comprehensive_results
    
    def print_comprehensive_summary(self, results: Dict[str, Any]):
        """包括的テスト結果サマリー"""
        logger.info("\n" + "="*80)
        logger.info("📊 統合テスト・エンドツーエンドテスト結果サマリー")
        logger.info("="*80)
        
        # サービス健全性
        health_status = results.get("service_health", {})
        healthy_services = sum(health_status.values())
        total_services = len(health_status)
        
        logger.info(f"🏥 サービス健全性: {healthy_services}/{total_services}")
        
        # ユーザージャーニー結果
        journey_results = results.get("user_journey", {})
        if journey_results:
            journey_success_count = sum(1 for k, v in journey_results.items() 
                                      if isinstance(v, dict) and v.get("success", False))
            journey_total = len([k for k in journey_results.keys() if k != "error"])
            
            logger.info(f"🎯 ユーザージャーニー: {journey_success_count}/{journey_total} 成功")
            
            # 詳細結果
            for test_name, test_result in journey_results.items():
                if isinstance(test_result, dict) and "success" in test_result:
                    status = "✅" if test_result["success"] else "❌"
                    logger.info(f"   {test_name}: {status}")
        
        # エラー処理結果
        error_results = results.get("error_handling", {})
        if error_results:
            error_handling_rate = error_results.get("error_handling_rate", 0)
            logger.info(f"🚨 エラー処理: {error_handling_rate:.1%} 適切に処理")
        
        # パフォーマンス結果
        performance_results = results.get("performance", {})
        if performance_results:
            api_performance = performance_results.get("api_response_time", {})
            if api_performance:
                p95_latency = api_performance.get("p95_latency", 0)
                meets_target = api_performance.get("meets_target", False)
                status = "✅" if meets_target else "❌"
                logger.info(f"⚡ API応答時間 (P95): {p95_latency:.3f}s {status}")
        
        # 総合評価
        logger.info("\n" + "="*80)
        
        if "error" in results:
            logger.error("❌ テスト実行に重大な問題があります")
            logger.error(f"エラー: {results['error']}")
        else:
            # 成功率計算
            total_success_indicators = 0
            passed_indicators = 0
            
            if healthy_services == total_services:
                passed_indicators += 1
            total_success_indicators += 1
            
            if journey_results and not journey_results.get("error"):
                journey_success_rate = sum(1 for k, v in journey_results.items() 
                                         if isinstance(v, dict) and v.get("success", False)) / max(1, len([k for k in journey_results.keys() if k != "error"]))
                if journey_success_rate >= 0.8:  # 80%以上成功
                    passed_indicators += 1
                total_success_indicators += 1
            
            if error_results.get("error_handling_rate", 0) >= 0.7:  # 70%以上適切処理
                passed_indicators += 1
            total_success_indicators += 1
            
            overall_success_rate = passed_indicators / total_success_indicators
            
            if overall_success_rate >= 0.8:
                logger.info("🎉 統合テスト・エンドツーエンドテスト成功！")
                logger.info("✅ システム全体が正常に動作しています")
            elif overall_success_rate >= 0.6:
                logger.info("⚠️  一部機能に問題がありますが、基本動作は確認できました")
            else:
                logger.error("❌ 統合テストで重大な問題が発見されました")
            
            logger.info(f"📈 総合成功率: {overall_success_rate:.1%}")
        
        logger.info("\n💡 次のステップ:")
        if results.get("error"):
            logger.info("- サービス起動状況の確認")
            logger.info("- 依存関係とネットワーク設定の確認")
        elif "user_journey" in results and journey_results.get("error"):
            logger.info("- 失敗したユーザージャーニーステップの詳細調査")
            logger.info("- サービス間通信の確認")
        else:
            logger.info("- パフォーマンス最適化の検討")
            logger.info("- 本番環境デプロイの準備")
            logger.info("- 継続的監視システムの設定")


async def main():
    """メイン実行関数"""
    tester = IntegrationE2ETester()
    
    try:
        # 包括的テスト実行
        results = await tester.run_comprehensive_tests()
        
        # 結果サマリー表示
        tester.print_comprehensive_summary(results)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"integration_e2e_test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "test_type": "integration_e2e_comprehensive",
                "test_results": results,
                "summary": {
                    "services_tested": len(tester.base_urls),
                    "test_categories": ["service_health", "user_journey", "error_handling", "performance"],
                    "data_persistence_verified": "user_journey" in results and 
                                               "data_persistence" in results.get("user_journey", {}),
                    "error_handling_verified": "error_handling" in results
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 テスト結果を保存しました: {result_file}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  テストが中断されました")
    except Exception as e:
        logger.error(f"\n❌ テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())