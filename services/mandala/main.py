"""
Mandala Service API

?API実装Mandala?
/mandala/{uid}/grid APIエラー

Requirements: 4.1, 4.3
"""

from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mandala_system import MandalaSystemInterface, MandalaGrid
from shared.interfaces.mandala_validation import MandalaValidator
from shared.interfaces.validation import ValidationResult
from shared.interfaces.mobile_types import (
    MobileViewport, TouchEvent, SwipeEvent, PinchEvent, 
    ADHDMobileOptimization, MobileOptimizedResponse, TouchInteractionResponse
)
from services.mandala.mobile_mandala_system import MobileMandalaSystem

app = FastAPI(
    title="Mandala Service",
    description="9x9 Mandala?API",
    version="1.0.0"
)

# ?
mandala_interface = MandalaSystemInterface()
validator = MandalaValidator()
mobile_mandala = MobileMandalaSystem(mandala_interface)


class UnlockCellRequest(BaseModel):
    """?"""
    x: int = Field(..., ge=0, le=8, description="X? (0-8)")
    y: int = Field(..., ge=0, le=8, description="Y? (0-8)")
    quest_title: str = Field(..., min_length=1, max_length=100, description="?")
    quest_description: str = Field(..., min_length=1, max_length=500, description="?")
    xp_reward: int = Field(..., ge=1, le=1000, description="XP?")
    difficulty: int = Field(..., ge=1, le=5, description="? (1-5)")
    therapeutic_focus: Optional[str] = Field(None, description="治療")
    linked_story_node: Optional[str] = Field(None, description="?")


class CompleteCellRequest(BaseModel):
    """?"""
    x: int = Field(..., ge=0, le=8, description="X? (0-8)")
    y: int = Field(..., ge=0, le=8, description="Y? (0-8)")


class MandalaGridResponse(BaseModel):
    """Mandala応答"""
    uid: str
    chapter_type: Optional[str] = None
    center_value: Optional[str] = None
    grid: List[List[Dict[str, Any]]]
    unlocked_count: int
    completed_count: Optional[int] = None
    completion_percentage: Optional[float] = None
    total_cells: int
    core_values: Optional[Dict[str, str]] = None
    last_updated: str


class UnlockResponse(BaseModel):
    """アプリ"""
    success: bool
    message: str
    unlocked_count: Optional[int] = None
    cell_info: Optional[Dict[str, Any]] = None


class CompletionResponse(BaseModel):
    """?"""
    success: bool
    message: str
    completion_time: Optional[str] = None
    xp_earned: Optional[int] = None


