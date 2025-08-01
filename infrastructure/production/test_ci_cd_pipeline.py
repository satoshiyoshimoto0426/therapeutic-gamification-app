#!/usr/bin/env python3
"""
CI/CDパイプラインテストスクリプト
"""

import unittest
import json
import os
import sys
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# テスト対象のインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from deploy_script import DeploymentManager
from get_last_stable_revision import RevisionManager
from post_deployment_monitoring import PostDeploymentMonitor
from update_deployment_status import DeploymentStatusManager
from generate_deployment_report import DeploymentReportGenerator

class TestDeploymentManager(unittest.TestCase):
    """デプロイメントマネージャーのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.deployment_manager = DeploymentManager(
            project_id="test-project",
            service_name="test-service",
            region="asia-northeast1"
        )
    
    def test_init(self):
        """初期化テスト"""
        self.assertEqual(self.deployment_manager.project_id, "test-project")
        self.assertEqual(self.deployment_manager.service_name, "test-service")
        self.assertEqual(self.deployment_manager.region, "asia-northeast1")
        self.assertIsNotNone(self.deployment_manager.deployment_id)
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """コマンド実行成功テスト"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, stdout, stderr = self.deployment_manager.run_command(["echo", "test"])
        
        self.assertTrue(success)
        self.assertEqual(stdout, "success output")
        self.assertEqual(stderr, "")
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """コマンド実行失敗テスト"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["false"], "error output", "stderr")
        
        success, stdout, stderr = self.deployment_manager.run_command(["false"], check=False)
        
        self.assertFalse(success)
    
    @patch.object(DeploymentManager, 'run_command')
    def test_get_current_revision(self, mock_run_command):
        """現在のリビジョン取得テスト"""
        mock_run_command.return_value = (True, "test-service-12345", "")
        
        revision = self.deployment_manager.get_current_revision()
        
        self.assertEqual(revision, "test-service-12345")
        mock_run_command.assert_called_once()
    
    @patch.object(DeploymentManager, 'run_command')
    def test_get_service_url(self, mock_run_command):
        """サービスURL取得テスト"""
        mock_run_command.return_value = (True, "https://test-service.example.com", "")
        
        url = self.deployment_manager.get_service_url()
        
        self.assertEqual(url, "https://test-service.example.com")
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """ヘルスチェック成功テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response
        
        result = self.deployment_manager.health_check("https://test.example.com")
        
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """ヘルスチェック失敗テスト"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.deployment_manager.health_check("https://test.example.com")
        
        self.assertFalse(result)
    
    @patch.object(DeploymentManager, 'run_command')
    def test_deploy_new_revision(self, mock_run_command):
        """新しいリビジョンデプロイテスト"""
        mock_run_command.return_value = (True, "Deployed successfully", "")
        
        revision = self.deployment_manager.deploy_new_revision("gcr.io/test/image:latest")
        
        self.assertIsNotNone(revision)
        self.assertIn("test-service", revision)
    
    @patch.object(DeploymentManager, 'run_command')
    def test_update_traffic(self, mock_run_command):
        """トラフィック更新テスト"""
        mock_run_command.return_value = (True, "Traffic updated", "")
        
        result = self.deployment_manager.update_traffic("test-revision", 50)
        
        self.assertTrue(result)

class TestRevisionManager(unittest.TestCase):
    """リビジョンマネージャーのテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.revision_manager = RevisionManager("test-service", "asia-northeast1")
    
    @patch.object(RevisionManager, 'run_command')
    def test_get_current_revision(self, mock_run_command):
        """現在のリビジョン取得テスト"""
        mock_run_command.return_value = (True, "test-service-current", "")
        
        revision = self.revision_manager.get_current_revision()
        
        self.assertEqual(revision, "test-service-current")
    
    @patch.object(RevisionManager, 'run_command')
    def test_get_cloud_run_revisions(self, mock_run_command):
        """Cloud Runリビジョン一覧取得テスト"""
        mock_revisions = [
            {"metadata": {"name": "test-service-rev1"}},
            {"metadata": {"name": "test-service-rev2"}}
        ]
        mock_run_command.return_value = (True, json.dumps(mock_revisions), "")
        
        revisions = self.revision_manager.get_cloud_run_revisions()
        
        self.assertEqual(len(revisions), 2)
        self.assertIn("test-service-rev1", revisions)
        self.assertIn("test-service-rev2", revisions)
    
    @patch.object(RevisionManager, 'run_command')
    def test_is_revision_healthy(self, mock_run_command):
        """リビジョン健全性チェックテスト"""
        mock_revision_info = {
            "status": {
                "conditions": [
                    {"type": "Ready", "status": "True"}
                ]
            }
        }
        mock_run_command.return_value = (True, json.dumps(mock_revision_info), "")
        
        result = self.revision_manager.is_revision_healthy("test-revision")
        
        self.assertTrue(result)

