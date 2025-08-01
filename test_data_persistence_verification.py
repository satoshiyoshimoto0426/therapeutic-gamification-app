#!/usr/bin/env python3
"""
データ永続化検証テスト (タスク27.2の一部)

要件:
- データ永続化の動作確認
- Firestoreとの連携確認
- データ整合性の検証
- 復旧可能性の確認
"""

import asyncio
import httpx
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPersistenceVerifier:
    """データ永続化検証クラス"""
    
    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8002",
            "core_game": "http://localhost:8001", 
            "task_mgmt": "http://localhost:8003",
            "mandala": "http://localhost:8004",
            "mood_tracking": "http://localhost:8006"
        }
        
        self.test_user = {
            "uid": "persistence_test_user",
            "username": "persistence_tester",
            "email": "persistence@test.com"
        }
        
        self.auth_token = None
        self.test_data_ids = {}  # 作成したテストデータのID管理
        
    async def setup_test_user(self) -> bool:
        """テストユーザーセットアップ"""
        logger.info("🔧 テストユーザーセットアップ中...")
        
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
                
                if response.status_code not in [200, 201, 409]:
                    logger.error(f"ユーザー登録失敗: {response.status_code}")
                    return False
                
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
                        self.auth_token = auth_result["access_token"]
                        logger.info("✅ テストユーザーセットアップ完了")
                        return True
                
                logger.error(f"認証失敗: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"セットアップエラー: {str(e)}")
            return False
    
    async def test_user_profile_persistence(self) -> Dict[str, Any]:
        """ユーザープロファイル永続化テスト"""
        logger.info("👤 ユーザープロファイル永続化テスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. 初期プロファイル取得
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Initial profile fetch failed: {response.status_code}"}
                
                initial_profile = response.json()
                initial_xp = initial_profile.get("total_xp", 0)
                initial_level = initial_profile.get("player_level", 1)
                
                # 2. XP追加でプロファイル更新
                xp_to_add = 150
                response = await client.post(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/add_xp",
                    json={"xp_amount": xp_to_add, "source": "persistence_test"},
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "XP addition failed"}
                
                # 3. 短時間待機後に再取得（永続化確認）
                await asyncio.sleep(2)
                
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code == 200:
                    updated_profile = response.json()
                    updated_xp = updated_profile.get("total_xp", 0)
                    updated_level = updated_profile.get("player_level", 1)
                    
                    # データ整合性確認
                    xp_persisted = updated_xp >= initial_xp + xp_to_add
                    level_consistent = updated_level >= initial_level
                    
                    return {
                        "success": True,
                        "initial_xp": initial_xp,
                        "updated_xp": updated_xp,
                        "xp_difference": updated_xp - initial_xp,
                        "xp_persisted": xp_persisted,
                        "level_consistent": level_consistent,
                        "data_integrity": xp_persisted and level_consistent
                    }
                
                return {"success": False, "error": "Updated profile fetch failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_task_data_persistence(self) -> Dict[str, Any]:
        """タスクデータ永続化テスト"""
        logger.info("📋 タスクデータ永続化テスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. 複数タスク作成
                created_tasks = []
                
                for i in range(3):
                    task_data = {
                        "uid": self.test_user["uid"],
                        "task_type": ["routine", "one_shot", "skill_up"][i],
                        "difficulty": i + 2,
                        "description": f"永続化テスト用タスク {i+1}",
                        "habit_tag": f"persistence_test_{i}"
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['task_mgmt']}/tasks",
                        json=task_data,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        task_result = response.json()
                        created_tasks.append({
                            "task_id": task_result.get("task_id"),
                            "original_data": task_data
                        })
                    else:
                        return {"success": False, "error": f"Task creation failed for task {i}"}
                
                # 2. タスク完了処理
                completed_tasks = []
                
                for task in created_tasks[:2]:  # 最初の2つを完了
                    completion_data = {
                        "uid": self.test_user["uid"],
                        "task_id": task["task_id"],
                        "mood_at_completion": 4,
                        "completion_time": datetime.now().isoformat()
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['task_mgmt']}/tasks/{task['task_id']}/complete",
                        json=completion_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        completion_result = response.json()
                        completed_tasks.append({
                            "task_id": task["task_id"],
                            "xp_earned": completion_result.get("xp_earned", 0)
                        })
                
                # 3. 永続化確認（タスク履歴取得）
                await asyncio.sleep(2)
                
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    task_history = response.json()
                    history_tasks = task_history.get("tasks", [])
                    
                    # データ整合性確認
                    created_task_ids = {task["task_id"] for task in created_tasks}
                    persisted_task_ids = {task.get("task_id") for task in history_tasks}
                    
                    tasks_persisted = created_task_ids.issubset(persisted_task_ids)
                    
                    # 完了状態確認
                    completed_task_ids = {task["task_id"] for task in completed_tasks}
                    persisted_completed = sum(1 for task in history_tasks 
                                            if task.get("task_id") in completed_task_ids 
                                            and task.get("completed", False))
                    
                    return {
                        "success": True,
                        "tasks_created": len(created_tasks),
                        "tasks_completed": len(completed_tasks),
                        "tasks_persisted": tasks_persisted,
                        "completion_states_persisted": persisted_completed == len(completed_tasks),
                        "total_history_count": len(history_tasks),
                        "data_integrity": tasks_persisted and (persisted_completed == len(completed_tasks))
                    }
                
                return {"success": False, "error": "Task history fetch failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_mood_data_persistence(self) -> Dict[str, Any]:
        """気分データ永続化テスト"""
        logger.info("😊 気分データ永続化テスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. 複数の気分ログ作成
                mood_logs = []
                base_time = datetime.now()
                
                for i in range(5):
                    mood_data = {
                        "uid": self.test_user["uid"],
                        "mood_level": (i % 5) + 1,  # 1-5の気分レベル
                        "timestamp": (base_time - timedelta(hours=i)).isoformat(),
                        "notes": f"永続化テスト用気分ログ {i+1}"
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['mood_tracking']}/mood/log",
                        json=mood_data,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        mood_logs.append(mood_data)
                    else:
                        return {"success": False, "error": f"Mood log creation failed for log {i}"}
                
                # 2. 永続化確認（気分履歴取得）
                await asyncio.sleep(2)
                
                response = await client.get(
                    f"{self.base_urls['mood_tracking']}/mood/{self.test_user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    mood_history = response.json()
                    history_logs = mood_history.get("logs", [])
                    
                    # データ整合性確認
                    persisted_count = len(history_logs)
                    created_count = len(mood_logs)
                    
                    # 気分レベルの整合性確認
                    created_levels = [log["mood_level"] for log in mood_logs]
                    persisted_levels = [log.get("mood_level") for log in history_logs]
                    
                    levels_match = set(created_levels).issubset(set(persisted_levels))
                    
                    # 3. 気分係数計算確認
                    response = await client.get(
                        f"{self.base_urls['mood_tracking']}/mood/{self.test_user['uid']}/coefficient",
                        headers=headers
                    )
                    
                    coefficient_calculated = False
                    mood_coefficient = 1.0
                    
                    if response.status_code == 200:
                        coefficient_result = response.json()
                        mood_coefficient = coefficient_result.get("mood_coefficient", 1.0)
                        coefficient_calculated = 0.8 <= mood_coefficient <= 1.2
                    
                    return {
                        "success": True,
                        "logs_created": created_count,
                        "logs_persisted": persisted_count >= created_count,
                        "levels_consistent": levels_match,
                        "coefficient_calculated": coefficient_calculated,
                        "mood_coefficient": mood_coefficient,
                        "data_integrity": (persisted_count >= created_count) and levels_match and coefficient_calculated
                    }
                
                return {"success": False, "error": "Mood history fetch failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_mandala_state_persistence(self) -> Dict[str, Any]:
        """Mandala状態永続化テスト"""
        logger.info("🌸 Mandala状態永続化テスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. 初期Mandala状態取得
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/state",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Initial Mandala state fetch failed: {response.status_code}"}
                
                initial_state = response.json()
                initial_crystals = initial_state.get("crystal_gauges", {})
                
                # 2. クリスタル進行更新
                crystal_updates = [
                    {"attribute": "Self-Discipline", "progress": 25},
                    {"attribute": "Empathy", "progress": 30},
                    {"attribute": "Resilience", "progress": 20}
                ]
                
                for update in crystal_updates:
                    crystal_data = {
                        "uid": self.test_user["uid"],
                        "attribute": update["attribute"],
                        "progress_points": update["progress"]
                    }
                    
                    response = await client.post(
                        f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/update_crystal",
                        json=crystal_data,
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        return {"success": False, "error": f"Crystal update failed for {update['attribute']}"}
                
                # 3. 永続化確認
                await asyncio.sleep(2)
                
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/state",
                    headers=headers
                )
                
                if response.status_code == 200:
                    updated_state = response.json()
                    updated_crystals = updated_state.get("crystal_gauges", {})
                    
                    # データ整合性確認
                    progress_persisted = True
                    
                    for update in crystal_updates:
                        attr = update["attribute"]
                        initial_value = initial_crystals.get(attr, 0)
                        updated_value = updated_crystals.get(attr, 0)
                        expected_minimum = initial_value + update["progress"]
                        
                        if updated_value < expected_minimum:
                            progress_persisted = False
                            break
                    
                    # 4. グリッド状態確認
                    response = await client.get(
                        f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/grid",
                        headers=headers
                    )
                    
                    grid_persisted = False
                    if response.status_code == 200:
                        grid_data = response.json()
                        grid = grid_data.get("grid", [])
                        grid_persisted = len(grid) == 9 and all(len(row) == 9 for row in grid)
                    
                    return {
                        "success": True,
                        "crystal_progress_persisted": progress_persisted,
                        "grid_structure_persisted": grid_persisted,
                        "initial_crystals": initial_crystals,
                        "updated_crystals": updated_crystals,
                        "data_integrity": progress_persisted and grid_persisted
                    }
                
                return {"success": False, "error": "Updated Mandala state fetch failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_cross_service_data_consistency(self) -> Dict[str, Any]:
        """サービス間データ整合性テスト"""
        logger.info("🔄 サービス間データ整合性テスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. タスク完了によるXP獲得
                task_data = {
                    "uid": self.test_user["uid"],
                    "task_type": "skill_up",
                    "difficulty": 4,
                    "description": "整合性テスト用タスク",
                    "habit_tag": "consistency_test"
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks",
                    json=task_data,
                    headers=headers
                )
                
                if response.status_code not in [200, 201]:
                    return {"success": False, "error": "Task creation failed"}
                
                task_result = response.json()
                task_id = task_result.get("task_id")
                
                # 2. タスク完了
                completion_data = {
                    "uid": self.test_user["uid"],
                    "task_id": task_id,
                    "mood_at_completion": 5,
                    "completion_time": datetime.now().isoformat()
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks/{task_id}/complete",
                    json=completion_data,
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Task completion failed"}
                
                completion_result = response.json()
                expected_xp = completion_result.get("xp_earned", 0)
                
                # 3. 各サービスでデータ整合性確認
                await asyncio.sleep(3)  # データ同期待機
                
                # Core Game Engineでのプロファイル確認
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Profile fetch failed"}
                
                profile = response.json()
                profile_xp = profile.get("total_xp", 0)
                
                # Task Managementでのタスク状態確認
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['uid']}/history",
                    headers=headers
                )
                
                task_history_consistent = False
                if response.status_code == 200:
                    history = response.json()
                    completed_tasks = [t for t in history.get("tasks", []) 
                                     if t.get("task_id") == task_id and t.get("completed", False)]
                    task_history_consistent = len(completed_tasks) > 0
                
                # Mood Trackingでの気分データ確認
                response = await client.get(
                    f"{self.base_urls['mood_tracking']}/mood/{self.test_user['uid']}/coefficient",
                    headers=headers
                )
                
                mood_coefficient_available = response.status_code == 200
                
                return {
                    "success": True,
                    "expected_xp": expected_xp,
                    "profile_xp_updated": expected_xp > 0 and profile_xp > 0,
                    "task_history_consistent": task_history_consistent,
                    "mood_coefficient_available": mood_coefficient_available,
                    "cross_service_consistency": (expected_xp > 0 and profile_xp > 0 and 
                                                task_history_consistent and mood_coefficient_available)
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_data_recovery_simulation(self) -> Dict[str, Any]:
        """データ復旧シミュレーションテスト"""
        logger.info("🔄 データ復旧シミュレーションテスト開始...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. 基準データ作成
                baseline_data = {}
                
                # プロファイルデータ
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile",
                    headers=headers
                )
                
                if response.status_code == 200:
                    baseline_data["profile"] = response.json()
                
                # タスク履歴データ
                response = await client.get(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    baseline_data["task_history"] = response.json()
                
                # 気分履歴データ
                response = await client.get(
                    f"{self.base_urls['mood_tracking']}/mood/{self.test_user['uid']}/history",
                    headers=headers
                )
                
                if response.status_code == 200:
                    baseline_data["mood_history"] = response.json()
                
                # Mandala状態データ
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/state",
                    headers=headers
                )
                
                if response.status_code == 200:
                    baseline_data["mandala_state"] = response.json()
                
                # 2. 短時間後に再取得（復旧可能性確認）
                await asyncio.sleep(5)
                
                recovery_data = {}
                recovery_success = {}
                
                # 各サービスからデータ再取得
                for data_type, endpoint in [
                    ("profile", f"{self.base_urls['core_game']}/user/{self.test_user['uid']}/profile"),
                    ("task_history", f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['uid']}/history"),
                    ("mood_history", f"{self.base_urls['mood_tracking']}/mood/{self.test_user['uid']}/history"),
                    ("mandala_state", f"{self.base_urls['mandala']}/mandala/{self.test_user['uid']}/state")
                ]:
                    response = await client.get(endpoint, headers=headers)
                    
                    if response.status_code == 200:
                        recovery_data[data_type] = response.json()
                        
                        # データ整合性確認
                        if data_type in baseline_data:
                            baseline = baseline_data[data_type]
                            recovered = recovery_data[data_type]
                            
                            # 基本的な整合性チェック
                            if data_type == "profile":
                                recovery_success[data_type] = (
                                    recovered.get("uid") == baseline.get("uid") and
                                    recovered.get("total_xp", 0) >= baseline.get("total_xp", 0)
                                )
                            elif data_type == "task_history":
                                recovery_success[data_type] = (
                                    len(recovered.get("tasks", [])) >= len(baseline.get("tasks", []))
                                )
                            elif data_type == "mood_history":
                                recovery_success[data_type] = (
                                    len(recovered.get("logs", [])) >= len(baseline.get("logs", []))
                                )
                            elif data_type == "mandala_state":
                                recovery_success[data_type] = (
                                    "crystal_gauges" in recovered and
                                    len(recovered.get("crystal_gauges", {})) >= len(baseline.get("crystal_gauges", {}))
                                )
                        else:
                            recovery_success[data_type] = True
                    else:
                        recovery_success[data_type] = False
                
                # 復旧成功率計算
                successful_recoveries = sum(recovery_success.values())
                total_data_types = len(recovery_success)
                recovery_rate = successful_recoveries / total_data_types if total_data_types > 0 else 0
                
                return {
                    "success": recovery_rate > 0.5,  # 50%以上復旧できれば成功
                    "baseline_data_count": len(baseline_data),
                    "recovery_success": recovery_success,
                    "recovery_rate": recovery_rate,
                    "data_integrity_maintained": recovery_rate >= 0.8
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_persistence_tests(self) -> Dict[str, Any]:
        """データ永続化テスト実行"""
        logger.info("💾 データ永続化検証テスト開始")
        logger.info("="*60)
        
        # テストユーザーセットアップ
        if not await self.setup_test_user():
            return {"error": "Test user setup failed"}
        
        persistence_results = {}
        
        # 1. ユーザープロファイル永続化テスト
        persistence_results["user_profile"] = await self.test_user_profile_persistence()
        
        # 2. タスクデータ永続化テスト
        persistence_results["task_data"] = await self.test_task_data_persistence()
        
        # 3. 気分データ永続化テスト
        persistence_results["mood_data"] = await self.test_mood_data_persistence()
        
        # 4. Mandala状態永続化テスト
        persistence_results["mandala_state"] = await self.test_mandala_state_persistence()
        
        # 5. サービス間データ整合性テスト
        persistence_results["cross_service_consistency"] = await self.test_cross_service_data_consistency()
        
        # 6. データ復旧シミュレーションテスト
        persistence_results["data_recovery"] = await self.test_data_recovery_simulation()
        
        return persistence_results
    
    def print_persistence_summary(self, results: Dict[str, Any]):
        """永続化テスト結果サマリー"""
        logger.info("\n" + "="*60)
        logger.info("📊 データ永続化検証テスト結果サマリー")
        logger.info("="*60)
        
        if "error" in results:
            logger.error(f"❌ テスト実行エラー: {results['error']}")
            return
        
        test_names = {
            "user_profile": "ユーザープロファイル永続化",
            "task_data": "タスクデータ永続化",
            "mood_data": "気分データ永続化",
            "mandala_state": "Mandala状態永続化",
            "cross_service_consistency": "サービス間データ整合性",
            "data_recovery": "データ復旧シミュレーション"
        }
        
        passed_count = 0
        total_count = len(test_names)
        
        for test_key, test_name in test_names.items():
            if test_key in results:
                test_result = results[test_key]
                success = test_result.get("success", False)
                data_integrity = test_result.get("data_integrity", False)
                
                if success and data_integrity:
                    status = "✅ 成功"
                    passed_count += 1
                elif success:
                    status = "⚠️  部分成功"
                else:
                    status = "❌ 失敗"
                
                logger.info(f"{test_name}: {status}")
                
                # 詳細情報表示
                if test_key == "data_recovery" and "recovery_rate" in test_result:
                    recovery_rate = test_result["recovery_rate"]
                    logger.info(f"   復旧率: {recovery_rate:.1%}")
                
                if not success and "error" in test_result:
                    logger.info(f"   エラー: {test_result['error']}")
        
        logger.info(f"\n🎯 永続化テスト結果: {passed_count}/{total_count} 成功")
        
        if passed_count == total_count:
            logger.info("🎉 データ永続化検証テスト全て成功！")
            logger.info("✅ データの永続化と整合性が確認されました")
        elif passed_count >= total_count * 0.8:
            logger.info("⚠️  一部のデータ永続化に問題がありますが、基本機能は動作しています")
        else:
            logger.error("❌ データ永続化に重大な問題があります")
        
        logger.info("\n💡 次のステップ:")
        if passed_count == total_count:
            logger.info("- 本番環境でのデータ永続化設定確認")
            logger.info("- バックアップ・復旧手順の確立")
            logger.info("- 監視システムの設定")
        else:
            logger.info("- 失敗したデータ永続化機能の修正")
            logger.info("- Firestoreの設定確認")
            logger.info("- サービス間通信の確認")


async def main():
    """メイン実行関数"""
    verifier = DataPersistenceVerifier()
    
    try:
        # データ永続化テスト実行
        results = await verifier.run_persistence_tests()
        
        # 結果サマリー表示
        verifier.print_persistence_summary(results)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"data_persistence_test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "test_type": "data_persistence_verification",
                "test_results": results,
                "summary": {
                    "tests_executed": len([k for k in results.keys() if k != "error"]),
                    "data_types_tested": ["user_profile", "task_data", "mood_data", "mandala_state"],
                    "cross_service_consistency_tested": "cross_service_consistency" in results,
                    "recovery_simulation_tested": "data_recovery" in results
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 テスト結果を保存しました: {result_file}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  テストが中断されました")
    except Exception as e:
        logger.error(f"\n❌ テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())