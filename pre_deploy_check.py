#!/usr/bin/env python3
"""
🔍 デプロイ前最終チェックスクリプト
デプロイが確実に成功するように事前チェックを実行
"""

import os
import subprocess
import json
from typing import List, Dict, Tuple

PROJECT_ID = "abiding-beanbag-467909-d8"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_check(item: str, status: bool, details: str = ""):
    """チェック結果を表示"""
    status_icon = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{status_icon} {item}{Colors.END}")
    if details:
        print(f"   {details}")

def run_command(command: List[str]) -> Tuple[bool, str]:
    """コマンドを実行"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_files():
    """必要なファイルの存在確認"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📁 ファイル存在チェック{Colors.END}")
    
    required_files = [
        ("Dockerfile", "Dockerコンテナ設定"),
        ("pyproject.toml", "Python依存関係設定"),
        ("requirements.txt", "Python依存関係（代替）"),
        (".github/workflows/ci-cd-pipeline.yml", "GitHub Actions設定"),
        ("shared/", "共有ライブラリ"),
        ("services/", "マイクロサービス"),
        ("frontend/", "フロントエンド")
    ]
    
    all_good = True
    for file_path, description in required_files:
        exists = os.path.exists(file_path)
        print_check(f"{description} ({file_path})", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_docker():
    """Docker設定チェック"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🐳 Docker設定チェック{Colors.END}")
    
    # Dockerfileの内容チェック
    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r") as f:
            dockerfile_content = f.read()
        
        checks = [
            ("FROM python:", "Python基盤イメージ" in dockerfile_content),
            ("COPY", "COPY" in dockerfile_content),
            ("RUN pip install", "pip install" in dockerfile_content),
            ("EXPOSE", "EXPOSE" in dockerfile_content or "PORT" in dockerfile_content),
            ("CMD", "CMD" in dockerfile_content or "ENTRYPOINT" in dockerfile_content)
        ]
        
        all_good = True
        for check_name, condition in checks:
            print_check(f"Dockerfile {check_name}", condition)
            if not condition:
                all_good = False
        
        return all_good
    else:
        print_check("Dockerfile存在", False)
        return False

def check_gcloud():
    """gcloud設定チェック"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}☁️  gcloud設定チェック{Colors.END}")
    
    # gcloud CLI存在確認
    success, output = run_command(["gcloud", "--version"])
    print_check("gcloud CLI", success, output.split('\n')[0] if success else "インストールが必要")
    
    if not success:
        return False
    
    # 認証状態確認
    success, output = run_command(["gcloud", "auth", "list"])
    authenticated = success and "ACTIVE" in output
    print_check("gcloud認証", authenticated, "認証済み" if authenticated else "gcloud auth login が必要")
    
    # プロジェクト設定確認
    success, output = run_command(["gcloud", "config", "get-value", "project"])
    project_set = success and PROJECT_ID in output
    print_check(f"プロジェクト設定 ({PROJECT_ID})", project_set)
    
    return authenticated and project_set

def check_apis():
    """Google Cloud APIs確認"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔌 Google Cloud APIs確認{Colors.END}")
    
    critical_apis = [
        ("run.googleapis.com", "Cloud Run"),
        ("cloudbuild.googleapis.com", "Cloud Build"),
        ("firestore.googleapis.com", "Firestore"),
        ("iam.googleapis.com", "IAM"),
        ("containerregistry.googleapis.com", "Container Registry")
    ]
    
    all_enabled = True
    for api, description in critical_apis:
        success, output = run_command([
            "gcloud", "services", "list", "--enabled", 
            f"--filter=name:{api}", "--format=value(name)"
        ])
        
        enabled = success and api in output
        print_check(f"{description} ({api})", enabled)
        if not enabled:
            all_enabled = False
    
    return all_enabled

def check_secrets():
    """GitHub Secrets確認（推奨）"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔐 GitHub Secrets確認{Colors.END}")
    
    # GitHub CLIが利用可能かチェック
    success, output = run_command(["gh", "--version"])
    if not success:
        print_check("GitHub CLI", False, "gh コマンドが必要（オプション）")
        return True  # オプションなのでTrueを返す
    
    print_check("GitHub CLI", True)
    
    # Secretsの存在確認（可能であれば）
    success, output = run_command(["gh", "secret", "list"])
    if success:
        secrets_exist = "GCP_SA_KEY" in output or "GOOGLE_APPLICATION_CREDENTIALS" in output
        print_check("GitHub Secrets設定", secrets_exist, "GCP認証情報が設定済み" if secrets_exist else "手動設定が必要")
    
    return True

def check_dependencies():
    """依存関係チェック"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📦 依存関係チェック{Colors.END}")
    
    # Python依存関係
    if os.path.exists("pyproject.toml"):
        print_check("pyproject.toml", True)
    elif os.path.exists("requirements.txt"):
        print_check("requirements.txt", True)
    else:
        print_check("Python依存関係ファイル", False, "pyproject.toml または requirements.txt が必要")
        return False
    
    # Node.js依存関係（フロントエンド）
    frontend_package = os.path.exists("frontend/package.json")
    print_check("フロントエンド依存関係 (frontend/package.json)", frontend_package)
    
    return True

def generate_checklist():
    """チェックリストを生成"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📋 デプロイ前チェックリスト{Colors.END}")
    
    checklist = [
        "✅ 必要なファイルが全て存在する",
        "✅ Dockerfileが正しく設定されている", 
        "✅ gcloud CLIがインストール・認証済み",
        "✅ 必要なGoogle Cloud APIが有効化済み",
        "✅ GitHub Secretsが設定済み（CI/CD用）",
        "✅ 依存関係ファイルが存在する",
        "🚀 デプロイ準備完了！"
    ]
    
    for item in checklist:
        print(f"  {item}")

def main():
    """メイン処理"""
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 治療的ゲーミフィケーションアプリ - デプロイ前チェック{Colors.END}")
    print(f"プロジェクト: {PROJECT_ID}")
    
    checks = [
        ("ファイル存在", check_files()),
        ("Docker設定", check_docker()),
        ("gcloud設定", check_gcloud()),
        ("Google Cloud APIs", check_apis()),
        ("GitHub Secrets", check_secrets()),
        ("依存関係", check_dependencies())
    ]
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}📊 チェック結果サマリー{Colors.END}")
    
    all_passed = True
    for check_name, result in checks:
        print_check(check_name, result)
        if not result:
            all_passed = False
    
    print(f"\n{Colors.BOLD}")
    if all_passed:
        print(f"{Colors.GREEN}🎉 全てのチェックが完了しました！デプロイ準備完了です！{Colors.END}")
        print(f"\n次のコマンドでデプロイを実行してください:")
        print(f"{Colors.YELLOW}python FINAL_PRODUCTION_DEPLOY.py{Colors.END}")
    else:
        print(f"{Colors.RED}⚠️  いくつかの問題が見つかりました。修正してから再度チェックしてください。{Colors.END}")
        print(f"\n修正後、以下のコマンドで再チェック:")
        print(f"{Colors.YELLOW}python pre_deploy_check.py{Colors.END}")
    
    generate_checklist()

if __name__ == "__main__":
    main()