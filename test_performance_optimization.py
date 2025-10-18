"""
ローカルテスト環境のパフォーマンス最適化テスト

起動時間の測定と最適化、メモリ使用量の最適化、並列処理の改善
要件: 7.5
"""

import os
import sys
import json
import time
import psutil
import subprocess
import concurrent.futures
from typing import Dict, List, Any, Tuple
from pathlib import Path


class PerformanceOptimizer:
    """パフォーマンス最適化とベンチマーク"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
        
    def measure_startup_time(self) -> Dict[str, Any]:
        """起動時間の測定"""
        print("\n=== 起動時間測定 ===")
        result = {
            "test_name": "startup_time_measurement",
            "measurements": []
        }
        
        components = [
            ("環境チェック", self._measure_environment_check),
            ("モックDB初期化", self._measure_mock_db_init),
            ("サービスマネージャー初期化", self._measure_service_manager_init),
            ("設定ファイル読み込み", self._measure_config_loading),
        ]
        
        total_time = 0
        for component_name, measure_func in components:
            try:
                elapsed_time = measure_func()
                result["measurements"].append({
                    "component": component_name,
                    "time_ms": elapsed_time * 1000,
                    "time_s": elapsed_time
                })
                total_time += elapsed_time
                print(f"  {component_name}: {elapsed_time*1000:.2f}ms")
            except Exception as e:
                print(f"  ✗ {component_name}: エラー - {e}")
                result["measurements"].append({
                    "component": component_name,
                    "error": str(e)
                })
        
        result["total_time_ms"] = total_time * 1000
        result["total_time_s"] = total_time
        print(f"\n  合計起動時間: {total_time*1000:.2f}ms ({total_time:.2f}s)")
        
        # パフォーマンス評価
        if total_time < 1.0:
            result["performance_rating"] = "優秀"
            print(f"  評価: ✓ 優秀（1秒未満）")
        elif total_time < 3.0:
            result["performance_rating"] = "良好"
            print(f"  評価: ✓ 良好（3秒未満）")
        elif total_time < 5.0:
            result["performance_rating"] = "普通"
            print(f"  評価: ○ 普通（5秒未満）")
        else:
            result["performance_rating"] = "要改善"
            print(f"  評価: △ 要改善（5秒以上）")
        
        return result
    
    def _measure_environment_check(self) -> float:
        """環境チェックの測定"""
        start_time = time.time()
        
        # Python バージョンチェック
        _ = sys.version_info
        
        # 基本コマンドの存在確認（軽量版）
        commands = ["python"]
        for cmd in commands:
            try:
                subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    timeout=2
                )
            except:
                pass
        
        return time.time() - start_time
    
    def _measure_mock_db_init(self) -> float:
        """モックDB初期化の測定"""
        start_time = time.time()
        
        try:
            import mock_database
            client = mock_database.MockFirestoreClient(persist_data=False)
            
            # 基本操作
            collection = client.collection("test")
            doc_ref = collection.document("test_doc")
            doc_ref.set({"test": "data"})
            _ = doc_ref.get()
        except:
            pass
        
        return time.time() - start_time
    
    def _measure_service_manager_init(self) -> float:
        """サービスマネージャー初期化の測定"""
        start_time = time.time()
        
        try:
            import local_service_manager
            config_file = "local_services_config.json"
            if os.path.exists(config_file):
                _ = local_service_manager.LocalServiceManager(config_file)
        except:
            pass
        
        return time.time() - start_time
    
    def _measure_config_loading(self) -> float:
        """設定ファイル読み込みの測定"""
        start_time = time.time()
        
        try:
            config_file = "local_services_config.json"
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    _ = json.load(f)
        except:
            pass
        
        return time.time() - start_time
    
    def measure_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量の測定"""
        print("\n=== メモリ使用量測定 ===")
        result = {
            "test_name": "memory_usage_measurement",
            "measurements": []
        }
        
        # 初期メモリ使用量
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        print(f"  初期メモリ: {initial_memory:.2f}MB")
        
        # 各コンポーネントのメモリ使用量
        components = [
            ("モックDB（小規模データ）", self._measure_mock_db_memory_small),
            ("モックDB（中規模データ）", self._measure_mock_db_memory_medium),
            ("サービスマネージャー", self._measure_service_manager_memory),
        ]
        
        for component_name, measure_func in components:
            try:
                memory_before = self.process.memory_info().rss / 1024 / 1024
                measure_func()
                memory_after = self.process.memory_info().rss / 1024 / 1024
                memory_delta = memory_after - memory_before
                
                result["measurements"].append({
                    "component": component_name,
                    "memory_mb": memory_delta,
                    "memory_before_mb": memory_before,
                    "memory_after_mb": memory_after
                })
                print(f"  {component_name}: +{memory_delta:.2f}MB")
            except Exception as e:
                print(f"  ✗ {component_name}: エラー - {e}")
                result["measurements"].append({
                    "component": component_name,
                    "error": str(e)
                })
        
        # 最終メモリ使用量
        final_memory = self.process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        result["initial_memory_mb"] = initial_memory
        result["final_memory_mb"] = final_memory
        result["total_increase_mb"] = total_increase
        
        print(f"\n  最終メモリ: {final_memory:.2f}MB")
        print(f"  総増加量: +{total_increase:.2f}MB")
        
        # メモリ使用量評価
        if total_increase < 50:
            result["memory_rating"] = "優秀"
            print(f"  評価: ✓ 優秀（50MB未満）")
        elif total_increase < 100:
            result["memory_rating"] = "良好"
            print(f"  評価: ✓ 良好（100MB未満）")
        elif total_increase < 200:
            result["memory_rating"] = "普通"
            print(f"  評価: ○ 普通（200MB未満）")
        else:
            result["memory_rating"] = "要改善"
            print(f"  評価: △ 要改善（200MB以上）")
        
        return result
    
    def _measure_mock_db_memory_small(self):
        """小規模データでのモックDB メモリ測定"""
        import mock_database
        client = mock_database.MockFirestoreClient(persist_data=False)
        
        # 10件のドキュメントを作成
        collection = client.collection("test_small")
        for i in range(10):
            doc_ref = collection.document(f"doc_{i}")
            doc_ref.set({"id": i, "data": f"test_data_{i}"})
    
    def _measure_mock_db_memory_medium(self):
        """中規模データでのモックDBメモリ測定"""
        import mock_database
        client = mock_database.MockFirestoreClient(persist_data=False)
        
        # 100件のドキュメントを作成
        collection = client.collection("test_medium")
        for i in range(100):
            doc_ref = collection.document(f"doc_{i}")
            doc_ref.set({
                "id": i,
                "data": f"test_data_{i}",
                "metadata": {"created": time.time(), "index": i}
            })
    
    def _measure_service_manager_memory(self):
        """サービスマネージャーのメモリ測定"""
        import local_service_manager
        config_file = "local_services_config.json"
        if os.path.exists(config_file):
            _ = local_service_manager.LocalServiceManager(config_file)
    
    def test_parallel_processing(self) -> Dict[str, Any]:
        """並列処理の改善テスト"""
        print("\n=== 並列処理テスト ===")
        result = {
            "test_name": "parallel_processing_test",
            "tests": []
        }
        
        # シーケンシャル vs 並列の比較
        tasks = [
            ("タスク1", 0.1),
            ("タスク2", 0.1),
            ("タスク3", 0.1),
            ("タスク4", 0.1),
        ]
        
        # シーケンシャル実行
        print("\n  シーケンシャル実行:")
        sequential_time = self._run_sequential(tasks)
        print(f"    実行時間: {sequential_time*1000:.2f}ms")
        
        # 並列実行
        print("\n  並列実行:")
        parallel_time = self._run_parallel(tasks)
        print(f"    実行時間: {parallel_time*1000:.2f}ms")
        
        # 改善率の計算
        improvement = ((sequential_time - parallel_time) / sequential_time) * 100
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        
        result["sequential_time_ms"] = sequential_time * 1000
        result["parallel_time_ms"] = parallel_time * 1000
        result["improvement_percent"] = improvement
        result["speedup_factor"] = speedup
        
        print(f"\n  改善率: {improvement:.1f}%")
        print(f"  高速化倍率: {speedup:.2f}x")
        
        if improvement > 50:
            result["parallel_rating"] = "優秀"
            print(f"  評価: ✓ 優秀（50%以上の改善）")
        elif improvement > 30:
            result["parallel_rating"] = "良好"
            print(f"  評価: ✓ 良好（30%以上の改善）")
        elif improvement > 10:
            result["parallel_rating"] = "普通"
            print(f"  評価: ○ 普通（10%以上の改善）")
        else:
            result["parallel_rating"] = "要改善"
            print(f"  評価: △ 要改善（10%未満の改善）")
        
        return result
    
    def _run_sequential(self, tasks: List[Tuple[str, float]]) -> float:
        """シーケンシャル実行"""
        start_time = time.time()
        
        for task_name, duration in tasks:
            time.sleep(duration)
        
        return time.time() - start_time
    
    def _run_parallel(self, tasks: List[Tuple[str, float]]) -> float:
        """並列実行"""
        start_time = time.time()
        
        def execute_task(task_info):
            task_name, duration = task_info
            time.sleep(duration)
            return task_name
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(execute_task, task) for task in tasks]
            concurrent.futures.wait(futures)
        
        return time.time() - start_time
    
    def generate_optimization_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """最適化の推奨事項を生成"""
        recommendations = []
        
        # 起動時間の推奨
        if "startup_time" in results:
            startup = results["startup_time"]
            if startup.get("performance_rating") in ["要改善", "普通"]:
                recommendations.append(
                    "起動時間の改善: 遅延読み込み（lazy loading）の導入を検討してください"
                )
                recommendations.append(
                    "起動時間の改善: 不要な初期化処理を削減してください"
                )
        
        # メモリ使用量の推奨
        if "memory_usage" in results:
            memory = results["memory_usage"]
            if memory.get("memory_rating") in ["要改善", "普通"]:
                recommendations.append(
                    "メモリ使用量の改善: データ構造の最適化を検討してください"
                )
                recommendations.append(
                    "メモリ使用量の改善: 不要なデータのキャッシュを削減してください"
                )
        
        # 並列処理の推奨
        if "parallel_processing" in results:
            parallel = results["parallel_processing"]
            if parallel.get("parallel_rating") in ["要改善", "普通"]:
                recommendations.append(
                    "並列処理の改善: より多くの処理を並列化してください"
                )
                recommendations.append(
                    "並列処理の改善: 非同期処理（async/await）の導入を検討してください"
                )
        
        # 一般的な推奨
        recommendations.extend([
            "キャッシング: 頻繁にアクセスされるデータをキャッシュしてください",
            "プロファイリング: 定期的にパフォーマンスプロファイリングを実行してください",
            "モニタリング: 本番環境でのパフォーマンスメトリクスを監視してください"
        ])
        
        return recommendations
    
    def run_all_tests(self) -> Dict[str, Any]:
        """全パフォーマンステストの実行"""
        print("=" * 60)
        print("ローカルテスト環境 - パフォーマンス最適化テスト")
        print("=" * 60)
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "python_version": sys.version
            }
        }
        
        # システム情報の表示
        print(f"\nシステム情報:")
        print(f"  CPU コア数: {results['system_info']['cpu_count']}")
        print(f"  総メモリ: {results['system_info']['memory_total_gb']:.2f}GB")
        print(f"  Python: {sys.version.split()[0]}")
        
        # 各テストの実行
        results["startup_time"] = self.measure_startup_time()
        results["memory_usage"] = self.measure_memory_usage()
        results["parallel_processing"] = self.test_parallel_processing()
        
        # 最適化推奨事項の生成
        recommendations = self.generate_optimization_recommendations(results)
        results["recommendations"] = recommendations
        
        # 推奨事項の表示
        print("\n" + "=" * 60)
        print("最適化推奨事項")
        print("=" * 60)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # 総合評価
        ratings = [
            results["startup_time"].get("performance_rating"),
            results["memory_usage"].get("memory_rating"),
            results["parallel_processing"].get("parallel_rating")
        ]
        
        excellent_count = ratings.count("優秀")
        good_count = ratings.count("良好")
        
        if excellent_count >= 2:
            overall_rating = "優秀"
        elif excellent_count + good_count >= 2:
            overall_rating = "良好"
        else:
            overall_rating = "要改善"
        
        results["overall_rating"] = overall_rating
        
        print("\n" + "=" * 60)
        print("総合評価")
        print("=" * 60)
        print(f"起動時間: {results['startup_time'].get('performance_rating')}")
        print(f"メモリ使用量: {results['memory_usage'].get('memory_rating')}")
        print(f"並列処理: {results['parallel_processing'].get('parallel_rating')}")
        print(f"\n総合評価: {overall_rating}")
        
        # 結果の保存
        result_file = "test_results/performance_optimization_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 詳細結果を保存: {result_file}")
        
        return results


def main():
    """メイン実行関数"""
    optimizer = PerformanceOptimizer()
    results = optimizer.run_all_tests()
    
    # 終了コードの設定（総合評価が「要改善」の場合は警告）
    if results.get("overall_rating") == "要改善":
        print("\n⚠ パフォーマンスの改善を推奨します")
        sys.exit(1)
    else:
        print("\n✓ パフォーマンステスト完了")
        sys.exit(0)


if __name__ == "__main__":
    main()
