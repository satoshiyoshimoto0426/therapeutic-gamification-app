"""
Simple Mobile Mandala System Test

モデルMandalaシステム
"""

import sys
import os
from unittest.mock import Mock

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mandala.mobile_mandala_system import MobileMandalaSystem
from shared.interfaces.mobile_types import (
    DeviceType, ScreenOrientation, TouchEventType,
    MobileViewport, TouchEvent
)
from shared.interfaces.mandala_system import MandalaSystemInterface


def test_basic_mobile_mandala_functionality():
    """基本Mandala?"""
    print("? モデルMandalaシステム")
    
    # モデル
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mock_mandala_interface.get_grid_api_response.return_value = {
        "uid": "test_user",
        "grid": [[None for _ in range(9)] for _ in range(9)],
        "unlocked_count": 5,
        "total_cells": 81
    }
    
    # モデル
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    # ?
    mobile_viewport = MobileViewport(
        width=375,
        height=667,
        orientation=ScreenOrientation.PORTRAIT,
        device_pixel_ratio=2.0,
        safe_area_insets={"top": 44, "bottom": 34, "left": 0, "right": 0}
    )
    
    print("? モデル")
    
    # ?
    config = mobile_system.calculate_grid_size_for_screen(mobile_viewport)
    print(f"? ?: デフォルト={config.device_type}, ?={config.cell_size}px")
    
    assert config.device_type == DeviceType.MOBILE_STANDARD
    assert config.cell_size > 0
    assert config.zoom_enabled == True
    
    # ?
    uid = "test_user"
    layout = mobile_system.create_mobile_grid_layout(uid, mobile_viewport)
    print(f"? レベル: ?={layout.total_width}px, ?={layout.total_height}px")
    
    assert layout.cell_size > 0
    assert layout.total_width > 0
    assert len(layout.visible_cells) == 9  # モデル3x3?
    
    # タスク
    touch_event = TouchEvent(
        event_type=TouchEventType.TAP,
        x=100.0,
        y=100.0,
        timestamp=1234567890
    )
    
    # モデル
    mock_grid = Mock()
    mock_grid.get_cell.return_value = None
    mock_grid.can_unlock.return_value = False
    mock_mandala_interface.get_or_create_grid.return_value = mock_grid
    
    response = mobile_system.handle_touch_event(uid, touch_event)
    print(f"? タスク: 成={response.success}")
    
    # モデル
    optimized_data = mobile_system.get_mobile_optimized_grid_data(uid, mobile_viewport)
    print(f"? ?: 設定={len(optimized_data.mobile_config)}")
    
    assert optimized_data.data is not None
    assert optimized_data.mobile_config is not None
    assert optimized_data.performance_hints is not None
    assert optimized_data.accessibility_metadata is not None
    
    print("? モデルMandalaシステム")
    return True


def test_tablet_vs_mobile_differences():
    """タスク"""
    print("\n? タスク vs モデル")
    
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mock_mandala_interface.get_grid_api_response.return_value = {
        "uid": "test_user",
        "grid": [[None for _ in range(9)] for _ in range(9)],
        "unlocked_count": 5,
        "total_cells": 81
    }
    
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    # モデル
    mobile_viewport = MobileViewport(
        width=375,
        height=667,
        orientation=ScreenOrientation.PORTRAIT,
        device_pixel_ratio=2.0,
        safe_area_insets={"top": 44, "bottom": 34, "left": 0, "right": 0}
    )
    
    # タスク
    tablet_viewport = MobileViewport(
        width=768,
        height=1024,
        orientation=ScreenOrientation.PORTRAIT,
        device_pixel_ratio=2.0,
        safe_area_insets={"top": 20, "bottom": 0, "left": 0, "right": 0}
    )
    
    # 設定
    mobile_config = mobile_system.calculate_grid_size_for_screen(mobile_viewport)
    tablet_config = mobile_system.calculate_grid_size_for_screen(tablet_viewport)
    
    print(f"? モデル: デフォルト={mobile_config.device_type}, ?={mobile_config.zoom_enabled}")
    print(f"? タスク: デフォルト={tablet_config.device_type}, ?={tablet_config.zoom_enabled}")
    
    assert mobile_config.device_type == DeviceType.MOBILE_STANDARD
    assert tablet_config.device_type == DeviceType.TABLET_PORTRAIT
    assert mobile_config.zoom_enabled == True
    assert tablet_config.zoom_enabled == False
    
    # レベル
    mobile_layout = mobile_system.create_mobile_grid_layout("mobile_user", mobile_viewport)
    tablet_layout = mobile_system.create_mobile_grid_layout("tablet_user", tablet_viewport)
    
    print(f"? モデル: {len(mobile_layout.visible_cells)}")
    print(f"? タスク: {len(tablet_layout.visible_cells)}")
    
    assert len(mobile_layout.visible_cells) == 9  # 3x3?
    assert len(tablet_layout.visible_cells) == 81  # 9x9?
    
    print("? タスク vs モデル")
    return True


def test_adhd_focus_mode():
    """ADHD?"""
    print("\n? ADHD?")
    
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    mobile_viewport = MobileViewport(
        width=375,
        height=667,
        orientation=ScreenOrientation.PORTRAIT,
        device_pixel_ratio=2.0,
        safe_area_insets={"top": 44, "bottom": 34, "left": 0, "right": 0}
    )
    
    uid = "adhd_user"
    normal_layout = mobile_system.create_mobile_grid_layout(uid, mobile_viewport)
    
    # ADHD設定
    from shared.interfaces.mobile_types import ADHDMobileSettings
    adhd_settings = ADHDMobileSettings(
        large_touch_targets=True,
        reduced_animations=True,
        focus_mode_available=True
    )
    
    mobile_system.update_adhd_settings(uid, adhd_settings)
    focus_layout = mobile_system.get_focus_mode_layout(uid)
    
    print(f"? ?: {len(normal_layout.visible_cells)}")
    print(f"? ?: {len(focus_layout.visible_cells)}")
    print(f"? ?: {normal_layout.cell_size}px")
    print(f"? ?: {focus_layout.cell_size}px")
    
    assert focus_layout is not None
    assert len(focus_layout.visible_cells) <= 3  # ?3?
    assert focus_layout.cell_size > normal_layout.cell_size  # ?
    assert focus_layout.zoom_level == 1.2  # ?
    
    print("? ADHD?")
    return True


if __name__ == "__main__":
    try:
        test_basic_mobile_mandala_functionality()
        test_tablet_vs_mobile_differences()
        test_adhd_focus_mode()
        print("\n? ?")
    except Exception as e:
        print(f"\n? ?: {e}")
        raise