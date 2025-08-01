"""
Authentication Service Integration Tests

?

Requirements: 6.1
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.main import app
from shared.interfaces.rbac_system import PermissionLevel, ResourceType, Action


class TestAuthenticationService:
    """?"""
    
    def setup_method(self):
        """?"""
        self.client = TestClient(app)
        self.test_user_id = "test_user_001"
        self.test_guardian_id = "test_guardian_001"
        self.test_granted_by = "system_admin"
    
    def test_health_check(self):
        """ヘルパー"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth"
    
    def test_get_system_roles(self):
        """システム"""
        response = self.client.get("/auth/system/roles")
        assert response.status_code == 200
        
        data = response.json()
        assert "roles" in data
        assert "user_roles_count" in data
        assert "guardian_roles_count" in data
        
        # 3つ
        roles = data["roles"]
        assert len(roles) == 3
        assert "view-only" in roles
        assert "task-edit" in roles
        assert "chat-send" in roles
    
    def test_grant_guardian_access_success(self):
        """?"""
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.VIEW_ONLY.value,
            "granted_by": self.test_granted_by
        }
        
        response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == self.test_user_id
        assert data["guardian_id"] == self.test_guardian_id
        assert data["permission_level"] == PermissionLevel.VIEW_ONLY.value
    
    def test_grant_guardian_access_with_expiration(self):
        """?"""
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.TASK_EDIT.value,
            "granted_by": self.test_granted_by,
            "expires_at": expires_at
        }
        
        response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["permission_level"] == PermissionLevel.TASK_EDIT.value
    
    def test_guardian_login_success(self):
        """?"""
        # ま
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.CHAT_SEND.value,
            "granted_by": self.test_granted_by
        }
        
        grant_response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert grant_response.status_code == 200
        
        # ログ
        login_request = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": PermissionLevel.CHAT_SEND.value
        }
        
        response = self.client.post("/auth/guardian/login", json=login_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["guardian_id"] == self.test_guardian_id
        assert data["user_id"] == self.test_user_id
        assert data["permission_level"] == PermissionLevel.CHAT_SEND.value
        assert "permissions" in data
        
        return data["access_token"]
    
    def test_guardian_login_no_access(self):
        """?"""
        login_request = {
            "guardian_id": "nonexistent_guardian",
            "user_id": "nonexistent_user",
            "permission_level": PermissionLevel.VIEW_ONLY.value
        }
        
        response = self.client.post("/auth/guardian/login", json=login_request)
        assert response.status_code == 401  # Unauthorized
    
    def test_guardian_login_permission_mismatch(self):
        """?"""
        # View-Only?
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.VIEW_ONLY.value,
            "granted_by": self.test_granted_by
        }
        
        grant_response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert grant_response.status_code == 200
        
        # Chat-Send?
        login_request = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "permission_level": PermissionLevel.CHAT_SEND.value
        }
        
        response = self.client.post("/auth/guardian/login", json=login_request)
        assert response.status_code == 403  # Forbidden
    
    def test_permission_check(self):
        """?"""
        # Task-Edit?
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.TASK_EDIT.value,
            "granted_by": self.test_granted_by
        }
        
        grant_response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert grant_response.status_code == 200
        
        # ?
        check_request = {
            "guardian_id": self.test_guardian_id,
            "user_id": self.test_user_id,
            "resource_type": ResourceType.TASK_DATA.value,
            "action": Action.READ.value
        }
        
        response = self.client.post("/auth/permission/check", json=check_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_permission"] is True
        
        # ?
        check_request["action"] = Action.WRITE.value
        response = self.client.post("/auth/permission/check", json=check_request)
        assert response.status_code == 200
        assert response.json()["has_permission"] is True
        
        # ?
        check_request["resource_type"] = ResourceType.CHAT_MESSAGES.value
        response = self.client.post("/auth/permission/check", json=check_request)
        assert response.status_code == 200
        assert response.json()["has_permission"] is False
    
    def test_get_guardian_users(self):
        """?"""
        # ?
        user_2 = "test_user_002"
        
        grant_requests = [
            {
                "user_id": self.test_user_id,
                "guardian_id": self.test_guardian_id,
                "permission_level": PermissionLevel.VIEW_ONLY.value,
                "granted_by": self.test_granted_by
            },
            {
                "user_id": user_2,
                "guardian_id": self.test_guardian_id,
                "permission_level": PermissionLevel.TASK_EDIT.value,
                "granted_by": self.test_granted_by
            }
        ]
        
        for grant_request in grant_requests:
            response = self.client.post("/auth/guardian/grant", json=grant_request)
            assert response.status_code == 200
        
        # ユーザー
        response = self.client.get(f"/auth/guardian/{self.test_guardian_id}/users")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # ユーザー
        user_ids = [user["user_id"] for user in data]
        assert self.test_user_id in user_ids
        assert user_2 in user_ids
        
        # ?
        permission_levels = [user["permission_level"] for user in data]
        assert PermissionLevel.VIEW_ONLY.value in permission_levels
        assert PermissionLevel.TASK_EDIT.value in permission_levels
    
    def test_get_user_guardians(self):
        """ユーザー"""
        # ?
        guardian_2 = "test_guardian_002"
        
        grant_requests = [
            {
                "user_id": self.test_user_id,
                "guardian_id": self.test_guardian_id,
                "permission_level": PermissionLevel.VIEW_ONLY.value,
                "granted_by": self.test_granted_by
            },
            {
                "user_id": self.test_user_id,
                "guardian_id": guardian_2,
                "permission_level": PermissionLevel.CHAT_SEND.value,
                "granted_by": self.test_granted_by
            }
        ]
        
        for grant_request in grant_requests:
            response = self.client.post("/auth/guardian/grant", json=grant_request)
            assert response.status_code == 200
        
        # ?
        response = self.client.get(f"/auth/user/{self.test_user_id}/guardians")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # ?
        guardian_ids = [guardian["guardian_id"] for guardian in data]
        assert self.test_guardian_id in guardian_ids
        assert guardian_2 in guardian_ids
        
        # ?
        permission_levels = [guardian["permission_level"] for guardian in data]
        assert PermissionLevel.VIEW_ONLY.value in permission_levels
        assert PermissionLevel.CHAT_SEND.value in permission_levels
    
    def test_revoke_guardian_access(self):
        """?"""
        # ま
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.VIEW_ONLY.value,
            "granted_by": self.test_granted_by
        }
        
        grant_response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert grant_response.status_code == 200
        
        # ?
        users_response = self.client.get(f"/auth/guardian/{self.test_guardian_id}/users")
        assert users_response.status_code == 200
        assert len(users_response.json()) == 1
        
        # ?
        revoke_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id
        }
        
        response = self.client.post("/auth/guardian/revoke", json=revoke_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == self.test_user_id
        assert data["guardian_id"] == self.test_guardian_id
        
        # ?
        users_response = self.client.get(f"/auth/guardian/{self.test_guardian_id}/users")
        assert users_response.status_code == 200
        assert len(users_response.json()) == 0
    
    def test_cleanup_expired_roles(self):
        """?"""
        # ?
        expired_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        grant_request = {
            "user_id": self.test_user_id,
            "guardian_id": self.test_guardian_id,
            "permission_level": PermissionLevel.VIEW_ONLY.value,
            "granted_by": self.test_granted_by,
            "expires_at": expired_time
        }
        
        grant_response = self.client.post("/auth/guardian/grant", json=grant_request)
        assert grant_response.status_code == 200
        
        # ?
        response = self.client.post("/auth/system/cleanup")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["cleaned_count"] >= 1
    
    def test_authenticated_endpoints(self):
        """?"""
        # ?
        response = self.client.get("/auth/me")
        assert response.status_code == 403  # Forbidden (no auth header)
        
        # 無
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized
        
        # ?
        access_token = self.test_guardian_login_success()
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = self.client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["guardian_id"] == self.test_guardian_id
        assert data["user_id"] == self.test_user_id
        assert data["authenticated"] is True
    
    def test_permission_summary(self):
        """?"""
        # ?
        access_token = self.test_guardian_login_success()
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # ?
        response = self.client.get("/auth/permissions/summary", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["guardian_id"] == self.test_guardian_id
        assert data["user_id"] == self.test_user_id
        assert "summary" in data
        
        summary = data["summary"]
        assert summary["has_access"] is True
        assert summary["permission_level"] == PermissionLevel.CHAT_SEND.value
        assert "permissions" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])