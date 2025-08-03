#!/usr/bin/env python3
"""
超簡単デプロイスクリプト
"""

import subprocess
import webbrowser

def main():
    print("🚀 超簡単デプロイ")
    print("=" * 30)
    
    print("📋 必要な作業:")
    print("1. Personal Access Token作成")
    print("2. GitHubリポジトリ作成")
    print("3. コードプッシュ")
    print("4. GitHub Pages設定")
    
    # Personal Access Token作成ページを開く
    print("\n🔑 Step 1: Personal Access Token作成")
    try:
        webbrowser.open("https://github.com/settings/tokens")
        print("✅ トークン作成ページを開きました")
    except:
        print("手動で https://github.com/settings/tokens にアクセス")
    
    print("\n📝 トークン設定:")
    print("- Note: Therapeutic Gamification App")
    print("- 権限: repo, workflow, write:packages")
    
    token = input("\n作成したPersonal Access Tokenを入力してください: ").strip()
    
    if not token:
        print("❌ トークンが入力されませんでした")
        return
    
    # GitHubリポジトリ作成ページを開く
    print("\n📁 Step 2: GitHubリポジトリ作成")
    try:
        webbrowser.open("https://github.com/new")
        print("✅ リポジトリ作成ページを開きました")
    except:
        print("手動で https://github.com/new にアクセス")
    
    print("\n📝 リポジトリ設定:")
    print("- Repository name: therapeutic-gamification-app")
    print("- Public を選択")
    print("- README, .gitignore, license は追加しない")
    
    input("\nリポジトリを作成したら、Enterキーを押してください...")
    
    # Git設定とプッシュ
    print("\n🔧 Step 3: コードプッシュ")
    
    # 認証付きURLを作成
    repo_url = f"https://{token}@github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git"
    
    commands = [
        "git remote remove origin",
        f"git remote add origin {repo_url}",
        "git add .",
        "git commit -m \"feat: therapeutic gamification app\"",
        "git branch -M main",
        "git push -u origin main"
    ]
    
    print("実行中...")
    for i, command in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] {command.split()[1] if len(command.split()) > 1 else command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0 and "remove origin" not in command:
                print(f"❌ エラー: {result.stderr}")
                if "Repository not found" in result.stderr:
                    print("リポジトリが見つかりません。作成を確認してください。")
                    return
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return
    
    print("✅ プッシュ完了！")
    
    # GitHub Pages設定
    print("\n🌐 Step 4: GitHub Pages設定")
    pages_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/pages"
    
    try:
        webbrowser.open(pages_url)
        print("✅ GitHub Pages設定ページを開きました")
    except:
        print(f"手動で {pages_url} にアクセス")
    
    print("\n📝 Pages設定:")
    print("- Source で 'GitHub Actions' を選択")
    print("- 'Save' をクリック")
    
    print("\n🎉 完了！")
    print("🌐 アプリURL: https://satoshiyoshimoto0426.github.io/therapeutic-gamification-app/")
    print("⏰ 5-10分後に利用可能になります")

if __name__ == "__main__":
    main()