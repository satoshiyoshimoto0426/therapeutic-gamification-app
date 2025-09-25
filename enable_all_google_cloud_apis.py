#!/usr/bin/env python3
"""
Google Cloud APIs 一括有効化スクリプト
治療的ゲーミフィケーションアプリのデプロイに必要な全てのAPIを有効化します
"""

import subprocess
import sys
import time
from typing import List, Dict

# プロジェクトID
PROJECT_ID = "abiding-beanbag-467909-d8"

# 必要なAPIのリスト
REQUIRED_APIS = [
    # Core APIs
    "run.googleapis.com",                    # Cloud Run
    "cloudbuild.googleapis.com",             # Cloud Build
    "containerregistry.googleapis.com",     # Container Registry
    "artifactregistry.googleapis.com",      # Artifact Registry
    
    # Database & Storage
    "firestore.googleapis.com",             # Firestore
    "storage-api.googleapis.com",           # Cloud Storage
    "storage-component.googleapis.com",     # Cloud Storage Component
    
    # Security & IAM
    "iam.googleapis.com",                   # Identity and Access Management
    "iamcredentials.googleapis.com",        # IAM Service Account Credentials
    "cloudresourcemanager.googleapis.com",  # Cloud Resource Manager
    "secretmanager.googleapis.com",         # Secret Manager
    
    # Networking & Security
    "compute.googleapis.com",               # Compute Engine (for VPC, etc.)
    "servicenetworking.googleapis.com",     # Service Networking
    "vpcaccess.googleapis.com",             # VPC Access
    
    # Monitoring & Logging
    "logging.googleapis.com",               # Cloud Logging
    "monitoring.googleapis.com",            # Cloud Monitoring
    "cloudtrace.googleapis.com",            # Cloud Trace
    "clouderrorreporting.googleapis.com",   # Error Reporting
    
    # AI & ML (if needed)
    "aiplatform.googleapis.com",            # Vertex AI
    "translate.googleapis.com",             # Translation API
    
    # Additional Services
    "cloudfunctions.googleapis.com",        # Cloud Functions
    "cloudscheduler.googleapis.com",        # Cloud Scheduler
    "pubsub.googleapis.com",                # Pub/Sub
    
    # Security
    "cloudkms.googleapis.com",              # Cloud KMS
    "binaryauthorization.googleapis.com",   # Binary Authorization
    
    # Networking Security
    "dns.googleapis.com",                   # Cloud DNS
    "certificatemanager.googleapis.com",    # Certificate Manager
]

def run_command(command: List[str]) -> tuple[bool, str]:
    """コマンドを実行して結果を返す"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def check_gcloud_auth():
    """gcloud認証状態をチェック"""
    print("🔍 gcloud認証状態をチェック中...")
    success, output = run_command(["gcloud", "auth", "list"])
    
    if not success:
        print("❌ gcloud認証に問題があります")
        print("以下のコマンドで認証してください:")
        print("gcloud auth login")
        print("gcloud auth application-default login")
        return False
    
    print("✅ gcloud認証OK")
    return True

def set_project():
    """プロジェクトを設定"""
    print(f"🔧 プロジェクト {PROJECT_ID} を設定中...")
    success, output = run_command(["gcloud", "config", "set", "project", PROJECT_ID])
    
    if not success:
        print(f"❌ プロジェクト設定に失敗: {output}")
        return False
    
    print("✅ プロジェクト設定完了")
    return True

def check_api_status(api: str) -> bool:
    """APIが有効かどうかチェック"""
    success, output = run_command([
        "gcloud", "services", "list", 
        "--enabled", 
        f"--filter=name:{api}",
        "--format=value(name)"
    ])
    
    return success and api in output

def enable_api(api: str) -> bool:
    """APIを有効化"""
    print(f"🔄 {api} を有効化中...")
    
    # まず現在の状態をチェック
    if check_api_status(api):
        print(f"✅ {api} は既に有効です")
        return True
    
    # APIを有効化
    success, output = run_command([
        "gcloud", "services", "enable", api, 
        f"--project={PROJECT_ID}"
    ])
    
    if success:
        print(f"✅ {api} の有効化完了")
        return True
    else:
        print(f"❌ {api} の有効化に失敗: {output}")
        return False

def enable_all_apis():
    """全てのAPIを有効化"""
    print(f"\n🚀 {len(REQUIRED_APIS)}個のAPIを有効化開始...")
    
    enabled_count = 0
    failed_apis = []
    
    for i, api in enumerate(REQUIRED_APIS, 1):
        print(f"\n[{i}/{len(REQUIRED_APIS)}] {api}")
        
        if enable_api(api):
            enabled_count += 1
            # API有効化後の待機時間
            time.sleep(2)
        else:
            failed_apis.append(api)
    
    print(f"\n📊 結果:")
    print(f"✅ 成功: {enabled_count}/{len(REQUIRED_APIS)}")
    
    if failed_apis:
        print(f"❌ 失敗: {len(failed_apis)}")
        print("失敗したAPI:")
        for api in failed_apis:
            print(f"  - {api}")
        return False
    else:
        print("🎉 全てのAPIの有効化が完了しました！")
        return True

def verify_critical_apis():
    """重要なAPIが有効化されているか確認"""
    critical_apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "firestore.googleapis.com",
        "iam.googleapis.com"
    ]
    
    print("\n🔍 重要なAPIの確認中...")
    all_good = True
    
    for api in critical_apis:
        if check_api_status(api):
            print(f"✅ {api}")
        else:
            print(f"❌ {api}")
            all_good = False
    
    return all_good

def main():
    """メイン処理"""
    print("=" * 60)
    print("🌟 Google Cloud APIs 一括有効化スクリプト")
    print("=" * 60)
    
    # 1. gcloud認証チェック
    if not check_gcloud_auth():
        sys.exit(1)
    
    # 2. プロジェクト設定
    if not set_project():
        sys.exit(1)
    
    # 3. 全APIを有効化
    if not enable_all_apis():
        print("\n⚠️  一部のAPIの有効化に失敗しましたが、続行します...")
    
    # 4. 重要なAPIの確認
    if verify_critical_apis():
        print("\n🎉 重要なAPIは全て有効化されています！")
    else:
        print("\n⚠️  一部の重要なAPIが有効化されていません")
    
    print("\n📝 次のステップ:")
    print("1. GitHub Actionsでデプロイを再実行してください")
    print("2. エラーが続く場合は、Google Cloud Consoleで手動確認してください")
    print(f"3. プロジェクトURL: https://console.cloud.google.com/apis/dashboard?project={PROJECT_ID}")

if __name__ == "__main__":
    main()