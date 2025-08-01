#!/usr/bin/env python3
"""
簡単な統合テスト (タスク27.2の動作確認用)

認証システムの問題を修正して基本的な統合テストを実行
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleIntegrationTester:
    """簡単な統合テスター"""
    
    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8002",
            "core_game": "http://localhost:8001", 
            "task_mgmt": "http://localhost:8003",
            "mandala": "http://localhost:8004"
        }
        
        self.test_user = {
            "guardian_id": "test_guardian_001",
            "user_id": "test_user_001"
        }
        
        self.auth_token = None
        
    async def test_service_health(self) -> Dict[str, bool]:
        """サービスヘルスチェック"""
        logger.info("🔍 サービスヘルスチェック...")
        
        health_status = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, base_url in self.base_urls.items():
                try:
                    response = await client.get(f"{base_url}/health")
                    health_status[service_name] = response.status_code == 200
                    status = "✅" if health_status[service_name] else "❌"
                    logger.info(f"   {service_name}: {status}")
                except Exception as e:
                    health_status[service_name] = False
                    logger.info(f"   {service_name}: ❌ ({str(e)})")
        
        return health_status
    
    async def test_authentication_flow(self) -> Dict[str, Any]:
        """認証フローテスト"""
        logger.info("🔐 認証フローテスト...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Guardian権限付与
                grant_data = {
                    "user_id": self.test_user["user_id"],
                    "guardian_id": self.test_user["guardian_id"],
                    "permission_level": "task_edit",
                    "granted_by": "system_test"
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/grant",
                    json=grant_data
                )
                
                logger.info(f"   権限付与: {response.status_code}")
                
                # 2. Guardian認証
                login_data = {
                    "guardian_id": self.test_user["guardian_id"],
                    "user_id": self.test_user["user_id"],
                    "permission_level": "task_edit"
                }
                
                response = await client.post(
                    f"{self.base_urls['auth']}/auth/guardian/login",
                    json=login_data
                )
                
                logger.info(f"   認証: {response.status_code}")
                
                if response.status_code == 200:
                    auth_result = response.json()
                    self.auth_token = auth_result.get("access_token")
                    
                    return {
                        "success": True,
                        "token_received": bool(self.auth_token),
                        "guardian_id": auth_result.get("guardian_id"),
                        "permission_level": auth_result.get("permission_level")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Authentication failed: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_core_game_integration(self) -> Dict[str, Any]:
        """コアゲーム統合テスト"""
        logger.info("🎮 コアゲーム統合テスト...")
        
        if not self.auth_token:
            return {"success": False, "error": "No auth token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # XP追加テスト（実際に存在するエンドポイント）
                xp_data = {
                    "uid": self.test_user["user_id"],
                    "xp_amount": 50,
                    "source": "integration_test"
                }
                
                response = await client.post(
                    f"{self.base_urls['core_game']}/xp/add",
                    json=xp_data,
                    headers=headers
                )
                
                logger.info(f"   XP追加: {response.status_code}")
                
                if response.status_code == 200:
                    xp_result = response.json()
                    return {
                        "success": True,
                        "xp_added": True,
                        "user_id": xp_result.get("uid"),
                        "total_xp": xp_result.get("total_xp", 0),
                        "player_level": xp_result.get("player_level", 1),
                        "xp_gained": xp_result.get("xp_gained", 0)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"XP add failed: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_task_management_integration(self) -> Dict[str, Any]:
        """タスク管理統合テスト"""
        logger.info("📋 タスク管理統合テスト...")
        
        if not self.auth_token:
            return {"success": False, "error": "No auth token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # タスク作成テスト（正しいエンドポイント）
                task_data = {
                    "task_type": "routine",
                    "title": "統合テスト用タスク",
                    "description": "統合テスト用タスク",
                    "difficulty": 2,
                    "habit_tag": "integration_test"
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user['user_id']}/create",
                    json=task_data,
                    headers=headers
                )
                
                logger.info(f"   タスク作成: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    task_result = response.json()
                    return {
                        "success": True,
                        "task_created": True,
                        "task_id": task_result.get("task_id"),
                        "task_type": task_result.get("task_type")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Task creation failed: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_mandala_integration(self) -> Dict[str, Any]:
        """Mandala統合テスト"""
        logger.info("🌸 Mandala統合テスト...")
        
        if not self.auth_token:
            return {"success": False, "error": "No auth token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Mandalaグリッド取得テスト
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user['user_id']}/grid",
                    headers=headers
                )
                
                logger.info(f"   Mandalaグリッド取得: {response.status_code}")
                
                if response.status_code == 200:
                    mandala_data = response.json()
                    grid = mandala_data.get("grid", [])
                    
                    return {
                        "success": True,
                        "grid_retrieved": True,
                        "grid_size": f"{len(grid)}x{len(grid[0]) if grid else 0}",
                        "unlocked_count": mandala_data.get("unlocked_count", 0)
                    }
                else:
                    # エラーの詳細をログに出力
                    logger.error(f"   Mandalaエラー詳細: {response.text}")
                    return {
                        "success": False,
                        "error": f"Mandala grid fetch failed: {response.status_code}",
                        "response": response.text[:200]  # レスポンスを短縮
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_data_flow_integration(self) -> Dict[str, Any]:
        """データフロー統合テスト"""
        logger.info("🔄 データフロー統合テスト...")
        
        if not self.auth_token:
            return {"success": False, "error": "No auth token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. XP追加（初回）
                xp_data = {
                    "uid": self.test_user["user_id"],
                    "xp_amount": 30,
                    "source": "integration_test_1"
                }
                
                response = await client.post(
                    f"{self.base_urls['core_game']}/xp/add",
                    json=xp_data,
                    headers=headers
                )
                
                logger.info(f"   初回XP追加: {response.status_code}")
                
                if response.status_code != 200:
                    return {"success": False, "error": "Could not add initial XP"}
                
                initial_result = response.json()
                initial_xp = initial_result.get("total_xp", 0)
                
                # 2. 追加XP追加
                xp_data = {
                    "uid": self.test_user["user_id"],
                    "xp_amount": 50,
                    "source": "integration_test_2"
                }
                
                response = await client.post(
                    f"{self.base_urls['core_game']}/xp/add",
                    json=xp_data,
                    headers=headers
                )
                
                logger.info(f"   追加XP追加: {response.status_code}")
                
                if response.status_code == 200:
                    updated_result = response.json()
                    updated_xp = updated_result.get("total_xp", 0)
                    
                    return {
                        "success": True,
                        "data_flow_working": True,
                        "initial_xp": initial_xp,
                        "updated_xp": updated_xp,
                        "xp_increased": updated_xp > initial_xp,
                        "xp_difference": updated_xp - initial_xp
                    }
                else:
                    return {"success": False, "error": "Second XP addition failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_simple_integration_tests(self) -> Dict[str, Any]:
        """簡単な統合テスト実行"""
        logger.info("🎯 簡単な統合テスト開始")
        logger.info("="*60)
        
        results = {}
        
        # 1. サービスヘルスチェック
        results["service_health"] = await self.test_service_health()
        
        # 2. 認証フローテスト
        results["authentication"] = await self.test_authentication_flow()
        
        # 3. コアゲーム統合テスト
        results["core_game"] = await self.test_core_game_integration()
        
        # 4. タスク管理統合テスト
        results["task_management"] = await self.test_task_management_integration()
        
        # 5. Mandala統合テスト
        results["mandala"] = await self.test_mandala_integration()
        
        # 6. データフロー統合テスト
        results["data_flow"] = await self.test_data_flow_integration()
        
        return results
    
    def print_results_summary(self, results: Dict[str, Any]):
        """結果サマリー表示"""
        logger.info("\n" + "="*60)
        logger.info("📊 簡単な統合テスト結果サマリー")
        logger.info("="*60)
        
        test_names = {
            "service_health": "サービスヘルス",
            "authentication": "認証フロー",
            "core_game": "コアゲーム統合",
            "task_management": "タスク管理統合",
            "mandala": "Mandala統合",
            "data_flow": "データフロー統合"
        }
        
        passed_count = 0
        total_count = 0
        
        for test_key, test_name in test_names.items():
            if test_key in results:
                total_count += 1
                test_result = results[test_key]
                
                if test_key == "service_health":
                    # サービスヘルスは特別処理
                    healthy_services = sum(test_result.values())
                    total_services = len(test_result)
                    success = healthy_services >= 3  # 最低3つのサービスが必要
                    status = f"✅ {healthy_services}/{total_services}" if success else f"❌ {healthy_services}/{total_services}"
                    if success:
                        passed_count += 1
                else:
                    success = test_result.get("success", False)
                    status = "✅ 成功" if success else "❌ 失敗"
                    if success:
                        passed_count += 1
                    
                    # エラー詳細表示
                    if not success and "error" in test_result:
                        status += f" ({test_result['error']})"
                
                logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n🎯 テスト結果: {passed_count}/{total_count} 成功")
        
        success_rate = passed_count / total_count if total_count > 0 else 0
        
        if success_rate >= 0.8:
            logger.info("🎉 簡単な統合テスト成功！")
            logger.info("✅ 基本的な統合機能が正常に動作しています")
        elif success_rate >= 0.6:
            logger.info("⚠️  一部の統合機能に問題がありますが、基本動作は確認できました")
        else:
            logger.error("❌ 統合テストで重大な問題が発見されました")
        
        logger.info(f"📈 成功率: {success_rate:.1%}")


async def main():
    """メイン実行関数"""
    tester = SimpleIntegrationTester()
    
    try:
        # 簡単な統合テスト実行
        results = await tester.run_simple_integration_tests()
        
        # 結果サマリー表示
        tester.print_results_summary(results)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"simple_integration_test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "test_type": "simple_integration_test",
                "test_results": results,
                "summary": {
                    "total_tests": len([k for k in results.keys() if k != "service_health"]) + 1,
                    "passed_tests": sum(1 for k, v in results.items() 
                                      if (k == "service_health" and sum(v.values()) >= 3) or 
                                         (k != "service_health" and v.get("success", False))),
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 テスト結果を保存しました: {result_file}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  テストが中断されました")
    except Exception as e:
        logger.error(f"\n❌ テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())