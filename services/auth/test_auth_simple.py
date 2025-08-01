"""
?

JWT?
?6.1, 10.3に

Requirements: 6.1, 10.3
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.jwt_service import jwt_service, TokenType
from shared.interfaces.rbac_system import PermissionLevel

# ?
auth_service = None


def test_jwt_token_creation():
    """JWT?"""
    print("=== JWT? ===")
    
    guardian_id = "test_guardian_001"
    user_id = "test_user_001"
    permission_level = PermissionLevel.TASK_EDIT.value
    
    try:
        # ?
        token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level
        )
        
        print(f"? アプリ")
        print(f"? リスト")
        print(f"? ?: {token_pair.token_type}")
        print(f"? ?: {token_pair.expires_in}?")
        
        # アプリ
        access_token_data = jwt_service.verify_token(token_pair.access_token)
        assert access_token_data.guardian_id == guardian_id
        assert access_token_data.user_id == user_id
        assert access_token_data.permission_level == permission_level
        assert access_token_data.token_type == TokenType.ACCESS
        print(f"? アプリ")
        
        # リスト
        refresh_token_data = jwt_service.verify_token(token_pair.refresh_token)
        assert refresh_token_data.guardian_id == guardian_id
        assert refresh_token_data.user_id == user_id
        assert refresh_token_data.permission_level == permission_level
        assert refresh_token_data.token_type == TokenType.REFRESH
        print(f"? リスト")
        
        return True
        
    except Exception as e:
        print(f"? JWT?: {str(e)}")
        return False


def test_token_refresh():
    """?"""
    print("\n=== ? ===")
    
    guardian_id = "test_guardian_002"
    user_id = "test_user_002"
    permission_level = PermissionLevel.CHAT_SEND.value
    
    try:
        # ?
        original_token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level
        )
        print(f"? ?")
        
        # ?
        new_token_pair = jwt_service.refresh_access_token(original_token_pair.refresh_token)
        print(f"? ?")
        
        # ?
        assert new_token_pair.access_token != original_token_pair.access_token
        assert new_token_pair.refresh_token != original_token_pair.refresh_token
        print(f"? ?")
        
        # ?
        new_access_token_data = jwt_service.verify_token(new_token_pair.access_token)
        assert new_access_token_data.guardian_id == guardian_id
        assert new_access_token_data.user_id == user_id
        assert new_access_token_data.permission_level == permission_level
        print(f"? ?")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def test_token_revocation():
    """?"""
    print("\n=== ? ===")
    
    guardian_id = "test_guardian_003"
    user_id = "test_user_003"
    permission_level = PermissionLevel.VIEW_ONLY.value
    
    try:
        # ?
        token_pair = jwt_service.create_token_pair(
            guardian_id, user_id, permission_level
        )
        print(f"? ?")
        
        # ?
        jwt_service.verify_token(token_pair.access_token)
        print(f"? ?")
        
        # ?
        revoke_success = jwt_service.revoke_token(token_pair.access_token)
        assert revoke_success is True
        print(f"? ?")
        
        # ?
        try:
            jwt_service.verify_token(token_pair.access_token)
            print(f"? ?")
            return False
        except:
            print(f"? ?")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def test_token_info_extraction():
    """?"""
    print("\n=== ? ===")
    
    guardian_id = "test_guardian_004"
    user_id = "test_user_004"
    permission_level = PermissionLevel.TASK_EDIT.value
    
    try:
        # カスタム
        access_token = jwt_service.create_access_token(
            guardian_id, user_id, permission_level,
            {"custom_claim": "test_value"}
        )
        print(f"? カスタム")
        
        # ?
        token_info = jwt_service.get_token_info(access_token)
        
        assert token_info["guardian_id"] == guardian_id
        assert token_info["user_id"] == user_id
        assert token_info["permission_level"] == permission_level
        assert token_info["token_type"] == "access"
        assert token_info["is_expired"] is False
        assert token_info["is_revoked"] is False
        assert "jti" in token_info
        assert "issued_at" in token_info
        assert "expires_at" in token_info
        
        print(f"? ?")
        print(f"  - Guardian ID: {token_info['guardian_id']}")
        print(f"  - User ID: {token_info['user_id']}")
        print(f"  - Permission Level: {token_info['permission_level']}")
        print(f"  - Token Type: {token_info['token_type']}")
        print(f"  - JTI: {token_info['jti']}")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


async def test_authentication_service():
    """?"""
    print("\n=== ? ===")
    
    try:
        # ?
        from services.auth.auth_middleware import auth_service
        
        guardian_id = "test_guardian_005"
        user_id = "test_user_005"
        permission_level = PermissionLevel.CHAT_SEND
        
        # ?
        auth_result = await auth_service.authenticate_and_authorize(
            guardian_id, user_id, permission_level
        )
        
        assert auth_result["authorized"] is True
        assert "authentication" in auth_result
        assert "tokens" in auth_result
        print(f"? ?")
        
        tokens = auth_result["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        print(f"? ?")
        
        # ?
        refresh_result = await auth_service.refresh_authentication(
            tokens["refresh_token"]
        )
        
        assert "tokens" in refresh_result
        assert refresh_result["guardian_id"] == guardian_id
        assert refresh_result["user_id"] == user_id
        print(f"? ?")
        
        # ログ
        logout_result = await auth_service.logout(
            refresh_result["tokens"]["access_token"],
            refresh_result["tokens"]["refresh_token"]
        )
        
        assert logout_result["success"] is True
        print(f"? ログ")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def test_permission_levels():
    """?"""
    print("\n=== ? ===")
    
    try:
        # ?
        permission_levels = [
            PermissionLevel.VIEW_ONLY,
            PermissionLevel.TASK_EDIT,
            PermissionLevel.CHAT_SEND
        ]
        
        for level in permission_levels:
            guardian_id = f"test_guardian_{level.value}"
            user_id = f"test_user_{level.value}"
            
            token = jwt_service.create_access_token(
                guardian_id, user_id, level.value
            )
            
            token_data = jwt_service.verify_token(token)
            assert token_data.permission_level == level.value
            
            print(f"? {level.value} ?")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


async def run_all_tests():
    """?"""
    print("=== ? ===")
    
    tests = [
        ("JWT?", test_jwt_token_creation),
        ("?", test_token_refresh),
        ("?", test_token_revocation),
        ("?", test_token_info_extraction),
        ("?", test_authentication_service),
        ("?", test_permission_levels),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_name == "?":
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            
        except Exception as e:
            print(f"? {test_name}?: {str(e)}")
    
    print(f"\n=== ?: {passed}/{total} 成 ===")
    
    if passed == total:
        print("? ?")
        return True
    else:
        print("? 一般")
        return False


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)