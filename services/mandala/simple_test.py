"""
Mandala実装の簡単なテスト

基本的な動作確認を行う。
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from shared.interfaces.mandala_system import MandalaSystemInterface, CellStatus
    print("✓ MandalaSystemInterface インポート成功")
except Exception as e:
    print(f"✗ MandalaSystemInterface インポートエラー: {e}")
    sys.exit(1)

try:
    from shared.interfaces.mandala_validation import MandalaValidator
    print("✓ MandalaValidator インポート成功")
except Exception as e:
    print(f"✗ MandalaValidator インポートエラー: {e}")
    sys.exit(1)

def test_basic_functionality():
    """基本機能テスト"""
    print("\n=== 基本機能テスト ===")
    
    # インターフェース作成
    interface = MandalaSystemInterface()
    test_uid = "simple_test_user"
    
    # グリッド作成
    grid = interface.get_or_create_grid(test_uid)
    print(f"✓ グリッド作成: UID={grid.uid}, 総セル数={grid.total_cells}")
    
    # 中央価値観セル確認
    core_cell = grid.get_cell(4, 4)
    if core_cell and core_cell.status == CellStatus.CORE_VALUE:
        print(f"✓ 中央価値観セル確認: {core_cell.quest_title}")
    else:
        print("✗ 中央価値観セルが見つかりません")
    
    # セルアンロックテスト
    quest_data = {
        "quest_title": "テストクエスト",
        "quest_description": "簡単なテスト",
        "xp_reward": 25,
        "difficulty": 2
    }
    
    success = interface.unlock_cell_for_user(test_uid, 4, 2, quest_data)
    if success:
        print("✓ セルアンロック成功")
    else:
        print("✗ セルアンロック失敗")
    
    # API応答生成テスト
    api_response = interface.get_grid_api_response(test_uid)
    print(f"✓ API応答生成: アンロック数={api_response['unlocked_count']}")
    
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
        print("\n✅ 簡単なテスト完了")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)