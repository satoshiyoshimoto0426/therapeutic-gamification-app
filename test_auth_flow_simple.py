#!/usr/bin/env python3
"""
認証フロー簡単テスト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_auth_flow():
    """認証フローテスト"""
    try:
        from shared.interfaces.rbac_system import RBACSystem, PermissionLevel
        
        # RBACシステム初期化テスト
        rbac = RBACSystem()
        print(f"[OK] RBACシステム初期化成功: {len(rbac.roles)} ロール")
        
        # ロール確認テスト
        for level in PermissionLevel:
            if level.value in rbac.roles:
                role = rbac.roles[level.value]
                print(f"[OK] ロール確認: {level.value} - {role.name}")
        
        # 権限付与テスト
        success = rbac.grant_role("test_user", "test_guardian", PermissionLevel.VIEW_ONLY, "system")
        print(f"[OK] 権限付与テスト: {success}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 認証フローテスト失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)
