"""
KPI Dashboard Service ?
"""
import pytest
import asyncio
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from main import app, kpi_dashboard, KPIDashboardEngine, UserState, UserEngagementData

client = TestClient(app)

class TestKPIDashboard:
    def setup_method(self):
        """?"""
        # ?KPI?
        self.dashboard = KPIDashboardEngine()
    
    def test_dashboard_initialization(self):
        """?"""
        assert len(self.dashboard.kpi_metrics) > 0
        assert len(self.dashboard.user_data) > 0
        
        # ?
        critical_metrics = ["d1_retention", "d7_continuation_rate", "d21_habituation_rate", "arpmau"]
        for metric_id in critical_metrics:
            assert metric_id in self.dashboard.kpi_metrics
            assert self.dashboard.kpi_metrics[metric_id].is_critical
    
    @pytest.mark.asyncio
    async def test_d1_retention_calculation(self):
        """D1リスト"""
        # ?
        yesterday = date.today() - timedelta(days=1)
        day_before_yesterday = date.today() - timedelta(days=2)
        
        # 一般
        test_users = {
            "user_retained": UserEngagementData(
                user_id="user_retained",
                registration_date=day_before_yesterday,
                last_login_date=yesterday,
                current_state=UserState.ACTION,
                consecutive_days=2,
                total_sessions=4,
                total_xp=100,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            ),
            "user_not_retained": UserEngagementData(
                user_id="user_not_retained",
                registration_date=day_before_yesterday,
                last_login_date=day_before_yesterday,
                current_state=UserState.APATHY,
                consecutive_days=1,
                total_sessions=1,
                total_xp=25,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            )
        }
        
        # ?
        self.dashboard.user_data = test_users
        
        # D1リスト
        retention_rate = await self.dashboard._calculate_d1_retention()
        
        # 50%の2?1?
        assert retention_rate == 0.5
    
    @pytest.mark.asyncio
    async def test_d7_continuation_rate_calculation(self):
        """7?"""
        seven_days_ago = date.today() - timedelta(days=7)
        
        # ?
        test_users = {
            "user_action": UserEngagementData(
                user_id="user_action",
                registration_date=seven_days_ago,
                last_login_date=date.today(),
                current_state=UserState.ACTION,
                consecutive_days=7,
                total_sessions=14,
                total_xp=350,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            ),
            "user_apathy": UserEngagementData(
                user_id="user_apathy",
                registration_date=seven_days_ago,
                last_login_date=seven_days_ago + timedelta(days=2),
                current_state=UserState.APATHY,
                consecutive_days=2,
                total_sessions=3,
                total_xp=75,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            )
        }
        
        self.dashboard.user_data = test_users
        
        # 7?
        continuation_rate = await self.dashboard._calculate_d7_continuation_rate()
        
        # 50%の2?1?ACTION?
        assert continuation_rate == 0.5
    
    @pytest.mark.asyncio
    async def test_d21_habituation_rate_calculation(self):
        """21?"""
        twenty_one_days_ago = date.today() - timedelta(days=21)
        
        # ?
        test_users = {
            "user_habituation": UserEngagementData(
                user_id="user_habituation",
                registration_date=twenty_one_days_ago,
                last_login_date=date.today(),
                current_state=UserState.HABITUATION,
                consecutive_days=21,
                total_sessions=42,
                total_xp=1050,
                revenue_generated=100.0,
                therapeutic_progress={"self_efficacy": 0.8},
                safety_incidents=0
            ),
            "user_continuation": UserEngagementData(
                user_id="user_continuation",
                registration_date=twenty_one_days_ago,
                last_login_date=date.today(),
                current_state=UserState.CONTINUATION,
                consecutive_days=15,
                total_sessions=30,
                total_xp=750,
                revenue_generated=50.0,
                therapeutic_progress={"self_efficacy": 0.6},
                safety_incidents=0
            ),
            "user_dropped": UserEngagementData(
                user_id="user_dropped",
                registration_date=twenty_one_days_ago,
                last_login_date=twenty_one_days_ago + timedelta(days=5),
                current_state=UserState.APATHY,
                consecutive_days=3,
                total_sessions=6,
                total_xp=150,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            )
        }
        
        self.dashboard.user_data = test_users
        
        # 21?
        habituation_rate = await self.dashboard._calculate_d21_habituation_rate()
        
        # 33.3%の3?1?HABITUATION?
        assert abs(habituation_rate - 1/3) < 0.01
    
    @pytest.mark.asyncio
    async def test_arpmau_calculation(self):
        """ARPMAU計算"""
        thirty_days_ago = date.today() - timedelta(days=30)
        
        # ?
        test_users = {
            "user_high_revenue": UserEngagementData(
                user_id="user_high_revenue",
                registration_date=thirty_days_ago,
                last_login_date=date.today(),
                current_state=UserState.HABITUATION,
                consecutive_days=30,
                total_sessions=60,
                total_xp=1500,
                revenue_generated=500.0,
                therapeutic_progress={"self_efficacy": 0.9},
                safety_incidents=0
            ),
            "user_low_revenue": UserEngagementData(
                user_id="user_low_revenue",
                registration_date=thirty_days_ago,
                last_login_date=date.today(),
                current_state=UserState.ACTION,
                consecutive_days=20,
                total_sessions=40,
                total_xp=1000,
                revenue_generated=100.0,
                therapeutic_progress={"self_efficacy": 0.7},
                safety_incidents=0
            ),
            "user_inactive": UserEngagementData(
                user_id="user_inactive",
                registration_date=thirty_days_ago,
                last_login_date=thirty_days_ago + timedelta(days=5),
                current_state=UserState.APATHY,
                consecutive_days=3,
                total_sessions=6,
                total_xp=150,
                revenue_generated=0.0,
                therapeutic_progress={},
                safety_incidents=0
            )
        }
        
        self.dashboard.user_data = test_users
        
        # ARPMAU計算
        arpmau = await self.dashboard._calculate_arpmau()
        
        # 300?ARPMAUを2?
        assert arpmau == 300.0
    
    @pytest.mark.asyncio
    async def test_alert_generation(self):
        """アプリ"""
        # ?
        self.dashboard.kpi_metrics["d1_retention"].current_value = 0.30  # ?0.35を
        self.dashboard.kpi_metrics["d1_retention"].alert_threshold = 0.35
        
        # アプリ
        await self.dashboard._check_alerts()
        
        # アプリ
        active_alerts = [a for a in self.dashboard.alerts.values() if a.resolved_at is None]
        assert len(active_alerts) > 0
        
        # D1リスト
        d1_alerts = [a for a in active_alerts if a.metric_id == "d1_retention"]
        assert len(d1_alerts) > 0
    
    @pytest.mark.asyncio
    async def test_dashboard_summary(self):
        """?"""
        summary = await self.dashboard.get_dashboard_summary()
        
        # ?
        required_fields = [
            "overall_health_score",
            "critical_metrics",
            "active_alerts",
            "total_users",
            "last_updated",
            "summary_insights"
        ]
        
        for field in required_fields:
            assert field in summary
        
        # ?0-1の
        assert 0 <= summary["overall_health_score"] <= 1
        
        # ?
        critical_metrics = summary["critical_metrics"]
        assert "d1_retention" in critical_metrics
        assert "d7_continuation_rate" in critical_metrics
        assert "d21_habituation_rate" in critical_metrics
        assert "arpmau" in critical_metrics

