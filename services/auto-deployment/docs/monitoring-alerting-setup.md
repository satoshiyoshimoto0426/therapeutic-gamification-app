# Auto-Deployment System 監視・アラート設定ガイド

## 概要

このガイドでは、Auto-Deployment Systemの包括的な監視とアラート設定について説明します。効果的な監視により、問題の早期発見と迅速な対応が可能になります。

## 監視アーキテクチャ

### 監視レイヤー

```
┌─────────────────────────────────────────────────────────────┐
│                    アラート・通知層                          │
│  Slack, Email, PagerDuty, Microsoft Teams                  │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                    ダッシュボード層                          │
│  Grafana, Cloud Monitoring, カスタムダッシュボード           │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                    メトリクス収集層                          │
│  Prometheus, Cloud Monitoring, カスタムメトリクス           │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                    アプリケーション層                        │
│  Auto-Deployment Services, Cloud Run, Firestore           │
└─────────────────────────────────────────────────────────────┘
```

## 基本監視設定

### 1. Google Cloud Monitoring設定

#### Cloud Monitoring APIの有効化
```bash
# Cloud Monitoring APIを有効化
gcloud services enable monitoring.googleapis.com

# 必要な権限を確認
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

#### 基本メトリクスの設定
```yaml
# config/monitoring.yaml
monitoring:
  provider: "google_cloud_monitoring"
  project_id: "your-project-id"
  
  # 基本メトリクス
  basic_metrics:
    - name: "deployment_success_rate"
      type: "gauge"
      description: "デプロイメント成功率"
      
    - name: "deployment_duration"
      type: "histogram"
      description: "デプロイメント実行時間"
      
    - name: "rollback_frequency"
      type: "counter"
      description: "ロールバック実行回数"
      
    - name: "health_check_status"
      type: "gauge"
      description: "ヘルスチェック状況"
```

### 2. カスタムメトリクス実装

#### メトリクス収集クラス
```python
# services/auto_deployment/monitoring/metrics_collector.py
import time
from typing import Dict, Any
from google.cloud import monitoring_v3
from dataclasses import dataclass

@dataclass
class MetricPoint:
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str]

class MetricsCollector:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
    
    def record_deployment_start(self, deployment_id: str, environment: str):
        """デプロイメント開始メトリクス"""
        self._write_metric(
            "deployment_started",
            1,
            {
                "deployment_id": deployment_id,
                "environment": environment
            }
        )
    
    def record_deployment_success(self, deployment_id: str, duration: float):
        """デプロイメント成功メトリクス"""
        self._write_metric("deployment_success", 1, {"deployment_id": deployment_id})
        self._write_metric("deployment_duration", duration, {"deployment_id": deployment_id})
    
    def record_deployment_failure(self, deployment_id: str, error_type: str):
        """デプロイメント失敗メトリクス"""
        self._write_metric(
            "deployment_failure",
            1,
            {
                "deployment_id": deployment_id,
                "error_type": error_type
            }
        )
    
    def record_health_check(self, service: str, status: str, response_time: float):
        """ヘルスチェックメトリクス"""
        self._write_metric(
            "health_check_status",
            1 if status == "healthy" else 0,
            {"service": service}
        )
        self._write_metric(
            "health_check_response_time",
            response_time,
            {"service": service}
        )
    
    def _write_metric(self, metric_name: str, value: float, labels: Dict[str, str]):
        """メトリクスをCloud Monitoringに送信"""
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/auto_deployment/{metric_name}"
        series.resource.type = "global"
        
        # ラベルを設定
        for key, val in labels.items():
            series.metric.labels[key] = val
        
        # データポイントを作成
        point = series.points.add()
        point.value.double_value = value
        point.interval.end_time.seconds = int(time.time())
        
        # メトリクスを送信
        self.client.create_time_series(
            name=self.project_name,
            time_series=[series]
        )
```

### 3. ヘルスチェック監視

#### 包括的ヘルスチェック
```python
# services/auto_deployment/monitoring/comprehensive_health_check.py
import asyncio
import aiohttp
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class HealthCheckResult:
    service: str
    endpoint: str
    status: str
    response_time: float
    status_code: int
    error_message: str = None

