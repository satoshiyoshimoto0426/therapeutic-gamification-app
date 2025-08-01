# Mandala Service

## 概要

9x9 Mandalaグリッドシステムのセルアンロック機能とAPI実装を提供するサービスです。

## 実装された機能

### コア機能
- **9x9グリッド構造**: 81個のメモリセル（クエスト）を管理
- **中央価値観システム**: ACT療法統合による9つの固定価値観セル
- **段階的アンロック**: 隣接セルベースの進行システム
- **セル完了管理**: XP報酬とタイムスタンプ付き完了処理

### APIエンドポイント

#### 1. GET /mandala/{uid}/grid
Mandalaグリッドの取得
- **応答**: 9x9グリッドデータ、アンロック数、完了率
- **中央価値観**: 9つの固定価値観セルを含む

#### 2. POST /mandala/{uid}/unlock
セルのアンロック
- **要求**: 座標、クエストデータ（タイトル、説明、XP報酬、難易度）
- **検証**: 隣接セル条件、データ整合性、ビジネスルール
- **応答**: アンロック結果、セル情報

#### 3. POST /mandala/{uid}/complete
セルの完了
- **要求**: 座標
- **検証**: セル状態、完了間隔制限
- **応答**: 完了結果、XP獲得、完了時刻

#### 4. GET /mandala/{uid}/reminder
日次価値観リマインダーの取得
- **応答**: ランダムに選択された価値観メッセージ

#### 5. GET /mandala/{uid}/status
Mandalaシステムの状態取得
- **応答**: 進行状況、警告、利用可能アンロック数

#### 6. GET /health
ヘルスチェック
- **応答**: サービス状態

### データモデル

#### MemoryCell (メモリセル)
```python
@dataclass
class MemoryCell:
    cell_id: str
    position: Tuple[int, int]
    status: CellStatus  # LOCKED, UNLOCKED, COMPLETED, CORE_VALUE
    quest_title: str
    quest_description: str
    xp_reward: int
    difficulty: int  # 1-5
    completion_time: Optional[datetime]
    therapeutic_focus: Optional[str]
```

#### CoreValue (中央価値観)
```python
@dataclass
class CoreValue:
    name: str
    description: str
    daily_reminder: str
    position: Tuple[int, int]
    therapeutic_principle: str
```

### バリデーション機能

#### データ検証
- **座標検証**: 0-8範囲の座標
- **難易度検証**: 1-5範囲
- **XP報酬検証**: 1-1000範囲
- **テキスト長制限**: タイトル100文字、説明500文字
- **治療的焦点検証**: 定義済み焦点リストとの照合

#### ビジネスルール
- **日次アンロック制限**: 1日最大3セル
- **完了間隔制限**: 最小1時間間隔
- **段階的進行**: 隣接セル要件
- **孤立セル検出**: 進行パス妥当性検証

### 中央価値観システム (ACT療法統合)

固定配置される9つの価値観セル：

1. **Core Self (4,4)**: 真の自分 - Self-Acceptance
2. **Compassion (3,4)**: 慈悲心 - Self-Compassion  
3. **Growth (5,4)**: 成長 - Growth Mindset
4. **Authenticity (4,3)**: 真正性 - Authentic Living
5. **Connection (4,5)**: つながり - Social Connection
6. **Present Moment (3,3)**: 今この瞬間 - Mindfulness
7. **Values Action (5,5)**: 価値に基づく行動 - Values-Based Action
8. **Acceptance (3,5)**: 受容 - Radical Acceptance
9. **Commitment (5,3)**: コミットメント - Psychological Flexibility

### エラーハンドリング

- **400 Bad Request**: バリデーションエラー、ビジネスルール違反
- **422 Unprocessable Entity**: 入力データ形式エラー
- **429 Too Many Requests**: レート制限超過
- **500 Internal Server Error**: システムエラー

### 治療的配慮

- **ADHD配慮**: 段階的進行、認知負荷軽減
- **治療安全性**: 適切な難易度設定、過度な負荷防止
- **価値観統合**: ACT療法原則に基づく中央価値観
- **進行支援**: 日次リマインダー、進行状況可視化

## 要件対応

### Requirement 4.1: Mandala Chart Integration
✅ 9x9グリッド構造実装
✅ 81個のメモリセル管理
✅ 8属性+中央価値観の構造化

### Requirement 4.3: セルアンロック機能
✅ `/mandala/{uid}/grid` APIエンドポイント
✅ ロック状態管理とJSON応答
✅ 段階的アンロック条件

## 使用技術

- **FastAPI**: REST API実装
- **Pydantic**: データバリデーション
- **Python Dataclasses**: データモデル
- **Datetime**: タイムスタンプ管理

## テスト

- **統合テスト**: `test_mandala_api.py`
- **バリデーションテスト**: 各種エラーケース
- **実装検証**: `validate_implementation.py`

## 次のステップ

1. Firestoreデータ永続化統合
2. 認証ミドルウェア統合
3. パフォーマンス最適化
4. 本番環境デプロイ設定