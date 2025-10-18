# AWS 簡易デプロイ手順

## 🚨 最優先事項：認証情報のローテーション

デプロイ前に**必ず**以下を実行してください：

### 1. AWS認証情報の再発行
```
https://console.aws.amazon.com/iam/
→ ユーザー → セキュリティ認証情報 → アクセスキーを削除 → 新規作成
```

### 2. LINE認証情報の再発行
```
https://developers.line.biz/console/
→ チャンネル選択 → Messaging API設定 → トークン再発行
```

## 📋 デプロイ手順（3ステップ）

### ステップ1: AWS CLIの設定

```bash
# AWS CLIをインストール（未インストールの場合）
# Windows: https://aws.amazon.com/cli/

# 新しい認証情報で設定
aws configure
# AWS Access Key ID: [新しいキー]
# AWS Secret Access Key: [新しいシークレット]
# Default region name: ap-northeast-1
# Default output format: json
```

### ステップ2: Dockerイメージのビルドとプッシュ

```bash
# ECRリポジトリ作成
aws ecr create-repository --repository-name therapeutic-app --region ap-northeast-1

# アカウントIDを取得
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# ECRにログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com

# イメージをビルド
docker build -t therapeutic-app .

# タグ付け
docker tag therapeutic-app:latest $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest

# プッシュ
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
```

### ステップ3: 自動デプロイ実行

```bash
# Pythonスクリプトを実行
python deploy_to_aws.py

# プロンプトでECR URIを入力:
# 例: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
```

## ✅ デプロイ後の確認

### アプリケーションの動作確認

```bash
# ALBのDNS名を取得
aws elbv2 describe-load-balancers --names therapeutic-app-alb --query 'LoadBalancers[0].DNSName' --output text

# ヘルスチェック
curl http://[ALB-DNS]/health
```

### ログの確認

```bash
# CloudWatch Logsを確認
aws logs tail /ecs/therapeutic-app --follow
```

### サービスの状態確認

```bash
# ECSサービスの状態
aws ecs describe-services --cluster therapeutic-app-cluster --services therapeutic-app-service
```

## 🔧 トラブルシューティング

### タスクが起動しない場合

```bash
# タスクの詳細を確認
aws ecs list-tasks --cluster therapeutic-app-cluster
aws ecs describe-tasks --cluster therapeutic-app-cluster --tasks [タスクID]
```

### 接続できない場合

1. セキュリティグループの確認
2. ターゲットグループのヘルスチェック確認
3. タスクのログ確認

## 🔄 更新デプロイ

```bash
# 新しいイメージをビルド＆プッシュ
docker build -t therapeutic-app .
docker tag therapeutic-app:latest $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest

# サービスを更新（新しいタスク定義で）
aws ecs update-service --cluster therapeutic-app-cluster --service therapeutic-app-service --force-new-deployment
```

## 💰 コスト見積もり

- Fargate (512 CPU, 1GB RAM, 2タスク): 約$30-40/月
- Application Load Balancer: 約$20-25/月
- データ転送: 使用量による
- **合計見積もり**: 約$50-70/月

## 🛑 リソースの削除（必要な場合）

```bash
# サービス削除
aws ecs update-service --cluster therapeutic-app-cluster --service therapeutic-app-service --desired-count 0
aws ecs delete-service --cluster therapeutic-app-cluster --service therapeutic-app-service

# クラスター削除
aws ecs delete-cluster --cluster therapeutic-app-cluster

# ロードバランサー削除
aws elbv2 delete-load-balancer --load-balancer-arn [ARN]

# その他のリソースも同様に削除
```

## 📞 サポート

問題が発生した場合：
1. CloudWatch Logsを確認
2. ECSサービスイベントを確認
3. AWS_DEPLOYMENT_GUIDE.mdの詳細手順を参照

---

**重要**: 本番環境では必ずHTTPS（SSL/TLS）を設定してください！
