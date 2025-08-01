"""
Authentication Service Integration Tests

JWT?RBAC?
Guardian Portal?

Requirements: 6.1, 10.3
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.main import app
from services.auth.jwt_service import jwt_service, TokenType
from services.auth.auth_middleware import auth_service
from shared.interfaces.rbac_system import PermissionLevel, ResourceType, Action, rbac_system


class TestAuthenticationIntegration:
    """?"""
    
    def setup_method(self):
        """?"""
        self.client = TestClient(app)
        self.test_guardian_id = "test_guardian_001"
        self.test_user_id = "test_user_001"
        self.test_permission_level = PermissionLevel.TASK_EDIT
        
        # ?
        rbac_system.grant_role(
            self.test_user_id,
            self.test_guardian_id,
            self.test_permission_level,
            granted_by="test_admin"
        )
    
    def teardown_method(self):
        """?"""
        # ?
        rbac_system.revoke_role(self.test_user_id, self.test_guardian_id)
    
    def test_jwt_token_creation(self):
        """JWT?"""
        # ログ
        login_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": self.test_permission_level.value
        }
        
        response = self.client.post("/auth/token", json=login_data)
        
        assert response.status_code == 200
        token_data = response.json()
        
        # レベル
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        assert "refresh_expires_in" in token_data
        assert token_data["token_type"] == "Bearer"
        
        # ?
        access_token_data = jwt_service.verify_token(token_data["access_token"])
        assert access_token_data.guardian_id == self.test_guardian_id
        assert access_token_data.user_id == self.test_user_id
        assert access_token_data.permission_level == self.test_permission_level.value
        assert access_token_data.token_type == TokenType.ACCESS
        
        refresh_token_data = jwt_service.verify_token(token_data["refresh_token"])
        assert refresh_token_data.token_type == TokenType.REFRESH
    
    def test_token_refresh(self):
        """?"""
        # ?
        login_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": self.test_permission_level.value
        }
        
        login_response = self.client.post("/auth/token", json=login_data)
        assert login_response.status_code == 200
        
        original_tokens = login_response.json()
        
        # ?
        refresh_data = {
            "refresh_token": original_tokens["refresh_token"]
        }
        
        refresh_response = self.client.post("/auth/token/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        new_tokens = refresh_response.json()
        
        # ?
        assert new_tokens["access_token"] != original_tokens["access_token"]
        assert new_tokens["refresh_token"] != original_tokens["refresh_token"]
        
        # ?
        new_token_data = jwt_service.verify_token(new_tokens["access_token"])
        assert new_token_data.guardian_id == self.test_guardian_id
        assert new_token_data.user_id == self.test_user_id
    
    def test_token_info_endpoint(self):
        """?"""
        # ログ
        login_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": self.test_permission_level.value
        }
        
        login_response = self.client.post("/auth/token", json=login_data)
        tokens = login_response.json()
        
        # ?
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        info_response = self.client.get("/auth/token/info", headers=headers)
        
        assert info_response.status_code == 200
        token_info = info_response.json()
        
        assert token_info["guardian_id"] == self.test_guardian_id
        assert token_info["user_id"] == self.test_user_id
        assert token_info["permission_level"] == self.test_permission_level.value
        assert token_info["token_type"] == "access"
        assert "issued_at" in token_info
        assert "expires_at" in token_info
        assert "jti" in token_info
        assert token_info["is_expired"] == False
    
    def test_protected_endpoint_access(self):
        """?"""
        # ログ
        login_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": self.test_permission_level.value
        }
        
        login_response = self.client.post("/auth/token", json=login_data)
        tokens = login_response.json()
        
        # ?
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = self.client.get("/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        user_info = me_response.json()
        
        assert user_info["guardian_id"] == self.test_guardian_id
        assert user_info["user_id"] == self.test_user_id
        assert user_info["authenticated"] == True
        
        # ?
        no_auth_response = self.client.get("/auth/me")
        assert no_auth_response.status_code == 401
    
    def test_permission_level_enforcement(self):
        """?"""
        # VIEW_ONLY?
        view_only_guardian = "view_only_guardian"
        rbac_system.grant_role(
            self.test_user_id,
            view_only_guardian,
            PermissionLevel.VIEW_ONLY,
            granted_by="test_admin"
        )
        
        try:
            # VIEW_ONLY?
            login_data = {
                "guardian_id": view_only_guardian,
                "user_id": self.test_user_id,
                "permission_level": PermissionLevel.VIEW_ONLY.value
            }
            
            login_response = self.client.post("/auth/token", json=login_data)
            assert login_response.status_code == 200
            
            tokens = login_response.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            # ?VIEW_ONLY?
            summary_response = self.client.get("/auth/permissions/summary", headers=headers)
            assert summary_response.status_code == 200
            
            # ?
            # こ
            
        finally:
            rbac_system.revoke_role(self.test_user_id, view_only_guardian)
    
    def test_token_revocation(self):
        """?"""
        # ログ
        login_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": self.test_permission_level.value
        }
        
        login_response = self.client.post("/auth/token", json=login_data)
        tokens = login_response.json()
        
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # ?
        me_response = self.client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # ?
        logout_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        logout_response = self.client.post("/auth/token/revoke", json=logout_data, headers=headers)
        assert logout_response.status_code == 200
        
        logout_result = logout_response.json()
        assert logout_result["success"] == True
    
    def test_invalid_token_handling(self):
        """無"""
        # 無
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        response = self.client.get("/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # ?
        expired_token = jwt_service.create_access_token(
            self.test_guardian_id,
            self.test_user_id,
            self.test_permission_level.value
        )
        
        # 実装
        # こ
        malformed_headers = {"Authorization": "Bearer malformed.token.here"}
        response = self.client.get("/auth/me", headers=malformed_headers)
        assert response.status_code == 401
    
    def test_permission_check_endpoint(self):
        """?"""
        permission_check_data = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "resource_type": ResourceType.DASHBOARD.value,
            "action": Action.VIEW.value
        }
        
        response = self.client.post("/auth/permission/check", json=permission_check_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "has_permission" in result
        assert result["guardian_id"] == self.test_guardian_id
        assert result["user_id"] == self.test_user_id
    
    def test_guardian_user_management(self):
        """?"""
        # ?
        response = self.client.get(f"/auth/guardian/{self.test_guardian_id}/users")
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        
        # ユーザー
        response = self.client.get(f"/auth/user/{self.test_user_id}/guardians")
        assert response.status_code == 200
        
        guardians = response.json()
        assert isinstance(guardians, list)
    
    def test_system_management_endpoints(self):
        """システム"""
        # システム
        response = self.client.get("/auth/system/roles")
        assert response.status_code == 200
        
        roles_data = response.json()
        assert isinstance(roles_data, dict)
        
        # ?
        response = self.client.post("/auth/system/cleanup")
        assert response.status_code == 200
        
        cleanup_result = response.json()
        assert cleanup_result["success"] == True
        assert "cleaned_count" in cleanup_result
    
    def test_health_check(self):
        """ヘルパー"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "auth"


