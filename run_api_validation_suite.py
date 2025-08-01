"""
API連携とエンドポイント検証統合スイート

タスク26.4: API連携とエンドポイント検証の完全実行
- サービス間API呼び出しの動作確認
- エラーハンドリングの適切性を検証
- レスポンス形式の統一性を確認
- CORS設定の正常動作を確認
"""

import asyncio
import json
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class APIValidationSuite:
    """API連携とエンドポイント検証統合スイート"""
    
    def __init__(self):
        self.validation_modules = [
            {
                "name": "基本API連携テスト",
                "script": "test_api_integration.py",
                "description": "基本的なAPI連携とサービス間通信の確認"
            },
            {
                "name": "包括的エンドポイント検証",
                "script": "test_api_endpoint_validation.py",
                "description": "全エンドポイントの包括的な機能検証"
            },
            {
                "name": "サービス間通信詳細検証",
                "script": "test_service_communication.py",
                "description": "サービス間通信の詳細な動作確認"
            },
            {
                "name": "CORS設定詳細検証",
                "script": "test_cors_advanced_validation.py",
                "description": "CORS設定の詳細な検証"
            },
            {
                "name": "エラーハンドリング統一性検証",
                "script": "test_error_handling.py",
                "description": "エラーハンドリングの統一性と適切性の検証"
            }
        ]
        
        self.services_to_check = [
            {"name": "Core Game Engine", "port": 8001, "url": "http://localhost:8001/health"},
            {"name": "Auth Service", "port": 8002, "url": "http://localhost:8002/health"},
            {"name": "Task Management", "port": 8003, "url": "http://localhost:8003/health"}
        ]
        
        self.results = {
            "suite_start_time": None,
            "suite_end_time": None,
            "total_duration": 0,
            "service_availability": {},
            "validation_results": {},
            "overall_success": False,
            "summary": {},
            "recommendations": []
        }
    
    async def run_complete_validation_suite(self) -> Dict[str, Any]:
        """完全なAPI検証スイートを実行"""
        print("=" * 60)
        print("API連携とエンドポイント検証統合スイート")
        print("=" * 60)
        print(f"実行開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.results["suite_start_time"] = datetime.now().isoformat()
        
        # 1. サービス可用性確認
        await self._check_service_availability()
        
        # 2. 各検証モジュールの実行
        await self._run_validation_modules()
        
        # 3. 結果の統合と分析
        self._analyze_overall_results()
        
        # 4. 最終レポートの生成
        self._generate_final_report()
        
        self.results["suite_end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = (
            datetime.fromisoformat(self.results["suite_end_time"]) - 
            datetime.fromisoformat(self.results["suite_start_time"])
        ).total_seconds()
        
        return self.results
    
    async def _check_service_availability(self):
        """サービス可用性確認"""
        print("1. サービス可用性確認")
        print("-" * 30)
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            for service in self.services_to_check:
                try:
                    start_time = time.time()
                    response = await client.get(service["url"], timeout=5.0)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        status = "利用可能"
                        available = True
                        print(f"✓ {service['name']}: {status} ({response_time:.1f}ms)")
                    else:
                        status = f"HTTP {response.status_code}"
                        available = False
                        print(f"⚠ {service['name']}: {status} ({response_time:.1f}ms)")
                    
                    self.results["service_availability"][service["name"]] = {
                        "available": available,
                        "status": status,
                        "response_time_ms": response_time,
                        "port": service["port"]
                    }
                    
                except httpx.ConnectError:
                    status = "接続失敗 (サービス未起動)"
                    print(f"✗ {service['name']}: {status}")
                    self.results["service_availability"][service["name"]] = {
                        "available": False,
                        "status": status,
                        "response_time_ms": 0,
                        "port": service["port"]
                    }
                    
                except Exception as e:
                    status = f"エラー: {str(e)}"
                    print(f"✗ {service['name']}: {status}")
                    self.results["service_availability"][service["name"]] = {
                        "available": False,
                        "status": status,
                        "response_time_ms": 0,
                        "port": service["port"]
                    }
        
        # サービス可用性サマリー
        available_services = len([s for s in self.results["service_availability"].values() if s["available"]])
        total_services = len(self.services_to_check)
        
        print()
        print(f"サービス可用性: {available_services}/{total_services}")
        
        if available_services == 0:
            print("⚠ 警告: すべてのサービスが利用できません。deploy_local.pyでサービスを起動してください。")
            print("   検証は続行しますが、接続エラーが発生します。")
        elif available_services < total_services:
            print("⚠ 警告: 一部のサービスが利用できません。")
        else:
            print("✓ すべてのサービスが利用可能です。")
        
        print()
    
    async def _run_validation_modules(self):
        """各検証モジュールの実行"""
        print("2. 検証モジュール実行")
        print("-" * 30)
        
        for i, module in enumerate(self.validation_modules, 1):
            print(f"{i}. {module['name']}")
            print(f"   {module['description']}")
            
            module_start_time = time.time()
            
            try:
                # Pythonスクリプトを実行
                result = subprocess.run(
                    [sys.executable, module["script"]],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2分のタイムアウト
                )
                
                module_duration = time.time() - module_start_time
                
                # 実行結果の解析
                success = result.returncode == 0
                stdout_lines = result.stdout.strip().split('\n') if result.stdout else []
                stderr_lines = result.stderr.strip().split('\n') if result.stderr else []
                
                # 成功/失敗の判定
                if success:
                    print(f"   ✓ 実行成功 ({module_duration:.1f}秒)")
                else:
                    print(f"   ✗ 実行失敗 ({module_duration:.1f}秒)")
                    if stderr_lines:
                        print(f"   エラー: {stderr_lines[-1]}")
                
                # 結果の保存
                self.results["validation_results"][module["name"]] = {
                    "script": module["script"],
                    "success": success,
                    "duration": module_duration,
                    "return_code": result.returncode,
                    "stdout_lines": len(stdout_lines),
                    "stderr_lines": len(stderr_lines),
                    "last_stdout": stdout_lines[-1] if stdout_lines else "",
                    "last_stderr": stderr_lines[-1] if stderr_lines else ""
                }
                
                # レポートファイルの確認
                report_files = self._find_report_files(module["script"])
                if report_files:
                    self.results["validation_results"][module["name"]]["report_files"] = report_files
                    print(f"   📄 レポートファイル: {', '.join(report_files)}")
                
            except subprocess.TimeoutExpired:
                module_duration = time.time() - module_start_time
                print(f"   ⏰ タイムアウト ({module_duration:.1f}秒)")
                self.results["validation_results"][module["name"]] = {
                    "script": module["script"],
                    "success": False,
                    "duration": module_duration,
                    "return_code": -1,
                    "error": "タイムアウト"
                }
                
            except Exception as e:
                module_duration = time.time() - module_start_time
                print(f"   ✗ 実行エラー: {str(e)} ({module_duration:.1f}秒)")
                self.results["validation_results"][module["name"]] = {
                    "script": module["script"],
                    "success": False,
                    "duration": module_duration,
                    "return_code": -1,
                    "error": str(e)
                }
            
            print()
    
    def _find_report_files(self, script_name: str) -> List[str]:
        """スクリプトが生成したレポートファイルを検索"""
        report_patterns = [
            f"{script_name.replace('.py', '')}_report.json",
            f"{script_name.replace('test_', '').replace('.py', '')}_report.json",
            "*validation_report.json",
            "*_report.json"
        ]
        
        found_files = []
        for pattern in report_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    found_files.append(str(file_path))
        
        return found_files
    
    def _analyze_overall_results(self):
        """結果の統合と分析"""
        print("3. 結果分析")
        print("-" * 30)
        
        # 基本統計
        total_modules = len(self.validation_modules)
        successful_modules = len([
            r for r in self.results["validation_results"].values() 
            if r.get("success", False)
        ])
        failed_modules = total_modules - successful_modules
        
        # サービス可用性統計
        available_services = len([
            s for s in self.results["service_availability"].values() 
            if s["available"]
        ])
        total_services = len(self.services_to_check)
        
        # 全体成功判定
        service_availability_ok = available_services >= total_services * 0.5  # 50%以上のサービスが利用可能
        module_success_ok = successful_modules >= total_modules * 0.7  # 70%以上のモジュールが成功
        
        overall_success = service_availability_ok and module_success_ok
        
        # サマリーの生成
        self.results["summary"] = {
            "total_modules": total_modules,
            "successful_modules": successful_modules,
            "failed_modules": failed_modules,
            "module_success_rate": (successful_modules / total_modules * 100) if total_modules > 0 else 0,
            "available_services": available_services,
            "total_services": total_services,
            "service_availability_rate": (available_services / total_services * 100) if total_services > 0 else 0,
            "service_availability_ok": service_availability_ok,
            "module_success_ok": module_success_ok
        }
        
        self.results["overall_success"] = overall_success
        
        # 結果表示
        print(f"検証モジュール: {successful_modules}/{total_modules} 成功 ({self.results['summary']['module_success_rate']:.1f}%)")
        print(f"サービス可用性: {available_services}/{total_services} 利用可能 ({self.results['summary']['service_availability_rate']:.1f}%)")
        print()
        
        if overall_success:
            print("✓ 全体的な検証結果: 成功")
        else:
            print("⚠ 全体的な検証結果: 改善が必要")
        
        print()
    
    def _generate_final_report(self):
        """最終レポートの生成"""
        print("4. 最終レポート生成")
        print("-" * 30)
        
        # 推奨事項の生成
        recommendations = []
        
        # サービス可用性に基づく推奨事項
        unavailable_services = [
            name for name, info in self.results["service_availability"].items()
            if not info["available"]
        ]
        
        if unavailable_services:
            recommendations.append(
                f"以下のサービスを起動してください: {', '.join(unavailable_services)}"
            )
            recommendations.append(
                "deploy_local.pyを使用してすべてのサービスを起動することを推奨します"
            )
        
        # 失敗したモジュールに基づく推奨事項
        failed_modules = [
            name for name, info in self.results["validation_results"].items()
            if not info.get("success", False)
        ]
        
        if failed_modules:
            recommendations.append(
                f"以下の検証モジュールが失敗しました: {', '.join(failed_modules)}"
            )
            recommendations.append(
                "個別にスクリプトを実行して詳細なエラー情報を確認してください"
            )
        
        # パフォーマンスに基づく推奨事項
        slow_services = [
            name for name, info in self.results["service_availability"].items()
            if info["available"] and info["response_time_ms"] > 1000
        ]
        
        if slow_services:
            recommendations.append(
                f"以下のサービスの応答時間が遅いです: {', '.join(slow_services)}"
            )
        
        if not recommendations:
            recommendations.append("すべての検証が正常に完了しました")
        
        self.results["recommendations"] = recommendations
        
        # 推奨事項の表示
        print("推奨事項:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"  {i}. {recommendation}")
        
        print()
        
        # レポートファイルの保存
        report_filename = f"api_validation_integrated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 統合レポートが '{report_filename}' に保存されました。")
        print()
        
        # 生成されたレポートファイルの一覧
        all_report_files = [report_filename]
        for module_result in self.results["validation_results"].values():
            if "report_files" in module_result:
                all_report_files.extend(module_result["report_files"])
        
        if len(all_report_files) > 1:
            print("生成されたレポートファイル:")
            for report_file in all_report_files:
                print(f"  - {report_file}")
            print()

async def main():
    """メイン実行関数"""
    suite = APIValidationSuite()
    
    try:
        results = await suite.run_complete_validation_suite()
        
        print("=" * 60)
        print("API連携とエンドポイント検証完了")
        print("=" * 60)
        print(f"実行時間: {results['total_duration']:.1f}秒")
        print(f"全体結果: {'成功' if results['overall_success'] else '改善が必要'}")
        print()
        
        return results["overall_success"]
        
    except KeyboardInterrupt:
        print("\n検証スイートが中断されました。")
        return False
        
    except Exception as e:
        print(f"\n検証スイート実行中にエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"実行エラー: {str(e)}")
        sys.exit(1)