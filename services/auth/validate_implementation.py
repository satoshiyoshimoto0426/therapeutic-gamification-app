"""
Authentication Service Implementation Validation

?

Requirements: 6.1
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.rbac_system import (
    RBACSystem, PermissionLevel, ResourceType, Action,
    rbac_system
)
from shared.middleware.rbac_middleware import (
    GuardianAuthService, guardian_auth_service,
    create_access_token, verify_access_token,
    AuthenticationError, AuthorizationError
)


def validate_rbac_system_initialization():
    """RBACシステム"""
    print("=== RBACシステム ===")
    
    # デフォルト
    expected_roles = [
        PermissionLevel.VIEW_ONLY.value,
        PermissionLevel.TASK_EDIT.value,
        PermissionLevel.CHAT_SEND.value
    ]
    
    print(f"? ?: {len(expected_roles)}")
    print(f"? 実装: {len(rbac_system.roles)}")
    
    for role_key in expected_roles:
        if role_key in rbac_system.roles:
            role = rbac_system.roles[role_key]
            print(f"  - {role_key}: {role.name} ?")
        else:
            print(f"  - {role_key}: ? ?")
            return False
    
    # ?
    print("\n?:")
    
    # View-Only?
    view_only_role = rbac_system.roles[PermissionLevel.VIEW_ONLY.value]
    view_only_checks = [
        (ResourceType.USER_PROFILE, Action.READ, True),
        (ResourceType.TASK_DATA, Action.WRITE, False),
        (ResourceType.CHAT_MESSAGES, Action.WRITE, False)
    ]
    
    print(f"  View-Only ({view_only_role.name}):")
    for resource, action, expected in view_only_checks:
        actual = view_only_role.has_permission(resource, action)
        status = "?" if actual == expected else "?"
        print(f"    - {resource.value}:{action.value} = {actual} {status}")
    
    # Task-Edit?
    task_edit_role = rbac_system.roles[PermissionLevel.TASK_EDIT.value]
    task_edit_checks = [
        (ResourceType.USER_PROFILE, Action.READ, True),
        (ResourceType.TASK_DATA, Action.WRITE, True),
        (ResourceType.CHAT_MESSAGES, Action.WRITE, False)
    ]
    
    print(f"  Task-Edit ({task_edit_role.name}):")
    for resource, action, expected in task_edit_checks:
        actual = task_edit_role.has_permission(resource, action)
        status = "?" if actual == expected else "?"
        print(f"    - {resource.value}:{action.value} = {actual} {status}")
    
    # Chat-Send?
    chat_send_role = rbac_system.roles[PermissionLevel.CHAT_SEND.value]
    chat_send_checks = [
        (ResourceType.USER_PROFILE, Action.READ, True),
        (ResourceType.TASK_DATA, Action.WRITE, True),
        (ResourceType.CHAT_MESSAGES, Action.WRITE, True)
    ]
    
    print(f"  Chat-Send ({chat_send_role.name}):")
    for resource, action, expected in chat_send_checks:
        actual = chat_send_role.has_permission(resource, action)
        status = "?" if actual == expected else "?"
        print(f"    - {resource.value}:{action.value} = {actual} {status}")
    
    return True


def validate_guardian_auth_service():
    """?"""
    print("\n=== ? ===")
    
    test_user_id = "validation_user_001"
    test_guardian_id = "validation_guardian_001"
    
    # 1. アプリ
    print("\n1. アプリ")
    success = guardian_auth_service.grant_guardian_access(
        test_user_id,
        test_guardian_id,
        PermissionLevel.TASK_EDIT,
        "validation_admin"
    )
    print(f"? ?: {success}")
    
    if not success:
        print("? ?")
        return False
    
    # 2. ?
    print("\n2. ?")
    try:
        auth_result = guardian_auth_service.authenticate_guardian(
            test_guardian_id,
            test_user_id,
            PermissionLevel.TASK_EDIT
        )
        
        print("? ?")
        print(f"  - アプリ: {len(auth_result['access_token'])}文字")
        print(f"  - ?: {auth_result['token_type']}")
        print(f"  - ?: {auth_result['expires_in']}?")
        print(f"  - ?ID: {auth_result['guardian_id']}")
        print(f"  - ユーザーID: {auth_result['user_id']}")
        print(f"  - ?: {auth_result['permission_level']}")
        
        access_token = auth_result['access_token']
        
    except Exception as e:
        print(f"? ?: {e}")
        return False
    
    # 3. ?
    print("\n3. ?")
    try:
        invalid_auth = guardian_auth_service.authenticate_guardian(
            test_guardian_id,
            test_user_id,
            PermissionLevel.CHAT_SEND  # ?
        )
        print("? ?")
        return False
        
    except AuthorizationError:
        print("? ?")
    except Exception as e:
        print(f"? ?: {e}")
        return False
    
    # 4. アプリ
    print("\n4. アプリ")
    
    # 許
    allowed_checks = [
        (ResourceType.USER_PROFILE, Action.READ),
        (ResourceType.TASK_DATA, Action.READ),
        (ResourceType.TASK_DATA, Action.WRITE)
    ]
    
    for resource, action in allowed_checks:
        has_access = guardian_auth_service.check_access(
            test_guardian_id, test_user_id, resource, action
        )
        status = "?" if has_access else "?"
        print(f"  - {resource.value}:{action.value} = {has_access} {status}")
    
    # 許
    denied_checks = [
        (ResourceType.CHAT_MESSAGES, Action.WRITE),
        (ResourceType.TASK_DATA, Action.DELETE)
    ]
    
    for resource, action in denied_checks:
        has_access = guardian_auth_service.check_access(
            test_guardian_id, test_user_id, resource, action
        )
        status = "?" if not has_access else "?"
        print(f"  - {resource.value}:{action.value} = {has_access} {status}")
    
    # 5. ユーザー
    print("\n5. ユーザー")
    
    guardian_users = guardian_auth_service.get_guardian_users(test_guardian_id)
    print(f"? ?: {len(guardian_users)}")
    
    user_guardians = guardian_auth_service.get_user_guardians(test_user_id)
    print(f"? ユーザー: {len(user_guardians)}")
    
    return True, access_token


def validate_jwt_token_system():
    """JWT?"""
    print("\n=== JWT? ===")
    
    test_guardian_id = "jwt_validation_guardian"
    test_user_id = "jwt_validation_user"
    
    # 1. ?
    print("\n1. ?")
    token = create_access_token(
        test_guardian_id,
        test_user_id,
        PermissionLevel.VIEW_ONLY
    )
    
    print(f"? ?")
    print(f"  - ?: {len(token)}文字")
    print(f"  - ?: {token[:20]}...")
    
    # 2. ?
    print("\n2. ?")
    try:
        payload = verify_access_token(token)
        
        print("? ?")
        print(f"  - ?ID: {payload['guardian_id']}")
        print(f"  - ユーザーID: {payload['user_id']}")
        print(f"  - ?: {payload['permission_level']}")
        print(f"  - ?: {payload['type']}")
        print(f"  - 発: {datetime.fromtimestamp(payload['iat'])}")
        print(f"  - ?: {datetime.fromtimestamp(payload['exp'])}")
        
    except Exception as e:
        print(f"? ?: {e}")
        return False
    
    # 3. 無
    print("\n3. 無")
    invalid_tokens = [
        "invalid_token",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
        ""
    ]
    
    for invalid_token in invalid_tokens:
        try:
            invalid_payload = verify_access_token(invalid_token)
            print(f"? 無: {invalid_token}")
            return False
        except AuthenticationError:
            print(f"? 無: {invalid_token[:20]}...")
        except Exception as e:
            print(f"? 無: {type(e).__name__}")
    
    # 4. ?
    print("\n4. ?")
    # ?
    print("? ?JWT?")
    
    return True


def validate_permission_scenarios():
    """?"""
    print("\n=== ? ===")
    
    # ?
    scenarios = [
        {
            "name": "?",
            "user_id": "child_001",
            "guardian_id": "parent_001",
            "permission_level": PermissionLevel.VIEW_ONLY,
            "expected_permissions": {
                (ResourceType.USER_PROFILE, Action.READ): True,
                (ResourceType.PROGRESS_DATA, Action.READ): True,
                (ResourceType.TASK_DATA, Action.WRITE): False,
                (ResourceType.CHAT_MESSAGES, Action.WRITE): False
            }
        },
        {
            "name": "カスタム",
            "user_id": "client_001",
            "guardian_id": "counselor_001",
            "permission_level": PermissionLevel.TASK_EDIT,
            "expected_permissions": {
                (ResourceType.USER_PROFILE, Action.READ): True,
                (ResourceType.TASK_DATA, Action.READ): True,
                (ResourceType.TASK_DATA, Action.WRITE): True,
                (ResourceType.CHAT_MESSAGES, Action.WRITE): False
            }
        },
        {
            "name": "支援",
            "user_id": "support_user_001",
            "guardian_id": "support_worker_001",
            "permission_level": PermissionLevel.CHAT_SEND,
            "expected_permissions": {
                (ResourceType.USER_PROFILE, Action.READ): True,
                (ResourceType.TASK_DATA, Action.WRITE): True,
                (ResourceType.CHAT_MESSAGES, Action.WRITE): True,
                (ResourceType.REPORTS, Action.READ): True
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}システム:")
        
        # ?
        success = guardian_auth_service.grant_guardian_access(
            scenario['user_id'],
            scenario['guardian_id'],
            scenario['permission_level'],
            "scenario_admin"
        )
        
        if not success:
            print(f"? ?")
            continue
        
        print(f"? ?")
        
        # ?
        all_correct = True
        for (resource, action), expected in scenario['expected_permissions'].items():
            actual = guardian_auth_service.check_access(
                scenario['guardian_id'],
                scenario['user_id'],
                resource,
                action
            )
            
            status = "?" if actual == expected else "?"
            print(f"  - {resource.value}:{action.value} = {actual} {status}")
            
            if actual != expected:
                all_correct = False
        
        if not all_correct:
            print(f"? {scenario['name']}システム")
            return False
    
    return True


def validate_system_robustness():
    """システム"""
    print("\n=== システム ===")
    
    # 1. ?
    print("\n1. ?")
    
    nonexistent_checks = [
        ("nonexistent_guardian", "nonexistent_user"),
        ("real_guardian", "nonexistent_user"),
        ("nonexistent_guardian", "real_user")
    ]
    
    for guardian_id, user_id in nonexistent_checks:
        has_permission = guardian_auth_service.check_access(
            guardian_id, user_id, ResourceType.USER_PROFILE, Action.READ
        )
        status = "?" if not has_permission else "?"
        print(f"  - {guardian_id}?{user_id}: {has_permission} {status}")
    
    # 2. ?
    print("\n2. ?")
    
    expired_user = "expired_test_user"
    expired_guardian = "expired_test_guardian"
    
    # ?
    expired_time = datetime.now() - timedelta(hours=1)
    rbac_system.grant_role(
        expired_user, expired_guardian,
        PermissionLevel.VIEW_ONLY, "test_admin",
        expired_time
    )
    
    # ?
    has_expired_permission = guardian_auth_service.check_access(
        expired_guardian, expired_user,
        ResourceType.USER_PROFILE, Action.READ
    )
    
    status = "?" if not has_expired_permission else "?"
    print(f"  - ?: {has_expired_permission} {status}")
    
    # ?
    cleaned_count = rbac_system.cleanup_expired_roles()
    print(f"  - ?: {cleaned_count}")
    
    # 3. ?
    print("\n3. ?")
    
    import time
    
    # 100?
    start_time = time.time()
    for i in range(100):
        rbac_system.grant_role(
            f"perf_user_{i:03d}",
            f"perf_guardian_{i:03d}",
            PermissionLevel.VIEW_ONLY,
            "perf_admin"
        )
    
    creation_time = time.time() - start_time
    print(f"  - 100ログ: {creation_time:.3f}?")
    
    # ?
    start_time = time.time()
    for i in range(100):
        rbac_system.check_permission(
            f"perf_guardian_{i:03d}",
            f"perf_user_{i:03d}",
            ResourceType.USER_PROFILE,
            Action.READ
        )
    
    check_time = time.time() - start_time
    print(f"  - 100?: {check_time:.3f}?")
    
    return True


def main():
    """メイン"""
    print("Authentication Service Implementation Validation")
    print("=" * 60)
    
    validation_results = []
    
    try:
        # 1. RBACシステム
        result = validate_rbac_system_initialization()
        validation_results.append(("RBACシステム", result))
        
        if not result:
            print("? RBACシステム")
            return False
        
        # 2. ?
        result, access_token = validate_guardian_auth_service()
        validation_results.append(("?", result))
        
        if not result:
            print("? ?")
            return False
        
        # 3. JWT?
        result = validate_jwt_token_system()
        validation_results.append(("JWT?", result))
        
        if not result:
            print("? JWT?")
            return False
        
        # 4. ?
        result = validate_permission_scenarios()
        validation_results.append(("?", result))
        
        if not result:
            print("? ?")
            return False
        
        # 5. システム
        result = validate_system_robustness()
        validation_results.append(("システム", result))
        
        if not result:
            print("? システム")
            return False
        
        # 検証
        print("\n" + "=" * 60)
        print("? ?")
        print("\n検証:")
        
        for test_name, result in validation_results:
            status = "? 成" if result else "? ?"
            print(f"  - {test_name}: {status}")
        
        print(f"\n実装:")
        print(f"  - 3つview-only, task-edit, chat-send?")
        print(f"  - JWT?")
        print(f"  - ?")
        print(f"  - ?")
        print(f"  - ?")
        
        return True
        
    except Exception as e:
        print(f"\n? 検証: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)