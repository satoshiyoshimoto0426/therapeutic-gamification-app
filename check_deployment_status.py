#!/usr/bin/env python3
"""
GitHub ActionsとCloud Runのデプロイメント状況を確認するスクリプト
"""

import requests
import json
import time
from datetime import datetime

def check_github_actions():
    """GitHub Actionsの実行状況を確認"""
    print("🔍 GitHub Actions状況確認中...")
    
    # GitHub APIを使用してActions状況を確認
    repo_url = "https://api.github.com/repos/satoshiyoshimoto0426/therapeutic-gamification-app"
    
    try:
        # 最新のワークフロー実行を取得
        response = requests.get(f"{repo_url}/actions/runs", timeout=10)
        
        if response.status_code == 200:
            runs = response.json()
            if runs['workflow_runs']:
                latest_run = runs['workflow_runs'][0]
                print(f"✅ 最新のワークフロー実行:")
                print(f"   - ID: {latest_run['id']}")
                print(f"   - ステータス: {latest_run['status']}")
                print(f"   - 結論: {latest_run['conclusion']}")
                print(f"   - 開始時刻: {latest_run['created_at']}")
                print(f"   - URL: {latest_run['html_url']}")
                
                return latest_run['status'], latest_run['conclusion']
            else:
                print("❌ ワークフロー実行が見つかりません")
                return None, None
        else:
            print(f"❌ GitHub API エラー: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ GitHub Actions確認エラー: {e}")
        return None, None

def check_cloud_run_service():
    """Cloud Runサービスの状況を確認"""
    print("\n🔍 Cloud Run サービス確認中...")
    
    # Cloud Run サービスのヘルスチェック
    service_urls = [
        "https://therapeutic-gamification-app-asia-northeast1.a.run.app",
        "https://therapeutic-gamification-app-asia-northeast1.a.run.app/health",
        "https://therapeutic-gamification-app-asia-northeast1.a.run.app/api/health"
    ]
    
    for url in service_urls:
        try:
            print(f"   チェック中: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {url} - 正常応答 (200)")
                if 'health' in url:
                    try:
                        health_data = response.json()
                        print(f"      ヘルス情報: {health_data}")
                    except:
                        print(f"      レスポンス: {response.text[:100]}...")
            else:
                print(f"   ⚠️ {url} - ステータス: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ {url} - タイムアウト")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {url} - 接続エラー")
        except Exception as e:
            print(f"   ❌ {url} - エラー: {e}")

def check_github_secrets():
    """GitHub Secretsの設定状況を確認"""
    print("\n🔍 GitHub Secrets確認...")
    
    required_secrets = [
        "GCP_PROJECT_ID",
        "GCP_SA_KEY"
    ]
    
    print("必要なSecrets:")
    for secret in required_secrets:
        print(f"   - {secret}")
    
    print("\n📋 Secrets設定手順:")
    print("1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions")
    print("2. 'New repository secret' をクリック")
    print("3. 以下のSecretsを設定:")
    print("   - GCP_PROJECT_ID: therapeutic-gamification-app-prod")
    print("   - GCP_SA_KEY: Google Cloud Service Accountの JSON キー")

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App デプロイメント状況確認")
    print("=" * 60)
    
    # 現在時刻
    print(f"確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # GitHub Actions確認
    status, conclusion = check_github_actions()
    
    # Cloud Run確認
    check_cloud_run_service()
    
    # GitHub Secrets確認
    check_github_secrets()
    
    print("\n" + "=" * 60)
    print("🎯 次のステップ:")
    
    if status == "in_progress":
        print("✅ GitHub Actionsが実行中です。完了まで待機してください。")
        print("   進捗確認: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions")
    elif conclusion == "success":
        print("✅ デプロイメント成功！アプリケーションが利用可能です。")
        print("   アクセス: https://therapeutic-gamification-app-asia-northeast1.a.run.app")
    elif conclusion == "failure":
        print("❌ デプロイメントが失敗しました。")
        print("   ログ確認: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions")
        print("   GitHub Secretsの設定を確認してください。")
    else:
        print("⏳ GitHub Actionsを手動でトリガーしてください:")
        print("   1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions")
        print("   2. 'CI/CD Pipeline' を選択")
        print("   3. 'Run workflow' をクリック")

if __name__ == "__main__":
    main()