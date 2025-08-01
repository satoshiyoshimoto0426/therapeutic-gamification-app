#!/usr/bin/env python3
"""
本番環境設定検証のテストスクリプト
"""

import unittest
import json
import os
import sys
import yaml
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# テスト対象のインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from production_config_validator import ProductionConfigValidator

class TestProductionConfigValidator(unittest.TestCase):
    """本番環境設定検証のテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.project_id = "test-therapeutic-app"
        self.validator = ProductionConfigValidator(self.project_id)
    
    def test_init(self):
        """初期化テスト"""
        self.assertEqual(self.validator.project_id, self.project_id)
        self.assertIn("timestamp", self.validator.validation_results)
        self.assertIn("validations", self.validator.validation_results)
        self.assertEqual(self.validator.validation_results["overall_status"], "UNKNOWN")
    
    @patch('subprocess.run')
    def test_run_gcloud_command_success(self, mock_run):
        """gcloudコマンド実行成功テスト"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, stdout, stderr = self.validator.run_gcloud_command(["gcloud", "test"])
        
        self.assertTrue(success)
        self.assertEqual(stdout, "success output")
        self.assertEqual(stderr, "")
    
    @patch('subprocess.run')
    def test_run_gcloud_command_failure(self, mock_run):
        """gcloudコマンド実行失敗テスト"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error output"
        mock_run.return_value = mock_result
        
        success, stdout, stderr = self.validator.run_gcloud_command(["gcloud", "test"])
        
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error output")
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_project_setup_success(self, mock_gcloud):
        """プロジェクト設定検証成功テスト"""
        # プロジェクト情報のモック
        project_info = {
            "projectId": self.project_id,
            "projectNumber": "123456789",
            "lifecycleState": "ACTIVE"
        }
        
        # API一覧のモック
        api_responses = [
            (True, json.dumps(project_info), ""),  # プロジェクト情報
            (True, "run.googleapis.com", ""),      # API確認
            (True, "firestore.googleapis.com", ""),
            (True, "storage.googleapis.com", ""),
            (True, "secretmanager.googleapis.com", ""),
            (True, "cloudkms.googleapis.com", ""),
            (True, "monitoring.googleapis.com", ""),
            (True, "logging.googleapis.com", ""),
            (True, "cloudbuild.googleapis.com", "")
        ]
        
        mock_gcloud.side_effect = api_responses
        
        result = self.validator.validate_project_setup()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results["validations"]["project"]["status"], "VALID")
        self.assertEqual(self.validator.validation_results["validations"]["apis"]["status"], "VALID")
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_project_setup_missing_apis(self, mock_gcloud):
        """プロジェクト設定検証（API不足）テスト"""
        project_info = {
            "projectId": self.project_id,
            "projectNumber": "123456789",
            "lifecycleState": "ACTIVE"
        }
        
        # 一部APIが無効な場合
        api_responses = [
            (True, json.dumps(project_info), ""),  # プロジェクト情報
            (True, "run.googleapis.com", ""),      # API確認
            (False, "", "API not enabled"),        # firestore無効
            (True, "storage.googleapis.com", ""),
            (False, "", "API not enabled"),        # secretmanager無効
            (True, "cloudkms.googleapis.com", ""),
            (True, "monitoring.googleapis.com", ""),
            (True, "logging.googleapis.com", ""),
            (True, "cloudbuild.googleapis.com", "")
        ]
        
        mock_gcloud.side_effect = api_responses
        
        result = self.validator.validate_project_setup()
        
        self.assertFalse(result)
        self.assertEqual(self.validator.validation_results["validations"]["apis"]["status"], "INVALID")
        self.assertGreater(len(self.validator.validation_results["errors"]), 0)
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_cloud_run_config_not_deployed(self, mock_gcloud):
        """Cloud Run設定検証（未デプロイ）テスト"""
        mock_gcloud.return_value = (True, "[]", "")  # 空のサービス一覧
        
        result = self.validator.validate_cloud_run_config()
        
        self.assertTrue(result)  # 未デプロイは警告のみ
        self.assertEqual(self.validator.validation_results["validations"]["cloud_run"]["status"], "NOT_DEPLOYED")
        self.assertGreater(len(self.validator.validation_results["warnings"]), 0)
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_cloud_run_config_deployed(self, mock_gcloud):
        """Cloud Run設定検証（デプロイ済み）テスト"""
        service_info = [{
            "metadata": {
                "name": "therapeutic-gamification-app",
                "labels": {"cloud.googleapis.com/location": "asia-northeast1"}
            },
            "status": {
                "url": "https://therapeutic-app.example.com",
                "conditions": [{"status": "True"}]
            }
        }]
        
        mock_gcloud.return_value = (True, json.dumps(service_info), "")
        
        result = self.validator.validate_cloud_run_config()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results["validations"]["cloud_run"]["status"], "VALID")
        self.assertEqual(self.validator.validation_results["validations"]["cloud_run"]["service_name"], "therapeutic-gamification-app")
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_firestore_config_success(self, mock_gcloud):
        """Firestore設定検証成功テスト"""
        database_info = [{
            "name": f"projects/{self.project_id}/databases/(default)",
            "locationId": "asia-northeast1",
            "type": "FIRESTORE_NATIVE"
        }]
        
        rules_info = [{"name": "rule1"}, {"name": "rule2"}]
        
        mock_gcloud.side_effect = [
            (True, json.dumps(database_info), ""),  # データベース一覧
            (True, json.dumps(rules_info), "")      # セキュリティルール
        ]
        
        result = self.validator.validate_firestore_config()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results["validations"]["firestore"]["status"], "VALID")
        self.assertEqual(self.validator.validation_results["validations"]["firestore"]["security_rules"]["status"], "CONFIGURED")
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_secret_manager_config_partial(self, mock_gcloud):
        """Secret Manager設定検証（部分的）テスト"""
        # 一部のシークレットのみ存在
        secret_responses = [
            (True, '{"name": "openai-api-key"}', ""),     # 存在
            (False, "", "Secret not found"),              # line-channel-secret不存在
            (True, '{"name": "jwt-secret"}', ""),         # 存在
            (False, "", "Secret not found")               # stripe-secret-key不存在
        ]
        
        mock_gcloud.side_effect = secret_responses
        
        result = self.validator.validate_secret_manager_config()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results["validations"]["secret_manager"]["status"], "PARTIAL")
        self.assertGreater(len(self.validator.validation_results["warnings"]), 0)
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_kms_config_not_configured(self, mock_gcloud):
        """KMS設定検証（未設定）テスト"""
        mock_gcloud.return_value = (True, "[]", "")  # 空のキーリング一覧
        
        result = self.validator.validate_kms_config()
        
        self.assertTrue(result)  # 未設定は警告のみ
        self.assertEqual(self.validator.validation_results["validations"]["kms"]["status"], "NOT_CONFIGURED")
        self.assertGreater(len(self.validator.validation_results["warnings"]), 0)
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_monitoring_config_configured(self, mock_gcloud):
        """監視設定検証（設定済み）テスト"""
        policies_info = [
            {"displayName": "Therapeutic App Performance Alerts"},
            {"displayName": "Therapeutic Safety Alerts"},
            {"displayName": "Other App Alerts"}
        ]
        
        mock_gcloud.return_value = (True, json.dumps(policies_info), "")
        
        result = self.validator.validate_monitoring_config()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results["validations"]["monitoring"]["status"], "CONFIGURED")
        self.assertEqual(self.validator.validation_results["validations"]["monitoring"]["alert_policies"], 2)
    
    @patch.object(ProductionConfigValidator, 'run_gcloud_command')
    def test_validate_iam_permissions_missing_sa(self, mock_gcloud):
        """IAM権限検証（サービスアカウント不存在）テスト"""
        mock_gcloud.return_value = (True, "[]", "")  # 空のサービスアカウント一覧
        
        result = self.validator.validate_iam_permissions()
        
        self.assertTrue(result)  # 警告のみ
        self.assertEqual(self.validator.validation_results["validations"]["iam"]["status"], "MISSING")
        self.assertGreater(len(self.validator.validation_results["warnings"]), 0)
    
    def test_run_full_validation_mock(self):
        """全体検証実行テスト（モック使用）"""
        # 各検証メソッドをモック
        with patch.multiple(
            self.validator,
            validate_project_setup=Mock(return_value=True),
            validate_cloud_run_config=Mock(return_value=True),
            validate_firestore_config=Mock(return_value=True),
            validate_secret_manager_config=Mock(return_value=True),
            validate_kms_config=Mock(return_value=True),
            validate_vpc_security_config=Mock(return_value=True),
            validate_monitoring_config=Mock(return_value=True),
            validate_logging_config=Mock(return_value=True),
            validate_iam_permissions=Mock(return_value=True),
            validate_security_settings=Mock(return_value=True)
        ):
            results = self.validator.run_full_validation()
            
            self.assertEqual(results["overall_status"], "READY")
            self.assertEqual(results["summary"]["successful_validations"], 10)
            self.assertEqual(results["summary"]["success_rate"], 1.0)
    
    def test_run_full_validation_partial_failure(self):
        """全体検証実行テスト（部分的失敗）"""
        # 一部の検証が失敗
        with patch.multiple(
            self.validator,
            validate_project_setup=Mock(return_value=True),
            validate_cloud_run_config=Mock(return_value=False),  # 失敗
            validate_firestore_config=Mock(return_value=True),
            validate_secret_manager_config=Mock(return_value=False),  # 失敗
            validate_kms_config=Mock(return_value=True),
            validate_vpc_security_config=Mock(return_value=True),
            validate_monitoring_config=Mock(return_value=True),
            validate_logging_config=Mock(return_value=True),
            validate_iam_permissions=Mock(return_value=True),
            validate_security_settings=Mock(return_value=True)
        ):
            results = self.validator.run_full_validation()
            
            self.assertEqual(results["overall_status"], "MOSTLY_READY")  # 80%成功
            self.assertEqual(results["summary"]["successful_validations"], 8)
            self.assertEqual(results["summary"]["success_rate"], 0.8)
    
    def test_generate_report(self):
        """レポート生成テスト"""
        # テスト用の検証結果を設定
        self.validator.validation_results = {
            "timestamp": "2024-01-01T12:00:00",
            "project_id": self.project_id,
            "overall_status": "READY",
            "validations": {
                "project": {"status": "VALID", "project_id": self.project_id},
                "cloud_run": {"status": "NOT_DEPLOYED", "message": "未デプロイ"}
            },
            "errors": ["テストエラー"],
            "warnings": ["テスト警告"],
            "summary": {
                "total_validations": 10,
                "successful_validations": 9,
                "success_rate": 0.9,
                "error_count": 1,
                "warning_count": 1
            }
        }
        
        report = self.validator.generate_report()
        
        self.assertIn("本番環境設定検証レポート", report)
        self.assertIn(self.project_id, report)
        self.assertIn("READY", report)
        self.assertIn("90.0%", report)
        self.assertIn("テストエラー", report)
        self.assertIn("テスト警告", report)
    
    def test_validation_results_structure(self):
        """検証結果構造テスト"""
        required_keys = [
            "timestamp", "project_id", "validations", 
            "errors", "warnings", "overall_status"
        ]
        
        for key in required_keys:
            self.assertIn(key, self.validator.validation_results)
        
        self.assertIsInstance(self.validator.validation_results["validations"], dict)
        self.assertIsInstance(self.validator.validation_results["errors"], list)
        self.assertIsInstance(self.validator.validation_results["warnings"], list)

class TestProductionConfigIntegration(unittest.TestCase):
    """本番環境設定統合テストクラス"""
    
    def setUp(self):
        """統合テストセットアップ"""
        self.project_id = "test-therapeutic-app-integration"
    
    @unittest.skipUnless(os.getenv("RUN_INTEGRATION_TESTS"), "統合テストはRUN_INTEGRATION_TESTS環境変数が設定されている場合のみ実行")
    def test_real_gcloud_command(self):
        """実際のgcloudコマンドテスト"""
        validator = ProductionConfigValidator(self.project_id)
        
        # プロジェクト一覧取得（実際のコマンド）
        success, stdout, stderr = validator.run_gcloud_command([
            "gcloud", "projects", "list", "--format=json", "--limit=1"
        ])
        
        # gcloudが正しくインストールされていれば成功するはず
        if success:
            self.assertTrue(success)
            self.assertIsInstance(json.loads(stdout), list)
        else:
            self.skipTest("gcloudコマンドが利用できません")
    
    def test_config_file_validation(self):
        """設定ファイル検証テスト"""
        config_files = [
            "cloud-run.yaml",
            "firestore-security-rules.js",
            "secret-manager-kms.yaml",
            "vpc-security-config.yaml",
            "cloud-armor-waf.yaml",
            "iam-conditions.yaml",
            "monitoring-config.yaml",
            "logging-config.yaml",
            "alerting-config.yaml"
        ]
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        for config_file in config_files:
            file_path = os.path.join(base_path, config_file)
            self.assertTrue(os.path.exists(file_path), f"設定ファイル {config_file} が存在しません")
            
            # ファイルサイズチェック（空でないこと）
            self.assertGreater(os.path.getsize(file_path), 0, f"設定ファイル {config_file} が空です")
    
    def test_yaml_config_syntax(self):
        """YAML設定ファイル構文テスト"""
        yaml_files = [
            "cloud-run.yaml",
            "secret-manager-kms.yaml", 
            "vpc-security-config.yaml",
            "cloud-armor-waf.yaml",
            "iam-conditions.yaml",
            "monitoring-config.yaml",
            "logging-config.yaml",
            "alerting-config.yaml"
        ]
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        for yaml_file in yaml_files:
            file_path = os.path.join(base_path, yaml_file)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 複数ドキュメント対応
                        for document in yaml.safe_load_all(f):
                            pass  # ドキュメントが正常に読み込めることを確認
                except yaml.YAMLError as e:
                    self.fail(f"YAML構文エラー in {yaml_file}: {e}")
    
    def test_security_config_completeness(self):
        """セキュリティ設定完全性テスト"""
        # 必要なセキュリティ設定項目
        required_security_items = [
            "VPC-SC",
            "IAM Conditions", 
            "Cloud Armor WAF",
            "Secret Manager KMS",
            "Firestore Security Rules"
        ]
        
        # 各設定ファイルの存在確認
        base_path = os.path.dirname(os.path.abspath(__file__))
        security_files = {
            "VPC-SC": "vpc-security-config.yaml",
            "IAM Conditions": "iam-conditions.yaml",
            "Cloud Armor WAF": "cloud-armor-waf.yaml", 
            "Secret Manager KMS": "secret-manager-kms.yaml",
            "Firestore Security Rules": "firestore-security-rules.js"
        }
        
        for item, filename in security_files.items():
            file_path = os.path.join(base_path, filename)
            self.assertTrue(os.path.exists(file_path), f"セキュリティ設定 {item} のファイル {filename} が存在しません")

def run_production_validation_tests():
    """本番環境設定検証テストの実行"""
    print("本番環境設定検証テストを開始...")
    
    # テストスイート作成
    test_suite = unittest.TestSuite()
    
    # 単体テスト追加
    test_suite.addTest(unittest.makeSuite(TestProductionConfigValidator))
    test_suite.addTest(unittest.makeSuite(TestProductionConfigIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print(f"\n{'='*80}")
    print("本番環境設定検証テスト結果")
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
    success = run_production_validation_tests()
    sys.exit(0 if success else 1)