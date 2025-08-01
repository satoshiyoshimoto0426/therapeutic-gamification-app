"""
サービス間通信の詳細検証

タスク26.4の一部: サービス間API呼び出しの動作確認
"""

import asyncio
import httpx
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Windows環境でのUnicodeサポート
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class ServiceCommunicationValidator:
    """サービス間通信検証クラス"""
    
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
        
        self.test_user_id = "test_user_api_validation"
        self.test_guardian_id = "test_guardian_api_validation"
    
    async def run_communication_validation(self) -> Dict[str, Any]:
        """サービス間通信検証を実行"""
        print("=== サービス間通信検証 ===")
        print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "workflow_tests": [],
            "data_consistency_tests": [],
            "error_propagation_tests": [],
            "performance_tests": [],
            "integration_scenarios": []
        }
        
        # 1. 基本ワークフローテスト
        await self._test_basic_workflows(results)
        
        # 2. データ整合性テスト
        await self._test_data_consistency(results)
        
        # 3. エラー伝播テスト
        await self._test_error_propagation(results)
        
        # 4. パフォーマンステスト
        await self._test_performance(results)
        
        # 5. 統合シナリオテスト
        await self._test_integration_scenarios(results)
        
        return self._generate_communication_report(results)
    
    async def _test_basic_workflows(self, results: Dict[str, Any]):
        """基本ワークフローテスト"""
        print("1. 基本ワークフローテスト")
        
        workflows = [
            {
                "name": "ユーザー認証→タスク作成→XP追加",
                "steps": [
                    {
                        "service": "auth",
                        "action": "認証トークン取得",
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
                        "action": "タスク作成",
                        "endpoint": f"/tasks/{self.test_user_id}/create",
                        "method": "POST",
                        "data": {
                            "task_type": "routine",
                            "title": "API検証テストタスク",
                            "description": "サービス間通信テスト用",
                            "difficulty": 2
                        }
                    },
                    {
                        "service": "core_game",
                        "action": "XP追加",
                        "endpoint": "/xp/add",
                        "method": "POST",
                        "data": {
                            "uid": self.test_user_id,
                            "xp_amount": 50,
                            "source": "task_completion"
                        }
                    }
                ]
            },
            {
                "name": "レベル進行→共鳴イベント確認",
                "steps": [
                    {
                        "service": "core_game",
                        "action": "レベル進行確認",
                        "endpoint": "/level/progress",
                        "method": "POST",
                        "data": {
                            "uid": self.test_user_id
                        }
                    },
                    {
                        "service": "core_game",
                        "action": "共鳴イベント確認",
                        "endpoint": "/resonance/check",
                        "method": "POST",
                        "data": {
                            "uid": self.test_user_id
                        }
                    }
                ]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for workflow in workflows:
                print(f"   {workflow['name']}:")
                workflow_success = True
                workflow_data = {}
                
                for step in workflow["steps"]:
                    try:
                        service_config = self.services[step["service"]]
                        url = f"{service_config['base_url']}{step['endpoint']}"
                        
                        start_time = time.time()
                        
                        if step["method"] == "POST":
                            response = await client.post(url, json=step["data"], timeout=10.0)
                        else:
                            response = await client.get(url, timeout=10.0)
                        
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code in [200, 201]:
                            try:
                                response_data = response.json()
                                workflow_data[step["action"]] = response_data
                                print(f"     ✓ {step['action']}: 成功 ({response_time:.1f}ms)")
                            except json.JSONDecodeError:
                                print(f"     ⚠ {step['action']}: 成功 (非JSON) ({response_time:.1f}ms)")
                        elif response.status_code == 422:
                            print(f"     ⚠ {step['action']}: バリデーションエラー ({response_time:.1f}ms)")
                        else:
                            print(f"     ✗ {step['action']}: HTTP {response.status_code} ({response_time:.1f}ms)")
                            workflow_success = False
                            
                    except httpx.ConnectError:
                        print(f"     ✗ {step['action']}: 接続失敗")
                        workflow_success = False
                    except Exception as e:
                        print(f"     ✗ {step['action']}: {str(e)}")
                        workflow_success = False
                
                results["workflow_tests"].append({
                    "workflow": workflow["name"],
                    "success": workflow_success,
                    "data": workflow_data
                })
        print()
    
    async def _test_data_consistency(self, results: Dict[str, Any]):
        """データ整合性テスト"""
        print("2. データ整合性テスト")
        
        async with httpx.AsyncClient() as client:
            # XP追加後のレベル整合性確認
            try:
                # 初期状態確認
                initial_response = await client.post(
                    f"{self.services['core_game']['base_url']}/level/progress",
                    json={"uid": self.test_user_id},
                    timeout=5.0
                )
                
                if initial_response.status_code == 200:
                    initial_data = initial_response.json()
                    initial_xp = initial_data.get("data", {}).get("player", {}).get("total_xp", 0)
                    
                    # XP追加
                    xp_response = await client.post(
                        f"{self.services['core_game']['base_url']}/xp/add",
                        json={
                            "uid": self.test_user_id,
                            "xp_amount": 100,
                            "source": "consistency_test"
                        },
                        timeout=5.0
                    )
                    
                    if xp_response.status_code == 200:
                        # 更新後状態確認
                        final_response = await client.post(
                            f"{self.services['core_game']['base_url']}/level/progress",
                            json={"uid": self.test_user_id},
                            timeout=5.0
                        )
                        
                        if final_response.status_code == 200:
                            final_data = final_response.json()
                            final_xp = final_data.get("data", {}).get("player", {}).get("total_xp", 0)
                            
                            xp_difference = final_xp - initial_xp
                            consistency_check = xp_difference >= 100
                            
                            if consistency_check:
                                print("   ✓ XP追加後のデータ整合性: 正常")
                            else:
                                print(f"   ⚠ XP追加後のデータ整合性: 異常 (差分: {xp_difference})")
                            
                            results["data_consistency_tests"].append({
                                "test": "XP追加整合性",
                                "success": consistency_check,
                                "initial_xp": initial_xp,
                                "final_xp": final_xp,
                                "expected_difference": 100,
                                "actual_difference": xp_difference
                            })
                        else:
                            print("   ✗ 最終状態確認失敗")
                    else:
                        print("   ✗ XP追加失敗")
                else:
                    print("   ✗ 初期状態確認失敗")
                    
            except Exception as e:
                print(f"   ✗ データ整合性テストエラー: {str(e)}")
                results["data_consistency_tests"].append({
                    "test": "XP追加整合性",
                    "success": False,
                    "error": str(e)
                })
        print()
    
    async def _test_error_propagation(self, results: Dict[str, Any]):
        """エラー伝播テスト"""
        print("3. エラー伝播テスト")
        
        error_scenarios = [
            {
                "name": "無効なユーザーIDでのXP追加",
                "service": "core_game",
                "endpoint": "/xp/add",
                "data": {
                    "uid": "",  # 無効なUID
                    "xp_amount": 50,
                    "source": "test"
                },
                "expected_status": [400, 422]
            },
            {
                "name": "無効な権限レベルでの認証",
                "service": "auth",
                "endpoint": "/auth/token",
                "data": {
                    "guardian_id": "test",
                    "user_id": "test",
                    "permission_level": "invalid_level"
                },
                "expected_status": [400, 422]
            },
            {
                "name": "存在しないタスクの更新",
                "service": "task_mgmt",
                "endpoint": f"/tasks/{self.test_user_id}/nonexistent_task",
                "method": "PUT",
                "data": {
                    "title": "Updated Task"
                },
                "expected_status": [404]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for scenario in error_scenarios:
                try:
                    service_config = self.services[scenario["service"]]
                    url = f"{service_config['base_url']}{scenario['endpoint']}"
                    method = scenario.get("method", "POST")
                    
                    if method == "POST":
                        response = await client.post(url, json=scenario["data"], timeout=5.0)
                    elif method == "PUT":
                        response = await client.put(url, json=scenario["data"], timeout=5.0)
                    else:
                        response = await client.get(url, timeout=5.0)
                    
                    expected_statuses = scenario["expected_status"]
                    error_handled_correctly = response.status_code in expected_statuses
                    
                    if error_handled_correctly:
                        print(f"   ✓ {scenario['name']}: 適切なエラーハンドリング ({response.status_code})")
                        
                        # エラーレスポンス形式確認
                        try:
                            error_data = response.json()
                            has_error_detail = "detail" in error_data or "message" in error_data
                            if has_error_detail:
                                print(f"     エラー詳細: 適切な形式")
                            else:
                                print(f"     エラー詳細: 詳細情報不足")
                        except:
                            print(f"     エラー詳細: 非JSON形式")
                    else:
                        print(f"   ⚠ {scenario['name']}: 予期しないステータス ({response.status_code})")
                    
                    results["error_propagation_tests"].append({
                        "scenario": scenario["name"],
                        "service": scenario["service"],
                        "expected_status": expected_statuses,
                        "actual_status": response.status_code,
                        "error_handled_correctly": error_handled_correctly
                    })
                    
                except Exception as e:
                    print(f"   ✗ {scenario['name']}: {str(e)}")
                    results["error_propagation_tests"].append({
                        "scenario": scenario["name"],
                        "service": scenario["service"],
                        "error": str(e),
                        "error_handled_correctly": False
                    })
        print()
    
    async def _test_performance(self, results: Dict[str, Any]):
        """パフォーマンステスト"""
        print("4. パフォーマンステスト")
        
        performance_tests = [
            {
                "name": "ヘルスチェック応答時間",
                "endpoint": "/health",
                "method": "GET",
                "target_ms": 100
            },
            {
                "name": "XP追加応答時間",
                "endpoint": "/xp/add",
                "method": "POST",
                "data": {
                    "uid": self.test_user_id,
                    "xp_amount": 25,
                    "source": "performance_test"
                },
                "target_ms": 500
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for service_key, service_config in self.services.items():
                print(f"   {service_config['name']}:")
                
                for test in performance_tests:
                    # XP追加テストはCore Game Engineのみ
                    if test["name"] == "XP追加応答時間" and service_key != "core_game":
                        continue
                    
                    try:
                        url = f"{service_config['base_url']}{test['endpoint']}"
                        response_times = []
                        
                        # 5回測定して平均を取る
                        for _ in range(5):
                            start_time = time.time()
                            
                            if test["method"] == "POST":
                                response = await client.post(
                                    url, 
                                    json=test.get("data", {}), 
                                    timeout=10.0
                                )
                            else:
                                response = await client.get(url, timeout=10.0)
                            
                            response_time = (time.time() - start_time) * 1000
                            
                            if response.status_code in [200, 201]:
                                response_times.append(response_time)
                        
                        if response_times:
                            avg_response_time = sum(response_times) / len(response_times)
                            performance_ok = avg_response_time <= test["target_ms"]
                            
                            if performance_ok:
                                print(f"     ✓ {test['name']}: {avg_response_time:.1f}ms (目標: {test['target_ms']}ms)")
                            else:
                                print(f"     ⚠ {test['name']}: {avg_response_time:.1f}ms (目標: {test['target_ms']}ms)")
                            
                            results["performance_tests"].append({
                                "service": service_config["name"],
                                "test": test["name"],
                                "avg_response_time_ms": avg_response_time,
                                "target_ms": test["target_ms"],
                                "performance_ok": performance_ok,
                                "measurements": response_times
                            })
                        else:
                            print(f"     ✗ {test['name']}: 測定失敗")
                            
                    except Exception as e:
                        print(f"     ✗ {test['name']}: {str(e)}")
                        results["performance_tests"].append({
                            "service": service_config["name"],
                            "test": test["name"],
                            "error": str(e),
                            "performance_ok": False
                        })
        print()
    
    async def _test_integration_scenarios(self, results: Dict[str, Any]):
        """統合シナリオテスト"""
        print("5. 統合シナリオテスト")
        
        # 複雑なワークフローをテスト
        scenario = {
            "name": "完全なタスク完了フロー",
            "description": "タスク作成→開始→完了→XP獲得→レベル確認の一連の流れ"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"   {scenario['name']}:")
                scenario_success = True
                scenario_data = {}
                
                # 1. タスク作成
                task_response = await client.post(
                    f"{self.services['task_mgmt']['base_url']}/tasks/{self.test_user_id}/create",
                    json={
                        "task_type": "one_shot",
                        "title": "統合テストタスク",
                        "description": "完全フロー検証用",
                        "difficulty": 3
                    },
                    timeout=10.0
                )
                
                if task_response.status_code in [200, 201]:
                    task_data = task_response.json()
                    task_id = task_data.get("task_id")
                    scenario_data["task_created"] = task_data
                    print("     ✓ タスク作成: 成功")
                    
                    if task_id:
                        # 2. タスク開始
                        start_response = await client.post(
                            f"{self.services['task_mgmt']['base_url']}/tasks/{self.test_user_id}/{task_id}/start",
                            json={"pomodoro_session": False},
                            timeout=10.0
                        )
                        
                        if start_response.status_code == 200:
                            print("     ✓ タスク開始: 成功")
                            
                            # 3. タスク完了
                            complete_response = await client.post(
                                f"{self.services['task_mgmt']['base_url']}/tasks/{self.test_user_id}/{task_id}/complete",
                                json={
                                    "mood_score": 4,
                                    "actual_duration": 30,
                                    "notes": "統合テスト完了",
                                    "pomodoro_sessions_completed": 1
                                },
                                timeout=10.0
                            )
                            
                            if complete_response.status_code == 200:
                                complete_data = complete_response.json()
                                xp_earned = complete_data.get("xp_earned", 0)
                                scenario_data["task_completed"] = complete_data
                                print(f"     ✓ タスク完了: 成功 (XP: {xp_earned})")
                                
                                # 4. レベル進行確認
                                level_response = await client.post(
                                    f"{self.services['core_game']['base_url']}/level/progress",
                                    json={"uid": self.test_user_id},
                                    timeout=10.0
                                )
                                
                                if level_response.status_code == 200:
                                    level_data = level_response.json()
                                    scenario_data["level_progress"] = level_data
                                    print("     ✓ レベル進行確認: 成功")
                                else:
                                    print("     ✗ レベル進行確認: 失敗")
                                    scenario_success = False
                            else:
                                print("     ✗ タスク完了: 失敗")
                                scenario_success = False
                        else:
                            print("     ✗ タスク開始: 失敗")
                            scenario_success = False
                    else:
                        print("     ✗ タスクID取得失敗")
                        scenario_success = False
                else:
                    print("     ✗ タスク作成: 失敗")
                    scenario_success = False
                
                results["integration_scenarios"].append({
                    "scenario": scenario["name"],
                    "success": scenario_success,
                    "data": scenario_data
                })
                
            except Exception as e:
                print(f"     ✗ 統合シナリオエラー: {str(e)}")
                results["integration_scenarios"].append({
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e)
                })
        print()
    
    def _generate_communication_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """サービス間通信レポートを生成"""
        print("=== サービス間通信検証結果サマリー ===")
        
        categories = {
            "ワークフロー": results["workflow_tests"],
            "データ整合性": results["data_consistency_tests"],
            "エラー伝播": results["error_propagation_tests"],
            "パフォーマンス": results["performance_tests"],
            "統合シナリオ": results["integration_scenarios"]
        }
        
        overall_success = True
        category_summary = {}
        
        for category_name, tests in categories.items():
            if not tests:
                continue
            
            if category_name == "パフォーマンス":
                success_count = len([t for t in tests if t.get("performance_ok", False)])
            elif category_name == "エラー伝播":
                success_count = len([t for t in tests if t.get("error_handled_correctly", False)])
            else:
                success_count = len([t for t in tests if t.get("success", False)])
            
            total_count = len(tests)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            category_summary[category_name] = {
                "success_count": success_count,
                "total_count": total_count,
                "success_rate": success_rate
            }
            
            if success_rate < 80:
                overall_success = False
            
            print(f"{category_name}: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        print()
        if overall_success:
            print("✓ サービス間通信は正常に動作しています")
        else:
            print("⚠ サービス間通信に改善が必要な箇所があります")
        
        return {
            "overall_success": overall_success,
            "category_summary": category_summary,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """メイン実行関数"""
    validator = ServiceCommunicationValidator()
    report = await validator.run_communication_validation()
    
    # レポートをファイルに保存
    with open("service_communication_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nサービス間通信レポートが 'service_communication_report.json' に保存されました。")
    
    return report["overall_success"]

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)