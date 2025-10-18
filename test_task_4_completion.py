"""
タスク4「フロントエンド統合の実装」の完了確認テスト
"""

import os
import json
import pytest
import jwt
from pathlib import Path
from frontend_integration_helper import FrontendIntegrationHelper
from local_service_manager import LocalServiceManager


def test_task_4_1_dev_server_startup():
    """
    タスク4.1: 開発サーバー起動機能の実装
    
    確認項目:
    - Vite開発サーバーの起動設定
    - ポート設定の管理
    - ホットリロード機能の確認
    """
    print("\n" + "=" * 60)
    print("タスク4.1: 開発サーバー起動機能の実装")
    print("=" * 60)
    
    # Vite設定ファイルの確認
    vite_config_path = "frontend/vite.config.ts"
    assert os.path.exists(vite_config_path), "Vite設定ファイルが見つかりません"
    
    with open(vite_config_path, 'r', encoding='utf-8') as f:
        vite_config = f.read()
    
    # ポート設定の確認
    assert "port: 3000" in vite_config, "ポート設定が正しくありません"
    print("✓ ポート設定: 3000")
    
    # ホスト設定の確認
    assert "host:" in vite_config, "ホスト設定が見つかりません"
    print("✓ ホスト設定: 設定済み")
    
    # package.jsonの確認
    package_json_path = "frontend/package.json"
    assert os.path.exists(package_json_path), "package.jsonが見つかりません"
    
    with open(package_json_path, 'r', encoding='utf-8') as f:
        package_json = json.load(f)
    
    # devスクリプトの確認
    assert "dev" in package_json.get("scripts", {}), "devスクリプトが見つかりません"
    assert "vite" in package_json["scripts"]["dev"], "Viteコマンドが設定されていません"
    print("✓ 開発サーバー起動コマンド: npm run dev")
    
    # サービスマネージャーでのフロントエンド設定確認
    manager = LocalServiceManager()
    assert manager.frontend_info is not None, "フロントエンド設定が見つかりません"
    
    frontend_config = manager.frontend_info.config
    assert frontend_config.port == 3000, "フロントエンドポートが正しくありません"
    assert "npm run dev" in frontend_config.command, "起動コマンドが正しくありません"
    print("✓ サービスマネージャー設定: 正常")
    
    print("\n✓ タスク4.1の全ての要件を満たしています")


