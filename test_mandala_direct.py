#!/usr/bin/env python3
"""
Mandalaサービス直接テスト
"""

import asyncio
import httpx
import json

async def test_mandala_service():
    """Mandalaサービス直接テスト"""
    print("=== Mandalaサービス直接テスト ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # ヘルスチェック
            print("1. ヘルスチェック...")
            response = await client.get("http://localhost:8004/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                # グリッド取得テスト
                print("\n2. グリッド取得テスト...")
                response = await client.get("http://localhost:8004/mandala/test_user/grid")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                
                if response.status_code != 200:
                    print(f"   エラー詳細: {response.text}")
            
        except Exception as e:
            print(f"エラー: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mandala_service())