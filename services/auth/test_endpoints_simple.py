"""
?

?
?6.1, 10.3に

Requirements: 6.1, 10.3
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.jwt_service import jwt_service
from shared.interfaces.rbac_system import PermissionLevel, rbac_system


def test_jwt_service_endpoints():
    """JWT?"""
    print("=== JWT? ===")
    
    try:
        guardian_id = "test_guardian_001"
        user_id = "test_user_001"
        permission_level = PermissionLevel.TASK_EDIT.value
        
        # 1. ?
        token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level
        )
        
        print(f"? ログ: 成")
        print(f"  - アプリ: {token_pair.access_token[:20]}...")
        print(f"  - リスト: {token_pair.refresh_token[:20]}...")
        print(f"  - ?: {token_pair.expires_in}?")
        
        # 2. ?
        access_token_data = jwt_service.verify_token(token_pair.access_token)
        print(f"? ?: 成")
        print(f"  - Guardian ID: {access_token_data.guardian_id}")
        print(f"  - User ID: {access_token_data.user_id}")
        print(f"  - Permission Level: {access_token_data.permission_level}")
        
        # 3. ?
        new_token_pair = jwt_service.refresh_access_token(token_pair.refresh_token)
        print(f"? ?: 成")
        print(f"  - ?: {new_token_pair.access_token[:20]}...")
        
        # 4. ?
        token_info = jwt_service.get_token_info(new_token_pair.access_token)
        print(f"? ?: 成")
        print(f"  - JTI: {token_info['jti']}")
        print(f"  - 発: {token_info['issued_at']}")
        print(f"  - ?: {token_info['expires_at']}")
        
        # 5. ?
        revoke_success = jwt_service.revoke_token(new_token_pair.access_token)
        print(f"? ログ: {'成' if revoke_success else '?'}")
        
        return True
        
    except Exception as e:
        print(f"? JWT?: {str(e)}")
        return False


def test_rbac_system_basic():
    """RBACシステム"""
    print("\n=== RBACシステム ===")
    
    try:
        # 1. デフォルト
        roles_data = rbac_system.export_roles_data()
        print(f"? デフォルト: {len(roles_data['roles'])}")
        
        for role_key, role_info in roles_data['roles'].items():
            print(f"  - {role_key}: {role_info['name']} ({role_info['description']})")
        
        # 2. ?
        test_guardian_id = "test_guardian_rbac"
        test_user_id = "test_user_rbac"
        
        grant_success = rbac_system.grant_role(
            test_user_id, test_guardian_id, 
            PermissionLevel.TASK_EDIT, "system_test"
        )
        print(f"? ログ: {'成' if grant_success else '?'}")
        
        # 3. ?
        from shared.interfaces.rbac_system import ResourceType, Action
        
        has_permission = rbac_system.check_permission(
            test_guardian_id, test_user_id,
            ResourceType.TASK_DATA, Action.READ
        )
        print(f"? ?: {'許' if has_permission else '?'}")
        
        # 4. ?
        permission_summary = rbac_system.get_permission_summary(
            test_guardian_id, test_user_id
        )
        print(f"? ?: {'成' if permission_summary.get('has_access') else '?'}")
        
        # 5. ログ
        revoke_success = rbac_system.revoke_role(test_user_id, test_guardian_id)
        print(f"? ログ: {'成' if revoke_success else '?'}")
        
        return True
        
    except Exception as e:
        print(f"? RBACシステム: {str(e)}")
        return False


def test_authentication_flow_simulation():
    """?"""
    print("\n=== ? ===")
    
    try:
        # システム: Guardian Portal ログ
        guardian_id = "guardian_portal_001"
        user_id = "managed_user_001"
        permission_level = PermissionLevel.CHAT_SEND
        
        print(f"システム:")
        print(f"  Guardian ID: {guardian_id}")
        print(f"  User ID: {user_id}")
        print(f"  Permission Level: {permission_level.value}")
        
        # 1. RBACシステム
        rbac_system.grant_role(
            user_id, guardian_id, permission_level, "admin"
        )
        print(f"? Step 1: RBAC?")
        
        # 2. ログJWT?
        token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level.value
        )
        print(f"? Step 2: ログJWT?")
        
        # 3. ?
        token_data = jwt_service.verify_token(token_pair.access_token)
        print(f"? Step 3: ?")
        
        # 4. ?
        from shared.interfaces.rbac_system import ResourceType, Action
        
        has_chat_permission = rbac_system.check_permission(
            guardian_id, user_id, ResourceType.CHAT_MESSAGES, Action.WRITE
        )
        print(f"? Step 4: ?: {'許' if has_chat_permission else '?'}")
        
        # 5. ?
        new_token_pair = jwt_service.refresh_access_token(token_pair.refresh_token)
        print(f"? Step 5: ?")
        
        # 6. ログ
        jwt_service.revoke_token(new_token_pair.access_token)
        jwt_service.revoke_token(new_token_pair.refresh_token)
        print(f"? Step 6: ログ")
        
        # 7. ?
        rbac_system.revoke_role(user_id, guardian_id)
        print(f"? Step 7: ?")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def test_error_scenarios():
    """エラー"""
    print("\n=== エラー ===")
    
    try:
        # 1. 無
        try:
            jwt_service.verify_token("invalid.jwt.token")
            print("? 無")
            return False
        except:
            print("? 無")
        
        # 2. ?Guardianで
        from shared.interfaces.rbac_system import ResourceType, Action
        
        has_permission = rbac_system.check_permission(
            "nonexistent_guardian", "nonexistent_user",
            ResourceType.TASK_DATA, Action.READ
        )
        if not has_permission:
            print("? ?Guardianの")
        else:
            print("? ?Guardianに")
            return False
        
        # 3. ?
        token = jwt_service.create_access_token("test_guardian", "test_user", "view-only")
        jwt_service.revoke_token(token)
        
        try:
            jwt_service.verify_token(token)
            print("? ?")
            return False
        except:
            print("? ?")
        
        return True
        
    except Exception as e:
        print(f"? エラー: {str(e)}")
        return False


def run_endpoint_tests():
    """エラー"""
    print("=== ? ===")
    
    tests = [
        ("JWT?", test_jwt_service_endpoints),
        ("RBACシステム", test_rbac_system_basic),
        ("?", test_authentication_flow_simulation),
        ("エラー", test_error_scenarios),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"? {test_name}?: {str(e)}")
    
    print(f"\n=== エラー: {passed}/{total} 成 ===")
    
    if passed == total:
        print("? ?")
        return True
    else:
        print("? 一般")
        return False


if __name__ == "__main__":
    success = run_endpoint_tests()
    exit(0 if success else 1)