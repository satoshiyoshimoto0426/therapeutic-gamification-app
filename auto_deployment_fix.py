#!/usr/bin/env python3
"""
自動デプロイメント修正スクリプト
GitHub Actionsワークフローを更新してコミット・プッシュする
"""

import subprocess
import time

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout.strip():
                print(f"   出力: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} 失敗")
            if result.stderr.strip():
                print(f"   エラー: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} エラー: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🚀 自動デプロイメント修正スクリプト")
    print("=" * 60)
    
    print("\n📋 実行内容:")
    print("1. GitHub Actionsワークフローを修正済み")
    print("2. API自動有効化を追加")
    print("3. プロジェクトIDのフォールバック設定")
    print("4. 変更をGitにコミット・プッシュ")
    
    # Git操作
    commands = [
        ("git add .", "変更ファイルをステージング"),
        ("git commit -m \"fix: auto-enable APIs and improve deployment robustness\"", "変更をコミット"),
        ("git push origin main", "変更をプッシュ")
    ]
    
    print("\n🔄 Git操作を実行中...")
    all_success = True
    
    for command, description in commands:
        success = run_command(command, description)
        if not success:
            all_success = False
            break
        time.sleep(1)
    
    if all_success:
        print("\n🎉 自動修正完了！")
        print("\n📋 修正内容:")
        print("✅ GitHub Actionsワークフローを更新")
        print("✅ Google Cloud APIの自動有効化を追加")
        print("✅ プロジェクトIDのフォールバック設定")
        print("✅ 変更をGitHubにプッシュ")
        
        print("\n🎯 次のステップ:")
        print("1. GitHub Secretsで GCP_PROJECT_ID を 'therapeutic-gamification-app-prod' に設定")
        print("2. GitHub Actionsでワークフローを再実行")
        print("3. 今度はAPIが自動で有効化されるため成功するはず")
        
        print("\n🌐 必要なリンク:")
        print("- GitHub Secrets: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions")
        print("- GitHub Actions: https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions")
        
    else:
        print("\n❌ 一部の操作が失敗しました")
        print("手動でGit操作を完了してください")
    
    print("\n✨ スクリプト完了")

if __name__ == "__main__":
    main()