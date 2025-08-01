#!/usr/bin/env python3
"""
XP・レベルシステム簡単テスト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_xp_level_system():
    """XP・レベルシステムテスト"""
    try:
        from shared.interfaces.level_system import LevelCalculator, PlayerLevelManager
        
        # レベル計算テスト
        calc = LevelCalculator()
        level = calc.get_level_from_xp(1000)
        print(f"[OK] レベル計算成功: XP 1000 -> レベル {level}")
        
        # プレイヤーレベル管理テスト
        player_mgr = PlayerLevelManager(0)
        result = player_mgr.add_xp(500)
        current_level = player_mgr.level_progression.current_level
        print(f"[OK] プレイヤーレベル管理成功: レベル {current_level}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] XP・レベルシステムテスト失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_xp_level_system()
    sys.exit(0 if success else 1)
