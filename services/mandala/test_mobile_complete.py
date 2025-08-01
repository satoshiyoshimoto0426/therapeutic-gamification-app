"""
Complete Mobile Mandala System Test

モデルMandalaシステム
"""

import sys
import os
from unittest.mock import Mock

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mandala.mobile_mandala_complete import MobileMandalaSystem
from shared.interfaces.mobile_types import (
    DeviceType, ScreenOrientation, TouchEventType, SwipeDirection,
    MobileViewport, TouchEvent, SwipeEvent, PinchEvent,
    ADHDMobileSettings
)
from shared.interfaces.mandala_system import MandalaSystemInterface


def test_complete_mobile_mandala_functionality():
    """?Mandala?"""
    print("? ?Mandalaシステム")
    
    # モデル
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mock_mandala_interface.get_grid_api_response.return_value = {
        "uid": "test_user",
        "grid": [[None for _ in range(9)] for _ in range(9)],
        "unlocked_count": 5,
        "total_cells": 81
    }
    
    # モデル
    mock_grid = Mock()
    mock_grid.get_cell.return_value = None
    mock_grid.can_unlock.return_value = False
    mock_mandala_interface.get_or_create_grid.return_value = mock_grid
    
    # モデル
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    print("? システム")
    
    # 1. ?
    print("\n? ?")
    
    viewports = [
        ("?", MobileViewport(width=320, height=568, orientation=ScreenOrientation.PORTRAIT)),
        ("?", MobileViewport(width=375, height=667, orientation=ScreenOrientation.PORTRAIT)),
        ("?", MobileViewport(width=414, height=896, orientation=ScreenOrientation.PORTRAIT)),
        ("タスク", MobileViewport(width=768, height=1024, orientation=ScreenOrientation.PORTRAIT)),
    ]
    
    for name, viewport in viewports:
        config = mobile_system.calculate_grid_size_for_screen(viewport)
        print(f"  {name}: ?={config.cell_size}px, ?={config.zoom_enabled}")
    
    # 2. ?
    print("\n? ?")
    
    uid = "test_user"
    standard_viewport = MobileViewport(width=375, height=667, orientation=ScreenOrientation.PORTRAIT)
    layout = mobile_system.create_mobile_grid_layout(uid, standard_viewport)
    
    print(f"  レベル: {layout.cell_size}x{layout.cell_size}px ?")
    print(f"  表: {len(layout.visible_cells)}?")
    print(f"  ?: {layout.zoom_level}?")
    
    # 3. タスク
    print("\n? タスク")
    
    touch_events = [
        ("タスク", TouchEvent(event_type=TouchEventType.TAP, x=100.0, y=100.0, timestamp=1234567890)),
        ("ログ", TouchEvent(event_type=TouchEventType.LONG_PRESS, x=150.0, y=150.0, timestamp=1234567891)),
        ("?", TouchEvent(event_type=TouchEventType.DOUBLE_TAP, x=200.0, y=200.0, timestamp=1234567892)),
    ]
    
    for name, event in touch_events:
        response = mobile_system.handle_touch_event(uid, event)
        print(f"  {name}: 成={response.success}, ?={response.feedback_type}")
    
    # 4. ストーリー
    print("\n? ストーリー")
    
    swipe_directions = [
        ("?", SwipeDirection.LEFT),
        ("?", SwipeDirection.RIGHT),
        ("?", SwipeDirection.UP),
        ("?", SwipeDirection.DOWN),
    ]
    
    for name, direction in swipe_directions:
        swipe_event = SwipeEvent(
            direction=direction,
            distance=50.0,
            velocity=100.0,
            start_x=200.0,
            start_y=300.0,
            end_x=150.0 if direction == SwipeDirection.LEFT else 250.0,
            end_y=250.0 if direction == SwipeDirection.UP else 350.0
        )
        
        response = mobile_system.handle_swipe_event(uid, swipe_event)
        print(f"  {name}ストーリー: 成={response.success}")
    
    # ?
    updated_layout = mobile_system.grid_layouts[uid]
    print(f"  ?: X={updated_layout.pan_offset_x:.1f}, Y={updated_layout.pan_offset_y:.1f}")
    
    # 5. ?
    print("\n? ?")
    
    pinch_scales = [1.5, 0.8, 2.5, 0.3]  # ?2つ
    
    for scale in pinch_scales:
        pinch_event = PinchEvent(
            scale=scale,
            center_x=200.0,
            center_y=300.0,
            velocity=0.1
        )
        
        response = mobile_system.handle_pinch_event(uid, pinch_event)
        current_zoom = mobile_system.grid_layouts[uid].zoom_level
        print(f"  ストーリー{scale}: 成={response.success}, ?={current_zoom:.1f}?")
    
    # 6. ADHD?
    print("\n? ADHD?")
    
    adhd_settings = ADHDMobileSettings(
        large_touch_targets=True,
        reduced_animations=True,
        high_contrast_mode=True,
        focus_mode_available=True
    )
    
    success = mobile_system.update_adhd_settings(uid, adhd_settings)
    print(f"  ADHD設定: 成={success}")
    
    # ?
    focus_layout = mobile_system.get_focus_mode_layout(uid)
    if focus_layout:
        print(f"  ?: ?={focus_layout.cell_size}px, 表={len(focus_layout.visible_cells)}?")
    else:
        print("  ?: ?")
    
    # 7. モデル
    print("\n? モデル")
    
    mobile_response = mobile_system.get_mobile_optimized_grid_data(uid, standard_viewport)
    print(f"  レベル")
    print(f"  デフォルト: {mobile_response.mobile_config['device_type']}")
    print(f"  ?: {len(mobile_response.performance_hints)}?")
    print(f"  アプリ: タスク={mobile_response.accessibility_metadata['touch_target_size']}px")
    
    # 8. ビジネス
    print("\n? ビジネス")
    
    reset_response = mobile_system.reset_grid_view(uid)
    print(f"  ビジネス: 成={reset_response.success}")
    
    # リスト
    reset_layout = mobile_system.grid_layouts[uid]
    print(f"  リスト: ?={reset_layout.zoom_level}?, ?X={reset_layout.pan_offset_x}, ?Y={reset_layout.pan_offset_y}")
    
    print("\n? ?Mandalaシステム")
    return True


