#!/usr/bin/env python3
"""
デプロイメントエラーを解消するための自動化スクリプト
"""

import webbrowser
import time
import sys

def open_github_secrets():
    """GitHub Secrets設定ページを開く"""
    print("🔐 GitHub Secrets設定ページを開いています...")
    url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions"
    webbrowser.open(url)
    print(f"✅ ブラウザで開きました: {url}")

def open_google_cloud_console():
    """Google Cloud Console Service Accountsページを開く"""
    print("☁️ Google Cloud Console Service Accountsページを開いています...")
    url = "https://console.cloud.google.com/iam-admin/serviceaccounts"
    webbrowser.open(url)
    print(f"✅ ブラウザで開きました: {url}")

def open_github_actions():
    """GitHub Actionsページを開く"""
    print("🚀 GitHub Actionsページを開いています...")
    url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions"
    webbrowser.open(url)
    print(f"✅ ブラウザで開きました: {url}")

def display_instructions():
    """設定手順を表示"""
    print("\n" + "="*60)
    print("🎯 エラー解消手順")
    print("="*60)
    
    print("\n📋 ステップ1: Google Cloud Service Account作成")
    print("1. Google Cloud Consoleで新しいService Accountを作成")
    print("2. 名前: 'github-actions'")
    print("3. 以下の権限を付与:")
    print("   - Cloud Run Admin")
    print("   - Cloud Build Editor")
    print("   - Storage Admin")
    print("   - Service Account User")
    print("   - Cloud Datastore Owner")
    print("   - Secret Manager Admin")
    print("   - Logging Viewer")
    print("4. JSONキーを生成・ダウンロード")
    
    print("\n🔐 ステップ2: GitHub Secrets設定")
    print("1. GCP_PROJECT_ID = 'therapeutic-gamification-app-prod'")
    print("2. GCP_SA_KEY = ダウンロードしたJSONファイルの内容全体")
    
    print("\n🚀 ステップ3: GitHub Actions実行")
    print("1. 'CI/CD Pipeline' を選択")
    print("2. 'Run workflow' をクリック")
    print("3. デプロイ完了まで15-20分待機")
    
    print("\n✅ 完了確認")
    print("デプロイ成功後のアプリURL:")
    print("https://therapeutic-gamification-app-asia-northeast1.a.run.app")

def main():
    """メイン実行関数"""
    print("🔧 Therapeutic Gamification App デプロイメントエラー解消")
    print("="*60)
    
    print("\n現在のエラー状況:")
    print("❌ GitHub Actions失敗 (認証エラー)")
    print("❌ Cloud Run 404エラー (サービス未デプロイ)")
    print("❌ GitHub Secrets未設定")
    
    print("\n🎯 解決策: GitHub Secretsを正しく設定する")
    
    # 手順表示
    display_instructions()
    
    print("\n" + "="*60)
    print("🌐 必要なページを自動で開きます...")
    
    # 必要なページを順番に開く
    time.sleep(2)
    open_google_cloud_console()
    
    time.sleep(3)
    open_github_secrets()
    
    time.sleep(3)
    open_github_actions()
    
    print("\n✨ 全ての必要なページを開きました！")
    print("上記の手順に従って設定を完了してください。")
    
    print("\n🎉 設定完了後、GitHub Actionsが自動的にアプリをデプロイします！")

if __name__ == "__main__":
    main()