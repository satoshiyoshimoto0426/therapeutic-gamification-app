#!/usr/bin/env python3
"""
Git認証設定の詳細ガイド（画像付き手順）
"""

import webbrowser
import time

def main():
    print("🔐 Git認証設定 - 詳細ガイド")
    print("=" * 50)
    
    print("📋 現在の状況:")
    print("❌ GitHubにプッシュできない")
    print("❌ 認証エラーが発生")
    print("✅ コードは準備完了")
    
    print("\n" + "="*50)
    print("🎯 ステップ1: Personal Access Token作成")
    print("="*50)
    
    print("\n1️⃣ GitHubにログイン")
    print("   ブラウザで https://github.com にアクセス")
    print("   あなたのアカウントでログイン")
    
    print("\n2️⃣ Settings（設定）ページへ")
    print("   右上のプロフィール画像をクリック")
    print("   ドロップダウンメニューから「Settings」を選択")
    
    print("\n3️⃣ Developer settings へ")
    print("   左サイドバーの一番下にある")
    print("   「Developer settings」をクリック")
    
    print("\n4️⃣ Personal access tokens へ")
    print("   左サイドバーで「Personal access tokens」を展開")
    print("   「Tokens (classic)」をクリック")
    
    print("\n5️⃣ 新しいトークンを作成")
    print("   「Generate new token」ボタンをクリック")
    print("   「Generate new token (classic)」を選択")
    
    print("\n6️⃣ トークンの設定")
    print("   Note: 'Therapeutic Gamification App' と入力")
    print("   Expiration: '90 days' を選択")
    print("   Select scopes（権限）で以下をチェック:")
    print("   ✅ repo (全ての項目)")
    print("   ✅ workflow")
    print("   ✅ write:packages")
    print("   ✅ delete:packages")
    
    print("\n7️⃣ トークンを生成")
    print("   ページ下部の「Generate token」をクリック")
    print("   ⚠️  生成されたトークンをコピー（一度しか表示されません！）")
    
    # ブラウザでトークン作成ページを開く
    token_url = "https://github.com/settings/tokens"
    print(f"\n🌐 ブラウザでトークン作成ページを開きます...")
    print(f"URL: {token_url}")
    
    try:
        webbrowser.open(token_url)
        print("✅ ページを開きました")
    except:
        print("⚠️  手動でアクセスしてください")
    
    input("\n⏸️  トークンを作成したら、Enterキーを押してください...")
    
    print("\n" + "="*50)
    print("🎯 ステップ2: Git認証設定")
    print("="*50)
    
    print("\n📝 以下のコマンドを順番に実行してください:")
    print("\n1️⃣ 認証情報の保存を有効化")
    print("   PowerShellで以下を実行:")
    print("   git config --global credential.helper manager-core")
    
    print("\n2️⃣ リポジトリのプッシュ")
    print("   PowerShellで以下を実行:")
    print("   git push --set-upstream origin main")
    
    print("\n3️⃣ 認証情報の入力")
    print("   プッシュ時に認証が求められたら:")
    print("   Username: satoshiyoshimoto0426")
    print("   Password: [作成したPersonal Access Token]")
    print("   ⚠️  パスワード欄にはGitHubのパスワードではなく、")
    print("       Personal Access Tokenを入力してください！")
    
    print("\n" + "="*50)
    print("🎯 ステップ3: 確認")
    print("="*50)
    
    print("\n✅ 成功した場合:")
    print("   - 'Enumerating objects' などのメッセージが表示")
    print("   - 'Writing objects: 100%' と表示")
    print("   - 'Branch 'main' set up to track...' と表示")
    
    print("\n❌ 失敗した場合:")
    print("   - 'Authentication failed' エラー")
    print("   - 'Repository not found' エラー")
    print("   → Personal Access Tokenを再確認")
    
    print("\n" + "="*50)
    print("🎯 ステップ4: GitHub Pages設定")
    print("="*50)
    
    print("\nプッシュが成功したら:")
    print("1️⃣ リポジトリページにアクセス")
    print("   https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app")
    
    print("\n2️⃣ Settings タブをクリック")
    
    print("\n3️⃣ 左サイドバーで 'Pages' をクリック")
    
    print("\n4️⃣ Source を設定")
    print("   'Source' で 'GitHub Actions' を選択")
    print("   'Save' ボタンをクリック")
    
    print("\n5️⃣ デプロイ完了を待つ")
    print("   5-10分後にアプリのURLが表示されます")
    
    print("\n🎉 完了！")
    print("アプリURL: https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")
    
    print("\n💡 困ったときは:")
    print("- トークンの権限を再確認")
    print("- PowerShellを管理者として実行")
    print("- Git認証情報をクリア: git config --global --unset credential.helper")

if __name__ == "__main__":
    main()