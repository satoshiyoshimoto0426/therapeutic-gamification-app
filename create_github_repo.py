#!/usr/bin/env python3
"""
GitHubリポジトリ作成ガイド
"""

import webbrowser
import time

def main():
    print("🔧 GitHubリポジトリ作成ガイド")
    print("=" * 50)
    
    print("❌ 現在の問題:")
    print("   Repository not found エラー")
    print("   → リポジトリがまだ作成されていません")
    
    print("\n" + "="*50)
    print("🎯 解決方法: GitHubでリポジトリを作成")
    print("="*50)
    
    print("\n📋 手順1: GitHubにアクセス")
    print("1️⃣ ブラウザで https://github.com を開く")
    print("2️⃣ あなたのアカウントでログイン")
    
    print("\n📋 手順2: 新しいリポジトリを作成")
    print("3️⃣ 右上の '+' ボタンをクリック")
    print("4️⃣ 'New repository' を選択")
    
    print("\n📋 手順3: リポジトリ設定")
    print("5️⃣ Repository name: 'therapeutic-gamification-app'")
    print("6️⃣ Description: 'ADHD支援とRPG要素を組み合わせた治療アプリ'")
    print("7️⃣ Public を選択")
    print("8️⃣ 'Add a README file' のチェックを外す")
    print("9️⃣ 'Add .gitignore' は None のまま")
    print("🔟 'Choose a license' は None のまま")
    
    print("\n📋 手順4: リポジトリ作成")
    print("1️⃣1️⃣ 'Create repository' ボタンをクリック")
    
    print("\n🌐 ブラウザでGitHubを開きます...")
    
    try:
        # GitHubのリポジトリ作成ページを開く
        webbrowser.open("https://github.com/new")
        print("✅ GitHub新規リポジトリ作成ページを開きました")
    except:
        print("⚠️  手動でアクセスしてください")
        print("URL: https://github.com/new")
    
    input("\n⏸️  リポジトリを作成したら、Enterキーを押してください...")
    
    print("\n" + "="*50)
    print("🎯 リポジトリ作成後の手順")
    print("="*50)
    
    print("\n📝 PowerShellで以下のコマンドを実行:")
    
    print("\n1️⃣ 認証設定")
    print("git config --global credential.helper manager-core")
    
    print("\n2️⃣ リモートリポジトリ設定")
    print("git remote remove origin")
    print("git remote add origin https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git")
    
    print("\n3️⃣ ファイル追加・コミット")
    print("git add .")
    print("git commit -m \"feat: initial commit with therapeutic gamification app\"")
    
    print("\n4️⃣ ブランチ設定とプッシュ")
    print("git branch -M main")
    print("git push -u origin main")
    
    print("\n📝 認証情報入力時:")
    print("Username: satoshiyoshimoto0426")
    print("Password: [Personal Access Token]")
    
    print("\n✅ 成功の確認:")
    print("- 'Enumerating objects' メッセージ")
    print("- 'Writing objects: 100%' メッセージ")
    print("- 'Branch main set up to track origin/main' メッセージ")
    
    print("\n🎯 次のステップ:")
    print("1. GitHub Pages設定")
    print("2. 自動デプロイ開始")
    print("3. アプリ公開完了")
    
    print("\n🌐 最終的なアプリURL:")
    print("https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")

if __name__ == "__main__":
    main()