class ComprehensiveHealthChecker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_collector = MetricsCollector(config['project_id'])
    
    async def check_all_services(self) -> List[HealthCheckResult]:
        """すべてのサービスのヘルスチェック"""
        services = self.config.get('services', [])
        tasks = []
        
        for service in services:
            for endpoint in service.get('health_endpoints', []):
                task = self._check_endpoint(service['name'], endpoint)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # メトリクスを記録
        for result in results:
            if isinstance(result, HealthCheckResult):
                self.metrics_collector.record_health_check(
                    result.service,
                    result.status,
                    result.response_time
                )
        
        return [r for r in results if isinstance(r, HealthCheckResult)]
    
    async def _check_endpoint(self, service: str, endpoint: Dict[str, Any]) -> HealthCheckResult:
        """個別エンドポイントのヘルスチェック"""
        url = endpoint['url']
        timeout = endpoint.get('timeout', 30)
        expected_status = endpoint.get('expected_status', 200)
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == expected_status:
                        status = "healthy"
                    else:
                        status = "unhealthy"
                    
                    return HealthCheckResult(
                        service=service,
                        endpoint=url,
                        status=status,
                        response_time=response_time * 1000,  # ms
                        status_code=response.status
                    )
        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                service=service,
                endpoint=url,
                status="timeout",
                response_time=(time.time() - start_time) * 1000,
                status_code=0,
                error_message="Request timeout"
            )
        
        except Exception as e:
            return HealthCheckResult(
                service=service,
                endpoint=url,
                status="error",
                response_time=(time.time() - start_time) * 1000,
                status_code=0,
                error_message=str(e)
            )
```

## アラート設定

### 1. アラートルールの定義

#### 基本アラートルール
```yaml
# config/alert_rules.yaml
alert_rules:
  # 重要度: Critical
  critical:
    - name: "deployment_failure_rate_high"
      description: "デプロイメント失敗率が高い"
      condition: "deployment_failure_rate > 0.2"
      duration: "5m"
      severity: "critical"
      channels: ["slack", "email", "pagerduty"]
      
    - name: "service_down"
      description: "サービスがダウンしている"
      condition: "health_check_success_rate < 0.5"
      duration: "2m"
      severity: "critical"
      channels: ["slack", "email", "pagerduty"]
      auto_rollback: true
      
    - name: "rollback_failure"
      description: "ロールバックが失敗した"
      condition: "rollback_failure_count > 0"
      duration: "1m"
      severity: "critical"
      channels: ["slack", "email", "pagerduty"]
  
  # 重要度: Warning
  warning:
    - name: "deployment_duration_long"
      description: "デプロイメント時間が長い"
      condition: "deployment_duration_p95 > 1800"  # 30分
      duration: "10m"
      severity: "warning"
      channels: ["slack"]
      
    - name: "health_check_slow"
      description: "ヘルスチェックが遅い"
      condition: "health_check_response_time_p95 > 5000"  # 5秒
      duration: "15m"
      severity: "warning"
      channels: ["slack"]
      
    - name: "error_rate_elevated"
      description: "エラー率が上昇している"
      condition: "error_rate > 0.05"  # 5%
      duration: "10m"
      severity: "warning"
      channels: ["slack", "email"]
  
  # 重要度: Info
  info:
    - name: "deployment_completed"
      description: "デプロイメントが完了した"
      condition: "deployment_success_count > 0"
      duration: "0m"
      severity: "info"
      channels: ["slack"]
      
    - name: "rollback_triggered"
      description: "ロールバックが実行された"
      condition: "rollback_count > 0"
      duration: "0m"
      severity: "info"
      channels: ["slack", "email"]
```

### 2. アラート管理システム

#### アラートマネージャー
```python
# services/auto_deployment/monitoring/alert_manager.py
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Alert:
    name: str
    description: str
    severity: AlertSeverity
    timestamp: float
    labels: Dict[str, str]
    value: float
    threshold: float

class AlertManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts = {}
        self.notification_manager = NotificationManager(config)
        self.metrics_collector = MetricsCollector(config['project_id'])
    
    async def evaluate_alerts(self, metrics: Dict[str, float]):
        """アラートルールを評価"""
        alert_rules = self.config.get('alert_rules', {})
        
        for severity, rules in alert_rules.items():
            for rule in rules:
                await self._evaluate_rule(rule, metrics, AlertSeverity(severity))
    
    async def _evaluate_rule(self, rule: Dict[str, Any], metrics: Dict[str, float], severity: AlertSeverity):
        """個別ルールの評価"""
        condition = rule['condition']
        duration = rule.get('duration', '0m')
        
        # 条件を評価
        if self._evaluate_condition(condition, metrics):
            alert_key = rule['name']
            
            if alert_key not in self.active_alerts:
                # 新しいアラート
                alert = Alert(
                    name=rule['name'],
                    description=rule['description'],
                    severity=severity,
                    timestamp=time.time(),
                    labels=rule.get('labels', {}),
                    value=self._extract_value(condition, metrics),
                    threshold=self._extract_threshold(condition)
                )
                
                self.active_alerts[alert_key] = alert
                
                # 持続時間チェック
                if self._check_duration(duration):
                    await self._fire_alert(alert, rule)
            
            else:
                # 既存のアラート - 持続時間をチェック
                alert = self.active_alerts[alert_key]
                if time.time() - alert.timestamp >= self._parse_duration(duration):
                    await self._fire_alert(alert, rule)
        
        else:
            # 条件が満たされない場合、アラートを解除
            alert_key = rule['name']
            if alert_key in self.active_alerts:
                await self._resolve_alert(self.active_alerts[alert_key])
                del self.active_alerts[alert_key]
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, float]) -> bool:
        """条件式を評価"""
        # 簡単な条件評価（実際にはより複雑なパーサーが必要）
        try:
            # メトリクス名を実際の値に置換
            for metric_name, value in metrics.items():
                condition = condition.replace(metric_name, str(value))
            
            # 安全な評価
            return eval(condition)
        except:
            return False
    
    async def _fire_alert(self, alert: Alert, rule: Dict[str, Any]):
        """アラートを発火"""
        channels = rule.get('channels', [])
        
        # 通知を送信
        for channel in channels:
            await self.notification_manager.send_alert(alert, channel)
        
        # 自動ロールバックが設定されている場合
        if rule.get('auto_rollback', False) and alert.severity == AlertSeverity.CRITICAL:
            await self._trigger_auto_rollback(alert)
        
        # メトリクスを記録
        self.metrics_collector.record_alert_fired(alert.name, alert.severity.value)
    
    async def _resolve_alert(self, alert: Alert):
        """アラートを解除"""
        await self.notification_manager.send_alert_resolution(alert)
        self.metrics_collector.record_alert_resolved(alert.name)
    
    async def _trigger_auto_rollback(self, alert: Alert):
        """自動ロールバックをトリガー"""
        from services.auto_deployment.rollback.rollback_manager import RollbackManager
        
        rollback_manager = RollbackManager(self.config)
        await rollback_manager.trigger_emergency_rollback(
            reason=f"Auto-rollback triggered by alert: {alert.name}"
        )
```

### 3. 通知チャネル設定

#### Slack通知
```python
# services/auto_deployment/notification/slack_alerting.py
import aiohttp
import json
from typing import Dict, Any

class SlackAlerting:
    def __init__(self, webhook_url: str, channel: str):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send_alert(self, alert: Alert):
        """Slackにアラートを送信"""
        color = self._get_color(alert.severity)
        
        payload = {
            "channel": self.channel,
            "username": "Auto-Deploy Alert",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {alert.name}",
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "重要度",
                            "value": alert.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "値",
                            "value": f"{alert.value:.2f} (閾値: {alert.threshold})",
                            "short": True
                        },
                        {
                            "title": "時刻",
                            "value": f"<t:{int(alert.timestamp)}:F>",
                            "short": True
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "text": "ダッシュボードを確認",
                            "url": f"https://console.cloud.google.com/monitoring"
                        },
                        {
                            "type": "button",
                            "text": "ログを確認",
                            "url": f"https://console.cloud.google.com/logs"
                        }
                    ]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Slack notification failed: {response.status}")
    
    def _get_color(self, severity: AlertSeverity) -> str:
        """重要度に応じた色を取得"""
        colors = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.INFO: "good"
        }
        return colors.get(severity, "good")
