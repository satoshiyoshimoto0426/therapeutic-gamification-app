#!/usr/bin/env python3
"""
📊 デプロイメント監視スクリプト
デプロイ後のサービス状態を監視・確認
"""

import subprocess
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ID = "abiding-beanbag-467909-d8"
REGION = "asia-northeast1"
SERVICE_NAME = "therapeutic-gamification-app"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_status(text: str, status: str = "info"):
    """ステータスメッセージを表示"""
    colors = {
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE
    }
    color = colors.get(status, Colors.BLUE)
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    icon = icons.get(status, "ℹ️")
    print(f"{color}{icon} {text}{Colors.END}")

def run_command(command: List[str]) -> tuple[bool, str]:
    """コマンドを実行"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def get_service_url() -> Optional[str]:
    """サービスURLを取得"""
    success, output = run_command([
        "gcloud", "run", "services", "describe", SERVICE_NAME,
        "--region", REGION,
        "--format", "value(status.url)",
        "--project", PROJECT_ID
    ])
    
    if success and output:
        return output
    return None

def check_service_status():
    """Cloud Runサービスの状態確認"""
    print_status("Cloud Runサービス状態確認中...", "info")
    
    success, output = run_command([
        "gcloud", "run", "services", "describe", SERVICE_NAME,
        "--region", REGION,
        "--format", "json",
        "--project", PROJECT_ID
    ])
    
    if not success:
        print_status("サービス情報の取得に失敗", "error")
        return False
    
    try:
        service_info = json.loads(output)
        
        # サービス状態
        status = service_info.get("status", {})
        conditions = status.get("conditions", [])
        
        for condition in conditions:
            condition_type = condition.get("type", "")
            condition_status = condition.get("status", "")
            
            if condition_type == "Ready":
                if condition_status == "True":
                    print_status("サービスは正常に稼働中", "success")
                else:
                    print_status(f"サービス状態: {condition_status}", "warning")
                    reason = condition.get("reason", "")
                    message = condition.get("message", "")
                    if reason:
                        print_status(f"理由: {reason}", "info")
                    if message:
                        print_status(f"メッセージ: {message}", "info")
        
        # URL情報
        url = status.get("url", "")
        if url:
            print_status(f"サービスURL: {url}", "success")
        
        # トラフィック情報
        traffic = status.get("traffic", [])
        for t in traffic:
            percent = t.get("percent", 0)
            revision = t.get("revisionName", "")
            print_status(f"トラフィック: {percent}% -> {revision}", "info")
        
        return True
        
    except json.JSONDecodeError:
        print_status("サービス情報の解析に失敗", "error")
        return False

def test_endpoints(service_url: str):
    """エンドポイントのテスト"""
    print_status("エンドポイントテスト開始...", "info")
    
    endpoints = [
        ("/", "メインページ"),
        ("/health", "ヘルスチェック"),
        ("/api/v1/health", "APIヘルスチェック"),
        ("/api/v1/auth/status", "認証状態"),
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        url = f"{service_url}{endpoint}"
        try:
            print_status(f"テスト中: {description} ({endpoint})", "info")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print_status(f"✓ {description}: OK (200)", "success")
                results[endpoint] = {"status": "success", "code": 200}
            elif response.status_code == 404:
                print_status(f"- {description}: Not Found (404)", "warning")
                results[endpoint] = {"status": "not_found", "code": 404}
            else:
                print_status(f"! {description}: {response.status_code}", "warning")
                results[endpoint] = {"status": "warning", "code": response.status_code}
                
        except requests.exceptions.Timeout:
            print_status(f"✗ {description}: タイムアウト", "error")
            results[endpoint] = {"status": "timeout", "code": None}
        except requests.exceptions.ConnectionError:
            print_status(f"✗ {description}: 接続エラー", "error")
            results[endpoint] = {"status": "connection_error", "code": None}
        except Exception as e:
            print_status(f"✗ {description}: エラー ({str(e)})", "error")
            results[endpoint] = {"status": "error", "code": None, "error": str(e)}
    
    return results

def check_logs():
    """最新のログを確認"""
    print_status("最新ログ確認中...", "info")
    
    success, output = run_command([
        "gcloud", "logs", "read",
        f"resource.type=cloud_run_revision AND resource.labels.service_name={SERVICE_NAME}",
        "--limit", "10",
        "--format", "value(timestamp,severity,textPayload)",
        "--project", PROJECT_ID
    ])
    
    if success and output:
        print_status("最新ログ (最新10件):", "info")
        lines = output.split('\n')
        for line in lines[:10]:  # 最新10件のみ表示
            if line.strip():
                print(f"  {line}")
    else:
        print_status("ログの取得に失敗またはログが存在しません", "warning")

def check_metrics():
    """基本的なメトリクスを確認"""
    print_status("メトリクス確認中...", "info")
    
    # リクエスト数の確認
    success, output = run_command([
        "gcloud", "logging", "read",
        f'resource.type="cloud_run_revision" AND resource.labels.service_name="{SERVICE_NAME}"',
        "--limit", "1",
        "--format", "value(timestamp)",
        "--project", PROJECT_ID
    ])
    
    if success and output:
        print_status("サービスにアクティビティが確認されました", "success")
    else:
        print_status("まだアクティビティが記録されていません", "info")

def generate_monitoring_report(service_url: str, test_results: Dict):
    """監視レポートを生成"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "service_name": SERVICE_NAME,
        "region": REGION,
        "service_url": service_url,
        "endpoint_tests": test_results,
        "overall_status": "healthy" if all(r.get("status") == "success" for r in test_results.values()) else "issues_detected"
    }
    
    try:
        with open("monitoring_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_status("監視レポート生成完了: monitoring_report.json", "success")
    except Exception as e:
        print_status(f"レポート生成エラー: {str(e)}", "error")
    
    return report

def main():
    """メイン処理"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 治療的ゲーミフィケーションアプリ - デプロイメント監視{Colors.END}")
    print(f"プロジェクト: {PROJECT_ID}")
    print(f"サービス: {SERVICE_NAME}")
    print(f"リージョン: {REGION}")
    
    # サービスURL取得
    service_url = get_service_url()
    if not service_url:
        print_status("サービスURLの取得に失敗", "error")
        print_status("サービスがデプロイされていない可能性があります", "warning")
        return
    
    print_status(f"監視対象URL: {service_url}", "info")
    
    # 1. サービス状態確認
    print(f"\n{Colors.BOLD}1. サービス状態確認{Colors.END}")
    check_service_status()
    
    # 2. エンドポイントテスト
    print(f"\n{Colors.BOLD}2. エンドポイントテスト{Colors.END}")
    test_results = test_endpoints(service_url)
    
    # 3. ログ確認
    print(f"\n{Colors.BOLD}3. ログ確認{Colors.END}")
    check_logs()
    
    # 4. メトリクス確認
    print(f"\n{Colors.BOLD}4. メトリクス確認{Colors.END}")
    check_metrics()
    
    # 5. レポート生成
    print(f"\n{Colors.BOLD}5. レポート生成{Colors.END}")
    report = generate_monitoring_report(service_url, test_results)
    
    # サマリー
    print(f"\n{Colors.BOLD}{Colors.CYAN}📋 監視サマリー{Colors.END}")
    
    success_count = sum(1 for r in test_results.values() if r.get("status") == "success")
    total_count = len(test_results)
    
    if success_count == total_count:
        print_status(f"全てのエンドポイントが正常 ({success_count}/{total_count})", "success")
        print_status("🎉 デプロイメントは成功しています！", "success")
    else:
        print_status(f"一部のエンドポイントに問題 ({success_count}/{total_count})", "warning")
        print_status("詳細を確認して必要に応じて修正してください", "warning")
    
    print(f"\n{Colors.BOLD}次のステップ:{Colors.END}")
    print("1. ブラウザでサービスにアクセスして動作確認")
    print("2. 継続的な監視の設定")
    print("3. アラートの設定")
    print("4. パフォーマンステストの実行")

if __name__ == "__main__":
    main()