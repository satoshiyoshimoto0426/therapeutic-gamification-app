#!/usr/bin/env python3
"""
Git認証コマンドの実行支援
"""

def main():
    print("🚀 Git認証コマンド実行ガイド")
    print("=" * 40)
    
    print("📋 Personal Access Tokenを作成済みの場合、")
    print("   以下のコマンドを順番に実行してください:")
    
    print("\n" + "="*40)
    print("コマンド1: 認証設定")
    print("="*40)
    print("git config --global credential.helper manager-core")
    
    print("\n" + "="*40)
    print("コマンド2: プッシュ実行")
    print("="*40)
    print("git push --set-upstream origin main")
    
    print("\n📝 認証情報入力時:")
    print("Username: satoshiyoshimoto0426")
    print("Password: [あなたのPersonal Access Token]")
    
    print("\n⚠️  重要:")
    print("- パスワード欄にはGitHubのパスワードではなく")
    print("- Personal Access Tokenを入力してください")
    print("- トークンは ghp_ で始まる長い文字列です")
    
    print("\n🎯 成功の確認:")
    print("以下のようなメッセージが表示されれば成功:")
    print("- Enumerating objects: XX, done.")
    print("- Writing objects: 100% (XX/XX), done.")
    print("- Branch 'main' set up to track 'origin/main'.")
    
    print("\n❌ エラーの場合:")
    print("- 'Authentication failed' → トークンを再確認")
    print("- 'Repository not found' → リポジトリURLを確認")
    
    print("\n🌐 成功後の次のステップ:")
    print("1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/pages")
    print("2. Source で 'GitHub Actions' を選択")
    print("3. Save をクリック")
    print("4. 5-10分待つとアプリが利用可能になります")
    
    print("\n✨ 最終的なアプリURL:")
    print("https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")

if __name__ == "__main__":
    main()