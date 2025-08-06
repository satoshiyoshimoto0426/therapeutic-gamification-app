#!/usr/bin/env python3
"""
Google Cloud Service Account作成の詳細ガイド
JSONキー生成の問題を解決するための段階的手順
"""

import webbrowser
import time

def step1_create_project():
    """ステップ1: Google Cloudプロジェクト作成"""
    print("📋 ステップ1: Google Cloudプロジェクト作成")
    print("-" * 50)
    
    print("1. Google Cloud Consoleにアクセス:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. 新しいプロジェクトを作成:")
    print("   - 画面上部の「プロジェクトを選択」をクリック")
    print("   - 「新しいプロジェクト」をクリック")
    print("   - プロジェクト名: therapeutic-gamification-app-prod")
    print("   - 「作成」をクリック")
    
    print("\n3. プロジェクトが作成されるまで待機（1-2分）")
    
    # Google Cloud Consoleを開く
    url = "https://console.cloud.google.com/projectcreate"
    print(f"\n🌐 ブラウザで開きます: {url}")
    webbrowser.open(url)
    
    input("\n✅ プロジェクト作成完了後、Enterキーを押してください...")

def step2_enable_apis():
    """ステップ2: 必要なAPIを有効化"""
    print("\n📋 ステップ2: 必要なAPIを有効化")
    print("-" * 50)
    
    apis = [
        ("Cloud Run API", "https://console.cloud.google.com/apis/library/run.googleapis.com"),
        ("Cloud Build API", "https://console.cloud.google.com/apis/library/cloudbuild.googleapis.com"),
        ("Container Registry API", "https://console.cloud.google.com/apis/library/containerregistry.googleapis.com"),
        ("IAM Service Account Credentials API", "https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com")
    ]
    
    for api_name, api_url in apis:
        print(f"\n{api_name}を有効化:")
        print(f"   URL: {api_url}")
        print("   - 「有効にする」をクリック")
        webbrowser.open(api_url)
        time.sleep(2)
    
    input("\n✅ 全てのAPI有効化完了後、Enterキーを押してください...")

def step3_create_service_account():
    """ステップ3: Service Account作成"""
    print("\n📋 ステップ3: Service Account作成")
    print("-" * 50)
    
    print("1. IAM & Admin > Service Accountsにアクセス:")
    url = "https://console.cloud.google.com/iam-admin/serviceaccounts"
    print(f"   {url}")
    
    print("\n2. 「サービス アカウントを作成」をクリック")
    
    print("\n3. サービス アカウントの詳細:")
    print("   - サービス アカウント名: github-actions")
    print("   - サービス アカウント ID: github-actions")
    print("   - 説明: GitHub Actions deployment service account")
    print("   - 「作成して続行」をクリック")
    
    print("\n4. このサービス アカウントにプロジェクトへのアクセス権を付与:")
    roles = [
        "Cloud Run 管理者",
        "Cloud Build 編集者",
        "ストレージ管理者",
        "サービス アカウント ユーザー",
        "Cloud Datastore オーナー",
        "Secret Manager 管理者",
        "ログ閲覧者"
    ]
    
    for role in roles:
        print(f"   - {role}")
    
    print("\n   「ロールを追加」で上記の権限を全て追加")
    print("   「続行」をクリック")
    
    print("\n5. 「完了」をクリック")
    
    webbrowser.open(url)
    input("\n✅ Service Account作成完了後、Enterキーを押してください...")

