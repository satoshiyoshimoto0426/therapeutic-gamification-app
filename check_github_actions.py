#!/usr/bin/env python3
"""
GitHub Actionsの状況確認
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
    print("🔍 GitHub Actions 状況確認")
    print("=" * 40)
    
    # 最新のコミット確認
    success, stdout, stderr = run_command("git log --oneline -1")
    if success:
        print(f"✅ 最新コミット: {stdout.strip()}")
    
    # リモートの状況確認
    success, stdout, stderr = run_command("git remote -v")
    if success:
        print("✅ リモートリポジトリ設定済み")
    
    # ブランチ確認
    success, stdout, stderr = run_command("git branch")
    if success:
        print(f"✅ 現在のブランチ: {stdout.strip()}")
    
    print("\n🚀 次のステップ:")
    print("1. GitHub Actionsの実行状況を確認")
    print("2. デプロイメント完了まで待機")
    print("3. アプリのURLが生成されるのを確認")
    
    print("\n🌐 確認URL:")
    repo_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app"
    actions_url = f"{repo_url}/actions"
    
    print(f"リポジトリ: {repo_url}")
    print(f"Actions: {actions_url}")
    
    # ブラウザで開く
    try:
        webbrowser.open(actions_url)
        print("\n✅ GitHub Actionsページを開きました")
    except:
        print("\n⚠️  手動でActionsページにアクセスしてください")
    
    print("\n📋 確認ポイント:")
    print("- 🟢 緑のチェックマーク = デプロイ成功")
    print("- 🟡 黄色の円 = 実行中")
    print("- 🔴 赤のX = エラー（ログを確認）")
    
    print("\n⏰ 通常5-15分でデプロイ完了します")
    print("404エラーは正常です。心配不要！")

if __name__ == "__main__":
    main()