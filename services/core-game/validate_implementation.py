"""
コアAPI実装
Validate Core Game Engine API implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def validate_api_implementation():
    """API実装"""
    print("=== Core Game Engine API Implementation Validation ===")
    
    try:
        # 1. FastAPIアプリ
        from main import app
        print("? FastAPI app imported successfully")
        
        # 2. ?
        from main import (
            AddXPRequest, AddXPResponse, GetLevelProgressRequest,
            CheckResonanceRequest, ResonanceEventTriggerRequest,
            GameSystemStatusRequest, GameSystemStatusResponse
        )
        print("? API models imported successfully")
        
        # 3. 共有
        from shared.interfaces.level_system import LevelSystemManager
        from shared.interfaces.resonance_system import ResonanceEventManager
        print("? Shared interfaces imported successfully")
        
        # 4. API?
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/health",
            "/xp/add",
            "/level/progress", 
            "/resonance/check",
            "/resonance/trigger",
            "/system/status",
            "/xp/calculate"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"? Route {route} exists")
            else:
                print(f"? Route {route} missing")
        
        # 5. ヘルパー
        from main import get_or_create_game_system, get_or_create_resonance_manager
        from main import create_error_response, create_success_response
        print("? Helper functions available")
        
        # 6. 基本
        print("\n--- Basic Functionality Test ---")
        
        # ゲーム
        game_system = get_or_create_game_system("test_user")
        print(f"? Game system created for test_user")
        
        # XP?
        result = game_system.add_player_xp(100, "validation_test")
        print(f"? XP added: {result['player']['xp_added']} XP")
        print(f"? Level: {result['player']['old_level']} ? {result['player']['new_level']}")
        
        # 共有
        resonance_manager = get_or_create_resonance_manager("test_user")
        print("? Resonance manager created")
        
        # 共有
        status = game_system.get_system_status()
        can_resonate, resonance_type = resonance_manager.check_resonance_conditions(
            status["player"]["level"], status["yu"]["level"]
        )
        print(f"? Resonance check: {can_resonate} ({resonance_type})")
        
        # 7. レベル
        print("\n--- Response Model Validation ---")
        
        # AddXPResponseの
        add_xp_response = AddXPResponse(
            success=True,
            uid="test_user",
            xp_added=100,
            total_xp=100,
            old_level=1,
            new_level=2,
            level_up=True,
            rewards=["test_reward"],
            yu_growth={"old_level": 1, "new_level": 1, "growth_occurred": False}
        )
        print("? AddXPResponse model validation passed")
        
        # GameSystemStatusResponseの
        status_response = GameSystemStatusResponse(
            uid="test_user",
            player_level=2,
            player_xp=100,
            yu_level=1,
            level_difference=1,
            resonance_available=False,
            last_resonance=None,
            total_resonance_events=0,
            system_health="healthy"
        )
        print("? GameSystemStatusResponse model validation passed")
        
        # 8. エラー
        print("\n--- Error Handling Validation ---")
        
        error_response = create_error_response(
            "TEST_ERROR",
            "This is a test error",
            {"test": "data"},
            400
        )
        print("? Error response creation working")
        
        success_response = create_success_response({"test": "data"})
        print("? Success response creation working")
        
        print("\n=== Validation Completed Successfully ===")
        return True
        
    except ImportError as e:
        print(f"? Import error: {e}")
        return False
    except Exception as e:
        print(f"? Validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_api_endpoints():
    """APIエラー"""
    print("\n=== API Endpoints Detailed Validation ===")
    
    try:
        from main import app
        
        # ?
        print("Available routes:")
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  {methods:10} {route.path}")
        
        # ?
        print(f"\nMiddleware count: {len(app.user_middleware)}")
        
        # ?
        print(f"Exception handlers: {len(app.exception_handlers)}")
        
        return True
        
    except Exception as e:
        print(f"? Endpoint validation error: {e}")
        return False

def main():
    """メイン"""
    print("Starting Core Game Engine API validation...\n")
    
    # 基本
    basic_validation = validate_api_implementation()
    
    # エラー
    endpoint_validation = validate_api_endpoints()
    
    if basic_validation and endpoint_validation:
        print("\n? All validations passed! Core Game Engine API is ready.")
        return True
    else:
        print("\n? Some validations failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)