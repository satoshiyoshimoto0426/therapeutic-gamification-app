"""
Mobile-Optimized Mandala System

画面サイズ別グリッドサイズ計算機能、スワイプナビゲーションとズーム機能、
タッチイベント処理（タップ、ロングプレス、スワイプ）を実装。

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
from shared.interfaces.mandala_system import MandalaGrid, MandalaSystemInterface, MemoryCell, CellStatus


@dataclass
class MobileGridLayout:
    """モバイル向けグリッドレイアウト設定"""
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
    """タッチジェスチャーの状態管理"""
    is_active: bool = False
    start_time: Optional[datetime] = None
    start_position: Optional[Tuple[float, float]] = None
    current_position: Optional[Tuple[float, float]] = None
    gesture_type: Optional[TouchEventType] = None
    target_cell: Optional[Tuple[int, int]] = None


class MobileMandalaSystem:
    """
    モバイル最適化Mandalaシステム
    
    画面サイズ別グリッドサイズ計算、スワイプナビゲーション、
    ズーム機能、タッチイベント処理を提供
    """
    
    def __init__(self, mandala_interface: MandalaSystemInterface):
        self.mandala_interface = mandala_interface
        self.mobile_configs: Dict[str, MobileMandalaConfig] = {}
        self.grid_layouts: Dict[str, MobileGridLayout] = {}
        self.touch_gestures: Dict[str, TouchGesture] = {}
        self.adhd_settings: Dict[str, ADHDMobileOptimization] = {}
        
        # デフォルトのADHD設定
        self.default_adhd_settings = ADHDMobileOptimization()
    
    def calculate_grid_size_for_screen(self, viewport: MobileViewport) -> MobileMandalaConfig:
        """
        画面サイズに基づいてグリッドサイズを計算
        
        Args:
            viewport: モバイルビューポート情報
            
        Returns:
            MobileMandalaConfig: モバイル向けMandala設定
        """
        # デバイスタイプに基づく基本設定
        config = MobileMandalaConfig.for_device_width(viewport.width)
        
        # 画面の向きに応じた調整
        if viewport.orientation == ScreenOrientation.LANDSCAPE:
            # 横向きの場合、セルサイズを少し大きくできる
            config.cell_size = int(config.cell_size * 1.2)
            config.total_width = int(config.total_width * 1.2)
            config.zoom_enabled = False  # 横向きではズーム不要
        
        # セーフエリアを考慮した調整
        safe_area_width = viewport.width - viewport.safe_area_insets["left"] - viewport.safe_area_insets["right"]
        safe_area_height = viewport.height - viewport.safe_area_insets["top"] - viewport.safe_area_insets["bottom"]
        
        # 利用可能な幅に基づいてセルサイズを再計算
        available_width = safe_area_width - 32  # 左右マージン16px
        max_cell_size = (available_width - (8 * config.gap)) // 9  # 9x9グリッド
        
        if max_cell_size < config.cell_size:
            config.cell_size = max_cell_size
            config.total_width = (config.cell_size * 9) + (config.gap * 8)
            config.zoom_enabled = True  # 小さい画面ではズーム有効
        
        return config
    
    def create_mobile_grid_layout(self, uid: str, viewport: MobileViewport) -> MobileGridLayout:
        """
        モバイル向けグリッドレイアウトを作成
        
        Args:
            uid: ユーザーID
            viewport: モバイルビューポート情報
            
        Returns:
            MobileGridLayout: モバイルグリッドレイアウト
        """
        config = self.calculate_grid_size_for_screen(viewport)
        self.mobile_configs[uid] = config
        
        layout = MobileGridLayout(
            cell_size=config.cell_size,
            gap=config.gap,
            total_width=config.total_width,
            total_height=config.total_width,  # 正方形グリッド
            visible_cells=self._calculate_visible_cells(viewport, config)
        )
        
        self.grid_layouts[uid] = layout
        return layout
    
    def _calculate_visible_cells(self, viewport: MobileViewport, config: MobileMandalaConfig) -> List[Tuple[int, int]]:
        """表示可能なセルを計算"""
        if config.device_type in [DeviceType.TABLET_PORTRAIT, DeviceType.TABLET_LANDSCAPE]:
            # タブレットでは全セル表示
            return [(x, y) for x in range(9) for y in range(9)]
        
        # スマートフォンでは中央部分を優先表示
        center_cells = [
            (3, 3), (3, 4), (3, 5),
            (4, 3), (4, 4), (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        return center_cells
    
    def handle_touch_event(self, uid: str, touch_event: TouchEvent) -> TouchInteractionResponse:
        """
        タッチイベントを処理
        
        Args:
            uid: ユーザーID
            touch_event: タッチイベント
            
        Returns:
            TouchInteractionResponse: タッチ処理結果
        """
        if uid not in self.touch_gestures:
            self.touch_gestures[uid] = TouchGesture()
        
        gesture = self.touch_gestures[uid]
        layout = self.grid_layouts.get(uid)
        
        if not layout:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none",
                accessibility_announcement="グリッドレイアウトが初期化されていません"
            )
        
        # タッチされたセルを特定
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
        スワイプイベントを処理
        
        Args:
            uid: ユーザーID
            swipe_event: スワイプイベント
            
        Returns:
            TouchInteractionResponse: スワイプ処理結果
        """
        layout = self.grid_layouts.get(uid)
        config = self.mobile_configs.get(uid)
        
        if not layout or not config or not config.swipe_navigation:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none"
            )
        
        # スワイプによるパン操作
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
            accessibility_announcement=f"グリッドを{swipe_event.direction.value}方向に移動しました"
        )
    
    def handle_pinch_event(self, uid: str, pinch_event: PinchEvent) -> TouchInteractionResponse:
        """
        ピンチイベント（ズーム）を処理
        
        Args:
            uid: ユーザーID
            pinch_event: ピンチイベント
            
        Returns:
            TouchInteractionResponse: ピンチ処理結果
        """
        layout = self.grid_layouts.get(uid)
        config = self.mobile_configs.get(uid)
        
        if not layout or not config or not config.zoom_enabled:
            return TouchInteractionResponse(
                success=False,
                feedback_type="none"
            )
        
        # ズームレベルを調整（0.5x - 2.0x）
        new_zoom = layout.zoom_level * pinch_event.scale
        layout.zoom_level = max(0.5, min(2.0, new_zoom))
        
        return TouchInteractionResponse(
            success=True,
            feedback_type="haptic",
            animation="zoom",
            accessibility_announcement=f"ズームレベル: {layout.zoom_level:.1f}倍"
        )
    
    def _get_cell_from_touch(self, x: float, y: float, layout: MobileGridLayout) -> Optional[Tuple[int, int]]:
        """タッチ座標からセル位置を計算"""
        # ズームとパンを考慮した座標変換
        adjusted_x = (x - layout.pan_offset_x) / layout.zoom_level
        adjusted_y = (y - layout.pan_offset_y) / layout.zoom_level
        
        # グリッド座標に変換
        cell_x = int(adjusted_x // (layout.cell_size + layout.gap))
        cell_y = int(adjusted_y // (layout.cell_size + layout.gap))
        
        # 有効範囲チェック
        if 0 <= cell_x < 9 and 0 <= cell_y < 9:
            return (cell_x, cell_y)
        
        return None
    
    def _handle_tap(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """タップ処理"""
        if not cell_position:
            return TouchInteractionResponse(
                success=False,
                feedback_type="haptic",
                accessibility_announcement="有効なセルがタップされませんでした"
            )
        
        x, y = cell_position
        grid = self.mandala_interface.get_or_create_grid(uid)
        cell = grid.get_cell(x, y)
        
        if not cell:
            # ロックされたセル
            if grid.can_unlock(x, y):
                return TouchInteractionResponse(
                    success=True,
                    feedback_type="haptic",
                    next_action="show_unlock_dialog",
                    accessibility_announcement=f"位置 {x+1}, {y+1} のセルをアンロックできます"
                )
            else:
                return TouchInteractionResponse(
                    success=False,
                    feedback_type="haptic",
                    accessibility_announcement=f"位置 {x+1}, {y+1} のセルはまだアンロックできません"
                )
        
        elif cell.status == CellStatus.UNLOCKED:
            # アンロック済みセル - 詳細表示
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_cell_details",
                accessibility_announcement=f"{cell.quest_title} - {cell.quest_description}"
            )
        
        elif cell.status == CellStatus.CORE_VALUE:
            # 価値観セル - リマインダー表示
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_core_value",
                accessibility_announcement=f"コア価値: {cell.quest_title} - {cell.quest_description}"
            )
        
        elif cell.status == CellStatus.COMPLETED:
            # 完了済みセル - 成果表示
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="show_completion_details",
                accessibility_announcement=f"完了済み: {cell.quest_title} - {cell.xp_reward} XP獲得"
            )
        
        return TouchInteractionResponse(success=False, feedback_type="none")
    
    def _handle_long_press(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """ロングプレス処理"""
        if not cell_position:
            return TouchInteractionResponse(
                success=False,
                feedback_type="haptic"
            )
        
        x, y = cell_position
        grid = self.mandala_interface.get_or_create_grid(uid)
        cell = grid.get_cell(x, y)
        
        if cell and cell.status == CellStatus.UNLOCKED:
            # アンロック済みセルの完了処理
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                next_action="complete_cell",
                accessibility_announcement=f"{cell.quest_title} を完了しますか？"
            )
        
        return TouchInteractionResponse(
            success=True,
            feedback_type="haptic",
            next_action="show_context_menu",
            accessibility_announcement="コンテキストメニューを表示"
        )
    
    def _handle_double_tap(self, uid: str, cell_position: Optional[Tuple[int, int]], touch_event: TouchEvent) -> TouchInteractionResponse:
        """ダブルタップ処理"""
        if not cell_position:
            return TouchInteractionResponse(success=False, feedback_type="none")
        
        layout = self.grid_layouts.get(uid)
        
        if layout:
            # ダブルタップでズームリセット
            layout.zoom_level = 1.0
            layout.pan_offset_x = 0.0
            layout.pan_offset_y = 0.0
            
            return TouchInteractionResponse(
                success=True,
                feedback_type="haptic",
                animation="zoom_reset",
                accessibility_announcement="ズームをリセットしました"
            )
        
        return TouchInteractionResponse(success=False, feedback_type="none")
    
    def get_mobile_optimized_grid_data(self, uid: str, viewport: MobileViewport) -> MobileOptimizedResponse:
        """
        モバイル最適化されたグリッドデータを取得
        
        Args:
            uid: ユーザーID
            viewport: モバイルビューポート情報
            
        Returns:
            MobileOptimizedResponse: モバイル最適化レスポンス
        """
        # グリッドレイアウトを作成/更新
        layout = self.create_mobile_grid_layout(uid, viewport)
        config = self.mobile_configs[uid]
        
        # 基本グリッドデータを取得
        from shared.interfaces.core_types import ChapterType
        grid_data = self.mandala_interface.get_grid_api_response(uid, ChapterType.SELF_DISCIPLINE)
        
        # モバイル最適化設定を追加
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
        
        # ADHD配慮設定
        adhd_settings = self.adhd_settings.get(uid, self.default_adhd_settings)
        
        # パフォーマンスヒント
        performance_hints = {
            "lazy_load_cells": config.device_type in [DeviceType.MOBILE_SMALL, DeviceType.MOBILE_STANDARD],
            "reduce_animations": adhd_settings.reduced_animations,
            "preload_adjacent": True,
            "cache_strategy": "stale-while-revalidate"
        }
        
        # アクセシビリティメタデータ
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
        ADHD配慮設定を更新
        
        Args:
            uid: ユーザーID
            settings: ADHD設定
            
        Returns:
            bool: 更新成功/失敗
        """
        self.adhd_settings[uid] = settings
        
        # レイアウトを再計算
        if uid in self.grid_layouts:
            layout = self.grid_layouts[uid]
            
            # 大きなタッチターゲット設定
            if settings.large_touch_targets:
                layout.cell_size = max(layout.cell_size, 48)
            
            # 集中モード設定
            if settings.focus_mode_available:
                # 表示セル数を制限
                layout.visible_cells = layout.visible_cells[:9]  # 最大9セル
        
        return True
    
    def get_focus_mode_layout(self, uid: str) -> Optional[MobileGridLayout]:
        """
        集中モード用のレイアウトを取得
        
        Args:
            uid: ユーザーID
            
        Returns:
            Optional[MobileGridLayout]: 集中モード用レイアウト
        """
        adhd_settings = self.adhd_settings.get(uid, self.default_adhd_settings)
        
        if not adhd_settings.focus_mode_available:
            return None
        
        layout = self.grid_layouts.get(uid)
        if not layout:
            return None
        
        # 集中モード用にレイアウトをコピー・調整
        focus_layout = MobileGridLayout(
            cell_size=layout.cell_size + 20,  # セルサイズを大きく
            gap=layout.gap + 4,  # 間隔を広く
            total_width=layout.total_width,
            total_height=layout.total_height,
            zoom_level=1.2,  # 少しズーム
            visible_cells=layout.visible_cells[:3]  # 最大3セルのみ表示
        )
        
        return focus_layout
    
    def reset_grid_view(self, uid: str) -> TouchInteractionResponse:
        """
        グリッドビューをリセット
        
        Args:
            uid: ユーザーID
            
        Returns:
            TouchInteractionResponse: リセット結果
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
                accessibility_announcement="グリッドビューをリセットしました"
            )
        
        return TouchInteractionResponse(
            success=False,
            feedback_type="none"
        )