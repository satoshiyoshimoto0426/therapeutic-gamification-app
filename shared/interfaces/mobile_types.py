"""
Mobile Types Interface

モバイル対応のための型定義
Requirements: 9.1, 9.4, 9.5
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """デバイスタイプ"""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    DESKTOP = "desktop"


class ScreenOrientation(str, Enum):
    """画面向き"""
    PORTRAIT = "portrait"      # 縦向き
    LANDSCAPE = "landscape"    # 横向き


class TouchEventType(str, Enum):
    """タッチイベントタイプ"""
    TAP = "tap"               # タップ
    LONG_PRESS = "long_press" # 長押し
    DOUBLE_TAP = "double_tap" # ダブルタップ
    SWIPE = "swipe"          # スワイプ
    PINCH = "pinch"          # ピンチ


class SwipeDirection(str, Enum):
    """スワイプ方向"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class MobileMandalaConfig(BaseModel):
    """モバイルMandala設定"""
    device_type: DeviceType
    screen_width: int
    screen_height: int
    orientation: ScreenOrientation
    grid_size: int = 9
    cell_size: int = 40  # ピクセル
    touch_target_size: int = 44  # 最小タッチターゲットサイズ
    zoom_enabled: bool = True
    swipe_navigation: bool = True
    
    def calculate_optimal_cell_size(self) -> int:
        """最適なセルサイズ計算"""
        available_width = self.screen_width - 40  # マージン考慮
        available_height = self.screen_height - 200  # ヘッダー・フッター考慮
        
        # グリッドに収まる最大サイズ
        max_cell_width = available_width // self.grid_size
        max_cell_height = available_height // self.grid_size
        
        # 正方形セルのサイズ
        optimal_size = min(max_cell_width, max_cell_height)
        
        # 最小タッチターゲットサイズを保証
        return max(optimal_size, self.touch_target_size)


class TouchEvent(BaseModel):
    """タッチイベント"""
    event_type: TouchEventType
    position: Tuple[int, int]  # (x, y)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    pressure: float = 1.0
    duration: Optional[int] = None  # ミリ秒


