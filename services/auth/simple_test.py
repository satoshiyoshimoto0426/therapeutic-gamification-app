"""
Simple Authentication Test

?
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.jwt_service import jwt_service, TokenType
from shared.interfaces.rbac_system import PermissionLevel


def test_jwt_basic_functionality():
    """JWT基本"""
    print("=== JWT Basic Functionality Test ===")
    
    # ?
    guardian_id = "test_guardian_001"
    user_id = "test_user_001"
    permission_level = "task-edit"
    
    try:
        # ?
        print("1. Creating token pair...")
        token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level
        )
        
        print(f"   Access token created: {len(token_pair.access_token)} chars")
        print(f"   Refresh token created: {len(token_pair.refresh_token)} chars")
        print(f"   Token type: {token_pair.token_type}")
        print(f"   Expires in: {token_pair.expires_in} seconds")
        
        # アプリ
        print("2. Verifying access token...")
        access_data = jwt_service.verify_token(token_pair.access_token)
        
        print(f"   Guardian ID: {access_data.guardian_id}")
        print(f"   User ID: {access_data.user_id}")
        print(f"   Permission Level: {access_data.permission_level}")
        print(f"   Token Type: {access_data.token_type}")
        print(f"   Issued At: {access_data.issued_at}")
        print(f"   Expires At: {access_data.expires_at}")
        
        # リスト
        print("3. Verifying refresh token...")
        refresh_data = jwt_service.verify_token(token_pair.refresh_token)
        
        print(f"   Token Type: {refresh_data.token_type}")
        print(f"   Same Guardian ID: {refresh_data.guardian_id == guardian_id}")
        print(f"   Same User ID: {refresh_data.user_id == user_id}")
        
        # ?
        print("4. Refreshing tokens...")
        new_pair = jwt_service.refresh_access_token(token_pair.refresh_token)
        
        print(f"   New access token: {len(new_pair.access_token)} chars")
        print(f"   New refresh token: {len(new_pair.refresh_token)} chars")
        print(f"   Tokens are different: {new_pair.access_token != token_pair.access_token}")
        
        # ?
        print("5. Getting token info...")
        token_info = jwt_service.get_token_info(new_pair.access_token)
        
        print(f"   Guardian ID: {token_info['guardian_id']}")
        print(f"   User ID: {token_info['user_id']}")
        print(f"   Is Expired: {token_info['is_expired']}")
        print(f"   Is Revoked: {token_info['is_revoked']}")
        
        # ?
        print("6. Revoking token...")
        revoke_success = jwt_service.revoke_token(new_pair.access_token)
        print(f"   Revocation successful: {revoke_success}")
        
        # ?
        print("7. Verifying revoked token...")
        try:
            jwt_service.verify_token(new_pair.access_token)
            print("   ERROR: Revoked token should not be valid!")
            return False
        except Exception as e:
            print(f"   Expected error: {type(e).__name__}")
        
        print("\n? All JWT tests passed!")
        return True
        
    except Exception as e:
        print(f"\n? JWT test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rbac_integration():
    """RBAC?"""
    print("\n=== RBAC Integration Test ===")
    
    try:
        from shared.interfaces.rbac_system import rbac_system, PermissionLevel, ResourceType, Action
        
        # ?
        user_id = "test_user_rbac"
        guardian_id = "test_guardian_rbac"
        permission_level = PermissionLevel.TASK_EDIT
        
        print("1. Granting RBAC role...")
        success = rbac_system.grant_role(
            user_id, guardian_id, permission_level, granted_by="test_admin"
        )
        print(f"   Role granted: {success}")
        
        print("2. Checking permissions...")
        has_view = rbac_system.check_permission(
            user_id, guardian_id, ResourceType.DASHBOARD, Action.VIEW
        )
        has_edit = rbac_system.check_permission(
            user_id, guardian_id, ResourceType.TASKS, Action.EDIT
        )
        has_send = rbac_system.check_permission(
            user_id, guardian_id, ResourceType.CHAT, Action.SEND
        )
        
        print(f"   Has VIEW permission: {has_view}")
        print(f"   Has EDIT permission: {has_edit}")
        print(f"   Has SEND permission: {has_send}")
        
        print("3. Getting user permissions...")
        permissions = rbac_system.get_user_permissions(guardian_id, user_id)
        print(f"   Permissions: {permissions}")
        
        print("4. Revoking role...")
        revoke_success = rbac_system.revoke_role(user_id, guardian_id)
        print(f"   Role revoked: {revoke_success}")
        
        print("\n? RBAC integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n? RBAC integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン"""
    print("Starting Authentication System Tests...\n")
    
    jwt_success = test_jwt_basic_functionality()
    rbac_success = test_rbac_integration()
    
    print(f"\n{'='*50}")
    print("Test Results:")
    print(f"JWT Tests: {'? PASSED' if jwt_success else '? FAILED'}")
    print(f"RBAC Tests: {'? PASSED' if rbac_success else '? FAILED'}")
    
    if jwt_success and rbac_success:
        print("\n? All authentication tests passed!")
        return True
    else:
        print("\n? Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)