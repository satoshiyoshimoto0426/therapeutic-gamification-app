#!/usr/bin/env python3
"""
Mandala進行簡単テスト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_mandala_progression():
    """Mandala進行テスト"""
    try:
        from shared.interfaces.mandala_system import MandalaGrid, MemoryCell
        from shared.interfaces.core_types import CrystalAttribute
        
        # Mandalaグリッド作成テスト
        grid = MandalaGrid("test_user")
        print(f"[OK] Mandalaグリッド作成成功: {len(grid.grid)}x{len(grid.grid[0])} グリッド")
        
        # セル取得テスト
        cell = grid.grid[1][1]
        if cell:
            print(f"[OK] セル取得成功: ({1}, {1}) - ステータス: {cell.status}")
        else:
            print(f"[OK] セル取得: ({1}, {1}) - 未初期化")
        
        # コアバリュー確認テスト
        core_values_count = len(grid.core_values)
        print(f"[OK] コアバリュー確認: {core_values_count}個")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Mandala進行テスト失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mandala_progression()
    sys.exit(0 if success else 1)
