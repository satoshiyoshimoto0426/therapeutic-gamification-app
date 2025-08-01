"""
Auth Middleware

認証ミドルウェア
Requirements: 6.1, 10.3
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.rbac_system import (
    PermissionLevel, ResourceType, Action, rbac_system
)
from shared.middleware.rbac_middleware import (
    GuardianAuthService, guardian_auth_service, AuthenticationError, AuthorizationError
)
from jwt_service import jwt_service, JWTClaims, TokenPair


class AuthService:
    """認証サービス"""
    
    def __init__(self):
        self.guardian_auth_service = guardian_auth_service
        self.jwt_service = jwt_service
        self.rbac_system = rbac_system
    
    async def authenticate_and_authorize(
        self,
        guardian_id: str,
        user_id: str,
        permission_level: PermissionLevel
    ) -> Dict[str, Any]:
        """認証と認可の統合処理"""
        try:
            # 権限チェック
            if not self.rbac_system.check_permission(
                guardian_id, user_id, ResourceType.USER_PROFILE, Action.READ
            ):
                # 権限がない場合は自動付与（開発用）
                self.rbac_system.grant_role(
                    guardian_id, user_id, permission_level, "system"
                )
            
            # トークンペア作成
            token_pair = self.jwt_service.create_token_pair(
                guardian_id=guardian_id,
                user_id=user_id,
                permission_level=permission_level.value
            )
            
            # 権限情報取得
            permissions = self.rbac_system.get_permission_summary(guardian_id, user_id)
            
            return {
                "success": True,
                "tokens": token_pair.dict(),
                "guardian_id": guardian_id,
                "user_id": user_id,
                "permission_level": permission_level.value,
                "permissions": permissions
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"認証に失敗しました: {str(e)}"
            )
    
    async def refresh_authentication(self, refresh_token: str) -> Dict[str, Any]:
        """認証リフレッシュ"""
        try:
            # トークンリフレッシュ
            new_token_pair = self.jwt_service.refresh_token(refresh_token)
            
            # リフレッシュトークンから情報取得
            claims = self.jwt_service.verify_token(refresh_token)
            
            # 権限情報取得
            permissions = self.rbac_system.get_permission_summary(
                claims.guardian_id, claims.user_id
            )
            
            return {
                "success": True,
                "tokens": new_token_pair.dict(),
                "guardian_id": claims.guardian_id,
                "user_id": claims.user_id,
                "permission_level": claims.permission_level,
                "permissions": permissions
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"トークンリフレッシュに失敗しました: {str(e)}"
            )
    
    async def logout(
        self,
        access_token_jti: str,
        refresh_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """ログアウト"""
        try:
            # アクセストークン無効化
            self.jwt_service.revoke_token(access_token_jti)
            
            # リフレッシュトークンも無効化
            if refresh_token:
                try:
                    refresh_claims = self.jwt_service.verify_token(refresh_token)
                    self.jwt_service.revoke_token(refresh_claims.jti)
                except:
                    pass  # リフレッシュトークンが無効でもログアウトは成功
            
            return {
                "success": True,
                "message": "ログアウトしました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"ログアウト処理でエラーが発生しました: {str(e)}"
            }
    
    def verify_token(self, token: str) -> JWTClaims:
        """トークン検証"""
        return self.jwt_service.verify_token(token)
    
    def check_permission(
        self,
        guardian_id: str,
        user_id: str,
        resource_type: ResourceType,
        action: Action
    ) -> bool:
        """権限チェック"""
        return self.rbac_system.check_permission(guardian_id, user_id, resource_type, action)


# グローバルインスタンス
auth_service = AuthService()

# FastAPI セキュリティ
security = HTTPBearer()


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JWTClaims:
    """現在のトークン取得"""
    try:
        return auth_service.verify_token(credentials.credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"トークン検証に失敗しました: {str(e)}"
        )


def get_optional_guardian(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """オプショナルガーディアン情報取得"""
    if not credentials:
        return None
    
    try:
        token = auth_service.verify_token(credentials.credentials)
        permissions = rbac_system.get_permission_summary(token.guardian_id, token.user_id)
        
        return {
            "guardian_id": token.guardian_id,
            "user_id": token.user_id,
            "permission_level": token.permission_level,
            "permissions": permissions,
            "token": token
        }
    except:
        return None


def require_view_only_access(
    token: JWTClaims = Depends(get_current_token)
) -> Dict[str, Any]:
    """閲覧専用アクセス要求"""
    if not auth_service.check_permission(
        token.guardian_id,
        token.user_id,
        ResourceType.USER_PROFILE,
        Action.READ
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="閲覧権限がありません"
        )
    
    permissions = rbac_system.get_permission_summary(token.guardian_id, token.user_id)
    
    return {
        "guardian_id": token.guardian_id,
        "user_id": token.user_id,
        "permission_level": token.permission_level,
        "permissions": permissions,
        "token": token
    }


def require_task_edit_access(
    token: JWTClaims = Depends(get_current_token)
) -> Dict[str, Any]:
    """タスク編集アクセス要求"""
    if not auth_service.check_permission(
        token.guardian_id,
        token.user_id,
        ResourceType.TASK_DATA,
        Action.WRITE
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="タスク編集権限がありません"
        )
    
    permissions = rbac_system.get_permission_summary(token.guardian_id, token.user_id)
    
    return {
        "guardian_id": token.guardian_id,
        "user_id": token.user_id,
        "permission_level": token.permission_level,
        "permissions": permissions,
        "token": token
    }


def require_chat_send_access(
    token: JWTClaims = Depends(get_current_token)
) -> Dict[str, Any]:
    """チャット送信アクセス要求"""
    if not auth_service.check_permission(
        token.guardian_id,
        token.user_id,
        ResourceType.CHAT_MESSAGES,
        Action.WRITE
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="チャット送信権限がありません"
        )
    
    permissions = rbac_system.get_permission_summary(token.guardian_id, token.user_id)
    
    return {
        "guardian_id": token.guardian_id,
        "user_id": token.user_id,
        "permission_level": token.permission_level,
        "permissions": permissions,
        "token": token
    }