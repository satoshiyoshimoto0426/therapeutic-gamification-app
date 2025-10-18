# 🎉 AWSデプロイ完了ガイド

## デプロイが完了したら

おめでとうございます！アプリケーションがAWS上で稼働しています。

### 📍 アクセス方法

1. **ALBのDNS名を取得**
   ```bash
   aws elbv2 describe-load-balancers \
       --names therapeutic-app-alb \
       --query 'LoadBalancers[0].DNSName' \
       --output text
   ```

2. **ブラウザでアクセス**
   ```
   http://[ALB-DNS名]
   ```

3. **ヘルスチェック**
   ```bash
   curl http://[ALB-DNS名]/health
   ```

## 🔍 監視とログ

### リアルタイム監視

```bash
# 1回だけ状態確認
python monitor_aws_deployment.py

# 継続的に監視（30秒ごと）
python monitor_aws_deployment.py --continuous 30
```

### CloudWatch Logs

```bash
# 最新のログを表示
aws logs tail /ecs/therapeutic-app --follow

# 特定の時間範囲のログ
aws logs filter-log-events \
    --log-group-name /ecs/therapeutic-app \
    --start-time $(date -d '1 hour ago' +%s)000
```

### ECSコンソール

```
https://console.aws.amazon.com/ecs/
→ クラスター: therapeutic-app-cluster
→ サービス: therapeutic-app-service
```

## 🔧 運用タスク

### アプリケーションの更新

```bash
# 1. 新しいイメージをビルド
docker build -t therapeutic-app .

# 2. ECRにプッシュ
docker tag therapeutic-app:latest \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/therapeutic-app:latest

# 3. サービスを更新
aws ecs update-service \
    --cluster therapeutic-app-cluster \
    --service therapeutic-app-service \
    --force-new-deployment
```

### スケーリング

```bash
# タスク数を変更
aws ecs update-service \
    --cluster therapeutic-app-cluster \
    --service therapeutic-app-service \
    --desired-count 4
```

### ロールバック

```bash
# 前のタスク定義リビジョンを確認
aws ecs list-task-definitions \
    --family-prefix therapeutic-app \
    --sort DESC

# 特定のリビジョンにロールバック
aws ecs update-service \
    --cluster therapeutic-app-cluster \
    --service therapeutic-app-service \
    --task-definition therapeutic-app:[リビジョン番号]
```

## 🔒 セキュリティ設定

### HTTPS設定（推奨）

1. **AWS Certificate Managerで証明書を取得**
   ```bash
   aws acm request-certificate \
       --domain-name yourdomain.com \
       --validation-method DNS
   ```

2. **ALBにHTTPSリスナーを追加**
   ```bash
   aws elbv2 create-listener \
       --load-balancer-arn [ALB-ARN] \
       --protocol HTTPS \
       --port 443 \
       --certificates CertificateArn=[証明書ARN] \
       --default-actions Type=forward,TargetGroupArn=[TG-ARN]
   ```

### WAF設定

```bash
# AWS WAFでWebアプリケーションを保護
aws wafv2 create-web-acl \
    --name therapeutic-app-waf \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules file://waf-rules.json
```

### セキュリティグループの最適化

```bash
# 不要なポートを閉じる
aws ec2 revoke-security-group-ingress \
    --group-id [SG-ID] \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0
```

## 📊 モニタリング設定

### CloudWatch Alarms

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
    --evaluation-periods 2 \
    --dimensions Name=ServiceName,Value=therapeutic-app-service \
                 Name=ClusterName,Value=therapeutic-app-cluster

# メモリ使用率アラーム
aws cloudwatch put-metric-alarm \
    --alarm-name therapeutic-app-high-memory \
    --alarm-description "メモリ使用率が80%を超えた" \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=ServiceName,Value=therapeutic-app-service \
                 Name=ClusterName,Value=therapeutic-app-cluster
```

### SNS通知設定

```bash
# SNSトピック作成
aws sns create-topic --name therapeutic-app-alerts

# メール通知を登録
aws sns subscribe \
    --topic-arn arn:aws:sns:ap-northeast-1:[ACCOUNT-ID]:therapeutic-app-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com

# アラームにSNSを関連付け
aws cloudwatch put-metric-alarm \
    --alarm-name therapeutic-app-high-cpu \
    --alarm-actions arn:aws:sns:ap-northeast-1:[ACCOUNT-ID]:therapeutic-app-alerts \
    [その他のパラメータ...]
```

## 💰 コスト管理

### コスト確認

```bash
# 今月のコストを確認
aws ce get-cost-and-usage \
    --time-period Start=$(date -d 'first day of this month' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=SERVICE
```

### コスト最適化のヒント

1. **Auto Scaling設定**
   - 負荷に応じて自動スケール
   - 夜間はタスク数を減らす

2. **Spot Instancesの活用**
   - 開発環境ではSpotを使用
   - 最大70%のコスト削減

3. **不要なリソースの削除**
   - 古いECRイメージを削除
   - 未使用のロードバランサーを削除

## 🔄 バックアップ

### Firestoreバックアップ

```bash
# Firestoreのエクスポート
gcloud firestore export gs://[BUCKET-NAME]/backups/$(date +%Y%m%d)
```

### 設定のバックアップ

```bash
# タスク定義をエクスポート
aws ecs describe-task-definition \
    --task-definition therapeutic-app \
    > task-definition-backup.json

# サービス設定をエクスポート
aws ecs describe-services \
    --cluster therapeutic-app-cluster \
    --services therapeutic-app-service \
    > service-backup.json
```

## 📞 トラブルシューティング

### サービスが起動しない

```bash
# タスクの停止理由を確認
aws ecs describe-tasks \
    --cluster therapeutic-app-cluster \
    --tasks [TASK-ID] \
    --query 'tasks[0].stoppedReason'

# ログを確認
aws logs tail /ecs/therapeutic-app --follow
```

### ヘルスチェック失敗

```bash
# ターゲットグループのヘルスを確認
aws elbv2 describe-target-health \
    --target-group-arn [TG-ARN]

# セキュリティグループを確認
aws ec2 describe-security-groups \
    --group-ids [SG-ID]
```

### パフォーマンス問題

```bash
# メトリクスを確認
python monitor_aws_deployment.py

# タスク数を増やす
aws ecs update-service \
    --cluster therapeutic-app-cluster \
    --service therapeutic-app-service \
    --desired-count 4
```

## 📚 参考リンク

- [AWS ECS ドキュメント](https://docs.aws.amazon.com/ecs/)
- [AWS CloudWatch ドキュメント](https://docs.aws.amazon.com/cloudwatch/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## ✅ チェックリスト

デプロイ後に確認すべき項目：

- [ ] アプリケーションにアクセスできる
- [ ] ヘルスチェックが成功している
- [ ] ログが正常に出力されている
- [ ] HTTPSを設定した（本番環境）
- [ ] CloudWatch Alarmsを設定した
- [ ] バックアップを設定した
- [ ] コスト監視を設定した
- [ ] ドキュメントを更新した

---

**おめでとうございます！🎉**

アプリケーションが本番環境で稼働しています。
定期的な監視とメンテナンスを忘れずに！
