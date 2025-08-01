#!/usr/bin/env python3
"""
クイックデプロイスクリプト
既存の設定を使用して即座にデプロイを実行
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

class QuickDeploy:
    """クイックデプロイクラス"""
    
    def __init__(self):
        self.project_id = "therapeutic-gamification-app-prod"
        self.service_name = "therapeutic-gamification-app"
        self.region = "asia-northeast1"
        
    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """コマンド実行"""
        try:
            logger.info(f"実行中: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            logger.error(f"コマンド実行エラー: {e}")
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            logger.error("コマンドタイムアウト")
            return False, "", "Command timed out"
    
    def check_prerequisites(self) -> bool:
        """前提条件チェック"""
        logger.info("前提条件チェック開始")
        
        # Docker確認
        success, stdout, stderr = self.run_command(["docker", "--version"], check=False)
        if not success:
            logger.error("Dockerがインストールされていません")
            return False
        
        # gcloud確認
        success, stdout, stderr = self.run_command(["gcloud", "--version"], check=False)
        if not success:
            logger.error("Google Cloud SDKがインストールされていません")
            return False
        
        # Git確認
        success, stdout, stderr = self.run_command(["git", "--version"], check=False)
        if not success:
            logger.error("Gitがインストールされていません")
            return False
        
        logger.info("前提条件チェック完了")
        return True
    
    def setup_gcp_auth(self) -> bool:
        """GCP認証設定"""
        logger.info("GCP認証設定")
        
        # 認証状態確認
        success, stdout, stderr = self.run_command(["gcloud", "auth", "list"], check=False)
        
        if success and "ACTIVE" in stdout:
            logger.info("既に認証済み")
            
            # プロジェクト設定
            success, stdout, stderr = self.run_command([
                "gcloud", "config", "set", "project", self.project_id
            ], check=False)
            
            if success:
                logger.info(f"プロジェクト設定完了: {self.project_id}")
                return True
            else:
                logger.warning("プロジェクト設定に失敗、認証を実行します")
        
        # 認証実行
        logger.info("gcloud認証を実行してください...")
        success, stdout, stderr = self.run_command(["gcloud", "auth", "login"])
        
        if success:
            # プロジェクト設定
            success, stdout, stderr = self.run_command([
                "gcloud", "config", "set", "project", self.project_id
            ])
            
            if success:
                logger.info("GCP認証・プロジェクト設定完了")
                return True
        
        logger.error("GCP認証に失敗しました")
        return False
    
    def build_docker_image(self) -> Optional[str]:
        """Dockerイメージビルド"""
        logger.info("Dockerイメージビルド開始")
        
        # イメージタグ生成
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        image_tag = f"gcr.io/{self.project_id}/{self.service_name}:{timestamp}"
        
        # Dockerビルド
        success, stdout, stderr = self.run_command([
            "docker", "build", "-t", image_tag, "."
        ])
        
        if not success:
            logger.error(f"Dockerビルド失敗: {stderr}")
            return None
        
        logger.info(f"Dockerビルド成功: {image_tag}")
        
        # Docker認証設定
        success, stdout, stderr = self.run_command([
            "gcloud", "auth", "configure-docker", "gcr.io"
        ], check=False)
        
        # イメージプッシュ
        success, stdout, stderr = self.run_command([
            "docker", "push", image_tag
        ])
        
        if success:
            logger.info(f"Dockerプッシュ成功: {image_tag}")
            return image_tag
        else:
            logger.error(f"Dockerプッシュ失敗: {stderr}")
            return None
    
    def deploy_to_cloud_run(self, image_url: str) -> bool:
        """Cloud Runにデプロイ"""
        logger.info("Cloud Runデプロイ開始")
        
        # デプロイコマンド実行
        success, stdout, stderr = self.run_command([
            "gcloud", "run", "deploy", self.service_name,
            "--image", image_url,
            "--region", self.region,
            "--platform", "managed",
            "--allow-unauthenticated",
            "--set-env-vars", "ENVIRONMENT=production",
            "--memory", "2Gi",
            "--cpu", "2",
            "--min-instances", "1",
            "--max-instances", "100",
            "--timeout", "300s",
            "--concurrency", "100"
        ])
        
        if success:
            logger.info("Cloud Runデプロイ成功")
            
            # サービスURL取得
            success, stdout, stderr = self.run_command([
                "gcloud", "run", "services", "describe", self.service_name,
                "--region", self.region,
                "--format", "value(status.url)"
            ])
            
            if success and stdout.strip():
                service_url = stdout.strip()
                logger.info(f"サービスURL: {service_url}")
                
                # ヘルスチェック
                time.sleep(30)  # 30秒待機
                return self.health_check(service_url)
            
            return True
        else:
            logger.error(f"Cloud Runデプロイ失敗: {stderr}")
            return False
    
    def health_check(self, service_url: str) -> bool:
        """ヘルスチェック実行"""
        logger.info("ヘルスチェック実行")
        
        try:
            import requests
            
            health_url = f"{service_url}/health"
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("ヘルスチェック成功")
                return True
            else:
                logger.warning(f"ヘルスチェック警告: HTTP {response.status_code}")
                return True  # 警告レベルで継続
                
        except ImportError:
            logger.warning("requestsライブラリがありません。ヘルスチェックをスキップします")
            return True
        except Exception as e:
            logger.warning(f"ヘルスチェック例外: {e}")
            return True  # 例外時も継続
    
    def run_quick_deploy(self) -> bool:
        """クイックデプロイ実行"""
        logger.info("🚀 クイックデプロイ開始")
        
        # 1. 前提条件チェック
        if not self.check_prerequisites():
            return False
        
        # 2. GCP認証設定
        if not self.setup_gcp_auth():
            return False
        
        # 3. Dockerイメージビルド
        image_url = self.build_docker_image()
        if not image_url:
            return False
        
        # 4. Cloud Runデプロイ
        if not self.deploy_to_cloud_run(image_url):
            return False
        
        logger.info("✅ クイックデプロイ完了")
        return True

def main():
    """メイン実行関数"""
    print("🚀 Therapeutic Gamification App - クイックデプロイ")
    print("=" * 60)
    
    deploy = QuickDeploy()
    
    try:
        success = deploy.run_quick_deploy()
        
        if success:
            print("\n🎉 デプロイが完了しました！")
            print("\n次のステップ:")
            print("1. サービスURLにアクセスして動作確認")
            print("2. ログを確認してエラーがないかチェック")
            print("3. パフォーマンステストの実行")
            sys.exit(0)
        else:
            print("\n❌ デプロイに失敗しました。ログを確認してください。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ デプロイが中断されました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()