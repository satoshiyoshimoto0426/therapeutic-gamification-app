#!/usr/bin/env python3
"""
認証システムデバッグテスト
"""

import asyncio
import httpx
import json
from typing import Dict, Any

async def test_auth_endpoints():
    """認証エンドポイントのデバッグテスト"""
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. ヘルスチェック
        print("1. ヘルスチェック:")
        response = await client.get("http://localhost:8002/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # 2. システムロール確認
        print("\n2. システムロール確認:")
        response = await client.get("http://localhost:8002/auth/system/roles")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # 3. Guardian権限付与テスト（正しい形式）
        print("\n3. Guardian権限付与テスト:")
        grant_data = {
            "user_id": "test_user_001",
            "guardian_id": "test_guardian_001", 
            "permission_level": "task_edit",  # アンダースコア形式
            "granted_by": "system_test"
        }
        
        response = await client.post(
            "http://localhost:8002/auth/guardian/grant",
            json=grant_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # 4. Guardian認証テスト
        print("\n4. Guardian認証テスト:")
        login_data = {
            "guardian_id": "test_guardian_001",
            "user_id": "test_user_001",
            "permission_level": "task_edit"
        }
        
        response = await client.post(
            "http://localhost:8002/auth/guardian/login",
            json=login_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # 5. 異なる権限レベルでのテスト
        print("\n5. 異なる権限レベルでのテスト:")
        for permission in ["view_only", "task_edit", "chat_send"]:
            grant_data["permission_level"] = permission
            login_data["permission_level"] = permission
            
            print(f"\n   権限レベル: {permission}")
            
            # 権限付与
            response = await client.post(
                "http://localhost:8002/auth/guardian/grant",
                json=grant_data
            )
            print(f"   付与 Status: {response.status_code}")
            
            # 認証
            response = await client.post(
                "http://localhost:8002/auth/guardian/login", 
                json=login_data
            )
            print(f"   認証 Status: {response.status_code}")
            if response.status_code == 200:
                auth_result = response.json()
                print(f"   Token: {auth_result.get('access_token', 'None')[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_auth_endpoints())