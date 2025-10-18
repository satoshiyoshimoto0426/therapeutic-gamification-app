# ローカルテスト環境セットアップガイド

このガイドでは、治療的ゲーミフィケーションアプリをローカル環境でテストする方法を説明します。開発者が最小限の手動設定で、フルスタックアプリケーションをローカルで起動し、テストできる環境を提供します。

## 📖 目次

- [クイックスタート](#-クイックスタート)
- [前提条件](#-前提条件)
- [詳細なセットアップ手順](#-詳細なセットアップ手順)
- [テストの実行](#-テストの実行)
- [トラブルシューティング](#-トラブルシューティング)
- [サービスアーキテクチャ](#-サービスアーキテクチャ)
- [CLIコマンドリファレンス](#-cliコマンドリファレンス)
- [開発ワークフロー](#-開発ワークフロー)
- [よくある質問](#-よくある質問)

## 🚀 クイックスタート

### 統一CLIを使用する方法（推奨）

```bash
# 1. 環境セットアップ
python local_test_cli.py setup

# 2. サービス起動
python local_test_cli.py start

# 3. ヘルスチェック
python local_test_cli.py health

# 4. ブラウザでアクセス
# http://localhost:3000
```

### 従来の方法

#### 1. セットアップ実行

```bash
python local_test_setup.py
```

このコマンドは以下を自動的に実行します：
- 環境チェック（Python, Node.js, npm, pip）
- Python依存関係のインストール
- フロントエンド依存関係のインストール
- 環境変数ファイル（.env.local）の生成

#### 2. サービス起動

```bash
python start_mvp_services.py
```

以下のサービスが起動します：
- 認証サービス (ポート: 8002)
- コアゲームサービス (ポート: 8001)
- タスク管理サービス (ポート: 8003)
- Mandalaサービス (ポート: 8004)

#### 3. フロントエンド起動

別のターミナルで：

```bash
cd frontend
npm run dev
```

#### 4. ブラウザでアクセス

```
http://localhost:3000
```

## 📋 前提条件

### システム要件

#### 必須ソフトウェア

| ソフトウェア | 最小バージョン | 推奨バージョン | 用途 |
|------------|--------------|--------------|------|
| Python | 3.9 | 3.11以上 | バックエンドサービス |
| Node.js | 16.x | 18.x以上 | フロントエンド開発 |
| npm | 7.x | 9.x以上 | パッケージ管理 |
| pip | 21.x | 最新版 | Python パッケージ管理 |

#### ハードウェア要件

| リソース | 最小 | 推奨 | 備考 |
|---------|------|------|------|
| RAM | 4GB | 8GB以上 | 複数サービス同時起動のため |
| ディスク空き容量 | 2GB | 5GB以上 | 依存関係とログ用 |
| CPU | 2コア | 4コア以上 | 並列処理のため |

#### オペレーティングシステム

- **Windows**: 10以上（PowerShell 5.1以上）
- **macOS**: 10.15 (Catalina)以上
- **Linux**: Ubuntu 20.04以上、または同等のディストリビューション

### インストール確認

以下のコマンドで必要なソフトウェアがインストールされているか確認してください：

```bash
# Python バージョン確認
python --version
# 出力例: Python 3.11.0

# Node.js バージョン確認
node --version
# 出力例: v18.17.0

# npm バージョン確認
npm --version
# 出力例: 9.6.7

# pip バージョン確認
pip --version
# 出力例: pip 23.2.1
```

### 必須ソフトウェアのインストール

#### Windows

```powershell
# Python のインストール（Microsoft Store経由）
winget install Python.Python.3.11

# Node.js のインストール
winget install OpenJS.NodeJS.LTS

# または、公式インストーラーを使用
# Python: https://www.python.org/downloads/
# Node.js: https://nodejs.org/
```

#### macOS

```bash
# Homebrew を使用
brew install python@3.11
brew install node@18

# または、公式インストーラーを使用
# Python: https://www.python.org/downloads/
# Node.js: https://nodejs.org/
```

#### Linux (Ubuntu/Debian)

```bash
# Python のインストール
sudo apt update
sudo apt install python3.11 python3-pip

# Node.js のインストール（NodeSource経由）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### オプションツール

以下のツールは必須ではありませんが、開発体験を向上させます：

- **Git**: バージョン管理（2.30以上推奨）
- **VS Code**: 推奨エディタ（拡張機能: Python, ESLint, Prettier）
- **Postman**: API テスト用
- **Docker**: コンテナ化されたテスト環境用（オプション）

## 🔧 詳細なセットアップ手順

### ステップ1: リポジトリのクローン

```bash
git clone <repository-url>
cd therapeutic-gamification-app
```

### ステップ2: 環境チェック

```bash
python local_test_setup.py
```

環境チェックが失敗した場合は、表示されたメッセージに従って問題を解決してください。

### ステップ3: 手動での依存関係インストール（必要な場合）

#### Python依存関係

```bash
pip install -r requirements.txt
```

#### フロントエンド依存関係

```bash
cd frontend
npm install
cd ..
```

### ステップ4: 環境変数の設定

`.env.local`ファイルが自動生成されます。必要に応じて編集してください：

```bash
# データベース設定
USE_MOCK_DATABASE=true
MOCK_DATABASE_PERSIST=false

# サービスポート設定
AUTH_SERVICE_PORT=8002
CORE_GAME_SERVICE_PORT=8001
TASK_MGMT_SERVICE_PORT=8003

# フロントエンド設定
FRONTEND_PORT=3000
VITE_API_BASE_URL=http://localhost:8001
```

## 🧪 テストの実行

### 統一CLIを使用する方法（推奨）

```bash
# ユニットテスト
python local_test_cli.py test unit -v

# 統合テスト
python local_test_cli.py test integration -v

# E2Eテスト
python local_test_cli.py test e2e -v

# 全テスト実行
python local_test_cli.py test all -v

# カバレッジレポート生成
python local_test_cli.py test coverage
```

### 従来の方法

#### ユニットテスト

```bash
pytest services/ -v
```

#### 特定のサービスのテスト

```bash
pytest services/auth/test_auth.py -v
pytest services/core-game/test_core_game.py -v
```

#### カバレッジ付きテスト

```bash
pytest --cov=services --cov-report=html
```

## 🔍 トラブルシューティング

### ポート競合エラー

エラーメッセージ: `Address already in use`

**解決方法:**

Windows:
```powershell
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

Mac/Linux:
```bash
lsof -ti:8001 | xargs kill -9
```

### Python依存関係のインストール失敗

**解決方法:**

1. pipをアップグレード:
```bash
python -m pip install --upgrade pip
```

2. 仮想環境を使用:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Node.js依存関係のインストール失敗

**解決方法:**

1. npmキャッシュをクリア:
```bash
npm cache clean --force
```

2. node_modulesを削除して再インストール:
```bash
cd frontend
rm -rf node_modules package-lock.json  # Mac/Linux
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

### サービスが起動しない

**確認事項:**

1. ポートが使用されていないか確認
2. 必要なファイルが存在するか確認
3. Python/Node.jsのバージョンを確認
4. ログファイルを確認: `./logs/local_test.log`

### CORS エラー

フロントエンドからAPIにアクセスできない場合：

1. `frontend/vite.config.ts`のプロキシ設定を確認
2. バックエンドサービスのCORS設定を確認
3. ブラウザのコンソールでエラーメッセージを確認

## 📊 サービスアーキテクチャ

```
┌─────────────────────────────────────────────┐
│         Frontend (React + Vite)             │
│              :3000                          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           API Gateway / Proxy               │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────┐
        ▼         ▼         ▼         ▼
    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
    │ Auth │ │ Core │ │ Task │ │Mandala│
    │ :8002│ │ :8001│ │ :8003│ │ :8004│
    └──────┘ └──────┘ └──────┘ └──────┘
        │         │         │         │
        └─────────┴─────────┴─────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  Mock Firestore  │
        │  (In-Memory DB)  │
        └──────────────────┘
```

## 🎯 次のステップ

1. **API ドキュメントの確認**
   - http://localhost:8001/docs (Core Game)
   - http://localhost:8002/docs (Auth)
   - http://localhost:8003/docs (Task Management)

2. **サンプルデータの作成**
   - テストユーザーの作成
   - サンプルタスクの追加

3. **機能テスト**
   - ユーザー登録・ログイン
   - タスク作成・完了
   - XP獲得・レベルアップ

## 🎮 CLI コマンドリファレンス

### 基本コマンド

```bash
# ヘルプ表示
python local_test_cli.py --help

# 環境セットアップ
python local_test_cli.py setup

# 全サービス起動
python local_test_cli.py start

# 個別サービス起動
python local_test_cli.py start --service auth

# サービス停止
python local_test_cli.py stop

# 個別サービス停止
python local_test_cli.py stop --service auth

# サービス再起動
python local_test_cli.py restart auth

# ヘルスチェック
python local_test_cli.py health

# システム状態表示
python local_test_cli.py status
```

### ログ管理

```bash
# ログ表示（最新50行）
python local_test_cli.py logs --service auth

# ログ表示（行数指定）
python local_test_cli.py logs --service auth --lines 100

# ログレベルでフィルタリング
python local_test_cli.py logs --service auth --level ERROR

# リアルタイムログ表示
python local_test_cli.py logs --service auth --follow

# ログをファイルに保存
python local_test_cli.py logs --service auth --save auth.log
```

### テスト実行

```bash
# ユニットテスト
python local_test_cli.py test unit

# 統合テスト
python local_test_cli.py test integration

# E2Eテスト
python local_test_cli.py test e2e

# 全テスト
python local_test_cli.py test all

# カバレッジレポート
python local_test_cli.py test coverage
```

### クリーンアップ

```bash
# 基本クリーンアップ
python local_test_cli.py cleanup

# ログ保存付きクリーンアップ
python local_test_cli.py cleanup --save-logs

# 一時ファイルも削除
python local_test_cli.py cleanup --temp-files

# サービスを停止せずにクリーンアップ
python local_test_cli.py cleanup --keep-services

# データを保持してクリーンアップ
python local_test_cli.py cleanup --keep-data
```

## 🔄 開発ワークフロー

### 日常的な開発フロー

```bash
# 1. 朝の起動
python local_test_cli.py start

# 2. ヘルスチェック
python local_test_cli.py health

# 3. 開発作業
# コードを編集...

# 4. テスト実行
python local_test_cli.py test unit -v

# 5. 統合テスト
python local_test_cli.py test integration -v

# 6. 終了時
python local_test_cli.py stop
```

### 新機能開発フロー

```bash
# 1. 環境セットアップ（初回のみ）
python local_test_cli.py setup

# 2. 必要なサービスのみ起動
python local_test_cli.py start --service auth
python local_test_cli.py start --service core-game

# 3. テストデータの準備
# test_data/sample_data.json を編集

# 4. 開発とテストのサイクル
# - コード編集
# - ユニットテスト実行
# - 統合テスト実行

# 5. 全体テスト
python local_test_cli.py test all

# 6. クリーンアップ
python local_test_cli.py cleanup
```

### デバッグワークフロー

```bash
# 1. 詳細ログを有効化
# .env.local で LOG_LEVEL=DEBUG に設定

# 2. サービスを再起動
python local_test_cli.py restart auth

# 3. リアルタイムログ監視
python local_test_cli.py logs --service auth --follow

# 4. 特定のテストを実行
pytest services/auth/test_auth.py::test_specific_function -v -s

# 5. ログを保存
python local_test_cli.py logs --service auth --save debug_auth.log
```

## ❓ よくある質問

### Q1: セットアップに失敗します

**A:** 以下を確認してください：

1. Python と Node.js のバージョンが要件を満たしているか
2. インターネット接続が安定しているか
3. ディスク容量が十分にあるか
4. ファイアウォールやアンチウイルスがブロックしていないか

詳細なエラーメッセージを確認し、トラブルシューティングセクションを参照してください。

### Q2: サービスが起動しません

**A:** 以下を試してください：

```bash
# ポート使用状況を確認
python local_test_cli.py status

# ログを確認
python local_test_cli.py logs --service <service-name>

# サービスを再起動
python local_test_cli.py restart <service-name>

# 完全なクリーンアップと再起動
python local_test_cli.py cleanup
python local_test_cli.py start
```

### Q3: テストが失敗します

**A:** テスト失敗の一般的な原因：

1. **サービスが起動していない**: `python local_test_cli.py health` で確認
2. **ポート競合**: 他のアプリケーションがポートを使用している
3. **依存関係の問題**: `pip install -r requirements.txt` を再実行
4. **データベースの状態**: モックデータベースをリセット

```bash
# テストデータをリセット
python local_test_cli.py cleanup --keep-services
python local_test_cli.py start
```

### Q4: フロントエンドからAPIにアクセスできません

**A:** CORS設定を確認してください：

1. `frontend/vite.config.ts` のプロキシ設定を確認
2. バックエンドサービスが起動しているか確認
3. ブラウザの開発者ツールでネットワークエラーを確認

```bash
# バックエンドのヘルスチェック
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Q5: メモリ使用量が多すぎます

**A:** 以下の最適化を試してください：

1. **必要なサービスのみ起動**:
```bash
python local_test_cli.py start --service auth --service core-game
```

2. **フロントエンドの開発サーバーを停止**:
```bash
# バックエンドのみでテスト
python local_test_cli.py start --no-frontend
```

3. **ログレベルを下げる**:
```bash
# .env.local で LOG_LEVEL=WARNING に設定
```

### Q6: 本番環境のデータを使いたい

**A:** ローカルテスト環境は本番データを使用しないように設計されています。

安全にテストするには：

1. **サンプルデータを使用**: `test_data/sample_data.json`
2. **モックデータベースを使用**: `USE_MOCK_DATABASE=true`
3. **本番環境の認証情報を使用しない**

本番データが必要な場合は、データをエクスポートして匿名化してください。

### Q7: 複数の開発者で環境を共有できますか？

**A:** ローカル環境は各開発者のマシンで独立して動作します。

チーム開発の推奨事項：

1. **設定ファイルの共有**: `.env.local.template` を使用
2. **サンプルデータの共有**: `test_data/` ディレクトリを Git で管理
3. **ドキュメントの更新**: 環境固有の設定を README に記載

### Q8: CI/CD パイプラインで使用できますか？

**A:** はい、可能です。以下の例を参照してください：

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Setup
        run: python local_test_cli.py setup
      - name: Start services
        run: python local_test_cli.py start --no-frontend
      - name: Run tests
        run: python local_test_cli.py test all
      - name: Cleanup
        run: python local_test_cli.py cleanup
```

## 📚 関連ドキュメント

### 主要ドキュメント

- [メインREADME](README.md) - プロジェクト概要
- [ユーザーマニュアル](THERAPEUTIC_APP_USER_GUIDE.md) - エンドユーザー向けガイド
- [デプロイメントガイド](AWS_DEPLOYMENT_GUIDE.md) - 本番環境へのデプロイ

### 技術ドキュメント

- [トラブルシューティングガイド](TROUBLESHOOTING_GUIDE.md) - 詳細な問題解決方法
- [アーキテクチャドキュメント](ARCHITECTURE.md) - システム設計の詳細
- [API リファレンス](API_REFERENCE.md) - API エンドポイントの詳細

### 完了レポート

- [CLI完了レポート](task_6_completion_report.md) - CLI実装の詳細
- [テストランナー完了レポート](task_5_completion_report.md) - テスト機能の詳細
- [サービスマネージャー完了レポート](task_3_completion_report.md) - サービス管理の詳細

## 🤝 サポート

### 問題が発生した場合

1. **このドキュメントを確認**: トラブルシューティングセクションとFAQ
2. **ログを確認**: `./logs/local_test.log` または `python local_test_cli.py logs`
3. **GitHub Issues**: 既存の問題を検索、または新しい Issue を作成
4. **コミュニティ**: ディスカッションフォーラムで質問

### バグ報告

GitHub Issues で以下の情報を含めて報告してください：

- **環境情報**: OS、Python バージョン、Node.js バージョン
- **再現手順**: 問題を再現する具体的な手順
- **エラーメッセージ**: 完全なエラーログ
- **期待される動作**: 本来どうあるべきか

### 機能リクエスト

新機能の提案は GitHub Discussions で歓迎します。

## 🔒 セキュリティ

### ローカル環境のセキュリティ

- **認証情報**: `.env.local` は Git にコミットしない（`.gitignore` に含まれています）
- **テストデータ**: 個人情報を含まないサンプルデータのみ使用
- **ポート**: ローカルホスト（127.0.0.1）のみにバインド
- **本番環境**: 本番の認証情報やデータは使用しない

### セキュリティ問題の報告

セキュリティ上の問題を発見した場合は、公開 Issue ではなく、プロジェクトメンテナーに直接連絡してください。

## 📝 ライセンス

MIT License

Copyright (c) 2024 Therapeutic Gamification App

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**最終更新**: 2024年10月18日  
**バージョン**: 1.0.0  
**メンテナー**: Therapeutic Gamification App Team