def step4_create_json_key():
    """ステップ4: JSONキー作成"""
    print("\n📋 ステップ4: JSONキー作成")
    print("-" * 50)
    
    print("1. 作成したService Account「github-actions」をクリック")
    
    print("\n2. 「キー」タブをクリック")
    
    print("\n3. 「鍵を追加」→「新しい鍵を作成」をクリック")
    
    print("\n4. キーのタイプ:")
    print("   - 「JSON」を選択")
    print("   - 「作成」をクリック")
    
    print("\n5. JSONファイルが自動ダウンロードされます")
    print("   - ファイル名: therapeutic-gamification-app-prod-xxxxx.json")
    print("   - このファイルを安全な場所に保存")
    
    print("\n⚠️ 重要な注意事項:")
    print("   - このJSONファイルは一度しかダウンロードできません")
    print("   - ファイルの内容全体をコピーしてGitHub Secretsに設定します")
    
    url = "https://console.cloud.google.com/iam-admin/serviceaccounts"
    webbrowser.open(url)
    
    input("\n✅ JSONキーダウンロード完了後、Enterキーを押してください...")

def step5_setup_github_secrets():
    """ステップ5: GitHub Secrets設定"""
    print("\n📋 ステップ5: GitHub Secrets設定")
    print("-" * 50)
    
    print("1. GitHub Secretsページにアクセス:")
    url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/settings/secrets/actions"
    print(f"   {url}")
    
    print("\n2. 「New repository secret」をクリック")
    
    print("\n3. 1つ目のSecret:")
    print("   - Name: GCP_PROJECT_ID")
    print("   - Secret: therapeutic-gamification-app-prod")
    print("   - 「Add secret」をクリック")
    
    print("\n4. 2つ目のSecret:")
    print("   - Name: GCP_SA_KEY")
    print("   - Secret: ダウンロードしたJSONファイルの内容全体")
    print("   - JSONファイルをテキストエディタで開いてコピー")
    print("   - 「Add secret」をクリック")
    
    print("\n📝 JSONファイルの内容例:")
    print("""
    {
      "type": "service_account",
      "project_id": "therapeutic-gamification-app-prod",
      "private_key_id": "...",
      "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
      "client_email": "github-actions@therapeutic-gamification-app-prod.iam.gserviceaccount.com",
      ...
    }
    """)
    
    webbrowser.open(url)
    input("\n✅ GitHub Secrets設定完了後、Enterキーを押してください...")

def step6_trigger_deployment():
    """ステップ6: デプロイメント実行"""
    print("\n📋 ステップ6: デプロイメント実行")
    print("-" * 50)
    
    print("1. GitHub Actionsページにアクセス:")
    url = "https://github.com/satoshiyoshimoto0426/therapeutic-gamification-app/actions"
    print(f"   {url}")
    
    print("\n2. 「CI/CD Pipeline」をクリック")
    
    print("\n3. 「Run workflow」をクリック")
    
    print("\n4. 「Run workflow」ボタンをクリック")
    
    print("\n5. デプロイメント進捗を監視:")
    print("   - 約15-20分でデプロイ完了")
    print("   - 各ステップの進捗をリアルタイムで確認")
    
    print("\n✅ デプロイ成功後のアプリURL:")
    print("   https://therapeutic-gamification-app-asia-northeast1.a.run.app")
    
    webbrowser.open(url)

def main():
    """メイン実行関数"""
    print("🔧 Google Cloud Service Account & JSONキー作成ガイド")
    print("=" * 60)
    
    print("\n現在の問題: JSONキー生成ができない")
    print("解決策: 段階的に正しい手順で設定")
    
    print("\n⚠️ 事前準備:")
    print("- Googleアカウントでログイン済み")
    print("- Google Cloud Consoleにアクセス可能")
    print("- 請求先アカウントが設定済み（無料枠でOK）")
    
    try:
        step1_create_project()
        step2_enable_apis()
        step3_create_service_account()
        step4_create_json_key()
        step5_setup_github_secrets()
        step6_trigger_deployment()
        
        print("\n🎉 全ての設定が完了しました！")
        print("GitHub Actionsが自動的にアプリをデプロイします。")
        
    except KeyboardInterrupt:
        print("\n\n⏸️ 設定を中断しました。")
        print("いつでも再実行できます: python google_cloud_setup_detailed.py")

if __name__ == "__main__":
    main()