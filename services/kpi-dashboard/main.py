"""
KPI Dashboard Service - デフォルト
?
- D1リスト 45%?
- 7? (state ? ACTION) 25%?
- 21? 12%?
- ARPMAU ?350?
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from enum import Enum
import logging
import uuid
import json
import asyncio
from collections import defaultdict

# 共有
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

app = FastAPI(title="KPI Dashboard Service", version="1.0.0")
logger = logging.getLogger(__name__)

class KPIMetricType(Enum):
    RETENTION = "retention"           # リスト
    ENGAGEMENT = "engagement"         # エラー
    THERAPEUTIC = "therapeutic"       # 治療
    REVENUE = "revenue"              # ?
    SAFETY = "safety"                # 安全

class UserState(Enum):
    APATHY = "APATHY"
    INTEREST = "INTEREST"
    ACTION = "ACTION"
    CONTINUATION = "CONTINUATION"
    HABITUATION = "HABITUATION"

class KPIMetric(BaseModel):
    metric_id: str
    name: str
    description: str
    metric_type: KPIMetricType
    current_value: float
    target_value: float
    unit: str  # "%", "?", "count", "score"
    trend: str  # "up", "down", "stable"
    last_updated: datetime
    alert_threshold: Optional[float] = None
    is_critical: bool = False

class UserEngagementData(BaseModel):
    user_id: str
    registration_date: date
    last_login_date: Optional[date] = None
    current_state: UserState
    consecutive_days: int
    total_sessions: int
    total_xp: int
    revenue_generated: float
    therapeutic_progress: Dict[str, float]
    safety_incidents: int

class KPIAlert(BaseModel):
    alert_id: str
    metric_id: str
    alert_type: str  # "threshold", "trend", "anomaly"
    severity: str    # "low", "medium", "high", "critical"
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

class KPIDashboardEngine:
    def __init__(self):
        self.user_data = {}  # 実装Firestore/BigQueryを
        self.kpi_metrics = {}
        self.alerts = {}
        self.historical_data = defaultdict(list)
        
        # ?
        self.target_values = {
            "d1_retention": 0.45,      # 45%
            "d7_continuation_rate": 0.25,  # 25%
            "d21_habituation_rate": 0.12,  # 12%
            "arpmau": 350.0            # ?350
        }
        
        self._initialize_kpi_metrics()
        self._generate_sample_data()

    def _initialize_kpi_metrics(self):
        """KPIメイン"""
        metrics = [
            # リスト
            KPIMetric(
                metric_id="d1_retention",
                name="D1リスト",
                description="?",
                metric_type=KPIMetricType.RETENTION,
                current_value=0.42,
                target_value=self.target_values["d1_retention"],
                unit="%",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=0.35,
                is_critical=True
            ),
            KPIMetric(
                metric_id="d7_retention",
                name="D7リスト",
                description="?7?",
                metric_type=KPIMetricType.RETENTION,
                current_value=0.28,
                target_value=0.30,
                unit="%",
                trend="stable",
                last_updated=datetime.now(),
                alert_threshold=0.20
            ),
            # エラー
            KPIMetric(
                metric_id="d7_continuation_rate",
                name="7? (ACTION?)",
                description="7?ACTION?",
                metric_type=KPIMetricType.ENGAGEMENT,
                current_value=0.23,
                target_value=self.target_values["d7_continuation_rate"],
                unit="%",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=0.18,
                is_critical=True
            ),
            KPIMetric(
                metric_id="daily_active_users",
                name="?",
                description="1?",
                metric_type=KPIMetricType.ENGAGEMENT,
                current_value=1250.0,
                target_value=1500.0,
                unit="count",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=1000.0
            ),
            # 治療
            KPIMetric(
                metric_id="d21_habituation_rate",
                name="21?",
                description="21?HABITUATION?",
                metric_type=KPIMetricType.THERAPEUTIC,
                current_value=0.11,
                target_value=self.target_values["d21_habituation_rate"],
                unit="%",
                trend="stable",
                last_updated=datetime.now(),
                alert_threshold=0.08,
                is_critical=True
            ),
            KPIMetric(
                metric_id="avg_self_efficacy_improvement",
                name="?",
                description="ユーザー",
                metric_type=KPIMetricType.THERAPEUTIC,
                current_value=0.68,
                target_value=0.70,
                unit="score",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=0.50
            ),
            KPIMetric(
                metric_id="cbt_engagement_rate",
                name="CBT?",
                description="CBT?",
                metric_type=KPIMetricType.THERAPEUTIC,
                current_value=0.74,
                target_value=0.80,
                unit="%",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=0.60
            ),
            # ?
            KPIMetric(
                metric_id="arpmau",
                name="ARPMAU (?)",
                description="?1?",
                metric_type=KPIMetricType.REVENUE,
                current_value=320.0,
                target_value=self.target_values["arpmau"],
                unit="?",
                trend="up",
                last_updated=datetime.now(),
                alert_threshold=250.0,
                is_critical=True
            ),
            KPIMetric(
                metric_id="care_points_conversion",
                name="?",
                description="?",
                metric_type=KPIMetricType.REVENUE,
                current_value=0.08,
                target_value=0.12,
                unit="%",
                trend="stable",
                last_updated=datetime.now(),
                alert_threshold=0.05
            ),
            # 安全
            KPIMetric(
                metric_id="safety_incident_rate",
                name="安全",
                description="治療",
                metric_type=KPIMetricType.SAFETY,
                current_value=0.002,
                target_value=0.001,
                unit="%",
                trend="down",
                last_updated=datetime.now(),
                alert_threshold=0.005,
                is_critical=True
            ),
            KPIMetric(
                metric_id="feature_flag_stability",
                name="?",
                description="Kill Switch発",
                metric_type=KPIMetricType.SAFETY,
                current_value=0.998,
                target_value=0.999,
                unit="score",
                trend="stable",
                last_updated=datetime.now(),
                alert_threshold=0.995
            )
        ]
        
        for metric in metrics:
            self.kpi_metrics[metric.metric_id] = metric

    def _generate_sample_data(self):
        """?"""
        # ?30?
        base_date = date.today() - timedelta(days=30)
        
        for i in range(500):  # 500?
            user_id = f"user_{i:04d}"
            registration_date = base_date + timedelta(days=i % 30)
            
            # ユーザー
            days_since_registration = (date.today() - registration_date).days
            
            # ?
            if days_since_registration >= 21 and i % 8 == 0:  # 12.5% が
                current_state = UserState.HABITUATION
                consecutive_days = 21 + (i % 10)
            elif days_since_registration >= 7 and i % 4 == 0:  # 25% がACTION?
                current_state = UserState.ACTION if i % 2 == 0 else UserState.CONTINUATION
                consecutive_days = 7 + (i % 14)
            elif days_since_registration >= 3 and i % 3 == 0:
                current_state = UserState.INTEREST
                consecutive_days = i % 7
            else:
                current_state = UserState.APATHY
                consecutive_days = i % 3
            
            # ?
            if i % 10 == 0:  # 10%は
                last_login = None
            else:
                last_login = date.today() - timedelta(days=i % 3)
            
            user_data = UserEngagementData(
                user_id=user_id,
                registration_date=registration_date,
                last_login_date=last_login,
                current_state=current_state,
                consecutive_days=consecutive_days,
                total_sessions=max(1, consecutive_days * 2 + (i % 10)),
                total_xp=consecutive_days * 50 + (i % 500),
                revenue_generated=(i % 1000) * 0.5,  # 0-500?
                therapeutic_progress={
                    "self_efficacy": min(1.0, consecutive_days * 0.05),
                    "cbt_engagement": 1.0 if i % 3 == 0 else 0.0,
                    "mood_improvement": min(1.0, consecutive_days * 0.03)
                },
                safety_incidents=1 if i % 500 == 0 else 0  # 0.2%の
            )
            
            self.user_data[user_id] = user_data

    async def calculate_kpi_metrics(self) -> Dict[str, Any]:
        """KPIメイン"""
        try:
            current_date = date.today()
            
            # D1リスト
            d1_retention = await self._calculate_d1_retention()
            self.kpi_metrics["d1_retention"].current_value = d1_retention
            
            # 7?
            d7_continuation = await self._calculate_d7_continuation_rate()
            self.kpi_metrics["d7_continuation_rate"].current_value = d7_continuation
            
            # 21?
            d21_habituation = await self._calculate_d21_habituation_rate()
            self.kpi_metrics["d21_habituation_rate"].current_value = d21_habituation
            
            # ARPMAU計算
            arpmau = await self._calculate_arpmau()
            self.kpi_metrics["arpmau"].current_value = arpmau
            
            # DAU計算
            dau = await self._calculate_daily_active_users()
            self.kpi_metrics["daily_active_users"].current_value = dau
            
            # 治療
            avg_efficacy = await self._calculate_avg_self_efficacy_improvement()
            self.kpi_metrics["avg_self_efficacy_improvement"].current_value = avg_efficacy
            
            cbt_engagement = await self._calculate_cbt_engagement_rate()
            self.kpi_metrics["cbt_engagement_rate"].current_value = cbt_engagement
            
            # ?
            care_points_conversion = await self._calculate_care_points_conversion()
            self.kpi_metrics["care_points_conversion"].current_value = care_points_conversion
            
            # 安全
            safety_incident_rate = await self._calculate_safety_incident_rate()
            self.kpi_metrics["safety_incident_rate"].current_value = safety_incident_rate
            
            # アプリ
            await self._check_alerts()
            
            # ?
            await self._save_historical_data()
            
            return {
                "calculation_completed": True,
                "metrics_updated": len(self.kpi_metrics),
                "alerts_generated": len([a for a in self.alerts.values() if a.resolved_at is None]),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}")
            raise HTTPException(status_code=500, detail="KPI計算")

    async def _calculate_d1_retention(self) -> float:
        """D1リスト"""
        yesterday = date.today() - timedelta(days=1)
        day_before_yesterday = date.today() - timedelta(days=2)
        
        # 一般
        registered_users = [
            user for user in self.user_data.values()
            if user.registration_date == day_before_yesterday
        ]
        
        if not registered_users:
            return 0.0
        
        # ?
        retained_users = [
            user for user in registered_users
            if user.last_login_date == yesterday
        ]
        
        return len(retained_users) / len(registered_users)

    async def _calculate_d7_continuation_rate(self) -> float:
        """7?ACTION?"""
        seven_days_ago = date.today() - timedelta(days=7)
        
        # 7?
        registered_users = [
            user for user in self.user_data.values()
            if user.registration_date == seven_days_ago
        ]
        
        if not registered_users:
            return 0.0
        
        # ACTION?
        action_users = [
            user for user in registered_users
            if user.current_state.value in ["ACTION", "CONTINUATION", "HABITUATION"]
        ]
        
        return len(action_users) / len(registered_users)

    async def _calculate_d21_habituation_rate(self) -> float:
        """21?"""
        twenty_one_days_ago = date.today() - timedelta(days=21)
        
        # 21?
        registered_users = [
            user for user in self.user_data.values()
            if user.registration_date == twenty_one_days_ago
        ]
        
        if not registered_users:
            return 0.0
        
        # HABITUATION?
        habituation_users = [
            user for user in registered_users
            if user.current_state == UserState.HABITUATION
        ]
        
        return len(habituation_users) / len(registered_users)

    async def _calculate_arpmau(self) -> float:
        """ARPMAU?"""
        # ?30?
        thirty_days_ago = date.today() - timedelta(days=30)
        active_users = [
            user for user in self.user_data.values()
            if user.last_login_date and user.last_login_date >= thirty_days_ago
        ]
        
        if not active_users:
            return 0.0
        
        total_revenue = sum(user.revenue_generated for user in active_users)
        return total_revenue / len(active_users)

    async def _calculate_daily_active_users(self) -> float:
        """?"""
        today = date.today()
        active_today = [
            user for user in self.user_data.values()
            if user.last_login_date == today
        ]
        return len(active_today)

    async def _calculate_avg_self_efficacy_improvement(self) -> float:
        """?"""
        efficacy_scores = [
            user.therapeutic_progress.get("self_efficacy", 0.0)
            for user in self.user_data.values()
            if user.therapeutic_progress.get("self_efficacy", 0.0) > 0
        ]
        
        if not efficacy_scores:
            return 0.0
        
        return sum(efficacy_scores) / len(efficacy_scores)

    async def _calculate_cbt_engagement_rate(self) -> float:
        """CBT?"""
        total_users = len(self.user_data)
        if total_users == 0:
            return 0.0
        
        cbt_engaged_users = [
            user for user in self.user_data.values()
            if user.therapeutic_progress.get("cbt_engagement", 0.0) > 0
        ]
        
        return len(cbt_engaged_users) / total_users

    async def _calculate_care_points_conversion(self) -> float:
        """?"""
        total_users = len(self.user_data)
        if total_users == 0:
            return 0.0
        
        # ?
        paying_users = [
            user for user in self.user_data.values()
            if user.revenue_generated > 0
        ]
        
        return len(paying_users) / total_users

    async def _calculate_safety_incident_rate(self) -> float:
        """安全"""
        total_users = len(self.user_data)
        if total_users == 0:
            return 0.0
        
        total_incidents = sum(user.safety_incidents for user in self.user_data.values())
        return total_incidents / total_users

    async def _check_alerts(self):
        """アプリ"""
        for metric_id, metric in self.kpi_metrics.items():
            if metric.alert_threshold is None:
                continue
            
            # ?
            if metric.unit == "%" and metric.current_value < metric.alert_threshold:
                await self._create_alert(
                    metric_id,
                    "threshold",
                    "high" if metric.is_critical else "medium",
                    f"{metric.name}が{metric.alert_threshold*100:.1f}%を: {metric.current_value*100:.1f}%?"
                )
            elif metric.unit in ["?", "count", "score"] and metric.current_value < metric.alert_threshold:
                await self._create_alert(
                    metric_id,
                    "threshold",
                    "high" if metric.is_critical else "medium",
                    f"{metric.name}が{metric.alert_threshold}を: {metric.current_value}?"
                )
            
            # ?
            if metric.current_value < metric.target_value * 0.8:  # ?80%を
                await self._create_alert(
                    metric_id,
                    "target_deviation",
                    "critical" if metric.is_critical else "high",
                    f"{metric.name}が: {metric.target_value}, ?: {metric.current_value}?"
                )

    async def _create_alert(self, metric_id: str, alert_type: str, severity: str, message: str):
        """アプリ"""
        alert_id = str(uuid.uuid4())
        
        # ?
        existing_alerts = [
            alert for alert in self.alerts.values()
            if alert.metric_id == metric_id and alert.resolved_at is None
        ]
        if existing_alerts:
            return
        
        alert = KPIAlert(
            alert_id=alert_id,
            metric_id=metric_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            created_at=datetime.now()
        )
        
        self.alerts[alert_id] = alert
        logger.warning(f"KPI Alert created: {message}")

    async def _save_historical_data(self):
        """?"""
        timestamp = datetime.now()
        for metric_id, metric in self.kpi_metrics.items():
            self.historical_data[metric_id].append({
                "timestamp": timestamp,
                "value": metric.current_value,
                "target": metric.target_value
            })
            
            # ?30?
            if len(self.historical_data[metric_id]) > 30:
                self.historical_data[metric_id] = self.historical_data[metric_id][-30:]

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """?"""
        # ?KPI計算
        await self.calculate_kpi_metrics()
        
        # ?
        critical_metrics = {
            metric_id: {
                "name": metric.name,
                "current_value": metric.current_value,
                "target_value": metric.target_value,
                "unit": metric.unit,
                "trend": metric.trend,
                "achievement_rate": (metric.current_value / metric.target_value) * 100 if metric.target_value > 0 else 0
            }
            for metric_id, metric in self.kpi_metrics.items()
            if metric.is_critical
        }
        
        # アプリ
        active_alerts = [
            {
                "alert_id": alert.alert_id,
                "metric_name": self.kpi_metrics[alert.metric_id].name,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at.isoformat()
            }
            for alert in self.alerts.values()
            if alert.resolved_at is None
        ]
        
        # ?
        health_score = await self._calculate_overall_health_score()
        
        return {
            "overall_health_score": health_score,
            "critical_metrics": critical_metrics,
            "active_alerts": active_alerts,
            "total_users": len(self.user_data),
            "last_updated": datetime.now().isoformat(),
            "summary_insights": await self._generate_summary_insights()
        }

    async def _calculate_overall_health_score(self) -> float:
        """?"""
        critical_metrics = [m for m in self.kpi_metrics.values() if m.is_critical]
        if not critical_metrics:
            return 1.0
        
        achievement_rates = []
        for metric in critical_metrics:
            if metric.target_value > 0:
                achievement_rate = min(1.0, metric.current_value / metric.target_value)
                achievement_rates.append(achievement_rate)
        
        return sum(achievement_rates) / len(achievement_rates) if achievement_rates else 1.0

    async def _generate_summary_insights(self) -> List[str]:
        """?"""
        insights = []
        
        # D1リスト
        d1_metric = self.kpi_metrics["d1_retention"]
        if d1_metric.current_value < d1_metric.target_value:
            insights.append(f"D1リスト{(d1_metric.target_value - d1_metric.current_value)*100:.1f}%?")
        
        # ?
        d21_metric = self.kpi_metrics["d21_habituation_rate"]
        if d21_metric.current_value >= d21_metric.target_value:
            insights.append("21?")
        
        # ARPMAU?
        arpmau_metric = self.kpi_metrics["arpmau"]
        if arpmau_metric.current_value < arpmau_metric.target_value:
            insights.append(f"ARPMAUが{arpmau_metric.target_value - arpmau_metric.current_value:.0f}?")
        
        # 安全
        safety_metric = self.kpi_metrics["safety_incident_rate"]
        if safety_metric.current_value > safety_metric.target_value:
            insights.append("安全")
        
        return insights[:5]  # ?5つ

    async def get_metric_details(self, metric_id: str) -> Dict[str, Any]:
        """メイン"""
        if metric_id not in self.kpi_metrics:
            raise HTTPException(status_code=404, detail="メイン")
        
        metric = self.kpi_metrics[metric_id]
        historical_data = self.historical_data.get(metric_id, [])
        
        # ?
        trend_analysis = await self._analyze_trend(historical_data)
        
        return {
            "metric": metric,
            "historical_data": historical_data[-14:],  # ?14?
            "trend_analysis": trend_analysis,
            "related_alerts": [
                alert for alert in self.alerts.values()
                if alert.metric_id == metric_id
            ][-5:]  # ?5?
        }

    async def _analyze_trend(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """?"""
        if len(historical_data) < 2:
            return {"trend": "insufficient_data", "change_rate": 0.0}
        
        recent_values = [point["value"] for point in historical_data[-7:]]  # ?7?
        older_values = [point["value"] for point in historical_data[-14:-7]]  # ?7?
        
        if not older_values:
            return {"trend": "insufficient_data", "change_rate": 0.0}
        
        recent_avg = sum(recent_values) / len(recent_values)
        older_avg = sum(older_values) / len(older_values)
        
        if older_avg == 0:
            change_rate = 0.0
        else:
            change_rate = (recent_avg - older_avg) / older_avg
        
        if change_rate > 0.05:
            trend = "improving"
        elif change_rate < -0.05:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_rate": change_rate,
            "recent_average": recent_avg,
            "previous_average": older_avg
        }

# ?
kpi_dashboard = KPIDashboardEngine()

# APIエラー
@app.get("/kpi/dashboard")
async def get_dashboard_summary():
    """KPI?"""
    return await kpi_dashboard.get_dashboard_summary()

@app.get("/kpi/metrics")
async def list_all_metrics():
    """?KPIメイン"""
    return {
        "metrics": list(kpi_dashboard.kpi_metrics.values()),
        "total_count": len(kpi_dashboard.kpi_metrics)
    }

@app.get("/kpi/metrics/{metric_id}")
async def get_metric_details(metric_id: str):
    """?"""
    return await kpi_dashboard.get_metric_details(metric_id)

@app.get("/kpi/alerts")
async def list_active_alerts():
    """アプリ"""
    active_alerts = [
        alert for alert in kpi_dashboard.alerts.values()
        if alert.resolved_at is None
    ]
    return {
        "alerts": active_alerts,
        "total_count": len(active_alerts)
    }

@app.post("/kpi/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """アプリ"""
    if alert_id not in kpi_dashboard.alerts:
        raise HTTPException(status_code=404, detail="アプリ")
    
    alert = kpi_dashboard.alerts[alert_id]
    if alert.resolved_at is not None:
        raise HTTPException(status_code=400, detail="?")
    
    alert.resolved_at = datetime.now()
    return {"message": "アプリ", "resolved_at": alert.resolved_at.isoformat()}

@app.post("/kpi/calculate")
async def trigger_kpi_calculation():
    """KPI計算"""
    return await kpi_dashboard.calculate_kpi_metrics()

@app.get("/kpi/health")
async def get_system_health():
    """システム"""
    health_score = await kpi_dashboard._calculate_overall_health_score()
    active_alerts_count = len([a for a in kpi_dashboard.alerts.values() if a.resolved_at is None])
    
    return {
        "status": "healthy" if health_score > 0.8 else "warning" if health_score > 0.6 else "critical",
        "health_score": health_score,
        "active_alerts": active_alerts_count,
        "last_calculation": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)