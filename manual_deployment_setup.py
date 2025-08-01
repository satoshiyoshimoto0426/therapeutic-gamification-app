#!/usr/bin/env python3
"""
手動デプロイメント準備スクリプト
必要なファイルを準備し、手動でのGitHub操作をガイド
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManualDeploymentSetup:
    """手動デプロイメント準備クラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        
    def create_requirements_txt(self) -> bool:
        """requirements.txt作成"""
        logger.info("requirements.txt作成")
        
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
gunicorn==21.2.0
aiofiles==23.2.1"""
        
        try:
            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write(requirements_content)
            logger.info("requirements.txt作成完了")
            return True
        except Exception as e:
            logger.error(f"requirements.txt作成エラー: {e}")
            return False
    
    def create_dockerfile(self) -> bool:
        """Dockerfile作成"""
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

# 環境変数設定
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# ポート設定
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=10)" || exit 1

# アプリケーション起動
CMD ["python", "-m", "uvicorn", "services.auth.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]"""
        
        try:
            with open("Dockerfile", "w", encoding="utf-8") as f:
                f.write(dockerfile_content)
            logger.info("Dockerfile作成完了")
            return True
        except Exception as e:
            logger.error(f"Dockerfile作成エラー: {e}")
            return False
    
    def create_dockerignore(self) -> bool:
        """.dockerignore作成"""
        logger.info(".dockerignore作成")
        
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
yarn-error.log*
auto_deployment.log
deployment_trigger.txt
manual_deployment_setup.py
quick_deploy.py
github_actions_deploy.py
auto_deployment_setup.py"""
        
        try:
            with open(".dockerignore", "w", encoding="utf-8") as f:
                f.write(dockerignore_content)
            logger.info(".dockerignore作成完了")
            return True
        except Exception as e:
            logger.error(f".dockerignore作成エラー: {e}")
            return False
    
    def create_deployment_trigger(self) -> bool:
        """デプロイメントトリガーファイル作成"""
        logger.info("デプロイメントトリガーファイル作成")
        
        trigger_content = f"""# Deployment Trigger for GitHub Actions
# Generated at: {datetime.now().isoformat()}

DEPLOYMENT_ID={datetime.now().strftime('%Y%m%d_%H%M%S')}
PROJECT_ID={self.project_id}
SERVICE_NAME={self.service_name}
ENVIRONMENT=production
TRIGGER_REASON=manual_deployment_setup
"""
        
        try:
            with open("deployment_trigger.txt", "w", encoding="utf-8") as f:
                f.write(trigger_content)
            logger.info("デプロイメントトリガーファイル作成完了")
            return True
        except Exception as e:
            logger.error(f"デプロイメントトリガーファイル作成エラー: {e}")
            return False
    
    def create_github_secrets_guide(self) -> bool:
        """GitHub Secrets設定ガイド作成"""
        logger.info("GitHub Secrets設定ガイド作成")
        
        guide_content = f"""# GitHub Secrets 設定ガイド

## 🔧 必要なSecrets設定

GitHubリポジトリの **Settings > Secrets and variables > Actions** で以下を設定してください：

### 1. GCP_PROJECT_ID
```
{self.project_id}
```

### 2. GCP_SA_KEY
以下の手順でサービスアカウントキーを生成し、JSON全体をコピー&ペーストしてください：

```bash
# 1. GCPプロジェクト設定
gcloud config set project {self.project_id}

# 2. サービスアカウント作成
gcloud iam service-accounts create github-actions \\
    --description="GitHub Actions CI/CD" \\
    --display-name="GitHub Actions"

# 3. 権限付与
for role in "roles/run.admin" "roles/cloudbuild.builds.editor" "roles/storage.admin" "roles/iam.serviceAccountUser" "roles/datastore.owner" "roles/secretmanager.admin" "roles/logging.viewer"; do
    gcloud projects add-iam-policy-binding {self.project_id} \\
        --member="serviceAccount:github-actions@{self.project_id}.iam.gserviceaccount.com" \\
        --role="$role"
done

# 4. キーファイル生成
gcloud iam service-accounts keys create github-actions-key.json \\
    --iam-account=github-actions@{self.project_id}.iam.gserviceaccount.com

# 5. キーファイル内容をコピー
cat github-actions-key.json
```

### 3. SLACK_WEBHOOK (オプション)
Slack通知用のWebhook URLを設定してください。

## 🚀 デプロイメント実行手順

1. **ファイル準備完了** ✅
   - requirements.txt
   - Dockerfile
   - .dockerignore
   - deployment_trigger.txt

2. **GitHub Secrets設定**
   - 上記の手順でGCP_PROJECT_IDとGCP_SA_KEYを設定

