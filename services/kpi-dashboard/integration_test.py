"""
KPI Dashboard Service ?
?
"""
import asyncio
import json
import requests
from datetime import datetime, date, timedelta
from main import KPIDashboardEngine, UserState, UserEngagementData

class MockServiceIntegration:
    """?"""
    
    def __init__(self):
        self.auth_service_url = "http://localhost:8001"
        self.task_service_url = "http://localhost:8002"
        self.mood_service_url = "http://localhost:8003"
        
    async def fetch_user_data_from_services(self):
        """?"""
        # 実装APIを
        mock_users = []
        
        # ?
        auth_users = await self._mock_auth_service_data()
        
        # タスク
        task_data = await self._mock_task_service_data()
        
        # 気分
        mood_data = await self._mock_mood_service_data()
        
        # デフォルトUserEngagementDataを
        for user_id in auth_users:
            user_auth = auth_users[user_id]
            user_tasks = task_data.get(user_id, {})
            user_mood = mood_data.get(user_id, {})
            
            # ユーザー
            current_state = self._determine_user_state(user_tasks, user_mood)
            
            user_engagement = UserEngagementData(
                user_id=user_id,
                registration_date=user_auth["registration_date"],
                last_login_date=user_auth.get("last_login_date"),
                current_state=current_state,
                consecutive_days=user_tasks.get("consecutive_days", 0),
                total_sessions=user_tasks.get("total_sessions", 0),
                total_xp=user_tasks.get("total_xp", 0),
                revenue_generated=user_auth.get("revenue_generated", 0.0),
                therapeutic_progress=user_mood.get("therapeutic_progress", {}),
                safety_incidents=user_mood.get("safety_incidents", 0)
            )
            
            mock_users.append(user_engagement)
        
        return mock_users
    
    async def _mock_auth_service_data(self):
        """?"""
        return {
            "user_001": {
                "registration_date": date.today() - timedelta(days=30),
                "last_login_date": date.today(),
                "revenue_generated": 500.0
            },
            "user_002": {
                "registration_date": date.today() - timedelta(days=21),
                "last_login_date": date.today() - timedelta(days=1),
                "revenue_generated": 200.0
            },
            "user_003": {
                "registration_date": date.today() - timedelta(days=7),
                "last_login_date": date.today(),
                "revenue_generated": 0.0
            },
            "user_004": {
                "registration_date": date.today() - timedelta(days=2),
                "last_login_date": date.today() - timedelta(days=1),
                "revenue_generated": 100.0
            }
        }
    
    async def _mock_task_service_data(self):
        """タスク"""
        return {
            "user_001": {
                "consecutive_days": 25,
                "total_sessions": 50,
                "total_xp": 1250,
                "completed_tasks": 75
            },
            "user_002": {
                "consecutive_days": 18,
                "total_sessions": 36,
                "total_xp": 900,
                "completed_tasks": 54
            },
            "user_003": {
                "consecutive_days": 5,
                "total_sessions": 10,
                "total_xp": 250,
                "completed_tasks": 15
            },
            "user_004": {
                "consecutive_days": 2,
                "total_sessions": 4,
                "total_xp": 100,
                "completed_tasks": 6
            }
        }
    
    async def _mock_mood_service_data(self):
        """気分"""
        return {
            "user_001": {
                "therapeutic_progress": {
                    "self_efficacy": 0.85,
                    "cbt_engagement": 1.0,
                    "mood_improvement": 0.75
                },
                "safety_incidents": 0
            },
            "user_002": {
                "therapeutic_progress": {
                    "self_efficacy": 0.70,
                    "cbt_engagement": 1.0,
                    "mood_improvement": 0.60
                },
                "safety_incidents": 0
            },
            "user_003": {
                "therapeutic_progress": {
                    "self_efficacy": 0.45,
                    "cbt_engagement": 0.0,
                    "mood_improvement": 0.30
                },
                "safety_incidents": 0
            },
            "user_004": {
                "therapeutic_progress": {
                    "self_efficacy": 0.25,
                    "cbt_engagement": 0.0,
                    "mood_improvement": 0.15
                },
                "safety_incidents": 0
            }
        }
    
    def _determine_user_state(self, task_data, mood_data):
        """ユーザー"""
        consecutive_days = task_data.get("consecutive_days", 0)
        self_efficacy = mood_data.get("therapeutic_progress", {}).get("self_efficacy", 0)
        
        if consecutive_days >= 21 and self_efficacy >= 0.7:
            return UserState.HABITUATION
        elif consecutive_days >= 7 and self_efficacy >= 0.5:
            return UserState.CONTINUATION
        elif consecutive_days >= 3 and self_efficacy >= 0.3:
            return UserState.ACTION
        elif consecutive_days >= 1:
            return UserState.INTEREST
        else:
            return UserState.APATHY

