#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的なサービス動作確認スクリプト
Unicode問題を回避した版
"""

import sys
import os
import subprocess
import time
import socket

def check_port_available(port):
    """ポートが利用可能かチェック"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def test_python_syntax(service_path, service_name):
    """Python構文チェック"""
    print(f"構文チェック: {service_name}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", service_path
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"  OK - 構文エラーなし")
            return True
        else:
            print(f"  ERROR - 構文エラー:")
            print(f"    {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ERROR - 例外: {str(e)}")
        return False

def test_service_import(service_path, service_name):
    """サービスのインポートテスト（環境変数でUTF-8強制）"""
    print(f"インポートテスト: {service_name}")
    
    try:
        # UTF-8環境変数を設定
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        service_dir = os.path.dirname(service_path)
        
        result = subprocess.run([
            sys.executable, "-c", 
            "import main; print('Import successful')"
        ], cwd=service_dir, env=env, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"  OK - インポート成功")
            return True
        else:
            print(f"  ERROR - インポートエラー:")
            print(f"    stdout: {result.stdout}")
            print(f"    stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ERROR - インポートタイムアウト")
        return False
    except Exception as e:
        print(f"  ERROR - 例外: {str(e)}")
        return False

def test_service_startup(service_path, service_name, port):
    """サービスの起動テスト"""
    print(f"起動テスト: {service_name} (ポート: {port})")
    
    if not check_port_available(port):
        print(f"  SKIP - ポート {port} は使用中")
        return False
    
    try:
        # UTF-8環境変数を設定
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        service_dir = os.path.dirname(service_path)
        
        # uvicornでサービス起動
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", str(port),
            "--timeout-keep-alive", "5"
        ], cwd=service_dir, env=env, stdout=subprocess.PIPE, 
           stderr=subprocess.PIPE, text=True)
        
        # 5秒待機
        time.sleep(5)
        
        if process.poll() is None:
            print(f"  OK - 起動成功")
            
            # プロセス終了
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"  ERROR - 起動失敗:")
            if stdout:
                print(f"    stdout: {stdout[:200]}...")
            if stderr:
                print(f"    stderr: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ERROR - 起動例外: {str(e)}")
        return False

def main():
    print("治療的ゲーミフィケーションアプリ - 包括的動作確認")
    print("=" * 60)
    
    # テスト対象サービス
    services = [
        ("services/core-game/main.py", "Core Game Engine", 8001),
        ("services/auth/main.py", "Authentication Service", 8002),
        ("services/task-mgmt/main.py", "Task Management Service", 8003),
        ("services/mandala/main.py", "Mandala Service", 8004),
        ("services/mood-tracking/main.py", "Mood Tracking Service", 8006),
    ]
    
    results = {
        'syntax': [],
        'import': [],
        'startup': []
    }
    
    print("\nPhase 1: 構文チェック")
    print("-" * 30)
    for service_path, service_name, port in services:
        if os.path.exists(service_path):
            result = test_python_syntax(service_path, service_name)
            results['syntax'].append((service_name, result))
        else:
            print(f"SKIP - ファイルが見つかりません: {service_path}")
            results['syntax'].append((service_name, False))
    
    print("\nPhase 2: インポートテスト")
    print("-" * 30)
    for i, (service_path, service_name, port) in enumerate(services):
        if results['syntax'][i][1]:  # 構文チェックが成功した場合のみ
            result = test_service_import(service_path, service_name)
            results['import'].append((service_name, result))
        else:
            print(f"SKIP - 構文エラーのため: {service_name}")
            results['import'].append((service_name, False))
    
    print("\nPhase 3: 起動テスト")
    print("-" * 30)
    for i, (service_path, service_name, port) in enumerate(services):
        if results['import'][i][1]:  # インポートが成功した場合のみ
            result = test_service_startup(service_path, service_name, port)
            results['startup'].append((service_name, result))
        else:
            print(f"SKIP - インポート失敗のため: {service_name}")
            results['startup'].append((service_name, False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    syntax_success = sum(1 for _, result in results['syntax'] if result)
    import_success = sum(1 for _, result in results['import'] if result)
    startup_success = sum(1 for _, result in results['startup'] if result)
    
    total_services = len(services)
    
    print(f"構文チェック: {syntax_success}/{total_services} 成功")
    print(f"インポートテスト: {import_success}/{total_services} 成功")
    print(f"起動テスト: {startup_success}/{total_services} 成功")
    
    if startup_success == total_services:
        print("\n🎉 すべてのサービスが正常に動作しています！")
        print("\n次のステップ:")
        print("1. python deploy_local.py を実行")
        print("2. ブラウザで game_launcher.html を開く")
        print("3. 各サービスのAPI文書を確認")
        return True
    else:
        print("\n⚠️ 修正が必要なサービスがあります")
        
        print("\n問題のあるサービス:")
        for service_name, result in results['syntax']:
            if not result:
                print(f"  - {service_name}: 構文エラー")
        
        for service_name, result in results['import']:
            if not result:
                print(f"  - {service_name}: インポートエラー")
        
        for service_name, result in results['startup']:
            if not result:
                print(f"  - {service_name}: 起動エラー")
        
        return False

if __name__ == "__main__":
    main()