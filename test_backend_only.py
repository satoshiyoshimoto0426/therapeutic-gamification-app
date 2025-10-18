#!/usr/bin/env python3
"""
バックエンドのみのテストスクリプト

フロントエンドなしでバックエンドサービスをテストします。
"""

import subprocess
import time
import sys
import requests
from typing import Dict, List


class BackendTester:
    """バックエンドテストクラス"""
    
    def __init__(self):
        self.services = {
            "core-game": {"port": 8001, "path": "services/core-game"},
            "auth": {"port": 8002, "path": "services/auth"},
            "task-mgmt": {"port": 8003, "path": "services/task-mgmt"},
            "mandala": {"port": 8004, "path": "services/mandala"},
        }
        self.processes = []
    
    def start_service(self, name: str, config: Dict) -> bool:
        """サービスを起動"""
        print(f"🚀 {name}サービスを起動中... (ポート: {config['port']})")
        
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", str(config['port']),
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=config['path'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.processes.append((name, process, config['port']))
            time.sleep(3)  # 起動待機
            
            if process.poll() is None:
                print(f"✅ {name}サービス起動成功")
                return True
            else:
                print(f"❌ {name}サービス起動失敗")
                return False
                
        except Exception as e:
            print(f"❌ {name}サービス起動エラー: {str(e)}")
            return False
    
    def check_health(self, name: str, port: int) -> bool:
        """ヘルスチェック"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ {name}: 正常")
                return True
            else:
                print(f"⚠️  {name}: 応答異常 (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {name}: ヘルスチェック失敗 - {str(e)}")
            return False
    
    def test_api_endpoint(self, name: str, port: int, endpoint: str) -> bool:
        """APIエンドポイントテスト"""
        try:
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=3)
            print(f"  {endpoint}: {response.status_code}")
            return response.status_code in [200, 404]  # 404も許容（未実装エンドポイント）
        except Exception as e:
            print(f"  {endpoint}: エラー - {str(e)}")
            return False
    
    def run_tests(self):
        """テスト実行"""
        print("\n" + "="*60)
        print("🎮 バックエンドサービステスト")
        print("="*60 + "\n")
        
        # サービス起動
        print("ステップ 1: サービス起動")
        print("-"*60)
        success_count = 0
        for name, config in self.services.items():
            if self.start_service(name, config):
                success_count += 1
        
        print(f"\n起動結果: {success_count}/{len(self.services)} サービス成功\n")
        
        if success_count == 0:
            print("❌ サービスが起動できませんでした")
            return False
        
        # ヘルスチェック
        print("\nステップ 2: ヘルスチェック")
        print("-"*60)
        time.sleep(2)  # サービス安定化待機
        
        healthy_count = 0
        for name, process, port in self.processes:
            if self.check_health(name, port):
                healthy_count += 1
        
        print(f"\nヘルスチェック結果: {healthy_count}/{len(self.processes)} サービス正常\n")
        
        # APIテスト
        print("\nステップ 3: 基本APIテスト")
        print("-"*60)
        
        # Core Game API
        print("\n[Core Game API]")
        self.test_api_endpoint("core-game", 8001, "/health")
        self.test_api_endpoint("core-game", 8001, "/docs")
        
        # Auth API
        print("\n[Auth API]")
        self.test_api_endpoint("auth", 8002, "/health")
        self.test_api_endpoint("auth", 8002, "/docs")
        
        # Task Management API
        print("\n[Task Management API]")
        self.test_api_endpoint("task-mgmt", 8003, "/health")
        self.test_api_endpoint("task-mgmt", 8003, "/docs")
        
        # 完了メッセージ
        print("\n" + "="*60)
        print("✅ バックエンドテスト完了！")
        print("="*60)
        print("\nAPIドキュメントにアクセス:")
        print("  Core Game: http://localhost:8001/docs")
        print("  Auth:      http://localhost:8002/docs")
        print("  Task Mgmt: http://localhost:8003/docs")
        print("\nサービスを停止するには Ctrl+C を押してください")
        print("="*60 + "\n")
        
        return True
    
    def stop_all(self):
        """全サービス停止"""
        print("\n🛑 サービスを停止中...")
        for name, process, port in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=3)
                    print(f"✅ {name}サービス停止")
            except Exception as e:
                print(f"❌ {name}サービス停止エラー: {str(e)}")
        print("✅ 全サービス停止完了")


def main():
    """メイン関数"""
    tester = BackendTester()
    
    try:
        if tester.run_tests():
            # サービスを起動したまま待機
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  停止要求を受信しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
    finally:
        tester.stop_all()


if __name__ == "__main__":
    main()
