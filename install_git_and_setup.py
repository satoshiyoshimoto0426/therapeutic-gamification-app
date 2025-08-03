#!/usr/bin/env python3
"""
Git インストールとGitHub認証設定スクリプト
"""

import subprocess
import sys
import os
import webbrowser
from pathlib import Path

def run_command(command, shell=True):
    """コマンドを実行し、結果を返す"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_git():
    """Gitをインストール"""
    print("🔧 Gitのインストールを開始します...")
    
    # Chocolateyを使ってGitをインストール
    success, stdout, stderr = run_command("choco install git -y")
    
    if success:
        print("✅ Gitのインストールが完了しました")
        print("⚠️  PowerShellを再起動してください")
        return True
    else:
        print("❌ Chocolateyが見つかりません。手動でGitをインストールしてください")
        print("📥 https://git-scm.com/download/win からGitをダウンロードしてインストールしてください")
        webbrowser.open("https://git-scm.com/download/win")
        return False

def check_git_installed():
    """Gitがインストールされているかチェック"""
    success, stdout, stderr = run_command("git --version")
    return success

def setup_git_credentials():
    """Git認証情報を設定"""
    print("\n🔐 Git認証情報の設定")
    
    # ユーザー名とメールアドレスの設定
    username = input("GitHubユーザー名を入力してください: ")
    email = input("GitHubメールアドレスを入力してください: ")
    
    run_command(f'git config --global user.name "{username}"')
    run_command(f'git config --global user.email "{email}"')
    
    print(f"✅ Git設定完了: {username} <{email}>")
    
    return username

def setup_github_token():
    """GitHub Personal Access Tokenの設定"""
    print("\n🔑 GitHub Personal Access Token の設定")
    print("1. https://github.com/settings/tokens にアクセス")
    print("2. 'Generate new token (classic)' をクリック")
    print("3. 以下の権限を選択:")
    print("   - repo (全て)")
    print("   - workflow")
    print("   - write:packages")
    print("   - delete:packages")
    print("4. トークンをコピーして、以下に貼り付けてください")
    
    webbrowser.open("https://github.com/settings/tokens")
    
    token = input("\nPersonal Access Token を入力してください: ").strip()
    
    if token:
        # Windows Credential Managerに保存
        run_command(f'git config --global credential.helper manager-core')
        print("✅ トークンが設定されました")
        return token
    else:
        print("❌ トークンが入力されませんでした")
        return None

def setup_repository():
    """リポジトリの設定"""
    print("\n📁 リポジトリの設定")
    
    # 現在のリモートを確認
    success, stdout, stderr = run_command("git remote -v")
    if success and stdout:
        print("現在のリモート設定:")
        print(stdout)
    
    # リモートの設定
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git"
    
    # 既存のoriginを削除
    run_command("git remote remove origin")
    
    # 新しいoriginを追加
    success, stdout, stderr = run_command(f"git remote add origin {repo_url}")
    
    if success:
        print(f"✅ リモートリポジトリを設定しました: {repo_url}")
    else:
        print(f"❌ リモートリポジトリの設定に失敗: {stderr}")
        return False
    
    return True

def commit_and_push():
    """ファイルをコミットしてプッシュ"""
    print("\n📤 ファイルのコミットとプッシュ")
    
    # ファイルを追加
    run_command("git add .")
    
    # コミット
    success, stdout, stderr = run_command('git commit -m "feat: complete deployment setup"')
    if not success and "nothing to commit" not in stderr:
        print(f"⚠️  コミット警告: {stderr}")
    
    # ブランチを設定
    run_command("git branch -M main")
    
    # プッシュ
    print("🚀 GitHubにプッシュしています...")
    success, stdout, stderr = run_command("git push -u origin main")
    
    if success:
        print("✅ プッシュが完了しました！")
        print("🌐 リポジトリ: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app")
        return True
    else:
        print(f"❌ プッシュに失敗しました: {stderr}")
        if "Authentication failed" in stderr:
            print("💡 認証に失敗しました。Personal Access Tokenを確認してください")
        return False

def main():
    """メイン処理"""
    print("🚀 Git セットアップとGitHubデプロイメント")
    print("=" * 50)
    
    # Gitがインストールされているかチェック
    if not check_git_installed():
        print("📦 Gitがインストールされていません")
        if install_git():
            print("⚠️  PowerShellを再起動してから、このスクリプトを再実行してください")
            input("Enterキーを押して終了...")
            return
        else:
            print("❌ Gitのインストールに失敗しました")
            input("Enterキーを押して終了...")
            return
    
    print("✅ Gitがインストールされています")
    
    # Git認証情報の設定
    username = setup_git_credentials()
    
    # GitHub Tokenの設定
    token = setup_github_token()
    if not token:
        print("❌ トークンの設定に失敗しました")
        input("Enterキーを押して終了...")
        return
    
    # リポジトリの設定
    if not setup_repository():
        input("Enterキーを押して終了...")
        return
    
    # コミットとプッシュ
    if commit_and_push():
        print("\n🎉 デプロイメント準備が完了しました！")
        print("次のステップ:")
        print("1. GitHub Actionsが自動実行されます")
        print("2. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions で進捗を確認")
        print("3. デプロイが完了したら、アプリケーションにアクセスできます")
    
    input("\nEnterキーを押して終了...")

if __name__ == "__main__":
    main()