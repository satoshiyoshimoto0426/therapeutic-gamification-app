"""
タスク27.3 パフォーマンスとスケーラビリティの基本確認 - 統合テスト
- 同時接続数の基本テスト（10-50ユーザー）
- API応答時間の測定と最適化
- メモリ使用量とCPU使用率の監視
- 基本的なロードテストの実行
"""

import unittest
import asyncio
import time
import threading
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from load_test_system import (
    SystemMonitor, ConcurrentUserSimulator, LoadTestRunner,
    PerformanceTestSuite, LoadTestResult, SystemMetrics, APIResponseMetrics,
    run_performance_test_suite, run_async_performance_test_suite
)

class TestSystemMonitor(unittest.TestCase):
    """システム監視テスト"""
    
    def setUp(self):
        self.monitor = SystemMonitor()
    
    def tearDown(self):
        if self.monitor.monitoring:
            self.monitor.stop_monitoring()
    
    def test_start_stop_monitoring(self):
        """監視開始・停止テスト"""
        self.assertFalse(self.monitor.monitoring)
        
        self.monitor.start_monitoring(0.1)
        self.assertTrue(self.monitor.monitoring)
        
        # 少し待ってメトリクスが収集されることを確認
        time.sleep(0.3)
        self.assertGreater(len(self.monitor.metrics_history), 0)
        
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring)
    
    def test_get_current_metrics(self):
        """現在のメトリクス取得テスト"""
        self.monitor.start_monitoring(0.1)
        time.sleep(0.2)
        
        current_metrics = self.monitor.get_current_metrics()
        self.assertIsNotNone(current_metrics)
        self.assertIsInstance(current_metrics, SystemMetrics)
        self.assertGreaterEqual(current_metrics.cpu_percent, 0)
        self.assertGreaterEqual(current_metrics.memory_percent, 0)
    
    def test_get_metrics_summary(self):
        """メトリクス要約テスト"""
        self.monitor.start_monitoring(0.1)
        time.sleep(0.5)
        
        summary = self.monitor.get_metrics_summary(1)
        
        self.assertIn("cpu", summary)
        self.assertIn("memory", summary)
        self.assertIn("network", summary)
        self.assertIn("connections", summary)
        
        # CPU統計の確認
        cpu_stats = summary["cpu"]
        self.assertIn("avg", cpu_stats)
        self.assertIn("min", cpu_stats)
        self.assertIn("max", cpu_stats)
        self.assertIn("current", cpu_stats)
        
        # メモリ統計の確認
        memory_stats = summary["memory"]
        self.assertIn("avg", memory_stats)
        self.assertIn("used_mb", memory_stats)
        self.assertIn("available_mb", memory_stats)

class TestConcurrentUserSimulator(unittest.TestCase):
    """同時ユーザーシミュレーターテスト"""
    
    def setUp(self):
        # テスト用のモックサーバーURL
        self.simulator = ConcurrentUserSimulator("http://localhost:8001")
    
    @patch('requests.Session.get')
    def test_simulate_user_session(self, mock_get):
        """ユーザーセッションシミュレーションテスト"""
        # モックレスポンス設定
        mock_response = MagicMock()
        mock_