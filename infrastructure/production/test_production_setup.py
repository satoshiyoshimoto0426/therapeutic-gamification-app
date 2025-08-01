#!/usr/bin/env python3
"""
本番環境インフラストラクチャ設定のテスト

このテストは本番環境設定の検証を行います。
- Cloud Run設定の検証
- Firestore セキュリティルールの検証
- VPC-SC設定の検証
- Cloud Armor WAF設定の検証
- Secret Manager KMS設定の検証
- IAM Conditions設定の検証
"""

import unittest
import json
import os
from typing import Dict, Any, List
import re


class TestProductionInfrastructure(unittest.TestCase):
    """本番環境インフラストラクチャ設定のテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        self.infrastructure_path = "infrastructure/production"
        
    def test_cloud_run_configuration(self):
        """Cloud Run設定の検証"""
        config_path = f"{self.infrastructure_path}/cloud-run.yaml"
        self.assertTrue(os.path.exists(config_path), "Cloud Run設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 基本設定の検証
        self.assertIn('kind: Service', config_content)
        self.assertIn('name: therapeutic-gamification-app', config_content)
        
        # セキュリティ設定の検証
        self.assertIn('run.googleapis.com/vpc-access-connector', config_content)
        self.assertIn('run.googleapis.com/vpc-access-egress', config_content)
        self.assertIn('private-ranges-only', config_content)
        
        # リソース制限の検証
        self.assertIn('memory: "2Gi"', config_content)
        self.assertIn('cpu: "2"', config_content)
        
        # 環境変数の検証
        env_vars = ['ENVIRONMENT', 'PROJECT_ID', 'FIRESTORE_DATABASE']
        for env_var in env_vars:
            self.assertIn(f'name: {env_var}', config_content)
        
        # Secret Manager統合の検証
        secret_vars = ['OPENAI_API_KEY', 'LINE_CHANNEL_SECRET', 'JWT_SECRET', 'STRIPE_SECRET_KEY']
        for secret_var in secret_vars:
            self.assertIn(f'name: {secret_var}', config_content)
            self.assertIn('valueFrom:', config_content)
            self.assertIn('secretKeyRef:', config_content)
        
        # ヘルスチェックの検証
        self.assertIn('livenessProbe:', config_content)
        self.assertIn('readinessProbe:', config_content)
        self.assertIn('path: /health', config_content)
        self.assertIn('path: /ready', config_content)
        
        print("✅ Cloud Run設定の検証完了")
    
    def test_firestore_security_rules(self):
        """Firestoreセキュリティルールの検証"""
        rules_path = f"{self.infrastructure_path}/firestore-security-rules.js"
        self.assertTrue(os.path.exists(rules_path), "Firestoreセキュリティルールファイルが存在しません")
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        # 基本構造の検証
        self.assertIn("rules_version = '2'", rules_content)
        self.assertIn("service cloud.firestore", rules_content)
        
        # 重要なコレクションのルール存在確認
        required_collections = [
            'user_profiles',
            'tasks',
            'story_states',
            'mood_logs',
            'mandala_grids',
            'guardian_permissions',
            'safety_logs',
            'performance_metrics'
        ]
        
        for collection in required_collections:
            self.assertIn(f"match /{collection}/", rules_content)
        
        # 認証チェックの存在確認
        self.assertIn("request.auth != null", rules_content)
        self.assertIn("request.auth.uid", rules_content)
        
        # Guardian権限チェックの存在確認
        self.assertIn("guardian_permissions", rules_content)
        self.assertIn("view-only", rules_content)
        self.assertIn("task-edit", rules_content)
        
        # データ検証関数の存在確認
        self.assertIn("function isValidUserData", rules_content)
        self.assertIn("function isValidTaskData", rules_content)
        
        # レート制限の存在確認
        self.assertIn("checkRateLimit", rules_content)
        
        print("✅ Firestoreセキュリティルールの検証完了")
    
    def test_vpc_security_configuration(self):
        """VPC-SC設定の検証"""
        config_path = f"{self.infrastructure_path}/vpc-security-config.yaml"
        self.assertTrue(os.path.exists(config_path), "VPC-SC設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # AccessPolicy設定の検証
        self.assertIn('kind: AccessPolicy', config_content)
        
        # ServicePerimeter設定の検証
        self.assertIn('kind: ServicePerimeter', config_content)
        
        # 制限されるサービスの検証
        required_services = [
            'firestore.googleapis.com',
            'storage.googleapis.com',
            'run.googleapis.com',
            'secretmanager.googleapis.com',
            'cloudkms.googleapis.com'
        ]
        
        for service in required_services:
            self.assertIn(service, config_content)
        
        # AccessLevel設定の検証
        self.assertIn('kind: AccessLevel', config_content)
        
        # 地域制限の検証
        self.assertIn('regions:', config_content)
        self.assertIn('- "JP"', config_content)
        
        print("✅ VPC-SC設定の検証完了")
    
    def test_cloud_armor_waf_configuration(self):
        """Cloud Armor WAF設定の検証"""
        config_path = f"{self.infrastructure_path}/cloud-armor-waf.yaml"
        self.assertTrue(os.path.exists(config_path), "Cloud Armor WAF設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 基本設定の検証
        self.assertIn('kind: SecurityPolicy', config_content)
        self.assertIn('name: therapeutic-app-security-policy', config_content)
        
        # 重要なルールの検証
        self.assertIn('priority: 2147483647', config_content)  # デフォルトルール
        self.assertIn('priority: 1100', config_content)  # レート制限
        self.assertIn('priority: 1200', config_content)  # SQLインジェクション保護
        self.assertIn('priority: 1300', config_content)  # XSS保護
        self.assertIn('priority: 1400', config_content)  # ストーリーAPI保護
        self.assertIn('priority: 1500', config_content)  # Guardian API保護
        
        # レート制限設定の検証
        self.assertIn('action: "rate_based_ban"', config_content)
        self.assertIn('count: 120', config_content)
        self.assertIn('intervalSec: 60', config_content)
        
        # セキュリティ保護の検証
        self.assertIn('sqli-stable', config_content)
        self.assertIn('xss-stable', config_content)
        
        # 治療アプリ特有の保護
        self.assertIn('/api/story/', config_content)
        self.assertIn('/api/guardian/', config_content)
        
        # アダプティブ保護設定の検証
        self.assertIn('adaptiveProtectionConfig:', config_content)
        self.assertIn('layer7DdosDefenseConfig:', config_content)
        
        print("✅ Cloud Armor WAF設定の検証完了")
    
    def test_secret_manager_kms_configuration(self):
        """Secret Manager KMS設定の検証"""
        config_path = f"{self.infrastructure_path}/secret-manager-kms.yaml"
        self.assertTrue(os.path.exists(config_path), "Secret Manager KMS設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Secret設定の検証
        required_secrets = ['openai-api-key', 'line-channel-secret', 'jwt-secret', 'stripe-secret-key']
        for required_secret in required_secrets:
            self.assertIn(f'name: {required_secret}', config_content)
        
        # 基本設定の検証
        self.assertIn('kind: Secret', config_content)
        self.assertIn('replication:', config_content)
        self.assertIn('userManaged:', config_content)
        self.assertIn('customerManagedEncryption:', config_content)
        self.assertIn('kmsKeyName:', config_content)
        
        # KeyRing設定の検証
        self.assertIn('kind: KeyRing', config_content)
        self.assertIn('name: therapeutic-app-keyring', config_content)
        
        # CryptoKey設定の検証
        self.assertIn('kind: CryptoKey', config_content)
        required_keys = ['openai-key', 'line-key', 'jwt-key', 'stripe-key']
        for required_key in required_keys:
            self.assertIn(f'name: {required_key}', config_content)
        
        # キーローテーション設定の検証
        self.assertIn('rotationPeriod:', config_content)
        self.assertIn('2592000s', config_content)  # 30日（JWT用）
        self.assertIn('7776000s', config_content)  # 90日（その他）
        
        print("✅ Secret Manager KMS設定の検証完了")
    
    def test_iam_conditions_configuration(self):
        """IAM Conditions設定の検証"""
        config_path = f"{self.infrastructure_path}/iam-conditions.yaml"
        self.assertTrue(os.path.exists(config_path), "IAM Conditions設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Policy設定の検証
        self.assertIn('kind: Policy', config_content)
        
        # 重要なロールの存在確認
        required_roles = [
            'roles/run.invoker',
            'roles/datastore.user',
            'roles/storage.objectAdmin',
            'roles/secretmanager.secretAccessor',
            'roles/monitoring.metricWriter',
            'roles/logging.logWriter'
        ]
        
        for required_role in required_roles:
            self.assertIn(required_role, config_content)
        
        # 条件付きアクセスの検証
        self.assertIn('condition:', config_content)
        self.assertIn('expression:', config_content)
        
        # Guardian権限の時間・地域制限確認
        self.assertIn('therapeutic-app-guardians', config_content)
        self.assertIn('origin.region_code == "JP"', config_content)
        self.assertIn('request.time.getHours()', config_content)
        
        # ServiceAccount設定の検証
        self.assertIn('kind: ServiceAccount', config_content)
        self.assertIn('name: therapeutic-app-service-account', config_content)
        
        # カスタムロール設定の検証
        self.assertIn('kind: Role', config_content)
        self.assertIn('name: therapeutic.app.operator', config_content)
        
        # 必要な権限の確認
        required_permissions = [
            'firestore.documents.create',
            'firestore.documents.get',
            'storage.objects.create',
            'secretmanager.versions.access',
            'monitoring.timeSeries.create',
            'logging.logEntries.create'
        ]
        
        for required_permission in required_permissions:
            self.assertIn(required_permission, config_content)
        
        print("✅ IAM Conditions設定の検証完了")
    
    def test_cloud_storage_configuration(self):
        """Cloud Storage設定の検証"""
        config_path = f"{self.infrastructure_path}/cloud-storage-config.yaml"
        self.assertTrue(os.path.exists(config_path), "Cloud Storage設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Bucket設定の検証
        self.assertIn('kind: Bucket', config_content)
        required_buckets = [
            'therapeutic-app-storage-prod',
            'therapeutic-app-user-data-prod',
            'therapeutic-app-backup-prod',
            'therapeutic-app-access-logs-prod'
        ]
        
        for required_bucket in required_buckets:
            self.assertIn(f'name: {required_bucket}', config_content)
        
        # 基本設定の検証
        self.assertIn('location: asia-northeast1', config_content)
        self.assertIn('storageClass: STANDARD', config_content)
        self.assertIn('storageClass: COLDLINE', config_content)
        
        # バージョニング設定
        self.assertIn('versioning:', config_content)
        self.assertIn('enabled: true', config_content)
        
        # ライフサイクル設定
        self.assertIn('lifecycle:', config_content)
        self.assertIn('rule:', config_content)
        self.assertIn('age: 2555', config_content)  # 7年保持
        self.assertIn('age: 7', config_content)     # 1週間（ユーザーデータ）
        self.assertIn('age: 30', config_content)    # 1ヶ月
        
        # 暗号化設定
        self.assertIn('encryption:', config_content)
        self.assertIn('defaultKmsKeyName:', config_content)
        
        # CORS設定
        self.assertIn('cors:', config_content)
        
        # IAM設定
        self.assertIn('iamConfiguration:', config_content)
        self.assertIn('uniformBucketLevelAccess:', config_content)
        self.assertIn('publicAccessPrevention: enforced', config_content)
        
        # ラベル設定の確認
        self.assertIn('data-classification: personal', config_content)
        self.assertIn('gdpr-applicable: true', config_content)
        
        print("✅ Cloud Storage設定の検証完了")
    
    def test_deployment_script_validation(self):
        """デプロイメントスクリプトの検証"""
        script_path = f"{self.infrastructure_path}/deployment-script.sh"
        self.assertTrue(os.path.exists(script_path), "デプロイメントスクリプトが存在しません")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 基本構造の検証
        self.assertIn('#!/bin/bash', script_content)
        self.assertIn('set -euo pipefail', script_content)
        
        # 重要なステップの存在確認
        required_steps = [
            'gcloud config set project',
            'gcloud services enable',
            'gcloud kms keyrings create',
            'gcloud secrets create',
            'gcloud iam service-accounts create',
            'gcloud projects add-iam-policy-binding',
            'gsutil mb',
            'gcloud firestore databases create',
            'gcloud compute networks vpc-access connectors create',
            'gcloud compute security-policies create',
            'gcloud builds submit',
            'gcloud run deploy'
        ]
        
        for step in required_steps:
            self.assertIn(step, script_content)
        
        # 必要なAPIの有効化確認
        required_apis = [
            'run.googleapis.com',
            'firestore.googleapis.com',
            'storage.googleapis.com',
            'secretmanager.googleapis.com',
            'cloudkms.googleapis.com',
            'monitoring.googleapis.com',
            'logging.googleapis.com'
        ]
        
        for api in required_apis:
            self.assertIn(api, script_content)
        
        # セキュリティ設定の確認
        self.assertIn('--vpc-connector', script_content)
        self.assertIn('--vpc-egress private-ranges-only', script_content)
        self.assertIn('--security-policy', script_content)
        
        # エラーハンドリングの確認
        self.assertIn('|| echo', script_content)  # エラー時の継続処理
        
        print("✅ デプロイメントスクリプトの検証完了")
    
    def test_security_compliance(self):
        """セキュリティコンプライアンスの検証"""
        # 要件16.2, 16.4の検証
        
        # 1. 地域ロック設定の確認
        vpc_config_path = f"{self.infrastructure_path}/vpc-security-config.yaml"
        with open(vpc_config_path, 'r', encoding='utf-8') as f:
            vpc_content = f.read()
        
        self.assertIn('kind: AccessLevel', vpc_content)
        self.assertIn('- "JP"', vpc_content, "日本地域制限が設定されていません")
        
        # 2. 16文字メッセージハッシュ設定の確認（概念的検証）
        # 実際の実装では、アプリケーションコードでハッシュ化を行う
        
        # 3. VPC-SC設定の確認
        self.assertIn('kind: ServicePerimeter', vpc_content)
        required_protected_services = [
            'firestore.googleapis.com',
            'storage.googleapis.com',
            'secretmanager.googleapis.com',
            'cloudkms.googleapis.com'
        ]
        
        for service in required_protected_services:
            self.assertIn(service, vpc_content, f"{service}がVPC-SCで保護されていません")
        
        # 4. IAM Conditions設定の確認
        iam_config_path = f"{self.infrastructure_path}/iam-conditions.yaml"
        with open(iam_config_path, 'r', encoding='utf-8') as f:
            iam_content = f.read()
        
        # 条件付きアクセスの確認
        self.assertIn('condition:', iam_content, "条件付きアクセス制御が設定されていません")
        
        # 5. Cloud Armor WAF設定の確認
        waf_config_path = f"{self.infrastructure_path}/cloud-armor-waf.yaml"
        with open(waf_config_path, 'r', encoding='utf-8') as f:
            waf_content = f.read()
        
        # 地域制限ルールの確認
        self.assertIn('priority: 1000', waf_content, "地域制限ルールが設定されていません")
        
        # レート制限の確認
        self.assertIn('priority: 1100', waf_content, "レート制限が設定されていません")
        self.assertIn('count: 120', waf_content)
        
        # 6. Secret Manager KMS設定の確認
        kms_config_path = f"{self.infrastructure_path}/secret-manager-kms.yaml"
        with open(kms_config_path, 'r', encoding='utf-8') as f:
            kms_content = f.read()
        
        self.assertIn('customerManagedEncryption:', kms_content, "KMS暗号化が設定されていません")
        
        print("✅ セキュリティコンプライアンスの検証完了")


def run_infrastructure_tests():
    """インフラストラクチャテストの実行"""
    print("🧪 本番環境インフラストラクチャ設定テスト開始")
    
    # テストスイートの作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestProductionInfrastructure)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果の表示
    if result.wasSuccessful():
        print("\n✅ 全てのインフラストラクチャテストが成功しました")
        print(f"実行テスト数: {result.testsRun}")
        return True
    else:
        print(f"\n❌ {len(result.failures)} 個のテストが失敗しました")
        print(f"❌ {len(result.errors)} 個のエラーが発生しました")
        
        # 失敗詳細の表示
        for test, traceback in result.failures:
            print(f"\n失敗: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nエラー: {test}")
            print(traceback)
        
        return False


if __name__ == "__main__":
    success = run_infrastructure_tests()
    exit(0 if success else 1)