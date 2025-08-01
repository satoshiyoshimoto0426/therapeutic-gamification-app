#!/usr/bin/env python3
"""
デプロイメント後監視スクリプト
デプロイ後の一定期間、システムの健全性を監視し、問題があればアラートを送信
"""

import argparse
import json
import time
import logging
import sys
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostDeploymentMonitor:
    """デプロイメント後監視クラス"""
    
    def __init__(self, service_name: str, region: str = "asia-northeast1"):
        self.service_name = service_name
        self.region = region
        self.monitoring_active = True
        self.alert_queue = queue.Queue()
        
        # 監視閾値
        self.thresholds = {
            "error_rate": 0.05,      # 5%
            "response_time_p95": 1200,  # 1.2秒（ミリ秒）
            "cpu_utilization": 0.8,   # 80%
            "memory_utilization": 0.8, # 80%
            "request_rate_drop": 0.5   # 50%減少
        }
        
        # ベースラインメトリクス
        self.baseline_metrics = {}
    
    def run_command(self, command: List[str]) -> Tuple[bool, str, str]:
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
    
    def get_service_url(self) -> Optional[str]:
        """サービスURLを取得"""
        command = [
            "gcloud", "run", "services", "describe", self.service_name,
            "--region", self.region,
            "--format", "value(status.url)"
        ]
        
        success, stdout, stderr = self.run_command(command)
        
        if success and stdout.strip():
            return stdout.strip()
        return None
    
    def health_check(self, url: str) -> Dict:
        """ヘルスチェック実行"""
        health_url = f"{url}/health"
        
        try:
            start_time = time.time()
            response = requests.get(health_url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # ミリ秒
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_error_rate(self, minutes: int = 5) -> float:
        """エラー率を取得"""
        try:
            # Cloud Loggingからエラーログを取得
            command = [
                "gcloud", "logging", "read",
                f'resource.type="cloud_run_revision" AND resource.labels.service_name="{self.service_name}" AND severity>=ERROR',
                "--limit", "1000",
                "--format", "json",
                f"--freshness", f"{minutes}m"
            ]
            
            success, stdout, stderr = self.run_command(command)
            
            if success and stdout.strip():
                error_logs = json.loads(stdout)
                error_count = len(error_logs)
            else:
                error_count = 0
            
            # 全リクエスト数を取得
            command = [
                "gcloud", "logging", "read",
                f'resource.type="cloud_run_revision" AND resource.labels.service_name="{self.service_name}"',
                "--limit", "1000",
                "--format", "json",
                f"--freshness", f"{minutes}m"
            ]
            
            success, stdout, stderr = self.run_command(command)
            
            if success and stdout.strip():
                all_logs = json.loads(stdout)
                total_count = len(all_logs)
            else:
                total_count = 0
            
            if total_count > 0:
                error_rate = error_count / total_count
            else:
                error_rate = 0.0
            
            logger.info(f"エラー率: {error_rate:.3f} ({error_count}/{total_count})")
            return error_rate
            
        except Exception as e:
            logger.error(f"エラー率取得エラー: {e}")
            return 0.0
    
    def get_response_time_metrics(self, minutes: int = 5) -> Dict:
        """レスポンス時間メトリクスを取得"""
        try:
            # Cloud Monitoringからレスポンス時間を取得
            # 実際の実装では、Cloud Monitoring APIを使用
            
            # 簡易的な実装として、ヘルスチェックのレスポンス時間を使用
            service_url = self.get_service_url()
            if not service_url:
                return {"p95": 0, "avg": 0, "count": 0}
            
            response_times = []
            for _ in range(10):  # 10回測定
                health_result = self.health_check(service_url)
                if health_result.get("response_time"):
                    response_times.append(health_result["response_time"])
                time.sleep(1)
            
            if response_times:
                response_times.sort()
                count = len(response_times)
                avg = sum(response_times) / count
                p95_index = int(count * 0.95)
                p95 = response_times[p95_index] if p95_index < count else response_times[-1]
                
                return {"p95": p95, "avg": avg, "count": count}
            else:
                return {"p95": 0, "avg": 0, "count": 0}
                
        except Exception as e:
            logger.error(f"レスポンス時間取得エラー: {e}")
            return {"p95": 0, "avg": 0, "count": 0}
    
    def get_resource_utilization(self) -> Dict:
        """リソース使用率を取得"""
        try:
            # Cloud Monitoringからリソース使用率を取得
            # 実際の実装では、Cloud Monitoring APIを使用
            
            # 簡易的な実装として、固定値を返す
            return {
                "cpu_utilization": 0.3,  # 30%
                "memory_utilization": 0.4,  # 40%
                "instance_count": 5
            }
            
        except Exception as e:
            logger.error(f"リソース使用率取得エラー: {e}")
            return {
                "cpu_utilization": 0.0,
                "memory_utilization": 0.0,
                "instance_count": 0
            }
    
    def collect_metrics(self) -> Dict:
        """メトリクス収集"""
        logger.info("メトリクス収集中...")
        
        # 各種メトリクスを並行して取得
        error_rate = self.get_error_rate()
        response_metrics = self.get_response_time_metrics()
        resource_metrics = self.get_resource_utilization()
        
        service_url = self.get_service_url()
        health_result = self.health_check(service_url) if service_url else {"status": "unknown"}
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "service_name": self.service_name,
            "health_status": health_result.get("status"),
            "error_rate": error_rate,
            "response_time_p95": response_metrics.get("p95", 0),
            "response_time_avg": response_metrics.get("avg", 0),
            "cpu_utilization": resource_metrics.get("cpu_utilization", 0),
            "memory_utilization": resource_metrics.get("memory_utilization", 0),
            "instance_count": resource_metrics.get("instance_count", 0)
        }
        
        return metrics
    
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """閾値チェック"""
        alerts = []
        
        # エラー率チェック
        if metrics["error_rate"] > self.thresholds["error_rate"]:
            alerts.append({
                "type": "error_rate",
                "severity": "critical",
                "message": f"エラー率が閾値を超過: {metrics['error_rate']:.3f} > {self.thresholds['error_rate']:.3f}",
                "value": metrics["error_rate"],
                "threshold": self.thresholds["error_rate"]
            })
        
        # レスポンス時間チェック
        if metrics["response_time_p95"] > self.thresholds["response_time_p95"]:
            alerts.append({
                "type": "response_time",
                "severity": "warning",
                "message": f"P95レスポンス時間が閾値を超過: {metrics['response_time_p95']:.1f}ms > {self.thresholds['response_time_p95']}ms",
                "value": metrics["response_time_p95"],
                "threshold": self.thresholds["response_time_p95"]
            })
        
        # CPU使用率チェック
        if metrics["cpu_utilization"] > self.thresholds["cpu_utilization"]:
            alerts.append({
                "type": "cpu_utilization",
                "severity": "warning",
                "message": f"CPU使用率が閾値を超過: {metrics['cpu_utilization']:.1%} > {self.thresholds['cpu_utilization']:.1%}",
                "value": metrics["cpu_utilization"],
                "threshold": self.thresholds["cpu_utilization"]
            })
        
        # メモリ使用率チェック
        if metrics["memory_utilization"] > self.thresholds["memory_utilization"]:
            alerts.append({
                "type": "memory_utilization",
                "severity": "warning",
                "message": f"メモリ使用率が閾値を超過: {metrics['memory_utilization']:.1%} > {self.thresholds['memory_utilization']:.1%}",
                "value": metrics["memory_utilization"],
                "threshold": self.thresholds["memory_utilization"]
            })
        
        # ヘルスステータスチェック
        if metrics["health_status"] != "healthy":
            alerts.append({
                "type": "health_check",
                "severity": "critical",
                "message": f"ヘルスチェック失敗: {metrics['health_status']}",
                "value": metrics["health_status"],
                "threshold": "healthy"
            })
        
        return alerts
    
    def send_alert(self, alert: Dict) -> bool:
        """アラート送信"""
        try:
            # Slackやメール、PagerDutyなどにアラートを送信
            # 実際の実装では、適切な通知サービスを使用
            
            alert_message = {
                "service": self.service_name,
                "alert": alert,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.warning(f"🚨 ALERT: {alert['message']}")
            
            # アラートをファイルに記録
            with open(f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                json.dump(alert_message, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"アラート送信エラー: {e}")
            return False
    
    def generate_monitoring_report(self, metrics_history: List[Dict]) -> Dict:
        """監視レポート生成"""
        if not metrics_history:
            return {"status": "no_data"}
        
        # 統計計算
        error_rates = [m["error_rate"] for m in metrics_history]
        response_times = [m["response_time_p95"] for m in metrics_history if m["response_time_p95"] > 0]
        
        report = {
            "monitoring_period": {
                "start": metrics_history[0]["timestamp"],
                "end": metrics_history[-1]["timestamp"],
                "duration_minutes": len(metrics_history)
            },
            "summary": {
                "total_samples": len(metrics_history),
                "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
                "max_error_rate": max(error_rates) if error_rates else 0,
                "avg_response_time_p95": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time_p95": max(response_times) if response_times else 0
            },
            "health_status": {
                "healthy_samples": sum(1 for m in metrics_history if m["health_status"] == "healthy"),
                "unhealthy_samples": sum(1 for m in metrics_history if m["health_status"] != "healthy"),
                "availability": sum(1 for m in metrics_history if m["health_status"] == "healthy") / len(metrics_history)
            },
            "threshold_violations": {
                "error_rate": sum(1 for m in metrics_history if m["error_rate"] > self.thresholds["error_rate"]),
                "response_time": sum(1 for m in metrics_history if m["response_time_p95"] > self.thresholds["response_time_p95"])
            }
        }
        
        # 全体評価
        if report["summary"]["max_error_rate"] > self.thresholds["error_rate"]:
            report["overall_status"] = "critical"
        elif report["threshold_violations"]["response_time"] > len(metrics_history) * 0.1:  # 10%以上の違反
            report["overall_status"] = "warning"
        else:
            report["overall_status"] = "healthy"
        
        return report
    
    def monitor(self, duration_minutes: int, interval_seconds: int = 60) -> Dict:
        """監視実行"""
        logger.info(f"デプロイメント後監視開始: {duration_minutes}分間")
        
        metrics_history = []
        alert_count = 0
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time and self.monitoring_active:
                # メトリクス収集
                metrics = self.collect_metrics()
                metrics_history.append(metrics)
                
                # 閾値チェック
                alerts = self.check_thresholds(metrics)
                
                # アラート送信
                for alert in alerts:
                    self.send_alert(alert)
                    alert_count += 1
                
                # 進捗表示
                elapsed_minutes = (time.time() - start_time) / 60
                logger.info(f"監視進捗: {elapsed_minutes:.1f}/{duration_minutes}分 (アラート: {alert_count}件)")
                
                # 次の監視まで待機
                time.sleep(interval_seconds)
            
            # 監視レポート生成
            report = self.generate_monitoring_report(metrics_history)
            report["alert_count"] = alert_count
            
            logger.info(f"監視完了: 全体ステータス={report['overall_status']}, アラート={alert_count}件")
            
            return report
            
        except KeyboardInterrupt:
            logger.info("監視中断")
            self.monitoring_active = False
            return self.generate_monitoring_report(metrics_history)
        except Exception as e:
            logger.error(f"監視エラー: {e}")
            return {"status": "error", "error": str(e)}
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring_active = False

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description="デプロイメント後監視")
    parser.add_argument("--service", required=True, help="Cloud Runサービス名")
    parser.add_argument("--region", default="asia-northeast1", help="リージョン")
    parser.add_argument("--duration", type=int, default=15, help="監視時間（分）")
    parser.add_argument("--interval", type=int, default=60, help="監視間隔（秒）")
    parser.add_argument("--alert-threshold", type=float, default=0.05, help="エラー率アラート閾値")
    parser.add_argument("--output", help="レポート出力ファイル")
    
    args = parser.parse_args()
    
    # 監視開始
    monitor = PostDeploymentMonitor(args.service, args.region)
    
    # 閾値設定
    if args.alert_threshold:
        monitor.thresholds["error_rate"] = args.alert_threshold
    
    try:
        # 監視実行
        report = monitor.monitor(args.duration, args.interval)
        
        # レポート出力
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"レポート出力: {args.output}")
        else:
            print(json.dumps(report, indent=2))
        
        # 終了コード決定
        if report.get("overall_status") == "critical":
            sys.exit(2)  # クリティカル
        elif report.get("overall_status") == "warning":
            sys.exit(1)  # 警告
        else:
            sys.exit(0)  # 正常
            
    except KeyboardInterrupt:
        logger.info("監視中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()