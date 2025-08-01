"""
API連携テスト

サービス間API呼び出しの動作確認
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime

# Windows環境でのUnicodeサポート
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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
                    results.append(f"✓ {service['name']}: OK")
                else:
                    results.append(f"✗ {service['name']}: HTTP {response.status_code}")
            except httpx.ConnectError:
                results.append(f"✗ {service['name']}: Connection failed (service not running)")
            except Exception as e:
                results.append(f"✗ {service['name']}: {str(e)}")
    
    return results

def test_shared_interfaces():
    """共有インターフェースのインポートテスト"""
    results = []
    
    try:
        from shared.interfaces.core_types import TaskType, TaskStatus, CrystalAttribute
        results.append("✓ Core Types: OK")
    except Exception as e:
        results.append(f"✗ Core Types: {str(e)}")
    
    try:
        from shared.interfaces.task_system import Task, TaskXPCalculator, TaskDifficulty
        results.append("✓ Task System: OK")
    except Exception as e:
        results.append(f"✗ Task System: {str(e)}")
    
    try:
        from shared.interfaces.level_system import LevelCalculator, PlayerLevelManager
        results.append("✓ Level System: OK")
    except Exception as e:
        results.append(f"✗ Level System: {str(e)}")
    
    try:
        from shared.interfaces.mood_system import MoodTrackingSystem, MoodLevel
        results.append("✓ Mood System: OK")
    except Exception as e:
        results.append(f"✗ Mood System: {str(e)}")
    
    try:
        from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid
        results.append("✓ Mandala System: OK")
    except Exception as e:
        results.append(f"✗ Mandala System: {str(e)}")
    
    try:
        from shared.interfaces.rbac_system import RBACSystem, PermissionLevel
        results.append("✓ RBAC System: OK")
    except Exception as e:
        results.append(f"✗ RBAC System: {str(e)}")
    
    return results

def test_basic_functionality():
    """基本機能のテスト"""
    results = []
    
    try:
        # Level System Test
        from shared.interfaces.level_system import LevelCalculator
        level = LevelCalculator.calculate_level(500)
        if level > 1:
            results.append("✓ Level Calculation: OK")
        else:
            results.append("✗ Level Calculation: Unexpected result")
    except Exception as e:
        results.append(f"✗ Level Calculation: {str(e)}")
    
    try:
        # Task System Test
        from shared.interfaces.task_system import TaskXPCalculator, TaskType, TaskDifficulty, ADHDSupportLevel
        xp = TaskXPCalculator.get_xp_preview(
            TaskType.ROUTINE, TaskDifficulty.MEDIUM, 3, ADHDSupportLevel.NONE
        )
        if xp > 0:
            results.append("✓ XP Calculation: OK")
        else:
            results.append("✗ XP Calculation: Unexpected result")
    except Exception as e:
        results.append(f"✗ XP Calculation: {str(e)}")
    
    try:
        # Mood System Test
        from shared.interfaces.mood_system import mood_tracking_system, MoodLevel
        entry = mood_tracking_system.log_mood("test_user", MoodLevel.NEUTRAL)
        if entry.calculated_coefficient == 1.0:
            results.append("✓ Mood Tracking: OK")
        else:
            results.append("✗ Mood Tracking: Unexpected coefficient")
    except Exception as e:
        results.append(f"✗ Mood Tracking: {str(e)}")
    
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
    success_count = len([r for r in all_results if r.startswith("✓")])
    total_count = len(all_results)
    
    print("=== テスト結果サマリー ===")
    print(f"成功: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("✓ すべてのテストが成功しました！")
    else:
        print("⚠ 一部のテストが失敗しました。詳細を確認してください。")

if __name__ == "__main__":
    asyncio.run(main())