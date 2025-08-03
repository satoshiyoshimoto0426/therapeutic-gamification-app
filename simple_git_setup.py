#!/usr/bin/env python3
"""
簡単なGit設定スクリプト
"""

import subprocess
import sys
import os
import webbrowser

def run_command(command):
    """コマンドを実行"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Git セットアップガイド")
    print("=" * 40)
    
    # Gitがインストールされているかチェック
    success, stdout, stderr = run_command("git --version")
    
    if not success:
        print("📦 Gitがインストールされていません")
        print("\n手動インストール手順:")
        print("1. https://git-scm.com/download/win にアクセス")
        print("2. 'Download for Windows' をクリック")
        print("3. インストーラーを実行")
        print("4. 全てデフォルト設定でインストール")
        print("5. PowerShellを再起動")
        print("6. このスクリプトを再実行")
        
        # ブラウザでダウンロードページを開く
        try:
            webbrowser.open("https://git-scm.com/download/win")
        except:
            pass
        
        input("\nGitをインストール後、Enterキーを押してください...")
        return
    
    print("✅ Gitがインストールされています")
    print(f"バージョン: {stdout.strip()}")
    
    # Git設定
    print("\n🔧 Git設定")
    username = input("GitHubユーザー名: ")
    email = input("GitHubメールアドレス: ")
    
    run_command(f'git config --global user.name "{username}"')
    run_command(f'git config --global user.email "{email}"')
    
    print("✅ Git設定完了")
    
    # GitHub Token設定ガイド
    print("\n🔑 GitHub Personal Access Token 設定")
    print("1. https://github.com/settings/tokens にアクセス")
    print("2. 'Generate new token (classic)' をクリック")
    print("3. 権限を選択: repo, workflow, write:packages")
    print("4. トークンをコピー")
    
    try:
        webbrowser.open("https://github.com/settings/tokens")
    except:
        pass
    
    input("\nトークンを取得したら、Enterキーを押してください...")
    
    # リポジトリ設定
    print("\n📁 リポジトリ設定")
    
    # 既存のoriginを削除（エラーは無視）
    run_command("git remote remove origin")
    
    # 新しいoriginを追加
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git"
    success, stdout, stderr = run_command(f"git remote add origin {repo_url}")
    
    if success:
        print(f"✅ リモートリポジトリ設定: {repo_url}")
    else:
        print(f"⚠️  リモート設定: {stderr}")
    
    # ファイル追加とコミット
    print("\n📤 ファイルのコミット")
    run_command("git add .")
    run_command('git commit -m "feat: complete deployment setup"')
    run_command("git branch -M main")
    
    # プッシュ
    print("🚀 GitHubにプッシュ中...")
    success, stdout, stderr = run_command("git push -u origin main")
    
    if success:
        print("✅ プッシュ完了！")
        print("🌐 https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app")
    else:
        print(f"❌ プッシュ失敗: {stderr}")
        if "Authentication failed" in stderr or "could not read" in stderr:
            print("\n💡 認証エラーの解決方法:")
            print("1. Personal Access Tokenが正しく設定されているか確認")
            print("2. 以下のコマンドを手動で実行:")
            print("   git push -u origin main")
            print("3. ユーザー名: GitHubユーザー名")
            print("4. パスワード: Personal Access Token")

if __name__ == "__main__":
    main()