```

#### メール通知
```python
# services/auto_deployment/notification/email_alerting.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailAlerting:
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_server = smtp_config['server']
        self.smtp_port = smtp_config['port']
        self.username = smtp_config['username']
        self.password = smtp_config['password']
        self.from_email = smtp_config['from_email']
    
    async def send_alert(self, alert: Alert, recipients: List[str]):
        """メールでアラートを送信"""
        subject = f"[{alert.severity.value.upper()}] Auto-Deploy Alert: {alert.name}"
        
        # HTMLメール本文を作成
        html_body = self._create_html_body(alert)
        text_body = self._create_text_body(alert)
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = ', '.join(recipients)
        
        # テキストとHTML部分を追加
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # メールを送信
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
    
    def _create_html_body(self, alert: Alert) -> str:
        """HTMLメール本文を作成"""
        severity_color = {
            AlertSeverity.CRITICAL: "#ff4444",
            AlertSeverity.WARNING: "#ffaa00",
            AlertSeverity.INFO: "#00aa00"
        }
        
        color = severity_color.get(alert.severity, "#00aa00")
        
        return f"""
        <html>
        <body>
            <h2 style="color: {color};">🚨 {alert.name}</h2>
            <p><strong>説明:</strong> {alert.description}</p>
            <p><strong>重要度:</strong> <span style="color: {color};">{alert.severity.value.upper()}</span></p>
            <p><strong>値:</strong> {alert.value:.2f} (閾値: {alert.threshold})</p>
            <p><strong>発生時刻:</strong> {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>対応アクション</h3>
            <ul>
                <li><a href="https://console.cloud.google.com/monitoring">Cloud Monitoringダッシュボード</a></li>
                <li><a href="https://console.cloud.google.com/logs">ログを確認</a></li>
                <li><a href="https://console.cloud.google.com/run">Cloud Runサービス</a></li>
            </ul>
        </body>
        </html>
        """
    
    def _create_text_body(self, alert: Alert) -> str:
        """テキストメール本文を作成"""
        return f"""
Auto-Deploy Alert: {alert.name}

説明: {alert.description}
重要度: {alert.severity.value.upper()}
値: {alert.value:.2f} (閾値: {alert.threshold})
発生時刻: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}

対応が必要な場合は、以下のリンクから詳細を確認してください:
- Cloud Monitoring: https://console.cloud.google.com/monitoring
- ログ: https://console.cloud.google.com/logs
- Cloud Run: https://console.cloud.google.com/run
        """
```

## ダッシュボード設定

### 1. カスタムダッシュボード

#### ダッシュボード設定
```python
# services/auto_deployment/monitoring/dashboard_config.py
DASHBOARD_CONFIG = {
    "deployment_overview": {
        "title": "デプロイメント概要",
        "widgets": [
            {
                "type": "stat",
                "title": "今日のデプロイメント数",
                "query": "sum(rate(deployment_started[24h]))",
                "size": {"width": 3, "height": 2}
            },
            {
                "type": "stat",
                "title": "成功率",
                "query": "sum(deployment_success) / sum(deployment_started) * 100",
                "unit": "%",
                "size": {"width": 3, "height": 2}
            },
            {
                "type": "graph",
                "title": "デプロイメント時間トレンド",
                "query": "histogram_quantile(0.95, deployment_duration)",
                "size": {"width": 6, "height": 4}
            }
        ]
    },
    
    "service_health": {
        "title": "サービスヘルス",
        "widgets": [
            {
                "type": "heatmap",
                "title": "サービス可用性",
                "query": "health_check_success_rate by (service)",
                "size": {"width": 12, "height": 6}
            },
            {
                "type": "table",
                "title": "サービス状況",
                "query": "health_check_status by (service)",
                "size": {"width": 6, "height": 4}
            }
        ]
    },
    
    "performance_metrics": {
        "title": "パフォーマンスメトリクス",
        "widgets": [
            {
                "type": "graph",
                "title": "レスポンス時間",
                "queries": [
                    "histogram_quantile(0.50, response_time)",
                    "histogram_quantile(0.95, response_time)",
                    "histogram_quantile(0.99, response_time)"
                ],
                "size": {"width": 6, "height": 4}
            },
            {
                "type": "graph",
                "title": "エラー率",
                "query": "rate(error_count[5m]) / rate(request_count[5m]) * 100",
                "unit": "%",
                "size": {"width": 6, "height": 4}
            }
        ]
    }
}
```

### 2. Grafanaダッシュボード

#### Grafana設定ファイル
```json
{
  "dashboard": {
    "title": "Auto-Deployment System",
    "tags": ["auto-deployment", "monitoring"],
    "timezone": "Asia/Tokyo",
    "panels": [
      {
        "title": "デプロイメント成功率",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(deployment_success[1h])) / sum(rate(deployment_started[1h])) * 100",
            "legendFormat": "成功率"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 80},
                {"color": "green", "value": 95}
              ]
            }
          }
        }
      },
      {
        "title": "デプロイメント時間",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, deployment_duration)",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, deployment_duration)",
            "legendFormat": "P95"
          }
        ]
      },
      {
        "title": "アクティブアラート",
        "type": "table",
        "targets": [
          {
            "expr": "ALERTS{alertstate=\"firing\"}",
            "format": "table"
          }
        ]
      }
    ]
  }
}
```

## 運用監視手順

### 1. 日次監視チェックリスト

#### 毎日の確認項目
```markdown
## 日次監視チェックリスト

