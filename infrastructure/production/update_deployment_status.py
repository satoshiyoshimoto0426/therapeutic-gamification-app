#!/usr/bin/env python3
"""
デプロイメント状況更新スクリプト
Firestoreにデプロイメント状況を記録し、ダッシュボードで表示可能にする
"""

import argparse
import json
import sys
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStatusManager:
    """デプロイメント状況管理クラス"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        # 実際の実装では、Firestore SDKを初期化
        # from google.cloud import firestore
        # self.db = firestore.Client(project=project_id)
        
    def update_deployment_status(self, deployment_data: Dict) -> bool:
        """デプロイメント状況を更新"""
        try:
            # Firestoreのdeploymentsコレクションに記録
            deployment_record = {
                "deployment_id": deployment_data["deployment_id"],
                "service_name": deployment_data["service_name"],
                "revision": deployment_data["revision"],
                "image_url": deployment_data["image_url"],
                "commit_sha": deployment_data["commit_sha"],
                "status": deployment_data["status"],
                "environment": deployment_data.get("environment", "production"),
                "region": deployment_data.get("region", "asia-northeast1"),
                "timestamp": deployment_data["timestamp"],
                "metadata": deployment_data.get("metadata", {})
            }
            
            # 実際の実装では、Firestoreに保存
            # doc_ref = self.db.collection('deployments').document(deployment_data["deployment_id"])
            # doc_ref.set(deployment_record)
            
            # 現在は、ローカルファイルに保存
            filename = f"deployment_status_{deployment_data['deployment_id']}.json"
            with open(filename, "w") as f:
                json.dump(deployment_record, f, indent=2)
            
            logger.info(f"デプロイメント状況更新: {deployment_data['deployment_id']} -> {deployment_data['status']}")
            
            # 最新デプロイメント状況も更新
            self.update_latest_deployment_status(deployment_record)
            
            return True
            
        except Exception as e:
            logger.error(f"デプロイメント状況更新エラー: {e}")
            return False
    
    def update_latest_deployment_status(self, deployment_record: Dict) -> bool:
        """最新デプロイメント状況を更新"""
        try:
            service_name = deployment_record["service_name"]
            environment = deployment_record["environment"]
            
            latest_status = {
                "service_name": service_name,
                "environment": environment,
                "latest_deployment": deployment_record,
                "last_updated": datetime.now().isoformat()
            }
            
            # 実際の実装では、Firestoreの latest_deployments コレクションに保存
            filename = f"latest_deployment_{service_name}_{environment}.json"
            with open(filename, "w") as f:
                json.dump(latest_status, f, indent=2)
            
            logger.info(f"最新デプロイメント状況更新: {service_name} ({environment})")
            return True
            
        except Exception as e:
            logger.error(f"最新デプロイメント状況更新エラー: {e}")
            return False
    
    def get_deployment_history(self, service_name: str, limit: int = 10) -> list:
        """デプロイメント履歴を取得"""
        try:
            # 実際の実装では、Firestoreから取得
            # deployments = self.db.collection('deployments')\
            #     .where('service_name', '==', service_name)\
            #     .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            #     .limit(limit)\
            #     .stream()
            
            # 現在は、ローカルファイルから取得
            import glob
            deployment_files = glob.glob(f"deployment_status_*.json")
            deployments = []
            
            for file_path in deployment_files:
                try:
                    with open(file_path, 'r') as f:
                        deployment = json.load(f)
                        if deployment.get("service_name") == service_name:
                            deployments.append(deployment)
                except Exception as e:
                    logger.warning(f"デプロイメント記録読み込みエラー: {file_path}, {e}")
            
            # タイムスタンプでソート
            deployments.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return deployments[:limit]
            
        except Exception as e:
            logger.error(f"デプロイメント履歴取得エラー: {e}")
            return []
    
    def get_deployment_statistics(self, service_name: str, days: int = 30) -> Dict:
        """デプロイメント統計を取得"""
        try:
            deployments = self.get_deployment_history(service_name, limit=100)
            
            # 指定日数以内のデプロイメントをフィルタ
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent_deployments = []
            for deployment in deployments:
                try:
                    deployment_time = datetime.fromisoformat(deployment["timestamp"].replace("Z", "+00:00"))
                    if deployment_time >= cutoff_date:
                        recent_deployments.append(deployment)
                except Exception:
                    continue
            
            # 統計計算
            total_deployments = len(recent_deployments)
            successful_deployments = sum(1 for d in recent_deployments if d["status"] in ["DEPLOY_SUCCESS", "ROLLBACK_SUCCESS"])
            failed_deployments = sum(1 for d in recent_deployments if "FAILED" in d["status"])
            rollback_count = sum(1 for d in recent_deployments if "ROLLBACK" in d["status"])
            
            success_rate = successful_deployments / total_deployments if total_deployments > 0 else 0
            
            statistics = {
                "service_name": service_name,
                "period_days": days,
                "total_deployments": total_deployments,
                "successful_deployments": successful_deployments,
                "failed_deployments": failed_deployments,
                "rollback_count": rollback_count,
                "success_rate": success_rate,
                "last_deployment": recent_deployments[0] if recent_deployments else None,
                "generated_at": datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"デプロイメント統計取得エラー: {e}")
            return {}
    
    def create_deployment_dashboard_data(self, service_names: list) -> Dict:
        """デプロイメントダッシュボード用データを作成"""
        try:
            dashboard_data = {
                "generated_at": datetime.now().isoformat(),
                "services": {}
            }
            
            for service_name in service_names:
                # 最新デプロイメント状況
                try:
                    with open(f"latest_deployment_{service_name}_production.json", 'r') as f:
                        latest_deployment = json.load(f)
                except FileNotFoundError:
                    latest_deployment = None
                
                # 統計情報
                statistics = self.get_deployment_statistics(service_name)
                
                # 最近のデプロイメント履歴
                recent_history = self.get_deployment_history(service_name, limit=5)
                
                dashboard_data["services"][service_name] = {
                    "latest_deployment": latest_deployment,
                    "statistics": statistics,
                    "recent_history": recent_history
                }
            
            # ダッシュボードデータを保存
            with open("deployment_dashboard.json", "w") as f:
                json.dump(dashboard_data, f, indent=2)
            
            logger.info("デプロイメントダッシュボードデータ作成完了")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"ダッシュボードデータ作成エラー: {e}")
            return {}

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="デプロイメント状況更新")
    parser.add_argument("--project-id", help="GCPプロジェクトID")
    parser.add_argument("--deployment-id", help="デプロイメントID")
    parser.add_argument("--service", help="サービス名")
    parser.add_argument("--revision", help="リビジョン名")
    parser.add_argument("--image", help="イメージURL")
    parser.add_argument("--commit", help="コミットSHA")
    parser.add_argument("--status", help="デプロイメント状況")
    parser.add_argument("--environment", default="production", help="環境")
    parser.add_argument("--region", default="asia-northeast1", help="リージョン")
    
    # 操作モード
    parser.add_argument("--get-history", help="デプロイメント履歴取得（サービス名指定）")
    parser.add_argument("--get-statistics", help="デプロイメント統計取得（サービス名指定）")
    parser.add_argument("--create-dashboard", nargs='+', help="ダッシュボードデータ作成（サービス名リスト）")
    
    args = parser.parse_args()
    
    if not args.project_id:
        args.project_id = "therapeutic-gamification-app"  # デフォルト値
    
    status_manager = DeploymentStatusManager(args.project_id)
    
    try:
        if args.get_history:
            # デプロイメント履歴取得
            history = status_manager.get_deployment_history(args.get_history)
            print(json.dumps(history, indent=2))
            
        elif args.get_statistics:
            # デプロイメント統計取得
            statistics = status_manager.get_deployment_statistics(args.get_statistics)
            print(json.dumps(statistics, indent=2))
            
        elif args.create_dashboard:
            # ダッシュボードデータ作成
            dashboard_data = status_manager.create_deployment_dashboard_data(args.create_dashboard)
            print(json.dumps(dashboard_data, indent=2))
            
        else:
            # デプロイメント状況更新
            if not all([args.deployment_id, args.service, args.revision, args.status]):
                logger.error("デプロイメント状況更新には --deployment-id, --service, --revision, --status が必要です")
                sys.exit(1)
            
            deployment_data = {
                "deployment_id": args.deployment_id,
                "service_name": args.service,
                "revision": args.revision,
                "image_url": args.image or "",
                "commit_sha": args.commit or "",
                "status": args.status,
                "environment": args.environment,
                "region": args.region,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "updated_by": "ci_cd_pipeline"
                }
            }
            
            success = status_manager.update_deployment_status(deployment_data)
            
            if success:
                logger.info("デプロイメント状況更新完了")
                sys.exit(0)
            else:
                logger.error("デプロイメント状況更新失敗")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()