async def test_service_integration():
    """?"""
    print("=== KPI Dashboard Service ? ===")
    
    # モデル
    integration = MockServiceIntegration()
    
    # KPI?
    dashboard = KPIDashboardEngine()
    
    print("? ?")
    
    # ?
    print("\n=== ? ===")
    integrated_users = await integration.fetch_user_data_from_services()
    
    print(f"? ?: {len(integrated_users)}?")
    
    # ?
    dashboard.user_data = {user.user_id: user for user in integrated_users}
    
    # ?
    print("\n=== ユーザー ===")
    for user in integrated_users:
        print(f"? {user.user_id}")
        print(f"  ?: {user.current_state.value}")
        print(f"  ?: {user.consecutive_days}?")
        print(f"  XP: {user.total_xp}")
        print(f"  ?: ?{user.revenue_generated}")
        print(f"  自動: {user.therapeutic_progress.get('self_efficacy', 0):.2f}")
    
    # KPI計算
    print("\n=== ?KPI計算 ===")
    calculation_result = await dashboard.calculate_kpi_metrics()
    
    print(f"? KPI計算")
    print(f"  ?: {calculation_result['metrics_updated']}")
    print(f"  ?: {calculation_result['alerts_generated']}")
    
    # ?
    print("\n=== ? ===")
    critical_metrics = [m for m in dashboard.kpi_metrics.values() if m.is_critical]
    for metric in critical_metrics:
        print(f"? {metric.name}")
        print(f"  ?: {metric.current_value:.3f} {metric.unit}")
        print(f"  ?: {metric.target_value:.3f} {metric.unit}")
        achievement = (metric.current_value / metric.target_value * 100) if metric.target_value > 0 else 0
        print(f"  ?: {achievement:.1f}%")
    
    # ?
    print("\n=== ? ===")
    summary = await dashboard.get_dashboard_summary()
    
    print(f"? ?: {summary['overall_health_score']:.3f}")
    print(f"? ?: {summary['total_users']}")
    print(f"? アプリ: {len(summary['active_alerts'])}")
    
    # 治療
    print("\n=== 治療 ===")
    habituation_users = [u for u in integrated_users if u.current_state == UserState.HABITUATION]
    action_plus_users = [u for u in integrated_users if u.current_state.value in ["ACTION", "CONTINUATION", "HABITUATION"]]
    
    print(f"? ?: {len(habituation_users)}? ({len(habituation_users)/len(integrated_users)*100:.1f}%)")
    print(f"? ACTION?: {len(action_plus_users)}? ({len(action_plus_users)/len(integrated_users)*100:.1f}%)")
    
    # ?
    total_revenue = sum(u.revenue_generated for u in integrated_users)
    paying_users = [u for u in integrated_users if u.revenue_generated > 0]
    
    print(f"? ?: ?{total_revenue}")
    print(f"? ?: {len(paying_users)}? ({len(paying_users)/len(integrated_users)*100:.1f}%)")
    if paying_users:
        avg_revenue = total_revenue / len(paying_users)
        print(f"? ?: ?{avg_revenue:.0f}")
    
    # アプリ
    if summary['active_alerts']:
        print("\n=== アプリ ===")
        for alert in summary['active_alerts']:
            print(f"?  {alert['severity'].upper()}: {alert['message']}")
    
    print("\n=== ? ===")
    return True

async def test_real_time_updates():
    """リスト"""
    print("\n=== リスト ===")
    
    dashboard = KPIDashboardEngine()
    
    # ?
    initial_summary = await dashboard.get_dashboard_summary()
    initial_health_score = initial_summary['overall_health_score']
    
    print(f"?: {initial_health_score:.3f}")
    
    # ?
    new_user = UserEngagementData(
        user_id="new_user_high_performer",
        registration_date=date.today() - timedelta(days=25),
        last_login_date=date.today(),
        current_state=UserState.HABITUATION,
        consecutive_days=25,
        total_sessions=50,
        total_xp=1250,
        revenue_generated=800.0,
        therapeutic_progress={
            "self_efficacy": 0.95,
            "cbt_engagement": 1.0,
            "mood_improvement": 0.85
        },
        safety_incidents=0
    )
    
    dashboard.user_data[new_user.user_id] = new_user
    
    # ?
    updated_summary = await dashboard.get_dashboard_summary()
    updated_health_score = updated_summary['overall_health_score']
    
    print(f"?: {updated_health_score:.3f}")
    print(f"?: {updated_health_score - initial_health_score:+.3f}")
    
    # メイン
    print("\n=== メイン ===")
    for metric_id in ["arpmau", "d21_habituation_rate"]:
        if metric_id in updated_summary['critical_metrics']:
            metric = updated_summary['critical_metrics'][metric_id]
            print(f"? {metric['name']}: {metric['current_value']:.3f} {metric['unit']}")
    
    print("? リスト")

def test_api_performance():
    """API ?"""
    print("\n=== API ? ===")
    
    from fastapi.testclient import TestClient
    from main import app
    import time
    
    client = TestClient(app)
    
    # ?
    endpoints = [
        ("/kpi/dashboard", "?"),
        ("/kpi/metrics", "メイン"),
        ("/kpi/metrics/d1_retention", "?"),
        ("/kpi/alerts", "アプリ"),
        ("/kpi/health", "システム")
    ]
    
    for endpoint, name in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # ?
        
        print(f"? {name}: {response_time:.2f}ms (Status: {response.status_code})")
        
        # 1.2?1200ms?
        assert response_time < 1200, f"{name}の: {response_time:.2f}ms"
        assert response.status_code == 200, f"{name}で: {response.status_code}"
    
    print("? ?")

if __name__ == "__main__":
    # ?
    asyncio.run(test_service_integration())
    
    # リスト
    asyncio.run(test_real_time_updates())
    
    # ?
    test_api_performance()
    
    print("\n? KPI Dashboard Service ?")