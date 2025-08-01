"""
Mood Tracking Service

?XP係数
1-5ストーリー0.8-1.2の

Requirements: 5.4
"""

from fastapi import FastAPI, HTTPException, Depends, Body, Path, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.interfaces.mood_system import (
    MoodTrackingSystem, MoodEntry, MoodLevel, MoodCategory, MoodTrigger, MoodTrend,
    mood_tracking_system
)

app = FastAPI(
    title="Mood Tracking Service",
    description="?XP係数",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ?
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class MoodLogRequest(BaseModel):
    """気分"""
    overall_mood: int = Field(..., ge=1, le=5, description="?1-5?")
    energy_level: Optional[int] = Field(None, ge=1, le=5, description="エラー1-5?")
    motivation_level: Optional[int] = Field(None, ge=1, le=5, description="や1-5?")
    focus_level: Optional[int] = Field(None, ge=1, le=5, description="?1-5?")
    anxiety_level: Optional[int] = Field(3, ge=1, le=5, description="?1=?, 5=?")
    stress_level: Optional[int] = Field(3, ge=1, le=5, description="ストーリー1=?, 5=?")
    social_mood: Optional[int] = Field(None, ge=1, le=5, description="?1-5?")
    physical_condition: Optional[int] = Field(None, ge=1, le=5, description="?1-5?")
    mood_triggers: List[str] = Field([], description="気分")
    notes: str = Field("", max_length=500, description="メイン")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="?")
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440, description="?")
    log_date: Optional[str] = Field(None, description="?YYYY-MM-DD?")


class MoodResponse(BaseModel):
    """気分"""
    entry_id: str
    uid: str
    date: str
    timestamp: str
    overall_mood: int
    energy_level: int
    motivation_level: int
    focus_level: int
    anxiety_level: int
    stress_level: int
    social_mood: int
    physical_condition: int
    mood_triggers: List[str]
    notes: str
    sleep_hours: Optional[float]
    exercise_minutes: Optional[int]
    mood_coefficient: float
    weighted_mood_coefficient: float
    mood_summary: str
    category_scores: Dict[str, int]


class MoodTrendResponse(BaseModel):
    """気分"""
    period_days: int
    start_date: str
    end_date: str
    avg_overall_mood: float
    avg_energy: float
    avg_motivation: float
    avg_focus: float
    avg_anxiety: float
    avg_stress: float
    overall_trend: float
    energy_trend: float
    motivation_trend: float
    best_day: Optional[str]
    worst_day: Optional[str]
    mood_variance: float
    avg_mood_coefficient: float
    min_mood_coefficient: float
    max_mood_coefficient: float


class ReminderSettingsRequest(BaseModel):
    """リスト"""
    enabled: bool = Field(..., description="リスト/無")


# Helper Functions
def mood_entry_to_response(entry: MoodEntry) -> MoodResponse:
    """MoodEntryをMoodResponseに"""
    return MoodResponse(
        entry_id=entry.entry_id,
        uid=entry.uid,
        date=entry.date.isoformat(),
        timestamp=entry.timestamp.isoformat(),
        overall_mood=entry.overall_mood.value,
        energy_level=entry.energy_level.value,
        motivation_level=entry.motivation_level.value,
        focus_level=entry.focus_level.value,
        anxiety_level=entry.anxiety_level.value,
        stress_level=entry.stress_level.value,
        social_mood=entry.social_mood.value,
        physical_condition=entry.physical_condition.value,
        mood_triggers=[trigger.value for trigger in entry.mood_triggers],
        notes=entry.notes,
        sleep_hours=entry.sleep_hours,
        exercise_minutes=entry.exercise_minutes,
        mood_coefficient=entry.get_mood_coefficient(),
        weighted_mood_coefficient=entry.get_weighted_mood_coefficient(),
        mood_summary=entry.get_mood_summary(),
        category_scores=entry.get_category_scores()
    )


