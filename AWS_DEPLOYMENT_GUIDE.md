# AWS本番環境デプロイガイド

## ⚠️ セキュリティ重要事項

### 認証情報のローテーション（最優先）

デプロイ前に、以下の認証情報を**必ず**再発行してください：

1. **AWS認証情報の再発行**
   ```bash
   # AWS IAMコンソールにアクセス
   # https://console.aws.amazon.com/iam/
   
   # 手順：
   # 1. 左メニュー「ユーザー」→ 該当ユーザーを選択
   # 2. 「セキュリティ認証情報」タブ
   # 3. 古いアクセスキーを「無効化」→「削除」
   # 4. 「アクセスキーを作成」で新規発行
   ```

2. **LINE認証情報の再発行**
   ```bash
   # LINE Developers Consoleにアクセス
   # https://developers.line.biz/console/
   
   # 手順：
   # 1. 該当チャンネルを選択
   # 2. 「Messaging API設定」タブ
   # 3. 「チャネルアクセストークン」を再発行
   ```

## デプロイ方法の選択

### オプション1: AWS ECS (Fargate) - 推奨
コンテナベースのマネージドサービス。スケーラブルで管理が容易。

### オプション2: AWS Elastic Beanstalk
アプリケーションのデプロイと管理を自動化。

### オプション3: AWS Lambda + API Gateway
サーバーレスアーキテクチャ。コスト効率が高い。

## 前提条件

- AWS CLI インストール済み
- Docker インストール済み（ECS使用時）
- 新しいAWS認証情報
- AWSアカウントに適切な権限

## デプロイ手順（ECS Fargate）

### 1. AWS認証情報の設定

```bash
# 新しい認証情報で設定
aws configure

# 入力項目：
# AWS Access Key ID: [新しいアクセスキー]
# AWS Secret Access Key: [新しいシークレットキー]
# Default region name: ap-northeast-1  # 東京リージョン
# Default output format: json
```

### 2. 環境変数の設定

```bash
# .env.production ファイルを作成（このファイルは.gitignoreに追加）
cat > .env.production << 'EOF'
# データベース
FIRESTORE_PROJECT_ID=your-project-id

# LINE Bot（新しい認証情報）
LINE_CHANNEL_ACCESS_TOKEN=your-new-token
LINE_CHANNEL_SECRET=your-new-secret

# JWT
JWT_SECRET=your-secure-random-string

# 環境
ENVIRONMENT=production
EOF
```

### 3. AWS Secrets Managerに認証情報を保存

```bash
# LINE認証情報を保存
aws secretsmanager create-secret \
    --name therapeutic-app/line-credentials \
    --description "LINE Bot credentials" \
    --secret-string '{
        "channel_access_token":"新しいLINEアクセストークン",
        "channel_secret":"新しいLINEシークレット"
    }'

# その他の機密情報
aws secretsmanager create-secret \
    --name therapeutic-app/app-secrets \
    --description "Application secrets" \
    --secret-string '{
        "jwt_secret":"ランダムな文字列",
        "firestore_project_id":"your-project-id"
    }'
```

### 4. ECRリポジトリの作成

```bash
# コンテナレジストリを作成
aws ecr create-repository \
    --repository-name therapeutic-app \
    --region ap-northeast-1
```

### 5. Dockerイメージのビルドとプッシュ

```bash
# ECRにログイン
aws ecr get-login-password --region ap-northeast-1 | \
    docker login --username AWS --password-stdin \
    [アカウントID].dkr.ecr.ap-northeast-1.amazonaws.com

# イメージをビルド
docker build -t therapeutic-app .

# タグ付け
docker tag therapeutic-app:latest \
    [アカウントID].dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest

# プッシュ
docker push [アカウントID].dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
```

### 6. ECSクラスターとサービスの作成

自動デプロイスクリプトを使用：

```bash
python deploy_to_aws.py
```

## デプロイ後の確認

### ヘルスチェック

```bash
# サービスのステータス確認
aws ecs describe-services \
    --cluster therapeutic-app-cluster \
    --services therapeutic-app-service

# ログ確認
aws logs tail /ecs/therapeutic-app --follow
```

### エンドポイントテスト

```bash
# ALBのDNS名を取得
aws elbv2 describe-load-balancers \
    --names therapeutic-app-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text

# ヘルスチェック
curl http://[ALB-DNS]/health
```

## ロールバック手順

問題が発生した場合：

```bash
# 前のタスク定義にロールバック
aws ecs update-service \
    --cluster therapeutic-app-cluster \
    --service therapeutic-app-service \
    --task-definition therapeutic-app:[前のリビジョン番号]
```

## モニタリング設定

### CloudWatch アラーム

```bash
# CPU使用率アラーム
aws cloudwatch put-metric-alarm \
    --alarm-name therapeutic-app-high-cpu \
    --alarm-description "CPU使用率が80%を超えた" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

## コスト最適化

- **Auto Scaling**: 負荷に応じて自動スケール
- **Spot Instances**: 開発環境ではSpotインスタンスを使用
- **リソース監視**: 不要なリソースを定期的に削除

## トラブルシューティング

### タスクが起動しない

```bash
# タスクの詳細を確認
aws ecs describe-tasks \
    --cluster therapeutic-app-cluster \
    --tasks [タスクID]

# ログを確認
aws logs get-log-events \
    --log-group-name /ecs/therapeutic-app \
    --log-stream-name [ストリーム名]
```

### 接続エラー

- セキュリティグループの設定を確認
- VPCとサブネットの設定を確認
- IAMロールの権限を確認

## セキュリティベストプラクティス

1. **認証情報は環境変数やSecrets Managerで管理**
2. **最小権限の原則でIAMロールを設定**
3. **VPC内でプライベートサブネットを使用**
4. **ALBでHTTPS（SSL/TLS）を設定**
5. **WAF（Web Application Firewall）を有効化**
6. **定期的なセキュリティパッチ適用**

## サポート

問題が発生した場合は、以下を確認してください：
- CloudWatch Logs
- ECSサービスイベント
- ALBターゲットグループのヘルスチェック

---

**重要**: デプロイ前に必ず認証情報をローテーションしてください！
