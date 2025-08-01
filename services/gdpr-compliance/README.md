# GDPR準拠システム

このモジュールは、GDPR（一般データ保護規則）に準拠した包括的な個人情報管理とプライバシー保護システムを提供します。

## 概要

治療的ゲーミフィケーションアプリケーションにおいて、ユーザーの個人情報とプライバシーを最高レベルで保護するため、GDPR第1条から第99条までの要件に準拠したシステムを実装しています。

## 主要機能

### 1. 個人情報管理とプライバシー保護 (`privacy_protection_system.py`)

- **データ分類システム**: 6つのカテゴリによる個人情報の自動分類
- **同意管理**: 明示的同意の取得、管理、撤回機能
- **データ最小化**: 処理目的に応じた必要最小限のデータ処理
- **匿名化機能**: 分析用データの自動匿名化
- **保存期間管理**: データカテゴリ別の自動保存期間チェック

### 2. プライバシーバイデザイン (`privacy_by_design.py`)

- **7つの基本原則**: プライバシーバイデザインの完全実装
- **4段階のプライバシーレベル**: ユーザーのニーズに応じた柔軟な設定
- **自動プライバシー制御**: データフロー各段階での自動保護
- **ユーザー設定可能制御**: ユーザーが管理できるプライバシー設定

### 3. 同意管理システム (`consent_management.py`)

- **年齢確認機能**: 13歳未満、13-17歳、18歳以上の自動判定
- **保護者同意**: 未成年者に対する保護者同意システム
- **同意履歴管理**: 全ての同意・撤回の完全な履歴追跡
- **一括オプトアウト**: 全ての同意からの一括撤回機能

### 4. データ主体の権利行使支援 (`data_subject_rights.py`)

GDPR第12-22条に準拠した7つの権利を完全サポート：

- **第15条 アクセス権**: 個人データへの完全なアクセス提供
- **第16条 訂正権**: 不正確なデータの訂正機能
- **第17条 削除権**: 忘れられる権利の実装
- **第18条 処理制限権**: データ処理の制限機能
- **第19条 通知義務**: 第三者への変更通知
- **第20条 ポータビリティ権**: 構造化されたデータ提供
- **第21条 異議申立権**: 処理への異議申立機能

### 5. データポータビリティ (`data_portability.py`)

- **多形式エクスポート**: JSON、CSV、XML、YAML形式対応
- **データ整合性保証**: チェックサムによる完全性検証
- **圧縮機能**: 大容量データの効率的な転送
- **直接転送**: 他サービスへの直接データ転送（準備中）

### 6. 監査ログとコンプライアンス監視 (`audit_logging.py`)

- **包括的監査ログ**: 全ての個人情報アクセスを記録
- **自動コンプライアンス監視**: 6つの主要ルールの継続監視
- **違反検出とアラート**: リアルタイムでの違反検出
- **DPIA支援**: データ保護影響評価の自動化支援

## データ分類

システムは以下の6つのカテゴリで個人情報を分類します：

| カテゴリ | 機密レベル | 保存期間 | 匿名化可能 |
|---------|-----------|---------|-----------|
| 基本プロファイル | 2 | 7年 | ✓ |
| 治療データ | 5 | 10年 | ✗ |
| 行動データ | 3 | 3年 | ✓ |
| 生体データ | 5 | 1年 | ✗ |
| 位置情報 | 4 | 3ヶ月 | ✓ |
| コミュニケーション | 3 | 3年 | ✓ |

## 使用方法

### 基本的な使用例

```python
from services.gdpr_compliance.main import GDPRComplianceSystem
from services.gdpr_compliance.privacy_by_design import PrivacyLevel
from datetime import datetime, timedelta

# システムの初期化
gdpr_system = GDPRComplianceSystem()

# ユーザー登録
user_id = "user_001"
birth_date = datetime.now() - timedelta(days=25*365)  # 25歳

result = gdpr_system.register_user(
    user_id, 
    birth_date, 
    PrivacyLevel.ENHANCED
)

# 同意要求
consent_result = gdpr_system.request_consent(
    user_id, 
    "therapeutic_data", 
    "therapeutic_support"
)

# 権利行使
rights_result = gdpr_system.exercise_data_subject_right(
    user_id, 
    "access", 
    "自分のデータにアクセスしたい"
)

# データエクスポート
export_result = gdpr_system.export_personal_data(
    user_id, 
    "json", 
    "all_data"
)
```

