"""
Core Game Engine API
Core Game Engine API with XP management, level progression, and resonance events
Requirements: 8.1, 8.2
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import traceback
import uuid

# Shared imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.level_system import (
    LevelCalculator, PlayerLevelManager, YuLevelManager, LevelSystemManager
)
from shared.interfaces.resonance_system import (
    ResonanceEventManager, ResonanceType, ResonanceIntensity
)
from shared.interfaces.task_system import TaskXPCalculator, Task
from shared.interfaces.core_types import TaskType, TaskStatus
from shared.interfaces.api_models import (
    APIResponse, XPCalculationRequest, XPCalculationResponse,
    LevelProgressResponse, ResonanceEventResponse
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Therapeutic Gamification - Core Game Engine",
    description="XP Management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ?
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ?
game_systems: Dict[str, LevelSystemManager] = {}
resonance_managers: Dict[str, ResonanceEventManager] = {}


# === リスト/レベル ===

class AddXPRequest(BaseModel):
    """XP?"""
    uid: str = Field(..., description="ユーザーID")
    xp_amount: int = Field(..., ge=1, le=10000, description="?XP?")
    source: str = Field("api", description="XPの")
    task_id: Optional[str] = Field(None, description="?ID")


class AddXPResponse(BaseModel):
    """XP?"""
    success: bool
    uid: str
    xp_added: int
    total_xp: int
    old_level: int
    new_level: int
    level_up: bool
    rewards: List[str]
    yu_growth: Dict[str, Any]
    resonance_event: Optional[Dict[str, Any]] = None


class GetLevelProgressRequest(BaseModel):
    """レベル"""
    uid: str = Field(..., description="ユーザーID")


class CheckResonanceRequest(BaseModel):
    """共有"""
    uid: str = Field(..., description="ユーザーID")
    force_check: bool = Field(False, description="?")


class ResonanceEventTriggerRequest(BaseModel):
    """共有"""
    uid: str = Field(..., description="ユーザーID")
    resonance_type: Optional[ResonanceType] = Field(None, description="共有None?")


class GameSystemStatusRequest(BaseModel):
    """ゲーム"""
    uid: str = Field(..., description="ユーザーID")


class GameSystemStatusResponse(BaseModel):
    """ゲーム"""
    uid: str
    player_level: int
    player_xp: int
    yu_level: int
    level_difference: int
    resonance_available: bool
    last_resonance: Optional[datetime]
    total_resonance_events: int
    system_health: str


# === ヘルパー ===

def get_or_create_game_system(uid: str) -> LevelSystemManager:
    """ゲーム"""
    if uid not in game_systems:
        game_systems[uid] = LevelSystemManager(player_xp=0, yu_level=1)
        logger.info(f"Created new game system for user {uid}")
    return game_systems[uid]


def get_or_create_resonance_manager(uid: str) -> ResonanceEventManager:
    """共有"""
    if uid not in resonance_managers:
        resonance_managers[uid] = ResonanceEventManager()
        logger.info(f"Created new resonance manager for user {uid}")
    return resonance_managers[uid]


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict] = None,
    status_code: int = 400
) -> JSONResponse:
    """?"""
    error_response = {
        "success": False,
        "error_code": error_code,
        "message": message,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """?"""
    return {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


# === APIエラー ===

@app.get("/health")
async def health_check():
    """ヘルパー"""
    return {
        "status": "healthy",
        "service": "core-game-engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "active_users": len(game_systems),
        "active_resonance_managers": len(resonance_managers)
    }


@app.post("/xp/add", response_model=AddXPResponse)
async def add_xp(request: AddXPRequest):
    """XPを"""
    try:
        # ゲーム
        game_system = get_or_create_game_system(request.uid)
        resonance_manager = get_or_create_resonance_manager(request.uid)
        
        # XPを
        result = game_system.add_player_xp(request.xp_amount, request.source)
        
        # 共有
        resonance_event = None
        player_level = result["player"]["new_level"]
        yu_level = result["yu"]["new_level"]
        
        can_resonate, resonance_type = resonance_manager.check_resonance_conditions(
            player_level, yu_level
        )
        
        if can_resonate:
            resonance_event_obj = resonance_manager.trigger_resonance_event(
                player_level, yu_level, resonance_type
            )
            
            # 共有XPを
            bonus_result = game_system.add_player_xp(
                resonance_event_obj.bonus_xp, 
                f"resonance_{resonance_type.value}"
            )
            
            resonance_event = {
                "event_id": resonance_event_obj.event_id,
                "type": resonance_event_obj.resonance_type.value,
                "intensity": resonance_event_obj.intensity.value,
                "bonus_xp": resonance_event_obj.bonus_xp,
                "crystal_bonuses": {
                    attr.value: bonus for attr, bonus in resonance_event_obj.crystal_bonuses.items()
                },
                "special_rewards": resonance_event_obj.special_rewards,
                "therapeutic_message": resonance_event_obj.therapeutic_message,
                "story_unlock": resonance_event_obj.story_unlock
            }
            
            # 共有
            final_status = game_system.get_system_status()
            player_level = final_status["player"]["level"]
        
        response = AddXPResponse(
            success=True,
            uid=request.uid,
            xp_added=request.xp_amount,
            total_xp=game_system.player_manager.total_xp,
            old_level=result["player"]["old_level"],
            new_level=player_level,
            level_up=result["player"]["level_up"],
            rewards=result["player"]["rewards"],
            yu_growth={
                "old_level": result["yu"]["old_level"],
                "new_level": result["yu"]["new_level"],
                "growth_occurred": result["yu"]["growth_occurred"]
            },
            resonance_event=resonance_event
        )
        
        logger.info(f"XP added for user {request.uid}: {request.xp_amount} XP, level {result['player']['old_level']}?{player_level}")
        
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error in add_xp: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"入力: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in add_xp: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"XP?: {str(e)}"
        )


@app.post("/level/progress")
async def get_level_progress(request: GetLevelProgressRequest):
    """レベル"""
    try:
        game_system = get_or_create_game_system(request.uid)
        status = game_system.get_system_status()
        
        player_progression = game_system.player_manager.level_progression
        
        response_data = {
            "uid": request.uid,
            "player": {
                "current_level": player_progression.current_level,
                "total_xp": player_progression.current_xp,
                "xp_for_current_level": player_progression.xp_for_current_level,
                "xp_for_next_level": player_progression.xp_for_next_level,
                "xp_needed_for_next": player_progression.xp_needed_for_next,
                "progress_percentage": player_progression.progress_percentage
            },
            "yu": {
                "current_level": status["yu"]["level"],
                "personality": status["yu"]["personality"],
                "description": status["yu"]["description"]
            },
            "level_difference": status["level_difference"]
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_level_progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"レベル: {str(e)}"
        )


@app.post("/resonance/check")
async def check_resonance(request: CheckResonanceRequest):
    """共有"""
    try:
        game_system = get_or_create_game_system(request.uid)
        resonance_manager = get_or_create_resonance_manager(request.uid)
        
        status = game_system.get_system_status()
        player_level = status["player"]["level"]
        yu_level = status["yu"]["level"]
        
        can_resonate, resonance_type = resonance_manager.check_resonance_conditions(
            player_level, yu_level
        )
        
        # 共有
        stats = resonance_manager.get_resonance_statistics()
        
        # ?
        simulation = resonance_manager.simulate_resonance_probability(
            player_level, yu_level, days_ahead=7
        )
        
        response_data = {
            "uid": request.uid,
            "can_resonate": can_resonate,
            "resonance_type": resonance_type.value if resonance_type else None,
            "player_level": player_level,
            "yu_level": yu_level,
            "level_difference": abs(player_level - yu_level),
            "statistics": stats,
            "simulation": simulation
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in check_resonance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"共有: {str(e)}"
        )


@app.post("/resonance/trigger")
async def trigger_resonance_event(request: ResonanceEventTriggerRequest):
    """共有"""
    try:
        game_system = get_or_create_game_system(request.uid)
        resonance_manager = get_or_create_resonance_manager(request.uid)
        
        status = game_system.get_system_status()
        player_level = status["player"]["level"]
        yu_level = status["yu"]["level"]
        
        # 共有
        can_resonate, auto_resonance_type = resonance_manager.check_resonance_conditions(
            player_level, yu_level
        )
        
        if not can_resonate:
            return create_error_response(
                "RESONANCE_CONDITIONS_NOT_MET",
                "共有",
                {
                    "player_level": player_level,
                    "yu_level": yu_level,
                    "level_difference": abs(player_level - yu_level),
                    "min_required_difference": 5
                }
            )
        
        # 共有
        resonance_type = request.resonance_type or auto_resonance_type
        
        # 共有
        resonance_event = resonance_manager.trigger_resonance_event(
            player_level, yu_level, resonance_type
        )
        
        # ?XPを
        xp_result = game_system.add_player_xp(
            resonance_event.bonus_xp,
            f"resonance_{resonance_type.value}"
        )
        
        response_data = {
            "uid": request.uid,
            "resonance_event": {
                "event_id": resonance_event.event_id,
                "type": resonance_event.resonance_type.value,
                "intensity": resonance_event.intensity.value,
                "bonus_xp": resonance_event.bonus_xp,
                "crystal_bonuses": {
                    attr.value: bonus for attr, bonus in resonance_event.crystal_bonuses.items()
                },
                "special_rewards": resonance_event.special_rewards,
                "therapeutic_message": resonance_event.therapeutic_message,
                "story_unlock": resonance_event.story_unlock,
                "triggered_at": resonance_event.triggered_at.isoformat()
            },
            "xp_result": {
                "xp_added": resonance_event.bonus_xp,
                "old_level": xp_result["player"]["old_level"],
                "new_level": xp_result["player"]["new_level"],
                "level_up": xp_result["player"]["level_up"],
                "rewards": xp_result["player"]["rewards"]
            }
        }
        
        logger.info(f"Resonance event triggered for user {request.uid}: {resonance_type.value}")
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in trigger_resonance_event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"共有: {str(e)}"
        )


@app.post("/system/status")
async def get_system_status(request: GameSystemStatusRequest):
    """ゲーム"""
    try:
        game_system = get_or_create_game_system(request.uid)
        resonance_manager = get_or_create_resonance_manager(request.uid)
        
        # システム
        status = game_system.get_system_status()
        resonance_stats = resonance_manager.get_resonance_statistics()
        
        # 共有
        can_resonate, _ = resonance_manager.check_resonance_conditions(
            status["player"]["level"], status["yu"]["level"]
        )
        
        response = GameSystemStatusResponse(
            uid=request.uid,
            player_level=status["player"]["level"],
            player_xp=status["player"]["xp"],
            yu_level=status["yu"]["level"],
            level_difference=status["level_difference"],
            resonance_available=can_resonate,
            last_resonance=resonance_stats.get("last_event"),
            total_resonance_events=resonance_stats["total_events"],
            system_health="healthy"
        )
        
        return create_success_response(response.dict())
        
    except Exception as e:
        logger.error(f"Error in get_system_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"システム: {str(e)}"
        )


class XPPreviewRequest(BaseModel):
    """XP計算"""
    task_difficulty: int = Field(..., ge=1, le=5, description="タスク1-5?")
    mood_score: int = Field(..., ge=1, le=5, description="気分1-5?")
    adhd_assist_usage: str = Field("none", description="ADHD支援")


@app.post("/xp/calculate")
async def calculate_xp_preview(request: XPPreviewRequest):
    """XP計算"""
    try:
        from shared.interfaces.task_system import TaskDifficulty, ADHDSupportLevel
        
        # 文字enumに
        try:
            difficulty_enum = TaskDifficulty(request.task_difficulty)
            adhd_support_enum = ADHDSupportLevel(request.adhd_assist_usage)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無: {str(e)}"
            )
        
        # タスクXP計算
        preview_xp = TaskXPCalculator.get_xp_preview(
            task_type=TaskType.ONE_SHOT,  # デフォルト
            difficulty=difficulty_enum,
            mood_score=request.mood_score,
            adhd_support_level=adhd_support_enum
        )
        
        # 係数
        mood_coefficient = 0.8 + (request.mood_score - 1) * 0.1
        
        # ADHD支援
        adhd_multipliers = {
            "none": 1.0,
            "basic": 1.1,
            "moderate": 1.2,
            "intensive": 1.3
        }
        adhd_assist_multiplier = adhd_multipliers.get(request.adhd_assist_usage, 1.0)
        
        # 基本XP?
        base_xp_values = {1: 5, 2: 10, 3: 15, 4: 25, 5: 40}
        base_xp = base_xp_values.get(request.task_difficulty, 15)
        
        response = XPCalculationResponse(
            base_xp=base_xp,
            mood_coefficient=mood_coefficient,
            adhd_assist_multiplier=adhd_assist_multiplier,
            final_xp=preview_xp,
            level_up=False  # プレビュー
        )
        
        return create_success_response(response.dict())
        
    except Exception as e:
        logger.error(f"Error in calculate_xp_preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"XP計算: {str(e)}"
        )


# === エラー ===

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """バリデーション"""
    return create_error_response(
        "VALIDATION_ERROR",
        "入力",
        {"errors": exc.errors()},
        422
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTPエラー"""
    return create_error_response(
        "HTTP_ERROR",
        exc.detail,
        {"status_code": exc.status_code},
        exc.status_code
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """一般"""
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return create_error_response(
        "INTERNAL_SERVER_ERROR",
        "内部",
        {"error_type": type(exc).__name__},
        500
    )


# === 起動 ===

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )