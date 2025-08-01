"""
RBAC Middleware

Role-Based Access Control ミドルウェア
Requirements: 6.1
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uuid

from ..interfaces.rbac_system import (
    RBACSystem, PermissionLevel, ResourceType, Action, rbac_system
)


class AuthenticationError(HTTPException):
    """認証エラー"""
    def __init__(self, detail: str = "認証に失敗しました"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """認可エラー"""
    def __init__(self, detail: str = "権限がありません"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class GuardianToken:
    """ガーディアントークン"""
    def __init__(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: str,
        jti: str,
        issued_at: datetime,
        expires_at: datetime
    ):
        self.guardian_id = guardian_id
        self.user_id = user_id
        self.permission_level = permission_level
        self.jti = jti
        self.issued_at = issued_at
        self.expires_at = expires_at


class GuardianAuthService:
    """ガーディアン認証サービス"""
    
    def __init__(self):
        self.rbac_system = rbac_system
        self.secret_key = "your-secret-key"  # 実際の実装では環境変数から取得
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 30
        
        # トークンブラックリスト（実際の実装ではRedisを使用）
        self.blacklisted_tokens: set = set()
    
    def authenticate_guardian(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: PermissionLevel
    ) -> Dict[str, Any]:
        """ガーディアン認証"""
        try:
            # 権限チェック
            if not self.rbac_system.check_permission(
                guardian_id, user_id, ResourceType.USER_PROFILE, Action.READ
            ):
                raise AuthorizationError("指定されたユーザーへのアクセス権限がありません")
            
            # トークン生成
            access_token = self._create_access_token(guardian_id, user_id, permission_level)
            refresh_token = self._create_refresh_token(guardian_id, user_id)
            
            # 権限情報取得
            permissions = self.rbac_system.get_permission_summary(guardian_id, user_id)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "guardian_id": guardian_id,
                "user_id": user_id,
                "permission_level": permission_level.value,
                "permissions": permissions
            }
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, AuthorizationError)):
                raise
            raise AuthenticationError(f"認証処理でエラーが発生しました: {str(e)}")
    
    def grant_guardian_access(
        self,
        user_id: str,
        guardian_id: str,
        permission_level: PermissionLevel,
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """ガーディアンアクセス権付与"""
        try:
            return self.rbac_system.grant_role(
                guardian_id, user_id, permission_level, granted_by, expires_at
            )
        except Exception:
            return False
    
    def revoke_guardian_access(self, user_id: str, guardian_id: str) -> bool:
        """ガーディアンアクセス権取り消し"""
        try:
            return self.rbac_system.revoke_role(guardian_id, user_id)
        except Exception:
            return False
    
    def check_access(
        self,
        guardian_id: str,
        user_id: str,
        resource_type: ResourceType,
        action: Action
    ) -> bool:
        """アクセス権チェック"""
        return self.rbac_system.check_permission(guardian_id, user_id, resource_type, action)
    
    def get_guardian_users(self, guardian_id: str) -> List[Dict[str, Any]]:
        """ガーディアンの管理ユーザー一覧"""
        return self.rbac_system.get_guardian_users(guardian_id)
    
    def get_user_guardians(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーのガーディアン一覧"""
        return self.rbac_system.get_user_guardians(user_id)
    
    def verify_token(self, token: str) -> GuardianToken:
        """トークン検証"""
        try:
            # ブラックリストチェック
            if token in self.blacklisted_tokens:
                raise AuthenticationError("無効なトークンです")
            
            # JWT デコード
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 必須フィールドチェック
            required_fields = ["guardian_id", "user_id", "permission_level", "jti", "iat", "exp"]
            for field in required_fields:
                if field not in payload:
                    raise AuthenticationError("トークンの形式が正しくありません")
            
            # 有効期限チェック
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise AuthenticationError("トークンの有効期限が切れています")
            
            return GuardianToken(
                guardian_id=payload["guardian_id"],
                user_id=payload["user_id"],
                permission_level=payload["permission_level"],
                jti=payload["jti"],
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("トークンの有効期限が切れています")
        except jwt.InvalidTokenError:
            raise AuthenticationError("無効なトークンです")
        except Exception as e:
            raise AuthenticationError(f"トークン検証でエラーが発生しました: {str(e)}")
    
    def revoke_token(self, jti: str):
        """トークン無効化"""
        self.blacklisted_tokens.add(jti)
    
    def _create_access_token(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: PermissionLevel
    ) -> str:
        """アクセストークン作成"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "guardian_id": guardian_id,
            "user_id": user_id,
            "permission_level": permission_level.value,
            "token_type": "access",
            "jti": str(uuid.uuid4()),
            "iat": now.timestamp(),
            "exp": expire.timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, guardian_id: str, user_id: str) -> str:
        """リフレッシュトークン作成"""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "guardian_id": guardian_id,
            "user_id": user_id,
            "token_type": "refresh",
            "jti": str(uuid.uuid4()),
            "iat": now.timestamp(),
            "exp": expire.timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)


# グローバルインスタンス
guardian_auth_service = GuardianAuthService()

# FastAPI セキュリティ
security = HTTPBearer()


def get_current_guardian(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """現在のガーディアン情報取得"""
    try:
        token = guardian_auth_service.verify_token(credentials.credentials)
        
        # 権限情報取得
        permissions = rbac_system.get_permission_summary(token.guardian_id, token.user_id)
        
        return {
            "guardian_id": token.guardian_id,
            "user_id": token.user_id,
            "permission_level": token.permission_level,
            "permissions": permissions,
            "token": token
        }
        
    except Exception as e:
        if isinstance(e, (AuthenticationError, AuthorizationError)):
            raise
        raise AuthenticationError("認証情報の取得に失敗しました")


def require_view_access(
    guardian_info: Dict[str, Any] = Depends(get_current_guardian)
) -> Dict[str, Any]:
    """閲覧権限要求"""
    if not guardian_auth_service.check_access(
        guardian_info["guardian_id"],
        guardian_info["user_id"],
        ResourceType.USER_PROFILE,
        Action.READ
    ):
        raise AuthorizationError("閲覧権限がありません")
    
    return guardian_info


def require_task_edit_access(
    guardian_info: Dict[str, Any] = Depends(get_current_guardian)
) -> Dict[str, Any]:
    """タスク編集権限要求"""
    if not guardian_auth_service.check_access(
        guardian_info["guardian_id"],
        guardian_info["user_id"],
        ResourceType.TASK_DATA,
        Action.WRITE
    ):
        raise AuthorizationError("タスク編集権限がありません")
    
    return guardian_info


def require_chat_send_access(
    guardian_info: Dict[str, Any] = Depends(get_current_guardian)
) -> Dict[str, Any]:
    """チャット送信権限要求"""
    if not guardian_auth_service.check_access(
        guardian_info["guardian_id"],
        guardian_info["user_id"],
        ResourceType.CHAT_MESSAGES,
        Action.WRITE
    ):
        raise AuthorizationError("チャット送信権限がありません")
    
    return guardian_info