class TestKPIDashboardAPI:
    def test_get_dashboard_summary_endpoint(self):
        """?API?"""
        response = client.get("/kpi/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overall_health_score" in data
        assert "critical_metrics" in data
        assert "active_alerts" in data
    
    def test_list_all_metrics_endpoint(self):
        """?API?"""
        response = client.get("/kpi/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "metrics" in data
        assert "total_count" in data
        assert data["total_count"] > 0
    
    def test_get_metric_details_endpoint(self):
        """メインAPI?"""
        response = client.get("/kpi/metrics/d1_retention")
        assert response.status_code == 200
        
        data = response.json()
        assert "metric" in data
        assert "historical_data" in data
        assert "trend_analysis" in data
    
    def test_get_metric_details_not_found(self):
        """?API?"""
        response = client.get("/kpi/metrics/nonexistent_metric")
        assert response.status_code == 404
    
    def test_list_active_alerts_endpoint(self):
        """アプリAPI?"""
        response = client.get("/kpi/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data
    
    def test_trigger_kpi_calculation_endpoint(self):
        """KPI計算API?"""
        response = client.post("/kpi/calculate")
        assert response.status_code == 200
        
        data = response.json()
        assert "calculation_completed" in data
        assert data["calculation_completed"] is True
    
    def test_get_system_health_endpoint(self):
        """システムAPI?"""
        response = client.get("/kpi/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "health_score" in data
        assert "active_alerts" in data
        assert data["status"] in ["healthy", "warning", "critical"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])