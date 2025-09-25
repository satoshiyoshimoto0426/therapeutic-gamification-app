# Auto-Deployment System API ドキュメント

## 概要

Auto-Deployment SystemはREST APIとPython APIの両方を提供し、プログラムからデプロイメント機能にアクセスできます。このドキュメントでは、両方のAPIの使用方法について説明します。

## REST API

### 基本情報

- **ベースURL**: `http://localhost:8080/api/v1`
- **認証**: Bearer Token または API Key
- **コンテンツタイプ**: `application/json`
- **レスポンス形式**: JSON

### 認証

```bash
# Bearer Token認証
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/deployments

# API Key認証
curl -H "X-API-Key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/deployments
```

### エンドポイント一覧

#### 1. デプロイメント管理

##### POST /deployments

新しいデプロイメントを開始します。

**リクエスト:**
```json
{
  "environment": "production",
  "services": ["auth", "core-game"],
  "strategy": "blue-green",
  "options": {
    "dry_run": false,
    "skip_validation": false,
    "force": false
  },
  "metadata": {
    "triggered_by": "user@example.com",
    "reason": "Bug fix deployment"
  }
}
```

**レスポンス:**
```json
{
  "deployment_id": "dep-20240109-001",
  "status": "started",
  "environment": "production",
  "services": ["auth", "core-game"],
  "strategy": "blue-green",
  "created_at": "2024-01-09T10:00:00Z",
  "estimated_duration": 1800,
  "progress_url": "/api/v1/deployments/dep-20240109-001/progress"
}
```

**cURLの例:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "production",
    "services": ["auth", "core-game"],
    "strategy": "blue-green"
  }' \
  http://localhost:8080/api/v1/deployments
