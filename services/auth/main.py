"""
Authentication Service

Guardian/Support System Portal?
RBAC?JWT?

Requirements: 6.1, 10.3
"""

from fastapi import FastAPI, HTTPException, Depends, Body, Path, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.rbac_system import (
    RBACSystem, PermissionLevel, ResourceType, Action,
    rbac_system
)
from shared.middleware.rbac_middleware import (
    GuardianAuthService, guardian_auth_service,
    get_current_guardian, require_view_access, require_task_edit_access,
    require_chat_send_access, AuthenticationError, AuthorizationError
)
from services.auth.jwt_service import jwt_service, TokenPair
from services.auth.auth_middleware import (
    auth_service, get_current_token, get_optional_guardian,
    require_view_only_access, require_task_edit_access as require_task_edit,
    require_chat_send_access as require_chat_send
)

app = FastAPI(
    title="Authentication Service",
    description="Guardian/Support System Portal?",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ?
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class GuardianLoginRequest(BaseModel):
    """?"""
    guardian_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    user_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    permission_level: PermissionLevel = Field(..., description="?")


class TokenRefreshRequest(BaseModel):
    """?"""
    refresh_token: str = Field(..., description="リスト")


class LogoutRequest(BaseModel):
    """ログ"""
    refresh_token: Optional[str] = Field(None, description="リスト")


class TokenResponse(BaseModel):
    """?"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int


class TokenInfoResponse(BaseModel):
    """?"""
    guardian_id: str
    user_id: str
    permission_level: str
    token_type: str
    issued_at: str
    expires_at: str
    jti: str
    is_expired: bool
    is_revoked: bool


class GrantAccessRequest(BaseModel):
    """アプリ"""
    user_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    guardian_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    permission_level: PermissionLevel = Field(..., description="?")
    granted_by: str = Field(..., min_length=1, max_length=50, description="?")
    expires_at: Optional[datetime] = Field(None, description="?")


class RevokeAccessRequest(BaseModel):
    """アプリ"""
    user_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    guardian_id: str = Field(..., min_length=1, max_length=50, description="?ID")


class PermissionCheckRequest(BaseModel):
    """?"""
    guardian_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    user_id: str = Field(..., min_length=1, max_length=50, description="?ID")
    resource_type: ResourceType = Field(..., description="リスト")
    action: Action = Field(..., description="アプリ")


class AuthResponse(BaseModel):
    """?"""
    access_token: str
    token_type: str
    expires_in: int
    guardian_id: str
    user_id: str
    permission_level: str
    permissions: Dict[str, Any]


class GuardianInfo(BaseModel):
    """?"""
    guardian_id: str
    permission_level: str
    role_name: str
    granted_at: str
    expires_at: Optional[str]


class UserInfo(BaseModel):
    """ユーザー"""
    user_id: str
    permission_level: str
    role_name: str
    granted_at: str
    expires_at: Optional[str]
    allowed_actions: Dict[str, List[str]]


# JWT Token Endpoints
@app.post("/auth/token", response_model=TokenResponse)
async def create_token(request: GuardianLoginRequest = Body(...)) -> TokenResponse:
    """
    JWT?
    
    Args:
        request: ログ
        
    Returns:
        TokenResponse: JWT?
        
    Raises:
        HTTPException: ?
    """
    try:
        # 入力
        if not request.guardian_id or len(request.guardian_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Guardian ID is required"
            )
        
        if not request.user_id or len(request.user_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        # ?
        auth_result = await auth_service.authenticate_and_authorize(
            request.guardian_id.strip(),
            request.user_id.strip(),
            request.permission_level
        )
        
        return TokenResponse(**auth_result["tokens"])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token creation error: {str(e)}"
        )


@app.post("/auth/token/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest = Body(...)) -> TokenResponse:
    """
    JWT?
    
    Args:
        request: ?
        
    Returns:
        TokenResponse: ?JWT?
        
    Raises:
        HTTPException: ?
    """
    try:
        # 入力
        if not request.refresh_token or len(request.refresh_token.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # リスト
        try:
            # ?JWT?
            token_parts = request.refresh_token.split('.')
            if len(token_parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid refresh token format"
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token format"
            )
        
        refresh_result = await auth_service.refresh_authentication(request.refresh_token.strip())
        return TokenResponse(**refresh_result["tokens"])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh error: {str(e)}"
        )


@app.post("/auth/token/revoke")
async def revoke_token(
    request: LogoutRequest = Body(...),
    current_token: str = Depends(get_current_token)
) -> Dict[str, Any]:
    """
    JWT?
    
    Args:
        request: ログ
        current_token: ?
        
    Returns:
        Dict[str, Any]: ログ
    """
    try:
        logout_result = await auth_service.logout(
            current_token.jti if hasattr(current_token, 'jti') else str(current_token),
            request.refresh_token
        )
        return logout_result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Logout error: {str(e)}"
        }


@app.get("/auth/token/info", response_model=TokenInfoResponse)
async def get_token_info(
    current_token = Depends(get_current_token)
) -> TokenInfoResponse:
    """
    ?
    
    Args:
        current_token: ?
        
    Returns:
        TokenInfoResponse: ?
    """
    return TokenInfoResponse(
        guardian_id=current_token.guardian_id,
        user_id=current_token.user_id,
        permission_level=current_token.permission_level,
        token_type=current_token.token_type.value,
        issued_at=current_token.issued_at.isoformat(),
        expires_at=current_token.expires_at.isoformat(),
        jti=current_token.jti,
        is_expired=current_token.expires_at < datetime.utcnow(),
        is_revoked=False  # TODO: 実装
    )


# Authentication Endpoints
@app.post("/auth/guardian/login", response_model=AuthResponse)
async def guardian_login(request: GuardianLoginRequest = Body(...)) -> AuthResponse:
    """
    ?
    
    Args:
        request: ログ
        
    Returns:
        AuthResponse: ?
        
    Raises:
        HTTPException: ?
    """
    try:
        auth_result = guardian_auth_service.authenticate_guardian(
            request.guardian_id,
            request.user_id,
            request.permission_level
        )
        
        return AuthResponse(**auth_result)
        
    except (AuthenticationError, AuthorizationError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )


@app.post("/auth/guardian/grant")
async def grant_guardian_access(request: GrantAccessRequest = Body(...)) -> Dict[str, Any]:
    """
    ?
    
    Args:
        request: ?
        
    Returns:
        Dict[str, Any]: ?
        
    Raises:
        HTTPException: ?
    """
    try:
        success = guardian_auth_service.grant_guardian_access(
            request.user_id,
            request.guardian_id,
            request.permission_level,
            request.granted_by,
            request.expires_at
        )
        
        if success:
            return {
                "success": True,
                "message": "Guardian access granted successfully",
                "user_id": request.user_id,
                "guardian_id": request.guardian_id,
                "permission_level": request.permission_level.value
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to grant guardian access"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grant access error: {str(e)}"
        )


@app.post("/auth/guardian/revoke")
async def revoke_guardian_access(request: RevokeAccessRequest = Body(...)) -> Dict[str, Any]:
    """
    ?
    
    Args:
        request: ?
        
    Returns:
        Dict[str, Any]: ?
        
    Raises:
        HTTPException: ?
    """
    try:
        success = guardian_auth_service.revoke_guardian_access(
            request.user_id,
            request.guardian_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Guardian access revoked successfully",
                "user_id": request.user_id,
                "guardian_id": request.guardian_id
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to revoke guardian access"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Revoke access error: {str(e)}"
        )


# Permission Check Endpoints
@app.post("/auth/permission/check")
async def check_permission(request: PermissionCheckRequest = Body(...)) -> Dict[str, Any]:
    """
    ?
    
    Args:
        request: ?
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        has_permission = guardian_auth_service.check_access(
            request.guardian_id,
            request.user_id,
            request.resource_type,
            request.action
        )
        
        return {
            "has_permission": has_permission,
            "guardian_id": request.guardian_id,
            "user_id": request.user_id,
            "resource_type": request.resource_type.value,
            "action": request.action.value
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission check error: {str(e)}"
        )


@app.get("/auth/guardian/{guardian_id}/users", response_model=List[UserInfo])
async def get_guardian_users(
    guardian_id: str = Path(..., description="?ID", min_length=1, max_length=50)
) -> List[UserInfo]:
    """
    ?
    
    Args:
        guardian_id: ?ID
        
    Returns:
        List[UserInfo]: ユーザー
    """
    try:
        users = guardian_auth_service.get_guardian_users(guardian_id)
        return [UserInfo(**user) for user in users]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get guardian users error: {str(e)}"
        )


