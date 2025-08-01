"""
直接API呼び出しテスト

実際のAPIエンドポイントの動作を直接確認
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_direct_api_calls():
    """直接API呼び出しテスト"""
    print("=== 直接API呼び出しテスト ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    async with httpx.AsyncClient() as client:
        
        # 1. Core Game Engine - Health Check
        print("1. Core Game Engine - Health Check")
        try:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 2. Core Game Engine - XP Add
        print("2. Core Game Engine - XP Add")
        try:
            data = {
                "uid": "test_user",
                "xp_amount": 50,
                "source": "test"
            }
            response = await client.post("http://localhost:8001/xp/add", json=data, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 3. Auth Service - Health Check
        print("3. Auth Service - Health Check")
        try:
            response = await client.get("http://localhost:8002/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 4. Auth Service - Token
        print("4. Auth Service - Token")
        try:
            data = {
                "guardian_id": "test_guardian",
                "user_id": "test_user",
                "permission_level": "task_edit"
            }
            response = await client.post("http://localhost:8002/auth/token", json=data, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 5. Task Management - Health Check
        print("5. Task Management - Health Check")
        try:
            response = await client.get("http://localhost:8003/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 6. Task Management - Create Task
        print("6. Task Management - Create Task")
        try:
            data = {
                "task_type": "routine",
                "title": "テストタスク",
                "description": "API検証用",
                "difficulty": 2
            }
            response = await client.post("http://localhost:8003/tasks/test_user/create", json=data, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()
        
        # 7. Core Game Engine - Level Progress
        print("7. Core Game Engine - Level Progress")
        try:
            data = {
                "uid": "test_user"
            }
            response = await client.post("http://localhost:8001/level/progress", json=data, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
        print()

if __name__ == "__main__":
    asyncio.run(test_direct_api_calls())