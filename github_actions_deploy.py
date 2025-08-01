#!/usr/bin/env python3
"""
GitHub Actions経由での自動デプロイメント実行スクリプト
Windows環境でも動作するGitHub Actions CI/CDパイプライン実行
"""

import os
import subprocess
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubActionsDeploy:
    """GitHub Actions デプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        
    def run_command(self, command: List[str], check: bool = True, shell: bool = False) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            logger.info(f"実行中: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=check,
                shell=shell
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            logger.error(f"コマンド実行エラー: {e}")
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            logger.error("コマンドタイムアウト")
            return False, "", "Command timed out"
    
    def check_git_status(self) -> bool:
        """Git状態確認"""
        logger.info("Git状態確認")
        
        # Gitリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "status"], check=False)
        
        if not success:
            logger.error("Gitリポジトリではありません")
            return False
        
        # リモートリポジトリ確認
        success, stdout, stderr = self.run_command(["git", "remote", "-v"], check=False)
        
        if success and "github.com" in stdout:
            logger.info("GitHubリポジトリ確認済み")
            return True
        else:
            logger.error("GitHubリモートリポジトリが設定されていません")
            return False
    
    def check_github_secrets(self) -> Dict[str, bool]:
        """GitHub Secrets設定状況確認"""
        logger.info("GitHub Secrets設定状況確認")
        
        # GitHub CLIが利用可能かチェック
        success, stdout, stderr = self.run_command(["gh", "--version"], check=False)
        
        secrets_status = {
            "gh_cli_available": success,
            "gcp_project_id": False,
            "gcp_sa_key": False,
            "slack_webhook": False
        }
        
        if success:
            # GitHub Secretsリスト取得
            success, stdout, stderr = self.run_command(["gh", "secret", "list"], check=False)
            
            if success:
                secrets_list = stdout.lower()
                secrets_status["gcp_project_id"] = "gcp_project_id" in secrets_list
                secrets_status["gcp_sa_key"] = "gcp_sa_key" in secrets_list
                secrets_status["slack_webhook"] = "slack_webhook" in secrets_list
        
        return secrets_status
    
    def prepare_deployment_files(self) -> bool:
        """デプロイメントファイル準備"""
        logger.info("デプロイメントファイル準備")
        
        # requirements.txtの確認・更新
        requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
google-cloud-firestore==2.13.1
google-cloud-secret-manager==2.17.0
google-auth==2.25.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
requests==2.31.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
gunicorn==21.2.0"""
        
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)
        
        logger.info("requirements.txt更新完了")
        
        # Dockerfileの確認
        if not os.path.exists("Dockerfile"):
            logger.info("Dockerfile作成")
            dockerfile_content = """# マルチステージビルド
FROM python:3.12-slim as builder

# 作業ディレクトリ設定
WORKDIR /app

# システム依存関係インストール
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Python依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番ステージ
FROM python:3.12-slim

# 作業ディレクトリ設定
WORKDIR /app

# 非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# ビルドステージから依存関係をコピー
COPY --from=builder /root/.local /home/appuser/.local

# アプリケーションコードをコピー
COPY . .

# 権限設定
RUN chown -R appuser:appuser /app
USER appuser

# PATHにローカルbinを追加
ENV PATH=/home/appuser/.local/bin:$PATH

# ポート設定
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=10)"

# アプリケーション起動
CMD ["uvicorn", "services.auth.main:app", "--host", "0.0.0.0", "--port", "8080"]"""
            
            with open("Dockerfile", "w", encoding="utf-8") as f:
                f.write(dockerfile_content)
        
        # .dockerignoreの作成
        dockerignore_content = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.vscode
.idea
*.swp
*.swo
*~
.DS_Store
node_modules
.env
.env.local
.env.*.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*"""
        
        with open(".dockerignore", "w", encoding="utf-8") as f:
            f.write(dockerignore_content)
        
        logger.info("デプロイメントファイル準備完了")
        return True
    
    def create_deployment_trigger_file(self) -> bool:
        """デプロイメントトリガーファイル作成"""
        logger.info("デプロイメントトリガーファイル作成")
        
        trigger_content = f"""# Deployment Trigger
# This file triggers GitHub Actions deployment
# Generated at: {datetime.now().isoformat()}

