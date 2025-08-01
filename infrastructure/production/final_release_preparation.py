#!/usr/bin/env python3
"""
最終リリース準備スクリプト
全機能の統合テスト、セキュリティ監査、パフォーマンステスト、ドキュメント整備を実行
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 既存のテストモジュールをインポート
from final_integration_test import FinalIntegrationTester
from security_audit import SecurityAuditor
from performance_scalability_test import PerformanceScalabilityTester

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_release_preparation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FinalReleasePreparation:
    """最終リリース準備クラス"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target": base_url,
            "phases": {},
            "overall_status": "UNKNOWN",
            "release_readiness": "UNKNOWN"
        }
        
        # 出力ディレクトリ作成
        self.output_dir = Path("release_reports")
        self.output_dir.mkdir(exist_ok=True)
    
    async def phase_1_integration_tests(self) -> Dict:
        """フェーズ1: 全機能統合テスト"""
        logger.info("=== フェーズ1: 全機能統合テスト開始 ===")
        
        phase_result = {
            "name": "integration_tests",
            "status": "UNKNOWN",
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        try:
            # 統合テスト実行
            tester = FinalIntegrationTester(self.base_url)
            test_results = await tester.run_all_tests()
            
            phase_result["tests"] = test_results["tests"]
            phase_result["summary"] = test_results["summary"]
            phase_result["status"] = test_results["overall_status"]
            
            # レポート保存
            report_content = tester.generate_report()
            report_path = self.output_dir / "integration_test_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            # JSON結果保存
            json_path = self.output_dir / "integration_test_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"統合テスト完了: {phase_result['status']}")
            
        except Exception as e:
            phase_result["status"] = "ERROR"
            phase_result["error"] = str(e)
            logger.error(f"統合テストエラー: {e}")
        
        phase_result["end_time"] = datetime.now().isoformat()
        return phase_result
    
    async def phase_2_security_audit(self) -> Dict:
        """フェーズ2: セキュリティ監査"""
        logger.info("=== フェーズ2: セキュリティ監査開始 ===")
        
        phase_result = {
            "name": "security_audit",
            "status": "UNKNOWN",
            "start_time": datetime.now().isoformat(),
            "audits": {},
            "summary": {}
        }
        
        try:
            # セキュリティ監査実行
            auditor = SecurityAuditor(self.base_url)
            audit_results = auditor.run_all_audits()
            
            phase_result["audits"] = audit_results["audits"]
            phase_result["summary"] = audit_results["summary"]
            phase_result["status"] = audit_results["overall_status"]
            
            # レポート保存
            report_content = auditor.generate_report()
            report_path = self.output_dir / "security_audit_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            # JSON結果保存
            json_path = self.output_dir / "security_audit_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(audit_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"セキュリティ監査完了: {phase_result['status']}")
            
        except Exception as e:
            phase_result["status"] = "ERROR"
            phase_result["error"] = str(e)
            logger.error(f"セキュリティ監査エラー: {e}")
        
        phase_result["end_time"] = datetime.now().isoformat()
        return phase_result
    
    async def phase_3_performance_tests(self) -> Dict:
        """フェーズ3: パフォーマンステスト"""
        logger.info("=== フェーズ3: パフォーマンステスト開始 ===")
        
        phase_result = {
            "name": "performance_tests",
            "status": "UNKNOWN",
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        try:
            # パフォーマンステスト実行
            tester = PerformanceScalabilityTester(self.base_url)
            test_results = await tester.run_all_tests()
            
            phase_result["tests"] = test_results["tests"]
            phase_result["summary"] = test_results["summary"]
            phase_result["status"] = test_results["overall_status"]
            
            # レポート保存
            report_content = tester.generate_report()
            report_path = self.output_dir / "performance_test_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            # JSON結果保存
            json_path = self.output_dir / "performance_test_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"パフォーマンステスト完了: {phase_result['status']}")
            
        except Exception as e:
            phase_result["status"] = "ERROR"
            phase_result["error"] = str(e)
            logger.error(f"パフォーマンステストエラー: {e}")
        
        phase_result["end_time"] = datetime.now().isoformat()
        return phase_result
    
    def phase_4_documentation(self) -> Dict:
        """フェーズ4: ドキュメント整備"""
        logger.info("=== フェーズ4: ドキュメント整備開始 ===")
        
        phase_result = {
            "name": "documentation",
            "status": "UNKNOWN",
            "start_time": datetime.now().isoformat(),
            "documents": {},
            "summary": {}
        }
        
        try:
            # 各種ドキュメント生成
            documents_created = []
            
            # 1. API仕様書の確認・更新
            api_docs = self.generate_api_documentation()
            if api_docs:
                documents_created.append("API仕様書")
                phase_result["documents"]["api_documentation"] = api_docs
            
            # 2. ユーザーマニュアルの確認・更新
            user_manual = self.update_user_manual()
            if user_manual:
                documents_created.append("ユーザーマニュアル")
                phase_result["documents"]["user_manual"] = user_manual
            
            # 3. 運用マニュアルの作成
            ops_manual = self.generate_operations_manual()
            if ops_manual:
                documents_created.append("運用マニュアル")
                phase_result["documents"]["operations_manual"] = ops_manual
            
            # 4. デプロイメントガイドの作成
            deploy_guide = self.generate_deployment_guide()
            if deploy_guide:
                documents_created.append("デプロイメントガイド")
                phase_result["documents"]["deployment_guide"] = deploy_guide
            
            # 5. トラブルシューティングガイドの作成
            troubleshooting = self.generate_troubleshooting_guide()
            if troubleshooting:
                documents_created.append("トラブルシューティングガイド")
                phase_result["documents"]["troubleshooting_guide"] = troubleshooting
            
            phase_result["summary"] = {
                "documents_created": len(documents_created),
                "document_list": documents_created
            }
            
            if len(documents_created) >= 4:  # 最低4つのドキュメント
                phase_result["status"] = "PASS"
            elif len(documents_created) >= 2:
                phase_result["status"] = "PARTIAL"
            else:
                phase_result["status"] = "FAIL"
            
            logger.info(f"ドキュメント整備完了: {len(documents_created)}個のドキュメントを作成")
            
        except Exception as e:
            phase_result["status"] = "ERROR"
            phase_result["error"] = str(e)
            logger.error(f"ドキュメント整備エラー: {e}")
        
        phase_result["end_time"] = datetime.now().isoformat()
        return phase_result
    
    def generate_api_documentation(self) -> Optional[str]:
        """API仕様書生成"""
        try:
            api_doc_content = """# API仕様書

## 概要
治療的ゲーミフィケーションアプリケーションのAPI仕様書です。

## 認証
すべてのAPIエンドポイントはJWTトークンによる認証が必要です。

```
Authorization: Bearer <JWT_TOKEN>
```

## エンドポイント一覧

### 認証API
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/profile` - プロファイル取得
- `POST /api/auth/refresh` - トークン更新

### ゲームAPI
- `GET /api/game/profile` - ゲームプロファイル取得
- `POST /api/game/xp` - XP追加
- `GET /api/game/level` - レベル情報取得
- `POST /api/game/resonance` - 共鳴イベントチェック

### タスク管理API
- `GET /api/tasks` - タスク一覧取得
- `POST /api/tasks/create` - タスク作成
- `POST /api/tasks/{id}/complete` - タスク完了
- `GET /api/tasks/stats` - タスク統計取得

### Mandala API
- `GET /api/mandala/grid` - Mandalaグリッド取得
- `POST /api/mandala/unlock` - セルアンロック
- `GET /api/mandala/progress` - 進捗取得

### ストーリーAPI
- `POST /api/story/generate` - ストーリー生成
- `GET /api/story/current` - 現在のストーリー取得
- `POST /api/story/choice` - 選択肢選択

### 治療安全性API
- `POST /api/safety/moderate` - コンテンツモデレーション
- `GET /api/safety/metrics` - 安全性メトリクス取得
- `POST /api/safety/cbt-intervention` - CBT介入

## エラーレスポンス
```json
{
  "error": "error_code",
  "message": "エラーメッセージ",
  "details": {}
}
```

## レート制限
- 120リクエスト/分/IP
- 認証済みユーザー: 300リクエスト/分

## データ形式
すべてのAPIはJSON形式でデータを送受信します。
"""
            
            doc_path = self.output_dir / "api_documentation.md"
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(api_doc_content)
            
            return str(doc_path)
            
        except Exception as e:
            logger.error(f"API仕様書生成エラー: {e}")
            return None
    
    def update_user_manual(self) -> Optional[str]:
        """ユーザーマニュアル更新"""
        try:
            # 既存のユーザーマニュアルを確認
            existing_manual = Path("docs/user_manual.md")
            
            if existing_manual.exists():
                # 既存マニュアルをコピーして更新
                with open(existing_manual, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # リリース情報を追加
                updated_content = f"""# ユーザーマニュアル

## リリース情報
- **バージョン**: 1.0.0
- **リリース日**: {datetime.now().strftime('%Y年%m月%d日')}
- **対応環境**: スマートフォン、タブレット、PC

{content}

## サポート情報
- **問い合わせ先**: support@therapeutic-gaming.com
- **FAQ**: https://docs.therapeutic-gaming.com/faq
- **コミュニティ**: https://community.therapeutic-gaming.com
"""
            else:
                # 新規マニュアル作成
                updated_content = """# ユーザーマニュアル

## はじめに
治療的ゲーミフィケーションアプリへようこそ。このアプリは、ADHD、不登校、若年NEET層の方々の自己効力感再構築と社会復帰を支援するために設計されています。

## 基本的な使い方

### 1. アカウント登録
1. アプリを起動し、「新規登録」をタップ
2. メールアドレスとパスワードを入力
3. 利用規約に同意して登録完了

### 2. 初期設定
1. プロファイル情報を入力
2. 治療目標を設定
3. 通知設定を調整

### 3. 日々の使い方
1. 朝7時にLINE Botからタスクが配信されます
2. タスクを完了したらワンタップで報告
3. 夜21:30にAIが生成したストーリーを楽しみます
4. 22時にグルノート（振り返り）を記入

## 機能説明

### Mandalaシステム
9x9のグリッドで成長を可視化します。8つの属性（自律性、共感力、回復力、好奇心、コミュニケーション、創造性、勇気、知恵）をバランスよく育てましょう。

### XPとレベルシステム
タスク完了でXPを獲得し、レベルアップします。キャラクター「ユウ」と自分のレベルが連動し、差が5以上になると特別な共鳴イベントが発生します。

### 治療安全性機能
AIが有害なコンテンツを自動検出し、必要に応じてCBT（認知行動療法）ベースの介入を提供します。

## トラブルシューティング

### よくある問題
- **ログインできない**: パスワードリセット機能をご利用ください
- **通知が来ない**: 端末の通知設定を確認してください
- **アプリが重い**: 端末を再起動してください

### サポート
問題が解決しない場合は、アプリ内の「お問い合わせ」からご連絡ください。
"""
            
            manual_path = self.output_dir / "user_manual_updated.md"
            with open(manual_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            return str(manual_path)
            
        except Exception as e:
            logger.error(f"ユーザーマニュアル更新エラー: {e}")
            return None
    
    def generate_operations_manual(self) -> Optional[str]:
        """運用マニュアル生成"""
        try:
            ops_manual_content = """# 運用マニュアル

## 概要
治療的ゲーミフィケーションアプリケーションの運用手順書です。

## 日常運用

### 監視項目
1. **システム稼働状況**
   - アプリケーションサーバーの稼働状況
   - データベースの接続状況
   - 外部API（OpenAI、LINE）の応答状況

2. **パフォーマンス指標**
   - レスポンス時間（P95 < 1.2秒）
   - スループット（120 req/min以上）
   - エラー率（< 1%）

3. **治療安全性指標**
   - コンテンツモデレーションF1スコア（> 98%）
   - CBT介入実行率
   - ユーザー報告件数

### 定期メンテナンス
- **日次**: ログ確認、バックアップ確認
- **週次**: パフォーマンス分析、セキュリティ更新
- **月次**: 容量計画見直し、依存関係更新

## 障害対応

### 緊急度レベル
- **Critical**: サービス全停止、データ損失
- **High**: 主要機能停止、セキュリティ問題
- **Medium**: 一部機能停止、パフォーマンス劣化
- **Low**: 軽微な不具合、改善要望

### エスカレーション手順
1. 障害検知（監視アラート、ユーザー報告）
2. 初期対応（影響範囲確認、暫定対処）
3. 根本原因調査
4. 恒久対策実施
5. 事後レビュー

## セキュリティ運用

### 定期セキュリティチェック
- 脆弱性スキャン（月次）
- ペネトレーションテスト（四半期）
- アクセスログ監査（週次）

### インシデント対応
1. セキュリティインシデント検知
2. 影響範囲の特定
3. 封じ込め対策実施
4. 証拠保全
5. 関係者への報告
6. 復旧作業
7. 事後対策

## データ管理

### バックアップ
- **頻度**: 日次自動バックアップ
- **保存期間**: 30日間
- **復旧テスト**: 月次実施

### データ保護
- 個人情報の暗号化
- アクセス制御の実施
- 監査ログの記録

## 連絡先
- **開発チーム**: dev-team@therapeutic-gaming.com
- **インフラチーム**: infra-team@therapeutic-gaming.com
- **セキュリティチーム**: security-team@therapeutic-gaming.com
"""
            
            manual_path = self.output_dir / "operations_manual.md"
            with open(manual_path, "w", encoding="utf-8") as f:
                f.write(ops_manual_content)
            
            return str(manual_path)
            
        except Exception as e:
            logger.error(f"運用マニュアル生成エラー: {e}")
            return None
    
    def generate_deployment_guide(self) -> Optional[str]:
        """デプロイメントガイド生成"""
        try:
            deploy_guide_content = """# デプロイメントガイド

## 概要
治療的ゲーミフィケーションアプリケーションのデプロイメント手順書です。

## 前提条件

### 必要なツール
- Docker
- Google Cloud SDK
- kubectl
- Python 3.9+
- Node.js 16+

### 環境変数
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-northeast1"
export CLUSTER_NAME="therapeutic-gaming-cluster"
```

## ローカル環境セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/your-org/therapeutic-gaming-app.git
cd therapeutic-gaming-app
```

### 2. 依存関係インストール
```bash
# Python依存関係
pip install -r requirements.txt

# Node.js依存関係（フロントエンド）
cd frontend
npm install
cd ..
```

### 3. ローカル起動
```bash
python deploy_local.py
```

## 本番環境デプロイ

### 1. 事前準備
```bash
# GCPプロジェクト設定
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# 認証
gcloud auth login
gcloud auth configure-docker
```

### 2. インフラストラクチャ構築
```bash
# Terraformでインフラ構築
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 3. アプリケーションデプロイ
```bash
# CI/CDパイプライン実行
cd infrastructure/production
./deploy_script.sh
```

### 4. デプロイ後確認
```bash
# ヘルスチェック
curl https://your-domain.com/health

# 統合テスト実行
python final_integration_test.py --target https://your-domain.com
```

## ロールバック手順

### 1. 前バージョンへのロールバック
```bash
# 最新の安定版リビジョンを取得
python get_last_stable_revision.py

# ロールバック実行
gcloud run services update-traffic therapeutic-gaming-service \
  --to-revisions=REVISION_NAME=100 \
  --region=$REGION
```

### 2. データベースロールバック
```bash
# バックアップからの復元
gcloud sql backups restore BACKUP_ID \
  --restore-instance=therapeutic-gaming-db \
  --backup-instance=therapeutic-gaming-db
```

## 監視設定

### 1. アラート設定
```bash
# 監視ダッシュボード作成
gcloud monitoring dashboards create \
  --config-from-file=monitoring-dashboard.json
```

### 2. ログ設定
```bash
# ログ集約設定
gcloud logging sinks create therapeutic-gaming-logs \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/app_logs
```

## トラブルシューティング

### よくある問題
1. **デプロイ失敗**: ログを確認し、権限設定を見直す
2. **接続エラー**: ファイアウォール設定を確認
3. **パフォーマンス問題**: リソース配分を調整

### ログ確認方法
```bash
# アプリケーションログ
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# エラーログのみ
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=20
```

## セキュリティ設定

### SSL証明書
```bash
# Let's Encrypt証明書取得
gcloud compute ssl-certificates create therapeutic-gaming-ssl \
  --domains=your-domain.com
```

### WAF設定
```bash
# Cloud Armor設定
gcloud compute security-policies create therapeutic-gaming-waf \
  --description="WAF for therapeutic gaming app"
```

## 連絡先
デプロイメントに関する問題は以下にお問い合わせください：
- **DevOpsチーム**: devops@therapeutic-gaming.com
- **緊急時**: emergency@therapeutic-gaming.com
"""
            
            guide_path = self.output_dir / "deployment_guide.md"
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(deploy_guide_content)
            
            return str(guide_path)
            
        except Exception as e:
            logger.error(f"デプロイメントガイド生成エラー: {e}")
            return None
    
    def generate_troubleshooting_guide(self) -> Optional[str]:
        """トラブルシューティングガイド生成"""
        try:
            troubleshooting_content = """# トラブルシューティングガイド

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
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
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
   curl -X GET https://api.line.me/v2/bot/info \
        -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN"
   ```

2. **Webhook設定確認**
   ```bash
   # Webhook URL テスト
   curl -X POST https://your-domain.com/api/line/webhook \
        -H "Content-Type: application/json" \
        -d '{"events":[]}'
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
   grep "401\\|403\\|429" /var/log/nginx/access.log | tail -20
   
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
gcloud compute backend-services remove-backend therapeutic-gaming-backend \
  --instance-group=therapeutic-gaming-ig \
  --instance-group-zone=asia-northeast1-a
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
"""
            
            guide_path = self.output_dir / "troubleshooting_guide.md"
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(troubleshooting_content)
            
            return str(guide_path)
            
        except Exception as e:
            logger.error(f"トラブルシューティングガイド生成エラー: {e}")
            return None
    
    def evaluate_release_readiness(self) -> str:
        """リリース準備状況評価"""
        phases = self.results["phases"]
        
        # 各フェーズの結果を評価
        integration_status = phases.get("integration_tests", {}).get("status", "UNKNOWN")
        security_status = phases.get("security_audit", {}).get("status", "UNKNOWN")
        performance_status = phases.get("performance_tests", {}).get("status", "UNKNOWN")
        documentation_status = phases.get("documentation", {}).get("status", "UNKNOWN")
        
        # 必須条件チェック
        critical_pass = integration_status in ["PASS", "PARTIAL"]
        security_pass = security_status in ["PASS", "PARTIAL"]
        performance_pass = performance_status in ["PASS", "PARTIAL"]
        documentation_pass = documentation_status in ["PASS", "PARTIAL"]
        
        # 全体評価
        if all([critical_pass, security_pass, performance_pass, documentation_pass]):
            if all(status == "PASS" for status in [integration_status, security_status, performance_status, documentation_status]):
                return "READY"
            else:
                return "READY_WITH_WARNINGS"
        else:
            return "NOT_READY"
    
    def generate_final_report(self) -> str:
        """最終リリースレポート生成"""
        release_readiness = self.evaluate_release_readiness()
        
        report = f"""# 最終リリース準備レポート

## 概要
- **実行日時**: {self.results['timestamp']}
- **対象システム**: {self.results['target']}
- **リリース準備状況**: {release_readiness}

## 実行フェーズ結果

"""
        
        # 各フェーズの結果を追加
        for phase_name, phase_data in self.results["phases"].items():
            status_icon = {
                "PASS": "✅",
                "PARTIAL": "⚠️",
                "FAIL": "❌",
                "ERROR": "💥",
                "UNKNOWN": "❓"
            }.get(phase_data.get("status", "UNKNOWN"), "❓")
            
            report += f"### {status_icon} {phase_data.get('name', phase_name).upper()}\n"
            report += f"**ステータス**: {phase_data.get('status', 'UNKNOWN')}\n"
            report += f"**実行時間**: {phase_data.get('start_time', 'N/A')} - {phase_data.get('end_time', 'N/A')}\n\n"
            
            if phase_data.get("summary"):
                report += "**サマリー**:\n"
                for key, value in phase_data["summary"].items():
                    report += f"- {key}: {value}\n"
                report += "\n"
        
        # リリース判定
        report += "## リリース判定\n\n"
        
        if release_readiness == "READY":
            report += "✅ **リリース可能**: すべてのテストに合格しました。本番環境へのリリースを推奨します。\n\n"
        elif release_readiness == "READY_WITH_WARNINGS":
            report += "⚠️ **条件付きリリース可能**: 一部警告がありますが、リリース可能です。以下の点にご注意ください：\n\n"
        else:
            report += "❌ **リリース不可**: 重要な問題が検出されました。以下の問題を解決してから再テストしてください：\n\n"
        
        # 推奨事項
        report += "## 推奨事項\n\n"
        
        phases = self.results["phases"]
        
        # 統合テストの推奨事項
        if phases.get("integration_tests", {}).get("status") != "PASS":
            report += "### 統合テスト\n"
            report += "- 失敗したテストケースを確認し、修正してください\n"
            report += "- 依存サービスの接続状況を確認してください\n\n"
        
        # セキュリティの推奨事項
        if phases.get("security_audit", {}).get("status") != "PASS":
            report += "### セキュリティ\n"
            report += "- 検出された脆弱性を修正してください\n"
            report += "- セキュリティヘッダーの設定を見直してください\n"
            report += "- 認証・認可機能を強化してください\n\n"
        
        # パフォーマンスの推奨事項
        if phases.get("performance_tests", {}).get("status") != "PASS":
            report += "### パフォーマンス\n"
            report += "- レスポンス時間の最適化を行ってください\n"
            report += "- データベースクエリを最適化してください\n"
            report += "- キャッシュ戦略を見直してください\n\n"
        
        # ドキュメントの推奨事項
        if phases.get("documentation", {}).get("status") != "PASS":
            report += "### ドキュメント\n"
            report += "- 不足しているドキュメントを作成してください\n"
            report += "- 既存ドキュメントを最新情報に更新してください\n\n"
        
        # 次のステップ
        report += "## 次のステップ\n\n"
        
        if release_readiness == "READY":
            report += "1. 本番環境へのデプロイメント実行\n"
            report += "2. 本番環境での動作確認\n"
            report += "3. ユーザーへのリリース通知\n"
            report += "4. 監視体制の強化\n"
        else:
            report += "1. 検出された問題の修正\n"
            report += "2. 修正後の再テスト実行\n"
            report += "3. リリース準備状況の再評価\n"
        
        report += "\n## 生成されたドキュメント\n\n"
        report += f"- 統合テストレポート: `{self.output_dir}/integration_test_report.md`\n"
        report += f"- セキュリティ監査レポート: `{self.output_dir}/security_audit_report.md`\n"
        report += f"- パフォーマンステストレポート: `{self.output_dir}/performance_test_report.md`\n"
        report += f"- API仕様書: `{self.output_dir}/api_documentation.md`\n"
        report += f"- ユーザーマニュアル: `{self.output_dir}/user_manual_updated.md`\n"
        report += f"- 運用マニュアル: `{self.output_dir}/operations_manual.md`\n"
        report += f"- デプロイメントガイド: `{self.output_dir}/deployment_guide.md`\n"
        report += f"- トラブルシューティングガイド: `{self.output_dir}/troubleshooting_guide.md`\n"
        
        return report
    
    async def run_all_phases(self) -> Dict:
        """全フェーズの実行"""
        logger.info("=== 最終リリース準備開始 ===")
        
        try:
            # フェーズ1: 統合テスト
            phase1_result = await self.phase_1_integration_tests()
            self.results["phases"]["integration_tests"] = phase1_result
            
            # フェーズ2: セキュリティ監査
            phase2_result = await self.phase_2_security_audit()
            self.results["phases"]["security_audit"] = phase2_result
            
            # フェーズ3: パフォーマンステスト
            phase3_result = await self.phase_3_performance_tests()
            self.results["phases"]["performance_tests"] = phase3_result
            
            # フェーズ4: ドキュメント整備
            phase4_result = self.phase_4_documentation()
            self.results["phases"]["documentation"] = phase4_result
            
            # 全体評価
            self.results["release_readiness"] = self.evaluate_release_readiness()
            
            # 最終レポート生成
            final_report = self.generate_final_report()
            report_path = self.output_dir / "final_release_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(final_report)
            
            # JSON結果保存
            json_path = self.output_dir / "final_release_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"=== 最終リリース準備完了: {self.results['release_readiness']} ===")
            
        except Exception as e:
            self.results["overall_status"] = "ERROR"
            self.results["error"] = str(e)
            logger.error(f"最終リリース準備エラー: {e}")
        
        return self.results

async def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="最終リリース準備実行")
    parser.add_argument("--target", default="http://localhost:8080", help="テスト対象URL")
    parser.add_argument("--quick", action="store_true", help="クイックテスト（短時間）")
    
    args = parser.parse_args()
    
    try:
        # 最終リリース準備実行
        preparation = FinalReleasePreparation(args.target)
        
        if args.quick:
            # クイックモード（統合テストとドキュメント整備のみ）
            logger.info("クイックモードで実行...")
            
            phase1_result = await preparation.phase_1_integration_tests()
            preparation.results["phases"]["integration_tests"] = phase1_result
            
            phase4_result = preparation.phase_4_documentation()
            preparation.results["phases"]["documentation"] = phase4_result
            
            preparation.results["release_readiness"] = preparation.evaluate_release_readiness()
        else:
            # フルモード
            await preparation.run_all_phases()
        
        # 結果表示
        print(f"\n=== 最終リリース準備結果 ===")
        print(f"リリース準備状況: {preparation.results['release_readiness']}")
        print(f"レポート出力先: {preparation.output_dir}")
        
        # 終了コード設定
        if preparation.results["release_readiness"] in ["READY", "READY_WITH_WARNINGS"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())