# 🎯 API使用ガイド

このガイドでは、検出されたAPIエンドポイントの使用方法を説明します。

## 📊 検出結果サマリー

- **総エンドポイント数**: 27
- **動作中**: 10 (36.9%)
- **データ必要**: 11 (40.7%)
- **利用可能**: 21 (77.8%)

## ✅ すぐに使えるエンドポイント

### Core Game サービス (localhost:8001)

#### 1. レベル進捗取得
```bash
curl -X POST http://localhost:8001/level/progress \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user"}'
```

#### 2. 共鳴チェック
```bash
curl -X POST http://localhost:8001/resonance/check \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user", "force_check": false}'
```

#### 3. システム状態取得
```bash
curl -X POST http://localhost:8001/system/status \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user"}'
```

### Task Management サービス (localhost:8003)

#### 1. タスク一覧取得
```bash
curl -X GET http://localhost:8003/tasks/test_user
```

#### 2. 統計取得
```bash
curl -X GET http://localhost:8003/tasks/test_user/statistics
```

### Mandala サービス (localhost:8004)

#### 1. リマインダー取得
```bash
curl -X GET http://localhost:8004/mandala/test_user/reminder
```

## ⚠️ 有効なデータが必要なエンドポイント

これらのエンドポイントは実装されていますが、正しいデータ形式が必要です。

### Core Game サービス

#### XP追加
```bash
curl -X POST http://localhost:8001/xp/add \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "test_user",
    "xp_amount": 100,
    "source": "task_completion"
  }'
```

### Task Management サービス

#### タスク作成
```bash
curl -X POST http://localhost:8003/tasks/test_user/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "one_shot",
    "difficulty": 3,
    "description": "テストタスク",
    "estimated_duration": 30
  }'
```

#### タスク完了
```bash
curl -X POST http://localhost:8003/tasks/test_user/TASK_ID/complete \
  -H "Content-Type: application/json" \
  -d '{
    "mood_at_completion": 4,
    "actual_duration": 25
  }'
```

### Mandala サービス

#### セルアンロック
```bash
curl -X POST http://localhost:8004/mandala/test_user/unlock \
  -H "Content-Type: application/json" \
  -d '{
    "x": 1,
    "y": 1,
    "quest_data": {
      "title": "テストクエスト",
      "description": "説明",
      "xp_reward": 50
    }
  }'
```

## 🔥 エラーが発生するエンドポイント

以下のエンドポイントはサーバーエラー(500)が発生します：

### Mandala サービス

- `GET /mandala/{uid}/grid` - グリッド取得
- `GET /mandala/{uid}/status` - ステータス取得

**原因**: データベース接続またはデータ構造の問題の可能性

**対処方法**:
1. サービスのログを確認
2. モックデータベースの初期化を確認
3. データ構造の検証

## 🎮 実用的なテストシナリオ

### シナリオ1: ユーザーの現在状態を確認

```bash
# 1. システム状態取得
curl -X POST http://localhost:8001/system/status \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user"}'

# 2. レベル進捗確認
curl -X POST http://localhost:8001/level/progress \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user"}'

# 3. タスク一覧取得
curl -X GET http://localhost:8003/tasks/test_user
```

### シナリオ2: タスク完了フロー

```bash
# 1. タスク作成
curl -X POST http://localhost:8003/tasks/test_user/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "one_shot",
    "difficulty": 3,
    "description": "朝の運動",
    "estimated_duration": 30
  }'

# 2. タスク完了（task_idは作成時のレスポンスから取得）
curl -X POST http://localhost:8003/tasks/test_user/TASK_ID/complete \
  -H "Content-Type: application/json" \
  -d '{
    "mood_at_completion": 4,
    "actual_duration": 25
  }'

# 3. XP追加
curl -X POST http://localhost:8001/xp/add \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "test_user",
    "xp_amount": 50,
    "source": "task_completion"
  }'

# 4. 新しいレベル確認
curl -X POST http://localhost:8001/level/progress \
  -H "Content-Type: application/json" \
  -d '{"uid": "test_user"}'
```

## 🐍 Pythonでの使用例

```python
import requests

BASE_URL_CORE = "http://localhost:8001"
BASE_URL_TASK = "http://localhost:8003"

# システム状態取得
response = requests.post(
    f"{BASE_URL_CORE}/system/status",
    json={"uid": "test_user"}
)
print(response.json())

# タスク一覧取得
response = requests.get(f"{BASE_URL_TASK}/tasks/test_user")
print(response.json())

# XP追加
response = requests.post(
    f"{BASE_URL_CORE}/xp/add",
    json={
        "uid": "test_user",
        "xp_amount": 100,
        "source": "test"
    }
)
print(response.json())
```

## 📝 次のステップ

1. **エラーの修正**
   - Mandalaサービスのサーバーエラーを修正
   - 未実装のエンドポイントを実装

2. **テストの拡充**
   - 各エンドポイントの詳細なテスト
   - エラーケースのテスト

3. **ドキュメントの更新**
   - 各エンドポイントのリクエスト/レスポンス形式を文書化
   - エラーコードと対処方法を追加

## 🔗 関連ドキュメント

- [API_ENDPOINTS_REPORT.md](API_ENDPOINTS_REPORT.md) - 詳細な検出レポート
- [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) - テスト結果
- [README_LOCAL_TEST.md](README_LOCAL_TEST.md) - ローカルテスト環境ガイド
