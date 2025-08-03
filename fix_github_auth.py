#!/usr/bin/env python3
"""
GitHub認証問題の解決スクリプト
"""

import subprocess
import webbrowser

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔐 GitHub認証問題の解決")
    print("=" * 40)
    
    print("❌ 現在の問題:")
    print("- リポジトリが見つからない")
    print("- 認証がキャンセルされた")
    
    print("\n🔧 解決手順:")
    print("1. Personal Access Tokenを作成")
    print("2. Git認証情報を更新")
    print("3. リポジトリURLを確認")
    
    # Personal Access Token作成ページを開く
    token_url = "https://github.com/settings/tokens"
    print(f"\n🌐 Personal Access Token作成:")
    print(f"URL: {token_url}")
    
    try:
        webbrowser.open(token_url)
        print("✅ トークン作成ページを開きました")
    except:
        print("⚠️  手動でアクセスしてください")
    
    print("\n📋 トークン作成手順:")
    print("1. 'Generate new token (classic)' をクリック")
    print("2. Note: 'Therapeutic Gamification App'")
    print("3. 権限選択:")
    print("   ✅ repo (全て)")
    print("   ✅ workflow")
    print("   ✅ write:packages")
    print("4. 'Generate token' をクリック")
    print("5. トークンをコピー（一度しか表示されません）")
    
    print("\n⚡ トークン取得後の設定:")
    print("以下のコマンドを実行してください:")
    print()
    print("# リモートURLを更新（トークンを含む）")
    print("git remote set-url origin https://YOUR_TOKEN@github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git")
    print()
    print("# または、認証情報を設定")
    print("git config --global credential.helper store")
    print("git push --set-upstream origin main")
    print("# ユーザー名: satoshiyoshimoto0426")
    print("# パスワード: YOUR_PERSONAL_ACCESS_TOKEN")
    
    print("\n🎯 期待される結果:")
    print("- プッシュが成功する")
    print("- GitHub Actionsが自動実行される")
    print("- GitHub Pagesが利用可能になる")
    
    print("\n💡 代替方法:")
    print("GitHub CLIを使用する場合:")
    print("gh auth login")
    print("gh repo create --public")

if __name__ == "__main__":
    main()