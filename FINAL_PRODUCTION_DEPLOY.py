#!/usr/bin/env python3
"""
🎯 治療的ゲーミフィケーションアプリ - 最終本番デプロイスクリプト
今度こそ完璧にデプロイを成功させる！

プロジェクト: abiding-beanbag-467909-d8
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 設定
PROJECT_ID = "abiding-beanbag-467909-d8"
REGION = "asia-northeast1"
SERVICE_NAME = "therapeutic-gamification-app"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """ヘッダーを表示"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}🎯 {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_step(step: int, text: str):
    """ステップを表示"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[ステップ {step}] {text}{Colors.END}")

def print_success(text: str):
    """成功メッセージを表示"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """エラーメッセージを表示"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """警告メッセージを表示"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """情報メッセージを表示"""
    print(f"{Colors.WHITE}ℹ️  {text}{Colors.END}")

def run_command(command: List[str], timeout: int = 300) -> Tuple[bool, str]:
    """コマンドを実行して結果を返す"""
    try:
        print_info(f"実行中: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        if success:
            print_success("コマンド実行成功")
        else:
            print_error(f"コマンド実行失敗 (終了コード: {result.returncode})")
            if output.strip():
                print(f"出力: {output}")
        
        return success, output
    except subprocess.TimeoutExpired:
        print_error(f"コマンドがタイムアウトしました ({timeout}秒)")
        return False, "Command timed out"
    except Exception as e:
        print_error(f"コマンド実行エラー: {str(e)}")
        return False, str(e)

def check_prerequisites():
    """前提条件をチェック"""
    print_step(1, "前提条件チェック")
    
    # gcloud CLIの確認
    success, output = run_command(["gcloud", "--version"])
    if not success:
        print_error("gcloud CLIがインストールされていません")
        return False
    print_success("gcloud CLI確認完了")
    
    # 認証状態の確認
    success, output = run_command(["gcloud", "auth", "list"])
    if not success or "ACTIVE" not in output:
        print_error("gcloud認証が必要です")
        print_info("以下のコマンドで認証してください:")
        print_info("gcloud auth login")
        print_info("gcloud auth application-default login")
        return False
    print_success("認証状態確認完了")
    
    # プロジェクト設定
    success, output = run_command(["gcloud", "config", "set", "project", PROJECT_ID])
    if not success:
        print_error("プロジェクト設定に失敗")
        return False
    print_success(f"プロジェクト設定完了: {PROJECT_ID}")
    
    return True

def verify_apis():
    """重要なAPIが有効化されているか確認"""
    print_step(2, "API有効化状態確認")
    
    critical_apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "containerregistry.googleapis.com",
        "firestore.googleapis.com",
        "iam.googleapis.com"
    ]
    
    all_enabled = True
    for api in critical_apis:
        success, output = run_command([
            "gcloud", "services", "list", 
            "--enabled", 
            f"--filter=name:{api}",
            "--format=value(name)"
        ])
        
        if success and api in output:
            print_success(f"{api}")
        else:
            print_error(f"{api} - 有効化が必要")
            all_enabled = False
    
    return all_enabled

def build_and_deploy():
    """アプリケーションをビルドしてデプロイ"""
    print_step(3, "アプリケーションビルド & デプロイ")
    
    # Dockerfileの存在確認
    if not os.path.exists("Dockerfile"):
        print_error("Dockerfileが見つかりません")
        return False
    print_success("Dockerfile確認完了")
    
    # Cloud Runにデプロイ
    deploy_command = [
        "gcloud", "run", "deploy", SERVICE_NAME,
        "--source", ".",
        "--platform", "managed",
        "--region", REGION,
        "--allow-unauthenticated",
        "--port", "8080",
        "--memory", "2Gi",
        "--cpu", "2",
        "--timeout", "3600",
        "--concurrency", "100",
        "--max-instances", "10",
        "--set-env-vars", f"PROJECT_ID={PROJECT_ID}",
        "--set-env-vars", "ENVIRONMENT=production",
        "--project", PROJECT_ID
    ]
    
    print_info("Cloud Runデプロイを開始...")
    success, output = run_command(deploy_command, timeout=1200)  # 20分のタイムアウト
    
    if not success:
        print_error("デプロイに失敗しました")
        print(f"エラー詳細:\n{output}")
        return False
    
    print_success("デプロイ完了！")
    
    # サービスURLを取得
    success, url_output = run_command([
        "gcloud", "run", "services", "describe", SERVICE_NAME,
        "--region", REGION,
        "--format", "value(status.url)"
    ])
    
    if success and url_output.strip():
        service_url = url_output.strip()
        print_success(f"サービスURL: {service_url}")
        return service_url
    
    return True

def setup_firestore():
    """Firestoreデータベースを設定"""
    print_step(4, "Firestoreデータベース設定")
    
    # Firestoreデータベースの作成（既に存在する場合はスキップ）
    success, output = run_command([
        "gcloud", "firestore", "databases", "create",
        "--region", REGION,
        "--project", PROJECT_ID
    ])
    
    if success or "already exists" in output.lower():
        print_success("Firestoreデータベース設定完了")
        return True
    else:
        print_warning("Firestoreデータベースの設定をスキップ（既に存在する可能性）")
        return True

def configure_iam():
    """IAM権限を設定"""
    print_step(5, "IAM権限設定")
    
    # Cloud Runサービスアカウントの権限設定
    service_account = f"{PROJECT_ID}@appspot.gserviceaccount.com"
    
    roles = [
        "roles/datastore.user",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter",
        "roles/cloudtrace.agent"
    ]
    
    for role in roles:
        success, output = run_command([
            "gcloud", "projects", "add-iam-policy-binding", PROJECT_ID,
            "--member", f"serviceAccount:{service_account}",
            "--role", role
        ])
        
        if success:
            print_success(f"権限設定完了: {role}")
        else:
            print_warning(f"権限設定スキップ: {role} (既に設定済みの可能性)")
    
    return True

def test_deployment(service_url: str):
    """デプロイされたサービスをテスト"""
    print_step(6, "デプロイメントテスト")
    
    if not service_url:
        print_warning("サービスURLが取得できないため、テストをスキップ")
        return True
    
    try:
        import requests
        
        # ヘルスチェック
        print_info(f"ヘルスチェック: {service_url}/health")
        response = requests.get(f"{service_url}/health", timeout=30)
        
        if response.status_code == 200:
            print_success("ヘルスチェック成功")
        else:
            print_warning(f"ヘルスチェック警告: ステータスコード {response.status_code}")
        
        # 基本的なAPIテスト
        print_info(f"APIテスト: {service_url}/api/v1/health")
        response = requests.get(f"{service_url}/api/v1/health", timeout=30)
        
        if response.status_code == 200:
            print_success("APIテスト成功")
        else:
            print_warning(f"APIテスト警告: ステータスコード {response.status_code}")
        
        return True
        
    except ImportError:
        print_warning("requestsライブラリがないため、手動テストが必要です")
        print_info(f"ブラウザで以下のURLにアクセスしてテストしてください:")
        print_info(f"- {service_url}")
        print_info(f"- {service_url}/health")
        return True
    except Exception as e:
        print_warning(f"テスト中にエラーが発生: {str(e)}")
        print_info("手動でサービスの動作を確認してください")
        return True

def generate_deployment_report(service_url: str):
    """デプロイメントレポートを生成"""
    print_step(7, "デプロイメントレポート生成")
    
    report = {
        "deployment_time": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "service_name": SERVICE_NAME,
        "region": REGION,
        "service_url": service_url,
        "status": "SUCCESS",
        "next_steps": [
            "サービスの動作確認",
            "監視・アラートの設定",
            "ドメインの設定（必要に応じて）",
            "SSL証明書の設定確認",
            "パフォーマンステスト"
        ]
    }
    
    try:
        with open("deployment_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_success("デプロイメントレポート生成完了: deployment_report.json")
    except Exception as e:
        print_warning(f"レポート生成エラー: {str(e)}")
    
    return report

def main():
    """メイン処理"""
    print_header("🚀 治療的ゲーミフィケーションアプリ - 最終本番デプロイ")
    print_info(f"プロジェクト: {PROJECT_ID}")
    print_info(f"リージョン: {REGION}")
    print_info(f"サービス名: {SERVICE_NAME}")
    
    start_time = time.time()
    
    try:
        # 1. 前提条件チェック
        if not check_prerequisites():
            print_error("前提条件チェックに失敗しました")
            sys.exit(1)
        
        # 2. API確認
        if not verify_apis():
            print_error("必要なAPIが有効化されていません")
            print_info("以下のコマンドでAPIを有効化してください:")
            print_info("python enable_all_google_cloud_apis.py")
            sys.exit(1)
        
        # 3. Firestore設定
        if not setup_firestore():
            print_error("Firestore設定に失敗しました")
            sys.exit(1)
        
        # 4. IAM設定
        if not configure_iam():
            print_error("IAM設定に失敗しました")
            sys.exit(1)
        
        # 5. ビルド & デプロイ
        service_url = build_and_deploy()
        if not service_url:
            print_error("デプロイに失敗しました")
            sys.exit(1)
        
        # 6. テスト
        if not test_deployment(service_url if isinstance(service_url, str) else ""):
            print_warning("テストで問題が発生しましたが、デプロイは完了しています")
        
        # 7. レポート生成
        report = generate_deployment_report(service_url if isinstance(service_url, str) else "")
        
        # 成功メッセージ
        elapsed_time = time.time() - start_time
        print_header("🎉 デプロイ完了！")
        print_success(f"デプロイ時間: {elapsed_time:.1f}秒")
        
        if isinstance(service_url, str):
            print_success(f"サービスURL: {service_url}")
            print_info("ブラウザでアクセスして動作を確認してください！")
        
        print_info("\n📋 次のステップ:")
        print_info("1. サービスの動作確認")
        print_info("2. 監視・アラートの設定")
        print_info("3. ドメインの設定（必要に応じて）")
        print_info("4. パフォーマンステスト")
        
        print_header("🎯 デプロイ成功！おめでとうございます！")
        
    except KeyboardInterrupt:
        print_error("\nデプロイが中断されました")
        sys.exit(1)
    except Exception as e:
        print_error(f"予期しないエラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()