#!/usr/bin/env python3
"""
デプロイメント成功を監視するスクリプト
"""

import requests
import time
import webbrowser
from datetime import datetime

def check_github_actions_status():
    """GitHub Actionsの実行状況をチェック"""
    print("🔍 GitHub Actions実行状況を確認中...")
    
    try:
        # GitHub APIで最新のワークフロー実行を取得
        url = "https://api.github.com/repos/satoshiyoshimoto0426/therapeutic-gamification-app/actions/runs"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            runs = response.json()
            if runs['workflow_runs']:
                latest_run = runs['workflow_runs'][0]
                
                print(f"✅ 最新のワークフロー:")
                print(f"   ID: {latest_run['id']}")
                print(f"   ステータス: {latest_run['status']}")
                print(f"   結論: {latest_run['conclusion']}")
                print(f"   開始時刻: {latest_run['created_at']}")
                print(f"   URL: {latest_run['html_url']}")
                
                return latest_run['status'], latest_run['conclusion']
        
        return None, None
        
    except Exception as e:
        print(f"❌ GitHub Actions確認エラー: {e}")
        return None, None

def check_cloud_run_deployment():
    """Cloud Runデプロイメント状況をチェック"""
    print("\n🔍 Cloud Run デプロイメント確認中...")
    
    # 予想されるCloud Run URL
    urls_to_check = [
        "https://therapeutic-gamification-app-asia-northeast1.a.run.app",
        "https://therapeutic-gamification-app-asia-northeast1.a.run.app/health"
    ]
    
    for url in urls_to_check:
        try:
            print(f"   チェック中: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {url} - 正常応答!")
                return True
            else:
                print(f"   ⚠️ {url} - ステータス: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⏳ {url} - まだデプロイ中...")
        except Exception as e:
            print(f"   ❌ {url} - エラー: {e}")
    
    return False

def open_monitoring_pages():
    """監視用ページを開く"""
    print("\n🌐 監視ページを開いています...")
    
    # GitHub Actions
    actions_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions"
    webbrowser.open(actions_url)
    print(f"✅ GitHub Actions: {actions_url}")
    
    time.sleep(2)
    
    # Google Cloud Console
    cloud_console_url = "https://console.cloud.google.com/run?project=therapeutic-gamification-app-prod"
    webbrowser.open(cloud_console_url)
    print(f"✅ Cloud Console: {cloud_console_url}")

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App デプロイメント監視")
    print("=" * 60)
    print(f"監視開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 監視ページを開く
    open_monitoring_pages()
    
    print("\n📋 次のステップ:")
    print("1. GitHub Actionsページで 'CI/CD Pipeline' を選択")
    print("2. 'Run workflow' をクリック")
    print("3. 'Run workflow' ボタンを押してデプロイ開始")
    print("4. 約15-20分でデプロイ完了")
    
    print("\n⏰ デプロイメント進捗:")
    print("- テスト実行 (5分)")
    print("- Dockerイメージビルド (5分)")
    print("- Cloud Runデプロイ (5-10分)")
    
    # 初回状況確認
    print("\n" + "=" * 60)
    status, conclusion = check_github_actions_status()
    
    if status == "in_progress":
        print("✅ GitHub Actionsが実行中です！")
        print("   進捗はGitHub Actionsページで確認できます。")
    elif conclusion == "success":
        print("🎉 デプロイメント成功！")
        check_cloud_run_deployment()
    elif conclusion == "failure":
        print("❌ デプロイメントが失敗しました。")
        print("   GitHub Actionsのログを確認してください。")
    else:
        print("⏳ GitHub Actionsを手動で実行してください。")
    
    print("\n🎯 成功時のアプリURL:")
    print("https://therapeutic-gamification-app-asia-northeast1.a.run.app")
    
    print("\n✨ 監視準備完了！GitHub Actionsでワークフローを実行してください。")

if __name__ == "__main__":
    main()