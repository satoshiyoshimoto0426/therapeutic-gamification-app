#!/usr/bin/env python3
"""
ローカルデプロイメントシステムのテスト
"""

import subprocess
import sys
import os
import time

def test_deploy_system():
    """デプロイメントシステムのテスト"""
    print("🧪 ローカルデプロイメントシステムのテスト開始")
    print("="*50)
    
    tests = [
        ("ヘルスチェック機能", ["python", "deploy_local.py", "--health-check-only"]),
        ("ポートチェック機能", ["python", "deploy_local.py", "--port-check"]),
        ("ランチャー作成機能", ["python", "deploy_local.py", "--launcher-only"]),
    ]
    
    results = []
    
    for test_name, command in tests:
        print(f"\n🔍 {test_name}をテスト中...")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                print(f"✅ {test_name}: 成功")
                results.append((test_name, "成功", None))
            else:
                print(f"❌ {test_name}: 失敗 (終了コード: {result.returncode})")
                results.append((test_name, "失敗", result.stderr))
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name}: タイムアウト")
            results.append((test_name, "タイムアウト", None))
        except Exception as e:
            print(f"❌ {test_name}: エラー - {str(e)}")
            results.append((test_name, "エラー", str(e)))
            
        # デバッグ情報を表示
        if result.returncode != 0:
            print(f"   標準出力: {result.stdout[:200]}...")
            print(f"   標準エラー: {result.stderr[:200]}...")
    
    # ファイル存在チェック
    print(f"\n📁 ファイル存在チェック...")
    files_to_check = [
        "deploy_local.py",
        "game_launcher.html",
        "simple_game_launcher.py"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {filename}: 存在")
            results.append((f"ファイル存在: {filename}", "成功", None))
        else:
            print(f"❌ {filename}: 存在しない")
            results.append((f"ファイル存在: {filename}", "失敗", None))
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, status, error in results:
        status_emoji = "✅" if status == "成功" else "❌"
        print(f"{status_emoji} {test_name}: {status}")
        if error and len(error.strip()) > 0:
            print(f"   エラー詳細: {error[:100]}...")
        
        if status == "成功":
            success_count += 1
    
    print(f"\n🎯 結果: {success_count}/{total_count} テストが成功")
    
    if success_count == total_count:
        print("🎉 すべてのテストが成功しました！")
        print("✅ ローカルデプロイメントシステムは正常に動作しています。")
    elif success_count > total_count * 0.7:
        print("⚠️  大部分のテストが成功しました。")
        print("🔧 一部の機能に問題がある可能性があります。")
    else:
        print("❌ 多くのテストが失敗しました。")
        print("🛠️  システムの修正が必要です。")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_deploy_system()
    sys.exit(0 if success else 1)