### 管理者向け機能

```python
# コンプライアンスチェック
compliance_result = gdpr_system.run_compliance_check()

# コンプライアンスダッシュボード
dashboard = gdpr_system.get_compliance_dashboard()

# 監査ログエクスポート
audit_logs = gdpr_system.export_audit_logs(
    start_date=datetime.now() - timedelta(days=30),
    format="json"
)

# DPIA必要性評価
dpia_assessment = gdpr_system.assess_dpia_necessity({
    "automated_decision_making": True,
    "sensitive_data": True,
    "vulnerable_individuals": True
})
```

## API エンドポイント

### ユーザー向けAPI

- `POST /gdpr/register` - ユーザー登録
- `POST /gdpr/consent` - 同意要求
- `POST /gdpr/rights` - 権利行使要求
- `GET /gdpr/export` - データエクスポート
- `GET /gdpr/dashboard` - プライバシーダッシュボード

### 管理者向けAPI

- `POST /gdpr/admin/compliance-check` - コンプライアンスチェック
- `GET /gdpr/admin/dashboard` - 管理ダッシュボード
- `GET /gdpr/admin/audit-logs` - 監査ログ取得
- `POST /gdpr/admin/dpia-assessment` - DPIA評価

## コンプライアンス監視

システムは以下の6つの主要ルールを継続的に監視します：

1. **データ保存期間チェック** (第5条)
2. **同意有効性チェック** (第7条)
3. **アクセス制御チェック** (第32条)
4. **権利行使応答時間チェック** (第12条)
5. **データ侵害通知チェック** (第33-34条)
6. **プライバシーバイデザインチェック** (第25条)

## テスト

### 単体テスト実行

```bash
# 全テストの実行
python -m pytest services/gdpr-compliance/test_*.py -v

# 特定モジュールのテスト
python -m pytest services/gdpr-compliance/test_privacy_protection.py -v
python -m pytest services/gdpr-compliance/test_data_subject_rights_integration.py -v
python -m pytest services/gdpr-compliance/test_compliance_monitoring_integration.py -v
```

### 統合テスト実行

```bash
# メインシステムのテスト
python services/gdpr-compliance/main.py
```

## セキュリティ考慮事項

- **暗号化**: 保存時・転送時の両方でAES-256-GCM暗号化
- **アクセス制御**: RBAC（役割ベースアクセス制御）による厳格な権限管理
- **監査ログ**: 全ての個人情報アクセスの完全な記録
- **データ最小化**: 処理目的に必要な最小限のデータのみ処理
- **匿名化**: 分析用データの自動匿名化

## パフォーマンス

- **応答時間**: 権利行使要求への30日以内の応答保証
- **データ処理**: 大容量データの効率的な処理とエクスポート
- **監査ログ**: 7年間の監査ログ保持と高速検索
- **コンプライアンス監視**: 24時間間隔での自動監視

## 法的準拠

このシステムは以下の法規制に準拠しています：

- **GDPR** (EU一般データ保護規則)
- **個人情報保護法** (日本)
- **JIS X 8341-3 AAA** (アクセシビリティ)
- **WCAG 2.2 AA** (ウェブアクセシビリティ)

## ライセンス

このソフトウェアは治療的ゲーミフィケーションアプリケーション専用として開発されており、
適切なライセンス条項の下で使用されます。

## サポート

技術的な質問やサポートが必要な場合は、以下にお問い合わせください：

- **プライバシー担当**: privacy@therapeutic-app.com
- **データ保護責任者**: dpo@therapeutic-app.com
- **技術サポート**: tech-support@therapeutic-app.com

## 更新履歴

- **v1.0.0** (2024-01-01): 初回リリース
  - 基本的なGDPR準拠機能の実装
  - プライバシーバイデザインの実装
  - データ主体の権利行使支援
  - 監査ログとコンプライアンス監視

---

**注意**: このシステムは治療データを扱うため、最高レベルのセキュリティとプライバシー保護を提供します。本番環境での使用前に、必ず法務・コンプライアンス部門による確認を受けてください。