#!/usr/bin/env python3
"""
完全自動デプロイスクリプト
"""

import subprocess
import sys
import os
import getpass
import webbrowser
import time

def run_command(command, description, hide_output=False):
    """コマンドを実行して結果を表示"""
    if not hide_output:
        print(f"\n🔧 {description}")
        print(f"実行: {command}")
        print("-" * 40)
    
    try:
        if hide_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, text=True)
        
        if not hide_output and result.returncode == 0:
            print("✅ 成功")
        elif not hide_output:
            print(f"❌ 失敗 (終了コード: {result.returncode})")
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        if not hide_output:
            print(f"❌ 実行エラー: {e}")
        return False, "", str(e)

def setup_git_with_token(token, username):
    """Personal Access Tokenを使ってGitを設定"""
    print("🔐 Git認証設定中...")
    
    # 認証情報を含むURLを設定
    repo_url_with_token = f"https://{token}@github.com/{username}/therapeutic-gamification-app.git"
    
    commands = [
        ("git config --global credential.helper manager-core", "認証ヘルパー設定"),
        ("git remote remove origin", "既存リモート削除"),
        (f"git remote add origin {repo_url_with_token}", "認証付きリモート設定"),
        ("git add .", "ファイル追加"),
        ("git commit -m \"feat: complete therapeutic gamification app deployment\"", "コミット作成"),
        ("git branch -M main", "ブランチ設定"),
        ("git push -u origin main", "プッシュ実行"),
    ]
    
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        if not success and "remove origin" not in command:
            print(f"❌ エラー: {stderr}")
            if "Repository not found" in stderr:
                print("\n🔧 GitHubリポジトリを作成します...")
                create_github_repo(username)
                return False
            elif "Authentication failed" in stderr:
                print("❌ 認証に失敗しました。Personal Access Tokenを確認してください。")
                return False
    
    return True

def create_github_repo(username):
    """GitHubリポジトリ作成ガイド"""
    print("\n" + "="*50)
    print("🎯 GitHubリポジトリ作成が必要です")
    print("="*50)
    
    print("\n📋 手順:")
    print("1. ブラウザでGitHubを開きます")
    print("2. 右上の '+' → 'New repository'")
    print("3. Repository name: 'therapeutic-gamification-app'")
    print("4. Public を選択")
    print("5. README, .gitignore, license は追加しない")
    print("6. 'Create repository' をクリック")
    
    try:
        webbrowser.open("https://github.com/new")
        print("✅ ブラウザでGitHub新規リポジトリページを開きました")
    except:
        print("⚠️  手動で https://github.com/new にアクセスしてください")
    
    input("\n⏸️  リポジトリを作成したら、Enterキーを押してください...")

def setup_github_pages():
    """GitHub Pages設定ガイド"""
    print("\n" + "="*50)
    print("🌐 GitHub Pages設定")
    print("="*50)
    
    pages_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/pages"
    
    print("\n📋 手順:")
    print("1. GitHub Pages設定ページを開きます")
    print("2. Source で 'GitHub Actions' を選択")
    print("3. 'Save' をクリック")
    print("4. 5-10分でアプリが利用可能になります")
    
    try:
        webbrowser.open(pages_url)
        print("✅ GitHub Pages設定ページを開きました")
    except:
        print(f"⚠️  手動で {pages_url} にアクセスしてください")
    
    print("\n🎯 最終的なアプリURL:")
    print("https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")

def main():
    print("🚀 完全自動デプロイスクリプト")
    print("=" * 50)
    
    print("🎮 治療的ゲーミフィケーションアプリをデプロイします")
    print("📋 必要な情報を入力してください:")
    
    # Personal Access Token入力
    print("\n🔑 Personal Access Token:")
    print("- GitHub Settings → Developer settings → Personal access tokens")
    print("- Generate new token (classic)")
    print("- 権限: repo, workflow, write:packages")
    
    token = getpass.getpass("Personal Access Token を入力してください: ").strip()
    
    if not token:
        print("❌ Personal Access Tokenが入力されませんでした")
        return
    
    username = "satoshiyoshimoto0426"
    
    print(f"\n✅ 設定完了:")
    print(f"   ユーザー: {username}")
    print(f"   トークン: {'*' * (len(token) - 4) + token[-4:]}")
    
    # Git設定とプッシュ
    print("\n🔧 Git設定とプッシュを開始...")
    
    retry_count = 0
    max_retries = 2
    
    while retry_count < max_retries:
        success = setup_git_with_token(token, username)
        
        if success:
            print("\n🎉 プッシュ成功！")
            break
        else:
            retry_count += 1
            if retry_count < max_retries:
                print(f"\n🔄 再試行 ({retry_count}/{max_retries})")
                input("準備ができたら、Enterキーを押してください...")
            else:
                print("\n❌ 自動デプロイに失敗しました")
                print("手動でリポジトリを作成してから再実行してください")
                return
    
    # GitHub Pages設定
    setup_github_pages()
    
    print("\n" + "="*50)
    print("🎊 デプロイ完了！")
    print("="*50)
    
    print("\n✅ 完了した作業:")
    print("- Git認証設定")
    print("- ファイルコミット")
    print("- GitHubプッシュ")
    print("- GitHub Pages設定ガイド")
    
    print("\n🌐 アプリURL:")
    print("https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")
    
    print("\n⏰ 5-10分後にアプリが利用可能になります")
    print("🎮 治療的ゲーミフィケーションアプリの完成です！")

if __name__ == "__main__":
    main()