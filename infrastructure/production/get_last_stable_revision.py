#!/usr/bin/env python3
"""
最後に安定したリビジョンを取得するスクリプト
"""

import argparse
import json
import subprocess
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RevisionManager:
    """リビジョン管理クラス"""
    
    def __init__(self, service_name: str, region: str = "asia-northeast1"):
        self.service_name = service_name
        self.region = region
    
    def run_command(self, command: List[str]) -> tuple[bool, str, str]:
        """コマンド実行"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
    
    def get_deployment_history(self) -> List[Dict]:
        """デプロイメント履歴を取得"""
        try:
            # デプロイメント記録ファイルから履歴を取得
            import glob
            import os
            
            deployment_files = glob.glob("deployment_record_*.json")
            deployments = []
            
            for file_path in deployment_files:
                try:
                    with open(file_path, 'r') as f:
                        deployment = json.load(f)
                        if deployment.get("service_name") == self.service_name:
                            deployments.append(deployment)
                except Exception as e:
                    logger.warning(f"デプロイメント記録読み込みエラー: {file_path}, {e}")
            
            # タイムスタンプでソート（新しい順）
            deployments.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return deployments
            
        except Exception as e:
            logger.error(f"デプロイメント履歴取得エラー: {e}")
            return []
    
    def get_cloud_run_revisions(self) -> List[str]:
        """Cloud Runのリビジョン一覧を取得"""
        command = [
            "gcloud", "run", "revisions", "list",
            "--service", self.service_name,
            "--region", self.region,
            "--format", "json",
            "--sort-by", "~metadata.creationTimestamp"
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success and stdout.strip():
            try:
                revisions = json.loads(stdout)
                return [rev["metadata"]["name"] for rev in revisions]
            except json.JSONDecodeError:
                logger.error("リビジョン一覧のJSON解析エラー")
                return []
        else:
            logger.error(f"リビジョン一覧取得エラー: {stderr}")
            return []
    
    def get_current_revision(self) -> Optional[str]:
        """現在のリビジョンを取得"""
        command = [
            "gcloud", "run", "services", "describe", self.service_name,
            "--region", self.region,
            "--format", "value(status.latestReadyRevisionName)"
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success and stdout.strip():
            return stdout.strip()
        return None
    
    def is_revision_healthy(self, revision: str) -> bool:
        """リビジョンの健全性をチェック"""
        try:
            # リビジョンの詳細情報を取得
            command = [
                "gcloud", "run", "revisions", "describe", revision,
                "--region", self.region,
                "--format", "json"
            ]
            
            success, stdout, stderr = self.run_command(command)
            
            if success and stdout.strip():
                revision_info = json.loads(stdout)
                
                # ステータスチェック
                conditions = revision_info.get("status", {}).get("conditions", [])
                for condition in conditions:
                    if condition.get("type") == "Ready":
                        return condition.get("status") == "True"
                
                return False
            else:
                logger.warning(f"リビジョン情報取得失敗: {revision}")
                return False
                
        except Exception as e:
            logger.error(f"リビジョン健全性チェックエラー: {e}")
            return False
    
    def get_last_stable_revision(self) -> Optional[str]:
        """最後に安定したリビジョンを取得"""
        current_revision = self.get_current_revision()
        logger.info(f"現在のリビジョン: {current_revision}")
        
        # 1. デプロイメント履歴から成功したリビジョンを探す
        deployment_history = self.get_deployment_history()
        
        for deployment in deployment_history:
            if deployment.get("status") in ["DEPLOY_SUCCESS", "ROLLBACK_SUCCESS"]:
                revision = deployment.get("revision")
                if revision and revision != current_revision:
                    # リビジョンが実際に存在し、健全かチェック
                    if self.is_revision_healthy(revision):
                        logger.info(f"デプロイメント履歴から安定リビジョン発見: {revision}")
                        return revision
                    else:
                        logger.warning(f"リビジョンが不健全: {revision}")
        
        # 2. Cloud Runのリビジョン一覧から健全なリビジョンを探す
        revisions = self.get_cloud_run_revisions()
        
        for revision in revisions:
            if revision != current_revision:
                if self.is_revision_healthy(revision):
                    logger.info(f"Cloud Runから安定リビジョン発見: {revision}")
                    return revision
                else:
                    logger.warning(f"リビジョンが不健全: {revision}")
        
        logger.warning("安定したリビジョンが見つかりませんでした")
        return None
    
    def get_revision_metrics(self, revision: str, hours: int = 1) -> Dict:
        """リビジョンのメトリクスを取得"""
        try:
            # Cloud Monitoringからメトリクスを取得
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 簡易的なメトリクス取得（実際の実装では、Cloud Monitoring APIを使用）
            command = [
                "gcloud", "logging", "read",
                f'resource.type="cloud_run_revision" AND resource.labels.revision_name="{revision}"',
                "--limit", "100",
                "--format", "json",
                f"--freshness", f"{hours}h"
            ]
            
            success, stdout, stderr = self.run_command(command)
            
            if success and stdout.strip():
                logs = json.loads(stdout)
                
                error_count = sum(1 for log in logs if log.get("severity") in ["ERROR", "CRITICAL"])
                total_requests = len(logs)
                
                return {
                    "revision": revision,
                    "total_requests": total_requests,
                    "error_count": error_count,
                    "error_rate": error_count / max(total_requests, 1),
                    "period_hours": hours
                }
            else:
                return {
                    "revision": revision,
                    "total_requests": 0,
                    "error_count": 0,
                    "error_rate": 0.0,
                    "period_hours": hours
                }
                
        except Exception as e:
            logger.error(f"メトリクス取得エラー: {e}")
            return {
                "revision": revision,
                "total_requests": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "period_hours": hours
            }
    
    def get_best_rollback_candidate(self) -> Optional[str]:
        """最適なロールバック候補を取得"""
        current_revision = self.get_current_revision()
        revisions = self.get_cloud_run_revisions()
        
        candidates = []
        
        for revision in revisions[:5]:  # 最新5つのリビジョンを評価
            if revision == current_revision:
                continue
            
            if not self.is_revision_healthy(revision):
                continue
            
            # メトリクスを取得
            metrics = self.get_revision_metrics(revision, hours=24)
            
            # スコア計算（エラー率が低く、リクエスト数が多いほど高スコア）
            error_rate = metrics["error_rate"]
            total_requests = metrics["total_requests"]
            
            # エラー率が5%以上の場合は候補から除外
            if error_rate > 0.05:
                continue
            
            score = total_requests * (1 - error_rate)
            
            candidates.append({
                "revision": revision,
                "score": score,
                "metrics": metrics
            })
        
        if candidates:
            # スコアでソートして最適な候補を返す
            candidates.sort(key=lambda x: x["score"], reverse=True)
            best_candidate = candidates[0]
            
            logger.info(f"最適なロールバック候補: {best_candidate['revision']} (スコア: {best_candidate['score']:.2f})")
            return best_candidate["revision"]
        
        return None

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="最後に安定したリビジョンを取得")
    parser.add_argument("--service", required=True, help="Cloud Runサービス名")
    parser.add_argument("--region", default="asia-northeast1", help="リージョン")
    parser.add_argument("--best-candidate", action="store_true", help="最適なロールバック候補を取得")
    parser.add_argument("--metrics", action="store_true", help="メトリクス情報も表示")
    
    args = parser.parse_args()
    
    revision_manager = RevisionManager(args.service, args.region)
    
    try:
        if args.best_candidate:
            revision = revision_manager.get_best_rollback_candidate()
        else:
            revision = revision_manager.get_last_stable_revision()
        
        if revision:
            print(revision)
            
            if args.metrics:
                metrics = revision_manager.get_revision_metrics(revision)
                print(f"メトリクス: {json.dumps(metrics, indent=2)}", file=sys.stderr)
            
            sys.exit(0)
        else:
            logger.error("安定したリビジョンが見つかりませんでした")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()