@app.get("/mandala/{uid}/grid", response_model=MandalaGridResponse)
async def get_mandala_grid(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> MandalaGridResponse:
    """
    ユーザーMandala?
    
    Args:
        uid: ユーザーID
        
    Returns:
        MandalaGridResponse: ?
        
    Raises:
        HTTPException: バリデーション
    """
    try:
        # デフォルトのchapter_typeを使用（統合テスト用）
        from shared.interfaces.core_types import ChapterType
        default_chapter_type = ChapterType.SELF_DISCIPLINE
        
        # グリッドデータ取得
        grid_data = mandala_interface.get_grid_api_response(uid, default_chapter_type)
        
        # API応答データ検証
        validation_result = MandalaValidator.validate_api_response_data(grid_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=500,
                detail=f"データ検証エラー: {validation_result.error_message}"
            )
        
        return MandalaGridResponse(**grid_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mandalaグリッド取得エラー: {str(e)}"
        )


@app.post("/mandala/{uid}/unlock", response_model=UnlockResponse)
async def unlock_cell(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: UnlockCellRequest = Body(..., description="アプリ")
) -> UnlockResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        request: アプリ
        
    Returns:
        UnlockResponse: アプリ
        
    Raises:
        HTTPException: バリデーション
    """
    try:
        # ?
        grid = mandala_interface.get_or_create_grid(uid)
        
        # ?
        quest_data = {
            "cell_id": f"cell_{request.x}_{request.y}",
            "quest_title": request.quest_title,
            "quest_description": request.quest_description,
            "xp_reward": request.xp_reward,
            "difficulty": request.difficulty,
            "therapeutic_focus": request.therapeutic_focus,
            "linked_story_node": request.linked_story_node
        }
        
        # アンロック検証
        validation_result = MandalaValidator.validate_unlock_request(grid, request.x, request.y, quest_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"アプリ: {validation_result.error_message}"
            )
        
        # 治療
        if request.therapeutic_focus:
            focus_validation = MandalaValidator.validate_therapeutic_focus(request.therapeutic_focus)
            if not focus_validation.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"治療: {focus_validation.error_message}"
                )
        
        # ビジネス
        # 実装
        today_unlocks = 0  # TODO: 実装
        business_validation = business_rules.can_unlock_today(grid, today_unlocks)
        if not business_validation.is_valid:
            raise HTTPException(
                status_code=429,
                detail=f"ビジネス: {business_validation.error_message}"
            )
        
        # ?
        success = mandala_interface.unlock_cell_for_user(uid, request.x, request.y, quest_data)
        
        if success:
            # アプリ
            updated_grid = mandala_interface.get_or_create_grid(uid)
            cell = updated_grid.get_cell(request.x, request.y)
            
            cell_info = {
                "cell_id": cell.cell_id,
                "position": cell.position,
                "quest_title": cell.quest_title,
                "xp_reward": cell.xp_reward,
                "difficulty": cell.difficulty
            } if cell else None
            
            return UnlockResponse(
                success=True,
                message="?",
                unlocked_count=updated_grid.unlocked_count,
                cell_info=cell_info
            )
        else:
            return UnlockResponse(
                success=False,
                message="?"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"アプリ: {str(e)}"
        )


@app.post("/mandala/{uid}/complete", response_model=CompletionResponse)
async def complete_cell(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: CompleteCellRequest = Body(..., description="?")
) -> CompletionResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        request: ?
        
    Returns:
        CompletionResponse: ?
        
    Raises:
        HTTPException: バリデーション
    """
    try:
        # ?
        grid = mandala_interface.get_or_create_grid(uid)
        
        # 完了検証
        validation_result = MandalaValidator.validate_completion_request(grid, request.x, request.y)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"?: {validation_result.error_message}"
            )
        
        # ビジネス
        # 実装
        last_completion_time = None  # TODO: 実装
        business_validation = business_rules.can_complete_now(grid, request.x, request.y, last_completion_time)
        if not business_validation.is_valid:
            raise HTTPException(
                status_code=429,
                detail=f"ビジネス: {business_validation.error_message}"
            )
        
        # ?
        success = mandala_interface.complete_cell_for_user(uid, request.x, request.y)
        
        if success:
            # ?
            updated_grid = mandala_interface.get_or_create_grid(uid)
            cell = updated_grid.get_cell(request.x, request.y)
            
            return CompletionResponse(
                success=True,
                message="?",
                completion_time=cell.completion_time.isoformat() if cell and cell.completion_time else None,
                xp_earned=cell.xp_reward if cell else None
            )
        else:
            return CompletionResponse(
                success=False,
                message="?"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"?: {str(e)}"
        )


@app.get("/mandala/{uid}/reminder")
async def get_daily_reminder(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Dict[str, str]:
    """
    ?
    
    Args:
        uid: ユーザーID
        
    Returns:
        Dict[str, str]: リスト
    """
    try:
        reminder = mandala_interface.get_daily_reminder_for_user(uid)
        return {"reminder": reminder}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"リスト: {str(e)}"
        )


