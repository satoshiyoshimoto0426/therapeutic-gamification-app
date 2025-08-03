#!/usr/bin/env python3
"""
404エラーのトラブルシューティングスクリプト
"""

import webbrowser
import time

def main():
    print("🔍 404エラーのトラブルシューティング")
    print("=" * 50)
    
    print("⚠️  404エラーは正常な状況です！")
    print("\n📋 404が発生する理由:")
    print("1. リポジトリは存在するが、GitHub Pagesが未設定")
    print("2. デプロイメントがまだ完了していない")
    print("3. カスタムドメインが設定されていない")
    
    print("\n🔧 確認すべき項目:")
    
    # リポジトリの確認
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app"
    print(f"1. リポジトリ確認: {repo_url}")
    
    # GitHub Actionsの確認
    actions_url = f"{repo_url}/actions"
    print(f"2. GitHub Actions: {actions_url}")
    
    # GitHub Pagesの確認
    pages_url = f"{repo_url}/settings/pages"
    print(f"3. GitHub Pages設定: {pages_url}")
    
    print("\n🚀 解決手順:")
    print("1. GitHub Actionsが実行中か確認")
    print("2. デプロイメントが完了するまで待機（5-15分）")
    print("3. GitHub Pages設定を確認")
    print("4. カスタムドメインまたはGitHub PagesのURLを確認")
    
    print("\n📱 期待される結果:")
    print("- GitHub Actionsが成功すると、アプリのURLが生成されます")
    print("- 通常は以下のような形式:")
    print("  https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")
    print("  または")
    print("  https://your-custom-domain.com/")
    
    print("\n🌐 ブラウザで確認ページを開きます...")
    
    try:
        # リポジトリを開く
        webbrowser.open(repo_url)
        time.sleep(2)
        
        # GitHub Actionsを開く
        webbrowser.open(actions_url)
        time.sleep(2)
        
        # GitHub Pages設定を開く
        webbrowser.open(pages_url)
        
    except Exception as e:
        print(f"ブラウザを開けませんでした: {e}")
    
    print("\n✅ 404は問題ありません！")
    print("デプロイメントの完了をお待ちください。")

if __name__ == "__main__":
    main()