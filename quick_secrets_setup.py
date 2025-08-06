#!/usr/bin/env python3
"""
GitHub Secrets設定を簡単にするためのガイドスクリプト
"""

import webbrowser
import time

def main():
    print("🔐 GitHub Secrets 正しい設定ガイド")
    print("="*50)
    
    print("\n❌ エラーの原因:")
    print("Secret名に無効な文字が含まれています")
    
    print("\n✅ 正しいSecret名:")
    print("1. GCP_PROJECT_ID")
    print("2. GCP_SA_KEY")
    
    print("\n📋 設定する値:")
    print("GCP_PROJECT_ID = therapeutic-gamification-app-prod")
    print("GCP_SA_KEY = Google Cloud Service AccountのJSONキー")
    
    print("\n🌐 必要なページを開きます...")
    
    # Google Cloud Console
    print("\n1. Google Cloud Console (Service Account作成)")
    time.sleep(2)
    webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
    
    # GitHub Secrets
    print("2. GitHub Secrets設定ページ")
    time.sleep(3)
    webbrowser.open("https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions")
    
    print("\n📝 設定手順:")
    print("1. Google Cloud ConsoleでService Account作成")
    print("   - 名前: github-actions")
    print("   - 権限: Cloud Run Admin, Cloud Build Editor, Storage Admin等")
    print("   - JSONキーをダウンロード")
    print("\n2. GitHub Secretsで以下を設定:")
    print("   - Name: GCP_PROJECT_ID, Value: therapeutic-gamification-app-prod")
    print("   - Name: GCP_SA_KEY, Value: JSONキーの内容全体")
    
    print("\n🚀 設定完了後:")
    print("GitHub Actionsを手動実行してデプロイを開始")
    
    time.sleep(3)
    print("\n3. GitHub Actions実行ページ")
    webbrowser.open("https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions")
    
    print("\n✨ 全てのページを開きました！")
    print("上記の手順に従って設定してください。")

if __name__ == "__main__":
    main()