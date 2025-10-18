# トラブルシューティングガイド

このガイドでは、ローカルテスト環境で発生する可能性のある問題と、その解決方法を説明します。

## 📖 目次

- [環境セットアップの問題](#環境セットアップの問題)
- [サービス起動の問題](#サービス起動の問題)
- [ネットワークとポートの問題](#ネットワークとポートの問題)
- [依存関係の問題](#依存関係の問題)
- [データベースの問題](#データベースの問題)
- [フロントエンドの問題](#フロントエンドの問題)
- [テスト実行の問題](#テスト実行の問題)
- [パフォーマンスの問題](#パフォーマンスの問題)
- [デバッグ方法](#デバッグ方法)
- [エラーメッセージリファレンス](#エラーメッセージリファレンス)

---

## 環境セットアップの問題

### Python が見つからない

**症状:**
```
'python' is not recognized as an internal or external command
```

**原因:**
- Python がインストールされていない
- PATH 環境変数が設定されていない

**解決方法:**

#### Windows
```powershell
# Python のインストール確認
where python

# PATH に追加（管理者権限で実行）
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"

# または、Microsoft Store から Python をインストール
winget install Python.Python.3.11
```

#### macOS/Linux
```bash
# Python のインストール確認
which python3

# シンボリックリンクを作成
sudo ln -s /usr/bin/python3 /usr/local/bin/python

# または、Homebrew でインストール（macOS）
brew install python@3.11
```

### Node.js が見つからない

**症状:**
```
'node' is not recognized as an internal or external command
```

**解決方法:**

#### Windows
```powershell
# Node.js のインストール
winget install OpenJS.NodeJS.LTS

# インストール後、新しいターミナルを開く
```

#### macOS
```bash
# Homebrew でインストール
brew install node@18

# PATH に追加
echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```


#### Linux (Ubuntu/Debian)
```bash
# Node.js のインストール
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# バージョン確認
node --version
npm --version
```

### バージョンが古い

**症状:**
```
Python version 3.8 is not supported. Please use Python 3.9 or higher.
```

**解決方法:**

```bash
# 現在のバージョン確認
python --version

# 新しいバージョンをインストール
# Windows: 公式サイトからインストーラーをダウンロード
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11

# 仮想環境で特定のバージョンを使用
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 権限エラー

**症状:**
```
PermissionError: [Errno 13] Permission denied
```

**解決方法:**

#### Windows
```powershell
# 管理者権限でターミナルを開く
# または、ユーザーディレクトリにインストール
pip install --user -r requirements.txt
```

#### macOS/Linux
```bash
# sudo を使用（推奨しない）
sudo pip install -r requirements.txt

# 仮想環境を使用（推奨）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## サービス起動の問題

### サービスが起動しない

**症状:**
```
Failed to start service: auth
Error: Service process exited with code 1
```

**診断手順:**

```bash
# 1. ログを確認
python local_test_cli.py logs --service auth

# 2. ヘルスチェック
python local_test_cli.py health

# 3. 手動でサービスを起動してエラーを確認
cd services/auth
python main.py
```

**一般的な原因と解決方法:**

#### 1. 依存関係が不足
```bash
# 依存関係を再インストール
pip install -r requirements.txt
```

#### 2. ポートが使用中
```bash
# ポート使用状況を確認
python local_test_cli.py status

# 使用中のプロセスを終了（Windows）
netstat -ano | findstr :8002
taskkill /PID <PID> /F

# 使用中のプロセスを終了（macOS/Linux）
lsof -ti:8002 | xargs kill -9
```

#### 3. 環境変数が設定されていない
```bash
# .env.local ファイルを確認
cat .env.local  # macOS/Linux
type .env.local # Windows

# テンプレートから再生成
python local_test_cli.py setup
```

### サービスが突然停止する

**症状:**
サービスが起動後、数秒で停止する

**診断手順:**

```bash
# 詳細ログを有効化
# .env.local で LOG_LEVEL=DEBUG に設定

# サービスを再起動
python local_test_cli.py restart auth

# リアルタイムログを監視
python local_test_cli.py logs --service auth --follow
```

**一般的な原因:**

1. **メモリ不足**: タスクマネージャーでメモリ使用量を確認
2. **設定エラー**: `services/<service>/main.py` の設定を確認
3. **データベース接続エラー**: モックデータベースの状態を確認


### ヘルスチェックが失敗する

**症状:**
```
Health check failed for service: core-game
Status: unhealthy
```

**解決方法:**

```bash
# 1. サービスが実際に起動しているか確認
python local_test_cli.py status

# 2. ヘルスエンドポイントに直接アクセス
curl http://localhost:8001/health

# 3. サービスを再起動
python local_test_cli.py restart core-game

# 4. それでも失敗する場合、完全なクリーンアップ
python local_test_cli.py cleanup
python local_test_cli.py start
```

---

## ネットワークとポートの問題

### ポート競合エラー

**症状:**
```
OSError: [Errno 48] Address already in use
OSError: [WinError 10048] Only one usage of each socket address
```

**解決方法:**

#### Windows
```powershell
# ポート使用状況を確認
netstat -ano | findstr :8001
netstat -ano | findstr :8002
netstat -ano | findstr :8003

# プロセスを終了
taskkill /PID <PID> /F

# または、すべてのPythonプロセスを終了
taskkill /IM python.exe /F
```

#### macOS/Linux
```bash
# ポート使用状況を確認
lsof -i :8001
lsof -i :8002
lsof -i :8003

# プロセスを終了
kill -9 <PID>

# または、ポートを使用しているすべてのプロセスを終了
lsof -ti:8001,8002,8003 | xargs kill -9
```

#### ポート番号を変更する方法

`.env.local` ファイルを編集：

```bash
# デフォルトポート
AUTH_SERVICE_PORT=8002
CORE_GAME_SERVICE_PORT=8001
TASK_MGMT_SERVICE_PORT=8003

# 別のポートに変更
AUTH_SERVICE_PORT=9002
CORE_GAME_SERVICE_PORT=9001
TASK_MGMT_SERVICE_PORT=9003
```

### CORS エラー

**症状:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**原因:**
フロントエンドからバックエンドAPIへのアクセスがブロックされている

**解決方法:**

#### 1. Vite プロキシ設定を確認

`frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

#### 2. バックエンドのCORS設定を確認

`services/*/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. サービスを再起動

```bash
python local_test_cli.py restart core-game
cd frontend && npm run dev
```

### ネットワークタイムアウト

**症状:**
```
TimeoutError: Service did not respond within 30 seconds
```

**解決方法:**

```bash
# タイムアウト時間を延長
# local_services_config.json を編集
{
  "services": [
    {
      "name": "auth",
      "startup_timeout": 60  # 30から60に変更
    }
  ]
}

# サービスを再起動
python local_test_cli.py restart auth
```

---

## 依存関係の問題

### pip インストールエラー

**症状:**
```
ERROR: Could not find a version that satisfies the requirement
ERROR: No matching distribution found
```

**解決方法:**

```bash
# 1. pip をアップグレード
python -m pip install --upgrade pip

# 2. キャッシュをクリア
pip cache purge

# 3. 依存関係を再インストール
pip install -r requirements.txt --no-cache-dir

# 4. 特定のパッケージでエラーが出る場合
pip install <package-name> --upgrade
```

### npm インストールエラー

**症状:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**解決方法:**

```bash
# 1. npm キャッシュをクリア
npm cache clean --force

# 2. node_modules を削除
cd frontend
rm -rf node_modules package-lock.json  # macOS/Linux
rmdir /s /q node_modules & del package-lock.json  # Windows

# 3. 再インストール
npm install

# 4. それでも失敗する場合、レガシーピア依存関係を使用
npm install --legacy-peer-deps
```


### パッケージバージョン競合

**症状:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**解決方法:**

```bash
# 1. 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. クリーンインストール
pip install -r requirements.txt

# 3. 競合を確認
pip check

# 4. 特定のバージョンを指定
pip install "fastapi==0.104.1" "uvicorn==0.24.0"
```

---

## データベースの問題

### モックデータベースの初期化エラー

**症状:**
```
Failed to initialize mock database
FileNotFoundError: test_data/sample_data.json not found
```

**解決方法:**

```bash
# 1. サンプルデータファイルが存在するか確認
ls test_data/sample_data.json  # macOS/Linux
dir test_data\sample_data.json # Windows

# 2. ファイルが存在しない場合、作成
mkdir -p test_data  # macOS/Linux
mkdir test_data     # Windows

# 3. 基本的なサンプルデータを作成
cat > test_data/sample_data.json << 'EOF'
{
  "users": [],
  "tasks": [],
  "mood_entries": []
}
EOF

# 4. セットアップを再実行
python local_test_cli.py setup
```

### データが保存されない

**症状:**
サービスを再起動すると、データが消える

**原因:**
モックデータベースがインメモリモードで動作している

**解決方法:**

`.env.local` を編集：
```bash
# データ永続化を有効化
USE_MOCK_DATABASE=true
MOCK_DATABASE_PERSIST=true
MOCK_DATABASE_FILE=./data/mock_firestore.json
```

サービスを再起動：
```bash
python local_test_cli.py restart
```

### データの破損

**症状:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**解決方法:**

```bash
# 1. データファイルをバックアップ
cp data/mock_firestore.json data/mock_firestore.json.backup  # macOS/Linux
copy data\mock_firestore.json data\mock_firestore.json.backup # Windows

# 2. データファイルを削除
rm data/mock_firestore.json  # macOS/Linux
del data\mock_firestore.json # Windows

# 3. サンプルデータから再初期化
python local_test_cli.py setup

# 4. サービスを再起動
python local_test_cli.py restart
```

---

## フロントエンドの問題

### Vite 開発サーバーが起動しない

**症状:**
```
Error: Cannot find module 'vite'
```

**解決方法:**

```bash
# 1. フロントエンドディレクトリに移動
cd frontend

# 2. 依存関係を再インストール
npm install

# 3. Vite を明示的にインストール
npm install vite --save-dev

# 4. 開発サーバーを起動
npm run dev
```

### ホットリロードが動作しない

**症状:**
コードを変更しても、ブラウザが自動的に更新されない

**解決方法:**

#### 1. Vite 設定を確認

`frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    watch: {
      usePolling: true  // WSL や Docker で必要な場合
    }
  }
})
```

#### 2. ブラウザのキャッシュをクリア

- Chrome: Ctrl+Shift+Delete (Windows) / Cmd+Shift+Delete (macOS)
- ハードリロード: Ctrl+F5 (Windows) / Cmd+Shift+R (macOS)

#### 3. 開発サーバーを再起動

```bash
cd frontend
npm run dev
```

### ビルドエラー

**症状:**
```
Error: Build failed with errors
```

**解決方法:**

```bash
# 1. TypeScript エラーを確認
cd frontend
npx tsc --noEmit

# 2. ESLint エラーを確認
npm run lint

# 3. 依存関係を更新
npm update

# 4. クリーンビルド
rm -rf dist  # macOS/Linux
rmdir /s /q dist  # Windows
npm run build
```

### API リクエストが失敗する

**症状:**
```
Failed to fetch
Network Error
```

**診断手順:**

```bash
# 1. バックエンドが起動しているか確認
python local_test_cli.py health

# 2. API エンドポイントに直接アクセス
curl http://localhost:8001/health
curl http://localhost:8002/health

# 3. ブラウザの開発者ツールでネットワークタブを確認
# - リクエストURL
# - ステータスコード
# - レスポンスヘッダー
```

**解決方法:**

1. **CORS エラー**: 上記の「CORS エラー」セクションを参照
2. **認証エラー**: JWT トークンが正しく設定されているか確認
3. **プロキシ設定**: `vite.config.ts` のプロキシ設定を確認


---

## テスト実行の問題

### pytest が見つからない

**症状:**
```
'pytest' is not recognized as an internal or external command
```

**解決方法:**

```bash
# pytest をインストール
pip install pytest pytest-cov pytest-asyncio

# または、requirements.txt から再インストール
pip install -r requirements.txt

# インストール確認
pytest --version
```

### テストが失敗する

**症状:**
```
FAILED tests/test_auth.py::test_login - AssertionError
```

**診断手順:**

```bash
# 1. 詳細出力でテストを実行
pytest tests/test_auth.py -v -s

# 2. 特定のテストのみ実行
pytest tests/test_auth.py::test_login -v -s

# 3. デバッグモードで実行
pytest tests/test_auth.py --pdb

# 4. ログを確認
pytest tests/test_auth.py -v --log-cli-level=DEBUG
```

**一般的な原因:**

#### 1. サービスが起動していない
```bash
# サービスを起動
python local_test_cli.py start

# ヘルスチェック
python local_test_cli.py health
```

#### 2. テストデータが不正
```bash
# テストデータをリセット
python local_test_cli.py cleanup --keep-services
python local_test_cli.py start
```

#### 3. 環境変数が設定されていない
```bash
# .env.local を確認
cat .env.local

# テスト用の環境変数を設定
export USE_MOCK_DATABASE=true  # macOS/Linux
set USE_MOCK_DATABASE=true     # Windows
```

### カバレッジレポートが生成されない

**症状:**
```
Coverage report not found
```

**解決方法:**

```bash
# 1. pytest-cov がインストールされているか確認
pip list | grep pytest-cov  # macOS/Linux
pip list | findstr pytest-cov  # Windows

# 2. カバレッジ付きでテストを実行
pytest --cov=services --cov-report=html --cov-report=term

# 3. HTMLレポートを確認
# macOS/Linux
open htmlcov/index.html

# Windows
start htmlcov\index.html
```

### テストが遅い

**症状:**
テストの実行に時間がかかりすぎる

**最適化方法:**

```bash
# 1. 並列実行を有効化
pip install pytest-xdist
pytest -n auto

# 2. 特定のテストのみ実行
pytest tests/unit/ -v

# 3. マーカーを使用してテストを選択
pytest -m "not slow" -v

# 4. 失敗したテストのみ再実行
pytest --lf -v
```

---

## パフォーマンスの問題

### メモリ使用量が多い

**症状:**
システムが遅くなる、メモリ不足エラー

**診断:**

```bash
# メモリ使用量を確認
# Windows
tasklist | findstr python

# macOS/Linux
ps aux | grep python
top -p $(pgrep -d',' python)
```

**解決方法:**

#### 1. 必要なサービスのみ起動
```bash
# 全サービスを停止
python local_test_cli.py stop

# 必要なサービスのみ起動
python local_test_cli.py start --service auth --service core-game
```

#### 2. ログレベルを下げる
`.env.local`:
```bash
LOG_LEVEL=WARNING  # DEBUG から WARNING に変更
```

#### 3. データベースの永続化を無効化
`.env.local`:
```bash
MOCK_DATABASE_PERSIST=false
```

#### 4. フロントエンドを別途起動
```bash
# バックエンドのみ起動
python local_test_cli.py start --no-frontend

# 必要な時だけフロントエンドを起動
cd frontend
npm run dev
```

### CPU 使用率が高い

**症状:**
ファンが回る、システムが遅い

**解決方法:**

```bash
# 1. 自動リロードを無効化
# services/*/main.py で --reload オプションを削除

# 2. ログ出力を減らす
# .env.local で LOG_LEVEL=ERROR に設定

# 3. 不要なサービスを停止
python local_test_cli.py stop --service mandala
python local_test_cli.py stop --service mood-tracking
```

### 起動が遅い

**症状:**
サービスの起動に時間がかかる

**最適化:**

```bash
# 1. 依存関係をキャッシュ
pip install --cache-dir ~/.cache/pip -r requirements.txt

# 2. 並列起動を有効化
# local_services_config.json で parallel_startup: true に設定

# 3. タイムアウトを調整
# local_services_config.json で startup_timeout を短縮
```

---

## デバッグ方法

### ログの確認

#### CLI を使用
```bash
# 全サービスのログ
python local_test_cli.py logs

# 特定のサービスのログ
python local_test_cli.py logs --service auth

# リアルタイムログ
python local_test_cli.py logs --service auth --follow

# エラーのみ表示
python local_test_cli.py logs --service auth --level ERROR

# ログをファイルに保存
python local_test_cli.py logs --service auth --save debug.log
```

#### 直接ファイルを確認
```bash
# ログファイルの場所
tail -f logs/local_test.log  # macOS/Linux
Get-Content logs\local_test.log -Wait  # Windows PowerShell
```

### デバッガーの使用

#### Python デバッガー (pdb)

コードに以下を追加：
```python
import pdb; pdb.set_trace()
```

または、pytest で：
```bash
pytest tests/test_auth.py --pdb
```

#### VS Code デバッガー

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "services.auth.main:app",
        "--reload",
        "--port",
        "8002"
      ],
      "jinja": true
    }
  ]
}
```


### ブラウザ開発者ツール

#### ネットワークタブ
1. ブラウザで F12 を押す
2. Network タブを開く
3. API リクエストを確認
   - リクエストURL
   - メソッド (GET, POST, etc.)
   - ステータスコード
   - レスポンスボディ

#### コンソールタブ
1. Console タブを開く
2. JavaScript エラーを確認
3. console.log() の出力を確認

### API テスト

#### curl を使用
```bash
# ヘルスチェック
curl http://localhost:8001/health

# 認証テスト
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# JWT トークン付きリクエスト
curl http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer <token>"
```

#### Postman を使用
1. Postman をインストール
2. コレクションをインポート
3. 環境変数を設定
4. リクエストを実行

---

## エラーメッセージリファレンス

### 環境エラー

#### `EnvironmentError: Python version 3.8 is not supported`

**意味:** Python のバージョンが古い

**解決方法:**
```bash
# Python 3.9以上をインストール
# Windows: winget install Python.Python.3.11
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

#### `EnvironmentError: Node.js not found`

**意味:** Node.js がインストールされていない

**解決方法:**
```bash
# Node.js をインストール
# Windows: winget install OpenJS.NodeJS.LTS
# macOS: brew install node@18
# Linux: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs
```

### 依存関係エラー

#### `DependencyError: Failed to install Python dependencies`

**意味:** Python パッケージのインストールに失敗

**解決方法:**
```bash
# pip をアップグレード
python -m pip install --upgrade pip

# キャッシュをクリアして再インストール
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

#### `DependencyError: Failed to install Node.js dependencies`

**意味:** npm パッケージのインストールに失敗

**解決方法:**
```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### サービスエラー

#### `ServiceError: Port 8001 is already in use`

**意味:** ポートが既に使用されている

**解決方法:**
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8001 | xargs kill -9
```

#### `ServiceError: Service failed to start within timeout`

**意味:** サービスの起動がタイムアウト

**解決方法:**
```bash
# タイムアウトを延長
# local_services_config.json で startup_timeout を増やす

# ログを確認
python local_test_cli.py logs --service <service-name>

# 手動で起動してエラーを確認
cd services/<service-name>
python main.py
```

#### `ServiceError: Health check failed`

**意味:** サービスのヘルスチェックに失敗

**解決方法:**
```bash
# サービスを再起動
python local_test_cli.py restart <service-name>

# ヘルスエンドポイントに直接アクセス
curl http://localhost:<port>/health

# ログを確認
python local_test_cli.py logs --service <service-name>
```

### データベースエラー

#### `DatabaseError: Failed to initialize mock database`

**意味:** モックデータベースの初期化に失敗

**解決方法:**
```bash
# サンプルデータファイルを確認
ls test_data/sample_data.json

# ファイルが存在しない場合、作成
mkdir -p test_data
echo '{"users":[],"tasks":[],"mood_entries":[]}' > test_data/sample_data.json

# セットアップを再実行
python local_test_cli.py setup
```

#### `DatabaseError: Data file is corrupted`

**意味:** データファイルが破損している

**解決方法:**
```bash
# データファイルをバックアップ
cp data/mock_firestore.json data/mock_firestore.json.backup

# データファイルを削除
rm data/mock_firestore.json

# サービスを再起動
python local_test_cli.py restart
```

### ネットワークエラー

#### `NetworkError: Connection refused`

**意味:** サービスに接続できない

**解決方法:**
```bash
# サービスが起動しているか確認
python local_test_cli.py status

# サービスを起動
python local_test_cli.py start

# ファイアウォールを確認
# Windows: ファイアウォール設定でPythonを許可
# macOS: システム環境設定 > セキュリティとプライバシー > ファイアウォール
```

#### `NetworkError: Timeout`

**意味:** リクエストがタイムアウト

**解決方法:**
```bash
# タイムアウト時間を延長
# .env.local で REQUEST_TIMEOUT を増やす

# サービスのパフォーマンスを確認
python local_test_cli.py status

# ログを確認
python local_test_cli.py logs --level ERROR
```

### テストエラー

#### `TestError: Service not available for testing`

**意味:** テスト対象のサービスが起動していない

**解決方法:**
```bash
# サービスを起動
python local_test_cli.py start

# ヘルスチェック
python local_test_cli.py health

# テストを再実行
python local_test_cli.py test unit -v
```

#### `TestError: Test data not found`

**意味:** テストデータが見つからない

**解決方法:**
```bash
# テストデータを確認
ls test_data/

# サンプルデータをロード
python local_test_cli.py setup

# テストを再実行
pytest -v
```

---

## 高度なトラブルシューティング

### システム全体のリセット

すべてが失敗する場合、完全なリセットを試してください：

```bash
# 1. すべてのサービスを停止
python local_test_cli.py stop

# 2. 仮想環境を削除（使用している場合）
rm -rf venv  # macOS/Linux
rmdir /s /q venv  # Windows

# 3. 依存関係を削除
rm -rf node_modules  # macOS/Linux
rmdir /s /q node_modules  # Windows
pip uninstall -r requirements.txt -y

# 4. キャッシュをクリア
pip cache purge
npm cache clean --force

# 5. 再セットアップ
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
python local_test_cli.py setup

# 6. サービスを起動
python local_test_cli.py start
```

### ログの詳細分析

```bash
# エラーのみ抽出
grep ERROR logs/local_test.log  # macOS/Linux
findstr ERROR logs\local_test.log  # Windows

# 特定のサービスのログのみ
grep "service=auth" logs/local_test.log

# タイムスタンプでフィルタリング
grep "2024-10-18" logs/local_test.log

# ログを整形して表示
python -c "import json; print(json.dumps(json.load(open('logs/local_test.log')), indent=2))"
```

### パフォーマンスプロファイリング

```bash
# Python プロファイリング
python -m cProfile -o profile.stats services/auth/main.py

# プロファイル結果を表示
python -m pstats profile.stats

# メモリプロファイリング
pip install memory_profiler
python -m memory_profiler services/auth/main.py
```

---

## サポートとコミュニティ

### 問題を報告する前に

1. **このガイドを確認**: 該当する問題がないか確認
2. **ログを確認**: エラーメッセージの詳細を確認
3. **検索**: GitHub Issues で同様の問題を検索
4. **再現**: 問題を再現できる最小限の手順を確認

### GitHub Issues でのバグ報告

以下の情報を含めてください：

```markdown
## 環境情報
- OS: Windows 11 / macOS 13 / Ubuntu 22.04
- Python バージョン: 3.11.0
- Node.js バージョン: 18.17.0
- ブラウザ: Chrome 118

## 再現手順
1. `python local_test_cli.py setup` を実行
2. `python local_test_cli.py start` を実行
3. エラーが発生

## 期待される動作
サービスが正常に起動する

## 実際の動作
エラーメッセージ: [エラーメッセージをここに貼り付け]

## ログ
```
[関連するログをここに貼り付け]
```

## 試したこと
- 依存関係の再インストール
- サービスの再起動
```

### コミュニティサポート

- **GitHub Discussions**: 質問や議論
- **Stack Overflow**: タグ `therapeutic-gamification-app`
- **Discord**: コミュニティチャット（リンクは README 参照）

---

**最終更新**: 2024年10月18日  
**バージョン**: 1.0.0  
**メンテナー**: Therapeutic Gamification App Team


---

## テスト実行の問題

### テストが失敗する

**症状:**
```
FAILED tests/test_auth.py::test_login - AssertionError
```

**診断手順:**

```bash
# 1. 詳細な出力でテストを実行
pytest tests/test_auth.py -v -s

# 2. 特定のテストのみ実行
pytest tests/test_auth.py::test_login -v -s

# 3. デバッグモードで実行
pytest tests/test_auth.py --pdb
```

**一般的な原因と解決方法:**

#### 1. サービスが起動していない
```bash
# サービスを起動
python local_test_cli.py start

# ヘルスチェック
python local_test_cli.py health
```

#### 2. テストデータが不正
```bash
# テストデータをリセット
python local_test_cli.py cleanup --keep-services
python local_test_cli.py setup
```

#### 3. 環境変数が設定されていない
```bash
# .env.local を確認
cat .env.local  # macOS/Linux
type .env.local # Windows

# テスト用の環境変数を設定
export TEST_MODE=true  # macOS/Linux
set TEST_MODE=true     # Windows
```

### テストがタイムアウトする

**症状:**
```
TimeoutError: Test exceeded maximum execution time
```

**解決方法:**

```bash
# タイムアウト時間を延長
pytest tests/ --timeout=60

# または、pytest.ini で設定
# [pytest]
# timeout = 60
```

### カバレッジレポートが生成されない

**症状:**
```
ERROR: Coverage data not found
```

**解決方法:**

```bash
# 1. pytest-cov がインストールされているか確認
pip install pytest-cov

# 2. カバレッジ付きでテストを実行
pytest --cov=services --cov-report=html

# 3. レポートを確認
# htmlcov/index.html をブラウザで開く
```

---

## パフォーマンスの問題

### 起動が遅い

**症状:**
サービスの起動に1分以上かかる

**診断手順:**

```bash
# 起動時間を測定
time python local_test_cli.py start  # macOS/Linux
Measure-Command { python local_test_cli.py start }  # Windows PowerShell
```

**解決方法:**

#### 1. 必要なサービスのみ起動
```bash
# 特定のサービスのみ起動
python local_test_cli.py start --service auth --service core-game
```

#### 2. 並列起動を有効化
`local_services_config.json` を編集：
```json
{
  "parallel_startup": true,
  "max_parallel_services": 4
}
```

#### 3. 依存関係をキャッシュ
```bash
# Python パッケージをキャッシュ
pip install --cache-dir ~/.pip/cache -r requirements.txt

# npm パッケージをキャッシュ
npm ci --cache ~/.npm
```

### メモリ使用量が多い

**症状:**
システムのメモリ使用量が80%を超える

**診断手順:**

```bash
# メモリ使用量を確認
python local_test_cli.py status --memory

# プロセスごとのメモリ使用量（Windows）
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

# プロセスごとのメモリ使用量（macOS/Linux）
ps aux | grep python
```

**解決方法:**

#### 1. 不要なサービスを停止
```bash
# 使用していないサービスを停止
python local_test_cli.py stop --service mandala
```

#### 2. ログレベルを下げる
`.env.local` を編集：
```bash
LOG_LEVEL=WARNING  # DEBUG から WARNING に変更
```

#### 3. データベースの永続化を無効化
`.env.local` を編集：
```bash
MOCK_DATABASE_PERSIST=false  # メモリ使用量を削減
```

### CPU使用率が高い

**症状:**
CPU使用率が常に80%以上

**診断手順:**

```bash
# CPU使用率を確認（Windows）
wmic cpu get loadpercentage

# CPU使用率を確認（macOS/Linux）
top -l 1 | grep "CPU usage"
```

**解決方法:**

#### 1. ホットリロードを無効化
```bash
# 開発サーバーをホットリロードなしで起動
cd services/auth
uvicorn main:app --host 0.0.0.0 --port 8002  # --reload を削除
```

#### 2. ログ出力を削減
`.env.local` を編集：
```bash
LOG_LEVEL=ERROR  # エラーのみログ出力
```

---

## デバッグ方法

### ログの確認

#### 統一CLIを使用
```bash
# 特定のサービスのログを表示
python local_test_cli.py logs --service auth

# 最新100行を表示
python local_test_cli.py logs --service auth --lines 100

# エラーのみ表示
python local_test_cli.py logs --service auth --level ERROR

# リアルタイムでログを監視
python local_test_cli.py logs --service auth --follow
```

#### 直接ログファイルを確認
```bash
# ログファイルの場所
cat ./logs/local_test.log  # macOS/Linux
type .\logs\local_test.log # Windows

# 最新のログを表示
tail -f ./logs/local_test.log  # macOS/Linux
Get-Content .\logs\local_test.log -Wait -Tail 50  # Windows PowerShell
```

### デバッガーの使用

#### Python デバッガー (pdb)

サービスコードにブレークポイントを設定：
```python
import pdb; pdb.set_trace()
```

サービスを手動で起動：
```bash
cd services/auth
python main.py
```

#### VS Code デバッガー

`.vscode/launch.json` を作成：
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Auth Service",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/services/auth/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### ネットワークトラフィックの監視

#### curl を使用
```bash
# ヘルスチェック
curl -v http://localhost:8001/health

# 認証テスト
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# レスポンスヘッダーを表示
curl -I http://localhost:8001/health
```

#### ブラウザ開発者ツール

1. ブラウザで F12 を押す
2. Network タブを開く
3. リクエストを実行
4. リクエスト/レスポンスの詳細を確認

### データベースの状態確認

```bash
# モックデータベースの内容を確認
cat data/mock_firestore.json  # macOS/Linux
type data\mock_firestore.json # Windows

# JSON を整形して表示
python -m json.tool data/mock_firestore.json

# 特定のコレクションを確認
python -c "import json; print(json.load(open('data/mock_firestore.json'))['users'])"
```

---

## エラーメッセージリファレンス

### 環境関連エラー

| エラーメッセージ | 原因 | 解決方法 |
|----------------|------|---------|
| `Python not found` | Python がインストールされていない | Python 3.9以上をインストール |
| `Node.js not found` | Node.js がインストールされていない | Node.js 16以上をインストール |
| `Permission denied` | 権限不足 | 管理者権限で実行、または仮想環境を使用 |
| `Command not found` | PATH が設定されていない | 環境変数 PATH を設定 |

### サービス起動エラー

| エラーメッセージ | 原因 | 解決方法 |
|----------------|------|---------|
| `Address already in use` | ポートが使用中 | ポートを使用しているプロセスを終了 |
| `Module not found` | 依存関係が不足 | `pip install -r requirements.txt` |
| `Connection refused` | サービスが起動していない | サービスを起動 |
| `Timeout waiting for service` | 起動に時間がかかりすぎ | タイムアウト時間を延長 |

### データベースエラー

| エラーメッセージ | 原因 | 解決方法 |
|----------------|------|---------|
| `File not found: sample_data.json` | サンプルデータが存在しない | サンプルデータファイルを作成 |
| `JSONDecodeError` | データファイルが破損 | データファイルを削除して再作成 |
| `Database connection failed` | データベースに接続できない | モックデータベースの設定を確認 |

### ネットワークエラー

| エラーメッセージ | 原因 | 解決方法 |
|----------------|------|---------|
| `CORS policy blocked` | CORS設定が不正 | CORS設定を確認 |
| `Network timeout` | ネットワークが遅い | タイムアウト時間を延長 |
| `Connection reset` | サービスが停止した | サービスを再起動 |
| `404 Not Found` | エンドポイントが存在しない | URLを確認 |

### テストエラー

| エラーメッセージ | 原因 | 解決方法 |
|----------------|------|---------|
| `Test failed: AssertionError` | テストの期待値と実際の値が異なる | テストコードまたは実装を確認 |
| `Fixture not found` | テストフィクスチャが定義されていない | フィクスチャを定義 |
| `Coverage data not found` | カバレッジデータが生成されていない | `pytest-cov` をインストール |

---

## 高度なトラブルシューティング

### システムリソースの監視

#### Windows
```powershell
# リソースモニターを起動
resmon

# タスクマネージャーでプロセスを確認
taskmgr

# PowerShell でリソース使用量を確認
Get-Process python | Select-Object Name, CPU, WorkingSet
```

#### macOS/Linux
```bash
# システムリソースを監視
top

# プロセスごとのリソース使用量
htop  # インストールが必要: brew install htop

# メモリ使用量
free -h  # Linux
vm_stat  # macOS
```

### ネットワーク診断

```bash
# ポートが開いているか確認
nc -zv localhost 8001  # macOS/Linux
Test-NetConnection -ComputerName localhost -Port 8001  # Windows PowerShell

# ネットワーク接続を確認
netstat -an | grep 8001  # macOS/Linux
netstat -an | findstr 8001  # Windows

# DNS解決を確認
nslookup localhost
```

### ログ分析

```bash
# エラーログのみ抽出
grep ERROR ./logs/local_test.log  # macOS/Linux
Select-String -Path .\logs\local_test.log -Pattern "ERROR"  # Windows PowerShell

# 特定の時間帯のログを確認
grep "2024-10-18 10:" ./logs/local_test.log

# ログの統計情報
grep -c ERROR ./logs/local_test.log  # エラー数をカウント
```

### パフォーマンスプロファイリング

#### Python プロファイリング
```bash
# cProfile を使用
python -m cProfile -o profile.stats services/auth/main.py

# プロファイル結果を表示
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

#### メモリプロファイリング
```bash
# memory_profiler をインストール
pip install memory_profiler

# メモリ使用量をプロファイル
python -m memory_profiler services/auth/main.py
```

---

## 緊急時の対応

### 完全なリセット

すべてが動作しなくなった場合の最終手段：

```bash
# 1. すべてのサービスを停止
python local_test_cli.py stop

# 2. すべてのPythonプロセスを終了（注意！）
# Windows
taskkill /IM python.exe /F

# macOS/Linux
killall python

# 3. 一時ファイルとログを削除
python local_test_cli.py cleanup --temp-files

# 4. 依存関係を再インストール
pip install -r requirements.txt --force-reinstall
cd frontend && npm install

# 5. 環境を再セットアップ
python local_test_cli.py setup

# 6. サービスを起動
python local_test_cli.py start
```

### バックアップからの復元

```bash
# データをバックアップ（事前に実行）
cp data/mock_firestore.json data/backup_$(date +%Y%m%d).json  # macOS/Linux
copy data\mock_firestore.json data\backup_%date:~0,4%%date:~5,2%%date:~8,2%.json  # Windows

# バックアップから復元
cp data/backup_20241018.json data/mock_firestore.json  # macOS/Linux
copy data\backup_20241018.json data\mock_firestore.json  # Windows
```

---

## サポートとコミュニティ

### ヘルプの取得

1. **ドキュメントを確認**
   - [README_LOCAL_TEST.md](README_LOCAL_TEST.md) - セットアップガイド
   - [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) - API使用方法

2. **GitHub Issues**
   - 既存の問題を検索
   - 新しい Issue を作成

3. **ログを共有**
   ```bash
   # ログをファイルに保存
   python local_test_cli.py logs --service auth --save auth_debug.log
   ```

### バグ報告のベストプラクティス

Issue を作成する際は、以下の情報を含めてください：

```markdown
## 環境情報
- OS: Windows 11 / macOS 13 / Ubuntu 22.04
- Python バージョン: 3.11.0
- Node.js バージョン: 18.17.0

## 再現手順
1. `python local_test_cli.py setup` を実行
2. `python local_test_cli.py start` を実行
3. エラーが発生

## 期待される動作
サービスが正常に起動する

## 実際の動作
エラーメッセージ:
```
[エラーメッセージをここに貼り付け]
```

## ログ
```
[関連するログをここに貼り付け]
```

## 試したこと
- 依存関係を再インストール
- ポートを確認
```

---

## まとめ

このトラブルシューティングガイドでは、ローカルテスト環境で発生する可能性のある問題と解決方法を説明しました。

### 問題解決の基本フロー

1. **エラーメッセージを確認** - 何が問題なのかを理解する
2. **ログを確認** - 詳細な情報を収集する
3. **このガイドを参照** - 類似の問題と解決方法を探す
4. **基本的な対処を試す** - 再起動、再インストールなど
5. **それでも解決しない場合** - コミュニティに質問する

### よく使うコマンド

```bash
# 状態確認
python local_test_cli.py status
python local_test_cli.py health

# ログ確認
python local_test_cli.py logs --service <service-name>

# 再起動
python local_test_cli.py restart <service-name>

# クリーンアップ
python local_test_cli.py cleanup
```

### さらなるヘルプ

- [README_LOCAL_TEST.md](README_LOCAL_TEST.md) - 基本的なセットアップ
- [GitHub Issues](https://github.com/your-repo/issues) - バグ報告と質問
- [API ドキュメント](http://localhost:8001/docs) - API リファレンス

---

**最終更新**: 2024年10月18日  
**バージョン**: 1.0.0  
**メンテナー**: Therapeutic Gamification App Team
