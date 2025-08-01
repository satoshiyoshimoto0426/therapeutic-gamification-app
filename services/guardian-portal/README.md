# Guardian Portal Service

保護者・支援者向けポータルサービス。SAML/Magic Link認証、週次PDFレポート生成、ケアポイントシステムを提供します。

## 機能概要

### 1. Guardian認証システム
- **Magic Link認証**: メールアドレスベースのパスワードレス認証
- **SAML認証**: 企業向けシングルサインオン対応
- **JWT トークン管理**: セキュアなセッション管理
- **RBAC権限管理**: 3段階の権限レベル（view-only, task-edit, chat-send）

### 2. 週次PDFレポート生成
- **自動レポート生成**: ユーザーの週次進捗を詳細にレポート化
- **日本語対応**: 完全日本語対応のPDFレポート
- **カスタマイズ可能**: Guardian向けの個別メモ機能
- **ダウンロード機能**: セキュアなレポートダウンロード

### 3. ケアポイントシステム
- **企業向け購入**: Stripe統合による安全な決済処理
- **大口割引**: 購入金額に応じた段階的割引
- **ポイント配布**: 企業からユーザーへのケアポイント転送
- **ADHD医療文書割引**: 医療文書による50%割引適用

## API エンドポイント

### 認証関連
```
POST /auth/magic-link     # Magic Link生成
GET  /auth/magic          # Magic Link検証
POST /auth/saml           # SAML認証
```

### ダッシュボード
```
GET  /dashboard                    # Guardian ダッシュボード
GET  /users/{user_id}/progress     # ユーザー進捗詳細
```

### レポート生成
```
GET  /reports/weekly/{user_id}     # 週次レポート生成
GET  /reports/download/{filename}  # レポートダウンロード
```

### ケアポイント
```
POST /care-points/corporate/purchase    # 企業向け購入
POST /care-points/corporate/confirm     # 購入確認
POST /care-points/transfer              # ポイント配布
GET  /care-points/balance/{entity_id}   # 残高確認
GET  /care-points/transactions/{entity_id} # 履歴確認
```

### ADHD割引
```
POST /care-points/adhd/verify-document    # 医療文書検証
POST /care-points/adhd/apply-discount     # 割引適用
GET  /care-points/adhd/eligibility/{user_id} # 資格確認
```

## 権限レベル

### view-only
- レポート閲覧
- 進捗確認
- 残高・履歴確認

### task-edit
- view-only の全権限
- タスク編集・割り当て
- ケアポイント購入・配布

### chat-send
- task-edit の全権限
- メッセージ送信
- 緊急連絡
- 医療文書検証

## 使用技術

- **FastAPI**: Web フレームワーク
- **JWT**: 認証トークン管理
- **ReportLab**: PDF生成
- **Stripe**: 決済処理
- **Pydantic**: データバリデーション

## セットアップ

### 依存関係インストール
```bash
pip install fastapi uvicorn jwt pydantic stripe reportlab matplotlib
```

### 環境変数設定
```bash
export STRIPE_SECRET_KEY="your_stripe_secret_key"
export JWT_SECRET_KEY="your_jwt_secret_key"
export GUARDIAN_SAML_CERT="your_saml_certificate"
```

### サービス起動
```bash
python main.py
```

サービスは `http://localhost:8007` で起動します。

## テスト実行

### 認証機能テスト
```bash
python test_guardian_auth.py
```

### ケアポイントシステムテスト
```bash
python test_care_points_integration.py
```

### 全テスト実行
```bash
pytest services/guardian-portal/ -v
```

## 設計思想

### セキュリティファースト
- 全APIエンドポイントで認証必須
- 権限ベースアクセス制御（RBAC）
- JWTトークンによるセキュアなセッション管理

### 治療的配慮
- Guardian の心理的負担軽減
- 分かりやすいレポート形式
- 適切な権限分離による安全性確保

### スケーラビリティ
- マイクロサービス設計
- 非同期処理対応
- キャッシュ機能統合

## データモデル

### GuardianProfile
```python
{
    "guardian_id": "guardian_001",
    "name": "田中花子",
    "email": "guardian@example.com",
    "relationship": "parent",
    "managed_users": ["user_001", "user_002"],
    "permission_level": "chat-send"
}
```

### WeeklyReport
```python
{
    "user_id": "user_001",
    "week_start": "2024-01-15",
    "total_tasks_completed": 28,
    "total_xp_earned": 1740,
    "mood_average": 3.8,
    "crystal_progress": {...},
    "recommendations": [...]
}
```

### CarePointTransaction
```python
{
    "transaction_id": "tx_001",
    "from_entity": "corp_001",
    "to_user": "user_001",
    "points": 500,
    "transaction_type": "transfer",
    "created_at": "2024-01-20T10:30:00Z"
}
```

## 今後の拡張予定

- [ ] リアルタイム通知機能
- [ ] 多言語対応
- [ ] モバイルアプリ連携
- [ ] 高度な分析機能
- [ ] 機械学習による推奨システム

## ライセンス

このプロジェクトは治療的ゲーミフィケーションアプリケーションの一部として開発されています。