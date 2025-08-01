"""
Alpha Playtest Service - ? (n=50) システム
?
- ?
- ?
- リスト
- ?
- A/B?
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta, date
from enum import Enum
import logging
import uuid
import json
import asyncio
import hashlib
import statistics
from collections import defaultdict, Counter
import random

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="Alpha Playtest Service", version="1.0.0")
logger = logging.getLogger(__name__)

class TestUserStatus(Enum):
    INVITED = "invited"           # ?
    ACTIVE = "active"             # アプリ
    INACTIVE = "inactive"         # ?
    COMPLETED = "completed"       # ?
    DROPPED = "dropped"           # ?

class FeedbackType(Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    USABILITY = "usability"
    THERAPEUTIC_EFFECT = "therapeutic_effect"
    GENERAL = "general"

class ABTestVariant(Enum):
    CONTROL = "control"           # コア
    VARIANT_A = "variant_a"       # バリデーションA
    VARIANT_B = "variant_b"       # バリデーションB

class TestUser(BaseModel):
    user_id: str
    email: str = Field(..., description="?")
    status: TestUserStatus
    assigned_variant: ABTestVariant
    registration_date: datetime
    last_active_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    demographics: Dict[str, Any] = Field(default_factory=dict)
    consent_given: bool = True
    privacy_settings: Dict[str, bool] = Field(default_factory=dict)

class BehaviorLog(BaseModel):
    log_id: str
    user_id: str
    session_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    screen_name: Optional[str] = None
    user_agent: Optional[str] = None
    anonymized: bool = True

class UserFeedback(BaseModel):
    feedback_id: str
    user_id: str
    feedback_type: FeedbackType
    title: str
    content: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    sentiment_score: Optional[float] = None
    themes: List[str] = Field(default_factory=list)
    created_at: datetime
    processed: bool = False

class ABTestResult(BaseModel):
    test_id: str
    metric_name: str
    control_value: float
    variant_a_value: float
    variant_b_value: float
    statistical_significance: float
    confidence_interval: Dict[str, Dict[str, float]]
    sample_sizes: Dict[str, int]
    test_duration_days: int

class PlaytestAnalytics(BaseModel):
    total_users: int
    active_users: int
    completion_rate: float
    average_session_duration: float
    retention_rates: Dict[str, float]
    feature_usage: Dict[str, float]
    bug_reports_count: int
    satisfaction_score: float

class AlphaPlaytestEngine:
    """?"""
    
    def __init__(self):
        self.test_users: Dict[str, TestUser] = {}
        self.behavior_logs: List[BehaviorLog] = []
        self.feedback_data: List[UserFeedback] = []
        self.ab_tests: Dict[str, Dict] = {}
        self.analytics_cache = {}
        self.max_test_users = 50
        
        # プレビュー
        self.privacy_config = {
            "anonymize_ips": True,
            "hash_emails": True,
            "data_retention_days": 90,
            "consent_required": True
        }
        
        self._initialize_ab_tests()
    
    def _initialize_ab_tests(self):
        """A/B?"""
        self.ab_tests = {
            "onboarding_flow": {
                "name": "?",
                "description": "?",
                "variants": {
                    ABTestVariant.CONTROL: "?",
                    ABTestVariant.VARIANT_A: "?",
                    ABTestVariant.VARIANT_B: "?"
                },
                "metrics": ["completion_rate", "time_to_first_task", "user_satisfaction"],
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30)
            },
            "task_recommendation": {
                "name": "タスク",
                "description": "AI?",
                "variants": {
                    ABTestVariant.CONTROL: "?",
                    ABTestVariant.VARIANT_A: "?",
                    ABTestVariant.VARIANT_B: "?"
                },
                "metrics": ["task_completion_rate", "user_engagement", "therapeutic_progress"],
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30)
            },
            "gamification_elements": {
                "name": "ゲーム",
                "description": "ゲーム",
                "variants": {
                    ABTestVariant.CONTROL: "?",
                    ABTestVariant.VARIANT_A: "?",
                    ABTestVariant.VARIANT_B: "?RPG?"
                },
                "metrics": ["retention_rate", "session_duration", "therapeutic_outcomes"],
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30)
            }
        }
    
    async def register_test_user(self, email: str, demographics: Dict[str, Any] = None) -> TestUser:
        """?"""
        if len(self.test_users) >= self.max_test_users:
            raise HTTPException(status_code=400, detail="?")
        
        # メイン
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        
        # A/B?
        variant = self._assign_ab_variant()
        
        # ユーザー
        user = TestUser(
            user_id=str(uuid.uuid4()),
            email=email_hash,
            status=TestUserStatus.INVITED,
            assigned_variant=variant,
            registration_date=datetime.now(),
            demographics=demographics or {},
            privacy_settings={
                "data_collection": True,
                "analytics": True,
                "feedback_collection": True
            }
        )
        
        self.test_users[user.user_id] = user
        
        logger.info(f"Test user registered: {user.user_id} (variant: {variant.value})")
        return user
    
    def _assign_ab_variant(self) -> ABTestVariant:
        """A/B?"""
        # ?
        variant_counts = Counter(user.assigned_variant for user in self.test_users.values())
        
        # ?
        for variant in ABTestVariant:
            if variant not in variant_counts:
                variant_counts[variant] = 0
        
        # ?
        min_count = min(variant_counts.values())
        available_variants = [
            variant for variant in ABTestVariant
            if variant_counts[variant] == min_count
        ]
        
        return random.choice(available_variants)
    
    async def log_user_behavior(self, user_id: str, event_type: str, 
                               event_data: Dict[str, Any], session_id: str = None) -> bool:
        """ユーザー"""
        if user_id not in self.test_users:
            raise HTTPException(status_code=404, detail="?")
        
        user = self.test_users[user_id]
        
        # プレビュー
        if not user.privacy_settings.get("data_collection", False):
            return False
        
        # デフォルト
        anonymized_data = await self._anonymize_event_data(event_data)
        
        # ログ
        log = BehaviorLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            event_type=event_type,
            event_data=anonymized_data,
            timestamp=datetime.now(),
            anonymized=True
        )
        
        self.behavior_logs.append(log)
        
        # ユーザー
        user.last_active_date = datetime.now()
        if user.status == TestUserStatus.INVITED:
            user.status = TestUserStatus.ACTIVE
        
        # ログ
        await self._cleanup_old_logs()
        
        return True
    
    async def _anonymize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """?"""
        anonymized = event_data.copy()
        
        # ?
        sensitive_keys = ["email", "phone", "address", "name", "ip_address"]
        for key in sensitive_keys:
            if key in anonymized:
                del anonymized[key]
        
        # ?
        if "location" in anonymized:
            location = anonymized["location"]
            if isinstance(location, dict) and "lat" in location and "lng" in location:
                # ?1km?
                anonymized["location"] = {
                    "lat": round(location["lat"], 2),
                    "lng": round(location["lng"], 2)
                }
        
        # タスク
        if "timestamp" in anonymized:
            timestamp = anonymized["timestamp"]
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp)
                    anonymized["timestamp"] = dt.replace(second=0, microsecond=0).isoformat()
                except:
                    pass
        
        return anonymized
    
    async def _cleanup_old_logs(self):
        """?"""
        cutoff_date = datetime.now() - timedelta(days=self.privacy_config["data_retention_days"])
        
        original_count = len(self.behavior_logs)
        self.behavior_logs = [
            log for log in self.behavior_logs
            if log.timestamp > cutoff_date
        ]
        
        deleted_count = original_count - len(self.behavior_logs)
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old behavior logs")
    
    async def collect_feedback(self, user_id: str, feedback_type: FeedbackType,
                              title: str, content: str, rating: int = None) -> UserFeedback:
        """?"""
        if user_id not in self.test_users:
            raise HTTPException(status_code=404, detail="?")
        
        user = self.test_users[user_id]
        
        # プレビュー
        if not user.privacy_settings.get("feedback_collection", False):
            raise HTTPException(status_code=403, detail="?")
        
        # ?
        sentiment_score = await self._analyze_sentiment(content)
        
        # ?
        themes = await self._extract_themes(content, feedback_type)
        
        # ?
        feedback = UserFeedback(
            feedback_id=str(uuid.uuid4()),
            user_id=user_id,
            feedback_type=feedback_type,
            title=title,
            content=content,
            rating=rating,
            sentiment_score=sentiment_score,
            themes=themes,
            created_at=datetime.now()
        )
        
        self.feedback_data.append(feedback)
        
        logger.info(f"Feedback collected: {feedback.feedback_id} (type: {feedback_type.value})")
        return feedback
    
    async def _analyze_sentiment(self, text: str) -> float:
        """?"""
        # 実装
        positive_words = ["?", "?", "?", "?", "?", "?", "?"]
        negative_words = ["?", "?", "?", "?", "バリデーション", "?", "?"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.5
        
        # -1?1?
        score = (positive_count - negative_count) / max(total_words, 1)
        return max(-1.0, min(1.0, score))
    
    async def _extract_themes(self, text: str, feedback_type: FeedbackType) -> List[str]:
        """?"""
        themes = []
        
        # ?
        theme_keywords = {
            FeedbackType.BUG_REPORT: {
                "crash": "アプリ",
                "login": "ログ",
                "sync": "デフォルト",
                "performance": "?"
            },
            FeedbackType.USABILITY: {
                "navigation": "?",
                "ui": "ユーザー",
                "accessibility": "アプリ",
                "onboarding": "?"
            },
            FeedbackType.THERAPEUTIC_EFFECT: {
                "mood": "気分",
                "motivation": "モデル",
                "habit": "?",
                "progress": "?"
            }
        }
        
        keywords = theme_keywords.get(feedback_type, {})
        text_lower = text.lower()
        
        for keyword, theme in keywords.items():
            if keyword in text_lower:
                themes.append(theme)
        
        return themes
    
    async def generate_improvement_suggestions(self, feedback_list: List[UserFeedback]) -> List[str]:
        """?"""
        suggestions = []
        
        # ?
        type_counts = Counter(fb.feedback_type for fb in feedback_list)
        
        # ?
        all_themes = []
        for fb in feedback_list:
            all_themes.extend(fb.themes)
        theme_counts = Counter(all_themes)
        
        # ?
        sentiment_scores = [fb.sentiment_score for fb in feedback_list if fb.sentiment_score is not None]
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
        
        # ?
        if type_counts[FeedbackType.BUG_REPORT] > len(feedback_list) * 0.3:
            suggestions.append("バリデーション")
        
        if type_counts[FeedbackType.USABILITY] > len(feedback_list) * 0.2:
            suggestions.append("ユーザーUI/UX?")
        
        if avg_sentiment < -0.2:
            suggestions.append("?")
        
        # ?
        for theme, count in theme_counts.most_common(3):
            if count > 2:
                suggestions.append(f"?{theme}?")
        
        return suggestions[:5]  # ?5つ
    
    async def run_ab_test_analysis(self, test_id: str) -> ABTestResult:
        """A/B?"""
        if test_id not in self.ab_tests:
            raise HTTPException(status_code=404, detail="A/B?")
        
        test_config = self.ab_tests[test_id]
        
        # バリデーション
        variant_users = {
            ABTestVariant.CONTROL: [],
            ABTestVariant.VARIANT_A: [],
            ABTestVariant.VARIANT_B: []
        }
        
        for user in self.test_users.values():
            variant_users[user.assigned_variant].append(user)
        
        # メイン
        metric_name = "completion_rate"
        control_value = await self._calculate_completion_rate(variant_users[ABTestVariant.CONTROL])
        variant_a_value = await self._calculate_completion_rate(variant_users[ABTestVariant.VARIANT_A])
        variant_b_value = await self._calculate_completion_rate(variant_users[ABTestVariant.VARIANT_B])
        
        # ?
        significance = await self._calculate_statistical_significance(
            control_value, variant_a_value, variant_b_value,
            len(variant_users[ABTestVariant.CONTROL]),
            len(variant_users[ABTestVariant.VARIANT_A]),
            len(variant_users[ABTestVariant.VARIANT_B])
        )
        
        # 信頼
        confidence_interval = {
            "control": {"lower": control_value - 0.05, "upper": control_value + 0.05},
            "variant_a": {"lower": variant_a_value - 0.05, "upper": variant_a_value + 0.05},
            "variant_b": {"lower": variant_b_value - 0.05, "upper": variant_b_value + 0.05}
        }
        
        test_duration = (datetime.now() - test_config["start_date"]).days
        
        result = ABTestResult(
            test_id=test_id,
            metric_name=metric_name,
            control_value=control_value,
            variant_a_value=variant_a_value,
            variant_b_value=variant_b_value,
            statistical_significance=significance,
            confidence_interval=confidence_interval,
            sample_sizes={
                "control": len(variant_users[ABTestVariant.CONTROL]),
                "variant_a": len(variant_users[ABTestVariant.VARIANT_A]),
                "variant_b": len(variant_users[ABTestVariant.VARIANT_B])
            },
            test_duration_days=test_duration
        )
        
        return result
    
    async def _calculate_completion_rate(self, users: List[TestUser]) -> float:
        """?"""
        if not users:
            return 0.0
        
        completed_users = [u for u in users if u.status == TestUserStatus.COMPLETED]
        return len(completed_users) / len(users)
    
    async def _calculate_statistical_significance(self, control: float, variant_a: float, 
                                                variant_b: float, n_control: int, 
                                                n_a: int, n_b: int) -> float:
        """?"""
        # 実装
        # こ
        
        if n_control == 0 or n_a == 0 or n_b == 0:
            return 0.0
        
        # ?
        effect_size_a = abs(variant_a - control)
        effect_size_b = abs(variant_b - control)
        
        # ?
        min_sample_size = min(n_control, n_a, n_b)
        sample_factor = min(1.0, min_sample_size / 20)  # 20?
        
        # ?0-1?
        max_effect = max(effect_size_a, effect_size_b)
        significance = min(1.0, max_effect * 10 * sample_factor)
        
        return significance
    
    async def generate_analytics_report(self) -> PlaytestAnalytics:
        """?"""
        total_users = len(self.test_users)
        active_users = len([u for u in self.test_users.values() if u.status == TestUserStatus.ACTIVE])
        
        # ?
        completed_users = len([u for u in self.test_users.values() if u.status == TestUserStatus.COMPLETED])
        completion_rate = completed_users / total_users if total_users > 0 else 0.0
        
        # ?
        session_durations = await self._calculate_session_durations()
        avg_session_duration = statistics.mean(session_durations) if session_durations else 0.0
        
        # リスト
        retention_rates = await self._calculate_retention_rates()
        
        # ?
        feature_usage = await self._calculate_feature_usage()
        
        # バリデーション
        bug_reports = len([fb for fb in self.feedback_data if fb.feedback_type == FeedbackType.BUG_REPORT])
        
        # ?
        ratings = [fb.rating for fb in self.feedback_data if fb.rating is not None]
        satisfaction_score = statistics.mean(ratings) if ratings else 0.0
        
        return PlaytestAnalytics(
            total_users=total_users,
            active_users=active_users,
            completion_rate=completion_rate,
            average_session_duration=avg_session_duration,
            retention_rates=retention_rates,
            feature_usage=feature_usage,
            bug_reports_count=bug_reports,
            satisfaction_score=satisfaction_score
        )
    
    async def _calculate_session_durations(self) -> List[float]:
        """?"""
        # ?
        session_logs = defaultdict(list)
        for log in self.behavior_logs:
            session_logs[log.session_id].append(log)
        
        durations = []
        for session_id, logs in session_logs.items():
            if len(logs) >= 2:
                logs.sort(key=lambda x: x.timestamp)
                duration = (logs[-1].timestamp - logs[0].timestamp).total_seconds() / 60  # ?
                durations.append(duration)
            elif len(logs) == 1:
                # ?durationを
                log = logs[0]
                if "duration" in log.event_data:
                    durations.append(log.event_data["duration"] / 60)  # ?
        
        return durations
    
    async def _calculate_retention_rates(self) -> Dict[str, float]:
        """リスト"""
        retention_rates = {}
        
        for days in [1, 3, 7, 14, 30]:
            cutoff_date = datetime.now() - timedelta(days=days)
            eligible_users = [
                u for u in self.test_users.values()
                if u.registration_date <= cutoff_date
            ]
            
            if eligible_users:
                retained_users = [
                    u for u in eligible_users
                    if u.last_active_date and u.last_active_date >= cutoff_date
                ]
                retention_rates[f"day_{days}"] = len(retained_users) / len(eligible_users)
            else:
                retention_rates[f"day_{days}"] = 0.0
        
        return retention_rates
    
    async def _calculate_feature_usage(self) -> Dict[str, float]:
        """?"""
        feature_usage = defaultdict(int)
        total_events = len(self.behavior_logs)
        
        for log in self.behavior_logs:
            event_type = log.event_type
            feature_usage[event_type] += 1
        
        # 使用
        usage_rates = {}
        for feature, count in feature_usage.items():
            usage_rates[feature] = count / total_events if total_events > 0 else 0.0
        
        return dict(usage_rates)

# ?
playtest_engine = AlphaPlaytestEngine()

# APIエラー
@app.post("/playtest/users/register")
async def register_test_user(email: str, demographics: Dict[str, Any] = None):
    """?"""
    try:
        user = await playtest_engine.register_test_user(email, demographics)
        return {
            "user_id": user.user_id,
            "status": user.status.value,
            "assigned_variant": user.assigned_variant.value,
            "registration_date": user.registration_date.isoformat()
        }
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=500, detail="ユーザー")

@app.post("/playtest/behavior/log")
async def log_behavior(user_id: str, event_type: str, event_data: Dict[str, Any], 
                      session_id: str = None):
    """?"""
    success = await playtest_engine.log_user_behavior(user_id, event_type, event_data, session_id)
    return {"logged": success}

@app.post("/playtest/feedback/submit")
async def submit_feedback(user_id: str, feedback_type: str, title: str, 
                         content: str, rating: int = None):
    """?"""
    try:
        feedback_type_enum = FeedbackType(feedback_type)
        feedback = await playtest_engine.collect_feedback(
            user_id, feedback_type_enum, title, content, rating
        )
        return {
            "feedback_id": feedback.feedback_id,
            "sentiment_score": feedback.sentiment_score,
            "themes": feedback.themes
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="無")

@app.get("/playtest/analytics/report")
async def get_analytics_report():
    """?"""
    report = await playtest_engine.generate_analytics_report()
    return report

@app.get("/playtest/abtest/{test_id}/results")
async def get_ab_test_results(test_id: str):
    """A/B?"""
    results = await playtest_engine.run_ab_test_analysis(test_id)
    return results

@app.get("/playtest/abtest/list")
async def list_ab_tests():
    """A/B?"""
    return {
        "tests": [
            {
                "test_id": test_id,
                "name": config["name"],
                "description": config["description"],
                "variants": list(config["variants"].keys()),
                "metrics": config["metrics"],
                "start_date": config["start_date"].isoformat(),
                "end_date": config["end_date"].isoformat()
            }
            for test_id, config in playtest_engine.ab_tests.items()
        ]
    }

@app.get("/playtest/feedback/analysis")
async def get_feedback_analysis():
    """?"""
    # ?
    total_feedback = len(playtest_engine.feedback_data)
    type_distribution = Counter(fb.feedback_type for fb in playtest_engine.feedback_data)
    
    # ?
    sentiment_scores = [fb.sentiment_score for fb in playtest_engine.feedback_data if fb.sentiment_score is not None]
    avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
    
    # ?
    all_themes = []
    for fb in playtest_engine.feedback_data:
        all_themes.extend(fb.themes)
    theme_distribution = Counter(all_themes)
    
    # ?
    suggestions = await playtest_engine.generate_improvement_suggestions(playtest_engine.feedback_data)
    
    return {
        "total_feedback": total_feedback,
        "type_distribution": dict(type_distribution),
        "average_sentiment": avg_sentiment,
        "theme_distribution": dict(theme_distribution.most_common(10)),
        "improvement_suggestions": suggestions
    }

@app.get("/playtest/users/status")
async def get_users_status():
    """ユーザー"""
    status_distribution = Counter(user.status for user in playtest_engine.test_users.values())
    variant_distribution = Counter(user.assigned_variant for user in playtest_engine.test_users.values())
    
    return {
        "total_users": len(playtest_engine.test_users),
        "status_distribution": dict(status_distribution),
        "variant_distribution": dict(variant_distribution),
        "max_users": playtest_engine.max_test_users
    }

@app.get("/playtest/health")
async def health_check():
    """ヘルパー"""
    return {
        "status": "healthy",
        "total_users": len(playtest_engine.test_users),
        "behavior_logs": len(playtest_engine.behavior_logs),
        "feedback_count": len(playtest_engine.feedback_data),
        "ab_tests": len(playtest_engine.ab_tests)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)