```

##### GET /deployments

デプロイメント一覧を取得します。

**クエリパラメータ:**
- `environment`: 環境でフィルタ
- `status`: ステータスでフィルタ
- `limit`: 取得件数制限（デフォルト: 50）
- `offset`: オフセット（デフォルト: 0）

**レスポンス:**
```json
{
  "deployments": [
    {
      "deployment_id": "dep-20240109-001",
      "status": "completed",
      "environment": "production",
      "services": ["auth", "core-game"],
      "created_at": "2024-01-09T10:00:00Z",
      "completed_at": "2024-01-09T10:30:00Z",
      "duration": 1800
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

##### GET /deployments/{deployment_id}

特定のデプロイメントの詳細を取得します。

**レスポンス:**
```json
{
  "deployment_id": "dep-20240109-001",
  "status": "completed",
  "environment": "production",
  "services": ["auth", "core-game"],
  "strategy": "blue-green",
  "created_at": "2024-01-09T10:00:00Z",
  "completed_at": "2024-01-09T10:30:00Z",
  "duration": 1800,
  "steps": [
    {
      "name": "validation",
      "status": "completed",
      "started_at": "2024-01-09T10:00:00Z",
      "completed_at": "2024-01-09T10:05:00Z"
    },
    {
      "name": "build",
      "status": "completed",
      "started_at": "2024-01-09T10:05:00Z",
      "completed_at": "2024-01-09T10:20:00Z"
    }
  ],
  "health_checks": [
    {
      "endpoint": "/health",
      "status": "healthy",
      "response_time": 150,
      "last_check": "2024-01-09T10:35:00Z"
    }
  ]
}
```

##### DELETE /deployments/{deployment_id}

デプロイメントをキャンセルします（実行中の場合）。

**レスポンス:**
```json
{
  "deployment_id": "dep-20240109-001",
  "status": "cancelled",
  "message": "Deployment cancelled successfully"
}
```

#### 2. ロールバック管理

##### POST /rollbacks

ロールバックを実行します。

**リクエスト:**
```json
{
  "environment": "production",
  "services": ["auth"],
  "target_revision": "auth-00001-abc",
  "reason": "Critical bug detected"
}
```

**レスポンス:**
```json
{
  "rollback_id": "rb-20240109-001",
  "status": "started",
  "environment": "production",
  "services": ["auth"],
  "target_revision": "auth-00001-abc",
  "created_at": "2024-01-09T11:00:00Z"
}
```

##### GET /rollbacks/{rollback_id}

ロールバックの状況を取得します。

**レスポンス:**
```json
{
  "rollback_id": "rb-20240109-001",
  "status": "completed",
  "environment": "production",
  "services": ["auth"],
  "target_revision": "auth-00001-abc",
  "created_at": "2024-01-09T11:00:00Z",
  "completed_at": "2024-01-09T11:05:00Z",
  "verification_status": "passed"
}
```

#### 3. ヘルスチェック

##### GET /health

システム全体のヘルス状況を取得します。

**レスポンス:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-09T12:00:00Z",
  "services": {
    "auth": {
      "status": "healthy",
      "response_time": 120,
      "last_deployment": "2024-01-09T10:30:00Z"
    },
    "core-game": {
      "status": "healthy",
      "response_time": 95,
      "last_deployment": "2024-01-09T10:30:00Z"
    }
  },
  "infrastructure": {
    "cloud_run": "healthy",
    "firestore": "healthy",
    "secret_manager": "healthy"
  }
}
```

##### GET /health/{service}

特定のサービスのヘルス状況を取得します。

**レスポンス:**
```json
{
  "service": "auth",
  "status": "healthy",
  "timestamp": "2024-01-09T12:00:00Z",
  "endpoints": [
    {
      "path": "/health",
      "status": "healthy",
      "response_time": 120,
      "status_code": 200
    }
  ],
  "metrics": {
    "cpu_usage": 0.45,
    "memory_usage": 0.62,
    "request_rate": 150.5,
    "error_rate": 0.001
  }
}
```

#### 4. 設定管理

##### GET /config

現在の設定を取得します。

**クエリパラメータ:**
- `environment`: 特定の環境の設定を取得

**レスポンス:**
```json
{
  "project": {
    "id": "your-project-id",
    "region": "asia-northeast1"
  },
  "deployment": {
    "strategy": "blue-green",
    "timeout": 1800
  },
  "environments": {
    "production": {
      "min_instances": 2,
      "max_instances": 100
    }
  }
}
```

##### PUT /config

設定を更新します。

**リクエスト:**
```json
{
  "deployment": {
    "timeout": 2400
  },
  "environments": {
    "production": {
      "max_instances": 150
    }
  }
}
```

#### 5. 監視とメトリクス

##### GET /metrics

システムメトリクスを取得します。

**クエリパラメータ:**
- `service`: 特定のサービスのメトリクス
- `start_time`: 開始時刻（ISO 8601形式）
- `end_time`: 終了時刻（ISO 8601形式）
- `interval`: データ間隔（秒）

**レスポンス:**
```json
{
  "metrics": [
    {
      "timestamp": "2024-01-09T12:00:00Z",
      "service": "auth",
      "cpu_usage": 0.45,
      "memory_usage": 0.62,
      "request_rate": 150.5,
      "error_rate": 0.001,
      "response_time_p95": 180
    }
  ],
  "summary": {
    "avg_cpu_usage": 0.42,
    "avg_memory_usage": 0.58,
    "total_requests": 54180,
    "total_errors": 54
  }
}
```

##### GET /logs

ログを取得します。

**クエリパラメータ:**
- `service`: サービス名
- `level`: ログレベル（debug, info, warn, error）
- `start_time`: 開始時刻
- `end_time`: 終了時刻
- `limit`: 取得件数制限

**レスポンス:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-09T12:00:00Z",
      "level": "info",
      "service": "auth",
      "message": "User authentication successful",
      "metadata": {
        "user_id": "user123",
        "ip_address": "192.168.1.100"
      }
    }
  ],
  "total": 1,
  "limit": 100
}
```

## Python API

### インストール

```bash
pip install auto-deployment-sdk
```

### 基本的な使用方法

```python
from services.auto_deployment import AutoDeploymentClient

# クライアントの初期化
client = AutoDeploymentClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# デプロイメントの実行
deployment = client.deploy(
    environment="production",
    services=["auth", "core-game"],
    strategy="blue-green"
)

print(f"Deployment ID: {deployment.id}")
print(f"Status: {deployment.status}")
```

### クライアントクラス

#### AutoDeploymentClient

```python
class AutoDeploymentClient:
    def __init__(self, base_url: str, api_key: str = None, token: str = None):
        """
        Auto-Deployment APIクライアント
        
        Args:
            base_url: APIのベースURL
            api_key: API Key認証用
            token: Bearer Token認証用
        """
        pass
    
    def deploy(self, environment: str, services: List[str] = None, 
               strategy: str = "blue-green", **options) -> Deployment:
        """
        デプロイメントを実行
        
        Args:
            environment: デプロイ先環境
            services: デプロイするサービス一覧
            strategy: デプロイメント戦略
            **options: その他のオプション
            
        Returns:
            Deployment: デプロイメントオブジェクト
        """
        pass
    
    def get_deployment(self, deployment_id: str) -> Deployment:
        """デプロイメント情報を取得"""
        pass
    
    def list_deployments(self, environment: str = None, 
                        status: str = None, limit: int = 50) -> List[Deployment]:
        """デプロイメント一覧を取得"""
        pass
    
    def rollback(self, environment: str, services: List[str] = None,
                target_revision: str = None) -> Rollback:
        """ロールバックを実行"""
        pass
    
    def get_health(self, service: str = None) -> HealthStatus:
        """ヘルス状況を取得"""
        pass
    
    def get_metrics(self, service: str = None, start_time: datetime = None,
                   end_time: datetime = None) -> MetricsData:
        """メトリクスを取得"""
        pass
```

### データモデル

#### Deployment

```python
@dataclass
class Deployment:
    id: str
    status: str  # started, running, completed, failed, cancelled
    environment: str
    services: List[str]
    strategy: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    steps: List[DeploymentStep] = field(default_factory=list)
    health_checks: List[HealthCheck] = field(default_factory=list)
    
    def wait_for_completion(self, timeout: int = 3600) -> bool:
        """デプロイメント完了まで待機"""
        pass
    
    def cancel(self) -> bool:
        """デプロイメントをキャンセル"""
        pass
    
    def get_logs(self, level: str = None) -> List[LogEntry]:
        """デプロイメントログを取得"""
        pass
```

#### HealthStatus

```python
@dataclass
class HealthStatus:
    status: str  # healthy, unhealthy, unknown
    timestamp: datetime
    services: Dict[str, ServiceHealth]
    infrastructure: Dict[str, str]
    
    def is_healthy(self) -> bool:
        """全体的にヘルシーかどうか"""
        return self.status == "healthy"
```

#### MetricsData

```python
@dataclass
class MetricsData:
    metrics: List[MetricPoint]
    summary: Dict[str, float]
    
    def get_average(self, metric_name: str) -> float:
        """指定メトリクスの平均値を取得"""
        pass
    
    def get_max(self, metric_name: str) -> float:
        """指定メトリクスの最大値を取得"""
        pass
```

### 使用例

#### 1. 基本的なデプロイメント

```python
from services.auto_deployment import AutoDeploymentClient

client = AutoDeploymentClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# プロダクション環境にデプロイ
deployment = client.deploy(
    environment="production",
    services=["auth", "core-game"],
    strategy="blue-green"
)

# 完了まで待機
if deployment.wait_for_completion(timeout=1800):
    print("Deployment completed successfully")
else:
    print("Deployment failed or timed out")
```

#### 2. 監視付きデプロイメント

```python
import time
from services.auto_deployment import AutoDeploymentClient

client = AutoDeploymentClient(base_url="http://localhost:8080")

# デプロイメント開始
deployment = client.deploy(environment="production")

# 進捗を監視
while deployment.status in ["started", "running"]:
    print(f"Status: {deployment.status}")
    
    # ヘルスチェック
    health = client.get_health()
    if not health.is_healthy():
        print("Health check failed, considering rollback")
        break
    
    time.sleep(30)
    deployment = client.get_deployment(deployment.id)

print(f"Final status: {deployment.status}")
```

#### 3. 条件付きロールバック

```python
from services.auto_deployment import AutoDeploymentClient

client = AutoDeploymentClient(base_url="http://localhost:8080")

# デプロイメント後の監視
deployment = client.deploy(environment="production")
deployment.wait_for_completion()

# メトリクスを確認
metrics = client.get_metrics(start_time=deployment.completed_at)

# エラー率が高い場合はロールバック
error_rate = metrics.get_average("error_rate")
if error_rate > 0.05:  # 5%
    print(f"Error rate too high: {error_rate:.2%}")
    rollback = client.rollback(environment="production")
    print(f"Rollback initiated: {rollback.id}")
```

#### 4. バッチデプロイメント

```python
from services.auto_deployment import AutoDeploymentClient
from concurrent.futures import ThreadPoolExecutor

client = AutoDeploymentClient(base_url="http://localhost:8080")

environments = ["staging", "production"]
services = ["auth", "core-game", "task-mgmt"]

def deploy_to_environment(env):
    deployment = client.deploy(
        environment=env,
        services=services,
        strategy="blue-green"
    )
    deployment.wait_for_completion()
    return deployment

# 並列デプロイメント
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(deploy_to_environment, env) for env in environments]
    
    for future in futures:
        deployment = future.result()
        print(f"Environment {deployment.environment}: {deployment.status}")
```

#### 5. カスタム検証付きデプロイメント

```python
from services.auto_deployment import AutoDeploymentClient
from services.auto_deployment.validation import CustomValidator

class BusinessLogicValidator(CustomValidator):
    def validate(self, context):
        # カスタムビジネスロジック検証
        if not self.check_business_rules():
            return ValidationResult(
                success=False,
                message="Business logic validation failed"
            )
        return ValidationResult(success=True)

client = AutoDeploymentClient(base_url="http://localhost:8080")

# カスタムバリデーターを追加
client.add_validator(BusinessLogicValidator())

# 検証付きデプロイメント
deployment = client.deploy(
    environment="production",
    skip_validation=False  # 検証を実行
)
```

## エラーハンドリング

### HTTPエラーコード

| コード | 説明 | 対処方法 |
|--------|------|----------|
| 400 | Bad Request | リクエストパラメータを確認 |
| 401 | Unauthorized | 認証情報を確認 |
| 403 | Forbidden | 権限を確認 |
| 404 | Not Found | リソースの存在を確認 |
| 409 | Conflict | 既存のデプロイメントと競合 |
| 429 | Too Many Requests | レート制限に達している |
| 500 | Internal Server Error | サーバーログを確認 |

### Python例外

```python
from services.auto_deployment.exceptions import (
    DeploymentError,
    ValidationError,
    AuthenticationError,
    ConfigurationError
)

try:
    deployment = client.deploy(environment="production")
except AuthenticationError:
    print("Authentication failed")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
except DeploymentError as e:
    print(f"Deployment failed: {e.message}")
    if e.rollback_available:
        print("Rollback is available")
```

## レート制限

APIには以下のレート制限があります：

- **デプロイメント**: 1時間あたり10回
- **ヘルスチェック**: 1分あたり60回
- **メトリクス取得**: 1分あたり100回
- **その他のAPI**: 1分あたり1000回

レート制限に達した場合は、`429 Too Many Requests`が返されます。

## Webhook

デプロイメントイベントをWebhookで受信できます：

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    event = request.json
    
    if event['type'] == 'deployment.completed':
        print(f"Deployment {event['deployment_id']} completed")
    elif event['type'] == 'deployment.failed':
        print(f"Deployment {event['deployment_id']} failed")
    
    return 'OK'
```

Webhook設定：

```yaml
# config.yaml
webhooks:
  - url: "https://your-app.com/webhook"
    events: ["deployment.started", "deployment.completed", "deployment.failed"]
    secret: "webhook-secret"
```

このAPIドキュメントを参考に、Auto-Deployment Systemをプログラムから効率的に活用してください。