def test_edge_cases():
    """エラー"""
    print("\n?  エラー")
    
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    # 1. 無
    print("  無")
    
    viewport = MobileViewport(width=375, height=667, orientation=ScreenOrientation.PORTRAIT)
    mobile_system.create_mobile_grid_layout("edge_test", viewport)
    
    invalid_touch = TouchEvent(
        event_type=TouchEventType.TAP,
        x=-100.0,  # 無
        y=-100.0,
        timestamp=1234567890
    )
    
    response = mobile_system.handle_touch_event("edge_test", invalid_touch)
    print(f"    無: 成={response.success}")
    
    # 2. ?
    print("  ?")
    
    # ?
    extreme_pinch = PinchEvent(
        scale=10.0,  # ?
        center_x=200.0,
        center_y=200.0,
        velocity=0.1
    )
    
    mobile_system.handle_pinch_event("edge_test", extreme_pinch)
    layout = mobile_system.grid_layouts["edge_test"]
    print(f"    ?: {layout.zoom_level}? (?)")
    
    # 3. ?
    print("  ?")
    
    reset_response = mobile_system.reset_grid_view("nonexistent_user")
    print(f"    ?: 成={reset_response.success}")
    
    print("? エラー")


def test_device_specific_optimizations():
    """デフォルト"""
    print("\n? デフォルト")
    
    mock_mandala_interface = Mock(spec=MandalaSystemInterface)
    mock_mandala_interface.get_grid_api_response.return_value = {
        "uid": "test_user",
        "grid": [[None for _ in range(9)] for _ in range(9)],
        "unlocked_count": 5,
        "total_cells": 81
    }
    
    mobile_system = MobileMandalaSystem(mock_mandala_interface)
    
    # デフォルト
    devices = [
        ("iPhone SE", 320, 568, DeviceType.MOBILE_SMALL),
        ("iPhone 12", 390, 844, DeviceType.MOBILE_STANDARD),
        ("iPhone 12 Pro Max", 428, 926, DeviceType.MOBILE_LARGE),
        ("iPad", 768, 1024, DeviceType.TABLET_PORTRAIT),
        ("iPad Pro", 1024, 1366, DeviceType.TABLET_LANDSCAPE),
    ]
    
    for device_name, width, height, expected_type in devices:
        viewport = MobileViewport(width=width, height=height, orientation=ScreenOrientation.PORTRAIT)
        config = mobile_system.calculate_grid_size_for_screen(viewport)
        
        print(f"  {device_name}: タスク={config.device_type}, ?={config.cell_size}px, ?={config.zoom_enabled}")
        
        # ?
        if config.device_type in [DeviceType.MOBILE_SMALL, DeviceType.MOBILE_STANDARD, DeviceType.MOBILE_LARGE, DeviceType.TABLET_PORTRAIT, DeviceType.TABLET_LANDSCAPE]:
            print(f"    ? ?")
        else:
            print(f"    ?  ?: {config.device_type}")
    
    print("? デフォルト")


def main():
    """メイン"""
    print("? モデルMandalaシステム ?")
    print("=" * 60)
    
    try:
        # ?
        test_complete_mobile_mandala_functionality()
        
        # エラー
        test_edge_cases()
        
        # デフォルト
        test_device_specific_optimizations()
        
        print("\n" + "=" * 60)
        print("? ?Mandalaシステム")
        
    except Exception as e:
        print(f"\n? ?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)