# KPI Dashboard Service

治療ゲーミフィケーションアプリのデータ駆動型治療効果監視システム

## 概要

KPIダッシュボードサービスは、ブラッシュアップ資料で定義された重要指標を監視し、治療効果とビジネス成果を可視化するシステムです。

## 主要機能

### 1. 重要指標監視
- **D1リテンション率**: 45%目標（登録翌日ログイン率）
- **7日継続率**: 25%目標（ACTION状態以上到達率）
- **21日習慣化達成率**: 12%目標（HABITUATION状態到達率）
- **ARPMAU**: ¥350目標（月間平均収益）

### 2. 治療効果指標
- 平均自己効力感向上度
- CBT介入エンゲージメント率
- 安全性インシデント率

### 3. エンゲージメント指標
- 日次アクティブユーザー数
- ユーザー状態遷移率
- セッション継続率

### 4. アラートシステム
- 閾値ベースアラート
- 目標値乖離アラート
- トレンド異常検知

## API エンドポイント

### ダッシュボード
```
GET /kpi/dashboard
```
重要指標のサマリーと健康度スコアを取得

### メトリクス管理
```
GET /kpi/metrics
GET /kpi/metrics/{metric_id}
POST /kpi/calculate
```

### アラート管理
```
GET /kpi/alerts
POST /kpi/alerts/{alert_id}/resolve
```

### システム監視
```
GET /kpi/health
```

## データモデル

### KPIMetric
```python
class KPIMetric(BaseModel):
    metric_id: str
    name: str
    description: str
    metric_type: KPIMetricType
    current_value: float
    target_value: float
    unit: str
    trend: str
    last_updated: datetime
    alert_threshold: Optional[float]
    is_critical: bool
```

### UserEngagementData
```python
class UserEngagementData(BaseModel):
    user_id: str
    registration_date: date
    last_login_date: Optional[date]
    current_state: UserState
    consecutive_days: int
    total_sessions: int
    total_xp: int
    revenue_generated: float
    therapeutic_progress: Dict[str, float]
    safety_incidents: int
```

## 使用方法

### サービス起動
```bash
cd services/kpi-dashboard
python main.py
```

### テスト実行
```bash
python -m pytest test_kpi_dashboard.py -v
```

### API使用例

#### ダッシュボードサマリー取得
```bash
curl http://localhost:8000/kpi/dashboard
```

#### 特定メトリクス詳細取得
```bash
curl http://localhost:8000/kpi/metrics/d1_retention
```

#### KPI計算実行
```bash
curl -X POST http://localhost:8000/kpi/calculate
```

## 設定

### 目標値設定
```python
target_values = {
    "d1_retention": 0.45,      # 45%
    "d7_continuation_rate": 0.25,  # 25%
    "d21_habituation_rate": 0.12,  # 12%
    "arpmau": 350.0            # ¥350
}
```

### アラート閾値
- D1リテンション: 35%以下で警告
- 7日継続率: 18%以下で警告
- 21日習慣化率: 8%以下で警告
- ARPMAU: ¥250以下で警告

## 監視項目

### 健康度スコア
重要指標の目標達成率に基づく総合スコア（0-1）
- 0.8以上: 健康
- 0.6-0.8: 警告
- 0.6未満: 危険

### トレンド分析
- 過去7日間の平均値比較
- 変化率5%以上で改善/悪化判定
- 履歴データは30日間保持

## 統合

### 他サービスとの連携
- **認証サービス**: ユーザー登録・ログイン情報
- **タスク管理**: タスク完了・XP獲得データ
- **気分追跡**: 治療効果指標
- **Guardian Portal**: 収益データ

### データソース
- Firestore: ユーザープロファイル、セッション履歴
- BigQuery: 集計データ、履歴分析
- Cloud Monitoring: システムメトリクス

## 治療的価値

### エビデンスベース監視
- 行動変容の5段階（APATHY → HABITUATION）追跡
- CBT介入効果の定量化
- 自己効力感向上の測定

### 安全性保証
- インシデント率監視
- 治療的安全性の継続確認
- アラートによる早期介入

### 継続的改善
- データ駆動型意思決定支援
- A/Bテスト結果の定量評価
- 治療効果最適化のための洞察提供

## 今後の拡張

1. **予測分析**: 機械学習による離脱予測
2. **セグメント分析**: ユーザー群別KPI比較
3. **リアルタイム監視**: ストリーミングデータ処理
4. **カスタムダッシュボード**: 役割別表示カスタマイズ
5. **外部連携**: Slack/Teams通知、レポート自動生成