def mood_trend_to_response(trend: MoodTrend) -> MoodTrendResponse:
    """MoodTrendをMoodTrendResponseに"""
    return MoodTrendResponse(
        period_days=trend.period_days,
        start_date=trend.start_date.isoformat(),
        end_date=trend.end_date.isoformat(),
        avg_overall_mood=trend.avg_overall_mood,
        avg_energy=trend.avg_energy,
        avg_motivation=trend.avg_motivation,
        avg_focus=trend.avg_focus,
        avg_anxiety=trend.avg_anxiety,
        avg_stress=trend.avg_stress,
        overall_trend=trend.overall_trend,
        energy_trend=trend.energy_trend,
        motivation_trend=trend.motivation_trend,
        best_day=trend.best_day.isoformat() if trend.best_day else None,
        worst_day=trend.worst_day.isoformat() if trend.worst_day else None,
        mood_variance=trend.mood_variance,
        avg_mood_coefficient=trend.avg_mood_coefficient,
        min_mood_coefficient=trend.min_mood_coefficient,
        max_mood_coefficient=trend.max_mood_coefficient
    )


# Mood Logging Endpoints
@app.post("/mood/{uid}/log", response_model=MoodResponse)
async def log_mood(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: MoodLogRequest = Body(..., description="気分")
) -> MoodResponse:
    """
    気分
    
    Args:
        uid: ユーザーID
        request: 気分
        
    Returns:
        MoodResponse: ?
        
    Raises:
        HTTPException: 気分
    """
    try:
        # ?
        if request.log_date:
            log_date = date.fromisoformat(request.log_date)
        else:
            log_date = date.today()
        
        # 気分
        mood_data = {
            'date': log_date,
            'overall_mood': request.overall_mood,
            'energy_level': request.energy_level or request.overall_mood,
            'motivation_level': request.motivation_level or request.overall_mood,
            'focus_level': request.focus_level or request.overall_mood,
            'anxiety_level': request.anxiety_level,
            'stress_level': request.stress_level,
            'social_mood': request.social_mood or request.overall_mood,
            'physical_condition': request.physical_condition or request.overall_mood,
            'mood_triggers': request.mood_triggers,
            'notes': request.notes,
            'sleep_hours': request.sleep_hours,
            'exercise_minutes': request.exercise_minutes
        }
        
        # 気分
        mood_entry = mood_tracking_system.log_mood(uid, mood_data)
        
        return mood_entry_to_response(mood_entry)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood logging error: {str(e)}"
        )


@app.get("/mood/{uid}/today", response_model=Optional[MoodResponse])
async def get_today_mood(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Optional[MoodResponse]:
    """
    ?
    
    Args:
        uid: ユーザーID
        
    Returns:
        Optional[MoodResponse]: ?None?
    """
    try:
        mood_entry = mood_tracking_system.get_mood_entry(uid, date.today())
        
        if mood_entry:
            return mood_entry_to_response(mood_entry)
        else:
            return None
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get today mood error: {str(e)}"
        )


@app.get("/mood/{uid}/date/{target_date}", response_model=Optional[MoodResponse])
async def get_mood_by_date(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    target_date: str = Path(..., description="?YYYY-MM-DD?")
) -> Optional[MoodResponse]:
    """
    ?
    
    Args:
        uid: ユーザーID
        target_date: ?
        
    Returns:
        Optional[MoodResponse]: ?None?
        
    Raises:
        HTTPException: ?
    """
    try:
        target_date_obj = date.fromisoformat(target_date)
        mood_entry = mood_tracking_system.get_mood_entry(uid, target_date_obj)
        
        if mood_entry:
            return mood_entry_to_response(mood_entry)
        else:
            return None
            
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get mood by date error: {str(e)}"
        )


@app.get("/mood/{uid}/recent", response_model=List[MoodResponse])
async def get_recent_moods(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    days: int = Query(7, ge=1, le=365, description="?")
) -> List[MoodResponse]:
    """
    ?
    
    Args:
        uid: ユーザーID
        days: ?
        
    Returns:
        List[MoodResponse]: ?
    """
    try:
        recent_entries = mood_tracking_system.get_recent_mood_entries(uid, days)
        return [mood_entry_to_response(entry) for entry in recent_entries]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get recent moods error: {str(e)}"
        )