class SwipeEvent(BaseModel):
    """スワイプイベント"""
    direction: SwipeDirection
    start_position: Tuple[int, int]
    end_position: Tuple[int, int]
    velocity: float  # ピクセル/秒
    distance: float  # ピクセル
    duration: int    # ミリ秒
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PinchEvent(BaseModel):
    """ピンチイベント"""
    scale_factor: float  # 拡大率
    center_position: Tuple[int, int]
    start_distance: float
    end_distance: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MobileViewport(BaseModel):
    """モバイルビューポート"""
    width: int
    height: int
    scale: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    
    def is_position_visible(self, x: int, y: int) -> bool:
        """位置が表示範囲内かチェック"""
        scaled_x = (x - self.offset_x) * self.scale
        scaled_y = (y - self.offset_y) * self.scale
        
        return (0 <= scaled_x <= self.width and 
                0 <= scaled_y <= self.height)
    
    def screen_to_world_position(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """スクリーン座標をワールド座標に変換"""
        world_x = int((screen_x / self.scale) + self.offset_x)
        world_y = int((screen_y / self.scale) + self.offset_y)
        return (world_x, world_y)


class TouchInteractionResponse(BaseModel):
    """タッチ操作レスポンス"""
    success: bool
    action_performed: str
    feedback_message: Optional[str] = None
    haptic_feedback: bool = False
    visual_feedback: Dict[str, Any] = {}
    navigation_hint: Optional[str] = None


class MobileOptimizedResponse(BaseModel):
    """モバイル最適化レスポンス"""
    content: Dict[str, Any]
    layout_config: Dict[str, Any]
    touch_targets: List[Dict[str, Any]] = []
    navigation_options: List[Dict[str, Any]] = []
    accessibility_info: Dict[str, Any] = {}
    
    def add_touch_target(
        self,
        id: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        action: str,
        label: str
    ):
        """タッチターゲット追加"""
        self.touch_targets.append({
            "id": id,
            "position": position,
            "size": size,
            "action": action,
            "label": label,
            "min_size": 44  # アクセシビリティ要件
        })


class MobileLayoutManager:
    """モバイルレイアウト管理"""
    
    def __init__(self):
        self.breakpoints = {
            "xs": 320,   # 小型スマートフォン
            "sm": 375,   # 標準スマートフォン
            "md": 768,   # タブレット縦
            "lg": 1024,  # タブレット横
            "xl": 1200   # デスクトップ
        }
    
    def get_device_category(self, width: int, height: int) -> DeviceType:
        """デバイスカテゴリ判定"""
        min_dimension = min(width, height)
        max_dimension = max(width, height)
        
        if min_dimension < 600:
            return DeviceType.SMARTPHONE
        elif min_dimension < 900:
            return DeviceType.TABLET
        else:
            return DeviceType.DESKTOP
    
    def get_optimal_layout(
        self,
        device_type: DeviceType,
        screen_width: int,
        screen_height: int,
        orientation: ScreenOrientation
    ) -> Dict[str, Any]:
        """最適レイアウト取得"""
        layout = {
            "grid_columns": 1,
            "sidebar_enabled": False,
            "navigation_style": "bottom",
            "font_scale": 1.0,
            "spacing_scale": 1.0
        }
        
        if device_type == DeviceType.SMARTPHONE:
            layout.update({
                "grid_columns": 1,
                "navigation_style": "bottom",
                "font_scale": 1.0,
                "compact_mode": True
            })
        elif device_type == DeviceType.TABLET:
            if orientation == ScreenOrientation.LANDSCAPE:
                layout.update({
                    "grid_columns": 2,
                    "sidebar_enabled": True,
                    "navigation_style": "side",
                    "font_scale": 1.1
                })
            else:
                layout.update({
                    "grid_columns": 1,
                    "navigation_style": "top",
                    "font_scale": 1.05
                })
        else:  # DESKTOP
            layout.update({
                "grid_columns": 3,
                "sidebar_enabled": True,
                "navigation_style": "side",
                "font_scale": 1.0,
                "compact_mode": False
            })
        
        return layout
    
    def calculate_responsive_grid(
        self,
        container_width: int,
        item_count: int,
        min_item_width: int = 280,
        max_columns: int = 4
    ) -> Dict[str, int]:
        """レスポンシブグリッド計算"""
        # 可能な列数計算
        possible_columns = container_width // min_item_width
        columns = min(possible_columns, max_columns, item_count)
        columns = max(1, columns)  # 最低1列
        
        # アイテムサイズ計算
        gap = 16  # グリッドギャップ
        available_width = container_width - (gap * (columns - 1))
        item_width = available_width // columns
        
        return {
            "columns": columns,
            "item_width": item_width,
            "gap": gap,
            "total_width": container_width
        }


class ADHDMobileOptimization(BaseModel):
    """ADHD配慮モバイル最適化"""
    reduce_animations: bool = True
    high_contrast_mode: bool = False
    focus_indicators: bool = True
    simplified_navigation: bool = True
    auto_save_enabled: bool = True
    distraction_free_mode: bool = False
    
    def get_ui_config(self) -> Dict[str, Any]:
        """UI設定取得"""
        return {
            "animations": {
                "enabled": not self.reduce_animations,
                "duration": 200 if self.reduce_animations else 300
            },
            "colors": {
                "high_contrast": self.high_contrast_mode,
                "focus_color": "#FFC857" if self.focus_indicators else "#007AFF"
            },
            "navigation": {
                "max_items": 3 if self.simplified_navigation else 5,
                "show_labels": True,
                "large_touch_targets": True
            },
            "content": {
                "auto_save_interval": 30 if self.auto_save_enabled else 0,
                "distraction_free": self.distraction_free_mode,
                "max_content_width": 600 if self.distraction_free_mode else None
            }
        }


class MobileAccessibilityFeatures(BaseModel):
    """モバイルアクセシビリティ機能"""
    voice_over_enabled: bool = False
    large_text_enabled: bool = False
    reduce_motion_enabled: bool = False
    button_shapes_enabled: bool = False
    
    def get_accessibility_config(self) -> Dict[str, Any]:
        """アクセシビリティ設定取得"""
        return {
            "screen_reader": {
                "enabled": self.voice_over_enabled,
                "announce_changes": True,
                "describe_images": True
            },
            "typography": {
                "large_text": self.large_text_enabled,
                "font_scale": 1.3 if self.large_text_enabled else 1.0,
                "line_height_scale": 1.2 if self.large_text_enabled else 1.0
            },
            "motion": {
                "reduce_motion": self.reduce_motion_enabled,
                "disable_parallax": self.reduce_motion_enabled,
                "static_backgrounds": self.reduce_motion_enabled
            },
            "visual": {
                "button_shapes": self.button_shapes_enabled,
                "focus_rings": True,
                "high_contrast_borders": self.button_shapes_enabled
            }
        }