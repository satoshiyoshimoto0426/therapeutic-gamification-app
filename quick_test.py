#!/usr/bin/env python3
"""
クイックMVPテスト

最小限の機能テストを実行
"""

import asyncio
import httpx
import json
from datetime import datetime

class QuickMVPTest:
    """クイックMVPテスト"""
    
    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8002",
            "core_game": "http://localhost:8001", 
            "task_mgmt": "http://localhost:8003",
            "mandala": "http://localhost:8004"
        }
        self.test_user_uid = "quick_test_user_001"
    
    async def test_service_health(self) -> dict:
        """サービスヘルスチェック"""
        print("🔍 サービスヘルスチェック...")
        
        results = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, base_url in self.base_urls.items():
                try:
                    # ヘルスエンドポイントまたはルートエンドポイントをチェック
                    endpoints_to_try = ["/health", "/", "/docs"]
                    
                    service_healthy = False
                    for endpoint in endpoints_to_try:
                        try:
                            response = await client.get(f"{base_url}{endpoint}")
                            if response.status_code in [200, 404]:
                                service_healthy = True
                                break
                        except:
                            continue
                    
                    results[service_name] = service_healthy
                    status = "✅ 正常" if service_healthy else "❌ 異常"
                    print(f"   {service_name}: {status}")
                    
                except Exception as e:
                    results[service_name] = False
                    print(f"   {service_name}: ❌ エラー - {str(e)}")
        
        healthy_count = sum(results.values())
        print(f"\n📊 ヘルスチェック結果: {healthy_count}/{len(results)} サービス正常")
        
        return results
    
    async def test_core_game_basic(self) -> bool:
        """コアゲーム基本機能テスト"""
        print("\n⚡ コアゲーム基本機能テスト...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. ユーザープロファイル取得テスト
                print("   1. ユーザープロファイル取得テスト...")
                
                response = await client.get(
                    f"{self.base_urls['core_game']}/user/{self.test_user_uid}/profile"
                )
                
                if response.status_code in [200, 404]:  # 404は新規ユーザーの場合
                    print("      ✅ プロファイル取得成功")
                    
                    # 2. XP追加テスト
                    print("   2. XP追加テスト...")
                    
                    response = await client.post(
                        f"{self.base_urls['core_game']}/xp/add",
                        json={"uid": self.test_user_uid, "xp_amount": 100, "source": "quick_test"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"      ✅ XP追加成功 (総XP: {result.get('total_xp', 0)})")
                        return True
                    else:
                        print(f"      ❌ XP追加失敗: {response.status_code}")
                        return False
                else:
                    print(f"      ❌ プロファイル取得失敗: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ コアゲームテストエラー: {str(e)}")
            return False
    
    async def test_task_mgmt_basic(self) -> bool:
        """タスク管理基本機能テスト"""
        print("\n📋 タスク管理基本機能テスト...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. タスク作成テスト
                print("   1. タスク作成テスト...")
                
                task_data = {
                    "task_type": "routine",
                    "title": "クイックテスト用タスク",
                    "description": "MVP機能テスト用のサンプルタスク",
                    "difficulty": 3,
                    "habit_tag": "quick_test"
                }
                
                response = await client.post(
                    f"{self.base_urls['task_mgmt']}/tasks/{self.test_user_uid}/create",
                    json=task_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    task_id = result.get("task_id")
                    print(f"      ✅ タスク作成成功 (ID: {task_id})")
                    
                    # 2. タスク一覧取得テスト
                    print("   2. タスク一覧取得テスト...")
                    
                    response = await client.get(
                        f"{self.base_urls['task_mgmt']}/tasks/{self.test_user_uid}"
                    )
                    
                    if response.status_code == 200:
                        tasks = response.json()
                        print(f"      ✅ タスク一覧取得成功 (件数: {len(tasks)})")
                        return True
                    else:
                        print(f"      ❌ タスク一覧取得失敗: {response.status_code}")
                        return False
                else:
                    print(f"      ❌ タスク作成失敗: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ タスク管理テストエラー: {str(e)}")
            return False
    
    async def test_mandala_basic(self) -> bool:
        """Mandala基本機能テスト"""
        print("\n🌸 Mandala基本機能テスト...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Mandalaグリッド取得テスト
                print("   1. Mandalaグリッド取得テスト...")
                
                response = await client.get(
                    f"{self.base_urls['mandala']}/mandala/{self.test_user_uid}/grid?chapter_type=self_discipline"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    grid = result.get("grid", [])
                    
                    if len(grid) == 9 and all(len(row) == 9 for row in grid):
                        print("      ✅ 9x9グリッド取得成功")
                        return True
                    else:
                        print("      ❌ グリッド構造が不正")
                        return False
                else:
                    print(f"      ❌ グリッド取得失敗: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"      エラー詳細: {error_detail}")
                    except:
                        print(f"      レスポンステキスト: {response.text[:200]}")
                    return False
                    
        except Exception as e:
            print(f"❌ Mandalaテストエラー: {str(e)}")
            return False
    
    async def run_quick_test(self) -> dict:
        """クイックテスト実行"""
        print("🎯 クイックMVPテスト開始")
        print("="*50)
        
        # 1. サービスヘルスチェック
        health_results = await self.test_service_health()
        
        # 必須サービスが利用できない場合は終了
        required_services = ["core_game", "task_mgmt", "mandala"]
        missing_services = [svc for svc in required_services if not health_results.get(svc, False)]
        
        if missing_services:
            print(f"\n❌ 必須サービスが利用できません: {', '.join(missing_services)}")
            return {"service_health": False}
        
        # 2. 各機能テスト実行
        test_results = {"service_health": True}
        
        # コアゲームテスト
        test_results["core_game"] = await self.test_core_game_basic()
        
        # タスク管理テスト
        test_results["task_mgmt"] = await self.test_task_mgmt_basic()
        
        # Mandalaテスト
        test_results["mandala"] = await self.test_mandala_basic()
        
        return test_results
    
    def print_test_summary(self, results: dict):
        """テスト結果サマリー表示"""
        print("\n" + "="*50)
        print("📊 クイックMVPテスト結果")
        print("="*50)
        
        test_names = {
            "core_game": "コアゲーム基本機能",
            "task_mgmt": "タスク管理基本機能",
            "mandala": "Mandala基本機能"
        }
        
        passed_count = 0
        total_count = len([k for k in results.keys() if k != "service_health"])
        
        for test_key, test_name in test_names.items():
            if test_key in results:
                status = "✅ 成功" if results[test_key] else "❌ 失敗"
                print(f"{test_name}: {status}")
                if results[test_key]:
                    passed_count += 1
            else:
                print(f"{test_name}: ⚠️  未実行")
        
        print(f"\n🎯 テスト結果: {passed_count}/{total_count} 成功")
        
        if passed_count == total_count:
            print("🎉 クイックMVPテスト全て成功！")
            print("✅ 基本機能が正常に動作しています")
        elif passed_count > 0:
            print("⚠️  一部機能に問題があります")
        else:
            print("❌ クイックMVPテストが失敗しました")
        
        return passed_count == total_count

async def main():
    """メイン実行関数"""
    tester = QuickMVPTest()
    
    try:
        # クイックテスト実行
        results = await tester.run_quick_test()
        
        # 結果サマリー表示
        success = tester.print_test_summary(results)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"quick_test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "test_results": results,
                "success": success
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 テスト結果を保存しました: {result_file}")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  テストが中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))