# Mood Coefficient Endpoints
@app.get("/mood/{uid}/coefficient/current")
async def get_current_mood_coefficient(
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
        coefficient = mood_tracking_system.get_current_mood_coefficient(uid)
        today_entry = mood_tracking_system.get_mood_entry(uid, date.today())
        
        return {
            "uid": uid,
            "date": date.today().isoformat(),
            "mood_coefficient": coefficient,
            "has_today_log": today_entry is not None,
            "overall_mood": today_entry.overall_mood.value if today_entry else None,
            "coefficient_range": {"min": 0.8, "max": 1.2},
            "description": "XP計算0.8-1.2?"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get mood coefficient error: {str(e)}"
        )


@app.get("/mood/{uid}/coefficient/date/{target_date}")
async def get_mood_coefficient_by_date(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    target_date: str = Path(..., description="?YYYY-MM-DD?")
) -> Dict[str, Any]:
    """
    ?
    
    Args:
        uid: ユーザーID
        target_date: ?
        
    Returns:
        Dict[str, Any]: ?
        
    Raises:
        HTTPException: ?
    """
    try:
        target_date_obj = date.fromisoformat(target_date)
        coefficient = mood_tracking_system.get_mood_coefficient_for_date(uid, target_date_obj)
        mood_entry = mood_tracking_system.get_mood_entry(uid, target_date_obj)
        
        return {
            "uid": uid,
            "date": target_date,
            "mood_coefficient": coefficient,
            "has_mood_log": mood_entry is not None,
            "overall_mood": mood_entry.overall_mood.value if mood_entry else None,
            "coefficient_range": {"min": 0.8, "max": 1.2},
            "is_default": mood_entry is None
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get mood coefficient by date error: {str(e)}"
        )

# Mood Analysis Endpoints
@app.get("/mood/{uid}/trend", response_model=MoodTrendResponse)
async def get_mood_trend(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    days: int = Query(30, ge=7, le=365, description="?")
) -> MoodTrendResponse:
    """
    気分
    
    Args:
        uid: ユーザーID
        days: ?
        
    Returns:
        MoodTrendResponse: 気分
    """
    try:
        mood_trend = mood_tracking_system.analyze_mood_trend(uid, days)
        return mood_trend_to_response(mood_trend)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood trend analysis error: {str(e)}"
        )