class TestPostDeploymentMonitor(unittest.TestCase):
    """デプロイメント後監視のテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.monitor = PostDeploymentMonitor("test-service", "asia-northeast1")
    
    @patch('requests.get')
    def test_health_check(self, mock_get):
        """ヘルスチェックテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.monitor.health_check("https://test.example.com")
        
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["status_code"], 200)
        self.assertIsNotNone(result["response_time"])
    
    @patch.object(PostDeploymentMonitor, 'run_command')
    def test_get_error_rate(self, mock_run_command):
        """エラー率取得テスト"""
        # エラーログ
        mock_run_command.side_effect = [
            (True, json.dumps([{"severity": "ERROR"}] * 5), ""),  # 5件のエラー
            (True, json.dumps([{"log": "entry"}] * 100), "")     # 100件の総ログ
        ]
        
        error_rate = self.monitor.get_error_rate()
        
        self.assertEqual(error_rate, 0.05)  # 5/100 = 5%
    
    def test_check_thresholds(self):
        """閾値チェックテスト"""
        metrics = {
            "error_rate": 0.1,  # 10% (閾値5%を超過)
            "response_time_p95": 2000,  # 2000ms (閾値1200msを超過)
            "cpu_utilization": 0.9,  # 90% (閾値80%を超過)
            "memory_utilization": 0.7,  # 70% (閾値内)
            "health_status": "unhealthy"
        }
        
        alerts = self.monitor.check_thresholds(metrics)
        
        # エラー率、レスポンス時間、CPU使用率、ヘルスステータスでアラート
        self.assertEqual(len(alerts), 4)
        
        # エラー率アラートの確認
        error_rate_alert = next((a for a in alerts if a["type"] == "error_rate"), None)
        self.assertIsNotNone(error_rate_alert)
        self.assertEqual(error_rate_alert["severity"], "critical")

class TestDeploymentStatusManager(unittest.TestCase):
    """デプロイメント状況管理のテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.status_manager = DeploymentStatusManager("test-project")
    
    def test_update_deployment_status(self):
        """デプロイメント状況更新テスト"""
        deployment_data = {
            "deployment_id": "test-deploy-123",
            "service_name": "test-service",
            "revision": "test-revision",
            "image_url": "gcr.io/test/image:latest",
            "commit_sha": "abc123",
            "status": "DEPLOY_SUCCESS",
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.status_manager.update_deployment_status(deployment_data)
        
        self.assertTrue(result)
        
        # ファイルが作成されたことを確認
        filename = f"deployment_status_{deployment_data['deployment_id']}.json"
        self.assertTrue(os.path.exists(filename))
        
        # クリーンアップ
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_get_deployment_statistics(self):
        """デプロイメント統計取得テスト"""
        # テスト用のデプロイメント記録を作成
        test_deployments = [
            {
                "service_name": "test-service",
                "status": "DEPLOY_SUCCESS",
                "timestamp": datetime.now().isoformat()
            },
            {
                "service_name": "test-service", 
                "status": "DEPLOY_FAILED",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # テストファイル作成
        test_files = []
        for i, deployment in enumerate(test_deployments):
            filename = f"deployment_status_test_{i}.json"
            with open(filename, "w") as f:
                json.dump(deployment, f)
            test_files.append(filename)
        
        try:
            statistics = self.status_manager.get_deployment_statistics("test-service")
            
            self.assertEqual(statistics["service_name"], "test-service")
            self.assertEqual(statistics["total_deployments"], 2)
            self.assertEqual(statistics["successful_deployments"], 1)
            self.assertEqual(statistics["failed_deployments"], 1)
            self.assertEqual(statistics["success_rate"], 0.5)
            
        finally:
            # クリーンアップ
            for filename in test_files:
                if os.path.exists(filename):
                    os.remove(filename)

class TestDeploymentReportGenerator(unittest.TestCase):
    """デプロイメントレポート生成のテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.report_generator = DeploymentReportGenerator("test-service", "asia-northeast1")
    
    @patch.object(DeploymentReportGenerator, 'run_command')
    def test_get_current_service_info(self, mock_run_command):
        """現在のサービス情報取得テスト"""
        mock_service_info = {
            "status": {
                "url": "https://test-service.example.com",
                "latestReadyRevisionName": "test-service-12345"
            },
            "metadata": {
                "creationTimestamp": "2024-01-01T00:00:00Z"
            }
        }
        mock_run_command.return_value = (True, json.dumps(mock_service_info), "")
        
        service_info = self.report_generator.get_current_service_info()
        
        self.assertEqual(service_info["service_name"], "test-service")
        self.assertEqual(service_info["url"], "https://test-service.example.com")
        self.assertEqual(service_info["latest_revision"], "test-service-12345")
    
    def test_assess_deployment_health(self):
        """デプロイメント健全性評価テスト"""
        mock_report = {
            "service_info": {"url": "https://test.example.com"},
            "revision_details": {"ready": True, "serving": True},
            "metrics": {
                "last_1_hour": {"error_rate": 0.005}  # 0.5%
            },
            "performance": {
                "response_time": {"p95": 800}  # 800ms
            }
        }
        
        assessment = self.report_generator.assess_deployment_health(mock_report)
        
        self.assertEqual(assessment["overall_status"], "excellent")
        self.assertEqual(assessment["score"], 100)
        self.assertEqual(assessment["checks"]["service_availability"], "pass")
        self.assertEqual(assessment["checks"]["revision_health"], "pass")
        self.assertEqual(assessment["checks"]["error_rate"], "pass")
        self.assertEqual(assessment["checks"]["performance"], "pass")

