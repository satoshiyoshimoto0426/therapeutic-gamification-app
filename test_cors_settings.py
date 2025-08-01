"""
CORS設定テスト

Cross-Origin Resource Sharing設定の確認
"""

import asyncio
import httpx
from datetime import datetime

async def test_cors_headers():
    """CORS ヘッダーのテスト"""
    services = [
        {"name": "Core Game Engine", "url": "http://localhost:8001/health"},
        {"name": "Auth Service", "url": "http://localhost:8002/health"},
        {"name": "Task Management", "url": "http://localhost:8003/health"}
    ]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for service in services:
            try:
                # OPTIONS リクエストでCORSプリフライトをテスト
                response = await client.options(
                    service["url"],
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": "GET",
                        "Access-Control-Request-Headers": "Content-Type"
                    },
                    timeout=5.0
                )
                
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                    "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                }
                
                if cors_headers["Access-Control-Allow-Origin"]:
                    results.append(f"✓ {service['name']}: CORS enabled")
                    results.append(f"   Origin: {cors_headers['Access-Control-Allow-Origin']}")
                    results.append(f"   Methods: {cors_headers['Access-Control-Allow-Methods']}")
                    results.append(f"   Headers: {cors_headers['Access-Control-Allow-Headers']}")
                else:
                    results.append(f"⚠ {service['name']}: CORS headers not found")
                
            except httpx.ConnectError:
                results.append(f"✗ {service['name']}: Connection failed (service not running)")
            except Exception as e:
                results.append(f"✗ {service['name']}: {str(e)}")
    
    return results

async def test_api_endpoints():
    """API エンドポイントのテスト"""
    endpoints = [
        {"service": "Core Game Engine", "url": "http://localhost:8001/health", "method": "GET"},
        {"service": "Auth Service", "url": "http://localhost:8002/health", "method": "GET"},
        {"service": "Task Management", "url": "http://localhost:8003/health", "method": "GET"}
    ]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = await client.get(endpoint["url"], timeout=5.0)
                elif endpoint["method"] == "POST":
                    response = await client.post(endpoint["url"], json={}, timeout=5.0)
                
                if response.status_code == 200:
                    results.append(f"✓ {endpoint['service']}: {endpoint['method']} {endpoint['url']} - OK")
                    
                    # レスポンス形式チェック
                    try:
                        data = response.json()
                        if "status" in data:
                            results.append(f"   Response format: Valid JSON with status")
                        else:
                            results.append(f"   Response format: JSON (no status field)")
                    except:
                        results.append(f"   Response format: Non-JSON")
                else:
                    results.append(f"⚠ {endpoint['service']}: HTTP {response.status_code}")
                    
            except httpx.ConnectError:
                results.append(f"✗ {endpoint['service']}: Connection failed")
            except Exception as e:
                results.append(f"✗ {endpoint['service']}: {str(e)}")
    
    return results

async def main():
    """メインテスト実行"""
    print("=== CORS設定とエンドポイント検証 ===")
    print(f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # API エンドポイントテスト
    print("1. API エンドポイントテスト")
    endpoint_results = await test_api_endpoints()
    for result in endpoint_results:
        print(f"   {result}")
    print()
    
    # CORS ヘッダーテスト
    print("2. CORS ヘッダーテスト")
    cors_results = await test_cors_headers()
    for result in cors_results:
        print(f"   {result}")
    print()
    
    # 結果サマリー
    all_results = endpoint_results + cors_results
    success_count = len([r for r in all_results if r.startswith("✓")])
    warning_count = len([r for r in all_results if r.startswith("⚠")])
    error_count = len([r for r in all_results if r.startswith("✗")])
    
    print("=== テスト結果サマリー ===")
    print(f"成功: {success_count}")
    print(f"警告: {warning_count}")
    print(f"エラー: {error_count}")
    
    if error_count == 0:
        print("✓ 重大なエラーはありませんでした")
    else:
        print("⚠ エラーが発生しました。サービスが起動しているか確認してください。")

if __name__ == "__main__":
    asyncio.run(main())