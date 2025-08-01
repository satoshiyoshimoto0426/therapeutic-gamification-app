#!/usr/bin/env python3
"""
デプロイメント検証テストスクリプト
本番環境とステージング環境でのヘルスチェックと基本機能テスト
"""

import argparse
import sys
import time
import requests
import json
from typing import Dict, List, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentTester:
    """デプロイメント検証テスター"""
    
    def __init__(self, base_url: str, environment: str):
        self.base_url = base_url.rstrip('/')
        self.environment = environment
        self.session = requests.Session()
        self.session.timeout = 30
    
    def health_check(self) -> bool:
        """基本ヘルスチェック"""
        try:
            logger.info(f"ヘルスチェック実行: {self.base_url}/health")
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    logger.info("✅ ヘルスチェック成功")
                    return True
                else:
                    logger.error(f"❌ ヘルスチェック失敗: {health_data}")
                    return False
            else:
                logger.error(f"❌ ヘルスチェック失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ ヘルスチェックエラー: {e}")
            return False
    
    def test_core_endpoints(self) -> bool:
        """コアエンドポイントテスト"""
        endpoints = [
            "/health",
            "/api/user/test_user/dashboard",
            "/api/user/test_user/tasks",
            "/api/user/test_user/mandala",
            "/api/performance/metrics"
        ]
        
        success_count = 0
        
        for endpoint in endpoints:
            try:
                logger.info(f"テスト中: {endpoint}")
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code < 500:  # 5xxエラー以外は許容
                    success_count += 1
                    logger.info(f"✅ {endpoint}: HTTP {response.status_code}")
                else:
                    logger.error(f"❌ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ {endpoint}: {e}")
        
        success_rate = success_count / len(endpoints)
        logger.info(f"エンドポイントテスト成功率: {success_rate:.1%}")
        
        return success_rate >= 0.8  # 80%以上の成功率を要求
    
    def test_response_times(self) -> bool:
        """レスポンス時間テスト"""
        test_endpoints = [
            "/health",
            "/api/user/test_user/dashboard"
        ]
        
        response_times = []
        
        for endpoint in test_endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                logger.info(f"📊 {endpoint}: {response_time:.3f}秒")
                
            except Exception as e:
                logger.error(f"❌ {endpoint}: {e}")
                response_times.append(10.0)  # タイムアウト値
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            logger.info(f"平均レスポンス時間: {avg_time:.3f}秒")
            logger.info(f"最大レスポンス時間: {max_time:.3f}秒")
            
            # 本番環境では厳しい基準、ステージングでは緩い基準
            threshold = 2.0 if self.environment == "production" else 5.0
            
            if avg_time <= threshold:
                logger.info("✅ レスポンス時間テスト合格")
                return True
            else:
                logger.error(f"❌ レスポンス時間テスト失敗: {avg_time:.3f}秒 > {threshold}秒")
                return False
        
        return False
    
    def test_error_rates(self) -> bool:
        """エラー率テスト"""
        test_requests = 10
        error_count = 0
        
        logger.info(f"エラー率テスト実行中... ({test_requests}回)")
        
        for i in range(test_requests):
            try:
                response = self.session.get(f"{self.base_url}/health")
                if response.status_code >= 500:
                    error_count += 1
            except:
                error_count += 1
            
            time.sleep(0.1)  # 100ms間隔
        
        error_rate = error_count / test_requests
        logger.info(f"エラー率: {error_rate:.1%}")
        
        # 本番環境では1%未満、ステージングでは5%未満
        threshold = 0.01 if self.environment == "production" else 0.05
        
        if error_rate <= threshold:
            logger.info("✅ エラー率テスト合格")
            return True
        else:
            logger.error(f"❌ エラー率テスト失敗: {error_rate:.1%} > {threshold:.1%}")
            return False
    
    def run_smoke_tests(self) -> bool:
        """スモークテスト実行"""
        logger.info(f"🧪 スモークテスト開始 ({self.environment})")
        
        tests = [
            ("ヘルスチェック", self.health_check),
            ("コアエンドポイント", self.test_core_endpoints),
            ("レスポンス時間", self.test_response_times),
            ("エラー率", self.test_error_rates)
        ]
        
        passed_tests = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name}テスト ---")
            try:
                if test_func():
                    passed_tests += 1
                    logger.info(f"✅ {test_name}テスト: 合格")
                else:
                    logger.error(f"❌ {test_name}テスト: 不合格")
            except Exception as e:
                logger.error(f"❌ {test_name}テスト: 例外発生 - {e}")
        
        success_rate = passed_tests / len(tests)
        logger.info(f"\n📊 総合結果: {passed_tests}/{len(tests)} 合格 ({success_rate:.1%})")
        
        if success_rate >= 0.75:  # 75%以上で合格
            logger.info("🎉 スモークテスト合格！")
            return True
        else:
            logger.error("💥 スモークテスト失敗")
            return False
    
    def run_quick_check(self) -> bool:
        """クイックチェック（トラフィック移行時用）"""
        logger.info("⚡ クイックチェック実行")
        
        # ヘルスチェックのみ実行
        if self.health_check():
            logger.info("✅ クイックチェック合格")
            return True
        else:
            logger.error("❌ クイックチェック失敗")
            return False

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="デプロイメント検証テスト")
    parser.add_argument("--url", required=True, help="テスト対象URL")
    parser.add_argument("--environment", default="production", choices=["production", "staging"], help="環境")
    parser.add_argument("--health-check-only", action="store_true", help="ヘルスチェックのみ実行")
    parser.add_argument("--quick-check", action="store_true", help="クイックチェック実行")
    
    args = parser.parse_args()
    
    tester = DeploymentTester(args.url, args.environment)
    
    try:
        if args.health_check_only:
            success = tester.health_check()
        elif args.quick_check:
            success = tester.run_quick_check()
        else:
            success = tester.run_smoke_tests()
        
        if success:
            logger.info("🎯 デプロイメント検証成功")
            sys.exit(0)
        else:
            logger.error("💥 デプロイメント検証失敗")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("テスト中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()