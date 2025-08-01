#!/usr/bin/env python3
"""
修正後のサービス動作確認スクリプト
"""

import sys
import os
import subprocess
import time

def test_service_import(service_path, service_name):
    """サービスのインポートテスト"""
    print(f"🔍 {service_name} インポートテスト中...")
    
    try:
        # サービスディレクトリに移動してインポートテスト
        original_cwd = os.getcwd()
        service_dir = os.path.dirname(service_path)
        os.chdir(service_dir)
        
        # Pythonでインポートテスト
        result = subprocess.run([
            sys.executable, "-c", 
            "import main; print('✅ インポート成功')"
        ], capture_output=True, text=True, timeout=10)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print(f"✅ {service_name} - インポート成功")
            return True
        else:
            print(f"❌ {service_name} - インポートエラー:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {service_name} - インポートタイムアウト")
        return False
    except Exception as e:
        print(f"❌ {service_name} - 例外: {str(e)}")
        return False

def test_service_startup(service_path, service_name, port):
    """サービスの起動テスト"""
    print(f"🚀 {service_name} 起動テスト中... (ポート: {port})")
    
    try:
        # サービスディレクトリに移動
        original_cwd = os.getcwd()
        service_dir = os.path.dirname(service_path)
        os.chdir(service_dir)
        
        # uvicornでサービス起動（短時間）
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", str(port),
            "--timeout-keep-alive", "5"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 3秒待機
        time.sleep(3)
        
        os.chdir(original_cwd)
        
        if process.poll() is None:
            # プロセスが生きている = 起動成功
            print(f"✅ {service_name} - 起動成功")
            
            # プロセス終了
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            # プロセスが終了している = 起動失敗
            stdout, stderr = process.communicate()
            print(f"❌ {service_name} - 起動失敗:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {service_name} - 起動例外: {str(e)}")
        return False

def main():
    print("🔧 修正後サービス動作確認")
    print("="*50)
    
    # テスト対象サービス
    services = [
        ("services/core-game/main.py", "Core Game Engine", 8001),
        ("services/auth/main.py", "Authentication Service", 8002),
        ("services/task-mgmt/main.py", "Task Management Service", 8003),
        ("services/mandala/main.py", "Mandala Service", 8004),
        ("services/mood-tracking/main.py", "Mood Tracking Service", 8006),
    ]
    
    import_results = []
    startup_results = []
    
    # インポートテスト
    print("\n📋 Phase 1: インポートテスト")
    for service_path, service_name, port in services:
        if os.path.exists(service_path):
            result = test_service_import(service_path, service_name)
            import_results.append((service_name, result))
        else:
            print(f"⚠️ {service_name} - ファイルが見つかりません: {service_path}")
            import_results.append((service_name, False))
    
    # 起動テスト（インポートが成功したもののみ）
    print("\n📋 Phase 2: 起動テスト")
    for i, (service_path, service_name, port) in enumerate(services):
        if import_results[i][1]:  # インポートが成功した場合のみ
            result = test_service_startup(service_path, service_name, port)
            startup_results.append((service_name, result))
        else:
            print(f"⏭️ {service_name} - インポート失敗のためスキップ")
            startup_results.append((service_name, False))
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print("-" * 50)
    
    import_success = sum(1 for _, result in import_results if result)
    startup_success = sum(1 for _, result in startup_results if result)
    
    print(f"インポートテスト: {import_success}/{len(import_results)} 成功")
    print(f"起動テスト: {startup_success}/{len(startup_results)} 成功")
    
    if import_success == len(import_results) and startup_success == len(startup_results):
        print("\n🎉 すべてのサービスが正常に動作しています！")
        print("\n💡 次のステップ:")
        print("1. deploy_local.py を実行してすべてのサービスを起動")
        print("2. ブラウザで http://localhost:8001/docs にアクセスしてAPI確認")
        return True
    else:
        print("\n⚠️ 一部のサービスに問題があります")
        print("\n💡 修正が必要な項目:")
        
        for service_name, result in import_results:
            if not result:
                print(f"  - {service_name}: インポートエラー")
        
        for service_name, result in startup_results:
            if not result:
                print(f"  - {service_name}: 起動エラー")
        
        return False

if __name__ == "__main__":
    main()