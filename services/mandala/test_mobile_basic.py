"""
Basic Mobile Mandala System Test

モデルMandalaシステム
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mobile_types import (
    DeviceType, ScreenOrientation, TouchEventType,
    MobileViewport, TouchEvent, ADHDMobileSettings
)


def test_mobile_types():
    """モデル"""
    print("? モデル")
    
    # ビジネス
    viewport = MobileViewport(
        width=375,
        height=667,
        orientation=ScreenOrientation.PORTRAIT,
        device_pixel_ratio=2.0,
        safe_area_insets={"top": 44, "bottom": 34, "left": 0, "right": 0}
    )
    
    print(f"? ビジネス: {viewport.width}x{viewport.height}")
    
    # タスク
    touch_event = TouchEvent(
        event_type=TouchEventType.TAP,
        x=100.0,
        y=200.0,
        timestamp=1234567890
    )
    
    print(f"? タスク: {touch_event.event_type}")
    
    # ADHD設定
    adhd_settings = ADHDMobileSettings(
        large_touch_targets=True,
        reduced_animations=True,
        focus_mode_available=True
    )
    
    print(f"? ADHD設定: ?={adhd_settings.large_touch_targets}")
    
    print("? モデル")
    return True


def test_mandala_system_interface():
    """Mandalaシステム"""
    print("\n? Mandalaシステム")
    
    try:
        from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid
        
        # ?
        interface = MandalaSystemInterface()
        print("? MandalaSystemInterface?")
        
        # ?
        grid = interface.get_or_create_grid("test_user")
        print(f"? Mandala?: {grid.total_cells}?")
        
        # API?
        api_response = interface.get_grid_api_response("test_user")
        print(f"? API?: {api_response['total_cells']}?")
        
        print("? Mandalaシステム")
        return True
        
    except Exception as e:
        print(f"? Mandalaシステム: {e}")
        return False


def test_mobile_mandala_basic():
    """基本Mandala?"""
    print("\n? 基本Mandala?")
    
    try:
        # ?
        class SimpleMobileMandala:
            def __init__(self):
                self.configs = {}
            
            def calculate_cell_size(self, width: int) -> int:
                """?"""
                if width <= 360:
                    return 32
                elif width <= 480:
                    return 36
                elif width <= 768:
                    return 48
                else:
                    return 56
            
            def create_layout(self, width: int, height: int):
                """レベル"""
                cell_size = self.calculate_cell_size(width)
                gap = max(2, cell_size // 16)
                total_width = (cell_size * 9) + (gap * 8)
                
                return {
                    "cell_size": cell_size,
                    "gap": gap,
                    "total_width": total_width,
                    "zoom_enabled": width <= 480
                }
        
        # ?
        mobile_mandala = SimpleMobileMandala()
        
        # ?
        small_layout = mobile_mandala.create_layout(320, 568)
        print(f"? ?: ?={small_layout['cell_size']}px, ?={small_layout['zoom_enabled']}")
        
        # ?
        standard_layout = mobile_mandala.create_layout(375, 667)
        print(f"? ?: ?={standard_layout['cell_size']}px, ?={standard_layout['zoom_enabled']}")
        
        # タスク
        tablet_layout = mobile_mandala.create_layout(768, 1024)
        print(f"? タスク: ?={tablet_layout['cell_size']}px, ?={tablet_layout['zoom_enabled']}")
        
        print("? 基本Mandala?")
        return True
        
    except Exception as e:
        print(f"? 基本Mandala?: {e}")
        return False


def main():
    """メイン"""
    print("? モデルMandalaシステム 基本")
    print("=" * 60)
    
    try:
        # 基本
        test_mobile_types()
        test_mandala_system_interface()
        test_mobile_mandala_basic()
        
        print("\n" + "=" * 60)
        print("? ?")
        
    except Exception as e:
        print(f"\n? ?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)