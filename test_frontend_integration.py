"""
フロントエンド統合機能のテスト
"""

import os
import json
import pytest
import jwt
from pathlib import Path
from frontend_integration_helper import FrontendIntegrationHelper


class TestFrontendIntegrationHelper:
    """FrontendIntegrationHelperのテスト"""
    
    def setup_method(self):
        """各テストの前処理"""
        self.helper = FrontendIntegrationHelper()
        self.test_files = []
    
    def teardown_method(self):
        """各テストの後処理"""
        # テストで作成したファイルを削除
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_generate_test_jwt_token(self):
        """JWTトークン生成のテスト"""
        token = self.helper.generate_test_jwt_token(
            user_id="test_user",
            username="テストユーザー",
            email="test@example.com",
            role="user"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # トークンのデコード
        payload = jwt.decode(
            token,
            self.helper.jwt_secret,
            algorithms=[self.helper.jwt_algorithm]
        )
        
        assert payload["uid"] == "test_user"
        assert payload["username"] == "テストユーザー"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_generate_test_tokens_file(self):
        """トークンファイル生成のテスト"""
        output_file = "test_tokens_temp.json"
        self.test_files.append(output_file)
        
        result = self.helper.generate_test_tokens_file(output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        
        # ファイル内容の確認
        with open(output_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        assert "user" in tokens
        assert "guardian" in tokens
        assert "admin" in tokens
        
        assert "token" in tokens["user"]
        assert "description" in tokens["user"]
        
        # 各トークンの検証
        for role, token_data in tokens.items():
            token = token_data["token"]
            payload = jwt.decode(
                token,
                self.helper.jwt_secret,
                algorithms=[self.helper.jwt_algorithm]
            )
            assert payload["role"] == role
    
    def test_verify_token(self):
        """トークン検証のテスト"""
        # 有効なトークンの生成
        token = self.helper.generate_test_jwt_token()
        
        # 検証
        payload = self.helper.verify_token(token)
        
        assert payload is not None
        assert "uid" in payload
        assert "username" in payload
        assert "email" in payload
        assert "role" in payload
    
    def test_verify_invalid_token(self):
        """無効なトークン検証のテスト"""
        invalid_token = "invalid.token.here"
        
        payload = self.helper.verify_token(invalid_token)
        
        assert payload is None
    
    def test_generate_env_file_for_frontend(self):
        """フロントエンド環境変数ファイル生成のテスト"""
        output_file = "test_frontend_env.local"
        self.test_files.append(output_file)
        
        result = self.helper.generate_env_file_for_frontend(output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        
        # ファイル内容の確認
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "VITE_API_BASE_URL" in content
        assert "VITE_AUTH_SERVICE_URL" in content
        assert "VITE_TEST_JWT_TOKEN" in content
        assert "VITE_DEV_MODE" in content
        assert "VITE_USE_MOCK_DATABASE" in content
    
    def test_generate_different_roles(self):
        """異なるロールのトークン生成テスト"""
        roles = ["user", "guardian", "admin"]
        
        for role in roles:
            token = self.helper.generate_test_jwt_token(
                user_id=f"test_{role}",
                role=role
            )
            
            payload = jwt.decode(
                token,
                self.helper.jwt_secret,
                algorithms=[self.helper.jwt_algorithm]
            )
            
            assert payload["role"] == role
            assert payload["uid"] == f"test_{role}"


def test_vite_config_proxy_settings():
    """Vite設定のプロキシ設定テスト"""
    vite_config_path = "frontend/vite.config.ts"
    
    if not os.path.exists(vite_config_path):
        pytest.skip("Vite設定ファイルが見つかりません")
    
    with open(vite_config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # プロキシ設定の確認
    assert "proxy:" in content
    assert "/api/auth" in content
    assert "/api/game" in content
    assert "/api/tasks" in content
    assert "/api/mandala" in content
    assert "/api/mood" in content
    
    # CORS設定の確認
    assert "cors: true" in content
    
    # ポート設定の確認
    assert "port: 3000" in content


def test_integration_with_service_manager():
    """サービスマネージャーとの統合テスト"""
    from local_service_manager import LocalServiceManager
    
    # サービスマネージャーの初期化
    manager = LocalServiceManager()
    
    # フロントエンドヘルパーが初期化されているか確認
    assert manager.frontend_helper is not None
    assert isinstance(manager.frontend_helper, FrontendIntegrationHelper)
    
    # フロントエンド統合準備メソッドが存在するか確認
    assert hasattr(manager, 'prepare_frontend_integration')
    assert hasattr(manager, 'start_with_frontend')
    assert hasattr(manager, 'display_frontend_integration_info')


def main():
    """テストの実行"""
    print("=" * 60)
    print("フロントエンド統合機能のテスト")
    print("=" * 60)
    
    # pytest実行
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✓ 全てのテストが成功しました")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 一部のテストが失敗しました")
        print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    exit(main())
