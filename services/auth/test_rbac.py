"""
RBAC System Simple Test

RBACシステム

Requirements: 6.1
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.rbac_system import (
    RBACSystem, PermissionLevel, ResourceType, Action
)
from shared.middleware.rbac_middleware import (
    GuardianAuthService, create_access_token, verify_access_token
)


def test_rbac_basic_functionality():
    """RBAC基本"""
    print("=== RBAC基本 ===")
    
    # RBACシステム
    rbac_system = RBACSystem()
    print(f"? RBACシステム")
    print(f"  - デフォルト: {len(rbac_system.roles)}")
    
    # ?
    test_user_id = "test_user_001"
    test_guardian_id = "test_guardian_001"
    test_granted_by = "system_admin"
    
    # 1. ログ
    print("\n1. ログ")
    success = rbac_system.grant_role(
        test_user_id,
        test_guardian_id,
        PermissionLevel.TASK_EDIT,
        test_granted_by
    )
    print(f"? ログ: {success}")
    
    # 2. ?
    print("\n2. ?")
    
    # ?
    has_read = rbac_system.check_permission(
        test_guardian_id, test_user_id,
        ResourceType.TASK_DATA, Action.READ
    )
    print(f"? タスク: {has_read}")
    
    # ?
    has_write = rbac_system.check_permission(
        test_guardian_id, test_user_id,
        ResourceType.TASK_DATA, Action.WRITE
    )
    print(f"? タスク: {has_write}")
    
    # ?
    has_chat = rbac_system.check_permission(
        test_guardian_id, test_user_id,
        ResourceType.CHAT_MESSAGES, Action.WRITE
    )
    print(f"? ?: {has_chat}")
    
    # 3. ?
    print("\n3. ?")
    summary = rbac_system.get_permission_summary(test_guardian_id, test_user_id)
    print(f"? アプリ: {summary['has_access']}")
    print(f"? ?: {summary['permission_level']}")
    print(f"? ログ: {summary['role_name']}")
    
    return rbac_system, test_user_id, test_guardian_id


def test_guardian_auth_service():
    """?"""
    print("\n=== ? ===")
    
    auth_service = GuardianAuthService()
    test_user_id = "auth_test_user"
    test_guardian_id = "auth_test_guardian"
    
    # 1. アプリ
    print("\n1. アプリ")
    success = auth_service.grant_guardian_access(
        test_user_id,
        test_guardian_id,
        PermissionLevel.CHAT_SEND,
        "system_admin"
    )
    print(f"? ?: {success}")
    
    # 2. ?
    print("\n2. ?")
    try:
        auth_result = auth_service.authenticate_guardian(
            test_guardian_id,
            test_user_id,
            PermissionLevel.CHAT_SEND
        )
        print(f"? ?")
        print(f"  - ?: {auth_result['token_type']}")
        print(f"  - ?: {auth_result['expires_in']}?")
        print(f"  - ?: {auth_result['permission_level']}")
        
        return auth_result["access_token"]
        
    except Exception as e:
        print(f"? ?: {e}")
        return None


def test_jwt_token_functionality():
    """JWT?"""
    print("\n=== JWT? ===")
    
    test_guardian_id = "jwt_test_guardian"
    test_user_id = "jwt_test_user"
    
    # 1. ?
    print("\n1. ?")
    token = create_access_token(
        test_guardian_id,
        test_user_id,
        PermissionLevel.VIEW_ONLY
    )
    print(f"? ?")
    print(f"  - ?: {len(token)}文字")
    
    # 2. ?
    print("\n2. ?")
    try:
        payload = verify_access_token(token)
        print(f"? ?")
        print(f"  - ?ID: {payload['guardian_id']}")
        print(f"  - ユーザーID: {payload['user_id']}")
        print(f"  - ?: {payload['permission_level']}")
        print(f"  - ?: {payload['type']}")
        
    except Exception as e:
        print(f"? ?: {e}")
    
    # 3. 無
    print("\n3. 無")
    try:
        invalid_payload = verify_access_token("invalid_token")
        print(f"? ?: {invalid_payload}")
    except Exception as e:
        print(f"? 無: {type(e).__name__}")


def test_multiple_guardians_scenario():
    """?"""
    print("\n=== ? ===")
    
    rbac_system = RBACSystem()
    user_id = "multi_test_user"
    
    # ?
    guardians = [
        ("parent_001", PermissionLevel.VIEW_ONLY, "?"),
        ("counselor_001", PermissionLevel.TASK_EDIT, "カスタム"),
        ("support_worker_001", PermissionLevel.CHAT_SEND, "支援")
    ]
    
    print("\n1. ?")
    for guardian_id, permission_level, description in guardians:
        success = rbac_system.grant_role(
            user_id, guardian_id, permission_level, "system_admin"
        )
        print(f"? {description}: {success}")
    
    # 2. ?
    print("\n2. ?")
    for guardian_id, permission_level, description in guardians:
        # ユーザー
        can_read_profile = rbac_system.check_permission(
            guardian_id, user_id, ResourceType.USER_PROFILE, Action.READ
        )
        
        # タスクTask-Edit?
        can_edit_tasks = rbac_system.check_permission(
            guardian_id, user_id, ResourceType.TASK_DATA, Action.WRITE
        )
        
        # ?Chat-Sendの
        can_send_chat = rbac_system.check_permission(
            guardian_id, user_id, ResourceType.CHAT_MESSAGES, Action.WRITE
        )
        
        print(f"  {description}:")
        print(f"    - プレビュー: {can_read_profile}")
        print(f"    - タスク: {can_edit_tasks}")
        print(f"    - ?: {can_send_chat}")
    
    # 3. ユーザー
    print("\n3. ユーザー")
    user_guardians = rbac_system.get_user_guardians(user_id)
    print(f"? ?: {len(user_guardians)}")
    for guardian in user_guardians:
        print(f"  - {guardian['guardian_id']}: {guardian['permission_level']}")


def test_expired_roles_scenario():
    """?"""
    print("\n=== ? ===")
    
    rbac_system = RBACSystem()
    user_id = "expire_test_user"
    guardian_id = "expire_test_guardian"
    
    # 1. ?
    print("\n1. ?")
    expired_time = datetime.now() - timedelta(hours=1)
    success = rbac_system.grant_role(
        user_id, guardian_id, PermissionLevel.VIEW_ONLY,
        "system_admin", expired_time
    )
    print(f"? ?: {success}")
    
    # 2. ?
    print("\n2. ?")
    has_permission = rbac_system.check_permission(
        guardian_id, user_id, ResourceType.USER_PROFILE, Action.READ
    )
    print(f"? ?: {has_permission} (Falseで)")
    
    # 3. ?
    print("\n3. ?")
    cleaned_count = rbac_system.cleanup_expired_roles()
    print(f"? ?: {cleaned_count}")


def test_system_statistics():
    """システム"""
    print("\n=== システム ===")
    
    rbac_system = RBACSystem()
    
    # い
    test_data = [
        ("user_001", "guardian_001", PermissionLevel.VIEW_ONLY),
        ("user_001", "guardian_002", PermissionLevel.TASK_EDIT),
        ("user_002", "guardian_001", PermissionLevel.CHAT_SEND),
        ("user_003", "guardian_003", PermissionLevel.VIEW_ONLY),
    ]
    
    for user_id, guardian_id, permission_level in test_data:
        rbac_system.grant_role(user_id, guardian_id, permission_level, "system_admin")
    
    # ?
    stats = rbac_system.export_roles_data()
    
    print(f"? システム:")
    print(f"  - ?: {len(stats['roles'])}")
    print(f"  - ユーザー: {stats['user_roles_count']}")
    print(f"  - ?: {stats['guardian_roles_count']}")
    print(f"  - アプリ: {stats['total_active_assignments']}")
    
    # ?
    print(f"\n? ログ:")
    for role_key, role_info in stats['roles'].items():
        print(f"  - {role_key}: {role_info['name']}")
        print(f"    ?: {role_info['description']}")
        print(f"    ?: {len(role_info['permissions'])}")


def main():
    """メイン"""
    print("RBAC System Test Suite")
    print("=" * 50)
    
    try:
        # 1. 基本
        rbac_system, user_id, guardian_id = test_rbac_basic_functionality()
        
        # 2. ?
        access_token = test_guardian_auth_service()
        
        # 3. JWT?
        test_jwt_token_functionality()
        
        # 4. ?
        test_multiple_guardians_scenario()
        
        # 5. ?
        test_expired_roles_scenario()
        
        # 6. システム
        test_system_statistics()
        
        print("\n" + "=" * 50)
        print("? ?RBAC?")
        print("RBACシステム")
        
        return True
        
    except Exception as e:
        print(f"\n? ?: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)