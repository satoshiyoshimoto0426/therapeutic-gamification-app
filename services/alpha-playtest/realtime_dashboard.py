"""
リスト
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class DashboardMetric:
    """?"""
    name: str
    value: float
    unit: str
    trend: str  # "up", "down", "stable"
    change_percentage: float
    last_updated: datetime

@dataclass
class UserEngagementMetrics:
    """ユーザー"""
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    average_session_duration: float
    bounce_rate: float
    retention_rate_day_1: float
    retention_rate_day_7: float
    retention_rate_day_30: float

@dataclass
class FeatureUsageMetrics:
    """?"""
    feature_name: str
    usage_count: int
    unique_users: int
    average_time_spent: float
    completion_rate: float
    error_rate: float

@dataclass
class FeedbackMetrics:
    """?"""
    total_feedback: int
    average_rating: float
    sentiment_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    response_rate: float

class RealTimeDashboard:
    """リスト"""
    
    def __init__(self, playtest_engine):
        self.playtest_engine = playtest_engine
        self.metrics_cache: Dict[str, Any] = {}
        self.update_interval = 30  # 30?
        self.historical_data: Dict[str, List[Dict]] = defaultdict(list)
        self.alert_thresholds = self._initialize_alert_thresholds()
        self.active_alerts: List[Dict] = []
        
    def _initialize_alert_thresholds(self) -> Dict[str, Dict]:
        """アプリ"""
        return {
            "user_engagement": {
                "daily_active_users_min": 5,
                "bounce_rate_max": 0.7,
                "average_session_duration_min": 300  # 5?
            },
            "system_performance": {
                "error_rate_max": 0.05,
                "response_time_max": 2000  # 2?
            },
            "feedback_quality": {
                "average_rating_min": 3.0,
                "negative_sentiment_max": 0.3
            }
        }
    
    async def start_real_time_updates(self):
        """リスト"""
        logger.info("Starting real-time dashboard updates")
        
        while True:
            try:
                await self.update_all_metrics()
                await self.check_alerts()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in dashboard update: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def update_all_metrics(self):
        """?"""
        timestamp = datetime.now()
        
        # ユーザー
        engagement_metrics = await self.calculate_user_engagement_metrics()
        self.metrics_cache["user_engagement"] = asdict(engagement_metrics)
        
        # ?
        feature_metrics = await self.calculate_feature_usage_metrics()
        self.metrics_cache["feature_usage"] = feature_metrics
        
        # ?
        feedback_metrics = await self.calculate_feedback_metrics()
        self.metrics_cache["feedback"] = asdict(feedback_metrics)
        
        # A/B?
        ab_test_metrics = await self.calculate_ab_test_metrics()
        self.metrics_cache["ab_tests"] = ab_test_metrics
        
        # システム
        performance_metrics = await self.calculate_performance_metrics()
        self.metrics_cache["performance"] = performance_metrics
        
        # ?
        self.historical_data["metrics"].append({
            "timestamp": timestamp.isoformat(),
            "data": self.metrics_cache.copy()
        })
        
        # ?24?
        cutoff_time = timestamp - timedelta(hours=24)
        self.historical_data["metrics"] = [
            entry for entry in self.historical_data["metrics"]
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        logger.debug(f"Dashboard metrics updated at {timestamp}")
    
    async def calculate_user_engagement_metrics(self) -> UserEngagementMetrics:
        """ユーザー"""
        now = datetime.now()
        
        # アプリ
        day_1_ago = now - timedelta(days=1)
        week_1_ago = now - timedelta(days=7)
        month_1_ago = now - timedelta(days=30)
        
        daily_active = set()
        weekly_active = set()
        monthly_active = set()
        
        for log in self.playtest_engine.behavior_logs:
            if log.timestamp >= day_1_ago:
                daily_active.add(log.user_id)
            if log.timestamp >= week_1_ago:
                weekly_active.add(log.user_id)
            if log.timestamp >= month_1_ago:
                monthly_active.add(log.user_id)
        
        # ?
        session_durations = await self.playtest_engine._calculate_session_durations()
        avg_session_duration = statistics.mean(session_durations) if session_durations else 0
        
        # バリデーション1つ
        session_event_counts = defaultdict(int)
        for log in self.playtest_engine.behavior_logs:
            session_event_counts[log.session_id] += 1
        
        single_event_sessions = sum(1 for count in session_event_counts.values() if count == 1)
        total_sessions = len(session_event_counts)
        bounce_rate = single_event_sessions / total_sessions if total_sessions > 0 else 0
        
        # リスト
        retention_rates = await self.playtest_engine._calculate_retention_rates()
        
        return UserEngagementMetrics(
            daily_active_users=len(daily_active),
            weekly_active_users=len(weekly_active),
            monthly_active_users=len(monthly_active),
            average_session_duration=avg_session_duration,
            bounce_rate=bounce_rate,
            retention_rate_day_1=retention_rates.get("day_1", 0),
            retention_rate_day_7=retention_rates.get("day_7", 0),
            retention_rate_day_30=retention_rates.get("day_30", 0)
        )
    
    async def calculate_feature_usage_metrics(self) -> List[Dict]:
        """?"""
        feature_stats = defaultdict(lambda: {
            "usage_count": 0,
            "unique_users": set(),
            "total_time": 0,
            "completions": 0,
            "errors": 0
        })
        
        # ログ
        for log in self.playtest_engine.behavior_logs:
            event_type = log.event_type
            stats = feature_stats[event_type]
            
            stats["usage_count"] += 1
            stats["unique_users"].add(log.user_id)
            
            # ?
            if "duration" in log.event_data:
                stats["total_time"] += log.event_data.get("duration", 0)
            
            if "completed" in log.event_data and log.event_data["completed"]:
                stats["completions"] += 1
            
            if "error" in log.event_data or log.event_type == "error_occurred":
                stats["errors"] += 1
        
        # メイン
        feature_metrics = []
        for feature_name, stats in feature_stats.items():
            unique_users_count = len(stats["unique_users"])
            
            feature_metrics.append({
                "feature_name": feature_name,
                "usage_count": stats["usage_count"],
                "unique_users": unique_users_count,
                "average_time_spent": stats["total_time"] / stats["usage_count"] if stats["usage_count"] > 0 else 0,
                "completion_rate": stats["completions"] / stats["usage_count"] if stats["usage_count"] > 0 else 0,
                "error_rate": stats["errors"] / stats["usage_count"] if stats["usage_count"] > 0 else 0
            })
        
        return sorted(feature_metrics, key=lambda x: x["usage_count"], reverse=True)
    
    async def calculate_feedback_metrics(self) -> FeedbackMetrics:
        """?"""
        feedback_data = self.playtest_engine.feedback_data
        
        if not feedback_data:
            return FeedbackMetrics(
                total_feedback=0,
                average_rating=0,
                sentiment_distribution={},
                category_distribution={},
                response_rate=0
            )
        
        # ?
        ratings = [fb.rating for fb in feedback_data if fb.rating is not None]
        average_rating = statistics.mean(ratings) if ratings else 0
        
        # ?
        sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        for fb in feedback_data:
            if fb.sentiment_score is not None:
                if fb.sentiment_score > 0.1:
                    sentiment_distribution["positive"] += 1
                elif fb.sentiment_score < -0.1:
                    sentiment_distribution["negative"] += 1
                else:
                    sentiment_distribution["neutral"] += 1
        
        # カスタム
        category_distribution = Counter(fb.feedback_type.value for fb in feedback_data)
        
        # ?
        active_users = len([u for u in self.playtest_engine.test_users.values() 
                          if u.status.value == "active"])
        feedback_users = len(set(fb.user_id for fb in feedback_data))
        response_rate = feedback_users / active_users if active_users > 0 else 0
        
        return FeedbackMetrics(
            total_feedback=len(feedback_data),
            average_rating=average_rating,
            sentiment_distribution=dict(sentiment_distribution),
            category_distribution=dict(category_distribution),
            response_rate=response_rate
        )
    
    async def calculate_ab_test_metrics(self) -> Dict[str, Any]:
        """A/B?"""
        ab_metrics = {}
        
        for test_id, test_config in self.playtest_engine.ab_tests.items():
            try:
                result = await self.playtest_engine.run_ab_test_analysis(test_id)
                
                ab_metrics[test_id] = {
                    "name": test_config["name"],
                    "control_value": result.control_value,
                    "variant_a_value": result.variant_a_value,
                    "variant_b_value": result.variant_b_value,
                    "statistical_significance": result.statistical_significance,
                    "sample_sizes": result.sample_sizes,
                    "test_duration_days": result.test_duration_days,
                    "winner": self._determine_ab_test_winner(result)
                }
            except Exception as e:
                logger.error(f"Error calculating A/B test metrics for {test_id}: {e}")
                ab_metrics[test_id] = {"error": str(e)}
        
        return ab_metrics
    
    def _determine_ab_test_winner(self, result) -> str:
        """A/B?"""
        if result.statistical_significance < 0.8:
            return "inconclusive"
        
        values = {
            "control": result.control_value,
            "variant_a": result.variant_a_value,
            "variant_b": result.variant_b_value
        }
        
        winner = max(values, key=values.get)
        return winner
    
    async def calculate_performance_metrics(self) -> Dict[str, Any]:
        """システム"""
        # エラー
        error_logs = [log for log in self.playtest_engine.behavior_logs 
                     if log.event_type == "error_occurred"]
        total_logs = len(self.playtest_engine.behavior_logs)
        error_rate = len(error_logs) / total_logs if total_logs > 0 else 0
        
        # レベル
        response_times = []
        for log in self.playtest_engine.behavior_logs:
            if "response_time" in log.event_data:
                response_times.append(log.event_data["response_time"])
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0
        
        # システム
        current_users = len([u for u in self.playtest_engine.test_users.values() 
                           if u.status.value == "active"])
        max_users = self.playtest_engine.max_test_users
        system_utilization = current_users / max_users
        
        return {
            "error_rate": error_rate,
            "average_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "system_utilization": system_utilization,
            "total_requests": total_logs,
            "error_count": len(error_logs)
        }
    
    async def check_alerts(self):
        """アプリ"""
        current_alerts = []
        
        # ユーザー
        engagement = self.metrics_cache.get("user_engagement", {})
        thresholds = self.alert_thresholds["user_engagement"]
        
        if engagement.get("daily_active_users", 0) < thresholds["daily_active_users_min"]:
            current_alerts.append({
                "type": "warning",
                "category": "user_engagement",
                "message": f"?: {engagement.get('daily_active_users', 0)}?",
                "timestamp": datetime.now().isoformat()
            })
        
        if engagement.get("bounce_rate", 0) > thresholds["bounce_rate_max"]:
            current_alerts.append({
                "type": "warning",
                "category": "user_engagement",
                "message": f"バリデーション: {engagement.get('bounce_rate', 0):.1%}",
                "timestamp": datetime.now().isoformat()
            })
        
        # システム
        performance = self.metrics_cache.get("performance", {})
        perf_thresholds = self.alert_thresholds["system_performance"]
        
        if performance.get("error_rate", 0) > perf_thresholds["error_rate_max"]:
            current_alerts.append({
                "type": "critical",
                "category": "system_performance",
                "message": f"エラー: {performance.get('error_rate', 0):.1%}",
                "timestamp": datetime.now().isoformat()
            })
        
        # ?
        feedback = self.metrics_cache.get("feedback", {})
        feedback_thresholds = self.alert_thresholds["feedback_quality"]
        
        if feedback.get("average_rating", 5) < feedback_thresholds["average_rating_min"]:
            current_alerts.append({
                "type": "warning",
                "category": "feedback_quality",
                "message": f"?: {feedback.get('average_rating', 0):.1f}/5.0",
                "timestamp": datetime.now().isoformat()
            })
        
        # ?
        new_alerts = [alert for alert in current_alerts if alert not in self.active_alerts]
        for alert in new_alerts:
            logger.warning(f"Alert: {alert['message']}")
        
        self.active_alerts = current_alerts
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """?"""
        return {
            "last_updated": datetime.now().isoformat(),
            "metrics": self.metrics_cache,
            "alerts": self.active_alerts,
            "update_interval": self.update_interval
        }
    
    def get_historical_data(self, hours: int = 24) -> Dict[str, Any]:
        """?"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_data = [
            entry for entry in self.historical_data["metrics"]
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        return {
            "period_hours": hours,
            "data_points": len(filtered_data),
            "historical_metrics": filtered_data
        }
    
    def export_dashboard_report(self, format: str = "json") -> str:
        """?"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_dashboard_data(),
            "historical_data": self.get_historical_data(24),
            "alert_summary": {
                "total_alerts": len(self.active_alerts),
                "critical_alerts": len([a for a in self.active_alerts if a["type"] == "critical"]),
                "warning_alerts": len([a for a in self.active_alerts if a["type"] == "warning"])
            }
        }
        
        if format == "json":
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        else:
            # ?CSV?PDFな
            return json.dumps(report_data, indent=2, ensure_ascii=False)

# ?
dashboard = None

def initialize_dashboard(playtest_engine):
    """?"""
    global dashboard
    dashboard = RealTimeDashboard(playtest_engine)
    return dashboard

def get_dashboard():
    """?"""
    return dashboard