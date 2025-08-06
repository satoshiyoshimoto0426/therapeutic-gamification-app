#!/usr/bin/env python3
"""
プロジェクトIDとAPI有効化エラーを修正するスクリプト
"""

import webbrowser
import time

def main():
    print("🔧 Google Cloud プロジェクトとAPI設定修正")
    print("=" * 60)
    
    print("\n❌ 現在の問題:")
    print("1. 間違ったプロジェクトID: abiding-beanbag-467909-d8")
    print("2. 正しいプロジェクトID: therapeutic-gamification-app-prod")
    print("3. Cloud Run APIが無効化されている")
    
    print("\n🎯 解決方法:")
    print("GitHub SecretsのGCP_PROJECT_IDを正しい値に更新する必要があります")
    
    print("\n📋 修正手順:")
    print("1. GitHub Secretsページを開く")
    print("2. GCP_PROJECT_ID を編集")
    print("3. 値を 'therapeutic-gamification-app-prod' に変更")
    print("4. Google Cloud ConsoleでAPIを有効化")
    
    print("\n🌐 必要なページを開きます...")
    
    # GitHub Secrets編集ページ
    time.sleep(2)
    github_secrets_url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions"
    webbrowser.open(github_secrets_url)
    print(f"✅ GitHub Secrets: {github_secrets_url}")
    
    # Google Cloud Console API有効化ページ
    time.sleep(3)
    api_enable_url = "https://console.developers.google.com/apis/api/run.googleapis.com/overview?project=therapeutic-gamification-app-prod"
    webbrowser.open(api_enable_url)
    print(f"✅ Cloud Run API有効化: {api_enable_url}")
    
    # Google Cloud Console プロジェクト選択
    time.sleep(3)
    project_url = "https://console.cloud.google.com/projectselector2/home/dashboard"
    webbrowser.open(project_url)
    print(f"✅ プロジェクト選択: {project_url}")
    
    print("\n" + "=" * 60)
    print("🔧 修正手順詳細:")
    
    print("\n1️⃣ GitHub Secrets修正:")
    print("   - GCP_PROJECT_ID をクリック")
    print("   - 'Update secret' をクリック")
    print("   - 値を 'therapeutic-gamification-app-prod' に変更")
    print("   - 'Update secret' で保存")
    
    print("\n2️⃣ Google Cloud プロジェクト確認:")
    print("   - プロジェクト 'therapeutic-gamification-app-prod' を選択")
    print("   - 存在しない場合は新規作成")
    
    print("\n3️⃣ 必要なAPIを有効化:")
    print("   - Cloud Run Admin API")
    print("   - Cloud Build API")
    print("   - Container Registry API")
    print("   - Cloud Resource Manager API")
    print("   - Firestore API")
    
    print("\n4️⃣ Service Account権限確認:")
    print("   - github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com")
    print("   - 必要な権限が付与されていることを確認")
    
    print("\n✅ 修正完了後:")
    print("GitHub Actionsを再実行してください")
    
    print("\n🎉 これで正常にデプロイされるはずです！")

if __name__ == "__main__":
    main()