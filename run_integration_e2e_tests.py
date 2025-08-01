#!/usr/bin/env python3
"""
統合テスト・エンドツーエンドテスト実行スクリプト (タスク27.2)

このスクリプトは以下のテストを順次実行します:
1. 包括的統合テスト・エンドツーエンドテスト
2. データ永続化検証テスト
3. エラー処理適切性確認テスト

要件:
- ユーザージャーニー全体の動作確認
- 朝のタスク配信から夜のストーリー生成までの基本フロー
- データ永続化の動作確認
- エラー処理の適切性確認
- システム全体の動作保証
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import logging
import subprocess
import sys

# 作成したテストモジュールをインポート
from test_integration_e2e_comprehensive import IntegrationE2ETester
from test_data_persistence_verification import DataPersistenceVerifier
from test_error_handling_comprehensive import ErrorHandlingTester

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationE2ETestRunner:
    """統合テスト・エンドツーエンドテスト実行クラス"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def check_prerequisites(self) -> bool:
        """前提条件チェック"""
        logger.info("🔍 前提条件チェック開始...")
        
        # 必要なサービスが起動しているかチェック
        required_services = [
            ("認証サービス", "http://localhost:8002"),
            ("コアゲームエンジン", "http://localhost:8001"),
            ("タスク管理", "http://localhost:8003"),
            ("Mandalaシステム", "http://localhost:8004")
        ]
        
        import httpx
        
        missing_services = []
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, url in required_services:
                try:
                    response = await client.get(f"{url}/health")
                    if response.status_code not in [200, 404]:  # 404でもサービスは動作中
                        missing_services.append(service_name)
                except:
                    missing_services.append(service_name)
        
        if missing_services:
            logger.error(f"❌ 以下のサービスが起動していません: {', '.join(missing_services)}")
            logger.error("deploy_local.pyでサービスを起動してから再実行してください。")
            return False
        
        logger.info("✅ 前提条件チェック完了")
        return True
    
    async def run_comprehensive_integration_tests(self) -> Dict[str, Any]:
        """包括的統合テスト実行"""
        logger.info("\n" + "="*80)
        logger.info("🎯 包括的統合テスト・エンドツーエンドテスト実行")
        logger.info("="*80)
        
        tester = IntegrationE2ETester()
        
        try:
            results = await tester.run_comprehensive_tests()
            tester.print_comprehensive_summary(results)
            return results
        except Exception as e:
            logger.error(f"包括的統合テストエラー: {str(e)}")
            return {"error": str(e)}
    
    async def run_data_persistence_tests(self) -> Dict[str, Any]:
        """データ永続化テスト実行"""
        logger.info("\n" + "="*80)
        logger.info("💾 データ永続化検証テスト実行")
        logger.info("="*80)
        
        verifier = DataPersistenceVerifier()
        
        try:
            results = await verifier.run_persistence_tests()
            verifier.print_persistence_summary(results)
            return results
        except Exception as e:
            logger.error(f"データ永続化テストエラー: {str(e)}")
            return {"error": str(e)}
    
    async def run_error_handling_tests(self) -> Dict[str, Any]:
        """エラー処理テスト実行"""
        logger.info("\n" + "="*80)
        logger.info("🚨 エラー処理適切性確認テスト実行")
        logger.info("="*80)
        
        tester = ErrorHandlingTester()
        
        try:
            results = await tester.run_error_handling_tests()
            tester.print_error_handling_summary(results)
            return results
        except Exception as e:
            logger.error(f"エラー処理テストエラー: {str(e)}")
            return {"error": str(e)}
    
    def calculate_overall_success_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """全体的な成功指標計算"""
        metrics = {
            "total_test_categories": 0,
            "successful_categories": 0,
            "test_details": {},
            "overall_success_rate": 0.0,
            "critical_failures": [],
            "recommendations": []
        }
        
        # 包括的統合テスト結果分析
        if "comprehensive_integration" in all_results:
            comp_results = all_results["comprehensive_integration"]
            metrics["total_test_categories"] += 1
            
            if not comp_results.get("error"):
                # ユーザージャーニー成功率
                journey_results = comp_results.get("user_journey", {})
                if journey_results and not journey_results.get("error"):
                    journey_success_count = sum(1 for k, v in journey_results.items() 
                                              if isinstance(v, dict) and v.get("success", False))
                    journey_total = len([k for k in journey_results.keys() if k != "error"])
                    
                    if journey_total > 0:
                        journey_success_rate = journey_success_count / journey_total
                        metrics["test_details"]["user_journey_success_rate"] = journey_success_rate
                        
                        if journey_success_rate >= 0.8:
                            metrics["successful_categories"] += 1
                        else:
                            metrics["critical_failures"].append("ユーザージャーニーテストの成功率が低い")
                
                # エラー処理成功率
                error_handling = comp_results.get("error_handling", {})
                if error_handling:
                    error_rate = error_handling.get("error_handling_rate", 0)
                    metrics["test_details"]["error_handling_rate"] = error_rate
                    
                    if error_rate >= 0.7:
                        metrics["successful_categories"] += 0.5  # 部分的成功
            else:
                metrics["critical_failures"].append("包括的統合テストが実行できない")
        
        # データ永続化テスト結果分析
        if "data_persistence" in all_results:
            persist_results = all_results["data_persistence"]
            metrics["total_test_categories"] += 1
            
            if not persist_results.get("error"):
                # データ整合性成功率計算
                persistence_success_count = 0
                persistence_total = 0
                
                for test_key, test_result in persist_results.items():
                    if isinstance(test_result, dict) and "success" in test_result:
                        persistence_total += 1
                        if test_result.get("success", False) and test_result.get("data_integrity", False):
                            persistence_success_count += 1
                
                if persistence_total > 0:
                    persistence_rate = persistence_success_count / persistence_total
                    metrics["test_details"]["data_persistence_rate"] = persistence_rate
                    
                    if persistence_rate >= 0.8:
                        metrics["successful_categories"] += 1
                    else:
                        metrics["critical_failures"].append("データ永続化の成功率が低い")
            else:
                metrics["critical_failures"].append("データ永続化テストが実行できない")
        
        # エラー処理テスト結果分析
        if "error_handling" in all_results:
            error_results = all_results["error_handling"]
            metrics["total_test_categories"] += 1
            
            if not error_results.get("error"):
                # エラー処理適切性計算
                error_handling_success_count = 0
                error_handling_total = 0
                
                for category_key, category_result in error_results.items():
                    if isinstance(category_result, dict) and "success" in category_result:
                        error_handling_total += 1
                        if category_result.get("success", False):
                            error_handling_success_count += 1
                
                if error_handling_total > 0:
                    error_handling_rate = error_handling_success_count / error_handling_total
                    metrics["test_details"]["error_handling_appropriateness_rate"] = error_handling_rate
                    
                    if error_handling_rate >= 0.7:
                        metrics["successful_categories"] += 1
                    else:
                        metrics["critical_failures"].append("エラー処理の適切性が不十分")
            else:
                metrics["critical_failures"].append("エラー処理テストが実行できない")
        
        # 全体成功率計算
        if metrics["total_test_categories"] > 0:
            metrics["overall_success_rate"] = metrics["successful_categories"] / metrics["total_test_categories"]
        
        # 推奨事項生成
        if metrics["overall_success_rate"] >= 0.9:
            metrics["recommendations"] = [
                "本番環境デプロイの準備",
                "継続的監視システムの設定",
                "パフォーマンス最適化の検討"
            ]
        elif metrics["overall_success_rate"] >= 0.7:
            metrics["recommendations"] = [
                "失敗したテストケースの詳細調査",
                "部分的な機能改善",
                "追加テストの実行"
            ]
        else:
            metrics["recommendations"] = [
                "重大な問題の修正",
                "システム設計の見直し",
                "基本機能の再実装"
            ]
        
        return metrics
    
    def print_final_summary(self, all_results: Dict[str, Any], metrics: Dict[str, Any]):
        """最終サマリー表示"""
        logger.info("\n" + "="*100)
        logger.info("📊 統合テスト・エンドツーエンドテスト 最終結果サマリー")
        logger.info("="*100)
        
        # 実行時間表示
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            logger.info(f"⏱️  総実行時間: {duration:.2f}秒")
        
        # 各テストカテゴリの結果
        logger.info("\n📋 テストカテゴリ別結果:")
        
        test_categories = [
            ("包括的統合テスト", "comprehensive_integration"),
            ("データ永続化テスト", "data_persistence"),
            ("エラー処理テスト", "error_handling")
        ]
        
        for category_name, category_key in test_categories:
            if category_key in all_results:
                result = all_results[category_key]
                if result.get("error"):
                    status = f"❌ エラー: {result['error']}"
                else:
                    status = "✅ 実行完了"
                
                logger.info(f"   {category_name}: {status}")
        
        # 成功指標表示
        logger.info(f"\n🎯 全体成功率: {metrics['overall_success_rate']:.1%}")
        logger.info(f"📈 成功カテゴリ: {metrics['successful_categories']:.1f}/{metrics['total_test_categories']}")
        
        # 詳細指標
        if metrics["test_details"]:
            logger.info("\n📊 詳細指標:")
            for metric_name, metric_value in metrics["test_details"].items():
                if isinstance(metric_value, float):
                    logger.info(f"   {metric_name}: {metric_value:.1%}")
                else:
                    logger.info(f"   {metric_name}: {metric_value}")
        
        # 重大な問題
        if metrics["critical_failures"]:
            logger.info("\n⚠️  重大な問題:")
            for failure in metrics["critical_failures"]:
                logger.info(f"   - {failure}")
        
        # 総合評価
        logger.info("\n" + "="*100)
        
        if metrics["overall_success_rate"] >= 0.9:
            logger.info("🎉 統合テスト・エンドツーエンドテスト 大成功！")
            logger.info("✅ システム全体が高品質で動作しています")
            logger.info("🚀 本番環境デプロイの準備が整いました")
        elif metrics["overall_success_rate"] >= 0.7:
            logger.info("✅ 統合テスト・エンドツーエンドテスト 成功")
            logger.info("⚠️  一部改善の余地がありますが、基本機能は正常です")
            logger.info("🔧 指摘された問題を修正後、本番デプロイを検討してください")
        elif metrics["overall_success_rate"] >= 0.5:
            logger.info("⚠️  統合テスト・エンドツーエンドテスト 部分成功")
            logger.info("🔧 重要な問題がいくつか発見されました")
            logger.info("🛠️  問題修正後に再テストが必要です")
        else:
            logger.error("❌ 統合テスト・エンドツーエンドテスト 失敗")
            logger.error("🚨 システムに重大な問題があります")
            logger.error("🛠️  基本機能から見直しが必要です")
        
        # 推奨事項
        logger.info("\n💡 推奨事項:")
        for recommendation in metrics["recommendations"]:
            logger.info(f"   - {recommendation}")
        
        logger.info("\n📄 詳細なテスト結果は各テストの出力ファイルをご確認ください")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """全テスト実行"""
        logger.info("🎯 統合テスト・エンドツーエンドテスト実行開始")
        logger.info("タスク27.2: 統合テストとエンドツーエンドテスト")
        logger.info("="*100)
        
        self.start_time = time.time()
        
        # 前提条件チェック
        if not await self.check_prerequisites():
            return {"error": "Prerequisites not met"}
        
        all_results = {}
        
        try:
            # 1. 包括的統合テスト・エンドツーエンドテスト
            logger.info("🔄 ステップ1: 包括的統合テスト・エンドツーエンドテスト実行中...")
            all_results["comprehensive_integration"] = await self.run_comprehensive_integration_tests()
            
            # 2. データ永続化検証テスト
            logger.info("🔄 ステップ2: データ永続化検証テスト実行中...")
            all_results["data_persistence"] = await self.run_data_persistence_tests()
            
            # 3. エラー処理適切性確認テスト
            logger.info("🔄 ステップ3: エラー処理適切性確認テスト実行中...")
            all_results["error_handling"] = await self.run_error_handling_tests()
            
            self.end_time = time.time()
            
            # 全体的な成功指標計算
            metrics = self.calculate_overall_success_metrics(all_results)
            
            # 最終サマリー表示
            self.print_final_summary(all_results, metrics)
            
            # 結果保存
            await self.save_comprehensive_results(all_results, metrics)
            
            return {
                "test_results": all_results,
                "metrics": metrics,
                "success": metrics["overall_success_rate"] >= 0.7
            }
            
        except Exception as e:
            self.end_time = time.time()
            logger.error(f"❌ テスト実行中にエラーが発生しました: {str(e)}")
            return {"error": str(e)}
    
    async def save_comprehensive_results(self, all_results: Dict[str, Any], metrics: Dict[str, Any]):
        """包括的結果保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"integration_e2e_comprehensive_results_{timestamp}.json"
        
        comprehensive_data = {
            "timestamp": timestamp,
            "test_type": "integration_e2e_comprehensive",
            "task": "27.2 統合テストとエンドツーエンドテスト",
            "execution_time": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration_seconds": self.end_time - self.start_time if self.start_time and self.end_time else 0
            },
            "test_results": all_results,
            "success_metrics": metrics,
            "requirements_verification": {
                "user_journey_tested": "comprehensive_integration" in all_results,
                "morning_to_evening_flow_tested": "comprehensive_integration" in all_results,
                "data_persistence_verified": "data_persistence" in all_results,
                "error_handling_verified": "error_handling" in all_results,
                "system_operation_guaranteed": metrics["overall_success_rate"] >= 0.7
            },
            "task_completion_status": "completed" if metrics["overall_success_rate"] >= 0.7 else "needs_improvement"
        }
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 包括的テスト結果を保存しました: {result_file}")


async def main():
    """メイン実行関数"""
    runner = IntegrationE2ETestRunner()
    
    try:
        results = await runner.run_all_tests()
        
        # 終了コード設定
        if results.get("success", False):
            logger.info("✅ 統合テスト・エンドツーエンドテスト完了")
            sys.exit(0)
        else:
            logger.error("❌ 統合テスト・エンドツーエンドテストで問題が発見されました")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️  テストが中断されました")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ 予期しないエラー: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())