@app.get("/mood/{uid}/insights")
async def get_mood_insights(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Dict[str, Any]:
    """
    気分
    
    Args:
        uid: ユーザーID
        
    Returns:
        Dict[str, Any]: 気分
    """
    try:
        insights = mood_tracking_system.get_mood_insights(uid)
        return {
            "uid": uid,
            "generated_at": datetime.now().isoformat(),
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood insights error: {str(e)}"
        )


@app.get("/mood/{uid}/statistics")
async def get_mood_statistics(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    days: int = Query(30, ge=1, le=365, description="?")
) -> Dict[str, Any]:
    """
    気分
    
    Args:
        uid: ユーザーID
        days: ?
        
    Returns:
        Dict[str, Any]: 気分
    """
    try:
        recent_entries = mood_tracking_system.get_recent_mood_entries(uid, days)
        
        if not recent_entries:
            return {
                "uid": uid,
                "period_days": days,
                "total_entries": 0,
                "message": "気分"
            }
        
        # 基本
        total_entries = len(recent_entries)
        overall_moods = [entry.overall_mood.value for entry in recent_entries]
        
        # カスタム
        category_averages = {}
        for category in MoodCategory:
            if category == MoodCategory.OVERALL:
                category_averages[category.value] = sum(overall_moods) / len(overall_moods)
            elif category == MoodCategory.ENERGY:
                category_averages[category.value] = sum(entry.energy_level.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.MOTIVATION:
                category_averages[category.value] = sum(entry.motivation_level.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.FOCUS:
                category_averages[category.value] = sum(entry.focus_level.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.ANXIETY:
                category_averages[category.value] = sum(6 - entry.anxiety_level.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.STRESS:
                category_averages[category.value] = sum(6 - entry.stress_level.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.SOCIAL:
                category_averages[category.value] = sum(entry.social_mood.value for entry in recent_entries) / total_entries
            elif category == MoodCategory.PHYSICAL:
                category_averages[category.value] = sum(entry.physical_condition.value for entry in recent_entries) / total_entries
        
        # ?
        trigger_counts = {}
        for entry in recent_entries:
            for trigger in entry.mood_triggers:
                trigger_counts[trigger.value] = trigger_counts.get(trigger.value, 0) + 1
        
        # 気分
        mood_coefficients = [entry.get_weighted_mood_coefficient() for entry in recent_entries]
        
        return {
            "uid": uid,
            "period_days": days,
            "total_entries": total_entries,
            "logging_rate": total_entries / days,
            "category_averages": category_averages,
            "mood_distribution": {
                "very_low": sum(1 for mood in overall_moods if mood == 1),
                "low": sum(1 for mood in overall_moods if mood == 2),
                "neutral": sum(1 for mood in overall_moods if mood == 3),
                "high": sum(1 for mood in overall_moods if mood == 4),
                "very_high": sum(1 for mood in overall_moods if mood == 5)
            },
            "trigger_analysis": dict(sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)),
            "mood_coefficient_stats": {
                "average": sum(mood_coefficients) / len(mood_coefficients),
                "minimum": min(mood_coefficients),
                "maximum": max(mood_coefficients),
                "range": max(mood_coefficients) - min(mood_coefficients)
            },
            "sleep_exercise_correlation": {
                "entries_with_sleep": sum(1 for entry in recent_entries if entry.sleep_hours is not None),
                "entries_with_exercise": sum(1 for entry in recent_entries if entry.exercise_minutes is not None),
                "avg_sleep_hours": sum(entry.sleep_hours for entry in recent_entries if entry.sleep_hours) / 
                                 sum(1 for entry in recent_entries if entry.sleep_hours) if any(entry.sleep_hours for entry in recent_entries) else None,
                "avg_exercise_minutes": sum(entry.exercise_minutes for entry in recent_entries if entry.exercise_minutes) / 
                                      sum(1 for entry in recent_entries if entry.exercise_minutes) if any(entry.exercise_minutes for entry in recent_entries) else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood statistics error: {str(e)}"
        )


# Reminder Management Endpoints
@app.post("/mood/{uid}/reminder")
async def set_mood_reminder(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: ReminderSettingsRequest = Body(..., description="リスト")
) -> Dict[str, Any]:
    """
    気分
    
    Args:
        uid: ユーザーID
        request: リスト
        
    Returns:
        Dict[str, Any]: 設定
    """
    try:
        mood_tracking_system.set_daily_reminder(uid, request.enabled)
        
        return {
            "uid": uid,
            "reminder_enabled": request.enabled,
            "message": f"気分{'?' if request.enabled else '無'}に"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Set reminder error: {str(e)}"
        )


@app.get("/mood/{uid}/reminder")
async def get_mood_reminder_status(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50)
) -> Dict[str, Any]:
    """
    気分
    
    Args:
        uid: ユーザーID
        
    Returns:
        Dict[str, Any]: リスト
    """
    try:
        reminder_enabled = mood_tracking_system.daily_reminders.get(uid, False)
        today_logged = mood_tracking_system.get_mood_entry(uid, date.today()) is not None
        
        return {
            "uid": uid,
            "reminder_enabled": reminder_enabled,
            "today_logged": today_logged,
            "needs_reminder": reminder_enabled and not today_logged
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get reminder status error: {str(e)}"
        )


# Data Export Endpoints
@app.get("/mood/{uid}/export")
async def export_mood_data(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    start_date: str = Query(..., description="?YYYY-MM-DD?"),
    end_date: str = Query(..., description="終YYYY-MM-DD?"),
    format: str = Query("json", description="エラーjson/csv?")
) -> Any:
    """
    気分
    
    Args:
        uid: ユーザーID
        start_date: ?
        end_date: 終
        format: エラー
        
    Returns:
        Any: エラー
        
    Raises:
        HTTPException: ?
    """
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
        
        if start_date_obj > end_date_obj:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )
        
        exported_data = mood_tracking_system.export_mood_data(uid, start_date_obj, end_date_obj)
        
        if format.lower() == "csv":
            # CSV?
            import io
            import csv
            from fastapi.responses import StreamingResponse
            
            if not exported_data:
                raise HTTPException(
                    status_code=404,
                    detail="No mood data found for the specified period"
                )
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=exported_data[0].keys())
            writer.writeheader()
            writer.writerows(exported_data)
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=mood_data_{uid}_{start_date}_{end_date}.csv"}
            )
        else:
            # JSON?
            return {
                "uid": uid,
                "start_date": start_date,
                "end_date": end_date,
                "total_entries": len(exported_data),
                "data": exported_data
            }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export mood data error: {str(e)}"
        )


# XP Integration Endpoints
@app.get("/mood/{uid}/coefficient/for-xp")
async def get_mood_coefficient_for_xp(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    task_difficulty: int = Query(1, ge=1, le=5, description="タスク"),
    base_xp: int = Query(10, ge=1, le=1000, description="基本XP")
) -> Dict[str, Any]:
    """
    XP計算XPを
    
    Args:
        uid: ユーザーID
        task_difficulty: タスク
        base_xp: 基本XP
        
    Returns:
        Dict[str, Any]: XP計算
    """
    try:
        # ?
        mood_coefficient = mood_tracking_system.get_current_mood_coefficient(uid)
        today_entry = mood_tracking_system.get_mood_entry(uid, date.today())
        
        # XP?
        adjusted_xp = int(base_xp * mood_coefficient)
        
        return {
            "uid": uid,
            "date": date.today().isoformat(),
            "mood_coefficient": mood_coefficient,
            "base_xp": base_xp,
            "adjusted_xp": adjusted_xp,
            "xp_bonus": adjusted_xp - base_xp,
            "has_mood_log": today_entry is not None,
            "overall_mood": today_entry.overall_mood.value if today_entry else None,
            "mood_summary": today_entry.get_mood_summary() if today_entry else "気分",
            "calculation_details": {
                "formula": "base_xp ? mood_coefficient",
                "coefficient_range": {"min": 0.8, "max": 1.2},
                "mood_impact": "positive" if mood_coefficient > 1.0 else "negative" if mood_coefficient < 1.0 else "neutral"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"XP coefficient calculation error: {str(e)}"
        )


@app.post("/mood/{uid}/xp-integration")
async def integrate_mood_with_xp(
    uid: str = Path(..., description="ユーザーID", min_length=1, max_length=50),
    request: Dict[str, Any] = Body(..., description="XP?")
) -> Dict[str, Any]:
    """
    気分XP計算
    
    Args:
        uid: ユーザーID
        request: XP?
        
    Returns:
        Dict[str, Any]: ?
    """
    try:
        task_type = request.get('task_type', 'one_shot')
        base_xp = request.get('base_xp', 10)
        task_difficulty = request.get('task_difficulty', 1)
        
        # ?
        mood_coefficient = mood_tracking_system.get_current_mood_coefficient(uid)
        today_entry = mood_tracking_system.get_mood_entry(uid, date.today())
        
        # XP?
        adjusted_xp = int(base_xp * mood_coefficient)
        
        # 気分
        recent_entries = mood_tracking_system.get_recent_mood_entries(uid, 7)
        mood_trend = mood_tracking_system.analyze_mood_trend(uid, 7) if recent_entries else None
        
        # 治療
        therapeutic_feedback = generate_therapeutic_feedback(
            today_entry, mood_trend, adjusted_xp, base_xp
        )
        
        return {
            "uid": uid,
            "integration_result": {
                "base_xp": base_xp,
                "mood_coefficient": mood_coefficient,
                "adjusted_xp": adjusted_xp,
                "xp_bonus": adjusted_xp - base_xp,
                "task_type": task_type,
                "task_difficulty": task_difficulty
            },
            "mood_context": {
                "has_today_log": today_entry is not None,
                "overall_mood": today_entry.overall_mood.value if today_entry else None,
                "mood_summary": today_entry.get_mood_summary() if today_entry else "気分",
                "recent_entries_count": len(recent_entries),
                "trend_direction": mood_trend.overall_trend if mood_trend else 0
            },
            "therapeutic_feedback": therapeutic_feedback,
            "recommendations": generate_mood_based_recommendations(today_entry, mood_coefficient)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood-XP integration error: {str(e)}"
        )


def generate_therapeutic_feedback(
    mood_entry: Optional[MoodEntry], 
    mood_trend: Optional[MoodTrend], 
    adjusted_xp: int, 
    base_xp: int
) -> Dict[str, Any]:
    """治療"""
    feedback = {
        "message": "",
        "encouragement": "",
        "insights": [],
        "mood_impact": ""
    }
    
    if not mood_entry:
        feedback["message"] = "?XP?"
        feedback["encouragement"] = "気分"
        return feedback
    
    mood_level = mood_entry.overall_mood.value
    xp_bonus = adjusted_xp - base_xp
    
    # 気分
    if mood_level >= 4:
        feedback["message"] = f"?XP +{xp_bonus} を"
        feedback["encouragement"] = "こ"
        feedback["mood_impact"] = "positive"
    elif mood_level == 3:
        feedback["message"] = "?"
        feedback["encouragement"] = "安全"
        feedback["mood_impact"] = "neutral"
    else:
        feedback["message"] = f"?"
        feedback["encouragement"] = "?"
        feedback["mood_impact"] = "challenging"
    
    # ?
    if mood_trend:
        if mood_trend.overall_trend > 0.1:
            feedback["insights"].append("?")
        elif mood_trend.overall_trend < -0.1:
            feedback["insights"].append("?")
        else:
            feedback["insights"].append("気分")
    
    # ?
    if mood_entry.energy_level.value <= 2:
        feedback["insights"].append("エラー")
    if mood_entry.anxiety_level.value <= 2:
        feedback["insights"].append("?")
    if mood_entry.motivation_level.value >= 4:
        feedback["insights"].append("や")
    
    return feedback


def generate_mood_based_recommendations(
    mood_entry: Optional[MoodEntry], 
    mood_coefficient: float
) -> List[str]:
    """気分"""
    recommendations = []
    
    if not mood_entry:
        recommendations.append("?")
        recommendations.append("気分")
        return recommendations
    
    mood_level = mood_entry.overall_mood.value
    
    # 気分
    if mood_level >= 4:
        recommendations.append("?")
        recommendations.append("?")
    elif mood_level == 3:
        recommendations.append("安全")
        recommendations.append("?")
    else:
        recommendations.append("無")
        recommendations.append("?")
    
    # ?
    if mood_entry.energy_level.value <= 2:
        recommendations.append("エラー")
    if mood_entry.anxiety_level.value <= 2:
        recommendations.append("?")
    if mood_entry.focus_level.value <= 2:
        recommendations.append("?")
    if mood_entry.social_mood.value <= 2:
        recommendations.append("?")
    
    return recommendations


# System Management Endpoints
@app.get("/mood/system/reminders")
async def get_users_needing_reminder() -> Dict[str, Any]:
    """
    リスト
    
    Returns:
        Dict[str, Any]: リスト
    """
    try:
        users_needing_reminder = mood_tracking_system.get_users_needing_reminder()
        
        return {
            "date": date.today().isoformat(),
            "users_needing_reminder": users_needing_reminder,
            "total_count": len(users_needing_reminder)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Get users needing reminder error: {str(e)}"
        )


@app.get("/mood/system/statistics")
async def get_system_mood_statistics() -> Dict[str, Any]:
    """
    システム
    
    Returns:
        Dict[str, Any]: システム
    """
    try:
        total_users = len(mood_tracking_system.mood_entries)
        total_entries = sum(len(entries) for entries in mood_tracking_system.mood_entries.values())
        
        # ?
        today = date.today()
        today_logged_users = sum(
            1 for uid in mood_tracking_system.mood_entries.keys()
            if mood_tracking_system.get_mood_entry(uid, today) is not None
        )
        
        # リスト
        reminder_enabled_users = sum(1 for enabled in mood_tracking_system.daily_reminders.values() if enabled)
        
        return {
            "total_users": total_users,
            "total_mood_entries": total_entries,
            "today_logged_users": today_logged_users,
            "reminder_enabled_users": reminder_enabled_users,
            "average_entries_per_user": total_entries / total_users if total_users > 0 else 0,
            "today_logging_rate": today_logged_users / total_users if total_users > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"System statistics error: {str(e)}"
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """ヘルパー"""
    return {"status": "healthy", "service": "mood-tracking"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)