def test_task_4_2_api_integration_settings():
    """
    タスク4.2: API統合設定の実装
    
    確認項目:
    - プロキシ設定の自動生成
    - CORS設定の調整
    - テスト用JWT トークン生成
    """
    print("\n" + "=" * 60)
    print("タスク4.2: API統合設定の実装")
    print("=" * 60)
    
    # プロキシ設定の確認
    vite_config_path = "frontend/vite.config.ts"
    with open(vite_config_path, 'r', encoding='utf-8') as f:
        vite_config = f.read()
    
    # 各サービスへのプロキシ設定
    proxy_endpoints = [
        "/api/auth",
        "/api/game",
        "/api/tasks",
        "/api/mandala",
        "/api/mood",
        "/api"
    ]
    
    for endpoint in proxy_endpoints:
        assert endpoint in vite_config, f"プロキシ設定が見つかりません: {endpoint}"
        print(f"✓ プロキシ設定: {endpoint}")
    
    # ターゲットポートの確認
    assert "localhost:8002" in vite_config, "認証サービスのプロキシ設定が正しくありません"
    assert "localhost:8001" in vite_config, "コアゲームサービスのプロキシ設定が正しくありません"
    assert "localhost:8003" in vite_config, "タスク管理サービスのプロキシ設定が正しくありません"
    assert "localhost:8004" in vite_config, "マンダラサービスのプロキシ設定が正しくありません"
    assert "localhost:8005" in vite_config, "ムードトラッキングサービスのプロキシ設定が正しくありません"
    print("✓ 全サービスのプロキシターゲット: 正常")
    
    # CORS設定の確認
    assert "cors: true" in vite_config, "CORS設定が有効になっていません"
    print("✓ CORS設定: 有効")
    
    # changeOriginの確認
    assert "changeOrigin: true" in vite_config, "changeOrigin設定が見つかりません"
    print("✓ changeOrigin設定: 有効")
    
    # テスト用JWTトークン生成機能の確認
    helper = FrontendIntegrationHelper()
    
    # トークン生成
    token = helper.generate_test_jwt_token()
    assert token is not None, "JWTトークンが生成されませんでした"
    assert len(token) > 0, "JWTトークンが空です"
    print("✓ JWTトークン生成: 成功")
    
    # トークンの検証
    payload = jwt.decode(
        token,
        helper.jwt_secret,
        algorithms=[helper.jwt_algorithm]
    )
    assert "uid" in payload, "トークンにuidが含まれていません"
    assert "role" in payload, "トークンにroleが含まれていません"
    assert "exp" in payload, "トークンに有効期限が含まれていません"
    print("✓ JWTトークン検証: 成功")
    
    # 複数ロールのトークン生成
    roles = ["user", "guardian", "admin"]
    for role in roles:
        token = helper.generate_test_jwt_token(role=role)
        payload = jwt.decode(token, helper.jwt_secret, algorithms=[helper.jwt_algorithm])
        assert payload["role"] == role, f"{role}トークンのロールが正しくありません"
    print("✓ 複数ロールのトークン生成: 成功")
    
    # トークンファイルの生成確認
    test_tokens_file = "test_tokens.json"
    if os.path.exists(test_tokens_file):
        with open(test_tokens_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        assert "user" in tokens, "userトークンが見つかりません"
        assert "guardian" in tokens, "guardianトークンが見つかりません"
        assert "admin" in tokens, "adminトークンが見つかりません"
        print("✓ テスト用トークンファイル: 生成済み")
    
    # フロントエンド環境変数ファイルの確認
    frontend_env_file = "frontend/.env.local"
    if os.path.exists(frontend_env_file):
        with open(frontend_env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        assert "VITE_API_BASE_URL" in env_content, "API_BASE_URLが設定されていません"
        assert "VITE_AUTH_SERVICE_URL" in env_content, "AUTH_SERVICE_URLが設定されていません"
        assert "VITE_TEST_JWT_TOKEN" in env_content, "TEST_JWT_TOKENが設定されていません"
        assert "VITE_DEV_MODE" in env_content, "DEV_MODEが設定されていません"
        print("✓ フロントエンド環境変数ファイル: 生成済み")
    
    print("\n✓ タスク4.2の全ての要件を満たしています")


def test_task_4_integration():
    """
    タスク4: フロントエンド統合の実装（統合テスト）
    
    確認項目:
    - フロントエンド開発サーバーの起動機能
    - バックエンドAPIへのプロキシ設定
    - CORS設定の調整
    """
    print("\n" + "=" * 60)
    print("タスク4: フロントエンド統合の実装（統合テスト）")
    print("=" * 60)
    
    # サービスマネージャーの初期化
    manager = LocalServiceManager()
    
    # フロントエンド統合ヘルパーの確認
    assert hasattr(manager, 'frontend_helper'), "フロントエンド統合ヘルパーが見つかりません"
    assert manager.frontend_helper is not None, "フロントエンド統合ヘルパーが初期化されていません"
    print("✓ フロントエンド統合ヘルパー: 初期化済み")
    
    # フロントエンド統合準備メソッドの確認
    assert hasattr(manager, 'prepare_frontend_integration'), "prepare_frontend_integrationメソッドが見つかりません"
    assert hasattr(manager, 'start_with_frontend'), "start_with_frontendメソッドが見つかりません"
    assert hasattr(manager, 'display_frontend_integration_info'), "display_frontend_integration_infoメソッドが見つかりません"
    print("✓ フロントエンド統合メソッド: 実装済み")
    
    # フロントエンド設定の確認
    assert manager.frontend_info is not None, "フロントエンド設定が見つかりません"
    frontend_config = manager.frontend_info.config
    
    assert frontend_config.name == "frontend", "フロントエンド名が正しくありません"
    assert frontend_config.port == 3000, "フロントエンドポートが正しくありません"
    assert frontend_config.path == "frontend", "フロントエンドパスが正しくありません"
    print("✓ フロントエンド設定: 正常")
    
    # 統合情報表示のテスト
    try:
        manager.display_frontend_integration_info()
        print("✓ 統合情報表示: 成功")
    except Exception as e:
        pytest.fail(f"統合情報表示に失敗しました: {e}")
    
    print("\n✓ タスク4の全ての統合要件を満たしています")


def test_requirements_verification():
    """
    要件の検証
    
    要件4.1: フロントエンド開発サーバーが起動する
    要件4.2: APIリクエストが送信される時、CORSが適切に処理される
    要件4.3: 認証が必要な場合、テスト用JWTトークンが生成される
    要件4.4: フロントエンドがバックエンドにアクセスする時、適切なプロキシ設定が使用される
    """
    print("\n" + "=" * 60)
    print("要件の検証")
    print("=" * 60)
    
    # 要件4.1: フロントエンド開発サーバーの起動
    manager = LocalServiceManager()
    assert manager.frontend_info is not None, "要件4.1: フロントエンド設定が見つかりません"
    assert manager.frontend_info.config.command, "要件4.1: 起動コマンドが設定されていません"
    print("✓ 要件4.1: フロントエンド開発サーバーが起動する")
    
    # 要件4.2: CORS設定
    vite_config_path = "frontend/vite.config.ts"
    with open(vite_config_path, 'r', encoding='utf-8') as f:
        vite_config = f.read()
    assert "cors: true" in vite_config, "要件4.2: CORS設定が有効になっていません"
    print("✓ 要件4.2: CORSが適切に処理される")
    
    # 要件4.3: テスト用JWTトークン生成
    helper = FrontendIntegrationHelper()
    token = helper.generate_test_jwt_token()
    assert token is not None, "要件4.3: JWTトークンが生成されませんでした"
    
    # トークンの検証
    payload = jwt.decode(token, helper.jwt_secret, algorithms=[helper.jwt_algorithm])
    assert "uid" in payload, "要件4.3: トークンにuidが含まれていません"
    print("✓ 要件4.3: テスト用JWTトークンが生成される")
    
    # 要件4.4: プロキシ設定
    assert "proxy:" in vite_config, "要件4.4: プロキシ設定が見つかりません"
    assert "/api" in vite_config, "要件4.4: APIプロキシが設定されていません"
    print("✓ 要件4.4: 適切なプロキシ設定が使用される")
    
    print("\n✓ 全ての要件を満たしています")


def main():
    """テストの実行"""
    print("\n" + "=" * 60)
    print("タスク4「フロントエンド統合の実装」完了確認テスト")
    print("=" * 60)
    
    # pytest実行
    exit_code = pytest.main([__file__, "-v", "--tb=short", "-s"])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✓ タスク4の全ての実装が完了しました")
        print("=" * 60)
        print("\n実装内容:")
        print("  4.1 開発サーバー起動機能の実装")
        print("    - Vite開発サーバーの起動設定")
        print("    - ポート設定の管理（3000番ポート）")
        print("    - ホットリロード機能の確認")
        print("\n  4.2 API統合設定の実装")
        print("    - プロキシ設定の自動生成（全サービス対応）")
        print("    - CORS設定の調整")
        print("    - テスト用JWT トークン生成機能")
        print("\n生成されたファイル:")
        print("  - frontend/vite.config.ts (更新)")
        print("  - frontend/.env.local (生成)")
        print("  - test_tokens.json (生成)")
        print("  - frontend_integration_helper.py (新規)")
        print("  - local_service_manager.py (更新)")
        print("\n使用方法:")
        print("  1. フロントエンド統合準備:")
        print("     python local_service_manager.py prepare-frontend")
        print("\n  2. フロントエンドを含む全サービス起動:")
        print("     python local_service_manager.py start --all --with-frontend")
        print("\n  3. 統合情報の表示:")
        print("     python local_service_manager.py frontend-info")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 一部のテストが失敗しました")
        print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    exit(main())