class TestCICDIntegration(unittest.TestCase):
    """CI/CD統合テストクラス"""
    
    def test_deployment_workflow(self):
        """デプロイメントワークフローテスト"""
        # 1. デプロイメントマネージャー初期化
        deployment_manager = DeploymentManager(
            project_id="test-project",
            service_name="test-service"
        )
        
        # 2. リビジョンマネージャー初期化
        revision_manager = RevisionManager("test-service")
        
        # 3. 監視マネージャー初期化
        monitor = PostDeploymentMonitor("test-service")
        
        # 4. 状況管理マネージャー初期化
        status_manager = DeploymentStatusManager("test-project")
        
        # 5. レポート生成マネージャー初期化
        report_generator = DeploymentReportGenerator("test-service")
        
        # 各コンポーネントが正常に初期化されることを確認
        self.assertIsNotNone(deployment_manager)
        self.assertIsNotNone(revision_manager)
        self.assertIsNotNone(monitor)
        self.assertIsNotNone(status_manager)
        self.assertIsNotNone(report_generator)
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        deployment_manager = DeploymentManager(
            project_id="invalid-project",
            service_name="invalid-service"
        )
        
        # 無効なプロジェクト/サービスでもエラーが適切に処理されることを確認
        with patch.object(deployment_manager, 'run_command') as mock_run_command:
            mock_run_command.return_value = (False, "", "Project not found")
            
            revision = deployment_manager.get_current_revision()
            self.assertIsNone(revision)
    
    def test_configuration_validation(self):
        """設定検証テスト"""
        # 必要な設定ファイルが存在することを確認
        config_files = [
            ".github/workflows/ci-cd-pipeline.yml",
            "infrastructure/production/deploy_script.py",
            "infrastructure/production/get_last_stable_revision.py",
            "infrastructure/production/post_deployment_monitoring.py"
        ]
        
        for config_file in config_files:
            self.assertTrue(os.path.exists(config_file), f"設定ファイル {config_file} が存在しません")

def run_ci_cd_tests():
    """CI/CDテストの実行"""
    print("CI/CDパイプラインテストを開始...")
    
    # テストスイート作成
    test_suite = unittest.TestSuite()
    
    # テスト追加
    test_suite.addTest(unittest.makeSuite(TestDeploymentManager))
    test_suite.addTest(unittest.makeSuite(TestRevisionManager))
    test_suite.addTest(unittest.makeSuite(TestPostDeploymentMonitor))
    test_suite.addTest(unittest.makeSuite(TestDeploymentStatusManager))
    test_suite.addTest(unittest.makeSuite(TestDeploymentReportGenerator))
    test_suite.addTest(unittest.makeSuite(TestCICDIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print(f"\n{'='*80}")
    print("CI/CDパイプラインテスト結果")
    print(f"{'='*80}")
    print(f"実行テスト数: {result.testsRun}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print(f"スキップ: {len(result.skipped)}")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            error_lines = traceback.split('\n')
            error_msg = error_lines[-2] if len(error_lines) > 1 else str(traceback)
            print(f"- {test}: {error_msg}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n全体結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    return success

if __name__ == "__main__":
    success = run_ci_cd_tests()
    sys.exit(0 if success else 1)