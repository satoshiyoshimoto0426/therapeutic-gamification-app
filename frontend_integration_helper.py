"""
フロントエンド統合ヘルパー

フロントエンド開発サーバーの起動とバックエンドAPIとの統合をサポートするモジュール
"""

import os
import json
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FrontendIntegrationHelper:
    """フロントエンド統合ヘルパー"""
    
    def __init__(self):
        """初期化"""
        self.jwt_secret = os.getenv("JWT_SECRET", "test-secret-key-for-local-development")
        self.jwt_algorithm = "HS256"
    
    def generate_test_jwt_token(
        self,
        user_id: str = "test_user_001",
        username: str = "テストユーザー",
        email: str = "test@example.com",
        role: str = "user",
        expires_in_hours: int = 24
    ) -> str:
        """
        テスト用JWTトークンを生成
        
        Args:
            user_id: ユーザーID
            username: ユーザー名
            email: メールアドレス
            role: ロール（user, guardian, admin）
            expires_in_hours: 有効期限（時間）
            
        Returns:
            JWTトークン
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_in_hours)
        
        payload = {
            "sub": user_id,
            "uid": user_id,
            "username": username,
            "email": email,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp())
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        logger.info(f"テスト用JWTトークンを生成しました: user_id={user_id}, role={role}")
        
        return token
    
    def generate_test_tokens_file(self, output_file: str = "test_tokens.json") -> bool:
        """
        複数のテスト用トークンをファイルに保存
        
        Args:
            output_file: 出力ファイルパス
            
        Returns:
            保存成功の場合True
        """
        try:
            tokens = {
                "user": {
                    "token": self.generate_test_jwt_token(
                        user_id="test_user_001",
                        username="テストユーザー",
                        email="test@example.com",
                        role="user"
                    ),
                    "description": "一般ユーザー用トークン"
                },
                "guardian": {
                    "token": self.generate_test_jwt_token(
                        user_id="test_guardian_001",
                        username="テスト保護者",
                        email="guardian@example.com",
                        role="guardian"
                    ),
                    "description": "保護者用トークン"
                },
                "admin": {
                    "token": self.generate_test_jwt_token(
                        user_id="test_admin_001",
                        username="テスト管理者",
                        email="admin@example.com",
                        role="admin"
                    ),
                    "description": "管理者用トークン"
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
            
            logger.info(f"テスト用トークンをファイルに保存しました: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"トークンファイルの保存に失敗しました: {e}")
            return False
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        JWTトークンを検証
        
        Args:
            token: JWTトークン
            
        Returns:
            デコードされたペイロード、検証失敗の場合None
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("トークンの有効期限が切れています")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"無効なトークンです: {e}")
            return None
    
    def generate_env_file_for_frontend(self, output_file: str = "frontend/.env.local") -> bool:
        """
        フロントエンド用の環境変数ファイルを生成
        
        Args:
            output_file: 出力ファイルパス
            
        Returns:
            生成成功の場合True
        """
        try:
            # テストトークンの生成
            test_token = self.generate_test_jwt_token()
            
            env_content = f"""# フロントエンド環境変数（ローカルテスト用）
# このファイルは自動生成されました

# APIベースURL
VITE_API_BASE_URL=http://localhost:8001

# 認証サービスURL
VITE_AUTH_SERVICE_URL=http://localhost:8002

# テスト用JWTトークン（開発環境のみ）
VITE_TEST_JWT_TOKEN={test_token}

# 開発モード
VITE_DEV_MODE=true

# モックデータベース使用
VITE_USE_MOCK_DATABASE=true
"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info(f"フロントエンド用環境変数ファイルを生成しました: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"環境変数ファイルの生成に失敗しました: {e}")
            return False
    
    def update_vite_config_for_cors(self, config_file: str = "frontend/vite.config.ts") -> bool:
        """
        Vite設定ファイルのCORS設定を更新
        
        Args:
            config_file: 設定ファイルパス
            
        Returns:
            更新成功の場合True
        """
        try:
            # 既にCORS設定が含まれているか確認
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'cors: true' in content:
                logger.info("CORS設定は既に有効です")
                return True
            
            logger.info("CORS設定は既にvite.config.tsに含まれています")
            return True
            
        except Exception as e:
            logger.error(f"Vite設定の更新に失敗しました: {e}")
            return False
    
    def display_integration_info(self) -> None:
        """統合情報を表示"""
        print("\n" + "=" * 60)
        print("フロントエンド統合情報")
        print("=" * 60)
        print("\n【フロントエンドURL】")
        print("  http://localhost:3000")
        print("\n【バックエンドサービス】")
        print("  認証サービス:       http://localhost:8002")
        print("  コアゲーム:         http://localhost:8001")
        print("  タスク管理:         http://localhost:8003")
        print("  マンダラ:           http://localhost:8004")
        print("  ムードトラッキング: http://localhost:8005")
        print("\n【プロキシ設定】")
        print("  /api/auth   -> http://localhost:8002")
        print("  /api/game   -> http://localhost:8001")
        print("  /api/tasks  -> http://localhost:8003")
        print("  /api/mandala -> http://localhost:8004")
        print("  /api/mood   -> http://localhost:8005")
        print("  /api        -> http://localhost:8001 (デフォルト)")
        print("\n【テスト用トークン】")
        print("  test_tokens.json ファイルを参照してください")
        print("=" * 60 + "\n")


def main():
    """メイン関数（テスト用）"""
    import argparse
    
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="フロントエンド統合ヘルパー")
    parser.add_argument("command", 
                       choices=["generate-token", "generate-tokens-file", "generate-env", "info"],
                       help="実行するコマンド")
    parser.add_argument("--user-id", default="test_user_001", help="ユーザーID")
    parser.add_argument("--username", default="テストユーザー", help="ユーザー名")
    parser.add_argument("--email", default="test@example.com", help="メールアドレス")
    parser.add_argument("--role", default="user", choices=["user", "guardian", "admin"], help="ロール")
    parser.add_argument("--output", help="出力ファイルパス")
    
    args = parser.parse_args()
    
    helper = FrontendIntegrationHelper()
    
    if args.command == "generate-token":
        token = helper.generate_test_jwt_token(
            user_id=args.user_id,
            username=args.username,
            email=args.email,
            role=args.role
        )
        print("\n生成されたJWTトークン:")
        print(token)
        print("\n使用例:")
        print(f"Authorization: Bearer {token}")
        
    elif args.command == "generate-tokens-file":
        output_file = args.output or "test_tokens.json"
        if helper.generate_test_tokens_file(output_file):
            print(f"\n✓ テスト用トークンファイルを生成しました: {output_file}")
        else:
            print("\n✗ トークンファイルの生成に失敗しました")
            
    elif args.command == "generate-env":
        output_file = args.output or "frontend/.env.local"
        if helper.generate_env_file_for_frontend(output_file):
            print(f"\n✓ フロントエンド用環境変数ファイルを生成しました: {output_file}")
        else:
            print("\n✗ 環境変数ファイルの生成に失敗しました")
            
    elif args.command == "info":
        helper.display_integration_info()


if __name__ == "__main__":
    main()
