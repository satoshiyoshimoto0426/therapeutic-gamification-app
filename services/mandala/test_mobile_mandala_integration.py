"""
Mobile Mandala System Integration Tests

モデルMandalaシステム
?
タスク

Requirements: 9.5, 4.1
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from dataclasses import dataclass

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mandala.mobile_mandala_system import MobileMandalaSystem, MobileGridLayout, TouchGesture
from shared.interfaces.mobile_types import (
    DeviceType, ScreenOrientation, TouchEventType, SwipeDirection,
    MobileMandalaConfig, TouchEvent, SwipeEvent, PinchEvent,
    MobileViewport, ADHDMobileSettings, TouchInteractionResponse
)
from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid, MemoryCell, CellStatus


class TestMobileMandalaIntegration:
    """モデルMandalaシステム"""
    
    def setup_method(self):
        """?"""
        self.mock_mandala_interface = Mock(spec=MandalaSystemInterface)
        self.mobile_system = MobileMandalaSystem(self.mock_mandala_interface)
        
        # ?
        self.mobile_viewport = MobileViewport(
            width=375,
            height=667,
            orientation=ScreenOrientation.PORTRAIT,
            device_pixel_ratio=2.0,
            safe_area_insets={"top": 44, "bottom": 34, "left": 0, "right": 0}
        )
        
        self.tablet_viewport = MobileViewport(
            width=768,
            height=1024,
            orientation=ScreenOrientation.PORTRAIT,
            device_pixel_ratio=2.0,
            safe_area_insets={"top": 20, "bottom": 0, "left": 0, "right": 0}
        )
        
        # ?Mandala?
        self.mock_grid = Mock(spec=MandalaGrid)
        self.mock_mandala_interface.get_or_create_grid.return_value = self.mock_grid
        self.mock_mandala_interface.get_grid_api_response.return_value = {
            "uid": "test_user",
            "grid": [[None for _ in range(9)] for _ in range(9)],
            "unlocked_count": 5,
            "total_cells": 81
        }
    
    def test_screen_size_calculation_mobile(self):
        """モデル"""
        config = self.mobile_system.calculate_grid_size_for_screen(self.mobile_viewport)
        
        assert config.device_type == DeviceType.MOBILE_STANDARD
        assert config.cell_size > 0
        assert config.gap > 0
        assert config.zoom_enabled == True  # ?
        assert config.swipe_navigation == True
        assert config.haptic_feedback == True
    
    def test_screen_size_calculation_tablet(self):
        """タスク"""
        config = self.mobile_system.calculate_grid_size_for_screen(self.tablet_viewport)
        
        assert config.device_type == DeviceType.TABLET_PORTRAIT
        assert config.cell_size > 0
        assert config.gap > 0
        assert config.zoom_enabled == False  # タスク
        assert config.swipe_navigation == True
        assert config.haptic_feedback == True
    
    def test_landscape_orientation_adjustment(self):
        """?"""
        landscape_viewport = MobileViewport(
            width=667,
            height=375,
            orientation=ScreenOrientation.LANDSCAPE,
            device_pixel_ratio=2.0,
            safe_area_insets={"top": 0, "bottom": 0, "left": 44, "right": 44}
        )
        
        config = self.mobile_system.calculate_grid_size_for_screen(landscape_viewport)
        
        # ?
        portrait_config = self.mobile_system.calculate_grid_size_for_screen(self.mobile_viewport)
        assert config.cell_size >= portrait_config.cell_size
        assert config.zoom_enabled == False  # ?
    
    def test_mobile_grid_layout_creation(self):
        """モデル"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        assert isinstance(layout, MobileGridLayout)
        assert layout.cell_size > 0
        assert layout.gap > 0
        assert layout.total_width > 0
        assert layout.total_height > 0
        assert layout.zoom_level == 1.0
        assert layout.pan_offset_x == 0.0
        assert layout.pan_offset_y == 0.0
        assert len(layout.visible_cells) > 0
        
        # ユーザー
        assert uid in self.mobile_system.mobile_configs
        assert uid in self.mobile_system.grid_layouts
    
    def test_visible_cells_calculation_mobile(self):
        """モデル"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # モデル
        assert len(layout.visible_cells) == 9  # 3x3の
        center_cells = [(3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)]
        assert set(layout.visible_cells) == set(center_cells)
    
    def test_visible_cells_calculation_tablet(self):
        """タスク"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.tablet_viewport)
        
        # タスク
        assert len(layout.visible_cells) == 81  # 9x9の
    
    def test_touch_event_tap_handling(self):
        """タスク"""
        uid = "test_user"
        self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # モデル
        mock_cell = Mock(spec=MemoryCell)
        mock_cell.status = CellStatus.UNLOCKED
        mock_cell.quest_title = "?"
        mock_cell.quest_description = "?"
        self.mock_grid.get_cell.return_value = mock_cell
        
        touch_event = TouchEvent(
            event_type=TouchEventType.TAP,
            x=100.0,
            y=100.0,
            timestamp=1234567890
        )
        
        response = self.mobile_system.handle_touch_event(uid, touch_event)
        
        assert response.success == True
        assert response.feedback_type == "haptic"
        assert response.next_action == "show_cell_details"
        assert "?" in response.accessibility_announcement
    
    def test_touch_event_long_press_handling(self):
        """ログ"""
        uid = "test_user"
        self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # アプリ
        mock_cell = Mock(spec=MemoryCell)
        mock_cell.status = CellStatus.UNLOCKED
        mock_cell.quest_title = "?"
        self.mock_grid.get_cell.return_value = mock_cell
        
        touch_event = TouchEvent(
            event_type=TouchEventType.LONG_PRESS,
            x=100.0,
            y=100.0,
            timestamp=1234567890
        )
        
        response = self.mobile_system.handle_touch_event(uid, touch_event)
        
        assert response.success == True
        assert response.feedback_type == "haptic"
        assert response.next_action == "complete_cell"
        assert "?" in response.accessibility_announcement
    
    def test_touch_event_double_tap_zoom_reset(self):
        """?"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        layout.zoom_level = 1.5
        layout.pan_offset_x = 50.0
        layout.pan_offset_y = 30.0
        
        touch_event = TouchEvent(
            event_type=TouchEventType.DOUBLE_TAP,
            x=100.0,
            y=100.0,
            timestamp=1234567890
        )
        
        response = self.mobile_system.handle_touch_event(uid, touch_event)
        
        assert response.success == True
        assert response.feedback_type == "haptic"
        assert response.animation == "zoom_reset"
        assert "?" in response.accessibility_announcement
        
        # ?
        assert layout.zoom_level == 1.0
        assert layout.pan_offset_x == 0.0
        assert layout.pan_offset_y == 0.0
    
    def test_swipe_event_navigation(self):
        """ストーリー"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        swipe_event = SwipeEvent(
            direction=SwipeDirection.LEFT,
            distance=50.0,
            velocity=100.0,
            start_x=200.0,
            start_y=300.0,
            end_x=150.0,
            end_y=300.0
        )
        
        initial_offset = layout.pan_offset_x
        response = self.mobile_system.handle_swipe_event(uid, swipe_event)
        
        assert response.success == True
        assert response.feedback_type == "visual"
        assert response.animation == "pan"
        assert "LEFT?" in response.accessibility_announcement
        
        # ?
        assert layout.pan_offset_x < initial_offset
    
    def test_pinch_event_zoom(self):
        """?"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        pinch_event = PinchEvent(
            scale=1.5,
            center_x=200.0,
            center_y=300.0,
            velocity=0.1
        )
        
        initial_zoom = layout.zoom_level
        response = self.mobile_system.handle_pinch_event(uid, pinch_event)
        
        assert response.success == True
        assert response.feedback_type == "haptic"
        assert response.animation == "zoom"
        assert "?" in response.accessibility_announcement
        
        # ?
        assert layout.zoom_level > initial_zoom
        assert layout.zoom_level <= 2.0  # ?
    
    def test_mobile_optimized_grid_data(self):
        """モデル"""
        uid = "test_user"
        response = self.mobile_system.get_mobile_optimized_grid_data(uid, self.mobile_viewport)
        
        assert response.data is not None
        assert response.mobile_config is not None
        assert response.performance_hints is not None
        assert response.accessibility_metadata is not None
        
        # モデル
        mobile_config = response.mobile_config
        assert "device_type" in mobile_config
        assert "cell_size" in mobile_config
        assert "zoom_enabled" in mobile_config
        assert "swipe_navigation" in mobile_config
        assert "haptic_feedback" in mobile_config
        
        # ?
        performance_hints = response.performance_hints
        assert "lazy_load_cells" in performance_hints
        assert "reduce_animations" in performance_hints
        assert "preload_adjacent" in performance_hints
        assert "cache_strategy" in performance_hints
        
        # アプリ
        accessibility_metadata = response.accessibility_metadata
        assert "touch_target_size" in accessibility_metadata
        assert "high_contrast" in accessibility_metadata
        assert "reduced_motion" in accessibility_metadata
        assert "voice_over_labels" in accessibility_metadata
    
    def test_adhd_settings_update(self):
        """ADHD設定"""
        uid = "test_user"
        self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        adhd_settings = ADHDMobileSettings(
            large_touch_targets=True,
            reduced_animations=True,
            high_contrast_mode=True,
            focus_mode_available=True
        )
        
        result = self.mobile_system.update_adhd_settings(uid, adhd_settings)
        
        assert result == True
        assert uid in self.mobile_system.adhd_settings
        
        # レベル
        layout = self.mobile_system.grid_layouts[uid]
        assert layout.cell_size >= 48  # ?
    
    def test_focus_mode_layout(self):
        """?"""
        uid = "test_user"
        self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        adhd_settings = ADHDMobileSettings(focus_mode_available=True)
        self.mobile_system.update_adhd_settings(uid, adhd_settings)
        
        focus_layout = self.mobile_system.get_focus_mode_layout(uid)
        
        assert focus_layout is not None
        assert isinstance(focus_layout, MobileGridLayout)
        assert len(focus_layout.visible_cells) <= 3  # ?3?
        assert focus_layout.zoom_level == 1.2  # ?
        
        # ?
        normal_layout = self.mobile_system.grid_layouts[uid]
        assert focus_layout.cell_size > normal_layout.cell_size
        assert focus_layout.gap > normal_layout.gap
    
    def test_grid_view_reset(self):
        """?"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        layout.zoom_level = 1.8
        layout.pan_offset_x = 100.0
        layout.pan_offset_y = 50.0
        
        response = self.mobile_system.reset_grid_view(uid)
        
        assert response.success == True
        assert response.feedback_type == "haptic"
        assert response.animation == "reset"
        assert "?" in response.accessibility_announcement
        
        # ?
        assert layout.zoom_level == 1.0
        assert layout.pan_offset_x == 0.0
        assert layout.pan_offset_y == 0.0
    
    def test_cell_coordinate_conversion(self):
        """?"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        cell_pos = self.mobile_system._get_cell_from_touch(100.0, 100.0, layout)
        assert cell_pos is not None
        assert isinstance(cell_pos, tuple)
        assert len(cell_pos) == 2
        assert 0 <= cell_pos[0] < 9
        assert 0 <= cell_pos[1] < 9
        
        # ?
        layout.zoom_level = 1.5
        layout.pan_offset_x = 50.0
        layout.pan_offset_y = 30.0
        
        cell_pos_zoomed = self.mobile_system._get_cell_from_touch(100.0, 100.0, layout)
        assert cell_pos_zoomed is not None
        # ?
        assert cell_pos_zoomed != cell_pos
    
    def test_invalid_touch_coordinates(self):
        """無"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        cell_pos = self.mobile_system._get_cell_from_touch(-10.0, -10.0, layout)
        assert cell_pos is None
        
        cell_pos = self.mobile_system._get_cell_from_touch(10000.0, 10000.0, layout)
        assert cell_pos is None
    
    def test_touch_event_without_layout(self):
        """レベル"""
        uid = "test_user"
        
        touch_event = TouchEvent(
            event_type=TouchEventType.TAP,
            x=100.0,
            y=100.0,
            timestamp=1234567890
        )
        
        response = self.mobile_system.handle_touch_event(uid, touch_event)
        
        assert response.success == False
        assert response.feedback_type == "none"
        assert "?" in response.accessibility_announcement
    
    def test_swipe_disabled_configuration(self):
        """ストーリー"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ストーリー
        config = self.mobile_system.mobile_configs[uid]
        config.swipe_navigation = False
        
        swipe_event = SwipeEvent(
            direction=SwipeDirection.LEFT,
            distance=50.0,
            velocity=100.0,
            start_x=200.0,
            start_y=300.0,
            end_x=150.0,
            end_y=300.0
        )
        
        response = self.mobile_system.handle_swipe_event(uid, swipe_event)
        
        assert response.success == False
        assert response.feedback_type == "none"
    
    def test_zoom_disabled_configuration(self):
        """?"""
        uid = "test_user"
        layout = self.mobile_system.create_mobile_grid_layout(uid, self.mobile_viewport)
        
        # ?
        config = self.mobile_system.mobile_configs[uid]
        config.zoom_enabled = False
        
        pinch_event = PinchEvent(
            scale=1.5,
            center_x=200.0,
            center_y=300.0,
            velocity=0.1
        )
        
        response = self.mobile_system.handle_pinch_event(uid, pinch_event)
        
        assert response.success == False
        assert response.feedback_type == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])