class TestJWTServiceUnit:
    """JWT?"""
    
    def setup_method(self):
        """?"""
        self.test_guardian_id = "unit_test_guardian"
        self.test_user_id = "unit_test_user"
        self.test_permission_level = "task-edit"
    
    def test_token_pair_creation(self):
        """?"""
        token_pair = jwt_service.create_token_pair(
            self.test_guardian_id,
            self.test_user_id,
            self.test_permission_level
        )
        
        assert token_pair.access_token
        assert token_pair.refresh_token
        assert token_pair.token_type == "Bearer"
        assert token_pair.expires_in > 0
        assert token_pair.refresh_expires_in > 0
        
        # アプリ
        access_data = jwt_service.verify_token(token_pair.access_token)
        assert access_data.guardian_id == self.test_guardian_id
        assert access_data.user_id == self.test_user_id
        assert access_data.token_type == TokenType.ACCESS
        
        # リスト
        refresh_data = jwt_service.verify_token(token_pair.refresh_token)
        assert refresh_data.guardian_id == self.test_guardian_id
        assert refresh_data.user_id == self.test_user_id
        assert refresh_data.token_type == TokenType.REFRESH
    
    def test_token_refresh_flow(self):
        """?"""
        # ?
        original_pair = jwt_service.create_token_pair(
            self.test_guardian_id,
            self.test_user_id,
            self.test_permission_level
        )
        
        # ?
        new_pair = jwt_service.refresh_access_token(original_pair.refresh_token)
        
        # ?
        assert new_pair.access_token != original_pair.access_token
        assert new_pair.refresh_token != original_pair.refresh_token
        
        # ?
        new_access_data = jwt_service.verify_token(new_pair.access_token)
        assert new_access_data.guardian_id == self.test_guardian_id
        assert new_access_data.user_id == self.test_user_id
    
    def test_token_revocation(self):
        """?"""
        token_pair = jwt_service.create_token_pair(
            self.test_guardian_id,
            self.test_user_id,
            self.test_permission_level
        )
        
        # ?
        token_data = jwt_service.verify_token(token_pair.access_token)
        assert token_data.guardian_id == self.test_guardian_id
        
        # ?
        success = jwt_service.revoke_token(token_pair.access_token)
        assert success == True
        
        # ?
        with pytest.raises(Exception):  # HTTPExceptionまJWTエラー
            jwt_service.verify_token(token_pair.access_token)
    
    def test_token_info_extraction(self):
        """?"""
        token_pair = jwt_service.create_token_pair(
            self.test_guardian_id,
            self.test_user_id,
            self.test_permission_level
        )
        
        token_info = jwt_service.get_token_info(token_pair.access_token)
        
        assert token_info["guardian_id"] == self.test_guardian_id
        assert token_info["user_id"] == self.test_user_id
        assert token_info["permission_level"] == self.test_permission_level
        assert token_info["token_type"] == "access"
        assert "issued_at" in token_info
        assert "expires_at" in token_info
        assert "jti" in token_info
        assert token_info["is_expired"] == False
        assert token_info["is_revoked"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])