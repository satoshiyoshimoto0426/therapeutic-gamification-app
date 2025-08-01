#!/usr/bin/env python3
"""
監視・ログ・アラートシステム設定のテスト

このテストは監視システム設定の検証を行います。
- 監視設定の検証
- ログ設定の検証
- アラート設定の検証
- ダッシュボード設定の検証
- 治療安全性メトリクス監視の検証
"""

import unittest
import json
import os
from typing import Dict, Any, List
import re


class TestMonitoringSetup(unittest.TestCase):
    """監視・ログ・アラートシステム設定のテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        self.infrastructure_path = "infrastructure/production"
        
    def test_monitoring_configuration(self):
        """監視設定の検証"""
        config_path = f"{self.infrastructure_path}/monitoring-config.yaml"
        self.assertTrue(os.path.exists(config_path), "監視設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 基本設定の検証
        self.assertIn('kind: AlertPolicy', config_content)
        self.assertIn('name: therapeutic-app-performance-alerts', config_content)
        self.assertIn('name: therapeutic-safety-alerts', config_content)
        
        # パフォーマンス監視の検証
        self.assertIn('API Response Time P95 > 1.2s', config_content)
        self.assertIn('thresholdValue: 1200', config_content)  # 1.2秒
        self.assertIn('Error Rate > 1%', config_content)
        self.assertIn('Memory Usage > 80%', config_content)
        self.assertIn('CPU Usage > 70%', config_content)
        self.assertIn('Concurrent Users > 18000', config_content)
        
        # 治療安全性監視の検証
        self.assertIn('Safety F1 Score < 98%', config_content)
        self.assertIn('thresholdValue: 0.98', config_content)  # 98%
        self.assertIn('Self-harm Detection Failures', config_content)
        self.assertIn('CBT Intervention Failures', config_content)
        self.assertIn('Moderation API Failures', config_content)
        
        # アップタイムチェックの検証
        self.assertIn('kind: UptimeCheckConfig', config_content)
        self.assertIn('path: "/health"', config_content)
        self.assertIn('port: 443', config_content)
        self.assertIn('useSsl: true', config_content)
        
        # カスタムメトリクスの検証
        self.assertIn('kind: MetricDescriptor', config_content)
        self.assertIn('therapeutic/safety/f1_score', config_content)
        self.assertIn('therapeutic/user/engagement_score', config_content)
        self.assertIn('therapeutic/task/completion_rate', config_content)
        
        # 通知チャンネルの検証
        self.assertIn('notificationChannels:', config_content)
        self.assertIn('SLACK_CHANNEL_ID', config_content)
        self.assertIn('EMAIL_CHANNEL_ID', config_content)
        self.assertIn('SMS_CHANNEL_ID', config_content)
        
        print("✅ 監視設定の検証完了")
    
    def test_logging_configuration(self):
        """ログ設定の検証"""
        config_path = f"{self.infrastructure_path}/logging-config.yaml"
        self.assertTrue(os.path.exists(config_path), "ログ設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 基本設定の検証
        self.assertIn('kind: LogSink', config_content)
        self.assertIn('kind: LogMetric', config_content)
        self.assertIn('kind: LogBucket', config_content)
        
        # ログシンクの検証
        required_sinks = [
            'therapeutic-app-audit-logs',
            'therapeutic-app-error-logs',
            'therapeutic-safety-logs',
            'therapeutic-performance-logs'
        ]
        
        for sink in required_sinks:
            self.assertIn(f'name: {sink}', config_content)
        
        # 監査ログフィルターの検証
        audit_events = [
            'user_authentication',
            'guardian_access',
            'data_access',
            'safety_violation',
            'cbt_intervention',
            'task_completion',
            'story_generation'
        ]
        
        for event in audit_events:
            self.assertIn(event, config_content)
        
        # ログベースメトリクスの検証
        self.assertIn('therapeutic-safety-f1-score-metric', config_content)
        self.assertIn('therapeutic-api-latency-metric', config_content)
        self.assertIn('therapeutic-user-engagement-metric', config_content)
        
        # BigQuery出力設定の検証
        self.assertIn('bigquery.googleapis.com', config_content)
        self.assertIn('usePartitionedTables: true', config_content)
        self.assertIn('usesTimestampColumnPartitioning: true', config_content)
        
        # ログ保持ポリシーの検証
        self.assertIn('retentionDays: 2555', config_content)  # 7年保持
        
        # プライバシー設定の検証
        self.assertIn('restrictedFields:', config_content)
        self.assertIn('user_id', config_content)
        self.assertIn('personal_data', config_content)
        self.assertIn('medical_info', config_content)
        
        # 構造化ログ設定の検証
        self.assertIn('kind: LoggingConfig', config_content)
        self.assertIn('requiredFields:', config_content)
        self.assertIn('safetyFields:', config_content)
        self.assertIn('performanceFields:', config_content)
        
        # 16文字メッセージハッシュ設定の検証
        self.assertIn('messageHashLength: 16', config_content)
        self.assertIn('hashAlgorithm: "SHA-256"', config_content)
        
        print("✅ ログ設定の検証完了")
    
    def test_alerting_configuration(self):
        """アラート設定の検証"""
        config_path = f"{self.infrastructure_path}/alerting-config.yaml"
        self.assertTrue(os.path.exists(config_path), "アラート設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 基本設定の検証
        self.assertIn('kind: NotificationChannel', config_content)
        self.assertIn('kind: AlertPolicy', config_content)
        
        # 通知チャンネルの検証
        notification_channels = [
            'therapeutic-slack-alerts',
            'therapeutic-emergency-slack',
            'therapeutic-email-alerts',
            'therapeutic-safety-email',
            'therapeutic-oncall-sms'
        ]
        
        for channel in notification_channels:
            self.assertIn(f'name: {channel}', config_content)
        
        # Slack設定の検証
        self.assertIn('type: "slack"', config_content)
        self.assertIn('channel_name: "#therapeutic-app-alerts"', config_content)
        self.assertIn('channel_name: "#therapeutic-app-emergency"', config_content)
        
        # メール設定の検証
        self.assertIn('type: "email"', config_content)
        self.assertIn('therapeutic-alerts@example.com', config_content)
        self.assertIn('safety-team@example.com', config_content)
        
        # SMS設定の検証
        self.assertIn('type: "sms"', config_content)
        self.assertIn('+81-90-XXXX-XXXX', config_content)
        
        # 治療効果監視アラートの検証
        self.assertIn('therapeutic-effectiveness-alerts', config_content)
        self.assertIn('User Engagement Score < 0.6', config_content)
        self.assertIn('Task Completion Rate < 70%', config_content)
        self.assertIn('Apathy State Users Increasing', config_content)
        
        # システム健全性監視アラートの検証
        self.assertIn('therapeutic-system-health-alerts', config_content)
        self.assertIn('Firestore Connection Errors', config_content)
        self.assertIn('OpenAI API Rate Limit Exceeded', config_content)
        self.assertIn('Secret Manager Access Errors', config_content)
        self.assertIn('Cloud Storage Access Errors', config_content)
        
        # GDPR/プライバシー監視アラートの検証
        self.assertIn('therapeutic-privacy-alerts', config_content)
        self.assertIn('Unusual Personal Data Access', config_content)
        self.assertIn('Data Deletion Request Failures', config_content)
        self.assertIn('Access from Non-JP Regions', config_content)
        
        # アラート重要度の検証
        self.assertIn('severity: ERROR', config_content)
        self.assertIn('severity: WARNING', config_content)
        self.assertIn('severity: CRITICAL', config_content)
        
        # 通知レート制限の検証
        self.assertIn('notificationRateLimit:', config_content)
        self.assertIn('autoClose:', config_content)
        
        print("✅ アラート設定の検証完了")
    
    def test_dashboard_configuration(self):
        """ダッシュボード設定の検証"""
        config_path = f"{self.infrastructure_path}/monitoring-dashboard.json"
        self.assertTrue(os.path.exists(config_path), "ダッシュボード設定ファイルが存在しません")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            dashboard_config = json.load(f)
        
        # 基本設定の検証
        self.assertEqual(dashboard_config['displayName'], 'Therapeutic Gamification App Dashboard')
        self.assertIn('mosaicLayout', dashboard_config)
        self.assertIn('tiles', dashboard_config['mosaicLayout'])
        
        # タイルの検証
        tiles = dashboard_config['mosaicLayout']['tiles']
        self.assertIsInstance(tiles, list)
        self.assertGreater(len(tiles), 0)
        
        # 重要なウィジェットの存在確認
        widget_titles = []
        for tile in tiles:
            if 'widget' in tile and 'title' in tile['widget']:
                widget_titles.append(tile['widget']['title'])
        
        required_widgets = [
            'API応答時間 (P95)',
            'エラー率',
            '治療安全性 F1スコア',
            '同時接続ユーザー数',
            'メモリ使用率',
            'CPU使用率',
            'ユーザーエンゲージメントスコア',
            'タスク完了率（タイプ別）',
            'ユーザー状態分布',
            'システムアラート状況',
            '安全性違反検出数',
            'CBT介入実行数'
        ]
        
        for required_widget in required_widgets:
            self.assertIn(required_widget, widget_titles, f"必要なウィジェット '{required_widget}' が見つかりません")
        
        # 閾値設定の検証
        dashboard_content = json.dumps(dashboard_config)
        self.assertIn('0.98', dashboard_content)  # F1スコア閾値
        self.assertIn('20000', dashboard_content)  # 同時接続ユーザー数閾値
        self.assertIn('0.8', dashboard_content)   # メモリ使用率閾値
        self.assertIn('0.7', dashboard_content)   # CPU使用率閾値
        
        # フィルター設定の検証
        self.assertIn('dashboardFilters', dashboard_config)
        filters = dashboard_config['dashboardFilters']
        service_filter = next((f for f in filters if f['labelKey'] == 'service_name'), None)
        self.assertIsNotNone(service_filter, "サービス名フィルターが見つかりません")
        self.assertEqual(service_filter['stringValue'], 'therapeutic-gamification-app')
        
        print("✅ ダッシュボード設定の検証完了")
    
    def test_monitoring_setup_script(self):
        """監視設定スクリプトの検証"""
        script_path = f"{self.infrastructure_path}/monitoring-setup-script.sh"
        self.assertTrue(os.path.exists(script_path), "監視設定スクリプトが存在しません")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 基本構造の検証
        self.assertIn('#!/bin/bash', script_content)
        self.assertIn('set -euo pipefail', script_content)
        
        # 重要なステップの存在確認
        required_steps = [
            'gcloud config set project',
            'gcloud services enable',
            'bq mk --dataset',
            'gsutil mb',
            'gcloud alpha monitoring channels create',
            'gcloud logging metrics create',
            'gcloud logging sinks create',
            'gcloud monitoring uptime create',
            'gcloud alpha monitoring policies create',
            'gcloud monitoring dashboards create'
        ]
        
        for step in required_steps:
            self.assertIn(step, script_content)
        
        # 必要なAPIの有効化確認
        required_apis = [
            'monitoring.googleapis.com',
            'logging.googleapis.com',
            'clouderrorreporting.googleapis.com',
            'cloudtrace.googleapis.com',
            'cloudprofiler.googleapis.com',
            'bigquery.googleapis.com'
        ]
        
        for api in required_apis:
            self.assertIn(api, script_content)
        
        # BigQueryデータセットの確認
        required_datasets = [
            'therapeutic_app_errors',
            'therapeutic_safety_logs',
            'therapeutic_performance_logs'
        ]
        
        for dataset in required_datasets:
            self.assertIn(dataset, script_content)
        
        # カスタムメトリクスの確認
        custom_metrics = [
            'therapeutic_safety_f1_score',
            'therapeutic_api_latency',
            'therapeutic_user_engagement'
        ]
        
        for metric in custom_metrics:
            self.assertIn(metric, script_content)
        
        # ログシンクの確認
        log_sinks = [
            'therapeutic-app-audit-logs',
            'therapeutic-app-error-logs',
            'therapeutic-safety-logs',
            'therapeutic-performance-logs'
        ]
        
        for sink in log_sinks:
            self.assertIn(sink, script_content)
        
        # 通知チャンネルの確認
        self.assertIn('Therapeutic App Slack Alerts', script_content)
        self.assertIn('Therapeutic App Emergency Slack', script_content)
        self.assertIn('Therapeutic App Email Alerts', script_content)
        self.assertIn('Therapeutic Safety Team Email', script_content)
        self.assertIn('Therapeutic On-call SMS', script_content)
        
        # エラーハンドリングの確認
        self.assertIn('|| echo', script_content)  # エラー時の継続処理
        
        print("✅ 監視設定スクリプトの検証完了")
    
    def test_therapeutic_safety_monitoring(self):
        """治療安全性監視の検証"""
        # 要件7.5の検証
        
        # 1. 監視設定での治療安全性メトリクス確認
        monitoring_config_path = f"{self.infrastructure_path}/monitoring-config.yaml"
        with open(monitoring_config_path, 'r', encoding='utf-8') as f:
            monitoring_content = f.read()
        
        # F1スコア監視の確認
        self.assertIn('Safety F1 Score < 98%', monitoring_content)
        self.assertIn('thresholdValue: 0.98', monitoring_content)
        
        # 自傷リスク検出失敗監視の確認
        self.assertIn('Self-harm Detection Failures', monitoring_content)
        self.assertIn('thresholdValue: 5', monitoring_content)  # 5件以上
        
        # CBT介入失敗監視の確認
        self.assertIn('CBT Intervention Failures', monitoring_content)
        self.assertIn('thresholdValue: 10', monitoring_content)  # 10件以上
        
        # OpenAI Moderation API失敗監視の確認
        self.assertIn('Moderation API Failures', monitoring_content)
        self.assertIn('thresholdValue: 3', monitoring_content)  # 3件以上
        
        # 2. ログ設定での治療安全性ログ確認
        logging_config_path = f"{self.infrastructure_path}/logging-config.yaml"
        with open(logging_config_path, 'r', encoding='utf-8') as f:
            logging_content = f.read()
        
        # 治療安全性ログシンクの確認
        self.assertIn('therapeutic-safety-logs', logging_content)
        self.assertIn('therapeutic_safety', logging_content)
        self.assertIn('content_moderation', logging_content)
        self.assertIn('cbt_intervention', logging_content)
        
        # F1スコアログメトリクスの確認
        self.assertIn('therapeutic-safety-f1-score-metric', logging_content)
        self.assertIn('f1_score EXISTS', logging_content)
        
        # 3. アラート設定での緊急通知確認
        alerting_config_path = f"{self.infrastructure_path}/alerting-config.yaml"
        with open(alerting_config_path, 'r', encoding='utf-8') as f:
            alerting_content = f.read()
        
        # 緊急通知チャンネルの確認
        self.assertIn('therapeutic-emergency-slack', alerting_content)
        self.assertIn('therapeutic-safety-email', alerting_content)
        self.assertIn('therapeutic-oncall-sms', alerting_content)
        
        # 治療安全性アラートの重要度確認
        self.assertIn('severity: CRITICAL', alerting_content)
        
        # 短い通知間隔の確認（緊急性が高い）
        # monitoring-config.yamlで設定されているため、そちらを確認
        monitoring_config_path = f"{self.infrastructure_path}/monitoring-config.yaml"
        with open(monitoring_config_path, 'r', encoding='utf-8') as f:
            monitoring_content = f.read()
        self.assertIn('period: 60s', monitoring_content)  # 1分間隔
        
        print("✅ 治療安全性監視の検証完了")
    
    def test_performance_monitoring_compliance(self):
        """パフォーマンス監視コンプライアンスの検証"""
        # 要件8.1-8.4の検証
        
        monitoring_config_path = f"{self.infrastructure_path}/monitoring-config.yaml"
        with open(monitoring_config_path, 'r', encoding='utf-8') as f:
            monitoring_content = f.read()
        
        # 1. 1.2秒P95レイテンシ監視の確認
        self.assertIn('API Response Time P95 > 1.2s', monitoring_content)
        self.assertIn('thresholdValue: 1200', monitoring_content)  # 1.2秒（ミリ秒）
        
        # 2. 20,000同時ユーザー監視の確認
        self.assertIn('Concurrent Users > 18000', monitoring_content)  # 90%閾値
        
        # 3. 99.95%アップタイム監視の確認
        self.assertIn('kind: UptimeCheckConfig', monitoring_content)
        self.assertIn('period: 60s', monitoring_content)  # 1分間隔
        
        # 4. レート制限監視（120req/min/IP）の確認
        # これはCloud Armor WAFで設定されているため、ここでは概念的確認
        
        # ダッシュボードでの閾値確認
        dashboard_config_path = f"{self.infrastructure_path}/monitoring-dashboard.json"
        with open(dashboard_config_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # パフォーマンス閾値の確認
        self.assertIn('20000', dashboard_content)  # 同時接続ユーザー数
        self.assertIn('0.8', dashboard_content)    # メモリ使用率80%
        self.assertIn('0.7', dashboard_content)    # CPU使用率70%
        
        print("✅ パフォーマンス監視コンプライアンスの検証完了")


def run_monitoring_tests():
    """監視システムテストの実行"""
    print("🧪 監視・ログ・アラートシステム設定テスト開始")
    
    # テストスイートの作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMonitoringSetup)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果の表示
    if result.wasSuccessful():
        print("\n✅ 全ての監視システムテストが成功しました")
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
    success = run_monitoring_tests()
    exit(0 if success else 1)