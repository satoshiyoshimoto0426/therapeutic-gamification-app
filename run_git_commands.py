#!/usr/bin/env python3
"""
Git コマンド実行スクリプト
"""

import subprocess
import sys

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"\n🔧 {description}")
    print(f"実行: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("✅ 出力:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  エラー/警告:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 成功")
        else:
            print(f"❌ 失敗 (終了コード: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

def main():
    print("🚀 Git コマンド自動実行")
    print("=" * 40)
    
    print("📋 前提条件:")
    print("✅ GitHubリポジトリが作成済み")
    print("✅ Personal Access Tokenが準備済み")
    
    input("\n⏸️  準備ができたら、Enterキーを押してください...")
    
    # コマンド実行
    commands = [
        ("git config --global credential.helper manager-core", "認証設定"),
        ("git remote remove origin", "既存リモート削除"),
        ("git remote add origin https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app.git", "リモートリポジトリ設定"),
        ("git add .", "ファイル追加"),
        ("git commit -m \"feat: initial commit with therapeutic gamification app\"", "コミット作成"),
        ("git branch -M main", "ブランチ設定"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            if "remove origin" not in command:  # origin削除の失敗は無視
                success = False
                break
    
    if success:
        print("\n" + "="*50)
        print("🎯 最終ステップ: プッシュ")
        print("="*50)
        
        print("\n📝 以下のコマンドを手動で実行してください:")
        print("git push -u origin main")
        
        print("\n🔐 認証情報入力時:")
        print("Username: satoshiyoshimoto0426")
        print("Password: [あなたのPersonal Access Token]")
        
        print("\n✅ 成功の確認:")
        print("- 'Enumerating objects' メッセージ")
        print("- 'Writing objects: 100%' メッセージ")
        print("- 'Branch main set up to track origin/main' メッセージ")
        
        print("\n🌐 成功後:")
        print("1. https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/pages")
        print("2. Source で 'GitHub Actions' を選択")
        print("3. Save をクリック")
        print("4. 5-10分でアプリが利用可能になります")
        
    else:
        print("\n❌ エラーが発生しました")
        print("手動でコマンドを実行してください")

if __name__ == "__main__":
    main()