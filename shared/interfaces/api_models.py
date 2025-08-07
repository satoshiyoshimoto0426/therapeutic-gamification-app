"""
API Models Interface

API用のリクエスト・レスポンスモデル定義
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from .core_types import TaskType, TaskStatus, CrystalAttribute, CrystalGrowthEvent


class APIResponse(BaseModel):
    """基本APIレスポンス"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """ページネーション付きレスポンス"""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_next: bool


class XPCalculationRequest(BaseModel):
    """XP計算リクエスト"""
    task_type: TaskType
    difficulty: int = Field(..., ge=1, le=5)
    mood_score: int = Field(..., ge=1, le=5)
    adhd_support_level: str = "none"
    actual_duration: Optional[int] = None
    estimated_duration: Optional[int] = None


class XPCalculationResponse(BaseModel):
    """XP計算レスポンス"""
    base_xp: int
    mood_coefficient: float
    adhd_assist_multiplier: float
    time_efficiency_bonus: float = 0.0
    priority_bonus: float = 0.0
    final_xp: int
    level_up: bool = False
    breakdown: Dict[str, Any] = {}


class LevelProgressResponse(BaseModel):
    """レベル進行レスポンス"""
    current_level: int
    total_xp: int
    xp_for_current_level: int
    xp_for_next_level: int
    xp_needed_for_next: int
    progress_percentage: float


class ResonanceEventResponse(BaseModel):
    """共鳴イベントレスポンス"""
    event_id: str
    resonance_type: str
    intensity: str
    player_level: int
    yu_level: int
    level_difference: int
    bonus_xp: int
    crystal_bonuses: Dict[str, int]
    special_rewards: List[str]
    therapeutic_message: str
    story_unlock: Optional[str] = None
    triggered_at: datetime


class TaskCreateRequest(BaseModel):
    """タスク作成リクエスト"""
    task_type: TaskType
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    difficulty: int = Field(..., ge=1, le=5)
    priority: str = "medium"
    estimated_duration: int = Field(30, ge=5, le=480)
    due_date: Optional[datetime] = None
    tags: List[str] = []


class TaskUpdateRequest(BaseModel):
    """タスク更新リクエスト"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    priority: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=5, le=480)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskCompleteRequest(BaseModel):
    """タスク完了リクエスト"""
    mood_score: int = Field(..., ge=1, le=5)
    actual_duration: Optional[int] = Field(None, ge=1, le=1440)
    notes: str = Field("", max_length=1000)


class MoodLogRequest(BaseModel):
    """気分ログリクエスト"""
    mood_score: int = Field(..., ge=1, le=5)
    notes: Optional[str] = Field("", max_length=500)
    context_tags: List[str] = []


class MoodLogResponse(BaseModel):
    """気分ログレスポンス"""
    log_id: str
    uid: str
    log_date: datetime
    mood_score: int
    calculated_coefficient: float
    notes: str
    context_tags: List[str]


class ValidationResult(BaseModel):
    """バリデーション結果"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class HealthCheckResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    error_code: str
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrystalGrowthRequest(BaseModel):
    """Crystal growth request"""
    attribute: CrystalAttribute
    event_type: CrystalGrowthEvent
    growth_amount: int = Field(..., ge=1)
    trigger_context: Dict[str, Any] = {}


class CrystalGrowthResponse(BaseModel):
    """Crystal growth response"""
    success: bool
    attribute: CrystalAttribute
    previous_value: int
    new_value: int
    growth_amount: int
    milestone_reached: bool = False
    milestone_rewards: List[str] = []
    therapeutic_message: str = ""


class CrystalSystemResponse(BaseModel):
    """Summary of user's crystal system"""
    crystals: Dict[str, Dict[str, Any]]
    total_growth_events: int
    resonance_level: int
    active_synergies: List[Dict[str, Any]] = []
    available_milestones: List[Dict[str, Any]] = []


class CrystalResonanceRequest(BaseModel):
    """Request for crystal resonance calculation"""
    player_level: int
    yu_level: int
    resonance_type: Optional[str] = None


class CrystalResonanceResponse(BaseModel):
    """Response for crystal resonance result"""
    success: bool
    resonance_type: str
    intensity: str
    bonus_xp: int
    crystal_bonuses: Dict[str, int] = {}
    message: str = ""


class CrystalMilestoneResponse(BaseModel):
    """Crystal milestone information"""
    attribute: CrystalAttribute
    threshold: int
    title: str
    description: str = ""
    reached: bool = False