DEPLOYMENT_ID={datetime.now().strftime('%Y%m%d_%H%M%S')}
PROJECT_ID={self.project_id}
SERVICE_NAME={self.service_name}
ENVIRONMENT=production
"""
        
        with open("deployment_trigger.txt", "w", encoding="utf-8") as f:
            f.write(trigger_content)
        
        logger.info("デプロイメントトリガーファイル作成完了")
        return True
    
    def commit_and_push(self) -> bool:
        """コミット・プッシュ実行"""
        logger.info("Git コミット・プッシュ開始")
        
        # 変更をステージング
        success, stdout, stderr = self.run_command(["git", "add", "."])
        
        if not success:
            logger.error(f"git add失敗: {stderr}")
            return False
        
        # コミット
        commit_message = f"feat: trigger automatic deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = self.run_command([
            "git", "commit", "-m", commit_message
        ], check=False)
        
        if not success and "nothing to commit" not in stderr:
            logger.error(f"git commit失敗: {stderr}")
            return False
        
        # プッシュ
        success, stdout, stderr = self.run_command(["git", "push", "origin", "main"])
        
        if success:
            logger.info("Git プッシュ成功")
            return True
        else:
            logger.error(f"git push失敗: {stderr}")
            return False
    
    def get_github_actions_url(self) -> Optional[str]:
        """GitHub ActionsのURLを取得"""
        success, stdout, stderr = self.run_command(["git", "remote", "get-url", "origin"], check=False)
        
        if success:
            repo_url = stdout.strip().replace(".git", "")
            if "github.com" in repo_url:
                # SSH URLをHTTPS URLに変換
                if repo_url.startswith("git@github.com:"):
                    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
                
                actions_url = f"{repo_url}/actions"
                return actions_url
        
        return None
    
    def display_deployment_info(self, secrets_status: Dict[str, bool]) -> None:
        """デプロイメント情報表示"""
        print("\n" + "=" * 60)
        print("🚀 GitHub Actions デプロイメント情報")
        print("=" * 60)
        
        # GitHub Secrets設定状況
        print("\n📋 GitHub Secrets設定状況:")
        for secret, status in secrets_status.items():
            if secret == "gh_cli_available":
                continue
            
            status_icon = "✅" if status else "❌"
            secret_name = secret.upper()
            print(f"   {status_icon} {secret_name}")
        
        # 未設定のSecretsがある場合の案内
        missing_secrets = [k.upper() for k, v in secrets_status.items() if not v and k != "gh_cli_available"]
        
        if missing_secrets:
            print(f"\n⚠️ 未設定のSecrets: {', '.join(missing_secrets)}")
            print("\n🔧 GitHub Secrets設定方法:")
            print("1. GitHubリポジトリページを開く")
            print("2. Settings > Secrets and variables > Actions")
            print("3. 'New repository secret' をクリック")
            print("4. 以下の情報を設定:")
            
            if "GCP_PROJECT_ID" in missing_secrets:
                print(f"   - Name: GCP_PROJECT_ID")
                print(f"   - Value: {self.project_id}")
            
            if "GCP_SA_KEY" in missing_secrets:
                print(f"   - Name: GCP_SA_KEY")
                print(f"   - Value: [サービスアカウントキーのJSON全体]")
        
        # GitHub ActionsのURL
        actions_url = self.get_github_actions_url()
        if actions_url:
            print(f"\n🔗 GitHub Actions URL:")
            print(f"   {actions_url}")
        
        print(f"\n📊 デプロイメント監視:")
        print(f"   - GitHub Actionsタブでビルド・デプロイ進行状況を確認")
        print(f"   - 通常15-20分でデプロイ完了")
        print(f"   - エラー時は自動ロールバック実行")
    
    def run_github_actions_deploy(self) -> bool:
        """GitHub Actions デプロイ実行"""
        logger.info("🚀 GitHub Actions デプロイ開始")
        
        # 1. Git状態確認
        if not self.check_git_status():
            return False
        
        # 2. GitHub Secrets確認
        secrets_status = self.check_github_secrets()
        
        # 3. デプロイメントファイル準備
        if not self.prepare_deployment_files():
            return False
        
        # 4. デプロイメントトリガーファイル作成
        if not self.create_deployment_trigger_file():
            return False
        
        # 5. コミット・プッシュ
        if not self.commit_and_push():
            return False
        
        # 6. デプロイメント情報表示
        self.display_deployment_info(secrets_status)
        
        logger.info("✅ GitHub Actions デプロイトリガー完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - GitHub Actions デプロイ")
    print("=" * 60)
    
    deploy = GitHubActionsDeploy()
    
    try:
        success = deploy.run_github_actions_deploy()
        
        if success:
            print("\n🎉 GitHub Actions デプロイトリガーが完了しました！")
            print("\n次のステップ:")
            print("1. GitHub ActionsタブでCI/CDパイプラインの進行状況を確認")
            print("2. 必要に応じてGitHub Secretsを設定")
            print("3. デプロイ完了後、本番環境での動作確認")
            print("4. エラー時は自動ロールバックが実行されます")
            sys.exit(0)
        else:
            print("\n❌ デプロイトリガーに失敗しました。ログを確認してください。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()