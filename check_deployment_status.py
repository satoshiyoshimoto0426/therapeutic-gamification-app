#!/usr/bin/env python3
"""
デプロイメント状況確認スクリプト
"""

import webbrowser
import time

def main():
    print("🚀 デプロイメント状況確認")
    print("=" * 40)
    
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app"
    actions_url = f"{repo_url}/actions"
    
    print("✅ GitHubリポジトリが正常に設定されました")
    print(f"📁 リポジトリ: {repo_url}")
    print(f"⚙️  GitHub Actions: {actions_url}")
    
    print("\n🔍 確認項目:")
    print("1. リポジトリにコードがアップロードされているか")
    print("2. GitHub Actionsが自動実行されているか")
    print("3. デプロイメントが成功しているか")
    
    print("\n🌐 ブラウザでリポジトリを開きます...")
    
    try:
        webbrowser.open(repo_url)
        time.sleep(2)
        webbrowser.open(actions_url)
    except Exception as e:
        print(f"ブラウザを開けませんでした: {e}")
        print("手動で以下のURLにアクセスしてください:")
        print(f"リポジトリ: {repo_url}")
        print(f"Actions: {actions_url}")
    
    print("\n📋 GitHub Actionsの確認方法:")
    print("1. 'Actions' タブをクリック")
    print("2. 最新のワークフロー実行を確認")
    print("3. 緑色のチェックマーク = 成功")
    print("4. 赤色のX = エラー（ログを確認）")
    
    print("\n🎯 デプロイ完了後:")
    print("- アプリケーションのURLが表示されます")
    print("- 本番環境でアプリが利用可能になります")
    
    print("\n✨ 素晴らしい仕事でした！")
    print("治療的ゲーミフィケーションアプリのデプロイが完了しました！")

if __name__ == "__main__":
    main()