### デプロイメント状況
- [ ] 過去24時間のデプロイメント成功率 (目標: >95%)
- [ ] 平均デプロイメント時間 (目標: <20分)
- [ ] 失敗したデプロイメントの原因分析
- [ ] ロールバック実行回数と原因

### サービスヘルス
- [ ] 全サービスのヘルスチェック状況
- [ ] レスポンス時間の異常値確認
- [ ] エラー率の確認 (目標: <1%)
- [ ] リソース使用率の確認

### アラート状況
- [ ] アクティブアラートの確認と対応
- [ ] 解決済みアラートの原因分析
- [ ] アラート頻度の傾向分析

### インフラストラクチャ
- [ ] Cloud Runインスタンス数の確認
- [ ] Firestoreの使用量とパフォーマンス
- [ ] ネットワーク遅延の確認
```

### 2. 週次レビュー

#### 週次分析レポート
```python
# scripts/weekly_monitoring_report.py
import pandas as pd
from datetime import datetime, timedelta
from services.auto_deployment.monitoring import MetricsCollector

class WeeklyMonitoringReport:
    def __init__(self, project_id: str):
        self.metrics_collector = MetricsCollector(project_id)
    
    def generate_report(self) -> Dict[str, Any]:
        """週次監視レポートを生成"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        # デプロイメントメトリクス
        deployment_metrics = self._analyze_deployments(start_time, end_time)
        
        # パフォーマンスメトリクス
        performance_metrics = self._analyze_performance(start_time, end_time)
        
        # アラートメトリクス
        alert_metrics = self._analyze_alerts(start_time, end_time)
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "deployment": deployment_metrics,
            "performance": performance_metrics,
            "alerts": alert_metrics,
            "recommendations": self._generate_recommendations(
                deployment_metrics, performance_metrics, alert_metrics
            )
        }
    
    def _analyze_deployments(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """デプロイメント分析"""
        deployments = self.metrics_collector.get_deployments(start_time, end_time)
        
        total_deployments = len(deployments)
        successful_deployments = len([d for d in deployments if d.status == 'completed'])
        failed_deployments = len([d for d in deployments if d.status == 'failed'])
        
        success_rate = successful_deployments / total_deployments if total_deployments > 0 else 0
        
        # デプロイメント時間の分析
        durations = [d.duration for d in deployments if d.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_deployments": total_deployments,
            "success_rate": success_rate,
            "failed_deployments": failed_deployments,
            "average_duration": avg_duration,
            "trend": self._calculate_trend(deployments)
        }
    
    def _generate_recommendations(self, deployment_metrics: Dict, performance_metrics: Dict, alert_metrics: Dict) -> List[str]:
        """改善提案を生成"""
        recommendations = []
        
        # デプロイメント成功率が低い場合
        if deployment_metrics['success_rate'] < 0.95:
            recommendations.append(
                "デプロイメント成功率が95%を下回っています。事前検証の強化を検討してください。"
            )
        
        # デプロイメント時間が長い場合
        if deployment_metrics['average_duration'] > 1800:  # 30分
            recommendations.append(
                "デプロイメント時間が長くなっています。並列化やキャッシュの活用を検討してください。"
            )
        
        # アラート頻度が高い場合
        if alert_metrics['total_alerts'] > 50:
            recommendations.append(
                "アラート頻度が高くなっています。閾値の調整やノイズの除去を検討してください。"
            )
        
        return recommendations
```

### 3. 緊急時対応手順

#### インシデント対応フロー
```markdown
## インシデント対応フロー

### レベル1: 軽微な問題
**対応時間: 1時間以内**
- 単一サービスの軽微な問題
- パフォーマンスの軽微な劣化

**対応手順:**
1. アラートの確認と分析
2. ログの詳細確認
3. 必要に応じて設定調整
4. 状況の継続監視

### レベル2: 中程度の問題
**対応時間: 30分以内**
- 複数サービスに影響
- エラー率の上昇
- レスポンス時間の大幅な増加

**対応手順:**
1. 即座にチームに通知
2. 問題の範囲と影響を特定
3. 一時的な回避策の実施
4. 根本原因の調査開始
5. ロールバックの検討

### レベル3: 重大な問題
**対応時間: 15分以内**
- サービス全体の停止
- データ損失の可能性
- セキュリティインシデント

**対応手順:**
1. 緊急事態宣言
2. 全関係者への即座の通知
3. 即座のロールバック実行
4. サービス復旧の確認
5. インシデント後レビューの実施
```

## 監視の最適化

### 1. メトリクス最適化

#### 重要メトリクスの選定
```yaml
# 重要度別メトリクス分類
critical_metrics:
  - deployment_success_rate
  - service_availability
  - error_rate
  - response_time_p95

important_metrics:
  - deployment_duration
  - rollback_frequency
  - resource_utilization
  - alert_frequency

nice_to_have_metrics:
  - deployment_frequency
  - code_coverage
  - technical_debt_ratio
  - team_productivity
```

### 2. アラート最適化

#### アラート疲れの防止
```python
# services/auto_deployment/monitoring/alert_optimizer.py
class AlertOptimizer:
    def __init__(self):
        self.alert_history = []
        self.false_positive_threshold = 0.3
    
    def optimize_thresholds(self, metric_name: str, historical_data: List[float]):
        """統計的手法でアラート閾値を最適化"""
        import numpy as np
        
        # 異常値を除外
        q75, q25 = np.percentile(historical_data, [75, 25])
        iqr = q75 - q25
        lower_bound = q25 - (iqr * 1.5)
        upper_bound = q75 + (iqr * 1.5)
        
        filtered_data = [x for x in historical_data if lower_bound <= x <= upper_bound]
        
        # 動的閾値の計算
        mean = np.mean(filtered_data)
        std = np.std(filtered_data)
        
        # 3シグマルールを適用
        warning_threshold = mean + (2 * std)
        critical_threshold = mean + (3 * std)
        
        return {
            "warning": warning_threshold,
            "critical": critical_threshold,
            "confidence": self._calculate_confidence(filtered_data)
        }
    
    def reduce_alert_noise(self, alerts: List[Alert]) -> List[Alert]:
        """アラートノイズを削減"""
        # 類似アラートをグループ化
        grouped_alerts = self._group_similar_alerts(alerts)
        
        # 重複を除去
        deduplicated_alerts = []
        for group in grouped_alerts:
            if len(group) > 1:
                # 最も重要なアラートのみを保持
                most_important = max(group, key=lambda a: a.severity.value)
                deduplicated_alerts.append(most_important)
            else:
                deduplicated_alerts.extend(group)
        
        return deduplicated_alerts
```

このガイドを参考に、効果的な監視・アラートシステムを構築し、Auto-Deployment Systemの信頼性を向上させてください。