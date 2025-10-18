# 🚀 クイックスタートガイド

このプロダクトをローカル環境で素早くテストする方法を説明します。

## 📋 前提条件

- Python 3.9以上
- Node.js 16以上（フロントエンド開発の場合）
- 2GB以上の空きメモリ（推奨）

## ⚡ 3ステップでスタート

### ステップ1: セットアップ

```bash
python local_test_setup.py
```

このコマンドで以下が自動実行されます：
- ✅ 環境チェック
- ✅ Python依存関係のインストール
- ✅ フロントエンド依存関係のインストール
- ✅ 環境変数ファイルの生成

### ステップ2: バックエンド起動

```bash
python start_mvp_services.py
```

以下のサービスが起動します：
- 🔐 認証サービス (http://localhost:8002)
- 🎮 コアゲームサービス (http://localhost:8001)
- 📝 タスク管理サービス (http://localhost:8003)
- 🎨 Mandalaサービス (http://localhost:8004)

### ステップ3: フロントエンド起動（オプション）

別のターミナルで：

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:3000 にアクセス

## 🧪 バックエンドのみテスト

フロントエンドなしでバックエンドAPIをテストする場合：

```bash
python test_backend_only.py
```

このスクリプトは：
- ✅ 全バックエンドサービスを起動
- ✅ ヘルスチェックを実行
- ✅ 基本APIエンドポイントをテスト
- ✅ APIドキュメントのURLを表示

## 📚 APIドキュメント

各サービスのAPIドキュメントにアクセス：

- **Core Game API**: http://localhost:8001/docs
- **Auth API**: http://localhost:8002/docs
- **Task Management API**: http://localhost:8003/docs
- **Mandala API**: http://localhost:8004/docs

## 🔧 トラブルシューティング

### ポート競合エラー

```bash
# Windowsの場合
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Python依存関係エラー

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### npm/Node.jsが見つからない

Node.jsをインストール: https://nodejs.org/

バックエンドのみのテストは可能です：
```bash
python test_backend_only.py
```

## 📖 詳細ドキュメント

より詳しい情報は以下を参照：
- [ローカルテスト環境セットアップガイド](README_LOCAL_TEST.md)
- [メインREADME](README.md)

## 🎯 次のステップ

1. **APIを試す**: http://localhost:8001/docs でAPIを試してみる
2. **テストを実行**: `pytest services/ -v`
3. **コードを編集**: サービスは自動リロードされます

---

**問題が発生した場合は、[README_LOCAL_TEST.md](README_LOCAL_TEST.md)のトラブルシューティングセクションを確認してください。**
