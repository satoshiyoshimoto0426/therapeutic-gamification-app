# グルノート（Growth Note）システム

日次振り返りとグルノートシステムの実装です。治療的ゲーミフィケーションアプリケーションの一部として、ユーザーの自己理解と成長を支援します。

## 概要

グルノートシステムは以下の4つのカテゴリによる構造化振り返りを提供します：

1. **現実世界で困っていること** - 現在の課題や悩みの認識
2. **理想的な世界とは** - 目標や理想状態の明確化
3. **理想的な世界に住むあなたの感情は？** - 理想実現時の感情の具体化
4. **明日から何が出来る？** - 具体的な行動計画の策定

## 主要機能

### 1. 構造化振り返りシステム (`main.py`)

- **コンテキスト適応型プロンプト生成**: ユーザーの気分、タスク完了状況に基づいてパーソナライズされたプロンプトを生成
- **感情分析**: 振り返り内容から感情トーンを自動分析（5段階評価）
- **問題テーマ抽出**: 6つのカテゴリ（社会、仕事・学習、健康、メンタル、時間、モチベーション）から問題テーマを特定
- **行動指向性分析**: 明日の行動計画の具体性と実行可能性を3段階で評価
- **XP計算**: 振り返りの質に基づいて25-50 XPを付与

### 2. LINE Bot統合 (`line_bot_integration.py`)

- **22:00自動配信**: 毎日22:00に振り返りプロンプトを自動配信
- **Flexメッセージ**: モバイル最適化されたカルーセル形式の入力フォーム
- **段階的入力**: 4つのカテゴリを順次入力する使いやすいUI
- **進捗表示**: リアルタイムで入力進捗を表示
- **完了時XP表示**: 振り返り完了時に獲得XPと分析結果を表示

### 3. 継続支援システム (`reflection_continuity_system.py`)

- **ストリーク管理**: 連続振り返り日数の追跡と記録
- **マイルストーン報酬**: 3日、7日、21日、100日などの節目でボーナスXP付与
- **3段階リマインダー**: スキップ日数に応じて優しい→励まし→やる気向上のメッセージ
- **ストーリーパーソナライゼーション**: 振り返りデータをAIストーリー生成に活用
- **成長領域特定**: 問題テーマから個人の成長領域を自動特定

## アーキテクチャ

```
GrowthNoteSystem (コア)
├── ReflectionLINEInterface (UI層)
└── ReflectionContinuitySystem (継続支援)
```

### データフロー

1. **プロンプト生成**: ユーザーコンテキスト → パーソナライズされたプロンプト
2. **振り返り実行**: LINE Bot UI → 4カテゴリの段階的入力
3. **分析処理**: 入力データ → 感情分析・テーマ抽出・行動分析
4. **XP計算**: 分析結果 → 質に基づくXP付与（25-50 XP）
5. **ストリーク更新**: 完了状況 → 連続日数・マイルストーン管理
6. **パーソナライゼーション**: 分析データ → ストーリー生成用コンテキスト

## 主要クラス

### `GrowthNoteSystem`
- 振り返りプロンプト生成
- 感情分析・テーマ抽出
- XP計算

### `ReflectionLINEInterface`
- LINE Bot UI生成
- セッション管理
- 入力処理

### `ReflectionContinuitySystem`
- ストリーク管理
- リマインダー生成
- ストーリーパーソナライゼーション

## 使用例

```python
from main import GrowthNoteSystem
from line_bot_integration import ReflectionLINEInterface
from reflection_continuity_system import ReflectionContinuitySystem

# システム初期化
growth_note_system = GrowthNoteSystem()
line_interface = ReflectionLINEInterface(growth_note_system)
continuity_system = ReflectionContinuitySystem(growth_note_system)

# 振り返りプロンプト生成
user_context = {"mood": 3, "completed_tasks": 4}
prompt_message = line_interface.create_reflection_prompt_message("user123", user_context)

# 振り返り処理
responses = {
    "current_problems": "人間関係で悩んでいる",
    "ideal_world": "友達と楽しく過ごせる環境",
    "ideal_emotions": "幸せで安心している",
    "tomorrow_actions": "明日は同僚に挨拶をする"
}

for field, response in responses.items():
    line_interface.process_reflection_input("user123", field, response)

# ストリーク更新
streak_result = continuity_system.update_reflection_streak("user123", True)
```

## テスト

```bash
# 単体テスト
python -m pytest services/growth-note/test_growth_note_system.py -v
python -m pytest services/growth-note/test_line_bot_integration.py -v
python -m pytest services/growth-note/test_reflection_continuity_system.py -v

# 統合テスト
python -m pytest services/growth-note/test_integration.py -v

# 全テスト実行
python -m pytest services/growth-note/ -v
```

## 設定可能な要素

### マイルストーン報酬
```python
milestone_rewards = {
    3: {"xp": 50, "message": "3日連続振り返り達成！"},
    7: {"xp": 100, "message": "1週間連続達成！"},
    21: {"xp": 300, "message": "3週間連続達成！習慣化の第一段階をクリア！"},
    100: {"xp": 1500, "message": "100日連続達成！真の習慣マスター！"}
}
```

### リマインダーメッセージ
- **優しいリマインダー** (2-3日スキップ): 無理をしない範囲での参加を促す
- **励ましのリマインダー** (4-7日スキップ): 成長の価値を伝えて動機づけ
- **やる気向上リマインダー** (8日以上スキップ): 継続の力を強調して再開を促す

## 治療的配慮

- **ADHD配慮**: シンプルな4カテゴリ構造、段階的入力
- **認知負荷軽減**: 一度に1つのカテゴリのみ表示
- **感情的安全性**: 優しいトーンのメッセージ、強制しない設計
- **自己効力感向上**: 小さな成功の積み重ね、マイルストーン報酬

## 今後の拡張予定

- [ ] 音声入力対応
- [ ] 画像・写真添付機能
- [ ] グループ振り返り機能
- [ ] AIによる振り返り内容の要約
- [ ] 長期的な成長トレンド分析
- [ ] カスタムプロンプト機能

## 要件対応

このシステムは以下の要件を満たしています：

- **要件15.1**: 22:00の自動振り返りプロンプト配信
- **要件15.2**: 4つのカテゴリによる構造化振り返り
- **要件15.3**: 振り返り完了時のXP付与（25 XP）
- **要件15.4**: 振り返りストリーク管理システム
- **要件15.5**: 2日連続スキップ時の優しいリマインダー機能

## ライセンス

このプロジェクトは治療的ゲーミフィケーションアプリケーションの一部として開発されています。