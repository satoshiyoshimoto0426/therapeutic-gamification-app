#!/usr/bin/env python3
"""
GitHub Pages設定スクリプト
"""

import webbrowser
import time

def main():
    print("🔧 GitHub Pages 設定ガイド")
    print("=" * 40)
    
    print("📋 現在の状況:")
    print("✅ リポジトリ作成済み")
    print("✅ コードアップロード済み")
    print("❌ GitHub Pages未設定")
    
    print("\n🚀 GitHub Pages設定手順:")
    print("1. GitHubリポジトリの設定ページにアクセス")
    print("2. 'Pages' セクションを選択")
    print("3. Source を 'GitHub Actions' に設定")
    print("4. 自動デプロイが開始される")
    
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app"
    settings_url = f"{repo_url}/settings"
    pages_url = f"{repo_url}/settings/pages"
    
    print(f"\n🌐 設定URL:")
    print(f"リポジトリ設定: {settings_url}")
    print(f"Pages設定: {pages_url}")
    
    print("\n📝 詳細手順:")
    print("1. ブラウザでPages設定ページを開く")
    print("2. 'Source' で 'GitHub Actions' を選択")
    print("3. 'Save' をクリック")
    print("4. 数分待つとアプリのURLが表示される")
    
    print("\n🎯 期待される結果:")
    print("設定後、以下のようなURLでアクセス可能:")
    print("https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")
    
    print("\n🌐 ブラウザでPages設定を開きます...")
    
    try:
        webbrowser.open(pages_url)
        print("✅ GitHub Pages設定ページを開きました")
    except Exception as e:
        print(f"⚠️  ブラウザを開けませんでした: {e}")
        print("手動で以下のURLにアクセスしてください:")
        print(pages_url)
    
    print("\n⚡ 設定完了後:")
    print("- GitHub Actionsが自動実行されます")
    print("- 5-10分でアプリが利用可能になります")
    print("- URLが生成されてアクセス可能になります")
    
    print("\n✨ これで治療的ゲーミフィケーションアプリが公開されます！")

if __name__ == "__main__":
    main()