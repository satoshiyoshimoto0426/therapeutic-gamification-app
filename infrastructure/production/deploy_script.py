#!/usr/bin/env python3
"""
自動デプロイメントスクリプト
Blue-Green デプロイメント、ヘルスチェック、ロールバック機能を提供
"""

import argparse
import json
import subprocess
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """デプロイメント管理クラス"""
    
    def __init__(self, project_id: str, service_name: str, region: str = "asia-northeast1"):
        self.project_id = project_id
        self.service_name = service_name
        self.region = region
        self.deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
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
    
    def get_current_revision(self) -> Optional[str]:
        """現在のリビジョンを取得"""
        success, stdout, stderr = self.run_command([
            "gcloud", "run", "services", "describe", self.service_name,
            "--region", self.region,
            "--format", "value(status.latestReadyRevisionName)"
        ], check=False)
        
        if success and stdout.strip():
            return stdout.strip()
        return None
    
    def get_service_url(self) -> Optional[str]:
        """サービスURLを取得"""
        success, stdout, stderr = self.run_command([
            "gcloud", "run", "services", "describe", self.service_name,
            "--region", self.region,
            "--format", "value(status.url)"
        ], check=False)
        
        if success and stdout.strip():
            return stdout.strip()
        return None
    
    def health_check(self, url: str, timeout: int = 30) -> bool:
        """ヘルスチェック実行"""
        health_url = f"{url}/health"
        
        try:
            logger.info(f"ヘルスチェック実行: {health_url}")
            response = requests.get(health_url, timeout=timeout)
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    logger.info("ヘルスチェック成功")
                    return True
                else:
                    logger.error(f"ヘルスチェック失敗: {health_data}")
                    return False
            else:
                logger.error(f"ヘルスチェック失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"ヘルスチェックエラー: {e}")
            return False
    
    def deploy_new_revision(self, image_url: str, environment: str = "production") -> Optional[str]:
        """新しいリビジョンをデプロイ"""
        revision_suffix = self.deployment_id.replace("deploy-", "")
        
        # 環境別設定
        env_config = {
            "production": {
                "memory": "2Gi",
                "cpu": "2",
                "min_instances": "5",
                "max_instances": "1000",
                "concurrency": "100"
            },
            "staging": {
                "memory": "1Gi",
                "cpu": "1",
                "min_instances": "1",
                "max_instances": "10",
                "concurrency": "50"
            }
        }
        
        config = env_config.get(environment, env_config["staging"])
        
        command = [
            "gcloud", "run", "deploy", self.service_name,
            "--image", image_url,
            "--region", self.region,
            "--platform", "managed",
            "--allow-unauthenticated",
            "--set-env-vars", f"ENVIRONMENT={environment}",
            "--memory", config["memory"],
            "--cpu", config["cpu"],
            "--min-instances", config["min_instances"],
            "--max-instances", config["max_instances"],
            "--timeout", "300s",
            "--concurrency", config["concurrency"],
            "--revision-suffix", revision_suffix,
            "--no-traffic"  # トラフィックは後で段階的に移行
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success:
            new_revision = f"{self.service_name}-{revision_suffix}"
            logger.info(f"新しいリビジョンデプロイ成功: {new_revision}")
            return new_revision
        else:
            logger.error(f"デプロイ失敗: {stderr}")
            return None
    
    def update_traffic(self, revision: str, percentage: int) -> bool:
        """トラフィック配分を更新"""
        command = [
            "gcloud", "run", "services", "update-traffic", self.service_name,
            "--region", self.region,
            "--to-revisions", f"{revision}={percentage}"
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success:
            logger.info(f"トラフィック更新成功: {revision} -> {percentage}%")
            return True
        else:
            logger.error(f"トラフィック更新失敗: {stderr}")
            return False
    
    def gradual_traffic_migration(self, new_revision: str, service_url: str) -> bool:
        """段階的トラフィック移行"""
        migration_steps = [
            (10, 60),   # 10% -> 1分待機
            (25, 120),  # 25% -> 2分待機
            (50, 180),  # 50% -> 3分待機
            (75, 120),  # 75% -> 2分待機
            (100, 0)    # 100% -> 完了
        ]
        
        for percentage, wait_time in migration_steps:
            logger.info(f"トラフィック {percentage}% に移行中...")
            
            if not self.update_traffic(new_revision, percentage):
                logger.error(f"トラフィック移行失敗: {percentage}%")
                return False
            
            if wait_time > 0:
                logger.info(f"{wait_time}秒待機中...")
                time.sleep(wait_time)
                
                # ヘルスチェック実行
                if not self.health_check(service_url):
                    logger.error(f"ヘルスチェック失敗 at {percentage}%")
                    return False
                
                # エラー率チェック
                if not self.check_error_rate(percentage_threshold=5.0):
                    logger.error(f"エラー率が高すぎます at {percentage}%")
                    return False
        
        logger.info("段階的トラフィック移行完了")
        return True
    
    def check_error_rate(self, percentage_threshold: float = 5.0) -> bool:
        """エラー率チェック"""
        try:
            # Cloud Monitoring APIを使用してエラー率を取得
            command = [
                "gcloud", "logging", "read",
                f'resource.type="cloud_run_revision" AND resource.labels.service_name="{self.service_name}" AND severity>=ERROR',
                "--limit", "100",
                "--format", "json",
                "--freshness", "5m"
            ]
            
            success, stdout, stderr = self.run_command(command, check=False)
            
            if success:
                logs = json.loads(stdout) if stdout.strip() else []
                error_count = len(logs)
                
                # 簡易的なエラー率計算（実際の実装では、より詳細な計算が必要）
                if error_count > 10:  # 5分間で10件以上のエラー
                    logger.warning(f"エラー数が多すぎます: {error_count}")
                    return False
                
                logger.info(f"エラー率チェック通過: {error_count} errors in 5 minutes")
                return True
            else:
                logger.warning("エラー率チェックに失敗、継続します")
                return True
                
        except Exception as e:
            logger.warning(f"エラー率チェック例外: {e}")
            return True  # チェック失敗時は継続
    
    def rollback_to_revision(self, revision: str) -> bool:
        """指定されたリビジョンにロールバック"""
        logger.info(f"ロールバック実行: {revision}")
        
        if not self.update_traffic(revision, 100):
            return False
        
        # ロールバック後のヘルスチェック
        service_url = self.get_service_url()
        if service_url:
            time.sleep(30)  # 30秒待機
            return self.health_check(service_url)
        
        return True
    
    def get_previous_stable_revision(self) -> Optional[str]:
        """前回の安定したリビジョンを取得"""
        try:
            # デプロイメント履歴から最後に成功したリビジョンを取得
            command = [
                "gcloud", "run", "revisions", "list",
                "--service", self.service_name,
                "--region", self.region,
                "--format", "value(metadata.name)",
                "--sort-by", "~metadata.creationTimestamp",
                "--limit", "5"
            ]
            
            success, stdout, stderr = self.run_command(command, check=False)
            
            if success and stdout.strip():
                revisions = stdout.strip().split('\n')
                # 現在のリビジョンを除く最新のリビジョンを返す
                current_revision = self.get_current_revision()
                for revision in revisions:
                    if revision != current_revision:
                        logger.info(f"前回の安定リビジョン: {revision}")
                        return revision
            
            return None
            
        except Exception as e:
            logger.error(f"前回リビジョン取得エラー: {e}")
            return None
    
    def cleanup_old_revisions(self, keep_count: int = 3) -> bool:
        """古いリビジョンをクリーンアップ"""
        try:
            command = [
                "gcloud", "run", "revisions", "list",
                "--service", self.service_name,
                "--region", self.region,
                "--format", "value(metadata.name)",
                "--sort-by", "~metadata.creationTimestamp"
            ]
            
            success, stdout, stderr = self.run_command(command, check=False)
            
            if success and stdout.strip():
                revisions = stdout.strip().split('\n')
                old_revisions = revisions[keep_count:]  # 最新N個を保持
                
                for revision in old_revisions:
                    delete_command = [
                        "gcloud", "run", "revisions", "delete", revision,
                        "--region", self.region,
                        "--quiet"
                    ]
                    
                    success, _, _ = self.run_command(delete_command, check=False)
                    if success:
                        logger.info(f"古いリビジョン削除: {revision}")
                    else:
                        logger.warning(f"リビジョン削除失敗: {revision}")
                
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"リビジョンクリーンアップエラー: {e}")
            return False
    
    def record_deployment(self, status: str, revision: str, image_url: str, commit_sha: str = "") -> bool:
        """デプロイメント記録"""
        deployment_record = {
            "deployment_id": self.deployment_id,
            "service_name": self.service_name,
            "revision": revision,
            "image_url": image_url,
            "commit_sha": commit_sha,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "region": self.region
        }
        
        try:
            # Firestoreに記録（実際の実装では、Firestore SDKを使用）
            with open(f"deployment_record_{self.deployment_id}.json", "w") as f:
                json.dump(deployment_record, f, indent=2)
            
            logger.info(f"デプロイメント記録保存: {self.deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"デプロイメント記録エラー: {e}")
            return False

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="自動デプロイメントスクリプト")
    parser.add_argument("--project-id", required=True, help="GCPプロジェクトID")
    parser.add_argument("--service-name", required=True, help="Cloud Runサービス名")
    parser.add_argument("--image-url", required=True, help="デプロイするDockerイメージURL")
    parser.add_argument("--region", default="asia-northeast1", help="デプロイリージョン")
    parser.add_argument("--environment", default="production", choices=["production", "staging"], help="デプロイ環境")
    parser.add_argument("--commit-sha", default="", help="コミットSHA")
    parser.add_argument("--rollback", action="store_true", help="ロールバック実行")
    parser.add_argument("--rollback-revision", help="ロールバック先リビジョン")
    parser.add_argument("--dry-run", action="store_true", help="ドライラン実行")
    
    args = parser.parse_args()
    
    # デプロイメントマネージャー初期化
    deployment_manager = DeploymentManager(
        project_id=args.project_id,
        service_name=args.service_name,
        region=args.region
    )
    
    try:
        if args.rollback:
            # ロールバック実行
            logger.info("ロールバック開始")
            
            rollback_revision = args.rollback_revision
            if not rollback_revision:
                rollback_revision = deployment_manager.get_previous_stable_revision()
            
            if not rollback_revision:
                logger.error("ロールバック先リビジョンが見つかりません")
                sys.exit(1)
            
            if args.dry_run:
                logger.info(f"[DRY RUN] ロールバック先: {rollback_revision}")
                sys.exit(0)
            
            success = deployment_manager.rollback_to_revision(rollback_revision)
            
            if success:
                deployment_manager.record_deployment("ROLLBACK_SUCCESS", rollback_revision, "", args.commit_sha)
                logger.info("ロールバック完了")
                sys.exit(0)
            else:
                deployment_manager.record_deployment("ROLLBACK_FAILED", rollback_revision, "", args.commit_sha)
                logger.error("ロールバック失敗")
                sys.exit(1)
        
        else:
            # 通常デプロイメント実行
            logger.info(f"デプロイメント開始: {args.image_url}")
            
            if args.dry_run:
                logger.info(f"[DRY RUN] デプロイ対象: {args.image_url}")
                sys.exit(0)
            
            # 現在のリビジョンを記録（ロールバック用）
            current_revision = deployment_manager.get_current_revision()
            logger.info(f"現在のリビジョン: {current_revision}")
            
            # 新しいリビジョンをデプロイ
            new_revision = deployment_manager.deploy_new_revision(args.image_url, args.environment)
            
            if not new_revision:
                deployment_manager.record_deployment("DEPLOY_FAILED", "", args.image_url, args.commit_sha)
                logger.error("デプロイ失敗")
                sys.exit(1)
            
            # サービスURLを取得
            service_url = deployment_manager.get_service_url()
            if not service_url:
                logger.error("サービスURL取得失敗")
                sys.exit(1)
            
            # 新しいリビジョンのヘルスチェック
            revision_url = f"https://{new_revision}---{args.service_name}-{args.region}.a.run.app"
            if not deployment_manager.health_check(revision_url):
                logger.error("新しいリビジョンのヘルスチェック失敗")
                deployment_manager.record_deployment("HEALTH_CHECK_FAILED", new_revision, args.image_url, args.commit_sha)
                sys.exit(1)
            
            # 段階的トラフィック移行
            if args.environment == "production":
                success = deployment_manager.gradual_traffic_migration(new_revision, service_url)
            else:
                # ステージング環境では即座に100%移行
                success = deployment_manager.update_traffic(new_revision, 100)
            
            if success:
                # 古いリビジョンをクリーンアップ
                deployment_manager.cleanup_old_revisions()
                
                deployment_manager.record_deployment("DEPLOY_SUCCESS", new_revision, args.image_url, args.commit_sha)
                logger.info("デプロイメント完了")
                sys.exit(0)
            else:
                # デプロイ失敗時のロールバック
                logger.error("デプロイ失敗、ロールバック実行")
                
                if current_revision:
                    rollback_success = deployment_manager.rollback_to_revision(current_revision)
                    if rollback_success:
                        deployment_manager.record_deployment("DEPLOY_FAILED_ROLLBACK_SUCCESS", current_revision, args.image_url, args.commit_sha)
                        logger.info("ロールバック完了")
                    else:
                        deployment_manager.record_deployment("DEPLOY_FAILED_ROLLBACK_FAILED", current_revision, args.image_url, args.commit_sha)
                        logger.error("ロールバック失敗")
                else:
                    deployment_manager.record_deployment("DEPLOY_FAILED_NO_ROLLBACK", "", args.image_url, args.commit_sha)
                
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("デプロイメント中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()