@app.get("/mandala/{uid}/status")
async def get_mandala_status(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Dict[str, Any]:
    """
    Mandalaシステム
    
    Args:
        uid: ユーザーID
        
    Returns:
        Dict[str, Any]: システム
    """
    try:
        grid = mandala_interface.get_or_create_grid(uid)
        
        # ?
        progression_validation = business_rules.validate_progression_path(grid)
        
        unlocked_cells = grid.get_unlocked_cells()
        completed_cells = grid.get_completed_cells()
        
        return {
            "uid": uid,
            "total_cells": grid.total_cells,
            "unlocked_count": grid.unlocked_count,
            "completed_count": len(completed_cells),
            "completion_rate": len(completed_cells) / grid.total_cells if grid.total_cells > 0 else 0,
            "core_values_count": len(grid.core_values),
            "last_updated": grid.last_updated.isoformat(),
            "progression_warnings": progression_validation.warnings if progression_validation.warnings else [],
            "available_unlocks": len([
                (x, y) for x in range(9) for y in range(9)
                if grid.can_unlock(x, y)
            ])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"?: {str(e)}"
        )


# モデル

@app.post("/mandala/{uid}/mobile/grid", response_model=MobileOptimizedResponse)
async def get_mobile_optimized_grid(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    viewport: MobileViewport = Body(..., description="モデル")
) -> MobileOptimizedResponse:
    """
    モデルMandala?
    
    Args:
        uid: ユーザーID
        viewport: モデル
        
    Returns:
        MobileOptimizedResponse: モデル
    """
    try:
        return mobile_mandala.get_mobile_optimized_grid_data(uid, viewport)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"モデル: {str(e)}"
        )


@app.post("/mandala/{uid}/mobile/touch", response_model=TouchInteractionResponse)
async def handle_touch_interaction(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    touch_event: TouchEvent = Body(..., description="タスク")
) -> TouchInteractionResponse:
    """
    タスク
    
    Args:
        uid: ユーザーID
        touch_event: タスク
        
    Returns:
        TouchInteractionResponse: タスク
    """
    try:
        return mobile_mandala.handle_touch_event(uid, touch_event)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"タスク: {str(e)}"
        )


@app.post("/mandala/{uid}/mobile/swipe", response_model=TouchInteractionResponse)
async def handle_swipe_interaction(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    swipe_event: SwipeEvent = Body(..., description="ストーリー")
) -> TouchInteractionResponse:
    """
    ストーリー
    
    Args:
        uid: ユーザーID
        swipe_event: ストーリー
        
    Returns:
        TouchInteractionResponse: ストーリー
    """
    try:
        return mobile_mandala.handle_swipe_event(uid, swipe_event)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ストーリー: {str(e)}"
        )


@app.post("/mandala/{uid}/mobile/pinch", response_model=TouchInteractionResponse)
async def handle_pinch_interaction(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    pinch_event: PinchEvent = Body(..., description="?")
) -> TouchInteractionResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        pinch_event: ?
        
    Returns:
        TouchInteractionResponse: ?
    """
    try:
        return mobile_mandala.handle_pinch_event(uid, pinch_event)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"?: {str(e)}"
        )


@app.put("/mandala/{uid}/mobile/adhd-settings")
async def update_adhd_settings(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    settings: ADHDMobileOptimization = Body(..., description="ADHD配慮設定")
) -> Dict[str, Any]:
    """
    ADHD?
    
    Args:
        uid: ユーザーID
        settings: ADHD?
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        success = mobile_mandala.update_adhd_settings(uid, settings)
        return {
            "success": success,
            "message": "ADHD設定" if success else "ADHD設定",
            "settings": settings.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ADHD設定: {str(e)}"
        )


@app.get("/mandala/{uid}/mobile/focus-mode")
async def get_focus_mode_layout(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Dict[str, Any]:
    """
    ?
    
    Args:
        uid: ユーザーID
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        focus_layout = mobile_mandala.get_focus_mode_layout(uid)
        
        if focus_layout:
            return {
                "available": True,
                "layout": {
                    "cell_size": focus_layout.cell_size,
                    "gap": focus_layout.gap,
                    "total_width": focus_layout.total_width,
                    "total_height": focus_layout.total_height,
                    "zoom_level": focus_layout.zoom_level,
                    "visible_cells": focus_layout.visible_cells
                }
            }
        else:
            return {
                "available": False,
                "message": "?"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"?: {str(e)}"
        )


@app.post("/mandala/{uid}/mobile/reset-view", response_model=TouchInteractionResponse)
async def reset_grid_view(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> TouchInteractionResponse:
    """
    ?
    
    Args:
        uid: ユーザーID
        
    Returns:
        TouchInteractionResponse: リスト
    """
    try:
        return mobile_mandala.reset_grid_view(uid)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ビジネス: {str(e)}"
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """ヘルパー"""
    return {"status": "healthy", "service": "mandala"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)