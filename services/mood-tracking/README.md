# 気分追跡サービス (Mood Tracking Service)

治療的ゲーミフィケーションアプリの気分追跡マイクロサービスです。日次の気分ログ、XP乗数用の係数計算、気分履歴とトレンド分析を提供します。

## 機能概要

### 主要機能
- **日次気分ログ**: 1-5スケールでの気分記録
- **係数計算**: XP乗数用の気分係数（0.8-1.2範囲）
- **履歴追跡**: 気分の履歴とトレンド分析
- **CRUD API**: 気分データの作成・読取・更新・削除

### 治療的配慮
- ADHD特性を考慮した簡潔なインターフェース
- トレンド分析による継続的なモニタリング
- 極端な気分変動の検出と適切な係数調整

## API エンドポイント

### 気分ログ作成
```http
POST /mood
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "mood_score": 4,
  "notes": "良い一日でした",
  "context_tags": ["work", "exercise"]
}
```

### 今日の気分取得
```http
GET /mood/today
Authorization: Bearer <JWT_TOKEN>
```

### 気分履歴取得
```http
GET /mood/history?days=30
Authorization: Bearer <JWT_TOKEN>
```

### 気分トレンド分析
```http
GET /mood/trend?days=30
Authorization: Bearer <JWT_TOKEN>
```

### 現在の係数取得
```http
GET /mood/coefficient
Authorization: Bearer <JWT_TOKEN>
```

## 気分係数計算

### 基本計算式
```
基本係数 = 0.6 + (気分スコア × 0.1)
```

| 気分スコア | 基本係数 | 意味 |
|-----------|----------|------|
| 1 | 0.8 | 最低気分 |
| 2 | 0.9 | 低い気分 |
| 3 | 1.0 | 普通の気分 |
| 4 | 1.1 | 良い気分 |
| 5 | 1.2 | 最高の気分 |

### トレンド調整
- 過去3日間の気分スコアから傾向を分析
- 改善傾向: +0.05の調整
- 悪化傾向: -0.05の調整
- 最終係数は0.8-1.2の範囲内に制限

## トレンド分析

### 分析アルゴリズム
線形回帰の傾きを使用してトレンドを判定：
- **improving**: 傾き > 0.1（改善傾向）
- **stable**: -0.1 ≤ 傾き ≤ 0.1（安定）
- **declining**: 傾き < -0.1（悪化傾向）

### 統計情報
- 平均気分スコア
- 平均係数
- 気分分布（1-5の各スコアの出現回数）
- 総ログ数

## データモデル

### MoodLog
```python
{
  "uid": "user_id",
  "log_date": "2024-01-15T00:00:00Z",
  "mood_score": 4,
  "notes": "良い一日でした",
  "context_tags": ["work", "exercise"],
  "calculated_coefficient": 1.1
}
```

### MoodTrend
```python
{
  "uid": "user_id",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "average_mood": 3.2,
  "mood_trend": "improving",
  "coefficient_average": 1.02,
  "total_logs": 25,
  "mood_distribution": {
    "1": 2, "2": 5, "3": 8, "4": 7, "5": 3
  }
}
```

## セットアップと実行

### 依存関係
```bash
pip install fastapi uvicorn pydantic google-cloud-firestore
```

### 環境変数
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export JWT_SECRET_KEY="your-jwt-secret"
```

### サービス起動
```bash
python main.py
```

サービスは `http://localhost:8003` で起動します。

### ヘルスチェック
```bash
curl http://localhost:8003/health
```

## テスト実行

### ユニットテスト
```bash
python -m pytest test_mood_tracking.py -v
```

### 実装検証
```bash
python validate_implementation.py
```

## 治療的安全性

### 低気分の継続監視
- 気分スコア1-2が3日以上続く場合の検出
- 係数が極端に低くなりすぎないよう調整
- トレンド分析による早期警告

### プライバシー保護
- 個人の気分データは暗号化して保存
- アクセス制御による適切な権限管理
- ガーディアンポータルでの監視機能

## 統合について

### 他サービスとの連携
- **Core Game Engine**: XP計算時の係数提供
- **Task Management**: タスク完了時の気分影響分析
- **AI Story Engine**: ストーリー生成時の気分考慮
- **Guardian Portal**: 気分トレンドの監視レポート

### イベント通知
気分の大きな変動や継続的な低気分を検出した場合、適切なサービスに通知を送信します。

## パフォーマンス

### レスポンス時間目標
- 気分ログ作成: < 500ms
- 履歴取得: < 800ms
- トレンド分析: < 1.2s

### スケーラビリティ
- Firestore の自動スケーリング
- ステートレス設計による水平スケーリング対応
- Redis キャッシュによる高速化（将来実装予定）

## 監視とログ

### メトリクス
- API レスポンス時間
- 気分ログ作成頻度
- 係数計算の分布
- エラー率

### アラート
- 連続する低気分の検出
- API エラー率の上昇
- レスポンス時間の悪化

## 今後の拡張予定

- [ ] 気分予測機能（機械学習）
- [ ] コンテキストタグの自動提案
- [ ] 気分と天気・季節の相関分析
- [ ] リアルタイム気分変動アラート
- [ ] 気分日記の自動要約機能