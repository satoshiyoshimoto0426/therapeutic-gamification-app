"""
API連携テスト（シンプル版）

サービス間API呼び出しの動作確認
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime

# Add project root to path
sys.path.append('.')

async def test_service_health_checks():
    """サービスのヘルスチェック"""
    services = [
        {"name": "Core Game Engine", "url": "http://localhost:8001/health"},
        {"name": "Auth Service", "url": "http://localhost:8002/health"},
        {"name": "Task Management", "url": "http://localhost:8003/health"}
    ]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for service in services:
            try:
                response = await client.get(service["url"], timeout=5.0)
                if response.status_code == 200:
                    results.append(f"[OK] {service['name']}: OK")
                else:
                    results.append(f"[FAIL] {service['name']}: HTTP {response.status_code}")
            except httpx.ConnectError:
                results.append(f"[FAIL] {service['name']}: Connection failed (service not running)")
            except Exception as e:
                results.append(f"[FAIL] {service['name']}: {str(e)}")
    
    return results

def test_shared_interfaces():
    """共有インターフェースのインポートテスト"""
    results = []
    
    try:
        from shared.interfaces.core_types import TaskType, TaskStatus, CrystalAttribute
        results.append("[OK] Core Types: OK")
    except Exception as e:
        results.append(f"[FAIL] Core Types: {str(e)}")
    
    try:
        from shared.interfaces.task_system import Task, TaskXPCalculator, TaskDifficulty
        results.append("[OK] Task System: OK")
    except Exception as e:
        results.append(f"[FAIL] Task System: {str(e)}")
    
    try:
        from shared.interfaces.level_system import LevelCalculator, PlayerLevelManager
        results.append("[OK] Level System: OK")
    except Exception as e:
        results.append(f"[FAIL] Level System: {str(e)}")
    
    try:
        from shared.interfaces.mood_system import MoodTrackingSystem, MoodLevel
        results.append("[OK] Mood System: OK")
    except Exception as e:
        results.append(f"[FAIL] Mood System: {str(e)}")
    
    try:
        from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid
        results.append("[OK] Mandala System: OK")
    except Exception as e:
        results.append(f"[FAIL] Mandala System: {str(e)}")
    
    try:
        from shared.interfaces.rbac_system import RBACSystem, PermissionLevel
        results.append("[OK] RBAC System: OK")
    except Exception as e:
        results.append(f"[FAIL] RBAC System: {str(e)}")
    
    return results

def test_basic_functionality():
    """基本機能のテスト"""
    results = []
    
    try:
        # Level System Test
        from shared.interfaces.level_system import LevelCalculator
        level = LevelCalculator.calculate_level(500)
        if level > 1:
            results.append("[OK] Level Calculation: OK")
        else:
            results.append("[FAIL] Level Calculation: Unexpected result")
    except Exception as e:
        results.append(f"[FAIL] Level Calculation: {str(e)}")
    
    try:
        # Task System Test
        from shared.interfaces.task_system import TaskXPCalculator, TaskType, TaskDifficulty, ADHDSupportLevel
        xp = TaskXPCalculator.get_xp_preview(
            TaskType.ROUTINE, TaskDifficulty.MEDIUM, 3, ADHDSupportLevel.NONE
        )
        if xp > 0:
            results.append("[OK] XP Calculation: OK")
        else:
            results.append("[FAIL] XP Calculation: Unexpected result")
    except Exception as e:
        results.append(f"[FAIL] XP Calculation: {str(e)}")
    
    try:
        # Mood System Test
        from shared.interfaces.mood_system import mood_tracking_system, MoodLevel
        entry = mood_tracking_system.log_mood("test_user", MoodLevel.NEUTRAL)
        if entry.calculated_coefficient == 1.0:
            results.append("[OK] Mood Tracking: OK")
        else:
            results.append("[FAIL] Mood Tracking: Unexpected coefficient")
    except Exception as e:
        results.append(f"[FAIL] Mood Tracking: {str(e)}")
    
    return results

async def main():
    """メインテスト実行"""
    print("=== API連携とエンドポイント検証 ===")
    print(f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 共有インターフェーステスト
    print("1. 共有インターフェースのインポートテスト")
    interface_results = test_shared_interfaces()
    for result in interface_results:
        print(f"   {result}")
    print()
    
    # 基本機能テスト
    print("2. 基本機能テスト")
    functionality_results = test_basic_functionality()
    for result in functionality_results:
        print(f"   {result}")
    print()
    
    # サービスヘルスチェック
    print("3. サービスヘルスチェック")
    print("   注意: サービスが起動していない場合は接続エラーになります")
    health_results = await test_service_health_checks()
    for result in health_results:
        print(f"   {result}")
    print()
    
    # 結果サマリー
    all_results = interface_results + functionality_results + health_results
    success_count = len([r for r in all_results if r.startswith("[OK]")])
    total_count = len(all_results)
    
    print("=== テスト結果サマリー ===")
    print(f"成功: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("[OK] すべてのテストが成功しました！")
        return True
    else:
        print("[WARN] 一部のテストが失敗しました。詳細を確認してください。")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)