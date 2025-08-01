#!/usr/bin/env python3
"""
MVP用サービス起動スクリプト

必要最小限のサービスのみを起動してMVPテストを実行
"""

import subprocess
import time
import sys
import os
from typing import List, Tuple

class MVPServiceStarter:
    """MVP用サービス起動管理"""
    
    def __init__(self):
        self.mvp_services = [
            ("コアゲーム", "services/core-game", 8001),
            ("認証", "services/auth", 8002),
            ("タスク管理", "services/task-mgmt", 8003),
            ("Mandala", "services/mandala", 8004),
        ]
        self.processes = []
    
    def start_service(self, name: str, path: str, port: int) -> bool:
        """サービス起動"""
        print(f"🚀 {name}サービス起動中... (ポート: {port})")
        
        try:
            # UTF-8環境変数を設定
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONPATH'] = os.path.abspath('.')
            
            # uvicornでサービス起動（バックグラウンド）
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--reload",
                "--log-level", "warning"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=path,
                env=env,
                stdout=subprocess.DEVNULL,  # 出力を抑制
                stderr=subprocess.DEVNULL,  # エラー出力を抑制
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 起動確認（3秒待機）
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ {name}サービス起動成功")
                self.processes.append((name, process, port))
                return True
            else:
                print(f"❌ {name}サービス起動失敗")
                return False
                
        except Exception as e:
            print(f"❌ {name}サービス起動エラー: {str(e)}")
            return False
    
    def check_service_health(self, port: int) -> bool:
        """サービスヘルスチェック"""
        try:
            import httpx
            with httpx.Client() as client:
                try:
                    response = client.get(f"http://localhost:{port}/health", timeout=3.0)
                    return response.status_code == 200
                except:
                    try:
                        response = client.get(f"http://localhost:{port}/", timeout=3.0)
                        return response.status_code in [200, 404]
                    except:
                        return False
        except ImportError:
            # httpxが利用できない場合、urllibを使用
            import urllib.request
            import urllib.error
            
            try:
                url = f"http://localhost:{port}/health"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3) as response:
                    return response.status == 200
            except:
                try:
                    url = f"http://localhost:{port}/"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=3) as response:
                        return response.status in [200, 404]
                except:
                    return False
    
    def start_all_mvp_services(self) -> bool:
        """全MVPサービス起動"""
        print("🎯 MVP用サービス起動開始")
        print("="*50)
        
        success_count = 0
        
        for name, path, port in self.mvp_services:
            if self.start_service(name, path, port):
                success_count += 1
        
        print(f"\n📊 起動結果: {success_count}/{len(self.mvp_services)} サービス成功")
        
        if success_count == len(self.mvp_services):
            print("✅ 全MVPサービス起動成功！")
            
            # ヘルスチェック実行
            print("\n🔍 ヘルスチェック実行中...")
            time.sleep(2)  # サービス安定化待機
            
            healthy_count = 0
            for name, process, port in self.processes:
                if self.check_service_health(port):
                    print(f"   {name}: ✅ 正常")
                    healthy_count += 1
                else:
                    print(f"   {name}: ⚠️  応答なし")
            
            print(f"\n🎯 ヘルスチェック結果: {healthy_count}/{len(self.processes)} サービス正常")
            
            return healthy_count >= 3  # 最低3つのサービスが正常であればOK
        else:
            print("❌ 一部サービスの起動に失敗しました")
            return False
    
    def stop_all_services(self):
        """全サービス停止"""
        print("\n🛑 MVPサービス停止中...")
        
        for name, process, port in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                        print(f"✅ {name}サービス停止")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        print(f"🔪 {name}サービス強制停止")
                else:
                    print(f"⚠️  {name}サービス: 既に停止済み")
            except Exception as e:
                print(f"❌ {name}サービス停止エラー: {str(e)}")
        
        self.processes.clear()
        print("🎯 MVPサービス停止完了")

def main():
    """メイン実行"""
    starter = MVPServiceStarter()
    
    try:
        # MVPサービス起動
        if starter.start_all_mvp_services():
            print("\n🎮 MVPサービス起動完了！")
            print("次のコマンドでMVPテストを実行してください:")
            print("python mvp_test.py")
            print("\nサービスを停止するには Ctrl+C を押してください")
            
            # サービス監視ループ
            while True:
                time.sleep(30)  # 30秒ごとにチェック
                
                # プロセス生存確認
                alive_count = 0
                for name, process, port in starter.processes:
                    if process.poll() is None:
                        alive_count += 1
                    else:
                        print(f"⚠️  {name}サービスが停止しました")
                
                if alive_count == 0:
                    print("❌ 全サービスが停止しました")
                    break
        else:
            print("❌ MVPサービス起動に失敗しました")
            
    except KeyboardInterrupt:
        print("\n⚠️  停止要求を受信しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
    finally:
        starter.stop_all_services()

if __name__ == "__main__":
    main()