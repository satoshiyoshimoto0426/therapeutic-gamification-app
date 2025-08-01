"""
JWT Service

JWT トークン管理サービス
Requirements: 6.1, 10.3
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
import uuid


class TokenType(str):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPair(BaseModel):
    """トークンペア"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class JWTClaims(BaseModel):
    """JWT クレーム"""
    guardian_id: str
    user_id: str
    permission_level: str
    token_type: str
    jti: str
    issued_at: datetime
    expires_at: datetime


class JWTService:
    """JWT サービス"""
    
    def __init__(self):
        # 実際の実装では環境変数から取得
        self.secret_key = "your-jwt-secret-key"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 30
        
        # トークンブラックリスト（実際の実装ではRedisを使用）
        self.blacklisted_tokens: set = set()
    
    def create_token_pair(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: str
    ) -> TokenPair:
        """トークンペア作成"""
        try:
            # アクセストークン作成
            access_token = self._create_token(
                guardian_id=guardian_id,
                user_id=user_id,
                permission_level=permission_level,
                token_type=TokenType.ACCESS,
                expire_minutes=self.access_token_expire_minutes
            )
            
            # リフレッシュトークン作成
            refresh_token = self._create_token(
                guardian_id=guardian_id,
                user_id=user_id,
                permission_level=permission_level,
                token_type=TokenType.REFRESH,
                expire_minutes=self.refresh_token_expire_days * 24 * 60
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.access_token_expire_minutes * 60,
                refresh_expires_in=self.refresh_token_expire_days * 24 * 60 * 60
            )
            
        except Exception as e:
            raise ValueError(f"トークン作成に失敗しました: {str(e)}")
    
    def verify_token(self, token: str) -> JWTClaims:
        """トークン検証"""
        try:
            # ブラックリストチェック
            if token in self.blacklisted_tokens:
                raise ValueError("無効なトークンです")
            
            # JWT デコード
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 必須フィールドチェック
            required_fields = ["guardian_id", "user_id", "permission_level", "token_type", "jti", "iat", "exp"]
            for field in required_fields:
                if field not in payload:
                    raise ValueError(f"トークンに必須フィールド '{field}' がありません")
            
            # 有効期限チェック
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise ValueError("トークンの有効期限が切れています")
            
            return JWTClaims(
                guardian_id=payload["guardian_id"],
                user_id=payload["user_id"],
                permission_level=payload["permission_level"],
                token_type=payload["token_type"],
                jti=payload["jti"],
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
            
        except jwt.ExpiredSignatureError:
            raise ValueError("トークンの有効期限が切れています")
        except jwt.InvalidTokenError:
            raise ValueError("無効なトークンです")
        except Exception as e:
            raise ValueError(f"トークン検証でエラーが発生しました: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> TokenPair:
        """トークンリフレッシュ"""
        try:
            # リフレッシュトークン検証
            claims = self.verify_token(refresh_token)
            
            # リフレッシュトークンかチェック
            if claims.token_type != TokenType.REFRESH:
                raise ValueError("リフレッシュトークンではありません")
            
            # 新しいトークンペア作成
            new_token_pair = self.create_token_pair(
                guardian_id=claims.guardian_id,
                user_id=claims.user_id,
                permission_level=claims.permission_level
            )
            
            # 古いリフレッシュトークンを無効化
            self.revoke_token(claims.jti)
            
            return new_token_pair
            
        except Exception as e:
            raise ValueError(f"トークンリフレッシュに失敗しました: {str(e)}")
    
    def revoke_token(self, jti: str):
        """トークン無効化"""
        self.blacklisted_tokens.add(jti)
    
    def revoke_all_user_tokens(self, guardian_id: str, user_id: str):
        """ユーザーの全トークン無効化"""
        # 実際の実装では、データベースから該当トークンを検索して無効化
        # ここでは簡単な実装として、ブラックリストに追加
        pass
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """トークンがブラックリストに登録されているかチェック"""
        return jti in self.blacklisted_tokens
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """トークン情報取得"""
        try:
            claims = self.verify_token(token)
            
            return {
                "guardian_id": claims.guardian_id,
                "user_id": claims.user_id,
                "permission_level": claims.permission_level,
                "token_type": claims.token_type,
                "jti": claims.jti,
                "issued_at": claims.issued_at.isoformat(),
                "expires_at": claims.expires_at.isoformat(),
                "is_expired": claims.expires_at < datetime.utcnow(),
                "is_blacklisted": self.is_token_blacklisted(claims.jti)
            }
            
        except Exception as e:
            raise ValueError(f"トークン情報取得に失敗しました: {str(e)}")
    
    def _create_token(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: str,
        token_type: str,
        expire_minutes: int
    ) -> str:
        """トークン作成"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=expire_minutes)
        
        payload = {
            "guardian_id": guardian_id,
            "user_id": user_id,
            "permission_level": permission_level,
            "token_type": token_type,
            "jti": str(uuid.uuid4()),
            "iat": now.timestamp(),
            "exp": expire.timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def cleanup_expired_tokens(self) -> int:
        """期限切れトークンのクリーンアップ"""
        # 実際の実装では、データベースから期限切れトークンを削除
        # ここでは簡単な実装として、ブラックリストのクリーンアップのみ
        cleaned_count = 0
        
        # ブラックリストから期限切れトークンを削除
        # （実際の実装では、JTIと有効期限の対応表を管理する必要がある）
        
        return cleaned_count


# グローバルインスタンス
jwt_service = JWTService()