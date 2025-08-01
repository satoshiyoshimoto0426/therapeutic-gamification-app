# トラブルシューティングガイド

## 概要
治療的ゲーミフィケーションアプリケーションの問題解決手順書です。

## 一般的な問題

### 1. アプリケーション起動しない

#### 症状
- サービスが起動しない
- ヘルスチェックが失敗する

#### 原因と対処法
1. **ポート競合**
   ```bash
   # ポート使用状況確認
   netstat -tulpn | grep :8080
   
   # プロセス終了
   kill -9 <PID>
   ```

2. **依存関係の問題**
   ```bash
   # 依存関係再インストール
   pip install -r requirements.txt --force-reinstall
   ```

3. **環境変数未設定**
   ```bash
   # 必要な環境変数を確認
   python -c "import os; print([k for k in os.environ.keys() if 'THERAPEUTIC' in k])"
   ```

### 2. データベース接続エラー

#### 症状
- Firestore接続失敗
- データ取得エラー

#### 対処法
1. **認証確認**
   ```bash
   # サービスアカウントキー確認
   echo $GOOGLE_APPLICATION_CREDENTIALS
   
   # 権限確認
   gcloud auth list
   ```

2. **ネットワーク確認**
   ```bash
   # Firestore接続テスト
   python -c "from google.cloud import firestore; db = firestore.Client(); print('Connection OK')"
   ```

### 3. API応答が遅い

#### 症状
- レスポンス時間が1.2秒を超える
- タイムアウトエラー

#### 対処法
1. **パフォーマンス分析**
   ```bash
   # パフォーマンステスト実行
   python infrastructure/production/performance_scalability_test.py
   ```

2. **リソース確認**
   ```bash
   # CPU・メモリ使用率確認
   top
   free -h
   ```

3. **データベースクエリ最適化**
   - インデックス確認
   - クエリ実行計画分析

### 4. 治療安全性機能の問題

#### 症状
- コンテンツモデレーションが機能しない
- CBT介入が発動しない

#### 対処法
1. **OpenAI API確認**
   ```bash
   # API キー確認
   python -c "import openai; print(openai.api_key[:10] + '...')"
   
   # API接続テスト
   curl -H "Authorization: Bearer $OPENAI_API_KEY"         https://api.openai.com/v1/models
   ```

2. **モデレーション設定確認**
   ```bash
   # 設定ファイル確認
   cat services/therapeutic-safety/config.json
   ```

### 5. LINE Bot が応答しない

#### 症状
- メッセージが送信されない
- Webhook エラー

#### 対処法
1. **LINE API設定確認**
   ```bash
   # チャンネルアクセストークン確認
   echo $LINE_CHANNEL_ACCESS_TOKEN | cut -c1-10
   
   # Webhook URL確認
   curl -X GET https://api.line.me/v2/bot/info         -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN"
   ```

2. **Webhook設定確認**
   ```bash
   # Webhook URL テスト
   curl -X POST https://your-domain.com/api/line/webhook         -H "Content-Type: application/json"         -d '{"events":[]}'
   ```

## パフォーマンス問題

### メモリリーク
1. **メモリ使用量監視**
   ```bash
   # プロセスメモリ確認
   ps aux | grep python | head -5
   
   # メモリリークテスト
   python infrastructure/production/performance_scalability_test.py --test memory_leaks
   ```

2. **ガベージコレクション強制実行**
   ```python
   import gc
   gc.collect()
   ```

### CPU使用率高騰
1. **プロファイリング**
   ```bash
   # CPU使用率の高いプロセス特定
   top -p $(pgrep -f "python.*main.py")
   
   # プロファイリング実行
   python -m cProfile -o profile.stats main.py
   ```

## セキュリティ問題

### 不正アクセス検知
1. **アクセスログ確認**
   ```bash
   # 異常なアクセスパターン検索
   grep "401\|403\|429" /var/log/nginx/access.log | tail -20
   
   # IP別アクセス数集計
   awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -10
   ```

2. **セキュリティ監査実行**
   ```bash
   python infrastructure/production/security_audit.py
   ```

### SSL証明書期限切れ
1. **証明書確認**
   ```bash
   # 証明書有効期限確認
   openssl x509 -in /path/to/cert.pem -text -noout | grep "Not After"
   
   # 自動更新設定確認
   certbot certificates
   ```

## 監視・アラート

### ログ分析
```bash
# エラーログ抽出
grep -i error /var/log/therapeutic-gaming/*.log | tail -50

# 特定時間範囲のログ
journalctl --since "2024-01-01 00:00:00" --until "2024-01-01 23:59:59" -u therapeutic-gaming
```

### メトリクス確認
```bash
# Prometheus メトリクス確認
curl http://localhost:9090/metrics | grep therapeutic_gaming

# Grafana ダッシュボード URL
echo "http://monitoring.your-domain.com/d/therapeutic-gaming"
```

## 緊急時対応

### サービス緊急停止
```bash
# 全サービス停止
sudo systemctl stop therapeutic-gaming-*

# 特定サービスのみ停止
sudo systemctl stop therapeutic-gaming-core-game
```

### 緊急メンテナンスモード
```bash
# メンテナンスページ表示
sudo cp /var/www/maintenance.html /var/www/html/index.html

# ロードバランサーからの除外
gcloud compute backend-services remove-backend therapeutic-gaming-backend   --instance-group=therapeutic-gaming-ig   --instance-group-zone=asia-northeast1-a
```

## 連絡先・エスカレーション

### 緊急時連絡先
- **Level 1 Support**: support@therapeutic-gaming.com
- **Level 2 Engineering**: engineering@therapeutic-gaming.com  
- **Level 3 Architecture**: architecture@therapeutic-gaming.com
- **緊急時**: emergency@therapeutic-gaming.com (24時間対応)

### エスカレーション基準
- **15分以内**: Level 1 → Level 2
- **30分以内**: Level 2 → Level 3
- **1時間以内**: Level 3 → Management

## 参考資料
- [API仕様書](./api_documentation.md)
- [運用マニュアル](./operations_manual.md)
- [デプロイメントガイド](./deployment_guide.md)
- [システム設計書](../docs/design.md)