3. **GitHubにプッシュ**
   ```bash
   git add .
   git commit -m "feat: setup automatic deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
   git push origin main
   ```

4. **デプロイメント監視**
   - GitHub ActionsタブでCI/CDパイプラインの進行状況を確認
   - 通常15-20分でデプロイ完了
   - エラー時は自動ロールバック実行

## 📊 デプロイメント後の確認

1. **サービス確認**
   - Cloud Runコンソールでサービス状態確認
   - サービスURLにアクセスして動作確認

2. **ログ確認**
   - Cloud Loggingでアプリケーションログ確認
   - エラーがないかチェック

3. **パフォーマンステスト**
   - 基本機能の動作確認
   - レスポンス時間の確認

## 🆘 トラブルシューティング

### よくある問題

1. **権限エラー**
   - サービスアカウントの権限を再確認
   - 必要なAPIが有効化されているか確認

2. **ビルドエラー**
   - requirements.txtの依存関係を確認
   - Dockerfileの構文を確認

3. **デプロイエラー**
   - Cloud Runの設定を確認
   - メモリ・CPU制限を確認

---

**準備完了！** 上記の手順に従ってデプロイを実行してください。
"""
        
        try:
            with open("DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
                f.write(guide_content)
            logger.info("GitHub Secrets設定ガイド作成完了")
            return True
        except Exception as e:
            logger.error(f"GitHub Secrets設定ガイド作成エラー: {e}")
            return False
    
    def create_health_endpoint(self) -> bool:
        """ヘルスチェックエンドポイント作成"""
        logger.info("ヘルスチェックエンドポイント作成")
        
        # services/auth/main.py にヘルスチェックエンドポイントを追加
        health_endpoint_code = '''
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "therapeutic-gamification-app",
        "version": "1.0.0"
    }
'''
        
        # services/auth/main.py を確認・更新
        auth_main_path = "services/auth/main.py"
        
        if os.path.exists(auth_main_path):
            try:
                with open(auth_main_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # ヘルスチェックエンドポイントが既に存在するかチェック
                if "/health" not in content:
                    # datetime importを追加
                    if "from datetime import datetime" not in content:
                        content = "from datetime import datetime\n" + content
                    
                    # ヘルスチェックエンドポイントを追加
                    content += health_endpoint_code
                    
                    with open(auth_main_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    logger.info("ヘルスチェックエンドポイント追加完了")
                else:
                    logger.info("ヘルスチェックエンドポイント既存")
                
                return True
                
            except Exception as e:
                logger.error(f"ヘルスチェックエンドポイント追加エラー: {e}")
                return False
        else:
            logger.warning("services/auth/main.py が見つかりません")
            return True  # 警告レベルで継続
    
    def run_manual_setup(self) -> bool:
        """手動セットアップ実行"""
        logger.info("🚀 手動デプロイメント準備開始")
        
        success_count = 0
        total_tasks = 5
        
        # 1. requirements.txt作成
        if self.create_requirements_txt():
            success_count += 1
        
        # 2. Dockerfile作成
        if self.create_dockerfile():
            success_count += 1
        
        # 3. .dockerignore作成
        if self.create_dockerignore():
            success_count += 1
        
        # 4. デプロイメントトリガー作成
        if self.create_deployment_trigger():
            success_count += 1
        
        # 5. GitHub Secrets設定ガイド作成
        if self.create_github_secrets_guide():
            success_count += 1
        
        # 6. ヘルスチェックエンドポイント作成
        self.create_health_endpoint()
        
        logger.info(f"✅ 手動デプロイメント準備完了 ({success_count}/{total_tasks})")
        return success_count == total_tasks

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - 手動デプロイメント準備")
    print("=" * 60)
    
    setup = ManualDeploymentSetup()
    
    try:
        success = setup.run_manual_setup()
        
        if success:
            print("\n🎉 デプロイメント準備が完了しました！")
            print("\n📋 作成されたファイル:")
            print("   ✅ requirements.txt")
            print("   ✅ Dockerfile")
            print("   ✅ .dockerignore")
            print("   ✅ deployment_trigger.txt")
            print("   ✅ DEPLOYMENT_GUIDE.md")
            
            print("\n📖 次のステップ:")
            print("1. DEPLOYMENT_GUIDE.md を開いて設定手順を確認")
            print("2. GitHub Secrets を設定")
            print("3. 変更をGitHubにプッシュしてデプロイ開始")
            
            print("\n🔗 重要なリンク:")
            print("   - GitHub Secrets設定: リポジトリ > Settings > Secrets and variables > Actions")
            print("   - GitHub Actions監視: リポジトリ > Actions タブ")
            print("   - Cloud Run管理: https://console.cloud.google.com/run")
            
        else:
            print("\n❌ 一部のファイル作成に失敗しました。ログを確認してください。")
        
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()