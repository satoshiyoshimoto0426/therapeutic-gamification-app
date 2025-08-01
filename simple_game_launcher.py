#!/usr/bin/env python3
"""
シンプルゲームランチャー

MVPテスト用の簡単なサービス起動とテスト実行
"""

import subprocess
import time
import sys
import os
import asyncio
from typing import List, Tuple

class SimpleGameLauncher:
    """シンプルゲームランチャー"""
    
    def __init__(self):
        self.mvp_services = [
            ("コアゲーム", "services/core-game", 8001),
            ("認証", "services/auth", 8002),
            ("タスク管理", "services/task-mgmt", 8003),
            ("Mandala", "services/mandala", 8004),
        ]
        self.processes = []
    
    def start_service_background(self, name: str, path: str, port: int) -> bool:
        """バックグラウンドでサービス起動"""
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONPATH'] = os.path.abspath('.')
            
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--log-level", "error"  # エラーのみ表示
            ]
            
            # Windowsでバックグラウンド起動
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd,
                    cwd=path,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Unix系
                process = subprocess.Popen(
                    cmd,
                    cwd=path,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            self.processes.append((name, process, port))
            return True
            
        except Exception as e:
            print(f"❌ {name}サービス起動エラー: {str(e)}")
            return False
    
    def check_service_ready(self, port: int, max_attempts: int = 10) -> bool:
        """サービス準備完了チェック"""
        for attempt in range(max_attempts):
            try:
                import httpx
                with httpx.Client() as client:
                    try:
                        response = client.get(f"http://localhost:{port}/health", timeout=2.0)
                        if response.status_code == 200:
                            return True
                    except:
                        try:
                            response = client.get(f"http://localhost:{port}/", timeout=2.0)
                            if response.status_code in [200, 404]:
                                return True
                        except:
                            pass
            except ImportError:
                # httpxが利用できない場合
                import urllib.request
                try:
                    url = f"http://localhost:{port}/"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=2) as response:
                        if response.status in [200, 404]:
                            return True
                except:
                    pass
            
            time.sleep(1)  # 1秒待機
        
        return False
    
    def launch_mvp_game(self):
        """MVPゲーム起動"""
        print("🎮 治療的ゲーミフィケーションアプリ - MVP起動")
        print("="*60)
        
        # 1. サービス起動
        print("🚀 MVPサービス起動中...")
        
        for name, path, port in self.mvp_services:
            print(f"   {name}サービス起動中... (ポート: {port})")
            if self.start_service_background(name, path, port):
                print(f"   ✅ {name}サービス起動")
            else:
                print(f"   ❌ {name}サービス起動失敗")
                return False
        
        # 2. サービス準備完了待機
        print("\n🔍 サービス準備完了待機中...")
        
        ready_count = 0
        for name, process, port in self.processes:
            print(f"   {name}サービス準備確認中...")
            if self.check_service_ready(port):
                print(f"   ✅ {name}サービス準備完了")
                ready_count += 1
            else:
                print(f"   ⚠️  {name}サービス準備未完了")
        
        if ready_count < 3:  # 最低3つのサービスが必要
            print(f"\n❌ 準備完了サービス数不足: {ready_count}/4")
            self.cleanup_processes()
            return False
        
        print(f"\n✅ {ready_count}/4 サービス準備完了")
        
        # 3. MVPテスト実行
        print("\n🧪 MVPテスト実行中...")
        
        try:
            # MVPテストを実行
            result = subprocess.run(
                [sys.executable, "mvp_test.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60  # 60秒タイムアウト
            )
            
            print("📊 MVPテスト結果:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️  エラー出力:")
                print(result.stderr)
            
            success = result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ MVPテストがタイムアウトしました")
            success = False
        except Exception as e:
            print(f"❌ MVPテスト実行エラー: {str(e)}")
            success = False
        
        # 4. 結果表示
        print("\n" + "="*60)
        if success:
            print("🎉 MVP起動・テスト完了！")
            print("✅ 最小動作版の核心機能が正常に動作しています")
            
            print("\n🔧 開発者向けAPI文書:")
            for name, process, port in self.processes:
                if process.poll() is None:  # プロセスが生きている場合
                    print(f"- {name}: http://localhost:{port}/docs")
            
            print("\n💡 次のステップ:")
            print("- 統合テストとエンドツーエンドテストの実行")
            print("- パフォーマンステストの実行")
            print("- 本番環境デプロイの準備")
            
        else:
            print("❌ MVP起動・テストに問題があります")
            print("ログを確認して問題を修正してください")
        
        # 5. クリーンアップ
        print("\n🛑 サービス停止中...")
        self.cleanup_processes()
        
        return success
    
    def cleanup_processes(self):
        """プロセスクリーンアップ"""
        for name, process, port in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                        print(f"   ✅ {name}サービス停止")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        print(f"   🔪 {name}サービス強制停止")
            except Exception as e:
                print(f"   ❌ {name}サービス停止エラー: {str(e)}")
        
        self.processes.clear()

def main():
    """メイン実行"""
    launcher = SimpleGameLauncher()
    
    try:
        success = launcher.launch_mvp_game()
        
        if success:
            print("\n🎯 MVP起動完了！")
            return 0
        else:
            print("\n❌ MVP起動失敗")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  中断されました")
        launcher.cleanup_processes()
        return 1
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {str(e)}")
        launcher.cleanup_processes()
        return 1

if __name__ == "__main__":
    sys.exit(main())