@app.get("/auth/user/{user_id}/guardians", response_model=List[GuardianInfo])
async def get_user_guardians(
    user_id: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> List[GuardianInfo]:
    """
    ユーザー
    
    Args:
        user_id: ユーザーID
        
    Returns:
        List[GuardianInfo]: ?
    """
    try:
        guardians = guardian_auth_service.get_user_guardians(user_id)
        return [GuardianInfo(**guardian) for guardian in guardians]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get user guardians error: {str(e)}"
        )


# Protected Endpoints (require authentication)
@app.get("/auth/me")
async def get_current_user_info(
    guardian_info: Dict[str, Any] = Depends(get_current_guardian)
) -> Dict[str, Any]:
    """
    ?
    
    Args:
        guardian_info: ?
        
    Returns:
        Dict[str, Any]: ?
    """
    return {
        "guardian_id": guardian_info["guardian_id"],
        "user_id": guardian_info["user_id"],
        "permission_level": guardian_info["permission_level"],
        "permissions": guardian_info["permissions"],
        "authenticated": True
    }


@app.get("/auth/permissions/summary")
async def get_permission_summary(
    guardian_info: Dict[str, Any] = Depends(get_current_guardian)
) -> Dict[str, Any]:
    """
    ?
    
    Args:
        guardian_info: ?
        
    Returns:
        Dict[str, Any]: ?
    """
    permission_summary = rbac_system.get_permission_summary(
        guardian_info["guardian_id"],
        guardian_info["user_id"]
    )
    
    return {
        "guardian_id": guardian_info["guardian_id"],
        "user_id": guardian_info["user_id"],
        "summary": permission_summary
    }


# System Management Endpoints
@app.get("/auth/system/roles")
async def get_system_roles() -> Dict[str, Any]:
    """
    システム
    
    Returns:
        Dict[str, Any]: システム
    """
    try:
        roles_data = rbac_system.export_roles_data()
        return roles_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get system roles error: {str(e)}"
        )


@app.post("/auth/system/cleanup")
async def cleanup_expired_roles() -> Dict[str, Any]:
    """
    ?
    
    Returns:
        Dict[str, Any]: ?
    """
    try:
        cleaned_count = rbac_system.cleanup_expired_roles()
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} expired roles",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup error: {str(e)}"
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """ヘルパー"""
    return {"status": "healthy", "service": "auth"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)