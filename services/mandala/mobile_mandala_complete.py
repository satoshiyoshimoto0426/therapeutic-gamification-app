"""
Complete Mobile-Optimized Mandala System

?
タスク

Requirements: 9.5, 4.1
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import math
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mobile_types import (
    DeviceType, ScreenOrientation, TouchEventType, SwipeDirection,
    MobileMandalaConfig, TouchEvent, SwipeEvent, PinchEvent,
    MobileViewport, ADHDMobileOptimization,
    TouchInteractionResponse, MobileOptimizedResponse
)
from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid, MemoryCell, CellStatus


@dataclass
class MobileGridLayout:
    """モデル"""
    cell_size: int
    gap: int
    total_width: int
    total_height: int
    zoom_level: float = 1.0
    pan_offset_x: float = 0.0
    pan_offset_y: float = 0.0
    visible_cells: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class TouchGesture:
    """タスク"""
    is_active: bool = False
    start_time: Optional[datetime] = None
    start_position: Optional[Tuple[float, float]] = None
    current_position: Optional[Tuple[float, float]] = None
    gesture_type: Optional[TouchEventType] = None
    target_cell: Optional[Tuple[int, int]] = None


class MobileMandalaSystem:
    """
    モデルMandalaシステム
    
    ?
    ?
    """
    
    def __init__(self, mandala_interface: MandalaSystemInterface):
        self.mandala_interface = mandala_interface
        self.mobile_configs: Dict[str, MobileMandalaConfig] = {}
        self.grid_layouts: Dict[str, MobileGridLayout] = {}
        self.touch_gestures: Dict[str, TouchGesture] = {}
        self.adhd_settings: Dict[str, ADHDMobileOptimization] = {}
        
        # デフォルトADHD設定
        self.default_adhd_settings = ADHDMobileOptimization()
    
    def calculate_grid_size_for_screen(self, viewport: MobileViewport) -> MobileMandalaConfig:
        """
        ?
        
        Args:
            viewport: モデル
            
        Returns:
            MobileMandalaConfig: モデルMandala設定
        """
        # デフォルト
        config = MobileMandalaConfig.for_device_width(viewport.width)
        
        # ?
        if viewport.orientation == ScreenOrientation.LANDSCAPE:
            # ?
            config.cell_size = int(config.cell_size * 1.2)
            config.total_width = int(config.total_width * 1.2)
            config.zoom_enabled = False  # ?
        
        # ?
        safe_area_width = viewport.width - viewport.safe_area_insets["left"] - viewport.safe_area_insets["right"]
        safe_area_height = viewport.height - viewport.safe_area_insets["top"] - viewport.safe_area_insets["bottom"]
        
        # ?
        available_width = safe_area_width - 32  # ?16px
        max_cell_size = (available_width - (8 * config.gap)) // 9  # 9x9?
        
        if max_cell_size < config.cell_size:
            config.cell_size = max_cell_size
            config.total_width = (config.cell_size * 9) + (config.gap * 8)
            config.zoom_enabled = True  # ?
        
        return config
    
    def create_mobile_grid_layout(self, uid: str, viewport: MobileViewport) -> MobileGridLayout:
        """
        モデル
        
        Args:
            uid: ユーザーID
            viewport: モデル
            
        Returns:
            MobileGridLayout: モデル
        """
        config = self.calculate_grid_size_for_screen(viewport)
        self.mobile_configs[uid] = config
        
        layout = MobileGridLayout(
            cell_size=config.cell_size,
            gap=config.gap,
            total_width=config.total_width,
            total_height=config.total_width,  # ?
            visible_cells=self._calculate_visible_cells(viewport, config)
        )
        
        self.grid_layouts[uid] = layout
        return layout
    
    def _calculate_visible_cells(self, viewport: MobileViewport, config: MobileMandalaConfig) -> List[Tuple[int, int]]:
        """表"""
        if config.device_type in [DeviceType.TABLET_PORTRAIT, DeviceType.TABLET_LANDSCAPE]:
            # タスク
            return [(x, y) for x in range(9) for y in range(9)]
        
        # ストーリー
        center_cells = [
            (3, 3), (3, 4), (3, 5),
            (4, 3), (4, 4), (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        return center_cells
    
    def handle_touch_event(self, uid: str, touch_event: TouchEvent) -> TouchInteractionResponse:
        """
        タスク
        
        Args:
            uid: ユーザーID
            touch_event: タスク
            
        Returns:
            TouchInteractionResponse: タスク
        """
        if uid not in self.touch_gestures:
            self.touch_gestures[uid] = TouchGesture()
        
        gesture = self.touch_gestures[uid]
        layout = self.grid_layouts.get(uid)
        
        if not layout:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none",
                accessibility_announcement="?"
            )
        
        # タスク
        cell_position = self._get_cell_from_touch(touch_event.x, touch_event.y, layout)
        
        if touch_event.event_type == TouchEventType.TAP:
            return self._handle_tap(uid, cell_position, touch_event)
        elif touch_event.event_type == TouchEventType.LONG_PRESS:
            return self._handle_long_press(uid, cell_position, touch_event)
        elif touch_event.event_type == TouchEventType.DOUBLE_TAP:
            return self._handle_double_tap(uid, cell_position, touch_event)
        else:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none"
            )
    
    def handle_swipe_event(self, uid: str, swipe_event: SwipeEvent) -> TouchInteractionResponse:
        """
        ストーリー
        
        Args:
            uid: ユーザーID
            swipe_event: ストーリー
            
        Returns:
            TouchInteractionResponse: ストーリー
        """
        layout = self.grid_layouts.get(uid)
        config = self.mobile_configs.get(uid)
        
        if not layout or not config or not config.swipe_navigation:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none"
            )
        
        # ストーリー
        pan_distance = min(swipe_event.distance, layout.cell_size)
        
        if swipe_event.direction == SwipeDirection.LEFT:
            layout.pan_offset_x = max(layout.pan_offset_x - pan_distance, -layout.total_width * 0.3)
        elif swipe_event.direction == SwipeDirection.RIGHT:
            layout.pan_offset_x = min(layout.pan_offset_x + pan_distance, layout.total_width * 0.3)
        elif swipe_event.direction == SwipeDirection.UP:
            layout.pan_offset_y = max(layout.pan_offset_y - pan_distance, -layout.total_height * 0.3)
        elif swipe_event.direction == SwipeDirection.DOWN:
            layout.pan_offset_y = min(layout.pan_offset_y + pan_distance, layout.total_height * 0.3)
        
        return TouchInteractionResponse(
            success=True,
            feedback_type="visual",
            animation="pan",
            accessibility_announcement=f"?{swipe_event.direction.value}?"
        )
    
    def handle_pinch_event(self, uid: str, pinch_event: PinchEvent) -> TouchInteractionResponse:
        """
        ?
        
        Args:
            uid: ユーザーID
            pinch_event: ?
            
        Returns:
            TouchInteractionResponse: ?
        """
        layout = self.grid_layouts.get(uid)
        config = self.mobile_configs.get(uid)
        
        if not layout or not config or not config.zoom_enabled:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none"
            )
        
        # ?0.5x - 2.0x?
        new_zoom = layout.zoom_level * pinch_event.scale
        layout.zoom_level = max(0.5, min(2.0, new_zoom))
        
        return TouchInteractionResponse(
            success=True,
            feedback_type="haptic",
            animation="zoom",
            accessibility_announcement=f"?: {layout.zoom_level:.1f}?"
        )
    
    def _get_cell_from_touch(self, x: float, y: float, layout: MobileGridLayout) -> Optional[Tuple[int, int]]:
        """タスク"""
        # ?
        adjusted_x = (x - layout.pan_offset_x) / layout.zoom_level
        adjusted_y = (y - layout.pan_offset_y) / layout.zoom_level
        
        # ?
        cell_x = int(adjusted_x // (layout.cell_size + layout.gap))
        cell_y = int(adjusted_y // (layout.cell_size + layout.gap))
        
        # ?
        if 0 <= cell_x < 9 and 0 <= cell_y < 9:
            return (cell_x, cell_y)
        
        return None
    
    def _handle_tap(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """タスク"""
        if not cell_position:
            return TouchInteractionResponse(
                success=False,
                feedback_type="haptic",
                accessibility_announcement="?"
            )
        
        x, y = cell_position
        grid = self.mandala_interface.get_or_create_grid(uid)
        cell = grid.get_cell(x, y)
        
        if not cell:
            # ログ
            if grid.can_unlock(x, y):
                return TouchInteractionResponse(
                    success=True,
                    feedback_type="haptic",
                    next_action="show_unlock_dialog",
                    accessibility_announcement=f"? {x+1}, {y+1} の"
                )
            else:
                return TouchInteractionResponse(
                    success=False,
                    feedback_type="haptic",
                    accessibility_announcement=f"? {x+1}, {y+1} の"
                )
        
        elif cell.status == CellStatus.UNLOCKED:
            # アプリ - ?
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_cell_details",
                accessibility_announcement=f"{cell.quest_title} - {cell.quest_description}"
            )
        
        elif cell.status == CellStatus.CORE_VALUE:
            # 価 - リスト
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_core_value",
                accessibility_announcement=f"コア: {cell.quest_title} - {cell.quest_description}"
            )
        
        elif cell.status == CellStatus.COMPLETED:
            # ? - 成
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_completion_details",
                accessibility_announcement=f"?: {cell.quest_title} - {cell.xp_reward} XP?"
            )
        
        return TouchInteractionResponse(success=False, feedback_type="none")
    
    def _handle_long_press(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """ログ"""
        if not cell_position:
            return TouchInteractionResponse(
                success=False,
                feedback_type="haptic"
            )
        
        x, y = cell_position
        grid = self.mandala_interface.get_or_create_grid(uid)
        cell = grid.get_cell(x, y)
        
        if cell and cell.status == CellStatus.UNLOCKED:
            # アプリ
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="complete_cell",
                accessibility_announcement=f"{cell.quest_title} を"
            )
        
        return TouchInteractionResponse(
            success=True,
            feedback_type="haptic",
            next_action="show_context_menu",
            accessibility_announcement="コア"
        )
    
    def _handle_double_tap(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """?"""
        if not cell_position:
            return TouchInteractionResponse(success=False, feedback_type="none")
        
        layout = self.grid_layouts.get(uid)
        
        if layout:
            # ?
            layout.zoom_level = 1.0
            layout.pan_offset_x = 0.0
            layout.pan_offset_y = 0.0
            
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                animation="zoom_reset",
                accessibility_announcement="?"
            )
        
        return TouchInteractionResponse(success=False, feedback_type="none")
    
    def get_mobile_optimized_grid_data(self, uid: str, viewport: MobileViewport) -> MobileOptimizedResponse:
        """
        モデル
        
        Args:
            uid: ユーザーID
            viewport: モデル
            
        Returns:
            MobileOptimizedResponse: モデル
        """
        # ?/?
        layout = self.create_mobile_grid_layout(uid, viewport)
        config = self.mobile_configs[uid]
        
        # 基本グリッドデータを取得
        from shared.interfaces.core_types import ChapterType
        grid_data = self.mandala_interface.get_grid_api_response(uid, ChapterType.SELF_DISCIPLINE)
        
        # モデル
        mobile_config = {
            "device_type": config.device_type.value,
            "cell_size": layout.cell_size,
            "gap": layout.gap,
            "total_width": layout.total_width,
            "total_height": layout.total_height,
            "zoom_enabled": config.zoom_enabled,
            "swipe_navigation": config.swipe_navigation,
            "haptic_feedback": config.haptic_feedback,
            "visible_cells": layout.visible_cells,
            "zoom_level": layout.zoom_level,
            "pan_offset": {
                "x": layout.pan_offset_x,
                "y": layout.pan_offset_y
            }
        }
        
        # ADHD?
        adhd_settings = self.adhd_settings.get(uid, self.default_adhd_settings)
        
        # ?
        performance_hints = {
            "lazy_load_cells": config.device_type in [DeviceType.MOBILE_SMALL, DeviceType.MOBILE_STANDARD],
            "reduce_animations": adhd_settings.reduced_animations,
            "preload_adjacent": True,
            "cache_strategy": "stale-while-revalidate"
        }
        
        # アプリ
        accessibility_metadata = {
            "touch_target_size": 44 if adhd_settings.large_touch_targets else 32,
            "high_contrast": adhd_settings.high_contrast_mode,
            "reduced_motion": adhd_settings.reduced_animations,
            "voice_over_labels": True,
            "gesture_alternatives": True
        }
        
        return MobileOptimizedResponse(
            data=grid_data,
            mobile_config=mobile_config,
            performance_hints=performance_hints,
            accessibility_metadata=accessibility_metadata
        )
    
    def update_adhd_settings(self, uid: str, settings: ADHDMobileOptimization) -> bool:
        """
        ADHD?
        
        Args:
            uid: ユーザーID
            settings: ADHD設定
            
        Returns:
            bool: ?/?
        """
        self.adhd_settings[uid] = settings
        
        # レベル
        if uid in self.grid_layouts:
            layout = self.grid_layouts[uid]
            
            # ?
            if settings.large_touch_targets:
                layout.cell_size = max(layout.cell_size, 48)
            
            # ?
            if settings.focus_mode_available:
                # 表
                layout.visible_cells = layout.visible_cells[:9]  # ?9?
        
        return True
    
    def get_focus_mode_layout(self, uid: str) -> Optional[MobileGridLayout]:
        """
        ?
        
        Args:
            uid: ユーザーID
            
        Returns:
            Optional[MobileGridLayout]: ?
        """
        adhd_settings = self.adhd_settings.get(uid, self.default_adhd_settings)
        
        if not adhd_settings.focus_mode_available:
            return None
        
        layout = self.grid_layouts.get(uid)
        if not layout:
            return None
        
        # ?
        focus_layout = MobileGridLayout(
            cell_size=layout.cell_size + 20,  # ?
            gap=layout.gap + 4,  # ?
            total_width=layout.total_width,
            total_height=layout.total_height,
            zoom_level=1.2,  # ?
            visible_cells=layout.visible_cells[:3]  # ?3?
        )
        
        return focus_layout
    
    def reset_grid_view(self, uid: str) -> TouchInteractionResponse:
        """
        ?
        
        Args:
            uid: ユーザーID
            
        Returns:
            TouchInteractionResponse: リスト
        """
        layout = self.grid_layouts.get(uid)
        
        if layout:
            layout.zoom_level = 1.0
            layout.pan_offset_x = 0.0
            layout.pan_offset_y = 0.0
            
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                animation="reset",
                accessibility_announcement="?"
            )
        
        return TouchInteractionResponse(
            success=False,
            feedback_type="none"
        )