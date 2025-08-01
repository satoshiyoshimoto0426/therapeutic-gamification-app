"""
JWT?

JWT?
?6.1, 10.3に

Requirements: 6.1, 10.3
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.auth.jwt_service import jwt_service, TokenType
from services.auth.auth_middleware import JWTAuthMiddleware
from shared.interfaces.rbac_system import PermissionLevel


def test_jwt_middleware_token_validation():
    """JWT?"""
    print("=== JWT? ===")
    
    middleware = JWTAuthMiddleware()
    
    try:
        # ?
        guardian_id = "test_guardian_001"
        user_id = "test_user_001"
        permission_level = PermissionLevel.TASK_EDIT.value
        
        access_token = jwt_service.create_access_token(
            guardian_id, user_id, permission_level
        )
        print(f"? ?")
        
        # ?
        valid_header = f"Bearer {access_token}"
        extracted_token = middleware.validate_token_format(valid_header)
        assert extracted_token == access_token
        print(f"? ?")
        
        # ?
        invalid_headers = [
            "",  # ?
            "Basic invalid_token",  # ?
            "Bearer",  # ?
            "Bearer ",  # ?
            "invalid_format",  # ?
        ]
        
        for invalid_header in invalid_headers:
            try:
                middleware.validate_token_format(invalid_header)
                print(f"? ? '{invalid_header}' が")
                return False
            except:
                pass  # ?
        
        print(f"? ?")
        
        return True
        
    except Exception as e:
        print(f"? JWT?: {str(e)}")
        return False


def test_middleware_error_handling():
    """?"""
    print("\n=== ? ===")
    
    middleware = JWTAuthMiddleware()
    
    try:
        # 無
        invalid_token = "invalid.jwt.token"
        invalid_header = f"Bearer {invalid_token}"
        
        try:
            middleware.validate_token_format(invalid_header)
            # ?JWTと
            print(f"? 無JWT?")
        except:
            print(f"? ?")
            return False
        
        # ?JWT検証
        print(f"? エラー")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def test_token_format_validation():
    """?"""
    print("\n=== ? ===")
    
    middleware = JWTAuthMiddleware()
    
    test_cases = [
        # (header, should_pass, description)
        ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature", True, "?JWT?"),
        ("Bearer token_without_dots", True, "?"),
        ("Bearer ", False, "?"),
        ("Basic token", False, "?"),
        ("", False, "?"),
        ("Bearer", False, "?"),
        ("token_without_scheme", False, "ストーリー"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for header, should_pass, description in test_cases:
        try:
            result = middleware.validate_token_format(header)
            if should_pass:
                print(f"? {description}: 成")
                passed += 1
            else:
                print(f"? {description}: ?")
        except Exception as e:
            if not should_pass:
                print(f"? {description}: ?")
                passed += 1
            else:
                print(f"? {description}: ? - {str(e)}")
    
    print(f"?: {passed}/{total}")
    return passed == total


def test_permission_level_tokens():
    """?"""
    print("\n=== ? ===")
    
    permission_levels = [
        PermissionLevel.VIEW_ONLY,
        PermissionLevel.TASK_EDIT,
        PermissionLevel.CHAT_SEND
    ]
    
    try:
        for level in permission_levels:
            guardian_id = f"guardian_{level.value}"
            user_id = f"user_{level.value}"
            
            # ?
            token = jwt_service.create_access_token(
                guardian_id, user_id, level.value
            )
            
            # ?
            token_data = jwt_service.verify_token(token)
            assert token_data.guardian_id == guardian_id
            assert token_data.user_id == user_id
            assert token_data.permission_level == level.value
            assert token_data.token_type == TokenType.ACCESS
            
            print(f"? {level.value} ?: ?")
        
        return True
        
    except Exception as e:
        print(f"? ?: {str(e)}")
        return False


def run_middleware_tests():
    """?"""
    print("=== JWT? ===")
    
    tests = [
        ("JWT?", test_jwt_middleware_token_validation),
        ("?", test_middleware_error_handling),
        ("?", test_token_format_validation),
        ("?", test_permission_level_tokens),
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
    
    print(f"\n=== ?: {passed}/{total} 成 ===")
    
    if passed == total:
        print("? ?")
        return True
    else:
        print("? 一般")
        return False


if __name__ == "__main__":
    success = run_middleware_tests()
    exit(0 if success else 1)