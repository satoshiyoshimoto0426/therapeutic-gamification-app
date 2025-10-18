#!/usr/bin/env python3
"""
APIエンドポイント自動検出スクリプト

各サービスのAPIエンドポイントを自動的に検出してレポートを生成します。
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any
from datetime import datetime


class APIEndpointDiscoverer:
    """APIエンドポイント検出クラス"""
    
    def __init__(self):
        self.base_urls = {
            "auth": "http://localhost:8002",
            "core_game": "http://localhost:8001",
            "task_mgmt": "http://localhost:8003",
            "mandala": "http://localhost:8004"
        }
        
        # ソースコードから特定したエンドポイント
        self.known_endpoints = {
            "core_game": [
                {"method": "GET", "path": "/health", "description": "ヘルスチェック"},
                {"method": "POST", "path": "/xp/add", "description": "XP追加"},
                {"method": "POST", "path": "/level/progress", "description": "レベル進捗取得"},
                {"method": "POST", "path": "/resonance/check", "description": "共鳴チェック"},
                {"method": "POST", "path": "/resonance/trigger", "description": "共鳴イベント発動"},
                {"method": "POST", "path": "/system/status", "description": "システム状態取得"},
                {"method": "POST", "path": "/xp/calculate", "description": "XP計算プレビュー"},
            ],
            "task_mgmt": [
                {"method": "GET", "path": "/health", "description": "ヘルスチェック"},
                {"method": "POST", "path": "/tasks/{uid}/create", "description": "タスク作成"},
                {"method": "GET", "path": "/tasks/{uid}", "description": "タスク一覧取得"},
                {"method": "GET", "path": "/tasks/{uid}/{task_id}", "description": "タスク詳細取得"},
                {"method": "PUT", "path": "/tasks/{uid}/{task_id}", "description": "タスク更新"},
                {"method": "POST", "path": "/tasks/{uid}/{task_id}/start", "description": "タスク開始"},
                {"method": "POST", "path": "/tasks/{uid}/{task_id}/complete", "description": "タスク完了"},
                {"method": "DELETE", "path": "/tasks/{uid}/{task_id}", "description": "タスク削除"},
                {"method": "GET", "path": "/tasks/{uid}/statistics", "description": "統計取得"},
                {"method": "POST", "path": "/tasks/xp-preview", "description": "XPプレビュー"},
            ],
            "mandala": [
                {"method": "GET", "path": "/health", "description": "ヘルスチェック"},
                {"method": "GET", "path": "/mandala/{uid}/grid", "description": "グリッド取得"},
                {"method": "POST", "path": "/mandala/{uid}/unlock", "description": "セルアンロック"},
                {"method": "POST", "path": "/mandala/{uid}/complete", "description": "セル完了"},
                {"method": "GET", "path": "/mandala/{uid}/status", "description": "ステータス取得"},
                {"method": "GET", "path": "/mandala/{uid}/reminder", "description": "リマインダー取得"},
            ],
            "auth": [
                {"method": "GET", "path": "/health", "description": "ヘルスチェック"},
                {"method": "POST", "path": "/auth/token", "description": "トークン作成"},
                {"method": "POST", "path": "/auth/guardian/login", "description": "Guardian ログイン"},
                {"method": "POST", "path": "/auth/guardian/grant", "description": "アクセス許可"},
            ]
        }
    
    async def test_endpoint(self, service_name: str, base_url: str, endpoint: Dict) -> Dict:
        """エンドポイントをテスト"""
        method = endpoint["method"]
        path = endpoint["path"]
        
        # パスパラメータを置換
        test_path = path.replace("{uid}", "test_user").replace("{task_id}", "test_task")
        
        full_url = f"{base_url}{test_path}"
        
        result = {
            "service": service_name,
            "method": method,
            "path": path,
            "description": endpoint["description"],
            "status": "unknown",
            "status_code": None,
            "error": None
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                if method == "GET":
                    response = await client.get(full_url)
                elif method == "POST":
                    # 最小限のテストデータ
                    test_data = {"uid": "test_user"}
                    response = await client.post(full_url, json=test_data)
                elif method == "PUT":
                    test_data = {"uid": "test_user"}
                    response = await client.put(full_url, json=test_data)
                elif method == "DELETE":
                    response = await client.delete(full_url)
                else:
                    result["status"] = "unsupported_method"
                    return result
                
                result["status_code"] = response.status_code
                
                # ステータスコードに基づいて判定
                if response.status_code == 200:
                    result["status"] = "working"
                elif response.status_code in [400, 422]:
                    result["status"] = "needs_valid_data"
                elif response.status_code == 404:
                    result["status"] = "not_found"
                elif response.status_code == 405:
                    result["status"] = "method_not_allowed"
                elif response.status_code == 500:
                    result["status"] = "server_error"
                else:
                    result["status"] = "other"
                    
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    async def discover_all_endpoints(self) -> Dict[str, List[Dict]]:
        """全エンドポイントを検出"""
        print("🔍 APIエンドポイント検出開始...\n")
        
        all_results = {}
        
        for service_name, base_url in self.base_urls.items():
            print(f"📡 {service_name} サービスをスキャン中...")
            
            endpoints = self.known_endpoints.get(service_name, [])
            results = []
            
            for endpoint in endpoints:
                result = await self.test_endpoint(service_name, base_url, endpoint)
                results.append(result)
                
                # ステータス表示
                status_icon = {
                    "working": "✅",
                    "needs_valid_data": "⚠️",
                    "not_found": "❌",
                    "method_not_allowed": "❌",
                    "server_error": "🔥",
                    "error": "❌",
                    "other": "❓"
                }.get(result["status"], "❓")
                
                print(f"  {status_icon} {result['method']:6} {result['path']:40} [{result['status_code']}]")
            
            all_results[service_name] = results
            print()
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> str:
        """レポート生成"""
        report = []
        report.append("# APIエンドポイント検出レポート\n")
        report.append(f"**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        report.append("---\n")
        
        for service_name, endpoints in results.items():
            report.append(f"\n## {service_name.upper()} サービス\n")
            report.append(f"**ベースURL**: {self.base_urls[service_name]}\n")
            
            # ステータス別に分類
            working = [e for e in endpoints if e["status"] == "working"]
            needs_data = [e for e in endpoints if e["status"] == "needs_valid_data"]
            not_found = [e for e in endpoints if e["status"] == "not_found"]
            errors = [e for e in endpoints if e["status"] in ["server_error", "error", "method_not_allowed"]]
            
            report.append(f"\n### ✅ 動作中のエンドポイント ({len(working)})\n")
            for e in working:
                report.append(f"- `{e['method']} {e['path']}` - {e['description']}\n")
            
            report.append(f"\n### ⚠️ 有効なデータが必要 ({len(needs_data)})\n")
            for e in needs_data:
                report.append(f"- `{e['method']} {e['path']}` - {e['description']} (Status: {e['status_code']})\n")
            
            if not_found:
                report.append(f"\n### ❌ 未実装 ({len(not_found)})\n")
                for e in not_found:
                    report.append(f"- `{e['method']} {e['path']}` - {e['description']}\n")
            
            if errors:
                report.append(f"\n### 🔥 エラー ({len(errors)})\n")
                for e in errors:
                    report.append(f"- `{e['method']} {e['path']}` - {e['description']} (Status: {e['status_code']})\n")
        
        # サマリー
        report.append("\n---\n")
        report.append("\n## 📊 サマリー\n")
        
        total = sum(len(endpoints) for endpoints in results.values())
        working_total = sum(len([e for e in endpoints if e["status"] == "working"]) for endpoints in results.values())
        needs_data_total = sum(len([e for e in endpoints if e["status"] == "needs_valid_data"]) for endpoints in results.values())
        
        report.append(f"- **総エンドポイント数**: {total}\n")
        report.append(f"- **動作中**: {working_total}\n")
        report.append(f"- **データ必要**: {needs_data_total}\n")
        report.append(f"- **利用可能**: {working_total + needs_data_total} ({(working_total + needs_data_total) / total * 100:.1f}%)\n")
        
        return "".join(report)


async def main():
    """メイン関数"""
    discoverer = APIEndpointDiscoverer()
    
    try:
        # エンドポイント検出
        results = await discoverer.discover_all_endpoints()
        
        # レポート生成
        report = discoverer.generate_report(results)
        
        # レポート表示
        print("="*60)
        print(report)
        print("="*60)
        
        # ファイルに保存
        report_file = "API_ENDPOINTS_REPORT.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 レポートを保存しました: {report_file}")
        
        # JSON形式でも保存
        json_file = "api_endpoints.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON形式でも保存しました: {json_file}\n")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
